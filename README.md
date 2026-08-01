# 💎 Eldorado GG Bot

Безопасная платформа для сделок в Telegram.

## 🚀 Установка

```bash
pip install -r requirements.txt
python bot.py
```

## ⚙️ Настройка

Бот: **@EldoradoGG_Robot**. Токен — из env `BOT_TOKEN` или актуальный в `bot.py`.  
Старые токены `8879343383:...` не используй: в Render → Environment удали `BOT_TOKEN` или поставь новый.

### Баннеры после деплоя

Баннеры пишутся в `db.json` и дублируются в `banners_seed.json`.  
На Render нужен **Disk** (mount `/data`), иначе после Redeploy база снова пустая:

1. Render → Web Service бота → **Disks** → Add Disk  
2. Mount path: `/data`, Size: 1 GB  
3. Environment:
```
DATA_DIR=/data
DB_FILE=/data/db.json
```
4. Manual Deploy ветки **`main`**

После одного выставления баннеров в `/admin` они переживают рестарты и деплои.

### Бот «падает» через ~10–15 минут

На **Render Free** Web Service засыпает без HTTP-трафика (~15 мин) — polling бота умирает вместе с ним.

В коде уже есть keep-alive на `/health`. Проверь:
1. Health Check Path в Render: **`/health`**
2. После деплоя открой `https://<твой-сервис>.onrender.com/health` — должен быть `{"ok":true...}`
3. Запасной вариант: [UptimeRobot](https://uptimerobot.com) → монитор каждые 5 мин на этот `/health`
4. Надёжнее всего: план **Starter** (не засыпает)

## 📁 Файлы

| Файл | Описание |
|------|----------|
| `bot.py` | Основной код бота |
| `miniapp/` | Mini App с отзывами |
| `requirements.txt` | Зависимости |
| `db.json` | База данных (создаётся автоматически) |

Меню слева внизу — команда `/start` (не Mini App).  
Главное меню → **Информация**: Telegraph «Как проходят сделки» + **Отзывы** (Mini App, `REVIEWS_MINIAPP_URL`).

### Реквизиты

Привязка: карта/телефон, Tonkeeper (приложение или вручную), Звёзды `@username`.

На Render: `/index.html` (отзывы), `/tonconnect.html` (Tonkeeper). В BotFather добавь домен `onrender.com`.

```
REVIEWS_MINIAPP_URL=https://<сервис>.onrender.com/index.html
TONCONNECT_MINIAPP_URL=https://<сервис>.onrender.com/tonconnect.html
```

### Eldorado AI

По умолчанию **Eldorado AI** отвечает через живой LLM (`g4f`) на любые вопросы — ключ не обязателен.

Опционально на Render (стабильнее):
```
GEMINI_API_KEY=...          # Google AI Studio
# или
OPENAI_API_KEY=sk-...       # официальный OpenAI
AI_PROVIDER=auto
```

### Mini App с отзывами

Кнопка **Отзывы** открывает `REVIEWS_MINIAPP_URL` (HTTPS). Старый catbox/litter URL мог протухнуть → 404 в Telegram.

**Быстрый фикс сейчас:** в Render → бот → Environment:
```
REVIEWS_MINIAPP_URL=https://litter.catbox.moe/8n77lf.htm
```
и **Manual Deploy**. В @BotFather разреши домен `catbox.moe` / `litter.catbox.moe`.

**Постоянно (рекомендуется):** бот как **Web Service** на Render (не Background Worker). При наличии `PORT` бот сам раздаёт `miniapp/`. Тогда:
```
REVIEWS_MINIAPP_URL=https://<твой-сервис>.onrender.com/index.html
```
или оставь пустым — возьмётся `RENDER_EXTERNAL_URL/index.html`. В BotFather добавь `onrender.com`.

Обновление отзывов: правь `miniapp/reviews.json` → `python3 miniapp/build.py` → redeploy.

## 🔧 Команды

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню |
| `/admin` | Панель администратора |
| `/neptunteam` | Секретные команды |

## 💡 Функционал

- 🤝 Создание сделок (НФТ, Звёзды, Крипта, Premium)
- 🔒 Защита обеих сторон
- 💰 Пополнение баланса (ВТБ / TON / USDT)
- 🌍 12 языков
- 🏆 Топ продавцов
- 🛡 Админ панель
