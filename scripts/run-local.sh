#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_PY="$BACKEND_DIR/.venv/bin/python"

if [[ ! -x "$BACKEND_PY" ]]; then
  echo "Backend venv not found. Run: ./scripts/setup-local.sh" >&2
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "Frontend dependencies not found. Run: ./scripts/setup-local.sh" >&2
  exit 1
fi

if [[ ! -f "$BACKEND_DIR/.env" && -f "$BACKEND_DIR/.env.example" ]]; then
  cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
  echo "Created backend/.env from .env.example"
fi

if [[ ! -f "$FRONTEND_DIR/.env.local" ]]; then
  cat > "$FRONTEND_DIR/.env.local" <<'ENVVARS'
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
ENVVARS
  echo "Created frontend/.env.local"
fi

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi

  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

echo "Starting backend on http://localhost:8000"
(
  cd "$BACKEND_DIR"
  exec "$BACKEND_PY" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:3000"
(
  cd "$FRONTEND_DIR"
  exec npm run dev
) &
FRONTEND_PID=$!

echo "Both services started. Press Ctrl+C to stop."
wait "$BACKEND_PID" "$FRONTEND_PID"
