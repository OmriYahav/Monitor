import logging, sys, time
from datetime import datetime, timezone
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))
from sqlalchemy import select
from app.db.session import SessionLocal, Base, engine
from app.models.models import Device, DeviceCheck, Metric
from alert_evaluator import evaluate_device
from ping_poller import ping

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
last_polled: dict[str, float] = {}

def poll_once() -> None:
    with SessionLocal() as db:
        devices = db.scalars(select(Device).where(Device.enabled == True)).all()
        now_monotonic = time.monotonic()
        for device in devices:
            key = str(device.id)
            if now_monotonic - last_polled.get(key, 0) < device.polling_interval_seconds: continue
            last_polled[key] = now_monotonic
            try:
                result = ping(device.ip_address)
                now = datetime.now(timezone.utc)
                db.add(DeviceCheck(device_id=device.id, checked_at=now, success=result.success, latency_ms=result.latency_ms, error_message=result.error_message))
                db.add(Metric(time=now, device_id=device.id, metric_name="ping_success", metric_value=1 if result.success else 0, unit="bool", tags={}))
                if result.latency_ms is not None:
                    db.add(Metric(time=now, device_id=device.id, metric_name="ping_latency_ms", metric_value=result.latency_ms, unit="ms", tags={}))
                device.last_check = now; device.status = "online" if result.success else "offline"
                if result.success: device.last_seen = now
                evaluate_device(db, device); db.commit()
                logging.info("Checked %s (%s): %s", device.name, device.ip_address, device.status)
            except Exception:
                db.rollback(); logging.exception("Failed to poll device %s", device.id)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    logging.info("Worker started")
    while True:
        poll_once(); time.sleep(5)
