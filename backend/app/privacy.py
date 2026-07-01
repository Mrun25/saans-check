"""
Privacy boundary enforcement (PRD §4.3, §5).

This module exists so the "no employer access to individual results" and "audio deleted by
default" guarantees are a single, auditable code path rather than a policy that depends on every
endpoint developer remembering to follow it correctly.

Any new endpoint that touches audio or individual-level results MUST go through these functions.
Code review checklist item: does this PR call delete_audio_file() after embedding? Does this PR
ever return raw_model_score or device_token to a non-worker-facing endpoint?
"""

import logging
import os

logger = logging.getLogger("saans_check.privacy")

# Fields that must NEVER appear in any dashboard-facing API response or export.
# Enforced in app/routers/dashboard.py via the AggregateSiteStats-only query boundary,
# and checked here as a defensive second layer for any ad-hoc export script.
FORBIDDEN_IN_AGGREGATE_EXPORTS = {
    "device_token",
    "raw_model_score",
    "has_symptoms_checklist",  # free-text symptom data is individual-level, not for export
}


def delete_audio_file(filepath: str) -> None:
    """
    Delete a raw audio file from disk. Called immediately after embedding extraction
    in app/audio_pipeline.py, UNLESS the submission has explicit_audio_retention_consent=True.

    This is intentionally a hard delete (os.remove), not a soft-delete flag, because the
    threat model here is "audio sitting on a server is itself the risk" — there's no use case
    in this product where a deleted-by-default file needs to be recoverable later.
    """
    if not os.path.exists(filepath):
        logger.warning("Attempted to delete non-existent audio file: %s", filepath)
        return
    os.remove(filepath)
    logger.info("Deleted raw audio file post-embedding: %s", filepath)


def assert_safe_for_export(record: dict) -> dict:
    """
    Defensive check: strip any forbidden field before a record leaves the system via export,
    API response, or dashboard query. Raises if called on a record that shouldn't exist in an
    aggregate context at all (i.e. it still has a device_token — it's an individual record that
    was about to leak into an aggregate-only pathway).
    """
    if "device_token" in record:
        raise ValueError(
            "Refusing to export a record containing device_token. This indicates an "
            "individual-level record is being routed through an aggregate-export path — "
            "check the calling code in app/routers/dashboard.py."
        )
    return {k: v for k, v in record.items() if k not in FORBIDDEN_IN_AGGREGATE_EXPORTS}


def employer_access_check(requesting_role: str) -> None:
    """
    There is no code path in this application where requesting_role == "employer" is a valid
    value at all — employer accounts are not a concept this schema supports, by design (PRD §5:
    "No data pipeline should allow an employer to access individual worker results").

    This function exists as an explicit tripwire: if anyone ever adds an employer-facing role
    to the auth system in the future, this raise is what should force them to re-read PRD §5
    and this module's docstring before proceeding.
    """
    if requesting_role == "employer":
        raise PermissionError(
            "Employer-role access is not supported by this application's data model. "
            "See PRD §5 and docs/architecture.md before adding this capability."
        )
