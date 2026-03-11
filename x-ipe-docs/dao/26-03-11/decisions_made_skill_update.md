# DAO Decisions — Skill Update (2026-03-11)

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-039 | 2026-03-11T11:14:10Z | TASK-839 | N/A (human direct) | instruction | 0.90 | Update acceptance test skill: (1) run ALL tests from spec not just web UI, choosing best tool per test type; (2) add chrome-devtools-mcp to tools.json quality stage; (3) skill reads tools.json config like ideation does |
| DAO-041 | 2026-03-11T11:53:33Z | TASK-840 | N/A (human direct) | instruction | 0.92 | Change next_task_based_skill in x-ipe-task-based-feature-acceptance-test to only include code-refactor |
| DAO-044 | 2026-03-11T13:58:34Z | N/A | N/A (human direct) | pass_through | 0.92 | Investigate feature refinement skill for scope+mockup → specification flow |

## DAO-039
- **Timestamp:** 2026-03-11T11:14:10Z
- **Task ID:** TASK-839
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (human direct)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> Update acceptance test skill — it should not only check if feature has web UI component (skip if backend-only), it should run all the tests listed in the feature specification, no matter if frontend or backend or any other types. The idea is for different type of implementation you should choose best tool for it. For example web-based frontend uses chrome-devtools MCP. Also: (1) set chrome-devtools MCP as a configuration in tools.json and display on x-ipe tools quality stage; (2) acceptance test skill should base on it to leverage enabled tools (reference ideation pattern).

