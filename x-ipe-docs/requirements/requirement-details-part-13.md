# Requirement Summary

## EPIC-041: CR-Optimize Feature Implementation Level Actions

### Project Overview

A Change Request to extend the Action Execution Modal to fully support **per-feature workflow actions** — the actions in implement, validation, and feedback stages that operate on individual features. This CR supersedes the unimplemented FEATURE-040-B scope and introduces a more targeted approach using direct per-feature deliverable resolution, feature ID propagation, multi-source input UI, and skill `workflow.action` hardcoding.

> Source: IDEA-028 (CR-Optimize Feature Implementation Level Actions)
> Status: Proposed
> Priority: High
> Predecessor: EPIC-040 (CR-Generalize Action Execution Modal)
> Idea Summary: [idea-summary-v1.md](../ideas/028.%20CR-Optimize%20Feature%20Implementation%20Level%20Actions/refined-idea/idea-summary-v1.md)

### User Request

> for feature refinement, technical design ... all the actions we need the modal window logic similar to refine idea, requirement gathering or feature breakdown, which having an input param section that listing all the input file dependencies. and for the related skills we need also update them to support workflows
>
> — Feedback-20260225-160442

### Clarifications

| # | Question | Answer |
|---|----------|--------|
| 1 | Scope: which per-feature actions? | **All**: feature_refinement, technical_design, implementation, acceptance_testing, change_request (existing) + test_generation, human_playground, feature_closing (new — Phase 5) |
| 2 | Feature ID propagation method? | **Dual**: both `<feature-id>` placeholder in command text AND `--feature-id FEATURE-XXX` flag; skill accepts either |
| 3 | `--action` flag for workflow updates? | **Retired** — each skill has a hardcoded `workflow.action` value matching the action key in workflow JSON |
| 4 | Multi-source input UX? | **One labeled dropdown per input_source** (e.g. "From technical_design:", "From feature_refinement:") — not a single flat list |
| 5 | Auto-suggest rules? | **File pattern matching** — each input_source entry has a `file_pattern` (e.g. `specification.md`) to auto-select the best match |
| 6 | Per-feature deliverable API? | Workflow GET API already returns `features[].implement|validation|feedback.actions[*].deliverables[]` — no new endpoints needed |
| 7 | Feature ID flow in skills? | Each skill's Input Initialization parses `--feature-id` from command (not the delegator) |
| 8 | Skill workflow.action updates? | Update all per-feature skills to add hardcoded `workflow.action` matching their action key in workflow JSON |
| 9 | `quality_evaluation`? | **Out of scope** — exists in workflow template but deferred, `skill: null` |
| 10 | New workflow actions (test_generation, etc.)? | **Phase 5** — requires `workflow_manager_service.py` updates to `_stage_config`, `next_actions_map`, `_deliverable_categories`, and `ACTION_MAP` in `workflow-stage.js` |

### High-Level Requirements

#### HLR-1: Per-Feature Copilot-Prompt Configuration

Every per-feature CLI action MUST have a copilot-prompt.json entry under a `"feature"` section with `input_source` and `file_pattern` fields.

**Functional Requirements:**

- **FR-041.1:** Add a new `"feature"` section to copilot-prompt.json with a `"prompts"` array (matches existing schema pattern so `_getConfigEntry()` finds entries automatically).
- **FR-041.2:** Add prompt entries for 5 existing per-feature actions: `feature-refinement`, `technical-design`, `implementation`, `acceptance-testing`, `change-request`.
- **FR-041.3:** Each entry MUST include: `id`, `icon`, `input_source` (array of source action keys), `prompt-details` (with `language`, `label`, `command`).
- **FR-041.4:** Each `input_source` entry MAY include a `file_pattern` field (string, glob-style) for auto-suggest pre-selection.
- **FR-041.5:** Command templates MUST use `<input-file>` and `<feature-id>` placeholders (NOT `<current-idea-file>`).
- **FR-041.6:** The `change-request` entry MUST NOT have `input_source` (uses manual path input — CR can target any stage).
- **FR-041.7:** Add a `<feature-id>` entry to the `"placeholder"` section describing its replacement behavior.

#### HLR-2: Per-Feature Deliverable Resolution

The `_resolveInputFiles()` method MUST support resolving deliverables scoped to a specific feature.

**Functional Requirements:**

- **FR-041.8:** `_resolveInputFiles()` MUST accept an optional `featureId` parameter.
- **FR-041.9:** When `featureId` is provided, the resolver MUST scan `features[featureId].implement|validation|feedback.actions[sourceAction].deliverables` in the workflow state.
- **FR-041.10:** When a source action is NOT found in per-feature stages (e.g. `feature_breakdown` is a shared action), the resolver MUST fall back to scanning shared stages (`shared.requirement.actions[sourceAction].deliverables`).
- **FR-041.11:** The resolver MUST apply `file_pattern` matching from the copilot-prompt config to auto-suggest the best file per source.
- **FR-041.12:** Auto-suggested files MUST be pre-selected in the dropdown with a visual indicator (✨ auto).
- **FR-041.13:** When no deliverables are found for a source, that source's dropdown MUST show a manual file path input as fallback.

