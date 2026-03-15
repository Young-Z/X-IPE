# DAO Decisions — Skill Update (26-03-12)

| Entry | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|-------|-----------|---------|---------------|-------------|------------|---------|
| DAO-060 | 2026-03-12T05:39:24Z | TASK-TBD | N/A (direct human message) | instruction | 0.85 | Create x-ipe-tool-ui-testing-via-chrome-mcp tool skill + update AC skill to store by test type and route UI tests through new tool |
| DAO-061 | 2026-03-12T10:53:01Z | TASK-TBD | N/A (direct human message) | instruction | 0.90 | Add mockup input to UI testing tool + AC skill; compare actual UI against mockup; auto-detect freshness, set N/A if outdated |
| DAO-062 | 2026-03-12T12:24:22Z | TASK-TBD | N/A (direct human message) | instruction | 0.95 | Rename x-ipe-tool-ui-testing-via-chrome-mcp → x-ipe-tool-ui-testing-via-chrome-mcp across entire codebase (2 dirs, 9 files, 20+ refs) |
| DAO-063 | 2026-03-12T14:22:00Z | TASK-TBD | N/A (direct human message) | instruction | 0.92 | Add mockup_link input to code-implementation skill (derive from spec) + pass to frontend tool skills (html5); mirror AC skill pattern |

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
> Can we update task based AC skill as below: 1. after it's defined the AC scope, can it store by test type. 2. add a tool skill called x-ipe-tool-ui-testing-via-chrome-mcp, it should base on the UI test best practice to define its capability. 3. task based AC skill and tools.json should support adding this tool. 4. if using this tool, for sets of UI tests, let's call the tool for test.

### 3-Perspective Analysis

| Perspective | Assessment |
|-------------|------------|
| Supporting | Modularizing UI testing into a dedicated tool skill follows X-IPE architecture. The AC skill already classifies by test type but lacks formal grouping/storage. Chrome MCP tools are available. |
| Opposing | The AC skill already references chrome-devtools-mcp in tools.json. Is a separate tool skill necessary? Yes — tool skills encapsulate best practices and execution patterns that raw MCP tool calls don't provide. |
| Neutral | Request is clear, well-structured, and aligns with existing patterns (other tool skills like x-ipe-tool-implementation-python exist). Two distinct work items: create new skill, update existing skill + config. |

### Instruction Units

**Unit 0:** Create `x-ipe-tool-ui-testing-via-chrome-mcp` tool skill based on UI testing best practices with Chrome DevTools MCP capabilities.
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

## DAO-062
- **Timestamp:** 2026-03-12T12:24:22Z
- **Task ID:** TASK-TBD
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction (1 unit)
- **Confidence:** 0.95

### Message
> the name x-ipe-tool-ui-testing-via-chrome-mcp is wrong, it should be x-ipe-tool-ui-testing-via-chrome-mcp, please fix it and all the reference places

### 3-Perspective Analysis

| Perspective | Assessment |
|-------------|------------|
| Supporting | The naming convention `x-ipe-tool-` is the correct prefix for tool skills in X-IPE (e.g., `x-ipe-tool-implementation-python`). The current name `x-ipe-tool-ui-testing-via-chrome-mcp` violates this convention. Fixing it now prevents downstream confusion. |
| Opposing | Historical records (DAO logs, task-board) also contain the old name. Renaming everywhere alters audit trail. However, consistency outweighs — the old name was a mistake that should not propagate. |
| Neutral | Straightforward mechanical rename: 2 directories + 9 files + 20+ string occurrences. Fully bounded, reversible via git. No logic changes required. |

### Instruction Units

**Unit 0:** Rename skill `x-ipe-tool-ui-testing-via-chrome-mcp` → `x-ipe-tool-ui-testing-via-chrome-mcp` across the entire codebase: rename 2 directories, update 20+ string references in 9 files.
- Suggested skill: `x-ipe-task-based-code-refactor` (strong match)

