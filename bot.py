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
BOT_TOKEN = "ВСТАВЬТЕ_НОВЫЙ_ТОКЕН_СЮДА"
ADMIN_ID = 174415647
BOT_USERNAME = "GiftDealsRoBot"
MANAGER_USERNAME = "@GiftDealsManager"
CRYPTO_ADDRESS = "UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc"
CRYPTO_BOT_LINK = "https://t.me/send?start=IVtoVqCXSHV0"
DB_FILE = "db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "deals": {}, "banner": None, "banner_photo": None, "banner_video": None, "menu_description": None, "deal_counter": 1}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(db, user_id):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "username": "", "balance": 0, "total_deals": 0, "success_deals": 0,
            "turnover": 0, "reputation": 0, "reviews": [], "status": "", "lang": "ru"
        }
    return db["users"][uid]

LANGS = {
    "ru": "RU Русский", "en": "EN English", "kz": "KZ Казахский",
    "az": "AZ Азербайджанский", "uz": "UZ Узбекский", "kg": "KG Кыргызский",
    "tj": "TJ Таджикский", "by": "BY Белорусский",
}

WELCOME_TEXT = {
    "ru": (
        "Gift Deals — одна из самых безопасных площадок в Telegram для проведения сделок.\n\n"
        "Мы гарантируем честность каждой транзакции: средства и товар передаются только после подтверждения обеих сторон. "
        "Никаких рисков, никаких мошенников — только надёжные сделки под защитой нашей платформы.\n\n"
        "Тысячи успешных сделок уже позади — и каждая из них прошла безопасно."
    ),
    "en": "Gift Deals is one of the safest platforms in Telegram. We guarantee honest transactions.",
    "kz": "Gift Deals — Telegram-дағы мәмілелер жүргізу үшін ең қауіпсіз алаңдардың бірі.",
    "az": "Gift Deals — Telegram-da ən təhlükəsiz platformalardan biridir.",
    "uz": "Gift Deals — Telegram'da eng xavfsiz platformalardan biri.",
    "kg": "Gift Deals — Telegram'дагы эң коопсуз аянтча.",
    "tj": "Gift Deals — яке аз бехтарин майдончаҳо дар Telegram.",
    "by": "Gift Deals — адна з самых бяспечных пляцовак у Telegram.",
}

BTN = {
    "ru": {"deal": "Создать сделку", "support": "Поддержка", "balance": "Пополнить баланс",
           "lang": "Сменить язык", "profile": "Профиль", "top": "Топ продавцов"},
    "en": {"deal": "Create Deal", "support": "Support", "balance": "Top Up",
           "lang": "Language", "profile": "Profile", "top": "Top Sellers"},
    "kz": {"deal": "Мәміле жасау", "support": "Қолдау", "balance": "Балансты толтыру",
           "lang": "Тілді өзгерту", "profile": "Профиль", "top": "Үздік сатушылар"},
    "az": {"deal": "Müqavilə yarat", "support": "Dəstək", "balance": "Balansı artır",
           "lang": "Dili dəyiş", "profile": "Profil", "top": "Top satıcılar"},
    "uz": {"deal": "Bitim yaratish", "support": "Qollab-quvvatlash", "balance": "Balansni toldirish",
           "lang": "Tilni ozgartirish", "profile": "Profil", "top": "Top sotuvchilar"},
    "kg": {"deal": "Butum tuzuu", "support": "Koldoo", "balance": "Balans tolturuu",
           "lang": "Tildi ozgoruu", "profile": "Profil", "top": "Top satuuchular"},
    "tj": {"deal": "Ejodi muomila", "support": "Dastgiri", "balance": "Pur kardani balans",
           "lang": "Taghyiri zabon", "profile": "Profil", "top": "Behtarin furushandagon"},
    "by": {"deal": "Stvaryts zdzelku", "support": "Padtrymka", "balance": "Papounits balans",
           "lang": "Zmyanits movu", "profile": "Profil", "top": "Top pradavcou"},
}

def get_btn(lang, key):
    return BTN.get(lang, BTN["ru"]).get(key, BTN["ru"][key])

