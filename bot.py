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
    # Новые
    "tonkeeper":  ce("5397829221605191505", "💎"),  # адрес тонкипера
    "top_medal":  ce("5188344996356448758", "🏆"),  # топ продавцов
    "stars_deal": ce("5321485469249198987", "⭐️"), # звёзды в сделке/пополнении
    "joined":     ce("5902335789798265487", "🤝"),  # второй участник присоединился
    "security_e": ce("5197288647275071607", "🛡"),  # безопасность в сделке
    "deal_link":  ce("5972261808747057065", "🔗"),  # ссылка при создании сделки
    "warning":    ce("5447644880824181073", "⚠️"),  # предупреждение про менеджера
    "stats":      ce("5028746137645876535", "📊"),  # статистика в меню
    "requisites": ce("5242631901214171852", "💳"),  # реквизиты
    "cryptobot":  ce("5242606681166220600", "🤖"),  # крипто бот
    "welcome":    ce("5251340119205501791", "👋"),  # приветствие в меню
    "balance_e":  ce("5424976816530014958", "💰"),  # баланс в профиле/реквизиты
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
    "nft":              f"{E['nft']} NFT подарок",
    "username":         f"{E['user']} NFT Username",
    "stars":            f"{E['stars_deal']} Звёзды Telegram",
    "crypto":           f"{E['tonkeeper']} Крипта (TON/USDT)",
    "premium":          f"{E['premium']} Telegram Premium",
    "premium_stickers": f"{E['sticker']} Премиум стикеры",
}

TNAMES_EN = {
    "nft":              f"{E['nft']} NFT Gift",
    "username":         f"{E['user']} NFT Username",
    "stars":            f"{E['stars_deal']} Telegram Stars",
    "crypto":           f"{E['tonkeeper']} Crypto (TON/USDT)",
    "premium":          f"{E['premium']} Telegram Premium",
    "premium_stickers": f"{E['sticker']} Premium Stickers",
}

def tname(dtype, lang):
    if lang=="en": return TNAMES_EN.get(dtype, dtype)
    return TNAMES.get(dtype, dtype)

T = {
    "deal_title":      {"ru": "Сделка", "en": "Deal"},
    "seller":          {"ru": "Продавец", "en": "Seller"},
    "buyer":           {"ru": "Покупатель", "en": "Buyer"},
    "deal_type":       {"ru": "Тип сделки", "en": "Deal type"},
    "amount":          {"ru": "Сумма", "en": "Amount"},
    "security":        {"ru": "Гарантия безопасности", "en": "Security guarantee"},
    "security_text":   {"ru": "Средства заморожены до подтверждения передачи. Сделка защищена платформой Gift Deals.", "en": "Funds are frozen until the transfer is confirmed. The deal is protected by Gift Deals."},
    "sbp":             {"ru": "СБП / Карта", "en": "SBP / Card"},
    "phone":           {"ru": "Телефон", "en": "Phone"},
    "recipient":       {"ru": "Получатель", "en": "Recipient"},
    "bank":            {"ru": "Банк", "en": "Bank"},
    "ton_title":       {"ru": "TON / USDT", "en": "TON / USDT"},
    "ton_addr":        {"ru": "TON адрес", "en": "TON address"},
    "crypto_bot":      {"ru": "Крипто бот", "en": "Crypto bot"},
    "after_pay":       {"ru": "После перевода нажмите кнопку «Я оплатил»", "en": "After payment press «I paid»"},
    "deal_created":    {"ru": "Сделка создана", "en": "Deal created"},
    "you":             {"ru": "Вы", "en": "You"},
    "link_for_buyer":  {"ru": "Ссылка для покупателя", "en": "Link for buyer"},
    "send_link":       {"ru": "Отправьте ссылку партнёру.", "en": "Send the link to your partner."},
    "i_paid":          {"ru": "✅ Я оплатил", "en": "✅ I paid"},
    "write_seller":    {"ru": "💬 Написать продавцу", "en": "💬 Write to seller"},
    "main_menu":       {"ru": "🏠 Главное меню", "en": "🏠 Main menu"},
    "profile_title":   {"ru": "Профиль", "en": "Profile"},
    "balance":         {"ru": "Баланс", "en": "Balance"},
    "deals_count":     {"ru": "Сделок", "en": "Deals"},
    "success":         {"ru": "Успешных", "en": "Successful"},
    "turnover":        {"ru": "Оборот", "en": "Turnover"},
    "reputation":      {"ru": "Репутация", "en": "Reputation"},
    "reviews_title":   {"ru": "Отзывы", "en": "Reviews"},
    "topup":           {"ru": "➕ Пополнить", "en": "➕ Top Up"},
    "withdraw_btn":    {"ru": "➖ Вывод", "en": "➖ Withdraw"},
    "back":            {"ru": "🔙 Назад", "en": "🔙 Back"},
    "status_label":    {"ru": "Статус", "en": "Status"},
    "top_title":       {"ru": "Топ продавцов Gift Deals", "en": "Gift Deals Top Sellers"},
    "my_deals_title":  {"ru": "Мои сделки", "en": "My Deals"},
    "no_deals":        {"ru": "У вас пока нет сделок.", "en": "You have no deals yet."},
    "topup_title":     {"ru": "Пополнить / Вывод", "en": "Top Up / Withdraw"},
    "topup_method":    {"ru": "Выберите способ пополнения:", "en": "Choose top-up method:"},
    "stars_topup":     {"ru": "Звёзды", "en": "Stars"},
    "rub_topup":       {"ru": "Рубли", "en": "Rubles"},
    "crypto_topup":    {"ru": "TON / USDT", "en": "TON / USDT"},
    "within_5min":     {"ru": "После перевода баланс пополнится в течение 5 минут.", "en": "Balance will be topped up within 5 minutes after transfer."},
}

def t(key, lang):
    return T.get(key, {}).get(lang, T.get(key, {}).get("ru", key))

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "deals": {}, "banner": None, "banner_photo": None,
            "banner_video": None, "banner_gif": None, "menu_description": None, "deal_counter": 1,
            "banners": {}, "logs": []}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def add_log(db, event, deal_id=None, uid=None, username=None, extra=""):
    if "logs" not in db: db["logs"]=[]
    entry = {
        "time": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "event": event,
        "deal_id": deal_id or "",
        "uid": str(uid) if uid else "",
        "username": username or "",
        "extra": extra,
    }
    db["logs"].append(entry)
    # Храним последние 500 событий
    if len(db["logs"]) > 500:
        db["logs"] = db["logs"][-500:]

def mask(text):
    """Скрываем середину строки: @username -> @us***me"""
    if not text: return "—"
    if text.startswith("@"):
        t = text[1:]
        if len(t) <= 3: return "@***"
        return f"@{t[:2]}***{t[-2:]}"
    if text.isdigit():
        return text[:3] + "***" + text[-2:]
    return text[:2] + "***"

def get_user(db, uid):
    k = str(uid)
    if k not in db["users"]:
        db["users"][k] = {"username": "", "balance": 0, "total_deals": 0,
            "success_deals": 0, "turnover": 0, "reputation": 0,
            "reviews": [], "status": "", "lang": "ru",
            "requisites": {}, "ref_by": None, "ref_count": 0, "ref_earned": 0,
            "hidden": False}
    u = db["users"][k]
    # Добавляем новые поля если их нет (для старых пользователей)
    if "requisites" not in u: u["requisites"] = {}
    if "ref_by" not in u: u["ref_by"] = None
    if "ref_count" not in u: u["ref_count"] = 0
    if "ref_earned" not in u: u["ref_earned"] = 0
    if "hidden" not in u: u["hidden"] = False
    return u

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
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

def get_welcome(lang):
    if lang == "en":
        intro = "Gift Deals — the safest platform for deals in Telegram"
        pts = ["Automatic NFT & gift deals","Full protection for both parties","Funds frozen until confirmation","Transfer via manager: @GiftDealsManager"]
        footer = "Choose an action below"
        stats = "1000+ deals · $6,350 turnover"
    else:
        intro = "Gift Deals — самая безопасная площадка для сделок в Telegram"
        pts = ["Автоматические сделки с НФТ и подарками","Полная защита обеих сторон","Средства заморожены до подтверждения","Передача через менеджера: @GiftDealsManager"]
        footer = "Выберите действие ниже"
        stats = "1000+ сделок · оборот $6,350"
    nums = [E['num1'], E['num2'], E['num3'], E['num4']]
    lines = "\n".join(f"<blockquote><b>{nums[i]} {pts[i]}.</b></blockquote>" for i in range(4))
    return (
        f"{E['welcome']} <b>{intro}</b>\n\n"
        f"{lines}\n\n"
        f"<blockquote><b>{E['stats']} {stats}</b></blockquote>\n\n"
        f"{E['spark']} <b>{footer}</b>"
    )

BTN = {
    "ru": {"deal": "💎 Создать сделку", "balance": "💸 Пополнить/Вывод", "lang": "🌍 Язык / Lang", "profile": "⭐ Профиль", "top": "🏆 Топ продавцов"},
    "en": {"deal": "💎 Create Deal", "balance": "💸 Top Up/Withdraw", "lang": "🌍 Language", "profile": "⭐ Profile", "top": "🏆 Top Sellers"},
}

