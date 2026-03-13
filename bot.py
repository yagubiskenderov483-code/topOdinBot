import logging
import re
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== CONFIG =====================
BOT_TOKEN = "8636524725:AAHY7j6yHm5fo3H2uLFs9GzZbBQsPj5fLeY"
ADMIN_ID = 174415647
BOT_USERNAME = "GiftDealsRoBot"
MANAGER_USERNAME = "@GiftDealsManager"
SUPPORT_USERNAME = "@GiftDealsSupport"
CRYPTO_ADDRESS = "UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc"
CRYPTO_BOT_LINK = "https://t.me/send?start=IVtoVqCXSHV0"

DB_FILE = "db.json"

# ===================== DATABASE =====================
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "users": {},
        "deals": {},
        "banner": None,
        "banner_photo": None,
        "menu_description": None,
        "deal_counter": 1
    }

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(db, user_id):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "username": "",
            "balance": 0,
            "total_deals": 0,
            "success_deals": 0,
            "turnover": 0,
            "reputation": 0,
            "reviews": [],
            "status": "",
            "lang": "ru"
        }
    return db["users"][uid]

# ===================== LANGUAGES =====================
LANGS = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "kz": "🇰🇿 Казахский",
    "az": "🇦🇿 Азербайджанский",
    "uz": "🇺🇿 Узбекский",
    "kg": "🇰🇬 Кыргызский",
    "tj": "🇹🇯 Таджикский",
    "by": "🇧🇾 Белорусский",
}

TRANSLATIONS = {
    "ru": {
        "welcome_title": "💎 Gift Deals",
        "welcome_text": (
            "Gift Deals — одна из самых безопасных площадок в Telegram для проведения сделок.\n\n"
            "Мы гарантируем честность каждой транзакции: средства и товар передаются только после подтверждения обеих сторон. "
            "Никаких рисков, никаких мошенников — только надёжные сделки под защитой нашей платформы.\n\n"
            "Тысячи успешных сделок уже позади — и каждая из них прошла безопасно."
        ),
        "btn_deal": "✏️ Создать сделку",
        "btn_support": "🆘 Поддержка",
        "btn_balance": "➕ Пополнить баланс",
        "btn_lang": "🔄 Сменить язык",
        "btn_profile": "👤 Профиль",
        "btn_top": "🏆 Топ продавцов",
    },
    "en": {
        "welcome_title": "💎 Gift Deals",
        "welcome_text": (
            "Gift Deals is one of the safest platforms in Telegram for conducting deals.\n\n"
            "We guarantee the honesty of every transaction: funds and goods are transferred only after confirmation from both parties. "
            "No risks, no fraudsters — only reliable deals under the protection of our platform."
        ),
        "btn_deal": "✏️ Create Deal",
        "btn_support": "🆘 Support",
        "btn_balance": "➕ Top Up Balance",
        "btn_lang": "🔄 Change Language",
        "btn_profile": "👤 Profile",
        "btn_top": "🏆 Top Sellers",
    },
    "kz": {
        "welcome_title": "💎 Gift Deals",
        "welcome_text": "Gift Deals — Telegram-дағы мәмілелер жүргізу үшін ең қауіпсіз алаңдардың бірі.",
        "btn_deal": "✏️ Мәміле жасау",
        "btn_support": "🆘 Қолдау",
        "btn_balance": "➕ Балансты толтыру",
        "btn_lang": "🔄 Тілді өзгерту",
        "btn_profile": "👤 Профиль",
        "btn_top": "🏆 Үздік сатушылар",
    },
    "az": {
        "welcome_title": "💎 Gift Deals",
        "welcome_text": "Gift Deals — Telegram-da əməliyyatlar aparmaq üçün ən təhlükəsiz platformalardan biridir.",
        "btn_deal": "✏️ Müqavilə yarat",
        "btn_support": "🆘 Dəstək",
        "btn_balance": "➕ Balansı artır",
        "btn_lang": "🔄 Dili dəyiş",
        "btn_profile": "👤 Profil",
        "btn_top": "🏆 Top satıcılar",
    },
    "uz": {
        "welcome_title": "💎 Gift Deals",
        "welcome_text": "Gift Deals — Telegram'da bitimlar o'tkazish uchun eng xavfsiz platformalardan biri.",
        "btn_deal": "✏️ Bitim yaratish",
        "btn_support": "🆘 Qo'llab-quvvatlash",
        "btn_balance": "➕ Balansni to'ldirish",
        "btn_lang": "🔄 Tilni o'zgartirish",
        "btn_profile": "👤 Profil",
        "btn_top": "🏆 Top sotuvchilar",
    },
    "kg": {
        "welcome_title": "💎 Gift Deals",
        "welcome_text": "Gift Deals — Telegram'дагы бүтүмдөр үчүн эң коопсуз аянтча.",
        "btn_deal": "✏️ Бүтүм түзүү",
        "btn_support": "🆘 Колдоо",
        "btn_balance": "➕ Баланс толтуруу",
        "btn_lang": "🔄 Тилди өзгөртүү",
        "btn_profile": "👤 Профиль",
        "btn_top": "🏆 Топ сатуучулар",
    },
    "tj": {
        "welcome_title": "💎 Gift Deals",
        "welcome_text": "Gift Deals — яке аз бехтарин майдончаҳо дар Telegram барои анҷом додани муомилот.",
        "btn_deal": "✏️ Эҷоди муомила",
        "btn_support": "🆘 Дастгирӣ",
        "btn_balance": "➕ Пур кардани баланс",
        "btn_lang": "🔄 Тағйири забон",
        "btn_profile": "👤 Профил",
        "btn_top": "🏆 Беҳтарин фурӯшандагон",
    },
    "by": {
        "welcome_title": "💎 Gift Deals",
        "welcome_text": "Gift Deals — адна з самых бяспечных пляцовак у Telegram для правядзення здзелак.",
        "btn_deal": "✏️ Стварыць здзелку",
        "btn_support": "🆘 Падтрымка",
        "btn_balance": "➕ Папоўніць баланс",
        "btn_lang": "🔄 Змяніць мову",
        "btn_profile": "👤 Профіль",
        "btn_top": "🏆 Топ прадаўцоў",
    },
}