#### HLR-3: Multi-Source Input UI

The modal MUST render one labeled dropdown per `input_source` entry for multi-source actions.

**Functional Requirements:**

- **FR-041.14:** When an action's `input_source` has multiple entries, the modal MUST render a separate labeled dropdown for each source (e.g. "From technical_design:", "From feature_refinement:").
- **FR-041.15:** Each dropdown MUST list deliverables from that specific source action only.
- **FR-041.16:** When the user changes any dropdown selection, the command in the instructions section MUST update to reflect all selected files.
- **FR-041.17:** The command template MUST support multiple `<input-file>` replacements — the first `<input-file>` is replaced with the primary source, additional files are appended to the command.
- **FR-041.18:** The modal title MUST include the feature ID when present (e.g. "Technical Design — FEATURE-001").

#### HLR-4: Feature ID Propagation

The feature ID MUST flow from the Feature Lane UI through the modal to the CLI command.

**Functional Requirements:**

- **FR-041.19:** `_dispatchFeatureAction()` in workflow-stage.js MUST pass `featureId` through `_dispatchCliAction()` to the ActionExecutionModal constructor.
- **FR-041.20:** `_dispatchCliAction()` MUST accept a `featureId` parameter and forward it to the modal.
- **FR-041.21:** The ActionExecutionModal constructor MUST accept and store a `featureId` property.
- **FR-041.22:** `_loadInstructions()` MUST replace `<feature-id>` placeholder in command templates with the actual feature ID.
- **FR-041.23:** `_buildCommand()` MUST inject `--feature-id {featureId}` flag into the command string when `featureId` is present.
- **FR-041.24:** `_resolveInputFiles()` MUST receive `featureId` from the modal instance to scope deliverable resolution.

#### HLR-5: Skill Workflow Action Hardcoding

All per-feature skills MUST have hardcoded `workflow.action` values and handle `feature_id` input.

**Functional Requirements:**

- **FR-041.25:** 5 existing-action skills MUST add `workflow.action: "{action_key}"` to their Input Parameters matching the workflow JSON action key:
  - `x-ipe-task-based-feature-refinement` → `"feature_refinement"`
  - `x-ipe-task-based-technical-design` → `"technical_design"`
  - `x-ipe-task-based-code-implementation` → `"implementation"`
  - `x-ipe-task-based-feature-acceptance-test` → `"acceptance_testing"`
  - `x-ipe-task-based-change-request` → `"change_request"`
- **FR-041.26:** Each skill MUST add `feature_id` to Input Parameters with initialization steps: parse from `--feature-id` flag → extract from command text → default `"N/A"`.
- **FR-041.27:** Each skill's completion step MUST pass `feature_id` to the `update_workflow_action` MCP tool call (alongside `workflow_name`, `action`, `status`, `deliverables`).
- **FR-041.28:** Skills MUST treat `feature_id: "N/A"` as free-mode (no per-feature workflow update).

#### HLR-6: New Workflow Actions (Deferred to Phase 5)

Three new action keys MUST be added to the workflow template and frontend.

**Functional Requirements:**

- **FR-041.29:** Add `test_generation` to the `implement` stage in `workflow_manager_service.py` (`_stage_config`, `next_actions_map`, `_deliverable_categories`).
- **FR-041.30:** Add `human_playground` and `feature_closing` to the `feedback` stage.
- **FR-041.31:** Add corresponding entries to `ACTION_MAP` in `workflow-stage.js` with skill references.
- **FR-041.32:** Add copilot-prompt.json entries for the 3 new actions.
- **FR-041.33:** Update the 3 corresponding skills with `workflow.action` and `feature_id` handling.

### Non-Functional Requirements

- **NFR-041.1:** Per-feature deliverable resolution MUST reuse the existing GET `/api/workflow/{name}` response — no additional API calls.
- **NFR-041.2:** Existing shared-level actions (refine_idea, requirement_gathering, feature_breakdown) MUST continue working without regression.
- **NFR-041.3:** The `file_pattern` field MUST be backward-compatible — config loaders that don't know about it silently ignore it.
- **NFR-041.4:** File pattern matching MUST use simple glob rules executable in browser JS (exact match, `*` wildcard).
- **NFR-041.5:** The `"feature"` section in copilot-prompt.json MUST follow the `{prompts: [...]}` schema pattern.

### Acceptance Criteria

