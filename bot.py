import logging
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
CRYPTO_ADDRESS = "UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc"
CRYPTO_BOT_LINK = "https://t.me/send?start=IVtoVqCXSHV0"
DB_FILE = "db.json"

# ===================== DATABASE =====================
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "deals": {}, "banner": None, "banner_photo": None, "menu_description": None, "deal_counter": 1}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(db, user_id):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "username": "", "balance": 0, "total_deals": 0,
            "success_deals": 0, "turnover": 0, "reputation": 0,
            "reviews": [], "status": "", "lang": "ru"
        }
    return db["users"][uid]

def gen_deal_id(db):
    did = db.get("deal_counter", 1)
    db["deal_counter"] = did + 1
    save_db(db)
    return f"GD{did:05d}"

# ===================== TRANSLATIONS =====================
LANGS = {
    "ru": "🇷🇺 Русский", "en": "🇬🇧 English", "kz": "🇰🇿 Казахский",
    "az": "🇦🇿 Азербайджанский", "uz": "🇺🇿 Узбекский", "kg": "🇰🇬 Кыргызский",
    "tj": "🇹🇯 Таджикский", "by": "🇧🇾 Белорусский",
}

WELCOME_TEXT = {
    "ru": (
        "Gift Deals — одна из самых безопасных площадок в Telegram для проведения сделок.\n\n"
        "Мы гарантируем честность каждой транзакции: средства и товар передаются только после "
        "подтверждения обеих сторон. Никаких рисков, никаких мошенников — только надёжные сделки "
        "под защитой нашей платформы.\n\nТысячи успешных сделок уже позади — и каждая прошла безопасно."
    ),
    "en": (
        "Gift Deals is one of the safest platforms in Telegram for conducting deals.\n\n"
        "We guarantee the honesty of every transaction. No risks, no fraudsters — "
        "only reliable deals under our platform's protection."
    ),
    "kz": "Gift Deals — Telegram-дағы мәмілелер жүргізу үшін ең қауіпсіз алаңдардың бірі.",
    "az": "Gift Deals — Telegram-da əməliyyatlar aparmaq üçün ən təhlükəsiz platformalardan biridir.",
    "uz": "Gift Deals — Telegram'da bitimlar o'tkazish uchun eng xavfsiz platformalardan biri.",
    "kg": "Gift Deals — Telegram'дагы бүтүмдөр үчүн эң коопсуз аянтча.",
    "tj": "Gift Deals — яке аз бехтарин майдончаҳо дар Telegram барои анҷом додани муомилот.",
    "by": "Gift Deals — адна з самых бяспечных пляцовак у Telegram для правядзення здзелак.",
}

BTN = {
    "ru": {"deal": "✏️ Создать сделку", "support": "🆘 Поддержка", "balance": "➕ Пополнить баланс",
           "lang": "🔄 Сменить язык", "profile": "👤 Профиль", "top": "🏆 Топ продавцов"},
    "en": {"deal": "✏️ Create Deal", "support": "🆘 Support", "balance": "➕ Top Up",
           "lang": "🔄 Language", "profile": "👤 Profile", "top": "🏆 Top Sellers"},
    "kz": {"deal": "✏️ Мәміле жасау", "support": "🆘 Қолдау", "balance": "➕ Балансты толтыру",
            "lang": "🔄 Тілді өзгерту", "profile": "👤 Профиль", "top": "🏆 Үздік сатушылар"},
    "az": {"deal": "✏️ Müqavilə yarat", "support": "🆘 Dəstək", "balance": "➕ Balansı artır",
            "lang": "🔄 Dili dəyiş", "profile": "👤 Profil", "top": "🏆 Top satıcılar"},
    "uz": {"deal": "✏️ Bitim yaratish", "support": "🆘 Qo'llab", "balance": "➕ Balans",
            "lang": "🔄 Til", "profile": "👤 Profil", "top": "🏆 Top sotuvchilar"},
    "kg": {"deal": "✏️ Бүтүм түзүү", "support": "🆘 Колдоо", "balance": "➕ Баланс",
            "lang": "🔄 Тил", "profile": "👤 Профиль", "top": "🏆 Топ сатуучулар"},
    "tj": {"deal": "✏️ Эҷоди муомила", "support": "🆘 Дастгирӣ", "balance": "➕ Баланс",
            "lang": "🔄 Забон", "profile": "👤 Профил", "top": "🏆 Беҳтарин фурӯшандагон"},
    "by": {"deal": "✏️ Стварыць здзелку", "support": "🆘 Падтрымка", "balance": "➕ Баланс",
            "lang": "🔄 Мова", "profile": "👤 Профіль", "top": "🏆 Топ прадаўцоў"},
}

