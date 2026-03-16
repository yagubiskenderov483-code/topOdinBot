import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8636524725:AAHY7j6yHm5fo3H2uLFs9GzZbBQsPj5fLeY"
ADMIN_ID = 174415647
BOT_USERNAME = "GiftDealsRobot"
MANAGER_USERNAME = "@GiftDealsManager"
CRYPTO_ADDRESS = "UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc"
DB_FILE = "db.json"

# Функция для создания премиум эмодзи
def ae(eid, fb): return f"<tg-emoji emoji-id='{eid}'>{fb}</tg-emoji>"

# Обычные эмодзи (заглушки)
E = {
    "diamond":  "💎",
    "check":    "✅",
    "cross":    "❌",
    "fire":     "🔥",
    "star":     "⭐️",
    "lock":     "🔒",
    "bell":     "🔔",
    "gift":     "🎁",
    "trophy":   "🏆",
    "shield":   "🛡",
    "money":    "💰",
    "pencil":   "✏️",
    "globe":    "🌍",
    "nft":      "🖼",
    "user":     "👤",
    "premium":  "✈️",
    "deal":     "🤝",
    "card":     "💳",
}

# Премиум эмодзи (для пользователей с Telegram Premium)
CEMOJI = {
    "deal":    "5267021122383086560",  # 🤝
    "star":    "5368324170671202286",  # ⭐️
    "money":   "5451882697270755274",  # 💰
    "rocket":  "5431815452437257407",  # 🚀
    "crown":   "5373026167722876724",  # 👑
    "fire":    "5422998492250386138",  # 🔥
    "shield":  "5472354553527541051",  # 🛡
}
CD="💎"; CC="✅"; CF="🔥"; CS="⭐"; CL="🔒"; CSH="🛡"; CR="🚀"
CG="🎁"; CM="💰"; CDL="🤝"; CBL="🔔"

# ── DB ──────────────────────────────────────────────────────────────────────
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {"users":{},"deals":{},"banner":None,"banner_photo":None,
            "banner_video":None,"menu_description":None,"deal_counter":1}

def save_db(db):
    with open(DB_FILE,"w",encoding="utf-8") as f:
        json.dump(db,f,ensure_ascii=False,indent=2)

def get_user(db, uid):
    k = str(uid)
    if k not in db["users"]:
        db["users"][k] = {"username":"","balance":0,"total_deals":0,
            "success_deals":0,"turnover":0,"reputation":0,
            "reviews":[],"status":"","lang":"ru"}
    return db["users"][k]

def get_lang(uid):
    try:
        db = load_db()
        return get_user(db, uid).get("lang","ru")
    except:
        return "ru"

def gen_deal_id(db):
    n = db.get("deal_counter",1)
    db["deal_counter"] = n+1
    save_db(db)
    return f"GD{n:05d}"

# ── Localization ─────────────────────────────────────────────────────────────
LANGS = {
    "ru":"🇷🇺 Россия",    "en":"🇬🇧 English",
    "kz":"🇰🇿 Қазақстан", "az":"🇦🇿 Azərbaycan",
    "uz":"🇺🇿 O'zbek",    "kg":"🇰🇬 Кыргызстан",
    "tj":"🇹🇯 Тоҷикистон","by":"🇧🇾 Беларусь",
    "am":"🇦🇲 Հայաستان",  "ge":"🇬🇪 საქართველო",
    "ua":"🇺🇦 Україна",   "md":"🇲🇩 Moldova",
}

def get_welcome(lang):
    base = {
        "en": "Gift Deals — safe platform for deals in Telegram.\n\nWe guarantee honest transactions.",
        "kz": "Gift Deals — Telegram-дағы қауіпсіз мәміле алаңы.",
        "az": "Gift Deals — Telegram-da etibarlı əməliyyat platforması.",
        "uz": "Gift Deals — Telegram'dagi ishonchli bitim platformasi.",
        "kg": "Gift Deals — Telegram'дагы коопсуз бүтүм аянтчасы.",
        "tj": "Gift Deals — майдончаи боэтимоди муомилот дар Telegram.",
        "by": "Gift Deals — надзейная пляцоўка для здзелак у Telegram.",
        "am": "Gift Deals — надёжная платформа в Telegram.",
        "ge": "Gift Deals — საიმედო პლატფორმა Telegram-ში.",
        "ua": "Gift Deals — надійна платформа для угод у Telegram.",
        "md": "Gift Deals — platformă de încredere în Telegram.",
    }
    if lang not in base:
        return (
            f"{CD} <b>Gift Deals</b> — самая безопасная площадка для сделок в Telegram\n\n"
            f"1️⃣ {CDL} Автоматические сделки с НФТ и подарками\n"
            f"2️⃣ {CSH} Полная защита обеих сторон\n"
            f"3️⃣ {CL} Средства заморожены до подтверждения\n"
            f"4️⃣ {CG} Передача через менеджера: @GiftDealsManager\n\n"
            f"{CF} <b>Выберите действие ниже</b> {CF}"
        )
    return base.get(lang, base["en"])

