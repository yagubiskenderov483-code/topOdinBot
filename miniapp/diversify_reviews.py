#!/usr/bin/env python3
"""Rewrite Mini App reviews so every text is unique and matches the nickname language."""
from __future__ import annotations

import json
import random
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "reviews.json"

CYR = re.compile(r"[А-Яа-яЁёІіЇїЄє]")
LAT = re.compile(r"[A-Za-z]")

ANON_RU = {"аноним", "анонимный", "без ника", "скрытый ник"}
ANON_EN = {"anonymous", "anon", "hidden user"}

RU_GIVEN = {
    "алина", "аня", "артём", "артем", "богдан", "варя", "вера", "вика", "влад",
    "вова", "глеб", "даня", "даша", "денис", "дима", "егор", "женя", "игорь",
    "илья", "ира", "катя", "кира", "кирилл", "ксюша", "лена", "лев", "лиза",
    "лёша", "леша", "максим", "макс", "марина", "марк", "маша", "милана",
    "миша", "настя", "никита", "олег", "оля", "паша", "полина", "рита", "рома",
    "саша", "света", "сергей", "слава", "соня", "таня", "тимур", "толя", "федя",
    "юля", "яна", "ваня", "dima", "vika", "sasha", "nikita", "kirill", "lena",
    "masha", "katya", "nastya", "dasha", "polina", "alina", "sonya",
}
MALE_RU = {
    "артём", "артем", "богдан", "влад", "вова", "глеб", "даня", "денис", "дима",
    "егор", "игорь", "илья", "кирилл", "лёша", "леша", "максим", "макс", "марк",
    "миша", "никита", "олег", "паша", "рома", "сергей", "слава", "тимур", "толя",
    "федя", "ваня", "лев", "dima", "nikita", "kirill",
}
FEMALE_RU = {
    "алина", "аня", "варя", "вера", "вика", "даша", "ира", "катя", "кира",
    "ксюша", "лена", "лиза", "марина", "маша", "милана", "настя", "оля", "полина",
    "рита", "света", "соня", "таня", "юля", "яна", "vika", "lena",
}
EN_GIVEN = {
    "alex", "avery", "ben", "blake", "brett", "cameron", "casey", "chris",
    "cole", "drew", "elle", "emma", "ethan", "gabe", "hannah", "ian", "ivy",
    "jake", "lila", "luke", "maya", "mia", "miles", "nate", "nora", "owen",
    "parker", "quinn", "ruby", "ryan", "sam", "seth", "taylor", "max",
    "tonking", "stars",
}

