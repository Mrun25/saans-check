"""
Inference wrapper: loads a trained Stage-1 pipeline (model + scaler + threshold) and exposes
a simple .predict(filepath) -> (score, model_version) interface. This is what
phase1-intake-app/backend/app/audio_pipeline.py imports.
"""

from dataclasses import dataclass
import logging
import os
import sys

import joblib

sys.path.insert(0, os.path.dirname(__file__))

from embed_yamnet import YAMNET_SAMPLE_RATE, embed  # noqa: E402
from preprocessing import preprocess_clip  # noqa: E402

logger = logging.getLogger("phase2.inference")


@dataclass
class ProxyClassifierPipeline:
    model: object
    scaler: object
    elevated_threshold: float
    model_version: str
    disclaimer: str

    @classmethod
    def load(cls, path: str) -> "ProxyClassifierPipeline":
        obj = joblib.load(path)
        return cls(
            model=obj["model"],
            scaler=obj["scaler"],
            elevated_threshold=obj["elevated_threshold"],
            model_version=obj["model_version"],
            disclaimer=obj.get("IMPORTANT_DISCLAIMER", ""),
        )

    def predict(self, filepath: str) -> tuple[float, str]:
        """Returns (probability_score, model_version). Probability is P(elevated-pattern)."""
        audio = preprocess_clip(filepath, target_sr=YAMNET_SAMPLE_RATE)
        emb = embed(audio, YAMNET_SAMPLE_RATE).reshape(1, -1)
        emb_scaled = self.scaler.transform(emb)
        proba = self.model.predict_proba(emb_scaled)[0, 1]
        return float(proba), self.model_version