BTN = {
    "ru":{"deal":"🤝 Создать сделку","support":"🛡 Поддержка","balance":"💰 Баланс","lang":"🌐 Язык / Lang","profile":"👤 Профиль","top":"🏆 Топ продавцов"},
    "en":{"deal":"🤝 Create Deal","support":"🛡 Support","balance":"💰 Balance","lang":"🌐 Language","profile":"👤 Profile","top":"🏆 Top Sellers"},
    "kz":{"deal":"🤝 Мәміле","support":"🛡 Қолдау","balance":"💰 Баланс","lang":"🌐 Тіл","profile":"👤 Профиль","top":"🏆 Үздіктер"},
    "az":{"deal":"🤝 Müqavilə","support":"🛡 Dəstək","balance":"💰 Balans","lang":"🌐 Dil","profile":"👤 Profil","top":"🏆 Top"},
    "uz":{"deal":"🤝 Bitim","support":"🛡 Yordam","balance":"💰 Balans","lang":"🌐 Til","profile":"👤 Profil","top":"🏆 Top"},
    "kg":{"deal":"🤝 Бүтүм","support":"🛡 Колдоо","balance":"💰 Баланс","lang":"🌐 Тил","profile":"👤 Профиль","top":"🏆 Топ"},
    "tj":{"deal":"🤝 Муомила","support":"🛡 Ёрдам","balance":"💰 Баланс","lang":"🌐 Забон","profile":"👤 Профил","top":"🏆 Топ"},
    "by":{"deal":"🤝 Здзелка","support":"🛡 Падтрымка","balance":"💰 Баланс","lang":"🌐 Мова","profile":"👤 Профіль","top":"🏆 Топ"},
    "am":{"deal":"🤝 Գործarqner","support":"🛡 Aջakцutyun","balance":"💰 Balanss","lang":"🌐 Lezun","profile":"👤 Profil","top":"🏆 Lavagoyn"},
    "ge":{"deal":"🤝 გარიგება","support":"🛡 მხარდ.","balance":"💰 ბალანსი","lang":"🌐 ენა","profile":"👤 პროფ.","top":"🏆 საუკ."},
    "ua":{"deal":"🤝 Угода","support":"🛡 Підтримка","balance":"💰 Баланс","lang":"🌐 Мова","profile":"👤 Профіль","top":"🏆 Топ"},
    "md":{"deal":"🤝 Tranzacție","support":"🛡 Suport","balance":"💰 Sold","lang":"🌐 Limbă","profile":"👤 Profil","top":"🏆 Top"},
}

CUR = {
    "TON":"💎 TON","USDT":"💵 USDT",
    "Stars":{"ru":"⭐️ Звёзды","en":"⭐️ Stars","kz":"⭐️ Жұлдыз","az":"⭐️ Ulduz","uz":"⭐️ Yulduz","kg":"⭐️ Жылдыз","tj":"⭐️ Ситора","by":"⭐️ Зоркі","am":"⭐️ Astegh","ge":"⭐️ ვარსკვ.","ua":"⭐️ Зірки","md":"⭐️ Stele"},
    "RUB":{"ru":"🇷🇺 Рубли","en":"🇷🇺 RUB","kz":"🇷🇺 Рубль","az":"🇷🇺 Rubl","uz":"🇷🇺 Rubl","kg":"🇷🇺 Рубль","tj":"🇷🇺 Рубл","by":"🇷🇺 Рублі","am":"🇷🇺 Rubl","ge":"🇷🇺 რუბლი","ua":"🇷🇺 Рублі","md":"🇷🇺 Ruble"},
    "KZT":{"ru":"🇰🇿 Тенге","en":"🇰🇿 Tenge","kz":"🇰🇿 Теңге","az":"🇰🇿 Tenge","uz":"🇰🇿 Tenge","kg":"🇰🇿 Теңге","tj":"🇰🇿 Тенге","by":"🇰🇿 Тэнге","am":"🇰🇿 Tenge","ge":"🇰🇿 ტენგე","ua":"🇰🇿 Тенге","md":"🇰🇿 Tenge"},
    "AZN":{"ru":"🇦🇿 Манат","en":"🇦🇿 Manat","kz":"🇦🇿 Манат","az":"🇦🇿 Manat","uz":"🇦🇿 Manat","kg":"🇦🇿 Манат","tj":"🇦🇿 Манат","by":"🇦🇿 Манат","am":"🇦🇿 Manat","ge":"🇦🇿 მანათი","ua":"🇦🇿 Манат","md":"🇦🇿 Manat"},
    "KGS":{"ru":"🇰🇬 Сомы","en":"🇰🇬 Som","kz":"🇰🇬 Сом","az":"🇰🇬 Som","uz":"🇰🇬 Som","kg":"🇰🇬 Сом","tj":"🇰🇬 Сом","by":"🇰🇬 Сомы","am":"🇰🇬 Som","ge":"🇰🇬 სომი","ua":"🇰🇬 Соми","md":"🇰🇬 Som"},
    "UZS":{"ru":"🇺🇿 Сумы","en":"🇺🇿 Sum","kz":"🇺🇿 Сум","az":"🇺🇿 Sum","uz":"🇺🇿 So'm","kg":"🇺🇿 Сум","tj":"🇺🇿 Сум","by":"🇺🇿 Сумы","am":"🇺🇿 Sum","ge":"🇺🇿 სუმი","ua":"🇺🇿 Суми","md":"🇺🇿 Sum"},
    "TJS":{"ru":"🇹🇯 Сомони","en":"🇹🇯 Somoni","kz":"🇹🇯 Сомонӣ","az":"🇹🇯 Somoni","uz":"🇹🇯 Somoni","kg":"🇹🇯 Сомонӣ","tj":"🇹🇯 Сомонӣ","by":"🇹🇯 Самані","am":"🇹🇯 Somoni","ge":"🇹🇯 სომონი","ua":"🇹🇯 Сомоні","md":"🇹🇯 Somoni"},
    "BYN":{"ru":"🇧🇾 Рубли BY","en":"🇧🇾 BYN","kz":"🇧🇾 Руб. BY","az":"🇧🇾 Rubl BY","uz":"🇧🇾 Rubl BY","kg":"🇧🇾 Руб. BY","tj":"🇧🇾 Руб. BY","by":"🇧🇾 Рублі","am":"🇧🇾 Rubl BY","ge":"🇧🇾 რუბ. BY","ua":"🇧🇾 Рублі BY","md":"🇧🇾 Ruble BY"},
    "UAH":{"ru":"🇺🇦 Гривны","en":"🇺🇦 Hryvnia","kz":"🇺🇦 Гривна","az":"🇺🇦 Grivna","uz":"🇺🇦 Grivna","kg":"🇺🇦 Гривна","tj":"🇺🇦 Гривна","by":"🇺🇦 Грыўні","am":"🇺🇦 Grivna","ge":"🇺🇦 გრივნა","ua":"🇺🇦 Гривні","md":"🇺🇦 Grivne"},
    "GEL":{"ru":"🇬🇪 Лари","en":"🇬🇪 Lari","kz":"🇬🇪 Лари","az":"🇬🇪 Lari","uz":"🇬🇪 Lari","kg":"🇬🇪 Лари","tj":"🇬🇪 Лари","by":"🇬🇪 Лары","am":"🇬🇪 Lari","ge":"🇬🇪 ლარი","ua":"🇬🇪 Ларі","md":"🇬🇪 Lari"},
}

