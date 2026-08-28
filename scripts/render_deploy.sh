#!/usr/bin/env bash
# Создаёт/обновляет web-сервис funpay-saving-bot на Render через API.
# Нужен RENDER_API_KEY: https://dashboard.render.com/u/settings#api-keys
set -euo pipefail

API_KEY="${RENDER_API_KEY:-}"
REPO="${RENDER_REPO:-https://github.com/yagubiskenderov483-code/topOdinBot}"
BRANCH="${RENDER_BRANCH:-main}"
SERVICE_NAME="${RENDER_SERVICE_NAME:-funpay-saving-bot}"
REGION="${RENDER_REGION:-frankfurt}"
PLAN="${RENDER_PLAN:-free}"

if [[ -z "$API_KEY" ]]; then
  echo "ERROR: set RENDER_API_KEY (Render Dashboard → Account Settings → API Keys)"
  exit 1
fi

auth=(-H "Authorization: Bearer $API_KEY" -H "Accept: application/json" -H "Content-Type: application/json")

echo "== owners =="
owners=$(curl -sf "${auth[@]}" "https://api.render.com/v1/owners?limit=20")
echo "$owners" | python3 -c "
import json,sys
data=json.load(sys.stdin)
items=data if isinstance(data,list) else data.get('items',data.get('owners',[]))
for o in items:
    oid=o.get('owner',o).get('id') or o.get('id')
    name=o.get('owner',o).get('name') or o.get('name') or oid
    print(oid, name)
" || { echo "Failed to list owners. Check RENDER_API_KEY."; exit 1; }

OWNER_ID="${RENDER_OWNER_ID:-$(echo "$owners" | python3 -c "
import json,sys
data=json.load(sys.stdin)
items=data if isinstance(data,list) else data.get('items',[])
if not items: raise SystemExit(1)
print(items[0].get('owner',items[0]).get('id') or items[0].get('id'))
")}"

echo "Using owner: $OWNER_ID"

echo "== existing service =="
existing=$(curl -sf "${auth[@]}" "https://api.render.com/v1/services?limit=100" || echo "[]")
sid=$(echo "$existing" | python3 -c "
import json,sys
name=sys.argv[1]
data=json.load(sys.stdin)
items=data if isinstance(data,list) else data.get('items',[])
for it in items:
    s=it.get('service',it)
    if s.get('name')==name:
        print(s.get('id',''))
        break
" "$SERVICE_NAME" 2>/dev/null || true)

payload=$(python3 - <<PY
import json
print(json.dumps({
  "type": "web_service",
  "name": "$SERVICE_NAME",
  "ownerId": "$OWNER_ID",
  "repo": "$REPO",
  "branch": "$BRANCH",
  "autoDeploy": "yes",
  "serviceDetails": {
    "env": "python",
    "region": "$REGION",
    "plan": "$PLAN",
    "buildCommand": "pip install -r requirements.txt && python3 miniapp/build.py",
    "startCommand": "bash start_render.sh",
    "healthCheckPath": "/health",
    "envVars": [
      {"key": "PUBLIC_BASE_URL", "value": "https://$SERVICE_NAME.onrender.com"},
      {"key": "BOT_MODE", "value": "miniapp"},
      {"key": "USE_WEBHOOK", "value": "0"},
      {"key": "RENDER_KEEPALIVE", "value": "1"},
      {"key": "KEEPALIVE_INTERVAL_SEC", "value": "480"},
      {"key": "PYTHON_VERSION", "value": "3.11.0"},
    ],
  },
}))
PY
)

if [[ -n "$sid" ]]; then
  echo "Service exists: $sid - triggering deploy"
  curl -sf "${auth[@]}" -X POST "https://api.render.com/v1/services/$sid/deploys" \
    -d '{"clearCache":"do_not_clear"}' | python3 -m json.tool
else
  echo "Creating service..."
  curl -sf "${auth[@]}" -X POST "https://api.render.com/v1/services" -d "$payload" | python3 -m json.tool
fi

echo "Done. URL: https://$SERVICE_NAME.onrender.com"
