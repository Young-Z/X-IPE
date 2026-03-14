# DAO Decisions — 26-03-14 — Bug Fix

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-070 | 2026-03-14T06:36:43Z | TASK-867 | N/A (direct human message) | instruction | 0.90 | Reference KB from +Create New Idea should auto-create draft idea folder before opening picker |
| DAO-071 | 2026-03-14T06:51:15Z | TASK-868 | N/A (direct human message) | instruction | 0.95 | Add KB Reference button to Compose Idea modal in workflow mode |
| DAO-075 | 2026-03-14T09:10:56Z | TASK-873 | x-ipe-task-based-code-implementation | instruction | 0.85 | Compose Idea file upload shows only one of multiple uploaded files |
| DAO-077 | 2026-03-14T10:45:00Z | TASK-875 | N/A (direct human message) | instruction | 0.92 | Compose idea reopen/edit mode regression — stuck (1 file) or "No file path" (2+ files) after TASK-874 format change |

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

---

| DAO-077 | 2026-03-14T09:56:34Z | TASK-877 | N/A (direct human message) | instruction | 0.90 | Make deliverable file cards smaller to match action button height |

## DAO-077
- **Timestamp:** 2026-03-14T09:56:34Z
- **Task ID:** TASK-877
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> make the deliverable file box also smaller the same height as action button?

### Guidance Returned
> Implement the UI fix: reduce deliverable file card height to match the action button height in the workflow UI. Adjust padding, icon size, and font size in CSS.

### Rationale
> Direct continuation of TASK-876 UIUX feedback. User wants consistent sizing between deliverable cards and action buttons. Bounded CSS fix.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "CSS height adjustment for existing UI component"

### Follow-up
> None

---

## DAO-077 — Compose Idea Reopen/Edit Mode Regression (TASK-874 Format Change)

**Timestamp:** 2026-03-14T10:45:00Z
**Task ID:** TASK-875 (follow-up)
**Calling Skill:** N/A (direct human message)
**Agent:** Bolt ⚡

### Phase 1: 聞 — Listen & Interpret

**Raw message:** "I found two bug, when i reopen a composed idea with uploaded one file, it will stuck. if with two uploaded file or more, it will show No file path — opening in create mode in the compose idea modal window."

**Interpretation:** User reports two regression bugs in compose idea reopen/edit mode, both triggered after TASK-874 changed the deliverable format from legacy list `[filePath, folder_path]` to keyed dict `{"raw-ideas": ..., "ideas-folder": ...}`. The reopen code path reads deliverables from workflow state and likely still expects the old list format.

- **Bug 1:** Single uploaded file → modal gets stuck (likely undefined access on keyed dict treated as array)
- **Bug 2:** Two+ uploaded files → modal shows "No file path — opening in create mode" (format mismatch causes path extraction failure)

**Three Perspectives:**
1. **Literal:** Two bugs — stuck modal (1 file) and wrong message (2+ files) when reopening composed idea
2. **Intended:** Fix the reopen/edit code path to handle the new keyed dict deliverable format from TASK-874
3. **Beneficial:** Ensure compose idea edit mode is fully compatible with the new deliverable format, preventing future regressions

### Phase 2: 量 — Weigh & Decide

**Disposition:** `instruction`
**Confidence:** 0.92

**Gain/Loss Analysis:**
- ✅ Fix: Restores compose idea edit functionality, completes TASK-874 integration
- ⚠️ Risk: Minimal — targeted fix to format handling in reopen code path
- ❌ Skip: Users cannot reopen any composed idea — critical UX blocker

**Scenario fork:**
- Both bugs share the same root cause (deliverable format mismatch) → single fix unit

### Phase 3: 伝 — Formulate Response

**Instruction Units:** 1

> **Unit 0:** Fix two regression bugs in compose idea reopen/edit mode caused by TASK-874's deliverable format change. Bug 1: single file → modal stuck. Bug 2: 2+ files → "No file path" message. Root cause: reopen code expects old list format `[filePath, folder_path]` but receives keyed dict `{"raw-ideas": ..., "ideas-folder": ...}`. Investigate `compose-idea-modal.js` and `workflow-stage.js` edit mode code paths.

**Execution Plan:** Sequential — single group `[0]`

### Phase 4: 省 — Reflect

**Why this disposition?** Clear regression from a known recent change (TASK-874). Both bugs are deterministic, share one root cause, and map directly to `x-ipe-task-based-bug-fix`. High confidence because the format change is documented and the symptom matches a format mismatch pattern.

**Suggested Skills:**
> - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Regression bugs from recent TASK-874 deliverable format change"

### Follow-up
> None

| DAO-078 | 2026-03-14T16:04:14Z | TASK-878 | N/A | instruction | 0.85 | UIUX feedback: Compose Idea dialog doesn't restore saved content/KB references when reopening an existing idea |

## DAO-078
- **Timestamp:** 2026-03-14T16:04:14Z
- **Task ID:** TASK-878
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.85

### Message
> Get uiux feedback, please visit feedback folder x-ipe-docs/uiux-feedback/Feedback-20260314-234833 to get details. Feedback: when reopening a composed idea with KB references, nothing is changed — expected the deliverable file to show composed idea and referenced knowledge.

### Guidance Returned
> Proceed with bug fix. The Compose Idea dialog fails to restore saved content (idea name, editor text, KB references) when reopening an existing idea. Investigate the compose idea component's initialization/loading logic and the deliverable file persistence layer.

### Rationale
> Clear UIUX feedback with screenshot evidence showing empty editor on reopen. This is a functional bug — data was saved but not restored on reopen. Maps directly to bug-fix skill.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "User reports broken behavior: saved compose idea content not shown on reopen. This is a functional bug."
>     execution_steps:
>       - phase: "1. Diagnosis"
>         step: "1.1 Reproduce and locate root cause"
>       - phase: "2. Fix"
>         step: "2.1 Write failing test, implement fix, verify"

### Follow-up
> None
| DAO-079 | 2026-03-14T16:25:17Z | TBD (new) | N/A (direct human message) | instruction (x2) | 0.80 | Two compose-idea bugs: (1) KB reference file not shown as deliverable, (2) upload files broken on reopen after TASK-878 |

## DAO-079
- **Timestamp:** 2026-03-14T16:25:17Z
- **Task ID:** TBD (new bugs — tasks to be created)
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction (2 units)
- **Confidence:** 0.80

### Message
> first of all, the reference file didn't show as file deliverable, 2. I found that if I try to reopen and upload files, it's no longer working

### Guidance Returned
> Unit 0: Diagnose and fix why KB reference files don't appear as deliverables in the workflow stage UI. Use x-ipe-task-based-bug-fix skill.
> Unit 1: Diagnose and fix the upload regression introduced by TASK-878 — reopening an idea and uploading files no longer works. Use x-ipe-task-based-bug-fix skill.

### Rationale
> Two independent bugs in compose-idea flow. Unit 0 is a display/deliverable issue. Unit 1 is a likely regression from TASK-878 (KB reference loading changes may have broken upload flow). Sequential execution since both may touch compose-idea-modal.js.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Both units are bugs — missing deliverable display and broken upload"
>     execution_steps:
>       - phase: "1. Understand"
>         step: "1.1 Read bug, categorize severity"
>       - phase: "2. Fix"
>         step: "2.1 Write failing test, implement fix, verify"

### Follow-up
> None