CURMAP = {"cur_ton":"TON","cur_usdt":"USDT","cur_rub":"RUB","cur_stars":"Stars",
          "cur_kzt":"KZT","cur_azn":"AZN","cur_kgs":"KGS","cur_uzs":"UZS",
          "cur_tjs":"TJS","cur_byn":"BYN","cur_uah":"UAH","cur_gel":"GEL"}

def cur_name(code, lang):
    v = CUR.get(code, code)
    if isinstance(v, dict): return v.get(lang, v.get("ru", code))
    return v

def cur_kb(lang):
    def n(c): return cur_name(c,lang)
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

# ── Safe send ────────────────────────────────────────────────────────────────
async def send_text(update, text, kb=None):
    """Always sends a NEW message. Use for deal steps."""
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)

async def edit_or_send(update, text, kb=None):
    """Try edit, fallback to new message."""
    try:
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)

# ── Main menu ────────────────────────────────────────────────────────────────
def main_kb(lang):
    b = BTN.get(lang, BTN["ru"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=ae(CEMOJI["deal"], "🤝") + " " + b["deal"], 
            callback_data="menu_deal"
         ),
         InlineKeyboardButton(
            text=ae(CEMOJI["star"], "⭐️") + " " + b["profile"], 
            callback_data="menu_profile"
         )],
        [InlineKeyboardButton(
            text=ae(CEMOJI["money"], "💰") + " " + b["balance"], 
            callback_data="menu_balance"
         ),
         InlineKeyboardButton(
            text=ae(CEMOJI["rocket"], "🚀") + " 📋 Мои сделки", 
            callback_data="menu_my_deals"
         )],
        [InlineKeyboardButton(
            text=ae(CEMOJI["crown"], "👑") + " " + b["lang"], 
            callback_data="menu_lang"
         ),
         InlineKeyboardButton(
            text=ae(CEMOJI["fire"], "🔥") + " " + b["top"], 
            callback_data="menu_top"
         )],
        [InlineKeyboardButton(
            text=ae(CEMOJI["shield"], "🛡") + " 🆘 Техподдержка ↗️", 
            url="https://t.me/GiftDealsSupport"
         )],
    ])

async def show_main(update, context, edit=False):
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    lang = u.get("lang","ru")
    desc = db.get("menu_description") or get_welcome(lang)
    banner = db.get("banner") or ""
    text = f"💎 <b>Gift Deals</b>\n\n{desc}"
    if banner: text += f"\n\n<b>{banner}</b>"
    kb = main_kb(lang)
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

# ── /start ───────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        db = load_db()
        u = get_user(db, update.effective_user.id)
        u["username"] = update.effective_user.username or ""
        save_db(db)
        context.user_data.clear()
        args = context.args
        if args and args[0].startswith("deal_"):
            deal_id = args[0][5:].upper()
            d = db.get("deals",{}).get(deal_id)
            if d:
                await send_deal_card(update, context, deal_id, d, buyer=True)
                return
            await update.effective_message.reply_text(f"<b>Сделка {deal_id} не найдена.</b>", parse_mode="HTML")
        await show_main(update, context)
    except Exception as e:
        logger.error(f"START ERROR: {e}", exc_info=True)
        try:
            await update.effective_message.reply_text(f"Ошибка: {e}")
        except Exception:
            pass

# ── Deal types menu ──────────────────────────────────────────────────────────
def deal_types_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=ae(CEMOJI["deal"], "🖼") + " НФТ", 
            callback_data="dt_nft"
         ),
         InlineKeyboardButton(
            text=ae(CEMOJI["star"], "👤") + " НФТ Юзернейм", 
            callback_data="dt_usr"
         )],
        [InlineKeyboardButton(
            text=ae(CEMOJI["star"], "⭐️") + " Звёзды", 
            callback_data="dt_str"
         ),
         InlineKeyboardButton(
            text=ae(CEMOJI["money"], "💎") + " Крипта (TON/$)", 
            callback_data="dt_cry"
         )],
        [InlineKeyboardButton(
            text=ae(CEMOJI["rocket"], "✈️") + " Telegram Premium", 
            callback_data="dt_prm"
         )],
        [InlineKeyboardButton(
            text=ae(CEMOJI["shield"], "◀️") + " Назад", 
            callback_data="main_menu"
         )],
    ])

async def show_deal_types(update, context):
    await edit_or_send(update,
        f"{ae(CEMOJI['star'], '✏️')} <b>Создать сделку\n\nВыберите тип:</b>",
        deal_types_kb())