# acc = «оплатил X»; nom = «X пришёл»; prep = «по X».
NOUN_RU = {
    "Stars": {"acc": "звёзды", "nom": "звёзды", "prep": "звёздам", "land": ["пришли", "капнули", "оказались на аккаунте"]},
    "TON": {"acc": "TON", "nom": "TON", "prep": "TON", "land": ["дошёл", "пришёл", "упал на кошелёк"]},
    "USDT": {"acc": "USDT", "nom": "USDT", "prep": "USDT", "land": ["дошли", "пришли", "упали на кошелёк"]},
    "Premium": {"acc": "премиум", "nom": "премиум", "prep": "премиуму", "land": ["активировался", "включился", "прилетел"]},
    "NFT": {"acc": "NFT", "nom": "NFT", "prep": "NFT", "land": ["передали", "оказался у меня"]},
    "NFT Gift": {"acc": "NFT-гифт", "nom": "NFT-гифт", "prep": "гифту", "land": ["передали", "пришёл после проверки"]},
    "NFT Username": {"acc": "NFT-юзернейм", "nom": "ник", "prep": "юзернейму", "land": ["передали", "сменился как в заявке"]},
    "Crypto": {"acc": "крипту", "nom": "оплата криптой", "prep": "крипте", "land": ["прошла", "закрылась"]},
    "Крипта": {"acc": "крипту", "nom": "оплата криптой", "prep": "крипте", "land": ["прошла", "закрылась"]},
    "Escrow": {"acc": "сделку через гаранта", "nom": "сделка через гаранта", "prep": "гаранту", "land": ["закрылась", "прошла спокойно"]},
    "Гарант": {"acc": "сделку через гаранта", "nom": "сделка через гаранта", "prep": "гаранту", "land": ["закрылась", "прошла спокойно"]},
    "Username": {"acc": "юзернейм", "nom": "юзернейм", "prep": "нику", "land": ["передали", "ушёл покупателю"]},
    "Gift": {"acc": "гифт", "nom": "гифт", "prep": "подарку", "land": ["дошёл", "отдали"]},
    "Карта": {"acc": "перевод на карту", "nom": "перевод на карту", "prep": "карте", "land": ["дошёл", "деньги пришли"]},
    "Card": {"acc": "перевод на карту", "nom": "перевод на карту", "prep": "карте", "land": ["дошёл", "деньги пришли"]},
}
NOUN_EN = {
    "Stars": {"obj": "Stars", "land": ["landed", "showed up", "hit the account"]},
    "TON": {"obj": "TON", "land": ["arrived", "hit the wallet", "went through"]},
    "USDT": {"obj": "USDT", "land": ["arrived", "hit the wallet", "went through"]},
    "Premium": {"obj": "Premium", "land": ["activated", "turned on", "started"]},
    "NFT": {"obj": "the NFT", "land": ["was transferred", "showed up"]},
    "NFT Gift": {"obj": "the NFT gift", "land": ["came through after the check", "arrived"]},
    "NFT Username": {"obj": "the NFT username", "land": ["was handed over", "updated"]},
    "Crypto": {"obj": "crypto", "land": ["went through", "cleared"]},
    "Крипта": {"obj": "crypto", "land": ["went through", "cleared"]},
    "Escrow": {"obj": "the escrow deal", "land": ["closed cleanly", "released on time"]},
    "Гарант": {"obj": "the escrow deal", "land": ["closed cleanly", "released on time"]},
    "Username": {"obj": "the username", "land": ["was transferred", "moved over"]},
    "Gift": {"obj": "the gift", "land": ["arrived", "came through"]},
    "Карта": {"obj": "the card payout", "land": ["hit the card", "landed"]},
    "Card": {"obj": "the card payout", "land": ["hit the card", "landed"]},
}


def fold_name(name: str) -> str:
    return unicodedata.normalize("NFKC", name or "").strip()


def first_token(name: str) -> str:
    folded = fold_name(name)
    parts = re.split(r"[\s._0-9]+", folded)
    return (parts[0] if parts else folded).lower()


def name_lang(name: str) -> str:
    raw = (name or "").strip()
    folded = fold_name(raw)
    low = folded.lower()
    if CYR.search(raw) or CYR.search(folded):
        return "ru"
    if low in ANON_RU:
        return "ru"
    if low in ANON_EN:
        return "en"
    token = first_token(raw)
    if token in RU_GIVEN:
        return "ru"
    if token in EN_GIVEN:
        return "en"
    if re.fullmatch(r"[A-Z][a-z]+(?:\s+[A-Z]\.)?", folded):
        return "en"
    if "_" in raw or re.search(r"\d", raw) or raw.islower():
        return "ru"
    if LAT.search(raw) and not CYR.search(raw):
        return "en"
    return "ru"


def ru_gender(name: str) -> str:
    token = first_token(name)
    if token in MALE_RU:
        return "m"
    if token in FEMALE_RU:
        return "f"
    return "n"


def pick(rng: random.Random, seq):
    return seq[rng.randrange(len(seq))]


def cap(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    return s[0].upper() + s[1:]


def finish(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.!?])", r"\1", s)
    s = re.sub(r"[.]{2,}", ".", s)
    if s and s[-1] not in ".!?…👍🔥✅⭐":
        s += "."
    return cap(s)


def join_sents(*parts: str) -> str:
    out = []
    for p in parts:
        p = (p or "").strip()
        if not p:
            continue
        out.append(finish(p))
    return " ".join(out)


def ru_num(n: int, one: str, few: str, many: str) -> str:
    n2 = n % 100
    if 11 <= n2 <= 14:
        return many
    n1 = n % 10
    if n1 == 1:
        return one
    if 2 <= n1 <= 4:
        return few
    return many


