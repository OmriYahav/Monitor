from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.models import Site
from app.schemas.schemas import SiteCreate, SiteUpdate

def list_sites(db: Session): return db.scalars(select(Site).order_by(Site.name)).all()
def get_site(db: Session, site_id: UUID):
    site = db.get(Site, site_id)
    if not site: raise HTTPException(404, "Site not found")
    return site
def create_site(db: Session, data: SiteCreate):
    site = Site(**data.model_dump()); db.add(site); db.commit(); db.refresh(site); return site
def update_site(db: Session, site_id: UUID, data: SiteUpdate):
    site = get_site(db, site_id)
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(site,k,v)
    db.commit(); db.refresh(site); return site
def delete_site(db: Session, site_id: UUID):
    db.delete(get_site(db, site_id)); db.commit()
