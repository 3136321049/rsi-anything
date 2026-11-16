# Local First-Release Candidate

> 2026-10-30: the current package is [`rsi_anything-0.3.0.dev0`](../dist/rsi_anything-0.3.0.dev0-py3-none-any.whl) (18 templates, including `rsi new`, `rsi setup`, roles and plugins); see [build validation](build-validation-0.3.0.dev0.json) and [clean install receipt](install-receipt-0.3.0.dev0.json). Below is the original record of the first release `0.2.0.dev0`, kept unchanged.

Version `0.2.0.dev0`, dated 2026-10-24. Provides 15 domains and 16 templates; 13 domains have complete real multi-round runs, D07 is a partial real video-generation run, and D15 awaits a personal GPU. Current development and handoff follow the `rebuild` branch and [cross-computer collaboration](../docs/COLLABORATION.md).

| Entry | Contents |
|---|---|
| [Case collection](../examples/index.html) | Initial, per-round and final work by domain; compare code, text, charts, video and schedules |
| [35-second demo](../examples/showcase-media/openrsi-demo.mp4) | Silent cut of real saved work, playable directly |
| [CLI package](../dist/rsi_anything-0.2.0.dev0-py3-none-any.whl) | All 16 templates; excludes large case media |
| [Lightweight source package](../dist/rsi_anything-0.2.0.dev0.tar.gz) | Source, templates, tests and docs; excludes case media |
| [Install guide](../docs/INSTALL.zh-CN.md) | Personal account setup, initialization, running, swapping inputs and viewing results |
| [Handoff notes](../docs/HANDOFF.md) | Current implementation, experiment locations, missing resources and next steps |
| [Item-by-item audit](../docs/RELEASE-AUDIT.md) | Acceptance basis and scope for domains and shared capabilities |

Verification evidence: [build](build-validation.json), [clean install](install-receipt.json), [showcase files and scope of existing visual checks](showcase-validation.json). 114 program tests passed; raw results of model experiments are in each case directory and are not mixed into install tests.

The two install artifacts and the original receipts keep the first-release build snapshot; the latest collaboration docs are read from the repository files. The full local ZIP archive is not committed; the ZIP entries in `package-validation.json` and `SHA256SUMS` record the original archive's checksums and are not a remote download source. The current upload scope and review are in `github-sync-audit.json`; the full pre-upload regression passed 115 tests.

When sharing in full, keep the relative positions of the source, `examples/` and docs. Pages are easier to view through a local HTTP server (see the install guide for commands); sending an HTML file alone will not include all media. Third-party material terms are in [Open Source and Sources](../docs/OPEN-SOURCE.zh-CN.md); this project's code license does not cover all videos, market data or original materials.
