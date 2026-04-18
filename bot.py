import logging, json, os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN    = '8678016177:AAGW4aLb-JtqDVUdETKr3mU8KUQK9TkM03k'
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

# ─── Premium emoji (в тексты) ─────────────────────────────────────────────────
E_USER    = ce("5199552030615558774","👤")
E_STAR    = ce("5267500801240092311","⭐")
E_DEAL    = ce("5445221832074483553","💼")
E_CHECK   = ce("5274055917766202507","✅")
E_MONEY   = ce("5278467510604160626","💰")
E_DIAMOND = ce("5264713049637409446","💎")
E_NFT     = ce("5193177581888755275","💻")
E_STICK   = ce("5294167145079395967","🛍")
E_PREM    = ce("5377620962390857342","🪙")
E_PENCIL  = ce("5197371802136892976","⛏")
E_BELL    = ce("5312361253610475399","🛒")
E_SHIELD  = ce("5197434882321567830","⭐")
E_WARN    = ce("5447644880824181073","⚠️")
E_SEC     = ce("5197288647275071607","🛡")
E_LINK    = ce("5902449142575141204","🔗")
E_DLNK    = ce("5972261808747057065","🔗")
E_TON     = ce("5397829221605191505","💎")
E_CBOT    = ce("5242606681166220600","🤖")
E_REQ     = ce("5242631901214171852","💳")
E_WALLET  = ce("5893382531037794941","👛")
E_SPARK   = ce("5902449142575141204","🔎")
E_STATS   = ce("5028746137645876535","📊")
E_TROPHY  = ce("5188344996356448758","🏆")
E_STAR2   = ce("5321485469249198987","⭐️")
E_JOIN    = ce("5902335789798265487","🤝")
E_WELCOME = ce("5251340119205501791","👋")
E_BAL     = ce("5424976816530014958","💰")
E_GEM     = ce("5258203794772085854","⚡️")
E_CLOCK   = ce("5429651785352501917","↗️")
E_PIN     = ce("5893297890117292323","📞")
E_NUM1    = ce("5794164805065514131","1️⃣")
E_NUM2    = ce("5794085322400733645","2️⃣")
E_NUM3    = ce("5794280000383358988","3️⃣")
E_NUM4    = ce("5794241397217304511","4️⃣")
CM        = ce("5278467510604160626","💰")

# Дополнительные
E_SHIELD2 = ce("5447414070593739764","🛡")
E_FIRE    = ce("5373100545224608922","🔥")
E_CROWN   = ce("5392699498427405578","👑")
E_LOCK    = ce("5472124911399807202","🔒")
E_OK      = ce("5206607081334906820","✅")
E_GIFT    = ce("5373163891218598706","🎁")
E_ROCKET  = ce("5381072436286190944","🚀")
E_PERCENT = ce("5407025283456835900","💸")
E_HAND    = ce("5469654973308476699","🤜")
E_CARD2   = ce("5471952986678738719","💳")
E_PHONE   = ce("5393556898287866251","📱")

E_SELLER_ICON = ce("5377620962390857342","🪙")
E_BUYER_ICON  = ce("5294167145079395967","🛍")
E_DEALS_ICON  = ce("5188344996356448758","🏆")
E_TURN_ICON   = ce("5424976816530014958","💰")
E_REV_ICON    = ce("5028746137645876535","📊")

# ─── Типы сделок — без premium_stickers ───────────────────────────────────────
TNAMES_RU = {
    "nft":     f"{E_NFT} NFT подарок",
    "username":f"{E_USER} NFT Username",
    "stars":   f"{E_STAR2} Звёзды Telegram",
    "crypto":  f"{E_TON} Крипта (TON/USDT)",
    "premium": f"{E_PREM} Telegram Premium",
}
TNAMES_EN = {
    "nft":     f"{E_NFT} NFT Gift",
    "username":f"{E_USER} NFT Username",
    "stars":   f"{E_STAR2} Telegram Stars",
    "crypto":  f"{E_TON} Crypto (TON/USDT)",
    "premium": f"{E_PREM} Telegram Premium",
}

def tname(t, lang="ru"): return TNAMES_EN.get(t, t) if lang=="en" else TNAMES_RU.get(t, t)

# ─── Валюты ───────────────────────────────────────────────────────────────────
# FIX: Гривня → Гривнi (украинское написание)
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
    "TON":"💎 TON","USDT":"💵 USDT","Stars":"⭐️ Stars / Звёзды",
    "RUB":"🇷🇺 Рубли","KZT":"🇰🇿 Теңге","AZN":"🇦🇿 Manat","KGS":"🇰🇬 Сом",
    "UZS":"🇺🇿 So'm","TJS":"🇹🇯 Сомонӣ","BYN":"🇧🇾 Рубли (BYN)","UAH":"🇺🇦 Гривнi","GEL":"🇬🇪 ლარი",
}
CURMAP = {
    "cur_ton":"TON","cur_usdt":"USDT","cur_rub":"RUB","cur_stars":"Stars",
    "cur_kzt":"KZT","cur_azn":"AZN","cur_kgs":"KGS","cur_uzs":"UZS",
    "cur_tjs":"TJS","cur_byn":"BYN","cur_uah":"UAH","cur_gel":"GEL"
}

def cur_plain(code, lang="ru"):
    if lang=="en": return CUR_PLAIN_EN.get(code, code)
    return CUR_PLAIN_RU.get(code, code)

def card_bank(lang="ru"): return CARD_BANK_EN if lang=="en" else CARD_BANK_RU

def R(ru, a, b): return a if ru else b

BANNER_SECTIONS = {
    "main":"🏠 Главное меню","deal":"🎁 Создать сделку","balance":"💸 Пополнить/Вывод",
    "profile":"👤 Профиль","top":"🏆 Топ","my_deals":"🗂 Мои сделки",
    "deal_card":"💼 Карточка сделки","ref":"👥 Рефералы",
}

# ─── DB ───────────────────────────────────────────────────────────────────────
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE,"r",encoding="utf-8") as f: return json.load(f)
    return {"users":{},"deals":{},"banner":None,"banner_photo":None,"banner_video":None,
            "banner_gif":None,"menu_description":None,"deal_counter":1,"banners":{},
            "logs":[],"log_chat_id":None,"log_hidden":False}

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
    db["logs"].append({"time":datetime.now().strftime("%d.%m.%Y %H:%M"),"event":event,
        "deal_id":deal_id or "","uid":str(uid) if uid else "","username":username or "","extra":extra})
    if len(db["logs"])>500: db["logs"]=db["logs"][-500:]

def mask_str(t):
    if not t: return "—"
    if t.startswith("@"):
        s=t[1:]; return "@***" if len(s)<=3 else f"@{s[:2]}***{s[-2:]}"
    if t.isdigit(): return t[:3]+"***"+t[-2:]
    return t[:2]+"***"

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
        await context.bot.send_message(chat_id=int(chat_id),
            text=f"<b>{entry['time']}</b> {entry['event']}{deal}\n{ud} {uid_d}{ex}",parse_mode="HTML")
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
                except: pass
            try: await msg.delete()
            except: pass
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

# FIX: убрана категория premium_stickers
def types_kb(lang):
    ru=lang=="ru"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 NFT",callback_data="dt_nft"),
         InlineKeyboardButton("🎴 NFT Username",callback_data="dt_usr")],
        [InlineKeyboardButton("⭐️ "+R(ru,"Звёзды","Stars"),callback_data="dt_str"),
         InlineKeyboardButton("💎 "+R(ru,"Крипта","Crypto"),callback_data="dt_cry")],
        [InlineKeyboardButton("✈️ Telegram Premium",callback_data="dt_prm")],
        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")],
    ])

def cur_kb(lang):
    def n(c): return CUR_BTN.get(c,c)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(n("TON"),callback_data="cur_ton"),InlineKeyboardButton(n("USDT"),callback_data="cur_usdt")],
        [InlineKeyboardButton(n("RUB"),callback_data="cur_rub"),InlineKeyboardButton(n("Stars"),callback_data="cur_stars")],
        [InlineKeyboardButton(n("KZT"),callback_data="cur_kzt"),InlineKeyboardButton(n("AZN"),callback_data="cur_azn")],
        [InlineKeyboardButton(n("KGS"),callback_data="cur_kgs"),InlineKeyboardButton(n("UZS"),callback_data="cur_uzs")],
        [InlineKeyboardButton(n("TJS"),callback_data="cur_tjs"),InlineKeyboardButton(n("BYN"),callback_data="cur_byn")],
        [InlineKeyboardButton(n("UAH"),callback_data="cur_uah"),InlineKeyboardButton(n("GEL"),callback_data="cur_gel")],
    ])

# ─── Validation ───────────────────────────────────────────────────────────────
def validate_username(text):
    if not text.startswith("@"): return None,"no_at"
    u=text[1:]
    if len(u)<4: return None,"short"
    if not all(c.isascii() and (c.isalpha() or c.isdigit() or c=="_") for c in u):
        return None,"chars"
    if not any(c.isalpha() for c in u): return None,"chars"
    return text, None

def validate_card(text):
    c=text.replace(" ","").replace("-","").replace("+","")
    if c.isdigit() and 10<=len(c)<=12: return text
    if c.isdigit() and len(c) in (14,16): return c
    return None

def validate_ton_address(text):
    t=text.strip()
    return (t.startswith("UQ") or t.startswith("EQ")) and len(t)>=40

def validate_nft_link(text, dtype):
    clean=text.strip()
    for prefix in ("https://","http://"):
        if clean.startswith(prefix): clean=clean[len(prefix):]; break
    if not clean.startswith("t.me/"): return False,"no_tme"
    path=clean[5:]
    if dtype=="nft":
        if not path.startswith("nft/"): return False,"wrong_nft"
        if len(path[4:])<2: return False,"wrong_nft"
    return True,None

