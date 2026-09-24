---
title: "Distributed Transactions: Two-Phase Commit (2PC), Three-Phase Commit (3PC), and the Saga Pattern"
weight: 4
toc: true
---

## What it is

A distributed transaction coordinates work across independent databases, queues, or services. **Two-phase commit (2PC)** and **three-phase commit (3PC)** are atomic-commit protocols in which a coordinator drives participant decisions; **XA** is a standard interface for connecting transactional resource managers to such a coordinator. A **Saga** takes a different approach: it splits work into local transactions and defines compensating actions for completed steps, so it avoids one atomic commit across independent services but does not provide a single all-or-nothing boundary.

## How it works

For 2PC, the coordinator first asks each participant to **prepare**. A participant validates and durably records the transaction, votes yes or no, and retains enough state to obey the coordinator's final decision. After collecting the votes, the coordinator durably records `commit` if all participants vote yes and `abort` otherwise, then sends that decision to every participant. A participant cannot unilaterally abort after a yes vote if the global decision is commit; if the coordinator fails before participants learn the decision, recovery must discover the durable decision, otherwise the participant remains **in-doubt** and may hold locks while waiting.

3PC inserts a pre-commit state between voting and commit. Under its bounded-delay network assumption, participants can use the pre-commit state to reduce the blocking window, but a network partition can still leave a participant unable to distinguish a committed transaction from one that should be blocked. 3PC is therefore not a general partition-safe replacement for 2PC. XA standardizes the coordinator/resource interface but inherits 2PC's blocking and recovery costs.

A Saga executes a sequence of local transactions. In an orchestrated Saga, a coordinator sends commands and records progress; in a choreography, services react to events. If a later step fails, compensating actions run for completed steps, usually in reverse order. Compensation cannot erase an external side effect, so business operations must define an actual reversal, such as refunding a payment or releasing a reservation. The **outbox pattern** writes the business change and an event record in one local transaction; a relay publishes that record, giving at-least-once delivery without losing the event when the local transaction commits. Consumers use **idempotency keys** or deduplication records so retries do not apply an effect twice.

```yaml
two_phase_commit:
  phase_1: [coordinator asks, participant validates and durably prepares, participant votes]
  phase_2: [coordinator records commit or abort, participants obey the decision]
  recovery: [new coordinator reads durable decision, resolves in-doubt participants]
  cost: prepared participants can block when the decision is unavailable
three_phase_commit:
  phases: [can_commit, pre_commit, do_commit]
  benefit: can reduce blocking under a synchrony assumption
  partition_limit: timing assumptions do not provide general partition safety
xa:
  role: standard interface between a coordinator and transactional resource managers
saga:
  unit: local transaction with a compensating action
  styles: [choreography, orchestration]
  failure: run compensations for completed steps
  limit: compensation cannot undo an irreversible external effect
outbox_pattern:
  local_transaction: [business change, event record]
  relay: publish committed outbox records
  delivery: at least once
idempotency:
  receiver: [accept an operation key, persist its result, return the result for duplicates]
```

## Tradeoffs

| Pattern | Gain | Cost |
| --- | --- | --- |
| 2PC / XA | Strong atomic commit across resources with a single decision | Coordinator recovery, in-doubt transactions, blocking, and lower availability |
| 3PC | Can reduce the blocking window under bounded network delay | Extra round trips and a synchrony assumption that partitions violate |
| Saga | Keeps each step local and avoids long-held distributed locks | Eventual business completion, compensation design, and recovery of partially completed work |
| Transactional outbox | Makes the business change and event record atomic in one local database transaction | A relay, at-least-once delivery, duplicate handling, and publication delay |
| Idempotency | Makes retries and redeliveries safe to repeat | Persistent keys, deduplication storage, and a defined retention policy |

## When to use

- You need atomic commit across a small set of resources that already participate in XA and can tolerate 2PC's blocking and recovery model.
- You need a long-running business workflow across services where holding distributed locks is unacceptable and every completed step has a meaningful compensation.
- You need a reliable database-to-broker change and can run a relay plus idempotent consumers.
- You need a protocol description or state machine that makes prepare, commit, abort, and in-doubt recovery explicit.

## Alternatives

- **Local transactions plus reconciliation** — maximizes availability and keeps services independent, but the application must detect and repair cross-resource inconsistency.
- **Try-confirm/cancel** — gives each service explicit preparation, confirmation, and cancellation operations, but requires business-specific coordination and does not remove partial failure handling.
- **Change-data capture (Debezium)** — publishes database changes from the transaction log and avoids application polling, but adds infrastructure, schema-change handling, and delivery latency.

## Related

- [Consensus Protocols: Paxos, Raft, Multi-Paxos, and Distributed Locks (Chubby, Redlock)](02-consensus.md)
- [Clocks & Ordering](03-clocks-ordering.md)
- [ACID and Isolation Levels](../02-databases/04-acid-isolation.md)
- [Replication](../02-databases/05-replication.md)
- [Message Delivery Guarantees](../../03-messaging/01-messaging/03-delivery-guarantees.md)
