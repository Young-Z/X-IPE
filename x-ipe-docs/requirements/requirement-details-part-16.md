# Requirement Details — Part 16

> Part 16 of the X-IPE requirement details series
> Epics covered: EPIC-044

---

## EPIC-044: CR — Unified Auto-Proceed & Decision Making for Workflow Mode

### Project Overview

A Change Request to replace the fragmented `auto_proceed` (boolean) and `require_human_review` (boolean) flags across all 22 task-based skills, the `x-ipe-workflow-task-execution` orchestrator, the `x-ipe-meta-skill-creator` template, and the workflow runtime (`workflow-{name}.json`) with a unified **3-mode `process_preference.auto_proceed`** enum. Introduces a new **`x-ipe-tool-decision-making`** tool skill for autonomous conflict/question resolution, and a shared **`x-ipe-docs/decision_made_by_ai.md`** audit log.

**Source:** [IDEA-031 Refined Summary](x-ipe-docs/ideas/031. CR-Adding Auto Proceed option to workflow mode/refined-idea/idea-summary-v1.md)

### User Request

> "Update existing auto_proceed and require_human_review behavior to workflow skills and all task-based skills. Introduce a general structure with 3 modes (manual, auto, stop_for_question). Create a decision_making_skill. Update all existing task-based skills. Update workflow skill. Add UI toggle for workflow mode."

### Clarifications

| Question | Answer |
|----------|--------|
| Scope of auto_proceed — workflow-level or per-feature? | Workflow-global (all features share one mode). Flag stored in `workflow-{name}.json` global section. |
| `stop_for_question` — what exactly stops? | Inter-task: auto-proceed. Within-skill questions/conflicts: stop for human feedback. |
| `auto` mode — what if decision skill can't resolve? | Log as UNRESOLVED in `decision_made_by_ai.md`, continue execution. Human reviews later. |
| Decision log location? | Single shared `x-ipe-docs/decision_made_by_ai.md` per project. Structured with decision registry table + detail sections. |
| Web search in decision_making_skill? | Yes, optional — used for general topics, skipped for project-specific questions. |
| Is this a CR? | Yes — modifies existing skills/features. |
| Skill input parameter design? | `process_preference.auto_proceed` is a standard input field on every task-based skill SKILL.md. |
| Free-mode behavior? | CLI flags: `--proceed@auto`, `--proceed@stop-for-question`. Default: `manual` (preserving current behavior). |
| Rollout strategy? | All 22 skills updated simultaneously as one big CR. |
| Decision making skill type? | Tool skill (lightweight, invoked inline, no task board entry). |
| Multi-problem support? | Decision context accepts a `problems` array supporting multiple problems per call. |
| Multi next steps in auto-proceed? | Both `auto` and `stop_for_question` modes invoke decision_making_skill when multiple next steps are suggested. |

### High-Level Requirements

1. **HLR-044.1: Unified Process Preference** — All task-based skills MUST replace `auto_proceed` (bool) and `require_human_review` (bool) with a single `process_preference.auto_proceed` enum (`manual | auto | stop_for_question`). Default: `manual`.

2. **HLR-044.2: 3-Mode Behavior** — The system MUST support three execution modes with the following behavior:
   - `manual`: Agent stops between tasks and stops for within-skill questions (current behavior).
   - `stop_for_question`: Agent auto-proceeds between tasks but stops for within-skill questions/conflicts (human decides).
   - `auto`: Agent auto-proceeds between tasks and calls `x-ipe-tool-decision-making` for within-skill questions/conflicts (fully autonomous).

3. **HLR-044.3: Decision Making Tool Skill** — A new tool skill (`x-ipe-tool-decision-making`) MUST be created that AI agents invoke inline to resolve questions and conflicts autonomously when running in `auto` mode.

4. **HLR-044.4: Decision Audit Log** — All AI-made decisions MUST be logged to `x-ipe-docs/decision_made_by_ai.md` with structured registry + detail sections. Unresolvable items MUST be logged as `UNRESOLVED` and execution continues.

5. **HLR-044.5: Workflow Template & Runtime** — `workflow-template.json` MUST include a `global.process_preference.auto_proceed` field (default: `manual`). Runtime `workflow-{name}.json` MUST support this field with runtime updates via UI toggle.

