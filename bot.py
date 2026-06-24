import logging, json, os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN    = '8767675859:AAEYrMnVMAZjI7rBEc1QLNpHs7rVlUIv-0Q'
ADMIN_ID     = 8726084830
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
    "premium":    ce("5377620962390857342", "✈️"),
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
    "nft":      "NFT подарок",
    "username": "NFT Username",
    "stars":    "Звёзды Telegram",
    "crypto":   "Крипта (TON/USDT)",
    "premium":  "Telegram Premium",
}
TNAMES_EN = {
    "nft":      "NFT Gift",
    "username": "NFT Username",
    "stars":    "Telegram Stars",
    "crypto":   "Crypto (TON/USDT)",
    "premium":  "Telegram Premium",
}

def tname(t, lang="ru"): 
    return TNAMES_EN.get(t, t) if lang=="en" else TNAMES_RU.get(t, t)

# ─── Валюты ───────────────────────────────────────────────────────────────────
CUR_PLAIN_RU = {
    "TON":"TON","USDT":"USDT","Stars":"Звёзды",
    "RUB":"Рубли","KZT":"Теңге","AZN":"Manat","KGS":"Сом",
    "UZS":"So'm","TJS":"Сомонӣ","BYN":"Рубли","UAH":"Гривнi","GEL":"ლარი",
}
CUR_PLAIN_EN = {
    "TON":"TON","USDT":"USDT","Stars":"Stars",
    "RUB":"Rubles","KZT":"Tenge","AZN":"Manat","KGS":"Som",
    "UZS":"So'm","TJS":"Somoni","BYN":"Rubles","UAH":"Hryvnia","GEL":"Lari",
}
CUR_BTN = {
    "TON":"💎 TON","USDT":"💵 USDT","Stars":"⭐ Звёзды",
    "RUB":"🇷🇺 Россия","KZT":"🇰🇿 Казахстан","AZN":"🇦🇿 Азербайджан","KGS":"🇰🇬 Кыргызстан",
    "UZS":"🇺🇿 Узбекистан","TJS":"🇹🇯 Таджикистан","BYN":"🇧🇾 Беларусь","UAH":"🇺🇦 Украина","GEL":"🇬🇪 Грузия",
}
CUR_EMOJI = {
    "TON":"💎","USDT":"💵","Stars":"⭐","RUB":"💳","KZT":"💳","AZN":"💳",
    "KGS":"💳","UZS":"💳","TJS":"💳","BYN":"💳","UAH":"💳","GEL":"💳",
}
CURMAP = {
    "cur_ton":"TON","cur_usdt":"USDT","cur_rub":"RUB","cur_stars":"Stars",
    "cur_kzt":"KZT","cur_azn":"AZN","cur_kgs":"KGS","cur_uzs":"UZS",
    "cur_tjs":"TJS","cur_byn":"BYN","cur_uah":"UAH","cur_gel":"GEL"
}

def cur_plain(code, lang="ru"):
    if lang=="en": return CUR_PLAIN_EN.get(code, code)
    return CUR_PLAIN_RU.get(code, code)

def cur_with_emoji(code, lang="ru"):
    emoji = CUR_EMOJI.get(code, "💰")
    name = cur_plain(code, lang)
    return f"{emoji} {name}"

def card_bank(lang="ru"): 
    return CARD_BANK_EN if lang=="en" else CARD_BANK_RU

def R(ru, a, b): 
    return a if ru else b

BANNER_SECTIONS = {
    "main":"Главное меню","deal":"Создать сделку","balance":"Пополнить/Вывод",
    "profile":"Профиль","top":"Топ","my_deals":"Мои сделки",
    "deal_card":"Карточка сделки","ref":"Рефералы",
}

# ─── DB ───────────────────────────────────────────────────────────────────────
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE,"r",encoding="utf-8") as f: 
            return json.load(f)
    return {
        "users":{},"deals":{},"banner":None,"banner_photo":None,"banner_video":None,
        "banner_gif":None,"menu_description":None,"deal_counter":1,"banners":{},
        "logs":[],"log_chat_id":None,"log_hidden":False
    }

def save_db(db):
    with open(DB_FILE,"w",encoding="utf-8") as f: 
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(db, uid):
    k=str(uid)
    if k not in db["users"]:
        db["users"][k]={
            "username":"","balance":0,"total_deals":0,"success_deals":0,
            "turnover":0,"reviews":[],"status":"","lang":"ru",
            "requisites":{},"ref_by":None,"ref_count":0,"ref_earned":0
        }
    u=db["users"][k]
    for f,v in [("requisites",{}),("ref_by",None),("ref_count",0),("ref_earned",0),("balance",0),("reviews",[])]:
        if f not in u: u[f]=v
    return u

def get_lang(uid):
    try: 
        return get_user(load_db(), uid).get("lang","ru")
    except: 
        return "ru"

def gen_deal_id(db):
    n=db.get("deal_counter",1)
    db["deal_counter"]=n+1
    save_db(db)
    return f"GD{n:05d}"

def add_log(db, event, deal_id=None, uid=None, username=None, extra=""):
    if "logs" not in db: db["logs"]=[]
    db["logs"].append({
        "time":datetime.now().strftime("%d.%m.%Y %H:%M"),
        "event":event,
        "deal_id":deal_id or "",
        "uid":str(uid) if uid else "",
        "username":username or "",
        "extra":extra
    })
    if len(db["logs"])>500: 
        db["logs"]=db["logs"][-500:]

def mask_str(t):
    if not t: return "—"
    if t.startswith("@"):
        s=t[1:]
        return "@***" if len(s)<=3 else f"@{s[:2]}***{s[-2:]}"
    if t.isdigit(): 
        return t[:3]+"***"+t[-2:]
    return t[:2]+"***"

async def send_log_msg(context, db, entry):
    chat_id=db.get("log_chat_id")
    if not chat_id: return
    hidden=db.get("log_hidden",False)
    try:
        u=entry.get("username","")
        us=entry.get("uid","")
        deal=f" #{entry['deal_id']}" if entry.get("deal_id") else ""
        ex=f"\n{entry['extra']}" if entry.get("extra") else ""
        ud=mask_str(f"@{u}") if hidden and u else (f"@{u}" if u else "")
        uid_d=mask_str(us) if hidden and us else (f"<code>{us}</code>" if us else "")
        await context.bot.send_message(
            chat_id=int(chat_id),
            text=f"<b>{entry['time']}</b> {entry['event']}{deal}\n{ud} {uid_d}{ex}",
            parse_mode="HTML"
        )
    except Exception as e: 
        logger.error(f"send_log_msg: {e}")

# ─── Banner ───────────────────────────────────────────────────────────────────
def get_banner(db, section="main"):
    b=db.get("banners",{}).get(section)
    if b and any(b.get(k) for k in ("photo","video","gif","text")): 
        return b
    if section=="main":
        lg={
            "photo":db.get("banner_photo"),
            "video":db.get("banner_video"),
            "gif":db.get("banner_gif"),
            "text":db.get("banner") or ""
        }
        if any(v for v in lg.values()): 
            return lg
    return None

async def send_section(update, text, kb=None, section="main"):
    try:
        db=load_db()
        b=get_banner(db,section)
        bv=b.get("video") if b else None
        bg=b.get("gif") if b else None
        bp=b.get("photo") if b else None
        bt=b.get("text","") if b else ""
        full=text+(f"\n\n<b>{bt}</b>" if bt else "")
        
        if update.callback_query and update.callback_query.message:
            msg=update.callback_query.message
            has_media=bool(msg.photo or msg.video or msg.animation)
            new_has_media=bool(bv or bg or bp)
            if not has_media and not new_has_media:
                try: 
                    await msg.edit_text(full,parse_mode="HTML",reply_markup=kb)
                    return
                except: 
                    pass
            try: 
                await msg.delete()
            except: 
                pass
        
        if bv: 
            await update.effective_chat.send_video(video=bv,caption=full,parse_mode="HTML",reply_markup=kb)
        elif bg: 
            await update.effective_chat.send_animation(animation=bg,caption=full,parse_mode="HTML",reply_markup=kb)
        elif bp: 
            await update.effective_chat.send_photo(photo=bp,caption=full,parse_mode="HTML",reply_markup=kb)
        else: 
            await update.effective_chat.send_message(full,parse_mode="HTML",reply_markup=kb)
    except Exception as e:
        logger.error(f"send_section: {e}")
        try: 
            await update.effective_chat.send_message(text,parse_mode="HTML",reply_markup=kb)
        except: 
            pass

async def send_new(update, text, kb=None, section="main"):
    try:
        db=load_db()
        b=get_banner(db,section)
        bv=b.get("video") if b else None
        bg=b.get("gif") if b else None
        bp=b.get("photo") if b else None
        bt=b.get("text","") if b else ""
        full=text+(f"\n\n<b>{bt}</b>" if bt else "")
        
        if bv: 
            await update.effective_chat.send_video(video=bv,caption=full,parse_mode="HTML",reply_markup=kb)
        elif bg: 
            await update.effective_chat.send_animation(animation=bg,caption=full,parse_mode="HTML",reply_markup=kb)
        elif bp: 
            await update.effective_chat.send_photo(photo=bp,caption=full,parse_mode="HTML",reply_markup=kb)
        else: 
            await update.effective_chat.send_message(full,parse_mode="HTML",reply_markup=kb)
    except Exception as e:
        logger.error(f"send_new: {e}")
        try: 
            await update.effective_chat.send_message(text,parse_mode="HTML",reply_markup=kb)
        except: 
            pass

