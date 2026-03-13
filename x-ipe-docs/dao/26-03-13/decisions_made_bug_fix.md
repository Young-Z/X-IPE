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
