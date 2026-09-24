---
title: "CAP and PACELC Theorems"
weight: 1
toc: true
---

## What it is

The CAP theorem states that a distributed data store can guarantee at most two of three properties at once: **Consistency** (every read sees the latest write), **Availability** (every request receives a non-error response, even during failures), and **Partition tolerance** (the system keeps working despite messages being dropped or delayed between nodes). Since network partitions are unavoidable in practice, every real system must tolerate partitions and therefore must choose between consistency and availability when a partition occurs. PACELC refines CAP: if there is a **P**artition, choose between **A**vailability and **C**onsistency; **E**lse (during normal operation), choose between **L**atency and **C**onsistency.

## How it works

During a partition, the nodes of a replicated store cannot communicate to agree on the current state. A **CP** system chooses consistency, refusing or erroring writes on the minority side so no divergent copy can serve stale data; a **AP** system chooses availability, accepting writes on any reachable node and reconciling later. Because partitions are rare relative to normal operation, PACELC points out that the more common decision is the "else" branch: even with no partition, a system must decide whether each read waits for all replicas to agree (consistent but slow) or returns a fast, possibly stale answer (low latency). The theorem frames a spectrum, not a binary — many systems offer tunable consistency per operation.

The choice surface is described below:

```yaml
# CAP / PACELC decision surface for one replicated store
partition_behavior:          # the "PA" or "PC" branch, chosen once per system
  choice: CP                 # or AP
  cp: rejects minority writes/reads during partition (e.g. ZooKeeper, HBase)
  ap: accepts any-reachable-node writes, reconciles later (e.g. DynamoDB, Cassandra)
normal_operation_behavior:   # the "EL" branch, usually tunable per read/write
  choice: EC                 # or EL (consistency vs latency)
  ec: strong consistency — read waits for quorum agreement, higher latency
  el: low latency — read any replica, may return stale data
tuning:
  quorum: [R + W > N for strong consistency, else eventual]
  examples:
    - DynamoDB:  AP with per-item tunable consistency (strong vs eventual)
    - Cassandra: AP with per-query consistency levels (ONE, QUORUM, ALL)
    - PostgreSQL: CP/EC (single-node strong consistency, no partition survival)
```

## Tradeoffs

| Property | Gain | Cost |
| --- | --- | --- |
| Consistency (C) | Every client observes the same, latest state; reasoning is simple | Slower reads/writes; reduced or zero availability during partitions |
| Availability (A) | The system answers even when the network is partitioned | Reads may return stale data; requires conflict resolution (CRDTs, LWW, version vectors) |
| Partition tolerance (P) | System survives node/network failures | Forces the C-vs-A (and E-vs-L) choice; adds replication and reconciliation machinery |
| Low latency (PACELC "E") | Fast reads/writes; better user experience and throughput | Eventual consistency; stale reads and read-your-writes anomalies |
| Strong consistency (PACELC "C") | No anomalies; linearizable behavior | Higher tail latency; quorum round-trips on every operation |

## When to use

- When choosing a database, decide the CP/AP posture first: payment ledgers and coordination (locks, leader election) need CP, while shopping carts and social feeds tolerate AP for availability and low latency.
- When documenting why a system accepts stale reads or refuses writes under failure, to make the trade-off explicit for reviewers.
- When an existing store offers tunable consistency, to pick the right per-query level (e.g. QUORUM for correctness-critical paths, ONE for hot reads).

## Alternatives

- **Strongly consistent single-node store (PostgreSQL)** — simplest model, no partition survival, but becomes a single point of failure under network issues.
- **Quorum-based tunable store (Cassandra/DynamoDB)** — lets each operation choose consistency vs latency, but pushes conflict handling onto the application.
- **CRDT / conflict-free replicated data types** — always available and merge-safe, but restricted to commutative data types and eventually-consistent reads.

## Related

- [Consensus Algorithms](02-consensus.md)
- [Clocks and Ordering](03-clocks-ordering.md)
- [Distributed Transactions](04-distributed-transactions.md)
- [Replication](../02-databases/05-replication.md)
- [ACID and Isolation Levels](../02-databases/04-acid-isolation.md)