def get_btn(lang, key):
    return BTN.get(lang, BTN["ru"]).get(key, BTN["ru"][key])

# ===================== CURRENCY =====================
def currency_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 TON", callback_data="cur_ton"),
         InlineKeyboardButton("💵 USDT ($)", callback_data="cur_usdt")],
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
    NFT_P, NFT_L, NFT_C, NFT_A,
    USR_P, USR_I, USR_C, USR_A,
    STR_P, STR_N, STR_C, STR_A,
    CRY_C, CRY_A,
    GFT_P, GFT_L, GFT_C, GFT_A,
    PRM_P, PRM_D, PRM_C, PRM_A,
    ADM_MAIN, ADM_USER, ADM_VAL,
    BNR_SET, DSC_SET,
) = range(28)

# ===================== MENU =====================
def main_menu_kb(lang="ru"):
    b = BTN.get(lang, BTN["ru"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(b["deal"], callback_data="menu_deal")],
        [InlineKeyboardButton(b["support"], url="https://t.me/GiftDealsSupport"),
         InlineKeyboardButton(b["balance"], callback_data="menu_balance")],
        [InlineKeyboardButton(b["lang"], callback_data="menu_lang"),
         InlineKeyboardButton(b["profile"], callback_data="menu_profile")],
        [InlineKeyboardButton(b["top"], callback_data="menu_top")],
    ])

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    db = load_db()
    uid = update.effective_user.id
    user = get_user(db, uid)
    lang = user.get("lang", "ru")
    menu_desc = db.get("menu_description")
    banner = db.get("banner")
    banner_photo = db.get("banner_photo")
    desc = menu_desc if menu_desc else WELCOME_TEXT.get(lang, WELCOME_TEXT["ru"])
    text = f"<b>💎 Gift Deals\n\n{desc}</b>"
    if banner:
        text += f"\n\n<b>{banner}</b>"
    kb = main_menu_kb(lang)
    if banner_photo:
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

    args = context.args
    if args and args[0].startswith("deal_"):
        deal_id = args[0][5:].upper()
        deals = db.get("deals", {})
        if deal_id in deals:
            d = deals[deal_id]
            type_names = {
                "nft": "🖼 НФТ", "username": "👤 НФТ Юзернейм", "stars": "⭐️ Звёзды",
                "crypto": "💎 Крипта", "giftbox": "🎁 НФТ Подарок", "premium": "✈️ Telegram Premium",
            }
            dd = d.get("data", {})
            extra = ""
            if d.get("type") in ("nft", "giftbox"):
                extra = f"\n<b>Ссылка НФТ:</b> {dd.get('nft_link', '—')}"
            elif d.get("type") == "username":
                extra = f"\n<b>Юзернейм товара:</b> {dd.get('trade_username', '—')}"
            elif d.get("type") == "stars":
                extra = f"\n<b>Количество звёзд:</b> {dd.get('stars_count', '—')}"
            elif d.get("type") == "premium":
                extra = f"\n<b>Срок Premium:</b> {dd.get('premium_period', '—')}"
            status_map = {"pending": "⏳ Ожидает оплаты", "confirmed": "✅ Подтверждена"}
            text = (
                f"<b>📋 Информация о сделке\n\n"
                f"Код (MEMO):</b> <code>{deal_id}</code>\n"
                f"<b>Тип:</b> {type_names.get(d.get('type',''), d.get('type',''))}\n"
                f"<b>Партнёр:</b> {d.get('partner','—')}"
                f"{extra}\n"
                f"<b>Валюта:</b> {d.get('currency','—')}\n"
                f"<b>Сумма:</b> {d.get('amount','—')}\n"
                f"<b>Статус:</b> {status_map.get(d.get('status',''), d.get('status','—'))}\n"
                f"<b>Создана:</b> {d.get('created','—')[:16].replace('T',' ')}"
            )
            await update.effective_message.reply_text(
                text, parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))
            return
        else:
            await update.effective_message.reply_text(f"<b>Сделка {deal_id} не найдена.</b>", parse_mode="HTML")

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
    elif data == "menu_lang":
        await show_lang_menu(update, context)
    elif data == "menu_profile":
        await show_profile(update, context)
    elif data == "menu_top":
        await show_top_sellers(update, context)
    elif data.startswith("lang_"):
        await set_language(update, context, data[5:])
    elif data.startswith("balance_"):
        await show_balance_info(update, context, data[8:])
    elif data == "withdraw":
        await withdraw_handler(update, context)

