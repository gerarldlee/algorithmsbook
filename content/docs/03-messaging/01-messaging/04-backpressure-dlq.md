---
title: "Backpressure and Dead Letter Queues"
weight: 4
toc: true
---

## What it is

Backpressure is the mechanism that prevents a fast producer from overwhelming a slow consumer by throttling or buffering the flow. A **dead letter queue (DLQ)** is a holding queue where messages that cannot be processed successfully — after exhausting retries, or that are malformed — are parked for inspection instead of being lost or retried forever.

## How it works

When consumers fall behind, the broker buffers messages and consumer lag grows; backpressure signals the producer to slow down (bounded queues, blocking puts, TCP flow control, or Kafka producer quotas) so memory and disk are not exhausted. Retries handle transient failures, typically with **exponential backoff and jitter** to avoid a retry storm. After a configured retry limit, the broker routes the message to a DLQ, where operators can inspect, replay, or discard it. This keeps a poison message from blocking its queue (head-of-line blocking) and preserves the evidence of failures for later analysis.

A typical flow-control and retry configuration:

```yaml
# Backpressure and dead-letter handling
backpressure:
  bounded_queue: true           # reject or block when full
  consumer_lag: alert_threshold # monitor and scale out if exceeded
  producer: [quota, pause]     # slow the source, don't buffer forever
retries:
  max_attempts: 5              # bounded, never infinite
  backoff: exponential         # 1s, 2s, 4s, 8s ...
  jitter: full                 # randomize to spread the retry storm
  idempotency_key: required    # so retries are safe
dead_letter:
  on: retry_exhausted          # or poison message / schema error
  action: [inspect, replay, discard]
  alert: true                  # DLQ growth is a signal, not a sink
```

## Tradeoffs

| Approach | Strengths | Costs |
| --- | --- | --- |
| Unbounded buffering | Never drops; producer never blocks | Unbounded memory/disk; lag can grow forever |
| Bounded queue + blocking | Predictable resource use | Producer stalls if consumers stay slow |
| Exponential backoff + jitter | Spreads retries, avoids thundering herd | Adds latency; needs an idempotent consumer |
| Dead letter queue | Isolates poison messages, preserves evidence | Requires ops to monitor and replay; silent failure if ignored |

## When to use

- Use backpressure whenever producers can outpace consumers — event ingestion, batch jobs, and any queue with bursty traffic — to keep memory and latency bounded.
- Use a DLQ whenever messages can be permanently unprocessable (schema changes, poisoned payloads) or when retries are bounded and failures must be inspected rather than dropped.
- Use exponential backoff with jitter for calls to flaky downstream services so retries converge instead of synchronizing into a storm.

## Alternatives

- **Drop on overflow** — shed load when the queue is full, trading lost messages for stable latency (common in telemetry and rate-limited APIs).
- **Scale consumers instead of buffering** — autoscale workers to absorb the surge, which keeps latency low but costs more and lags behind sudden spikes.
- **Infinite retry** — keep retrying forever, which preserves the message but risks a poison message blocking the queue indefinitely.

## Related

- [Delivery Guarantees](03-delivery-guarantees.md)
- [Queues vs Streams](01-queues-vs-streams.md)
- [Rate Limiting](../../02-system-design/02-caching/04-rate-limiting.md)
- [Notification Dispatchers](../02-realtime/01-notification-dispatchers.md)
