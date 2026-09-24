---
title: "Distributed Transactions"
weight: 4
toc: true
---

## What it is

A distributed transaction is a unit of work that spans multiple independent resources — several databases, a database plus a message queue, or services on different machines — and must either commit atomically on all of them or roll back on all of them. The classic atomic-commit protocols are **two-phase commit (2PC)** and **three-phase commit (3PC)**, coordinated via the **XA** standard. Because blocking atomicity is expensive and fragile, modern systems often prefer compensation-based **Sagas** with the **outbox pattern** for reliable messaging, plus **idempotency** to make retries safe.

## How it works

**2PC** elects a coordinator: phase 1 asks every participant to *prepare* (persist the changes and reply "ready"), and phase 2 tells everyone to *commit* once all are ready, or *abort* if any fails. It is atomic but blocks if the coordinator dies between phases (a participant holding locks must wait). **3PC** adds a pre-commit phase to reduce that blocking window, but at the cost of extra round-trips and no safety guarantee against network partitions. **XA** is the standard interface exposing 2PC to databases and message brokers. A **Saga** instead breaks the work into a sequence of local transactions, each with a compensating action, so a failure triggers the compensations of already-committed steps rather than a rollback. The **outbox pattern** writes the business change and the outbound event in the *same* local transaction to an outbox table, then a relay publishes it — guaranteeing "change made iff message sent". **Idempotency** (idempotency keys, deduplication) makes retries and redeliveries safe to repeat.

The patterns are described below:

```yaml
# Distributed transaction toolbox
two_phase_commit:
  phases: [prepare, commit]
  guarantee: atomic across participants
  failure: blocks if coordinator dies after prepare (in-doubt transaction)
three_phase_commit:
  phases: [can_commit, pre_commit, do_commit]
  gain: narrower blocking window
  cost: extra round-trip; no safety under network partition
xa:
  role: standard 2PC interface (databases, brokers)
saga:
  model: sequence of local transactions + compensating actions
  guarantee: eventual consistency, no distributed locks
  styles: [choreography, orchestration]
outbox_pattern:
  steps: [write change + event in one local tx, relay publishes event]
  guarantee: at-least-once delivery, change and event atomic
idempotency:
  mechanism: idempotency key, dedup on receiver
  purpose: make retries/redeliveries safe
```

## Tradeoffs

| Pattern | Gain | Cost |
| --- | --- | --- |
| 2PC / XA | Strong atomicity across resources; simple mental model | Blocking on coordinator failure; poor availability; slow under contention |
| 3PC | Smaller blocking window than 2PC | Extra round-trips; still unsafe under partitions; rarely used in practice |
| Saga | High availability, no long-held distributed locks | Eventual consistency; requires compensating actions for every step |
| Outbox pattern | Reliable, atomic change-plus-event publication | Needs a relay/poller and at-least-once delivery handling |
| Idempotency | Safe retries and exactly-once *effect* | Requires keys and dedup storage on every receiver |

## When to use

- Use 2PC/XA when strong atomicity across a few tightly-coupled databases is truly required (e.g. a bank transfer spanning two ledgers) and failure is rare.
- Use Sagas for long-running business processes across microservices where locks and blocking are unacceptable.
- Use the outbox pattern whenever a local write must reliably publish an event to a queue or broker, to avoid dual-write problems.

## Alternatives

- **Local transaction + eventual reconciliation** — simplest and highly available, but the application must detect and repair inconsistency on its own.
- **2PC/XA via database** — strong guarantees, but blocks and lowers availability, so only for small, low-failure scope.
- **Transactional outbox + message relay (Debezium/change-data-capture)** — reliable publication without the app polling, but adds infrastructure and latency.

## Related

- [Consensus Algorithms](02-consensus.md)
- [Clocks and Ordering](03-clocks-ordering.md)
- [ACID and Isolation Levels](../02-databases/04-acid-isolation.md)
- [Replication](../02-databases/05-replication.md)
- [Delivery Guarantees](../../03-messaging/01-messaging/03-delivery-guarantees.md)
