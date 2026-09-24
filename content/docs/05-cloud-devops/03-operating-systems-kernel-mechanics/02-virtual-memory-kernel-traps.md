---
title: "Virtual Memory & Kernel Traps: Paging, Page Tables, Translation Lookaside Buffer (TLB), Page Faults, Swap, Syscalls, User/Kernel Transitions, Interrupts, and Signals"
weight: 2
toc: true
---

## What it is

Virtual memory gives each process its own protected address space while the kernel maps those virtual pages to physical memory or storage on demand. Paging performs that mapping, page tables describe it, the translation lookaside buffer caches recent translations, and traps such as page faults, system calls, interrupts, and signals transfer control when work requires the operating system.

## How it works

A process uses virtual addresses instead of physical frame numbers. The memory management unit divides an address into a virtual-page number and offset, consults a page table, and produces a physical frame plus the same offset. On a typical x86-64 process, the lower canonical half uses 4 KiB pages and a hierarchical page-table walk. The hierarchy keeps unused address ranges from requiring a top-level entry for every page. Other architectures, kernel configurations, huge pages, and 5-level paging use different layouts.

A **translation lookaside buffer (TLB)** is a CPU cache of recent virtual-to-physical translations. A hit avoids the page-table walk. A miss walks the levels; the TLB can then cache the result. Transparent huge pages can reduce the number of entries and translations by covering a larger contiguous region, but they increase fragmentation and copy-on-write costs. Memory-management unit costs also include cache misses, so a small TLB miss can be much slower than a TLB hit on real hardware.

When the kernel cannot supply a valid mapping, it raises a **page fault**:

1. The processor records the faulting address and reason and enters kernel mode.
2. The kernel checks whether the address is legal for the process.
3. A present-page accounting fault updates statistics or permissions.
4. A minor fault maps an already available page without storage I/O.
5. A major fault reads a file-backed, executable, or swapped-out page from storage, installs its mapping, and restarts the faulting instruction.
6. Copy-on-write, stack growth, and demand zero-filled pages also use fault handling.

**Swap** is storage reserved for resident anonymous pages that the scheduler evicts. It extends capacity but adds storage I/O and can make latency unpredictable. With the Linux memory overcommit policy, virtual allocation may succeed before physical backing exists; a later major fault can still fail if the kernel cannot obtain memory. `madvise` and memory-pressure policies can influence reclaim, but "free" virtual address space does not imply committed physical memory.

A **system call** is a controlled transition from user mode into the kernel. The calling convention places arguments and a syscall identifier in an agreed location; a trap changes privilege, the kernel validates access, the syscall performs work on a kernel stack, and a return mechanism restores user mode. Interrupts are asynchronous events, often from devices or timers, and can preempt a user or kernel thread at an interrupt-safe point. A signal is an asynchronous software notification that asks a process to run a handler, terminate, stop, or continue. Pending signals are delivered at a safe boundary rather than exactly when another process sends them.

A production host can reveal the enabled paging and memory policies without changing them:

```bash
cat /proc/sys/vm/overcommit_memory
cat /proc/sys/vm/swappiness
cat /sys/kernel/mm/transparent_hugepage/enabled
perf stat -e page-faults,minor-faults,major-faults,dTLB-loads,dTLB-load-misses sleep 10
```

## Complexity

The following bounds use a fixed-width page-table walk and count kernel or hardware operations, not device latency or cache effects.

| Operation | Time | Additional dependency |
| --- | --- | --- |
| TLB hit | `O(1)` | Cache and TLB contention |
| TLB miss | `O(d)` | `d` is the number of page-table levels walked |
| Minor page fault | `O(d)` plus page allocation | Reclaim work depends on available memory |
| Major page fault | `O(d)` plus I/O | Storage latency and amount read |
| Page-table entry change | `O(1 + c)` | `c` is the number of CPUs that must receive a TLB invalidation |
| System-call boundary | `O(1)` plus requested operation | Argument validation and syscall work |
| Interrupt or signal delivery | `O(1)` plus handler work | Interruption of the target thread |

## When to use

- Each workload needs an isolated address range and permission boundary.
- Physical memory is smaller than the sum of a process's actively addressable working sets.
- The workload benefits from demand paging, copy-on-write, or shared mappings.
- You need controlled entry into the operating system for resources or devices.
- You can measure paging, TLB, fault, and swap behavior for the target workload.

## Alternatives

- **Physical contiguous memory** — avoids translation overhead, but requires scarce contiguous RAM and gives processes little isolation.
- **Flat 4-level page tables** — are simple and fast on common hardware, but consume more entries than radix trees and can overflow address spaces with irregular mappings.
- **Radix or clustered page tables** — scale to large sparse mappings, but add a level of lookup and platform-specific management.
- **No swap or pinned memory** — avoids eviction stalls for latency-sensitive data, but reduces flexibility and can cause allocation failure sooner.
- **User-space threads and asynchronous I/O** — reduce kernel scheduling transitions, but cannot provide kernel services or a complete protection boundary by themselves.

## Related

- [Processes & Threads](01-processes-threads.md)
- [High-Performance File Systems & Low-Level I/O](03-file-systems-low-level-io.md)
- [Container Internals: Docker, OCI Runtimes, Linux Namespaces, and cgroups](../02-containers-cicd/01-container-internals.md)
