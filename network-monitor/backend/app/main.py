import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.db.session import Base, engine, SessionLocal
from app.models.models import AlertRule

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="network-monitor API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(AlertRule).first():
            db.add(AlertRule(name="Device offline", metric_name="ping", condition="3 failed checks or 180 seconds unavailable", threshold=3, duration_seconds=180, severity="critical", enabled=True)); db.commit()

@app.get("/health")
def health(): return {"status":"ok"}
app.include_router(router)
