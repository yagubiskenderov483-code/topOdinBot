# 💎 Gift Deals Bot

Безопасная платформа для сделок в Telegram.

## 🚀 Установка

```bash
pip install -r requirements.txt
python bot.py
```

## ⚙️ Настройка

Токен получить: @BotFather → `/newbot`. Перед запуском добавьте его в
переменную окружения `BOT_TOKEN`:

```bash
export BOT_TOKEN="ВАШ_ТОКЕН"
python bot.py
```

На Render создайте **Web Service** со следующими настройками:

- Build Command: `pip install -r requirements.txt`
- Start Command: `python bot.py`
- Environment Variable: `BOT_TOKEN` — токен от @BotFather

Render автоматически задаёт адрес и порт сервиса, после чего бот запускается
в режиме webhook. Локально, без адреса Render, бот использует polling.

## 📁 Файлы

| Файл | Описание |
|------|----------|
| `bot.py` | Основной код бота |
| `requirements.txt` | Зависимости |
| `db.json` | База данных (создаётся автоматически) |

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