6. **HLR-044.6: Workflow Orchestrator Update** — `x-ipe-workflow-task-execution` MUST route all flow-control decisions through `process_preference.auto_proceed`. All other stopping/gating logic MUST be consolidated. In `auto`/`stop_for_question` modes with multiple `next_actions_suggested`, the orchestrator MUST invoke `x-ipe-tool-decision-making` to choose.

7. **HLR-044.7: Skill Creator Template Update** — The `x-ipe-meta-skill-creator` task-based template MUST include `process_preference.auto_proceed` as a standard input parameter for all future skills.

8. **HLR-044.8: Workflow UI Toggle** — The workflow panel MUST display a workflow-global execution mode toggle (manual/auto/stop_for_question). Changing the toggle MUST update `workflow-{name}.json` via backend API.

9. **HLR-044.9: Free-Mode Support** — When not in workflow-mode, skills MUST support CLI flags (`--proceed@auto`, `--proceed@stop-for-question`) to set the execution mode. Default is `manual`.

10. **HLR-044.10: Backward Compatibility** — `manual` mode MUST preserve 100% backward compatibility with current behavior across all skills and workflows.

### Functional Requirements

#### FR Group 1: Process Preference Input (Skill-Level)

- **FR-044.1:** Every task-based skill SKILL.md input YAML MUST include `process_preference.auto_proceed: "manual | auto | stop_for_question"` with default `manual`.
- **FR-044.2:** The existing `auto_proceed: false` boolean input MUST be removed from all 22 skill SKILL.md files.
- **FR-044.3:** The existing `require_human_review: yes` output field MUST be removed from all 22 skill SKILL.md Output Result YAML blocks.
- **FR-044.4:** Each skill's `task_completion_output` MUST include `process_preference.auto_proceed: "{from input}"` (pass-through for orchestrator routing).

#### FR Group 2: Mode-Aware Execution (Within-Skill)

- **FR-044.5:** In `manual` mode, skills MUST stop and ask human at every decision point and at skill completion review (current behavior).
- **FR-044.6:** In `stop_for_question` mode, skills MUST stop and ask human at every within-skill decision point (same as manual for questions/conflicts).
- **FR-044.7:** In `auto` mode, skills MUST invoke `x-ipe-tool-decision-making` instead of asking human at every within-skill decision point.
- **FR-044.8:** In `manual` and `stop_for_question` modes, skills MUST present results to human and wait for approval at skill completion.
- **FR-044.9:** In `auto` mode, skills MUST skip human review at skill completion.
- **FR-044.10:** Each skill's human-review/approval step MUST be replaced with a mode-aware conditional block checking `process_preference.auto_proceed`.

#### FR Group 3: Decision Making Tool Skill

- **FR-044.11:** A new tool skill `x-ipe-tool-decision-making` MUST be created at `.github/skills/x-ipe-tool-decision-making/SKILL.md`.
- **FR-044.12:** The skill MUST accept `decision_context` input with: `calling_skill`, `task_id`, `feature_id` (optional), `workflow_name`, and `problems` array.
- **FR-044.13:** Each problem in the `problems` array MUST have: `problem_id`, `description`, `type` (question | conflict | routing), `options` (optional list), `related_files` (optional list).
- **FR-044.14:** The skill MUST execute a 6-step process: (1) Identify & classify problems, (2) Study project docs/tests/code, (3) Optional web search for general topics, (4) Sub-agent critique with constructive feedback, (5) Refine answers/solutions, (6) Record to decision_made_by_ai.md.
- **FR-044.15:** When a problem cannot be resolved, the skill MUST log it as `UNRESOLVED` in `decision_made_by_ai.md` and return to the calling skill to continue execution.
- **FR-044.16:** The skill MUST return a structured response with decision per problem: `{ problem_id, status: "resolved|unresolved", decision, rationale }`.

#### FR Group 4: Decision Audit Log

- **FR-044.17:** A single shared decision log file MUST exist at `x-ipe-docs/decision_made_by_ai.md`.
- **FR-044.18:** The log MUST have a Decision Registry table with columns: #, Date, Task ID, Feature ID, Skill, Workflow, Problem Type, Status, Section link.
- **FR-044.19:** Each decision detail section MUST include: Task/Skill/Workflow metadata, Problem description, Type, Context, Analysis (project docs insight, web research, critique feedback), Decision, Rationale, Follow-up Required.
- **FR-044.20:** Decision IDs (D-001, D-002, ...) MUST be globally unique per project (auto-increment from existing registry).
- **FR-044.21:** In multi-agent scenarios, each agent MUST append atomically to avoid corruption.
- **FR-044.22:** A template for `decision_made_by_ai.md` MUST be created in the decision-making skill's templates folder.

