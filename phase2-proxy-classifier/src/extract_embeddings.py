#!/usr/bin/env python3
"""
Extract YAMNet embeddings for an entire dataset and save as a single .npz file
(embeddings, labels, metadata) for fast downstream classifier training.

Usage:
    python extract_embeddings.py --dataset coswara --input data/raw/coswara \
        --output data/embeddings/coswara.npz
    python extract_embeddings.py --dataset virufy --input data/raw/virufy \
        --output data/embeddings/virufy.npz
"""

import argparse
import logging
import os
import sys

import numpy as np
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(__file__))

from datasets import load_coswara, load_virufy  # noqa: E402
from embed_yamnet import YAMNET_SAMPLE_RATE, embed  # noqa: E402
from preprocessing import preprocess_clip  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("extract_embeddings")

LOADERS = {
    "coswara": load_coswara,
    "virufy": load_virufy,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, choices=list(LOADERS.keys()))
    parser.add_argument("--input", required=True, help="Path to the dataset root directory")
    parser.add_argument("--output", required=True, help="Output .npz path")
    parser.add_argument(
        "--max-samples", type=int, default=None, help="Cap sample count (useful for a quick test run)"
    )
    parser.add_argument(
        "--skip-bandpass", action="store_true", help="Disable bandpass filtering in preprocessing"
    )
    args = parser.parse_args()

    loader = LOADERS[args.dataset]
    samples = loader(args.input)
    if args.max_samples:
        samples = samples[: args.max_samples]

    if not samples:
        logger.error(
            "No samples loaded from %s. Check the dataset path and that it matches the "
            "structure documented in data/README.md.",
            args.input,
        )
        sys.exit(1)

    embeddings = []
    labels = []
    subject_ids = []
    source_datasets = []
    failed = 0

    for sample in tqdm(samples, desc=f"Embedding {args.dataset}"):
        try:
            audio = preprocess_clip(
                sample.filepath,
                target_sr=YAMNET_SAMPLE_RATE,
                apply_bandpass=not args.skip_bandpass,
            )
            if len(audio) < YAMNET_SAMPLE_RATE * 0.1:  # shorter than 100ms — likely a bad clip
                logger.warning("Skipping too-short clip: %s", sample.filepath)
                failed += 1
                continue
            emb = embed(audio, YAMNET_SAMPLE_RATE)
            embeddings.append(emb)
            labels.append(sample.label)
            subject_ids.append(sample.subject_id)
            source_datasets.append(sample.source_dataset)
        except Exception as e:
            logger.warning("Failed on %s: %s", sample.filepath, e)
            failed += 1

    if not embeddings:
        logger.error("All samples failed to embed. Nothing to save.")
        sys.exit(1)

    embeddings_arr = np.stack(embeddings)
    labels_arr = np.array(labels, dtype=np.int64)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    np.savez(
        args.output,
        embeddings=embeddings_arr,
        labels=labels_arr,
        subject_ids=np.array(subject_ids),
        source_datasets=np.array(source_datasets),
    )

    logger.info(
        "Saved %d embeddings (%d failed/skipped) to %s. Label distribution: %d positive, %d negative.",
        len(embeddings),
        failed,
        args.output,
        int(labels_arr.sum()),
        int((labels_arr == 0).sum()),
    )


if __name__ == "__main__":
    main()
