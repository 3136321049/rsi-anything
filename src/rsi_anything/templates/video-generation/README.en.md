# D07: Real video generation

[简体中文](README.md)

The agent changes only the prompt, negative prompt and seed in `generation.json`. The prepare step calls Lightricks' official public Space and actually generates a short clip. The judge looks at evenly sampled still frames and gives feedback, and the agent then tries to improve.

The default service is [LTX Video Fast](https://huggingface.co/spaces/Lightricks/ltx-video-distilled), which upstream describes as LTX 0.9.8 13B distilled. The real experiment on 2026-10-24 got the starting clip and the round-1 clip. In the last two rounds the service returned errors and no new video, so their quality is marked unknown. The experiment is currently kept as partially measured under a resource exception. The public service may rate-limit, queue or pause, and this package doesn't switch to a paid service automatically.

## Getting started

You need Python, this project, FFmpeg/ffprobe and a personal model judge that can read images.

```sh
rsi init video-generation demo-video-generation
cd demo-video-generation
export RSI_VIDEO_CACHE="$HOME/.cache/rsi-anything/video-generation"
rsi run --rounds 5
```

`python3 judge/prepare.py` also really submits a generation; it isn't an offline preview command. To check the program offline, run the unit tests in the repository. If you change only the subject in `judge/brief.md`, also change the starting prompt and the rubric, then start a new run. The prepare script fixes the size and duration at 704×512 and about two seconds.

## Evaluation and outputs

The program confirms that the service returned a video and uses ffprobe to check the video track, size and duration. The model judges the cup, material, setting, steam and composition from still frames. It doesn't evaluate audio and can't confirm whether the full motion is smooth. With `pairwise: false`, this example keeps the better version by score under the same rubric; the final clip still needs to be checked by playing it.

`out/video.mp4` is the real result downloaded from the service, and `preview.html` plays it. `request.json`, `metadata.json` and `events.txt` record the input, event ID, returned seed, video hash, service version and reuse status. `outputs: [out]` saves each round's outputs. On failure, the program writes `error.json`, explicitly marks the artifact's quality as unknown, and doesn't produce a substitute video.

## Cache and recovery

Each request is hashed from the service address, the fixed parameters, the prompt and the seed. `RSI_VIDEO_CACHE` can point to a persistent folder outside the project; if it's unset, `rsi-anything/video-generation` under the user cache folder is used. The cache can't live in the temporary folder used for scoring.

State is written before submitting, and the event ID is saved as soon as it arrives. If waiting is interrupted, the next attempt keeps waiting on the same event. If a download is interrupted, the finished result URL is reused. An identical request that already finished reuses its clip after the hash is checked. A system file lock prevents concurrent submissions of the same request, and the lock is released when the process ends.

If no event ID comes back after submitting, the program keeps `submission_unknown` or `submission_pending` and doesn't resend automatically. A person needs to check the cache record to confirm whether the service accepted the request, then decide what to do with that cache entry. This limit keeps timeout retries from quietly generating duplicates.

## API and sources

- `RSI_VIDEO_ENDPOINT` can override the public service's base URL, but the target must offer the same input order and `text_to_video` endpoint. There is no account or paid fallback.
- `RSI_VIDEO_TIMEOUT` sets how many seconds this call waits, 480 by default; the main evaluation step is capped at 900 seconds.
- First `POST /gradio_api/call/text_to_video` to get an event ID, then `GET /gradio_api/call/text_to_video/<event_id>` to read the event stream. Only a video URL from `event: complete` is accepted.
- The [official Gradio guide to calling apps](https://gradio.app/4.44.1/guides/querying-gradio-apps-with-curl) describes the two-step protocol. The service was measured as running Gradio 5.42.0 and uses that instance's `/gradio_api` prefix.
- The [upstream README](https://huggingface.co/spaces/Lightricks/ltx-video-distilled/blob/main/README.md), the [upstream implementation](https://huggingface.co/spaces/Lightricks/ltx-video-distilled/blob/main/app.py) and the public `/config` were checked on 2026-10-24. Every new submission checks the input order and saves the service version. The model upstream declares can't be treated as if it were model evidence returned by the remote service at runtime.

This adapter uses only the Python standard library and FFmpeg. The offline interface and recovery tests pass. Real clips, requests, error evidence and video-decoding results are saved in `examples/video-generation/` in the repository. A complete multi-round run still awaits an available generation resource; the mocked responses in the tests are only for unit testing.