def ru_time_pos(rng: random.Random) -> str:
    kind = rng.randrange(6)
    if kind == 0:
        n = rng.randint(18, 88)
        return f"за {n} {ru_num(n, 'секунду', 'секунды', 'секунд')}"
    if kind == 1:
        n = pick(rng, [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15])
        return f"за {n} {ru_num(n, 'минуту', 'минуты', 'минут')}"
    if kind == 2:
        n = pick(rng, [2, 3, 4, 5, 6, 7, 8, 10])
        return f"через {n} {ru_num(n, 'минуту', 'минуты', 'минут')}"
    return pick(rng, [
        "за минуту", "за пару минут", "почти сразу", "без паузы после оплаты",
        "на одном дыхании", "с первой попытки",
        "буквально сразу после оплаты", "за считанные минуты",
        "быстрее обычного", "сразу после подтверждения",
    ])


def ru_time_slow(rng: random.Random) -> str:
    n = pick(rng, [12, 15, 18, 20, 25, 30, 35, 40, 45, 50, 55, 70, 90])
    return pick(rng, [
        f"ответили только через {n} {ru_num(n, 'минуту', 'минуты', 'минут')}",
        f"статус висел минут {n}",
        f"подтверждение крутилось {n} {ru_num(n, 'минуту', 'минуты', 'минут')}",
        "продавец сначала пропал",
        "менеджер взял паузу",
        "реквизиты пришлось переспрашивать",
        "уведомление запоздало",
    ])


def en_time_pos(rng: random.Random) -> str:
    kind = rng.randrange(5)
    if kind == 0:
        n = rng.randint(18, 88)
        unit = "second" if n == 1 else "seconds"
        return f"in {n} {unit}"
    if kind == 1:
        n = pick(rng, [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15])
        return f"in {n} min"
    return pick(rng, [
        "in a minute", "in a couple of minutes", "right after I paid",
        "at the first attempt", "before I locked the phone", "without extra back and forth",
    ])


def en_time_slow(rng: random.Random) -> str:
    n = pick(rng, [12, 15, 20, 25, 30, 40, 45, 50, 60])
    return pick(rng, [
        f"it sat pending for {n} min",
        f"the reply came after {n} min",
        "the seller went quiet for a bit",
        "the status lagged",
        "I had to re-ask the details",
        "the manager was slow to pick it up",
    ])


def amount_ru(rng, tag: str) -> str:
    if tag == "Stars":
        n = pick(rng, [15, 25, 40, 50, 75, 80, 100, 120, 150, 200, 250, 300, 500, 750, 1000])
        return f"заказ на {n} звёзд"
    if tag == "TON":
        n = pick(rng, [2, 3, 5, 8, 10, 12, 15, 20, 25, 40, 50])
        return f"{n} TON"
    if tag == "USDT":
        n = pick(rng, [5, 8, 10, 12, 15, 20, 25, 40, 50, 75, 100])
        return f"{n} USDT"
    if tag in ("Premium",):
        return pick(rng, ["премиум на месяц", "премиум на 3 месяца"])
    if tag in ("NFT Username", "Username"):
        return pick(rng, ["ник короткий", "юзерка с редкими символами", "ник как в заявке"])
    if tag in ("NFT Gift", "Gift", "NFT"):
        return pick(rng, ["после проверки гифта", "лот не из дешёвых", "мелочь, но принцип важен"])
    if tag in ("Карта", "Card"):
        return pick(rng, ["перевод на карту", "сумма небольшая", "чек не огромный"])
    return pick(rng, ["сумма небольшая", "лот недорогой", "чек нормальный"])


def amount_en(rng, tag: str) -> str:
    if tag == "Stars":
        n = pick(rng, [15, 25, 50, 75, 100, 150, 200, 250, 300, 500, 1000])
        return f"a {n}-star order"
    if tag == "TON":
        n = pick(rng, [2, 3, 5, 8, 10, 12, 20, 25, 40])
        return f"{n} TON"
    if tag == "USDT":
        n = pick(rng, [5, 10, 12, 20, 25, 40, 50, 80])
        return f"{n} USDT"
    if tag == "Premium":
        return pick(rng, ["a one-month Premium", "three months of Premium"])
    if tag in ("NFT Username", "Username"):
        return pick(rng, ["a short username", "the exact handle from the request"])
    return pick(rng, ["a small lot", "not a tiny order", "a mid-size deal"])


