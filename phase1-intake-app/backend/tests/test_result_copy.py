import pytest
from app.models import RiskTier
from app.result_copy import (
    ExposureRiskFlags,
    compute_exposure_flags,
    build_result_message,
    _RESULT_STRINGS,
    _EXPOSURE_REMINDER,
)

def test_compute_exposure_flags():
    # High risk
    flags = compute_exposure_flags(12.0, "never", "none")
    assert flags.high_years_exposure is True
    assert flags.poor_mask_usage is True
    assert flags.poor_dust_suppression is True
    
    # Low risk
    flags = compute_exposure_flags(5.0, "always", "water_sprays")
    assert flags.high_years_exposure is False
    assert flags.poor_mask_usage is False
    assert flags.poor_dust_suppression is False
    
    # Borderline
    flags = compute_exposure_flags(10.0, "sometimes", "unknown")
    assert flags.high_years_exposure is True
    assert flags.poor_mask_usage is True
    assert flags.poor_dust_suppression is True

def test_build_result_message_normal_high_exposure():
    # Asymmetric-caution logic: normal result + high exposure should ALWAYS append reminder.
    flags = ExposureRiskFlags(high_years_exposure=True, poor_mask_usage=False, poor_dust_suppression=False)
    msg = build_result_message(RiskTier.NORMAL_PROXY, flags, "en")
    assert _RESULT_STRINGS["en"][RiskTier.NORMAL_PROXY] in msg
    assert _EXPOSURE_REMINDER["en"] in msg

def test_build_result_message_normal_low_exposure():
    # Normal result + low exposure should NOT append reminder.
    flags = ExposureRiskFlags(high_years_exposure=False, poor_mask_usage=False, poor_dust_suppression=False)
    msg = build_result_message(RiskTier.NORMAL_PROXY, flags, "en")
    assert _RESULT_STRINGS["en"][RiskTier.NORMAL_PROXY] in msg
    assert _EXPOSURE_REMINDER["en"] not in msg

def test_build_result_message_elevated_high_exposure():
    # Elevated result should NOT append the generic normal exposure reminder.
    flags = ExposureRiskFlags(high_years_exposure=True, poor_mask_usage=True, poor_dust_suppression=True)
    msg = build_result_message(RiskTier.ELEVATED_PROXY, flags, "en")
    assert _RESULT_STRINGS["en"][RiskTier.ELEVATED_PROXY] in msg
    assert _EXPOSURE_REMINDER["en"] not in msg

def test_build_result_message_fallback_language():
    flags = ExposureRiskFlags(high_years_exposure=False, poor_mask_usage=False, poor_dust_suppression=False)
    msg = build_result_message(RiskTier.NORMAL_PROXY, flags, "fr")
    # Should fallback to 'hi'
    assert _RESULT_STRINGS["hi"][RiskTier.NORMAL_PROXY] in msg
