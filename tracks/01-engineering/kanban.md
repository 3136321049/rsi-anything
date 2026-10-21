# Ralph Loop Kanban

## Claimed

- [x] Freeze ten correctness checks and the deterministic 4,000-order benchmark.
- [x] Capture SHA-256 hashes for the verifier before mutation.

## Ratcheted

- [x] Round 1 — deduplicate repeated `order_id` retries (`KEEP`).
- [x] Round 2 — make VWAP empty-safe and settle basis points in integer cents (`KEEP`).
- [x] Round 3 — test an aggressive global risk cache (`REVERT_SCORE`).
- [x] Round 4 — simulate disabling a frozen assertion (`REVERT_GUARD`).
- [x] Round 5 — replace nested scans with hash-indexed O(N) aggregation (`KEEP`).
- [x] Round 6 — fuse aggregation into one pre-allocated pass (`KEEP`).

## Done

- [x] Champion restored after every rejected mutation.
- [x] 10/10 correctness tests pass.
- [x] Champion score exceeds the 95.0 target.
- [x] Results and lessons persisted for the next Ralph loop.
