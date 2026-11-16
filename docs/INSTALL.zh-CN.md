# 安装、个人账号与运行

[English](INSTALL.md)

本文对应 `0.3.0.dev0`，建议 Python 3.11。代码声明支持 Python 3.9+；视频、训练、GPU 和各助手 CLI 另有依赖。软件包没有发布到 PyPI，请从网站下载安装包，或在源码目录安装。

当前有 14 个领域的完整多轮与独立验证，包含写作手册、合同演练和讲义。D07 保留已生成视频及服务受限的部分实测，D15 保留无 GPU 探测；两项资源例外不算完整实测。先看[35 秒真实产物短片](../examples/showcase-media/openrsi-demo.mp4)或[案例状态](DEMO-PLAN.md)，再选择要运行的模板。

## 从网站安装

在新的虚拟环境中安装网站上的 wheel：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install https://www.riseai.top/darwin/dist/rsi_anything-0.3.0.dev0-py3-none-any.whl
rsi --version
rsi init
```

Windows 的激活入口为 `.venv\Scripts\Activate.ps1`。安装依赖、运行 `rsi` 和执行评分必须使用同一个 Python。

## 安装当前源码

在已拿到的项目根目录执行：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
rsi --version
rsi init
```

已有可用隔离环境可以直接复用；虚拟环境是本机环境，不随仓库交付。

## 使用本地 wheel

源码根目录构建：

```bash
python -m pip install build
python -m build --wheel
```

在另一个干净虚拟环境中安装实际生成的文件，例如：

```bash
python -m pip install /path/to/rsi_anything-0.3.0.dev0-py3-none-any.whl
rsi --version
rsi init
```

当前交付的 `dist/rsi_anything-0.3.0.dev0-py3-none-any.whl` 已在使用临时主目录的干净环境中离线安装通过：18 个模板与源码逐字节一致；初始化、固定评分、测试代理运行、导出、`rsi plugins`、`rsi setup --check`、`rsi new` 测试类任务以及画图模板的断网截图都通过。见 [包内容与 SHA256](../release/build-validation-0.3.0.dev0.json)、[安装回执](../release/install-receipt-0.3.0.dev0.json)；首发 `0.2.0.dev0` 的回执仍在同一目录。安装测试没有模型调用，不作为新增真实实验。源码级测试和 `scripts/` 不属于 wheel 中的命令行包。

## 明确使用哪个助手与模型

`rsi agents` 列出适配器和检测结果。当前已有十种 CLI 适配，完整案例主要由个人 Codex 实跑，其余适配不代表已逐家验收。最直接的配置是固定执行助手和请求型号：

```bash
rsi run --agent codex --model gpt-6.1-sol --rounds 3
```

模型名是本轮已用过的示例；账号不支持时换成自己的可用型号。文本模型评审也应明确固定，例如 `--jury cli:codex:gpt-6.1-sol`。也可以在运行前设置 `RSI_AGENT=codex`、`RSI_JURY=cli:codex:gpt-6.1-sol`，不要依赖 `auto` 做严格复现。

模型引用有两种：`cli:<助手>:<型号>` 复用个人 CLI 登录；`<供应商>:<型号>` 走配置好的个人 API，例如 `deepseek:deepseek-chat`。API 密钥只放环境变量，不写进 `rsi.yaml`、仓库或报告。已有后端与变量名以 `src/rsi_anything/llm.py` 为准；当前支持 OpenAI、Anthropic、Gemini、OpenRouter、DeepSeek、Qwen、Kimi、GLM、Doubao、SiliconFlow、MiniMax 和 Ollama 等适配。

只做个人项目时使用个人账号与公开或获准素材，不继承其他工作的服务配置。请求型号、服务端实际返回型号、调用量和美元费用分别记录；没有返回的字段保持未知，不能将请求型号当成服务端确认，也不能将未知费用当成零。

### Codex CLI 设置

先运行 `codex --version`，确认 CLI 能识别当前账号型号。本项目通过以下环境变量配置适配器：

| 变量 | 用途 |
|---|---|
| `RSI_CODEX_BIN` | 指定希望使用的 Codex CLI 可执行文件；在启动 `rsi` 前设置 |
| `RSI_CODEX_ISOLATED=1` | 使用新版 CLI 的 `--ignore-user-config`、`--ignore-rules` 等参数，避免继承个人全局配置和其他项目说明 |
| `RSI_CODEX_REASONING_EFFORT=medium` | 显式固定思考强度；当前代码接受 `low`、`medium`、`high`、`xhigh` |

隔离参数要求较新的 CLI。出现 `unexpected argument` 时，先检查实际执行路径和 `exec --help`，使用支持这些参数的个人 CLI；不要把参数错误当成模型失败，也不要自动替换成更大权限的运行方式。Claude 适配器会先检查登录状态，未登录时在发送任务前停止。

提示词与讲义模板还需固定 `RSI_TASK_MODEL`；写作手册模板固定 `RSI_WRITER_MODEL`。这些是“被优化方法实际调用的模型”，与负责改文件的助手、评分的评委是不同职责，可以使用同一账号，但要各自记录。

## 首个完整案例

从源码目录初始化到相邻目录，避免把试验文件混进开发仓库：

```bash
rsi init code-repair ../open-rsi-demo
cd ../open-rsi-demo
rsi check
rsi run --agent codex --model gpt-6.1-sol --rounds 3
rsi status
rsi report
rsi export --to ../open-rsi-result
```

