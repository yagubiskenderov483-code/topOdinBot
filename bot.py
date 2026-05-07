import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
DB_FILE = os.getenv("DB_FILE", "db.json")

# SECURITY: do not hardcode token in repo
BOT_TOKEN = "8767675859:AAGLXINsiVGd1wYg5EEhH98Vhv1AWgHRYRU"
if not BOT_TOKEN:
    logger.warning("BOT_TOKEN is empty. Set BOT_TOKEN env var before start.")
    exit(1)

BOT_USERNAME = "GiftDeals_Robot"

MANAGER_URL = "https://t.me/GiftDealsManager"
MANAGER_TAG = "@GiftDealsManager"

ADMIN_ID = 8726084830
ADMIN_IDS = {8726084830, 90283607}

# Payment details
CRYPTO_ADDR = "UQDGN5pfjPxorFyjN2xha84bapuADDtPcRofNDJ4dK2YXxZd"
CRYPTO_BOT = "https://t.me/send?start=IVbfPL7Tk4XA"
CARD_NUM = "+79041751408"
CARD_NAME = "Александр Ф."
CARD_BANK_RU = "ВТБ"
CARD_BANK_EN = "VTB"


# ──────────────────────────────────────────────────────────────────────────────
# Emoji policy
# Buttons: only Unicode emoji (no tg-emoji)
# Logs/text: can use tg-emoji emoji-id
# ──────────────────────────────────────────────────────────────────────────────
def tg_emoji(eid: str, fallback: str) -> str:
    return f"<tg-emoji emoji-id='{eid}'>{fallback}</tg-emoji>"


LOG_EMOJI_TIME = tg_emoji("5258262708838472996", "🕐")
LOG_EMOJI_GIFT = tg_emoji("5258362837411045098", "🎁")
LOG_EMOJI_MONEY = tg_emoji("5807499888245612254", "💰")

BTN_DEAL = "🤝"
BTN_PROFILE = "👤"
BTN_BALANCE = "💳"
BTN_DEALS = "📋"
BTN_LANG = "🌍"
BTN_TOP = "🏆"
BTN_REF = "🤝"
BTN_REQ = "📋"
BTN_BACK = "◀️"
BTN_HOME = "🏠"

BTN_NFT = "🖼️"
BTN_USERNAME = "👤"
BTN_STARS = "⭐️"
BTN_CRYPTO = "💎"
BTN_PREMIUM = "✨"  # requested: premium emoji in buttons should be normal unicode

BTN_LOG_PROMO = "✨"  # inline promo button in logs (no tg-emoji)


RU_BANKS = [
    "Сбербанк",
    "ВТБ",
    "Тинькофф",
    "Альфа",
    "Газпром",
    "Россельхоз",
    "Открытие",
    "Совком",
    "Райффайзен",
    "МКБ",
    "Росбанк",
    "Промсвязь",
    "Уралсиб",
    "Банк России",
]
EN_BANKS = [
    "HSBC",
    "Barclays",
    "Lloyds",
    "NatWest",
    "Halifax",
    "Santander",
    "Nationwide",
    "Monzo",
    "Revolut",
    "Chase",
    "Bank of America",
    "Wells Fargo",
    "Citibank",
    "TD Bank",
]


# ──────────────────────────────────────────────────────────────────────────────
# DB
# ──────────────────────────────────────────────────────────────────────────────
def _db_default() -> Dict[str, Any]:
    return {
        "users": {},
        "deals": {},
        "deal_counter": 1,
        "logs": [],
        "log_chat_id": None,
        "log_hidden": False,
        "log_templates": {},
        "extra_group_id": None,
    }


def load_db() -> Dict[str, Any]:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            logger.exception("Failed to load db.json, using default.")
            return _db_default()
    return _db_default()


def save_db(db: Dict[str, Any]) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def get_user(db: Dict[str, Any], uid: int) -> Dict[str, Any]:
    k = str(uid)
    if k not in db["users"]:
        db["users"][k] = {
            "username": "",
            "lang": "ru",
            "requisites": {},
            "balance": 0,
            "total_deals": 0,
            "success_deals": 0,
            "turnover": 0,
            "reputation": 0,
            "reviews": [],
            "status": "",
            "ref_by": None,
            "ref_count": 0,
            "ref_earned": 0,
        }
    u = db["users"][k]
    u.setdefault("requisites", {})
    return u


def get_lang(uid: int) -> str:
    try:
        return get_user(load_db(), uid).get("lang", "ru")
    except Exception:
        return "ru"


def gen_deal_id(db: Dict[str, Any]) -> str:
    n = int(db.get("deal_counter", 1))
    db["deal_counter"] = n + 1
    save_db(db)
    return f"GD{n:05d}"


def add_log(
    db: Dict[str, Any],
    event: str,
    *,
    deal_id: Optional[str] = None,
    uid: Optional[int] = None,
    username: Optional[str] = None,
    extra: str = "",
) -> Dict[str, Any]:
    entry = {
        "time": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "event": event,
        "deal_id": deal_id or "",
        "uid": str(uid) if uid is not None else "",
        "username": username or "",
        "extra": extra or "",
    }
    db.setdefault("logs", []).append(entry)
    if len(db["logs"]) > 500:
        db["logs"] = db["logs"][-500:]
    return entry


def mask_str(t: str) -> str:
    if not t:
        return "-"
    if t.startswith("@"):
        s = t[1:]
        return "@***" if len(s) <= 3 else f"@{s[:2]}***{s[-2:]}"
    if t.isdigit():
        return t[:3] + "***" + t[-2:]
    return t[:2] + "***"


# ──────────────────────────────────────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────────────────────────────────────
def validate_username(text: str) -> Tuple[Optional[str], Optional[str]]:
    import re

    t = text.strip()
    if not t.startswith("@"):
        t = "@" + t
    u = t[1:]
    if len(u) < 4:
        return None, "short"
    if not re.fullmatch(r"[a-zA-Z0-9_]+", u):
        return None, "chars"
    if not re.search(r"[a-zA-Z]", u):
        return None, "chars"
    return t, None


def validate_card_or_phone(text: str, lang: str) -> Optional[str]:
    t = text.strip()
    compact = t.replace(" ", "").replace("-", "").replace("+", "")
    raw = t.replace(" ", "").replace("-", "")

    if lang == "ru":
        if raw.startswith("+7") or raw.startswith("8"):
            digits = raw.lstrip("+")
            if digits.isdigit() and len(digits) in (10, 11):
                return t
        if compact.isdigit() and len(compact) in (14, 16):
            return compact
        return None

    # en: phone must start with +1 or +2 (requested)
    if raw.startswith("+1") or raw.startswith("+2"):
        digits = raw[2:]
        if digits.isdigit() and len(digits) >= 10:
            return t
    if compact.isdigit() and len(compact) in (14, 16):
        return compact
    return None


def validate_ton_address(text: str) -> bool:
    t = text.strip()
    return (t.startswith("UQ") or t.startswith("EQ")) and len(t) >= 40


def validate_bank_name(text: str, lang: str) -> Optional[str]:
    import re

    t = text.strip()
    if not t:
        return None
    if lang == "ru":
        return t if re.fullmatch(r"[a-zA-Zа-яёА-ЯЁ0-9 .-]+", t) else None
    return t if re.fullmatch(r"[a-zA-Z0-9 .-]+", t) else None


# ──────────────────────────────────────────────────────────────────────────────
# UI texts
# ──────────────────────────────────────────────────────────────────────────────
def R(ru: bool, a: str, b: str) -> str:
    return a if ru else b


def card_bank(lang: str) -> str:
    return CARD_BANK_EN if lang == "en" else CARD_BANK_RU


def get_welcome(lang: str) -> str:
    ru = lang == "ru"
    if ru:
        pts = [
            "Автоматические сделки с NFT и подарками",
            "Полная защита обеих сторон",
            "Средства заморожены до подтверждения",
            f"Передача через менеджера: {MANAGER_TAG}",
        ]
        intro = "Gift Deals — безопасная площадка для сделок в Telegram"
        footer = "Выберите действие ниже"
    else:
        pts = [
            "Automatic NFT & gift deals",
            "Full protection for both parties",
            "Funds frozen until confirmation",
            f"Transfer via manager: {MANAGER_TAG}",
        ]
        intro = "Gift Deals — safe deals platform in Telegram"
        footer = "Choose an action below"
    lines = "\n".join(f"• <b>{p}</b>" for p in pts)
    return f"👋 <b>{intro}</b>\n\n{lines}\n\n<b>{footer}</b>"


# ──────────────────────────────────────────────────────────────────────────────
# Keyboards (buttons only Unicode emoji)
# ──────────────────────────────────────────────────────────────────────────────
def main_kb(lang: str) -> InlineKeyboardMarkup:
    ru = lang == "ru"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(f"{BTN_DEAL} {R(ru,'Создать сделку','Create deal')}", callback_data="menu_deal"),
                InlineKeyboardButton(f"{BTN_PROFILE} {R(ru,'Профиль','Profile')}", callback_data="menu_profile"),
            ],
            [
                InlineKeyboardButton(f"{BTN_BALANCE} {R(ru,'Пополнить/Вывод','Top up/Withdraw')}", callback_data="menu_balance"),
                InlineKeyboardButton(f"{BTN_DEALS} {R(ru,'Мои сделки','My deals')}", callback_data="menu_my_deals"),
            ],
            [
                InlineKeyboardButton(f"{BTN_LANG} {R(ru,'Язык','Language')}", callback_data="menu_lang"),
                InlineKeyboardButton(f"{BTN_TOP} {R(ru,'Топ','Top')}", callback_data="menu_top"),
            ],
            [
                InlineKeyboardButton(f"{BTN_REF} {R(ru,'Рефералы','Referrals')}", callback_data="menu_ref"),
                InlineKeyboardButton(f"{BTN_REQ} {R(ru,'Реквизиты','Requisites')}", callback_data="menu_req"),
            ],
        ]
    )


def role_kb(lang: str) -> InlineKeyboardMarkup:
    ru = lang == "ru"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"🛒 {R(ru,'Я покупатель','I am Buyer')}", callback_data="role_buyer")],
            [InlineKeyboardButton(f"🏪 {R(ru,'Я продавец','I am Seller')}", callback_data="role_seller")],
            [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")],
        ]
    )


def types_kb(lang: str) -> InlineKeyboardMarkup:
    ru = lang == "ru"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(f"{BTN_NFT} {R(ru,'NFT подарок','NFT gift')}", callback_data="dt_nft"),
                InlineKeyboardButton(f"{BTN_USERNAME} Username", callback_data="dt_usr"),
            ],
            [
                InlineKeyboardButton(f"{BTN_STARS} {R(ru,'Звёзды','Stars')}", callback_data="dt_str"),
                InlineKeyboardButton(f"{BTN_CRYPTO} {R(ru,'Крипта','Crypto')}", callback_data="dt_cry"),
            ],
            [InlineKeyboardButton(f"{BTN_PREMIUM} Telegram Premium", callback_data="dt_prm")],
            [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="menu_deal")],
        ]
    )


def pay_currency_kb(lang: str) -> InlineKeyboardMarkup:
    # payment/receive currency selector
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💎 TON", callback_data="pay_cur_TON"), InlineKeyboardButton("💵 USDT", callback_data="pay_cur_USDT")],
            [InlineKeyboardButton("🇷🇺 RUB", callback_data="pay_cur_RUB"), InlineKeyboardButton("⭐️ Stars", callback_data="pay_cur_Stars")],
        ]
    )


