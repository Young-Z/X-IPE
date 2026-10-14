# Feature Specification Template

Use this complete scaffold for one feature. Preserve established EN/ZH prose,
stable IDs and unaffected sections during CR; placeholders are not completion.

---

## Specification Structure

```markdown
# Feature Specification: {Feature Title}

> Feature ID: {actual legacy FEATURE-XXX or FEATURE-XXX-X}  
> Version: {actual approved vX.Y}  
> Status: {specification readiness; not a fabricated board transition}  
> Last Updated: MM-DD-YYYY

## Version History

| Version | Date | Description | Change Request |
| --- | --- | --- | --- |
| v1.0 | MM-DD-YYYY | Initial specification | {N/A or actual CR link} |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| Dashboard Main | HTML | [x-ipe-docs/requirements/{EPIC-ID}/mockups/dashboard-v1.html](x-ipe-docs/requirements/{EPIC-ID}/mockups/dashboard-v1.html) | Main dashboard layout | current | MM-DD-YYYY |

> **Path Convention:** Use full project-root-relative paths for mockup links (e.g., `x-ipe-docs/requirements/EPIC-XXX/mockups/file.html`).
> This enables the link preview feature (IDEA-033) — clicking opens an in-app DeliverableViewer modal.
> Do NOT use relative paths like `../mockups/` or `../../mockups/`.
>
> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".  
> Mockups marked as "outdated" are directional references only -- do not use for AC comparison.
>
> **Conflict Resolution:** Compare content, authorized scope and SHA256 revisions.
> Linked Date is provenance, not automatic precedence. A material divergence needs
> an explicit scoped decision under the resolved interaction policy; do not make
> a newer mockup override approved requirements merely because of its date.

## Overview
[2-3 paragraph description: what, why, who]

## User Stories
[US-{stable ID}: As a [user], I want to [action], so that [benefit]]
[Map current in-scope mockup element IDs and source requirements where applicable]

## Goal / Subgoal Coverage

| Goal ID | Parent / Source | Stakeholder | Desired Observable Outcome | Contribution / Selection | Success Evidence | Constraints / Non-goals | AC Links | Outcome State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {stable US/FR ID or optional doc-local G} | {parent requirement/source anchor; labeled inferred for legacy explicit so-that} | {beneficiary} | {observable change, not artifact name} | {credible contribution; all-required or selected bounded alternative} | {known measure or qualitative scenario; planned versus actual observation} | {limits} | {stable GWT AC IDs} | {not measured or observed stakeholder outcome with source} |

{New/changed scope requires honest coverage, not invented measurement. Keep goal
count bounded by coherent scope; no fixed minimum/three-goal cap. Unchanged legacy
content is not rewritten; ambiguous inference blocks only its pertinent claim.}

## Acceptance Criteria

### AC-XXX-01: {AC Group Name}

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-XXX-01a | GIVEN [precondition] WHEN [action] THEN [expected outcome] | UI / API / Unit / Integration |
| AC-XXX-01b | GIVEN [context] WHEN [event] THEN [result] AND [additional result] | UI / API / Unit / Integration |

### AC-XXX-02: {AC Group Name}

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-XXX-02a | GIVEN [precondition] WHEN [action] THEN [expected outcome] | UI / API / Unit / Integration |

> **Test Type Legend:**
> - **UI** — Browser/DOM interaction test (clicks, renders, layout)
> - **API** — HTTP request/response test (status codes, response body)
> - **Unit** — Isolated function/module test (parsing, calculations)
> - **Integration** — Multi-component interaction test (service + DB)

## Functional Requirements
[FR-N: Requirement with Input/Process/Output]

## Non-Functional Requirements
[NFR-{stable ID}: measurable Performance, Security, Scalability, Reliability,
Accessibility and data/privacy constraints, or explicit justified N/A]

## UI/UX Requirements
[Wireframes, User Flows, UI Elements]

## Dependencies
[Internal and External]

## Business Rules
[BR-N: Clear rule statements]

## Edge Cases & Constraints
[Scenarios with expected behavior]

## Out of Scope
[What is NOT included]

## Technical Considerations
[Hints for technical design - WHAT not HOW]

## Open Questions
[What needs clarification]
[Material unanswered questions block completion; resolved answers carry decision evidence]

## Acceptance Traceability

| Source Requirement / FR / NFR | User Story | AC ID | Mockup Element / Status | Primary Validation | Coverage / CR Decision |
| --- | --- | --- | --- | --- | --- |
| {actual stable source ID} | {US-ID} | {AC-ID} | {element/current or N/A} | {UI/API/Unit/Integration plan; not invented passing result} | {covered or approved deferral / CR link} |

## Context and Verification Evidence

{Source/parts/index/specification/board/mockup SHA256, reused findings and affected
delta, confirmation revision, known blockers, affected downstream evidence invalidation}
{Actual artifact paths; workflow readback or honest free-mode/blocked result;
lifecycle board specification_link/status handoff, no manual JSON writes}

| AC ID | Validation Evidence | Delivery State | Outcome State |
| --- | --- | --- | --- |
| {stable AC ID from coverage} | {planned UI/API/Unit/Integration scenario or actual command/result + revision; not a fabricated pass} | {planned / verified engineering delivery / invalidated by goal delta} | {not measured or observed stakeholder outcome + actual source} |

{CR parent goal/source delta and affected evidence invalidation; unaffected
IDs/evidence retained. Passing delivery tests do not prove stakeholder outcome.}
```

---

## Version History Rules

MANDATORY: Maintain ONE specification file per feature with version history inside.

- Keep single `specification.md` file with Version History table
- Do NOT create versioned files like `specification-v2.md`
- Approved additive CR may use v1.1/v1.2; major redesign may use v2.0.
- Preserve prior version/CR rows; unchanged resume has no version bump.
- Update affected content in place; stable US/FR/AC IDs and language stay intact.

---

## Specification Quality Checklist

- [ ] All acceptance criteria use Given/When/Then (GWT) format
- [ ] All acceptance criteria are testable
- [ ] All acceptance criteria have a Test Type assigned (UI/API/Unit/Integration)
- [ ] User stories provide clear value
- [ ] Functional requirements are complete
- [ ] Non-functional requirements defined
- [ ] Dependencies clearly stated
- [ ] Edge cases identified
- [ ] Out of scope explicitly listed
- [ ] Mockups linked and analyzed (if applicable)
- [ ] Current in-scope mockups mapped to stories/UI/ACs; outdated directional only
- [ ] Source/story/AC/validation traceability and approved CR/deferral records complete
- [ ] New/changed goal/source/parent/story/AC/evidence coverage and outcome gaps honest
- [ ] Material open questions resolved; exact-revision confirmation recorded
