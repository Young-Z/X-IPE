---
name: x-ipe-task-based-code-refactor
description: Execute code refactoring end-to-end — analyze scope, sync docs, plan, execute, and validate. Single entry point for all refactoring work. Invokes x-ipe-tool-refactoring-analysis and x-ipe-tool-code-quality-sync as tool steps. Triggers on requests like "refactor code", "execute refactoring", "analyze for refactoring", "code quality assessment".
---

# Task-Based Skill: Code Refactor

## Purpose

Execute safe, end-to-end code refactoring with full traceability by:
1. **Analyze** scope and evaluate quality gaps (via `x-ipe-tool-refactoring-analysis`)
2. **Sync** documentation and tests with current code (via `x-ipe-tool-code-quality-sync`)
3. **Plan** refactoring following suggestions and principles
4. **Execute** refactoring incrementally with test validation
5. **Validate** quality improvement and update references

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

This skill is the **single entry point** for all refactoring work. It orchestrates:
- `x-ipe-tool-refactoring-analysis` — scope expansion + quality evaluation
- `x-ipe-tool-code-quality-sync` — doc sync + test baseline

BLOCKING: If user requests "refactor", "analyze for refactoring", or "assess code quality" — this skill handles it. Do NOT redirect to separate analysis skills.

IMPORTANT: When `process_preference.auto_proceed == "auto"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Code Refactor"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A"
    extra_context_reference:
      test-report: "path | N/A | auto-detect"
      specification: "path | N/A | auto-detect"

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"

  # Required inputs
  refactoring_scope:
    scope_level: "feature | custom"
    feature_id: "{FEATURE-XXX}"
    refactoring_purpose: "<why refactoring is needed>"
    files: []
    modules: []
    description: "<user's refactoring intent>"

  # Tech context (optional — auto-detected if not provided)
  program_type: "frontend | backend | fullstack | cli | library | skills | mcp | ..."
  tech_stack: []
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />

  <field name="refactoring_scope.scope_level">
    <steps>
      1. IF caller provides scope_level → use provided value
      2. IF feature_id is provided → default to "feature"
      3. IF files[] is provided → default to "custom"
      4. ELSE → ASK human for scope
    </steps>
  </field>

  <field name="refactoring_scope.refactoring_purpose">
    <steps>
      1. IF caller provides → use provided value
      2. IF human describes intent → derive from description
      3. ELSE → ASK human: "What is the purpose of this refactoring?"
    </steps>
  </field>

  <field name="program_type">
    <steps>
      1. IF caller provides → use provided value
      2. ELSE → auto-detect from scope files (extensions, frameworks, project structure)
    </steps>
  </field>

  <field name="tech_stack">
    <steps>
      1. IF caller provides → use provided value
      2. ELSE → auto-detect from package.json, pyproject.toml, go.mod, etc.
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Refactoring scope provided</name>
    <verification>scope_level set; if feature: feature_id exists; if custom: files[] or description present</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Target code accessible</name>
    <verification>All listed files/modules can be read from filesystem</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Code compiles without errors</name>
    <verification>Run build/lint to confirm no pre-existing failures</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Analyze Scope & Quality | Invoke `x-ipe-tool-refactoring-analysis` | Analysis complete, human approves |
| 2 | Sync Docs & Tests | Invoke `x-ipe-tool-code-quality-sync` | All aligned, coverage ≥ 80% |
| 3 | Generate Refactoring Plan | Design target structure, propose plan | Human approves plan |
| 4 | Execute Refactoring | Apply changes incrementally with tests | All tests pass |
| 5 | Validate & Complete | Verify improvement, update refs, apply tracing | Human approves |

BLOCKING: Step 1 → 2 requires human review of analysis results.
BLOCKING: Step 3 → 4 requires human approval of refactoring plan.
BLOCKING: Step 4 halts if any test fails (must fix or revert).

---

## Execution Procedure

```xml
<procedure name="code-refactor">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Analyze Scope & Quality</name>
    <action>
      1. INVOKE x-ipe-tool-refactoring-analysis with:
         - operation: "full_analysis"
         - scope: {from input refactoring_scope}
         - quality_baseline_path: "x-ipe-docs/planning/project-quality-evaluation.md"
      2. RECEIVE output: refactoring_scope (expanded), code_quality_evaluated,
         refactoring_suggestion, refactoring_principle, report_path
      3. PRESENT analysis summary to human:
         - Overall quality score
         - Gaps per dimension
         - Suggested refactoring goals and principles
      4. Mode-aware gate:
         IF process_preference.auto_proceed == "auto":
           Proceed automatically. If concerns found, use x-ipe-dao-end-user-representative.
         ELSE:
           WAIT for human approval of analysis results.
    </action>
    <constraints>
      - BLOCKING: Do not proceed to Step 2 without approved analysis
    </constraints>
    <output>Approved analysis: refactoring_scope, code_quality_evaluated, suggestions, principles</output>
  </step_1>

  <step_2>
    <name>Sync Docs & Tests</name>
    <action>
      1. INVOKE x-ipe-tool-code-quality-sync with:
         - operation: "full_sync"
         - refactoring_scope: {from Step 1 output}
         - code_quality_evaluated: {from Step 1 output}
         - refactoring_suggestion: {pass-through from Step 1}
         - refactoring_principle: {pass-through from Step 1}
      2. RECEIVE output: updated code_quality_evaluated, validation report
      3. VERIFY all alignments "aligned" and coverage ≥ 80%
      4. IF any sync failed → present issues to human, decide to retry or proceed
    </action>
    <constraints>
      - BLOCKING: All alignment statuses must be "aligned" before proceeding
      - BLOCKING: Test coverage must be ≥ 80%
    </constraints>
    <output>Synced documentation, test baseline at 80%+</output>
  </step_2>

  <step_3>
    <name>Generate Refactoring Plan</name>
    <action>
      1. ANALYZE current structure (sizes, smells, violations) using analysis output
      2. DESIGN target structure applying principles:
         - SOLID: Extract classes/modules for SRP violations
         - DRY: Plan abstractions
         - KISS: Simplifications
         - YAGNI: Remove unused code
      3. CREATE refactoring_plan with phases ordered by goal priority
      4. VALIDATE plan against constraints from refactoring_principle
      5. Mode-aware gate:
         IF process_preference.auto_proceed == "auto":
            → CALL x-ipe-dao-end-user-representative with:
                message_context:
                  source: "ai"
                  calling_skill: "code-refactor"
                  task_id: "{task_id}"
                  feature_id: "N/A"
                  workflow_name: "N/A"
                  downstream_context: "Evaluating whether the generated refactoring plan should be approved or revised"
                  messages:
                    - content: "Approve refactoring plan"
                      preferred_dispositions: ["answer", "clarification"]
                human_shadow: false
            → IF disposition is "answer" or "approval" or "instruction": use approval decision
            → IF disposition is "clarification" or "reframe" or "critique": revise plan
            → IF disposition is "pass_through": escalate to human
         ELSE:
           → PRESENT plan to human, WAIT for approval
    </action>
    <constraints>
      - BLOCKING (manual/stop_for_question): Do not proceed to Step 4 without human approval of plan
    </constraints>
    <output>Approved refactoring_plan with phases and principle mappings</output>
  </step_3>

  <step_4>
    <name>Execute Refactoring</name>
    <action>
      FOR EACH phase in refactoring_plan:
        1. CREATE checkpoint: git commit -m "checkpoint: before phase {N}"
        2. Apply changes following principle_applied, update imports
        3. RUN tests after each change (based on program_type/tech_stack):
           - Backend/CLI: pytest (or equivalent)
           - Frontend: Vitest/Jest for JS logic tests
           - Fullstack: Run ALL test suites
        4. IF tests fail:
           - Fix if import/reference issue
           - REVERT if behavior changed
           - Update test if change is legitimate
        5. COMMIT: git commit -m "refactor({scope}): {desc} [principle: {p}]"
    </action>
    <constraints>
      - BLOCKING: Must fix or revert if any test fails before continuing
      - CRITICAL: Structure changes only — preserve existing behavior
    </constraints>
    <output>Refactored code with incremental commits per phase</output>
  </step_4>

  <step_5>
    <name>Validate & Complete</name>
    <action>
      1. UPDATE technical designs (component list, paths, Design Change Log)
      2. UPDATE feature specifications (file references)
      3. UPDATE requirements (implementation notes)
      4. RUN final test suite (coverage maintained or improved)
      5. VALIDATE goals achieved from refactoring_suggestion
      6. CALCULATE quality improvements (before/after scores)
      7. CHECK tracing preserved on moved/renamed functions
      8. IF tracing infrastructure exists:
         - INVOKE x-ipe-tool-tracing-instrumentation for new files/functions
         - RE-RUN tests, UPDATE tracing counts
      9. IF execution_mode == "workflow-mode":
         Call update_workflow_action of x-ipe-app-and-agent-interaction MCP:
           - workflow_name: {from context}
           - action: "code_refactor"
           - status: "done"
           - feature_id: {feature_id}
           - deliverables: {"refactor-report": "{path}"}
      10. Mode-aware review gate:
          IF process_preference.auto_proceed == "auto":
            Skip human review. Resolve open questions via x-ipe-dao-end-user-representative.
          ELSE:
            PRESENT summary to human, WAIT for approval.
      11. CREATE final commit
    </action>
    <success_criteria>
      - All tests passing
      - Quality score improved
      - All goals achieved or documented
      - Tracing preserved on existing code
    </success_criteria>
    <output>Refactoring summary with quality scores and tracing status</output>
  </step_5>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill: null
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "x-ipe-docs/refactoring/analysis-{context}.md"
    - "x-ipe-docs/refactoring/validation-{context}.md"
    - "{paths to refactored files}"

  refactoring_summary:
    files_modified: "<count>"
    files_created: "<count>"
    files_deleted: "<count>"
    principles_applied:
      - principle: "<name>"
        application_count: "<count>"
        areas: "<list>"
    goals_achieved:
      - goal: "<name>"
        status: "achieved | partial | skipped"
        notes: "<details>"

  code_quality_evaluated:
    quality_score_before: "<1-10>"
    quality_score_after: "<1-10>"
    test_coverage:
      before: "<percentage>"
      after: "<percentage>"
      status: "maintained | improved | degraded"
    references_updated:
      requirements: "<count>"
      specifications: "<count>"
      technical_designs: "<count>"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Analysis completed and approved</name>
    <verification>x-ipe-tool-refactoring-analysis output received and reviewed</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Documentation synced</name>
    <verification>x-ipe-tool-code-quality-sync completed, all alignments "aligned"</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All planned changes executed</name>
    <verification>Compare completed phases against refactoring_plan</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All tests passing</name>
    <verification>Run full test suite with zero failures</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test coverage maintained or improved</name>
    <verification>Compare coverage before/after, verify no regression</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Quality score improved</name>
    <verification>Compare quality_score_before vs quality_score_after</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All references updated</name>
    <verification>Tech designs, feature specs, requirements all reflect new structure</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All changes committed</name>
    <verification>Clean git status with no uncommitted changes</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tracing preserved and applied</name>
    <verification>Existing decorators preserved; new public functions have @x_ipe_tracing</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Full Refactoring Flow

