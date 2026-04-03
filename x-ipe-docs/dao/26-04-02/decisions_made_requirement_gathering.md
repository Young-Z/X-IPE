# DAO Decisions: Requirement Gathering

> Semantic log of human representative interactions grouped by task type.
> Each entry records a DAO interaction with full context and rationale.

| Entry | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|-------|-----------|---------|---------------|-------------|------------|---------|
| DAO-105 | 2026-04-02T11:15:00Z | TASK-1043 | x-ipe-task-based-requirement-gathering | answer | 0.87 | 6 routing + clarification decisions for IDEA-038/EPIC-054 (Feature-Learn Module) requirement gathering Phase 2: conflict resolution (EPIC-030-B overlap), MVP scoping, integration boundaries, session model, retention policy |

---

<!-- Detail sections are appended below this line -->

## DAO-105
- **Timestamp:** 2026-04-02T11:15:00Z
- **Task ID:** TASK-1043
- **Feature ID:** N/A
- **Workflow:** EPIC-054 (Feature-Learn Module)
- **Calling Skill:** x-ipe-task-based-requirement-gathering
- **Source:** ai
- **Disposition:** answer
- **Confidence:** 0.87

### Message
> Requirement gathering agent requests DAO routing + clarification decisions for 6 questions in Phase 2 of IDEA-038/EPIC-054 requirement gathering. Two conflict decisions (EPIC-030-B Chrome DevTools injection overlap and UI panel coexistence) and four clarifying questions (MVP feature priority, downstream integration specificity, concurrent recording sessions, session data retention policy). Each question includes options and a recommendation.

### Guidance Returned

> **Conflict Decisions (Phase 2.2):**
>
> **Q1: EPIC-030-B Overlap — Chrome DevTools Injection Infrastructure**
> **Decision: Option A — CR on EPIC-030-B to extract shared utility.**
> Proceed with a Change Request on EPIC-030-B to extract `x-ipe-util-chrome-devtools-integration` as a shared utility module. EPIC-054 will declare a dependency on this utility. This is the correct path: the idea summary already explicitly planned to share injection infrastructure (DRY), and the overlap is real — both EPICs use `evaluate_script` + `navigate_page` + reinject-on-redirect patterns. Option B (independent implementation) directly contradicts the idea's architecture intent and creates tech debt from day one. Option C (new standalone EPIC) is over-engineering — this is an extraction refactor from existing code, not a new capability, so a CR is the right-sized intervention.
>
> **Q2: EPIC-030-B Overlap — Injected UI Panel Coexistence**
> **Decision: Option B — Defer z-index strategy to technical design.**
> The requirement should state: "EPIC-054 toolbox MUST coexist with EPIC-030-B toolbar when both are active on the same page." That is the requirement-level concern — *what* must work. The *how* (z-index layering, Shadow DOM isolation, event propagation) is a technical design concern. Defining z-index numbers in requirements would over-constrain the solution space and create brittle cross-EPIC coupling at the wrong abstraction level.
>
> **Clarifying Questions (Phase 2.1):**
>
> **Q3: MVP Feature Priority**
> **Decision: Accept recommended MVP scope with one refinement.**
> MVP (must-have for v1): Features 1–5 and 7 (GUI toolbox, Chrome DevTools injection, recording engine, cross-page persistence, toolbox UI, PII protection). These form the minimum viable recording pipeline.
> Deferred: Feature 6 (hybrid AI annotation) — for v1, use **post-processing annotation only**. Real-time annotation adds UX complexity and requires tight event-loop integration that risks destabilizing the recording engine. Post-processing with full session context will produce better annotations anyway. Feature 8 (crash recovery) — defer entirely to v2. Session loss is an inconvenience, not a data integrity risk, since recordings are append-to-file.
> **Refinement:** Ensure the recording engine (Feature 3) outputs a format that post-processing annotation can consume without modification — this preserves the upgrade path to real-time annotation in v2 without requiring schema changes.
>
> **Q4: Downstream Integration Specificity**
> **Decision: Requirement defines output schema + consuming skills; defer integration API to technical design.**
> The requirement document should include: (a) the `behavior-recording.json` output schema (already defined in the idea summary), (b) the list of consuming skills (`x-ipe-task-based-requirement-gathering` and `x-ipe-task-based-code-implementation`), and (c) the semantic contract — what each consuming skill expects from the recording data. The detailed integration API (function signatures, parsing logic, import patterns) belongs in technical design of the consuming features. This follows the requirements/design boundary: requirements say WHAT is produced and WHO consumes it; design says HOW they consume it.
>
> **Q5: Concurrent Recording Sessions**
> **Decision: Single active session for v1. KISS.**
> One recording session active at a time. If a new recording is requested while one is active, prompt the user to stop the current session first. Do NOT silently queue — the user should make an explicit choice. Rationale: multi-session tracking requires complex state management (which tab belongs to which session, merged vs. separate persistence, toolbox UI multiplexing) with no clear v1 use case. The requirement should state: "System supports one active recording session at a time. Starting a new session requires explicitly ending the current session."
>
> **Q6: Session Data Retention Policy**
> **Decision: Project folder storage, project lifecycle retention, no auto-deletion.**
> Completed `behavior-recording.json` files are stored in the project's artifact folder (alongside idea summaries, requirement documents, and other X-IPE outputs). Retention follows the project lifecycle — files persist until the user manually deletes them or the project is archived. No auto-deletion, no TTL, no size limits for v1. This is consistent with how all other X-IPE artifacts are managed. The requirement should state the storage location convention but not impose retention automation.

### Rationale
> All 6 questions are tightly coupled parts of requirement gathering Phase 2 for EPIC-054. They target the same calling skill and the same downstream requirement document. The answers follow established X-IPE engineering principles: DRY (Q1 — shared utility), correct abstraction level (Q2, Q4 — requirements vs. design boundary), KISS (Q5 — single session), YAGNI (Q3 — defer real-time annotation and crash recovery), and consistency with existing patterns (Q6 — project folder storage). Confidence is 0.87: high because the idea summary from DAO-104 provides clear directional context and the recommendations from the calling agent are well-reasoned — I agree with 5 of 6 recommendations fully and refined Q3 with an upgrade-path consideration. No decisions are irreversible; all can be adjusted during feature refinement.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-requirement-gathering"
>     match_strength: "strong"
>     reason: "Calling skill is requirement gathering. DAO output feeds directly back into Phase 2 to resolve conflicts and clarifications, unblocking Phase 3 (requirement document authoring)."
>     execution_steps:
>       - phase: "2. REQUIREMENT"
>         step: "2.3 Author requirement document with resolved conflicts and clarifications"
>   - skill_name: "x-ipe-task-based-change-request"
>     match_strength: "partial"
>     reason: "Q1 decision triggers a CR on EPIC-030-B to extract shared Chrome DevTools utility. This CR should be created as a prerequisite task before EPIC-054 implementation begins."
>     execution_steps:
>       - phase: "5. FEEDBACK"
>         step: "change_request — CR on EPIC-030-B to extract x-ipe-util-chrome-devtools-integration"

### Follow-up
> Q1 triggers a downstream action: create a Change Request on EPIC-030-B to extract shared Chrome DevTools injection infrastructure as `x-ipe-util-chrome-devtools-integration`. This CR should be tracked as a prerequisite for EPIC-054 implementation. The requirement gathering agent should note this dependency in the EPIC-054 requirement document.