def currency_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("TON", callback_data="cur_ton"),
         InlineKeyboardButton("USDT", callback_data="cur_usdt")],
        [InlineKeyboardButton("RUB", callback_data="cur_rub"),
         InlineKeyboardButton("Stars", callback_data="cur_stars")],
        [InlineKeyboardButton("KZT (Тенге)", callback_data="cur_kzt"),
         InlineKeyboardButton("AZN (Манат)", callback_data="cur_azn")],
        [InlineKeyboardButton("KGS (Сом)", callback_data="cur_kgs"),
         InlineKeyboardButton("UZS (Сум)", callback_data="cur_uzs")],
        [InlineKeyboardButton("TJS (Сомони)", callback_data="cur_tjs"),
         InlineKeyboardButton("BYN (Рубль)", callback_data="cur_byn")],
        [InlineKeyboardButton("UAH (Гривна)", callback_data="cur_uah"),
         InlineKeyboardButton("GEL (Лари)", callback_data="cur_gel")],
    ])

CURRENCY_MAP = {
    "cur_ton": "TON", "cur_usdt": "USDT", "cur_rub": "RUB", "cur_stars": "Stars",
    "cur_kzt": "KZT", "cur_azn": "AZN", "cur_kgs": "KGS", "cur_uzs": "UZS",
    "cur_tjs": "TJS", "cur_byn": "BYN", "cur_uah": "UAH", "cur_gel": "GEL",
}

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

def gen_deal_id(db):
    did = db.get("deal_counter", 1)
    db["deal_counter"] = did + 1
    save_db(db)
    return "GD{:05d}".format(did)

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_to_types")]])

def main_menu_keyboard(lang="ru"):
    b = BTN.get(lang, BTN["ru"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ " + b["deal"], callback_data="menu_deal")],
        [InlineKeyboardButton("🆘 " + b["support"], url="https://t.me/GiftDealsSupport"),
         InlineKeyboardButton("➕ " + b["balance"], callback_data="menu_balance")],
        [InlineKeyboardButton("🔄 " + b["lang"], callback_data="menu_lang"),
         InlineKeyboardButton("👤 " + b["profile"], callback_data="menu_profile")],
        [InlineKeyboardButton("🏆 " + b["top"], callback_data="menu_top")],
    ])

