# D15: local environment check

[简体中文](README.zh-CN.md)

On 2026-10-24, `python judge/check.py --probe` and the default check were run for real on the current Mac (arm64). Both exited with code 2 and status `environment_unavailable`, with an empty score. The template requires Linux x86_64 and an NVIDIA CUDA GPU, so no candidate was compiled, no numerical test ran and no performance number was produced.

[Environment](environment.json) · [Check result](metrics.json) · [Report](report.md) · [Verification](verification.json)

This record only shows that the check stops cleanly without a GPU. It doesn't count as a finished D15 experiment. The next step needs a compatible GPU that is cleared for this personal project: install the dependencies as the [template guide](../../../../src/rsi_anything/templates/kernel-speed/README.md) describes, then run the numerical checks, a real multi-round optimization and the small-module replacement comparison. No device was rented automatically, and no machine outside this personal project was used.
