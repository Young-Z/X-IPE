# Requirement Details — Part 18

> Part 18 covers: EPIC-046

---

## EPIC-046: 5-Phase Learning Method Skill Restructuring

### Origin

- **Source:** IDEA-102 (Research-Software Engineering)
- **Research:** TASK-751 research report — gap analysis of 19 task-based skills against Chinese 5-phase learning method
- **Refined Idea:** `x-ipe-docs/ideas/102. Research-Software Engineering/refined-idea/idea-summary-v1.md`

### Problem Statement

Research (TASK-751) revealed systematic gaps in X-IPE task-based skills when evaluated against the classical Chinese learning method (博学之，审问之，慎思之，明辨之，笃行之):

- 笃行之 (Practice Earnestly): 10/10 strong ✅
- 博学之 (Study Broadly): 6/10 strong
- 审问之 (Inquire Thoroughly): 3/10 strong ⚠️
- 慎思之 (Think Carefully): 3/10 strong ⚠️
- 明辨之 (Discern Clearly): 1/10 strong ❌

Skills are designed as flat procedural workflows rather than learning cycles. This leads to action-heavy, reflection-light processes.

### Scope

Restructure the **skill-creator template** and **8 Ideation + Requirement stage skills** to use a 5-phase hierarchy as the universal structural backbone for all task-based skills. Remaining 11 skills (batch 2) will be addressed in a future Epic.

### Target Users

1. **AI Agents** — follow more rigorous study→inquire→think→discern→act process
2. **Skill Creators** — use 5-phase template when creating/updating skills
3. **Human Reviewers** — benefit from documented reasoning and decisions

---

### High-Level Requirements

**HR-1: Universal 5-Phase Backbone Structure**

All task-based skills MUST organize their Execution Flow and Execution Procedure into 5 mandatory phases in strict order:

| Phase | Chinese | English | SE Purpose |
|-------|---------|---------|------------|
| 1 | 博学之 | Study Broadly | Gather comprehensive context before acting |
| 2 | 审问之 | Inquire Thoroughly | Question assumptions, probe for gaps |
| 3 | 慎思之 | Think Carefully | Reflect on trade-offs, risks, alternatives |
| 4 | 明辨之 | Discern Clearly | Make informed decisions with documented rationale |
| 5 | 笃行之 | Practice Earnestly | Execute with discipline, verify with rigor |

**HR-2: Phase-Based Execution Flow Table**

The Execution Flow summary table MUST use phase-based format:

```
| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 1. 博学之 (Study Broadly) | 1.1 | {Name} | {Action} | {Gate} |
| 2. 审问之 (Inquire Thoroughly) | 2.1 | {Name} | {Action} | {Gate} |
| 3. 慎思之 (Think Carefully) | — | SKIP | {Reason} | — |
| 4. 明辨之 (Discern Clearly) | 4.1 | {Name} | {Action} | {Gate} |
| 5. 笃行之 (Practice Earnestly) | 5.1 | {Name} | {Action} | {Gate} |
```

**HR-3: Phase-Based XML Procedure**

The Execution Procedure MUST use `<phase_N>` → `<step_N_M>` hierarchy:

```xml
<phase_1 name="博学之 — Study Broadly">
  <step_1_1>...</step_1_1>
</phase_1>
<phase_3 name="慎思之 — Think Carefully">
  <skip reason="..." />
</phase_3>
```

**HR-4: Explicit Skip Pattern**

Non-applicable phases use `<skip reason="..." />` with a standardized reason. All 5 phases MUST appear even if skipped. Phase names always include both Chinese and English.

**HR-5: Scope of Restructuring**

The 5-phase backbone restructures ONLY the ACTION section (Execution Flow + Execution Procedure). The Section Order (CONTEXT → DECISION → ACTION → VERIFY → REFERENCE) remains unchanged.

**HR-6: Auto-Proceed Behavior in Phase 2**

When `auto_proceed == "auto"`, Phase 2 (审问之) is NOT skipped. Agent still performs inquiry but self-resolves via `x-ipe-tool-decision-making` instead of asking human. Assumptions are logged to decision log.

---

### Functional Requirements by Feature

#### FEATURE-046-A: Skill-Creator Template + Guidelines Update

**FR-A1:** Update `x-ipe-meta-skill-creator/templates/x-ipe-task-based.md` to replace flat `<step_N>` structure with `<phase_N>` → `<step_N_M>` hierarchy.

**FR-A2:** Update Execution Flow table template to use phase-based format with Phase column.

**FR-A3:** Add phase definitions (all 5 phases with Chinese + English names and SE purpose) to the template.

**FR-A4:** Add skip pattern documentation with `<skip reason="..." />` syntax and common skip reasons.

**FR-A5:** Update step numbering convention from `step_N` to `step_N_M` (phase.step format).

