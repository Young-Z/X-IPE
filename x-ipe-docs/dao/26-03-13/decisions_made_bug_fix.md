# DAO Decisions — 26-03-13 — Bug Fix

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-064 | 2026-03-13T02:19:07Z | TASK-TBD | N/A (direct human message) | instruction | 0.90 | KB Reference Picker (FEATURE-049-G) reported non-functional despite being marked done — diagnose and fix |

## DAO-064
- **Timestamp:** 2026-03-13T02:19:07Z
- **Task ID:** TASK-TBD
- **Feature ID:** FEATURE-049-G
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> you can test kb reference feature, in workflow you mentioned feature 49-G is done, but looks like it's not working

### Guidance Returned
> The KB Reference Picker (FEATURE-049-G) is reported as non-functional despite being marked done (TASK-837 implementation + TASK-838/849 acceptance testing). Use x-ipe-task-based-bug-fix to diagnose the root cause and fix it. The feature was implemented as KBReferencePicker class in kb-reference-picker.js with a two-panel modal, folder tree, search, multi-select. Investigate whether the modal opens, loads data, and allows selection.

### Rationale
> User tested a completed feature and found it broken — this is the discovery loop (human_playground → bug-fix). Strong keyword match ("not working") and engineering-next (standalone bug-fix skill) agree. Single unit, single skill.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Feature marked done but reported non-functional — classic bug report on completed feature"
>     execution_steps:
>       - phase: "1. Diagnosis"
>         step: "1.1 Reproduce and identify root cause"
>       - phase: "2. Fix"
>         step: "2.1 Write failing test, implement fix, verify"

### Follow-up
> None

---

## DAO-067 — Modal Size Consistency

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-13T05:56:43Z |
| Source | human |
| Task ID | TASK-861 |
| Feature ID | FEATURE-049-G |
| Disposition | instruction |
| Confidence | 0.95 |

**Message:** "the modal window size should be the same as the others"

**Need:** Match KB Reference Picker modal dimensions to the standard 90vw × 90vh used by all other modals (KB Browse, Compose Idea, Action Execution, Folder Browser, Stage Toolbox).

**Rationale:** All 5 other full-size modals use `width: 90vw; height: 90vh`. The KB Reference Picker currently uses `max-width: 800px; max-height: 600px` which is inconsistent. User explicitly requests consistency.

**Suggested Skill:** x-ipe-task-based-bug-fix (partial match — CSS fix)

**Execution Plan:** sequential, groups: [[0]]

---

## DAO-069 — KB Reference Persistence

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-13T22:00:00Z |
| Source | human |
| Task ID | TASK-862 |
| Feature ID | FEATURE-049-G |
| Disposition | instruction |
| Confidence | 0.92 |

**Message:** "I inserted a KB reference into 002. Feature-Brand Themes, but I didn't see the .knowledge-reference.yaml within its folder"

**Need:** Insert button in KB Reference Picker does not persist `.knowledge-reference.yaml` when opened via KB Browse Modal → "Reference KB" path (global `window.kbReferencePicker` with no `onInsert` callback).

**Root Cause:** Two code paths: (1) Workplace compose pane creates new picker WITH `onInsert` → saves; (2) KB Browse Modal uses global picker WITHOUT `onInsert` → Insert did nothing.

**Fix:** Added `_persistReferences()` fallback that auto-detects current ideation folder from DOM breadcrumb and POSTs directly to `/api/ideas/kb-references`.

**Suggested Skill:** x-ipe-task-based-bug-fix (strong match)

**Execution Plan:** sequential, groups: [[0]]
