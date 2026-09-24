---
title: "Deep Learning Architectures"
weight: 4
toc: true
---

## What it is
Deep learning architectures are specialized neural network topologies designed to exploit structure in specific data modalities — spatial locality in images, temporal order in sequences, and generative modeling of distributions.

## How it works
- **Convolutional Neural Networks (CNNs)** apply learned convolutional filters that slide over inputs, sharing weights to capture local spatial patterns; pooling layers downsample and expand receptive fields.
- **Recurrent Neural Networks (RNNs)** process sequences step by step, passing a hidden state forward; **LSTM** and **GRU** add gating mechanisms to combat vanishing/exploding gradients and retain long-range memory.
- **Residual networks (ResNets)** add skip connections (`y = F(x) + x`) so layers learn residuals, enabling much deeper networks without degradation.
- **Generative Adversarial Networks (GANs)** pit a generator against a discriminator in a minimax game, producing realistic synthetic samples.
- **Encoder–decoder** models compress an input into a latent vector (encoder) and reconstruct or translate it (decoder), the foundation of seq2seq and autoencoders.

## Tradeoffs

| Architecture | Strengths | Weaknesses |
| --- | --- | --- |
| CNN | Parameter sharing, translation invariance | Fixed receptive fields; not sequence-native |
| RNN | Sequential modeling | Vanishing gradients, slow unrolled training |
| LSTM/GRU | Long-range memory | Still sequential; complex gating, compute-heavy |
| ResNet | Very deep training, strong accuracy | More parameters/layers |
| GAN | High-fidelity generation | Training instability, mode collapse |
| Encoder–decoder | Flexible seq2seq | Latent bottleneck limits long inputs |

## When to use
- Images and spatial data — CNNs (or ResNets for very deep models).
- Time series, speech, and sequential text — RNN/LSTM/GRU.
- Image synthesis and data augmentation — GANs.
- Machine translation and summarization — encoder–decoder models.

## Alternatives
- **Transformers** — parallel attention over full sequences, but quadratic memory vs. recurrent models.
- **Diffusion models** — more stable generation than GANs, but slower sampling.

## Related
- [Neural Networks](03-neural-networks.md)
- [Transformers](05-transformers.md)
- [Supervised Learning](01-supervised-learning.md)
