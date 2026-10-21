---
name: "Order Matching & Risk Settlement Kernel Optimization"
track: "01-engineering"
direction: "maximize"
target_score: 95.0
max_iterations: 7
eval_cmd: "python3 eval_engineering.py"
mutable_paths: ["order_engine.py"]
frozen_paths: ["eval_engineering.py", "test_order_engine.py"]
upstream_credits: ["Ralph loop", "Git ratchet", "test-driven development"]
---
# Engineering objective

Improve a deterministic order settlement kernel without weakening its frozen
correctness suite or benchmark. The champion must preserve exact cent-level
fees, idempotent retries, safe zero-volume handling, and linear-time risk
aggregation.
