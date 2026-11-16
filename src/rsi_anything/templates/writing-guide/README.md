# Reusable writing guide

[简体中文](README.zh-CN.md)

This case is the guide half of D05. Each round, the AI changes `writing-guide.md`. A fixed writer model then actually writes copy for three briefs, and the judge scores it on reader fit, organization, voice and call to action. A separate new brief is used at the start and at the end. All briefs are fictional product material written independently for this project.

After installing this project and signing in to a personal coding agent:

```bash
rsi init writing-guide guide-demo
cd guide-demo
export RSI_WRITER_MODEL=cli:codex:gpt-6.1-sol
rsi check --jury cli:codex:gpt-6.1-sol
rsi run --agent codex --model gpt-6.1-sol --jury cli:codex:gpt-6.1-sol --rounds 5
rsi report
```

Fix the writer and judge models before running. Each round includes three writer calls, plus scoring and possibly a head-to-head comparison of the new and current versions. Use a personal subscription you already have or your own API access; no resources are bought automatically. Choose model names based on what your personal account can actually use.

Replacing inputs: edit `judge/briefs.json`, giving each brief a distinct `id`, product name, target reader, facts and call to action. Put the new brief in `holdout/briefs.json`. Commit the material before starting a new experiment. You can open `out/posts.html` directly. Each draft, the call metadata and any errors are in `out/` and are saved with each round. Model scores are feedback from this judge, not actual clicks or sales.

The only dependencies are this project's model-calling layer and the Python standard library; no external optimization engine is imported. The template is implemented; for the current real multi-round status, go by the records in `examples/writing-guide/`.
