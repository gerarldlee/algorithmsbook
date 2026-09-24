---
title: "Delivery Guarantees"
weight: 3
toc: true
---

## What it is

Delivery guarantees describe how many times a message may be delivered and processed: **at-most-once** (0 or 1), **at-least-once** (1 or more), and **exactly-once** (precisely 1). They are the contract between a producer, a broker, and a consumer, and they determine how you must design for duplicates, retries, and idempotency.

## How it works

The guarantee is the product of acknowledgment timing and retry behavior. At-most-once fires the message and never retries: if the consumer crashes before processing, the message is lost. At-least-once acknowledges only after processing, so a crash before the ack triggers redelivery — safe against loss but permitting duplicates. Exactly-once is impossible to achieve by the broker alone across an unreliable network; it is built by combining at-least-once delivery with **idempotent consumers** (deduplicating by message ID) and, where supported, transactional writes to broker and store together (Kafka's idempotent producer + transactional API, or an outbox pattern). Ordering is a related guarantee: a queue preserves order per-queue and a stream per-partition, but a single key must map to one partition to keep its events ordered.

The guarantees mapped to their mechanisms:

```yaml
# Delivery guarantees and how they are built
at_most_once:
  ack: before processing          # or fire-and-forget
  retry: never
  loss: possible                  # message may vanish
at_least_once:
  ack: after processing
  retry: on no-ack / timeout
  duplicates: possible            # reprocess after crash
exactly_once:
  transport: at-least-once        # broker redelivers
  consumer: idempotent            # dedupe by message id / idempotency key
  storage: transactional          # write result + offset atomically
ordering:
  queue: per-queue (FIFO modes)
  stream: per-partition            # route one key to one partition
```

## Tradeoffs

| Guarantee | Strengths | Costs |
| --- | --- | --- |
| At-most-once | Lowest latency, no dedupe state | Messages can be silently lost |
| At-least-once | No message loss; simple to build | Duplicates — consumers must tolerate or dedupe |
| Exactly-once | Cleanest application semantics | Requires idempotency, transactional stores, higher latency and complexity |
| Strict ordering | Simplifies stateful consumers | Limits parallelism — a hot key serializes its partition |

## When to use

- Use at-least-once plus an idempotency key when losing a message is unacceptable (payments, orders) but an occasional retried duplicate is tolerable.
- Use exactly-once (idempotent consumer + transactional write) when a duplicate would corrupt state — e.g. incrementing a balance twice.
- Use at-most-once for lossy telemetry and metrics where a fresh sample is worth more than a stale retry.

## Alternatives

- **Idempotency keys in the consumer** — achieve exactly-once effect on top of at-least-once without broker transactions, at the cost of storing processed IDs.
- **Transactional outbox** — write the message to a database table in the same transaction as the business change, guaranteeing exactly-once publication without two-phase commit.

## Related

- [Queues vs Streams](01-queues-vs-streams.md)
- [Backpressure and Dead Letter Queues](04-backpressure-dlq.md)
- [Publish-Subscribe](02-pub-sub.md)
- [Distributed Transactions](../../04-distributed-systems/01-consensus/04-distributed-transactions.md)
