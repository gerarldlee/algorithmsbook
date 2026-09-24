---
title: "Notification Dispatchers"
weight: 1
toc: true
---

## What it is
A notification dispatcher is a service that routes outgoing messages to users across multiple delivery channels—push (APNs/FCM), email, SMS, and in-app—deciding per recipient which channel(s) to use, fanning out to potentially millions of targets, retrying failures, and de-duplicating repeated deliveries.

## How it works
An upstream event (message sent, payment cleared, comment liked) is normalized into a notification envelope containing the recipient, payload, priority, and channel preferences. The dispatcher fans out the envelope to every subscriber of the recipient, looks up each subscriber's device tokens and channel settings, then hands each message to a per-channel adapter. Push adapters speak to Apple Push Notification service (APNs) or Firebase Cloud Messaging (FCM); email adapters use SMTP or a provider API; SMS adapters use carriers or aggregators like Twilio. Each adapter enforces provider rate limits and handles transport errors. The dispatcher maintains a retry queue with exponential backoff for transient failures (rate-limited, temporarily unreachable) and a dead-letter queue for permanent failures (invalid token, unsubscribed). A de-duplication layer keyed by a stable notification ID (e.g. `userId:eventId`) prevents the same event from being delivered twice when retries overlap or events are replayed. Delivery receipts and open/click callbacks flow back to analytics.

## Tradeoffs
- **Fan-out model**: database-driven fan-out (query subscribers per event) is storage-cheap but slow at send time; inbox/precomputed fan-out (write to each recipient's inbox on event) is fast to send but multiplies writes by the fan-out factor.
- **Channel guarantees**: push and SMS are best-effort with no delivery receipt in some paths; email has richer bounce/receipt semantics. Cross-channel consistency is only eventual.
- **Ordering vs. throughput**: global per-recipient ordering adds a serialization bottleneck; most dispatchers relax to per-channel best-effort ordering.
- **Dedup vs. storage**: exact-once dedup requires persisting delivery state, trading storage/reads for idempotency.
- **Vendor coupling**: routing through APNs/FCM/twilio locks the system to provider APIs and rate limits; a provider outage degrades one channel independently.

## When to use
- Sending push notifications to mobile/web users at scale (APNs for iOS, FCM for Android).
- Multi-channel fan-out where a single event must reach email, SMS, and push subscribers with per-user preferences.
- Scenarios requiring retries with backoff, dead-letter handling for invalid tokens, and dedup of replayed events.

## Alternatives
- **Direct provider integration per service**: each service calls APNs/FCM itself—simpler to start, but fragments retry/dedup logic and rate-limit handling across the codebase.
- **Third-party notification APIs (OneSignal, Courier)**: rapid adoption and cross-provider abstraction, but adds a vendor dependency and per-message cost at scale.
- **Email/SMTP-only delivery**: trivial and reliable for low urgency, but no realtime push and poor mobile engagement.

## Related
- [Queues vs. Streams](../01-messaging/01-queues-vs-streams.md)
- [Pub/Sub Systems](../01-messaging/02-pub-sub.md)
- [Delivery Guarantees](../01-messaging/03-delivery-guarantees.md)
- [Backpressure & Dead Letter Queues](../01-messaging/04-backpressure-dlq.md)
