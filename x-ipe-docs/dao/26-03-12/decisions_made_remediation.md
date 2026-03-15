# DAO Decisions — Remediation Phase (26-03-12)

---

## DAO-053
- **Timestamp:** 2026-03-12T00:00:00Z
- **Task ID:** TASK-848
- **Feature ID:** N/A
- **Workflow:** Knowledge-Base-Implementation
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** critique
- **Confidence:** 0.95

### Message
> for UI testing why you didn't call chrome-devtools mcp?

### 3-Perspective Analysis

| Perspective | Assessment |
|-------------|-----------|
| **🧑 Supporting** | User is right to question this. The acceptance test skill (`x-ipe-task-based-feature-acceptance-test`) explicitly mandates: "For frontend-ui tests, Chrome DevTools MCP is required." The tools.json config has `chrome-devtools-mcp: true`. The specification.md files classify multiple ACs as `frontend-ui` test type. The agent had every signal to use chrome-devtools-mcp and did not. |
| **🤖 Opposing** | The agent achieved 100% pass rate across all 6 features using vitest and pytest. All tests pass. The functional correctness may be covered even without browser-based testing. Chrome DevTools MCP testing adds complexity and may not find additional bugs if unit tests already cover the logic. |
| **⚖️ Neutral** | The skill spec is unambiguous — `frontend-ui → chrome-devtools-mcp (if enabled)`. It is enabled. The agent deviated from the skill's mandatory procedure. Passing unit tests do NOT substitute for browser-based UI testing: unit tests verify logic in isolation, while chrome-devtools-mcp verifies rendered DOM, user interaction flows, visual rendering, and end-to-end browser behavior. The 100% pass rate is real but incomplete — it covers backend-api, unit, and integration test types but NOT the frontend-ui test type. This is a procedural gap, not a test failure. |

### Phase 2: 致知 — Understanding

**Skill Scan:**
- `x-ipe-task-based-feature-acceptance-test` (strong match) — this is the skill that was executed in TASK-848. Its procedure explicitly states:
  - Test type classification: `frontend-ui → chrome-devtools-mcp (if enabled)`
  - MANDATORY rule: "For frontend-ui tests, Chrome DevTools MCP is required. If chrome-devtools-mcp is disabled in tools.json or MCP is not available, generate test cases but mark UI test execution as blocked."
  - tools.json has `chrome-devtools-mcp: true` under `quality.testing`
- **Engineering workflow position:** VALIDATION stage → `acceptance_testing` action. The agent completed this action but with incomplete tool coverage. The correct remediation is to re-run acceptance testing for frontend-ui classified ACs using chrome-devtools-mcp.

**Disposition Reasoning:**
- `critique` selected because the user is pointing out a procedural deviation, not asking a question or giving a new instruction. The agent failed to follow a MANDATORY rule in the skill it was executing. The DAO must acknowledge this gap clearly and provide corrective guidance.
- NOT `answer` — this is not a neutral information request; the user is flagging a mistake.
- NOT `instruction` — the user hasn't yet commanded a re-run; they're asking WHY it wasn't done.

### Guidance Returned
> The agent did not use chrome-devtools-mcp for frontend-ui acceptance testing, which is a procedural deviation from the `x-ipe-task-based-feature-acceptance-test` skill. The skill mandates: `frontend-ui → chrome-devtools-mcp (if enabled)`, and tools.json confirms `chrome-devtools-mcp: true`. The agent used only vitest (unit/integration) and pytest (backend) — these cover backend-api, unit, and integration test types but do NOT substitute for browser-based UI testing. Frontend-ui ACs (DOM rendering, click interactions, form submissions, visual state) require actual browser execution via chrome-devtools-mcp to be properly validated. The 100% pass rate reported is accurate for the test types that WERE executed, but frontend-ui test type ACs remain unvalidated. **Corrective action:** Re-run acceptance testing for all features that have `frontend-ui` classified ACs, this time routing those specific ACs through chrome-devtools-mcp as the skill requires. The agent should: (1) identify all ACs with Test Type = `frontend-ui` across the 6 features, (2) for each, execute browser-based validation using chrome-devtools-mcp (navigate to page, interact with UI elements, verify rendered output), (3) update acceptance-test-cases.md with browser-test results.

