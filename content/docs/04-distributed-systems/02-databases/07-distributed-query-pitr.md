---
title: "Distributed Query and Point-in-Time Recovery"
weight: 7
toc: true
---

## What it is
Distributed query execution fans a query out across shards/replicas and merges partial results (scatter-gather), while point-in-time recovery (PITR) restores a database to an exact past moment using continuous WAL archiving combined with periodic base backups/snapshots.

## How it works
A distributed query coordinator parses and plans the query, pushes filters and aggregations down to each shard, and merges the partial results (shuffle for joins, merge for sorts). PITR continuously ships WAL segments to archive storage and periodically captures a full snapshot; recovery replays the archived WAL from the snapshot time up to the target timestamp, enabling rollback to any point between snapshots. Change data capture (CDC) is the live analogue: the log itself is published as a stream to downstream consumers.

```yaml
distributed_query:
  coordinator: parses, plans, routes to shards
  pushdown: filters/aggregates execute on each shard (reduce network)
  merge: sort-merge / hash-join / shuffle across shards
  failure: retry on replica; skip slow shards (speculative execution)
pitr:
  base_backup: periodic full snapshot
  wal_archiving: continuous shipping of WAL segments to object storage
  recovery: restore snapshot + replay WAL to target timestamp
  rpo: near-zero (bounded by WAL archiving lag)
  rto: restore+replay time, grows with WAL volume
cdc:
  mechanism: publish WAL/commit log as a change stream
  consumers: replication, caches, search indexes, data warehouses
```

## Tradeoffs
| Property | Characteristic |
| --- | --- |
| Query latency | Scatter-gather is fast when pushdown works, slow when large intermediate results must shuffle. |
| Query consistency | Cross-shard reads without global MVCC can observe mixed versions. |
| PITR RPO | Near-zero with continuous archiving; coarse with only periodic snapshots. |
| PITR RTO | Replaying large WAL volumes can be slow; snapshot+parallel replay helps. |
| Storage cost | Archived WAL and extra snapshots consume object-storage capacity. |

## When to use
- Distributed query engines (Presto/Trino, BigQuery) for analytics spanning many shards or external sources.
- PITR for databases that must recover to a precise time after operator error or data corruption.
- CDC for streaming changes into search indexes, caches, and data warehouses without batch ETL.

## Alternatives
- Full snapshots only — simpler, but coarse RPO (loss up to the last snapshot).
- Logical replication/streaming — continuous, but tracks forward state rather than arbitrary rollback.
- Batch ETL — moves data at scale, but high latency compared to CDC.

## Related
- [Storage Engines](03-storage-engines.md)
- [Replication](05-replication.md)
- [Sharding](06-sharding.md)
- [NoSQL Databases](02-nosql.md)