def t(lang, key):
    return TRANSLATIONS.get(lang, TRANSLATIONS["ru"]).get(key, TRANSLATIONS["ru"].get(key, key))

# ===================== CURRENCY KEYBOARD =====================
def currency_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 TON", callback_data="cur_ton"),
         InlineKeyboardButton("💵 USDT", callback_data="cur_usdt")],
        [InlineKeyboardButton("💴 RUB", callback_data="cur_rub"),
         InlineKeyboardButton("⭐️ Stars", callback_data="cur_stars")],
        [InlineKeyboardButton("🇰🇿 KZT (Тенге)", callback_data="cur_kzt"),
         InlineKeyboardButton("🇦🇿 AZN (Манат)", callback_data="cur_azn")],
        [InlineKeyboardButton("🇰🇬 KGS (Сом)", callback_data="cur_kgs"),
         InlineKeyboardButton("🇺🇿 UZS (Сум)", callback_data="cur_uzs")],
        [InlineKeyboardButton("🇹🇯 TJS (Сомони)", callback_data="cur_tjs"),
         InlineKeyboardButton("🇧🇾 BYN (Рубль)", callback_data="cur_byn")],
        [InlineKeyboardButton("🇺🇦 UAH (Гривна)", callback_data="cur_uah"),
         InlineKeyboardButton("🇬🇪 GEL (Лари)", callback_data="cur_gel")],
    ])

CURRENCY_MAP = {
    "cur_ton": "TON", "cur_usdt": "USDT", "cur_rub": "RUB", "cur_stars": "Stars",
    "cur_kzt": "KZT", "cur_azn": "AZN", "cur_kgs": "KGS", "cur_uzs": "UZS",
    "cur_tjs": "TJS", "cur_byn": "BYN", "cur_uah": "UAH", "cur_gel": "GEL",
}

# ===================== STATES =====================
(
    DEAL_TYPE,
    DEAL_NFT_PARTNER, DEAL_NFT_LINK, DEAL_NFT_CURRENCY, DEAL_NFT_AMOUNT,
    DEAL_USERNAME_PARTNER, DEAL_USERNAME_INPUT, DEAL_USERNAME_CURRENCY, DEAL_USERNAME_AMOUNT,
    DEAL_STARS_PARTNER, DEAL_STARS_COUNT, DEAL_STARS_CURRENCY, DEAL_STARS_AMOUNT,
    DEAL_CRYPTO_CURRENCY, DEAL_CRYPTO_AMOUNT,
    DEAL_PREMIUM_PARTNER, DEAL_PREMIUM_PERIOD, DEAL_PREMIUM_CURRENCY, DEAL_PREMIUM_AMOUNT,
    DEAL_GIFTBOX_PARTNER, DEAL_GIFTBOX_LINK, DEAL_GIFTBOX_CURRENCY, DEAL_GIFTBOX_AMOUNT,
    ADMIN_ACTION, ADMIN_SET_USER, ADMIN_SET_VALUE,
    BANNER_SET, MENU_DESC_SET,
) = range(28)

# ===================== HELPERS =====================
def gen_deal_id(db):
    did = db.get("deal_counter", 1)
    db["deal_counter"] = did + 1
    save_db(db)
    return f"GD{did:05d}"

def validate_nft_link(link: str) -> bool:
    return link.startswith("https://")

def main_menu_keyboard(lang="ru"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "btn_deal"), callback_data="menu_deal")],
        [
            InlineKeyboardButton(t(lang, "btn_support"), url="https://t.me/GiftDealsSupport"),
            InlineKeyboardButton(t(lang, "btn_balance"), callback_data="menu_balance"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_lang"), callback_data="menu_lang"),
            InlineKeyboardButton(t(lang, "btn_profile"), callback_data="menu_profile"),
        ],
        [InlineKeyboardButton(t(lang, "btn_top"), callback_data="menu_top")],
    ])

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    db = load_db()
    uid = update.effective_user.id
    user = get_user(db, uid)
    lang = user.get("lang", "ru")

    banner = db.get("banner")
    banner_photo = db.get("banner_photo")
    menu_desc = db.get("menu_description")

    title = f"<b>{t(lang, 'welcome_title')}</b>"
    desc = f"<b>{menu_desc if menu_desc else t(lang, 'welcome_text')}</b>"
    text = f"{title}\n\n{desc}"
    if banner:
        text = f"{text}\n\n<b>{banner}</b>"

    kb = main_menu_keyboard(lang)

    if banner_photo:
        if edit:
            try:
                await update.effective_message.reply_photo(photo=banner_photo, caption=text, parse_mode="HTML", reply_markup=kb)
            except Exception:
                await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)
        else:
            await update.effective_message.reply_photo(photo=banner_photo, caption=text, parse_mode="HTML", reply_markup=kb)
    elif edit:
        try:
            await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)

# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user = update.effective_user
    u = get_user(db, user.id)
    u["username"] = user.username or ""
    save_db(db)
    context.user_data.clear()
    await send_main_menu(update, context)

# ===================== CALLBACK ROUTER =====================
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "main_menu":
        context.user_data.clear()
        await send_main_menu(update, context, edit=True)
        return ConversationHandler.END

    if data == "menu_balance":
        await show_balance_menu(update, context)
        return

    if data == "menu_lang":
        await show_lang_menu(update, context)
        return

    if data == "menu_profile":
        await show_profile(update, context)
        return

    if data == "menu_top":
        await show_top_sellers(update, context)
        return

    if data.startswith("lang_"):
        await set_language(update, context, data[5:])
        return

    if data.startswith("balance_"):
        await show_balance_info(update, context, data[8:])
        return

    if data == "withdraw":
        await withdraw_handler(update, context)
        return

# ===================== DEAL FLOW =====================
async def show_deal_types(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 НФТ", callback_data="deal_nft"),
         InlineKeyboardButton("👤 НФТ Юзернейм", callback_data="deal_username")],
        [InlineKeyboardButton("⭐️ Звёзды", callback_data="deal_stars"),
         InlineKeyboardButton("💎 Крипта (TON/$)", callback_data="deal_crypto")],
        [InlineKeyboardButton("🎁 НФТ Подарок", callback_data="deal_giftbox"),
         InlineKeyboardButton("✈️ Telegram Premium", callback_data="deal_premium")],
        [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
    ])
    text = "<b>✏️ Создать сделку\n\nВыберите тип товара:</b>"
    try:
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)
    return DEAL_TYPE

async def deal_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "main_menu":
        context.user_data.clear()
        await send_main_menu(update, context, edit=True)
        return ConversationHandler.END

    if data == "back_to_types":
        await show_deal_types(update, context)
        return DEAL_TYPE

    if data == "deal_nft":
        context.user_data["deal_type"] = "nft"
        await q.edit_message_text(
            "<b>🖼 НФТ Сделка\n\nШаг 1 из 4 — Введите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back_to_types")]]))
        return DEAL_NFT_PARTNER

    if data == "deal_username":
        context.user_data["deal_type"] = "username"
        await q.edit_message_text(
            "<b>👤 НФТ Юзернейм\n\nШаг 1 из 4 — Введите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back_to_types")]]))
        return DEAL_USERNAME_PARTNER

    if data == "deal_stars":
        context.user_data["deal_type"] = "stars"
        await q.edit_message_text(
            "<b>⭐️ Звёзды\n\nШаг 1 из 4 — Введите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back_to_types")]]))
        return DEAL_STARS_PARTNER

    if data == "deal_crypto":
        context.user_data["deal_type"] = "crypto"
        await q.edit_message_text(
            "<b>💎 Крипта (TON/$)\n\nШаг 1 из 2 — Выберите валюту:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 TON", callback_data="crypto_ton"),
                 InlineKeyboardButton("💵 USDT", callback_data="crypto_usdt")],
                [InlineKeyboardButton("◀️ Назад", callback_data="back_to_types")]
            ]))
        return DEAL_CRYPTO_CURRENCY

    if data == "deal_giftbox":
        context.user_data["deal_type"] = "giftbox"
        await q.edit_message_text(
            "<b>🎁 НФТ Подарок\n\nШаг 1 из 4 — Введите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back_to_types")]]))
        return DEAL_GIFTBOX_PARTNER

    if data == "deal_premium":
        context.user_data["deal_type"] = "premium"
        await q.edit_message_text(
            "<b>✈️ Telegram Premium\n\nШаг 1 из 4 — Введите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back_to_types")]]))
        return DEAL_PREMIUM_PARTNER

    return DEAL_TYPE

# ===================== NFT =====================
async def deal_nft_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    partner = update.message.text.strip()
    if not partner.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return DEAL_NFT_PARTNER
    context.user_data["partner"] = partner
    await update.message.reply_text(
        "<b>🖼 НФТ Сделка\n\nШаг 2 из 4 — Введите ссылку на НФТ:\n(ссылка должна начинаться с https://)</b>",
        parse_mode="HTML")
    return DEAL_NFT_LINK

async def deal_nft_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    link = update.message.text.strip()
    if not validate_nft_link(link):
        await update.message.reply_text(
            "<b>Ссылка не валидна. Ссылка должна начинаться с https://\nПопробуйте снова:</b>",
            parse_mode="HTML")
        return DEAL_NFT_LINK
    context.user_data["nft_link"] = link
    await update.message.reply_text(
        "<b>🖼 НФТ Сделка\n\nШаг 3 из 4 — Выберите валюту оплаты:</b>",
        parse_mode="HTML",
        reply_markup=currency_keyboard())
    return DEAL_NFT_CURRENCY

