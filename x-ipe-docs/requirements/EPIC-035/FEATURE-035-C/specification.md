# Specification: Feature Lifecycle Skill Updates

> Feature ID: FEATURE-035-C
> Version: v1.0
> Status: Refined
> Last Updated: 02-17-2026
> Dependencies: FEATURE-035-A, FEATURE-035-B

---

## Overview

Update all feature lifecycle skills to use Epic-aware paths and naming in their reference/example files. Also update git commit message format to reference `FEATURE-{nnn}-{X}` IDs.

### Scope

Update reference/example files in 8 skills:
1. x-ipe-task-based-change-request — references/examples.md, references/patterns.md
2. x-ipe-task-based-feature-refinement — references/examples.md
3. x-ipe-task-based-technical-design — references/design-templates.md, references/examples.md
4. x-ipe-task-based-test-generation — references/examples.md
5. x-ipe-task-based-code-implementation — references/examples.md
6. x-ipe-task-based-feature-acceptance-test — references/examples.md
7. x-ipe-task-based-feature-closing — references/examples.md
8. x-ipe-tool-git-version-control — SKILL.md, references/commit-message-format.md, references/examples.md

---

## Acceptance Criteria

### AC-035-C.1: Change Request paths updated
Old `FEATURE-XXX/` paths in examples/patterns → `EPIC-XXX/FEATURE-XXX-X/`

### AC-035-C.2: Feature Refinement paths updated
Old `FEATURE-XXX/specification.md` → `EPIC-XXX/FEATURE-XXX-X/specification.md`

### AC-035-C.3: Technical Design paths updated
Old `FEATURE-XXX/technical-design.md` → `EPIC-XXX/FEATURE-XXX-X/technical-design.md`

### AC-035-C.4: Test Generation paths updated
Old `FEATURE-XXX/technical-design.md` → `EPIC-XXX/FEATURE-XXX-X/technical-design.md`

### AC-035-C.5: Code Implementation paths updated
Old `FEATURE-XXX/technical-design.md` → `EPIC-XXX/FEATURE-XXX-X/technical-design.md`

### AC-035-C.6: Feature Acceptance Test paths updated
Old `FEATURE-XXX/acceptance-test-cases.md` → `EPIC-XXX/FEATURE-XXX-X/acceptance-test-cases.md`

### AC-035-C.7: Feature Closing paths updated
Old `FEATURE-XXX/` paths → `EPIC-XXX/FEATURE-XXX-X/`

### AC-035-C.8: Git commit format updated
Feature IDs in commit messages use `FEATURE-XXX-X` format with letter suffix

### AC-035-C.9: Legacy note in examples
All updated example files include a note that examples use legacy feature numbering where applicable

### AC-035-C.10: No old-format FEATURE-{nnn}/ paths remain
Grep across all 8 skills returns zero matches for `FEATURE-\d{3}/` pattern

---

## Files to Modify

| File | Changes |
|------|---------|
| `.github/skills/x-ipe-task-based-change-request/references/examples.md` | Update FEATURE-013/, FEATURE-005/ paths |
| `.github/skills/x-ipe-task-based-change-request/references/patterns.md` | Update FEATURE-015/ path |
| `.github/skills/x-ipe-task-based-feature-refinement/references/examples.md` | Update FEATURE-001/ paths |
| `.github/skills/x-ipe-task-based-technical-design/references/design-templates.md` | Update FEATURE-001/ links |
| `.github/skills/x-ipe-task-based-technical-design/references/examples.md` | Update FEATURE-001/, FEATURE-007/ paths |
| `.github/skills/x-ipe-task-based-test-generation/references/examples.md` | Update FEATURE-001/, FEATURE-003/ paths |
| `.github/skills/x-ipe-task-based-code-implementation/references/examples.md` | Update FEATURE-001/ paths |
| `.github/skills/x-ipe-task-based-feature-acceptance-test/references/examples.md` | Update FEATURE-008/, FEATURE-010/ paths |
| `.github/skills/x-ipe-task-based-feature-closing/references/examples.md` | Update FEATURE-002/ path |
| `.github/skills/x-ipe-tool-git-version-control/SKILL.md` | Update feature_id format |
| `.github/skills/x-ipe-tool-git-version-control/references/commit-message-format.md` | Update all FEATURE-XXX IDs to FEATURE-XXX-X |
| `.github/skills/x-ipe-tool-git-version-control/references/examples.md` | Update feature_id example |