# ─── Welcome ──────────────────────────────────────────────────────────────────
def get_welcome(lang):
    ru=lang=="ru"
    if ru:
        pts=["Автоматические сделки с НФТ и подарками","Полная защита обеих сторон",
             "Средства заморожены до подтверждения","Передача через менеджера: @GiftDealsManager"]
        intro="Gift Deals — самая безопасная площадка для сделок в Telegram"
        footer="Выберите действие ниже"; stats="6500+ сделок · оборот $48,200"
    else:
        pts=["Automatic NFT & gift deals","Full protection for both parties",
             "Funds frozen until confirmation","Transfer via manager: @GiftDealsManager"]
        intro="Gift Deals — the safest platform for deals in Telegram"
        footer="Choose an action below"; stats="6500+ deals · $48,200 turnover"
    nums=[E_NUM1,E_NUM2,E_NUM3,E_NUM4]
    icons=[E_GIFT,E_SHIELD2,E_LOCK,E_JOIN]
    lines="\n".join(f"<blockquote><b>{nums[i]} {icons[i]} {pts[i]}.</b></blockquote>" for i in range(4))
    return (f"{E_CROWN} <b>{intro}</b>\n\n{lines}\n\n"
            f"<blockquote><b>{E_FIRE} {stats}</b></blockquote>\n\n"
            f"{E_ROCKET} <b>{footer}</b>")

# ─── Deal card builder ────────────────────────────────────────────────────────
def build_deal_text(deal_id, d, creator_tag, partner_tag, lang, joined=False):
    """joined=True — второй участник присоединился, показываем реквизиты для оплаты."""
    try:
        ru=lang=="ru"
        dtype=d.get("type",""); cur=d.get("currency","—"); amt=d.get("amount","—")
        dd=d.get("data",{})
        creator_role=d.get("creator_role","seller")

        item=""
        if dtype=="nft":       item=f"\n{E_LINK} {R(ru,'Ссылка','Link')}: {dd.get('nft_link','—')}"
        elif dtype=="username": item=f"\n{E_LINK} Username: {dd.get('trade_username','—')}"
        elif dtype=="stars":    item=f"\n{E_STAR2} {R(ru,'Звёзд','Stars')}: {dd.get('stars_count','—')}"
        elif dtype=="premium":  item=f"\n{E_PREM} {R(ru,'Срок','Period')}: {dd.get('premium_period','—')}"

        if creator_role=="buyer":
            lbl_creator=R(ru,"Покупатель","Buyer")
            lbl_partner=R(ru,"Продавец","Seller")
            note=R(ru,
                f"Продавец должен передать товар менеджеру {MANAGER_TAG}",
                f"Seller must transfer the item to manager {MANAGER_TAG}")
        else:
            lbl_creator=R(ru,"Продавец","Seller")
            lbl_partner=R(ru,"Покупатель","Buyer")
            note=R(ru,
                f"Покупатель должен перевести оплату менеджеру {MANAGER_TAG}",
                f"Buyer must send payment to manager {MANAGER_TAG}")

        db=load_db()
        def stats_block(uid_s):
            try:
                u=db["users"].get(str(uid_s),{}) if uid_s else {}
                nd=u.get("success_deals",0); nt=u.get("turnover",0); nv=len(u.get("reviews",[]))
                st=u.get("status","")
                sl=f"\n{ce('5438496463044752972','⭐️')} <b>{st}</b>" if st else ""
                return (f"{E_DEALS_ICON} {R(ru,'Сделок','Deals')}: <b>{nd}</b>\n"
                        f"{E_REV_ICON} {R(ru,'Отзывов','Reviews')}: <b>{nv}</b>\n"
                        f"{E_TURN_ICON} {R(ru,'Оборот','Turnover')}: <b>{nt} ₽</b>{sl}")
            except: return "—"

        creator_uid=d.get("user_id","")
        p_uname=d.get("partner","").lstrip("@").lower()
        partner_uid=next((k for k,v in db.get("users",{}).items() if v.get("username","").lower()==p_uname),None)
        cur_d=cur_plain(cur, lang)
        bank=card_bank(lang)

        lines=[
            f"{E_OK} <b>{R(ru,'Сделка','Deal')}</b>\n",
            f"{E_GIFT} <b>{R(ru,'Тип','Type')}:</b> {tname(dtype,lang)}{item}",
            f"{E_MONEY} <b>{R(ru,'Сумма','Amount')}:</b> {amt} {cur_d}\n",
            f"{E_SELLER_ICON} <b>{lbl_creator}:</b> {creator_tag}",
            f"<blockquote>{stats_block(creator_uid)}</blockquote>\n",
            f"{E_BUYER_ICON} <b>{lbl_partner}:</b> {partner_tag}",
            f"<blockquote>{stats_block(partner_uid)}</blockquote>\n",
            f"{E_SHIELD2} <b>{R(ru,'Гарантия безопасности','Security Guarantee')}</b>",
            f"<blockquote>{E_LOCK} {R(ru,'Средства заморожены до подтверждения. Сделка защищена Gift Deals.','Funds frozen until confirmation. Deal protected by Gift Deals.')}</blockquote>\n",
            f"{E_WARN} <b>{R(ru,'Важно','Important')}:</b>",
            f"<blockquote>{note}</blockquote>",
        ]

        # Реквизиты — только после того как покупатель присоединился
        if joined:
            lines += [
                f"\n{E_CARD2} <b>{'СБП / Карта' if ru else 'Card / Phone'} {bank}:</b>",
                f"<blockquote>{E_PHONE} {R(ru,'Номер','Number')}: <code>{CARD_NUM}</code>\n{R(ru,'Получатель','Recipient')}: {CARD_NAME}</blockquote>\n",
                f"{E_TON} <b>TON:</b>",
                f"<blockquote><code>{CRYPTO_ADDR}</code></blockquote>\n",
                f"{E_DIAMOND} <b>USDT:</b>",
                f"<blockquote>{E_CBOT} {CRYPTO_BOT}</blockquote>\n",
                f"{E_STAR2} <b>{R(ru,'Звёзды / NFT','Stars / NFT')}:</b>",
                f"<blockquote>{MANAGER_TAG}</blockquote>\n",
                f"{E_OK} {R(ru,'После перевода нажмите «Я оплатил»','After payment press «I paid»')}",
            ]
        else:
            lines.append(f"\n{E_SPARK} <b>{R(ru,'Ожидание второго участника...','Waiting for second participant...')}</b>")

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
                add_log(db,"👥 Новый реферал",uid=uid,username=u["username"])
                tag=f"@{u['username']}" if u.get("username") else f"#{uid}"
                try:
                    rr=ref_user.get("lang","ru")=="ru"
                    await context.bot.send_message(chat_id=int(ref_uid),
                        text=f"{E_JOIN} <b>{R(rr,'Новый реферал!','New referral!')}</b>\n<blockquote>{tag}</blockquote>",parse_mode="HTML")
                except: pass
        save_db(db); context.user_data.clear()

        if args and args[0].startswith("deal_"):
            deal_id=args[0][5:].upper(); d=db.get("deals",{}).get(deal_id)
            if d:
                seller_uid=d.get("user_id"); lang=u.get("lang","ru"); ru=lang=="ru"
                if seller_uid and seller_uid==str(uid):
                    await update.effective_message.reply_text(f"{E_WARN} "+R(ru,"Нельзя быть покупателем своей сделки.","Can't be buyer of your own deal."))
                    await show_main(update,context); return

                buyer_reqs=u.get("requisites",{})
                if not any(buyer_reqs.get(f) for f in ("card","ton","stars")):
                    kb=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💳 "+R(ru,"Карта / Телефон","Card / Phone"),callback_data=f"req_deal_card_{deal_id}")],
                        [InlineKeyboardButton("💎 TON",callback_data=f"req_deal_ton_{deal_id}")],
                        [InlineKeyboardButton("⭐️ "+R(ru,"Звёзды","Stars"),callback_data=f"req_deal_stars_{deal_id}")],
                    ])
                    await update.effective_message.reply_text(
                        f"{E_WARN} <b>{R(ru,'Добавьте реквизиты для получения оплаты:','Add requisites to receive payment:')}</b>",
                        parse_mode="HTML",reply_markup=kb)
                    context.user_data["pending_deal"]=deal_id; return

                buyer_tag=f"@{update.effective_user.username}" if update.effective_user.username else f"#{uid}"
                add_log(db,"🔗 Покупатель открыл сделку",deal_id=deal_id,uid=uid,username=u["username"])
                db["deals"][deal_id]["buyer_uid"]=str(uid); save_db(db)
                if db.get("logs"): await send_log_msg(context,db,db["logs"][-1])

                if seller_uid:
                    try:
                        sl=get_lang(int(seller_uid)); rs=sl=="ru"
                        await context.bot.send_message(chat_id=int(seller_uid),
                            text=f"{E_JOIN} <b>{R(rs,'Покупатель присоединился!','Buyer joined!')}</b>\n<blockquote>{buyer_tag}</blockquote>",parse_mode="HTML")
                    except: pass

                cu=db["users"].get(str(seller_uid),{}).get("username","") if seller_uid else ""
                creator_tag=f"@{cu}" if cu else f"#{seller_uid}"
                buyer_uname=update.effective_user.username or ""
                buyer_tag2=f"@{buyer_uname}" if buyer_uname else f"#{uid}"
                text=build_deal_text(deal_id,d,creator_tag,buyer_tag2,lang,joined=True)

                seller_uname_for_btn=db["users"].get(str(seller_uid),{}).get("username","") if seller_uid else ""
                pu=f"https://t.me/{seller_uname_for_btn}" if seller_uname_for_btn else MANAGER_URL
                kb=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ "+R(ru,"Я оплатил","I paid"),callback_data=f"paid_{deal_id}")],
                    [InlineKeyboardButton("💬 "+R(ru,"Написать продавцу","Write to seller"),url=pu)],
                    [InlineKeyboardButton("🆘 "+R(ru,"Тех. поддержка","Tech Support"),url="https://t.me/GiftDealsSupport")],
                    [InlineKeyboardButton("🏠 "+R(ru,"Главное меню","Main menu"),callback_data="main_menu")],
                ])
                await send_new(update,text,kb,section="deal_card"); return
        await show_main(update,context)
    except Exception as e: logger.error(f"cmd_start: {e}")