def ru_noun(tag):
    return NOUN_RU.get(tag) or NOUN_RU["Escrow"]


def en_noun(tag):
    return NOUN_EN.get(tag) or NOUN_EN["Escrow"]


def gform(gender: str, m: str, f: str, n: str) -> str:
    return {"m": m, "f": f, "n": n}[gender]


SITU_RU = [
    "с телефона", "с компа", "ночью", "утром", "после работы", "в обед",
    "перед сном", "в выходной", "прямо в боте", "без выхода в лс",
]
SITU_EN = [
    "from my phone", "from desktop", "late at night", "in the morning",
    "after work", "during lunch", "inside the bot", "without leaving to DMs",
]
EXTRA_RU = [
    "история обновилась сама",
    "скрин кинули без просьбы",
    "сумма сошлась копейка в копейку",
    "комиссию показали заранее",
    "доступ открылся сразу",
    "статус сменился понятно",
    "условия не прыгали",
    "повторно ничего не просили",
    "реквизиты совпали с карточкой",
    "продавец без воды писал",
    "шаги в боте понятные",
    "не пришлось ничего гуглить",
    "уведомление пришло вовремя",
    "чат не уводили в лс",
    "ник в заявке совпал",
    "деньги и товар сошлись",
    "поддержка не понадобилась",
    "всё осталось внутри бота",
    "продавец сразу подтвердил получение",
    "комментарий к платежу нашли",
    "после оплаты статус сам прыгнул",
    "без спора и претензий",
]
EXTRA_EN = [
    "history updated by itself",
    "they sent a screenshot unprompted",
    "the amount matched exactly",
    "the fee was shown up front",
    "access flipped on immediately",
    "the status changes were readable",
    "the terms did not move",
    "nobody asked the same thing twice",
    "the details matched the card",
    "the seller wrote without fluff",
    "the steps in the bot were clear",
    "I didn't need to google anything",
    "the handle matched the request",
    "funds and item lined up",
    "didn't need support at all",
    "stayed inside the bot",
    "seller confirmed receipt right away",
    "they found the payment comment",
    "status flipped by itself after payment",
    "no dispute, no extras",
]
END_RU = [
    "без сюрпризов", "спокойно прошло", "как и обещали", "без нервов",
    "ещё зайду", "буду брать снова", "зашло", "всё прозрачно",
    "гарант отработал", "не кинули", "чисто", "нормальная сделка",
    "без лишней суеты", "продавец адекватный", "можно повторять",
]
END_EN = [
    "would use again", "no drama", "clean deal", "seller was chill",
    "escrow did its job", "I'm good with it", "exactly as listed",
    "no weird DMs", "worked first time", "I'll be back", "solid overall",
]
NIT_RU = [
    "менеджер ответил не сразу",
    "интерфейс местами мутный",
    "статус обновлялся с паузой",
    "один раз переспросили реквизиты",
    "долго висело pending",
    "саппорт не молниеносный",
    "кнопки не самые очевидные",
    "продавец коротко пропал и вернулся",
    "уведомление пришло с лагом",
    "чуть подождали подтверждение",
]
NIT_EN = [
    "support wasn't instant",
    "the status lagged a bit",
    "the UI is a little confusing",
    "I had to re-ask the details once",
    "the seller went quiet for a minute",
    "pending sat there too long",
    "the buttons aren't obvious",
    "the notification was late",
]
NEG_RU_M = [
    "уже хотел отменять",
    "слишком много возни",
    "продавец тупил с ответами",
    "подтверждение тянули",
    "реквизиты путали",
    "больше так не хочу",
    "поддержка разочаровала",
    "сделка еле доползла",
]
NEG_RU_F = [
    "уже хотела отменять",
    "слишком много возни",
    "продавец тупил с ответами",
    "подтверждение тянули",
    "реквизиты путали",
    "больше так не хочу",
    "поддержка разочаровала",
    "сделка еле доползла",
]
MIX_RU_M = [
    "в итоге закрыли",
    "товар на месте, процесс так себе",
    "средне, без катастрофы",
    "можно быстрее",
    "сработало, но нервы потратил",
    "не провал, но и не вау",
    "закрылось, впечатление серое",
    "ожидал проще",
    "по факту ок, по ощущениям тягомотина",
    "не отменил, но и не кайфанул",
    "сделка живая, сервис вялый",
    "норм результат, кривой путь",
]
MIX_RU_F = [
    "в итоге закрыли",
    "товар на месте, процесс так себе",
    "средне, без катастрофы",
    "можно быстрее",
    "сработало, но нервы потратила",
    "не провал, но и не вау",
    "закрылось, впечатление серое",
    "ожидала проще",
    "по факту ок, по ощущениям тягомотина",
    "не отменила, но и не кайфанула",
    "сделка живая, сервис вялый",
    "норм результат, кривой путь",
]
BAD_RU_M = [
    "очень долго и непонятно",
    "разбирать пришлось вручную",
    "ощущение бардака",
    "второй раз так не пойду",
    "время ушло на ожидание",
    "организация слабая",
]
BAD_RU_F = BAD_RU_M
NEG_EN = [
    "I almost cancelled",
    "too much back and forth",
    "the seller was slow",
    "confirmation dragged",
    "the details were messy",
    "support didn't help much",
]
MIX_EN = [
    "got the item, process was meh",
    "not bad, not great",
    "it closed, that's the nicest I can say",
    "fine in the end",
]
BAD_EN = [
    "really messy process",
    "too slow and unclear",
    "wouldn't repeat that",
    "felt disorganized",
    "burned time waiting",
]


