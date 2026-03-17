# DAO Decisions — Investigation

## Entry 1 — Workflow Action Naming Inconsistency Question

- **Timestamp:** 2026-03-17T07:14:33Z
- **Source:** human
- **Task ID:** N/A (ad-hoc investigation)
- **Disposition:** answer
- **Confidence:** 0.95
- **Summary:** User observed naming mismatch between `code_implementation` (used in skills/DAO references) and `implementation` (used in backend workflow engine). Investigated and confirmed the inconsistency exists across multiple layers.
- **Content:** Provided detailed breakdown of where each name is used and identified it as a real inconsistency requiring alignment.

## Entry 2 — Fix All Naming Inconsistencies

- **Timestamp:** 2026-03-17T07:21:47Z
- **Source:** human
- **Task ID:** TBD (to be created on task-board)
- **Disposition:** instruction
- **Confidence:** 0.92
- **Summary:** User instructs to fix all workflow action naming inconsistencies across the codebase. Classified as bug fix — naming mismatches between backend (`implementation`, `acceptance_testing`) and skills/MCP/docs layer (`code_implementation`, `acceptance_test`) can cause silent runtime failures.
- **Suggested Skill:** x-ipe-task-based-bug-fix (strong match)
- **Content:** Align all action names to be consistent across workflow-template.json, workflow_manager_service.py, MCP docstrings, engineering-workflow.md, skills, frontend JS, and workflow state files.

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-112 | 2026-03-17T17:05:00Z | TASK-937 | N/A (direct human message) | instruction | 0.94 | Independently validate TASK-934 / CR-003 for FEATURE-049-B by auditing CR docs, spec/mockup updates, implementation, and tests; report only meaningful gaps |
| DAO-108 | 2026-03-17T16:13:00Z | TASK-NEW | N/A (direct human message) | instruction | 0.90 | Process UIUX feedback: fix duplicate folder chip display in deliverables + add sub-header separator line with right-aligned chips |
| DAO-114 | 2026-03-17T09:11:17Z | TASK-939 | N/A (direct human message) | instruction | 0.95 | Process UIUX feedback Feedback-20260317-170937 as a single bug-fix task to sort feedback entries in ascending A-Z, 0-9 order |
| DAO-115 | 2026-03-17T09:16:51Z | TASK-940 | N/A (direct human message) | instruction | 0.96 | Use real folder names for deliverables folder chips instead of tag names when folder paths end with `/` |
| DAO-116 | 2026-03-17T09:29:51Z | TASK-939 | N/A (direct human message) | instruction | 0.96 | Continue TASK-939 to finish validation, complete independent review, and close the task if the fix remains clean |

## DAO-108
- **Timestamp:** 2026-03-17T16:13:00Z
- **Task ID:** TASK-NEW
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> Get uiux feedback, please visit feedback folder x-ipe-docs/uiux-feedback/Feedback-20260317-161023 to get details.

### Guidance Returned
> Process the UIUX feedback from Feedback-20260317-161023. Fix two issues in the deliverables panel: (1) duplicate 'feature-docs-folder' chip display for feature-050-B — remove duplicate rendering, (2) add a horizontal separator line below deliverable sub-headers spanning the full panel width, and right-align folder chips. Use x-ipe-task-based-bug-fix skill.

### Rationale
> Both feedback items target the same deliverables component in the workflow UI. Item 1 is a clear rendering bug (triplicate chip display). Item 2 is a tightly coupled layout improvement. Single unit with bug-fix skill is the smallest useful intervention.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Duplicate chip rendering is a display bug; layout fix is a tightly coupled UI improvement in the same component"
>     execution_steps:
>       - phase: "1. Diagnose"
>         step: "1.1 Reproduce and identify root cause"
>       - phase: "2. Fix"
>         step: "2.1 Implement fix with failing test first"

### Follow-up
> None

## DAO-116
- **Timestamp:** 2026-03-17T09:29:51Z
- **Task ID:** TASK-939
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.96

### Message
> continue

### Guidance Returned
> Continue the in-progress TASK-939 bug-fix workflow. Finish remaining validation, complete the independent review, and if no meaningful issues are found, close the task and report the outcome.

### Rationale
> The user did not change scope; they asked to resume the current task. The bounded action is to continue the existing bug-fix flow through verification and closure rather than start a new task or reopen requirements.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "The active task is already a bug-fix task, and the user explicitly asked to continue it"
>     execution_steps:
>       - phase: "8. Verify"
>         step: "8 Verify Fix"
>       - phase: "9.1 Decide Next Action"
>         step: "9.1 Decide Next Action"

### Follow-up
> None

## DAO-114
- **Timestamp:** 2026-03-17T09:11:17Z
- **Task ID:** TASK-939
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.95

### Message
> Get uiux feedback, please visit feedback folder x-ipe-docs/uiux-feedback/Feedback-20260317-170937 to get details.

