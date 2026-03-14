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

# ===================== CONFIG =====================
BOT_TOKEN = "8636524725:AAHY7j6yHm5fo3H2uLFs9GzZbBQsPj5fLeY"
ADMIN_ID = 174415647
BOT_USERNAME = "GiftDealsRoBot"
MANAGER_USERNAME = "@GiftDealsManager"
CRYPTO_ADDRESS = "UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc"
CRYPTO_BOT_LINK = "https://t.me/send?start=IVtoVqCXSHV0"
DB_FILE = "db.json"

# ===================== ANIMATED EMOJI HELPER =====================
def ae(emoji_id, fallback):
    """Animated emoji tag for HTML parse_mode"""
    return f"<tg-emoji emoji-id='{emoji_id}'>{fallback}</tg-emoji>"

# Common animated emoji
AE = {
    "diamond":  ae("5447644880824181073", "💎"),
    "check":    ae("5445284367535759945", "✅"),
    "cross":    ae("5447354187759300341", "❌"),
    "fire":     ae("5422998492250386138", "🔥"),
    "star":     ae("5368324170671202286", "⭐"),
    "lock":     ae("5472354553527541051", "🔒"),
    "bell":     ae("5383165799791730254", "🔔"),
    "gift":     ae("5373026167722876724", "🎁"),
    "trophy":   ae("5373165539476767939", "🏆"),
    "shield":   ae("5472354553527541051", "🛡"),
    "rocket":   ae("5431815452437257407", "🚀"),
    "money":    ae("5451882697270755274", "💰"),
    "pencil":   ae("5431815452437257407", "✏️"),
    "globe":    ae("5440539497383087970", "🌍"),
    "nft":      ae("5409081890498491521", "🖼"),
    "user":     ae("5440539497383087970", "👤"),
    "premium":  ae("5383165799791730254", "✈️"),
    "deal":     ae("5267021122383086560", "🤝"),
    "hourglass":ae("5451882697270755274", "⏳"),
    "card":     ae("5368324170671202286", "💳"),
}

# ===================== DATABASE =====================
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "users": {}, "deals": {}, "banner": None,
        "banner_photo": None, "banner_video": None,
        "menu_description": None, "deal_counter": 1
    }

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

# ===================== LOCALIZATION =====================
# Languages: code -> (flag + name in native language)
LANGS = {
    "ru": "🇷🇺 Россия",
    "en": "🇬🇧 English",
    "kz": "🇰🇿 Қазақстан",
    "az": "🇦🇿 Azərbaycan",
    "uz": "🇺🇿 O'zbekiston",
    "kg": "🇰🇬 Кыргызстан",
    "tj": "🇹🇯 Тоҷикистон",
    "by": "🇧🇾 Беларусь",
    "am": "🇦🇲 Հայաստան",
    "ge": "🇬🇪 საქართველო",
    "ua": "🇺🇦 Україна",
    "md": "🇲🇩 Moldova",
}

WELCOME_TEXT = {
    "ru": "Gift Deals — одна из самых безопасных площадок в Telegram для сделок.\n\nГарантируем честность каждой транзакции. Никаких рисков — только надёжные сделки.",
    "en": "Gift Deals is one of the safest platforms in Telegram.\n\nWe guarantee honest transactions. No risks — only reliable deals.",
    "kz": "Gift Deals — Telegram-дағы ең қауіпсіз мәміле алаңдарының бірі.",
    "az": "Gift Deals — Telegram-da ən etibarlı əməliyyat platforması.",
    "uz": "Gift Deals — Telegram'dagi eng ishonchli bitim platformasi.",
    "kg": "Gift Deals — Telegram'дагы эң ишенимдүү бүтүм аянтчасы.",
    "tj": "Gift Deals — боэтимодтарин майдончаи муомилот дар Telegram.",
    "by": "Gift Deals — адна з самых надзейных пляцовак у Telegram.",
    "am": "Gift Deals — Telegram-ի ամենահուսալի գործարքային հարթակը:",
    "ge": "Gift Deals — Telegram-ის ყველაზე სანდო გარიგების პლატფორმა.",
    "ua": "Gift Deals — одна з найнадійніших платформ для угод у Telegram.",
    "md": "Gift Deals — una dintre cele mai de încredere platforme din Telegram.",
}

# Buttons in native language
BTN = {
    "ru": {"deal": "✏️ Создать сделку", "support": "🆘 Поддержка", "balance": "➕ Пополнить баланс", "lang": "🌍 Сменить язык", "profile": "👤 Профиль", "top": "🏆 Топ продавцов"},
    "en": {"deal": "✏️ Create Deal", "support": "🆘 Support", "balance": "➕ Top Up", "lang": "🌍 Language", "profile": "👤 Profile", "top": "🏆 Top Sellers"},
    "kz": {"deal": "✏️ Мәміле жасау", "support": "🆘 Қолдау", "balance": "➕ Баланс толтыру", "lang": "🌍 Тіл", "profile": "👤 Профиль", "top": "🏆 Үздіктер"},
    "az": {"deal": "✏️ Müqavilə yarat", "support": "🆘 Dəstək", "balance": "➕ Balans artır", "lang": "🌍 Dil", "profile": "👤 Profil", "top": "🏆 Top satıcılar"},
    "uz": {"deal": "✏️ Bitim yaratish", "support": "🆘 Qo'llab", "balance": "➕ Balans", "lang": "🌍 Til", "profile": "👤 Profil", "top": "🏆 Top"},
    "kg": {"deal": "✏️ Бүтүм түзүү", "support": "🆘 Колдоо", "balance": "➕ Баланс", "lang": "🌍 Тил", "profile": "👤 Профиль", "top": "🏆 Топ"},
    "tj": {"deal": "✏️ Муомила", "support": "🆘 Дастгирӣ", "balance": "➕ Баланс", "lang": "🌍 Забон", "profile": "👤 Профил", "top": "🏆 Беҳтарин"},
    "by": {"deal": "✏️ Здзелка", "support": "🆘 Падтрымка", "balance": "➕ Баланс", "lang": "🌍 Мова", "profile": "👤 Профіль", "top": "🏆 Топ"},
    "am": {"deal": "✏️ Գործարք", "support": "🆘 Օգնություն", "balance": "➕ Հաշիվ", "lang": "🌍 Լեզու", "profile": "👤 Պրոֆիլ", "top": "🏆 Լավագույն"},
    "ge": {"deal": "✏️ გარიგება", "support": "🆘 მხარდაჭერა", "balance": "➕ ბალანსი", "lang": "🌍 ენა", "profile": "👤 პროფილი", "top": "🏆 საუკეთესო"},
    "ua": {"deal": "✏️ Угода", "support": "🆘 Підтримка", "balance": "➕ Поповнити", "lang": "🌍 Мова", "profile": "👤 Профіль", "top": "🏆 Топ"},
    "md": {"deal": "✏️ Tranzacție", "support": "🆘 Suport", "balance": "➕ Sold", "lang": "🌍 Limbă", "profile": "👤 Profil", "top": "🏆 Top"},
}

