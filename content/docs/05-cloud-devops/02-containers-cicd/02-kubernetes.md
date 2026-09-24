---
title: "Kubernetes"
weight: 2
toc: true
---

## What it is
Kubernetes (K8s) is an open-source container orchestration platform that schedules and manages containerized workloads across a cluster of machines, maintaining a declarative desired state. It abstracts individual hosts behind an API, providing self-healing, scaling, service discovery, and rolling updates as built-in controllers.

## How it works
A cluster has a **control plane** (API server, etcd state store, scheduler, controller manager) and **worker nodes** (kubelet, container runtime, kube-proxy). Users and operators submit declarative objects — Pods, Deployments, Services, Ingresses — to the API server; controllers reconcile the actual state toward the desired state stored in etcd in a continuous control loop. The scheduler assigns each Pod to a node; the kubelet starts and monitors its containers.

```yaml
# Declarative desired state: Deployment -> ReplicaSet -> Pods
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels: { app: web }
  template:
    metadata:
      labels: { app: web }
    spec:
      containers:
        - name: web
          image: ghcr.io/example/web:1.4.0
          resources:
            requests: { cpu: "250m", memory: "128Mi" }
            limits:   { cpu: "500m", memory: "256Mi" }
---
# Stable cluster-internal endpoint for the Pods
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector: { app: web }
  ports:
    - port: 80
      targetPort: 8080
---
# External HTTP routing into the Service
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
spec:
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: { name: web, port: { number: 80 } }
```

Controllers watch for drift: a crashed Pod is replaced by the ReplicaSet controller, the Horizontal Pod Autoscaler scales replicas on CPU/memory metrics, and the EndpointSlice controller keeps the Service pointed at healthy Pods. Scheduling uses resource `requests`/`limits` and taints/tolerations to place Pods, while namespaces, RBAC, and network policies provide multi-tenancy and isolation.

## Tradeoffs
- **Consistency model**: strong, eventually-consistent convergence toward desired state gives self-healing, but the reconcile loop introduces delay between a change and its full effect.
- **Operational complexity**: standardized APIs and a huge ecosystem, but the control plane (etcd, upgrades, certs) is a significant operational burden — many teams prefer managed offerings (EKS/GKE/AKS).
- **Resource efficiency**: bin-packing and autoscaling improve utilization, but requests/limits must be tuned correctly or workloads are throttled or waste capacity.
- **Networking**: Service/Ingress abstract routing well, but the overlay/CNI layer adds latency and troubleshooting complexity.
- **Multi-tenancy**: namespaces and RBAC enable sharing, but real isolation between tenants is weaker than VMs and needs careful network policy.

## When to use
- Running a large, heterogeneous set of containerized services that need self-healing, scaling, and rolling deployments.
- Standardizing deployment and operations across teams and clouds via a common API and declarative manifests.
- Workloads that benefit from automatic bin-packing, horizontal autoscaling, and service discovery.

## Alternatives
- **Docker Compose / docker run**: far simpler for a single host, but no scheduling, self-healing, or scaling across machines.
- **Nomad**: simpler single-binary orchestrator with a lower operational footprint, but a smaller ecosystem and less native integration.
- **Serverless / Fargate**: no cluster or node management at all, at the cost of less control and higher per-invocation pricing for steady traffic.

## Related
- [Container Internals](01-container-internals.md)
- [Deployment Strategies](03-deployment-strategies.md)
- [Compute](../01-cloud-primitives/01-compute.md)
- [CI/CD and GitOps](04-cicd-gitops.md)
