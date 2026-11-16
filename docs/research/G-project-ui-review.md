# Project Review and Product Design Research

Checked: 2026-10-25. Project source baseline is `2f6df82`. This file records facts and external references; for the current product plan, see [Product direction](../PRODUCT.md).

## Project and workspace check

At the first check, the server's `rebuild` workspace was clean; after fetching remote refs, it was 0 commits ahead / 0 behind `origin/rebuild`. Current research work is on `codex/project-ui-review`. The remote default ref is still the old `main`, and the README does not yet describe completed results; the public entry point should point to a specific version.

Regression result: 114 passed, 1 skipped, 14.53 seconds, Python 3.10.12. The skip is at `tests/test_release_templates_numeric.py:131`, missing optional training dependencies for the CPU classifier template. The earlier 115 passes belonged to the environment at that time; both results must keep their specific conditions.

Recomputed SHA256 for the 598 artifact manifest entries: none missing or mismatched; all 698 local file entries in the current showcase data exist. The wheel is 216992 bytes, and its SHA256 matches the original install receipt: `6decf01ac333b45cb76a4b6636fd74e46e26863c076ce4476c27cc2a54cbd373`.

There are currently 15 domains and 16 templates; 13 domains contain 14 complete template cases. D07 has partial generation measurements; D15 awaits a GPU. The browser was used to actually view the classifier's initial/final misclassifications, code fixes and text diffs; this pass did not cover all cases, mobile, or video playback.

The current project environment lacks training dependencies, and the shell found no FFmpeg, ffprobe, Codex or Claude entry points; new experiments require preparing personal run conditions for the chosen template. The current project has no recoverable `.rsi/**/run.json`; exported results are readable, but it cannot be assumed that the experiment branches from the original machine have been migrated.

## Product boundaries set by the source code

`scripts/build_showcase.py` generates a static page from directories and raw runs; `src/rsi_anything/report.py` generates a single-run report. The current collection HTML is about 3.21 MB, containing a lot of inline text and HTML, with media loaded via file links. Task creation, execution, resume and export are done on the command line; a web run service is not yet implemented.

The existing round ledger already records the change hypothesis, decision, score, best result, checks, feedback, changed paths, time, cost and artifact location — enough to be reused by pages for different domains. A state file records the current phase; these records can support progress display later. Queuing, web authentication, duplicate-submission control and a reliable web stop action still need to be added.

`code-speed`'s evaluation first verifies search results, then measures time; each evaluation generates random inputs and records the seed. Historical three-round speedup results belong to their respective runs; cross-device re-measurements must be listed separately. It cannot serve as evidence of model inference speedup.

`cpu-classifier` currently produces a formal improvement in the first round, with no formal changes in the next two rounds. The page should show real accuracy, configuration and misclassified examples; there is currently no large-model training loss series.

`video-cut` currently allows changing sentence selection and order; FFmpeg renders real video, and the judge mainly evaluates the edited text. It cannot yet show automatic optimization of visual art, motion or audio quality.

