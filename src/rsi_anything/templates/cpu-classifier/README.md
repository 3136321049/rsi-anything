# D04: CPU handwritten digit classification

[简体中文](README.zh-CN.md)

Train a classifier on the digits data that ship with scikit-learn: 1,797 grayscale 8×8 digit images, split by class proportion into a fixed 75% training set and 25% validation set, with the split seed fixed at `20261023`. The default three-level decision tree is a simple starting point that runs. You can try tree depth, other classifiers and preprocessing. All preprocessing is fitted only on the training set.

```bash
rsi init cpu-classifier my-classifier
cd my-classifier
python -m pip install -r requirements.txt
python judge/evaluate.py
rsi check
rsi run --agent codex --rounds 6
```

Install with the same Python that runs `rsi`. This package pins scikit-learn 1.6.1 and Matplotlib 3.9.4, needs Python 3.9+, and uses only the CPU. The data come with scikit-learn, so no training set is downloaded and no paid service is called. The first plot may need to build a font cache.

The AI may change only `training.json`. `model` can be `tree`, `knn`, `svm` or `random_forest`; `scaling` can be `none`, `standard` or `minmax`; `pca_components` is 0 (no PCA) or 2–64. Fill in `params` to match the model:

| Model | Tunable parameters |
|---|---|
| tree | `max_depth`: 1–40 or null; `min_samples_leaf`: 1–30; `criterion`: gini/entropy/log_loss |
| knn | `n_neighbors`: 1–50; `weights`: uniform/distance; `p`: 1/2 |
| svm | `C`: 0.001–1000; `gamma`: scale/auto or 0.000001–10; `kernel`: rbf/linear/poly/sigmoid |
| random_forest | `n_estimators`: 10–200; `max_depth` and `min_samples_leaf` as above; `max_features` as described in the scikit-learn docs |

The score is accuracy on the fixed validation set. A candidate whose training plus prediction takes more than 30 seconds isn't accepted; the outer evaluation timeout of 120 seconds is what stops the process. Timing depends on the machine and isn't part of the score. This validation set is used again and again for optimization, so **its results can't be called independent blind-test results**.

`out/report.md` summarizes the results. `confusion.png` shows the confusion matrix (the vertical axis is the actual class, the horizontal axis the predicted class). `mistakes.png` shows the first 12 mistakes, each labeled with its sample ID and "actual digit → predicted digit". `predictions.json` holds every sample ID and its prediction; `mistakes.json` holds all mistakes; `training.json` holds this round's configuration; `split.json` holds the split; `metrics.json` records the metrics, timing, versions, and the SHA256 of the data and the split. The images are labeled in English, and the written explanation is in the report. `outputs: [out]` in the configuration lets the engine save each round's outputs.

Replacing inputs: set `source` in `judge/data.json` to `csv` and put the data in `judge/dataset.csv`. The first row is a header. Each following row holds 64 finite numeric pixel features and a final `target` column (0–9). You need at least 100 rows and at least two samples per class. Pixels are laid out 8×8. Commit after changing the inputs or the split, then start a new experiment. Custom images should also keep a usable number of classes for the stratified split.

## Components used and sources

Official documentation was checked on 2026-10-23, and scikit-learn 1.6.1 / Matplotlib 3.9.4 were chosen. `judge/evaluate.py` calls data loading, the fixed split, Pipeline, the classifiers and plotting directly, without any other optimization engine.

- [scikit-learn digits data](https://scikit-learn.org/1.6/modules/generated/sklearn.datasets.load_digits.html), [official digit recognition example](https://scikit-learn.org/stable/auto_examples/classification/plot_digits_classification.html): make real training possible without external data.
- [train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html): fixed random seed and stratified sampling; training and validation don't overlap.
- [DecisionTreeClassifier](https://scikit-learn.org/1.6/modules/generated/sklearn.tree.DecisionTreeClassifier.html), [SVC](https://scikit-learn.org/1.6/modules/generated/sklearn.svm.SVC.html): CPU classifiers to compare.
- [KNeighborsClassifier](https://scikit-learn.org/1.6/modules/generated/sklearn.neighbors.KNeighborsClassifier.html), [RandomForestClassifier](https://scikit-learn.org/1.6/modules/generated/sklearn.ensemble.RandomForestClassifier.html): real training with neighbor-count and tree-ensemble parameters. [Pipeline](https://scikit-learn.org/1.6/modules/generated/sklearn.pipeline.Pipeline.html) ensures preprocessing is fitted only on training data.
- [Matplotlib subplots](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html): produce exportable confusion-matrix and mistake images, so there's a real artifact to look at.

Passing the baseline and evaluator tests isn't the same as accepting a multi-round demo. Real model runs should be saved separately under `examples/cpu-classifier/runs/`, keeping every round.
