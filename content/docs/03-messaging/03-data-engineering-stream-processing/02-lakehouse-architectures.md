---
title: "Data Architecture & Lakehouse Engines: ETL vs ELT, Data Lake vs Data Warehouse vs Data Lakehouse (Apache Iceberg, Delta Lake, Apache Hudi)"
weight: 2
toc: true
---

## What it is

A data lake stores files in object storage with a schema or structure imposed by the data producer, a data warehouse provides a managed relational model for curated analytical queries, and a **lakehouse** combines object-storage economics with table-like metadata, schema evolution, and transactional controls. ETL transforms data before it reaches its destination; **ELT** loads raw data first and transforms it inside the analytical platform. Apache Iceberg, Delta Lake, and Apache Hudi are open table formats that add manifests, snapshots, schema metadata, and commit or write semantics to files in a data lake.

The lakehouse mental model is a directory of files, a **table format** that defines table metadata and commits, and a **catalog** that maps a logical table name to its current metadata or snapshot. A query engine asks the catalog to resolve a table, then reads the files selected by the table format's snapshot. The format records which files belong to the snapshot, how they are partitioned, and how they evolve; the catalog provides discovery, access control, and pointer management. This separation lets a query engine operate on the same governed data without moving every dataset into a proprietary database.

## How it works

In an ETL pipeline, source data is extracted, transformed in a staging system, and loaded into a target. Transformations can normalize names, join reference data, reject bad records, and publish a stable schema before the write. In an ELT pipeline, raw events land in object storage and SQL transformations run in the lakehouse. ELT preserves a replayable landing zone and makes the transformation visible to analysts, but it requires secure raw-data access and enough compute to rerun the transformation.

A lakehouse write normally follows this sequence:

```text
writer:
  create_files_in_a_staging_location()
  collect_file_statistics()
  add_files_to_a_manifest()
  atomically_commit_a_table_snapshot()
reader:
  resolve_snapshot_or_time_travel_version()
  prune_files_by_partition_and_statistics()
  scan_selected_columnar_files()
  return_rows_at_the_requested_consistency()
```

The table format supplies the metadata and commit mechanism for those steps, while the catalog resolves a logical table name to its current metadata or snapshot. Iceberg uses manifests and snapshots to describe table files and supports branch and tag time travel. Delta Lake records transactional actions in a Delta transaction log, enabling ACID table operations and time travel. Hudi uses commit metadata, file versions, and configurable copy-on-write or merge-on-read layouts for incremental and streaming ingestion. The implementations differ, so a table format is not a complete query engine, a catalog is not the table data itself, and an engine is not a complete storage system.

A practical catalog contract can make the separation explicit:

```yaml
lakehouse:
  landing:
    format: immutable_files
    examples: [json, protobuf, parquet]
    purpose: replayable_source_evidence
  catalog:
    purpose: resolve_logical_table_names_to_governed_metadata
    responsibilities: [discovery, access_control, current_version_pointer]
  table:
    format_options: [apache_iceberg, delta_lake, apache_hudi]
    metadata: [schema, partitions, manifest, snapshot, commit]
    storage: object_storage
  query:
    engines: [Trino, Spark, Flink, Snowflake]
    capabilities: [sql, scan, time_travel, vectorized_execution]
  governance:
    contract: [owner, schema_version, freshness, quality, retention]
    publication: commit_only_after_files_are_valid
  consistency:
    isolation: snapshot_scoped
    readers: see_a_committed_snapshot_or_a_valid_time_travel_version
```

Open table formats change the cost model, not the need for data engineering. A table can still contain duplicate records, late events, invalid types, or a semantically wrong feature. A lakehouse therefore needs ingestion keys, data-quality checks, compaction, retention, and lineage. A small files problem also appears when many jobs continually append files; compaction merges them, while partition design controls how much data a query must scan.

A common serving path keeps raw events and curated tables separate. Streaming jobs write recent changes, batch jobs recalculate history, and a serving model reads a stable snapshot. This gives analysts a replayable path while keeping operational queries predictable:

```sql
SELECT customer_id, date_trunc('day', event_time) AS day, sum(amount) AS total
FROM curated_orders
WHERE event_time >= TIMESTAMP '2026-09-01'
  AND event_time < TIMESTAMP '2026-09-02'
GROUP BY customer_id, date_trunc('day', event_time);
```

## Tradeoffs

| Design choice | Gain | Cost |
| --- | --- | --- |
| ETL | Curated target can receive clean, stable records | Upstream logic is duplicated and replay is less direct |
| ELT | Raw evidence stays available and SQL is easy to revise | Compute and storage are consumed before quality is established |
| Data lake | Cheap, scalable object storage and broad file support | Weak table semantics, discoverability, and governance without extra work |
| Data warehouse | Managed schemas, optimization, and predictable SQL | Proprietary formats, ingestion work, and higher platform coupling |
| Lakehouse | Open storage with snapshots and table-like consistency | Metadata, compaction, catalog, and format-specific operations add complexity |
| Copy-on-write table files | Simple immutable file history and predictable reads | Rewriting large files costs write amplification and storage |
| Merge-on-read table files | Faster small updates with delta files | More file planning, read work, and compaction operations |
| Streaming plus batch | Fresh results and full historical rebuilds | Two execution paths, duplicate handling, and reconciliation |

## When to use

- You need analytical scans over large event history while retaining a replayable raw landing zone.
- Different consumers need compatible tables without copying data into separate proprietary warehouses.
- You need schema evolution, time travel, or snapshot isolation for audit and correction workflows.
- You can operate object storage, a catalog, compaction, and data-quality checks.
- Batch and streaming jobs must publish to the same governed table contract.

## Alternatives

- **A single warehouse** — gives a managed analytical surface, but can couple storage, compute, and governance to one vendor.
- **Raw files without a table format** — is inexpensive and flexible, but every consumer must interpret manifests, partitions, and schema changes.
- **Change-data capture into a relational warehouse** — simplifies source updates for transactional data, but does not naturally handle very large event history or open table formats.
- **A per-team object-storage pipeline** — gives teams autonomy, but fragments data contracts, increases duplicate copies, and makes cross-domain analysis harder.

## Related

- [Stateful Stream & Batch Processing Frameworks](01-stateful-stream-batch-processing.md)
- [Data Serialization & In-Memory Formats](03-serialization-in-memory-formats.md)
- [Storage Engines: OLTP (Row-Oriented) vs OLAP (Columnar/Parquet/ClickHouse)](../../04-distributed-systems/02-databases/03-storage-engines.md)
- [Feature Stores, Dataset Versioning (DVC), and Pipeline Orchestration (Airflow, Kubeflow)](../../06-ml-ai/02-mlops/02-feature-stores-pipelines.md)
- [Distributed Query Execution, Global Secondary Indexes, and Point-In-Time Recovery (PITR)](../../04-distributed-systems/02-databases/07-distributed-query-pitr.md)
