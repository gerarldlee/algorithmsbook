---
title: "API Paradigms: REST, GraphQL, gRPC Protocol Buffers, and Event-Driven Systems"
weight: 5
toc: true
---

## What it is

API paradigms define the contract and direction of communication between components. **REST** exposes resources through HTTP methods and representations, **GraphQL** exposes a typed graph that clients query for selected fields, **gRPC** exposes typed RPC methods serialized as Protocol Buffers, and **event-driven systems** publish facts that consumers process independently.

## How it works

REST maps a domain operation to a resource URI and an HTTP method, then uses status codes, headers, and a representation such as JSON to exchange data. GraphQL clients send operations against a schema; the server resolves the selected fields and returns matching data, usually as JSON. gRPC code generators turn a schema into typed clients and servers, and Protocol Buffers provide a compact, language-neutral wire format. Event-driven systems instead publish a domain event to durable storage or a broker; consumers acknowledge progress and may replay the event to rebuild state or trigger follow-on work.

The GraphQL contract names resources as graph fields:

```graphql
type Query {
  user(id: ID!): User
}

type User {
  id: ID!
  name: String!
  email: String!
}
```

The gRPC contract defines the same operation as a typed RPC:

```proto
syntax = "proto3";

package accounts.v1;

message GetUserRequest {
  string id = 1;
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
}

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
}
```

REST represents the same operation as `GET /users/{id}`, while an event describes something that already happened rather than commanding a receiver to perform work:

```json
{
  "eventId": "01J2YH6J8Q3P6M4N2K7R9T1V0X",
  "eventType": "user.created.v1",
  "occurredAt": "2026-09-24T12:00:00Z",
  "key": "user-123",
  "data": {
    "userId": "user-123",
    "name": "Ada"
  }
}
```

For REST, clients and intermediaries can cache responses when cache headers permit, and independent resources can evolve without exposing every internal service. GraphQL reduces accidental over-fetching for clients with different field needs, but arbitrary selections complicate HTTP caching and can trigger excessive resolver work unless query cost and data-loader controls are explicit. gRPC makes method schemas and generated types visible to build systems, but browser clients need a proxy and generic clients need tooling for discovery. In an event-driven design, the producer records that a fact occurred; the broker orders records within a partition, and consumers track offsets. Retries can duplicate delivery, so consumers need idempotent handling, schema compatibility, and a policy for poison messages. A webhook is one delivery mechanism for an event, not a substitute for the event-driven architecture itself.

## Tradeoffs

Use the interaction and deployment model together when choosing a paradigm:

| Paradigm | Gain | Cost or risk | Prefer when |
| --- | --- | --- | --- |
| REST over HTTP | Cacheable semantics, broad tooling, independent resources | Multiple calls for related data; field and contract drift across endpoints | Public resource-oriented APIs or cacheable HTTP workloads |
| GraphQL | One endpoint can serve different field selections and related data | Query-cost control, resolver N+1 patterns, and less predictable intermediary caching | Several clients need different views of a connected domain |
| gRPC with Protocol Buffers | Typed methods, compact messages, and native streaming | Browser support requires a bridge; wire traffic is less human-readable | Controlled service-to-service calls and typed internal contracts |
| Event-driven system | Producers and consumers scale and deploy independently; new consumers can use past facts | Duplicate delivery, ordering boundaries, schema evolution, and replay operations | Long-running workflows, fan-out, or decoupled integrations |
| Webhook delivery | Pushes an event directly to an HTTP endpoint without polling callbacks | The provider handles retries, signatures, and endpoint availability | The consumer exposes a stable, security-controlled HTTPS endpoint |

GraphQL and gRPC require explicit query and method limits. Event-driven systems require explicit delivery semantics. These are not formats that can be selected safely without capacity, failure, and security rules.

## When to use

- You need cacheable, resource-oriented operations with broad HTTP client support, which points to REST.
- Several client roles need different fields from connected domain data, which points to GraphQL.
- Controlled services need typed contracts, compact messages, or streaming, which points to gRPC.
- Producers and consumers need independent deployment, durable replay, or many downstream reactions, which points to events.
- A third party needs near-real-time notification through an HTTPS callback, which points to webhooks.

## Alternatives

- **Server-Sent Events** — provide simple one-way browser push over HTTP, but the server holds the connection and the model does not support arbitrary consumer groups.
- **Long polling** — works through ordinary HTTP infrastructure, but repeated empty polls consume connections and often add latency compared with streaming.
- **Command messages** — coordinate an action the receiver must perform, but couple senders to receiver-side state and workflow more tightly than a past-tense domain event.

## Related

- [Fundamentals of System Design: Latency, Throughput, Availability, and SLA/SLO/SLI](01-fundamentals.md)
- [Network Protocols](02-network-protocols.md)
- [Reverse Proxies, API Gateways, and Edge Routing](04-proxies-gateways.md)
- [Rate Limiting & Traffic Shaping: Token Bucket, Leaky Bucket, Sliding Window Log, and Counter](../02-caching/04-rate-limiting.md)
- [Queues vs Streams](../../03-messaging/01-messaging/01-queues-vs-streams.md)
