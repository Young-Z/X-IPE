# DAO Decisions — Ideation

## Registry

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-007 | 2026-03-09T03:59:19Z | TASK-792 | N/A (initial) | instruction | 0.92 | Refine idea 034 CR-'道' for x-ipe using ideation skill — based on UIUX feedback Feedback-20260309-111628 |
| DAO-008 | 2026-03-09T05:57:09Z | TASK-792 | N/A (continuation) | instruction | 0.93 | Continuation — refine idea 034 with ideation skill, same request as DAO-007 in new session |
| DAO-009 | 2026-03-09T06:22:33Z | TASK-792 | x-ipe-task-based-ideation | instruction | 0.90 | User says "continue" — proceed with ideation using best-judgment defaults for 3 open questions |
| DAO-010 | 2026-03-09T07:00:48Z | TASK-792 | x-ipe-task-based-ideation | instruction | 0.95 | User feedback: enum keys too terse — AI needs semantic clarity over brevity. Update idea-summary-v1.md with meaningful keys |
| DAO-011 | 2026-03-09T07:07:48Z | TASK-792 | x-ipe-task-based-ideation | approval | 0.95 | User proposes final keys: dao-represent-human-to-interact, dao-represent-human-to-interact-for-questions-in-skill, interact-with-human — accepted |
| DAO-012 | 2026-03-09T07:10:31Z | TASK-792 | x-ipe-task-based-ideation | instruction | 0.95 | User says "move on" — ideation complete, proceed to x-ipe-task-based-change-request |
| DAO-016 | 2026-03-10T02:19:16Z | TASK-803 | N/A (initial) | instruction | 0.90 | Route UIUX feedback on code-implementation tool config to ideation skill |
| DAO-017 | 2026-03-10T02:42:47Z | TASK-804 | x-ipe-task-based-feature-refinement | instruction | 0.93 | FEATURE-045-A refinement complete (spec v1.1) — proceed to Technical Design |
| DAO-018 | 2026-03-10T02:53:06Z | TASK-805 | x-ipe-task-based-technical-design | instruction | 0.94 | FEATURE-045-A technical design v1.1 complete (16/16 DoD) — proceed to Code Implementation |

---

