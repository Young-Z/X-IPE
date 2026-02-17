# Technical Design: Epic Core Workflow Skills

> Feature ID: FEATURE-035-A
> Version: v1.0
> Status: Designed
> Last Updated: 02-17-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-17-2026 | Initial technical design |

---

## Part 1: Agent-Facing Summary

### Scope

Update two agent skill document sets (SKILL.md + references) to support Epic layer:
- `x-ipe-task-based-requirement-gathering` — Epic folder creation, Epic headers
- `x-ipe-task-based-feature-breakdown` — Feature sub-folder creation under Epics, naming convention

### Approach

**Skill-only changes** — no application code, no tests, no build. All changes are markdown edits to SKILL.md and reference files.

### File Change Summary

| File | Change Type | Description |
|------|-------------|-------------|
| `.github/skills/x-ipe-task-based-requirement-gathering/SKILL.md` | Edit | Update MANDATORY note, Step 4, Step 6, Input Parameters |
| `.github/skills/x-ipe-task-based-requirement-gathering/references/requirement-details-template.md` | Edit | Update header format to `## EPIC-{nnn}` |
| `.github/skills/x-ipe-task-based-requirement-gathering/references/file-splitting.md` | Edit | Update index example to reference Epic ranges |
| `.github/skills/x-ipe-task-based-requirement-gathering/references/examples.md` | Edit | Update examples with Epic folder creation |
| `.github/skills/x-ipe-task-based-feature-breakdown/SKILL.md` | Edit | Update MANDATORY note, Steps 3-6, mockup path |
| `.github/skills/x-ipe-task-based-feature-breakdown/references/breakdown-guidelines.md` | Edit | Update ID format section, folder paths, part ranges, mockup paths |
| `.github/skills/x-ipe-task-based-feature-breakdown/references/examples.md` | Edit | Update examples with Epic-based naming |

### Dependencies

None — foundation feature.

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agents mid-workflow may encounter mixed old/new conventions | Low | Backward compatibility: accept both `## FEATURE-{nnn}` and `## EPIC-{nnn}` headers |

---

## Part 2: Implementation Guide

### Change 1: Requirement Gathering SKILL.md

**File:** `.github/skills/x-ipe-task-based-requirement-gathering/SKILL.md`

#### Change 1a: MANDATORY note (line 26)

**Current:**
```
MANDATORY: Every feature mentioned or identified in the output MUST have a feature ID in the format `FEATURE-{nnn}` (e.g., FEATURE-001, FEATURE-027). This applies regardless of the output language used.
```

**New:**
```
MANDATORY: Every requirement MUST create an Epic with ID format `EPIC-{nnn}` (e.g., EPIC-001, EPIC-035). Features created during Feature Breakdown use format `FEATURE-{nnn}-{X}` (e.g., FEATURE-035-A). The `{nnn}` in Feature IDs always matches the parent Epic number.
```

#### Change 1b: Input Parameters — add epic_id (after line 48)

Add to the input parameters YAML block:
```yaml
  epic_id: "EPIC-{nnn}"  # Auto-assigned: scan x-ipe-docs/requirements/ for highest EPIC-{nnn}, next is EPIC-{nnn+1}
```

#### Change 1c: Step 4 — Update Impacted Features (line 170)

In the CR impact marker template, change `{new_feature_id}` reference to mention Epic context:
```
> - **New Feature Ref:** EPIC-{nnn} — see {requirement-details-part-N.md}
```

#### Change 1d: Step 6 — Create Requirement Details Document (around line 207)

Add new action item after existing item 1:
```
1b. Create Epic folder structure:
    - Create x-ipe-docs/requirements/EPIC-{nnn}/ directory
    - Create x-ipe-docs/requirements/EPIC-{nnn}/mockups/ sub-directory
    - If mockup_list is provided, copy mockups to EPIC-{nnn}/mockups/
```

Update action item 2 (template usage):
```
2. Use ## EPIC-{nnn}: {Epic Title} as the section header in requirement-details
   (NOT ## FEATURE-{nnn})
```

#### Change 1e: Step 6 — Output path (line 221)