def get_btn(lang, key):
    return BTN.get(lang, BTN["ru"]).get(key, BTN["ru"][key])

# Currency names in native languages
CURRENCY_NAMES = {
    "TON":   {"ru": "💎 TON", "en": "💎 TON", "kz": "💎 TON", "az": "💎 TON", "uz": "💎 TON", "kg": "💎 TON", "tj": "💎 TON", "by": "💎 TON", "am": "💎 TON", "ge": "💎 TON", "ua": "💎 TON", "md": "💎 TON"},
    "USDT":  {"ru": "💵 USDT", "en": "💵 USDT", "kz": "💵 USDT", "az": "💵 USDT", "uz": "💵 USDT", "kg": "💵 USDT", "tj": "💵 USDT", "by": "💵 USDT", "am": "💵 USDT", "ge": "💵 USDT", "ua": "💵 USDT", "md": "💵 USDT"},
    "Stars": {"ru": "⭐️ Звёзды", "en": "⭐️ Stars", "kz": "⭐️ Жұлдыздар", "az": "⭐️ Ulduzlar", "uz": "⭐️ Yulduzlar", "kg": "⭐️ Жылдыздар", "tj": "⭐️ Ситораҳо", "by": "⭐️ Зоркі", "am": "⭐️ Աստղեր", "ge": "⭐️ ვარსკვლავები", "ua": "⭐️ Зірки", "md": "⭐️ Stele"},
    "RUB":   {"ru": "🇷🇺 Рубли", "en": "🇷🇺 RUB", "kz": "🇷🇺 Рубль", "az": "🇷🇺 Rubl", "uz": "🇷🇺 Rubl", "kg": "🇷🇺 Рубль", "tj": "🇷🇺 Рубл", "by": "🇷🇺 Рублі", "am": "🇷🇺 Ռուբլի", "ge": "🇷🇺 რუბლი", "ua": "🇷🇺 Рублі", "md": "🇷🇺 Ruble"},
    "KZT":   {"ru": "🇰🇿 Тенге", "en": "🇰🇿 Tenge", "kz": "🇰🇿 Теңге", "az": "🇰🇿 Tenge", "uz": "🇰🇿 Tenge", "kg": "🇰🇿 Теңге", "tj": "🇰🇿 Тенге", "by": "🇰🇿 Тэнге", "am": "🇰🇿 Տենգե", "ge": "🇰🇿 ტენგე", "ua": "🇰🇿 Тенге", "md": "🇰🇿 Tenge"},
    "AZN":   {"ru": "🇦🇿 Манаты", "en": "🇦🇿 Manat", "kz": "🇦🇿 Манат", "az": "🇦🇿 Manat", "uz": "🇦🇿 Manat", "kg": "🇦🇿 Манат", "tj": "🇦🇿 Манат", "by": "🇦🇿 Манаты", "am": "🇦🇿 Մանաթ", "ge": "🇦🇿 მანათი", "ua": "🇦🇿 Манати", "md": "🇦🇿 Manat"},
    "KGS":   {"ru": "🇰🇬 Сомы", "en": "🇰🇬 Som", "kz": "🇰🇬 Сом", "az": "🇰🇬 Som", "uz": "🇰🇬 Som", "kg": "🇰🇬 Сом", "tj": "🇰🇬 Сом", "by": "🇰🇬 Сомы", "am": "🇰🇬 Սոմ", "ge": "🇰🇬 სომი", "ua": "🇰🇬 Соми", "md": "🇰🇬 Som"},
    "UZS":   {"ru": "🇺🇿 Сумы", "en": "🇺🇿 Sum", "kz": "🇺🇿 Сум", "az": "🇺🇿 Sum", "uz": "🇺🇿 So'm", "kg": "🇺🇿 Сум", "tj": "🇺🇿 Сум", "by": "🇺🇿 Сумы", "am": "🇺🇿 Սում", "ge": "🇺🇿 სუმი", "ua": "🇺🇿 Суми", "md": "🇺🇿 Sum"},
    "TJS":   {"ru": "🇹🇯 Сомони", "en": "🇹🇯 Somoni", "kz": "🇹🇯 Сомонӣ", "az": "🇹🇯 Somoni", "uz": "🇹🇯 Somoni", "kg": "🇹🇯 Сомонӣ", "tj": "🇹🇯 Сомонӣ", "by": "🇹🇯 Самані", "am": "🇹🇯 Սոմոնի", "ge": "🇹🇯 სომონი", "ua": "🇹🇯 Сомоні", "md": "🇹🇯 Somoni"},
    "BYN":   {"ru": "🇧🇾 Рубли BY", "en": "🇧🇾 BYN", "kz": "🇧🇾 Рубль BY", "az": "🇧🇾 Rubl BY", "uz": "🇧🇾 Rubl BY", "kg": "🇧🇾 Рубль BY", "tj": "🇧🇾 Рубл BY", "by": "🇧🇾 Рублі", "am": "🇧🇾 Ռուբլի BY", "ge": "🇧🇾 რუბლი BY", "ua": "🇧🇾 Рублі BY", "md": "🇧🇾 Ruble BY"},
    "UAH":   {"ru": "🇺🇦 Гривны", "en": "🇺🇦 Hryvnia", "kz": "🇺🇦 Гривна", "az": "🇺🇦 Qrivna", "uz": "🇺🇦 Grivna", "kg": "🇺🇦 Гривна", "tj": "🇺🇦 Гривна", "by": "🇺🇦 Грыўні", "am": "🇺🇦 Հրիվնա", "ge": "🇺🇦 გრივნა", "ua": "🇺🇦 Гривні", "md": "🇺🇦 Grivne"},
    "GEL":   {"ru": "🇬🇪 Лари", "en": "🇬🇪 Lari", "kz": "🇬🇪 Лари", "az": "🇬🇪 Lari", "uz": "🇬🇪 Lari", "kg": "🇬🇪 Лари", "tj": "🇬🇪 Лари", "by": "🇬🇪 Лары", "am": "🇬🇪 Լարի", "ge": "🇬🇪 ლარი", "ua": "🇬🇪 Ларі", "md": "🇬🇪 Lari"},
}

