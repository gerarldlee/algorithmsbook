---
title: "Database Replication (Leader-Follower, Multi-Leader, Leaderless/Dynamo-Style)"
weight: 5
toc: true
---

## What it is

Database replication keeps copies of the same data on multiple nodes so the system can serve reads, survive failures, and improve durability. The main topologies are leader-follower, multi-leader, and leaderless replication; synchronous and asynchronous propagation determine the latency and durability boundary for writes.

## How it works

In leader-follower replication, one leader accepts writes and sends a WAL, row log, or logical change stream to followers. Followers apply changes in order and can serve reads. A synchronous follower acknowledgement extends the durability boundary to that follower only when the follower is configured to durably flush the replicated log or data before acknowledging it. Acknowledging receipt or replay without a durable flush extends replication but not the durability boundary. Waiting for a durable flush can add network and disk latency and can block progress when the follower is unavailable. Asynchronous acknowledgement keeps commits fast, but a leader failure can lose an acknowledged write that has not reached another durable copy.

Multi-leader replication lets independent writers accept changes in different regions or sites. It reduces write latency for local users, but concurrent updates can create conflicts. Leaders exchange changes and resolve them with rules such as last-writer-wins, version vectors, CRDTs, or application-specific reconciliation.

Leaderless replication lets any replica accept a write. A common quorum condition is `W + R > N` for `N` replicas, where `W` is the number of write acknowledgements and `R` is the number of read responses. Versions and vector clocks let the coordinator reconcile concurrent writes, while read repair and anti-entropy return stale replicas toward the converged value. Quorum overlap is a coordination property, not a complete application consistency policy by itself.

```yaml
topologies:
  leader_follower:
    writers: one_leader
    readers: leader_and_followers
    examples: [PostgreSQL, MySQL, Kafka]
  multi_leader:
    writers: multiple_regions
    conflict_resolution: [last_writer_wins, crdt, application]
    examples: [CouchDB, multi_region_sql]
  leaderless:
    writers: any_replica
    read_write_overlap: W_plus_R_greater_than_N
    convergence: [read_repair, anti_entropy, vector_clocks]
    examples: [DynamoDB, Cassandra, Riak]
propagation:
  synchronous: durable_follower_ack_before_commit
  asynchronous: follower_applies_after_commit
```

## Tradeoffs

| Property | Gain | Cost |
| --- | --- | --- |
| Synchronous replication | Extends durability to a follower only when it durably flushes before acknowledging | Commit latency includes remote acknowledgement and, when configured, the follower flush |
| Asynchronous replication | Lower write latency and higher availability during follower failure | A leader failover can lose the latest acknowledged writes |
| Read replicas | Scale reads and shorten distance to users | Reads can be stale unless the system defines a consistency token or wait |
| Multi-leader writes | Local writes and regional autonomy | Conflict resolution can discard or merge updates unpredictably |
| Leaderless writes | No single write bottleneck and flexible node placement | Quorum coordination, versioning, repair, and conflict handling add complexity |
| Read repair | Repairs stale replicas during normal reads | Repair work competes with user traffic and may be delayed if reads are rare |

## When to use

- You need read scaling with a clear single writer and straightforward failover.
- You need local writes in several regions and can design conflict resolution.
- You need high write availability and accept eventual convergence with explicit version handling.
- You can define the read consistency required by each user-visible operation.

## Alternatives

- **Backups without replicas** — simple recovery from snapshots, with a recovery point limited by backup frequency.
- **Shared-storage active-passive clustering** — one logical database with shared durable state, with limits from storage and failover coordination.
- **Change data capture** — exposes a durable change log for downstream systems, but does not by itself make multi-node writes consistent.
- **Application-level replication** — supports custom data ownership, with more protocol, monitoring, and recovery code to maintain.

## Related

- [ACID Guarantees & Transaction Isolation Levels (Read Committed, Repeatable Read, Serializable)](04-acid-isolation.md)
- [Partitioning & Sharding Strategies: Range, Hash, List, and Directory-Based Sharding](06-sharding.md)
- [Distributed Query Execution, Global Secondary Indexes, and Point-In-Time Recovery (PITR)](07-distributed-query-pitr.md)
- [Consensus Algorithms](../01-consensus/02-consensus.md)
