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
    "tonkeeper":  ce("5397829221605191505", "💎"),
    "top_medal":  ce("5188344996356448758", "🏆"),
    "stars_deal": ce("5321485469249198987", "⭐️"),
    "joined":     ce("5902335789798265487", "🤝"),
    "security_e": ce("5197288647275071607", "🛡"),
    "deal_link":  ce("5972261808747057065", "🔗"),
    "warning":    ce("5447644880824181073", "⚠️"),
    "stats":      ce("5028746137645876535", "📊"),
    "requisites": ce("5242631901214171852", "💳"),
    "cryptobot":  ce("5242606681166220600", "🤖"),
    "welcome":    ce("5251340119205501791", "👋"),
    "balance_e":  ce("5424976816530014958", "💰"),
    "star_prem":  ce("5361541546057189236", "⭐"),
}

CM = ce("5278467510604160626", "💰")

TNAMES_RU = {
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
TNAMES = TNAMES_RU

def tname(dtype, lang="ru"):
    return TNAMES_EN.get(dtype, dtype) if lang == "en" else TNAMES_RU.get(dtype, dtype)

# Currency names always in native language
CUR_NATIVE_NAMES = {
    "TON":   "💎 TON",
    "USDT":  "💵 USDT",
    "Stars": "⭐️ Stars",
    "RUB":   "Рубли",
    "KZT":   "Теңге",
    "AZN":   "Manat",
    "KGS":   "Сом",
    "UZS":   "So'm",
    "TJS":   "Сомонӣ",
    "BYN":   "Рублі",
    "UAH":   "Гривня",
    "GEL":   "ლარი",
}

# Currency in button (with flag)
CUR_BTN_NAMES = {
    "TON":   "💎 TON",
    "USDT":  "💵 USDT",
    "Stars": "⭐️ Stars / Звёзды",
    "RUB":   "🇷🇺 Рубли",
    "KZT":   "🇰🇿 Теңге",
    "AZN":   "🇦🇿 Manat",
    "KGS":   "🇰🇬 Сом",
    "UZS":   "🇺🇿 So'm",
    "TJS":   "🇹🇯 Сомонӣ",
    "BYN":   "🇧🇾 Рублі",
    "UAH":   "🇺🇦 Гривня",
    "GEL":   "🇬🇪 ლარი",
}

def cur_native(code):
    return CUR_NATIVE_NAMES.get(code, code)

def format_amount(amount, currency, lang="ru"):
    """Format amount like: 83 Рубля / 0.5 TON / 100 Stars"""
    ru = lang == "ru"
    name = CUR_NATIVE_NAMES.get(currency, currency)
    return f"{amount} {name}"

def lbl(ru, ru_text, en_text):
    return ru_text if ru else en_text

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "deals": {}, "banner": None, "banner_photo": None,
            "banner_video": None, "banner_gif": None, "menu_description": None, "deal_counter": 1,
            "banners": {}, "logs": [], "log_chat_id": None}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def add_log(db, event, deal_id=None, uid=None, username=None, extra="", item_link=""):
    if "logs" not in db: db["logs"] = []
    entry = {
        "time": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "event": event, "deal_id": deal_id or "",
        "uid": str(uid) if uid else "", "username": username or "",
        "extra": extra, "item_link": item_link,
    }
    db["logs"].append(entry)
    if len(db["logs"]) > 500:
        db["logs"] = db["logs"][-500:]

async def send_log_to_channel(context, db, entry, hidden=False):
    chat_id = db.get("log_chat_id")
    if not chat_id: return
    try:
        uname = entry.get("username", ""); uid_str = entry.get("uid", "")
        deal = f" #{entry['deal_id']}" if entry.get("deal_id") else ""
        extra = f"\n{entry['extra']}" if entry.get("extra") else ""
        item_link = f"\n{entry['item_link']}" if entry.get("item_link") else ""
        if hidden:
            uname_display = mask(f"@{uname}") if uname else ""; uid_display = mask(uid_str) if uid_str else ""
        else:
            uname_display = f"@{uname}" if uname else ""; uid_display = f"<code>{uid_str}</code>" if uid_str else ""
        text = f"<b>{entry['time']}</b> {entry['event']}{deal}\n{uname_display} {uid_display}{extra}{item_link}"
        await context.bot.send_message(chat_id=int(chat_id), text=text, parse_mode="HTML")
    except Exception as e: logger.error(f"send_log_to_channel: {e}")

def mask(text):
    if not text: return "—"
    if text.startswith("@"):
        t2 = text[1:]
        if len(t2) <= 3: return "@***"
        return f"@{t2[:2]}***{t2[-2:]}"
    if text.isdigit(): return text[:3] + "***" + text[-2:]
    return text[:2] + "***"

def get_user(db, uid):
    k = str(uid)
    if k not in db["users"]:
        db["users"][k] = {"username": "", "balance": 0, "total_deals": 0,
            "success_deals": 0, "turnover": 0, "reputation": 0,
            "reviews": [], "status": "", "lang": "ru",
            "requisites": {}, "ref_by": None, "ref_count": 0, "ref_earned": 0, "hidden": False}
    u = db["users"][k]
    for f2, v in [("requisites",{}),("ref_by",None),("ref_count",0),("ref_earned",0),("hidden",False)]:
        if f2 not in u: u[f2] = v
    return u

def get_lang(uid):
    try: return get_user(load_db(), uid).get("lang", "ru")
    except: return "ru"

def gen_deal_id(db):
    n = db.get("deal_counter", 1); db["deal_counter"] = n + 1; save_db(db)
    return f"GD{n:05d}"

LANGS = {"ru": "🇷🇺 Русский", "en": "🇬🇧 English"}

def get_welcome(lang):
    if lang == "en":
        intro = "Gift Deals — the safest platform for deals in Telegram"
        pts = ["Automatic NFT & gift deals", "Full protection for both parties",
               "Funds frozen until confirmation", "Transfer via manager: @GiftDealsManager"]
        footer = "Choose an action below"; stats = "1000+ deals · $6,350 turnover"
    else:
        intro = "Gift Deals — самая безопасная площадка для сделок в Telegram"
        pts = ["Автоматические сделки с НФТ и подарками", "Полная защита обеих сторон",
               "Средства заморожены до подтверждения", "Передача через менеджера: @GiftDealsManager"]
        footer = "Выберите действие ниже"; stats = "1000+ сделок · оборот $6,350"
    nums = [E['num1'], E['num2'], E['num3'], E['num4']]
    lines = "\n".join(f"<blockquote><b>{nums[i]} {pts[i]}.</b></blockquote>" for i in range(4))
    return (f"{E['welcome']} <b>{intro}</b>\n\n{lines}\n\n"
            f"<blockquote><b>{E['stats']} {stats}</b></blockquote>\n\n{E['spark']} <b>{footer}</b>")

CURMAP = {"cur_ton":"TON","cur_usdt":"USDT","cur_rub":"RUB","cur_stars":"Stars",
          "cur_kzt":"KZT","cur_azn":"AZN","cur_kgs":"KGS","cur_uzs":"UZS",
          "cur_tjs":"TJS","cur_byn":"BYN","cur_uah":"UAH","cur_gel":"GEL"}

def cur_kb(lang):
    def n(c): return CUR_BTN_NAMES.get(c, c)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(n("TON"), callback_data="cur_ton"),
         InlineKeyboardButton(n("USDT"), callback_data="cur_usdt")],
        [InlineKeyboardButton(n("RUB"), callback_data="cur_rub"),
         InlineKeyboardButton(n("Stars"), callback_data="cur_stars")],
        [InlineKeyboardButton(n("KZT"), callback_data="cur_kzt"),
         InlineKeyboardButton(n("AZN"), callback_data="cur_azn")],
        [InlineKeyboardButton(n("KGS"), callback_data="cur_kgs"),
         InlineKeyboardButton(n("UZS"), callback_data="cur_uzs")],
        [InlineKeyboardButton(n("TJS"), callback_data="cur_tjs"),
         InlineKeyboardButton(n("BYN"), callback_data="cur_byn")],
        [InlineKeyboardButton(n("UAH"), callback_data="cur_uah"),
         InlineKeyboardButton(n("GEL"), callback_data="cur_gel")],
    ])

BANNER_SECTIONS = {
    "main":"🏠 Главное меню", "deal":"🎁 Создать сделку", "balance":"💸 Пополнить/Вывод",
    "profile":"👤 Профиль", "top":"🏆 Топ сделок", "my_deals":"🗂 Мои сделки", "deal_card":"💼 Карточка сделки",
}

def get_banner(db, section="main"):
    banners = db.get("banners", {})
    b = banners.get(section)
    if b and (b.get("photo") or b.get("video") or b.get("gif") or b.get("text")): return b
    if section == "main":
        legacy = {"photo": db.get("banner_photo"), "video": db.get("banner_video"),
                  "gif": db.get("banner_gif"), "text": db.get("banner") or ""}
        if any(legacy.values()): return legacy
    return None

async def send_with_banner(update, text, kb=None, section="main"):
    try:
        db = load_db(); b = get_banner(db, section)
        bv = b.get("video") if b else None; bg = b.get("gif") if b else None; bp = b.get("photo") if b else None
        banner_text = b.get("text","") if b else ""
        full_text = text + (f"\n\n<b>{banner_text}</b>" if banner_text else "")
        has_media = bool(bv or bg or bp)
        old_msg = None; old_has_media = False
        try:
            if update.callback_query:
                old_msg = update.callback_query.message
                if old_msg: old_has_media = bool(old_msg.photo or old_msg.video or old_msg.animation)
        except: pass
        if not has_media and not old_has_media and old_msg:
            try: await old_msg.edit_text(full_text, parse_mode="HTML", reply_markup=kb); return
            except: pass
        elif has_media and old_has_media and old_msg:
            try: await old_msg.edit_caption(caption=full_text, parse_mode="HTML", reply_markup=kb); return
            except:
                try: await old_msg.delete()
                except: pass
        elif old_msg:
            try: await old_msg.delete()
            except: pass
        if bv: await update.effective_chat.send_video(video=bv, caption=full_text, parse_mode="HTML", reply_markup=kb)
        elif bg: await update.effective_chat.send_animation(animation=bg, caption=full_text, parse_mode="HTML", reply_markup=kb)
        elif bp: await update.effective_chat.send_photo(photo=bp, caption=full_text, parse_mode="HTML", reply_markup=kb)
        else: await update.effective_chat.send_message(full_text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        logger.error(f"send_with_banner: {e}")
        try: await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)
        except: pass

async def edit_or_send(update, text, kb=None, section="main"):
    await send_with_banner(update, text, kb, section=section)

def main_kb(lang):
    ru = lang == "ru"
    support_label = "🆘 Тех. поддержка" if ru else "🆘 Tech Support"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 " + lbl(ru,"Создать сделку","Create Deal"), callback_data="menu_deal"),
         InlineKeyboardButton("⭐ " + lbl(ru,"Профиль","Profile"), callback_data="menu_profile")],
        [InlineKeyboardButton("💸 " + lbl(ru,"Пополнить/Вывод","Top Up/Withdraw"), callback_data="menu_balance"),
         InlineKeyboardButton("🪪 " + lbl(ru,"Мои сделки","My Deals"), callback_data="menu_my_deals")],
        [InlineKeyboardButton("🌍 " + lbl(ru,"Язык / Lang","Language"), callback_data="menu_lang"),
         InlineKeyboardButton("🏆 " + lbl(ru,"Топ сделок","Top Deals"), callback_data="menu_top")],
        [InlineKeyboardButton("👥 " + lbl(ru,"Рефералы","Referrals"), callback_data="menu_ref"),
         InlineKeyboardButton("📋 " + lbl(ru,"Реквизиты","Requisites"), callback_data="menu_req")],
        [InlineKeyboardButton(support_label, url="https://t.me/GiftDealsSupport")],
    ])

