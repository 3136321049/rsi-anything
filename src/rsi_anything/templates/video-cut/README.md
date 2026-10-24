# 口播剪辑

AI 每轮只修改 `edit.json` 的句子编号和顺序，FFmpeg 将对应画面和声音剪成40–75秒短片。评分检查时长、片段数和内容组织；不是完整视听质量评价。所有保留和拒绝的成片会随轮次导出，另有文字与字幕。

默认 `rsi init video-cut video-demo` 使用本机语音合成与字卡生成开发素材，需要 FFmpeg 和 macOS `say` 或 Linux `espeak-ng`。

使用自己的视频时，在初始化前设置：

```bash
export RSI_VIDEO_INPUT=/path/to/input.mp4
export RSI_VIDEO_TRANSCRIPT=/path/to/sentences.json
export RSI_VIDEO_BRIEF=/path/to/brief.md
rsi init video-cut video-demo
cd video-demo
rsi run --agent codex --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5
```

`sentences.json` 是含 `id`、`start`、`end`（秒）、`text` 的列表。可使用已有字幕转换并核对，也可省略 `RSI_VIDEO_TRANSCRIPT` 并安装 `faster-whisper` 自动转写。`brief.md` 写清目标受众和想保留的信息。可用 `RSI_VIDEO_SOURCE_INFO` 指向含公开来源与授权说明的 JSON，初始化时会一并冻结。

替换素材后新开实验，不改变正在运行的句子时间线。外部原素材不会重复打包到每轮报告，分享时另保存原素材及来源，再整体导出实验记录。真实口播案例的素材入口和当前结果见仓库 `examples/video-cut/`。

实际调用 [FFmpeg](https://github.com/FFmpeg/FFmpeg)；自动转写可选 [faster-whisper](https://github.com/SYSTRAN/faster-whisper)。当前没有接入其他剪辑框架。
