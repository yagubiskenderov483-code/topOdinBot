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
DB_FILE = "db.json"


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

BTN_DEAL = tg_emoji("5258262708838472997", "🤝")
BTN_PROFILE = tg_emoji("5258262708838472998", "👤")
BTN_BALANCE = tg_emoji("5258262708838472999", "💳")
BTN_DEALS = tg_emoji("5258262708838473000", "📋")
BTN_LANG = tg_emoji("5258262708838473001", "🌍")
BTN_TOP = tg_emoji("5258262708838473002", "🏆")
BTN_REF = tg_emoji("5258262708838472997", "🤝")
BTN_REQ = tg_emoji("5258262708838473000", "📋")
BTN_BACK = tg_emoji("5258262708838473003", "◀️")
BTN_HOME = tg_emoji("5258262708838473004", "🏠")

BTN_NFT = tg_emoji("5258262708838473005", "🖼️")
BTN_USERNAME = tg_emoji("5258262708838472998", "👤")
BTN_STARS = tg_emoji("5258262708838473006", "⭐️")
BTN_CRYPTO = tg_emoji("5258262708838473007", "💎")
BTN_PREMIUM = tg_emoji("5258262708838473008", "✨")

BTN_LOG_PROMO = tg_emoji("5258262708838473008", "✨")

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
            "🤝 Автоматические сделки с NFT и подарками",
            "🛡️ Полная защита обеих сторон",
            "🔒 Средства заморожены до подтверждения",
            f"👤 Передача через менеджера: {MANAGER_TAG}",
        ]
        intro = "Gift Deals — безопасная площадка для сделок в Telegram"
        footer = "Выберите действие ниже"
    else:
        pts = [
            "🤝 Automatic NFT & gift deals",
            "🛡️ Full protection for both parties",
            "🔒 Funds frozen until confirmation",
            f"👤 Transfer via manager: {MANAGER_TAG}",
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
                InlineKeyboardButton(f"🤝 {R(ru,'Создать сделку','Create deal')}", callback_data="menu_deal"),
                InlineKeyboardButton(f"👤 {R(ru,'Профиль','Profile')}", callback_data="menu_profile"),
            ],
            [
                InlineKeyboardButton(f"💳 {R(ru,'Пополнить/Вывод','Top up/Withdraw')}", callback_data="menu_balance"),
                InlineKeyboardButton(f"📋 {R(ru,'Мои сделки','My deals')}", callback_data="menu_my_deals"),
            ],
            [
                InlineKeyboardButton(f"🌍 {R(ru,'Язык','Language')}", callback_data="menu_lang"),
                InlineKeyboardButton(f"🏆 {R(ru,'Топ','Top')}", callback_data="menu_top"),
            ],
            [
                InlineKeyboardButton(f"🤝 {R(ru,'Рефералы','Referrals')}", callback_data="menu_ref"),
                InlineKeyboardButton(f"📋 {R(ru,'Реквизиты','Requisites')}", callback_data="menu_req"),
            ],
        ]
    )


def role_kb(lang: str) -> InlineKeyboardMarkup:
    ru = lang == "ru"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"{tg_emoji('5258262708838473010', '🛒')} {R(ru,'Я покупатель','I am Buyer')}", callback_data="role_buyer")],
            [InlineKeyboardButton(f"{tg_emoji('5258262708838473011', '🏪')} {R(ru,'Я продавец','I am Seller')}", callback_data="role_seller")],
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
            [InlineKeyboardButton(f"{BTN_CRYPTO} TON", callback_data="pay_cur_TON"), InlineKeyboardButton(f"{tg_emoji('5258262708838473012', '💵')} USDT", callback_data="pay_cur_USDT")],
            [InlineKeyboardButton(f"{tg_emoji('5258262708838473013', '🇷🇺')} RUB", callback_data="pay_cur_RUB"), InlineKeyboardButton(f"{BTN_STARS} Stars", callback_data="pay_cur_Stars")],
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
        f"<b>{BTN_DEAL} {R(ru,'Гарантированная сделка','Guaranteed deal')}</b>",
        f"<b>{tg_emoji('5258262708838473014', '🆔')}</b> <code>{deal_id}</code>",
        f"<b>{tg_emoji('5258262708838473015', '📦')} {R(ru,'Тип','Type')}:</b> {deal_type_name(dtype, lang)}",
        f"{item_text}" if item_text else "",
        f"<b>{LOG_EMOJI_MONEY} {R(ru,'Сумма','Amount')}:</b> <b>{amount}</b> <b>{currency}</b>",
        "",
        f"<b>{BTN_PROFILE} {R(ru,'Создатель','Creator')}:</b> {creator_tag}",
        f"<b>{BTN_PROFILE} {R(ru,'Партнёр','Partner')}:</b> {partner_tag}",
        "",
        f"<b>{tg_emoji('5258262708838473016', '🔰')} {R(ru,'Инструкция','Instruction')}:</b>",
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
        lines.append(f"<b>{BTN_BALANCE} {R(ru,'Реквизиты','Payment details')}:</b>")
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

        lines.append(f"<b>{tg_emoji('5258262708838473017', '✅')} {R(ru,'После перевода нажмите «Я оплатил»','After payment press «I paid»')}</b>")

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
    
    # Handle referral links
    if args and args[0].startswith("ref_"):
        try:
            ref_id = int(args[0][4:])
            if ref_id != uid:
                ref_user = get_user(db, ref_id)
                ref_user["ref_count"] = ref_user.get("ref_count", 0) + 1
                save_db(db)
                await update.effective_message.reply_text(
                    f"{tg_emoji('5258262708838473017', '✅')} {R(u.get('lang', 'ru') == 'ru', 'Вы были приглашены по реферальной ссылке!', 'You were invited by a referral link!')}"
                )
        except (ValueError, KeyError):
            pass
    
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
                f"{tg_emoji('5258262708838473018', '⚠️')} <b>{R(ru,'Сначала добавьте реквизиты (обязательно).','Add requisites first (required).')}</b>",
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
                [InlineKeyboardButton(f"{tg_emoji('5258262708838473017', '✅')} {R(ru, 'Я оплатил', 'I paid')}", callback_data=f"paid_{deal_id}")],
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