# ─── Keyboards ────────────────────────────────────────────────────────────────
def main_kb(lang):
    ru=lang=="ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 "+R(ru,"Создать сделку","Create Deal"),callback_data="menu_deal"),
         InlineKeyboardButton("⭐ "+R(ru,"Профиль","Profile"),callback_data="menu_profile")],
        [InlineKeyboardButton("💸 "+R(ru,"Пополнить/Вывод","Top Up/Withdraw"),callback_data="menu_balance"),
         InlineKeyboardButton("🪪 "+R(ru,"Мои сделки","My Deals"),callback_data="menu_my_deals")],
        [InlineKeyboardButton("🌍 "+R(ru,"Язык / Lang","Language"),callback_data="menu_lang"),
         InlineKeyboardButton("🏆 "+R(ru,"Топ продавцов","Top Sellers"),callback_data="menu_top")],
        [InlineKeyboardButton("👥 "+R(ru,"Рефералы","Referrals"),callback_data="menu_ref"),
         InlineKeyboardButton("📋 "+R(ru,"Реквизиты","Requisites"),callback_data="menu_req")],
        [InlineKeyboardButton("🆘 "+R(ru,"Тех. поддержка","Tech Support"),url="https://t.me/GiftDealsSupport")],
    ])

def role_kb(lang):
    ru=lang=="ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 "+R(ru,"Я покупатель","I am the Buyer"),callback_data="role_buyer")],
        [InlineKeyboardButton("🏷 "+R(ru,"Я продавец","I am the Seller"),callback_data="role_seller")],
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")],
    ])

def types_kb(lang):
    ru=lang=="ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 NFT",callback_data="dt_nft"),
         InlineKeyboardButton("🎴 NFT Username",callback_data="dt_usr")],
        [InlineKeyboardButton("⭐ "+R(ru,"Звёзды","Stars"),callback_data="dt_str"),
         InlineKeyboardButton("💎 "+R(ru,"Крипта","Crypto"),callback_data="dt_cry")],
        [InlineKeyboardButton("✈️ Telegram Premium",callback_data="dt_prm")],
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")],
    ])

def cur_kb(lang):
    def n(c): return CUR_BTN.get(c,c)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(n("TON"),callback_data="cur_ton"),
         InlineKeyboardButton(n("USDT"),callback_data="cur_usdt")],
        [InlineKeyboardButton(n("RUB"),callback_data="cur_rub"),
         InlineKeyboardButton(n("Stars"),callback_data="cur_stars")],
        [InlineKeyboardButton(n("KZT"),callback_data="cur_kzt"),
         InlineKeyboardButton(n("AZN"),callback_data="cur_azn")],
        [InlineKeyboardButton(n("KGS"),callback_data="cur_kgs"),
         InlineKeyboardButton(n("UZS"),callback_data="cur_uzs")],
        [InlineKeyboardButton(n("TJS"),callback_data="cur_tjs"),
         InlineKeyboardButton(n("BYN"),callback_data="cur_byn")],
        [InlineKeyboardButton(n("UAH"),callback_data="cur_uah"),
         InlineKeyboardButton(n("GEL"),callback_data="cur_gel")],
    ])

# ─── Validation ───────────────────────────────────────────────────────────────
def validate_username(text):
    if not text.startswith("@"): 
        return None,"no_at"
    u=text[1:]
    if len(u)<4: 
        return None,"short"
    if not all(c.isascii() and (c.isalpha() or c.isdigit() or c=="_") for c in u):
        return None,"chars"
    if not any(c.isalpha() for c in u): 
        return None,"chars"
    return text, None

def validate_card(text):
    c=text.replace(" ","").replace("-","").replace("+","")
    if c.isdigit() and 10<=len(c)<=12: 
        return text
    if c.isdigit() and len(c) in (14,16): 
        return c
    return None

def validate_ton_address(text):
    t=text.strip()
    return (t.startswith("UQ") or t.startswith("EQ")) and len(t)>=40

def validate_nft_link(text, dtype):
    clean=text.strip()
    for prefix in ("https://","http://"):
        if clean.startswith(prefix): 
            clean=clean[len(prefix):]
            break
    if not clean.startswith("t.me/"): 
        return False,"no_tme"
    path=clean[5:]
    if dtype=="nft":
        if not path.startswith("nft/"): 
            return False,"wrong_nft"
        if len(path[4:])<2: 
            return False,"wrong_nft"
    return True,None

def calc_rating(reviews):
    """Подсчёт средней оценки из отзывов"""
    if not reviews:
        return 0
    total = 0
    count = 0
    for rev in reviews:
        if rev.startswith("⭐"):
            try:
                rating_part = rev.split("/")[0].replace("⭐","").strip()
                total += int(rating_part)
                count += 1
            except:
                pass
    return round(total / count, 1) if count > 0 else 0

# ─── Welcome ──────────────────────────────────────────────────────────────────
def get_welcome(lang):
    ru=lang=="ru"
    if ru:
        pts=[
            "Автоматические сделки с НФТ и подарками",
            "Полная защита обеих сторон",
            "Средства заморожены до подтверждения",
            "Передача через менеджера: @GiftDealsManager"
        ]
        intro="Gift Deals — самая безопасная площадка для сделок в Telegram"
        footer="Выберите действие ниже"
        stats="6500+ сделок · оборот $48,200"
    else:
        pts=[
            "Automatic NFT & gift deals",
            "Full protection for both parties",
            "Funds frozen until confirmation",
            "Transfer via manager: @GiftDealsManager"
        ]
        intro="Gift Deals — the safest platform for deals in Telegram"
        footer="Choose an action below"
        stats="6500+ deals · $48,200 turnover"
    
    nums=[En1,En2,En3,En4]
    icons=[Eslr, Elck, Ejn, Epct]
    lines="\n".join(
        f"<blockquote><b>{nums[i]} {icons[i]} {pts[i]}.</b></blockquote>" 
        for i in range(4)
    )
    
    return (
        f"{Ecwn} <b>{intro}</b>\n\n"
        f"{lines}\n\n"
        f"<blockquote><b>{Efire} {stats}</b></blockquote>\n\n"
        f"{Erkt} <b>{footer}</b>"
    )

# ─── Deal card ────────────────────────────────────────────────────────────────
def build_deal_text(deal_id, d, creator_tag, partner_tag, lang, joined=False):
    try:
        ru=lang=="ru"
        dtype=d.get("type","")
        cur=d.get("currency","—")
        amt=d.get("amount","—")
        dd=d.get("data",{})
        creator_role=d.get("creator_role","seller")
        
        # Инфо о товаре
        item=""
        if dtype=="nft":       
            item=f"\n{Eln} {R(ru,'Ссылка','Link')}: {dd.get('nft_link','—')}"
        elif dtype=="username": 
            item=f"\n{Eln} Username: {dd.get('trade_username','—')}"
        elif dtype=="stars":    
            item=f"\n{Est} {R(ru,'Звёзд','Stars')}: {dd.get('stars_count','—')}"
        elif dtype=="premium":  
            item=f"\n{Eprem} {R(ru,'Срок','Period')}: {dd.get('premium_period','—')}"
        
        if creator_role=="buyer":
            lbl_creator=R(ru,"Покупатель","Buyer")
            lbl_partner=R(ru,"Продавец","Seller")
        else:
            lbl_creator=R(ru,"Продавец","Seller")
            lbl_partner=R(ru,"Покупатель","Buyer")
        
        db=load_db()
        
        def stats_block(uid_s):
            try:
                u=db["users"].get(str(uid_s),{}) if uid_s else {}
                nd=u.get("success_deals",0)
                nt=u.get("turnover",0)
                reviews=u.get("reviews",[])
                nv=len(reviews)
                rating=calc_rating(reviews)
                st=u.get("status","")
                
                sl=f"\n{Emdl} <b>{st}</b>" if st else ""
                rating_stars = "⭐" * int(rating) if rating > 0 else ""
                
                return (
                    f"{Etph} {R(ru,'Сделок','Deals')}: <b>{nd}</b>\n"
                    f"{Estr} {R(ru,'Отзывов','Reviews')}: <b>{nv}</b> {rating_stars} <b>{rating}/5</b>\n"
                    f"{Emn} {R(ru,'Оборот','Turnover')}: <b>{nt} ₽</b>{sl}"
                )
            except: 
                return "—"
        
        creator_uid=d.get("user_id","")
        p_uname=d.get("partner","").lstrip("@").lower()
        partner_uid=next(
            (k for k,v in db.get("users",{}).items() if v.get("username","").lower()==p_uname),
            None
        )
        
        cur_display = cur_with_emoji(cur, lang)
        
        lines=[
            f"<b>{Ech} {R(ru,'Сделка','Deal')} #{deal_id}</b>\n",
            f"<b>{tname(dtype,lang)}</b>{item}",
            f"<b>{Emn} {R(ru,'Сумма','Amount')}:</b> <b>{amt} {cur_display}</b>\n",
            f"<b>{lbl_creator}:</b> <b>{creator_tag}</b>",
            f"<blockquote>{stats_block(creator_uid)}</blockquote>\n",
        ]
        
        if joined:
            lines.extend([
                f"<b>{lbl_partner}:</b> <b>{partner_tag}</b>",
                f"<blockquote>{stats_block(partner_uid)}</blockquote>\n",
            ])
            
            # Инструкции для присоединившегося
            if creator_role=="seller":
                # Присоединился покупатель
                instr = R(ru,
                    f"Переведите оплату менеджеру {MANAGER_TAG}, затем нажмите «Я оплатил»",
                    f"Send payment to manager {MANAGER_TAG}, then press «I paid»"
                )
            else:
                # Присоединился продавец
                instr = R(ru,
                    f"Передайте товар менеджеру {MANAGER_TAG}",
                    f"Transfer the item to manager {MANAGER_TAG}"
                )
            
            lines.append(f"<blockquote><b>{Ebl} {instr}</b></blockquote>")
        else:
            lines.append(f"<b>{Ewrn} {R(ru,'Ожидание второй стороны','Waiting for second party')}...</b>\n")
            lines.append(f"<blockquote><b>{Esrk} {R(ru,'Отправьте ссылку партнёру','Send link to partner')}</b></blockquote>")
        
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"build_deal_text error: {e}")
        return f"Error: {e}"