- [ ] AC-041.1: Clicking "Feature Refinement" for FEATURE-XXX opens modal with auto-resolved files from `feature_breakdown` deliverables (cross-stage fallback to shared)
- [ ] AC-041.2: Clicking "Technical Design" for FEATURE-XXX opens modal with auto-resolved `specification.md` from that feature's `feature_refinement` deliverables
- [ ] AC-041.3: Clicking "Implementation" for FEATURE-XXX opens modal with multi-source dropdowns: technical-design.md from `technical_design` + specification.md from `feature_refinement`
- [ ] AC-041.4: Clicking "Acceptance Testing" for FEATURE-XXX opens modal with auto-resolved files from `implementation` deliverables
- [ ] AC-041.5: Clicking "Change Request" opens modal with manual file path input (no auto-resolution)
- [ ] AC-041.6: All per-feature action modals show `--feature-id FEATURE-XXX` in the command
- [ ] AC-041.7: Modal title includes feature ID (e.g. "Technical Design — FEATURE-001")
- [ ] AC-041.8: Auto-suggested files show ✨ indicator in dropdown
- [ ] AC-041.9: Multi-source dropdowns update the command when selection changes
- [ ] AC-041.10: All 5 skills have hardcoded `workflow.action` values
- [ ] AC-041.11: Skills pass `feature_id` to `update_workflow_action` on completion
- [ ] AC-041.12: Existing shared-level actions work without regression
- [ ] AC-041.13: copilot-prompt.json has `"feature"` section with 5 action entries
- [ ] AC-041.14: `<feature-id>` placeholder documented in `"placeholder"` section

### Constraints

- **C-1:** Must reuse existing `ActionExecutionModal` class — extend, don't rewrite
- **C-2:** Must maintain backward compatibility with existing copilot-prompt.json schema
- **C-3:** `quality_evaluation` is out of scope (deferred, `skill: null`)
- **C-4:** Phase 5 (new workflow actions) requires `workflow_manager_service.py` changes to `_stage_config`, `next_actions_map`, `_deliverable_categories` + `ACTION_MAP` in `workflow-stage.js`
- **C-5:** Skill updates are SKILL.md file edits, not application code changes

### Related Features (CR Impact)

| Feature | Overlap Type | Decision |
|---------|-------------|----------|
| FEATURE-040-A (Modal Generalization & Core Actions) | Foundation — this CR extends it | Reference only (already implemented) |
| FEATURE-040-B (Workflow Config & Remaining Actions) | **Superseded** — EPIC-041 replaces this unimplemented feature with a per-feature-aware approach | Supersede — FEATURE-040-B should be marked as superseded by EPIC-041 |
| FEATURE-040-C (Skill Workflow-Mode Compliance) | Partial overlap — EPIC-040 planned general workflow-mode, EPIC-041 adds `workflow.action` hardcoding + `feature_id` | Extend — EPIC-041 adds specifics beyond FEATURE-040-C scope |

### Open Questions

- None (all resolved during ideation and clarification)

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| N/A (extends existing modal pattern — multi-source UI is text-based enhancement) | - |

---

## Feature List (EPIC-041)

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|--------------------|
| FEATURE-041-A | EPIC-041 | Per-Feature Config & Core Resolution (MVP) | v1.0 | Add `"feature"` copilot-prompt section, feature ID propagation through modal/command, basic per-feature deliverable resolution with cross-stage fallback | None |
| FEATURE-041-B | EPIC-041 | Multi-Source UI & Auto-Suggest | v1.0 | Multi-dropdown UI per input_source entry, file_pattern auto-suggest with ✨ indicator, command updates on selection change | FEATURE-041-A |
| FEATURE-041-C | EPIC-041 | Skill Workflow Action Updates | v1.0 | Add hardcoded `workflow.action` and `feature_id` handling to 5 per-feature skills (SKILL.md edits only) | None |
| FEATURE-041-D | EPIC-041 | New Workflow Actions (Phase 5) | v1.0 | Add test_generation, human_playground, feature_closing to workflow template, ACTION_MAP, copilot-prompt, and skills (deferred) | FEATURE-041-A, FEATURE-041-C |

---

## Feature Details (EPIC-041)

### FEATURE-041-A: Per-Feature Config & Core Resolution (MVP)

**Summary:** The minimum viable change to enable per-feature actions in the Action Execution Modal. Adds the copilot-prompt configuration, wires feature ID from the Feature Lane UI through to the CLI command, and implements basic per-feature deliverable resolution with cross-stage fallback.

**Scope:**
- Add `"feature"` section to copilot-prompt.json with 5 action entries + `<feature-id>` placeholder doc
- Wire `featureId` through `_dispatchFeatureAction()` → `_dispatchCliAction()` → ActionExecutionModal constructor
- `_loadInstructions()` replaces `<feature-id>` placeholder; `_buildCommand()` injects `--feature-id` flag
- `_resolveInputFiles(actionKey, featureId)` scans per-feature stages first, falls back to shared stages
- Manual path fallback when no deliverables found
- Change-request entry has no `input_source` (manual input only)

