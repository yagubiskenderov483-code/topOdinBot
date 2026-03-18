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

BOT_TOKEN = "8636524725:AAHohfHayrAE2MXswcFMHHiC4kLoI7fd5XE"
ADMIN_ID = 174415647
BOT_USERNAME = "GiftDealsRobot"
MANAGER_USERNAME = "@GiftDealsManager"
CRYPTO_ADDRESS = "UQDGN5pfjPxorFyjN2xha84bapuADDtPcRofNDJ4dK2YXxZd"
CRYPTO_BOT = "https://t.me/send?start=IVbfPL7Tk4XA"
CARD_NUMBER = "+79041751408"
CARD_NAME = "Александр Ф."
CARD_BANK = "ВТБ"
DB_FILE = "db.json"

def ce(eid, fb):
    return f"<tg-emoji emoji-id='{eid}'>{fb}</tg-emoji>"

E = {
    "user":      ce("5199552030615558774", "👤"),
    "star":      ce("5267500801240092311", "⭐"),
    "shield":    ce("5197434882321567830", "⭐"),
    "gift":      ce("5197369495739455200", "💵"),
    "lock":      ce("5197161121106123533", "💶"),
    "globe":     ce("5377746319601324795", "💴"),
    "premium":   ce("5377620962390857342", "🪙"),
    "pencil":    ce("5197371802136892976", "⛏"),
    "card":      ce("5445353829304387411", "💳"),
    "cross":     ce("5443127283898405358", "📥"),
    "rocket":    ce("5444856076954520455", "🧾"),
    "sticker":   ce("5294167145079395967", "🛍"),
    "fire":      ce("5303138782004924588", "💬"),
    "bell":      ce("5312361253610475399", "🛒"),
    "deal":      ce("5445221832074483553", "💼"),
    "trophy":    ce("5332455502917949981", "🏦"),
    "check":     ce("5274055917766202507", "🗓"),
    "money":     ce("5278467510604160626", "💰"),
    "diamond":   ce("5264713049637409446", "🪙"),
    "nft":       ce("5193177581888755275", "💻"),
    "bag":       ce("5377660214096974712", "🛍"),
    "medal":     ce("5463289097336405244", "⭐️"),
    "gem":       ce("5258203794772085854", "⚡️"),
    "clock":     ce("5429651785352501917", "↗️"),
    "handshake": ce("5287231198098117669", "💰"),
    "crystal":   ce("5195033767969839232", "🚀"),
    "safe":      ce("5262517101578443800", "🖼"),
    "chart":     ce("5382194935057372936", "⏱"),
    "spark":     ce("5902449142575141204", "🔎"),
    "target":    ce("5893081007153746175", "❌"),
    "pin":       ce("5893297890117292323", "📞"),
    "wallet":    ce("5893382531037794941", "👛"),
    "num1":      ce("5794164805065514131", "1️⃣"),
    "num2":      ce("5794085322400733645", "2️⃣"),
    "num3":      ce("5794280000383358988", "3️⃣"),
    "num4":      ce("5794241397217304511", "4️⃣"),
    "bank":      ce("5238132025323444613", "🏦"),
    "banknote":  ce("5201873447554145566", "💵"),
    "link":      ce("5902449142575141204", "🔗"),
    "shine":     ce("5235630047959727475", "💎"),
    "store":     ce("4988289890769699938", "⭐️"),
}

CD  = ce("5235630047959727475", "💎")
CM  = ce("5278467510604160626", "💰")
CDL = ce("5445221832074483553", "💼")
CSH = ce("5197434882321567830", "⭐")
CL  = ce("5197161121106123533", "💶")
CG  = ce("5197369495739455200", "💵")
CF  = ce("5303138782004924588", "💬")
CS  = ce("5267500801240092311", "⭐")
CR  = ce("5195033767969839232", "🚀")

TNAMES = {
    "nft":              "🎁 NFT подарок",
    "username":         "🎴 NFT Username",
    "stars":            "⭐️ Звёзды Telegram",
    "crypto":           "💎 Крипта (TON/USDT)",
    "premium":          "✈️ Telegram Premium",
    "premium_stickers": "🎭 Премиум стикеры",
}

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "deals": {}, "banner": None, "banner_photo": None,
            "banner_video": None, "menu_description": None, "deal_counter": 1}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(db, uid):
    k = str(uid)
    if k not in db["users"]:
        db["users"][k] = {"username": "", "balance": 0, "total_deals": 0,
            "success_deals": 0, "turnover": 0, "reputation": 0,
            "reviews": [], "status": "", "lang": "ru"}
    return db["users"][k]

def get_lang(uid):
    try:
        db = load_db()
        return get_user(db, uid).get("lang", "ru")
    except:
        return "ru"

def gen_deal_id(db):
    n = db.get("deal_counter", 1)
    db["deal_counter"] = n + 1
    save_db(db)
    return f"GD{n:05d}"

LANGS = {
    "ru": "🇷🇺 Россия",    "en": "🇬🇧 English",
    "kz": "🇰🇿 Қазақстан", "az": "🇦🇿 Azərbaycan",
    "uz": "🇺🇿 O'zbek",    "kg": "🇰🇬 Кыргызстан",
    "tj": "🇹🇯 Тоҷикистон","by": "🇧🇾 Беларусь",
    "am": "🇦🇲 Հայաստան",  "ge": "🇬🇪 საქართველო",
    "ua": "🇺🇦 Україна",   "md": "🇲🇩 Moldova",
}

def get_welcome(lang):
    intros = {
        "en": "Gift Deals — the safest platform for deals in Telegram",
        "kz": "Gift Deals — Telegram-дағы ең қауіпсіз мәміле алаңы",
        "az": "Gift Deals — Telegram-da ən etibarlı əməliyyat platforması",
        "uz": "Gift Deals — Telegram'dagi eng ishonchli bitim platformasi",
        "kg": "Gift Deals — Telegram'дагы эң коопсуз бүтүм аянтчасы",
        "tj": "Gift Deals — бехтарин майдончаи муомилот дар Telegram",
        "by": "Gift Deals — самая надзейная пляцоўка для здзелак у Telegram",
        "am": "Gift Deals — Telegram-ի ամենահուսալի գործարքային հարթակը",
        "ge": "Gift Deals — Telegram-ის ყველაზე სანდო პლატფორმა",
        "ua": "Gift Deals — найнадійніша платформа для угод у Telegram",
        "md": "Gift Deals — cea mai sigură platformă pentru tranzacții în Telegram",
        "ru": "Gift Deals — самая безопасная площадка для сделок в Telegram",
    }
    items = {
        "ru": ["Автоматические сделки с НФТ и подарками","Полная защита обеих сторон","Средства заморожены до подтверждения","Передача через менеджера: @GiftDealsManager"],
        "en": ["Automatic deals with NFT and gifts","Full protection for both parties","Funds frozen until confirmation","Transfer via manager: @GiftDealsManager"],
        "kz": ["НФТ және сыйлықтармен автоматты мәмілелер","Екі тараптың толық қорғанысы","Растауға дейін қаражат бұғатталған","Менеджер арқылы: @GiftDealsManager"],
        "az": ["NFT və hədiyyələrlə avtomatik əməliyyatlar","Hər iki tərəf üçün tam qoruma","Təsdiqə qədər vəsaitlər dondurulur","Menecer vasitəsilə: @GiftDealsManager"],
        "uz": ["NFT va sovg'alar bilan avtomatik bitimlar","Ikkala tomon uchun to'liq himoya","Tasdiqlanguncha mablag'lar muzlatilgan","Menejer orqali: @GiftDealsManager"],
        "kg": ["НФТ жана белектер менен авто бүтүмдөр","Эки тараптын толук коргоосу","Тастыкталганга чейин каражат тоңдурулган","Менеджер аркылуу: @GiftDealsManager"],
        "tj": ["Муомилоти автоматӣ бо НФТ ва тӯҳфаҳо","Ҳифзи пурраи ҳарду тараф","Маблағ то тасдиқ яхкарда аст","Тавассути менеҷер: @GiftDealsManager"],
        "by": ["Аўтаматычныя здзелкі з НФТ і падарункамі","Поўная абарона абодвух бакоў","Сродкі замарожаны да пацверджання","Перадача праз мэнэджара: @GiftDealsManager"],
        "am": ["Ավտոմատ գործարքներ NFT-ով և նվերներով","Երկու կողմի լիարժեք պաշտպանություն","Հաստատման ժամանակ միջոցները սառեցված են","Կառավարչի միջոցով: @GiftDealsManager"],
        "ge": ["ავტომატური გარიგებები NFT-ით და საჩუქრებით","ორივე მხარის სრული დაცვა","სახსრები დადასტურებამდე გაყინულია","მენეჯერის მეშვეობით: @GiftDealsManager"],
        "ua": ["Автоматичні угоди з НФТ та подарунками","Повний захист обох сторін","Кошти заморожені до підтвердження","Передача через менеджера: @GiftDealsManager"],
        "md": ["Tranzacții automate cu NFT și cadouri","Protecție completă pentru ambele părți","Fonduri înghețate până la confirmare","Transfer prin manager: @GiftDealsManager"],
    }
    intro = intros.get(lang, intros["ru"])
    pts = items.get(lang, items["ru"])
    nums = [E['num1'], E['num2'], E['num3'], E['num4']]
    lines = "\n".join(f"<blockquote>{nums[i]} {pts[i]}.</blockquote>" for i in range(4))
    return (
        f"{CD} <b>{intro}</b>\n\n"
        f"{lines}\n\n"
        f"{E['spark']} <b>{'Выберите действие ниже' if lang=='ru' else 'Choose an action below' if lang=='en' else '👇'}</b>"
    )