CURRENCY_MAP = {
    "cur_ton": "TON", "cur_usdt": "USDT", "cur_rub": "RUB", "cur_stars": "Stars",
    "cur_kzt": "KZT", "cur_azn": "AZN", "cur_kgs": "KGS", "cur_uzs": "UZS",
    "cur_tjs": "TJS", "cur_byn": "BYN", "cur_uah": "UAH", "cur_gel": "GEL",
}

def currency_keyboard(lang="ru"):
    def n(code): return CURRENCY_NAMES.get(code, {}).get(lang, code)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(n("TON"),  callback_data="cur_ton"),
         InlineKeyboardButton(n("USDT"), callback_data="cur_usdt")],
        [InlineKeyboardButton(n("RUB"),  callback_data="cur_rub"),
         InlineKeyboardButton(n("Stars"),callback_data="cur_stars")],
        [InlineKeyboardButton(n("KZT"),  callback_data="cur_kzt"),
         InlineKeyboardButton(n("AZN"),  callback_data="cur_azn")],
        [InlineKeyboardButton(n("KGS"),  callback_data="cur_kgs"),
         InlineKeyboardButton(n("UZS"),  callback_data="cur_uzs")],
        [InlineKeyboardButton(n("TJS"),  callback_data="cur_tjs"),
         InlineKeyboardButton(n("BYN"),  callback_data="cur_byn")],
        [InlineKeyboardButton(n("UAH"),  callback_data="cur_uah"),
         InlineKeyboardButton(n("GEL"),  callback_data="cur_gel")],
    ])

# ===================== STATES =====================
(
    DEAL_TYPE,
    NFT_P, NFT_L, NFT_C, NFT_A,
    USR_P, USR_I, USR_C, USR_A,
    STR_P, STR_N, STR_C, STR_A,
    CRY_C, CRY_A,
    PRM_P, PRM_D, PRM_C, PRM_A,
    ADM_MAIN, ADM_USER, ADM_VAL,
    BNR_SET, DSC_SET,
) = range(24)

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

def get_lang(update, db=None):
    if db is None:
        db = load_db()
    uid = update.effective_user.id
    return get_user(db, uid).get("lang", "ru")

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    db = load_db()
    user = update.effective_user
    u = get_user(db, user.id)
    lang = u.get("lang", "ru")
    menu_desc = db.get("menu_description")
    banner = db.get("banner")
    banner_photo = db.get("banner_photo")
    banner_video = db.get("banner_video")
    desc = menu_desc if menu_desc else WELCOME_TEXT.get(lang, WELCOME_TEXT["ru"])
    text = f"{AE['diamond']} <b>Gift Deals\n\n{desc}</b>"
    if banner:
        text += f"\n\n<b>{banner}</b>"
    kb = main_menu_kb(lang)
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
            await send_deal_card(update, context, deal_id, deals[deal_id], is_buyer=True)
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
    elif data == "menu_balance":
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
    elif data.startswith("paid_"):
        await paid_callback(update, context)
    elif data == "noop":
        pass
    elif data.startswith("adm_confirm_"):
        await admin_confirm_payment(update, context)
    elif data.startswith("adm_decline_"):
        await admin_decline_payment(update, context)

# ===================== DEAL TYPES =====================
def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back_to_types")]])

async def show_deal_types(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 НФТ", callback_data="deal_nft"),
         InlineKeyboardButton("👤 Юзернейм", callback_data="deal_username")],
        [InlineKeyboardButton("⭐️ Звёзды", callback_data="deal_stars"),
         InlineKeyboardButton("💎 Крипта", callback_data="deal_crypto")],
        [InlineKeyboardButton("✈️ Telegram Premium", callback_data="deal_premium")],
        [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
    ])
    msg = f"{AE['pencil']} <b>Создать сделку\n\nВыберите тип:</b>"
    try:
        await update.callback_query.edit_message_text(msg, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await update.effective_message.reply_text(msg, parse_mode="HTML", reply_markup=kb)
    return DEAL_TYPE

async def deal_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == "main_menu":
        context.user_data.clear()
        await send_main_menu(update, context, edit=True)
        return ConversationHandler.END
    if data in ("back_to_types", "menu_deal"):
        await show_deal_types(update, context)
        return DEAL_TYPE
    prompts = {
        "deal_nft":      ("nft",     f"{AE['nft']} <b>НФТ\n\nВведите @юзернейм партнёра:</b>",             NFT_P),
        "deal_username": ("username",f"{AE['user']} <b>Юзернейм\n\nВведите @юзернейм партнёра:</b>",        USR_P),
        "deal_stars":    ("stars",   f"{AE['star']} <b>Звёзды\n\nВведите @юзернейм партнёра:</b>",          STR_P),
        "deal_premium":  ("premium", f"{AE['premium']} <b>Telegram Premium\n\nВведите @юзернейм партнёра:</b>", PRM_P),
    }
    if data == "deal_crypto":
        context.user_data["deal_type"] = "crypto"
        await q.edit_message_text(
            f"{AE['diamond']} <b>Крипта\n\nВыберите валюту:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 TON", callback_data="crypto_ton"),
                 InlineKeyboardButton("💵 USDT", callback_data="crypto_usdt")],
                [InlineKeyboardButton("◀️ Назад", callback_data="back_to_types")],
            ]))
        return CRY_C
    if data in prompts:
        deal_type, msg, state = prompts[data]
        context.user_data["deal_type"] = deal_type
        await q.edit_message_text(msg, parse_mode="HTML", reply_markup=back_kb())
        return state
    return DEAL_TYPE

