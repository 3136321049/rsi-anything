# D15: GPU kernel optimization, awaiting measurement

[简体中文](README.md)

The template uses Softmax as its example: the agent edits a Triton kernel, first compares its numerics with PyTorch reference results, then times the single kernel and a small inference module. For the default inputs, device requirements and launch commands, see the [template guide](../../src/rsi_anything/templates/kernel-speed/README.en.md); for public references and licenses, see the [third-party notice](../../src/rsi_anything/templates/kernel-speed/THIRD_PARTY.en.md).

There is currently no personal NVIDIA GPU. The real local probe returned `environment_unavailable` with exit code 2 and an empty score; the candidate wasn't imported and no GPU measurement ran. See the [probe notes](probes/2026-10-24-local/README.en.md) and the [verification evidence](probes/2026-10-24-local/verification.json).

Under the resource exception, this domain delivers the template, fixed inputs, a no-device message and an entry point for running the measurements later; it isn't counted among the 13 complete multi-round domains. Once a personal GPU is available, the next steps are to run the template's baseline check first, then run multi-round optimization with a personal agent, saving device information, correctness, kernel timings and the small-module comparison. No hardware is being rented for now, and no company resources are used.