#### FR Group 5: Workflow Orchestrator Updates

- **FR-044.23:** `x-ipe-workflow-task-execution` Step 6 (Task Routing) MUST use 3-mode logic instead of boolean `auto_proceed`:
  - `manual`: STOP, wait for human instruction.
  - `stop_for_question`: auto-proceed to next task. If multiple `next_actions_suggested`, invoke `x-ipe-tool-decision-making` (type: routing).
  - `auto`: auto-proceed to next task. If multiple `next_actions_suggested`, invoke `x-ipe-tool-decision-making` (type: routing).
- **FR-044.24:** `x-ipe-workflow-task-execution` MUST remove/consolidate all other flow-control logic — `process_preference.auto_proceed` is the SOLE gate for task continuation.
- **FR-044.25:** The orchestrator's Input Parameters MUST replace `auto_proceed: true | false` with `process_preference.auto_proceed: "manual | auto | stop_for_question"`.
- **FR-044.26:** The orchestrator MUST resolve `process_preference.auto_proceed` from: (a) `workflow-{name}.json` global section in workflow-mode, (b) CLI flag in free-mode, (c) default `manual`.

#### FR Group 6: Workflow Template & Runtime

- **FR-044.27:** `workflow-template.json` (both at `x-ipe-docs/config/` and `src/x_ipe/resources/config/`) MUST add a `global` section: `{ "global": { "process_preference": { "auto_proceed": "manual" } } }`.
- **FR-044.28:** When creating a new workflow instance (`workflow-{name}.json`), the backend MUST copy the `global.process_preference` from the template.
- **FR-044.29:** The backend MUST expose an API endpoint (e.g., `PATCH /api/workflow/{name}/settings`) to update `global.process_preference.auto_proceed` at runtime.
- **FR-044.30:** The `workflow-{name}.json` file MUST persist the `global.process_preference.auto_proceed` value across server restarts.

#### FR Group 7: Workflow UI Toggle

- **FR-044.31:** The workflow panel header MUST display an "Execution Mode" dropdown/toggle with 3 options: Manual, Auto, Stop for Question.
- **FR-044.32:** Changing the toggle MUST call the backend API (FR-044.29) to update `workflow-{name}.json`.
- **FR-044.33:** The toggle state MUST reflect the current value from `workflow-{name}.json` on page load.
- **FR-044.34:** The toggle MUST be workflow-global (applies to all features within the workflow).

#### FR Group 8: Skill Creator Template Update

- **FR-044.35:** The `x-ipe-meta-skill-creator` task-based template MUST include `process_preference.auto_proceed` in the Input Parameters section.
- **FR-044.36:** The template MUST include a mode-aware conditional block pattern in the Execution Procedure section for human-review steps.
- **FR-044.37:** The template MUST NOT include `require_human_review` in the Output Result section.

#### FR Group 9: Free-Mode CLI Integration

- **FR-044.38:** The workflow-task-execution orchestrator MUST recognize `--proceed@auto` CLI flag and map to `auto` mode.
- **FR-044.39:** The workflow-task-execution orchestrator MUST recognize `--proceed@stop-for-question` CLI flag and map to `stop_for_question` mode.
- **FR-044.40:** If no `--proceed@` flag is provided in free-mode, the default MUST be `manual`.

### Non-Functional Requirements

- **NFR-044.1:** `manual` mode MUST produce identical behavior to the current system (zero regressions).
- **NFR-044.2:** Decision log writes MUST be atomic (no partial entries visible to concurrent readers).
- **NFR-044.3:** All 22 skill SKILL.md updates MUST pass `x-ipe-meta-skill-creator` validation (structure, required sections, YAML schema).
- **NFR-044.4:** The UI toggle MUST update within 1 second of user interaction (optimistic update pattern).

### Constraints

