---
title: "Container Orchestration: Kubernetes Architecture (Control Plane, Worker Nodes, Pods, Services, Ingress)"
weight: 2
toc: true
---

## What it is
Kubernetes is a declarative orchestration system that schedules and operates containerized workloads across a cluster. Its API represents a **desired state**, and controllers continuously compare that state with cluster reality so that workloads are scheduled, replaced, exposed, and scaled across nodes.

## How it works
A Kubernetes cluster has a **control plane** and **worker nodes**. The API server exposes the HTTP API and authenticates requests. `etcd` stores the API objects that represent desired state. The scheduler selects a node for each pending Pod, while the controller manager runs reconciliation loops such as the Deployment and ReplicaSet controllers. A worker runs `kubelet`, which asks the CRI runtime to start and monitor Pod containers, along with a Container Network Interface (CNI) plugin and other node services.

A Pod is the smallest schedulable Kubernetes object. Its containers share a network namespace and declared volumes, so a Pod is the deployment boundary when those containers must communicate directly. A Deployment manages a ReplicaSet, and the ReplicaSet controller creates or deletes Pods to match the declared replica count and pod template. The Horizontal Pod Autoscaler can change a workload's scale through its scale subresource when metrics satisfy its configured policy.

A Service provides a stable virtual endpoint and selects Pods through labels. Ingress defines host and path rules, but an ingress controller or gateway must implement those rules. NetworkPolicy objects restrict traffic when the installed CNI and policy engine support them.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: ghcr.io/example/web:1.4.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 250m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: production
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  namespace: production
spec:
  ingressClassName: nginx
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  number: 80
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-from-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

Kubernetes updates run through reconciliation rather than a single transaction across every object. A Deployment controller can create a replacement Pod before deleting an old one, while other controllers publish Service endpoints, admit resources, and collect status. This convergent model supports self-healing, but reaching the final state can involve several successful control-loop iterations.

## Tradeoffs
- **Declarative convergence** — controllers repair drift and expose one API model, but the live state can lag a write until the relevant controllers and health checks complete.
- **Scheduling efficiency** — requests, limits, affinity, and taints improve placement and utilization, but capacity depends on accurate workload demands and configured node classes.
- **Service networking** — Services abstract changing Pod addresses, but the CNI and kube-proxy or eBPF data path add components that operators must observe.
- **API scope** — a small core object model supports many controllers, but many resources, status fields, and version conversions make the system substantial to master.
- **Multi-tenancy** — namespaces, RBAC, quotas, and policies separate teams logically, but strong isolation also requires suitable CNI, storage, and node-hardening controls.
- **Operations** — the API and ecosystem standardize workload management, but upgrades, certificates, admission controllers, and cluster upgrades remain operational responsibilities for self-managed clusters.

## When to use
- You need to run containerized services across multiple machines and replace failed Pods automatically.
- You need a common deployment API across local, on-premises, and managed clusters.
- You need service discovery, horizontal scaling, or gradual workload rollout across a cluster.
- Your platform team can operate the control plane, networking, storage, upgrades, and security policy.

## Alternatives
- **Docker Compose** — a local or single-host application stack is simpler to run, but it does not provide a multi-node scheduler or self-healing control plane.
- **HashiCorp Nomad** — a smaller orchestrator can operate with a lower control-plane footprint, but it has a smaller Kubernetes-compatible API and ecosystem.
- **Amazon ECS, Azure Container Apps, or Google Cloud Run** — managed services reduce cluster operations, but portability and runtime control depend on the provider.
- **Virtual machines managed by Terraform or Ansible** — direct infrastructure automation is familiar, but application replicas, health replacement, and service routing require additional systems.

## Related
- [Container Internals: Docker, OCI Runtimes, Linux Namespaces, and cgroups](01-container-internals.md)
- [CI/CD Workflows, Automated Testing Pipelines, and GitOps Engines (ArgoCD, Flux)](04-cicd-gitops.md)
- [Observability Platforms: Structured Logging, Metrics (Prometheus), Distributed Tracing (OpenTelemetry), and Alerting](05-observability.md)
- [Deployment Strategies: Blue-Green, Canary Releases, Rolling Updates, and Shadow Deployments](03-deployment-strategies.md)
