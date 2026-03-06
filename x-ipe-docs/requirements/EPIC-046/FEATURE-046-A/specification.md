# Feature Specification: Skill-Creator Template + Guidelines Update

> Feature ID: FEATURE-046-A
> Epic ID: EPIC-046
> Version: v1.0
> Status: Refined
> Last Updated: 03-05-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-05-2026 | Initial specification |

## Overview

FEATURE-046-A updates the X-IPE skill-creator's task-based skill template (`x-ipe-task-based.md`) and associated guidelines to introduce the **5-phase Chinese learning method** as the mandatory structural backbone for all task-based skills.

The 5 phases — **博学之 (Study Broadly), 审问之 (Inquire Thoroughly), 慎思之 (Think Carefully), 明辨之 (Discern Clearly), 笃行之 (Practice Earnestly)** — replace the current flat `<step_N>` structure with a `<phase_N>` → `<step_N_M>` hierarchy. This addresses systematic gaps identified in TASK-751 research: while execution discipline (笃行之) is universally strong, inquiry (审问之 3/10), reflection (慎思之 3/10), and discernment (明辨之 1/10) are underrepresented.

This is the foundation feature — all other EPIC-046 features (B, C) depend on the template being updated first.

## User Stories

- **US-1:** As an AI agent creating a new task-based skill, I want the skill template to have a 5-phase backbone so that every new skill inherently includes study, inquiry, reflection, discernment, and execution phases.
- **US-2:** As a skill creator, I want clear guidance on how to map my skill's steps to the 5 phases so that I can organize my skill correctly.
- **US-3:** As a skill creator, I want a skip pattern for non-applicable phases so that simple skills don't have artificial complexity but still acknowledge the complete cycle.

## Acceptance Criteria

### AC Group 1: Template Phase Structure

- **AC-1.1:** The template Execution Procedure section MUST contain all 5 `<phase_N>` blocks in strict order:
  - `<phase_1 name="博学之 — Study Broadly">`
  - `<phase_2 name="审问之 — Inquire Thoroughly">`
  - `<phase_3 name="慎思之 — Think Carefully">`
  - `<phase_4 name="明辨之 — Discern Clearly">`
  - `<phase_5 name="笃行之 — Practice Earnestly">`
- **AC-1.2:** Each `<phase_N>` block MUST contain either `<step_N_M>` sub-elements OR a `<skip reason="..." />` element.
- **AC-1.3:** Steps within phases MUST use the numbering format `step_N_M` where N is the phase number and M is the step within that phase (e.g., `step_1_1`, `step_1_2`, `step_2_1`).

### AC Group 2: Template Execution Flow Table

- **AC-2.1:** The Execution Flow table MUST have a Phase column as the first column.
- **AC-2.2:** The table format MUST be: `| Phase | Step | Name | Action | Gate |`
- **AC-2.3:** Skipped phases MUST appear as a row with `—` in Step, `SKIP` in Name, the reason in Action, and `—` in Gate.
- **AC-2.4:** Phase names in the table MUST include both Chinese and English (e.g., `1. 博学之 (Study Broadly)`).

### AC Group 3: Skip Pattern

- **AC-3.1:** The template MUST contain at least one example of a skip pattern: `<skip reason="..." />`.
- **AC-3.2:** The template MUST document common skip reasons:
  - Phase 2 skip: "Input is fully specified by upstream skill; no ambiguity to resolve"
  - Phase 3 skip: "No design decisions or trade-offs; purely procedural execution"
  - Phase 4 skip: "Single valid approach; no alternatives to evaluate"
- **AC-3.3:** Phase 1 (博学之) and Phase 5 (笃行之) MUST NOT have skip examples (these should always have content).

### AC Group 4: Preserved Template Elements

- **AC-4.1:** The Section Order MUST remain: CONTEXT → DECISION → ACTION → VERIFY → REFERENCE.
- **AC-4.2:** Input Parameters section MUST be unchanged (including `process_preference.auto_proceed`).
- **AC-4.3:** Definition of Ready, Definition of Done, Output Result sections MUST be structurally unchanged.
- **AC-4.4:** The mode-aware completion pattern MUST be preserved in the final step of Phase 5.
- **AC-4.5:** The `<execute_dor_checks_before_starting/>` and `<schedule_dod_checks_with_sub_agent_before_starting/>` elements MUST remain at the top of the procedure.

### AC Group 5: Phase Definitions

- **AC-5.1:** The template MUST include a Phase Definitions table with all 5 phases, their Chinese name, English name, and SE purpose.
- **AC-5.2:** Each phase definition MUST describe typical activities for that phase.

### AC Group 6: Skill-Creator Guidelines

- **AC-6.1:** The skill-creator's SKILL.md or guidelines MUST reference the 5-phase method as the mandatory backbone for task-based skills.
- **AC-6.2:** The guidelines MUST provide mapping guidance: how to assign existing steps to the correct phase.