# ===================== NFT =====================
async def nft_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    p = update.message.text.strip()
    if not p.startswith("@"):
        await update.message.reply_text(f"{AE['cross']} <b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return NFT_P
    context.user_data["partner"] = p
    await update.message.reply_text(f"{AE['nft']} <b>НФТ\n\nВставьте ссылку на НФТ:\n(https://...)</b>", parse_mode="HTML")
    return NFT_L

async def nft_l(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    if not link.startswith("https://"):
        await update.message.reply_text(f"{AE['cross']} <b>Ссылка должна начинаться с https://</b>", parse_mode="HTML")
        return NFT_L
    context.user_data["nft_link"] = link
    lang = get_lang(update)
    await update.message.reply_text(f"{AE['nft']} <b>НФТ\n\nВыберите валюту:</b>", parse_mode="HTML", reply_markup=currency_keyboard(lang))
    return NFT_C

async def nft_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text(f"{AE['nft']} <b>НФТ\n\nВведите сумму сделки:</b>", parse_mode="HTML")
    return NFT_A

async def nft_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== USERNAME =====================
async def usr_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    p = update.message.text.strip()
    if not p.startswith("@"):
        await update.message.reply_text(f"{AE['cross']} <b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return USR_P
    context.user_data["partner"] = p
    await update.message.reply_text(f"{AE['user']} <b>Юзернейм\n\nВведите @юзернейм который продаёте:</b>", parse_mode="HTML")
    return USR_I

async def usr_i(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uname = update.message.text.strip()
    if not uname.startswith("@"):
        await update.message.reply_text(f"{AE['cross']} <b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return USR_I
    context.user_data["trade_username"] = uname
    lang = get_lang(update)
    await update.message.reply_text(f"{AE['user']} <b>Юзернейм\n\nВыберите валюту:</b>", parse_mode="HTML", reply_markup=currency_keyboard(lang))
    return USR_C

async def usr_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text(f"{AE['user']} <b>Юзернейм\n\nВведите сумму сделки:</b>", parse_mode="HTML")
    return USR_A

async def usr_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== STARS =====================
async def str_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    p = update.message.text.strip()
    if not p.startswith("@"):
        await update.message.reply_text(f"{AE['cross']} <b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return STR_P
    context.user_data["partner"] = p
    await update.message.reply_text(f"{AE['star']} <b>Звёзды\n\nСколько звёзд?</b>", parse_mode="HTML")
    return STR_N

async def str_n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = update.message.text.strip()
    if not count.isdigit():
        await update.message.reply_text(f"{AE['cross']} <b>Только цифры!</b>", parse_mode="HTML")
        return STR_N
    context.user_data["stars_count"] = count
    lang = get_lang(update)
    await update.message.reply_text(f"{AE['star']} <b>Звёзды\n\nВыберите валюту:</b>", parse_mode="HTML", reply_markup=currency_keyboard(lang))
    return STR_C

async def str_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text(f"{AE['star']} <b>Звёзды\n\nВведите сумму сделки:</b>", parse_mode="HTML")
    return STR_A

async def str_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== CRYPTO =====================
async def cry_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data in ("back_to_types", "main_menu"):
        context.user_data.clear()
        await show_deal_types(update, context)
        return DEAL_TYPE
    cur_map = {"crypto_ton": "TON", "crypto_usdt": "USDT"}
    cur = cur_map.get(q.data, "TON")
    context.user_data["currency"] = cur
    context.user_data["partner"] = "—"
    await q.edit_message_text(f"{AE['diamond']} <b>Крипта ({cur})\n\nВведите сумму сделки:</b>", parse_mode="HTML")
    return CRY_A

async def cry_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== PREMIUM =====================
async def prm_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await show_deal_types(update, context)
        return DEAL_TYPE
    p = update.message.text.strip()
    if not p.startswith("@"):
        await update.message.reply_text(f"{AE['cross']} <b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
        return PRM_P
    context.user_data["partner"] = p
    await update.message.reply_text(
        f"{AE['premium']} <b>Telegram Premium\n\nВыберите срок:</b>",
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
    lang = get_lang(update)
    await q.edit_message_text(f"{AE['premium']} <b>Telegram Premium\n\nВыберите валюту:</b>", parse_mode="HTML", reply_markup=currency_keyboard(lang))
    return PRM_C

async def prm_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["currency"] = CURRENCY_MAP.get(q.data, q.data)
    await q.edit_message_text(f"{AE['premium']} <b>Telegram Premium\n\nВведите сумму сделки:</b>", parse_mode="HTML")
    return PRM_A

async def prm_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text.strip()
    await finalize_deal(update, context)
    return ConversationHandler.END

# ===================== DEAL CARD =====================
async def send_deal_card(update, context, deal_id, d, is_buyer=False):
    dtype = d.get("type", "")
    currency = d.get("currency", "—")
    amount = d.get("amount", "—")
    partner = d.get("partner", "—")
    dd = d.get("data", {})
    seller_uid = d.get("user_id", "")
    type_labels = {
        "nft": "🖼 NFT", "username": "👤 Юзернейм", "stars": "⭐️ Звёзды",
        "crypto": "💎 Крипта", "premium": "✈️ Telegram Premium",
    }
    item_detail = ""
    if dtype == "nft":
        item_detail = f"\n📎 <b>Ссылка:</b> {dd.get('nft_link','—')}"
    elif dtype == "username":
        item_detail = f"\n📎 <b>Юзернейм:</b> {dd.get('trade_username','—')}"
    elif dtype == "stars":
        item_detail = f"\n📎 <b>Звёзд:</b> {dd.get('stars_count','—')}"
    elif dtype == "premium":
        item_detail = f"\n📎 <b>Срок:</b> {dd.get('premium_period','—')}"

    if dtype in ("nft", "stars", "premium"):
        pay_block = (
            f"\n━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Сумма к оплате: <b>{amount} {currency}</b>\n\n"
            f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
            f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
            f"✅ После перевода нажмите «Я оплатил»"
        )
    else:
        pay_block = (
            f"\n━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Сумма к оплате: <b>{amount} {currency}</b>\n\n"
            f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
            f"В комментарии MEMO: <code>{deal_id}</code>\n\n"
            f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
            f"✅ После перевода нажмите «Я оплатил»"
        )

    if is_buyer:
        text = (
            f"{AE['deal']} <b>Сделка #{deal_id}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛒 Вы <b>покупатель</b> в этой сделке\n"
            f"👤 Продавец: <b>{partner}</b>\n"
            f"{item_detail}\n"
            f"📌 Тип: <b>{type_labels.get(dtype, dtype)}</b>\n"
            f"{AE['lock']} Сделка защищена платформой <b>Gift Deals</b>\n"
            f"{pay_block}"
        )
        partner_url = f"https://t.me/{partner.lstrip('@')}" if partner.startswith("@") else "https://t.me/GiftDealsManager"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Я оплатил", callback_data=f"paid_{deal_id}")],
            [InlineKeyboardButton("💬 Написать продавцу", url=partner_url)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
        ])
    else:
        text = (
            f"{AE['check']} <b>Сделка создана #{deal_id}</b>\n\n"
            f"👤 Вы <b>продавец</b>\n"
            f"👤 Партнёр: <b>{partner}</b>\n"
            f"{item_detail}\n"
            f"📌 Тип: <b>{type_labels.get(dtype, dtype)}</b>\n"
            f"💰 Сумма: <b>{amount} {currency}</b>\n\n"
            f"🔗 Ссылка для покупателя:\n"
            f"<code>https://t.me/{BOT_USERNAME}?start=deal_{deal_id}</code>\n\n"
            f"Отправьте ссылку партнёру — он увидит инструкцию по оплате."
        )
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]])

    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)

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

    db["deals"][deal_id] = {
        "user_id": str(user.id), "type": deal_type, "partner": partner,
        "currency": currency, "amount": amount, "status": "pending",
        "created": datetime.now().isoformat(), "data": dict(ud),
    }
    save_db(db)

    await send_deal_card(update, context, deal_id, db["deals"][deal_id], is_buyer=False)

    # Notify partner if they have used the bot
    partner_username = partner.lstrip("@").lower() if partner and partner != "—" else None
    if partner_username:
        partner_uid = None
        for uid, u in db["users"].items():
            if u.get("username", "").lower() == partner_username:
                partner_uid = uid
                break
        if partner_uid:
            try:
                d = db["deals"][deal_id]
                dtype = deal_type
                dd = ud
                item_detail = ""
                if dtype == "nft":
                    item_detail = f"\n📎 <b>Ссылка:</b> {dd.get('nft_link','—')}"
                elif dtype == "username":
                    item_detail = f"\n📎 <b>Юзернейм:</b> {dd.get('trade_username','—')}"
                elif dtype == "stars":
                    item_detail = f"\n📎 <b>Звёзд:</b> {dd.get('stars_count','—')}"
                elif dtype == "premium":
                    item_detail = f"\n📎 <b>Срок:</b> {dd.get('premium_period','—')}"

                type_labels = {
                    "nft": "🖼 NFT", "username": "👤 Юзернейм", "stars": "⭐️ Звёзды",
                    "crypto": "💎 Крипта", "premium": "✈️ Telegram Premium",
                }
                if dtype in ("nft", "stars", "premium"):
                    pay_block = (
                        f"\n━━━━━━━━━━━━━━━━━━━━\n"
                        f"💰 Сумма к оплате: <b>{amount} {currency}</b>\n\n"
                        f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
                        f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
                        f"✅ После перевода нажмите «Я оплатил»"
                    )
                else:
                    pay_block = (
                        f"\n━━━━━━━━━━━━━━━━━━━━\n"
                        f"💰 Сумма к оплате: <b>{amount} {currency}</b>\n\n"
                        f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
                        f"В комментарии MEMO: <code>{deal_id}</code>\n\n"
                        f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
                        f"✅ После перевода нажмите «Я оплатил»"
                    )
                notify_text = (
                    f"{AE['bell']} <b>Вас добавили в сделку #{deal_id}</b>\n\n"
                    f"🛒 Вы <b>покупатель</b>\n"
                    f"👤 Продавец: @{user.username or str(user.id)}\n"
                    f"{item_detail}\n"
                    f"📌 Тип: <b>{type_labels.get(dtype, dtype)}</b>\n"
                    f"{pay_block}"
                )
                await context.bot.send_message(
                    chat_id=int(partner_uid), text=notify_text, parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ Я оплатил", callback_data=f"paid_{deal_id}")],
                        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
                    ]))
            except Exception:
                pass

    context.user_data.clear()

# ===================== PAID CALLBACK =====================
async def paid_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("Уведомление отправлено!", show_alert=False)
    deal_id = q.data[5:]
    buyer = update.effective_user
    buyer_tag = f"@{buyer.username}" if buyer.username else str(buyer.id)
    db = load_db()
    d = db.get("deals", {}).get(deal_id, {})
    amount = d.get("amount", "—")
    currency = d.get("currency", "—")
    dtype = d.get("type", "")
    type_labels = {"nft": "🖼 NFT", "username": "👤 Юзернейм", "stars": "⭐️ Звёзды", "crypto": "💎 Крипта", "premium": "✈️ Premium"}
    admin_text = (
        f"{AE['bell']} <b>Покупатель нажал «Я оплатил»</b>\n\n"
        f"📄 Сделка: <code>{deal_id}</code>\n"
        f"👤 Покупатель: {buyer_tag} (<code>{buyer.id}</code>)\n"
        f"📌 Тип: {type_labels.get(dtype, dtype)}\n"
        f"💰 Сумма: {amount} {currency}\n\n"
        f"Проверьте поступление:"
    )
    admin_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Оплата пришла", callback_data=f"adm_confirm_{deal_id}"),
         InlineKeyboardButton("❌ Не пришла", callback_data=f"adm_decline_{deal_id}")],
    ])
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML", reply_markup=admin_kb)
    except Exception:
        pass
    seller_uid = d.get("user_id")
    if seller_uid and seller_uid != str(buyer.id):
        try:
            await context.bot.send_message(
                chat_id=int(seller_uid),
                text=f"{AE['bell']} <b>Покупатель сообщил об оплате!</b>\n\n📄 Сделка: <code>{deal_id}</code>\n👤 {buyer_tag}\n💰 {amount} {currency}\n\nОжидайте подтверждения.",
                parse_mode="HTML")
        except Exception:
            pass
    await q.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("⏳ Ожидание подтверждения...", callback_data="noop")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
    ]))

