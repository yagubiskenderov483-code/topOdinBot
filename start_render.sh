#!/usr/bin/env bash
# Render: только Mini App + /health. Telegram-бот здесь НЕ запускается -
# апдейты (polling) получает Bothost, иначе оба инстанса ловят 409 Conflict.
set -euo pipefail
cd "$(dirname "$0")"
export BOT_MODE=miniapp
export USE_WEBHOOK=0
export PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-https://funpay-saving-bot.onrender.com}"
exec python3 bot.py
