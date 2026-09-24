---
title: "Resilience & Fault Tolerance Patterns: Circuit Breakers, Bulkheading, Exponential Backoff with Jitter, Retry Strategies, and Timeout Budgets"
weight: 3
toc: true
---

## What it is

Resilience and fault-tolerance patterns keep a system useful when a dependency is slow, unavailable, or overloaded. A **circuit breaker** stops sending requests to a failing dependency for a period, a **bulkhead** partitions resources so one workload cannot consume every connection or worker, **exponential backoff with jitter** spaces retries without synchronized retry storms, and a **timeout budget** gives each nested call a deadline that fits the caller's remaining time.

## How it works

A timeout is a promise not to wait indefinitely. A caller chooses a deadline based on the user-visible operation, then gives each dependency a smaller slice of the remaining budget. If a database call receives 200 ms while the overall request has 500 ms left, it must stop before it consumes the entire request. A response that arrives after the caller's timeout is too late to help the caller and may still consume server resources.

Retries are useful for short, transient failures such as a connection reset or a temporary overload. They are dangerous when the operation is not idempotent, because a timeout can hide a successful server-side effect. A retry policy therefore includes which failures qualify, the maximum attempts, the deadline, and whether the operation has an idempotency key. A blind retry of a payment can charge twice.

Exponential backoff increases the delay after each failed attempt, such as 100 ms, 200 ms, and 400 ms. **Jitter** randomizes each delay so many clients do not wake at the same instant. Full jitter chooses a random value between zero and the current backoff cap. Retries remain inside the caller's timeout budget, and a retry budget can cap the fraction of requests that are retries so new traffic still reaches a recovering service.

A **circuit breaker** has three states. **Closed** permits calls and measures failures. **Open** fails fast without contacting the dependency. **Half-open** permits a limited number of trial calls; success closes the circuit, while failure opens it again. The failure threshold and open interval must fit the dependency's recovery behavior. A circuit breaker protects a caller, but it does not repair the dependency or make a partial result correct.

A **bulkhead** is a separate resource limit for each dependency, customer tier, region, or operation. Each partition gets a bounded connection pool, queue, or worker count. One tenant exhausting its own quota then fails predictably instead of starving every other tenant. Bulkheads can be implemented in a gateway, service-mesh policy, thread pool, or application queue, but the limit must be observable.

```yaml
resilience_policy:
  orders_to_payments:
    timeout: 350ms
    circuit_breaker:
      failure_ratio: 0.5
      minimum_requests: 20
      open_for: 30s
      half_open_requests: 3
    retry:
      attempts: 2
      eligible: [connection_reset, temporary_overload]
      not_eligible: [invalid_request, authorization_failure]
      backoff: exponential_full_jitter
      base_delay: 100ms
      maximum_delay: 1s
  bulkheads:
    payments_default: 80
    payments_premium: 20
    orders_default: 120
```

The execution order matters. A gateway can reject excessive traffic before it reaches the service. The service applies its own deadline and bulkhead. The client library applies the circuit breaker and retry policy. The dependency can apply admission control and shed load. When every layer retries independently, a slow dependency can receive more traffic than it originally received, so the system needs a shared retry budget or an explicit propagation rule.

A timeout policy should be observable. Record the dependency, caller operation, deadline, outcome, retry count, and circuit state without logging credentials or sensitive payloads. Alert on error-budget burn, saturation, and breaker state, not merely on a single failed request. Resilience patterns are controls around failure; they do not remove the need for capacity planning, idempotency, or an incident runbook.

## Tradeoffs

| Pattern | Gain | Cost or limitation |
| --- | --- | --- |
| Deadline propagation | Prevents nested calls from outliving the user-visible request | Requires cooperation across libraries, services, and queues |
| Retry with backoff and jitter | Recovers some transient failures without synchronized retries | Adds latency, duplicate work, and retry traffic |
| Circuit breaker | Fails fast and gives a failing dependency breathing room | May reject recoverable requests and needs a recovery policy |
| Bulkhead | Contains overload and noisy-neighbor effects | Splits capacity and can leave resources underused |
| Queue-based load leveling | Absorbs bursts and protects downstream services | Adds delivery delay, backlog, and replay responsibilities |
| Load shedding | Preserves capacity for essential work | Rejects work and needs priority and user-facing behavior |

## When to use

- A remote dependency can fail or slow down enough to exhaust your request, connection, or worker capacity.
- A user-visible operation needs a strict latency deadline across several network calls.
- A transient failure is safe to retry and the operation is idempotent or has an idempotency key.
- One tenant, endpoint, or region can consume a shared resource needed by other work.
- You need to test degraded behavior with deliberately slow or unavailable dependencies.

## Alternatives

- **No retries** — preserves request latency and avoids duplicate effects, but turns a brief blip into a user-visible failure.
- **Fixed-delay retries** — are simple, but synchronized clients can create a retry storm after recovery.
- **A single global worker pool** — is simple to operate, but one slow dependency can starve unrelated operations.
- **Longer timeouts** — may allow slow work to finish, but ties up capacity and often violates the caller's latency target.

## Related

- [Enterprise Architecture Patterns: Monoliths, Microservices, Service Mesh, BFF, Strangler Fig, and Cell-Based Architecture](01-enterprise-architecture-patterns.md)
- [Domain-Driven Design & Event Architectures: Bounded Contexts, CQRS, Event Sourcing, and Transactional Outbox](02-domain-driven-event-architectures.md)
- [Fundamentals of System Design: Latency, Throughput, Availability, and SLA/SLO/SLI](../01-system-design-fundamentals/01-fundamentals.md)
- [Message Delivery Guarantees: At-Most-Once, At-Least-Once, and Exactly-Once (Idempotency Patterns)](../../03-messaging/01-messaging/03-delivery-guarantees.md)
