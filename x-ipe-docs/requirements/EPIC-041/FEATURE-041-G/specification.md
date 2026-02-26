# Feature Specification: Skill Extra Context Reference

> Feature ID: FEATURE-041-G
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

N/A — This feature is skill documentation (SKILL.md) changes only.

## Overview

FEATURE-041-G adds `extra_context_reference` to the skill workflow input block, enabling skills to receive explicit context file paths from the workflow instance's `context` field. When a skill runs in workflow mode, it reads `extra_context_reference` to get the user's action context selections. Skills handle three value types: a file path (use as direct input), "N/A" (skip that context), and "auto-detect" (use the skill's own discovery logic).

This feature also deprecates `copilot-prompt.json` `input_source` for actions that have `action_context` defined in the template. Skills must remain backward-compatible when `extra_context_reference` is not provided (free-mode execution).

**Who:** Skill authors, AI agents executing skills in workflow mode, X-IPE framework developers.

**Why:** Currently, skills in workflow mode have no standard way to receive context from the workflow. They rely on auto-discovery or ad-hoc parameter passing. `extra_context_reference` provides a unified, explicit input contract.

## User Stories

- **US-1:** As a skill author, I want to declare `extra_context_reference` in my skill's workflow input block, so the framework knows my skill accepts context paths.
- **US-2:** As an AI agent executing a skill in workflow mode, I want `extra_context_reference` to contain the resolved file paths from the workflow instance `context` field, so I don't need to guess file locations.
- **US-3:** As an AI agent, when `extra_context_reference[ref]` is "N/A", I want the skill to skip that context input entirely.
- **US-4:** As an AI agent, when `extra_context_reference[ref]` is "auto-detect", I want the skill to use its own discovery logic to find relevant files.
- **US-5:** As a skill author, I want my skill to work without `extra_context_reference` (free-mode), so it remains usable outside workflow contexts.

## Acceptance Criteria

- [ ] **AC-1:** All workflow-aware skills have `extra_context_reference` declared in their `workflow` input block.
- [ ] **AC-2:** In workflow mode, the skill reads `extra_context_reference` from the workflow instance's `context` field for its action.
- [ ] **AC-3:** When `extra_context_reference[ref]` is a file path, the skill uses it as direct input (reads the file).
- [ ] **AC-4:** When `extra_context_reference[ref]` is "N/A", the skill skips that context input.
- [ ] **AC-5:** When `extra_context_reference[ref]` is "auto-detect", the skill uses its own discovery logic.
- [ ] **AC-6:** Skills work correctly when `extra_context_reference` is not provided (free-mode / backward compat).
- [ ] **AC-7:** `copilot-prompt.json` `input_source` is documented as deprecated for actions with `action_context`.

## Functional Requirements

### FR-1: Skill Input Block Extension

- **FR-1.1:** Add `extra_context_reference` to the skill `workflow` input block in SKILL.md:
  ```yaml
  input:
    workflow:
      name: "N/A"
      action: "{action_name}"
      extra_context_reference:
        ref-name-1: "path/to/file | N/A | auto-detect"
        ref-name-2: "path/to/file | N/A | auto-detect"
  ```
- **FR-1.2:** The ref names in `extra_context_reference` MUST match the `action_context` entry names from the action's template definition.
- **FR-1.3:** Default value for `extra_context_reference` is `N/A` (not provided — free-mode).

### FR-2: Context Value Handling

- **FR-2.1:** File path value → skill reads and uses the file as direct input.
- **FR-2.2:** `"N/A"` value → skill skips that context ref entirely.
- **FR-2.3:** `"auto-detect"` value → skill uses its existing discovery logic (scan project, read known paths, etc.).
- **FR-2.4:** Skills MUST NOT fail if `extra_context_reference` is absent — fall back to existing behavior (free-mode).

### FR-3: Skill File Updates

- **FR-3.1:** Update the following skills with `extra_context_reference` in their workflow input block:
  - `x-ipe-task-based-ideation-v2` (refine_idea action: raw-idea, uiux-reference)
  - `x-ipe-task-based-idea-mockup` (design_mockup action: refined-idea, uiux-reference)
  - `x-ipe-task-based-requirement-gathering` (requirement_gathering action: refined-idea, mockup-html)
  - `x-ipe-task-based-feature-breakdown` (feature_breakdown action: requirement-doc)
  - `x-ipe-task-based-feature-refinement` (feature_refinement action: requirement-doc, features-list)
  - `x-ipe-task-based-technical-design` (technical_design action: specification)
  - `x-ipe-task-based-code-implementation` (implementation action: tech-design, specification)
  - `x-ipe-task-based-feature-acceptance-test` (acceptance_testing action: specification, impl-files)
  - `x-ipe-task-based-change-request` (change_request action: eval-report, specification)
- **FR-3.2:** Each skill's execution procedure MUST reference `extra_context_reference` in the step where it reads context (e.g., "If `extra_context_reference.raw-idea` is provided, read that file; else use discovery logic").
- **FR-3.3:** Skills that already have context-reading steps (e.g., ideation reads idea file) MUST integrate `extra_context_reference` into those existing steps — do not add duplicate logic.

### FR-4: Deprecation of input_source

- **FR-4.1:** Add deprecation note to `copilot-prompt.json` documentation: `input_source` is deprecated for actions with `action_context` in the template.
- **FR-4.2:** Do NOT remove `input_source` from `copilot-prompt.json` in this feature — it remains as fallback for FEATURE-041-F's legacy path.

## Non-Functional Requirements

- **NFR-1:** Skill file changes are pure SKILL.md documentation edits — no application code changes in this feature.
- **NFR-2:** Skills MUST remain functional without `extra_context_reference` (zero regression in free-mode).
- **NFR-3:** Each skill update should be atomic — one skill file change per commit or logical unit.

## UI/UX Requirements

N/A — This feature is skill documentation only.

## Dependencies

### Internal Dependencies

- None for implementation (SKILL.md edits are independent of backend/frontend).
- At runtime, `extra_context_reference` values come from the workflow instance `context` field (established by FEATURE-041-E + FEATURE-041-F). However, the skill docs can be written before those features ship — skills just need to handle the case where `extra_context_reference` is absent.

### External Dependencies

None.

## Business Rules

- **BR-1:** Ref names in `extra_context_reference` MUST match `action_context` keys in the template.
- **BR-2:** A skill MUST NOT require `extra_context_reference` to function — it's an enhancement, not a prerequisite.
- **BR-3:** "auto-detect" delegates to the skill's own logic — the framework does NOT resolve it.
- **BR-4:** "N/A" means "no context for this ref" — the skill skips, not fails.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| `extra_context_reference` absent (free-mode) | Skill uses existing discovery logic; no error |
| `extra_context_reference` has a ref the skill doesn't recognize | Skill ignores unknown refs silently |
| File path in `extra_context_reference` points to non-existent file | Skill logs warning, falls back to discovery logic |
| All refs are "auto-detect" | Equivalent to free-mode — skill discovers everything |
| All refs are "N/A" | Skill runs with no external context input |
| Skill added after FEATURE-041-G ships (new skill) | New skills should include `extra_context_reference` in their input block |

### Constraints

- **C-1:** Changes are SKILL.md files only — no Python/JS code changes.
- **C-2:** Must not break free-mode (non-workflow) execution of any skill.
- **C-3:** `input_source` not removed — only deprecated.

## Out of Scope

- Backend logic to populate `extra_context_reference` from instance (→ handled by workflow manager when launching CLI)
- Modal UI for context selection (→ FEATURE-041-F)
- Template/instance schema changes (→ FEATURE-041-E)
- Actual removal of `input_source` from `copilot-prompt.json` (post-migration)

## Technical Considerations

- **Affected skill files:** All skills in `.github/skills/x-ipe-task-based-*/SKILL.md` that have workflow input blocks (see FR-3.1 list)
- **Pattern:** Each skill's input YAML adds `extra_context_reference` under `workflow`; execution procedure steps add conditional: "If workflow mode AND extra_context_reference.{ref} is a path → use it; else → existing behavior"
- **Testing:** Skill behavior with `extra_context_reference` is tested via acceptance tests for each feature that uses the skill (not in this feature)

## Open Questions

None — all questions resolved during IDEA-029 brainstorming.
