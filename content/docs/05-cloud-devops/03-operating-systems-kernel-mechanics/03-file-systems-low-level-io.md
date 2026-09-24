---
title: "High-Performance File Systems & Low-Level I/O: Inodes, File Descriptors, POSIX I/O, Page Cache, Journaling, `epoll` vs `kqueue`, and `io_uring` Asynchronous Ring Buffers"
weight: 3
toc: true
---

## What it is

A file system is a durable, named data model backed by kernels, block devices, and storage caches. POSIX provides the common file-descriptor interface, readiness APIs such as Linux `epoll` and BSD/macOS `kqueue` report when a descriptor can be attempted, and Linux `io_uring` submits operations through shared rings for completion-oriented I/O.

## How it works

A path such as `/srv/orders/day-1.json` is resolved component by component. A **dentry** caches a parent-directory and name relationship, while an **inode** stores metadata and identifies the underlying object, such as a regular file. Different paths can reach the same inode through hard links. Opening a path creates a file descriptor in the process descriptor table; a descriptor references an open file description that stores state such as the current offset. `fork` copies descriptor-table entries that refer to the same open descriptions, whereas `dup` adds another descriptor to one existing description.

POSIX calls separate the identity of a descriptor from an operation. `open` obtains a descriptor, `read` and `write` copy bytes through the current offset, `pread` and `pwrite` supply an explicit offset, and `lseek` changes the current offset. POSIX describes the interface; it does not force every filesystem to store files the same way. Ext4, XFS, Btrfs, ZFS, network filesystems, and FUSE can all present similar calls with different consistency, durability, and performance behavior.

Linux's **page cache** holds file-backed data pages that were read or written. A cache hit avoids a storage read, while a write usually updates the page cache before its data reaches durable media. `fsync` asks the kernel to complete a file's required durability work, but the guarantee depends on the filesystem mode, mounted device, storage cache, and hardware failure model. Calling `fsync` does not make every file or directory update part of the same atomic transaction. Direct I/O can avoid or constrain the page cache for eligible aligned operations, at the cost of alignment, size, and application-buffering complexity.

A metadata **journal** records operations before or during a transaction so a crash during a multi-step update can be rolled forward or rejected. Write ordering and barriers determine how data-file updates, metadata, and device caches are coordinated. Journaling protects filesystem structure; backups and replication still determine recovery from media loss, corruption, or deletion.

When an application waits on many sockets, polling every descriptor wastes work on entries that are not ready. Linux `epoll` and BSD/macOS `kqueue` maintain registered interest sets and return ready descriptors. `epoll` supports level-triggered and edge-triggered operation; an edge-triggered consumer must drain or otherwise handle state until the next event. Readiness is an observation, not a reservation: another consumer can take the data, or an error, hangup, or priority condition can change the outcome before the application calls `read` or `write`. A nonblocking descriptor should therefore still be attempted, and `EAGAIN` or `EWOULDBLOCK` must return the descriptor to the wait set. End-of-file and errors are results, not proof that a read succeeded.

`io_uring` uses a **submission queue** for work descriptors called SQEs and a **completion queue** for completion entries called CQEs. User space and the kernel share mapped ring memory. A process can submit many filesystem, network, and timer operations in a batch, then consume completions. Some operations complete inline and others run asynchronously. Batching amortizes entry and exit costs, but queue depth, memory registration, filesystem support, and completion policy still determine throughput and tail latency.

A blocking diagnostic can show the actual call path and timestamps:

```bash
findmnt -T /var/lib/orders
stat /var/lib/orders/day-1.json
strace -T -e trace=openat,read,write,pread64,pwrite64,fsync /usr/bin/find /var/lib/orders
```

## Complexity

These bounds describe visible algorithmic work, not disk, network, or filesystem latency. Directory layout and the selected filesystem can make path lookup and write costs more expensive than the table alone suggests.

| Operation | Work bound | Important cost outside the bound |
| --- | --- | --- |
| Descriptor-table lookup | `O(1)` | Cache and kernel locking |
| Path component lookup | `O(1)` per component with an effective directory index | Directory depth, collisions, and filesystem structure |
| Cached `read` or `write` of `k` bytes | `O(k)` | Memory bandwidth and copy behavior |
| Uncached read of `k` bytes | `O(k)` plus storage I/O | Readahead and device queueing |
| Scan `r` descriptors with `poll` | `O(r)` | Kernel transitions and scheduler behavior |
| Wait for an active interest set | Proportional to registrations and returned ready events | `epoll` and `kqueue` internal data-structure details are implementation-dependent |
| Submit `n` SQEs and drain their completions | `O(n)` application work | Kernel execution, I/O, and completion batching |
| Copy between bounded `k`-byte buffers | `O(k)` work | Number of copies dominates memory traffic |

## When to use

- The application needs a durable namespace, shared file access, or random access to file data.
- POSIX calls are sufficient and blocking behavior fits the service model.
- A connection server needs a scalable way to wait for many descriptors.
- You need to measure page-cache, syscall, journaling, and storage behavior before optimizing.
- The Linux workload can benefit from batched completion-oriented operations.

## Alternatives

- **Memory-mapped files** — can reduce explicit copying and enable page-based access, but page faults, mapping lifetime, and cross-platform behavior complicate correctness.
- **Blocking threads or synchronous calls** — are easy to reason about, but each active operation can consume a thread and a context switch.
- **`select` or `poll`** — are portable and simple, but scanning the full descriptor set can waste CPU as concurrency grows.
- **Kernel-bypass networking** — can reduce copies and queues for supported devices, but sacrifices portability, kernel scheduling, and some compatibility.
- **Object storage APIs** — win for durable blobs accessed over a network, but they do not provide a local filesystem namespace or POSIX file semantics.

## Related

- [Virtual Memory & Kernel Traps](02-virtual-memory-kernel-traps.md)
- [Processes & Threads](01-processes-threads.md)
- [Storage Primitives: Block Storage, Object Storage (S3), and Network File Systems](../01-cloud-primitives/02-storage-primitives.md)
- [Container Internals: Docker, OCI Runtimes, Linux Namespaces, and cgroups](../02-containers-cicd/01-container-internals.md)
