---
title: "Clocks and Ordering"
weight: 3
toc: true
---

## What it is

Clocks and ordering cover the mechanisms a distributed system uses to establish a shared notion of time and causality when every machine has its own clock and messages take unknown time. **Wall clocks** (synchronized by NTP) give an approximate physical timestamp; **logical clocks** (Lamport and vector clocks) capture the causal *happens-before* relationship between events without physical time. Ordering also includes the consistency guarantees that build on these clocks: **linearizability** (a single real-time order) and **serializability** (an order equivalent to some sequential execution).

## How it works

**NTP** periodically adjusts each host's clock against reference servers, so wall clocks are roughly synchronized but never exact — clock skew and leap-second jumps remain, making physical time unreliable for ordering. A **Lamport clock** assigns each event a counter: on a local event increment `C`, and on receiving a message set `C = max(local, incoming) + 1`, so that if `a` happens before `b` then `LC(a) < LC(b)`; the converse does not hold (concurrent events can share order). A **vector clock** keeps a per-node counter vector, incrementing its own entry on each event and merging on receive; it can detect concurrency exactly — two events are concurrent iff neither vector dominates the other. **Linearizability** requires operations to appear atomic at some point between their real-time invocation and response, giving a single global order; **serializability** only requires equivalence to *some* sequential order (no real-time constraint), which is what databases enforce with transactions and isolation levels.

The ordering primitives are described below:

```yaml
# Clocks and ordering primitives
wall_clock:
  sync: NTP  # hierarchical stratum, periodic, offset+drift adjusted
  limits: [clock_skew, leap_seconds, clock_jumps]   # unreliable for ordering
lamport_clock:
  rule: C = max(C_local, C_incoming) + 1
  guarantee: a -> b  =>  LC(a) < LC(b)   # one-way, cannot detect concurrency
vector_clock:
  state: [c1, c2, ..., cn]   # per-node counters, merged on receive
  guarantee: a -> b <=> VC(a) < VC(b)   # exact concurrency detection
linearizability:
  meaning: single global order matching real-time  # strongest
  use: consensus, locks, single-key compare-and-set
serializability:
  meaning: equivalent to some sequential order      # weaker than linearizability
  use: ACID transactions across multiple keys
```

## Tradeoffs

| Property | Gain | Cost |
| --- | --- | --- |
| Wall clock (NTP) | Human-meaningful timestamps, TTLs, and expiry logic | Skew and jumps make it unsafe for ordering decisions |
| Lamport clock | Tiny overhead (one integer) and preserves causality direction | Cannot detect concurrent events; total order needs tie-breaking |
| Vector clock | Exact causality and concurrency detection | Grows O(n) with the number of nodes; merge complexity |
| Linearizability | Simplest mental model — one global order | Requires coordination/consensus, limiting availability and throughput |
| Serializability | Strong isolation across many objects via transactions | Weaker than linearizability; can add locking and abort overhead |

## When to use

- Use vector clocks when merging concurrent writes (multi-datacenter stores, CRDT conflict detection) and you need to know *which* events are concurrent.
- Use Lamport clocks when a cheap total order of events suffices and you can break ties by node ID.
- Choose linearizability for single-key invariants (locks, leader election, counters) and serializability for multi-key transactions.

## Alternatives

- **Hybrid Logical Clocks (HLC)** — combine wall time with a logical counter to get real-time-like timestamps plus causality, but more complex to reason about than pure Lamport clocks.
- **TrueTime / synchronized hardware (Google Spanner)** — bounds clock uncertainty with GPS+atomic clocks for external consistency, but requires specialized infrastructure.
- **Event sourcing / sequence numbers from a single log** — a totally ordered append-only log gives ordering for free, but becomes a central bottleneck.

## Related

- [Consensus Algorithms](02-consensus.md)
- [Distributed Transactions](04-distributed-transactions.md)
- [CAP and PACELC Theorems](01-cap-pacelc.md)
- [ACID and Isolation Levels](../02-databases/04-acid-isolation.md)
