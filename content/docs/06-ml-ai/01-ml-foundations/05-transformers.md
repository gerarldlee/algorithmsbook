---
title: "Transformer Architecture: Self-Attention Mechanics, Scaled Dot-Product, Positional Encodings, Multi-Head Attention"
weight: 5
toc: true
---

## What it is
A Transformer is a neural-network architecture that uses self-attention to combine information from sequence positions without recurrence. Its blocks combine attention, feed-forward networks, residual paths, and normalization, producing encoder-only models such as BERT and decoder-only autoregressive models such as GPT.

## How it works
A Transformer processes tokens in parallel during training and uses position information to represent order. PyTorch and TensorFlow provide the core tensor and differentiation operations; Hugging Face builds higher-level model components on supported frameworks, with variations in masking, normalization placement, and parameter sharing.

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
  model_families:
    encoder_only: "BERT"
    decoder_only: "GPT"
    encoder_decoder: "T5"
```

Each token produces a query, key, and value through learned projections. For one head, scaled dot-product attention computes `softmax(QK^T / sqrt(d_k))V`. The scaling by `sqrt(d_k)` keeps dot products from growing too large as key dimension increases. Softmax turns each query's scores into weights, and the weighted sum of values produces a context vector. A causal mask replaces disallowed attention scores with a large negative value before softmax, preventing a decoder token from using future target tokens.

**Multi-head attention (MHA)** applies several projections in parallel. Each head can represent a different relationship or feature subspace; concatenating the head outputs and projecting them back gives the block a wider interaction space than one attention projection. Creating the query, key, and value projections and combining the head outputs costs O(n d²), in addition to attention scoring and value aggregation. The feed-forward network applies the same small network independently to each token, usually with a hidden expansion and nonlinear activation.

**Positional encoding** adds order information because self-attention alone does not distinguish token positions. Sinusoidal encodings use fixed functions of position; learned embeddings are trained with the model; relative encodings represent offsets directly. Transformer blocks then repeat attention, residual connections, normalization, and feed-forward transformations over layers. BERT uses bidirectional encoder representations and pretraining objectives, while GPT uses a causal decoder to predict the next token.

## Complexity
Let `n` be the sequence length, `c` the number of tokens already in the KV cache, `d` the model width, `d_ff` the feed-forward hidden width, `h` the number of attention heads, and `d_k` the dimension per head, with `d = h d_k`.

| Operation | Representative time | Additional space |
| --- | --- | --- |
| Scaled dot-product attention | O(n^2 d_k) | O(n^2) attention scores for one head |
| Multi-head attention | O(n d^2 + h n^2 d_k) | O(h n^2) if head scores are materialized |
| Position-wise feed-forward network | O(n d d_ff) | O(n d_ff) for intermediate activations |
| Transformer block | O(n^2 d + n d^2 + n d d_ff) | O(n^2 + n d_ff) for typical eager implementations |
| Attention step with a KV cache of `c` tokens | O(d^2 + c h d_k) = O(d^2 + c d), including query, key, value, and output projections | O(c h d_k) = O(c d) per layer for cached keys and values |

## When to use
- You need encoder representations for classification, extraction, retrieval, or understanding.
- You need a decoder for text generation, chat, code completion, or other next-token prediction.
- You can exploit parallel training across sequence positions and have accelerator capacity for attention memory.
- The sequence has dependencies that benefit from direct token-to-token interaction.
- You can define the model mask and evaluate errors on the target task rather than only next-token loss.

## Alternatives
- **RNNs and LSTMs** — maintain compact recurrent state and can stream sequentially, but train more slowly and often lose long-range information.
- **State-space models** — target efficient long sequence processing with different memory and complexity behavior, but have a smaller and more task-dependent ecosystem.
- **Sparse or approximate attention** — reduces memory and computation for long contexts, but can lose interactions or require more complex kernels.

## Related
- [Neural Networks](03-neural-networks.md)
- [Distributed Model Training: Data Parallelism, Tensor Parallelism, Pipeline Parallelism (DeepSpeed, Megatron-LM)](../03-genai/03-distributed-training.md)
- [Retrieval-Augmented Generation (RAG)](../03-genai/02-rag.md)
- [High-Throughput LLM Serving Frameworks: vLLM, PagedAttention, KV Caching, Continuous Batching, and Speculative Decoding](../03-genai/04-llm-serving.md)
