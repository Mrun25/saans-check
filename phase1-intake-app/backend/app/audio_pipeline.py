"""
Audio preprocessing + classifier invocation (PRD §4.2.B, §4.2.C, §4.2.D).

Designed so Phase 1 can run with ZERO dependency on Phase 2's model existing or working.
If phase2-proxy-classifier isn't installed/trained yet, this module degrades gracefully to
RiskTier.MODEL_UNAVAILABLE and the rest of the app (exposure intake, dashboard) works exactly
the same — this is the PRD's "ship the wedge that doesn't depend on the model working"
principle, implemented as an actual code boundary rather than just a project-planning idea.
"""

import logging
import os
import uuid

import numpy as np

from app.models import RiskTier
from app.privacy import delete_audio_file

logger = logging.getLogger("saans_check.audio_pipeline")

AUDIO_TEMP_DIR = os.getenv("AUDIO_TEMP_DIR", "/tmp/saans_check_audio")
os.makedirs(AUDIO_TEMP_DIR, exist_ok=True)

# Lazy-loaded so importing this module never fails even if phase2's dependencies
# (tensorflow/tensorflow-hub for YAMNet) aren't installed in this deployment.
_classifier_pipeline = None
_classifier_load_attempted = False


def _try_load_classifier():
    global _classifier_pipeline, _classifier_load_attempted
    if _classifier_load_attempted:
        return _classifier_pipeline
    _classifier_load_attempted = True
    try:
        # This import reaches into phase2-proxy-classifier/src. In a real deployment, the
        # phase2 package would be pip-installed (see phase2-proxy-classifier/setup.py); in this
        # repo layout, set PYTHONPATH to include phase2-proxy-classifier/src, or copy the
        # inference module in directly. We attempt both.
        import sys

        phase2_src = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "phase2-proxy-classifier", "src"
        )
        if os.path.isdir(phase2_src) and phase2_src not in sys.path:
            sys.path.insert(0, phase2_src)

        from inference import ProxyClassifierPipeline  # type: ignore

        model_path = os.getenv("STAGE1_MODEL_PATH")
        if not model_path or not os.path.exists(model_path):
            logger.warning(
                "STAGE1_MODEL_PATH not set or file missing — running in Phase 1 standalone "
                "mode (no acoustic classifier). This is expected and fine if you haven't run "
                "phase2-proxy-classifier/src/train_classifier.py yet."
            )
            return None

        _classifier_pipeline = ProxyClassifierPipeline.load(model_path)
        logger.info("Loaded Stage-1 proxy classifier from %s", model_path)
    except ImportError as e:
        logger.warning(
            "Could not import phase2 classifier pipeline (%s) — running in Phase 1 "
            "standalone mode. Install phase2-proxy-classifier/requirements.txt to enable.",
            e,
        )
        _classifier_pipeline = None
    return _classifier_pipeline


def save_temp_audio(audio_bytes: bytes, suffix: str = ".wav") -> str:
    filename = f"{uuid.uuid4()}{suffix}"
    filepath = os.path.join(AUDIO_TEMP_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(audio_bytes)
    return filepath


def process_submission_audio(
    audio_bytes: bytes, retain_audio: bool = False
) -> tuple[RiskTier, float | None, str | None]:
    """
    Full pipeline: save -> (preprocess + embed + classify) -> delete (unless consented to retain).

    Returns (risk_tier, raw_model_score_or_None, model_version_or_None).

    If no classifier is available, returns (MODEL_UNAVAILABLE, None, None) — this is a normal,
    expected return value in Phase 1 standalone deployments, not an error state.
    """
    filepath = save_temp_audio(audio_bytes)
    pipeline = _try_load_classifier()

    try:
        if pipeline is None:
            return RiskTier.MODEL_UNAVAILABLE, None, None

        score, model_version = pipeline.predict(filepath)
        # Threshold is set conservatively per the proxy classifier's own validation
        # (see phase2-proxy-classifier — threshold tuned for higher recall on "elevated" given
        # the asymmetric-caution principle: PRD §3.3, a missed elevated flag is worse than an
        # extra false alarm).
        tier = RiskTier.ELEVATED_PROXY if score >= pipeline.elevated_threshold else RiskTier.NORMAL_PROXY
        return tier, float(score), model_version

    finally:
        if not retain_audio:
            delete_audio_file(filepath)
        else:
            logger.info(
                "Retaining audio at %s per explicit_audio_retention_consent — "
                "ensure this path is included in any data-retention audit.",
                filepath,
            )
