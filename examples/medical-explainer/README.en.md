# D12: Physical activity guidelines as common sense for an office workday

[简体中文](README.md)

This real three-round experiment edited only the health explainer, using frozen WHO material. Built around commuting, breaks at work and planning activity, the final draft explains what aerobic activity, muscle strengthening and reducing sedentary time each address. It keeps the scope (generally healthy adults) and the advice to start small.

| Version | Score | Outcome |
|---|---:|---|
| Starting | 58.5 | Baseline |
| Round 1 | 80 | Kept; uses everyday scenarios to explain terms, activity types and common misreadings |
| Round 2 | 77.5 | Rejected; did not beat the current draft |
| Round 3 | 77.5 | Rejected; round 1 remains the final version |

[Open the full experiment report](runs/20261024-001506-adult-activity-explainer/report.html) · [Read the final explainer and sources](runs/20261024-001506-adult-activity-explainer/artifacts/final/files/out/explainer.html) · [Final Markdown](runs/20261024-001506-adult-activity-explainer/artifacts/final/files/out/explainer.md) · [Verification record](runs/20261024-001506-adult-activity-explainer/verification.json)

The final draft was read paragraph by paragraph, and the fixed age, activity amounts and frequencies were checked. It contains no medication advice, diagnoses, promises about treating disease, or exercise prescriptions for a specific person. The examples and plain-language explanations are the article's own wording, not quotations from WHO. It clearly distinguishes light movement from moderate-to-vigorous activity, and doesn't treat meeting the aerobic amount as the whole of the physical activity recommendations.

The exported starting version, the three round candidates and the final version were all rerun through the frozen prepare script, and the outputs matched byte for byte. A browser displayed the text, the four guideline quantities and the source links. This run used the scoring rule that can check quotes made of several separate passages. Quote matching triggered no deductions in any of the four scorings, and the raw judge JSON for each is saved under `judge_details` in `verdict.json`. The difference between 77.5 and 80 is still a single model evaluation, not a judgment of clinical effectiveness.

Both the agent and the judge explicitly requested `gpt-6.1-sol` at `medium` through a personal Codex account; the CLI didn't return the actual model or cost, so both stay unknown. This case only demonstrates organizing and rewriting a public health explainer. It doesn't accept medical records and hasn't been reviewed by a clinical expert.

To start a new experiment with your own personal Codex login, run this from the project root:

```bash
python3 scripts/run_demo.py medical-explainer --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 3 --minutes 25 --codex-isolated --continue-after-target
```

The sources are [the WHO/Europe physical activity fact sheet](https://www.who.int/europe/news-room/fact-sheets/item/physical-activity), [the WHO physical activity fact sheet](https://www.who.int/news-room/fact-sheets/detail/physical-activity) and [the executive summary of the WHO guidelines](https://www.ncbi.nlm.nih.gov/books/NBK566048/?report=reader). On 2026-10-24, the WHO main site and the official search index were checked. Reading the Europe page directly timed out, and reading NCBI directly hit a CAPTCHA, so the passages on age, activity amounts, strengthening frequency and starting gradually were read through the official index. There's no claim that the full guidelines were reread.
