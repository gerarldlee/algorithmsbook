---
title: "Clocks & Ordering: Physical Clocks, NTP, Logical Clocks (Lamport), and Vector Clocks"
weight: 3
toc: true
---

## What it is

Clocks and ordering mechanisms let a distributed system distinguish causal order from concurrent events when machines have independent physical clocks and messages arrive after unknown delays. **Physical clocks** provide approximate real-world time, commonly coordinated with NTP, while **logical clocks** record the **happens-before** relation without depending on synchronized hardware. The relation means that one process's events are ordered locally, or that a message send precedes its matching receive. **Linearizability** places each operation between its invocation and response in one real-time order, while **serializability** only requires an equivalent sequential order.

## How it works

NTP periodically estimates clock offset and drift between hosts. The resulting timestamps are useful for human-readable events, time-to-live values, and approximate expiry, but network delay, clock drift, adjustments, and uncertain synchronization mean a physical timestamp alone cannot establish causality. Applications that need ordering use a protocol bound, a logical clock, or a consensus log instead of comparing raw wall-clock values.

A **Lamport clock** stores one counter per process. A process increments its counter for a local event. When it receives an event with counter `C_remote`, it sets its counter to `max(C_local, C_remote) + 1`. If event `a` happens before event `b`, then `LC(a) < LC(b)`; the reverse implication is false. Two concurrent events can have equal counters or counters ordered only by an application tie-breaker, so Lamport clocks preserve causality but do not identify concurrency by themselves.

A **vector clock** stores one counter per known process. A process increments its own component on a local event and merges a received vector component-wise with `max` on receipt. With complete clock knowledge, `a` happens before `b` when every component of `VC(a)` is less than or equal to the corresponding component of `VC(b)` and the vectors are not equal. Events are concurrent when neither vector dominates the other component-wise. The metadata grows with the number of processes, and a partial vector clock cannot prove causality for omitted processes. Linearizability applies a real-time order to individual operations, while serializability orders transactions without requiring that non-overlapping transactions follow wall-clock time; strict serializability adds that real-time constraint.

```yaml
physical_clock:
  time_source: NTP
  sync: estimate offset and drift between hosts
  guarantees: approximate human time; not a causal order
lamport_clock:
  state: one integer counter
  local_event: increment the local counter
  receive: set counter to max(local, remote) + 1
  guarantee: happens-before implies a smaller timestamp
  limitation: concurrency requires additional detection or tie-breaking
vector_clock:
  state: one counter per known process
  local_event: increment the local process component
  receive: merge component-wise with max
  causality: a happens-before b when VC(a) is component-wise less than or equal to VC(b) and the vectors differ
  concurrency: neither vector strictly dominates the other
linearizability:
  order: one order consistent with non-overlapping real-time invocations and responses
serializability:
  order: equivalent to a sequential execution
  strict_serializability: also preserves real-time precedence of non-overlapping transactions
```

## Tradeoffs

| Property | Gain | Cost |
| --- | --- | --- |
| Physical clock with NTP | Human-meaningful timestamps and simple expiry logic | Offset, drift, and adjustment uncertainty make raw timestamps unsafe for ordering |
| Lamport clock | One counter per event and a compact causal timestamp | A strict timestamp order does not prove causality; concurrency needs another mechanism |
| Vector clock | Distinguishes causality from concurrency when all relevant processes are represented | Metadata grows with the number of processes; partial clocks weaken the result |
| Linearizability | Gives a simple real-time order for locks, counters, and single-key operations | Requires coordination and can reduce availability or throughput during failures |
| Serializability | Preserves multi-object invariants for a transaction | Adds validation, locking, or aborts and is not automatically linearizable |

## When to use

- You need approximate timestamps for human-facing events or TTLs and can tolerate clock uncertainty.
- You need to order events that already have a causal relationship and a tie-breaker is sufficient.
- You need to detect concurrent writes across processes and can carry metadata proportional to the known process set.
- You need a real-time order for individual operations, or a transaction order for multi-object invariants.

## Alternatives

- **Hybrid Logical Clocks (HLC)** — combine physical time with a logical counter to preserve causality while keeping timestamps close to real time, but require more state and careful merge rules.
- **TrueTime and bounded-clock APIs (Google Spanner)** — expose an uncertainty interval and support external consistency without exposing physical time as a perfect clock, but require specialized infrastructure.
- **A single consensus log with sequence numbers** — provides one total order for every subscriber, but makes the log service a coordination dependency and a potential throughput bottleneck.

## Related

- [Consensus Protocols: Paxos, Raft, Multi-Paxos, and Distributed Locks (Chubby, Redlock)](02-consensus.md)
- [Distributed Transactions](04-distributed-transactions.md)
- [The CAP Theorem, PACELC, and Architectural Trade-offs](01-cap-pacelc.md)
- [ACID and Isolation Levels](../02-databases/04-acid-isolation.md)
- [Distributed Presence Engines](../../03-messaging/02-realtime/03-presence-engines.md)
