# D09：固定历史上的三轮策略参数实验

[English](README.en.md)

2026-10-24 用个人 ChatGPT 账号的 Codex CLI 真实运行 3 轮，AI 修改 `strategy.json`，固定 Python 回测程序计算结果，没有模型评委或真实交易。初始化通过官方公开接口下载 BTCUSDT 的 731 条日线；评价期间为 2023-07-01 至 2024-12-31，共 550 天，之前价格用于均线预热。

| 版本 | 得分 | 累计收益 | 最大回撤 | 成交笔数 | 成本合计 USDT | 配置变化 |
|---|---:|---:|---:|---:|---:|---|
| 初始 | 7.567 | 27.7220% | 13.4370% | 76 | 638.4787 | 3/8 日均线，半仓 |
| 第 1 轮，保留 | 31.215 | 63.2489% | 21.3557% | 16 | 167.3999 | 延长为 10/30 日均线 |
| 第 2 轮，保留 | 39.857 | 77.0542% | 24.7979% | 16 | 210.5015 | 仓位从 50% 提高到 60% |
| 第 3 轮，保留 | 49.058 | 91.1240% | 28.0442% | 16 | 256.8869 | 仓位从 60% 提高到 70% |

得分固定为“累计收益百分点 − 1.5 × 最大回撤百分点”。第一轮减少了反复交易和成本，之后两轮增加仓位，**收益上升，同时最大回撤也扩大**。这个案例展示的是固定评分下的参数迭代，不表示风险降低。同期全仓买入持有的累计收益为 206.1687%，图中始终保留该参照，没有宣称策略收益优于持有。

[完整运行报告](runs/20261024-001517-historical-sma-backtest/report.html) · [初始曲线](runs/20261024-001517-historical-sma-backtest/artifacts/baseline/files/out/equity-drawdown.png) · [最终净值与回撤](runs/20261024-001517-historical-sma-backtest/artifacts/final/files/out/equity-drawdown.png) · [最终报告及交易表](runs/20261024-001517-historical-sma-backtest/artifacts/final/files/out/report.md) · [最终策略](runs/20261024-001517-historical-sma-backtest/artifacts/final/files/strategy.json) · [独立复验](runs/20261024-001517-historical-sma-backtest/verification.json)

初始现金 10000 USDT，只做多或持有现金，无杠杆、无卖空。信号只使用前一天及更早收盘价，下一天开盘成交；每次成交扣 10 基点费用和 5 基点滑点，期末平仓同样计成本。这是固定假设，不代表平台当前费率。

AI 显式请求 `gpt-6.1-sol`、`medium` 思考强度，使用隔离配置。CLI 未返回服务端实际型号，`actual_model` 为 `null`；调用量按原始返回记录，美元费用未返回。每轮候选由模型真实修改，三轮全部保留，正常达到轮数结束。

已把导出的初始、三个候选和最终配置分别与冻结价格、成本和回测程序放进新的临时目录，删除旧输出后独立重跑。所有分数、收益、回撤、交易笔数与原记录一致；逐笔核对信号日期早于成交日期，期末平仓单独标识。数据 SHA256 为 `b9dd21e29974b4c13babd79214e43a15829abf52580d3d23c0c6450c1053b8d3`。

复现时准备个人 Codex 登录，并在运行 `rsi` 的 Python 中安装模板 `requirements.txt`，从仓库根目录执行：

```bash
python scripts/run_demo.py quant-backtest --model gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

需要指定 CLI 路径时设置 `RSI_CODEX_BIN`。模板初始化会一次下载公开历史，随后每轮离线评审。来源链接、采集时间、原始响应与 CSV SHA256 均保留在导出记录的 `source.json`。

此实验在同一段历史上反复调参，没有独立样本外验收，不代表未来收益，也不提供投资建议。行情来自 [Binance 官方市场数据接口](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints)。数据、曲线及派生分析遵循 [CC BY-NC-SA 4.0 与官方数据条款](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md)，供非商业研究、教学和开源演示；这些数据权利与本项目代码许可分开。模板安装包不捆绑行情，本实验记录保留实际使用的数据与署名。
