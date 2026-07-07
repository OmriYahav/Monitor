from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.models import Alert, Device
from app.schemas.schemas import AlertRead, DashboardSummary, DeviceCheckRead, DeviceCreate, DeviceRead, DeviceUpdate
from app.services import alert_service, device_service

router = APIRouter()

@router.get("/devices", response_model=list[DeviceRead])
def devices(db: Session = Depends(get_db)): return device_service.list_devices(db)
@router.post("/devices", response_model=DeviceRead, status_code=201)
def create_device(data: DeviceCreate, db: Session = Depends(get_db)): return device_service.create_device(db, data)
@router.get("/devices/{device_id}", response_model=DeviceRead)
def get_device(device_id: UUID, db: Session = Depends(get_db)): return device_service.get_device(db, device_id)
@router.put("/devices/{device_id}", response_model=DeviceRead)
def update_device(device_id: UUID, data: DeviceUpdate, db: Session = Depends(get_db)): return device_service.update_device(db, device_id, data)
@router.delete("/devices/{device_id}", status_code=204)
def delete_device(device_id: UUID, db: Session = Depends(get_db)): device_service.delete_device(db, device_id)
@router.get("/devices/{device_id}/checks", response_model=list[DeviceCheckRead])
def checks(device_id: UUID, db: Session = Depends(get_db)): return device_service.list_checks(db, device_id)

@router.get("/alerts", response_model=list[AlertRead])
def alerts(db: Session = Depends(get_db)): return alert_service.list_alerts(db)
@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertRead)
def ack(alert_id: UUID, db: Session = Depends(get_db)): return alert_service.acknowledge(db, alert_id)
@router.post("/alerts/{alert_id}/resolve", response_model=AlertRead)
def res(alert_id: UUID, db: Session = Depends(get_db)): return alert_service.resolve(db, alert_id)

@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard(db: Session = Depends(get_db)):
    counts = dict(db.execute(select(Device.status, func.count()).group_by(Device.status)).all())
    recent = db.scalars(select(Alert).options(joinedload(Alert.device)).order_by(Alert.started_at.desc()).limit(10)).unique().all()
    offline = db.scalars(select(Device).where(Device.status == "offline").order_by(Device.name).limit(20)).all()
    return DashboardSummary(total_devices=sum(counts.values()), online_devices=counts.get("online",0), offline_devices=counts.get("offline",0), unknown_devices=counts.get("unknown",0), open_alerts_count=db.scalar(select(func.count()).select_from(Alert).where(Alert.status.in_(["open","acknowledged"]))) or 0, recent_alerts=recent, offline_devices_list=offline)
