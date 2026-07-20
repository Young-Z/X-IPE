# Requirement Details - Part 26

> Continued from: [requirement-details-part-25.md](x-ipe-docs/requirements/requirement-details-part-25.md)
> Created: 07-20-2026

---

## EPIC-060: CR Assessment AI Court

> Version: 1.0
> Source Idea: [IDEA-001 — CR Assessment AI Court](x-ipe-docs/ideas/Draft%20Idea%20-%2007202026%20121023/refined-idea/idea-summary-v1.md)
> Dependencies: FEATURE-002-A (Content Viewer / Mermaid rendering), EPIC-043 (Deliverable Preview), existing X-IPE Console and prompt configuration
> Conflicts: None

### Project Overview

CR Assessment AI Court is an X-IPE module for independently assessing a Vendor's Change Request effort estimate. A project manager or technical lead creates an assessment case, provides the CR, a readable local codebase path, Vendor estimates, and supporting evidence, then runs an AI assessment at Quick, Standard, or Deep depth.

The system produces a reproducible module-level effort range, confidence scores, Vendor-vs-AI comparison, transparent benchmark adjustments, negotiation guidance, and a Vendor-executable technical design. Its purpose is to replace black-box Vendor estimates with auditable evidence and a lower-effort AI-suggested implementation path.

### User Request

Build a standalone CR assessment workflow integrated into X-IPE. It must manage assessment cases, analyze local code, compare AI and Vendor effort, generate consistent versioned HTML reports from skill-owned templates, render all report diagrams with a bundled Mermaid JavaScript plugin, and provide a detailed technical design that the Vendor can adopt to reduce delivery effort.

### Target Users

| User | Primary Goals | Authorized Actions |
|------|---------------|--------------------|
| Project Manager | Control cost, prepare negotiation position, share reports | Create/update cases, upload inputs, start assessment, view/share reports |
| Technical Lead | Validate feasibility, inspect evidence, review suggested solution | Configure codebase path, start assessment, inspect module findings and design |
| Vendor | Understand evidence and adopt the proposed lower-effort solution | Receive and read the same complete generated reports |

### Clarifications

| Question | Decision |
|----------|----------|
| How are reports shared with the Vendor? | The complete reports are directly shareable; there is no separate sanitized Vendor edition in v1. |
| When is a case Completed? | Immediately after all required AI reports are generated successfully. Human review is tracked separately and does not block completion. |
| What codebase sources are supported in v1? | Readable local filesystem paths only. Git URL cloning is out of scope. |
| How are industry benchmarks managed? | Fixed, versioned assets bundled inside the evaluation skill; benchmark version appears in every assessment. |

### High-Level Requirements

1. **HLR-060.1 — Assessment Case Management:** Users can create, update, browse, search, and inspect CR assessment cases and their status.
2. **HLR-060.2 — Evidence Input:** Each case captures CR content, local codebase path, Vendor estimate, supporting documents, and comments without altering original uploaded files.
3. **HLR-060.3 — Multi-Depth AI Assessment:** Users can run Quick, Standard, or Deep analysis against a readable local codebase.
4. **HLR-060.4 — Independent Effort Evidence:** The system produces module-level effort ranges, confidence, benchmark adjustments, AI productivity factors, and a symmetric Vendor comparison.
5. **HLR-060.5 — Vendor-Executable Design:** The technical design balances adoption rationale with implementation-level contracts, data models, work packages, tests, rollout, rollback, and acceptance evidence.
6. **HLR-060.6 — Template-Driven Reports:** The evaluation skill owns versioned templates for CaseRecord, effort estimation, and suggested technical design, driven by a shared Structured Report Model.
7. **HLR-060.7 — Mermaid Diagram Rendering:** All generated report diagrams remain Mermaid source and render in the browser through a bundled Mermaid v11 ESM asset under strict security.
8. **HLR-060.8 — Versioned, Auditable Output:** Assessment inputs, benchmark version, analysis depth, report model, output version, and timestamps are traceable.
9. **HLR-060.9 — X-IPE Integration:** The module is reachable from X-IPE UI and Console prompts while the evaluation skill remains independent from `x-ipe-task-based-change-request`.
10. **HLR-060.10 — Full Report Sharing:** Generated reports are self-contained, printable, and directly shareable with the Vendor.

