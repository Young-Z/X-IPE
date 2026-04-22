# Feature Specification: Knowledge & Assistant Skill Type Infrastructure

> Feature ID: FEATURE-059-A
> Epic ID: EPIC-059
> Version: v1.0
> Status: Refined
> Last Updated: 04-15-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-15-2026 | Initial specification |
| v1.1 | 04-16-2026 | CR-001: Add `skill-meta-x-ipe-knowledge.md` template (moved from Out of Scope to in-scope) |

## Linked Mockups

_No mockups applicable for this feature — infrastructure/template work only._

## Overview

This feature extends the X-IPE skill creation infrastructure to support two new skill types: **knowledge** and **assistant**. Knowledge skills follow a hybrid **Operations + Steps** structure where each operation is the primary unit of work, and phases (博学之→笃行之) provide internal structure within each operation. This design enables assistant orchestrators (e.g., `x-ipe-assistant-knowledge-librarian-DAO`) to call individual operations as stateless services while maintaining the familiar cognitive flow inside each operation. Assistant skills replace the current "dao" type with a renamed namespace (`x-ipe-assistant-*`) using the same 格物致知 backbone.

The feature also updates `x-ipe-meta-skill-creator` to recognize these new types, updates custom instructions so that `x-ipe-knowledge-*` and `x-ipe-assistant-*` skills are auto-discovered, and creates a comparison reference document covering all skill types. The existing "dao" type is immediately deprecated with an alias redirect to "assistant".

This is the **Layer 0 prerequisite** — no new knowledge or assistant skill can be created until these templates and tooling updates are in place. All subsequent EPIC-059 features depend on this.

## User Stories

1. As a **skill author**, I want to create a new knowledge skill using `x-ipe-meta-skill-creator` with a "knowledge" type, so that I get a properly structured SKILL.md with Operations + Steps sections and don't have to build the template from scratch.

2. As a **skill author**, I want to create a new assistant skill using `x-ipe-meta-skill-creator` with an "assistant" type, so that I get a properly structured SKILL.md with orchestration procedure (格物致知 backbone) without using the deprecated "dao" type.

3. As an **AI agent**, I want the custom instructions to auto-discover `x-ipe-knowledge-*` and `x-ipe-assistant-*` skills, so that knowledge-related work is routed to the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) and assistant skills are available in the skills registry.

4. As a **contributor**, I want a skill type comparison reference document, so that I can quickly understand the structural, invocation, and state model differences between all skill types when deciding which type to use for a new skill.

5. As a **skill author using the deprecated "dao" type**, I want `x-ipe-meta-skill-creator` to recognize "dao" as a deprecated alias for "assistant" and warn me, so that existing workflows don't break but I'm guided to use the new type.

## Acceptance Criteria

### AC-059A-01: Knowledge Skill Template

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059A-01a | GIVEN the templates folder `.github/skills/x-ipe-meta-skill-creator/templates/` WHEN listing files THEN `x-ipe-knowledge.md` exists | Unit |
| AC-059A-01b | GIVEN the knowledge template WHEN reading its content THEN it contains an `## Operations` section with at least one example operation block | Unit |
| AC-059A-01c | GIVEN the knowledge template WHEN reading an operation block THEN it defines `name`, `description`, `input` (typed params), `output` (typed results), `steps[]`, `writes_to`, and `constraints[]` fields | Unit |
| AC-059A-01d | GIVEN the knowledge template WHEN reading an operation's steps THEN each operation internally follows the phase structure (博学之→笃行之) as sub-sections within the operation | Unit |
| AC-059A-01e | GIVEN the knowledge template WHEN reading its content THEN it includes an `## Important Notes` section with the constraint "Operations are stateless services — the assistant orchestrator passes full context per call" | Unit |

