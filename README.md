# RSI-Anything

> Work in progress on the `rebuild` branch. Nothing here has been released yet.

Point any coding agent at anything you can score. Each round the agent makes one change, a frozen judge scores
it in a clean copy, and only proven gains are committed to a run branch. Works with Claude Code, Codex, Cursor,
Gemini CLI, Qwen Code, Kimi CLI, CodeBuddy, OpenCode, or any OpenAI-compatible model API.

```bash
uv pip install -e ".[dev]"
rsi init code-speed demo && cd demo
rsi check
rsi run --rounds 5
rsi report
```

Development notes and handoff (Chinese): [docs/DEVLOG.zh-CN.md](docs/DEVLOG.zh-CN.md).
