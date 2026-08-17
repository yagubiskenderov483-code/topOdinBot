# FunPay Bot

Безопасные сделки в Telegram FunPay.

## Бот

- Бот: **@FunPayDeaIsOTCRobot**
- Менеджер: **@FunPayDeaIManager**
- Поддержка: https://support.funpay.com/tickets
- Сайт: https://funpay.com/
- Отзывы: в боте (Информация → Отзывы) — отзывы с сайта перенаправлены сюда

Токен бота зашит в `bot.py`. Хостинг бота — **Bothost** (ветка `main`). Сайт/Mini App — Render.

## Установка

```bash
pip install -r requirements.txt
python bot.py
```

## Bothost

1. Репозиторий `topOdinBot`, ветка `main`, точка входа `bot.py`
2. База: `/app/data/db.json` (папка `data` переживает обновление из Git)
3. После пуша в `main` — «Обновить из Git» в панели Bothost (или автодеплой, если включён)

Ссылки на сделки: `https://t.me/FunPayDeaIsOTCRobot?start=deal_FPxxxxx`

## Mini App

- Отзывы: `REVIEWS_MINIAPP_URL` или `REVIEWS_HTML_REMOTE` (self-contained HTML), иначе `PUBLIC_BASE_URL` / `RENDER_EXTERNAL_URL` + `/index.html`.
- TonConnect: `TONCONNECT_MINIAPP_URL` или тот же base + `/tonconnect.html` (нужен живой сервис бота с `/api/bind-ton`).
- В `/admin` → **Mini App URL** — текущие ссылки.
- В BotFather → Configure Mini App укажите домен Render (например `*.onrender.com`).

Если отзывы 404 — обновите `REVIEWS_MINIAPP_URL` / `REVIEWS_HTML_REMOTE` на свежий HTTPS HTML.