CUR = {
    "TON": "💎 TON", "USDT": "💵 USDT",
    "Stars": {"ru": "⭐️ Звёзды", "en": "⭐️ Stars", "kz": "⭐️ Жұлдыз", "az": "⭐️ Ulduz", "uz": "⭐️ Yulduz", "kg": "⭐️ Жылдыз", "tj": "⭐️ Ситора", "by": "⭐️ Зоркі", "am": "⭐️ Astegh", "ge": "⭐️ ვარსკვ.", "ua": "⭐️ Зірки", "md": "⭐️ Stele"},
    "RUB": {"ru": "🇷🇺 Рубли", "en": "🇷🇺 Rubles", "kz": "🇷🇺 Рубль", "az": "🇷🇺 Rubl", "uz": "🇷🇺 Rubl", "kg": "🇷🇺 Рубль", "tj": "🇷🇺 Рубл", "by": "🇷🇺 Рублі", "am": "🇷🇺 Rubl", "ge": "🇷🇺 რუბლი", "ua": "🇷🇺 Рублі", "md": "🇷🇺 Ruble"},
    "KZT": {"ru": "🇰🇿 Тенге", "en": "🇰🇿 Tenge", "kz": "🇰🇿 Теңге", "az": "🇰🇿 Tenge", "uz": "🇰🇿 Tenge", "kg": "🇰🇿 Теңге", "tj": "🇰🇿 Тенге", "by": "🇰🇿 Тэнге", "am": "🇰🇿 Tenge", "ge": "🇰🇿 თენგე", "ua": "🇰🇿 Тенге", "md": "🇰🇿 Tenge"},
    "AZN": {"ru": "🇦🇿 Манат", "en": "🇦🇿 Manat", "kz": "🇦🇿 Манат", "az": "🇦🇿 Manat", "uz": "🇦🇿 Manat", "kg": "🇦🇿 Манат", "tj": "🇦🇿 Манот", "by": "🇦🇿 Манат", "am": "🇦🇿 Manat", "ge": "🇦🇿 მანათი", "ua": "🇦🇿 Манат", "md": "🇦🇿 Manat"},
    "KGS": {"ru": "🇰🇬 Сомы", "en": "🇰🇬 Som", "kz": "🇰🇬 Сом", "az": "🇰🇬 Som", "uz": "🇰🇬 Som", "kg": "🇰🇬 Сом", "tj": "🇰🇬 Сом", "by": "🇰🇬 Сомы", "am": "🇰🇬 Som", "ge": "🇰🇬 სომი", "ua": "🇰🇬 Соми", "md": "🇰🇬 Som"},
    "UZS": {"ru": "🇺🇿 Сумы", "en": "🇺🇿 Sum", "kz": "🇺🇿 Сум", "az": "🇺🇿 Sum", "uz": "🇺🇿 So'm", "kg": "🇺🇿 Сум", "tj": "🇺🇿 Сум", "by": "🇺🇿 Сумы", "am": "🇺🇿 Sum", "ge": "🇺🇿 სუმი", "ua": "🇺🇿 Суми", "md": "🇺🇿 Sum"},
    "TJS": {"ru": "🇹🇯 Сомони", "en": "🇹🇯 Somoni", "kz": "🇹🇯 Сомонӣ", "az": "🇹🇯 Somoni", "uz": "🇹🇯 Somoni", "kg": "🇹🇯 Сомонӣ", "tj": "🇹🇯 Сомонӣ", "by": "🇹🇯 Самані", "am": "🇹🇯 Somoni", "ge": "🇹🇯 სომონი", "ua": "🇹🇯 Сомоні", "md": "🇹🇯 Somoni"},
    "BYN": {"ru": "🇧🇾 Рубли BY", "en": "🇧🇾 BYN", "kz": "🇧🇾 Руб. BY", "az": "🇧🇾 Rubl BY", "uz": "🇧🇾 Rubl BY", "kg": "🇧🇾 Руб. BY", "tj": "🇧🇾 Руб. BY", "by": "🇧🇾 Рублі", "am": "🇧🇾 Rubl BY", "ge": "🇧🇾 რუბ. BY", "ua": "🇧🇾 Рублі BY", "md": "🇧🇾 Ruble BY"},
    "UAH": {"ru": "🇺🇦 Гривны", "en": "🇺🇦 Hryvnia", "kz": "🇺🇦 Гривна", "az": "🇺🇦 Qrivna", "uz": "🇺🇦 Grivna", "kg": "🇺🇦 Гривна", "tj": "🇺🇦 Гривна", "by": "🇺🇦 Грыўні", "am": "🇺🇦 Grivna", "ge": "🇺🇦 გრივნა", "ua": "🇺🇦 Гривні", "md": "🇺🇦 Grivne"},
    "GEL": {"ru": "🇬🇪 Лари", "en": "🇬🇪 Lari", "kz": "🇬🇪 Лари", "az": "🇬🇪 Lari", "uz": "🇬🇪 Lari", "kg": "🇬🇪 Лари", "tj": "🇬🇪 Лари", "by": "🇬🇪 Лары", "am": "🇬🇪 Lari", "ge": "🇬🇪 ლარი", "ua": "🇬🇪 Ларі", "md": "🇬🇪 Lari"},
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

BANNER_SECTIONS = {
    "main":     "🏠 Главное меню",
    "deal":     "🎁 Создать сделку",
    "balance":  "💸 Пополнить/Вывод",
    "profile":  "👤 Профиль",
    "top":      "🏆 Топ продавцов",
    "my_deals": "🗂 Мои сделки",
    "deal_card":"💼 Карточка сделки",
}

def get_banner(db, section="main"):
    """Каждый раздел полностью независим. Нет баннера — нет медиа."""
    banners = db.get("banners", {})
    b = banners.get(section)
    if b and (b.get("photo") or b.get("video") or b.get("gif") or b.get("text")):
        return b
    # Только main использует legacy поля для обратной совместимости
    if section == "main":
        legacy = {
            "photo": db.get("banner_photo"),
            "video": db.get("banner_video"),
            "gif":   db.get("banner_gif"),
            "text":  db.get("banner") or "",
        }
        if legacy["photo"] or legacy["video"] or legacy["gif"] or legacy["text"]:
            return legacy
    return None  # Нет баннера для этого раздела
async def send_with_banner(update, text, kb=None, section="main"):
    """Отправляет сообщение с баннером раздела. Каждый раздел полностью независим."""
    try:
        db=load_db()
        b=get_banner(db, section)
        bv=b.get("video") if b else None
        bg=b.get("gif")   if b else None
        bp=b.get("photo") if b else None
        banner_text=(b.get("text","") if b else "")
        full_text = text + (f"\n\n<b>{banner_text}</b>" if banner_text else "")
        has_media = bool(bv or bg or bp)

        old_msg = None
        old_has_media = False
        try:
            if update.callback_query:
                old_msg = update.callback_query.message
                if old_msg:
                    old_has_media = bool(old_msg.photo or old_msg.video or old_msg.animation)
        except: pass

        if not has_media and not old_has_media and old_msg:
            # Оба текстовые — просто редактируем
            try:
                await old_msg.edit_text(full_text, parse_mode="HTML", reply_markup=kb)
                return
            except: pass
        elif has_media and old_has_media and old_msg:
            # Оба медиа — пробуем edit_caption, иначе удаляем и шлём новое
            try:
                await old_msg.edit_caption(caption=full_text, parse_mode="HTML", reply_markup=kb)
                return
            except:
                try: await old_msg.delete()
                except: pass
        elif old_msg:
            # Смена типа — удаляем старое
            try: await old_msg.delete()
            except: pass

        # Отправляем новое
        if bv:
            await update.effective_chat.send_video(video=bv, caption=full_text, parse_mode="HTML", reply_markup=kb)
        elif bg:
            await update.effective_chat.send_animation(animation=bg, caption=full_text, parse_mode="HTML", reply_markup=kb)
        elif bp:
            await update.effective_chat.send_photo(photo=bp, caption=full_text, parse_mode="HTML", reply_markup=kb)
        else:
            await update.effective_chat.send_message(full_text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        logger.error(f"send_with_banner: {e}")
        try: await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)
        except: pass

async def send_text(update, text, kb=None):
    try: await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e: logger.error(f"send_text: {e}")

async def edit_or_send(update, text, kb=None, section="main"):
    await send_with_banner(update, text, kb, section=section)

def main_kb(lang):
    b = BTN.get(lang, BTN["ru"])
    ru=lang=="ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(b["deal"],callback_data="menu_deal"),InlineKeyboardButton(b["profile"],callback_data="menu_profile")],
        [InlineKeyboardButton(b["balance"],callback_data="menu_balance"),InlineKeyboardButton("🪪 "+("Мои сделки" if ru else "My Deals"),callback_data="menu_my_deals")],
        [InlineKeyboardButton(b["lang"],callback_data="menu_lang"),InlineKeyboardButton(b["top"],callback_data="menu_top")],
        [InlineKeyboardButton("👥 "+("Рефералы" if ru else "Referrals"),callback_data="menu_ref"),InlineKeyboardButton("📋 "+("Реквизиты" if ru else "Requisites"),callback_data="menu_req")],
        [InlineKeyboardButton("🆘 Техподдержка",url="https://t.me/GiftDealsSupport")],
    ])