# Additional admin commands
async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    logs = db.get("logs", [])[-20:]  # Last 20 logs
    
    if not logs:
        await update.message.reply_text("No logs found")
        return
    
    lines = ["<b>Recent Logs:</b>\n"]
    for log in logs:
        lines.append(f"{log.get('time', '')} - {log.get('event', '')} - {log.get('deal_id', '')}")
    
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    users_count = len(db.get("users", {}))
    deals_count = len(db.get("deals", {}))
    logs_count = len(db.get("logs", []))
    
    stats_text = (
        f"<b>Bot Statistics:</b>\n\n"
        f"👥 Users: {users_count}\n"
        f"🤝 Deals: {deals_count}\n"
        f"📝 Logs: {logs_count}\n"
        f"💾 DB size: {os.path.getsize(DB_FILE) if os.path.exists(DB_FILE) else 0} bytes"
    )
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    message = " ".join(context.args)
    db = load_db()
    users = db.get("users", {})
    
    sent = 0
    failed = 0
    
    for uid in users.keys():
        try:
            await context.bot.send_message(chat_id=int(uid), text=message)
            sent += 1
        except Exception:
            failed += 1
    
    await update.message.reply_text(
        f"Broadcast completed:\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )


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
    await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} OK")


async def cmd_resetstats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["total_deals"] = 0
    u["success_deals"] = 0
    u["turnover"] = 0
    u["reputation"] = 0
    save_db(db)
    await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} OK")


async def cmd_sendbalance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    if not context.args or not context.args[0].replace(".", "", 1).isdigit():
        await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} {R(ru,'Пример: /sendbalance 500','Example: /sendbalance 500')}")
        return
    amt = int(float(context.args[0]))
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["balance"] = int(u.get("balance", 0)) + amt
    save_db(db)
    await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} {R(ru,'Баланс пополнен','Balance topped up')}: {u['balance']} RUB")


async def cmd_setdeals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} {R(ru,'Пример: /setdeals 50','Example: /setdeals 50')}")
        return
    n = int(context.args[0])
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["total_deals"] = n
    u["success_deals"] = n
    save_db(db)
    await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} OK")


async def cmd_setturnover(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} {R(ru,'Пример: /setturnover 15000','Example: /setturnover 15000')}")
        return
    n = int(context.args[0])
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["turnover"] = n
    save_db(db)
    await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} OK")


async def cmd_addrep(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    if not context.args or not context.args[0].lstrip("-").isdigit():
        await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} {R(ru,'Пример: /addrep 100','Example: /addrep 100')}")
        return
    n = int(context.args[0])
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["reputation"] = int(u.get("reputation", 0)) + n
    save_db(db)
    await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} OK")


async def cmd_addreview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    text = " ".join(context.args or []).strip()
    if not text:
        await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} /addreview Текст")
        return
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u.setdefault("reviews", []).append(text)
    save_db(db)
    await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} OK")


