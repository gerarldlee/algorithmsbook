---
title: "Serverless & Edge Computing (AWS Lambda, Cloudflare Workers, Event-Driven Triggers)"
weight: 4
toc: true
---

## What it is
Serverless is a compute model where you deploy code (or containers) and the cloud provider runs, scales, and bills it per invocation or per second of execution — you never provision, patch, or size a server. Despite the name, servers still exist; the point is that capacity management, scaling, and idle cost disappear behind a fully managed execution model.

## How it works
Two dominant forms are **functions**, such as AWS Lambda, and **serverless containers**, such as Amazon ECS on Fargate. A function is a short-lived handler invoked by an event such as an HTTP request, queue message, object-upload notification, or schedule. The provider keeps a runtime and its dependencies in a warm execution environment; when one is unavailable, it initializes an environment before running the handler. Fargate accepts a container image and runs it on provider-managed compute without requiring you to operate nodes, billing for the vCPU and memory time used by running tasks. Edge functions such as Cloudflare Workers run JavaScript or WebAssembly in isolates near users, which reduces network distance for request handling but imposes runtime, API, and execution-time limits different from Lambda.

```yaml
Resources:
  UploadQueue:
    Type: AWS::SQS::Queue

  ProcessLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/lambda/process-upload

  ProcessRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: process
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action: logs:CreateLogStream
                Resource: !GetAtt ProcessLogGroup.Arn
              - Effect: Allow
                Action: logs:PutLogEvents
                Resource: !GetAtt ProcessLogGroup.Arn
              - Effect: Allow
                Action:
                  - sqs:ReceiveMessage
                  - sqs:DeleteMessage
                  - sqs:GetQueueAttributes
                Resource: !GetAtt UploadQueue.Arn

  ProcessUpload:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: process-upload
      Runtime: python3.12
      Handler: index.handler
      Role: !GetAtt ProcessRole.Arn
      MemorySize: 512
      Timeout: 15
      Code:
        ZipFile: |
          def handler(event, context):
              return {"statusCode": 200}

  TriggerOnUpload:
    Type: AWS::Lambda::EventSourceMapping
    Properties:
      FunctionName: !Ref ProcessUpload
      EventSourceArn: !GetAtt UploadQueue.Arn
      BatchSize: 10
```

The execution role restricts log writes to `ProcessLogGroup` and queue actions to `UploadQueue`.

**Cold starts** are the defining operational detail: when no warm execution environment exists, the provider initializes the runtime and loads dependencies before the handler runs, adding latency. Larger runtimes and heavy imports generally increase that latency. Lambda concurrency is bounded by account and function limits, and each invocation runs in isolation. Scaling is automatic: the provider can create multiple execution environments for concurrent requests, up to the configured concurrency limit.

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
- **Fargate vs. Lambda**: Fargate runs a container without code rewrites and supports longer-running tasks, but bills for task vCPU and memory time and can be less economical for steady utilization.

## Related
- [Compute](01-compute.md)
- [Cloud Networking](03-cloud-networking.md)
- [Infrastructure as Code](05-infrastructure-as-code.md)
- [Observability Platforms: Structured Logging, Metrics (Prometheus), Distributed Tracing (OpenTelemetry), and Alerting](../02-containers-cicd/05-observability.md)
