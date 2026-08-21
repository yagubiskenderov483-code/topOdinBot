#!/usr/bin/env bash
# Render: webhook + Mini App на одном сервисе
set -euo pipefail
cd "$(dirname "$0")"
export USE_WEBHOOK=1
export PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-https://funpay-saving-bot.onrender.com}"
exec python3 bot.py