# ===================== DEAL TYPES MENU =====================
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
    try:
        await update.callback_query.edit_message_text(
            "<b>✏️ Создать сделку\n\nВыберите тип товара:</b>",
            parse_mode="HTML", reply_markup=kb)
    except Exception:
        await update.effective_message.reply_text(
            "<b>✏️ Создать сделку\n\nВыберите тип товара:</b>",
            parse_mode="HTML", reply_markup=kb)
    return DEAL_TYPE

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад к типам", callback_data="back_to_types")]])

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
            "<b>🖼 НФТ — Создание сделки\n\n"
            "Шаги:\n"
            "1. Юзернейм партнёра\n"
            "2. Ссылка на НФТ\n"
            "3. Валюта\n"
            "4. Сумма\n\n"
            "Шаг 1 из 4 — Введите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML", reply_markup=back_kb())
        return NFT_P

    if data == "deal_username":
        context.user_data["deal_type"] = "username"
        await q.edit_message_text(
            "<b>👤 НФТ Юзернейм — Создание сделки\n\n"
            "Шаги:\n"
            "1. Юзернейм партнёра\n"
            "2. Юзернейм товара\n"
            "3. Валюта\n"
            "4. Сумма\n\n"
            "Шаг 1 из 4 — Введите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML", reply_markup=back_kb())
        return USR_P

    if data == "deal_stars":
        context.user_data["deal_type"] = "stars"
        await q.edit_message_text(
            "<b>⭐️ Звёзды — Создание сделки\n\n"
            "Шаги:\n"
            "1. Юзернейм партнёра\n"
            "2. Количество звёзд\n"
            "3. Валюта\n"
            "4. Сумма\n\n"
            "Шаг 1 из 4 — Введите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML", reply_markup=back_kb())
        return STR_P

    if data == "deal_crypto":
        context.user_data["deal_type"] = "crypto"
        await q.edit_message_text(
            "<b>💎 Крипта — Создание сделки\n\n"
            "Шаги:\n"
            "1. TON или $ (USDT)\n"
            "2. Сумма\n\n"
            "Шаг 1 из 2 — Выберите: TON или $?</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 TON", callback_data="crypto_ton"),
                 InlineKeyboardButton("💵 $ (USDT)", callback_data="crypto_usdt")],
                [InlineKeyboardButton("◀️ Назад к типам", callback_data="back_to_types")],
            ]))
        return CRY_C

    if data == "deal_giftbox":
        context.user_data["deal_type"] = "giftbox"
        await q.edit_message_text(
            "<b>🎁 НФТ Подарок — Создание сделки\n\n"
            "Шаги:\n"
            "1. Юзернейм партнёра\n"
            "2. Ссылка на НФТ Подарок\n"
            "3. Валюта\n"
            "4. Сумма\n\n"
            "Шаг 1 из 4 — Введите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML", reply_markup=back_kb())
        return GFT_P

    if data == "deal_premium":
        context.user_data["deal_type"] = "premium"
        await q.edit_message_text(
            "<b>✈️ Telegram Premium — Создание сделки\n\n"
            "Шаги:\n"
            "1. Юзернейм партнёра\n"
            "2. Срок подписки\n"
            "3. Валюта\n"
            "4. Сумма\n\n"
            "Шаг 1 из 4 — Введите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML", reply_markup=back_kb())
        return PRM_P

    return DEAL_TYPE

