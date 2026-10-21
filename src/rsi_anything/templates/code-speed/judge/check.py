"""Correctness first, then speed. Inputs are freshly random every run, so answers cannot be memorized."""
from time import perf_counter as clock  # bound before any candidate code is imported

import json
import os
import random
import string
import sys

sys.path.insert(0, os.getcwd())
sys.dont_write_bytecode = True

from judge.reference import search as reference  # noqa: E402

try:
    import search as candidate  # noqa: E402
except Exception as exc:  # a broken artifact is a failed gate, not a crashed judge
    candidate = None
    import_error = repr(exc)

SEED = int.from_bytes(os.urandom(4), "big")
rng = random.Random(SEED)


def word(low: int, high: int) -> str:
    return "".join(rng.choice(string.ascii_letters + "  -'éü") for _ in range(rng.randint(low, high))).strip() or "x"


names = sorted({word(3, 16) for _ in range(1200)})
names += [names[0], names[1].upper()]  # duplicates and case variants
queries = [word(1, 12) for _ in range(12)] + ["", names[5], names[7][:3]]
edge = [("", ["b", "a"], 5), ("abc", [], 3), ("abc", ["abd", "abc", "ABC"], 2), ("ab", ["ba", "ab", "aa"], 10)]


def report(score, correct, feedback, metrics):
    payload = {"score": score, "gates": {"correct": correct}, "feedback": feedback, "metrics": metrics}
    target = os.environ.get("RSI_RESULT")
    if target:
        with open(target, "w", encoding="utf-8") as out:
            json.dump(payload, out)
    else:
        print(json.dumps(payload, indent=2))


if candidate is None:
    report(0.0, False, f"search.py does not import: {import_error}", {})
    sys.exit(0)

wrong = []
for query, pool, k in edge + [(q, names, 5) for q in queries]:
    try:
        got = candidate.search(query, list(pool), k)
    except Exception as exc:
        got = f"raised {exc!r}"
    want = reference(query, list(pool), k)
    if got != want:
        wrong.append(f"search({query!r}, <{len(pool)} names>, {k}) returned {str(got)[:120]}, expected {want}")
# The same list object, changed in place between calls: caches must notice.
mutable = names[:60]
for step in range(3):
    query = queries[step]
    got, want = candidate.search(query, mutable, 4), reference(query, list(mutable), 4)
    if got != want:
        wrong.append(f"after the name list changed, search({query!r}) returned {got}, expected {want}")
    mutable.append(query + "x")
    mutable.pop(0)

if wrong:
    report(0.0, False, f"{len(wrong)} wrong answers, e.g. " + " | ".join(wrong[:2]), {"seed": SEED})
    sys.exit(0)


def timed(fn, repeats):
    best = float("inf")
    for _ in range(repeats):
        start = clock()
        for query in queries:
            fn(query, names, 5)
        best = min(best, clock() - start)
    return best


reference_time = timed(reference, 2)
candidate_time = timed(candidate.search, 3)
speedup = reference_time / max(candidate_time, 1e-9)
report(round(speedup, 2), True,
       f"correct on all {len(edge) + len(queries)} checks; {speedup:.1f}x faster than the original "
       f"({candidate_time * 1000:.1f} ms vs {reference_time * 1000:.1f} ms for {len(queries)} queries over {len(names)} names)",
       {"seed": SEED, "candidate_ms": round(candidate_time * 1000, 2), "reference_ms": round(reference_time * 1000, 2)})