# ─── /neptunteam — пользовательские команды ───────────────────────────────────
async def cmd_neptune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ru=get_lang(update.effective_user.id)=="ru"
        await update.message.reply_text(
            f"{E_LOCK} <b>{R(ru,'Секретные команды:','Secret commands:')}</b>\n\n"
            "/set_my_deals [число] — установить кол-во сделок\n"
            "/set_my_amount [сумма] — установить оборот\n"
            "/add_review [текст] — добавить отзыв себе\n"
            "/del_review [номер] — удалить свой отзыв (номер из списка)\n"
            "/my_reviews — список своих отзывов\n\n"
            "<i>Только для admin:</i>\n"
            "/add_balance [uid] [сумма]\n"
            "/take_balance [uid] [сумма]\n"
            "/buy [deal_id]",
            parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_neptune: {e}")

# FIX: /add_review — добавить отзыв себе
async def cmd_add_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"
        args=context.args
        if not args:
            await update.message.reply_text(f"{E_WARN} <b>{R(ru,'Укажите текст: /add_review Текст','Usage: /add_review Text')}</b>",parse_mode="HTML"); return
        text=" ".join(args)
        u.setdefault("reviews",[]).append(text); save_db(db)
        await update.message.reply_text(f"{E_OK} <b>{R(ru,'Отзыв добавлен!','Review added!')}</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_add_review: {e}")

# FIX: /del_review — удалить свой отзыв по номеру
async def cmd_del_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"
        args=context.args
        reviews=u.get("reviews",[])
        if not args or not args[0].isdigit():
            await update.message.reply_text(f"{E_WARN} <b>{R(ru,'Укажите номер: /del_review 1','Usage: /del_review 1')}</b>",parse_mode="HTML"); return
        idx=int(args[0])-1
        if idx<0 or idx>=len(reviews):
            await update.message.reply_text(f"{E_WARN} <b>{R(ru,f'Нет отзыва №{idx+1}.',f'No review #{idx+1}.')}</b>",parse_mode="HTML"); return
        removed=reviews.pop(idx); save_db(db)
        await update.message.reply_text(f"{E_OK} <b>{R(ru,'Отзыв удалён!','Review deleted!')}</b>\n<blockquote>{removed}</blockquote>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_del_review: {e}")

# FIX: /my_reviews — список своих отзывов
async def cmd_my_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; db=load_db(); u=get_user(db,uid)
        ru=u.get("lang","ru")=="ru"
        reviews=u.get("reviews",[])
        if not reviews:
            await update.message.reply_text(f"{E_STATS} <b>{R(ru,'Отзывов нет.','No reviews.')}</b>",parse_mode="HTML"); return
        lines=[f"{E_STATS} <b>{R(ru,'Мои отзывы:','My reviews:')}</b>\n"]
        for i,r in enumerate(reviews,1):
            lines.append(f"<b>{i}.</b> {r}")
        await update.message.reply_text("\n".join(lines),parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_my_reviews: {e}")

# ─── Callbacks ────────────────────────────────────────────────────────────────
async def on_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q=update.callback_query; await q.answer(); d=q.data
        ud=context.user_data; uid=update.effective_user.id
        lang=get_lang(uid); ru=lang=="ru"

        if d=="main_menu":
            ud.clear(); await show_main(update,context); return
        if d=="menu_profile": await show_profile(update,context); return
        if d=="menu_balance":
            try: await q.message.delete()
            except: pass
            await show_balance(update,context); return
        if d=="menu_my_deals": await show_my_deals(update,context); return
        if d=="menu_lang": await show_lang(update,context); return
        if d=="menu_top": await show_top(update,context); return
        if d=="menu_ref": await show_ref(update,context); return
        if d=="menu_req": await show_req(update,context); return

        if d=="menu_deal":
            ud.clear()
            try: await q.message.delete()
            except: pass
            await update.effective_chat.send_message(
                f"{E_PENCIL} <b>{R(ru,'Создать сделку','Create Deal')}\n\n{R(ru,'Кто вы в этой сделке?','What is your role?')}</b>",
                parse_mode="HTML",reply_markup=role_kb(lang)); return

        if d in ("role_buyer","role_seller"):
            ud["creator_role"]="buyer" if d=="role_buyer" else "seller"
            try: await q.message.delete()
            except: pass
            await update.effective_chat.send_message(
                f"{E_PENCIL} <b>{R(ru,'Выберите тип сделки:','Choose deal type:')}</b>",
                parse_mode="HTML",reply_markup=types_kb(lang)); return

        TYPE_MAP={"dt_nft":"nft","dt_usr":"username","dt_str":"stars","dt_cry":"crypto","dt_prm":"premium"}
        if d in TYPE_MAP:
            ud["type"]=TYPE_MAP[d]; ud["step"]="partner"
            cr=ud.get("creator_role","seller")
            pp=R(ru,"Введите @username продавца:","Enter seller @username:") if cr=="buyer" else R(ru,"Введите @username покупателя:","Enter buyer @username:")
            try: await q.message.delete()
            except: pass
            msg=await update.effective_chat.send_message(
                f"{pp}\n\n<b>{R(ru,'Пример','Example')}:</b> <code>@username</code>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_deal")]]))
            ud["last_msg"]=msg.message_id; return

        if d=="cry_ton":
            ud["currency"]="TON"; ud["step"]="amount"
            try: await q.message.delete()
            except: pass
            msg=await update.effective_chat.send_message(f"{E_TON} {R(ru,'Введите сумму','Enter amount')} (TON):",parse_mode="HTML")
            ud["last_msg"]=msg.message_id; return

        if d=="cry_usd":
            ud["currency"]="USDT"; ud["step"]="amount"
            try: await q.message.delete()
            except: pass
            msg=await update.effective_chat.send_message(f"{E_DIAMOND} {R(ru,'Введите сумму','Enter amount')} (USDT):",parse_mode="HTML")
            ud["last_msg"]=msg.message_id; return

        if d in ("prm_3","prm_6","prm_12"):
            prru={"prm_3":"3 месяца","prm_6":"6 месяцев","prm_12":"12 месяцев"}
            pren={"prm_3":"3 months","prm_6":"6 months","prm_12":"12 months"}
            ud["premium_period"]=(prru if ru else pren)[d]; ud["step"]="currency"
            try: await q.message.delete()
            except: pass
            msg=await update.effective_chat.send_message(R(ru,"Выберите валюту:","Choose currency:"),reply_markup=cur_kb(lang),parse_mode="HTML")
            ud["last_msg"]=msg.message_id; return

        if d.startswith("cur_"):
            ud["currency"]=CURMAP.get(d,d); ud["step"]="amount"
            try: await q.message.delete()
            except: pass
            msg=await update.effective_chat.send_message(
                f"{R(ru,'Введите сумму сделки','Enter deal amount')} ({CURMAP.get(d,d)}):",parse_mode="HTML")
            ud["last_msg"]=msg.message_id; return

        # ── Реквизиты ──
        if d=="req_del_menu":
            db=load_db(); u=get_user(db,uid); reqs=u.get("requisites",{})
            rows=[]
            if reqs.get("card"): rows.append([InlineKeyboardButton("💳 "+R(ru,"Удалить карту/телефон","Delete card/phone"),callback_data="req_del_card")])
            if reqs.get("ton"):  rows.append([InlineKeyboardButton("💎 "+R(ru,"Удалить TON","Delete TON"),callback_data="req_del_ton")])
            if reqs.get("stars"):rows.append([InlineKeyboardButton("⭐️ "+R(ru,"Удалить @username","Delete @username"),callback_data="req_del_stars")])
            rows.append([InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_req")])
            await send_section(update,f"{E_DEAL} <b>{R(ru,'Что удалить?','What to delete?')}</b>",InlineKeyboardMarkup(rows),section="profile"); return

        if d.startswith("req_del_"):
            field=d[8:]; db=load_db(); u=get_user(db,uid)
            u.setdefault("requisites",{}).pop(field,None); save_db(db)
            await show_req(update,context); return

        if d.startswith("req_edit_"):
            field=d[9:]; bank=card_bank(lang)
            prompts={
                # FIX: убрана подсказка про латинские буквы, оставлен только пример
                "card": f"{E_REQ} <b>{R(ru,f'Карта / Номер телефона {bank}',f'Card / Phone Number {bank}')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>+79041751408</code></blockquote>",
                "ton":  f"{E_TON} <b>TON</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>UQDxxx...xxx</code></blockquote>",
                "stars":f"{E_STAR2} <b>{R(ru,'Звёзды','Stars')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>@username</code></blockquote>",
            }
            ud["req_step"]=field
            await send_section(update,prompts.get(field,"?"),
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_req")]]),section="profile"); return

        if d.startswith("add_req_"):
            deal_id=d[8:]; ud["req_for_deal"]=deal_id
            bank=card_bank(lang)
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 "+R(ru,f"Карта / Телефон {bank}",f"Card / Phone {bank}"),callback_data=f"req_deal_card_{deal_id}")],
                [InlineKeyboardButton("💎 TON",callback_data=f"req_deal_ton_{deal_id}")],
                [InlineKeyboardButton("⭐️ "+R(ru,"Звёзды","Stars"),callback_data=f"req_deal_stars_{deal_id}")],
                [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")],
            ])
            await send_section(update,f"{E_WARN} <b>{R(ru,'Добавьте реквизиты:','Add requisites:')}</b>",kb,section="deal_card"); return

        if d.startswith("req_deal_"):
            parts=d[9:].split("_",1); field=parts[0]; deal_id=parts[1] if len(parts)>1 else ""
            ud["req_step"]=field; ud["req_for_deal"]=deal_id
            bank=card_bank(lang)
            prompts={
                "card": f"{E_REQ} <b>{R(ru,f'Карта / Телефон {bank}',f'Card / Phone {bank}')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>+79041751408</code></blockquote>",
                "ton":  f"{E_TON} <b>TON</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>UQDxxx...xxx</code></blockquote>",
                "stars":f"{E_STAR2} <b>{R(ru,'Звёзды','Stars')}</b>\n\n<blockquote>{R(ru,'Пример:','Example:')}\n<code>@username</code></blockquote>",
            }
            await send_section(update,prompts.get(field,"?"),
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data=f"add_req_{deal_id}")]]),section="deal_card"); return

        if d.startswith("lang_"): await set_lang(update,context,d[5:]); return

        # ── Баланс ──
        if d=="menu_balance" or d=="show_balance":
            try: await q.message.delete()
            except: pass
            await show_balance(update,context); return

        if d=="balance_topup":
            # FIX: сначала показываем кнопки способа пополнения, реквизиты — после выбора
            await send_section(update,
                f"{E_MONEY} <b>{R(ru,'Выберите способ пополнения:','Choose top-up method:')}</b>",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("⭐️ "+R(ru,"Звёзды","Stars"),callback_data="balance_stars")],
                    [InlineKeyboardButton("💳 "+R(ru,"Карта / Телефон","Card / Phone"),callback_data="balance_rub")],
                    [InlineKeyboardButton("💎 TON",callback_data="balance_ton_only")],
                    [InlineKeyboardButton("💵 USDT",callback_data="balance_usdt_only")],
                    [InlineKeyboardButton("🤖 Crypto Bot",callback_data="balance_crypto")],
                    [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_balance")],
                ]),section="balance"); return

        if d.startswith("balance_ton_only"):
            bank=card_bank(lang)
            within=R(ru,"Баланс пополнится в течение 5 минут.","Balance topped up within 5 minutes.")
            text=(f"{E_TON} <b>TON</b>\n\n"
                  f"<blockquote>{R(ru,'Адрес','Address')}:\n<code>{CRYPTO_ADDR}</code>\n\n{within}</blockquote>")
            await send_section(update,text,InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ "+R(ru,"Я отправил","I sent"),callback_data="topup_sent_crypto")],
                [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="balance_topup")],
            ]),section="balance"); return

        if d.startswith("balance_usdt_only"):
            within=R(ru,"Баланс пополнится в течение 5 минут.","Balance topped up within 5 minutes.")
            text=(f"{E_DIAMOND} <b>USDT</b>\n\n"
                  f"<blockquote>{E_CBOT} {CRYPTO_BOT}\n\nID: <code>{uid}</code>\n\n{within}</blockquote>")
            await send_section(update,text,InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ "+R(ru,"Я отправил","I sent"),callback_data="topup_sent_crypto")],
                [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="balance_topup")],
            ]),section="balance"); return

        if d.startswith("balance_"):
            await show_balance_info(update,context,d[8:]); return

        if d=="withdraw":
            # FIX: проверяем реквизиты перед выводом
            db=load_db(); u=get_user(db,uid); reqs=u.get("requisites",{})
            if not any(reqs.get(f) for f in ("card","ton","stars")):
                await send_section(update,
                    f"{E_WARN} <b>{R(ru,'Для вывода добавьте реквизиты.','Add requisites to withdraw.')}</b>",
                    InlineKeyboardMarkup([
                        [InlineKeyboardButton("💳 "+R(ru,"Добавить карту/телефон","Add card/phone"),callback_data="req_edit_card")],
                        [InlineKeyboardButton("💎 "+R(ru,"Добавить TON","Add TON"),callback_data="req_edit_ton")],
                        [InlineKeyboardButton("⭐️ "+R(ru,"Добавить @username","Add @username"),callback_data="req_edit_stars")],
                        [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_balance")],
                    ]),section="balance"); return
            await show_withdraw(update,context); return

        if d.startswith("topup_sent_"):
            method=d[11:]; uname2=update.effective_user.username or str(uid)
            mmap={"stars":R(ru,"Звёзды","Stars"),"rub":R(ru,"Рубли","Rubles"),"crypto":"TON/USDT","ton_only":"TON","usdt_only":"USDT"}
            try:
                await context.bot.send_message(chat_id=ADMIN_ID,
                    text=f"{E_BELL} <b>Пополнение — {mmap.get(method,method)}</b>\n{E_USER} @{uname2} (<code>{uid}</code>)",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("✅ Пришло",callback_data=f"adm_topup_ok_{uid}"),
                        InlineKeyboardButton("❌ Не пришло",callback_data=f"adm_topup_no_{uid}"),
                    ]]))
            except: pass
            try: await q.edit_message_reply_markup(InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ "+R(ru,"Ожидание...","Waiting..."),callback_data="noop")],
                [InlineKeyboardButton("🏠 "+R(ru,"Главное меню","Main menu"),callback_data="main_menu")],
            ]))
            except: pass
            return

        if d.startswith("adm_topup_ok_"):
            if update.effective_user.id!=ADMIN_ID: return
            target=d[13:]
            await q.edit_message_text(f"{E_OK} <b>Пополнение подтверждено!</b>\n<code>{target}</code>",parse_mode="HTML")
            try:
                tl=get_lang(int(target)); tr=tl=="ru"
                await context.bot.send_message(chat_id=int(target),
                    text=f"{E_CHECK} <b>{R(tr,'Баланс пополнен!','Balance topped up!')}</b>",parse_mode="HTML")
            except: pass
            return

        if d.startswith("adm_topup_no_"):
            if update.effective_user.id!=ADMIN_ID: return
            target=d[13:]
            await q.edit_message_text(f"{E_WARN} <b>Не подтверждено.</b>\n<code>{target}</code>",parse_mode="HTML")
            return

        if d.startswith("withdraw_"):
            method=d[9:]
            prompts={"stars":R(ru,"@username для звёзд:","@username for stars:"),
                     "crypto":R(ru,"TON/USDT адрес:","TON/USDT address:"),
                     "card":R(ru,"Номер карты или телефона:","Card or phone number:")}
            ud["withdraw_method"]=method; ud["withdraw_step"]="req"
            await send_section(update,f"{E_WALLET} <b>{R(ru,'Вывод','Withdraw')}</b>\n\n<blockquote>{prompts.get(method,'?')}</blockquote>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="withdraw")]]),section="balance"); return

        if d.startswith("rev_"):
            parts=d.split("_"); deal_id=parts[1]; role=parts[2]; stars_n=int(parts[3])
            ud["review_deal"]=deal_id; ud["review_role"]=role; ud["review_stars"]=stars_n; ud["review_step"]="text"
            await q.edit_message_text(f"{E_STAR2} {R(ru,'Оценка','Rating')}: {stars_n}/5\n\n{R(ru,'Напишите комментарий:','Write a comment:')}",parse_mode="HTML"); return

        if d.startswith("adm_del_rev_"):
            parts=d[12:].split("_",1); target_uid=parts[0]; ridx=int(parts[1]) if len(parts)>1 else -1
            db=load_db()
            if target_uid in db["users"] and 0<=ridx<len(db["users"][target_uid].get("reviews",[])):
                db["users"][target_uid]["reviews"].pop(ridx); save_db(db); await q.answer("Удалено ✅")
                revs=db["users"][target_uid].get("reviews",[]); u2=db["users"][target_uid]; uname2=u2.get("username","?")
                if not revs:
                    await q.edit_message_text(f"<b>@{uname2}: отзывов нет</b>",parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return
                lines=[f"{E_STATS} <b>Отзывы @{uname2} ({len(revs)}):</b>"]; rows2=[]
                for i,r in enumerate(revs):
                    lines.append(f"\n{i+1}. {r}")
                    rows2.append([InlineKeyboardButton(f"🗑 #{i+1}",callback_data=f"adm_del_rev_{target_uid}_{i}")])
                rows2.append([InlineKeyboardButton("🔙 Назад",callback_data="adm_back")])
                await q.edit_message_text("\n".join(lines),parse_mode="HTML",reply_markup=InlineKeyboardMarkup(rows2)); return
            return

        if d.startswith("paid_"): await on_paid(update,context); return
        if d=="noop": return
        if d.startswith("adm_confirm_"): await adm_confirm(update,context); return
        if d.startswith("adm_decline_"): await adm_decline(update,context); return
        if d=="adm_back":
            try: await q.message.edit_text(f"{E_DEAL} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())
            except: await q.message.reply_text(f"{E_DEAL} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())
            return
        if d.startswith("adm_"): await handle_adm_cb(update,context); return

    except Exception as e: logger.error(f"on_cb: {e}")

# ─── Messages ─────────────────────────────────────────────────────────────────
async def on_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ud=context.user_data; uid=update.effective_user.id; lang=get_lang(uid); ru=lang=="ru"
        text=update.message.text.strip() if update.message.text else ""
        if uid==ADMIN_ID and ud.get("adm_step"): await handle_adm_msg(update,context); return

        # ── Реквизиты ──
        if ud.get("req_step") in ("card","ton","stars"):
            field=ud["req_step"]; db=load_db(); u=get_user(db,uid)
            err=None
            if field=="card":
                r=validate_card(text)
                if r is None: err=R(ru,
                    f"Введите номер телефона или карты.\n\n<b>Пример:</b>\n<code>+79041751408</code>",
                    f"Enter phone or card number.\n\n<b>Example:</b>\n<code>+79041751408</code>")
                else: text=r
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
                await update.message.reply_text(f"{E_WARN} {err}",parse_mode="HTML"); return

            # FIX: при добавлении одного реквизита — старый того же типа заменяется (не удаляются другие)
            u.setdefault("requisites",{})[field]=text
            save_db(db); ud.pop("req_step",None)

            pending=ud.pop("req_for_deal",None) or ud.pop("pending_deal",None)
            if pending:
                db2=load_db(); d2=db2.get("deals",{}).get(pending)
                if d2:
                    await update.message.reply_text(f"{E_OK} <b>{R(ru,'Реквизиты сохранены!','Requisites saved!')}</b>",parse_mode="HTML")
                    db2["deals"][pending]["buyer_uid"]=str(uid); save_db(db2)
                    cu=db2["users"].get(str(d2.get("user_id","")),{}).get("username","") if d2.get("user_id") else ""
                    ct=f"@{cu}" if cu else f"#{d2.get('user_id','')}"
                    bu=update.effective_user.username or ""; bt=f"@{bu}" if bu else f"#{uid}"
                    text2=build_deal_text(pending,d2,ct,bt,lang,joined=True)
                    seller_uid_p=d2.get("user_id","")
                    seller_uname_p=db2["users"].get(str(seller_uid_p),{}).get("username","") if seller_uid_p else ""
                    pu=f"https://t.me/{seller_uname_p}" if seller_uname_p else MANAGER_URL
                    kb=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ "+R(ru,"Я оплатил","I paid"),callback_data=f"paid_{pending}")],
                        [InlineKeyboardButton("💬 "+R(ru,"Написать продавцу","Write to seller"),url=pu)],
                        [InlineKeyboardButton("🏠 "+R(ru,"Главное меню","Main menu"),callback_data="main_menu")],
                    ])
                    await send_new(update,text2,kb,section="deal_card"); return

            await update.message.reply_text(f"{E_OK} <b>{R(ru,'Реквизиты сохранены!','Requisites saved!')}</b>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 "+R(ru,"Мои реквизиты","My Requisites"),callback_data="menu_req")]])); return

        # ── Вывод ──
        if ud.get("withdraw_step")=="req":
            method=ud.get("withdraw_method","?"); db=load_db()
            u=get_user(db,uid); bal=u.get("balance",0); uname3=update.effective_user.username or str(uid)
            mnames={"stars":R(ru,"Звёзды","Stars"),"crypto":R(ru,"Крипта","Crypto"),"card":R(ru,"Карта","Card")}
            mname=mnames.get(method,method)
            try:
                await context.bot.send_message(chat_id=ADMIN_ID,
                    text=f"{E_GEM} <b>Вывод — {mname}</b>\n{E_USER} @{uname3} (<code>{uid}</code>)\n{CM} {bal} RUB\n\nРеквизиты: <code>{text}</code>",
                    parse_mode="HTML")
            except: pass
            ud.pop("withdraw_step",None); ud.pop("withdraw_method",None)
            await update.message.reply_text(
                f"{E_CHECK} <b>{R(ru,'Запрос отправлен!','Request sent!')}</b>\n\n<blockquote>{R(ru,'Менеджер свяжется с вами.','Manager will contact you.')}</blockquote>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💬 "+R(ru,"Менеджер","Manager"),url=MANAGER_URL)],
                    [InlineKeyboardButton("🏠 "+R(ru,"Главное меню","Main menu"),callback_data="main_menu")],
                ])); return

        # ── Отзыв ──
        if ud.get("review_step")=="text":
            deal_id=ud.get("review_deal"); role=ud.get("review_role"); stars_r=ud.get("review_stars",5)
            db=load_db(); deal=db.get("deals",{}).get(deal_id,{})
            rev_text=f"{E_STAR2} {stars_r}/5 — {text}"
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
            await update.message.reply_text(f"{E_OK} <b>{R(ru,'Отзыв сохранён!' if saved else 'Принят!','Review saved!' if saved else 'Received!')}</b>",parse_mode="HTML"); return

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
            if not text.startswith("@"): text="@"+text
            cl,ec=validate_username(text)
            if ec:
                await update.message.reply_text(
                    f"{E_WARN} <b>{R(ru,'Неверный @username.','Invalid @username.')}</b>\n\n<b>{R(ru,'Пример','Example')}:</b> <code>@username</code>",
                    parse_mode="HTML"); return
            ud["partner"]=cl
            if dtype=="nft":
                ud["step"]="nft_link"
                await send_step(f"{E_NFT} <b>{R(ru,'Вставьте ссылку на NFT:','Paste NFT link:')}</b>\n\n<code>t.me/nft/...</code>")
            elif dtype=="username":
                ud["step"]="trade_usr"
                await send_step(f"{E_USER} <b>{R(ru,'Введите ссылку (t.me/...):','Enter link (t.me/...):')}</b>")
            elif dtype=="stars":
                ud["step"]="stars_cnt"
                await send_step(f"{E_STAR2} <b>{R(ru,'Сколько звёзд?','How many stars?')}</b>")
            elif dtype=="crypto":
                ud["step"]="cry_currency"
                await send_step(f"{E_DIAMOND} <b>{R(ru,'Выберите валюту:','Choose currency:')}</b>",
                    InlineKeyboardMarkup([[InlineKeyboardButton("💎 TON",callback_data="cry_ton"),InlineKeyboardButton("💵 USDT",callback_data="cry_usd")]]))
            elif dtype=="premium":
                ud["step"]="prem_period"
                await send_step(f"{E_PREM} <b>Telegram Premium\n\n{R(ru,'Выберите срок:','Choose period:')}</b>",
                    InlineKeyboardMarkup([[
                        InlineKeyboardButton("3 "+R(ru,"месяца","months"),callback_data="prm_3"),
                        InlineKeyboardButton("6 "+R(ru,"месяцев","months"),callback_data="prm_6"),
                        InlineKeyboardButton("12 "+R(ru,"месяцев","months"),callback_data="prm_12")]]))
            return

        if step=="nft_link":
            ok,em=validate_nft_link(text,dtype)
            if not ok:
                await update.message.reply_text(f"{E_WARN} <b>{R(ru,'Используйте t.me/nft/...','Use t.me/nft/...')}</b>",parse_mode="HTML"); return
            clean_link=text.strip()
            for prefix in ("https://","http://"):
                if clean_link.startswith(prefix): clean_link=clean_link[len(prefix):]; break
            if not clean_link.startswith("t.me/"): clean_link="t.me/"+clean_link
            ud["nft_link"]=clean_link; ud["step"]="currency"
            await send_step(f"{E_NFT} <b>{R(ru,'Выберите валюту:','Choose currency:')}</b>",cur_kb(lang)); return

        if step=="trade_usr":
            cl=text.replace("https://","").replace("http://","")
            if not cl.startswith("t.me/") and not text.startswith("@"):
                await update.message.reply_text(f"{E_WARN} <b>{R(ru,'Введите t.me/... или @username.','Enter t.me/... or @username.')}</b>",parse_mode="HTML"); return
            ud["trade_username"]=text; ud["step"]="currency"
            await send_step(f"{E_USER} <b>{R(ru,'Выберите валюту:','Choose currency:')}</b>",cur_kb(lang)); return

        if step=="stars_cnt":
            if not text.isdigit():
                await update.message.reply_text(f"{E_WARN} <b>{R(ru,'Только цифры!','Numbers only!')}</b>",parse_mode="HTML"); return
            ud["stars_count"]=text; ud["step"]="currency"
            await send_step(f"{E_STAR2} <b>{R(ru,'Выберите валюту:','Choose currency:')}</b>",cur_kb(lang)); return

        if step=="amount":
            ca=text.replace(" ","").replace(",",".")
            try: float(ca)
            except:
                await update.message.reply_text(f"{E_WARN} <b>{R(ru,'Введите число. Пример: 500','Enter number. Example: 500')}</b>",parse_mode="HTML"); return
            ud["amount"]=ca
            await del_prev()
            await finalize_deal(update,context)
            return

    except Exception as e: logger.error(f"on_msg: {e}")

