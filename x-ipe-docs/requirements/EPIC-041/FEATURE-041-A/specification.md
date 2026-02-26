# Feature Specification: Per-Feature Config & Core Resolution (MVP)

> Feature ID: FEATURE-041-A
> Epic ID: EPIC-041
> Version: v1.0
> Status: Refined
> Last Updated: 02-25-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-25-2026 | Initial specification |

## Linked Mockups

N/A — extends existing modal pattern; no new visual mockups.

## Overview

FEATURE-041-A is the MVP for enabling per-feature workflow actions in the Action Execution Modal. Currently, the modal only resolves input files from shared-level actions (ideation, requirement stages). Per-feature actions (feature_refinement, technical_design, implementation, acceptance_testing, change_request) have no config entries and no way to pass a feature ID or resolve per-feature deliverables.

This feature adds three capabilities: (1) a new `"feature"` section in copilot-prompt.json with 5 per-feature action entries, (2) feature ID propagation from the Feature Lane UI through the modal constructor into the CLI command, and (3) per-feature deliverable resolution in `_resolveInputFiles()` with cross-stage fallback to shared actions.

**Who:** Developers using the workflow UI to execute per-feature actions via Copilot CLI.

**Why:** Without this, clicking a per-feature action in the Feature Lane either shows "no instructions available" or fails to find the correct deliverables scoped to that feature.

## User Stories

- **US-1:** As a developer, I want to click "Feature Refinement" for a specific feature and see the modal pre-populated with that feature's input files from `feature_breakdown` deliverables, so I can immediately start refining.
- **US-2:** As a developer, I want the `--feature-id FEATURE-XXX` flag automatically included in the CLI command when I execute a per-feature action, so the skill knows which feature to operate on.
- **US-3:** As a developer, I want per-feature actions to fall back to shared-stage deliverables when the source action is a shared action (e.g. `feature_breakdown` is in the shared requirement stage), so the resolver doesn't fail.
- **US-4:** As a developer, I want to click "Change Request" and get a manual file path input (no auto-resolution), since CRs can target any file in the project.
- **US-5:** As a developer, I want the `<feature-id>` placeholder in command templates to be replaced with the actual feature ID, so commands are ready to execute without manual editing.

## Acceptance Criteria

- [ ] **AC-1:** Clicking "Feature Refinement" for FEATURE-XXX opens the Action Execution Modal with auto-resolved files from `feature_breakdown` deliverables. Since `feature_breakdown` is a shared action, the resolver falls back to `shared.requirement.actions.feature_breakdown.deliverables`.
- [ ] **AC-2:** Clicking "Change Request" for any feature opens the modal with a manual file path text input (no dropdown), since the `change-request` config has no `input_source`.
- [ ] **AC-3:** All per-feature action modals include `--feature-id FEATURE-XXX` in the constructed CLI command (visible in the instructions section).
- [ ] **AC-4:** Existing shared-level actions (refine_idea, requirement_gathering, feature_breakdown, design_mockup) continue to work without regression — no feature ID injected, same resolution behavior.
- [ ] **AC-5:** copilot-prompt.json contains a `"feature"` section with a `"prompts"` array holding 5 entries: `feature-refinement`, `technical-design`, `implementation`, `acceptance-testing`, `change-request`.
- [ ] **AC-6:** The `"placeholder"` section in copilot-prompt.json has a `"feature-id"` entry documenting its replacement behavior.
- [ ] **AC-7:** When the workflow API returns no deliverables for any source action (per-feature or shared fallback), the modal shows a manual file path input as fallback.
- [ ] **AC-8:** The `<feature-id>` placeholder in command templates is replaced with the feature ID passed to the modal (e.g. `FEATURE-041-A`).
- [ ] **AC-9:** Clicking "Technical Design" for FEATURE-XXX opens the modal and `_resolveInputFiles()` checks `features[XXX].implement.actions.feature_refinement.deliverables` first, then falls back to shared stages if not found.

## Functional Requirements

### FR-1: Copilot-Prompt "feature" Section

- **FR-1.1:** Add a `"feature"` top-level key to copilot-prompt.json containing `{ "prompts": [...] }`.
- **FR-1.2:** The section MUST use the `"prompts"` array pattern so `_getConfigEntry()` finds entries automatically (it iterates all sections looking for `sectionData.prompts`).
- **FR-1.3:** Add 5 prompt entries:

