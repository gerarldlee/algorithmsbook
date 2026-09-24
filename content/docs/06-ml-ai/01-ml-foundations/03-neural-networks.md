---
title: "Neural Network Mechanics: Forward/Backpropagation, Activation Functions, Loss Functions, and Optimizers (Adam, SGD)"
weight: 3
toc: true
---

## What it is
A neural network is a parameterized function composed of connected layers that transform inputs into outputs. A multilayer perceptron (MLP) uses affine transformations and nonlinear activation functions, while training adjusts the parameters to reduce a task loss.

## How it works
A feed-forward training run repeats three operations: forward propagation computes predictions, a loss function measures prediction error, and an optimizer updates parameters. Backpropagation applies the chain rule in the reverse direction to compute gradients. PyTorch autograd, TensorFlow GradientTape, and JAX transformations implement this differentiation; the optimizer then consumes the gradients.

```yaml
training_run:
  batch:
    size: 128
    shuffle: true
  forward_pass:
    input: "batch of feature vectors"
    hidden: ["linear", "ReLU"]
    output: ["linear", "softmax"]
  loss:
    name: "cross_entropy"
    class_count: 10
  backward_pass:
    algorithm: "chain rule through every layer"
    gradient: "loss gradient with respect to each parameter"
  optimizer:
    name: "Adam"
    learning_rate: 0.001
    regularization: ["weight_decay", "early_stopping"]
  evaluation:
    split: "validation"
    metric: "accuracy"
```

For a layer, forward propagation computes `h = sigma(Wx + b)`. **Activation functions** introduce nonlinearity: ReLU keeps positive inputs and maps negative inputs to zero, sigmoid maps values to `(0, 1)`, tanh maps values to `(-1, 1)`, and softmax turns a vector of scores into a probability distribution. Hidden layers commonly use ReLU or a related function; the output activation follows the target type.

**Backpropagation** first computes the loss gradient at the output and then repeatedly applies the derivative of each layer to the incoming gradient. The resulting gradient is paired with each parameter. **Stochastic gradient descent (SGD)** updates a parameter in the negative-gradient direction. **Adam** maintains running first- and second-moment estimates and scales updates using both, which often makes the first tuning attempt less sensitive than plain SGD. Training also uses minibatches, initialization, learning-rate schedules, and regularization such as weight decay, dropout, and early stopping.

The loss determines what the network optimizes. Mean squared error is common for regression, while cross-entropy compares predicted probabilities with class targets. A network can fit the training objective yet generalize poorly, so validation data must drive model selection and the test set must remain untouched until final evaluation.

## Complexity
Let `B` be the batch size, `P` be the number of model parameters, and `d_l` be the width of layer `l`. Stored model parameters occupy O(P) independently of the operation. For a dense MLP, the following bounds cover the main matrix operations; activation and loss costs depend on the layer widths and batch size.

| Operation | Representative time | Additional space |
| --- | --- | --- |
| Forward pass | O(B Σ_l d_l d_(l+1)) | O(B Σ_l d_l) for stored activations |
| Backward pass | O(B Σ_l d_l d_(l+1)) | O(B Σ_l d_l) plus parameter gradients |
| SGD update | O(P) | O(P) for parameter gradients, excluding the O(P) model parameters |
| Adam update | O(P) | O(P) for parameter gradients and O(P) for optimizer moment state, excluding the O(P) model parameters |
| Inference | O(Σ_l d_l d_(l+1)) per example | O(Σ_l d_l) for one example, excluding the model |

## When to use
- You have enough labeled examples for the model's capacity and can measure generalization on held-out data.
- The input contains useful structure that a model should learn rather than encode as hand-crafted features.
- You have accelerator memory and compute for minibatched matrix operations.
- The task benefits from learned representations, such as image, text, audio, or sensor modeling.
- You can tune the learning rate, initialization, regularization, and stopping criteria.

## Alternatives
- **Linear and logistic models** — train quickly and remain interpretable, but represent only the feature interactions supplied to them.
- **Decision trees and gradient-boosted trees** — are strong on many small-to-medium tabular datasets, but do not learn the same reusable dense representation.
- **Kernel methods and Gaussian processes** — provide strong nonlinear baselines and uncertainty in some settings, but scale poorly with large datasets.

## Related
- [Supervised Learning](01-supervised-learning.md)
- [Deep Learning Architectures](04-deep-learning-architectures.md)
- [Transformers](05-transformers.md)
- [Distributed Model Training: Data Parallelism, Tensor Parallelism, Pipeline Parallelism (DeepSpeed, Megatron-LM)](../03-genai/03-distributed-training.md)
