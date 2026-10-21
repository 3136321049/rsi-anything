"""Label every example with the prompt under test and report accuracy.

The task model comes from $RSI_TASK_MODEL (any rsi model reference, e.g. deepseek:deepseek-chat or
cli:codex); by default the first model `rsi agents` can reach. API models label one message per call,
in parallel. Coding-agent CLIs are slow to start, so they label a batch of messages per call
($RSI_TASK_BATCH, default 20) and return a JSON list.
"""
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from rsi_anything import llm, report_result

LABELS = ["refund", "late_delivery", "wrong_item", "cancel_order", "account", "payment", "praise", "other"]

examples = [json.loads(line) for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if line.strip()]
prompt = Path("prompt.md").read_text(encoding="utf-8") if Path("prompt.md").exists() else ""
if len(prompt.strip()) < 10:
    report_result(0, {"prompt_present": False}, "prompt.md is empty")
    sys.exit(0)
model = llm.parse(os.environ.get("RSI_TASK_MODEL") or llm.resolve_models(["auto"])[0])


def parse_label(reply):
    found = [name for name in LABELS if re.search(rf"\b{name}\b", reply.lower())]
    return found[-1] if found else "unparseable"


def label(example):
    question = (f"{prompt}\n\n---\nCustomer message:\n{example['text']}\n---\n"
                f"Reply with exactly one of: {', '.join(LABELS)}.")
    try:
        reply = llm.ask(model, question, timeout=300).text
    except llm.LLMError as exc:
        return None, str(exc)
    return parse_label(reply), reply[:80]


def label_batch(batch):
    listing = "\n".join(f"{i + 1}. {json.dumps(e['text'], ensure_ascii=False)}" for i, e in enumerate(batch))
    question = (f"{prompt}\n\n---\nApply the instructions above to each customer message below, independently.\n"
                f"{listing}\n---\nReply with a JSON object {{\"labels\": [...]}} holding exactly {len(batch)} "
                f"labels in the same order, each one of: {', '.join(LABELS)}.")
    try:
        labels = llm.extract_json(llm.ask(model, question, timeout=900).text).get("labels") or []
    except llm.LLMError as exc:
        return [(None, str(exc))] * len(batch)
    if len(labels) != len(batch):
        return [(None, f"expected {len(batch)} labels, got {len(labels)}")] * len(batch)
    return [(parse_label(str(item)), str(item)) for item in labels]


batch_size = int(os.environ.get("RSI_TASK_BATCH", "20" if model.kind == "cli" else "1"))
workers = int(os.environ.get("RSI_TASK_WORKERS", "6"))
with ThreadPoolExecutor(max_workers=workers) as pool:
    if batch_size <= 1:
        results = list(pool.map(label, examples))
    else:
        batches = [examples[i:i + batch_size] for i in range(0, len(examples), batch_size)]
        results = [item for chunk in pool.map(label_batch, batches) for item in chunk]

errors = [detail for got, detail in results if got is None]
if len(errors) > len(examples) // 4:
    print("too many model errors: " + errors[0], file=sys.stderr)
    sys.exit(2)
mistakes, correct = [], 0
for example, (got, _) in zip(examples, results):
    if got == example["label"]:
        correct += 1
    else:
        mistakes.append(f"expected {example['label']}, got {got}: {example['text'][:70]}")
accuracy = 100 * correct / len(examples)
confusions = {}
for line in mistakes:
    pair = line.split(":")[0]
    confusions[pair] = confusions.get(pair, 0) + 1
worst = sorted(confusions.items(), key=lambda kv: -kv[1])[:4]
report_result(round(accuracy, 1), {"prompt_present": True},
              f"{correct}/{len(examples)} correct with {model.raw}. Most common mistakes: "
              + "; ".join(f"{k} (x{v})" for k, v in worst)
              + ("\nExamples:\n" + "\n".join(mistakes[:6]) if mistakes else ""),
              {"model": model.raw, "errors": len(errors)})
