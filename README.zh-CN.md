# Open RSI / RSI-Anything

**给 AI 一个目标，让它反复修改作品、接受反馈，并留下真正有用的版本。**

Open RSI 是一个本地运行的多领域 Demo 工具：编程助手改代码、文章、配置或提示词，程序和模型评委检查结果，再决定保留还是拒绝。你可以看到初稿、每轮改动、最后保留的作品及完整记录。

当前版本为 `0.2.0.dev0`，提供 **15 个领域、16 个模板**；文案领域有单篇与写作手册两个模板。这是可运行的首发开发版，安装以当前源码或本地 wheel 为准，不表示已在 PyPI 发布。需要一个可用的个人编程助手或模型账号。

**目前 13 个领域已有完整多轮记录、初始与最终作品和独立验证。** D07 视频生成取得了初始及第 1 轮成片，后续服务失败，保留部分实测；D15 因缺少兼容个人 GPU，性能结果留空。两项资源例外都明确展示，不计入完整实测数量。

[观看 35 秒真实产物短片](examples/showcase-media/openrsi-demo.mp4) · [短片来源与媒体验证](examples/showcase-media/demo-video.json) · [本地案例集合](examples/index.html)

**换电脑继续开发：检出 `rebuild` 分支，先读[跨电脑协作](docs/COLLABORATION.zh-CN.md)和[接手说明](docs/HANDOFF.zh-CN.md)。** Codex 与 Claude Code 共用仓库的 [AGENTS.md](AGENTS.md)，最近成果、当前目标和下一步通过 Git 中的文档交接，账号与运行环境在各电脑独立准备。

[English](README.md) · [安装与账号配置](docs/INSTALL.zh-CN.md) · [领域与实验状态](docs/DEMO-PLAN.zh-CN.md) · [扩展模板](docs/EXTENDING.zh-CN.md) · [开源组件与资料来源](docs/OPEN-SOURCE.zh-CN.md)

## 先看几个真实案例

| 案例 | 这次具体发生了什么 | 记录 |
|---|---|---|
| Python 记账修复 | 三轮从 6/15 项测试通过，依次修到 9/15、12/15、15/15 | [源码、逐轮测试和成品](examples/code-repair/README.md) |
| CPU 数字分类 | 固定验证集正确率从 46.889% 到 99.333%；后两轮没有正式新改动 | [混淆矩阵与错例](examples/cpu-classifier/README.md) |
| 经营分析报告 | 初稿 53.5 分，最终保留 74 分稿；更高分候选也可能在新旧比较中被拒绝 | [报告、数据图表与理由](examples/business-report/README.md) |
| 客服提示词 | 完整三轮均未提升，保留原提示词；开发集 89.6%，留出集 82.8% | [提示词、错例与拒绝记录](examples/prompt-opt/README.md) |
| 写作手册 | 五轮保留 62→69.5→74.5 分手册；用于一份新简报时，评分 69→77.5 | [手册、三份开发稿与新简报结果](examples/writing-guide/README.md) |
| 示例合同 | 三轮最终保留 91.5 分讨论稿，有效定位 7/7 类问题；失败和较弱候选照常保留 | [虚构合同、建议与独立复核](examples/contract-review/README.md) |
| 百分比讲义 | 三轮让受提示词限制的学生模型从 2/10 到 10/10 题答对且有原句依据 | [讲义、作答与结果边界](examples/lesson-builder/README.md) |

这些结果属于对应任务与评价条件，不是跨任务能力保证。训练验证集被反复用于调参；模型评分不是专家认证。所有正式失败、停滞和拒绝都保留，不把分数补成连续上升。

## 从一个小项目开始