BTN = {
    "ru": {"deal": "💎 Создать сделку", "balance": "💸 Пополнить/Вывод", "lang": "🌍 Язык / Lang", "profile": "⭐ Профиль", "top": "🏆 Топ продавцов"},
    "en": {"deal": "💎 Create Deal", "balance": "💸 Top Up/Withdraw", "lang": "🌍 Language", "profile": "⭐ Profile", "top": "🏆 Top Sellers"},
    "kz": {"deal": "💎 Мәміле", "balance": "💸 Толықтыру/Шығару", "lang": "🌍 Тіл", "profile": "⭐ Профиль", "top": "🏆 Үздіктер"},
    "az": {"deal": "💎 Müqavilə", "balance": "💸 Doldur/Çıxar", "lang": "🌍 Dil", "profile": "⭐ Profil", "top": "🏆 Top"},
    "uz": {"deal": "💎 Bitim", "balance": "💸 To'ldirish/Chiqarish", "lang": "🌍 Til", "profile": "⭐ Profil", "top": "🏆 Top"},
    "kg": {"deal": "💎 Бүтүм", "balance": "💸 Толуктоо/Чыгаруу", "lang": "🌍 Тил", "profile": "⭐ Профиль", "top": "🏆 Топ"},
    "tj": {"deal": "💎 Муомила", "balance": "💸 Пур кардан/Баровардан", "lang": "🌍 Забон", "profile": "⭐ Профил", "top": "🏆 Топ"},
    "by": {"deal": "💎 Здзелка", "balance": "💸 Папоўніць/Вывесці", "lang": "🌍 Мова", "profile": "⭐ Профіль", "top": "🏆 Топ"},
    "am": {"deal": "💎 Գործ", "balance": "💸 Լրացնել/Հանել", "lang": "🌍 Lezun", "profile": "⭐ Profil", "top": "🏆 Top"},
    "ge": {"deal": "💎 გარიგება", "balance": "💸 შევსება/გამოტანა", "lang": "🌍 ენა", "profile": "⭐ პროფ.", "top": "🏆 საუკ."},
    "ua": {"deal": "💎 Угода", "balance": "💸 Поповнити/Вивести", "lang": "🌍 Мова", "profile": "⭐ Профіль", "top": "🏆 Топ"},
    "md": {"deal": "💎 Tranzacție", "balance": "💸 Reîncărcare/Retragere", "lang": "🌍 Limbă", "profile": "⭐ Profil", "top": "🏆 Top"},
}

CUR = {
    "TON": "💎 TON", "USDT": "💵 USDT",
    "Stars": {"ru": "⭐️ Звёзды", "en": "⭐️ Stars", "kz": "⭐️ Жұлдыздар", "az": "⭐️ Ulduzlar", "uz": "⭐️ Yulduzlar", "kg": "⭐️ Жылдыздар", "tj": "⭐️ Ситорахо", "by": "⭐️ Зоркі", "am": "⭐️ Աստղեր", "ge": "⭐️ ვარსკვლავები", "ua": "⭐️ Зірки", "md": "⭐️ Stele"},
    "RUB": {"ru": "🇷🇺 Рубли", "en": "🇷🇺 Rubles", "kz": "🇷🇺 Рубль", "az": "🇷🇺 Rublu", "uz": "🇷🇺 Rubl", "kg": "🇷🇺 Рубль", "tj": "🇷🇺 Рубл", "by": "🇷🇺 Рублі", "am": "🇷🇺 Ռուբլի", "ge": "🇷🇺 რუბლი", "ua": "🇷🇺 Рублі", "md": "🇷🇺 Ruble"},
    "KZT": {"ru": "🇰🇿 Тенге", "en": "🇰🇿 Tenge", "kz": "🇰🇿 Теңге", "az": "🇰🇿 Tenge", "uz": "🇰🇿 Tenge", "kg": "🇰🇿 Теңге", "tj": "🇰🇿 Тенге", "by": "🇰🇿 Тэнге", "am": "🇰🇿 Թենգե", "ge": "🇰🇿 თენგე", "ua": "🇰🇿 Тенге", "md": "🇰🇿 Tenge"},
    "AZN": {"ru": "🇦🇿 Манат", "en": "🇦🇿 Manat", "kz": "🇦🇿 Манат", "az": "🇦🇿 Manat", "uz": "🇦🇿 Manat", "kg": "🇦🇿 Манат", "tj": "🇦🇿 Манот", "by": "🇦🇿 Манат", "am": "🇦🇿 Մանաթ", "ge": "🇦🇿 მანათი", "ua": "🇦🇿 Манат", "md": "🇦🇿 Manat"},
    "KGS": {"ru": "🇰🇬 Сомы", "en": "🇰🇬 Som", "kz": "🇰🇬 Сом", "az": "🇰🇬 Som", "uz": "🇰🇬 Som", "kg": "🇰🇬 Сом", "tj": "🇰🇬 Сом", "by": "🇰🇬 Сомы", "am": "🇰🇬 Սոմ", "ge": "🇰🇬 სომი", "ua": "🇰🇬 Соми", "md": "🇰🇬 Som"},
    "UZS": {"ru": "🇺🇿 Сумы", "en": "🇺🇿 Sum", "kz": "🇺🇿 Сум", "az": "🇺🇿 Sum", "uz": "🇺🇿 So'm", "kg": "🇺🇿 Сум", "tj": "🇺🇿 Сум", "by": "🇺🇿 Сумы", "am": "🇺🇿 Սում", "ge": "🇺🇿 სუმი", "ua": "🇺🇿 Суми", "md": "🇺🇿 Sum"},
    "TJS": {"ru": "🇹🇯 Сомони", "en": "🇹🇯 Somoni", "kz": "🇹🇯 Сомонӣ", "az": "🇹🇯 Somoni", "uz": "🇹🇯 Somoni", "kg": "🇹🇯 Сомонӣ", "tj": "🇹🇯 Сомонӣ", "by": "🇹🇯 Саманi", "am": "🇹🇯 Սոմոնի", "ge": "🇹🇯 სომონი", "ua": "🇹🇯 Сомоні", "md": "🇹🇯 Somoni"},
    "BYN": {"ru": "🇧🇾 Рубли BY", "en": "🇧🇾 BYN", "kz": "🇧🇾 Руб. BY", "az": "🇧🇾 Rubl BY", "uz": "🇧🇾 Rubl BY", "kg": "🇧🇾 Руб. BY", "tj": "🇧🇾 Руб. BY", "by": "🇧🇾 Рублі", "am": "🇧🇾 Ռուբ. BY", "ge": "🇧🇾 რუბ. BY", "ua": "🇧🇾 Рублі BY", "md": "🇧🇾 Ruble BY"},
    "UAH": {"ru": "🇺🇦 Гривны", "en": "🇺🇦 Hryvnia", "kz": "🇺🇦 Гривна", "az": "🇺🇦 Qrivna", "uz": "🇺🇦 Grivna", "kg": "🇺🇦 Гривна", "tj": "🇺🇦 Гривна", "by": "🇺🇦 Грыўні", "am": "🇺🇦 Գրիվնա", "ge": "🇺🇦 გრივნა", "ua": "🇺🇦 Гривні", "md": "🇺🇦 Grivne"},
    "GEL": {"ru": "🇬🇪 Лари", "en": "🇬🇪 Lari", "kz": "🇬🇪 Лари", "az": "🇬🇪 Lari", "uz": "🇬🇪 Lari", "kg": "🇬🇪 Лари", "tj": "🇬🇪 Лари", "by": "🇬🇪 Лары", "am": "🇬🇪 Լարի", "ge": "🇬🇪 ლარი", "ua": "🇬🇪 Ларі", "md": "🇬🇪 Lari"},
}
CURMAP = {"cur_ton":"TON","cur_usdt":"USDT","cur_rub":"RUB","cur_stars":"Stars",
          "cur_kzt":"KZT","cur_azn":"AZN","cur_kgs":"KGS","cur_uzs":"UZS",
          "cur_tjs":"TJS","cur_byn":"BYN","cur_uah":"UAH","cur_gel":"GEL"}

