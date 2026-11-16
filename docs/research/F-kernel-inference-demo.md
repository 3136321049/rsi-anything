# Inference Acceleration and Kernel Optimization: Public Sources and Demo Plan

Date: 2026-10-23. This document is the design and selection material for D15; no template has been implemented and no GPU experiment has been run. Sources are limited to the public projects, official documentation and independent design listed below.

## 1. Product scenario

Have AI optimize one piece of a neural network's computation: first measure which computations take time, then modify one GPU kernel implementation, check that the results are within the agreed tolerance, measure speed, keep effective changes, and keep trying.

The first version shows two layers of results: multi-round optimization of a standalone kernel, and the overall latency after swapping the final kernel into a small inference module. The two metrics are shown separately; a kernel speed change cannot be presented directly as a whole-model speedup.

This differs from the existing fuzzy-search speedup template: it involves GPU compilation, parallel partitioning, memory access, kernel fusion and numerical error. The existing RSI main loop is kept; a new domain template and evaluation adapter are added.

## 2. Usable public projects

| Project | Official capabilities | Integration judgment for this project |
|---|---|---|
| [AutoKernel](https://github.com/RightNow-AI/autokernel) | Locates PyTorch model hotspots, extracts kernels, iteratively modifies and tests Triton or CUDA implementations, checks overall effect | Closest reference for this domain. Study its benchmarks, candidate interface and feedback first, reuse parts as needed; avoid nesting another full loop |
| [KernelBench](https://github.com/ScalingIntelligence/KernelBench) | Public single-kernel, fused-computation and model tasks; checks output consistency against a PyTorch reference, and speed | Can pick one public task as the example; pin the task version and input conventions; a small demo need not run the full leaderboard |
| [Triton](https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html) | Write GPU kernels in a Python-style language; official tutorials include fused Softmax | Preferred candidate implementation; start from simple kernels so the scope of model-written code stays easy to control |
| [TileLang](https://github.com/tile-ai/tilelang) | Tile-based programming language and compiler support for high-performance computing | Candidate backend; adopt only once the target device, version and examples are verified to work |
| [CUTLASS](https://github.com/NVIDIA/cutlass) | CUDA linear algebra components and programming interfaces | Implementation reference or comparison for later matmul and fusion work; not required for the first example |
| [FlashInfer](https://github.com/flashinfer-ai/flashinfer) | Attention, matrix, normalization and other kernels for inference, with multiple backends | Candidate for later real inference integration and a stronger baseline; check hardware support per kernel |

The capabilities above come from upstream public descriptions; their actual compatibility with this repository's current dependencies has not been verified, and speedup numbers advertised upstream are not adopted as this project's results.

The public license files of AutoKernel and KernelBench are at [AutoKernel LICENSE](https://github.com/RightNow-AI/autokernel/blob/main/LICENSE) and [KernelBench LICENSE](https://github.com/ScalingIntelligence/KernelBench/blob/main/LICENSE). When actually brought in, pin the version, follow the corresponding license, and keep the required copyright and attribution notices. Renaming or rewriting code is not used to hide public sources.

## 3. First-version scope and implementation order

### A. Environment and baseline

First check the available, authorized personal compute resources, device model, driver, and PyTorch / compiler toolchain versions. With only a CPU or an incompatible device, first finish the template, configuration and no-GPU error message, and mark GPU measurement as pending; simulated timing or CPU results must not be presented as GPU speedup.

Do not use corporate compute environments by default. Before renting a GPU or adding a paid service, state the spec, intended use and budget, then get the user's decision.

First pick a small public task that runs in that environment. Try fused Softmax first; if the current hardware or baseline leaves no obvious room for improvement, choose normalization or a small fused computation based on measurements. No fixed speedup is promised.

Distinguish baselines clearly: the original composed implementation, the framework's built-in implementation, and the initial candidate. Public presentations state what is being compared. The initial candidate should work correctly, with changes coming from subsequent model attempts — do not pre-write a series of "optimized versions".

### B. Multi-round single-kernel optimization

The suggested template name is `kernel-speed`; the following are proposed new files, not an existing implementation:

- `rsi.yaml`: goal, editable paths, judge command, number of rounds and timeout.
- `candidate.py`: the GPU kernel and necessary launch parameters the assistant may modify.
- `judge/reference.py`: the fixed reference computation and interface conventions.
- `judge/check.py`: result checking, warm-up, timing and structured feedback.
- `judge/cases.json`: input shapes, dtypes, random seeds and tolerances, either self-designed or from public tasks with a clear license.
- `judge/module.py`: a small inference module for the integration comparison.
- `README.md`: device requirements, installation, running and how to view results.

Each round, the assistant modifies the candidate based on compile errors, numerical errors or performance feedback. Use the existing command-based judge to return a score, check results and feedback; keep using the existing Git branches, per-round records and reporting.

Common public directions to explore include reducing intermediate tensor reads/writes, fusing adjacent computations, adjusting parallel partitioning, tiling and launch parameters. Record the hypothesis behind each round's change, to avoid blind parameter sweeps whose effects can't be explained.

### C. Small inference module integration

Use a self-written small neural network module, or a public example with a clear license, and plug the initial and final kernels into the same call path. Record the module's output error, overall latency, and the kernel's share of that latency.

Keep model structure, inputs, precision and run configuration identical. The first version does not need production serving, multi-node communication or large model weights; the small module may use randomly initialized parameters and synthetic inputs, but must state that this is not a language generation task.

If the final kernel brings no gain to the module, save the result, analyze the computation's share and call overhead, and choose a meaningful next attempt. Describe inference speedup for the module only when the module measurably improves.

## 4. Demo-level evaluation requirements

1. First check shapes, dtypes, output error, and a small set of common and edge-case inputs; tolerances are configured before the experiment and cannot be changed by a candidate to pass.
2. Finish compilation and warm-up first, then measure steady-state execution time; cold start and compilation cost may be listed separately.
3. Use synchronization or timing appropriate to the device, measure repeatedly and report the median, rather than recording a single fastest run.
4. Comparisons use the same device, inputs and timing scope; time out and exit if an external tool or candidate hangs.
5. Name single-kernel, whole-module and end-to-end serving results separately; leave levels not measured in this demo blank.
6. Try about 5–8 rounds, saving candidates, errors, speed, and reasons for acceptance or rejection; whether there is an improvement is decided by actual results.

The public evaluation approach follows [KernelBench](https://github.com/ScalingIntelligence/KernelBench)'s separate checks for correctness and performance, and the fused computation and benchmark examples in the [Triton Softmax tutorial](https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html). The specific implementation arrangements above are this project's suggestions.

## 5. Presentation and acceptance

Presentation includes: what the original computation does, a summary of each round's change, the latency curve of the current best kernel, representative code diffs, numerical error, results across input sizes, the small module's overall latency, and device and software versions.

First-version acceptance: one public or independently constructed task genuinely runs through multiple rounds; initial and final implementations, per-round records and basic correctness results are all present; one small-module swap comparison is done; and it can be rerun by following the docs. Without GPU measurements, keep "pending measurement" — finishing the template does not substitute for acceptance.

## 6. Source and implementation boundaries

The source code, documentation, tests, data, screenshots, reports, commit messages and public materials of this personal project use only public sources, independently written content, and personal materials explicitly cleared for use in this project.

Non-public material is used only to understand general problems. Any method that lands in the project must be independently supported by public sources; no internal code, wording, configuration, private algorithm details, model weights, request samples, performance numbers, charts, logos or links are brought in. Rewriting, renaming or translating internal content does not lift this restriction.

Internal material is not given to coding assistants as task attachments or as inputs for reproduction experiments. If no independent public basis can be found, leave the item empty and use a public example or a self-constructed approach instead.
