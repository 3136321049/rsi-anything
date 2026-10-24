from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

import pytest

from rsi_anything import llm
from rsi_anything.agents.cli import CLIAgent, _run
from rsi_anything.agents import registry
from rsi_anything.judges.command import CommandJudge


@pytest.fixture
def fake_cli(tmp_path):
    executable = tmp_path / "fake-cli"
    calls = tmp_path / "calls.jsonl"
    pids = tmp_path / "pids.json"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, os, pathlib, subprocess, sys\n"
        f"with open({str(calls)!r}, 'a') as out: out.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "if sys.argv[1:] == ['--version'] and not os.environ.get('TEST_PROBE_TIMEOUT'):\n"
        "    print('1.0'); sys.exit(0)\n"
        "if sys.argv[1:3] == ['auth', 'status']:\n"
        "    logged_in = os.environ.get('TEST_LOGGED_IN') == '1'\n"
        "    print(json.dumps({'loggedIn': logged_in})); sys.exit(0 if logged_in else 1)\n"
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        f"pathlib.Path({str(pids)!r}).write_text(json.dumps({{'parent': os.getpid(), 'child': child.pid}}))\n"
        "print('已启动子进程', flush=True)\n"
        "child.wait()\n"
    )
    executable.chmod(0o700)
    spec = registry.CLISpec("claude", str(executable), "Claude", "global", "claude-json")
    return spec, calls, pids


def assert_stopped(pid):
    for _ in range(50):
        result = subprocess.run(["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True)
        state = result.stdout.strip()
        if not state or state.startswith("Z"):
            return
        time.sleep(0.02)
    pytest.fail(f"超时后仍有存活进程：{pid}")


@pytest.mark.skipif(os.name != "posix", reason="验证 POSIX 进程组清理")
@pytest.mark.parametrize("entry", ["ask", "probe", "round", "judge", "prepare"])
def test_timeout_stops_descendants(entry, fake_cli, tmp_path, monkeypatch):
    spec, _, pids = fake_cli
    monkeypatch.setitem(registry.CLI_AGENTS, "claude", spec)
    monkeypatch.setattr(registry, "_READY", {})
    monkeypatch.setenv("TEST_LOGGED_IN", "1")
    try:
        if entry == "ask":
            with pytest.raises(llm.LLMError, match="timed out"):
                llm._ask_cli(llm.parse("cli:claude"), "测试输入", [], 1)
        elif entry == "probe":
            monkeypatch.setenv("TEST_PROBE_TIMEOUT", "1")
            assert not registry.ready(spec, timeout=1)
        elif entry == "round":
            result, _ = _run([spec.binary], tmp_path, "测试输入", None, 1, tmp_path / "agent.log")
            assert result is None
        else:
            from types import SimpleNamespace
            judge = CommandJudge(SimpleNamespace(run=shlex.quote(spec.binary), timeout=1,
                                                prepare=shlex.quote(spec.binary)))
            result = judge._prepare(tmp_path, 0) if entry == "prepare" else judge._once(tmp_path, 0)
            assert "timed out" in result.error
        recorded = json.loads(pids.read_text())
        assert_stopped(recorded["parent"])
        assert_stopped(recorded["child"])
    finally:
        # 断言失败时也清理假命令，测试不留下后台进程。
        if pids.exists():
            import signal
            for pid in json.loads(pids.read_text()).values():
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass


def test_unauthenticated_cli_never_receives_prompt(fake_cli, tmp_path, monkeypatch):
    spec, calls, _ = fake_cli
    monkeypatch.setitem(registry.CLI_AGENTS, "claude", spec)
    monkeypatch.setattr(registry, "_READY", {})
    monkeypatch.delenv("TEST_LOGGED_IN", raising=False)
    assert not registry.ready(spec)
    with pytest.raises(llm.LLMError, match="尚未登录"):
        llm._ask_cli(llm.parse("cli:claude"), "不应传给未登录命令的输入", [], 1)
    agent = CLIAgent(spec, "", [], False)
    result = agent.run(tmp_path, "不应传给未登录命令的输入", tmp_path, 1)
    assert not result.ok and "尚未登录" in result.error
    arguments = [json.loads(line) for line in calls.read_text().splitlines()]
    assert arguments and all(args == ["--version"] or args == ["auth", "status", "--json"]
                             for args in arguments)
