# Feature Specification: New Workflow Actions (Phase 5)

> Feature ID: FEATURE-041-D
> Version: v1.0
> Status: Refined
> Last Updated: 03-04-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-04-2026 | Initial specification — updated scope from original requirement (moved feature_closing to validation, human_playground to feedback, added code_refactor replacing quality_evaluation, added test_generation to implement) |
| v1.1 | 03-04-2026 | Added change_request to scope — copilot prompt entry + update_workflow_action skill integration for completeness |

## Overview

FEATURE-041-D completes the workflow pipeline by adding four new actions to the workflow engine: `test_generation`, `code_refactor`, `feature_closing`, and `human_playground`. The original requirement (FR-041.29–33) specified three actions (test_generation, human_playground, feature_closing) with human_playground and feature_closing both in the feedback stage. This updated scope reorganises the actions based on the natural development lifecycle:

- **test_generation** is added to the implement stage as a mandatory step between technical_design and implementation, enforcing a TDD workflow.
- **code_refactor** is a new addition that replaces the placeholder `quality_evaluation` action in the validation stage, making refactoring a mandatory post-acceptance step.
- **feature_closing** moves from feedback to validation as the final mandatory validation gate — it produces the PR and closes the feature.
- **human_playground** moves to feedback as an optional interactive demo step alongside change_request.

This feature touches the backend workflow engine (`workflow_manager_service.py`), the workflow template JSON configuration, the frontend ACTION_MAP, the copilot prompt configuration, and five agent skill definitions. Both dependencies (FEATURE-041-A config infrastructure, FEATURE-041-C skill update pattern) are already completed.

## User Stories

- **US-1:** As a developer using workflow mode, I want a test_generation action between technical_design and implementation so that I follow a TDD approach and generate tests before writing code.
- **US-2:** As a developer using workflow mode, I want a code_refactor action after acceptance_testing so that I can clean up and refactor code with confidence after tests pass.
- **US-3:** As a developer using workflow mode, I want a feature_closing action as the final validation step so that PR creation and feature board updates happen as a structured workflow gate.
- **US-4:** As a developer using workflow mode, I want an optional human_playground action in feedback so that I can create interactive demos for stakeholder review before or instead of a change request.
- **US-5:** As a developer using workflow mode, I want the change_request action fully integrated with workflow tracking (copilot prompt + action status update) so that feedback-stage actions are consistently tracked.

## Acceptance Criteria

### AC-1: test_generation in implement stage (FR-041.29)
- **AC-1.1:** `workflow-template.json` implement stage MUST contain a `test_generation` action with `optional: false`, positioned after `technical_design` in the actions list.
- **AC-1.2:** `test_generation` action_context MUST declare `tech-design` (required) and `specification` (required) as inputs.
- **AC-1.3:** `test_generation` deliverables MUST include `$output:test-plan` and `$output-folder:test-folder`.
- **AC-1.4:** `test_generation` next_actions_suggested MUST be `["implementation"]`.
- **AC-1.5:** `workflow_manager_service.py` hardcoded `_stage_config` for implement stage MUST include `test_generation` in `mandatory_actions` list, after `technical_design` and before `implementation`.
- **AC-1.6:** `_next_actions_map` MUST include `test_generation` mapping: `technical_design → [test_generation]` and `test_generation → [implementation]`.
- **AC-1.7:** `_deliverable_categories` MUST map `test_generation` to `"quality"`.
- **AC-1.8:** `ACTION_MAP` in `workflow-stage.js` implement stage MUST include `test_generation: { label: 'Test Generation', icon: '🧪', mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-test-generation' }`.

### AC-2: code_refactor replaces quality_evaluation in validation stage (NEW)
- **AC-2.1:** `workflow-template.json` validation stage MUST replace `quality_evaluation` with `code_refactor` action with `optional: false`.
- **AC-2.2:** `code_refactor` action_context MUST declare `test-report` (not required) and `specification` (required) as inputs.
- **AC-2.3:** `code_refactor` deliverables MUST include `$output:refactor-report`.
- **AC-2.4:** `code_refactor` next_actions_suggested MUST be `["feature_closing"]`.
- **AC-2.5:** `workflow_manager_service.py` hardcoded `_stage_config` for validation stage MUST include `code_refactor` in `mandatory_actions` (not optional_actions), replacing `quality_evaluation`.
- **AC-2.6:** `_next_actions_map` MUST update: `acceptance_testing → [code_refactor]` and add `code_refactor → [feature_closing]`.
- **AC-2.7:** `_deliverable_categories` MUST replace `quality_evaluation` → `"quality"` with `code_refactor` → `"quality"`.
- **AC-2.8:** `ACTION_MAP` in `workflow-stage.js` validation stage MUST replace `quality_evaluation` with `code_refactor: { label: 'Code Refactor', icon: '🔧', mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-code-refactor' }`.

