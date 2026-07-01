import pytest
from datetime import datetime, timedelta
from app.privacy import (
    assert_safe_for_export,
    employer_access_check,
    FORBIDDEN_IN_AGGREGATE_EXPORTS
)
from app.aggregation import MINIMUM_COHORT_SIZE, compute_site_aggregate
from app.models import Site, Submission, RiskTier
from unittest.mock import Mock, MagicMock

def test_assert_safe_for_export_strips_forbidden_fields():
    record = {
        "site_id": 1,
        "total_submissions": 10,
        "raw_model_score": 0.85, # forbidden
        "has_symptoms_checklist": True, # forbidden
    }
    safe_record = assert_safe_for_export(record)
    assert "site_id" in safe_record
    assert "total_submissions" in safe_record
    assert "raw_model_score" not in safe_record
    assert "has_symptoms_checklist" not in safe_record

def test_assert_safe_for_export_raises_on_device_token():
    record = {
        "site_id": 1,
        "device_token": "abc-123", # explicitly triggers exception
        "total_submissions": 10
    }
    with pytest.raises(ValueError, match="Refusing to export a record containing device_token"):
        assert_safe_for_export(record)

def test_employer_access_check():
    with pytest.raises(PermissionError, match="Employer-role access is not supported"):
        employer_access_check("employer")
    
    # Should not raise for other roles
    employer_access_check("ngo_admin")

def test_compute_site_aggregate_minimum_cohort_enforced():
    # Setup mock db and site
    db = MagicMock()
    site = Site(id=1, site_code="TEST01")
    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()

    # Create fewer submissions than MINIMUM_COHORT_SIZE
    mock_submissions = []
    for i in range(MINIMUM_COHORT_SIZE - 1):
        s = Submission(
            site_id=1, 
            risk_tier=RiskTier.NORMAL_PROXY, 
            years_of_exposure=5.0, 
            mask_usage_frequency="always",
            dust_suppression_at_site="water_sprays"
        )
        mock_submissions.append(s)

    db.query.return_value.filter.return_value.all.return_value = mock_submissions

    agg = compute_site_aggregate(db, site, start, end)
    # Should return None because it's below minimum cohort size
    assert agg is None

def test_compute_site_aggregate_calculates_correctly():
    db = MagicMock()
    site = Site(id=1, site_code="TEST01")
    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()

    # Create exactly MINIMUM_COHORT_SIZE submissions
    mock_submissions = []
    for i in range(MINIMUM_COHORT_SIZE):
        tier = RiskTier.NORMAL_PROXY if i % 2 == 0 else RiskTier.ELEVATED_PROXY
        mask = "never" if i == 0 else "always"
        s = Submission(
            site_id=1, 
            risk_tier=tier, 
            years_of_exposure=10.0, 
            mask_usage_frequency=mask,
            dust_suppression_at_site="none"
        )
        mock_submissions.append(s)

    db.query.return_value.filter.return_value.all.return_value = mock_submissions

    agg = compute_site_aggregate(db, site, start, end)
    assert agg is not None
    assert agg.total_submissions == MINIMUM_COHORT_SIZE
    assert agg.avg_years_exposure == 10.0
    # 1 out of MINIMUM_COHORT_SIZE has "never" mask usage
    assert agg.pct_never_mask == round(100 * 1 / MINIMUM_COHORT_SIZE, 1)
    assert agg.pct_no_dust_suppression == 100.0
