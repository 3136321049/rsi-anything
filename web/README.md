# DARWIN Website

DARWIN builds two static websites, English and Chinese, from Open RSI's saved official experiments: Home, Code Optimization, Model Experiments, Video Creation, Visual Work, All Experiments and Get Started. All interaction reads static data in the browser; no models are called.

```bash
python scripts/build_site.py
python -m http.server 8765 --bind 127.0.0.1 --directory build/site
```

English is the default language (`/`); Chinese is at `/zh/`. Both languages share the same page structure and the header links between them. When a Chinese-language browser first visits an English page, a prompt in the bottom-right corner offers to switch; there is no automatic redirect. The official entry point is `https://www.riseai.top/darwin/`. Deploy only `build/site`; do not use the source repository root as the website root.

## File Responsibilities

- `page.html`: shared header, footer and metadata; `home.html`, `code.html`, `experiments.html`, `video.html`, `visual.html`, `cases.html` and `start.html` hold each page's content.
- `i18n/en.json`, `i18n/zh.json`: UI text. Templates reference it with `{{key}}`, scripts with `t("key")`; both files must have identical keys, and a missing key fails the build.
- `i18n/records.en.json`, `i18n/records.zh.json`: translations of experiment records (domain titles, change rationale, judge feedback, etc.), keyed by the original text. A missing translation on the English pages fails the build; `python scripts/site_i18n.py --missing en` lists text awaiting translation. Work files themselves stay in their original language.
- Documentation comes in English and Chinese with one naming rule everywhere: `X.md` is English and `X.zh-CN.md` in the same directory is Chinese (`docs/`, the `README.md` of templates, cases and environment probes, and `THIRD_PARTY.md`). On Chinese pages, document buttons and case links open the Chinese version automatically. When editing one language, update the other too; new documents must include a translation, otherwise tests fail.
- `assets/site.css`: design variables, components and narrow-screen layout. Light background with a dark screening area; the accent color is used only for "kept" versions, and rejections use orange. The dark theme changes only the variables on `:root` (enabled automatically when the system is dark; `html[data-theme]` records the visitor's manual choice and is restored by `assets/theme.js` before the first frame; the production CSP is `script-src 'self'`, so do not write inline scripts). Use variables for new styles rather than hard-coded colors, otherwise dark mode will show light blocks or unreadable text.
- `assets/app.js`: home-page evolution replay, the four labs, All Experiments browsing and comparison, document preview and language switching. The visual lab pages through screenshots, per-criterion scores and comparisons with the best version at the time, round by round, and can play the kept versions in sequence.
- `assets/fonts/`: self-hosted Latin subsets of Inter and JetBrains Mono (SIL OFL), avoiding font services that are unreachable in mainland China; Chinese uses system fonts.

## Data and Public Scope

`scripts/build_site.py` uses four fixed accepted runs to generate data for the first three labs (`CASES`); the visual lab reads the two pelican runs and the one landing-page run listed in `VISUAL`, and if a later run's starting point is byte-identical to the previous run's final work, the two are joined into one timeline. The All Experiments page is aggregated from `examples/catalog.json` and the original runs, with file contents read on demand. The build copies only what needs to be public: `examples/`, template directories, four documentation files (Chinese and English), the Chinese and English READMEs, the license and the wheel package. The source includes internal development docs that are not put on the website; the collaboration conventions, handoff notes, devlog and release audit do not go onto the website. The old `examples/index.html` address redirects to the All Experiments page on the website.

The source repository is not public yet, so pages do not link to it, and the Get Started page installs via the wheel hosted on the website. Video cards and covers are taken from real finished videos; timestamps, crops and hashes are in `assets/media-sources.json`. `assets/og.png` is a share image drawn to match the page design and does not represent any particular experiment's data.

## Checks After Changes

Run `python -m pytest -q`. `tests/test_site.py` checks all page links in both languages, cross-language links, UI text keys, no missing translations in English data, English versions of documentation and their links, unreviewed-round boundaries, video subtitle timing, result bundles and the public file scope. Then check in a browser on desktop and at 390px narrow width: home-page replay, round switching, code diffs, matrix filters, video subtitle seeking, screenshot switching and sequential playback in the visual lab, and version comparison and download in All Experiments.