Both the repository source and the attribution notes list `autoresearch` as the loop reference; the upstream training engine is not imported. The [upstream README](https://github.com/karpathy/autoresearch/blob/master/README.md), read via the GitHub connector on 2026-10-25, still describes the product as single-GPU, small model, fixed training budget, modify-and-keep loop. The upstream file version is `953ea55d5599c45c1be7dad93ec03e47dfa7df9d`. Upstream capabilities cannot be counted as this project's completed work.

## Research lab homepage references

The following comes from the official websites; Periodic Labs and General Intuition were actually viewed in a browser with local reference screenshots saved, while for Thinking Machines and Physical Intelligence this check covered page content and navigation. The reference screenshots are for internal design judgment and are not brand assets of this project.

| Reference | Verifiable content | Takeaway for this project |
|---|---|---|
| [Periodic Labs](https://periodic.com/) | Homepage opens with a short research thesis; visuals are a light warm background, lots of whitespace, restrained text and minimal navigation | The brand homepage builds its character through typography and concrete research process, while keeping a direct path into cases |
| [General Intuition](https://www.generalintuition.com/) | Dynamic media and a bold logo above the fold; the research section offers playable demos, technical reports and code together | Visual appeal should be followed by entry points to concrete, usable results |
| [Physical Intelligence](https://www.pi.website/) | After a short mission statement, lists research projects with dates, titles and specific capabilities | Each domain's results should be independently accessible, with tasks and results clearly identifiable |
| [Thinking Machines Lab](https://thinkingmachines.ai/) | Navigation separates product, research and news; body text describes customization and empirical iteration | Brand expression, actual tools and evidence can be organized in layers |

None of these websites provides conversion data attributable to page design. Adopting their layouts is this project's design judgment; it cannot be claimed that copying a visual style replicates growth.

## Verifiable material on distribution and adoption

### autoresearch

The upstream README frames usage as a concrete scenario: hand an assistant a small training task, let it experiment continuously, and review logs and kept results; it opens directly with a progress chart. The public [Hacker News discussion](https://news.ycombinator.com/item?id=47291123) shows it sparked discussion about automated experimentation, verification and capability limits; that page alone cannot separate the respective contributions of the author's influence, code quality and presentation format.

The judgment for Open RSI: each main case should also have a one-sentence task people can repeat, one checkable change, and an entry point to view the process directly. Merely saying it covers many domains makes it hard for visitors to judge how it relates to them. This is a product judgment pending validation through user trials.

### Manus

The [official feature docs](https://manus.im/docs/features/wide-research) place run replays next to concrete tasks and outputs; [official in-person events](https://events.manus.im/events/manus-fellow-sf-002) also use shareable projects as showcase material. This indicates that replays and concrete cases are part of how the product spreads, but there is no data sufficient to show how much growth replays directly bring.

What Open RSI can adopt: generate directly openable pages for real runs, with links pointing to a specific round and comparison target. On first open, the artifact is visible; those willing to try can then enter the same kind of task.

### Langfuse

The [official write-up from 2026-03-24](https://langfuse.com/blog/2026-03-24-optimizing-ai-skill-with-autoresearch) describes the author trying to automatically improve their own skill, and also records side effects that arose when the evaluation target was inadequate. Technical users need to see the task scope, how checks are done, and why things failed.

For this project, this means keeping a justified rejection, a non-improvement or a failure in the accessible process, so results are easy to audit. This does not require filling the homepage with caveats; specific conditions can unfold with each case.

## Video production path

[Remotion's coding-agent workflow](https://www.remotion.dev/docs/ai/coding-agents) and [official skills](https://www.remotion.dev/docs/ai/skills) let an assistant create animation code, preview it and render video. This can be used for this project's promo video and demo assets without adding a text-to-video model. Specific models, costs, licenses and deployment are checked separately at selection time; nothing was installed or called in this round.

The homepage promo video should be stored separately from formal domain experiments. If RSI is later to modify animation code, a separate editable scope, render step and evaluation must be built, rather than treating the promo production record as a completed multi-round optimization.

## Performance and interaction references

The [MDN video docs](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/video) cover poster images, preloading and playback controls; the [reduced motion setting](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) supports reducing non-essential motion based on user preference.

This project's specific choices: the first screen gives readable content and usable entry points first; videos show a poster first and load full media on demand; browsing replays does not start model tasks; the run page can be refreshed and returned to while a background task exists. Performance targets must be confirmed by testing on real devices.

## Current recommendation

The brand homepage and three domain pages — code optimization, model experiments and video creation — are implemented and share formal run data and state. They currently use saved real results; personal main-case assets and a controlled server-side run service come next. Specific pages, assets, user paths, implementation batches and acceptance all follow [Product direction](../PRODUCT.md).