async def show_main(update, context, edit=False):
    try:
        db = load_db(); uid = update.effective_user.id; u = get_user(db, uid)
        lang = u.get("lang", "ru")
        desc = db.get("menu_description") or get_welcome(lang)
        await send_with_banner(update, desc, main_kb(lang), section="main")
    except Exception as e: logger.error(f"show_main: {e}")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        db = load_db(); uid = update.effective_user.id; u = get_user(db, uid)
        u["username"] = update.effective_user.username or ""
        args = context.args
        if args and args[0].startswith("ref_") and not u.get("ref_by"):
            ref_uid = args[0][4:]; ref_user = db.get("users", {}).get(ref_uid)
            if ref_uid != str(uid) and ref_user is not None:
                u["ref_by"] = ref_uid
                db["users"][ref_uid]["ref_count"] = db["users"][ref_uid].get("ref_count", 0) + 1
                add_log(db, "👥 Новый реферал", uid=uid, username=u["username"],
                    extra=f"Пришёл по реф. ссылке @{ref_user.get('username','?')}")
                tag = f"@{u['username']}" if u.get('username') else f"#{uid}"
                try:
                    rr = ref_user.get("lang","ru") == "ru"
                    await context.bot.send_message(chat_id=int(ref_uid),
                        text=f"👥 <b>{lbl(rr,'По вашей реферальной ссылке зарегистрировался новый пользователь!','A new user joined via your referral link!')}</b>\n\n<blockquote>{tag}</blockquote>",
                        parse_mode="HTML")
                except: pass
                if db.get("logs"):
                    await send_log_to_channel(context, db, db["logs"][-1], hidden=db.get("log_hidden",False))
        save_db(db); context.user_data.clear()
        if args and args[0].startswith("deal_"):
            deal_id = args[0][5:].upper(); d = db.get("deals",{}).get(deal_id)
            if d:
                buyer_tag = f"@{update.effective_user.username}" if update.effective_user.username else f"#{uid}"
                seller_uid = d.get("user_id"); lang = u.get("lang","ru"); ru = lang == "ru"
                if seller_uid and seller_uid == str(uid):
                    await update.effective_message.reply_text(
                        "⚠️ " + lbl(ru,"Вы не можете быть покупателем в своей же сделке.","You cannot be the buyer of your own deal."))
                    await show_main(update, context); return
                buyer_reqs = u.get("requisites",{})
                if not buyer_reqs.get("card") and not buyer_reqs.get("ton") and not buyer_reqs.get("stars"):
                    warn_e = ce("5420323339723881652","⚠️")
                    msg = (f"{warn_e} <b>{lbl(ru,'Вы не можете продолжить сделку, пока не добавите реквизиты.','You cannot proceed until you add your requisites.')}</b>\n\n"
                           f"<blockquote><b>{lbl(ru,'Реквизиты нужны на случай спора или возврата. Выберите что хотите добавить:','Requisites are needed in case of dispute. Choose what to add:')}</b></blockquote>")
                    kb = InlineKeyboardMarkup([
                        [InlineKeyboardButton("💳 " + lbl(ru,"Карта / СБП","Card / SBP"), callback_data=f"req_deal_card_{deal_id}")],
                        [InlineKeyboardButton("💎 TON / USDT", callback_data=f"req_deal_ton_{deal_id}")],
                        [InlineKeyboardButton("⭐️ " + lbl(ru,"Звёзды","Stars"), callback_data=f"req_deal_stars_{deal_id}")],
                    ])
                    await update.effective_message.reply_text(msg, parse_mode="HTML", reply_markup=kb)
                    context.user_data["pending_deal"] = deal_id; return
                add_log(db,"🔗 Покупатель открыл сделку",deal_id=deal_id,uid=uid,username=u["username"],extra=f"Продавец: {d.get('partner','?')}")
                db["deals"][deal_id]["buyer_uid"] = str(uid); save_db(db)
                if db.get("logs"): await send_log_to_channel(context,db,db["logs"][-1],hidden=db.get("log_hidden",False))
                if seller_uid:
                    try:
                        sl2 = get_lang(int(seller_uid)); rs2 = sl2=="ru"
                        await context.bot.send_message(chat_id=int(seller_uid),
                            text=f"{E['joined']} <b>{lbl(rs2,'Покупатель присоединился к сделке!','Buyer joined the deal!')}</b>\n\n"
                                 f"<blockquote><b>{lbl(rs2,'Сделка','Deal')}: #{deal_id}\n{lbl(rs2,'Покупатель','Buyer')}: {buyer_tag}</b></blockquote>",
                            parse_mode="HTML")
                    except Exception as e: logger.error(f"joined notify: {e}")
                await send_deal_card(update, context, deal_id, d, buyer=True); return
        await show_main(update, context)
    except Exception as e: logger.error(f"cmd_start: {e}")

def deal_types_kb(lang="ru"):
    ru = lang == "ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 NFT", callback_data="dt_nft"),
         InlineKeyboardButton("🎴 NFT Username", callback_data="dt_usr")],
        [InlineKeyboardButton("⭐️ " + lbl(ru,"Звёзды","Stars"), callback_data="dt_str"),
         InlineKeyboardButton("💎 " + lbl(ru,"Крипта","Crypto"), callback_data="dt_cry")],
        [InlineKeyboardButton("✈️ Telegram Premium", callback_data="dt_prm")],
        [InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")],
    ])

def role_kb(lang):
    ru = lang == "ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 " + lbl(ru,"Я покупатель","I am the Buyer"), callback_data="role_buyer")],
        [InlineKeyboardButton("🏷 " + lbl(ru,"Я продавец","I am the Seller"), callback_data="role_seller")],
        [InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")],
    ])

def validate_username(text):
    if not text.startswith("@"): return None, "must_start_with_at"
    uname = text[1:]
    if len(uname) < 4: return None, "too_short"
    if not all(c.isascii() and (c.isalnum() or c == '_') for c in uname): return None, "invalid_chars"
    return text, None

def validate_card(text):
    clean = text.replace(" ","").replace("-","").replace("+","")
    if text.startswith("+") or (clean.isdigit() and 10 <= len(clean) <= 12):
        if clean.isdigit() and 10 <= len(clean) <= 12: return text
    if clean.isdigit() and len(clean) in (14,16): return clean
    return None

def validate_nft_link(text, dtype):
    clean = text.replace("https://","").replace("http://","")
    if not clean.startswith("t.me/"): return False,"no_tme"
    if dtype == "nft" and not clean[5:].startswith("nft/"): return False,"wrong_nft"
    return True, None

