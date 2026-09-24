---
title: "Publish-Subscribe"
weight: 2
toc: true
---

## What it is

Publish-subscribe (pub/sub) is a messaging pattern where a producer publishes events to a **topic**, and every subscriber interested in that topic receives a copy — decoupling publishers from consumers entirely. Neither side knows the other exists: publishers emit to a channel, and the broker fans the message out to all current subscribers.

## How it works

A publisher sends a message to a topic rather than to a specific consumer. The broker maintains a registry of subscribers for each topic and duplicates the message to each one (fan-out). Subscription can be pull-based (subscribers poll or hold a consumer-group position, as in Kafka) or push-based (the broker delivers to a registered endpoint or socket). Kafka achieves fan-out through independent consumer groups — every group gets a full copy of the topic, while members within a group split the partitions. RabbitMQ implements pub/sub with a **fanout** or **topic** exchange that routes to bound queues. Redis Pub/Sub is the simplest form: a fire-and-forget broadcast to any client currently subscribed, with no persistence or replay.

A comparison of the common engines:

```yaml
# Pub/sub engines compared
kafka:
  model: partitioned log + consumer groups
  fan_out: one full copy per group
  persistence: durable, replayable
  ordering: per partition
rabbitmq:
  model: exchange routes to bound queues
  fan_out: fanout exchange to every queue; topic exchange by routing key
  persistence: messages durable on disk until acked
  ordering: best-effort per queue
redis_pubsub:
  model: channel broadcast to connected clients
  fan_out: to all current subscribers
  persistence: none — missed messages are lost
  ordering: none across missed connections
```

## Tradeoffs

| Engine | Strengths | Costs |
| --- | --- | --- |
| Kafka | Durable, replayable, high throughput, many groups | Operational weight; consumers must manage offsets and lag |
| RabbitMQ | Flexible routing (topic/fanout/headers), mature ack model | Lower throughput than a log; no replay once consumed |
| Redis Pub/Sub | Minimal latency, trivial to operate | No persistence, no replay, drops messages for disconnected clients |
| Push (webhooks/websockets) | Near-real-time delivery, simple consumer | Backpressure and retry burden shifts to the publisher |

## When to use

- Use pub/sub to broadcast an event to many independent services — e.g. an "order placed" event consumed by inventory, email, and analytics.
- Use Kafka-style fan-out when every subscriber must see every event and be able to replay history independently.
- Use Redis Pub/Sub for ephemeral, in-memory fan-out where losing a message to a briefly disconnected client is acceptable (live notifications, presence updates).

## Alternatives

- **Point-to-point queue** — a message goes to exactly one consumer, which is simpler but cannot broadcast to many services at once.
- **Database polling** — consumers read new rows from a table, avoiding a broker entirely, but adds latency, load, and no native fan-out or ordering.

## Related

- [Queues vs Streams](01-queues-vs-streams.md)
- [Delivery Guarantees](03-delivery-guarantees.md)
- [Realtime Protocols](../02-realtime/02-realtime-protocols.md)
- [System Design Fundamentals](../../02-system-design/01-system-design-fundamentals/01-fundamentals.md)
