# A single anonymous service diagnosis

[简体中文](README.md)

On 2026-10-24, exactly one generation request was submitted. It reused the 24-character prompt, seed, size, two-second duration and other settings from an earlier successful request. The POST returned HTTP 200 and an event ID, and the event stream also returned HTTP 200, but its content was `event: error` and `data: null`. There was no retry, and no switching of accounts, IPs or paid tiers.

- `request.json`: the input actually sent.
- `receipt.json`, `events.txt`: the actual acceptance and failure events.
- `service.json`: the live API's input order, Gradio version, `show_error`, the public upstream commit and the code hash.

This shows that a short prompt also hit a service error. It can't show whether the cause was an exhausted quota, an unavailable GPU or some internal fault. No video was generated, so the quality score stays unknown.