### AC-3: feature_closing in validation stage (FR-041.30 — updated placement)
- **AC-3.1:** `workflow-template.json` validation stage MUST contain a `feature_closing` action with `optional: false`, positioned after `code_refactor`.
- **AC-3.2:** `feature_closing` action_context MUST declare `specification` (required) and `refactor-report` (not required) as inputs.
- **AC-3.3:** `feature_closing` deliverables MUST include `$output:closing-report`.
- **AC-3.4:** `feature_closing` next_actions_suggested MUST be `["human_playground", "change_request"]` (pointing to feedback stage).
- **AC-3.5:** `workflow_manager_service.py` hardcoded `_stage_config` for validation stage MUST include `feature_closing` in `mandatory_actions`.
- **AC-3.6:** `_next_actions_map` MUST include `feature_closing → [human_playground, change_request]`.
- **AC-3.7:** `_deliverable_categories` MUST map `feature_closing` to `"quality"`.
- **AC-3.8:** `ACTION_MAP` in `workflow-stage.js` validation stage MUST include `feature_closing: { label: 'Feature Closing', icon: '🏁', mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-feature-closing' }`.

### AC-4: human_playground in feedback stage (FR-041.30 — updated placement)
- **AC-4.1:** `workflow-template.json` feedback stage MUST contain a `human_playground` action with `optional: true`, positioned before `change_request`.
- **AC-4.2:** `human_playground` action_context MUST declare `specification` (required) and `impl-files` (not required) as inputs.
- **AC-4.3:** `human_playground` deliverables MUST include `$output:playground-url`.
- **AC-4.4:** `human_playground` next_actions_suggested MUST be `["change_request"]`.
- **AC-4.5:** `workflow_manager_service.py` hardcoded `_stage_config` for feedback stage MUST include `human_playground` in `optional_actions`.
- **AC-4.6:** `_next_actions_map` MUST include `human_playground → [change_request]`.
- **AC-4.7:** `_deliverable_categories` MUST map `human_playground` to `"quality"`.
- **AC-4.8:** `ACTION_MAP` in `workflow-stage.js` feedback stage MUST include `human_playground: { label: 'Human Playground', icon: '🎮', mandatory: false, interaction: 'cli', skill: 'x-ipe-task-based-human-playground' }`.

### AC-5: Copilot prompt configuration (FR-041.32)
- **AC-5.1:** `copilot-prompt.json` workflow-prompts MUST contain an entry for `code_refactor` with action, icon, input_source referencing `acceptance_testing`, and bilingual prompt-details.
- **AC-5.2:** `copilot-prompt.json` workflow-prompts MUST contain an entry for `feature_closing` with action, icon, input_source referencing `code_refactor`, and bilingual prompt-details.
- **AC-5.3:** `copilot-prompt.json` workflow-prompts MUST contain an entry for `human_playground` with action, icon, input_source referencing `implementation`, and bilingual prompt-details.
- **AC-5.4:** Existing `test_generation` prompt entry MUST remain unchanged (already present at lines 113-129).
- **AC-5.5:** Existing `implementation` prompt entry input_source MUST update from `["technical_design"]` to `["test_generation"]` to reflect the new action ordering.
- **AC-5.6:** `copilot-prompt.json` workflow-prompts MUST contain an entry for `change_request` with action, icon, input_source referencing `feature_closing`, and bilingual prompt-details.