### Rationale
> `critique` — user correctly identified that the agent skipped a mandatory tool routing rule in the acceptance test skill. chrome-devtools-mcp was enabled in tools.json, frontend-ui ACs exist in specs, but the agent used only vitest/pytest. Unit tests ≠ browser tests. This is a skill compliance gap that must be remediated by re-running frontend-ui ACs through chrome-devtools-mcp.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-acceptance-test"
>     match_strength: "strong"
>     reason: "Re-run frontend-ui classified ACs using chrome-devtools-mcp as the skill mandates"
>     execution_steps:
>       - phase: "2. Generate Test Cases"
>         step: "2.1 Classify ACs by Test Type"
>       - phase: "3. Execute Tests"
>         step: "3.1 Route frontend-ui tests to chrome-devtools-mcp"

### Execution Plan

| Field | Value |
|-------|-------|
| **Strategy** | `sequential` |
| **Groups** | `[[0]]` |
| **Rationale** | Single instruction unit — critique with corrective guidance. Downstream agent should re-run acceptance testing for frontend-ui ACs using chrome-devtools-mcp. |

### Follow-up
> Agent should re-run acceptance testing specifically for frontend-ui test type ACs across all 6 MVP features using chrome-devtools-mcp. Backend-api, unit, and integration test results from the prior run remain valid and do not need re-execution.

---

### DAO-054 — Replace native dialogs with Bootstrap 5 modals

| Field | Value |
|-------|-------|
| **Timestamp** | 2026-03-12T13:45:00Z |
| **Source** | human |
| **Task ID** | TASK-849 |
| **Feature ID** | EPIC-049 (cross-cutting) |
| **Workflow** | Knowledge-Base-Implementation |
| **Disposition** | instruction |
| **Confidence** | 0.85 |

**User Need:** Replace all native browser dialogs (alert, confirm, prompt) across the application with Bootstrap 5 styled modal dialogs for consistent UI.

**Unit 0 — instruction:**
Replace all native `alert()`, `confirm()`, and `prompt()` calls with custom Bootstrap 5 modal dialogs. Scope: KB features first (kb-article-editor.js has 1 confirm), then broader codebase (workplace.js has 6, content-editor.js has 3, folder-view.js has 1, quality-evaluation.js has 2, tracing-dashboard.js has 1, kb-article-editor.js has 1). Note: workflow-stage.js and workflow.js already have `_showConfirmModal()` and `_showPromptModal()` implementations that can serve as patterns. This is a change request — use x-ipe-task-based-change-request skill to properly scope and implement.

**Rationale:** User explicitly requested Bootstrap 5 modals over native dialogs. Native dialogs are visually inconsistent with the dark-themed UI. Existing modal patterns in workflow code prove feasibility.

---

### DAO-055 — Continue (TASK-849 done) + Start dialog replacement

| Field | Value |
|-------|-------|
| **Timestamp** | 2026-03-12T15:00:00Z |
| **Source** | human |
| **Task ID** | TASK-849 → new task TBD |
| **Feature ID** | N/A → EPIC-049 (cross-cutting) |
| **Workflow** | Knowledge-Base-Implementation |
| **Calling Skill** | N/A (direct human message) |
| **Confidence** | 0.92 |

**User Message:** "continue first, then work on dialog window update"

**Decomposition:** 2 instruction units identified.

#### Unit 0 — Mark TASK-849 complete

| Field | Value |
|-------|-------|
| **Disposition** | `instruction` |
| **Confidence** | 0.95 |
| **Skill** | `x-ipe+all+task-board-management` |

**Action:** Update TASK-849 from `🔄 in_progress` to `✅ done` on task-board.md. All 34/34 browser UI ACs passed, committed as `7dd1d54`, pushed to GitHub.

#### Unit 1 — Start Bootstrap 5 dialog replacement (DAO-054)

| Field | Value |
|-------|-------|
| **Disposition** | `instruction` |
| **Confidence** | 0.90 |
| **Skill** | `x-ipe-task-based-change-request` |
| **Match Strength** | strong |
| **Prior Reference** | DAO-054 (scoping analysis already done) |

