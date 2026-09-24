---
title: "Distributed Training"
weight: 3
toc: true
---

## What it is
Distributed training splits the computation and memory of training a model across many GPUs or machines, because modern models are too large to fit on a single device. The three canonical forms are **data parallelism**, **model parallelism** (tensor/pipeline), and hybrid **3D parallelism**, coordinated by collective communication and memory-saving sharding.

## How it works

- **Data parallelism:** each worker holds a full copy of the model on a different batch shard, computes gradients, then averages them with an **all-reduce** before the optimizer step. It scales throughput but not memory.
- **Model parallelism:** splits the model itself across devices. **Tensor parallelism** shards individual weight matrices/layers; **pipeline parallelism** partitions layers into stages that process micro-batches in a bubble-minimizing schedule.
- **ZeRO / FSDP (Fully Sharded Data Parallel):** shards optimizer states, gradients, and parameters across workers so each device holds only a slice, dramatically cutting per-device memory while keeping data-parallel simplicity.
- **Checkpointing:** saves sharded weights and optimizer states so training can resume or scale up/down without losing progress.

```yaml
# Distributed training (architecture description)
parallelism:
  data:    shard the batch; all-reduce gradients each step (throughput)
  tensor:  shard weight matrices across GPUs (intra-node, high bandwidth)
  pipeline: split layers into stages; micro-batch scheduling hides latency
  hybrid:  3D = data + tensor + pipeline combined for very large models

memory:
  zero_stage_1: shard optimizer states
  zero_stage_2: + shard gradients
  zero_stage_3: + shard parameters (FSDP)

communication:
  - all-reduce (gradient averaging)
  - all-gather (collect sharded parameters on demand)
  - reduce-scatter (precondition gradients before the step)

reliability:
  - checkpointing: persist sharded weights/optimizer state
  - elastic scaling: resume on a different worker count
```

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Throughput | Data parallelism scales throughput linearly until communication bound |
| Memory | ZeRO/FSDP shrinks per-GPU memory at the cost of more communication |
| Network | All-reduce and parameter gather need fast interconnects (NVLink/InfiniBand) |
| Pipeline bubbles | Pipeline parallelism wastes idle cycles at stage boundaries |
| Fault tolerance | More devices mean more failure modes; checkpoint/resume is essential |

## When to use
- Training models whose parameters or optimizer states exceed a single GPU's memory.
- Large-batch pretraining where many GPUs can hide gradient-sync latency.
- Fine-tuning LLMs with FSDP/LoRA to fit consumer-scale clusters.

## Alternatives
- **Gradient checkpointing** — trades recomputation for memory with no extra hardware, but adds a forward pass.
- **Parameter-efficient fine-tuning (LoRA)** — trains tiny adapters instead of full weights, but can underperform full tuning on hard tasks.
- **Gradient accumulation** — emulates larger batches on one GPU, but slower and memory-bound for big models.

## Related
- [LLM Serving](04-llm-serving.md)
- [AI Agents](05-ai-agents.md)
- [Transformers](../01-ml-foundations/05-transformers.md)
- [Neural Networks](../01-ml-foundations/03-neural-networks.md)