# ─── /start ───────────────────────────────────────────────────────────────────
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id
    uname=update.effective_user.username or ""
    db=load_db()
    u=get_user(db, uid)
    u["username"]=uname
    lang=u.get("lang","ru")
    ru=lang=="ru"
    
    args=context.args
    if args and args[0].startswith("ref_"):
        ref_id=args[0][4:]
        if ref_id.isdigit() and int(ref_id)!=uid and not u.get("ref_by"):
            u["ref_by"]=int(ref_id)
            ref_user=db["users"].get(ref_id)
            if ref_user:
                ref_user["ref_count"]=ref_user.get("ref_count",0)+1
            add_log(db, R(ru,"Переход по реферальной ссылке","Referral link used"),
                    uid=uid, username=uname, extra=f"Реферер: {ref_id}")
    
    # Проверка на ссылку сделки
    if args and args[0].startswith("deal_"):
        deal_id=args[0][5:].upper()
        d=db.get("deals",{}).get(deal_id)
        if d:
            creator_id=d.get("user_id")
            if str(creator_id)==str(uid):
                await update.message.reply_text(
                    R(ru,"❌ Вы не можете присоединиться к собственной сделке",
                       "❌ You cannot join your own deal"),
                    parse_mode="HTML"
                )
                save_db(db)
                await send_section(update, get_welcome(lang), main_kb(lang), "main")
                return
            
            # Проверяем реквизиты
            req=u.get("requisites",{})
            if not any(req.get(f) for f in ("card","phone","ton")):
                text=(
                    f"{Ewrn} <b>{R(ru,'Добавьте реквизиты','Add requisites')}</b>\n\n"
                    f"{R(ru,'Для участия в сделке необходимо добавить реквизиты','To participate you need to add requisites')}"
                )
                kb=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        "📋 "+R(ru,"Перейти к реквизитам","Go to requisites"),
                        callback_data=f"req_for_deal_{deal_id}"
                    )],
                    [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]
                ])
                context.user_data["pending_deal"]=deal_id
                save_db(db)
                await send_new(update, text, kb, "deal_card")
                return
            
            # Присоединяемся к сделке
            d["partner_id"]=uid
            d["status"]="active"
            save_db(db)
            
            add_log(db, R(ru,"Присоединение к сделке","Joined deal"), 
                    deal_id=deal_id, uid=uid, username=uname)
            await send_log_msg(context, db, db["logs"][-1])
            
            # Показываем карточку сделки с инструкциями
            creator_uname=db["users"].get(str(creator_id),{}).get("username","") if creator_id else ""
            creator_tag=f"@{creator_uname}" if creator_uname else f"#{creator_id}"
            partner_tag=f"@{uname}" if uname else f"#{uid}"
            
            text=build_deal_text(deal_id, d, creator_tag, partner_tag, lang, joined=True)
            
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ "+R(ru,"Я оплатил","I paid"),callback_data=f"deal_paid_{deal_id}")],
                [InlineKeyboardButton("💬 "+R(ru,"Связаться с менеджером","Contact manager"),url=MANAGER_URL)],
                [InlineKeyboardButton("🔙 "+R(ru,"Главное меню","Main menu"),callback_data="main_menu")]
            ])
            
            await send_new(update, text, kb, "deal_card")
            return
    
    save_db(db)
    add_log(db,"Запуск бота",uid=uid,username=uname)
    await send_log_msg(context,db,db["logs"][-1])
    
    await send_section(update, get_welcome(lang), main_kb(lang), "main")

# ─── Main menu ────────────────────────────────────────────────────────────────
async def main_menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    context.user_data.clear()
    lang=get_lang(q.from_user.id)
    await send_section(update, get_welcome(lang), main_kb(lang), "main")

# ─── Language ─────────────────────────────────────────────────────────────────
async def menu_lang_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    lang=get_lang(q.from_user.id)
    ru=lang=="ru"
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("🇷🇺 Русский",callback_data="set_lang_ru"),
         InlineKeyboardButton("🇬🇧 English",callback_data="set_lang_en")],
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]
    ])
    
    await send_section(update, f"{E['globe']} <b>{R(ru,'Выберите язык','Select language')}</b>", kb, "main")

async def set_lang_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    new_lang="en" if data.endswith("en") else "ru"
    
    db=load_db()
    u=get_user(db, q.from_user.id)
    u["lang"]=new_lang
    save_db(db)
    
    await send_section(update, get_welcome(new_lang), main_kb(new_lang), "main")

# ─── Profile ──────────────────────────────────────────────────────────────────
async def menu_profile_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    uid=q.from_user.id
    
    db=load_db()
    u=get_user(db, uid)
    lang=u.get("lang","ru")
    ru=lang=="ru"
    
    total=u.get("total_deals",0)
    success=u.get("success_deals",0)
    turn=u.get("turnover",0)
    reviews=u.get("reviews",[])
    nrev=len(reviews)
    rating=calc_rating(reviews)
    bal=u.get("balance",0)
    st=u.get("status","")
    
    rating_stars = "⭐" * int(rating) if rating > 0 else ""
    
    text=(
        f"{Eu} <b>{R(ru,'Ваш профиль','Your profile')}</b>\n\n"
        f"{Edl} {R(ru,'Всего сделок','Total deals')}: <b>{total}</b>\n"
        f"{Ech} {R(ru,'Успешных','Successful')}: <b>{success}</b>\n"
        f"{Emn} {R(ru,'Оборот','Turnover')}: <b>{turn} ₽</b>\n"
        f"{Estr} {R(ru,'Отзывов','Reviews')}: <b>{nrev}</b> {rating_stars} <b>{rating}/5</b>\n"
        f"{Ebal} {R(ru,'Баланс','Balance')}: <b>{bal} ₽</b>"
    )
    
    if st: 
        text+=f"\n{Emdl} <b>{st}</b>"
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]
    ])
    
    await send_section(update, text, kb, "profile")

# ─── Top ──────────────────────────────────────────────────────────────────────
async def menu_top_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    
    db=load_db()
    lang=get_lang(q.from_user.id)
    ru=lang=="ru"
    
    users=sorted(
        db.get("users",{}).items(), 
        key=lambda x: x[1].get("success_deals",0), 
        reverse=True
    )[:10]
    
    lines=[f"{Etph} <b>{R(ru,'Топ продавцов','Top sellers')}</b>\n"]
    
    for i,(uid_s,usr) in enumerate(users,1):
        uname=usr.get("username","") or R(ru,"Аноним","Anonymous")
        deals=usr.get("success_deals",0)
        turn=usr.get("turnover",0)
        reviews=usr.get("reviews",[])
        rating=calc_rating(reviews)
        st=usr.get("status","")
        
        medal=""
        if i==1: medal="🥇 "
        elif i==2: medal="🥈 "
        elif i==3: medal="🥉 "
        
        status_txt=f" • {st}" if st else ""
        rating_stars = "⭐" * int(rating) if rating > 0 else ""
        
        lines.append(
            f"{medal}<b>{i}.</b> @{uname} — {deals} {R(ru,'сделок','deals')}, "
            f"{turn} ₽ {rating_stars} {rating}/5{status_txt}"
        )
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]
    ])
    
    await send_section(update, "\n".join(lines), kb, "top")

