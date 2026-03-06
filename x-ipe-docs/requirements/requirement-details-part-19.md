# Requirement Details — Part 19

> Part 19 covers: EPIC-047

---

## EPIC-047: DAO End-User Human Proxy Layer

### Project Overview

Create a new standalone Epic that supersedes the decision-making-specific parts of EPIC-044 by introducing a new **DAO (`道`) skill type** and its first concrete skill, **`x-ipe-dao-end-user`**. DAO is a digital-human proxy layer: it stands in for human-origin guidance at points where X-IPE currently requires a human, while preserving the existing `process_preference.auto_proceed` workflow semantics.

Unlike `x-ipe-tool-decision-making`, DAO is not limited to making a decision. It may answer directly, reframe a request, ask a rhetorical or clarifying follow-up, issue an instruction, provide critique or feedback, or pass the original question through to the downstream AI agent when that is the most human-like behavior.

This Epic also replaces the legacy single-file decision log with semantic DAO log files under `x-ipe-docs/dao/`, and removes `x-ipe-docs/decision_made_by_ai.md` once DAO is introduced.

**Source:** [IDEA-033 Refined Summary](x-ipe-docs/ideas/033.%20Feature-'道'%20for%20x-ipe/refined-idea/idea-summary-v1.md)

### User Request

> "Transform the existing decision making skill into a new type skill called 道 / dao (`x-ipe-dao-end-user`) so it behaves like a human proxy. It should intercept human-origin needs, decide whether to answer, reframe, or pass through, support human-shadow mode, later support experience/memory, create DAO-specific logs under x-ipe-docs/dao/, and migrate existing decision-making call sites and instructions to DAO."

### Clarifications

| Question | Answer |
|----------|--------|
| Is DAO only a decision-and-guidance replacement? | No. DAO is a broader human-origin proxy layer that can provide instruction, feedback, critique, clarification, approval-like guidance, or pass-through behavior. |
| Does DAO replace all work done by downstream skills? | No. DAO replaces only places that currently require human input; downstream task scope does not change. |
| Must DAO always answer the incoming message itself? | No. DAO may answer, redirect, reframe, ask a follow-up, or pass the original question to the downstream AI agent if DAO lacks the relevant context. |
| Should DAO have reusable memory in v1? | No. V1 only defines extension points for future experience/memory. |
| What is DAO's default mode? | Autonomous by default; human-shadow is optional and only controls fallback to the real human. |
| Does DAO replace IDEA-031 auto-proceed semantics? | No. Existing `process_preference.auto_proceed` semantics remain valid. |
| What happens to `x-ipe-docs/decision_made_by_ai.md`? | Delete it once DAO is introduced. |
| How are DAO logs organized? | Under `x-ipe-docs/dao/` as `decisions_made_{semantic_task_type}.md`, with DAO deciding whether to merge into an existing semantic file or create a new one. |
| Is this work a new standalone Epic or a CR on EPIC-044? | New standalone Epic that supersedes EPIC-044 decision-making pieces. |
| Are there mockups? | No mockups for this Epic. |

### High-Level Requirements

1. **HLR-047.1: New DAO Skill Type** — X-IPE MUST support a new skill type named DAO (`道`) in the skill-creator system.
2. **HLR-047.2: First DAO Skill** — X-IPE MUST define `x-ipe-dao-end-user` as the first DAO skill and standardize it as the human-proxy layer for human-required touchpoints.
3. **HLR-047.3: Human-Proxy Behavior** — DAO MUST support multiple dispositions: direct answer, clarification, critique, instruction, approval-like guidance, reframing, and pass-through to downstream agents.
4. **HLR-047.4: Preserved Workflow Semantics** — DAO MUST preserve the existing `process_preference.auto_proceed` semantics from EPIC-044/IDEA-031 rather than replacing them.
5. **HLR-047.5: Autonomous Default + Human-Shadow** — DAO MUST be autonomous by default and support optional human-shadow fallback behavior.
6. **HLR-047.6: Semantic DAO Logs** — DAO MUST write semantic grouped logs under `x-ipe-docs/dao/decisions_made_{semantic_task_type}.md` and may merge related work into an existing semantic file.
7. **HLR-047.7: Legacy Log Removal** — `x-ipe-docs/decision_made_by_ai.md` MUST be removed from the active design once DAO is introduced.
8. **HLR-047.8: Decision-Making Skill Deprecation** — `x-ipe-tool-decision-making` MUST be deprecated and its current call sites migrated to DAO.
9. **HLR-047.9: Instruction Interception** — Human-facing instruction resources, including packaged instruction templates, MUST be updated so human-origin message handling is routed through DAO where appropriate.
10. **HLR-047.10: Future Memory Extension Point** — DAO MUST reserve extension points for future experience/memory capabilities without making them part of v1 delivery.

