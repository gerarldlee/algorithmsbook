---
title: "Serverless"
weight: 4
toc: true
---

## What it is
Serverless is a compute model where you deploy code (or containers) and the cloud provider runs, scales, and bills it per invocation or per second of execution — you never provision, patch, or size a server. Despite the name, servers still exist; the point is that capacity management, scaling, and idle cost disappear behind a fully managed execution model.

## How it works
Two dominant forms: **functions (Lambda)** and **serverless containers (Fargate)**. A function is a short-lived handler invoked by an **event** — an HTTP request, a queue message, an object-upload notification, a schedule. The platform holds the function's runtime and dependencies in a warm environment; on a request it starts a **sandbox** (microVM, ~10 ms to spin), runs the handler, and returns. **Fargate** extends the model to containers: you submit an image, and it runs on a fully managed pool with no nodes to operate, billed per vCPU-hour and GB-hour while the task runs.

```yaml
# A Lambda wired to two event sources and a destination
Resources:
  ProcessUpload:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.12
      Handler: index.handler
      MemorySize: 512
      Timeout: 15

  TriggerOnUpload:
    Type: AWS::Lambda::EventSourceMapping
    Properties:
      FunctionName: !Ref ProcessUpload
      EventSourceArn: !GetAtt UploadQueue.Arn   # SQS messages trigger invocations
      BatchSize: 10

  HttpEndpoint:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref Api
      Target: !Sub "integrations/${Integration}"
      RouteKey: "POST /upload"
```

**Cold starts** are the defining operational detail: when no warm sandbox exists for a function, the platform must initialize the runtime and load dependencies before executing, adding hundreds of milliseconds (or more for large runtimes like JVM/.NET or heavy imports). **Concurrency** is capped per account/function, and each invocation runs in isolation with a short maximum timeout (e.g. 15 minutes), pushing long-running work to queues and step functions. Scaling is automatic and per-invocation: 1,000 concurrent requests produce up to 1,000 concurrent sandboxes, bounded by the concurrency limit.

## Tradeoffs
- **Zero idle cost vs. unpredictable latency**: you pay only for actual execution, but cold starts add tail latency and can spike P99 for sporadic or JVM-heavy functions.
- **Automatic scaling vs. control**: concurrency scales with load with no capacity planning, but you lose control over placement, instance type, and warm capacity (mitigated by provisioned concurrency, at a cost).
- **Simplicity vs. limits**: no servers to patch or size, but you hit fixed caps — timeout (15 min), payload size, `/tmp` disk, environment size, and per-account concurrency.
- **Event-driven fit vs. statefulness**: stateless, event-triggered functions compose cleanly, but stateful or long-lived connections (databases, websockets, streaming) need external state stores and careful design.
- **Vendor coupling**: deep integration with provider services speeds development but makes portability harder than container-based approaches.

## When to use
- Event-driven glue: reacting to uploads, queue messages, schedules, and API calls with small, stateless handlers.
- Spiky or sporadic traffic where paying per-invocation beats idle VM/container costs.
- Background jobs, cron tasks, and short data-processing pipelines that fit within the timeout and payload limits.

## Alternatives
- **Containers on Kubernetes/ECS**: more control, portability, and no timeout limits, but you own capacity, scaling, and idle cost.
- **VMs/EC2**: cheapest for steady, high-throughput, long-lived workloads, but slow to scale and you manage the OS.
- **Fargate vs. Lambda**: Fargate runs any container without code rewrites and longer runtimes, but bills per second even when idle and starts slower than functions.

## Related
- [Compute](01-compute.md)
- [Cloud Networking](03-cloud-networking.md)
- [Infrastructure as Code](05-infrastructure-as-code.md)
- [Container Internals](../02-containers-cicd/01-container-internals.md)
- [Inference Serving](../../06-ml-ai/02-mlops/04-inference-serving.md)