def cur_name(code, lang):
    v = CUR.get(code, code)
    if isinstance(v, dict): return v.get(lang, v.get("ru", code))
    return v

# Название валюты на языке страны происхождения
CUR_NATIVE = {
    "TON": "TON", "USDT": "USDT",
    "Stars": "Stars", "RUB": "Рубли",
    "KZT": "Теңге", "AZN": "Manat",
    "KGS": "Сом", "UZS": "So'm",
    "TJS": "Сомонӣ", "BYN": "Рублі",
    "UAH": "Гривні", "GEL": "ლარი",
}

def cur_native(code):
    return CUR_NATIVE.get(code, code)

def cur_kb(lang):
    def n(c): return cur_name(c, lang)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(n("TON"),callback_data="cur_ton"),InlineKeyboardButton(n("USDT"),callback_data="cur_usdt")],
        [InlineKeyboardButton(n("RUB"),callback_data="cur_rub"),InlineKeyboardButton(n("Stars"),callback_data="cur_stars")],
        [InlineKeyboardButton(n("KZT"),callback_data="cur_kzt"),InlineKeyboardButton(n("AZN"),callback_data="cur_azn")],
        [InlineKeyboardButton(n("KGS"),callback_data="cur_kgs"),InlineKeyboardButton(n("UZS"),callback_data="cur_uzs")],
        [InlineKeyboardButton(n("TJS"),callback_data="cur_tjs"),InlineKeyboardButton(n("BYN"),callback_data="cur_byn")],
        [InlineKeyboardButton(n("UAH"),callback_data="cur_uah"),InlineKeyboardButton(n("GEL"),callback_data="cur_gel")],
    ])

async def send_text(update, text, kb=None):
    try: await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e: logger.error(f"send_text: {e}")

async def edit_or_send(update, text, kb=None):
    try: await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        try: await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception as e: logger.error(f"edit_or_send: {e}")

def main_kb(lang):
    b = BTN.get(lang, BTN["ru"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(b["deal"],callback_data="menu_deal"),InlineKeyboardButton(b["profile"],callback_data="menu_profile")],
        [InlineKeyboardButton(b["balance"],callback_data="menu_balance"),InlineKeyboardButton("🪪 Мои сделки",callback_data="menu_my_deals")],
        [InlineKeyboardButton(b["lang"],callback_data="menu_lang"),InlineKeyboardButton(b["top"],callback_data="menu_top")],
        [InlineKeyboardButton("🆘 Техподдержка",url="https://t.me/GiftDealsSupport")],
    ])

async def show_main(update, context, edit=False):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=u.get("lang","ru"); desc=db.get("menu_description") or get_welcome(lang)
        banner=db.get("banner") or ""; text=desc
        if banner: text+=f"\n\n<b>{banner}</b>"
        kb=main_kb(lang); bv=db.get("banner_video"); bp=db.get("banner_photo")
        if bv: await update.effective_message.reply_video(video=bv,caption=text,parse_mode="HTML",reply_markup=kb)
        elif bp: await update.effective_message.reply_photo(photo=bp,caption=text,parse_mode="HTML",reply_markup=kb)
        elif edit:
            try: await update.callback_query.edit_message_text(text,parse_mode="HTML",reply_markup=kb)
            except: await update.effective_message.reply_text(text,parse_mode="HTML",reply_markup=kb)
        else: await update.effective_message.reply_text(text,parse_mode="HTML",reply_markup=kb)
    except Exception as e: logger.error(f"show_main: {e}")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        db=load_db(); u=get_user(db,update.effective_user.id)
        u["username"]=update.effective_user.username or ""; save_db(db); context.user_data.clear()
        args=context.args
        if args and args[0].startswith("deal_"):
            deal_id=args[0][5:].upper(); d=db.get("deals",{}).get(deal_id)
            if d: await send_deal_card(update,context,deal_id,d,buyer=True); return
        await show_main(update,context)
    except Exception as e: logger.error(f"cmd_start: {e}")

def deal_types_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 NFT",callback_data="dt_nft"),InlineKeyboardButton("🎴 NFT Username",callback_data="dt_usr")],
        [InlineKeyboardButton("⭐️ Звёзды",callback_data="dt_str"),InlineKeyboardButton("💎 Крипта (TON/$)",callback_data="dt_cry")],
        [InlineKeyboardButton("✈️ Telegram Premium",callback_data="dt_prm")],
        [InlineKeyboardButton("🔙 Назад",callback_data="main_menu")],
    ])

