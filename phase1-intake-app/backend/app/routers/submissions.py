from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.audio_pipeline import process_submission_audio
from app.database import get_db
from app.models import RiskTier, Site, Submission
from app.result_copy import build_proxy_disclaimer, build_result_message, compute_exposure_flags
from app.schemas import SubmissionCreate, SubmissionResult, symptoms_to_json

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10MB — generous ceiling for a ~30s mono clip


@router.post("", response_model=SubmissionResult)
async def create_submission(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
):
    """
    Exposure intake WITHOUT audio. This endpoint alone is enough to run Phase 1 standalone
    (PRD §6, Phase 1 goal). Use POST /api/submissions/{id}/audio afterward if a recording
    is being submitted too — they're separate calls so a flaky mobile connection dropping the
    (larger) audio upload never loses the (smaller, more important) exposure data.
    """
    site = db.query(Site).filter(Site.site_code == payload.site_code).first()
    if not site:
        raise HTTPException(status_code=404, detail=f"Unknown site_code: {payload.site_code}")

    submission = Submission(
        device_token=payload.device_token,
        site_id=site.id,
        years_of_exposure=payload.years_of_exposure,
        mask_usage_frequency=payload.mask_usage_frequency,
        dust_suppression_at_site=payload.dust_suppression_at_site,
        has_symptoms_checklist=symptoms_to_json(payload.symptoms),
        risk_tier=RiskTier.NO_AUDIO_SUBMITTED,
        explicit_audio_retention_consent=payload.explicit_audio_retention_consent,
        consent_timestamp=datetime.utcnow() if payload.explicit_audio_retention_consent else None,
        language=payload.language,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    flags = compute_exposure_flags(
        payload.years_of_exposure, payload.mask_usage_frequency, payload.dust_suppression_at_site
    )
    message = build_result_message(submission.risk_tier, flags, payload.language)

    return SubmissionResult(
        submission_id=submission.id,
        risk_tier=submission.risk_tier,
        message=message,
        proxy_disclaimer=None,
        model_version=None,
        created_at=submission.created_at,
    )


@router.post("/{submission_id}/audio", response_model=SubmissionResult)
async def attach_audio(
    submission_id: str,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Attach a cough recording to an existing submission and run it through the Stage-1 proxy
    classifier, if one is deployed. Gracefully returns MODEL_UNAVAILABLE if not — see
    app/audio_pipeline.py. This is the only place in the entire backend that audio bytes exist.
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio file too large (max 10MB)")
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")

    risk_tier, raw_score, model_version = process_submission_audio(
        audio_bytes, retain_audio=submission.explicit_audio_retention_consent
    )

    submission.risk_tier = risk_tier
    submission.raw_model_score = raw_score
    submission.model_version = model_version
    db.commit()
    db.refresh(submission)

    flags = compute_exposure_flags(
        submission.years_of_exposure,
        submission.mask_usage_frequency,
        submission.dust_suppression_at_site,
    )
    message = build_result_message(risk_tier, flags, submission.language)
    disclaimer = (
        build_proxy_disclaimer(submission.language)
        if model_version and model_version.startswith("stage1_proxy")
        else None
    )

    return SubmissionResult(
        submission_id=submission.id,
        risk_tier=risk_tier,
        message=message,
        proxy_disclaimer=disclaimer,
        model_version=model_version,
        created_at=submission.created_at,
    )
