# D11: Three review rounds on a fictional design-services contract

[简体中文](README.zh-CN.md)

The input was written entirely by the project author; it isn't a user's real contract. The AI went from discussing only two issue categories to covering seven: delivery scope, payment, changes and scheduling, acceptance and rework, rights in materials, termination and settlement, and client data. It also wrote draft clauses for both parties to discuss.

| Version | Score | Outcome |
|---|---:|---|
| Starting | 41 | Validly located 2/7 issue categories |
| Round 1 | 91.5 | Kept; validly located 7/7 issue categories |
| Round 2 | 0 | Rejected; the I6 suggestion exceeded the fixed length limit, so the model judge wasn't called |
| Round 3 | 87 | Rejected; did not beat the currently kept draft |

[Open the full experiment report](runs/20261024-002852-design-contract-review/report.html) · [Read the final discussion draft](runs/20261024-002852-design-contract-review/artifacts/final/files/out/review.html) · [Structured issue list](runs/20261024-002852-design-contract-review/artifacts/final/files/review.json) · [Independent verification record](runs/20261024-002852-design-contract-review/verification.json)

In round 2, the I6 suggestion was 1205 characters, over the 1200-character limit, so the program didn't count it as valid coverage and rejected the round before scoring. That round still included all seven issue IDs. The score of 0 means it failed this fixed requirement; it can't be read as "found no issues" or "the legal analysis was all wrong". The original candidate and the reason for the failure are kept in full.

The final draft was read item by item, and the seven clause locations, quoted sentences and suggestion lengths were checked independently. The draft clearly marks new amounts, deadlines and license scopes as pending confirmation by both parties. It doesn't invent statutes or case law, doesn't assert the validity of a real contract, and doesn't assume third-party rights can be transferred directly. The suggestions are still long, and the parties would need to keep working on the attachments and open items. Full ID coverage doesn't mean the contract is ready to sign.

The exported starting version, the three round candidates and the final version were each rerun through the frozen prepare script, and the generated files matched byte for byte. Both the agent and the model judge explicitly requested `gpt-6.1-sol` at `medium` through a personal Codex account; the CLI didn't return the actual model or cost, so both stay unknown. A model score isn't a lawyer's review, and this example isn't legal advice.

To start a new experiment with your own personal Codex login, run this from the project root:

```bash
python3 scripts/run_demo.py contract-review --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

The review guide was written by the author and only draws on [the contract essentials from business.gov.au](https://business.gov.au/people/contractors/prepare-a-contract); the original page was opened and checked on 2026-10-24 for this run. Its notes on Australian law aren't applied to this fictional contract.
