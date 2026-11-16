# D12：把身体活动指南讲成办公日里的常识

[English](README.md)

这次真实三轮实验只修改科普文章，使用冻结的 WHO 资料。最终稿围绕通勤、工作间隙和活动安排，解释有氧活动、肌肉强化与减少久坐各自解决什么问题，保留一般健康成人的适用范围和少量起步的建议。

| 版本 | 得分 | 处理结果 |
|---|---:|---|
| 初始 | 58.5 | 建立基线 |
| 第 1 轮 | 80 | 保留；用生活场景解释术语、活动类型和常见误读 |
| 第 2 轮 | 77.5 | 拒绝，没有超过当前稿 |
| 第 3 轮 | 77.5 | 拒绝，最终仍使用第 1 轮 |

[打开完整实验报告](runs/20261024-001506-adult-activity-explainer/report.html) · [阅读最终科普与来源](runs/20261024-001506-adult-activity-explainer/artifacts/final/files/out/explainer.html) · [最终 Markdown](runs/20261024-001506-adult-activity-explainer/artifacts/final/files/out/explainer.md) · [核验记录](runs/20261024-001506-adult-activity-explainer/verification.json)

已逐段阅读最终稿，核对固定年龄、活动量和频率，确认没有药物、诊断、疾病疗效承诺或针对某个人的运动处方。文中例子与通俗解释是作者表达，不是 WHO 原文引语；它明确区分轻微走动和中高强度活动，也没有把完成有氧量等同于全部身体活动建议。

导出的初始、三轮候选和最终版本都重新执行了冻结准备脚本，输出逐字节一致。浏览器实际显示正文、四项指南数量和来源链接。本次使用支持多段原句核对的评分规则，四次评分的引文匹配未触发扣分，原始评委 JSON 均保存在 `verdict.json` 的 `judge_details` 中。77.5 与 80 的差别仍属于单次模型评价，不是临床有效性判断。

写手和评委都通过个人 Codex 显式请求 `gpt-6.1-sol`、`medium`；CLI 没有返回实际型号与费用，保持未知。此案例只演示公众科普的组织与改写，不接收病历，也没有经过临床专家审稿。

从项目根目录使用自己的个人 Codex 登录另开实验：

```bash
python3 scripts/run_demo.py medical-explainer --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

来源是 [WHO 欧洲区域身体活动清单](https://www.who.int/europe/news-room/fact-sheets/item/physical-activity)、[WHO 身体活动事实清单](https://www.who.int/news-room/fact-sheets/detail/physical-activity) 以及 [WHO 指南执行摘要](https://www.ncbi.nlm.nih.gov/books/NBK566048/?report=reader)。本次在 2026-10-24 核对 WHO 主站及官方搜索索引；欧洲页直读超时、NCBI 直读出现验证码，年龄、活动量、强化频率与渐进起步段通过官方索引读取，未声称重新读完指南全文。
