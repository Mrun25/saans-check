"""
Database models for Saans Check Phase 1.

Privacy design (see docs/architecture.md and PRD §4.3):
- IndividualResult is keyed to a per-device anonymous token, NOT a name, phone number, or
  Aadhaar/government ID. Nothing in this schema can be used by an employer to identify a worker.
- AggregateSiteStats is the ONLY table the NGO/welfare-board dashboard reads from. It is
  populated by a nightly rollup job (see app/aggregation.py), never written to directly by
  worker-facing endpoints.
- Raw audio is never stored in the database. It exists on disk only transiently during
  preprocessing+embedding (see app/audio_pipeline.py) and is deleted immediately afterward
  unless explicit_audio_retention_consent is True.
"""

from datetime import datetime
import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def gen_uuid() -> str:
    return str(uuid.uuid4())


class RiskTier(str, enum.Enum):
    """
    Output of the Stage-1 proxy classifier, per PRD §3.2/§4.2.E.
    This is explicitly NOT a silicosis diagnosis. See result_copy.py for the exact
    user-facing language tied to each tier — it is intentionally hedged.
    """

    NORMAL_PROXY = "normal_proxy"  # cough pattern looks typical of the proxy training distribution
    ELEVATED_PROXY = "elevated_proxy"  # cough pattern resembles distress patterns in proxy data
    NO_AUDIO_SUBMITTED = "no_audio_submitted"  # worker completed exposure intake only, no recording
    MODEL_UNAVAILABLE = "model_unavailable"  # Phase 1 standalone mode, no classifier deployed at all


class Site(Base):
    """A quarry, mine, or stone-processing site. Identified by a short code, not GPS pin,
    to avoid the dashboard itself becoming a tool to locate informal/unregistered mines."""

    __tablename__ = "sites"

    id = Column(String, primary_key=True, default=gen_uuid)
    site_code = Column(String, unique=True, nullable=False)  # e.g. "JDH-KaliBeri-01"
    district = Column(String, nullable=False)
    state = Column(String, nullable=False, default="Rajasthan")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    submissions = relationship("Submission", back_populates="site")


class Submission(Base):
    """
    One worker's visit: exposure intake + optional audio-derived result.

    `device_token` is a random UUID generated client-side and stored in browser-local state,
    NOT tied to any worker-identifying info. It exists only so a worker can see their own
    history across repeat visits on the same device; it is never exported to the dashboard.
    """

    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=gen_uuid)
    device_token = Column(String, nullable=False, index=True)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)

    # --- Exposure context (PRD §3.3 — this is the core safety requirement, not a nicety) ---
    years_of_exposure = Column(Float, nullable=False)
    mask_usage_frequency = Column(
        String, nullable=False
    )  # "never" | "sometimes" | "most_of_time" | "always"
    dust_suppression_at_site = Column(
        String, nullable=True
    )  # "none" | "some" | "wet_drilling" | "unknown"
    has_symptoms_checklist = Column(Text, nullable=True)  # JSON-encoded list of symptom strings

    # --- Acoustic model output (optional — Phase 1 can run with this entirely null) ---
    risk_tier = Column(Enum(RiskTier), nullable=False, default=RiskTier.NO_AUDIO_SUBMITTED)
    model_version = Column(String, nullable=True)  # e.g. "stage1_proxy_v1" — for auditability
    raw_model_score = Column(Float, nullable=True)  # internal only, never shown to worker as-is

    # --- Consent and retention ---
    explicit_audio_retention_consent = Column(Boolean, nullable=False, default=False)
    consent_timestamp = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    language = Column(String, nullable=False, default="hi")  # "hi" | "mwr" | "gu" | "en"

    site = relationship("Site", back_populates="submissions")


class AggregateSiteStats(Base):
    """
    The ONLY table the dashboard queries. Populated by app/aggregation.py on a schedule.
    No field here can be traced back to an individual worker.
    """

    __tablename__ = "aggregate_site_stats"

    id = Column(String, primary_key=True, default=gen_uuid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    total_submissions = Column(Integer, default=0)
    normal_proxy_count = Column(Integer, default=0)
    elevated_proxy_count = Column(Integer, default=0)
    no_audio_count = Column(Integer, default=0)

    avg_years_exposure = Column(Float, nullable=True)
    pct_never_mask = Column(Float, nullable=True)
    pct_no_dust_suppression = Column(Float, nullable=True)

    computed_at = Column(DateTime, default=datetime.utcnow)
