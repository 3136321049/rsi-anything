# Components, reference projects and sources

[简体中文](OPEN-SOURCE.zh-CN.md)

Updated: 2026-10-24. This page separates what the code actually calls, public material used as input, and projects used only as research references. More detailed versions, call sites and verification records are in each template README, the frozen configs and the experiment directories.

14 domains currently have real multi-round runs and independent verification. D07 has only partial generation results, and the cause of the later service errors is unknown. D15 has no measured GPU run. Whether a component is in a template, whether it was really called, and whether the experiment was completed are each stated separately; one doesn't stand in for another.

Code written for this project is provided under the root [LICENSE](../LICENSE). It doesn't change the terms of use for third-party libraries, model weights, source material, market data, videos or derived outputs.

## Used by the code

| Component | How this project uses it | Location and notes |
|---|---|---|
| Python, Git, PyYAML | Configuration, separate run branches, evaluators and result records | Main loop; [PyYAML](https://github.com/yaml/pyyaml) |
| pytest | Development regression tests; the mock agent in the tests only verifies program behavior | `tests/`; not used as real demo results |
| scikit-learn 1.6.1 | Loads digits, makes the fixed split, trains and predicts | [CPU classifier template](../src/rsi_anything/templates/cpu-classifier/README.md); calls existing learning algorithms and doesn't copy their training engine |
| Matplotlib 3.9.4 | Draws confusion matrices, misclassified examples and backtest curves | CPU classifier and quant templates; [official project](https://matplotlib.org/) |
| FFmpeg / ffprobe | Cutting, subtitles, video decoding and basic media checks | [Video-cut template](../src/rsi_anything/templates/video-cut/README.md), [video-generation template](../src/rsi_anything/templates/video-generation/README.md); the conditions for the installed FFmpeg build and its codecs come from upstream |
| faster-whisper | Optional transcription when the user has no transcript | [Official repository](https://github.com/SYSTRAN/faster-whisper); not a required default dependency, and models are downloaded separately |
| Mermaid | Chart descriptions for business analysis; the HTML can render them via a CDN | [Business-report template](../src/rsi_anything/templates/business-report/README.md); the table of figures is kept for offline viewing |
| Lightricks LTX Video Fast / Gradio | Sends prompts to the official public Space; this run got real videos for the starting artifact and round 1, and none for the next two rounds | [Official Space](https://huggingface.co/spaces/Lightricks/ltx-video-distilled); one short-prompt diagnostic still returned `error/null`, for an unknown reason. See the [partial measured run and sources](../examples/video-generation/README.md). The service's status and terms of use are independent of the code license |
| PyTorch 2.6.0, Triton 3.2.0 | GPU Softmax, numeric comparison, event timing and a small module comparison | [GPU template](../src/rsi_anything/templates/kernel-speed/README.md); no measured GPU run by this project yet. The public tutorial's copyright and license are kept in [THIRD_PARTY.md](../src/rsi_anything/templates/kernel-speed/THIRD_PARTY.md) |

Model calls use the user's own personal CLI or API. Third-party agents, subscription services and model APIs aren't part of this repository. Having an adapter doesn't mean every account, region and version has been verified.

## Default material and data

| Use | Actual source | Use and distribution limits |
|---|---|---|
| Code repair, copywriting, writing guide, contract, lesson, schedule | Synthetic business material, exercises or schedules written by the project author | No real customer, patient, student or company data. The first drafts are hand-prepared starting points for the task; later model candidates are recorded separately |
| CPU handwritten-digit classification | [scikit-learn digits dataset description](https://scikit-learn.org/1.6/modules/generated/sklearn.datasets.load_digits.html) | Public teaching data read through the dependency. Its origin and description follow that page and the dataset notes; this project's MIT license can't simply be applied to it |
| Video-cut run | [Kennedy's inaugural address on Wikimedia Commons](https://commons.wikimedia.org/wiki/File:John_F._Kennedy_Inauguration_Speech.ogv) and its subtitles | The source page carries the Public Domain Mark. This project records the source, the excerpt's start and the file hash; see [source.json](../examples/video-cut/inputs/public-speech/source.json). This doesn't imply endorsement of the person or any policy |
| Business analysis | [Apple FY2024 official financial statements](https://www.apple.com/newsroom/pdfs/fy2024-q4/FY24_Q4_Consolidated_Financial_Statements.pdf) and the press release | Fixed financial facts are extracted and the analysis is written independently; the full report isn't redistributed. The source and the full-year basis are frozen |
| Quant backtest | [Binance public market data](https://github.com/binance/binance-public-data) and the official Kline API | The [CC BY-NC-SA 4.0 and Binance Vision Dataset Terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md) registered in the template apply independently. The default data, derived charts and analysis keep the attribution, non-commercial and share-alike conditions; the code's MIT license can't be used to claim unrestricted commercial use. The template package contains only the downloader and doesn't bundle market data |
| Literature review | Official index pages for two cognitive research studies and a UNESCO guide | Uses short summaries written by the author, keeping authors, years, links, evidence type and limitations; not a substitute for a license to the original text. See the [template sources](../src/rsi_anything/templates/literature-review/judge/sources.json) |
| Contract exercise | A self-written contract and checklist, with reference to [business.gov.au's guide to preparing a contract](https://business.gov.au/people/contractors/prepare-a-contract) | Doesn't copy a real contract, doesn't apply the law of the source's jurisdiction to this example, and is explicitly not legal advice |
| Health education | WHO's official physical-activity material and guideline summaries | Only restates public health information, keeping the sources and the population limits; the article isn't individual medical advice. What was actually read is listed in the [run notes](../examples/medical-explainer/README.md) |
| Percentages lesson | A self-written lesson and exercises, with concepts drawing on [OpenStax Prealgebra 2e](https://openstax.org/books/prealgebra-2e/pages/6-introduction-to-percents) | No textbook problems or whole chapters are copied; if you switch to another textbook, check its terms separately |

The default backtest is a parameter demonstration on a single historical period and isn't investment advice. The legal and health templates only handle clearly bounded synthetic exercises or public material and give no judgment on real individual cases. Before using material in commercial promotion or redistributing it, check the terms of each item; open-source code and publicly readable material are not the same thing.

The [35-second silent demo clip](../examples/showcase-media/openrsi-demo.mp4) uses saved results from code repair, the writing guide, the speech cut and classifier mistakes; it isn't newly generated data or an optimization result. [demo-video.json](../examples/showcase-media/demo-video.json) lists the exact inputs, the video's SHA256, the 35-second duration, the 1280×720 size and the decode check. The historical speech excerpt in it keeps the original material's public-domain source note.

## Engines referenced but not integrated

| Project | What we looked at | Current relationship |
|---|---|---|
| [karpathy/autoresearch](https://github.com/karpathy/autoresearch) | The simple edit, evaluate, keep loop | Design reference; its engine isn't imported |
| [GEPA](https://github.com/gepa-ai/gepa) | Optimizing text from failure feedback while keeping multiple candidates | Possible future comparison; no dependency today |
| [OpenEvolve](https://github.com/algorithmicsuperintelligence/openevolve) | Algorithm candidate search and evolution | Future candidate; the main loop is still one candidate per round |
| [RD-Agent](https://github.com/microsoft/RD-Agent) | Data and model R&D workflow | Research reference; the quant template doesn't call it or Qlib |
| [FunClip](https://github.com/modelscope/FunClip), [video-use](https://github.com/browser-use/video-use) | Linking text and video through a transcript and an edit decision table | Idea reference; the existing cuts are made by the project's own scripts and FFmpeg |
| [KernelBench](https://github.com/ScalingIntelligence/KernelBench) | Checking numeric correctness and performance separately | Design reference for GPU evaluation; its problems and data aren't imported |
| ComfyUI, diffusers, OR-Tools, FSRS and others | Potential domain tools from the research | Not called by current templates; not presented as first-release dependencies |

`docs/research/` holds the tool-selection surveys. The versions, counts, costs and APIs there reflect what was known at the time and aren't a list of current integrations. When a new component is needed, check the official source first, use it to solve a concrete run's problem, then record where it's actually called and the conditions that apply.
