"""
Google HeAR (Health Acoustic Representations) embedding wrapper — Phase 4 upgrade path
(PRD §4.2.C v2, §6 Phase 4).

Implements the SAME embed(audio_array, sample_rate) -> np.ndarray interface as
phase2-proxy-classifier/src/embed_yamnet.py, so the classifier head and inference pipeline
require zero changes when swapping the embedding backend — only this module and the
STAGE1_MODEL_PATH/embedding-source config need to change (see docs/architecture.md, "Why Phase
1 and Phase 2 are decoupled" / Phase 4 integration points section).

ACCESS STATUS (confirmed June 2026): HeAR is not an open download like YAMNet. Access requires
a request to Google, reviewed case-by-case — this module cannot be tested against the real
model without that access being granted first. This file is the integration code, ready to
activate the moment access exists; it is not itself a substitute for getting that access.

To request access: the published pathway (as of this research) is via Google's Health AI
Developer Foundations (HAI-DEF) program request form, with a Google Cloud-mediated review
process — search "Google HAI-DEF HeAR access request" for the current form, since intake
processes for gated research models commonly move between specific URLs. Salcit Technologies'
Swaasa product (PRD §2) is the existing production example of a partner who has this access —
worth mentioning in any access request as the precedent for an Indian occupational-health use
case specifically.
"""

import logging

import numpy as np

logger = logging.getLogger("phase4.hear_embedder")

HEAR_EXPECTED_SAMPLE_RATE = 16000  # matches YAMNet's expected rate; verify against HeAR's
# actual published spec once access is granted — this is inferred from HeAR's training data
# description (313M clips, health-acoustic foundation model) following common practice for
# this model class, not confirmed against HeAR's own technical documentation, which is not
# publicly available without access.

_hear_client = None


def _load_hear_client():
    """
    Placeholder for whatever HeAR's actual access pattern turns out to be — based on Google's
    published pattern for gated health foundation models, this is likely either:
    (a) a Vertex AI model endpoint reached via the google-cloud-aiplatform SDK, or
    (b) a downloadable checkpoint provided directly after an approved access request.

    This function intentionally raises NotImplementedError rather than guessing at an SDK
    call structure that would silently fail or, worse, silently succeed against the wrong
    endpoint. Once Google's access grant specifies the actual integration method, replace this
    function body with the real client initialization — do not leave embed() below
    "working" against a guessed-at, untested API surface.
    """
    raise NotImplementedError(
        "HeAR access has not been granted/configured yet. See this module's docstring for the "
        "request pathway. Once access exists, implement the actual client here based on "
        "Google's provided integration instructions — do not guess at the API surface."
    )


def embed(audio_array: np.ndarray, sample_rate: int = HEAR_EXPECTED_SAMPLE_RATE) -> np.ndarray:
    """
    Mirrors embed_yamnet.embed()'s exact signature and contract: same input shape expectations,
    same raise-on-wrong-sample-rate behavior. The classifier head trained against YAMNet
    embeddings will need RETRAINING against HeAR embeddings — frozen embedding spaces from
    different models are not interchangeable even though the calling interface is identical.
    This is a backend swap at the embedding layer, not a drop-in replacement at the classifier
    layer — update train_classifier.py's --embeddings input to point at HeAR-extracted .npz
    files, then retrain, rather than expecting an existing YAMNet-trained .pkl to work unchanged.
    """
    if sample_rate != HEAR_EXPECTED_SAMPLE_RATE:
        raise ValueError(
            f"HeAR expects {HEAR_EXPECTED_SAMPLE_RATE}Hz audio (per inference from published "
            f"training description — confirm against actual HeAR docs once access is granted), "
            f"got {sample_rate}Hz."
        )
    if audio_array.ndim != 1:
        raise ValueError(f"Expected mono 1D audio array, got shape {audio_array.shape}")

    client = _load_hear_client()
    raise NotImplementedError("Implement the real HeAR inference call once client access exists.")
