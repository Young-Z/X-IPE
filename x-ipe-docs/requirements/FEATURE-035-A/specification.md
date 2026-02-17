# Feature Specification: Epic Core Workflow Skills

> Feature ID: FEATURE-035-A
> Version: v1.0
> Status: Refined
> Last Updated: 02-17-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-17-2026 | Initial specification |

## Linked Mockups

N/A — This feature modifies agent skill files (SKILL.md), not application UI.

## Overview

This feature updates the two core workflow skills — **x-ipe-task-based-requirement-gathering** and **x-ipe-task-based-feature-breakdown** — to support the Epic layer. After this change:

- Requirement Gathering creates `EPIC-{nnn}/` folders (with `mockups/` sub-directory) instead of flat feature folders
- Requirement Gathering writes Epic-level acceptance criteria using `## EPIC-{nnn}` headers in requirement-details
- Feature Breakdown creates `FEATURE-{nnn}-{X}/` sub-folders under the parent Epic folder
- The naming convention `EPIC-{nnn}` / `FEATURE-{nnn}-{A|B|C}` is enforced
- Every requirement always creates an Epic (even for single-feature requirements)

This is the **foundation feature** — all other Epic features (035-B through 035-E) depend on it.

## User Stories

1. **As an AI agent** running Requirement Gathering, I want to create an `EPIC-{nnn}/mockups/` folder structure so that shared artifacts have a formal home at the Epic level.
2. **As an AI agent** running Feature Breakdown, I want to create `FEATURE-{nnn}-{X}/` sub-folders under `EPIC-{nnn}/` so that features are properly organized under their parent Epic.
3. **As a project manager**, I want every requirement to produce an Epic so that the hierarchy is consistent and I don't have to decide "is this big enough for an Epic?"

## Acceptance Criteria

### Requirement Gathering Skill Changes

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-035-A.1 | Agent runs Requirement Gathering for a new requirement | Agent reaches Step 6 (Document) | `EPIC-{nnn}/` folder created under `x-ipe-docs/requirements/` with `mockups/` sub-directory |
| AC-035-A.2 | Agent documents requirements | Agent writes requirement-details | Section header uses `## EPIC-{nnn}: {Epic Title}` format (not `## FEATURE-{nnn}`) |
| AC-035-A.3 | Mockups are provided or auto-detected | Agent processes mockups | Mockups stored in `EPIC-{nnn}/mockups/` (not in a Feature sub-folder) |
| AC-035-A.4 | Requirement is simple (single-feature scope) | Agent completes Requirement Gathering | Epic folder still created (consistency rule: always Epic) |
| AC-035-A.5 | SKILL.md `MANDATORY` note references FEATURE-{nnn} format | After update | MANDATORY note updated to reference both `EPIC-{nnn}` and `FEATURE-{nnn}-{X}` formats |

### Feature Breakdown Skill Changes

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-035-A.6 | Epic folder exists from Requirement Gathering | Agent runs Feature Breakdown | `FEATURE-{nnn}-{X}/` sub-folders created under `EPIC-{nnn}/` |
| AC-035-A.7 | Agent assigns feature IDs | Agent identifies features | Feature IDs follow `FEATURE-{nnn}-{A|B|C}` pattern where `{nnn}` matches parent Epic number |
| AC-035-A.8 | Agent writes Feature List table in requirement-details | After Feature Breakdown | Table includes features with IDs matching `FEATURE-{nnn}-{X}` format |
| AC-035-A.9 | Agent creates feature detail sections | After Feature Breakdown | Detail sections use `### FEATURE-{nnn}-{X}: {Title}` headers under parent `## EPIC-{nnn}` section |
| AC-035-A.10 | Feature has mockups | Agent processes mockups | Mockup references point to `../mockups/` (parent Epic folder), not per-feature mockup folders |

### Naming Convention Enforcement

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-035-A.11 | Agent determines next Epic number | Highest existing Epic is EPIC-034 | Next Epic assigned EPIC-035 |
| AC-035-A.12 | Agent determines next Feature suffix | Epic has features A and B | Next feature assigned suffix C (FEATURE-{nnn}-C) |
| AC-035-A.13 | SKILL.md ID format rules reference `FEATURE-{NNN}` | After update | Rules updated to show `EPIC-{NNN}` for Epics and `FEATURE-{NNN}-{X}` for Features |

### Backward Compatibility

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-035-A.14 | Old `FEATURE-XXX/` folders exist (pre-migration) | Agent reads existing requirement-details | Agent can still read and reference old `FEATURE-XXX/` paths without error |

## Functional Requirements

### Requirement Gathering Skill (x-ipe-task-based-requirement-gathering)

| ID | Requirement |
|----|-------------|
| FR-035-A.1 | **SKILL.md Step 6** — When creating requirement details, create `EPIC-{nnn}/` folder under `x-ipe-docs/requirements/` with `mockups/` sub-directory |
| FR-035-A.2 | **SKILL.md Step 6** — Use `## EPIC-{nnn}: {Title}` as section header in requirement-details (replacing `## FEATURE-{nnn}`) |
| FR-035-A.3 | **SKILL.md Step 4** — When adding mockups, store in `EPIC-{nnn}/mockups/` path |
| FR-035-A.4 | **SKILL.md MANDATORY note** — Update text to: "Every requirement MUST create an Epic with ID format `EPIC-{nnn}`. Features created during breakdown use format `FEATURE-{nnn}-{X}`." |
| FR-035-A.5 | **SKILL.md Input Parameters** — Add `epic_id` parameter (auto-assigned if not provided) |
| FR-035-A.6 | **references/requirement-details-template.md** — Update template to show `## EPIC-{nnn}` header format |
| FR-035-A.7 | **references/file-splitting.md** — Update part range descriptions to reference Epic ranges (e.g., "EPIC-001 to EPIC-011") |
| FR-035-A.8 | **references/examples.md** — Update examples to show Epic folder creation and naming |

