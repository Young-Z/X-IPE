# FEATURE-046-B: Restructure 4 Ideation-Stage Skills

> Feature ID: FEATURE-046-B
> Epic: EPIC-046 (5-Phase Learning Method Skill Restructuring)
> Depends On: FEATURE-046-A (Template + Guidelines — ✅ Done)
> Status: In Refinement
> Created: 2026-03-05

---

## Overview

Restructure 4 Ideation-stage task-based skills to use the 5-phase learning method backbone (`<phase_N>` → `<step_N_M>` hierarchy). This involves reshuffling existing steps under phases, adding skip markers for non-applicable phases, updating Execution Flow tables, and renaming `ideation-v2` to `ideation`.

---

## Scope

### In Scope

1. **x-ipe-task-based-ideation-v2** → rename to **x-ipe-task-based-ideation**
2. **x-ipe-task-based-idea-mockup** — reshuffle steps into 5 phases
3. **x-ipe-task-based-idea-to-architecture** — reshuffle steps into 5 phases
4. **x-ipe-task-based-share-idea** — reshuffle steps into 5 phases

### Out of Scope

- Adding new steps (reshuffle only per research finding)
- Modifying step logic or actions (content preserved, only structure changes)
- Requirement-stage skills (FEATURE-046-C)
- Non-task-based skills

---

## Functional Requirements

### FR-1: Rename ideation-v2 → ideation

Rename `x-ipe-task-based-ideation-v2` to `x-ipe-task-based-ideation`:
- Rename folder `.github/skills/x-ipe-task-based-ideation-v2/` → `.github/skills/x-ipe-task-based-ideation/`
- Update frontmatter `name:` field
- Update all internal self-references
- Update candidate folder path in `x-ipe-docs/skill-meta/`

### FR-2: Phase-Based Execution Flow Tables

Each skill's Execution Flow table must use the new phase-based format:

```
| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 1. 博学之 (Study Broadly) | 1.1 | {Name} | {Action} | {Gate} |
```

### FR-3: Phase-Based XML Procedure

Each skill's Execution Procedure must use `<phase_N>` → `<step_N_M>` hierarchy with bilingual phase names.

### FR-4: Explicit Skip Patterns

Non-applicable phases must use `<skip reason="..." />` with descriptive reason.

### FR-5: Preserved Elements

For each skill, preserve:
- All existing DoR/DoD checkpoints (reorder under phases)
- Input Parameters (including `process_preference`, `execution_mode`, `workflow`)
- Output Result YAML
- Sub-agent planning definitions
- References and related skills sections
- Input Initialization subsection
- Mode-aware completion pattern in final step

---

## Phase Mappings Per Skill

### Ideation (currently ideation-v2, 9 steps → 5 phases)

| Phase | Chinese | Steps Mapped | Rationale |
|-------|---------|-------------|-----------|
| 1 博学之 | Study Broadly | 1.1 Load Toolbox Meta, 1.2 Analyze Idea Files, 1.3 Research Common Principles | Gathering all context and knowledge before engaging |
| 2 审问之 | Inquire Thoroughly | 2.1 Generate Understanding Summary, 2.2 Brainstorming Session | Questioning user, probing idea, challenging assumptions |
| 3 慎思之 | Think Carefully | 3.1 Critique and Feedback | Sub-agent reflects on quality, completeness, feasibility |
| 4 明辨之 | Discern Clearly | 4.1 Improve and Decide on Feedback | Selecting which feedback to address, deciding final direction |
| 5 笃行之 | Practice Earnestly | 5.1 Generate Idea Draft, 5.2 Complete and Request Review | Disciplined execution of final deliverable |

**Reorder note:** Current steps 1→2→3→4→5→6→7→8→9 become: 1→2→5→3→4→7→8→6→9. Research (old step 5) moves to Phase 1 before brainstorming. Draft (old step 6) moves to Phase 5 after discernment.

### Idea Mockup (10 steps → 5 phases)

| Phase | Chinese | Steps Mapped | Rationale |
|-------|---------|-------------|-----------|
| 1 博学之 | Study Broadly | 1.1 Validate Folder, 1.2 Load Config, 1.3 Read Idea Summary, 1.4 Research References | Gathering all inputs and context |
| 2 审问之 | Inquire Thoroughly | 2.1 Identify Mockup Needs | Analyzing what mockups are needed, questioning scope |
| 3 慎思之 | Think Carefully | 3.1 Load Brand Theme and Plan Layout | Considering theme constraints, reflecting on approach |
| 4 明辨之 | Discern Clearly | SKIP — single implementation approach; mockup tool selection done in Phase 1 config | |
| 5 笃行之 | Practice Earnestly | 5.1 Create Mockups, 5.2 Save Artifacts, 5.3 Update Idea Summary, 5.4 Complete | Disciplined creation and delivery |