async def deal_nft_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text("<b>🖼 НФТ Сделка\n\nШаг 4 из 4 — Введите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_NFT_AMOUNT

async def deal_nft_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== NFT USERNAME =====================
async def deal_username_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    partner = update.message.text.strip()
    if not partner.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return DEAL_USERNAME_PARTNER
    context.user_data["partner"] = partner
    await update.message.reply_text(
        "<b>👤 НФТ Юзернейм\n\nШаг 2 из 4 — Введите юзернейм который продаёте/покупаете:\n(пример: @username)</b>",
        parse_mode="HTML")
    return DEAL_USERNAME_INPUT

async def deal_username_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uname = update.message.text.strip()
    if not uname.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return DEAL_USERNAME_INPUT
    context.user_data["trade_username"] = uname
    await update.message.reply_text(
        "<b>👤 НФТ Юзернейм\n\nШаг 3 из 4 — Выберите валюту оплаты:</b>",
        parse_mode="HTML",
        reply_markup=currency_keyboard())
    return DEAL_USERNAME_CURRENCY

async def deal_username_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text("<b>👤 НФТ Юзернейм\n\nШаг 4 из 4 — Введите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_USERNAME_AMOUNT

async def deal_username_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== STARS =====================
async def deal_stars_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    partner = update.message.text.strip()
    if not partner.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return DEAL_STARS_PARTNER
    context.user_data["partner"] = partner
    await update.message.reply_text(
        "<b>⭐️ Звёзды\n\nШаг 2 из 4 — Введите количество звёзд:</b>",
        parse_mode="HTML")
    return DEAL_STARS_COUNT

async def deal_stars_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = update.message.text.strip()
    if not count.isdigit():
        await update.message.reply_text("<b>Введите число звёзд (только цифры):</b>", parse_mode="HTML")
        return DEAL_STARS_COUNT
    context.user_data["stars_count"] = count
    await update.message.reply_text(
        "<b>⭐️ Звёзды\n\nШаг 3 из 4 — Выберите валюту оплаты:</b>",
        parse_mode="HTML",
        reply_markup=currency_keyboard())
    return DEAL_STARS_CURRENCY

async def deal_stars_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text("<b>⭐️ Звёзды\n\nШаг 4 из 4 — Введите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_STARS_AMOUNT

async def deal_stars_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== CRYPTO =====================
async def deal_crypto_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "back_to_types":
        await show_deal_types(update, context)
        return DEAL_TYPE
    cur_map = {"crypto_ton": "TON", "crypto_usdt": "USDT"}
    context.user_data["currency"] = cur_map.get(q.data, q.data)
    await q.edit_message_text("<b>💎 Крипта\n\nШаг 2 из 2 — Введите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_CRYPTO_AMOUNT

async def deal_crypto_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    context.user_data["partner"] = "—"
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== GIFTBOX =====================
async def deal_giftbox_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    partner = update.message.text.strip()
    if not partner.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return DEAL_GIFTBOX_PARTNER
    context.user_data["partner"] = partner
    await update.message.reply_text(
        "<b>🎁 НФТ Подарок\n\nШаг 2 из 4 — Введите ссылку на НФТ Подарок:\n(ссылка должна начинаться с https://)</b>",
        parse_mode="HTML")
    return DEAL_GIFTBOX_LINK

async def deal_giftbox_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    if not validate_nft_link(link):
        await update.message.reply_text(
            "<b>Ссылка не валидна. Ссылка должна начинаться с https://\nПопробуйте снова:</b>",
            parse_mode="HTML")
        return DEAL_GIFTBOX_LINK
    context.user_data["nft_link"] = link
    await update.message.reply_text(
        "<b>🎁 НФТ Подарок\n\nШаг 3 из 4 — Выберите валюту оплаты:</b>",
        parse_mode="HTML",
        reply_markup=currency_keyboard())
    return DEAL_GIFTBOX_CURRENCY

async def deal_giftbox_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text("<b>🎁 НФТ Подарок\n\nШаг 4 из 4 — Введите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_GIFTBOX_AMOUNT

async def deal_giftbox_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== PREMIUM =====================
async def deal_premium_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    partner = update.message.text.strip()
    if not partner.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return DEAL_PREMIUM_PARTNER
    context.user_data["partner"] = partner
    await update.message.reply_text(
        "<b>✈️ Telegram Premium\n\nШаг 2 из 4 — Выберите срок подписки:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("3 месяца", callback_data="prem_3"),
             InlineKeyboardButton("6 месяцев", callback_data="prem_6"),
             InlineKeyboardButton("12 месяцев", callback_data="prem_12")],
        ]))
    return DEAL_PREMIUM_PERIOD

async def deal_premium_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    period_map = {"prem_3": "3 месяца", "prem_6": "6 месяцев", "prem_12": "12 месяцев"}
    context.user_data["premium_period"] = period_map.get(q.data, q.data)
    await q.edit_message_text(
        "<b>✈️ Telegram Premium\n\nШаг 3 из 4 — Выберите валюту оплаты:</b>",
        parse_mode="HTML",
        reply_markup=currency_keyboard())
    return DEAL_PREMIUM_CURRENCY

async def deal_premium_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text("<b>✈️ Telegram Premium\n\nШаг 4 из 4 — Введите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_PREMIUM_AMOUNT

async def deal_premium_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== FINALIZE DEAL =====================
async def finalize_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    ud = context.user_data
    deal_id = gen_deal_id(db)
    deal_type = ud.get("deal_type", "unknown")
    partner = ud.get("partner", "—")
    currency = ud.get("currency", "—")
    amount = ud.get("amount", "—")
    user = update.effective_user

    type_names = {
        "nft": "🖼 НФТ",
        "username": "👤 НФТ Юзернейм",
        "stars": "⭐️ Звёзды",
        "crypto": "💎 Крипта",
        "giftbox": "🎁 НФТ Подарок",
        "premium": "✈️ Telegram Premium",
    }

    lines = [
        "<b>✅ Сделка успешно создана!</b>",
        "",
        f"<b>Код сделки (MEMO):</b> <code>{deal_id}</code>",
        f"<b>Тип:</b> {type_names.get(deal_type, deal_type)}",
        f"<b>Партнёр:</b> {partner}",
    ]

    if deal_type in ("nft", "giftbox"):
        lines.append(f"<b>Ссылка НФТ:</b> {ud.get('nft_link', '—')}")
    elif deal_type == "username":
        lines.append(f"<b>Юзернейм товара:</b> {ud.get('trade_username', '—')}")
    elif deal_type == "stars":
        lines.append(f"<b>Количество звёзд:</b> {ud.get('stars_count', '—')}")
    elif deal_type == "premium":
        lines.append(f"<b>Срок Premium:</b> {ud.get('premium_period', '—')}")

    lines += [
        f"<b>Валюта:</b> {currency}",
        f"<b>Сумма:</b> {amount}",
        "",
    ]

    if deal_type in ("nft", "stars", "giftbox"):
        lines += [
            "<b>📤 Куда отправить оплату:</b>",
            f"<b>Менеджер:</b> {MANAGER_USERNAME}",
            f"<b>Укажите MEMO при переводе:</b> <code>{deal_id}</code>",
        ]
    elif deal_type == "username":
        lines += [
            "<b>📤 Куда отправить оплату:</b>",
            "<b>Адрес TON (TonKeeper):</b>",
            f"<code>{CRYPTO_ADDRESS}</code>",
            f"<b>Укажите MEMO при переводе:</b> <code>{deal_id}</code>",
        ]
    elif deal_type == "crypto":
        lines += [
            "<b>📤 Куда отправить оплату:</b>",
            "<b>Адрес TON (TonKeeper):</b>",
            f"<code>{CRYPTO_ADDRESS}</code>",
            f"<b>Укажите MEMO при переводе:</b> <code>{deal_id}</code>",
        ]
    elif deal_type == "premium":
        lines += [
            "<b>📤 Оплату отправьте менеджеру:</b>",
            f"<b>Менеджер:</b> {MANAGER_USERNAME}",
            "<b>После оплаты Premium будет зачислен автоматически.</b>",
            f"<b>Укажите MEMO при переводе:</b> <code>{deal_id}</code>",
        ]

    lines += [
        "",
        "<b>🔗 Ссылка на сделку:</b>",
        f"<code>https://t.me/{BOT_USERNAME}?start=deal_{deal_id}</code>",
    ]

    db["deals"][deal_id] = {
        "user_id": str(user.id),
        "type": deal_type,
        "partner": partner,
        "currency": currency,
        "amount": amount,
        "status": "pending",
        "created": datetime.now().isoformat(),
        "data": dict(ud),
    }
    save_db(db)

    text = "\n".join(lines)
    await update.effective_message.reply_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))
    context.user_data.clear()

# ===================== BALANCE =====================
async def show_balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐️ Звёзды", callback_data="balance_stars")],
        [InlineKeyboardButton("💴 Рубли", callback_data="balance_rub")],
        [InlineKeyboardButton("💎 TON / USDT", callback_data="balance_crypto")],
        [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
    ])
    await update.callback_query.edit_message_text(
        "<b>➕ Пополнение баланса\n\nВыберите способ пополнения:</b>",
        parse_mode="HTML", reply_markup=kb)