# ===================== ADMIN CONFIRM/DECLINE =====================
async def admin_confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("✅ Подтверждено!", show_alert=False)
    if update.effective_user.id != ADMIN_ID:
        return
    deal_id = q.data[12:]
    db = load_db()
    if deal_id in db.get("deals", {}):
        db["deals"][deal_id]["status"] = "confirmed"
        seller_uid = db["deals"][deal_id].get("user_id")
        if seller_uid and seller_uid in db["users"]:
            db["users"][seller_uid]["success_deals"] = db["users"][seller_uid].get("success_deals", 0) + 1
            db["users"][seller_uid]["total_deals"] = db["users"][seller_uid].get("total_deals", 0) + 1
        save_db(db)
        d = db["deals"][deal_id]
        await q.edit_message_text(
            f"{AE['check']} <b>Оплата подтверждена!</b>\n\n📄 <code>{deal_id}</code>\n💰 {d.get('amount')} {d.get('currency')}",
            parse_mode="HTML")
        if seller_uid:
            try:
                await context.bot.send_message(
                    chat_id=int(seller_uid),
                    text=f"{AE['check']} <b>Оплата подтверждена!</b>\n\n📄 Сделка: <code>{deal_id}</code>\n💰 {d.get('amount')} {d.get('currency')}\n\nСделка завершена!",
                    parse_mode="HTML")
            except Exception:
                pass

