# Feature Specification Template

> Reference from SKILL.md: `See [references/specification-template.md](references/specification-template.md)`

---

## Specification Structure

```markdown
# Feature Specification: {Feature Title}

> Feature ID: FEATURE-XXX  
> Version: v1.0  
> Status: Refined  
> Last Updated: MM-DD-YYYY

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | MM-DD-YYYY | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| Dashboard Main | HTML | [mockups/dashboard-v1.html](mockups/dashboard-v1.html) | Main dashboard layout | current | MM-DD-YYYY |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".  
> Mockups marked as "outdated" are directional references only -- do not use for AC comparison.
>
> **Conflict Resolution:** If specification and mockup diverge, compare Linked Date vs spec Last Updated.
> If the mockup is newer and not stale → mockup takes precedence (update spec to match).
> If the spec is newer → spec takes precedence (mockup may need refresh).

## Overview
[2-3 paragraph description: what, why, who]

## User Stories
[As a [user], I want to [action], so that [benefit]]

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
[Performance, Security, Scalability]

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
```

---

## Version History Rules

MANDATORY: Maintain ONE specification file per feature with version history inside.

- Keep single `specification.md` file with Version History table
- Do NOT create versioned files like `specification-v2.md`
- Increment version in document header (v1.0 -> v2.0)
- Update content in place with new version

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