### AC-059A-02: Assistant Skill Template

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059A-02a | GIVEN the templates folder `.github/skills/x-ipe-meta-skill-creator/templates/` WHEN listing files THEN `x-ipe-assistant.md` exists AND `skill-meta-x-ipe-assistant.md` exists | Unit |
| AC-059A-02b | GIVEN the assistant template WHEN comparing structure to the existing `x-ipe-dao.md` template THEN it follows the same 格物致知 backbone (格物 → 致知 phases) with namespace changed from `x-ipe-dao-{name}` to `x-ipe-assistant-{name}` | Unit |
| AC-059A-02c | GIVEN the assistant template WHEN reading the frontmatter THEN the `name` field uses pattern `x-ipe-assistant-{name}` | Unit |
| AC-059A-02d | GIVEN the `skill-meta-x-ipe-assistant.md` template WHEN comparing to `skill-meta-x-ipe-dao.md` THEN it follows the same structure with namespace updated | Unit |

### AC-059A-03: Skill Creator SKILL.md Update

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059A-03a | GIVEN `x-ipe-meta-skill-creator` SKILL.md WHEN reading the skill type enum THEN it includes `x-ipe-knowledge` and `x-ipe-assistant` as valid types | Unit |
| AC-059A-03b | GIVEN `x-ipe-meta-skill-creator` SKILL.md WHEN reading the skill type table THEN it lists "knowledge" and "assistant" rows with correct template paths and naming conventions | Unit |
| AC-059A-03c | GIVEN `x-ipe-meta-skill-creator` SKILL.md WHEN reading the type selection logic THEN "knowledge" type maps to `templates/x-ipe-knowledge.md` AND "assistant" maps to `templates/x-ipe-assistant.md` | Unit |
| AC-059A-03d | GIVEN `x-ipe-meta-skill-creator` SKILL.md WHEN a user selects skill type "dao" THEN the skill warns that "dao" is deprecated and redirects to "assistant" type | Unit |
| AC-059A-03e | GIVEN `x-ipe-meta-skill-creator` SKILL.md WHEN reading the total skill type count THEN it shows 8 types (task-based, task-category, tool, workflow-orchestration, meta, dao [deprecated], knowledge, assistant) | Unit |

### AC-059A-04: Custom Instructions Update

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059A-04a | GIVEN `copilot-instructions.md` WHEN reading the auto-discovery section THEN it includes a note that `x-ipe-knowledge-*` skills are coordinated by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) and not directly task-matched | Unit |
| AC-059A-04b | GIVEN `copilot-instructions.md` WHEN reading the auto-discovery section THEN `x-ipe-assistant-*` skills are included in the scan patterns alongside `x-ipe-task-based-*` | Unit |
| AC-059A-04c | GIVEN `copilot-instructions.md` WHEN reading the skill matching logic THEN existing `x-ipe-task-based-*`, `x-ipe-tool-*`, and `x-ipe-dao-*` patterns still work (backward compatible) | Unit |

### AC-059A-05: Skill Type Comparison Document

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059A-05a | GIVEN the references folder `.github/skills/x-ipe-meta-skill-creator/references/` WHEN listing files THEN `skill-type-comparison.md` exists | Unit |
| AC-059A-05b | GIVEN the comparison document WHEN reading its content THEN it contains a comparison table with columns: Skill Type, Structure, Caller, State Model, When to Use — covering all 4 active types (task-based, tool, knowledge, assistant) | Unit |
| AC-059A-05c | GIVEN the comparison document WHEN reading the knowledge row THEN it describes "Operations + Steps (phases inside each operation)" as the structure AND "Assistant orchestrator (e.g., Knowledge Librarian)" as the caller AND "External — orchestrator passes context per call" as the state model | Unit |
| AC-059A-05d | GIVEN the comparison document WHEN reading its content THEN it includes a "dao (deprecated)" note referencing assistant as the replacement | Unit |
| AC-059A-05e | GIVEN the comparison document WHEN reading its content THEN it includes per-type sections with: structural overview, invocation model, state management, when-to-use guidance, and an example skill name | Unit |

### AC-059A-06: DAO Deprecation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059A-06a | GIVEN `x-ipe-meta-skill-creator` SKILL.md WHEN the type selection step encounters "dao" THEN it displays a deprecation warning AND automatically maps to "assistant" type | Unit |
| AC-059A-06b | GIVEN the existing `x-ipe-dao.md` template WHEN it is still present THEN it contains a deprecation header pointing to `x-ipe-assistant.md` as the replacement | Unit |

