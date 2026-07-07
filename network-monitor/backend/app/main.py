import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.api.routes import router
from app.auth.security import hash_password
from app.core import get_settings
from app.db.session import Base, engine, SessionLocal
from app.models.models import AlertRule, User

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="network-monitor API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.email == settings.initial_admin_email.lower())):
            db.add(User(name=settings.initial_admin_name, email=settings.initial_admin_email.lower(), password_hash=hash_password(settings.initial_admin_password), role="admin", enabled=True))
        if not db.query(AlertRule).first():
            db.add_all([
                AlertRule(name="Device offline", description="Device is down after failed ping checks", metric_name="ping_success", condition="equals", threshold=0, duration_seconds=180, severity="critical", enabled=True),
                AlertRule(name="High latency", description="Ping latency is above 250ms", metric_name="ping_latency_ms", condition="greater_than", threshold=250, duration_seconds=300, severity="warning", enabled=True),
                AlertRule(name="CPU above 85%", metric_name="cpu_percent", condition="greater_than", threshold=85, duration_seconds=300, severity="high", enabled=True),
            ])
        db.commit()

@app.get("/health")
def health(): return {"status":"ok"}
app.include_router(router)
