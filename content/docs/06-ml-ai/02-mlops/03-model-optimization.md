---
title: "Model Optimization"
weight: 3
toc: true
---

## What it is
Model optimization is the process of shrinking model size, latency, and memory footprint while preserving as much accuracy as possible. It covers quantization, pruning, knowledge distillation, graph/compiler optimization, and hardware targeting, enabling deployment to constrained CPUs, mobile devices, and GPUs with higher throughput.

## How it works
Optimization trades precision and parameter count for efficiency. **Quantization** reduces numerical precision (e.g. FP32→INT8/INT4), shrinking memory and speeding up integer kernels. **Pruning** removes near-zero or low-importance weights/neurons. **Distillation** trains a smaller "student" model to mimic a larger "teacher" model's outputs. **Compilation/graph optimization** fuses operators and eliminates overhead (TensorRT, ONNX Runtime, torch.compile), while **hardware targeting** adapts kernels to specific accelerators.

```yaml
# Common optimization techniques and levers
quantization:
  type: [post_training, quantization_aware_training]
  precision: [FP16, INT8, INT4, FP8]
  benefit: "2-8x smaller, faster integer math"
pruning:
  scope: [unstructured_weights, structured_channels]
  benefit: "sparser compute, smaller footprint"
distillation:
  teacher: "large pretrained model"
  student: "small model trained on teacher logits"
  benefit: "small model retains much of teacher accuracy"
compilation:
  tools: [TensorRT, ONNX_Runtime, torch.compile, XLA]
  benefit: "operator fusion, kernel tuning, lower latency"
hardware_targeting:
  targets: [GPU, TPU, NPU, edge CPU]
```

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Quantization aggressiveness | Lower precision shrinks models but risks accuracy loss on sensitive tasks |
| Pruning | Sparse models may not speed up real hardware without sparse-kernel support |
| Distillation | Adds a training stage and needs the teacher's logits, but yields compact models |
| Compilation | Big latency wins but longer build times and less portability across hardware |
| Accuracy vs efficiency | Every technique trades some quality; must validate on the target metric |

## When to use
- Serving large models under tight latency or memory budgets (mobile, edge, high-QPS).
- Reducing per-inference GPU/cloud cost for LLMs and vision models.
- Deploying models to hardware lacking FP32 support or with small on-device memory.

## Alternatives
- **Larger/faster hardware** — simplest and preserves accuracy, but costs more per inference.
- **Smaller architecture from the start** — avoids post-hoc optimization, but may under-fit the task.

## Related
- [Inference Serving](04-inference-serving.md)
- [Deep Learning Architectures](../01-ml-foundations/04-deep-learning-architectures.md)
- [LLM Serving](../03-genai/04-llm-serving.md)
