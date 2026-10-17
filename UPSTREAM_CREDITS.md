# Standing on the Shoulders of Open Source

> RSI-Anything is an independent project. Inspiration is not authorship, and
> interoperability is not endorsement. No upstream project is presented as a
> dependency unless the relevant integration explicitly says so.

Great ideas should compound **without erasing their provenance**. RSI-Anything
uses the Three-Tier Attribution Protocol below so that credit travels with an
idea from source metadata, through runtime output, into a public discovery
loop.

## The Three-Tier Attribution Protocol

### Tier 1 — `ATTRIBUTION.yaml`: machine-readable provenance

Every imported method, adapter, benchmark, prompt pattern, dataset, or
substantial design influence should add an entry at the repository root. The
contract is intentionally small enough to copy into any project:

```yaml
version: 1
project: rsi-anything
updated: 2026-10-17
upstreams:
  - id: karpathy/autoresearch            # stable owner/repository identifier
    url: https://github.com/karpathy/autoresearch
    authors: [Andrej Karpathy]
    relationship: inspiration            # inspiration|integration|derivative|data
    contributions:
      - Git-as-ratchet experiment history
      - fixed-budget autonomous experiment loop
    used_in:
      - skills/rsi-loop
    license: verify-upstream              # SPDX ID when known; never guess
    revision: null                        # commit/tag required for copied material
    notices: []
```

**Contract rules**

1. `version`, `project`, and `upstreams` are required; every upstream requires
   `id`, `url`, `relationship`, `contributions`, and `used_in`.
2. Use `relationship: derivative` when code, prose, prompts, or assets are
   adapted. Record the exact `revision`, SPDX license, and required notices.
3. Use `inspiration` only for independently implemented ideas. It is not a
   substitute for license compliance.
4. Paths in `used_in` must be repository-relative and reviewable. Unknown
   authors or licenses must be marked `unknown` or `verify-upstream`, never
   invented.
5. CI should reject malformed entries, dead URLs, missing derivative revisions,
   and removals that leave referenced material unattributed.

### Tier 2 — Runtime Banner Attribution: credit where value appears

Commands that activate an attributed method print one compact banner once per
run. Quiet and machine-readable modes may redirect it to metadata, but must not
discard it.

```text
┌─ RSI-Anything · upstream credit ──────────────────────────────────────┐
│ Method: Git-as-ratchet + fixed-budget loop                           │
│ Inspired by: karpathy/autoresearch · https://github.com/karpathy/autoresearch
│ Full provenance: ./ATTRIBUTION.yaml                                  │
└───────────────────────────────────────────────────────────────────────┘
```

Adapters should also expose the same records in their result metadata under
`attribution.upstreams[]`. Runtime credit is informational; copyright notices
and license files still travel with derivative material.

### Tier 3 — Star Leaderboard: turn credit into discovery

The project homepage renders a leaderboard from `ATTRIBUTION.yaml`. Stars are
fetched from the GitHub API, cached, and stamped with `as_of`; they are never
hard-coded or treated as a quality score. Ties sort alphabetically. Every row
links upstream, and every runtime banner links back to the full record.

