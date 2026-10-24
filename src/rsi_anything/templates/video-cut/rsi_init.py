"""Build the raw talk video and its sentence timeline. `rsi init` runs this once, before the first commit.

Default: synthesize judge/talk.txt with the system's text-to-speech (macOS `say`, Linux `espeak-ng`), one
sentence per line, over simple title cards. Nothing copyrighted is shipped; the video is made on your machine.

Bring your own video instead: put it at input.mp4 and install faster-whisper (`pip install faster-whisper`);
the script then transcribes it and uses the speech segments as sentences.

Outputs: assets/raw.mp4 (not committed), judge/transcript.json (frozen sentence timeline), edit.json
(starting cut: simply the first minute).
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = ["/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc",
         "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc"]
GAP = 0.3  # seconds of silence between sentences


def run(*args: str):
    subprocess.run(args, check=True, capture_output=True)


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def speak(text: str, out: Path):
    if platform.system() == "Darwin" and shutil.which("say"):
        voice = "Tingting" if any("一" <= ch <= "鿿" for ch in text) else "Samantha"
        run("say", "-v", voice, "-o", str(out.with_suffix(".aiff")), text)
        run("ffmpeg", "-y", "-v", "error", "-i", str(out.with_suffix(".aiff")), "-ar", "44100", "-ac", "1", str(out))
    elif shutil.which("espeak-ng"):
        run("espeak-ng", "-v", "cmn" if any("一" <= ch <= "鿿" for ch in text) else "en", "-w", str(out), text)
    else:
        sys.exit("need macOS `say` or `espeak-ng` to synthesize the demo talk (or provide input.mp4)")


def synthesize(lines: list[str], raw: Path) -> list[dict]:
    font = next((f for f in FONTS if Path(f).exists()), None)
    timeline, clips, cursor = [], [], 0.0
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for index, text in enumerate(lines, start=1):
            audio = tmp_dir / f"{index:03d}.wav"
            speak(text, audio)
            length = duration(audio) + GAP
            card = f"color=c=0x1d2433:s=720x1280:d={length:.3f}"
            draw = []
            if font:
                caption = text if len(text) <= 16 else "\n".join(text[i:i + 14] for i in range(0, len(text), 14))
                (tmp_dir / f"{index:03d}.txt").write_text(caption, encoding="utf-8")
                draw = ["-vf", f"drawtext=fontfile='{font}':textfile='{tmp_dir / f'{index:03d}.txt'}':fontcolor=white:"
                               f"fontsize=44:line_spacing=18:x=(w-text_w)/2:y=(h-text_h)/2"]
            clip = tmp_dir / f"{index:03d}.mp4"
            run("ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", card, "-i", str(audio), *draw,
                "-af", f"apad=pad_dur={GAP}", "-t", f"{length:.3f}", "-c:v", "libx264", "-preset", "veryfast",
                "-pix_fmt", "yuv420p", "-r", "25", "-c:a", "aac", "-ar", "44100", "-ac", "1", str(clip))
            real = duration(clip)
            timeline.append({"id": index, "start": round(cursor, 3), "end": round(cursor + real, 3), "text": text})
            cursor += real
            clips.append(clip)
        listing = tmp_dir / "list.txt"
        listing.write_text("".join(f"file '{c}'\n" for c in clips), encoding="utf-8")
        raw.parent.mkdir(parents=True, exist_ok=True)
        run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(raw))
    return timeline


def transcribe(source: Path, raw: Path) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("input.mp4 found: install faster-whisper to transcribe it (pip install faster-whisper)")
    raw.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, raw)
    model = WhisperModel("small", compute_type="int8")
    segments, _ = model.transcribe(str(source), vad_filter=True)
    return [{"id": i, "start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip()}
            for i, s in enumerate(segments, start=1) if s.text.strip()]


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is required (https://ffmpeg.org)")
    raw = HERE / "assets" / "raw.mp4"
    source = Path(os.environ.get("RSI_VIDEO_INPUT", str(HERE / "input.mp4"))).expanduser().resolve()
    supplied_timeline = os.environ.get("RSI_VIDEO_TRANSCRIPT")
    if source.exists():
        if supplied_timeline:
            timeline = json.loads(Path(supplied_timeline).read_text(encoding="utf-8"))
            limit = duration(source)
            if not timeline or any(not (0 <= float(s["start"]) < float(s["end"]) <= limit + 0.1)
                                   or not str(s.get("text", "")).strip() for s in timeline):
                sys.exit("提供的句子时间线为空或超出视频时长")
            if len({s["id"] for s in timeline}) != len(timeline):
                sys.exit("句子编号不能重复")
            raw.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, raw)
        else:
            timeline = transcribe(source, raw)
        (HERE / "judge" / "talk.txt").write_text("\n".join(s["text"] for s in timeline) + "\n", encoding="utf-8")
        # 自备素材使用对应的目标说明，避免继承默认学习话题。
        if os.environ.get("RSI_VIDEO_BRIEF"):
            (HERE / "judge" / "keypoints.md").write_text(Path(os.environ["RSI_VIDEO_BRIEF"]).read_text(), encoding="utf-8")
        else:
            (HERE / "judge" / "keypoints.md").write_text(
                "# 剪辑目标\n\n从给定原始讲稿中选取主题明确、衔接自然的片段，保持原意和语境。\n", encoding="utf-8")
        import yaml
        cfg = yaml.safe_load((HERE / "rsi.yaml").read_text())
        cfg["goal"] = ("从 judge/transcript.json 对应的真实口播中选出40到75秒的短片，只修改edit.json。"
                       "按judge/keypoints.md给出的目标选句和安排顺序，保留原意，不拼接出相反含义。")
        (HERE / "rsi.yaml").write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
        if os.environ.get("RSI_VIDEO_SOURCE_INFO"):
            shutil.copyfile(os.environ["RSI_VIDEO_SOURCE_INFO"], HERE / "judge" / "source.json")
    else:
        lines = [l.strip() for l in (HERE / "judge" / "talk.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
        timeline = synthesize(lines, raw)
    (HERE / "judge" / "transcript.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1) + "\n",
                                                    encoding="utf-8")
    first_minute, total = [], 0.0
    for item in timeline:
        if total + item["end"] - item["start"] > 60:
            break
        first_minute.append(item["id"])
        total += item["end"] - item["start"]
    (HERE / "edit.json").write_text(json.dumps({"segments": first_minute}, indent=1) + "\n", encoding="utf-8")
    print(f"talk: {len(timeline)} sentences, {timeline[-1]['end']:.0f}s; starting cut: first {total:.0f}s")


if __name__ == "__main__":
    main()
