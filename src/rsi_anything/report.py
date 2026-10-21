"""Turn a run's ledger into something worth sharing: a terminal table, Markdown, and one HTML file."""
from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from . import gitops
from .ledger import KEEP, RunStore

STATUS_MARK = {"BASELINE": "◆", "KEEP": "▲", "REVERT": "·", "NO_CHANGE": "○", "AGENT_FAIL": "✕", "JUDGE_FAIL": "✕"}


def _fmt(value) -> str:
    return "-" if value is None else f"{value:g}"


def terminal(store: RunStore) -> str:
    rows = store.rows()
    if not rows:
        return "no rounds yet"
    scores = [r["score"] for r in rows if r.get("score") is not None]
    low, high = (min(scores), max(scores)) if scores else (0, 1)
    span = (high - low) or 1
    lines = [f"run {store.run_id}", "round  status      score    best     chart"]
    for r in rows:
        bar = ""
        if r.get("score") is not None:
            filled = 1 + round(24 * (r["score"] - low) / span)
            bar = ("█" if r["status"] in ("KEEP", "BASELINE") else "░") * filled
        lines.append(f"{r['round']:>5}  {r['status']:<10}  {_fmt(r.get('score')):>7}  {_fmt(r.get('best')):>7}  {bar}")
    kept = sum(1 for r in rows if r["status"] == KEEP)
    lines.append(f"{len(rows) - 1} rounds, {kept} kept, best {_fmt(rows[-1].get('best'))} (baseline {_fmt(rows[0].get('score'))})")
    return "\n".join(lines)


def markdown(store: RunStore) -> str:
    meta, rows = store.meta(), store.rows()
    out = [f"# RSI run `{store.run_id}`", "", f"**Goal:** {meta.get('goal', '').strip()}", "",
           f"Agent `{meta.get('agent')}` · judge `{meta.get('judge')}`"
           + (f" · jury {', '.join(meta['jury'])}" if meta.get("jury") else "")
           + f" · branch `{meta.get('branch')}`", "",
           "| round | status | score | best | change | why |", "|---:|---|---:|---:|---|---|"]
    for r in rows:
        change = (r.get("hypothesis") or ("baseline" if r["round"] == 0 else "")).replace("|", "\\|")
        why = (r.get("note") or "").replace("|", "\\|")
        out.append(f"| {r['round']} | {r['status']} | {_fmt(r.get('score'))} | {_fmt(r.get('best'))} | {change[:160]} | {why[:160]} |")
    if meta.get("stop_reason"):
        out += ["", f"Stopped: {meta['stop_reason']}."]
    holdout = meta.get("holdout") or {}
    if holdout:
        out += ["", f"Hold-out judge (never shown to the agent): {_fmt(holdout.get('baseline'))} → {_fmt(holdout.get('final'))}"]
    return "\n".join(out) + "\n"


def _chart(rows: list[dict[str, Any]], width: int = 720, height: int = 260) -> str:
    points = [(r["round"], r["score"], r["status"]) for r in rows if r.get("score") is not None]
    if not points:
        return ""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1 = min(xs), max(max(xs), 1)
    y0, y1 = min(ys), max(ys)
    pad = (y1 - y0) * 0.1 or 1
    y0, y1 = y0 - pad, y1 + pad
    left, right, top, bottom = 48, 16, 16, 32

    def sx(x):
        return left + (x - x0) / ((x1 - x0) or 1) * (width - left - right)

    def sy(y):
        return top + (1 - (y - y0) / (y1 - y0)) * (height - top - bottom)

    best_path, best = [], None
    for r in rows:
        if r["status"] in ("BASELINE", "KEEP") and r.get("score") is not None:
            best = r["score"]
        if best is not None:
            best_path.append(f"{sx(r['round']):.1f},{sy(best):.1f}")
    marks = []
    for x, y, status in points:
        kept = status in ("BASELINE", "KEEP")
        marks.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="{5 if kept else 3.5}" '
                     f'class="{"kept" if kept else "dropped"}"><title>r{x} {status} {y:g}</title></circle>')
    ticks = "".join(f'<text x="{left - 8}" y="{sy(v):.1f}" class="tick" text-anchor="end">{v:.3g}</text>'
                    for v in (y0 + pad, (y0 + y1) / 2, y1 - pad))
    xt = "".join(f'<text x="{sx(x):.1f}" y="{height - 10}" class="tick" text-anchor="middle">r{x}</text>' for x in xs)
    return (f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="score by round">'
            f'<polyline points="{" ".join(best_path)}" class="best"/>{"".join(marks)}{ticks}{xt}</svg>')