- All 22 task-based skills + orchestrator + template updated in one batch (no phased rollout).
- `x-ipe-tool-decision-making` is a tool skill, NOT a task-based skill.
- Web search in decision_making_skill is optional and context-dependent.
- Workflow `global.process_preference` is workflow-level, not per-feature.

### Acceptance Criteria

- [ ] AC-044.1: All 22 task-based skills have `process_preference.auto_proceed` input parameter (enum, default: manual)
- [ ] AC-044.2: No skill contains `auto_proceed: false` (boolean) or `require_human_review: yes` in input/output
- [ ] AC-044.3: `x-ipe-tool-decision-making` SKILL.md exists with 6-step process, multi-problem input
- [ ] AC-044.4: `decision_made_by_ai.md` template exists with registry + detail format
- [ ] AC-044.5: `workflow-template.json` has `global.process_preference.auto_proceed: "manual"` field
- [ ] AC-044.6: New workflow instances inherit `global.process_preference` from template
- [ ] AC-044.7: Backend API `PATCH /api/workflow/{name}/settings` updates auto_proceed value
- [ ] AC-044.8: Workflow panel shows execution mode toggle; changing it calls API
- [ ] AC-044.9: `x-ipe-workflow-task-execution` uses 3-mode routing (no boolean auto_proceed)
- [ ] AC-044.10: Orchestrator consolidates all flow-control to single `process_preference.auto_proceed` gate
- [ ] AC-044.11: `x-ipe-meta-skill-creator` template includes `process_preference` standard input
- [ ] AC-044.12: CLI flags `--proceed@auto` and `--proceed@stop-for-question` work in free-mode
- [ ] AC-044.13: `manual` mode produces identical behavior to current system (backward compatible)
- [ ] AC-044.14: In `auto` mode, within-skill questions invoke `x-ipe-tool-decision-making` instead of asking human
- [ ] AC-044.15: In `stop_for_question` mode, inter-task flow auto-proceeds, within-skill questions stop for human
- [ ] AC-044.16: Unresolvable decisions logged as UNRESOLVED in decision_made_by_ai.md, execution continues
- [ ] AC-044.17: Multiple `next_actions_suggested` handled by decision_making_skill in auto/stop_for_question modes
- [ ] AC-044.18: All 22 updated SKILL.md files pass skill-creator validation

### Related Features (Conflict Review)

| Existing Feature | Overlap Type | Decision |
|-----------------|--------------|----------|
| EPIC-040 (Workflow Mode Execution) | Extension — added `execution_mode` + `workflow.name` to skills. EPIC-044 adds `process_preference.auto_proceed` alongside. | Extend — no conflict, EPIC-044 adds new input field to the same parameter block |
| EPIC-041 (Skill Workflow Enrichment) | Extension — added `workflow.action`, `feature_id`, `extra_context_reference`. EPIC-044 adds another parameter. | Extend — no conflict, parallel new field |
| EPIC-042 (Workflow Prompts Config) | Orthogonal — prompt resolution is independent of execution mode | No conflict |
| EPIC-043 (File Link Preview) | No overlap | No conflict |

No CR impact markers needed — all overlaps are extensions (new fields added alongside existing ones).

### Open Questions

- None — all clarified during ideation.

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| N/A | No mockups for this CR (skill/config changes) |

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-044-A | EPIC-044 | Decision Making Tool Skill | v1.0 | Create `x-ipe-tool-decision-making` SKILL.md with 6-step decision process, multi-problem input, decision log template, and UNRESOLVED handling | None |
| FEATURE-044-B | EPIC-044 | Skill Creator Template Update | v1.0 | Update `x-ipe-meta-skill-creator` task-based template to replace boolean flags with `process_preference.auto_proceed` enum, add mode-aware conditional blocks, remove `require_human_review` output | FEATURE-044-A |
| FEATURE-044-C | EPIC-044 | Batch Update All 22 Task-Based Skills | v1.0 | Update all 22 task-based skill SKILL.md files: replace `auto_proceed` boolean + `require_human_review` with `process_preference.auto_proceed` enum in input/output, add mode-aware conditional blocks | FEATURE-044-A, FEATURE-044-B |
| FEATURE-044-D | EPIC-044 | Workflow Orchestrator Update | v1.0 | Update `x-ipe-workflow-task-execution` with 3-mode routing logic, consolidate all flow-control to single gate, resolve mode from workflow JSON/CLI flags, handle multi-next-step routing via decision skill | FEATURE-044-A |
| FEATURE-044-E | EPIC-044 | Workflow Template & Backend API | v1.0 | Add `global.process_preference.auto_proceed` to workflow-template.json and runtime workflow JSON, create backend PATCH endpoint for settings update, persist across restarts | FEATURE-044-D |
| FEATURE-044-F | EPIC-044 | Workflow UI Toggle | v1.0 | Add execution mode dropdown to workflow panel header (manual/auto/stop_for_question), wire to backend PATCH API, reflect current state on load | FEATURE-044-E |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| N/A | — | No mockups (config/skill changes, no visual UI except FEATURE-044-F toggle) |

