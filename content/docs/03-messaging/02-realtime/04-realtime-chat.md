---
title: "Realtime Chat"
weight: 4
toc: true
---

## What it is
A realtime chat system delivers messages between users with low latency while preserving conversation integrity—ordering, persistence, read receipts, and typing indicators—typically built on WebSocket connections fronted by a fan-out and storage layer.

## How it works
A client opens a WebSocket (or long-polling) connection to a gateway server, which registers the session in a presence engine. On send, the message is written to durable storage with a monotonically increasing per-conversation sequence number, then fanned out to every participant's gateway for push, while also being returned to the sender as an echo/ack. **Message ordering** is established via server-assigned sequence IDs per conversation (or Lamport clocks for cross-device ordering); offline recipients are delivered later from an inbox, and ordering is reconciled against the stored sequence on reconnect. **Read receipts** are emitted when a client fetches or renders a message, and are themselves events broadcast to the sender. **Typing indicators** are lightweight ephemeral events sent on keystroke start/stop, throttled to avoid flooding, and never persisted. **Storage** typically uses a database sharded by conversation or user, with hot recent messages cached and older messages archived; attachments are written to object storage and referenced by URL.

## Tradeoffs
- **Ordering**: global ordering guarantees are expensive at scale; per-conversation ordering is usually sufficient but cross-device consistency needs extra logic.
- **At-least-once vs. exactly-once delivery**: retries can duplicate messages, so the system either accepts occasional dupes or pays for idempotent de-duplication.
- **Read receipts**: richer engagement but doubles write volume (one event per recipient); often batched/compressed to reduce load.
- **Typing indicators**: cheap realtime signals but must be throttled and dropped freely—persisting them is wasteful and privacy-sensitive.
- **Storage strategy**: hot/cold tiering (recent in cache/SSD, old in object storage) balances cost against retrieval latency for history search.
- **Connection scaling**: many long-lived sockets require sticky sessions or a pub/sub layer behind the gateways.

## When to use
- One-to-one and group messaging in consumer or enterprise apps needing sub-second delivery.
- Any product needing presence, read state, and typing cues alongside message history.
- High-volume messaging where per-conversation ordering, durable history, and offline delivery are required.

## Alternatives
- **Polling-based chat**: the client polls a messages endpoint every few seconds—trivial to build, but high latency and load, and no push for typing/read events.
- **Managed chat SDKs (Sendbird, Stream, Twilio)**: rapid feature-rich delivery with less ops, but per-message cost and limited control at large scale.
- **Email/forum-style messaging**: durable and simple, but no realtime semantics (ordering, receipts, presence).

## Related
- [Realtime Protocols](02-realtime-protocols.md)
- [Presence Engines](03-presence-engines.md)
- [Notification Dispatchers](01-notification-dispatchers.md)
- [Pub/Sub Systems](../01-messaging/02-pub-sub.md)
