# Feature Specification: AI Change Request Assessment Skill

> Feature ID: FEATURE-060-B
> Epic ID: EPIC-060
> Version: v1.0
> Status: Refined
> Last Updated: 07-22-2026

## Version History

| Version | Date | Description |
|---|---|---|
| v1.0 | 07-22-2026 | Initial refined specification for AI assessment, structured report generation, offline templates, and atomic publication |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|---|---|---|---|---|---|
| CR Assessment View v1 | Interactive HTML | [cr-assessment-view-v1.html](x-ipe-docs/requirements/EPIC-060/mockups/cr-assessment-view-v1.html) | CaseRecord CIO presentation and report-entry context owned jointly by the FEATURE-060-A/B contract | current | 07-22-2026 |
| Effort Estimation AI v2 | Interactive HTML | [effort-estimation-ai-v2.html](x-ipe-docs/requirements/EPIC-060/mockups/effort-estimation-ai-v2.html) | Authoritative information architecture and interaction baseline for the effort report template | current | 07-22-2026 |
| Suggested Technical Design AI v2 | Interactive HTML | [suggested-technical-design-ai-v2.html](x-ipe-docs/requirements/EPIC-060/mockups/suggested-technical-design-ai-v2.html) | Authoritative high-level adoption and low-level Vendor implementation blueprint | current | 07-22-2026 |

The mockups define information hierarchy, visual relationships, report navigation, disclosures, and printable presentation. Example case data, numeric estimates, technologies, and decisions are illustrative and must never be hard-coded into templates.

## Overview

FEATURE-060-B creates the independent `x-ipe-task-based-evaluate-change-request-efforts` skill. The skill consumes the immutable FEATURE-060-A case snapshot and a selected `quick`, `standard`, or `deep` depth, inspects the readable local codebase through AI reasoning, and publishes an evidence-based effort report, a Vendor-executable suggested technical design, and an updated CaseRecord CIO report.

The assessed repository is the primary source of truth. Versioned industry benchmarks provide fallback and comparison context but do not override observed project evidence. AI productivity adjustments are applied per module only when supported by concrete reuse, tooling, coverage, and ambiguity evidence. The deterministic Python publisher validates a versioned Structured Report Model, preserves it as JSON, renders skill-owned templates, publishes atomically, and updates the bounded CaseRecord metadata envelope.

## User Stories

1. **US-060-B-01 — Evidence-Based Assessment:** As a Technical Lead, I want the skill to inspect the actual implementation and dependencies at the selected depth so that the estimate reflects the real codebase.
2. **US-060-B-02 — Transparent Estimate:** As a Project Manager, I want module ranges, confidence, evidence, assumptions, benchmarks, and AI factors in the Effort Estimation v2 layout so that I can challenge or support a Vendor estimate fairly.
3. **US-060-B-03 — Executable Design:** As a Vendor Engineer, I want the Suggested Technical Design v2 report to combine adoption guidance with concrete contracts, data changes, sequences, work packages, tests, rollout, and rollback so that I can implement without repeating discovery.
4. **US-060-B-04 — Auditable Publication:** As an Auditor, I want the input, model, benchmark, skill, template, and report versions retained so that a result can be explained and re-rendered.
5. **US-060-B-05 — Offline Review:** As a Vendor reviewer, I want all three reports and Mermaid diagrams to work from the shared case folder without a server or CDN.
6. **US-060-B-06 — Safe Failure:** As a Project Manager, I want invalid or incomplete publication attempts to preserve the latest valid reports and expose a non-sensitive failure reason.

## Acceptance Criteria

### AC-060-B-01: Invocation and Case Contract

| AC ID | Criterion (Given/When/Then) | Test Type |
|---|---|---|
| AC-060-B-01a | GIVEN a readable FEATURE-060-A case folder and `quick`, `standard`, or `deep` depth WHEN the skill starts THEN it validates the CaseRecord metadata envelope, immutable input snapshot, evidence references, and local codebase before assessment | Integration |
| AC-060-B-01b | GIVEN an unsupported depth, missing snapshot, unreadable codebase, or malformed required metadata WHEN validation runs THEN assessment stops before report generation AND the publisher records a non-sensitive Failed reason without replacing valid outputs | Integration |
| AC-060-B-01c | GIVEN a valid case whose dominant narrative language can be determined WHEN reports are generated THEN all narrative content uses that language consistently AND identifiers, paths, API names, and code symbols remain unchanged | Unit |

### AC-060-B-02: Depth-Aware Inspection

