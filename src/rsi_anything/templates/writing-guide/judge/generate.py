"""A fixed writer model drafts a post for each brief from the current guide; every round makes real model calls."""
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
        prompt = ("Following the writing guide below, write a Xiaohongshu (RedNote) post for the product brief. The brief is the only "
                  "source of facts. Output only the title and the body: no explanations, no tool calls.\n\n"
                  + "## Guide\n" + guide + "\n\n## Brief\n" + json.dumps(brief, ensure_ascii=False))
        try:
            reply = ask(model, prompt, timeout=600)
            text = reply.text.strip()
            if not text:
                raise llm.LLMError("the writer returned an empty draft")
        except llm.LLMError as exc:
            errors.append({"id": brief["id"], "error": str(exc)})
            continue
        (out / f"{brief['id']}.md").write_text(text + "\n")
        facts = "; ".join(brief["facts"])
        posts.append(f"# Brief {brief['id']}\n\nProduct: {brief['name']}\n\nTarget reader: {brief['reader']}\n\nGiven facts: {facts}"
                     f"\n\nGiven call to action: {brief['action']}\n\n## Generated draft\n\n{text}")
        records.append({"id": brief["id"], "requested_model": model.raw, "actual_model": reply.model or None,
                        "usage": reply.usage, "seconds": reply.seconds, "file": f"{brief['id']}.md"})
    combined = "\n\n---\n\n".join(posts)
    (out / "posts.md").write_text(combined + "\n")
    (out / "posts.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Posts written from the guide</title>'
        '<style>body{max-width:850px;margin:40px auto;padding:20px;font:17px/1.8 system-ui}pre{white-space:pre-wrap}</style>'
        '<h1>Posts written from the guide</h1><pre>' + html.escape(combined) + '</pre></html>')
    (out / "generation.json").write_text(json.dumps({"split": split, "synthetic_briefs": True, "calls": records,
                                                      "errors": errors}, ensure_ascii=False, indent=2) + "\n")
    (out / "gates.json").write_text(json.dumps({"all_briefs_generated": len(records) == len(briefs),
                                               "guide_present": len(guide.strip()) >= 30}))
    (out / "notes.txt").write_text(f"{split}: fixed writer {model.raw} drafted posts for {len(records)}/{len(briefs)} briefs.")
    return records


if __name__ == "__main__":
    generate(Path.cwd(), sys.argv[1] if len(sys.argv) > 1 else "development")
