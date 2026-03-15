# Feature Specification: Deliverable Tagging & Action Context Schema (MVP)

> Feature ID: FEATURE-041-E
> Epic ID: EPIC-041
> CR: CR-002, CR-003
> Version: v2.0
> Status: Refined
> Last Updated: 03-14-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-26-2026 | Initial specification from CR-002 Feature Breakdown |
| v1.1 | 03-14-2026 | [CR-003](x-ipe-docs/requirements/EPIC-041/FEATURE-041-E/CR-003.md): Support array-valued deliverable tags for multi-file outputs |
| v2.0 | 03-14-2026 | Full spec rewrite for CR-003: array-valued tags, GWT acceptance criteria, updated FRs/BRs/edge cases |

## Linked Mockups

N/A — This is a backend/config feature with frontend rendering handled by FEATURE-036-E.

## Overview

FEATURE-041-E is the foundational data model change for CR-002 and CR-003. It replaces the flat `deliverable_category` string in `workflow-template.json` with a tagged deliverables array (`$output:name`, `$output-folder:name`), adds `action_context` declarations per action in the template, converts workflow instance `deliverables` from arrays to keyed objects, adds a `context` field to instance actions, and updates the `update_workflow_action` MCP tool to accept both legacy list and new keyed-object formats.

**CR-003 extension:** All `$output:` tags now support array values (`[path1, path2, ...]`) in addition to single string values. This enables actions like `compose_idea` to list all produced files (e.g., idea markdown + uploaded images) under a single tag. Template token resolution uses the first array element for prompt substitution; consumers discover all files via the tag. The specific rename of `$output:raw-idea` → `$output:raw-ideas` in `compose_idea` is included as part of this change.

**Who:** X-IPE backend developers, MCP tool consumers (AI agents), workflow template maintainers, frontend deliverable renderers.

**Why:** The current `deliverable_category` field doesn't distinguish individual outputs from folders, can't express inter-action dependencies, and forces ad-hoc resolution logic. Tagged deliverables + action context create a machine-readable dependency graph that downstream features (Modal UI, Skill contract) build upon. Array support (CR-003) addresses the limitation where actions producing multiple outputs (e.g., idea file + uploaded PNGs) could only show one file per tag.

## User Stories

- **US-1:** As a workflow template maintainer, I want each action to declare its outputs with typed tags (`$output:name`, `$output-folder:name`), so downstream actions can reference specific deliverables by name.
- **US-2:** As a workflow template maintainer, I want each action to declare an `action_context` block listing what inputs it needs from prior actions (with required/optional + candidates), so the dependency graph is explicit.
- **US-3:** As an AI agent (MCP tool consumer), I want to pass deliverables as a keyed object `{ tagName: path }` to `update_workflow_action`, so each deliverable is semantically named.
- **US-4:** As an AI agent, I want to also pass deliverables as a legacy list (for backward compat), and have the system convert it to keyed format using template tag order.
- **US-5:** As a workflow system, I want static validation at template load time to ensure all `candidates` references resolve to existing prior-action `$output-folder` names.
- **US-6:** As a workflow system, I want runtime validation at action completion to ensure instance deliverables keys match template tags.
- **US-7:** As a workflow template maintainer, I want deliverable tags that support multiple file paths (array values), so actions producing multiple outputs (e.g., idea file + uploaded images) can list all files under one semantic tag.
- **US-8:** As a UI user, I want each file in an array-valued deliverable tag rendered as a separate deliverable card, so I can see and access all outputs individually.
- **US-9:** As an AI agent, when resolving a template token `$output:tag-name$` for an array-valued tag, I want it to resolve to the first element while I can discover all files via the tag, so prompt text stays clean while all outputs remain accessible.

## Acceptance Criteria

