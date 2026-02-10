---
name: x-ipe-task-based-refactoring-analysis
description: Analyze refactoring scope and evaluate code quality gaps. Use when starting a refactoring initiative. Iteratively expands scope until complete, then evaluates requirements, features, technical spec, and test coverage alignment. Triggers on requests like "analyze for refactoring", "evaluate refactoring scope", "assess code quality".
---

# Task-Based Skill: Refactoring Analysis

## Purpose

Analyze and expand refactoring scope, then evaluate code quality alignment by:
1. **Check** existing quality baseline for prior evaluation data
2. **Evaluate** initial refactoring scope from user input
3. **Reflect & Expand** scope iteratively until no new related code is found
4. **Assess** code quality across 5 perspectives (requirements, features, tech spec, test coverage, tracing)
5. **Suggest** refactoring improvements with applicable principles
6. **Output** finalized scope, code quality evaluation, and refactoring suggestions for next phase

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

This skill is part of the **code-refactoring-stage** chain:
1. `x-ipe-task-based-refactoring-analysis` - produces scope, evaluation, suggestions (this skill)
2. `x-ipe-task-based-improve-code-quality` - syncs docs with code
3. `x-ipe-task-based-code-refactor` - executes refactoring

**If user requests "refactor" directly without prior analysis:**
-> REDIRECT to this skill to start the proper chain.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Refactoring Analysis"

  # Task type attributes
  category: "code-refactoring-stage"
  next_task_based_skill: "Improve Code Quality Before Refactoring"
  require_human_review: "yes"

  # Required inputs
  auto_proceed: false
  initial_refactoring_scope:
    files: [<list of file paths>]
    modules: [<list of module names>]
    description: "<user's refactoring intent>"
    reason: "<why refactoring is needed>"

  # Context (from project)
  quality_baseline_path: "x-ipe-docs/planning/project-quality-evaluation.md"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>initial_refactoring_scope provided</name>
    <verification>Validate files exist, modules identifiable, description present</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Target code exists and is accessible</name>
    <verification>All listed files/modules can be read</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Code compiles/runs without errors</name>
    <verification>Run build/lint to confirm no pre-existing failures</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 0 | Check Quality Baseline | Check for existing project-quality-evaluation.md | Baseline loaded or skipped |
| 1 | Parse Initial Scope | Validate and parse initial_refactoring_scope | Scope parsed |
| 2 | Scope Reflection Loop | Iteratively expand scope until stable | No new scope found |
| 3 | Evaluate Requirements | Check alignment with requirement docs | Gaps documented |
| 4 | Evaluate Features | Check alignment with feature specs | Gaps documented |
| 5 | Evaluate Tech Spec | Check alignment with technical designs | Gaps documented |
| 6 | Evaluate Test Coverage | Analyze test and tracing coverage gaps | Coverage documented |
| 7 | Generate Suggestions | Derive suggestions and principles from evaluation | Suggestions documented |
| 8 | Generate Output | Compile all output data models, self-review, present | Human approves |

BLOCKING: Step 0 MUST check for baseline before analysis starts.
BLOCKING: Step 2 MUST iterate until no new related code is discovered.
BLOCKING: Step 7 MUST derive actionable suggestions with principles.
BLOCKING: Step 8 MUST include all output data models.

---

## Execution Procedure

CRITICAL: For detailed sub-steps, scoring formulas, and gap type definitions, see [references/detailed-procedures.md](references/detailed-procedures.md).

