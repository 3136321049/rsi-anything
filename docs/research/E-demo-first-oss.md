# Demo 导向的开源选型复查

核查日期：2026-10-23。目标是确定最小接入能补足什么 Demo 效果。来源为当前代码和上游官方仓库；表中的接入难度与优先级是本项目的判断，尚未实际安装这些候选或验证兼容性。执行计划见 [Demo 计划](../DEMO-PLAN.zh-CN.md)。

## 1. 当前真正使用的组件

| 项目 | 当前代码里的关系 | 本次核查来源 |
|---|---|---|
| FFmpeg | 视频素材生成、裁切、拼接和渲染直接调用 `ffmpeg` / `ffprobe`；见 `templates/video-cut/rsi_init.py` 和 `judge/render.py` | [官方 GitHub 镜像](https://github.com/FFmpeg/FFmpeg)；官网介绍页本次抓取超时，改查官方镜像 |
| faster-whisper | 用户提供 `input.mp4` 时导入 `WhisperModel` 转写；该可选路径已写，尚无该路径的完整 Demo 验收记录 | [官方仓库](https://github.com/SYSTRAN/faster-whisper) |
| Git / PyYAML | 版本保存与配置解析；前者外部命令，后者是包的直接运行依赖 | 当前 `gitops.py`、`contract.py`、`pyproject.toml` |
| pytest | 本项目自动化测试所用开发依赖 | 当前 `tests/`、`pyproject.toml` |

代码提速、文案和提示词三个模板的循环及评分适配为当前仓库实现。Codex、Claude Code 等属于执行工具接入；使用其命令行不等于集成了额外的开源 RSI 框架。macOS 合成演示素材所用 `say` 是系统能力。

## 2. 最相关的上游及具体接法

### autoresearch：循环设计参考

官方描述为：助手修改小型模型训练代码，运行固定时长训练，比较结果，保留或丢弃后继续。当前 openRSI 借鉴这个任务循环的思路，但没有导入它的训练代码或运行其 GPU 实验。[官方项目](https://github.com/karpathy/autoresearch)

### FunClip：中文真实素材的候选入口

官方项目提供基于 FunASR 的视频转写、时间戳、按文本或说话人选段、字幕与模型辅助剪辑。最小接法是把一次转写的结果转换成现有 `judge/transcript.json`，仍让 openRSI 修改 `edit.json` 并调用现有渲染。需要单独安装模型环境和验证输出格式。[官方项目](https://github.com/modelscope/FunClip)

判断：若现有 faster-whisper 已满足第一段素材，无须马上增加依赖；中文转写效果成为瓶颈时优先试它。尚未接入。

### video-use：局部剪辑能力与展示方式参考

官方项目是供编程助手使用的 Skill 与辅助脚本集合，包含转写、剪辑决策表、字幕、音画处理与渲染。其默认转写依赖 ElevenLabs；直接复用不能假设所有步骤都已在当前环境就绪。[官方项目](https://github.com/browser-use/video-use)、[渲染脚本](https://github.com/browser-use/video-use/blob/main/helpers/render.py)

候选接法：把 `edit.json` 转成上游的剪辑决策文件，通过准备步骤调用其渲染器，输出路径仍由本项目约定。判断：已有 FFmpeg 能渲染，只有明确需要字幕、声音衔接或视觉处理时才引入局部能力。尚未接入。

### GEPA：提示词优化的可选对照

官方提供反思式文本优化，通过评分及运行反馈生成候选；`optimize_anything` 可接受文本候选和用户评价函数。可以把现有 `prompt.md` 和客服分类评价接进去，形成独立实验，再导入结果展示。[官方接口](https://github.com/gepa-ai/gepa#optimize_anything-beyond-prompts)

判断：当前主循环已经能改提示词。GEPA 的收益是增加另一种搜索策略和可比较的案例，不是首发跑通的必要条件。需要适配评价和结果格式，尚未接入。

### OpenEvolve：算法搜索扩展

官方项目提供面向程序的进化搜索、多个候选群体、用户评价和检查点机制。以后可对接 `search.py` 与评分程序，展示多个算法方向的探索。[官方项目](https://github.com/algorithmicsuperintelligence/openevolve)

判断：现有提速案例已经完整，首发重接一套搜索引擎的展示收益有限，留到需要并行候选或算法探索时再做。尚未接入。

### RD-Agent：金融与机器学习领域扩展

官方提供数据驱动研发流程，涵盖量化因子、模型和数据科学任务；官方当前安装说明以 Linux、Docker 等环境为基础。[官方项目](https://github.com/microsoft/RD-Agent)

判断：适合以后独立领域包。其环境与完整研发循环超过当前“先做一个可见 Demo”的最小需求，首发不引入。尚未接入。

### scikit-learn：轻量训练新 Demo

官方有手写数字识别示例，可作为小型分类任务起点。[官方示例](https://scikit-learn.org/stable/auto_examples/classification/plot_digits_classification.html)

本项目建议：固定数据划分和评价脚本，让助手改训练参数或预处理，保存正确率、错分样例和耗时。适合补充训练领域，不要求 GPU；尚未实现、未估算实测运行时长。

### diffusers：生成类后续候选

官方库覆盖图像、视频和音频生成。后续可通过固定生成管线，把提示词与参数作为可改产物，生成结果交给评委。[官方项目](https://github.com/huggingface/diffusers)

判断：环境、模型与生成成本需要单独评估；当前没有视频生成 Demo，暂不列为首发必做。

## 3. 选型结论

首发复用当前主循环和已有视频组件。新增组件必须直接解决一个可见问题：中文转写选 FunClip 作候选，字幕和视觉处理查 video-use，另一种提示词搜索再考虑 GEPA。项目名称出现在调研、原理参考、可选接口或真实运行里，分别注明关系。

本次不把旧调研中的星数、价格、速度估算或许可证分类当成当前结论。实际引入代码和模型时再核对所选版本的依赖与许可证，记录上游版本及致谢。

