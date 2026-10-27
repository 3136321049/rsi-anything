# D13：补齐百分比讲义后，让受限模型作答

[English](README.en.md)

初稿只介绍百分比定义和已知整体求部分。真实写手补充了逆向求解、变化率、连续变化、整体改变和百分点，并用不同于固定练习的例题解释方法。一个受提示词限制的学生模型阅读讲义后，回答十道固定原创题，程序核对数值、推导文字和讲义原句依据。

| 版本 | 有原句依据且答对 | 纯数值正确率 | 处理结果 |
|---|---:|---:|---|
| 初始 | 2/10 | 20% | 建立基线 |
| 第 1 轮 | 10/10 | 100% | 保留 |
| 第 2 轮 | 10/10 | 100% | 拒绝，没有超过当前分数 |
| 第 3 轮 | 10/10 | 100% | 拒绝，最终仍使用第 1 轮 |

[打开完整实验报告](runs/20261024-003730-percent-lesson/report.html) · [阅读最终讲义与十题推导](runs/20261024-003730-percent-lesson/artifacts/final/files/out/lesson.html) · [初始错例](runs/20261024-003730-percent-lesson/artifacts/baseline/files/out/mistakes.json) · [独立复验记录](runs/20261024-003730-percent-lesson/verification.json)

写手显式请求个人 Codex 的 `gpt-6.1-sol`，受限学生固定请求 `cli:codex:gpt-5.6-sol`，思考强度为 `medium`。这里由程序比对固定答案给分，不另设模型写作评委。CLI 未返回实际型号或美元费用，保持未知；所有原回复、推导和调用量均保存。

已独立重算十道题的固定答案，并用冻结的判分程序重放初始、三个候选和最终版本的原始学生回复，结果与账本一致，没有追加模型调用或覆盖原成绩。已阅读最终讲义及十题推导，例题使用新的情节或数值组合，正文没有复制固定题整句。浏览器能够查看完整讲义、学生答案、依据原句和固定解答。

这个结果只说明给定提示词约束下的模型作答变化。学生模型本来就可能掌握这些知识，限制由提示词表达；原句出现也不能自动证明语义支持，题目未作为隐藏留出集。因此不能把20%到100%解释成真人学习效果或对新题的泛化能力。

从项目根目录使用自己的个人 Codex 登录另开实验：

```bash
python3 scripts/run_demo.py lesson-builder --model gpt-6.1-sol --task-model cli:codex:gpt-5.6-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

安装本项目后，可在运行目录执行 `python verify_saved_results.py` 离线复验。讲义和题目由项目作者编写，仅以 [OpenStax 百分比章节](https://openstax.org/books/prealgebra-2e/pages/6-introduction-to-percents) 为公开概念参考，没有复制教材题目或正文。
