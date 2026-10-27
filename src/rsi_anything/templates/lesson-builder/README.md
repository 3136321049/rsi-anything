# D13：百分比讲义与练习

[English](README.en.md)

助手改进 `lesson.md`，让一个真实学生模型阅读后完成十道固定原创练习。内容从求部分延伸到还原原量、变化率、连续涨跌、百分点和整体改变。初稿只讲基本定义与求部分。

```sh
rsi init lesson-builder demo-lesson
cd demo-lesson
export RSI_TASK_MODEL='cli:codex'
rsi run --rounds 6
```

`RSI_TASK_MODEL` 必须明确设置，可填已有个人模型引用，例如 `cli:codex` 或自己配置的 API 模型。学生收到讲义、题目与格式要求，不收到固定答案；允许算术与按讲义方法推导，所需方法缺失时返回不确定。此限制通过提示词表达，不是经过校准的人类学生模拟。

程序逐题比较真实模型给出的数值与固定答案，并检查推导文字和讲义原句是否存在。主分数是“有原句依据且数值正确”的比例，同时保留纯数值正确率。原句匹配不能证明语义上充分支持答案；强模型可能在初稿上已满分，必须如实记录，不人为降低成绩。

`out/lesson.html`、`lesson.md` 保存讲义，`exercise-results.md` 保存每题解答，`results.json` 含实际模型与调用信息，`mistakes.json` 保存错例，`student-response.txt` 保留原回复。模型或响应格式失败写入 `error.json` 并作为运行错误退出，不计为学生答错。`outputs: [out]` 保存逐轮产物。

本包沿用项目的模型调用接口，没有新增依赖。直接运行 `python3 judge/evaluate.py` 会真实调用学生模型；离线开发应运行仓库测试，不会调用模型。固定题目与初稿由作者自行编写，公开概念参考 [OpenStax Prealgebra 2e 第六章](https://openstax.org/books/prealgebra-2e/pages/6-introduction-to-percents)，查阅日期为 2026-10-24，没有复制教材题目。

更换主题前同步修改 `judge/brief.md`、`exercises.json` 的题目/答案/容差/解析及初始讲义；保持数值题格式可复用现有评分器。提交新输入后开始新运行，不在一次实验中修改固定练习。已完成真实三轮实验，受限学生模型由 2/10 提高到 10/10；记录与离线判分重放保存在仓库 `examples/lesson-builder/`。这不等同于真人学习效果。
