# DAO Decisions — Skill Update (2026-03-11)

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-039 | 2026-03-11T11:14:10Z | TASK-839 | N/A (human direct) | instruction | 0.90 | Update acceptance test skill: (1) run ALL tests from spec not just web UI, choosing best tool per test type; (2) add chrome-devtools-mcp to tools.json quality stage; (3) skill reads tools.json config like ideation does |

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