**FR-A6:** Update skill-creator SKILL.md and/or guidelines to document the 5-phase method as mandatory backbone for all task-based skills.

**FR-A7:** Preserve existing template elements: Input Parameters, DoR, DoD, Output Result, process_preference, mode-aware completion pattern.

**Acceptance Criteria:**
- AC-A1: Template contains all 5 `<phase_N>` blocks with bilingual names
- AC-A2: Template contains skip pattern example
- AC-A3: Execution Flow table uses Phase column
- AC-A4: Step numbering uses N.M format
- AC-A5: Section Order (CONTEXT→DECISION→ACTION→VERIFY→REFERENCE) unchanged
- AC-A6: process_preference and mode-aware completion pattern preserved
- AC-A7: Skill-creator guidelines reference 5-phase method

#### FEATURE-046-B: Restructure 4 Ideation-Stage Skills

**Scope:** Ideation (rename from `x-ipe-task-based-ideation-v2` to `x-ipe-task-based-ideation`), Idea Mockup, Idea to Architecture, Share Idea

**FR-B1:** Rename `x-ipe-task-based-ideation-v2` to `x-ipe-task-based-ideation` (folder, frontmatter name, all references).

**FR-B2:** Reorganize each skill's existing steps under the 5-phase hierarchy (reshuffle — no new steps needed per research analysis).

**FR-B3:** Add SKIP markers with reasons for non-applicable phases (e.g., Idea Mockup Phase 4, Share Idea Phases 3-4).

**FR-B4:** Update Execution Flow tables to phase-based format.

**FR-B5:** Update XML procedure to `<phase_N>` → `<step_N_M>` format.

**FR-B6:** Preserve all existing DoD checkpoints (reordered under phases).

**Phase Mappings (high-level, detail in Technical Design):**

| Skill | Phase 1 博学 | Phase 2 审问 | Phase 3 慎思 | Phase 4 明辨 | Phase 5 笃行 |
|-------|-------------|-------------|-------------|-------------|-------------|
| Ideation | Load tools, Analyze files, Research | Understanding Summary, Brainstorming | Critique & Feedback | Improve & Decide on feedback | Generate draft, Complete |
| Idea Mockup | Validate folder, Load config, Read summary, Research refs | Identify needs | Load theme & Plan | SKIP | Create, Save, Update, Complete |
| Idea to Architecture | Validate folder, Load config, Read summary | Identify arch needs | SKIP | Select diagram types | Create, Save, Update, Complete |
| Share Idea | Load config, Identify source | Confirm target formats | SKIP | SKIP | Prepare, Convert, Verify |

**Acceptance Criteria:**
- AC-B1: `x-ipe-task-based-ideation-v2` renamed to `x-ipe-task-based-ideation` (folder + all references)
- AC-B2: All 4 skills have 5-phase structure in Execution Flow and Procedure
- AC-B3: All SKIP phases have explicit `<skip reason="..." />`
- AC-B4: Step numbering uses N.M format throughout
- AC-B5: All existing DoD checkpoints preserved
- AC-B6: Each skill body ≤ 500 lines

#### FEATURE-046-C: Restructure 4 Requirement-Stage Skills

**Scope:** Requirement Gathering, Feature Breakdown, Feature Refinement, Change Request

**FR-C1:** Reorganize each skill's existing steps under the 5-phase hierarchy.

**FR-C2:** Add ★NEW steps to address gaps identified in research report (high-level intent; detail in Technical Design):
- Requirement Gathering: Domain & Context Research (Phase 1), Feasibility & Risk Reflection (Phase 3)
- Feature Breakdown: Scope Challenge (Phase 2)
- Feature Refinement: Specification Review Questions (Phase 2), AC Quality Reflection (Phase 3)
- Change Request: CR Context Study (Phase 1), CR Challenge (Phase 2)

**FR-C3:** Add SKIP markers with reasons where applicable.

**FR-C4:** Update Execution Flow tables to phase-based format.

**FR-C5:** Update XML procedure to `<phase_N>` → `<step_N_M>` format.

**FR-C6:** Preserve all existing DoD checkpoints.

**Phase Mappings (high-level, detail in Technical Design):**

| Skill | Phase 1 博学 | Phase 2 审问 | Phase 3 慎思 | Phase 4 明辨 | Phase 5 笃行 |
|-------|-------------|-------------|-------------|-------------|-------------|
| Req Gathering | Understand request, Domain research ★ | Clarifying questions, Conflict review | Feasibility reflection ★ | Update impacted, Scope decision | Create doc, Complete |
| Feature Breakdown | Analyze requirements, Assess Epic scope | Scope challenge ★ | Identify feature boundaries | MVP prioritization | Create list, Init board, Complete |
| Feature Refinement | Query board, Gather context, Process mockups | Spec review questions ★ | AC quality reflection ★ | Spec scope decision | Create spec, Complete |
| Change Request | Understand CR, CR context study ★ | CR challenge ★, Analyze impact | Detect conflicts | Classify type, Route workflow | Complete output |