async def show_main(update, context, edit=False):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=u.get("lang","ru"); desc=db.get("menu_description") or get_welcome(lang)
        kb=main_kb(lang)
        await send_with_banner(update, desc, kb, section="main")
    except Exception as e: logger.error(f"show_main: {e}")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        u["username"]=update.effective_user.username or ""
        args=context.args

        # Реферальная система
        if args and args[0].startswith("ref_") and not u.get("ref_by"):
            ref_uid=args[0][4:]
            if ref_uid != str(uid) and ref_uid in db.get("users",{}):
                u["ref_by"]=ref_uid
                db["users"][ref_uid]["ref_count"]=db["users"][ref_uid].get("ref_count",0)+1
                add_log(db,"👥 Новый реферал",uid=uid,username=u["username"],
                    extra=f"Пришёл по ссылке от {db['users'][ref_uid].get('username','?')}")

        save_db(db); context.user_data.clear()

        if args and args[0].startswith("deal_"):
            deal_id=args[0][5:].upper(); d=db.get("deals",{}).get(deal_id)
            if d:
                buyer_tag=f"@{update.effective_user.username}" if update.effective_user.username else f"#{uid}"
                seller_uid=d.get("user_id")

                # Проверяем реквизиты покупателя
                buyer_reqs = u.get("requisites",{})
                lang=u.get("lang","ru")
                ru=lang=="ru"
                if not buyer_reqs.get("card") and not buyer_reqs.get("ton") and not buyer_reqs.get("stars"):
                    warn_e = ce("5420323339723881652", "⚠️")
                    msg = (f"{warn_e} <b>{'Вы не можете продолжить сделку, пока не добавите реквизиты.' if ru else 'You cannot proceed until you add your requisites.'}</b>\n\n"
                           f"<blockquote><b>{'Реквизиты нужны на случай спора или возврата. Выберите что хотите добавить:' if ru else 'Requisites are needed in case of dispute. Choose what to add:'}</b></blockquote>")
                    kb=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💳 "+("Карта / СБП" if ru else "Card / SBP"),callback_data=f"req_deal_card_{deal_id}")],
                        [InlineKeyboardButton("💎 TON / USDT",callback_data=f"req_deal_ton_{deal_id}")],
                        [InlineKeyboardButton("⭐️ "+("Звёзды" if ru else "Stars"),callback_data=f"req_deal_stars_{deal_id}")],
                    ])
                    await update.effective_message.reply_text(msg, parse_mode="HTML", reply_markup=kb)
                    context.user_data["pending_deal"]=deal_id
                    return

                # Логируем вход в сделку
                add_log(db,"🔗 Покупатель открыл сделку",deal_id=deal_id,uid=uid,
                    username=u["username"],extra=f"Продавец: {d.get('partner','?')}")
                save_db(db)

                # Уведомляем продавца
                if seller_uid and seller_uid!=str(uid):
                    seller_lang=get_lang(int(seller_uid))
                    try:
                        notify=(f"{E['joined']} <b>{'Покупатель присоединился к сделке!' if seller_lang=='ru' else 'Buyer joined the deal!'}</b>\n\n"
                               f"<blockquote><b>{'Сделка' if seller_lang=='ru' else 'Deal'}: #{deal_id}\n"
                               f"{'Покупатель' if seller_lang=='ru' else 'Buyer'}: {buyer_tag}</b></blockquote>")
                        await context.bot.send_message(chat_id=int(seller_uid),text=notify,parse_mode="HTML")
                    except Exception as e: logger.error(f"joined notify: {e}")
                await send_deal_card(update,context,deal_id,d,buyer=True); return
        await show_main(update,context)
    except Exception as e: logger.error(f"cmd_start: {e}")

def deal_types_kb(lang="ru"):
    ru=lang=="ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 NFT",callback_data="dt_nft"),InlineKeyboardButton("🎴 NFT Username",callback_data="dt_usr")],
        [InlineKeyboardButton("⭐️ "+("Звёзды" if ru else "Stars"),callback_data="dt_str"),InlineKeyboardButton("💎 "+("Крипта" if ru else "Crypto"),callback_data="dt_cry")],
        [InlineKeyboardButton("✈️ Telegram Premium",callback_data="dt_prm")],
        [InlineKeyboardButton("🔙 "+("Назад" if ru else "Back"),callback_data="main_menu")],
    ])

async def on_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q=update.callback_query; await q.answer(); d=q.data
        ud=context.user_data; uid=update.effective_user.id; lang=get_lang(uid)
        if d=="menu_ref": await show_ref(update,context); return
        if d=="menu_req": await show_req(update,context); return
        if d.startswith("req_del_"):
            field=d[8:]; db=load_db(); u=get_user(db,uid)
            if "requisites" not in u: u["requisites"]={}
            u["requisites"].pop(field,None); save_db(db)
            await show_req(update,context); return
        if d.startswith("req_edit_"):
            field=d[9:]; ru=lang=="ru"
            examples={"card":"79041751408 или 2200 1234 5678 9012","ton":"UQD...xyz (48 символов)","stars":"@username"}
            labels={"card":"💳 "+("Карта / Телефон (СБП)" if ru else "Card / Phone (SBP)"),
                    "ton":"💎 TON "+("адрес" if ru else "address"),
                    "stars":ce("5438496463044752972", "⭐️")+" "+("Юзернейм для звёзд" if ru else "Stars username")}
            descs={"card":("Введите номер телефона (СБП) или номер карты.\n\nПримеры:\n<code>+79041751408</code>\n<code>2200 1234 5678 9012</code>" if ru else "Enter phone number (SBP) or card number.\n\nExamples:\n<code>+79041751408</code>\n<code>2200 1234 5678 9012</code>"),
                   "ton":("Введите TON адрес (начинается с UQ или EQ, 48 символов).\n\nПример:\n<code>UQDxxx...xxx</code>" if ru else "Enter TON address (starts with UQ or EQ, 48 chars).\n\nExample:\n<code>UQDxxx...xxx</code>"),
                   "stars":("Введите @юзернейм Telegram для получения звёзд.\n\nПример:\n<code>@username</code>" if ru else "Enter Telegram @username for receiving stars.\n\nExample:\n<code>@username</code>")}
            context.user_data["req_step"]=field
            text=f"{labels.get(field,'?')}\n\n<blockquote><b>{descs.get(field,'?')}</b></blockquote>"
            await edit_or_send(update,text,InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+("Назад" if ru else "Back"),callback_data="menu_req")]]), section="profile"); return
        if d.startswith("add_req_"):
            deal_id=d[8:]; context.user_data["req_for_deal"]=deal_id; ru=lang=="ru"
            warn=ce("5420323339723881652", "⚠️")
            text=(f"{warn} <b>{'Добавьте реквизиты для участия в сделке' if ru else 'Add requisites to join the deal'}</b>\n\n"
                  f"<blockquote><b>{'Выберите способ получения средств в случае спора или возврата.' if ru else 'Choose a refund method in case of dispute.'}</b></blockquote>")
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 "+("Карта / СБП" if ru else "Card / SBP"),callback_data=f"req_deal_card_{deal_id}")],
                [InlineKeyboardButton("💎 TON "+("адрес" if ru else "address"),callback_data=f"req_deal_ton_{deal_id}")],
                [InlineKeyboardButton("⭐️ "+("Юзернейм для звёзд" if ru else "Stars username"),callback_data=f"req_deal_stars_{deal_id}")],
                [InlineKeyboardButton("🔙 "+("Назад" if ru else "Back"),callback_data="main_menu")],
            ])
            await edit_or_send(update,text,kb, section="deal_card"); return
        if d.startswith("req_deal_"):
            parts=d[9:].split("_",1); field=parts[0]; deal_id=parts[1] if len(parts)>1 else ""
            context.user_data["req_step"]=field; context.user_data["req_for_deal"]=deal_id; ru=lang=="ru"
            prompts={
                "card":(f"💳 <b>{'Карта / СБП' if ru else 'Card / SBP'}</b>\n\n<blockquote><b>{'Введите номер телефона (СБП) или карты.' if ru else 'Enter phone (SBP) or card number.'}\n\n{'Примеры' if ru else 'Examples'}:\n<code>+79041751408</code>\n<code>2200 1234 5678 9012</code></b></blockquote>"),
                "ton": (f"💎 <b>TON {'адрес' if ru else 'address'}</b>\n\n<blockquote><b>{'Введите TON адрес (начинается с UQ или EQ).' if ru else 'Enter TON address (starts with UQ or EQ).'}\n\n{'Пример' if ru else 'Example'}:\n<code>UQDxxx...xxx</code></b></blockquote>"),
                "stars":(f"{ce('5438496463044752972','⭐️')} <b>{'Звёзды' if ru else 'Stars'}</b>\n\n<blockquote><b>{'Введите ваш @юзернейм.' if ru else 'Enter your @username.'}\n\n{'Пример' if ru else 'Example'}:\n<code>@username</code></b></blockquote>"),
            }
            await edit_or_send(update,prompts.get(field,"?"),InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+("Назад" if ru else "Back"),callback_data=f"add_req_{deal_id}")]]), section="deal_card"); return
        if d=="main_menu":
            ud.clear()
            try: await q.message.delete()
            except: pass
            await show_main(update,context,edit=False); return
        if d=="menu_deal":
            ud.clear()
            ru=lang=="ru"
            try: await q.message.delete()
            except: pass
            await update.effective_message.reply_text(f"{E['pencil']} <b>{'Создать сделку' if ru else 'Create Deal'}\n\n{'Выберите тип' if ru else 'Choose type'}:</b>",parse_mode="HTML",reply_markup=deal_types_kb(lang)); return
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
                ]),section="balance"); return
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
        if d.startswith("lang_"): await set_lang(update,context,d[5:]); return
        if d.startswith("balance_"): await show_balance_info(update,context,d[8:]); return
        if d=="withdraw": await show_withdraw(update,context); return
        if d.startswith("withdraw_"):
            method=d[9:]
            prompts={"stars":"Укажите @юзернейм получателя звёзд:","crypto":"Укажите TON/USDT адрес для вывода:","card":"Укажите номер карты для вывода:"}
            context.user_data["withdraw_method"]=method; context.user_data["withdraw_step"]="requisite"
            await edit_or_send(update,f"{E['wallet']} <b>Вывод средств</b>\n\n<blockquote><b>{prompts.get(method,'Укажите реквизиты:')}</b></blockquote>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="withdraw")]]), section="balance"); return
        if d.startswith("rev_"):
            parts=d.split("_"); deal_id=parts[1]; role=parts[2]; stars=int(parts[3])
            context.user_data["review_deal"]=deal_id; context.user_data["review_role"]=role; context.user_data["review_stars"]=stars
            context.user_data["review_step"]="text"
            ru=lang=="ru"
            star_e = ce("5438496463044752972", "⭐️")
            await q.edit_message_text(f"{star_e*stars} {'Оценка' if ru else 'Rating'}: {stars}/5\n\n{'Напишите комментарий к отзыву' if ru else 'Write a review comment'}:",parse_mode="HTML"); return
        if d.startswith("paid_"): await on_paid(update,context); return
        if d=="noop": return
        if d.startswith("adm_confirm_"): await adm_confirm(update,context); return
        if d.startswith("adm_decline_"): await adm_decline(update,context); return
        if d=="adm_back":
            try: await q.message.edit_text(f"{E['shield']} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())
            except: await q.message.reply_text(f"{E['shield']} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())
            return
        if d.startswith("adm_"): await handle_adm_cb(update,context); return
        type_map={"dt_nft":"nft","dt_usr":"username","dt_str":"stars","dt_cry":"crypto","dt_prm":"premium","dt_pst":"premium_stickers"}
        if d in type_map:
            ud.clear(); ud["type"]=type_map[d]; ud["step"]="partner"
            ru=lang=="ru"
            icons={"nft":E["nft"],"username":E["user"],"stars":E["star"],"crypto":E["diamond"],"premium":E["premium"],"premium_stickers":E["sticker"]}
            icon=icons.get(type_map[d],E["deal"])
            try: await q.message.delete()
            except: pass
            msg=await update.effective_chat.send_message(f"{icon} <b>{'Введите @юзернейм партнёра' if ru else 'Enter partner @username'}:</b>",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+("Назад" if ru else "Back"),callback_data="menu_deal")]]))
            ud["last_bot_msg"]=msg.message_id; return
        if d=="cry_ton":
            ru=lang=="ru"; ud["currency"]="TON"; ud["step"]="amount"
            msg=await update.effective_chat.send_message(f"{E['diamond']} <b>{'Крипта' if ru else 'Crypto'} (TON)\n\n{'Введите сумму' if ru else 'Enter amount'}:</b>",parse_mode="HTML")
            ud["last_bot_msg"]=msg.message_id; return
        if d=="cry_usd":
            ru=lang=="ru"; ud["currency"]="USDT"; ud["step"]="amount"
            msg=await update.effective_chat.send_message(f"{E['diamond']} <b>{'Крипта' if ru else 'Crypto'} (USDT)\n\n{'Введите сумму' if ru else 'Enter amount'}:</b>",parse_mode="HTML")
            ud["last_bot_msg"]=msg.message_id; return
        if d in ("prm_3","prm_6","prm_12"):
            ru=lang=="ru"
            periods_ru={"prm_3":"3 месяца","prm_6":"6 месяцев","prm_12":"12 месяцев"}
            periods_en={"prm_3":"3 months","prm_6":"6 months","prm_12":"12 months"}
            ud["premium_period"]=(periods_ru if ru else periods_en)[d]; ud["step"]="currency"
            await send_text(update,f"{E['premium']} <b>Telegram Premium\n\n{'Выберите валюту' if ru else 'Choose currency'}:</b>",cur_kb(lang)); return
        if d in ("pst_1","pst_3","pst_5","pst_10"):
            ru=lang=="ru"
            counts_ru={"pst_1":"1 пак","pst_3":"3 пака","pst_5":"5 паков","pst_10":"10 паков"}
            counts_en={"pst_1":"1 pack","pst_3":"3 packs","pst_5":"5 packs","pst_10":"10 packs"}
            ud["sticker_count"]=(counts_ru if ru else counts_en)[d]; ud["step"]="currency"
            await send_text(update,f"{E['sticker']} <b>{'Премиум стикеры' if ru else 'Premium Stickers'}\n\n{'Выберите валюту' if ru else 'Choose currency'}:</b>",cur_kb(lang)); return
        if d.startswith("cur_"):
            ru=lang=="ru"; ud["currency"]=CURMAP.get(d,d); ud["step"]="amount"
            icons={"nft":E["nft"],"username":E["user"],"stars":E["star"],"premium":E["premium"],"premium_stickers":E["sticker"]}
            icon=icons.get(ud.get("type",""),E["deal"])
            await send_text(update,f"{icon} <b>{'Введите сумму сделки' if ru else 'Enter deal amount'}:</b>"); return
    except Exception as e: logger.error(f"on_cb: {e}")