### Functional Requirements

#### FR Group 1: DAO Skill Type & Template Foundation

- **FR-047.1:** `x-ipe-meta-skill-creator` MUST support a new DAO skill type in its creation flow.
- **FR-047.2:** A DAO template MUST define required sections for human-proxy scope, bounded outputs, human-shadow behavior, semantic logging, and future memory hooks.
- **FR-047.3:** DAO templates MUST explicitly state that DAO returns guidance/results only and does not expose full inner reasoning to the main agent.
- **FR-047.4:** DAO templates MUST include the Chinese 7-step backbone: 静虑、兼听、审势、权衡、谋后而定、试错、断.

#### FR Group 2: `x-ipe-dao-end-user` Core Skill

- **FR-047.5:** A new skill `x-ipe-dao-end-user` MUST be created as the first DAO implementation.
- **FR-047.6:** The skill MUST operate as a bounded sub-agent that synthesizes what a capable human would contribute at a human-required touchpoint.
- **FR-047.7:** The skill MUST be autonomous by default when no DAO-specific override is present.
- **FR-047.8:** The skill MUST support optional human-shadow fallback for low-confidence or ambiguous cases.
- **FR-047.9:** The skill MUST be able to process the initial human message as DAO-mediated input without changing downstream task scope.

#### FR Group 3: Human-Proxy Disposition Behavior

- **FR-047.10:** DAO MUST support direct-answer behavior when sufficient context exists.
- **FR-047.11:** DAO MUST support clarification/reframing behavior when intent needs sharpening.
- **FR-047.12:** DAO MUST support critique and instruction outputs for guiding other skills or agents.
- **FR-047.13:** DAO MUST support approval-like outputs where workflow policy allows it.
- **FR-047.14:** DAO MUST support pass-through/delegation when the downstream AI agent is better positioned to answer the user's original question.
- **FR-047.15:** DAO MUST not force every incoming human-style message into a declarative instruction; question-form human inputs remain valid inputs.

#### FR Group 4: Semantic DAO Logging & Legacy Log Replacement

- **FR-047.16:** DAO MUST write logs under `x-ipe-docs/dao/` only.
- **FR-047.17:** Log files MUST follow the pattern `decisions_made_{semantic_task_type}.md` with names no longer than 100 words.
- **FR-047.18:** DAO MUST decide whether a new event belongs in an existing semantic log file or a new one based on DAO's understanding of similarity/difference.
- **FR-047.19:** Each DAO log entry MUST include interaction metadata, task/workflow context, DAO mode, trigger, options considered, guidance returned, rationale summary, and follow-up if any.
- **FR-047.20:** The existing `x-ipe-docs/decision_made_by_ai.md` file MUST be deleted as part of DAO rollout.

#### FR Group 5: Workflow & Skill Migration

- **FR-047.21:** All current places that invoke `x-ipe-tool-decision-making` MUST migrate to `x-ipe-dao-end-user`.
- **FR-047.22:** Within-task human-required touchpoints in `auto` mode MUST use DAO instead of the decision-making tool.
- **FR-047.23:** Inter-task routing logic introduced in EPIC-044 MUST remain governed by `process_preference.auto_proceed`, but DAO becomes the replacement for decision-oriented human substitution.
- **FR-047.24:** Existing task-based skills and orchestration logic MUST preserve current manual / stop_for_question / auto behavior contracts after migration.
- **FR-047.25:** EPIC-046 references that currently mention `x-ipe-tool-decision-making` as the Phase 2 self-resolution mechanism MUST be updated during downstream implementation to point at DAO.

#### FR Group 6: Instruction Resource Interception

- **FR-047.26:** Instruction resources that define how user messages are interpreted MUST be updated so DAO is the human-proxy interception layer where appropriate.
- **FR-047.27:** The packaged instruction resources shipped with X-IPE MUST be updated consistently with repo-local instruction resources.
- **FR-047.28:** DAO interception MUST remain bounded: it mediates human-origin meaning, but does not absorb the responsibilities of task-based skills.

### Non-Functional Requirements

- **NFR-047.1:** DAO migration MUST preserve backward-compatible workflow semantics for `manual`, `stop_for_question`, and `auto` modes.
- **NFR-047.2:** DAO outputs MUST remain human-auditable through semantic log files.
- **NFR-047.3:** DAO must remain bounded and composable; it must not become an unscoped general-purpose implementation agent.
- **NFR-047.4:** Semantic log naming must remain stable and understandable to humans reviewing project history.
- **NFR-047.5:** Future memory support must be architecturally possible without forcing v1 persistence design.

### Constraints

- DAO v1 does not implement reusable cross-task memory.
- DAO replaces human-required touchpoints only; it does not change downstream task scope.
- The initial human message is DAO-mediated, but workflow execution policy still follows `process_preference.auto_proceed`.
- The old single-file decision log design from EPIC-044 is superseded.
- DAO may merge semantically similar events into the same log file.
- No mockups are required for this Epic.

