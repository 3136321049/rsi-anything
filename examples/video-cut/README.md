# D06: Cutting a real talking-head speech

[简体中文](README.zh-CN.md)

This example uses a continuous excerpt of John F. Kennedy's 1961 inaugural address, marked with the Public Domain Mark on Wikimedia Commons. The source footage, transcript segments and source information are in `inputs/public-speech/`. It's used to show selecting and reordering passages from a historical speech; it doesn't represent contemporary policy views or an endorsement by the speaker.

Full experiment: `runs/20261024-002228-talk-highlight/`. The baseline scored 18.5, and round 1 scored 75.5 and was kept. The later rounds, at 68, 77 and 75, were all rejected; the 77 didn't win the head-to-head comparison with the current best. The run stopped normally after three rounds without improvement, 4 rounds in total. The score comes from a judge using the same requested model, reading the text of each cut; full audiovisual quality wasn't evaluated.

`artifacts/baseline/files/out/cut.mp4`, `rounds/rNNN/artifacts/files/out/cut.mp4` and `artifacts/final/files/out/cut.mp4` are playable videos actually rendered with FFmpeg on a local machine, each with matching text and SRT subtitles. `verification.json` records per-version decoding, duration and audio-track checks.

To reproduce, install FFmpeg, sign in to a personal Codex, and set `RSI_CODEX_BIN` explicitly (if needed). Then, from the repository root:

```bash
export RSI_VIDEO_INPUT="$PWD/examples/video-cut/inputs/public-speech/input.mp4"
export RSI_VIDEO_TRANSCRIPT="$PWD/examples/video-cut/inputs/public-speech/sentences.json"
export RSI_VIDEO_BRIEF="$PWD/examples/video-cut/inputs/public-speech/brief.md"
export RSI_VIDEO_SOURCE_INFO="$PWD/examples/video-cut/inputs/public-speech/source.json"
python scripts/run_demo.py video-cut --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5 --minutes 60 --codex-isolated
```

Pick the first cut, an intermediate candidate and the final cut to compare directly; rejected candidates are kept too. A rerun gets a new run folder and doesn't overwrite the historical record. For how to replace the footage with your own, see the template README.
