# 扩展一个自己的任务

[English](EXTENDING.md)

先选择相近模板，保留现有循环，只替换这个领域的输入、可改产物和评价。命令评分可从 `code-repair` 或 `cpu-classifier` 开始；文字评分可从 `business-report` 或 `literature-review` 开始；需要模型实际执行方法时参考 `writing-guide`、`lesson-builder`。

当前 13 个领域已有完整多轮和独立验证。写作手册、合同演练、讲义都可以直接参考真实作品与记录；D07 是服务受限的部分实测，D15 等待 GPU，不能用这两项的模板或探测替代成功案例。完整入口见[领域清单](DEMO-PLAN.zh-CN.md)。

## 把任务写清楚

一个最小领域包需要回答：给什么材料、AI 改什么、如何产生作品、怎样比较好坏、何时停止、结果保存在哪里。模型修改产物，固定程序负责渲染、训练或核对；不要让模型自己写最终得分。

```yaml
name: my-writing-task
goal: 根据 judge/brief.md 的固定资料改进 draft.md，让目标读者更容易理解。
artifact: [draft.md]
outputs: [out]
judge:
  type: rubric
  prepare: "{python} judge/prepare.py"
  rubric: judge/rubric.yaml
  files: [judge]
  inputs: [out/article.md]
  models: [cli:codex:gpt-6.1-sol]
  pairwise: true
  timeout: 600
agent:
  use: codex
  model: gpt-6.1-sol
  timeout: 600
budget:
  rounds: 5
  minutes: 60
  stagnation: 3
```

这段配置需要配套创建初稿、固定资料、准备脚本和评分细则。模型型号换成自己账号可用的型号，且在一次运行内固定。

| 配置 | 实际含义 |
|---|---|
| `artifact` | 允许修改并形成候选的相对路径；不能与固定评分文件重叠 |
| `judge.files` | 固定测试、资料与评价程序；开始运行时从起始提交取快照 |
| `prepare` | 评分前在评审副本执行的命令，可生成报告、视频、模型回答 |
| `inputs` | 模型评委看到的作品路径；未填写时默认用 `artifact` |
| `outputs` | 需要随初始、候选和最终版本保存的生成文件或目录；不是额外可改范围 |
| `assets` | 外部大素材入口；评审会使用链接，不把外部文件自动复制进每份导出 |
| `holdout` | 可选的另组评价，在开始和结束时运行；结果与开发评分分开 |

路径不能越出项目；使用 `judge/` 固定资料、`out/` 保存生成文件最直接。初始化或改变资料后先提交，再开始新运行。

## 程序评分

`judge.type: command` 使用 `judge.run`，例如 `"{python} judge/evaluate.py"`。`{python}` 会替换成运行 `rsi` 的解释器。评分程序把结果写到 `RSI_RESULT` 指定的文件；使用项目提供的 `report_result` 即可。标准输出日志不会被当成得分。

下面是接口片段，其中 `checks` 应来自真正执行的固定测试：

```python
from rsi_anything import report_result

passed = sum(checks.values())
score = 100 * passed / len(checks)
report_result(
    score,
    gates={"executed": True},
    feedback=f"通过 {passed}/{len(checks)} 项测试",
    metrics={"checks": checks},
)
```

如果希望每一项业务检查都必须通过，把它们放入 `gates`；如果任务本身是逐步修复，测试通过率可作为实际得分，结构有效、程序确已运行等条件作为门槛。模型或服务无法调用时，写明错误并以非零状态退出，不伪造一个质量分数。

可以设置 `direction: maximize` 或 `minimize`、`min_delta`、`min_gain: 5%`，也可用 `repeats` 重复评价取中位数。只有超过要求幅度的改善才保留。

## 模型评分与准备步骤

`rubric.yaml` 写清任务、固定参考资料、评价维度与具体档位。先保留少数能解释改进方向的维度，例如事实一致性、论证、读者是否看懂。`context` 可列出固定参考文件，`checks` 是模型判断的必要条件；`gates` 提供长度、必需词、禁用词等基础规则。

准备脚本可输出 `out/gates.json`，格式为 `{"条件名称": true}`，以及 `out/notes.txt`。这些规则失败时不会继续调用模型评委。规则通过后，模型依据作品和细则评分；文字任务可以再做正反顺序的新旧比较。图片、视频输入目前跳过这一步，视频按均匀抽帧评价，不能代表完整视听质量。

外部生成或环境失败时，准备脚本还应写 `out/error.json`，明确 `quality_result: "unknown"`，并以非零状态退出。当前引擎将这种失败记为无质量分的评审失败。已经保存的旧记录不要改写，可像 [D07 的派生核验](../examples/video-generation/runs/20261024-003656-warm-morning-product-video/outcome-audit.json)那样关联原账本哈希，说明原失败与有效解释。

程序检查与模型检查各有范围。正文含有一个真实引用编号，不等于那篇资料真的支持该句；模型给分提高，也不等于真实业务收益。把当前检查范围写进模板 README 即可，不必先做研究级校准才能开发 Demo。

## 把模型当作任务的一部分

提示词优化、写作手册和讲义都需要“生成后再评价”。应固定执行该任务的个人模型，并保留输入、模型回答、调用信息和错例。

- `prompt-opt` 通过 `RSI_TASK_MODEL` 执行分类，再和固定标签比较。
- `writing-guide` 通过 `RSI_WRITER_MODEL` 按手册生成文章，再交给模型评委。
- `lesson-builder` 让 `RSI_TASK_MODEL` 读讲义答固定练习，再核对答案与讲义依据。

不要预写一组越来越好的候选作为自动迭代结果。测试中可以模拟模型接口，但测试产物必须留在测试目录，不能计入 Demo 实跑。

## 保存、恢复和验收

引擎在临时评审副本清理前保存 `artifact + outputs`。每份快照有文件清单、字节数与 SHA256，并标记来源是正式评审还是助手工作目录。没有正式改动的轮次可能含助手试验文件，不能把它们当成正式评审结果。

需要外部昂贵任务时，按 `video-generation` 的方式在项目外持久缓存事件编号和成片。已受理请求优先恢复，不把一次超时直接变成第二次提交。服务返回结果不确定时明确停止自动重发。

新增包至少完成：固定输入和可读初稿、离线程序测试、一次真实多轮、初始与最终产物、失败与拒绝记录、独立复核、替换材料入口和来源说明。缺少资源的项按首发任务书的资源例外单列，不能写成实测成功。

将包放入 `src/rsi_anything/templates/<名称>/`，至少提供 `rsi.yaml`、`ABOUT.txt`、`README.md`、初稿和 `judge/`。需要下载素材或准备数据时增加 `rsi_init.py`；该脚本会被 `rsi init` 实际执行，所以 README 必须讲清网络与资源需求。

提交到案例集合时，先用 `rsi export` 保存原始运行与独立验证，再登记 `examples/catalog.json`，最后重新运行 `scripts/build_showcase.py`。已验收需要正常结束、至少两轮有效尝试、最终作品和通过的独立验证；视频、留出评价和 GPU 案例还有对应结果要求。无修改轮次的内部 `out` 不充当正式作品，服务失败的质量分留空。展示页来自原始记录，不能反向覆盖账本。原始素材与数据若不随导出打包，应提供来源、版本和补齐办法。

制作宣传材料时直接使用保存的作品，并列出来源。现有[35 秒展示剪辑](../examples/showcase-media/openrsi-demo.mp4)及其[来源凭证](../examples/showcase-media/demo-video.json)可作为参考；展示剪辑本身不是新的优化实验。