```xml
<procedure name="refactoring-analysis">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_0>
    <name>Check Quality Baseline</name>
    <action>
      1. CHECK for existing quality evaluation at quality_baseline_path
      2. IF exists: READ report, EXTRACT baseline data (scores, violations, gaps)
      3. IF not exists: SET quality_baseline.exists = false
    </action>

    <output>quality_baseline (populated or empty)</output>
  </step_0>

  <step_1>
    <name>Parse Initial Scope</name>
    <action>
      1. VALIDATE initial_refactoring_scope (files are valid paths, modules identifiable, description present)
      2. IF validation fails: ASK human for clarification, WAIT for response
      3. INITIALIZE working_scope with files, modules, empty dependencies and expansion log
    </action>
    <constraints>
      - BLOCKING: All file paths must resolve to existing files
    </constraints>
    <output>Validated working_scope</output>
  </step_1>

  <step_2>
    <name>Scope Reflection Loop</name>
    <action>
      1. FOR EACH file: ANALYZE imports/dependencies, IDENTIFY importing/imported/shared-interface files
      2. FOR EACH module: IDENTIFY sibling/parent/child modules, ASSESS coupling (tight coupling or shared state -> include)
      3. REFLECT: check for hidden dependencies, config files, test files, documentation files
      4. LOG expansion with iteration count, files/modules added, reason
    </action>
    <constraints>
      - BLOCKING: REPEAT until no new items found OR iteration > 10
      - CRITICAL: If iteration > 10, WARN about possible circular dependencies
    </constraints>
    <output>Finalized refactoring_scope with expansion log</output>
  </step_2>

  <step_3_to_6>
    <name>Evaluate Quality Perspectives</name>
    <action>
      Step 3 - Requirements: SEARCH x-ipe-docs/requirements/**/*.md, extract criteria, compare with code, identify gaps
      Step 4 - Features: SEARCH x-ipe-docs/requirements/FEATURE-XXX/, read specs, compare behavior, identify gaps
      Step 5 - Tech Spec: SEARCH for technical-design.md and architecture docs, compare structure/interfaces/patterns
      Step 6 - Test Coverage: RUN coverage tool (pytest/npm/go), analyze line/branch coverage, identify critical gaps
      Step 6b - Tracing: SCAN for @x_ipe_tracing decorators, check coverage and sensitive param redaction
    </action>
    <constraints>
      - CRITICAL: Evaluate ALL 5 perspectives even if docs are missing (set status: not_found)
      - CRITICAL: Gap types per perspective:
        Requirements: undocumented|unimplemented|deviated
        Features: missing|extra|deviated
        Tech Spec: structure|interface|data_model|pattern
        Test: business_logic|error_handling|edge_case
        Tracing: untraced|unredacted|wrong_level
    </constraints>
    <output>code_quality_evaluated with all dimension alignments</output>
  </step_3_to_6>

  <step_7>
    <name>Generate Refactoring Suggestions</name>
    <action>
      1. ANALYZE quality gaps: requirements gaps -> doc sync; feature gaps -> compliance refactoring; tech spec gaps -> structural refactoring; test gaps -> test-first approach
      2. SCAN code for principle violations: large files -> SRP/SOLID; duplicated code -> DRY; complex logic -> KISS; unused code -> YAGNI; mixed concerns -> SoC
      3. PRIORITIZE principles into primary (MUST apply) and secondary (nice-to-have)
      4. FORMULATE specific, measurable goals with priority and rationale
      5. DEFINE target structure and identify constraints (backward compat, API stability, performance)
    </action>
    <constraints>
      - BLOCKING: Every suggestion must trace back to a documented gap
      - CRITICAL: Constraints must include backward compatibility and API stability
    </constraints>
    <output>refactoring_suggestion and refactoring_principle data models</output>
  </step_7>

  <step_8>
    <name>Generate Output</name>
    <action>
      1. CALCULATE dimension scores (1-10): score = 10 - SUM(violations x importance_weights), clamped to 1-10
      2. DERIVE status: 8-10 = aligned, 6-7 = needs_attention, 1-5 = critical
      3. CALCULATE overall_quality_score as weighted average (req 0.20, feat 0.20, tech 0.20, test 0.20, tracing 0.10, code_alignment 0.10)
      4. GENERATE analysis report to x-ipe-docs/refactoring/analysis-{task_id}.md
      5. SELF-REVIEW: read report, check for missing content, inconsistencies, unmatched suggestions
      6. PRESENT summary to human, WAIT for approval
    </action>
    <success_criteria>
      - All output data models populated
      - Report self-review completed with no unresolved issues
      - Human approves to proceed
    </success_criteria>
    <output>Complete analysis report, human approval</output>
  </step_8>

</procedure>
```

---

## Output Result

See [references/output-schema.md](references/output-schema.md) for complete output data model schema.

```yaml
task_completion_output:
  category: "code-refactoring-stage"
  status: completed | blocked
  next_task_based_skill: "Improve Code Quality Before Refactoring"
  require_human_review: "yes"
  task_output_links:
    - "x-ipe-docs/refactoring/analysis-{task_id}.md"

  # Dynamic attributes - MUST be passed to next task
  quality_baseline:
    exists: true | false
    evaluated_date: "<date>"
    overall_score: "<1-10>"
  refactoring_scope:
    files: [<expanded file list>]
    modules: [<expanded module list>]
    dependencies: [<identified dependencies>]
    scope_expansion_log: [<log entries>]
  code_quality_evaluated:
    requirements_alignment: { score: "<1-10>", status: "<aligned|needs_attention|critical>", gaps: [] }
    specification_alignment: { score: "<1-10>", status: "<aligned|needs_attention|critical>", gaps: [] }
    test_coverage: { score: "<1-10>", line_coverage: "<XX%>", critical_gaps: [] }
    code_alignment: { score: "<1-10>", file_size_violations: [], solid_assessment: {}, kiss_assessment: {} }
    overall_quality_score: "<1-10>"
  refactoring_suggestion:
    summary: "<high-level description>"
    goals: [{ goal: "<specific goal>", priority: "<high|medium|low>", rationale: "<why>" }]
    target_structure: "<desired end state>"
  refactoring_principle:
    primary_principles: [{ principle: "<name>", rationale: "<why>", applications: [] }]
    secondary_principles: [{ principle: "<name>", rationale: "<why>" }]
    constraints: [{ constraint: "<what>", reason: "<why>" }]
```

**Evaluation Thresholds:** Line Coverage >=80%, File Size <=800 lines, Function Size <=50 lines

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>initial_refactoring_scope validated</name>
    <verification>All files/modules resolved and accessible</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Scope expansion loop completed (stable)</name>
    <verification>Loop terminated with no new items or at iteration cap</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All quality perspectives evaluated</name>
    <verification>Requirements, features, tech spec, test coverage, and tracing all have status and gaps</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Refactoring suggestions generated with principles</name>
    <verification>refactoring_suggestion and refactoring_principle data models populated</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Analysis report generated and self-reviewed</name>
    <verification>Report at x-ipe-docs/refactoring/analysis-{task_id}.md, no unresolved issues</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human review approved</name>
    <verification>Human explicitly approved the analysis results</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Deep Dependency Expansion

**When:** Initial scope has complex dependencies
**Then:**
```
1. Start with direct imports only
2. Expand to shared interfaces
3. Expand to shared state/config
4. Stop at package/module boundaries
```

### Pattern: No Documentation Found

**When:** Code has no requirement/feature/tech docs
**Then:**
```
1. Set status: not_found
2. Note in gaps: "Documentation missing"
3. Recommend creating docs before refactoring
4. Continue with test coverage evaluation
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Expanding scope infinitely | Analysis paralysis | Cap at 10 iterations, flag for review |
| Skipping documentation check | Miss alignment issues | Always check all 5 perspectives |
| Assuming test coverage sufficient | Risk in refactoring | Always run actual coverage analysis |
| Manual scope estimation | Miss dependencies | Use automated import analysis |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.
