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
Direction: maximize. Current best score: 60.5.

Judge feedback on the current best:
真实生成事件 7e83c0459d1b46179a8c5980f6148bf6；1.90秒，704×512；相同请求缓存复用=False。评委仅看抽帧，声音与完整运动仍需播放检查。
steam 1.0/10: 八张静帧的杯口上方均未见可辨认的蒸汽，因此按不可见的锚点计1分，缺少升至下一档所需的可见证据。
subject 7.0/10: 八张静帧中的杯口、杯底和单个杯柄均完整可见，釉面反光可信、比例自然，但杯身明显偏暖棕米色，与浅米白要求有距离，未达到8分。
[cli:codex:gpt-6.1-sol] 让杯口上方出现清晰可辨、轻薄自然且不遮挡杯体的蒸汽。

## Recent rounds (newest last)
- r0 BASELINE score=60.5: (baseline)

## Lessons from earlier rounds and runs
- none yet

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
