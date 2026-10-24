"""固定写手根据当前手册和简报生成作品，每轮都真实调用模型。"""
import html
import json
import os
import sys
from pathlib import Path

from rsi_anything import llm


def generate(root, split, ask=llm.ask):
    root = Path(root)
    briefs = json.loads((root / ("holdout/briefs.json" if split == "holdout" else "judge/briefs.json")).read_text())
    guide = (root / "writing-guide.md").read_text()
    model = llm.parse(os.environ.get("RSI_WRITER_MODEL") or os.environ.get("RSI_TASK_MODEL") or llm.resolve_models(["auto"])[0])
    out = root / "out"
    out.mkdir(exist_ok=True)
    posts, records, errors = [], [], []
    for brief in briefs:
        prompt = ("根据下列写作手册为产品简报写一篇小红书笔记。所有事实以简报为准。直接输出标题和正文，不解释，不调用工具。\n\n"
                  + "## 手册\n" + guide + "\n\n## 简报\n" + json.dumps(brief, ensure_ascii=False))
        try:
            reply = ask(model, prompt, timeout=600)
            text = reply.text.strip()
            if not text:
                raise llm.LLMError("写手返回空稿")
        except llm.LLMError as exc:
            errors.append({"id": brief["id"], "error": str(exc)})
            continue
        (out / f"{brief['id']}.md").write_text(text + "\n")
        facts = "；".join(brief["facts"])
        posts.append(f"# 简报 {brief['id']}\n\n目标读者：{brief['reader']}\n\n给定事实：{facts}\n\n## 生成稿\n\n{text}")
        records.append({"id": brief["id"], "requested_model": model.raw, "actual_model": reply.model or None,
                        "usage": reply.usage, "seconds": reply.seconds, "file": f"{brief['id']}.md"})
    combined = "\n\n---\n\n".join(posts)
    (out / "posts.md").write_text(combined + "\n")
    (out / "posts.html").write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>手册生成的文案</title>'
        '<style>body{max-width:850px;margin:40px auto;padding:20px;font:17px/1.8 system-ui}pre{white-space:pre-wrap}</style>'
        '<h1>手册生成的文案</h1><pre>' + html.escape(combined) + '</pre></html>')
    (out / "generation.json").write_text(json.dumps({"split": split, "synthetic_briefs": True, "calls": records,
                                                      "errors": errors}, ensure_ascii=False, indent=2) + "\n")
    (out / "gates.json").write_text(json.dumps({"all_briefs_generated": len(records) == len(briefs),
                                               "guide_present": len(guide.strip()) >= 30}))
    (out / "notes.txt").write_text(f"{split}：固定写手 {model.raw} 已生成 {len(records)}/{len(briefs)} 份简报的文案。")
    return records


if __name__ == "__main__":
    generate(Path.cwd(), sys.argv[1] if len(sys.argv) > 1 else "development")
