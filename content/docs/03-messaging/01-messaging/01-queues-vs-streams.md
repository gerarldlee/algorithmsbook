---
title: "Message Queues vs Event Streams (RabbitMQ, Apache Kafka, Apache Pulsar)"
weight: 1
toc: true
---

## What it is

Message queues and event streams are asynchronous delivery models with different retention and consumption semantics. A **message queue** assigns a message to one competing consumer at a time, while an **event stream** stores an ordered, replayable log that each consumer group can read independently. RabbitMQ and Amazon SQS illustrate the queue model; Apache Kafka and Apache Pulsar illustrate the stream model.

## How it works

A queue broker routes a message to a queue and makes it available to one member of a competing-consumer pool. The broker removes the message after the consumer acknowledges it, so a failed or disconnected consumer can cause redelivery. Queue order depends on the broker and queue configuration; multiple consumers, retries, and competing deliveries can change the order observed by an application.

A stream broker appends records to a partitioned, durable log. Each consumer group stores its own position, and a group normally reads each record once while it advances through the log, while members of one group share the partitions. A group can continue from its last offset, reset to an earlier retained offset, or start a new derived stream. Keys map related records to the same partition, which gives ordering only within that partition, not across the whole stream.

The delivery models can be represented as an infrastructure contract:

```yaml
queue:
  engines: [rabbitmq, amazon_sqs]
  destination: one queue
  consumers: competing
  acknowledgment: removes or completes delivery
  history: retained only while the queue retains the message
  ordering: broker and queue dependent
stream:
  engines: [apache_kafka, apache_pulsar]
  destination: append_only_partitioned_log
  consumers: independent_groups
  acknowledgment: advances_a_group_offset
  history: configured_time_or_size_retention
  ordering: within_a_partition
  replay: from_any_retained_offset
```

RabbitMQ emphasizes flexible routing and acknowledgments, including quorum queues that replicate messages and queue metadata. Kafka emphasizes a replicated, partitioned log and consumer-group offsets. Pulsar separates a durable logical topic from its partitioned storage and supports configurable retention, compaction, and consumer positions. These products share the stream vocabulary but differ in storage, replication, and operational controls; select the engine from its failure and retention semantics rather than from the name alone.

## Tradeoffs

| Dimension | Queue | Stream |
| --- | --- | --- |
| Consumption | One consumer handles each delivery; retries can produce duplicates | A group advances through retained records; members share a group |
| Replay | Requires redelivery or an archive before acknowledgment | Native offset reset while the record is retained |
| Retention | Usually tied to acknowledgment and message visibility | Explicit time, size, or compaction policies |
| Ordering | Depends on the queue and delivery mode | Ordered within a partition; no global stream order |
| Load leveling | Natural because workers pull at their own pace | Consumers track lag and capacity explicitly |
| Storage | Usually smaller working set | Retained history increases storage and network cost |
| Routing | Exchanges, routing keys, and dead-letter policies are central | Producers append records; consumers choose partitions and groups |

## When to use

- You need to distribute background jobs among interchangeable workers and load-level traffic spikes.
- You need a work item to move to one consumer without maintaining a long-lived event history.
- You need independent consumers to replay retained facts for audit, analytics, or rebuilding state.
- You can choose a partitioning key and accept ordering only within each key's partition.

## Alternatives

- **Amazon SQS** — provides managed at-least-once queue delivery with little broker operations, but its standard queue does not provide a retained replay log.
- **Amazon Kinesis Data Streams** — provides a managed partitioned stream with consumer offsets, but shard count, retention, and throughput require explicit capacity planning.
- **Redis Streams** — provides consumer groups and replayable entries in Redis, but memory, persistence, and retention settings must fit the workload.
- **RabbitMQ publisher confirms** — confirms that a broker accepted a publish, but it does not by itself make the downstream business operation exactly once.

## Related

- [Publish-Subscribe](02-pub-sub.md)
- [Delivery Guarantees](03-delivery-guarantees.md)
- [Backpressure and Dead Letter Queues](04-backpressure-dlq.md)
- [Notification Dispatchers](../02-realtime/01-notification-dispatchers.md)
- [API Paradigms: REST, GraphQL, gRPC Protocol Buffers, and Event-Driven Systems](../../02-system-design/01-system-design-fundamentals/05-api-paradigms.md)
