---
title: "Domain-Driven Design & Event Architectures: DDD Bounded Contexts, CQRS, Event Sourcing, and Transactional Outbox Pattern"
weight: 2
toc: true
---

## What it is

Domain-driven design (DDD) models a business around the language and rules of its domain. A **bounded context** is a boundary inside which a model has one meaning; **CQRS** separates commands that change state from queries that read it; **event sourcing** stores domain events as the authoritative history; and the **transactional outbox** makes a database change and an event-publication intent commit together.

## How it works

A bounded context is not merely a folder. It contains a model, language, invariants, and an owner. For example, `OrderPlaced` can mean one thing to the sales context and another to fulfillment. A shared `Order` model across both contexts makes every team negotiate every change. Contexts can use a published language or an anti-corruption layer when they must translate between models.

DDD identifies domain concepts and relationships, then separates them from application orchestration and infrastructure. A domain service contains business behavior that does not belong naturally to one entity. An application service coordinates a use case and transaction, while an adapter connects the model to HTTP, a database, or a broker. This keeps the business rules understandable and testable without coupling them to a framework.

```text
Sales context
  Customer, Quote, OrderPlaced
  invariant: an order cannot exceed the customer's credit limit

Fulfillment context
  Shipment, Carrier, DeliveryAttempt
  event consumed: OrderAccepted
  invariant: one shipment can have one active delivery attempt
```

**CQRS** gives a write model and one or more read models different shapes. A command such as `PlaceOrder` validates the current state and appends or updates the write model. A query such as `GetOrderSummary` reads a projection optimized for the screen. The projection can be built synchronously for a small system or asynchronously from events for a larger one. The cost is temporary inconsistency, projection monitoring, and a contract for rebuilding reads.

Event sourcing stores events such as `OrderCreated`, `PaymentAuthorized`, and `OrderShipped` instead of treating the current row as the only source of truth. A stream for an aggregate is replayed to rebuild its current state. Events are facts in the past tense, so they should be immutable. A snapshot can shorten a long replay, but it is an optimization rather than the source of truth. Event sourcing helps when audit history, temporal queries, or replay are valuable; it makes schema evolution and event correction more demanding.

The transactional outbox solves a dual-write problem. A service cannot usually make a database commit and a Kafka publish one atomic operation. Instead, it writes the business change and an outbox row in the same local transaction. A relay reads committed outbox rows and publishes them, recording progress. Publication is normally at-least-once, so consumers deduplicate by event ID or use an idempotent operation key.

```sql
begin;

insert into orders (id, customer_id, status)
values ('order-123', 'customer-9', 'placed');

insert into outbox_events (event_id, aggregate_id, event_type, payload)
values ('event-456', 'order-123', 'order.placed.v1', $1);

commit;
```

A consumer can apply the event and insert its event ID into a `processed_events` table in one transaction. A unique constraint on the event ID makes a redelivery a no-op. This design separates the fact that the business change committed from the fact that a broker accepted the resulting message; monitoring must expose the relay's lag and failed events.

CQRS and event sourcing are independent choices. A system can use CQRS with ordinary tables, event sourcing without separate read projections, or both. The transactional outbox is useful whenever a reliable database change must eventually notify another component.

## Tradeoffs

| Pattern | Gain | Cost or limitation |
| --- | --- | --- |
| Bounded context | Keeps a model and its language coherent | Requires domain discovery and explicit integration translations |
| Modular monolith boundary | Preserves local transactions while allowing future extraction | Boundary violations can accumulate inside one deployment |
| CQRS | Optimizes commands and queries independently | Adds projection lag, rebuild logic, and monitoring |
| Event sourcing | Preserves an auditable history and supports temporal reconstruction | Event evolution, replay performance, and correction policies |
| Transactional outbox | Removes the business-write versus publish race | Adds an outbox table, relay, publication delay, and duplicate handling |

## When to use

- Different parts of the business use conflicting models or change under different owners, which points to bounded contexts.
- A write model is optimized for invariants while a read model needs a different shape, which points to CQRS.
- You need an auditable history, replay, or historical state reconstruction, which points to event sourcing.
- A committed database change must reliably trigger a downstream event, which points to the transactional outbox.

## Alternatives

- **Shared models and direct service calls** — reduce initial ceremony, but couple teams and make schema changes harder as the organization grows.
- **Database polling for changes** — avoids a separate outbox table, but can miss or duplicate intent unless the polling and checkpoints are carefully designed.
- **Two-phase commit** — coordinates a database and broker when both support it, but introduces blocking, recovery, and availability costs.
- **CRUD-only services** — are simpler for straightforward workflows, but provide less explicit audit history and temporal behavior.

## Related

- [Enterprise Architecture Patterns: Monoliths, Microservices, Service Mesh, BFF, Strangler Fig, and Cell-Based Architecture](01-enterprise-architecture-patterns.md)
- [Resilience & Fault Tolerance Patterns: Circuit Breakers, Bulkheads, Backoff, Retries, and Timeout Budgets](03-resilience-fault-tolerance.md)
- [API Paradigms: REST, GraphQL, gRPC Protocol Buffers, Event-Driven Systems, tRPC, and OpenAPI/AsyncAPI](../01-system-design-fundamentals/05-api-paradigms.md)
- [Distributed Transactions: Two-Phase Commit, Three-Phase Commit, and the Saga Pattern](../../04-distributed-systems/01-consensus/04-distributed-transactions.md)
- [Message Queues vs Event Streams (RabbitMQ, Apache Kafka, Apache Pulsar)](../../03-messaging/01-messaging/01-queues-vs-streams.md)