| id | icon | input_source | command template |
|----|------|-------------|-----------------|
| `feature-refinement` | `bi-rulers` | `["feature_breakdown"]` | `refine feature <feature-id> from <input-file> with feature refinement skill` |
| `technical-design` | `bi-gear` | `["feature_refinement"]` | `create technical design for <feature-id> from <input-file> with technical design skill` |
| `implementation` | `bi-code-slash` | `["technical_design"]` | `implement <feature-id> from <input-file> with code implementation skill` |
| `acceptance-testing` | `bi-check2-circle` | `["implementation"]` | `run acceptance tests for <feature-id> from <input-file> with feature acceptance test skill` |
| `change-request` | `bi-arrow-repeat` | _(none)_ | `process change request for <feature-id> with change request skill` |

- **FR-1.4:** Each entry MUST include `prompt-details` with at least an `"en"` language entry containing `label` and `command`.
- **FR-1.5:** Each `input_source` entry MAY include a `file_pattern` field (string) — deferred to FEATURE-041-B but the schema must not break if present.
- **FR-1.6:** The `change-request` entry MUST NOT have an `input_source` field, forcing the modal to show a manual file path input.

### FR-2: Feature ID Propagation

- **FR-2.1:** `_dispatchFeatureAction(wfName, featureId, actionKey, featureData)` in workflow-stage.js MUST pass `featureId` to `_dispatchCliAction()` as a new parameter.
- **FR-2.2:** `_dispatchCliAction(wfName, actionKey, skillName, triggerBtn, featureId)` MUST accept an optional `featureId` parameter and forward it to the ActionExecutionModal constructor.
- **FR-2.3:** The ActionExecutionModal constructor MUST accept a `featureId` option: `constructor({ ..., featureId })` and store it as `this.featureId`.
- **FR-2.4:** `_loadInstructions()` MUST replace `<feature-id>` in the command template with `this.featureId` when present.
- **FR-2.5:** `_buildCommand()` MUST append `--feature-id {featureId}` to the command string when `this.featureId` is truthy.
- **FR-2.6:** When `this.featureId` is falsy (shared actions), NO `--feature-id` flag is added and `<feature-id>` placeholder is left unresolved or stripped.

### FR-3: Per-Feature Deliverable Resolution

- **FR-3.1:** `_resolveInputFiles(inputSource)` MUST accept an optional second parameter `featureId` (or read from `this.featureId`).
- **FR-3.2:** When `featureId` is provided, the resolver MUST first search per-feature stages in the workflow JSON: `data.features[featureId].implement.actions[sourceAction].deliverables`, then `data.features[featureId].validation.actions[sourceAction].deliverables`, then `data.features[featureId].feedback.actions[sourceAction].deliverables`.
- **FR-3.3:** When a source action is NOT found in any per-feature stage, the resolver MUST fall back to shared stages: `data.shared.ideation.actions[sourceAction]`, `data.shared.requirement.actions[sourceAction]`.
- **FR-3.4:** When `featureId` is NOT provided (shared actions), the resolver MUST behave exactly as it does today — scan `data.shared` stages only.
- **FR-3.5:** `_loadInstructions()` MUST pass `this.featureId` to `_resolveInputFiles()` so the resolver knows to scope to a specific feature.
- **FR-3.6:** When no deliverables are found from any source (per-feature + shared fallback), the modal MUST show a manual file path text input as fallback (existing behavior for zero results).

### FR-4: Placeholder Documentation

- **FR-4.1:** Add `"feature-id": "Replaced with the target feature ID (e.g. FEATURE-041-A) for per-feature actions"` to the `"placeholder"` section of copilot-prompt.json.

## Non-Functional Requirements

- **NFR-1:** Per-feature resolution MUST reuse the existing single GET `/api/workflow/{name}` call — no additional API endpoints or requests.
- **NFR-2:** The `"feature"` section MUST follow the same `{ "prompts": [...] }` schema so `_getConfigEntry()` works without modification.
- **NFR-3:** Backward compatibility: existing entries in `"ideation"`, `"evaluation"`, and `"workflow"` sections MUST remain untouched.
- **NFR-4:** copilot-prompt.json version MUST be bumped from `"3.1"` to `"3.2"`.

## UI/UX Requirements