async def on_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ud=context.user_data; uid=update.effective_user.id; lang=get_lang(uid)
        text=update.message.text.strip() if update.message.text else ""
        if uid==ADMIN_ID and ud.get("adm_step"): await handle_adm_msg(update,context); return

        # Обработка сохранения реквизитов
        if ud.get("req_step") in ("card","ton","stars"):
            field=ud.get("req_step"); db=load_db(); u=get_user(db,uid)
            ru_r=lang=="ru"
            if not u.get("requisites"): u["requisites"]={}

            # Валидация
            err=None
            if field=="card":
                clean=text.replace(" ","").replace("+","")
                if not (clean.isdigit() and 10<=len(clean)<=19):
                    err=("Введите корректный номер телефона или карты.\n\nПримеры:\n<code>+79041751408</code>\n<code>2200123456789012</code>" if ru_r else
                         "Enter a valid phone or card number.\n\nExamples:\n<code>+79041751408</code>\n<code>2200123456789012</code>")
            elif field=="ton":
                if not ((text.startswith("UQ") or text.startswith("EQ")) and len(text)>=40):
                    err=("Введите корректный TON адрес (начинается с UQ или EQ).\n\nПример:\n<code>UQDxxx...xxx</code>" if ru_r else
                         "Enter a valid TON address (starts with UQ or EQ).\n\nExample:\n<code>UQDxxx...xxx</code>")
            elif field=="stars":
                t_clean=text if text.startswith("@") else f"@{text}"
                if len(t_clean)<3:
                    err=("Введите @юзернейм.\n\nПример:\n<code>@username</code>" if ru_r else
                         "Enter @username.\n\nExample:\n<code>@username</code>")
                else: text=t_clean

            if err:
                await update.message.reply_text(f"❌ {err}",parse_mode="HTML"); return

            u["requisites"][field]=text; save_db(db); ud.pop("req_step",None)
            pending_deal=ud.pop("req_for_deal",None) or ud.pop("pending_deal",None)
            if pending_deal:
                db2=load_db(); d2=db2.get("deals",{}).get(pending_deal)
                if d2:
                    await update.message.reply_text(f"{ce('5206607081334906820','✅')} <b>{'Реквизиты сохранены! Открываем сделку...' if ru_r else 'Requisites saved! Opening deal...'}</b>",parse_mode="HTML")
                    add_log(db2,"🔗 Покупатель открыл сделку",deal_id=pending_deal,uid=uid,username=u.get("username",""))
                    save_db(db2)
                    await send_deal_card(update,context,pending_deal,d2,buyer=True); return
            await update.message.reply_text(f"{ce('5206607081334906820','✅')} <b>{'Реквизиты сохранены!' if ru_r else 'Requisites saved!'}</b>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 "+("Мои реквизиты" if ru_r else "My Requisites"),callback_data="menu_req")]])); return
        # Обработка реквизитов вывода
        if ud.get("withdraw_step")=="requisite":
            method=ud.get("withdraw_method","?"); db=load_db()
            ru_w=lang=="ru"
            uid3=update.effective_user.id; u3=get_user(db,uid3); bal=u3.get("balance",0)
            uname3=update.effective_user.username or str(uid3)
            methods={"stars":"Звёзды" if ru_w else "Stars","crypto":"Крипта" if ru_w else "Crypto","card":"Карта" if ru_w else "Card"}
            mname=methods.get(method,method)
            try: await context.bot.send_message(chat_id=ADMIN_ID,
                text=f"{E['gem']} <b>Запрос на вывод — {mname}</b>\n{E['user']} @{uname3} (<code>{uid3}</code>)\n{CM} {bal} RUB\n\nРеквизиты: <code>{text}</code>",parse_mode="HTML")
            except Exception as e: logger.error(f"withdraw req admin: {e}")
            ud.pop("withdraw_step",None); ud.pop("withdraw_method",None)
            await update.message.reply_text(
                f"{E['check']} <b>{'Запрос отправлен!' if ru_w else 'Request sent!'}</b>\n\n"
                f"<blockquote><b>{'Способ' if ru_w else 'Method'}: {mname}\n{'Сумма' if ru_w else 'Amount'}: {bal} RUB\n\n"
                f"{'Менеджер свяжется с вами в ближайшее время.' if ru_w else 'Manager will contact you shortly.'}</b></blockquote>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💬 "+("Менеджер" if ru_w else "Manager"),url=f"https://t.me/{MANAGER_USERNAME.lstrip('@')}")],
                    [InlineKeyboardButton("🏠 "+("Главное меню" if ru_w else "Main menu"),callback_data="main_menu")]
                ])); return
            deal_id=ud.get("review_deal"); role=ud.get("review_role"); stars=ud.get("review_stars",5)
            db=load_db(); deal=db.get("deals",{}).get(deal_id,{})
            star_e2 = ce("5438496463044752972", "⭐️")
            review_text=f"{star_e2*stars} {stars}/5 — {text}"
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
            ru_rev=lang=="ru"
            await update.message.reply_text(f"{E['check']} <b>{'Отзыв сохранён!' if ru_rev else 'Review saved!'}</b>",parse_mode="HTML"); return
        dtype=ud.get("type"); step=ud.get("step")
        if not dtype or not step: return

        # Удаляем сообщение пользователя и предыдущий бот-ответ
        async def delete_prev():
            try: await update.message.delete()
            except: pass
            if ud.get("last_bot_msg"):
                try: await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=ud["last_bot_msg"])
                except: pass

        async def send_step(text, kb=None):
            await delete_prev()
            msg = await update.effective_chat.send_message(text, parse_mode="HTML", reply_markup=kb)
            ud["last_bot_msg"] = msg.message_id

        if step=="partner":
            ru=lang=="ru"
            if not text.startswith("@"):
                await update.message.reply_text(f"{E['cross']} <b>{'Юзернейм должен начинаться с @' if ru else 'Username must start with @'}</b>",parse_mode="HTML"); return
            ud["partner"]=text
            if dtype=="nft":
                ud["step"]="nft_link"
                await send_step(f"{E['nft']} <b>{'НФТ' if ru else 'NFT'}\n\n{'Вставьте ссылку на НФТ (https://...)' if ru else 'Paste the NFT link (https://...)'}:</b>")
            elif dtype=="username":
                ud["step"]="trade_usr"
                await send_step(f"{E['user']} <b>{'Юзернейм' if ru else 'Username'}\n\n{'Введите @юзернейм товара' if ru else 'Enter the @username of the item'}:</b>")
            elif dtype=="stars":
                ud["step"]="stars_cnt"
                await send_step(f"{E['star']} <b>{'Звёзды' if ru else 'Stars'}\n\n{'Сколько звёзд?' if ru else 'How many stars?'}</b>")
            elif dtype=="crypto":
                ud["step"]="cry_currency"
                await send_step(f"{E['diamond']} <b>{'Крипта' if ru else 'Crypto'}\n\n{'Выберите валюту' if ru else 'Choose currency'}:</b>",
                    InlineKeyboardMarkup([[InlineKeyboardButton("💎 TON",callback_data="cry_ton"),InlineKeyboardButton("💵 USDT",callback_data="cry_usd")]]))
            elif dtype=="premium":
                ud["step"]="prem_period"
                await send_step(f"{E['premium']} <b>Telegram Premium\n\n{'Выберите срок' if ru else 'Choose period'}:</b>",
                    InlineKeyboardMarkup([[InlineKeyboardButton("3 "+("месяца" if ru else "months"),callback_data="prm_3"),InlineKeyboardButton("6 "+("месяцев" if ru else "months"),callback_data="prm_6"),InlineKeyboardButton("12 "+("месяцев" if ru else "months"),callback_data="prm_12")]]))
            elif dtype=="premium_stickers":
                ud["step"]="sticker_pack"
                await send_step(f"{E['sticker']} <b>{'Премиум стикеры' if ru else 'Premium Stickers'}\n\n{'Выберите количество стикерпаков' if ru else 'Choose number of sticker packs'}:</b>",
                    InlineKeyboardMarkup([[InlineKeyboardButton("1 "+("пак" if ru else "pack"),callback_data="pst_1"),InlineKeyboardButton("3 "+("пака" if ru else "packs"),callback_data="pst_3")],[InlineKeyboardButton("5 "+("паков" if ru else "packs"),callback_data="pst_5"),InlineKeyboardButton("10 "+("паков" if ru else "packs"),callback_data="pst_10")]]))
            return
        if step=="nft_link":
            ru=lang=="ru"
            if not text.startswith("https://"):
                await update.message.reply_text(f"{E['cross']} <b>{'Ссылка должна начинаться с https://' if ru else 'Link must start with https://'}</b>",parse_mode="HTML"); return
            ud["nft_link"]=text; ud["step"]="currency"
            await send_step(f"{E['nft']} <b>{'НФТ' if ru else 'NFT'}\n\n{'Выберите валюту' if ru else 'Choose currency'}:</b>", cur_kb(lang)); return
        if step=="trade_usr":
            ru=lang=="ru"
            if not text.startswith("@"):
                await update.message.reply_text(f"{E['cross']} <b>{'Юзернейм должен начинаться с @' if ru else 'Username must start with @'}</b>",parse_mode="HTML"); return
            ud["trade_username"]=text; ud["step"]="currency"
            await send_step(f"{E['user']} <b>{'Юзернейм' if ru else 'Username'}\n\n{'Выберите валюту' if ru else 'Choose currency'}:</b>", cur_kb(lang)); return
        if step=="stars_cnt":
            ru=lang=="ru"
            if not text.isdigit():
                await update.message.reply_text(f"{E['cross']} <b>{'Только цифры!' if ru else 'Numbers only!'}</b>",parse_mode="HTML"); return
            ud["stars_count"]=text; ud["step"]="currency"
            await send_step(f"{E['star']} <b>{'Звёзды' if ru else 'Stars'}\n\n{'Выберите валюту' if ru else 'Choose currency'}:</b>", cur_kb(lang)); return
        if step=="amount":
            await delete_prev()
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
                    buyer_lang=get_lang(int(puid))
                    txt=build_buyer_card(deal_id,db["deals"][deal_id],f"@{user.username or str(user.id)}",buyer_lang)
                    kb=InlineKeyboardMarkup([[InlineKeyboardButton(t("i_paid",buyer_lang),callback_data=f"paid_{deal_id}")],[InlineKeyboardButton(t("main_menu",buyer_lang),callback_data="main_menu")]])
                    await context.bot.send_message(chat_id=int(puid),text=txt,parse_mode="HTML",reply_markup=kb)
                except Exception as e: logger.error(f"notify partner: {e}")
        context.user_data.clear()
    except Exception as e: logger.error(f"finalize_deal: {e}")

