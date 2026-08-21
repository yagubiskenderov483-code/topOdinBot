#!/usr/bin/env bash
# Локальная проверка перед/после деплоя на Render
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== compile =="
python3 -m py_compile bot.py miniapp/build.py

echo "== miniapp build =="
python3 miniapp/build.py

echo "== render mode check =="
RENDER=true PORT=10000 RENDER_EXTERNAL_URL=https://funpay-saving-bot.onrender.com USE_WEBHOOK=1 python3 - <<'PY'
import os, importlib, bot
importlib.reload(bot)
assert bot._resolve_bot_mode() == "webhook"
assert bot.reviews_miniapp_url().endswith("/index.html")
print("webhook mode OK, reviews:", bot.reviews_miniapp_url())
PY

echo "== HTTP smoke =="
PORT=8765 RENDER=true RENDER_EXTERNAL_URL=http://127.0.0.1:8765 USE_WEBHOOK=0 RENDER_KEEPALIVE=0 DATA_DIR=/tmp/funpay-render-test python3 bot.py &
PID=$!
sleep 5
curl -sf "http://127.0.0.1:8765/health" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('ok'); print('health OK', d.get('bot'))"
curl -sf -o /dev/null -w "index.html HTTP %{http_code}\n" "http://127.0.0.1:8765/index.html"
kill $PID 2>/dev/null || true
wait $PID 2>/dev/null || true

echo "ALL OK"
