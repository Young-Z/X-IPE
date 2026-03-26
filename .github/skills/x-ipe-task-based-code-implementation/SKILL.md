---
name: x-ipe-task-based-code-implementation
description: Implement code for a single feature using orchestrator pattern. Generates AAA test scenarios from specification, routes to language-specific tool skills via semantic matching, and validates results. Delegates to x-ipe-meta-skill-creator for skill files and mcp-builder for MCP servers. Triggers on requests like "implement feature", "write code", "develop feature".
---

# Task-Based Skill: Code Implementation

## Purpose

Implement code for a single feature by:
1. Querying feature board for full Feature Data Model
2. Learning technical design document thoroughly
3. Reading architecture designs (if referenced in technical design)
4. **Generating AAA test scenarios** from specification + technical design
5. **Routing to language-specific tool skills** via semantic matching
6. **Validating all Assert clauses** pass across tool skill outputs

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

**BLOCKING: Single Feature Only.** This skill operates on exactly ONE feature at a time. Do NOT batch or combine multiple features in a single execution. If multiple features need processing, run this skill separately for each feature.

**Workflow Mode:** When `execution_mode == "workflow-mode"`, the completion step MUST call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with `workflow_name` from `workflow.name` input, `action` from `workflow.action` input, `status: "done"`, and a `deliverables` keyed dict using ONLY the extract tags defined in `workflow-template.json` for this action (format: `{"tag-name": "path/to/file"}`). Do NOT pass a flat list of file paths. Verify the workflow state was updated before marking the task complete.

**Phase 1 Coexistence:** AAA scenario generation coexists with `x-ipe-tool-test-generation`. If AAA generation fails (ambiguous spec, insufficient detail), fall back to `x-ipe-tool-test-generation` as a safety net. This fallback will be removed in Phase 3 after all tool skills are proven stable.

### Implementation Principles

| Principle | Rule |
|-----------|------|
| KISS | Keep code simple and readable; prefer clarity over cleverness |
| YAGNI | Implement ONLY what is in technical design; no extras |
| AAA-Driven | Arrange/Act/Assert scenarios drive implementation and validation |
| Coverage | Target 80%+; NEVER add complexity just for coverage |
| Standards | Use linters, formatters, meaningful names |
| Mockups | For frontend work, reference mockups from specification.md and match layout, components, and visual states |

See [references/implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md) for detailed principles, coding standards, AAA format specification, and error handling patterns.

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-code-implementation"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      tech-design: "path | N/A | auto-detect"
      specification: "path | N/A | auto-detect"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-acceptance-test"
      condition: "Verify implementation with acceptance tests"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  feature_phase: "Code Implementation"

  # Required inputs
  feature_id: "{FEATURE-XXX}"

  # Git strategy (from .x-ipe.yaml, passed by workflow)
  git_strategy: "main-branch-only | dev-session-based"
  git_main_branch: "{auto-detected}"

  # Context (from previous task or project)
  specification_link: "x-ipe-docs/requirements/FEATURE-XXX/specification.md"
  mockup_link: "{path | N/A}"       # Derived from specification's Linked Mockups section; N/A if outdated or missing
  technical_design_link: "x-ipe-docs/requirements/FEATURE-XXX/technical-design.md"

  # Tech context (from Technical Design output)
  program_type: "frontend | backend | fullstack | cli | library | skills | mcp | ..."  # non-exhaustive
  tech_stack: []  # e.g. ["Python/Flask", "JavaScript/Vanilla", "HTML/CSS"]
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="feature_id" source="from previous task (Technical Design) output or task board" />
  <field name="extra_context_reference" source="from workflow context or auto-detect from feature artifacts (x-ipe-docs/requirements/FEATURE-XXX/)" />
  <field name="specification_link" source="IF workflow mode AND extra_context_reference.specification is a path → use it; ELSE → x-ipe-docs/requirements/{feature_id}/specification.md" />
  <field name="technical_design_link" source="IF workflow mode AND extra_context_reference.tech-design is a path → use it; ELSE → x-ipe-docs/requirements/{feature_id}/technical-design.md" />
  <field name="mockup_link">
    <steps>
      1. READ specification at specification_link, find "Linked Mockups" section
      2. IF mockup found AND Linked Date >= latest spec/design update → set mockup_link = "{path}"
      3. ELSE (no mockup, missing section, or Linked Date outdated) → set mockup_link = "N/A"
    </steps>
  </field>
  <field name="git_strategy" source="from .x-ipe.yaml" />
  <field name="git_main_branch" source="auto-detect via `git symbolic-ref refs/remotes/origin/HEAD`" />
  <field name="program_type" source="from Technical Design output" />
  <field name="tech_stack" source="from Technical Design output" />
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Feature exists on feature board</name>
    <verification>Query feature board for feature_id; status must exist</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature status is "Designed"</name>
    <verification>Feature board status == "Designed"</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Technical design document exists</name>
    <verification>File exists at x-ipe-docs/requirements/FEATURE-XXX/technical-design.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tracing utility exists in project</name>
    <verification>Check for tracing/ directory or x_ipe.tracing import; if missing, use x-ipe-tool-tracing-creator skill first</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 Query Board, 1.2 Learn Design, 1.3 Read Architecture | Load feature data, study technical design, read architecture | Design fully understood |