### AC-041E-01: Template Tagging Structure

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-041E-01a | GIVEN workflow-template.json is loaded WHEN any action is inspected THEN its `deliverables` field is an array of `$output:name` and/or `$output-folder:name` tags AND no `deliverable_category` field remains | Unit |
| AC-041E-01b | GIVEN an action has no prior dependencies (e.g., `compose_idea`) WHEN it is inspected THEN it has no `action_context` field | Unit |
| AC-041E-01c | GIVEN an action depends on prior outputs WHEN it is inspected THEN it has an `action_context` object listing required/optional refs with candidates | Unit |
| AC-041E-01d | GIVEN the `compose_idea` action in the template WHEN it is inspected THEN its deliverables include `$output:raw-ideas` (plural, renamed from `raw-idea`) AND `$output-folder:ideas-folder` | Unit |

### AC-041E-02: Instance Deliverable Storage

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-041E-02a | GIVEN `update_workflow_action` is called with keyed-object deliverables `{ tagName: "path" }` WHEN the action completes THEN the instance stores deliverables as the keyed object verbatim | Unit |
| AC-041E-02b | GIVEN `update_workflow_action` is called with list deliverables `["path1", "path2"]` WHEN the action completes THEN the instance converts them to a keyed object using the template's tag names in positional order | Unit |
| AC-041E-02c | GIVEN keyed deliverables are written for the first time WHEN the instance is persisted THEN `schema_version` is set to `"3.0"` | Unit |
| AC-041E-02d | GIVEN an existing instance has `deliverables: []` legacy array format WHEN it is read by the system THEN it continues to work without error (duck-typed backward compat) | Unit |
| AC-041E-02e | GIVEN `update_workflow_action` is called with `context` values WHEN the action completes THEN the instance stores `context` as `{ refName: path \| "N/A" \| "auto-detect" }` | Unit |

### AC-041E-03: Array-Valued Deliverable Tags (CR-003)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-041E-03a | GIVEN `update_workflow_action` is called with deliverables `{ tagName: ["path1.md", "path2.png"] }` WHEN the action completes THEN the instance stores the tag value as an array of strings | Unit |
| AC-041E-03b | GIVEN a deliverable tag has a single string value `"path"` WHEN the system processes it internally THEN it is treated as functionally equivalent to a single-element array `["path"]` | Unit |
| AC-041E-03c | GIVEN a deliverable tag has an array value `["idea.md", "img1.png", "img2.png"]` WHEN template token `$output:tag-name$` is resolved in a prompt THEN it resolves to the first element only (`"idea.md"`) | Unit |
| AC-041E-03d | GIVEN a deliverable tag has an array value WHEN the resolve_deliverables API returns results THEN all files in the array are listed as individual deliverable entries | API |
| AC-041E-03e | GIVEN a deliverable tag has an array value WHEN the frontend renders deliverables for that action THEN each file in the array appears as a separate deliverable card | UI |
| AC-041E-03f | GIVEN array-valued deliverables are written to an instance for the first time WHEN the instance is persisted THEN `schema_version` is bumped to `"4.0"` | Unit |
| AC-041E-03g | GIVEN `compose_idea` completes with multiple outputs WHEN deliverables are stored as `{ "raw-ideas": ["new-idea.md", "uploaded1.png", "uploaded2.png"], "ideas-folder": "path/to/folder" }` THEN all three files appear as deliverable cards in the UI | Integration |

### AC-041E-04: Validation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-041E-04a | GIVEN a template is loaded WHEN an `action_context.*.candidates` value references `$output-folder:name` THEN that name must exist in a prior action's deliverables within `stage_order` OR validation fails with a clear error | Unit |
| AC-041E-04b | GIVEN a template is loaded WHEN tag names within a single stage are inspected THEN all tag names are unique OR validation fails with a duplicate-tag error | Unit |
| AC-041E-04c | GIVEN an action completes WHEN instance deliverables keys are checked against template tags THEN every template tag has a corresponding key in the instance (missing keys produce a warning log, not a blocking error) | Unit |
| AC-041E-04d | GIVEN `update_workflow_action` receives deliverables with a tag value that is an array WHEN the array is validated THEN each element must be a non-empty string (empty strings or non-string elements produce a validation error) | Unit |

