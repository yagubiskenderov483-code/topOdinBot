# FunPay Saving Bot

Безопасные сделки в Telegram в стиле FunPay.

## Бот

- Бот: **@FunPaySavingRobot**
- Менеджер: **@FunPaySavingManager**
- Поддержка: https://support.funpay.com/tickets
- Сайт: https://funpay.com/
- Отзывы: в боте (Информация → Отзывы) — отзывы с сайта перенаправлены сюда

Токен — из env `BOT_TOKEN` для `@FunPaySavingRobot`.

## Установка

```bash
pip install -r requirements.txt
python bot.py
```

## Render

1. Disk mount `/data`, env `DATA_DIR=/data`, `DB_FILE=/data/db.json`
2. Health Check Path: `/health`
3. `BOT_TOKEN=` токен `@FunPaySavingRobot`
4. Manual Deploy ветки `main`

Ссылки на сделки: `https://t.me/FunPaySavingRobot?start=deal_FPxxxxx`

## Mini App

`REVIEWS_MINIAPP_URL` / `TONCONNECT_MINIAPP_URL` — как раньше, или пусто → `RENDER_EXTERNAL_URL`.

В BotFather добавь домены `onrender.com` и `funpay.com`.
