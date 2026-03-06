# Feature Specification: DAO Skill Foundation & End-User Core

> Feature ID: FEATURE-047-A
> Epic ID: EPIC-047
> Version: v2.1
> Status: Refined
> Last Updated: 03-06-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-06-2026 | Initial specification |
| v1.1 | 03-06-2026 | [CR-001](./CR-001.md): Avoid "DAO" in external descriptions; position 道 as internal CORE backbone; fix AC-047-A.6 template backbone |
| v2.0 | 03-06-2026 | Specification refinement per CR-001: renamed "human-proxy" to "human representative" throughout; added AC-047-A.21 for naming convention; aligned terminology with implemented skill artifacts |
| v2.1 | 03-06-2026 | Input contract redesigned: removed operation field; mediation_request→message_context with source/messages; human_shadow standalone; confidence_threshold internal; "mediate" prose→"represent human intent" |

## Linked Mockups

No mockups — this feature defines skill contracts and behavior, not a UI surface.

## Overview

FEATURE-047-A delivers the minimum runnable human representative capability for X-IPE. It introduces a new skill type (`x-ipe-dao`) in the skill-creator system and defines `x-ipe-dao-end-user-representative` as the first concrete human representative skill that can stand in for human-origin guidance without expanding downstream task scope.

The 道 (DAO) concept serves as the **internal CORE backbone** — a structured 7-step cognitive reasoning methodology rooted in Chinese philosophical tradition — that shapes how these skills evaluate context and select dispositions. Externally, the skills are described using universally understood language (e.g., "human representative", "guidance on behalf of the human") to avoid misinterpretation by users unfamiliar with Chinese cultural context.

This feature is needed because the existing `x-ipe-tool-decision-making` concept is too narrow for the broader human-representative role X-IPE now requires. The skill must handle more than binary decisions: it needs to support clarification, critique, approval-like guidance, reframing, and pass-through behavior while remaining bounded, auditable, and compatible with the existing `process_preference.auto_proceed` workflow model.

The primary users are X-IPE maintainers creating human representative skills, calling skills and workflows that need human-like guidance, and human operators who want autonomous default behavior with optional human-shadow fallback.

## User Stories

- **US-1:** As a skill creator, I want a dedicated skill type (`x-ipe-dao`) so that I can create human representative skills using the standard X-IPE workflow instead of ad hoc conventions.
- **US-2:** As a calling skill or workflow, I want `x-ipe-dao-end-user-representative` to return bounded human-like guidance so that blocked human-required touchpoints can continue without changing downstream task scope.
- **US-3:** As a maintainer, I want human representative skills to preserve existing `manual`, `stop_for_question`, and `auto` workflow semantics so that introducing them does not break current execution policy.
- **US-4:** As a human operator, I want optional human-shadow fallback for ambiguous cases so that the skill can escalate when confidence is low without becoming human-dependent by default.
- **US-5:** As a future implementer, I want explicit extension points for reusable memory so that later versions can add experience support without redesigning the v1 contract.
- **US-6:** As a non-Chinese-culture contributor, I want external-facing skill descriptions to use universally understood language so that I can understand and use the skills without needing background in Chinese philosophy.

## Acceptance Criteria

### AC Group 1: Skill Type Support

- [ ] **AC-047-A.1:** `x-ipe-meta-skill-creator` supports `x-ipe-dao` as a selectable skill type in the same creation flow used for other supported skill categories.
- [ ] **AC-047-A.2:** Skill creation produces a valid artifact structure with a main `SKILL.md` and any required support folders or reference files defined by the template.
- [ ] **AC-047-A.3:** Skill-type guidance explicitly states that `x-ipe-dao` skills act as human representatives and are not general-purpose implementation skills.
- [ ] **AC-047-A.4:** Skill-type guidance explicitly states that `x-ipe-dao` skills may replace human-required touchpoints but must not expand the downstream task's scope of work.

### AC Group 2: Template Contract

