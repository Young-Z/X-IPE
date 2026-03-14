# DAO Decisions — 26-03-14 — Bug Fix

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-070 | 2026-03-14T06:36:43Z | TASK-867 | N/A (direct human message) | instruction | 0.90 | Reference KB from +Create New Idea should auto-create draft idea folder before opening picker |
| DAO-071 | 2026-03-14T06:51:15Z | TASK-868 | N/A (direct human message) | instruction | 0.95 | Add KB Reference button to Compose Idea modal in workflow mode |
| DAO-075 | 2026-03-14T09:10:56Z | TASK-873 | x-ipe-task-based-code-implementation | instruction | 0.85 | Compose Idea file upload shows only one of multiple uploaded files |

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

---

## DAO-075 — Compose Idea File Upload Shows Only One of Multiple Files

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-14T09:10:56Z |
| Source | human |
| Task ID | TASK-873 |
| Feature ID | FEATURE-041-E |
| Disposition | instruction |
| Confidence | 0.85 |
| Calling Skill | x-ipe-task-based-code-implementation |

### Message
"when I upload files in composing idea, I uploaded two, but only showing one"

### Interpretation
User reports a bug in the ideation file upload feature: when composing an idea and uploading two files, only one file is displayed. This is a functional defect in the compose_idea upload flow — separate from CR-003 (array deliverables).

### Decision
Disposition: instruction — route to x-ipe-task-based-bug-fix skill. The user is implicitly requesting the bug be diagnosed and fixed. The compose_idea file upload should display all uploaded files.

### Instruction Units
1. Unit 0: Diagnose and fix the compose_idea file upload bug where uploading multiple files only shows one.
   - Suggested skill: x-ipe-task-based-bug-fix (strong match)

---

## DAO-076

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-14T09:26:32Z |
| Source | human |
| Task ID | TASK-874 |
| Feature ID | FEATURE-041-E |
| Disposition | instruction |
| Confidence | 0.90 |
| Calling Skill | x-ipe-task-based-bug-fix |

### Message
"the label for files in the deliverable should not call raw-idea, let's using file name for the label, and folder let's using folder name as well"

### Interpretation
User wants the deliverable cards in the workflow UI to show actual file/folder names as labels instead of the internal tag names (e.g., "raw-ideas"). For file deliverables, show the filename (e.g., "new-idea.md"). For folder deliverables, show the folder name (e.g., "my-idea-folder").

### Decision
Disposition: instruction — route to x-ipe-task-based-bug-fix. This is a UI display fix in the deliverables rendering code. The label extraction needs to parse the file path to get the basename for files and the folder name for folders.

### Instruction Units
1. Unit 0: Change deliverable card labels from tag names to file/folder names. Files show basename (e.g., "sketch1.png"), folders show folder name.
   - Suggested skill: x-ipe-task-based-bug-fix (strong match)

| DAO-076 | 2026-03-14T09:44:46Z | TASK-876 | N/A (direct human message) | instruction | 0.88 | UIUX feedback: In deliverables section, move folder paths beside the subtitle and make them smaller to visually distinguish folders from generated files |

## DAO-076
- **Timestamp:** 2026-03-14T09:44:46Z
- **Task ID:** TASK-876
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.88

### Message
> Get uiux feedback, please visit feedback folder x-ipe-docs/uiux-feedback/Feedback-20260314-174241 to get details. Feedback: for the folders in the deliverables, let's having the beside the subtitle, and make them as small as sub title, so we can more clearly know which is folders from deliverable, which is generated files

### Guidance Returned
> Implement the UIUX feedback: In the deliverables cards, reposition folder paths to appear beside (inline with) the subtitle text, and reduce their font size to match the subtitle. This will create a clear visual distinction between folder containers and generated file deliverables.

### Rationale
> User provided specific UIUX feedback via the feedback tool with a screenshot and element selector targeting deliverable cards. The request is a concrete, bounded UI fix — reposition and resize folder paths. Matches bug-fix skill (strong) as it's fixing visual presentation of existing feature.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "UI presentation fix based on UIUX feedback — existing feature needs visual adjustment"
>     execution_steps:
>       - phase: "1. Diagnosis"
>         step: "1.1 Root Cause Analysis"

### Follow-up
> None
