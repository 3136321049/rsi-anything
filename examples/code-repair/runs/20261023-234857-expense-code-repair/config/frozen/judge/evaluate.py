"""执行固定测试，输出通过率、逐项失败与示例结果。"""
import importlib.util
import io
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.dont_write_bytecode = True


class Results(unittest.TextTestResult):
    def __init__(self, *args):
        super().__init__(*args)
        self.passed_names = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed_names.append(test.id())


def main():
    out = Path("out")
    out.mkdir(exist_ok=True)
    details, example = {}, {}
    try:
        spec = importlib.util.spec_from_file_location("fixed_expense_tests", "judge/test_expense.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        expected = suite.countTestCases()
        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=Results).run(suite)
        failures = [{"test": test.id(), "detail": error} for test, error in result.failures + result.errors]
        details = {"total": expected, "passed": len(result.passed_names), "failed": failures,
                   "skipped": len(result.skipped), "passed_tests": result.passed_names}
        score = round(100 * details["passed"] / expected, 2) if expected else 0
        gates = {"tests_executed": expected > 0 and result.testsRun == expected, "no_skips": not result.skipped}
        feedback = f"固定测试通过 {details['passed']}/{expected}。"
        feedback += "\n" + "\n".join(f"{f['test']}: {f['detail'].strip().splitlines()[-1]}" for f in failures)
        try:
            from example import build_example
            example = build_example()
        except Exception as exc:
            example = {"error": str(exc)}
    except Exception as exc:
        score, gates, feedback = 0, {"tests_executed": False}, f"业务模块无法运行：{type(exc).__name__}: {exc}"
        details = {"total": 0, "passed": 0, "failed": [], "error": feedback}
    payload = {"score": score, "gates": gates, "feedback": feedback,
               "metrics": {"tests_passed": details["passed"], "tests_total": details["total"],
                           "all_tests_passed": bool(details["total"]) and score == 100}}
    (out / "tests.json").write_text(json.dumps(details, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "example.json").write_text(json.dumps(example, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "report.md").write_text("# 记账项目检查\n\n" + feedback + "\n\n## 当前示例\n\n```json\n"
                                   + json.dumps(example, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.environ.get("RSI_RESULT"):
        Path(os.environ["RSI_RESULT"]).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
