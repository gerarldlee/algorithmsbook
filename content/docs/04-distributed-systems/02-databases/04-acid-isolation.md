---
title: "ACID and Isolation Levels"
weight: 4
toc: true
---

## What it is
ACID describes the four guarantees a transactional database offers: Atomicity (all-or-nothing), Consistency (constraints hold before/after), Isolation (concurrent transactions do not interfere), and Durability (committed writes survive crashes). Isolation is implemented at graduated "levels" that trade strictness against concurrency and anomalies.

## How it works
Isolation levels define which anomalies are permitted. Read committed prevents dirty reads; repeatable read additionally prevents non-repeatable reads; snapshot isolation (often MVCC-based) gives each transaction a consistent view of data as of its start; serializable prevents all anomalies (including write skew and phantoms), typically via two-phase locking (2PL) or serializable snapshot isolation (SSI). Multi-version concurrency control (MVCC) keeps multiple row versions so readers never block writers and vice versa.

```yaml
isolation_levels:
  read_uncommitted: allows dirty reads; rarely used
  read_committed:     blocks dirty reads; allows non-repeatable reads & phantoms
  repeatable_read:    blocks dirty & non-repeatable reads; may allow phantoms
  snapshot (MVCC):    each txn sees a start-time snapshot; no dirty/non-repeatable reads
  serializable:       no anomalies at all; via 2PL or SSI
anomalies:
  dirty_read:         reads an uncommitted write
  non_repeatable_read: same row changes between two reads in one txn
  phantom_read:       a new matching row appears between two range scans
  write_skew:         two txns write based on a stale shared snapshot (needs serializable)
mvcc:
  mechanism: versioned rows with visibility timestamps; read/write non-blocking
  cleanup: vacuum/compaction removes obsolete versions
```

## Tradeoffs
| Property | Characteristic |
| --- | --- |
| Strictness vs. concurrency | Higher isolation reduces anomalies but increases lock contention and aborts. |
| Read throughput | MVCC lets long reads run without blocking writers (good for analytics+OLTP mix). |
| Storage overhead | Versioning retains multiple row copies until vacuum/compaction. |
| Latency under contention | Serializable via 2PL can serialize hot rows; SSI aborts speculative writes. |
| Durability | fsync of the WAL on commit gives durability but caps commit throughput. |

## When to use
- Serializable for financial transfers, inventory, and other invariants where anomalies are unacceptable.
- Snapshot/read committed for general OLTP needing high concurrency with minimal anomalies.
- Read committed (or lower) only for workloads where occasional inconsistency is tolerable and throughput dominates.

## Alternatives
- Eventually consistent systems (NoSQL quorum) — far higher write throughput, but no multi-record atomicity.
- Single-threaded transactional stores (Redis, Spanner-style serializable) — simpler reasoning, but limited per-node throughput.
- Sagas (app-level compensating transactions) — long-running distributed workflows where DB transactions cannot span services.

## Related
- [Relational Modeling](01-relational-modeling.md)
- [Storage Engines](03-storage-engines.md)
- [Replication](05-replication.md)
- [CAP and PACELC Theorems](../01-consensus/01-cap-pacelc.md)