**Action:** Create new task on board, load `x-ipe-task-based-change-request` skill, follow its procedure to analyze impact and implement the replacement of all native `alert()`/`confirm()`/`prompt()` calls with Bootstrap 5 modals. ~14 call sites across 6 JS files. Existing patterns in `workflow-stage.js`/`workflow.js` serve as implementation reference.

**3-Perspective Summary:**
- 🧑 **Supporting:** Native dialogs jarring in dark Bootstrap UI; DAO-054 pre-scoped; existing patterns prove feasibility
- 🤖 **Opposing:** Cosmetic change; sync→async control flow risk; all features work with native dialogs
- ⚖️ **Neutral:** Well-bounded CR; change-request skill will analyze impact per feature and detect conflicts before implementation

#### Execution Plan

| Field | Value |
|-------|-------|
| **Strategy** | `sequential` |
| **Groups** | `[[0], [1]]` |
| **Rationale** | Unit 0 (board cleanup) completes before Unit 1 (new work). Unit 1 is the substantive task — routed to change-request skill. |

#### Suggested Skills

```yaml
instruction_units:
  - unit: 0
    disposition: instruction
    suggested_skills:
      - skill_name: "x-ipe+all+task-board-management"
        match_strength: "exact"
        reason: "Update TASK-849 status to done"
  - unit: 1
    disposition: instruction
    suggested_skills:
      - skill_name: "x-ipe-task-based-change-request"
        match_strength: "strong"
        reason: "Cross-cutting CR to replace native dialogs with Bootstrap 5 modals — DAO-054 pre-scoped"
execution_plan:
  strategy: sequential
  groups: [[0], [1]]
```

## DAO-056

| Field | Value |
|-------|-------|
| **Timestamp** | 2026-03-12 |
| **Source** | ai / x-ipe-task-based-change-request |
| **Task** | TASK-850 |
| **Request** | Confirm CR classification as MODIFICATION for Bootstrap 5 dialog replacement |
| **Disposition** | `approval` |
| **Confidence** | 0.95 |

### Phase 1 — Restate & Decompose

**Need:** The change-request skill completed challenge + conflict analysis for replacing 14 native browser dialogs (`alert`, `confirm`, `prompt`) with Bootstrap 5 modals across 6 JS files. It asks: is this a MODIFICATION or a NEW FEATURE?

**Decomposition:**
1. Does this introduce new capabilities? → No. Same user actions, same outcomes, improved presentation only.
2. Does this add new data models, API endpoints, workflows, or user types? → No. Zero backend changes.
3. Does the cross-cutting nature (6 files, ~5 features) change the classification? → No. Cross-cutting MODIFICATIONs are valid; breadth ≠ novelty.
4. Does extracting a shared utility constitute a new feature? → No. Utility extraction is an implementation technique, not a user-facing capability.

### Phase 2 — Three Perspectives & Disposition

| Perspective | Position |
|-------------|----------|
| 🧑 **Supporting** | Textbook MODIFICATION — same behavior, better UI. No new workflows, data models, or endpoints. Existing Bootstrap modal patterns in `workflow-stage.js` prove the codebase already "knows" this pattern. Conflict analysis found zero conflicts. |
| 🤖 **Opposing** | Could argue cross-cutting scope (6 files, 5+ features) warrants NEW FEATURE for better tracking granularity. Sync→async control flow shift (native dialogs are synchronous, Bootstrap modals are async) is a behavioral change, not just cosmetic. | 
| ⚖️ **Neutral** | Opposing points are implementation risks, not classification arguments. MODIFICATION is correct by CR taxonomy: existing functionality, improved presentation, no new capabilities. The async refactor is contained within each call site. |

**Disposition committed: `approval`**

MODIFICATION is the correct classification. The work replaces UI presentation layer (native → Bootstrap modal) without introducing new user-facing capabilities, data models, or system boundaries.

### Action

Confirm MODIFICATION classification. The change-request skill should proceed to refinement, routing the work as modifications to existing features (primarily FEATURE-049-D for KB scope, plus the other affected features).

---

## DAO-057

| Field | Value |
|-------|-------|
| **Timestamp** | 2026-03-12T16:30:00Z |
| **Source** | ai / x-ipe-task-based-change-request |
| **Task ID** | TASK-850 |
| **Feature ID** | FEATURE-049-D |
| **Workflow** | Knowledge-Base-Implementation |
| **Calling Skill** | x-ipe-task-based-change-request |
| **Disposition** | `instruction` |
| **Confidence** | 0.90 |

