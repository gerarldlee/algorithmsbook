---
title: "Inference Serving"
weight: 4
toc: true
---

## What it is
Inference serving is the runtime layer that loads a trained model and delivers predictions to applications at production scale. It covers the serving mode (batch vs real-time), GPU scheduling, autoscaling, model servers, and optimizations such as KV-cache management for generative models.

## How it works
A model server (Triton, TorchServe, vLLM, TensorFlow Serving) loads one or more model versions, exposes an HTTP/gRPC API, and orchestrates requests against hardware. **Batch inference** amortizes overhead over large jobs, while **real-time inference** optimizes for per-request latency. **GPU scheduling** packs requests and manages memory/attention, and **autoscaling** adjusts replica counts to load. For autoregressive models, the **KV cache** stores attention key/value tensors across tokens to avoid recomputation, and **continuous batching** schedules new tokens as they are generated.

```yaml
# Inference serving anatomy
serving_modes:
  batch: "offline, high throughput, tolerant of latency"
  real_time: "online, low latency per request"
model_server:
  examples: [Triton, TorchServe, vLLM, TensorFlow_Serving]
  responsibilities: [model_versioning, batching, API, health]
gpu_scheduling:
  concerns: [memory_management, request_packing, kernel_efficiency]
  batching: [static, dynamic, continuous]
autoscaling:
  signals: [queue_depth, latency, GPU_utilization]
  policy: "scale replicas, not just hardware"
llm_optimizations:
  kv_cache: "cache attention K/V across generated tokens"
  paged_attention: "non-contiguous KV storage to reduce fragmentation"
```

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Batch vs real-time | Batch maximizes throughput; real-time minimizes latency but underutilizes hardware |
| Static vs dynamic batching | Static is predictable; dynamic improves GPU utilization at scheduling complexity |
| GPU vs CPU serving | GPUs are fast but costly and scarce; CPUs cheaper for small/frequent models |
| Autoscaling | Elasticity lowers idle cost but adds cold-start latency and complexity |
| KV-cache growth | Enables fast autoregressive decoding but memory scales with sequence length |

## When to use
- Low-latency online predictions for user-facing applications and APIs.
- High-throughput offline scoring of large datasets or media (batch mode).
- LLM generation requiring continuous batching and KV-cache management for cost efficiency.

## Alternatives
- **Serverless/on-demand inference** — zero idle cost and auto-scaling, but cold starts and payload limits.
- **Embedded/in-process inference** — lowest latency with no network hop, but no centralized versioning or scaling.

## Related
- [Model Optimization](03-model-optimization.md)
- [Feature Stores and Pipelines](02-feature-stores-pipelines.md)
- [LLM Serving](../03-genai/04-llm-serving.md)
- [Distributed Training](../03-genai/03-distributed-training.md)
