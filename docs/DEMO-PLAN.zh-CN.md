# 首发 Demo 与当前证据

更新日期：2026-10-24。首发提供 15 个领域、16 个模板，文案领域分别演示单篇改写和可复用写作手册。本文是案例入口；实时验收和下一步以[执行表](GOAL-PROGRESS.zh-CN.md)为准，完整范围及资源例外以[任务书](GOAL-FIRST-RELEASE.zh-CN.md)为准。

当前为 **13 个领域完整多轮，D07 部分实测但服务受限，D15 待 GPU 实测**。D05 的手册、新简报结果以及 D11、D13 的独立验证均已收齐。[35 秒真实产物短片](../examples/showcase-media/openrsi-demo.mp4)可直接观看，[媒体验证与来源](../examples/showcase-media/demo-video.json)列出所用的实际作品。

展示以作品为中心：先看任务和初稿，再看几次实际尝试、保留或拒绝的原因，以及最终产物。分数用于解释选择，不把单例分数写成普遍能力。真实迭代可以停滞或失败，不要求每轮上涨。

## 领域入口

| 编号 | 模板 | 状态与当前结果 | 入口 |
|---|---|---|---|
| D01 | `code-speed` | 已验收；历史三轮 1→4.45→17.83→27.45 倍，源码版本已重建复核 | [历史记录](../examples/code-speed/runs/2026-10-21-codex-3-rounds/NOTES.md) |
| D02 | `code-repair` | 已验收；三轮固定测试 6/15→15/15 | [完整案例](../examples/code-repair/README.md) |
| D03 | `prompt-opt` | 已验收；三轮均未提升，保留开发 89.6%、留出 82.8% 的原提示词 | [完整案例及历史部分实验](../examples/prompt-opt/README.md) |
| D04 | `cpu-classifier` | 已验收；固定验证集 46.889%→99.333%，后两轮无正式改动 | [配置、混淆矩阵和错例](../examples/cpu-classifier/README.md) |
| D05 | `copywriting`、`writing-guide` | 已验收；单篇五轮 16.5→96；手册五轮保留 74.5 分，新简报 69→77.5 | [单篇原记录](../examples/copywriting/runs/2026-10-21-codex-5-rounds/NOTES.md) · [手册与新简报](../examples/writing-guide/README.md) |
| D06 | `video-cut` | 已验收；真实口播四轮，初剪、候选、最终视频与字幕均保存 | [完整案例](../examples/video-cut/README.md) |
| D07 | `video-generation` | 部分实测、服务受限；初始 60.5、第 1 轮 61 有视频，后两轮质量未知 | [成功视频、失败与派生核验](../examples/video-generation/README.md) |
| D08 | `business-report` | 已验收；三轮最终保留 74 分稿，数字和图表已核对 | [完整案例](../examples/business-report/README.md) |
| D09 | `quant-backtest` | 已验收；三轮收益 27.722%→91.124%，回撤 13.437%→28.0442%，保留持有对照 | [完整案例与数据条件](../examples/quant-backtest/README.md) |
| D10 | `literature-review` | 已验收；三轮综述 61→91.5，来源映射已复核 | [完整案例](../examples/literature-review/README.md) |
| D11 | `contract-review` | 已验收；三轮最终保留 91.5 分稿，有效定位 7/7 类问题 | [合同讨论稿与独立核验](../examples/contract-review/README.md) |
| D12 | `medical-explainer` | 已验收；三轮科普 58.5→80，固定来源与用途边界保留 | [完整案例](../examples/medical-explainer/README.md) |
| D13 | `lesson-builder` | 已验收；三轮从 2/10 到 10/10 有依据且答对，原始作答已独立重放 | [讲义、答题与验证](../examples/lesson-builder/README.md) |
| D14 | `weekly-planner` | 已验收；三轮 38.08→100，最终十四项活动无冲突 | [完整案例](../examples/weekly-planner/README.md) |
| D15 | `kernel-speed` | 待 GPU 实测、资源例外；模板与环境探测已验证，性能结果为空 | [模板与待补入口](../src/rsi_anything/templates/kernel-speed/README.md) |

原始 `run.json`、账本、候选作品和独立验证记录共同决定验收状态。D07 与 D15 按资源例外单列，不计完整多轮数量；D07 原始 0 分属于旧服务失败编码，派生视图保持质量未知，不用来画质量下降曲线。

## 展示结构

从源码根目录运行 `python scripts/build_showcase.py`，再启动本地 HTTP 服务，打开 `examples/index.html`。集合页提供领域、运行、左右版本与文件选择，支持文字差异、图表和视频播放。公开分享前核对资料条件，尤其量化行情与派生分析的非商业条件。

主展示优先选择普通读者能直接比较的片段与文章。工程修复、代码提速和 CPU 分类提供程序指标；提示词的未提升案例用于说明系统也会拒绝候选。模型评分曲线必须与作品一起呈现，不能独立当成业务效果。

## 当前交付与后续入口

1. 13 个完整领域的正式结果与验证已经保存，包含 D05 的单篇与写作手册、D11 合同和 D13 讲义。
2. 案例集合与 35 秒展示剪辑已经生成。页面已做过桌面浏览器功能检查；后续访问受限后的改动只做本地生成器、语法和链接检查，保留先前截图。
3. 使用已验证的本地 wheel 和完整案例包交付；16 个模板与干净安装路径已检查，安装、扩展、来源与接手说明已同步。随后按个人输入制作主展示，发布按明确授权执行。
4. D07 服务恢复或另有获准的免费资源、D15 有合适个人 GPU 后，另开实测记录，不覆盖当前资源例外或购买资源。部署、发帖和正式发布按明确授权执行。

高级搜索、强沙箱和研究级评委校准保留为后续方向，不作为已有正常案例交付的前置条件。