async def on_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query; await q.answer(); d = q.data
        ud = context.user_data; uid = update.effective_user.id; lang = get_lang(uid); ru = lang=="ru"

        if d == "menu_ref": await show_ref(update, context); return
        if d == "menu_req": await show_req(update, context); return

        if d.startswith("req_del_confirm_"):
            # actual delete after confirmation
            field = d[16:]; db = load_db(); u = get_user(db, uid)
            if "requisites" not in u: u["requisites"] = {}
            u["requisites"].pop(field, None); save_db(db)
            await show_req(update, context); return

        if d.startswith("req_del_"):
            field = d[8:]
            names = {"card": lbl(ru,"карту","card"), "ton": lbl(ru,"TON кошелёк","TON wallet"),
                     "stars": lbl(ru,"@username для звёзд","Stars @username")}
            name = names.get(field, field)
            await edit_or_send(update,
                f"🗑 <b>{lbl(ru,'Удалить реквизит?','Delete requisite?')}</b>\n\n<blockquote><b>{name}</b></blockquote>",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ " + lbl(ru,"Да, удалить","Yes, delete"), callback_data=f"req_del_confirm_{field}")],
                    [InlineKeyboardButton("🔙 " + lbl(ru,"Отмена","Cancel"), callback_data="menu_req")],
                ]), section="profile")
            return

        if d.startswith("req_edit_"):
            field = d[9:]
            prompts = {
                "card":  (f"💳 <b>{lbl(ru,'Карта / СБП','Card / SBP')}</b>\n\n"
                          f"<blockquote><b>{lbl(ru,'Введите номер телефона (СБП) или номер карты (14 или 16 цифр).','Enter phone number (SBP) or card number (14 or 16 digits).')}\n\n"
                          f"{lbl(ru,'Примеры','Examples')}:\n<code>+79041751408</code>\n<code>4276123456781234</code></b></blockquote>"),
                "ton":   (f"💎 <b>TON / USDT</b>\n\n"
                          f"<blockquote><b>{lbl(ru,'Введите TON адрес (начинается с UQ или EQ).','Enter TON address (starts with UQ or EQ).')}\n\n"
                          f"{lbl(ru,'Пример','Example')}:\n<code>UQDxxx...xxx</code></b></blockquote>"),
                "stars": (f"{ce('5438496463044752972','⭐️')} <b>{lbl(ru,'Звёзды','Stars')}</b>\n\n"
                          f"<blockquote><b>{lbl(ru,'Введите ваш @юзернейм (только латиница).','Enter your @username (English only).')}\n\n"
                          f"{lbl(ru,'Пример','Example')}:\n<code>@username</code></b></blockquote>"),
            }
            context.user_data["req_step"] = field
            await edit_or_send(update, prompts.get(field,"?"),
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="menu_req")]]),
                section="profile")
            return

        if d.startswith("add_req_"):
            deal_id = d[8:]; context.user_data["req_for_deal"] = deal_id
            text = (f"{ce('5420323339723881652','⚠️')} <b>{lbl(ru,'Добавьте реквизиты для участия в сделке','Add requisites to join the deal')}</b>\n\n"
                    f"<blockquote><b>{lbl(ru,'Выберите способ получения средств в случае спора или возврата.','Choose a refund method in case of dispute.')}</b></blockquote>")
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 " + lbl(ru,"Карта / СБП","Card / SBP"), callback_data=f"req_deal_card_{deal_id}")],
                [InlineKeyboardButton("💎 TON " + lbl(ru,"адрес","address"), callback_data=f"req_deal_ton_{deal_id}")],
                [InlineKeyboardButton("⭐️ " + lbl(ru,"Юзернейм для звёзд","Stars username"), callback_data=f"req_deal_stars_{deal_id}")],
                [InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")],
            ])
            await edit_or_send(update, text, kb, section="deal_card"); return

        if d.startswith("req_deal_"):
            parts = d[9:].split("_",1); field = parts[0]; deal_id = parts[1] if len(parts)>1 else ""
            context.user_data["req_step"] = field; context.user_data["req_for_deal"] = deal_id
            prompts = {
                "card":  f"💳 <b>{lbl(ru,'Карта / СБП','Card / SBP')}</b>\n\n<blockquote><b>{lbl(ru,'Введите телефон (СБП) или карту (14/16 цифр).','Enter phone (SBP) or card (14/16 digits).')}\n\n{lbl(ru,'Примеры','Examples')}:\n<code>+79041751408</code>\n<code>4276123456781234</code></b></blockquote>",
                "ton":   f"💎 <b>TON {lbl(ru,'адрес','address')}</b>\n\n<blockquote><b>{lbl(ru,'Введите TON адрес (UQ или EQ).','Enter TON address (UQ or EQ).')}\n\n{lbl(ru,'Пример','Example')}:\n<code>UQDxxx...xxx</code></b></blockquote>",
                "stars": f"{ce('5438496463044752972','⭐️')} <b>{lbl(ru,'Звёзды','Stars')}</b>\n\n<blockquote><b>{lbl(ru,'Введите @юзернейм (только латиница).','Enter @username (English only).')}\n\n{lbl(ru,'Пример','Example')}:\n<code>@username</code></b></blockquote>",
            }
            await edit_or_send(update, prompts.get(field,"?"),
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data=f"add_req_{deal_id}")]]),
                section="deal_card")
            return

        if d == "main_menu":
            ud.clear()
            try: await q.message.delete()
            except: pass
            await show_main(update, context, edit=False); return

        if d == "menu_deal":
            ud.clear()
            try: await q.message.delete()
            except: pass
            await update.effective_message.reply_text(
                f"{E['pencil']} <b>{lbl(ru,'Создать сделку','Create Deal')}\n\n{lbl(ru,'Кто вы в этой сделке?','What is your role in this deal?')}</b>",
                parse_mode="HTML", reply_markup=role_kb(lang))
            return

        if d in ("role_buyer","role_seller"):
            ud["creator_role"] = "buyer" if d=="role_buyer" else "seller"
            try: await q.message.delete()
            except: pass
            await update.effective_message.reply_text(
                f"{E['pencil']} <b>{lbl(ru,'Создать сделку','Create Deal')}\n\n{lbl(ru,'Выберите тип','Choose type')}:</b>",
                parse_mode="HTML", reply_markup=deal_types_kb(lang))
            return

        if d == "menu_balance":
            try: await q.message.delete()
            except: pass
            await show_balance(update, context); return

        if d == "balance_topup":
            await edit_or_send(update, f"{E['money']} <b>{lbl(ru,'Выберите способ пополнения:','Choose top-up method:')}</b>",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("⭐️ " + lbl(ru,"Звёзды","Stars"), callback_data="balance_stars")],
                    [InlineKeyboardButton("💰 " + lbl(ru,"Рубли","Rubles"), callback_data="balance_rub")],
                    [InlineKeyboardButton("💎 TON / USDT", callback_data="balance_crypto")],
                    [InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="menu_balance")],
                ]), section="balance"); return

        if d == "menu_lang":
            try: await q.message.delete()
            except: pass
            await show_lang(update, context); return

        if d == "menu_profile":
            try: await q.message.delete()
            except: pass
            await show_profile(update, context); return

        if d == "menu_top":
            try: await q.message.delete()
            except: pass
            await show_top(update, context); return

        if d == "menu_my_deals":
            try: await q.message.delete()
            except: pass
            await show_my_deals(update, context); return

        if d.startswith("lang_"): await set_lang(update, context, d[5:]); return
        if d.startswith("balance_"): await show_balance_info(update, context, d[8:]); return
        if d == "withdraw": await show_withdraw(update, context); return

        if d.startswith("withdraw_"):
            method = d[9:]
            prompts = {"stars": lbl(ru,"Укажите @юзернейм получателя звёзд:","Enter @username to receive stars:"),
                       "crypto": lbl(ru,"Укажите TON/USDT адрес для вывода:","Enter TON/USDT address for withdrawal:"),
                       "card": lbl(ru,"Укажите номер карты для вывода:","Enter card number for withdrawal:")}
            context.user_data["withdraw_method"] = method; context.user_data["withdraw_step"] = "requisite"
            await edit_or_send(update,
                f"{E['wallet']} <b>{lbl(ru,'Вывод средств','Withdraw')}</b>\n\n<blockquote><b>{prompts.get(method,'?')}</b></blockquote>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="withdraw")]]),
                section="balance")
            return

        if d.startswith("rev_"):
            parts = d.split("_"); deal_id = parts[1]; role = parts[2]; stars = int(parts[3])
            context.user_data["review_deal"] = deal_id; context.user_data["review_role"] = role
            context.user_data["review_stars"] = stars; context.user_data["review_step"] = "text"
            star_e = ce("5438496463044752972","⭐️")
            await q.edit_message_text(
                f"{star_e * stars} {lbl(ru,'Оценка','Rating')}: {stars}/5\n\n{lbl(ru,'Напишите комментарий к отзыву','Write a review comment')}:",
                parse_mode="HTML")
            return

        # Admin delete review
        if d.startswith("adm_del_rev_"):
            parts = d[12:].split("_", 1)
            target_uid = parts[0]; rev_idx = int(parts[1]) if len(parts)>1 else -1
            db = load_db()
            if target_uid in db["users"] and rev_idx >= 0:
                reviews = db["users"][target_uid].get("reviews",[])
                if 0 <= rev_idx < len(reviews):
                    reviews.pop(rev_idx); db["users"][target_uid]["reviews"] = reviews; save_db(db)
                    await q.answer("Отзыв удалён ✅")
                    # Reload review list
                    u2 = db["users"][target_uid]; uname2 = u2.get("username","?")
                    revs = u2.get("reviews",[])
                    if not revs:
                        await q.edit_message_text(f"<b>@{uname2}: отзывов нет</b>", parse_mode="HTML",
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="adm_back")]]))
                    else:
                        lines = [f"<b>📋 Отзывы @{uname2}:</b>"]
                        rows = []
                        for i, r in enumerate(revs):
                            lines.append(f"\n{i+1}. {r}")
                            rows.append([InlineKeyboardButton(f"🗑 Удалить #{i+1}", callback_data=f"adm_del_rev_{target_uid}_{i}")])
                        rows.append([InlineKeyboardButton("🔙 Назад", callback_data="adm_back")])
                        await q.edit_message_text("\n".join(lines), parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))
            return

        if d.startswith("paid_"): await on_paid(update, context); return

        # Balance topup "I sent" button
        if d.startswith("topup_sent_"):
            method = d[11:]; db = load_db(); u2 = get_user(db, uid)
            uname2 = update.effective_user.username or str(uid)
            methods_map = {"stars": "Звёзды", "rub": "Рубли", "crypto": "TON/USDT"}
            mname = methods_map.get(method, method)
            try:
                await context.bot.send_message(chat_id=ADMIN_ID,
                    text=f"{E['bell']} <b>Запрос на пополнение — {mname}</b>\n{E['user']} @{uname2} (<code>{uid}</code>)\n\nПроверьте поступление и подтвердите:",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("✅ Пришло", callback_data=f"adm_topup_ok_{uid}_{method}"),
                        InlineKeyboardButton("❌ Не пришло", callback_data=f"adm_topup_no_{uid}"),
                    ]]))
            except Exception as e: logger.error(f"topup_sent admin: {e}")
            await q.edit_message_reply_markup(InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ " + lbl(ru,"Ожидание подтверждения...","Waiting for confirmation..."), callback_data="noop")],
                [InlineKeyboardButton("🏠 " + lbl(ru,"Главное меню","Main menu"), callback_data="main_menu")],
            ]))
            return

        if d.startswith("adm_topup_ok_"):
            if update.effective_user.id != ADMIN_ID: return
            parts = d[13:].split("_",1); target_uid = parts[0]; method = parts[1] if len(parts)>1 else "?"
            await q.edit_message_text(f"✅ <b>Пополнение подтверждено!</b>\nПользователь: <code>{target_uid}</code>", parse_mode="HTML")
            try:
                tl = get_lang(int(target_uid)); tr = tl=="ru"
                await context.bot.send_message(chat_id=int(target_uid),
                    text=f"{E['check']} <b>{lbl(tr,'Ваш баланс пополнен! Спасибо.','Your balance has been topped up! Thank you.')}</b>",
                    parse_mode="HTML")
            except: pass
            return

        if d.startswith("adm_topup_no_"):
            if update.effective_user.id != ADMIN_ID: return
            target_uid = d[13:]
            await q.edit_message_text(f"❌ <b>Пополнение не подтверждено.</b>\nПользователь: <code>{target_uid}</code>", parse_mode="HTML")
            try:
                tl = get_lang(int(target_uid)); tr = tl=="ru"
                await context.bot.send_message(chat_id=int(target_uid),
                    text=f"{E['cross']} <b>{lbl(tr,'Пополнение не было найдено. Обратитесь к менеджеру.','Top-up not found. Please contact manager.')}</b>",
                    parse_mode="HTML")
            except: pass
            return

        if d == "noop": return
        if d.startswith("adm_confirm_"): await adm_confirm(update, context); return
        if d.startswith("adm_decline_"): await adm_decline(update, context); return
        if d == "adm_back":
            try: await q.message.edit_text(f"{E['shield']} <b>Панель администратора</b>", parse_mode="HTML", reply_markup=adm_kb())
            except: await q.message.reply_text(f"{E['shield']} <b>Панель администратора</b>", parse_mode="HTML", reply_markup=adm_kb())
            return
        if d.startswith("adm_"): await handle_adm_cb(update, context); return

        type_map = {"dt_nft":"nft","dt_usr":"username","dt_str":"stars","dt_cry":"crypto","dt_prm":"premium","dt_pst":"premium_stickers"}
        if d in type_map:
            ud["type"] = type_map[d]; ud["step"] = "partner"
            creator_role = ud.get("creator_role","seller")
            partner_prompt = lbl(ru,"Введите @username продавца:","Enter seller @username:") if creator_role=="buyer" else lbl(ru,"Введите @username покупателя:","Enter buyer @username:")
            try: await q.message.delete()
            except: pass
            msg = await update.effective_chat.send_message(
                f"{partner_prompt}\n\n<b>{lbl(ru,'Пример','Example')}:</b> <code>@username</code>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="menu_deal")]]))
            ud["last_bot_msg"] = msg.message_id; return

        if d == "cry_ton":
            ud["currency"] = "TON"; ud["step"] = "amount"
            try: await q.message.delete()
            except: pass
            msg = await update.effective_chat.send_message(f"💎 {lbl(ru,'Введите сумму','Enter amount')} (TON):", parse_mode="HTML")
            ud["last_bot_msg"] = msg.message_id; return

        if d == "cry_usd":
            ud["currency"] = "USDT"; ud["step"] = "amount"
            try: await q.message.delete()
            except: pass
            msg = await update.effective_chat.send_message(f"💵 {lbl(ru,'Введите сумму','Enter amount')} (USDT):", parse_mode="HTML")
            ud["last_bot_msg"] = msg.message_id; return

        if d in ("prm_3","prm_6","prm_12"):
            periods_ru = {"prm_3":"3 месяца","prm_6":"6 месяцев","prm_12":"12 месяцев"}
            periods_en = {"prm_3":"3 months","prm_6":"6 months","prm_12":"12 months"}
            ud["premium_period"] = (periods_ru if ru else periods_en)[d]; ud["step"] = "currency"
            try: await q.message.delete()
            except: pass
            msg = await update.effective_chat.send_message(lbl(ru,"Выберите валюту:","Choose currency:"), reply_markup=cur_kb(lang), parse_mode="HTML")
            ud["last_bot_msg"] = msg.message_id; return

        if d in ("pst_1","pst_3","pst_5","pst_10"):
            counts_ru = {"pst_1":"1 пак","pst_3":"3 пака","pst_5":"5 паков","pst_10":"10 паков"}
            counts_en = {"pst_1":"1 pack","pst_3":"3 packs","pst_5":"5 packs","pst_10":"10 packs"}
            ud["sticker_count"] = (counts_ru if ru else counts_en)[d]; ud["step"] = "currency"
            try: await q.message.delete()
            except: pass
            msg = await update.effective_chat.send_message(lbl(ru,"Выберите валюту:","Choose currency:"), reply_markup=cur_kb(lang), parse_mode="HTML")
            ud["last_bot_msg"] = msg.message_id; return

        if d.startswith("cur_"):
            ud["currency"] = CURMAP.get(d,d); ud["step"] = "amount"
            try: await q.message.delete()
            except: pass
            cur_code = CURMAP.get(d,d)
            msg = await update.effective_chat.send_message(
                f"{lbl(ru,'Введите сумму сделки','Enter deal amount')} ({cur_code}):", parse_mode="HTML")
            ud["last_bot_msg"] = msg.message_id; return

    except Exception as e: logger.error(f"on_cb: {e}")

async def on_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ud = context.user_data; uid = update.effective_user.id; lang = get_lang(uid); ru = lang=="ru"
        text = update.message.text.strip() if update.message.text else ""
        if uid == ADMIN_ID and ud.get("adm_step"): await handle_adm_msg(update, context); return

        if ud.get("req_step") in ("card","ton","stars"):
            field = ud.get("req_step"); db = load_db(); u = get_user(db, uid)
            if not u.get("requisites"): u["requisites"] = {}
            err = None
            if field == "card":
                result = validate_card(text)
                if result is None:
                    err = lbl(ru,"Введите корректный номер телефона (СБП) или карты (14 или 16 цифр).\n\nПримеры:\n<code>+79041751408</code>\n<code>4276123456781234</code>",
                              "Enter a valid phone number (SBP) or card number (14 or 16 digits).\n\nExamples:\n<code>+79041751408</code>\n<code>4276123456781234</code>")
                else: text = result
            elif field == "ton":
                if not ((text.startswith("UQ") or text.startswith("EQ")) and len(text) >= 40):
                    err = lbl(ru,"Введите корректный TON адрес (начинается с UQ или EQ).\n\nПример:\n<code>UQDxxx...xxx</code>",
                              "Enter a valid TON address (starts with UQ or EQ).\n\nExample:\n<code>UQDxxx...xxx</code>")
            elif field == "stars":
                t_input = text if text.startswith("@") else f"@{text}"
                cleaned, err_code = validate_username(t_input)
                if err_code == "invalid_chars":
                    err = lbl(ru,"Юзернейм должен содержать только латинские буквы, цифры и _.\n\nПример:\n<code>@username</code>",
                              "Username must contain only English letters, digits and _.\n\nExample:\n<code>@username</code>")
                elif err_code:
                    err = lbl(ru,"Введите корректный @юзернейм.\n\nПример:\n<code>@username</code>",
                              "Enter a valid @username.\n\nExample:\n<code>@username</code>")
                else: text = cleaned
            if err:
                await update.message.reply_text(f"❌ {err}", parse_mode="HTML"); return
            u["requisites"][field] = text; save_db(db); ud.pop("req_step",None)
            pending_deal = ud.pop("req_for_deal",None) or ud.pop("pending_deal",None)
            if pending_deal:
                db2 = load_db(); d2 = db2.get("deals",{}).get(pending_deal)
                if d2:
                    await update.message.reply_text(
                        f"{ce('5206607081334906820','✅')} <b>{lbl(ru,'Реквизиты сохранены! Открываем сделку...','Requisites saved! Opening deal...')}</b>",
                        parse_mode="HTML")
                    add_log(db2,"🔗 Покупатель открыл сделку",deal_id=pending_deal,uid=uid,username=u.get("username",""))
                    db2["deals"][pending_deal]["buyer_uid"] = str(uid); save_db(db2)
                    if db2.get("logs"): await send_log_to_channel(context,db2,db2["logs"][-1],hidden=db2.get("log_hidden",False))
                    await send_deal_card(update, context, pending_deal, d2, buyer=True); return
            await update.message.reply_text(
                f"{ce('5206607081334906820','✅')} <b>{lbl(ru,'Реквизиты сохранены!','Requisites saved!')}</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 " + lbl(ru,"Мои реквизиты","My Requisites"), callback_data="menu_req")]]))
            return

        if ud.get("withdraw_step") == "requisite":
            method = ud.get("withdraw_method","?"); db = load_db()
            uid3 = uid; u3 = get_user(db, uid3); bal = u3.get("balance",0)
            uname3 = update.effective_user.username or str(uid3)
            methods = {"stars": lbl(ru,"Звёзды","Stars"), "crypto": lbl(ru,"Крипта","Crypto"), "card": lbl(ru,"Карта","Card")}
            mname = methods.get(method, method)
            try:
                await context.bot.send_message(chat_id=ADMIN_ID,
                    text=f"{E['gem']} <b>Запрос на вывод — {mname}</b>\n{E['user']} @{uname3} (<code>{uid3}</code>)\n{CM} {bal} RUB\n\nРеквизиты: <code>{text}</code>",
                    parse_mode="HTML")
            except Exception as e: logger.error(f"withdraw req admin: {e}")
            ud.pop("withdraw_step",None); ud.pop("withdraw_method",None)
            await update.message.reply_text(
                f"{E['check']} <b>{lbl(ru,'Запрос отправлен!','Request sent!')}</b>\n\n"
                f"<blockquote><b>{lbl(ru,'Способ','Method')}: {mname}\n{lbl(ru,'Сумма','Amount')}: {bal} RUB\n\n"
                f"{lbl(ru,'Менеджер свяжется с вами в ближайшее время.','Manager will contact you shortly.')}</b></blockquote>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💬 " + lbl(ru,"Менеджер","Manager"), url=f"https://t.me/{MANAGER_USERNAME.lstrip('@')}")],
                    [InlineKeyboardButton("🏠 " + lbl(ru,"Главное меню","Main menu"), callback_data="main_menu")]
                ]))
            return

        if ud.get("review_step") == "text":
            deal_id = ud.get("review_deal"); role = ud.get("review_role"); stars = ud.get("review_stars",5)
            db = load_db(); deal = db.get("deals",{}).get(deal_id,{})
            # FIX: use premium stars emoji in review
            star_str = f"{E['star_prem']} " * stars
            review_text = f"{star_str.strip()} {stars}/5 — {text}"
            saved = False
            if role == "s":
                buyer_uname = deal.get("partner","").lstrip("@").lower()
                buyer_uid = next((k for k,v in db.get("users",{}).items() if v.get("username","").lower()==buyer_uname), None)
                if not buyer_uid and deal.get("buyer_uid"): buyer_uid = deal.get("buyer_uid")
                if buyer_uid and buyer_uid in db["users"]:
                    db["users"][buyer_uid].setdefault("reviews",[]).append(review_text); save_db(db); saved = True
            elif role == "b":
                seller_uid = deal.get("user_id")
                if seller_uid and seller_uid in db.get("users",{}):
                    db["users"][seller_uid].setdefault("reviews",[]).append(review_text); save_db(db); saved = True
            ud.pop("review_step",None); ud.pop("review_deal",None); ud.pop("review_role",None); ud.pop("review_stars",None)
            await update.message.reply_text(
                f"✅ <b>{lbl(ru,'Отзыв сохранён!','Review saved!') if saved else lbl(ru,'Отзыв принят!','Review received!')}</b>",
                parse_mode="HTML")
            return

        dtype = ud.get("type"); step = ud.get("step")
        if not dtype or not step: return

        async def delete_prev():
            try: await update.message.delete()
            except: pass
            if ud.get("last_bot_msg"):
                try: await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=ud["last_bot_msg"])
                except: pass

        async def send_step(msg_text, kb=None):
            await delete_prev()
            msg = await update.effective_chat.send_message(msg_text, parse_mode="HTML", reply_markup=kb)
            ud["last_bot_msg"] = msg.message_id

        if step == "partner":
            if not text.startswith("@"): text = "@" + text
            cleaned, err_code = validate_username(text)
            if err_code == "invalid_chars":
                await update.message.reply_text(
                    f"❌ <b>{lbl(ru,'Юзернейм должен содержать только латинские буквы, цифры и _.','Username must contain only English letters, digits and _.')}</b>\n\n"
                    f"<b>{lbl(ru,'Пример','Example')}:</b> <code>@username</code>", parse_mode="HTML"); return
            if err_code:
                await update.message.reply_text(
                    f"❌ <b>{lbl(ru,'Неверный формат. Введите @username (мин. 4 символа)','Invalid format. Enter @username (min 4 chars)')}</b>\n\n"
                    f"<b>{lbl(ru,'Пример','Example')}:</b> <code>@username</code>", parse_mode="HTML"); return
            ud["partner"] = cleaned
            if dtype == "nft":
                ud["step"] = "nft_link"
                await send_step(f"{E['nft']} <b>{lbl(ru,'НФТ','NFT')}\n\n{lbl(ru,'Вставьте ссылку на НФТ (t.me/nft/...)','Paste the NFT link (t.me/nft/...)')}:</b>")
            elif dtype == "username":
                ud["step"] = "trade_usr"
                await send_step(f"{E['user']} <b>{lbl(ru,'NFT Юзернейм','NFT Username')}\n\n{lbl(ru,'Введите t.me/... ссылку или @юзернейм товара','Enter the t.me/... link or @username of the item')}:</b>")
            elif dtype == "stars":
                ud["step"] = "stars_cnt"
                await send_step(f"{E['star_prem']} <b>{lbl(ru,'Звёзды Telegram','Telegram Stars')}\n\n{lbl(ru,'Сколько звёзд?','How many stars?')}</b>")
            elif dtype == "crypto":
                ud["step"] = "cry_currency"
                await send_step(f"{E['diamond']} <b>{lbl(ru,'Крипта','Crypto')}\n\n{lbl(ru,'Выберите валюту','Choose currency')}:</b>",
                    InlineKeyboardMarkup([[InlineKeyboardButton("💎 TON", callback_data="cry_ton"),
                                           InlineKeyboardButton("💵 USDT", callback_data="cry_usd")]]))
            elif dtype == "premium":
                ud["step"] = "prem_period"
                await send_step(f"{E['premium']} <b>Telegram Premium\n\n{lbl(ru,'Выберите срок','Choose period')}:</b>",
                    InlineKeyboardMarkup([[
                        InlineKeyboardButton("3 " + lbl(ru,"месяца","months"), callback_data="prm_3"),
                        InlineKeyboardButton("6 " + lbl(ru,"месяцев","months"), callback_data="prm_6"),
                        InlineKeyboardButton("12 " + lbl(ru,"месяцев","months"), callback_data="prm_12")]]))
            elif dtype == "premium_stickers":
                ud["step"] = "sticker_pack"
                await send_step(f"{E['sticker']} <b>{lbl(ru,'Премиум стикеры','Premium Stickers')}\n\n{lbl(ru,'Выберите количество стикерпаков','Choose number of packs')}:</b>",
                    InlineKeyboardMarkup([
                        [InlineKeyboardButton("1 " + lbl(ru,"пак","pack"), callback_data="pst_1"),
                         InlineKeyboardButton("3 " + lbl(ru,"пака","packs"), callback_data="pst_3")],
                        [InlineKeyboardButton("5 " + lbl(ru,"паков","packs"), callback_data="pst_5"),
                         InlineKeyboardButton("10 " + lbl(ru,"паков","packs"), callback_data="pst_10")]]))
            return

        if step == "nft_link":
            ok, errmsg = validate_nft_link(text, dtype)
            if not ok:
                disp = lbl(ru,"Ссылка должна начинаться с t.me/","Link must start with t.me/") if errmsg=="no_tme" else lbl(ru,"Для NFT сделок используйте ссылку t.me/nft/...","For NFT deals use a t.me/nft/... link.")
                await update.message.reply_text(f"{E['cross']} <b>{disp}</b>", parse_mode="HTML"); return
            ud["nft_link"] = text; ud["step"] = "currency"
            await send_step(f"{E['nft']} <b>{lbl(ru,'НФТ','NFT')}\n\n{lbl(ru,'Выберите валюту','Choose currency')}:</b>", cur_kb(lang)); return

        if step == "trade_usr":
            cl = text.replace("https://","").replace("http://","")
            if not cl.startswith("t.me/") and not text.startswith("@"):
                await update.message.reply_text(
                    f"{E['cross']} <b>{lbl(ru,'Введите t.me/... ссылку или @юзернейм.','Enter a t.me/... link or @username.')}</b>",
                    parse_mode="HTML"); return
            ud["trade_username"] = text; ud["step"] = "currency"
            await send_step(f"{E['user']} <b>{lbl(ru,'NFT Юзернейм','NFT Username')}\n\n{lbl(ru,'Выберите валюту','Choose currency')}:</b>", cur_kb(lang)); return

        if step == "stars_cnt":
            if not text.isdigit():
                await update.message.reply_text(f"{E['cross']} <b>{lbl(ru,'Только цифры!','Numbers only!')}</b>", parse_mode="HTML"); return
            ud["stars_count"] = text; ud["step"] = "currency"
            await send_step(f"{E['star_prem']} <b>{lbl(ru,'Звёзды Telegram','Telegram Stars')}\n\n{lbl(ru,'Выберите валюту','Choose currency')}:</b>", cur_kb(lang)); return

        if step == "amount":
            clean_amt = text.replace(" ","").replace(",",".")
            try: float(clean_amt)
            except ValueError:
                await update.message.reply_text(
                    f"❌ <b>{lbl(ru,'Введите сумму цифрами. Пример: 500 или 1.5','Enter amount as number. Example: 500 or 1.5')}</b>",
                    parse_mode="HTML"); return
            await delete_prev()
            ud["amount"] = clean_amt; await finalize_deal(update, context); return

    except Exception as e: logger.error(f"on_msg: {e}")