# ─── Finalize deal ────────────────────────────────────────────────────────────
async def finalize_deal(update, context):
    try:
        ud=context.user_data; db=load_db()
        dtype=ud.get("type","?"); partner=ud.get("partner","—")
        currency=ud.get("currency","—"); amount=ud.get("amount","—")
        creator_role=ud.get("creator_role","seller"); user=update.effective_user

        data={}
        for key in ("nft_link","trade_username","stars_count","premium_period"):
            if ud.get(key) is not None: data[key]=ud[key]

        deal_id=gen_deal_id(db)
        db["deals"][deal_id]={
            "user_id":str(user.id),"type":dtype,"partner":partner,
            "currency":currency,"amount":amount,"status":"pending",
            "created":datetime.now().isoformat(),"data":data,"creator_role":creator_role,
        }
        add_log(db,"🆕 Новая сделка",deal_id=deal_id,uid=user.id,username=user.username or "",
            extra=f"{dtype} | {amount} {currency} | {creator_role}")
        save_db(db)
        if db.get("logs"): await send_log_msg(context,db,db["logs"][-1])

        cu=db["users"].get(str(user.id),{}).get("username","")
        creator_tag=f"@{cu}" if cu else f"@{user.username or str(user.id)}"
        partner_tag=partner
        lang=get_lang(user.id); ru=lang=="ru"

        # Карточка без реквизитов — ждём партнёра
        text=build_deal_text(deal_id,db["deals"][deal_id],creator_tag,partner_tag,lang,joined=False)
        ll=R(ru,"Ссылка для партнёра","Link for partner")
        sl=R(ru,"Отправьте ссылку — реквизиты откроются после перехода партнёра.",
             "Share the link — payment details appear after partner joins.")
        text+=f"\n\n{E_DLNK} <b>{ll}:</b>\n<code>https://t.me/{BOT_USERNAME}?start=deal_{deal_id}</code>\n\n<i>{sl}</i>"

        kb=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 "+R(ru,"Главное меню","Main menu"),callback_data="main_menu")]])
        await send_new(update,text,kb,section="deal_card")

        # Уведомить партнёра если он есть в боте
        pname=partner.lstrip("@").lower() if partner.startswith("@") else None
        if pname:
            puid=next((k for k,v in db["users"].items() if v.get("username","").lower()==pname),None)
            if puid:
                try:
                    pl=get_lang(int(puid)); pr=pl=="ru"
                    partner_tag2=f"@{db['users'][puid].get('username','')}" if db["users"][puid].get("username") else f"#{puid}"
                    txt2=build_deal_text(deal_id,db["deals"][deal_id],creator_tag,partner_tag2,pl,joined=False)
                    join_link=f"https://t.me/{BOT_USERNAME}?start=deal_{deal_id}"
                    txt2+=f"\n\n{E_JOIN} <b>{R(pr,'Нажмите чтобы присоединиться:','Click to join:')}</b>\n<code>{join_link}</code>"
                    kb2=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🤝 "+R(pr,"Присоединиться","Join"),url=join_link)],
                        [InlineKeyboardButton("🏠 "+R(pr,"Главное меню","Main menu"),callback_data="main_menu")]
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
        amt=d.get("amount","—"); cur=d.get("currency","—")
        suid=d.get("user_id"); sl2=get_lang(int(suid)) if suid else "ru"; rs2=sl2=="ru"
        try:
            await context.bot.send_message(chat_id=ADMIN_ID,
                text=f"{E_BELL} <b>«Я оплатил»</b>\n\n{E_DEAL} <code>{deal_id}</code>\n{E_USER} {btag} (<code>{buyer.id}</code>)\n{CM} {amt} {cur}\n\nПроверьте:",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ Пришла",callback_data=f"adm_confirm_{deal_id}"),
                    InlineKeyboardButton("❌ Не пришла",callback_data=f"adm_decline_{deal_id}")
                ]]))
        except Exception as e: logger.error(f"on_paid admin: {e}")
        add_log(db,"💳 Оплачено",deal_id=deal_id,uid=buyer.id,username=buyer.username or "",extra=f"{amt} {cur}")
        save_db(db)
        if db.get("logs"): await send_log_msg(context,db,db["logs"][-1])
        seller=d.get("user_id")
        if seller and seller!=str(buyer.id):
            try:
                await context.bot.send_message(chat_id=int(seller),
                    text=f"{E_BELL} <b>{R(rs2,'Покупатель оплатил!','Buyer paid!')}</b>\n{btag}\n{amt} {cur}",parse_mode="HTML")
            except: pass
        try:
            await q.edit_message_reply_markup(InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ "+R(rb,"Ожидание...","Waiting..."),callback_data="noop")],
                [InlineKeyboardButton("🏠 "+R(rb,"Главное меню","Main menu"),callback_data="main_menu")]
            ]))
        except: pass
    except Exception as e: logger.error(f"on_paid: {e}")

