# RSI run `20261023-234857-expense-code-repair`

**Goal:** 修复 expense.py 中的金额解析、账单均分和月度分类汇总，使 judge/test_expense.py 的固定测试全部通过。
金额用整数分保存；均分时前几人各多分一分钱；退款为负数；月份按有效的 YYYY-MM 匹配。
保持公开函数接口与返回类型，不能改测试或针对测试输入写死答案。每轮优先修复一类根因。
得分为固定测试通过率，100 分才表示全部修复；部分通过也能作为下一轮起点。

Agent `codex` · judge `command` · branch `rsi/20261023-234857-expense-code-repair`

| round | status | score | best | change | why |
|---:|---|---:|---:|---|---|
| 0 | BASELINE | 40 | 40 | baseline |  |
| 1 | KEEP | 60 | 60 | 金额解析改为格式校验后用整数计算分，消除浮点误差并拒绝非法金额，因此提高固定测试通过率。 | score 40 -> 60 |
| 2 | KEEP | 80 | 80 | 修复均分时丢失余数和缺少参数校验的问题，使金额完整分配并拒绝非法输入，因此提高固定测试通过率。 | score 60 -> 80 |
| 3 | KEEP | 100 | 100 | 修复月度汇总中的日期和月份校验及退款符号处理，使非法日期被拒绝、退款正确抵扣，因此提高固定测试通过率。 | score 80 -> 100 |

Stopped: reached 3 rounds.

运行状态：finished。调用费用：工具未提供。

[任务配置](config/rsi.yaml) · [模型与运行参数](config/execution.json)

## 产物版本

- 初始产物：[expense.py](artifacts/baseline/files/expense.py) · [out/example.json](artifacts/baseline/files/out/example.json) · [out/metrics.json](artifacts/baseline/files/out/metrics.json) · [out/report.md](artifacts/baseline/files/out/report.md) · [out/tests.json](artifacts/baseline/files/out/tests.json)
- 第 1 轮 · KEEP：[expense.py](rounds/r001/artifacts/files/expense.py) · [out/example.json](rounds/r001/artifacts/files/out/example.json) · [out/metrics.json](rounds/r001/artifacts/files/out/metrics.json) · [out/report.md](rounds/r001/artifacts/files/out/report.md) · [out/tests.json](rounds/r001/artifacts/files/out/tests.json)
- 第 2 轮 · KEEP：[expense.py](rounds/r002/artifacts/files/expense.py) · [out/example.json](rounds/r002/artifacts/files/out/example.json) · [out/metrics.json](rounds/r002/artifacts/files/out/metrics.json) · [out/report.md](rounds/r002/artifacts/files/out/report.md) · [out/tests.json](rounds/r002/artifacts/files/out/tests.json)
- 第 3 轮 · KEEP：[expense.py](rounds/r003/artifacts/files/expense.py) · [out/example.json](rounds/r003/artifacts/files/out/example.json) · [out/metrics.json](rounds/r003/artifacts/files/out/metrics.json) · [out/report.md](rounds/r003/artifacts/files/out/report.md) · [out/tests.json](rounds/r003/artifacts/files/out/tests.json)
- 最终产物：[expense.py](artifacts/final/files/expense.py) · [out/example.json](artifacts/final/files/out/example.json) · [out/metrics.json](artifacts/final/files/out/metrics.json) · [out/report.md](artifacts/final/files/out/report.md) · [out/tests.json](artifacts/final/files/out/tests.json)
