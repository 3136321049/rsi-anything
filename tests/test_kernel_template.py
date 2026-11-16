"""GPU results are never simulated; only the template and its explicit result in an unavailable environment are checked."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from rsi_anything.contract import load

TEMPLATE = Path(__file__).resolve().parents[1] / "src/rsi_anything/templates/kernel-speed"


def checker():
    spec = importlib.util.spec_from_file_location("kernel_checker_for_test", TEMPLATE / "judge/check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_kernel_contract_and_fixed_cases():
    contract = load(TEMPLATE)
    assert contract.artifact == ["candidate.py"]
    assert contract.judge.min_gain == 0.03
    cases = json.loads((TEMPLATE / "judge/cases.json").read_text())
    assert {case["dtype"] for case in cases["correctness"]} == {"float16", "float32"}
    assert any(case["columns"] % 2 for case in cases["correctness"])
    assert cases["timing"]["samples"] >= 5


def test_probe_unsupported_host_never_imports_gpu_or_candidate(monkeypatch):
    module = checker()
    monkeypatch.setattr(module.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(module.platform, "machine", lambda: "arm64")
    before = set(sys.modules)
    info = module.probe()
    assert info["status"] == "environment_unavailable"
    assert info["device"] is None and "Linux" in info["reason"]
    assert "candidate" not in set(sys.modules) - before
    assert "torch" not in set(sys.modules) - before


def test_probe_missing_dependencies_is_not_zero_score(monkeypatch, tmp_path):
    module = checker()
    monkeypatch.setattr(module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(module.platform, "machine", lambda: "x86_64")
    def missing(name):
        raise module.importlib.metadata.PackageNotFoundError(name)
    monkeypatch.setattr(module.importlib.metadata, "version", missing)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["check.py"])
    target = tmp_path / "judge-result.json"
    monkeypatch.setenv("RSI_RESULT", str(target))
    assert module.main() == 2
    data = json.loads((tmp_path / "out/metrics.json").read_text())
    assert data["score"] is None and data["status"] == "environment_unavailable"
    assert not target.exists()
    assert "simulated" in (tmp_path / "out/report.md").read_text()


def test_real_local_probe_cannot_run_candidate(tmp_path):
    root = tmp_path / "kernel"
    shutil.copytree(TEMPLATE, root, ignore=shutil.ignore_patterns("out", "__pycache__"))
    (root / "candidate.py").write_text("raise RuntimeError('probe must not import candidate')\n")
    result = subprocess.run([sys.executable, "judge/check.py", "--probe"], cwd=root, text=True,
                            capture_output=True, timeout=30, env={**os.environ, "CUDA_VISIBLE_DEVICES": ""})
    assert result.returncode == 2
    data = json.loads((root / "out/metrics.json").read_text())
    assert data["score"] is None and data["status"] == "environment_unavailable"
    assert "probe must not import candidate" not in result.stdout + result.stderr