### AC Group 7: Template Usability

- **AC-7.1:** The template body MUST stay under 500 lines.
- **AC-7.2:** Template Usage Notes section MUST be updated to reference the phase-based structure.
- **AC-7.3:** The Category Values table MUST be preserved.

## Functional Requirements

**FR-1: Replace Flat Step Structure with Phase Hierarchy**

Replace the current `<step_1>`, `<step_2>`, ..., `<step_N>` flat structure in the Execution Procedure section with:

```xml
<phase_1 name="博学之 — Study Broadly">
  <step_1_1>
    <name>{Step Name}</name>
    <action>...</action>
    <output>...</output>
  </step_1_1>
</phase_1>
```

Input: Current flat template with `<step_N>` elements.
Output: Template with `<phase_N>` → `<step_N_M>` hierarchy.

**FR-2: Update Execution Flow Table Format**

Replace the current table:
```
| Step | Name | Action | Gate |
```
With phase-based table:
```
| Phase | Step | Name | Action | Gate |
```

**FR-3: Add Phase Definitions Section**

Add a Phase Definitions table after the Execution Flow table:

| Phase | Chinese | English | SE Purpose | Typical Activities |
|-------|---------|---------|------------|-------------------|
| 1 | 博学之 | Study Broadly | Gather comprehensive context | Read specs, study domain, research patterns |
| 2 | 审问之 | Inquire Thoroughly | Question assumptions | Ask questions, challenge inputs, probe gaps |
| 3 | 慎思之 | Think Carefully | Reflect on trade-offs | Analyze risks, evaluate alternatives |
| 4 | 明辨之 | Discern Clearly | Make informed decisions | Choose approach, document rationale |
| 5 | 笃行之 | Practice Earnestly | Execute with discipline | Implement, test, verify, commit |

**FR-4: Add Skip Pattern Documentation**

Add skip pattern with XML syntax and 3 common skip reasons to the template.

**FR-5: Update Step Numbering Convention**

Change from `step_N` to `step_N_M` (phase.step format) throughout the template.

**FR-6: Update Skill-Creator Guidelines**

Add a section to the skill-creator's documentation that:
- Explains the 5-phase method origin and rationale
- Provides phase-mapping guidance for skill creators
- Lists phase 1 and phase 5 as mandatory (never skip)

**FR-7: Preserve Existing Elements**

All existing template elements outside the ACTION section must remain unchanged:
- Input Parameters, Input Initialization (with process_preference)
- Definition of Ready (XML checkpoints)
- Output Result (YAML)
- Definition of Done (XML checkpoints)
- Patterns & Anti-Patterns, Examples
- Template Usage Notes, Format Standards, Category Values

## Non-Functional Requirements

- **NFR-1:** Template body MUST stay under 500 lines.
- **NFR-2:** Phase names MUST always include both Chinese and English.
- **NFR-3:** Template must be backward-compatible — skills using the old flat structure should not break if they haven't been migrated yet (template is guidance, not enforcement).

## UI/UX Requirements

N/A — this feature modifies markdown templates, not UI components.

## Dependencies

- **Internal:** None — this is the foundation feature.
- **External:** EPIC-044 (process_preference changes) already merged — template preserves these.

## Business Rules

- **BR-1:** Phase 1 (博学之) and Phase 5 (笃行之) MUST always have content — they are never skippable.
- **BR-2:** Phases 2, 3, 4 may be skipped with explicit `<skip reason="..." />`.
- **BR-3:** All 5 phases MUST appear in every skill, even if skipped.
- **BR-4:** Phase order is fixed: 1→2→3→4→5. No reordering permitted.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Skill has only 2 steps (simple utility) | Phase 1 gets step 1, Phase 5 gets step 2. Phases 2-4 all SKIP. |
| Skill has 15+ steps (complex) | Distribute across phases; multiple steps per phase allowed. |
| Step doesn't clearly fit one phase | Default to Phase 5 (笃行之) for action-oriented steps. |
| auto_proceed in Phase 2 | Agent self-resolves via decision-making tool, does not skip phase. |

## Out of Scope

- Restructuring individual skills — that's FEATURE-046-B and FEATURE-046-C.
- Modifying non-task-based skill templates (tool skills, meta skills, workflow-orchestration).
- Changing the Section Order (CONTEXT → DECISION → ACTION → VERIFY → REFERENCE).
- Modifying Input Parameters, DoR, DoD, or Output Result structures.

## Technical Considerations

- The template file is at `.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-task-based.md`.
- Changes must go through the candidate workflow per skill-creator rules (edit in `x-ipe-docs/skill-meta/` first, then merge).
- Guidelines updates may touch `.github/skills/x-ipe-meta-skill-creator/SKILL.md` and/or `references/skill-general-guidelines-v2.md`.
- The template's Template Usage Notes section documents the section order — this must be updated to reflect phase-based structure in the ACTION section.

## Open Questions

None — all clarified during ideation and requirement gathering.