# ─── Referrals ────────────────────────────────────────────────────────────────
async def menu_ref_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    uid=q.from_user.id
    
    db=load_db()
    u=get_user(db, uid)
    lang=u.get("lang","ru")
    ru=lang=="ru"
    
    ref_count=u.get("ref_count",0)
    ref_earned=u.get("ref_earned",0)
    ref_link=f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"
    
    text=(
        f"{Ejn} <b>{R(ru,'Реферальная программа','Referral program')}</b>\n\n"
        f"{R(ru,'Приглашайте друзей и получайте','Invite friends and get')} <b>5%</b> "
        f"{R(ru,'от их оборота','from their turnover')}!\n\n"
        f"{Esrk} {R(ru,'Рефералов','Referrals')}: <b>{ref_count}</b>\n"
        f"{Emn} {R(ru,'Заработано','Earned')}: <b>{ref_earned} ₽</b>\n\n"
        f"{Eln} {R(ru,'Ваша ссылка','Your link')}:\n<code>{ref_link}</code>"
    )
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]
    ])
    
    await send_section(update, text, kb, "ref")

# ─── Requisites ───────────────────────────────────────────────────────────────
async def menu_req_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    uid=q.from_user.id
    
    db=load_db()
    u=get_user(db, uid)
    lang=u.get("lang","ru")
    ru=lang=="ru"
    
    req=u.get("requisites",{})
    text=f"{Ereq} <b>{R(ru,'Ваши реквизиты','Your requisites')}</b>\n\n"
    
    if req.get("card"):
        text+=f"{Ecrd} {R(ru,'Карта','Card')}: <code>{req['card']}</code>\n"
    if req.get("phone"):
        text+=f"{Ephn} {R(ru,'Телефон','Phone')}: <code>{req['phone']}</code>\n"
    if req.get("ton"):
        text+=f"{Eton} TON: <code>{req['ton']}</code>\n"
    
    if not any(req.values()):
        text+=R(ru,
            "Реквизиты не добавлены. Нажмите кнопку ниже для добавления.",
            "No requisites added. Press the button below to add."
        )
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            Epen+" "+R(ru,"Изменить реквизиты","Edit requisites"),
            callback_data="req_edit"
        )],
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]
    ])
    
    await send_section(update, text, kb, "profile")

async def req_edit_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    uid=q.from_user.id
    lang=get_lang(uid)
    ru=lang=="ru"
    
    db=load_db()
    u=get_user(db, uid)
    req=u.get("requisites",{})
    
    buttons=[]
    if req.get("card"):
        buttons.append([
            InlineKeyboardButton(Ecrd+" "+R(ru,"Изменить карту","Edit card"),callback_data="req_add_card"),
            InlineKeyboardButton("🗑",callback_data="req_del_card")
        ])
    else:
        buttons.append([InlineKeyboardButton(Ecrd+" "+R(ru,"Добавить карту","Add card"),callback_data="req_add_card")])
    
    if req.get("phone"):
        buttons.append([
            InlineKeyboardButton(Ephn+" "+R(ru,"Изменить телефон","Edit phone"),callback_data="req_add_phone"),
            InlineKeyboardButton("🗑",callback_data="req_del_phone")
        ])
    else:
        buttons.append([InlineKeyboardButton(Ephn+" "+R(ru,"Добавить телефон","Add phone"),callback_data="req_add_phone")])
    
    if req.get("ton"):
        buttons.append([
            InlineKeyboardButton(Eton+" "+R(ru,"Изменить TON","Edit TON"),callback_data="req_add_ton"),
            InlineKeyboardButton("🗑",callback_data="req_del_ton")
        ])
    else:
        buttons.append([InlineKeyboardButton(Eton+" "+R(ru,"Добавить TON","Add TON"),callback_data="req_add_ton")])
    
    buttons.append([InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_req")])
    
    text=f"{Epen} <b>{R(ru,'Выберите тип реквизита','Select requisite type')}</b>"
    await send_section(update, text, InlineKeyboardMarkup(buttons), "profile")

async def req_add_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    uid=q.from_user.id
    lang=get_lang(uid)
    ru=lang=="ru"
    
    req_type=""
    if "card" in data: req_type="card"
    elif "phone" in data: req_type="phone"
    elif "ton" in data: req_type="ton"
    
    context.user_data["req_type"]=req_type
    context.user_data["state"]="req_input"
    
    prompt=""
    if req_type=="card":
        prompt=R(ru,"Отправьте номер карты (16 цифр)","Send card number (16 digits)")
    elif req_type=="phone":
        prompt=R(ru,"Отправьте номер телефона","Send phone number")
    elif req_type=="ton":
        prompt=R(ru,"Отправьте TON адрес (UQ или EQ)","Send TON address (UQ or EQ)")
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ "+R(ru,"Отмена","Cancel"),callback_data="req_cancel")]
    ])
    
    await send_new(update, f"{Epen} <b>{prompt}</b>", kb, "profile")

async def req_del_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    uid=q.from_user.id
    
    db=load_db()
    u=get_user(db, uid)
    
    if "card" in data:
        u.setdefault("requisites",{}).pop("card",None)
    elif "phone" in data:
        u.setdefault("requisites",{}).pop("phone",None)
    elif "ton" in data:
        u.setdefault("requisites",{}).pop("ton",None)
    
    save_db(db)
    await menu_req_cb(update, context)

async def req_cancel_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    context.user_data.pop("state",None)
    context.user_data.pop("req_type",None)
    
    # Проверяем откуда пришли
    if context.user_data.get("req_from")=="withdraw":
        context.user_data.pop("req_from",None)
        await balance_withdraw_cb(update, context)
    else:
        await menu_req_cb(update, context)

