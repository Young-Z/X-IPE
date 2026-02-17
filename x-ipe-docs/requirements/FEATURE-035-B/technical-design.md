# Technical Design: Feature Board Epic Tracking

> Feature ID: FEATURE-035-B
> Version: v1.0
> Status: Designed
> Last Updated: 02-17-2026

---

## Part 1: Agent-Facing Summary

### Scope

Update the feature-board-management skill (SKILL.md, templates, examples) to support `epic_id` in Feature Data Model, table schema, and all operations.

### File Change Summary

| File | Change Type | Description |
|------|-------------|-------------|
| `.github/skills/x-ipe+feature+feature-board-management/SKILL.md` | Edit | Add epic_id to input params, Feature Data Model reference, query output, Epic status derivation note |
| `.github/skills/x-ipe+feature+feature-board-management/templates/features.md` | Edit | Add Epic ID column to table header and example row |
| `.github/skills/x-ipe+feature+feature-board-management/references/examples.md` | Edit | Add epic_id to all examples (Data Model, board template, create, query, status update) |

### Dependencies

FEATURE-035-A (completed)

---

## Part 2: Implementation Guide

### Change 1: SKILL.md — Input Parameters

**File:** `.github/skills/x-ipe+feature+feature-board-management/SKILL.md`

#### Change 1a: Input params — add epic_id (line 77)

**Current:**
```yaml
  features:  # For create_or_update_features
    - feature_id: "FEATURE-XXX"
      title: "{Feature Title}"
```

**New:**
```yaml
  features:  # For create_or_update_features
    - feature_id: "FEATURE-XXX-X"
      epic_id: "EPIC-XXX"  # Parent Epic ID (use "-" for legacy features)
      title: "{Feature Title}"
```

#### Change 1b: Feature Data Model reference (line 34)

After the existing Feature Data Model bullet, add:
```
- **Epic ID** — `EPIC-{nnn}` matching parent Epic, or `-` for legacy features without an Epic
```

#### Change 1c: Board Sections (line 37)

Update to note Epic ID column:
```
- **Board Sections** — Overview, Feature Tracking Table (with Epic ID column)
```

#### Change 1d: Create operation — mention epic_id (line 132)

Add to the action list after "Set status = Planned":
```
          Set epic_id from input (or "-" if not provided)
```

#### Change 1e: Query output — add epic_id (line 156)

**Current:**
```
    <output>Complete Feature Data Model (feature_id, title, version, status, description, dependencies, specification_link, technical_design_link, created, last_updated, tasks)</output>
```

**New:**
```
    <output>Complete Feature Data Model (epic_id, feature_id, title, version, status, description, dependencies, specification_link, technical_design_link, created, last_updated, tasks)</output>
```

#### Change 1f: Epic Status Derivation note

Add after the Error Handling section (before Templates):
```markdown
## Epic Status Derivation

Epic status is NOT stored in the table. It is derived from constituent Feature statuses:

| Condition | Derived Epic Status |
|-----------|-------------------|
| All Features `Completed` | Epic complete |
| Any Feature active (Refined/Designed/Implemented) | Epic in progress |
| All Features `Planned` | Epic planned |

**Note:** There are no standalone Epic rows in the table. Epics are represented only via the `Epic ID` column on Feature rows.
```

---

### Change 2: Template — features.md

**File:** `.github/skills/x-ipe+feature+feature-board-management/templates/features.md`

**Current table:**
```
| Feature ID | Feature Title | Version | Status | Specification Link | Created | Last Updated |
|------------|---------------|---------|--------|-------------------|---------|--------------|
| _No features yet_ | | | | | | |
```

**New table:**
```
| Epic ID | Feature ID | Feature Title | Version | Status | Specification Link | Created | Last Updated |
|---------|------------|---------------|---------|--------|-------------------|---------|--------------|
| _No features yet_ | | | | | | | |
```

---

### Change 3: Examples — references/examples.md

#### Change 3a: Feature Data Model (line 8-35)

Add `epic_id` field after `feature_id`:
```yaml
Feature:
  # Core identification
  epic_id: EPIC-XXX  # Parent Epic ID (or null for legacy features)
  feature_id: FEATURE-XXX-X
```

Update artifact links to Epic paths:
```yaml
  specification_link: x-ipe-docs/requirements/EPIC-XXX/FEATURE-XXX-X/specification.md | null
  technical_design_link: x-ipe-docs/requirements/EPIC-XXX/FEATURE-XXX-X/technical-design.md | null
```

#### Change 3b: Board Template Structure (line 76-79)

**Current:**
```
| Feature ID | Feature Title | Version | Status | Specification Link | Created | Last Updated |
|------------|---------------|---------|--------|-------------------|---------|--------------|
| FEATURE-001 | User Authentication | v1.0 | Designed | [spec](FEATURE-001/specification.md) | 01-15-2026 | 01-17-2026 |
```

**New:**
```
| Epic ID | Feature ID | Feature Title | Version | Status | Specification Link | Created | Last Updated |
|---------|------------|---------------|---------|--------|-------------------|---------|--------------|
| EPIC-001 | FEATURE-001-A | User Authentication | v1.0 | Designed | [spec](EPIC-001/FEATURE-001-A/specification.md) | 01-15-2026 | 01-17-2026 |
```

#### Change 3c: Example 1 — Create Features (line 90-102)

**New:**
```yaml
operation: create_or_update_features
features:
  - feature_id: FEATURE-001-A
    epic_id: EPIC-001
    title: User Authentication
    version: v1.0
    description: JWT-based authentication
    dependencies: []
  - feature_id: FEATURE-001-B
    epic_id: EPIC-001
    title: User Profile
    version: v1.0
    description: Profile management
    dependencies: [FEATURE-001-A]
```

#### Change 3d: Example 2 — Query Feature (line 114-127)

Add `epic_id: EPIC-001` to the response.

#### Change 3e: Example 3 — Category Closing (line 137)

Update path:
```yaml
task_output_links: [x-ipe-docs/requirements/EPIC-001/FEATURE-001-A/specification.md]
```

#### Change 3f: Example 4 — Full Category (line 157)

Update path:
```yaml
task_output_links: [x-ipe-docs/requirements/EPIC-001/FEATURE-001-A/technical-design.md]
```

---

### Implementation Order

1. SKILL.md (Changes 1a-1f)
2. templates/features.md (Change 2)
3. references/examples.md (Changes 3a-3f)

### Testing Strategy

No automated tests — skill document edits. Validation via sub-agent review of all 3 files for consistency.
