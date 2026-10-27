# 实际组件、参考项目与资料来源

[English](OPEN-SOURCE.md)

更新日期：2026-10-24。这里按“程序实际调用”“公开资料输入”“仅作研究参考”区分。更细的版本、调用位置和核查凭证保存在各模板 README、冻结配置和实验目录中。

当前 13 个领域已完成真实多轮和独立验证；D07 仅有部分生成结果，后续服务错误原因未知；D15 未做 GPU 实测。组件是否写入模板、是否真实调用、是否完成实验分别说明，不互相替代。

本项目自行编写的代码按根目录 [LICENSE](../LICENSE) 提供。它不会改变第三方库、模型权重、原始资料、行情、视频或派生产物的使用条件。

## 程序实际使用

| 组件 | 本项目如何使用 | 位置与说明 |
|---|---|---|
| Python、Git、PyYAML | 配置、独立运行分支、评价程序和结果记录 | 主循环；[PyYAML](https://github.com/yaml/pyyaml) |
| pytest | 项目开发回归；测试中的模拟助手只验证程序行为 | `tests/`，不作为真实演示结果 |
| scikit-learn 1.6.1 | 读取 digits，固定划分、训练和预测 | [CPU 分类模板](../src/rsi_anything/templates/cpu-classifier/README.md)；调用现有学习算法，不复制其训练引擎 |
| Matplotlib 3.9.4 | 生成混淆矩阵、错例和回测曲线 | CPU 分类与量化模板；[官方项目](https://matplotlib.org/) |
| FFmpeg / ffprobe | 剪片、字幕、视频解码和基本媒体检查 | [剪辑模板](../src/rsi_anything/templates/video-cut/README.md)、[生成模板](../src/rsi_anything/templates/video-generation/README.md)；安装的 FFmpeg 构建与编解码器条件由上游提供 |
| faster-whisper | 用户没有现成转写时的可选转写入口 | [官方仓库](https://github.com/SYSTRAN/faster-whisper)；不是默认必需依赖，模型另行下载 |
| Mermaid | 经营分析的图表描述，HTML 可通过 CDN 渲染 | [经营分析模板](../src/rsi_anything/templates/business-report/README.md)；离线保留数值表 |
| Lightricks LTX Video Fast / Gradio | 向官方公开 Space 提交描述；本次初始与第 1 轮取得真实视频，后两轮未生成 | [官方 Space](https://huggingface.co/spaces/Lightricks/ltx-video-distilled)；一次短描述诊断仍为 `error/null`，具体原因未知。见[部分实测与来源](../examples/video-generation/README.md)；服务状态及使用条件独立于代码许可 |
| PyTorch 2.6.0、Triton 3.2.0 | GPU Softmax、数值比较、事件计时与小型模块对照 | [GPU 模板](../src/rsi_anything/templates/kernel-speed/README.md)；尚无本项目 GPU 实测。公开教程版权与许可保留在 [THIRD_PARTY.md](../src/rsi_anything/templates/kernel-speed/THIRD_PARTY.md) |

模型调用使用用户自己的个人 CLI 或 API。第三方助手、订阅服务和模型接口不是本仓库的一部分；“写了适配器”不表示所有账号、地区和版本都已验证。

## 默认资料与数据

| 用途 | 实际来源 | 使用与交付边界 |
|---|---|---|
| 代码修复、文案、写作手册、合同、讲义、日程 | 项目作者自编的合成业务材料、练习或安排 | 没有真实客户、患者、学生或公司资料；初稿是人工准备的任务起点，后续模型候选另留记录 |
| CPU 手写数字分类 | [scikit-learn digits 数据说明](https://scikit-learn.org/1.6/modules/generated/sklearn.datasets.load_digits.html) | 通过依赖读取公开教学数据，数据来源与描述以该页面及数据集说明为准，不能仅套用本项目 MIT |
| 视频剪辑案例 | [Wikimedia Commons 的肯尼迪就职演说](https://commons.wikimedia.org/wiki/File:John_F._Kennedy_Inauguration_Speech.ogv)与对应字幕 | 来源页标注 Public Domain Mark；本项目保存来源、节选起点与文件哈希，见 [source.json](../examples/video-cut/inputs/public-speech/source.json)。不代表人物或政策背书 |
| 经营分析 | [Apple FY2024 官方财务报表](https://www.apple.com/newsroom/pdfs/fy2024-q4/FY24_Q4_Consolidated_Financial_Statements.pdf)及新闻稿 | 提取固定财务事实并自行撰写分析，不重新分发整份报告；来源与全年口径冻结 |
| 量化回测 | [Binance 公共行情](https://github.com/binance/binance-public-data)、官方 Kline 接口 | 模板登记的 [CC BY-NC-SA 4.0 与 Binance Vision Dataset Terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md) 独立适用。默认数据、派生图表及分析保留署名、非商业和相同方式共享条件；不得以代码 MIT 宣称无限制商用。模板包只含下载器，不捆绑行情 |
| 资料综述 | 两篇认知研究的官方索引与 UNESCO 指南 | 使用作者自写的短摘要，保留作者、年份、链接、证据类型与局限；不是原文授权替代。见[模板来源](../src/rsi_anything/templates/literature-review/judge/sources.json) |
| 合同演练 | 自编合同与检查标准，参考 [business.gov.au 合同写作要素](https://business.gov.au/people/contractors/prepare-a-contract) | 不复制真实合同，不把来源司法辖区的法律套到本例，明确不构成法律意见 |
| 医学科普 | WHO 官方身体活动资料与指南摘要 | 只转述公开科普信息，保留来源与人群边界，不把文章当成个体医疗建议。实际读取范围见[案例说明](../examples/medical-explainer/README.md) |
| 百分比讲义 | 自编讲义与练习，概念参考 [OpenStax Prealgebra 2e](https://openstax.org/books/prealgebra-2e/pages/6-introduction-to-percents) | 没有复制教材题目或整章内容；替换为其他教材时另核对资料使用条件 |

默认回测属于同一段历史上的参数演示，不是投资建议。法律和医学模板仅处理边界清楚的合成演练或公众资料，不提供真实个案判断。商业宣传或再分发素材前，逐项检查具体资料条件；开源代码与公开可读资料不是同一回事。

[35 秒无声演示短片](../examples/showcase-media/openrsi-demo.mp4) 使用已保存的代码修复、写作手册、口播剪辑与分类错例，不是新生成的数据或优化结果。[demo-video.json](../examples/showcase-media/demo-video.json) 列出具体输入、视频 SHA256、35 秒时长、1280×720 尺寸与解码检查；其中历史演讲片段仍沿用原素材的公共领域来源说明。

## 参考过但没有接入的引擎

| 项目 | 参考点 | 当前关系 |
|---|---|---|
| [karpathy/autoresearch](https://github.com/karpathy/autoresearch) | 修改、评价、保留的简单循环 | 设计参考，没有导入其运行引擎 |
| [GEPA](https://github.com/gepa-ai/gepa) | 根据失败反馈优化文本，保留多种候选 | 后续可选对照，当前没有依赖 |
| [OpenEvolve](https://github.com/algorithmicsuperintelligence/openevolve) | 算法候选搜索与进化 | 后续候选，当前主循环仍是单候选逐轮尝试 |
| [RD-Agent](https://github.com/microsoft/RD-Agent) | 数据与模型研发流程 | 研究参考，量化模板没有调用它或 Qlib |
| [FunClip](https://github.com/modelscope/FunClip)、[video-use](https://github.com/browser-use/video-use) | 用转写与剪辑决策表连接文字和视频 | 参考思路，现有剪辑由自写脚本与 FFmpeg 执行 |
| [KernelBench](https://github.com/ScalingIntelligence/KernelBench) | 将数值正确性和性能分别检查 | GPU 评价设计参考，未导入其题目或数据 |
| ComfyUI、diffusers、OR-Tools、FSRS 等 | 研究中的潜在领域工具 | 当前模板未调用，不作为首发依赖宣传 |

`docs/research/` 保存选型调查，涉及的版本、数量、费用和接口属于当时资料，不是当前接入清单。需要新组件时先核官方来源，解决具体案例的问题，再记录实际调用位置与适用条件。
