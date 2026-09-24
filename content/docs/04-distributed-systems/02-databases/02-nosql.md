---
title: "NoSQL Databases"
weight: 2
toc: true
---

## What it is
NoSQL is a family of non-relational databases that relax the relational model — flexible schemas, no fixed joins, and horizontal scalability — in exchange for weaker consistency guarantees. The main families are key-value, document, wide-column (columnar/column-family), and graph stores.

## How it works
Each family optimizes a different access pattern. Key-value stores map a single key to an opaque value for point lookups. Document stores persist self-contained JSON-like documents, queryable by embedded fields. Wide-column stores model rows with many sparse columns grouped into column families, tuned for high write throughput and range scans across a row. Graph stores store nodes and edges natively so multi-hop relationship traversal avoids repeated joins. Most achieve scale by sharding on a key and settling for eventual consistency instead of distributed transactions.

```yaml
families:
  key-value:
    model: "key -> opaque value"
    examples: [Redis, DynamoDB, Etcd]
    best_for: point lookups, caching, low-latency counters
  document:
    model: "self-contained JSON documents"
    examples: [MongoDB, CouchDB, Firestore]
    best_for: flexible nested entities, single-entity reads/writes
  wide-column:
    model: "rows x sparse column families"
    examples: [Cassandra, HBase, Bigtable]
    best_for: high write volume, time-series, range scans by row key
  graph:
    model: "nodes + edges"
    examples: [Neo4j, Neptune, JanusGraph]
    best_for: deep relationship traversal, recommendation, fraud
  search/columnar (adjacent):
    examples: [Elasticsearch, ClickHouse]
    best_for: full-text search / OLAP aggregation
```

## Tradeoffs
| Property | Characteristic |
| --- | --- |
| Consistency | Often eventual or tunable (quorum), not serializable-by-default; no multi-record ACID across shards. |
| Schema | Flexible, evolve independently; burden of validation shifts to the application. |
| Scale-out | Excellent: shard by key, add nodes, no cross-shard joins to break. |
| Query power | Restricted to the chosen model; ad-hoc joins and cross-entity analytics are weak or absent. |
| Operational complexity | Schema-on-read, denormalization, and data duplication push logic and consistency into app code. |

## When to use
- High-volume, low-latency workloads where data shape varies per item (user profiles, session data, catalogs).
- Workloads that outgrow a single relational node and need horizontal scale with relaxed consistency.
- Access patterns dominated by key lookups, single-entity reads, or relationship traversal rather than joins.

## Alternatives
- Relational (PostgreSQL/MySQL) — ACID and rich joins, but harder to scale horizontally and less schema-flexible.
- NewSQL (CockroachDB, Spanner) — distributed SQL with strong consistency, at higher operational/complexity cost than a simple key-value store.

## Related
- [Relational Modeling](01-relational-modeling.md)
- [Storage Engines](03-storage-engines.md)
- [Replication](05-replication.md)
- [Sharding](06-sharding.md)