async def show_balance_info(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    q = update.callback_query
    uid = update.effective_user.id
    if method == "stars":
        text = (
            f"<b>⭐️ Пополнение звёздами\n\n"
            f"Отправьте звёзды менеджеру:\n"
            f"Менеджер: {MANAGER_USERNAME}\n\n"
            f"После подтверждения баланс будет зачислен.</b>"
        )
    elif method == "rub":
        text = (
            f"<b>💴 Пополнение рублями\n\n"
            f"Переводите рубли менеджеру:\n"
            f"Менеджер: {MANAGER_USERNAME}\n\n"
            f"После подтверждения баланс будет зачислен.</b>"
        )
    elif method == "crypto":
        text = (
            f"<b>💎 Пополнение TON / USDT\n\n"
            f"Адрес TON (TonKeeper):\n<code>{CRYPTO_ADDRESS}</code>\n\n"
            f"Или через крипто бот:\n{CRYPTO_BOT_LINK}\n\n"
            f"Укажите в комментарии ваш Telegram ID: <code>{uid}</code></b>"
        )
    else:
        text = "<b>Неизвестный метод</b>"

    await q.edit_message_text(text, parse_mode="HTML",
                              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_balance")]]))

# ===================== LANGUAGE =====================
async def show_lang_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    row = []
    for code, name in LANGS.items():
        row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
    await update.callback_query.edit_message_text(
        "<b>🔄 Выберите язык:</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    db = load_db()
    user = get_user(db, update.effective_user.id)
    user["lang"] = lang
    save_db(db)
    await update.callback_query.answer("Язык изменён!")
    await send_main_menu(update, context, edit=True)

# ===================== PROFILE =====================
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    uid = update.effective_user.id
    user = get_user(db, uid)
    uname = update.effective_user.username or "—"
    status_line = f"\n🏷 Статус: {user['status']}" if user.get("status") else ""
    reviews = user.get("reviews", [])
    reviews_text = ""
    if reviews:
        reviews_text = "\n\n<b>📝 Отзывы:</b>\n" + "\n".join([f"• {r}" for r in reviews[-5:]])

    text = (
        f"<b>👤 Профиль пользователя{status_line}\n\n"
        f"📱 Имя пользователя: @{uname}\n"
        f"💰 Общий баланс: {user.get('balance', 0)} RUB\n"
        f"📊 Всего сделок: {user.get('total_deals', 0)}\n"
        f"✅ Успешных сделок: {user.get('success_deals', 0)}\n"
        f"💵 Суммарный оборот: {user.get('turnover', 0)} RUB\n"
        f"⭐️ Репутация: {user.get('reputation', 0)}</b>"
        f"{reviews_text}"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Пополнить баланс", callback_data="menu_balance"),
         InlineKeyboardButton("💸 Вывод средств", callback_data="withdraw")],
        [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
    ])
    await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

# ===================== TOP SELLERS =====================
async def show_top_sellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    TOP = [
        ("@al***ndr", 450, 47),
        ("@ie***ym", 380, 38),
        ("@ma***ov", 310, 29),
        ("@kr***na", 290, 31),
        ("@pe***ko", 270, 25),
        ("@se***ev", 240, 22),
        ("@an***va", 210, 19),
        ("@vi***or", 190, 17),
        ("@dm***iy", 170, 15),
        ("@ni***la", 140, 13),
    ]
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    lines = ["<b>🏆 Топ продавцов Gift Deals\n</b>"]
    for i, (uname, amount, deals) in enumerate(TOP):
        lines.append(f"<b>{medals[i]} {i+1}. {uname} — ${amount} | {deals} сделок</b>")
    lines.append("\n<b>Хочешь попасть в топ? Создавай больше сделок!</b>")
    await update.callback_query.edit_message_text(
        "\n".join(lines), parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]))

