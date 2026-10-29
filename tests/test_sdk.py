"""评分工具包：门槛与说明、“结果未知”、页面文字与渲染失败时的处理。"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from rsi_anything import sdk
from rsi_anything.contract import JudgeSpec
from rsi_anything.judges.base import Judge


def test_gates_and_notes_reach_the_verdict(tmp_path):
    (tmp_path / "judge.py").write_text("from rsi_anything import sdk\n"
                                       "sdk.write_gates({'renders': True, 'small': False}, notes='too big: 80 KB')\n")
    spec = JudgeSpec(type="command", run="x", prepare=f"{sys.executable} judge.py")
    verdict = Judge(spec).evaluate(tmp_path, 1)  # a failed gate stops before scoring
    assert verdict.gates == {"renders": True, "small": False} and verdict.feedback == "too big: 80 KB"


def test_unavailable_is_unknown_not_zero(tmp_path):
    (tmp_path / "judge.py").write_text("from rsi_anything import sdk\nsdk.unavailable('service down', 'render')\n")
    spec = JudgeSpec(type="command", run="x", prepare=f"{sys.executable} judge.py")
    verdict = Judge(spec).evaluate(tmp_path, 1)
    assert verdict.score is None and verdict.metrics["quality_result"] == "unknown"
    assert json.loads((tmp_path / "out/error.json").read_text())["stage"] == "render"


def test_visible_text_skips_head_scripts_and_styles():
    html = ("<html><head><title>T</title><style>p{}</style></head><body><h1>Night</h1><script>x=1</script>"
            "<p>¥129 <b>trial</b></p><img src=a.png alt='desk lamp'></body></html>")
    assert sdk.visible_text(html) == "Night\n¥129 trial [image: desk lamp]"


def test_missing_browser_is_reported_as_unavailable(tmp_path):
    (tmp_path / "page.html").write_text("<p>hi</p>")
    env = {**os.environ, "RSI_BROWSER": str(tmp_path / "no-such-browser")}
    run = subprocess.run([sys.executable, "-c", "from pathlib import Path\nfrom rsi_anything import sdk\n"
                          "sdk.screenshot(Path('page.html'), Path('out/page.png'), 800, 600)"],
                         cwd=tmp_path, env=env, capture_output=True, text=True)
    assert run.returncode == 3, run.stderr
    assert json.loads((tmp_path / "out/error.json").read_text())["quality_result"] == "unknown"


def _png_rows(path: Path) -> list[bytes]:
    """Decode an 8-bit RGB PNG (what Chrome writes) into raw rows, enough to look at pixels."""
    import struct
    import zlib
    data, pos, chunks = path.read_bytes(), 8, b""
    width, height = struct.unpack(">II", data[16:24])
    while pos < len(data):
        size, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if kind == b"IDAT":
            chunks += data[pos + 8:pos + 8 + size]
        pos += 12 + size
    raw, stride, rows, prev = zlib.decompress(chunks), width * 3, [], bytes(width * 3)
    for y in range(height):
        kind, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a, b = line[x - 3] if x >= 3 else 0, prev[x]
            c = prev[x - 3] if x >= 3 else 0
            p = a + b - c
            pred = {0: 0, 1: a, 2: b, 3: (a + b) // 2,
                    4: a if abs(p - a) <= abs(p - b) and abs(p - a) <= abs(p - c) else b if abs(p - b) <= abs(p - c) else c}[kind]
            line[x] = (line[x] + pred) & 0xFF
        rows.append(bytes(line))
        prev = line
    return rows


@pytest.mark.skipif(sdk.find_browser() is None, reason="no Chrome-family browser on this machine")
def test_phone_width_is_laid_out_and_painted_in_full(tmp_path):
    page = tmp_path / "w.html"
    # 页面全黑、比截图更高：手机宽度下应整张都是黑的，底部不能出现未绘制的白色。
    page.write_text("<!doctype html><meta name=viewport content='width=device-width'><style>html,body{margin:0;"
                    "background:#000}div{height:3000px}@media (min-width:401px){html,body{background:#f00}}</style><div></div>")
    png = sdk.screenshot(page, tmp_path / "w.png", 390, 1400)
    rows = _png_rows(png)
    assert (len(rows[0]) // 3, len(rows)) == (500, 1795)  # 390 css px zoomed to the 500px minimum window
    for y in (10, 900, 1700, 1794):
        assert set(rows[y]) == {0}, f"row {y} is not black: the phone layout or its painting is wrong"
