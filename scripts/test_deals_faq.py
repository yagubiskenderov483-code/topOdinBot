#!/usr/bin/env python3
"""Unit tests for My Deals helpers and FAQ screens (no Telegram I/O)."""
import os
import sys

os.environ.setdefault("BOT_MODE", "miniapp")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bot


def test_user_in_deal():
    d = {"user_id": "1", "partner_uid": "2", "buyer_uid": "2", "seller_uid": "1"}
    assert bot.user_in_deal(d, 1)
    assert bot.user_in_deal(d, "2")
    assert not bot.user_in_deal(d, 99)
    assert not bot.user_in_deal({}, 1)
    assert not bot.user_in_deal(None, 1)


def test_iter_and_filter():
    db = {"deals": {
        "FP1": {"user_id": "5", "status": "pending", "created": "2026-01-01"},
        "FP2": {"user_id": "5", "status": "confirmed", "created": "2026-02-01"},
        "FP3": {"user_id": "9", "status": "pending", "created": "2026-03-01"},
        "FP4": {"partner_uid": "5", "status": "pending", "created": "2026-04-01"},
    }}
    items = bot.iter_user_deals(db, 5)
    ids = [k for k, _ in items]
    assert ids == ["FP4", "FP2", "FP1"]
    assert [k for k, _ in bot.filter_user_deals(items, "act")] == ["FP4", "FP1"]
    assert [k for k, _ in bot.filter_user_deals(items, "done")] == ["FP2"]
    assert len(bot.filter_user_deals(items, "all")) == 3


def test_status_and_button():
    pending = {"status": "pending", "type": "nft", "currency": "TON", "amount": "3"}
    assert "партн" in bot.deal_status_label(pending, "ru") or "partner" in bot.deal_status_label(pending, "en")
    joined = dict(pending, partner_uid="2")
    assert bot.deal_status_label(joined, "ru") == "в работе"
    paid = dict(joined, item_transferred=True, payment_reported=True)
    assert "подтвержд" in bot.deal_status_label(paid, "ru")
    done = {"status": "confirmed", "type": "stars", "currency": "Stars", "amount": "700"}
    assert bot.deal_status_label(done, "uk") == "завершена"
    label = bot.deal_button_label("FP29548", pending, "ru")
    assert label.startswith("FP29548")
    assert len(label) <= 64


def test_page_cb():
    assert bot.parse_my_deals_page_cb("md_p_all_0") == ("all", 0)
    assert bot.parse_my_deals_page_cb("md_p_act_12") == ("act", 12)
    assert bot.parse_my_deals_page_cb("md_p_done_2") == ("done", 2)
    assert bot.parse_my_deals_page_cb("md_p_bad_1") is None
    assert bot.parse_my_deals_page_cb("md_open_FP1") is None


def test_viewer_and_tags():
    db = {"users": {"10": {"username": "alice"}, "20": {"username": "bob"}}}
    deal = {"user_id": "10", "partner_uid": "20", "creator_role": "seller",
            "buyer_uid": "20", "seller_uid": "10", "partner": "@bob"}
    role, is_c = bot.deal_viewer_context(deal, 10)
    assert role == "seller" and is_c is True
    role, is_c = bot.deal_viewer_context(deal, 20)
    assert role == "buyer" and is_c is False
    ctag, ptag, puname = bot.deal_party_tags(db, deal)
    assert ctag == "@alice"
    assert ptag == "@bob"
    assert puname == "bob"


def test_share_and_faq():
    link, share = bot.deal_share_links("FP29548", "ru")
    assert link.endswith("deal_FP29548")
    assert "share/url" in share
    for topic in (None, "deal", "join", "pay", "req", "ref"):
        text = bot.info_how_hub_text("ru") if topic is None else bot.info_how_topic_text(topic, "uk")
        visible = bot.html.unescape(bot._strip_html_tags(text))
        assert len(visible) <= 1024, (topic, len(visible))
        assert "<" in text


def test_user_deal_kb_confirmed():
    kb = bot.user_deal_kb("FP1", {"status": "confirmed"}, "buyer", "ru")
    data = [b.callback_data for row in kb.inline_keyboard for b in row]
    assert "menu_my_deals" in data
    assert "noop" in data


if __name__ == "__main__":
    tests = [
        test_user_in_deal, test_iter_and_filter, test_status_and_button,
        test_page_cb, test_viewer_and_tags, test_share_and_faq,
        test_user_deal_kb_confirmed,
    ]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print("ALL OK")