async def cmd_delreview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} /delreview 1")
        return
    idx = int(context.args[0]) - 1
    db = load_db()
    u = get_user(db, update.effective_user.id)
    revs = u.get("reviews", [])
    if idx < 0 or idx >= len(revs):
        await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} Нет такого отзыва")
        return
    revs.pop(idx)
    save_db(db)
    await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} OK")


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
            await send_section(update, f"{tg_emoji('5258262708838473018', '⚠️')} <b>{R(ru,'Добавьте реквизиты (обязательно).','Add requisites (required).')}</b>", kb)
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
            await send_section(update, f"<b>Введите TON адрес</b>\n<code>UQ...</code>")
        elif field == "stars":
            await send_section(update, f"<b>Введите @username</b>\n<code>@username</code>")
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
        await send_section(update, f"{tg_emoji('5258262708838473017', '✅')} {R(ru,'Отправлено менеджеру','Sent to manager')}", InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_HOME} {R(ru,'Главное меню','Main menu')}", callback_data="main_menu")]]))
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
                    await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} {R(ru,'Введите название банка:','Enter bank name:')}\n<blockquote>{ex}</blockquote>", parse_mode=ParseMode.HTML)
                    return
                card_val = str(context.user_data.pop("card_pending", "")).strip()
                context.user_data.pop("card_step", None)
                if not card_val:
                    await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} error, try again")
                    return
                u.setdefault("requisites", {})["card"] = card_val + "|" + bank
            else:
                v = validate_card_or_phone(text, lang)
                if not v:
                    await update.message.reply_text(
                        f"{tg_emoji('5258262708838473018', '⚠️')} {R(ru,'Неверный номер. RU: +7... / 8... или карта 16 цифр. EN: +1... или +2...','Invalid. RU: +7... / 8... or 16-digit card. EN: +1... or +2...')}"
                    )
                    return
                context.user_data["card_pending"] = v
                context.user_data["card_step"] = "bank"
                ex = "HSBC, Barclays, Lloyds" if lang == "en" else "Сбербанк, ВТБ, Тинькофф"
                await update.message.reply_text(f"{tg_emoji('5258262708838473019', '🏦')} <b>{R(ru,'Введите название банка:','Enter bank name:')}</b>\n<blockquote>{ex}</blockquote>", parse_mode=ParseMode.HTML)
                return
        elif field == "ton":
            if not validate_ton_address(text):
                await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} TON address invalid")
                return
            u.setdefault("requisites", {})["ton"] = text.strip()
        elif field == "stars":
            uname, err = validate_username(text)
            if err:
                await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} @username invalid")
                return
            u.setdefault("requisites", {})["stars"] = uname
        save_db(db)
        context.user_data.pop("req_step", None)
        context.user_data.pop("card_pending", None)
        context.user_data.pop("card_step", None)

        # continue pending deal join
        pending = context.user_data.get("pending_deal")
        if pending:
            await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} OK. Откройте ссылку сделки ещё раз.")
            return

        # continue creating deal flow
        if context.user_data.get("creator_role"):
            await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} {R(ru,'Реквизиты сохранены. Теперь выберите тип сделки.','Saved. Now choose deal type.')}")
            await update.effective_chat.send_message(f"<b>{R(ru,'Выберите тип сделки:','Choose deal type:')}</b>", parse_mode=ParseMode.HTML, reply_markup=types_kb(lang))
            return

        await update.message.reply_text(f"{tg_emoji('5258262708838473017', '✅')} OK")
        return

    # deal creation steps
    step = context.user_data.get("step")
    dtype = context.user_data.get("dtype")
    if not step:
        return
    
    if dtype == "premium" and step == "prem_period":
        # This is handled by callback, just ignore text input
        await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} {R(ru,'Выберите период кнопкой','Choose period via buttons')}")
        return

    if step == "partner":
        uname, err = validate_username(text)
        if err:
            await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} @username invalid")
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
            await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} {R(ru,'Введите число > 0','Enter number > 0')}")
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
        await update.message.reply_text(f"{tg_emoji('5258262708838473018', '⚠️')} {R(ru,'Выберите валюту кнопкой.','Choose currency via buttons.')}")
        return


