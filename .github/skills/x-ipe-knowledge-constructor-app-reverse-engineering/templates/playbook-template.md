# Application Reverse Engineering — Playbook Template

> This playbook defines the standard framework for application reverse engineering reports.
> Used by the `provide_framework` operation to scaffold RE reports.
> Sections are mapped to `x-ipe-tool-rev-eng-*` sub-skills for extraction.

---

## Section → Sub-Skill Map

| # | Section | Sub-Skill | Output Type |
|---|---------|-----------|-------------|
| 1 | Architecture Recovery | `x-ipe-tool-rev-eng-architecture-recovery` | Subfolder (Markdown + diagrams) |
| 2 | API Contract Extraction | `x-ipe-tool-rev-eng-api-contract-extraction` | Subfolder (Markdown + schemas) |
| 3 | Business Logic Mapping | `x-ipe-tool-rev-eng-business-logic-mapping` | Subfolder (Markdown + flow diagrams) |
| 4 | Data Model Analysis | `x-ipe-tool-rev-eng-data-model-analysis` | Subfolder (Markdown + ER diagrams) |
| 5 | Dependency Analysis | `x-ipe-tool-rev-eng-dependency-analysis` | Subfolder (Markdown + dep graphs) |
| 6 | Infrastructure Analysis | `x-ipe-tool-rev-eng-infrastructure-analysis` | Subfolder (Markdown + infra diagrams) |
| 7 | Security & Auth Patterns | `x-ipe-tool-rev-eng-security-auth-pattern` | Subfolder (Markdown) |
| 8 | Testing Strategy | `x-ipe-tool-rev-eng-testing-strategy` | Subfolder (Markdown + test files) |

---

## Mixin Composition

The framework is composed from three layers:

1. **Base playbook** (this file) — 8 standard RE sections
2. **Language mixin** — Language-specific overlay prompts and detection signals (e.g., `mixin-python.md`)
3. **Repo-type mixin** — Repository structure overlay prompts and additional subsections (e.g., `mixin-microservices.md`)

**Available language mixins:** go, java, javascript, typescript, python
**Available repo-type mixins:** single-module, multi-module, monorepo, microservices

---

## Section 1: Architecture Recovery
<!-- SUB-SKILL: x-ipe-tool-rev-eng-architecture-recovery -->

Recover the system's architecture at multiple abstraction levels.

**Subsections:**
- **1.1 Conceptual Level** — Application landscape view (Architecture DSL)
- **1.2 Logical Level** — Module/component view with responsibilities (Architecture DSL)
- **1.3 Physical Level** — Class/file level structure (Mermaid class diagrams)
- **1.4 Data Flow Level** — Request/response paths through the system (Mermaid sequence diagrams)

**Output Structure:**
```
section-01-architecture-recovery/
├── _index.md
├── screenshots/
├── conceptual-landscape.md
├── logical-module-view.md
├── physical-classes.md
└── data-flow-sequences.md
```

**Tools:** Use `x-ipe-tool-architecture-dsl` for conceptual and logical levels.

---

## Section 2: API Contract Extraction
<!-- SUB-SKILL: x-ipe-tool-rev-eng-api-contract-extraction -->

Extract internal and external API contracts with request/response schemas.

**Subsections:**
- **2.1 Internal APIs** — Module-to-module function/class interfaces
- **2.2 External APIs** — HTTP endpoints, CLI commands, message handlers
- **2.3 Per-API-Group Files** — Grouped by module or service boundary
- **2.4 Schema Documentation** — Request/response types, validation rules

**Output Structure:**
```
section-02-api-contracts/
├── _index.md
├── screenshots/
└── api-{group-name}.md
```

---

## Section 3: Business Logic Mapping
<!-- SUB-SKILL: x-ipe-tool-rev-eng-business-logic-mapping -->

Map the core business rules and domain logic embedded in the codebase.