async def send_main_menu(update, context, edit=False):
    db = load_db()
    uid = update.effective_user.id
    user = get_user(db, uid)
    lang = user.get("lang", "ru")
    banner = db.get("banner")
    banner_photo = db.get("banner_photo")
    banner_video = db.get("banner_video")
    menu_desc = db.get("menu_description")
    body = menu_desc if menu_desc else WELCOME_TEXT.get(lang, WELCOME_TEXT["ru"])
    text = "<b>💎 Gift Deals\n\n{}</b>".format(body)
    if banner:
        text = text + "\n\n<b>{}</b>".format(banner)
    kb = main_menu_keyboard(lang)
    if banner_video:
        await update.effective_message.reply_video(video=banner_video, caption=text, parse_mode="HTML", reply_markup=kb)
    elif banner_photo:
        await update.effective_message.reply_photo(photo=banner_photo, caption=text, parse_mode="HTML", reply_markup=kb)
    elif edit:
        try:
            await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)

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
                "nft": "NFT", "username": "НФТ Юзернейм",
                "stars": "Звёзды", "crypto": "Крипта",
                "giftbox": "НФТ Подарок", "premium": "Telegram Premium",
            }
            dd = d.get("data", {})
            extra = ""
            if d.get("type") in ("nft", "giftbox"):
                extra = "\n<b>Ссылка НФТ:</b> {}".format(dd.get("nft_link", "—"))
            elif d.get("type") == "username":
                extra = "\n<b>Юзернейм товара:</b> {}".format(dd.get("trade_username", "—"))
            elif d.get("type") == "stars":
                extra = "\n<b>Количество звёзд:</b> {}".format(dd.get("stars_count", "—"))
            elif d.get("type") == "premium":
                extra = "\n<b>Срок Premium:</b> {}".format(dd.get("premium_period", "—"))
            status_map = {"pending": "⏳ Ожидает оплаты", "confirmed": "✅ Подтверждена"}
            dtype = d.get("type", "")
            currency = d.get("currency", "—")
            # Build payment instruction based on deal type and currency
            if dtype in ("nft", "stars", "giftbox", "premium"):
                pay_info = "<b>📤 Куда отправить оплату:</b>\n<b>Менеджер:</b> @GiftDealsManager\n<b>Укажите MEMO:</b> <code>{}</code>".format(deal_id)
            else:  # username, crypto
                pay_info = ("<b>📤 Куда отправить оплату:</b>\n"
                    "<b>Адрес TON (TonKeeper):</b>\n"
                    "<code>{}</code>\n"
                    "<b>В комментарии/MEMO укажите:</b> <code>{}</code>").format(CRYPTO_ADDRESS, deal_id)
            text = (
                "<b>📋 Сделка найдена!\n\n"
                "Код (MEMO):</b> <code>{}</code>\n"
                "<b>Тип:</b> {}\n"
                "<b>Партнёр:</b> {}"
                "{}\n"
                "<b>Валюта:</b> {}\n"
                "<b>Сумма:</b> {}\n"
                "<b>Статус:</b> {}\n"
                "<b>Создана:</b> {}\n\n"
                "{}"
            ).format(
                deal_id,
                type_names.get(d.get("type"), d.get("type", "—")),
                d.get("partner", "—"),
                extra,
                d.get("currency", "—"),
                d.get("amount", "—"),
                status_map.get(d.get("status", ""), d.get("status", "—")),
                d.get("created", "—")[:16].replace("T", " "),
                pay_info
            )
            await update.effective_message.reply_text(
                text, parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))
            return
        else:
            await update.effective_message.reply_text(
                "<b>Сделка {} не найдена.</b>".format(deal_id), parse_mode="HTML")
    await send_main_menu(update, context)

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
            "<b>✏️ Создать сделку\n\nВыберите тип товара:</b>", parse_mode="HTML", reply_markup=kb)
    except Exception:
        await update.effective_message.reply_text(
            "<b>✏️ Создать сделку\n\nВыберите тип товара:</b>", parse_mode="HTML", reply_markup=kb)
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
            "<b>🖼 НФТ\n\nВведите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML", reply_markup=back_kb())
        return DEAL_NFT_PARTNER
    if data == "deal_username":
        context.user_data["deal_type"] = "username"
        await q.edit_message_text(
            "<b>👤 НФТ Юзернейм\n\nВведите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML", reply_markup=back_kb())
        return DEAL_USERNAME_PARTNER
    if data == "deal_stars":
        context.user_data["deal_type"] = "stars"
        await q.edit_message_text(
            "<b>⭐️ Звёзды\n\nВведите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML", reply_markup=back_kb())
        return DEAL_STARS_PARTNER
    if data == "deal_crypto":
        context.user_data["deal_type"] = "crypto"
        await q.edit_message_text(
            "<b>💎 Крипта\n\nВыберите: TON или $?</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 TON", callback_data="crypto_ton"),
                 InlineKeyboardButton("💵 $ (USDT)", callback_data="crypto_usdt")],
                [InlineKeyboardButton("◀️ Назад", callback_data="back_to_types")],
            ]))
        return DEAL_CRYPTO_CURRENCY
    if data == "deal_giftbox":
        context.user_data["deal_type"] = "giftbox"
        await q.edit_message_text(
            "<b>🎁 НФТ Подарок\n\nВведите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML", reply_markup=back_kb())
        return DEAL_GIFTBOX_PARTNER
    if data == "deal_premium":
        context.user_data["deal_type"] = "premium"
        await q.edit_message_text(
            "<b>✈️ Telegram Premium\n\nВведите юзернейм партнёра:\n(пример: @username)</b>",
            parse_mode="HTML", reply_markup=back_kb())
        return DEAL_PREMIUM_PARTNER
    return DEAL_TYPE

# NFT
async def deal_nft_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    p = update.message.text.strip()
    if not p.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return DEAL_NFT_PARTNER
    context.user_data["partner"] = p
    await update.message.reply_text(
        "<b>🖼 НФТ\n\nВведите ссылку на НФТ:\n(должна начинаться с https://)</b>",
        parse_mode="HTML")
    return DEAL_NFT_LINK

async def deal_nft_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    link = update.message.text.strip()
    if not link.startswith("https://"):
        await update.message.reply_text("<b>Ссылка должна начинаться с https://</b>", parse_mode="HTML")
        return DEAL_NFT_LINK
    context.user_data["nft_link"] = link
    await update.message.reply_text(
        "<b>🖼 НФТ\n\nВыберите валюту оплаты:</b>",
        parse_mode="HTML", reply_markup=currency_keyboard())
    return DEAL_NFT_CURRENCY