Update constraint reference to mention Epic folder:
```
- CRITICAL: Create EPIC-{nnn}/ folder under x-ipe-docs/requirements/ with mockups/ sub-directory
```

#### Change 1f: Output Result (line 243)

Add to task_completion_output YAML:
```yaml
  epic_id: "EPIC-{nnn}"  # The Epic created by this requirement gathering
```

#### Change 1g: Patterns section — add new pattern (after line 337)

Add pattern:
```
### Pattern: Epic Folder Creation

**When:** Creating any new requirement
**Then:**
1. Determine next EPIC-{nnn} (scan x-ipe-docs/requirements/ for highest existing)
2. Create EPIC-{nnn}/ folder
3. Create EPIC-{nnn}/mockups/ sub-directory
4. Store any mockups in EPIC-{nnn}/mockups/
5. Write requirement-details section with ## EPIC-{nnn}: {Title} header
6. Note: Feature sub-folders are created later during Feature Breakdown
```

---

### Change 2: Requirement Gathering References

#### Change 2a: requirement-details-template.md

Add Epic header example after the `## High-Level Requirements` section:
```markdown
## EPIC-{nnn}: {Epic Title}

### High-Level Requirements
1. [Requirement 1]
...
```

#### Change 2b: file-splitting.md — Index example (line 85-86)

**Current:**
```
| 1 | [Part 1](requirement-details-part-1.md) | FEATURE-001 to FEATURE-005 | ~420 |
| 2 | [Part 2](requirement-details-part-2.md) | FEATURE-006 to FEATURE-010 | ~380 |
```

**New:**
```
| 1 | [Part 1](requirement-details-part-1.md) | EPIC-001 to EPIC-005 | ~420 |
| 2 | [Part 2](requirement-details-part-2.md) | EPIC-006 to EPIC-010 | ~380 |
```

#### Change 2c: examples.md — Update examples

In Example 1 (step 6), change:
```
6. Create x-ipe-docs/requirements/requirement-details.md:
```
to:
```
6. Create EPIC-{nnn}/ folder with mockups/ sub-directory
   Create/update x-ipe-docs/requirements/requirement-details.md:
   Use ## EPIC-{nnn}: User Authentication as section header
```

---

### Change 3: Feature Breakdown SKILL.md

**File:** `.github/skills/x-ipe-task-based-feature-breakdown/SKILL.md`

#### Change 3a: MANDATORY note (line 26)

**Current:**
```
MANDATORY: Every feature MUST have a feature ID in the format `FEATURE-{nnn}` (e.g., FEATURE-001, FEATURE-027). This applies regardless of the output language used.
```

**New:**
```
MANDATORY: Every feature MUST have a feature ID in the format `FEATURE-{nnn}-{X}` (e.g., FEATURE-035-A, FEATURE-035-B) where `{nnn}` matches the parent Epic number. Features are created as sub-folders under the parent `EPIC-{nnn}/` folder.
```

#### Change 3b: Step 3 — Identify Features (line 173)

Update feature ID assignment text:
```
   Assign Feature IDs as FEATURE-{nnn}-{A|B|C...} where {nnn} matches parent Epic number.
   First feature gets suffix A, second gets B, etc.
```

#### Change 3c: Step 4 — Process Mockups (line 193-201)

**Current:**
```
1. IF mockup_list empty -- scan x-ipe-docs/ideas/{idea-folder}/mockups/
2. IF still empty -- skip to Step 5
3. Create x-ipe-docs/requirements/{FEATURE-ID}/mockups/ for each feature
4. Copy mockups, link in requirement-details.md
```

**New:**
```
1. IF mockup_list empty -- scan EPIC-{nnn}/mockups/ (shared Epic-level mockups)
2. IF still empty -- scan x-ipe-docs/ideas/{idea-folder}/mockups/
3. IF still empty -- skip to Step 5
4. Mockups remain at EPIC-{nnn}/mockups/ (shared) — do NOT create per-feature mockup folders
5. Features reference mockups via ../mockups/ relative path
6. Link in requirement-details.md
```

