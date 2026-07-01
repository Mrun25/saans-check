"""
Schema for Phase 3 paired clinical data: cough recording + confirmed X-ray/spirometry diagnosis.

This is the schema the retraining script (scripts/retrain_stage2.py) expects once real data
exists. It does NOT exist as a populated database anywhere — this file defines the target
shape so that when a partnership produces real data, the collection tooling and the retraining
code agree on format from day one, rather than improvising a schema under time pressure once
data starts arriving.

Field design follows the same privacy principles as Phase 1 (see ../../docs/architecture.md):
identifying information is kept in a separate table from clinical/audio data, linked only by a
random participant_id, with the link itself restricted to specifically named roles per the
consent form.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class DiagnosisMethod(str, Enum):
    CHEST_XRAY_ILO = "chest_xray_ilo"  # ILO International Classification of Radiographs of
    # Pneumoconioses — the actual clinical standard for radiographic silicosis staging
    SPIROMETRY = "spirometry"
    BOTH = "both"


class SilicosisStage(str, Enum):
    """
    Per the ILO classification system actually used in Indian Pneumoconiosis Board
    certification (referenced in PRD §1.1, §5). Category 0 = no pneumoconiosis;
    categories 1-3 reflect increasing profusion of small opacities on chest X-ray.
    This is the real clinical staging system, not a simplified invented one — using the
    actual standard means Phase 3 data is directly comparable to existing Pneumoconiosis
    Board records, which matters for partner organizations who already use this system.
    """

    CATEGORY_0 = "0"  # no pneumoconiosis
    CATEGORY_1 = "1"
    CATEGORY_2 = "2"
    CATEGORY_3 = "3"
    PROGRESSIVE_MASSIVE_FIBROSIS = "pmf"  # complicated/advanced silicosis


@dataclass
class ClinicalDiagnosisRecord:
    """
    Populated by the partner clinic's own diagnostic process — Saans Check does not perform
    or interpret X-rays/spirometry itself, only links to results already produced by qualified
    clinicians, per PRD §3.2 ("not a replacement for X-ray/spirometry").
    """

    participant_id: str  # random UUID, generated at consent time — never a name or government ID
    diagnosis_method: DiagnosisMethod
    silicosis_stage: SilicosisStage | None  # None if spirometry-only and no radiograph done
    spirometry_fvc_pct_predicted: float | None
    spirometry_fev1_pct_predicted: float | None
    diagnosing_clinician_id: str  # clinician's own ID/registration, not patient-identifying
    diagnosis_date: date
    diagnosing_facility: str  # e.g. "K.N. Chest Hospital, Jodhpur"


@dataclass
class PairedExposureRecord:
    """Same shape as Phase 1's exposure intake (see ../../phase1-intake-app/backend/app/models.py
    Submission table) — deliberately kept consistent so Phase 1 -> Phase 3 data isn't a format
    migration, just an additional clinical_diagnosis field being attached."""

    participant_id: str
    years_of_exposure: float
    mask_usage_frequency: str
    dust_suppression_at_site: str | None
    site_id: str
    symptoms: list[str] = field(default_factory=list)


@dataclass
class PairedAudioRecord:
    """
    The actual cough recording, linked by participant_id. Unlike Phase 1's default behavior
    (delete audio post-embedding), Phase 3 audio IS retained — this is a research dataset whose
    entire purpose is the audio, with explicit informed consent covering exactly this retention
    (see consent_forms/consent_form_draft.md). The retention exception is intentional and
    consent-gated, not a quiet relaxation of Phase 1's privacy default.
    """

    participant_id: str
    audio_filepath: str  # stored in a access-controlled location, never publicly hosted
    recording_date: date
    recording_device_model: str | None
    consent_form_id: str  # reference to the specific signed consent record


@dataclass
class PairedTrainingExample:
    """The final joined record retrain_stage2.py actually consumes."""

    participant_id: str
    audio_filepath: str
    silicosis_label: int  # 1 if silicosis_stage in {1, 2, 3, pmf}, 0 if CATEGORY_0 — the binary
    # collapse retrain_stage2.py applies, mirroring phase2's binary design (PRD §4.2.D)
    exposure: PairedExposureRecord
    diagnosis: ClinicalDiagnosisRecord
