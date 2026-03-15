# DAO Decisions — Change Request

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-065 | 2026-03-13T02:35:31Z | TBD | N/A | instruction | 0.92 | Process 8-point UIUX feedback as CR for FEATURE-049-G (KB Reference Picker) |

## DAO-065
- **Timestamp:** 2026-03-13T02:35:31Z
- **Task ID:** TBD (to be created on task-board)
- **Feature ID:** FEATURE-049-G
- **Workflow:** wf-007-knowledge-base-implementation
- **Calling Skill:** N/A (initial user message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.92

### Message
> Get uiux feedback, please visit feedback folder x-ipe-docs/uiux-feedback/Feedback-20260313-102717 to get details. (8-point UIUX feedback on KB Reference Picker: non-selectable folders, tree from KB root, no dark theme, standard modal size, scrollable content, tag line separation, breadcrumb nav with folder checkbox, full path links)

### Guidance Returned
> Process the 8-point UIUX feedback as a Change Request (CR) for FEATURE-049-G (KB Reference Picker). FEATURE-049-G is post-implementation (TASK-837, TASK-858 done). Engineering workflow: FEEDBACK stage → change_request → feature_refinement. Follow x-ipe-task-based-change-request skill procedure.

### Rationale
> All 8 feedback items target the same component (KB Reference Picker modal). They form a coherent redesign of the folder/file browsing UX — tightly coupled, not splittable. FEATURE-049-G is in FEEDBACK stage. Keyword match ("UIUX feedback" + specific changes) and engineering-next (feedback → change_request) agree → high confidence. Change Request skill handles impact analysis, spec update, and routes to implementation.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-change-request"
>     match_strength: "strong"
>     reason: "8-point UIUX feedback on existing FEATURE-049-G in FEEDBACK stage — standard change request flow"
>     execution_steps:
>       - phase: "1. Analyze"
>         step: "1.1 Read CR input and analyze impact"
>       - phase: "2. Process"
>         step: "2.1 Determine if CR modifies existing feature or requires new"
>       - phase: "3. Route"
>         step: "3.1 Route to feature refinement or feature breakdown"

### Follow-up
> None
# DAO Decisions — 26-03-13 — Change Request

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-065 | 2026-03-13T08:40:33Z | TASK-TBD | N/A (direct human message) | instruction | 0.92 | CR on FEATURE-049-G: sub-folder checkboxes, list/icon view toggle, icon-view checkbox placement, click/dblclick navigation |

## DAO-065
- **Timestamp:** 2026-03-13T08:40:33Z
- **Task ID:** TASK-TBD
- **Feature ID:** FEATURE-049-G
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.92

### Message
> For the kb folder content view in the kb reference picker, it should show the check box for sub-folder as well. 2. it should support two views one is as-is list view, second should be icons view. on the navigation bar, before the checker. it should show the view modes. 3. for icons view, the checkbox should be on it's right bottom corner. 4. one click on the folder or file should check or check off. and for folders let's enable double click to get into the sub folders. (in the bottom of the modal, show the tips that double click get into the sub-folder)

### Guidance Returned
> CR-002 on FEATURE-049-G (KB Reference Picker): 4 enhancements to the file/folder content panel. (1) Render checkboxes for sub-folders in file list panel, not just root folders in tree panel. (2) Add list/icon view toggle buttons on toolbar before the selection count. (3) In icon view, position checkbox at bottom-right corner of each card. (4) Single-click toggles check state; double-click on folders navigates into sub-folder; add tip in footer about double-click behavior.

### Rationale
> Clear, bounded CR on completed feature with specific UI requirements. All 4 changes target the same component (kb-reference-picker.js + CSS). Single unit, single skill path: change-request → implementation.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-change-request"
>     match_strength: "strong"
>     reason: "Enhancement request on completed FEATURE-049-G — standard CR flow"

### Follow-up
> None

---

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-066 | 2026-03-13T13:08:12Z | TASK-TBD | N/A (direct human message) | instruction | 0.85 | UIUX feedback: Add KB Reference button to compose pane, integrate picker, insert .knowledge-reference.yaml, show reference count label |

## DAO-066
- **Timestamp:** 2026-03-13T13:08:12Z
- **Task ID:** TASK-TBD
- **Feature ID:** N/A (new feature area — Workplace/Ideation compose)
- **Workflow:** wf-007-knowledge-base-implementation
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.85

### Message
> Get uiux feedback from Feedback-20260313-165013: On the same line as Submit button, add KB Reference button (leftmost). (1) Click opens KB Reference Picker. (2) Insert writes selected knowledge paths to .knowledge-reference.yaml in the idea folder. Format: `knowledge-reference: [list of paths]`. (3) Show reference count label; click reveals inline popup listing referenced files with type icons (folder/file).

### Guidance Returned
> Process UIUX feedback Feedback-20260313-165013 as a Change Request on Workplace/Ideation compose. Four tightly coupled sub-requirements: (1) Add KB Reference button left of Submit Idea, (2) Wire to existing KB Reference Picker, (3) On insert, write .knowledge-reference.yaml to idea folder with linked file paths, (4) Display reference count label with click-to-expand popup. Use x-ipe-task-based-change-request to analyze impact and route to refinement → implementation.

### Rationale
> Structured UIUX feedback modifying existing Workplace compose feature by adding KB reference integration. All 4 items are tightly coupled (button→picker→persist→display) — single unit. Keyword match ("uiux feedback" + add button + insert logic) and engineering-next (FEEDBACK → change_request) agree. Existing KB Reference Picker (FEATURE-049-G) provides foundation. Change Request handles impact analysis.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-change-request"
>     match_strength: "strong"
>     reason: "UIUX feedback adding KB reference integration to existing Workplace compose — CR flow analyzes impact, routes to refinement/implementation"
>     execution_steps:
>       - phase: "1. Analyze"
>         step: "1.1 Read CR input and analyze impact"
>       - phase: "2. Process"
>         step: "2.1 Determine if CR modifies existing feature or requires new"
>       - phase: "3. Route"
>         step: "3.1 Route to feature refinement or feature breakdown"

### Follow-up
> None

---

### DAO-067 | CR-004 Button Styling Fix

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-13T13:43:25Z |
| Source | human |
| Task ID | TASK-865 |
| Feature ID | FEATURE-049-G |
| Disposition | instruction |
| Confidence | 0.95 |

**Message:** "the KB Reference button should not be in dark mode"

**Content:** Fix KB Reference button CSS from dark-mode colors (`#2a2a2e`, `#a0a0a8`, `#3a3a3e`) to light-mode colors (`#f8f9fa`, `#495057`, `#dee2e6`) matching the compose pane's existing light theme. Also fix popup colors.

**Rationale:** Direct feedback on just-completed implementation. The compose pane uses light theme (editor toolbar `#f8f9fa`, borders `#dee2e6`, focus `#007bff`) but the button was styled with dark CSS custom properties. Simple CSS correction.

---

### DAO-068 | CR-004 Refinement: Layout, Immediate YAML, Delete

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-13T13:58:31Z |
| Source | human |
| Task ID | TASK-865 |
| Feature ID | FEATURE-049-G |
| Disposition | instruction |
| Confidence | 0.90 |

**Message:** 3 refinements from Feedback-20260313-215355:
1. Move KB button + count label from compose-actions → tab bar area (right side)
2. Create .knowledge-reference.yaml immediately on insert (not deferred to submit)
3. Add delete icon on hover of reference label to remove YAML

**Units:** 3 tightly-coupled units, sequential execution (0→1→2).