# ─── adm_confirm / decline ────────────────────────────────────────────────────
async def adm_confirm(update, context):
    try:
        q=update.callback_query; await q.answer()
        if update.effective_user.id!=ADMIN_ID: return
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
        if dtype=="nft" and dd.get("nft_link"): ilink=f"\n{E_LINK} {dd['nft_link']}"
        elif dtype=="username" and dd.get("trade_username"): ilink=f"\n{E_LINK} {dd['trade_username']}"
        seller_uname=db["users"].get(s,{}).get("username","?") if s else "?"
        add_log(db,"✅ Подтверждено",deal_id=deal_id,uid=s,username=seller_uname,extra=f"{amt_str} {d.get('currency','')}")
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
                            text=f"{E_MONEY} <b>{R(rr,'Реферальный бонус!','Referral bonus!')}</b>\n<blockquote>+{bonus} RUB (3%)</blockquote>",parse_mode="HTML")
                    except: pass
        save_db(db)
        if db.get("logs"): await send_log_msg(context,db,db["logs"][-1])
        try: await q.edit_message_text(f"{E_OK} <b>Подтверждено!</b>\n<code>{deal_id}</code>\n{d.get('amount')} {d.get('currency')}{ilink}",parse_mode="HTML")
        except: pass
        if s:
            try:
                sl=get_lang(int(s)); rs=sl=="ru"; bt2=d.get("partner","—")
                await context.bot.send_message(chat_id=int(s),
                    text=f"{E_CHECK} <b>{R(rs,'Сделка завершена!','Deal completed!')}</b>{ilink}\n\n{R(rs,'Оцените покупателя','Rate the buyer')} {bt2}:",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("1⭐",callback_data=f"rev_{deal_id}_s_1"),
                        InlineKeyboardButton("2⭐",callback_data=f"rev_{deal_id}_s_2"),
                        InlineKeyboardButton("3⭐",callback_data=f"rev_{deal_id}_s_3"),
                        InlineKeyboardButton("4⭐",callback_data=f"rev_{deal_id}_s_4"),
                        InlineKeyboardButton("5⭐",callback_data=f"rev_{deal_id}_s_5"),
                    ]]))
            except: pass
        buyer_uid=d.get("buyer_uid")
        if not buyer_uid:
            for u_,ud_ in db.get("users",{}).items():
                if ud_.get("username","").lower()==d.get("partner","").lstrip("@").lower(): buyer_uid=u_; break
        if buyer_uid:
            try:
                bl2=get_lang(int(buyer_uid)); rb2=bl2=="ru"
                stag=f"@{db['users'].get(s,{}).get('username','')}" if s else MANAGER_TAG
                await context.bot.send_message(chat_id=int(buyer_uid),
                    text=f"{E_CHECK} <b>{R(rb2,'Сделка подтверждена!','Deal confirmed!')}</b>{ilink}\n\n{R(rb2,'Оцените продавца','Rate the seller')} {stag}:",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("1⭐",callback_data=f"rev_{deal_id}_b_1"),
                        InlineKeyboardButton("2⭐",callback_data=f"rev_{deal_id}_b_2"),
                        InlineKeyboardButton("3⭐",callback_data=f"rev_{deal_id}_b_3"),
                        InlineKeyboardButton("4⭐",callback_data=f"rev_{deal_id}_b_4"),
                        InlineKeyboardButton("5⭐",callback_data=f"rev_{deal_id}_b_5"),
                    ]]))
            except: pass
    except Exception as e: logger.error(f"adm_confirm: {e}")