在拿到的源码目录中执行，建议使用 Python 3.11：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
rsi agents
rsi init code-repair ../open-rsi-demo
cd ../open-rsi-demo
rsi check
rsi run --agent codex --model gpt-6.1-sol --rounds 3
rsi report
rsi export --to ../open-rsi-result
```

示例需要个人 Codex CLI 已登录并支持指定型号；可替换为自己的助手和型号。`rsi check` 会真实执行模板评分，含模型或视频生成的模板会产生实际调用。首次 Git 提交失败、CLI 版本、可选依赖和 API 配置见[安装说明](docs/INSTALL.zh-CN.md)。

## 有哪些模板

| 领域 | 模板 | 每轮改什么 |
|---|---|---|
| D01 工程提速 | `code-speed` | 模糊搜索实现 |
| D02 工程修复 | `code-repair` | 小型记账程序 |
| D03 提示词 | `prompt-opt` | 外卖客服八分类提示词 |
| D04 算法与训练 | `cpu-classifier` | CPU 分类器与预处理配置 |
| D05 文案与写作手册 | `copywriting`、`writing-guide` | 单篇文案，或供固定写手重复使用的方法 |
| D06 视频剪辑 | `video-cut` | 口播选句与顺序 |
| D07 视频生成 | `video-generation` | 生成描述、反向描述与种子 |
| D08 经营分析 | `business-report` | 报告与图表选择 |
| D09 量化研究 | `quant-backtest` | 固定历史上的策略参数 |
| D10 资料综述 | `literature-review` | 论证与来源映射 |
| D11 示例合同 | `contract-review` | 问题定位与修改建议 |
| D12 医学科普 | `medical-explainer` | 权威资料的公众表达 |
| D13 学习教育 | `lesson-builder` | 讲义与例题解释 |
| D14 生活规划 | `weekly-planner` | 一周日程 |
| D15 GPU 算子 | `kernel-speed` | Softmax 实现与启动参数 |

每个模板都有自己的输入、使用说明与评价方法，运行 `rsi init` 可列出入口。D01–D06、D08–D14 已完成多轮与独立验证，D05 的单篇和手册结果均已保存。**模板存在不等于完成实跑。** [D07](examples/video-generation/README.md) 保留部分实测与服务错误，[D15](examples/kernel-speed/probes/2026-10-24-local/README.md) 保留无 GPU 探测及空的性能结果；两项按资源例外处理，不阻挡其他成果交付。逐项证据见[领域说明](docs/DEMO-PLAN.zh-CN.md)与[执行表](docs/GOAL-PROGRESS.zh-CN.md)。

## 多轮如何运行

`rsi.yaml` 定义目标、可改文件、固定评分资料、助手与预算。每轮从当前最好提交开始，只把允许范围内的改动送进新的评审副本。先过必要检查，再比较分数；文字任务可增加交换顺序的新旧比较。通过的候选成为运行分支上的真实 Git 提交，其他候选保留记录后丢弃。

初始、逐轮和最终作品保存于 `.rsi/runs/<运行号>/`。`outputs` 指定需要保存的视频、图表或报告，`rsi export` 会一起导出。`rsi run --resume <运行号>` 可以恢复同一配置的中断运行。详见[当前架构](docs/PLAN.zh-CN.md)。

这套流程优化任务产物与可复用手册，没有训练助手权重，也没有证明通用能力会自行提升。评分代码仍在本机执行，工作目录分开不等于强安全沙箱。只运行自己理解并愿意执行的模板。

## 查看品牌首页与三个实验室

正式展示入口：[DARWIN — An evolution lab by RiseAI.](https://www.riseai.top/darwin/) 用真实反馈，持续改进作品。

新版网站提供代码优化、模型实验、视频创作三个入口，各自展示真实修改、参数、图像或成片。支持轮次比较、字幕跳转、预测筛选、结果下载和使用说明，浏览不调用模型。

```bash
python scripts/build_site.py
python -m http.server 8765 --bind 127.0.0.1 --directory build/site
```

浏览器打开 `http://127.0.0.1:8765/`。构建目录包含运行所需的媒体、记录和下载包；完整案例集合仍可从导航进入。详见 [网站说明](web/README.md)与[网站验收](release/site-validation.json)。网页运行新实验的服务尚未接入，开始使用页面提供真实命令行步骤。

## 本地查看案例集合

从源码根目录生成并打开本地展示：

```bash
python scripts/build_showcase.py
python -m http.server 8765 --bind 127.0.0.1
```

浏览器打开 `http://127.0.0.1:8765/examples/index.html`，可选领域、运行、左右版本和文件，查看文字差异、图表与视频。展示页从 `examples/catalog.json` 和原始实验目录生成，不修改账本。分享时应保留整个导出目录；HTML 页面不会把所有视频变成单文件。

[35 秒无声演示短片](examples/showcase-media/openrsi-demo.mp4) 由已经保存的代码修复记录、手册评分、口播剪辑和分类错例组成，不是新的优化实验。[媒体验证记录](examples/showcase-media/demo-video.json) 保存来源、哈希、时长、尺寸与解码结果。

## 组件与资源

主循环由本项目实现，实际使用 Git、Python、PyYAML；领域包按需调用 scikit-learn、Matplotlib、FFmpeg、Triton/PyTorch 或公开视频生成接口。GEPA、OpenEvolve、RD-Agent、FunClip、video-use 等在研究资料中出现，不代表当前已经接入。

项目代码采用 MIT 许可；第三方代码、模型、行情、视频和文献各有自己的条件。尤其默认量化行情及派生产物带有非商业等条件，不能因为代码是 MIT 就忽略资料要求。[详细来源与边界](docs/OPEN-SOURCE.zh-CN.md)。

公开视频生成接口在已成功两次后，对后续候选和一次短描述诊断返回 `error/null`。具体远端原因未知，不认定为额度不足，也不把没有生成的作品记作质量 0 分；原账本与派生核验分别保留。

继续开发请读[接手说明](docs/HANDOFF.zh-CN.md)；当前首发范围见[任务书](docs/GOAL-FIRST-RELEASE.zh-CN.md)。