# ──────────────────────────────────────────────────────────────────────────────
# Additional handlers for missing functionality
# ──────────────────────────────────────────────────────────────────────────────
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    stats_text = (
        f"{BTN_PROFILE} <b>{R(ru,'Профиль','Profile')}</b>\n\n"
        f"<b>{R(ru,'ID','ID')}:</b> <code>{uid}</code>\n"
        f"<b>{R(ru,'Username','Username')}:</b> @{u.get('username', 'N/A')}\n"
        f"<b>{R(ru,'Баланс','Balance')}:</b> {u.get('balance', 0)} RUB\n"
        f"<b>{R(ru,'Всего сделок','Total deals')}:</b> {u.get('total_deals', 0)}\n"
        f"<b>{R(ru,'Успешных сделок','Successful deals')}:</b> {u.get('success_deals', 0)}\n"
        f"<b>{R(ru,'Оборот','Turnover')}:</b> {u.get('turnover', 0)} RUB\n"
        f"<b>{R(ru,'Репутация','Reputation')}:</b> {u.get('reputation', 0)}\n"
    )
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]])
    await send_section(update, stats_text, kb)


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
        text = f"{BTN_DEALS} <b>{R(ru,'Мои сделки','My deals')}</b>\n\n{R(ru,'У вас пока нет сделок','You have no deals yet')}"
    else:
        lines = [f"{BTN_DEALS} <b>{R(ru,'Мои сделки','My deals')}</b>\n\n"]
        for deal_id, deal in user_deals[:10]:  # Show last 10 deals
            status = deal.get("status", "unknown")
            dtype = deal.get("type", "")
            amount = deal.get("amount", "")
            currency = deal.get("pay_currency", "")
            lines.append(f"• <code>{deal_id}</code> - {deal_type_name(dtype, lang)} - {amount} {currency} - {status}")
        text = "\n".join(lines)
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]])
    await send_section(update, text, kb)


async def show_top_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    lang = get_lang(update.effective_user.id)
    ru = lang == "ru"
    
    # Sort users by reputation
    users_by_rep = sorted(
        [(uid, u) for uid, u in db.get("users", {}).items()],
        key=lambda x: x[1].get("reputation", 0),
        reverse=True
    )[:10]  # Top 10
    
    if not users_by_rep:
        text = f"{BTN_TOP} <b>{R(ru,'Топ пользователей','Top users')}</b>\n\n{R(ru,'Пока нет данных','No data yet')}"
    else:
        lines = [f"{BTN_TOP} <b>{R(ru,'Топ пользователей','Top users')}</b>\n\n"]
        for i, (uid, u) in enumerate(users_by_rep, 1):
            username = u.get("username", f"user_{uid}")
            rep = u.get("reputation", 0)
            deals = u.get("success_deals", 0)
            lines.append(f"{i}. @{username} - {R(ru,'Репутация','Reputation')}: {rep}, {R(ru,'Сделок','Deals')}: {deals}")
        text = "\n".join(lines)
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]])
    await send_section(update, text, kb)


async def show_balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    balance = u.get("balance", 0)
    text = (
        f"{BTN_BALANCE} <b>{R(ru,'Баланс','Balance')}</b>\n\n"
        f"{R(ru,'Текущий баланс','Current balance')}: <b>{balance} RUB</b>\n\n"
        f"{R(ru,'Для пополнения или вывода свяжитесь с менеджером','For top up or withdrawal contact manager')}: {MANAGER_TAG}"
    )
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]])
    await send_section(update, text, kb)


async def show_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    ref_count = u.get("ref_count", 0)
    ref_earned = u.get("ref_earned", 0)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"
    
    text = (
        f"{BTN_REF} <b>{R(ru,'Рефералы','Referrals')}</b>\n\n"
        f"{R(ru,'Приглашено','Invited')}: <b>{ref_count}</b>\n"
        f"{R(ru,'Заработано','Earned')}: <b>{ref_earned} RUB</b>\n\n"
        f"{R(ru,'Ваша реферальная ссылка','Your referral link')}:\n"
        f"<code>{ref_link}</code>"
    )
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]])
    await send_section(update, text, kb)


async def show_requisites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    reqs = u.get("requisites", {})
    req_text = []
    
    if reqs.get("card"):
        card_data = reqs["card"].split("|")
        if len(card_data) == 2:
            req_text.append(f"{R(ru,'Карта','Card')}: {card_data[0]} ({card_data[1]})")
        else:
            req_text.append(f"{R(ru,'Карта','Card')}: {card_data[0]}")
    
    if reqs.get("ton"):
        req_text.append(f"TON: {reqs['ton']}")
    
    if reqs.get("stars"):
        req_text.append(f"Stars: {reqs['stars']}")
    
    if not req_text:
        req_text.append(f"{R(ru,'Реквизиты не добавлены','No requisites added')}")
    
    text = (
        f"{BTN_REQ} <b>{R(ru,'Реквизиты','Requisites')}</b>\n\n"
        + "\n".join(req_text) +
        f"\n\n{R(ru,'Для изменения реквизитов выберите действие ниже','To change requisites select action below')}"
    )
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(R(ru, "Изменить карту/телефон", "Change card/phone"), callback_data="req_edit_card")],
        [InlineKeyboardButton("Изменить TON", callback_data="req_edit_ton")],
        [InlineKeyboardButton(R(ru, "Изменить @username (Stars)", "Change @username (Stars)"), callback_data="req_edit_stars")],
        [InlineKeyboardButton(f"{BTN_BACK} {R(ru,'Назад','Back')}", callback_data="main_menu")]
    ])
    await send_section(update, text, kb)