async def adm_decline(update, context):
    try:
        q=update.callback_query; await q.answer()
        if update.effective_user.id!=ADMIN_ID: return
        deal_id=q.data[12:]; db=load_db(); d=db.get("deals",{}).get(deal_id,{})
        try:
            await q.edit_message_text(f"{E_WARN} <b>Не подтверждено.</b>\n<code>{deal_id}</code>\n{CM} {d.get('amount','—')} {d.get('currency','—')}",
                parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Всё же пришла",callback_data=f"adm_confirm_{deal_id}")]]))
        except: pass
    except Exception as e: logger.error(f"adm_decline: {e}")

# ─── Sections ─────────────────────────────────────────────────────────────────
async def show_balance(update, context):
    """FIX: сначала главный экран с кнопками, без реквизитов прямо тут."""
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=get_lang(uid); ru=lang=="ru"; bal=u.get("balance",0)
        await send_section(update,
            f"{E_WALLET} <b>{R(ru,'Пополнить / Вывод','Top Up / Withdraw')}</b>\n\n"
            f"<blockquote>{E_BAL} <b>{R(ru,'Баланс','Balance')}: {bal} RUB</b></blockquote>",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ "+R(ru,"Пополнить","Top Up"),callback_data="balance_topup")],
                [InlineKeyboardButton("➖ "+R(ru,"Вывод","Withdraw"),callback_data="withdraw")],
                [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")],
            ]),section="balance")
    except Exception as e: logger.error(f"show_balance: {e}")

async def show_balance_info(update, context, method):
    try:
        uid=update.effective_user.id; lang=get_lang(uid); ru=lang=="ru"
        bank=card_bank(lang)
        within=R(ru,"Баланс пополнится в течение 5 минут.","Balance topped up within 5 minutes.")
        i_sent=InlineKeyboardButton("✅ "+R(ru,"Я отправил","I sent"),callback_data=f"topup_sent_{method}")
        back=InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="balance_topup")
        if method=="stars":
            text=f"{E_STAR2} <b>{R(ru,'Пополнение звёздами','Top up with Stars')}</b>\n\n<blockquote>{R(ru,'Отправьте звёзды менеджеру','Send stars to manager')}: {MANAGER_TAG}\n\n{within}</blockquote>"
        elif method=="rub":
            text=(f"{E_REQ} <b>{R(ru,f'Пополнение картой / телефон {bank}',f'Top up — Card / Phone {bank}')}</b>\n\n"
                  f"<blockquote>{E_PHONE} {R(ru,'Номер','Number')}: <code>{CARD_NUM}</code>\n"
                  f"{R(ru,'Получатель','Recipient')}: {CARD_NAME}\n\n{within}</blockquote>")
        elif method=="crypto":
            text=(f"{E_CBOT} <b>Crypto Bot (TON/USDT)</b>\n\n"
                  f"<blockquote>{CRYPTO_BOT}\n\nID: <code>{uid}</code>\n\n{within}</blockquote>")
        else: text="<b>?</b>"
        await send_section(update,text,InlineKeyboardMarkup([[i_sent],[back]]),section="balance")
    except Exception as e: logger.error(f"show_balance_info: {e}")

async def show_lang(update, context):
    try:
        uid=update.effective_user.id; lang=get_lang(uid); ru=lang=="ru"
        rows=[[InlineKeyboardButton(n,callback_data=f"lang_{c}")] for c,n in {"ru":"🇷🇺 Русский","en":"🇬🇧 English"}.items()]
        rows.append([InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")])
        await send_section(update,f"{ce('5447410659077661506','🌐')} <b>"+R(ru,"Выберите язык:","Select language:")+"</b>",
            InlineKeyboardMarkup(rows),section="main")
    except Exception as e: logger.error(f"show_lang: {e}")

async def set_lang(update, context, lang):
    try:
        db=load_db(); u=get_user(db,update.effective_user.id); u["lang"]=lang; save_db(db)
        await update.callback_query.answer("✅")
        await show_main(update,context)
    except Exception as e: logger.error(f"set_lang: {e}")

async def show_profile(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=get_lang(uid); ru=lang=="ru"
        uname=update.effective_user.username or "—"
        status=u.get("status","")
        sl=f"\n<blockquote>{R(ru,'Статус','Status')}: {status}</blockquote>" if status else ""
        reviews=u.get("reviews",[])
        rv=""
        if reviews:
            rv_lines="\n".join(f"{i+1}. {r}" for i,r in enumerate(reviews[-10:]))
            rv=f"\n\n{E_STATS} <b>{R(ru,'Отзывы','Reviews')}:</b>\n<blockquote>{rv_lines}</blockquote>"
        text=(f"{E_CROWN} <b>{R(ru,'Профиль','Profile')}</b>{sl}\n\n"
              f"{E_USER} @{uname}\n"
              f"{E_BAL} {R(ru,'Баланс','Balance')}: <b>{u.get('balance',0)} RUB</b>\n"
              f"{E_STATS} {R(ru,'Сделок','Deals')}: <b>{u.get('total_deals',0)}</b>\n"
              f"{E_OK} {R(ru,'Успешных','Successful')}: <b>{u.get('success_deals',0)}</b>\n"
              f"{E_TURN_ICON} {R(ru,'Оборот','Turnover')}: <b>{u.get('turnover',0)} RUB</b>\n"
              f"{E_TROPHY} {R(ru,'Репутация','Reputation')}: <b>{u.get('reputation',0)}</b>{rv}")
        await send_section(update,text,InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]
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
        if refs: refs_str="\n\n"+R(ru,"Рефералы","Referrals")+":\n"+"\n".join(f"• @{r}" if r and r!="?" else "• #?" for r in refs[-10:])
        text=(f"{E_JOIN} <b>{R(ru,'Реферальная программа','Referral Program')}</b>\n\n"
              f"<blockquote>{E_PERCENT} {R(ru,'Приглашайте друзей — 3% с каждой их сделки!','Invite friends — 3% from each deal!')}\n\n"
              f"{E_USER} {R(ru,'Приглашено','Invited')}: <b>{rc}</b>\n"
              f"{E_BAL} {R(ru,'Заработано','Earned')}: <b>{re} RUB</b>{refs_str}</blockquote>\n\n"
              f"{E_SPARK} {R(ru,'Ваша ссылка:','Your link:')}\n<code>{ref_link}</code>")
        await send_section(update,text,InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]]),section="ref")
    except Exception as e: logger.error(f"show_ref: {e}")

