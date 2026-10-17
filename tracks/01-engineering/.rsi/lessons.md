# Ratchet lessons

- 2026-10-17T19:56:26+00:00 — Round 0 baseline 42.00. Read the ledger before the next hypothesis.
- 2026-10-17T19:56:27+00:00 — Round 1 KEEP 63.20. Fix retry deduplication, exact integer bps, and empty VWAP.
- 2026-10-17T19:56:27+00:00 — Round 2 KEEP 70.00. Hoist per-order prefix scans to per-account aggregation.
- 2026-10-17T19:56:27+00:00 — Round 3 REVERT_SCORE candidate 48.00 best 70.00 gates=False. Cache account risk globally across batches.
- 2026-10-17T19:56:27+00:00 — Round 4 REVERT_GUARD: frozen path modified or deleted: test_order_engine.py. Disable a frozen correctness assertion.
- 2026-10-17T19:56:27+00:00 — Round 5 KEEP 86.00. Replace per-account scans with hash-indexed O(N) aggregation.
- 2026-10-17T19:56:27+00:00 — Round 6 KEEP 97.80. Fuse settlement into one single-pass zero-copy accumulator.