# ── Callback handler ─────────────────────────────────────────────────────────
async def on_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    ud = context.user_data
    uid = update.effective_user.id
    lang = get_lang(uid)

    logger.info(f"CB {d} uid={uid}")

    # Navigation
    if d == "main_menu":
        ud.clear()
        try: await q.message.delete()
        except: pass
        await show_main(update, context, edit=False)
        return
    if d == "menu_deal":
        ud.clear()
        try: await q.message.delete()
        except: pass
        await update.effective_message.reply_text(
            f"{ae(CEMOJI['star'], '✏️')} <b>Создать сделку\n\nВыберите тип:</b>",
            parse_mode="HTML", reply_markup=deal_types_kb())
        return
    if d == "menu_balance":  await show_balance(update, context); return
    if d == "menu_lang":     await show_lang(update, context); return
    if d == "menu_profile":  await show_profile(update, context); return
    if d == "menu_top":      await show_top(update, context); return
    if d == "menu_my_deals": await show_my_deals(update, context); return
    if d.startswith("lang_"):    await set_lang(update, context, d[5:]); return
    if d.startswith("balance_"): await show_balance_info(update, context, d[8:]); return
    if d == "withdraw":      await show_withdraw(update, context); return
    if d.startswith("paid_"):    await on_paid(update, context); return
    if d == "noop":          return
    if d.startswith("adm_confirm_"): await adm_confirm(update, context); return
    if d.startswith("adm_decline_"): await adm_decline(update, context); return
    if d == "adm_back":
        await edit_or_send(update, f"{ae(CEMOJI['shield'], '🛡')} <b>Панель администратора</b>", adm_kb())
        return
    if d.startswith("adm_"):
        await handle_adm_cb(update, context)
        return

    # Deal type buttons
    if d == "dt_nft":
        ud.clear(); ud["type"]="nft"; ud["step"]="partner"
        await send_text(update, f"{ae(CEMOJI['deal'], '🖼')} <b>НФТ\n\nВведите @юзернейм партнёра:</b>",
            InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад",callback_data="menu_deal")]]))
        return
    if d == "dt_usr":
        ud.clear(); ud["type"]="username"; ud["step"]="partner"
        await send_text(update, f"{ae(CEMOJI['star'], '👤')} <b>Юзернейм\n\nВведите @юзернейм партнёра:</b>",
            InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад",callback_data="menu_deal")]]))
        return
    if d == "dt_str":
        ud.clear(); ud["type"]="stars"; ud["step"]="partner"
        await send_text(update, f"{ae(CEMOJI['star'], '⭐️')} <b>Звёзды\n\nВведите @юзернейм партнёра:</b>",
            InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад",callback_data="menu_deal")]]))
        return
    if d == "dt_cry":
        ud.clear(); ud["type"]="crypto"; ud["step"]="partner"
        await send_text(update, f"{ae(CEMOJI['money'], '💎')} <b>Крипта\n\nВведите @юзернейм партнёра:</b>",
            InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_deal")]]))
        return
    if d == "dt_prm":
        ud.clear(); ud["type"]="premium"; ud["step"]="partner"
        await send_text(update, f"{ae(CEMOJI['rocket'], '✈️')} <b>Telegram Premium\n\nВведите @юзернейм партнёра:</b>",
            InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад",callback_data="menu_deal")]]))
        return

    # Crypto currency selection (comes after partner)
    if d == "cry_ton":
        ud["currency"]="TON"; ud["step"]="amount"
        await send_text(update, f"{ae(CEMOJI['money'], '💎')} <b>Крипта (TON)\n\nВведите сумму сделки:</b>")
        return
    if d == "cry_usd":
        ud["currency"]="USDT"; ud["step"]="amount"
        await send_text(update, f"{ae(CEMOJI['money'], '💎')} <b>Крипта (USDT)\n\nВведите сумму сделки:</b>")
        return

    # Premium period
    if d in ("prm_3","prm_6","prm_12"):
        periods = {"prm_3":"3 месяца","prm_6":"6 месяцев","prm_12":"12 месяцев"}
        ud["premium_period"] = periods[d]
        ud["step"] = "currency"
        await send_text(update, f"{ae(CEMOJI['rocket'], '✈️')} <b>Telegram Premium\n\nВыберите валюту:</b>", cur_kb(lang))
        return

    # Currency selection
    if d.startswith("cur_"):
        ud["currency"] = CURMAP.get(d, d)
        ud["step"] = "amount"
        icons = {"nft":ae(CEMOJI['deal'], '🖼'),"username":ae(CEMOJI['star'], '👤'),"stars":ae(CEMOJI['star'], '⭐️'),"premium":ae(CEMOJI['rocket'], '✈️')}
        icon = icons.get(ud.get("type",""), ae(CEMOJI['deal'], '🤝'))
        await send_text(update, f"{icon} <b>Введите сумму сделки:</b>")
        return

# ── Message handler ──────────────────────────────────────────────────────────
async def on_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud = context.user_data
    uid = update.effective_user.id
    lang = get_lang(uid)
    text = update.message.text.strip() if update.message.text else ""

    # Admin photo/video for banner
    if uid == ADMIN_ID and ud.get("adm_step") == "banner":
        await handle_adm_msg(update, context)
        return

    # Admin text
    if uid == ADMIN_ID and ud.get("adm_step"):
        await handle_adm_msg(update, context)
        return

    # Deal flow
    dtype = ud.get("type")
    step  = ud.get("step")
    if not dtype or not step:
        return

    if step == "partner":
        if not text.startswith("@"):
            await update.message.reply_text(f"{E['cross']} <b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
            return
        ud["partner"] = text
        if dtype == "nft":
            ud["step"] = "nft_link"
            await update.message.reply_text(f"{ae(CEMOJI['deal'], '🖼')} <b>НФТ\n\nВставьте ссылку на НФТ (https://...):</b>", parse_mode="HTML")
        elif dtype == "username":
            ud["step"] = "trade_usr"
            await update.message.reply_text(f"{ae(CEMOJI['star'], '👤')} <b>Юзернейм\n\nВведите @юзернейм товара:</b>", parse_mode="HTML")
        elif dtype == "stars":
            ud["step"] = "stars_cnt"
            await update.message.reply_text(f"{ae(CEMOJI['star'], '⭐️')} <b>Звёзды\n\nСколько звёзд?</b>", parse_mode="HTML")
        elif dtype == "crypto":
            ud["step"] = "cry_currency"
            await update.message.reply_text(
                f"{ae(CEMOJI['money'], '💎')} <b>Крипта\n\nВыберите валюту:</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💎 TON",   callback_data="cry_ton"),
                     InlineKeyboardButton("💵 USDT",  callback_data="cry_usd")],
                ]))
        elif dtype == "premium":
            ud["step"] = "prem_period"
            await update.message.reply_text(
                f"{ae(CEMOJI['rocket'], '✈️')} <b>Telegram Premium\n\nВыберите срок:</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("3 месяца", callback_data="prm_3"),
                     InlineKeyboardButton("6 месяцев", callback_data="prm_6"),
                     InlineKeyboardButton("12 месяцев", callback_data="prm_12")],
                ]))
        return

    if step == "nft_link":
        if not text.startswith("https://"):
            await update.message.reply_text(f"{E['cross']} <b>Ссылка должна начинаться с https://</b>", parse_mode="HTML")
            return
        ud["nft_link"] = text
        ud["step"] = "currency"
        await update.message.reply_text(f"{ae(CEMOJI['deal'], '🖼')} <b>НФТ\n\nВыберите валюту:</b>", parse_mode="HTML", reply_markup=cur_kb(lang))
        return

    if step == "trade_usr":
        if not text.startswith("@"):
            await update.message.reply_text(f"{E['cross']} <b>Юзернейм должен начинаться с @</b>", parse_mode="HTML")
            return
        ud["trade_username"] = text
        ud["step"] = "currency"
        await update.message.reply_text(f"{ae(CEMOJI['star'], '👤')} <b>Юзернейм\n\nВыберите валюту:</b>", parse_mode="HTML", reply_markup=cur_kb(lang))
        return

    if step == "stars_cnt":
        if not text.isdigit():
            await update.message.reply_text(f"{E['cross']} <b>Только цифры!</b>", parse_mode="HTML")
            return
        ud["stars_count"] = text
        ud["step"] = "currency"
        await update.message.reply_text(f"{ae(CEMOJI['star'], '⭐️')} <b>Звёзды\n\nВыберите валюту:</b>", parse_mode="HTML", reply_markup=cur_kb(lang))
        return

    if step == "amount":
        ud["amount"] = text
        await finalize_deal(update, context)
        return