async def deal_nft_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text("<b>🖼 НФТ\n\nВведите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_NFT_AMOUNT

async def deal_nft_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# USERNAME
async def deal_username_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    p = update.message.text.strip()
    if not p.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return DEAL_USERNAME_PARTNER
    context.user_data["partner"] = p
    await update.message.reply_text(
        "<b>👤 НФТ Юзернейм\n\nВведите юзернейм товара:\n(пример: @username)</b>",
        parse_mode="HTML")
    return DEAL_USERNAME_INPUT

async def deal_username_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uname = update.message.text.strip()
    if not uname.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return DEAL_USERNAME_INPUT
    context.user_data["trade_username"] = uname
    await update.message.reply_text(
        "<b>👤 НФТ Юзернейм\n\nВыберите валюту оплаты:</b>",
        parse_mode="HTML", reply_markup=currency_keyboard())
    return DEAL_USERNAME_CURRENCY

async def deal_username_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text("<b>👤 НФТ Юзернейм\n\nВведите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_USERNAME_AMOUNT

async def deal_username_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# STARS
async def deal_stars_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    p = update.message.text.strip()
    if not p.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return DEAL_STARS_PARTNER
    context.user_data["partner"] = p
    await update.message.reply_text(
        "<b>⭐️ Звёзды\n\nВведите количество звёзд:</b>",
        parse_mode="HTML")
    return DEAL_STARS_COUNT

async def deal_stars_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = update.message.text.strip()
    if not count.isdigit():
        await update.message.reply_text("<b>Введите только цифры:</b>", parse_mode="HTML")
        return DEAL_STARS_COUNT
    context.user_data["stars_count"] = count
    await update.message.reply_text(
        "<b>⭐️ Звёзды\n\nВыберите валюту оплаты:</b>",
        parse_mode="HTML", reply_markup=currency_keyboard())
    return DEAL_STARS_CURRENCY

async def deal_stars_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text("<b>⭐️ Звёзды\n\nВведите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_STARS_AMOUNT

async def deal_stars_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# CRYPTO
async def deal_crypto_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "back_to_types":
        await show_deal_types(update, context)
        return DEAL_TYPE
    cur_map = {"crypto_ton": "TON", "crypto_usdt": "USDT"}
    cur = cur_map.get(q.data, q.data)
    context.user_data["currency"] = cur
    await q.edit_message_text(
        "<b>💎 Крипта ({})\n\nВведите сумму сделки:</b>".format(cur),
        parse_mode="HTML")
    return DEAL_CRYPTO_AMOUNT

async def deal_crypto_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    context.user_data["partner"] = "—"
    await finalize_deal(update, context)
    return ConversationHandler.END

# GIFTBOX
async def deal_giftbox_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    p = update.message.text.strip()
    if not p.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return DEAL_GIFTBOX_PARTNER
    context.user_data["partner"] = p
    await update.message.reply_text(
        "<b>🎁 НФТ Подарок\n\nВведите ссылку на подарок:\n(должна начинаться с https://)</b>",
        parse_mode="HTML")
    return DEAL_GIFTBOX_LINK

async def deal_giftbox_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    if not link.startswith("https://"):
        await update.message.reply_text("<b>Ссылка должна начинаться с https://</b>", parse_mode="HTML")
        return DEAL_GIFTBOX_LINK
    context.user_data["nft_link"] = link
    await update.message.reply_text(
        "<b>🎁 НФТ Подарок\n\nВыберите валюту оплаты:</b>",
        parse_mode="HTML", reply_markup=currency_keyboard())
    return DEAL_GIFTBOX_CURRENCY

async def deal_giftbox_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text("<b>🎁 НФТ Подарок\n\nВведите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_GIFTBOX_AMOUNT

async def deal_giftbox_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# PREMIUM
async def deal_premium_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    p = update.message.text.strip()
    if not p.startswith("@"):
        await update.message.reply_text("<b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return DEAL_PREMIUM_PARTNER
    context.user_data["partner"] = p
    await update.message.reply_text(
        "<b>✈️ Telegram Premium\n\nВыберите срок подписки:</b>",
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
        "<b>✈️ Telegram Premium\n\nВыберите валюту оплаты:</b>",
        parse_mode="HTML", reply_markup=currency_keyboard())
    return DEAL_PREMIUM_CURRENCY

async def deal_premium_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text("<b>✈️ Telegram Premium\n\nВведите сумму сделки:</b>", parse_mode="HTML")
    return DEAL_PREMIUM_AMOUNT

async def deal_premium_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# FINALIZE
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
        "nft": "🖼 НФТ", "username": "👤 НФТ Юзернейм",
        "stars": "⭐️ Звёзды", "crypto": "💎 Крипта",
        "giftbox": "🎁 НФТ Подарок", "premium": "✈️ Telegram Premium",
    }
    lines = [
        "<b>✅ Сделка успешно создана!</b>", "",
        "<b>Код сделки (MEMO):</b> <code>{}</code>".format(deal_id),
        "<b>Тип:</b> {}".format(type_names.get(deal_type, deal_type)),
        "<b>Партнёр:</b> {}".format(partner),
    ]
    if deal_type in ("nft", "giftbox"):
        lines.append("<b>Ссылка НФТ:</b> {}".format(ud.get("nft_link", "—")))
    elif deal_type == "username":
        lines.append("<b>Юзернейм товара:</b> {}".format(ud.get("trade_username", "—")))
    elif deal_type == "stars":
        lines.append("<b>Количество звёзд:</b> {}".format(ud.get("stars_count", "—")))
    elif deal_type == "premium":
        lines.append("<b>Срок Premium:</b> {}".format(ud.get("premium_period", "—")))
    lines += [
        "<b>Валюта:</b> {}".format(currency),
        "<b>Сумма:</b> {}".format(amount), "",
    ]
    if deal_type in ("nft", "stars", "giftbox"):
        lines += [
            "<b>📤 Куда отправить оплату:</b>",
            "<b>Менеджер:</b> {}".format(MANAGER_USERNAME),
            "<b>Напишите менеджеру MEMO:</b> <code>{}</code>".format(deal_id),
        ]
    elif deal_type in ("username", "crypto"):
        lines += [
            "<b>📤 Куда отправить оплату:</b>",
            "<b>Адрес TON (TonKeeper):</b>",
            "<code>{}</code>".format(CRYPTO_ADDRESS),
            "<b>В комментарии/MEMO укажите:</b> <code>{}</code>".format(deal_id),
        ]
    elif deal_type == "premium":
        lines += [
            "<b>📤 Куда отправить оплату:</b>",
            "<b>Менеджер:</b> {}".format(MANAGER_USERNAME),
            "<b>После оплаты Premium зачислят автоматически.</b>",
            "<b>Напишите менеджеру MEMO:</b> <code>{}</code>".format(deal_id),
        ]
    lines += [
        "",
        "<b>🔗 Ссылка на сделку:</b>",
        "<code>https://t.me/{}?start=deal_{}</code>".format(BOT_USERNAME, deal_id),
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
    # Notify partner if they are in db
    partner_username = partner.lstrip("@").lower() if partner and partner != "—" else None
    if partner_username:
        partner_uid = None
        for uid, u in db["users"].items():
            if u.get("username", "").lower() == partner_username:
                partner_uid = uid
                break
        if partner_uid:
            type_names2 = {
                "nft": "🖼 НФТ", "username": "👤 НФТ Юзернейм", "stars": "⭐️ Звёзды",
                "crypto": "💎 Крипта", "giftbox": "🎁 НФТ Подарок", "premium": "✈️ Telegram Premium",
            }
            if deal_type in ("nft", "stars", "giftbox", "premium"):
                pay_info_partner = (
                    "<b>📤 Куда отправить оплату:</b>\n"
                    "<b>Менеджер:</b> {}\n"
                    "<b>Укажите MEMO:</b> <code>{}</code>"
                ).format(MANAGER_USERNAME, deal_id)
            else:
                pay_info_partner = (
                    "<b>📤 Куда отправить оплату:</b>\n"
                    "<b>Адрес TON (TonKeeper):</b>\n"
                    "<code>{}</code>\n"
                    "<b>В комментарии/MEMO укажите:</b> <code>{}</code>"
                ).format(CRYPTO_ADDRESS, deal_id)
            notify_text = (
                "<b>🔔 Вас добавили в сделку!</b>\n\n"
                "<b>Код (MEMO):</b> <code>{}</code>\n"
                "<b>Тип:</b> {}\n"
                "<b>Инициатор:</b> @{}\n"
                "<b>Валюта:</b> {}\n"
                "<b>Сумма:</b> {}\n\n"
                "{}"
            ).format(
                deal_id,
                type_names2.get(deal_type, deal_type),
                user.username or str(user.id),
                currency, amount,
                pay_info_partner
            )
            try:
                await context.bot.send_message(
                    chat_id=int(partner_uid), text=notify_text, parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))
            except Exception:
                pass
    context.user_data.clear()

# BALANCE
async def show_balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "<b>➕ Пополнение баланса\n\nВыберите способ:</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐️ Звёзды", callback_data="balance_stars")],
            [InlineKeyboardButton("💴 Рубли", callback_data="balance_rub")],
            [InlineKeyboardButton("💎 TON / USDT", callback_data="balance_crypto")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
        ]))

