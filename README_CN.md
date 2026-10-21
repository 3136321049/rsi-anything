<div align="center">

# ♾️ RSI-Anything · Open RSI

## RSI 属于每一个人，AGI 属于每一个人。

**只要能评分，就能让它在你睡觉时继续进化。**

[**English**](./README.md) · [**简体中文**](./README_CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg)](./LICENSE)
[![Agent Ready](https://img.shields.io/badge/Agent_Ready-Cursor%20%7C%20Claude%20Code%20%7C%20Codex-635bff.svg)](#快速开始)
[![Six Tracks](https://img.shields.io/badge/学科轨道-6-19a974.svg)](#六大学科轨道)
[![Provenance](https://img.shields.io/badge/开源致谢-三级协议-blue.svg)](./UPSTREAM_CREDITS.md)

**一个 `GOAL.md`，一把锁死的尺子，睡后一百代自动进化。**

</div>

大多数 AI 在你停止催促时也停止进步。RSI-Anything 把工作变成一条可测量的
进化闭环：你定义“什么叫好”，现有 Agent 每轮只做一个变异，进步就保留，
退步就回滚，并把每次教训带进下一轮。

不绑架你的编辑器，不要求新平台，也不宣称今天的 Agent 已经能无限自我进化。
它是一套可移植、可审计的 Git 棘轮，让代码、模型、研报、法律、学习与生活
都能用证据说话。

## 五步 Git 进化棘轮

```text
 人类负责锁定契约                                  循环只保留真实进步

 ┌──────────────────┐     ┌────────────────┐     ┌──────────────────┐
 │ 1  目标与边界    │ ──▶ │ 2  单一原子变异│ ──▶ │ 3  锁死的裁判    │
 │ GOAL.md          │     │ mutable_paths  │     │ 测试 + rubric    │
 └──────────────────┘     └────────────────┘     └────────┬─────────┘
          ▲                                                │
          │                                                ▼
 ┌────────┴─────────┐                              ┌──────────────────┐
 │ 5  错题本与技能  │ ◀─────────────────────────── │ 4  Git 棘轮裁决  │
 │ lessons + skills │    变好：commit ✅           │ 真的更好吗？     │
 └──────────────────┘    变差：rollback ↩          └──────────────────┘
          │
          └──────────────────── 下一条可证伪假设 ───────────────────▶
```

首轮开始前，评测器与安全边界会被 SHA-256 锁死。只有分数更高且所有硬门禁
仍通过的候选，才有资格成为新冠军。

## 实时进化账本 / Live Evolution Ledger

<table>
<tr>
<th>旗舰 Demo 1 · 工程</th>
<th>旗舰 Demo 2 · 金融深度研报</th>
</tr>
<tr>
<td valign="top">

```text
Round 0  42.0 分 · ~280ms  BASELINE        7/10 通过，O(N²) 逐单前缀扫描
Round 1  63.2 分 · ~145ms  KEEP ✅         10/10 通过（幂等去重 + 整型基点）
Round 2  70.0 分 ·  ~30ms  KEEP ✅         10/10 通过，按账户聚合（提速 ~5×）
Round 3  48.0 分 ·  ~30ms  REVERT_SCORE ↩  8/10 通过，跨批次缓存泄漏被回滚
Round 4  70.0 分 ·    —    REVERT_GUARD ↩  篡改冻结测试断言，门禁拦截
Round 5  86.0 分 · ~3.5ms  KEEP ✅         10/10 通过，哈希索引 O(N) 聚合
Round 6  97.8 分 · ~1.7ms  KEEP 🏆         10/10 通过，单遍零拷贝结算内核
```

坏变异、破坏测试的捷径和 reward hacking 会自动回滚。只有**又快又正确**
的实现才能推进棘轮。

</td>
<td valign="top">

```text
Round 0  58.0 分   BASELINE        AI 味空话初稿
Round 1  72.5 分   KEEP ✅         5 家竞品毛利率与产能对照表
Round 2  64.5 分   REVERT_SCORE ↩  伪造 [SRC-99] 信源，一票否决
Round 3  84.0 分   KEEP ✅         看空章节 (Bear Case) + BOM 拆解
Round 4  84.0 分   REVERT_GUARD ↩  篡改 rubric.yaml 权重，门禁拦截
Round 5  94.5 分   KEEP 🏆         16 条核验信源 + 份额交叉配平
```

终稿是一篇关于 **2026 年人形机器人执行器与滚柱丝杠（Humanoid Robot
Actuators & Roller Screws）** 的机构级报告：一手证据、公司级经济性、
反方论证、情景触发器与逐条主张溯源表。

</td>
</tr>
</table>

账本本身就是产品：它告诉你改了什么、哪里失败、为什么淘汰，以及哪次 Git
提交是当前冠军。

<a id="快速开始"></a>
## 30 秒极速开始

把四个技能装入已检测到的 Cursor、Claude Code 和 Codex 目录：

```bash
npx rsi-anything setup
```

也可以克隆仓库，直接使用透明的本地安装脚本：

```bash
./setup.sh
python3 rsi.py demo
```

运行两个旗舰轨道：

```bash
python3 rsi.py run tracks/01-engineering --demo
python3 rsi.py run tracks/03-finance-quant-research --demo
```

然后直接对 Agent 说：

```text
/rsi 把这个接口优化 20 轮，绝不允许用正确性换速度。
/rsi-report 调研一个赛道，先锁死机构级量表，再迭代到 90 分以上。
```

不改动机器，只预览安装计划：

```bash
./setup.sh --dry-run
```

## 四个可移植 Agent Skills

| 命令 | 能力 |
|---|---|
| [`/rsi`](./skills/rsi-loop/SKILL.md) | 读取 `GOAL.md`、锁定裁判哈希、每轮只做一个改动、实测、提交赢家、回滚退步，并记录 `results.tsv` 与 `.rsi/lessons.md`。 |
| [`/rsi-rubric`](./skills/rsi-rubric/SKILL.md) | 把跨学科模糊目标变成一票否决门禁、100 分锚定量表与防作弊规则。 |
| [`/rsi-kanban`](./skills/rsi-ralph-kanban/SKILL.md) | 原子认领任务，在隔离 worktree 执行，并同时通过测试与独立 diff 审计。 |
| [`/rsi-report`](./skills/rsi-deep-report/SKILL.md) | 选题聚焦 → 量表归纳 → 定向检索/对抗审稿/修订 → 有证据的终稿交付。 |

这些技能以 Markdown 为主，完全可检查。人类拥有目标与裁判，Agent 负责产生
候选，Git 负责记住谁真正赢了。

<a id="六大学科轨道"></a>
## 六大学科轨道

| 轨道 | 允许进化什么 | 锁死的反馈 | 典型结果 |
|---|---|---|---|
| `tracks/01-engineering` | 源码、配置、性能路径 | 测试、类型、lint、基准、diff 审计 | 修 Bug 并提速，零回归 |
| `tracks/02-algorithms-ml` | 模型配置、Prompt、数据过滤器 | holdout 指标、算力上限、泄漏检查 | 固定预算下改进模型与流水线 |
| `tracks/03-finance-quant-research` | 因子、策略、行业研报 | 样本外回测或机构级量表 | 稳健策略与可溯源深度研究 |
| `tracks/04-humanities-social-sci` | 论点、大纲、证据综合 | 史料完整性、论证量表、反方 | 更深入、可核验的人文社科成果 |
| `tracks/05-law-medicine` | 合同红线、法律意见、方案、综述 | 法源/PMID 校验、行业清单 | 经对抗审查的决策支持 |
| `tracks/06-learning-life-auto` | 讲义、简历、文案、日程 | 测验、ATS、硬约束、用户反馈 | 经真实使用反馈改进的产物 |

六个领域使用同一个抽象：**可变产物 + 冻结反馈 + 有界搜索 + 证据留存**。
医学、法律与投资属于高风险场景，输出只能作为决策支持，必须由合格人士复核。

## 如何防止“假进步”？

- **锁死裁判**：优化前哈希评测器、rubric、fixture 与 holdout。
- **路径白名单**：候选只能改 `mutable_paths`，不能改游戏规则。
- **先过门禁再谈分数**：错误的快答案、编造引用、不安全输出都不是赢家。
- **独立审稿**：主观任务使用匿名跨模型审查和逐主张信源核验。
- **熔断器**：轮数、费用、时间、停滞和完整性阈值可随时停止循环。
- **全量历史**：失败假设与回滚原因也写入账本，不只展示幸存冠军。

实操请读[《反奖励黑客手册》](./docs/knowledge-base/04-anti-reward-hacking.md)。

## 三级致谢协议

开源思想要复利，荣誉也必须跟着价值走：

1. **机器可读出处**：[`ATTRIBUTION.yaml`](./ATTRIBUTION.yaml) 记录上游链接、
   关系、具体影响、落地路径与许可证核验状态。
2. **运行时署名**：启用相关方法时打印简洁致谢，并把相同记录写入结果元数据。
3. **README 英雄榜**：[`UPSTREAM_CREDITS.md`](./UPSTREAM_CREDITS.md) 用实时、
   带日期的 Star 徽章导流，不硬编码热度数字。

受到启发不等于拥有原作，互操作也不代表上游背书。若改编了代码、文字、
Prompt 或素材，必须额外记录精确 revision 与许可证通知。

## RSI 知识库

从大白话入门，再造一个值得信任的循环：

1. [10 分钟读懂 RSI](./docs/knowledge-base/01-what-is-rsi.md)——能做什么，
   以及它不证明什么。
2. [RSI 的三个层级](./docs/knowledge-base/02-three-levels-of-rsi.md)——先改产物，
   再改记忆，最后改 Harness。
3. [Rubric 工程指南](./docs/knowledge-base/03-rubric-engineering-guide.md)——把专家
   直觉翻译成硬门禁和可观察评分锚点。
4. [反奖励黑客手册](./docs/knowledge-base/04-anti-reward-hacking.md)——保护指标，
   不让优化器钻空子。
5. [精选阅读路径](./docs/knowledge-base/05-curated-reading-list.md)——从实用循环、
   自动研究到开放式进化与安全。

## 人机契约

```yaml
objective: "让目标可测量地变好"
mutable_paths: ["target/**"]
frozen_paths: ["tests/**", "rubric.yaml"]
eval_cmd: "python eval.py --json"
limits:
  max_iterations: 20
  max_stagnant_rounds: 5
```

裁判变了，就是一场新实验；硬门禁失败，就不叫进步；证据不足时，正确答案
是不确定，而不是更流畅的幻觉。

---

<div align="center">

**Chat 是打零工，RSI 才是复利机器。**

本项目独立实现，并向 [UPSTREAM_CREDITS.md](./UPSTREAM_CREDITS.md) 中所有
开源研究者与建设者明确致谢。

</div>