### Message
> CR-001 is complete. Classification: MODIFICATION. The CR scope is well-defined: create a shared utility module and replace 14 native dialog calls. Existing patterns in workflow-stage.js already prove the approach. Options: A) Full pipeline (refinement → design → implementation → acceptance test), B) Skip to code-implementation directly, C) Lightweight refinement (update spec ACs only) then implementation.

### 3-Perspective Analysis

| Perspective | Assessment |
|-------------|-----------|
| 🧑 **Supporting** | Scope IS crystal clear — 14 native dialog calls, 6 files, proven pattern in `workflow-stage.js`. Full pipeline is overkill for a cosmetic change with proven approach. Option B or C saves time without meaningful risk. |
| 🤖 **Opposing** | Skipping refinement means no updated specification ACs. Acceptance testing then has nothing formal to validate against. Skipping erodes engineering discipline — sync→async control flow shift can have subtle bugs even in "obvious" changes. |
| ⚖️ **Neutral** | Option C is the correct balance. Update specification ACs to create testable criteria, then skip technical_design (approach is proven in codebase), proceed to code_implementation → acceptance_test. Engineering workflow DAG says `change_request → feature_refinement` — Option C aligns with the process while acknowledging scope simplicity. |

### Phase 2 — Skill Scan & Disposition

**Engineering workflow position:** FEEDBACK → `change_request` (just completed). DAG says next = `feature_refinement` (for MODIFICATION). Keyword match + engineering-next **agree** → high confidence.

**Disposition reasoning:**
- `instruction` selected — calling skill explicitly asks for routing guidance with preferred_dispositions: ["instruction"]. This is a routing decision, not a question or approval.
- Option A rejected: 害 > 利 — technical design adds zero value when approach is proven in `workflow-stage.js`
- Option B rejected: 利 high but 害 real — no updated ACs means acceptance testing has no formal criteria; process violation
- Option C selected: 利 >> 害 — creates testable ACs, preserves traceability, skips only the redundant step (technical design)

### Guidance Returned
> **Route: Option C — Lightweight refinement → skip technical_design → code_implementation → acceptance_test.**
>
> 1. **Feature Refinement (lightweight):** Update FEATURE-049-D specification.md to add/modify ACs for the Bootstrap 5 modal replacement. Focus on: (a) shared utility module (`dialog-utils.js`) ACs — alert/confirm/prompt wrapper functions, Bootstrap 5 modal rendering, async Promise-based API; (b) per-file replacement ACs — each of the 14 call sites replaced and working; (c) visual consistency ACs — modals match existing dark theme. Do NOT create a new feature — modify the existing FEATURE-049-D spec.
> 2. **Skip technical_design** — approach is already proven in `workflow-stage.js` (`_showConfirmModal()`, `_showPromptModal()`). No new architectural decisions needed.
> 3. **Code Implementation** — create shared utility, replace 14 call sites, write tests.
> 4. **Acceptance Testing** — validate against the updated ACs from step 1.

### Rationale
> `instruction` — CR-001 completed as MODIFICATION. Engineering DAG routes to `feature_refinement`. Option C balances process compliance (updated ACs for testability) with efficiency (skip redundant technical design). The approach is proven in the codebase — `workflow-stage.js` already implements Bootstrap 5 modal patterns. Lightweight refinement creates the formal criteria acceptance testing needs without unnecessary overhead.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-refinement"
>     match_strength: "strong"
>     reason: "CR classified as MODIFICATION → update existing feature spec with modal replacement ACs"
>     execution_steps:
>       - phase: "1. Query Context"
>         step: "1.1 Read feature board and existing spec"
>       - phase: "2. Refine Specification"
>         step: "2.1 Update ACs for dialog replacement scope"

### Execution Plan

| Field | Value |
|-------|-------|
| **Strategy** | `sequential` |
| **Groups** | `[[0]]` |
| **Rationale** | Single instruction unit — routing guidance for post-CR pipeline. Agent should execute lightweight feature refinement next, then proceed to code_implementation (skipping technical_design). |