async def show_balance_info(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    uid = update.effective_user.id
    if method == "stars":
        text = "<b>⭐️ Пополнение звёздами\n\nМенеджер: {}\n\nПосле подтверждения баланс зачислится.</b>".format(MANAGER_USERNAME)
    elif method == "rub":
        text = (
            "<b>💴 Пополнение рублями\n\n"
            "Переводите на номер ВТБ:\n"
            "<code>89041751408</code>\n"
            "Получатель: Александр Ф.\n\n"
            "После перевода напишите менеджеру: {}\n"
            "Приложите скриншот — баланс зачислят вручную.</b>"
        ).format(MANAGER_USERNAME)
    elif method == "crypto":
        text = "<b>💎 Пополнение TON / USDT\n\nАдрес TON (TonKeeper):\n<code>{}</code>\n\nКрипто бот:\n{}\n\nВаш ID: <code>{}</code></b>".format(
            CRYPTO_ADDRESS, CRYPTO_BOT_LINK, uid)
    else:
        text = "<b>Неизвестный метод</b>"
    await update.callback_query.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_balance")]]))

# LANGUAGE
async def show_lang_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons, row = [], []
    for code, name in LANGS.items():
        row.append(InlineKeyboardButton(name, callback_data="lang_{}".format(code)))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
    await update.callback_query.edit_message_text(
        "<b>🔄 Выберите язык:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    db = load_db()
    user = get_user(db, update.effective_user.id)
    user["lang"] = lang
    save_db(db)
    await update.callback_query.answer("Язык изменён!")
    await send_main_menu(update, context, edit=True)

# PROFILE
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    uid = update.effective_user.id
    user = get_user(db, uid)
    uname = update.effective_user.username or "—"
    status_line = "\n🏷 Статус: {}".format(user["status"]) if user.get("status") else ""
    reviews = user.get("reviews", [])
    reviews_text = ("\n\n<b>📝 Отзывы:</b>\n" + "\n".join(["• {}".format(r) for r in reviews[-5:]])) if reviews else ""
    text = (
        "<b>👤 Профиль пользователя{}\n\n"
        "📱 Юзернейм: @{}\n"
        "💰 Баланс: {} RUB\n"
        "📊 Всего сделок: {}\n"
        "✅ Успешных сделок: {}\n"
        "💵 Оборот: {} RUB\n"
        "⭐️ Репутация: {}</b>{}"
    ).format(
        status_line, uname,
        user.get("balance", 0), user.get("total_deals", 0),
        user.get("success_deals", 0), user.get("turnover", 0),
        user.get("reputation", 0), reviews_text
    )
    await update.callback_query.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Пополнить баланс", callback_data="menu_balance"),
             InlineKeyboardButton("💸 Вывод средств", callback_data="withdraw")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
        ]))

