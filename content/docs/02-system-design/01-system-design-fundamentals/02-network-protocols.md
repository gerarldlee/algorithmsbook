---
title: "Network Protocols: OSI Model, TCP/UDP, HTTP/1.1 vs HTTP/2 vs HTTP/3, gRPC, and WebSockets"
weight: 2
toc: true
---

## What it is

Network protocols define how communicating systems frame, route, and interpret messages. The **Open Systems Interconnection (OSI) model** separates communication responsibilities into seven layers, while deployed systems commonly use the TCP/IP model; below them, TCP and UDP provide transport services, and HTTP, gRPC, and WebSocket define application-level exchanges.

## How it works

Each protocol adds meaning without discarding the layers beneath it. Ethernet and IP carry frames between links and hosts, TCP establishes a connection and provides an ordered reliable byte stream, and UDP sends independent datagrams without connection setup, delivery guarantees, or ordering. Application protocols then define messages such as HTTP requests, Protocol Buffers records, and WebSocket frames.

An HTTP exchange exposes the application layer directly:

```http
GET /users/42 HTTP/1.1
Host: api.example.com
Accept: application/json

HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: private, max-age=60

{"id":"42","name":"Ada"}
```

The seven-layer OSI model organizes the stack by responsibility:

| Layer | Unit or concept | Example protocols or technologies | System-design concern |
| --- | --- | --- | --- |
| 7 Application | Messages and operations | HTTP, gRPC, WebSocket, SMTP | Contracts, status semantics, streaming |
| 6 Presentation | Encoding, compression, encryption | JSON, Protocol Buffers, TLS | Payload size, CPU cost, compatibility |
| 5 Session | Dialog and session state | RPC sessions, WebSocket sessions | Connection lifetime, state ownership |
| 4 Transport | Processes across networks | TCP, UDP, QUIC's transport | Reliability, ordering, flow and congestion control |
| 3 Network | Packets between networks | IP, ICMP, routing protocols | Addressing, hops, topology, MTU |
| 2 Data link | Frames on one link | Ethernet, Wi-Fi, PPP | Framing, local delivery, link errors |
| 1 Physical | Signals on a medium | Electrical, optical, or radio links | Bandwidth, latency, distance |

TCP uses sequence numbers, acknowledgments, retransmission, and congestion control to create a reliable stream. This works well for ordinary request/response traffic, but a missing segment can delay later bytes on that same connection. HTTP/1.1 normally sends one request at a time on a connection unless clients use multiple connections. HTTP/2 frames multiple independent streams over one TCP connection and compresses headers, but loss of a TCP segment can still block delivery of every stream on that connection. HTTP/3 carries HTTP semantics over QUIC, whose independently managed streams avoid transport-level head-of-line blocking between requests; QUIC also integrates encrypted transport and connection establishment.

gRPC uses HTTP/2 for unary or streaming calls and Protocol Buffers for typed, compact messages. WebSocket begins with an HTTP upgrade and then reuses the connection for full-duplex text or binary frames. Both suit long-lived service communication, but a stateful long-lived connection changes reconnection, load-balancing, and capacity management.

## Tradeoffs

Choose a protocol by matching its guarantees to the operation rather than by transport label alone:

| Choice | Wins when | Main cost or limitation | Decision rule |
| --- | --- | --- | --- |
| TCP | Ordered, reliable delivery matters | Retransmission and connection state can delay later data | Use for ordinary request/response and file transfer |
| UDP | A fresh datagram is more useful than a delayed one | Application must handle loss, duplication, ordering, and congestion | Use for real-time media, DNS, or QUIC building blocks |
| HTTP/1.1 | Interoperability and simple intermediaries matter | Limited multiplexing increases connection and request overhead | Use through general-purpose caches and legacy clients |
| HTTP/2 | Many concurrent RPCs share a connection | A TCP loss can block all streams on that connection | Use for gRPC and modern clients behind controlled infrastructure |
| HTTP/3 | Loss on one request should not stall other requests | Requires QUIC-aware endpoints and intermediaries | Use when the end-to-end path supports HTTP/3 |
| gRPC | A typed internal contract and streaming matter | Browser access and human-readable inspection require extra tooling | Use between controlled services, not as the only public contract |
| WebSocket | Both peers exchange messages over a long-lived channel | Reconnection, heartbeat, and connection-affinity state complicate scaling | Use for interactive bidirectional sessions |

## When to use

- You need a public request/response contract and the widest client compatibility, which points to HTTP/1.1 or HTTP/2 over TLS.
- You need typed internal RPC, compact messages, or streaming, which points to gRPC over HTTP/2.
- You need a full-duplex interactive channel, which points to WebSocket.
- You need a QUIC-aware path where transport head-of-line blocking matters, which points to HTTP/3.
- You need low-latency datagrams and can tolerate application-level loss handling, which points to UDP.

## Alternatives

- **Raw TCP or UDP sockets** — offer direct control over framing, but require you to build compatibility, discovery, security, and often reliability yourself.
- **Server-Sent Events** — provide simpler one-way server push over HTTP, but cannot carry client-to-server messages on the same stream.
- **Message-oriented middleware** — decouple producers from consumers, but add broker operations and delivery semantics rather than preserving a direct socket connection.

## Related

- [Fundamentals of System Design](01-fundamentals.md)
- [Load Balancing Strategies](03-load-balancing.md)
- [Reverse Proxies, API Gateways, and Edge Routing](04-proxies-gateways.md)
- [API Paradigms: REST, GraphQL, gRPC Protocol Buffers, and Event-Driven Systems](05-api-paradigms.md)