### Follow-up
> After lightweight refinement updates the spec ACs, proceed directly to `x-ipe-task-based-code-implementation` (skip `x-ipe-task-based-technical-design`). Then run `x-ipe-task-based-feature-acceptance-test` against the updated ACs.

---

## DAO-058
- **Timestamp:** 2026-03-12T22:30:00Z
- **Task ID:** TASK-850
- **Feature ID:** N/A
- **Workflow:** Knowledge-Base-Implementation
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** instruction (×2 units)
- **Confidence:** 0.85

### Message
> but me, I still cannot click intake menu, and I don't know how to get into the general knowledge base home page

### Instruction Unit 1 — Intake Placeholder UX Bug
> **Disposition:** instruction
> **Content:** The "📥 Intake" sidebar item is a static placeholder for post-MVP FEATURE-049-F. It currently appears interactive but does nothing on click, creating a misleading UX pattern. Fix: make the placeholder visually indicate it's a future/disabled feature — add a "Coming Soon" tooltip, apply a disabled/dimmed visual style, and suppress click events so it doesn't appear broken. Do NOT implement Intake functionality — only fix the misleading affordance.
> **Depends on:** none

### Instruction Unit 2 — KB Browse Page Navigation Discoverability Bug
> **Disposition:** instruction
> **Content:** The KB browse/home view currently requires DOUBLE-CLICKING the KB section header or a folder header in sidebar.js (_bindKBFolderClicks, lines 690-725). Single-click only expands/collapses the tree. This is an undiscoverable interaction pattern — users cannot find how to navigate to the main KB page. Fix: add a discoverable single-click entry point to the KB browse view. Options include: (a) add a visible "📚 Browse" or "🏠 Home" sub-item under the KB section, (b) make single-click on the KB section header navigate to browse view (move expand/collapse to a chevron), or (c) add a right-click context menu option. Choose the approach that best fits the existing sidebar patterns.
> **Depends on:** none (but sequential execution due to same-file write conflict with Unit 1)

### Rationale
> Both issues are UX/usability bugs discovered during human playground testing (FEEDBACK stage → discovery loop → bug-fix). The Intake placeholder creates a false interactive affordance; the KB navigation requires an undiscoverable double-click. Both are low-risk sidebar fixes. Sequential execution recommended because both modify sidebar.js. Engineering workflow: FEEDBACK → bug-fix → acceptance_testing.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Unit 1 — Intake placeholder appears clickable but is non-functional; UX bug in sidebar"
>     execution_steps:
>       - phase: "1. Diagnose"
>         step: "1.1 Reproduce the bug — click Intake in sidebar, confirm no response"
>       - phase: "2. Fix"
>         step: "2.1 Add disabled visual state and Coming Soon tooltip to Intake placeholder"
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Unit 2 — KB browse page requires undiscoverable double-click; navigation UX bug"
>     execution_steps:
>       - phase: "1. Diagnose"
>         step: "1.1 Confirm double-click is only path to KB browse view"
>       - phase: "2. Fix"
>         step: "2.1 Add discoverable single-click entry point for KB browse navigation"

### Execution Plan

| Field | Value |
|-------|-------|
| **Strategy** | `sequential` |
| **Groups** | `[[0], [1]]` |
| **Rationale** | Both units modify sidebar.js — sequential execution avoids write conflicts. Unit 1 (Intake placeholder) first, then Unit 2 (KB navigation discoverability). |

### Follow-up
> Execute both bug-fixes via `x-ipe-task-based-bug-fix` skill, sequentially. After each fix, run `x-ipe-task-based-feature-acceptance-test` to validate. Both are UX-only changes — no backend or data model impact.

---

## DAO-059
- **Timestamp:** 2026-03-12T13:30:00+08:00
- **Task ID:** TASK-851
- **Feature ID:** FEATURE-049-B, FEATURE-049-D
- **Workflow:** Knowledge-Base-Implementation
- **Calling Skill:** x-ipe-task-based-bug-fix
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.85

### Message
> don't change sidebar logic, can we do this, for knowledge base entry can we put it on top bar, on the rightside of the workflow mode. when click on the knowledge base text or icon, open a modal window, the left side should the knowledge base folder tree as is, the right side show the content

