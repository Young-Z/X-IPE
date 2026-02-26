# Feature Specification: Deliverable Tagging & Action Context Schema (MVP)

> Feature ID: FEATURE-041-E
> Epic ID: EPIC-041
> CR: CR-002
> Version: v1.0
> Status: Refined
> Last Updated: 02-26-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-26-2026 | Initial specification from CR-002 Feature Breakdown |

## Linked Mockups

N/A — This is a backend/config feature. No UI changes.

## Overview

FEATURE-041-E is the foundational data model change for CR-002. It replaces the flat `deliverable_category` string in `workflow-template.json` with a tagged deliverables array (`$output:name`, `$output-folder:name`), adds `action_context` declarations per action in the template, converts workflow instance `deliverables` from arrays to keyed objects, adds a `context` field to instance actions, and updates the `update_workflow_action` MCP tool to accept both legacy list and new keyed-object formats.

**Who:** X-IPE backend developers, MCP tool consumers (AI agents), workflow template maintainers.

**Why:** The current `deliverable_category` field doesn't distinguish individual outputs from folders, can't express inter-action dependencies, and forces ad-hoc resolution logic. Tagged deliverables + action context create a machine-readable dependency graph that downstream features (Modal UI, Skill contract) build upon.

## User Stories

- **US-1:** As a workflow template maintainer, I want each action to declare its outputs with typed tags (`$output:name`, `$output-folder:name`), so downstream actions can reference specific deliverables by name.
- **US-2:** As a workflow template maintainer, I want each action to declare an `action_context` block listing what inputs it needs from prior actions (with required/optional + candidates), so the dependency graph is explicit.
- **US-3:** As an AI agent (MCP tool consumer), I want to pass deliverables as a keyed object `{ tagName: path }` to `update_workflow_action`, so each deliverable is semantically named.
- **US-4:** As an AI agent, I want to also pass deliverables as a legacy list (for backward compat), and have the system convert it to keyed format using template tag order.
- **US-5:** As a workflow system, I want static validation at template load time to ensure all `candidates` references resolve to existing prior-action `$output-folder` names.
- **US-6:** As a workflow system, I want runtime validation at action completion to ensure instance deliverables keys match template tags.

## Acceptance Criteria

- [ ] **AC-1:** All actions in `workflow-template.json` use `deliverables: ["$output:name", "$output-folder:name"]` syntax instead of `deliverable_category: "string"`.
- [ ] **AC-2:** Actions with prior dependencies have an `action_context` object; first-in-chain actions (e.g., `compose_idea`) have no `action_context`.
- [ ] **AC-3:** Workflow instance JSON stores `deliverables` as `{ tagName: path }` object and `context` as `{ refName: path | "N/A" | "auto-detect" }`.
- [ ] **AC-4:** `update_workflow_action` MCP tool accepts keyed-object deliverables and stores them directly.
- [ ] **AC-5:** `update_workflow_action` MCP tool accepts list deliverables (legacy) and converts them to keyed format using the template's tag names in order.
- [ ] **AC-6:** Instances using keyed deliverables have `"schema_version": "3.0"`.
- [ ] **AC-7:** Existing instances with `deliverables: []` arrays continue to work (duck-typed migration).
- [ ] **AC-8:** Static validation at template load: every `action_context.*.candidates` value must reference an existing `$output-folder:name` from a prior action in `stage_order`. Invalid templates fail fast with clear error.
- [ ] **AC-9:** Runtime validation at action completion: every key in template `deliverables` array must have a corresponding key in instance `deliverables` object.
- [ ] **AC-10:** Tag names are unique within each stage. Cross-stage duplicates allowed.
- [ ] **AC-11:** Per-feature scoping: candidate resolution within a `per_feature` stage searches current feature's deliverables first, then falls back to shared-stage deliverables.

## Functional Requirements

### FR-1: Template Deliverable Tagging

- **FR-1.1:** Replace `deliverable_category` with `deliverables` array in every action across ALL stages.
- **FR-1.2:** `$output:name` resolves to exactly ONE file path. `$output-folder:name` resolves to one folder path.
- **FR-1.3:** Tag names MUST be unique within each stage. Cross-stage duplicates are allowed (stage precedence applies during resolution).
- **FR-1.4:** The old `deliverable_category` field MUST be removed from all actions.

### FR-2: Template Action Context Schema

- **FR-2.1:** Add `action_context` object to each action that depends on prior action outputs. Actions with no prior context (e.g., `compose_idea`) have no `action_context`.
- **FR-2.2:** Each `action_context` entry has: `required` (boolean) and optional `candidates` (string referencing a `$output-folder:name` from prior actions).
- **FR-2.3:** `candidates` absent means the context ref matches by name against any prior action's `$output:name` or `$output-folder:name`.

### FR-3: Instance Deliverables Format Change

- **FR-3.1:** Instance `deliverables` changes from `string[]` to `{ tagName: path }` object.
- **FR-3.2:** Instance actions gain a `context` field: `{ refName: path | "N/A" | "auto-detect" }`.
- **FR-3.3:** Add `"schema_version": "3.0"` to instance root for new-format instances.
- **FR-3.4:** `idea_folder` field in instance is NOT removed — remains for backward compatibility.

### FR-4: MCP Tool Dual-Format Support

