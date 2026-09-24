---
title: "Storage Engines"
weight: 3
toc: true
---

## What it is
A storage engine is the component of a database that physically organizes and retrieves data on disk and in memory — how records are laid out, indexed, and made durable. The two dominant families are B-tree (page-oriented, in-place updates) and LSM-tree (log-structured, immutable sorted runs).

## How it works
B-tree engines keep records in fixed-size pages arranged as a balanced tree, updating pages in place and protecting against crashes with a write-ahead log (WAL). LSM-tree engines buffer writes in an in-memory memtable, flush it to disk as an immutable sorted file (SSTable), and periodically merge overlapping files in background compaction to reclaim space and bound read amplification. Both rely on a WAL so committed writes survive a crash before they reach their final on-disk structure.

```yaml
b-tree:
  structure: balanced tree of fixed-size pages
  update: in-place page writes
  durability: write-ahead log (WAL) + dirty page flush
  read_amplification: low (single tree traversal)
  write_amplification: high (page rewrites, fragmentation)
  examples: [InnoDB, Postgres heap, BerkeleyDB]
lsm-tree:
  structure: memtable -> immutable SSTable levels
  update: append-only; compaction merges levels
  durability: WAL/memtable + periodic SSTable flush
  read_amplification: higher (may probe multiple levels + bloom filters)
  write_amplification: low, sequential (but compaction rewrites)
  examples: [RocksDB, LevelDB, Cassandra, HBase]
common: [WAL for crash recovery, bloom filters to skip absent keys]
```

## Tradeoffs
| Property | B-tree | LSM-tree |
| --- | --- | --- |
| Write throughput | Lower; random in-place page writes | High; append-only sequential writes |
| Read latency | Lower; one tree lookup | Higher; multiple files/levels, mitigated by bloom filters |
| Space overhead | Fragmentation, page slack | Compaction rewrites, temporary file growth |
| Predictability | Stable, bounded worst case | Compaction can cause latency spikes |
| Crash recovery | WAL replay | WAL + SSTable reuse |

## When to use
- B-tree engines for transaction-heavy OLTP with many point reads and in-place updates (banking, orders).
- LSM-tree engines for write-heavy and append-mostly workloads such as time-series, metrics, and event ingestion.
- Any engine where durability across crash is required — rely on the WAL, not the in-memory cache.

## Alternatives
- Heap files with append-only logs (classic) — simple sequential writes, but require periodic compaction and slower point reads.
- In-memory engines (Redis, MemSQL) — eliminate disk I/O entirely at the cost of capacity and durability (mitigated by snapshots/AOF).
- Specialized columnar engines (ClickHouse, Parquet) — fast column scans for analytics, poor for row-level OLTP updates.

## Related
- [Relational Modeling](01-relational-modeling.md)
- [NoSQL Databases](02-nosql.md)
- [ACID and Isolation Levels](04-acid-isolation.md)
- [Distributed Query and Point-in-Time Recovery](07-distributed-query-pitr.md)
