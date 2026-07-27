#!/usr/bin/env python3
"""Embed miniapp/reviews.json into miniapp/index.html as window.REVIEWS_DATA."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
DATA = ROOT / "reviews.json"
MARKER = "window.REVIEWS_DATA="


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = HTML.read_text(encoding="utf-8")
    pattern = re.compile(r"window\.REVIEWS_DATA=\{.*?\};", re.DOTALL)
    if not pattern.search(html):
        raise SystemExit("REVIEWS_DATA marker not found in index.html")
    html = pattern.sub(f"{MARKER}{payload};", html, count=1)
    HTML.write_text(html, encoding="utf-8")
    print(f"embedded {data.get('count', len(data.get('reviews', [])))} reviews into {HTML.name}")


if __name__ == "__main__":
    main()
