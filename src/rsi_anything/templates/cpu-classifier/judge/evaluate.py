"""固定数据划分，拟合预处理与分类器，保存逐样本结果和可读图。"""
import hashlib
import json
import os
import platform
import time
from pathlib import Path

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"


def integer(value, low, high, name):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"{name} 应为 {low}..{high} 的整数")
    return value


def build_pipeline(config, seed):
    from sklearn.decomposition import PCA
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import MinMaxScaler, StandardScaler
    from sklearn.svm import SVC
    from sklearn.tree import DecisionTreeClassifier

    params = config.get("params", {})
    if not isinstance(params, dict):
        raise ValueError("params 应为对象")
    model = config.get("model", "tree")
    allowed = {"tree": {"max_depth", "min_samples_leaf", "criterion"},
               "knn": {"n_neighbors", "weights", "p"}, "svm": {"C", "gamma", "kernel"},
               "random_forest": {"n_estimators", "max_depth", "min_samples_leaf", "max_features"}}
    if model not in allowed or set(params) - allowed[model]:
        raise ValueError("未知分类器或参数，请按 README.md 配置")
    for key, low, high in (("max_depth", 1, 40), ("min_samples_leaf", 1, 30),
                           ("n_neighbors", 1, 50), ("n_estimators", 10, 200), ("p", 1, 2)):
        if key in params and not (key == "max_depth" and params[key] is None):
            integer(params[key], low, high, key)
    if "C" in params and (isinstance(params["C"], bool) or not isinstance(params["C"], (int, float))
                           or not 0.001 <= params["C"] <= 1000):
        raise ValueError("C 应在 0.001..1000 之间")
    if "gamma" in params and params["gamma"] not in ("scale", "auto"):
        gamma = params["gamma"]
        if isinstance(gamma, bool) or not isinstance(gamma, (int, float)) or not 1e-6 <= gamma <= 10:
            raise ValueError("gamma 应为 scale、auto 或 1e-6..10 的数值")
    constructors = {
        "tree": lambda: DecisionTreeClassifier(random_state=seed, **params),
        "knn": lambda: KNeighborsClassifier(n_jobs=1, **params),
        "svm": lambda: SVC(cache_size=128, **params),
        "random_forest": lambda: RandomForestClassifier(random_state=seed, n_jobs=1, **params),
    }
    steps = []
    scaling = config.get("scaling", "none")
    if scaling == "standard":
        steps.append(("scale", StandardScaler()))
    elif scaling == "minmax":
        steps.append(("scale", MinMaxScaler()))
    elif scaling != "none":
        raise ValueError("scaling 应为 none、standard 或 minmax")
    components = integer(config.get("pca_components", 0), 0, 64, "pca_components")
    if components == 1:
        raise ValueError("pca_components 应为 0 或 2..64")
    if components:
        steps.append(("pca", PCA(n_components=components, svd_solver="full", random_state=seed)))
    return Pipeline(steps + [("classifier", constructors[model]())])


