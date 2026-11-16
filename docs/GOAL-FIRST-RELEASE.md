# Open RSI First Release: Codex Goal Brief

Date: 2026-10-23. The user references this document via `/goal` in the main development chat to run it. This file is authoritative for scope, current priorities and completion criteria; existing development records and research material provide implementation context.

2026-10-24 additional user authorization: items that lack a personal API or GPU resource may keep their interface/config entry point and a pending-test note, with the user supplying the resource later; this does not block the rest of the first-release deliverables. Confirmed that D15 has no personal GPU; do not rent one and do not use company resources. For items missing resources, finish whatever is doable now (template, inputs, documentation, error messages) and never describe them as tested. Continue all other executable work. The overall acceptance below applies this resource exception.

## 1. Overall goal

Bring Open RSI / RSI-Anything to a first-release demo version that can be shown publicly, installed and run by other users, and covers the 15 domain cases below. Deliver the full generic loop, domain templates, real multi-round experiments, viewable artifacts, a unified showcase, installation instructions and handoff docs.

This is an initial release aimed mainly at demo impact and reach. The point is to show: the user gives a goal, the AI actually modifies an artifact, tool execution and review produce feedback, the system keeps the better version and keeps trying. Basic rules, programmatic metrics and one usable model judge are enough for the first round of development.

Prioritize producing the real workflow and real outputs. Engineering work should first solve normal operation, result persistence, necessary timeout cleanup and user onboarding. Complex judge research, strong adversarial isolation, large-scale statistical validation and advanced search algorithms are later enhancements.

The showcase may pick representative successful cases, but must keep every round of that run. Stalls, failures and rejections are allowed; scores need not rise every round. A model-judge score only describes the result under that evaluation; show how the actual work changed, and do not equate it with real business value.

## 2. How to execute

After the user starts the Goal, first inspect the project and environment and form an execution plan, then go straight into development, experiments and verification, and keep pushing until the completion criteria are met. Do not stop at auditing, research or planning.

Maintain an execution table in `docs/GOAL-PROGRESS.md`. For each item state: status, concrete task, dependencies, acceptance criteria, artifact or record path, next step. Statuses are "To do, In progress, Waiting on external condition, Accepted". Stage results may be reported, but finishing a stage is not finishing the overall Goal.

Run low-cost validation first, then scale up experiments. For technical problems, proactively read logs, inspect code, check relevant history and official docs, and try a minimal fix. Make ordinary implementation choices yourself. When an account, extra cost or asset license is genuinely needed, raise these with the user in one batch and continue other work that does not depend on them.

When hitting permission limits, follow the current tool's requirements and do not bypass them. Respect budgets and stop conditions set by the user and system; running out of budget is not task completion. Mark the overall Goal complete only when all required deliverables pass acceptance; externally blocked items still count as incomplete, and their status is handled per the Goal tool's rules.

Keep progress updates to the user short, in Simplified Chinese and in plain language: only important results, real blockers and decisions needed. Put in-depth investigation, command entry points and details into project files.

## 3. Restore context before starting

Read as needed:

1. `docs/DEMO-PLAN.md`: the four existing demos, actual results and initial direction.
2. `docs/DEVLOG.md`, `.agents/WORKLOG.md`: development records and known issues.
3. `docs/PLAN.zh-CN.md`: architecture and domain extension design.
4. `docs/research/`: earlier research and open-source component reviews.
5. `src/`, `tests/`, `examples/`: implementation, tests and historical artifacts.
6. Applicable `AGENTS.md` files in the repo, plus commit identity and privacy rules.

Check the current branch, remotes, uncommitted changes and running tasks, and preserve existing work. Existing development is mainly on `rebuild`; re-verify the current state to avoid editing the same code as another chat. When isolation is needed, follow existing conventions and never discard uncommitted changes.

Historical baseline: code speedup and copywriting have complete records; prompt optimization has only partial records; video has a template. Login checks, process cleanup and some docs were once uncommitted; at start, the actual Git state is authoritative.

