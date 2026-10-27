# D11：虚构设计服务合同的三轮审阅

[English](README.en.md)

输入完全由项目作者编写，不是用户的真实合同。AI 从只讨论两类问题，扩展到交付范围、付款、变更排期、验收返工、素材权利、终止结算和客户资料七类问题，并给出供双方讨论的条款草案。

| 版本 | 得分 | 处理结果 |
|---|---:|---|
| 初始 | 41 | 有效定位 2/7 类问题 |
| 第 1 轮 | 91.5 | 保留，有效定位 7/7 类问题 |
| 第 2 轮 | 0 | 拒绝，I6 建议长度超过固定上限，未调用模型评委 |
| 第 3 轮 | 87 | 拒绝，没有超过当前保留稿 |

[打开完整实验报告](runs/20261024-002852-design-contract-review/report.html) · [阅读最终讨论稿](runs/20261024-002852-design-contract-review/artifacts/final/files/out/review.html) · [结构化问题清单](runs/20261024-002852-design-contract-review/artifacts/final/files/review.json) · [独立核验记录](runs/20261024-002852-design-contract-review/verification.json)

第 2 轮的 I6 建议有 1205 字，超过 1200 字上限，因此程序未将其计入有效覆盖并在评分前拒绝。该轮仍包含七个问题编号；0 分表示没有通过这项固定要求，不能解释成“没有发现问题”或“法律分析全部错误”。原候选和失败原因完整保留。

已逐条阅读最终稿，独立核对七处条款定位、原句及建议长度。草案把新增金额、期限和许可范围明确标为待双方确认，没有编造法条、判例或断言真实合同效力，也没有假设能直接转让第三方权利。建议仍偏长，附件和待确认事项需要参与方继续整理；覆盖编号完整不等于可以直接签署。

导出的初始、三轮候选和最终版本分别重跑冻结准备脚本，生成文件逐字节一致。写手和模型评委均通过个人 Codex 显式请求 `gpt-6.1-sol`、`medium`；实际型号和费用未由 CLI 返回，保持未知。模型评分不是律师审查结论，本例不构成法律意见。

从项目根目录使用自己的个人 Codex 登录另开实验：

```bash
python3 scripts/run_demo.py contract-review --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

检查指南为作者自拟，只参考 [business.gov.au 的合同写作要素](https://business.gov.au/people/contractors/prepare-a-contract)，本次于 2026-10-24 打开原页核对。不将其中的澳大利亚法律说明用于这份虚构合同。