def build_item_line(dtype, dd, lang="ru"):
    ru=lang=="ru"
    if dtype=="nft": return f"\n{E['link']} {'Ссылка' if ru else 'Link'}: {dd.get('nft_link','—')}"
    elif dtype=="username": return f"\n{E['user']} {'Юзернейм' if ru else 'Username'}: {dd.get('trade_username','—')}"
    elif dtype=="stars": return f"\n{E['star']} {'Звёзд' if ru else 'Stars'}: {dd.get('stars_count','—')}"
    elif dtype=="premium": return f"\n{E['clock']} {'Срок' if ru else 'Period'}: {dd.get('premium_period','—')}"
    elif dtype=="premium_stickers": return f"\n{E['sticker']} {'Паков' if ru else 'Packs'}: {dd.get('sticker_count','—')}"
    return ""

def build_buyer_card(deal_id, d, seller_tag, lang="ru"):
    dtype=d.get("type",""); cur=d.get("currency","—"); amt=d.get("amount","—")
    item=build_item_line(dtype,d.get("data",{}),lang)
    item_str=f"\n{item.strip()}" if item.strip() else ""
    ru = lang=="ru"
    return (
        f"<tg-emoji emoji-id='5445221832074483553'>💼</tg-emoji> <b>{'Сделка' if ru else 'Deal'} #{deal_id}</b>\n\n"
        f"<blockquote>"
        f"{'Продавец' if ru else 'Seller'}: <b>{seller_tag}</b>\n"
        f"{'Покупатель' if ru else 'Buyer'}: <b>{'Вы' if ru else 'You'}</b>\n"
        f"{'Тип' if ru else 'Type'}: <b>{tname(dtype,lang)}</b>"
        f"{item_str}\n"
        f"{'Сумма' if ru else 'Amount'}: <b>{amt} {cur_native(cur)}</b>"
        f"</blockquote>\n\n"
        f"{E['security_e']} <b>{'Гарантия безопасности' if ru else 'Security guarantee'}</b>\n"
        f"<blockquote><b>{t('security_text',lang)}</b></blockquote>\n\n"
        f"{E['warning']} <b>{'Важно' if ru else 'Important'}:</b>\n"
        f"<blockquote><b>{'Не передавайте товар напрямую! Только через менеджера @GiftDealsManager.' if ru else 'Do not transfer goods directly! Only through @GiftDealsManager.'}</b></blockquote>\n\n"
        f"{E['requisites']} <b>{'СБП / Карта' if ru else 'SBP / Card'} {CARD_BANK}:</b>\n"
        f"<blockquote><b>{'Телефон' if ru else 'Phone'}: <code>{CARD_NUMBER}</code>\n{'Получатель' if ru else 'Recipient'}: {CARD_NAME}\n{'Банк' if ru else 'Bank'}: {CARD_BANK}</b></blockquote>\n\n"
        f"{E['tonkeeper']} <b>TON / USDT:</b>\n"
        f"<blockquote><b>{'TON адрес' if ru else 'TON address'}:\n<code>{CRYPTO_ADDRESS}</code>\n\n{E['cryptobot']} {'Крипто бот' if ru else 'Crypto bot'}: {CRYPTO_BOT}</b></blockquote>\n\n"
        f"{E['stars_deal']} <b>{'Звёзды / NFT' if ru else 'Stars / NFT'}:</b>\n"
        f"<blockquote><b>{'Отправьте звёзды менеджеру' if ru else 'Send stars to manager'}: @GiftDealsManager</b></blockquote>\n\n"
        f"<tg-emoji emoji-id='5206607081334906820'>✅</tg-emoji> {'После перевода нажмите «Я оплатил»' if ru else 'After payment press «I paid»'}"
    )

