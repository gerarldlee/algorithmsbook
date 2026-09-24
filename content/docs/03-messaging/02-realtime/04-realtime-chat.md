---
title: "Scalable Real-Time Chat & Collaboration Systems Architecture"
weight: 4
toc: true
---

## What it is

A scalable real-time chat and collaboration system accepts concurrent events, assigns a durable order within each conversation, distributes updates to connected participants, and restores missed state after disconnection. The same architecture can carry chat messages, presence, read state, typing signals, and shared-document operations without making every event equally durable or ordered.

## How it works

Clients authenticate at a real-time gateway and subscribe to conversation and presence streams. Gateway nodes publish accepted events to a partitioned log such as Kafka, route resulting updates back to local sockets, and use a presence engine to locate active sessions. Durable chat history and collaboration metadata live in stores that clients can query after a stream resumes.

A canonical chat message separates client intent from server-assigned state:

```json
{
  "message_id": "msg_01JZ7ZB1H4VJ8KQ2M6N9P3R5T7",
  "client_message_id": "mobile-7f31",
  "conversation_id": "conversation_842",
  "sender_id": "user_142",
  "sequence": 91847,
  "type": "text",
  "body": "The rollout is complete.",
  "created_at": "2026-09-24T17:42:16Z"
}
```

The send path begins when a client creates a unique `client_message_id` and sends the message over WebSocket. The ingress service authenticates the sender, checks conversation membership, validates the payload, and publishes the command to the partition for `conversation_id`. Using that identifier as the partition key keeps accepted events for one conversation in partition order. A consumer allocates the next conversation sequence, persists the message, and records the client identifier used for deduplication.

Exactly-once processing across a gateway, log, database, and push path is not automatic. The design instead makes every retry safe: the database enforces a unique `(conversation_id, client_message_id)` constraint, the client treats its local ID as an idempotency key, and consumers commit offsets only after the durable effect succeeds. A gateway that loses its acknowledgment can resend the same command without creating another message.

After commit, the system fans out the assigned event to participant gateways through pub/sub or the same durable log. Each gateway sends it to local connections and advances a membership cursor. Clients de-duplicate by `message_id` and place messages by `sequence`; a gap suspends normal rendering until catch-up completes. For long outages, clients request missing events by conversation and sequence rather than relying on an ephemeral socket replay.

Offline participants need durable inbox state even when fan-out happens only at delivery time. A projection consumes the message log, determines each user's conversation membership, and creates or advances that user's inbox cursor. Reopening chat reads the conversation store and catches up from the last confirmed sequence. Conversation snapshots can bound catch-up work after a very large gap.

Presence, typing, and read state follow different rules:

- **Presence** is ephemeral, heartbeat-backed state that can be reconstructed from active sessions.
- **Typing** is a throttled hint with a short expiry; missed or duplicated events are acceptable.
- **Read state** is a user-and-conversation watermark rather than a new copy of every message.
- **Shared-document operations** use a CRDT or operational transformation layer to merge concurrent edits, while chat messages keep a conversation order.

This separation prevents a losable typing hint from entering the durable message path and prevents every connected client from writing a separate receipt for every rendered message. Collaboration documents may use presence-aware connections while keeping the document operation log independent of chat delivery.

## Tradeoffs

| Choice | Gain | Cost or risk |
| --- | --- | --- |
| Partition by conversation | Natural message ordering and parallel conversations | One hot conversation can saturate a partition; cross-conversation order is absent |
| Global sequence service | One easy ordering model | Adds coordination latency and limits throughput |
| Durable log as source | Replay, recovery, and independent projections | Consumers must manage offsets, lag, and retention |
| Database as source | Transactional history and straightforward queries | Requires a separate durable event log when cross-service replay is needed |
| Gateway fan-out | Low delivery latency for active participants | Requires connection routing, backpressure, and per-user offline handling |
| Read-modify-write plus notifications | Simple and familiar client code | Concurrent messages and duplicate HTTP requests can lose data |
| CRDT collaboration | Clients can edit and merge during disconnection | Larger payloads and metadata, semantic conflicts, and privacy tradeoffs |
| Operational transformation | Compact transformation history for shared editors | A central ordering service and complex transformation rules |

## When to use

- Users need low-latency messages, presence, typing state, and durable history in the same product.
- Conversations require stable ordering, retry safety, offline catch-up, and multi-device synchronization.
- Collaboration sessions need concurrent edits to merge without holding a central connection lock.
- Gateway capacity and durable event volume require independent horizontal scaling.

## Alternatives

- **Polling-based messaging** — works with simple HTTP infrastructure, but adds polling load and latency to every update.
- **A managed real-time chat SDK** — provides presence, typing, and multi-device features quickly, but adds provider cost and constrains architecture at large scale.
- **Email-style asynchronous discussion** — provides durable history and broad client support, but does not provide live cursors or low-latency collaboration.
- **WebRTC data channels** — move suitable data transfers toward peer-to-peer paths, but signaling, NAT traversal, and fallback relays add complexity and do not replace durable server state.

## Related

- [Real-Time Protocols: WebSockets, Server-Sent Events (SSE), and Long Polling](02-realtime-protocols.md)
- [Distributed Presence Engines, User State Tracking, and Heartbeat Protocols](03-presence-engines.md)
- [Multi-Channel Notification Dispatchers: Push (APNs, FCM), SMS, Email, and Webhook Architecture](01-notification-dispatchers.md)
- [Publish-Subscribe (Pub/Sub) Architecture Mechanics & Fan-Out Design Patterns](../01-messaging/02-pub-sub.md)