def gen_ru(rng: random.Random, stars: int, tag: str, gender: str, casual: bool) -> str:
    info = ru_noun(tag)
    acc, nom, prep = info["acc"], info["nom"], info["prep"]
    land = pick(rng, info["land"])
    tpos = ru_time_pos(rng)
    tslow = ru_time_slow(rng)
    amt = amount_ru(rng, tag)
    situ = pick(rng, SITU_RU)
    extra = pick(rng, EXTRA_RU)
    end = pick(rng, END_RU)
    nit = pick(rng, NIT_RU)
    mix = pick(rng, MIX_RU_F if gender == "f" else MIX_RU_M)
    neg = pick(rng, NEG_RU_F if gender == "f" else NEG_RU_M)
    bad = pick(rng, BAD_RU_F if gender == "f" else BAD_RU_M)
    pay = gform(gender, "оплатил", "оплатила", "оплатили")
    took = gform(gender, "взял", "взяла", "оформили")
    got = gform(gender, "получил", "получила", "получили")
    wait = gform(gender, "ждал", "ждала", "ждали")
    did = gform(gender, "делал", "делала", "оформляли")
    wrote = gform(gender, "писал", "писала", "писали")
    repeat = pick(rng, [
        "первый раз тут", "второй раз", "уже третий заказ",
        "уже не первый раз", "снова сюда", "впервые через этого гаранта",
    ])

    if stars == 5:
        shapes = [
            lambda: join_sents(f"{pay} {acc} {tpos}", extra),
            lambda: join_sents(f"{nom} {land} {tpos}", f"продавец на связи, {end}"),
            lambda: join_sents(repeat, f"{nom} {land} {tpos}"),
            lambda: join_sents(f"сделку по {prep} закрыли {tpos}", end),
            lambda: join_sents(f"в лс не {wrote}", f"{nom} {land} {tpos}"),
            lambda: join_sents(f"{did} {situ}", f"{pay} {acc} — {land} {tpos}"),
            lambda: join_sents(f"{took} {amt}", f"{land} {tpos}", end),
            lambda: join_sents(f"по {prep} — {end}", tpos, extra),
            lambda: join_sents(f"{got} {acc} {tpos}", extra, end if rng.random() < 0.5 else ""),
            lambda: join_sents(f"{nom} {land}, {extra}", situ, end),
            lambda: join_sents(f"гарант отработал, {nom} {land} {tpos}"),
            lambda: join_sents(f"{pay} {acc} {situ}", extra, end),
            lambda: join_sents(f"{situ} {took} {acc}", f"{land} {tpos}"),
            lambda: join_sents(f"{amt} — {land} {tpos}", extra),
            lambda: join_sents(f"без споров закрыли {acc}", tpos, extra),
            lambda: join_sents(f"{got} ровно то, что в заявке", f"{nom} {land} {tpos}"),
        ]
        if casual:
            shapes += [
                lambda: join_sents(f"норм, {nom} {land} {tpos}"),
                lambda: join_sents("мне зашло", f"{nom} {tpos}, {end}"),
                lambda: join_sents("не кинули", f"{nom} {land} {tpos}"),
                lambda: join_sents(f"короче по {prep} — {end}", extra),
            ]
    elif stars == 4:
        shapes = [
            lambda: join_sents(f"{nom} {land}", f"но {nit}"),
            lambda: join_sents(f"{took} {acc}, в целом ок", nit),
            lambda: join_sents("4 звезды только из-за ожидания", f"по {prep} само нормально"),
            lambda: join_sents(f"{got} {acc}", f"{nit}, зато {end}"),
            lambda: join_sents(repeat, f"товар тот, но {nit}"),
            lambda: join_sents(f"сделка закрылась, {nit}", amt),
            lambda: join_sents("почти пятёрка", f"{nom} {land} {situ}", nit),
            lambda: join_sents(f"{pay} {acc} {situ}", nit, extra),
        ]
    elif stars == 3:
        shapes = [
            lambda: join_sents(f"средне по {prep}", mix, tslow),
            lambda: join_sents(f"{wait} дольше, чем хотелось", f"но {nom} в итоге на месте"),
            lambda: join_sents(f"{nom}: {mix}", nit),
            lambda: join_sents("не вау и не провал", f"{nom} — {tslow}"),
            lambda: join_sents("сначала реквизиты криво кинули, потом разобрались", mix),
            lambda: join_sents(f"{got} что надо, процесс не зашёл", f"{nom}, {situ}"),
            lambda: join_sents(f"{nom} {land}, но {nit}", mix),
            lambda: join_sents(f"три звезды и ни больше", f"{got} {acc}, {tslow}"),
            lambda: join_sents(f"{situ} всё вышло кривовато", f"{nom} всё же на месте"),
            lambda: join_sents(mix, f"по {prep} {tslow}"),
        ]
    elif stars == 2:
        shapes = [
            lambda: join_sents(f"{nom} вроде дошёл, но {neg}", tslow),
            lambda: join_sents(f"{wait} слишком долго", "сделку еле закрыли"),
            lambda: join_sents(neg, f"{nom} — {tslow}"),
            lambda: join_sents(f"почти сорвалось по {prep}", tslow, nit),
            lambda: join_sents("товар ок по итогу, организация нет", nit),
            lambda: join_sents(f"два балла за результат, не за сервис", f"{nom}, {tslow}"),
            lambda: join_sents(f"{neg}, хотя {got} {acc}"),
            lambda: join_sents("долго спорили из-за мелочей", f"{nom} — {tslow}"),
        ]
    else:
        shapes = [
            lambda: join_sents(bad, f"{nom} — {tslow}", neg),
            lambda: join_sents(f"не понравилось, как вели сделку по {prep}", tslow),
            lambda: join_sents(neg, f"{nom} — {tslow}"),
            lambda: join_sents("очень муторно", f"{nom}: {tslow}", bad),
            lambda: join_sents("разбирать пришлось", tslow, "второй раз так не пойду"),
            lambda: join_sents("один балл, чтобы отметить что вообще закрыли", f"{nom} — {tslow}"),
            lambda: join_sents(bad, nit, f"{acc} больше не возьму так"),
        ]

    text = pick(rng, shapes)()
    if stars >= 5 and rng.random() < 0.07:
        text = text.rstrip(".") + " " + pick(rng, ["👍", "✅", "🔥"])
    return text


