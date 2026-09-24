---
title: "Message Delivery Guarantees: At-Most-Once, At-Least-Once, and Exactly-Once (Idempotency Patterns)"
weight: 3
toc: true
---

## What it is

Message delivery guarantees describe the number of delivery attempts a system makes under failure. **At-most-once** delivery may deliver a message zero or one time, **at-least-once** delivery delivers it one or more times, and **exactly-once** delivery defines one processing effect within an explicitly bounded system boundary. Delivery is not the same as a business effect: a broker can deliver a message once while a handler sends an email twice, or redeliver a message after a handler completed its database write.

## How it works

At-most-once delivery sends a message and does not retry after an uncertain failure. A fire-and-forget producer can lose a message, and a consumer that acknowledges before processing can also lose work. At-least-once delivery acknowledges only after the handler completes. A crash between the side effect and acknowledgment causes redelivery, so the handler must tolerate duplicates or deduplicate them.

Exactly-once processing is a scoped property. Kafka can use idempotent producers, consumer isolation, and transactions to make a Kafka-to-Kafka read-process-write operation atomic. A database and a broker cannot become exactly once merely because both support transactions; the boundary, failure recovery, and external side effects must be included. The common application pattern is an **inbox**: insert the event ID and apply the business change in one database transaction, then acknowledge the broker. The event ID is protected by a unique constraint, so a redelivery becomes a no-op.

The guarantee and its recovery point can be expressed as an operational policy:

```yaml
at_most_once:
  acknowledgment: before_processing
  retry: none
  failure: loss_is_accepted
at_least_once:
  acknowledgment: after_transaction_commit
  retry: on_timeout_or_negative_acknowledgment
  failure: duplicate_handling_required
exactly_once:
  scope: all_effects_in_one_transactional_boundary
  consumer: unique_event_id_and_business_write
  external_side_effects: use_idempotency_key_or_reconciliation
ordering:
  queue: only_when_delivery_mode_and_consumer_count_allow_it
  stream: within_one_partition
```

An inbox table and its insert turn the deduplication decision into a database constraint:

```sql
create table processed_events (
  event_id text primary key,
  processed_at timestamptz not null default now()
);

insert into processed_events (event_id)
values ($1)
on conflict (event_id) do nothing;
```

The handler checks whether the insert affected a row. If it did, the handler applies the business change in the same transaction and commits both together; if it did not, the event was already processed and the handler only acknowledges it. A unique event ID is essential, and the handler must not acknowledge before the transaction commits.

The **transactional outbox** solves a different dual-write problem: the producer writes a business change and an outbound event to the database in one transaction, then a relay publishes the event. The relay normally remains at-least-once, so the consumer still needs idempotency. Ordering is likewise bounded: a queue can preserve order only when its delivery mode and consumer behavior permit it, while a stream preserves order within a partition and only when related records use the same partition key.

## Tradeoffs

| Guarantee or technique | Gain | Cost or limitation |
| --- | --- | --- |
| At-most-once | Lowest processing overhead and no deduplication state | A failure can lose work silently |
| At-least-once | Prevents broker-side loss and suits retryable work | Duplicates, retry traffic, and idempotency state |
| Transactional exactly-once | Atomic read-process-write inside one supported boundary | Narrow scope, infrastructure requirements, and added latency |
| Idempotent consumer | Effectively-once effects over at-least-once delivery | Stable IDs, unique constraints, and retention or cleanup of processed IDs |
| Transactional outbox | Avoids a business-write versus publish race | A relay, polling or change-data-capture path, and delayed publication |
| Strict partition ordering | Simplifies stateful event handling | Hot keys serialize processing and reduce parallelism |

## When to use

- You cannot tolerate losing an order, payment, or account event and can tolerate a duplicate attempt.
- A duplicate would corrupt state, so the consumer can enforce a stable event ID or idempotency key transactionally.
- A provider explicitly supports transactions and every effect stays inside that provider's boundary.
- Lossy telemetry is acceptable and avoiding deduplication state is more valuable than replaying a missed sample.

## Alternatives

- **Inbox deduplication** — makes redelivery safe with ordinary at-least-once delivery, but requires durable event IDs and database uniqueness.
- **Transactional outbox** — makes the business change and publication intent atomic, but does not by itself make the published message's consumer effect exactly once.
- **Two-phase commit or XA** — can coordinate supported resources atomically, but adds blocking, availability, and operational costs.
- **Reconciliation** — repairs missing or duplicate effects by comparing authoritative state later, but temporarily permits divergence and requires a repair process.

## Related

- [Queues vs Streams](01-queues-vs-streams.md)
- [Backpressure and Dead Letter Queues](04-backpressure-dlq.md)
- [Publish-Subscribe](02-pub-sub.md)
- [Distributed Transactions](../../04-distributed-systems/01-consensus/04-distributed-transactions.md)
- [Resilience & Fault Tolerance Patterns: Circuit Breakers, Bulkheads, Exponential Backoff, Retry Strategies, and Timeout Budgets](../../02-system-design/02-software-architecture-patterns/03-resilience-fault-tolerance.md)
