---
title: "Chapter 6 References"
weight: 5
---

These sources cover the chapter topics in [In-Memory Caching Engines (Redis, Memcached), Data Structures, and Eviction Policies](01-in-memory-caching.md), [Application Caching Patterns: Cache-Aside, Write-Through, Write-Around, Write-Behind](02-caching-patterns.md), [Content Delivery Networks (CDNs), Edge Computing, and Static/Dynamic Content Acceleration](03-cdns-edge.md), and [Rate Limiting & Traffic Shaping: Token Bucket, Leaky Bucket, Sliding Window Log, and Counter](04-rate-limiting.md).

## Books

- *Designing Data-Intensive Applications* by Martin Kleppmann explains caching, replication, and the consistency trade-offs behind cache-aside and write-behind designs.
- *Redis in Action* by Josiah Carlson and Jeffrey Y. Miller covers Redis data structures, persistence, replication, and eviction behavior.
- *Site Reliability Engineering* by Betsy Beyer, Chris Jones, Jennifer Petoff, and Niall Richard Murphy covers caching and traffic protection as operational concerns.

## Websites

- [Redis sorted sets](https://redis.io/docs/latest/develop/data-types/sorted-sets/), [streams](https://redis.io/docs/latest/develop/data-types/streams/), [bitmaps](https://redis.io/docs/latest/develop/data-types/bitmaps/), and [HyperLogLog commands](https://redis.io/docs/latest/commands/pfcount/) document Redis structures and their trade-offs.
- [Redis eviction policies](https://redis.io/docs/latest/develop/reference/eviction/) and [Caffeine's replacement policies](https://github.com/ben-manes/caffeine/wiki/Adventures-in-Cache-Replacement) document the available eviction behavior, including ARC implementations outside Redis and Memcached.
- [Memcached](https://memcached.org/) documents the opaque key-value cache model.
- [Cloudflare Cache Rules](https://developers.cloudflare.com/cache/how-to/cache-rules/) documents edge and browser TTL policies; [WebAssembly at the edge](https://developers.cloudflare.com/workers/runtime-apis/webassembly/) documents sandboxed edge modules; [eBPF](https://ebpf.io/) documents the Linux kernel programming model used for low-level network policy.
- [Envoy's local rate-limit filter](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/local_rate_limit_filter) documents local token-bucket scope, descriptors, and filter behavior.
