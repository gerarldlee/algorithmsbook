---
title: "Realtime Protocols"
weight: 2
toc: true
---

## What it is
Realtime protocols are the transport mechanisms that push server-originated events to clients with low latency: WebSocket (bidirectional), Server-Sent Events (one-way server push), long-polling (emulated push over HTTP), and WebRTC (peer-to-peer media and data channels).

## How it works
**WebSocket** upgrades an HTTP connection to a full-duplex TCP channel, letting either side send frames at any time; a persistent connection avoids repeated handshakes. **Server-Sent Events (SSE)** keep a long-lived HTTP response open and stream `text/event-stream` frames server-to-client only, with automatic reconnection and event IDs. **Long-polling** has the client open a request the server holds until data is available or a timeout, then immediately re-request—simulating push while working through intermediaries. **WebRTC** negotiates a direct peer-to-peer connection (via ICE/STUN/TURN) carrying encrypted audio, video, or arbitrary data channels, bypassing the server for media transport. In practice an architecture often layers them: WebSocket or SSE for signaling and control, WebRTC for media, and long-polling as a fallback where proxies block upgrades.

## Tradeoffs
- **WebSocket**: lowest bidirectional latency and overhead per message, but needs sticky sessions or a connection-aware load balancer, has no built-in reconnection/backoff, and holds a server socket per client.
- **SSE**: simple, HTTP-native, auto-reconnects, and works with standard load balancers, but is unidirectional (client sends via separate POST) and has proxy/timeout quirks; fewer client libraries than WebSocket.
- **Long-polling**: maximal compatibility through any proxy/firewall, but adds request overhead and higher average latency; connection churn stresses servers at scale.
- **WebRTC**: sub-second peer media with no server relay for data, but needs TURN/STUN infrastructure for NAT traversal, signaling for setup, and is complex to operate.
- **Connection scaling**: persistent connections consume server memory/ports; horizontal scaling requires connection affinity or a pub/sub fan-out behind the transport.

## When to use
- WebSocket for interactive bidirectional apps: chat, live collaboration, games, realtime dashboards.
- SSE for one-way feeds—notifications, stock ticks, log tails—where simplicity and auto-reconnect matter.
- Long-polling as a fallback for old clients or restrictive networks that block WebSocket/SSE.
- WebRTC for voice/video calls, screen sharing, and low-latency peer data (file transfer).

## Alternatives
- **Periodic client polling (fixed interval)**: trivial to implement and cache-friendly, but wastes bandwidth and adds up-to-a-poll-interval latency.
- **WebTransport (HTTP/3)**: lower-latency multiplexed bidirectional transport, but newer and less widely supported than WebSocket.
- **MQTT**: lightweight pub/sub over TCP designed for constrained IoT devices, but heavier broker infra for general web apps.

## Related
- [Notification Dispatchers](01-notification-dispatchers.md)
- [Presence Engines](03-presence-engines.md)
- [Realtime Chat](04-realtime-chat.md)
- [Load Balancing](../../02-system-design/01-system-design-fundamentals/03-load-balancing.md)