async def req_for_deal_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переход к добавлению реквизитов для участия в сделке"""
    q=update.callback_query
    await q.answer()
    data=q.data
    deal_id=data.replace("req_for_deal_","")
    
    context.user_data["pending_deal"]=deal_id
    await req_edit_cb(update, context)

async def req_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state")!="req_input": 
        return
    
    uid=update.effective_user.id
    text=update.message.text.strip()
    
    db=load_db()
    u=get_user(db, uid)
    lang=u.get("lang","ru")
    ru=lang=="ru"
    
    req_type=context.user_data.get("req_type")
    
    if req_type=="card":
        cleaned=validate_card(text)
        if not cleaned:
            await update.message.reply_text(
                R(ru,"❌ Неверный формат карты","❌ Invalid card format")
            )
            return
        u.setdefault("requisites",{})["card"]=cleaned
    elif req_type=="phone":
        u.setdefault("requisites",{})["phone"]=text
    elif req_type=="ton":
        if not validate_ton_address(text):
            await update.message.reply_text(
                R(ru,"❌ Неверный TON адрес","❌ Invalid TON address")
            )
            return
        u.setdefault("requisites",{})["ton"]=text
    
    save_db(db)
    context.user_data.pop("state",None)
    context.user_data.pop("req_type",None)
    
    await update.message.reply_text(
        R(ru,"✅ Реквизит сохранён","✅ Requisite saved")
    )
    
    # Проверяем откуда пришли
    pending_deal=context.user_data.pop("pending_deal",None)
    req_from=context.user_data.pop("req_from",None)
    
    if pending_deal:
        # Возвращаем к сделке
        db2=load_db()
        d=db2.get("deals",{}).get(pending_deal)
        if d:
            # Присоединяемся автоматически
            d["partner_id"]=uid
            d["status"]="active"
            save_db(db2)
            
            add_log(db2, R(ru,"Присоединение к сделке","Joined deal"), 
                    deal_id=pending_deal, uid=uid, username=u.get("username",""))
            await send_log_msg(context, db2, db2["logs"][-1])
            
            creator_id=d.get("user_id")
            creator_uname=db2["users"].get(str(creator_id),{}).get("username","") if creator_id else ""
            creator_tag=f"@{creator_uname}" if creator_uname else f"#{creator_id}"
            
            uname=u.get("username","")
            partner_tag=f"@{uname}" if uname else f"#{uid}"
            
            text_deal=build_deal_text(pending_deal, d, creator_tag, partner_tag, lang, joined=True)
            
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ "+R(ru,"Я оплатил","I paid"),callback_data=f"deal_paid_{pending_deal}")],
                [InlineKeyboardButton("💬 "+R(ru,"Связаться с менеджером","Contact manager"),url=MANAGER_URL)],
                [InlineKeyboardButton("🔙 "+R(ru,"Главное меню","Main menu"),callback_data="main_menu")]
            ])
            
            await send_new(update, text_deal, kb, "deal_card")
            return
    elif req_from=="withdraw":
        # Возвращаем к выводу
        await balance_withdraw_cb(update, context)
        return
    
    # Иначе в меню реквизитов
    await menu_req_cb(update, context)

# ─── Balance ──────────────────────────────────────────────────────────────────
async def menu_balance_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    uid=q.from_user.id
    
    db=load_db()
    u=get_user(db, uid)
    lang=u.get("lang","ru")
    ru=lang=="ru"
    bal=u.get("balance",0)
    
    text=(
        f"{Ebal} <b>{R(ru,'Баланс','Balance')}</b>: <b>{bal} ₽</b>\n\n"
        f"{R(ru,'Выберите действие:','Choose action:')}"
    )
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("💸 "+R(ru,"Пополнить","Top up"),callback_data="balance_topup")],
        [InlineKeyboardButton("💰 "+R(ru,"Вывести","Withdraw"),callback_data="balance_withdraw")],
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]
    ])
    
    await send_section(update, text, kb, "balance")

async def balance_topup_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    lang=get_lang(q.from_user.id)
    ru=lang=="ru"
    
    text=(
        f"{Ecrd} <b>{R(ru,'Пополнение баланса','Balance top up')}</b>\n\n"
        f"<b>{R(ru,'Карта','Card')}:</b> <code>{CARD_NUM}</code>\n"
        f"{R(ru,'Банк','Bank')}: {card_bank(lang)}\n"
        f"{R(ru,'Получатель','Recipient')}: {CARD_NAME}\n\n"
        f"<b>{Eton} TON/USDT:</b>\n"
        f"{CRYPTO_BOT}\n\n"
        f"{Ewrn} <b>{R(ru,'После оплаты свяжитесь с','After payment contact')} {MANAGER_TAG}</b>"
    )
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_balance")]
    ])
    
    await send_section(update, text, kb, "balance")

async def balance_withdraw_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    uid=q.from_user.id
    
    db=load_db()
    u=get_user(db, uid)
    lang=u.get("lang","ru")
    ru=lang=="ru"
    
    req=u.get("requisites",{})
    if not any(req.values()):
        text=R(ru,
            "❌ Сначала добавьте реквизиты в меню 'Реквизиты'",
            "❌ First add requisites in 'Requisites' menu"
        )
        context.user_data["req_from"]="withdraw"
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "📋 "+R(ru,"Добавить реквизиты","Add requisites"),
                callback_data="req_edit"
            )],
            [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_balance")]
        ])
        await send_new(update, text, kb, "balance")
        return
    
    text=(
        f"{Ewlt} <b>{R(ru,'Вывод средств','Withdraw funds')}</b>\n\n"
        f"{R(ru,'Свяжитесь с менеджером для вывода:','Contact manager for withdrawal:')} {MANAGER_TAG}"
    )
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_balance")]
    ])
    
    await send_section(update, text, kb, "balance")

# ─── My Deals ─────────────────────────────────────────────────────────────────
async def menu_my_deals_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    uid=q.from_user.id
    
    db=load_db()
    lang=get_lang(uid)
    ru=lang=="ru"
    
    my_deals=[
        (did,d) for did,d in db.get("deals",{}).items()
        if str(d.get("user_id"))==str(uid) or str(d.get("partner_id"))==str(uid)
    ]
    
    if not my_deals:
        text=R(ru,"❌ У вас пока нет сделок","❌ You have no deals yet")
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]
        ])
        await send_section(update, text, kb, "my_deals")
        return
    
    text=f"{Edl} <b>{R(ru,'Ваши сделки','Your deals')}</b>\n\n"
    buttons=[]
    
    for did,d in my_deals[:20]:
        dtype=d.get("type","")
        amt=d.get("amount","")
        cur=d.get("currency","")
        
        status_ico={
            "waiting":"⏳",
            "active":"🔄",
            "completed":"✅",
            "cancelled":"❌"
        }.get(d.get("status","waiting"),"⏳")
        
        cur_display=cur_with_emoji(cur, lang)
        
        buttons.append([
            InlineKeyboardButton(
                f"{status_ico} #{did} • {tname(dtype,lang)} • {amt} {cur_display}",
                callback_data=f"deal_view_{did}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")
    ])
    
    await send_section(update, text, InlineKeyboardMarkup(buttons), "my_deals")

# ─── Create Deal ──────────────────────────────────────────────────────────────
async def menu_deal_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    uid=q.from_user.id
    
    db=load_db()
    u=get_user(db, uid)
    lang=u.get("lang","ru")
    ru=lang=="ru"
    
    # НЕ проверяем реквизиты для продавца
    text=f"{Edl} <b>{R(ru,'Кто вы в сделке?','Who are you in the deal?')}</b>"
    await send_section(update, text, role_kb(lang), "deal")

async def role_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    uid=q.from_user.id
    
    role="buyer" if "buyer" in data else "seller"
    context.user_data["deal_role"]=role
    
    lang=get_lang(uid)
    ru=lang=="ru"
    
    # Проверяем реквизиты только для покупателя
    if role=="buyer":
        db=load_db()
        u=get_user(db, uid)
        req=u.get("requisites",{})
        
        if not any(req.get(f) for f in ("card","phone","ton")):
            text=(
                f"{Ewrn} <b>{R(ru,'Добавьте реквизиты','Add requisites')}</b>\n\n"
                f"{R(ru,'Покупателю необходимо добавить реквизиты для получения средств','Buyer needs to add requisites to receive funds')}"
            )
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "📋 "+R(ru,"Добавить реквизиты","Add requisites"),
                    callback_data="req_edit"
                )],
                [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_deal")]
            ])
            await send_section(update, text, kb, "deal")
            return
    
    text=f"{Egft} <b>{R(ru,'Выберите тип сделки','Choose deal type')}</b>"
    await send_section(update, text, types_kb(lang), "deal")

async def type_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    
    dtype=""
    if "nft" in data: dtype="nft"
    elif "usr" in data: dtype="username"
    elif "str" in data: dtype="stars"
    elif "cry" in data: dtype="crypto"
    elif "prm" in data: dtype="premium"
    
    context.user_data["deal_type"]=dtype
    lang=get_lang(q.from_user.id)
    ru=lang=="ru"
    
    if dtype=="nft":
        context.user_data["state"]="nft_link"
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ "+R(ru,"Отмена","Cancel"),callback_data="deal_cancel")]
        ])
        await send_new(
            update, 
            f"{Eln} <b>{R(ru,'Отправьте ссылку на NFT подарок','Send NFT gift link')}</b>\n"
            f"{R(ru,'Пример','Example')}: https://t.me/nft/gift_12345", 
            kb, 
            "deal"
        )
    elif dtype=="username":
        context.user_data["state"]="username_input"
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ "+R(ru,"Отмена","Cancel"),callback_data="deal_cancel")]
        ])
        await send_new(
            update, 
            f"{Eu} <b>{R(ru,'Отправьте NFT Username','Send NFT Username')}</b>\n"
            f"{R(ru,'Пример','Example')}: @username", 
            kb, 
            "deal"
        )
    elif dtype=="stars":
        context.user_data["state"]="stars_count"
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ "+R(ru,"Отмена","Cancel"),callback_data="deal_cancel")]
        ])
        await send_new(
            update, 
            f"{Est} <b>{R(ru,'Введите сумму звёзд','Enter stars amount')}</b>", 
            kb, 
            "deal"
        )
    elif dtype=="premium":
        context.user_data["state"]="premium_period"
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ "+R(ru,"Отмена","Cancel"),callback_data="deal_cancel")]
        ])
        await send_new(
            update, 
            f"{Eprem} <b>{R(ru,'Укажите срок Premium','Specify Premium period')}</b>\n"
            f"{R(ru,'Например','Example')}: 1 {R(ru,'месяц','month')}, 3 {R(ru,'месяца','months')}", 
            kb, 
            "deal"
        )
    elif dtype=="crypto":
        text=f"{Emn} <b>{R(ru,'Выберите валюту','Choose currency')}</b>"
        await send_section(update, text, cur_kb(lang), "deal")

async def currency_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    
    cur=CURMAP.get(data,"RUB")
    context.user_data["deal_currency"]=cur
    context.user_data["state"]="amount_input"
    
    lang=get_lang(q.from_user.id)
    ru=lang=="ru"
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ "+R(ru,"Отмена","Cancel"),callback_data="deal_cancel")]
    ])
    
    await send_new(
        update, 
        f"{Emn} <b>{R(ru,'Укажите сумму сделки','Specify deal amount')}</b>", 
        kb, 
        "deal"
    )

async def deal_cancel_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    context.user_data.clear()
    await main_menu_cb(update, context)

async def deal_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state=context.user_data.get("state")
    if not state or state=="req_input": 
        return
    
    uid=update.effective_user.id
    text=update.message.text.strip()
    
    db=load_db()
    u=get_user(db, uid)
    lang=u.get("lang","ru")
    ru=lang=="ru"
    
    if state=="nft_link":
        valid,err=validate_nft_link(text, "nft")
        if not valid:
            if err=="no_tme":
                await update.message.reply_text(
                    R(ru,"❌ Ссылка должна начинаться с t.me/nft/","❌ Link must start with t.me/nft/")
                )
            else:
                await update.message.reply_text(
                    R(ru,"❌ Неверный формат ссылки","❌ Invalid link format")
                )
            return
        context.user_data["nft_link"]=text
        text_msg=f"{Emn} <b>{R(ru,'Выберите валюту','Choose currency')}</b>"
        await update.message.reply_text(text_msg, reply_markup=cur_kb(lang), parse_mode="HTML")
        context.user_data.pop("state",None)
        
    elif state=="username_input":
        validated,err=validate_username(text)
        if not validated:
            if err=="no_at":
                await update.message.reply_text(
                    R(ru,"❌ Username должен начинаться с @","❌ Username must start with @")
                )
            elif err=="short":
                await update.message.reply_text(
                    R(ru,"❌ Username слишком короткий (минимум 4 символа)","❌ Username too short (minimum 4 chars)")
                )
            else:
                await update.message.reply_text(
                    R(ru,"❌ Недопустимые символы в username","❌ Invalid characters in username")
                )
            return
        context.user_data["trade_username"]=validated
        text_msg=f"{Emn} <b>{R(ru,'Выберите валюту','Choose currency')}</b>"
        await update.message.reply_text(text_msg, reply_markup=cur_kb(lang), parse_mode="HTML")
        context.user_data.pop("state",None)
        
    elif state=="stars_count":
        if not text.isdigit():
            await update.message.reply_text(
                R(ru,"❌ Укажите число","❌ Enter a number")
            )
            return
        context.user_data["stars_count"]=text
        text_msg=f"{Emn} <b>{R(ru,'Выберите валюту','Choose currency')}</b>"
        await update.message.reply_text(text_msg, reply_markup=cur_kb(lang), parse_mode="HTML")
        context.user_data.pop("state",None)
        
    elif state=="premium_period":
        context.user_data["premium_period"]=text
        text_msg=f"{Emn} <b>{R(ru,'Выберите валюту','Choose currency')}</b>"
        await update.message.reply_text(text_msg, reply_markup=cur_kb(lang), parse_mode="HTML")
        context.user_data.pop("state",None)
        
    elif state=="amount_input":
        if not text.replace(".","").replace(",","").isdigit():
            await update.message.reply_text(
                R(ru,"❌ Укажите число","❌ Enter a number")
            )
            return
        context.user_data["deal_amount"]=text.replace(",",".")
        context.user_data["state"]="partner_input"
        
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ "+R(ru,"Отмена","Cancel"),callback_data="deal_cancel")]
        ])
        await update.message.reply_text(
            f"{Eu} <b>{R(ru,'Укажите username второй стороны','Specify counterparty username')}</b>\n"
            f"{R(ru,'Пример','Example')}: @username",
            reply_markup=kb, 
            parse_mode="HTML"
        )
        
    elif state=="partner_input":
        validated,err=validate_username(text)
        if not validated:
            if err=="no_at":
                await update.message.reply_text(
                    R(ru,"❌ Username должен начинаться с @","❌ Username must start with @")
                )
            elif err=="short":
                await update.message.reply_text(
                    R(ru,"❌ Username слишком короткий","❌ Username too short")
                )
            else:
                await update.message.reply_text(
                    R(ru,"❌ Недопустимые символы","❌ Invalid characters")
                )
            return
        
        dtype=context.user_data.get("deal_type","")
        cur=context.user_data.get("deal_currency","RUB")
        amt=context.user_data.get("deal_amount","0")
        role=context.user_data.get("deal_role","seller")
        
        deal_data={}
        if dtype=="nft": 
            deal_data["nft_link"]=context.user_data.get("nft_link","")
        elif dtype=="username": 
            deal_data["trade_username"]=context.user_data.get("trade_username","")
        elif dtype=="stars": 
            deal_data["stars_count"]=context.user_data.get("stars_count","")
        elif dtype=="premium": 
            deal_data["premium_period"]=context.user_data.get("premium_period","")
        
        deal_id=gen_deal_id(db)
        db["deals"][deal_id]={
            "type":dtype,
            "currency":cur,
            "amount":amt,
            "data":deal_data,
            "user_id":uid,
            "partner":validated,
            "partner_id":None,
            "status":"waiting",
            "creator_role":role,
            "created":datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        save_db(db)
        
        context.user_data.clear()
        
        add_log(db, R(ru,"Создана сделка","Deal created"), 
                deal_id=deal_id, uid=uid, username=u.get("username",""))
        await send_log_msg(context, db, db["logs"][-1])
        
        link=f"https://t.me/{BOT_USERNAME}?start=deal_{deal_id}"
        text_done=(
            f"{Ech} <b>{R(ru,'Сделка создана','Deal created')} #{deal_id}</b>\n\n"
            f"{R(ru,'Отправьте эту ссылку второй стороне','Send this link to counterparty')}:\n"
            f"<code>{link}</code>"
        )
        
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 "+R(ru,"В главное меню","To main menu"),callback_data="main_menu")]
        ])
        
        await update.message.reply_text(text_done, reply_markup=kb, parse_mode="HTML")

# ─── View Deal ────────────────────────────────────────────────────────────────
async def deal_view_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    deal_id=data.split("_")[-1]
    uid=q.from_user.id
    
    db=load_db()
    lang=get_lang(uid)
    ru=lang=="ru"
    
    d=db.get("deals",{}).get(deal_id)
    if not d:
        await q.message.edit_text(
            R(ru,"❌ Сделка не найдена","❌ Deal not found")
        )
        return
    
    creator_id=d.get("user_id")
    partner_id=d.get("partner_id")
    
    creator_uname=db["users"].get(str(creator_id),{}).get("username","") if creator_id else ""
    partner_uname=d.get("partner","").lstrip("@")
    
    creator_tag=f"@{creator_uname}" if creator_uname else R(ru,"Неизвестен","Unknown")
    partner_tag=f"@{partner_uname}" if partner_uname else R(ru,"Неизвестен","Unknown")
    
    joined=bool(partner_id)
    text=build_deal_text(deal_id, d, creator_tag, partner_tag, lang, joined)
    
    buttons=[]
    
    if not joined and str(uid)!=str(creator_id):
        buttons.append([
            InlineKeyboardButton(
                Ejn+" "+R(ru,"Присоединиться","Join"),
                callback_data=f"deal_join_{deal_id}"
            )
        ])
    
    status=d.get("status","waiting")
    
    if status=="active":
        buttons.append([
            InlineKeyboardButton(
                "✅ "+R(ru,"Я оплатил","I paid"),
                callback_data=f"deal_paid_{deal_id}"
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                Ech+" "+R(ru,"Завершить сделку","Complete deal"),
                callback_data=f"deal_confirm_{deal_id}"
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                Etgt+" "+R(ru,"Отменить сделку","Cancel deal"),
                callback_data=f"deal_cancel_confirm_{deal_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_my_deals")
    ])
    
    await send_section(update, text, InlineKeyboardMarkup(buttons), "deal_card")

async def deal_join_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    deal_id=data.split("_")[-1]
    uid=q.from_user.id
    
    db=load_db()
    u=get_user(db, uid)
    lang=u.get("lang","ru")
    ru=lang=="ru"
    
    d=db.get("deals",{}).get(deal_id)
    if not d:
        await q.message.edit_text(
            R(ru,"❌ Сделка не найдена","❌ Deal not found")
        )
        return
    
    if d.get("partner_id"):
        await q.answer(
            R(ru,"❌ Сделка уже занята","❌ Deal already taken"), 
            show_alert=True
        )
        return
    
    partner_expected=d.get("partner","").lstrip("@").lower()
    user_uname=u.get("username","").lower()
    
    if partner_expected and user_uname!=partner_expected:
        await q.answer(
            R(ru,"❌ Эта сделка предназначена для другого пользователя","❌ This deal is for another user"), 
            show_alert=True
        )
        return
    
    # Проверка реквизитов
    req=u.get("requisites",{})
    if not any(req.get(f) for f in ("card","phone","ton")):
        text=(
            f"{Ewrn} <b>{R(ru,'Добавьте реквизиты','Add requisites')}</b>\n\n"
            f"{R(ru,'Для участия в сделке необходимо добавить реквизиты','To participate you need to add requisites')}"
        )
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "📋 "+R(ru,"Добавить реквизиты","Add requisites"),
                callback_data=f"req_for_deal_{deal_id}"
            )],
            [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data=f"deal_view_{deal_id}")]
        ])
        context.user_data["pending_deal"]=deal_id
        await send_new(update, text, kb, "deal_card")
        return
    
    d["partner_id"]=uid
    d["status"]="active"
    save_db(db)
    
    add_log(db, R(ru,"Присоединение к сделке","Joined deal"), 
            deal_id=deal_id, uid=uid, username=u.get("username",""))
    await send_log_msg(context, db, db["logs"][-1])
    
    await deal_view_cb(update, context)

async def deal_paid_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатия 'Я оплатил'"""
    q=update.callback_query
    await q.answer()
    data=q.data
    deal_id=data.split("_")[-1]
    uid=q.from_user.id
    
    db=load_db()
    lang=get_lang(uid)
    ru=lang=="ru"
    
    d=db.get("deals",{}).get(deal_id)
    if not d:
        return
    
    # Уведомляем админа
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"{Ebl} <b>Оплата по сделке</b>\n\n"
                 f"#{deal_id}\n"
                 f"От: <code>{uid}</code>\n"
                 f"Сумма: {d.get('amount','')} {d.get('currency','')}",
            parse_mode="HTML"
        )
    except:
        pass
    
    add_log(db, R(ru,"Оплата","Payment"), 
            deal_id=deal_id, uid=uid)
    await send_log_msg(context, db, db["logs"][-1])
    
    await q.answer(
        R(ru,"✅ Уведомление отправлено менеджеру","✅ Notification sent to manager"),
        show_alert=True
    )