# ── Finalize deal ─────────────────────────────────────────────────────────────
async def finalize_deal(update, context):
    db = load_db()
    ud = context.user_data
    deal_id = gen_deal_id(db)
    dtype   = ud.get("type","?")
    partner = ud.get("partner","—")
    currency= ud.get("currency","—")
    amount  = ud.get("amount","—")
    user    = update.effective_user

    db["deals"][deal_id] = {
        "user_id": str(user.id), "type": dtype, "partner": partner,
        "currency": currency, "amount": amount, "status": "pending",
        "created": datetime.now().isoformat(), "data": dict(ud),
    }
    save_db(db)
    await send_deal_card(update, context, deal_id, db["deals"][deal_id], buyer=False)

    # Notify partner
    pname = partner.lstrip("@").lower() if partner.startswith("@") else None
    if pname:
        puid = next((k for k,v in db["users"].items() if v.get("username","").lower()==pname), None)
        if puid:
            try:
                txt = build_buyer_card(deal_id, db["deals"][deal_id], f"@{user.username or str(user.id)}")
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Я оплатил", callback_data=f"paid_{deal_id}")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
                ])
                await context.bot.send_message(chat_id=int(puid), text=txt, parse_mode="HTML", reply_markup=kb)
            except Exception:
                pass
    context.user_data.clear()

def build_buyer_card(deal_id, d, seller_tag):
    dtype = d.get("type","")
    cur   = d.get("currency","—")
    amt   = d.get("amount","—")
    dd    = d.get("data",{})
    partner = d.get("partner","—")
    TNAMES = {"nft":"🖼 NFT","username":"👤 Юзернейм","stars":"⭐️ Звёзды","crypto":"💎 Крипта","premium":"✈️ Premium"}
    item = ""
    if dtype=="nft":      item = f"\n📎 Ссылка: {dd.get('nft_link','—')}"
    elif dtype=="username": item = f"\n📎 Юзернейм: {dd.get('trade_username','—')}"
    elif dtype=="stars":  item = f"\n📎 Звёзд: {dd.get('stars_count','—')}"
    elif dtype=="premium": item = f"\n📎 Срок: {dd.get('premium_period','—')}"
    pay = (f"\n━━━━━━━━━━━━━━━━━━━━\n"
           f"💰 Сумма: <b>{amt} {cur}</b>\n\n"
           f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
           f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
           f"✅ После перевода нажмите «Я оплатил»")
    return (f"{E['deal']} <b>Сделка #{deal_id}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛒 Вы <b>покупатель</b>\n"
            f"👤 Продавец: <b>{seller_tag}</b>\n"
            f"{item}\n"
            f"📌 Тип: <b>{TNAMES.get(dtype,dtype)}</b>\n"
            f"{E['lock']} Сделка защищена Gift Deals\n{pay}")

async def send_deal_card(update, context, deal_id, d, buyer=False):
    dtype = d.get("type","")
    cur   = d.get("currency","—")
    amt   = d.get("amount","—")
    partner = d.get("partner","—")
    dd    = d.get("data",{})
    TNAMES = {"nft":"🖼 NFT","username":"👤 Юзернейм","stars":"⭐️ Звёзды","crypto":"💎 Крипта","premium":"✈️ Premium"}
    item = ""
    if dtype=="nft":       item = f"\n📎 Ссылка: {dd.get('nft_link','—')}"
    elif dtype=="username": item = f"\n📎 Юзернейм: {dd.get('trade_username','—')}"
    elif dtype=="stars":   item = f"\n📎 Звёзд: {dd.get('stars_count','—')}"
    elif dtype=="premium": item = f"\n📎 Срок: {dd.get('premium_period','—')}"
    pay = (f"\n━━━━━━━━━━━━━━━━━━━━\n"
           f"💰 Сумма: <b>{amt} {cur}</b>\n\n"
           f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
           f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
           f"✅ После перевода нажмите «Я оплатил»")
    if buyer:
        pu = f"https://t.me/{partner.lstrip('@')}" if partner.startswith("@") else "https://t.me/GiftDealsManager"
        text = (f"{E['deal']} <b>Сделка #{deal_id}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🛒 Вы <b>покупатель</b>\n"
                f"👤 Продавец: <b>{partner}</b>\n"
                f"{item}\n"
                f"📌 Тип: <b>{TNAMES.get(dtype,dtype)}</b>\n"
                f"{E['lock']} Сделка защищена Gift Deals\n{pay}")
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Я оплатил",         callback_data=f"paid_{deal_id}")],
            [InlineKeyboardButton("💬 Написать продавцу", url=pu)],
            [InlineKeyboardButton("🏠 Главное меню",       callback_data="main_menu")],
        ])
    else:
        text = (f"{E['check']} <b>Сделка создана #{deal_id}</b>\n\n"
                f"👤 Вы <b>продавец</b>\n"
                f"👤 Партнёр: <b>{partner}</b>\n"
                f"{item}\n"
                f"📌 Тип: <b>{TNAMES.get(dtype,dtype)}</b>\n"
                f"💰 Сумма: <b>{amt} {cur}</b>\n\n"
                f"🔗 Ссылка для покупателя:\n"
                f"<code>https://t.me/{BOT_USERNAME}?start=deal_{deal_id}</code>\n\n"
                f"Отправьте ссылку партнёру.")
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]])
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)

