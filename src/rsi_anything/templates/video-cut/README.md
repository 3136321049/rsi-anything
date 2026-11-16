# Talking-head speech editing

[简体中文](README.zh-CN.md)

Each round, the AI changes only the sentence IDs and their order in `edit.json`, and FFmpeg cuts the matching video and audio into a 40–75 second short clip. Scoring checks duration, segment count and how the content is organized; it isn't a full audiovisual quality assessment. Every kept and rejected cut is exported with its round, along with its text and subtitles.

By default, `rsi init video-cut video-demo` builds development footage with local speech synthesis and title cards. It needs FFmpeg and either macOS `say` or Linux `espeak-ng`.

To use your own video, set these before initializing:

```bash
export RSI_VIDEO_INPUT=/path/to/input.mp4
export RSI_VIDEO_TRANSCRIPT=/path/to/sentences.json
export RSI_VIDEO_BRIEF=/path/to/brief.md
rsi init video-cut video-demo
cd video-demo
rsi run --agent codex --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5
```

`sentences.json` is a list of entries with `id`, `start`, `end` (in seconds) and `text`. You can convert existing subtitles and check them, or leave out `RSI_VIDEO_TRANSCRIPT` and install `faster-whisper` to transcribe automatically. In `brief.md`, state the target audience and the information you want to keep. You can point `RSI_VIDEO_SOURCE_INFO` at a JSON file with the public source and license notes; it is frozen along with the rest at initialization.

After replacing footage, start a new experiment; don't change the sentence timeline of a run in progress. External source footage isn't repackaged into every round's report. To share, save the source footage and its provenance separately, then export the whole experiment record. The footage and current results for a real talking-head speech case are in `examples/video-cut/` in the repository.

The template actually calls [FFmpeg](https://github.com/FFmpeg/FFmpeg); automatic transcription can optionally use [faster-whisper](https://github.com/SYSTRAN/faster-whisper). No other editing framework is integrated at present.
