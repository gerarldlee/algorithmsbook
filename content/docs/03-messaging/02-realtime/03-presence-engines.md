---
title: "Presence Engines"
weight: 3
toc: true
---

## What it is
A presence engine tracks which users are currently online or offline, and often their richer state (away, busy, in a call), distributing that state to interested peers in near-real time so applications can show status indicators and route messages appropriately.

## How it works
Clients announce presence when they connect and periodically emit heartbeats (e.g. every 30 seconds) while connected. The engine stores presence in a fast key-value store with short TTLs—a record `presence:{userId} = {status, last_seen, node}` with a TTL slightly longer than the heartbeat interval, so an expired key means the user silently dropped. On connect/heartbeat the engine refreshes the TTL; on explicit disconnect it deletes the key. State changes are broadcast to subscribers (friends, channel members) via pub/sub. Two dominant architectures exist: **Redis pub/sub** where each gateway node subscribes to per-user channels and tracks who is connected to it, periodically reporting aggregates; and a **gossip protocol** where nodes exchange membership state directly, eventually converging without a central coordinator. Reads for "who is online in this group" fan out to the nodes or to a maintained group-level presence set.

## Tradeoffs
- **Redis pub/sub**: simple, fast, and battle-tested, but Redis becomes a scalability and availability chokepoint; per-channel subscriptions scale with connections.
- **Gossip**: no central bottleneck and good fault tolerance, but convergence is only eventual and transiently inconsistent; state propagation adds chatter.
- **Heartbeat frequency**: shorter intervals give faster offline detection at the cost of more traffic; longer intervals save bandwidth but delay detecting dead connections.
- **Accuracy vs. load**: presence is inherently approximate—crashed clients are detected only after TTL expiry—so the engine trades detection latency against server load.
- **Ephemerality**: storing presence in volatile memory/TTL keys favors speed over durability; presence is rebuilt on reconnect.

## When to use
- Chat and collaboration apps showing online/offline, typing, and "active now" indicators.
- Routing calls or messages only to online nodes, or falling back to offline delivery when a user is absent.
- Multi-node deployments where you must know which gateway server holds a given user's connection.

## Alternatives
- **Polling-based status checks**: clients periodically request peer status—dead simple but high latency and load compared to push.
- **Central presence table in a database**: durable and easy to query, but slow writes and no natural TTL expiry, hurting realtime status.
- **Managed presence services (Pusher, Ably)**: turnkey scalable presence channels with less ops burden, but add cost and vendor lock-in.

## Related
- [Realtime Protocols](02-realtime-protocols.md)
- [Realtime Chat](04-realtime-chat.md)
- [Pub/Sub Systems](../01-messaging/02-pub-sub.md)
- [Consensus & Clocks](../../04-distributed-systems/01-consensus/03-clocks-ordering.md)
