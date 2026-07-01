"""
Nightly (or on-demand) rollup job: Submission rows -> AggregateSiteStats rows.

This is the ONLY code path permitted to read individual Submission rows and produce something
the dashboard can see. It deliberately never returns or logs device_token, raw_model_score, or
symptom free text in its output — see app/privacy.py for the enforced boundary.

Run as: python -m app.aggregation  (or schedule via cron/Celery in production)
"""

from datetime import datetime, timedelta
import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.models import AggregateSiteStats, RiskTier, Site, Submission

logger = logging.getLogger("saans_check.aggregation")

MINIMUM_COHORT_SIZE = 5  # don't publish a site-level stat for fewer than N submissions —
# a tiny cohort risks re-identifying individuals even in "aggregate" form.


def compute_site_aggregate(db: Session, site: Site, period_start: datetime, period_end: datetime):
    submissions = (
        db.query(Submission)
        .filter(
            Submission.site_id == site.id,
            Submission.created_at >= period_start,
            Submission.created_at < period_end,
        )
        .all()
    )

    total = len(submissions)
    if total < MINIMUM_COHORT_SIZE:
        logger.info(
            "Skipping aggregate for site %s (period %s–%s): only %d submissions, "
            "below MINIMUM_COHORT_SIZE=%d",
            site.site_code,
            period_start.date(),
            period_end.date(),
            total,
            MINIMUM_COHORT_SIZE,
        )
        return None

    normal_count = sum(1 for s in submissions if s.risk_tier == RiskTier.NORMAL_PROXY)
    elevated_count = sum(1 for s in submissions if s.risk_tier == RiskTier.ELEVATED_PROXY)
    no_audio_count = sum(1 for s in submissions if s.risk_tier == RiskTier.NO_AUDIO_SUBMITTED)

    avg_years = sum(s.years_of_exposure for s in submissions) / total
    never_mask_count = sum(1 for s in submissions if s.mask_usage_frequency == "never")
    no_dust_supp_count = sum(
        1 for s in submissions if s.dust_suppression_at_site in (None, "none", "unknown")
    )

    return AggregateSiteStats(
        site_id=site.id,
        period_start=period_start,
        period_end=period_end,
        total_submissions=total,
        normal_proxy_count=normal_count,
        elevated_proxy_count=elevated_count,
        no_audio_count=no_audio_count,
        avg_years_exposure=round(avg_years, 1),
        pct_never_mask=round(100 * never_mask_count / total, 1),
        pct_no_dust_suppression=round(100 * no_dust_supp_count / total, 1),
    )


def run_daily_rollup(db: Session | None = None, days_back: int = 1):
    """Compute aggregates for the trailing `days_back` days for every site."""
    owns_session = db is None
    db = db or SessionLocal()
    try:
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=days_back)

        sites = db.query(Site).all()
        created = 0
        for site in sites:
            agg = compute_site_aggregate(db, site, period_start, period_end)
            if agg:
                db.add(agg)
                created += 1
        db.commit()
        logger.info("Rollup complete: %d aggregate rows created across %d sites", created, len(sites))
    finally:
        if owns_session:
            db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    run_daily_rollup()
