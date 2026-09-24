---
title: "Queues vs Streams"
weight: 1
toc: true
---

## What it is

Queues and streams are the two fundamental message-delivery models. A **queue** (RabbitMQ, Amazon SQS) is a shared, transient buffer where a message is consumed once and then deleted, giving you load leveling and competing-consumer distribution. A **stream** (Apache Kafka, Amazon Kinesis) is an append-only, durable, replayable log of records that consumers read by offset, so many consumers can read the same history independently.

## How it works

A queue delivers a message to exactly one of a pool of competing consumers; on acknowledgment the broker removes it, so unacknowledged or failed messages are retried. The queue is a shared pointer — once a message is gone, it cannot be read again. A stream is instead an immutable log partitioned into topics; each consumer group tracks its own offset and reads forward, so the broker never removes data after delivery. Because offsets are per-consumer, a stream supports replay (rewind and reprocess), fan-out to many independent readers, and retention of history for auditing or backfilling.

A side-by-side of the two models:

```yaml
# Queue vs stream model
queue:                    # RabbitMQ, SQS
  delivery: once-per-message   # consumed then deleted
  consumers: competing        # one consumer per message
  order: per-queue (mostly)    # FIFO best-effort
  replay: no                   # gone after ack
  retention: until consumed    # no history
  scaling: more workers share load
stream:                   # Kafka, Kinesis
  delivery: offset-based       # many readers per record
  consumers: independent groups
  order: per-partition         # strict within a key
  replay: yes                   # rewind to any offset
  retention: time/size based    # durable history
  scaling: partitions parallelize reads/writes
```

## Tradeoffs

| Dimension | Queue | Stream |
| --- | --- | --- |
| Consumption | One consumer per message (competing) | Many independent consumer groups read all records |
| Replay | Not possible after ack | Native — rewind offsets and reprocess |
| Retention | Until consumed | Configurable (days/weeks), enabling audit and backfill |
| Ordering | Best-effort per queue; strict only with FIFO/SQS | Strict per partition, not globally across partitions |
| Load leveling | Natural — workers pull at their own pace | Requires tracking consumer lag yourself |
| Broker storage | Small; data leaves after delivery | Large; the log itself is the source of truth |
| Operational model | Broker routes and deletes (smart broker) | Dumb log; consumers keep their own state |

## When to use

- Use a queue to smooth traffic spikes and let a pool of workers consume tasks at their own pace (job processing, image resizing, email sending).
- Use a stream when you need the same events read by many independent services, event sourcing, or the ability to replay history after a bug or schema change.
- Use a stream as the backbone for a system where the log of events is itself durable data (audit, analytics, change data capture).

## Alternatives

- **Amazon SQS** — a fully managed queue with simple at-least-once semantics and no broker to run, but no replay and limited ordering (unless FIFO queues).
- **Amazon Kinesis** — a managed stream for ordered, replayable records, but you pay per-shard and manage retention explicitly.
- **Redis Streams** — lightweight log with consumer groups and replay inside a datastore you already run, but retention is memory-bound and not a standalone messaging system.

## Related

- [Publish-Subscribe](02-pub-sub.md)
- [Delivery Guarantees](03-delivery-guarantees.md)
- [Backpressure and Dead Letter Queues](04-backpressure-dlq.md)
- [Notification Dispatchers](../02-realtime/01-notification-dispatchers.md)
- [Caching Strategies](../../02-system-design/02-caching/01-in-memory-caching.md)
