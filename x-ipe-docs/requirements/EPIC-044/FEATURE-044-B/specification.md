# Feature Specification: Skill Creator Template Update

> Feature ID: FEATURE-044-B
> Epic ID: EPIC-044
> Version: v1.0
> Status: Refined
> Last Updated: 03-04-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-04-2026 | Initial specification |

## Linked Mockups

No mockups — template/config change only.

## Overview

FEATURE-044-B updates the `x-ipe-meta-skill-creator` task-based template to replace the legacy boolean flags (`auto_proceed: false` and `require_human_review: yes/no`) with the new unified `process_preference.auto_proceed` enum and mode-aware conditional blocks. This ensures all future skills created from the template follow the 3-mode auto-proceed pattern from day one.

## User Stories

1. **As a skill creator**, I want the task-based template to include `process_preference.auto_proceed` so new skills automatically support the 3-mode system.
2. **As an AI agent**, I want mode-aware conditional block patterns in the template so I know how to handle human-review steps in each mode.

## Acceptance Criteria

### AC Group 1: Input Parameter Changes

- [ ] AC-044-B.1: Template Input Parameters section has `process_preference.auto_proceed: "manual | auto | stop_for_question"` with default `manual` replacing the old `auto_proceed: false`
- [ ] AC-044-B.2: Template does NOT contain `auto_proceed: false` (boolean) anywhere in Input Parameters
- [ ] AC-044-B.3: Template does NOT contain `require_human_review: "{yes | no}"` in task type attributes

### AC Group 2: Output Result Changes

- [ ] AC-044-B.4: Template Output Result does NOT contain `require_human_review: "{yes | no}"`
- [ ] AC-044-B.5: Template Output Result includes `process_preference.auto_proceed: "{from input process_preference.auto_proceed}"`

### AC Group 3: Mode-Aware Blocks

- [ ] AC-044-B.6: Template Execution Procedure includes a mode-aware conditional block pattern at the completion/review step
- [ ] AC-044-B.7: Block pattern shows: `IF process_preference.auto_proceed == "auto" → skip human review, call x-ipe-tool-decision-making if needed`; `IF "manual" or "stop_for_question" → ask human and wait`

## Functional Requirements

- **FR-044-B.1:** Replace `auto_proceed: false` with `process_preference.auto_proceed: "manual | auto | stop_for_question"` (default: `manual`) in the template input section.
- **FR-044-B.2:** Remove `require_human_review: "{yes | no}"` from both input task type attributes and output result.
- **FR-044-B.3:** Add `process_preference.auto_proceed: "{from input process_preference.auto_proceed}"` to the output result YAML.
- **FR-044-B.4:** Add a mode-aware conditional block in the execution procedure's completion step showing the 3-mode branching pattern.

## Non-Functional Requirements

- **NFR-044-B.1:** Template changes MUST maintain the existing section order (v2 Cognitive Flow).
- **NFR-044-B.2:** Template body MUST stay under 500 lines.

## Dependencies

- FEATURE-044-A (Decision Making Tool Skill) — template references `x-ipe-tool-decision-making` in mode-aware blocks ✅ Complete

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Existing skills created from old template | Not affected — this only changes the template for future skills |
| Template line count near 500 | Mode-aware block adds ~10 lines; verify stays under limit |

## Out of Scope

- Updating existing 22 skills (that's FEATURE-044-C)
- Updating the tool-skill or other skill type templates

## Technical Considerations

- Template file: `.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-task-based.md`
- Changes are surgical: 3 removals + 3 additions
- The mode-aware block pattern should be in the last execution step (completion)

## Open Questions

None.