| 2. 审问之 — Inquire Thoroughly | 2.1 Generate AAA Scenarios | Create tagged test scenarios from spec + design | Scenarios with coverage |
| 3. 慎思之 — Think Carefully | 3.1 Route & Invoke Tool Skills | Semantic-match and invoke tool skills sequentially | All tool skills complete |
| 4. 明辨之 — Discern Clearly | 4.1 Validate Results, 4.2 Apply Tracing | Verify Assert clauses, run integration, add tracing | All checks pass |
| 5. 笃行之 — Practice Earnestly | 5.1 Update Workflow Status | Update workflow, verify DoD, output summary | Task complete |
| 继续执行 | 6.1 Decide Next Action | DAO-assisted next task decision | Next action decided |
| 继续执行 | 6.2 Execute Next Action | Load skill, generate plan, execute | Execution started |

BLOCKING: Phase 2 → 3 is BLOCKED until AAA scenarios are generated with coverage validated.
BLOCKING: Phase 3: If design needs changes → UPDATE technical design BEFORE implementing.
BLOCKING: Step 3.1 special-case delegations run BEFORE semantic routing.

---

## Execution Procedure

```xml
<procedure name="code-implementation">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">

    <step_1_1>
      <name>Query Feature Board</name>
      <action>
        1. CALL x-ipe+feature+feature-board-management skill with operation=query_feature
        2. RECEIVE Feature Data Model (feature_id, title, version, status, specification_link, technical_design_link)
      </action>
      <constraints>
        - BLOCKING: Feature must exist on board with status "Designed"
      </constraints>
      <output>Feature Data Model with all links and context</output>
    </step_1_1>

    <step_1_2>
      <name>Learn Technical Design</name>
      <action>
        1. Resolve spec/design from Input Initialization (specification_link, technical_design_link)
        2. READ technical_design_link; UNDERSTAND Part 1 (Summary) and Part 2 (Guide)
        3. NOTE architecture references; CHECK Design Change Log for updates
        4. IF mockup_link != "N/A": READ mockup files, extract layout/components/styling for Phase 3
        5. CHECK for skill files (.github/skills/) → FLAG for x-ipe-meta-skill-creator in Phase 3
        6. CHECK for MCP server keywords → FLAG for mcp-builder in Phase 3
      </action>
      <constraints>
        - BLOCKING: Do NOT code until design is understood; STOP and clarify if unclear
        - CRITICAL: If later steps reveal design issues → UPDATE technical-design.md + Design Change Log, then RESUME
      </constraints>
      <output>Implementation requirements understood, mockup references loaded (if applicable)</output>
    </step_1_2>

    <step_1_3>
      <name>Read Architecture Designs</name>
      <action>
        1. CHECK if technical design references architecture patterns
        2. IF no references: skip this step
           ELSE: READ x-ipe-docs/architecture/technical-designs/{component}.md; UNDERSTAND common patterns, interfaces, integration requirements
      </action>
      <output>Architecture patterns understood (or skipped)</output>
    </step_1_3>

  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">

    <step_2_1>
      <name>Generate AAA Scenarios</name>
      <action>
        1. PARSE specification.md: each AC → one @integration scenario (Arrange/Act/Assert)
        2. PARSE technical-design.md Part 2:
           - API endpoints → @backend happy + error scenarios
           - UI components → @frontend happy + error scenarios
           - Validation rules → @backend scenarios; edge cases → matching layer
        3. TAG scenarios: @backend, @frontend, @integration
        4. VALIDATE coverage: every AC ≥1 scenario, every endpoint/component has happy + sad path
        5. Large context (>20 components) → per-layer batches (see references/)
        6. IF generation fails → FALLBACK to x-ipe-tool-test-generation (Phase 1 coexistence)
      </action>
      <constraints>
        - MANDATORY: AAA format: @{tag} / Test Scenario: {name} / Arrange: / Act: / Assert:
        - BLOCKING: Do NOT proceed to Phase 3 until scenarios generated and coverage validated
      </constraints>
      <output>Tagged AAA scenarios with coverage summary</output>
    </step_2_1>

  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">

    <step_3_1>
      <name>Route and Invoke Tool Skills</name>
      <action>
        1. CHECK special-case delegations FIRST:
           a. IF program_type == "skills": DELEGATE to x-ipe-meta-skill-creator; VERIFY DoD; JUMP to step_4_2
              NOTE: Acceptance testing is NOT skipped — x-ipe-task-based-feature-acceptance-test will run structured-review tests on the deliverables
           b. IF MCP server detected: DELEGATE to mcp-builder; VERIFY quality checks; JUMP to step_4_2

        2. DISCOVER: SCAN .github/skills/x-ipe-tool-implementation-*/ for available tool skills

        3. READ CONFIG: Read x-ipe-docs/config/tools.json → extract stages.implement.implementation section
           - IF section missing OR empty (only _order key, no tool entries) → config_active = false
           - ELSE (has tool entries beyond _order and _extra_instruction) → config_active = true

        4. FILTER ENABLED TOOLS:
           IF config_active == false:
             → All discovered tools treated as ENABLED (backwards compatibility)
           ELSE (config_active == true):
             → FOR EACH discovered tool skill:
               a. Look up key "x-ipe-tool-implementation-{name}" in config
               b. IF key exists AND value is true → ENABLED
               c. IF key exists AND value is false → DISABLED, log: "skipped x-ipe-tool-implementation-{name} (disabled)"
               d. IF key does NOT exist (undeclared) → DISABLED (opt-in required), log: "skipped x-ipe-tool-implementation-{name} (undeclared, default disabled)"

        5. FORCE-ENABLE GENERAL: x-ipe-tool-implementation-general is ALWAYS enabled
           - IF general was disabled or undeclared → override to ENABLED
           - Log warning: "x-ipe-tool-implementation-general cannot be disabled — safety net fallback"

        6. LOAD _extra_instruction: IF stages.implement.implementation._extra_instruction exists → use as supplementary semantic routing context

        7. SEMANTIC MATCH: FOR EACH tech_stack entry: semantically match to ENABLED tool skill only
           - No match among enabled skills → assign x-ipe-tool-implementation-general
           - General insufficient → signal "new tool skill needed"
           dao-represent-human → log gap via DAO, continue; else → ask human

        8. INVOKE: FOR EACH matched tool skill (sequentially, backend first):
           a. FILTER AAA scenarios by layer tag
           b. INVOKE with: aaa_scenarios, source_code_path, feature_context, mockup_link (if frontend)
           c. RECEIVE: implementation_files, test_files, test_results, lint_status

        9. IF mockup_link != "N/A" AND frontend components:
           PASS mockup_link in feature_context to frontend tool skill (e.g., x-ipe-tool-implementation-html5)
           Tool skill uses mockup for visual fidelity: layout, components, spacing, color, states

        10. COLLECT all tool skill outputs for validation
      </action>
      <constraints>
        - BLOCKING: Special-case check runs BEFORE semantic routing
        - CRITICAL: Tool skills invoked sequentially, NOT in parallel
        - CRITICAL: Only ENABLED tools participate in semantic matching (step 7)
        - MANDATORY: Use standard tool skill I/O contract (see references/implementation-guidelines.md)
        - MANDATORY: All internal markdown links MUST use full project-root-relative paths
        - MANDATORY: Log diagnostic messages for all skipped (disabled/undeclared) tools
      </constraints>
      <output>All tool skill outputs collected</output>
    </step_3_1>

  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">

    <step_4_1>
      <name>Validate Tool Skill Results</name>
      <action>
        1. FOR EACH tool skill output: verify all Assert clauses (count pass/fail); verify lint_status == "pass"
        2. IF failing Asserts: re-invoke failed tool skill with original scenarios + error context
           - Retry succeeds → continue; retry fails → preserve passing results, escalate
           dao-represent-human → log failure via DAO; else → escalate to human
        3. RUN @integration scenarios: verify cross-layer behavior with mocking
        4. IF integration fails: report contract mismatch
           dao-represent-human → log via DAO; else → report to human
        5. PRODUCE aggregated report: per-skill pass/fail, integration results, overall status
      </action>
      <success_criteria>
        - All @backend, @frontend, @integration Assert clauses pass; all lint checks pass
      </success_criteria>
      <output>Aggregated validation report (PASS/FAIL)</output>
    </step_4_1>

    <step_4_2>
      <name>Apply Tracing Instrumentation</name>
      <action>
        1. IF no tracing infrastructure (no x_ipe.tracing module) or only skill/config files modified: skip
        2. ELSE: INVOKE x-ipe-tool-tracing-instrumentation for all modified files
           - REVIEW decorators (INFO for public, DEBUG for helpers)
           - APPLY with sensitive param redaction; RE-RUN tests to verify
      </action>
      <output>Tracing decorators applied; tests still pass</output>
    </step_4_2>

  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">

    <step_5_1>
      <name>Update Workflow Status</name>
      <action>
        1. IF execution_mode == "workflow-mode":
           a. Call update_workflow_action with: workflow_name, action, status: "done", feature_id,
              deliverables: {"impl-files": "{path}", "impl-folder": "{path}"}
           b. Log: "Workflow action status updated to done"
        2. Verify all DoD checkpoints
        3. Output task completion summary
      </action>
      <output>Task completion output, workflow_action_updated</output>
    </step_5_1>

  </phase_5>

  <phase_6 name="继续执行（Continue Execute）">
    <step_6_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Invoke x-ipe-dao-end-user-representative with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the context and full output to decide best next action."
          → DAO studies the complete context and decides the best next action
        ELSE (interact-with-human):
          → Present next task suggestion to human and wait for instruction
      </action>
      <constraints>
        - BLOCKING (manual): Human MUST confirm or redirect before proceeding
        - BLOCKING (auto): Proceed after DoD verification; auto-select next task via DAO
      </constraints>
      <output>Next action decided with execution context</output>
    </step_6_1>
    <step_6_2>
      <name>Execute Next Action</name>
      <action>
        Based on the decision from Step 6.1:
        1. Load the target task-based skill's SKILL.md
        2. Generate an execution plan from the skill's Execution Flow table
        3. Start execution from the skill's first phase/step
      </action>
      <constraints>
        - MUST load the skill before executing — do not skip skill loading
        - Execution follows the target skill's procedure, not this skill's
      </constraints>
      <output>Next task execution started</output>
    </step_6_2>
  </phase_6>

</procedure>
```

