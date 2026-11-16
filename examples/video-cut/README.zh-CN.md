# D06：真实口播剪辑

[English](README.md)

本例使用 Wikimedia Commons 标注 Public Domain Mark 的1961年肯尼迪就职演说连续节选；原素材、字幕片段和来源信息位于 `inputs/public-speech/`。用于展示历史讲话选段与重排，不代表当代政策观点或人物背书。

完整实验：`runs/20261024-002228-talk-highlight/`。基线18.5分，第一轮75.5分保留，后续68、77、75分均被拒绝，其中77分未赢过新旧对比。连续三轮无提升后正常停止，共4轮。评分由同请求型号模型判断剪后文字，未评价完整视听质量。

`artifacts/baseline/files/out/cut.mp4`、`rounds/rNNN/artifacts/files/out/cut.mp4`、`artifacts/final/files/out/cut.mp4` 是真实本地FFmpeg渲染的可播放视频，各有对应文字和SRT字幕。`verification.json` 保存逐版解码、时长和音轨检查。

复现：先安装FFmpeg，登录个人Codex，明确设置 `RSI_CODEX_BIN`（需要时），然后在仓库根目录：

```bash
export RSI_VIDEO_INPUT="$PWD/examples/video-cut/inputs/public-speech/input.mp4"
export RSI_VIDEO_TRANSCRIPT="$PWD/examples/video-cut/inputs/public-speech/sentences.json"
export RSI_VIDEO_BRIEF="$PWD/examples/video-cut/inputs/public-speech/brief.md"
export RSI_VIDEO_SOURCE_INFO="$PWD/examples/video-cut/inputs/public-speech/source.json"
python scripts/run_demo.py video-cut --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5 --minutes 60 --codex-isolated
```

选择初稿、中间候选、最终成片直接比较；被拒候选同样保留。设置新的运行目录，重跑不会覆盖历史记录。替换用户素材的办法见模板README。