# ========== НФТ ==========
async def nft_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    partner = update.message.text.strip()
    if not partner.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return NFT_P
    context.user_data["partner"] = partner
    await update.message.reply_text(
        "<b>🖼 НФТ\n\nШаг 2 из 4 — Введите ссылку на НФТ:\n(ссылка должна начинаться с https://)</b>",
        parse_mode="HTML")
    return NFT_L

async def nft_l(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    if not link.startswith("https://"):
        await update.message.reply_text(
            "<b>Ссылка должна начинаться с https://\nПопробуйте снова:</b>", parse_mode="HTML")
        return NFT_L
    context.user_data["nft_link"] = link
    await update.message.reply_text(
        "<b>🖼 НФТ\n\nШаг 3 из 4 — Выберите валюту оплаты:</b>",
        parse_mode="HTML", reply_markup=currency_keyboard())
    return NFT_C

async def nft_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text(
        "<b>🖼 НФТ\n\nШаг 4 из 4 — Введите сумму сделки:</b>", parse_mode="HTML")
    return NFT_A

async def nft_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ========== НФТ ЮЗЕРНЕЙМ ==========
async def usr_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    partner = update.message.text.strip()
    if not partner.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return USR_P
    context.user_data["partner"] = partner
    await update.message.reply_text(
        "<b>👤 НФТ Юзернейм\n\nШаг 2 из 4 — Введите юзернейм который продаёте/покупаете:\n(пример: @username)</b>",
        parse_mode="HTML")
    return USR_I

async def usr_i(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uname = update.message.text.strip()
    if not uname.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return USR_I
    context.user_data["trade_username"] = uname
    await update.message.reply_text(
        "<b>👤 НФТ Юзернейм\n\nШаг 3 из 4 — Выберите валюту оплаты:</b>",
        parse_mode="HTML", reply_markup=currency_keyboard())
    return USR_C

async def usr_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text(
        "<b>👤 НФТ Юзернейм\n\nШаг 4 из 4 — Введите сумму сделки:</b>", parse_mode="HTML")
    return USR_A

async def usr_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ========== ЗВЁЗДЫ ==========
async def str_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    partner = update.message.text.strip()
    if not partner.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return STR_P
    context.user_data["partner"] = partner
    await update.message.reply_text(
        "<b>⭐️ Звёзды\n\nШаг 2 из 4 — Введите количество звёзд:</b>", parse_mode="HTML")
    return STR_N

async def str_n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = update.message.text.strip()
    if not count.isdigit():
        await update.message.reply_text("<b>Введите только цифры. Попробуйте снова:</b>", parse_mode="HTML")
        return STR_N
    context.user_data["stars_count"] = count
    await update.message.reply_text(
        "<b>⭐️ Звёзды\n\nШаг 3 из 4 — Выберите валюту оплаты:</b>",
        parse_mode="HTML", reply_markup=currency_keyboard())
    return STR_C

async def str_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text(
        "<b>⭐️ Звёзды\n\nШаг 4 из 4 — Введите сумму сделки:</b>", parse_mode="HTML")
    return STR_A

async def str_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ========== КРИПТА ==========
async def cry_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "back_to_types":
        await show_deal_types(update, context)
        return DEAL_TYPE
    cur_map = {"crypto_ton": "TON", "crypto_usdt": "USDT"}
    cur = cur_map.get(q.data, "TON")
    context.user_data["currency"] = cur
    context.user_data["partner"] = "—"
    await q.edit_message_text(
        f"<b>💎 Крипта ({cur})\n\nШаг 2 из 2 — Введите сумму сделки:</b>", parse_mode="HTML")
    return CRY_A

async def cry_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ========== НФТ ПОДАРОК ==========
async def gft_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    partner = update.message.text.strip()
    if not partner.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return GFT_P
    context.user_data["partner"] = partner
    await update.message.reply_text(
        "<b>🎁 НФТ Подарок\n\nШаг 2 из 4 — Введите ссылку на НФТ Подарок:\n(ссылка должна начинаться с https://)</b>",
        parse_mode="HTML")
    return GFT_L

async def gft_l(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    if not link.startswith("https://"):
        await update.message.reply_text(
            "<b>Ссылка должна начинаться с https://\nПопробуйте снова:</b>", parse_mode="HTML")
        return GFT_L
    context.user_data["nft_link"] = link
    await update.message.reply_text(
        "<b>🎁 НФТ Подарок\n\nШаг 3 из 4 — Выберите валюту оплаты:</b>",
        parse_mode="HTML", reply_markup=currency_keyboard())
    return GFT_C

async def gft_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text(
        "<b>🎁 НФТ Подарок\n\nШаг 4 из 4 — Введите сумму сделки:</b>", parse_mode="HTML")
    return GFT_A

async def gft_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ========== TELEGRAM PREMIUM ==========
async def prm_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    partner = update.message.text.strip()
    if not partner.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @ . Попробуйте снова:</b>", parse_mode="HTML")
        return PRM_P
    context.user_data["partner"] = partner
    await update.message.reply_text(
        "<b>✈️ Telegram Premium\n\nШаг 2 из 4 — Выберите срок подписки:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("3 месяца", callback_data="prem_3"),
             InlineKeyboardButton("6 месяцев", callback_data="prem_6"),
             InlineKeyboardButton("12 месяцев", callback_data="prem_12")],
        ]))
    return PRM_D

