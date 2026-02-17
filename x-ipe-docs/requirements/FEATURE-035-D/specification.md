# Specification: Requirement-Details Epic Format

> Feature ID: FEATURE-035-D
> Version: v1.0
> Status: Refined
> Last Updated: 02-17-2026
> Dependencies: FEATURE-035-A

---

## Overview

Update the requirement-details index to use EPIC-based ranges instead of FEATURE-based ranges. The template and file-splitting heuristic were already updated in FEATURE-035-A.

### Scope

1. Update `requirement-details-index.md` to reference EPIC ranges
2. Verify template and file-splitting already have EPIC format (done in 035-A)
3. The actual content migration of requirement-details parts 1-9 (converting `## FEATURE-XXX` headers to `## EPIC-XXX` with nested features) is deferred to FEATURE-035-E (Retroactive Migration)

---

## Acceptance Criteria

### AC-035-D.1: Index uses EPIC ranges
`requirement-details-index.md` references EPIC ranges (e.g., `EPIC-001 to EPIC-005`) instead of Feature ranges

### AC-035-D.2: Template uses Epic format
`requirement-details-template.md` has `## EPIC-{nnn}:` section header (verified from 035-A)

### AC-035-D.3: File-splitting uses Epic grouping
`file-splitting.md` shows EPIC-based ranges in examples (verified from 035-A)

### AC-035-D.4: Index has consistent column headers
Index table uses consistent format with "Epics Covered" column

### AC-035-D.5: Legacy compatibility note
Index includes note that current content uses legacy Feature format pending migration

---

## Files to Modify

| File | Changes |
|------|---------|
| `x-ipe-docs/requirements/requirement-details-index.md` | Update "Features Covered" column to "Epics Covered" with EPIC ranges, add legacy note |
