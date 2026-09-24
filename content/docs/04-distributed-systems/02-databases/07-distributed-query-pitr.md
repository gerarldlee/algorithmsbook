---
title: "Distributed Query Execution, Global Secondary Indexes, and Point-In-Time Recovery (PITR)"
weight: 7
toc: true
---

## What it is

Distributed query execution coordinates work across partitions or replicas, pushes predicates and aggregations toward the data, and combines partial results. A **global secondary index** maintains search entries across partitions so a query can locate matching rows without scanning every shard. Point-in-time recovery (PITR) restores a database to a chosen past transaction point by replaying durable change logs over a base backup.

## How it works

A query coordinator parses and plans a statement, resolves partition predicates, and chooses local execution paths such as index scans, hash aggregation, or sorted merge. Predicate and aggregate pushdown reduce the bytes crossing the network. A scatter-gather plan sends work to the relevant shards, then merges results; joins across partitions may require a shuffle exchange, a distributed hash table, or a coordinator-side merge. Replicas can execute duplicate work for availability, but the coordinator must preserve the required consistency and deduplication semantics.

A local secondary index accelerates predicates on one partition. A global secondary index records a partition key together with indexed values and is maintained asynchronously or synchronously depending on the service. Because writes can arrive on many partitions, global indexes require a consistency model, duplicate handling, and a repair path when a partition or consumer fails. A query can use the global index to produce candidate keys, then fetch rows from the owning partitions.

PITR uses a base backup as the starting image and archives WAL segments or an equivalent redo log continuously. Recovery restores the base image into a clean destination, confirms the target timestamp, replays archived changes through that point, and verifies integrity before the restored instance becomes writable. Continuous log archiving reduces the recovery point objective (RPO) to the archive lag; restore and replay time determine the recovery time objective (RTO). Change data capture (CDC) uses the same durable change stream for downstream consumers rather than only for rollback.

```sql
CREATE INDEX orders_status_created_idx
ON orders (status, created_at DESC);

SELECT order_id, customer_id, created_at
FROM orders
WHERE status = 'ready'
  AND created_at >= '2026-09-01'
ORDER BY created_at DESC;
```

```yaml
distributed_query:
  coordinator: plan_and_route
  pushdown: filter_and_aggregate_on_each_shard
  merge: hash_join_or_sort_merge
  consistency: token_or_required_snapshot
  failure: retry_or_read_replica
global_secondary_index:
  entries: [partition_key, indexed_values, primary_key]
  maintenance: streaming_or_transactional
  repair: compare_and_rebuild_divergent_entries
pitr:
  base_backup: periodic_full_image
  redo_archive: continuous_wal_segments
  recovery: restore_replay_verify
  rpo: bounded_by_archive_lag
  rto: restore_and_replay_time
```

## Tradeoffs

| Property | Gain | Cost |
| --- | --- | --- |
| Predicate and aggregate pushdown | Less network traffic and less intermediate data | Requires partition-aware planning and can produce uneven work |
| Scatter-gather parallelism | Uses independent shards to reduce wall-clock latency for broad queries | Tail latency is controlled by the slowest shard |
| Local index | Simple, colocated lookup with the owning rows | Cannot efficiently find a value in another partition |
| Global secondary index | Broad searches can begin from indexed candidates | Extra write, storage, consistency, and repair work |
| Continuous WAL archive | Small PITR window and reusable change history | More archive storage and a dependable log pipeline |
| PITR restore | Recovery can target a transaction point before a failure | Replay time grows with the retained log volume |

## When to use

- Queries span many partitions, replicas, or external sources and can tolerate fan-out.
- Searches need to find rows without a table-wide scan across every shard.
- The database must recover from accidental deletion, corruption, or a bad deployment.
- A change stream must feed search indexes, caches, or analytical warehouses.

## Alternatives

- **Full snapshots only** — simple recovery, but the RPO is the interval between snapshots.
- **Local indexes and manual partition routing** — fewer moving parts, with application code responsible for cross-partition discovery.
- **Batch ETL** — predictable bulk movement, with higher latency than CDC.
- **A managed cross-region index** — less operational work, with provider-specific consistency and cost tradeoffs.

## Related

- [Storage Engines: OLTP (Row-Oriented) vs OLAP (Columnar/Parquet/ClickHouse)](03-storage-engines.md)
- [Database Replication (Leader-Follower, Multi-Leader, Leaderless/Dynamo-Style)](05-replication.md)
- [Partitioning & Sharding Strategies: Range, Hash, List, and Directory-Based Sharding](06-sharding.md)
- [NoSQL Classifications: Key-Value, Document, Columnar (Cassandra), and Graph Databases (Neo4j)](02-nosql.md)
