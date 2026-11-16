# D01：模糊搜索提速

[English](README.md)

2026-10-21 的真实三轮运行将固定负载下的速度从基线提高到 **4.45、17.83、27.45 倍**，三轮均保留。分别改进距离计算、候选剪枝和可复用的名字统计，输出仍须通过参考实现的正确性检查。

[运行报告](runs/2026-10-21-codex-3-rounds/report.html) · [原始账本](runs/2026-10-21-codex-3-rounds/ledger.jsonl) · [逐版正确性复核](runs/2026-10-21-codex-3-rounds/artifact-verification.json) · [模板与替换输入](../../src/rsi_anything/templates/code-speed/README.zh-CN.md)

初始、三轮候选与最终源码已按原始补丁重建，分别在运行目录的 `artifacts/baseline/`、`rounds/r001/artifacts/` 至 `rounds/r003/artifacts/`、`artifacts/final/`。本次复核全部正确；复核的耗时不替换历史分数。加速倍数依赖机器与输入规模。

```bash
rsi init code-speed speed-demo
cd speed-demo
rsi check
rsi run --agent codex --model gpt-6.1-sol --rounds 5
rsi report
```

该命令启动新实验，需要已登录的个人助手和可用型号。历史运行使用账号默认型号，没有额外返回的服务端型号确认。实现由本项目编写，循环思路参考 autoresearch，没有导入其运行引擎。
