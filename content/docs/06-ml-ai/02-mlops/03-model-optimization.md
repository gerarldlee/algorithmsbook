---
title: "Model Optimization: Quantization (INT8/FP16), Pruning, Knowledge Distillation, and Model Compilation (TensorRT, ONNX)"
weight: 3
toc: true
---

## What it is
Model optimization reduces a model’s memory footprint, latency, or cost while measuring the resulting change in predictive quality. The main techniques are quantization, pruning, knowledge distillation, and graph or kernel compilation. The right technique depends on the target hardware, workload, model architecture, and acceptable quality loss.

## How it works
**Quantization** represents weights, activations, or both with fewer bits. FP16 typically halves the storage of an FP32 weight and can increase throughput on hardware with efficient half-precision kernels. INT8 and INT4 reduce memory and bandwidth further, but require a calibration or quantization-aware training process and supported kernels. Per-channel scales, calibration data, and unsupported operators can determine whether the conversion is useful.

**Pruning** removes weights or structures selected by a sparsity criterion. Unstructured pruning can produce a sparse representation, but speedup requires a runtime and hardware that exploit that sparsity. Structured pruning removes channels, heads, or blocks and is more likely to produce a smaller dense graph, at the cost of a larger capacity change. **Knowledge distillation** trains a smaller student model against a teacher’s outputs or intermediate signals; the student can specialize to the teacher and retain useful behavior on the deployment distribution.

**Compilation** lowers a framework graph into an execution plan. ONNX provides a model interchange format, ONNX Runtime provides a cross-platform execution engine, and TensorRT builds an optimized NVIDIA deployment plan. Fusion, layout conversion, kernel selection, and memory planning reduce runtime overhead, but compiled artifacts are tied to a software and hardware configuration. Always evaluate an optimized artifact against the same validation protocol and target hardware as the original.

A reproducible optimization pipeline records the source model, precision and sparsity settings, calibration dataset, compiler version, target device, evaluation results, and artifact digest. The candidate should be tested for numerical overflow, unsupported operators, latency at realistic batch sizes, memory pressure, and output quality.

```yaml
optimization_pipeline:
  source:
    artifact: registered_model
    evaluation: baseline_validation_report
  quantization:
    methods: [post_training_quantization, quantization_aware_training]
    precisions: [FP16, INT8, INT4]
    checks: [calibration, saturation, unsupported_operators]
  pruning:
    modes: [unstructured_weights, structured_channels]
    checks: [sparsity_support, accuracy, target_latency]
  distillation:
    teacher: large_pretrained_model
    student: compact_deployment_model
    objective: [logits, intermediate_features, task_loss]
  compilation:
    model_interchange: ONNX
    runtimes: [ONNX_Runtime, TensorRT]
    optimizations: [operator_fusion, layout_conversion, kernel_selection]
  release_gate:
    metrics: [quality, p95_latency, throughput, peak_memory]
    provenance: [source_digest, settings, compiler, device, report]
```

## Tradeoffs

| Technique | Gain | Cost |
| --- | --- | --- |
| FP16 or INT8 quantization | Lower memory traffic and faster supported kernels | Calibration work, hardware support, and possible quality loss |
| INT4 or more aggressive precision | Greater model and memory reduction | Higher sensitivity to outliers, calibration, and accuracy loss |
| Unstructured pruning | Potentially high parameter reduction | Sparse kernels and runtime support may be required for speedup |
| Structured pruning | Simpler dense execution and possible kernel speedup | Removes capacity in larger units and can reduce quality more sharply |
| Knowledge distillation | A compact model specialized to deployment behavior | Requires teacher outputs, extra training, and teacher-dataset selection |
| ONNX or TensorRT compilation | Lower runtime overhead and hardware-tuned execution | Longer builds, narrower portability, and compiler-version coupling |

## When to use
- You have a model that misses a latency or memory budget on the target device.
- Model weights dominate memory use, or deployment hardware has optimized low-precision kernels.
- You need to reduce per-request cost at high request volume.
- You can validate quality on a representative, time-split evaluation set.
- A model must run on a constrained device such as a mobile device, edge CPU, or accelerator.

## Alternatives
- **More capable hardware** — preserves the original model and simplifies software changes, but raises capital and operating cost.
- **A smaller model from the start** — avoids conversion overhead, but may have lower capacity before task-specific training.
- **Pruning or distillation with the original runtime** — can improve size, but may not deliver the target latency without kernel or compiler support.
- **Model architecture search** — can produce a better deployment fit, but requires a larger training and evaluation budget.

## Related
- [High-Performance Inference: Batching, Parallel Execution, and Real-Time vs Async Pipeline Serving](04-inference-serving.md)
- [Deep Learning Architectures](../01-ml-foundations/04-deep-learning-architectures.md)
- [Feature Stores, Dataset Versioning (DVC), and Pipeline Orchestration (Airflow, Kubeflow)](02-feature-stores-pipelines.md)