**Subsections:**
- **3.1 Domain Model** — Core domain entities and their relationships
- **3.2 Business Rules** — Explicit and implicit rules with code citations
- **3.3 Workflow / Process Flows** — Business process sequences
- **3.4 Validation Logic** — Input validation, business constraint enforcement

**Output Structure:**
```
section-03-business-logic/
├── _index.md
├── screenshots/
├── domain-model.md
└── workflow-{name}.md
```

---

## Section 4: Data Model Analysis
<!-- SUB-SKILL: x-ipe-tool-rev-eng-data-model-analysis -->

Analyze data structures, schemas, and storage patterns.

**Subsections:**
- **4.1 Database Schema** — Tables/collections, columns/fields, relationships
- **4.2 Data Transfer Objects** — DTOs, view models, API payloads
- **4.3 Data Migrations** — Schema evolution history and migration patterns
- **4.4 Data Flow** — How data transforms between storage and API layers

**Output Structure:**
```
section-04-data-model/
├── _index.md
├── screenshots/
├── schema-diagram.md
└── dto-{name}.md
```

---

## Section 5: Dependency Analysis
<!-- SUB-SKILL: x-ipe-tool-rev-eng-dependency-analysis -->

Map inter-module and external library dependencies.

**Subsections:**
- **5.1 Inter-Module Dependencies** — Which modules depend on which (import/call graph)
- **5.2 External Library Dependencies** — Third-party libraries with versions and purposes
- **5.3 Per-Module Dependency Files** — Detailed dependency breakdown per module
- **5.4 Dependency Visualization** — Mermaid + Architecture DSL dependency graphs

**Output Structure:**
```
section-05-dependency-analysis/
├── _index.md
├── screenshots/
└── deps-{module-name}.md
```

**Tools:** Use `x-ipe-tool-architecture-dsl` for dependency landscape view.

---

## Section 6: Infrastructure Analysis
<!-- SUB-SKILL: x-ipe-tool-rev-eng-infrastructure-analysis -->

Analyze infrastructure, deployment, and operational configuration.

**Subsections:**
- **6.1 Build & CI/CD** — Build system configuration, CI/CD pipelines
- **6.2 Containerization** — Dockerfiles, docker-compose, container orchestration
- **6.3 Cloud / Infrastructure** — Cloud provider configs, IaC (Terraform, CloudFormation)
- **6.4 Monitoring & Observability** — Logging, metrics, tracing configuration

**Output Structure:**
```
section-06-infrastructure/
├── _index.md
├── screenshots/
├── cicd-pipeline.md
└── infra-{component}.md
```

---

## Section 7: Security & Auth Patterns
<!-- SUB-SKILL: x-ipe-tool-rev-eng-security-auth-pattern -->

Identify authentication, authorization, and security patterns.

**Subsections:**
- **7.1 Authentication** — Auth mechanisms (JWT, OAuth, session, API keys)
- **7.2 Authorization** — Role-based, policy-based, or attribute-based access control
- **7.3 Security Middleware** — Input sanitization, CORS, rate limiting, CSRF protection
- **7.4 Secret Management** — How secrets/credentials are stored and accessed

**Output Structure:**
```
section-07-security-auth/
├── _index.md
├── screenshots/
└── auth-{mechanism}.md
```

---

## Section 8: Testing Strategy
<!-- SUB-SKILL: x-ipe-tool-rev-eng-testing-strategy -->

Analyze the project's testing approach and coverage.

**Subsections:**
- **8.1 Test Framework Detection** — Test runners, assertion libraries, fixture patterns
- **8.2 Test Collection** — Catalog of existing test files and their scope
- **8.3 Coverage Analysis** — Line/branch coverage metrics and gaps
- **8.4 Test Patterns** — Unit vs. integration vs. E2E test distribution
- **8.5 Test Quality** — Assertion density, mock usage, test isolation

**Output Structure:**
```
section-08-testing-strategy/
├── _index.md
├── screenshots/
├── coverage-report.md
└── tests/
```

**Ground Truth Rule:** Source code is NEVER modified to fix failing tests. Tests adapt to actual code behavior.
