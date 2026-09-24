---
title: "LLM Serving"
weight: 4
toc: true
---

## What it is
LLM serving is the engineering of running a large language model behind an API, turning autoregressive token generation into a high-throughput, low-latency, cost-efficient online service. Because generation is sequential and memory-bound (dominated by attention and the **KV cache**), serving requires specialized batching and scheduling rather than plain request-per-thread execution.

## How it works

- **KV cache:** attention keys/values for already-generated tokens are cached so each new token only computes attention against the growing context, avoiding full recomputation. The cache grows with sequence length and is a major memory cost.
- **Batching:** requests are grouped to raise GPU utilization. **Continuous batching** (in-flight/orca-style) admits and evicts requests token-by-token instead of fixed-size batches, so finished sequences don't stall the batch.
- **Speculative decoding:** a small draft model proposes several tokens, which the large model verifies in parallel, accepting them if correct — trading extra compute for fewer sequential steps and lower latency.
- **Quantization:** weights are stored at reduced precision (INT8/INT4, GPTQ/AWQ) to shrink memory and speed up matrix multiplies, with a small quality cost.

```yaml
# LLM serving (architecture description)
request_lifecycle:
  - tokenize: convert prompt text to token IDs
  - schedule: continuous batching admits requests into the running batch
  - prefill: compute KV cache for the prompt (compute-bound)
  - decode: generate tokens autoregressively, one per step (memory-bound)
  - stream: emit tokens as they are produced

optimizations:
  - kv_cache: cache keys/values; use PagedAttention/vLLM to virtualize it
  - continuous_batching: add/remove requests per token step
  - speculative_decoding: draft model proposes, big model verifies
  - quantization: INT8/INT4 weights to cut memory and bandwidth

metrics:
  - TTFT: time to first token (prefill latency)
  - TPOT: time per output token (decode latency)
  - throughput: tokens per second across the batch
```

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Latency vs. throughput | Larger batches raise throughput but increase per-token latency |
| KV cache memory | Long contexts consume large GPU memory; paging mitigates but adds complexity |
| Quantization | Lower precision speeds inference but risks quality degradation |
| Speculative decoding | Reduces latency but needs a compatible draft model and extra compute |
| Scheduling fairness | Continuous batching must balance TTFT, throughput, and starvation |

## When to use
- Serving a chat/completion API to many concurrent users with a latency SLO.
- Long-context workloads where KV-cache memory must be managed carefully.
- Cost-sensitive deployments where quantization and high GPU utilization matter.

## Alternatives
- **Naive batching** — fixed-size batches, simpler but wastes capacity waiting on slow sequences.
- **Model sharding (tensor parallel)** — spreads one model over many GPUs for larger models, but needs fast interconnect.
- **Serverless/autoscaling serving** — scales replicas to demand, but cold starts hurt TTFT for large models.

## Related
- [Distributed Training](03-distributed-training.md)
- [Retrieval-Augmented Generation (RAG)](02-rag.md)
- [Vector Databases](01-vector-databases.md)
- [Transformers](../01-ml-foundations/05-transformers.md)