See [references/implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md) for detailed sub-procedures per step.

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-acceptance-test"
      condition: "Verify implementation with acceptance tests"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"   # triggers workflow status update when execution_mode == workflow-mode
  workflow_action_updated: true | false # true if update_workflow_action was called
  task_output_links:
    - "src/"
    - "tests/"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Code Implementation"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Context gathered (board queried + design learned)</name>
    <verification>Feature Data Model received with all links; agent can describe implementation plan from design</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>AAA scenarios generated OR special-case delegation invoked</name>
    <verification>Either AAA scenarios exist with coverage validated, or program_type triggered skill-creator/mcp-builder delegation (acceptance testing still required via feature-acceptance-test skill)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tool skills invoked and all assertions pass</name>
    <verification>All matched tool skills returned implementation_files, test_files, test_results, lint_status; aggregated validation report shows all pass (or delegation DoD satisfied)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Implementation matches technical design</name>
    <verification>Compare implemented components against design document</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Frontend matches current mockups</name>
    <verification>If feature has current mockups in specification, UI layout/components/styling match the mockup</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Special-case delegations used correctly (skill-creator / mcp-builder)</name>
    <verification>If design includes .github/skills/ files, created by x-ipe-meta-skill-creator; if it requires MCP server, built using mcp-builder skill (not directly)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Code follows YAGNI and KISS principles</name>
    <verification>No functionality beyond design spec; no unnecessary abstractions or over-engineering</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Linter passes and test coverage ≥80% for new code</name>
    <verification>Run ruff check / eslint with zero errors; run pytest --cov=src tests/ and check coverage report</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tracing decorators and redact annotations applied</name>
    <verification>Public functions have @x_ipe_tracing decorators; password/token/secret/key params have redact=[] set (skip if only skill files)</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>Workflow Action Updated</name>
    <verification>If execution_mode == "workflow-mode", called the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with status "done" and deliverables keyed dict</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

| Pattern | When | Then |
|---------|------|------|
| Orchestrator Flow | Code feature (backend/frontend/fullstack) | Generate AAA → route tool skills → validate → trace |
| Special-Case Delegation | program_type "skills" or MCP server | Bypass AAA, delegate to skill-creator/mcp-builder, verify DoD |
| Design Reference | Technical design references architecture | Read architecture docs, follow existing patterns, reuse utilities |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip reading design | Wrong implementation | Learn technical design first |
| Ignore architecture docs | Inconsistent patterns | Read referenced architecture |
| Skip AAA generation | No validation contract | Always generate scenarios first |
| Parallel tool skills | Context conflicts | Sequential invocation only |
| Add "nice to have" features | YAGNI violation | Only implement what's in design |
| Complex code for coverage | Maintenance nightmare | Keep simple, accept 80% |
| Ignore mockups | UI drifts from design | Use current mockups as visual spec |
| Copy-paste code | DRY violation | Extract reusable functions |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-code-implementation/references/examples.md) for detailed execution examples including:
- Standard backend+frontend feature with AAA orchestration
- Skills-type feature delegated to skill-creator
- AAA generation fallback to test-generation (Phase 1)
- Tool skill retry on failure
