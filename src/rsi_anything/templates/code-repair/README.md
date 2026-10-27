# D02：修复一个记账小项目

[English](README.en.md)

默认项目包含金额解析、账单均分和月度汇总，初始实现能跑常见输入，但精度、余数、退款及日期边界尚未处理完整。AI 每轮只能修改 `expense.py`；15 项业务测试和样例输入在 `judge/` 冻结。

```bash
rsi init code-repair my-repair
cd my-repair
python judge/evaluate.py
rsi check
rsi run --agent codex --rounds 6
```

手动执行会将当前产物写入 `out/report.md`、`out/tests.json`、`out/example.json` 和 `out/metrics.json`。运行期间声明的 `outputs: [out]` 供引擎保存各轮产物。`python example.py` 可独立查看月度分类账与三人分账。

得分是通过测试数除以总数，部分修复也能保留；测试必须真实执行且不能跳过。只有 100 分表示全部固定测试通过，不代表任意业务场景都已经覆盖。每条失败都附具体测试与错误，下一轮可以修一类根因。

替换输入：在新实验开始前修改 `judge/sample.json`，可调整展示用账目；替换业务需求时同步修改 `judge/test_expense.py`、`example.py` 和配置目标，先提交再运行。一次运行中保持测试不变。

依赖与来源（2026-10-23 查阅）：只用 Python 标准库，适用于项目要求的 Python 3.9+。`judge/evaluate.py` 使用 [unittest 测试套件及结果接口](https://docs.python.org/3/library/unittest.html)；金额和日期的预期行为参考 [Decimal](https://docs.python.org/3/library/decimal.html) 与 [datetime](https://docs.python.org/3/library/datetime.html)。模板业务数据为本项目编写的虚构账目，无网络和费用。

本包的基线与验收器测试由开发流程验证；真实模型多轮实验另存 `examples/code-repair/runs/`，模板本身不生成预设候选。