# Update callback handler to include new menu items
async def on_cb_extended(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    # Handle all other callbacks with original function
    await on_cb_original(update, context)


# Keep original on_cb as on_cb_original
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
            await send_section(update, f"{tg_emoji('5258262708838473018', '⚠️')} <b>{R(ru,'Добавьте реквизиты (обязательно).','Add requisites (required).')}</b>", kb)
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
            await send_section(update, f"<b>Введите TON адрес</b>\n<code>UQ...</code>")
        elif field == "stars":
            await send_section(update, f"<b>Введите @username</b>\n<code>@username</code>")
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
        await send_section(update, f"{tg_emoji('5258262708838473017', '✅')} {R(ru,'Отправлено менеджеру','Sent to manager')}", InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_HOME} {R(ru,'Главное меню','Main menu')}", callback_data="main_menu")]]))
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
    card_text += f"\n\n<b>{tg_emoji('5258262708838473020', '🔗')} {R(ru,'Ссылка для партнёра','Link for partner')}:</b>\n<code>{link}</code>"

    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{BTN_HOME} {R(ru,'Главное меню','Main menu')}", callback_data="main_menu")]])
    await update.effective_chat.send_message(card_text, parse_mode=ParseMode.HTML, reply_markup=kb)

    context.user_data.clear()


# ──────────────────────────────────────────────────────────────────────────────
# Deal management functions
# ──────────────────────────────────────────────────────────────────────────────
async def show_deal_details(update: Update, context: ContextTypes.DEFAULT_TYPE, deal_id: str) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    deal = db.get("deals", {}).get(deal_id)
    if not deal:
        await update.message.reply_text(R(ru, "Сделка не найдена", "Deal not found"))
        return
    
    # Check if user is participant
    if str(deal.get("creator_uid")) != str(uid) and str(deal.get("buyer_uid")) != str(uid):
        await update.message.reply_text(R(ru, "Доступ запрещен", "Access denied"))
        return
    
    text = build_deal_card_text(db, deal_id, lang, for_creator=(str(deal.get("creator_uid")) == str(uid)))
    
    # Add action buttons based on status
    buttons = []
    if deal.get("status") == "pending":
        if str(deal.get("buyer_uid")) == str(uid):
            buttons.append([InlineKeyboardButton(f"✅ {R(ru,'Я оплатил','I paid')}", callback_data=f"paid_{deal_id}")])
        elif str(deal.get("creator_uid")) == str(uid):
            buttons.append([InlineKeyboardButton(f"🚫 {R(ru,'Отменить сделку','Cancel deal')}", callback_data=f"cancel_{deal_id}")])
    
    buttons.append([InlineKeyboardButton(f"🏠 {R(ru,'Главное меню','Main menu')}", callback_data="main_menu")])
    
    kb = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)


async def cancel_deal(update: Update, context: ContextTypes.DEFAULT_TYPE, deal_id: str) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    deal = db.get("deals", {}).get(deal_id)
    if not deal:
        await update.message.reply_text(R(ru, "Сделка не найдена", "Deal not found"))
        return
    
    # Only creator can cancel
    if str(deal.get("creator_uid")) != str(uid):
        await update.message.reply_text(R(ru, "Только создатель может отменить", "Only creator can cancel"))
        return
    
    # Update deal status
    deal["status"] = "cancelled"
    deal["cancelled_at"] = datetime.now().isoformat()
    db["deals"][deal_id] = deal
    
    # Add log
    entry = add_log(db, "Сделка отменена", deal_id=deal_id, uid=uid, username=u.get("username", ""))
    save_db(db)
    await send_log_msg(context, db, entry)
    
    # Notify buyer if exists
    buyer_uid = deal.get("buyer_uid")
    if buyer_uid:
        try:
            await context.bot.send_message(
                chat_id=int(buyer_uid),
                text=f"❌ {R(ru,'Сделка','Deal')} {deal_id} {R(ru,'была отменена создателем','was cancelled by creator')}"
            )
        except Exception:
            logger.exception("Failed to notify buyer about cancellation")
    
    await update.message.reply_text(f"✅ {R(ru,'Сделка отменена','Deal cancelled')}")


