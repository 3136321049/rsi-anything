# D08：Apple 历史经营分析的三轮改写

[English](README.en.md)

这次实验使用 Apple 2023、2024 财年的固定官方资料，AI 修改报告和图表选择。最终稿把产品下降、服务增长、营业利润与净利润的不同走势连成可追踪的解释，区分数字事实、可能原因和资料不能回答的问题。

| 版本 | 得分 | 处理结果 |
|---|---:|---|
| 初始 | 53.5 | 建立基线 |
| 第 1 轮 | 74 | 保留；补充收入结构和一次性所得税费用的解释 |
| 第 2 轮 | 79 | 拒绝；交换顺序后新稿只获 1/2 票 |
| 第 3 轮 | 61.5 | 拒绝；没有超过当前保留稿 |

[打开完整实验报告](runs/20261024-000043-apple-operating-report/report.html) · [阅读最终成稿和图表](runs/20261024-000043-apple-operating-report/artifacts/final/files/out/report.html) · [查看最终 Markdown](runs/20261024-000043-apple-operating-report/artifacts/final/files/out/report.md) · [核验记录](runs/20261024-000043-apple-operating-report/verification.json)

程序核对数字键、单位、引用和图表；模型评价解释与结构。写手和评委都显式请求个人 Codex 的 `gpt-6.1-sol`、`medium`，实际型号和美元费用未由 CLI 返回，保持未知。每次评分是当前评价条件下的判断，不等同于独立财经专家认可。

第 3 轮有两项评委引文未通过当时的原文匹配，触发该维度最高 3 分的规则。旧核对逻辑可能把多处原句拼接引用误判为无法匹配；本次未保存原始评分 JSON，不能进一步确认这两项属于哪种情况，也不能只凭 61.5 推断正文大幅退化。当前模板只能选择最多三张单指标图，无法生成评委建议的合并贡献图；这限制了进一步图表改进。

已阅读最终稿，核对官方财报全年数据和一次性税费，独立重算同比和产品加服务的营收关系。导出的初始、三轮候选和最终版本均在新临时目录重新生成，输出逐字节一致。浏览器已实际显示正文、数据表和三张图；图形依赖联网加载 Mermaid，离线仍可读正文与数值表。

使用自己的个人 Codex 登录，从项目根目录另开实验：

```bash
python3 scripts/run_demo.py business-report --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

数据来自 [Apple 官方全年财务报表](https://www.apple.com/newsroom/pdfs/fy2024-q4/FY24_Q4_Consolidated_Financial_Statements.pdf)，本次核查日期为 2026-10-24。这是固定历史资料的经营分析演示，不是最新财报或投资建议。