**Covered FRs:** FR-041.1, FR-041.2, FR-041.3, FR-041.4, FR-041.5, FR-041.6, FR-041.7, FR-041.8, FR-041.9, FR-041.10, FR-041.13, FR-041.19, FR-041.20, FR-041.21, FR-041.22, FR-041.23, FR-041.24

**Acceptance Criteria:**
- [ ] AC-041.1: Clicking "Feature Refinement" for FEATURE-XXX opens modal with auto-resolved files from `feature_breakdown` deliverables (cross-stage fallback to shared)
- [ ] AC-041.5: Clicking "Change Request" opens modal with manual file path input (no auto-resolution)
- [ ] AC-041.6: All per-feature action modals show `--feature-id FEATURE-XXX` in the command
- [ ] AC-041.12: Existing shared-level actions work without regression
- [ ] AC-041.13: copilot-prompt.json has `"feature"` section with 5 action entries
- [ ] AC-041.14: `<feature-id>` placeholder documented in `"placeholder"` section

**Dependencies:** None (MVP — first feature)

**Technical Considerations:**
- `_getConfigEntry()` already searches all sections with `prompts` arrays — new `"feature"` section auto-discovered
- `_resolveInputFiles()` gets `featureId` from `this.featureId` stored in constructor
- Cross-stage fallback: when `features[id].implement.actions[source]` yields nothing, check `shared.requirement.actions[source]`
- `<current-idea-file>` alias retained for backward compat

---

### FEATURE-041-B: Multi-Source UI & Auto-Suggest

**Summary:** Enhance the modal to render one labeled dropdown per `input_source` entry and auto-suggest the best match using `file_pattern` glob matching. This turns the basic resolution from FEATURE-041-A into a polished multi-source UX.

**Scope:**
- Render separate labeled dropdown per `input_source` entry (e.g. "From technical_design:", "From feature_refinement:")
- Each dropdown lists deliverables from that specific source only
- `file_pattern` matching to auto-select best file per source (✨ auto indicator)
- Command updates dynamically when any dropdown selection changes
- Multiple `<input-file>` replacement: first = primary, rest appended
- Modal title includes feature ID when present (e.g. "Technical Design — FEATURE-001")

**Covered FRs:** FR-041.11, FR-041.12, FR-041.14, FR-041.15, FR-041.16, FR-041.17, FR-041.18

**Acceptance Criteria:**
- [ ] AC-041.2: Clicking "Technical Design" for FEATURE-XXX opens modal with auto-resolved `specification.md` from that feature's `feature_refinement` deliverables
- [ ] AC-041.3: Clicking "Implementation" for FEATURE-XXX opens modal with multi-source dropdowns: technical-design.md from `technical_design` + specification.md from `feature_refinement`
- [ ] AC-041.4: Clicking "Acceptance Testing" for FEATURE-XXX opens modal with auto-resolved files from `implementation` deliverables
- [ ] AC-041.7: Modal title includes feature ID (e.g. "Technical Design — FEATURE-001")
- [ ] AC-041.8: Auto-suggested files show ✨ indicator in dropdown
- [ ] AC-041.9: Multi-source dropdowns update the command when selection changes

**Dependencies:** FEATURE-041-A (requires per-feature config + resolution infrastructure)

**Technical Considerations:**
- `file_pattern` uses simple glob: exact match or `*` wildcard — implemented in browser JS
- Multiple `<input-file>` replacement strategy: scan command for all `<input-file>` occurrences, replace sequentially
- If more sources than placeholders, append remaining files as additional `--input-file` flags
- NFR-041.4: glob matching must be simple enough for browser JS (no external lib)

---

### FEATURE-041-C: Skill Workflow Action Updates

**Summary:** Update 5 per-feature skills to add hardcoded `workflow.action` values and `feature_id` handling. Pure SKILL.md documentation changes — no application code.

**Scope:**
- Add `workflow.action: "{action_key}"` to Input Parameters of each skill:
  - `x-ipe-task-based-feature-refinement` → `"feature_refinement"`
  - `x-ipe-task-based-technical-design` → `"technical_design"`
  - `x-ipe-task-based-code-implementation` → `"implementation"`
  - `x-ipe-task-based-feature-acceptance-test` → `"acceptance_testing"`
  - `x-ipe-task-based-change-request` → `"change_request"`
- Add `feature_id` to Input Parameters with initialization: parse `--feature-id` flag → extract from command → default `"N/A"`
- Update completion step to pass `feature_id` to `update_workflow_action` MCP tool
- Add `feature_id: "N/A"` guard (free-mode = no per-feature update)

**Covered FRs:** FR-041.25, FR-041.26, FR-041.27, FR-041.28

**Acceptance Criteria:**
- [ ] AC-041.10: All 5 skills have hardcoded `workflow.action` values
- [ ] AC-041.11: Skills pass `feature_id` to `update_workflow_action` on completion

