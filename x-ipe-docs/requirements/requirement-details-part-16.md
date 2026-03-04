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

### Feature Candidates (for Feature Breakdown)

| # | Candidate Feature | Scope | Dependencies |
|---|------------------|-------|--------------|
| A | Decision Making Tool Skill | Create `x-ipe-tool-decision-making` SKILL.md with 6-step process, templates, decision log format | None |
| B | Skill Creator Template Update | Update `x-ipe-meta-skill-creator` template: add `process_preference` input, mode-aware blocks, remove `require_human_review` | A |
| C | Update All 22 Task-Based Skills | Batch update all skills: replace booleans with enum, add mode-aware conditional blocks, update output | A, B |
| D | Workflow Orchestrator Update | Update `x-ipe-workflow-task-execution`: 3-mode routing, consolidate flow control, resolve from config/CLI | A |
| E | Workflow Template & Backend | Add `global.process_preference` to template + runtime JSON, backend API for settings update | D |
| F | Workflow UI Toggle | Frontend toggle in workflow panel header, calls backend API | E |