async def deal_confirm_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    deal_id=data.split("_")[-1]
    uid=q.from_user.id
    
    db=load_db()
    lang=get_lang(uid)
    ru=lang=="ru"
    
    d=db.get("deals",{}).get(deal_id)
    if not d:
        return
    
    # Проверяем права
    if str(d.get("user_id"))!=str(uid) and str(d.get("partner_id"))!=str(uid):
        await q.answer(
            R(ru,"❌ Нет доступа","❌ No access"), 
            show_alert=True
        )
        return
    
    d["status"]="completed"
    
    # Начисляем статистику
    creator_id=d.get("user_id")
    if creator_id and str(creator_id) in db["users"]:
        db["users"][str(creator_id)]["success_deals"]=db["users"][str(creator_id)].get("success_deals",0)+1
        db["users"][str(creator_id)]["total_deals"]=db["users"][str(creator_id)].get("total_deals",0)+1
        try:
            amt=int(float(d.get("amount","0")))
            db["users"][str(creator_id)]["turnover"]=db["users"][str(creator_id)].get("turnover",0)+amt
        except:
            pass
    
    save_db(db)
    
    add_log(db, R(ru,"Сделка завершена","Deal completed"), 
            deal_id=deal_id, uid=uid)
    await send_log_msg(context, db, db["logs"][-1])
    
    await q.answer(
        R(ru,"✅ Сделка завершена","✅ Deal completed"), 
        show_alert=True
    )
    
    # Показываем обновлённую карточку без инструкций
    creator_uname=db["users"].get(str(creator_id),{}).get("username","") if creator_id else ""
    creator_tag=f"@{creator_uname}" if creator_uname else f"#{creator_id}"
    
    partner_id=d.get("partner_id")
    partner_uname=db["users"].get(str(partner_id),{}).get("username","") if partner_id else d.get("partner","").lstrip("@")
    partner_tag=f"@{partner_uname}" if partner_uname else R(ru,"Неизвестен","Unknown")
    
    text=build_deal_text(deal_id, d, creator_tag, partner_tag, lang, joined=True)
    text+=f"\n\n{Ech} <b>{R(ru,'Сделка успешно завершена!','Deal successfully completed!')}</b>"
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 "+R(ru,"К моим сделкам","To my deals"),callback_data="menu_my_deals")]
    ])
    
    await send_section(update, text, kb, "deal_card")

