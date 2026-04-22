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

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-assistant-user-representative-Engineer` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-code-refactor"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A"
    extra_context_reference:
      test-report: "path | N/A | auto-detect"
      specification: "path | N/A | auto-detect"

  # Task type attributes
  category: "feature-stage | standalone"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-acceptance-test"
      condition: "Re-verify after refactoring"
    - skill: "x-ipe-task-based-feature-closing"
      condition: "Close feature if refactoring is the final step"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

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
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />

  <field name="refactoring_scope.scope_level">
    <steps>
      1. IF caller provides scope_level → use provided value
      2. IF feature_id is provided → default to "feature"
      3. IF files[] is provided → default to "custom"
      4. ELSE → IF interaction_mode == "dao-represent-human-to-interact": ASK x-ipe-assistant-user-representative-Engineer for scope; ELSE: ASK human for scope
    </steps>
  </field>

  <field name="refactoring_scope.refactoring_purpose">
    <steps>
      1. IF caller provides → use provided value
      2. IF human describes intent → derive from description
      3. ELSE → IF interaction_mode == "dao-represent-human-to-interact": ASK x-ipe-assistant-user-representative-Engineer; ELSE: ASK human: "What is the purpose of this refactoring?"
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

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 Analyze Scope & Quality | Invoke `x-ipe-tool-refactoring-analysis`, self-validate findings | Analysis complete |
| 2. 审问之 — Inquire Thoroughly | 2.1 Sync Docs & Tests | Invoke `x-ipe-tool-code-quality-sync` | All aligned, coverage ≥ 80% |
| 3. 慎思之 — Think Carefully | 3.1 Generate Refactoring Plan | Design target structure, AI self-validates plan | Plan validated |
| 4. 明辨之 — Discern Clearly | 4.1 Execute Refactoring | Apply changes incrementally with tests | All tests pass |
| 5. 笃行之 — Practice Earnestly | 5.1 Validate & Complete | Verify improvement, update refs, apply tracing | DoD verified |
| 继续执行 | 6.1 Decide Next Action | DAO-assisted next task decision | Next action decided |
| 继续执行 | 6.2 Execute Next Action | Load skill, generate plan, execute | Execution started |

BLOCKING: Phase 1 → 2 requires verification that analysis identified all issues.
BLOCKING: Phase 3 → 4 requires confirmation that refactoring plan addresses identified issues (manual/stop_for_question: human confirms; auto: DAO confirms).
BLOCKING: Phase 4 halts if any test fails (must fix or revert).

---

## Execution Procedure

```xml
<procedure name="code-refactor">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">
    <step_1_1>
      <name>Analyze Scope & Quality</name>
      <action>
        1. INVOKE x-ipe-tool-refactoring-analysis with:
           - operation: "full_analysis"
           - scope: {from input refactoring_scope}
           - quality_baseline_path: "x-ipe-docs/planning/project-quality-evaluation.md"
        2. RECEIVE output: refactoring_scope (expanded), code_quality_evaluated,
           refactoring_suggestion, refactoring_principle, report_path
        3. AI self-critique — validate analysis against objective criteria:
           a. Every item in refactoring_scope maps to a measurable quality gap
           b. No suggestions contradict each other (e.g., "extract class" + "inline class" on same target)
           c. Suggestions stay within the requested scope — no scope creep
           d. Quality scores are consistent (e.g., high complexity score but low smell count = investigate)
        4. Collect unresolved_questions[] — ONLY genuine ambiguities:
           - Scope conflicts: "You asked to refactor module X, but the analysis shows module Y is the root cause — include Y?"
           - Priority conflicts: "Both DRY and performance improvements are needed but they conflict — which to prioritize?"
        5. IF unresolved_questions is EMPTY → analysis validated, proceed
        6. IF unresolved_questions is NON-EMPTY:
           IF process_preference.interaction_mode == "dao-represent-human-to-interact":
             → Invoke x-ipe-assistant-user-representative-Engineer with specific questions list
           ELSE:
             → Present ONLY the specific questions to human
           → Incorporate answers, update analysis
      </action>
      <constraints>
        - MUST NOT ask broad "are these findings correct?" — only ask specific, bounded questions
        - IF self-critique passes with zero questions → skip human/DAO entirely
      </constraints>
      <output>Validated analysis: refactoring_scope, code_quality_evaluated, suggestions, principles</output>
    </step_1_1>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <step_2_1>
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
    </step_2_1>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <step_3_1>
      <name>Generate Refactoring Plan</name>
      <action>
        1. ANALYZE current structure (sizes, smells, violations) using analysis output
        2. DESIGN target structure applying principles:
           - SOLID: Extract classes/modules for SRP violations
           - DRY: Plan abstractions
           - KISS: Simplifications
           - YAGNI: Remove unused code
        3. CREATE refactoring_plan with phases ordered by goal priority
        4. AI self-critique — validate plan against objective criteria:
           a. Every identified issue from Step 1 has a corresponding plan item
           b. No plan item exceeds the approved refactoring_scope
           c. Plan respects refactoring_principle constraints (no new dependencies, etc.)
           d. Phases are ordered so earlier phases don't break later ones
           e. Each phase is independently testable — can verify before moving on
        5. Collect unresolved_questions[] — ONLY genuine trade-offs:
           - "Extracting this module improves DRY but adds a new dependency — acceptable?"
           - "Two valid refactoring orders exist: A→B is safer but slower, B→A is faster but riskier"
        6. IF unresolved_questions is EMPTY → plan validated, proceed
        7. IF unresolved_questions is NON-EMPTY:
           IF process_preference.interaction_mode == "dao-represent-human-to-interact":
             → Invoke x-ipe-assistant-user-representative-Engineer with specific trade-off questions
           ELSE:
             → Present ONLY the specific trade-offs to human
           → Incorporate answers, update plan
      </action>
      <constraints>
        - MUST NOT ask broad "does this plan look right?" — only ask specific trade-off questions
        - IF self-critique passes with zero questions → skip human/DAO entirely
      </constraints>
      <output>Validated refactoring_plan with phases and principle mappings</output>
    </step_3_1>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <step_4_1>
      <name>Execute Refactoring</name>
      <action>
        0. TOOL SKILL ROUTING (config-filtered):
           a. DISCOVER: Scan .github/skills/x-ipe-tool-implementation-*/
           b. READ CONFIG: Read x-ipe-docs/config/tools.json → stages.validation.code_refactor
              - IF section missing/empty → config_active = false (all tools enabled)
              - ELSE → config_active = true (opt-in); force-enable general
           c. FILTER: IF config_active → only ENABLED tools participate
           d. SEMANTIC MATCH: Match tech_stack to enabled tool skill
           e. IF no match → fall back to inline refactoring (current behavior)
        FOR EACH phase in refactoring_plan:
          1. CREATE checkpoint: git commit -m "checkpoint: before phase {N}"
          2. GENERATE per-phase AAA scenarios describing target state
          3. INVOKE matched tool skill with operation: "refactor", AAA scenarios, source/test paths
             - Tool skill handles: code writing, test running, linting
             - feature_context optional; synthetic fallback: REFACTOR-{task_id}
          4. IF tool skill reports test failure:
             - Fix if import/reference issue
             - REVERT phase if behavior changed (orchestrator manages rollback)
             - Update test if change is legitimate
          5. COMMIT: git commit -m "refactor({scope}): {desc} [principle: {p}]"
      </action>
      <constraints>
        - BLOCKING: Must fix or revert if any test fails before continuing
        - CRITICAL: Structure changes only — preserve existing behavior
        - CRITICAL: Orchestrator manages checkpoints/commits — tool skills do NOT manage git
      </constraints>
      <output>Refactored code with incremental commits per phase</output>
    </step_4_1>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <step_5_1>
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
           Run workflow update script via bash (`python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_update_action.py`):
             - workflow_name: {from context}
             - action: "code_refactor"
             - status: "done"
             - feature_id: {feature_id}
             - deliverables: {"refactor-report": "{path}"}
        10. Verify DoD checkpoints and resolve any open questions

            Response source (based on interaction_mode):
            IF process_preference.interaction_mode == "dao-represent-human-to-interact":
              → Resolve open questions via x-ipe-assistant-user-representative-Engineer
            ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
              → Ask human for answers
        11. CREATE final commit
      </action>
      <success_criteria>
        - All tests passing
        - Quality score improved
        - All goals achieved or documented
        - Tracing preserved on existing code
      </success_criteria>
      <output>Refactoring summary with quality scores and tracing status</output>
    </step_5_1>
  </phase_5>

  <phase_6 name="继续执行（Continue Execute）">
    <step_6_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Invoke x-ipe-assistant-user-representative-Engineer with:
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

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage | standalone"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-acceptance-test"
      condition: "Re-verify after refactoring"
    - skill: "x-ipe-task-based-feature-closing"
      condition: "Close feature if refactoring is the final step"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "x-ipe-docs/refactoring/analysis-{context}.md"
    - "x-ipe-docs/refactoring/validation-{context}.md"
    - "{paths to refactored files}"

  # Feature context pass-through
  feature_id: "{from input refactoring_scope.feature_id or N/A}"

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
    <verification>x-ipe-tool-refactoring-analysis output received and issues identified</verification>
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

| Pattern | When | Then |
|---------|------|------|
| Full Flow | "refactor this code" | Analysis → sync → plan → execute incrementally → validate → commit |
| Rollback | Tests fail after change | STOP, analyze, REVERT if behavior changed, fix if import issue |
| Tracing | Moving/renaming functions | Keep @x_ipe_tracing decorators, preserve redact=[], add to new public functions |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Big bang refactor | High risk, hard to debug | Small incremental changes |
| Skip analysis/sync | Missing baseline | Always run analysis + sync first |
| Skip test runs | Silent regressions | Test after EVERY change |
| Change behavior | Refactoring preserves semantics | Structure only, same behavior |
---

## References

| File | Purpose |
|------|---------|
| [references/refactoring-techniques.md](.github/skills/x-ipe-task-based-code-refactor/references/refactoring-techniques.md) | Detailed procedures, input/output structures, tracing rules |
| [references/examples.md](.github/skills/x-ipe-task-based-code-refactor/references/examples.md) | Concrete execution examples |