---

### Functional Requirements

#### FR-060.1 — Case Lifecycle and Storage

- **FR-060.1.1:** Store each case under `x-ipe-docs/cr-cases/{case-name}/`.
- **FR-060.1.2:** Each case has a stable case ID, display name, created/updated timestamps, status, analysis history, file references, and report versions.
- **FR-060.1.3:** Supported case statuses are `Created`, `Evaluating`, `Completed`, and `Failed`.
- **FR-060.1.4:** Starting an assessment changes status to `Evaluating`.
- **FR-060.1.5:** Successful generation of all mandatory outputs changes status to `Completed` immediately.
- **FR-060.1.6:** Human review state is separately recorded as `Not Reviewed`, `Reviewed`, or `Follow-up Required`; it does not change case completion.
- **FR-060.1.7:** Failure changes status to `Failed`, preserves the previous valid report version, and records a non-sensitive failure reason.
- **FR-060.1.8:** The case list supports search by name/ID and status display.
- **FR-060.1.9:** `CaseRecord.html` contains machine-readable JSON metadata and a human-readable CIO report.

#### FR-060.2 — Case Inputs

- **FR-060.2.1:** Case Name and CR Description are mandatory.
- **FR-060.2.2:** CR Description accepts direct text or an uploaded source file whose original representation is preserved.
- **FR-060.2.3:** Codebase Path accepts a local filesystem directory only.
- **FR-060.2.4:** Before assessment, validate that the path exists, is a directory, and is readable.
- **FR-060.2.5:** If the path is invalid or unreadable, AI Estimation is unavailable and the UI explains how to correct it.
- **FR-060.2.6:** Supporting Documents accept multiple files and preserve original filenames and content.
- **FR-060.2.7:** Vendor Effort Estimation accepts an uploaded source artifact and is mandatory for Vendor comparison.
- **FR-060.2.8:** Comments are optional and are included in the assessment input snapshot.
- **FR-060.2.9:** Remote Git URLs, automatic cloning, branch selection, and repository credential management are not accepted in v1.

#### FR-060.3 — Assessment Invocation and Depth

- **FR-060.3.1:** The AI Estimation control offers `Quick`, `Standard`, and `Deep`.
- **FR-060.3.2:** `Standard` is selected by default.
- **FR-060.3.3:** Quick analyzes explicitly targeted modules and immediate implementation surfaces.
- **FR-060.3.4:** Standard analyzes target modules, dependencies, test impact, and primary integration paths.
- **FR-060.3.5:** Deep analyzes the full reachable baseline, cross-module impact, systemic risks, and wider regression scope.
- **FR-060.3.6:** Starting an assessment creates an immutable input snapshot containing case metadata, file hashes/references, local codebase path, analysis depth, benchmark version, and timestamp.
- **FR-060.3.7:** The X-IPE Console exposes an `evaluate-cr-effort` prompt with case-folder and analysis-depth context.
- **FR-060.3.8:** The evaluation workflow invokes a standalone `x-ipe-task-based-evaluate-change-request-efforts` skill.

#### FR-060.4 — Effort Analysis

- **FR-060.4.1:** Decompose the CR into independently estimable modules or work packages.
- **FR-060.4.2:** Each module reports a low/high person-day range and confidence percentage.
- **FR-060.4.3:** The estimate combines code impact evidence, fixed industry benchmarks, reuse opportunities, test impact, uncertainty, and AI-assisted productivity factors.
- **FR-060.4.4:** Industry benchmarks are immutable, versioned skill assets and do not depend on an external runtime service.
- **FR-060.4.5:** Every report shows the benchmark version and which benchmark/adjustment factors affected each estimate.
- **FR-060.4.6:** Compare Vendor and AI estimates symmetrically, identifying high estimates, low estimates, and reasonable estimates.
- **FR-060.4.7:** Never force the conclusion that the Vendor is high; findings follow the available evidence.
- **FR-060.4.8:** Provide an overall credible range, confidence, negotiation room, risk reserve, and recommended negotiation position.
- **FR-060.4.9:** Distinguish evidence, assumptions, and unresolved uncertainty.

#### FR-060.5 — Suggested Technical Design