async def on_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q=update.callback_query; await q.answer(); d=q.data
        ud=context.user_data; uid=update.effective_user.id; lang=get_lang(uid)
        if d=="main_menu":
            ud.clear()
            try: await q.message.delete()
            except: pass
            await show_main(update,context,edit=False); return
        if d=="menu_deal":
            ud.clear()
            try: await q.message.delete()
            except: pass
            await update.effective_message.reply_text(f"{E['pencil']} <b>Создать сделку\n\nВыберите тип:</b>",parse_mode="HTML",reply_markup=deal_types_kb()); return
        if d=="menu_balance":
            try: await q.message.delete()
            except: pass
            await show_balance(update,context); return
        if d=="balance_topup":
            await edit_or_send(update,f"{E['money']} <b>Выберите способ пополнения:</b>",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("⭐️ Звёзды",callback_data="balance_stars")],
                    [InlineKeyboardButton("💰 Рубли",callback_data="balance_rub")],
                    [InlineKeyboardButton("💎 TON / USDT",callback_data="balance_crypto")],
                    [InlineKeyboardButton("🔙 Назад",callback_data="menu_balance")],
                ])); return
        if d=="menu_lang":
            try: await q.message.delete()
            except: pass
            await show_lang(update,context); return
        if d=="menu_profile":
            try: await q.message.delete()
            except: pass
            await show_profile(update,context); return
        if d=="menu_top":
            try: await q.message.delete()
            except: pass
            await show_top(update,context); return
        if d=="menu_my_deals":
            try: await q.message.delete()
            except: pass
            await show_my_deals(update,context); return
        if d.startswith("balance_"): await show_balance_info(update,context,d[8:]); return
        if d=="withdraw": await show_withdraw(update,context); return
        if d.startswith("withdraw_"):
            method=d[9:]
            prompts={"stars":"Укажите @юзернейм получателя звёзд:","crypto":"Укажите TON/USDT адрес для вывода:","card":"Укажите номер карты для вывода:"}
            context.user_data["withdraw_method"]=method; context.user_data["withdraw_step"]="requisite"
            await edit_or_send(update,f"{E['wallet']} <b>Вывод средств</b>\n\n<blockquote>{prompts.get(method,'Укажите реквизиты:')}</blockquote>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="withdraw")]])); return
        if d.startswith("rev_"):
            parts=d.split("_"); deal_id=parts[1]; role=parts[2]; stars=int(parts[3])
            context.user_data["review_deal"]=deal_id; context.user_data["review_role"]=role; context.user_data["review_stars"]=stars
            context.user_data["review_step"]="text"
            await q.edit_message_text(f"{'⭐️'*stars} Оценка: {stars}/5\n\nНапишите комментарий к отзыву:",parse_mode="HTML"); return
        if d.startswith("paid_"): await on_paid(update,context); return
        if d=="noop": return
        if d.startswith("adm_confirm_"): await adm_confirm(update,context); return
        if d.startswith("adm_decline_"): await adm_decline(update,context); return
        if d=="adm_back": await edit_or_send(update,f"{E['shield']} <b>Панель администратора</b>",adm_kb()); return
        if d.startswith("adm_"): await handle_adm_cb(update,context); return
        type_map={"dt_nft":"nft","dt_usr":"username","dt_str":"stars","dt_cry":"crypto","dt_prm":"premium","dt_pst":"premium_stickers"}
        if d in type_map:
            ud.clear(); ud["type"]=type_map[d]; ud["step"]="partner"
            icons={"nft":E["nft"],"username":E["user"],"stars":E["star"],"crypto":E["diamond"],"premium":E["premium"],"premium_stickers":E["sticker"]}
            icon=icons.get(type_map[d],E["deal"])
            await send_text(update,f"{icon} <b>Введите @юзернейм партнёра:</b>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="menu_deal")]])); return
        if d=="cry_ton": ud["currency"]="TON"; ud["step"]="amount"; await send_text(update,f"{E['diamond']} <b>Крипта (TON)\n\nВведите сумму:</b>"); return
        if d=="cry_usd": ud["currency"]="USDT"; ud["step"]="amount"; await send_text(update,f"{E['diamond']} <b>Крипта (USDT)\n\nВведите сумму:</b>"); return
        if d in ("prm_3","prm_6","prm_12"):
            periods={"prm_3":"3 месяца","prm_6":"6 месяцев","prm_12":"12 месяцев"}
            ud["premium_period"]=periods[d]; ud["step"]="currency"
            await send_text(update,f"{E['premium']} <b>Telegram Premium\n\nВыберите валюту:</b>",cur_kb(lang)); return
        if d in ("pst_1","pst_3","pst_5","pst_10"):
            counts={"pst_1":"1 пак","pst_3":"3 пака","pst_5":"5 паков","pst_10":"10 паков"}
            ud["sticker_count"]=counts[d]; ud["step"]="currency"
            await send_text(update,f"{E['sticker']} <b>Премиум стикеры\n\nВыберите валюту:</b>",cur_kb(lang)); return
        if d.startswith("cur_"):
            ud["currency"]=CURMAP.get(d,d); ud["step"]="amount"
            icons={"nft":E["nft"],"username":E["user"],"stars":E["star"],"premium":E["premium"],"premium_stickers":E["sticker"]}
            icon=icons.get(ud.get("type",""),E["deal"])
            await send_text(update,f"{icon} <b>Введите сумму сделки:</b>"); return
    except Exception as e: logger.error(f"on_cb: {e}")

async def on_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ud=context.user_data; uid=update.effective_user.id; lang=get_lang(uid)
        text=update.message.text.strip() if update.message.text else ""
        if uid==ADMIN_ID and ud.get("adm_step"): await handle_adm_msg(update,context); return
        # Обработка реквизитов вывода
        if ud.get("withdraw_step")=="requisite":
            method=ud.get("withdraw_method","?"); db=load_db()
            uid3=update.effective_user.id; u3=get_user(db,uid3); bal=u3.get("balance",0)
            uname3=update.effective_user.username or str(uid3)
            methods={"stars":"Звёзды","crypto":"Крипта","card":"Карта"}
            mname=methods.get(method,method)
            try: await context.bot.send_message(chat_id=ADMIN_ID,
                text=f"{E['gem']} <b>Запрос на вывод — {mname}</b>\n{E['user']} @{uname3} (<code>{uid3}</code>)\n{CM} {bal} RUB\n\nРеквизиты: <code>{text}</code>",parse_mode="HTML")
            except Exception as e: logger.error(f"withdraw req admin: {e}")
            ud.pop("withdraw_step",None); ud.pop("withdraw_method",None)
            await update.message.reply_text(f"{E['check']} <b>Запрос отправлен!</b>\n\n<blockquote>Способ: {mname}\nСумма: {bal} RUB\n\nМенеджер свяжется с вами в ближайшее время.</blockquote>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💬 Менеджер",url=f"https://t.me/{MANAGER_USERNAME.lstrip('@')}")],[InlineKeyboardButton("🏠 Главное меню",callback_data="main_menu")]])); return
            deal_id=ud.get("review_deal"); role=ud.get("review_role"); stars=ud.get("review_stars",5)
            db=load_db(); deal=db.get("deals",{}).get(deal_id,{})
            review_text=f"{'⭐️'*stars} {stars}/5 — {text}"
            # Продавец оценивает покупателя
            if role=="s":
                buyer_uid=next((k for k,v in db.get("users",{}).items() if v.get("username","").lower()==deal.get("partner","").lstrip("@").lower()),None)
                if buyer_uid:
                    db["users"][buyer_uid].setdefault("reviews",[]).append(review_text)
                    save_db(db)
            # Покупатель оценивает продавца
            elif role=="b":
                seller_uid=deal.get("user_id")
                if seller_uid and seller_uid in db.get("users",{}):
                    db["users"][seller_uid].setdefault("reviews",[]).append(review_text)
                    save_db(db)
            ud.pop("review_step",None); ud.pop("review_deal",None); ud.pop("review_role",None); ud.pop("review_stars",None)
            await update.message.reply_text(f"{E['check']} <b>Отзыв сохранён!</b>",parse_mode="HTML"); return
        dtype=ud.get("type"); step=ud.get("step")
        if not dtype or not step: return
        if step=="partner":
            if not text.startswith("@"):
                await update.message.reply_text(f"{E['cross']} <b>Юзернейм должен начинаться с @</b>",parse_mode="HTML"); return
            ud["partner"]=text
            if dtype=="nft": ud["step"]="nft_link"; await update.message.reply_text(f"{E['nft']} <b>НФТ\n\nВставьте ссылку на НФТ (https://...):</b>",parse_mode="HTML")
            elif dtype=="username": ud["step"]="trade_usr"; await update.message.reply_text(f"{E['user']} <b>Юзернейм\n\nВведите @юзернейм товара:</b>",parse_mode="HTML")
            elif dtype=="stars": ud["step"]="stars_cnt"; await update.message.reply_text(f"{E['star']} <b>Звёзды\n\nСколько звёзд?</b>",parse_mode="HTML")
            elif dtype=="crypto":
                ud["step"]="cry_currency"
                await update.message.reply_text(f"{E['diamond']} <b>Крипта\n\nВыберите валюту:</b>",parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 TON",callback_data="cry_ton"),InlineKeyboardButton("💵 USDT",callback_data="cry_usd")]]))
            elif dtype=="premium":
                ud["step"]="prem_period"
                await update.message.reply_text(f"{E['premium']} <b>Telegram Premium\n\nВыберите срок:</b>",parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("3 месяца",callback_data="prm_3"),InlineKeyboardButton("6 месяцев",callback_data="prm_6"),InlineKeyboardButton("12 месяцев",callback_data="prm_12")]]))
            elif dtype=="premium_stickers":
                ud["step"]="sticker_pack"
                await update.message.reply_text(f"{E['sticker']} <b>Премиум стикеры\n\nВыберите количество стикерпаков:</b>",parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("1 пак",callback_data="pst_1"),InlineKeyboardButton("3 пака",callback_data="pst_3")],[InlineKeyboardButton("5 паков",callback_data="pst_5"),InlineKeyboardButton("10 паков",callback_data="pst_10")]]))
            return
        if step=="nft_link":
            if not text.startswith("https://"):
                await update.message.reply_text(f"{E['cross']} <b>Ссылка должна начинаться с https://</b>",parse_mode="HTML"); return
            ud["nft_link"]=text; ud["step"]="currency"
            await update.message.reply_text(f"{E['nft']} <b>НФТ\n\nВыберите валюту:</b>",parse_mode="HTML",reply_markup=cur_kb(lang)); return
        if step=="trade_usr":
            if not text.startswith("@"):
                await update.message.reply_text(f"{E['cross']} <b>Юзернейм должен начинаться с @</b>",parse_mode="HTML"); return
            ud["trade_username"]=text; ud["step"]="currency"
            await update.message.reply_text(f"{E['user']} <b>Юзернейм\n\nВыберите валюту:</b>",parse_mode="HTML",reply_markup=cur_kb(lang)); return
        if step=="stars_cnt":
            if not text.isdigit():
                await update.message.reply_text(f"{E['cross']} <b>Только цифры!</b>",parse_mode="HTML"); return
            ud["stars_count"]=text; ud["step"]="currency"
            await update.message.reply_text(f"{E['star']} <b>Звёзды\n\nВыберите валюту:</b>",parse_mode="HTML",reply_markup=cur_kb(lang)); return
        if step=="amount":
            ud["amount"]=text; await finalize_deal(update,context); return
    except Exception as e: logger.error(f"on_msg: {e}")

