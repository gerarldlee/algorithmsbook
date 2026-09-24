---
title: "Infrastructure as Code (IaC): Declarative Provisioning with Terraform and OpenTofu"
weight: 5
toc: true
---

## What it is
Infrastructure as Code (IaC) is the practice of defining and managing infrastructure — networks, compute, storage, policies — through versioned, machine-readable configuration files instead of manual clicks or imperative scripts. It makes provisioning repeatable, reviewable, and auditable, treating infrastructure with the same tooling as application code.

## How it works
You write a **declarative** description of the desired end state (resources and their properties), and a tool reconciles the real world toward it. **Terraform** and **OpenTofu** maintain a state snapshot of the resources last observed plus provider metadata, compare configuration with that snapshot, and issue create, update, and delete API calls in dependency order to converge. **CloudFormation** is AWS-native and manages the same desired-state model through stacks and change sets. **Pulumi** expresses the same idea in general-purpose languages such as TypeScript, Python, and Go instead of a configuration DSL. A repeated apply makes no unnecessary changes when the desired state already matches, although remote API behavior can still require provider-specific controls.

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web.id]
  tags                   = { Name = "web" }
}

resource "aws_security_group" "web" {
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

```bash
tofu init
tofu plan -out=tfplan
tofu apply tfplan
```

The core loop is **write → plan → apply**: the plan shows the proposed changes before apply executes them, and the result is recorded in state. **Drift** occurs when reality changes outside the tool (a console edit, a manual fix), so a later plan can expose the difference and restore the declared state. Storing state remotely with locking enables team collaboration, and modules or compositions reuse patterns across environments. **Ansible** is also declarative and convergence-oriented: its modules inspect current state and act on declared module-level state. Most modules are designed for repeated use without unnecessary changes, but `command` and `shell` tasks need explicit change detection or other controls. Shell and SDK scripts are more directly imperative and generally must track prior execution themselves.

## Tradeoffs
- **Declarative vs. imperative**: declarative and convergence-oriented tools express desired state and let modules or providers converge toward it, but task- and module-specific controls still matter; imperative scripts express arbitrary step order and must track and verify state themselves.
- **State file**: tracking resources makes planning and drift detection possible, but the state file is an observed-state snapshot rather than the source of desired infrastructure. It can become stale, must be stored securely, and needs locking to avoid concurrent-write corruption.
- **Drift handling**: reconciling drift keeps reality honest, but blindly re-applying can revert legitimate emergency fixes unless you import the change back into code first.
- **Language vs. DSL**: Pulumi/general-purpose languages reuse familiar code and abstractions, but bring Turing-complete complexity; HCL/DSLs are simpler and safer but limited in expressiveness.
- **Vendor coupling**: CloudFormation is tightly integrated with AWS but single-vendor; Terraform is multi-cloud but adds a state file and provider-version management to operate.

## When to use
- Environments that must be reproducible: dev/staging/prod parity, disaster recovery, and onboarding new engineers.
- Teams that need reviewable, auditable changes to production infrastructure with an approval (plan) step before apply.
- Multi-environment or multi-cloud fleets where the same configuration is parameterized and reused.

## Alternatives
- **Manual console/click-ops**: fastest for a one-off prototype, but unrepeatable, error-prone, and impossible to review or audit.
- **Shell or SDK scripts**: fine for ad-hoc tasks, but they generally lack a native desired-state model or drift plan and must implement convergence controls themselves.
- **Ansible**: wins for configuration management and heterogeneous fleets through declarative, convergence-oriented modules, but run behavior depends on each module and tasks that bypass modules need explicit controls.
- **GitOps tools (Argo CD/Flux)**: continuous reconciliation of a live cluster to a Git repo with automatic drift correction, but mainly for Kubernetes and more moving parts.

## Related
- [Serverless](04-serverless.md)
- [CI/CD and GitOps](../02-containers-cicd/04-cicd-gitops.md)
- [Cloud Networking](03-cloud-networking.md)