### AC-6: Skill update_workflow_action integration (FR-041.33)
- **AC-6.1:** `x-ipe-task-based-test-generation` SKILL.md MUST have `update_workflow_action` MCP call in its completion step with `action: "test_generation"`, status, feature_id, and deliverables.
- **AC-6.2:** `x-ipe-task-based-code-refactor` SKILL.md MUST have `update_workflow_action` MCP call in its completion step with `action: "code_refactor"`, status, feature_id, and deliverables.
- **AC-6.3:** `x-ipe-task-based-feature-closing` SKILL.md MUST have `update_workflow_action` MCP call in its completion step with `action: "feature_closing"`, status, feature_id, and deliverables.
- **AC-6.4:** `x-ipe-task-based-human-playground` SKILL.md MUST have `update_workflow_action` MCP call in its completion step with `action: "human_playground"`, status, feature_id, and deliverables.
- **AC-6.5:** `x-ipe-task-based-change-request` SKILL.md MUST have `update_workflow_action` MCP call in its completion step with `action: "change_request"`, status, feature_id, and deliverables.
- **AC-6.6:** All 5 skills MUST include `extra_context_reference` in their input parameters with the same keys declared in their respective `action_context` definitions.

### AC-7: Backward compatibility
- **AC-7.1:** All existing workflow tests MUST continue to pass after changes.
- **AC-7.2:** The `quality_evaluation` key MUST be fully removed from all config files, service code, ACTION_MAP, and _next_actions_map — no orphaned references.
- **AC-7.3:** Existing workflows in progress that have `quality_evaluation` status data MUST NOT cause runtime errors (graceful handling of unknown action keys).

## Functional Requirements

### FR-1: Workflow Template Updates
- **FR-1.1:** Add `test_generation` action to implement stage in `workflow-template.json` with: `optional: false`, action_context (tech-design required, specification required), deliverables ($output:test-plan, $output-folder:test-folder), next_actions_suggested: [implementation].
- **FR-1.2:** Replace `quality_evaluation` with `code_refactor` action in validation stage with: `optional: false`, action_context (test-report not required, specification required), deliverables ($output:refactor-report), next_actions_suggested: [feature_closing].
- **FR-1.3:** Add `feature_closing` action to validation stage with: `optional: false`, action_context (specification required, refactor-report not required), deliverables ($output:closing-report), next_actions_suggested: [human_playground, change_request].
- **FR-1.4:** Add `human_playground` action to feedback stage with: `optional: true`, action_context (specification required, impl-files not required), deliverables ($output:playground-url), next_actions_suggested: [change_request].

### FR-2: Backend Service Updates
- **FR-2.1:** Update `_stage_config` implement mandatory_actions to: `["feature_refinement", "technical_design", "test_generation", "implementation"]`.
- **FR-2.2:** Update `_stage_config` validation mandatory_actions to: `["acceptance_testing", "code_refactor", "feature_closing"]`, optional_actions to: `[]`.
- **FR-2.3:** Update `_stage_config` feedback optional_actions to: `["human_playground", "change_request"]`.
- **FR-2.4:** Update `_next_actions_map`: `technical_design → [test_generation]`, `test_generation → [implementation]`, `acceptance_testing → [code_refactor]`, `code_refactor → [feature_closing]`, `feature_closing → [human_playground, change_request]`, `human_playground → [change_request]`. Remove `quality_evaluation` entry.
- **FR-2.5:** Update `_deliverable_categories`: add `test_generation → "quality"`, `code_refactor → "quality"`, `feature_closing → "quality"`, `human_playground → "quality"`. Remove `quality_evaluation` entry.

### FR-3: Frontend ACTION_MAP Updates
- **FR-3.1:** Add `test_generation` to implement stage in ACTION_MAP.
- **FR-3.2:** Replace `quality_evaluation` with `code_refactor` in validation stage ACTION_MAP.
- **FR-3.3:** Add `feature_closing` to validation stage in ACTION_MAP.
- **FR-3.4:** Add `human_playground` to feedback stage in ACTION_MAP.

### FR-4: Copilot Prompt Updates
- **FR-4.1:** Add `code_refactor` prompt entry with input_source from acceptance_testing deliverables.
- **FR-4.2:** Add `feature_closing` prompt entry with input_source from code_refactor deliverables.
- **FR-4.3:** Add `human_playground` prompt entry with input_source from implementation deliverables.
- **FR-4.4:** Update `implementation` prompt input_source from `["technical_design"]` to `["test_generation"]`.
- **FR-4.5:** Add `change_request` prompt entry with input_source from feature_closing deliverables.

### FR-5: Skill Workflow Integration
- **FR-5.1:** Add `update_workflow_action` MCP call to completion step of test-generation, code-refactor, feature-closing, human-playground, and change-request skills.
- **FR-5.2:** Add `extra_context_reference` input parameter to all 5 skills matching their action_context definitions.

