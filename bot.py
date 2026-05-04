mport json
import logging
import os
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
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    logger.warning("BOT_TOKEN is empty. Set BOT_TOKEN env var before запуск.")

BOT_USERNAME = os.getenv("BOT_USERNAME", "GiftDeals_Robot").strip("@")

MANAGER_URL = os.getenv("MANAGER_URL", "https://t.me/GiftDealsManager")
MANAGER_TAG = os.getenv("MANAGER_TAG", "@GiftDealsManager")

ADMIN_ID = int(os.getenv("ADMIN_ID", "8726084830"))
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "8726084830,90283607").split(",") if x.strip().isdigit()}

# Payment details (примерные — меняйте через env)
CRYPTO_ADDR = os.getenv("CRYPTO_ADDR", "UQDGN5pfjPxorFyjN2xha84bapuADDtPcRofNDJ4dK2YXxZd")
CRYPTO_BOT = os.getenv("CRYPTO_BOT", "https://t.me/send?start=IVbfPL7Tk4XA")
CARD_NUM = os.getenv("CARD_NUM", "+79041751408")
CARD_NAME = os.getenv("CARD_NAME", "Александр Ф.")
CARD_BANK_RU = os.getenv("CARD_BANK_RU", "ВТБ")
CARD_BANK_EN = os.getenv("CARD_BANK_EN", "VTB")


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
                    f"{BTN_LOG_PROMO} {('Хочешь такие профиты? Тебе к нам!' )}",
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
# Handlers
# ──────────────────────────────────────────────────────────────────────────────
async def show_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["username"] = update.effective_user.username or ""
    save_db(db)
    lang = u.get("lang", "ru")
    await send_section(update, get_welcome(lang), main_kb(lang))


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
        # handled above; but keep
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
        entry = add_log(db, "Оплачено", deal_id=deal_id, uid=uid, username=update.effective_user.username or "")
        save_db(db)
        await send_log_msg(context, db, entry)
        await send_section(update, f"✅ {R(ru,'Отправлено менеджеру','Sent to manager')}", InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_HOME} {R(ru,'Главное меню','Main menu')}", callback_data="main_menu")]]))
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


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    async def post_init(application: Application) -> None:
        await application.bot.set_my_commands([BotCommand("start", "Главное меню")])

    app.post_init = post_init

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

    app.add_handler(CallbackQueryHandler(on_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_msg))

    logger.info("Bot @%s started", BOT_USERNAME)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
