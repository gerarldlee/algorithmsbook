---
title: "Container Internals"
weight: 1
toc: true
---

## What it is
A container is an isolated, portable runtime for a process and its dependencies, built from a layered filesystem image and governed by the Open Container Initiative (OCI) specification. Unlike a virtual machine, a container shares the host kernel and isolates its workload using Linux namespaces (per-process view of the system) and cgroups (resource limits), so startup is near-instant and overhead is small.

## How it works
A container image is a read-only stack of filesystem layers, each produced by a `Dockerfile` instruction and addressed by a content hash. A running container is a thin read-write layer (usually an overlayfs mount) placed on top of those layers, plus a set of kernel primitives: namespaces isolate PID, mount, network, UTS, IPC, and user views; cgroups bound CPU, memory, and I/O; seccomp/AppArmor restrict syscalls. An OCI runtime (runc, containerd, CRI-O) unpacks the image, applies the namespace/cgroup configuration from an OCI bundle, and execs the entrypoint.

```yaml
# Image build description (Dockerfile -> layered image)
FROM debian:bookworm-slim          # layer 1: base OS
RUN apt-get update && apt-get install -y curl   # layer 2
COPY app /app                      # layer 3: application
WORKDIR /app
ENTRYPOINT ["/app/server"]

# OCI runtime bundle (config.json, excerpt)
process:
  args: ["/app/server"]
  env: ["PORT=8080"]
root:
  path: rootfs
linux:
  namespaces:
    - { type: pid }
    - { type: network }
    - { type: mount }
    - { type: uts }
  resources:
    memory: { limit: 536870912 }   # cgroup v2 memory limit (512 MiB)
    cpu: { quota: 100000, period: 100000 }
```

Layers are content-addressed and shared across images: two images built from the same base reuse identical lower layers, which makes pulls and disk usage efficient. Union mounting presents the stack as one coherent filesystem; writes are copied up to the container's own layer (copy-on-write), leaving the image immutable.

## Tradeoffs
- **Isolation**: strong process/filesystem isolation via namespaces, but weaker than a hypervisor — containers share the host kernel, so a kernel-level escape compromises all containers on the node.
- **Density**: no guest OS means thousands of containers per node, but a single noisy neighbor can contend for kernel and host resources beyond its cgroup (e.g., file descriptors, sockets).
- **Immutability**: layered, content-addressed images make rebuilds and rollbacks reproducible, but layer bloat accumulates and requires regular pruning and base-image updates.
- **Portability**: an OCI image runs anywhere with a compliant runtime, but images still carry OS/arch-specific binaries and must be rebuilt for ARM vs x86.
- **Startup**: milliseconds versus VM minutes, but cold image pulls to a node still take seconds-to-minutes unless layers are cached/prefetched.

## When to use
- Standardizing application delivery across dev, CI, staging, and production with identical runtime behavior.
- Packing a service and all of its dependencies into a single deployable artifact for microservices or serverless workloads.
- Running many small, resource-capped workloads on shared hosts where VM overhead is unacceptable.

## Alternatives
- **Virtual machines**: stronger isolation and full kernel control, at the cost of GB-scale images, slower boot, and lower density.
- **Unikernels / microVMs (Firecracker)**: near-container speed with a per-instance minimal kernel for stronger isolation, but a more constrained runtime and tooling ecosystem.
- **Jails/Zones (FreeBSD jails, Solaris Zones)**: OS-level virtualization with a different (older) isolation model and smaller portability story than OCI images.

## Related
- [Kubernetes](02-kubernetes.md)
- [Deployment Strategies](03-deployment-strategies.md)
- [Compute](../01-cloud-primitives/01-compute.md)
- [Serverless](../01-cloud-primitives/04-serverless.md)