- The modal for per-feature actions is visually identical to shared actions — same layout, same input selector dropdown, same extra-instructions textarea.
- When `featureId` is present, the instructions section shows the command with the actual feature ID substituted (e.g. `refine feature FEATURE-041-A from x-ipe-docs/requirements/...`).
- The `--feature-id` flag appears in the visible command text so the user can verify it.
- No changes to modal styling, layout, or animations.

## Dependencies

### Internal

| Dependency | Type | Status |
|-----------|------|--------|
| FEATURE-038-A (Action Execution Modal) | Foundation — extends this modal class | Implemented |
| FEATURE-040-A (Modal Generalization & Core Actions) | Foundation — `_resolveInputFiles()` and `_getConfigEntry()` from this | Done Implementation |

### External

None.

## Business Rules

- **BR-1:** Per-feature actions MUST only inject `--feature-id` when the modal is opened from a Feature Lane. Actions opened from the shared stage ribbon MUST NOT inject `--feature-id`.
- **BR-2:** The `change_request` action always uses manual file path input regardless of feature context — CRs can target any file in the project.
- **BR-3:** The resolver's cross-stage fallback is one-directional: per-feature stages → shared stages. It never searches shared → per-feature.
- **BR-4:** `quality_evaluation` is out of scope (deferred, `skill: null` in ACTION_MAP).

## Edge Cases & Constraints

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| E-1 | Feature has no deliverables for `feature_refinement` yet (first action in implement stage) | Resolver falls back to shared `feature_breakdown` deliverables; if still empty, shows manual path input |
| E-2 | Feature ID contains special characters (e.g. `FEATURE-041-A`) | Hyphens are valid; passed as-is in `--feature-id` flag and placeholder replacement |
| E-3 | Workflow JSON has no `features` key (no features created yet) | `data.features` is undefined — resolver skips per-feature search, falls back to shared stages normally |
| E-4 | User manually opens a per-feature action without feature context (edge case) | `featureId` is undefined → resolver skips per-feature search, behaves like shared action. `<feature-id>` placeholder left unresolved — command may be incomplete |
| E-5 | copilot-prompt.json not loaded (network error) | Existing behavior — modal shows "No instructions available" with execute button disabled |
| E-6 | Source action exists in both per-feature AND shared stages (shouldn't happen but possible) | Per-feature takes priority — shared fallback only when per-feature yields nothing |
| E-7 | Multiple features exist but wrong feature ID passed | Resolver scans `features[featureId]` — if not found, `features[featureId]` is undefined, falls back to shared |

## Out of Scope

- Multi-source dropdown UI (one dropdown per input_source) — deferred to FEATURE-041-B
- `file_pattern` auto-suggest matching — deferred to FEATURE-041-B
- ✨ auto indicator for auto-suggested files — deferred to FEATURE-041-B
- Modal title including feature ID — deferred to FEATURE-041-B
- Skill `workflow.action` / `feature_id` updates — deferred to FEATURE-041-C
- New workflow actions (test_generation, etc.) — deferred to FEATURE-041-D
- `quality_evaluation` action — deferred indefinitely

## Technical Considerations

- `_getConfigEntry()` (line 116-130 of action-execution-modal.js) iterates all top-level sections in copilot-prompt.json looking for `sectionData.prompts` arrays. Adding `"feature": { "prompts": [...] }` is auto-discovered with zero code changes to the lookup.
- The workflow API response structure is: `data.shared.{ideation|requirement}.actions.{key}.deliverables[]` for shared actions, and `data.features[].{implement|validation|feedback}.actions.{key}.deliverables[]` for per-feature actions.
- `_dispatchFeatureAction()` at line 877 already receives `featureId` as its second parameter but currently does NOT pass it to `_dispatchCliAction()` at line 902. This is the primary wiring gap.
- `_dispatchCliAction()` at line 515 creates `new ActionExecutionModal({...})` but has no `featureId` parameter — needs adding.
- The existing `_resolveInputFiles()` at line 132 only searches `data.stages || data.shared` — needs a new branch for `data.features[featureId]` when featureId is present.
- `_buildCommand()` at line 298 is the natural place to inject `--feature-id` — after the `--workflow-mode@{name}` prefix.
- The `<current-idea-file>` alias should remain for backward compatibility with ideation actions.

## Open Questions

None — all resolved during ideation and requirement gathering.