# ── Paid ─────────────────────────────────────────────────────────────────────
async def on_paid(update, context):
    q = update.callback_query
    await q.answer("Уведомление отправлено!")
    deal_id = q.data[5:]
    buyer = update.effective_user
    btag = f"@{buyer.username}" if buyer.username else str(buyer.id)
    db = load_db()
    d = db.get("deals",{}).get(deal_id,{})
    amt = d.get("amount","—"); cur = d.get("currency","—"); dtype = d.get("type","")
    TNAMES = {"nft":"🖼 NFT","username":"👤 Юзернейм","stars":"⭐️ Звёзды","crypto":"💎 Крипта","premium":"✈️ Premium"}
    adm_txt = (f"{E['bell']} <b>Покупатель нажал «Я оплатил»</b>\n\n"
               f"📄 <code>{deal_id}</code>\n👤 {btag} (<code>{buyer.id}</code>)\n"
               f"📌 {TNAMES.get(dtype,dtype)}\n💰 {amt} {cur}\n\nПроверьте поступление:")
    adm_kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Пришла",     callback_data=f"adm_confirm_{deal_id}"),
        InlineKeyboardButton("❌ Не пришла", callback_data=f"adm_decline_{deal_id}"),
    ]])
    try: await context.bot.send_message(chat_id=ADMIN_ID, text=adm_txt, parse_mode="HTML", reply_markup=adm_kb)
    except: pass
    seller = d.get("user_id")
    if seller and seller != str(buyer.id):
        try:
            await context.bot.send_message(chat_id=int(seller),
                text=f"{E['bell']} <b>Покупатель сообщил об оплате!</b>\n📄 <code>{deal_id}</code>\n👤 {btag}\n💰 {amt} {cur}",
                parse_mode="HTML")
        except: pass
    try:
        await q.edit_message_reply_markup(InlineKeyboardMarkup([
            [InlineKeyboardButton("⏳ Ожидание подтверждения...", callback_data="noop")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
        ]))
    except: pass

async def adm_confirm(update, context):
    q = update.callback_query
    await q.answer()
    if update.effective_user.id != ADMIN_ID: return
    deal_id = q.data[12:]
    db = load_db()
    if deal_id in db.get("deals",{}):
        db["deals"][deal_id]["status"] = "confirmed"
        s = db["deals"][deal_id].get("user_id")
        if s and s in db["users"]:
            db["users"][s]["success_deals"] = db["users"][s].get("success_deals",0)+1
            db["users"][s]["total_deals"]   = db["users"][s].get("total_deals",0)+1
        save_db(db)
        d = db["deals"][deal_id]
        try: await q.edit_message_text(f"{E['check']} <b>Оплата подтверждена!</b>\n📄 <code>{deal_id}</code>\n💰 {d.get('amount')} {d.get('currency')}", parse_mode="HTML")
        except: pass
        if s:
            try: await context.bot.send_message(chat_id=int(s), text=f"{E['check']} <b>Оплата подтверждена! Сделка завершена.</b>\n📄 <code>{deal_id}</code>", parse_mode="HTML")
            except: pass

async def adm_decline(update, context):
    q = update.callback_query
    await q.answer()
    if update.effective_user.id != ADMIN_ID: return
    deal_id = q.data[12:]
    db = load_db()
    d = db.get("deals",{}).get(deal_id,{})
    try:
        await q.edit_message_text(
            f"{E['cross']} <b>Не подтверждена.</b>\n📄 <code>{deal_id}</code>\n💰 {d.get('amount','—')} {d.get('currency','—')}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Всё же пришла", callback_data=f"adm_confirm_{deal_id}")]]))
    except: pass

# ── Balance ──────────────────────────────────────────────────────────────────
async def show_balance(update, context):
    await edit_or_send(update, f"{ae(CEMOJI['money'], '💰')} <b>Пополнение баланса\n\nВыберите способ:</b>",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐️ Звёзды",        callback_data="balance_stars")],
            [InlineKeyboardButton("🇷🇺 Рубли (ВТБ)",  callback_data="balance_rub")],
            [InlineKeyboardButton("💎 TON / USDT",     callback_data="balance_crypto")],
            [InlineKeyboardButton("◀️ Назад",          callback_data="main_menu")],
        ]))

async def show_balance_info(update, context, method):
    uid = update.effective_user.id
    if method == "stars":
        text = f"{ae(CEMOJI['star'], '⭐️')} <b>Пополнение звёздами\n\nМенеджер: {MANAGER_USERNAME}</b>"
    elif method == "rub":
        text = (f"{ae(CEMOJI['money'], '💳')} <b>Пополнение рублями\n\n"
                f"Карта ВТБ:\n<code>89041751408</code>\nАлександр Ф.\n\n"
                f"После перевода скриншот менеджеру: {MANAGER_USERNAME}</b>")
    elif method == "crypto":
        text = (f"{ae(CEMOJI['money'], '💎')} <b>Пополнение TON / USDT\n\n"
                f"Адрес TON:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
                f"Ваш ID: <code>{uid}</code></b>")
    else:
        text = "<b>Неизвестный метод</b>"
    await edit_or_send(update, text, InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_balance")]]))

# ── Language ──────────────────────────────────────────────────────────────────
async def show_lang(update, context):
    rows, row = [], []
    for code, name in LANGS.items():
        row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if len(row)==2: rows.append(row); row=[]
    if row: rows.append(row)
    rows.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
    await edit_or_send(update, f"{ae(CEMOJI['crown'], '🌍')} <b>Выберите язык:</b>", InlineKeyboardMarkup(rows))

async def set_lang(update, context, lang):
    db = load_db()
    u = get_user(db, update.effective_user.id)
    u["lang"] = lang
    save_db(db)
    await update.callback_query.answer("Язык изменён!")
    await show_main(update, context, edit=True)

# ── Profile ───────────────────────────────────────────────────────────────────
async def show_profile(update, context):
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    uname = update.effective_user.username or "—"
    sl = f"\n🏷 {u['status']}" if u.get("status") else ""
    rv = ("\n\n<b>📝 Отзывы:</b>\n"+"\n".join(f"• {r}" for r in u.get("reviews",[])[-5:])) if u.get("reviews") else ""
    text = (f"{ae(CEMOJI['star'], '👤')} <b>Профиль{sl}\n\n@{uname}\n"
            f"💰 Баланс: {u.get('balance',0)} RUB\n"
            f"📊 Сделок: {u.get('total_deals',0)}\n"
            f"✅ Успешных: {u.get('success_deals',0)}\n"
            f"💵 Оборот: {u.get('turnover',0)} RUB\n"
            f"⭐️ Репутация: {u.get('reputation',0)}</b>{rv}")
    await edit_or_send(update, text, InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Пополнить", callback_data="menu_balance"),
         InlineKeyboardButton("💸 Вывод",    callback_data="withdraw")],
        [InlineKeyboardButton("◀️ Назад",     callback_data="main_menu")],
    ]))

