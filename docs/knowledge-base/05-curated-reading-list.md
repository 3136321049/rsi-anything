# 05 · RSI 精选阅读路径 / Curated Reading Path

> **English summary:** Start with practical ratchet loops and reflection, then
> study program/prompt optimization and automated research, and finally examine
> open-ended self-improvement and safety. The links below are upstream sources,
> not endorsements; verify current papers, code, and licenses at the source.

这不是“链接越多越好”的仓库清单，而是一条从能动手到能质疑的路线。每读一项，
回答三个问题：它改什么？谁来评分？怎样阻止评分被钻空子？

## A. 新手入门：先看懂循环

1. **[Karpathy · autoresearch](https://github.com/karpathy/autoresearch)**  
   看 Git-as-ratchet、固定实验预算和 `results.tsv` 如何把自主试验变简单。
   重点观察“可改目标”和“固定评测”如何分离。

2. **[Anthropic · ralph-wiggum plugin](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)**  
   理解连续 Agent 循环与完成条件。思考为什么“继续跑”必须同时配熔断器。

3. **[Reflexion](https://arxiv.org/abs/2303.11366)**  
   语言反馈怎样成为跨尝试记忆。注意反思若无外部证据，也可能强化错误。

4. **[Self-Refine](https://arxiv.org/abs/2303.17651)**  
   单一模型如何反馈并迭代输出。把它与独立评审比较：自评何时会放水？

5. **[TextGrad](https://github.com/zou-group/textgrad)**  
   把文字批评当作“梯度”优化复合系统。重点看反馈如何定位到可改变量。

## B. 动手搭建：从单环到研究系统

6. **[DSPy](https://github.com/stanfordnlp/dspy)**  
   用声明式程序和评测优化 LM 流程。关注训练/开发/测试切分和过拟合。

7. **[Google Research · RRSI](https://github.com/google-research/rrsi)**  
   研究正则化递归自我改进：系统如何改进，同时约束复杂度与泛化风险。

8. **[AutoContext](https://github.com/greyhaven-ai/autocontext)**  
   观察持久上下文如何跨轮积累。区分可复用规则与堆积的原始聊天日志。

9. **[STORM](https://github.com/stanford-oval/storm)**  
   学习多视角提问、大纲与带引用长文生成。检查引用是否真正支持主张。

10. **[PaperQA](https://github.com/Future-House/paper-qa)**  
    理解科学文献检索与证据问答。特别关注来源定位、上下文与不确定性。

## C. 前沿与安全：系统开始改系统

11. **[AI Scientist v2](https://github.com/SakanaAI/AI-Scientist-v2)**  
    自动提出假设、实验和论文的完整研究流。区分“自动化流程”与“科学有效性”。

12. **[Agent Laboratory](https://github.com/SamuelSchmidgall/AgentLaboratory)**  
    多 Agent 科研协作案例。观察角色分工是否提供真实独立性与证据约束。

13. **[Darwin Gödel Machine](https://github.com/jennyzzt/dgm)**  
    开放式 Agent 自修改与经验档案。核心问题是改进能否跨任务泛化。

14. **[A-Evolve](https://github.com/A-EVO-Lab/a-evolve)**  
    阅读进化式 Agent 改进方法。关注搜索空间、选择压力和评估污染。

15. **[Specification Gaming Examples](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/)**  
    用大量反例理解“指标变好、目标变坏”。任何 RSI 设计都应先做这类威胁建模。

## 推荐练习

1. 选一个小型开源函数，写正确性测试和性能基准。
2. 冻结测试哈希，允许 Agent 每轮只改一个文件。
3. 跑五轮，记录所有失败而不只记录冠军。
4. 加一个隐藏边界测试，检查之前的“进步”是否仍成立。
5. 将经验写成一条有适用边界的 lesson，再在另一个函数上验证迁移。

上游项目的完整致谢与关系说明见
[UPSTREAM_CREDITS.md](../../UPSTREAM_CREDITS.md)和
[ATTRIBUTION.yaml](../../ATTRIBUTION.yaml)。