async def finalize_deal(update, context):
    try:
        db = load_db(); ud = context.user_data
        deal_id = gen_deal_id(db); dtype = ud.get("type","?"); partner = ud.get("partner","—")
        currency = ud.get("currency","—"); amount = ud.get("amount","—"); user = update.effective_user
        creator_role = ud.get("creator_role","seller")
        db["deals"][deal_id] = {
            "user_id": str(user.id), "type": dtype, "partner": partner,
            "currency": currency, "amount": amount, "status": "pending",
            "created": datetime.now().isoformat(), "data": dict(ud), "creator_role": creator_role,
        }
        add_log(db,"🆕 Новая сделка",deal_id=deal_id,uid=user.id,username=user.username or "",extra=f"Тип: {dtype} | Сумма: {amount} {currency}")
        save_db(db)
        if db.get("logs"): await send_log_to_channel(context,db,db["logs"][-1],hidden=db.get("log_hidden",False))
        await send_deal_card(update, context, deal_id, db["deals"][deal_id], buyer=False)
        pname = partner.lstrip("@").lower() if partner.startswith("@") else None
        if pname:
            puid = next((k for k,v in db["users"].items() if v.get("username","").lower()==pname), None)
            if puid:
                try:
                    buyer_lang = get_lang(int(puid)); ru_b = buyer_lang=="ru"
                    txt = build_deal_card_text(deal_id,db["deals"][deal_id],f"@{user.username or str(user.id)}",None,buyer_lang,is_buyer=True)
                    kb = InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ " + lbl(ru_b,"Я оплатил","I paid"), callback_data=f"paid_{deal_id}")],
                        [InlineKeyboardButton("🏠 " + lbl(ru_b,"Главное меню","Main menu"), callback_data="main_menu")]
                    ])
                    await context.bot.send_message(chat_id=int(puid), text=txt, parse_mode="HTML", reply_markup=kb)
                except Exception as e: logger.error(f"notify partner: {e}")
        context.user_data.clear()
    except Exception as e: logger.error(f"finalize_deal: {e}")

def build_item_line(dtype, dd, lang="ru"):
    ru = lang=="ru"
    if dtype == "nft": return f"\n{E['link']} {lbl(ru,'Ссылка','Link')}: {dd.get('nft_link','—')}"
    elif dtype == "username": return f"\n{E['user']} {lbl(ru,'Юзернейм','Username')}: {dd.get('trade_username','—')}"
    elif dtype == "stars": return f"\n{E['star_prem']} {lbl(ru,'Звёзд','Stars')}: {dd.get('stars_count','—')}"
    elif dtype == "premium": return f"\n{E['clock']} {lbl(ru,'Срок','Period')}: {dd.get('premium_period','—')}"
    elif dtype == "premium_stickers": return f"\n{E['sticker']} {lbl(ru,'Паков','Packs')}: {dd.get('sticker_count','—')}"
    return ""

def build_deal_card_text(deal_id, d, creator_display, partner_display_override, lang, is_buyer=False):
    ru = lang=="ru"
    dtype = d.get("type",""); cur = d.get("currency","—"); amt = d.get("amount","—")
    item = build_item_line(dtype, d.get("data",{}), lang)
    item_str = f"\n{item.strip()}" if item.strip() else ""
    # FIX: amount without flag
    cur_plain = CUR_NATIVE_NAMES.get(cur, cur)
    amt_str = f"{amt} {cur_plain}"
    creator_role = d.get("creator_role","seller")
    if creator_role == "buyer":
        creator_section = lbl(ru,"Покупатель","Buyer"); partner_section = lbl(ru,"Продавец","Seller")
        role_note = lbl(ru,"⚠️ Продавец должен передать товар покупателю через менеджера @GiftDealsManager",
                          "⚠️ The Seller must deliver the item to the Buyer via manager @GiftDealsManager")
    else:
        creator_section = lbl(ru,"Продавец","Seller"); partner_section = lbl(ru,"Покупатель","Buyer")
        role_note = lbl(ru,"⚠️ Продавец должен передать товар покупателю через менеджера @GiftDealsManager",
                          "⚠️ The Seller must deliver the item to the Buyer via manager @GiftDealsManager")
    db = load_db()
    def user_block(section_label, uname_display, uid_str):
        udata = db["users"].get(uid_str,{}) if uid_str else {}
        ud_deals = udata.get("success_deals",0); ud_turn = udata.get("turnover",0)
        ud_rep = udata.get("reputation",0); ud_reviews = udata.get("reviews",[])
        ud_status = udata.get("status","")
        status_line = f"\n{ce('5438496463044752972','⭐️')} <b>{ud_status}</b>" if ud_status else ""
        rev_text = ("\n\n" + "\n".join(f"  • {r}" for r in ud_reviews[-3:])) if ud_reviews else ""
        return (
            f"{ce('5199552030615558774','👤')} <b>{section_label}</b>\n"
            f"<blockquote><b>{uname_display}</b>{status_line}\n"
            f"{ce('5274055917766202507','✅')} {lbl(ru,'Сделок','Deals')}: <b>{ud_deals}</b>\n"
            f"{ce('5278467510604160626','💰')} {lbl(ru,'Оборот','Turnover')}: <b>{ud_turn} ₽</b>\n"
            f"{ce('5463289097336405244','⭐️')} {lbl(ru,'Репутация','Reputation')}: <b>{ud_rep}</b>\n"
            f"{ce('5303138782004924588','💬')} {lbl(ru,'Отзывов','Reviews')}: <b>{len(ud_reviews)}</b>{rev_text}</blockquote>\n\n"
        )
    creator_uid = d.get("user_id")
    if creator_display is None:
        u_data = db["users"].get(creator_uid,{}) if creator_uid else {}
        u_uname = u_data.get("username","")
        creator_display = f"@{u_uname}" if u_uname else f"#{creator_uid}"
    partner_uname = d.get("partner","").lstrip("@").lower()
    partner_uid = next((k for k,v in db.get("users",{}).items() if v.get("username","").lower()==partner_uname), None)
    if partner_display_override is not None:
        partner_display = partner_display_override
    else:
        partner_display = d.get("partner","—")
    card_title = lbl(ru,"Сделка","Deal") if is_buyer else lbl(ru,"Сделка создана","Deal created")
    return (
        f"<tg-emoji emoji-id='5206607081334906820'>✅</tg-emoji> <b>{card_title} #{deal_id}</b>\n\n"
        f"<b>{lbl(ru,'Тип','Type')}:</b> {tname(dtype,lang)}{item_str}\n"
        f"<b>{lbl(ru,'Сумма','Amount')}:</b> {amt_str}\n\n"
        f"{user_block(creator_section, creator_display, creator_uid)}"
        f"{user_block(partner_section, partner_display, partner_uid)}"
        f"{E['security_e']} <b>{lbl(ru,'Гарантия безопасности','Security Guarantee')}</b>\n"
        f"<blockquote><b>{lbl(ru,'Средства заморожены до подтверждения передачи. Сделка защищена платформой Gift Deals.','Funds are frozen until the transfer is confirmed. The deal is protected by Gift Deals.')}</b></blockquote>\n\n"
        f"{E['warning']} <b>{lbl(ru,'Важно','Important')}:</b>\n"
        f"<blockquote><b>{role_note}</b></blockquote>\n\n"
        f"{E['requisites']} <b>СБП / Карта {CARD_BANK}:</b>\n"
        f"<blockquote><b>{lbl(ru,'Телефон','Phone')}: <code>{CARD_NUMBER}</code>\n{lbl(ru,'Получатель','Recipient')}: {CARD_NAME}\n{lbl(ru,'Банк','Bank')}: {CARD_BANK}</b></blockquote>\n\n"
        f"{E['tonkeeper']} <b>TON / USDT:</b>\n"
        f"<blockquote><b>{lbl(ru,'TON адрес','TON address')}:\n<code>{CRYPTO_ADDRESS}</code>\n\n{E['cryptobot']} {lbl(ru,'Крипто бот','Crypto bot')}: {CRYPTO_BOT}</b></blockquote>\n\n"
        f"{E['star_prem']} <b>{lbl(ru,'Звёзды / NFT','Stars / NFT')}:</b>\n"
        f"<blockquote><b>{lbl(ru,'Отправьте звёзды менеджеру','Send stars to manager')}: @GiftDealsManager</b></blockquote>\n\n"
        f"<tg-emoji emoji-id='5206607081334906820'>✅</tg-emoji> {lbl(ru,'После перевода нажмите «Я оплатил»','After payment press «I paid»')}"
    )

async def send_deal_card(update, context, deal_id, d, buyer=False):
    try:
        db = load_db(); lang = get_lang(update.effective_user.id); ru = lang=="ru"
        partner = d.get("partner","—"); creator_uid = d.get("user_id")
        creator_uname = db["users"].get(creator_uid,{}).get("username","") if creator_uid else ""
        creator_display = f"@{creator_uname}" if creator_uname else f"#{creator_uid}"
        if buyer:
            buyer_uname = update.effective_user.username or ""
            buyer_display = f"@{buyer_uname}" if buyer_uname else f"#{update.effective_user.id}"
            text = build_deal_card_text(deal_id, d, creator_display, buyer_display, lang, is_buyer=True)
            pu = f"https://t.me/{partner.lstrip('@')}" if partner.startswith("@") else f"https://t.me/{MANAGER_USERNAME.lstrip('@')}"
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ " + lbl(ru,"Я оплатил","I paid"), callback_data=f"paid_{deal_id}")],
                # FIX: "Написать продавцу" — link to partner's @username
                [InlineKeyboardButton("💬 " + lbl(ru,"Написать продавцу","Write to seller"), url=pu)],
                [InlineKeyboardButton("🆘 " + lbl(ru,"Тех. поддержка","Tech Support"), url="https://t.me/GiftDealsSupport")],
                [InlineKeyboardButton("🏠 " + lbl(ru,"Главное меню","Main menu"), callback_data="main_menu")]
            ])
        else:
            text = build_deal_card_text(deal_id, d, creator_display, None, lang, is_buyer=False)
            link_label = lbl(ru,"Ссылка для покупателя","Link for buyer")
            send_label = lbl(ru,"Отправьте ссылку партнёру.","Send the link to your partner.")
            text += f"\n\n{E['deal_link']} {link_label}:\n<code>https://t.me/{BOT_USERNAME}?start=deal_{deal_id}</code>\n\n{send_label}"
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 " + lbl(ru,"Главное меню","Main menu"), callback_data="main_menu")]])
        await send_with_banner(update, text, kb, section="deal_card")
    except Exception as e: logger.error(f"send_deal_card: {e}")

async def on_paid(update, context):
    try:
        q = update.callback_query; buyer = update.effective_user
        buyer_lang = get_lang(buyer.id); ru_b = buyer_lang=="ru"
        await q.answer(lbl(ru_b,"Уведомление отправлено!","Notification sent!"))
        deal_id = q.data[5:]; btag = f"@{buyer.username}" if buyer.username else str(buyer.id)
        db = load_db(); d = db.get("deals",{}).get(deal_id,{})
        amt = d.get("amount","—"); cur = d.get("currency","—"); dtype = d.get("type","")
        seller_uid = d.get("user_id"); seller_lang = get_lang(int(seller_uid)) if seller_uid else "ru"; ru_s = seller_lang=="ru"
        adm_txt = (f"{E['bell']} <b>Покупатель нажал «Я оплатил»</b>\n\n{E['deal']} <code>{deal_id}</code>\n"
                   f"{E['user']} {btag} (<code>{buyer.id}</code>)\n{E['pin']} {TNAMES_RU.get(dtype,dtype)}\n{CM} {amt} {cur}\n\nПроверьте поступление:")
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=adm_txt, parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ Пришла", callback_data=f"adm_confirm_{deal_id}"),
                    InlineKeyboardButton("❌ Не пришла", callback_data=f"adm_decline_{deal_id}")
                ]]))
        except Exception as e: logger.error(f"on_paid admin: {e}")
        add_log(db,"💳 Покупатель оплатил",deal_id=deal_id,uid=buyer.id,username=buyer.username or "",extra=f"Сумма: {amt} {cur}")
        save_db(db)
        if db.get("logs"): await send_log_to_channel(context,db,db["logs"][-1],hidden=db.get("log_hidden",False))
        seller = d.get("user_id")
        if seller and seller != str(buyer.id):
            try:
                await context.bot.send_message(chat_id=int(seller),
                    text=f"{E['bell']} <b>{lbl(ru_s,'Покупатель сообщил об оплате!','Buyer reported payment!')}</b>\n<code>{deal_id}</code>\n{E['user']} {btag}\n{CM} {amt} {cur}",
                    parse_mode="HTML")
            except Exception as e: logger.error(f"on_paid seller: {e}")
        try:
            await q.edit_message_reply_markup(InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ " + lbl(ru_b,"Ожидание подтверждения...","Waiting for confirmation..."), callback_data="noop")],
                [InlineKeyboardButton("🏠 " + lbl(ru_b,"Главное меню","Main menu"), callback_data="main_menu")]
            ]))
        except Exception as e: logger.error(f"on_paid edit: {e}")
    except Exception as e: logger.error(f"on_paid: {e}")

async def adm_confirm(update, context):
    try:
        q = update.callback_query; await q.answer()
        if update.effective_user.id != ADMIN_ID: return
        deal_id = q.data[12:]; db = load_db()
        if deal_id in db.get("deals",{}):
            db["deals"][deal_id]["status"] = "confirmed"; d = db["deals"][deal_id]
            s = d.get("user_id"); amt_str = d.get("amount","0"); dtype = d.get("type",""); dd = d.get("data",{})
            try: amt_num = float(amt_str)
            except: amt_num = 0
            if s and s in db["users"]:
                db["users"][s]["success_deals"] = db["users"][s].get("success_deals",0)+1
                db["users"][s]["total_deals"] = db["users"][s].get("total_deals",0)+1
                db["users"][s]["turnover"] = db["users"][s].get("turnover",0)+int(amt_num)
            item_link_log=""; item_link_msg=""
            if dtype=="nft" and dd.get("nft_link"): item_link_log=f"🔗 NFT: {dd['nft_link']}"; item_link_msg=f"\n🔗 <b>NFT:</b> {dd['nft_link']}"
            elif dtype=="username" and dd.get("trade_username"): item_link_log=f"🔗 Username: {dd['trade_username']}"; item_link_msg=f"\n🔗 <b>Username:</b> {dd['trade_username']}"
            seller_uname = db["users"].get(s,{}).get("username","?") if s else "?"
            add_log(db,"✅ Сделка подтверждена",deal_id=deal_id,uid=s,username=seller_uname,extra=f"Сумма: {amt_str} {d.get('currency','')}",item_link=item_link_log)
            if s and s in db["users"]:
                ref_uid = db["users"][s].get("ref_by")
                if ref_uid and ref_uid in db["users"] and amt_num > 0:
                    bonus = int(amt_num*0.03)
                    if bonus > 0:
                        db["users"][ref_uid]["ref_earned"] = db["users"][ref_uid].get("ref_earned",0)+bonus
                        db["users"][ref_uid]["balance"] = db["users"][ref_uid].get("balance",0)+bonus
                        add_log(db,"💰 Реферальный бонус",uid=ref_uid,username=db["users"][ref_uid].get("username","?"),extra=f"+{bonus} RUB (3% от сделки {deal_id})")
                        try:
                            rl=get_lang(int(ref_uid)); rr=rl=="ru"
                            await context.bot.send_message(chat_id=int(ref_uid),
                                text=f"💰 <b>{lbl(rr,'Реферальный бонус!','Referral bonus!')}</b>\n\n<blockquote><b>+{bonus} RUB (3% {lbl(rr,'от сделки','from deal')} #{deal_id})</b></blockquote>",
                                parse_mode="HTML")
                        except: pass
            save_db(db)
            if db.get("logs"): await send_log_to_channel(context,db,db["logs"][-1],hidden=db.get("log_hidden",False))
            try: await q.edit_message_text(f"✅ <b>Оплата подтверждена!</b>\n<code>{deal_id}</code>\n💰 {d.get('amount')} {d.get('currency')}{item_link_msg}", parse_mode="HTML")
            except Exception as e: logger.error(f"adm_confirm edit: {e}")
            if s:
                try:
                    sl=get_lang(int(s)); rs=sl=="ru"; buyer_tag=d.get("partner","—")
                    await context.bot.send_message(chat_id=int(s),
                        text=f"{E['check']} <b>{lbl(rs,'Оплата подтверждена! Сделка завершена.','Payment confirmed! Deal completed.')}</b>\n<code>{deal_id}</code>{item_link_msg}\n\n{lbl(rs,'Оцените покупателя','Rate the buyer')} {buyer_tag}:",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("⭐️1",callback_data=f"rev_{deal_id}_s_1"),
                            InlineKeyboardButton("⭐️2",callback_data=f"rev_{deal_id}_s_2"),
                            InlineKeyboardButton("⭐️3",callback_data=f"rev_{deal_id}_s_3"),
                            InlineKeyboardButton("⭐️4",callback_data=f"rev_{deal_id}_s_4"),
                            InlineKeyboardButton("⭐️5",callback_data=f"rev_{deal_id}_s_5"),
                        ]]))
                except Exception as e: logger.error(f"adm_confirm notify seller: {e}")
            buyer_uid = d.get("buyer_uid")
            if not buyer_uid:
                for uid_, u_ in db.get("users",{}).items():
                    if u_.get("username","").lower() == d.get("partner","").lstrip("@").lower(): buyer_uid=uid_; break
            if buyer_uid:
                try:
                    bl2=get_lang(int(buyer_uid)); rb=bl2=="ru"
                    seller_tag=f"@{db['users'].get(s,{}).get('username',lbl(rb,'продавец','seller'))}" if s else lbl(rb,"продавца","seller")
                    await context.bot.send_message(chat_id=int(buyer_uid),
                        text=f"{E['check']} <b>{lbl(rb,'Сделка подтверждена!','Deal confirmed!')}</b>\n<code>{deal_id}</code>{item_link_msg}\n\n{lbl(rb,'Оцените продавца','Rate the seller')} {seller_tag}:",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("⭐️1",callback_data=f"rev_{deal_id}_b_1"),
                            InlineKeyboardButton("⭐️2",callback_data=f"rev_{deal_id}_b_2"),
                            InlineKeyboardButton("⭐️3",callback_data=f"rev_{deal_id}_b_3"),
                            InlineKeyboardButton("⭐️4",callback_data=f"rev_{deal_id}_b_4"),
                            InlineKeyboardButton("⭐️5",callback_data=f"rev_{deal_id}_b_5"),
                        ]]))
                except Exception as e: logger.error(f"adm_confirm notify buyer: {e}")
    except Exception as e: logger.error(f"adm_confirm: {e}")

async def adm_decline(update, context):
    try:
        q = update.callback_query; await q.answer()
        if update.effective_user.id != ADMIN_ID: return
        deal_id = q.data[12:]; db = load_db(); d = db.get("deals",{}).get(deal_id,{})
        try:
            await q.edit_message_text(
                f"❌ <b>Не подтверждено.</b>\n📄 <code>{deal_id}</code>\n{CM} {d.get('amount','—')} {d.get('currency','—')}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Всё же пришла", callback_data=f"adm_confirm_{deal_id}")]]))
        except Exception as e: logger.error(f"adm_decline edit: {e}")
    except Exception as e: logger.error(f"adm_decline: {e}")

async def show_balance(update, context):
    try:
        db = load_db(); uid = update.effective_user.id; u = get_user(db, uid)
        lang = get_lang(uid); ru = lang=="ru"; bal = u.get("balance",0)
        await edit_or_send(update,
            f"💸 <b>{lbl(ru,'Пополнить / Вывод','Top Up / Withdraw')}</b>\n\n<blockquote><b>{lbl(ru,'Баланс','Balance')}: {bal} RUB</b></blockquote>",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ " + lbl(ru,"Пополнить","Top Up"), callback_data="balance_topup")],
                [InlineKeyboardButton("➖ " + lbl(ru,"Вывод","Withdraw"), callback_data="withdraw")],
                [InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")],
            ]), section="balance")
    except Exception as e: logger.error(f"show_balance: {e}")

async def show_balance_info(update, context, method):
    try:
        uid = update.effective_user.id; lang = get_lang(uid); ru = lang=="ru"
        within = lbl(ru,"После перевода баланс пополнится в течение 5 минут.","Balance will be topped up within 5 minutes after transfer.")
        # FIX: add "I sent" button on all topup screens
        i_sent_btn = InlineKeyboardButton("✅ " + lbl(ru,"Я отправил","I sent"), callback_data=f"topup_sent_{method}")
        back_btn = InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="balance_topup")
        if method == "stars":
            text = (f"{E['stars_deal']} <b>{lbl(ru,'Пополнение звёздами','Top up with Stars')}</b>\n\n"
                    f"<blockquote><b>{lbl(ru,'Отправьте звёзды менеджеру','Send stars to manager')}: @GiftDealsManager\n\n{within}</b></blockquote>")
        elif method == "rub":
            text = (f"{E['requisites']} <b>{lbl(ru,'Пополнение рублями','Top up in Rubles')}</b>\n\n"
                    f"<blockquote><b>{lbl(ru,'Банк','Bank')}: {CARD_BANK}\n{lbl(ru,'Телефон','Phone')}: <code>{CARD_NUMBER}</code>\n"
                    f"{lbl(ru,'Получатель','Recipient')}: {CARD_NAME}\n\n{within}</b></blockquote>")
        elif method == "crypto":
            text = (f"{E['tonkeeper']} <b>{lbl(ru,'Пополнение TON / USDT','Top up TON / USDT')}</b>\n\n"
                    f"<blockquote><b>{lbl(ru,'TON адрес','TON address')}:\n<code>{CRYPTO_ADDRESS}</code>\n\n"
                    f"{E['cryptobot']} {lbl(ru,'Крипто бот','Crypto bot')}: {CRYPTO_BOT}\n\nID: <code>{uid}</code>\n\n{within}</b></blockquote>")
        else:
            text = "<b>?</b>"
        await edit_or_send(update, text, InlineKeyboardMarkup([[i_sent_btn],[back_btn]]), section="balance")
    except Exception as e: logger.error(f"show_balance_info: {e}")

async def show_lang(update, context):
    try:
        uid = update.effective_user.id; lang = get_lang(uid); ru = lang=="ru"
        rows = [[InlineKeyboardButton(name, callback_data=f"lang_{code}")] for code, name in LANGS.items()]
        rows.append([InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")])
        await edit_or_send(update,
            f"<tg-emoji emoji-id='5447410659077661506'>🌐</tg-emoji> <b>{lbl(ru,'Выберите язык:','Select language:')}</b>",
            InlineKeyboardMarkup(rows), section="main")
    except Exception as e: logger.error(f"show_lang: {e}")

async def set_lang(update, context, lang):
    try:
        db = load_db(); u = get_user(db, update.effective_user.id); u["lang"] = lang; save_db(db)
        await update.callback_query.answer("✅")
        try: await update.callback_query.message.delete()
        except: pass
        await show_main(update, context, edit=False)
    except Exception as e: logger.error(f"set_lang: {e}")

async def show_profile(update, context):
    try:
        db = load_db(); uid = update.effective_user.id; u = get_user(db, uid)
        lang = get_lang(uid); ru = lang=="ru"
        uname = update.effective_user.username or "—"
        status = u.get("status","")
        sl = f"\n<blockquote><b>{lbl(ru,'Статус','Status')}: {status}</b></blockquote>" if status else ""
        # FIX: reviews with premium stars in blockquote, numbered
        reviews = u.get("reviews",[])
        if reviews:
            rev_lines = "\n".join(f"{i+1}. {r}" for i,r in enumerate(reviews[-10:]))
            rv = f"\n\n<b>{lbl(ru,'Отзывы','Reviews')}:</b>\n<blockquote>{rev_lines}</blockquote>"
        else:
            rv = ""
        text = (f"<tg-emoji emoji-id='5275979556308674886'>👤</tg-emoji> <b>{lbl(ru,'Профиль','Profile')}{sl}\n\n@{uname}\n"
                f"{E['balance_e']} {lbl(ru,'Баланс','Balance')}: {u.get('balance',0)} RUB\n"
                f"<tg-emoji emoji-id='5028746137645876535'>📊</tg-emoji> {lbl(ru,'Сделок','Deals')}: {u.get('total_deals',0)}\n"
                f"<tg-emoji emoji-id='5206607081334906820'>✅</tg-emoji> {lbl(ru,'Успешных','Successful')}: {u.get('success_deals',0)}\n"
                f"<tg-emoji emoji-id='5902056028513505203'>💵</tg-emoji> {lbl(ru,'Оборот','Turnover')}: {u.get('turnover',0)} RUB\n"
                f"🏆 {lbl(ru,'Репутация','Reputation')}: {u.get('reputation',0)}</b>{rv}")
        await edit_or_send(update, text, InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ " + lbl(ru,"Пополнить","Top Up"), callback_data="menu_balance"),
             InlineKeyboardButton("➖ " + lbl(ru,"Вывод","Withdraw"), callback_data="withdraw")],
            [InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")]
        ]), section="profile")
    except Exception as e: logger.error(f"show_profile: {e}")

async def show_ref(update, context):
    try:
        db = load_db(); uid = update.effective_user.id; u = get_user(db, uid); save_db(db)
        db = load_db(); u = db["users"][str(uid)]; lang = get_lang(uid); ru = lang=="ru"
        ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"
        ref_count = u.get("ref_count",0); ref_earned = u.get("ref_earned",0)
        refs = [v.get("username","?") for v in db.get("users",{}).values() if v.get("ref_by")==str(uid)]
        refs_str = ""
        if refs:
            refs_str = "\n\n" + lbl(ru,"Рефералы","Referrals") + ":\n" + "\n".join(f"• @{r}" if r and r!="?" else "• #?" for r in refs[-10:])
        text = (
            f"{ce('6001526766714227911','👥')} <b>{lbl(ru,'Реферальная программа','Referral Program')}</b>\n\n"
            f"<blockquote>{lbl(ru,'Приглашайте друзей и получайте 3% с каждой их сделки!','Invite friends and earn 3% from each their deal!')}\n\n"
            f"{lbl(ru,'Приглашено','Invited')}: <b>{ref_count}</b>\n"
            f"{lbl(ru,'Заработано','Earned')}: <b>{ref_earned} RUB</b>{refs_str}</blockquote>\n\n"
            f"{lbl(ru,'Ваша реферальная ссылка (нажмите чтобы скопировать):','Your referral link (tap to copy):')}\n<code>{ref_link}</code>"
        )
        await edit_or_send(update, text, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")]]), section="profile")
    except Exception as e: logger.error(f"show_ref: {e}")

async def show_req(update, context):
    try:
        db = load_db(); uid = update.effective_user.id; u = get_user(db, uid)
        lang = get_lang(uid); ru = lang=="ru"
        reqs = u.get("requisites",{})
        card = reqs.get("card"); ton = reqs.get("ton"); stars = reqs.get("stars")
        e_check = ce("5206607081334906820","✅"); e_add = ce("5274055917766202507","➕")
        # FIX: show values in blockquote
        card_val = f"<blockquote><code>{card}</code></blockquote>" if card else f"<blockquote>{e_add} <b>{lbl(ru,'Не добавлена','Not added')}</b></blockquote>"
        ton_val  = f"<blockquote><code>{ton}</code></blockquote>"  if ton  else f"<blockquote>{e_add} <b>{lbl(ru,'Не добавлен','Not added')}</b></blockquote>"
        star_val = f"<blockquote><code>{stars}</code></blockquote>" if stars else f"<blockquote>{e_add} <b>{lbl(ru,'Не добавлен','Not added')}</b></blockquote>"
        text = (
            f"📋 <b>{lbl(ru,'Мои реквизиты','My Requisites')}</b>\n\n"
            f"💳 <b>{lbl(ru,'Карта / СБП','Card / SBP')}:</b>\n{card_val}\n"
            f"💎 <b>TON / USDT:</b>\n{ton_val}\n"
            f"{E['star_prem']} <b>{lbl(ru,'Звёзды (@username)','Stars (@username)')}:</b>\n{star_val}"
        )
        rows = []
        if card:
            rows.append([InlineKeyboardButton("💳 " + lbl(ru,"Изменить карту","Edit card"), callback_data="req_edit_card")])
        else:
            rows.append([InlineKeyboardButton("💳 " + lbl(ru,"Добавить карту","Add card"), callback_data="req_edit_card")])
        if ton:
            rows.append([InlineKeyboardButton("💎 " + lbl(ru,"Изменить TON","Edit TON"), callback_data="req_edit_ton")])
        else:
            rows.append([InlineKeyboardButton("💎 " + lbl(ru,"Добавить TON кошелёк","Add TON wallet"), callback_data="req_edit_ton")])
        if stars:
            rows.append([InlineKeyboardButton(f"{E['star_prem']} " + lbl(ru,"Изменить @username","Edit @username"), callback_data="req_edit_stars")])
        else:
            rows.append([InlineKeyboardButton(f"{E['star_prem']} " + lbl(ru,"Добавить @username для звёзд","Add Stars @username"), callback_data="req_edit_stars")])
        # FIX: delete button separate row, then 3 buttons which to delete
        if card or ton or stars:
            rows.append([InlineKeyboardButton("🗑 " + lbl(ru,"Удалить реквизит","Delete requisite"), callback_data="req_del_menu")])
        rows.append([InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")])
        await edit_or_send(update, text, InlineKeyboardMarkup(rows), section="profile")
    except Exception as e: logger.error(f"show_req: {e}")

async def show_my_deals(update, context):
    try:
        db = load_db(); uid = str(update.effective_user.id)
        lang = get_lang(int(uid)); ru = lang=="ru"
        deals = {k:v for k,v in db.get("deals",{}).items() if v.get("user_id")==uid}
        if not deals:
            await edit_or_send(update,
                f"💼 <b>{lbl(ru,'Мои сделки','My Deals')}\n\n{lbl(ru,'У вас пока нет сделок.','You have no deals yet.')}</b>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")]]),
                section="my_deals"); return
        SNAMES = {"pending": lbl(ru,"⏳ Ожидает","⏳ Pending"), "confirmed": lbl(ru,"✅ Завершена","✅ Completed")}
        lines = [f"<tg-emoji emoji-id='5445221832074483553'>💼</tg-emoji> <b>{lbl(ru,'Мои сделки','My Deals')} ({len(deals)}):</b>\n"]
        for i,(did,dv) in enumerate(list(deals.items())[-10:],start=1):
            tn = tname(dv.get("type",""),lang); s = SNAMES.get(dv.get("status",""),dv.get("status",""))
            lines.append(f"<b>{i}. {did}</b> | {tn} | {dv.get('amount')} {cur_native(dv.get('currency',''))} | {s}")
        await edit_or_send(update, "\n".join(lines),
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")]]),
            section="my_deals")
    except Exception as e: logger.error(f"show_my_deals: {e}")

async def show_top(update, context):
    # FIX: renamed to Top Deals, show recent confirmed deals
    try:
        db = load_db(); lang = get_lang(update.effective_user.id); ru = lang=="ru"
        deals = db.get("deals",{})
        confirmed = [(k,v) for k,v in deals.items() if v.get("status")=="confirmed"]
        confirmed.sort(key=lambda x: x[1].get("created",""), reverse=True)
        lines = [f"{E['top_medal']} <b>{lbl(ru,'Топ сделок Gift Deals','Gift Deals Top Deals')}</b>\n"]
        medals = ["🥇","🥈","🥉"]+["🏅"]*17
        if confirmed:
            for i,(did,dv) in enumerate(confirmed[:10]):
                seller_uid = dv.get("user_id")
                seller_uname = db["users"].get(seller_uid,{}).get("username","?") if seller_uid else "?"
                seller_mask = f"@{seller_uname[:2]}***{seller_uname[-2:]}" if len(seller_uname)>4 else f"@{seller_uname}"
                amt = dv.get("amount","?"); cur = cur_native(dv.get("currency",""))
                tn = tname(dv.get("type",""),lang)
                lines.append(f"<b>{medals[i]} {i+1}. {seller_mask} — {amt} {cur} | {tn}</b>")
        else:
            lines.append(f"<b>{lbl(ru,'Пока нет завершённых сделок.','No completed deals yet.')}</b>")
        lines.append(f"\n{E['stats']} <b>{lbl(ru,'1000+ сделок в боте','1000+ deals on platform')}</b>")
        await edit_or_send(update, "\n".join(lines),
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="main_menu")]]),
            section="top")
    except Exception as e: logger.error(f"show_top: {e}")

async def show_withdraw(update, context):
    try:
        db = load_db(); uid = update.effective_user.id; u = get_user(db, uid)
        lang = get_lang(uid); ru = lang=="ru"; bal = u.get("balance",0)
        if bal <= 0:
            await edit_or_send(update,
                f"{E['cross']} <b>{lbl(ru,'Недостаточно средств для вывода.','Insufficient balance.')}</b>\n\n<blockquote><b>{lbl(ru,'Ваш баланс','Your balance')}: {bal} RUB</b></blockquote>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="menu_balance")]]),
                section="balance"); return
        reqs = u.get("requisites",{})
        rows = []
        if reqs.get("ton"): rows.append([InlineKeyboardButton("💎 TON/USDT → " + reqs["ton"][:12]+"...", callback_data="withdraw_crypto")])
        else: rows.append([InlineKeyboardButton("💎 " + lbl(ru,"Крипта (TON/USDT)","Crypto (TON/USDT)"), callback_data="withdraw_crypto")])
        if reqs.get("stars"): rows.append([InlineKeyboardButton("⭐️ " + lbl(ru,"Звёзды → ","Stars → ")+reqs["stars"], callback_data="withdraw_stars")])
        else: rows.append([InlineKeyboardButton("⭐️ " + lbl(ru,"Звёзды","Stars"), callback_data="withdraw_stars")])
        if reqs.get("card"): rows.append([InlineKeyboardButton("💳 " + lbl(ru,"Карта → ","Card → ")+reqs["card"][:10]+"...", callback_data="withdraw_card")])
        else: rows.append([InlineKeyboardButton("💳 " + lbl(ru,"На карту","Card"), callback_data="withdraw_card")])
        rows.append([InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="menu_balance")])
        await edit_or_send(update,
            f"{E['wallet']} <b>{lbl(ru,'Вывод средств','Withdraw')}</b>\n\n<blockquote><b>{lbl(ru,'Ваш баланс','Your balance')}: {bal} RUB\n\n{lbl(ru,'Выберите способ вывода:','Choose withdrawal method:')}</b></blockquote>",
            InlineKeyboardMarkup(rows), section="balance")
    except Exception as e: logger.error(f"show_withdraw: {e}")

def adm_kb():
    db = load_db()
    hidden = db.get("log_hidden",False)
    toggle_label = "👁 Логи: данные открыты" if not hidden else "🙈 Логи: данные скрыты"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Управление пользователем", callback_data="adm_user")],
        [InlineKeyboardButton("🖼 Баннеры по разделам", callback_data="adm_banners")],
        [InlineKeyboardButton("✏️ Описание меню", callback_data="adm_menu_desc")],
        [InlineKeyboardButton("🗂 Список сделок", callback_data="adm_deals")],
        [InlineKeyboardButton("📋 Логи событий", callback_data="adm_logs"),
         InlineKeyboardButton(toggle_label, callback_data="adm_toggle_hidden")],
        [InlineKeyboardButton("📡 Настройка лог-канала", callback_data="adm_log_channel")],
    ])

def adm_banners_kb(db=None):
    if db is None: db = load_db()
    banners = db.get("banners",{})
    rows = []
    for key, name in BANNER_SECTIONS.items():
        b = banners.get(key) or {}
        has = bool(b.get("photo") or b.get("video") or b.get("gif") or b.get("text"))
        if not has and key=="main":
            has = bool(db.get("banner_photo") or db.get("banner_video") or db.get("banner_gif") or db.get("banner"))
        status = "✅" if has else "➕"
        rows.append([
            InlineKeyboardButton(f"{status} {name}", callback_data=f"adm_banner_{key}"),
            InlineKeyboardButton("🗑", callback_data=f"adm_banner_del_{key}") if has else InlineKeyboardButton("   ", callback_data="noop"),
        ])
    rows.append([InlineKeyboardButton("🔙 Назад", callback_data="adm_back")])
    return InlineKeyboardMarkup(rows)

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    context.user_data.clear(); context.user_data["adm"] = True
    await update.message.reply_text("⚙️ <b>Панель администратора</b>", parse_mode="HTML", reply_markup=adm_kb())

async def handle_adm_cb(update, context):
    try:
        q = update.callback_query; d = q.data; ud = context.user_data
        if update.effective_user.id != ADMIN_ID: return

        if d == "adm_user":
            ud["adm_step"] = "get_user"
            await q.message.edit_text("<b>Введите @юзернейм или числовой ID пользователя:</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="adm_back")]])); return

        if d == "adm_banners":
            db = load_db()
            await q.message.edit_text("<b>🖼 Баннеры по разделам</b>\n\n<blockquote>✅ — установлен  |  ➕ — нет  |  🗑 — удалить\n\nКаждый раздел независим.</blockquote>",
                parse_mode="HTML", reply_markup=adm_banners_kb(db)); return

        if d.startswith("adm_banner_del_"):
            section = d[15:]
            if section in BANNER_SECTIONS:
                db = load_db()
                if not db.get("banners"): db["banners"] = {}
                db["banners"][section] = {}
                if section == "main": db["banner"] = db["banner_photo"] = db["banner_video"] = db["banner_gif"] = None
                save_db(db); await q.answer("Баннер удалён")
                await q.message.edit_text("<b>🖼 Banners by section</b>\n\n<blockquote>✅ — set  |  ➕ — not set  |  🗑 — delete</blockquote>",
                    parse_mode="HTML", reply_markup=adm_banners_kb(load_db())); return

        if d.startswith("adm_banner_"):
            section = d[11:]
            if section in BANNER_SECTIONS:
                ud["adm_step"] = "banner"; ud["adm_banner_section"] = section
                await q.message.edit_text(
                    f"<b>Баннер для раздела «{BANNER_SECTIONS[section]}»\n\nОтправьте фото, видео, GIF или текст.\noff — удалить баннер.</b>",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Отмена", callback_data="adm_banners")]])); return

        if d == "adm_log_channel":
            db = load_db(); chat_id = db.get("log_chat_id","not set"); log_hidden = db.get("log_hidden",False)
            mask_status = "🙈 Скрыто (маска)" if log_hidden else "👁 Видно (реальные)"
            await q.message.edit_text(
                f"<b>📡 Настройки лог-канала</b>\n\n<blockquote>Текущий chat ID: <code>{chat_id}</code>\nОтображение данных: {mask_status}</blockquote>\n\nДля изменения chat ID — отправьте новый chat_id следующим сообщением.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👁 Показать реальные" if log_hidden else "🙈 Скрыть данные", callback_data="adm_log_toggle_mask")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="adm_back")]
                ]))
            ud["adm_step"] = "set_log_chat"; return

        if d == "adm_log_toggle_mask":
            db = load_db(); db["log_hidden"] = not db.get("log_hidden",False); save_db(db)
            log_hidden = db["log_hidden"]; chat_id = db.get("log_chat_id","not set")
            mask_status = "🙈 Скрыто (маска)" if log_hidden else "👁 Видно (реальные)"
            await q.message.edit_text(
                f"<b>📡 Настройки лог-канала</b>\n\n<blockquote>Текущий chat ID: <code>{chat_id}</code>\nОтображение данных: {mask_status}</blockquote>\n\nДля изменения chat ID — отправьте новый chat_id следующим сообщением.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👁 Показать реальные" if log_hidden else "🙈 Скрыть данные", callback_data="adm_log_toggle_mask")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="adm_back")]
                ]))
            await q.answer("✅ Обновлено"); return

        if d == "adm_toggle_hidden":
            db = load_db(); db["log_hidden"] = not db.get("log_hidden",False); save_db(db)
            hidden = db["log_hidden"]; await q.answer("🙈 Данные скрыты" if hidden else "👁 Данные открыты")
            try: await q.message.edit_text("⚙️ <b>Панель администратора</b>", parse_mode="HTML", reply_markup=adm_kb())
            except: pass; return

        if d in ("adm_logs","adm_logs_hidden","adm_logs_toggle"):
            db = load_db()
            if d == "adm_logs_toggle": db["log_hidden"] = not db.get("log_hidden",False); save_db(db)
            hidden = db.get("log_hidden",False); logs = db.get("logs",[])[-20:][::-1]
            if not logs:
                await q.message.edit_text("<b>Логов пока нет.</b>", parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="adm_back")]])); return
            status_icon = "🙈" if hidden else "👁"; status_text = "Данные скрыты" if hidden else "Данные открыты"
            lines = [f"<b>📋 Последние события</b> | {status_icon} {status_text}:\n"]
            for log in logs:
                if hidden:
                    uname = mask(f"@{log['username']}") if log.get('username') else ""
                    uid_str = mask(log['uid']) if log.get('uid') else ""
                    deal = f" #***{log['deal_id'][-3:]}" if log.get('deal_id') else ""
                else:
                    uname = f"@{log['username']}" if log.get('username') else ""
                    uid_str = f"<code>{log['uid']}</code>" if log.get('uid') else ""
                    deal = f" #{log['deal_id']}" if log.get('deal_id') else ""
                extra = f" — {log['extra']}" if log.get('extra') else ""
                lines.append(f"<b>{log['time']}</b> {log['event']}{deal}\n{uname} {uid_str}{extra}\n")
            txt = "\n".join(lines)[:4000]
            toggle_label = "👁 Показать всё" if hidden else "🙈 Скрыть данные"
            await q.message.edit_text(txt, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(toggle_label, callback_data="adm_logs_toggle")],
                [InlineKeyboardButton("🔄 Обновить", callback_data="adm_logs")],
                [InlineKeyboardButton("🔙 Назад", callback_data="adm_back")]
            ])); return

        if d == "adm_menu_desc":
            ud["adm_step"] = "menu_desc"
            await q.message.edit_text("<b>Введите новое описание меню:</b>", parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Отмена", callback_data="adm_back")]])); return

        if d == "adm_deals":
            db = load_db(); deals = db.get("deals",{})
            if not deals:
                await q.message.edit_text("<b>Сделок нет.</b>", parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="adm_back")]])); return
            text = "<b>📋 Последние 10 сделок:</b>\n"
            for did,dv in list(deals.items())[-10:]:
                text += f"\n<b>{did}</b> | {tname(dv.get('type',''))} | {dv.get('amount')} {dv.get('currency')} | {dv.get('status')}"
            await q.message.edit_text(text, parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="adm_back")]])); return

        action_map = {
            "adm_add_review":  ("review","Введите текст отзыва:"),
            "adm_set_deals":   ("total_deals","Введите количество сделок:"),
            "adm_set_success": ("success_deals","Введите количество успешных сделок:"),
            "adm_set_turnover":("turnover","Введите оборот:"),
            "adm_set_rep":     ("reputation","Введите репутацию:"),
            "adm_set_status":  ("status","Введите статус:"),
        }
        if d in action_map:
            field, prompt = action_map[d]; ud["adm_field"] = field; ud["adm_step"] = "set_value"
            await q.message.edit_text(f"<b>{prompt}</b>", parse_mode="HTML"); return

        # FIX: Admin review management
        if d == "adm_reviews":
            target = ud.get("adm_target")
            if not target: return
            db = load_db(); u2 = db["users"].get(target,{}); uname2 = u2.get("username","?")
            revs = u2.get("reviews",[])
            if not revs:
                await q.message.edit_text(f"<b>@{uname2}: отзывов нет</b>", parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="adm_back")]])); return
            lines = [f"<b>📋 Отзывы @{uname2} ({len(revs)}):</b>"]
            rows = []
            for i,r in enumerate(revs):
                lines.append(f"\n{i+1}. {r}")
                rows.append([InlineKeyboardButton(f"🗑 Удалить #{i+1}", callback_data=f"adm_del_rev_{target}_{i}")])
            rows.append([InlineKeyboardButton("🔙 Назад", callback_data="adm_back")])
            await q.message.edit_text("\n".join(lines), parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows)); return

        status_map = {
            "adm_status_verified": "✅ Проверенный", "adm_status_garant": "🛡 Гарант",
            "adm_status_caution": "⚠️ Осторожно", "adm_status_scammer": "🚫 Мошенник",
            "adm_status_clear": "",
        }
        if d in status_map:
            target = ud.get("adm_target")
            if target:
                db = load_db(); u2 = db["users"].get(target,{})
                u2["status"] = status_map[d]; db["users"][target] = u2; save_db(db)
                await q.answer(f"Статус: {status_map[d] or 'убран'}")
                try: await q.edit_message_reply_markup(reply_markup=None)
                except: pass
    except Exception as e: logger.error(f"handle_adm_cb: {e}")

