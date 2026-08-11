#!/usr/bin/env python3
"""Apply full i18n: wire uk_i18n.json and replace R(ru, -> L(lang, in bot.py."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOT = ROOT / "bot.py"
UK = ROOT / "uk_i18n.json"

I18N_BLOCK = '''
_UK_STRINGS = None

def _load_uk_strings():
    global _UK_STRINGS
    if _UK_STRINGS is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uk_i18n.json")
        try:
            with open(path, encoding="utf-8") as f:
                _UK_STRINGS = json.load(f)
        except Exception as e:
            logger.warning(f"uk_i18n.json: {e}")
            _UK_STRINGS = {}
    return _UK_STRINGS

def T(lang, ru, en, uk=None):
    if lang == "uk":
        if uk is not None:
            return uk
        hit = _load_uk_strings().get(ru)
        if hit is not None:
            return hit
        return ru
    if lang == "en":
        return en
    return ru

def L(lang, ru, en, uk=None):
    return T(lang, ru, en, uk)
'''

def main():
    text = BOT.read_text(encoding="utf-8")

    # Replace old T/L block
    old = re.search(
        r"def R\(ru, a, b\): return a if ru else b\n\ndef T\(lang, ru, en, uk=None\):\n    if lang==\"uk\".*?return ru\n\n",
        text,
        re.S,
    )
    if not old:
        raise SystemExit("T() block not found")
    text = text[: old.start()] + I18N_BLOCK.strip() + "\n\n" + text[old.end() :]

    # Remove duplicate L if we had T already with L - the block includes L

    # Replace R(ru, -> L(lang,
    text = re.sub(r"\bR\(ru,", "L(lang,", text)

    # Special lang variables
    special = [
        (r"\bR\(creator_ru,", "L(creator_lang,"),
        (r"\bR\(get_lang\(joiner\.id\)=='ru',", "L(get_lang(joiner.id),"),
        (r"\bR\(get_lang\(uid\)=='ru',", "L(get_lang(uid),"),
        (r"\bR\(get_lang\(seller\.id\)=='ru',", "L(get_lang(seller.id),"),
        (r"\bR\(rb,", "L(bl,"),
        (r"\bR\(rb2,", "L(rb2_lang,"),
        (r"\bR\(rs2,", "L(sl2,"),
        (r"\bR\(rr,", "L(rr_lang,"),
        (r"\bR\(tr,", "L(tr,"),
    ]
    for pat, rep in special:
        text = re.sub(pat, rep, text)

    # Fix rb2_lang - find adm_confirm and add rb2_lang = get_lang
    if "rb2_lang" in text and "rb2_lang =" not in text:
        text = text.replace(
            "suid=seller_uid; sl2=get_lang(int(suid)) if suid else \"ru\"; rs2=sl2==\"ru\"",
            "suid=seller_uid; sl2=get_lang(int(suid)) if suid else \"ru\"; rb2_lang=sl2; rs2=sl2==\"ru\"",
        )
        text = text.replace(
            "rb2=get_lang(int(buyer_uid_d)) if buyer_uid_d else \"ru\"",
            "rb2=get_lang(int(buyer_uid_d)) if buyer_uid_d else \"ru\"; rb2_lang=rb2",
        )

    # rr_lang for referral notifications
    for needle, insert in [
        (
            "rr=db[\"users\"].get(str(ref_by),{})",
            "rr_lang=get_lang(int(ref_by)) if ref_by else \"ru\"\n        rr=db[\"users\"].get(str(ref_by),{})",
        ),
    ]:
        if "rr_lang" in text and needle in text and insert not in text:
            text = text.replace(needle, insert, 1)

    # deal_payment_details_lines: replace ru ternary with L
    text = text.replace(
        "f\"<b>{Ecrd} {'СБП / Карта' if ru else 'Card / Phone'} {bank}:</b>\"",
        "f\"<b>{Ecrd} {L(lang,'СБП / Карта','Card / Phone','СБП / Картка')} {bank}:</b>\"",
    )

    # topup_unit
    text = text.replace(
        'def topup_unit(method, lang="ru"):\n    ru=lang=="ru"\n    return {\n        "stars":R(ru,"звёзд","Stars"),"rub":"RUB",',
        'def topup_unit(method, lang="ru"):\n    return {\n        "stars":L(lang,"звёзд","Stars","зірок"),"rub":balance_unit(lang),',
    )
    text = text.replace(
        'def topup_unit(method, lang="ru"):\n    ru=lang=="ru"\n    return {\n        "stars":L(lang,"звёзд","Stars"),"rub":"RUB",',
        'def topup_unit(method, lang="ru"):\n    return {\n        "stars":L(lang,"звёзд","Stars","зірок"),"rub":balance_unit(lang),',
    )

    # req_need_label
    text = text.replace(
        """def req_need_label(field, lang="ru"):
    ru=lang=="ru"
    if field=="ton": return R(ru,"кошелёк Tonkeeper","Tonkeeper wallet")
    if field=="stars": return R(ru,"@username для звёзд","@username for Stars")
    return R(ru,"карту / телефон","card / phone")""",
        """def req_need_label(field, lang="ru"):
    if field=="ton": return L(lang,"кошелёк Tonkeeper","Tonkeeper wallet","гамець Tonkeeper")
    if field=="stars": return L(lang,"@username для звёзд","@username for Stars","@username для зірок")
    return L(lang,"карту / телефон","card / phone","картку / телефон")""",
    )

    # deal_payment_details - remove ru= line if only used for R
    text = text.replace(
        "def deal_payment_details_lines(deal_id, d, lang=\"ru\"):\n    ru=lang==\"ru\"\n    pay_cur",
        "def deal_payment_details_lines(deal_id, d, lang=\"ru\"):\n    pay_cur",
    )

    # Remove redundant ru=lang=="ru" in keyboard functions (keep if ru used elsewhere)
    # Safe: only remove when next lines use L(lang, only

    BOT.write_text(text, encoding="utf-8")
    print("bot.py patched")

    # Fix em dashes in uk json
    uk_text = UK.read_text(encoding="utf-8")
    uk_text2 = uk_text.replace("\u2014", "-").replace("\u2013", "-")
    if uk_text2 != uk_text:
        UK.write_text(uk_text2, encoding="utf-8")
        print("uk_i18n.json dashes fixed")

if __name__ == "__main__":
    main()
