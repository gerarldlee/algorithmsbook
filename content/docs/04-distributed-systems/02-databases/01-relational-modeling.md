---
title: "Relational Modeling"
weight: 1
toc: true
---

## What it is
Relational modeling organizes data into normalized tables (relations) of rows and columns, linked by primary/foreign keys and queried with declarative SQL. The schema is fixed up front and enforced by the database, favoring consistency and integrity over schema flexibility.

## How it works
A logical entity model is decomposed into tables to remove redundancy through normalization (1NF/2NF/3NF, optionally BCNF). Each table declares a primary key that uniquely identifies a row; relationships are represented by foreign keys referencing another table's primary key. Queries join tables on those keys, and secondary indexes are added on columns used in frequent `WHERE`, `ORDER BY`, and join predicates to avoid full scans. The physical design — index choice, denormalization for read-heavy paths — is tuned after the logical model stabilizes.

```yaml
# Logical design, then physical tuning
entities:
  orders:
    primary_key: order_id
    foreign_keys: [customer_id -> customers.id]
    indexes: [order_date, customer_id]
  order_items:
    primary_key: [order_id, line_no]
    foreign_keys: [order_id -> orders.id, product_id -> products.id]
    indexes: [product_id]
normalization:
  level: 3NF           # eliminate transitive & partial dependencies
  exceptions:          # deliberate denormalization for hot reads
    - cached_total_on_order
joins:
  - orders join order_items on order_id   # index-backed nested loop / hash join
```

## Tradeoffs
| Property | Characteristic |
| --- | --- |
| Consistency & integrity | Strong: constraints, unique/foreign keys, and transactions enforce invariants centrally. |
| Schema evolution | Rigid; migrations (DDL) are costly on large tables and require lock/in-place rebuild care. |
| Horizontal scaling | Harder: joins and foreign keys do not partition naturally; sharding breaks cross-row constraints. |
| Query flexibility | High for the known schema (rich SQL), low for heterogeneous/rapidly changing shapes. |
| Read/write latency | Predictable via indexes, but join and index-maintenance overhead grows with write volume. |

## When to use
- Data with stable, well-understood structure and strong relationships (orders, accounts, inventory).
- Workloads needing multi-table joins, aggregate analytics over structured data, and referential integrity.
- Systems where correctness of cross-row invariants (unique constraints, foreign keys) matters more than write throughput.

## Alternatives
- Document databases (MongoDB) — schema-flexible, fast for single-entity reads, but weak cross-document joins/constraints.
- Key-value stores (Redis) — lowest latency for point lookups, no relational queries or integrity checks.
- Graph databases (Neo4j) — efficient deep-relationship traversal, weaker general-purpose aggregation.

## Related
- [NoSQL Databases](02-nosql.md)
- [Storage Engines](03-storage-engines.md)
- [ACID and Isolation Levels](04-acid-isolation.md)
- [Replication](05-replication.md)