### Guidance Returned
> Revert TASK-851 sidebar changes (📚 Browse All item + Intake placeholder styling). Instead, add a KB icon/button to the top bar (right of workflow mode toggle). On click, open a Bootstrap 5 modal with split-pane layout: left panel = KB folder tree (reuse existing tree rendering from sidebar.js), right panel = article content viewer (reuse kb-browse/kb-article-editor rendering). This stays within TASK-851 scope as a course-correction for KB browse discoverability. Classify as change request within existing task — use x-ipe-task-based-change-request to process impact, then x-ipe-task-based-code-implementation for the modal.

### Rationale
> User explicitly rejected the sidebar "Browse All" approach and specified a concrete alternative (top-bar modal with tree+content). This is a clear instruction with well-defined UI requirements. The modal pattern improves discoverability — KB becomes globally accessible from any page, not buried in sidebar navigation. Classifying as CR within TASK-851 to keep workflow clean.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-change-request"
>     match_strength: "strong"
>     reason: "User is changing the KB navigation approach from sidebar-based to top-bar modal — modifies FEATURE-049-D integration"
>     execution_steps:
>       - phase: "1. Impact Analysis"
>         step: "1.1 Analyze scope of change"
>   - skill_name: "x-ipe-task-based-code-implementation"
>     match_strength: "partial"
>     reason: "After CR processed, implementation of the KB modal component"
>     execution_steps:
>       - phase: "3. Implementation"
>         step: "3.1 Code implementation"

### Follow-up
> 1. Revert uncommitted sidebar.js and sidebar.css TASK-851 changes. 2. Process as CR-002 under FEATURE-049-D. 3. Implement KB top-bar modal with tree+content split layout.

| DAO-060 | 2026-03-12T05:35:29Z | TASK-852 | N/A | instruction | 0.90 | Simplify DAO 格物+致知 phases for efficiency |

## DAO-060
- **Timestamp:** 2026-03-12T05:35:29Z
- **Task ID:** TASK-852
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> for 'DAO' let's base on the 格物，致知，录，示，backbone, but for 格物 and 致知 part, can we make it more simple and efficient, so it won't spent too much time on these two part

### Guidance Returned
> User directs simplification of DAO phases 1 (格物) and 2 (致知). Keep 5-phase backbone. Merge/compress internal substeps to reduce token/time cost. Use x-ipe-meta-skill-creator to update the skill.

### Rationale
> Project owner giving clear design direction. Current 6 substeps across phases 1-2 are verbose for routine messages. Merging and compressing preserves cognitive rigor while reducing overhead.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-meta-skill-creator"
>     match_strength: "strong"
>     reason: "Updating an existing skill (DAO) requires the skill creator process"
>     execution_steps:
>       - phase: "Candidate creation"
>         step: "Update SKILL.md in candidate folder"

### Follow-up
> None

---

## DAO-060
- **Timestamp:** 2026-03-12T13:50:00+08:00
- **Task ID:** TASK-851
- **Feature ID:** FEATURE-049-B, FEATURE-049-C, FEATURE-049-D, FEATURE-049-E
- **Workflow:** Knowledge-Base-Implementation
- **Calling Skill:** x-ipe-task-based-change-request
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> the modal window for it should be following standard size in x-ipe, 2. intake menu is missing 3. all the views in mockup should be implemented, and the ui and ux should be exactly the same!

### Guidance Returned
> Three issues with the KB browse modal: (1) Modal size must match X-IPE standard — 90vw × 90vh per kb-article-editor pattern. (2) Intake (📥) entry must appear in the modal navigation. (3) The modal must implement ALL 4 mockup scenes: Browse Articles (grid/list with search, filters, sort, upload), Article Detail (with metadata sidebar), Reference Picker (already exists separately), and Intake (AI Librarian — FEATURE-049-F placeholder). The UI must exactly match the mockup's visual design including card layout, filter chips, tag taxonomy, stats bar, upload section, article layout with sidebar metadata, and intake table view.

### Rationale
> User is explicitly demanding mockup-faithful implementation. The current KB browse modal is too basic — it shows only a folder tree + content viewer. The mockup defines a much richer 4-scene experience with specific visual patterns. This is a continuation of CR-002, expanding scope to match the full mockup specification.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-code-implementation"
>     match_strength: "strong"
>     reason: "Full UI implementation matching mockup scenes — major coding task"
>     execution_steps:
>       - phase: "3. Implementation"
>         step: "3.1 Code implementation"

