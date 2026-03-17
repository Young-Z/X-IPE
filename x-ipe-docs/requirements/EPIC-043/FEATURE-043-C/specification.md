# Feature Specification: Skill Path Convention Updates

> Feature ID: FEATURE-043-C
> Epic ID: EPIC-043
> Version: v1.0
> Status: Refined
> Last Updated: 03-04-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-04-2026 | Initial specification |

## Linked Mockups

No mockups — this feature modifies SKILL.md documentation files only; no UI component.

## Overview

FEATURE-043-C ensures all markdown-generating skills produce internal links using full project-root-relative paths (e.g., `x-ipe-docs/requirements/EPIC-XXX/specification.md`, `.github/skills/x-ipe-task-based-XXX/SKILL.md`). This is a prerequisite for FEATURE-043-D (Existing File Migration) and ensures the link preview system from FEATURE-043-A/B can resolve all future links.

**Target users:** Agent developers (skills produce correctly formatted links), end-users (preview works on newly generated docs).

## User Stories

1. **US-043-C.1:** As a developer generating documentation via skills, I want all internal links to use full root-relative paths, so the File Link Preview feature can intercept and render them.

2. **US-043-C.2:** As a skill creator, I want the skill creator template to include the path convention, so newly created skills automatically comply.

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| None | - | - |

## Functional Requirements

### FR-043-C.1: Skill Constraint Addition

- **FR-043-C.1.1:** Each of the 12 skills listed below MUST have the following constraint added to a `<constraints>` section within their execution procedure:

> "All internal markdown links MUST use full project-root-relative paths (e.g., `x-ipe-docs/requirements/EPIC-XXX/specification.md`, `.github/skills/x-ipe-task-based-XXX/SKILL.md`). Do NOT use relative paths like `../` or `./`."

- **FR-043-C.1.2:** The 12 target skills are:
  1. `x-ipe-task-based-ideation-v2`
  2. `x-ipe-task-based-feature-refinement`
  3. `x-ipe-task-based-technical-design`
  4. `x-ipe-task-based-requirement-gathering`
  5. `x-ipe-task-based-feature-breakdown`
  6. `x-ipe-task-based-change-request`
  7. `x-ipe-task-based-idea-to-architecture`
  8. `x-ipe-task-based-feature-acceptance-test`
  9. `x-ipe-task-based-refactoring-analysis`
  10. `x-ipe-task-based-improve-code-quality`
  11. `x-ipe-task-based-code-implementation`
  12. `x-ipe-task-based-user-manual` _(deprecated → x-ipe-tool-readme-updator)_

- **FR-043-C.1.3:** The constraint MUST be placed in an existing `<constraints>` block of the primary output-generating step. If no `<constraints>` block exists, add one to the step that produces markdown output.

### FR-043-C.2: Skill Creator Template Update

- **FR-043-C.2.1:** The `x-ipe-meta-skill-creator` skill template(s) MUST include the path convention constraint in the default output template for all future task-based skills.

- **FR-043-C.2.2:** The constraint text in templates MUST match FR-043-C.1.1 exactly.

## Non-Functional Requirements

- **NFR-043-C.1:** Changes are backward compatible — no existing behavior is broken.
- **NFR-043-C.2:** Each skill change is independently reviewable.

## Acceptance Criteria

### Breadcrumb Navigation

N/A — this feature has no UI component.

### Skill Constraint Updates

- **AC-043-C.1:** All 12 skills listed in FR-043-C.1.2 have the path convention constraint in a `<constraints>` section of their primary output step.
- **AC-043-C.2:** The constraint text matches: "All internal markdown links MUST use full project-root-relative paths (e.g., `x-ipe-docs/requirements/EPIC-XXX/specification.md`, `.github/skills/x-ipe-task-based-XXX/SKILL.md`). Do NOT use relative paths like `../` or `./`."
- **AC-043-C.3:** `x-ipe-meta-skill-creator` template updated with the path convention constraint.
- **AC-043-C.4:** Newly generated skill outputs (from skill-creator) include the path convention constraint by default.

### Non-Regression

- **AC-043-C.5:** All 12 skills remain valid (SKILL.md structure not broken).
- **AC-043-C.6:** Existing skill behavior is unchanged (only a constraint is added).

## Technical Scope

- **Scope:** Documentation/skill configuration files only (`.github/skills/*/SKILL.md`)
- **No frontend, no backend, no tests needed** — this is a documentation-only change.
- **Implementation approach:** Direct edits to each SKILL.md file's `<constraints>` block.

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Constraint placed in wrong step | Low | Low | Verify each skill's output-generating step |
| Template update breaks skill creator | Low | Medium | Validate template structure after change |
