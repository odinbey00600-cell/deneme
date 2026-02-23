#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp -n backend/.env.example backend/.env || true
uvicorn backend.api_server.main:app --host 0.0.0.0 --port 8000 --reload
