from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.auth.dependencies import current_user, require_roles
from app.auth.security import create_access_token, hash_password
from app.core import get_settings
from app.db.session import get_db
from app.models.models import Alert, AlertRule, Device, SNMPProfile, Site, User
from app.schemas.schemas import *
from app.services import alert_service, device_service, site_service, user_service

router = APIRouter()

@router.post("/auth/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = user_service.authenticate(db, data.email, data.password)
    if not user: raise HTTPException(401, "Invalid email or password")
    return Token(access_token=create_access_token(str(user.id)))
@router.get("/auth/me", response_model=UserRead)
def me(user: User = Depends(current_user)): return user

@router.get("/users", response_model=list[UserRead], dependencies=[Depends(require_roles("admin"))])
def users(db: Session = Depends(get_db)): return user_service.list_users(db)
@router.post("/users", response_model=UserRead, status_code=201, dependencies=[Depends(require_roles("admin"))])
def create_user(data: UserCreate, db: Session = Depends(get_db)): return user_service.create_user(db, data)
@router.put("/users/{user_id}", response_model=UserRead, dependencies=[Depends(require_roles("admin"))])
def update_user(user_id: UUID, data: UserUpdate, db: Session = Depends(get_db)): return user_service.update_user(db, user_id, data)

@router.get("/sites", response_model=list[SiteRead], dependencies=[Depends(current_user)])
def sites(db: Session = Depends(get_db)): return site_service.list_sites(db)
@router.post("/sites", response_model=SiteRead, status_code=201, dependencies=[Depends(require_roles("admin","operator"))])
def create_site(data: SiteCreate, db: Session = Depends(get_db)): return site_service.create_site(db, data)
@router.put("/sites/{site_id}", response_model=SiteRead, dependencies=[Depends(require_roles("admin","operator"))])
def update_site(site_id: UUID, data: SiteUpdate, db: Session = Depends(get_db)): return site_service.update_site(db, site_id, data)
@router.delete("/sites/{site_id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_site(site_id: UUID, db: Session = Depends(get_db)): site_service.delete_site(db, site_id)

@router.get("/devices", response_model=list[DeviceRead], dependencies=[Depends(current_user)])
def devices(db: Session = Depends(get_db)): return device_service.list_devices(db)
@router.post("/devices", response_model=DeviceRead, status_code=201, dependencies=[Depends(require_roles("admin","operator"))])
def create_device(data: DeviceCreate, db: Session = Depends(get_db)): return device_service.create_device(db, data)
@router.get("/devices/{device_id}", response_model=DeviceRead, dependencies=[Depends(current_user)])
def get_device(device_id: UUID, db: Session = Depends(get_db)): return device_service.get_device(db, device_id)
@router.put("/devices/{device_id}", response_model=DeviceRead, dependencies=[Depends(require_roles("admin","operator"))])
def update_device(device_id: UUID, data: DeviceUpdate, db: Session = Depends(get_db)): return device_service.update_device(db, device_id, data)
@router.delete("/devices/{device_id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_device(device_id: UUID, db: Session = Depends(get_db)): device_service.delete_device(db, device_id)
@router.get("/devices/{device_id}/checks", response_model=list[DeviceCheckRead], dependencies=[Depends(current_user)])
def checks(device_id: UUID, db: Session = Depends(get_db)): return device_service.list_checks(db, device_id)

@router.get("/alerts", response_model=list[AlertRead], dependencies=[Depends(current_user)])
def alerts(db: Session = Depends(get_db)): return alert_service.list_alerts(db)
@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertRead, dependencies=[Depends(require_roles("admin","operator"))])
def ack(alert_id: UUID, db: Session = Depends(get_db)): return alert_service.acknowledge(db, alert_id)
@router.post("/alerts/{alert_id}/resolve", response_model=AlertRead, dependencies=[Depends(require_roles("admin","operator"))])
def res(alert_id: UUID, db: Session = Depends(get_db)): return alert_service.resolve(db, alert_id)

@router.get("/alert-rules", response_model=list[AlertRuleRead], dependencies=[Depends(current_user)])
def alert_rules(db: Session = Depends(get_db)): return db.scalars(select(AlertRule).order_by(AlertRule.name)).all()
@router.post("/alert-rules", response_model=AlertRuleRead, status_code=201, dependencies=[Depends(require_roles("admin"))])
def create_alert_rule(data: AlertRuleCreate, db: Session = Depends(get_db)):
    rule = AlertRule(**data.model_dump()); db.add(rule); db.commit(); db.refresh(rule); return rule

@router.get("/snmp-profiles", response_model=list[SNMPProfileRead], dependencies=[Depends(current_user)])
def snmp_profiles(db: Session = Depends(get_db)): return db.scalars(select(SNMPProfile).order_by(SNMPProfile.name)).all()
@router.post("/snmp-profiles", response_model=SNMPProfileRead, status_code=201, dependencies=[Depends(require_roles("admin"))])
def create_snmp_profile(data: SNMPProfileCreate, db: Session = Depends(get_db)):
    profile = SNMPProfile(**data.model_dump()); db.add(profile); db.commit(); db.refresh(profile); return profile

@router.get("/dashboard/summary", response_model=DashboardSummary, dependencies=[Depends(current_user)])
def dashboard(db: Session = Depends(get_db)):
    counts = dict(db.execute(select(Device.status, func.count()).group_by(Device.status)).all())
    recent = db.scalars(select(Alert).options(joinedload(Alert.device).joinedload(Device.site)).order_by(Alert.started_at.desc()).limit(10)).unique().all()
    offline = db.scalars(select(Device).options(joinedload(Device.site)).where(Device.status == "offline").order_by(Device.name).limit(20)).unique().all()
    return DashboardSummary(total_devices=sum(counts.values()), online_devices=counts.get("online",0), offline_devices=counts.get("offline",0), warning_devices=counts.get("warning",0), unknown_devices=counts.get("unknown",0), open_alerts_count=db.scalar(select(func.count()).select_from(Alert).where(Alert.status.in_(["open","acknowledged"]))) or 0, recent_alerts=recent, offline_devices_list=offline)