async def prm_d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    period_map = {"prem_3": "3 месяца", "prem_6": "6 месяцев", "prem_12": "12 месяцев"}
    context.user_data["premium_period"] = period_map.get(q.data, q.data)
    await q.edit_message_text(
        "<b>✈️ Telegram Premium\n\nШаг 3 из 4 — Выберите валюту оплаты:</b>",
        parse_mode="HTML", reply_markup=currency_keyboard())
    return PRM_C

async def prm_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text(
        "<b>✈️ Telegram Premium\n\nШаг 4 из 4 — Введите сумму сделки:</b>", parse_mode="HTML")
    return PRM_A

async def prm_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "nft": "🖼 НФТ", "username": "👤 НФТ Юзернейм", "stars": "⭐️ Звёзды",
        "crypto": "💎 Крипта", "giftbox": "🎁 НФТ Подарок", "premium": "✈️ Telegram Premium",
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

    lines += [f"<b>Валюта:</b> {currency}", f"<b>Сумма:</b> {amount}", ""]

    if deal_type in ("nft", "stars", "giftbox"):
        lines += [
            "<b>📤 Куда отправить оплату:</b>",
            f"<b>Менеджер:</b> {MANAGER_USERNAME}",
            f"<b>Укажите MEMO:</b> <code>{deal_id}</code>",
        ]
    elif deal_type == "username":
        lines += [
            "<b>📤 Куда отправить оплату:</b>",
            "<b>Адрес TON (TonKeeper):</b>",
            f"<code>{CRYPTO_ADDRESS}</code>",
            f"<b>Укажите MEMO:</b> <code>{deal_id}</code>",
        ]
    elif deal_type == "crypto":
        lines += [
            "<b>📤 Куда отправить оплату:</b>",
            "<b>Адрес TON (TonKeeper):</b>",
            f"<code>{CRYPTO_ADDRESS}</code>",
            f"<b>Укажите MEMO:</b> <code>{deal_id}</code>",
        ]
    elif deal_type == "premium":
        lines += [
            "<b>📤 Оплату отправьте менеджеру:</b>",
            f"<b>Менеджер:</b> {MANAGER_USERNAME}",
            "<b>После оплаты Premium зачислят автоматически.</b>",
            f"<b>Укажите MEMO:</b> <code>{deal_id}</code>",
        ]

    lines += [
        "",
        "<b>🔗 Ссылка на сделку:</b>",
        f"<code>https://t.me/{BOT_USERNAME}?start=deal_{deal_id}</code>",
    ]

    db["deals"][deal_id] = {
        "user_id": str(user.id), "type": deal_type, "partner": partner,
        "currency": currency, "amount": amount, "status": "pending",
        "created": datetime.now().isoformat(), "data": dict(ud),
    }
    save_db(db)

    await update.effective_message.reply_text(
        "\n".join(lines), parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))
    context.user_data.clear()

