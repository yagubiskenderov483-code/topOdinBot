# FunPay Bot

Безопасные сделки в Telegram FunPay.

## Бот

- Бот: **@FunPayDealsOTCRobot**
- Менеджер: **@FunPayDeaIManager**
- Поддержка: https://support.funpay.com/tickets
- Сайт: https://funpay.com/
- Отзывы: в боте (Информация → Отзывы) — Mini App

Токен бота зашит в `bot.py`. Хостинг — **Render** (один web-сервис, ветка `main`).

## Локальный запуск

```bash
pip install -r requirements.txt
python bot.py
```

Без `PORT` бот работает в режиме polling, HTTP-сервер не поднимается.

## Деплой на Render

1. Blueprint из `render.yaml` — создаётся один web-сервис `funpay-saving-bot`.
2. Build: `pip install -r requirements.txt && python3 miniapp/build.py` (встраивает `miniapp/reviews.json` в `index.html`).
3. Start: `python bot.py` — процесс сам поднимает HTTP на `$PORT`:
   - `/health` — health check;
   - `/index.html` — Mini App «Отзывы»;
   - `/tonconnect.html` + `/tonconnect-manifest.json` — Mini App привязки Tonkeeper;
   - `POST /api/bind-ton` — сохранение TON-кошелька из Mini App;
   - `POST /telegram` — Telegram webhook (режим включён через `USE_WEBHOOK=1`).
4. `RENDER_EXTERNAL_URL` Render задаёт сам — от него строятся ссылки Mini App и webhook.
5. На free-плане диск недоступен: `db.json` живёт в каталоге проекта и сбрасывается при redeploy.
   Для персистентности возьмите платный план, добавьте disk на `/data` и env `DATA_DIR=/data`, `DB_FILE=/data/db.json`.

Ссылки на сделки: `https://t.me/FunPayDealsOTCRobot?start=deal_FPxxxxx`

## Mini App

- Оба Mini App отдаёт сам бот со своего Render-домена (отдельный статический сайт не нужен).
- Переопределить ссылку отзывов можно через `REVIEWS_MINIAPP_URL`, TonConnect — через `TONCONNECT_MINIAPP_URL`.
- В `/admin` → **Mini App URL** — текущие ссылки.
- В BotFather → Configure Mini App укажите домен Render (например `*.onrender.com`).