Check that a usable execution agent and model configuration exist, along with Python, Git, video processing and other dependencies. Do not use company internal accounts, data or infrastructure for this personal project. Existing personal accounts and authorized resources may continue to be used; for any new paid resource, explain purpose and cost first.

## 4. Research must serve concrete implementation

Build on existing research, and for components actually used in this round, check the official repos, docs and examples. Every selection answers four questions: what concrete problem it solves, what the minimal integration is, what the dependencies and costs are, and what visible gain it brings over the current implementation.

Record official sources, date consulted, version chosen and the actual call site. Distinguish components actually used, ideas referenced and candidates. Reuse the existing main loop; do not bring in duplicate orchestration or search systems just to add project names.

Do enough research to decide the integration, then do a minimal validation. Keep researching when you hit concrete implementation obstacles; do not make researching every domain thoroughly a precondition for starting.

## 5. Generic engine acceptance

| Capability | First-release completion criteria |
|---|---|
| Task config | Goal, input materials, editable files, execution steps, evaluation method and stop conditions are explicit |
| Model calls | At least one configuration actually runs end to end, recording the actual model, call method and necessary parameters |
| Multi-round runs | Keep trying from the current best version; record accepts, rejects, failures and stalls |
| External tools | Support commands for testing, training, video rendering, material processing, etc. |
| Artifact persistence | Initial, per-round and final artifacts have stable paths and are not lost to temp-directory cleanup |
| Interruption handling | After a normal stop, timeout or restart, completed work is recognized and expensive steps are not repeated unintentionally |
| Resource control | Set rounds, per-step timeout and run duration; show call volume or cost when available |
| Export | Task config, rounds, artifacts, key changes and report can be saved and shared as a whole |

Only extract shared needs that have actually appeared. Keep domain-specific logic in domain packs first; do not refactor the whole system for hypothetical extensions.

## 6. The 15 required domain cases

| ID | Domain and concrete demo | What changes each round | Minimal acceptance and showcase |
|---|---|---|---|
| D01 | Engineering speedup: fuzzy search | Search implementation | Fixed basic correctness checks, speed results, key changes; prefer reusing the existing full experiment |
| D02 | Engineering repair: fix a small Python project | Business code | Fixed tests, round-by-round fixes, final runnable example |
| D03 | Prompting: food-delivery customer service 8-way classification | `prompt.md` | Initial and final prompt, accuracy, error cases, final result on the existing held-out set |
| D04 | Algorithms and training: small CPU classifier | Parameters, preprocessing or training code | Fixed split, metrics, time taken, change in misclassifications, final config |
| D05 | Social-media copywriting and writing guide | Article and reusable guide | Multi-round changes to a single piece; guide used on several briefs, then on a new brief |
| D06 | Video editing: talking-head footage to short clip | Segment selection, order and necessary parameters | Source footage, first cut, intermediate clips and final cut all playable |
| D07 | Video generation: brief to short video | Generation prompt and parameters | Real generation API calls, multi-round clips, how well requirements are met, playable comparison |
| D08 | Financial research: business analysis from fixed materials | Body structure, argumentation and charts | Sources, numeric consistency, report versions and final draft |
| D09 | Quant research: simple strategy backtest | Strategy rules or parameters | Fixed historical data, transaction costs, backtest curve and drawdown; state that it is a historical simulation |
| D10 | Humanities research: review of given materials | Structure, arguments and evidence organization | Source mapping, citations, coverage, before/after comparison of the text |
| D11 | Legal text: issue review of a sample contract | Issue list and text suggestions | Against preset issues and given materials, show omissions and improved wording; restricted to example use |
| D12 | Medical explainer: source material to public explanation | Information organization and wording | Use clearly sourced materials, check consistency and coverage of key points, show readability changes; restricted to popular-science use |
| D13 | Learning and education: handouts and exercise explanations | Handout, worked examples and explanations | Performance on fixed exercises, key explanation changes, final learning material |
| D14 | Life planning: one-week schedule | Time allocation and arrangement | Check conflicts, coverage and preferences; show before/after schedule |
| D15 | Inference acceleration and GPU kernel optimization | Implementation and launch parameters of one common kernel | Numeric checks, single-kernel multi-round timing, small inference module swap comparison, code changes and device info; implement per `research/F-kernel-inference-demo.md` |

