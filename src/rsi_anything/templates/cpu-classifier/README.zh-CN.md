# D04：CPU 手写数字分类

[English](README.md)

用 scikit-learn 自带的 digits 数据训练分类器。1797 张 8×8 灰度数字图，按类别比例固定划分 75% 训练、25% 验证，划分种子固定为 `20261023`。默认三层决策树是可运行的简单起点；可尝试树深度、分类器和预处理。所有预处理只在训练集拟合。

```bash
rsi init cpu-classifier my-classifier
cd my-classifier
python -m pip install -r requirements.txt
python judge/evaluate.py
rsi check
rsi run --agent codex --rounds 6
```

安装必须使用运行 `rsi` 的同一个 Python。本包固定 scikit-learn 1.6.1、Matplotlib 3.9.4，需要 Python 3.9+，仅用 CPU；数据随 scikit-learn 提供，不下载训练集，不调用付费服务。首次绘图可能需要生成字体缓存。

AI 只能改 `training.json`。`model` 可为 `tree`、`knn`、`svm`、`random_forest`；`scaling` 可为 `none`、`standard`、`minmax`；`pca_components` 为 0（不用 PCA）或 2–64。`params` 随模型填写：

| 模型 | 可调参数 |
|---|---|
| tree | `max_depth`：1–40 或 null；`min_samples_leaf`：1–30；`criterion`：gini/entropy/log_loss |
| knn | `n_neighbors`：1–50；`weights`：uniform/distance；`p`：1/2 |
| svm | `C`：0.001–1000；`gamma`：scale/auto 或 0.000001–10；`kernel`：rbf/linear/poly/sigmoid |
| random_forest | `n_estimators`：10–200；`max_depth`、`min_samples_leaf` 同上；`max_features` 按 scikit-learn 文档填写 |

得分为固定验证集正确率，训练加预测超过 30 秒不接受；外层评审超时 120 秒负责停止进程。耗时受机器影响，不作为分数。这个验证集会被反复用于优化，**不能称为独立盲测结果**。

`out/report.md` 汇总结果；`confusion.png` 展示混淆矩阵（纵轴为实际类别，横轴为预测类别）；`mistakes.png` 展示前 12 个错例，每张注明样本编号与“实际数字 → 预测数字”；`predictions.json` 保存全部样本编号与预测；`mistakes.json` 保存全部错例；`training.json` 保存本轮配置；`split.json` 保存划分；`metrics.json` 记录指标、耗时、版本、数据与划分 SHA256。图片标注为英文，文字说明在报告中。配置中的 `outputs: [out]` 供引擎保存逐轮产物。

替换输入：把 `judge/data.json` 的 `source` 改为 `csv`，将数据放在 `judge/dataset.csv`。首行表头，随后每行 64 个有限数值像素特征和最后一列 `target`（0–9），至少 100 行，每类至少两个样本。像素按 8×8 排列；修改输入或划分后提交，再开新实验。自定义图像也应保留可用的类别数量供分层划分。

## 实际组件与来源

2026-10-23 查阅官方资料，选用 scikit-learn 1.6.1 / Matplotlib 3.9.4。`judge/evaluate.py` 直接调用数据读取、固定划分、Pipeline、分类器和绘图，没有接入其他优化引擎。

- [scikit-learn digits 数据](https://scikit-learn.org/1.6/modules/generated/sklearn.datasets.load_digits.html)、[官方数字识别示例](https://scikit-learn.org/stable/auto_examples/classification/plot_digits_classification.html)：解决无需外部数据即可实际训练的问题。
- [train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)：固定随机种子和分层抽样；训练与验证不重叠。
- [DecisionTreeClassifier](https://scikit-learn.org/1.6/modules/generated/sklearn.tree.DecisionTreeClassifier.html)、[SVC](https://scikit-learn.org/1.6/modules/generated/sklearn.svm.SVC.html)：提供可比较的 CPU 分类器。
- [KNeighborsClassifier](https://scikit-learn.org/1.6/modules/generated/sklearn.neighbors.KNeighborsClassifier.html)、[RandomForestClassifier](https://scikit-learn.org/1.6/modules/generated/sklearn.ensemble.RandomForestClassifier.html)：支持邻居数量与树集成参数的实际训练；[Pipeline](https://scikit-learn.org/1.6/modules/generated/sklearn.pipeline.Pipeline.html) 保证预处理只在训练数据上拟合。
- [Matplotlib subplots](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html)：生成可导出的混淆矩阵与错例图，增加真实作品展示。

基线与验收器测试通过不等于多轮 Demo 验收。真实模型运行应另存 `examples/cpu-classifier/runs/`，保留全部轮次。
