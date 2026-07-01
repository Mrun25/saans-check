"""
Feature extraction layer (PRD §4.2.C, v1): YAMNet, frozen, pretrained, not trained by this
project. Open model, no API key, runs on CPU, produces a 1024-dim embedding per clip.

This module implements the embed(audio_array, sample_rate) -> np.ndarray interface that
phase4-scale/hear_migration/hear_embedder.py mirrors, so swapping the embedding backend later
doesn't require touching the classifier training code (see docs/architecture.md).
"""

import logging

import numpy as np

logger = logging.getLogger("phase2.embed_yamnet")

YAMNET_HANDLE = "https://tfhub.dev/google/yamnet/1"
YAMNET_SAMPLE_RATE = 16000

_model = None


def _load_model():
    """Lazy singleton load — avoids paying TF Hub download/init cost at import time, which
    matters because app/audio_pipeline.py in Phase 1 imports this module speculatively and
    must not fail/slow down if a deployment never trains or deploys a classifier at all."""
    global _model
    if _model is None:
        import tensorflow_hub as hub

        logger.info("Loading YAMNet from %s ...", YAMNET_HANDLE)
        _model = hub.load(YAMNET_HANDLE)
        logger.info("YAMNet loaded.")
    return _model


def embed(audio_array: np.ndarray, sample_rate: int = YAMNET_SAMPLE_RATE) -> np.ndarray:
    """
    Run YAMNet on a mono float32 waveform at 16kHz, return a single 1024-dim embedding for the
    whole clip (mean-pooled across YAMNet's internal ~0.96s frames — a clip-level pooling choice
    that's standard practice for using YAMNet as a fixed feature extractor for downstream
    classification, as opposed to its native per-frame AudioSet class predictions, which we
    discard entirely since we're not using YAMNet's own 521-class output here).

    Raises if sample_rate != 16000 — resampling is preprocessing.py's job, not this module's,
    to keep the "embedding model expects X" contract explicit at the call site.
    """
    if sample_rate != YAMNET_SAMPLE_RATE:
        raise ValueError(
            f"YAMNet expects {YAMNET_SAMPLE_RATE}Hz audio, got {sample_rate}Hz. "
            f"Resample with preprocessing.load_and_resample() first."
        )
    if audio_array.ndim != 1:
        raise ValueError(f"Expected mono 1D audio array, got shape {audio_array.shape}")

    model = _load_model()
    # YAMNet's signature: scores, embeddings, spectrogram = model(waveform)
    # embeddings shape: (num_frames, 1024)
    _, embeddings, _ = model(audio_array)
    clip_embedding = np.mean(embeddings.numpy(), axis=0)
    return clip_embedding.astype(np.float32)


def embed_batch(audio_arrays: list[np.ndarray], sample_rate: int = YAMNET_SAMPLE_RATE) -> np.ndarray:
    """Convenience wrapper — YAMNet's TF Hub signature doesn't batch natively across
    variable-length clips, so this is a simple loop, not a true batched call. Fine for the
    offline training-data extraction use case (extract_embeddings.py); not meant for
    low-latency serving of many concurrent requests."""
    return np.stack([embed(a, sample_rate) for a in audio_arrays])