async def deal_cancel_confirm_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    deal_id=data.split("_")[-1]
    lang=get_lang(q.from_user.id)
    ru=lang=="ru"
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton(
            Ech+" "+R(ru,"Подтвердить отмену","Confirm cancellation"),
            callback_data=f"deal_cancel_yes_{deal_id}"
        )],
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data=f"deal_view_{deal_id}")]
    ])
    
    text=f"{Ewrn} <b>{R(ru,'Вы уверены, что хотите отменить сделку?','Are you sure you want to cancel the deal?')}</b>"
    await send_section(update, text, kb, "deal_card")

async def deal_cancel_yes_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()
    data=q.data
    deal_id=data.split("_")[-1]
    uid=q.from_user.id
    
    db=load_db()
    lang=get_lang(uid)
    ru=lang=="ru"
    
    d=db.get("deals",{}).get(deal_id)
    if not d:
        await q.answer(
            R(ru,"❌ Сделка не найдена","❌ Deal not found"), 
            show_alert=True
        )
        return
    
    d["status"]="cancelled"
    save_db(db)
    
    add_log(db, R(ru,"Сделка отменена","Deal cancelled"), 
            deal_id=deal_id, uid=uid)
    await send_log_msg(context, db, db["logs"][-1])
    
    await q.answer(
        R(ru,"✅ Сделка отменена","✅ Deal cancelled"), 
        show_alert=True
    )
    
    await deal_view_cb(update, context)

# ─── Admin ────────────────────────────────────────────────────────────────────
async def neptuneteam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: 
        return
    
    db=load_db()
    
    text=(
        "<b>🔧 Neptune Admin Panel</b>\n\n"
        "Команды:\n"
        "/admin - админ панель\n"
        "/add_balance [uid] [сумма]\n"
        "/take_balance [uid] [сумма]\n"
        "/add_review [uid] [текст] - добавить отзыв\n"
        "/my_reviews [uid] - показать отзывы\n"
        "/del_review [uid] [номер] - удалить отзыв\n"
        "/add_req [uid] [тип] [значение] - добавить реквизит\n"
        "/del_req [uid] [тип] - удалить реквизит\n"
        "/logs - показать логи"
    )
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Логи",callback_data="adm_logs")],
        [InlineKeyboardButton("🎨 Баннеры",callback_data="adm_banners")],
    ])
    
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: 
        return
    
    db=load_db()
    text=f"<b>📊 Админ панель</b>\n\nПользователей: {len(db.get('users',{}))}\nСделок: {len(db.get('deals',{}))}"
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Логи",callback_data="adm_logs")],
        [InlineKeyboardButton("🎨 Баннеры",callback_data="adm_banners")],
    ])
    
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

async def add_balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: 
        return
    
    args=context.args
    if len(args)<2:
        await update.message.reply_text(
            "<b>Использование: /add_balance [uid] [сумма]</b>", 
            parse_mode="HTML"
        )
        return
    
    target_uid=args[0]
    amount=args[1]
    
    try:
        amount_int=int(amount)
    except:
        await update.message.reply_text(
            "<b>❌ Сумма должна быть числом</b>", 
            parse_mode="HTML"
        )
        return
    
    db=load_db()
    u=get_user(db, target_uid)
    u["balance"]=u.get("balance",0)+amount_int
    save_db(db)
    
    await update.message.reply_text(
        f"<b>✅ Баланс пополнен!\n\nUID: {target_uid}\n+{amount_int} ₽</b>", 
        parse_mode="HTML"
    )

async def take_balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: 
        return
    
    args=context.args
    if len(args)<2:
        await update.message.reply_text(
            "<b>Использование: /take_balance [uid] [сумма]</b>", 
            parse_mode="HTML"
        )
        return
    
    target_uid=args[0]
    amount=args[1]
    
    try:
        amount_int=int(amount)
    except:
        await update.message.reply_text(
            "<b>❌ Сумма должна быть числом</b>", 
            parse_mode="HTML"
        )
        return
    
    db=load_db()
    u=get_user(db, target_uid)
    u["balance"]=max(0, u.get("balance",0)-amount_int)
    save_db(db)
    
    await update.message.reply_text(
        f"<b>✅ Баланс списан!\n\nUID: {target_uid}\n-{amount_int} ₽</b>", 
        parse_mode="HTML"
    )

async def add_review_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить отзыв пользователю"""
    if update.effective_user.id!=ADMIN_ID: 
        return
    
    args=context.args
    if len(args)<2:
        await update.message.reply_text(
            "<b>Использование: /add_review [uid] [текст]\nПример: /add_review 123456 ⭐ 5/5 - Отличный продавец!</b>", 
            parse_mode="HTML"
        )
        return
    
    target_uid=args[0]
    review_text=" ".join(args[1:])
    
    db=load_db()
    u=get_user(db, target_uid)
    u.setdefault("reviews",[]).append(review_text)
    save_db(db)
    
    await update.message.reply_text(
        f"<b>✅ Отзыв добавлен!\n\nUID: {target_uid}\nТекст: {review_text}</b>", 
        parse_mode="HTML"
    )

async def my_reviews_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать отзывы пользователя"""
    if update.effective_user.id!=ADMIN_ID: 
        return
    
    args=context.args
    if len(args)<1:
        await update.message.reply_text(
            "<b>Использование: /my_reviews [uid]</b>", 
            parse_mode="HTML"
        )
        return
    
    target_uid=args[0]
    
    db=load_db()
    u=get_user(db, target_uid)
    reviews=u.get("reviews",[])
    
    if not reviews:
        await update.message.reply_text(
            f"<b>Отзывов нет для UID: {target_uid}</b>", 
            parse_mode="HTML"
        )
        return
    
    text=f"<b>Отзывы для UID: {target_uid}</b>\n\n"
    for i,rev in enumerate(reviews,1):
        text+=f"<b>{i}.</b> {rev}\n"
    
    await update.message.reply_text(text, parse_mode="HTML")

