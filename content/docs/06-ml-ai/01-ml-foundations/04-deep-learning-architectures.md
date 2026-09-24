---
title: "Deep Learning Architectures: Convolutional Neural Networks (CNNs), Recurrent Neural Networks (RNNs)"
weight: 4
toc: true
---

## What it is
Deep learning architectures are neural-network topologies arranged to exploit structure in a data modality. Convolutional neural networks encode local spatial structure, while recurrent neural networks encode state across an ordered sequence.

## How it works
An architecture determines which inductive bias the model carries into training. A CNN shares filters across positions so the same feature detector can fire wherever it matches; an RNN carries a state from one sequence position to the next. PyTorch and TensorFlow provide tensor, differentiation, and module primitives for both families; Keras is a higher-level API that can run on a supported backend.

```yaml
architecture:
  cnn:
    input_shape: [height, width, channels]
    stages:
      - operation: "convolution"
        purpose: "learn local spatial filters"
      - operation: "activation"
        purpose: "introduce nonlinearity"
      - operation: "pooling_or_strided_convolution"
        purpose: "reduce spatial resolution and enlarge effective receptive field"
    head:
      operation: "global pooling or dense layer"
      output: "class probabilities or regression values"
  rnn:
    input_shape: [time, features]
    recurrence: "hidden state updated at each time step"
    variants: ["vanilla RNN", "LSTM", "GRU"]
    output: "sequence state, final state, or one value per time step"
  training:
    objective: "task-specific loss"
    backpropagation: ["through time for RNN", "through layers for CNN"]
```

A **convolutional neural network (CNN)** applies a filter across a local receptive field. Weight sharing makes a filter independent of its absolute position, and stacking layers builds higher-level features from lower-level edges and textures. Pooling or strided convolutions reduce spatial dimensions; the final head aggregates spatial information for classification or regression. Architectures such as ResNet add residual connections so a block learns a residual function around an identity path.

A **recurrent neural network (RNN)** processes `x_t` at time `t` and updates a hidden state `h_t` using the current input and previous state. During training, backpropagation through time (BPTT) applies gradients across the unrolled sequence. **Long short-term memory (LSTM)** and **gated recurrent unit (GRU)** networks add gates that regulate what information is stored, updated, and exposed, which helps gradients travel farther through long sequences. Encoder-decoder models combine an encoder with a decoder when an output sequence depends on an input sequence.

## Complexity
Let `H_in` and `W_in` be input height and width, `H_out` and `W_out` be output height and width, `C_in` and `C_out` be input and output channels, `K` be the kernel side, `B` the batch size, `T` the sequence length, `d` the input width, and `h` the recurrent hidden width. The RNN bounds treat the fixed gate overhead of LSTM and GRU cells as a constant.

| Operation | Representative time | Additional space |
| --- | --- | --- |
| Dense convolution | O(B H_out W_out C_in C_out K²) | O(B H_out W_out C_out) for one output activation map |
| Average pooling | O(B H_out W_out C_in K²) for a `K × K` window | O(B H_out W_out C_in) for its output map |
| Strided convolution | O(B H_out W_out C_in C_out K²) | O(B H_out W_out C_out) for its output map |
| LSTM or GRU step | O(B(dh + h²)) | O(Bh) for the current state |
| RNN sequence training | O(TB(dh + h²)) | O(TBh) when unrolling the full sequence |
| RNN incremental inference | O(B(dh + h²)) per step | O(Bh) for the recurrent state; O(BTh) if all outputs are retained |

## When to use
- You need spatial locality, shared filters, and strong image or grid-structured predictions.
- You need to model ordered observations with state carried from one time step to the next.
- The sequence length is moderate and incremental stateful inference is valuable.
- You can train with enough data and compute to learn many filters or recurrent parameters.
- You need a task-specific loss and held-out evaluation rather than judging the representation only by training loss.

## Alternatives
- **Transformers** — provide parallel all-token interaction and strong long-range context, but standard self-attention uses quadratic sequence memory.
- **State-space models** — offer recurrent-style streaming with different sequence complexity, but their quality and tooling vary by task and implementation.
- **Convolutional or fully connected models** — are simpler and cheaper for data with strong locality or low-dimensional structure, but do not model long sequences as naturally.

## Related
- [Neural Networks](03-neural-networks.md)
- [Model Optimization](../02-mlops/03-model-optimization.md)
- [Distributed Training](../03-genai/03-distributed-training.md)