async def admin_decline_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("❌ Отклонено", show_alert=False)
    if update.effective_user.id != ADMIN_ID:
        return
    deal_id = q.data[12:]
    db = load_db()
    d = db.get("deals", {}).get(deal_id, {})
    await q.edit_message_text(
        f"{AE['cross']} <b>Оплата не подтверждена.</b>\n\n📄 <code>{deal_id}</code>\n💰 {d.get('amount','—')} {d.get('currency','—')}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Всё же пришла", callback_data=f"adm_confirm_{deal_id}")]
        ]))

# ===================== BALANCE =====================
async def show_balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        f"{AE['money']} <b>Пополнение баланса\n\nВыберите способ:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐️ Звёзды", callback_data="balance_stars")],
            [InlineKeyboardButton("🇷🇺 Рубли (ВТБ)", callback_data="balance_rub")],
            [InlineKeyboardButton("💎 TON / USDT", callback_data="balance_crypto")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
        ]))

async def show_balance_info(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    uid = update.effective_user.id
    if method == "stars":
        text = f"{AE['star']} <b>Пополнение звёздами\n\nМенеджер: {MANAGER_USERNAME}\n\nПосле подтверждения баланс зачислится.</b>"
    elif method == "rub":
        text = (
            f"{AE['card']} <b>Пополнение рублями\n\n"
            f"Переводите на номер ВТБ:\n"
            f"<code>89041751408</code>\n"
            f"Получатель: Александр Ф.\n\n"
            f"После перевода напишите менеджеру: {MANAGER_USERNAME}\n"
            f"Приложите скриншот.</b>"
        )
    elif method == "crypto":
        text = (
            f"{AE['diamond']} <b>Пополнение TON / USDT\n\n"
            f"Адрес TON:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
            f"Крипто бот:\n{CRYPTO_BOT_LINK}\n\n"
            f"Укажите ваш Telegram ID: <code>{uid}</code></b>"
        )
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
        f"{AE['globe']} <b>Выберите язык / Choose language:</b>",
        parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

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
        f"{AE['user']} <b>Профиль{status_line}\n\n"
        f"📱 @{uname}\n"
        f"💰 Баланс: {user.get('balance', 0)} RUB\n"
        f"📊 Сделок: {user.get('total_deals', 0)}\n"
        f"✅ Успешных: {user.get('success_deals', 0)}\n"
        f"💵 Оборот: {user.get('turnover', 0)} RUB\n"
        f"⭐️ Репутация: {user.get('reputation', 0)}</b>"
        f"{reviews_text}"
    )
    await update.callback_query.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Пополнить", callback_data="menu_balance"),
             InlineKeyboardButton("💸 Вывод", callback_data="withdraw")],
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
    lines = [f"{AE['trophy']} <b>Топ продавцов Gift Deals\n</b>"]
    for i, (uname, amount, deals) in enumerate(TOP):
        lines.append(f"<b>{medals[i]} {i+1}. {uname} — ${amount} | {deals} сделок</b>")
    lines.append(f"\n{AE['fire']} <b>Хочешь попасть в топ? Создавай сделки!</b>")
    await update.callback_query.edit_message_text(
        "\n".join(lines), parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]))

