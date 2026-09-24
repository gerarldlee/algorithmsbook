---
title: "Neural Networks"
weight: 3
toc: true
---

## What it is
A neural network is a stack of parameterized layers that apply linear transformations followed by non-linear activations, forming a universal function approximator. The perceptron is its single-neuron precursor; a multi-layer perceptron (MLP) adds hidden layers for non-linear capacity.

## How it works
Each layer computes `h = σ(Wx + b)` where `W`, `b` are learned weights/bias and `σ` is an activation function such as ReLU, sigmoid, tanh, or (for output) softmax. Training proceeds by **backpropagation**: the loss gradient is propagated from the output back through the network using the chain rule, and an optimizer (SGD, Adam, RMSProp) updates weights by a small step against the gradient.

Key components:
- **Activation** — introduces non-linearity; ReLU is the default for hidden layers.
- **Loss function** — MSE for regression, cross-entropy for classification.
- **Optimizer** — Adam adapts per-parameter learning rates, often the practical default over plain SGD.
- **Regularization** — weight decay, dropout, and early stopping control overfitting.

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Capacity | Universal approximator; overfits without regularization |
| Data hunger | Needs large labeled datasets to shine |
| Compute | GPU-friendly matrix ops, but expensive to train |
| Interpretability | Opaque "black box" compared to trees/linear models |
| Sensitivity | Non-convex loss; sensitive to init, learning rate, scale |

## When to use
- Large-scale problems (images, text, audio) where hand-crafted features fall short.
- Tasks requiring learned, hierarchical feature representations.
- When accuracy outweighs interpretability and training data is plentiful.

## Alternatives
- **Classical ML (trees, SVMs)** — better on small tabular data with fewer compute needs.
- **Kernel methods / Gaussian processes** — principled uncertainty estimates, but scale poorly to large `n`.

## Related
- [Supervised Learning](01-supervised-learning.md)
- [Unsupervised Learning](02-unsupervised-learning.md)
- [Deep Learning Architectures](04-deep-learning-architectures.md)
- [Transformers](05-transformers.md)