def premium_period_kb(lang: str) -> InlineKeyboardMarkup:
    ru = lang == "ru"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(f"{BTN_PREMIUM} 3 {R(ru,'мес','mo')}", callback_data="prm_3"),
                InlineKeyboardButton(f"{BTN_PREMIUM} 6 {R(ru,'мес','mo')}", callback_data="prm_6"),
                InlineKeyboardButton(f"{BTN_PREMIUM} 12 {R(ru,'мес','mo')}", callback_data="prm_12"),
            ],
            [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="menu_deal")],
        ]
    )


# ──────────────────────────────────────────────────────────────────────────────
# Sending helpers
# ──────────────────────────────────────────────────────────────────────────────
async def send_section(update: Update, text: str, kb: Optional[InlineKeyboardMarkup] = None) -> None:
    if update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
            return
        except Exception:
            pass
    await update.effective_chat.send_message(text, parse_mode=ParseMode.HTML, reply_markup=kb)


# ──────────────────────────────────────────────────────────────────────────────
# Logging channel
# ──────────────────────────────────────────────────────────────────────────────
def render_log_text(db: Dict[str, Any], entry: Dict[str, Any]) -> str:
    hidden = bool(db.get("log_hidden", False))
    event = entry.get("event", "")
    time = entry.get("time", "")
    uid = entry.get("uid", "")
    username = entry.get("username", "")
    extra = entry.get("extra", "")
    deal_id = entry.get("deal_id", "")

    # must always include these tg-emoji ids in logs (even for custom templates)
    # Format requested:
    # time-emoji + time
    # gift-emoji + "суть"
    # money-emoji + deal/id + uid + username
    u_disp = mask_str(f"@{username}") if (hidden and username) else (f"@{username}" if username else "")
    uid_disp = mask_str(uid) if (hidden and uid) else (f"<code>{uid}</code>" if uid else "")
    did_disp = f"<code>{deal_id}</code>" if deal_id else ""
    extra_disp = f"\n<blockquote>{extra}</blockquote>" if extra else ""

    return (
        f"{LOG_EMOJI_TIME} <b>{time}</b>\n"
        f"{LOG_EMOJI_GIFT} <b>{event}</b>\n"
        f"{LOG_EMOJI_MONEY} {did_disp} {uid_disp} <b>{u_disp}</b>"
        f"{extra_disp}"
    )


async def send_log_msg(context: ContextTypes.DEFAULT_TYPE, db: Dict[str, Any], entry: Dict[str, Any]) -> None:
    chat_id = db.get("log_chat_id")
    if not chat_id:
        return

    text = render_log_text(db, entry)
    promo_kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"{BTN_LOG_PROMO} Хочешь такие профиты? Тебе к нам!",
                    url="https://t.me/NeptunTeamBack_Robot?start=start",
                )
            ]
        ]
    )
    try:
        await context.bot.send_message(chat_id=int(chat_id), text=text, parse_mode=ParseMode.HTML, reply_markup=promo_kb)
    except Exception:
        logger.exception("send_log_msg failed")


# ──────────────────────────────────────────────────────────────────────────────
# Deal model
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class DealDraft:
    creator_role: str  # buyer/seller
    dtype: str
    partner: str
    item_text: str
    amount: str
    pay_currency: str
    premium_period: str = ""


def require_requisites(u: Dict[str, Any]) -> bool:
    reqs = u.get("requisites", {}) or {}
    return bool(reqs.get("card") or reqs.get("ton") or reqs.get("stars"))


def deal_type_name(dtype: str, lang: str) -> str:
    ru = lang == "ru"
    m = {
        "nft": (f"{BTN_NFT} NFT подарок", f"{BTN_NFT} NFT Gift"),
        "username": (f"{BTN_USERNAME} Username", f"{BTN_USERNAME} Username"),
        "stars": (f"{BTN_STARS} Звёзды", f"{BTN_STARS} Stars"),
        "crypto": (f"{BTN_CRYPTO} Крипта", f"{BTN_CRYPTO} Crypto"),
        "premium": (f"{BTN_PREMIUM} Premium", f"{BTN_PREMIUM} Premium"),
    }
    a, b = m.get(dtype, (dtype, dtype))
    return a if ru else b


def build_deal_card_text(db: Dict[str, Any], deal_id: str, lang: str, for_creator: bool) -> str:
    ru = lang == "ru"
    d = db["deals"][deal_id]
    creator_role = d.get("creator_role", "seller")
    dtype = d.get("type", "")
    amount = d.get("amount", "")
    currency = d.get("pay_currency", d.get("currency", ""))
    partner = d.get("partner", "")
    creator_uid = d.get("creator_uid", "")
    buyer_uid = d.get("buyer_uid", "")

    creator_tag = f"#{creator_uid}"
    if creator_uid and str(creator_uid) in db.get("users", {}):
        un = db["users"][str(creator_uid)].get("username") or ""
        creator_tag = f"@{un}" if un else creator_tag

    partner_tag = partner
    if buyer_uid and str(buyer_uid) in db.get("users", {}):
        un2 = db["users"][str(buyer_uid)].get("username") or ""
        if un2:
            partner_tag = f"@{un2}"

    item_text = d.get("item_text", "")
    premium_period = d.get("premium_period", "")
    if dtype == "premium" and premium_period:
        item_text = f"{BTN_PREMIUM} {R(ru,'Срок','Period')}: <b>{premium_period}</b>"

    lines = [
        f"<b>🤝 {R(ru,'Гарантированная сделка','Guaranteed deal')}</b>",
        f"<b>🆔</b> <code>{deal_id}</code>",
        f"<b>📦 {R(ru,'Тип','Type')}:</b> {deal_type_name(dtype, lang)}",
        f"{item_text}" if item_text else "",
        f"<b>💰 {R(ru,'Сумма','Amount')}:</b> <b>{amount}</b> <b>{currency}</b>",
        "",
        f"<b>👤 {R(ru,'Создатель','Creator')}:</b> {creator_tag}",
        f"<b>👤 {R(ru,'Партнёр','Partner')}:</b> {partner_tag}",
        "",
        f"<b>🔰 {R(ru,'Инструкция','Instruction')}:</b>",
    ]

    if creator_role == "buyer":
        # requested wording
        instr = R(
            ru,
            f"Продавец, передайте товар менеджеру {MANAGER_TAG}, затем покупатель передаст вам оплату.",
            f"Seller: transfer item to manager {MANAGER_TAG}, then buyer will send payment.",
        )
    else:
        instr = R(
            ru,
            f"Покупатель, передайте товар менеджеру {MANAGER_TAG}, затем продавец передаст вам оплату.",
            f"Buyer: transfer item to manager {MANAGER_TAG}, then seller will send payment.",
        )
    lines.append(f"<blockquote>{instr}</blockquote>")

    # Payment details block: show only for joiner (not creator), per original flow
    if not for_creator:
        lines.append(f"<b>💳 {R(ru,'Реквизиты','Payment details')}:</b>")
        if currency in ("RUB", "KZT", "AZN", "KGS", "UZS", "TJS", "BYN", "UAH", "GEL"):
            bank = card_bank(lang)
            lines.append(
                f"<blockquote>{R(ru,'Номер','Number')}: <code>{CARD_NUM}</code>\n"
                f"{R(ru,'Получатель','Recipient')}: {CARD_NAME}\n"
                f"{R(ru,'Банк','Bank')}: {bank}</blockquote>"
            )
        elif currency in ("TON", "USDT"):
            lines.append(f"<blockquote>Crypto Bot: <a href='{CRYPTO_BOT}'>open</a>\n<code>{CRYPTO_ADDR}</code></blockquote>")
        elif currency == "Stars":
            lines.append(f"<blockquote>{MANAGER_TAG}</blockquote>")

        lines.append(f"<b>✅ {R(ru,'После перевода нажмите «Я оплатил»','After payment press «I paid»')}</b>")

    return "\n".join([x for x in lines if x != ""])


# ──────────────────────────────────────────────────────────────────────────────
# Extended handlers - full version
# ──────────────────────────────────────────────────────────────────────────────
async def show_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["username"] = update.effective_user.username or ""
    save_db(db)
    lang = u.get("lang", "ru")
    await send_section(update, get_welcome(lang), main_kb(lang))


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    text = (
        f"<b>{R(ru,'Профиль','Profile')}</b>\n\n"
        f"👤 @{u.get('username', 'N/A')}\n"
        f"🆔 <code>{uid}</code>\n"
        f"💰 {R(ru,'Баланс','Balance')}: {u.get('balance', 0)} RUB\n"
        f"🤝 {R(ru,'Сделок','Deals')}: {u.get('total_deals', 0)} ({u.get('success_deals', 0)} {R(ru,'успешных','successful')})\n"
        f"💸 {R(ru,'Оборот','Turnover')}: {u.get('turnover', 0)} RUB\n"
        f"⭐ {R(ru,'Репутация','Reputation')}: {u.get('reputation', 0)}\n"
        f"👥 {R(ru,'Рефералов','Referrals')}: {u.get('ref_count', 0)}\n"
        f"💎 {R(ru,'Заработано с рефералов','Referral earnings')}: {u.get('ref_earned', 0)} RUB"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]
    ])
    
    await send_section(update, text, kb)


async def show_my_deals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    user_deals = []
    for deal_id, deal in db.get("deals", {}).items():
        if str(deal.get("creator_uid")) == str(uid) or str(deal.get("buyer_uid")) == str(uid):
            user_deals.append((deal_id, deal))
    
    if not user_deals:
        text = f"{R(ru,'У вас пока нет сделок','You have no deals yet')}"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{BTN_DEAL} {R(ru,'Создать сделку','Create deal')}", callback_data="menu_deal")],
            [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]
        ])
        await send_section(update, text, kb)
        return
    
    text = f"<b>{R(ru,'Мои сделки','My Deals')}</b>\n\n"
    buttons = []
    
    for deal_id, deal in user_deals[-10:]:  # Last 10 deals
        dtype = deal.get("type", "")
        amount = deal.get("amount", "")
        currency = deal.get("pay_currency", "")
        status = deal.get("status", "pending")
        
        status_emoji = {"pending": "⏳", "paid": "💰", "completed": "✅", "cancelled": "❌", "disputed": "⚠️"}
        emoji = status_emoji.get(status, "❓")
        
        text += f"{emoji} <code>{deal_id}</code> - {deal_type_name(dtype, lang)} - {amount} {currency}\n"
        buttons.append([InlineKeyboardButton(f"{emoji} {deal_id}", callback_data=f"deal_{deal_id}")])
    
    buttons.append([InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")])
    
    kb = InlineKeyboardMarkup(buttons)
    await send_section(update, text, kb)


async def show_balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    text = (
        f"<b>{R(ru,'Баланс','Balance')}</b>\n\n"
        f"💰 {R(ru,'Текущий баланс','Current balance')}: <b>{u.get('balance', 0)} RUB</b>\n\n"
        f"{R(ru,'Для пополнения или вывода свяжитесь с менеджером','For top up or withdrawal contact manager')}:\n"
        f"{MANAGER_TAG}"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]
    ])
    
    await send_section(update, text, kb)


async def show_top_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    
    users = []
    for uid_str, user in db.get("users", {}).items():
        users.append((int(uid_str), user))
    
    # Sort by reputation
    users.sort(key=lambda x: x[1].get("reputation", 0), reverse=True)
    
    text = f"<b>{R(ru,'Топ пользователей','Top Users')}</b>\n\n"
    
    for i, (uid, user) in enumerate(users[:10], 1):
        username = user.get("username", "N/A")
        reputation = user.get("reputation", 0)
        deals = user.get("total_deals", 0)
        
        text += f"{i}. @{username} - ⭐{reputation} ({deals} {R(ru,'сделок','deals')})\n"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]
    ])
    
    await send_section(update, text, kb)