def html_page(store: RunStore, repo: Path) -> str:
    meta, rows = store.meta(), store.rows()
    esc = html.escape
    diff = ""
    if meta.get("champion") and meta.get("base") and meta["champion"] != meta["base"]:
        try:
            diff = gitops.diff_stat(repo, meta["base"], meta["champion"])
        except gitops.GitError:
            diff = ""
    body_rows = []
    for r in rows:
        body_rows.append(
            f"<tr class='s-{r['status'].lower()}'><td>{r['round']}</td><td>{STATUS_MARK.get(r['status'], '')} {r['status']}</td>"
            f"<td>{_fmt(r.get('score'))}</td><td>{_fmt(r.get('best'))}</td>"
            f"<td>{esc(r.get('hypothesis') or ('baseline' if r['round'] == 0 else ''))}</td>"
            f"<td>{esc(r.get('note') or '')}</td></tr>")
    first, last = rows[0] if rows else {}, rows[-1] if rows else {}
    holdout = meta.get("holdout") or {}
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>RSI run {esc(store.run_id)}</title>
<style>
:root {{ --bg:#fbfaf7; --fg:#1d1d1b; --muted:#6b6a64; --line:#e4e1d8; --accent:#2f6fde; --keep:#1f9d55; --drop:#b7b3a6; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#161614; --fg:#ecebe6; --muted:#a3a198; --line:#2c2b27; --accent:#7aa7ff; --keep:#4cc38a; --drop:#5b5950; }} }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; margin:0; }}
main {{ max-width:960px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ font-size:22px; margin:0 0 4px; }} .muted {{ color:var(--muted); }}
.stats {{ display:flex; gap:24px; flex-wrap:wrap; margin:20px 0; }} .stat b {{ display:block; font-size:26px; }}
svg {{ width:100%; height:auto; border:1px solid var(--line); border-radius:8px; }}
.best {{ fill:none; stroke:var(--accent); stroke-width:2; }} .kept {{ fill:var(--keep); }} .dropped {{ fill:var(--drop); }}
.tick {{ fill:var(--muted); font-size:11px; }}
table {{ width:100%; border-collapse:collapse; margin-top:20px; font-size:14px; }}
td,th {{ border-bottom:1px solid var(--line); padding:6px 8px; text-align:left; vertical-align:top; }}
tr.s-keep td:nth-child(2) {{ color:var(--keep); font-weight:600; }}
pre {{ overflow-x:auto; background:color-mix(in srgb, var(--line) 40%, transparent); padding:12px; border-radius:8px; }}
</style></head><body><main>
<h1>{esc(meta.get('contract', 'RSI run'))}</h1>
<div class="muted">{esc(meta.get('goal', ''))}</div>
<div class="stats">
<div class="stat"><span class="muted">baseline</span><b>{_fmt(first.get('score'))}</b></div>
<div class="stat"><span class="muted">best</span><b>{_fmt(last.get('best'))}</b></div>
<div class="stat"><span class="muted">rounds / kept</span><b>{max(len(rows) - 1, 0)} / {sum(1 for r in rows if r['status'] == KEEP)}</b></div>
<div class="stat"><span class="muted">agent</span><b style="font-size:16px">{esc(str(meta.get('agent', '')))}</b></div>
</div>
{_chart(rows)}
<p class="muted">Line: best score so far. Green: kept. Grey: judged and thrown away.
{'Hold-out judge (never shown to the agent): ' + _fmt(holdout.get('baseline')) + ' → ' + _fmt(holdout.get('final')) + '.' if holdout else ''}
{('Stopped: ' + esc(meta['stop_reason']) + '.') if meta.get('stop_reason') else ''}</p>
<table><thead><tr><th>round</th><th>status</th><th>score</th><th>best</th><th>change</th><th>why</th></tr></thead>
<tbody>{''.join(body_rows)}</tbody></table>
{('<h2>Champion vs. start</h2><pre>' + esc(diff) + '</pre>') if diff else ''}
<p class="muted">Branch <code>{esc(str(meta.get('branch', '')))}</code>. Generated by RSI-Anything.</p>
</main></body></html>
"""


def write(store: RunStore, repo: Path) -> tuple[Path, Path]:
    md = store.dir / "report.md"
    page = store.dir / "report.html"
    md.write_text(markdown(store), encoding="utf-8")
    page.write_text(html_page(store, repo), encoding="utf-8")
    return md, page
