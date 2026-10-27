# D04：CPU 手写数字分类的三轮实验

[English](README.en.md)

2026-10-24 用个人 ChatGPT 账号的 Codex CLI 真实运行 3 轮，固定优化 `training.json`，评分由 scikit-learn 在 CPU 上实际训练与预测得到，没有模型评委。固定验证集包含 450 张数字图，训练集 1347 张；数据和划分整个实验保持一致。

| 轮次 | 正式状态 | 正式正确率 | 正式错分数 | 结果 |
|---|---|---:|---:|---|
| 初始 | 基线 | 46.889% | 239/450 | 三层决策树 |
| 第 1 轮 | 保留 | 99.333% | 3/450 | 改为 RBF 核 SVM，C=10、gamma=scale，不缩放、不降维 |
| 第 2 轮 | 无修改 | — | — | 助手尝试调整 gamma 后自行恢复配置，没有进入正式评审 |
| 第 3 轮 | 无修改 | — | — | 助手尝试 PCA 后自行恢复配置，没有进入正式评审 |

最终保留第 1 轮配置，真实运行因达到 3 轮停止。最终原始训练加预测耗时 0.0248 秒，耗时依赖机器，不作为模型质量分数。正式指标从 46.889% 提升到 99.333%，不能把两次无修改轮次画成新的正式评分点。

[完整运行报告](runs/20261024-001122-cpu-digits-classifier/report.html) · [初始错例](runs/20261024-001122-cpu-digits-classifier/artifacts/baseline/files/out/mistakes.png) · [最终错例](runs/20261024-001122-cpu-digits-classifier/artifacts/final/files/out/mistakes.png) · [最终混淆矩阵](runs/20261024-001122-cpu-digits-classifier/artifacts/final/files/out/confusion.png) · [最终配置](runs/20261024-001122-cpu-digits-classifier/artifacts/final/files/training.json) · [独立复验](runs/20261024-001122-cpu-digits-classifier/verification.json)

调用显式请求 `gpt-6.1-sol`、`medium` 思考强度，使用隔离配置。CLI 没有返回服务端实际型号，`actual_model` 保持 `null`；调用量按原始返回保存，美元费用未返回。初始、每轮与最终产物全部保留，不使用手写候选序列。

导出后的初始、第 1 轮与最终配置已分别放进新临时目录，删除旧输出后，用冻结评审重新训练；分数、数据 SHA256、划分 SHA256 与原记录一致，最终仍错 3 张。第 2、3 轮保存的 `out` 是助手内部试验输出，其配置分别是改变 gamma、使用 PCA；同轮 `training.json` 已恢复为冠军配置，因此这些输出不属于正式候选评审。独立复验明确标出这一差异，未覆盖原记录。

复现入口：先在同一 Python 环境安装模板的 `requirements.txt`，准备个人 Codex 登录，再从仓库根目录执行：

```bash
python scripts/run_demo.py cpu-classifier --model gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

需要指定 CLI 路径时设置 `RSI_CODEX_BIN`。评审固定使用 scikit-learn 1.6.1；本次 Python 为 3.11.14。该验证集被反复用于调参，这些数字只说明此固定任务的改善，不是独立新数据上的泛化成绩。
