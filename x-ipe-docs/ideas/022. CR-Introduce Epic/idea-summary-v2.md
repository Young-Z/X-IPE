# Idea Summary

> Idea ID: IDEA-022
> Folder: 022. CR-Introduce Epic
> Version: v2
> Created: 2026-02-17
> Status: Refined

## Overview

Introduce an **Epic** layer into X-IPE's requirement management workflow, sitting above Features. Epics group related Features under a single deliverable unit, replacing the current ad-hoc sub-feature pattern (e.g., `FEATURE-030-B-THEME`, `FEATURE-030-B-MOCKUP`) with a formal hierarchy: **Epic → Features**.

## Problem Statement

As the project grows, individual Features frequently expand beyond their original scope. A single Feature can no longer cover all required functionality, leading to organic splitting into sub-features with inconsistent naming (e.g., `FEATURE-030-B`, `FEATURE-030-B-THEME`, `FEATURE-030-B-MOCKUP`). There is no formal structure to:

1. Group related Features under a parent concept
2. Define high-level acceptance criteria that span multiple Features
3. Track the overall progress of a "big idea" across its constituent Features
4. Store shared artifacts (mockups, references) at the group level

## Target Users

- **X-IPE Agent sessions** — agents following the requirement/feature workflow
- **Human project managers** — reviewing and planning work across Epics
- **Developers** — understanding how Features relate to the bigger picture

## Proposed Solution

### Workflow Change

```mermaid
flowchart LR
    RG[Requirement Gathering] --> EC[Create EPIC-nnn/ folder]
    EC --> AC["Define Epic-level ACs<br/>in requirement-details"]
    AC --> MK["Store mockups in<br/>EPIC-nnn/mockups/"]
    MK --> FB[Feature Breakdown]
    FB --> FA["FEATURE-nnn-A/"]
    FB --> FBf["FEATURE-nnn-B/"]
    FB --> FC["FEATURE-nnn-C/"]
    FA --> SPEC["specification.md<br/>technical-design.md<br/>acceptance-test-cases.md"]
```

### Folder Structure

```
x-ipe-docs/requirements/
  EPIC-030/
    mockups/                       ← shared mockups at Epic level
    FEATURE-030-A/
      specification.md
      technical-design.md
      acceptance-test-cases.md
    FEATURE-030-B/
      specification.md
      technical-design.md
      acceptance-test-cases.md
```

**Epic folder contents:**
- `mockups/` — shared visual artifacts referenced by all child Features
- `FEATURE-{nnn}-{X}/` — sub-folders for each Feature
- No `specification.md` at Epic level — all functional specs live in Features
- No separate metadata file — the Epic's identity and ACs are defined in `requirement-details-part-N.md`

### Naming Convention

| Entity | Pattern | Example |
|--------|---------|---------|
| Epic | `EPIC-{nnn}` | `EPIC-030` |
| Feature | `FEATURE-{nnn}-{A\|B\|C...}` | `FEATURE-030-A` |

- The `{nnn}` in Feature **always follows** its parent Epic's number
- Every requirement gets an Epic (even single-feature requirements, for consistency)

### features.md Changes

Add an **Epic ID** column to the flat table, sorted by Epic ID:

| Epic ID | Feature ID | Title | Version | Status | Specification |
|---------|------------|-------|---------|--------|---------------|
| EPIC-030 | FEATURE-030-A | Toolbar Shell | v2.0 | Completed | [spec](EPIC-030/FEATURE-030-A/specification.md) |
| EPIC-030 | FEATURE-030-B | Theme Mode | v2.0 | Completed | [spec](EPIC-030/FEATURE-030-B/specification.md) |
| EPIC-031 | FEATURE-031-A | Console Core | v1.0 | Implemented | [spec](EPIC-031/FEATURE-031-A/specification.md) |

### requirement-details Format Change

Current format:
```markdown
## FEATURE-030: UIUX Reference Toolbar
### Acceptance Criteria
...
```

