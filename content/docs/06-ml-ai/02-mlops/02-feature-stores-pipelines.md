---
title: "Feature Stores, Dataset Versioning (DVC), and Pipeline Orchestration (Airflow, Kubeflow)"
weight: 2
toc: true
---

## What it is
A production feature store is a managed system for defining, computing, versioning, storing, and serving machine-learning features. **Dataset versioning** records the data and transformations used to create a training set, while **pipeline orchestration** schedules and monitors the work that produces features, datasets, and models. Together, these systems make the path from raw data to serving inputs reproducible.

## How it works
Feature definitions identify a feature by name, type, owner, source, transformation contract, freshness requirement, and compatibility version. A **feature registry** stores those definitions; it is not the low-latency value store. A batch pipeline materializes historical values in a warehouse or lakehouse, while a streaming or scheduled online pipeline materializes current feature values in a key-value store or feature service.

A training-set builder performs a **point-in-time-correct join**: for each event timestamp, it selects feature values that existed at that timestamp rather than values written later. This prevents **data leakage**, in which a training example contains information that would not have been available when its prediction was made. At serving time, the online path normally fetches a precomputed feature value keyed by entity and lookup time. A feature explicitly declared as request-time derived applies its versioned transformation definition to the current request and can materialize the result; the online path does not generally rerun every batch transformation. The response records the feature version used.

DVC versions data artifacts through a Git repository-backed metadata model. A `.dvc` file records a content identifier, while remote object storage holds large files; Git versions the pipeline definition and metadata without storing large datasets in every commit. A production pipeline also needs schema checks, freshness checks, idempotent writes, retries, lineage, and a quarantine path for invalid records.

Airflow schedules DAGs with explicit dependencies and backfills. Kubeflow Pipelines packages pipeline steps as versioned containerized components and records their inputs, outputs, and execution status. Both systems require retry policies, timeouts, idempotent task implementations, and a distinction between a data-quality failure and an infrastructure failure.

```yaml
feature_platform:
  registry:
    definition_fields: [name, type, owner, source, transformation, freshness, version]
  offline_store:
    purpose: historical_training_data
    materialization: batch_computed_values
    join_policy: point_in_time_correct
    examples: [warehouse, lakehouse, parquet]
  online_store:
    purpose: request_time_lookup
    materialization: precomputed_values_by_entity
    request_time_derived_features: apply_versioned_definition
    consistency: versioned_feature_values
    examples: [Redis, DynamoDB, feature_service]
dataset_versioning:
  tool: dvc
  metadata: git_tracked
  artifact_storage: remote_object_storage
  identity: content_hash
pipeline_orchestration:
  engine: [Airflow, Kubeflow_Pipelines]
  execution: [scheduled, triggered, backfill]
  required_controls:
    dependencies: enforced
    retries: bounded
    timeouts: per_task
    lineage: recorded_per_run
  side_effect_contract: idempotent_writes_or_compensation
```

## Tradeoffs

| Design choice | Gain | Cost |
| --- | --- | --- |
| Batch features | Simple backfills and reproducible historical computation | Values are not continuously fresh |
| Streaming features | Near-real-time online values | More state, ordering, replay, and operational complexity |
| Centralized feature store | Reuse, governance, and a shared consistency contract | A new dependency with centralized ownership and failure impact |
| Point-in-time joins | Prevents leakage and supports valid historical examples | Requires time-aware storage, metadata, and more complex queries |
| DVC metadata in Git | Reviewable data lineage without committing large artifacts | Remote storage and retrieval operations must be managed separately |
| Airflow or Kubeflow orchestration | Explicit dependencies, retries, and run history | Workflows require idempotency, backpressure, and operational tuning |

## When to use
- Several models or teams reuse the same feature definitions.
- You need a point-in-time-correct training set and reproducible dataset lineage.
- Online predictions require fresh values that are not available in the request payload.
- A regulator, auditor, or incident team must trace a model result to its data and transformations.
- Feature updates must be replayed, backfilled, or coordinated across batch and streaming paths.

## Alternatives
- **Ad-hoc feature scripts** — flexible for exploration, but they duplicate logic and make skew, leakage, and lineage harder to detect.
- **Warehouse-only feature computation** — centralizes batch data and simplifies governance, but may not meet online latency or freshness requirements.
- **Application-managed features** — keeps infrastructure small, but ties feature semantics to one service and limits reuse.
- **Managed feature platform** — reduces operational work, but introduces vendor dependencies, pricing, and platform-specific contracts.

## Related
- [End-to-End ML System Design: Training, Validation, Feature Engineering, and Inference Pipelines](01-ml-system-design.md)
- [High-Performance Inference: Batching, Parallel Execution, and Real-Time vs Async Pipeline Serving](04-inference-serving.md)
- [Model Optimization: Quantization (INT8/FP16), Pruning, Knowledge Distillation, and Model Compilation (TensorRT, ONNX)](03-model-optimization.md)
- [Supervised Learning](../01-ml-foundations/01-supervised-learning.md)
- [Stateful Stream & Batch Processing Frameworks](../../03-messaging/03-data-engineering-stream-processing/01-stateful-stream-batch-processing.md)
- [Data Architecture & Lakehouse Engines](../../03-messaging/03-data-engineering-stream-processing/02-lakehouse-architectures.md)