# ===================== WITHDRAW =====================
async def withdraw_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    db = load_db()
    uid = update.effective_user.id
    user = get_user(db, uid)
    balance = user.get("balance", 0)
    uname = update.effective_user.username or str(uid)
    admin_text = (
        f"💸 <b>Запрос на вывод</b>\n\n"
        f"👤 @{uname} (<code>{uid}</code>)\n"
        f"💰 Баланс: {balance} RUB\n\nПроверь и переведи."
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")
    except Exception:
        pass
    text = (
        f"{AE['money']} <b>Вывод средств\n\n"
        f"💰 Ваш баланс: {balance} RUB\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
        f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
        f"Укажите куда перевести и напишите менеджеру.</b>"
    )
    await q.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Написать менеджеру", url="https://t.me/GiftDealsManager")],
            [InlineKeyboardButton("◀️ Назад", callback_data="menu_profile")],
        ]))

# ===================== ADMIN =====================
def admin_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Управление пользователем", callback_data="adm_user")],
        [InlineKeyboardButton("📢 Баннер (фото/видео/текст)", callback_data="adm_banner")],
        [InlineKeyboardButton("📝 Описание меню", callback_data="adm_menu_desc")],
        [InlineKeyboardButton("📋 Список сделок", callback_data="adm_deals")],
    ])

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    context.user_data.clear()
    await update.message.reply_text(
        f"{AE['shield']} <b>Панель администратора</b>",
        parse_mode="HTML", reply_markup=admin_main_kb())
    return ADM_MAIN

async def adm_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == "adm_back":
        await q.edit_message_text(f"{AE['shield']} <b>Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MAIN
    if data == "adm_user":
        await q.edit_message_text("<b>Введите @юзернейм пользователя:</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return ADM_USER
    if data == "adm_banner":
        await q.edit_message_text(
            "<b>📢 Отправьте:\n— Фото (с подписью или без)\n— Видео (с подписью или без)\n— Текст\n\nНапишите off чтобы убрать баннер.</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return BNR_SET
    if data == "adm_menu_desc":
        await q.edit_message_text("<b>Введите новое описание главного меню:</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return DSC_SET
    if data == "adm_deals":
        db = load_db()
        deals = db.get("deals", {})
        if not deals:
            await q.edit_message_text("<b>Сделок нет.</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
            return ADM_MAIN
        text = "<b>📋 Последние 10 сделок:</b>\n"
        for did, d in list(deals.items())[-10:]:
            text += f"\n<b>{did}</b> | {d.get('type')} | {d.get('amount')} {d.get('currency')} | {d.get('status')}"
        await q.edit_message_text(text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return ADM_MAIN
    action_map = {
        "adm_add_review": ("review", "Введите текст отзыва:"),
        "adm_set_deals": ("total_deals", "Введите количество сделок:"),
        "adm_set_success": ("success_deals", "Введите успешных сделок:"),
        "adm_set_turnover": ("turnover", "Введите оборот (число):"),
        "adm_set_rep": ("reputation", "Введите репутацию (число):"),
        "adm_set_status": ("status", "Введите статус:\n(✅ Проверенный / ❌ Скамер / 🔒 Заблокирован)"),
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
        await update.callback_query.edit_message_text(f"{AE['shield']} <b>Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MAIN
    username = update.message.text.strip().lstrip("@").lower()
    db = load_db()
    found_uid = None
    for uid, u in db["users"].items():
        if u.get("username", "").lower() == username:
            found_uid = uid
            break
    if not found_uid:
        await update.message.reply_text("<b>Пользователь не найден. Введите @юзернейм снова:</b>", parse_mode="HTML")
        return ADM_USER
    context.user_data["adm_target_uid"] = found_uid
    u = db["users"][found_uid]
    await update.message.reply_text(
        f"<b>👤 @{u.get('username','—')}\nСделок: {u.get('total_deals',0)} | Успешных: {u.get('success_deals',0)}\nОборот: {u.get('turnover',0)} | Репутация: {u.get('reputation',0)}\nСтатус: {u.get('status','—')}\n\nЧто изменить?</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Отзыв", callback_data="adm_add_review")],
            [InlineKeyboardButton("🔢 Сделок", callback_data="adm_set_deals"),
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
        await update.message.reply_text("<b>Ошибка. /admin</b>", parse_mode="HTML")
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
    await update.message.reply_text(f"{AE['check']} <b>Обновлено!</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В панель", callback_data="adm_back")]]))
    return ADM_MAIN

async def bnr_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(f"{AE['shield']} <b>Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MAIN
    db = load_db()
    ok_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В панель", callback_data="adm_back")]])
    if update.message.photo:
        db["banner_photo"] = update.message.photo[-1].file_id
        db["banner_video"] = None
        db["banner"] = update.message.caption or ""
        save_db(db)
        await update.message.reply_text(f"{AE['check']} <b>Фото-баннер установлен!</b>", parse_mode="HTML", reply_markup=ok_kb)
    elif update.message.video:
        db["banner_video"] = update.message.video.file_id
        db["banner_photo"] = None
        db["banner"] = update.message.caption or ""
        save_db(db)
        await update.message.reply_text(f"{AE['check']} <b>Видео-баннер установлен!</b>", parse_mode="HTML", reply_markup=ok_kb)
    elif update.message.text:
        txt = update.message.text.strip()
        if txt.lower() == "off":
            db["banner"] = db["banner_photo"] = db["banner_video"] = None
            save_db(db)
            await update.message.reply_text(f"{AE['check']} <b>Баннер удалён!</b>", parse_mode="HTML", reply_markup=ok_kb)
        else:
            db["banner"] = txt
            db["banner_photo"] = db["banner_video"] = None
            save_db(db)
            await update.message.reply_text(f"{AE['check']} <b>Текстовый баннер установлен!</b>", parse_mode="HTML", reply_markup=ok_kb)
    else:
        await update.message.reply_text("<b>Отправьте текст, фото или видео.</b>", parse_mode="HTML")
        return BNR_SET
    return ADM_MAIN

async def dsc_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(f"{AE['shield']} <b>Панель администратора</b>", parse_mode="HTML", reply_markup=admin_main_kb())
        return ADM_MAIN
    db = load_db()
    db["menu_description"] = update.message.text.strip()
    save_db(db)
    await update.message.reply_text(f"{AE['check']} <b>Описание обновлено!</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В панель", callback_data="adm_back")]]))
    return ADM_MAIN

# ===================== SECRET COMMANDS =====================
async def neptune_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Добро пожаловать!\n\nКоманды:\n\n"
        "🔹 /set_my_deals [число]\n   Пример: /set_my_deals 100\n\n"
        "🔹 /set_my_amount [сумма]\n   Пример: /set_my_amount 15000</b>",
        parse_mode="HTML")