## Non-Functional Requirements

- **NFR-1:** All changes MUST maintain backward compatibility with existing workflow instances.
- **NFR-2:** Frontend ACTION_MAP changes MUST NOT increase workflow-stage.js beyond the 20KB size limit.
- **NFR-3:** Backend changes MUST NOT alter the on-demand stage gating behavior (stages unlock only when attempting an action in a locked stage).
- **NFR-4:** Template JSON MUST remain valid JSON after changes.

## UI/UX Requirements

No new UI components. Changes are limited to:
- New action cards appearing in existing stage panels (implement, validation, feedback).
- Icons and labels rendered via existing ACTION_MAP mechanism.
- Mandatory actions show lock/check indicators using existing CSS.

## Dependencies

### Internal (all completed)
- **FEATURE-041-A** (Workflow Config Infrastructure) — ✅ Completed. Provides workflow-template.json structure and backend config loading.
- **FEATURE-041-C** (Skill Workflow Integration Pattern) — ✅ Completed. Established the pattern for execution_mode, extra_context_reference, and update_workflow_action in skills.

### External
- None.

## Business Rules

- **BR-1:** test_generation MUST be mandatory — TDD is enforced in workflow mode.
- **BR-2:** code_refactor MUST be mandatory — code quality review is a validation gate.
- **BR-3:** feature_closing MUST be mandatory — every feature must go through a structured closing process in workflow mode.
- **BR-4:** human_playground MUST be optional — interactive demos are not required for every feature.
- **BR-5:** The action ordering within each stage defines the recommended workflow sequence via next_actions_suggested, but agents may execute actions in any order within a stage as long as mandatory actions are completed before stage progression.

## Edge Cases & Constraints

- **EC-1:** Existing workflow instances that have `quality_evaluation` action data: The backend must not crash when encountering `quality_evaluation` in stored workflow JSON. Unknown action keys should be silently ignored during status evaluation.
- **EC-2:** The `implementation` prompt currently references `technical_design` as input_source. After this change it references `test_generation`, but test_generation's deliverable ($output:test-plan) is different from technical_design's ($output:tech-design). The implementation prompt must still reference tech-design deliverable — update input_source to `["test_generation"]` which will chain through to include the test plan context alongside the existing tech-design reference.
- **EC-3:** The `test_generation` copilot prompt already exists (lines 113-129). It must NOT be duplicated or modified — only the 3 new prompts are added.
- **EC-4:** Stage gating: implement stage has 4 mandatory actions now. All 4 must be "done" before validation unlocks on-demand.

## Out of Scope

- **OOS-1:** Modifying the stage gating algorithm itself (stays on-demand).
- **OOS-2:** Adding new stages to the workflow.
- **OOS-3:** Updating `refactoring-analysis` or `improve-code-quality` skills — only `code-refactor` is mapped as a workflow action. The other refactoring skills are sub-skills called by code-refactor and don't need direct workflow integration.
- **OOS-4:** FEATURE-039-B (Enhanced Modal Features) — UI polish is a separate feature.
- **OOS-5:** Creating new workflow template versions — changes apply to the existing template.

## Technical Considerations

- The `workflow-template.json` drives both the backend (loaded in `_load_template_config`) and is also the authoritative source for action_context definitions used by skills. Both the template JSON and the hardcoded fallback in `workflow_manager_service.py` must be updated in sync.
- The ACTION_MAP in `workflow-stage.js` must match the template JSON exactly in terms of action keys, mandatory flags, and stage membership.
- Copilot prompts use a `$output:name$` and `$output-folder:name$` token syntax to reference deliverables from prior actions. New prompts must use the deliverable names declared in the template.
- The `update_workflow_action` MCP integration in skills follows the established pattern from FEATURE-041-C: a conditional block in the completion step that checks `execution_mode == "workflow-mode"` before calling the MCP tool.
- The `change_request` skill already has `execution_mode` and `extra_context_reference` but lacks `update_workflow_action` — only the MCP call needs to be added. Its `action_context` in workflow-template.json already exists (eval-report not required, specification required) and should be updated to reference `closing-report` instead of `eval-report` since quality_evaluation is being removed.

## Open Questions

None — all scope decisions have been confirmed by the user.