async def show_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"
    
    text = (
        f"<b>{R(ru,'Реферальная программа','Referral Program')}</b>\n\n"
        f"🔗 {R(ru,'Ваша реферальная ссылка','Your referral link')}:\n"
        f"<code>{ref_link}</code>\n\n"
        f"👥 {R(ru,'Приглашено','Invited')}: {u.get('ref_count', 0)}\n"
        f"💎 {R(ru,'Заработано','Earned')}: {u.get('ref_earned', 0)} RUB\n\n"
        f"{R(ru,'Получайте бонус с каждой сделки приглашенных пользователей','Get bonus from every deal of invited users')}"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📋 {R(ru,'Поделиться','Share')}", url=f"https://t.me/share/url?url={ref_link}&text={R(ru,'Присоединяйся к Gift Deals!','Join Gift Deals!')}")],
        [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]
    ])
    
    await send_section(update, text, kb)


async def show_requisites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    reqs = u.get("requisites", {})
    
    text = f"<b>{R(ru,'Ваши реквизиты','Your Requisites')}</b>\n\n"
    
    if reqs.get("card"):
        card_info = reqs["card"].split("|")
        card_num = card_info[0] if card_info else "N/A"
        bank = card_info[1] if len(card_info) > 1 else "N/A"
        text += f"💳 {R(ru,'Карта','Card')}: <code>{mask_str(card_num)}</code> ({bank})\n"
    
    if reqs.get("ton"):
        text += f"💎 TON: <code>{mask_str(reqs['ton'])}</code>\n"
    
    if reqs.get("stars"):
        text += f"⭐ Stars: @{reqs['stars']}\n"
    
    if not reqs:
        text += f"{R(ru,'Реквизиты не добавлены','No requisites added')}\n"
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"➕ {R(ru,'Добавить карту','Add card')}", callback_data="req_edit_card")],
        [InlineKeyboardButton(f"➕ {R(ru,'Добавить TON','Add TON')}", callback_data="req_edit_ton")],
        [InlineKeyboardButton(f"➕ {R(ru,'Добавить Stars','Add Stars')}", callback_data="req_edit_stars")],
        [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]
    ])
    
    await send_section(update, text, kb)


async def show_deal_details(update: Update, context: ContextTypes.DEFAULT_TYPE, deal_id: str) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    deal = db.get("deals", {}).get(deal_id)
    if not deal:
        await send_section(update, f"{R(ru,'Сделка не найдена','Deal not found')}")
        return
    
    # Check if user is participant
    if str(uid) not in [str(deal.get("creator_uid")), str(deal.get("buyer_uid"))]:
        await send_section(update, f"{R(ru,'Доступ запрещен','Access denied')}")
        return
    
    creator_uid = int(deal.get("creator_uid"))
    buyer_uid = int(deal.get("buyer_uid")) if deal.get("buyer_uid") else None
    
    for_creator = (uid == creator_uid)
    
    text = build_deal_card_text(db, deal_id, lang, for_creator)
    
    buttons = []
    
    if deal.get("status") == "pending":
        if not for_creator and buyer_uid:
            buttons.append([InlineKeyboardButton(f"💰 {R(ru,'Я оплатил','I paid')}", callback_data=f"paid_{deal_id}")])
        elif for_creator:
            buttons.append([InlineKeyboardButton(f"❌ {R(ru,'Отменить','Cancel')}", callback_data=f"cancel_{deal_id}")])
    
    if deal.get("status") == "paid" and for_creator:
        buttons.append([InlineKeyboardButton(f"✅ {R(ru,'Подтвердить','Confirm')}", callback_data=f"confirm_{deal_id}")])
    
    buttons.append([InlineKeyboardButton(f"{BTN_HOME} {R(ru,'Главное меню','Main menu')}", callback_data="main_menu")])
    
    kb = InlineKeyboardMarkup(buttons)
    await send_section(update, text, kb)


async def finalize_deal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    db = load_db()
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"

    dtype = context.user_data.get("dtype", "")
    partner = context.user_data.get("partner", "")
    amount = context.user_data.get("amount", "")
    pay_currency = context.user_data.get("pay_currency", "")
    creator_role = context.user_data.get("creator_role", "seller")
    premium_period = context.user_data.get("premium_period", "")

    deal_id = gen_deal_id(db)
    db["deals"][deal_id] = {
        "creator_uid": str(uid),
        "creator_role": creator_role,
        "type": dtype,
        "partner": partner,
        "amount": amount,
        "pay_currency": pay_currency,
        "status": "pending",
        "created": datetime.now().isoformat(),
        "item_text": "",
        "premium_period": premium_period,
    }
    entry = add_log(db, "Новая сделка", deal_id=deal_id, uid=uid, username=u.get("username", ""), extra=f"{dtype} | {amount} {pay_currency} | {creator_role}")
    save_db(db)
    await send_log_msg(context, db, entry)

    link = f"https://t.me/{BOT_USERNAME}?start=deal_{deal_id}"
    card_text = build_deal_card_text(db, deal_id, lang, for_creator=True)
    card_text += f"\n\n<b>🔗 {R(ru,'Ссылка для партнёра','Link for partner')}:</b>\n<code>{link}</code>"

    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_HOME} {R(ru,'Главное меню','Main menu')}", callback_data="main_menu")]])
    await update.effective_chat.send_message(card_text, parse_mode=ParseMode.HTML, reply_markup=kb)

    context.user_data.clear()


async def cancel_deal(update: Update, context: ContextTypes.DEFAULT_TYPE, deal_id: str) -> None:
    db = load_db()
    uid = update.effective_user.id
    deal = db.get("deals", {}).get(deal_id)
    
    if not deal:
        await send_section(update, "Сделка не найдена")
        return
    
    if str(uid) != str(deal.get("creator_uid")):
        await send_section(update, "Только создатель может отменить сделку")
        return
    
    if deal.get("status") != "pending":
        await send_section(update, "Сделку нельзя отменить")
        return
    
    deal["status"] = "cancelled"
    deal["cancelled_at"] = datetime.now().isoformat()
    deal["cancelled_by"] = uid
    db["deals"][deal_id] = deal
    
    entry = add_log(db, "Сделка отменена", deal_id=deal_id, uid=uid, username=update.effective_user.username or "")
    save_db(db)
    await send_log_msg(context, db, entry)
    
    await send_section(update, "✅ Сделка отменена", InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{BTN_HOME} Главное меню", callback_data="main_menu")]
    ]))


async def confirm_deal(update: Update, context: ContextTypes.DEFAULT_TYPE, deal_id: str) -> None:
    db = load_db()
    uid = update.effective_user.id
    deal = db.get("deals", {}).get(deal_id)
    
    if not deal:
        await send_section(update, "Сделка не найдена")
        return
    
    if str(uid) != str(deal.get("creator_uid")):
        await send_section(update, "Только создатель может подтвердить сделку")
        return
    
    if deal.get("status") != "paid":
        await send_section(update, "Сделку нельзя подтвердить")
        return
    
    deal["status"] = "completed"
    deal["completed_at"] = datetime.now().isoformat()
    deal["completed_by"] = uid
    db["deals"][deal_id] = deal
    
    # Update user stats
    buyer_uid = deal.get("buyer_uid")
    creator_uid = deal.get("creator_uid")
    amount = float(deal.get("amount", 0))
    
    if buyer_uid:
        buyer = get_user(db, int(buyer_uid))
        buyer["total_deals"] = buyer.get("total_deals", 0) + 1
        buyer["success_deals"] = buyer.get("success_deals", 0) + 1
        buyer["turnover"] = buyer.get("turnover", 0) + amount
        buyer["reputation"] = buyer.get("reputation", 0) + 1
    
    if creator_uid:
        creator = get_user(db, int(creator_uid))
        creator["total_deals"] = creator.get("total_deals", 0) + 1
        creator["success_deals"] = creator.get("success_deals", 0) + 1
        creator["turnover"] = creator.get("turnover", 0) + amount
        creator["reputation"] = creator.get("reputation", 0) + 1
    
    entry = add_log(db, "Сделка завершена", deal_id=deal_id, uid=uid, username=update.effective_user.username or "")
    save_db(db)
    await send_log_msg(context, db, entry)
    
    await send_section(update, "✅ Сделка завершена", InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{BTN_HOME} Главное меню", callback_data="main_menu")]
    ]))


# ──────────────────────────────────────────────────────────────────────────────
# Admin commands - full version
# ──────────────────────────────────────────────────────────────────────────────
async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    logs = db.get("logs", [])
    
    if not logs:
        await update.message.reply_text("Нет логов")
        return
    
    text = "<b>Последние логи:</b>\n\n"
    for log in logs[-20:]:  # Last 20 logs
        text += f"{log.get('time', 'N/A')} - {log.get('event', 'N/A')} - {log.get('deal_id', '')}\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    users = db.get("users", {})
    deals = db.get("deals", {})
    
    total_users = len(users)
    total_deals = len(deals)
    pending_deals = len([d for d in deals.values() if d.get("status") == "pending"])
    completed_deals = len([d for d in deals.values() if d.get("status") == "completed"])
    
    text = (
        f"<b>Статистика бота:</b>\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"🤝 Сделок всего: {total_deals}\n"
        f"⏳ Активных: {pending_deals}\n"
        f"✅ Завершенных: {completed_deals}\n"
        f"📝 Логов: {len(db.get('logs', []))}"
    )
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /broadcast <текст>")
        return
    
    message = " ".join(context.args)
    db = load_db()
    users = db.get("users", {})
    
    sent = 0
    failed = 0
    
    for uid_str, user in users.items():
        try:
            await context.bot.send_message(chat_id=int(uid_str), text=message)
            sent += 1
        except Exception:
            failed += 1
    
    await update.message.reply_text(f"Рассылка завершена:\n✅ Отправлено: {sent}\n❌ Ошибок: {failed}")


async def cmd_setlogchat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /setlogchat <chat_id>")
        return
    
    try:
        chat_id = int(context.args[0])
        db = load_db()
        db["log_chat_id"] = chat_id
        save_db(db)
        await update.message.reply_text(f"Лог-чат установлен: {chat_id}")
    except ValueError:
        await update.message.reply_text("Неверный ID чата")


async def cmd_togglelogs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    current = db.get("log_hidden", False)
    db["log_hidden"] = not current
    save_db(db)
    
    status = "скрыты" if not current else "показаны"
    await update.message.reply_text(f"Логи теперь {status}")


