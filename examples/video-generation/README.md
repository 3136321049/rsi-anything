# D07: Real video generation, partially measured

[简体中文](README.zh-CN.md)

This run includes a starting generation and 3 rounds of model edits. The baseline and round 1 produced real videos. Rounds 2 and 3 received `event: error / data: null` after the service had accepted them, so there was no video to evaluate. The round-1 clip and all inputs are kept, and the run is listed as **partially measured** under a resource exception; it doesn't count as a complete multi-round acceptance.

| Version | Actual result | Usable quality score | Video |
|---|---|---:|---|
| Baseline | Service generated successfully | 60.5 | 1.90 s, 704×512, H.264, no audio track |
| Round 1 | Service generated successfully, kept | 61.0 | 1.90 s, 704×512, H.264, no audio track |
| Round 2 | Service returned an error, no artifact | Unknown | None |
| Round 3 | Service returned an error, no artifact | Unknown | None |

Both the agent and the judge explicitly requested `gpt-6.1-sol` through a personal Codex CLI. The service didn't return the actual model, so it's still recorded as `null`. The generation service is Lightricks' official public [LTX Video Fast](https://huggingface.co/spaces/Lightricks/ltx-video-distilled). Upstream declares LTX 0.9.8 13B distilled, but that declaration can't be treated as model evidence returned at runtime. The model scores cover only the sampled still frames; full motion and sound weren't evaluated from them.

Round 1 mainly strengthened the steam, the light from behind and to the side, and the background contrast. The judge found that the steam now appeared but was too dense, and that the cup's base and handle were cropped, so the round ended up only 0.5 points above the baseline. This is the result of that one evaluation, not a reliable overall quality improvement.

[Baseline video](runs/20261024-003656-warm-morning-product-video/artifacts/baseline/files/out/video.mp4) · [Final kept video](runs/20261024-003656-warm-morning-product-video/artifacts/final/files/out/video.mp4) · [Final generation parameters](runs/20261024-003656-warm-morning-product-video/artifacts/final/files/generation.json) · [Playable preview](runs/20261024-003656-warm-morning-product-video/artifacts/final/files/out/preview.html) · [Independent verification](runs/20261024-003656-warm-morning-product-video/verification.json)

## Checking the service errors

On 2026-10-24, the [official implementation](https://huggingface.co/spaces/Lightricks/ltx-video-distilled/blob/8a42e93469c66b62d794b83a4233f5fc8439e2b5/app.py) and the public `/config` were checked again. The service still uses Gradio 5.42.0, the 13 input labels and their order match the original request, and `show_error` is false. The current `app.py` has no visible logic that rejects prompts by character count. The successful round-1 prompt was 868 characters and the two failed ones were 981 and 1159; all passed local input validation. No change in the interface order was found, but limits inside the model or remote faults can't be ruled out from the public app code alone.

Only **one** anonymous free diagnostic request was added. It reused exactly the earlier successful baseline's short prompt (24 characters), negative prompt, seed=42, 704×512 and two-second settings. Both the submission and the event stream returned HTTP 200, and event `4413c88e602948a19b642ddeae2b756f` was still `error/null`. So "it failed only because the prompt got longer this time" isn't supported. The service doesn't disclose the specific fault, and **it can't be confirmed whether the cause was quota, GPU resources, an internal service error or something else**. No other account, IP or paid service was used, and there were no further retries.

[The single diagnostic request and result](probes/2026-10-24-service-diagnosis/receipt.json) · [Service configuration and upstream version](probes/2026-10-24-service-diagnosis/service.json) · [Diagnostic input](probes/2026-10-24-service-diagnosis/request.json)

## Original records and derived checks

The original ledger encodes the prepare-step failures as `REVERT / 0`, and those original bytes are unchanged. This 0 doesn't mean the artifact's quality dropped, because no video was generated in those rounds. The [derived outcome check](runs/20261024-003656-warm-morning-product-video/outcome-audit.json) lists, item by item, the original status, the original score, the service events and the valid interpretation: rounds 2 and 3 are `JUDGE_FAIL`, with quality unknown and an empty quality score. The combined showcase page uses this interpretation, and the original failures remain traceable.

The baseline, round-1 and final videos were fully decoded with FFmpeg, and their size, duration, file hashes and source receipts were checked; the final file is byte-identical to round 1. Each round's `generation.json` matches the prompt, negative prompt and seed of the actual request. `verification.json` only confirms that this saved evidence is valid, and explicitly states `multi_round_demo_complete: false`.

[Raw ledger](runs/20261024-003656-warm-morning-product-video/ledger.jsonl) · [Original report (with the old failure code)](runs/20261024-003656-warm-morning-product-video/report.html) · [Source events and original video URLs](runs/20261024-003656-warm-morning-product-video/source-receipts.json)

## How to continue measuring

Once the service recovers, or a compatible free resource has been separately approved, check the interface as described in the [template guide](../../src/rsi_anything/templates/video-generation/README.md), then start a new experiment. Don't overwrite this run's successful video and failure records.

```bash
python scripts/run_demo.py video-generation --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

`RSI_VIDEO_ENDPOINT` can set a compatible endpoint, and `RSI_VIDEO_CACHE` stores accepted events and clips so nothing is resubmitted without your knowledge. Calls submit the prompt to a public service, so don't include sensitive personal information or company material. This project has no automatic paid fallback.
