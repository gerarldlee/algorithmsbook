---
title: "Consensus Algorithms"
weight: 2
toc: true
---

## What it is

Consensus is the problem of getting a group of distributed processes to agree on a single value (or a totally ordered sequence of values) and commit to it, even as some processes crash and messages are delayed or reordered. Consensus algorithms solve this under an asynchronous, crash-failure model, providing the building blocks for replicated state machines, leader election, and distributed coordination. The canonical algorithms are **Paxos**, **Raft**, and **ZAB** (used by ZooKeeper), each built on quorum voting.

## How it works

A consensus algorithm elects a distinguished leader (proposer) and drives a replicated log: the leader appends an entry, asks a **quorum** (majority) of nodes to accept it, and commits once a majority has acknowledged. Committed entries are applied to each node's state machine in log order, so every correct replica ends up in the same state. **Paxos** separates roles (proposer, acceptor, learner) and tolerates `2f+1` nodes with `f` failures via two-phase "prepare/promise, propose/accept" rounds. **Raft** simplifies this into a single strong leader that replicates the log with matching term numbers, explicit leader election via randomized timeouts, and a safety rule that a leader only overwrites entries it has committed. **ZAB** is ZooKeeper's atomic-broadcast protocol: a leader proposes transactions, followers acknowledge, and a commit propagates after a quorum, with epochs to bound leadership changes.

The Raft lifecycle is described below:

```yaml
# Raft consensus lifecycle
nodes: 2f+1                      # tolerate f failures; quorum = f+1
election:
  trigger: leader heartbeat timeout (randomized 150-300ms)
  candidate_votes: majority required
  term: monotonically increasing epoch number
log_replication:
  leader_appends: entry(term, index, command)
  followers_ack: entry appended
  commit_when: acknowledged by quorum (majority)
  applied: in log order to state machine
safety:
  leader_only_overwrites: uncommitted entries from its own term
  election_restriction: candidate must be at least as up-to-date as quorum
membership:
  joint_consensus: two-phase config change for safe add/remove
```

## Tradeoffs

| Property | Gain | Cost |
| --- | --- | --- |
| Raft | Single strong leader makes reasoning simple and implementable | Leader is a bottleneck; election pauses availability briefly |
| Paxos | Proven safety under f failures with 2f+1 nodes; role separation | Hard to implement correctly; two-phase per value adds round-trips |
| ZAB | Atomic broadcast optimized for primary-backup ordering in ZooKeeper | Tightly coupled to ZooKeeper's leader-follower model |
| Quorum (majority) | Progress as long as a majority is reachable | Reads/writes cost multiple round-trips; minority partitions stall |
| Durability | fsync'd log survives crashes | Disk sync latency on every commit |

## When to use

- For a replicated state machine or log (leader election, config store, locks) where all nodes must agree on one ordering.
- When correctness under crash failure matters more than raw throughput — coordination systems (ZooKeeper, etcd) are the canonical use.
- When you need linearizable reads and writes and are willing to pay quorum round-trips.

## Alternatives

- **Leaderless quorum (Dynamo-style, R+W>N)** — no election, lower coordination overhead, but only eventual per-key agreement, not a global order.
- **Paxos variants (Multi-Paxos, EPaxos)** — higher throughput or multi-leader concurrency, but significantly harder to implement correctly.
- **Blockchain/BFT protocols (PBFT, Tendermint)** — tolerate Byzantine (malicious) faults, but far more messages and lower throughput than crash-fault consensus.

## Related

- [CAP and PACELC Theorems](01-cap-pacelc.md)
- [Clocks and Ordering](03-clocks-ordering.md)
- [Distributed Transactions](04-distributed-transactions.md)
- [Replication](../02-databases/05-replication.md)
