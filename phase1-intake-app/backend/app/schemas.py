from datetime import datetime
import json

from pydantic import BaseModel, Field, field_validator

from app.models import RiskTier


class SubmissionCreate(BaseModel):
    device_token: str
    site_code: str
    years_of_exposure: float = Field(ge=0, le=80)
    mask_usage_frequency: str
    dust_suppression_at_site: str | None = None
    symptoms: list[str] = Field(default_factory=list)
    explicit_audio_retention_consent: bool = False
    language: str = "hi"

    @field_validator("mask_usage_frequency")
    @classmethod
    def validate_mask_usage(cls, v: str) -> str:
        allowed = {"never", "sometimes", "most_of_time", "always"}
        if v not in allowed:
            raise ValueError(f"mask_usage_frequency must be one of {allowed}")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        allowed = {"hi", "mwr", "gu", "en"}
        if v not in allowed:
            raise ValueError(f"language must be one of {allowed}")
        return v


class SubmissionResult(BaseModel):
    submission_id: str
    risk_tier: RiskTier
    message: str
    proxy_disclaimer: str | None = None
    model_version: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class SiteCreate(BaseModel):
    site_code: str
    district: str
    state: str = "Rajasthan"
    notes: str | None = None


class SiteOut(BaseModel):
    id: str
    site_code: str
    district: str
    state: str

    class Config:
        from_attributes = True


class AggregateSiteStatsOut(BaseModel):
    """This — and only this — is what the dashboard's API returns. Notice the complete absence
    of device_token, raw_model_score, or any per-worker field. See app/privacy.py."""

    site_id: str
    site_code: str
    district: str
    period_start: datetime
    period_end: datetime
    total_submissions: int
    normal_proxy_count: int
    elevated_proxy_count: int
    no_audio_count: int
    elevated_rate_pct: float
    avg_years_exposure: float | None
    pct_never_mask: float | None
    pct_no_dust_suppression: float | None


def symptoms_to_json(symptoms: list[str]) -> str:
    return json.dumps(symptoms)


def symptoms_from_json(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []
