import logging, json, os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN    = "8767675859:AAEYrMnVMAZjI7rBEc1QLNpHs7rVlUIv-0Q"
ADMIN_ID     = 8726084830
ADMIN_IDS    = {8726084830, 90283607}
BOT_USERNAME = "GiftDeals_Robot"
MANAGER_URL  = "https://t.me/GiftDealsManager"
MANAGER_TAG  = "@GiftDealsManager"
CRYPTO_ADDR  = "UQDGN5pfjPxorFyjN2xha84bapuADDtPcRofNDJ4dK2YXxZd"
CRYPTO_BOT   = "https://t.me/send?start=IVbfPL7Tk4XA"
CARD_NUM     = "+79041751408"
CARD_NAME    = "Александр Ф."
CARD_BANK_RU = "ВТБ"
CARD_BANK_EN = "VTB"
DB_FILE      = "db.json"

def ce(eid, fb): return f"<tg-emoji emoji-id='{eid}'>{fb}</tg-emoji>"

E = {
    "user":       ce("5199552030615558774", "👤"),
    "star":       ce("5267500801240092311", "⭐"),
    "shield":     ce("5197434882321567830", "🛡"),
    "gift":       ce("5197369495739455200", "🎁"),
    "lock":       ce("5197161121106123533", "🔒"),
    "globe":      ce("5377746319601324795", "🌍"),
    "premium":    ce("5370784581341422520", "⭐"),
    "pencil":     ce("5197371802136892976", "✏️"),
    "card":       ce("5445353829304387411", "💳"),
    "cross":      ce("5443127283898405358", "📥"),
    "rocket":     ce("5444856076954520455", "🚀"),
    "sticker":    ce("5294167145079395967", "🛍"),
    "fire":       ce("5303138782004924588", "🔥"),
    "bell":       ce("5312361253610475399", "🔔"),
    "deal":       ce("5445221832074483553", "💼"),
    "trophy":     ce("5332455502917949981", "🏆"),
    "check":      ce("5274055917766202507", "✅"),
    "money":      ce("5278467510604160626", "💰"),
    "diamond":    ce("5264713049637409446", "💎"),
    "nft":        ce("5193177581888755275", "🖼"),
    "bag":        ce("5377660214096974712", "🛍"),
    "medal":      ce("5463289097336405244", "🥇"),
    "gem":        ce("5258203794772085854", "💎"),
    "clock":      ce("5429651785352501917", "⏰"),
    "handshake":  ce("5287231198098117669", "🤝"),
    "crystal":    ce("5195033767969839232", "🔮"),
    "safe":       ce("5262517101578443800", "🔐"),
    "chart":      ce("5382194935057372936", "📊"),
    "spark":      ce("5902449142575141204", "✨"),
    "target":     ce("5893081007153746175", "❌"),
    "pin":        ce("5893297890117292323", "📞"),
    "wallet":     ce("5893382531037794941", "👛"),
    "num1":       ce("5794164805065514131", "1️⃣"),
    "num2":       ce("5794085322400733645", "2️⃣"),
    "num3":       ce("5794280000383358988", "3️⃣"),
    "num4":       ce("5794241397217304511", "4️⃣"),
    "bank":       ce("5238132025323444613", "🏦"),
    "banknote":   ce("5201873447554145566", "💵"),
    "link":       ce("5902449142575141204", "🔗"),
    "shine":      ce("5235630047959727475", "✨"),
    "store":      ce("4988289890769699938", "🏪"),
    "tonkeeper":  ce("5397829221605191505", "💎"),
    "top_medal":  ce("5188344996356448758", "🏆"),
    "stars_deal": ce("5321485469249198987", "⭐"),
    "joined":     ce("5902335789798265487", "🤝"),
    "security_e": ce("5197288647275071607", "🔰"),
    "deal_link":  ce("5972261808747057065", "🔗"),
    "warning":    ce("5447644880824181073", "⚠️"),
    "stats":      ce("5028746137645876535", "📊"),
    "requisites": ce("5242631901214171852", "📋"),
    "cryptobot":  ce("5242606681166220600", "🤖"),
    "welcome":    ce("5251340119205501791", "👋"),
    "balance_e":  ce("5424976816530014958", "💰"),
}

CD  = ce("5264713049637409446", "💎")
CM  = ce("5278467510604160626", "💰")
CDL = ce("5445221832074483553", "💼")
CSH = ce("5197434882321567830", "🛡")
CL  = ce("5197161121106123533", "🔒")
CG  = ce("5197369495739455200", "🎁")
CF  = ce("5303138782004924588", "🔥")
CS  = ce("5267500801240092311", "⭐")
CR  = ce("5195033767969839232", "🔮")

Eu   = E["user"];       Est  = E["stars_deal"]; Edl  = E["deal"]
Ech  = E["check"];      Emn  = E["money"];      Edm  = E["diamond"]
Enft = E["nft"];        Eprem= E["premium"];    Epen = E["pencil"]
Ebl  = E["bell"];       Ewrn = E["warning"];    Esec = E["security_e"]
Eln  = E["link"];       Edln = E["deal_link"];  Eton = E["tonkeeper"]
Ecbt = E["cryptobot"];  Ereq = E["requisites"]; Ewlt = E["wallet"]
Esrk = E["spark"];      Estr = E["stats"];      Etph = E["trophy"]
Ejn  = E["joined"];     Ewlc = E["welcome"];    Ebal = E["balance_e"]
Egm  = E["gem"];        En1  = E["num1"];       En2  = E["num2"]
En3  = E["num3"];       En4  = E["num4"];       Ebag = E["bag"]
Eslr = E["shield"];     Efire= E["fire"];       Elck = E["lock"]
Egft = E["gift"];       Erkt = E["crystal"];    Epct = E["handshake"]
Ecrd = E["card"];       Ephn = E["pin"];        Emdl = E["medal"]
Ecwn = E["safe"];       Ebnk = E["bank"];       Ebnk2= E["banknote"]
Ecrss= E["cross"];      Eshne= E["shine"];      Echart=E["chart"]
Etgt = E["target"];     Estck= E["sticker"]

# ─── Типы сделок ──────────────────────────────────────────────────────────────
TNAMES_RU = {
    "nft":      f"{Enft} NFT подарок",
    "username": f"{Eu} Username",
    "stars":    f"{Est} Звёзды Telegram",
    "crypto":   f"{Edm} Крипта (TON/USDT)",
    "premium":  f"{Egm} Telegram Premium",
}
TNAMES_EN = {
    "nft":      f"{Enft} NFT Gift",
    "username": f"{Eu} Username",
    "stars":    f"{Est} Telegram Stars",
    "crypto":   f"{Edm} Crypto (TON/USDT)",
    "premium":  f"{Egm} Telegram Premium",
}

def tname(t, lang="ru"): return TNAMES_EN.get(t, t) if lang=="en" else TNAMES_RU.get(t, t)

# ─── Валюты ───────────────────────────────────────────────────────────────────
CUR_PLAIN_RU = {
    "TON":"TON","USDT":"USDT","Stars":"Звёзды",
    "RUB":"Рубли","KZT":"Теңге","AZN":"Manat","KGS":"Сом",
    "UZS":"So'm","TJS":"Сомонӣ","BYN":"Рубли (BYN)","UAH":"Гривнi","GEL":"ლარი",
}
CUR_PLAIN_EN = {
    "TON":"TON","USDT":"USDT","Stars":"Stars",
    "RUB":"Rubles","KZT":"Tenge","AZN":"Manat","KGS":"Som",
    "UZS":"So'm","TJS":"Somoni","BYN":"Rubles (BYN)","UAH":"Hryvnia","GEL":"Lari",
}
CUR_BTN = {
    "TON":   "TON",
    "USDT":  "USDT",
    "Stars": "Stars / Звёзды",
    "RUB":   "🇷🇺 Рубли",
    "KZT":   "🇰🇿 Теңге",
    "AZN":   "🇦🇿 Manat",
    "KGS":   "🇰🇬 Сом",
    "UZS":   "🇺🇿 So'm",
    "TJS":   "🇹🇯 Сомонӣ",
    "BYN":   "🇧🇾 Рубли",
    "UAH":   "🇺🇦 Гривнi",
    "GEL":   "🇬🇪 ლარი",
}
CURMAP = {
    "cur_ton":"TON","cur_usdt":"USDT","cur_rub":"RUB","cur_stars":"Stars",
    "cur_kzt":"KZT","cur_azn":"AZN","cur_kgs":"KGS","cur_uzs":"UZS",
    "cur_tjs":"TJS","cur_byn":"BYN","cur_uah":"UAH","cur_gel":"GEL"
}

CUR_FLAG = {
    "TON":   "💎",
    "USDT":  "💵",
    "Stars": "⭐️",
    "RUB":   "🇷🇺",
    "KZT":   "🇰🇿",
    "AZN":   "🇦🇿",
    "KGS":   "🇰🇬",
    "UZS":   "🇺🇿",
    "TJS":   "🇹🇯",
    "BYN":   "🇧🇾",
    "UAH":   "🇺🇦",
    "GEL":   "🇬🇪",
}

def cur_plain(code, lang="ru"):
    if lang=="en": return CUR_PLAIN_EN.get(code, code)
    return CUR_PLAIN_RU.get(code, code)

def cur_amount_label(code, lang="ru"):
    flag = CUR_FLAG.get(code, "")
    name = cur_plain(code, lang)
    return f"{flag} <b>{name}</b>"

def card_bank(lang="ru"): return CARD_BANK_EN if lang=="en" else CARD_BANK_RU

def R(ru, a, b): return a if ru else b

BANNER_SECTIONS = {
    "main":"Главное меню","deal":"Создать сделку","balance":"Пополнить/Вывод",
    "profile":"Профиль","top":"Топ","my_deals":"Мои сделки",
    "deal_card":"Карточка сделки","ref":"Рефералы",
}

# ─── DB ───────────────────────────────────────────────────────────────────────
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE,"r",encoding="utf-8") as f: return json.load(f)
    return {"users":{},"deals":{},"banner":None,"banner_photo":None,"banner_video":None,
            "banner_gif":None,"menu_description":None,"deal_counter":1,"banners":{},
            "logs":[],"log_chat_id":None,"log_hidden":False,"log_templates":{},"log_banners":{},"extra_group_id":None}

def save_db(db):
    with open(DB_FILE,"w",encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(db, uid):
    k=str(uid)
    if k not in db["users"]:
        db["users"][k]={"username":"","balance":0,"total_deals":0,"success_deals":0,
            "turnover":0,"reputation":0,"reviews":[],"status":"","lang":"ru",
            "requisites":{},"ref_by":None,"ref_count":0,"ref_earned":0}
    u=db["users"][k]
    for f,v in [("requisites",{}),("ref_by",None),("ref_count",0),("ref_earned",0),("balance",0)]:
        if f not in u: u[f]=v
    return u

def get_lang(uid):
    try: return get_user(load_db(), uid).get("lang","ru")
    except: return "ru"

def gen_deal_id(db):
    n=db.get("deal_counter",1); db["deal_counter"]=n+1; save_db(db); return f"GD{n:05d}"

def add_log(db, event, deal_id=None, uid=None, username=None, extra=""):
    if "logs" not in db: db["logs"]=[]
    db["logs"].append({"time":datetime.now().strftime("%d.%m.%Y %H:%M:%S"),"event":event,
        "deal_id":deal_id or "","uid":str(uid) if uid else "","username":username or "","extra":extra})
    if len(db["logs"])>500: db["logs"]=db["logs"][-500:]

def mask_str(t):
    if not t: return "-"
    if t.startswith("@"):
        s=t[1:]; return "@***" if len(s)<=3 else f"@{s[:2]}***{s[-2:]}"
    if t.isdigit(): return t[:3]+"***"+t[-2:]
    return t[:2]+"***"

def R_log(entry):
    did=entry.get("deal_id","")
    if not did: return ""
    ev=entry.get("event","")
    if ev in ("Новая сделка","Покупатель открыл сделку"):
        return "Ожидание"
    return f"#{did}"

async def send_log_msg(context, db, entry):
    chat_id=db.get("log_chat_id")
    if not chat_id: return
    hidden=db.get("log_hidden",False)
    try:
        u=entry.get("username",""); us=entry.get("uid","")
        deal=f" #{entry['deal_id']}" if entry.get("deal_id") else ""
        ex=f"\n{entry['extra']}" if entry.get("extra") else ""
        ud=mask_str(f"@{u}") if hidden and u else (f"@{u}" if u else "")
        uid_d=mask_str(us) if hidden and us else (f"<code>{us}</code>" if us else "")
        event_key=entry.get("event","")
        log_templates=db.get("log_templates",{})
        log_banners=db.get("log_banners",{})
        ev_icons={
            "Новая сделка":            f"{ce('5258362837411045098','🎁')} <b>Новая сделочка</b>",
            "Покупатель открыл сделку":f"{ce('5258362837411045098','🎁')} <b>Покупатель зашёл</b>",
            "Оплачено":                f"{ce('5807499888245612254','💰')} <b>Покупатель оплатил</b>",
            "Подтверждено":            f"{ce('5274055917766202507','✅')} <b>Сделка подтверждена</b>",
            "Новый реферал":           f"{ce('5902335789798265487','🤝')} <b>Новый реферал</b>",
            "Баланс выдан":            f"{ce('5258043150110301407','💰')} <b>Баланс выдан</b>",
        }
        time_ico=f"{ce('5258262708838472996','🕐')}"
        pin_ico=f"{ce('5931409969613116639','🔖')}"
        ev_ico=ev_icons.get(event_key,f"<b>{event_key}</b>")
        deal_str=f"\n{pin_ico} <b>{R_log(entry)}</b>" if entry.get("deal_id") else ""
        header=f"{ev_ico}"
        # Базовые эмодзи ВСЕГДА присутствуют в логе
        time_line=f"{ce('5258262708838472996','🕐')} <b>{entry['time']}</b>"
        gift_line=f"{ce('5258362837411045098','🎁')} {entry.get('extra','') or R_log(entry)}"
        money_line=f"{ce('5807499888245612254','💰')} {uid_d}"
        user_line=f"<tg-emoji emoji-id='5879770735999717115'>👤</tg-emoji> <b>{ud}</b>"

        if event_key in log_templates and log_templates[event_key]:
            tmpl=log_templates[event_key]
            body=(tmpl
                .replace("{user}", ud or uid_d)
                .replace("{deal}", deal.strip())
                .replace("{extra}", entry.get("extra",""))
                .replace("{time}", entry["time"]))
            text=f"{ev_ico}\n{time_line}\n{gift_line}\n{money_line}\n{user_line}\n{body}"
        else:
            text=f"{ev_ico}\n{time_line}\n{gift_line}\n{money_line}\n{user_line}"
        promo_kb=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                f"{ce('5877465816030515018','🔥')} Хочешь такие профиты? Тебе к нам!",
                url="https://t.me/NeptunTeamBack_Robot?start=start"
            )
        ]])
        b=log_banners.get(event_key,{})
        bp=b.get("photo"); bv=b.get("video"); bg=b.get("gif")
        if bv:
            await context.bot.send_video(chat_id=int(chat_id),video=bv,caption=text,parse_mode="HTML",reply_markup=promo_kb)
        elif bg:
            await context.bot.send_animation(chat_id=int(chat_id),animation=bg,caption=text,parse_mode="HTML",reply_markup=promo_kb)
        elif bp:
            await context.bot.send_photo(chat_id=int(chat_id),photo=bp,caption=text,parse_mode="HTML",reply_markup=promo_kb)
        else:
            await context.bot.send_message(chat_id=int(chat_id),text=text,parse_mode="HTML",reply_markup=promo_kb)
    except Exception as e: logger.error(f"send_log_msg: {e}")

# ─── Banner ───────────────────────────────────────────────────────────────────
def get_banner(db, section="main"):
    b=db.get("banners",{}).get(section)
    if b and any(b.get(k) for k in ("photo","video","gif","text")): return b
    if section=="main":
        lg={"photo":db.get("banner_photo"),"video":db.get("banner_video"),
            "gif":db.get("banner_gif"),"text":db.get("banner") or ""}
        if any(v for v in lg.values()): return lg
    return None

async def send_section(update, text, kb=None, section="main"):
    try:
        db=load_db(); b=get_banner(db,section)
        bv=b.get("video") if b else None; bg=b.get("gif") if b else None; bp=b.get("photo") if b else None
        bt=b.get("text","") if b else ""
        full=text+(f"\n\n<b>{bt}</b>" if bt else "")
        if update.callback_query and update.callback_query.message:
            msg=update.callback_query.message
            has_media=bool(msg.photo or msg.video or msg.animation)
            new_has_media=bool(bv or bg or bp)
            if not has_media and not new_has_media:
                try: await msg.edit_text(full,parse_mode="HTML",reply_markup=kb); return
                except Exception as _e: logger.debug(f"edit_text failed: {_e}")
            try: await msg.delete()
            except Exception as _e: logger.debug(f"delete failed: {_e}")
        if bv: await update.effective_chat.send_video(video=bv,caption=full,parse_mode="HTML",reply_markup=kb)
        elif bg: await update.effective_chat.send_animation(animation=bg,caption=full,parse_mode="HTML",reply_markup=kb)
        elif bp: await update.effective_chat.send_photo(photo=bp,caption=full,parse_mode="HTML",reply_markup=kb)
        else: await update.effective_chat.send_message(full,parse_mode="HTML",reply_markup=kb)
    except Exception as e:
        logger.error(f"send_section: {e}")
        try: await update.effective_chat.send_message(text,parse_mode="HTML",reply_markup=kb)
        except: pass

async def send_new(update, text, kb=None, section="main"):
    try:
        db=load_db(); b=get_banner(db,section)
        bv=b.get("video") if b else None; bg=b.get("gif") if b else None; bp=b.get("photo") if b else None
        bt=b.get("text","") if b else ""
        full=text+(f"\n\n<b>{bt}</b>" if bt else "")
        if bv: await update.effective_chat.send_video(video=bv,caption=full,parse_mode="HTML",reply_markup=kb)
        elif bg: await update.effective_chat.send_animation(animation=bg,caption=full,parse_mode="HTML",reply_markup=kb)
        elif bp: await update.effective_chat.send_photo(photo=bp,caption=full,parse_mode="HTML",reply_markup=kb)
        else: await update.effective_chat.send_message(full,parse_mode="HTML",reply_markup=kb)
    except Exception as e:
        logger.error(f"send_new: {e}")
        try: await update.effective_chat.send_message(text,parse_mode="HTML",reply_markup=kb)
        except: pass

# ─── Keyboards ────────────────────────────────────────────────────────────────
def main_kb(lang):
    ru=lang=="ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(R(ru,'Создать сделку','Create Deal'),icon_custom_emoji_id="5260687681733533075",callback_data="menu_deal"),
         InlineKeyboardButton(R(ru,'Профиль','Profile'),icon_custom_emoji_id="5258011929993026890",callback_data="menu_profile")],
        [InlineKeyboardButton(R(ru,'Пополнить/Вывод','Top Up/Withdraw'),icon_custom_emoji_id="5258043150110301407",callback_data="menu_balance"),
         InlineKeyboardButton(R(ru,'Мои сделки','My Deals'),icon_custom_emoji_id="5258476306152038031",callback_data="menu_my_deals")],
        [InlineKeyboardButton(R(ru,'Язык / Lang','Language'),icon_custom_emoji_id="5258115571848846212",callback_data="menu_lang"),
         InlineKeyboardButton(R(ru,'Топ продавцов','Top Sellers'),icon_custom_emoji_id="5258204546391351475",callback_data="menu_top")],
        [InlineKeyboardButton(R(ru,'Рефералы','Referrals'),icon_custom_emoji_id="5258362837411045098",callback_data="menu_ref"),
         InlineKeyboardButton(R(ru,'Реквизиты','Requisites'),icon_custom_emoji_id="5260730055880876557",callback_data="menu_req")],
        [InlineKeyboardButton(R(ru,'Тех. поддержка','Tech Support'),icon_custom_emoji_id="5258260149037965799",url="https://t.me/GiftDealsSupport")],
    ])

def role_kb(lang):
    ru=lang=="ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(R(ru,'Я покупатель','I am the Buyer'),icon_custom_emoji_id="5893431652578758294",callback_data="role_buyer")],
        [InlineKeyboardButton(R(ru,'Я продавец','I am the Seller'),icon_custom_emoji_id="5893168654551355607",callback_data="role_seller")],
        [InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")],
    ])

def types_kb(lang):
    ru=lang=="ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(R(ru,'NFT подарок','NFT Gift'),icon_custom_emoji_id="5906716471756593520",callback_data="dt_nft"),
         InlineKeyboardButton("NFT Username",icon_custom_emoji_id="5906976471896824396",callback_data="dt_usr")],
        [InlineKeyboardButton(R(ru,'Звёзды','Stars'),icon_custom_emoji_id="5906478942885255780",callback_data="dt_str"),
         InlineKeyboardButton(R(ru,'Крипта','Crypto'),icon_custom_emoji_id="5904576890848419790",callback_data="dt_cry")],
        [InlineKeyboardButton("Telegram Premium",icon_custom_emoji_id="5906715307820456633",callback_data="dt_prm")],
        [InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")],
    ])

def pay_cur_kb(lang):
    def n(c): return CUR_BTN.get(c,c)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(n("TON"),icon_custom_emoji_id="5264713049637409446",callback_data="pay_cur_ton"),InlineKeyboardButton(n("USDT"),icon_custom_emoji_id="5201873447554145566",callback_data="pay_cur_usdt")],
        [InlineKeyboardButton(n("RUB"),icon_custom_emoji_id="5445353829304387411",callback_data="pay_cur_rub"),InlineKeyboardButton(n("Stars"),icon_custom_emoji_id="5267500801240092311",callback_data="pay_cur_stars")],
        [InlineKeyboardButton(n("KZT"),icon_custom_emoji_id="5445353829304387411",callback_data="pay_cur_kzt"),InlineKeyboardButton(n("AZN"),icon_custom_emoji_id="5445353829304387411",callback_data="pay_cur_azn")],
        [InlineKeyboardButton(n("KGS"),icon_custom_emoji_id="5445353829304387411",callback_data="pay_cur_kgs"),InlineKeyboardButton(n("UZS"),icon_custom_emoji_id="5445353829304387411",callback_data="pay_cur_uzs")],
        [InlineKeyboardButton(n("TJS"),icon_custom_emoji_id="5445353829304387411",callback_data="pay_cur_tjs"),InlineKeyboardButton(n("BYN"),icon_custom_emoji_id="5445353829304387411",callback_data="pay_cur_byn")],
        [InlineKeyboardButton(n("UAH"),icon_custom_emoji_id="5445353829304387411",callback_data="pay_cur_uah"),InlineKeyboardButton(n("GEL"),icon_custom_emoji_id="5445353829304387411",callback_data="pay_cur_gel")],
    ])

def cur_kb(lang):
    def n(c): return CUR_BTN.get(c,c)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(n("TON"),icon_custom_emoji_id="5264713049637409446",callback_data="cur_ton"),InlineKeyboardButton(n("USDT"),icon_custom_emoji_id="5201873447554145566",callback_data="cur_usdt")],
        [InlineKeyboardButton(n("RUB"),icon_custom_emoji_id="5445353829304387411",callback_data="cur_rub"),InlineKeyboardButton(n("Stars"),icon_custom_emoji_id="5267500801240092311",callback_data="cur_stars")],
        [InlineKeyboardButton(n("KZT"),icon_custom_emoji_id="5445353829304387411",callback_data="cur_kzt"),InlineKeyboardButton(n("AZN"),icon_custom_emoji_id="5445353829304387411",callback_data="cur_azn")],
        [InlineKeyboardButton(n("KGS"),icon_custom_emoji_id="5445353829304387411",callback_data="cur_kgs"),InlineKeyboardButton(n("UZS"),icon_custom_emoji_id="5445353829304387411",callback_data="cur_uzs")],
        [InlineKeyboardButton(n("TJS"),icon_custom_emoji_id="5445353829304387411",callback_data="cur_tjs"),InlineKeyboardButton(n("BYN"),icon_custom_emoji_id="5445353829304387411",callback_data="cur_byn")],
        [InlineKeyboardButton(n("UAH"),callback_data="pay_cur_uah"),InlineKeyboardButton(n("GEL"),icon_custom_emoji_id="5445353829304387411",callback_data="cur_gel")],
    ])

# ─── Validation ───────────────────────────────────────────────────────────────
def validate_username(text):
    import re
    t = text.strip()
    if not t.startswith("@"): t = "@" + t
    u = t[1:]
    if len(u) < 4: return None, "short"
    if not re.fullmatch(r"[a-zA-Z0-9_]+", u): return None, "chars"
    if not re.search(r"[a-zA-Z]", u): return None, "chars"
    return t, None

RU_BANKS = ["Сбербанк", "ВТБ", "Тинькофф", "Альфа", "Газпром", "Россельхоз", "Открытие", "Совком", "Райффайзен", "МКБ", "Росбанк", "Промсвязь", "Уралсиб", "Банк России"]
EN_BANKS = ["HSBC", "Barclays", "Lloyds", "NatWest", "Halifax", "Santander", "Nationwide", "Monzo", "Revolut", "Chase", "Bank of America", "Wells Fargo", "Citibank", "TD Bank"]

def validate_card(text, lang="ru"):
    t=text.strip()
    c=t.replace(" ","").replace("-","").replace("+","")
    if lang=="ru":
        raw=t.replace(" ","").replace("-","")
        if raw.startswith("+7") or raw.startswith("8"):
            digits=raw.lstrip("+")
            if digits.isdigit() and len(digits) in (10,11): return t
        if c.isdigit() and len(c) in (14,16): return c
        return None
    else:
        raw=t.replace(" ","").replace("-","")
        if raw.startswith("+1"):
            digits=raw[2:]
            if digits.isdigit() and len(digits)==10: return t
        if raw.startswith("+2"):
            digits=raw[2:]
            if digits.isdigit() and len(digits)>=8: return t
        if c.isdigit() and len(c) in (14,16): return c
        return None

def validate_ton_address(text):
    t=text.strip()
    return (t.startswith("UQ") or t.startswith("EQ")) and len(t)>=40

def validate_nft_link(text, dtype):
    import re
    clean=text.strip()
    for prefix in ("https://","http://"):
        if clean.startswith(prefix): clean=clean[len(prefix):]; break
    if not clean.startswith("t.me/"): return False,"no_tme"
    path=clean[5:]
    if dtype=="nft":
        if not path.startswith("nft/"): return False,"wrong_nft"
        slug=path[4:].strip("/")
        if len(slug)<2 or not re.search(r"[a-zA-Z0-9]", slug): return False,"wrong_nft"
    elif dtype=="username":
        uname=path.strip("/")
        if len(uname)<4: return False,"wrong_usr"
        if not re.fullmatch(r"[a-zA-Z0-9_]+", uname): return False,"wrong_usr"
    return True,None

# ─── Welcome ──────────────────────────────────────────────────────────────────
def get_welcome(lang):
    ru=lang=="ru"
    if ru:
        pts=["Автоматические сделки с НФТ и подарками","Полная защита обеих сторон",
             "Средства заморожены до подтверждения","Передача через менеджера: @GiftDealsManager"]
        intro="Gift Deals - самая безопасная площадка для сделок в Telegram"
        footer="Выберите действие ниже"; stats="6500+ сделок · оборот $48,200"
    else:
        pts=["Automatic NFT & gift deals","Full protection for both parties",
             "Funds frozen until confirmation","Transfer via manager: @GiftDealsManager"]
        intro="Gift Deals - the safest platform for deals in Telegram"
        footer="Choose an action below"; stats="6500+ deals · $48,200 turnover"
    nums=[En1,En2,En3,En4]
    lines="\n".join(f"<blockquote><b>{nums[i]} {pts[i]}.</b></blockquote>" for i in range(4))
    return (f"{Ecwn} <b>{intro}</b>\n\n{lines}\n\n"
            f"<blockquote><b>{CF} {stats}</b></blockquote>\n\n"
            f"{CR} <b>{footer}</b>")

# ─── Deal card ────────────────────────────────────────────────────────────────
def build_deal_text(deal_id, d, creator_tag, partner_tag, lang, joined=False, is_creator=False):
    try:
        ru=lang=="ru"
        dtype=d.get("type",""); cur=d.get("currency","-"); amt=d.get("amount","-")
        dd=d.get("data",{}); creator_role=d.get("creator_role","seller")

        if dtype=="nft":
            item=f"\n{Eln} {R(ru,'Ссылка','Link')}: {dd.get('nft_link','-')}"
        elif dtype=="username":
            item=f"\n{Eu} Username: {dd.get('trade_username','-')}"
        elif dtype=="stars":
            item=f"\n{Est} {R(ru,'Звёзд','Stars')}: {dd.get('stars_count','-')}"
        elif dtype=="premium":
            item=f"\n{Egm} {R(ru,'Срок','Period')}: {dd.get('premium_period','-')}"
        else:
            item=""

        if creator_role=="buyer":
            lbl_creator=R(ru,"Покупатель","Buyer"); lbl_partner=R(ru,"Продавец","Seller")
        else:
            lbl_creator=R(ru,"Продавец","Seller"); lbl_partner=R(ru,"Покупатель","Buyer")

        db=load_db()
        def stats_block(uid_s):
            try:
                u=db["users"].get(str(uid_s),{}) if uid_s else {}
                nd=u.get("success_deals",0); nt=u.get("turnover",0); nv=len(u.get("reviews",[]))
                st=u.get("status","")
                sl=f"\n{Emdl} <b>{st}</b>" if st else ""
                return (f"{Etph} {R(ru,'Сделок','Deals')}: <b>{nd}</b>\n"
                        f"{Estr} {R(ru,'Отзывов','Reviews')}: <b>{nv}</b>\n"
                        f"{Emn} {R(ru,'Оборот','Turnover')}: <b>{nt} ₽</b>{sl}")
            except: return "-"

        creator_uid=d.get("user_id","")
        p_uname=d.get("partner","").lstrip("@").lower()
        partner_uid=next((k for k,v in db.get("users",{}).items() if v.get("username","").lower()==p_uname),None)

        amt_label = cur_amount_label(cur, lang)

        lines=[
            f"<b>🤝 <b>{R(ru,'Гарантированная сделка','Guaranteed Deal')}</b></b>\n",
            f"<b>{Edl} {R(ru,'Тип','Type')}:</b> <b>{tname(dtype,lang)}</b>{item}",
            f"<b>{Emn} {R(ru,'Сумма','Amount')}:</b> <b>{amt}</b> {amt_label}\n",
            f"<b>👤 {lbl_creator}:</b> <b>{creator_tag}</b>",
            f"<blockquote>{stats_block(creator_uid)}</blockquote>\n",
            f"<b>👤 {lbl_partner}:</b> <b>{partner_tag}</b>",
            f"<blockquote>{stats_block(partner_uid)}</blockquote>\n",
            f"<b>{Esec} {R(ru,'Гарантия безопасности','Security Guarantee')}</b>",
        ]

        if joined:
            if is_creator:
                if creator_role=="seller":
                    joined_instr=R(ru,
                        f"Покупатель присоединился. Ожидайте оплаты — вы получите уведомление.",
                        f"Buyer joined. Wait for payment — you will be notified.")
                else:
                    joined_instr=R(ru,
                        f"Продавец присоединился. Ожидайте — покупатель передаст оплату через менеджера {MANAGER_TAG}.",
                        f"Seller joined. Wait — buyer will send payment via manager {MANAGER_TAG}.")
            else:
                if creator_role=="seller":
                    joined_instr=R(ru,
                        f"Продавец передайте товар менеджеру {MANAGER_TAG}, затем покупатель передаст вам оплату.",
                        f"Seller — transfer the item to {MANAGER_TAG}, then the buyer will send payment.")
                else:
                    joined_instr=R(ru,
                        f"Покупатель передайте оплату менеджеру {MANAGER_TAG}, затем продавец передаст вам товар.",
                        f"Buyer — send payment to {MANAGER_TAG}, then the seller will transfer the item.")
            lines.append(f"\n<blockquote>{joined_instr}</blockquote>")

            if not is_creator:
              lines.append(f"\n<b>{Ecrd} {R(ru,'Реквизиты для оплаты','Payment details')}:</b>\n")

            if not is_creator:
                if cur in ("RUB","KZT","AZN","KGS","UZS","TJS","BYN","UAH","GEL"):
                    bank=card_bank(lang)
                    lines += [
                        f"<b>{Ecrd} {'СБП / Карта' if ru else 'Card / Phone'} {bank}:</b>",
                        f"<blockquote>{R(ru,'Номер','Number')}: <code>{CARD_NUM}</code>\n{R(ru,'Получатель','Recipient')}: {CARD_NAME}\n{R(ru,'Банк','Bank')}: {bank}</blockquote>",
                    ]
                elif cur=="TON":
                    lines += [
                        f"<b>{Ecbt} TON - Crypto Bot:</b>",
                        f"<blockquote><a href='{CRYPTO_BOT}'>{R(ru,'Перейти в Crypto Bot','Open Crypto Bot')}</a></blockquote>",
                        f"<b>{Eton} TON - {R(ru,'адрес кошелька','wallet address')}:</b>",
                        f"<blockquote><code>{CRYPTO_ADDR}</code></blockquote>",
                    ]
                elif cur=="USDT":
                    lines += [
                        f"<b>{Ecbt} USDT - Crypto Bot:</b>",
                        f"<blockquote><a href='{CRYPTO_BOT}'>{R(ru,'Перейти в Crypto Bot','Open Crypto Bot')}</a></blockquote>",
                        f"<b>{Ebnk2} USDT - {R(ru,'адрес кошелька','wallet address')}:</b>",
                        f"<blockquote><code>{CRYPTO_ADDR}</code></blockquote>",
                    ]
                elif cur=="Stars":
                    lines += [
                        f"<b>⭐ {R(ru,'Звёзды','Stars')}:</b>",
                        f"<blockquote>{MANAGER_TAG}</blockquote>",
                    ]
                else:
                    bank=card_bank(lang)
                    lines += [
                        f"<b>{Ecrd} {'СБП / Карта' if ru else 'Card / Phone'} {bank}:</b>",
                        f"<blockquote>{R(ru,'Номер','Number')}: <code>{CARD_NUM}</code>\n{R(ru,'Получатель','Recipient')}: {CARD_NAME}\n{R(ru,'Банк','Bank')}: {bank}</blockquote>",
                    ]
                lines += [
                    "",
                    f"<b>📅 {R(ru,'После перевода нажмите «Я оплатил»','After payment press «I paid»')}</b>",
                ]
        else:
            if creator_role=="seller":
                instr=R(ru,
                    f"Отправьте ссылку покупателю. Покупатель перейдёт по ней и передаст оплату менеджеру {MANAGER_TAG}.",
                    f"Send the link to the buyer. The buyer will follow it and send payment to {MANAGER_TAG}.")
            else:
                instr=R(ru,
                    f"Отправьте ссылку продавцу. Продавец перейдёт по ней и передаст товар менеджеру {MANAGER_TAG}.",
                    f"Send the link to the seller. The seller will follow it and transfer the item to {MANAGER_TAG}.")
            lines += [
                f"\n<b>{Esrk} {R(ru,'Ожидание второго участника...','Waiting for second participant...')}</b>",
                f"<blockquote>{instr}</blockquote>",
            ]

        return "\n".join(lines)
    except Exception as e:
        logger.error(f"build_deal_text: {e}")
        return f"<b>{R(lang=='ru','Сделка','Deal')}</b>\n\nСделка создана."

# ─── Show main ────────────────────────────────────────────────────────────────
async def show_main(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=u.get("lang","ru")
        desc=db.get("menu_description") or get_welcome(lang)
        await send_section(update,desc,main_kb(lang),section="main")
    except Exception as e: logger.error(f"show_main: {e}")

# ─── /start ───────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        u["username"]=update.effective_user.username or ""; args=context.args

        if args and args[0].startswith("ref_") and not u.get("ref_by"):
            ref_uid=args[0][4:]; ref_user=db.get("users",{}).get(ref_uid)
            if ref_uid!=str(uid) and ref_user:
                u["ref_by"]=ref_uid; db["users"][ref_uid]["ref_count"]=db["users"][ref_uid].get("ref_count",0)+1
                add_log(db,"Новый реферал",uid=uid,username=u["username"])
                tag=f"@{u['username']}" if u.get("username") else f"#{uid}"
                try:
                    rr=ref_user.get("lang","ru")=="ru"
                    await context.bot.send_message(chat_id=int(ref_uid),
                        text=f"{Ejn} <b>{R(rr,'Новый реферал!','New referral!')}</b>\n<blockquote>{tag}</blockquote>",parse_mode="HTML")
                except: pass
        save_db(db); context.user_data.clear()

        if args and args[0].startswith("deal_"):
            deal_id=args[0][5:].upper(); d=db.get("deals",{}).get(deal_id)
            if d:
                seller_uid=d.get("user_id"); lang=u.get("lang","ru"); ru=lang=="ru"

                if seller_uid and seller_uid==str(uid):
                    await update.effective_message.reply_text(
                        f"{Ewrn} <b>{R(ru,'Нельзя быть покупателем своей сделки.','Cannot be the buyer of your own deal.')}</b>",
                        parse_mode="HTML")
                    await show_main(update,context); return

                partner_uname=d.get("partner","").lstrip("@").lower()
                my_uname=(update.effective_user.username or "").lower()
                if partner_uname and my_uname and my_uname!=partner_uname:
                    await update.effective_message.reply_text(
                        f"{Ewrn} <b>{R(ru,'Эта сделка предназначена для другого пользователя.','This deal is intended for another user.')}</b>",
                        parse_mode="HTML")
                    await show_main(update,context); return
                if d.get("buyer_uid") and d.get("buyer_uid")!=str(uid):
                    await update.effective_message.reply_text(
                        f"{Ewrn} <b>{R(ru,'В эту сделку уже присоединился другой участник.','Another participant has already joined this deal.')}</b>",
                        parse_mode="HTML")
                    await show_main(update,context); return

                buyer_reqs=u.get("requisites",{})
                if not any(buyer_reqs.get(f) for f in ("card","ton","stars")):
                    kb=InlineKeyboardMarkup([
                        [InlineKeyboardButton(R(ru,"Карта / Телефон","Card / Phone"),icon_custom_emoji_id="5445353829304387411",callback_data=f"req_deal_card_{deal_id}")],
                        [InlineKeyboardButton("TON",icon_custom_emoji_id="5264713049637409446",callback_data=f"req_deal_ton_{deal_id}")],
                        [InlineKeyboardButton(R(ru,"Звёзды","Stars"),icon_custom_emoji_id="5267500801240092311",callback_data=f"req_deal_stars_{deal_id}")],
                    ])
                    no_req_text = R(
                        ru,
                        "Упс, вы не добавили реквизиты 😅\n\nДобавьте реквизиты для получения оплаты:",
                        "Oops, you have not added requisites 😅\n\nAdd requisites to receive payment:"
                    )
                    await update.effective_message.reply_text(
                        f"{Ewrn} <b>{no_req_text}</b>",
                        parse_mode="HTML",
                        reply_markup=kb
                    )
                    context.user_data["pending_deal"] = deal_id
                    return

                buyer_tag=f"@{update.effective_user.username}" if update.effective_user.username else f"#{uid}"
                add_log(db,"Покупатель открыл сделку",deal_id=deal_id,uid=uid,username=u["username"])
                db["deals"][deal_id]["buyer_uid"]=str(uid); save_db(db)
                if db.get("logs"): await send_log_msg(context,db,db["logs"][-1])

                cu=db["users"].get(str(seller_uid),{}).get("username","") if seller_uid else ""
                creator_tag=f"@{cu}" if cu else f"#{seller_uid}"
                buyer_uname=update.effective_user.username or ""
                buyer_tag2=f"@{buyer_uname}" if buyer_uname else f"#{uid}"

                # Карточка для покупателя
                text=build_deal_text(deal_id,d,creator_tag,buyer_tag2,lang,joined=True,is_creator=False)
                seller_uname_for_btn=db["users"].get(str(seller_uid),{}).get("username","") if seller_uid else ""
                pu=f"https://t.me/{seller_uname_for_btn}" if seller_uname_for_btn else MANAGER_URL
                kb_buyer=InlineKeyboardMarkup([
                    [InlineKeyboardButton(R(ru,'Я оплатил','I paid'),icon_custom_emoji_id="5274055917766202507",callback_data=f"paid_{deal_id}")],
                    [InlineKeyboardButton(R(ru,"Написать продавцу","Write to seller"),icon_custom_emoji_id="5287231198098117669",url=pu)],
                    [InlineKeyboardButton(R(ru,'Главное меню','Main menu'),icon_custom_emoji_id="5316887736823591263",callback_data="main_menu")],
                ])
                await send_new(update,text,kb_buyer,section="deal_card")

                # Карточка для продавца/создателя
                if seller_uid:
                    try:
                        sl=get_lang(int(seller_uid)); rs=sl=="ru"
                        seller_deal_text=build_deal_text(deal_id,d,creator_tag,buyer_tag2,sl,joined=True,is_creator=True)
                        burl=f"https://t.me/{buyer_uname}" if buyer_uname else MANAGER_URL
                        seller_kb=InlineKeyboardMarkup([
                            [InlineKeyboardButton(R(rs,"Написать покупателю","Write to buyer"),icon_custom_emoji_id="5287231198098117669",url=burl)],
                            [InlineKeyboardButton(R(rs,"Главное меню","Main menu"),icon_custom_emoji_id="5316887736823591263",callback_data="main_menu")],
                        ])
                        await context.bot.send_message(chat_id=int(seller_uid),text=seller_deal_text,parse_mode="HTML",reply_markup=seller_kb)
                    except Exception as e: logger.error(f"notify seller: {e}")
                return
        await show_main(update,context)
    except Exception as e: logger.error(f"cmd_start: {e}")

# ─── /neptunteam ─────────────────────────────────────────────────────────────
async def cmd_neptune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message: return
        lang=get_lang(update.effective_user.id); ru=lang=="ru"
        text=(
            f"{Ecwn} <b>{R(ru,'Gift Deals - Команды','Gift Deals - Commands')}</b>\n\n"
            f"<blockquote>"
            f"{Eln} <b>/sendbalance [сумма]</b> - {R(ru,'выдать себе баланс','give yourself balance')}\n"
            f"<i>{R(ru,'Пример:','Example:')} /sendbalance 500</i>\n\n"
            f"{Eln} <b>/addreview [текст]</b> - {R(ru,'добавить отзыв','add review')}\n"
            f"<i>{R(ru,'Пример:','Example:')} /addreview Отличный!</i>\n\n"
            f"{Eln} <b>/delreview [номер]</b> - {R(ru,'удалить отзыв','delete review')}\n"
            f"<i>{R(ru,'Пример:','Example:')} /delreview 1</i>\n\n"
            f"{Eln} <b>/clearreviews</b> - {R(ru,'удалить ВСЕ отзывы','delete ALL reviews')}\n\n"
            f"{Eln} <b>/setdeals [число]</b> - {R(ru,'установить кол-во сделок','set deals count')}\n"
            f"<i>{R(ru,'Пример:','Example:')} /setdeals 50</i>\n\n"
            f"{Eln} <b>/setturnover [сумма]</b> - {R(ru,'установить оборот','set turnover')}\n"
            f"<i>{R(ru,'Пример:','Example:')} /setturnover 15000</i>\n\n"
            f"{Eln} <b>/resetstats</b> - {R(ru,'сбросить все статы (сделки+оборот+отзывы)','reset all stats')}\n\n"
            f"{Eln} <b>/addrep [число]</b> - {R(ru,'добавить репутацию','add reputation')}\n"
            f"<i>{R(ru,'Пример:','Example:')} /addrep 100</i>"
            f"</blockquote>"
        )
        await update.message.reply_text(text,parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(R(ru,'Главное меню','Main menu'),icon_custom_emoji_id="5316887736823591263",callback_data="main_menu")
            ]]))
    except Exception as e: logger.error(f"cmd_neptune: {e}")

async def cmd_sendbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message: return
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"; args=context.args
        if not args or not args[0].replace(".","",1).isdigit():
            await update.message.reply_text(f"{Ewrn} <b>{R(ru,'Пример: /sendbalance 500','Example: /sendbalance 500')}</b>",parse_mode="HTML"); return
        amt=int(float(args[0])); u["balance"]=u.get("balance",0)+amt; save_db(db)
        bal_new=u["balance"]
        await update.message.reply_text(f"{Ech} <b>{R(ru,f'Баланс пополнен на {amt} RUB!',f'Balance topped up by {amt} RUB!')}</b>\n{Ebal} <b>{R(ru,'Баланс','Balance')}: {bal_new} RUB</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_sendbalance: {e}")

async def cmd_addrep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message: return
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"; args=context.args
        if not args or not args[0].lstrip("-").isdigit():
            await update.message.reply_text(f"{Ewrn} <b>{R(ru,'Пример: /addrep 100','Example: /addrep 100')}</b>",parse_mode="HTML"); return
        amt=int(args[0]); u["reputation"]=u.get("reputation",0)+amt; save_db(db)
        rep_new=u["reputation"]
        await update.message.reply_text(f"{Ech} <b>{R(ru,f'Репутация +{amt}!',f'Reputation +{amt}!')}</b>\n{Etph} <b>{R(ru,'Репутация','Reputation')}: {rep_new}</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_addrep: {e}")

async def cmd_setdeals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message: return
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"; args=context.args
        if not args or not args[0].isdigit():
            await update.message.reply_text(f"{Ewrn} <b>{R(ru,'Пример: /setdeals 50','Example: /setdeals 50')}</b>",parse_mode="HTML"); return
        n=int(args[0]); u["total_deals"]=n; u["success_deals"]=n; save_db(db)
        await update.message.reply_text(f"{Ech} <b>{R(ru,f'Сделок: {n}',f'Deals: {n}')}</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_setdeals: {e}")

async def cmd_setturnover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message: return
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"; args=context.args
        if not args or not args[0].isdigit():
            await update.message.reply_text(f"{Ewrn} <b>{R(ru,'Пример: /setturnover 15000','Example: /setturnover 15000')}</b>",parse_mode="HTML"); return
        n=int(args[0]); u["turnover"]=n; save_db(db)
        await update.message.reply_text(f"{Ech} <b>{R(ru,f'Оборот: {n} RUB',f'Turnover: {n} RUB')}</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_setturnover: {e}")

async def cmd_add_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"; args=context.args
        if not args:
            await update.message.reply_text(f"{Ewrn} <b>{R(ru,'Укажите текст: /addreview Текст','Usage: /addreview Text')}</b>",parse_mode="HTML"); return
        rev_text=" ".join(args); u.setdefault("reviews",[]).append(rev_text); save_db(db)
        revs=u["reviews"]
        lines=[f"{Ech} <b>{R(ru,'Отзыв добавлен!','Review added!')}</b>\n"]
        for i,r in enumerate(revs,1): lines.append(f"<b>{i}.</b> {r}")
        lines.append(f"\n<i>{R(ru,'Удалить: /delreview [номер]','Delete: /delreview [number]')}</i>")
        await update.message.reply_text("\n".join(lines),parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_add_review: {e}")

async def cmd_del_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"; args=context.args; reviews=u.get("reviews",[])
        if not args or not args[0].isdigit():
            await update.message.reply_text(f"{Ewrn} <b>{R(ru,'Укажите номер: /delreview 1','Usage: /delreview 1')}</b>",parse_mode="HTML"); return
        idx=int(args[0])-1
        if idx<0 or idx>=len(reviews):
            await update.message.reply_text(f"{Ewrn} <b>{R(ru,f'Нет отзыва №{idx+1}.',f'No review #{idx+1}.')}</b>",parse_mode="HTML"); return
        removed=reviews.pop(idx); save_db(db)
        await update.message.reply_text(f"{Ech} <b>{R(ru,'Отзыв удалён!','Review deleted!')}</b>\n<blockquote>{removed}</blockquote>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_del_review: {e}")

async def cmd_my_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"; reviews=u.get("reviews",[])
        if not reviews:
            await update.message.reply_text(f"{Estr} <b>{R(ru,'Отзывов нет.','No reviews.')}</b>",parse_mode="HTML"); return
        lines=[f"{Estr} <b>{R(ru,'Мои отзывы:','My reviews:')}</b>\n"]
        for i,r in enumerate(reviews,1): lines.append(f"<b>{i}.</b> {r}")
        await update.message.reply_text("\n".join(lines),parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_my_reviews: {e}")

async def cmd_clear_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message: return
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"
        u["reviews"]=[]; save_db(db)
        await update.message.reply_text(f"{Ech} <b>{R(ru,'Все отзывы удалены!','All reviews deleted!')}</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_clear_reviews: {e}")

async def cmd_reset_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message: return
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"
        u["reviews"]=[]; u["total_deals"]=0; u["success_deals"]=0; u["turnover"]=0; u["reputation"]=0
        save_db(db)
        await update.message.reply_text(f"{Ech} <b>{R(ru,'Все статы сброшены!','All stats reset!')}</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_reset_stats: {e}")

# ─── Callbacks ────────────────────────────────────────────────────────────────
async def on_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q=update.callback_query; await q.answer(); d=q.data
        logger.info(f"CALLBACK: uid={update.effective_user.id} d={d!r}")
        ud=context.user_data; uid=update.effective_user.id
        lang=get_lang(uid); ru=lang=="ru"

        # ── Навигация главного меню ──
        if d=="main_menu":
            ud.clear(); await show_main(update,context); return
        if d=="menu_profile":
            await show_profile(update,context); return
        if d=="menu_balance":
            await show_balance(update,context); return
        if d=="menu_my_deals":
            await show_my_deals(update,context); return
        if d=="menu_lang":
            await show_lang(update,context); return
        if d=="menu_top":
            await show_top(update,context); return
        if d=="menu_ref":
            await show_ref(update,context); return
        if d=="menu_req":
            await show_req(update,context); return

        # ── Создать сделку ──
        if d=="menu_deal":
            ud.clear()
            try: await q.message.delete()
            except: pass
            await update.effective_chat.send_message(
                f"{Epen} <b>{R(ru,'Создать сделку','Create Deal')}\n\n{R(ru,'Кто вы в этой сделке?','What is your role?')}</b>",
                parse_mode="HTML",reply_markup=role_kb(lang)); return

        if d in ("role_buyer","role_seller"):
            role="buyer" if d=="role_buyer" else "seller"
            db=load_db(); u=get_user(db,uid); reqs=u.get("requisites",{})
            if not any(reqs.get(f) for f in ("card","ton","stars")):
                bank=card_bank(lang)
                kb=InlineKeyboardMarkup([
                    [InlineKeyboardButton(R(ru,f"Карта / Телефон {bank}",f"Card / Phone {bank}"),icon_custom_emoji_id="5445353829304387411",callback_data="req_edit_card_buyer")],
                    [InlineKeyboardButton("TON",icon_custom_emoji_id="5264713049637409446",callback_data="req_edit_ton_buyer")],
                    [InlineKeyboardButton(R(ru,"Звёзды","Stars"),icon_custom_emoji_id="5267500801240092311",callback_data="req_edit_stars_buyer")],
                    [InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="menu_deal")],
                ])
                no_req_text=R(ru,
                    "Добавьте реквизиты для получения оплаты после сделки:",
                    "Add requisites to receive payment after the deal:")
                await update.effective_chat.send_message(
                    f"{Ewrn} <b>{no_req_text}</b>",parse_mode="HTML",reply_markup=kb)
                ud["creator_role"]=role; return
            # Реквизиты есть — сразу к типу сделки
            ud["creator_role"]=role
            try: await q.message.delete()
            except: pass
            await update.effective_chat.send_message(
                f"{Epen} <b>{R(ru,'Выберите тип сделки:','Choose deal type:')}</b>",
                parse_mode="HTML",reply_markup=types_kb(lang)); return



        TYPE_MAP={"dt_nft":"nft","dt_usr":"username","dt_str":"stars","dt_cry":"crypto","dt_prm":"premium"}
        if d in TYPE_MAP:
            ud["type"]=TYPE_MAP[d]; ud["step"]="partner"
            cr=ud.get("creator_role","seller")
            pp=R(ru,f"{ce('5893290369629556374','👤')} Введите @username продавца:",f"{ce('5893290369629556374','👤')} Enter seller @username:") if cr=="buyer" else R(ru,f"{ce('5893290369629556374','👤')} Введите @username покупателя:",f"{ce('5893290369629556374','👤')} Enter buyer @username:")
            try: await q.message.delete()
            except: pass
            msg=await update.effective_chat.send_message(
                f"<b>{pp}</b>\n\n<b>{R(ru,'Пример','Example')}:</b> <code>@username</code>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="menu_deal")]]))
            ud["last_msg"]=msg.message_id; return

        # ── Крипто валюта ──
        if d=="cry_ton":
            ud["currency"]="TON"; ud["step"]="currency"
            try: await q.message.delete()
            except: pass
            _cr=ud.get("creator_role","seller")
            _q=R(ru,"Выберите валюту для получения оплаты:","Choose payment currency:") if _cr=="seller" else R(ru,"Выберите валюту для оплаты:","Choose currency to pay:")
            msg=await update.effective_chat.send_message(
                f"💎 <b>{_q}</b>",
                parse_mode="HTML",reply_markup=pay_cur_kb(lang))
            ud["last_msg"]=msg.message_id; return

        if d=="cry_usd":
            ud["currency"]="USDT"; ud["step"]="currency"
            try: await q.message.delete()
            except: pass
            _cr=ud.get("creator_role","seller")
            _q=R(ru,"Выберите валюту для получения оплаты:","Choose payment currency:") if _cr=="seller" else R(ru,"Выберите валюту для оплаты:","Choose currency to pay:")
            msg=await update.effective_chat.send_message(
                f"💵 <b>{_q}</b>",
                parse_mode="HTML",reply_markup=pay_cur_kb(lang))
            ud["last_msg"]=msg.message_id; return

        # ── Период Premium ──
        if d in ("prm_3","prm_6","prm_12"):
            prru={"prm_3":"3 месяца","prm_6":"6 месяцев","prm_12":"12 месяцев"}
            pren={"prm_3":"3 months","prm_6":"6 months","prm_12":"12 months"}
            ud["premium_period"]=(prru if ru else pren)[d]; ud["step"]="currency"
            try: await q.message.delete()
            except: pass
            msg=await update.effective_chat.send_message(
                f"{Eprem} <b>{R(ru,'Выберите валюту оплаты:','Choose payment currency:')}</b>",
                parse_mode="HTML",reply_markup=pay_cur_kb(lang))
            ud["last_msg"]=msg.message_id; return

        # ── Валюта оплаты ──
        if d.startswith("pay_cur_"):
            pay_code=d[8:]
            pay_map={"ton":"TON","usdt":"USDT","rub":"RUB","stars":"Stars",
                     "kzt":"KZT","azn":"AZN","kgs":"KGS","uzs":"UZS",
                     "tjs":"TJS","byn":"BYN","uah":"UAH","gel":"GEL"}
            ud["pay_currency"]=pay_map.get(pay_code,pay_code.upper())
            ud["step"]="amount"
            try: await q.message.delete()
            except: pass
            msg=await update.effective_chat.send_message(
                f"{Emn} <b>{R(ru,'Введите сумму сделки:','Enter deal amount:')}</b>",
                parse_mode="HTML")
            ud["last_msg"]=msg.message_id; return

        # ── Валюта товара (nft/username/stars) ──
        if d.startswith("cur_"):
            ud["currency"]=CURMAP.get(d,d); ud["step"]="amount"
            cur_code=CURMAP.get(d,d)
            flag=CUR_FLAG.get(cur_code,"")
            name=cur_plain(cur_code, lang)
            try: await q.message.delete()
            except: pass
            msg=await update.effective_chat.send_message(
                f"<b>{R(ru,'Введите сумму сделки','Enter deal amount')} {flag} {name}:</b>",
                parse_mode="HTML")
            ud["last_msg"]=msg.message_id; return

        # ── Реквизиты ──
        if d=="req_del_menu":
            db=load_db(); u=get_user(db,uid); reqs=u.get("requisites",{})
            rows=[]
            if reqs.get("card"): rows.append([InlineKeyboardButton("💳 "+R(ru,"Удалить карту/телефон","Delete card/phone"),callback_data="req_del_card")])
            if reqs.get("ton"):  rows.append([InlineKeyboardButton("💎 "+R(ru,"Удалить TON","Delete TON"),callback_data="req_del_ton")])
            if reqs.get("stars"):rows.append([InlineKeyboardButton("⭐️ "+R(ru,"Удалить @username","Delete @username"),callback_data="req_del_stars")])
            rows.append([InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="menu_req")])
            await send_section(update,f"{Edl} <b>{R(ru,'Что удалить?','What to delete?')}</b>",InlineKeyboardMarkup(rows),section="profile"); return

        if d.startswith("req_del_"):
            field=d[8:]; db=load_db(); u=get_user(db,uid)
            u.setdefault("requisites",{}).pop(field,None); save_db(db)
            await show_req(update,context); return

        if d.startswith("req_edit_"):
            raw=d[9:]
            if raw.endswith("_buyer"):
                field=raw[:-6]
                ud["req_step"]=field; ud["req_after_buyer_deal"]=True
                bank=card_bank(lang)
                prompts={
                    "card": f"{Ecrd} <b>{R(ru,'Карта / Номер телефона','Card / Phone Number')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>{R(ru,'+79041751408','+12025550123')}</code></blockquote>",
                    "ton":  f"{Edm} <b>TON</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>UQDxxx...xxx</code></blockquote>",
                    "stars":f"{Est} <b>{R(ru,'Звёзды','Stars')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>@username</code></blockquote>",
                }
                await send_section(update,prompts.get(field,"?"),
                    InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="menu_deal")]]),section="profile"); return
            field=raw; bank=card_bank(lang)
            prompts={
                "card": f"{Ecrd} <b>{R(ru,'Карта / Номер телефона','Card / Phone Number')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>{R(ru,'+79041751408','+12025550123')}</code></blockquote>",
                "ton":  f"{Edm} <b>TON</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>UQDxxx...xxx</code></blockquote>",
                "stars":f"{Est} <b>{R(ru,'Звёзды','Stars')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>@username</code></blockquote>",
            }
            ud["req_step"]=field
            await send_section(update,prompts.get(field,"?"),
                InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="menu_req")]]),section="profile"); return

        if d.startswith("add_req_"):
            deal_id=d[8:]; ud["req_for_deal"]=deal_id; bank=card_bank(lang)
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton(R(ru,f"Карта / Телефон {bank}",f"Card / Phone {bank}"),icon_custom_emoji_id="5445353829304387411",callback_data=f"req_deal_card_{deal_id}")],
                [InlineKeyboardButton("TON",icon_custom_emoji_id="5264713049637409446",callback_data=f"req_deal_ton_{deal_id}")],
                [InlineKeyboardButton(R(ru,"Звёзды","Stars"),icon_custom_emoji_id="5267500801240092311",callback_data=f"req_deal_stars_{deal_id}")],
                [InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")],
            ])
            await send_section(update,f"{Ewrn} <b>{R(ru,'Добавьте реквизиты:','Add requisites:')}</b>",kb,section="deal_card"); return

        if d.startswith("req_deal_"):
            parts=d[9:].split("_",1); field=parts[0]; deal_id=parts[1] if len(parts)>1 else ""
            ud["req_step"]=field; ud["req_for_deal"]=deal_id; bank=card_bank(lang)
            prompts={
                "card": f"{Ecrd} <b>{R(ru,f'Карта / Телефон {bank}',f'Card / Phone {bank}')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>{R(ru,'+79041751408','+12025550123')}</code></blockquote>",
                "ton":  f"{Edm} <b>TON</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>UQDxxx...xxx</code></blockquote>",
                "stars":f"{Est} <b>{R(ru,'Звёзды','Stars')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>@username</code></blockquote>",
            }
            await send_section(update,prompts.get(field,"?"),
                InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data=f"add_req_{deal_id}")]]),section="deal_card"); return

        if d.startswith("lang_"):
            await set_lang(update,context,d[5:]); return

        # ── Баланс ──
        if d=="show_balance":
            try: await q.message.delete()
            except: pass
            await show_balance(update,context); return

        if d=="balance_topup":
            await send_section(update,
                f"{Emn} <b>{R(ru,'Выберите валюту пополнения:','Choose top-up currency:')}</b>",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton(R(ru,"Звёзды","Stars"),icon_custom_emoji_id="5267500801240092311",callback_data="topup_cur_stars")],
                    [InlineKeyboardButton(R(ru,"Карта / Телефон","Card / Phone"),icon_custom_emoji_id="5445353829304387411",callback_data="topup_cur_rub")],
                    [InlineKeyboardButton("TON - Tonkeeper",icon_custom_emoji_id="5397829221605191505",callback_data="topup_cur_ton_tonkeeper")],
                    [InlineKeyboardButton("TON - Crypto Bot",icon_custom_emoji_id="5242606681166220600",callback_data="topup_cur_ton_only")],
                    [InlineKeyboardButton("USDT - Tonkeeper",icon_custom_emoji_id="5397829221605191505",callback_data="topup_cur_usdt_tonkeeper")],
                    [InlineKeyboardButton("USDT - Crypto Bot",icon_custom_emoji_id="5242606681166220600",callback_data="topup_cur_usdt_only")],
                    [InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="menu_balance")],
                ]),section="balance"); return

        if d.startswith("topup_cur_"):
            method=d[10:]
            ud["topup_method"]=method
            within=R(ru,"Баланс пополнится в течение 5 минут.","Balance topped up within 5 minutes.")
            if method=="stars":
                txt2=(f"{Est} <b>{R(ru,'Пополнение Звёздами','Top up with Stars')}</b>\n\n"
                      f"<blockquote>{R(ru,'Отправьте звёзды менеджеру','Send stars to manager')}: {MANAGER_TAG}\n\n{within}</blockquote>")
            elif method=="rub":
                bank=card_bank(lang)
                txt2=(f"{Ecrd} <b>{R(ru,f'Пополнение - Карта / Телефон {bank}',f'Top up - Card / Phone {bank}')}</b>\n\n"
                      f"<blockquote>{R(ru,'Номер','Number')}: <code>{CARD_NUM}</code>\n{R(ru,'Получатель','Recipient')}: {CARD_NAME}\n{R(ru,'Банк','Bank')}: {bank}\n\n{within}</blockquote>")
            elif method=="ton_tonkeeper":
                txt2=(f"{Edm} <b>TON - Tonkeeper</b>\n\n"
                      f"<blockquote>{R(ru,'Адрес','Address')}:\n<code>{CRYPTO_ADDR}</code>\n\n{within}</blockquote>")
            elif method=="ton_only":
                txt2=(f"{Ecbt} <b>TON - Crypto Bot</b>\n\n"
                      f"<blockquote>{CRYPTO_BOT}\n\nID: <code>{uid}</code>\n\n{within}</blockquote>")
            elif method=="usdt_tonkeeper":
                txt2=(f"{Ebnk2} <b>USDT - Tonkeeper</b>\n\n"
                      f"<blockquote>{R(ru,'Адрес','Address')}:\n<code>{CRYPTO_ADDR}</code>\n\n{within}</blockquote>")
            elif method=="usdt_only":
                txt2=(f"{Ecbt} <b>USDT - Crypto Bot</b>\n\n"
                      f"<blockquote>{CRYPTO_BOT}\n\nID: <code>{uid}</code>\n\n{within}</blockquote>")
            else:
                txt2=f"<b>{method}</b>"
            await send_section(update,txt2,InlineKeyboardMarkup([
                [InlineKeyboardButton(R(ru,"✅ Я отправил","✅ I sent"),icon_custom_emoji_id="5274055917766202507",callback_data=f"topup_sent_{method}")],
                [InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="balance_topup")],
            ]),section="balance"); return

        if d.startswith("topup_sent_"):
            method=d[11:]; uname2=update.effective_user.username or str(uid)
            mmap={
                "stars":R(ru,"Звёзды","Stars"),
                "rub":R(ru,"Рубли","Rubles"),
                "crypto":"TON/USDT",
                "ton_only":"TON - Crypto Bot",
                "ton_tonkeeper":"TON - Tonkeeper",
                "usdt_only":"USDT - Crypto Bot",
                "usdt_tonkeeper":"USDT - Tonkeeper",
            }
            try:
                await context.bot.send_message(chat_id=ADMIN_ID,
                    text=f"{Ebl} <b>Пополнение - {mmap.get(method,method)}</b>\n👤 @{uname2} (<code>{uid}</code>)",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("✅ Пришло",callback_data=f"adm_topup_ok_{uid}"),
                        InlineKeyboardButton("❌ Не пришло",callback_data=f"adm_topup_no_{uid}"),
                    ]]))
            except: pass
            try: await q.edit_message_reply_markup(InlineKeyboardMarkup([
                [InlineKeyboardButton(R(ru,'⏳ Ожидание подтверждения...','⏳ Waiting for confirmation...'),callback_data="noop")],
                [InlineKeyboardButton(R(ru,'Главное меню','Main menu'),icon_custom_emoji_id="5316887736823591263",callback_data="main_menu")],
            ]))
            except: pass
            return

        if d.startswith("adm_topup_ok_"):
            if update.effective_user.id not in ADMIN_IDS: return
            target=d[13:]
            await q.edit_message_text(f"{Ech} <b>Пополнение подтверждено!</b>\n<code>{target}</code>",parse_mode="HTML")
            try:
                tl=get_lang(int(target)); tr=tl=="ru"
                await context.bot.send_message(chat_id=int(target),
                    text=f"{Ech} <b>{R(tr,'Баланс пополнен!','Balance topped up!')}</b>",parse_mode="HTML")
            except: pass
            return

        if d.startswith("adm_topup_no_"):
            if update.effective_user.id not in ADMIN_IDS: return
            target=d[13:]
            await q.edit_message_text(f"{Ewrn} <b>Не подтверждено.</b>\n<code>{target}</code>",parse_mode="HTML")
            return

        if d=="withdraw":
            db=load_db(); u=get_user(db,uid); reqs=u.get("requisites",{})
            if not any(reqs.get(f) for f in ("card","ton","stars")):
                await send_section(update,
                    f"{Ewrn} <b>{R(ru,'Для вывода добавьте реквизиты.','Add requisites to withdraw.')}</b>",
                    InlineKeyboardMarkup([
                        [InlineKeyboardButton(R(ru,"Добавить карту/телефон","Add card/phone"),icon_custom_emoji_id="5445353829304387411",callback_data="req_edit_card")],
                        [InlineKeyboardButton(R(ru,"Добавить TON","Add TON"),icon_custom_emoji_id="5264713049637409446",callback_data="req_edit_ton")],
                        [InlineKeyboardButton(R(ru,"Добавить @username","Add @username"),icon_custom_emoji_id="5267500801240092311",callback_data="req_edit_stars")],
                        [InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="menu_balance")],
                    ]),section="balance"); return
            await show_withdraw(update,context); return

        if d.startswith("withdraw_"):
            method=d[9:]
            prompts={"stars":R(ru,"@username для звёзд:","@username for stars:"),
                     "crypto":R(ru,"TON/USDT адрес:","TON/USDT address:"),
                     "card":R(ru,"Номер карты или телефона:","Card or phone number:")}
            ud["withdraw_method"]=method; ud["withdraw_step"]="req"
            await send_section(update,
                f"{Ewlt} <b>{R(ru,'Вывод','Withdraw')}</b>\n\n<blockquote>{prompts.get(method,'?')}</blockquote>",
                InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="withdraw")]]),section="balance"); return

        if d.startswith("rev_"):
            parts=d.split("_"); deal_id=parts[1]; role=parts[2]; stars_n=int(parts[3])
            ud["review_deal"]=deal_id; ud["review_role"]=role; ud["review_stars"]=stars_n; ud["review_step"]="text"
            await q.edit_message_text(f"⭐ {R(ru,'Оценка','Rating')}: {stars_n}/5\n\n{R(ru,'Напишите комментарий:','Write a comment:')}",parse_mode="HTML"); return

        if d.startswith("adm_del_rev_"):
            parts=d[12:].split("_",1); target_uid=parts[0]; ridx=int(parts[1]) if len(parts)>1 else -1
            db=load_db()
            if target_uid in db["users"] and 0<=ridx<len(db["users"][target_uid].get("reviews",[])):
                db["users"][target_uid]["reviews"].pop(ridx); save_db(db); await q.answer("Удалено")
                revs=db["users"][target_uid].get("reviews",[]); u2=db["users"][target_uid]; uname2=u2.get("username","?")
                if not revs:
                    await q.edit_message_text(f"<b>@{uname2}: отзывов нет</b>",parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]])); return
                lines=[f"{Estr} <b>Отзывы @{uname2} ({len(revs)}):</b>"]; rows2=[]
                for i,r in enumerate(revs):
                    lines.append(f"\n{i+1}. {r}")
                    rows2.append([InlineKeyboardButton(f"🗑 #{i+1}",callback_data=f"adm_del_rev_{target_uid}_{i}")])
                rows2.append([InlineKeyboardButton("🔙 Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")])
                await q.edit_message_text("\n".join(lines),parse_mode="HTML",reply_markup=InlineKeyboardMarkup(rows2)); return
            return

        if d.startswith("paid_"): await on_paid(update,context); return
        if d=="noop": return
        if d.startswith("adm_confirm_"): await adm_confirm(update,context); return
        if d.startswith("adm_decline_"): await adm_decline(update,context); return
        if d=="adm_back":
            try: await q.message.edit_text(f"{Edl} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())
            except: await q.message.reply_text(f"{Edl} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())
            return
        if d.startswith("adm_"): await handle_adm_cb(update,context); return

    except Exception as e: logger.error(f"on_cb ERROR d={q.data if 'q' in dir() else '?'}: {e}", exc_info=True)

# ─── Messages ─────────────────────────────────────────────────────────────────
async def on_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ud=context.user_data; uid=update.effective_user.id; lang=get_lang(uid); ru=lang=="ru"
        text=update.message.text.strip() if update.message.text else ""
        if uid in ADMIN_IDS and ud.get("adm_step"): await handle_adm_msg(update,context); return

        if ud.get("req_step") in ("card","ton","stars"):
            field=ud["req_step"]; db=load_db(); u=get_user(db,uid)
            err=None
            if field=="card":
                if ud.get("card_step")=="bank":
                    import re as _re3
                    if not text.strip() or not _re3.match(r"^[a-zA-Zа-яёА-ЯЁ0-9 ]+$", text.strip()):
                        bank_ex=R(ru,"Сбербанк, ВТБ, Тинькофф...","HSBC, Barclays, Lloyds...")
                        await update.message.reply_text(f"{Ewrn} <b>{R(ru,'Введите название банка:','Enter bank name:')}</b>\n<blockquote>{bank_ex}</blockquote>",parse_mode="HTML"); return
                    ud["card_bank_name"]=text.strip()
                    card_val=ud.pop("card_pending","")
                    bank_val=ud.pop("card_bank_name","")
                    text=f"{card_val}|{bank_val}"
                    ud.pop("card_step",None)
                else:
                    r=validate_card(text, lang)
                    if r is None:
                        if ru:
                            err="Введите номер телефона (+7...) или номер карты (16 цифр).\n\n<b>Пример:</b>\n<code>+79041751408</code>"
                        else:
                            err="Enter phone number (+1...) or card number (16 digits).\n\n<b>Example:</b>\n<code>+12025550123</code>"
                    else:
                        ud["card_pending"]=r; ud["card_step"]="bank"
                        bank_ex=R(ru,"Сбербанк, ВТБ, Тинькофф...","HSBC, Barclays, Lloyds, NatWest...")
                        await update.message.reply_text(
                            f"{Ecrd} <b>{R(ru,'Введите название банка:','Enter your bank name:')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')} {bank_ex}</blockquote>",
                            parse_mode="HTML"); return
            elif field=="ton":
                if not validate_ton_address(text):
                    err=R(ru,"Введите TON адрес.\n\n<b>Пример:</b>\n<code>UQDxxx...xxx</code>",
                          "Enter TON address.\n\n<b>Example:</b>\n<code>UQDxxx...xxx</code>")
            elif field=="stars":
                t2=text if text.startswith("@") else f"@{text}"
                cl,ec=validate_username(t2)
                if ec: err=R(ru,"Введите @username.\n\n<b>Пример:</b>\n<code>@username</code>",
                              "Enter @username.\n\n<b>Example:</b>\n<code>@username</code>")
                else: text=cl
            if err:
                await update.message.reply_text(f"{Ewrn} {err}",parse_mode="HTML"); return

            u.setdefault("requisites",{})[field]=text
            save_db(db); ud.pop("req_step",None)

            if ud.pop("req_after_buyer_deal",None):
                await update.message.reply_text(f"{Ech} <b>{R(ru,'Реквизиты сохранены!','Requisites saved!')}</b>",parse_mode="HTML")
                await update.effective_chat.send_message(
                    f"{Epen} <b>{R(ru,'Выберите тип сделки:','Choose deal type:')}</b>",
                    parse_mode="HTML",reply_markup=types_kb(lang)); return

            pending=ud.pop("req_for_deal",None) or ud.pop("pending_deal",None)
            if pending:
                db2=load_db(); d2=db2.get("deals",{}).get(pending)
                if d2:
                    await update.message.reply_text(f"{Ech} <b>{R(ru,'Реквизиты сохранены!','Requisites saved!')}</b>",parse_mode="HTML")
                    db2["deals"][pending]["buyer_uid"]=str(uid); save_db(db2)
                    cu=db2["users"].get(str(d2.get("user_id","")),{}).get("username","") if d2.get("user_id") else ""
                    ct=f"@{cu}" if cu else f"#{d2.get('user_id','')}"
                    bu=update.effective_user.username or ""; bt=f"@{bu}" if bu else f"#{uid}"
                    text2=build_deal_text(pending,d2,ct,bt,lang,joined=True)
                    seller_uid_p=d2.get("user_id","")
                    seller_uname_p=db2["users"].get(str(seller_uid_p),{}).get("username","") if seller_uid_p else ""
                    pu=f"https://t.me/{seller_uname_p}" if seller_uname_p else MANAGER_URL
                    kb=InlineKeyboardMarkup([
                        [InlineKeyboardButton(R(ru,'Я оплатил','I paid'),icon_custom_emoji_id="5274055917766202507",callback_data=f"paid_{pending}")],
                        [InlineKeyboardButton(R(ru,"Написать продавцу","Write to seller"),icon_custom_emoji_id="5287231198098117669",url=pu)],
                        [InlineKeyboardButton(R(ru,'Главное меню','Main menu'),icon_custom_emoji_id="5316887736823591263",callback_data="main_menu")],
                    ])
                    if seller_uid_p:
                        try:
                            sl2=get_lang(int(seller_uid_p)); rs2=sl2=="ru"
                            btag2=f"@{bu}" if bu else f"#{uid}"
                            await context.bot.send_message(chat_id=int(seller_uid_p),
                                text=f"{Ejn} <b>{R(rs2,'Покупатель присоединился!','Buyer joined!')}</b>\n<blockquote>{btag2}</blockquote>",parse_mode="HTML")
                        except: pass
                    await send_new(update,text2,kb,section="deal_card"); return

            await update.message.reply_text(f"{Ech} <b>{R(ru,'Реквизиты сохранены!','Requisites saved!')}</b>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,"Мои реквизиты","My Requisites"),callback_data="menu_req")]])); return

        if ud.get("withdraw_step")=="req":
            method=ud.get("withdraw_method","?"); db=load_db()
            u=get_user(db,uid); bal=u.get("balance",0); uname3=update.effective_user.username or str(uid)
            mnames={"stars":R(ru,"Звёзды","Stars"),"crypto":R(ru,"Крипта","Crypto"),"card":R(ru,"Карта","Card")}
            mname=mnames.get(method,method)
            try:
                await context.bot.send_message(chat_id=ADMIN_ID,
                    text=f"{Edm} <b>Вывод - {mname}</b>\n👤 @{uname3} (<code>{uid}</code>)\n💰 {bal} RUB\n\nРеквизиты: <code>{text}</code>",
                    parse_mode="HTML")
            except: pass
            ud.pop("withdraw_step",None); ud.pop("withdraw_method",None)
            await update.message.reply_text(
                f"{Ech} <b>{R(ru,'Запрос отправлен!','Request sent!')}</b>\n\n<blockquote>{R(ru,'Менеджер свяжется с вами.','Manager will contact you.')}</blockquote>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(R(ru,"Менеджер","Manager"),icon_custom_emoji_id="5287231198098117669",url=MANAGER_URL)],
                    [InlineKeyboardButton(R(ru,'Главное меню','Main menu'),icon_custom_emoji_id="5316887736823591263",callback_data="main_menu")],
                ])); return

        if ud.get("review_step")=="text":
            deal_id=ud.get("review_deal"); role=ud.get("review_role"); stars_r=ud.get("review_stars",5)
            db=load_db(); deal=db.get("deals",{}).get(deal_id,{})
            rev_text=f"⭐ {stars_r}/5 - {text}"
            saved=False
            if role=="s":
                buname=deal.get("partner","").lstrip("@").lower()
                buid=next((k for k,v in db.get("users",{}).items() if v.get("username","").lower()==buname),None)
                if not buid and deal.get("buyer_uid"): buid=deal.get("buyer_uid")
                if buid and buid in db["users"]:
                    db["users"][buid].setdefault("reviews",[]).append(rev_text); save_db(db); saved=True
            elif role=="b":
                suid=deal.get("user_id")
                if suid and suid in db.get("users",{}):
                    db["users"][suid].setdefault("reviews",[]).append(rev_text); save_db(db); saved=True
            for k in ("review_step","review_deal","review_role","review_stars"): ud.pop(k,None)
            await update.message.reply_text(f"{Ech} <b>{R(ru,'Отзыв сохранён!' if saved else 'Принят!','Review saved!' if saved else 'Received!')}</b>",parse_mode="HTML"); return

        dtype=ud.get("type"); step=ud.get("step")
        if not dtype or not step: return

        async def del_prev():
            try: await update.message.delete()
            except: pass
            if ud.get("last_msg"):
                try: await context.bot.delete_message(chat_id=update.effective_chat.id,message_id=ud["last_msg"])
                except: pass

        async def send_step(t2, kb=None):
            await del_prev()
            msg=await update.effective_chat.send_message(t2,parse_mode="HTML",reply_markup=kb)
            ud["last_msg"]=msg.message_id

        if step=="partner":
            t_raw = text.strip()
            if not t_raw.startswith("@"): t_raw = "@" + t_raw
            cl_p, ec_p = validate_username(t_raw)
            if ec_p:
                err_msg = R(ru,
                    "Некорректный @username. Минимум 4 символа, только латиница/цифры/подчёркивание.",
                    "Invalid @username. Min 4 chars, only latin/digits/underscore.")
                await update.message.reply_text(f"{Ewrn} <b>{err_msg}</b>\n\n<b>{R(ru,'Пример','Example')}:</b> <code>@username</code>",parse_mode="HTML"); return
            ud["partner"]=cl_p
            if dtype=="nft":
                ud["step"]="nft_link"
                await send_step(f"{Enft} <b>{R(ru,'Вставьте ссылку на NFT:','Paste NFT link:')}</b>\n\n<code>t.me/nft/...</code>")
            elif dtype=="username":
                ud["step"]="trade_usr"
                await send_step(f"👤 <b>{R(ru,'Введите ссылку (t.me/...):','Enter link (t.me/...):')}</b>")
            elif dtype=="stars":
                ud["step"]="stars_cnt"
                await send_step(f"⭐ <b>{R(ru,'Введите количество звёзд:','Enter stars count:')}</b>")
            elif dtype=="crypto":
                ud["step"]="cry_currency"
                await send_step(
                    f"💎 <b>{R(ru,'Выберите крипту для сделки:','Choose crypto for the deal:')}</b>",
                    InlineKeyboardMarkup([
                        [InlineKeyboardButton("TON",icon_custom_emoji_id="5264713049637409446",callback_data="cry_ton"),
                         InlineKeyboardButton("USDT",icon_custom_emoji_id="5201873447554145566",callback_data="cry_usd")],
                    ]))
            elif dtype=="premium":
                ud["step"]="prem_period"
                await send_step(f"{Eprem} <b>Telegram Premium\n\n{R(ru,'Выберите период:','Choose period:')}</b>",
                    InlineKeyboardMarkup([[
                        InlineKeyboardButton("3 "+R(ru,"мес.","mo"),icon_custom_emoji_id="5370784581341422520",callback_data="prm_3"),
                        InlineKeyboardButton("6 "+R(ru,"мес.","mo"),icon_custom_emoji_id="5370784581341422520",callback_data="prm_6"),
                        InlineKeyboardButton("12 "+R(ru,"мес.","mo"),icon_custom_emoji_id="5370784581341422520",callback_data="prm_12")]]))
            return

        if step=="nft_link":
            ok,em=validate_nft_link(text,dtype)
            if not ok:
                await update.message.reply_text(f"{Ewrn} <b>{R(ru,'Некорректная ссылка. Формат: t.me/nft/НазваниеНФТ','Invalid link. Format: t.me/nft/NFTName')}</b>",parse_mode="HTML"); return
            clean_link=text.strip()
            for prefix in ("https://","http://"):
                if clean_link.startswith(prefix): clean_link=clean_link[len(prefix):]; break
            if not clean_link.startswith("t.me/"): clean_link="t.me/"+clean_link
            ud["nft_link"]=clean_link; ud["step"]="currency"
            _cr=ud.get("creator_role","seller")
            _q=R(ru,"Выберите валюту для получения оплаты:","Choose payment currency:") if _cr=="seller" else R(ru,"Выберите валюту для оплаты:","Choose currency to pay:")
            await send_step(f"{Enft} <b>{_q}</b>",pay_cur_kb(lang)); return

        if step=="trade_usr":
            cl=text.strip().replace("https://","").replace("http://","")
            import re as _re
            ok_link = cl.startswith("t.me/") and len(cl[5:].strip("/"))>=4 and _re.fullmatch(r"[a-zA-Z0-9_]+", cl[5:].strip("/"))
            ok_at   = text.strip().startswith("@") and len(text.strip()[1:])>=4 and _re.fullmatch(r"[a-zA-Z0-9_]+", text.strip()[1:])
            if not ok_link and not ok_at:
                await update.message.reply_text(
                    f"{Ewrn} <b>{R(ru,'Введите корректную ссылку t.me/username или @username (мин. 4 символа).','Enter valid t.me/username or @username (min 4 chars).')}</b>",
                    parse_mode="HTML"); return
            ud["trade_username"]=text.strip(); ud["step"]="currency"
            _cr=ud.get("creator_role","seller")
            _q=R(ru,"Выберите валюту для получения оплаты:","Choose payment currency:") if _cr=="seller" else R(ru,"Выберите валюту для оплаты:","Choose currency to pay:")
            await send_step(f"{Eu} <b>{_q}</b>",pay_cur_kb(lang)); return

        if step=="stars_cnt":
            if not text.isdigit():
                await update.message.reply_text(f"{Ewrn} <b>{R(ru,'Только цифры!','Numbers only!')}</b>",parse_mode="HTML"); return
            ud["stars_count"]=text; ud["step"]="currency"
            _cr=ud.get("creator_role","seller")
            _q=R(ru,"Выберите валюту для получения оплаты:","Choose payment currency:") if _cr=="seller" else R(ru,"Выберите валюту для оплаты:","Choose currency to pay:")
            await send_step(f"{Est} <b>{_q}</b>",pay_cur_kb(lang)); return

        if step in ("cry_currency","prem_period","currency","pay_currency","pay_cur"):
            await update.message.reply_text(
                f"{Ewrn} <b>{R(ru,'Выберите вариант из кнопок выше.','Please choose an option from the buttons above.')}</b>",
                parse_mode="HTML"); return

        if step=="amount":
            ca=text.replace(" ","").replace(",",".")
            try:
                v=float(ca)
                if v<=0: raise ValueError
            except:
                await update.message.reply_text(f"{Ewrn} <b>{R(ru,'Введите число больше 0. Пример: 500','Enter number greater than 0. Example: 500')}</b>",parse_mode="HTML")
                return
            ud["amount"]=ca
            dtype2=ud.get("type","")
            # Валюта уже выбрана через pay_cur_kb — финализируем
            await del_prev()
            await finalize_deal(update,context)
            return

    except Exception as e: logger.error(f"on_msg ERROR: {e}", exc_info=True)

# ─── Finalize deal ────────────────────────────────────────────────────────────
async def finalize_deal(update, context):
    try:
        ud=context.user_data; db=load_db()
        dtype=ud.get("type","?"); partner=ud.get("partner","-")
        currency=ud.get("currency","-"); amount=ud.get("amount","-")
        pay_currency=ud.get("pay_currency", currency)
        creator_role=ud.get("creator_role","seller"); user=update.effective_user

        data={}
        for key in ("nft_link","trade_username","stars_count","premium_period"):
            if ud.get(key) is not None: data[key]=ud[key]

        deal_id=gen_deal_id(db)
        db["deals"][deal_id]={
            "user_id":str(user.id),"type":dtype,"partner":partner,
            "currency":pay_currency,"amount":amount,"status":"pending",
            "created":datetime.now().isoformat(),"data":data,"creator_role":creator_role,
            "deal_currency":currency,
        }
        add_log(db,"Новая сделка",deal_id=deal_id,uid=user.id,username=user.username or "",
            extra=f"{dtype} | {amount} {pay_currency} | {creator_role}")
        save_db(db)
        if db.get("logs"): await send_log_msg(context,db,db["logs"][-1])

        cu=db["users"].get(str(user.id),{}).get("username","")
        creator_tag=f"@{cu}" if cu else f"@{user.username or str(user.id)}"
        partner_tag=partner
        lang=get_lang(user.id); ru=lang=="ru"

        join_link=f"https://t.me/{BOT_USERNAME}?start=deal_{deal_id}"
        ll=R(ru,"Ссылка для партнёра","Link for partner")
        lbl_send=R(ru,"Отправить ссылку партнёру","Send link to partner")
        text=f"{ce('5893368370530621889','⏳')} <b>{R(ru,'Сделка создана! Ожидание партнёра...','Deal created! Waiting for partner...')}</b>\n\n"
        text+=f"🔗 <b>{ll}:</b>\n<code>{join_link}</code>"
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton(lbl_send,icon_custom_emoji_id="5877465816030515018",switch_inline_query=f"Заходи в сделку\n{join_link}")],
            [InlineKeyboardButton(R(ru,'Главное меню','Main menu'),icon_custom_emoji_id="5316887736823591263",callback_data="main_menu")]
        ])
        await send_new(update,text,kb,section="deal_card")

        pname=partner.lstrip("@").lower() if partner.startswith("@") else None
        if pname:
            puid=next((k for k,v in db["users"].items() if v.get("username","").lower()==pname),None)
            if puid:
                try:
                    pl=get_lang(int(puid)); pr=pl=="ru"
                    partner_tag2=f"@{db['users'][puid].get('username','')}" if db["users"][puid].get("username") else f"#{puid}"
                    txt2=build_deal_text(deal_id,db["deals"][deal_id],creator_tag,partner_tag2,pl,joined=False)
                    join_link=f"https://t.me/{BOT_USERNAME}?start=deal_{deal_id}"
                    txt2+=f"\n\n🤝 <b>{R(pr,'Нажмите чтобы присоединиться:','Click to join:')}</b>\n<code>{join_link}</code>"
                    kb2=InlineKeyboardMarkup([
                        [InlineKeyboardButton(R(pr,"Присоединиться","Join"),icon_custom_emoji_id="5902335789798265487",url=join_link)],
                        [InlineKeyboardButton(R(pr,"Главное меню","Main menu"),callback_data="main_menu")]
                    ])
                    await context.bot.send_message(chat_id=int(puid),text=txt2,parse_mode="HTML",reply_markup=kb2)
                except Exception as e: logger.error(f"notify partner: {e}")

        context.user_data.clear()
    except Exception as e: logger.error(f"finalize_deal: {e}")

# ─── on_paid ──────────────────────────────────────────────────────────────────
async def on_paid(update, context):
    try:
        q=update.callback_query; buyer=update.effective_user
        bl=get_lang(buyer.id); rb=bl=="ru"
        await q.answer(R(rb,"Отправлено!","Sent!"))
        deal_id=q.data[5:]; btag=f"@{buyer.username}" if buyer.username else str(buyer.id)
        db=load_db(); d=db.get("deals",{}).get(deal_id,{})
        amt=d.get("amount","-"); cur=d.get("currency","-")
        suid=d.get("user_id"); sl2=get_lang(int(suid)) if suid else "ru"; rs2=sl2=="ru"
        paid_text=f"{Ebl} <b>'Я оплатил'</b>\n\n{Ecrd} {btag} (<code>{buyer.id}</code>)\n{Emn} {amt} {cur}\n\nПроверьте оплату:"
        paid_kb=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Пришла",callback_data=f"adm_confirm_{deal_id}"),
            InlineKeyboardButton("❌ Не пришла",callback_data=f"adm_decline_{deal_id}")
        ]])
        try:
            await context.bot.send_message(chat_id=ADMIN_ID,text=paid_text,parse_mode="HTML",reply_markup=paid_kb)
        except Exception as e: logger.error(f"on_paid admin: {e}")
        add_log(db,"Оплачено",deal_id=deal_id,uid=buyer.id,username=buyer.username or "",extra=f"{amt} {cur}")
        save_db(db)
        if db.get("logs"): await send_log_msg(context,db,db["logs"][-1])
        seller=d.get("user_id")
        if seller and seller!=str(buyer.id):
            try:
                await context.bot.send_message(chat_id=int(seller),
                    text=f"{Ebl} <b>{R(rs2,'Покупатель оплатил!','Buyer paid!')}</b>\n{btag}\n{amt} {cur}",parse_mode="HTML")
            except: pass
        try:
            await q.edit_message_reply_markup(InlineKeyboardMarkup([
                [InlineKeyboardButton(R(rb,'⏳ Ожидание подтверждения...','⏳ Waiting for confirmation...'),callback_data="noop")],
                [InlineKeyboardButton(R(rb,"Главное меню","Main menu"),callback_data="main_menu")]
            ]))
        except: pass
    except Exception as e: logger.error(f"on_paid: {e}")

# ─── adm_confirm / decline ────────────────────────────────────────────────────
async def adm_confirm(update, context):
    try:
        q=update.callback_query; await q.answer()
        if update.effective_user.id not in ADMIN_IDS: return
        deal_id=q.data[12:]; db=load_db()
        if deal_id not in db.get("deals",{}): return
        db["deals"][deal_id]["status"]="confirmed"; d=db["deals"][deal_id]
        s=d.get("user_id"); amt_str=d.get("amount","0"); dtype=d.get("type",""); dd=d.get("data",{})
        try: amt_num=float(amt_str)
        except: amt_num=0
        if s and s in db["users"]:
            db["users"][s]["success_deals"]=db["users"][s].get("success_deals",0)+1
            db["users"][s]["total_deals"]=db["users"][s].get("total_deals",0)+1
            db["users"][s]["turnover"]=db["users"][s].get("turnover",0)+int(amt_num)
        ilink=""
        if dtype=="nft" and dd.get("nft_link"): ilink=f"\n🔗 {dd['nft_link']}"
        elif dtype=="username" and dd.get("trade_username"): ilink=f"\n🔗 {dd['trade_username']}"
        seller_uname=db["users"].get(s,{}).get("username","?") if s else "?"
        add_log(db,"Подтверждено",deal_id=deal_id,uid=s,username=seller_uname,extra=f"{amt_str} {d.get('currency','')}")
        if s and s in db["users"]:
            ref_uid=db["users"][s].get("ref_by")
            if ref_uid and ref_uid in db["users"] and amt_num>0:
                bonus=int(amt_num*0.03)
                if bonus>0:
                    db["users"][ref_uid]["ref_earned"]=db["users"][ref_uid].get("ref_earned",0)+bonus
                    db["users"][ref_uid]["balance"]=db["users"][ref_uid].get("balance",0)+bonus
                    try:
                        rl=get_lang(int(ref_uid)); rr=rl=="ru"
                        await context.bot.send_message(chat_id=int(ref_uid),
                            text=f"{Emn} <b>{R(rr,'Реферальный бонус!','Referral bonus!')}</b>\n<blockquote>+{bonus} RUB (3%)</blockquote>",parse_mode="HTML")
                    except: pass
        save_db(db)
        if db.get("logs"): await send_log_msg(context,db,db["logs"][-1])
        try:
            log_chat=db.get("log_chat_id")
            if log_chat:
                buyer_uid_post=d.get("buyer_uid")
                if not buyer_uid_post:
                    for u_p,ud_p in db.get("users",{}).items():
                        if ud_p.get("username","").lower()==d.get("partner","").lstrip("@").lower():
                            buyer_uid_post=u_p; break
                buyer_uname_post=db["users"].get(buyer_uid_post,{}).get("username","") if buyer_uid_post else ""
                buyer_link_post=f"@{buyer_uname_post}" if buyer_uname_post else d.get("partner","?")
                nft_link_post=dd.get("nft_link","") if dtype=="nft" else dd.get("trade_username","") if dtype=="username" else ""
                link_str=f"\n{Eln} {nft_link_post}" if nft_link_post else ""
                post_text=(
                    f"{ce('5258262708838472996','🔥')} <b>Новый мамонтёнок!</b>\n\n"
                    f"👤 {buyer_link_post}\n"
                    f"💰 <b>{amt_str} {d.get('currency','')}</b>"
                    f"{link_str}"
                )
                await context.bot.send_message(chat_id=int(log_chat),text=post_text,parse_mode="HTML")
                extra_grp=db.get("extra_group_id")
                if extra_grp:
                    try:
                        await context.bot.send_message(chat_id=int(extra_grp),text=post_text,parse_mode="HTML")
                    except Exception as eg: logger.error(f"extra_group post: {eg}")
        except Exception as e: logger.error(f"confirm group post: {e}")
        try: await q.edit_message_text(f"{Ech} <b>Подтверждено!</b>\n{d.get('amount')} {d.get('currency')}{ilink}",parse_mode="HTML")
        except: pass
        if s:
            try:
                sl=get_lang(int(s)); rs=sl=="ru"
                await context.bot.send_message(chat_id=int(s),
                    text=f"{Ech} <b>{R(rs,'Сделка завершена!','Deal completed!')}</b>",parse_mode="HTML")
            except: pass
        buyer_uid=d.get("buyer_uid")
        if not buyer_uid:
            for u_,ud_ in db.get("users",{}).items():
                if ud_.get("username","").lower()==d.get("partner","").lstrip("@").lower(): buyer_uid=u_; break
        if buyer_uid:
            try:
                bl2=get_lang(int(buyer_uid)); rb2=bl2=="ru"
                await context.bot.send_message(chat_id=int(buyer_uid),
                    text=f"{Ech} <b>{R(rb2,'Оплата подтверждена!','Payment confirmed!')}</b>",parse_mode="HTML")
            except: pass
    except Exception as e: logger.error(f"adm_confirm: {e}")

async def adm_decline(update, context):
    try:
        q=update.callback_query; await q.answer()
        if update.effective_user.id not in ADMIN_IDS: return
        deal_id=q.data[12:]; db=load_db(); d=db.get("deals",{}).get(deal_id,{})
        try:
            await q.edit_message_text(
                f"{Ewrn} <b>Не подтверждено.</b>\n<code>{deal_id}</code>\n💰 {d.get('amount','-')} {d.get('currency','-')}",
                parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Всё же пришла",callback_data=f"adm_confirm_{deal_id}")]]))
        except: pass
    except Exception as e: logger.error(f"adm_decline: {e}")

# ─── Sections ─────────────────────────────────────────────────────────────────
async def show_balance(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=get_lang(uid); ru=lang=="ru"; bal=u.get("balance",0)
        await send_section(update,
            f"{Ewlt} <b>{R(ru,'Пополнить / Вывод','Top Up / Withdraw')}</b>\n\n"
            f"<blockquote>{Ebal} <b>{R(ru,'Баланс','Balance')}: {bal} RUB</b></blockquote>",
            InlineKeyboardMarkup([
                [InlineKeyboardButton(R(ru,"Пополнить","Top Up"),icon_custom_emoji_id="5258043150110301407",callback_data="balance_topup")],
                [InlineKeyboardButton(R(ru,"Вывод","Withdraw"),icon_custom_emoji_id="5893382531037794941",callback_data="withdraw")],
                [InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")],
            ]),section="balance")
    except Exception as e: logger.error(f"show_balance: {e}")

async def show_lang(update, context):
    try:
        uid=update.effective_user.id; lang=get_lang(uid); ru=lang=="ru"
        rows=[
            [InlineKeyboardButton("Русский",icon_custom_emoji_id="5258115571848846212",callback_data="lang_ru")],
            [InlineKeyboardButton("English",icon_custom_emoji_id="5258115571848846212",callback_data="lang_en")],
        ]
        rows.append([InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")])
        await send_section(update,
            f"<b>{Egm} {R(ru,'Выберите язык:','Select language:')}</b>",
            InlineKeyboardMarkup(rows),section="main")
    except Exception as e: logger.error(f"show_lang: {e}")

async def set_lang(update, context, lang):
    try:
        db=load_db(); u=get_user(db,update.effective_user.id); u["lang"]=lang; save_db(db)
        await update.callback_query.answer("OK")
        await show_main(update,context)
    except Exception as e: logger.error(f"set_lang: {e}")

async def show_profile(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=get_lang(uid); ru=lang=="ru"
        uname=update.effective_user.username or "-"
        status=u.get("status","")
        sl=f"\n<blockquote>{R(ru,'Статус','Status')}: {status}</blockquote>" if status else ""
        reviews=u.get("reviews",[])
        rv=""
        if reviews:
            rv_lines=[]
            for r in reviews[-10:]:
                import re as _re2
                m=_re2.search(r'(\d)/5',r)
                stars_num=int(m.group(1)) if m else 5
                star_str=ce("5321485469249198987","⭐")*stars_num
                rv_lines.append(f"{star_str} {r}")
            rv=f"\n\n{Estr} <b>{R(ru,f'Отзывы ({len(reviews)})',f'Reviews ({len(reviews)})')}</b>\n<blockquote>"+'\n'.join(rv_lines)+'</blockquote>'
        text=(f"{Ecwn} <b>{R(ru,'Профиль','Profile')}</b>{sl}\n\n"
              f"👤 @{uname}\n"
              f"{Ebal} {R(ru,'Баланс','Balance')}: <b>{u.get('balance',0)} RUB</b>\n"
              f"{Estr} {R(ru,'Сделок','Deals')}: <b>{u.get('total_deals',0)}</b>\n"
              f"{Ech} {R(ru,'Успешных','Successful')}: <b>{u.get('success_deals',0)}</b>\n"
              f"{Emn} {R(ru,'Оборот','Turnover')}: <b>{u.get('turnover',0)} RUB</b>{rv}")
        await send_section(update,text,InlineKeyboardMarkup([
            [InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")]
        ]),section="profile")
    except Exception as e: logger.error(f"show_profile: {e}")

async def show_ref(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid); save_db(db)
        db=load_db(); u=db["users"][str(uid)]; lang=get_lang(uid); ru=lang=="ru"
        ref_link=f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"
        rc=u.get("ref_count",0); re=u.get("ref_earned",0)
        refs=[v.get("username","?") for v in db.get("users",{}).values() if v.get("ref_by")==str(uid)]
        refs_str=""
        if refs: refs_str="\n\n"+R(ru,"Рефералы","Referrals")+":\n"+"\n".join(f"{Esrk} @{r}" if r and r!="?" else f"{Esrk} #?" for r in refs[-10:])
        text=(f"{Ejn} <b>{R(ru,'Реферальная программа','Referral Program')}</b>\n\n"
              f"<blockquote>🤝 {R(ru,'Приглашайте друзей - 3% с каждой их сделки!','Invite friends - 3% from each deal!')}\n\n"
              f"{Eu} {R(ru,'Приглашено','Invited')}: <b>{rc}</b>\n"
              f"{Ebal} {R(ru,'Заработано','Earned')}: <b>{re} RUB</b>{refs_str}</blockquote>\n\n"
              f"{Esrk} {R(ru,'Ваша ссылка:','Your link:')}\n<code>{ref_link}</code>")
        await send_section(update,text,InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")]]),section="ref")
    except Exception as e: logger.error(f"show_ref: {e}")

async def show_req(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=get_lang(uid); ru=lang=="ru"; reqs=u.get("requisites",{})
        card=reqs.get("card"); ton=reqs.get("ton"); stars=reqs.get("stars")
        bank=card_bank(lang)

        lines=[f"{Ecwn} <b>{R(ru,'Мои реквизиты','My Requisites')}</b>\n"]
        lines.append(f"{Ecrd} <b>{R(ru,'Карта / Телефон','Card / Phone')}:</b>")
        if card:
            if "|" in card:
                card_num,card_bnk=card.split("|",1)
            else:
                card_num=card; card_bnk=bank
            lines.append(f"<blockquote>{R(ru,'Номер','Number')}: <code>{card_num}</code>\n{R(ru,'Банк','Bank')}: {card_bnk}</blockquote>")
        else:
            lines.append(f"<blockquote>{R(ru,'Не добавлена','Not added')}</blockquote>")
        lines.append(f"\n{Eton} <b>TON:</b>")
        lines.append(f"<blockquote><code>{ton}</code></blockquote>" if ton else f"<blockquote>{R(ru,'Не добавлен','Not added')}</blockquote>")
        lines.append(f"\n{Est} <b>{R(ru,'Звёзды','Stars')}:</b>")
        lines.append(f"<blockquote><code>{stars}</code></blockquote>" if stars else f"<blockquote>{R(ru,'Не добавлен','Not added')}</blockquote>")

        rows=[]
        if card:
            rows.append([InlineKeyboardButton(R(ru,"✏️ Изменить","✏️ Edit"),icon_custom_emoji_id="5197371802136892976",callback_data="req_edit_card"),
                         InlineKeyboardButton(R(ru,"🗑 Удалить","🗑 Delete"),icon_custom_emoji_id="5443127283898405358",callback_data="req_del_card")])
        else:
            rows.append([InlineKeyboardButton(R(ru,"➕ Добавить карту / телефон","➕ Add card / phone"),icon_custom_emoji_id="5445353829304387411",callback_data="req_edit_card")])
        if ton:
            rows.append([InlineKeyboardButton(R(ru,"✏️ Изменить","✏️ Edit"),icon_custom_emoji_id="5197371802136892976",callback_data="req_edit_ton"),
                         InlineKeyboardButton(R(ru,"🗑 Удалить","🗑 Delete"),icon_custom_emoji_id="5443127283898405358",callback_data="req_del_ton")])
        else:
            rows.append([InlineKeyboardButton(R(ru,"➕ Добавить TON","➕ Add TON"),icon_custom_emoji_id="5264713049637409446",callback_data="req_edit_ton")])
        if stars:
            rows.append([InlineKeyboardButton(R(ru,"✏️ Изменить","✏️ Edit"),icon_custom_emoji_id="5197371802136892976",callback_data="req_edit_stars"),
                         InlineKeyboardButton(R(ru,"🗑 Удалить","🗑 Delete"),icon_custom_emoji_id="5443127283898405358",callback_data="req_del_stars")])
        else:
            rows.append([InlineKeyboardButton(R(ru,"➕ Добавить Звёзды","➕ Add Stars"),icon_custom_emoji_id="5267500801240092311",callback_data="req_edit_stars")])
        rows.append([InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")])
        await send_section(update,"\n".join(lines),InlineKeyboardMarkup(rows),section="profile")
    except Exception as e: logger.error(f"show_req: {e}")

async def show_my_deals(update, context):
    try:
        db=load_db(); uid=str(update.effective_user.id); lang=get_lang(int(uid)); ru=lang=="ru"
        deals={k:v for k,v in db.get("deals",{}).items() if v.get("user_id")==uid}
        if not deals:
            await send_section(update,
                f"{Edl} <b>{R(ru,'Мои сделки','My Deals')}\n\n{R(ru,'Пока нет сделок.','No deals yet.')}</b>",
                InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")]]),section="my_deals"); return
        SNAMES={
            "pending":   R(ru,f"{Esrk} Ожидает",  f"{Esrk} Pending"),
            "confirmed": R(ru,f"{Ech} Завершена",  f"{Ech} Completed"),
        }
        lines=[f"{Edl} <b>{R(ru,'Мои сделки','My Deals')} ({len(deals)}):</b>\n"]
        for i,(did,dv) in enumerate(list(deals.items())[-10:],start=1):
            tn=tname(dv.get("type",""),lang)
            cur_d=cur_plain(dv.get("currency",""),lang)
            s=SNAMES.get(dv.get("status",""),dv.get("status",""))
            lines.append(f"<b>{i}. {tn} · {dv.get('amount')} {cur_d} · {s}</b>")
        await send_section(update,"\n".join(lines),
            InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")]]),section="my_deals")
    except Exception as e: logger.error(f"show_my_deals: {e}")

async def show_top(update, context):
    try:
        lang=get_lang(update.effective_user.id); ru=lang=="ru"
        TOP=[
            ("@al***ndr",8450,312),("@ie***ym",6380,278),("@ma***ov",5910,241),
            ("@kr***na",4290,198),("@pe***ko",3870,175),("@se***ev",3240,152),
            ("@an***va",2810,134),("@vi***or",2390,117),("@dm***iy",1970,98),("@ni***la",1540,83)
        ]
        dw=R(ru,"сделок","deals")
        lines=[f"<b>{Ecwn} {R(ru,'Топ продавцов Gift Deals','Gift Deals Top Sellers')}</b>\n"]
        for i,(u2,a,dd) in enumerate(TOP):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            lines.append(f"<b>{medal} {u2} - ${a} · {dd} {dw}</b>")
        lines.append(f"\n<b>{CF} {R(ru,'6500+ сделок · оборот $48,200','6500+ deals · $48,200 turnover')}</b>")
        await send_section(update,"\n".join(lines),
            InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="main_menu")]]),section="top")
    except Exception as e: logger.error(f"show_top: {e}")

async def show_withdraw(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=get_lang(uid); ru=lang=="ru"; bal=u.get("balance",0)
        if bal<=0:
            await send_section(update,
                f"{Ewrn} <b>{R(ru,'Недостаточно средств.','Insufficient balance.')}</b>\n\n<blockquote>{R(ru,'Баланс','Balance')}: {bal} RUB</blockquote>",
                InlineKeyboardMarkup([[InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="menu_balance")]]),section="balance"); return
        reqs=u.get("requisites",{})
        rows=[]
        if reqs.get("ton"): rows.append([InlineKeyboardButton("💎 TON/USDT → "+reqs["ton"][:12]+"...",icon_custom_emoji_id="5264713049637409446",callback_data="withdraw_crypto")])
        else: rows.append([InlineKeyboardButton("💎 TON / USDT",icon_custom_emoji_id="5264713049637409446",callback_data="withdraw_crypto")])
        if reqs.get("stars"): rows.append([InlineKeyboardButton("⭐️ "+R(ru,"Звёзды → ","Stars → ")+reqs["stars"],icon_custom_emoji_id="5267500801240092311",callback_data="withdraw_stars")])
        else: rows.append([InlineKeyboardButton("⭐️ "+R(ru,"Звёзды","Stars"),icon_custom_emoji_id="5267500801240092311",callback_data="withdraw_stars")])
        if reqs.get("card"): rows.append([InlineKeyboardButton("💳 "+R(ru,"Карта → ","Card → ")+reqs["card"][:12]+"...",icon_custom_emoji_id="5445353829304387411",callback_data="withdraw_card")])
        else: rows.append([InlineKeyboardButton("💳 "+R(ru,"Карта / Телефон","Card / Phone"),icon_custom_emoji_id="5445353829304387411",callback_data="withdraw_card")])
        rows.append([InlineKeyboardButton(R(ru,'Назад','Back'),icon_custom_emoji_id="5877629862306385808",callback_data="menu_balance")])
        await send_section(update,
            f"{Ewlt} <b>{R(ru,'Вывод средств','Withdraw')}</b>\n\n<blockquote>{Ebal} {R(ru,'Баланс','Balance')}: {bal} RUB</blockquote>",
            InlineKeyboardMarkup(rows),section="balance")
    except Exception as e: logger.error(f"show_withdraw: {e}")

# ─── Admin ────────────────────────────────────────────────────────────────────
def adm_kb():
    db=load_db(); hidden=db.get("log_hidden",False)
    tl="Логи: открыты" if not hidden else "Логи: скрыты"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Управление пользователем",callback_data="adm_user")],
        [InlineKeyboardButton("Баннеры",callback_data="adm_banners")],
        [InlineKeyboardButton("Описание меню",callback_data="adm_menu_desc")],
        [InlineKeyboardButton("Список сделок",callback_data="adm_deals")],
        [InlineKeyboardButton("Логи",callback_data="adm_logs"),InlineKeyboardButton(tl,callback_data="adm_toggle_hidden")],
        [InlineKeyboardButton("Лог-канал",callback_data="adm_log_channel"),InlineKeyboardButton("Шаблоны логов",callback_data="adm_log_templates")],
    ])

def adm_banners_kb(db=None):
    if db is None: db=load_db()
    banners=db.get("banners",{})
    rows=[]
    for key,name in BANNER_SECTIONS.items():
        b=banners.get(key) or {}
        has=bool(b.get("photo") or b.get("video") or b.get("gif") or b.get("text"))
        if not has and key=="main":
            has=bool(db.get("banner_photo") or db.get("banner_video") or db.get("banner_gif") or db.get("banner"))
        status="+" if has else "-"
        rows.append([
            InlineKeyboardButton(f"{status} {name}",callback_data=f"adm_banner_{key}"),
            InlineKeyboardButton("X",callback_data=f"adm_banner_del_{key}") if has else InlineKeyboardButton(" ",callback_data="noop"),
        ])
    rows.append([InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")])
    return InlineKeyboardMarkup(rows)

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    if update.effective_user.id not in ADMIN_IDS: return
    context.user_data.clear(); context.user_data["adm"]=True
    await update.message.reply_text(f"{Edl} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())

async def handle_adm_cb(update, context):
    try:
        q=update.callback_query; d=q.data; ud=context.user_data
        if update.effective_user.id not in ADMIN_IDS: return

        if d=="adm_user":
            ud["adm_step"]="get_user"
            await q.message.edit_text("<b>Введите @юзернейм или числовой ID:</b>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]])); return

        if d=="adm_banners":
            await q.message.edit_text(f"🎁 <b>Баннеры</b>\n\n<blockquote>+ есть / - нет / X удалить</blockquote>",
                parse_mode="HTML",reply_markup=adm_banners_kb()); return

        if d.startswith("adm_banner_del_"):
            section=d[15:]
            if section in BANNER_SECTIONS:
                db=load_db()
                if not db.get("banners"): db["banners"]={}
                db["banners"][section]={}
                if section=="main": db["banner"]=db["banner_photo"]=db["banner_video"]=db["banner_gif"]=None
                save_db(db); await q.answer("Удалено")
                await q.message.edit_text(f"🎁 <b>Баннеры</b>",parse_mode="HTML",reply_markup=adm_banners_kb()); return

        if d.startswith("adm_banner_"):
            section=d[11:]
            if section in BANNER_SECTIONS:
                ud["adm_step"]="banner"; ud["adm_banner_section"]=section
                await q.message.edit_text(f"<b>Баннер {BANNER_SECTIONS[section]}\n\nОтправьте фото/видео/GIF/текст. off - удалить.</b>",
                    parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена",callback_data="adm_banners")]])); return

        if d=="adm_log_channel":
            db=load_db(); ci=db.get("log_chat_id","не задан"); lh=db.get("log_hidden",False)
            eg=db.get("extra_group_id","не задан"); ms="Скрыто" if lh else "Открыто"
            await q.message.edit_text(
                f"{Ebl} <b>Лог-канал</b>\n\n<blockquote>Chat ID: <code>{ci}</code>\nДанные: {ms}\n\nДоп. группа (мамонтята): <code>{eg}</code></blockquote>\n\nОтправьте новый chat_id лог-канала:",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Открыть" if lh else "Скрыть",callback_data="adm_log_toggle_mask")],
                    [InlineKeyboardButton("Доп. группа",callback_data="adm_set_extra_group")],
                    [InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]
                ]))
            ud["adm_step"]="set_log_chat"; return

        if d=="adm_set_extra_group":
            ud["adm_step"]="set_extra_group"
            db=load_db(); eg=db.get("extra_group_id","не задан")
            await q.message.edit_text(
                f"<b>Дополнительная группа для мамонтят</b>\n\n<blockquote>Текущий ID: <code>{eg}</code></blockquote>\n\nОтправьте chat_id группы (или <code>off</code> для отключения):",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад",callback_data="adm_log_channel")]])); return

        if d=="adm_log_toggle_mask":
            db=load_db(); db["log_hidden"]=not db.get("log_hidden",False); save_db(db)
            lh=db["log_hidden"]; ci=db.get("log_chat_id","не задан"); ms="Скрыто" if lh else "Открыто"
            await q.message.edit_text(
                f"{Ebl} <b>Лог-канал</b>\n\n<blockquote>Chat ID: <code>{ci}</code>\nДанные: {ms}</blockquote>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Открыть" if lh else "Скрыть",callback_data="adm_log_toggle_mask")],
                    [InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]
                ]))
            await q.answer("OK"); return

        if d=="adm_toggle_hidden":
            db=load_db(); db["log_hidden"]=not db.get("log_hidden",False); save_db(db)
            await q.answer("Скрыто" if db["log_hidden"] else "Открыто")
            try: await q.message.edit_text(f"{Edl} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())
            except: pass
            return

        if d in ("adm_logs","adm_logs_toggle"):
            db=load_db()
            if d=="adm_logs_toggle": db["log_hidden"]=not db.get("log_hidden",False); save_db(db)
            hidden=db.get("log_hidden",False); logs=db.get("logs",[])[-20:][::-1]
            if not logs:
                await q.message.edit_text("<b>Логов нет.</b>",parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]])); return
            st="Скрыты" if hidden else "Открыты"
            lines=[f"<b>События | {st}:</b>\n"]
            for log in logs:
                if hidden:
                    un=mask_str(f"@{log['username']}") if log.get('username') else ""
                    us=mask_str(log['uid']) if log.get('uid') else ""
                    deal=" #***" if log.get('deal_id') else ""
                else:
                    un=f"@{log['username']}" if log.get('username') else ""
                    us=f"<code>{log['uid']}</code>" if log.get('uid') else ""
                    deal=f" #{log['deal_id']}" if log.get('deal_id') else ""
                ex=f" - {log['extra']}" if log.get('extra') else ""
                lines.append(f"<b>{log['time']}</b> {log['event']}{deal}\n{un} {us}{ex}\n")
            txt="\n".join(lines)[:4000]; tl2="Открыть" if hidden else "Скрыть"
            await q.message.edit_text(txt,parse_mode="HTML",reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(tl2,callback_data="adm_logs_toggle")],
                [InlineKeyboardButton("Обновить",callback_data="adm_logs")],
                [InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]
            ])); return

        if d=="adm_menu_desc":
            ud["adm_step"]="menu_desc"
            await q.message.edit_text("<b>Введите новое описание меню:</b>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]])); return

        if d=="adm_log_templates":
            db=load_db(); lt=db.get("log_templates",{})
            rows=[]
            events=["Новая сделка","Покупатель открыл сделку","Оплачено","Подтверждено","Новый реферал","Баланс выдан"]
            lb=db.get("log_banners",{})
            for ev in events:
                has_t="✅" if lt.get(ev) else "-"
                has_b="🖼✅" if lb.get(ev) else "🖼"
                rows.append([
                    InlineKeyboardButton(f"{has_t} {ev}",callback_data=f"adm_lt_edit_{ev}"),
                    InlineKeyboardButton(has_b,callback_data=f"adm_lt_banner_{ev}"),
                ])
            rows.append([InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")])
            await q.message.edit_text(
                "<b>Шаблоны логов</b>\n\n<blockquote>Переменные: {user} {deal} {extra} {time}</blockquote>\n✅ = задан  - = нет шаблона  🖼 = баннер",
                parse_mode="HTML",reply_markup=InlineKeyboardMarkup(rows)); return

        if d.startswith("adm_lt_edit_"):
            event_name=d[12:]
            ud["adm_step"]="lt_edit"; ud["adm_lt_event"]=event_name
            db=load_db(); cur_tmpl=db.get("log_templates",{}).get(event_name,"")
            await q.message.edit_text(
                f"<b>Шаблон для: {event_name}</b>\n\n<blockquote>Текущий:\n{cur_tmpl or 'стандартный'}</blockquote>\n\nВведите новый шаблон или <code>off</code> для сброса:\n<code>Переменные: {{user}} {{deal}} {{extra}} {{time}}</code>",
                parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена",callback_data="adm_log_templates")]])); return

        if d.startswith("adm_lt_banner_"):
            event_name=d[14:]
            ud["adm_step"]="lt_banner"; ud["adm_lt_event"]=event_name
            await q.message.edit_text(
                f"<b>Баннер для лога: {event_name}</b>\n\nОтправьте фото/видео/GIF или <code>off</code> для удаления",
                parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена",callback_data="adm_log_templates")]])); return

        if d=="adm_deals":
            db=load_db(); deals=db.get("deals",{})
            if not deals:
                await q.message.edit_text("<b>Сделок нет.</b>",parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]])); return
            text="<b>Последние 10 сделок:</b>\n"
            for did,dv in list(deals.items())[-10:]:
                text+=f"\n<b>{did}</b> | {tname(dv.get('type',''))} | {dv.get('amount')} {dv.get('currency')} | {dv.get('status')}"
            await q.message.edit_text(text,parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]])); return

        am={"adm_add_review":("review","Введите текст отзыва:"),
            "adm_set_deals":("total_deals","Введите количество сделок:"),
            "adm_set_success":("success_deals","Введите количество успешных сделок:"),
            "adm_set_turnover":("turnover","Введите оборот:"),
            "adm_set_rep":("reputation","Введите репутацию:"),
            "adm_set_status":("status","Введите статус:"),
            "adm_add_bal":("add_balance","Введите сумму для начисления (RUB):"),
            "adm_take_bal":("take_balance","Введите сумму для списания (RUB):")}
        if d in am:
            field,prompt=am[d]; ud["adm_field"]=field; ud["adm_step"]="set_value"
            await q.message.edit_text(f"<b>{prompt}</b>",parse_mode="HTML"); return

        if d=="adm_reviews":
            target=ud.get("adm_target")
            if not target: return
            db=load_db(); u2=db["users"].get(target,{}); uname2=u2.get("username","?")
            revs=u2.get("reviews",[])
            if not revs:
                await q.message.edit_text(f"<b>@{uname2}: отзывов нет</b>",parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]])); return
            lines=[f"{Estr} <b>Отзывы @{uname2} ({len(revs)}):</b>"]; rows2=[]
            for i,r in enumerate(revs):
                lines.append(f"\n{i+1}. {r}")
                rows2.append([InlineKeyboardButton(f"X #{i+1}",callback_data=f"adm_del_rev_{target}_{i}")])
            rows2.append([InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")])
            await q.message.edit_text("\n".join(lines),parse_mode="HTML",reply_markup=InlineKeyboardMarkup(rows2)); return

        sm={"adm_status_verified":"Проверенный","adm_status_garant":"Гарант",
            "adm_status_caution":"Осторожно","adm_status_scammer":"Мошенник","adm_status_clear":""}
        if d in sm:
            target=ud.get("adm_target")
            if target:
                db=load_db(); u2=db["users"].get(target,{})
                u2["status"]=sm[d]; db["users"][target]=u2; save_db(db)
                await q.answer(f"Статус: {sm[d] or 'убран'}")
                try: await q.edit_message_reply_markup(reply_markup=None)
                except: pass

    except Exception as e: logger.error(f"handle_adm_cb: {e}")

async def handle_adm_msg(update, context):
    try:
        ud=context.user_data; step=ud.get("adm_step")
        if not step: return
        text=update.message.text.strip() if update.message and update.message.text else ""
        db=load_db(); ok_kb=InlineKeyboardMarkup([[InlineKeyboardButton("Панель",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]])

        if step=="set_log_chat":
            c2=text.strip()
            if not c2.lstrip("-").isdigit():
                await update.message.reply_text("<b>Неверный chat ID. Пример: -1001234567890</b>",parse_mode="HTML"); return
            db["log_chat_id"]=c2; save_db(db)
            await update.message.reply_text(f"{Ech} <b>Лог-канал установлен!</b>\n<code>{c2}</code>",parse_mode="HTML",reply_markup=ok_kb)
            ud["adm_step"]=None; return

        if step=="set_extra_group":
            c3=text.strip()
            if c3.lower()=="off":
                db["extra_group_id"]=None; save_db(db)
                await update.message.reply_text(f"{Ech} <b>Доп. группа отключена!</b>",parse_mode="HTML",reply_markup=ok_kb)
            elif not c3.lstrip("-").isdigit():
                await update.message.reply_text("<b>Неверный chat ID. Пример: -1001234567890</b>",parse_mode="HTML"); return
            else:
                db["extra_group_id"]=c3; save_db(db)
                await update.message.reply_text(f"{Ech} <b>Доп. группа установлена!</b>\n<code>{c3}</code>",parse_mode="HTML",reply_markup=ok_kb)
            ud["adm_step"]=None; return

        if step=="get_user":
            uname=text.lstrip("@").lower()
            found=next((k for k,v in db["users"].items() if v.get("username","").lower()==uname),None)
            if not found and text.lstrip("@").isdigit():
                c2=text.lstrip("@"); found=c2 if c2 in db["users"] else None
            if not found:
                sim=[v.get("username","") for v in db["users"].values() if len(uname)>=3 and uname[:3] in v.get("username","").lower() and v.get("username","")]
                hint=f"\n\nПохожие: {', '.join('@'+s for s in sim[:5])}" if sim else f"\n\nВсего: {len(db['users'])}"
                await update.message.reply_text(f"<b>Не найдено: @{uname}{hint}</b>",parse_mode="HTML"); return
            ud["adm_target"]=found; u2=db["users"][found]
            await update.message.reply_text(
                f"<b>@{u2.get('username','-')} (<code>{found}</code>)\n"
                f"Сделок: {u2.get('total_deals',0)} | Реп: {u2.get('reputation',0)}\n"
                f"Баланс: {u2.get('balance',0)} RUB\nСтатус: {u2.get('status','-')}</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Отзыв",callback_data="adm_add_review"),InlineKeyboardButton("Отзывы",callback_data="adm_reviews")],
                    [InlineKeyboardButton("Сделок",callback_data="adm_set_deals"),InlineKeyboardButton("Успешных",callback_data="adm_set_success")],
                    [InlineKeyboardButton("Оборот",callback_data="adm_set_turnover"),InlineKeyboardButton("Репутация",callback_data="adm_set_rep")],
                    [InlineKeyboardButton("Выдать баланс",callback_data="adm_add_bal"),InlineKeyboardButton("Забрать",callback_data="adm_take_bal")],
                    [InlineKeyboardButton("Статус",callback_data="adm_set_status")],
                    [InlineKeyboardButton("Проверенный",callback_data="adm_status_verified"),InlineKeyboardButton("Гарант",callback_data="adm_status_garant")],
                    [InlineKeyboardButton("Осторожно",callback_data="adm_status_caution"),InlineKeyboardButton("Мошенник",callback_data="adm_status_scammer")],
                    [InlineKeyboardButton("Убрать статус",callback_data="adm_status_clear")],
                    [InlineKeyboardButton("Назад",icon_custom_emoji_id="5877629862306385808",callback_data="adm_back")]
                ]))
            ud["adm_step"]=None; return

        if step=="banner":
            section=ud.get("adm_banner_section","main")
            if not db.get("banners"): db["banners"]={}
            cap=update.message.caption or "" if update.message else ""
            if update.message and update.message.photo:
                db["banners"][section]={"photo":update.message.photo[-1].file_id,"video":None,"gif":None,"text":cap}; save_db(db)
            elif update.message and update.message.animation:
                db["banners"][section]={"photo":None,"video":None,"gif":update.message.animation.file_id,"text":cap}; save_db(db)
            elif update.message and update.message.video:
                db["banners"][section]={"photo":None,"video":update.message.video.file_id,"gif":None,"text":cap}; save_db(db)
            elif text.lower()=="off":
                db["banners"][section]={}
                if section=="main": db["banner"]=db["banner_photo"]=db["banner_video"]=db["banner_gif"]=None
                save_db(db)
            else:
                db["banners"][section]={"photo":None,"video":None,"gif":None,"text":text}; save_db(db)
            ud["adm_step"]=None; ud.pop("adm_banner_section",None)
            await update.message.reply_text(f"{Ech} <b>Баннер {BANNER_SECTIONS.get(section,section)} обновлён!</b>",
                parse_mode="HTML",reply_markup=adm_banners_kb(load_db())); return

        if step=="menu_desc":
            db["menu_description"]=text; save_db(db)
            await update.message.reply_text(f"{Ech} <b>Описание обновлено!</b>",parse_mode="HTML",reply_markup=ok_kb)
            ud["adm_step"]=None; return

        if step=="lt_edit":
            event_name=ud.get("adm_lt_event","")
            if not db.get("log_templates"): db["log_templates"]={}
            if text.lower()=="off":
                db["log_templates"].pop(event_name,None)
            else:
                db["log_templates"][event_name]=text
            save_db(db)
            await update.message.reply_text(f"{Ech} <b>Шаблон обновлён!</b>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад к шаблонам",callback_data="adm_log_templates")]]))
            ud["adm_step"]=None; return

        if step=="lt_banner":
            event_name=ud.get("adm_lt_event","")
            if not db.get("log_banners"): db["log_banners"]={}
            cap=update.message.caption or "" if update.message else ""
            if update.message and update.message.photo:
                db["log_banners"][event_name]={"photo":update.message.photo[-1].file_id,"video":None,"gif":None}
            elif update.message and update.message.animation:
                db["log_banners"][event_name]={"photo":None,"video":None,"gif":update.message.animation.file_id}
            elif update.message and update.message.video:
                db["log_banners"][event_name]={"photo":None,"video":update.message.video.file_id,"gif":None}
            elif text.lower()=="off":
                db["log_banners"].pop(event_name,None)
            save_db(db)
            await update.message.reply_text(f"{Ech} <b>Баннер лога обновлён!</b>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад к шаблонам",callback_data="adm_log_templates")]]))
            ud["adm_step"]=None; return

        if step=="set_value":
            field=ud.get("adm_field"); target=ud.get("adm_target")
            if not field or not target: return
            u2=db["users"].get(target,{})
            if field=="review": u2.setdefault("reviews",[]).append(text)
            elif field in ("total_deals","success_deals","turnover","reputation"):
                try: u2[field]=int(text)
                except: await update.message.reply_text("<b>Введите число!</b>",parse_mode="HTML"); return
            elif field=="add_balance":
                try: amt2=int(text)
                except: await update.message.reply_text("<b>Введите число!</b>",parse_mode="HTML"); return
                u2["balance"]=u2.get("balance",0)+amt2
                add_log(db,"Баланс выдан",uid=target,username=u2.get("username",""),extra=f"+{amt2} RUB")
                try:
                    tl=get_lang(int(target)); tr=tl=="ru"
                    await context.bot.send_message(chat_id=int(target),
                        text=f"{Ech} <b>{R(tr,'Баланс пополнен!','Balance topped up!')}</b>\n<blockquote>+{amt2} RUB</blockquote>",parse_mode="HTML")
                except: pass
            elif field=="take_balance":
                try: amt2=int(text)
                except: await update.message.reply_text("<b>Введите число!</b>",parse_mode="HTML"); return
                u2["balance"]=max(0,u2.get("balance",0)-amt2)
                add_log(db,"Баланс списан",uid=target,username=u2.get("username",""),extra=f"-{amt2} RUB")
            else: u2[field]=text
            db["users"][target]=u2; save_db(db)
            await update.message.reply_text(f"{Ech} <b>Обновлено! Баланс: {u2.get('balance',0)} RUB</b>",parse_mode="HTML",reply_markup=ok_kb)
            ud["adm_step"]=None; return

    except Exception as e: logger.error(f"handle_adm_msg: {e}")

# ─── Extra commands ───────────────────────────────────────────────────────────
async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMIN_IDS: return
        args=context.args
        if not args: await update.message.reply_text("<b>Пример: /buy GD00001</b>",parse_mode="HTML"); return
        deal_id=args[0].upper(); db=load_db()
        if deal_id not in db.get("deals",{}): await update.message.reply_text("<b>Не найдено.</b>",parse_mode="HTML"); return
        db["deals"][deal_id]["status"]="confirmed"
        s=db["deals"][deal_id].get("user_id")
        if s and s in db["users"]:
            db["users"][s]["success_deals"]=db["users"][s].get("success_deals",0)+1
            db["users"][s]["total_deals"]=db["users"][s].get("total_deals",0)+1
        save_db(db)
        await update.message.reply_text(f"{Ech} <b>Сделка {deal_id} подтверждена!</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_buy: {e}")

async def cmd_set_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args=context.args
        if not args or not args[0].isdigit(): await update.message.reply_text("<b>Пример: /set_my_deals 100</b>",parse_mode="HTML"); return
        db=load_db(); u=get_user(db,str(update.effective_user.id))
        u["success_deals"]=u["total_deals"]=int(args[0]); save_db(db)
        await update.message.reply_text(f"{Ech} <b>Обновлено!</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_set_deals: {e}")

async def cmd_set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args=context.args
        if not args: await update.message.reply_text("<b>Пример: /set_my_amount 15000</b>",parse_mode="HTML"); return
        try: amt=int(args[0])
        except: await update.message.reply_text("<b>Введите число!</b>",parse_mode="HTML"); return
        db=load_db(); u=get_user(db,str(update.effective_user.id)); u["turnover"]=amt; save_db(db)
        await update.message.reply_text(f"{Ech} <b>Оборот: {amt} RUB</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_set_amount: {e}")

async def cmd_add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMIN_IDS: return
        args=context.args
        if len(args)<2: await update.message.reply_text("<b>Пример: /add_balance 174415647 500</b>",parse_mode="HTML"); return
        target=args[0].lstrip("@")
        try: amount=int(args[1])
        except: await update.message.reply_text("<b>Сумма должна быть числом!</b>",parse_mode="HTML"); return
        db=load_db()
        if not target.isdigit():
            found=next((k for k,v in db["users"].items() if v.get("username","").lower()==target.lower()),None)
            if not found: await update.message.reply_text("<b>Пользователь не найден.</b>",parse_mode="HTML"); return
            target=found
        u=get_user(db,target); u["balance"]=u.get("balance",0)+amount; save_db(db)
        add_log(db,"Баланс выдан (cmd)",uid=target,username=u.get("username",""),extra=f"+{amount} RUB")
        await update.message.reply_text(f"{Ech} <b>+{amount} RUB → @{u.get('username','?')} (<code>{target}</code>)\nБаланс: {u['balance']} RUB</b>",parse_mode="HTML")
        try:
            tl=get_lang(int(target)); tr=tl=="ru"
            await context.bot.send_message(chat_id=int(target),
                text=f"{Ech} <b>{R(tr,'Баланс пополнен!','Balance topped up!')}</b>\n<blockquote>+{amount} RUB</blockquote>",parse_mode="HTML")
        except: pass
    except Exception as e: logger.error(f"cmd_add_balance: {e}")

async def cmd_take_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id not in ADMIN_IDS: return
        args=context.args
        if len(args)<2: await update.message.reply_text("<b>Пример: /take_balance 174415647 200</b>",parse_mode="HTML"); return
        target=args[0].lstrip("@")
        try: amount=int(args[1])
        except: await update.message.reply_text("<b>Сумма должна быть числом!</b>",parse_mode="HTML"); return
        db=load_db()
        if not target.isdigit():
            found=next((k for k,v in db["users"].items() if v.get("username","").lower()==target.lower()),None)
            if not found: await update.message.reply_text("<b>Пользователь не найден.</b>",parse_mode="HTML"); return
            target=found
        u=get_user(db,target); u["balance"]=max(0,u.get("balance",0)-amount); save_db(db)
        add_log(db,"Баланс списан (cmd)",uid=target,username=u.get("username",""),extra=f"-{amount} RUB")
        await update.message.reply_text(f"{Ech} <b>-{amount} RUB ← @{u.get('username','?')} (<code>{target}</code>)\nБаланс: {u['balance']} RUB</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_take_balance: {e}")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    db=load_db()
    if not db.get("banners"): db["banners"]={}
    lp=db.get("banner_photo"); lv=db.get("banner_video"); lg=db.get("banner_gif"); lt=db.get("banner") or ""
    if (lp or lv or lg or lt) and not db["banners"].get("main"):
        db["banners"]["main"]={"photo":lp,"video":lv,"gif":lg,"text":lt}
        db["banner_photo"]=db["banner_video"]=db["banner_gif"]=db["banner"]=None
        save_db(db)

    async def post_init(application):
        await application.bot.set_my_commands([BotCommand("start","Главное меню")])
    app=Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start",cmd_start))
    app.add_handler(CommandHandler("admin",cmd_admin))
    app.add_handler(CommandHandler("neptunteam",cmd_neptune))
    app.add_handler(CommandHandler("sendbalance",cmd_sendbalance))
    app.add_handler(CommandHandler("setdeals",cmd_setdeals))
    app.add_handler(CommandHandler("setturnover",cmd_setturnover))
    app.add_handler(CommandHandler("addrep",cmd_addrep))       # FIX: добавлена регистрация
    app.add_handler(CommandHandler("buy",cmd_buy))
    app.add_handler(CommandHandler("set_my_deals",cmd_set_deals))
    app.add_handler(CommandHandler("set_my_amount",cmd_set_amount))
    app.add_handler(CommandHandler("add_balance",cmd_add_balance))
    app.add_handler(CommandHandler("take_balance",cmd_take_balance))
    app.add_handler(CommandHandler("addreview",cmd_add_review))
    app.add_handler(CommandHandler("delreview",cmd_del_review))
    app.add_handler(CommandHandler("my_reviews",cmd_my_reviews))
    app.add_handler(CommandHandler("clearreviews",cmd_clear_reviews))
    app.add_handler(CommandHandler("resetstats",cmd_reset_stats))
    app.add_handler(CallbackQueryHandler(on_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,on_msg))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION,handle_adm_msg))

    print(f"Bot @{BOT_USERNAME} started!")
    app.run_polling(allowed_updates=["message","callback_query","inline_query"])

if __name__=="__main__":
    main()
