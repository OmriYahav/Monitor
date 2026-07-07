# network-monitor

`network-monitor` is a Docker Compose based network monitoring platform built with FastAPI, PostgreSQL, a separate Python polling worker, and a Next.js frontend. This pass implements the foundational production path (phases 1-3 plus metrics foundations): local authentication, RBAC-protected APIs, sites, inventory, ping polling, check history, generic metrics rows, dashboard summaries, basic offline alerting, alert acknowledgement/resolution, SNMP profile storage without secret exposure, and a practical browser UI.

## Features included

- Local JWT authentication with bcrypt password hashing.
- Initial admin seeding from environment variables.
- Roles: `admin`, `operator`, and `viewer`.
- Protected backend endpoints and protected frontend data loading.
- Site/location model.
- Full device inventory fields for network infrastructure assets.
- PostgreSQL persistence with SQLAlchemy models.
- Separate worker that pings enabled devices, stores every result, records ping metrics, updates device status, and keeps polling after per-device failures.
- Basic alert engine for device-down detection with duplicate suppression and auto-resolution.
- Alert acknowledgement and manual resolution endpoints.
- SNMP profile API that omits secrets from responses.
- Dashboard with device status counts, offline devices, and recent alerts.
- Docker Compose for PostgreSQL, backend, worker, and frontend.

## Architecture

- `backend/`: FastAPI API, SQLAlchemy models, auth, services, schemas, and startup seed logic.
- `worker/`: long-running polling process using the backend models and database session.
- `frontend/`: Next.js UI for login, dashboard, and inventory table.
- `docker-compose.yml`: runnable local stack.

## Run with Docker Compose

```bash
cd network-monitor
cp .env.example .env
# Edit SECRET_KEY and INITIAL_ADMIN_PASSWORD before real use.
docker compose up --build
```

Open:

- Frontend: <http://localhost:3000>
- API docs: <http://localhost:8000/docs>
- API health: <http://localhost:8000/health>

## First admin

The backend creates the first admin user on startup from:

- `INITIAL_ADMIN_EMAIL`
- `INITIAL_ADMIN_PASSWORD`
- `INITIAL_ADMIN_NAME`

The defaults are for local development only. Change them in `.env` before deploying.

## Add a device

1. Log in to the frontend.
2. Use the API docs or REST API to create devices. The current UI displays devices; richer add/edit forms are the next UI increment.

Example:

```bash
TOKEN=$(curl -s http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"ChangeMe123!"}' | jq -r .access_token)

curl -X POST http://localhost:8000/devices \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Gateway","ip_address":"192.168.1.1","type":"firewall","criticality":"critical","polling_interval_seconds":60}'
```

The worker stores rows in `device_checks`, writes `ping_success` and `ping_latency_ms` metrics, and updates `devices.status`, `last_check`, and `last_seen`.

## Configure SNMP

SNMP profile storage is available through `/snmp-profiles`. Secret fields can be submitted, but API responses intentionally exclude communities and passwords. SNMP polling templates are not implemented in this pass.

## Alert rules and alerts

Default rules are seeded for device offline, high latency, and high CPU. The working evaluator currently enforces device-down ping behavior: it opens one alert after three failed checks or prolonged unavailability and resolves that alert when the device recovers.

Operators and admins can acknowledge or resolve alerts through:

- `POST /alerts/{alert_id}/acknowledge`
- `POST /alerts/{alert_id}/resolve`

## Notifications

Notification channel database foundations are present, but delivery integrations (SMTP, Teams, Telegram, generic webhook) are not wired in this pass.

## Discovery

Discovery is not implemented in this pass. The planned flow is subnet scan, ping sweep, optional SNMP probe, review results, and approved import.

## Troubleshooting

- Backend cannot connect to PostgreSQL: run `docker compose ps` and check the `postgres` health state.
- Login fails: confirm the `INITIAL_ADMIN_*` values and recreate the development database with `docker compose down -v` if you changed seed credentials after the first startup.
- Ping checks fail: confirm the worker container can reach the target IP and ICMP is allowed.
- Frontend cannot reach backend: ensure `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000` for local browser access.

## Known limitations

- Automatic migrations are not configured yet; this development build uses `Base.metadata.create_all`.
- SNMP polling, interface discovery, syslog, topology, reports, maintenance windows, and notification delivery remain roadmap work.
- The frontend is intentionally minimal and exposes the foundational login/dashboard/device list workflow.

## Roadmap

1. Alembic migrations and pagination/filtering.
2. Add/edit device, site, alert-rule, and SNMP profile UI pages.
3. SNMP polling with interface inventory and vendor templates.
4. Notification delivery and suppression during maintenance.
5. Discovery scans and import workflow.
6. Syslog receiver and syslog-based alerts.
7. Topology, reports, retention policies, and TimescaleDB hypertables.
