"""检查 CUDA 环境、固定数值用例，再分别测单算子和推理模块。"""
import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path


def probe():
    info = {"status": "environment_unavailable", "system": platform.system(), "machine": platform.machine(),
            "python": platform.python_version(), "torch": None, "triton": None, "cuda": None,
            "device": None, "reason": ""}
    for name in ("torch", "triton"):
        try:
            info[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    if info["system"] != "Linux" or info["machine"] not in ("x86_64", "AMD64"):
        info["reason"] = "本模板要求 Linux x86_64 和 NVIDIA CUDA GPU；当前平台不支持此路径。"
        return info
    if not info["torch"] or not info["triton"]:
        info["reason"] = "缺少 PyTorch 或 Triton；请在已授权的个人 CUDA 机器按 README 安装。"
        return info
    try:
        import torch
        if not torch.cuda.is_available() or not torch.version.cuda:
            info["reason"] = "没有可用的 NVIDIA CUDA 设备，或安装的是 CPU 版 PyTorch。"
            return info
        properties = torch.cuda.get_device_properties(0)
        info.update(cuda=torch.version.cuda, device=properties.name, capability=list(torch.cuda.get_device_capability(0)),
                    memory_bytes=properties.total_memory)
        if info["capability"][0] < 8:
            info["reason"] = "本模板首版限定 NVIDIA 计算能力 8.0 及以上设备。"
            return info
        try:
            result = subprocess.run(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                                    capture_output=True, text=True, timeout=5)
            info["driver"] = result.stdout.strip().splitlines()[0] if result.returncode == 0 else "unknown"
        except (OSError, subprocess.TimeoutExpired):
            info["driver"] = "unknown"
        info["status"] = "ready_not_measured"
        return info
    except Exception as exc:
        info["reason"] = f"CUDA 环境检查失败：{type(exc).__name__}: {exc}"
        return info


def tensor(torch, case, seed):
    shape = (case["rows"], case["columns"])
    dtype = getattr(torch, case["dtype"])
    generator = torch.Generator(device="cuda").manual_seed(seed)
    if case["pattern"] == "zeros":
        return torch.zeros(shape, device="cuda", dtype=dtype)
    value = torch.randn(shape, generator=generator, device="cuda", dtype=dtype)
    return value * 100 if case["pattern"] == "extreme" else value


def validate(torch, x, expected, implementation, tolerance):
    before = x.clone()
    got = implementation(x)
    torch.cuda.synchronize()
    if not isinstance(got, torch.Tensor) or got.shape != x.shape or got.dtype != x.dtype or got.device != x.device:
        return {"passed": False, "error": "输出形状、类型或设备与输入不同"}
    if not torch.equal(x, before):
        return {"passed": False, "error": "候选修改了输入"}
    finite = bool(torch.isfinite(got).all().item())
    error = float((got.float() - expected.float()).abs().max().item())
    correct = finite and bool(torch.allclose(got, expected, **tolerance))
    return {"passed": correct, "max_abs_error": error, "finite": finite}


def median_timing(torch, functions, config):
    records = {name: {"gpu_us_samples": [], "wall_us_samples": []} for name in functions}
    names = list(functions)
    for function in functions.values():
        for _ in range(config["warmup"]):
            function()
    torch.cuda.synchronize()
    for sample in range(config["samples"]):
        # 轮换先后顺序，减少固定先测某一实现的偏差。
        order = names[sample % len(names):] + names[:sample % len(names)]
        for name in order:
            start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
            torch.cuda.synchronize()
            wall = time.perf_counter()
            start.record()
            for _ in range(config["calls_per_sample"]):
                functions[name]()
            end.record()
            end.synchronize()
            elapsed = 1e6 * (time.perf_counter() - wall) / config["calls_per_sample"]
            gpu_us = start.elapsed_time(end) * 1000 / config["calls_per_sample"]
            records[name]["gpu_us_samples"].append(gpu_us)
            records[name]["wall_us_samples"].append(elapsed)
    for record in records.values():
        record["gpu_us_median"] = statistics.median(record["gpu_us_samples"])
        record["wall_us_median"] = statistics.median(record["wall_us_samples"])
        if record["gpu_us_median"] <= 0 or not math.isfinite(record["gpu_us_median"]):
            raise RuntimeError("计时未获得有效正数，不能计算加速倍数")
    return records


def run(info):
    import torch
    sys.path.insert(0, str(Path.cwd()))
    from judge.reference import native_softmax, composed_softmax
    from judge.module import inputs, forward
    from candidate import softmax

    spec = json.loads(Path("judge/cases.json").read_text())
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    checks, benchmarks = [], []
    cold_started = time.perf_counter()
    with torch.inference_mode():
        for index, case in enumerate(spec["correctness"] + spec["benchmark"]):
            x = tensor(torch, case, spec["seed"] + index)
            check = validate(torch, x, native_softmax(x), softmax, spec["tolerance"][case["dtype"]])
            checks.append({**case, **check})
        cold_ms = 1000 * (time.perf_counter() - cold_started)
        if not all(check["passed"] for check in checks):
            return {"status": "numerical_failure", "score": 0, "gates": {"correct": False},
                    "feedback": "至少一个固定数值用例未通过，不计性能成绩。", "metrics": {"checks": checks}}, []
        for index, case in enumerate(spec["benchmark"]):
            x = tensor(torch, case, spec["seed"] + len(spec["correctness"]) + index)
            timings = median_timing(torch, {"composed": lambda: composed_softmax(x), "torch_native": lambda: native_softmax(x),
                                           "candidate": lambda: softmax(x)}, spec["timing"])
            speedup = timings["torch_native"]["gpu_us_median"] / timings["candidate"]["gpu_us_median"]
            benchmarks.append({**case, "timing": timings, "speedup_vs_torch_native": speedup})
        x, weight, values = inputs(spec["module"], spec["seed"])
        expected = forward(x, weight, values, native_softmax)
        actual = forward(x, weight, values, softmax)
        torch.cuda.synchronize()
        module_correct = bool(torch.allclose(expected, actual, atol=spec["module"]["atol"], rtol=spec["module"]["rtol"]))
        module_error = float((expected - actual).abs().max().item())
        if not module_correct:
            return {"status": "numerical_failure", "score": 0, "gates": {"module_correct": False},
                    "feedback": "小型推理模块替换后数值检查未通过。", "metrics": {"checks": checks,
                    "operator": benchmarks, "module_max_abs_error": module_error}}, benchmarks
        module_timings = median_timing(torch, {"torch_native": lambda: forward(x, weight, values, native_softmax),
                                              "candidate": lambda: forward(x, weight, values, softmax)}, spec["timing"])
    operator_speedup = math.exp(statistics.mean(math.log(row["speedup_vs_torch_native"]) for row in benchmarks))
    module_speedup = module_timings["torch_native"]["gpu_us_median"] / module_timings["candidate"]["gpu_us_median"]
    metrics = {"environment": info, "checks": checks, "operator": benchmarks, "operator_speedup": operator_speedup,
               "module": {"configuration": spec["module"], "max_abs_error": module_error,
                          "timing": module_timings, "speedup": module_speedup},
               "cold_validation_ms": cold_ms, "timing_configuration": spec["timing"], "tf32": False,
               "candidate_sha256": hashlib.sha256(Path("candidate.py").read_bytes()).hexdigest(),
               "cases_sha256": hashlib.sha256(Path("judge/cases.json").read_bytes()).hexdigest()}
    return {"status": "measured", "score": round(operator_speedup, 6),
            "gates": {"correct": True, "module_correct": True},
            "feedback": f"单算子相对 torch.softmax 几何平均 {operator_speedup:.3f} 倍；小型模块单独测得 {module_speedup:.3f} 倍。",
            "metrics": metrics}, benchmarks


def write_outputs(info, payload, out):
    out.mkdir(exist_ok=True)
    (out / "environment.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = ["# GPU Softmax 检查", "", payload["feedback"], "", f"状态：{payload['status']}", ""]
    metrics = payload.get("metrics", {})
    if payload["status"] == "measured":
        report += ["## 单算子稳态中位数", "", "| 形状/精度 | 组合实现 µs | torch 内置 µs | 候选 µs | 相对内置倍数 |",
                   "|---|---:|---:|---:|---:|"]
        for row in metrics["operator"]:
            timing = row["timing"]
            report.append(f"| {row['rows']}×{row['columns']} {row['dtype']} | {timing['composed']['gpu_us_median']:.3f} | "
                          f"{timing['torch_native']['gpu_us_median']:.3f} | {timing['candidate']['gpu_us_median']:.3f} | "
                          f"{row['speedup_vs_torch_native']:.3f} |")
        module = metrics["module"]
        report += ["", "## 随机初始化小模块", "", f"框架版 {module['timing']['torch_native']['gpu_us_median']:.3f} µs；"
                   f"候选替换版 {module['timing']['candidate']['gpu_us_median']:.3f} µs；模块倍数 {module['speedup']:.3f}。",
                   "", "模块使用合成输入和随机参数，不是语言生成任务，也没有测端到端服务。"
                   "全部重复样本、CPU同步墙钟时间、数值误差和冷启动检查耗时在 metrics.json。"]
    else:
        report += ["当前没有有效 GPU 性能结果；不展示模拟分数或加速倍数。"]
    (out / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true", help="只检查硬件与依赖，不编译或运行候选")
    args = parser.parse_args()
    info = probe()
    if info["status"] != "ready_not_measured" or args.probe:
        payload = {"status": info["status"], "score": None, "gates": {"environment": info["status"] == "ready_not_measured"},
                   "feedback": info["reason"] or "环境可用，尚未编译、校验或计时。", "metrics": {"environment": info}}
    else:
        try:
            payload, _ = run(info)
        except Exception as exc:
            payload = {"status": "execution_failed", "score": None, "gates": {"execution": False},
                       "feedback": f"GPU 执行失败，未获得成绩：{type(exc).__name__}: {exc}", "metrics": {"environment": info}}
    write_outputs(info, payload, Path("out"))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    # 没有实测结果时不写虚构分数；命令式评审会记录评审失败并停止基线启动。
    import os
    if payload["score"] is not None and os.environ.get("RSI_RESULT"):
        Path(os.environ["RSI_RESULT"]).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return 0 if payload["status"] in ("measured", "numerical_failure", "ready_not_measured") else 2


if __name__ == "__main__":
    sys.exit(main())