Every case needs default inputs, an entry point for replacing them with user inputs, a launch method, an evaluation description and real experiment records. A generic engine that is "configurable in theory" does not count as a finished domain demo. Retitling one case does not count as another domain pack.

Model-generation tasks must actually call models or tools. Synthetic data or assets may be used for development but must be labeled with their source; hand-prepared inputs, templates and showcase layouts are allowed, but a hand-written candidate sequence must not be called automatic iteration.

For D15's first case, pick one of public Softmax, normalization or fused computation, reuse the existing RSI main loop, and reference public projects such as AutoKernel, KernelBench and Triton. Optimize the single kernel first, then put it into a small inference module to measure the overall effect; GPU measurements run only on available, authorized personal resources. Without a device, finish the executable template and docs first and leave the GPU experiment pending.

## 7. Four implementation batches and deliverables

### Batch 1: existing results and shared capabilities

- Organize D01's existing code-speedup evidence; rerun only when changes require revalidation.
- Complete one full D03 run, keeping the original partial experiments and not overwriting the original records.
- Add D05's per-round copywriting artifacts and comparisons.
- Fill in model config, timeout handling, artifact persistence and export where they affect the tasks above.
- Run the relevant tests the project's current way, and actually walk the path from launch to viewing results.

Deliverables: several complete cases viewable directly, plus a unified result-directory convention.

### Batch 2: main promotional showcase

- Focus on a real talking-head edit for D06, using existing transcription and FFmpeg first; add targeted components when needed.
- Evaluate the first editing version by post-cut text, duration, sentence count, etc.; manually check the final cut for playability and obvious cut problems.
- Complete D05's writing-guide iteration: a fixed writer generates drafts from the guide for several briefs, feedback is aggregated to revise the guide, and finally the result on a new brief is shown.
- Build unified result browsing in parallel, showing the first draft, intermediate versions, best version and per-round reasons.
- If a compatible, authorized GPU is already available, advance D15 in the same batch, making real kernel optimization the main technical showcase; otherwise prepare the template and run instructions first, and run it for real in Batch 3 once the device condition is resolved.

Deliverables: playable before/after video comparison, browsable copywriting and guide changes, a previewable showcase entry point.

### Batch 3: remaining domains

- Prioritize the lower-dependency D02, D04, D08, D10, D13, D14.
- D11 and D12 use clearly bounded example tasks and given materials.
- Complete the higher-dependency D09 and D07; when accounts or resources are missing, list the specific blockers and move on to other tasks.
- Complete D15's multi-round GPU experiment and small inference module comparison. Public selection and source boundaries are in `docs/research/F-kernel-inference-demo.md`.
- For each domain, first do one complete small case, choosing the shortest existing tool integration based on actual conditions.

Deliverables: status and result entry points for all 15 items; unfinished items are explicitly kept and not counted as accepted.

### Batch 4: product polish

- Unify template naming, input docs, launch method, output directories and error messages.
- Write complete Chinese and English READMEs with the easiest getting-started example.
- Complete the case collection entry point, installation and personal account setup guide, FAQ, extension tutorial and open-source acknowledgments.
- Prepare a short demo plus necessary screenshots, GIFs or video; promotional text must correspond to real artifacts.
- From a new user's perspective, check the full path of installing, launching, viewing results and replacing inputs.
- Prepare the first-release build or install artifact, and check that the package contains templates and necessary resources.

Deliverables: a locally previewable, installable and runnable first-release candidate with complete docs. Public release, posting, purchasing resources or changing the main branch require explicit user authorization.