async def del_review_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить отзыв"""
    if update.effective_user.id!=ADMIN_ID: 
        return
    
    args=context.args
    if len(args)<2:
        await update.message.reply_text(
            "<b>Использование: /del_review [uid] [номер]\nПример: /del_review 123456 1</b>", 
            parse_mode="HTML"
        )
        return
    
    target_uid=args[0]
    try:
        review_num=int(args[1])-1
    except:
        await update.message.reply_text(
            "<b>❌ Номер должен быть числом</b>", 
            parse_mode="HTML"
        )
        return
    
    db=load_db()
    u=get_user(db, target_uid)
    reviews=u.get("reviews",[])
    
    if review_num<0 or review_num>=len(reviews):
        await update.message.reply_text(
            f"<b>❌ Нет отзыва с номером {review_num+1}</b>", 
            parse_mode="HTML"
        )
        return
    
    removed=reviews.pop(review_num)
    save_db(db)
    
    await update.message.reply_text(
        f"<b>✅ Отзыв удалён!\n\nUID: {target_uid}\nТекст: {removed}</b>", 
        parse_mode="HTML"
    )

async def add_req_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить реквизит"""
    if update.effective_user.id!=ADMIN_ID: 
        return
    
    args=context.args
    if len(args)<3:
        await update.message.reply_text(
            "<b>Использование: /add_req [uid] [card/phone/ton] [значение]\nПример: /add_req 123456 card 1234567890123456</b>", 
            parse_mode="HTML"
        )
        return
    
    target_uid=args[0]
    req_type=args[1]
    req_value=" ".join(args[2:])
    
    if req_type not in ["card","phone","ton"]:
        await update.message.reply_text(
            "<b>❌ Тип должен быть: card, phone или ton</b>", 
            parse_mode="HTML"
        )
        return
    
    db=load_db()
    u=get_user(db, target_uid)
    u.setdefault("requisites",{})[req_type]=req_value
    save_db(db)
    
    await update.message.reply_text(
        f"<b>✅ Реквизит добавлен!\n\nUID: {target_uid}\nТип: {req_type}\nЗначение: {req_value}</b>", 
        parse_mode="HTML"
    )

async def del_req_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить реквизит"""
    if update.effective_user.id!=ADMIN_ID: 
        return
    
    args=context.args
    if len(args)<2:
        await update.message.reply_text(
            "<b>Использование: /del_req [uid] [card/phone/ton]\nПример: /del_req 123456 card</b>", 
            parse_mode="HTML"
        )
        return
    
    target_uid=args[0]
    req_type=args[1]
    
    if req_type not in ["card","phone","ton"]:
        await update.message.reply_text(
            "<b>❌ Тип должен быть: card, phone или ton</b>", 
            parse_mode="HTML"
        )
        return
    
    db=load_db()
    u=get_user(db, target_uid)
    removed=u.setdefault("requisites",{}).pop(req_type,None)
    save_db(db)
    
    if removed:
        await update.message.reply_text(
            f"<b>✅ Реквизит удалён!\n\nUID: {target_uid}\nТип: {req_type}</b>", 
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            f"<b>❌ Реквизит не найден\n\nUID: {target_uid}\nТип: {req_type}</b>", 
            parse_mode="HTML"
        )

async def logs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать логи"""
    if update.effective_user.id!=ADMIN_ID: 
        return
    
    db=load_db()
    logs=db.get("logs",[])[-20:][::-1]
    
    if not logs:
        await update.message.reply_text("<b>Логов нет</b>", parse_mode="HTML")
        return
    
    text="<b>📊 Последние логи:</b>\n\n"
    for log in logs:
        text+=f"<b>{log['time']}</b> {log['event']}\n"
        if log.get("deal_id"):
            text+=f"#{log['deal_id']} "
        if log.get("username"):
            text+=f"@{log['username']} "
        if log.get("uid"):
            text+=f"<code>{log['uid']}</code>"
        if log.get("extra"):
            text+=f"\n{log['extra']}"
        text+="\n\n"
    
    await update.message.reply_text(text[:4000], parse_mode="HTML")

async def adm_logs_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback для логов"""
    q=update.callback_query
    await q.answer()
    
    if q.from_user.id!=ADMIN_ID: 
        return
    
    db=load_db()
    logs=db.get("logs",[])[-20:][::-1]
    
    if not logs:
        await q.message.edit_text("<b>Логов нет</b>", parse_mode="HTML")
        return
    
    text="<b>📊 Последние логи:</b>\n\n"
    for log in logs:
        text+=f"<b>{log['time']}</b> {log['event']}\n"
        if log.get("deal_id"):
            text+=f"#{log['deal_id']} "
        if log.get("username"):
            text+=f"@{log['username']} "
        if log.get("uid"):
            text+=f"<code>{log['uid']}</code>"
        if log.get("extra"):
            text+=f"\n{log['extra']}"
        text+="\n\n"
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Обновить",callback_data="adm_logs")],
        [InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]
    ])
    
    await q.message.edit_text(text[:4000], parse_mode="HTML", reply_markup=kb)

async def adm_banners_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback для баннеров"""
    q=update.callback_query
    await q.answer()
    
    if q.from_user.id!=ADMIN_ID: 
        return
    
    text="<b>🎨 Управление баннерами</b>\n\nИспользуйте команды для настройки баннеров для разных секций бота."
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]
    ])
    
    await q.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

async def adm_back_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в админ меню"""
    q=update.callback_query
    await q.answer()
    
    if q.from_user.id!=ADMIN_ID: 
        return
    
    db=load_db()
    text=f"<b>📊 Админ панель</b>\n\nПользователей: {len(db.get('users',{}))}\nСделок: {len(db.get('deals',{}))}"
    
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Логи",callback_data="adm_logs")],
        [InlineKeyboardButton("🎨 Баннеры",callback_data="adm_banners")],
    ])
    
    await q.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

# ─── Error handler ────────────────────────────────────────────────────────────
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    app=Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("neptuneteam", neptuneteam_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("add_balance", add_balance_cmd))
    app.add_handler(CommandHandler("take_balance", take_balance_cmd))
    app.add_handler(CommandHandler("add_review", add_review_cmd))
    app.add_handler(CommandHandler("my_reviews", my_reviews_cmd))
    app.add_handler(CommandHandler("del_review", del_review_cmd))
    app.add_handler(CommandHandler("add_req", add_req_cmd))
    app.add_handler(CommandHandler("del_req", del_req_cmd))
    app.add_handler(CommandHandler("logs", logs_cmd))
    
    # Main callbacks
    app.add_handler(CallbackQueryHandler(main_menu_cb, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(menu_lang_cb, pattern="^menu_lang$"))
    app.add_handler(CallbackQueryHandler(set_lang_cb, pattern="^set_lang_"))
    app.add_handler(CallbackQueryHandler(menu_profile_cb, pattern="^menu_profile$"))
    app.add_handler(CallbackQueryHandler(menu_top_cb, pattern="^menu_top$"))
    app.add_handler(CallbackQueryHandler(menu_ref_cb, pattern="^menu_ref$"))
    
    # Requisites callbacks
    app.add_handler(CallbackQueryHandler(menu_req_cb, pattern="^menu_req$"))
    app.add_handler(CallbackQueryHandler(req_edit_cb, pattern="^req_edit$"))
    app.add_handler(CallbackQueryHandler(req_add_cb, pattern="^req_add_"))
    app.add_handler(CallbackQueryHandler(req_del_cb, pattern="^req_del_"))
    app.add_handler(CallbackQueryHandler(req_cancel_cb, pattern="^req_cancel$"))
    app.add_handler(CallbackQueryHandler(req_for_deal_cb, pattern="^req_for_deal_"))
    
    # Balance callbacks
    app.add_handler(CallbackQueryHandler(menu_balance_cb, pattern="^menu_balance$"))
    app.add_handler(CallbackQueryHandler(balance_topup_cb, pattern="^balance_topup$"))
    app.add_handler(CallbackQueryHandler(balance_withdraw_cb, pattern="^balance_withdraw$"))
    
    # Deals callbacks
    app.add_handler(CallbackQueryHandler(menu_my_deals_cb, pattern="^menu_my_deals$"))
    app.add_handler(CallbackQueryHandler(menu_deal_cb, pattern="^menu_deal$"))
    app.add_handler(CallbackQueryHandler(role_cb, pattern="^role_"))
    app.add_handler(CallbackQueryHandler(type_cb, pattern="^dt_"))
    app.add_handler(CallbackQueryHandler(currency_cb, pattern="^cur_"))
    app.add_handler(CallbackQueryHandler(deal_cancel_cb, pattern="^deal_cancel$"))
    app.add_handler(CallbackQueryHandler(deal_view_cb, pattern="^deal_view_"))
    app.add_handler(CallbackQueryHandler(deal_join_cb, pattern="^deal_join_"))
    app.add_handler(CallbackQueryHandler(deal_paid_cb, pattern="^deal_paid_"))
    app.add_handler(CallbackQueryHandler(deal_confirm_cb, pattern="^deal_confirm_"))
    app.add_handler(CallbackQueryHandler(deal_cancel_confirm_cb, pattern="^deal_cancel_confirm_"))
    app.add_handler(CallbackQueryHandler(deal_cancel_yes_cb, pattern="^deal_cancel_yes_"))
    
    # Admin callbacks
    app.add_handler(CallbackQueryHandler(adm_logs_cb, pattern="^adm_logs$"))
    app.add_handler(CallbackQueryHandler(adm_banners_cb, pattern="^adm_banners$"))
    app.add_handler(CallbackQueryHandler(adm_back_cb, pattern="^adm_back$"))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, deal_input_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, req_input_handler))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    logger.info("Bot started")
    app.run_polling()

if __name__=="__main__":
    main()
