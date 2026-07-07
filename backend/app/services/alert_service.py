from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.models.models import Alert

def list_alerts(db: Session):
    return db.scalars(select(Alert).options(joinedload(Alert.device)).order_by(Alert.started_at.desc())).unique().all()
def _get(db: Session, alert_id: UUID):
    alert = db.get(Alert, alert_id)
    if not alert: raise HTTPException(404, "Alert not found")
    return alert
def acknowledge(db: Session, alert_id: UUID):
    alert = _get(db, alert_id); alert.status = "acknowledged"; alert.acknowledged_at = datetime.now(timezone.utc); db.commit(); db.refresh(alert); return alert
def resolve(db: Session, alert_id: UUID):
    alert = _get(db, alert_id); alert.status = "resolved"; alert.resolved_at = datetime.now(timezone.utc); db.commit(); db.refresh(alert); return alert
