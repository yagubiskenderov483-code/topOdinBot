# FunPay Bot

Безопасные сделки в Telegram FunPay.

## Бот

- Бот: **@FunPayDeaIsOTCRobot**
- Менеджер: **@FunPayDeaIManager**
- Поддержка: https://support.funpay.com/tickets
- Сайт: https://funpay.com/
- Отзывы: в боте (Информация → Отзывы) — отзывы с сайта перенаправлены сюда

Токен — из env `BOT_TOKEN` для `@FunPayDeaIsOTCRobot`.

## Установка

```bash
pip install -r requirements.txt
python bot.py
```

## Render

1. Disk mount `/data`, env `DATA_DIR=/data`, `DB_FILE=/data/db.json`
2. Health Check Path: `/health`
3. `BOT_TOKEN=` токен `@FunPayDeaIsOTCRobot`
4. Manual Deploy ветки `main`

Ссылки на сделки: `https://t.me/FunPayDeaIsOTCRobot?start=deal_FPxxxxx`

## Mini App

- Отзывы: `REVIEWS_MINIAPP_URL` или `REVIEWS_HTML_REMOTE` (self-contained HTML), иначе `PUBLIC_BASE_URL` / `RENDER_EXTERNAL_URL` + `/index.html`.
- TonConnect: `TONCONNECT_MINIAPP_URL` или тот же base + `/tonconnect.html` (нужен живой сервис бота с `/api/bind-ton`).
- В `/admin` → **Mini App URL** — текущие ссылки.
- В BotFather → Configure Mini App укажите домен Render (например `*.onrender.com`).

Если отзывы 404 — обновите `REVIEWS_MINIAPP_URL` / `REVIEWS_HTML_REMOTE` на свежий HTTPS HTML.