def run(out):
    import numpy as np
    import sklearn
    from sklearn.datasets import load_digits
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    from sklearn.model_selection import train_test_split

    config = json.loads(Path("training.json").read_text(encoding="utf-8"))
    data_config = json.loads(Path("judge/data.json").read_text(encoding="utf-8"))
    if data_config["source"] == "digits":
        dataset = load_digits()
        x, y = dataset.data, dataset.target
    elif data_config["source"] == "csv":
        matrix = np.loadtxt(data_config["csv"], delimiter=",", skiprows=1)
        if matrix.ndim != 2 or matrix.shape[1] != 65 or len(matrix) < 100:
            raise ValueError("自定义 CSV 需要至少 100 行，每行 64 个像素特征和一个 target")
        x, y = matrix[:, :64], matrix[:, 64]
        if not np.isfinite(matrix).all() or not np.isin(y, np.arange(10)).all():
            raise ValueError("数据必须有限，target 必须为 0..9 的整数")
        y = y.astype(int)
    else:
        raise ValueError("source 应为 digits 或 csv")
    ids = np.arange(len(y))
    train_ids, valid_ids = train_test_split(ids, test_size=data_config["validation_fraction"],
                                           stratify=y, random_state=data_config["split_seed"])
    estimator = build_pipeline(config, data_config["training_seed"])
    started = time.perf_counter()
    estimator.fit(x[train_ids], y[train_ids])
    train_seconds = time.perf_counter() - started
    predicted = estimator.predict(x[valid_ids])
    seconds = time.perf_counter() - started
    score = float(100 * accuracy_score(y[valid_ids], predicted))
    matrix = confusion_matrix(y[valid_ids], predicted, labels=list(range(10)))
    predictions = [{"sample_id": int(i), "expected": int(y[i]), "predicted": int(got),
                    "correct": bool(y[i] == got)} for i, got in zip(valid_ids, predicted)]
    mistakes = [row for row in predictions if not row["correct"]]
    metrics = {"accuracy_percent": round(score, 3), "train_count": len(train_ids), "validation_count": len(valid_ids),
               "train_seconds": round(train_seconds, 4), "train_predict_seconds": round(seconds, 4),
               "mistakes": len(mistakes), "split_seed": data_config["split_seed"],
               "data_sha256": hashlib.sha256(x.tobytes() + y.tobytes()).hexdigest(),
               "split_sha256": hashlib.sha256(train_ids.tobytes() + valid_ids.tobytes()).hexdigest(),
               "python": platform.python_version(), "scikit_learn": sklearn.__version__, "numpy": np.__version__,
               "configuration": config, "confusion_matrix": matrix.tolist(),
               "classification": classification_report(y[valid_ids], predicted, output_dict=True, zero_division=0)}
    for name, content in (("predictions.json", predictions), ("mistakes.json", mistakes),
                          ("training.json", config), ("split.json", {"train": train_ids.tolist(), "validation": valid_ids.tolist()})):
        (out / name).write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plot(out, x, matrix, mistakes, score)
    weakness = sorted((row["recall"], label) for label, row in metrics["classification"].items() if label.isdigit())[:3]
    feedback = f"验证集正确率 {score:.2f}%，错分 {len(mistakes)}/{len(valid_ids)}；训练和预测 {seconds:.3f} 秒。"
    feedback += "召回率较低的数字：" + "、".join(f"{label}={recall:.1%}" for recall, label in weakness)
    text = ("# CPU 手写数字分类\n\n" + feedback + "\n\n"
            "这是优化过程中反复使用的固定验证集，结果不代表独立新数据上的泛化效果。\n\n"
            "![混淆矩阵](confusion.png)\n\n![错分图片](mistakes.png)\n\n"
            "## 当前配置\n\n```json\n" + json.dumps(config, ensure_ascii=False, indent=2) + "\n```\n")
    (out / "report.md").write_text(text, encoding="utf-8")
    return {"score": round(score, 3), "gates": {"finite_predictions": bool(np.isfinite(predicted).all()),
            "time_budget": seconds <= data_config["maximum_seconds"]}, "feedback": feedback, "metrics": metrics}


def plot(out, x, matrix, mistakes, score):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    available = {font.name for font in font_manager.fontManager.ttflist}
    chinese_font = next((name for name in ("PingFang SC", "Arial Unicode MS", "Noto Sans CJK SC",
                                          "Microsoft YaHei", "WenQuanYi Micro Hei") if name in available), None)
    if chinese_font:
        plt.rcParams["font.sans-serif"] = [chinese_font]

    fig, axis = plt.subplots(figsize=(6, 5))
    image = axis.imshow(matrix, cmap="Blues")
    for row in range(10):
        for col in range(10):
            axis.text(col, row, str(matrix[row, col]), ha="center", va="center", fontsize=8,
                      color="white" if matrix[row, col] > matrix.max() / 2 else "black")
    axis.set(xticks=range(10), yticks=range(10), xlabel="预测数字" if chinese_font else "",
             ylabel="实际数字" if chinese_font else "", title=f"正确率 {score:.2f}%" if chinese_font else f"{score:.2f}%")
    fig.colorbar(image, ax=axis)
    fig.tight_layout()
    fig.savefig(out / "confusion.png", dpi=140)
    plt.close(fig)
    fig, axes = plt.subplots(3, 4, figsize=(8, 6))
    for axis, mistake in zip(axes.flat, mistakes[:12]):
        axis.imshow(x[mistake["sample_id"]].reshape(8, 8), cmap="gray_r", interpolation="nearest")
        axis.set_title(f"#{mistake['sample_id']}  {mistake['expected']} → {mistake['predicted']}", fontsize=9)
    for axis in axes.flat:
        axis.axis("off")
    if chinese_font:
        fig.suptitle("前 12 个错例：实际数字 → 预测数字" if mistakes else "本验证集没有错例")
    fig.tight_layout()
    fig.savefig(out / "mistakes.png", dpi=140)
    plt.close(fig)


def main():
    out = Path("out")
    out.mkdir(exist_ok=True)
    for name in ("metrics.json", "report.md", "predictions.json", "mistakes.json", "training.json",
                 "split.json", "confusion.png", "mistakes.png"):
        path = out / name
        if path.is_file():
            path.unlink()
    try:
        payload = run(out)
    except ImportError as exc:
        payload = {"score": 0, "gates": {"dependencies": False},
                   "feedback": f"缺少依赖：{exc}。请用运行 rsi 的 Python 安装 requirements.txt。"}
    except Exception as exc:
        payload = {"score": 0, "gates": {"training_completed": False},
                   "feedback": f"训练失败：{type(exc).__name__}: {exc}"}
    (out / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not all(payload["gates"].values()):
        (out / "report.md").write_text("# CPU 分类检查\n\n" + payload["feedback"] + "\n", encoding="utf-8")
    if os.environ.get("RSI_RESULT"):
        Path(os.environ["RSI_RESULT"]).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