async def finalize_deal(update, context):
    try:
        db=load_db(); ud=context.user_data
        deal_id=gen_deal_id(db); dtype=ud.get("type","?"); partner=ud.get("partner","—")
        currency=ud.get("currency","—"); amount=ud.get("amount","—"); user=update.effective_user
        db["deals"][deal_id]={"user_id":str(user.id),"type":dtype,"partner":partner,
            "currency":currency,"amount":amount,"status":"pending",
            "created":datetime.now().isoformat(),"data":dict(ud)}
        save_db(db); await send_deal_card(update,context,deal_id,db["deals"][deal_id],buyer=False)
        pname=partner.lstrip("@").lower() if partner.startswith("@") else None
        if pname:
            puid=next((k for k,v in db["users"].items() if v.get("username","").lower()==pname),None)
            if puid:
                try:
                    txt=build_buyer_card(deal_id,db["deals"][deal_id],f"@{user.username or str(user.id)}")
                    kb=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Я оплатил",callback_data=f"paid_{deal_id}")],[InlineKeyboardButton("🏠 Главное меню",callback_data="main_menu")]])
                    await context.bot.send_message(chat_id=int(puid),text=txt,parse_mode="HTML",reply_markup=kb)
                except Exception as e: logger.error(f"notify partner: {e}")
        context.user_data.clear()
    except Exception as e: logger.error(f"finalize_deal: {e}")

def build_item_line(dtype, dd):
    if dtype=="nft": return f"\n{E['link']} Ссылка: {dd.get('nft_link','—')}"
    elif dtype=="username": return f"\n{E['user']} Юзернейм: {dd.get('trade_username','—')}"
    elif dtype=="stars": return f"\n{E['star']} Звёзд: {dd.get('stars_count','—')}"
    elif dtype=="premium": return f"\n{E['clock']} Срок: {dd.get('premium_period','—')}"
    elif dtype=="premium_stickers": return f"\n{E['sticker']} Паков: {dd.get('sticker_count','—')}"
    return ""

def build_buyer_card(deal_id, d, seller_tag):
    dtype=d.get("type",""); cur=d.get("currency","—"); amt=d.get("amount","—")
    item=build_item_line(dtype,d.get("data",{}))
    item_str=f"\n{item.strip()}" if item.strip() else ""
    return (
        f"💼 <b>Сделка #{deal_id}</b>\n\n"
        f"<blockquote>"
        f"👤 Продавец: <b>{seller_tag}</b>\n"
        f"🛒 Покупатель: <b>Вы</b>\n"
        f"📦 Тип сделки: <b>{TNAMES.get(dtype,dtype)}</b>"
        f"{item_str}\n"
        f"💰 Сумма: <b>{amt} {cur_native(cur)}</b>"
        f"</blockquote>\n\n"
        f"🔒 <b>Гарантия безопасности</b>\n"
        f"<blockquote>Средства заморожены до подтверждения передачи. "
        f"Сделка защищена платформой Gift Deals.</blockquote>\n\n"
        f"💳 <b>Реквизиты для оплаты:</b>\n"
        f"<blockquote>"
        f"Банк: {CARD_BANK}\n"
        f"Телефон: <code>{CARD_NUMBER}</code>\n"
        f"Получатель: {CARD_NAME}\n\n"
        f"TON адрес:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
        f"Крипто бот: {CRYPTO_BOT}\n\n"
        f"Звёзды: @GiftDealsManager"
        f"</blockquote>\n\n"
        f"✅ После перевода нажмите кнопку <b>«Я оплатил»</b>"
    )

async def send_deal_card(update, context, deal_id, d, buyer=False):
    try:
        dtype=d.get("type",""); cur=d.get("currency","—"); amt=d.get("amount","—")
        partner=d.get("partner","—"); item=build_item_line(dtype,d.get("data",{}))
        db=load_db(); seller_uid=d.get("user_id")
        seller_name=f"@{update.effective_user.username}" if update.effective_user.username else f"#{update.effective_user.id}"
        item_str=f"\n{item.strip()}" if item.strip() else ""
        if buyer:
            pu=f"https://t.me/{partner.lstrip('@')}" if partner.startswith("@") else f"https://t.me/{MANAGER_USERNAME.lstrip('@')}"
            status_str=f"\n{E['medal']} Статус: <b>{db['users'][seller_uid].get('status','')}</b>" if seller_uid and seller_uid in db.get('users',{}) and db['users'][seller_uid].get('status') else ""
            text=(
                f"💼 <b>Сделка #{deal_id}</b>\n\n"
                f"<blockquote>"
                f"👤 Продавец: <b>{partner}</b>{status_str}\n"
                f"🛒 Покупатель: <b>Вы</b>\n"
                f"📦 Тип сделки: <b>{TNAMES.get(dtype,dtype)}</b>"
                f"{item_str}\n"
                f"💰 Сумма: <b>{amt} {cur_native(cur)}</b>"
                f"</blockquote>\n\n"
                f"🔒 <b>Гарантия безопасности</b>\n"
                f"<blockquote>Средства заморожены до подтверждения передачи. "
                f"Сделка защищена платформой Gift Deals.</blockquote>\n\n"
                f"💳 <b>Реквизиты для оплаты:</b>\n"
                f"<blockquote>"
                f"Банк: {CARD_BANK}\n"
                f"Телефон: <code>{CARD_NUMBER}</code>\n"
                f"Получатель: {CARD_NAME}\n\n"
                f"TON адрес:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
                f"Крипто бот: {CRYPTO_BOT}\n\n"
                f"Звёзды: @GiftDealsManager"
                f"</blockquote>\n\n"
                f"✅ После перевода нажмите кнопку <b>«Я оплатил»</b>"
            )
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Я оплатил",callback_data=f"paid_{deal_id}")],
                [InlineKeyboardButton("💬 Написать продавцу",url=pu)],
                [InlineKeyboardButton("🏠 Главное меню",callback_data="main_menu")]
            ])
        else:
            text=(
                f"✅ <b>Сделка создана #{deal_id}</b>\n\n"
                f"<blockquote>"
                f"👤 Продавец: <b>Вы</b>\n"
                f"🛒 Покупатель: <b>{partner}</b>\n"
                f"📦 Тип сделки: <b>{TNAMES.get(dtype,dtype)}</b>"
                f"{item_str}\n"
                f"💰 Сумма: <b>{amt} {cur_native(cur)}</b>"
                f"</blockquote>\n\n"
                f"🔗 Ссылка для покупателя:\n"
                f"<code>https://t.me/{BOT_USERNAME}?start=deal_{deal_id}</code>\n\n"
                f"📨 Отправьте ссылку партнёру."
            )
            kb=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню",callback_data="main_menu")]])
        await update.effective_message.reply_text(text,parse_mode="HTML",reply_markup=kb)
    except Exception as e: logger.error(f"send_deal_card: {e}")

