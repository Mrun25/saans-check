#!/usr/bin/env python3
"""
Evaluate a trained Stage-1 pipeline against any embedding .npz file — typically a held-out
validation set, or later, the shadow-test data described in PRD §6 Phase 2 ("A/B or
shadow-test its output against actual camp outcomes").

Usage:
    python evaluate.py --model models/stage1_proxy_v1.pkl --test-split data/embeddings/virufy.npz
"""

import argparse
import logging

import joblib
import numpy as np
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluate")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--test-split", required=True)
    parser.add_argument("--plot", action="store_true", help="Save a confusion matrix + ROC curve PNG")
    parser.add_argument("--plot-output", default="evaluation_plots.png")
    args = parser.parse_args()

    pipeline_obj = joblib.load(args.model)
    model = pipeline_obj["model"]
    scaler = pipeline_obj["scaler"]
    threshold = pipeline_obj["elevated_threshold"]

    data = np.load(args.test_split, allow_pickle=True)
    X, y = data["embeddings"], data["labels"]

    X_scaled = scaler.transform(X)
    y_proba = model.predict_proba(X_scaled)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    print(f"\n=== Evaluation: {args.test_split} ===")
    print(f"Model version: {pipeline_obj['model_version']}")
    print(f"Threshold: {threshold}")
    print(f"N samples: {len(y)} ({y.sum()} positive, {(y == 0).sum()} negative)\n")

    try:
        auc = roc_auc_score(y, y_proba)
        print(f"AUC: {auc:.3f}")
    except ValueError as e:
        print(f"AUC could not be computed: {e}")

    print("\n" + classification_report(y, y_pred))
    print("Confusion matrix:\n", confusion_matrix(y, y_pred))

    print(
        "\nREMINDER: this evaluates the proxy classifier against TB/COVID/healthy labels, "
        "not silicosis. Good performance here is necessary-but-not-sufficient evidence the "
        "pipeline works end-to-end (PRD §6 Phase 0 goal) — it says nothing about silicosis "
        "detection, which requires Phase 3's paired clinical data."
    )

    if args.plot:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        ConfusionMatrixDisplay(confusion_matrix(y, y_pred)).plot(ax=axes[0])
        axes[0].set_title("Confusion Matrix")

        fpr, tpr, _ = roc_curve(y, y_proba)
        axes[1].plot(fpr, tpr, label=f"AUC={auc:.3f}" if "auc" in dir() else "ROC")
        axes[1].plot([0, 1], [0, 1], linestyle="--", color="gray")
        axes[1].set_xlabel("False Positive Rate")
        axes[1].set_ylabel("True Positive Rate")
        axes[1].set_title("ROC Curve")
        axes[1].legend()

        plt.tight_layout()
        plt.savefig(args.plot_output)
        print(f"\nSaved plots to {args.plot_output}")


if __name__ == "__main__":
    main()
