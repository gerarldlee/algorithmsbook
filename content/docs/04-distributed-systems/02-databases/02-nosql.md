---
title: "NoSQL Classifications: Key-Value, Document, Columnar (Cassandra), and Graph Databases (Neo4j)"
weight: 2
toc: true
---

## What it is

NoSQL databases are non-relational stores organized around access patterns rather than a fixed multi-table schema. The major families are key-value, document, wide-column, and graph stores, with different models for keys, values, relationships, consistency, and horizontal partitioning.

## How it works

A key-value store maps a unique key to an opaque value. The database can resolve a key quickly, but the application interprets the value and performs any secondary lookups. Redis commonly serves this role for cache-like data, while DynamoDB adds a durable, partitioned key-value service with configurable durability and read consistency.

A document store persists an independently addressable JSON-like document. The document model supports nested attributes and flexible schemas, but updates that span documents usually need application coordination. MongoDB and CouchDB use this model, and Firestore provides a document-oriented service with server-side rules and transactions.

A wide-column store represents rows with sparse columns grouped into column families. Cassandra partitions rows by a distribution key and orders the rows within a partition, so its strongest designs align writes and queries with that partition and clustering order. It avoids a general-purpose join engine in favor of bounded access paths.

A graph store represents entities as nodes and relationships as edges. Neo4j and Neptune can traverse multi-hop paths directly, which is useful for recommendations, fraud analysis, and dependency graphs. The application still chooses the identifiers and properties that keep traversals bounded.

```yaml
families:
  key_value:
    examples: [Redis, DynamoDB, etcd]
    access: exact_key
    consistency: configurable_by_service
  document:
    examples: [MongoDB, CouchDB, Firestore]
    access: key_plus_document_fields
    consistency: document_or_transaction_scope
  wide_column:
    examples: [Cassandra, HBase, Bigtable]
    access: partition_plus_clustering_range
    consistency: quorum_or_local
  graph:
    examples: [Neo4j, Neptune, JanusGraph]
    access: relationship_traversal
    consistency: transaction_or_application_defined
partitioning:
  common_key: explicit_distribution_key
  replication: usually_physical_and_automatic
```

## Tradeoffs

| Property | Gain | Cost |
| --- | --- | --- |
| Flexible model | The application can evolve records without changing every table | Validation and cross-record invariants move into application code |
| Partition-local access | A request can be routed to one shard by its key | Queries spanning partitions need fan-out or separate indexes |
| Specialized model | The engine can optimize one workload instead of every relational operation | A different model is required for unrelated access patterns |
| Configurable consistency | You can choose latency or stronger coordination per operation | Predicting anomalies and conflict resolution requires explicit design |
| Automatic scale-out | Nodes can be added when partitions or replication factors require them | Capacity, compaction, and topology still need operational care |

## When to use

- You need high-throughput key lookups or caches with a simple value model.
- The primary aggregate is a document whose shape changes with the application.
- You can express the workload as partition-local reads, writes, or relationship traversals.
- You can state the consistency and conflict behavior that each operation requires.

## Alternatives

- **Relational databases** — strong constraints and expressive joins, with more coupling between schema and workload.
- **NewSQL databases** — distributed SQL with transactions and familiar query semantics, but more coordination and operational complexity.
- **Search engines** — inverted indexes and relevance ranking, with a document-oriented model but different durability and transaction guarantees.
- **Columnar analytical databases** — efficient scans and aggregation, with a less natural fit for transactional point updates.

## Related

- [Relational Data Modeling, Normalization, and Indexing Strategies (B-Tree, Hash, GIN, GiST)](01-relational-modeling.md)
- [Storage Engines: OLTP (Row-Oriented) vs OLAP (Columnar/Parquet/ClickHouse)](03-storage-engines.md)
- [Database Replication (Leader-Follower, Multi-Leader, Leaderless/Dynamo-Style)](05-replication.md)
- [Partitioning & Sharding Strategies: Range, Hash, List, and Directory-Based Sharding](06-sharding.md)