async def on_paid(update, context):
    try:
        q=update.callback_query; await q.answer("Уведомление отправлено!")
        deal_id=q.data[5:]; buyer=update.effective_user
        btag=f"@{buyer.username}" if buyer.username else str(buyer.id)
        db=load_db(); d=db.get("deals",{}).get(deal_id,{})
        amt=d.get("amount","—"); cur=d.get("currency","—"); dtype=d.get("type","")
        adm_txt=(f"{E['bell']} <b>Покупатель нажал «Я оплатил»</b>\n\n{E['deal']} <code>{deal_id}</code>\n"
                 f"{E['user']} {btag} (<code>{buyer.id}</code>)\n{E['pin']} {TNAMES.get(dtype,dtype)}\n{CM} {amt} {cur}\n\nПроверьте поступление:")
        try:
            await context.bot.send_message(chat_id=ADMIN_ID,text=adm_txt,parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Пришла",callback_data=f"adm_confirm_{deal_id}"),InlineKeyboardButton("❌ Не пришла",callback_data=f"adm_decline_{deal_id}")]]))
        except Exception as e: logger.error(f"on_paid admin: {e}")
        seller=d.get("user_id")
        if seller and seller!=str(buyer.id):
            try:
                await context.bot.send_message(chat_id=int(seller),
                    text=f"{E['bell']} <b>Покупатель сообщил об оплате!</b>\n📄 <code>{deal_id}</code>\n{E['user']} {btag}\n{CM} {amt} {cur}",parse_mode="HTML")
            except Exception as e: logger.error(f"on_paid seller: {e}")
        try:
            await q.edit_message_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("⏳ Ожидание подтверждения...",callback_data="noop")],[InlineKeyboardButton("🏠 Главное меню",callback_data="main_menu")]]))
        except Exception as e: logger.error(f"on_paid edit: {e}")
    except Exception as e: logger.error(f"on_paid: {e}")

async def adm_confirm(update, context):
    try:
        q=update.callback_query; await q.answer()
        if update.effective_user.id!=ADMIN_ID: return
        deal_id=q.data[12:]; db=load_db()
        if deal_id in db.get("deals",{}):
            db["deals"][deal_id]["status"]="confirmed"
            d=db["deals"][deal_id]
            s=d.get("user_id")
            if s and s in db["users"]:
                db["users"][s]["success_deals"]=db["users"][s].get("success_deals",0)+1
                db["users"][s]["total_deals"]=db["users"][s].get("total_deals",0)+1
            save_db(db)
            try: await q.edit_message_text(f"{E['check']} <b>Оплата подтверждена!</b>\n<code>{deal_id}</code>\n{CM} {d.get('amount')} {d.get('currency')}",parse_mode="HTML")
            except Exception as e: logger.error(f"adm_confirm edit: {e}")
            # Уведомляем продавца с просьбой оставить отзыв
            if s:
                try:
                    buyer_tag=d.get("partner","—")
                    await context.bot.send_message(chat_id=int(s),
                        text=f"{E['check']} <b>Оплата подтверждена! Сделка завершена.</b>\n<code>{deal_id}</code>\n\n"
                             f"Оцените покупателя {buyer_tag}:",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("⭐️1",callback_data=f"rev_{deal_id}_s_1"),InlineKeyboardButton("⭐️2",callback_data=f"rev_{deal_id}_s_2"),InlineKeyboardButton("⭐️3",callback_data=f"rev_{deal_id}_s_3"),InlineKeyboardButton("⭐️4",callback_data=f"rev_{deal_id}_s_4"),InlineKeyboardButton("⭐️5",callback_data=f"rev_{deal_id}_s_5")],
                        ]))
                except Exception as e: logger.error(f"adm_confirm notify seller: {e}")
            # Уведомляем покупателя с просьбой оставить отзыв
            buyer_uid=None
            for uid_,u_ in db.get("users",{}).items():
                if u_.get("username","").lower()==d.get("partner","").lstrip("@").lower():
                    buyer_uid=uid_; break
            if buyer_uid:
                try:
                    seller_tag=f"@{db['users'].get(s,{}).get('username','продавец')}" if s else "продавца"
                    await context.bot.send_message(chat_id=int(buyer_uid),
                        text=f"{E['check']} <b>Сделка подтверждена!</b>\n<code>{deal_id}</code>\n\n"
                             f"Оцените продавца {seller_tag}:",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("⭐️1",callback_data=f"rev_{deal_id}_b_1"),InlineKeyboardButton("⭐️2",callback_data=f"rev_{deal_id}_b_2"),InlineKeyboardButton("⭐️3",callback_data=f"rev_{deal_id}_b_3"),InlineKeyboardButton("⭐️4",callback_data=f"rev_{deal_id}_b_4"),InlineKeyboardButton("⭐️5",callback_data=f"rev_{deal_id}_b_5")],
                        ]))
                except Exception as e: logger.error(f"adm_confirm notify buyer: {e}")
    except Exception as e: logger.error(f"adm_confirm: {e}")

async def adm_decline(update, context):
    try:
        q=update.callback_query; await q.answer()
        if update.effective_user.id!=ADMIN_ID: return
        deal_id=q.data[12:]; db=load_db(); d=db.get("deals",{}).get(deal_id,{})
        try: await q.edit_message_text(f"{E['cross']} <b>Не подтверждена.</b>\n📄 <code>{deal_id}</code>\n{CM} {d.get('amount','—')} {d.get('currency','—')}",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Всё же пришла",callback_data=f"adm_confirm_{deal_id}")]]))
        except Exception as e: logger.error(f"adm_decline edit: {e}")
    except Exception as e: logger.error(f"adm_decline: {e}")

async def show_balance(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        bal=u.get("balance",0)
        await edit_or_send(update,
            f"{E['money']} <b>Пополнить / Вывод</b>\n\n<blockquote>Баланс: {bal} RUB</blockquote>",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Пополнить",callback_data="balance_topup")],
                [InlineKeyboardButton("➖ Вывод",callback_data="withdraw")],
                [InlineKeyboardButton("🔙 Назад",callback_data="main_menu")],
            ]))
    except Exception as e: logger.error(f"show_balance: {e}")

async def show_balance_info(update, context, method):
    try:
        uid=update.effective_user.id
        if method=="stars":
            text=(f"⭐️ <b>Пополнение звёздами</b>\n\n"
                  f"<blockquote>Отправьте звёзды на:\n@GiftDealsManager\n\n"
                  f"После отправки баланс пополнится в течение 5 минут.</blockquote>")
        elif method=="rub":
            text=(f"💳 <b>Пополнение рублями</b>\n\n"
                  f"<blockquote>"
                  f"Банк: {CARD_BANK}\n"
                  f"Телефон: <code>{CARD_NUMBER}</code>\n"
                  f"Получатель: {CARD_NAME}\n\n"
                  f"После перевода баланс пополнится в течение 5 минут."
                  f"</blockquote>")
        elif method=="crypto":
            text=(f"💎 <b>Пополнение TON / USDT</b>\n\n"
                  f"<blockquote>"
                  f"TON адрес:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
                  f"Крипто бот: {CRYPTO_BOT}\n\n"
                  f"Ваш ID: <code>{uid}</code>"
                  f"</blockquote>")
        else: text="<b>Неизвестный метод</b>"
        await edit_or_send(update,text,InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="balance_topup")]]))
    except Exception as e: logger.error(f"show_balance_info: {e}")

