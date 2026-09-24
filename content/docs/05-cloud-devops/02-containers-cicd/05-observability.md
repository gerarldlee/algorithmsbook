---
title: "Observability"
weight: 5
toc: true
---

## What it is
Observability is the ability to understand a system's internal state from its external outputs — logs, metrics, and traces — especially when failures or unexpected behavior occur. It extends monitoring (alerting on known failures) toward answering arbitrary questions about unknown failure modes, and is expressed concretely through Service Level Objectives (SLOs) and telemetry pipelines built on Prometheus, Grafana, and OpenTelemetry.

## How it works
The three telemetry pillars capture different signals: **logs** record discrete events with context, **metrics** aggregate measurements over time (counters, gauges, histograms), and **traces** record a request's path across services with timing per span. A modern stack collects metrics with Prometheus (a pull-based time-series database and alerting engine), visualizes with Grafana, and standardizes instrumentation and transport with OpenTelemetry, which emits correlated traces, metrics, and logs from a single SDK.

```yaml
# OpenTelemetry + Prometheus + Grafana collection architecture
# Service instruments with OTel SDK -> OTel Collector -> backends
receivers:
  otlp:            # accepts OTLP traces/metrics/logs
    protocols: { grpc: {}, http: {} }
  prometheus:      # scrapes Prometheus-format metrics
    config: { scrape_configs: [ { job_name: "app", static_configs: [ { targets: ["app:9090"] } ] } ] }
processors:
  batch:
    timeout: 5s
exporters:
  prometheusremotewrite: { endpoint: "http://prometheus:9090/api/v1/write" }
  otlp/trace: { endpoint: "tempo:4317", tls: { insecure: true } }
  loki: { endpoint: "http://loki:3100/loki/api/v1/push" }
service:
  pipelines:
    traces:  { receivers: [otlp], processors: [batch], exporters: [otlp/trace] }
    metrics: { receivers: [otlp, prometheus], processors: [batch], exporters: [prometheusremotewrite] }
    logs:    { receivers: [otlp], processors: [batch], exporters: [loki] }
```

SLOs tie observability to business goals: an SLO sets a target (e.g., 99.9% availability over 30 days), SLIs are the underlying measurements (error ratio, latency percentiles), and error budgets quantify how much failure is tolerable before feature work must pause. Alerting fires on SLO burn-rate rather than individual spikes to reduce noise.

## Tradeoffs
- **Cardinality**: high-cardinality labels (user IDs, request IDs) give rich querying but blow up Prometheus memory and cost; keep high-cardinality data in logs/traces instead.
- **Sampling**: head-based trace sampling controls cost but can drop the very rare traces you need; tail-based sampling keeps interesting traces but requires a sampling-capable pipeline.
- **Cost vs coverage**: verbose logging and unsampled traces are invaluable in incidents but expensive to store and retain; retention and aggregation are constant tuning knobs.
- **Correlation**: OTel standardizes cross-signal correlation (trace ID in logs), but adopting it means instrumenting every service and maintaining a collector fleet.
- **Alert fatigue**: alerting on raw metrics causes noisy pages; SLO burn-rate alerts reduce noise but require clear SLO ownership and error budgets.

## When to use
- Operating distributed, containerized services where a single request spans many processes and hosts.
- Establishing SLOs and error budgets to make objective decisions about reliability versus feature velocity.
- Standardizing telemetry across many teams and languages via a single instrumentation SDK (OpenTelemetry).

## Alternatives
- **Log-only + grep (ELK)**: simpler to start, but lacks the aggregation and correlation of metrics/traces for complex distributed debugging.
- **APM SaaS (Datadog, New Relic)**: fast time-to-value and managed backends, at significant per-host cost and vendor lock-in.
- **Distributed tracing-only tools (Zipkin, Jaeger)**: focused trace analysis, but you still need separate metrics/logs systems and correlation plumbing.

## Related
- [Deployment Strategies](03-deployment-strategies.md)
- [CI/CD and GitOps](04-cicd-gitops.md)
- [Kubernetes](02-kubernetes.md)
- [Serverless](../01-cloud-primitives/04-serverless.md)
