---
title: "Supervised Learning: Linear/Logistic Regression, Decision Trees, Random Forests, Gradient Boosting (XGBoost)"
weight: 1
toc: true
---

## What it is
Supervised learning is the branch of machine learning that learns a mapping from inputs to known targets using labeled examples. The model optimizes a loss against the targets during training, then applies the learned mapping to examples whose targets are not known.

## How it works
A supervised training run separates data selection, fitting, evaluation, and selection. The data split prevents information from the test set from influencing training or tuning. Scikit-learn supplies regression, classification, decision-tree, and random-forest estimators; XGBoost supplies gradient-boosted trees. Their interfaces and optimization controls differ, but both support the same validation workflow.

```yaml
experiment:
  task: "binary classification"
  data:
    features: ["age", "region", "purchase_count"]
    target: "churned"
    split: {train: 0.70, validation: 0.15, test: 0.15}
    leakage_control: "fit preprocessing on the training split only"
  models:
    linear_regression:
      loss: "mean squared error"
      use_for: "continuous targets"
    logistic_regression:
      loss: "binary or multinomial cross-entropy"
      use_for: "binary or multiclass targets"
    decision_tree:
      split_criterion: "impurity reduction"
      pruning: ["cost complexity", "minimum leaf size"]
    random_forest:
      trees: "many decorrelated bootstrap trees"
      voting: "majority vote or mean probability"
    xgboost:
      boosting: "gradient boosted decision trees"
      objective: "logistic classification"
  evaluation:
    metrics: ["accuracy", "precision", "recall", "ROC AUC"]
    selection: "validation score"
    final_report: "test score"
```

The model family determines the hypothesis and loss. **Linear regression** predicts a continuous target with `y = wx + b` and minimizes squared error; **logistic regression** applies a sigmoid to a linear score and minimizes cross-entropy. **Decision trees** choose splits that reduce impurity, such as Gini impurity or variance. A **random forest** fits trees on bootstrap samples and random feature subsets, then averages or votes their predictions to reduce variance.

**Gradient boosting** fits trees sequentially. At round `m`, a new tree learns the residual or gradient signal from the current ensemble, so later trees correct earlier mistakes. XGBoost adds regularization, second-order gradient statistics, and efficient tree construction. Validation performance selects the number of rounds and other hyperparameters, while the test set is used only for the final estimate. Missing values, scaling, and categorical encodings must be fitted or defined without using test data.

## Complexity
Let `m` be the number of training examples, `d` the number of features, `h` the maximum tree depth, `L` the boosting-tree depth, `T` the number of forest trees, and `b` the number of histogram bins per feature. These are conservative bounds for depth-limited trees that sort feature values at split nodes; implementations that presort or approximate splits can differ.

| Operation | Representative time | Additional space |
| --- | --- | --- |
| Linear or logistic regression pass | O(md) | O(d) working space, excluding stored parameters |
| One decision-tree fit | O(mdh log m) with per-node sorting | O(m) for the model and O(m + h) working space |
| Random-forest fit | O(Tmdh log m) with per-node sorting | O(Tm) for the models and O(m + h) per-tree working space |
| XGBoost round | O(mdL) for a histogram-based implementation | O(d·b) per active histogram node, plus tree and metadata state |
| Prediction | O(d) for linear models; O(h) per tree, or O(Th) for a forest | O(1) working space beyond the model |

## When to use
- You have labeled examples and need a model that maps the same measured features to a known target.
- The target is continuous, so linear regression provides a transparent first baseline.
- The target is categorical and calibrated probabilities matter, so logistic regression or a tree ensemble is appropriate.
- The data is small or medium-sized, tabular, and interpretability or robust baseline performance matters.
- The decision is high impact, so you can reserve a test set and compare models on a task-specific metric.

## Alternatives
- **Support vector machines** — win on small, clean datasets with a useful kernel, but training cost grows with the sample count and regularization is sensitive.
- **Neural networks** — learn richer interactions and representations at scale, but need more data, compute, tuning, and interpretability work.
- **Nearest neighbors** — are simple baselines for local or nonparametric structure, but become expensive at prediction time as the dataset grows.

## Related
- [Unsupervised Learning](02-unsupervised-learning.md)
- [Neural Networks](03-neural-networks.md)
- [ML System Design](../02-mlops/01-ml-system-design.md)
- [Feature Stores and Pipelines](../02-mlops/02-feature-stores-pipelines.md)