async def send_deal_card(update, context, deal_id, d, buyer=False):
    try:
        dtype=d.get("type",""); cur=d.get("currency","—"); amt=d.get("amount","—")
        partner=d.get("partner","—"); item=build_item_line(dtype,d.get("data",{}))
        db=load_db(); seller_uid=d.get("user_id")
        lang=get_lang(update.effective_user.id)
        item_str=f"\n{item.strip()}" if item.strip() else ""
        if buyer:
            pu=f"https://t.me/{partner.lstrip('@')}" if partner.startswith("@") else f"https://t.me/{MANAGER_USERNAME.lstrip('@')}"
            status_str=f"\n<tg-emoji emoji-id='5438496463044752972'>⭐️</tg-emoji> {'Статус' if lang=='ru' else 'Status'}: <b>{db['users'][seller_uid].get('status','')}</b>" if seller_uid and seller_uid in db.get('users',{}) and db['users'][seller_uid].get('status') else ""
            ru = lang=="ru"
            text=(
                f"<tg-emoji emoji-id='5445221832074483553'>💼</tg-emoji> <b>{'Сделка' if ru else 'Deal'} #{deal_id}</b>\n\n"
                f"<blockquote>"
                f"{'Продавец' if ru else 'Seller'}: <b>{partner}</b>{status_str}\n"
                f"{'Покупатель' if ru else 'Buyer'}: <b>{'Вы' if ru else 'You'}</b>\n"
                f"{'Тип' if ru else 'Type'}: <b>{tname(dtype,lang)}</b>"
                f"{item_str}\n"
                f"{'Сумма' if ru else 'Amount'}: <b>{amt} {cur_native(cur)}</b>"
                f"</blockquote>\n\n"
                f"{E['security_e']} <b>{'Гарантия безопасности' if ru else 'Security guarantee'}</b>\n"
                f"<blockquote><b>{t('security_text',lang)}</b></blockquote>\n\n"
                f"{E['warning']} <b>{'Важно' if ru else 'Important'}:</b>\n"
                f"<blockquote><b>{'Не передавайте товар напрямую! Только через менеджера @GiftDealsManager.' if ru else 'Do not transfer goods directly! Only through @GiftDealsManager.'}</b></blockquote>\n\n"
                f"{E['requisites']} <b>{'СБП / Карта' if ru else 'SBP / Card'} {CARD_BANK}:</b>\n"
                f"<blockquote><b>{'Телефон' if ru else 'Phone'}: <code>{CARD_NUMBER}</code>\n{'Получатель' if ru else 'Recipient'}: {CARD_NAME}\n{'Банк' if ru else 'Bank'}: {CARD_BANK}</b></blockquote>\n\n"
                f"{E['tonkeeper']} <b>TON / USDT:</b>\n"
                f"<blockquote><b>{'TON адрес' if ru else 'TON address'}:\n<code>{CRYPTO_ADDRESS}</code>\n\n{E['cryptobot']} {'Крипто бот' if ru else 'Crypto bot'}: {CRYPTO_BOT}</b></blockquote>\n\n"
                f"{E['stars_deal']} <b>{'Звёзды / NFT' if ru else 'Stars / NFT'}:</b>\n"
                f"<blockquote><b>{'Отправьте звёзды менеджеру' if ru else 'Send stars to manager'}: @GiftDealsManager</b></blockquote>\n\n"
                f"<tg-emoji emoji-id='5206607081334906820'>✅</tg-emoji> {'После перевода нажмите «Я оплатил»' if ru else 'After payment press «I paid»'}"
            )
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ " + ("Я оплатил" if ru else "I paid"),callback_data=f"paid_{deal_id}")],
                [InlineKeyboardButton("💬 " + ("Написать продавцу" if ru else "Write to seller"),url=pu)],
                [InlineKeyboardButton("🏠 " + ("Главное меню" if ru else "Main menu"),callback_data="main_menu")]
            ])
        else:
            ru = lang=="ru"
            text=(
                f"<tg-emoji emoji-id='5206607081334906820'>✅</tg-emoji> <b>{'Сделка создана' if ru else 'Deal created'} #{deal_id}</b>\n\n"
                f"<blockquote>"
                f"{'Продавец' if ru else 'Seller'}: <b>{'Вы' if ru else 'You'}</b>\n"
                f"{'Покупатель' if ru else 'Buyer'}: <b>{partner}</b>\n"
                f"{'Тип' if ru else 'Type'}: <b>{tname(dtype,lang)}</b>"
                f"{item_str}\n"
                f"{'Сумма' if ru else 'Amount'}: <b>{amt} {cur_native(cur)}</b>"
                f"</blockquote>\n\n"
                f"{E['deal_link']} {'Ссылка для покупателя' if ru else 'Link for buyer'}:\n"
                f"<code>https://t.me/{BOT_USERNAME}?start=deal_{deal_id}</code>\n\n"
                f"{'Отправьте ссылку партнёру.' if ru else 'Send the link to your partner.'}"
            )
            kb=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 " + ("Главное меню" if ru else "Main menu"),callback_data="main_menu")]])
        await send_with_banner(update, text, kb, section="deal_card")
    except Exception as e: logger.error(f"send_deal_card: {e}")

async def on_paid(update, context):
    try:
        q=update.callback_query; await q.answer("Уведомление отправлено!")
        deal_id=q.data[5:]; buyer=update.effective_user
        btag=f"@{buyer.username}" if buyer.username else str(buyer.id)
        db=load_db(); d=db.get("deals",{}).get(deal_id,{})
        amt=d.get("amount","—"); cur=d.get("currency","—"); dtype=d.get("type","")
        buyer_lang=get_lang(buyer.id); ru_b=buyer_lang=="ru"
        seller_uid=d.get("user_id"); seller_lang=get_lang(int(seller_uid)) if seller_uid else "ru"; ru_s=seller_lang=="ru"
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
                    text=f"{E['bell']} <b>{'Покупатель сообщил об оплате!' if ru_s else 'Buyer reported payment!'}</b>\n<code>{deal_id}</code>\n{E['user']} {btag}\n{CM} {amt} {cur}",parse_mode="HTML")
            except Exception as e: logger.error(f"on_paid seller: {e}")
        try:
            await q.edit_message_reply_markup(InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ "+("Ожидание подтверждения..." if ru_b else "Waiting for confirmation..."),callback_data="noop")],
                [InlineKeyboardButton("🏠 "+("Главное меню" if ru_b else "Main menu"),callback_data="main_menu")]
            ]))
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
            s=d.get("user_id"); amt_str=d.get("amount","0")
            try: amt_num=float(amt_str)
            except: amt_num=0
            if s and s in db["users"]:
                db["users"][s]["success_deals"]=db["users"][s].get("success_deals",0)+1
                db["users"][s]["total_deals"]=db["users"][s].get("total_deals",0)+1
                db["users"][s]["turnover"]=db["users"][s].get("turnover",0)+int(amt_num)
            # Лог подтверждения
            seller_uname=db["users"].get(s,{}).get("username","?") if s else "?"
            add_log(db,"✅ Сделка подтверждена",deal_id=deal_id,uid=s,
                username=seller_uname,extra=f"Сумма: {amt_str} {d.get('currency','')}")
            # 3% рефераллу продавца
            if s and s in db["users"]:
                ref_uid=db["users"][s].get("ref_by")
                if ref_uid and ref_uid in db["users"] and amt_num>0:
                    bonus=int(amt_num*0.03)
                    if bonus>0:
                        db["users"][ref_uid]["ref_earned"]=db["users"][ref_uid].get("ref_earned",0)+bonus
                        db["users"][ref_uid]["balance"]=db["users"][ref_uid].get("balance",0)+bonus
                        add_log(db,"💰 Реферальный бонус",uid=ref_uid,
                            username=db["users"][ref_uid].get("username","?"),
                            extra=f"+{bonus} RUB (3% от сделки {deal_id})")
                        try:
                            await context.bot.send_message(chat_id=int(ref_uid),
                                text=f"💰 <b>Реферальный бонус!</b>\n\n<blockquote><b>+{bonus} RUB (3% от сделки #{deal_id})</b></blockquote>",
                                parse_mode="HTML")
                        except: pass
            save_db(db)
            try: await q.edit_message_text(f"{E['check']} <b>Оплата подтверждена!</b>\n<code>{deal_id}</code>\n{CM} {d.get('amount')} {d.get('currency')}",parse_mode="HTML")
            except Exception as e: logger.error(f"adm_confirm edit: {e}")
            if s:
                try:
                    sl=get_lang(int(s)); ru_s=sl=="ru"
                    buyer_tag=d.get("partner","—")
                    await context.bot.send_message(chat_id=int(s),
                        text=f"{E['check']} <b>{'Оплата подтверждена! Сделка завершена.' if ru_s else 'Payment confirmed! Deal completed.'}</b>\n<code>{deal_id}</code>\n\n"
                             f"{'Оцените покупателя' if ru_s else 'Rate the buyer'} {buyer_tag}:",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("⭐️1",callback_data=f"rev_{deal_id}_s_1"),InlineKeyboardButton("⭐️2",callback_data=f"rev_{deal_id}_s_2"),InlineKeyboardButton("⭐️3",callback_data=f"rev_{deal_id}_s_3"),InlineKeyboardButton("⭐️4",callback_data=f"rev_{deal_id}_s_4"),InlineKeyboardButton("⭐️5",callback_data=f"rev_{deal_id}_s_5")],
                        ]))
                except Exception as e: logger.error(f"adm_confirm notify seller: {e}")
            buyer_uid=None
            for uid_,u_ in db.get("users",{}).items():
                if u_.get("username","").lower()==d.get("partner","").lstrip("@").lower():
                    buyer_uid=uid_; break
            if buyer_uid:
                try:
                    bl=get_lang(int(buyer_uid)); ru_b=bl=="ru"
                    seller_tag=f"@{db['users'].get(s,{}).get('username',('продавец' if ru_b else 'seller'))}" if s else ("продавца" if ru_b else "seller")
                    await context.bot.send_message(chat_id=int(buyer_uid),
                        text=f"{E['check']} <b>{'Сделка подтверждена!' if ru_b else 'Deal confirmed!'}</b>\n<code>{deal_id}</code>\n\n"
                             f"{'Оцените продавца' if ru_b else 'Rate the seller'} {seller_tag}:",
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
        lang=get_lang(uid); bal=u.get("balance",0)
        ru=lang=="ru"
        await edit_or_send(update,
            f"💸 <b>{'Пополнить / Вывод' if ru else 'Top Up / Withdraw'}</b>\n\n<blockquote><b>{'Баланс' if ru else 'Balance'}: {bal} RUB</b></blockquote>",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ "+("Пополнить" if ru else "Top Up"),callback_data="balance_topup")],
                [InlineKeyboardButton("➖ "+("Вывод" if ru else "Withdraw"),callback_data="withdraw")],
                [InlineKeyboardButton("🔙 "+("Назад" if ru else "Back"),callback_data="main_menu")],
            ]), section="balance")
    except Exception as e: logger.error(f"show_balance: {e}")

