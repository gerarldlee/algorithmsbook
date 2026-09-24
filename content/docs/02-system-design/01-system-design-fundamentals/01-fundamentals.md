---
title: "Fundamentals of System Design: Latency, Throughput, Availability, and SLA/SLO/SLI"
weight: 1
toc: true
---

## What it is

System design turns product requirements into cooperating components and measurable operating goals. **Latency** measures how long an operation takes, **throughput** measures completed work per unit of time, and **availability** measures the fraction of time a service can perform its required work; a **service-level indicator (SLI)** measures one of those properties, a **service-level objective (SLO)** sets a target for the SLI, and a **service-level agreement (SLA)** is the contractual boundary built around the objective.

## How it works

A design starts with a workload model: request rates, arrival patterns, data sizes, latency targets, and the consequences of failure. A **goodput** target distinguishes useful completed requests from merely completed attempts, while percentile latency describes the slow tail that users experience. An SLI needs a precise numerator, denominator, observation window, and eligible traffic; "99.9% uptime" is incomplete until those boundaries define which failures count.

Prometheus rules can turn those definitions into continuously evaluated SLIs:

```yaml
groups:
  - name: checkout-api-service-level-indicators
    interval: 30s
    rules:
      - record: checkout_api:request_rate:5m
        expr: sum(rate(http_requests_total{service="checkout-api"}[5m]))
      - record: checkout_api:goodput:5m
        expr: sum(rate(http_requests_total{service="checkout-api",status!~"5.."}[5m]))
      - record: checkout_api:availability:5m
        expr: |
          sum(rate(http_requests_total{service="checkout-api",status!~"5.."}[5m]))
          /
          sum(rate(http_requests_total{service="checkout-api"}[5m]))
      - record: checkout_api:request_duration:p99_5m
        expr: |
          histogram_quantile(
            0.99,
            sum by (le) (
              rate(http_request_duration_seconds_bucket{service="checkout-api"}[5m])
            )
          )
      - alert: CheckoutApiAvailabilityBudgetBurn
        expr: checkout_api:availability:5m < 0.999
        for: 5m
```

The SLO sets targets such as a minimum availability ratio or maximum p99 latency. The SLA states external consequences and remedies when the provider misses the committed SLO, such as service credits. During capacity planning, you allocate a latency budget across DNS, connection setup, the edge, the application, each datastore call, and the client. During operations, you compare measured SLIs with the SLO, preserve raw indicators, and alert on error-budget burn rather than treating isolated infrastructure alerts as user-visible failures.

A request path commonly crosses DNS or an anycast address, a CDN, a load balancer, stateless application replicas, and a stateful tier. You scale stateless replicas horizontally; you scale databases and caches through replication, partitioning, or both; and you use queues to absorb work that does not need to finish in the request. Each hop must have bounded timeouts, and retries require a retry budget so one failed dependency does not multiply traffic.

## Tradeoffs

The design objective determines which measurements and optimization choices deserve priority:

| Objective | Primary measurement | Prefer when | Cost to manage |
| --- | --- | --- | --- |
| Tail latency | Successful-operation latency at a percentile such as p99 | Users directly feel slow requests | Instrumentation, coordinated timeout budgets, and tail-aware capacity testing |
| Maximum throughput | Good completed operations per second | The service has a hard demand or quota limit | More contention, backpressure, and cost from running near saturation |
| High availability | Successful eligible requests divided by eligible requests | The product must remain usable during dependency or zone failures | Redundant capacity, failover testing, and potentially weaker consistency |
| Fast recovery | Time to restore an SLO after a failure | Failures occur and restoration is operationally expensive | On-call capability, automation, and maintained recovery procedures |
| Durable processing | Successfully completed asynchronous work | Callers cannot wait for downstream work to finish | Duplicate delivery handling, backlog growth, and observability across stages |

Availability, latency, and consistency are separate choices rather than a single universal slider. Caching and replication can improve some requests while introducing stale data; synchronous writes can simplify correctness at the cost of latency and dependency availability. Pick explicit consistency and failure semantics for each operation, then document the resulting budget.

## When to use

- You need to translate user needs into measurable latency, throughput, availability, and recovery targets.
- You expect traffic, data volume, or failure domains to exceed one process or machine.
- You are choosing between synchronous and asynchronous work, or between caching and reading from the source of truth.
- You need an error budget to decide when reliability work takes priority over feature delivery.
- You are reviewing a design for dependency timeouts, retries, overload behavior, and recovery.

## Alternatives

- **Single-server monolith** — wins for small workloads and simple operations, but concentrates capacity and failure in one process or machine.
- **Serverless composition** — removes server management and scales on demand, but introduces platform limits, cold starts, and less control over steady-state capacity.
- **Fixed service contract** — a static SLA is simpler to administer, but offers a weaker operational objective than directly measuring and managing SLOs.

## Related

- [Network Protocols](02-network-protocols.md)
- [Load Balancing Strategies](03-load-balancing.md)
- [API Paradigms: REST, GraphQL, gRPC Protocol Buffers, Event-Driven Systems, tRPC, and OpenAPI/AsyncAPI](05-api-paradigms.md)
- [Resilience & Fault Tolerance Patterns: Circuit Breakers, Bulkheads, Exponential Backoff, Retry Strategies, and Timeout Budgets](../02-software-architecture-patterns/03-resilience-fault-tolerance.md)
- [In-Memory Caching Engines (Redis, Memcached) & Eviction Policies (LRU, LFU, ARC)](../02-caching/01-in-memory-caching.md)
- [Application Caching Patterns: Cache-Aside, Write-Through, Write-Around, Write-Behind](../02-caching/02-caching-patterns.md)
