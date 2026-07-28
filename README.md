# 💎 Eldorado GG Bot

Безопасная платформа для сделок в Telegram.

## 🚀 Установка

```bash
pip install -r requirements.txt
python bot.py
```

## ⚙️ Настройка

Вставь свой токен в `bot.py`:
```python
BOT_TOKEN = "ВАШ_ТОКЕН"
```

Токен получить: @BotFather → /newbot

## 📁 Файлы

| Файл | Описание |
|------|----------|
| `bot.py` | Основной код бота |
| `miniapp/` | Mini App с отзывами |
| `requirements.txt` | Зависимости |
| `db.json` | База данных (создаётся автоматически) |

Меню слева внизу — команда `/start` (не Mini App).  
Главное меню → **Информация**: Telegraph «Как проходят сделки» + **Отзывы** (Mini App, `REVIEWS_MINIAPP_URL`).

### Mini App с отзывами

Кнопка **Отзывы** открывает `REVIEWS_MINIAPP_URL` (HTTPS). Старый catbox/litter URL мог протухнуть → 404 в Telegram.

**Быстрый фикс сейчас:** в Render → бот → Environment:
```
REVIEWS_MINIAPP_URL=https://litter.catbox.moe/k4q8zc.htm
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
