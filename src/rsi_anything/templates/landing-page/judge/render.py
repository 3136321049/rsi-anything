"""Check index.html for facts and self-containment, then screenshot it on desktop and phone for the visual jury."""
from __future__ import annotations

import json
import re
from pathlib import Path

from rsi_anything import sdk

html = Path("index.html").read_text(encoding="utf-8") if Path("index.html").is_file() else ""
text = sdk.visible_text(html)
facts = json.loads(Path("judge/facts.json").read_text(encoding="utf-8"))
missing = [fact for fact in facts if fact not in text]
images = re.findall(r"<img\b[^>]*>", html, re.I)
gates = {
    # Screenshots are taken offline: every image, font, style and script on the page must be inlined.
    "self_contained": not re.search(r"<(?:script|img|iframe|source|video|audio)\b[^>]*\bsrc\s*=\s*[\"']?(?:https?:)?//"
                                    r"|<link\b[^>]*\bhref\s*=\s*[\"']?(?:https?:)?//|url\(\s*[\"']?(?:https?:)?//|@import",
                                    html, re.I),
    "facts_present": not missing,
    "no_placeholder": not re.search(r"lorem ipsum|placeholder text|\bTODO\b", text, re.I),
    "has_title_and_viewport": bool(re.search(r"<title>\s*\S", html, re.I))
                              and bool(re.search(r"name\s*=\s*[\"']?viewport", html, re.I)),
    "images_have_alt": all(re.search(r"\balt\s*=\s*[\"'][^\"']+", tag, re.I) for tag in images),
    "under_100kb": len(html.encode("utf-8")) <= 100_000,
}
notes = (f"missing facts: {', '.join(missing)}\n" if missing else "") + f"index.html: {len(html.encode('utf-8'))} bytes"
if sdk.write_gates(gates, notes):
    Path("out/page.txt").write_text(text + "\n", encoding="utf-8")
    sdk.screenshot(Path("index.html"), Path("out/desktop.png"), 1280, 1600)
    sdk.screenshot(Path("index.html"), Path("out/mobile.png"), 390, 1400)
