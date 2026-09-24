---
title: "End-to-End ML System Design: Training, Validation, Feature Engineering, and Inference Pipelines"
weight: 1
toc: true
---

## What it is
End-to-end machine learning system design is the engineering of a model’s complete lifecycle, from data collection and feature engineering through training, validation, deployment, inference, and monitoring. The model is one component in a data and software system; its quality depends on the contracts between data, features, artifacts, and serving behavior.

## How it works
A production ML system separates the **training plane** from the **serving plane**. The training plane ingests labeled data, validates schemas and quality, computes historical features, trains candidate models, evaluates them against validation and test sets, and registers an approved artifact. The serving plane loads that artifact behind an API, obtains request-time features, performs inference, applies post-processing, and records the prediction and its input context.

The two planes share versioned feature definitions and model metadata. **Feature consistency** means training and serving use the same transformation semantics. **Data drift** is a change in input distributions, while **concept drift** is a change in the relationship between inputs and outcomes. Monitoring compares these signals with thresholds and can trigger investigation, retraining, or rollback. A model registry should identify the training data, feature definitions, code revision, evaluation report, and serving configuration for every registered version.

A typical request path is:

1. Validate the request and authenticate the caller.
2. Resolve the active model version and fetch online features.
3. Build the feature vector, run inference, and apply calibrated post-processing.
4. Return the prediction while logging the model version, feature version, request identifier, and latency metrics.
5. Join predictions with delayed ground truth for offline evaluation and feedback.

The system contract should define feature freshness, missing-value behavior, timeout and retry policies, model compatibility, and rollback behavior. A prediction is not complete until its provenance and observability data are available.

```yaml
system:
  data_plane:
    sources: [events, databases, third_party_feeds]
    ingestion: [schema_validation, deduplication, labeling]
    storage: [warehouse, object_storage, online_store]
  training_plane:
    feature_engineering: [versioned_definitions, point_in_time_joins]
    training: [experiment_tracking, hyperparameter_search]
    validation: [offline_metrics, holdout_test, calibration]
    registry: [model_artifact, dataset_version, code_revision]
  serving_plane:
    request: [authentication, schema_validation, online_feature_lookup]
    inference: [model_server, batching, post_processing]
    response: [prediction, request_id, model_version]
  feedback_plane:
    monitoring: [latency, quality, data_drift, concept_drift]
    actions: [alert, rollback, retraining, investigation]
  contracts:
    features: [name, type, freshness, null_policy, version]
    models: [artifact_digest, runtime, hardware, compatibility]
```

## Tradeoffs

| Design choice | Gain | Cost |
| --- | --- | --- |
| Batch and asynchronous scoring | High throughput and predictable resource use | Results are delayed and feedback is less immediate |
| Synchronous online inference | Low response latency and immediate predictions | A request path must meet an availability and latency SLO |
| Centralized feature platform | Reuse, governance, and train/serve consistency | A shared dependency and operational overhead |
| Frequent retraining | Faster response to changing data | More compute, validation, and rollback risk |
| Rich observability | Faster diagnosis of quality and reliability failures | More storage, privacy controls, and analysis work |

## When to use
- You need a model whose predictions affect revenue, safety, compliance, or user experience.
- You must reproduce a training result from its data, code, feature definitions, and configuration.
- Training and serving teams share features and need a defined consistency contract.
- Predictions need rollback, auditability, or delayed-outcome evaluation in production.
- Model inputs or outcomes can drift, so retraining must be evidence-driven rather than calendar-driven.

## Alternatives
- **Notebook-only analysis** — fastest for exploration, but it does not provide an auditable training or serving lifecycle.
- **Batch-only scoring** — simpler and cheaper for periodic decisions, but it cannot support immediate user-facing predictions.
- **Managed ML platform** — reduces infrastructure work, but adds vendor cost, platform constraints, and less control over the runtime.
- **Rule-based or heuristic system** — easier to interpret and change for stable rules, but it does not learn complex relationships from labeled data.

## Related
- [Feature Stores, Dataset Versioning (DVC), and Pipeline Orchestration (Airflow, Kubeflow)](02-feature-stores-pipelines.md)
- [High-Performance Inference: Batching, Parallel Execution, and Real-Time vs Async Pipeline Serving](04-inference-serving.md)
- [Supervised Learning](../01-ml-foundations/01-supervised-learning.md)
- [Unsupervised Learning: K-Means, Hierarchical Clustering, Principal Component Analysis (PCA)](../01-ml-foundations/02-unsupervised-learning.md)
