---
title: "Proxies and Gateways"
weight: 4
toc: true
---

## What it is

Proxies and gateways are intermediaries that sit between clients and servers, forwarding, filtering, or transforming traffic. A forward proxy sits in front of clients (egress control), a reverse proxy sits in front of servers (ingress control), an API gateway is a reverse proxy specialized for managing public APIs, and a service mesh generalizes the same idea to every hop inside a datacenter via sidecar proxies.

## How it works

A reverse proxy accepts client connections, terminates TLS, and forwards requests to backend servers, often rewriting headers and caching responses. An API gateway adds API-specific concerns on the same path: authentication, rate limiting, request/response transformation, and routing to multiple backend services behind one public endpoint. A forward proxy instead receives outbound requests from clients and applies organization-level policy — allow/deny lists, logging, and caching — before reaching the internet. A service mesh deploys a sidecar proxy next to every service so that mutual TLS, retries, timeouts, and traffic splitting happen uniformly without changing application code.

The layering of these intermediaries is described below:

```yaml
# Ingress path: client -> edge -> gateway -> services
client:
  -> reverse_proxy:
      tls_termination: true
      caching: true
  -> api_gateway:
      auth: [oauth2, api_key]
      rate_limit: per_api_key
      routes:
        /users  -> user_service
        /orders -> order_service
      transform: [request_validation, response_mapping]
  -> services:
      # service mesh handles service-to-service hops
      sidecar: envoy_per_pod
      mTLS: true
      retries: [timeout=500ms, attempts=2]
egress:
  -> forward_proxy:
      policy: [allowlist_domains, logging]
```

## Tradeoffs

| Component | Benefits | Costs |
| --- | --- | --- |
| Reverse proxy | Central TLS, caching, and single entry point | One more hop and a central point of failure unless redundant |
| API gateway | One place for auth, rate limiting, and routing | Adds latency and can become an operational monolith if overloaded with logic |
| Forward proxy | Central egress policy and audit for outbound traffic | Bottleneck for all egress; can break apps expecting direct connectivity |
| Service mesh (sidecars) | Uniform mTLS, retries, and observability | Doubles proxy count, adds latency and significant operational complexity |

## When to use

- Use a reverse proxy to terminate TLS, cache responses, and hide backend topology behind one address.
- Use an API gateway when you expose many internal services through a single public API and need central auth, rate limiting, and routing.
- Use a forward proxy for corporate or security-controlled outbound access (allow-listing, egress auditing).
- Use a service mesh when you have many internal services needing consistent mTLS, retry, and observability policies.

## Alternatives

- **Direct client-to-service connections** — lowest latency and fewest moving parts, but no central auth, caching, or policy enforcement.
- **Library-based resilience (no sidecar)** — avoids extra proxy hops, but requires every service to adopt and version the same libraries.

## Related

- [System Design Fundamentals](01-fundamentals.md)
- [Load Balancing](03-load-balancing.md)
- [Network Protocols](02-network-protocols.md)
- [API Paradigms](05-api-paradigms.md)
- [Rate Limiting](../02-caching/04-rate-limiting.md)
