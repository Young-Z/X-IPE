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

IMPORTANT: When `process_preference.auto_proceed == "auto"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Code Implementation"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      tech-design: "path | N/A | auto-detect"
      specification: "path | N/A | auto-detect"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill: "Feature Acceptance Test"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  feature_phase: "Code Implementation"

  # Required inputs
  feature_id: "{FEATURE-XXX}"

  # Git strategy (from .x-ipe.yaml, passed by workflow)
  git_strategy: "main-branch-only | dev-session-based"
  git_main_branch: "{auto-detected}"

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
  <field name="process_preference.auto_proceed" source="from caller (x-ipe-workflow-task-execution) or default 'manual'" />
  <field name="feature_id" source="from previous task (Technical Design) output or task board" />
  <field name="extra_context_reference" source="from workflow context or auto-detect from feature artifacts (x-ipe-docs/requirements/FEATURE-XXX/)" />
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

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Query Board | Get Feature Data Model from feature board | Feature data received |
| 2 | Learn Design | Read technical design document thoroughly | Design understood |
| 3 | Read Architecture | Read referenced architecture designs (if any) | Architecture understood |
| 4 | Generate AAA Scenarios | Create tagged test scenarios from spec + design | Scenarios generated with coverage |
| 5 | Route & Invoke | Semantic-match tool skills and invoke sequentially | All tool skills complete |
| 6 | Validate Results | Verify Assert clauses, run integration scenarios | All checks pass |
| 7 | Tracing | Add tracing decorators to implemented code | Tests still pass |
| 9 | Routing | DAO-assisted next task routing | Routing decision made |

BLOCKING: Step 4 → 5 is BLOCKED until AAA scenarios are generated with coverage validated.
BLOCKING: Step 5: If design needs changes → UPDATE technical design BEFORE implementing.
BLOCKING: Step 5.1 special-case delegations run BEFORE semantic routing.

---

## Execution Procedure

```xml
<procedure name="code-implementation">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Query Feature Board</name>
    <action>
      1. CALL x-ipe+feature+feature-board-management skill with operation=query_feature
      2. RECEIVE Feature Data Model (feature_id, title, version, status, specification_link, technical_design_link)
    </action>
    <constraints>
      - BLOCKING: Feature must exist on board with status "Designed"
    </constraints>
    <output>Feature Data Model with all links and context</output>
  </step_1>

  <step_2>
    <name>Learn Technical Design</name>
    <action>
      0. Resolve extra_context_reference inputs:
         - FOR EACH ref in [tech-design, specification]:
           IF workflow mode AND extra_context_reference.{ref} is a file path:
             READ the file at that path (use instead of corresponding *_link)
           ELIF extra_context_reference.{ref} is "auto-detect":
             Use existing discovery logic below
           ELIF extra_context_reference.{ref} is "N/A":
             Skip this context input
           ELSE (free-mode / absent):
             Use existing behavior
      1. READ technical_design_link from Feature Data Model
      2. UNDERSTAND Part 1 (Agent-Facing Summary) and Part 2 (Implementation Guide)
      3. NOTE references to architecture designs
      4. CHECK Design Change Log for updates
      5. CHECK specification.md for Linked Mockups section:
         a. IF mockups exist with status "current":
            - READ each current mockup file from x-ipe-docs/requirements/FEATURE-XXX/mockups/
            - Extract: layout structure, component placement, visual states, interactions, styling details
            - These mockup details MUST guide frontend implementation in Step 5
         b. IF mockups are marked "outdated" or absent: note and proceed
      6. CHECK if technical design includes skill files (`.github/skills/*/SKILL.md`):
         a. SCAN technical design for references to `.github/skills/` paths
         b. IF skill file(s) found: FLAG for delegation to `x-ipe-meta-skill-creator` in Step 5
         c. NOTE: Skill files MUST NOT be created directly — they require the skill creator process
      7. CHECK if specification or technical design requires an MCP server:
         a. SCAN for keywords: "MCP server", "MCP tool", "Model Context Protocol", "MCP endpoint"
         b. IF MCP server is required: FLAG for delegation to `mcp-builder` skill in Step 5
         c. NOTE: MCP servers MUST be built via `mcp-builder` skill to ensure protocol compliance
    </action>
    <constraints>
      - BLOCKING: Do NOT code until design is understood
      - If design is unclear -> STOP and clarify before proceeding
      - CRITICAL: If implementation reveals design issues during later steps, STOP, UPDATE technical-design.md, add to Design Change Log, then RESUME
    </constraints>
    <output>Complete understanding of implementation requirements, mockup references loaded (if applicable)</output>
  </step_2>

  <step_3>
    <name>Read Architecture Designs</name>
    <action>
      1. CHECK if technical design references architecture patterns
      2. IF no architecture references: skip this step
         ELSE: READ x-ipe-docs/architecture/technical-designs/{component}.md and UNDERSTAND common patterns, interfaces, integration requirements
    </action>
    <output>Architecture patterns understood (or skipped)</output>
  </step_3>

  <step_4>
    <name>Generate AAA Scenarios</name>
    <action>
      1. PARSE specification.md:
         a. Extract each acceptance criterion → create one @integration scenario per AC
            (Arrange = preconditions, Act = user action, Assert = expected outcome)
      2. PARSE technical-design.md Part 2:
         a. FOR EACH API endpoint/service method → create @backend happy-path + error-path scenarios
         b. FOR EACH UI component/event handler → create @frontend happy-path + error-path scenarios
         c. FOR EACH validation rule → create @backend validation scenario
         d. FOR EACH documented error/edge case → create scenario in matching layer
      3. TAG each scenario: @backend, @frontend, or @integration
      4. VALIDATE coverage: every AC has ≥1 scenario, every endpoint/component has happy + sad path
      5. IF context is large (>20 components): generate per-layer batches
         (see references/implementation-guidelines.md for batching procedure)
      6. IF AAA generation fails (ambiguous spec, insufficient detail):
         FALLBACK to x-ipe-tool-test-generation (Phase 1 coexistence)
    </action>
    <constraints>
      - MANDATORY: AAA format: @{tag} / Test Scenario: {name} / Arrange: / Act: / Assert:
      - BLOCKING: Do NOT proceed to Step 5 until scenarios generated and coverage validated
      - See references/implementation-guidelines.md for full AAA format specification
    </constraints>
    <output>List of tagged AAA scenarios with coverage summary</output>
  </step_4>

  <step_5>
    <name>Route and Invoke Tool Skills</name>
    <action>
      1. CHECK special-case delegations FIRST:
         a. IF program_type == "skills":
            BLOCKING: DELEGATE entire implementation to x-ipe-meta-skill-creator
            - Skip AAA generation output; skill-creator has its own testing
            - INVOKE x-ipe-meta-skill-creator with skill_name, skill_type, user_request from technical design
            - WAIT for completion; VERIFY skill-creator DoD passes
            - JUMP to Step 7 (skip Step 6)
         b. IF MCP server detected in spec/design:
            BLOCKING: DELEGATE to mcp-builder skill
            - INVOKE mcp-builder with context from technical design
            - WAIT for completion; VERIFY mcp-builder quality checks pass
            - JUMP to Step 7 (skip Step 6)
      2. SCAN .github/skills/x-ipe-tool-implementation-*/ for available tool skills
      3. FOR EACH tech_stack entry: semantically match to a discovered tool skill
         - Use LLM understanding to match (e.g., "Python/Flask" → x-ipe-tool-implementation-python)
         - IF no match: assign x-ipe-tool-implementation-general
         - IF general insufficient: signal "new tool skill needed"

           Response source (based on auto_proceed):
           IF process_preference.auto_proceed == "auto":
             → Log gap via x-ipe-dao-end-user-representative, continue with general tool
           ELSE (manual/stop_for_question):
             → Ask human for guidance
      4. FOR EACH matched tool skill (sequentially, backend first then frontend):
         a. FILTER AAA scenarios by matching layer tag
         b. INVOKE tool skill with: aaa_scenarios, source_code_path, feature_context
         c. RECEIVE: implementation_files, test_files, test_results, lint_status
      5. IF current mockups loaded in Step 2 AND feature has frontend/UI components:
         a. Pass mockup constraints to frontend tool skill invocation
         b. Tool skill MUST match implementation to mockup layout, components, styling
      6. COLLECT all tool skill outputs for validation in Step 6
    </action>
    <constraints>
      - BLOCKING: Special-case check (5.1) runs BEFORE semantic routing
      - CRITICAL: Tool skills invoked sequentially, NOT in parallel
      - MANDATORY: Use standard tool skill I/O contract (see references/implementation-guidelines.md)
      - MANDATORY: All internal markdown links MUST use full project-root-relative paths
    </constraints>
    <output>All tool skill outputs collected</output>
  </step_5>

  <step_6>
    <name>Validate Tool Skill Results</name>
    <action>
      1. FOR EACH tool skill output:
         a. Verify all Assert clauses in test_results: count pass/fail
         b. Verify lint_status == "pass"
      2. IF any tool skill has failing Asserts:
         a. Re-invoke ONLY the failed tool skill with original scenarios + error context
         b. IF retry succeeds: continue
         c. IF retry fails: preserve passing results, escalate failure

            Response source (based on auto_proceed):
            IF process_preference.auto_proceed == "auto":
              → Log failure via x-ipe-dao-end-user-representative, continue with partial results
            ELSE (manual/stop_for_question):
              → Escalate to human
      3. RUN @integration scenarios: verify cross-layer behavior with mocking
      4. IF integration fails: report contract mismatch with both tool skill outputs

         Response source (based on auto_proceed):
         IF process_preference.auto_proceed == "auto":
           → Log via x-ipe-dao-end-user-representative, continue
         ELSE (manual/stop_for_question):
           → Report to human
      5. PRODUCE aggregated report: per-skill pass/fail, integration results, overall status
    </action>
    <success_criteria>
      - All @backend Assert clauses pass
      - All @frontend Assert clauses pass
      - All @integration scenarios pass
      - All lint checks pass
    </success_criteria>
    <output>Aggregated validation report (PASS/FAIL)</output>
  </step_6>

  <step_7>
    <name>Apply Tracing Instrumentation</name>
    <action>
      1. IF no tracing infrastructure (no x_ipe.tracing module) or only skill/config files modified: skip this step
      2. ELSE:
         a. INVOKE x-ipe-tool-tracing-instrumentation skill for all modified files
         b. REVIEW proposed decorators (INFO for public, DEBUG for helpers)
         c. APPLY decorators with sensitive param redaction
         d. RE-RUN tests to verify functionality
    </action>
    <output>Tracing decorators applied; tests still pass</output>
  </step_7>

  <step_8>
    <name>Update Workflow Status</name>
    <action>
      1. IF execution_mode == "workflow-mode":
         a. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with:
            - workflow_name: {from context}
            - action: {workflow.action}
            - status: "done"
            - feature_id: {feature_id}
            - deliverables: {"impl-files": "{path to main implementation file(s)}", "impl-folder": "{path to implementation folder}"}
         b. Log: "Workflow action status updated to done"
      2. Verify all DoD checkpoints
      3. Output task completion summary
    </action>
    <output>Task completion output, workflow_action_updated</output>
  </step_8>

  <step_9>
    <name>Routing</name>
    <actions>
      Collect the full context and task_completion_output from this skill execution.

      IF process_preference.auto_proceed == "auto":
        → Invoke x-ipe-dao-end-user-representative with:
          type: "routing"
          completed_skill_output: {full task_completion_output YAML from this skill}
          next_task_based_skill: "{from output}"
          context: "Skill completed. Study the context and full output to decide best next action."
        → DAO studies the complete context and decides the best next action
      ELSE (manual):
        → Present next task suggestion to human and wait for instruction
    </actions>
    <constraints>
      - BLOCKING (manual): Human MUST confirm or redirect before routing to next task
      - BLOCKING (auto/stop_for_question): Proceed after DoD verification; auto-select next task via DAO
    </constraints>
    <routing>
      **Execute next task based on the decision from above with related task based skill**
    </routing>
  </step_9>

