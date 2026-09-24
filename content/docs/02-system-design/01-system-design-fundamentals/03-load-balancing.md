---
title: "Load Balancing Strategies: L4 vs L7, Round-Robin, Least Connections, Consistent Hashing"
weight: 3
toc: true
---

## What it is

Load balancing distributes requests across backend instances and removes unhealthy targets from the eligible set. An **L4 load balancer** forwards transport connections using addresses and ports, while an **L7 load balancer** understands HTTP messages and can route by hostname, path, headers, or other application attributes.

## How it works

A load balancer receives traffic, selects an eligible backend, forwards the request, and observes the result. Health checks determine eligibility; a connection failure or unhealthy response removes a target until it recovers. The scheduler then applies a distribution strategy. **Round-robin** advances through targets in order. **Least connections** favors the target with the fewest active connections, which often handles uneven connection lifetimes better. **Consistent hashing** maps a selected key to a position on a hash ring, so adding or removing a target remaps only keys near that target; virtual nodes reduce skew caused by an uneven physical ring. None of these strategies can create capacity, so load tests must cover both the scheduler and the backend's bottleneck.

This Envoy configuration selects an L7 route and uses active health checks with least-request scheduling:

```yaml
static_resources:
  listeners:
    - name: ingress
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 8080
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: ingress_http
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: services
                      domains: ["*"]
                      routes:
                        - match:
                            prefix: "/api/"
                          route:
                            cluster: api_pool
                            timeout: 5s
  clusters:
    - name: api_pool
      type: STATIC
      lb_policy: LEAST_REQUEST
      load_assignment:
        cluster_name: api_pool
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: 10.0.1.10
                      port_value: 8080
              - endpoint:
                  address:
                    socket_address:
                      address: 10.0.1.11
                      port_value: 8080
              - endpoint:
                  address:
                    socket_address:
                      address: 10.0.1.12
                      port_value: 8080
      health_checks:
        - timeout: 1s
          interval: 10s
          unhealthy_threshold: 2
          http_health_check:
            path: /health
```

L4 balancing preserves the transport connection and works for TCP or UDP without parsing the application payload. L7 balancing can terminate TLS, select a service from an HTTP path, and apply retries or request policies, but it consumes more CPU and memory. Sticky sessions preserve local session state through a cookie or affinity mechanism, yet they reduce distribution freedom and can send a client to a failed backend. Prefer externalizing session state unless affinity is required by a real backend constraint.

## Tradeoffs

Match the balancer layer and scheduling policy to the workload:

| Choice | Gain | Cost or failure behavior | Use when |
| --- | --- | --- | --- |
| L4 | Protocol independence and lower per-request processing cost | Cannot inspect HTTP content; usually forwards connection-level failures | TCP or UDP services need high throughput or transparent proxying |
| L7 | Host and path routing, TLS termination, and per-request policy | More CPU and memory; policy bugs affect the entire ingress path | HTTP traffic needs content-aware routing or observability |
| Round-robin | Simple and predictable for similarly sized targets | Ignores target load and request cost | Backends have similar capacity and similar request cost |
| Least connections | Adapts to targets with long or short connections | Depends on timely connection accounting and may favor stale observations | Connection durations vary substantially |
| Weighted round-robin | Lets operators represent known capacity differences | Weights become stale as capacity changes | A small set of targets has different provisioned limits |
| Consistent hashing | Minimizes key remapping when membership changes | Skew remains possible when key distribution or virtual-node placement is poor | Cache or sharded work benefits from key affinity |
| Session affinity | Keeps stateful clients on one backend without a shared store | Reduces balancing freedom and complicates failover | A backend genuinely requires local session state |

## When to use

- Traffic exceeds one backend's safe capacity or you need to remove instances without interrupting clients.
- You need health checks and failover across availability zones or regions.
- HTTP requests must route by host, path, method, or header.
- You operate a cloud network load balancer for connection-level TCP or UDP traffic.
- Cache keys or partition ownership benefit from stable placement across membership changes.

## Alternatives

- **DNS round-robin** — adds no proxy hop, but clients and resolvers cache answers and the DNS layer gives weak backend-health signals.
- **Client-side load balancing** — removes one network hop, but requires every client to implement discovery, selection, and failover correctly.
- **Service discovery without a proxy** — keeps service-to-service paths direct, but central policy and consistent traffic observation become application responsibilities.

## Related

- [Fundamentals of System Design: Latency, Throughput, Availability, and SLA/SLO/SLI](01-fundamentals.md)
- [Network Protocols](02-network-protocols.md)
- [Reverse Proxies, API Gateways, and Edge Routing](04-proxies-gateways.md)
- [Rate Limiting & Traffic Shaping: Token Bucket, Leaky Bucket, Sliding Window Log, and Counter](../02-caching/04-rate-limiting.md)
- [Queues vs Streams](../../03-messaging/01-messaging/01-queues-vs-streams.md)
