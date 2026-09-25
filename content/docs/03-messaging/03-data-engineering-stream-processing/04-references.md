---
title: "Chapter 7A References"
weight: 4
---

These sources support the shared concepts in Chapter 7A: stream and batch execution, lakehouse table formats, and serialization boundaries.

## Books

- Tyler Akidau, Slava Chernyak, and Reuven Lax, *Streaming Systems: The What, Where, When, and How of Large-Scale Data Processing*, O'Reilly, 2018.
- Martin Kleppmann, *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Resilient, and Maintainable Systems*, O'Reilly, 2017.

## Websites

- [Apache Spark Structured Streaming guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html) — event-time processing, watermarks, windows, and stateful queries.
- [Apache Flink stateful stream processing](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/stateful-stream-processing/) and [event-time watermarks](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/event-time/generating_watermarks/) — keyed state, timers, checkpoints, and watermark behavior.
- [Apache Beam programming guide](https://beam.apache.org/documentation/programming-guide/model/) — the runner-independent stream and table model.
- [Apache Iceberg documentation](https://iceberg.apache.org/docs/latest/) — table snapshots, manifests, schema evolution, and time travel.
- [Delta Lake documentation](https://docs.delta.io/latest/index.html) — the transaction log, ACID table operations, schema evolution, and time travel.
- [Apache Hudi documentation](https://hudi.apache.org/docs/overview/) — incremental ingestion, file versions, and copy-on-write or merge-on-read layouts.
- [Apache Arrow columnar format](https://arrow.apache.org/docs/format/Columnar.html) and [Feather documentation](https://arrow.apache.org/docs/python/feather.html) — column buffers, validity data, IPC exchange, and Feather V2.
- [Protocol Buffers encoding guide](https://protobuf.dev/programming-guides/encoding/) — field numbers, wire types, and compatibility behavior.
- [Apache Avro specification](https://avro.apache.org/docs/current/specification/) and [Apache Thrift specification](https://thrift.apache.org/docs/spec) — schema models, encodings, and interface contracts.