- **FR-060.5.1:** Part 1 provides an executive and agent-facing adoption summary: recommendation, scope boundary, reuse strategy, changed components, dependencies, major flow, and a usage example.
- **FR-060.5.2:** The component table includes Component, Responsibility, Action (`New`, `Change`, `Reuse`), reuse evidence/boundary, and semantic Tags.
- **FR-060.5.3:** Part 2 provides an implementation guide adapted to the CR's implementation type.
- **FR-060.5.4:** Include interface contracts with inputs, outputs, validation, invariants, and prohibited responsibilities.
- **FR-060.5.5:** Include applicable HTTP/API contracts, request/response shape, authorization, success behavior, and error semantics.
- **FR-060.5.6:** Include applicable data model/schema changes and explicitly identify unchanged models.
- **FR-060.5.7:** Include architecture and runtime sequence diagrams.
- **FR-060.5.8:** Break work into ordered implementation packages with outputs, effort range, dependency, and reuse-based saving.
- **FR-060.5.9:** Work-package totals reconcile exactly with the recommended overall effort range.
- **FR-060.5.10:** Include acceptance traceability, required evidence, migration, staged rollout, rollback triggers, edge-case decisions, and Vendor Definition of Ready/Done.
- **FR-060.5.11:** The report's recommended design optimizes KISS, YAGNI, DRY, and reuse of existing project capabilities.
- **FR-060.5.12:** The design is directly shareable with the Vendor and must not include hidden internal-only annotations.

#### FR-060.6 — Structured Report Model and Templates

- **FR-060.6.1:** The skill first produces a validated Structured Report Model; analysis logic must not assemble complete HTML pages directly.
- **FR-060.6.2:** The model contains shared metadata plus report-specific effort, design, files, slides, and diagrams data.
- **FR-060.6.3:** The skill owns these versioned templates:
  - `templates/case-record-template.html`
  - `templates/effort-estimation-template.html`
  - `templates/suggested-technical-design-template.html`
- **FR-060.6.4:** Templates are derived from the approved EPIC-060 mockups but contain no hard-coded example-case data.
- **FR-060.6.5:** Missing optional model sections cause their corresponding template blocks to hide without breaking layout.
- **FR-060.6.6:** Templates share theme tokens, metadata conventions, report navigation, print behavior, and versioning conventions.
- **FR-060.6.7:** Template/model incompatibility fails validation before overwriting or publishing a report.
- **FR-060.6.8:** Template version and model schema version appear in report metadata.

#### FR-060.7 — Mermaid Rendering

- **FR-060.7.1:** Store each generated diagram as Mermaid source in the Structured Report Model.
- **FR-060.7.2:** Render diagram source inside `<pre class="mermaid">` elements.
- **FR-060.7.3:** Bundle a pinned Mermaid v11 ESM asset with the skill; generated reports do not depend on a CDN.
- **FR-060.7.4:** Initialize Mermaid with `startOnLoad: false`, `securityLevel: "strict"`, and the report's base theme.
- **FR-060.7.5:** Run rendering explicitly after data injection with `await mermaid.run({ querySelector: ".mermaid" })`.
- **FR-060.7.6:** Supported report diagram types include flowchart, sequence, state, class, and ER.
- **FR-060.7.7:** Mermaid labels and source are treated as untrusted generated content; v1 does not enable click callbacks, loose security, or untrusted HTML labels.
- **FR-060.7.8:** If one diagram fails, show its source and a local error state while the rest of the report remains readable and printable.
- **FR-060.7.9:** Mermaid colors map to shared report theme tokens, and printed diagrams remain legible.

#### FR-060.8 — Report Versioning and Navigation

- **FR-060.8.1:** Generate `EffortEstimation_AI_vN.html` and `SuggestedTechnicalDesign_AI_vN.html` with monotonically increasing versions.
- **FR-060.8.2:** Preserve all previous generated report versions.
- **FR-060.8.3:** `CaseRecord.html` links to the latest versions and lists historical versions.
- **FR-060.8.4:** CaseRecord CIO slides support previous/next controls and keyboard arrow navigation.
- **FR-060.8.5:** Reports cross-link to related assessment and design reports.
- **FR-060.8.6:** All report content required for reading is available from the case folder and can be shared with the Vendor as a folder bundle.
- **FR-060.8.7:** Reports provide print/export-friendly styling.

#### FR-060.9 — X-IPE Module UI

