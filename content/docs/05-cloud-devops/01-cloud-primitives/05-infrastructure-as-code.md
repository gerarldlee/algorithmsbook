---
title: "Infrastructure as Code"
weight: 5
toc: true
---

## What it is
Infrastructure as Code (IaC) is the practice of defining and managing infrastructure — networks, compute, storage, policies — through versioned, machine-readable configuration files instead of manual clicks or imperative scripts. It makes provisioning repeatable, reviewable, and auditable, treating infrastructure with the same tooling as application code.

## How it works
You write a **declarative** description of the desired end state (resources and their properties), and a tool reconciles the real world toward it. **Terraform** maintains a **state file** of the current inventory, diffs your configuration against it, and issues create/update/delete API calls in dependency order to converge. **CloudFormation** is AWS-native and manages the same via **stacks** and change sets; **Pulumi** expresses the same idea in general-purpose languages (TypeScript, Python, Go) instead of a DSL. The reconciliation loop is idempotent: re-running produces no changes unless the desired state drifted.

```yaml
# Terraform (HCL): declarative desired state with a plan/apply loop
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id

  tags = { Name = "web" }
}

resource "aws_security_group" "web" {
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

The core loop is **write → plan → apply**: the plan shows the exact diff before anything changes; apply executes it and records the result in state. **Drift** occurs when reality changes outside the tool (a console edit, a manual fix), so the next plan detects the difference and can restore it. Storing state remotely (with locking) enables team collaboration, and modules/compositions reuse patterns across environments. **Imperative** tools (Ansible, shell, SDK scripts) instead execute step-by-step commands and must track "what already ran" themselves.

## Tradeoffs
- **Declarative vs. imperative**: declarative tools converge to a state and detect drift automatically, but are less flexible for complex branching logic; imperative scripts express arbitrary logic but don't know the current state and can diverge from reality.
- **State file**: tracking state makes planning and drift detection possible, but the state file is a single source of truth that can get out of sync, must be stored securely, and needs locking to avoid concurrent-write corruption.
- **Drift handling**: reconciling drift keeps reality honest, but blindly re-applying can revert legitimate emergency fixes unless you import the change back into code first.
- **Language vs. DSL**: Pulumi/general-purpose languages reuse familiar code and abstractions, but bring Turing-complete complexity; HCL/DSLs are simpler and safer but limited in expressiveness.
- **Vendor coupling**: CloudFormation is tightly integrated with AWS but single-vendor; Terraform is multi-cloud but adds a state file and provider-version management to operate.

## When to use
- Environments that must be reproducible: dev/staging/prod parity, disaster recovery, and onboarding new engineers.
- Teams that need reviewable, auditable changes to production infrastructure with an approval (plan) step before apply.
- Multi-environment or multi-cloud fleets where the same configuration is parameterized and reused.

## Alternatives
- **Manual console/click-ops**: fastest for a one-off prototype, but unrepeatable, error-prone, and impossible to review or audit.
- **Imperative scripts (Ansible, bash, SDK)**: fine for config management and ad-hoc tasks, but no inherent state or drift detection and harder to keep idempotent.
- **GitOps tools (Argo CD/Flux)**: continuous reconciliation of a live cluster to a Git repo with automatic drift correction, but mainly for Kubernetes and more moving parts.

## Related
- [Compute](01-compute.md)
- [Serverless](04-serverless.md)
- [CI/CD and GitOps](../02-containers-cicd/04-cicd-gitops.md)
- [Kubernetes](../02-containers-cicd/02-kubernetes.md)
- [Cloud Networking](03-cloud-networking.md)