async def confirm_deal(update: Update, context: ContextTypes.DEFAULT_TYPE, deal_id: str) -> None:
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    ru = lang == "ru"
    
    # Only admin can confirm
    if uid not in ADMIN_IDS:
        await update.message.reply_text(R(ru, "Доступ запрещен", "Access denied"))
        return
    
    deal = db.get("deals", {}).get(deal_id)
    if not deal:
        await update.message.reply_text(R(ru, "Сделка не найдена", "Deal not found"))
        return
    
    # Update deal status
    deal["status"] = "completed"
    deal["completed_at"] = datetime.now().isoformat()
    db["deals"][deal_id] = deal
    
    # Update user stats
    creator_uid = int(deal.get("creator_uid"))
    buyer_uid = int(deal.get("buyer_uid"))
    
    for participant_uid in [creator_uid, buyer_uid]:
        participant = get_user(db, participant_uid)
        participant["total_deals"] = participant.get("total_deals", 0) + 1
        participant["success_deals"] = participant.get("success_deals", 0) + 1
        participant["reputation"] = participant.get("reputation", 0) + 1
        
        # Add turnover
        amount = float(deal.get("amount", 0))
        participant["turnover"] = participant.get("turnover", 0) + int(amount)
    
    # Add log
    entry = add_log(db, "Сделка завершена", deal_id=deal_id, uid=uid, username=u.get("username", ""))
    save_db(db)
    await send_log_msg(context, db, entry)
    
    # Notify participants
    for participant_uid in [creator_uid, buyer_uid]:
        try:
            await context.bot.send_message(
                chat_id=participant_uid,
                text=f"✅ {R(ru,'Сделка','Deal')} {deal_id} {R(ru,'успешно завершена','successfully completed')}"
            )
        except Exception:
            logger.exception(f"Failed to notify user {participant_uid} about deal completion")
    
    await update.message.reply_text(f"✅ {R(ru,'Сделка подтверждена и завершена','Deal confirmed and completed')}")


# ──────────────────────────────────────────────────────────────────────────────
# Admin functions
# ──────────────────────────────────────────────────────────────────────────────
async def cmd_setlogchat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /setlogchat <chat_id>")
        return
    
    try:
        chat_id = int(context.args[0])
        db = load_db()
        db["log_chat_id"] = chat_id
        save_db(db)
        await update.message.reply_text(f"✅ Log chat set to {chat_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid chat ID")


async def cmd_togglelogs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    current = db.get("log_hidden", False)
    db["log_hidden"] = not current
    save_db(db)
    
    status = "hidden" if not current else "visible"
    await update.message.reply_text(f"✅ Logs are now {status}")


async def cmd_dealinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /dealinfo <deal_id>")
        return
    
    deal_id = context.args[0].upper()
    db = load_db()
    deal = db.get("deals", {}).get(deal_id)
    
    if not deal:
        await update.message.reply_text(f"❌ Deal {deal_id} not found")
        return
    
    info = (
        f"<b>Deal Info: {deal_id}</b>\n\n"
        f"👤 Creator: {deal.get('creator_uid')}\n"
        f"👤 Buyer: {deal.get('buyer_uid', 'N/A')}\n"
        f"📦 Type: {deal.get('type')}\n"
        f"💰 Amount: {deal.get('amount')} {deal.get('pay_currency')}\n"
        f"📊 Status: {deal.get('status')}\n"
        f"📅 Created: {deal.get('created')}\n"
    )
    
    if deal.get("completed_at"):
        info += f"✅ Completed: {deal.get('completed_at')}\n"
    elif deal.get("cancelled_at"):
        info += f"🚫 Cancelled: {deal.get('cancelled_at')}\n"
    
    await update.message.reply_text(info, parse_mode=ParseMode.HTML)


async def cmd_userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /userinfo <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
        db = load_db()
        user = get_user(db, user_id)
        
        info = (
            f"<b>User Info: {user_id}</b>\n\n"
            f"👤 Username: @{user.get('username', 'N/A')}\n"
            f"🌍 Lang: {user.get('lang', 'ru')}\n"
            f"💳 Balance: {user.get('balance', 0)} RUB\n"
            f"🤝 Total Deals: {user.get('total_deals', 0)}\n"
            f"✅ Successful Deals: {user.get('success_deals', 0)}\n"
            f"💰 Turnover: {user.get('turnover', 0)} RUB\n"
            f"⭐ Reputation: {user.get('reputation', 0)}\n"
            f"👥 Referrals: {user.get('ref_count', 0)}\n"
            f"💵 Ref Earnings: {user.get('ref_earned', 0)} RUB\n"
            f"📝 Reviews: {len(user.get('reviews', []))}\n"
        )
        
        if user.get("requisites"):
            reqs = user["requisites"]
            info += f"\n📋 Requisites:\n"
            if reqs.get("card"):
                info += f"  💳 Card: {reqs['card']}\n"
            if reqs.get("ton"):
                info += f"  💎 TON: {reqs['ton']}\n"
            if reqs.get("stars"):
                info += f"  ⭐ Stars: {reqs['stars']}\n"
        
        await update.message.reply_text(info, parse_mode=ParseMode.HTML)
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")