# ===================== BALANCE =====================
async def show_balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "<b>➕ Пополнение баланса\n\nВыберите способ пополнения:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐️ Звёзды", callback_data="balance_stars")],
            [InlineKeyboardButton("💴 Рубли", callback_data="balance_rub")],
            [InlineKeyboardButton("💎 TON / USDT", callback_data="balance_crypto")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
        ]))

async def show_balance_info(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    uid = update.effective_user.id
    if method == "stars":
        text = (f"<b>⭐️ Пополнение звёздами\n\nОтправьте звёзды менеджеру:\n"
                f"Менеджер: {MANAGER_USERNAME}\n\nПосле подтверждения баланс будет зачислен.</b>")
    elif method == "rub":
        text = (f"<b>💴 Пополнение рублями\n\nПереводите рубли менеджеру:\n"
                f"Менеджер: {MANAGER_USERNAME}\n\nПосле подтверждения баланс будет зачислен.</b>")
    elif method == "crypto":
        text = (f"<b>💎 Пополнение TON / USDT\n\nАдрес TON (TonKeeper):\n"
                f"<code>{CRYPTO_ADDRESS}</code>\n\nИли через крипто бот:\n{CRYPTO_BOT_LINK}\n\n"
                f"Укажите в комментарии ваш Telegram ID: <code>{uid}</code></b>")
    else:
        text = "<b>Неизвестный метод</b>"
    await update.callback_query.edit_message_text(
        text, parse_mode="HTML",
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
    u = get_user(db, update.effective_user.id)
    u["lang"] = lang
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
    reviews_text = ("\n\n<b>📝 Отзывы:</b>\n" + "\n".join([f"• {r}" for r in reviews[-5:]])) if reviews else ""
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
    await update.callback_query.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Пополнить баланс", callback_data="menu_balance"),
             InlineKeyboardButton("💸 Вывод средств", callback_data="withdraw")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
        ]))

# ===================== TOP SELLERS =====================
async def show_top_sellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    TOP = [
        ("@al***ndr", 450, 47), ("@ie***ym", 380, 38), ("@ma***ov", 310, 29),
        ("@kr***na", 290, 31), ("@pe***ko", 270, 25), ("@se***ev", 240, 22),
        ("@an***va", 210, 19), ("@vi***or", 190, 17), ("@dm***iy", 170, 15), ("@ni***la", 140, 13),
    ]
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    lines = ["<b>🏆 Топ продавцов Gift Deals\n</b>"]
    for i, (uname, amount, deals) in enumerate(TOP):
        lines.append(f"<b>{medals[i]} {i+1}. {uname} — ${amount} | {deals} сделок</b>")
    lines.append("\n<b>Хочешь попасть в топ? Создавай больше сделок!</b>")
    await update.callback_query.edit_message_text(
        "\n".join(lines), parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]))

