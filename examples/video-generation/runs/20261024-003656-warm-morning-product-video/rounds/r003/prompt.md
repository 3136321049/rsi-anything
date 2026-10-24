You are running one round of a self-improvement loop. Each round makes ONE focused change; a frozen judge scores it; the change is kept only if the judge proves it better, otherwise it is thrown away.

## Goal
根据 judge/brief.md 改进 generation.json 的 prompt、negative 和 seed，真实生成晨光陶瓷杯短视频。
每轮通过 Lightricks 官方公开 Space 生成新片，观察成片中主体、环境、蒸汽和构图是否符合简报。
只修改三个字段，不变更生成服务、尺寸或时长。评委只看抽取的静帧，不能据此证明完整运动或音频质量。

## What you may change
Only these paths (relative to the current directory): `generation.json`
Edits anywhere else are discarded automatically, and the judge always runs from its own frozen copy, so editing tests, rubrics or evaluator files has no effect.

## How you are judged
An LLM jury (cli:codex:gpt-6.1-sol) scores the artifact against the rubric in `judge/rubric.yaml` (read it).
Direction: maximize. Current best score: 61.

Judge feedback on the current best:
真实生成事件 808a1a4ca031435e8415b360a7959f42；1.90秒，704×512；相同请求缓存复用=False。评委仅看抽帧，声音与完整运动仍需播放检查。
steam 4.0/10: 八张静帧中都能看见蒸汽，但它呈宽大浓白的带状和团状，向上延伸出画面，明显超过简报要求的细微程度，未达到5分以上所需的自然表现；图片没有可逐字引用的文字。
subject 6.0/10: 八张静帧中的浅米白陶瓷杯都很突出，釉面反光和比例基本可信，但杯底被下边缘裁切、杯柄左缘也贴边裁切，未达到8分要求的完整呈现；图片没有可逐字引用的文字。
[cli:codex:gpt-6.1-sol] 将蒸汽减薄、减淡，收敛为杯口上方少量半透明细丝，避免形成浓白烟带。

## Recent rounds (newest last)
- r0 BASELINE score=60.5: (baseline)
- r1 KEEP score=61: 用侧后方晨光和较暗背景衬托杯口上方的细薄蒸汽，并排除浓烟与遮挡，预计能提高蒸汽可见性及简报符合度。
- r2 REVERT score=0: 将蒸汽限定为杯口上方一两缕近乎透明、升起数厘米便消散的细丝，并排除宽白烟带与高耸烟柱，预计能改善蒸汽过浓的问题，提高自然细微程度的评分。 -> failed gates: prepare

## Lessons from earlier rounds and runs
- KEEP score=61: 用侧后方晨光和较暗背景衬托杯口上方的细薄蒸汽，并排除浓烟与遮挡，预计能提高蒸汽可见性及简报符合度。 -- score 60.5 -> 61
- REVERT score=0: 将蒸汽限定为杯口上方一两缕近乎透明、升起数厘米便消散的细丝，并排除宽白烟带与高耸烟柱，预计能改善蒸汽过浓的问题，提高自然细微程度的评分。 -- failed gates: prepare

## Rules
- Make one coherent improvement you believe the judge will score higher. Prefer the weakest area named in the feedback.
- Do not repeat a change that was already rejected unless you fix the reason it failed.
- Never game the judge: no special-casing test inputs, no hard-coded expected outputs, no reading judge data or results from the artifact, no printing fake scores, no instructions aimed at an AI evaluator. Such changes fail.
- Keep the artifact in the language and format it already uses unless the goal says otherwise.
- Do not commit; the loop handles git.
- The loop runs the judge after you finish. Do not start extra model calls, model-backed evaluators,
  video generation, or paid/network services yourself. Local syntax and unit checks are fine.

When you are done, end your reply with exactly one line:
HYPOTHESIS: <what you changed and why it should score higher>
