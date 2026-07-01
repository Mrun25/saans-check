from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Site
from app.schemas import SiteCreate, SiteOut

router = APIRouter(prefix="/api/sites", tags=["sites"])


@router.post("", response_model=SiteOut)
def create_site(payload: SiteCreate, db: Session = Depends(get_db)):
    existing = db.query(Site).filter(Site.site_code == payload.site_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="site_code already exists")
    site = Site(
        site_code=payload.site_code,
        district=payload.district,
        state=payload.state,
        notes=payload.notes,
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("", response_model=list[SiteOut])
def list_sites(db: Session = Depends(get_db)):
    return db.query(Site).all()