# ===================== ADMIN =====================
def admin_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Управление пользователем", callback_data="adm_user")],
        [InlineKeyboardButton("📢 Установить баннер", callback_data="adm_banner")],
        [InlineKeyboardButton("📝 Изменить описание меню", callback_data="adm_menu_desc")],
        [InlineKeyboardButton("📋 Список сделок", callback_data="adm_deals")],
    ])

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    await update.message.reply_text(
        "<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
    return ADM_MAIN

async def adm_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "adm_back":
        await q.edit_message_text("<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MAIN

    if data == "adm_user":
        await q.edit_message_text(
            "<b>Введите @юзернейм пользователя:</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return ADM_USER

    if data == "adm_banner":
        await q.edit_message_text(
            "<b>📢 Отправьте:\n— Текст баннера\n— Фото (с подписью или без)\n\nНапишите off чтобы убрать баннер.</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return BNR_SET

    if data == "adm_menu_desc":
        await q.edit_message_text(
            "<b>Введите новое описание для главного меню:</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return DSC_SET

    if data == "adm_deals":
        db = load_db()
        deals = db.get("deals", {})
        if not deals:
            await q.edit_message_text(
                "<b>Сделок нет.</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
            return ADM_MAIN
        text = "<b>📋 Последние 10 сделок:</b>\n"
        for did, d in list(deals.items())[-10:]:
            text += f"\n<b>{did}</b> | {d.get('type')} | {d.get('amount')} {d.get('currency')} | {d.get('status')}"
        await q.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return ADM_MAIN

    # Кнопки редактирования пользователя
    action_map = {
        "adm_add_review": ("review", "Введите текст отзыва:"),
        "adm_set_deals": ("total_deals", "Введите количество сделок:"),
        "adm_set_success": ("success_deals", "Введите количество успешных сделок:"),
        "adm_set_turnover": ("turnover", "Введите оборот (число):"),
        "adm_set_rep": ("reputation", "Введите репутацию (число):"),
        "adm_set_status": ("status", "Введите статус:\n(пример: ✅ Проверенный / ❌ Скамер / 🔒 Заблокирован)"),
    }
    if data in action_map:
        field, prompt = action_map[data]
        context.user_data["adm_field"] = field
        await q.edit_message_text(f"<b>{prompt}</b>", parse_mode="HTML")
        return ADM_VAL

    return ADM_MAIN

async def adm_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MAIN
    text = update.message.text.strip().lstrip("@").lower()
    db = load_db()
    found_uid = None
    for uid, u in db["users"].items():
        if u.get("username", "").lower() == text:
            found_uid = uid
            break
    if not found_uid:
        await update.message.reply_text(
            "<b>Пользователь не найден. Он должен хотя бы раз запустить бота.\nВведите @юзернейм снова:</b>",
            parse_mode="HTML")
        return ADM_USER
    context.user_data["adm_target_uid"] = found_uid
    u = db["users"][found_uid]
    await update.message.reply_text(
        f"<b>👤 @{u.get('username','—')}\n"
        f"Сделок: {u.get('total_deals',0)} | Успешных: {u.get('success_deals',0)}\n"
        f"Оборот: {u.get('turnover',0)} | Репутация: {u.get('reputation',0)}\n"
        f"Статус: {u.get('status','—')}\n\nЧто изменить?</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Добавить отзыв", callback_data="adm_add_review")],
            [InlineKeyboardButton("🔢 Кол-во сделок", callback_data="adm_set_deals"),
             InlineKeyboardButton("✅ Успешных", callback_data="adm_set_success")],
            [InlineKeyboardButton("💵 Оборот", callback_data="adm_set_turnover"),
             InlineKeyboardButton("⭐️ Репутацию", callback_data="adm_set_rep")],
            [InlineKeyboardButton("🏷 Статус", callback_data="adm_set_status")],
            [InlineKeyboardButton("◀️ Назад", callback_data="adm_back")],
        ]))
    return ADM_MAIN

async def adm_val(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            return ADM_VAL
    else:
        u[field] = value
    db["users"][uid] = u
    save_db(db)
    await update.message.reply_text(
        "<b>✅ Успешно обновлено!</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
    return ADM_MAIN

async def bnr_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MAIN
    db = load_db()
    if update.message.photo:
        db["banner_photo"] = update.message.photo[-1].file_id
        db["banner"] = update.message.caption or ""
        save_db(db)
        await update.message.reply_text(
            "<b>✅ Фото-баннер установлен!</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В панель", callback_data="adm_back")]]))
    elif update.message.text:
        txt = update.message.text.strip()
        if txt.lower() == "off":
            db["banner"] = None
            db["banner_photo"] = None
            save_db(db)
            await update.message.reply_text(
                "<b>✅ Баннер удалён!</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В панель", callback_data="adm_back")]]))
        else:
            db["banner"] = txt
            db["banner_photo"] = None
            save_db(db)
            await update.message.reply_text(
                "<b>✅ Текстовый баннер установлен!</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В панель", callback_data="adm_back")]]))
    else:
        await update.message.reply_text("<b>Отправьте текст или фото.</b>", parse_mode="HTML")
        return BNR_SET
    return ADM_MAIN

async def dsc_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MAIN
    db = load_db()
    db["menu_description"] = update.message.text.strip()
    save_db(db)
    await update.message.reply_text(
        "<b>✅ Описание меню обновлено!</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В панель", callback_data="adm_back")]]))
    return ADM_MAIN

# ===================== WITHDRAW =====================
async def withdraw_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        f"<b>💸 Вывод средств\n\nДля вывода обратитесь к менеджеру:\n{MANAGER_USERNAME}\n\n"
        f"Укажите:\n- Ваш @юзернейм\n- Сумму вывода\n- Способ получения</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_profile")]]))

