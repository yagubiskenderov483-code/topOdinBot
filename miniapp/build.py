#!/usr/bin/env python3
"""Embed miniapp/reviews.json into miniapp/index.html as window.REVIEWS_DATA."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
DATA = ROOT / "reviews.json"
MARKER = "window.REVIEWS_DATA="


def replace_reviews_data(html: str, payload: str) -> str:
    idx = html.find(MARKER)
    if idx < 0:
        raise SystemExit("REVIEWS_DATA marker not found in index.html")
    start = html.find("{", idx)
    if start < 0:
        raise SystemExit("REVIEWS_DATA object start not found")
    depth = 0
    end = None
    for i, ch in enumerate(html[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise SystemExit("REVIEWS_DATA object end not found")
    # include trailing semicolon if present
    if end < len(html) and html[end] == ";":
        end += 1
    return html[:idx] + f"{MARKER}{payload};" + html[end:]


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = HTML.read_text(encoding="utf-8")
    html = replace_reviews_data(html, payload)
    HTML.write_text(html, encoding="utf-8")
    print(
        f"embedded display={data.get('displayCount') or data.get('count')} "
        f"actual={len(data.get('reviews', []))} avg={data.get('average')} into {HTML.name}"
    )


if __name__ == "__main__":
    main()
