# FEATURE-047-C: Instruction Resource DAO Interception

> **Version:** v1.0
> **Status:** In Refinement
> **Epic:** EPIC-047
> **Depends On:** FEATURE-047-B (Completed)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 03-06-2026 | Initial specification from requirement-details-part-19.md (FR-047.26–28, HLR-047.9) |

---

## Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| N/A | No mockups — text-only instruction files |

---

## Overview

FEATURE-047-C updates the instruction resources that define how AI agents interpret and route human messages. After FEATURE-047-B migrated all skill-level call sites to DAO, the instruction resources still lack guidance about DAO as the human representative interception layer for `auto` mode.

This feature:
1. Adds DAO interception guidance to `.github/copilot-instructions.md` (repo-local)
2. Syncs the packaged instruction resources (`src/x_ipe/resources/copilot-instructions-en.md` and `-zh.md`) with the repo-local version
3. Ensures DAO is described as bounded — it represents human intent, not task execution

---

## User Stories

### US-1: As an AI agent reading instructions, I want to know that DAO handles human-origin decision points in auto mode.

**Acceptance Criteria:**

- [ ] AC-047-C.1: `.github/copilot-instructions.md` describes DAO (`x-ipe-assistant-user-representative-Engineer`) as the human representative interception layer for `auto` mode decision points.
- [ ] AC-047-C.2: The instruction explains that in `auto` mode, when a skill hits a human-required touchpoint, it calls `x-ipe-assistant-user-representative-Engineer` instead of asking the human.
- [ ] AC-047-C.3: The instruction clarifies that `manual` and `stop_for_question` modes still ask the human directly — DAO is NOT invoked.
- [ ] AC-047-C.4: The instruction states DAO is bounded — it represents human intent but does not execute tasks or make architectural decisions.

### US-2: As a project maintainer, I want packaged and repo-local instructions to be consistent.

**Acceptance Criteria:**

- [ ] AC-047-C.5: `src/x_ipe/resources/copilot-instructions-en.md` is synced with `.github/copilot-instructions.md` (same content for shared sections).
- [ ] AC-047-C.6: `src/x_ipe/resources/copilot-instructions-zh.md` is updated with the equivalent DAO interception guidance in Chinese.
- [ ] AC-047-C.7: The packaged English version uses `process_preference.auto_proceed` (not the stale `require_human_review`).

### US-3: As a skill author, I want the instruction template updated so new projects get DAO guidance.

**Acceptance Criteria:**

- [ ] AC-047-C.8: If an instructions template exists (`src/x_ipe/resources/templates/instructions-template.md` or similar), it includes DAO interception guidance.

---

## Functional Requirements

- **FR-047-C.1:** (FR-047.26) Instruction resources MUST describe DAO as the human representative interception layer for `auto` mode.
- **FR-047-C.2:** (FR-047.27) Packaged instruction resources MUST be consistent with repo-local.
- **FR-047-C.3:** (FR-047.28) DAO interception MUST be described as bounded — mediates human-origin meaning only.
- **FR-047-C.4:** The DAO section in instructions MUST NOT mention internal backbone (道/7-step) — keep it external-facing.
- **FR-047-C.5:** Instructions MUST reference `x-ipe-assistant-user-representative-Engineer` by name for auto-mode resolution.

---

## Non-Functional Requirements

- **NFR-047-C.1:** Instruction files should remain concise and scannable by AI agents.
- **NFR-047-C.2:** No breaking changes to existing instruction structure.

---

## Dependencies

### Internal
- **FEATURE-047-B** (Completed) — All skill call sites already migrated to DAO
- **FEATURE-047-A** (Completed) — DAO skill exists with message_context contract

### External
- None

---

## Business Rules

- **BR-047-C.1:** DAO is described using "human representative" terminology (per CR-001 naming convention).
- **BR-047-C.2:** Instructions MUST NOT expose internal 道 backbone or Chinese philosophical terms.

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| New project scaffolded after this feature | Gets DAO guidance in generated instructions |
| Existing project without DAO guidance | Human must re-scaffold or manually update |

---

## Out of Scope

- Updating `copilot-prompt.json` workflow prompts (separate concern)
- Updating historical requirement docs or idea files
- Adding DAO to the skill auto-discovery section (DAO is a tool skill, not task-based)
- Changes to DAO skill itself (done in 047-A/047-B)