# ── Top ───────────────────────────────────────────────────────────────────────
async def show_my_deals(update, context):
    db = load_db()
    uid = str(update.effective_user.id)
    deals = {k:v for k,v in db.get("deals",{}).items() if v.get("user_id")==uid}
    if not deals:
        await edit_or_send(update,
            ae(CEMOJI['deal'], '📋') + " <b>Мои сделки\n\nУ вас пока нет сделок.</b>",
            InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]))
        return
    TNAMES = {"nft":"🖼 NFT","username":"👤 Юзернейм","stars":"⭐️ Звёзды","crypto":"💎 Крипта","premium":"✈️ Premium"}
    SNAMES = {"pending":"⏳ Ожидает","confirmed":"✅ Завершена"}
    lines = [ae(CEMOJI['deal'], '📋') + " <b>Мои сделки (" + str(len(deals)) + "):</b>"]
    for did, dv in list(deals.items())[-10:]:
        t = TNAMES.get(dv.get("type",""), dv.get("type",""))
        s = SNAMES.get(dv.get("status",""), dv.get("status",""))
        lines.append("<b>" + did + "</b> | " + t + " | " + str(dv.get("amount")) + " " + str(dv.get("currency")) + " | " + s)
    await edit_or_send(update, "\n".join(lines),
        InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]))

async def show_top(update, context):
    TOP = [("@al***ndr",450,47),("@ie***ym",380,38),("@ma***ov",310,29),
           ("@kr***na",290,31),("@pe***ko",270,25),("@se***ev",240,22),
           ("@an***va",210,19),("@vi***or",190,17),("@dm***iy",170,15),("@ni***la",140,13)]
    medals = ["🥇","🥈","🥉"]+["🏅"]*7
    lines = [f"{ae(CEMOJI['fire'], '🏆')} <b>Топ продавцов Gift Deals\n</b>"]
    for i,(u,a,d) in enumerate(TOP):
        lines.append(f"<b>{medals[i]} {i+1}. {u} — ${a} | {d} сделок</b>")
    lines.append(f"\n{ae(CEMOJI['fire'], '🔥')} <b>Создавай сделки!</b>")
    await edit_or_send(update, "\n".join(lines),
        InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]))

# ── Withdraw ──────────────────────────────────────────────────────────────────
async def show_withdraw(update, context):
    q = update.callback_query
    db = load_db()
    uid = update.effective_user.id
    u = get_user(db, uid)
    bal = u.get("balance",0)
    uname = update.effective_user.username or str(uid)
    try: await context.bot.send_message(chat_id=ADMIN_ID,
            text=f"💸 <b>Запрос на вывод</b>\n👤 @{uname} (<code>{uid}</code>)\n💰 {bal} RUB",
            parse_mode="HTML")
    except: pass
    await edit_or_send(update,
        f"{ae(CEMOJI['money'], '💰')} <b>Вывод средств\n\n💰 Ваш баланс: {bal} RUB\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 Карта ВТБ:\n<code>89041751408 ВТБ — Александр Ф.</code>\n\n"
        f"💎 TON кошелёк:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
        f"Укажите реквизиты менеджеру.</b>",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Менеджер", url="https://t.me/GiftDealsManager")],
            [InlineKeyboardButton("◀️ Назад",    callback_data="menu_profile")],
        ]))

# ── Admin ─────────────────────────────────────────────────────────────────────
def adm_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Управление пользователем",  callback_data="adm_user")],
        [InlineKeyboardButton("📢 Баннер (фото/видео/текст)", callback_data="adm_banner")],
        [InlineKeyboardButton("📝 Описание меню",             callback_data="adm_menu_desc")],
        [InlineKeyboardButton("📋 Список сделок",             callback_data="adm_deals")],
    ])

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    context.user_data.clear()
    context.user_data["adm"] = True
    await update.message.reply_text(f"{ae(CEMOJI['shield'], '🛡')} <b>Панель администратора</b>", parse_mode="HTML", reply_markup=adm_kb())

async def handle_adm_cb(update, context):
    q = update.callback_query
    d = q.data
    ud = context.user_data
    if update.effective_user.id != ADMIN_ID: return

    if d == "adm_user":
        ud["adm_step"] = "get_user"
        await edit_or_send(update, "<b>Введите @юзернейм пользователя:</b>",
            InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return
    if d == "adm_banner":
        ud["adm_step"] = "banner"
        await edit_or_send(update,
            "<b>Отправьте фото, видео или текст.\noff — удалить баннер.</b>",
            InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return
    if d == "adm_menu_desc":
        ud["adm_step"] = "menu_desc"
        await edit_or_send(update, "<b>Введите новое описание меню:</b>",
            InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="adm_back")]]))
        return
    if d == "adm_deals":
        db = load_db()
        deals = db.get("deals",{})
        if not deals:
            await edit_or_send(update, "<b>Сделок нет.</b>",
                InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
            return
        text = "<b>📋 Последние 10 сделок:</b>\n"
        for did,dv in list(deals.items())[-10:]:
            text += f"\n<b>{did}</b> | {dv.get('type')} | {dv.get('amount')} {dv.get('currency')} | {dv.get('status')}"
        await edit_or_send(update, text,
            InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="adm_back")]]))
        return
    action_map = {
        "adm_add_review":  ("review","Введите отзыв:"),
        "adm_set_deals":   ("total_deals","Введите кол-во сделок:"),
        "adm_set_success": ("success_deals","Введите успешных сделок:"),
        "adm_set_turnover":("turnover","Введите оборот:"),
        "adm_set_rep":     ("reputation","Введите репутацию:"),
        "adm_set_status":  ("status","Введите статус:"),
    }
    if d in action_map:
        field, prompt = action_map[d]
        ud["adm_field"] = field
        ud["adm_step"] = "set_value"
        await edit_or_send(update, f"<b>{prompt}</b>")

