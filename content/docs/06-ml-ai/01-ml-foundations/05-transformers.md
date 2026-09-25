---
title: "Transformer Architecture: Self-Attention Mechanics, Scaled Dot-Product, Positional Encodings, Multi-Head Attention, and FlashAttention Mechanics"
weight: 5
toc: true
level: normal
---

## What it is
A Transformer is a neural-network architecture that uses self-attention to combine information from sequence positions without recurrence. Its blocks combine attention, feed-forward networks, residual paths, and normalization, producing encoder-only models such as BERT and decoder-only autoregressive models such as GPT.

## How it works
A Transformer processes tokens in parallel during training and uses position information to represent order. PyTorch and TensorFlow provide the core tensor and differentiation operations; Hugging Face builds higher-level model components on supported frameworks, with variations in masking, normalization placement, parameter sharing, and attention kernels.

```mermaid
flowchart LR
    I[Token and position representations] --> P[Query, key, and value projections]
    P --> S[Scale QK^T by 1/sqrt(d_k)]
    P --> V[Values]
    S --> M[Apply attention mask]
    M --> X[Softmax over allowed keys]
    X --> A[Weighted sum of values]
    V --> A
    A --> H[Concatenate heads and project]
    H --> F[Residual, normalization, and feed-forward network]
    F --> O[Contextual token representations]
```

```yaml
transformer:
  input:
    tokens: "integer token IDs"
    embedding: "token embedding plus positional encoding"
  encoder_block:
    - operation: "multi-head self-attention"
      inputs: "Q, K, V"
      output: "context vectors"
    - operation: "residual connection and layer normalization"
    - operation: "position-wise feed-forward network"
    - operation: "residual connection and layer normalization"
  decoder_block:
    attention: "causal self-attention followed by cross-attention when an encoder is present"
    mask: "position cannot attend to future target positions"
  positional_encoding:
    options: ["sinusoidal", "learned", "relative"]
  attention_kernel:
    name: "FlashAttention"
    semantics: "exact attention with tiled, IO-aware execution"
  model_families:
    encoder_only: "BERT"
    decoder_only: "GPT"
    encoder_decoder: "T5"
```

Each token produces a query, key, and value through learned projections. For one head, scaled dot-product attention computes `softmax(QK^T / sqrt(d_k))V`. The scaling by `sqrt(d_k)` limits score growth as key dimension increases. Softmax turns each query's scores into weights, and the weighted sum of values produces a context vector. Before softmax, a causal mask sets disallowed attention scores to negative infinity or adds a sufficiently negative mask value, preventing a decoder token from using future target tokens.

**Multi-head attention (MHA)** applies several projections in parallel. Each head can represent a different relationship or feature subspace; concatenating the head outputs and projecting them back gives the block a wider interaction space than one attention projection. Creating the query, key, and value projections and combining the head outputs costs O(n d²), in addition to attention scoring and value aggregation. The feed-forward network applies the same small network independently to each token, usually with a hidden expansion and nonlinear activation.

**Positional encoding** injects order information because self-attention alone does not distinguish token positions. Sinusoidal encodings use fixed functions of position and can be added to token embeddings; learned positional embeddings are trained with the model; relative encodings represent offsets directly or modify attention scores. Transformer blocks then repeat attention, residual connections, normalization, and feed-forward transformations over layers. BERT uses bidirectional encoder representations and pretraining objectives, while GPT uses a causal decoder to predict the next token.

**FlashAttention** is an IO-aware exact attention kernel, not a sparse approximation. It tiles queries, keys, and values, computes partial softmax normalization while visiting key-value blocks, and writes fewer intermediate results to high-bandwidth memory than an eager implementation that materializes the full score matrix. The algorithm changes data movement and working-memory use, not the full-attention arithmetic's asymptotic time complexity. The original algorithm targets training-time self-attention; inference kernels and causal variants require separate evaluation.

## Complexity
Let `n` be the sequence length, `c` the number of tokens already in the KV cache, `d` the model width, `d_ff` the feed-forward hidden width, `h` the number of attention heads, and `d_k` the dimension per head, with `d = h d_k`.

| Operation | Representative time | Additional space |
| --- | --- | --- |
| Scaled dot-product attention | O(n^2 d_k) | O(n^2) attention scores for one head |
| Multi-head attention | O(n d^2 + h n^2 d_k) = O(n d^2 + n^2 d) | O(h n^2) if head scores are materialized |
| FlashAttention self-attention | O(n^2 d) for the attention computation | O(n d + tile state) instead of an O(h n^2) materialized score matrix, excluding model parameters |
| Position-wise feed-forward network | O(n d d_ff) | O(n d_ff) for intermediate activations |
| Transformer block | O(n^2 d + n d^2 + n d d_ff) | O(n^2 + n d_ff) for typical eager implementations |
| Attention step with a KV cache of `c` tokens | O(d^2 + c h d_k) = O(d^2 + c d), including query, key, value, and output projections | O(c h d_k) = O(c d) per layer for cached keys and values |

## When to use
- You need encoder representations for classification, extraction, retrieval, or understanding.
- You need a decoder for text generation, chat, code completion, or other next-token prediction.
- You can exploit parallel training across sequence positions and have accelerator capacity for attention memory.
- The sequence has dependencies that benefit from direct token-to-token interaction.
- You need exact attention with lower memory traffic, so an IO-aware kernel such as FlashAttention is appropriate.
- You can define the model mask and evaluate errors on the target task rather than only next-token loss.

## Alternatives
- **RNNs, LSTMs, and GRUs** — maintain compact recurrent state and can stream sequentially, but usually cannot parallelize training across sequence positions and compress long-range information into a fixed-size state.
- **State-space models** — target efficient long sequence processing with different memory and complexity behavior, but have a smaller and more task-dependent ecosystem.
- **Sparse or approximate attention** — can reduce memory and computation for long contexts, but can change interactions and requires approximation-specific evaluation.

## Related
- [Neural Networks](03-neural-networks.md)
- [Deep Learning Architectures](04-deep-learning-architectures.md)
