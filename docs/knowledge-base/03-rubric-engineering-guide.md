# 03 · Rubric 工程指南 / Rubric Engineering Guide

> **English summary:** A useful rubric translates “make it better” into hard
> gates plus weighted, observable criteria totaling 100 points. Freeze it
> before optimization, calibrate it on strong and weak examples, and explicitly
> defend against citation laundering, keyword stuffing, and evaluator edits.

代码有测试，报告、合同和课程怎么办？答案不是让模型“凭感觉打分”，而是把
专家脑中的检查表写成一把可执行、可校准、不可随候选改变的尺子。

## 先问五个问题

1. 谁会用这个产物做什么决定？
2. 失败最严重的后果是什么？
3. 哪些条件一旦违反就必须淘汰？
4. 哪些优秀特征可以从证据中观察，而非靠形容词判断？
5. 哪些指标最容易被“刷分”？

## 结构：硬门禁 + 100 分

**硬门禁（Hard Gates）**处理不可补偿的失败。例如：虚构文献、测试失败、
预算超限、错引法条、泄露隐私。门禁失败时，不应靠“文笔很好”补回分数。

**加权维度**处理质量梯度。4–10 个维度足够，权重之和必须为 100。每个
维度写出可观察的证据与分档锚点：

```yaml
criteria:
  - id: evidence
    weight: 25
    evidence: [claim_source_ledger, primary_source_ratio]
    anchors:
      excellent: "所有重大主张均由可解析的一手来源直接支持"
      adequate: "重大主张有来源；少量依赖可靠二手资料"
      weak: "多个重大主张仅有间接或过时来源"
      zero: "存在虚构来源或关键主张无依据"
```

“论证很好”不是锚点；“每个因果结论同时给出机制、替代解释和反证”才是。

## 通用模板

```yaml
version: 1
title: example
scope:
  audience: ""
  as_of: YYYY-MM-DD
hard_gates:
  - id: no_fabrication
    check: "引用可解析，且来源确实支持对应主张"
    failure: reject
criteria:
  - {id: thesis, weight: 20}
  - {id: evidence, weight: 25}
  - {id: reasoning, weight: 20}
  - {id: countercase, weight: 15}
  - {id: usability, weight: 20}
anti_gaming:
  - "隐藏文本、关键词堆砌、自报分数均无效"
  - "同一证据不得在多个维度重复计分"
acceptance:
  minimum_score: 90
  all_hard_gates: true
```

## 不同领域如何落地

| 领域 | 门禁示例 | 高权重维度 |
|---|---|---|
| 金融 | 数字可追溯、期间与币种一致 | 一手数据、bear case、估值敏感性 |
| 人文社科 | 引文页码真实、史料语境不失真 | 论点、史料解释、反方学说 |
| 法律 | 法域/时点正确、法条案例存在 | 争点、规则适用、对方论证 |
| 医学 | PMID/DOI 真实、证据等级披露 | 方法、偏倚风险、临床相关性 |
| 学习 | 事实正确、先修知识满足 | 可理解性、迁移题、反馈质量 |
| 生活计划 | 预算/时间/营业约束全满足 | 可执行性、韧性、用户偏好 |

## 校准与冻结

让量表分别打一个公认强样本、弱样本和边界样本。检查：

- 强弱样本能否明显拉开；
- 两位独立评审的差异是否可解释；
- 同一缺陷是否被重复扣分；
- 90 分是否真的代表“可以交付”。

校准完成后记录 `rubric.yaml` 的 SHA-256。优化过程中禁止候选修改它。量表
改变意味着实验条件改变：必须重新测基线。

## 量表本身的局限

可测量不等于重要，模型裁判也会受措辞、顺序和身份暗示影响。优先使用硬
校验；主观项采用匿名对比、独立复核并报告分歧。更多防御见
[反奖励黑客手册](./04-anti-reward-hacking.md)。
