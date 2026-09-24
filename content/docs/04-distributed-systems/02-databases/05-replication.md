---
title: "Replication"
weight: 5
toc: true
---

## What it is
Replication keeps copies of the same data on multiple nodes to improve availability, durability, and read throughput. The three topologies are leader-follower (single-leader), multi-leader, and leaderless; the core tension is synchronous vs. asynchronous propagation of writes.

## How it works
In leader-follower replication, one node accepts writes and streams them (as a WAL/statement/row log) to followers, which serve reads. Multi-leader allows each leader to accept writes and reconciles conflicts across sites. Leaderless (Dynamo-style) lets any replica accept a write; reads/writes use a quorum (e.g., `W + R > N`) to reconcile versions, with anti-entropy and read-repair converging stale replicas. Synchronous replication guarantees the follower has the write before commit; asynchronous replication is fast but can lose data if the leader fails.

```yaml
topologies:
  leader_follower:
    writers: 1 leader
    readers: all nodes
    failover: manual/automatic promotion (split-brain risk)
    examples: [PostgreSQL, MySQL, Kafka]
  multi_leader:
    writers: multiple sites/leaders
    readers: any
    conflicts: needs conflict resolution (LWW, CRDTs, app logic)
    examples: [CouchDB, multi-DC setups]
  leaderless:
    writers: any replica (quorum-based)
    readers: quorum + read-repair
    examples: [DynamoDB, Cassandra, Riak]
sync_modes:
  synchronous: no data loss on leader failure; commit latency >= slowest follower
  asynchronous: low latency; risk of lost writes on failover
quorum: "with N replicas, W write + R read; W + R > N for overlap"
```

## Tradeoffs
| Property | Characteristic |
| --- | --- |
| Consistency | Sync replication is strongly consistent but slow; async is fast but may diverge. |
| Read throughput | Scale reads across followers; writes still bottleneck on the leader. |
| Failover | Automatic promotion risks split-brain; manual is slow. |
| Conflict handling | Multi-leader/leaderless need LWW/CRDT/app logic; last-writer-wins can silently drop updates. |
| Latency vs. durability | Sync trades commit latency for zero-loss durability; async the reverse. |

## When to use
- Leader-follower for single-region OLTP needing read scaling and simple failover.
- Multi-leader for multi-datacenter deployments where each site needs local writes (offline-capable apps).
- Leaderless/quorum for very high availability and write throughput where eventual consistency suffices.

## Alternatives
- Single node with backups (snapshots) — simplest, but no HA and RPO measured in backup interval.
- Shared-disk/active-passive clusters — simpler failover than logical replication, but limited write scale.
- Event sourcing/CDC — rebuild state from an append-only log; strong audit, higher complexity.

## Related
- [ACID and Isolation Levels](04-acid-isolation.md)
- [Sharding](06-sharding.md)
- [Distributed Query and Point-in-Time Recovery](07-distributed-query-pitr.md)
- [Consensus](../01-consensus/02-consensus.md)