def gen_en(rng: random.Random, stars: int, tag: str, casual: bool) -> str:
    info = en_noun(tag)
    obj = info["obj"]
    land = pick(rng, info["land"])
    tpos = en_time_pos(rng)
    tslow = en_time_slow(rng)
    amt = amount_en(rng, tag)
    situ = pick(rng, SITU_EN)
    extra = pick(rng, EXTRA_EN)
    end = pick(rng, END_EN)
    nit = pick(rng, NIT_EN)
    mix = pick(rng, MIX_EN)
    neg = pick(rng, NEG_EN)
    bad = pick(rng, BAD_EN)
    repeat = pick(rng, [
        "first time here", "second order", "third time buying",
        "not my first deal here", "came back again",
    ])
    paid = "bought " + obj

    if stars == 5:
        shapes = [
            lambda: join_sents(f"{paid} and it {land} {tpos}", extra),
            lambda: join_sents(f"{obj} {land} {tpos}", end),
            lambda: join_sents(repeat, f"{obj} {land} {tpos}"),
            lambda: join_sents("kept everything in the bot", f"{obj} {land} {tpos}"),
            lambda: join_sents("seller stayed available", f"{obj} {land} {tpos}", end),
            lambda: join_sents(f"pretty straightforward deal for {obj}", extra, tpos),
            lambda: join_sents(f"did it {situ}", f"{obj} {land}", end),
            lambda: join_sents(f"grabbed {amt} and it {land} {tpos}", extra),
            lambda: join_sents("no extra chat needed", f"{obj} {land} {tpos}"),
            lambda: join_sents(f"honestly, {end} on {obj}", extra),
            lambda: join_sents(f"escrow held funds, then {obj} {land} {tpos}"),
            lambda: join_sents(f"{situ}, I grabbed {obj}", f"it {land} {tpos}"),
            lambda: join_sents(f"{amt} {land} {tpos}", extra),
            lambda: join_sents(f"got exactly what was listed", f"{obj} {land} {tpos}"),
        ]
        if casual:
            shapes += [
                lambda: join_sents(f"{obj} done, {end}", tpos),
                lambda: join_sents("worked fine", f"{obj} {land} {tpos}"),
                lambda: join_sents(f"clean {obj} deal", extra),
            ]
    elif stars == 4:
        shapes = [
            lambda: join_sents(f"{obj} {land}", f"but {nit}"),
            lambda: join_sents("four stars only because of the wait", f"{obj} itself was fine"),
            lambda: join_sents(repeat, f"item matched, {nit}"),
            lambda: join_sents(nit, f"still, {obj} — {end}"),
            lambda: join_sents("almost five", f"{obj} {land} {situ}", nit),
            lambda: join_sents(f"deal closed, {nit}", amt),
        ]
    elif stars == 3:
        shapes = [
            lambda: join_sents(f"mid experience on {obj}", mix),
            lambda: join_sents("waited longer than I wanted", f"then {obj} {land}"),
            lambda: join_sents(f"{obj}: {mix}", nit),
            lambda: join_sents("not a fail, not a wow", f"{obj} — {tslow}"),
            lambda: join_sents(f"details were messy at first, then we closed {obj}"),
            lambda: join_sents(f"three stars feels right", f"{obj} {land}, {nit}"),
            lambda: join_sents(mix, f"{obj} still went through"),
            lambda: join_sents(f"got {obj}, didn't enjoy the process", tslow),
        ]
    elif stars == 2:
        shapes = [
            lambda: join_sents(f"{obj} eventually {land}", neg, tslow),
            lambda: join_sents(f"waited way too long on {obj}", tslow),
            lambda: join_sents(neg, f"{obj} — {tslow}"),
            lambda: join_sents(f"almost fell through on {obj}", nit),
            lambda: join_sents("two stars for delivery, not for support", f"{obj} — {tslow}"),
            lambda: join_sents(f"too much friction for {obj}", neg),
        ]
    else:
        shapes = [
            lambda: join_sents(bad, f"{obj} — {tslow}", neg),
            lambda: join_sents(f"didn't like how they handled {obj}", tslow),
            lambda: join_sents(neg, f"{obj} — {tslow}", "wouldn't repeat that"),
            lambda: join_sents(bad, f"{obj}: {tslow}"),
            lambda: join_sents(f"one star so it stays on the record", f"{obj} {tslow}"),
            lambda: join_sents(f"messy from the start on {obj}", bad),
        ]

    text = pick(rng, shapes)()
    if stars >= 5 and rng.random() < 0.07:
        text = text.rstrip(".") + " " + pick(rng, ["👍", "✅", "🔥"])
    return text