async def show_lang(update, context):
    try:
        uid=update.effective_user.id; lang=get_lang(uid)
        LANG_TEXT={"ru":"Выберите язык:","en":"Select language:","kz":"Тілді таңдаңыз:","az":"Dil seçin:","uz":"Tilni tanlang:","kg":"Тилди тандаңыз:","tj":"Забонро интихоб кунед:","by":"Выберыце мову:","am":"Ընտրեք լեզուն:","ge":"აირჩიეთ ენა:","ua":"Оберіть мову:","md":"Selectați limba:"}
        prompt=LANG_TEXT.get(lang,"Выберите язык:")
        rows,row=[],[]
        for code,name in LANGS.items():
            row.append(InlineKeyboardButton(name,callback_data=f"lang_{code}"))
            if len(row)==2: rows.append(row); row=[]
        if row: rows.append(row)
        rows.append([InlineKeyboardButton("🔙 Назад",callback_data="main_menu")])
        await edit_or_send(update,f"{E['globe']} <b>{prompt}</b>",InlineKeyboardMarkup(rows))
    except Exception as e: logger.error(f"show_lang: {e}")

async def set_lang(update, context, lang):
    try:
        db=load_db(); u=get_user(db,update.effective_user.id); u["lang"]=lang; save_db(db)
        await update.callback_query.answer("✅")
        try: await update.callback_query.message.delete()
        except: pass
        await show_main(update,context,edit=False)
    except Exception as e: logger.error(f"set_lang: {e}")

async def show_profile(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        uname=update.effective_user.username or "—"
        status=u.get("status","")
        sl=f"\n<blockquote>Статус: {status}</blockquote>" if status else ""
        rv=("\n\n<b>📝 Отзывы:</b>\n"+"\n".join(f"• {r}" for r in u.get("reviews",[])[-5:])) if u.get("reviews") else ""
        text=(f"{E['user']} <b>Профиль{sl}\n\n@{uname}\n{CM} Баланс: {u.get('balance',0)} RUB\n"
              f"{E['chart']} Сделок: {u.get('total_deals',0)}\n{E['check']} Успешных: {u.get('success_deals',0)}\n"
              f"{E['money']} Оборот: {u.get('turnover',0)} RUB\n{E['medal']} Репутация: {u.get('reputation',0)}</b>{rv}")
        await edit_or_send(update,text,InlineKeyboardMarkup([[InlineKeyboardButton("➕ Пополнить",callback_data="menu_balance"),InlineKeyboardButton("💸 Вывод",callback_data="withdraw")],[InlineKeyboardButton("🔙 Назад",callback_data="main_menu")]]))
    except Exception as e: logger.error(f"show_profile: {e}")

async def show_my_deals(update, context):
    try:
        db=load_db(); uid=str(update.effective_user.id)
        deals={k:v for k,v in db.get("deals",{}).items() if v.get("user_id")==uid}
        if not deals:
            await edit_or_send(update,f"{E['deal']} <b>Мои сделки\n\nУ вас пока нет сделок.</b>",InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="main_menu")]])); return
        SNAMES={"pending":"⏳ Ожидает","confirmed":"✅ Завершена"}
        lines=[f"{E['deal']} <b>Мои сделки ({len(deals)}):</b>"]
        for did,dv in list(deals.items())[-10:]:
            t=TNAMES.get(dv.get("type",""),dv.get("type","")); s=SNAMES.get(dv.get("status",""),dv.get("status",""))
            lines.append(f"<b>{did}</b> | {t} | {dv.get('amount')} {dv.get('currency')} | {s}")
        await edit_or_send(update,"\n".join(lines),InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="main_menu")]]))
    except Exception as e: logger.error(f"show_my_deals: {e}")

async def show_top(update, context):
    try:
        TOP=[("@al***ndr",450,47),("@ie***ym",380,38),("@ma***ov",310,29),("@kr***na",290,31),("@pe***ko",270,25),("@se***ev",240,22),("@an***va",210,19),("@vi***or",190,17),("@dm***iy",170,15),("@ni***la",140,13)]
        medals=["🥇","🥈","🥉"]+["🏅"]*7
        lines=[f"{E['trophy']} <b>Топ продавцов Gift Deals\n</b>"]
        for i,(u,a,d) in enumerate(TOP): lines.append(f"<b>{medals[i]} {i+1}. {u} — ${a} | {d} сделок</b>")
        lines.append(f"\n{E['rocket']} <b>Создавай сделки!</b>")
        await edit_or_send(update,"\n".join(lines),InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="main_menu")]]))
    except Exception as e: logger.error(f"show_top: {e}")

async def show_withdraw(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        bal=u.get("balance",0)
        if bal<=0:
            await edit_or_send(update,f"{E['cross']} <b>Недостаточно средств для вывода.</b>\n\n<blockquote>Ваш баланс: {bal} RUB</blockquote>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="menu_balance")]])); return
        await edit_or_send(update,
            f"{E['wallet']} <b>Вывод средств</b>\n\n<blockquote>Ваш баланс: {bal} RUB\n\nВыберите способ вывода:</blockquote>",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("⭐️ Звёзды",callback_data="withdraw_stars")],
                [InlineKeyboardButton("💎 Крипта (TON/USDT)",callback_data="withdraw_crypto")],
                [InlineKeyboardButton("💳 На карту",callback_data="withdraw_card")],
                [InlineKeyboardButton("🔙 Назад",callback_data="menu_balance")],
            ]))
    except Exception as e: logger.error(f"show_withdraw: {e}")

