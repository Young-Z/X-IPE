# Example: Refactoring Analysis Workflow (Pattern 3 - Phase Blocks)

Demonstrates Pattern 3 (Long Workflow) with nested Pattern 1 (YAML) and Pattern 2 (XML) inside phases.

```markdown
## Phase 1: Scope Identification (Complex Branching - YAML)

**Entry Criteria:** Refactoring request received with initial scope

```yaml
workflow:
  name: "Scope Expansion"
  steps:
    - step: 1
      name: "Identify Initial Files"
      action: "Locate the initial file or module to analyze"
      gate: "initial_files_identified == true"
      
    - step: 2
      name: "Map Dependencies"
      action: "Analyze imports and calls"
      branch:
        if: "dependency_type == direct"
        then: "Add to primary scope"
        else_if: "dependency_type == reverse"
        then: "Add to impact scope"
        else: "Mark as external - exclude"
      gate: "dependencies_mapped == true"
      
    - step: 3
      name: "Determine Boundary"
      action: "Define scope boundary"
      branch:
        if: "affected_files > 20"
        then: "Flag for human review - scope may be too large"
        else_if: "affected_files < 3"
        then: "Consider expanding scope for consistency"
        else: "Proceed with current scope"
      gate: "boundary_defined == true"

  critical_notes:
    - "CRITICAL: Include test files in scope analysis"
```

**Exit Criteria:**
- All affected files identified
- Dependency graph documented
- Scope boundary defined

---

## Phase 2: Current State Analysis (Linear with Constraints - XML)

**Entry Criteria:** Phase 1 complete + scope defined

```xml
<procedure name="Current State Analysis">
  <step_1>
    <name>Read Source Files</name>
    <action>
      1. Load each file in scope
      2. Parse structure and patterns
    </action>
    <constraints>
      - BLOCKING: Do not modify any files during analysis
    </constraints>
    <success_criteria>
      - All files loaded
      - Structure understood
    </success_criteria>
    <output>File structure map</output>
  </step_1>

  <step_2>
    <name>Document Patterns</name>
    <requires>File structure from step_1</requires>
    <action>
      1. Identify architecture patterns in use
      2. Note deviations from patterns
      3. Document code smells
    </action>
    <constraints>
      - CRITICAL: Be objective - document facts, not opinions
    </constraints>
    <success_criteria>
      - Patterns documented
      - Violations categorized
    </success_criteria>
    <output>Pattern analysis document</output>
  </step_2>

  <step_3>
    <name>Measure Metrics</name>
    <requires>Pattern analysis from step_2</requires>
    <action>
      1. Calculate lines of code
      2. Measure cyclomatic complexity
      3. Assess coupling metrics
    </action>
    <constraints>
      - MANDATORY: Include test coverage in metrics
    </constraints>
    <success_criteria>
      - All metrics calculated
      - Baseline established
    </success_criteria>
    <output>Metrics baseline document</output>
  </step_3>
</procedure>
```

**Exit Criteria:**
- All files analyzed
- Issues categorized by type
- Metrics baseline established

---

## Phase 3: Specification Gap Analysis (Simple)

**Entry Criteria:** Phase 2 complete + current state documented

Perform the following:
1. Load related feature specifications
2. Compare specs to actual implementation
3. Identify spec-code gaps
4. Document undocumented behaviors

CRITICAL: Gaps found may require spec updates before refactoring.

**Exit Criteria:**
- All related specs reviewed
- Gaps documented
- Decision made: update spec vs update code

---

## Phase 4: Test Coverage Assessment (Complex Branching - YAML)

**Entry Criteria:** Phase 3 complete + gaps documented

```yaml
workflow:
  name: "Test Coverage Assessment"
  steps:
    - step: 1
      name: "Run Tests"
      action: "Execute existing tests for scope"
      gate: "tests_executed == true"
      
    - step: 2
      name: "Calculate Coverage"
      action: "Measure coverage percentage"
      gate: "coverage_calculated == true"
      
    - step: 3
      name: "Evaluate Coverage"
      action: "Determine if coverage is adequate"
      branch:
        if: "coverage >= 80%"
        then: "Coverage adequate - proceed to Phase 5"
        else_if: "coverage >= 60%"
        then: "Create test improvement plan - can proceed with caution"
        else: "BLOCKING: Must improve tests before refactoring"
      gate: "evaluation_complete == true"
      
    - step: 4
      name: "Flag High-Risk Areas"
      action: "Identify untested code paths with high complexity"
      gate: "risks_flagged == true"

  blocking_rules:
    - "BLOCKING: Refactoring requires minimum 60% coverage"
```

**Exit Criteria:**
- Coverage measured
- Untested areas identified
- Test improvement plan created (if needed)

---

## Phase 5: Refactoring Plan (Simple)

**Entry Criteria:** Phase 4 complete + adequate coverage OR test plan created

Perform the following:
1. Prioritize issues by impact and effort
2. Define refactoring steps in order
3. Identify safe stopping points
4. Create rollback strategy

BLOCKING: Plan must be approved before execution.

**Exit Criteria:**
- Prioritized issue list
- Step-by-step refactoring plan
- Rollback strategy defined
- Human approval received

---

## Phase 6: Execution Preparation (Simple)

**Entry Criteria:** Phase 5 complete + plan approved

Perform the following:
1. Create feature branch
2. Ensure all tests pass on branch
3. Set up incremental commit strategy
4. Prepare for iterative validation

CRITICAL: Each commit should be independently reversible.

**Exit Criteria:**
- Branch created
- Tests passing
- Ready for refactoring execution
```
