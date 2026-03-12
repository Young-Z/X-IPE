# DAO Decisions — Skill Update (26-03-12)

| Entry | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|-------|-----------|---------|---------------|-------------|------------|---------|
| DAO-060 | 2026-03-12T05:39:24Z | TASK-TBD | N/A (direct human message) | instruction | 0.85 | Create x-ipe-ui-testing-via-chrome-mcp tool skill + update AC skill to store by test type and route UI tests through new tool |
| DAO-061 | 2026-03-12T10:53:01Z | TASK-TBD | N/A (direct human message) | instruction | 0.90 | Add mockup input to UI testing tool + AC skill; compare actual UI against mockup; auto-detect freshness, set N/A if outdated |

---

## DAO-060
- **Timestamp:** 2026-03-12T05:39:24Z
- **Task ID:** TASK-TBD
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction (2 units)
- **Confidence:** 0.85

### Message
> Can we update task based AC skill as below: 1. after it's defined the AC scope, can it store by test type. 2. add a tool skill called x-ipe-ui-testing-via-chrome-mcp, it should base on the UI test best practice to define its capability. 3. task based AC skill and tools.json should support adding this tool. 4. if using this tool, for sets of UI tests, let's call the tool for test.

### 3-Perspective Analysis

| Perspective | Assessment |
|-------------|------------|
| Supporting | Modularizing UI testing into a dedicated tool skill follows X-IPE architecture. The AC skill already classifies by test type but lacks formal grouping/storage. Chrome MCP tools are available. |
| Opposing | The AC skill already references chrome-devtools-mcp in tools.json. Is a separate tool skill necessary? Yes — tool skills encapsulate best practices and execution patterns that raw MCP tool calls don't provide. |
| Neutral | Request is clear, well-structured, and aligns with existing patterns (other tool skills like x-ipe-tool-implementation-python exist). Two distinct work items: create new skill, update existing skill + config. |

### Instruction Units

**Unit 0:** Create `x-ipe-ui-testing-via-chrome-mcp` tool skill based on UI testing best practices with Chrome DevTools MCP capabilities.
- Suggested skill: `x-ipe-meta-skill-creator` (strong match)

**Unit 1:** Update `x-ipe-task-based-feature-acceptance-test` SKILL.md to store AC by test type after scope definition, add new tool to tools.json, and route UI test sets through the new tool skill.
- Suggested skill: `x-ipe-meta-skill-creator` (strong match)
- Depends on: Unit 0

### Execution Plan
- Strategy: sequential
- Groups: [[0], [1]]
- Rationale: Unit 1 references the tool skill created by Unit 0; must be sequential.

### Suggested Skills
> - skill_name: "x-ipe-meta-skill-creator"
>   match_strength: "strong"
>   reason: "Creating new tool skill and updating existing task-based skill"
>   execution_steps:
>     - phase: "1. Preparation"
>       step: "1.1 Determine skill type and load template"
>     - phase: "2. Draft"
>       step: "2.1 Create candidate in x-ipe-docs/skill-meta/"

### Follow-up
> None
