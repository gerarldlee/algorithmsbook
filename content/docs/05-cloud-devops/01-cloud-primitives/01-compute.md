---
title: "Compute"
weight: 1
toc: true
---

## What it is
Cloud compute is on-demand, pay-as-you-go access to virtualized processing capacity — VMs, containers, and specialized instance types — without owning physical servers. It is the substrate on which every other cloud primitive runs, offered at three main levels of abstraction: raw virtual machines (EC2), managed container hosts, and fully managed/serverless execution.

## How it works
A compute service slices physical hosts into **instances** using a hypervisor (for VMs) or a container runtime (for containers). You choose an **instance type** that fixes the ratio of vCPU, memory, network bandwidth, and optional accelerators (GPU, FPGA, local NVMe), then launch it from a base **image** (AMI/container image) that carries the OS and application. A **control plane** (EC2 API, autoscaling groups) tracks desired vs. running capacity: an autoscaling group scales out by launching new instances when a metric (CPU, request rate) breaches a target, and scales in by terminating them when demand falls. Provisioning models range from on-demand (pay per second) to reserved/savings plans (committed capacity at a discount) to spot (spare capacity, interruptible, ~60–90% cheaper).

```yaml
# Autoscaling group describing desired VM capacity and scaling policy
resource "aws_autoscaling_group" "web" {
  desired_capacity = 3
  min_size         = 1
  max_size         = 10
  launch_template  = aws_launch_template.web.id

  tag {
    key                 = "Name"
    value               = "web"
    propagate_at_launch = true
  }
}

resource "aws_autoscaling_policy" "scale_out" {
  name                   = "cpu-scale-out"
  autoscaling_group_name = aws_autoscaling_group.web.name
  adjustment_type        = "ChangeInCapacity"
  scaling_adjustment     = 1
  cooldown               = 300
}
```

Instance types trade off in a few dimensions: **general purpose** (balanced CPU/memory), **compute optimized** (high CPU per core), **memory optimized** (large RAM, e.g. in-memory databases), **storage optimized** (high local I/O), and **accelerated** (GPU/FPGA for ML and inference). Modern fleets add **graviton/ARM** variants that lower cost-per-core. Containers sit on top of either self-managed hosts or a managed pool (Fargate) that hides the VM entirely.

## Tradeoffs
- **Control vs. effort**: raw VMs give full control of the OS, kernel, and networking, but you own patching, hardening, and image maintenance; managed/serverless options trade control for zero host ops.
- **Pricing model**: on-demand is flexible but the most expensive per hour; reserved/savings plans cut cost but lock in commitment; spot is cheapest but interruptible with seconds of notice.
- **Scaling latency**: VM-based autoscaling takes minutes (boot + image + health checks) vs. seconds for containers and milliseconds for serverless, so steady high-throughput workloads often prefer VMs for stability.
- **Over/under-provisioning**: fixed instance sizes mean you pay for unused headroom; right-sizing needs continuous tuning of type, size, and autoscaling thresholds.
- **Isolation**: VMs offer the strongest tenant isolation (dedicated kernel); containers share a kernel and are cheaper/denser but weaker isolation boundaries.

## When to use
- Running stateful, long-lived, or OS-sensitive workloads (databases, message brokers, legacy apps) that need a stable VM environment.
- Bursty or seasonal traffic that benefits from autoscaling groups that add and remove instances automatically.
- Workloads with predictable, committed usage where reserved capacity meaningfully cuts cost.

## Alternatives
- **Containers / Kubernetes**: denser, faster to start, and portable across clouds, but with a shared kernel and an orchestration layer to operate.
- **Serverless (Lambda)**: zero capacity management and per-invocation billing, but cold starts, short timeouts, and statelessness limit long-running or stateful jobs.
- **Bare metal**: full physical hardware with maximum performance and no hypervisor overhead, but no snapshotting, slower provisioning, and full hardware ownership.

## Related
- [Storage Primitives](02-storage-primitives.md)
- [Cloud Networking](03-cloud-networking.md)
- [Serverless](04-serverless.md)
- [Container Internals](../02-containers-cicd/01-container-internals.md)
- [Kubernetes](../02-containers-cicd/02-kubernetes.md)
