#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but not found." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but not found." >&2
  exit 1
fi

echo "[setup] Preparing backend..."
cd "$BACKEND_DIR"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements-dev.txt

if [[ ! -f .env && -f .env.example ]]; then
  cp .env.example .env
  echo "[setup] Created backend/.env from .env.example"
fi

echo "[setup] Preparing frontend..."
cd "$FRONTEND_DIR"
npm install

if [[ ! -f .env.local ]]; then
  cat > .env.local <<'ENVVARS'
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
ENVVARS
  echo "[setup] Created frontend/.env.local"
fi

echo "[setup] Local setup complete."
