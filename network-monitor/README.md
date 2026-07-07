# network-monitor

A small Docker-based MVP for monitoring network equipment. It lets you add devices by IP address, runs periodic ping checks in a separate worker, stores check history in PostgreSQL, shows current status in a web dashboard, and opens alerts when a device is unavailable.

## MVP scope

Included:
- FastAPI REST API for devices, alerts, and dashboard summary.
- PostgreSQL persistence using SQLAlchemy models and automatic table creation for MVP simplicity.
- Separate Python worker process that pings enabled devices on their polling interval.
- Next.js frontend with dashboard, devices, device details, and alerts pages.
- Critical offline alert rule: 3 consecutive failed checks or more than 3 minutes unavailable.

Intentionally not included yet: SNMP, Syslog, auto discovery, AI, WhatsApp, maps, multi-tenant support, complex permissions, mobile app, and full notification delivery.

## Run with Docker Compose

```bash
cd network-monitor
cp .env.example .env
docker compose up --build
```

Open:
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

## Add a device

Use the Devices page and fill in name, IP address, type, site, and polling interval. You can also use the API:

```bash
curl -X POST http://localhost:8000/devices \
  -H 'Content-Type: application/json' \
  -d '{"name":"Gateway","ip_address":"192.168.1.1","type":"firewall","site":"HQ","polling_interval_seconds":60}'
```

The worker will pick up enabled devices, ping them, save rows in `device_checks`, and update `devices.status`, `last_check`, and `last_seen`.

## Troubleshooting

- If the backend cannot connect, confirm PostgreSQL is healthy: `docker compose ps`.
- If ping checks fail inside Docker, confirm the container can reach the target IP and ICMP is allowed by the host/network.
- If the frontend cannot load data in the browser, verify `BACKEND_URL` and that the backend is reachable at http://localhost:8000.
- Recreate tables for a clean MVP database with `docker compose down -v` and then `docker compose up --build`.

## Next planned features

- Alembic migrations.
- Authentication.
- Notification channel implementations.
- Better filtering and pagination.
- Retention policy for old check history.
