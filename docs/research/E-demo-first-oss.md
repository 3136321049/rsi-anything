# Demo-First Open-Source Component Review

Checked: 2026-10-23. The goal is to determine which demo effects a minimal integration can add. Sources are the current code and the official upstream repositories; the integration difficulty and priority in the tables are this project's judgment — none of these candidates has been installed or tested for compatibility yet. For the execution plan, see the [Demo plan](../DEMO-PLAN.md).

## 1. Components actually in use today

| Project | Relationship in current code | Source checked this time |
|---|---|---|
| FFmpeg | Video asset generation, trimming, concatenation and rendering call `ffmpeg` / `ffprobe` directly; see `templates/video-cut/rsi_init.py` and `judge/render.py` | [Official GitHub mirror](https://github.com/FFmpeg/FFmpeg); the official website's about page timed out this time, so the official mirror was checked instead |
| faster-whisper | When the user provides `input.mp4`, `WhisperModel` is imported for transcription; this optional path is written, but there is no complete demo acceptance record for it yet | [Official repo](https://github.com/SYSTRAN/faster-whisper) |
| Git / PyYAML | Version saving and config parsing; the former is an external command, the latter a direct runtime dependency of the package | Current `gitops.py`, `contract.py`, `pyproject.toml` |
| pytest | Dev dependency used for this project's automated tests | Current `tests/`, `pyproject.toml` |

The loops and scoring adapters of the three templates — code speedup, copywriting and prompts — are implemented in this repository. Codex, Claude Code and similar are executor integrations; using their CLIs does not mean an additional open-source RSI framework is integrated. The `say` command used for macOS synthetic demo assets is a system capability.

## 2. Most relevant upstreams and concrete integration paths

### autoresearch: loop design reference

The official description: an assistant modifies small-model training code, runs a fixed-duration training run, compares results, keeps or discards, and continues. openRSI currently borrows the idea of this task loop, but does not import its training code or run its GPU experiments. [Official project](https://github.com/karpathy/autoresearch)

### FunClip: candidate entry point for real Chinese footage

The official project provides FunASR-based video transcription, timestamps, segment selection by text or speaker, subtitles, and model-assisted editing. The minimal integration is to convert one transcription result into the existing `judge/transcript.json`, still letting openRSI modify `edit.json` and call the existing renderer. Requires a separate model environment and verification of the output format. [Official project](https://github.com/modelscope/FunClip)

Judgment: if the existing faster-whisper is sufficient for the first footage, no need to add the dependency right away; try this first when Chinese transcription quality becomes the bottleneck. Not yet integrated.

### video-use: reference for partial editing capabilities and presentation

The official project is a collection of Skills and helper scripts for coding assistants, covering transcription, edit decision lists, subtitles, audio/video processing and rendering. Its default transcription depends on ElevenLabs; direct reuse cannot assume every step is ready in the current environment. [Official project](https://github.com/browser-use/video-use), [render script](https://github.com/browser-use/video-use/blob/main/helpers/render.py)

Candidate integration: convert `edit.json` into the upstream edit decision file, call its renderer through a preparation step, and keep output paths as defined by this project. Judgment: FFmpeg can already render; bring in partial capabilities only when subtitles, audio transitions or visual processing are clearly needed. Not yet integrated.

### GEPA: optional comparison for prompt optimization

Officially provides reflective text optimization, generating candidates from scores and run feedback; `optimize_anything` accepts text candidates and a user-defined evaluation function. The existing `prompt.md` and customer-service classification evaluation could be plugged in as an independent experiment, with results then imported for display. [Official API](https://github.com/gepa-ai/gepa#optimize_anything-beyond-prompts)

Judgment: the current main loop can already modify prompts. GEPA's benefit is an additional search strategy and comparable cases, not a requirement for the first release to work end to end. Requires adapting the evaluation and result format. Not yet integrated.

### OpenEvolve: algorithm search extension

The official project provides program-oriented evolutionary search, multiple candidate populations, user-defined evaluation and checkpointing. It could later be connected to `search.py` and the scoring program to show exploration of multiple algorithmic directions. [Official project](https://github.com/algorithmicsuperintelligence/openevolve)

Judgment: the existing speedup case is already complete; wiring in another search engine for the first release adds little demo value. Defer until parallel candidates or algorithm exploration are needed. Not yet integrated.

### RD-Agent: finance and machine learning domain extension

Officially provides data-driven R&D workflows covering quant factors, models and data science tasks; the current official installation instructions assume Linux, Docker and similar environments. [Official project](https://github.com/microsoft/RD-Agent)

Judgment: suitable for a future standalone domain pack. Its environment and full R&D loop exceed the current minimal need of "ship one visible demo first"; not included in the first release. Not yet integrated.

### scikit-learn: lightweight training demo

There is an official handwritten digit recognition example that can serve as the starting point for a small classification task. [Official example](https://scikit-learn.org/stable/auto_examples/classification/plot_digits_classification.html)

This project's suggestion: fix the data split and evaluation script, let the assistant change training parameters or preprocessing, and save accuracy, misclassified examples and time taken. Good for covering the training domain, no GPU required; not yet implemented, and actual run time has not been estimated.

### diffusers: later candidate for generation

The official library covers image, video and audio generation. Later, with a fixed generation pipeline, prompts and parameters could be the editable artifact, with generated output handed to the judge. [Official project](https://github.com/huggingface/diffusers)

Judgment: environment, models and generation cost need separate evaluation; there is currently no video generation demo, so it is not a must-do for the first release.

## 3. Selection conclusions

The first release reuses the current main loop and existing video components. Any new component must directly solve a visible problem: FunClip is the candidate for Chinese transcription, video-use for subtitles and visual processing, and GEPA if a second prompt search strategy is wanted. Wherever a project name appears — in research, as a design reference, as an optional interface, or in a real run — state the relationship.

Star counts, prices, speed estimates or license classifications from earlier research are not treated as current conclusions here. When code and models are actually brought in, re-check the dependencies and license of the chosen version and record the upstream version and acknowledgments.

