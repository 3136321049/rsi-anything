#!/usr/bin/env python3
"""Make a short silent demo from real artifacts and data; reruns no experiments and regenerates no model content.

The on-screen card text and demo-video.json metadata are kept in Chinese on purpose: they must match the committed
examples/showcase-media/openrsi-demo.mp4 (its SHA256 is recorded). Translating them means re-rendering the video."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples" / "showcase-media"
FONTS = ["/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc",
         "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]


def run(args):
    subprocess.run(args, check=True, capture_output=True, timeout=180)


def main():
    if not shutil.which("ffmpeg"):
        raise SystemExit("FFmpeg is required")
    font = next((path for path in FONTS if Path(path).exists()), None)
    if not font:
        raise SystemExit("Noto Sans CJK or a system Chinese font is required")
    OUT.mkdir(parents=True, exist_ok=True)
    sources = []
    with tempfile.TemporaryDirectory(prefix="rsi-demo-video-") as temp:
        work = Path(temp)
        clips = []
        def text_filter(text, index, y=70, size=38, color="white"):
            file = work / f"text-{index}.txt"
            file.write_text(text, encoding="utf-8")
            return f"drawtext=fontfile='{font}':textfile='{file}':fontcolor={color}:fontsize={size}:line_spacing=24:x=60:y={y}"
        def card(text, duration=5):
            index = len(clips)
            clip = work / f"scene-{index:02d}.mp4"
            run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x153c33:s=1280x720:r=25:d={duration}",
                 "-vf", text_filter(text, index, 150, 42), "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                 "-pix_fmt", "yuv420p", str(clip)])
            clips.append(clip)
        card("Open RSI\n看见 AI 的多轮改进\n\n代码、写作、视频、训练与日程", 4)
        card("代码修复：逐类解决真实问题\n\n固定测试：6 / 15、9 / 15、12 / 15、15 / 15\n三轮改动全部保留，源码与测试结果可查看", 5)
        sources.append("code-repair/runs/20261023-234857-expense-code-repair/ledger.jsonl")
        card("写作手册：改进可复用的方法\n\n三个简报评分：62 分至 74.5 分\n用于新简报：69 分至 77.5 分\n每轮都保存手册、稿件和反馈", 6)
        sources.append("writing-guide/runs/20261024-001816-reusable-writing-guide/ledger.jsonl")
        video_run = ROOT / "examples/video-cut/runs/20261024-002228-talk-highlight"
        before = video_run / "artifacts/baseline/files/out/cut.mp4"
        after = video_run / "artifacts/final/files/out/cut.mp4"
        index = len(clips)
        clip = work / f"scene-{index:02d}.mp4"
        graph = ("[0:v]scale=640:620:force_original_aspect_ratio=decrease,pad=640:620:(ow-iw)/2:(oh-ih)/2[a];"
                 "[1:v]scale=640:620:force_original_aspect_ratio=decrease,pad=640:620:(ow-iw)/2:(oh-ih)/2[b];"
                 "[a][b]hstack,pad=1280:720:0:100:color=0x153c33," +
                 text_filter("真实口播选段：初剪                         最终保留版本", index, 28, 31) + "[v]")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(before), "-i", str(after), "-filter_complex", graph,
             "-map", "[v]", "-an", "-t", "8", "-r", "25", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
             "-pix_fmt", "yuv420p", str(clip)])
        clips.append(clip)
        sources += [str(before.relative_to(ROOT / "examples")), str(after.relative_to(ROOT / "examples"))]
        picture = ROOT / "examples/cpu-classifier/runs/20261024-001122-cpu-digits-classifier/artifacts/final/files/out/mistakes.png"
        index = len(clips)
        clip = work / f"scene-{index:02d}.mp4"
        vf = ("scale=1160:520:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:160:color=white," +
              text_filter("CPU 分类：错分由 239 张降至 3 张", index, 55, 36, "0x153c33"))
        run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(picture), "-vf", vf, "-t", "6", "-r", "25",
             "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p", str(clip)])
        clips.append(clip)
        sources.append(str(picture.relative_to(ROOT / "examples")))
        card("结果可查看，也能重新运行\n\n保留初稿、中间稿、拒绝稿和最终作品\n模型分数说明本次评价，资源缺口明确列出\n打开 examples/index.html 浏览全部案例", 6)
        listing = work / "concat.txt"
        listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips))
        target = OUT / "openrsi-demo.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(target)])
    probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,width,height",
                                       "-of", "json", str(target)], check=True, capture_output=True, text=True).stdout)
    run(["ffmpeg", "-v", "error", "-i", str(target), "-f", "null", "-"])
    (OUT / "demo-video.json").write_text(json.dumps({"title": "Open RSI 多轮作品演示", "silent": True,
        "source_kind": "已有真实实验与产物的展示剪辑，不是新的优化实验", "sources": sources,
        "source_note": "历史演讲片段来源与公共领域标记见 video-cut/inputs/public-speech/source.json。模型分数不代表真实业务收益。",
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "probe": probe, "decode_ok": True}, ensure_ascii=False, indent=2) + "\n")
    print("Demo video built and decode-checked:", target.relative_to(ROOT))


if __name__ == "__main__":
    main()
