# D11: Sorting out issues in a synthetic contract

[简体中文](README.md)

The default material is a fictional design-services contract written by the project author. It contains seven categories of issues: delivery scope, payment, changes and scheduling, acceptance and rework, rights in materials, termination and settlement, and use of client data. It isn't a user's real contract, and the template doesn't judge whether a contract is valid.

```sh
rsi init contract-review demo-contract
cd demo-contract
python3 judge/prepare.py
rsi run --rounds 6
```

The agent edits only `review.json`. Each item has an `issue_id`, a `clause_id`, the original `quote`, the `risk` of dispute and a `suggestion`; the IDs come from `judge/review-guide.json`. The default starting draft discusses only two issue categories, which leaves room to find omissions, explain consequences and improve clauses.

The program checks clause locations, quoted sentences and content length, and reports coverage of the seven issue categories. The model judge separately rates the risk explanations, the suggested revisions and readability. Covering an ID doesn't mean the suggestion for it is adequate. The review criteria and the contract are both frozen; the starting draft and later candidates aren't a pre-written sequence played back.

`out/review.html` and `review.md` are the readable report, `coverage.json` records locations and gaps, and the other files are for the review; `outputs: [out]` saves each round's outputs. The prepare script uses only the Python standard library and can run offline; multi-round runs need your own agent or personal model account.

To change the material, edit `judge/contract.json` and `review-guide.json` before a new run, and update the starting draft and scoring rubric to match. The exercise criteria were written by the author and only draw on [the contract essentials from business.gov.au](https://business.gov.au/people/contractors/prepare-a-contract); Australian law isn't applied to this example. Sources were checked on 2026-10-24.

Every finished draft keeps the "示例、不构成法律意见" note ("an example; not legal advice"). A real three-round experiment is complete: the final kept score rose from 41 to 91.5, covering all seven preset issue categories. The records and per-version re-verification are saved in the repository under `examples/contract-review/`.