## 8. Concrete requirements for multi-round results

First list the room for improvement in each task: audience, opening and structure for copywriting; opening, redundancy and order for editing; parameters and preprocessing for training; data interpretation, arguments and risks for research reports.

Run short experiments first to confirm the feedback produces a meaningful next step, then do demo runs, typically 5–8 rounds. Existing complete experiments may be reused. If the goal is reached early, record the stop reason; if the model or environment fails, locate the cause first.

Flagship cases should have several intermediate versions worth showing. When results fall short, examine the task, materials, feedback and model, then set up a new experiment with a clear rationale for improvement. Keep evaluation criteria consistent within a run; after changing rules or data, start a new record.

Ordinary cases must complete at least one real multi-round run with an explainable result. Records with only a baseline, a single round or an aborted run are marked partially complete. Weak demo results may be improved further, but never by hiding failures or altering scores to fake a continuous rise.

## 9. Unified showcase requirements

Each case page or report contains the task and inputs, initial artifact, per-round changes and reasons, accept or reject results, final artifact, metric changes, models and tools, time and a reproduction entry point.

Videos use a player; articles support version comparison; code shows key changes; training shows curves and error cases; reports show body text and charts; schedules use a readable view. Build on the existing report infrastructure first and add display capabilities as actually needed; do not default to building a complex backend.

Finish local preview first. When deployment or publishing is needed, confirm the target and user authorization, and deliver per the applicable publishing and directory registration rules. Unauthorized public release is not a step to take on your own.

## 10. Docs, commits and privacy

During execution, maintain the current plan, architecture notes, per-domain usage, open-source sources, experiment records and handoff notes. Files directly describe the retained implementation and current state; remove outdated conclusions and conflicting instructions.

Save work in complete small batches; commit and push within the scope the user has authorized, using the anonymous identity required by the personal repo. Never include secrets, company information, internal addresses or local username paths. Do not force-push, do not overwrite other chats' changes, and do not automatically merge or publish a formal release.

Non-public materials are used only to understand general problems. The project uses methods that public materials can independently support, self-written code and public components whose licenses allow it; do not copy, cite, rewrite or port internal code, text, configs, private algorithm details, data, performance numbers, images or links. Do not attach internal materials to generation tasks, and do not get around these boundaries by renaming or translating. Public code keeps the necessary copyright, license and acknowledgments.

The final handoff should let another computer, or a Codex or Opus without the original conversation, continue just by reading the docs. List the actual commands run, result locations, reusable lessons, remaining problems and the next concrete task.

## 11. Overall Goal acceptance

Check each item:

1. D01–D15 all have actually runnable minimal cases; cases whose resources are available have real multi-round records. Per the user's 2026-10-24 authorization, cases lacking API/GPU resources complete the template, config entry point, no-resource check and handoff notes, and may be delivered as explicit pending-test items. D15 adds real multi-round runs and the small inference module comparison after a personal GPU is obtained; CPU or simulated results do not substitute.
2. Flagship cases have directly comparable initial, intermediate and final artifacts.
3. The generic engine, template installation and user onboarding path have been actually verified.
4. Relevant tests pass; actual artifacts can be read, played or run.
5. Unified showcase, READMEs, domain docs, open-source sources, experiment records and handoff materials are all in place.
6. Work is saved, committed and synced within the authorized scope, and the user can find the actual deliverables.

Finally, list in one table each case's status, result, run records, artifacts and launch entry point, and separately list blockers that actually exist. Resource-exception items are listed separately as pending-test per the additional authorization above and do not count toward the number of real multi-round successes; other items with only a template, partial experiments or passing tests remain incomplete. Except for the explicitly authorized resource exceptions, the overall Goal must not be marked complete while any required item is unfinished.

## 12. Goal usage reference

Codex's `/goal` is for continuously pursuing a goal with completion criteria; pausing, resuming and clearing are controlled by the user, and budget and runtime environment limits still apply. [OpenAI official docs](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)