### Follow-up
> Rewrite kb-browse-modal.js and kb-browse-modal.css to faithfully implement all 4 mockup scenes. Use the frontend-design skill for pixel-perfect UI matching.

---

## DAO-061
- **Timestamp:** 2026-03-12T15:30:00+08:00
- **Task ID:** TASK-851
- **Feature ID:** FEATURE-049-B, FEATURE-049-C, FEATURE-049-D
- **Workflow:** Knowledge-Base-Implementation
- **Calling Skill:** x-ipe-task-based-bug-fix
- **Source:** human
- **Disposition:** instruction (×3 units)
- **Confidence:** 0.92

### Message
> there are several bugs: 1. upload to didn't show all the folders exists in the knowledge base. 2. upload file drag & drop for both normal and intake is not working, the drag and drop in the intake view also not working. 3. the right panel in the knowledge detailed view should stick to the right

### Guidance Returned

> **Unit 0 — Upload folder picker incomplete:** The "Upload to:" breadcrumb (`data-action="toggle-folder-dropdown"` at L428) has NO handler in `_handleAction()`. The `_getFolderNames()` method (L108-114) only extracts folder names from already-loaded files, which may miss empty or newly-created folders. Fix: (a) Add a `toggle-folder-dropdown` case in the action handler that renders a dropdown listing ALL KB folders, (b) query the KB API for the complete folder tree instead of deriving from loaded file paths.
>
> **Unit 1 — Drag & drop not working:** Both `.kb-upload-zone` and `.kb-intake-dropzone` only have click-based action handlers (`trigger-upload`, `trigger-intake-upload`). There are ZERO `dragover`/`dragleave`/`drop` event listeners in the entire modal. The "Drag & drop" text is purely visual. Fix: Add `dragover` (preventDefault + visual feedback), `dragleave` (remove feedback), and `drop` (preventDefault + process `e.dataTransfer.files`) event listeners to both zones. Wire the dropped files into the respective upload flows (normal → `kbFileUpload`, intake → intake file list).
>
> **Unit 2 — Right panel not sticky:** `.kb-article-sidebar` (CSS L942) has no sticky positioning. The parent `.kb-article-layout` (L829) uses `overflow: hidden` which prevents CSS sticky from working. Fix: Add `position: sticky; top: 0; align-self: flex-start;` to `.kb-article-sidebar` and change parent overflow to `overflow-y: auto` or move overflow handling to `.kb-article-main` only.

### Rationale
> User is performing post-implementation QA on commit 8751fdc (KB browse modal redesign). All 3 bugs are confirmed by code inspection — they are genuine missing implementations, not regressions. Each targets a different subsystem (folder data logic, drag event handlers, CSS layout) and can be fixed independently in parallel.

### Suggested Skills
> **Unit 0:**
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Missing folder dropdown handler and incomplete folder enumeration"
>     execution_steps:
>       - phase: "1. Diagnose"
>         step: "1.1 Reproduce and identify root cause"
>       - phase: "2. Fix"
>         step: "2.1 Implement fix"
>       - phase: "3. Validate"
>         step: "3.1 Acceptance test"
>
> **Unit 1:**
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Missing drag & drop event listeners on upload zones"
>     execution_steps:
>       - phase: "1. Diagnose"
>         step: "1.1 Reproduce and identify root cause"
>       - phase: "2. Fix"
>         step: "2.1 Implement fix"
>       - phase: "3. Validate"
>         step: "3.1 Acceptance test"
>
> **Unit 2:**
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "CSS sticky positioning missing on article detail sidebar"
>     execution_steps:
>       - phase: "1. Diagnose"
>         step: "1.1 Reproduce and identify root cause"
>       - phase: "2. Fix"
>         step: "2.1 Implement fix"
>       - phase: "3. Validate"
>         step: "3.1 Acceptance test"

### Execution Plan
> - **Strategy:** parallel
> - **Groups:** [[0, 1, 2]]
> - **Rationale:** All 3 bugs target different code areas (folder dropdown logic in JS, drag event listeners in JS, CSS positioning). No shared state or data dependencies. Safe to fix concurrently by separate agents.

### Follow-up
> None — all 3 bugs are clear and actionable. No clarification needed.