New format:
```markdown
## EPIC-030: UIUX Reference Toolbar
### Epic-Level Acceptance Criteria
...
### Features
- FEATURE-030-A: Toolbar Shell
- FEATURE-030-B: Theme Mode
```

**Splitting heuristic stays the same**: parts are organized by number ranges but now reference `EPIC-{nnn}` headers instead of `FEATURE-{nnn}` headers.

### Epic Status Tracking

Epic status is **computed dynamically** from its constituent Features:

| All Features Status | Epic Status |
|---------------------|-------------|
| All Completed | Completed |
| Any In Progress | In Progress |
| Any Planned, none In Progress | Planned |
| Mixed Completed + Planned | Partially Complete |

No separate Epic status column in `features.md` — derived on read by sorting/grouping the Epic ID column.

### Key Design Decisions

1. **Always Epic** — every requirement creates an Epic, even for single-feature work (consistency > flexibility)
2. **No Epic-level specification.md** — all functional specs live at Feature level; Epic folder holds shared mockups only
3. **Epic-level ACs in requirement-details** — acceptance criteria written at Epic scope during Requirement Gathering, distributed to Features during Breakdown
4. **Mockups at Epic level only** — Features reference `../mockups/` from the Epic folder, no duplicate mockups per Feature
5. **Full retroactive migration** — all existing features reorganized under Epics after skill updates
6. **Epic status is derived** — computed from Feature statuses, no separate tracking needed

## Key Features

```mermaid
mindmap
  root((Epic Layer))
    Requirement Gathering
      Create EPIC-nnn/ folder
      Define Epic-level ACs
      Store mockups in EPIC/mockups/
    Feature Breakdown
      Create FEATURE-nnn-X/ sub-folders
      Distribute ACs to Features
      Reference Epic mockups
    Tracking
      Epic ID column in features.md
      Sort by Epic ID
      Derived Epic status
    Migration
      Update all skills first
      Re-organize existing features
      Update all path references
      Validate link integrity
```

## Migration Plan

### Strategy: Skills First, Then Data

```mermaid
flowchart TD
    S1["Phase 1: Update Skills<br/>(support both old + new paths)"] --> S2["Phase 2: Migrate Data<br/>(re-organize folders)"]
    S2 --> S3["Phase 3: Update References<br/>(features.md, task-board, req-details)"]
    S3 --> S4["Phase 4: Validate<br/>(all links resolve)"]
    S4 --> S5["Phase 5: Remove Compat<br/>(drop old path support)"]
```

### Phase 1 — Update Skills (support both old + new)
- Update all skills to create Epic-based folder structure for NEW requirements
- Keep backward compatibility: skills can still read old `FEATURE-XXX/` paths

### Phase 2 — Migrate Existing Features
- **Logical grouping rule for legacy features:**
  - Features that already have sub-features (e.g., `FEATURE-022-A/B/C/D`, `FEATURE-030-B-*`) → group under their natural Epic
  - Standalone features (e.g., `FEATURE-001`) → create `EPIC-001/FEATURE-001-A/` (single-feature Epic)
- Move files: `FEATURE-XXX/` → `EPIC-XXX/FEATURE-XXX-A/`
- Move sub-features: `FEATURE-XXX-Y/` → `EPIC-XXX/FEATURE-XXX-Y/`

### Phase 3 — Update References
- Update `features.md` — add Epic ID column, update all spec links
- Update `requirement-details-part-*.md` — change `## FEATURE-XXX` to `## EPIC-XXX`
- Update task-board **active tasks only** (archives unchanged)

### Phase 4 — Validate
- Verify all spec links in `features.md` resolve
- Verify all Feature folder paths in skill examples work
- Run existing tests to confirm no breakage

### Phase 5 — Remove Compatibility (optional, deferred)
- Remove old-path support from skills once migration is stable

