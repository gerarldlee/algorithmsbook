---
title: "Network Protocols"
weight: 2
toc: true
---

## What it is

Network protocols are the agreed formats and rules by which machines exchange data, layered from the physical medium up to application semantics. The choices that matter most in system design are the transport protocols (TCP, UDP) and the application protocols built on top of them (HTTP, gRPC, WebSocket), each optimized for a different pattern of reliability, latency, and connection lifetime.

## How it works

TCP delivers an ordered, reliable byte stream using sequence numbers, acknowledgments, and retransmission, with congestion control that backs off under loss. UDP delivers datagrams with no ordering, reliability, or congestion control, trading those guarantees for minimal overhead and latency. HTTP is a request/response protocol over TCP that adds methods, status codes, and headers; HTTP/1.1 uses persistent connections but head-of-line blocking per connection, HTTP/2 multiplexes many streams over one connection, and HTTP/3 moves to UDP (QUIC) to remove head-of-line blocking entirely. gRPC is a binary RPC framework running over HTTP/2 with Protocol Buffers serialization, while WebSocket upgrades an HTTP connection into a full-duplex, bidirectional channel for long-lived real-time sessions.

The layering of a typical service is described below:

```yaml
# Protocol stack choices for one service
transport:
  tcp:     # ordered, reliable streams; default for request/response
    use:     [http_1_1, http_2, grpc]
  udp:     # unordered, no retry; low latency, realtime
    use:     [dns, quic_http_3, media_streaming]
application:
  http:     # human-readable, cacheable, universally supported
    versions: [1.1, 2, 3]
  grpc:     # binary, schema-first, efficient inside a datacenter
    serialization: protobuf
  websocket:  # full-duplex push after HTTP upgrade
    use: [chat, live_scores, collaboration]
  mqtt:     # lightweight pub/sub for constrained IoT devices
    transport: tcp
```

## Tradeoffs

| Protocol | Strengths | Costs |
| --- | --- | --- |
| TCP | Reliable, ordered, congestion-controlled; works everywhere | Handshake and retransmission latency; head-of-line blocking per connection |
| UDP | Minimal latency and overhead; no connection setup | No delivery or ordering guarantees; you must implement reliability yourself |
| HTTP/1.1 | Simple, cacheable, universally supported | One outstanding request per connection → head-of-line blocking |
| HTTP/2 | Multiplexing over one connection, header compression | Still one TCP connection → blocking at the transport layer |
| HTTP/3 (QUIC) | No head-of-line blocking, faster handshake over UDP | Higher CPU cost; less mature middlebox/load-balancer support |
| gRPC | Strong typing, streaming, efficient binary encoding | Hard to inspect/debug, browser support limited, HTTP/2 required |
| WebSocket | Low-latency bidirectional push over one connection | Stateful, harder to load balance and scale horizontally |

## When to use

- Use TCP/HTTP when correctness and ordering matter more than latency — nearly all request/response APIs.
- Use UDP when losing a stale packet is better than delaying a fresh one — voice/video, telemetry, game state.
- Use gRPC for internal service-to-service calls where a typed contract and low serialization overhead pay off.
- Use WebSocket when the server must push events to clients with sub-second latency over a long-lived connection.

## Alternatives

- **REST over HTTP** — human-readable and cacheable, but text serialization and per-request overhead exceed gRPC for internal calls.
- **Raw TCP sockets** — minimal overhead and full control, but you reimplement framing, reliability, and error handling by hand.

## Related

- [System Design Fundamentals](01-fundamentals.md)
- [API Paradigms](05-api-paradigms.md)
- [Load Balancing](03-load-balancing.md)
- [Proxies and Gateways](04-proxies-gateways.md)
- [Caching Strategies](../02-caching/01-in-memory-caching.md)