**When:** User says "refactor this code"
**Then:**
```
1. Step 1: Invoke analysis tool → get scope, quality, suggestions
2. Step 2: Invoke sync tool → align docs, reach 80% coverage
3. Step 3: Generate plan from suggestions → human approval
4. Step 4: Execute incrementally with tests
5. Step 5: Validate, update refs, commit
```

### Pattern: Rollback on Failure

**When:** Tests fail after a change
**Then:**
```
1. STOP current work
2. Analyze failure cause
3. REVERT if behavior changed
4. Fix if import/reference issue
5. Update test if change is legitimate
```

### Pattern: Tracing Preservation

**When:** Moving, splitting, or renaming functions
**Then:**
```
1. Keep @x_ipe_tracing decorators on moved functions
2. Preserve redact=[] parameters
3. Add decorators to new public functions in split modules
4. Apply x-ipe-tool-tracing-instrumentation for new code
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Big bang refactor | High risk, hard to debug failures | Small incremental changes |
| Skip analysis step | Missing scope, quality gaps | Always run analysis tool first |
| Skip doc sync | Refactoring without baseline | Always run sync tool first |
| Skip test runs | Silent regressions | Test after EVERY change |
| Change behavior | Refactoring must preserve semantics | Structure only, same behavior |

---

## References

| File | Purpose |
|------|---------|
| [references/refactoring-techniques.md](.github/skills/x-ipe-task-based-code-refactor/references/refactoring-techniques.md) | Detailed procedures, input/output structures, tracing rules |
| [references/examples.md](.github/skills/x-ipe-task-based-code-refactor/references/examples.md) | Concrete execution examples |