### AC-041E-05: Scoping & Resolution

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-041E-05a | GIVEN a per-feature action references a deliverable via `candidates` WHEN candidate resolution runs THEN it searches the current feature's deliverables first AND falls back to shared-stage deliverables only if no match found | Integration |
| AC-041E-05b | GIVEN cross-stage duplicate tag names exist (e.g., `feature-docs-folder` in both implement and validation stages) WHEN candidate resolution runs THEN the later-stage tag takes precedence | Unit |
| AC-041E-05c | GIVEN tag names are unique within a stage but duplicated across stages WHEN static validation runs THEN validation passes (cross-stage duplicates are allowed) | Unit |

> **Test Type Legend:**
> - **UI** — Browser/DOM interaction test (clicks, renders, layout)
> - **API** — HTTP request/response test (status codes, response body)
> - **Unit** — Isolated function/module test (parsing, calculations)
> - **Integration** — Multi-component interaction test (service + DB/frontend)

## Functional Requirements

### FR-1: Template Deliverable Tagging

- **FR-1.1:** Replace `deliverable_category` with `deliverables` array in every action across ALL stages.
- **FR-1.2:** `$output:name` resolves to one file path (string) OR an array of file paths (`[string, ...]`). `$output-folder:name` resolves to one folder path (always a string, never an array).
- **FR-1.3:** Tag names MUST be unique within each stage. Cross-stage duplicates are allowed (stage precedence applies during resolution).
- **FR-1.4:** The old `deliverable_category` field MUST be removed from all actions.
- **FR-1.5:** Rename `$output:raw-idea` → `$output:raw-ideas` in `compose_idea` action to reflect multi-file support. Update all `action_context` references that previously pointed to `raw-idea`.

### FR-2: Template Action Context Schema

- **FR-2.1:** Add `action_context` object to each action that depends on prior action outputs. Actions with no prior context (e.g., `compose_idea`) have no `action_context`.
- **FR-2.2:** Each `action_context` entry has: `required` (boolean) and optional `candidates` (string referencing a `$output-folder:name` from prior actions).
- **FR-2.3:** `candidates` absent means the context ref matches by name against any prior action's `$output:name` or `$output-folder:name`.

### FR-3: Instance Deliverables Format Change

- **FR-3.1:** Instance `deliverables` changes from `string[]` to `{ tagName: path | [path1, path2, ...] }` object. Tag values can be a single string path or an array of string paths.
- **FR-3.2:** Instance actions gain a `context` field: `{ refName: path | "N/A" | "auto-detect" }`.
- **FR-3.3:** Add `"schema_version": "3.0"` to instance root for new keyed-format instances. Bump to `"4.0"` when array-valued deliverables are first written.
- **FR-3.4:** `idea_folder` field in instance is NOT removed — remains for backward compatibility.

### FR-4: MCP Tool Dual-Format Support

- **FR-4.1:** `update_workflow_action` MCP tool MUST accept deliverables as keyed object and store directly.
- **FR-4.2:** If deliverables is a list → convert to keyed object using template's `$output:name` tags in order (positional mapping).
- **FR-4.3:** If deliverables is a keyed object but context is missing → set context to `{}` (no context stored).
- **FR-4.4:** The MCP tool's `deliverables` parameter type changes from `list[str]` to `list[str] | dict[str, str | list[str]]`. Tag values accept both single strings and arrays of strings.

### FR-5: Static Template Validation

- **FR-5.1:** At template load time, parse all `action_context.*.candidates` values.
- **FR-5.2:** For each candidates value, verify a prior action in `stage_order` has a matching `$output-folder:{candidates}` in its deliverables array.
- **FR-5.3:** Verify tag name uniqueness within each stage.
- **FR-5.4:** If validation fails, raise a clear error with the offending action and candidates value.

### FR-6: Runtime Validation

- **FR-6.1:** At action completion, verify every key from the template's `deliverables` array has a matching key in the instance's `deliverables` object.
- **FR-6.2:** If validation fails, log a warning but do not block (graceful degradation for partial deliverables).
- **FR-6.3:** When a tag value is an array, validate that every element is a non-empty string. Reject arrays containing empty strings, non-string elements, or nested arrays.

### FR-7: Candidate Resolution Algorithm

