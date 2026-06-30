#!/usr/bin/env python3
"""
Stage-2 retraining: same classifier training approach as Phase 2
(../../phase2-proxy-classifier/src/train_classifier.py), pointed at real paired clinical data
instead of public proxy datasets.

THIS SCRIPT WILL NOT RUN SUCCESSFULLY TODAY. It requires a populated paired-data directory
matching ../data_schema/schema.py's PairedTrainingExample structure, which does not exist yet
because no clinical partnership has been secured (see ../../docs/phase0-research-findings.md,
exit criterion). This is not a bug to fix — it's an honest reflection of where the project
actually stands. Running this script today should fail loudly with a clear "no data found"
error, not silently produce a fake result.

Once real paired data exists, the actual training logic is intentionally NOT reimplemented here
— it imports directly from phase2-proxy-classifier/src/train_classifier.py's MODEL_TYPES and
training loop, because per the PRD (§4.2.D) and docs/architecture.md, the Stage 1 -> Stage 2
transition is meant to be a data swap, not a rewrite. This file is a thin orchestration wrapper
around the same embedding extraction + classifier head approach, applied to a different,
real, consented dataset.

Usage (once real data exists):
    python retrain_stage2.py --paired-data-dir /path/to/phase3/paired_dataset \
        --output ../models/stage2_silicosis_v1.pkl
"""

import argparse
import csv
import json
import logging
import os
import sys

import numpy as np

PHASE2_SRC = os.path.join(os.path.dirname(__file__), "..", "..", "phase2-proxy-classifier", "src")
sys.path.insert(0, PHASE2_SRC)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data_schema"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retrain_stage2")


def load_paired_dataset(paired_data_dir: str):
    """
    Expects a manifest CSV at <paired_data_dir>/manifest.csv with columns matching
    schema.PairedTrainingExample: participant_id, audio_filepath, silicosis_label (0/1), plus
    whatever exposure/diagnosis fields the partner's data collection tooling produces.

    This loader is intentionally strict — it raises clearly rather than guessing at a schema,
    since silently mis-parsing real clinical/consent data is a much worse failure mode here
    than it was for the public proxy datasets in Phase 2.
    """
    manifest_path = os.path.join(paired_data_dir, "manifest.csv")
    if not os.path.isfile(manifest_path):
        raise FileNotFoundError(
            f"No manifest.csv found at {manifest_path}. This script requires real paired "
            f"clinical data collected under the protocol in ../consent_forms/ and structured "
            f"per ../data_schema/schema.py. See ../../docs/phase0-research-findings.md for the "
            f"current status of partner outreach — if you're reading this because outreach "
            f"hasn't produced data yet, that's the actual blocker, not this script."
        )

    required_cols = {"participant_id", "audio_filepath", "silicosis_label"}
    rows = []
    with open(manifest_path, newline="") as f:
        reader = csv.DictReader(f)
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"manifest.csv is missing required columns: {missing}")
        for row in reader:
            rows.append(row)

    if len(rows) < 30:
        logger.warning(
            "Only %d paired examples found. Per ../data_schema/sample_size_notes.md, this is "
            "below even the pilot-phase target of 30-50 — treat any resulting model as a "
            "feasibility check, not a validated classifier. Do not present results from a "
            "dataset this size as conclusive evidence either way about the acoustic hypothesis.",
            len(rows),
        )

    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paired-data-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-type", default="logreg", choices=["logreg", "svm", "mlp", "rf"])
    args = parser.parse_args()

    rows = load_paired_dataset(args.paired_data_dir)
    logger.info("Loaded %d paired examples from %s", len(rows), args.paired_data_dir)

    from embed_yamnet import YAMNET_SAMPLE_RATE, embed  # noqa: E402
    from preprocessing import preprocess_clip  # noqa: E402

    embeddings, labels = [], []
    for row in rows:
        audio = preprocess_clip(row["audio_filepath"], target_sr=YAMNET_SAMPLE_RATE)
        emb = embed(audio, YAMNET_SAMPLE_RATE)
        embeddings.append(emb)
        labels.append(int(row["silicosis_label"]))

    X = np.stack(embeddings)
    y = np.array(labels)

    embeddings_path = os.path.join(args.paired_data_dir, "_stage2_embeddings_cache.npz")
    np.savez(embeddings_path, embeddings=X, labels=y)
    logger.info("Cached embeddings to %s", embeddings_path)

    # Reuse Phase 2's exact training approach — see phase2-proxy-classifier/src/train_classifier.py
    # for the actual model-fitting code this delegates to via subprocess, keeping the two phases'
    # training logic as one shared implementation rather than two copies that could drift apart.
    import subprocess

    train_script = os.path.join(PHASE2_SRC, "train_classifier.py")
    cmd = [
        sys.executable,
        train_script,
        "--embeddings",
        embeddings_path,
        "--output",
        args.output,
        "--model-type",
        args.model_type,
    ]
    logger.info("Delegating to Phase 2's training script: %s", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)

    # Stage 2 specific: overwrite the disclaimer, since this model — unlike Stage 1 — IS trained
    # on real silicosis-confirmed data, so the Stage-1 "not validated for silicosis" disclaimer
    # would now be actively wrong, not just appropriately cautious.
    import joblib

    obj = joblib.load(args.output)
    obj["IMPORTANT_DISCLAIMER"] = (
        f"This model was trained on {len(rows)} real, consented, clinically-confirmed paired "
        f"cough recordings (see manifest at {args.paired_data_dir}/manifest.csv). This is the "
        f"first model in this project actually trained on silicosis-confirmed data. Even so: "
        f"check ../data_schema/sample_size_notes.md for whether this n clears the threshold for "
        f"a statistically meaningful read before making any claim publicly, to users, or to "
        f"investors. A small-n result here is a feasibility signal, not proof."
    )
    obj["model_version"] = obj["model_version"].replace("stage1_proxy", "stage2_silicosis")
    joblib.dump(obj, args.output)
    logger.info("Updated disclaimer and model_version for Stage 2. Saved to %s", args.output)


if __name__ == "__main__":
    main()
