from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AggregateSiteStats, Site
from app.schemas import AggregateSiteStatsOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/hotspots", response_model=list[AggregateSiteStatsOut])
def get_hotspots(db: Session = Depends(get_db)):
    """
    The camp-prioritization view (PRD §4.2.F). Returns the most recent aggregate snapshot per
    site, sorted by elevated_rate_pct descending — i.e. "send the next camp here first."

    Reads ONLY from AggregateSiteStats. There is no parameter on this endpoint, and no other
    endpoint in this router, that can return an individual Submission row. That's enforced by
    construction here (the query never touches the Submission table), not just by convention.
    """
    rows = (
        db.query(AggregateSiteStats, Site)
        .join(Site, Site.id == AggregateSiteStats.site_id)
        .order_by(AggregateSiteStats.computed_at.desc())
        .all()
    )

    # Keep only the latest aggregate row per site
    latest_by_site: dict[str, tuple] = {}
    for agg, site in rows:
        if site.id not in latest_by_site:
            latest_by_site[site.id] = (agg, site)

    results = []
    for agg, site in latest_by_site.values():
        elevated_rate = (
            round(100 * agg.elevated_proxy_count / agg.total_submissions, 1)
            if agg.total_submissions
            else 0.0
        )
        results.append(
            AggregateSiteStatsOut(
                site_id=site.id,
                site_code=site.site_code,
                district=site.district,
                period_start=agg.period_start,
                period_end=agg.period_end,
                total_submissions=agg.total_submissions,
                normal_proxy_count=agg.normal_proxy_count,
                elevated_proxy_count=agg.elevated_proxy_count,
                no_audio_count=agg.no_audio_count,
                elevated_rate_pct=elevated_rate,
                avg_years_exposure=agg.avg_years_exposure,
                pct_never_mask=agg.pct_never_mask,
                pct_no_dust_suppression=agg.pct_no_dust_suppression,
            )
        )

    results.sort(key=lambda r: r.elevated_rate_pct, reverse=True)
    return results