def fingerprint(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[^a-zа-яё0-9]+", " ", t)
    return " ".join(t.split()[:7])


def make_text(rng, lang, stars, tag, name, casual, used, used_fp):
    gender = ru_gender(name) if lang == "ru" else "n"
    text = ""
    for salt in range(120):
        local = random.Random(rng.randint(0, 10**9) + salt * 17)
        if lang == "ru":
            text = gen_ru(local, stars, tag, gender, casual)
        else:
            text = gen_en(local, stars, tag, casual)
        text = text.strip()
        if len(text) < 20:
            continue
        fp = fingerprint(text)
        if text in used or fp in used_fp:
            continue
        used.add(text)
        used_fp.add(fp)
        return text
    # distinctive fallback without a fake ticket id
    bump = ru_time_pos(rng) if lang == "ru" else en_time_pos(rng)
    text = join_sents(text or ("сделка закрылась" if lang == "ru" else "the deal closed"), bump)
    n = 0
    while text in used:
        n += 1
        extra = f"{'ещё раз проверил статус' if lang == 'ru' else 'checked the status again'} {n}"
        text = join_sents(text.rstrip(".0123456789 "), extra)
    used.add(text)
    used_fp.add(fingerprint(text))
    return text


def rewrite(data: dict) -> dict:
    used: set[str] = set()
    used_fp: set[str] = set()
    for idx, row in enumerate(data.get("reviews") or []):
        lang = name_lang(row.get("name", ""))
        stars = int(row.get("stars") or 5)
        tag = row.get("tag") or "Escrow"
        rng = random.Random(f"main:{idx}:{row.get('name')}:{tag}:{stars}:v15")
        row["text"] = make_text(rng, lang, stars, tag, row.get("name", ""), False, used, used_fp)
    for idx, row in enumerate(data.get("future") or []):
        lang = name_lang(row.get("name", ""))
        stars = int(row.get("stars") or 5)
        tag = row.get("tag") or "Escrow"
        rng = random.Random(f"future:{idx}:{row.get('name')}:{tag}:{stars}:v15")
        row["text"] = make_text(rng, lang, stars, tag, row.get("name", ""), True, used, used_fp)
    return data


def audit(data: dict) -> None:
    rows = list(data.get("reviews") or []) + list(data.get("future") or [])
    texts = [r["text"] for r in rows]
    print("total", len(texts), "unique", len(set(texts)))
    mismatch = 0
    samples = []
    for r in rows:
        nl = name_lang(r["name"])
        tl = "ru" if CYR.search(r["text"] or "") else "en"
        if nl != tl:
            mismatch += 1
            if len(samples) < 15:
                samples.append((nl, tl, r["name"], r["text"]))
    print("lang mismatches", mismatch)
    for s in samples:
        print(" ", s)
    praise = ("рекоменду", "ещё зайду", "would use", "clean deal", "без сюрприз", "зашло")
    bad_pos = sum(
        1 for r in rows
        if int(r["stars"]) <= 2 and any(w in r["text"].lower() for w in praise)
    )
    print("low-star with leftover praise", bad_pos)
    print("unique fingerprints", len({fingerprint(t) for t in texts}))
    print("unique 36-char prefixes", len({t[:36] for t in texts}))
    print("avg len", round(sum(len(t) for t in texts) / len(texts), 1))
    print("len min/max", min(map(len, texts)), max(map(len, texts)))
    print("\nRU samples:")
    shown = 0
    for r in data["reviews"]:
        if name_lang(r["name"]) == "ru":
            print(f"  {r['stars']} {r['name']} [{r['tag']}] {r['text']}")
            shown += 1
            if shown >= 10:
                break
    print("\nEN samples:")
    shown = 0
    for r in data["reviews"]:
        if name_lang(r["name"]) == "en":
            print(f"  {r['stars']} {r['name']} [{r['tag']}] {r['text']}")
            shown += 1
            if shown >= 10:
                break
    print("\nlow-star samples:")
    shown = 0
    for r in data["reviews"]:
        if int(r["stars"]) <= 2:
            print(f"  {r['stars']} {r['name']} {r['text']}")
            shown += 1
            if shown >= 8:
                break
    print("\nfuture samples:")
    for r in data["future"][:12]:
        print(f"  {name_lang(r['name'])} {r['stars']} {r['name']} | {r['text']}")


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    rewrite(data)
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit(data)


if __name__ == "__main__":
    main()