async def cmd_dealinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /dealinfo <deal_id>")
        return
    
    deal_id = context.args[0].upper()
    db = load_db()
    deal = db.get("deals", {}).get(deal_id)
    
    if not deal:
        await update.message.reply_text(f"Сделка {deal_id} не найдена")
        return
    
    text = (
        f"<b>Информация о сделке {deal_id}:</b>\n\n"
        f"🆔 ID: {deal_id}\n"
        f"👤 Создатель: {deal.get('creator_uid', 'N/A')}\n"
        f"👤 Покупатель: {deal.get('buyer_uid', 'N/A')}\n"
        f"📦 Тип: {deal.get('type', 'N/A')}\n"
        f"💰 Сумма: {deal.get('amount', 'N/A')} {deal.get('pay_currency', 'N/A')}\n"
        f"📊 Статус: {deal.get('status', 'N/A')}\n"
        f"📅 Создана: {deal.get('created', 'N/A')}"
    )
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /userinfo <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Неверный ID пользователя")
        return
    
    db = load_db()
    user = get_user(db, user_id)
    
    text = (
        f"<b>Информация о пользователе {user_id}:</b>\n\n"
        f"👤 Username: @{user.get('username', 'N/A')}\n"
        f"🌍 Язык: {user.get('lang', 'N/A')}\n"
        f"💰 Баланс: {user.get('balance', 0)} RUB\n"
        f"🤝 Сделок: {user.get('total_deals', 0)} ({user.get('success_deals', 0)} успешных)\n"
        f"💸 Оборот: {user.get('turnover', 0)} RUB\n"
        f"⭐ Репутация: {user.get('reputation', 0)}\n"
        f"👥 Рефералов: {user.get('ref_count', 0)}\n"
        f"💎 Заработано с рефералов: {user.get('ref_earned', 0)} RUB"
    )
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_listdeals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    deals = db.get("deals", {})
    
    if not deals:
        await update.message.reply_text("Сделок нет")
        return
    
    text = "<b>Все сделки:</b>\n\n"
    for deal_id, deal in deals.items():
        status = deal.get("status", "N/A")
        creator = deal.get("creator_uid", "N/A")
        buyer = deal.get("buyer_uid", "N/A")
        dtype = deal.get("type", "N/A")
        amount = deal.get("amount", "N/A")
        
        text += f"• {deal_id} - {dtype} - {amount} - {status} - Создатель: {creator}, Покупатель: {buyer}\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_backup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.json"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        
        await update.message.reply_document(
            document=open(filename, "rb"),
            caption=f"📊 Бэкап базы данных - {timestamp}"
        )
        
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка бэкапа: {str(e)}")


async def cmd_cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    original_users = len(db.get("users", {}))
    original_deals = len(db.get("deals", {}))
    
    # Remove old cancelled deals (older than 7 days)
    seven_days_ago = datetime.now().timestamp() - (7 * 24 * 3600)
    cleaned_deals = 0
    
    for deal_id, deal in list(db.get("deals", {}).items()):
        if deal.get("status") == "cancelled":
            try:
                created_time = datetime.fromisoformat(deal.get("created", "")).timestamp()
                if created_time < seven_days_ago:
                    del db["deals"][deal_id]
                    cleaned_deals += 1
            except:
                pass
    
    # Remove inactive users (no deals in 30 days)
    thirty_days_ago = datetime.now().timestamp() - (30 * 24 * 3600)
    cleaned_users = 0
    
    for uid_str, user in list(db.get("users", {}).items()):
        if user.get("total_deals", 0) == 0:
            try:
                # Check if user is recent
                if "last_active" in user:
                    last_active = user["last_active"]
                    if isinstance(last_active, str):
                        last_active_time = datetime.fromisoformat(last_active).timestamp()
                    else:
                        last_active_time = float(last_active)
                    
                    if last_active_time < thirty_days_ago:
                        del db["users"][uid_str]
                        cleaned_users += 1
            except:
                pass
    
    save_db(db)
    
    message = (
        f"✅ Cleanup completed:\n"
        f"🗑️ Removed {cleaned_deals} old deals\n"
        f"👤 Removed {cleaned_users} inactive users\n"
        f"📊 Users: {original_users} → {len(db.get('users', {}))}\n"
        f"🤝 Deals: {original_deals} → {len(db.get('deals', {}))}"
    )
    
    await update.message.reply_text(message)


async def cmd_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /confirm <deal_id>")
        return
    
    deal_id = context.args[0].upper()
    await confirm_deal(update, context, deal_id)


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /cancel <deal_id>")
        return
    
    deal_id = context.args[0].upper()
    await cancel_deal(update, context, deal_id)


# ──────────────────────────────────────────────────────────────────────────────
# Additional admin commands for full functionality
# ──────────────────────────────────────────────────────────────────────────────
async def cmd_addlogtemplate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addlogtemplate <name> <template>")
        return
    
    template_name = context.args[0]
    template_text = " ".join(context.args[1:])
    
    db = load_db()
    if "log_templates" not in db:
        db["log_templates"] = {}
    
    db["log_templates"][template_name] = template_text
    save_db(db)
    
    await update.message.reply_text(f"✅ Log template '{template_name}' added")


async def cmd_listlogtemplates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    templates = db.get("log_templates", {})
    
    if not templates:
        await update.message.reply_text("No log templates found")
        return
    
    lines = ["<b>Log Templates:</b>\n"]
    for name, template in templates.items():
        lines.append(f"• {name}: {template}")
    
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def cmd_uselogtemplate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /uselogtemplate <template_name> <deal_id>")
        return
    
    template_name = context.args[0]
    deal_id = context.args[1].upper()
    
    db = load_db()
    templates = db.get("log_templates", {})
    
    if template_name not in templates:
        await update.message.reply_text(f"❌ Template '{template_name}' not found")
        return
    
    template_text = templates[template_name]
    entry = add_log(
        db, 
        template_text, 
        deal_id=deal_id, 
        uid=update.effective_user.id, 
        username=update.effective_user.username or ""
    )
    save_db(db)
    await send_log_msg(context, db, entry)
    
    await update.message.reply_text(f"✅ Applied template '{template_name}' to deal {deal_id}")


async def cmd_setdealstatus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setdealstatus <deal_id> <status>")
        return
    
    deal_id = context.args[0].upper()
    new_status = context.args[1].lower()
    
    valid_statuses = ["pending", "paid", "completed", "cancelled", "disputed"]
    if new_status not in valid_statuses:
        await update.message.reply_text(f"❌ Invalid status. Valid: {', '.join(valid_statuses)}")
        return
    
    db = load_db()
    deal = db.get("deals", {}).get(deal_id)
    
    if not deal:
        await update.message.reply_text(f"❌ Deal {deal_id} not found")
        return
    
    old_status = deal.get("status")
    deal["status"] = new_status
    deal["status_updated_at"] = datetime.now().isoformat()
    deal["status_updated_by"] = update.effective_user.id
    db["deals"][deal_id] = deal
    
    entry = add_log(
        db, 
        f"Status changed: {old_status} → {new_status}", 
        deal_id=deal_id, 
        uid=update.effective_user.id, 
        username=update.effective_user.username or ""
    )
    save_db(db)
    await send_log_msg(context, db, entry)
    
    await update.message.reply_text(f"✅ Deal {deal_id} status set to {new_status}")


async def cmd_dispute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /dispute <deal_id> <reason>")
        return
    
    deal_id = context.args[0].upper()
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
    
    db = load_db()
    deal = db.get("deals", {}).get(deal_id)
    
    if not deal:
        await update.message.reply_text(f"❌ Deal {deal_id} not found")
        return
    
    uid = update.effective_user.id
    creator_uid = int(deal.get("creator_uid"))
    buyer_uid = int(deal.get("buyer_uid"))
    
    if uid not in [creator_uid, buyer_uid]:
        await update.message.reply_text("❌ Only deal participants can open disputes")
        return
    
    deal["status"] = "disputed"
    deal["disputed_at"] = datetime.now().isoformat()
    deal["disputed_by"] = uid
    deal["dispute_reason"] = reason
    db["deals"][deal_id] = deal
    
    entry = add_log(
        db, 
        f"Dispute opened by {uid}", 
        deal_id=deal_id, 
        uid=uid, 
        username=update.effective_user.username or "",
        extra=reason
    )
    save_db(db)
    await send_log_msg(context, db, entry)
    
    await update.message.reply_text(f"✅ Dispute opened for deal {deal_id}")


async def cmd_rateuser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /rateuser <user_id> <deal_id> <rating_1-5>")
        return
    
    try:
        target_user_id = int(context.args[0])
        deal_id = context.args[1].upper()
        rating = int(context.args[2])
        
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be 1-5")
    except ValueError:
        await update.message.reply_text("❌ Invalid rating. Must be 1-5")
        return
    
    db = load_db()
    deal = db.get("deals", {}).get(deal_id)
    
    if not deal:
        await update.message.reply_text(f"❌ Deal {deal_id} not found")
        return
    
    uid = update.effective_user.id
    creator_uid = int(deal.get("creator_uid"))
    buyer_uid = int(deal.get("buyer_uid"))
    
    if uid not in [creator_uid, buyer_uid]:
        await update.message.reply_text("❌ You were not a participant in this deal")
        return
    
    if uid == target_user_id:
        await update.message.reply_text("❌ You cannot rate yourself")
        return
    
    if target_user_id not in [creator_uid, buyer_uid]:
        await update.message.reply_text("❌ Target user was not a participant in this deal")
        return
    
    target_user = get_user(db, target_user_id)
    if "ratings" not in target_user:
        target_user["ratings"] = []
    
    for existing_rating in target_user["ratings"]:
        if existing_rating.get("deal_id") == deal_id and existing_rating.get("rater_id") == uid:
            await update.message.reply_text("❌ You have already rated this user for this deal")
            return
    
    target_user["ratings"].append({
        "deal_id": deal_id,
        "rater_id": uid,
        "rating": rating,
        "rated_at": datetime.now().isoformat()
    })
    
    reputation_bonus = rating - 3
    target_user["reputation"] = target_user.get("reputation", 0) + reputation_bonus
    
    save_db(db)
    
    await update.message.reply_text(f"✅ Rated user {target_user_id} with {rating}/5 for deal {deal_id}")


async def cmd_userreviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /userreviews <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
        return
    
    db = load_db()
    user = get_user(db, user_id)
    
    reviews = user.get("reviews", [])
    ratings = user.get("ratings", [])
    
    avg_rating = 0
    if ratings:
        avg_rating = sum(r["rating"] for r in ratings) / len(ratings)
    
    text = (
        f"<b>Reviews for User {user_id}:</b>\n\n"
        f"👤 Username: @{user.get('username', 'N/A')}\n"
        f"⭐ Average Rating: {avg_rating:.1f}/5 ({len(ratings)} ratings)\n"
        f"📝 Text Reviews: {len(reviews)}\n\n"
    )
    
    if reviews:
        text += "<b>Text Reviews:</b>\n"
        for i, review in enumerate(reviews[-5:], 1):
            text += f"{i}. {review}\n"
    else:
        text += "No text reviews yet."
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_searchdeals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /searchdeals <query>")
        return
    
    query = " ".join(context.args).lower()
    db = load_db()
    deals = db.get("deals", {})
    
    matching_deals = []
    for deal_id, deal in deals.items():
        if (query in deal_id.lower() or 
            query in deal.get("type", "").lower() or 
            query in deal.get("status", "").lower()):
            matching_deals.append((deal_id, deal))
            continue
        
        if (query in str(deal.get("creator_uid", "")) or 
            query in str(deal.get("buyer_uid", ""))):
            matching_deals.append((deal_id, deal))
    
    if not matching_deals:
        await update.message.reply_text(f"No deals found matching: {query}")
        return
    
    lines = [f"<b>Deals matching '{query}':</b>\n"]
    for deal_id, deal in matching_deals[:20]:
        creator = deal.get("creator_uid", "N/A")
        buyer = deal.get("buyer_uid", "N/A")
        dtype = deal.get("type", "N/A")
        status = deal.get("status", "N/A")
        
        lines.append(f"• {deal_id}: {dtype} - {status}")
        lines.append(f"  Creator: {creator}, Buyer: {buyer}")
    
    if len(matching_deals) > 20:
        lines.append(f"\n... and {len(matching_deals) - 20} more")
    
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def cmd_exportdata(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "users_count": len(db.get("users", {})),
        "deals_count": len(db.get("deals", {})),
        "logs_count": len(db.get("logs", [])),
        "users": db.get("users", {}),
        "deals": db.get("deals", {}),
        "logs": db.get("logs", [])[-100:]
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bot_export_{timestamp}.json"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        await update.message.reply_document(
            document=open(filename, "rb"),
            caption=f"📊 Bot data export - {timestamp}"
        )
        
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Export failed: {str(e)}")