# ===================== ADMIN PANEL =====================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    await update.message.reply_text(
        "<b>🛠 Панель администратора</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👤 Управление пользователем", callback_data="adm_user")],
            [InlineKeyboardButton("📢 Установить баннер (текст/фото)", callback_data="adm_banner")],
            [InlineKeyboardButton("📝 Изменить описание меню", callback_data="adm_menu_desc")],
            [InlineKeyboardButton("📋 Список сделок", callback_data="adm_deals")],
        ]))
    return ADMIN_ACTION

def admin_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Управление пользователем", callback_data="adm_user")],
        [InlineKeyboardButton("📢 Установить баннер (текст/фото)", callback_data="adm_banner")],
        [InlineKeyboardButton("📝 Изменить описание меню", callback_data="adm_menu_desc")],
        [InlineKeyboardButton("📋 Список сделок", callback_data="adm_deals")],
    ])

async def admin_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "adm_back":
        await q.edit_message_text("<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADMIN_ACTION

    if data == "adm_user":
        await q.edit_message_text(
            "<b>Введите @юзернейм пользователя:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return ADMIN_SET_USER

    if data == "adm_banner":
        await q.edit_message_text(
            "<b>📢 Отправьте:\n"
            "— Текст баннера\n"
            "— Фото (с подписью или без)\n\n"
            "Чтобы убрать баннер — напишите: off</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return BANNER_SET

    if data == "adm_menu_desc":
        await q.edit_message_text(
            "<b>Введите новое описание для главного меню:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return MENU_DESC_SET

    if data == "adm_deals":
        db = load_db()
        deals = db.get("deals", {})
        if not deals:
            await q.edit_message_text(
                "<b>Сделок нет.</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
            return ADMIN_ACTION
        text = "<b>📋 Последние 10 сделок:\n</b>"
        for did, d in list(deals.items())[-10:]:
            text += f"\n<b>{did}</b> | {d.get('type')} | {d.get('amount')} {d.get('currency')} | {d.get('status')}"
        await q.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return ADMIN_ACTION

    # Кнопки редактирования пользователя
    action_map = {
        "adm_add_review": ("review", "Введите текст отзыва:"),
        "adm_set_deals": ("total_deals", "Введите количество сделок:"),
        "adm_set_success": ("success_deals", "Введите количество успешных сделок:"),
        "adm_set_turnover": ("turnover", "Введите оборот (число):"),
        "adm_set_rep": ("reputation", "Введите репутацию (число):"),
        "adm_set_status": ("status", "Введите статус:\n(например: ✅ Проверенный / ❌ Скамер / 🔒 Заблокирован)"),
    }
    if data in action_map:
        field, prompt = action_map[data]
        context.user_data["adm_field"] = field
        await q.edit_message_text(f"<b>{prompt}</b>", parse_mode="HTML")
        return ADMIN_SET_VALUE

    return ADMIN_ACTION

async def admin_set_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADMIN_ACTION
    text = update.message.text.strip()
    username = text.lstrip("@").lower()
    db = load_db()
    found_uid = None
    for uid, u in db["users"].items():
        if u.get("username", "").lower() == username:
            found_uid = uid
            break
    if not found_uid:
        await update.message.reply_text(
            "<b>Пользователь не найден.\nПользователь должен хотя бы раз запустить бота.\n\nВведите @юзернейм снова:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад в меню", callback_data="adm_back")]]))
        return ADMIN_SET_USER
    context.user_data["adm_target_uid"] = found_uid
    u = db["users"][found_uid]
    await update.message.reply_text(
        f"<b>👤 Пользователь: @{u.get('username', '—')}\n"
        f"Сделок: {u.get('total_deals', 0)} | Успешных: {u.get('success_deals', 0)}\n"
        f"Оборот: {u.get('turnover', 0)} | Репутация: {u.get('reputation', 0)}\n"
        f"Статус: {u.get('status', '—')}\n\nЧто изменить?</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Добавить отзыв", callback_data="adm_add_review")],
            [InlineKeyboardButton("🔢 Кол-во сделок", callback_data="adm_set_deals"),
             InlineKeyboardButton("✅ Успешных сделок", callback_data="adm_set_success")],
            [InlineKeyboardButton("💵 Оборот", callback_data="adm_set_turnover"),
             InlineKeyboardButton("⭐️ Репутацию", callback_data="adm_set_rep")],
            [InlineKeyboardButton("🏷 Статус", callback_data="adm_set_status")],
            [InlineKeyboardButton("◀️ Назад", callback_data="adm_back")],
        ]))
    return ADMIN_ACTION