| AC ID | Criterion (Given/When/Then) | Test Type |
|---|---|---|
| AC-060-B-02a | GIVEN Quick depth WHEN assessment runs THEN inspection covers explicitly targeted modules and their immediate implementation and test surfaces | Integration |
| AC-060-B-02b | GIVEN Standard depth WHEN assessment runs THEN inspection additionally covers dependencies, primary integration paths, data impact, and regression scope | Integration |
| AC-060-B-02c | GIVEN Deep depth WHEN assessment runs THEN inspection additionally covers the full reachable baseline, cross-module effects, systemic risks, and wider regression scope | Integration |
| AC-060-B-02d | GIVEN part of the selected depth is unreachable WHEN minimum required case inputs remain valid THEN the skill publishes qualified results that identify coverage gaps, required evidence, and reduced confidence rather than silently downgrading depth | Integration |

### AC-060-B-03: Evidence and Estimation

| AC ID | Criterion (Given/When/Then) | Test Type |
|---|---|---|
| AC-060-B-03a | GIVEN repository observations and a conflicting industry benchmark WHEN a module estimate is formed THEN observed project evidence takes precedence AND the benchmark remains visible as fallback or comparison context | Unit |
| AC-060-B-03b | GIVEN a decomposed module WHEN its estimate is reported THEN it includes low/high person-day range, confidence percentage, evidence references, assumptions, exclusions, uncertainty drivers, benchmark version, and adjustments | Unit |
| AC-060-B-03c | GIVEN a proposed AI productivity reduction WHEN module evidence does not demonstrate suitable reuse, tooling, coverage, and bounded ambiguity THEN no reduction is applied | Unit |
| AC-060-B-03d | GIVEN module evidence supports AI assistance WHEN a productivity factor is applied THEN its percentage, rationale, evidence, affected work, and limitations are shown for that module | Unit |
| AC-060-B-03e | GIVEN module ranges WHEN a total range is calculated THEN total low and high values reconcile deterministically with the included work packages and documented contingency rules | Unit |
| AC-060-B-03f | GIVEN Vendor effort evidence WHEN comparison is generated THEN overestimate, alignment, and underestimate outcomes are evaluated symmetrically AND negotiation guidance does not presume Vendor inflation | Unit |

### AC-060-B-04: Effort Estimation Report

| AC ID | Criterion (Given/When/Then) | Test Type |
|---|---|---|
| AC-060-B-04a | GIVEN a validated report model WHEN `EffortEstimation_AI_vN.html` renders THEN it follows the current v2 mockup hierarchy for verdict, Vendor comparison, module findings, adjustment factors, and negotiation guidance | UI |
| AC-060-B-04b | GIVEN multiple module findings WHEN a reviewer activates a module disclosure THEN its evidence, reuse, uncertainty, and adjustment detail expands or collapses with an exposed accessibility state | UI |
| AC-060-B-04c | GIVEN Vendor and AI ranges WHEN comparison is rendered THEN their numeric values and relationship remain understandable without color alone and in print | UI |

### AC-060-B-05: Suggested Technical Design

| AC ID | Criterion (Given/When/Then) | Test Type |
|---|---|---|
| AC-060-B-05a | GIVEN a validated assessment WHEN `SuggestedTechnicalDesign_AI_vN.html` renders THEN it follows the current v2 mockup's adoption summary and implementation guide hierarchy | UI |
| AC-060-B-05b | GIVEN the Vendor adopts the suggested solution WHEN reading the implementation guide THEN it provides reuse boundaries, component changes, interfaces, API and error contracts, data impacts, runtime sequences, edge decisions, and security constraints at implementation-ready detail | Unit |
| AC-060-B-05c | GIVEN ordered work packages WHEN the design is published THEN every package lists outputs, dependencies, estimated range, reuse savings, completion evidence, and traceability to requirements AND totals reconcile with the effort report | Unit |
| AC-060-B-05d | GIVEN migration or behavioral risk exists WHEN the design is published THEN rollout gates, stop conditions, rollback triggers/actions, tests, and acceptance evidence are explicit | Unit |

### AC-060-B-06: Structured Report Model and Templates