### Rollback Plan
- Migration is a single atomic commit per phase
- If agents break mid-workflow: revert the phase commit, old paths restored
- Task board archives are **never** modified (historical accuracy)

## Success Criteria

- [ ] Requirement Gathering skill creates `EPIC-{nnn}/` folder with `mockups/` sub-directory
- [ ] Feature Breakdown skill creates `FEATURE-{nnn}-{X}/` sub-folders under Epic folder
- [ ] features.md includes Epic ID column, sorted by Epic ID
- [ ] All Feature specs reference mockups from parent Epic's `mockups/` folder
- [ ] Change Request skill supports Epic-aware CR handling
- [ ] Git commit message format supports Epic references
- [ ] requirement-details files use `## EPIC-{nnn}` headers
- [ ] Existing features retroactively organized under Epics
- [ ] **All existing spec/design links in features.md resolve correctly after migration**
- [ ] **No active agent workflows break during migration** (verified by test suite)

## Constraints & Considerations

- **Blast radius is large**: 57+ skill files reference `FEATURE-` patterns — migration must be carefully phased
- **Backward compatibility**: task board archives reference old `FEATURE-XXX` IDs — archives are never rewritten
- **Single-feature Epics**: may feel like overhead but consistency eliminates classification decisions
- **File splitting**: requirement-details parts keep range-based splitting but with Epic headers
- **In-flight features**: features with active tasks on task-board should complete current workflow before migration

## Brainstorming Notes

### Key Insights

1. **Current pain is real** — FEATURE-030-B already split organically into THEME/MOCKUP, showing the need for a formal Epic layer
2. **Epic folder is a namespace, not a spec** — explicitly chosen: no Epic-level specification.md; all functional detail lives in Features
3. **Mockup sharing** — major benefit: mockups created during Requirement Gathering live at Epic level and are referenced (not duplicated) by Features
4. **Consistency over flexibility** — every requirement becomes an Epic, eliminating the "is this big enough for an Epic?" decision

### Skills Requiring Updates (Full Blast Radius)

**Critical (core workflow):**
- `x-ipe-task-based-requirement-gathering` — create Epic folder, Epic-level ACs
- `x-ipe-task-based-feature-breakdown` — create Feature sub-folders under Epic
- `x-ipe+feature+feature-board-management` — Epic ID column in features.md
- `x-ipe-task-based-change-request` — Epic-aware CR handling

**High impact (feature lifecycle):**
- `x-ipe-task-based-feature-refinement` — spec paths change to `EPIC-XXX/FEATURE-XXX-X/`
- `x-ipe-task-based-feature-acceptance-test` — path updates
- `x-ipe-task-based-feature-closing` — path updates
- `x-ipe-task-based-technical-design` — path updates
- `x-ipe-task-based-code-implementation` — path updates
- `x-ipe-task-based-test-generation` — path updates

**Medium impact (supporting):**
- `x-ipe-tool-git-version-control` — commit message format
- Requirement-details templates (index, parts, splitting logic)

**Low impact (reference updates):**
- Various skill references/examples that mention `FEATURE-` patterns

## Ideation Artifacts

- Source: [new idea.md](new%20idea.md)

## Source Files

- new idea.md

## Next Steps

- [ ] Proceed to Requirement Gathering (this is a Change Request affecting multiple skills)

## References & Common Principles

### Applied Principles

- **Epic/Feature/Story hierarchy** — standard agile practice (Jira, Azure DevOps, SAFe) for organizing work at scale
- **Single Responsibility** — Epic owns grouping + shared artifacts; Feature owns functional specification
- **Consistency over flexibility** — always-Epic rule eliminates classification overhead
- **Phased migration** — skills first, then data, then validation — reduces risk of breaking active workflows

### Further Reading

- SAFe Epic definition — large initiatives decomposed into Features and Stories
- Jira hierarchy — Epic → Story → Sub-task pattern used by most engineering teams
