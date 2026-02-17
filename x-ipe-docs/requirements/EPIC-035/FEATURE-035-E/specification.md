# Specification: Retroactive Feature Migration

> Feature ID: FEATURE-035-E
> Version: v1.0
> Status: Refined
> Last Updated: 02-17-2026
> Dependencies: FEATURE-035-A, FEATURE-035-B, FEATURE-035-C, FEATURE-035-D

---

## Overview

Migrate all existing feature folders from `x-ipe-docs/requirements/FEATURE-{nnn}/` to `EPIC-{nnn}/FEATURE-{nnn}-{X}/` structure. Update features.md with Epic ID column for all features.

### Migration Plan

#### Phase 1: Standalone features → single-feature Epics
Move `FEATURE-{nnn}/` → `EPIC-{nnn}/FEATURE-{nnn}-A/`

Features: 001, 002, 003, 004, 005, 006, 008, 009, 010, 011, 012, 013, 014, 015, 016, 018, 021, 024, 026, 031, 033

#### Phase 2: Multi-feature groups → Epics
Move `FEATURE-{nnn}-{X}/` → `EPIC-{nnn}/FEATURE-{nnn}-{X}/`

Groups: 022, 023, 025, 027, 028, 029, 030, 035

#### Phase 3: Update features.md with Epic ID column

#### Phase 4: Update requirement-details parts 1-9 headers

---

## Acceptance Criteria

### AC-035-E.1: All standalone features moved
No `FEATURE-{nnn}/` (without letter suffix) remains at top level of requirements/

### AC-035-E.2: All multi-feature groups moved
All groups under EPIC parent folders

### AC-035-E.3: Features.md has Epic ID column
Every feature row has its Epic ID

### AC-035-E.4: No broken links
All specification.md, technical-design.md links in features.md point to valid files

### AC-035-E.5: Git history preserved
Moves done via `git mv` to preserve history