#### Change 3d: Step 5 — Create Summary (line 216-218)

Update Feature List table example:
```
| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-035-A | ... | v1.0 | ... | None |
| FEATURE-035-B | ... | v1.0 | ... | FEATURE-035-A |
```

Update detail section template:
```
Under the existing ## EPIC-{nnn} header, add:
### FEATURE-{nnn}-{X}: {Feature Title}
```

#### Change 3e: Step 6 — Update Board (line 236-243)

Add `epic_id` to the feature-board-management call:
```yaml
CALL x-ipe+feature+feature-board-management skill:
  operation: create_or_update_features
  features:
    - feature_id: FEATURE-035-A
      epic_id: EPIC-035
      title: "{title}"
      ...
```

#### Change 3f: Output Result (line 324-325)

Add to task_completion_output YAML:
```yaml
  epic_id: "EPIC-{nnn}"  # Parent Epic
```

---

### Change 4: Feature Breakdown References

#### Change 4a: breakdown-guidelines.md — ID Format (lines 68-83)

**Current:**
```
FEATURE-{NNN}
Where NNN is a zero-padded 3-digit number (001, 002, etc.)
```

**New:**
```
Epic: EPIC-{NNN}
Feature: FEATURE-{NNN}-{X}

Where NNN is a zero-padded 3-digit number matching the parent Epic (001, 002, etc.)
and X is an uppercase letter suffix (A, B, C, ...).

Rules:
1. Feature {NNN} ALWAYS matches parent Epic {NNN}
2. Suffix assigned alphabetically: first feature = A, second = B
3. Scan x-ipe-docs/requirements/ for highest existing EPIC-{NNN} to determine next number
```

#### Change 4b: breakdown-guidelines.md — Part ranges (lines 80-83)

**Current:**
```
- Part 1: FEATURE-001 to FEATURE-011
- Part 2: FEATURE-012 to FEATURE-017
```

**New:**
```
- Part 1: EPIC-001 to EPIC-011
- Part 2: EPIC-012 to EPIC-017
```

#### Change 4c: breakdown-guidelines.md — Mockup paths (lines 210-211)

**Current:**
```
x-ipe-docs/requirements/FEATURE-001/mockups/main-dashboard.html
```

**New:**
```
x-ipe-docs/requirements/EPIC-001/mockups/main-dashboard.html
(Shared at Epic level — Features reference via ../mockups/)
```

#### Change 4d: breakdown-guidelines.md — Feature Details template (line 302)

**Current:**
```
### {FEATURE-ID}: {Feature Title}
```

**New:**
```
### {FEATURE-NNN-X}: {Feature Title}
(Nested under ## EPIC-{NNN}: {Epic Title} header)
```

#### Change 4e: examples.md — Update all FEATURE-001 references

Replace standalone `FEATURE-001` references with `FEATURE-001-A` and add `EPIC-001` context where appropriate.

---

### Change 5: Backward Compatibility

Both skills must accept both formats during the transition period:

1. **When scanning requirement-details**: accept both `## FEATURE-{nnn}` and `## EPIC-{nnn}` headers
2. **When reading folder paths**: accept both `FEATURE-{nnn}/` and `EPIC-{nnn}/FEATURE-{nnn}-{X}/`
3. **Add a note to both SKILL.md files:**
```
> **Transition Note:** During migration, both old (`FEATURE-{nnn}/`) and new (`EPIC-{nnn}/FEATURE-{nnn}-{X}/`) folder structures may coexist. Skills must handle both formats when scanning existing files.
```

---

### Implementation Order

1. Requirement Gathering SKILL.md (Changes 1a-1g)
2. Requirement Gathering references (Changes 2a-2c)
3. Feature Breakdown SKILL.md (Changes 3a-3f)
4. Feature Breakdown references (Changes 4a-4e)
5. Backward compatibility notes (Change 5)

### Testing Strategy

No automated tests — these are agent skill documents. Validation:
1. Sub-agent reviews all modified SKILL.md files for internal consistency
2. Verify all examples use correct Epic/Feature naming
3. Verify backward compatibility notes present in both skills
