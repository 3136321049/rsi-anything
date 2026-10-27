# D07：真实视频生成，部分实测

[English](README.en.md)

本次包含初始生成和 3 轮模型修改：初始与第 1 轮取得真实视频，第 2、3 轮在服务已受理后收到 `event: error / data: null`，没有视频可以评价。当前保留第 1 轮成片与全部输入，按资源例外列为**部分实测**，不计作完整多轮验收。

| 版本 | 实际结果 | 可用质量分 | 视频 |
|---|---|---:|---|
| 初始 | 服务生成成功 | 60.5 | 1.90 秒，704×512，H.264，无音轨 |
| 第 1 轮 | 服务生成成功，保留 | 61.0 | 1.90 秒，704×512，H.264，无音轨 |
| 第 2 轮 | 服务返回错误，没有作品 | 未知 | 无 |
| 第 3 轮 | 服务返回错误，没有作品 | 未知 | 无 |

写手和评委均显式请求个人 Codex CLI 的 `gpt-6.1-sol`，服务端实际型号没有返回，仍记 `null`。生成服务为 Lightricks 官方公开 [LTX Video Fast](https://huggingface.co/spaces/Lightricks/ltx-video-distilled)；上游声明 LTX 0.9.8 13B distilled，不能把这个声明当成运行时额外返回的模型证明。模型评分只覆盖抽取的静帧，未据此评价完整运动或声音。

第 1 轮主要强化蒸汽、侧后方光线和背景对比。评委发现蒸汽出现了，但偏浓，杯底和杯柄也存在裁切，最终仅比初始高 0.5 分。这是该次评价的结果，不代表可靠的整体质量提升。

[初始视频](runs/20261024-003656-warm-morning-product-video/artifacts/baseline/files/out/video.mp4) · [最终保留视频](runs/20261024-003656-warm-morning-product-video/artifacts/final/files/out/video.mp4) · [最终生成参数](runs/20261024-003656-warm-morning-product-video/artifacts/final/files/generation.json) · [可播放预览](runs/20261024-003656-warm-morning-product-video/artifacts/final/files/out/preview.html) · [独立验证](runs/20261024-003656-warm-morning-product-video/verification.json)

## 服务错误核对

2026-10-24 重新核对 [官方实现](https://huggingface.co/spaces/Lightricks/ltx-video-distilled/blob/8a42e93469c66b62d794b83a4233f5fc8439e2b5/app.py) 与公开 `/config`。服务仍使用 Gradio 5.42.0，13 个输入标签和顺序与原请求一致，`show_error` 为 false。当前 `app.py` 未见按字符数拒绝提示词的逻辑；成功第 1 轮描述 868 字符，失败两轮分别为 981、1159 字符，均通过本地输入校验。接口顺序没有发现变化，但模型内部限制或远端异常不能仅凭公开应用代码排除。

只追加了**一次**匿名免费诊断请求，完全复用先前成功基线的短描述（24 字符）、反向描述、seed=42、704×512 和两秒参数。提交与事件流都返回 HTTP 200，事件 `4413c88e602948a19b642ddeae2b756f` 仍为 `error/null`。因此“仅因本次描述变长而失败”得不到支持；服务没有公开具体异常，**无法确认是额度、GPU 资源、服务内部错误或其他原因**。没有切换账号、IP、付费服务，也没有继续重试。

[唯一诊断请求与结果](probes/2026-10-24-service-diagnosis/receipt.json) · [服务配置与上游版本](probes/2026-10-24-service-diagnosis/service.json) · [诊断输入](probes/2026-10-24-service-diagnosis/request.json)

## 原记录与派生核验

原账本将准备阶段失败编码为 `REVERT / 0`，这些原字节保持不变。这里的 0 不代表作品质量下降，因为对应轮次没有生成视频。[派生结果核验](runs/20261024-003656-warm-morning-product-video/outcome-audit.json) 逐项列出原状态、原分数、服务事件和有效解释：第 2、3 轮为 `JUDGE_FAIL`、质量未知、质量分为空。统一展示页使用这一解释，原始失败仍可追溯。

已用 FFmpeg 完整解码初始、第 1 轮和最终视频，核对尺寸、时长、文件哈希与来源回执；最终文件与第 1 轮逐字节相同。各轮 `generation.json` 与实际请求的描述、反向描述和种子一致。`verification.json` 只确认这些已保存证据有效，明确写有 `multi_round_demo_complete: false`。

[原始账本](runs/20261024-003656-warm-morning-product-video/ledger.jsonl) · [原始报告（含旧失败编码）](runs/20261024-003656-warm-morning-product-video/report.html) · [来源事件与原视频地址](runs/20261024-003656-warm-morning-product-video/source-receipts.json)

## 继续实测的入口

服务恢复或有另行获准的兼容免费资源后，按[模板说明](../../src/rsi_anything/templates/video-generation/README.md) 检查接口，再另开一条实验。不要覆盖这次的成功视频和失败记录。

```bash
python scripts/run_demo.py video-generation --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

`RSI_VIDEO_ENDPOINT` 可设置兼容接口，`RSI_VIDEO_CACHE` 保存已受理事件和成片，避免不知情地重复提交。调用会向公开服务提交描述；不要放个人敏感或公司资料。本项目没有自动付费回退。
