#!/usr/bin/env bash
# Bothost: polling-режим (без webhook на Render)
set -euo pipefail
cd "$(dirname "$0")"
export USE_WEBHOOK=0
unset PUBLIC_BASE_URL WEBHOOK_URL BOTHOST_PUBLIC_URL 2>/dev/null || true
export DATA_DIR="${DATA_DIR:-/app/data}"
# DB_FILE задаёт bot.py из фактически доступного DATA_DIR (не хардкодим /app/data/db.json)
exec python3 bot.py