- **FR-7.1:** Given a `candidates` value (e.g., `"ideas-folder"`):
  1. Walk `stage_order` from first stage to current stage
  2. For each stage, scan all actions' `deliverables` for `$output-folder:{candidates}` or `$output:{candidates}`
  3. Collect ALL matches; later-stage takes precedence over earlier-stage
  4. Within same stage, later action order takes precedence
- **FR-7.2:** Per-feature scoping: within a `per_feature` stage, search current feature's action deliverables first; fall back to shared-stage deliverables if no match.
- **FR-7.3:** Resolve matched deliverable name against workflow instance to get actual file/folder path. If the value is an array, return all paths.

### FR-8: Array Deliverable Handling (CR-003)

- **FR-8.1:** `update_workflow_action` MUST accept tag values as either a single string or an array of strings. Both formats are valid for any `$output:` tag.
- **FR-8.2:** When template token `$output:tag-name$` is resolved in a prompt and the tag value is an array, resolve to the **first element** only. Consumers needing all files use the tag to look up the full array.
- **FR-8.3:** The `resolve_deliverables` API MUST expand array-valued tags into individual file entries for rendering. Each file in the array becomes a separate deliverable entry with the same tag name.
- **FR-8.4:** String values and single-element arrays are functionally equivalent at the API layer. `"path"` and `["path"]` produce the same result when resolved.
- **FR-8.5:** `$output-folder:name` tags do NOT support array values — they always resolve to exactly one folder path.

## Non-Functional Requirements

- **NFR-1:** Dual-format detection must be zero-overhead — simple `isinstance(deliverables, list)` check for legacy vs keyed; `isinstance(value, list)` for string vs array tag values.
- **NFR-2:** Template validation must run once at load time, not per-request.
- **NFR-3:** Runtime validation warnings must not block action execution.
- **NFR-4:** No database schema changes — workflow instances are JSON files.
- **NFR-5:** Array expansion in `resolve_deliverables` must not degrade performance for actions with single-value tags (no unnecessary list wrapping in hot paths).

## UI/UX Requirements

N/A — This feature defines the data model. UI rendering of array-valued deliverables is handled by FEATURE-036-E (deliverable card rendering) using the expanded entries from FR-8.3.

## Dependencies

### Internal Dependencies

- **FEATURE-041-A** (Testing Complete): This feature builds on the per-feature config foundation. The instance structure with `features[].implement.{action}` was established by 041-A. The new keyed deliverables and context fields extend that structure.
- **FEATURE-036-E** (Deliverable Rendering): The frontend rendering of array-expanded deliverable entries depends on the data model defined here. Changes to `_renderDeliverables` and `_renderDeliverableCard` consume the expanded API output.

### External Dependencies

None.

## Business Rules

