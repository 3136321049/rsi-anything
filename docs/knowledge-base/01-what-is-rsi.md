# 01 · 什么是 RSI？ / What Is RSI?

> **English summary:** Recursive Self-Improvement (RSI) is a measured loop:
> propose one change, evaluate it with a frozen judge, keep proven gains, revert
> regressions, and carry lessons forward. RSI-Anything applies that practical
> pattern to artifacts and workflows; it does not claim that today's agents
> autonomously become AGI.

## 一句话解释

普通聊天像抓阄：模型答一次，好坏都交给你。普通工作流像流水线：
步骤固定，但不会因结果差而自动变聪明。RSI 更像一个有裁判的进化实验：

```text
定目标 → 产生一个变异 → 用锁死的尺子测量 → 只保留进步 → 记住教训 ↺
```

三个条件缺一不可：

1. **变异（Variation）**：每轮只提出一个可验证的小改动。
2. **选择（Selection）**：同一套测试或量表判断候选是否真的更好。
3. **遗传（Retention）**：Git 保存赢家，错题本保存跨轮可复用的经验。

这就是“棘轮”：向上的结果锁住，向下的结果回滚。它不是保证成功的魔法，
而是把“反复试错”变成可审计、可停止、可复现的工程过程。

## 五步循环

| 步骤 | 人话 | 关键产物 |
|---|---|---|
| 1. Goal | 说清想要什么、能改什么 | `GOAL.md` |
| 2. Mutate | 做一个原子改动 | candidate diff |
| 3. Judge | 用未改变的裁判测量 | tests / `rubric.yaml` |
| 4. Ratchet | 进步就提交，退步就回滚 | Git commit / revert |
| 5. Reflect | 把证据变成下一轮规则 | `.rsi/lessons.md` |

## 为什么 Git 很适合做棘轮？

Git 给每个版本一个身份，能精确比较差异，也能恢复到已知冠军。`results.tsv`
记录“试过什么、分数多少、为什么保留或淘汰”，避免只展示最后的幸存者。
但有未提交的人类工作时，绝不能粗暴执行破坏性回滚；应使用隔离 worktree。

## 哪些东西可以进化？

- 代码性能、测试通过率、模型参数与提示词；
- 研报、论文、合同草案、课程讲义和计划；
- 错题本、检索策略、工具链与可复用技能。

前提永远是：能把“更好”翻译成可靠反馈。指标越容易被钻空子，系统越需要
隐藏测试、事实核查和独立盲审。

## RSI 不是什么

- **不是 AGI 已经实现的证据**：局部工作流改进不等于无限智能增长。
- **不是无人监管的无限循环**：必须有轮数、费用、时间和停滞熔断器。
- **不是把主观判断伪装成科学**：模型评分有偏差，需校准并披露不确定性。
- **不是跳过专家责任**：医学、法律和投资结论仍需合格人员审查。

## 第一次实践

选择一个低风险、十分钟内可评估的小目标。写清可改路径，锁定测试，跑出
基线，只允许一个改动。无论成败都记录证据。然后继续阅读
[RSI 的三个层级](./02-three-levels-of-rsi.md)与
[Rubric 工程指南](./03-rubric-engineering-guide.md)。
