"""`rsi new`: turn a few answers into a task that runs — contract, judge and a starting file.

Four kinds cover most first tasks:

    text     any text file; a model scores it against criteria you name
    visual   an SVG drawing or an HTML page; a model scores a screenshot
    tests    code with tests; the score is the share of tests that pass
    number   any command that prints a number (speed, accuracy, size...)

Everything written is ordinary rsi.yaml and judge files, so the result can be edited
by hand afterwards exactly like a template.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .contract import CONTRACT_FILE, load

KINDS = {
    "text": "an article, prompt, README or any text file - a model judges it against your criteria",
    "visual": "an SVG drawing or an HTML page - a model judges a screenshot",
    "tests": "code that has tests - the score is the share of tests passing",
    "number": "any command that prints a number - speed, accuracy, size...",
}
DEFAULT_ARTIFACT = {"text": "draft.md", "visual": "drawing.svg"}
DEFAULT_CRITERIA = {"text": ["goal fit", "clarity", "craft"], "visual": ["subject", "composition", "craft"]}
VISUAL_SUFFIXES = (".svg", ".html")


@dataclass
class Plan:
    kind: str
    artifact: list[str]
    goal: str
    name: str = "my-task"
    criteria: list[str] = field(default_factory=list)
    command: str = ""                                  # tests / number: what to run
    frozen: list[str] = field(default_factory=list)    # tests / number: files the agent must not change
    maximize: bool = True
    agent: str = "auto"
    jury: list[str] = field(default_factory=lambda: ["auto"])
    rounds: int = 5

    def problems(self) -> list[str]:
        found = []
        if self.kind not in KINDS:
            found.append(f"kind must be one of {', '.join(KINDS)}")
        if not self.artifact:
            found.append("name at least one file the agent may edit")
        if not self.goal.strip():
            found.append("describe what better means (the goal)")
        if self.kind == "visual" and (len(self.artifact) != 1 or not self.artifact[0].endswith(VISUAL_SUFFIXES)):
            found.append("a visual task edits exactly one .svg or .html file")
        if self.kind in ("tests", "number") and not self.command.strip():
            found.append(f"a {self.kind} task needs the command to run")
        if self.kind in ("text", "visual") and not 1 <= len(self.criteria) <= 6:
            found.append("name between one and six criteria")
        if self.rounds < 1:
            found.append("rounds must be at least 1")
        return found


def slug(text: str) -> str:
    """A criterion or task name: lowercase words joined by `_` or `-`; other scripts are kept as they are."""
    words = re.findall(r"\w+", text.strip().lower())
    return "_".join(words) or "criterion"


def _weights(count: int) -> list[int]:
    base = 100 // count
    return [base + (1 if i < 100 - base * count else 0) for i in range(count)]


def _yaml_list(items: list[str]) -> str:
    return "[" + ", ".join(_quote(item) for item in items) + "]"


def _quote(text: str) -> str:
    plain = re.fullmatch(r"[\w./:@+-]+", text) and not text[0] in "-:@" and text.lower() not in {"yes", "no", "true", "false", "null"}
    return text if plain else '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _note(line: str, comment: str) -> str:
    return f"{line:<36} # {comment}"


def _block(text: str, indent: int = 2) -> str:
    pad = " " * indent
    return "\n".join(pad + line if line.strip() else "" for line in text.strip().splitlines())


def rubric(plan: Plan) -> str:
    what = "rendered picture" if plan.kind == "visual" else "work"
    lines = ["# Written by `rsi new`. Rewrite the questions and anchors in your own words: the judge reads them literally.",
             "task: |", _block(plan.goal), "", "criteria:"]
    for name, weight in zip(plan.criteria, _weights(len(plan.criteria))):
        lines += [f"  - name: {_quote(slug(name))}",
                  f"    weight: {weight}",
                  f"    question: {_quote(f'How good is the {what} on {name.strip()}, measured against the task?')}",
                  "    anchors:",
                  '      1: "missing or broken"',
                  '      4: "present but weak"',
                  '      7: "solid, with a few clear problems"',
                  '      10: "excellent; hard to see how to improve it"']
    if plan.kind == "visual":
        lines += ["", "checks:", "  - The picture contains no placeholder text such as lorem ipsum or TODO."]
    return "\n".join(lines) + "\n"


def contract(plan: Plan) -> str:
    lines = [f"# Written by `rsi new`. Edit freely; `rsi check --stress` tells you whether the judge holds up.",
             f"name: {_quote(plan.name)}", "goal: |", _block(plan.goal), f"artifact: {_yaml_list(plan.artifact)}"]
    if plan.kind == "visual":
        lines.append("outputs: [out]")
    lines.append("judge:")
    if plan.kind in ("text", "visual"):
        lines.append("  type: rubric")
        if plan.kind == "visual":
            inputs = ["out/picture.png"] if plan.artifact[0].endswith(".svg") else ["out/desktop.png", "out/mobile.png", "out/page.txt"]
            lines += [_note('  prepare: "{python} judge/render.py"', "checks the file, then screenshots it with headless Chrome"),
                      f"  inputs: {_yaml_list(inputs)}"]
        lines += ["  rubric: judge/rubric.yaml",
                  "  files: [judge]",
                  _note(f"  models: {_yaml_list(plan.jury)}", "auto = models you already have; e.g. [cli:claude]"),
                  _note("  pairwise: true", "a higher score must also win a side-by-side look, in both orders"),
                  _note("  ties: compare", "an equal score is settled by the same side-by-side look"),
                  "  timeout: 600"]
    else:
        lines += ["  type: command",
                  '  run: "{python} judge/score.py"',
                  _note(f"  files: {_yaml_list(['judge', *plan.frozen])}", "the agent can never change these"),
                  "  timeout: 600"]
        if not plan.maximize:
            lines.append("  direction: minimize")
        if plan.kind == "number":
            lines.append(_note("  repeats: 1", "raise to 3 or 5 when the number is noisy (timings)"))
    lines += ["agent:", _note(f"  use: {_quote(plan.agent)}", "see `rsi agents`"), "  timeout: 600",
              "budget:", f"  rounds: {plan.rounds}", "  minutes: 60", "  stagnation: 3"]
    if plan.kind == "tests":
        lines.append("  target: 100")
    return "\n".join(lines) + "\n"


_RENDER_SVG = '''"""Check that {name} is a clean vector drawing, then render it for the judge. Written by `rsi new`."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from rsi_anything import sdk

