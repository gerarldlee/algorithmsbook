---
title: "20.1 Regulatory Frameworks: PCI-DSS, SOX, GDPR/data residency, MiCA (crypto), Basel III (risk capital)"
weight: 1
toc: true
level: normal
---

## What it is

A **regulatory framework** is a jurisdiction- and obligation-specific set of requirements translated into scoped controls, accountable owners, operating procedures, and evidence. Frameworks do not substitute for legal advice, and applying one does not establish that an organization complies with every other law that may govern the same system.

## How it works

A defensible implementation starts with scope, identifies the authoritative requirement, maps it to a control, and preserves evidence that the control operated. The same technical control can satisfy several frameworks, but each mapping remains traceable to its own requirement, owner, test, and framework version.

```mermaid
flowchart LR
    Legal[Applicable law and regulator guidance] --> Scope[Entity, activity, data, and jurisdiction scope]
    Scope --> Requirement[Versioned requirement register]
    Requirement --> Control[Control and evidence mapping]
    Control --> Workflow[Owner, frequency, and procedure]
    Workflow --> Evidence[Assessment and remediation record]
    Evidence --> Review[Legal, risk, and audit review]
    Review --> Report[Filing or attestation]
```

The following assumptions must remain explicit in the control catalog:

| Framework | Applicability assumption | Common evidence | Boundary |
| --- | --- | --- | --- |
| PCI DSS | Cardholder data is stored, processed, or transmitted, or the environment is in scope | Scope inventory, segmentation tests, scan results, change approvals | The cardholder data environment and connected systems determine scope; a scan alone does not prove compliance |
| SOX | The reporting entity is subject to the applicable securities law and management assesses the relevant financial-reporting controls | Control narratives, evidence, deficiencies, certifications | Applicability and assurance depend on the reporting regime; the technical control is not the certification |
| GDPR and residency | Processing concerns personal data, and each transfer or storage location is assessed under its own legal rules | Records of processing, transfer assessments, data-subject request records | GDPR is not a residency rule, and data location alone does not determine GDPR applicability |
| MiCA | The activity is within the Markets in Crypto-Assets Regulation's scope and the organization meets the applicable authorization or registration condition | Customer and transaction records, prudential metrics, complaints, disclosures | Classification, authorization, and reporting duties depend on the service, entity, and Member State implementation |
| Basel III | The entity is subject to the applicable Basel prudential framework or adopts it as an internal capital basis | Exposure data, risk parameters, capital calculations, validation | National supervisors apply the framework in a jurisdiction-specific way; internal models are not automatically approved |

This executable control mapping is a practical starting artifact, not a certification record:

```yaml
schema_version: 1
catalog_id: regulatory-controls
assumptions:
  reporting_entity: Example Public Company
  card_data_processed: true
  eu_personal_data_processed: true
  crypto_asset_service_provided: false
  prudential_scope: not_applicable
  legal_review_required: true
frameworks:
  - framework: PCI-DSS
    version: "4.0.1"
    requirement: "12.8"
    control: external-accounts-callbacks
    owner: payments-security
    evidence: annual-access-review
    status: effective
  - framework: GDPR
    version: "2016/679"
    requirement: "Article 30"
    control: processing-records
    owner: privacy-operations
    evidence: records-of-processing
    status: effective
  - framework: SOX
    version: entity-policy-2026
    requirement: change-management
    control: production-change-approval
    owner: platform-engineering
    evidence: pull-request-and-approval-record
    status: testing
```

Control operation is a sequence, not a document dump:

1. Register the applicable obligation and its effective date.
2. Record scope exclusions, dependencies, assumptions, and legal interpretations.
3. Assign one accountable control owner even when several teams perform the work.
4. Execute the procedure at the required frequency and retain the result.
5. Evaluate exceptions, assign remediation, and preserve both the original and resolved states.
6. Reapprove the mapping when the framework, system, process, or jurisdiction changes.

A regulation version, contractual standard, and internal policy are different things. Store each with its own identifier and effective dates. Versioning prevents a later control test from being presented as evidence that an earlier reporting period was compliant.

## Tradeoffs

- **Reuse one control mapping** — reduces duplicated testing, but the cost is maintaining framework-specific interpretations and evidence views.
- **Centralize a control platform** — standardizes ownership and status, but the platform becomes a critical dependency and cannot replace accountable business review.
- **Enforce every jurisdiction globally** — simplifies implementation, but the cost is over-restrictive processing and missed local opportunities.
- **Store evidence in general data platforms** — improves queryability, but the cost is relying on their retention, immutability, and legal-hold behavior.

## When to use

- You need a traceable path from an obligation to a control and retained evidence.
- Multiple frameworks apply to one service and must share evidence without losing separate interpretations.
- A control owner must report the current, degraded, and failed states of a compliance program.
- Regulators, auditors, customers, or acquirers need reproducible evidence for a stated period.
- You need to determine whether a policy choice is a legal requirement, a contractual commitment, or an internal risk decision.

## Alternatives

- **Integrated compliance platform** — accelerates evidence collection when its mappings fit your jurisdictions; the cost is vendor lock-in and configuration drift.
- **Control-code policy as code** — makes preventive checks repeatable and testable, but it cannot encode legal interpretation or substitute for review.
- **GRC spreadsheet and issue tracker** — works for a small initial program, but weak lineage and inconsistent status reporting become costly as scope grows.
- **Certification by an external assessor** — provides independent evidence for some frameworks, but the cost is formal scope and does not cover unrelated legal duties.

## Related

- [20.2 Risk Engines: Credit Risk Scoring, Market Risk (VaR), Operational Risk Frameworks](02-risk-engines.md)
- [20.3 Audit & Compliance Reporting: Immutable Logging, Regulatory Reporting Pipelines, Explainability for Automated Decisions](03-audit-and-compliance-reporting.md)
- [20.4 Data Governance: PII Handling, Data Retention/Deletion, Consent Management](04-data-governance.md)
- [Chapter 20 References](05-references.md)
