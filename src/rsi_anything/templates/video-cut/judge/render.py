"""Render edit.json into out/cut.mp4 and out/cut.txt, and check the hard gates.

edit.json: {"segments": [3, 15, 16, ...]} (sentence ids from judge/transcript.json, in playback order).
Gates: the edit is valid, the cut lasts 40-75 s, and it uses 4-14 sentences.
Set RSI_RENDER=0 to skip writing the video (text and gates only).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

MIN_SECONDS, MAX_SECONDS = 40, 75
MIN_SEGMENTS, MAX_SEGMENTS = 4, 14

out = Path("out")
out.mkdir(exist_ok=True)
timeline = {item["id"]: item for item in json.loads(Path("judge/transcript.json").read_text(encoding="utf-8"))}


def finish(gates, notes, text=""):
    (out / "gates.json").write_text(json.dumps(gates), encoding="utf-8")
    (out / "notes.txt").write_text(notes, encoding="utf-8")
    (out / "cut.txt").write_text(text or "(empty cut)", encoding="utf-8")
    sys.exit(0)


try:
    edit = json.loads(Path("edit.json").read_text(encoding="utf-8"))
    ids = [int(x["id"] if isinstance(x, dict) else x) for x in edit["segments"]]
except Exception as exc:  # malformed edit: fail the gate, keep the judge running
    finish({"valid_edit": False}, f"edit.json is not valid: {exc}")

unknown = [i for i in ids if i not in timeline]
duplicates = sorted({i for i in ids if ids.count(i) > 1})
if unknown or duplicates or not ids:
    finish({"valid_edit": False}, f"edit.json problems: unknown ids {unknown}, repeated ids {duplicates}")

seconds = sum(timeline[i]["end"] - timeline[i]["start"] for i in ids)
text = "\n".join(timeline[i]["text"] for i in ids)
gates = {
    "valid_edit": True,
    f"duration_{MIN_SECONDS}_{MAX_SECONDS}s": MIN_SECONDS <= seconds <= MAX_SECONDS,
    f"segments_{MIN_SEGMENTS}_{MAX_SEGMENTS}": MIN_SEGMENTS <= len(ids) <= MAX_SEGMENTS,
}
notes = f"cut: {len(ids)} sentences, {seconds:.1f}s (allowed {MIN_SECONDS}-{MAX_SECONDS}s); order {ids}"

raw = Path("assets/raw.mp4")
if os.environ.get("RSI_RENDER", "1") != "0" and raw.exists():
    parts, labels = [], []
    for n, i in enumerate(ids):
        start, end = timeline[i]["start"], timeline[i]["end"]
        parts.append(f"[0:v]trim={start}:{end},setpts=PTS-STARTPTS,scale=360:640[v{n}];"
                     f"[0:a]atrim={start}:{end},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,"
                     f"afade=t=out:st={max(0.0, end - start - 0.03):.3f}:d=0.03[a{n}];")
        labels.append(f"[v{n}][a{n}]")
    graph = "".join(parts) + "".join(labels) + f"concat=n={len(ids)}:v=1:a=1[v][a]"
    render = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-filter_complex", graph, "-map", "[v]",
                             "-map", "[a]", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30", "-c:a", "aac",
                             str(out / "cut.mp4")], capture_output=True, text=True)
    gates["rendered"] = render.returncode == 0
    if render.returncode != 0:
        notes += f"\nrender failed: {render.stderr[-300:]}"

finish(gates, notes, text)
