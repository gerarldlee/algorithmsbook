---
title: "Reverse Proxies, API Gateways, and Edge Routing (Nginx, Envoy, Traefik)"
weight: 4
toc: true
---

## What it is

Proxies and gateways are intermediaries that accept traffic and route or transform it toward another destination. A **forward proxy** represents outbound clients, a **reverse proxy** represents backend servers, an **API gateway** applies API lifecycle policy, and **edge routing** uses proximity-aware DNS, anycast addresses, or edge networks to select an ingress point.

## How it works

An ingress request first reaches an edge router, then a reverse proxy or API gateway, and finally a backend service. The reverse proxy terminates TLS, selects a healthy pool, forwards headers, and may cache responses. The API gateway adds authentication, quotas, request validation, protocol transformation, and routing across services. In the opposite direction, a forward proxy applies egress allowlists, inspection, and audit policy before opening an outbound connection. A service mesh extends proxy-mediated control to service-to-service calls through sidecars or ambient data-plane components.

Traefik's dynamic file configuration expresses edge routing as host rules that terminate TLS and select backend services:

```yaml
http:
  routers:
    api-router:
      entryPoints:
        - websecure
      rule: Host(`api.example.com`) && PathPrefix(`/v1/`)
      tls: {}
      service: api-service
    web-router:
      entryPoints:
        - websecure
      rule: Host(`www.example.com`)
      tls: {}
      service: web-service
  services:
    api-service:
      loadBalancer:
        servers:
          - url: http://api-v1:8080
          - url: http://api-v2:8080
    web-service:
      loadBalancer:
        servers:
          - url: http://web:80
```

Nginx is widely used for reverse-proxy and static delivery configuration. Envoy provides a programmable data plane used by load balancers and service meshes, including listeners, routes, clusters, health checks, and telemetry. Traefik derives routes from labels or provider configuration and integrates well with container platforms. These products can occupy the same logical layer, so architecture should define ownership boundaries rather than deploy every feature in every proxy.

**Edge routing** first chooses a nearby or fault-isolated ingress, then forwards the request to a regional or origin tier. Server Name Indication can select a certificate before HTTP routing, while geolocation or company identity can constrain the eligible origins. Cache keys must include every header that changes the response, and any regional failover must preserve the API's consistency and data-residency rules.

## Tradeoffs

Choose intermediaries by the policy boundary they need to own:

| Component | Central gain | Central cost | Prefer when |
| --- | --- | --- | --- |
| Reverse proxy | One public address, TLS termination, caching, and backend selection | Adds a network hop and a shared failure domain | Many clients need uniform ingress behavior |
| API gateway | Central authentication, quotas, validation, and API routing | Can become a latency bottleneck or a platform coupled to every service | Several internal capabilities form a managed public API |
| Forward proxy | Auditable and enforceable outbound access | Can constrain direct networking and must handle protocol exceptions | Organization must control egress destinations |
| Edge router | Reduces network distance and can isolate regions | Requires cache invalidation, global traffic policy, and data-consistency design | Users are geographically distributed or need static-content acceleration |
| Service mesh data plane | Uniform mTLS, telemetry, and resilience policy | More processes, configuration, CPU, and failure modes | A large service fleet needs centrally managed east-west policy |
| In-process gateway library | Removes a proxy hop | Each language and service must maintain equivalent policy | A small, homogeneous fleet values direct connections over central control |

Separate routing from business logic. A gateway should validate and route requests, while domain rules remain in the owning service; otherwise every contract change becomes a coordinated gateway release.

## When to use

- You need one stable public entry point with TLS termination and backend health checks.
- You expose several backend capabilities through a managed API contract.
- You must enforce authentication, quotas, or auditing before traffic reaches applications.
- You need domain, geography, or data-residency policies at an edge ingress.
- You operate enough services to justify a centrally configured service-mesh data plane.

## Alternatives

- **Direct client-to-service connections** — remove proxy hops, but expose topology and duplicate security and routing logic across clients.
- **Application libraries** — keep calls in process, but require every service to adopt and test the same resilience and security behavior.
- **A CDN without an origin proxy** — accelerates cacheable static content, but cannot provide dynamic authentication or application-aware origin routing.

## Related

- [Load Balancing Strategies](03-load-balancing.md)
- [Network Protocols](02-network-protocols.md)
- [API Paradigms: REST, GraphQL, gRPC Protocol Buffers, and Event-Driven Systems](05-api-paradigms.md)
- [Cryptography & System Security: TLS/SSL, PKI, Symmetric/Asymmetric Encryption, KMS, OAuth 2.0/OIDC, and Zero-Trust Architecture](06-cryptography-system-security.md)
- [Enterprise Architecture Patterns: Monoliths, Microservices, Service Mesh, BFF, Strangler Fig, and Cell-Based Architecture](../02-software-architecture-patterns/01-enterprise-architecture-patterns.md)
- [Content Delivery Networks (CDNs), Edge Computing, and Static/Dynamic Content Acceleration](../02-caching/03-cdns-edge.md)
