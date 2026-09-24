---
title: "Load Balancing"
weight: 3
toc: true
---

## What it is

A load balancer distributes incoming traffic across a pool of backend servers so that no single instance becomes a bottleneck, and so that failures can be absorbed without user impact. Load balancers operate either at the transport layer (L4, routing by IP/port/TCP) or the application layer (L7, routing by HTTP attributes such as path, headers, and cookies).

## How it works

The balancer maintains a health-checked pool of backends and applies a scheduling algorithm to pick a target for each request. Round-robin cycles through backends in order; least-connections sends to the backend with the fewest active connections; consistent hashing maps each request key to a backend on a ring so that a stable subset of keys sticks to each backend and only a small fraction reshuffles when the pool changes. L7 balancers additionally terminate TLS and can route, rewrite, and cache based on request content. Sticky sessions (session affinity) pin a client to one backend via a cookie or source IP when the backend holds local state.

A typical L7 configuration is described below:

```yaml
# L7 load balancer configuration (e.g. ALB / HAProxy)
listener:
  protocol: https
  port: 443
  tls: cert_from_acm
target_group:
  backends: [10.0.1.10, 10.0.1.11, 10.0.1.12]
  health_check:
    path: /health
    interval_sec: 10
    healthy_threshold: 3
    unhealthy_threshold: 2
routing:
  algorithm: least_connections   # or round_robin | consistent_hash
  rules:
    - path: /api/*    -> api_target_group
    - host: img.example.com -> image_target_group
stickiness:
  enabled: true
  cookie: AWSALB
```

## Tradeoffs

| Choice | Trade-off |
| --- | --- |
| L4 balancer | Very fast, protocol-agnostic, low overhead — but cannot route on HTTP content or terminate TLS. |
| L7 balancer | Rich routing, TLS termination, caching — but higher latency and CPU cost per request. |
| Round-robin | Simple and fair for uniform load — but ignores backend load imbalance and long-lived connections. |
| Least-connections | Adapts to uneven request costs — but tracks connection state and can thrash under rapid connect/disconnect. |
| Consistent hashing | Stable key→backend mapping, minimal reshuffle on scale — but load can skew if key distribution is uneven. |
| Sticky sessions | Required for local server state — but breaks even distribution and complicates failover. |
| NLB vs ALB | NLB (L4) gives extreme throughput and static IPs; ALB (L7) gives content routing and TLS but adds latency. |

## When to use

- When traffic exceeds a single server's capacity or you need zero-downtime deploys and automatic failover.
- Use an L7 balancer when routing must depend on paths, hosts, or headers (e.g. `/api/*` vs static assets).
- Use consistent hashing for cache-backed or shard-aware services where a request must always reach the same backend.
- Use a cloud NLB for raw throughput/TCP workloads and an ALB or HAProxy for HTTP-layer control.

## Alternatives

- **DNS round-robin** — distributes across IPs with zero proxy cost, but has no health checking and caches stale results at resolvers.
- **Client-side load balancing** (service-discovery aware clients) — removes a hop and a proxy SPOF, but pushes logic into every client and complicates upgrades.

## Related

- [System Design Fundamentals](01-fundamentals.md)
- [Network Protocols](02-network-protocols.md)
- [Proxies and Gateways](04-proxies-gateways.md)
- [API Paradigms](05-api-paradigms.md)
- [Rate Limiting](../02-caching/04-rate-limiting.md)