async def show_balance_info(update, context, method):
    try:
        uid=update.effective_user.id; lang=get_lang(uid)
        if method=="stars":
            text=(f"{E['stars_deal']} <b>{'Пополнение звёздами' if lang=='ru' else 'Top up with Stars'}</b>\n\n"
                  f"<blockquote><b>{'Отправьте звёзды менеджеру' if lang=='ru' else 'Send stars to manager'}: @GiftDealsManager\n\n{t('within_5min',lang)}</b></blockquote>")
        elif method=="rub":
            text=(f"{E['requisites']} <b>{'Пополнение рублями' if lang=='ru' else 'Top up in Rubles'}</b>\n\n"
                  f"<blockquote><b>"
                  f"{'Банк' if lang=='ru' else 'Bank'}: {CARD_BANK}\n"
                  f"{'Телефон' if lang=='ru' else 'Phone'}: <code>{CARD_NUMBER}</code>\n"
                  f"{'Получатель' if lang=='ru' else 'Recipient'}: {CARD_NAME}\n\n"
                  f"{t('within_5min',lang)}"
                  f"</b></blockquote>")
        elif method=="crypto":
            text=(f"{E['tonkeeper']} <b>{'Пополнение TON / USDT' if lang=='ru' else 'Top up TON / USDT'}</b>\n\n"
                  f"<blockquote><b>"
                  f"{'TON адрес' if lang=='ru' else 'TON address'}:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
                  f"{E['cryptobot']} {'Крипто бот' if lang=='ru' else 'Crypto bot'}: {CRYPTO_BOT}\n\n"
                  f"ID: <code>{uid}</code>"
                  f"</b></blockquote>")
        else: text="<b>?</b>"
        await edit_or_send(update,text,InlineKeyboardMarkup([[InlineKeyboardButton(t("back",lang),callback_data="balance_topup")]]), section="balance")
    except Exception as e: logger.error(f"show_balance_info: {e}")

async def show_lang(update, context):
    try:
        uid=update.effective_user.id; lang=get_lang(uid)
        prompt = "Select language:" if lang=="en" else "Выберите язык:"
        rows=[]
        for code,name in LANGS.items():
            rows.append([InlineKeyboardButton(name,callback_data=f"lang_{code}")])
        rows.append([InlineKeyboardButton("🔙 Назад" if lang=="ru" else "🔙 Back",callback_data="main_menu")])
        await edit_or_send(update,f"<tg-emoji emoji-id='5447410659077661506'>🌐</tg-emoji> <b>{prompt}</b>",InlineKeyboardMarkup(rows), section="main")
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
        lang=get_lang(uid); uname=update.effective_user.username or "—"
        status=u.get("status","")
        sl=f"\n<blockquote><b>{t('status_label',lang)}: {status}</b></blockquote>" if status else ""
        rv=("\n\n<b>"+t("reviews_title",lang)+":</b>\n"+"\n".join(f"• {r}" for r in u.get("reviews",[])[-5:])) if u.get("reviews") else ""
        ru=lang=="ru"
        sl=f"\n<blockquote><b>{'Статус' if ru else 'Status'}: {status}</b></blockquote>" if status else ""
        rv=("\n\n<b>"+("Отзывы" if ru else "Reviews")+":</b>\n"+"\n".join(f"• {r}" for r in u.get("reviews",[])[-5:])) if u.get("reviews") else ""
        text=(f"<tg-emoji emoji-id='5275979556308674886'>👤</tg-emoji> <b>{'Профиль' if ru else 'Profile'}{sl}\n\n@{uname}\n"
              f"{E['balance_e']} {'Баланс' if ru else 'Balance'}: {u.get('balance',0)} RUB\n"
              f"<tg-emoji emoji-id='5028746137645876535'>📊</tg-emoji> {'Сделок' if ru else 'Deals'}: {u.get('total_deals',0)}\n"
              f"<tg-emoji emoji-id='5206607081334906820'>✅</tg-emoji> {'Успешных' if ru else 'Successful'}: {u.get('success_deals',0)}\n"
              f"<tg-emoji emoji-id='5902056028513505203'>💵</tg-emoji> {'Оборот' if ru else 'Turnover'}: {u.get('turnover',0)} RUB\n"
              f"<tg-emoji emoji-id='5438496463044752972'>⭐️</tg-emoji> {'Репутация' if ru else 'Reputation'}: {u.get('reputation',0)}</b>{rv}")
        await edit_or_send(update,text,InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ "+("Пополнить" if ru else "Top Up"),callback_data="menu_balance"),
             InlineKeyboardButton("➖ "+("Вывод" if ru else "Withdraw"),callback_data="withdraw")],
            [InlineKeyboardButton("🔙 "+("Назад" if ru else "Back"),callback_data="main_menu")]
        ]), section="profile")
    except Exception as e: logger.error(f"show_profile: {e}")

async def show_ref(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=get_lang(uid); ru=lang=="ru"
        ref_link=f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"
        ref_count=u.get("ref_count",0); ref_earned=u.get("ref_earned",0)
        text=(
            f"{ce('6001526766714227911','👥')} <b>{'Реферальная программа' if ru else 'Referral Program'}</b>\n\n"
            f"<blockquote>"
            f"{'Приглашайте друзей и получайте 3% с каждой их сделки!' if ru else 'Invite friends and earn 3% from each their deal!'}\n\n"
            f"{'Приглашено' if ru else 'Invited'}: <b>{ref_count}</b>\n"
            f"{'Заработано' if ru else 'Earned'}: <b>{ref_earned} RUB</b>"
            f"</blockquote>\n\n"
            f"{'Ваша реферальная ссылка (нажмите чтобы скопировать):' if ru else 'Your referral link (tap to copy):'}\n"
            f"<code>{ref_link}</code>"
        )
        await edit_or_send(update,text,InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 "+("Назад" if ru else "Back"),callback_data="main_menu")]
        ]), section="profile")
    except Exception as e: logger.error(f"show_ref: {e}")

async def show_req(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=get_lang(uid); ru=lang=="ru"
        reqs=u.get("requisites",{})
        card=reqs.get("card"); ton=reqs.get("ton"); stars=reqs.get("stars")

        e_card  = ce("5445353829304387411", "💳")
        e_ton   = ce("5397829221605191505", "💎")
        e_star  = ce("5321485469249198987", "⭐️")
        e_check = ce("5206607081334906820", "✅")
        e_add   = ce("5274055917766202507", "➕")

        card_line = f"{e_check} <code>{card}</code>" if card else f"{e_add} <b>{'Добавить карту' if ru else 'Add card'}</b>"
        ton_line  = f"{e_check} <code>{ton}</code>"  if ton  else f"{e_add} <b>{'Добавить TON адрес' if ru else 'Add TON address'}</b>"
        star_line = f"{e_check} <code>{stars}</code>" if stars else f"{e_add} <b>{'Добавить юзернейм' if ru else 'Add username'}</b>"

        text=(
            f"📋 <b>{'Мои реквизиты' if ru else 'My Requisites'}</b>\n\n"
            f"{e_card} <b>{'Карта / СБП' if ru else 'Card / SBP'}:</b>\n"
            f"<blockquote><b>{card_line}</b></blockquote>\n\n"
            f"{e_ton} <b>TON / USDT:</b>\n"
            f"<blockquote><b>{ton_line}</b></blockquote>\n\n"
            f"{e_star} <b>{'Звёзды' if ru else 'Stars'}:</b>\n"
            f"<blockquote><b>{star_line}</b></blockquote>"
        )
        r1 = [InlineKeyboardButton("💳 "+("Изменить" if ru else "Edit"),callback_data="req_edit_card"),
              InlineKeyboardButton("🗑 "+("Удалить" if ru else "Delete"),callback_data="req_del_card")] if card \
         else [InlineKeyboardButton("💳 "+("Добавить карту" if ru else "Add Card"),callback_data="req_edit_card")]
        r2 = [InlineKeyboardButton("💎 "+("Изменить" if ru else "Edit"),callback_data="req_edit_ton"),
              InlineKeyboardButton("🗑 "+("Удалить" if ru else "Delete"),callback_data="req_del_ton")] if ton \
         else [InlineKeyboardButton("💎 "+("Добавить TON" if ru else "Add TON"),callback_data="req_edit_ton")]
        r3 = [InlineKeyboardButton("⭐️ "+("Изменить" if ru else "Edit"),callback_data="req_edit_stars"),
              InlineKeyboardButton("🗑 "+("Удалить" if ru else "Delete"),callback_data="req_del_stars")] if stars \
         else [InlineKeyboardButton("⭐️ "+("Добавить юзернейм" if ru else "Add Username"),callback_data="req_edit_stars")]
        await edit_or_send(update,text,InlineKeyboardMarkup([r1,r2,r3,[InlineKeyboardButton("🔙 "+("Назад" if ru else "Back"),callback_data="main_menu")]]), section="profile")
    except Exception as e: logger.error(f"show_req: {e}")

async def show_my_deals(update, context):
    try:
        db=load_db(); uid=str(update.effective_user.id); lang=get_lang(int(uid))
        deals={k:v for k,v in db.get("deals",{}).items() if v.get("user_id")==uid}
        if not deals:
            await edit_or_send(update,f"💼 <b>{t('my_deals_title',lang)}\n\n{t('no_deals',lang)}</b>",InlineKeyboardMarkup([[InlineKeyboardButton(t("back",lang),callback_data="main_menu")]]), section="my_deals"); return
        pending = "⏳ Ожидает" if lang=="ru" else "⏳ Pending"
        confirmed = "✅ Завершена" if lang=="ru" else "✅ Completed"
        SNAMES={"pending":pending,"confirmed":confirmed}
        lines=[f"<tg-emoji emoji-id='5445221832074483553'>💼</tg-emoji> <b>{t('my_deals_title',lang)} ({len(deals)}):</b>"]
        for did,dv in list(deals.items())[-10:]:
            tn=tname(dv.get("type",""),lang); s=SNAMES.get(dv.get("status",""),dv.get("status",""))
            lines.append(f"<b>{did}</b> | {tn} | {dv.get('amount')} {cur_native(dv.get('currency',''))} | {s}")
        await edit_or_send(update,"\n".join(lines),InlineKeyboardMarkup([[InlineKeyboardButton(t("back",lang),callback_data="main_menu")]]), section="my_deals")
    except Exception as e: logger.error(f"show_my_deals: {e}")

async def show_top(update, context):
    try:
        lang=get_lang(update.effective_user.id)
        TOP=[("@al***ndr",450,47),("@ie***ym",380,38),("@ma***ov",310,29),("@kr***na",290,31),("@pe***ko",270,25),("@se***ev",240,22),("@an***va",210,19),("@vi***or",190,17),("@dm***iy",170,15),("@ni***la",140,13)]
        medals=["🥇","🥈","🥉"]+["🏅"]*7
        title = t("top_title",lang)
        lines=[f"{E['top_medal']} <b>{title}</b>\n"]
        for i,(u,a,d) in enumerate(TOP): lines.append(f"<b>{medals[i]} {i+1}. {u} — ${a} | {d} {'сделок' if lang=='ru' else 'deals'}</b>")
        lines.append(f"\n{E['stats']} <b>{'1000+ сделок в боте' if lang=='ru' else '1000+ deals on platform'}</b>")
        await edit_or_send(update,"\n".join(lines),InlineKeyboardMarkup([[InlineKeyboardButton(t("back",lang),callback_data="main_menu")]]), section="top")
    except Exception as e: logger.error(f"show_top: {e}")

async def show_withdraw(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        bal=u.get("balance",0)
        if bal<=0:
            await edit_or_send(update,f"{E['cross']} <b>Недостаточно средств для вывода.</b>\n\n<blockquote><b>Ваш баланс: {bal} RUB</b></blockquote>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="menu_balance")]]), section="balance"); return
        await edit_or_send(update,
            f"{E['wallet']} <b>Вывод средств</b>\n\n<blockquote><b>Ваш баланс: {bal} RUB\n\nВыберите способ вывода:</b></blockquote>",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("⭐️ Звёзды",callback_data="withdraw_stars")],
                [InlineKeyboardButton("💎 Крипта (TON/USDT)",callback_data="withdraw_crypto")],
                [InlineKeyboardButton("💳 На карту",callback_data="withdraw_card")],
                [InlineKeyboardButton("🔙 Назад",callback_data="menu_balance")],
            ]), section="balance")
    except Exception as e: logger.error(f"show_withdraw: {e}")