### Dependencies

- **EPIC-044:** Superseded in part — DAO replaces `x-ipe-tool-decision-making` and `decision_made_by_ai.md`, while preserving the 3-mode workflow semantics.
- **EPIC-046:** Downstream dependency update — requirement/ideation skill documents and templates that currently reference `x-ipe-tool-decision-making` must be updated to DAO during implementation.
- **IDEA-031:** Preserved behavioral baseline for `process_preference.auto_proceed`.

### Related Features (Conflict Review)

| Existing Feature / Epic | Overlap Type | Decision |
|-------------------------|--------------|----------|
| EPIC-044 / FEATURE-044-A | Direct supersession — replaces `x-ipe-tool-decision-making` with DAO human-proxy skill | New standalone Epic; supersede old decision tool |
| EPIC-044 / decision log design | Direct supersession — replaces `x-ipe-docs/decision_made_by_ai.md` with semantic DAO logs | New standalone Epic; delete legacy log on rollout |
| EPIC-044 / workflow mode semantics | Extension — preserve 3-mode behavior while changing the human-substitution mechanism | Extend, do not break semantics |
| EPIC-046 references to `x-ipe-tool-decision-making` | Downstream dependency update | Update references during DAO implementation |

No CR impact markers appended at this requirement stage because the human chose a new standalone Epic rather than a CR on EPIC-044.

### Open Questions

- None — core scope, logging, legacy-log handling, and conflict direction were clarified during requirement gathering.

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| N/A | No mockups for this Epic |

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-047-A | EPIC-047 | DAO Skill Foundation & End-User Core | v1.0 | Deliver the minimum runnable DAO by adding DAO skill-type support, template rules, and the first `x-ipe-dao-end-user` human-proxy skill with bounded dispositions | None |
| FEATURE-047-B | EPIC-047 | Semantic DAO Logging & Workflow Migration | v1.0 | Replace legacy decision logging and migrate workflow/task-skill DAO call sites while preserving existing `process_preference.auto_proceed` semantics | FEATURE-047-A |
| FEATURE-047-C | EPIC-047 | Instruction Resource DAO Interception | v1.0 | Update repo-local and packaged instruction resources so DAO mediates human-origin inputs without absorbing downstream task-based skill responsibilities | FEATURE-047-B |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| N/A | — | No mockups |

---

## Feature Details

### FEATURE-047-A: DAO Skill Foundation & End-User Core

**Version:** v1.0  
**Priority:** P0 (Minimum Runnable Feature)

**Scope:**
- Add DAO as a supported skill type in `x-ipe-meta-skill-creator`
- Create DAO template and guidance for bounded human-proxy skills
- Create `x-ipe-dao-end-user` as the first concrete DAO implementation
- Support answer / clarify / reframe / critique / instruction / approval-like / pass-through dispositions
- Preserve autonomous-by-default behavior with optional human-shadow fallback
- Reserve future memory extension hooks without implementing reusable memory in v1

**Key Deliverables:**
- DAO template/guidelines
- Candidate-to-production workflow support for DAO skill creation
- `x-ipe-dao-end-user` core skill definition
- Input/output contract for human-proxy behavior
- Bounded reasoning/result-return policy

**Requirement Coverage:** FR-047.1 to FR-047.15, HLR-047.1 to HLR-047.5, HLR-047.10

### FEATURE-047-B: Semantic DAO Logging & Workflow Migration

**Version:** v1.0  
**Priority:** P1

**Scope:**
- Introduce `x-ipe-docs/dao/` logging design
- Define merge-vs-new-file behavior
- Replace decision-making tool call sites with DAO
- Update workflow/task-skill references while preserving 3-mode behavior
- Update EPIC-046-era references that still name the old decision tool
- Remove `x-ipe-docs/decision_made_by_ai.md` from active design/usage during rollout

**Key Deliverables:**
- DAO logging structure
- Semantic file-selection rules and required entry metadata
- Migration/removal plan for legacy log
- Migrated workflow/task-skill references
- Preserved `process_preference.auto_proceed` behavior contract

**Requirement Coverage:** FR-047.16 to FR-047.25, HLR-047.6 to HLR-047.8

### FEATURE-047-C: Instruction Resource DAO Interception

**Version:** v1.0  
**Priority:** P2

**Scope:**
- Update instruction resources in-repo and packaged resources
- Route human-origin message mediation through DAO where appropriate after workflow migration
- Keep DAO bounded to human-proxy mediation only

**Key Deliverables:**
- Updated instruction resources
- Consistent packaged/in-repo interception policy

**Requirement Coverage:** FR-047.26 to FR-047.28, HLR-047.9
