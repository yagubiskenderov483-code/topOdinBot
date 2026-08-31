"""Фильтры пола, прототипы коллекции, миграция схемы."""

from market import (
    Lot,
    PrototypeIndex,
    female_filter_reason,
    is_clean_female_profile,
    looks_female,
    looks_male,
)
from tracker import Config, filter_for_post, format_lot
from tracker_filters import FILTER_SCHEMA, migrate_legacy_filters


def _lot(**kwargs) -> Lot:
    base = dict(id="1", title="Desk Calendar", number=1, stars=6000.0, slug="Desk-1")
    base.update(kwargs)
    return Lot(**base)


def test_emoji_female_name():
    lot = _lot(first_name="Катя 💋", seller="katya_sun")
    assert looks_female(lot)
    assert not looks_male(lot)
    assert is_clean_female_profile(lot)


def test_male_rejected():
    lot = _lot(first_name="Дима", seller="dima_trade")
    assert looks_male(lot)
    assert not looks_female(lot)
    assert female_filter_reason(lot) == "мужской"


def test_unisex_sasha_not_auto_male():
    lot = _lot(first_name="Саша")
    assert not looks_male(lot)


def test_female_username():
    lot = _lot(seller="alina_gift")
    assert looks_female(lot)


def test_ad_profile_rejected():
    lot = _lot(first_name="Катя", about="дарю гифт пиши в лс")
    assert female_filter_reason(lot) == "реклама"
    assert not is_clean_female_profile(lot)


def test_filter_for_post_skips_men():
    now = 1_000_000.0
    girl = _lot(id="g", first_name="Настя", seller="nastya1", free_dm=True, lang_code="ru")
    boy = _lot(id="b", first_name="Игорь", seller="igor1", free_dm=True, lang_code="ru")
    out, stats = filter_for_post(
        [boy, girl],
        {},
        now=now,
        female_only=True,
        strict_ru=True,
        strict_fair_price=False,
        max_gifts=20,
    )
    assert stats["not_female"] == 1
    assert [x.seller for x in out] == ["nastya1"]


def test_prototype_index_floor_and_doc():
    idx = PrototypeIndex()
    doc = object()

    class StarGiftAttributeModel:
        def __init__(self) -> None:
            self.name = "Long Beach"
            self.document = doc

    class Result:
        attributes = [StarGiftAttributeModel()]

    lots = [
        _lot(title="Snoop Dogg", model="Long Beach", stars=900.0),
        _lot(id="2", title="Snoop Dogg", model="Long Beach", stars=700.0),
        _lot(id="3", title="Snoop Dogg", model="Long Beach", stars=1200.0),
    ]
    idx.ingest_result(Result(), lots)
    target = _lot(id="x", title="Snoop Dogg", model="Long Beach", stars=800.0)
    idx.attach(target)
    assert target.market_floor == 700.0
    assert target.model_doc is doc


def test_format_includes_floor_and_backdrop():
    cfg = Config(
        api_id=1,
        api_hash="x",
        session_string="",
        bot_token="",
        target_channel="@test",
    )
    lot = _lot(
        title="Snoop Dogg",
        model="Long Beach",
        backdrop="Sunset",
        market_floor=750.0,
        seller="girl1",
    )
    text = format_lot(lot, cfg, ts=1_777_000_000)
    assert "📊 Рынок прототипа: <b>~750⭐</b>" in text
    assert "🎨 Фон: <b>Sunset</b>" in text


def test_migrate_enables_female_and_fair():
    out = migrate_legacy_filters({"filter_schema": 4, "female_only": False})
    assert out["female_only"] is True
    assert out["strict_fair_price"] is True
    assert out["filter_schema"] == FILTER_SCHEMA


if __name__ == "__main__":
    test_emoji_female_name()
    test_male_rejected()
    test_unisex_sasha_not_auto_male()
    test_female_username()
    test_ad_profile_rejected()
    test_filter_for_post_skips_men()
    test_prototype_index_floor_and_doc()
    test_format_includes_floor_and_backdrop()
    test_migrate_enables_female_and_fair()
    print("OK: filters + prototypes")