## DAO-007
- **Timestamp:** 2026-03-09T03:59:19Z
- **Task ID:** TASK-792
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (initial user message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.92

### Message
> refine the idea x-ipe-docs/ideas/034. CR-'道' for x-ipe/new idea.md with ideation skill

### Guidance Returned
> Proceed with ideation refinement. The idea file references UIUX feedback (Feedback-20260309-111628) proposing to rename "auto_proceed" mode to "End-User Representative Mode" with new interaction_mode enum values, UI label changes, and logic verification. Strong match for x-ipe-task-based-ideation skill to brainstorm and produce structured idea summary.

### Rationale
> User explicitly requests ideation refinement on a sparse idea file backed by concrete UIUX feedback. Direction aligns (early-stage ideation), timing is right (new idea, no conflicts), environment allows it. Smallest useful intervention: instruct agent to proceed with ideation skill.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-ideation"
>     match_strength: "strong"
>     reason: "User explicitly asks to refine an idea — direct match to ideation triggers"
>     execution_steps:
>       - phase: "1. Absorb"
>         step: "1.1 Read all files in idea folder"
>       - phase: "2. Clarify"
>         step: "2.1 Ask clarifying questions"
>       - phase: "3. Synthesize"
>         step: "3.1 Produce structured idea summary"

### Follow-up
> None

---

## DAO-009
- **Timestamp:** 2026-03-09T06:22:33Z
- **Task ID:** TASK-792
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** x-ipe-task-based-ideation (mid-execution)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> continue

### Guidance Returned
> Proceed with ideation — use best-judgment defaults for 3 open questions: (1) use shorter internal keys with longer UI labels, (2) support backward compat during transition, (3) label dropdown as "Interaction Mode". These are easily revisable in a CR document.

### Rationale
> "Continue" in context of pending clarifying questions means "use your best judgment." This is an idea document, not code — naming defaults are low-risk and reversible. Direction aligns (mid-ideation), timing is right (momentum matters), environment allows it. Smallest useful intervention: instruct with defaults.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-ideation"
>     match_strength: "strong"
>     reason: "Already in-progress — continue to Phase 3 (Synthesize)"
>     execution_steps:
>       - phase: "3. Synthesize"
>         step: "3.1 Produce structured idea summary"

### Follow-up
> None
- **Timestamp:** 2026-03-09T05:57:09Z
- **Task ID:** TASK-792
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (continuation from new session)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.93

### Message
> refine the idea x-ipe-docs/ideas/034. CR-'道' for x-ipe/new idea.md with ideation skill

### Guidance Returned
> Continuation of DAO-007. Proceed with ideation refinement for idea 034 — the idea file is sparse, referencing Feedback-20260309-111628 which proposes renaming auto_proceed to End-User Representative Mode. TASK-792 already exists on board. Load x-ipe-task-based-ideation skill and execute.

### Rationale
> Same request as DAO-007 in a new session. TASK-792 is already in_progress on board. Direction aligns (ideation stage), timing is right (continuation), environment allows it. Instruction: proceed with ideation skill.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-ideation"
>     match_strength: "strong"
>     reason: "User explicitly asks to refine an idea with ideation skill"
>     execution_steps:
>       - phase: "1. Absorb"
>         step: "1.1 Read all files in idea folder"
>       - phase: "2. Clarify"
>         step: "2.1 Ask clarifying questions"
>       - phase: "3. Synthesize"
>         step: "3.1 Produce structured idea summary"

### Follow-up
> None

---

## DAO-010
- **Timestamp:** 2026-03-09T07:00:48Z
- **Task ID:** TASK-792
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** x-ipe-task-based-ideation (post-synthesis feedback)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.95

### Message
> can we have more meaningful keys? dao-represent, dao-inner-only is short but not meaningful, since ai requirement accurate semantic understanding to work. so meaningful is over simplicity

### Guidance Returned
> Update idea-summary-v1.md enum keys from terse (dao-represent, dao-inner-only, human-direct) to semantically rich (interact-with-dao-representative, interact-with-dao-representative-inner-skill-only, interact-with-human). AI agents parse these keys to determine behavior — self-documenting keys prevent misinterpretation without requiring lookup tables.

### Rationale
> User explicitly states "meaningful is over simplicity" — a clear design principle for AI-consumed keys. The original proposal was directionally correct; terse keys were an over-correction toward brevity. Since keys appear in YAML/JSON/CLI (not inner loops), readability and semantic accuracy outweigh brevity. Low risk: this is an idea document refinement.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-ideation"
>     match_strength: "strong"
>     reason: "Refinement of in-progress idea summary — update enum values"

### Follow-up
> None

---

## DAO-011
- **Timestamp:** 2026-03-09T07:07:48Z
- **Task ID:** TASK-792
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** x-ipe-task-based-ideation (post-synthesis feedback)
- **Source:** human
- **Disposition:** approval
- **Confidence:** 0.95

### Message
> how about dao-represent-human-to-interact, dao-represent-human-to-interact-for-questions-in-skill, interact-with-human

### Guidance Returned
> Accept the user's proposed keys. They follow a consistent subject-verb-object pattern and are semantically clear for AI consumption. Updated idea-summary-v1.md with: dao-represent-human-to-interact, dao-represent-human-to-interact-for-questions-in-skill, interact-with-human.

### Rationale
> User is the product owner iterating on naming — this is their domain decision. The keys are meaningful, consistent, and readable. Minor length concern on the middle key is acceptable given the "meaningful over simplicity" principle established in DAO-010.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-ideation"
>     match_strength: "strong"
>     reason: "Same refinement cycle — updating enum values per user feedback"

### Follow-up
> None

---

## DAO-012
- **Timestamp:** 2026-03-09T07:10:31Z
- **Task ID:** TASK-792
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** x-ipe-task-based-ideation (completed)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.95

### Message
> move on

### Guidance Returned
> Ideation complete. Proceed to x-ipe-task-based-change-request skill to analyze impact and classify the CR for IDEA-034.

### Rationale
> Idea is refined (v1 with 3 rounds of user feedback on enum naming). This is explicitly a CR (folder named "034. CR-'道' for x-ipe"), so the change-request skill is the correct next step. Direction aligns, timing is right, environment allows.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-change-request"
>     match_strength: "strong"
>     reason: "Idea 034 is a CR — next step is change-request analysis"

### Follow-up
> None

## DAO-016
- **Timestamp:** 2026-03-10T02:19:16Z
- **Task ID:** TASK-803
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (initial user message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> Get uiux feedback, please visit feedback folder x-ipe-docs/uiux-feedback/Feedback-20260309-184047 to get details. Feedback content: "for code-implementation in feature stage, let's also like brainstorming in ideation stage that, since we have many tool-implementation-* skills, let's having can be enable or disabled in the toolbox config, so when task-based-code-implementation been called, just like ideation skill it can choose the best enabled tools for it's work."

### Guidance Returned
> Route to x-ipe-task-based-ideation for idea refinement. The user proposes extending the tools.json enable/disable pattern (already used in ideation stage) to the code-implementation stage, so tool-implementation-* skills can be configured. This follows the established Feedback → Ideation → CR pipeline seen in prior tasks (e.g., TASK-792).

### Rationale
> User explicitly references brainstorming pattern ("let's also like brainstorming in ideation stage"). The idea is well-framed but needs refinement — which tool-implementation-* skills exist, how should selection logic work, what config structure to use. Ideation is the right entry point to scope this properly before committing to a change request. Confidence 0.90 — clear intent, established pattern.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-ideation"
>     match_strength: "strong"
>     reason: "User proposes new capability with brainstorming framing — needs idea refinement before CR"
>     execution_steps:
>       - phase: "1. 博学之 — Study Broadly"
>         step: "1.1 Understand Idea"
>       - phase: "2. 审问之 — Question Deeply"
>         step: "2.1 Generate Questions"
>       - phase: "3. 慎思之 — Reflect Carefully"
>         step: "3.1 Synthesize Summary"
>       - phase: "4. 明辨之 — Distinguish Clearly"
>         step: "4.1 Human Review"
>       - phase: "5. 笃行之 — Act Decisively"
>         step: "5.1 Finalize and Complete"

### Follow-up
> None — proceed to task creation and ideation skill execution

---

## DAO-017
- **Timestamp:** 2026-03-10T02:42:47Z
- **Task ID:** TASK-804
- **Feature ID:** FEATURE-045-A
- **Workflow:** N/A
- **Calling Skill:** x-ipe-task-based-feature-refinement
- **Source:** ai
- **Disposition:** instruction
- **Confidence:** 0.93

### Message
> Feature Refinement for FEATURE-045-A is complete (spec v1.1). The skill's defined next step is Technical Design. Should we proceed to Technical Design for FEATURE-045-A, or take a different action?

### Guidance Returned
> Proceed to x-ipe-task-based-technical-design for FEATURE-045-A. The spec v1.1 is complete and DoD-verified with substantial scope (11 ACs in AC-3, 10-step routing procedure in FR-3, 5 new edge cases). Technical design is the correct next gate — it will define internal architecture and surface any remaining spec ambiguities before implementation begins.

### Rationale
> Three perspectives assessed: (1) Supporting — spec complete, pipeline established, design needed before complex implementation; (2) Opposing — spec expanded significantly, but design phase is itself a review mechanism; (3) Neutral — routine pipeline transition in DAO mode. Direction aligned (refinement→design), timing correct (DoD verified, no blockers), environment clear (DAO mode active). Smallest useful intervention: instruct forward to technical design.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-technical-design"
>     match_strength: "strong"
>     reason: "Declared next_task_based_skill from feature-refinement output — direct match to 'design feature' trigger"
>     execution_steps:
>       - phase: "1. Research"
>         step: "1.1 Query feature board for full Feature Data Model"
>       - phase: "2. Design"
>         step: "2.1 Read feature specification and design solution"
>       - phase: "3. Document"
>         step: "3.1 Create two-part technical design document"

### Follow-up
> None — Quill 🪶 should create a new task on task-board.md for Technical Design and execute x-ipe-task-based-technical-design for FEATURE-045-A

---

## DAO-018
- **Timestamp:** 2026-03-10T02:53:06Z
- **Task ID:** TASK-805
- **Feature ID:** FEATURE-045-A
- **Workflow:** N/A
- **Calling Skill:** x-ipe-task-based-technical-design
- **Source:** ai
- **Disposition:** instruction
- **Confidence:** 0.94

### Message
> Technical Design for FEATURE-045-A is complete (v1.1). The skill's defined next step is Code Implementation. Should we proceed to Code Implementation for FEATURE-045-A?

### Guidance Returned
> Proceed to x-ipe-task-based-code-implementation for FEATURE-045-A. The technical design v1.1 is complete with all 16 DoD checkpoints verified. It specifies config-aware routing: read tools.json → filter enabled → force-enable general → semantic match enabled only. The 8-step discovery procedure, ConfigFilter component, updated sequence diagram, and 7 new edge cases provide sufficient architectural clarity for implementation. Code implementation is the declared and correct next gate.

### Rationale
> Three perspectives assessed: (1) Supporting — design v1.1 complete with 16/16 DoD, CR-001 additions fully integrated (8-step config-aware procedure, ConfigFilter, 7 edge cases, tools.json file changes), implementation is the natural next gate; (2) Opposing — design expanded significantly from v1.0 to v1.1, but the design phase itself served as the review mechanism and all checkpoints passed; (3) Neutral — routine pipeline transition in DAO mode, identical pattern to DAO-017 (refinement→design). Direction aligned (design→implementation), timing correct (DoD verified, no blockers), environment clear (DAO mode active). Smallest useful intervention: instruct forward to code implementation.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-code-implementation"
>     match_strength: "strong"
>     reason: "Declared next_task_based_skill from technical-design output — direct match to 'implement feature' trigger"
>     execution_steps:
>       - phase: "1. Prepare"
>         step: "1.1 Read feature specification and technical design"
>       - phase: "2. Test"
>         step: "2.1 Generate AAA test scenarios from specification"
>       - phase: "3. Implement"
>         step: "3.1 Route to language-specific tool skills via semantic matching"
>       - phase: "4. Validate"
>         step: "4.1 Run tests and verify implementation"

### Follow-up
> None — Quill 🪶 should create a new task on task-board.md for Code Implementation and execute x-ipe-task-based-code-implementation for FEATURE-045-A

| DAO-019 | 2026-03-10T11:48:33Z | TASK-TBD | N/A (initial) | instruction | 0.90 | Refine knowledge-base idea + auto-detect UIUX reference via ideation skill in workflow mode |

## DAO-019
- **Timestamp:** 2026-03-10T11:48:33Z
- **Task ID:** TASK-TBD (to be assigned on task-board)
- **Feature ID:** N/A
- **Workflow:** Knowledge-Base-Implementation
- **Calling Skill:** N/A (initial user message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> refine the idea x-ipe-docs/ideas/wf-007-knowledge-base-implementation/new idea.md and uiux reference: auto-detect with ideation skill --workflow-mode@Knowledge-Base-Implementation

### Guidance Returned
> Execute ideation skill (x-ipe-task-based-ideation) in workflow-mode for workflow Knowledge-Base-Implementation. Inputs: idea_folder_path=x-ipe-docs/ideas/wf-007-knowledge-base-implementation, raw-idea=new idea.md, uiux-reference=auto-detect. Workflow is at ideation stage with compose_idea done; refine_idea is the target action. interaction_mode=interact-with-human.

### Rationale
> Clear instruction with aligned workflow state. The idea file exists, compose_idea is done, and refine_idea is the next suggested action. UIUX reference set to auto-detect per user specification — ideation skill input schema supports this value.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-ideation"
>     match_strength: "strong"
>     reason: "User explicitly requested ideation skill; refine_idea is the target workflow action"
>     execution_steps:
>       - phase: "1. 博学之 (Study Broadly)"
>         step: "1.1 Load Toolbox"
>       - phase: "1. 博学之 (Study Broadly)"
>         step: "1.2 Analyze Files"
>       - phase: "1. 博学之 (Study Broadly)"
>         step: "1.3 Research"
>       - phase: "2. 审问之 (Inquire Thoroughly)"
>         step: "2.1 Generate Summary"
>       - phase: "2. 审问之 (Inquire Thoroughly)"
>         step: "2.2 Brainstorm"
>       - phase: "3. 慎思之 (Think Carefully)"
>         step: "3.1 Critique"
>       - phase: "4. 明辨之 (Discern Clearly)"
>         step: "4.1 Improve Summary"
>       - phase: "5. 笃行之 (Practice Earnestly)"
>         step: "5.1 Generate Draft"
>       - phase: "5. 笃行之 (Practice Earnestly)"
>         step: "5.2 Complete"

### Follow-up
> None — agent should create task on task-board.md, then load and execute x-ipe-task-based-ideation following all steps exactly.

---

### DAO-020

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-10T12:40:48Z |
| Task ID | TASK-823 |
| Source | human |
| Calling Skill | x-ipe-task-based-idea-mockup |
| Workflow | Knowledge-Base-Implementation |

**Message:** "for the folders in the knowledgebase it's not predefined, it's just like any cloud storage, for example one drive or google drive, the folder structure is totally defined by end user or base on the original folder structure uploaded. 2. but we do should be able to tagging tag these docs, the tags should be predefined in knowledgebase config json"

**Instruction Unit 1/1:**
- **Disposition:** `instruction`
- **Content:** Update KB idea to replace predefined category directories with free-form user-defined folder structure (like OneDrive/Google Drive). Users create any folder hierarchy they want. Tags remain but must be predefined in kb-config.json (not free-form YAML frontmatter tags). Update idea-summary-v1.md storage structure, kb-config.json schema, sidebar mockup, and all references to "predefined categories."
- **Rationale:** User is the domain expert on KB UX requirements. Free-form folders are more flexible and match familiar cloud storage mental models. Predefined tags in config provide structure without restricting folder organization. Both changes are consistent and complementary.
- **Suggested Skills:** None (in-place idea update, not a new task)

**Confidence:** 0.95 | **Fallback:** false

---

### DAO-021

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-10T12:49:32Z |
| Task ID | TASK-823 |
| Source | human |
| Calling Skill | x-ipe-task-based-idea-mockup |
| Workflow | Knowledge-Base-Implementation |

**Message:** "in the reference modal window, we should not only to insert reference of selected docs or folders, but also directly 'copy' it into the clipboard, so I can manually paste them"

**Instruction Unit 1/1:**
- **Disposition:** `instruction`
- **Content:** Add "Copy to Clipboard" action to the KB Reference Picker modal alongside "Insert References". Users should be able to copy selected article paths/references to clipboard for manual pasting elsewhere.
- **Rationale:** Practical UX enhancement — not all contexts support auto-insertion. Clipboard copy gives users flexibility to paste references anywhere (external docs, chat, email, etc.). Low effort, high utility.
- **Suggested Skills:** None (in-place idea + mockup update)

**Confidence:** 0.97 | **Fallback:** false

---

### DAO-022

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-10T12:53:58Z |
| Task ID | TASK-823 |
| Source | human |
| Calling Skill | x-ipe-task-based-idea-mockup |
| Workflow | Knowledge-Base-Implementation |

**Message:** "I can not only reference files, but also folders. I can search also by tags, for predefined tags, it should have two dimension, one is vertical which defines which project or project specific purpose for. one is horizontal, which should in terms of software delivery lifecycle (requirement, feature, technical design...) you can have your more wise naming convention for both."

**Instruction Unit 1/1:**
- **Disposition:** `instruction`
- **Content:** Three updates: (1) Reference picker must support selecting folders, not just files. (2) Search in reference picker should also filter by tags. (3) Predefined tags should be a 2D taxonomy: Vertical axis = domain/purpose tags (project-specific), Horizontal axis = SDLC phase tags (requirement, design, implementation, etc.). Agent should design smart naming for both dimensions.
- **Rationale:** Folder references give broader context. Tag search enables precise discovery. 2D tag taxonomy (domain × lifecycle) creates a powerful cross-cutting classification system — every article sits at an intersection of "what it's about" and "which delivery phase it serves."

**Confidence:** 0.95 | **Fallback:** false

---

### DAO-023

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-10T12:59:57Z |
| Task ID | TASK-823 |
| Source | human |
| Calling Skill | x-ipe-task-based-idea-mockup |
| Workflow | Knowledge-Base-Implementation |

**Message:** "for lifecycle or Domain let's have a more differential way to display them, so I CAN KNOW which is which"

**Instruction Unit 1/1:**
- **Disposition:** `instruction`
- **Content:** Make lifecycle and domain tags visually distinct so users can tell dimensions apart at a glance. Design two clearly different visual treatments.
- **Confidence:** 0.98

---

### DAO-024

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-10T13:03:59Z |
| Task ID | TASK-823 |
| Source | human |
| Calling Skill | x-ipe-task-based-idea-mockup |
| Workflow | Knowledge-Base-Implementation |

**Message:** "cool, now please consider the current x-ipe uiux to see if any final adjustment required or change existing uiux to deliver better uiux"

**Instruction Unit 1/1:**
- **Disposition:** `instruction`
- **Content:** Audit the KB mockup against the real X-IPE UI. Identify gaps in consistency, improve UX where the mockup deviates from established patterns, and suggest/implement changes to existing X-IPE UI patterns if they would deliver a better experience for the KB feature.
- **Confidence:** 0.95

---

### DAO-025 — UIUX Audit Completion

**Task:** TASK-823 (Design Mockup)
**Source:** human → agent (DAO-024 continuation)
**Workflow:** Knowledge-Base-Implementation

**Instruction Unit 1/1:**
- **Disposition:** `instruction`
- **Content:** Applied all UIUX audit fixes to KB mockup to match real X-IPE patterns. Changes made: (1) Modal border-radius 14px→12px, (2) Modal overlay rgba(0,0,0,0.5)→0.4, z-index 1000→1051, (3) Modal animation from slideUp keyframes to scale(0.95)+translateY(10px) with spring easing cubic-bezier(0.34,1.56,0.64,1), (4) Top bar border rgba(255,255,255,0.06)→#333 with z-index 100→300, (5) Terminal panel bg #1a1a2e→#252526 with hover state + new-terminal/toggle buttons, (6) Modal header/footer padding/borders aligned to compose-modal pattern, (7) Cancel button style matched to compose-modal-btn-cancel, (8) Nav-section-header padding aligned to 0.5rem 1rem.
- **Rationale:** Consistency with existing X-IPE UI ensures the KB feature feels native, not bolted-on. Every discrepancy was verified against actual CSS files (base.css, terminal.css, compose-idea-modal.css, sidebar.css).
- **Confidence:** 0.95