**Acceptance Criteria:**
- AC-C1: All 4 skills have 5-phase structure in Execution Flow and Procedure
- AC-C2: ★NEW steps present with high-level content
- AC-C3: All SKIP phases have explicit `<skip reason="..." />`
- AC-C4: Step numbering uses N.M format throughout
- AC-C5: All existing DoD checkpoints preserved
- AC-C6: Each skill body ≤ 500 lines
- AC-C7: Auto-proceed behavior for Phase 2 follows HR-6

---

### Non-Functional Requirements

- **NFR-1:** All restructured skills MUST stay under 500 lines body. Move detailed sub-actions to `references/detailed-procedures.md` if needed.
- **NFR-2:** Template changes MUST be backward-compatible — existing skills that haven't been migrated yet should still be parseable.
- **NFR-3:** Phase names MUST always include both Chinese and English (e.g., "博学之 — Study Broadly").

### Constraints

- The 5-phase backbone replaces ONLY the Execution Flow table and Execution Procedure XML. No changes to Input Parameters, DoR, DoD, or Output Result structure.
- EPIC-044 changes (process_preference) already merged — new template must preserve these.
- Remaining 11 task-based skills (batch 2) deferred to future Epic.

### Dependencies

- **EPIC-044 (completed):** process_preference.auto_proceed — already in template, must be preserved
- **EPIC-045 (in progress):** Code Implementation restructuring — independent scope, no conflict
- **x-ipe-tool-decision-making:** Used for auto-proceed Phase 2 behavior — already exists

### Related Features

- No active conflicts identified. EPIC-044 template changes (TASK-725) already merged.

### Open Questions

None — all clarified during brainstorming and requirement gathering.

---

### Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-046-A | EPIC-046 | Skill-Creator Template + Guidelines Update | v1.0 | Update task-based skill template with 5-phase backbone (phase_N → step_N_M hierarchy), skip pattern, bilingual phase names; update guidelines | None |
| FEATURE-046-B | EPIC-046 | Restructure 4 Ideation-Stage Skills | v1.0 | Reshuffle Ideation (rename from v2), Idea Mockup, Idea to Architecture, Share Idea into 5-phase structure with SKIP markers | FEATURE-046-A |
| FEATURE-046-C | EPIC-046 | Restructure 4 Requirement-Stage Skills | v1.0 | Restructure Requirement Gathering, Feature Breakdown, Feature Refinement, Change Request with 5-phase backbone + ★NEW steps | FEATURE-046-A |

### Feature Details

#### FEATURE-046-A: Skill-Creator Template + Guidelines Update (MVP)

**Type:** Foundation — all other features depend on this.

**Scope:**
- Update `x-ipe-meta-skill-creator/templates/x-ipe-task-based.md`
- Update skill-creator guidelines to document 5-phase method

**Key Deliverables:**
- Updated template with `<phase_N>` → `<step_N_M>` hierarchy
- Phase-based Execution Flow table format
- Skip pattern documentation and examples
- Updated skill-creator guidelines referencing 5-phase method

**Acceptance Criteria:** AC-A1 through AC-A7 (see Functional Requirements above)

---

#### FEATURE-046-B: Restructure 4 Ideation-Stage Skills

**Type:** Reshuffle — reorganize existing steps, no new steps added.

**Scope:**
- `x-ipe-task-based-ideation-v2` → rename to `x-ipe-task-based-ideation`
- `x-ipe-task-based-idea-mockup`
- `x-ipe-task-based-idea-to-architecture`
- `x-ipe-task-based-share-idea`

**Key Deliverables:**
- 4 restructured SKILL.md files with 5-phase backbone
- Renamed ideation skill (folder + all references)

**Acceptance Criteria:** AC-B1 through AC-B6 (see Functional Requirements above)

---

#### FEATURE-046-C: Restructure 4 Requirement-Stage Skills

**Type:** Enriched — reorganize + add ★NEW steps for gap-filling.

**Scope:**
- `x-ipe-task-based-requirement-gathering` (+ Domain Research, Feasibility Reflection)
- `x-ipe-task-based-feature-breakdown` (+ Scope Challenge)
- `x-ipe-task-based-feature-refinement` (+ Spec Review Questions, AC Quality Reflection)
- `x-ipe-task-based-change-request` (+ CR Context Study, CR Challenge)

**Key Deliverables:**
- 4 restructured SKILL.md files with 5-phase backbone + new steps

**Acceptance Criteria:** AC-C1 through AC-C7 (see Functional Requirements above)