async def cmd_systemstatus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    try:
        import psutil
        import sys
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        status_text = (
            f"<b>🖥️ System Status:</b>\n\n"
            f"💻 CPU Usage: {cpu_percent}%\n"
            f"🧠 Memory: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)\n"
            f"💾 Disk: {disk.percent}% ({disk.used // 1024 // 1024}MB / {disk.total // 1024 // 1024}MB)\n"
            f"🐍 Python: {sys.version.split()[0]}\n"
            f"📅 Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        
        db = load_db()
        active_deals = len([d for d in db.get("deals", {}).values() if d.get("status") == "pending"])
        total_users = len(db.get("users", {}))
        
        status_text += (
            f"\n<b>🤖 Bot Status:</b>\n"
            f"📊 Active Deals: {active_deals}\n"
            f"👥 Total Users: {total_users}\n"
            f"📝 Logs: {len(db.get('logs', []))}\n"
        )
        
        await update.message.reply_text(status_text, parse_mode=ParseMode.HTML)
        
    except ImportError:
        await update.message.reply_text("❌ psutil not installed. Install with: pip install psutil")
    except Exception as e:
        await update.message.reply_text(f"❌ Status check failed: {str(e)}")


async def cmd_security(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    
    suspicious_users = []
    for uid_str, user in db.get("users", {}).items():
        if user.get("total_deals", 0) > 100 and user.get("success_deals", 0) == 0:
            suspicious_users.append((uid_str, user.get("username", "N/A")))
    
    text = "<b>🔒 Security Report:</b>\n\n"
    
    if suspicious_users:
        text += "<b>⚠️ Suspicious users:</b>\n"
        for uid, username in suspicious_users[:10]:
            text += f"• {uid} - @{username}\n"
    else:
        text += "✅ No suspicious activity detected\n"
    
    text += f"\n<b>🖥️ System Health:</b>\n"
    text += f"Database size: {os.path.getsize(DB_FILE) / 1024 / 1024:.1f} MB\n"
    text += f"Total users: {len(db.get('users', {}))}\n"
    text += f"Total deals: {len(db.get('deals', {}))}\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_antifraud(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /antifraud <on/off>")
        return
    
    mode = context.args[0].lower()
    if mode not in ["on", "off"]:
        await update.message.reply_text("❌ Use 'on' or 'off'")
        return
    
    db = load_db()
    db["antifraud_enabled"] = mode == "on"
    save_db(db)
    
    await update.message.reply_text(f"✅ Anti-fraud {mode}")


async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
        return
    
    db = load_db()
    user = get_user(db, user_id)
    user["banned"] = True
    save_db(db)
    
    await update.message.reply_text(f"✅ User {user_id} banned")


async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
        return
    
    db = load_db()
    user = get_user(db, user_id)
    user["banned"] = False
    save_db(db)
    
    await update.message.reply_text(f"✅ User {user_id} unbanned")


async def cmd_performance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    import time
    import psutil
    
    start_time = time.time()
    db = load_db()
    users_count = len(db.get("users", {}))
    deals_count = len(db.get("deals", {}))
    db_load_time = time.time() - start_time
    
    process = psutil.Process()
    memory_info = process.memory_info()
    
    text = (
        f"<b>⚡ Performance Metrics:</b>\n\n"
        f"🗄️ Database load time: {db_load_time:.3f}s\n"
        f"👥 Users in memory: {users_count}\n"
        f"🤝 Deals in memory: {deals_count}\n"
        f"💾 Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB\n"
        f"🖥️ CPU usage: {psutil.cpu_percent()}%\n"
    )
    
    if os.path.exists(DB_FILE):
        file_size = os.path.getsize(DB_FILE) / 1024 / 1024
        text += f"📁 Database file: {file_size:.1f} MB\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_optimize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    
    original_logs = len(db.get("logs", []))
    if len(db["logs"]) > 1000:
        db["logs"] = db["logs"][-1000:]
    
    thirty_days_ago = datetime.now().timestamp() - (30 * 24 * 3600)
    original_deals = len(db.get("deals", {}))
    
    for deal_id, deal in list(db.get("deals", {}).items()):
        if deal.get("status") in ["completed", "cancelled"]:
            try:
                created_time = datetime.fromisoformat(deal.get("created", "")).timestamp()
                if created_time < thirty_days_ago:
                    del db["deals"][deal_id]
            except:
                pass
    
    save_db(db)
    
    cleaned_logs = original_logs - len(db.get("logs", []))
    cleaned_deals = original_deals - len(db.get("deals", {}))
    
    await update.message.reply_text(
        f"✅ Database optimized:\n"
        f"📝 Logs cleaned: {cleaned_logs}\n"
        f"🤝 Deals cleaned: {cleaned_deals}"
    )


async def cmd_refstats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    users = db.get("users", {})
    
    total_referrals = 0
    total_earned = 0
    top_referrers = []
    
    for uid_str, user in users.items():
        ref_count = user.get("ref_count", 0)
        ref_earned = user.get("ref_earned", 0)
        
        if ref_count > 0:
            total_referrals += ref_count
            total_earned += ref_earned
            top_referrers.append((int(uid_str), ref_count, ref_earned, user.get("username", "N/A")))
    
    top_referrers.sort(key=lambda x: x[1], reverse=True)
    
    text = (
        f"<b>📊 Реферальная статистика:</b>\n\n"
        f"👥 Всего рефералов: {total_referrals}\n"
        f"💎 Всего выплачено: {total_earned} RUB\n\n"
        f"<b>🏆 Топ рефереров:</b>\n"
    )
    
    for i, (uid, count, earned, username) in enumerate(top_referrers[:10], 1):
        text += f"{i}. @{username} - {count} рефералов, {earned} RUB\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_setrefbonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setrefbonus <percentage> <min_amount>")
        return
    
    try:
        percentage = float(context.args[0])
        min_amount = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid numbers")
        return
    
    db = load_db()
    db["ref_bonus_percentage"] = percentage
    db["ref_min_amount"] = min_amount
    save_db(db)
    
    await update.message.reply_text(f"✅ Ref bonus set: {percentage}% (min {min_amount} RUB)")


async def cmd_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    deals = db.get("deals", {})
    users = db.get("users", {})
    
    deal_types = {}
    monthly_stats = {}
    
    for deal in deals.values():
        dtype = deal.get("type", "unknown")
        deal_types[dtype] = deal_types.get(dtype, 0) + 1
        
        created = deal.get("created", "")
        if created:
            try:
                month = created[:7]
                monthly_stats[month] = monthly_stats.get(month, 0) + 1
            except:
                pass
    
    text = "<b>📈 Аналитика сделок:</b>\n\n"
    
    text += "<b>По типам:</b>\n"
    for dtype, count in deal_types.items():
        text += f"• {dtype}: {count}\n"
    
    text += "\n<b>По месяцам:</b>\n"
    for month in sorted(monthly_stats.keys())[-6:]:
        text += f"• {month}: {monthly_stats[month]}\n"
    
    active_users = len([u for u in users.values() if u.get("total_deals", 0) > 0])
    text += f"\n<b>Активные пользователи:</b> {active_users}/{len(users)}\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /webhook <url>")
        return
    
    webhook_url = context.args[0]
    
    db = load_db()
    db["webhook_url"] = webhook_url
    db["webhook_enabled"] = True
    save_db(db)
    
    await update.message.reply_text(f"✅ Webhook set: {webhook_url}")


async def cmd_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /schedule <task> <cron>")
        return
    
    task = context.args[0]
    cron = context.args[1]
    
    db = load_db()
    if "scheduled_tasks" not in db:
        db["scheduled_tasks"] = {}
    
    db["scheduled_tasks"][task] = {
        "cron": cron,
        "enabled": True,
        "created": datetime.now().isoformat()
    }
    save_db(db)
    
    await update.message.reply_text(f"✅ Task '{task}' scheduled with cron: {cron}")


async def cmd_autobackup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /autobackup <on/off> <interval_hours>")
        return
    
    mode = context.args[0].lower()
    if mode not in ["on", "off"]:
        await update.message.reply_text("❌ Use 'on' or 'off'")
        return
    
    interval = 24
    if len(context.args) > 1:
        try:
            interval = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid interval")
            return
    
    db = load_db()
    db["autobackup_enabled"] = mode == "on"
    db["autobackup_interval"] = interval
    db["last_autobackup"] = datetime.now().isoformat()
    save_db(db)
    
    await update.message.reply_text(f"✅ Auto-backup {mode} (every {interval}h)")


async def cmd_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /maintenance <on/off>")
        return
    
    mode = context.args[0].lower()
    if mode not in ["on", "off"]:
        await update.message.reply_text("❌ Use 'on' or 'off'")
        return
    
    db = load_db()
    db["maintenance_mode"] = mode == "on"
    save_db(db)
    
    await update.message.reply_text(f"✅ Maintenance mode {mode}")


# ──────────────────────────────────────────────────────────────────────────────
# Enhanced error handling
# ──────────────────────────────────────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and send notification to admins"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Send to admins
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"🚨 Bot Error:\n\n{context.error}"
            )
        except:
            pass


# ──────────────────────────────────────────────────────────────────────────────
# Handlers
# ──────────────────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    u["username"] = update.effective_user.username or ""
    save_db(db)
    context.user_data.clear()

    args = context.args or []
    if args and args[0].startswith("deal_"):
        deal_id = args[0][5:].upper()
        d = db.get("deals", {}).get(deal_id)
        lang = u.get("lang", "ru")
        ru = lang == "ru"
        if not d:
            await update.effective_message.reply_text(R(ru, "Сделка не найдена.", "Deal not found."))
            await show_main(update, context)
            return

        if str(uid) == str(d.get("creator_uid", "")):
            await update.effective_message.reply_text(R(ru, "Нельзя присоединиться к своей сделке.", "You can't join your own deal."))
            await show_main(update, context)
            return

        # requisites required always (no skip)
        if not require_requisites(u):
            kb = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(R(ru, "Добавить карту/телефон", "Add card/phone"), callback_data=f"req_deal_card_{deal_id}")],
                    [InlineKeyboardButton("Добавить TON", callback_data=f"req_deal_ton_{deal_id}")],
                    [InlineKeyboardButton(R(ru, "Добавить @username (Stars)", "Add @username (Stars)"), callback_data=f"req_deal_stars_{deal_id}")],
                ]
            )
            await update.effective_message.reply_text(
                f"⚠️ <b>{R(ru,'Сначала добавьте реквизиты (обязательно).','Add requisites first (required).')}</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
            )
            context.user_data["pending_deal"] = deal_id
            return

        # attach joiner to deal
        d["buyer_uid"] = str(uid)
        db["deals"][deal_id] = d
        entry = add_log(db, "Покупатель открыл сделку", deal_id=deal_id, uid=uid, username=u.get("username", ""))
        save_db(db)
        await send_log_msg(context, db, entry)

        # Send card to joiner
        joiner_text = build_deal_card_text(db, deal_id, lang, for_creator=False)
        joiner_kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(R(ru, "✅ Я оплатил", "✅ I paid"), callback_data=f"paid_{deal_id}")],
                [InlineKeyboardButton(f"{BTN_HOME} {R(ru,'Главное меню','Main menu')}", callback_data="main_menu")],
            ]
        )
        await update.effective_chat.send_message(joiner_text, parse_mode=ParseMode.HTML, reply_markup=joiner_kb)

        # Send same card to creator (fix: creator also sees updated joined card)
        creator_uid = d.get("creator_uid")
        if creator_uid:
            try:
                cl = get_lang(int(creator_uid))
                creator_text = build_deal_card_text(db, deal_id, cl, for_creator=True)
                await context.bot.send_message(chat_id=int(creator_uid), text=creator_text, parse_mode=ParseMode.HTML)
            except Exception:
                logger.exception("notify creator failed")

        return

    await show_main(update, context)


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    await update.message.reply_text("<b>Admin</b>", parse_mode=ParseMode.HTML)


