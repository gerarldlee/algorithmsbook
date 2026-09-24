---
title: "CI/CD and GitOps"
weight: 4
toc: true
---

## What it is
CI/CD (Continuous Integration / Continuous Delivery) automates building, testing, and shipping software, while GitOps extends that automation to operations by treating a Git repository as the single source of truth for both application code and cluster state. In GitOps, an agent (Argo CD or Flux) continuously reconciles the live environment against the declared state in Git, and any drift is corrected automatically.

## How it works
A CI pipeline builds and validates code on every change: fetch, compile, test, scan, and package a container image. A CD/GitOps layer then promotes that artifact. GitOps comes in two forms: **push** (a pipeline runs `kubectl`/`helm` against the cluster) and **pull** (an in-cluster agent polls Git and applies differences). Pull-based GitOps is the canonical model: the agent watches a config repository, detects drift between Git and the cluster, and converges the cluster back to Git.

```yaml
# CI pipeline (GitHub Actions) — build, test, publish image
name: ci
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ghcr.io/example/web:${{ github.sha }} .
      - run: docker push ghcr.io/example/web:${{ github.sha }}
---
# GitOps application — Argo CD declares the desired state
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: web
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/infra.git
    path: apps/web
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true      # delete resources removed from Git
      selfHeal: true   # revert out-of-band cluster changes
```

GitOps enforces a strong invariant: the only supported way to change the cluster is a Git commit/merge, which produces an audit trail, enables review via PRs, and makes rollback a `git revert`. Secrets are stored separately (e.g., SOPS, External Secrets) rather than committed in plaintext.

## Tradeoffs
- **Auditability**: every change is a reviewed, immutable Git commit with full history, but teams must discipline themselves to make all changes through Git, not `kubectl apply` by hand.
- **Convergence**: the agent continuously enforces desired state and self-heals drift, but rapid-fire changes or misconfig can trigger reconcile loops and require rate limits.
- **Security**: pull-based agents need no cluster write credentials exposed to CI, but the Git repo and its credentials become a critical attack surface.
- **Complexity**: GitOps standardizes delivery and rollback, but adds an agent, a config-repo layout, and tooling that small teams may find heavy.
- **Push vs pull**: push pipelines are familiar and flexible, but expose cluster credentials and don't self-heal; pull agents self-heal but constrain how changes flow.

## When to use
- Teams managing many services and environments that need reproducible, reviewable, auditable deployments.
- Environments requiring disaster recovery and rollback as simple `git revert` operations.
- Organizations that want continuous drift detection and automatic convergence to declared state.

## Alternatives
- **Imperative scripting (kubectl/Ansible)**: flexible ad-hoc control, but no audit trail, no self-healing, and risk of config drift.
- **Terraform/CloudFormation (infra provisioning)**: excellent for provisioning cloud resources, but not designed to continuously reconcile running application workloads.
- **Traditional CD servers (Jenkins pipelines pushing)** : mature and widely understood, but weaker drift detection and more exposed credentials than a pull-based GitOps agent.

## Related
- [Kubernetes](02-kubernetes.md)
- [Deployment Strategies](03-deployment-strategies.md)
- [Infrastructure as Code](../01-cloud-primitives/05-infrastructure-as-code.md)
- [Observability](05-observability.md)
