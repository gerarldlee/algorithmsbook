---
title: "Deployment Strategies"
weight: 3
toc: true
---

## What it is
Deployment strategies are controlled techniques for releasing a new version of a service into production, trading off risk, downtime, and resource cost. The main patterns — recreate, rolling, blue-green, canary, and feature flags — differ in how much of the traffic, infrastructure, and time is shifted to the new version at once.

## How it works
Each strategy changes the rate and reversibility of the cutover:

- **Recreate**: terminate the old version entirely, then start the new one; simple but causes downtime.
- **Rolling**: incrementally replace old instances with new ones, keeping the service available while a mix of versions briefly serves traffic.
- **Blue-green**: run two full environments (old "blue" and new "green"), then switch all traffic at once via a load balancer; instant rollback by switching back.
- **Canary**: route a small, controlled percentage of traffic to the new version, observe it, and gradually ramp up.
- **Feature flags**: keep one deployed binary and toggle behavior at runtime per user/cohort, decoupling deploy from release.

```yaml
# Canary rollout driven by a service mesh / ingress (Istio example)
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: web
spec:
  hosts: ["web"]
  http:
    - route:
        - destination:
            host: web
            subset: stable
          weight: 90
        - destination:
            host: web
            subset: canary
          weight: 10
---
# Blue-green: two Deployments, one Service selector switch
apiVersion: v1
kind: Service
metadata:
  name: web-active
spec:
  selector: { app: web, version: green }   # flip to "blue" to roll back
  ports:
    - port: 80
      targetPort: 8080
```

Kubernetes implements rolling updates natively via Deployment `strategy: RollingUpdate` (`maxSurge`/`maxUnavailable`). Canary and blue-green are layered on top using duplicate Deployments plus a Service/Ingress selector switch or a service mesh. Feature flags are implemented in application code and controlled by a flag service, entirely independent of the infrastructure release.

## Tradeoffs
- **Recreate**: zero resource overhead and no version coexistence, but full downtime and no partial rollback.
- **Rolling**: no downtime and native to Kubernetes, but rollback is slow (re-reverse the rollout) and both versions must be backward-compatible during the transition.
- **Blue-green**: instant atomic switch and rollback, but doubles infrastructure cost and risks a big-bang failure on the whole fleet.
- **Canary**: smallest blast radius and real-world validation, but requires traffic routing, good metrics, and careful ramping discipline.
- **Feature flags**: decouples deploy from release and enables per-user rollout, but adds code complexity, flag drift, and a runtime dependency on the flag service.

## When to use
- Recreate for non-critical batch jobs or internal tools where downtime is acceptable.
- Rolling as the default for standard stateless web services needing zero downtime.
- Blue-green when instant, atomic rollback matters more than doubled cost (e.g., regulated releases).
- Canary for high-traffic services where you want to validate a release on real users before full exposure.
- Feature flags for long-running, gradual feature rollout and experimentation decoupled from deploys.

## Alternatives
- **Shadow deployment**: mirror real traffic to the new version without affecting users — excellent pre-release validation, but doubles traffic handling and yields no user-facing signal.
- **A/B testing**: route by cohort for experiment measurement rather than safety, trading operational simplicity for statistically meaningful comparison.
- **In-place updates (immutable VMs)**: bake a new image and swap instances, giving full-stack reproducibility at the cost of slower, heavier cutover than containers.

## Related
- [Container Internals](01-container-internals.md)
- [Kubernetes](02-kubernetes.md)
- [CI/CD and GitOps](04-cicd-gitops.md)
- [Observability](05-observability.md)
