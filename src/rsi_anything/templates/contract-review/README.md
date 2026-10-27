# D11：示例合同问题梳理

[English](README.en.md)

默认材料是项目作者自写的虚构设计服务合同，含交付范围、付款、变更排期、验收返工、素材权利、终止结算和客户资料使用七类问题。不是用户的真实合同，不判断合同效力。

```sh
rsi init contract-review demo-contract
cd demo-contract
python3 judge/prepare.py
rsi run --rounds 6
```

助手只改 `review.json`。每项写 `issue_id`、`clause_id`、原文 `quote`、争议 `risk` 和建议 `suggestion`，编号来自 `judge/review-guide.json`。默认初稿只讨论两类问题，留出发现遗漏、说明后果和完善条款的空间。

程序核对条款定位、原句和内容长度，输出七类问题的覆盖率；模型评委另评风险解释、修改建议和阅读体验。覆盖某个编号不代表该条建议合格。评审标准与合同均冻结，初稿和后续候选不是预写的播放序列。

`out/review.html`、`review.md` 是可读报告，`coverage.json` 是定位与遗漏记录，其他文件供评审使用；`outputs: [out]` 保存逐轮产物。准备脚本只用 Python 标准库，可离线执行；多轮运行需个人助手或个人模型账号。

更换材料时，在新运行前修改 `judge/contract.json`、`review-guide.json`，同步更新初稿和评分细则。演练标准为作者自拟，只借鉴 [business.gov.au 的合同写作要素](https://business.gov.au/people/contractors/prepare-a-contract)，不把澳大利亚法律套到本例。来源核查日期为 2026-10-24。

所有成稿保留“示例、不构成法律意见”的说明。已完成真实三轮实验，最终保留分数从 41 提高到 91.5，覆盖预设的七类问题；记录与逐版复验保存在仓库 `examples/contract-review/`。