- **FR-4.1:** `update_workflow_action` MCP tool MUST accept deliverables as keyed object and store directly.
- **FR-4.2:** If deliverables is a list → convert to keyed object using template's `$output:name` tags in order (positional mapping).
- **FR-4.3:** If deliverables is a keyed object but context is missing → set context to `{}` (no context stored).
- **FR-4.4:** The MCP tool's `deliverables` parameter type changes from `list[str]` to `list[str] | dict[str, str]`.

### FR-5: Static Template Validation

- **FR-5.1:** At template load time, parse all `action_context.*.candidates` values.
- **FR-5.2:** For each candidates value, verify a prior action in `stage_order` has a matching `$output-folder:{candidates}` in its deliverables array.
- **FR-5.3:** Verify tag name uniqueness within each stage.
- **FR-5.4:** If validation fails, raise a clear error with the offending action and candidates value.

### FR-6: Runtime Validation

- **FR-6.1:** At action completion, verify every key from the template's `deliverables` array has a matching key in the instance's `deliverables` object.
- **FR-6.2:** If validation fails, log a warning but do not block (graceful degradation for partial deliverables).

### FR-7: Candidate Resolution Algorithm

- **FR-7.1:** Given a `candidates` value (e.g., `"ideas-folder"`):
  1. Walk `stage_order` from first stage to current stage
  2. For each stage, scan all actions' `deliverables` for `$output-folder:{candidates}` or `$output:{candidates}`
  3. Collect ALL matches; later-stage takes precedence over earlier-stage
  4. Within same stage, later action order takes precedence
- **FR-7.2:** Per-feature scoping: within a `per_feature` stage, search current feature's action deliverables first; fall back to shared-stage deliverables if no match.
- **FR-7.3:** Resolve matched deliverable name against workflow instance to get actual file/folder path.

## Non-Functional Requirements

- **NFR-1:** Dual-format detection must be zero-overhead — simple `isinstance(deliverables, list)` check.
- **NFR-2:** Template validation must run once at load time, not per-request.
- **NFR-3:** Runtime validation warnings must not block action execution.
- **NFR-4:** No database schema changes — workflow instances are JSON files.

## UI/UX Requirements

N/A — This feature has no UI changes. UI is handled by FEATURE-041-F.

## Dependencies

### Internal Dependencies

- **FEATURE-041-A** (Testing Complete): This feature builds on the per-feature config foundation. The instance structure with `features[].implement.{action}` was established by 041-A. The new keyed deliverables and context fields extend that structure.

### External Dependencies

None.

## Business Rules

- **BR-1:** A `$output:name` tag ALWAYS resolves to exactly one file path (never a folder, never multiple files).
- **BR-2:** A `$output-folder:name` tag ALWAYS resolves to one folder path.
- **BR-3:** `action_context` is optional per action — it's absent on first-in-chain actions.
- **BR-4:** `candidates` in `action_context` is optional per context ref — when absent, the ref matches by name.
- **BR-5:** `schema_version: "3.0"` is set on first keyed-deliverable write; never downgraded.
- **BR-6:** Legacy list format is automatically converted; no user action required.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Template has action with empty `deliverables: []` | Valid — action produces no deliverables (e.g., quality_evaluation might only produce an eval-report) |
| Instance has extra deliverable keys not in template | Accepted silently — superset is OK |
| Instance is missing a deliverable key from template | Runtime validation logs warning; action still accepted |
| `update_workflow_action` called with empty list `[]` | Convert to `{}` empty object |
| `update_workflow_action` called with list longer than template tags | Extra items ignored with warning |
| `update_workflow_action` called with list shorter than template tags | Missing tags get `null` value |
| Per-feature action references shared-stage deliverable | Resolution falls back to shared stage after checking current feature |
| Cross-stage duplicate tag name (e.g., `feature-docs-folder` in implement and validation) | Allowed — later-stage takes precedence during resolution |
| Same-stage duplicate tag name | Validation error at template load |
| `compose_idea` has `action_context` (shouldn't) | Valid but ignored — no candidates to resolve from |

### Constraints

- **C-1:** Must extend existing `WorkflowManagerService` — not rewrite.
- **C-2:** `idea_folder` field preserved in instance for backward compatibility.
- **C-3:** `copilot-prompt.json` `input_source` NOT removed in this feature — only deprecated. Actual removal happens after FEATURE-041-F confirms fallback works.

## Out of Scope

- Modal UI changes (→ FEATURE-041-F)
- Dropdown rendering, reopen pre-population (→ FEATURE-041-F)
- Skill `extra_context_reference` input parameter (→ FEATURE-041-G)
- `copilot-prompt.json` `input_source` removal (post-migration cleanup)
- Workflow instance file migration script (duck-typing handles it at runtime)

## Technical Considerations

- **Affected backend files:**
  - `src/x_ipe/services/workflow_manager_service.py` — deliverables parsing, dual-format detection, context storage/retrieval, validation logic
  - `src/x_ipe/services/app_agent_interaction.py` — `update_workflow_action` MCP tool parameter type change, conversion logic
  - `src/x_ipe/routes/workflow_routes.py` — pass-through of new deliverable format
- **Affected config:**
  - `x-ipe-docs/config/workflow-template.json` — full rewrite with tagged deliverables + action_context
- **Affected tests:**
  - `tests/test_workflow_manager.py` — new tests for keyed deliverables, context field, validation
  - `tests/test_workflow_feature_lanes.py` — per-feature scoping tests
- **The candidate resolution algorithm (FR-7) is backend-only** — it's a utility function that FEATURE-041-F's UI will call via API

## Open Questions

None — all questions were resolved during IDEA-029 brainstorming (see CR-002 Clarifications table).