SOURCE, WIDTH, HEIGHT = Path({name!r}), 1024, 768
text = SOURCE.read_text(encoding="utf-8") if SOURCE.is_file() else ""
try:
    root = ET.fromstring(text)
except ET.ParseError:
    root = None
tags = [element.tag.split("}}")[-1] for element in root.iter()] if root is not None else []
gates = {{
    "valid_svg": tags[:1] == ["svg"],
    "has_viewbox": root is not None and bool(root.get("viewBox")),
    # Rendering is offline: no embedded images, external files or scripts.
    "self_contained": not any(tag in {{"image", "foreignObject", "script"}} for tag in tags)
                      and not re.search(r"(?:href|src)\\s*=\\s*[\\"'](?:https?:|data:)", text, re.I),
    "under_200kb": len(text.encode("utf-8")) <= 200_000,
}}
if sdk.write_gates(gates, f"{{SOURCE}}: {{len(tags)}} elements, {{len(text.encode('utf-8'))}} bytes"):
    page = Path("out/render.html")
    page.write_text('<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;background:#fff}}'
                    f'svg{{{{display:block;width:{{WIDTH}}px;height:{{HEIGHT}}px}}}}</style>' + text, encoding="utf-8")
    sdk.screenshot(page, Path("out/picture.png"), WIDTH, HEIGHT)
'''

_RENDER_HTML = '''"""Check that {name} is a self-contained page, then screenshot it on desktop and phone. Written by `rsi new`."""
import re
from pathlib import Path

from rsi_anything import sdk

SOURCE = Path({name!r})
html = SOURCE.read_text(encoding="utf-8") if SOURCE.is_file() else ""
text = sdk.visible_text(html)
gates = {{
    # Screenshots are taken offline: images, fonts, styles and scripts must be inline.
    "self_contained": not re.search(r"<(?:script|img|iframe|source|video|audio)\\b[^>]*\\bsrc\\s*=\\s*[\\"']?(?:https?:)?//"
                                    r"|<link\\b[^>]*\\bhref\\s*=\\s*[\\"']?(?:https?:)?//|url\\(\\s*[\\"']?(?:https?:)?//|@import",
                                    html, re.I),
    "has_title_and_viewport": bool(re.search(r"<title>\\s*\\S", html, re.I))
                              and bool(re.search(r"name\\s*=\\s*[\\"']?viewport", html, re.I)),
    "no_placeholder": not re.search(r"lorem ipsum|\\bTODO\\b", text, re.I),
    "under_200kb": len(html.encode("utf-8")) <= 200_000,
}}
if sdk.write_gates(gates, f"{{SOURCE}}: {{len(html.encode('utf-8'))}} bytes"):
    Path("out/page.txt").write_text(text + "\\n", encoding="utf-8")
    sdk.screenshot(SOURCE, Path("out/desktop.png"), 1280, 1600)
    sdk.screenshot(SOURCE, Path("out/mobile.png"), 390, 1400)
'''

_SCORE_TESTS = '''"""Run the tests and score the share that pass. Written by `rsi new`; edit freely.

The test files are frozen (judge.files in rsi.yaml), so the agent can make tests pass only by fixing the code.
"""
import re
import subprocess

from rsi_anything import sdk

COMMAND = {command!r}
run = subprocess.run(COMMAND, shell=True, capture_output=True, text=True, timeout=540)
output = run.stdout + run.stderr
counts = {{kind: int(n) for n, kind in re.findall(r"(\\d+) (passed|failed|errors?)\\b", output)}}
passed = counts.get("passed", 0)
failed = counts.get("failed", 0) + counts.get("error", 0) + counts.get("errors", 0)
ran = re.search(r"Ran (\\d+) tests?", output)          # unittest
if ran and not counts:
    total = int(ran[1])
    failed = sum(int(n) for n in re.findall(r"(?:failures|errors)=(\\d+)", output))
    passed = total - failed
total = passed + failed
score = 100 * passed / total if total else (100.0 if run.returncode == 0 else 0.0)
sdk.report(score, gates={{"tests_ran": total > 0 or run.returncode == 0}},
           feedback=f"{{passed}}/{{total}} tests pass\\n" + output[-2000:],
           metrics={{"passed": passed, "total": total, "exit_code": run.returncode}})
'''

_SCORE_NUMBER = '''"""Run the command and score the last number it prints. Written by `rsi new`; edit freely.

Make sure the code the agent edits cannot print that number itself, for example by timing the
code here or in a frozen script instead of trusting its own output. `rsi check --stress` helps.
"""
import re
import subprocess

from rsi_anything import sdk

COMMAND = {command!r}
run = subprocess.run(COMMAND, shell=True, capture_output=True, text=True, timeout=540)
numbers = re.findall(r"[-+]?(?:\\d+\\.?\\d*|\\.\\d+)(?:[eE][-+]?\\d+)?", run.stdout)
ok = run.returncode == 0 and bool(numbers)
sdk.report(float(numbers[-1]) if ok else 0.0, gates={{"command_ok": ok}},
           feedback=(run.stdout + run.stderr)[-2000:], metrics={{"exit_code": run.returncode}})
'''

_STARTERS = {
    ".svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 768">\n'
            '  <rect width="1024" height="768" fill="#f4f2ec"/>\n'
            '  <circle cx="512" cy="384" r="140" fill="#9fb8a0"/>\n</svg>\n',
    ".html": '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
             '<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Draft</title>\n</head>\n'
             '<body>\n<h1>Draft</h1>\n<p>A first version of the page.</p>\n</body>\n</html>\n',
}


def files(plan: Plan) -> dict[str, str]:
    """Every file `rsi new` would write, by relative path. Starting files are only used when missing."""
    out = {CONTRACT_FILE: contract(plan)}
    if plan.kind in ("text", "visual"):
        out["judge/rubric.yaml"] = rubric(plan)
    if plan.kind == "visual":
        source = plan.artifact[0]
        out["judge/render.py"] = (_RENDER_SVG if source.endswith(".svg") else _RENDER_HTML).format(name=source)
        out[source] = _STARTERS[Path(source).suffix]
    if plan.kind == "text":
        out[plan.artifact[0]] = "A first rough draft. Replace it with your own, or let the agent start from here.\n"
    if plan.kind == "tests":
        out["judge/score.py"] = _SCORE_TESTS.format(command=plan.command)
    if plan.kind == "number":
        out["judge/score.py"] = _SCORE_NUMBER.format(command=plan.command)
    return out


def write(plan: Plan, dest: Path) -> list[str]:
    """Write the task into `dest`; returns the files written. Existing work files are never overwritten."""
    problems = plan.problems()
    if problems:
        raise ValueError("; ".join(problems))
    planned = files(plan)
    load(dest, planned[CONTRACT_FILE])   # the same validation `rsi check` uses, before anything is written
    for name in (CONTRACT_FILE, "judge"):
        if (dest / name).exists():
            raise ValueError(f"{dest / name} already exists; use an empty folder or edit it by hand")
    if plan.kind in ("tests", "number"):
        missing = [p for p in [*plan.artifact, *plan.frozen] if not (dest / p).exists()]
        if missing:
            raise ValueError(f"not found in {dest}: {', '.join(missing)} (a {plan.kind} task works on files that exist)")
    written = []
    for name, text in planned.items():
        target = dest / name
        if name in plan.artifact and target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        written.append(name)
    return written