| AC ID | Criterion (Given/When/Then) | Test Type |
|---|---|---|
| AC-060-B-06a | GIVEN AI reasoning completes WHEN rendering begins THEN a schema-versioned Structured Report Model is validated before any HTML output is published | Integration |
| AC-060-B-06b | GIVEN a successful version `N` publication WHEN artifacts are inspected THEN `reports/report-model-vN.json` is retained with input snapshot, benchmark, skill, template, schema, and output version identifiers | Integration |
| AC-060-B-06c | GIVEN optional model sections are absent WHEN templates render THEN corresponding presentation blocks are omitted without empty placeholders or broken navigation | Unit |
| AC-060-B-06d | GIVEN model-provided text contains HTML or script syntax WHEN templates render THEN it is escaped as untrusted content and cannot execute | Unit |
| AC-060-B-06e | GIVEN the three skill-owned templates WHEN checked against the current mockups THEN they preserve the required layouts, styling hierarchy, navigation, interactive disclosures, and print behavior without hard-coded example case data | UI |

### AC-060-B-07: Mermaid Rendering

| AC ID | Criterion (Given/When/Then) | Test Type |
|---|---|---|
| AC-060-B-07a | GIVEN architecture, flow, sequence, state, class, or ER content WHEN represented in a report THEN the model stores Mermaid source and the template uses `<pre class="mermaid">` rather than pre-rendered image data | Unit |
| AC-060-B-07b | GIVEN a report folder is opened offline WHEN diagrams initialize THEN the pinned bundled Mermaid v11 ESM asset renders them with `startOnLoad: false`, `securityLevel: "strict"`, and explicit `mermaid.run(...)` | UI |
| AC-060-B-07c | GIVEN one diagram contains malformed Mermaid WHEN rendering executes THEN that diagram shows a local error and source fallback while all other report content remains usable | UI |
| AC-060-B-07d | GIVEN untrusted diagram labels WHEN reports render THEN click callbacks, loose security, and untrusted HTML labels remain disabled | Unit |

### AC-060-B-08: Atomic Publication and History

| AC ID | Criterion (Given/When/Then) | Test Type |
|---|---|---|
| AC-060-B-08a | GIVEN the latest valid report version is `N` WHEN publication succeeds THEN the publisher assigns `N+1`, atomically writes the model and three HTML outputs, and retains version `N` | Integration |
| AC-060-B-08b | GIVEN all new files are validated and committed WHEN publication completes THEN CaseRecord metadata atomically changes to Completed and points latest links at `N+1` while preserving history | Integration |
| AC-060-B-08c | GIVEN validation, rendering, or filesystem publication fails WHEN the run terminates THEN no partial output becomes latest, previous valid files remain readable, and CaseRecord records Failed with a non-sensitive reason | Integration |
| AC-060-B-08d | GIVEN two publishers target the same case version concurrently WHEN committing outputs THEN at most one claims the next version and neither overwrites the other's files | Integration |

## Functional Requirements

### FR-060-B-01: Skill Input and Validation

Accept exactly one case-folder path and one normalized analysis depth. Resolve all inputs from the immutable invocation snapshot and bounded CaseRecord metadata contract. Reject paths outside the case and assessed-code roots; never modify the assessed codebase.

### FR-060-B-02: Repository Inspection

Use AI capability to identify implementation surfaces, existing reusable assets, dependencies, data and integration impacts, tests, delivery risks, and unknowns. Record inspected paths and evidence summaries without copying sensitive source bodies into reports unnecessarily.

### FR-060-B-03: Estimation Method

Decompose work into modules and ordered work packages. Prefer actual project evidence, then apply named/versioned benchmark context and evidence-gated module-level AI factors. Produce deterministic total reconciliation and symmetric Vendor comparison.

### FR-060-B-04: Report Model

Produce one versioned JSON model containing case summary, provenance, scope coverage, evidence, module estimates, comparisons, design contracts, work packages, risks, tests, rollout/rollback, traceability, diagrams, and publication metadata. AI instructions create model data, not complete HTML strings.

### FR-060-B-05: Template Rendering

Own versioned CaseRecord, Effort Estimation, and Suggested Technical Design templates derived from the linked mockups. Templates share theme tokens, metadata conventions, safe injection, conditional sections, accessible controls, responsive layout, and print styles.

### FR-060-B-06: Publication

The Python publisher validates model and template compatibility, reserves the next monotonic version, renders to temporary files, validates outputs, atomically commits the complete set, retains model JSON and prior versions, and finally updates CaseRecord metadata/status.

## Non-Functional Requirements

### NFR-060-B-01: Integrity and Reproducibility

- A completed publication is all-or-nothing and never replaces prior valid history.
- Each result records input snapshot, benchmark dataset, skill, template, model schema, report, and Mermaid asset versions.
- Given the retained model and compatible templates, report rendering is repeatable without rerunning AI reasoning.