</procedure>
```

See [references/implementation-guidelines.md](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md) for detailed sub-procedures per step.

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill: "Feature Acceptance Test"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
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
    <name>Feature board queried for context</name>
    <verification>Feature Data Model received with all links</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Technical design learned and understood</name>
    <verification>Agent can describe implementation plan from design</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>AAA scenarios generated OR special-case delegation invoked</name>
    <verification>Either AAA scenarios exist with coverage validated, or program_type triggered skill-creator/mcp-builder delegation</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tool skills invoked and results collected</name>
    <verification>All matched tool skills returned implementation_files, test_files, test_results, lint_status</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All Assert clauses pass</name>
    <verification>Aggregated validation report shows all pass (or delegation DoD satisfied)</verification>
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
    <name>Skill files created via skill creator</name>
    <verification>If technical design includes .github/skills/ files, they were created by x-ipe-meta-skill-creator (not directly)</verification>
  </checkpoint>
  <checkpoint required="if-applicable">
    <name>MCP server built via mcp-builder</name>
    <verification>If specification or technical design requires MCP server, it was built using mcp-builder skill (not directly)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No extra features added (YAGNI)</name>
    <verification>Review code for functionality not specified in design</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Code is simple (KISS)</name>
    <verification>No unnecessary abstractions or over-engineering</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Linter passes</name>
    <verification>Run ruff check / eslint with zero errors</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Test coverage at least 80% for new code</name>
    <verification>Run pytest --cov=src tests/; check coverage report</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All public functions have @x_ipe_tracing decorators</name>
    <verification>Grep for public functions without decorators in modified files (skip if only skill files)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Sensitive parameters have redact=[] specified</name>
    <verification>Grep for password/token/secret/key params; verify redact is set (skip if only skill files)</verification>
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

### Pattern: Orchestrator Flow (Standard)

**When:** Starting implementation for a feature with code (backend/frontend/fullstack)
**Then:**
```
1. Generate AAA scenarios from spec + design
2. Route tech_stack entries to tool skills
3. Invoke tool skills sequentially (backend → frontend)
4. Validate all Assert clauses pass
5. Run @integration scenarios
6. Apply tracing
```

### Pattern: Special-Case Delegation

**When:** program_type is "skills" or MCP server detected
**Then:**
```
1. Bypass AAA generation entirely
2. Delegate to x-ipe-meta-skill-creator (skills) or mcp-builder (MCP)
3. Wait for delegation to complete
4. Verify delegated skill's DoD passes
5. Skip validation gate (Step 6)
```

### Pattern: Design Reference

**When:** Technical design references architecture patterns
**Then:**
```
1. Read referenced architecture docs
2. Follow existing patterns exactly
3. Reuse shared utilities
4. Ask if patterns unclear
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip reading design | Wrong implementation | Learn technical design first |
| Ignore architecture docs | Inconsistent patterns | Read referenced architecture |
| Skip AAA generation | No validation contract | Always generate scenarios first |
| Invoke tool skills in parallel | Context conflicts, unpredictable | Sequential invocation only |
| Add "nice to have" features | YAGNI violation | Only implement what is in design |
| Complex code for coverage | Maintenance nightmare | Keep simple, accept 80% coverage |
| Ignore mockups for frontend | UI drifts from approved design | Use current mockups as visual spec |
| Create skill files directly | Skill won't follow standards | Delegate to x-ipe-meta-skill-creator |
| Build MCP server directly | Won't follow MCP protocol standards | Delegate to mcp-builder skill |
| Copy-paste code | DRY violation | Extract reusable functions |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-code-implementation/references/examples.md) for detailed execution examples including:
- Standard backend+frontend feature with AAA orchestration
- Skills-type feature delegated to skill-creator
- AAA generation fallback to test-generation (Phase 1)
- Tool skill retry on failure