- **BR-1:** A `$output:name` tag resolves to one file path (string) OR an array of file paths (array of strings). Both are valid.
- **BR-2:** A `$output-folder:name` tag ALWAYS resolves to one folder path (never an array).
- **BR-3:** `action_context` is optional per action — it's absent on first-in-chain actions.
- **BR-4:** `candidates` in `action_context` is optional per context ref — when absent, the ref matches by name.
- **BR-5:** `schema_version: "3.0"` is set on first keyed-deliverable write; never downgraded. Bumps to `"4.0"` on first array-valued write.
- **BR-6:** Legacy list format is automatically converted; no user action required.
- **BR-7:** For template token resolution (`$output:tag-name$` in prompts), array-valued tags resolve to their first element. Consumers access all files via the tag name through the API.
- **BR-8:** String values and single-element arrays are interchangeable — `"path"` is functionally equivalent to `["path"]`.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Template has action with empty `deliverables: []` | Valid — action produces no deliverables |
| Instance has extra deliverable keys not in template | Accepted silently — superset is OK |
| Instance is missing a deliverable key from template | Runtime validation logs warning; action still accepted |
| `update_workflow_action` called with empty list `[]` | Convert to `{}` empty object |
| `update_workflow_action` called with list longer than template tags | Extra items ignored with warning |
| `update_workflow_action` called with list shorter than template tags | Missing tags get `null` value |
| Per-feature action references shared-stage deliverable | Resolution falls back to shared stage after checking current feature |
| Cross-stage duplicate tag name | Allowed — later-stage takes precedence during resolution |
| Same-stage duplicate tag name | Validation error at template load |
| `compose_idea` has `action_context` (shouldn't) | Valid but ignored — no candidates to resolve from |
| Tag value is an empty array `[]` | Treated as no deliverable for that tag; runtime validation logs warning |
| Tag value is a single-element array `["path"]` | Functionally equivalent to string `"path"` — one deliverable card rendered |
| Tag value is an array with mixed file types `["idea.md", "img.png"]` | All files rendered as individual deliverable cards; first element used for token resolution |
| Dict deliverables with mix of string and array values | Both accepted in same dict — string tags stored as strings, array tags stored as arrays |
| Array element is an empty string `["path", ""]` | Validation error — all array elements must be non-empty strings |
| Array element is not a string `["path", 123]` | Validation error — all array elements must be strings |
| Existing instance with `raw-idea` tag (pre-rename) | Duck-typed backward compat — old tag name works until instance is updated |
| `action_context` references renamed tag (`raw-idea` → `raw-ideas`) | Template validation ensures `action_context` refs match current tag names |

### Constraints

- **C-1:** Must extend existing `WorkflowManagerService` — not rewrite.
- **C-2:** `idea_folder` field preserved in instance for backward compatibility.
- **C-3:** `copilot-prompt.json` `input_source` NOT removed in this feature — only deprecated. Actual removal happens after FEATURE-041-F confirms fallback works.
- **C-4:** Both template copies (`x-ipe-docs/config/workflow-template.json` and `src/x_ipe/resources/config/workflow-template.json`) MUST stay in sync after tag rename.
- **C-5:** `copilot-prompt.json` references to `$output:raw-idea$` MUST be updated to `$output:raw-ideas$` in both copies.

## Out of Scope

- Modal UI changes (→ FEATURE-041-F)
- Dropdown rendering, reopen pre-population (→ FEATURE-041-F)
- Skill `extra_context_reference` input parameter (→ FEATURE-041-G)
- `copilot-prompt.json` `input_source` removal (post-migration cleanup)
- Workflow instance file migration script (duck-typing handles it at runtime)
- Multi-select UI for array-valued `action_context` refs (→ future CR if needed)

## Technical Considerations

- **Affected backend files:**
  - `src/x_ipe/services/workflow_manager_service.py` — deliverables parsing, dual-format detection, array expansion in `resolve_deliverables`, context storage/retrieval, validation logic (including array element validation)
  - `src/x_ipe/services/app_agent_interaction.py` — `update_workflow_action` MCP tool parameter type change, conversion logic
  - `src/x_ipe/routes/workflow_routes.py` — pass-through of new deliverable format
- **Affected config (dual locations — must stay in sync):**
  - `x-ipe-docs/config/workflow-template.json` — tag rename `raw-idea` → `raw-ideas`, all `action_context` ref updates
  - `src/x_ipe/resources/config/workflow-template.json` — same changes
  - `x-ipe-docs/config/copilot-prompt.json` — `$output:raw-idea$` → `$output:raw-ideas$` token updates
  - `src/x_ipe/resources/config/copilot-prompt.json` — same changes
- **Affected frontend:**
  - `src/x_ipe/static/js/features/workflow-stage.js` — `_renderDeliverables` must handle expanded array entries
  - `src/x_ipe/static/js/features/action-execution-modal.js` — `_resolveTemplate` must handle array-valued tags (first element)
- **Affected tests (~30+ files reference `$output:raw-idea`):**
  - `tests/test_workflow_manager.py` — new tests for array storage, validation, schema version bump
  - `tests/test_workflow_feature_lanes.py` — per-feature scoping tests
  - All test fixtures using `raw-idea` tag must be updated to `raw-ideas`
- **The candidate resolution algorithm (FR-7) is backend-only** — it's a utility function that FEATURE-041-F's UI will call via API

## Open Questions

None — all questions resolved during IDEA-029 brainstorming (CR-002) and CR-003 impact analysis.