### Idea to Architecture (8 steps → 5 phases)

| Phase | Chinese | Steps Mapped | Rationale |
|-------|---------|-------------|-----------|
| 1 博学之 | Study Broadly | 1.1 Validate Folder, 1.2 Load Config, 1.3 Read Idea Summary | Gathering context |
| 2 审问之 | Inquire Thoroughly | 2.1 Identify Architecture Needs | Analyzing what diagrams are needed, questioning system boundaries |
| 3 慎思之 | Think Carefully | SKIP — architecture decisions are at idea level, not implementation level | |
| 4 明辨之 | Discern Clearly | 4.1 Select Diagram Types | Choosing which diagram types to create based on needs |
| 5 笃行之 | Practice Earnestly | 5.1 Create Diagrams, 5.2 Save Artifacts, 5.3 Update Idea Summary, 5.4 Complete | Creation and delivery |

### Share Idea (6 steps → 5 phases)

| Phase | Chinese | Steps Mapped | Rationale |
|-------|---------|-------------|-----------|
| 1 博学之 | Study Broadly | 1.1 Load Config, 1.2 Identify Source File | Gathering context and available tools |
| 2 审问之 | Inquire Thoroughly | 2.1 Confirm Target Formats | Asking user about desired formats |
| 3 慎思之 | Think Carefully | SKIP — no trade-offs; conversion is mechanical | |
| 4 明辨之 | Discern Clearly | SKIP — format already confirmed in Phase 2 | |
| 5 笃行之 | Practice Earnestly | 5.1 Prepare Content, 5.2 Execute Conversion, 5.3 Verify and Complete | Disciplined execution |

---

## Acceptance Criteria

### AC Group 1: Structural Compliance (all skills)

- **AC-1.1:** All 4 skills have exactly 5 `<phase_N>` blocks in Execution Procedure
- **AC-1.2:** Phase names use bilingual format: `<phase_N name="中文 — English">`
- **AC-1.3:** Step numbering uses N.M format (e.g., `<step_1_1>`, `<step_2_1>`)
- **AC-1.4:** Non-applicable phases use `<skip reason="..." />`
- **AC-1.5:** Execution Flow table uses Phase column with all 5 phases present

### AC Group 2: Rename (ideation-v2 → ideation)

- **AC-2.1:** Folder `.github/skills/x-ipe-task-based-ideation/` exists (old `ideation-v2` removed)
- **AC-2.2:** Frontmatter `name: x-ipe-task-based-ideation`
- **AC-2.3:** All internal references updated to new name

### AC Group 3: Preserved Elements

- **AC-3.1:** All existing DoR checkpoints preserved (may be reordered)
- **AC-3.2:** All existing DoD checkpoints preserved (may be reordered)
- **AC-3.3:** Input Parameters sections unchanged (process_preference, execution_mode, workflow)
- **AC-3.4:** Output Result YAML unchanged
- **AC-3.5:** Sub-agent planning definitions preserved
- **AC-3.6:** Mode-aware completion pattern in final Phase 5 step
- **AC-3.7:** Input Initialization subsection preserved

### AC Group 4: Phase Mapping Correctness

- **AC-4.1:** Ideation Phase 1 contains Study steps (load, analyze, research)
- **AC-4.2:** Ideation Phase 2 contains Inquire steps (summary, brainstorm)
- **AC-4.3:** Ideation Phase 3 contains Think step (critique)
- **AC-4.4:** Ideation Phase 4 contains Discern step (improve/decide)
- **AC-4.5:** Ideation Phase 5 contains Practice steps (draft, complete)
- **AC-4.6:** Idea Mockup Phase 4 has `<skip reason="..." />`
- **AC-4.7:** Idea to Architecture Phase 3 has `<skip reason="..." />`
- **AC-4.8:** Share Idea Phases 3 and 4 both have `<skip reason="..." />`

### AC Group 5: Line Count

- **AC-5.1:** Each skill's SKILL.md stays under 500 lines

### AC Group 6: Candidate Workflow

- **AC-6.1:** All changes made in candidate/ folders first
- **AC-6.2:** Candidates merged to production via cp -r

---

## Non-Functional Requirements

- **NFR-1:** No new steps added — reshuffle only (per research finding)
- **NFR-2:** Skill behavior unchanged — same inputs produce same outputs
- **NFR-3:** Candidate workflow enforced — no direct production edits

---

## Business Rules

- **BR-1:** Phase 1 (博学之) and Phase 5 (笃行之) are NEVER skippable
- **BR-2:** auto_proceed in Phase 2: agent self-resolves via x-ipe-tool-decision-making
- **BR-3:** Skip reasons must explain WHY phase doesn't apply
- **BR-4:** Phase order is fixed: 1→2→3→4→5, no reordering

---

## Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| FEATURE-046-A (Template + Guidelines) | ✅ Done | Provides the template pattern to follow |
