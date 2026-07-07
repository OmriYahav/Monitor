from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.models import Alert, Device, DeviceCheck

PROBLEM_TITLE = "Device is offline"

def evaluate_device(db: Session, device: Device) -> None:
    recent = db.scalars(select(DeviceCheck).where(DeviceCheck.device_id == device.id).order_by(DeviceCheck.checked_at.desc()).limit(3)).all()
    failed_three = len(recent) == 3 and all(not c.success for c in recent)
    unavailable_long = device.status == "offline" and device.last_seen is not None and device.last_seen < datetime.now(timezone.utc) - timedelta(seconds=180)
    open_alert = db.scalars(select(Alert).where(Alert.device_id == device.id, Alert.title == PROBLEM_TITLE, Alert.status.in_(["open", "acknowledged"]))).first()
    if device.status == "online" and open_alert:
        open_alert.status = "resolved"; open_alert.resolved_at = datetime.now(timezone.utc); return
    if (failed_three or unavailable_long) and not open_alert:
        db.add(Alert(device_id=device.id, severity="critical", status="open", title=PROBLEM_TITLE, message=f"{device.name} ({device.ip_address}) is unavailable.", started_at=datetime.now(timezone.utc)))