### Guidance Returned
> Process the UIUX feedback from Feedback-20260317-170937 as a single feedback-stage bug-fix task. Update the feedback panel so saved feedback entries are sorted in ascending A-Z, 0-9 order, using a failing test first and then the minimal code change.

### Rationale
> The feedback points to a concrete behavior bug in one UI surface, `#feedback-list`, with a clear expected order and no need to split the request. Routing to the bug-fix skill is the smallest useful intervention because this is an existing behavior correction rather than a new feature.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "The request describes incorrect existing UI behavior and a precise expected ordering rule for the feedback list"
>     execution_steps:
>       - phase: "1. Understand"
>         step: "1 Understand the Bug"
>       - phase: "6. Write Test"
>         step: "6 Write Failing Test"

### Follow-up
> None

| DAO-113 | 2026-03-17T09:06:29Z | TASK-938 | N/A (direct human message) | instruction | 0.95 | Remove feature_closing deliverables from the workflow template and clean existing Knowledge-Extraction workflow data |

## DAO-113
- **Timestamp:** 2026-03-17T09:06:29Z
- **Task ID:** TASK-938
- **Feature ID:** N/A
- **Workflow:** Knowledge-Extraction
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.95

### Message
> it's expected, I found the issue for feature closing we should not have deliverable from this step. so remove the deliverable from the workflow template and fix the data of existing workflow.

### Guidance Returned
> Treat this as a bug fix to workflow metadata semantics. Remove `feature_closing` deliverable declarations from the workflow template, then clean the existing `workflow-Knowledge-Extraction.json` instance so commit/closing metadata is no longer emitted as deliverables.

### Rationale
> The user clarified intended behavior: `feature_closing` should not publish deliverables. The smallest useful intervention is to fix both the source template and the already-materialized workflow data so current UI output matches the intended model.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Current workflow metadata causes incorrect deliverables to appear in the UI, and the user has identified the expected behavior"
>     execution_steps:
>       - phase: "1. Diagnose"
>         step: "1.1 Reproduce and identify root cause"
>       - phase: "2. Fix"
>         step: "2.1 Implement fix with failing test first"

### Follow-up
> None

| DAO-110 | 2026-03-17T08:29:05Z | TASK-936 | N/A (direct human message) | instruction | 0.90 | Process UIUX feedback: fix duplicate deliverables chips and tighten sub-header layout in the deliverables panel |

## DAO-110
- **Timestamp:** 2026-03-17T08:29:05Z
- **Task ID:** TASK-936
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> Get uiux feedback, please visit feedback folder x-ipe-docs/uiux-feedback/Feedback-20260317-161023 to get details.

### Guidance Returned
> Process the UIUX feedback from Feedback-20260317-161023 as a single deliverables-panel bug-fix task. Fix duplicate `feature-docs-folder` chip rendering for FEATURE-050-B, then update the deliverable sub-header layout to add a full-width separator line and right-align folder chips.

### Rationale
> Both requested changes are tightly coupled in the same deliverables-panel surface. The duplicate chip display is the core bug, and the header layout change is a small adjacent UI correction in the same component, so a single bug-fix unit is the smallest complete intervention.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "The feedback centers on broken render output in an existing UI component, with a tightly coupled layout correction in the same surface"
>     execution_steps:
>       - phase: "1. Diagnose"
>         step: "1.1 Reproduce and identify root cause"
>       - phase: "2. Fix"
>         step: "2.1 Implement fix with failing test first"

### Follow-up
> None

| DAO-111 | 2026-03-17T08:37:35Z | TASK-936 | N/A (direct human message) | approval | 0.99 | Human approved renumbering the UIUX bug-fix record after a concurrent task-board collision and continuing with only TASK-936 files |

## DAO-111
- **Timestamp:** 2026-03-17T08:37:35Z
- **Task ID:** TASK-936
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** approval
- **Confidence:** 0.99

### Message
> Yes — renumber it to the next available task ID

### Guidance Returned
> Renumber the UIUX bug-fix record to the next available task ID and finalize only the TASK-936 files, leaving unrelated worktree changes untouched.

### Rationale
> A concurrent session claimed TASK-935 while this bug fix was in flight. The user explicitly approved resolving the collision by assigning the next free ID, which preserves board integrity without disturbing the other session's work.

### Suggested Skills
> suggested_skills: []

### Follow-up
> None
| DAO-109 | 2026-03-17T08:22:44Z | TASK-NEW | N/A (direct human message) | approval | 0.98 | Continue current UI bug-fix flow for the deliverables panel |

## DAO-109
- **Timestamp:** 2026-03-17T08:22:44Z
- **Task ID:** TASK-NEW
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** approval
- **Confidence:** 0.98

### Message
> continue

### Guidance Returned
> Continue the current UI bug-fix flow for the deliverables panel, following the loaded bug-fix skill and task-board process.