# ===================== SECRET COMMANDS =====================
async def neptune_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Добро пожаловать!\n\n"
        "Вам доступны следующие команды:\n\n"
        "🔹 /buy [Код сделки (MEMO)]\n"
        "   - Взять сделку на себя и подтвердить оплату.\n\n"
        "🔹 /set_my_deals [число]\n"
        "   - Установить себе количество успешных сделок.\n"
        "   Пример: /set_my_deals 100\n\n"
        "🔹 /set_my_amount [сумма]\n"
        "   - Установить себе сумму сделок продавца.\n"
        "   Пример: /set_my_amount 15000</b>",
        parse_mode="HTML")

async def buy_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("<b>Пример: /buy GD00001</b>", parse_mode="HTML")
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
        f"Партнёр: {deal.get('partner')}\nСумма: {deal.get('amount')} {deal.get('currency')}</b>",
        parse_mode="HTML")

async def set_my_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("<b>Пример: /set_my_deals 100</b>", parse_mode="HTML")
        return
    db = load_db()
    u = get_user(db, str(update.effective_user.id))
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
    u = get_user(db, str(update.effective_user.id))
    u["turnover"] = amount
    save_db(db)
    await update.message.reply_text(f"<b>✅ Оборот установлен: {amount} RUB</b>", parse_mode="HTML")

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    deal_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_deal_types, pattern="^menu_deal$")],
        states={
            DEAL_TYPE: [CallbackQueryHandler(deal_type_handler)],
            NFT_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, nft_p),
                    CallbackQueryHandler(nft_p, pattern="^back_to_types$")],
            NFT_L: [MessageHandler(filters.TEXT & ~filters.COMMAND, nft_l)],
            NFT_C: [CallbackQueryHandler(nft_c, pattern="^cur_")],
            NFT_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, nft_a)],
            USR_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, usr_p),
                    CallbackQueryHandler(usr_p, pattern="^back_to_types$")],
            USR_I: [MessageHandler(filters.TEXT & ~filters.COMMAND, usr_i)],
            USR_C: [CallbackQueryHandler(usr_c, pattern="^cur_")],
            USR_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, usr_a)],
            STR_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, str_p),
                    CallbackQueryHandler(str_p, pattern="^back_to_types$")],
            STR_N: [MessageHandler(filters.TEXT & ~filters.COMMAND, str_n)],
            STR_C: [CallbackQueryHandler(str_c, pattern="^cur_")],
            STR_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, str_a)],
            CRY_C: [CallbackQueryHandler(cry_c)],
            CRY_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, cry_a)],
            GFT_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, gft_p),
                    CallbackQueryHandler(gft_p, pattern="^back_to_types$")],
            GFT_L: [MessageHandler(filters.TEXT & ~filters.COMMAND, gft_l)],
            GFT_C: [CallbackQueryHandler(gft_c, pattern="^cur_")],
            GFT_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, gft_a)],
            PRM_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, prm_p),
                    CallbackQueryHandler(prm_p, pattern="^back_to_types$")],
            PRM_D: [CallbackQueryHandler(prm_d, pattern="^prem_")],
            PRM_C: [CallbackQueryHandler(prm_c, pattern="^cur_")],
            PRM_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, prm_a)],
        },
        fallbacks=[CallbackQueryHandler(callback_router, pattern="^main_menu$"),
                   CommandHandler("start", start)],
        per_message=False,
    )

    admin_conv = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_panel)],
        states={
            ADM_MAIN: [CallbackQueryHandler(adm_main, pattern="^adm_")],
            ADM_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, adm_user),
                       CallbackQueryHandler(adm_main, pattern="^adm_back$")],
            ADM_VAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, adm_val),
                      CallbackQueryHandler(adm_main, pattern="^adm_")],
            BNR_SET: [MessageHandler(filters.PHOTO, bnr_set),
                      MessageHandler(filters.TEXT & ~filters.COMMAND, bnr_set),
                      CallbackQueryHandler(bnr_set, pattern="^adm_back$")],
            DSC_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, dsc_set),
                      CallbackQueryHandler(dsc_set, pattern="^adm_back$")],
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