- [ ] **AC-047-A.5:** The template includes required sections for human representative scope, bounded outputs, autonomous default behavior, optional human-shadow fallback, semantic logging expectations, and future memory extension hooks.
- [ ] **AC-047-A.6:** The template embeds the Chinese 7-step backbone (道 CORE) in this exact order: 静虑, 兼听, 审势, 权衡, 谋后而定, 试错, 断.
- [ ] **AC-047-A.7:** Template guidance states that the skill returns guidance on behalf of the human only and must not expose full inner reasoning to the calling agent.
- [ ] **AC-047-A.8:** Template guidance allows question-form, feedback-form, and instruction-form human-origin inputs without forcing all input into a declarative command shape.

### AC Group 3: `x-ipe-dao-end-user-representative` Core Behavior

- [ ] **AC-047-A.9:** `.github/skills/x-ipe-dao-end-user-representative/SKILL.md` exists as the first concrete human representative skill.
- [ ] **AC-047-A.10:** `x-ipe-dao-end-user-representative` accepts human-origin context and returns one bounded disposition from the supported set: direct answer, clarification, reframing, critique, instruction, approval-like guidance, or pass-through.
- [ ] **AC-047-A.11:** `x-ipe-dao-end-user-representative` can pass the user's original question or intent through to the downstream AI agent when the skill determines that specialist handling is the most human-like response.
- [ ] **AC-047-A.12:** `x-ipe-dao-end-user-representative` does not claim ownership of downstream implementation work after returning guidance.
- [ ] **AC-047-A.13:** `x-ipe-dao-end-user-representative` treats the initial human message as valid input without requiring a separate pre-normalization step by the caller.

### AC Group 4: Workflow Compatibility and Human-Shadow

- [ ] **AC-047-A.14:** The skill is autonomous by default when no override is present.
- [ ] **AC-047-A.15:** The skill supports an optional human-shadow mode that is only used for fallback when low confidence, ambiguity, or policy requires real-human escalation.
- [ ] **AC-047-A.16:** The skill preserves the existing `process_preference.auto_proceed` contract for `manual`, `stop_for_question`, and `auto` modes rather than replacing it with skill-specific execution modes.
- [ ] **AC-047-A.17:** The skill's behavior remains bounded so that non-auto workflow states are not silently converted into autonomous execution.

### AC Group 5: Boundaries and Future Extension

- [ ] **AC-047-A.18:** FEATURE-047-A defines future memory or experience as extension hooks only and does not require reusable cross-task memory persistence in v1.
- [ ] **AC-047-A.19:** FEATURE-047-A documents the migration boundary clearly: semantic logging, legacy log removal, workflow-wide call-site migration, and instruction-resource interception are excluded from this feature.
- [ ] **AC-047-A.20:** All acceptance criteria in this specification are specific enough to be verified by document review, skill-file inspection, or automated tests added during implementation.

### AC Group 6: Naming and Terminology Convention

- [ ] **AC-047-A.21:** External-facing descriptions (frontmatter `description`, skill titles, template guidance, inter-skill documentation) use universally understood language such as "human representative" rather than "DAO" or "道" directly.
- [ ] **AC-047-A.22:** 道 (DAO) is explicitly positioned as the **internal CORE backbone** within skill bodies — the reasoning methodology — and is not the primary term used in external-facing surfaces.
- [ ] **AC-047-A.23:** Skill type identifiers (`x-ipe-dao`, `x-ipe-dao-{name}`) and directory names remain unchanged; only descriptions and documentation language are affected by the naming convention.

## Functional Requirements

### FR-047-A.1: Skill Type Enablement

The system must add `x-ipe-dao` as a supported skill type within `x-ipe-meta-skill-creator`.

- **Input:** Skill-creation request for a human representative skill.
- **Process:** Recognize `x-ipe-dao` as a valid type, route the request through the dedicated template and guidance material, and enforce structural expectations.
- **Output:** A valid skill skeleton or candidate artifact set ready for refinement and later implementation.

### FR-047-A.2: Template and Guidance Contract

The template and its companion guidance must define the minimum contract for human representative skills.

