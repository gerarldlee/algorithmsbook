---
title: "Storage Engines: OLTP (Row-Oriented) vs OLAP (Columnar/Parquet/ClickHouse/Apache Arrow In-Memory Engine)"
weight: 3
toc: true
---

## What it is

A storage engine is the database layer that maps logical rows, columns, and indexes to pages, files, buffers, and durable logs. It determines the access pattern a database optimizes: row-oriented B-tree engines favor OLTP point operations, log-structured merge-tree engines favor append-heavy writes, and columnar engines favor scans and aggregations.

## How it works

A row-oriented engine such as InnoDB stores an entire row in a page and organizes secondary indexes into B-trees. A transaction records changes in a write-ahead log, updates data pages, and recovers by replaying the log after a crash. A heap-plus-index design also lets a secondary index identify rows without duplicating the complete row.

A log-structured merge-tree engine such as RocksDB accepts writes in a memtable and flushes immutable sorted tables called SSTables. Reads search the memtable and relevant SSTables, using per-table filters to skip files that cannot contain a key. Compaction merges files to control file count and read amplification. Cassandra, HBase, and many other systems use LSM families for write-heavy workloads.

Columnar OLAP engines store values by column, compress repeated values, and process only the columns referenced by a query. Parquet provides a file format for this layout, while ClickHouse is a server engine that executes queries over columnar parts. OLTP row storage remains a better fit when a transaction updates a few attributes in a small record.

```yaml
oltp_row_engine:
  examples: [InnoDB, PostgreSQL heap]
  layout: row_and_index_pages
  write_path: wal_then_page_update
  recovery: wal_replay
olap_column_engine:
  examples: [ClickHouse]
  format: columnar_parts
  write_path: append_and_merge
  read_path: predicate_pushdown_and_vectorized_aggregation
lsm_engine:
  examples: [RocksDB, LevelDB, Cassandra, HBase]
  write_path: memtable_to_sstable
  maintenance: compaction
  read_path: memtable_and_sstable_search
```

## Complexity

| Operation | B-tree page engine | LSM-tree engine | Columnar OLAP engine |
| --- | --- | --- | --- |
| Point lookup by key | O(log n) after warm pages | Depends on the workload and SSTables searched; each relevant SSTable is typically O(log s) | Usually not the primary access pattern |
| Range scan | O(log n + k) pages or index entries | Depends on overlapping SSTables and filters; output work is O(k) after per-table search and read costs | O(Σ selected column values) |
| Point update | O(log n) index work plus page write | Lookup cost depends on the workload and SSTables searched, then append or merge work remains | Higher when a column segment must be rewritten |
| Bulk append or load | Repeated page and index maintenance | Sequential writes plus eventual compaction | Efficient column-wise encoding and compression |
| Memory and disk | Buffers, pages, indexes, and WAL | Memtable, WAL, SSTables, filters, and compaction | Compressed column segments plus query intermediates |
| Amplification | Random page and index writes | Read and write amplification; compaction I/O | Column pruning and vectorized execution trade memory for throughput |

Here, `n` is the number of entries in a B-tree, `m` is the number of SSTables searched, `s` is the number of entries in one SSTable, and `k` is the number of matching entries. LSM read cost also depends on key distribution, bloom-filter effectiveness, level structure, compaction, cache behavior, and overlap. The constants also depend on page size, compression, and hardware; the table describes asymptotic work rather than a latency guarantee.

## When to use

- You need transactional point reads and writes with strong constraints and durable commits.
- You ingest events or measurements where append throughput matters more than in-place updates.
- You run analytical scans that read a small subset of columns over many rows.
- You understand the backup, compaction, and recovery behavior of the engine you choose.

## Alternatives

- **Heap plus B-tree indexes** — flexible row updates and familiar relational behavior, with page and index maintenance costs.
- **LSM-tree storage** — high write throughput and efficient sequential persistence, with read amplification and compaction overhead.
- **Columnar storage** — compression, pruning, and aggregation, with less natural behavior for small transactional updates.
- **In-memory storage** — low latency and simple access paths, with capacity and durability requirements that need explicit design.

## Related

- [Relational Data Modeling, Normalization, and Indexing Strategies (B-Tree, Hash, GIN, GiST)](01-relational-modeling.md)
- [NoSQL Classifications: Key-Value, Document, Columnar (Cassandra), and Graph Databases (Neo4j)](02-nosql.md)
- [ACID Guarantees & Transaction Isolation Levels (Read Committed, Repeatable Read, Serializable)](04-acid-isolation.md)
- [Storage Primitives](../../05-cloud-devops/01-cloud-primitives/02-storage-primitives.md)
- [Data Architecture & Lakehouse Engines](../../03-messaging/03-data-engineering-stream-processing/02-lakehouse-architectures.md)
- [Data Serialization & In-Memory Formats](../../03-messaging/03-data-engineering-stream-processing/03-serialization-in-memory-formats.md)
- [Storage Engine Trees (B-Trees and LSM-Trees)](../../01-algorithms/02-search-trees/03-storage-engine-trees.md)
