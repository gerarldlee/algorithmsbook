---
title: "API Paradigms"
weight: 5
toc: true
---

## What it is

API paradigms are the conventions for how clients request and receive data from a service, defined by the shape of the contract between caller and callee. The dominant styles are REST (resource-oriented over HTTP), GraphQL (client-specified queries against a schema), gRPC (typed binary RPC), and Webhooks (server-initiated callbacks to push events to subscribers).

## How it works

REST models the system as resources addressed by URLs and manipulated with HTTP verbs, using status codes and hypermedia for semantics. GraphQL exposes a single endpoint with a typed schema; the client sends a query selecting exactly the fields it wants and the server returns a matching JSON shape in one round trip. gRPC defines services and messages in Protocol Buffers, compiles them into client and server stubs, and invokes methods over HTTP/2 with streaming. Webhooks invert the direction: the producer makes an HTTP POST to a subscriber-registered callback URL whenever an event occurs, with the subscriber responsible for acknowledging and retrying.

The four styles side by side:

```yaml
# One domain modeled four ways
rest:
  read_user:  GET    /users/{id}            -> 200 {id, name, email}
  list_users: GET    /users?page=2          -> 200 {items: [...], next}
  create:     POST   /users                 -> 201 Location: /users/123
graphql:
  endpoint: /graphql
  query:    "{ user(id: 123) { name, email } }"
  response: { "data": { "user": { "name": "...", "email": "..." } } }
grpc:
  service:  UserService { rpc GetUser(UserRequest) returns (User); }
  wire:     protobuf over HTTP/2, unary + streaming
webhook:
  subscribe: POST /webhooks { url: "https://sub.example/hook", events: ["user.created"] }
  deliver:   POST https://sub.example/hook  { event: "user.created", ... }
  contract:  subscriber returns 2xx, producer retries with backoff
```

## Tradeoffs

| Paradigm | Strengths | Costs |
| --- | --- | --- |
| REST | Simple, cacheable, universal tooling | Over/under-fetching; many round trips for related data; contract drift |
| GraphQL | Client specifies exact fields, one round trip | Harder caching, N+1 risk, complex server resolver cost, no native CDN caching |
| gRPC | Typed schema, efficient binary, streaming | Poor browser support, needs HTTP/2, opaque to debugging/inspection |
| Webhook | Real-time push, decoupled producer | Delivery and retry responsibility, no request/response, ordering/idempotency challenges |

## When to use

- Use REST for public, resource-centric APIs where caching and simplicity matter.
- Use GraphQL when many different clients need different field subsets and want to avoid multiple round trips.
- Use gRPC for internal service-to-service calls needing high throughput and a strict typed contract.
- Use webhooks when a third party must be notified of events asynchronously without polling.

## Alternatives

- **Server-Sent Events (SSE)** — simple one-way push over plain HTTP, but unidirectional and limited to browser text streaming.
- **Polling** — trivial to implement with no callback infrastructure, but wasteful and high-latency compared to webhooks.

## Related

- [System Design Fundamentals](01-fundamentals.md)
- [Network Protocols](02-network-protocols.md)
- [Proxies and Gateways](04-proxies-gateways.md)
- [Load Balancing](03-load-balancing.md)
- [Caching Strategies](../02-caching/01-in-memory-caching.md)
