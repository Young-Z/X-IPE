# DAO Decisions — 26-03-14 — Bug Fix

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-070 | 2026-03-14T06:36:43Z | TASK-867 | N/A (direct human message) | instruction | 0.90 | Reference KB from +Create New Idea should auto-create draft idea folder before opening picker |
| DAO-071 | 2026-03-14T06:51:15Z | TASK-868 | N/A (direct human message) | instruction | 0.95 | Add KB Reference button to Compose Idea modal in workflow mode |

---

## DAO-070 — Auto-create Draft Idea Folder for Reference KB

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-14T06:36:43Z |
| Source | human |
| Task ID | TASK-867 |
| Feature ID | FEATURE-049-G |
| Disposition | instruction |
| Confidence | 0.90 |

**Message:**  
> "if click +create new idea, and then click on referen KB, it should follow the submit idea logic to create the draft idea folder"

**Need:**  
When user clicks "+Create New Idea" and then "Reference KB", auto-create the draft idea folder (same logic as Submit Idea) before opening the KB Reference Picker, so `.knowledge-reference.yaml` has a valid target path.

**Rationale:**  
The KB Reference Picker's `_persistReferences()` needs a valid ideation folder to POST to. In the "+Create New Idea" flow, no folder exists yet. The Submit Idea button already has logic to create a draft folder — Reference KB should reuse that same logic.

**Suggested Skill:**  
`x-ipe-task-based-bug-fix` (strong match — missing behavior in existing feature flow)

**Execution Plan:**  
sequential, groups: [[0]]

**Context:**  
- This is part of KB Reference Picker persistence enhancement (FEATURE-049-G)
- Related to existing Submit Idea folder creation behavior
- Affects user flow: +Create New Idea → Reference KB → Picker should have valid target folder
