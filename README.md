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

### Mini App с отзывами (Render Static Site)

1. В Render: **New → Static Site**, репозиторий `topOdinBot`, ветка `main`.
2. **Root Directory:** `.` (корень репозитория).
3. **Build Command:** `python3 miniapp/build.py`
4. **Publish Directory:** `miniapp`
5. После деплоя скопируй URL (например `https://eldorado-reviews-miniapp.onrender.com`).
6. В Render → сервис бота → **Environment** → `REVIEWS_MINIAPP_URL` = этот URL.
7. В @BotFather → **Bot Settings → Configure Mini App / Domain** → добавь домен `onrender.com` (или свой поддомен).
8. Перезапусти бота (Manual Deploy).

Обновление отзывов: правь `miniapp/reviews.json`, затем `python3 miniapp/build.py` и redeploy Static Site.

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
