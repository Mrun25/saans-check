#!/usr/bin/env python3
"""
Train the Stage-1 proxy classifier head (PRD §4.2.D): a small, simple model on top of frozen
YAMNet embeddings. Deliberately not a large network — see the module docstring rationale in
docs/architecture.md ("Why the classifier head is small").

Usage:
    python train_classifier.py --embeddings data/embeddings/coswara.npz \
        --output models/stage1_proxy_v1.pkl --model-type logreg

    # Train on Coswara, hold out Virufy entirely for honest external validation:
    python train_classifier.py --embeddings data/embeddings/coswara.npz \
        --holdout data/embeddings/virufy.npz \
        --output models/stage1_proxy_v1.pkl
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train_classifier")

MODEL_TYPES = {
    "logreg": lambda: LogisticRegression(max_iter=2000, class_weight="balanced", C=1.0),
    "svm": lambda: SVC(probability=True, class_weight="balanced", kernel="rbf", C=1.0),
    "mlp": lambda: MLPClassifier(hidden_layer_sizes=(64,), max_iter=1000, alpha=0.01),
    "rf": lambda: RandomForestClassifier(n_estimators=200, class_weight="balanced", max_depth=8),
}


def load_npz(path: str):
    data = np.load(path, allow_pickle=True)
    return data["embeddings"], data["labels"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--embeddings", required=True, nargs="+", help="One or more .npz embedding files to train on")
    parser.add_argument("--holdout", nargs="*", default=[], help="Optional .npz files used ONLY for evaluation, never training")
    parser.add_argument("--output", required=True, help="Output .pkl path for the trained pipeline")
    parser.add_argument("--model-type", choices=list(MODEL_TYPES.keys()), default="logreg")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--elevated-threshold",
        type=float,
        default=0.4,
        help=(
            "Probability threshold above which the tier becomes ELEVATED_PROXY. Set below 0.5 "
            "by default per the asymmetric-caution principle (PRD §3.3): a missed elevated flag "
            "is worse than an extra false alarm, so we bias toward higher recall on the "
            "positive class at some precision cost. Tune against held-out data, don't leave "
            "this default unexamined."
        ),
    )
    args = parser.parse_args()

    # --- Load and concatenate training embeddings ---
    all_embeddings, all_labels = [], []
    for path in args.embeddings:
        emb, lab = load_npz(path)
        all_embeddings.append(emb)
        all_labels.append(lab)
        logger.info("Loaded %d samples from %s", len(lab), path)

    X = np.concatenate(all_embeddings, axis=0)
    y = np.concatenate(all_labels, axis=0)

    logger.info("Total training pool: %d samples (%d positive, %d negative)", len(y), y.sum(), (y == 0).sum())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = MODEL_TYPES[args.model_type]()
    logger.info("Training %s ...", args.model_type)
    model.fit(X_train_scaled, y_train)

    # --- Internal test split evaluation ---
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    y_pred = (y_proba >= args.elevated_threshold).astype(int)

    report = classification_report(y_test, y_pred, output_dict=True)
    try:
        auc = roc_auc_score(y_test, y_proba)
    except ValueError:
        auc = None

    logger.info("=== Internal held-out test split ===")
    logger.info("AUC: %s", auc)
    logger.info("\n%s", classification_report(y_test, y_pred))

    # --- External holdout dataset evaluation (e.g. train on Coswara, check on Virufy) ---
    holdout_results = {}
    for holdout_path in args.holdout:
        X_h, y_h = load_npz(holdout_path)
        X_h_scaled = scaler.transform(X_h)
        y_h_proba = model.predict_proba(X_h_scaled)[:, 1]
        y_h_pred = (y_h_proba >= args.elevated_threshold).astype(int)
        try:
            h_auc = roc_auc_score(y_h, y_h_proba)
        except ValueError:
            h_auc = None
        logger.info("=== External holdout: %s ===", holdout_path)
        logger.info("AUC: %s", h_auc)
        logger.info("\n%s", classification_report(y_h, y_h_pred))
        holdout_results[holdout_path] = {
            "auc": h_auc,
            "report": classification_report(y_h, y_h_pred, output_dict=True),
        }

    # --- Save the full pipeline + metadata ---
    model_version = f"stage1_proxy_{args.model_type}_{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    pipeline_obj = {
        "model": model,
        "scaler": scaler,
        "elevated_threshold": args.elevated_threshold,
        "model_version": model_version,
        "training_files": args.embeddings,
        "holdout_files": args.holdout,
        "internal_test_auc": auc,
        "internal_test_report": report,
        "holdout_results": holdout_results,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "IMPORTANT_DISCLAIMER": (
            "This model is trained on public TB/COVID/healthy cough datasets, NOT silicosis "
            "data. It has never been validated against confirmed silicosis cases. Do not "
            "present its output as silicosis detection to any user, partner, or investor. "
            "See PRD.md sections 1.3 and 4.2.D."
        ),
    }

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    joblib.dump(pipeline_obj, args.output)
    logger.info("Saved trained pipeline to %s (model_version=%s)", args.output, model_version)

    # Save a human-readable sidecar report too
    report_path = args.output.replace(".pkl", "_report.json")
    with open(report_path, "w") as f:
        json.dump(
            {
                "model_version": model_version,
                "internal_test_auc": auc,
                "internal_test_report": report,
                "holdout_results": {k: v["auc"] for k, v in holdout_results.items()},
                "disclaimer": pipeline_obj["IMPORTANT_DISCLAIMER"],
            },
            f,
            indent=2,
        )
    logger.info("Saved human-readable report to %s", report_path)


if __name__ == "__main__":
    main()
