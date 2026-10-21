# RSI run `20261021-203321-fuzzy-search-speed`

**Goal:** Make `search()` in search.py as fast as possible while returning exactly the same results as before
for every input. Score = how many times faster it is than the original implementation.

Agent `codex` · judge `command` · branch `rsi/20261021-203321-fuzzy-search-speed`

| round | status | score | best | change | why |
|---:|---|---:|---:|---|---|
| 0 | BASELINE | 1 | 1 | baseline |  |
| 1 | KEEP | 4.45 | 4.45 | 用位运算计算编辑距离，并复用查询的字符位置表，减少逐格计算和重复准备的开销，在保持结果一致的同时提高搜索速度。 | score 1 -> 4.45 |
| 2 | KEEP | 17.83 | 17.83 | 维护前 k 个候选，用长度和可匹配字符数推算距离下限，跳过确定无法入选的名称，减少完整距离计算和排序开销。 | score 4.45 -> 17.83 |
| 3 | KEEP | 27.45 | 27.45 | 缓存名称的字符频次编码，用位运算计算更准确的距离下限，减少逐字符扫描和完整编辑距离计算，提高搜索速度。 | score 17.83 -> 27.45 |

Stopped: reached 3 rounds.