---

## Feature Details

### FEATURE-044-A: Decision Making Tool Skill

**Version:** v1.0
**Priority:** P0 (MVP — Foundation)
**Brief Description:** Create the `x-ipe-tool-decision-making` tool skill that AI agents invoke to autonomously resolve questions, conflicts, and routing decisions. Includes the decision log template (`decision_made_by_ai.md`).

**Acceptance Criteria:**
- [ ] AC-044-A.1: `x-ipe-tool-decision-making` SKILL.md exists at `.github/skills/x-ipe-tool-decision-making/SKILL.md` with valid tool-skill structure
- [ ] AC-044-A.2: Skill accepts `decision_context` input with `calling_skill`, `task_id`, `feature_id` (optional), `workflow_name`, and `problems` array
- [ ] AC-044-A.3: Each problem in `problems` has `problem_id`, `description`, `type` (question|conflict|routing), `options` (optional), `related_files` (optional)
- [ ] AC-044-A.4: Skill executes 6-step process: identify, study docs, web search (optional), sub-agent critique, refine, record
- [ ] AC-044-A.5: Skill returns structured response per problem: `{ problem_id, status: "resolved|unresolved", decision, rationale }`
- [ ] AC-044-A.6: Unresolvable problems logged as UNRESOLVED in `decision_made_by_ai.md`, execution continues
- [ ] AC-044-A.7: Decision log template exists at `.github/skills/x-ipe-tool-decision-making/templates/decision-log-template.md`
- [ ] AC-044-A.8: Template includes Decision Registry table (columns: #, Date, Task ID, Feature ID, Skill, Workflow, Problem Type, Status, Section link)
- [ ] AC-044-A.9: Template includes detail section structure with metadata, problem description, analysis, decision, rationale, follow-up
- [ ] AC-044-A.10: Decision IDs (D-001, D-002, ...) are globally unique per project (auto-incremented from existing registry)
- [ ] AC-044-A.11: Skill passes `x-ipe-meta-skill-creator` validation for tool-skill type

**Dependencies:**
- None (MVP — no prior features required)

**Technical Considerations:**
- Tool skill type — no task board entry, invoked inline by other skills
- Single shared `x-ipe-docs/decision_made_by_ai.md` per project
- Multi-agent atomicity: each agent appends; registry table + detail sections
- Web search step is optional and context-dependent (skip for project-specific)

**Relevant FRs:** FR-044.11–FR-044.16 (Decision Making Tool Skill), FR-044.17–FR-044.22 (Decision Audit Log)
**Relevant ACs:** AC-044.3, AC-044.4, AC-044.16

---

### FEATURE-044-B: Skill Creator Template Update

**Version:** v1.0
**Priority:** P1
**Brief Description:** Update the `x-ipe-meta-skill-creator` task-based template so all future skills are generated with `process_preference.auto_proceed` enum instead of boolean flags, and include mode-aware conditional block patterns.

**Acceptance Criteria:**
- [ ] AC-044-B.1: Task-based template input section includes `process_preference.auto_proceed: "manual | auto | stop_for_question"` with default `manual`
- [ ] AC-044-B.2: Task-based template does NOT contain `auto_proceed: false` (boolean) in input
- [ ] AC-044-B.3: Task-based template Output Result does NOT contain `require_human_review: yes`
- [ ] AC-044-B.4: Task-based template Output Result includes `process_preference.auto_proceed: "{from input}"` pass-through
- [ ] AC-044-B.5: Task-based template Execution Procedure includes a mode-aware conditional block pattern for human-review steps
- [ ] AC-044-B.6: Mode-aware block pattern shows: `IF auto → skip review / call decision_making_skill`, `IF manual|stop_for_question → ask human`
- [ ] AC-044-B.7: Updated template passes `x-ipe-meta-skill-creator` self-validation

**Dependencies:**
- FEATURE-044-A (decision making skill must exist for template to reference it)

**Technical Considerations:**
- Template at `.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-task-based.md`
- Must also update skill-creator's own documentation to describe the new field
- Backward-compatible: `manual` default preserves existing behavior

**Relevant FRs:** FR-044.35–FR-044.37 (Skill Creator Template)
**Relevant ACs:** AC-044.11, AC-044.18

---

### FEATURE-044-C: Batch Update All 22 Task-Based Skills

**Version:** v1.0
**Priority:** P1
**Brief Description:** Update all 22 existing task-based skill SKILL.md files to replace `auto_proceed` (boolean) + `require_human_review` (boolean) with `process_preference.auto_proceed` enum in both input and output sections, and add mode-aware conditional blocks at human-review steps.

**Acceptance Criteria:**
- [ ] AC-044-C.1: All 22 task-based skill SKILL.md files have `process_preference.auto_proceed: "manual | auto | stop_for_question"` in Input Parameters
- [ ] AC-044-C.2: No skill SKILL.md contains `auto_proceed: false` (boolean) in Input Parameters
- [ ] AC-044-C.3: No skill SKILL.md contains `require_human_review: yes` in Output Result YAML
- [ ] AC-044-C.4: All skill Output Result YAML blocks include `process_preference.auto_proceed: "{from input}"` pass-through
- [ ] AC-044-C.5: All skills with human-review steps in Execution Procedure include mode-aware conditional blocks
- [ ] AC-044-C.6: Mode-aware blocks reference `x-ipe-tool-decision-making` for `auto` mode
- [ ] AC-044-C.7: All 22 updated SKILL.md files pass `x-ipe-meta-skill-creator` structural validation
- [ ] AC-044-C.8: `manual` mode behavior in each skill is identical to pre-update behavior (backward compatible)

**Dependencies:**
- FEATURE-044-A (decision making skill must exist to reference)
- FEATURE-044-B (template updated first to establish the pattern)

**Technical Considerations:**
- All 22 task-based skills listed in `.github/skills/x-ipe-task-based-*/SKILL.md`
- Each skill has slightly different human-review points (some at completion, some mid-procedure)
- Batch operation — scripted or systematic update to minimize inconsistency
- Test: verify each updated skill against template structure

**Relevant FRs:** FR-044.1–FR-044.10 (Process Preference Input + Mode-Aware Execution)
**Relevant ACs:** AC-044.1, AC-044.2, AC-044.13, AC-044.14, AC-044.15, AC-044.18

---

### FEATURE-044-D: Workflow Orchestrator Update

**Version:** v1.0
**Priority:** P0 (MVP — Core Routing)
**Brief Description:** Update `x-ipe-workflow-task-execution` to use 3-mode routing logic. Replace boolean `auto_proceed` with `process_preference.auto_proceed` enum. Consolidate all flow-control to a single gate. Resolve mode from workflow JSON (workflow-mode) or CLI flags (free-mode). Invoke decision skill for multi-next-step routing.

**Acceptance Criteria:**
- [ ] AC-044-D.1: Orchestrator Input Parameters replace `auto_proceed: true | false` with `process_preference.auto_proceed: "manual | auto | stop_for_question"`
- [ ] AC-044-D.2: Step 6 (Task Routing) uses 3-mode logic: manual=stop, stop_for_question=auto-proceed, auto=auto-proceed
- [ ] AC-044-D.3: In `auto`/`stop_for_question` modes with multiple `next_actions_suggested`, orchestrator invokes `x-ipe-tool-decision-making` (type: routing)
- [ ] AC-044-D.4: All other flow-control logic (boolean auto_proceed, require_human_review checks) consolidated to single `process_preference.auto_proceed` gate
- [ ] AC-044-D.5: Mode resolved from: (a) `workflow-{name}.json` global section in workflow-mode, (b) CLI flag in free-mode, (c) default `manual`
- [ ] AC-044-D.6: CLI flags `--proceed@auto` and `--proceed@stop-for-question` recognized and mapped
- [ ] AC-044-D.7: `manual` mode produces identical routing behavior to current orchestrator (backward compatible)
- [ ] AC-044-D.8: Orchestrator output includes `process_preference.auto_proceed` for downstream propagation

**Dependencies:**
- FEATURE-044-A (decision making skill must exist for multi-step routing)

**Technical Considerations:**
- `x-ipe-workflow-task-execution` is the central orchestrator — changes here affect all task execution
- Must preserve existing workflow state management (stage gating, feature lanes)
- CLI flag parsing: `--proceed@auto` → `auto`, `--proceed@stop-for-question` → `stop_for_question`
- Resolution priority: explicit CLI flag > workflow JSON > default `manual`

**Relevant FRs:** FR-044.23–FR-044.26 (Workflow Orchestrator), FR-044.38–FR-044.40 (Free-Mode CLI)
**Relevant ACs:** AC-044.9, AC-044.10, AC-044.12, AC-044.13, AC-044.17

---

### FEATURE-044-E: Workflow Template & Backend API

**Version:** v1.0
**Priority:** P2
**Brief Description:** Add `global.process_preference.auto_proceed` field to `workflow-template.json` (both config locations), ensure new workflow instances inherit it, create backend PATCH endpoint for runtime settings update, persist across server restarts.

**Acceptance Criteria:**
- [ ] AC-044-E.1: `x-ipe-docs/config/workflow-template.json` has `global.process_preference.auto_proceed: "manual"` field
- [ ] AC-044-E.2: `src/x_ipe/resources/config/workflow-template.json` has matching `global.process_preference.auto_proceed: "manual"` field
- [ ] AC-044-E.3: New workflow instances (`workflow-{name}.json`) inherit `global.process_preference` from template
- [ ] AC-044-E.4: Backend exposes `PATCH /api/workflow/{name}/settings` endpoint accepting `{ "process_preference": { "auto_proceed": "manual|auto|stop_for_question" } }`
- [ ] AC-044-E.5: PATCH endpoint validates `auto_proceed` value against allowed enum values
- [ ] AC-044-E.6: Updated `workflow-{name}.json` persists `global.process_preference.auto_proceed` across server restarts
- [ ] AC-044-E.7: GET `/api/workflow/{name}` response includes `global.process_preference` section

**Dependencies:**
- FEATURE-044-D (orchestrator must read the new field)

**Technical Considerations:**
- Two template locations: `x-ipe-docs/config/` (user-facing) and `src/x_ipe/resources/config/` (bundled)
- Backend API in Python (Flask) — add route to existing workflow blueprint
- File-based persistence (JSON read/write) — no database needed
- Validation: reject unknown enum values, return 400

**Relevant FRs:** FR-044.27–FR-044.30 (Workflow Template & Runtime)
**Relevant ACs:** AC-044.5, AC-044.6, AC-044.7

---

### FEATURE-044-F: Workflow UI Toggle

**Version:** v1.0
**Priority:** P2
**Brief Description:** Add execution mode dropdown/toggle to the workflow panel header. Options: Manual, Auto, Stop for Question. Calls backend PATCH API on change. Reflects current value from workflow JSON on load. Workflow-global (applies to all features).

**Acceptance Criteria:**
- [ ] AC-044-F.1: Workflow panel header displays "Execution Mode" dropdown with 3 options: Manual, Auto, Stop for Question
- [ ] AC-044-F.2: Changing the dropdown calls `PATCH /api/workflow/{name}/settings` with new auto_proceed value
- [ ] AC-044-F.3: Toggle state reflects current value from `workflow-{name}.json` on page load
- [ ] AC-044-F.4: Toggle is workflow-global (single toggle, applies to all features)
- [ ] AC-044-F.5: Optimistic update — UI updates immediately, reverts on API error
- [ ] AC-044-F.6: Dropdown uses consistent styling with existing workflow panel controls

**Dependencies:**
- FEATURE-044-E (backend API must exist)

**Technical Considerations:**
- Frontend: JavaScript component in existing workflow panel
- Uses fetch() to call PATCH endpoint
- Error handling: show toast/notification on API failure, revert selection
- Default label mapping: `manual` → "Manual", `auto` → "Auto", `stop_for_question` → "Stop for Question"

**Relevant FRs:** FR-044.31–FR-044.34 (Workflow UI Toggle)
**Relevant ACs:** AC-044.8