### Guidance Returned
> Proceed with skill update using x-ipe-meta-skill-creator. Three changes: (1) Remove web-UI-only gate in Step 1.1 — classify ALL acceptance criteria by test type (frontend-ui, backend-api, unit, integration) and route each to the best tool. (2) Add `chrome-devtools-mcp: true` to tools.json `stages.quality.testing`. (3) Refactor skill to read tools.json config at startup (like ideation's Step 1.1) and route test execution to enabled tools.

### Rationale
> The user's request is clear and well-scoped — broadening acceptance testing from UI-only to all test types is a natural evolution. The tools.json pattern is already proven in the ideation skill, so applying it to acceptance testing is consistent. Chrome DevTools MCP is already used by this skill; making it configurable adds flexibility. Single instruction unit since all parts are tightly coupled.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-meta-skill-creator"
>     match_strength: "strong"
>     reason: "Updating an existing task-based skill requires the skill creator process"
>     execution_steps:
>       - phase: "1. Validate"
>         step: "1.1 Load existing skill"
>       - phase: "2. Update"
>         step: "2.1 Apply changes following template"

### Follow-up
> None

## DAO-040
- **Timestamp:** 2026-03-11T10:57:08Z
- **Task ID:** N/A (pre-task)
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** copilot-instructions
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.94

### Message
> for DAO since it's mainly represent end-user to guide agent by following x-ipe software engineering flow to deliver business value, why not let's have a reference of the task based skills workflow(engineering workflow) within 'DAO', so when it's do decide which flow for the next, not only base on the logical context demands, but also engineering process

### Guidance Returned
> Create a new reference file `references/engineering-workflow.md` in the DAO skill that documents the X-IPE engineering workflow DAG — stages, skill sequence, routing logic. Update Step 2.1 (Scan Skills) to reference this file so skill suggestions are informed by both contextual matching AND engineering process position.

### Rationale
> Strong alignment with DAO's purpose. Currently Step 2.1 scans skill descriptions for keyword matching, but lacks awareness of WHERE in the engineering lifecycle the user is. Adding workflow context means DAO can suggest the engineering-correct next step (e.g., "you just finished technical design, next is code-implementation") rather than only pattern-matching keywords. This is the difference between a chatbot and an engineering guide.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-meta-skill-creator"
>     match_strength: "strong"
>     reason: "Adding reference file and updating SKILL.md procedure"

### Follow-up
> None

## DAO-041
- **Timestamp:** 2026-03-11T11:53:33Z
- **Task ID:** TASK-840
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (human direct)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.92

### Message
> for x-ipe-task-based-feature-acceptance-test skill the next step should only be refactoring

### Guidance Returned
> Update `next_task_based_skill` in x-ipe-task-based-feature-acceptance-test to only include `x-ipe-task-based-code-refactor`. Remove `x-ipe-task-based-feature-closing` and `x-ipe-task-based-human-playground` entries from both the input parameters and output result sections. Also update `references/engineering-workflow.md` in the DAO skill to reflect this routing change.

### Rationale
> User explicitly wants to enforce a quality-first workflow: after acceptance testing, always go through refactoring before any closing. This simplifies the decision tree and ensures code quality review happens consistently. The change is a clear, scoped user override of the current multi-option routing. Three perspectives considered — supporting (enforces quality gate), opposing (reduces flexibility to skip refactoring), neutral (user owns the workflow, reversible).

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-meta-skill-creator"
>     match_strength: "strong"
>     reason: "Modifying an existing task-based skill's YAML configuration requires skill creator process"
>     execution_steps:
>       - phase: "1. Validate"
>         step: "1.1 Load existing skill"
>       - phase: "2. Update"
>         step: "2.1 Apply changes following template"

### Follow-up
> None

## DAO-004
- **Timestamp:** 2026-03-11T13:41:06Z
- **Task ID:** TASK-842
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.85

### Message
> let's update DAO skill a bit, it should encourage parallelization with evaluation, if it identifies multi tasks which have no dependency, then it should suggest the execution plan with parallelism

### Guidance Returned
> Update the DAO skill (x-ipe-dao-end-user-representative) to add parallelism-awareness: when Step 1.1b decomposes a message into multiple instruction units, analyze dependencies between units. If units are independent, add an execution_plan field suggesting parallel execution. Update the output format, phases, and examples accordingly. Use x-ipe-meta-skill-creator process.

### Rationale
> User explicitly requests a skill enhancement. The DAO already produces instruction_units[] (1–3). Adding dependency analysis and a parallel execution plan is a natural extension. Aligns with workflow efficiency goals. Bounded change — only affects DAO output format and Phase 2 logic.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-meta-skill-creator"
>     match_strength: "strong"
>     reason: "Updating an existing skill requires the skill creator process"
>     execution_steps:
>       - phase: "1. Validate"
>         step: "1.1 Load existing skill"
>       - phase: "2. Update"
>         step: "2.1 Apply changes following template"

### Follow-up
> None

| DAO-042 | 2026-03-11T13:24:05Z | TASK-842 | N/A (human direct) | instruction | 0.90 | Update x-ipe-task-based-feature-refinement: add "Test Type" column (UI/API/other) to acceptance testing table in skill template |

## DAO-042
- **Timestamp:** 2026-03-11T13:24:05Z
- **Task ID:** TASK-842
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (human direct)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> let's update the existing feature refinement skill, for acceptance testing section, it's table we need have an extra column listing for these acceptance testing it's ui testing or api testing or some other way suggested to validate the ac

### Guidance Returned
> Update the feature refinement skill (x-ipe-task-based-feature-refinement) acceptance testing table to add a "Test Type" column. Each acceptance criterion row should specify how to validate it: UI Testing, API Testing, Unit Testing, Manual, or other suggested method. Use x-ipe-meta-skill-creator to make the update following proper skill modification process.

### Rationale
> Clear, bounded skill update request. User wants the acceptance testing table in the feature refinement skill to include a column indicating the validation method for each AC. This aids downstream acceptance testing skill by pre-classifying test types during refinement. Low risk — additive change to table format.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-meta-skill-creator"
>     match_strength: "strong"
>     reason: "Updating an existing skill requires the skill creator process"
>     execution_steps:
>       - phase: "1. Preparation"
>         step: "1.1 Load existing skill"
>       - phase: "2. Modification"
>         step: "2.1 Apply changes to candidate"
>       - phase: "3. Validation"
>         step: "3.1 Validate against checklist"

### Follow-up
> None

---

## DAO-043

### Meta
| Field | Value |
|-------|-------|
| Timestamp | 2026-03-11T13:26:00Z |
| Task ID | TASK-842 |
| Feature ID | N/A |
| Workflow | N/A |
| Calling Skill | x-ipe-meta-skill-creator |
| Source | human |
| Disposition | instruction |
| Confidence | 0.95 |

### Message
> "btw no manual testing this option"

### Guidance
> Remove "Manual" from Test Type options across all candidate files. Valid Test Type values should be: UI, API, Unit, Integration (4 types only). Update all references in candidate files: SKILL.md Step 3.1, Step 5.1, specification-template.md, and specification-writing-guide.md.

### Rationale
> User explicitly excludes manual testing; all ACs should be verifiable by automated tests. This aligns with the project's test automation philosophy — every acceptance criterion must be machine-checkable.

### Suggested Skills
> none (continuation of current TASK-842 work)

### Follow-up
> None

## DAO-005
- **Timestamp:** 2026-03-11T13:53:29Z
- **Task ID:** TASK-843
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> let's make 'DAO' simpler, we no longer need step 1.3 and step 2.3

### Guidance Returned
> Remove step 1.3 (Direction, Timing, Environment) and step 2.3 (Validate) from the DAO skill. Update Execution Flow table, procedure, references, and re-number affected steps accordingly.

### Rationale
> User explicitly requests simplification. Step 1.2 (Three Perspectives) already covers directional assessment. Step 2.2 (Weigh Gains/Losses) can absorb the validation/worst-case gate logic. Removing redundant steps reduces DAO token cost and execution time.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-meta-skill-creator"
>     match_strength: "strong"
>     reason: "Updating an existing skill"

### Follow-up
> None

## DAO-044
- **Timestamp:** 2026-03-11T13:58:34Z
- **Task ID:** N/A
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (human direct)
- **Source:** human
- **Disposition:** pass_through
- **Confidence:** 0.92

### Message
> check the feature refinement skill, did it follow feature scope and it's referenced mockup to genereate the specification doc?

### Guidance Returned
> Investigate the feature refinement skill (x-ipe-task-based-feature-refinement) procedure to verify it properly ensures: (1) feature scope from the feature board query and requirement context flows into specification generation, and (2) referenced mockups are analyzed and their UI/UX requirements are extracted into the specification document. Report findings to the user.

### Rationale
> Analytical question requiring procedure trace — user wants to understand whether the skill's execution steps properly incorporate feature scope and mockup references when generating the specification document. This requires reading and analyzing the skill, not making changes.

### Suggested Skills
> suggested_skills: none (investigation/analysis task)

### Follow-up
> None