**Dependencies:** None (skill doc changes are independent)

**Technical Considerations:**
- Reference pattern: `x-ipe-task-based-requirement-gathering` already has `workflow.action: "requirement_gathering"` and `x-ipe-task-based-feature-breakdown` has `workflow.action: "feature_breakdown"`
- Each skill update is a SKILL.md edit — can be done in parallel
- C-5 constraint: these are documentation changes, not code changes

---

### FEATURE-041-D: New Workflow Actions (Phase 5)

**Summary:** Add 3 missing action keys (test_generation, human_playground, feature_closing) to the workflow engine backend, frontend ACTION_MAP, copilot-prompt config, and corresponding skills. **Deferred — constrained by C-4.**

**Scope:**
- Add `test_generation` to `implement` stage in `workflow_manager_service.py` (`_stage_config`, `next_actions_map`, `_deliverable_categories`)
- Add `human_playground` and `feature_closing` to `feedback` stage
- Add entries to `ACTION_MAP` in `workflow-stage.js` with skill references
- Add copilot-prompt.json entries for all 3 actions
- Update `x-ipe-task-based-test-generation`, `x-ipe-task-based-human-playground`, `x-ipe-task-based-feature-closing` with `workflow.action` + `feature_id`

**Covered FRs:** FR-041.29, FR-041.30, FR-041.31, FR-041.32, FR-041.33

**Acceptance Criteria:**
- (Deferred — no dedicated ACs; constrained by C-4 requiring backend changes)

**Dependencies:** FEATURE-041-A (config infrastructure), FEATURE-041-C (skill update pattern)

**Technical Considerations:**
- Requires backend Python changes (`workflow_manager_service.py`) unlike other features
- `_stage_config` defines action keys per stage; `next_actions_map` defines transitions; `_deliverable_categories` maps actions to deliverable storage
- `ACTION_MAP` in `workflow-stage.js` maps action keys to `{label, icon, skill}` for frontend rendering
- These 3 actions currently exist only in `app_agent_interaction.py` docstrings — not in actual config

---

## CR-002: Action Context System (EPIC-041)

> Source: IDEA-029 (CR-Optimize Feature Implementation Part 2)
> Status: Proposed
> Priority: High
> Predecessor: EPIC-041 (CR-Optimize Feature Implementation Level Actions)
> Idea Summary: [idea-summary-v1.md](../ideas/029.%20CR-Optimize%20Feature%20Implementation-Part%202/refined-idea/idea-summary-v1.md)

### CR Overview

A Change Request to extend EPIC-041's workflow system with an **Action Context** mechanism. This replaces the simple `deliverable_category` string with a rich deliverable tagging system (`$output:name`, `$output-folder:name`) in `workflow-template.json`, adds per-action `action_context` definitions declaring what inputs each action needs, records user selections in the workflow instance JSON for reopen persistence, and updates skills to receive explicit context file paths via `extra_context_reference`.

### User Request

> since for the implementation, as we mentioned in the idea, it should accept multi input files for different prior actions [...] let's rename input files to action context [...] for the action context we should able to auto detect them via workflow-template.json [...] skills should base on these to input extra context
>
> — IDEA-029 (new idea.md)

### Clarifications

| # | Question | Answer |
|---|----------|--------|
| 1 | Dropdown content for `candidates` referencing `$output-folder` | List the specific `$output` file PLUS all files within the `$output-folder` |
| 2 | Auto-detect behavior | Agent AI discovers context within the project autonomously — no explicit file path provided |
| 3 | Old `deliverable_category` migration | All actions must use new `$output:name` / `$output-folder:name` syntax — no backward compat with old format |
| 4 | Context display in action panels | No — context is only shown/edited in the modal, not in the workflow stage view |
| 5 | Scope of `action_context` | ALL actions across ALL stages including per-feature (implement, validation, feedback) |
| 6 | Feature-level action reopen | Yes — feature-level actions have context and support reopen with previous selections |
| 7 | Skill `extra_context_reference` behavior | Skills receive explicit file paths as direct input (not hints), with existing/new steps to use them |
| 8 | Template vs instance separation | `action_context` schema in template; resolved `context` values in instance |
| 9 | `$output:name` cardinality | Always exactly ONE file path; multi-file outputs use `$output-folder:name` |

### High-Level Requirements

#### HLR-CR2.1: Deliverable Tagging System

Replace `deliverable_category` with tagged `deliverables` array in `workflow-template.json`.

**Functional Requirements:**

