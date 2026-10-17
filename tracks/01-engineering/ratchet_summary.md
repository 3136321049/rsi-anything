# Engineering Ratchet Summary

The loop finished at **97.8/100** with all 10 frozen
correctness tests passing. The deterministic reference benchmark progressed
from **220.0 ms** to **4.5 ms** on 4,000 orders (about **49×**, conservatively
reported as the target's **45× speedup**).

| Round | Mutation | Decision | Champion |
|---:|---|---|---:|
| 0 | Buggy quadratic baseline | BASELINE | 42.0 |
| 1 | `order_id` retry deduplication | KEEP | 54.0 |
| 2 | Safe VWAP and integer basis-point settlement | KEEP | 68.5 |
| 3 | Cross-batch global risk cache | REVERT_SCORE | 68.5 |
| 4 | Frozen-test assertion removal | REVERT_GUARD | 68.5 |
| 5 | Hash-indexed O(N) risk aggregation | KEEP | 89.2 |
| 6 | Single-pass, pre-allocated settlement accumulator | KEEP | 97.8 |

The wall-clock measurements from this machine remain in `results.tsv`
summaries; reference latency is fixed so demo scores remain reproducible across
developer hardware.
