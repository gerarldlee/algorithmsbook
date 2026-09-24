---
title: "Feature Stores and Pipelines"
weight: 2
toc: true
---

## What it is
A feature store is a centralized system for defining, computing, storing, and serving ML features so that training and serving use identical feature definitions and values. Feature pipelines are the data-engineering workflows that transform raw data into those features, supporting both batch (offline) and streaming (online) computation.

## How it works
Features are defined once (with a name, type, and transformation logic) and materialized into two coordinated stores. The **offline store** holds point-in-time-correct historical features for training-set generation, avoiding data leakage. The **online store** serves the same features with low latency for real-time prediction. A **feature registry** tracks definitions and metadata, while orchestration (e.g. Airflow, Flyte, Kubeflow) schedules the compute.

```yaml
# Feature store and pipeline anatomy
registry:
  - name: user_7d_spend
    type: "double"
    transformation: "sum(orders.amount) over last 7 days"
    owners: [fraud_team]
offline_store:
  purpose: "historical, point-in-time-correct training sets"
  example: [warehouse, lakehouse, parquet]
online_store:
  purpose: "low-latency feature lookup at serving time"
  example: [Redis, DynamoDB, embedded KV]
ingestion:
  batch: "scheduled recompute for backfills and training"
  streaming: "Flink/Kafka for fresh online features"
orchestration: [Airflow, Flyte, Kubeflow Pipelines]
```

## Tradeoffs

| Aspect | Notes |
| --- | --- |
| Batch vs streaming features | Batch is simpler and complete; streaming is fresher but operationally heavier |
| Centralized vs per-team | Centralization reduces duplication/skew; adds coupling and governance overhead |
| Point-in-time correctness | Avoids leakage but requires time-travel-capable storage and more engineering |
| Online store cost | Low-latency serving is expensive; cache only features actually used in production |
| Freshness vs consistency | Streaming updates can diverge from training-time values if not versioned |

## When to use
- Multiple teams reuse the same features and must avoid duplicate, inconsistent definitions.
- Real-time prediction that needs fresh features unavailable at model training time.
- Regulated or high-stakes domains where point-in-time correctness and auditability matter.

## Alternatives
- **Ad-hoc feature scripts per team** — fast and flexible, but breeds duplication, skew, and leakage.
- **Embedding features in the model server** — no extra infrastructure, but loses reuse, versioning, and consistency guarantees.

## Related
- [ML System Design](01-ml-system-design.md)
- [Inference Serving](04-inference-serving.md)
- [Vector Databases](../03-genai/01-vector-databases.md)