- **FR-CR2.1:** Replace `deliverable_category: "string"` with `deliverables: ["$output:name", "$output-folder:name"]` array in every action across ALL stages of `workflow-template.json`.
- **FR-CR2.2:** `$output:name` tags MUST resolve to exactly one file path. `$output-folder:name` tags MUST resolve to one folder path.
- **FR-CR2.3:** Tag names MUST be unique within each stage (cross-stage duplicates allowed since stage precedence applies).
- **FR-CR2.4:** Workflow instance `deliverables` MUST change from `string[]` to `{ tagName: path }` object format.
- **FR-CR2.5:** The `update_workflow_action` MCP tool MUST accept BOTH list (legacy) and keyed-object (new) formats — if a list is provided, convert using template tags as keys in order.
- **FR-CR2.6:** Add `"schema_version": "3.0"` to workflow instance JSON for instances using the keyed deliverables format.

#### HLR-CR2.2: Action Context Schema

Add `action_context` definition block per action in `workflow-template.json`.

**Functional Requirements:**

- **FR-CR2.7:** Add an `action_context` object to each action (except first-in-chain actions like `compose_idea` that have no prior context).
- **FR-CR2.8:** Each context entry has: `required` (boolean) and optional `candidates` (string referencing a `$output-folder:name` from prior actions).
- **FR-CR2.9:** When `candidates` is specified, resolve by walking `stage_order` from first to current stage, collecting matching `$output-folder` deliverables. Later-stage takes precedence over earlier-stage.
- **FR-CR2.10:** Per-feature scoping: when resolving within a `per_feature` stage, search current feature's deliverables first, fall back to shared-stage deliverables.
- **FR-CR2.11:** Static validation at template load: every `candidates` value MUST reference an existing `$output-folder:name` from a prior action in stage_order.
- **FR-CR2.12:** Runtime validation at action completion: every key in template `deliverables` array MUST have a corresponding key in instance `deliverables` object.

#### HLR-CR2.3: Action Context Modal UI

Render context dropdowns in the Action Execution Modal driven by `action_context` from the template.

**Functional Requirements:**

- **FR-CR2.13:** Rename "Input Files" section to "Action Context" in the modal UI.
- **FR-CR2.14:** Render one labeled dropdown per `action_context` entry, using the context ref name as subtitle.
- **FR-CR2.15:** Dropdown options: specific `$output` file from the producing action + all files within the `$output-folder` path. All file types listed (not just `.md`).
- **FR-CR2.16:** Every dropdown MUST include an "auto-detect" option — meaning no explicit path is provided to the AI agent.
- **FR-CR2.17:** `required: true` entries MUST have a value selected (or auto-detect). `required: false` entries allow N/A.
- **FR-CR2.18:** When reopening an action (shared or per-feature), pre-populate dropdowns from the instance `context` field.
- **FR-CR2.19:** If `action_context` is present in template → use it exclusively. If absent → fall back to legacy `input_source` from `copilot-prompt.json`.

#### HLR-CR2.4: Workflow Instance Context Persistence

Record user context selections in the workflow instance JSON.

**Functional Requirements:**

- **FR-CR2.20:** Add a `context` field to each action in the workflow instance JSON: `{ refName: path | "N/A" | "auto-detect" }`.
- **FR-CR2.21:** When executing an action, save the user's dropdown selections to the `context` field before launching the CLI command.
- **FR-CR2.22:** When reopening an action, read `context` to restore previous selections in the modal.
- **FR-CR2.23:** `"auto-detect"` persists in `context` until explicitly changed by the user.
- **FR-CR2.24:** Feature-level actions store `context` within their feature lane: `features[id].implement.{action}.context`.
- **FR-CR2.25:** Reopen state: status remains `done` until re-execution starts (→ `in_progress`). Old deliverables preserved until new execution overwrites. No automatic downstream cascade.

#### HLR-CR2.5: Skill Extra Context Reference

Skills receive explicit context file paths in workflow mode.

**Functional Requirements:**

- **FR-CR2.26:** Add `extra_context_reference` to the skill `workflow` input block: `{ refName: path | "N/A" | "auto-detect" }`.
- **FR-CR2.27:** In workflow mode, the skill reads `extra_context_reference` from the workflow instance's `context` field for its action.
- **FR-CR2.28:** When `extra_context_reference[ref]` is a file path → skill uses it as direct input.
- **FR-CR2.29:** When `extra_context_reference[ref]` is `"N/A"` → skill skips that context input.
- **FR-CR2.30:** When `extra_context_reference[ref]` is `"auto-detect"` → skill uses its own discovery logic.
- **FR-CR2.31:** `copilot-prompt.json` `input_source` is deprecated when `action_context` is present. After full migration → remove `input_source`.

### Non-Functional Requirements

- **NFR-CR2.1:** Existing workflow instances with `deliverables: []` arrays MUST continue to work (duck-typed migration).
- **NFR-CR2.2:** Template validation (FR-CR2.11) MUST run at template load time — invalid templates fail fast.
- **NFR-CR2.3:** Dropdown file listing MUST handle large folders (100+ files) — use lazy loading or pagination if needed.
- **NFR-CR2.4:** The `idea_folder` field in workflow instance is NOT subsumed — remains for backward compat.

