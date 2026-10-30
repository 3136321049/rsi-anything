# DARWIN · Open RSI

**给 AI 一个目标，只留下真正变好的版本。**

[网站](https://www.riseai.top/darwin/zh/) · [English](README.md) · [全部实验](https://www.riseai.top/darwin/zh/cases/) · [开始使用](https://www.riseai.top/darwin/zh/start/)

DARWIN 是 RiseAI 的进化实验室，底层是 Open RSI 工具包（`rsi-anything`）。编程助手一轮轮修改真实作品：代码、提示词、模型配置、文章、视频剪辑。每次尝试都由固定的评判方式检查，可能是测试、指标或模型评委。更好的版本成为 Git 提交，被拒绝和失败的尝试也一起保存。你可以看到初稿、每一次尝试、最终作品，以及每个决定的理由。

当前开发版本为 `0.3.0.dev0`：**16 个领域、18 个模板，其中 14 个领域已有完整多轮记录**和独立验证。另外两个领域属于资源例外，不计入完整数量：视频生成因公开生成服务停止响应只完成部分实测；GPU 算子因缺少个人 GPU，目前只有模板和环境探测。

## 先看几个真实案例

| 案例 | 这次具体发生了什么 | 记录 |
|---|---|---|
| 模糊搜索提速 | 连续三轮保留：1× → 4.45× → 17.83× → 27.45×，每次计时前都先核对结果 | [代码实验室](https://www.riseai.top/darwin/zh/labs/code/) |
| Python 记账修复 | 固定测试从 6/15 依次修到 9/15、12/15、15/15 | [源码与测试](examples/code-repair/README.md) |
| CPU 数字分类 | 验证集正确率从 46.889% 到 99.333%；后两轮没有正式新改动 | [模型实验室](https://www.riseai.top/darwin/zh/labs/experiments/) |
| 演讲剪成短片 | 从 18.5 分提升并保留 75.5 分版本；之后一版 77 分，但新旧两次直接比较都没赢，被拒绝 | [视频实验室](https://www.riseai.top/darwin/zh/labs/video/) |
| 客服提示词 | 三个候选都没有提升，保留原提示词（开发集 89.6%，留出集 82.8%） | [提示词与错例](examples/prompt-opt/README.md) |
| 示例合同 | 保留 91.5 分讨论稿，定位 7/7 类问题；较弱候选照常保留 | [合同稿与复核](examples/contract-review/README.md) |

这些结果属于对应任务与评价条件，不是跨任务的能力保证。固定验证集被反复用于调参，不能当作独立的泛化证据；模型评分也不是专家认证。停滞、拒绝和失败都完整保留。

## 快速开始

需要 Python 3.11（声明支持 3.9+）、Git，以及一个已登录的编程助手。从网站下载安装包，装进新的虚拟环境：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install https://www.riseai.top/darwin/dist/rsi_anything-0.3.0.dev0-py3-none-any.whl
rsi setup
rsi init code-repair my-first-run
cd my-first-run
rsi check
rsi run --agent codex --model YOUR_MODEL --rounds 3
rsi report
rsi export --to ../my-first-result
```

已有源码时改用 `python -m pip install -e '.[dev]'`。软件包没有发布到 PyPI。

`rsi setup` 检查 Python、Git、已登录的编程助手以及可选的浏览器和 FFmpeg，建议由谁修改、由谁评分（有两家时分开），并可安装 `/rsi` 技能。想改进自己的东西而不是模板，运行 `rsi new`：它会问清什么要变好（一段文字、一幅画或一个网页、带测试的代码，或者命令打印的任意数字），然后写出照原样就能运行的任务，见[扩展一个自己的任务](docs/EXTENDING.zh-CN.md)。

`rsi check` 会真实执行评分；含模型评委或视频生成的模板会产生实际调用。代码修复只跑本地测试，适合作为第一个任务。`rsi init` 会为任务创建 Git 仓库；首次提交失败时，请先配置 Git 身份。CLI 版本、可选依赖和 API 配置见[安装说明](docs/INSTALL.zh-CN.md)。

用 `rsi run --live`（或在另一个终端运行 `rsi watch`）可以在本地页面实时查看进化：分数曲线，以及每个版本和当时最好版本的并排对比。`rsi share --to run.html` 把同样的页面存成一个自带图片、去掉本机路径的单文件。

## 有哪些模板

运行 `rsi init` 可以列出全部模板。每个模板都带有输入、初始作品、评价程序、输出位置，以及替换输入的说明。

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
| D11 示例合同 | `contract-review` | 虚构合同的问题定位与修改建议 |
| D12 医学科普 | `medical-explainer` | 基于给定 WHO 资料的公众表达 |
| D13 学习教育 | `lesson-builder` | 讲义与例题解释，由学生模型检验 |
| D14 生活规划 | `weekly-planner` | 一周日程 |
| D15 GPU 算子 | `kernel-speed` | Softmax 实现与启动参数 |
| 视觉（新增） | `svg-drawing`、`landing-page` | 一幅 SVG 画，或一页网站，由能看图的评委按截图评分 |

两个视觉模板是源码中新增的，还没有进入可下载的安装包，实跑见[鹈鹕](examples/svg-drawing/README.md)和[落地页](examples/landing-page/README.md)案例。**模板存在不等于完成实跑。** D01–D06、D08–D14 已完成多轮与独立验证；D07 和 D15 是上面说明的资源例外。空的 GPU 结果和失败的生成请求不会被模拟，也不计作完成。

## 多轮如何运行

`rsi.yaml` 定义目标、可改文件、冻结的评分资料、助手与预算。每轮从当前最好的提交出发，只有允许范围内的改动才会成为候选，并在带原始评分资料的全新副本里接受评价。

先过必要检查，再比较是否达到提升幅度；文字任务还可以把新旧版本正反顺序各比一次。通过的候选成为 `rsi/<运行号>` 分支上的真实提交，被拒绝和失败的尝试保留记录。`rsi run --resume <运行号>` 可以恢复同一配置的中断运行；改了配置就开始新实验。

这套流程改进的是任务作品和可复用手册，不会训练助手的模型权重，也没有证明通用能力会自我提升。评分代码在本机执行，分开的工作目录不是强安全沙箱，只运行自己理解的模板。

## 模型与资源

- 执行助手：`rsi run --agent codex --model <型号>`。项目也为 Claude Code、Cursor、Gemini、Qwen Code、Kimi、OpenCode、Copilot、CodeBuddy 和 Qoder 准备了适配；这里的完整运行使用 Codex，并非每个适配都做过端到端测试。
- 评委：`--jury cli:codex:<型号>`，或受支持的 API 写法，例如 `deepseek:deepseek-chat`。
- 任务模型：提示词优化和讲义练习用 `RSI_TASK_MODEL`；写作手册的写手模型用 `RSI_WRITER_MODEL`。

请求的型号、服务端返回的型号、用量和费用分别记录，缺失的值保持未知。CPU 训练和回测使用各自模板的 `requirements.txt`；视频任务需要 FFmpeg 和 ffprobe；GPU 算子需要模板说明中的硬件，CPU 或 MPS 的测量不能代替 GPU 结果。

## 网站

DARWIN 网站用中英文回放已保存的运行，浏览时不调用任何模型。在源码目录本地生成：

```bash
python scripts/build_site.py
python -m http.server 8765 --bind 127.0.0.1 --directory build/site
```

打开 `http://127.0.0.1:8765/`（中文版在 `/zh/`）。结构与翻译流程见[网站说明](web/README.md)。`python scripts/build_showcase.py` 仍会生成旧版单文件浏览页 `examples/index.html`，供本地查看。

## 来源与边界

主循环由本项目实现，基于 Git、Python 和 PyYAML；各领域按需使用 scikit-learn、Matplotlib、FFmpeg、PyTorch/Triton 和公开视频生成服务。GEPA、OpenEvolve、RD-Agent、FunClip、video-use 是研究参考，没有作为引擎接入。

项目代码采用 MIT 许可；第三方软件、模型、数据、视频和文献保留各自的条件，尤其默认回测行情及其派生产物仅限非商业使用。合同和医学示例是虚构练习或给定的公开资料，不是法律或医疗建议；回测描述的是历史模拟，不代表未来收益。详见[开源组件与资料来源](docs/OPEN-SOURCE.zh-CN.md)。

参与开发请先读 [AGENTS.md](AGENTS.md)、[当前架构](docs/PLAN.zh-CN.md) 和[扩展模板](docs/EXTENDING.zh-CN.md)；换电脑继续开发见[跨电脑协作](docs/COLLABORATION.zh-CN.md)和[接手说明](docs/HANDOFF.zh-CN.md)。
