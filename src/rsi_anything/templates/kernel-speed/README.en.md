# D15: GPU Softmax and a small inference module

[简体中文](README.md)

This package has the AI edit `candidate.py` to optimize a 2D row-wise Softmax GPU kernel. In the starting candidate, one Triton program handles one row: load, subtract the max, exponentiate, sum, normalize and write back. No later optimized versions were written in advance. Parallel partitioning, launch parameters and memory access are all open to exploration, and the effect has to be decided by measurements on a real device.

**Current status: the template and the no-GPU path are implemented; there are no GPU measurements or real model optimization records.** Mac MPS and CPU aren't used for this timing. Without a device, the status is `environment_unavailable` and the score is empty; don't treat passing template tests as a kernel speedup.

## Check your own device first

The first version is limited to Linux x86_64, NVIDIA compute capability 8.0 or higher and a CUDA-compatible driver; Python 3.11 is recommended. Only run it on a device already approved for this personal project; the template won't connect to remote machines or rent resources automatically.

```bash
rsi init kernel-speed my-kernel
cd my-kernel
python judge/check.py --probe
```

The probe only reads system and dependency information; it doesn't import the candidate or compile kernels. It writes `out/environment.json` and `out/report.md`. The exit code is 2 when no device is available, and 0 when one is available but nothing has been measured. Environments without a GPU don't need to install the large dependencies below.

On an authorized GPU machine, pick a CUDA version compatible with your driver from [the official PyTorch 2.6 install table](https://pytorch.org/get-started/previous-versions/). This template pins PyTorch 2.6.0 and Triton 3.2.0 as its starting combination; for example, with the CUDA 12.4 build:

```bash
python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124
python -m pip install triton==3.2.0
python judge/check.py --probe
python judge/check.py
rsi check
rsi run --agent codex --rounds 6
```

You must use the same Python as `rsi`. The dependency versions are also listed in `requirements-linux.txt`; don't force-install the CUDA path on a Mac. The GPU combination above still has to be verified on an available machine, and no fixed speedup is guaranteed on any particular device.

## Inputs, evaluation and outputs

`judge/cases.json` fixes the random seed, shapes, precision, numeric tolerances, warm-up count and timing settings. By default it checks a single element, irregular column counts, zeros, large-magnitude values, and float32/float16. Only contiguous, non-empty 2D CUDA tensors with at most 8192 elements per row are accepted. The candidate's output must keep the shape, dtype and device, and the candidate must not modify the input.

Timing runs only after the numeric checks pass. Each implementation is compiled and warmed up first, then timed with CUDA Events and a closing sync, taking the median of 15 groups of 20 calls each; CPU wall-clock time including the sync is saved as well. Implementations rotate their measurement order, so the same one isn't always measured first. Compilation and first-check time are reported separately and not mixed into steady-state time. Inputs are generated on the GPU in advance, so host-to-device copies aren't included; the candidate function's output allocation is inside the timed region.

The three single-kernel implementations compared are the frozen original PyTorch composite implementation, the framework's built-in `torch.softmax`, and the current candidate. The score is only the geometric mean of "built-in time / candidate time" across three fixed performance cases, and a candidate must improve it by at least 3% to be kept. Beating the composite implementation can't stand in for the comparison with the built-in one.

The same candidate is also placed in a small inference module, `input matmul → Softmax → output matmul`. The module's full output is checked, and the built-in and swapped-in versions are timed separately. The module's inputs and parameters are randomly initialized with a fixed seed, in float32, with TF32 off; it has no language-model weights, text generation or service requests. The module speedup is reported separately; it can't be inferred from the single-kernel speedup, and it isn't an end-to-end serving metric.

`out/metrics.json` saves the status, numeric errors, every timing sample, the medians, the single-kernel and module speedups, and the SHA256 of the candidate and the cases; `out/environment.json` saves the hardware, CUDA, driver and library versions; `out/report.md` shows the tables. `outputs: [out]` lets the engine save each round's outputs. With no GPU, or on an execution error, no made-up result is produced: the command evaluator reports a failure and the baseline doesn't start.

To replace the inputs, edit the frozen `judge/cases.json` before a new experiment starts, keep the reference and candidate interfaces consistent, then commit and start a new record. Cases, precision, tolerances and timing settings must not change within a run.

## Public sources and licenses

The following public sources were consulted and pinned on 2026-10-24:

- [Triton v3.2.0 Softmax tutorial](https://github.com/triton-lang/triton/blob/v3.2.0/python/tutorials/02-fused-softmax.py): a public method for fused computation, reduction and masking. `candidate.py` uses the same public math and Triton primitives; this package independently puts together a minimal one-program-per-row implementation and doesn't adopt the upstream persistent scheduling or its promotional performance figures. The copyright and license text of the upstream [MIT License](https://github.com/triton-lang/triton/blob/v3.2.0/LICENSE) are kept in `THIRD_PARTY.md`.
- [PyTorch CUDA Event](https://docs.pytorch.org/docs/stable/generated/torch.cuda.Event.html): `judge/check.py` uses its event timing, wait and elapsed-time APIs. The [PyTorch v2.6.0 license](https://github.com/pytorch/pytorch/blob/v2.6.0/LICENSE) is a BSD-style license; this package calls the dependency and doesn't copy its implementation.
- [KernelBench](https://github.com/ScalingIntelligence/KernelBench): its separate checks for correctness and performance served as a design reference; none of its problems, data or code were imported. The small inference module and the test cases were written by this project.

Later GPU baselines and multi-round records should be saved separately under `examples/kernel-speed/runs/`, keeping failed rounds and rounds with no improvement.