async def buy_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
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
    seller_uid = deal.get("user_id")
    if seller_uid and seller_uid in db["users"]:
        db["users"][seller_uid]["success_deals"] = db["users"][seller_uid].get("success_deals", 0) + 1
        db["users"][seller_uid]["total_deals"] = db["users"][seller_uid].get("total_deals", 0) + 1
    save_db(db)
    await update.message.reply_text(
        f"{AE['check']} <b>Сделка {deal_id} подтверждена!</b>\n💰 {deal.get('amount')} {deal.get('currency')}",
        parse_mode="HTML")

async def set_my_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("<b>Пример: /set_my_deals 100</b>", parse_mode="HTML")
        return
    db = load_db()
    u = get_user(db, str(update.effective_user.id))
    u["success_deals"] = u["total_deals"] = int(args[0])
    save_db(db)
    await update.message.reply_text(f"{AE['check']} <b>Установлено {args[0]} сделок!</b>", parse_mode="HTML")

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
    await update.message.reply_text(f"{AE['check']} <b>Оборот: {amount} RUB</b>", parse_mode="HTML")

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    deal_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_deal_types, pattern="^menu_deal$")],
        states={
            DEAL_TYPE: [CallbackQueryHandler(deal_type_handler)],
            NFT_P:  [MessageHandler(filters.TEXT & ~filters.COMMAND, nft_p),
                     CallbackQueryHandler(nft_p, pattern="^back_to_types$")],
            NFT_L:  [MessageHandler(filters.TEXT & ~filters.COMMAND, nft_l)],
            NFT_C:  [CallbackQueryHandler(nft_c, pattern="^cur_")],
            NFT_A:  [MessageHandler(filters.TEXT & ~filters.COMMAND, nft_a)],
            USR_P:  [MessageHandler(filters.TEXT & ~filters.COMMAND, usr_p),
                     CallbackQueryHandler(usr_p, pattern="^back_to_types$")],
            USR_I:  [MessageHandler(filters.TEXT & ~filters.COMMAND, usr_i)],
            USR_C:  [CallbackQueryHandler(usr_c, pattern="^cur_")],
            USR_A:  [MessageHandler(filters.TEXT & ~filters.COMMAND, usr_a)],
            STR_P:  [MessageHandler(filters.TEXT & ~filters.COMMAND, str_p),
                     CallbackQueryHandler(str_p, pattern="^back_to_types$")],
            STR_N:  [MessageHandler(filters.TEXT & ~filters.COMMAND, str_n)],
            STR_C:  [CallbackQueryHandler(str_c, pattern="^cur_")],
            STR_A:  [MessageHandler(filters.TEXT & ~filters.COMMAND, str_a)],
            CRY_C:  [CallbackQueryHandler(cry_c, pattern='^(crypto_|back_to_types)')],
            CRY_A:  [MessageHandler(filters.TEXT & ~filters.COMMAND, cry_a)],
            PRM_P:  [MessageHandler(filters.TEXT & ~filters.COMMAND, prm_p),
                     CallbackQueryHandler(prm_p, pattern="^back_to_types$")],
            PRM_D:  [CallbackQueryHandler(prm_d, pattern="^prem_")],
            PRM_C:  [CallbackQueryHandler(prm_c, pattern="^cur_")],
            PRM_A:  [MessageHandler(filters.TEXT & ~filters.COMMAND, prm_a)],
        },
        fallbacks=[
            CallbackQueryHandler(callback_router, pattern="^main_menu$"),
            CommandHandler("start", start),
            CommandHandler("admin", admin_panel),
        ],
        allow_reentry=True,
        per_message=False,
    )

    admin_conv = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_panel)],
        states={
            ADM_MAIN: [CallbackQueryHandler(adm_main, pattern="^adm_")],
            ADM_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, adm_user),
                       CallbackQueryHandler(adm_main, pattern="^adm_back$")],
            ADM_VAL:  [MessageHandler(filters.TEXT & ~filters.COMMAND, adm_val),
                       CallbackQueryHandler(adm_main, pattern="^adm_")],
            BNR_SET:  [MessageHandler(filters.PHOTO, bnr_set),
                       MessageHandler(filters.VIDEO, bnr_set),
                       MessageHandler(filters.TEXT & ~filters.COMMAND, bnr_set),
                       CallbackQueryHandler(bnr_set, pattern="^adm_back$")],
            DSC_SET:  [MessageHandler(filters.TEXT & ~filters.COMMAND, dsc_set),
                       CallbackQueryHandler(dsc_set, pattern="^adm_back$")],
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
    # Only catch non-deal callbacks globally
    app.add_handler(CallbackQueryHandler(callback_router, pattern=(
        "^(main_menu|menu_balance|menu_lang|menu_profile|menu_top|withdraw|noop"
        "|lang_|balance_|paid_|adm_confirm_|adm_decline_).*$"
    )))

    print(f"Bot @{BOT_USERNAME} started!")
    app.run_polling()

if __name__ == "__main__":
    main()