| Upstream | Live stars | Why explore it |
|---|---:|---|
| [anthropics/claude-code](https://github.com/anthropics/claude-code) | ![GitHub stars](https://img.shields.io/github/stars/anthropics/claude-code?style=flat-square&label=%E2%98%85) | Agentic coding and the `ralph-wiggum` plugin |
| [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) | ![GitHub stars](https://img.shields.io/github/stars/stanfordnlp/dspy?style=flat-square&label=%E2%98%85) | Declarative LM programs and reflective optimization |
| [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | ![GitHub stars](https://img.shields.io/github/stars/assafelovic/gpt-researcher?style=flat-square&label=%E2%98%85) | Autonomous, source-rich research synthesis |
| [karpathy/autoresearch](https://github.com/karpathy/autoresearch) | ![GitHub stars](https://img.shields.io/github/stars/karpathy/autoresearch?style=flat-square&label=%E2%98%85) | Minimal autonomous experiment loops |
| [zou-group/textgrad](https://github.com/zou-group/textgrad) | ![GitHub stars](https://img.shields.io/github/stars/zou-group/textgrad?style=flat-square&label=%E2%98%85) | Textual gradients |
| [stanford-oval/storm](https://github.com/stanford-oval/storm) | ![GitHub stars](https://img.shields.io/github/stars/stanford-oval/storm?style=flat-square&label=%E2%98%85) | Multi-perspective, citation-grounded reports |
| [Future-House/paper-qa](https://github.com/Future-House/paper-qa) | ![GitHub stars](https://img.shields.io/github/stars/Future-House/paper-qa?style=flat-square&label=%E2%98%85) | Evidence-grounded scientific Q&A |
| [SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) | ![GitHub stars](https://img.shields.io/github/stars/SakanaAI/AI-Scientist-v2?style=flat-square&label=%E2%98%85) | End-to-end AI science |
| [jennyzzt/dgm](https://github.com/jennyzzt/dgm) | ![GitHub stars](https://img.shields.io/github/stars/jennyzzt/dgm?style=flat-square&label=%E2%98%85) | Darwin Gödel Machine |
| [SamuelSchmidgall/AgentLaboratory](https://github.com/SamuelSchmidgall/AgentLaboratory) | ![GitHub stars](https://img.shields.io/github/stars/SamuelSchmidgall/AgentLaboratory?style=flat-square&label=%E2%98%85) | Collaborative research agents |
| [google-research/rrsi](https://github.com/google-research/rrsi) | ![GitHub stars](https://img.shields.io/github/stars/google-research/rrsi?style=flat-square&label=%E2%98%85) | Regularized self-improvement |
| [greyhaven-ai/autocontext](https://github.com/greyhaven-ai/autocontext) | ![GitHub stars](https://img.shields.io/github/stars/greyhaven-ai/autocontext?style=flat-square&label=%E2%98%85) | Persistent agent context |
| [A-EVO-Lab/a-evolve](https://github.com/A-EVO-Lab/a-evolve) | ![GitHub stars](https://img.shields.io/github/stars/A-EVO-Lab/a-evolve?style=flat-square&label=%E2%98%85) | Evolutionary agent improvement |
| [frankbria/ralph-claude-code](https://github.com/frankbria/ralph-claude-code) | ![GitHub stars](https://img.shields.io/github/stars/frankbria/ralph-claude-code?style=flat-square&label=%E2%98%85) | Guardrailed Ralph loops |
| [aaronsb/chief-wiggum](https://github.com/aaronsb/chief-wiggum) | ![GitHub stars](https://img.shields.io/github/stars/aaronsb/chief-wiggum?style=flat-square&label=%E2%98%85) | Kanban and worktree orchestration |
| [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | ![GitHub stars](https://img.shields.io/github/stars/wanshuiyin/Auto-claude-code-research-in-sleep?style=flat-square&label=%E2%98%85) | Research-in-sleep workflows |
| [brycewang-stanford/Auto-Research-Skills](https://github.com/brycewang-stanford/Auto-Research-Skills) | ![GitHub stars](https://img.shields.io/github/stars/brycewang-stanford/Auto-Research-Skills?style=flat-square&label=%E2%98%85) | Research skill discovery and curation |
| [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | ![GitHub stars](https://img.shields.io/github/stars/Orchestra-Research/AI-Research-SKILLs?style=flat-square&label=%E2%98%85) | Two-loop research orchestration |
| [morluto/rea](https://github.com/morluto/rea) | ![GitHub stars](https://img.shields.io/github/stars/morluto/rea?style=flat-square&label=%E2%98%85) | Reverse-engineering evidence workflows |

## Detailed lineage

The table records **specific intellectual influence**, not a claim that upstream
authors contributed to or endorse RSI-Anything.

| Upstream and people | What we learned | How it appears here |
|---|---|---|
| **[karpathy/autoresearch](https://github.com/karpathy/autoresearch)** · Andrej Karpathy | Git-as-ratchet, the `program.md` paradigm, and a fixed-budget overnight experiment loop | The universal loop keeps only measured wins, makes the operating program editable, and treats history as experimental evidence. |
| **[morluto/rea](https://github.com/morluto/rea)** · Reverse Engineer Anything contributors | MCP + Skill bridge architecture and evidence-first verification | Agent skills remain portable while tools supply evidence; assertions must point to reproducible observations. |
| **[anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)** (`plugins/ralph-wiggum`) · Anthropic and Geoffrey Huntley; **[frankbria/ralph-claude-code](https://github.com/frankbria/ralph-claude-code)** · Frank Bria; **[aaronsb/chief-wiggum](https://github.com/aaronsb/chief-wiggum)** · Aaron SB | Ralph Loop continuous execution, dual-condition exit gates, and Kanban worktree workers | `/rsi-kanban` requires both objective tests and review gates before completion, with isolated workers and bounded retries. |
| **[wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)** · ARIS contributors | Markdown-first research-in-sleep workflow and cross-model review gates | Deep-report state is inspectable on disk and must survive independent critique before delivery. |
| **[brycewang-stanford/Auto-Research-Skills](https://github.com/brycewang-stanford/Auto-Research-Skills)** and **[Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs)** · project contributors | Ecosystem curation, the `STARS.md` attribution flywheel, and two-loop research orchestration | This leaderboard makes credit discoverable; report production separates retrieval/evidence work from synthesis/revision. |
| **[google-research/rrsi](https://github.com/google-research/rrsi)**, **[greyhaven-ai/autocontext](https://github.com/greyhaven-ai/autocontext)**, and **[A-EVO-Lab/a-evolve](https://github.com/A-EVO-Lab/a-evolve)** · project contributors | Regularized harness evolution and persistent lessons/playbooks | The evaluator is frozen before optimization; durable, generalized wins graduate into memory and then skills. |
| **[zou-group/textgrad](https://github.com/zou-group/textgrad)** and **[stanfordnlp/dspy](https://github.com/stanfordnlp/dspy)** (`GEPA`) · project contributors | Textual gradients and reflective prompt evolution | Rubric failures become actionable critiques, then controlled prompt or workflow mutations—not unmeasured rewrites. |
| **[SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2)**, **[SamuelSchmidgall/AgentLaboratory](https://github.com/SamuelSchmidgall/AgentLaboratory)**, and **[jennyzzt/dgm](https://github.com/jennyzzt/dgm)** · project contributors | Automated scientific workflows, research-agent collaboration, and the Darwin Gödel Machine | RSI-Anything borrows the ambition of systems that improve the process that creates the next candidate, while retaining hard gates and rollback. |
| **[stanford-oval/storm](https://github.com/stanford-oval/storm)**, **[assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher)**, and **[Future-House/paper-qa](https://github.com/Future-House/paper-qa)** · project contributors | Deep research synthesis and verified-citation retrieval-augmented generation | `/rsi-report` creates claim-to-source ledgers, challenges contradictory evidence, and blocks unverified citations. |

## Add or correct a credit

Open an issue or pull request with the upstream URL, the concrete influence,
the affected path, and—when material was adapted—the revision and license.
Corrections are treated as integrity fixes, not editorial preferences.

Each upstream retains its own copyright and license. Consult the linked
repository before reusing its code or assets. RSI-Anything's MIT license covers
only material owned by RSI-Anything contributors.
