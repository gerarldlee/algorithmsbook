---
title: "Publish-Subscribe (Pub/Sub) Architecture Mechanics & Fan-Out Design Patterns"
weight: 2
toc: true
---

## What it is

Publish-subscribe is a messaging pattern in which a producer publishes an event to a named channel and each eligible subscription receives its own copy. The broker, not the producer, maintains subscriptions and performs fan-out, so publishers do not need to know the addresses or processing logic of consumers. A subscription is the durable routing target when the broker supports it; a live client connection is only one possible subscription.

## How it works

A publisher sends an event with a topic or exchange name. The broker matches that name against subscriptions, creates a delivery or record for each matching subscription, and records whether the subscription is live, queued, or replayable. Consumers then process their copies independently. This is **fan-out**: one publication becomes multiple deliveries. Fan-out does not mean that every consumer receives every message; routing keys, partitions, filters, and consumer-group membership determine the eligible destinations.

RabbitMQ implements subscriptions as durable queues bound to exchanges. A fanout exchange copies a message to every bound queue, while a topic exchange selects queues by a routing-key pattern. Kafka implements group fan-out with consumer groups: every group reads the topic, but each record is assigned to one member within a group, and the group commits its own offset. Redis Pub/Sub broadcasts to currently connected subscribers and does not retain messages for later delivery. A webhook uses HTTP push instead of a broker subscription, so retries, endpoint availability, and backpressure become the sender's responsibility.

This broker-neutral topology shows two durable subscriptions receiving the same `order.placed` routing key through a topic exchange. It is a declarative manifest, not a single RabbitMQ Management API request; a deployment system would create the exchange, queues, and bindings with separate API calls:

```json
[
  {
    "exchange": "order.events",
    "type": "topic",
    "durable": true
  },
  {
    "queue": "inventory.order-events",
    "durable": true
  },
  {
    "queue": "notifications.order-events",
    "durable": true
  },
  {
    "binding": "order.events",
    "destination": "inventory.order-events",
    "routing_key": "order.placed"
  },
  {
    "binding": "order.events",
    "destination": "notifications.order-events",
    "routing_key": "order.placed"
  }
]
```

The common fan-out designs differ in where the independent copies live:

| Design | Routing rule | Failure behavior |
| --- | --- | --- |
| Fanout exchange | Every bound queue receives a copy | A queue's retry and acknowledgment policy is independent |
| Topic exchange | Each subscription selects a routing-key pattern | A missed binding is a routing error, not a delivery guarantee |
| Kafka consumer groups | Every group reads the topic; one member per group handles each partition | A group can replay its retained records by changing its offset |
| Redis Pub/Sub | Every currently connected subscriber receives the channel message | Disconnected subscribers miss messages; there is no durable backlog |
| Webhook fan-out | The provider posts to registered HTTPS endpoints | The provider owns retry and delivery status; the endpoint owns idempotency |

## Tradeoffs

| Engine or pattern | Gain | Cost |
| --- | --- | --- |
| RabbitMQ exchanges | Rich routing, acknowledgments, priorities, and dead-letter policies | The application must design queue topology and retry behavior |
| Kafka consumer groups | Durable history, replay, and independent downstream progress | Groups can lag, and every group adds network and storage cost |
| Redis Pub/Sub | Very simple, low-latency live broadcast | No persistence, replay, or recovery for disconnected subscribers |
| Webhooks | Integrates with ordinary HTTP endpoints and external systems | The provider and consumer must coordinate retries, signatures, and overload behavior |

## When to use

- One domain event must trigger independent reactions in inventory, billing, notifications, and analytics.
- Subscribers need different routing rules or independent processing progress.
- A live broadcast is sufficient and losing messages to disconnected clients is acceptable.
- You need durable replay for new consumers, audits, or state reconstruction.

## Alternatives

- **Point-to-point queue** — is simpler when only one worker should handle each work item, but it cannot provide independent copies to several consumers.
- **Database polling** — avoids a broker and makes records queryable, but adds polling load, schema coupling, and usually more latency.
- **Change-data capture** — propagates committed database changes to downstream systems, but the event contract follows the storage schema unless it is transformed.
- **HTTP webhooks** — push events to external endpoints, but require endpoint security, retry handling, and duplicate protection.

## Related

- [Queues vs Streams](01-queues-vs-streams.md)
- [Delivery Guarantees](03-delivery-guarantees.md)
- [Realtime Protocols](../02-realtime/02-realtime-protocols.md)
- [API Paradigms: REST, GraphQL, gRPC Protocol Buffers, and Event-Driven Systems](../../02-system-design/01-system-design-fundamentals/05-api-paradigms.md)