### Feature Breakdown Skill (x-ipe-task-based-feature-breakdown)

| ID | Requirement |
|----|-------------|
| FR-035-A.9 | **SKILL.md Step 3** — Feature IDs assigned as `FEATURE-{nnn}-{A|B|C}` where `{nnn}` matches parent Epic |
| FR-035-A.10 | **SKILL.md Step 4** — Mockup processing references `EPIC-{nnn}/mockups/` (shared at Epic level), not per-feature mockup folders |
| FR-035-A.11 | **SKILL.md Step 5** — Feature List table in requirement-details uses `FEATURE-{nnn}-{X}` IDs; detail sections nest under `## EPIC-{nnn}` header |
| FR-035-A.12 | **SKILL.md Step 6** — When calling feature-board-management, pass Epic ID with each feature |
| FR-035-A.13 | **SKILL.md MANDATORY note** — Update to reference both `EPIC-{nnn}` and `FEATURE-{nnn}-{X}` naming |
| FR-035-A.14 | **references/breakdown-guidelines.md** — Update ID format section: Epic numbering, Feature suffix assignment, part range references |
| FR-035-A.15 | **references/examples.md** — Update all examples to show Epic-based folder and naming patterns |

### Shared Requirements

| ID | Requirement |
|----|-------------|
| FR-035-A.16 | **Epic ID assignment** — Sequential: scan `x-ipe-docs/requirements/` for highest existing `EPIC-{nnn}`, next is `EPIC-{nnn+1}` |
| FR-035-A.17 | **Feature suffix assignment** — Alphabetical within Epic: A, B, C, ..., Z, AA, AB, ... |
| FR-035-A.18 | **Always Epic rule** — Even single-feature requirements get an Epic (e.g., `EPIC-035/FEATURE-035-A/`) |
| FR-035-A.19 | **Backward compatibility** — Skills must still read old `FEATURE-XXX/` paths when scanning existing requirement-details files |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-035-A.1 | Skill changes are SKILL.md + reference file edits only — no application code changes |
| NFR-035-A.2 | Updated skills must not break existing agent workflows referencing old FEATURE-XXX paths |
| NFR-035-A.3 | All changes must be backward-compatible during the transition period |

## Dependencies

### Internal Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| None | — | This is the foundation feature |

### External Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-035-B | Consumer | Feature Board Epic Tracking — will add Epic ID column to features.md (not blocking for this feature) |

## Business Rules

| ID | Rule |
|----|------|
| BR-035-A.1 | Every requirement creates exactly one Epic — no exceptions |
| BR-035-A.2 | Feature `{nnn}` always matches parent Epic `{nnn}` |
| BR-035-A.3 | Epic folder contains only `mockups/` and `FEATURE-{nnn}-{X}/` sub-folders — no `specification.md` at Epic level |
| BR-035-A.4 | Mockups are stored at Epic level only — Features reference `../mockups/` from their sub-folder |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Requirement with 1 feature | Create `EPIC-{nnn}/FEATURE-{nnn}-A/` (single-feature Epic) |
| Requirement with 7+ features | Create `EPIC-{nnn}/FEATURE-{nnn}-A/` through `G/` (still max 5-7 features per breakdown guidelines) |
| No mockups provided | Create `EPIC-{nnn}/` folder but skip `mockups/` sub-directory (create on demand) |
| Old `FEATURE-XXX/` folders exist alongside new `EPIC-XXX/` folders | Skills read both formats; no conflict |
| Agent scans requirement-details parts with mixed old/new headers | Accept both `## FEATURE-XXX` and `## EPIC-XXX` headers during transition |

## Out of Scope

- Updating features.md format (FEATURE-035-B)
- Updating feature lifecycle skills paths (FEATURE-035-C)
- Updating requirement-details header format for existing files (FEATURE-035-D)
- Migrating existing feature folders (FEATURE-035-E)
- Application code changes — this feature only modifies SKILL.md and reference files

## Technical Considerations

- **Files to modify in requirement-gathering skill:**
  - `SKILL.md` — Steps 4 and 6, MANDATORY note, Input Parameters
  - `references/requirement-details-template.md` — Header format
  - `references/file-splitting.md` — Range descriptions
  - `references/examples.md` — Example workflows

- **Files to modify in feature-breakdown skill:**
  - `SKILL.md` — Steps 3-6, MANDATORY note
  - `references/breakdown-guidelines.md` — ID format, folder paths, part ranges
  - `references/examples.md` — Example breakdowns

- **Testing approach:** No automated tests (these are agent skill documents). Validation is by DoD sub-agent checking skill file contents.

## Open Questions

None — all clarifications resolved during ideation (IDEA-022).