# TOP
async def show_top_sellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    TOP = [
        ("@al***ndr", 450, 47), ("@ie***ym", 380, 38), ("@ma***ov", 310, 29),
        ("@kr***na", 290, 31), ("@pe***ko", 270, 25), ("@se***ev", 240, 22),
        ("@an***va", 210, 19), ("@vi***or", 190, 17), ("@dm***iy", 170, 15), ("@ni***la", 140, 13),
    ]
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    lines = ["<b>🏆 Топ продавцов Gift Deals\n</b>"]
    for i, (uname, amount, deals) in enumerate(TOP):
        lines.append("<b>{} {}. {} — ${} | {} сделок</b>".format(medals[i], i+1, uname, amount, deals))
    lines.append("\n<b>Хочешь попасть в топ? Создавай сделки!</b>")
    await update.callback_query.edit_message_text(
        "\n".join(lines), parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]))

# WITHDRAW
async def withdraw_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "<b>💸 Вывод средств\n\nМенеджер: {}\n\nУкажите:\n— Ваш @юзернейм\n— Сумму вывода\n— Способ получения</b>".format(MANAGER_USERNAME),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_profile")]]))

# ADMIN
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
    await update.message.reply_text("<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
    return ADMIN_ACTION

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
            "<b>Введите @юзернейм пользователя:</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return ADMIN_SET_USER
    if data == "adm_banner":
        await q.edit_message_text(
            "<b>📢 Установить баннер\n\nОтправьте:\n— Фото (с подписью или без)\n— Видео (с подписью или без)\n— Текст\n\nЧтобы убрать баннер — напишите: off</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return BANNER_SET
    if data == "adm_menu_desc":
        await q.edit_message_text(
            "<b>Введите новое описание для главного меню:</b>", parse_mode="HTML",
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
            text += "\n<b>{}</b> | {} | {} {} | {}".format(did, d.get("type"), d.get("amount"), d.get("currency"), d.get("status"))
        await q.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return ADMIN_ACTION
    action_map = {
        "adm_add_review": ("review", "Введите текст отзыва:"),
        "adm_set_deals": ("total_deals", "Введите количество сделок:"),
        "adm_set_success": ("success_deals", "Введите количество успешных сделок:"),
        "adm_set_turnover": ("turnover", "Введите оборот (число):"),
        "adm_set_rep": ("reputation", "Введите репутацию (число):"),
        "adm_set_status": ("status", "Введите статус (✅ Проверенный / ❌ Скамер / 🔒 Заблокирован):"),
    }
    if data in action_map:
        field, prompt = action_map[data]
        context.user_data["adm_field"] = field
        await q.edit_message_text("<b>{}</b>".format(prompt), parse_mode="HTML")
        return ADMIN_SET_VALUE
    return ADMIN_ACTION

async def admin_set_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADMIN_ACTION
    username = update.message.text.strip().lstrip("@").lower()
    db = load_db()
    found_uid = next((uid for uid, u in db["users"].items() if u.get("username", "").lower() == username), None)
    if not found_uid:
        await update.message.reply_text("<b>Пользователь не найден. Он должен хотя бы раз запустить бота.</b>", parse_mode="HTML")
        return ADMIN_SET_USER
    context.user_data["adm_target_uid"] = found_uid
    u = db["users"][found_uid]
    await update.message.reply_text(
        "<b>👤 @{}\nСделок: {} | Успешных: {}\nОборот: {} | Репутация: {}\nСтатус: {}\n\nЧто изменить?</b>".format(
            u.get("username", "—"), u.get("total_deals", 0), u.get("success_deals", 0),
            u.get("turnover", 0), u.get("reputation", 0), u.get("status", "—")),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Добавить отзыв", callback_data="adm_add_review")],
            [InlineKeyboardButton("🔢 Кол-во сделок", callback_data="adm_set_deals"),
             InlineKeyboardButton("✅ Успешных", callback_data="adm_set_success")],
            [InlineKeyboardButton("💵 Оборот", callback_data="adm_set_turnover"),
             InlineKeyboardButton("⭐️ Репутация", callback_data="adm_set_rep")],
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
        "<b>✅ Успешно обновлено!</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
    return ADMIN_ACTION

async def banner_set_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("<b>🛠 Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADMIN_ACTION
    db = load_db()
    if update.message.photo:
        db["banner_photo"] = update.message.photo[-1].file_id
        db["banner_video"] = None
        db["banner"] = update.message.caption or ""
        save_db(db)
        await update.message.reply_text(
            "<b>✅ Фото-баннер установлен!</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
    elif update.message.video:
        db["banner_video"] = update.message.video.file_id
        db["banner_photo"] = None
        db["banner"] = update.message.caption or ""
        save_db(db)
        await update.message.reply_text(
            "<b>✅ Видео-баннер установлен!</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
    elif update.message.text:
        text = update.message.text.strip()
        if text.lower() == "off":
            db["banner"] = None
            db["banner_photo"] = None
            db["banner_video"] = None
            save_db(db)
            await update.message.reply_text(
                "<b>✅ Баннер удалён!</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
        else:
            db["banner"] = text
            db["banner_photo"] = None
            db["banner_video"] = None
            save_db(db)
            await update.message.reply_text(
                "<b>✅ Текстовый баннер установлен!</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В админ панель", callback_data="adm_back")]]))
    else:
        await update.message.reply_text("<b>Отправьте текст, фото или видео.</b>", parse_mode="HTML")
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

# SECRET COMMANDS
async def neptune_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Добро пожаловать!\n\n"
        "Вам доступны следующие команды:\n\n"
        "🔹 /buy [Код сделки]\n"
        "   — Взять сделку на себя и подтвердить оплату.\n\n"
        "🔹 /set_my_deals [число]\n"
        "   — Установить себе количество успешных сделок.\n"
        "   Пример: /set_my_deals 100\n\n"
        "🔹 /set_my_amount [сумма]\n"
        "   — Установить себе сумму оборота.\n"
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
    u = get_user(db, update.effective_user.id)
    u["success_deals"] = u.get("success_deals", 0) + 1
    u["total_deals"] = u.get("total_deals", 0) + 1
    save_db(db)
    await update.message.reply_text(
        "<b>✅ Сделка {} подтверждена!\nПартнёр: {}\nСумма: {} {}</b>".format(
            deal_id, deal.get("partner"), deal.get("amount"), deal.get("currency")),
        parse_mode="HTML")

async def set_my_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("<b>Пример: /set_my_deals 100</b>", parse_mode="HTML")
        return
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["success_deals"] = int(args[0])
    u["total_deals"] = int(args[0])
    save_db(db)
    await update.message.reply_text("<b>✅ Установлено {} успешных сделок!</b>".format(args[0]), parse_mode="HTML")

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
    u = get_user(db, update.effective_user.id)
    u["turnover"] = amount
    save_db(db)
    await update.message.reply_text("<b>✅ Оборот установлен: {} RUB</b>".format(amount), parse_mode="HTML")

# MAIN
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    deal_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_deal_types, pattern="^menu_deal$")],
        states={
            DEAL_TYPE: [CallbackQueryHandler(deal_type_handler)],
            DEAL_NFT_PARTNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_nft_partner),
                CallbackQueryHandler(deal_nft_partner, pattern="^back_to_types$"),
            ],
            DEAL_NFT_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_nft_link),
                CallbackQueryHandler(deal_nft_link, pattern="^back_to_types$"),
            ],
            DEAL_NFT_CURRENCY: [CallbackQueryHandler(deal_nft_currency, pattern="^cur_")],
            DEAL_NFT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deal_nft_amount)],
            DEAL_USERNAME_PARTNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_username_partner),
                CallbackQueryHandler(deal_username_partner, pattern="^back_to_types$"),
            ],
            DEAL_USERNAME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deal_username_input)],
            DEAL_USERNAME_CURRENCY: [CallbackQueryHandler(deal_username_currency, pattern="^cur_")],
            DEAL_USERNAME_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deal_username_amount)],
            DEAL_STARS_PARTNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_stars_partner),
                CallbackQueryHandler(deal_stars_partner, pattern="^back_to_types$"),
            ],
            DEAL_STARS_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deal_stars_count)],
            DEAL_STARS_CURRENCY: [CallbackQueryHandler(deal_stars_currency, pattern="^cur_")],
            DEAL_STARS_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deal_stars_amount)],
            DEAL_CRYPTO_CURRENCY: [CallbackQueryHandler(deal_crypto_currency)],
            DEAL_CRYPTO_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deal_crypto_amount)],
            DEAL_GIFTBOX_PARTNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_giftbox_partner),
                CallbackQueryHandler(deal_giftbox_partner, pattern="^back_to_types$"),
            ],
            DEAL_GIFTBOX_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, deal_giftbox_link)],
            DEAL_GIFTBOX_CURRENCY: [CallbackQueryHandler(deal_giftbox_currency, pattern="^cur_")],
            DEAL_GIFTBOX_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deal_giftbox_amount)],
            DEAL_PREMIUM_PARTNER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deal_premium_partner),
                CallbackQueryHandler(deal_premium_partner, pattern="^back_to_types$"),
            ],
            DEAL_PREMIUM_PERIOD: [CallbackQueryHandler(deal_premium_period, pattern="^prem_")],
            DEAL_PREMIUM_CURRENCY: [CallbackQueryHandler(deal_premium_currency, pattern="^cur_")],
            DEAL_PREMIUM_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deal_premium_amount)],
        },
        fallbacks=[
            CallbackQueryHandler(callback_router, pattern="^main_menu$"),
            CommandHandler("start", start),
        ],
        per_message=False,
    )

    admin_conv = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_panel)],
        states={
            ADMIN_ACTION: [CallbackQueryHandler(admin_action_callback, pattern="^adm_")],
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
                MessageHandler(filters.VIDEO, banner_set_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, banner_set_handler),
                CallbackQueryHandler(banner_set_handler, pattern="^adm_back$"),
            ],
            MENU_DESC_SET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, menu_desc_set_handler),
                CallbackQueryHandler(menu_desc_set_handler, pattern="^adm_back$"),
            ],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("admin", admin_panel)],
        allow_reentry=True,
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

    print("Bot @{} started!".format(BOT_USERNAME))
    app.run_polling()

if __name__ == "__main__":
    main()
