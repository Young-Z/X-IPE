# Specification: Feature Board Epic Tracking

> Feature ID: FEATURE-035-B
> Version: v1.0
> Status: Refined
> Last Updated: 02-17-2026
> Dependencies: FEATURE-035-A

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-17-2026 | Initial specification |

---

## Overview

Add an `Epic ID` column to the features.md tracking table and update the feature-board-management skill to support Epic-based organization. Epic status is derived (not stored) — computed from constituent Feature statuses.

### Scope

**In scope:**
- Add `Epic ID` column to features.md table
- Update feature-board-management SKILL.md for `epic_id` parameter
- Update templates/features.md template
- Update references/examples.md with Epic examples
- Specification links use `EPIC-{nnn}/FEATURE-{nnn}-{X}/` paths

**Out of scope:**
- Modifying other lifecycle skills (FEATURE-035-C)
- Migrating existing features (FEATURE-035-E)
- Separate Epic status column (derived, not stored)

---

## Acceptance Criteria

### AC-035-B.1: Epic ID Column in Features Table
**Given** the features.md tracking table
**When** features are listed
**Then** the table includes an `Epic ID` column after `Feature ID`

### AC-035-B.2: Table Sort Order
**Given** features listed in features.md
**When** multiple Epics have features
**Then** rows are sorted primarily by Epic ID, secondarily by Feature suffix letter

### AC-035-B.3: Feature Board Management — Epic ID Input
**Given** the feature-board-management skill input parameters
**When** `create_or_update_features` operation is called
**Then** the features list accepts an `epic_id` field per feature

### AC-035-B.4: Feature Board Management — Epic ID Population
**Given** a feature is created via feature-board-management
**When** `epic_id` is provided in the input
**Then** the Epic ID column is populated in features.md

### AC-035-B.5: Feature Data Model — Epic ID
**Given** the Feature Data Model schema
**When** querying a feature
**Then** the response includes `epic_id` field

### AC-035-B.6: Specification Link Format
**Given** a feature with an Epic ID
**When** the specification link is set
**Then** it uses the path format `../requirements/EPIC-{nnn}/FEATURE-{nnn}-{X}/specification.md`

### AC-035-B.7: Template Updated
**Given** the features.md template at `templates/features.md`
**When** a new board is created
**Then** it includes the `Epic ID` column

### AC-035-B.8: Examples Updated
**Given** the references/examples.md file
**When** an agent reads integration examples
**Then** examples show `epic_id` in Feature Data Model, create operations, and board structure

### AC-035-B.9: Backward Compatibility
**Given** existing features without an Epic ID (legacy)
**When** the board is read or queried
**Then** the `Epic ID` column shows `-` for legacy features

### AC-035-B.10: Epic Status Derivation Note
**Given** the feature-board-management SKILL.md
**When** an agent reads about Epic status
**Then** a note explains that Epic status is derived from constituent Feature statuses (not stored as a separate column)

---

## Functional Requirements

### FR-035-B.1: Features.md Table Schema
The features.md tracking table MUST have this column order:
`| Epic ID | Feature ID | Feature Title | Version | Status | Specification Link | Created | Last Updated |`

### FR-035-B.2: Epic ID Column Values
- New features: populated with `EPIC-{nnn}` matching the parent Epic
- Legacy features (no Epic): populated with `-`

### FR-035-B.3: Sort Order
Features MUST be sorted by:
1. Epic ID (ascending, `-` legacy features at top)
2. Feature suffix letter within same Epic (A, B, C...)

### FR-035-B.4: Input Parameter Update
The `create_or_update_features` input MUST accept `epic_id` per feature:
```yaml
features:
  - feature_id: "FEATURE-035-A"
    epic_id: "EPIC-035"
    title: "..."
```

### FR-035-B.5: Feature Data Model Update
The Feature Data Model MUST include:
```yaml
Feature:
  epic_id: EPIC-XXX | null  # Parent Epic ID
  feature_id: FEATURE-XXX-X
  ...
```

### FR-035-B.6: Specification Link Path
Specification links for Epic-organized features MUST use:
`../requirements/EPIC-{nnn}/FEATURE-{nnn}-{X}/specification.md`

### FR-035-B.7: Query Feature Response
The `query_feature` operation response MUST include `epic_id`.

### FR-035-B.8: Template File
The `templates/features.md` MUST include the `Epic ID` column with example row.

### FR-035-B.9: Examples File
The `references/examples.md` MUST show `epic_id` in:
- Feature Data Model schema
- Create operation examples
- Board template structure
- Query response examples
- Category closing examples

---

## Non-Functional Requirements

### NFR-035-B.1: Minimal Changes
Only modify files within the `x-ipe+feature+feature-board-management/` skill folder. Do NOT modify the actual `features.md` board (that's FEATURE-035-E migration).

### NFR-035-B.2: Backward Compatibility
All operations MUST work with features that lack an `epic_id` (treat as `-`).

---

## Business Rules

### BR-035-B.1: Epic Status Derivation
Epic status is computed from constituent Feature statuses:
- All Features `Completed` → Epic is complete
- Any Feature `in_progress` / active → Epic is in progress
- All Features `Planned` → Epic is planned
- No separate Epic status column in the table

### BR-035-B.2: No Epic-Only Rows
The features table does NOT have standalone Epic rows. Epics are represented only via the `Epic ID` column on Feature rows.

---

## Edge Cases

### EC-035-B.1: Single-Feature Epic
An Epic with only one Feature (e.g., EPIC-026 → FEATURE-026-A). The Epic ID column shows `EPIC-026` for that single feature row.

### EC-035-B.2: Legacy Features Without Epic
Features created before Epic system (e.g., FEATURE-001). Epic ID shows `-`.

### EC-035-B.3: Mixed Legacy and Epic Features
The board may contain both `-` (legacy) and `EPIC-{nnn}` entries. Sort puts legacy at top.

---

## Files to Modify

| File | Change |
|------|--------|
| `.github/skills/x-ipe+feature+feature-board-management/SKILL.md` | Add epic_id to input params, Feature Data Model, query output, derivation note |
| `.github/skills/x-ipe+feature+feature-board-management/templates/features.md` | Add Epic ID column to table |
| `.github/skills/x-ipe+feature+feature-board-management/references/examples.md` | Update all examples with epic_id |