### NFR-060-B-02: Security and Privacy

- Treat all case, model, and Mermaid content as untrusted; escape HTML by default and keep Mermaid strict.
- Canonicalize filesystem paths and confine writes to the case folder.
- Do not include secrets, credentials, or unnecessary source text in reports or failure reasons.
- Do not call external assessment services or automatically upload repository content.

### NFR-060-B-03: Offline and Portability

- Report text, styling, navigation, disclosures, print layouts, and diagrams work from the shared folder without an application server or CDN.
- Generated reports use relative links within their case bundle.

### NFR-060-B-04: Accessibility

- Reports meet WCAG 2.1 AA expectations for semantics, keyboard access, visible focus, contrast, non-color meaning, disclosures, and error states.
- Report navigation and content remain usable when Mermaid fails or JavaScript is unavailable.

### NFR-060-B-05: Compatibility

- Publisher updates preserve unknown forward-compatible CaseRecord metadata.
- Schema/template incompatibility fails before publication with an actionable non-sensitive message.
- The skill supports the Python runtime and skill package conventions used by X-IPE.

## UI/UX Requirements

- CaseRecord follows the linked CR Assessment mockup's CIO slide hierarchy and exposes latest and historical report links.
- Effort Estimation follows the v2 mockup's verdict-first hierarchy, comparison tracks, expandable module cards, transparent factor table, and negotiation guidance.
- Suggested Technical Design follows the v2 mockup's two-level reading path: executive adoption summary followed by implementation-ready contracts and delivery controls.
- All templates use content-driven sections, responsive single-column adaptation, keyboard-operable native controls, visible focus, and print-safe page breaks.
- Visual status, confidence, estimate relationships, and risk severity never rely on color alone.
- Example values from mockups are replaced exclusively through validated model fields.

## Dependencies

| Dependency | Requirement |
|---|---|
| FEATURE-060-A | Case folder, immutable snapshot, evidence references, CaseRecord envelope, lifecycle, and Console invocation contracts |
| `x-ipe-meta-skill-creator` | Mandatory candidate-first process for creating and validating the task-based skill |
| Python 3 runtime | Deterministic schema validation, safe template rendering, version reservation, atomic publication, and metadata update |
| Bundled Mermaid v11 ESM | Pinned offline diagram rendering asset; no CDN dependency |
| Versioned benchmark assets | Immutable benchmark identifiers, sources, ranges, and applicability notes packaged with the skill |

## Business Rules

1. Repository evidence outranks generic benchmarks when they conflict.
2. AI productivity never applies as a blanket project discount; every adjustment is module-specific and evidence-gated.
3. A qualified result must distinguish inspected, inferred, and unverified scope and reduce confidence accordingly.
4. Vendor comparison is symmetric and may conclude overestimate, alignment, underestimate, or insufficient evidence.
5. All three reports and the versioned model form one publication transaction.
6. The report narrative follows the dominant case language; technical identifiers remain verbatim.

## Edge Cases

- Missing optional supporting documents lower evidence strength but do not invalidate otherwise complete mandatory inputs.
- Binary or unreadable evidence is referenced and flagged rather than silently interpreted.
- Empty target discovery, cyclic dependencies, generated/vendor code, monorepos, and unsupported languages must be reported in coverage notes.
- Missing Vendor module decomposition requires the comparison to state allocation assumptions explicitly.
- Concurrent publication, disk exhaustion, permission loss, malformed templates, invalid model data, and CaseRecord revision conflicts must preserve the last valid result.
- Malformed Mermaid affects only its own diagram region.

## Out of Scope

- Modifying the assessed repository or applying the suggested design.
- Calling an assessment service API, running a background service, or automatically submitting the Console command.
- External web research during a case assessment; benchmark assets are curated and versioned before release.
- Knowledge-graph writes, Vendor workflow management, report editing, approval automation, or commercial decision enforcement.
- Guaranteeing elapsed assessment durations displayed illustratively in mockups.

## Technical Considerations

- Keep AI reasoning, schema validation, template rendering, and atomic publication as separate responsibilities.
- Define explicit compatibility among skill, benchmark, Structured Report Model, template, Mermaid asset, and CaseRecord schema versions.
- Use durable version reservation and same-filesystem atomic replacement so concurrency and failure behavior are testable.
- Template and publisher implementation must be created through the mandatory `x-ipe-meta-skill-creator` candidate workflow rather than directly editing a live skill.