async def show_req(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=get_lang(uid); ru=lang=="ru"; reqs=u.get("requisites",{})
        card=reqs.get("card"); ton=reqs.get("ton"); stars=reqs.get("stars")
        bank=card_bank(lang)

        lines=[f"{E_REQ} <b>{R(ru,'Мои реквизиты','My Requisites')}</b>\n"]
        lines.append(f"{E_CARD2} <b>{R(ru,f'Карта / Телефон {bank}',f'Card / Phone {bank}')}:</b>")
        lines.append(f"<blockquote><code>{card}</code></blockquote>" if card else f"<blockquote>{R(ru,'Не добавлена','Not added')}</blockquote>")
        lines.append(f"\n{E_TON} <b>TON:</b>")
        lines.append(f"<blockquote><code>{ton}</code></blockquote>" if ton else f"<blockquote>{R(ru,'Не добавлен','Not added')}</blockquote>")
        lines.append(f"\n{E_STAR2} <b>{R(ru,'Звёзды','Stars')}:</b>")
        lines.append(f"<blockquote><code>{stars}</code></blockquote>" if stars else f"<blockquote>{R(ru,'Не добавлен','Not added')}</blockquote>")

        rows=[]
        if card:
            rows.append([InlineKeyboardButton("💳 "+R(ru,"Изменить карту","Edit card"),callback_data="req_edit_card"),
                         InlineKeyboardButton("🗑 "+R(ru,"Удалить","Delete"),callback_data="req_del_card")])
        else:
            rows.append([InlineKeyboardButton("💳 "+R(ru,f"Добавить карту / телефон",f"Add card / phone"),callback_data="req_edit_card")])
        if ton:
            rows.append([InlineKeyboardButton("💎 "+R(ru,"Изменить TON","Edit TON"),callback_data="req_edit_ton"),
                         InlineKeyboardButton("🗑 "+R(ru,"Удалить","Delete"),callback_data="req_del_ton")])
        else:
            rows.append([InlineKeyboardButton("💎 "+R(ru,"Добавить TON","Add TON"),callback_data="req_edit_ton")])
        if stars:
            rows.append([InlineKeyboardButton("⭐️ "+R(ru,"Изменить @username","Edit @username"),callback_data="req_edit_stars"),
                         InlineKeyboardButton("🗑 "+R(ru,"Удалить","Delete"),callback_data="req_del_stars")])
        else:
            rows.append([InlineKeyboardButton("⭐️ "+R(ru,"Добавить Звёзды","Add Stars"),callback_data="req_edit_stars")])
        rows.append([InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")])
        await send_section(update,"\n".join(lines),InlineKeyboardMarkup(rows),section="profile")
    except Exception as e: logger.error(f"show_req: {e}")

async def show_my_deals(update, context):
    try:
        db=load_db(); uid=str(update.effective_user.id); lang=get_lang(int(uid)); ru=lang=="ru"
        deals={k:v for k,v in db.get("deals",{}).items() if v.get("user_id")==uid}
        if not deals:
            await send_section(update,f"{E_DEAL} <b>{R(ru,'Мои сделки','My Deals')}\n\n{R(ru,'Пока нет сделок.','No deals yet.')}</b>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]]),section="my_deals"); return
        SNAMES={
            "pending":  R(ru,f"{E_SPARK} Ожидает",  f"{E_SPARK} Pending"),
            "confirmed":R(ru,f"{E_OK} Завершена",   f"{E_OK} Completed"),
        }
        lines=[f"{E_DEAL} <b>{R(ru,'Мои сделки','My Deals')} ({len(deals)}):</b>\n"]
        for i,(did,dv) in enumerate(list(deals.items())[-10:],start=1):
            tn=tname(dv.get("type",""),lang)
            # FIX: на английском показываем английское название валюты
            cur_d=cur_plain(dv.get("currency",""),lang)
            s=SNAMES.get(dv.get("status",""),dv.get("status",""))
            lines.append(f"<b>{i}. {tn} · {dv.get('amount')} {cur_d} · {s}</b>")
        await send_section(update,"\n".join(lines),
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]]),section="my_deals")
    except Exception as e: logger.error(f"show_my_deals: {e}")

async def show_top(update, context):
    try:
        lang=get_lang(update.effective_user.id); ru=lang=="ru"
        TOP=[
            ("@al***ndr",8450,312),("@ie***ym",6380,278),("@ma***ov",5910,241),
            ("@kr***na",4290,198),("@pe***ko",3870,175),("@se***ev",3240,152),
            ("@an***va",2810,134),("@vi***or",2390,117),("@dm***iy",1970,98),("@ni***la",1540,83)
        ]
        medals=["🥇","🥈","🥉"]+["🏅"]*7
        dw=R(ru,"сделок","deals")
        lines=[f"{E_CROWN} <b>{R(ru,'Топ продавцов Gift Deals','Gift Deals Top Sellers')}</b>\n"]
        for i,(u2,a,dd) in enumerate(TOP):
            lines.append(f"<b>{medals[i]} {i+1}. {u2} — ${a} · {dd} {dw}</b>")
        lines.append(f"\n{E_FIRE} <b>{R(ru,'6500+ сделок · оборот $48,200','6500+ deals · $48,200 turnover')}</b>")
        await send_section(update,"\n".join(lines),
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="main_menu")]]),section="top")
    except Exception as e: logger.error(f"show_top: {e}")

