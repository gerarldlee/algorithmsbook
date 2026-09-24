---
title: "CDNs and Edge Computing"
weight: 3
toc: true
---

## What it is
A Content Delivery Network (CDN) is a globally distributed network of edge servers (points of presence, or PoPs) that cache and serve static content close to users, cutting latency and offloading origin traffic. Edge computing extends these PoPs to run application logic — compute, API handlers, and dynamic responses — on the same servers instead of only caching files.

## How it works
Requests are routed to the nearest PoP via Anycast DNS, which announces the same IP from many locations so the network converges on the closest healthy edge. On a cache hit the PoP serves the asset directly; on a miss it fetches from the origin, caches it, and replays the response. Content is either **pushed** (origin proactively uploads assets to edges) or **pulled** (edges fetch on first request). A `Cache-Control` header or CDN rule sets the TTL, and a surrogate/edge key controls invalidation. Edge functions (Cloudflare Workers, Lambda@Edge) intercept the request/response lifecycle to transform, personalize, or compute at the edge.

```yaml
# Example CDN + edge configuration (Cloudflare-style)
cdn:
  zone: example.com
  routing:
    mode: anycast            # same IP announced from every PoP
  cache:
    default_ttl: 3600        # seconds a pulled asset stays fresh
    rules:
      - match: "*.jpg"
        ttl: 86400           # immutable images cache longer
        immutable: true
      - match: "/api/*"
        cache: bypass        # dynamic API responses skip the cache
    invalidation:
      strategy: purge_by_tag # surrogate-key purge across all PoPs
  edge_function:              # runs at the PoP, near the user
    name: geo-personalize
    trigger: on_request
    actions:
      - read_header: "cf-ipcountry"
      - rewrite_path: "/region/{country}/catalog"
  origin:
    pull_protocol: https
    failover_backend: origin-failover.example.com
```

## Tradeoffs
- **Latency**: static assets served from the nearest PoP cut round-trip time from hundreds to tens of milliseconds; dynamic edge compute avoids an origin round trip entirely.
- **Freshness**: long TTLs maximize cache hits but delay propagation of updates; purge-by-tag reduces that window but invalidations still propagate asynchronously across PoPs.
- **Consistency**: each PoP holds an independent cache, so different users can briefly see different versions after an update.
- **Cost**: egress and cache fills at the edge cost money, and edge functions bill per invocation — cheaper than origin scaling but not free.
- **Operational complexity**: two layers (edge + origin) to debug, plus routing and invalidation tooling; push caching requires an explicit publish pipeline.
- **Compute limits**: edge runtimes have constrained CPU, memory, and cold-start budgets, so only lightweight, stateless logic belongs there.

## When to use
- Serving images, video, JavaScript, and other static assets to a global audience with low latency.
- Offloading traffic spikes (product launches, events) so the origin does not collapse.
- Running lightweight request-time logic — A/B flags, geolocation, authentication, header rewrites — without a full origin round trip.
- Accelerating whole-site delivery where TLS termination and caching happen at the edge.

## Alternatives
- **Self-hosted reverse proxy cache (Varnish/nginx)** — full control and lower egress cost, but only helps users near your own data centers.
- **Multi-region origin replication** — keeps dynamic data consistent and globally available, but you pay to run and sync full application stacks.
- **Cloud object storage with direct public access** — durable and cheap, but higher latency and no request-time compute.

## Related
- [In-Memory Caching](01-in-memory-caching.md)
- [Caching Patterns](02-caching-patterns.md)
- [Rate Limiting](04-rate-limiting.md)
- [Load Balancing](../01-system-design-fundamentals/03-load-balancing.md)
- [Proxies and Gateways](../01-system-design-fundamentals/04-proxies-gateways.md)
