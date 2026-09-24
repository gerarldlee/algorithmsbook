---
title: "Supervised Learning"
weight: 1
toc: true
---

## What it is
Supervised learning trains a model to map inputs to known outputs from a labeled dataset of `(feature, target)` pairs. The learner minimizes a loss between its predictions and the true labels, then generalizes to unseen examples.

## How it works
Given a dataset `D = {(x_i, y_i)}`, the model learns a function `f` by minimizing an objective such as mean squared error (regression) or cross-entropy (classification), typically via gradient descent. The data is split into train, validation, and test sets: the model fits on the train set, hyperparameters are tuned on the validation set, and final performance is reported on the untouched test set.

- **Linear regression** fits `y = w·x + b` by minimizing squared error; closed-form or gradient descent solution.
- **Logistic regression** applies a sigmoid to a linear combination, modeling `P(y=1|x)`, trained with binary cross-entropy.
- **Support Vector Machines (SVM)** find the maximum-margin hyperplane, optionally using kernels to handle non-linear boundaries.
- **Decision trees** recursively split features to maximize information gain / minimize impurity; **random forests** bag many trees to reduce variance.

The bias–variance tradeoff governs generalization: high-bias models (linear) underfit, high-variance models (deep trees) overfit; regularization and ensembling balance the two.

## Tradeoffs

| Method | Strengths | Weaknesses |
| --- | --- | --- |
| Linear regression | Fast, interpretable, closed form | Assumes linearity; sensitive to outliers |
| Logistic regression | Calibrated probabilities, cheap | Linear decision boundary unless engineered |
| SVM | Strong with kernels, max margin | O(n²)–O(n³) training; hard to interpret |
| Decision trees | Interpretable, non-linear | High variance, greedy overfitting |
| Random forest | Low variance, robust, feature importance | Less interpretable, slower than a single tree |

## When to use
- Predicting a continuous quantity (price, temperature) with linear regression.
- Binary/multi-class classification where calibrated probabilities matter (logistic regression).
- Small-to-medium tabular datasets where interpretability or robustness is required (trees, random forest).
- High-dimensional problems with clear margins (SVM with RBF kernel).

## Alternatives
- **Gradient-boosted trees (XGBoost/LightGBM)** — usually higher accuracy than random forests, but more hyperparameters to tune.
- **Neural networks** — scale to large data and non-linear patterns, but need far more data and compute and are opaque.

## Related
- [Unsupervised Learning](02-unsupervised-learning.md)
- [Neural Networks](03-neural-networks.md)
- [Deep Learning Architectures](04-deep-learning-architectures.md)