### Acceptance Criteria

- [ ] AC-CR2.1: All actions in `workflow-template.json` use `$output:name` / `$output-folder:name` syntax (no `deliverable_category`)
- [ ] AC-CR2.2: `action_context` defined for every action with prior dependencies
- [ ] AC-CR2.3: Workflow instance stores `deliverables` as `{ name: path }` and `context` as `{ ref: path | N/A | auto-detect }`
- [ ] AC-CR2.4: Modal "Action Context" renders dropdowns from template schema
- [ ] AC-CR2.5: Dropdowns list `$output` file + `$output-folder` contents
- [ ] AC-CR2.6: Every dropdown includes "auto-detect" option
- [ ] AC-CR2.7: Reopening an action pre-populates dropdowns from instance `context`
- [ ] AC-CR2.8: Feature-level actions support reopen with context restoration
- [ ] AC-CR2.9: Skills receive `extra_context_reference` map with resolved paths
- [ ] AC-CR2.10: Skills handle N/A (skip) and auto-detect (self-discover)
- [ ] AC-CR2.11: Existing instances with `deliverables: []` arrays still work
- [ ] AC-CR2.12: `input_source` used as fallback when `action_context` absent

### Constraints

- **C-CR2.1:** Must extend existing `ActionExecutionModal` class — not rewrite
- **C-CR2.2:** Must support dual deliverable format (list + keyed object) during transition
- **C-CR2.3:** `idea_folder` field preserved for backward compatibility
- **C-CR2.4:** Skill updates are SKILL.md file edits + skill input parameter changes

### CR Impact on Existing Features

| Feature | Impact | Detail |
|---------|--------|--------|
| FEATURE-041-A | **Extended** | `_resolveInputFiles()` replaced by template-driven context resolution; `input_source` fallback added |
| FEATURE-041-B | **Superseded** | Multi-source UI driven by `action_context` dropdowns instead of `input_source` per-dropdown; `file_pattern` auto-suggest subsumed by candidate file listing |
| FEATURE-041-C | **Extended** | Skills gain `extra_context_reference` on top of `workflow.action` + `feature_id` |
| FEATURE-041-D | **Extended** | New actions also need `action_context` definitions in template |

> **⚠️ CR Impact Note** (added 2026-02-26, ref: CR-002)
> - **Change:** Deliverable format changes from `deliverable_category` + array to tagged `$output:name` + keyed object; `action_context` replaces `input_source` for context resolution; skills receive `extra_context_reference`
> - **Affected FRs:** FR-041.1-7 (copilot-prompt input_source → deprecated), FR-041.8-13 (_resolveInputFiles → template-driven), FR-041.14-18 (multi-source UI → action_context dropdowns), FR-041.25-28 (skills gain extra_context_reference)
> - **Action Required:** Feature specifications for FEATURE-041-B, FEATURE-041-C, FEATURE-041-D need updating before implementation

---

## Feature List (CR-002)

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|--------------------|
| FEATURE-041-E | EPIC-041 | Deliverable Tagging & Action Context Schema (MVP) | v1.0 | Replace `deliverable_category` with `$output:name`/`$output-folder:name` tags, add `action_context` to template, keyed deliverables in instance, MCP tool dual-format support | None |
| FEATURE-041-F | EPIC-041 | Action Context Modal UI & Persistence | v1.0 | Rename "Input Files" to "Action Context", render template-driven dropdowns with auto-detect, persist context in instance, support reopen with pre-populated selections | FEATURE-041-E |
| FEATURE-041-G | EPIC-041 | Skill Extra Context Reference | v1.0 | Add `extra_context_reference` to skill workflow input, receive explicit context paths, handle N/A (skip) and auto-detect (self-discover), deprecate `input_source` | None |

---

## Feature Details (CR-002)

### FEATURE-041-E: Deliverable Tagging & Action Context Schema (MVP)

**Summary:** The foundational data model change. Replaces `deliverable_category` strings with tagged `$output:name` / `$output-folder:name` syntax in `workflow-template.json`, adds `action_context` declarations per action, changes workflow instance deliverables from arrays to keyed objects, and updates the MCP tool to accept both formats.

**Scope:**
- Replace `deliverable_category` with `deliverables: ["$output:name", "$output-folder:name"]` in ALL actions of `workflow-template.json`
- Add `action_context` block to every action with prior dependencies (required/optional refs with candidate sources)
- Change workflow instance `deliverables` from `string[]` to `{ tagName: path }` object
- Add `context` field to instance actions: `{ refName: path | "N/A" | "auto-detect" }`
- Update `update_workflow_action` MCP tool to accept both list (legacy) and keyed-object (new) formats
- Add `"schema_version": "3.0"` for instances using new format
- Static validation: `candidates` references must match existing `$output-folder:name` from prior actions
- Runtime validation: instance deliverables keys must match template tags
- Unique tag names within each stage; cross-stage duplicates allowed with stage precedence
- Per-feature scoping: resolve within current feature first, fallback to shared stages