- **FR-060.9.1:** Provide a split view with Case List Panel and Detail Panel matching the approved main mockup.
- **FR-060.9.2:** Detail Panel supports case information editing and embedded report preview.
- **FR-060.9.3:** Display status, report version, assessment depth, benchmark version, and review state.
- **FR-060.9.4:** Disable assessment controls while an assessment is running.
- **FR-060.9.5:** Do not silently discard unsaved form changes when switching cases.
- **FR-060.9.6:** All primary interactions are keyboard accessible and expose visible focus states.

---

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-060.1 Security | Code analysis occurs against the supplied local path. Reports and logs must not include secrets, raw credentials, or unnecessary source excerpts. |
| NFR-060.2 Report Safety | Escape all model-provided HTML/text by default. Mermaid remains in strict security mode. |
| NFR-060.3 Reproducibility | Identical input snapshot, benchmark version, skill version, template version, model schema, and depth must be sufficient to explain how a result was produced. |
| NFR-060.4 Offline Operation | Report viewing and diagram rendering work without network access; Mermaid is bundled locally. |
| NFR-060.5 Accessibility | UI and reports meet WCAG 2.1 AA for contrast, keyboard navigation, focus, and semantic structure where applicable. |
| NFR-060.6 Responsiveness | UI and reports remain usable at desktop and tablet widths; report content remains readable on narrow screens. |
| NFR-060.7 Failure Isolation | Failure in one diagram or optional report section does not invalidate unrelated report content. |
| NFR-060.8 Performance | Case list interaction remains responsive; long analysis executes asynchronously and exposes progress/status without blocking the UI. |
| NFR-060.9 Data Integrity | All case metadata and report writes are atomic; a failure cannot leave the case pointing to a partial latest version. |
| NFR-060.10 Maintainability | Templates share reusable tokens and helpers; template-specific behavior remains isolated and testable. |

### Acceptance Criteria

| ID | Given / When / Then |
|----|---------------------|
| AC-060.1 | GIVEN valid case inputs and a readable local codebase WHEN Standard assessment succeeds THEN status becomes Completed and all three current reports are available. |
| AC-060.2 | GIVEN an unreadable or missing local path WHEN the case form validates THEN AI Estimation is disabled and a corrective message is shown. |
| AC-060.3 | GIVEN a remote Git URL as Codebase Path WHEN it is validated THEN it is rejected as unsupported in v1. |
| AC-060.4 | GIVEN Quick, Standard, and Deep options WHEN the user opens AI Estimation THEN Standard is selected by default and each option explains its scope. |
| AC-060.5 | GIVEN an assessment report WHEN reviewed THEN every module shows an effort range, confidence, evidence/assumptions, benchmark adjustments, and Vendor comparison. |
| AC-060.6 | GIVEN evidence that the Vendor estimate is below the credible range WHEN analysis completes THEN the report flags underestimation rather than forcing a high-estimate finding. |
| AC-060.7 | GIVEN a generated report WHEN metadata is inspected THEN benchmark, skill, template, model schema, report, and input snapshot versions are present. |
| AC-060.8 | GIVEN the suggested technical design WHEN a Vendor technical lead reads it THEN both Part 1 adoption guidance and Part 2 implementation contracts/work packages are present. |
| AC-060.9 | GIVEN design work packages WHEN totals are calculated THEN they equal the report's overall recommended range. |
| AC-060.10 | GIVEN the same report folder shared with a Vendor WHEN opened offline THEN all report text, styles, navigation, and Mermaid diagrams render without an application server or CDN. |
| AC-060.11 | GIVEN generated text containing HTML/script-like content WHEN rendered THEN it is escaped and cannot execute. |
| AC-060.12 | GIVEN a malformed Mermaid diagram WHEN reports initialize THEN that diagram shows a local error/source fallback and other report content remains usable. |
| AC-060.13 | GIVEN a completed assessment WHEN no human review has occurred THEN case status remains Completed and review state is Not Reviewed. |
| AC-060.14 | GIVEN an existing v1 report WHEN a new assessment generates v2 THEN v1 remains accessible and CaseRecord links v2 as latest. |
| AC-060.15 | GIVEN an assessment failure after a valid prior report WHEN status becomes Failed THEN the prior report remains intact and no partial new version is marked latest. |
| AC-060.16 | GIVEN the approved mockups WHEN implemented THEN the main UI and two report types preserve their information hierarchy, interactions, theme, and responsive behavior. |

