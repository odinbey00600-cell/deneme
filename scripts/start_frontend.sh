#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../frontend"
cp -n .env.local.example .env.local || true
npm install
npm run dev
