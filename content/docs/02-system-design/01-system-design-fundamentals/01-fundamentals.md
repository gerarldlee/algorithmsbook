---
title: "System Design Fundamentals"
weight: 1
toc: true
---

## What it is

System design is the discipline of decomposing a product's requirements into a set of cooperating components — servers, storage, networks, and services — and arranging them so the system meets its non-functional goals. The core vocabulary of every design discussion is scalability, availability, latency, consistency, and reliability, each of which describes a different dimension of behavior under load or failure.

## How it works

A design starts from the request path: clients reach edge components (DNS, CDN, load balancer) that route to stateless application servers, which in turn read and write stateful stores (databases, caches, queues). Horizontal scaling adds more replicas of the stateless tier, while stateful tiers are scaled by partitioning (sharding) or replication. The fundamental tension is that low latency, high availability, and strong consistency cannot all be maximized at once; a concrete design picks a point on that trade-off surface and makes the choice explicit.

The canonical starting template for a high-scale service is captured in the architecture below:

```yaml
# Reference architecture: horizontally-scaled stateless tier over a stateful tier
entry:
  dns:            # global routing, geo-located
  cdn:            # cache static/edge content close to users
  load_balancer:  # spreads traffic across app replicas (L7)
application:
  replicas: N              # horizontally scalable, stateless
  auto_scale: cpu_gt_70%   # scale out/in by metric
stateful:
  cache:            # redis/memcached, in-memory, hot data
  primary_db:      # system of record, sharded by key
  replicas: M      # read replicas for scale
  queue:           # async work, decouples spikes
  object_store:     # blobs, images, backups
observability: [metrics, logs, traces]  # required, not optional
```

## Tradeoffs

| Dimension | Trade-off |
| --- | --- |
| Scalability | Horizontal scaling is operationally simple but adds load-balancer and coordination overhead; vertical scaling is trivial until it hits a hard ceiling. |
| Availability | More replicas and redundancy raise uptime but increase cost, replication lag, and consistency risk. |
| Latency | Caching and CDNs cut latency but introduce staleness and cache-invalidation complexity. |
| Consistency | Strong consistency simplifies reasoning but sacrifices availability during partitions; eventual consistency maximizes availability at the cost of stale reads. |
| Reliability | Redundancy, retries, and timeouts improve reliability but amplify load and can duplicate work without idempotency. |

## When to use

- When the expected traffic or data volume can exceed a single machine's capacity, requiring a scale-out plan from day one.
- When the product has explicit SLOs (uptime, p99 latency) that must be reasoned about and defended against failures.
- When a design decision — cache vs. source of truth, sync vs. async — will affect correctness, and the trade-off needs to be documented.

## Alternatives

- **Monolithic single-server design** — simplest to build and reason about, but cannot scale horizontally and has a single point of failure.
- **Serverless (FaaS) composition** — removes most capacity planning, but adds cold-start latency and less predictable cost at high sustained load.

## Related

- [Network Protocols](02-network-protocols.md)
- [Load Balancing](03-load-balancing.md)
- [Proxies and Gateways](04-proxies-gateways.md)
- [API Paradigms](05-api-paradigms.md)
- [Caching Strategies](../02-caching/01-in-memory-caching.md)
