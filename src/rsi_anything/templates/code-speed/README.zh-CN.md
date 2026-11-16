# 模糊搜索提速

[English](README.md)

在 `search.py` 中改进搜索实现：给定查询词、名字列表和返回数量，输出必须与冻结的参考实现一致。重复查询同一份列表可预计算，但列表变化后仍须正确。

```bash
rsi init code-speed speed-demo
cd speed-demo
rsi check
rsi run --agent codex --model gpt-6.1-sol --rounds 5
rsi report
```

只依赖 Python、Git 和一个已登录的个人编程助手。先检查基本正确性，再以参考实现耗时除以候选耗时为分数；至少提升5%才保留。结果依赖机器与当次输入，不保证固定倍数。

默认每次生成约1200个名字与多条查询。替换任务时编辑 `judge/check.py` 的输入规模/检查和 `judge/reference.py` 的固定接口，同时修改目标说明并新开实验。允许修改的产物仍只由 `rsi.yaml` 的 `artifact` 指定。

当前实跑展示和从补丁恢复的逐轮源码在仓库 `examples/code-speed/`。实现由本项目编写，循环思路参考 [autoresearch](https://github.com/karpathy/autoresearch)，未导入其训练代码。