- **Input:** Skill-creation flow and template selection for the `x-ipe-dao` type.
- **Process:** Provide required sections covering human representative scope, bounded outputs, human-shadow fallback, semantic logging expectations, the 道 CORE backbone, and future memory extension points.
- **Output:** A skill definition that consistently describes what the skill is allowed to do and what it must not do.

### FR-047-A.3: Chinese 7-Step Backbone (道 CORE)

The template must include the 7-step decision backbone as the normative internal cognitive structure for human representative reasoning.

- **Input:** Template or skill definition for `x-ipe-dao` type.
- **Process:** Present the ordered backbone steps (静虑→兼听→审势→权衡→谋后而定→试错→断) and explain that the skill uses them to shape internal reasoning and rationale summaries.
- **Output:** Artifacts that consistently encode the same 7-step pattern across future human representative skills.

### FR-047-A.4: `x-ipe-dao-end-user-representative` Core Skill

The system must create `x-ipe-dao-end-user-representative` as the first concrete human representative implementation.

- **Input:** Human-origin message or human-required touchpoint context from a calling workflow or skill.
- **Process:** Evaluate context using the 道 CORE backbone, choose an allowed disposition, and return only bounded guidance on behalf of the human.
- **Output:** A response that helps the caller proceed without exposing chain-of-thought or absorbing downstream task implementation work.

### FR-047-A.5: Human Representative Disposition Support

`x-ipe-dao-end-user-representative` must support multiple human representative dispositions.

- **Input:** Human-origin message, calling context, and workflow policy context.
- **Process:** Determine whether the most appropriate response is a direct answer, clarification, reframing, critique, instruction, approval-like guidance, or pass-through.
- **Output:** A single bounded guidance result appropriate for the current context.

### FR-047-A.6: Workflow Semantics Preservation

The skill must integrate with the current `process_preference.auto_proceed` contract instead of overriding it.

- **Input:** Calling workflow or skill mode (`manual`, `stop_for_question`, or `auto`) plus invocation context.
- **Process:** Respect existing execution policy while allowing the skill to represent human intent and, where policy allows, handle human-required touchpoints.
- **Output:** Behavior that preserves current workflow expectations.

### FR-047-A.7: Human-Shadow Fallback

The skill must support optional human-shadow escalation without becoming dependent on a real human in normal execution.

- **Input:** Invocation with ambiguity, low confidence, or explicit shadow-mode enablement.
- **Process:** Decide whether to return an autonomous best-effort result or request real-human fallback according to configured policy.
- **Output:** Clear guidance or a bounded fallback request path.

### FR-047-A.8: Future Memory Extension Boundary

The contract must reserve future memory extension points without implementing reusable memory persistence in v1.

- **Input:** Template and skill contract definitions.
- **Process:** Describe extensibility hooks or reserved sections for future memory capabilities while excluding persistent cross-task memory behavior from current delivery.
- **Output:** A forward-compatible v1 specification that does not require memory infrastructure now.

### FR-047-A.9: External-Facing Naming Convention

All external-facing artifacts must use universally understood terminology rather than culturally specific terms.

- **Input:** Skill descriptions, template titles, inter-skill documentation, and creator type-table entries.
- **Process:** Use "human representative" and similar universally understood terms in all surfaces read by callers or skill creators. Reserve 道 (DAO) for internal CORE backbone references within skill bodies.
- **Output:** Consistent, accessible naming across all externally-visible surfaces with 道 clearly positioned as internal reasoning methodology.

## Non-Functional Requirements

- **NFR-047-A.1:** Skill outputs must remain bounded and auditable; the skill must never expose chain-of-thought to the calling agent.
- **NFR-047-A.2:** Skill support must remain backward-compatible with the existing `manual`, `stop_for_question`, and `auto` workflow semantics.
- **NFR-047-A.3:** The template and core-skill contract must use universally understood terminology ("human representative") in external-facing surfaces that clearly distinguishes human representative guidance from downstream implementation work, while reserving 道 as the internal CORE backbone.
- **NFR-047-A.4:** Artifacts created for this feature must be written in a way that future variants can reuse without redefining the 7-step backbone.
- **NFR-047-A.5:** FEATURE-047-A must be implementable without requiring semantic logging rollout or cross-repository instruction-resource updates.