def adm_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Управление пользователем",callback_data="adm_user")],
        [InlineKeyboardButton("🖼 Баннеры по разделам",callback_data="adm_banners")],
        [InlineKeyboardButton("✏️ Описание меню",callback_data="adm_menu_desc")],
        [InlineKeyboardButton("🗂 Список сделок",callback_data="adm_deals")],
        [InlineKeyboardButton("📋 Логи событий",callback_data="adm_logs"),InlineKeyboardButton("📋 Логи (скрыт.)",callback_data="adm_logs_hidden")],
    ])

def adm_banners_kb(db=None):
    if db is None: db=load_db()
    banners=db.get("banners",{})
    rows=[]
    for key,name in BANNER_SECTIONS.items():
        b=banners.get(key) or {}
        has=bool(b.get("photo") or b.get("video") or b.get("gif") or b.get("text"))
        # Legacy для main
        if not has and key=="main":
            has=bool(db.get("banner_photo") or db.get("banner_video") or db.get("banner_gif") or db.get("banner"))
        status="✅" if has else "➕"
        rows.append([
            InlineKeyboardButton(f"{status} {name}",callback_data=f"adm_banner_{key}"),
            InlineKeyboardButton("🗑",callback_data=f"adm_banner_del_{key}") if has else InlineKeyboardButton("   ",callback_data="noop"),
        ])
    rows.append([InlineKeyboardButton("🔙 Назад",callback_data="adm_back")])
    return InlineKeyboardMarkup(rows)

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
            await q.message.edit_text("<b>Введите @юзернейм пользователя:</b>",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return

        if d=="adm_banners":
            db=load_db()
            await q.message.edit_text(
                "<b>🖼 Баннеры по разделам</b>\n\n"
                "<blockquote>✅ — установлен  |  ➕ — не установлен  |  🗑 — удалить\n\nКаждый раздел независим.</blockquote>",
                parse_mode="HTML",reply_markup=adm_banners_kb(db)); return

        if d.startswith("adm_banner_del_"):
            section=d[15:]
            if section in BANNER_SECTIONS:
                db=load_db()
                if not db.get("banners"): db["banners"]={}
                db["banners"][section]={}
                if section=="main":
                    db["banner"]=db["banner_photo"]=db["banner_video"]=db["banner_gif"]=None
                save_db(db)
                await q.answer(f"Баннер удалён")
                db2=load_db()
                await q.message.edit_text(
                    "<b>🖼 Баннеры по разделам</b>\n\n"
                    "<blockquote>✅ — установлен  |  ➕ — не установлен  |  🗑 — удалить\n\nКаждый раздел независим.</blockquote>",
                    parse_mode="HTML",reply_markup=adm_banners_kb(db2)); return

        if d.startswith("adm_banner_"):
            section=d[11:]
            if section in BANNER_SECTIONS:
                ud["adm_step"]="banner"; ud["adm_banner_section"]=section
                name=BANNER_SECTIONS[section]
                await q.message.edit_text(f"<b>Баннер для раздела «{name}»\n\nОтправьте фото, видео, GIF или текст.\noff — удалить баннер.</b>",parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Отмена",callback_data="adm_banners")]])); return

        if d in ("adm_logs","adm_logs_hidden"):
            hidden=d=="adm_logs_hidden"; db=load_db()
            logs=db.get("logs",[])[-20:][::-1]
            if not logs:
                await q.message.edit_text("<b>Логов пока нет.</b>",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return
            lines=["<b>📋 Последние события:</b>\n"]
            for log in logs:
                uname=mask(f"@{log['username']}") if hidden and log.get('username') else (f"@{log['username']}" if log.get('username') else "")
                uid_str=mask(log['uid']) if hidden and log.get('uid') else (f"<code>{log['uid']}</code>" if log.get('uid') else "")
                deal=f" #{log['deal_id']}" if log.get('deal_id') else ""
                extra=f" — {log['extra']}" if log.get('extra') else ""
                lines.append(f"<b>{log['time']}</b> {log['event']}{deal}\n{uname} {uid_str}{extra}\n")
            txt="\n".join(lines)[:4000]
            await q.message.edit_text(txt,parse_mode="HTML",reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👁 Показать реальные" if hidden else "🙈 Скрыть данные",callback_data="adm_logs" if hidden else "adm_logs_hidden")],
                [InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]
            ])); return

        if d=="adm_menu_desc":
            ud["adm_step"]="menu_desc"
            await q.message.edit_text("<b>Введите новое описание меню:</b>",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Отмена",callback_data="adm_back")]])); return

        if d=="adm_deals":
            db=load_db(); deals=db.get("deals",{})
            if not deals:
                await q.message.edit_text("<b>Сделок нет.</b>",parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return
            text="<b>📋 Последние 10 сделок:</b>\n"
            for did,dv in list(deals.items())[-10:]:
                text+=f"\n<b>{did}</b> | {TNAMES.get(dv.get('type',''),dv.get('type',''))} | {dv.get('amount')} {dv.get('currency')} | {dv.get('status')}"
            await q.message.edit_text(text,parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return

        action_map={"adm_add_review":("review","Введите отзыв:"),"adm_set_deals":("total_deals","Введите кол-во сделок:"),"adm_set_success":("success_deals","Введите успешных сделок:"),"adm_set_turnover":("turnover","Введите оборот:"),"adm_set_rep":("reputation","Введите репутацию:"),"adm_set_status":("status","Введите статус:")}
        if d in action_map:
            field,prompt=action_map[d]; ud["adm_field"]=field; ud["adm_step"]="set_value"
            await q.message.edit_text(f"<b>{prompt}</b>",parse_mode="HTML"); return

        status_map={"adm_status_verified":"✅ Проверенный","adm_status_garant":"🛡 Гарант","adm_status_caution":"⚠️ Осторожно","adm_status_scammer":"🚫 Мошенник","adm_status_clear":""}
        if d in status_map:
            target=ud.get("adm_target")
            if target:
                db=load_db(); u=db["users"].get(target,{})
                u["status"]=status_map[d]; db["users"][target]=u; save_db(db)
                await q.answer(f"Статус: {status_map[d] or 'убран'}")
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
            section=ud.get("adm_banner_section","main")
            if not db.get("banners"): db["banners"]={}
            caption=update.message.caption or "" if update.message else ""
            if update.message and update.message.photo:
                db["banners"][section]={"photo":update.message.photo[-1].file_id,"video":None,"gif":None,"text":caption}
                save_db(db)
            elif update.message and update.message.animation:
                db["banners"][section]={"photo":None,"video":None,"gif":update.message.animation.file_id,"text":caption}
                save_db(db)
            elif update.message and update.message.video:
                db["banners"][section]={"photo":None,"video":update.message.video.file_id,"gif":None,"text":caption}
                save_db(db)
            elif text.lower()=="off":
                db["banners"][section]={}
                if section=="main":
                    db["banner"]=db["banner_photo"]=db["banner_video"]=db["banner_gif"]=None
                save_db(db)
            else:
                db["banners"][section]={"photo":None,"video":None,"gif":None,"text":text}
                save_db(db)
            ud["adm_step"]=None; ud.pop("adm_banner_section",None)
            db2=load_db()
            await update.message.reply_text(
                f"{E['check']} <b>Баннер раздела «{BANNER_SECTIONS.get(section,section)}» обновлён!</b>\n\n"
                "<b>🖼 Баннеры по разделам:</b>\n"
                "<blockquote>✅ — установлен  |  ➕ — нет  |  🗑 — удалить</blockquote>",
                parse_mode="HTML",reply_markup=adm_banners_kb(db2)); return
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
    # Миграция: переносим legacy banner_photo/video/gif в banners["main"] и чистим legacy
    db=load_db()
    migrated=False
    if not db.get("banners"): db["banners"]={}
    lp=db.get("banner_photo"); lv=db.get("banner_video"); lg=db.get("banner_gif"); lt=db.get("banner") or ""
    if (lp or lv or lg or lt) and not db["banners"].get("main"):
        db["banners"]["main"]={"photo":lp,"video":lv,"gif":lg,"text":lt}
        db["banner_photo"]=None; db["banner_video"]=None; db["banner_gif"]=None; db["banner"]=None
        save_db(db); migrated=True
        logger.info("Миграция баннера в banners['main'] выполнена")

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
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION,handle_adm_msg))
    print(f"Bot @{BOT_USERNAME} started!")
    app.run_polling()

if __name__=="__main__":
    main()
