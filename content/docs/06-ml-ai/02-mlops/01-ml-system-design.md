---
title: "ML System Design"
weight: 1
toc: true
---

## What it is
ML system design is the end-to-end engineering discipline of turning a trained model into a reliable, observable, and maintainable production system. It spans data pipelines, feature computation, training, evaluation, deployment, serving, and monitoring, treating the model as one component of a larger software and data architecture rather than a standalone artifact.

## How it works
A production ML system separates the **training plane** from the **serving plane**. The training plane ingests labeled data, computes features, trains and evaluates candidates, and registers a model artifact in a model registry. The serving plane loads an approved artifact behind an API, applies the same feature logic at request time, and returns predictions. Two shared concerns bind the planes together:

- **Feature consistency** — training-time and serving-time feature logic must produce identical values, otherwise the model sees a different input distribution in production (train/serve skew).
- **Monitoring & drift** — track *data drift* (input distribution shifts), *concept drift* (the true input→label relationship changes), and *model drift* (output distribution shifts), triggering retraining or rollback.

```yaml
# Conceptual anatomy of a production ML system
training_plane:
  data: [ingestion, validation, labeling]
  features: "feature store (offline) computes training sets"
  training: [experiment tracking, hyperparameter tuning]
  evaluation: [offline metrics, validation, model registry]
serving_plane:
  features: "feature store (online) serves low-latency features"
  inference: [model server, batch/real-time predictors]
  post_processing: [thresholding, calibration, business rules]
shared:
  monitoring: [data_drift, concept_drift, model_drift]
  feedback: [prediction logs, ground-truth capture]
```

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Batch vs real-time | Batch is simpler and cheaper; real-time adds latency and freshness |
| Retraining cadence | Frequent retraining reduces drift but raises compute/ops cost |
| Feature reuse | A feature store reduces skew but adds a new infra dependency |
| Evaluation fidelity | Offline metrics are cheap proxies; online (A/B) is slower but authoritative |
| Operational surface | More components (registry, store, monitoring) improve quality at higher complexity |

## When to use
- Deploying any model whose predictions drive revenue or decisions, requiring drift monitoring and rollback.
- Systems where many teams share features and need train/serve consistency at scale.
- High-frequency or high-stakes predictions where stale models cause measurable harm.

## Alternatives
- **Notebook → script handoff** — fastest path to a prototype, but no reproducibility, monitoring, or drift control.
- **Batch-only scoring (offline reports)** — simpler and cheaper, but no real-time responsiveness or feedback loop.

## Related
- [Feature Stores and Pipelines](02-feature-stores-pipelines.md)
- [Model Optimization](03-model-optimization.md)
- [Inference Serving](04-inference-serving.md)
- [ML Foundations](../01-ml-foundations/01-supervised-learning.md)
