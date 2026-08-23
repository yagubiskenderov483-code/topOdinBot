# FunPay Bot — @FunPaySwapOTCRobot

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yagubiskenderov483-code/topOdinBot)

## Деплой на Render (один клик)

1. **Остановите бота на Bothost** (если там запущен) — один токен = один сервер.
2. Нажмите кнопку **Deploy to Render** выше (или откройте ссылку):
   https://render.com/deploy?repo=https://github.com/yagubiskenderov483-code/topOdinBot
3. Войдите в Render через GitHub → **Apply** (Blueprint подхватит `render.yaml` автоматически).
4. Дождитесь статуса **Live** (~5–10 мин).
5. Проверьте:
   - https://funpay-saving-bot.onrender.com/health
   - https://funpay-saving-bot.onrender.com/index.html
   - Telegram: `/start` у @FunPaySwapOTCRobot
6. **BotFather** → @FunPaySwapOTCRobot → Configure Mini App → домен:
   `funpay-saving-bot.onrender.com`

После этого: **Информация → Отзывы** в боте.

---

## Бот

- Бот: **@FunPaySwapOTCRobot**
- Менеджер: **@FunPayDeaIManager**
- Mini App (отзывы + Tonkeeper): тот же Render-сервис

Токен зашит в `bot.py`. На Render — **webhook**, на Bothost — **polling** (авто).

**Не запускайте Bothost и Render одновременно** — `/start` перестанет работать.

---

## Локальная проверка

```bash
bash scripts/render_smoke_test.sh
```

## Bothost (альтернатива)

1. Репозиторий `topOdinBot`, ветка `main`, файл `bot.py`
2. **Не ставьте** `USE_WEBHOOK=1` и `PUBLIC_BASE_URL` на Bothost
3. «Обновить из Git» в панели Bothost

---

## Что поднимает Render-сервис

| URL | Назначение |
|-----|------------|
| `/health` | health check |
| `/telegram` | Telegram webhook |
| `/index.html` | Mini App «Отзывы» |
| `/tonconnect.html` | привязка Tonkeeper |
| `/api/bind-ton` | сохранение TON-кошелька |

На free-плане `db.json` сбрасывается при redeploy (нет диска).

Ссылки на сделки: `https://t.me/FunPaySwapOTCRobot?start=deal_FPxxxxx`
