"""Check that drawing.svg is a clean, self-contained vector drawing, then render it for the visual jury."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from rsi_anything import sdk

WIDTH, HEIGHT = 1024, 768
SHAPES = {"path", "circle", "ellipse", "rect", "line", "polyline", "polygon"}

source = Path("drawing.svg")
text = source.read_text(encoding="utf-8") if source.is_file() else ""
try:
    root = ET.fromstring(text)
except ET.ParseError:
    root = None
tags = [element.tag.split("}")[-1] for element in root.iter()] if root is not None else []
shapes = sum(tag in SHAPES for tag in tags)
gates = {
    "valid_svg": root is not None and tags[:1] == ["svg"],
    "has_viewbox": root is not None and bool(root.get("viewBox")),
    # 只能用矢量图形画：不能嵌入位图、外部资源、脚本或 HTML。
    "vector_only": not any(tag in {"image", "foreignObject", "script", "iframe"} for tag in tags)
                   and not re.search(r"(?:href|src)\s*=\s*[\"'](?:https?:|data:)|url\(\s*[\"']?(?:https?:|data:)", text, re.I),
    # 写上 “PELICAN” 之类的字会讨好评委，不算画得像。
    "no_text": not any(tag in {"text", "textPath", "tspan"} for tag in tags),
    "under_60kb": len(text.encode("utf-8")) <= 60_000,
    "has_shapes": shapes >= 3,
}
notes = f"drawing.svg: {shapes} shapes, {len(text.encode('utf-8'))} bytes"
if sdk.write_gates(gates, notes):
    page = Path("out/render.html")
    page.write_text('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#fff}'
                    f'svg{{display:block;width:{WIDTH}px;height:{HEIGHT}px}}</style>' + text, encoding="utf-8")
    sdk.screenshot(page, Path("out/drawing.png"), WIDTH, HEIGHT)