`rsi init` 在新目录创建 Git 仓库和初始提交；若目录已经处在别的 Git 仓库中，需要先提交模板文件。若首次提交因为缺少 Git 身份失败，在 Demo 目录配置自己的公开身份，再执行 `git add -A` 和 `git commit`；不要借用其他人的提交身份。

`rsi check` 会执行真实评分，包括模板里的模型调用、训练或视频生成。代码修复示例评分只跑本地固定测试；不要在昂贵模板上把 `check` 当成免费的语法检查。配置里的 `budget.rounds`、`budget.minutes`、`budget.stagnation` 控制循环；`agent.timeout` 与 `judge.timeout` 控制单次执行。总时间在轮次之间检查，不是精确的费用上限。

## 可选依赖与资源

| 模板 | 需要什么 | 当前接法 |
|---|---|---|
| `cpu-classifier` | scikit-learn、Matplotlib，CPU 即可 | 在模板目录 `python -m pip install -r requirements.txt`，固定版本与原实验一致 |
| `quant-backtest` | Matplotlib，初始化时访问公开行情接口 | 同样安装 `requirements.txt`；行情下载失败会停止，不替换成合成数据 |
| `video-cut` | FFmpeg 与 ffprobe；已有视频或语音合成工具 | macOS 可用 Homebrew 安装 FFmpeg；Linux 用系统包管理器。默认合成素材还需 `say` 或 `espeak-ng` |
| `video-generation` | FFmpeg/ffprobe、可用的官方公开 Space、能看图的评委 | 已有初始与第 1 轮成片；后续请求及一次短描述诊断返回 `error/null`，具体原因未知。服务恢复或取得获准资源后另开实验，不自动付费回退 |
| `kernel-speed` | 已授权个人 Linux NVIDIA GPU、兼容驱动、PyTorch/Triton | 先执行 `python judge/check.py --probe`；具体硬件范围与版本见模板 README |

源码开发者也可用 `python -m pip install -e '.[dev,training]'` 安装较宽版本范围的训练依赖；若要复现已保存案例，使用模板 `requirements.txt` 中的固定版本。没有个人 GPU 时不安装 CUDA 大包、不租用设备，保留探测记录和空的性能结果。D15 按当前资源例外交付待补实测入口。

视频生成的 `RSI_VIDEO_CACHE` 应指向持久目录；默认使用用户缓存。请求已受理时复用事件编号和结果，提交结果不确定时停止自动重发。服务没有返回作品时，质量保持未知；这次旧账本的失败编码与[派生核验](../examples/video-generation/runs/20261024-003656-warm-morning-product-video/outcome-audit.json)分开保存，不能把原始 0 分解释成质量下降。原片、行情、模型和其他素材的使用条件见[来源说明](OPEN-SOURCE.zh-CN.md)。

## 看结果、续跑和展示

`rsi report` 打印报告路径。运行目录保存初始、逐轮和最终作品；`rsi export --to <目录>` 会复制这些作品与配置、账本、补丁。媒体和图片按原字节保存，文本中的本机路径会替换；原始助手长日志只有加 `--with-logs` 才导出。外部素材链接不会自动完整打包，分享前按模板说明另保存原素材和来源。

中断后先读 `run.json`、账本和最后一轮目录，确认没有同一实验仍在运行，然后执行 `rsi run --resume <运行号>`。配置改变需开新实验，不能用续跑混用新旧规则。已保存的基线和最好产物会复用，部分轮次明确记为中断；不要手工把失败改成成功。

在源码根目录：

```bash
python scripts/build_showcase.py
python -m http.server 8765 --bind 127.0.0.1
```

打开 `http://127.0.0.1:8765/examples/index.html`。这是本地预览，不会发布网站。

不运行模型也能查看[35 秒演示](../examples/showcase-media/openrsi-demo.mp4)及[来源和解码凭证](../examples/showcase-media/demo-video.json)。这些媒体和 `examples/` 保留在源码交付中，不属于 CLI wheel；只安装 wheel 不会自动得到完整案例集合。

## 常见问题

| 表现 | 优先检查 |
|---|---|
| `rsi: command not found` 或包无法导入 | 虚拟环境是否激活；安装与执行是否同一解释器 |
| 无法评分初始状态 | 初始评分错误与 `out/error.json`；缺依赖、未登录、接口失败不等于作品质量差 |
| 提示配置未提交或不是 Git 项目 | 模板文件、评分资料和 `rsi.yaml` 是否已提交 |
| CLI 型号不支持、隔离参数不认识 | 实际 CLI 路径、版本、个人账号能用的型号 |
| `RSI_TASK_MODEL` 未设置 | 讲义必须显式指定；提示词实验也应固定任务模型 |
| 视频没有生成或事件流中断 | `out/error.json`、持久缓存的 `state.json`、原事件编号；不重复乱发请求 |
| 模型说修改了但正式轮次无变化 | 允许修改的文件是否实际改变；助手可能在内部试验后恢复了原文件 |
| 分数更高却拒绝 | 必要检查、最小提升幅度，以及文本的新旧比较结果 |
| 图表 HTML 离线没有图形 | 经营报告 Mermaid 需联网；同页数字表仍可读，或打开 `.mmd` 文件 |

排障先看当前源码与原始运行目录，文档中的具体工具参数可能随外部 CLI 更新。