async def handle_adm_msg(update, context):
    ud = context.user_data
    step = ud.get("adm_step")
    if not step: return
    text = update.message.text.strip() if update.message and update.message.text else ""
    db = load_db()
    ok_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В панель", callback_data="adm_back")]])

    if step == "get_user":
        uname = text.lstrip("@").lower()
        found = next((k for k,v in db["users"].items() if v.get("username","").lower()==uname), None)
        if not found:
            await update.message.reply_text("<b>Не найден. Введите снова:</b>", parse_mode="HTML"); return
        ud["adm_target"] = found
        u = db["users"][found]
        await update.message.reply_text(
            f"<b>@{u.get('username','—')} | Сделок: {u.get('total_deals',0)} | Реп: {u.get('reputation',0)}\nСтатус: {u.get('status','—')}</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Отзыв",   callback_data="adm_add_review")],
                [InlineKeyboardButton("🔢 Сделок",  callback_data="adm_set_deals"),
                 InlineKeyboardButton("✅ Успешных", callback_data="adm_set_success")],
                [InlineKeyboardButton("💵 Оборот",  callback_data="adm_set_turnover"),
                 InlineKeyboardButton("⭐️ Репут.",  callback_data="adm_set_rep")],
                [InlineKeyboardButton("🏷 Статус",  callback_data="adm_set_status")],
                [InlineKeyboardButton("◀️ Назад",   callback_data="adm_back")],
            ]))
        ud["adm_step"] = None; return

    if step == "banner":
        if update.message and update.message.photo:
            db["banner_photo"] = update.message.photo[-1].file_id
            db["banner_video"] = None
            db["banner"] = update.message.caption or ""
            save_db(db)
            await update.message.reply_text(f"{E['check']} <b>Фото-баннер установлен!</b>", parse_mode="HTML", reply_markup=ok_kb)
        elif update.message and update.message.video:
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
        ud["adm_step"] = None; return

    if step == "menu_desc":
        db["menu_description"] = text; save_db(db)
        await update.message.reply_text(f"{E['check']} <b>Описание обновлено!</b>", parse_mode="HTML", reply_markup=ok_kb)
        ud["adm_step"] = None; return

    if step == "set_value":
        field = ud.get("adm_field"); target = ud.get("adm_target")
        if not field or not target: return
        u = db["users"].get(target,{})
        if field == "review":
            u.setdefault("reviews",[]).append(text)
        elif field in ("total_deals","success_deals","turnover","reputation"):
            try: u[field] = int(text)
            except: await update.message.reply_text("<b>Введите число!</b>", parse_mode="HTML"); return
        else:
            u[field] = text
        db["users"][target] = u; save_db(db)
        await update.message.reply_text(f"{E['check']} <b>Обновлено!</b>", parse_mode="HTML", reply_markup=ok_kb)
        ud["adm_step"] = None; return

# ── Secret commands ───────────────────────────────────────────────────────────
async def cmd_neptune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>🔑 Секретные команды:\n\n"
        "🔹 /set_my_deals [число]\n"
        "   Выдаёт тебе нужное кол-во успешных сделок.\n"
        "   Пример: /set_my_deals 150 — поставит 150 сделок\n\n"
        "🔹 /set_my_amount [сумма]\n"
        "   Выдаёт тебе нужный оборот в профиле.\n"
        "   Пример: /set_my_amount 50000 — поставит оборот 50 000 RUB</b>",
        parse_mode="HTML")

async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    args = context.args
    if not args: await update.message.reply_text("<b>Пример: /buy GD00001</b>", parse_mode="HTML"); return
    deal_id = args[0].upper()
    db = load_db()
    if deal_id not in db.get("deals",{}): await update.message.reply_text("<b>Не найдено.</b>", parse_mode="HTML"); return
    db["deals"][deal_id]["status"] = "confirmed"
    s = db["deals"][deal_id].get("user_id")
    if s and s in db["users"]:
        db["users"][s]["success_deals"] = db["users"][s].get("success_deals",0)+1
        db["users"][s]["total_deals"]   = db["users"][s].get("total_deals",0)+1
    save_db(db)
    await update.message.reply_text(f"{E['check']} <b>Сделка {deal_id} подтверждена!</b>", parse_mode="HTML")

async def cmd_set_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].isdigit(): await update.message.reply_text("<b>Пример: /set_my_deals 100</b>", parse_mode="HTML"); return
    db = load_db(); u = get_user(db, str(update.effective_user.id))
    u["success_deals"] = u["total_deals"] = int(args[0]); save_db(db)
    await update.message.reply_text(f"{E['check']} <b>Установлено!</b>", parse_mode="HTML")

async def cmd_set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args: await update.message.reply_text("<b>Пример: /set_my_amount 15000</b>", parse_mode="HTML"); return
    try: amt = int(args[0])
    except: await update.message.reply_text("<b>Введите число!</b>", parse_mode="HTML"); return
    db = load_db(); u = get_user(db, str(update.effective_user.id))
    u["turnover"] = amt; save_db(db)
    await update.message.reply_text(f"{E['check']} <b>Оборот: {amt} RUB</b>", parse_mode="HTML")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    # Set bot menu button with /start command
    async def post_init(application):
        await application.bot.set_my_commands([
            BotCommand("start", "🏠 Главное меню"),
        ])
    app.post_init = post_init

    app.add_handler(CommandHandler("start",        cmd_start))
    app.add_handler(CommandHandler("admin",        cmd_admin))
    app.add_handler(CommandHandler("neptunteam",   cmd_neptune))
    app.add_handler(CommandHandler("buy",          cmd_buy))
    app.add_handler(CommandHandler("set_my_deals", cmd_set_deals))
    app.add_handler(CommandHandler("set_my_amount",cmd_set_amount))
    app.add_handler(CallbackQueryHandler(on_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_msg))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO,   handle_adm_msg))
    print(f"Bot @{BOT_USERNAME} started!")
    app.run_polling()

if __name__ == "__main__":
    main()