async def admin_set_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    value = update.message.text.strip()
    field = context.user_data.get("adm_field")
    uid = context.user_data.get("adm_target_uid")
    if not field or not uid:
        await update.message.reply_text("<b>Ошибка. Начните заново /admin</b>", parse_mode="HTML")
        return ConversationHandler.END
    db = load_db()
    u = db["users"].get(uid, {})
    if field == "review":
        u.setdefault("reviews", []).append(value)
    elif field in ("total_deals", "success_deals", "turnover", "reputation"):
        try:
            u[field] = int(value)
        except ValueError:
            await update.message.reply_text("<b>Введите число!</b>", parse_mode="HTML")
            return ADMIN_SET_VALUE
    else:
        u[field] = value
    db["users"][uid] = u
    save_db(db)
    await update.message.reply_text(
        f"<b>✅ Поле успешно обновлено!</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
    return ADMIN_ACTION

async def banner_set_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    # Обработка нажатия кнопки "Назад" внутри состояния баннера
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADMIN_ACTION
    db = load_db()
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
        caption = update.message.caption or ""
        db["banner_photo"] = photo_id
        db["banner"] = caption
        save_db(db)
        await update.message.reply_text(
            "<b>✅ Фото-баннер установлен!</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
    elif update.message.text:
        text = update.message.text.strip()
        if text.lower() == "off":
            db["banner"] = None
            db["banner_photo"] = None
            save_db(db)
            await update.message.reply_text(
                "<b>✅ Баннер удалён!</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
        else:
            db["banner"] = text
            db["banner_photo"] = None
            save_db(db)
            await update.message.reply_text(
                "<b>✅ Текстовый баннер установлен!</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
    else:
        await update.message.reply_text("<b>Отправьте текст или фото.</b>", parse_mode="HTML")
        return BANNER_SET
    return ADMIN_ACTION

async def menu_desc_set_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADMIN_ACTION
    db = load_db()
    db["menu_description"] = update.message.text.strip()
    save_db(db)
    await update.message.reply_text(
        "<b>✅ Описание меню обновлено!</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
    return ADMIN_ACTION

# ===================== SECRET COMMAND =====================
async def neptune_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>Добро пожаловать!\n\n"
        "Вам доступны следующие команды:\n\n"
        "🔹 /buy [Код сделки (MEMO)]\n"
        "   - Взять сделку на себя и подтвердить оплату.\n\n"
        "🔹 /set_my_deals [число]\n"
        "   - Установить себе количество успешных сделок.\n"
        "   Пример: /set_my_deals 100\n\n"
        "🔹 /set_my_amount [сумма]\n"
        "   - Установить себе сумму сделок продавца.\n"
        "   Пример: /set_my_amount 15000</b>"
    )
    await update.message.reply_text(text, parse_mode="HTML")

async def buy_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("<b>Укажите код сделки. Пример: /buy GD00001</b>", parse_mode="HTML")
        return
    deal_id = args[0].upper()
    db = load_db()
    if deal_id not in db.get("deals", {}):
        await update.message.reply_text("<b>Сделка не найдена.</b>", parse_mode="HTML")
        return
    deal = db["deals"][deal_id]
    deal["status"] = "confirmed"
    uid = str(update.effective_user.id)
    u = get_user(db, uid)
    u["success_deals"] = u.get("success_deals", 0) + 1
    u["total_deals"] = u.get("total_deals", 0) + 1
    save_db(db)
    await update.message.reply_text(
        f"<b>✅ Сделка {deal_id} подтверждена!\n"
        f"Партнёр: {deal.get('partner')}\n"
        f"Сумма: {deal.get('amount')} {deal.get('currency')}</b>",
        parse_mode="HTML")

async def set_my_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("<b>Пример: /set_my_deals 100</b>", parse_mode="HTML")
        return
    db = load_db()
    uid = str(update.effective_user.id)
    u = get_user(db, uid)
    u["success_deals"] = int(args[0])
    u["total_deals"] = int(args[0])
    save_db(db)
    await update.message.reply_text(f"<b>✅ Установлено {args[0]} успешных сделок!</b>", parse_mode="HTML")

async def set_my_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("<b>Пример: /set_my_amount 15000</b>", parse_mode="HTML")
        return
    try:
        amount = int(args[0])
    except ValueError:
        await update.message.reply_text("<b>Введите число!</b>", parse_mode="HTML")
        return
    db = load_db()
    uid = str(update.effective_user.id)
    u = get_user(db, uid)
    u["turnover"] = amount
    save_db(db)
    await update.message.reply_text(f"<b>✅ Оборот установлен: {amount} RUB</b>", parse_mode="HTML")

async def withdraw_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        f"<b>💸 Вывод средств\n\n"
        f"Для вывода обратитесь к менеджеру:\n{MANAGER_USERNAME}\n\n"
        f"Укажите:\n"
        f"- Ваш @юзернейм\n"
        f"- Сумму вывода\n"
        f"- Способ получения</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_profile")]]))

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Deal ConversationHandler
    deal_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_deal_types, pattern="^menu_deal$")],
        states={
            DEAL_TYPE: [
                CallbackQueryHandler(deal_type_handler),
            ],
            DEAL_NFT_PARTNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_nft_partner),
                CallbackQueryHandler(deal_nft_partner, pattern="^back_to_types$"),
            ],
            DEAL_NFT_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_nft_link),
                CallbackQueryHandler(deal_nft_link, pattern="^back_to_types$"),
            ],
            DEAL_NFT_CURRENCY: [
                CallbackQueryHandler(deal_nft_currency, pattern="^cur_"),
            ],
            DEAL_NFT_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_nft_amount),
            ],
            DEAL_USERNAME_PARTNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_username_partner),
                CallbackQueryHandler(deal_username_partner, pattern="^back_to_types$"),
            ],
            DEAL_USERNAME_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_username_input),
            ],
            DEAL_USERNAME_CURRENCY: [
                CallbackQueryHandler(deal_username_currency, pattern="^cur_"),
            ],
            DEAL_USERNAME_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_username_amount),
            ],
            DEAL_STARS_PARTNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_stars_partner),
                CallbackQueryHandler(deal_stars_partner, pattern="^back_to_types$"),
            ],
            DEAL_STARS_COUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_stars_count),
            ],
            DEAL_STARS_CURRENCY: [
                CallbackQueryHandler(deal_stars_currency, pattern="^cur_"),
            ],
            DEAL_STARS_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_stars_amount),
            ],
            DEAL_CRYPTO_CURRENCY: [
                CallbackQueryHandler(deal_crypto_currency),
            ],
            DEAL_CRYPTO_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_crypto_amount),
            ],
            DEAL_GIFTBOX_PARTNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_giftbox_partner),
                CallbackQueryHandler(deal_giftbox_partner, pattern="^back_to_types$"),
            ],
            DEAL_GIFTBOX_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_giftbox_link),
            ],
            DEAL_GIFTBOX_CURRENCY: [
                CallbackQueryHandler(deal_giftbox_currency, pattern="^cur_"),
            ],
            DEAL_GIFTBOX_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_giftbox_amount),
            ],
            DEAL_PREMIUM_PARTNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_premium_partner),
                CallbackQueryHandler(deal_premium_partner, pattern="^back_to_types$"),
            ],
            DEAL_PREMIUM_PERIOD: [
                CallbackQueryHandler(deal_premium_period, pattern="^prem_"),
            ],
            DEAL_PREMIUM_CURRENCY: [
                CallbackQueryHandler(deal_premium_currency, pattern="^cur_"),
            ],
            DEAL_PREMIUM_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_premium_amount),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(callback_router, pattern="^main_menu$"),
            CommandHandler("start", start),
        ],
        per_message=False,
    )

    # Admin ConversationHandler
    admin_conv = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_panel)],
        states={
            ADMIN_ACTION: [
                CallbackQueryHandler(admin_action_callback, pattern="^adm_"),
            ],
            ADMIN_SET_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_set_user),
                CallbackQueryHandler(admin_action_callback, pattern="^adm_back$"),
            ],
            ADMIN_SET_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_set_value),
                CallbackQueryHandler(admin_action_callback, pattern="^adm_"),
            ],
            BANNER_SET: [
                MessageHandler(filters.PHOTO, banner_set_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, banner_set_handler),
                CallbackQueryHandler(banner_set_handler, pattern="^adm_back$"),
            ],
            MENU_DESC_SET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, menu_desc_set_handler),
                CallbackQueryHandler(menu_desc_set_handler, pattern="^adm_back$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("neptunteam", neptune_team))
    app.add_handler(CommandHandler("buy", buy_deal))
    app.add_handler(CommandHandler("set_my_deals", set_my_deals))
    app.add_handler(CommandHandler("set_my_amount", set_my_amount))
    app.add_handler(deal_conv)
    app.add_handler(admin_conv)
    app.add_handler(CallbackQueryHandler(callback_router))

    print(f"Bot @{BOT_USERNAME} started!")
    app.run_polling()

if __name__ == "__main__":
    main()