### AC-059A-07: Smoke Tests

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059A-07a | GIVEN `x-ipe-meta-skill-creator` is loaded WHEN an agent requests to create a skill of type "knowledge" with name "test-knowledge-skill" THEN the output SKILL.md contains `## Operations` section with operation contract structure (name, description, input, output, steps, writes_to, constraints) | Integration |
| AC-059A-07b | GIVEN `x-ipe-meta-skill-creator` is loaded WHEN an agent requests to create a skill of type "assistant" with name "test-assistant-skill" THEN the output SKILL.md contains 格物致知 backbone sections AND uses `x-ipe-assistant-test-assistant-skill` as the skill name | Integration |

## Functional Requirements

### FR-1: Knowledge Skill Template

**Description:** Create a Markdown template for knowledge-type skills that uses the Operations + Steps hybrid structure.

**Details:**
- Input: Template name `x-ipe-knowledge.md`, placed in `.github/skills/x-ipe-meta-skill-creator/templates/`
- Process: Template defines the standard skeleton for knowledge skills — operations as primary sections, with phases (博学之→笃行之) as internal structure within each operation
- Output: A reusable template that skill-creator uses when `skill_type == "x-ipe-knowledge"`

**Key sections the template must include:**
- Frontmatter with `name: x-ipe-knowledge-{sub-category}-{name}` pattern
- Purpose, Important Notes, About, When to Use
- Operations section with example operation contract (name, description, input, output, steps with phase structure, writes_to, constraints)
- Output Result, Definition of Done
- Error Handling

### FR-2: Assistant Skill Template

**Description:** Create a Markdown template for assistant-type skills that mirrors the existing DAO template with namespace rename.

**Details:**
- Input: Template name `x-ipe-assistant.md` + `skill-meta-x-ipe-assistant.md`
- Process: Copy existing `x-ipe-dao.md` structure, rename `x-ipe-dao-{name}` → `x-ipe-assistant-{name}`, update all internal references
- Output: Template pair (SKILL.md + skill-meta) for assistant type

### FR-3: Skill Creator Update

**Description:** Update `x-ipe-meta-skill-creator` SKILL.md to recognize "knowledge" and "assistant" as valid types.

**Details:**
- Input: Existing SKILL.md at `.github/skills/x-ipe-meta-skill-creator/SKILL.md`
- Process: Add "knowledge" and "assistant" to the skill type enum, type table, and type selection logic. Add "dao" as deprecated alias for "assistant" with warning
- Output: Updated SKILL.md that routes to correct templates for all 8 types

### FR-4: Custom Instructions Update

**Description:** Update `copilot-instructions.md` auto-discovery to include new skill namespaces.

**Details:**
- Input: Existing `.github/copilot-instructions.md`
- Process: Add `x-ipe-assistant-*` to scan patterns. Add note that `x-ipe-knowledge-*` skills are coordinated by the Knowledge Librarian assistant (not directly task-matched). Maintain backward compatibility with existing patterns
- Output: Updated custom instructions enabling auto-discovery of new skill types

### FR-5: Skill Type Comparison Document

**Description:** Create a reference document comparing all skill types.

**Details:**
- Input: Knowledge from idea summary Section 1c and the skill type comparison table
- Process: Create comprehensive comparison covering structure, invocation model, state model, and when-to-use guidance for each type
- Output: `.github/skills/x-ipe-meta-skill-creator/references/skill-type-comparison.md`

### FR-6: DAO Type Deprecation

**Description:** Mark the "dao" skill type as deprecated with alias redirect to "assistant".

**Details:**
- Input: Existing `x-ipe-dao.md` template and skill-creator SKILL.md
- Process: Add deprecation header to `x-ipe-dao.md`, update skill-creator to warn and redirect "dao" → "assistant"
- Output: Deprecated "dao" type that still works but warns and redirects

## Non-Functional Requirements