**Covered FRs:** FR-CR2.1, FR-CR2.2, FR-CR2.3, FR-CR2.4, FR-CR2.5, FR-CR2.6, FR-CR2.7, FR-CR2.8, FR-CR2.9, FR-CR2.10, FR-CR2.11, FR-CR2.12, FR-CR2.20

**Acceptance Criteria:**
- [ ] AC-CR2.1: All actions in `workflow-template.json` use `$output:name` / `$output-folder:name` syntax
- [ ] AC-CR2.2: `action_context` defined for every action with prior dependencies
- [ ] AC-CR2.3: Workflow instance stores `deliverables` as `{ name: path }` and `context` as `{ ref: path | N/A | auto-detect }`
- [ ] AC-CR2.11: Existing instances with `deliverables: []` arrays still work

**Dependencies:** None (MVP — foundational)

**Technical Considerations:**
- Backend: `workflow_manager_service.py` deliverables parsing needs duck-typing (list vs dict)
- Backend: `app_agent_interaction.py` `update_workflow_action` needs dual-format support
- Config: `workflow-template.json` full rewrite with tagged deliverables + action_context
- Candidate resolution algorithm: walk `stage_order`, later-stage precedence, per-feature scoping

---

### FEATURE-041-F: Action Context Modal UI & Persistence

**Summary:** Frontend changes to render template-driven context dropdowns in the Action Execution Modal, persist selections in the workflow instance, and support reopening actions with pre-populated context.

**Scope:**
- Rename "Input Files" section to "Action Context" in modal UI
- Read `action_context` from `workflow-template.json` to render one dropdown per context ref
- Populate dropdowns: `$output` file + `$output-folder` contents from prior action deliverables (all file types, not just `.md`)
- Add "auto-detect" option to every dropdown
- Enforce required/optional: `required: true` must have selection or auto-detect; `required: false` allows N/A
- Save context selections to instance `context` field before launching CLI command
- On reopen: read `context` from instance to pre-populate dropdowns
- Feature-level actions store context within feature lane
- Fallback: if `action_context` absent in template → use legacy `input_source` from `copilot-prompt.json`
- Reopen state machine: status → `in_progress`, old deliverables preserved, no downstream cascade

**Covered FRs:** FR-CR2.13, FR-CR2.14, FR-CR2.15, FR-CR2.16, FR-CR2.17, FR-CR2.18, FR-CR2.19, FR-CR2.21, FR-CR2.22, FR-CR2.23, FR-CR2.24, FR-CR2.25

**Acceptance Criteria:**
- [ ] AC-CR2.4: Modal "Action Context" renders dropdowns from template schema
- [ ] AC-CR2.5: Dropdowns list `$output` file + `$output-folder` contents
- [ ] AC-CR2.6: Every dropdown includes "auto-detect" option
- [ ] AC-CR2.7: Reopening an action pre-populates dropdowns from instance `context`
- [ ] AC-CR2.8: Feature-level actions support reopen with context restoration
- [ ] AC-CR2.12: `input_source` used as fallback when `action_context` absent

**Dependencies:** FEATURE-041-E (template schema + instance format must exist first)

**Technical Considerations:**
- `action-execution-modal.js`: replace `_resolveInputFiles()` with template-driven context resolution
- Need API to list files within a folder path (for `$output-folder` contents)
- `workflow-stage.js`: feature-level action reopen support
- NFR-CR2.3: lazy load for large folders (100+ files)

---

### FEATURE-041-G: Skill Extra Context Reference

**Summary:** Update all workflow-aware skills to receive `extra_context_reference` map with explicit context file paths, and deprecate `copilot-prompt.json` `input_source`.

**Scope:**
- Add `extra_context_reference` to skill `workflow` input block
- In workflow mode, skill reads context from workflow instance's `context` field
- File path → use as direct input; "N/A" → skip; "auto-detect" → self-discover
- Update all per-feature skills + shared-level skills with `extra_context_reference` parameter
- Deprecate `input_source` in `copilot-prompt.json` for actions with `action_context`

**Covered FRs:** FR-CR2.26, FR-CR2.27, FR-CR2.28, FR-CR2.29, FR-CR2.30, FR-CR2.31

**Acceptance Criteria:**
- [ ] AC-CR2.9: Skills receive `extra_context_reference` map with resolved paths
- [ ] AC-CR2.10: Skills handle N/A (skip) and auto-detect (self-discover)

**Dependencies:** None (SKILL.md documentation changes are independent of backend/frontend)

**Technical Considerations:**
- Pure SKILL.md file edits (no application code changes)
- Each skill needs existing or new steps to consume context paths
- Backward compat: skills must still work when `extra_context_reference` is not provided (free-mode)
