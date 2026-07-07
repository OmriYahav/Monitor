from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.models.models import Device, DeviceCheck
from app.schemas.schemas import DeviceCreate, DeviceUpdate

def list_devices(db: Session): return db.scalars(select(Device).options(joinedload(Device.site)).order_by(Device.name)).unique().all()
def get_device(db: Session, device_id: UUID):
    device = db.scalar(select(Device).options(joinedload(Device.site)).where(Device.id == device_id))
    if not device: raise HTTPException(404, "Device not found")
    return device
def create_device(db: Session, data: DeviceCreate):
    device = Device(**data.model_dump(), status="unknown")
    db.add(device); db.commit(); db.refresh(device); return device
def update_device(db: Session, device_id: UUID, data: DeviceUpdate):
    device = get_device(db, device_id)
    for key, value in data.model_dump(exclude_unset=True).items(): setattr(device, key, value)
    db.commit(); db.refresh(device); return get_device(db, device.id)
def delete_device(db: Session, device_id: UUID):
    device = get_device(db, device_id); db.delete(device); db.commit()
def list_checks(db: Session, device_id: UUID, limit: int = 100):
    get_device(db, device_id)
    return db.scalars(select(DeviceCheck).where(DeviceCheck.device_id == device_id).order_by(DeviceCheck.checked_at.desc()).limit(limit)).all()