### NFR-1: Backward Compatibility
- All existing `x-ipe-dao-*` skills continue to work without modification
- Existing `x-ipe-task-based-*` and `x-ipe-tool-*` auto-discovery is unaffected
- The deprecated "dao" type still produces valid output (maps to assistant template)

### NFR-2: Template Consistency
- Knowledge template follows the same structural conventions as other templates (frontmatter, Purpose, Important Notes, etc.)
- Assistant template maintains structural parity with DAO template — only namespace changes

### NFR-3: Documentation Quality
- Comparison document is self-contained — a contributor can understand all types without reading other files
- Templates include sufficient inline comments and examples for first-time authors

## UI/UX Requirements

_Not applicable — this feature involves only Markdown templates and documentation._

## Dependencies

### Internal Dependencies
- **EPIC-044 (Skill Creator):** The existing `x-ipe-meta-skill-creator` infrastructure must be functional — this feature extends it
- **EPIC-041 (Custom Instructions):** The `copilot-instructions.md` auto-discovery mechanism must exist

### External Dependencies
- None

## Business Rules

- BR-1: Knowledge skills MUST use Operations + Steps as primary structure with phases inside each operation — they are stateless services called by assistant orchestrators (e.g., `x-ipe-assistant-knowledge-librarian-DAO`)
- BR-2: Assistant skills are structurally identical to DAO skills — only the namespace changes
- BR-3: The "dao" type is deprecated immediately — selecting "dao" in skill-creator warns and redirects to "assistant"
- BR-4: Knowledge skills are NOT directly task-matched — the Knowledge Librarian assistant routes to them. Custom instructions should reflect this
- BR-5: All template changes go through the candidate folder workflow (`x-ipe-docs/skill-meta/*/candidate/`) before merging to production

## Edge Cases & Constraints

### Edge Case 1: Skill author selects deprecated "dao" type
**Scenario:** A skill author runs skill-creator and selects "dao" as the type.
**Expected Behavior:** Skill-creator displays a deprecation warning message and automatically uses the "assistant" template instead. The created skill uses `x-ipe-assistant-{name}` naming.

### Edge Case 2: Existing x-ipe-dao-* skills in auto-discovery
**Scenario:** The system has existing `x-ipe-dao-*` skills that haven't been migrated yet.
**Expected Behavior:** These skills continue to be discovered and functional. The custom instructions maintain backward-compatible patterns for `x-ipe-dao-*`.

### Edge Case 3: Knowledge skill created with no operations defined
**Scenario:** A skill author creates a knowledge skill but removes all example operations.
**Expected Behavior:** The template includes a clear comment stating at least one operation is required, but no validation blocks creation — the author is responsible for adding operations.

## Out of Scope

- Actual knowledge skills (extractor, constructor, keeper, etc.) — those are Layer 1+ features (FEATURE-059-B through 059-E)
- Memory folder structure creation — Layer 1 (FEATURE-059-B)
- Ontology model schema/data files — Layer 2 (FEATURE-059-C)
- Migration of existing `x-ipe-dao-*` skills to `x-ipe-assistant-*` namespace — Layer 5 (FEATURE-059-F)
- Web application changes — Layer 5 (FEATURE-059-F)
- Skill-meta template for knowledge type (`skill-meta-x-ipe-knowledge.md`) — ~~if needed, add in a follow-up~~ Added via [CR-001](./CR-001.md)

## Technical Considerations

- The knowledge template's hybrid structure (Operations as primary, phases inside each operation) resolves the contradiction between Section 1c (Operations + Steps) and line 646 (博学之 phase backbone) of the idea summary
- Each operation in a knowledge skill should define its own input/output contract so the assistant orchestrator can call operations independently
- The `writes_to` field in each operation enables the orchestrator to understand side effects before calling
- The assistant template is a namespace rename of the existing dao template — structural divergence (if any) should be deferred to future iterations
- Custom instructions should add `x-ipe-assistant-*` to scan patterns but note that `x-ipe-knowledge-*` are coordinated by the Knowledge Librarian assistant (not directly available for task matching)

## Open Questions

_None — all questions resolved during refinement._
