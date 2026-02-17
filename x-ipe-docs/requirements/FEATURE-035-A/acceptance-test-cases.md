# Acceptance Test Results: FEATURE-035-A (Epic Core Workflow Skills)

> Tested: 2026-02-17
> Tester: AI Agent (Acceptance Test)
> Result: **14/14 PASS**

## Test Results

| AC ID | AC Description | Result | Evidence |
|-------|---------------|--------|----------|
| AC-035-A.1 | `EPIC-{nnn}/` folder created under `x-ipe-docs/requirements/` with `mockups/` sub-directory when Agent reaches Step 6 | **PASS** | req-gathering SKILL.md Step 6 lines 212-215: "Create x-ipe-docs/requirements/EPIC-{nnn}/ directory" and "Create x-ipe-docs/requirements/EPIC-{nnn}/mockups/ sub-directory" |
| AC-035-A.2 | Section header uses `## EPIC-{nnn}: {Epic Title}` format (not `## FEATURE-{nnn}`) | **PASS** | req-gathering SKILL.md Step 6 line 217: "Use ## EPIC-{nnn}: {Epic Title} as the section header in requirement-details (NOT ## FEATURE-{nnn})"; requirement-details-template.md line 3: `## EPIC-{nnn}: {Epic Title}` |
| AC-035-A.3 | Mockups stored in `EPIC-{nnn}/mockups/` (not in a Feature sub-folder) | **PASS** | req-gathering SKILL.md Step 6 line 215: "copy mockups to EPIC-{nnn}/mockups/"; requirement-details-template.md line 33: `[mockup.html](EPIC-{nnn}/mockups/mockup.html)` |
| AC-035-A.4 | Epic folder still created for single-feature scope (consistency rule: always Epic) | **PASS** | req-gathering SKILL.md line 26: "MANDATORY: Every requirement MUST create an Epic with ID format `EPIC-{nnn}`"; Pattern "Epic Folder Creation" lines 357-366 confirms this for "any new requirement" |
| AC-035-A.5 | MANDATORY note updated to reference both `EPIC-{nnn}` and `FEATURE-{nnn}-{X}` formats | **PASS** | req-gathering SKILL.md line 26: "Every requirement MUST create an Epic with ID format `EPIC-{nnn}` (e.g., EPIC-001, EPIC-035). Features created during Feature Breakdown use format `FEATURE-{nnn}-{X}` (e.g., FEATURE-035-A)." |
| AC-035-A.6 | `FEATURE-{nnn}-{X}/` sub-folders created under `EPIC-{nnn}/` | **PASS** | feature-breakdown SKILL.md line 26: "Features are created as sub-folders under the parent `EPIC-{nnn}/` folder."; feature-breakdown examples.md lines 65-67: `x-ipe-docs/requirements/EPIC-001/FEATURE-001-A/`, `EPIC-001/FEATURE-001-B/` |
| AC-035-A.7 | Feature IDs follow `FEATURE-{nnn}-{A\|B\|C}` pattern where `{nnn}` matches parent Epic number | **PASS** | feature-breakdown SKILL.md Step 3 line 176: "Assign Feature IDs as FEATURE-{nnn}-{A\|B\|C...} where {nnn} matches parent Epic number"; breakdown-guidelines.md lines 70-78: `Feature: FEATURE-{NNN}-{X}` and "Feature {NNN} ALWAYS matches parent Epic {NNN}" |
| AC-035-A.8 | Feature List table includes features with IDs matching `FEATURE-{nnn}-{X}` format | **PASS** | feature-breakdown SKILL.md Step 5 lines 225-226: table shows `FEATURE-001-A`, `FEATURE-001-B`; breakdown-guidelines.md Part File Structure line 271: `FEATURE-012-A` |
| AC-035-A.9 | Feature detail sections use `### FEATURE-{nnn}-{X}: {Title}` headers under parent `## EPIC-{nnn}` section | **PASS** | breakdown-guidelines.md Feature Details Template line 311: `### {FEATURE-NNN-X}: {Feature Title}`; Part File Structure line 285: `### FEATURE-012-A: Design Themes`; req-gathering creates parent `## EPIC-{nnn}: {Title}` header (template line 3), features nest below it |
| AC-035-A.10 | Mockup references point to `../mockups/` (parent Epic folder), not per-feature mockup folders | **PASS** | feature-breakdown SKILL.md Step 4 lines 202-203: "Mockups remain at EPIC-{nnn}/mockups/ (shared) — do NOT create per-feature mockup folders" and "Features reference mockups via ../mockups/ relative path"; breakdown-guidelines.md lines 218-219: "Shared at Epic level — Features reference via ../mockups/" and "FEATURE-001-A/mockups/ → NOT used" |
| AC-035-A.11 | Next Epic assigned sequentially (e.g., EPIC-034 → EPIC-035) | **PASS** | req-gathering SKILL.md Input Parameters line 47: "Auto-assigned: scan x-ipe-docs/requirements/ for highest EPIC-{nnn}, next is EPIC-{nnn+1}"; breakdown-guidelines.md line 80: "Scan x-ipe-docs/requirements/ for highest existing EPIC-{NNN} to determine next number" |
| AC-035-A.12 | Next feature suffix assigned alphabetically (A, B → next is C) | **PASS** | feature-breakdown SKILL.md Step 3 line 177: "First feature gets suffix A, second gets B, etc."; breakdown-guidelines.md line 79: "Suffix assigned alphabetically: first feature = A, second = B" |
| AC-035-A.13 | ID format rules updated to show `EPIC-{NNN}` for Epics and `FEATURE-{NNN}-{X}` for Features | **PASS** | breakdown-guidelines.md lines 69-75: `Epic: EPIC-{NNN}` and `Feature: FEATURE-{NNN}-{X}`; req-gathering SKILL.md line 26 and feature-breakdown SKILL.md line 26 both show updated formats; file-splitting.md lines 86-87: ranges updated to "EPIC-001 to EPIC-005" |
| AC-035-A.14 | Agent can still read and reference old `FEATURE-XXX/` paths without error | **PASS** | req-gathering SKILL.md lines 28-29: Transition Note says "both old (`FEATURE-{nnn}/`) and new (`EPIC-{nnn}/FEATURE-{nnn}-{X}/`) folder structures may coexist. Skills must handle both formats"; feature-breakdown SKILL.md lines 28-29: identical Transition Note; req-gathering examples.md line 3: legacy note acknowledging old format |

## Summary

All 14 acceptance criteria **PASS**. The Epic Core Workflow Skills changes are correctly implemented across all 7 modified files:

- **Requirement Gathering SKILL.md**: Epic folder creation in Step 6, MANDATORY note with both formats, `epic_id` input parameter, transition note, Epic Folder Creation pattern
- **requirement-details-template.md**: `## EPIC-{nnn}` header, `EPIC-{nnn}/mockups/` paths
- **file-splitting.md**: Part ranges use Epic references (e.g., "EPIC-001 to EPIC-005")
- **Requirement Gathering examples.md**: Legacy note for old format, updated examples showing Epic workflow
- **Feature Breakdown SKILL.md**: `FEATURE-{nnn}-{X}` IDs under parent Epic, shared mockups at Epic level, `epic_id` in board calls, transition note
- **breakdown-guidelines.md**: ID format section with `EPIC-{NNN}` and `FEATURE-{NNN}-{X}`, part ranges, mockup sharing rules, Epic-based folder examples
- **Feature Breakdown examples.md**: All examples use `FEATURE-{nnn}-{X}` format with Epic-based folder paths