async def cmd_listdeals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    deals = db.get("deals", {})
    
    if not deals:
        await update.message.reply_text("No deals found")
        return
    
    # Filter by status if provided
    status_filter = None
    if context.args:
        status_filter = context.args[0].lower()
    
    lines = ["<b>Deals List:</b>\n"]
    count = 0
    
    for deal_id, deal in deals.items():
        status = deal.get("status", "unknown")
        if status_filter and status != status_filter:
            continue
        
        count += 1
        creator = deal.get("creator_uid", "N/A")
        buyer = deal.get("buyer_uid", "N/A")
        dtype = deal.get("type", "N/A")
        amount = deal.get("amount", "0")
        currency = deal.get("pay_currency", "N/A")
        
        lines.append(f"• {deal_id}: {dtype} - {amount} {currency} - {status}")
        lines.append(f"  Creator: {creator}, Buyer: {buyer}")
    
    if count == 0:
        lines.append(f"No deals found with status: {status_filter or 'all'}")
    else:
        lines.append(f"\nTotal: {count} deals")
    
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def cmd_backup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    try:
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"db_backup_{timestamp}.json"
        shutil.copy2(DB_FILE, backup_file)
        
        await update.message.reply_text(f"✅ Database backed up to {backup_file}")
    except Exception as e:
        await update.message.reply_text(f"❌ Backup failed: {str(e)}")


async def cmd_cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = load_db()
    original_users = len(db.get("users", {}))
    original_deals = len(db.get("deals", {}))
    
    # Clean up old completed/cancelled deals (older than 30 days)
    from datetime import datetime, timedelta
    cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
    
    cleaned_deals = 0
    for deal_id, deal in list(db.get("deals", {}).items()):
        status = deal.get("status")
        if status in ["completed", "cancelled"]:
            completed_at = deal.get("completed_at") or deal.get("cancelled_at")
            if completed_at and completed_at < cutoff_date:
                del db["deals"][deal_id]
                cleaned_deals += 1
    
    # Clean up inactive users (no activity in 90 days)
    cleaned_users = 0
    user_cutoff = (datetime.now() - timedelta(days=90)).isoformat()
    
    for user_id, user in list(db.get("users", {}).items()):
        # Keep users with deals or balance
        if (user.get("total_deals", 0) > 0 or 
            user.get("balance", 0) > 0 or 
            user.get("ref_count", 0) > 0):
            continue
        
        del db["users"][user_id]
        cleaned_users += 1
    
    save_db(db)
    
    message = (
        f"✅ Cleanup completed:\n"
        f"🗑️ Removed {cleaned_deals} old deals\n"
        f"👤 Removed {cleaned_users} inactive users\n"
        f"📊 Users: {original_users} → {len(db.get('users', {}))}\n"
        f"🤝 Deals: {original_deals} → {len(db.get('deals', {}))}"
    )
    
    await update.message.reply_text(message)


# ──────────────────────────────────────────────────────────────────────────────
# Notification system
# ──────────────────────────────────────────────────────────────────────────────
async def send_notification_to_user(context: ContextTypes.DEFAULT_TYPE, user_id: int, message: str) -> bool:
    """Send notification to specific user"""
    try:
        await context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
        return True
    except Exception as e:
        logger.exception(f"Failed to send notification to user {user_id}: {e}")
        return False