## UI/UX Requirements

Not applicable — this feature defines skill contracts, behavior, and template support rather than end-user interface components.

## Dependencies

### Internal Dependencies

- **EPIC-047 requirement definition:** Provides the approved scope, feature boundaries, and behavior contract for this feature.
- **x-ipe-meta-skill-creator:** Hosts the skill-type selection flow and template support introduced by this feature.

### External Dependencies

- **Existing X-IPE workflow semantics:** The skill must integrate with the established `process_preference.auto_proceed` model from earlier workflow work.
- **Sub-agent execution capability:** `x-ipe-dao-end-user-representative` depends on the runtime's ability to invoke a bounded skill from calling workflows or skills.

## Business Rules

- **BR-047-A.1:** `x-ipe-dao` skills are human representative layers, not general implementation agents.
- **BR-047-A.2:** The skill may replace human-required touchpoints, but it must not expand the downstream task's scope.
- **BR-047-A.3:** The skill is autonomous by default; human-shadow is optional fallback, not the baseline behavior.
- **BR-047-A.4:** The skill may pass a user's original question through unchanged when that is the most appropriate human-like action.
- **BR-047-A.5:** Reusable cross-task memory is not part of FEATURE-047-A delivery.
- **BR-047-A.6:** External-facing descriptions use universally understood language; 道 is internal CORE backbone only.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Human-origin input is a question rather than an instruction | The skill treats the question as valid input and may answer, reframe, or pass it through without forcing instruction conversion first. |
| The skill lacks sufficient context to provide confident guidance | Returns a bounded clarification, pass-through, or human-shadow fallback result instead of inventing implementation details. |
| Calling workflow is `manual` or `stop_for_question` | The skill may still represent human intent, but workflow execution policy must continue to honor the existing non-auto contract. |
| Calling context tries to use the skill as an implementation agent | The contract rejects that expectation and limits itself to guidance on behalf of the human. |
| Future memory design is not yet available | Artifacts keep reserved extension points but remain fully usable without memory persistence. |
| Non-Chinese-culture user reads skill documentation | External descriptions use "human representative" and other universally understood terms; 道 appears only in internal CORE backbone sections with explanation. |

## Out of Scope

- Semantic log file creation under `x-ipe-docs/dao/` and removal of `x-ipe-docs/decision_made_by_ai.md` (FEATURE-047-B).
- Workflow-wide migration of existing `x-ipe-tool-decision-making` call sites (FEATURE-047-B).
- Updating instruction resources in repo-local or packaged assets (FEATURE-047-C).
- Implementing reusable cross-task memory or experience persistence.
- Redesigning downstream task-based skills to change their substantive work scope.
- Renaming skill type identifiers or directory names (the `x-ipe-dao` type ID and `x-ipe-dao-{name}` directory convention are stable).

## Technical Considerations

- The feature should follow the repo's Epic-aware requirements structure and place the specification at `x-ipe-docs/requirements/EPIC-047/FEATURE-047-A/specification.md`.
- Skill-type support should fit the existing skill-creator candidate-to-production workflow rather than inventing a parallel creation path.
- `x-ipe-dao-end-user-representative` should expose a clear input/output contract that later technical design can map to concrete tool or skill invocations.
- Boundaries must remain explicit so later implementation work can separate core skill creation from logging rollout and migration work.
- External-facing descriptions must be reviewed for universally understood language before shipping; any occurrence of "DAO" or "道" in caller-visible surfaces (frontmatter description, template titles, type-table descriptions) should use "human representative" or equivalent plain-language terms instead.

## Open Questions

None — scope, disposition behavior, human-shadow semantics, pass-through behavior, future-memory deferral, and naming convention were clarified during ideation, requirement gathering, and CR-001.