async def handle_adm_msg(update, context):
    try:
        ud = context.user_data; step = ud.get("adm_step")
        if not step: return
        text = update.message.text.strip() if update.message and update.message.text else ""
        db = load_db(); ok_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛠 Панель", callback_data="adm_back")]])

        if step == "set_log_chat":
            cleaned = text.strip()
            if not (cleaned.lstrip("-").isdigit()):
                await update.message.reply_text("<b>Неверный chat ID. Должен быть числом, например -1001234567890</b>", parse_mode="HTML"); return
            db["log_chat_id"] = cleaned; save_db(db)
            await update.message.reply_text(f"{E['check']} <b>Лог-канал установлен!</b>\n\nChat ID: <code>{cleaned}</code>", parse_mode="HTML", reply_markup=ok_kb)
            ud["adm_step"] = None; return

        if step == "get_user":
            uname = text.lstrip("@").lower()
            found = next((k for k,v in db["users"].items() if v.get("username","").lower()==uname), None)
            if not found and text.lstrip("@").isdigit():
                candidate = text.lstrip("@")
                found = candidate if candidate in db["users"] else None
            if not found:
                similar = [v.get("username","") for v in db["users"].values() if len(uname)>=3 and uname[:3] in v.get("username","").lower() and v.get("username","")]
                hint = f"\n\nПохожие: {', '.join('@'+s for s in similar[:5])}" if similar else f"\n\nВсего пользователей в БД: {len(db['users'])}"
                await update.message.reply_text(f"<b>Не найдено: @{uname}{hint}\n\nВведите @юзернейм или числовой ID:</b>", parse_mode="HTML"); return
            ud["adm_target"] = found; u2 = db["users"][found]
            await update.message.reply_text(
                f"<b>@{u2.get('username','—')} (ID: <code>{found}</code>)\nСделок: {u2.get('total_deals',0)} | Реп: {u2.get('reputation',0)}\nСтатус: {u2.get('status','—')}</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📝 Отзыв", callback_data="adm_add_review"),
                     InlineKeyboardButton("🗑 Отзывы", callback_data="adm_reviews")],
                    [InlineKeyboardButton("🔢 Сделок", callback_data="adm_set_deals"),
                     InlineKeyboardButton("✅ Успешных", callback_data="adm_set_success")],
                    [InlineKeyboardButton("💵 Оборот", callback_data="adm_set_turnover"),
                     InlineKeyboardButton("⭐️ Репут.", callback_data="adm_set_rep")],
                    [InlineKeyboardButton("🏷 Свой статус", callback_data="adm_set_status")],
                    [InlineKeyboardButton("✅ Проверенный", callback_data="adm_status_verified"),
                     InlineKeyboardButton("🛡 Гарант", callback_data="adm_status_garant")],
                    [InlineKeyboardButton("⚠️ Осторожно", callback_data="adm_status_caution"),
                     InlineKeyboardButton("🚫 Мошенник", callback_data="adm_status_scammer")],
                    [InlineKeyboardButton("❌ Убрать статус", callback_data="adm_status_clear")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="adm_back")]
                ]))
            ud["adm_step"] = None; return

        if step == "banner":
            section = ud.get("adm_banner_section","main")
            if not db.get("banners"): db["banners"] = {}
            caption = update.message.caption or "" if update.message else ""
            if update.message and update.message.photo:
                db["banners"][section] = {"photo":update.message.photo[-1].file_id,"video":None,"gif":None,"text":caption}; save_db(db)
            elif update.message and update.message.animation:
                db["banners"][section] = {"photo":None,"video":None,"gif":update.message.animation.file_id,"text":caption}; save_db(db)
            elif update.message and update.message.video:
                db["banners"][section] = {"photo":None,"video":update.message.video.file_id,"gif":None,"text":caption}; save_db(db)
            elif text.lower() == "off":
                db["banners"][section] = {}
                if section=="main": db["banner"] = db["banner_photo"] = db["banner_video"] = db["banner_gif"] = None
                save_db(db)
            else:
                db["banners"][section] = {"photo":None,"video":None,"gif":None,"text":text}; save_db(db)
            ud["adm_step"] = None; ud.pop("adm_banner_section",None)
            await update.message.reply_text(
                f"{E['check']} <b>Баннер раздела «{BANNER_SECTIONS.get(section,section)}» обновлён!</b>\n\n"
                "<b>🖼 Баннеры по разделам:</b>\n<blockquote>✅ — установлен  |  ➕ — нет  |  🗑 — удалить</blockquote>",
                parse_mode="HTML", reply_markup=adm_banners_kb(load_db())); return

        if step == "menu_desc":
            db["menu_description"] = text; save_db(db)
            await update.message.reply_text(f"{E['check']} <b>Описание обновлено!</b>", parse_mode="HTML", reply_markup=ok_kb)
            ud["adm_step"] = None; return

        if step == "set_value":
            field = ud.get("adm_field"); target = ud.get("adm_target")
            if not field or not target: return
            u2 = db["users"].get(target,{})
            if field == "review": u2.setdefault("reviews",[]).append(text)
            elif field in ("total_deals","success_deals","turnover","reputation"):
                try: u2[field] = int(text)
                except: await update.message.reply_text("<b>Введите число!</b>", parse_mode="HTML"); return
            else: u2[field] = text
            db["users"][target] = u2; save_db(db)
            await update.message.reply_text(f"{E['check']} <b>Обновлено!</b>", parse_mode="HTML", reply_markup=ok_kb)
            ud["adm_step"] = None; return

    except Exception as e: logger.error(f"handle_adm_msg: {e}")

# Handle req_del_menu callback (show 3 delete buttons)
async def handle_req_del_menu(update, context):
    uid = update.effective_user.id; lang = get_lang(uid); ru = lang=="ru"
    db = load_db(); u = get_user(db, uid); reqs = u.get("requisites",{})
    rows = []
    if reqs.get("card"): rows.append([InlineKeyboardButton("💳 " + lbl(ru,"Удалить карту","Delete card"), callback_data="req_del_card")])
    if reqs.get("ton"):  rows.append([InlineKeyboardButton("💎 " + lbl(ru,"Удалить TON кошелёк","Delete TON wallet"), callback_data="req_del_ton")])
    if reqs.get("stars"): rows.append([InlineKeyboardButton("⭐️ " + lbl(ru,"Удалить @username звёзд","Delete Stars @username"), callback_data="req_del_stars")])
    rows.append([InlineKeyboardButton("🔙 " + lbl(ru,"Назад","Back"), callback_data="menu_req")])
    await edit_or_send(update, f"🗑 <b>{lbl(ru,'Выберите что удалить:','Choose what to delete:')}</b>",
        InlineKeyboardMarkup(rows), section="profile")

async def cmd_neptune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "<b>🔑 Secret commands:\n\n🔹 /set_my_deals [number]\n   Example: /set_my_deals 150\n\n🔹 /set_my_amount [amount]\n   Example: /set_my_amount 50000</b>",
            parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_neptune: {e}")

async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID: return
        args = context.args
        if not args: await update.message.reply_text("<b>Example: /buy GD00001</b>", parse_mode="HTML"); return
        deal_id = args[0].upper(); db = load_db()
        if deal_id not in db.get("deals",{}): await update.message.reply_text("<b>Not found.</b>", parse_mode="HTML"); return
        db["deals"][deal_id]["status"] = "confirmed"
        s = db["deals"][deal_id].get("user_id")
        if s and s in db["users"]:
            db["users"][s]["success_deals"] = db["users"][s].get("success_deals",0)+1
            db["users"][s]["total_deals"] = db["users"][s].get("total_deals",0)+1
        save_db(db)
        await update.message.reply_text(f"{E['check']} <b>Deal {deal_id} confirmed!</b>", parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_buy: {e}")

async def cmd_set_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args or not args[0].isdigit(): await update.message.reply_text("<b>Example: /set_my_deals 100</b>", parse_mode="HTML"); return
        db = load_db(); u = get_user(db, str(update.effective_user.id))
        u["success_deals"] = u["total_deals"] = int(args[0]); save_db(db)
        await update.message.reply_text(f"{E['check']} <b>Обновлено!</b>", parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_set_deals: {e}")

async def cmd_set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args: await update.message.reply_text("<b>Example: /set_my_amount 15000</b>", parse_mode="HTML"); return
        try: amt = int(args[0])
        except: await update.message.reply_text("<b>Введите число!</b>", parse_mode="HTML"); return
        db = load_db(); u = get_user(db, str(update.effective_user.id))
        u["turnover"] = amt; save_db(db)
        await update.message.reply_text(f"{E['check']} <b>Turnover: {amt} RUB</b>", parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_set_amount: {e}")

async def on_cb_extended(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Extended callback to handle req_del_menu before main on_cb."""
    try:
        q = update.callback_query
        if q.data == "req_del_menu":
            await q.answer()
            await handle_req_del_menu(update, context)
            return
    except Exception as e: logger.error(f"on_cb_extended: {e}")
    await on_cb(update, context)

def main():
    db = load_db()
    if not db.get("banners"): db["banners"] = {}
    lp = db.get("banner_photo"); lv = db.get("banner_video"); lg = db.get("banner_gif"); lt = db.get("banner") or ""
    if (lp or lv or lg or lt) and not db["banners"].get("main"):
        db["banners"]["main"] = {"photo":lp,"video":lv,"gif":lg,"text":lt}
        db["banner_photo"] = db["banner_video"] = db["banner_gif"] = db["banner"] = None
        save_db(db); logger.info("Banner migrated to banners['main']")

    app = Application.builder().token(BOT_TOKEN).build()

    async def post_init(application):
        await application.bot.set_my_commands([BotCommand("start","🏠 Main menu")])
    app.post_init = post_init

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CommandHandler("neptunteam", cmd_neptune))
    app.add_handler(CommandHandler("buy", cmd_buy))
    app.add_handler(CommandHandler("set_my_deals", cmd_set_deals))
    app.add_handler(CommandHandler("set_my_amount", cmd_set_amount))
    app.add_handler(CallbackQueryHandler(on_cb_extended))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_msg))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION, handle_adm_msg))

    print(f"Bot @{BOT_USERNAME} started!")
    app.run_polling()

if __name__ == "__main__":
    main()