def adm_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Управление пользователем",callback_data="adm_user")],
        [InlineKeyboardButton("🖼 Баннер (фото/видео/текст)",callback_data="adm_banner")],
        [InlineKeyboardButton("✏️ Описание меню",callback_data="adm_menu_desc")],
        [InlineKeyboardButton("🗂 Список сделок",callback_data="adm_deals")],
    ])

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: return
    context.user_data.clear(); context.user_data["adm"]=True
    await update.message.reply_text(f"{E['shield']} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())

async def handle_adm_cb(update, context):
    try:
        q=update.callback_query; d=q.data; ud=context.user_data
        if update.effective_user.id!=ADMIN_ID: return
        if d=="adm_user":
            ud["adm_step"]="get_user"
            await edit_or_send(update,"<b>Введите @юзернейм пользователя:</b>",InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return
        if d=="adm_banner":
            ud["adm_step"]="banner"
            await edit_or_send(update,"<b>Отправьте фото, видео или текст.\noff — удалить баннер.</b>",InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Отмена",callback_data="adm_back")]])); return
        if d=="adm_menu_desc":
            ud["adm_step"]="menu_desc"
            await edit_or_send(update,"<b>Введите новое описание меню:</b>",InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Отмена",callback_data="adm_back")]])); return
        if d=="adm_deals":
            db=load_db(); deals=db.get("deals",{})
            if not deals:
                await edit_or_send(update,"<b>Сделок нет.</b>",InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return
            text="<b>📋 Последние 10 сделок:</b>\n"
            for did,dv in list(deals.items())[-10:]:
                text+=f"\n<b>{did}</b> | {TNAMES.get(dv.get('type',''),dv.get('type',''))} | {dv.get('amount')} {dv.get('currency')} | {dv.get('status')}"
            await edit_or_send(update,text,InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return
        action_map={"adm_add_review":("review","Введите отзыв:"),"adm_set_deals":("total_deals","Введите кол-во сделок:"),"adm_set_success":("success_deals","Введите успешных сделок:"),"adm_set_turnover":("turnover","Введите оборот:"),"adm_set_rep":("reputation","Введите репутацию:"),"adm_set_status":("status","Введите статус:")}
        if d in action_map:
            field,prompt=action_map[d]; ud["adm_field"]=field; ud["adm_step"]="set_value"
            await edit_or_send(update,f"<b>{prompt}</b>")
        status_map={"adm_status_verified":"✅ Проверенный","adm_status_garant":"🛡 Гарант","adm_status_caution":"⚠️ Осторожно","adm_status_scammer":"🚫 Мошенник","adm_status_clear":""}
        if d in status_map:
            target=ud.get("adm_target")
            if target:
                db=load_db(); u=db["users"].get(target,{})
                u["status"]=status_map[d]; db["users"][target]=u; save_db(db)
                await q.answer(f"Статус установлен: {status_map[d] or 'убран'}")
                try: await q.edit_message_reply_markup(reply_markup=None)
                except: pass
    except Exception as e: logger.error(f"handle_adm_cb: {e}")

async def handle_adm_msg(update, context):
    try:
        ud=context.user_data; step=ud.get("adm_step")
        if not step: return
        text=update.message.text.strip() if update.message and update.message.text else ""
        db=load_db(); ok_kb=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 В панель",callback_data="adm_back")]])
        if step=="get_user":
            uname=text.lstrip("@").lower()
            found=next((k for k,v in db["users"].items() if v.get("username","").lower()==uname),None)
            if not found:
                await update.message.reply_text("<b>Не найден. Введите снова:</b>",parse_mode="HTML"); return
            ud["adm_target"]=found; u=db["users"][found]
            sl = u.get('status','—')
            await update.message.reply_text(
                f"<b>@{u.get('username','—')} | Сделок: {u.get('total_deals',0)} | Реп: {u.get('reputation',0)}\nСтатус: {sl}</b>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📝 Отзыв",callback_data="adm_add_review")],
                    [InlineKeyboardButton("🔢 Сделок",callback_data="adm_set_deals"),InlineKeyboardButton("✅ Успешных",callback_data="adm_set_success")],
                    [InlineKeyboardButton("💵 Оборот",callback_data="adm_set_turnover"),InlineKeyboardButton("⭐️ Репут.",callback_data="adm_set_rep")],
                    [InlineKeyboardButton("🏷 Свой статус",callback_data="adm_set_status")],
                    [InlineKeyboardButton("✅ Проверенный",callback_data="adm_status_verified"),InlineKeyboardButton("🛡 Гарант",callback_data="adm_status_garant")],
                    [InlineKeyboardButton("⚠️ Осторожно",callback_data="adm_status_caution"),InlineKeyboardButton("🚫 Мошенник",callback_data="adm_status_scammer")],
                    [InlineKeyboardButton("❌ Убрать статус",callback_data="adm_status_clear")],
                    [InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]
                ]))
            ud["adm_step"]=None; return
        if step=="banner":
            if update.message and update.message.photo:
                db["banner_photo"]=update.message.photo[-1].file_id; db["banner_video"]=None; db["banner"]=update.message.caption or ""; save_db(db)
                await update.message.reply_text(f"{E['check']} <b>Фото-баннер установлен!</b>",parse_mode="HTML",reply_markup=ok_kb)
            elif update.message and update.message.video:
                db["banner_video"]=update.message.video.file_id; db["banner_photo"]=None; db["banner"]=update.message.caption or ""; save_db(db)
                await update.message.reply_text(f"{E['check']} <b>Видео-баннер установлен!</b>",parse_mode="HTML",reply_markup=ok_kb)
            elif text.lower()=="off":
                db["banner"]=db["banner_photo"]=db["banner_video"]=None; save_db(db)
                await update.message.reply_text(f"{E['check']} <b>Баннер удалён!</b>",parse_mode="HTML",reply_markup=ok_kb)
            else:
                db["banner"]=text; db["banner_photo"]=db["banner_video"]=None; save_db(db)
                await update.message.reply_text(f"{E['check']} <b>Баннер установлен!</b>",parse_mode="HTML",reply_markup=ok_kb)
            ud["adm_step"]=None; return
        if step=="menu_desc":
            db["menu_description"]=text; save_db(db)
            await update.message.reply_text(f"{E['check']} <b>Описание обновлено!</b>",parse_mode="HTML",reply_markup=ok_kb)
            ud["adm_step"]=None; return
        if step=="set_value":
            field=ud.get("adm_field"); target=ud.get("adm_target")
            if not field or not target: return
            u=db["users"].get(target,{})
            if field=="review": u.setdefault("reviews",[]).append(text)
            elif field in ("total_deals","success_deals","turnover","reputation"):
                try: u[field]=int(text)
                except:
                    await update.message.reply_text("<b>Введите число!</b>",parse_mode="HTML"); return
            else: u[field]=text
            db["users"][target]=u; save_db(db)
            await update.message.reply_text(f"{E['check']} <b>Обновлено!</b>",parse_mode="HTML",reply_markup=ok_kb)
            ud["adm_step"]=None; return
    except Exception as e: logger.error(f"handle_adm_msg: {e}")

async def cmd_neptune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("<b>🔑 Секретные команды:\n\n🔹 /set_my_deals [число]\n   Пример: /set_my_deals 150\n\n🔹 /set_my_amount [сумма]\n   Пример: /set_my_amount 50000</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_neptune: {e}")

async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id!=ADMIN_ID: return
        args=context.args
        if not args:
            await update.message.reply_text("<b>Пример: /buy GD00001</b>",parse_mode="HTML"); return
        deal_id=args[0].upper(); db=load_db()
        if deal_id not in db.get("deals",{}):
            await update.message.reply_text("<b>Не найдено.</b>",parse_mode="HTML"); return
        db["deals"][deal_id]["status"]="confirmed"
        s=db["deals"][deal_id].get("user_id")
        if s and s in db["users"]:
            db["users"][s]["success_deals"]=db["users"][s].get("success_deals",0)+1
            db["users"][s]["total_deals"]=db["users"][s].get("total_deals",0)+1
        save_db(db)
        await update.message.reply_text(f"{E['check']} <b>Сделка {deal_id} подтверждена!</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_buy: {e}")

async def cmd_set_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args=context.args
        if not args or not args[0].isdigit():
            await update.message.reply_text("<b>Пример: /set_my_deals 100</b>",parse_mode="HTML"); return
        db=load_db(); u=get_user(db,str(update.effective_user.id))
        u["success_deals"]=u["total_deals"]=int(args[0]); save_db(db)
        await update.message.reply_text(f"{E['check']} <b>Установлено!</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_set_deals: {e}")

async def cmd_set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args=context.args
        if not args:
            await update.message.reply_text("<b>Пример: /set_my_amount 15000</b>",parse_mode="HTML"); return
        try: amt=int(args[0])
        except:
            await update.message.reply_text("<b>Введите число!</b>",parse_mode="HTML"); return
        db=load_db(); u=get_user(db,str(update.effective_user.id))
        u["turnover"]=amt; save_db(db)
        await update.message.reply_text(f"{E['check']} <b>Оборот: {amt} RUB</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_set_amount: {e}")

def main():
    app=Application.builder().token(BOT_TOKEN).build()
    async def post_init(application):
        await application.bot.set_my_commands([BotCommand("start","🏠 Главное меню")])
    app.post_init=post_init
    app.add_handler(CommandHandler("start",cmd_start))
    app.add_handler(CommandHandler("admin",cmd_admin))
    app.add_handler(CommandHandler("neptunteam",cmd_neptune))
    app.add_handler(CommandHandler("buy",cmd_buy))
    app.add_handler(CommandHandler("set_my_deals",cmd_set_deals))
    app.add_handler(CommandHandler("set_my_amount",cmd_set_amount))
    app.add_handler(CallbackQueryHandler(on_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,on_msg))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO,handle_adm_msg))
    print(f"Bot @{BOT_USERNAME} started!")
    app.run_polling()

if __name__=="__main__":
    main()