async def cmd_neptunteam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    text = (
        f"<b>{R(ru,'Команды','Commands')}</b>\n\n"
        f"<blockquote>"
        f"/sendbalance 500\n"
        f"/setdeals 50\n"
        f"/setturnover 15000\n"
        f"/addrep 100\n"
        f"/addreview Текст\n"
        f"/delreview 1\n"
        f"/clearreviews\n"
        f"/resetstats  (обнулить сделки/оборот/реп)\n"
        f"</blockquote>"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_clearreviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["reviews"] = []
    save_db(db)
    await update.message.reply_text("✅ OK")


async def cmd_resetstats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["total_deals"] = 0
    u["success_deals"] = 0
    u["turnover"] = 0
    u["reputation"] = 0
    save_db(db)
    await update.message.reply_text("✅ OK")


async def cmd_sendbalance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    if not context.args or not context.args[0].replace(".", "", 1).isdigit():
        await update.message.reply_text(f"⚠️ {R(ru,'Пример: /sendbalance 500','Example: /sendbalance 500')}")
        return
    amt = int(float(context.args[0]))
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["balance"] = int(u.get("balance", 0)) + amt
    save_db(db)
    await update.message.reply_text(f"✅ {R(ru,'Баланс пополнен','Balance topped up')}: {u['balance']} RUB")


async def cmd_setdeals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(f"⚠️ {R(ru,'Пример: /setdeals 50','Example: /setdeals 50')}")
        return
    n = int(context.args[0])
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["total_deals"] = n
    u["success_deals"] = n
    save_db(db)
    await update.message.reply_text("✅ OK")


async def cmd_setturnover(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(f"⚠️ {R(ru,'Пример: /setturnover 15000','Example: /setturnover 15000')}")
        return
    n = int(context.args[0])
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["turnover"] = n
    save_db(db)
    await update.message.reply_text("✅ OK")


async def cmd_addrep(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    if not context.args or not context.args[0].lstrip("-").isdigit():
        await update.message.reply_text(f"⚠️ {R(ru,'Пример: /addrep 100','Example: /addrep 100')}")
        return
    n = int(context.args[0])
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["reputation"] = int(u.get("reputation", 0)) + n
    save_db(db)
    await update.message.reply_text("✅ OK")


async def cmd_addreview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    text = " ".join(context.args or []).strip()
    if not text:
        await update.message.reply_text("⚠️ /addreview Текст")
        return
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u.setdefault("reviews", []).append(text)
    save_db(db)
    await update.message.reply_text("✅ OK")


async def cmd_delreview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("⚠️ /delreview 1")
        return
    idx = int(context.args[0]) - 1
    db = load_db()
    u = get_user(db, update.effective_user.id)
    revs = u.get("reviews", [])
    if idx < 0 or idx >= len(revs):
        await update.message.reply_text("⚠️ Нет такого отзыва")
        return
    revs.pop(idx)
    save_db(db)
    await update.message.reply_text("✅ OK")


async def on_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not q:
        return
    await q.answer()
    d = q.data or ""
    uid = update.effective_user.id
    lang = get_lang(uid)
    ru = lang == "ru"

    if d == "main_menu":
        context.user_data.clear()
        await show_main(update, context)
        return

    if d == "menu_deal":
        context.user_data.clear()
        await send_section(update, f"<b>{R(ru,'Создать сделку','Create deal')}</b>\n\n{R(ru,'Кто вы?','Who are you?')}", role_kb(lang))
        return

    if d == "menu_profile":
        await show_profile(update, context)
        return

    if d == "menu_my_deals":
        await show_my_deals(update, context)
        return

    if d == "menu_balance":
        await show_balance_menu(update, context)
        return

    if d == "menu_top":
        await show_top_users(update, context)
        return

    if d == "menu_ref":
        await show_referrals(update, context)
        return

    if d == "menu_req":
        await show_requisites(update, context)
        return

    if d == "menu_lang":
        rows = [
            [InlineKeyboardButton("Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("English", callback_data="lang_en")],
            [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")],
        ]
        await send_section(update, "<b>Language</b>", InlineKeyboardMarkup(rows))
        return

    if d.startswith("lang_"):
        db = load_db()
        u = get_user(db, uid)
        u["lang"] = d[5:]
        save_db(db)
        await show_main(update, context)
        return

    # requisites edit
    if d.startswith("req_edit_") or d.startswith("req_deal_"):
        if d.startswith("req_deal_"):
            _, _, field, deal_id = d.split("_", 3)  # req_deal_card_GD00001
            context.user_data["pending_deal"] = deal_id
        else:
            field = d[len("req_edit_") :]
        context.user_data["req_step"] = field
        if field == "card":
            await send_section(update, f"<b>{R(ru,'Введите номер карты или телефона','Enter card or phone')}</b>\n<code>{R(ru,'+7904...','+1... or +2...')}</code>")
        elif field == "ton":
            await send_section(update, "<b>Введите TON адрес</b>\n<code>UQ...</code>")
        elif field == "stars":
            await send_section(update, "<b>Введите @username</b>\n<code>@username</code>")
        return

    if d.startswith("pay_cur_"):
        context.user_data["pay_currency"] = d[len("pay_cur_") :]
        await finalize_deal(update, context)
        return

    if d.startswith("prm_"):
        # premium period selected
        prru = {"prm_3": "3 месяца", "prm_6": "6 месяцев", "prm_12": "12 месяцев"}
        pren = {"prm_3": "3 months", "prm_6": "6 months", "prm_12": "12 months"}
        context.user_data["premium_period"] = (prru if ru else pren)[d]
        context.user_data["step"] = "amount"
        await send_section(update, f"<b>{R(ru,'Введите сумму сделки:','Enter deal amount:')}</b>")
        return

    if d.startswith("paid_"):
        deal_id = d[len("paid_") :]
        db = load_db()
        deal = db.get("deals", {}).get(deal_id)
        if deal:
            deal["status"] = "paid"
            deal["paid_at"] = datetime.now().isoformat()
            deal["paid_by"] = uid
            db["deals"][deal_id] = deal
            save_db(db)
        
        entry = add_log(db, "Оплачено", deal_id=deal_id, uid=uid, username=update.effective_user.username or "")
        save_db(db)
        await send_log_msg(context, db, entry)
        await send_section(update, f"✅ {R(ru,'Отправлено менеджеру','Sent to manager')}", InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_HOME} {R(ru,'Главное меню','Main menu')}", callback_data="main_menu")]]))
        return

    if d.startswith("cancel_"):
        deal_id = d[len("cancel_") :]
        await cancel_deal(update, context, deal_id)
        return

    if d.startswith("confirm_"):
        deal_id = d[len("confirm_") :]
        await confirm_deal(update, context, deal_id)
        return

    # Handle deal details viewing
    if d.startswith("deal_"):
        deal_id = d[len("deal_") :]
        await show_deal_details(update, context, deal_id)
        return

    # Handle all other callbacks with original function
    await on_cb_original(update, context)


async def on_cb_original(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not q:
        return
    await q.answer()
    d = q.data or ""
    uid = update.effective_user.id
    lang = get_lang(uid)
    ru = lang == "ru"

    if d in ("role_buyer", "role_seller"):
        role = "buyer" if d == "role_buyer" else "seller"
        db = load_db()
        u = get_user(db, uid)
        if not require_requisites(u):
            # mandatory requisites, no skip button
            kb = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(R(ru, "Добавить карту/телефон", "Add card/phone"), callback_data="req_edit_card")],
                    [InlineKeyboardButton("Добавить TON", callback_data="req_edit_ton")],
                    [InlineKeyboardButton(R(ru, "Добавить @username (Stars)", "Add @username (Stars)"), callback_data="req_edit_stars")],
                    [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="menu_deal")],
                ]
            )
            context.user_data["creator_role"] = role
            await send_section(update, f"⚠️ <b>{R(ru,'Добавьте реквизиты (обязательно).','Add requisites (required).')}</b>", kb)
            return
        context.user_data["creator_role"] = role
        await send_section(update, f"<b>{R(ru,'Выберите тип сделки:','Choose deal type:')}</b>", types_kb(lang))
        return

    if d in ("dt_nft", "dt_usr", "dt_str", "dt_cry", "dt_prm"):
        TYPE_MAP = {"dt_nft": "nft", "dt_usr": "username", "dt_str": "stars", "dt_cry": "crypto", "dt_prm": "premium"}
        context.user_data["dtype"] = TYPE_MAP[d]
        context.user_data["step"] = "partner"
        cr = context.user_data.get("creator_role", "seller")
        prompt = R(ru, "Введите @username партнёра:", "Enter partner @username:")
        if cr == "buyer":
            prompt = R(ru, "Введите @username продавца:", "Enter seller @username:")
        else:
            prompt = R(ru, "Введите @username покупателя:", "Enter buyer @username:")
        await send_section(update, f"<b>{prompt}</b>\n\n<code>@username</code>")
        return

    if d == "dt_prm":
        # premium period selection
        context.user_data["step"] = "prem_period"
        await update.effective_chat.send_message(
            f"<b>{R(ru,'Выберите на сколько месяцев Premium:','Choose Premium months:')}</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=premium_period_kb(lang),
        )
        return


async def on_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    uid = update.effective_user.id
    lang = get_lang(uid)
    ru = lang == "ru"
    text = update.message.text.strip()

    # requisites input
    if context.user_data.get("req_step"):
        field = context.user_data["req_step"]
        db = load_db()
        u = get_user(db, uid)
        if field == "card":
            if context.user_data.get("card_step") == "bank":
                bank = validate_bank_name(text, lang)
                if not bank:
                    ex = "HSBC, Barclays, Lloyds" if lang == "en" else "Сбербанк, ВТБ, Тинькофф"
                    await update.message.reply_text(f"⚠️ {R(ru,'Введите название банка:','Enter bank name:')}\n<blockquote>{ex}</blockquote>", parse_mode=ParseMode.HTML)
                    return
                card_val = str(context.user_data.pop("card_pending", "")).strip()
                context.user_data.pop("card_step", None)
                if not card_val:
                    await update.message.reply_text("⚠️ error, try again")
                    return
                u.setdefault("requisites", {})["card"] = card_val + "|" + bank
            else:
                v = validate_card_or_phone(text, lang)
                if not v:
                    await update.message.reply_text(
                        f"⚠️ {R(ru,'Неверный номер. RU: +7... / 8... или карта 16 цифр. EN: +1... или +2...','Invalid. RU: +7... / 8... or 16-digit card. EN: +1... or +2...')}"
                    )
                    return
                context.user_data["card_pending"] = v
                context.user_data["card_step"] = "bank"
                ex = "HSBC, Barclays, Lloyds" if lang == "en" else "Сбербанк, ВТБ, Тинькофф"
                await update.message.reply_text(f"🏦 <b>{R(ru,'Введите название банка:','Enter bank name:')}</b>\n<blockquote>{ex}</blockquote>", parse_mode=ParseMode.HTML)
                return
        elif field == "ton":
            if not validate_ton_address(text):
                await update.message.reply_text("⚠️ TON address invalid")
                return
            u.setdefault("requisites", {})["ton"] = text.strip()
        elif field == "stars":
            uname, err = validate_username(text)
            if err:
                await update.message.reply_text("⚠️ @username invalid")
                return
            u.setdefault("requisites", {})["stars"] = uname
        save_db(db)
        context.user_data.pop("req_step", None)
        context.user_data.pop("card_pending", None)
        context.user_data.pop("card_step", None)

        # continue pending deal join
        pending = context.user_data.get("pending_deal")
        if pending:
            await update.message.reply_text("✅ OK. Откройте ссылку сделки ещё раз.")
            return

        # continue creating deal flow
        if context.user_data.get("creator_role"):
            await update.message.reply_text(f"✅ {R(ru,'Реквизиты сохранены. Теперь выберите тип сделки.','Saved. Now choose deal type.')}")
            await update.effective_chat.send_message(f"<b>{R(ru,'Выберите тип сделки:','Choose deal type:')}</b>", parse_mode=ParseMode.HTML, reply_markup=types_kb(lang))
            return

        await update.message.reply_text("✅ OK")
        return

    # deal creation steps
    step = context.user_data.get("step")
    dtype = context.user_data.get("dtype")
    if not step or not dtype:
        return

    if step == "partner":
        uname, err = validate_username(text)
        if err:
            await update.message.reply_text("⚠️ @username invalid")
            return
        context.user_data["partner"] = uname
        if dtype == "premium":
            # requested: not "Введите стоимость", but choose months
            context.user_data["step"] = "prem_period"
            await update.effective_chat.send_message(
                f"<b>{R(ru,'Выберите на сколько месяцев Premium:','Choose Premium months:')}</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=premium_period_kb(lang),
            )
            return
        context.user_data["step"] = "amount"
        await update.message.reply_text(f"<b>{R(ru,'Введите сумму сделки:','Enter deal amount:')}</b>", parse_mode=ParseMode.HTML)
        return

    if step == "amount":
        ca = text.replace(" ", "").replace(",", ".")
        try:
            v = float(ca)
            if v <= 0:
                raise ValueError
        except Exception:
            await update.message.reply_text(f"⚠️ {R(ru,'Введите число > 0','Enter number > 0')}")
            return
        context.user_data["amount"] = ca

        # currency prompt depends on creator role
        creator_role = context.user_data.get("creator_role", "seller")
        prompt = R(ru, "Выберите валюту для оплаты:", "Choose payment currency:")
        if creator_role == "seller":
            prompt = R(ru, "Выберите валюту для получения оплаты:", "Choose currency to receive payment:")
        context.user_data["step"] = "pay_currency"
        await update.effective_chat.send_message(f"<b>{prompt}</b>", parse_mode=ParseMode.HTML, reply_markup=pay_currency_kb(lang))
        return

    if step == "pay_currency":
        await update.message.reply_text(f"⚠️ {R(ru,'Выберите валюту кнопкой.','Choose currency via buttons.')}")
        return


# ──────────────────────────────────────────────────────────────────────────────
# Missing functions - add all required command handlers
# ──────────────────────────────────────────────────────────────────────────────
async def cmd_addlogtemplate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addlogtemplate <name> <template>")
        return
    
    template_name = context.args[0]
    template_text = " ".join(context.args[1:])
    
    db = load_db()
    if "log_templates" not in db:
        db["log_templates"] = {}
    
    db["log_templates"][template_name] = template_text
    save_db(db)
    
    await update.message.reply_text(f"✅ Log template '{template_name}' added")


async def cmd_listlogtemplates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    templates = db.get("log_templates", {})
    
    if not templates:
        await update.message.reply_text("No log templates found")
        return
    
    lines = ["<b>Log Templates:</b>\n"]
    for name, template in templates.items():
        lines.append(f"• {name}: {template}")
    
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def cmd_uselogtemplate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /uselogtemplate <template_name> <deal_id>")
        return
    
    template_name = context.args[0]
    deal_id = context.args[1].upper()
    
    db = load_db()
    templates = db.get("log_templates", {})
    
    if template_name not in templates:
        await update.message.reply_text(f"❌ Template '{template_name}' not found")
        return
    
    template_text = templates[template_name]
    entry = add_log(
        db, 
        template_text, 
        deal_id=deal_id, 
        uid=update.effective_user.id, 
        username=update.effective_user.username or ""
    )
    save_db(db)
    await send_log_msg(context, db, entry)
    
    await update.message.reply_text(f"✅ Applied template '{template_name}' to deal {deal_id}")


async def cmd_setdealstatus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setdealstatus <deal_id> <status>")
        return
    
    deal_id = context.args[0].upper()
    new_status = context.args[1].lower()
    
    valid_statuses = ["pending", "paid", "completed", "cancelled", "disputed"]
    if new_status not in valid_statuses:
        await update.message.reply_text(f"❌ Invalid status. Valid: {', '.join(valid_statuses)}")
        return
    
    db = load_db()
    deal = db.get("deals", {}).get(deal_id)
    
    if not deal:
        await update.message.reply_text(f"❌ Deal {deal_id} not found")
        return
    
    old_status = deal.get("status")
    deal["status"] = new_status
    deal["status_updated_at"] = datetime.now().isoformat()
    deal["status_updated_by"] = update.effective_user.id
    db["deals"][deal_id] = deal
    
    entry = add_log(
        db, 
        f"Status changed: {old_status} → {new_status}", 
        deal_id=deal_id, 
        uid=update.effective_user.id, 
        username=update.effective_user.username or ""
    )
    save_db(db)
    await send_log_msg(context, db, entry)
    
    await update.message.reply_text(f"✅ Deal {deal_id} status set to {new_status}")


async def cmd_dispute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /dispute <deal_id> <reason>")
        return
    
    deal_id = context.args[0].upper()
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
    
    db = load_db()
    deal = db.get("deals", {}).get(deal_id)
    
    if not deal:
        await update.message.reply_text(f"❌ Deal {deal_id} not found")
        return
    
    uid = update.effective_user.id
    creator_uid = int(deal.get("creator_uid"))
    buyer_uid = int(deal.get("buyer_uid"))
    
    if uid not in [creator_uid, buyer_uid]:
        await update.message.reply_text("❌ Only deal participants can open disputes")
        return
    
    deal["status"] = "disputed"
    deal["disputed_at"] = datetime.now().isoformat()
    deal["disputed_by"] = uid
    deal["dispute_reason"] = reason
    db["deals"][deal_id] = deal
    
    entry = add_log(
        db, 
        f"Dispute opened by {uid}", 
        deal_id=deal_id, 
        uid=uid, 
        username=update.effective_user.username or "",
        extra=reason
    )
    save_db(db)
    await send_log_msg(context, db, entry)
    
    await update.message.reply_text(f"✅ Dispute opened for deal {deal_id}")


async def cmd_rateuser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /rateuser <user_id> <deal_id> <rating_1-5>")
        return
    
    try:
        target_user_id = int(context.args[0])
        deal_id = context.args[1].upper()
        rating = int(context.args[2])
        
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be 1-5")
    except ValueError:
        await update.message.reply_text("❌ Invalid rating. Must be 1-5")
        return
    
    db = load_db()
    deal = db.get("deals", {}).get(deal_id)
    
    if not deal:
        await update.message.reply_text(f"❌ Deal {deal_id} not found")
        return
    
    uid = update.effective_user.id
    creator_uid = int(deal.get("creator_uid"))
    buyer_uid = int(deal.get("buyer_uid"))
    
    if uid not in [creator_uid, buyer_uid]:
        await update.message.reply_text("❌ You were not a participant in this deal")
        return
    
    if uid == target_user_id:
        await update.message.reply_text("❌ You cannot rate yourself")
        return
    
    if target_user_id not in [creator_uid, buyer_uid]:
        await update.message.reply_text("❌ Target user was not a participant in this deal")
        return
    
    target_user = get_user(db, target_user_id)
    if "ratings" not in target_user:
        target_user["ratings"] = []
    
    for existing_rating in target_user["ratings"]:
        if existing_rating.get("deal_id") == deal_id and existing_rating.get("rater_id") == uid:
            await update.message.reply_text("❌ You have already rated this user for this deal")
            return
    
    target_user["ratings"].append({
        "deal_id": deal_id,
        "rater_id": uid,
        "rating": rating,
        "rated_at": datetime.now().isoformat()
    })
    
    reputation_bonus = rating - 3
    target_user["reputation"] = target_user.get("reputation", 0) + reputation_bonus
    
    save_db(db)
    
    await update.message.reply_text(f"✅ Rated user {target_user_id} with {rating}/5 for deal {deal_id}")


async def cmd_userreviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /userreviews <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
        return
    
    db = load_db()
    user = get_user(db, user_id)
    
    reviews = user.get("reviews", [])
    ratings = user.get("ratings", [])
    
    avg_rating = 0
    if ratings:
        avg_rating = sum(r["rating"] for r in ratings) / len(ratings)
    
    text = (
        f"<b>Reviews for User {user_id}:</b>\n\n"
        f"👤 Username: @{user.get('username', 'N/A')}\n"
        f"⭐ Average Rating: {avg_rating:.1f}/5 ({len(ratings)} ratings)\n"
        f"📝 Text Reviews: {len(reviews)}\n\n"
    )
    
    if reviews:
        text += "<b>Text Reviews:</b>\n"
        for i, review in enumerate(reviews[-5:], 1):
            text += f"{i}. {review}\n"
    else:
        text += "No text reviews yet."
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_searchdeals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /searchdeals <query>")
        return
    
    query = " ".join(context.args).lower()
    db = load_db()
    deals = db.get("deals", {})
    
    matching_deals = []
    for deal_id, deal in deals.items():
        if (query in deal_id.lower() or 
            query in deal.get("type", "").lower() or 
            query in deal.get("status", "").lower()):
            matching_deals.append((deal_id, deal))
            continue
        
        if (query in str(deal.get("creator_uid", "")) or 
            query in str(deal.get("buyer_uid", ""))):
            matching_deals.append((deal_id, deal))
    
    if not matching_deals:
        await update.message.reply_text(f"No deals found matching: {query}")
        return
    
    lines = [f"<b>Deals matching '{query}':</b>\n"]
    for deal_id, deal in matching_deals[:20]:
        creator = deal.get("creator_uid", "N/A")
        buyer = deal.get("buyer_uid", "N/A")
        dtype = deal.get("type", "N/A")
        status = deal.get("status", "N/A")
        
        lines.append(f"• {deal_id}: {dtype} - {status}")
        lines.append(f"  Creator: {creator}, Buyer: {buyer}")
    
    if len(matching_deals) > 20:
        lines.append(f"\n... and {len(matching_deals) - 20} more")
    
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def cmd_exportdata(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "users_count": len(db.get("users", {})),
        "deals_count": len(db.get("deals", {})),
        "logs_count": len(db.get("logs", [])),
        "users": db.get("users", {}),
        "deals": db.get("deals", {}),
        "logs": db.get("logs", [])[-100:]
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bot_export_{timestamp}.json"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        await update.message.reply_document(
            document=open(filename, "rb"),
            caption=f"📊 Bot data export - {timestamp}"
        )
        
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Export failed: {str(e)}")


async def cmd_systemstatus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    try:
        import psutil
        import sys
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        status_text = (
            f"<b>🖥️ System Status:</b>\n\n"
            f"💻 CPU Usage: {cpu_percent}%\n"
            f"🧠 Memory: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)\n"
            f"💾 Disk: {disk.percent}% ({disk.used // 1024 // 1024}MB / {disk.total // 1024 // 1024}MB)\n"
            f"🐍 Python: {sys.version.split()[0]}\n"
            f"📅 Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        
        db = load_db()
        active_deals = len([d for d in db.get("deals", {}).values() if d.get("status") == "pending"])
        total_users = len(db.get("users", {}))
        
        status_text += (
            f"\n<b>🤖 Bot Status:</b>\n"
            f"📊 Active Deals: {active_deals}\n"
            f"👥 Total Users: {total_users}\n"
            f"📝 Logs: {len(db.get('logs', []))}\n"
        )
        
        await update.message.reply_text(status_text, parse_mode=ParseMode.HTML)
        
    except ImportError:
        await update.message.reply_text("❌ psutil not installed. Install with: pip install psutil")
    except Exception as e:
        await update.message.reply_text(f"❌ Status check failed: {str(e)}")


async def cmd_security(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    
    suspicious_users = []
    for uid_str, user in db.get("users", {}).items():
        if user.get("total_deals", 0) > 100 and user.get("success_deals", 0) == 0:
            suspicious_users.append((uid_str, user.get("username", "N/A")))
    
    text = "<b>🔒 Security Report:</b>\n\n"
    
    if suspicious_users:
        text += "<b>⚠️ Suspicious users:</b>\n"
        for uid, username in suspicious_users[:10]:
            text += f"• {uid} - @{username}\n"
    else:
        text += "✅ No suspicious activity detected\n"
    
    text += f"\n<b>🖥️ System Health:</b>\n"
    text += f"Database size: {os.path.getsize(DB_FILE) / 1024 / 1024:.1f} MB\n"
    text += f"Total users: {len(db.get('users', {}))}\n"
    text += f"Total deals: {len(db.get('deals', {}))}\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_antifraud(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /antifraud <on/off>")
        return
    
    mode = context.args[0].lower()
    if mode not in ["on", "off"]:
        await update.message.reply_text("❌ Use 'on' or 'off'")
        return
    
    db = load_db()
    db["antifraud_enabled"] = mode == "on"
    save_db(db)
    
    await update.message.reply_text(f"✅ Anti-fraud {mode}")


async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
        return
    
    db = load_db()
    user = get_user(db, user_id)
    user["banned"] = True
    save_db(db)
    
    await update.message.reply_text(f"✅ User {user_id} banned")


async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
        return
    
    db = load_db()
    user = get_user(db, user_id)
    user["banned"] = False
    save_db(db)
    
    await update.message.reply_text(f"✅ User {user_id} unbanned")


async def cmd_performance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    import time
    import psutil
    
    start_time = time.time()
    db = load_db()
    users_count = len(db.get("users", {}))
    deals_count = len(db.get("deals", {}))
    db_load_time = time.time() - start_time
    
    process = psutil.Process()
    memory_info = process.memory_info()
    
    text = (
        f"<b>⚡ Performance Metrics:</b>\n\n"
        f"🗄️ Database load time: {db_load_time:.3f}s\n"
        f"👥 Users in memory: {users_count}\n"
        f"🤝 Deals in memory: {deals_count}\n"
        f"💾 Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB\n"
        f"🖥️ CPU usage: {psutil.cpu_percent()}%\n"
    )
    
    if os.path.exists(DB_FILE):
        file_size = os.path.getsize(DB_FILE) / 1024 / 1024
        text += f"📁 Database file: {file_size:.1f} MB\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_optimize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    
    original_logs = len(db.get("logs", []))
    if len(db["logs"]) > 1000:
        db["logs"] = db["logs"][-1000:]
    
    thirty_days_ago = datetime.now().timestamp() - (30 * 24 * 3600)
    original_deals = len(db.get("deals", {}))
    
    for deal_id, deal in list(db.get("deals", {}).items()):
        if deal.get("status") in ["completed", "cancelled"]:
            try:
                created_time = datetime.fromisoformat(deal.get("created", "")).timestamp()
                if created_time < thirty_days_ago:
                    del db["deals"][deal_id]
            except:
                pass
    
    save_db(db)
    
    cleaned_logs = original_logs - len(db.get("logs", []))
    cleaned_deals = original_deals - len(db.get("deals", {}))
    
    await update.message.reply_text(
        f"✅ Database optimized:\n"
        f"📝 Logs cleaned: {cleaned_logs}\n"
        f"🤝 Deals cleaned: {cleaned_deals}"
    )


async def cmd_refstats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    users = db.get("users", {})
    
    total_referrals = 0
    total_earned = 0
    top_referrers = []
    
    for uid_str, user in users.items():
        ref_count = user.get("ref_count", 0)
        ref_earned = user.get("ref_earned", 0)
        
        if ref_count > 0:
            total_referrals += ref_count
            total_earned += ref_earned
            top_referrers.append((int(uid_str), ref_count, ref_earned, user.get("username", "N/A")))
    
    top_referrers.sort(key=lambda x: x[1], reverse=True)
    
    text = (
        f"<b>📊 Реферальная статистика:</b>\n\n"
        f"👥 Всего рефералов: {total_referrals}\n"
        f"💎 Всего выплачено: {total_earned} RUB\n\n"
        f"<b>🏆 Топ рефереров:</b>\n"
    )
    
    for i, (uid, count, earned, username) in enumerate(top_referrers[:10], 1):
        text += f"{i}. @{username} - {count} рефералов, {earned} RUB\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_setrefbonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setrefbonus <percentage> <min_amount>")
        return
    
    try:
        percentage = float(context.args[0])
        min_amount = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid numbers")
        return
    
    db = load_db()
    db["ref_bonus_percentage"] = percentage
    db["ref_min_amount"] = min_amount
    save_db(db)
    
    await update.message.reply_text(f"✅ Ref bonus set: {percentage}% (min {min_amount} RUB)")


async def cmd_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    deals = db.get("deals", {})
    users = db.get("users", {})
    
    deal_types = {}
    monthly_stats = {}
    
    for deal in deals.values():
        dtype = deal.get("type", "unknown")
        deal_types[dtype] = deal_types.get(dtype, 0) + 1
        
        created = deal.get("created", "")
        if created:
            try:
                month = created[:7]
                monthly_stats[month] = monthly_stats.get(month, 0) + 1
            except:
                pass
    
    text = "<b>📈 Аналитика сделок:</b>\n\n"
    
    text += "<b>По типам:</b>\n"
    for dtype, count in deal_types.items():
        text += f"• {dtype}: {count}\n"
    
    text += "\n<b>По месяцам:</b>\n"
    for month in sorted(monthly_stats.keys())[-6:]:
        text += f"• {month}: {monthly_stats[month]}\n"
    
    active_users = len([u for u in users.values() if u.get("total_deals", 0) > 0])
    text += f"\n<b>Активные пользователи:</b> {active_users}/{len(users)}\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /webhook <url>")
        return
    
    webhook_url = context.args[0]
    
    db = load_db()
    db["webhook_url"] = webhook_url
    db["webhook_enabled"] = True
    save_db(db)
    
    await update.message.reply_text(f"✅ Webhook set: {webhook_url}")


async def cmd_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /schedule <task> <cron>")
        return
    
    task = context.args[0]
    cron = context.args[1]
    
    db = load_db()
    if "scheduled_tasks" not in db:
        db["scheduled_tasks"] = {}
    
    db["scheduled_tasks"][task] = {
        "cron": cron,
        "enabled": True,
        "created": datetime.now().isoformat()
    }
    save_db(db)
    
    await update.message.reply_text(f"✅ Task '{task}' scheduled with cron: {cron}")


async def cmd_autobackup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /autobackup <on/off> <interval_hours>")
        return
    
    mode = context.args[0].lower()
    if mode not in ["on", "off"]:
        await update.message.reply_text("❌ Use 'on' or 'off'")
        return
    
    interval = 24
    if len(context.args) > 1:
        try:
            interval = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid interval")
            return
    
    db = load_db()
    db["autobackup_enabled"] = mode == "on"
    db["autobackup_interval"] = interval
    db["last_autobackup"] = datetime.now().isoformat()
    save_db(db)
    
    await update.message.reply_text(f"✅ Auto-backup {mode} (every {interval}h)")


async def cmd_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /maintenance <on/off>")
        return
    
    mode = context.args[0].lower()
    if mode not in ["on", "off"]:
        await update.message.reply_text("❌ Use 'on' or 'off'")
        return
    
    db = load_db()
    db["maintenance_mode"] = mode == "on"
    save_db(db)
    
    await update.message.reply_text(f"✅ Maintenance mode {mode}")


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    async def post_init(application: Application) -> None:
        await application.bot.set_my_commands([BotCommand("start", "Главное меню")])

    app.post_init = post_init

    # Basic commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CommandHandler("neptunteam", cmd_neptunteam))
    app.add_handler(CommandHandler("sendbalance", cmd_sendbalance))
    app.add_handler(CommandHandler("setdeals", cmd_setdeals))
    app.add_handler(CommandHandler("setturnover", cmd_setturnover))
    app.add_handler(CommandHandler("addrep", cmd_addrep))
    app.add_handler(CommandHandler("addreview", cmd_addreview))
    app.add_handler(CommandHandler("delreview", cmd_delreview))
    app.add_handler(CommandHandler("clearreviews", cmd_clearreviews))
    app.add_handler(CommandHandler("resetstats", cmd_resetstats))

    # Admin commands
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("setlogchat", cmd_setlogchat))
    app.add_handler(CommandHandler("togglelogs", cmd_togglelogs))
    app.add_handler(CommandHandler("dealinfo", cmd_dealinfo))
    app.add_handler(CommandHandler("userinfo", cmd_userinfo))
    app.add_handler(CommandHandler("listdeals", cmd_listdeals))
    app.add_handler(CommandHandler("backup", cmd_backup))
    app.add_handler(CommandHandler("cleanup", cmd_cleanup))
    app.add_handler(CommandHandler("confirm", cmd_confirm))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    
    # Log templates
    app.add_handler(CommandHandler("addlogtemplate", cmd_addlogtemplate))
    app.add_handler(CommandHandler("listlogtemplates", cmd_listlogtemplates))
    app.add_handler(CommandHandler("uselogtemplate", cmd_uselogtemplate))
    
    # Deal management
    app.add_handler(CommandHandler("setdealstatus", cmd_setdealstatus))
    app.add_handler(CommandHandler("dispute", cmd_dispute))
    
    # User ratings
    app.add_handler(CommandHandler("rateuser", cmd_rateuser))
    app.add_handler(CommandHandler("userreviews", cmd_userreviews))
    
    # Search and export
    app.add_handler(CommandHandler("searchdeals", cmd_searchdeals))
    app.add_handler(CommandHandler("exportdata", cmd_exportdata))
    app.add_handler(CommandHandler("systemstatus", cmd_systemstatus))
    
    # Security commands
    app.add_handler(CommandHandler("security", cmd_security))
    app.add_handler(CommandHandler("antifraud", cmd_antifraud))
    app.add_handler(CommandHandler("ban", cmd_ban))
    app.add_handler(CommandHandler("unban", cmd_unban))
    
    # Performance commands
    app.add_handler(CommandHandler("performance", cmd_performance))
    app.add_handler(CommandHandler("optimize", cmd_optimize))
    
    # Enhanced commands
    app.add_handler(CommandHandler("refstats", cmd_refstats))
    app.add_handler(CommandHandler("setrefbonus", cmd_setrefbonus))
    app.add_handler(CommandHandler("analytics", cmd_analytics))
    app.add_handler(CommandHandler("webhook", cmd_webhook))
    app.add_handler(CommandHandler("schedule", cmd_schedule))
    app.add_handler(CommandHandler("autobackup", cmd_autobackup))
    app.add_handler(CommandHandler("maintenance", cmd_maintenance))

    # Add error handler
    app.add_error_handler(error_handler)

    app.add_handler(CallbackQueryHandler(on_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_msg))

    logger.info("Bot @%s started with 2222 lines version", BOT_USERNAME)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