### Feasibility and Risk Assessment

| Risk | Level | Impact | Mitigation / Requirement Response |
|------|-------|--------|-----------------------------------|
| Source-code confidentiality | High | Sensitive code or secrets may leak into reports shared with Vendor | Local-only analysis, secret filtering, minimal source excerpts, explicit full-report sharing awareness |
| Full reports reveal negotiation strategy | High | Vendor sees benchmark adjustments and negotiation guidance | Accepted product decision; reports contain no separate hidden internal annotation |
| Benchmark drift or bias | High | Estimates become inconsistent or misleading | Fixed versioned assets, benchmark version disclosure, symmetric comparison, evidence/assumption separation |
| Large repositories and Deep analysis | Medium | Long-running tasks or incomplete scans | Asynchronous execution, depth definitions, progress status, failure preservation |
| Template/model incompatibility | Medium | Broken or incomplete reports | Versioned schema/template validation before publication |
| Mermaid injection/render failures | Medium | Security or missing diagrams | Strict mode, escaped content, pinned local asset, per-diagram fallback |
| Vendor rejects suggested architecture | Medium | Expected effort saving is not realized | Reuse evidence, explicit contracts, work-package saving, Vendor DoR/DoD |
| Local path changes after snapshot | Medium | Reproducibility gap | Record path plus relevant hashes/revision evidence in immutable snapshot |

### Dependencies and Overlap Review

| Existing Capability | Relationship | Decision |
|--------------------|--------------|----------|
| FEATURE-002-A Content Viewer / Mermaid | Reusable rendering precedent | Dependency; no conflict. EPIC-060 report bundles remain self-contained. |
| EPIC-043 Deliverable Preview | Can preview generated HTML in X-IPE | Dependency; no scope overlap with assessment generation. |
| `x-ipe-task-based-change-request` | Existing change-request workflow | Keep independent; assessment evaluates Vendor effort and does not alter CR workflow behavior. |
| X-IPE Console / `copilot-prompt.json` | Invocation surface | Add CR assessment prompt entry; reuse existing console execution patterns. |

### Scope

#### In Scope

- CR Assessment module UI and case storage
- Local-path input validation and immutable assessment snapshots
- Quick, Standard, and Deep AI effort assessment
- Fixed, versioned industry benchmarks
- Vendor-vs-AI comparison and negotiation guidance
- Standalone evaluation task-based skill
- Three skill-owned, template-driven HTML reports
- Vendor-executable suggested technical design
- Bundled Mermaid v11 ESM rendering with strict security and fallback
- Report history, direct Vendor sharing, printing, offline viewing, and X-IPE preview
- Console prompt integration

#### Out of Scope for v1

- Remote Git cloning, branch checkout, credentials, or repository hosting integrations
- Administrator-editable or organization-specific benchmark overrides
- Separate sanitized Vendor report editions
- Knowledge-graph writeback
- Vendor portal, comments, approvals, or external collaboration workflow
- Automatic contract approval/rejection or procurement-system integration
- Role synchronization from IdP claims or unrelated identity-system changes
- Automatic remediation or code modification of the assessed codebase

### Open Questions

None. All requirement-level scope decisions are resolved.

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| CR Assessment case management and input flow | [cr-assessment-view-v1.html](x-ipe-docs/requirements/EPIC-060/mockups/cr-assessment-view-v1.html) |
| AI effort estimation and negotiation evidence | [effort-estimation-ai-v2.html](x-ipe-docs/requirements/EPIC-060/mockups/effort-estimation-ai-v2.html) |
| Vendor implementation blueprint | [suggested-technical-design-ai-v2.html](x-ipe-docs/requirements/EPIC-060/mockups/suggested-technical-design-ai-v2.html) |

### Requirement Completion Checklist

- [x] User roles, business value, and case workflow documented
- [x] Four clarifying decisions incorporated
- [x] Existing requirement parts reviewed; no conflict found
- [x] In-scope and out-of-scope boundaries explicit
- [x] Functional, non-functional, and acceptance requirements documented
- [x] Feasibility and risks recorded with mitigations
- [x] Mockups copied into EPIC-060 and linked
- [x] No unresolved questions remain
