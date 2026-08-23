#!/usr/bin/env bash
# Bothost: polling-режим (без webhook на Render)
set -euo pipefail
cd "$(dirname "$0")"
export USE_WEBHOOK=0
export RENDER_KEEPALIVE=0
unset PUBLIC_BASE_URL WEBHOOK_URL RENDER_EXTERNAL_URL MINIAPP_BASE_URL 2>/dev/null || true
# BOTHOST_PUBLIC_URL оставляем — нужен для Mini App на Bothost, polling задаётся USE_WEBHOOK=0
export DATA_DIR="${DATA_DIR:-/app/data}"
# DB_FILE задаёт bot.py из фактически доступного DATA_DIR (не хардкодим /app/data/db.json)
exec python3 bot.py
