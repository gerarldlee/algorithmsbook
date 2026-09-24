---
title: "Transformers"
weight: 5
toc: true
---

## What it is
The Transformer is an attention-based sequence model that replaces recurrence with parallel self-attention, enabling long-range dependencies and highly scalable training. It underlies modern LLMs via the encoder-only BERT family and decoder-only GPT family.

## How it works
Inputs are tokenized and summed with **positional encodings** so order information is retained without recurrence. Each layer applies multi-head **self-attention**: queries `Q`, keys `K`, and values `V` are projected from the input, and attention scores are computed as `softmax(QKᵀ / √d_k)V`, letting every token attend to every other token. **Multi-head** attention runs several such projections in parallel to capture different relationships, followed by feed-forward layers, residual connections, and layer normalization.

- **BERT** is encoder-only and bidirectional, pretrained with masked-language modeling and next-sentence prediction, then fine-tuned for understanding tasks.
- **GPT** is decoder-only and autoregressive, trained with causal masking to predict the next token, and scaled for generation.

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Long-range context | O(n²) attention in sequence length; memory/GPU heavy |
| Parallelism | Trains far faster than RNNs on GPUs |
| Data scale | Excels with massive corpora; overfits small data |
| Interpretability | Attention maps are partial clues, not full explanations |
| Inference | Autoregressive decoding is sequential and compute-intensive |

## When to use
- Natural language understanding and classification (fine-tuned BERT).
- Text generation, chat, and code completion (GPT-style decoders).
- Tasks requiring long-range dependencies and parallelizable training at scale.

## Alternatives
- **RNN/LSTM** — constant memory per step for long sequences, but slow and weaker long-range memory.
- **State-space models (Mamba)** — linear-time sequence modeling, but newer and less proven across tasks.

## Related
- [Neural Networks](03-neural-networks.md)
- [Deep Learning Architectures](04-deep-learning-architectures.md)
- [Supervised Learning](01-supervised-learning.md)
