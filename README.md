# Finance Data Processing and Access Control

A full-stack assignment implementation focused on backend architecture quality, business logic clarity, robust access control, and a polished dashboard UI.

## Stack Selection

### Backend

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- JWT authentication (access + refresh)
- PostgreSQL (Docker), SQLite (local default)
- Pytest integration tests
- Ruff linting

### Frontend

- Next.js (App Router) + TypeScript
- Tailwind CSS
- TanStack Query
- React Hook Form + Zod
- Recharts

## Why This Design

- Layered architecture: routes -> services -> repositories -> models.
- Clear RBAC boundaries in dependency guards.
- Strict schema contracts with Pydantic + typed frontend client.
- Dashboard endpoints provide aggregate analytics, not only CRUD.
- Soft delete and audit logs improve operational reliability.

## Implemented Requirements

### 1. User and Role Management

- User creation and update endpoints.
- Roles: `viewer`, `analyst`, `admin`.
- Active/inactive user status (`is_active`).
- Role-based restrictions enforced server-side.

### 2. Financial Records Management

- Create, read, update, soft-delete records.
- Fields: amount, type, category, date, notes.
- Filters: type, category, date range, search.
- Pagination support.

### 3. Dashboard Summary APIs

- Total income
- Total expenses
- Net balance
- Category totals
- Monthly trend series
- Recent activity

### 4. Access Control Logic

- Viewer: dashboard summary only.
- Analyst: dashboard + record viewing.
- Admin: full records + user management.

### 5. Validation and Error Handling

- Input validation using Pydantic schemas.
- Structured error payloads with code/message/details.
- Appropriate HTTP status codes and guard checks.

### 6. Data Persistence

- SQLAlchemy models with indexed columns.
- SQLite local default for quick setup.
- PostgreSQL runtime via Docker Compose.

## Optional Enhancements Included

- JWT token auth
- Pagination + search
- Soft delete
- Rate limiting (SlowAPI)
- Integration tests
- OpenAPI docs (`/docs`)
- Audit logs for sensitive actions

## Project Structure

```text
.
├── backend
│   ├── app
│   │   ├── api
│   │   ├── core
│   │   ├── db
│   │   ├── models
│   │   ├── repositories
│   │   ├── schemas
│   │   ├── services
│   │   └── main.py
│   ├── tests
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend
│   ├── src/app
│   ├── src/components
│   └── src/lib
└── docker-compose.yml
```

## API Overview

Base URL: `/api/v1`

### Auth

- `POST /auth/bootstrap-admin`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout` (revokes access + optional refresh token)
- `GET /auth/me`

### Users (Admin)

- `POST /users`
- `GET /users`
- `PATCH /users/{user_id}`

### Records

- `POST /records` (Admin)
- `GET /records` (Analyst/Admin)
- `GET /records/export/csv` (Analyst/Admin)
- `GET /records/{record_id}` (Analyst/Admin)
- `PATCH /records/{record_id}` (Admin)
- `DELETE /records/{record_id}` (Admin, soft delete)

### Dashboard

- `GET /dashboard/summary` (Viewer/Analyst/Admin)

### Reports

- `GET /reports` (Analyst/Admin)
- `POST /reports/run` (Admin)
- `GET /reports/{report_id}/csv` (Analyst/Admin)

## Local Setup (without Docker)

### Quick Start (recommended)

From project root:

```bash
./scripts/setup-local.sh
./scripts/run-local.sh
```

This starts:

- Backend at `http://localhost:8000`
- Frontend at `http://localhost:3000`

Press `Ctrl+C` to stop both services.

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Backend URLs:

- API root: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- `http://localhost:3000`

### 3. First Login

- Go to `/login`.
- Use **Bootstrap admin** once.
- Login with admin credentials.

## Docker Setup

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Postgres: `localhost:5432`

## Quality Checks

### Backend

```bash
cd backend
./.venv/bin/python -m ruff check app tests
./.venv/bin/python -m pytest
```

### Frontend

```bash
cd frontend
npm run lint
npm run build
```

## Assumptions and Tradeoffs

- Initial admin bootstrapping is open only until first user exists.
- SQLite is default for local speed; PostgreSQL is preferred for evaluation demos.
- Refresh token rotation and token blacklist revocation are implemented.
- Rate limiting uses app-level limiter and can be moved to distributed storage for multi-instance deployments.

## Additional Implemented Enhancements

- CSV export for filtered records from dashboard and API.
- Scheduled report generation with persisted snapshots.
- Manual report run + report CSV download in dashboard UI.
- Token blacklist revocation on logout and refresh rotation.

## Scheduler Configuration

Set in backend environment (`.env` or Docker env):

- `REPORT_SCHEDULER_ENABLED=true|false`
- `REPORT_SCHEDULE_MINUTES=60`
- `REPORT_LOOKBACK_DAYS=1`

When enabled, the backend runs a recurring snapshot report job on startup.

## UI Usage for Extras

After admin login in dashboard:

1. Use **Export CSV** in Financial records to download filtered records.
2. Use **Run report now** in Scheduled reports.
3. Download any generated report via its **CSV** action.
4. Use **Log out** to revoke current session token(s) on the server.
