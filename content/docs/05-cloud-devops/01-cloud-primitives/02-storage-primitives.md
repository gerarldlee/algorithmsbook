---
title: "Storage Primitives"
weight: 2
toc: true
---

## What it is
Cloud storage primitives are managed data services that persist bytes across three fundamental access models: **block** (raw volumes mounted like a disk), **file** (shared filesystems with a directory hierarchy), and **object** (flat key–value blobs addressed over HTTP). Each model trades latency, sharing, and cost differently, and most platforms also layer **tiers** and **snapshots** on top.

## How it works
- **Block storage (EBS)** attaches a virtual disk to a single instance in one availability zone. It is accessed at the sector level over a SAN, giving low-latency random I/O, and supports volume types from cheap magnetic/HDD up to high-IOPS NVMe SSD. Snapshots copy only changed blocks to object storage and are the basis for backup and volume cloning.
- **File storage (EFS/NFS)** presents a POSIX filesystem mountable by many instances at once. It scales capacity and throughput with usage, keeps strong consistency, and is billed per byte stored — ideal for shared directories, home dirs, and apps that need a filesystem.
- **Object storage (S3)** stores immutable objects (files + metadata) in a flat namespace of buckets and keys, served over HTTP with 11 nines of durability via erasure coding and replication. Reads/writes are per-object (no random byte edits), and access tiers trade retrieval cost for storage price.

```yaml
# The three storage models side by side
block:  # EBS — raw virtual disk, one AZ, one instance
  type: gp3 | io2 | st1 | sc1
  io: low-latency random read/write, sector level
  sharing: single instance in one AZ
  persistence: detached from instance lifecycle; snapshots to object store

file:   # EFS — shared POSIX filesystem
  protocol: NFSv4
  sharing: thousands of concurrent instances across AZs
  scaling: capacity and throughput grow automatically with usage
  cost: billed per GB stored (no provisioning)

object: # S3 — flat key-value blobs over HTTP
  namespace: bucket / key
  durability: 99.999999999% (11 nines) via erasure coding
  access: whole-object GET/PUT/LIST, no random byte edits
  tiers: standard -> infrequent access -> archive (glacier)
```

Object storage **lifecycle tiers** move data automatically: *Standard* (frequent access, highest cost), *Infrequent Access* (cheaper storage, per-GB retrieval fee), *Archive/Glacier* (deeply cheap storage, minutes-to-hours retrieval), plus *Intelligent Tiering* that auto-migrates based on access patterns. Most services add **versioning**, **server-side encryption**, and **replication** across regions as first-class features.

## Tradeoffs
- **Latency vs. sharing**: block gives the lowest latency and highest IOPS but is bound to one instance/AZ; file and object are shareable across many consumers but add network and protocol overhead.
- **Access granularity**: block and file support random byte-level edits (databases, apps), while object only reads/writes whole objects — fine for media and archives, awkward for hot databases.
- **Durability vs. cost**: object storage is the most durable and cheapest per GB but has per-object access latency and eventual (or configurable) consistency; block is fast but you manage replication yourself for durability.
- **Capacity scaling**: block volumes are fixed-size and must be resized manually; file/object grow elastically but bill continuously for what you store.
- **Consistency**: modern object stores offer strong read-after-write for new objects, but cross-region replication is eventually consistent; block and file are strongly consistent locally.

## When to use
- **Block (EBS)**: boot volumes, databases, and any hot workload needing low-latency random I/O on a single instance.
- **File (EFS)**: shared datasets, container persistence, home directories, and lift-and-shift apps that expect a POSIX filesystem.
- **Object (S3)**: media, backups, logs, data lakes, static assets, and anything served over HTTP at scale with tiered cost.

## Alternatives
- **Local instance store (NVMe)**: highest performance ephemeral storage colocated with the instance, but data is lost on stop/terminate and is not replicated.
- **Managed databases / data lakes**: query-ready storage with a real engine (SQL, analytics), but more cost and less raw flexibility than plain object storage.
- **Self-managed SAN/NAS on compute**: full control and potentially lower cost at large scale, but you own replication, durability, and operations.

## Related
- [Compute](01-compute.md)
- [Cloud Networking](03-cloud-networking.md)
- [Infrastructure as Code](05-infrastructure-as-code.md)
- [Storage Engines](../../04-distributed-systems/02-databases/03-storage-engines.md)
- [Container Internals](../02-containers-cicd/01-container-internals.md)