### Rationale
> The user is confirming the previously scoped work and not changing scope or requirements.

### Suggested Skills
> suggested_skills: []

### Follow-up
> None

## DAO-112
- **Timestamp:** 2026-03-17T17:05:00Z
- **Task ID:** TASK-937
- **Feature ID:** FEATURE-049-B
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.94

### Message
> Independently validate TASK-934 / CR-003 for FEATURE-049-B in repo /Users/yzhang/Library/CloudStorage/OneDrive-Personal/ML/2026/agent/X-IPE.
>
> Please verify the Definition of Done for the change request work that was just completed:
> - CR documented at x-ipe-docs/requirements/EPIC-049/FEATURE-049-B/CR-003.md
> - Classification determined and appropriate
> - Conflict analysis completed and conflicts are all expected/mitigated
> - Specification version history updated with CR link
> - Conflicting docs resolved appropriately
> - Specification updated for the change
> - Mockup versioning handled appropriately for the UI/UX change
> - Code implementation matches the CR intent
> - Tests added and passing
>
> Read the actual changed artifacts, inspect the relevant JS/CSS/test/spec/mockup files, and provide a concise validation report with any gaps. Surface only meaningful issues.

### Guidance Returned
> Treat this as a single independent validation unit for FEATURE-049-B. Audit the CR document, linked specification/mockup updates, relevant KB browse modal JS/CSS/test artifacts, and execute the pertinent test suite to verify the implementation matches CR-003. Report only meaningful gaps.

### Rationale
> The request is a bounded audit of one completed change request and its directly linked artifacts. Feature acceptance testing is the strongest fit because the user wants implementation-and-test validation, while the CR document itself still needs traceability checks in the same pass.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-acceptance-test"
>     match_strength: "strong"
>     reason: "The user is asking for independent validation of implementation/test completeness for a single feature change"
>     execution_steps:
>       - phase: "1. 博学之 — Study Broadly"
>         step: "1.1 Load Toolbox Config"
>       - phase: "4. 明辨之 — Discern Clearly"
>         step: "4.1 Execute Tests"
>   - skill_name: "x-ipe-task-based-change-request"
>     match_strength: "partial"
>     reason: "The audit must also verify CR classification, conflict analysis, and traceability artifacts"
>     execution_steps:
>       - phase: "3. 慎思之 — Think Carefully"
>         step: "3.1 Detect Conflicts"
>       - phase: "5. 笃行之 — Practice Earnestly"
>         step: "5.1 Execute & Document"

### Follow-up
> None

---

### DAO-111 — Enforce AC Testing for Skills Program Type

| Field | Value |
|-------|-------|
| Task | TASK-936 |
| Feature | N/A (process improvement) |
| Disposition | instruction |
| Confidence | 0.95 |

**Context:** User observed that FEATURE-050-A/B/C all skipped acceptance testing because program_type=skills. User correctly notes that skills are deliverables too and must have AC verification.

**Decision:** Implement "Structured Review" acceptance testing for skills program_type. Based on research:
- For non-code deliverables, acceptance testing = structured criteria-driven review (checklists, inspections, coverage mapping)
- The acceptance-test skill already handles UI/API/CLI/Library — add "skills" as a 5th test type using checklist-based review
- The code-implementation skill explicitly skips AAA for skills — remove this skip and route to acceptance-test skill like all other types
- Test method for skills: AC-by-AC structured review with pass/fail per criterion, coverage mapping, and documented results

**Changes Required:**
1. `x-ipe-task-based-feature-acceptance-test/SKILL.md` — Add "Structured Review" test type for skills/non-code deliverables
2. `x-ipe-task-based-code-implementation/SKILL.md` — Remove the skip-AAA-for-skills exception; ensure next_task routes to acceptance testing

## DAO-115
- **Timestamp:** 2026-03-17T09:16:51Z
- **Task ID:** TASK-940
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.96

### Message
> looks good, btw the folder name can we not using tag name? can we use the real folder name for example 'FEATURE-050-A/'

### Guidance Returned
> Treat this as a focused frontend bug fix in the deliverables panel. Update folder chip labeling so folder paths ending with `/` display the real folder basename with the trailing slash preserved (for example `FEATURE-050-A/`) instead of falling back to the deliverable tag name. Use x-ipe-task-based-bug-fix.

### Rationale
> The user is describing incorrect existing UI behavior in the same deliverables surface already under investigation. The smallest useful intervention is a bug fix: keep current fallback behavior for empty paths, but derive chip labels from real folder paths when available, including trailing-slash folders.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "The request targets incorrect existing folder-chip label behavior in frontend code with a precise expected display result"
>     execution_steps:
>       - phase: "1. Understand"
>         step: "1 Understand the Bug"
>       - phase: "6. Write Test"
>         step: "6 Write Failing Test"

### Follow-up
> None