### Execution Plan
- Strategy: sequential
- Groups: [[0]]
- Rationale: Single unit — no parallelism needed.

### Suggested Skills
> - skill_name: "x-ipe-task-based-code-refactor"
>   match_strength: "strong"
>   reason: "Codebase-wide rename of identifier + directory — classic refactoring operation with scope analysis, execution, and validation"
>   execution_steps:
>     - phase: "1. Analyze"
>       step: "1.1 Identify all files and directories containing old name"
>     - phase: "2. Execute"
>       step: "2.1 Rename directories, then update all string references"
>     - phase: "3. Validate"
>       step: "3.1 Verify no remaining references to old name"

### Follow-up
> None

---

## DAO-063
- **Timestamp:** 2026-03-12T14:22:00Z
- **Task ID:** TASK-TBD
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction (1 unit)
- **Confidence:** 0.92

### Message
> Just like acceptance test task based skill, the code-implementation task based skill also needs to reference mockup and when frontend implementation is required, pass it to related frontend implementation tool skills, such as x-ipe-tool-implementation-html5 if needed (just like acceptance test task based skill -> ui-testing tool skill)

### 3-Perspective Analysis

| Perspective | Assessment |
|-------------|------------|
| Supporting | Consistent with the pattern just established in the AC skill. The code-implementation skill already has a conceptual step 3.1.9 ("IF current mockups AND frontend components: pass mockup constraints to frontend tool skill") — formalizing with a proper `mockup_link` input param + initialization ensures reliability and auto-detection with freshness checks. |
| Opposing | Step 3.1.9 already mentions mockup constraints informally. Is formalizing needed? Yes — without a formal `mockup_link` input + initialization, the skill has no guaranteed way to locate/validate the mockup path or check freshness. The AC skill proved this pattern works. |
| Neutral | Clear, well-scoped request with explicit prior art reference. Two skills touched (code-implementation + html5), but tightly coupled — one passes, the other receives. Engineering-correct: standalone skill update. |

### Instruction Units

**Unit 0:** Update `x-ipe-task-based-code-implementation` and `x-ipe-tool-implementation-html5` to support `mockup_link`, mirroring the acceptance test skill pattern:

**(A) `x-ipe-task-based-code-implementation`:**
1. Add `mockup_link: "{path | N/A}"` to Input Parameters
2. Add Input Initialization for `mockup_link` — derive from specification (resolved from `extra_context_reference.specification`): read "Linked Mockups" section, check freshness (Linked Date ≥ latest spec/design update), set path or N/A
3. Formalize Step 3.1.9 to explicitly pass `mockup_link` (not just vague "mockup constraints") to frontend tool skills when invoking — add it to the INVOKE payload alongside `aaa_scenarios`, `source_code_path`, `feature_context`

**(B) `x-ipe-tool-implementation-html5`:**
4. Add `mockup_link: "{path | N/A}"` to Input Parameters (in `feature_context` or as a top-level optional input)
5. Update Input Initialization to document source: "From orchestrator (code-implementation) mockup_link"
6. In implementation steps, reference mockup for visual fidelity when `mockup_link != "N/A"` (layout, colors, spacing, typography from mockup)

- Suggested skill: `x-ipe-meta-skill-creator` (strong match)

### Execution Plan
- Strategy: sequential
- Groups: [[0]]
- Rationale: Single unit — no parallelism needed.

### Suggested Skills
> - skill_name: "x-ipe-meta-skill-creator"
>   match_strength: "strong"
>   reason: "Updating two existing skills (task-based + tool) to add mockup_link input, initialization, and propagation — skill-creator handles all skill modifications"
>   execution_steps:
>     - phase: "1. Preparation"
>       step: "1.1 Determine skill type and load template"
>     - phase: "2. Draft"
>       step: "2.1 Create candidate in x-ipe-docs/skill-meta/"
>     - phase: "3. Validate"
>       step: "3.1 Verify against checklist"
>     - phase: "4. Merge"
>       step: "4.1 Merge to production"

### Follow-up
> None