async def notify_all_admins(context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
    """Send notification to all admins"""
    for admin_id in ADMIN_IDS:
        await send_notification_to_user(context, admin_id, f"🔔 Admin Notification:\n\n{message}")


async def notify_deal_participants(context: ContextTypes.DEFAULT_TYPE, deal_id: str, message: str) -> None:
    """Send notification to all deal participants"""
    db = load_db()
    deal = db.get("deals", {}).get(deal_id)
    if not deal:
        return
    
    participants = [deal.get("creator_uid"), deal.get("buyer_uid")]
    for participant_id in participants:
        if participant_id:
            await send_notification_to_user(
                context, 
                int(participant_id), 
                f"🤝 Deal {deal_id} Update:\n\n{message}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# Log templates system
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


# ──────────────────────────────────────────────────────────────────────────────
# Deal status management
# ──────────────────────────────────────────────────────────────────────────────
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
    
    # Add log entry
    entry = add_log(
        db, 
        f"Status changed: {old_status} → {new_status}", 
        deal_id=deal_id, 
        uid=update.effective_user.id, 
        username=update.effective_user.username or ""
    )
    save_db(db)
    await send_log_msg(context, db, entry)
    
    # Notify participants
    await notify_deal_participants(
        context, 
        deal_id, 
        f"Deal status changed to: {new_status}"
    )
    
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
    
    # Only participants can dispute
    if uid not in [creator_uid, buyer_uid]:
        await update.message.reply_text("❌ Only deal participants can open disputes")
        return
    
    # Update deal status
    deal["status"] = "disputed"
    deal["disputed_at"] = datetime.now().isoformat()
    deal["disputed_by"] = uid
    deal["dispute_reason"] = reason
    db["deals"][deal_id] = deal
    
    # Add log entry
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
    
    # Notify admins
    await notify_all_admins(
        context, 
        f"🚨 New dispute in deal {deal_id}\n"
        f"By: {update.effective_user.username or uid}\n"
        f"Reason: {reason}"
    )
    
    # Notify other participant
    other_participant = buyer_uid if uid == creator_uid else creator_uid
    await send_notification_to_user(
        context,
        other_participant,
        f"⚠️ Dispute opened in deal {deal_id}\n"
        f"Reason: {reason}"
    )
    
    await update.message.reply_text(f"✅ Dispute opened for deal {deal_id}")


# ──────────────────────────────────────────────────────────────────────────────
# User rating and review system
# ──────────────────────────────────────────────────────────────────────────────
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
    
    # Check if user was participant in this deal
    if uid not in [creator_uid, buyer_uid]:
        await update.message.reply_text("❌ You were not a participant in this deal")
        return
    
    # Can't rate yourself
    if uid == target_user_id:
        await update.message.reply_text("❌ You cannot rate yourself")
        return
    
    # Check if target user was participant
    if target_user_id not in [creator_uid, buyer_uid]:
        await update.message.reply_text("❌ Target user was not a participant in this deal")
        return
    
    # Add rating
    target_user = get_user(db, target_user_id)
    if "ratings" not in target_user:
        target_user["ratings"] = []
    
    # Check if already rated
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
    
    # Update reputation based on rating
    reputation_bonus = rating - 3  # 3 is neutral
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
    
    # Calculate average rating
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
        for i, review in enumerate(reviews[-5:], 1):  # Show last 5
            text += f"{i}. {review}\n"
    else:
        text += "No text reviews yet."
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


# ──────────────────────────────────────────────────────────────────────────────
# Advanced search and filtering
# ──────────────────────────────────────────────────────────────────────────────
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
        # Search in deal ID, type, status
        if (query in deal_id.lower() or 
            query in deal.get("type", "").lower() or 
            query in deal.get("status", "").lower()):
            matching_deals.append((deal_id, deal))
            continue
        
        # Search in participant IDs
        if (query in str(deal.get("creator_uid", "")) or 
            query in str(deal.get("buyer_uid", ""))):
            matching_deals.append((deal_id, deal))
    
    if not matching_deals:
        await update.message.reply_text(f"No deals found matching: {query}")
        return
    
    lines = [f"<b>Deals matching '{query}':</b>\n"]
    for deal_id, deal in matching_deals[:20]:  # Limit to 20 results
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
    
    # Create export data
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "users_count": len(db.get("users", {})),
        "deals_count": len(db.get("deals", {})),
        "logs_count": len(db.get("logs", [])),
        "users": db.get("users", {}),
        "deals": db.get("deals", {}),
        "logs": db.get("logs", [])[-100:]  # Last 100 logs
    }
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bot_export_{timestamp}.json"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        await update.message.reply_document(
            document=open(filename, "rb"),
            caption=f"📊 Bot data export - {timestamp}"
        )
        
        # Clean up file
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Export failed: {str(e)}")


async def cmd_systemstatus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    try:
        import psutil
        import sys
        
        # System info
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
        
        # Bot status
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
    app.add_handler(CommandHandler("addlogtemplate", cmd_addlogtemplate))
    app.add_handler(CommandHandler("listlogtemplates", cmd_listlogtemplates))
    app.add_handler(CommandHandler("uselogtemplate", cmd_uselogtemplate))
    app.add_handler(CommandHandler("setdealstatus", cmd_setdealstatus))
    app.add_handler(CommandHandler("dispute", cmd_dispute))
    app.add_handler(CommandHandler("rateuser", cmd_rateuser))
    app.add_handler(CommandHandler("userreviews", cmd_userreviews))
    app.add_handler(CommandHandler("searchdeals", cmd_searchdeals))
    app.add_handler(CommandHandler("exportdata", cmd_exportdata))
    app.add_handler(CommandHandler("systemstatus", cmd_systemstatus))

    app.add_handler(CallbackQueryHandler(on_cb_extended))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_msg))

    logger.info("Bot @%s started", BOT_USERNAME)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