async def show_withdraw(update, context):
    try:
        db=load_db(); uid=update.effective_user.id; u=get_user(db,uid)
        lang=get_lang(uid); ru=lang=="ru"; bal=u.get("balance",0)
        if bal<=0:
            await send_section(update,f"{E_WARN} <b>{R(ru,'Недостаточно средств.','Insufficient balance.')}</b>\n\n<blockquote>{R(ru,'Баланс','Balance')}: {bal} RUB</blockquote>",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_balance")]]),section="balance"); return
        reqs=u.get("requisites",{})
        rows=[]
        if reqs.get("ton"): rows.append([InlineKeyboardButton("💎 TON/USDT → "+reqs["ton"][:12]+"...",callback_data="withdraw_crypto")])
        else: rows.append([InlineKeyboardButton("💎 TON / USDT",callback_data="withdraw_crypto")])
        if reqs.get("stars"): rows.append([InlineKeyboardButton("⭐️ "+R(ru,"Звёзды → ","Stars → ")+reqs["stars"],callback_data="withdraw_stars")])
        else: rows.append([InlineKeyboardButton("⭐️ "+R(ru,"Звёзды","Stars"),callback_data="withdraw_stars")])
        if reqs.get("card"): rows.append([InlineKeyboardButton("💳 "+R(ru,"Карта → ","Card → ")+reqs["card"][:12]+"...",callback_data="withdraw_card")])
        else: rows.append([InlineKeyboardButton("💳 "+R(ru,"Карта / Телефон","Card / Phone"),callback_data="withdraw_card")])
        rows.append([InlineKeyboardButton("🔙 "+R(ru,"Назад","Back"),callback_data="menu_balance")])
        await send_section(update,
            f"{E_WALLET} <b>{R(ru,'Вывод средств','Withdraw')}</b>\n\n<blockquote>{E_BAL} {R(ru,'Баланс','Balance')}: {bal} RUB</blockquote>",
            InlineKeyboardMarkup(rows),section="balance")
    except Exception as e: logger.error(f"show_withdraw: {e}")

# ─── Admin ────────────────────────────────────────────────────────────────────
def adm_kb():
    db=load_db(); hidden=db.get("log_hidden",False)
    tl="👁 Логи: открыты" if not hidden else "🙈 Логи: скрыты"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Управление пользователем",callback_data="adm_user")],
        [InlineKeyboardButton("🖼 Баннеры",callback_data="adm_banners")],
        [InlineKeyboardButton("✏️ Описание меню",callback_data="adm_menu_desc")],
        [InlineKeyboardButton("🗂 Список сделок",callback_data="adm_deals")],
        [InlineKeyboardButton("📋 Логи",callback_data="adm_logs"),InlineKeyboardButton(tl,callback_data="adm_toggle_hidden")],
        [InlineKeyboardButton("📡 Лог-канал",callback_data="adm_log_channel")],
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
    await update.message.reply_text(f"{E_DEAL} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())

async def handle_adm_cb(update, context):
    try:
        q=update.callback_query; d=q.data; ud=context.user_data
        if update.effective_user.id!=ADMIN_ID: return

        if d=="adm_user":
            ud["adm_step"]="get_user"
            await q.message.edit_text("<b>Введите @юзернейм или числовой ID:</b>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return

        if d=="adm_banners":
            await q.message.edit_text(f"{E_GIFT} <b>Баннеры</b>\n\n<blockquote>✅ — есть | ➕ — нет | 🗑 — удалить</blockquote>",
                parse_mode="HTML",reply_markup=adm_banners_kb()); return

        if d.startswith("adm_banner_del_"):
            section=d[15:]
            if section in BANNER_SECTIONS:
                db=load_db()
                if not db.get("banners"): db["banners"]={}
                db["banners"][section]={}
                if section=="main": db["banner"]=db["banner_photo"]=db["banner_video"]=db["banner_gif"]=None
                save_db(db); await q.answer("Удалено")
                await q.message.edit_text(f"{E_GIFT} <b>Баннеры</b>",parse_mode="HTML",reply_markup=adm_banners_kb()); return

        if d.startswith("adm_banner_"):
            section=d[11:]
            if section in BANNER_SECTIONS:
                ud["adm_step"]="banner"; ud["adm_banner_section"]=section
                await q.message.edit_text(f"<b>Баннер «{BANNER_SECTIONS[section]}»\n\nОтправьте фото/видео/GIF/текст. off — удалить.</b>",
                    parse_mode="HTML",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Отмена",callback_data="adm_banners")]])); return

        if d=="adm_log_channel":
            db=load_db(); ci=db.get("log_chat_id","не задан"); lh=db.get("log_hidden",False)
            ms="🙈 Скрыто" if lh else "👁 Открыто"
            await q.message.edit_text(f"{E_BELL} <b>Лог-канал</b>\n\n<blockquote>Chat ID: <code>{ci}</code>\nДанные: {ms}</blockquote>\n\nОтправьте новый chat_id:",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👁 Открыть" if lh else "🙈 Скрыть",callback_data="adm_log_toggle_mask")],
                    [InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]
                ]))
            ud["adm_step"]="set_log_chat"; return

        if d=="adm_log_toggle_mask":
            db=load_db(); db["log_hidden"]=not db.get("log_hidden",False); save_db(db)
            lh=db["log_hidden"]; ci=db.get("log_chat_id","не задан"); ms="🙈 Скрыто" if lh else "👁 Открыто"
            await q.message.edit_text(f"{E_BELL} <b>Лог-канал</b>\n\n<blockquote>Chat ID: <code>{ci}</code>\nДанные: {ms}</blockquote>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👁 Открыть" if lh else "🙈 Скрыть",callback_data="adm_log_toggle_mask")],
                    [InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]
                ]))
            await q.answer("✅"); return

        if d=="adm_toggle_hidden":
            db=load_db(); db["log_hidden"]=not db.get("log_hidden",False); save_db(db)
            await q.answer("🙈 Скрыто" if db["log_hidden"] else "👁 Открыто")
            try: await q.message.edit_text(f"{E_DEAL} <b>Панель администратора</b>",parse_mode="HTML",reply_markup=adm_kb())
            except: pass; return

        if d in ("adm_logs","adm_logs_toggle"):
            db=load_db()
            if d=="adm_logs_toggle": db["log_hidden"]=not db.get("log_hidden",False); save_db(db)
            hidden=db.get("log_hidden",False); logs=db.get("logs",[])[-20:][::-1]
            if not logs:
                await q.message.edit_text("<b>Логов нет.</b>",parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return
            si="🙈" if hidden else "👁"; st="Скрыты" if hidden else "Открыты"
            lines=[f"<b>📋 События</b> | {si} {st}:\n"]
            for log in logs:
                if hidden:
                    un=mask_str(f"@{log['username']}") if log.get('username') else ""
                    us=mask_str(log['uid']) if log.get('uid') else ""
                    deal=" #***" if log.get('deal_id') else ""
                else:
                    un=f"@{log['username']}" if log.get('username') else ""
                    us=f"<code>{log['uid']}</code>" if log.get('uid') else ""
                    deal=f" #{log['deal_id']}" if log.get('deal_id') else ""
                ex=f" — {log['extra']}" if log.get('extra') else ""
                lines.append(f"<b>{log['time']}</b> {log['event']}{deal}\n{un} {us}{ex}\n")
            txt="\n".join(lines)[:4000]; tl2="👁 Открыть" if hidden else "🙈 Скрыть"
            await q.message.edit_text(txt,parse_mode="HTML",reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(tl2,callback_data="adm_logs_toggle")],
                [InlineKeyboardButton("🔄 Обновить",callback_data="adm_logs")],
                [InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]
            ])); return

        if d=="adm_menu_desc":
            ud["adm_step"]="menu_desc"
            await q.message.edit_text("<b>Введите новое описание меню:</b>",parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Отмена",callback_data="adm_back")]])); return

        if d=="adm_deals":
            db=load_db(); deals=db.get("deals",{})
            if not deals:
                await q.message.edit_text("<b>Сделок нет.</b>",parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return
            text="<b>📋 Последние 10 сделок:</b>\n"
            for did,dv in list(deals.items())[-10:]:
                text+=f"\n<b>{did}</b> | {tname(dv.get('type',''))} | {dv.get('amount')} {dv.get('currency')} | {dv.get('status')}"
            await q.message.edit_text(text,parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return

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
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]])); return
            lines=[f"{E_STATS} <b>Отзывы @{uname2} ({len(revs)}):</b>"]; rows2=[]
            for i,r in enumerate(revs):
                lines.append(f"\n{i+1}. {r}")
                rows2.append([InlineKeyboardButton(f"🗑 #{i+1}",callback_data=f"adm_del_rev_{target}_{i}")])
            rows2.append([InlineKeyboardButton("🔙 Назад",callback_data="adm_back")])
            await q.message.edit_text("\n".join(lines),parse_mode="HTML",reply_markup=InlineKeyboardMarkup(rows2)); return

        sm={"adm_status_verified":"✅ Проверенный","adm_status_garant":"🛡 Гарант",
            "adm_status_caution":"⚠️ Осторожно","adm_status_scammer":"🚫 Мошенник","adm_status_clear":""}
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
        db=load_db(); ok_kb=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 Панель",callback_data="adm_back")]])

        if step=="set_log_chat":
            c2=text.strip()
            if not c2.lstrip("-").isdigit():
                await update.message.reply_text("<b>Неверный chat ID. Пример: -1001234567890</b>",parse_mode="HTML"); return
            db["log_chat_id"]=c2; save_db(db)
            await update.message.reply_text(f"{E_OK} <b>Лог-канал установлен!</b>\n<code>{c2}</code>",parse_mode="HTML",reply_markup=ok_kb)
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
                f"<b>@{u2.get('username','—')} (<code>{found}</code>)\nСделок: {u2.get('total_deals',0)} | Реп: {u2.get('reputation',0)}\nБаланс: {u2.get('balance',0)} RUB\nСтатус: {u2.get('status','—')}</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📝 Отзыв",callback_data="adm_add_review"),InlineKeyboardButton("🗑 Отзывы",callback_data="adm_reviews")],
                    [InlineKeyboardButton("🔢 Сделок",callback_data="adm_set_deals"),InlineKeyboardButton("✅ Успешных",callback_data="adm_set_success")],
                    [InlineKeyboardButton("💵 Оборот",callback_data="adm_set_turnover"),InlineKeyboardButton("⭐️ Репут.",callback_data="adm_set_rep")],
                    [InlineKeyboardButton("➕ Выдать баланс",callback_data="adm_add_bal"),InlineKeyboardButton("➖ Забрать",callback_data="adm_take_bal")],
                    [InlineKeyboardButton("🏷 Статус",callback_data="adm_set_status")],
                    [InlineKeyboardButton("✅ Проверенный",callback_data="adm_status_verified"),InlineKeyboardButton("🛡 Гарант",callback_data="adm_status_garant")],
                    [InlineKeyboardButton("⚠️ Осторожно",callback_data="adm_status_caution"),InlineKeyboardButton("🚫 Мошенник",callback_data="adm_status_scammer")],
                    [InlineKeyboardButton("❌ Убрать статус",callback_data="adm_status_clear")],
                    [InlineKeyboardButton("🔙 Назад",callback_data="adm_back")]
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
            await update.message.reply_text(f"{E_OK} <b>Баннер «{BANNER_SECTIONS.get(section,section)}» обновлён!</b>",
                parse_mode="HTML",reply_markup=adm_banners_kb(load_db())); return

        if step=="menu_desc":
            db["menu_description"]=text; save_db(db)
            await update.message.reply_text(f"{E_OK} <b>Описание обновлено!</b>",parse_mode="HTML",reply_markup=ok_kb)
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
                add_log(db,"💰 Баланс выдан",uid=target,username=u2.get("username",""),extra=f"+{amt2} RUB")
                try:
                    tl=get_lang(int(target)); tr=tl=="ru"
                    await context.bot.send_message(chat_id=int(target),
                        text=f"{E_CHECK} <b>{R(tr,'Баланс пополнен!','Balance topped up!')}</b>\n<blockquote>+{amt2} RUB</blockquote>",parse_mode="HTML")
                except: pass
            elif field=="take_balance":
                try: amt2=int(text)
                except: await update.message.reply_text("<b>Введите число!</b>",parse_mode="HTML"); return
                u2["balance"]=max(0,u2.get("balance",0)-amt2)
                add_log(db,"💸 Баланс списан",uid=target,username=u2.get("username",""),extra=f"-{amt2} RUB")
            else: u2[field]=text
            db["users"][target]=u2; save_db(db)
            await update.message.reply_text(f"{E_OK} <b>Обновлено! Баланс: {u2.get('balance',0)} RUB</b>",parse_mode="HTML",reply_markup=ok_kb)
            ud["adm_step"]=None; return

    except Exception as e: logger.error(f"handle_adm_msg: {e}")

# ─── Commands ─────────────────────────────────────────────────────────────────
async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id!=ADMIN_ID: return
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
        await update.message.reply_text(f"{E_OK} <b>Сделка {deal_id} подтверждена!</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_buy: {e}")

async def cmd_set_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args=context.args
        if not args or not args[0].isdigit(): await update.message.reply_text("<b>Пример: /set_my_deals 100</b>",parse_mode="HTML"); return
        db=load_db(); u=get_user(db,str(update.effective_user.id))
        u["success_deals"]=u["total_deals"]=int(args[0]); save_db(db)
        await update.message.reply_text(f"{E_OK} <b>Обновлено!</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_set_deals: {e}")

async def cmd_set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args=context.args
        if not args: await update.message.reply_text("<b>Пример: /set_my_amount 15000</b>",parse_mode="HTML"); return
        try: amt=int(args[0])
        except: await update.message.reply_text("<b>Введите число!</b>",parse_mode="HTML"); return
        db=load_db(); u=get_user(db,str(update.effective_user.id)); u["turnover"]=amt; save_db(db)
        await update.message.reply_text(f"{E_OK} <b>Оборот: {amt} RUB</b>",parse_mode="HTML")
    except Exception as e: logger.error(f"cmd_set_amount: {e}")

async def cmd_add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id!=ADMIN_ID: return
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
        add_log(db,"💰 Баланс выдан (cmd)",uid=target,username=u.get("username",""),extra=f"+{amount} RUB")
        await update.message.reply_text(f"{E_OK} <b>+{amount} RUB → @{u.get('username','?')} (<code>{target}</code>)\nБаланс: {u['balance']} RUB</b>",parse_mode="HTML")
        try:
            tl=get_lang(int(target)); tr=tl=="ru"
            await context.bot.send_message(chat_id=int(target),
                text=f"{E_CHECK} <b>{R(tr,'Баланс пополнен!','Balance topped up!')}</b>\n<blockquote>+{amount} RUB</blockquote>",parse_mode="HTML")
        except: pass
    except Exception as e: logger.error(f"cmd_add_balance: {e}")

async def cmd_take_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id!=ADMIN_ID: return
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
        add_log(db,"💸 Баланс списан (cmd)",uid=target,username=u.get("username",""),extra=f"-{amount} RUB")
        await update.message.reply_text(f"{E_OK} <b>-{amount} RUB ← @{u.get('username','?')} (<code>{target}</code>)\nБаланс: {u['balance']} RUB</b>",parse_mode="HTML")
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
    app.add_handler(CommandHandler("add_balance",cmd_add_balance))
    app.add_handler(CommandHandler("take_balance",cmd_take_balance))
    app.add_handler(CommandHandler("add_review",cmd_add_review))
    app.add_handler(CommandHandler("del_review",cmd_del_review))
    app.add_handler(CommandHandler("my_reviews",cmd_my_reviews))
    app.add_handler(CallbackQueryHandler(on_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,on_msg))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION,handle_adm_msg))

    print(f"Bot @{BOT_USERNAME} started!")
    app.run_polling()

if __name__=="__main__":
    main()
