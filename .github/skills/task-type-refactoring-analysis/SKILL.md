---
name: task-type-refactoring-analysis
description: Analyze refactoring scope and evaluate code quality gaps. Use when starting a refactoring initiative. Iteratively expands scope until complete, then evaluates requirements, features, technical spec, and test coverage alignment. Triggers on requests like "analyze for refactoring", "evaluate refactoring scope", "assess code quality".
---

# Task Type: Refactoring Analysis

## Purpose

Analyze and expand refactoring scope, then evaluate code quality alignment by:
1. **Evaluate** initial refactoring scope from user input
2. **Reflect & Expand** scope iteratively until no new related code is found
3. **Assess** code quality across 4 perspectives (requirements, features, tech spec, test coverage)
4. **Suggest** refactoring improvements with applicable principles
5. **Output** finalized scope, code quality evaluation, and refactoring suggestions for next phase

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Refactoring Analysis |
| Category | code-refactoring-stage |
| Next Task Type | Improve Code Quality Before Refactoring |
| Require Human Review | Yes |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |
| initial_refactoring_scope | (required - no default) |

**initial_refactoring_scope Structure:**
```yaml
initial_refactoring_scope:
  files: [<list of file paths>]
  modules: [<list of module names>]
  description: "<user's refactoring intent>"
  reason: "<why refactoring is needed>"
```

---

## Skill/Task Completion Output Attributes

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: code-refactoring-stage
  status: completed | blocked
  next_task_type: Improve Code Quality Before Refactoring
  require_human_review: Yes
  auto_proceed: {from input Auto Proceed}
  task_output_links: [<path to analysis report>]
  
  # Dynamic attributes - MUST be passed to next task
  quality_baseline:
    exists: true | false
    evaluated_date: <date from report if exists>
    overall_score: <1-10 if exists>
    code_violations:
      file_size: [<files exceeding 800 lines>]
      approaching_threshold: [<files 500-800 lines>]
    feature_gaps: [<features with violations>]
    test_coverage: <percentage if available>
  
  refactoring_scope:
    files: [<expanded list of files>]
    modules: [<expanded list of modules>]
    dependencies: [<identified dependencies>]
    scope_expansion_log: [<log of scope expansions>]
    
  code_quality_evaluated:
    requirements_alignment:
      status: aligned | needs_update | not_found
      gaps: [<list of gaps>]
      related_docs: [<paths to requirement docs>]
      
    specification_alignment:
      status: aligned | needs_update | not_found
      gaps: [<list of gaps>]
      feature_ids: [<FEATURE-XXX>]
      spec_docs: [<paths to tech design docs>]
      
    test_coverage:
      status: sufficient | insufficient | no_tests
      line_coverage: <XX%>
      branch_coverage: <XX%>
      target_percentage: 80
      critical_gaps: [<untested areas>]
      external_api_mocked: true | false
      
    code_alignment:
      status: aligned | needs_attention | critical
      
      # File Size Analysis (threshold: ≤800 lines)
      file_size_violations:
        - file: <path>
          lines: <count>
          severity: high | medium
          recommendation: "<split suggestion>"
      files_approaching_threshold:
        - file: <path>
          lines: <count>
          buffer: <lines remaining>
      
      # SOLID Principles Assessment
      solid_assessment:
        srp: { status: good | partial | violation, notes: "<details>" }
        ocp: { status: good | partial | violation, notes: "<details>" }
        lsp: { status: good | partial | violation, notes: "<details>" }
        isp: { status: good | partial | violation, notes: "<details>" }
        dip: { status: good | partial | violation, notes: "<details>" }
      
      # KISS Principle Assessment
      kiss_assessment:
        over_engineering: { status: good | violation, notes: "<details>" }
        straightforward_logic: { status: good | violation, notes: "<details>" }
        minimal_dependencies: { status: good | violation, notes: "<details>" }
        clear_intent: { status: good | violation, notes: "<details>" }
      
      # Modular Design Assessment
      modular_design_assessment:
        module_cohesion: { status: good | partial | violation, notes: "<details>" }
        module_coupling: { status: good | partial | violation, notes: "<details>" }
        single_entry_point: { status: good | partial | violation, notes: "<details>" }
        folder_structure: { status: good | partial | violation, notes: "<details>" }
        reusability: { status: good | partial | violation, notes: "<details>" }
        testability: { status: good | partial | violation, notes: "<details>" }
      
      # Code Smell Detection
      code_smells:
        - smell: god_class | long_method | large_file | deep_nesting | too_many_params | duplicate_code
          file: <path>
          severity: high | medium | low
          details: "<description>"
      
    overall_quality_score: <1-10>
    
  refactoring_suggestion:
    summary: "<high-level description of suggested refactoring>"
    goals:
      - goal: "<specific improvement goal>"
        priority: high | medium | low
        rationale: "<why this goal matters>"
        principle: "<SOLID | DRY | KISS | YAGNI | Modular Design | etc.>"
    target_structure: "<description of desired structure after refactoring>"
    
  refactoring_principle:
    primary_principles:
      - principle: <SOLID | DRY | KISS | YAGNI | SoC | Modular Design | etc.>
        rationale: "<why this principle applies>"
        applications:
          - area: "<code area>"
            action: "<specific application>"
    secondary_principles:
      - principle: <name>
        rationale: "<supporting rationale>"
    constraints:
      - constraint: "<what to avoid or preserve>"
        reason: "<why this constraint exists>"
```

### Evaluation Thresholds Reference

> These thresholds align with `project-quality-board-management` skill.

| Category | Principle | Threshold |
|----------|-----------|-----------|
| Test | Line Coverage | ≥ 80% |
| Test | Branch Coverage | ≥ 70% |
| Test | Mock External APIs | Required |
| Code | File Size | ≤ 800 lines |
| Code | Function Size | ≤ 50 lines |
| Code | Class Size | ≤ 500 lines |
| Code | Cyclomatic Complexity | ≤ 10 |

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | initial_refactoring_scope provided | Yes |
| 2 | Target code exists and is accessible | Yes |
| 3 | Code compiles/runs without errors | Yes |

---

## Execution Flow

Execute Refactoring Analysis by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 0 | Check Quality Baseline | Check for existing project-quality-evaluation.md | Baseline loaded or skipped |
| 1 | Parse Initial Scope | Validate and parse initial_refactoring_scope | Scope parsed |
| 2 | Scope Reflection Loop | Iteratively expand scope until stable | No new scope found |
| 3 | Evaluate Requirements | Check alignment with requirement docs | Gaps documented |
| 4 | Evaluate Features | Check alignment with feature specs | Gaps documented |
| 5 | Evaluate Tech Spec | Check alignment with technical designs | Gaps documented |
| 6 | Evaluate Test Coverage | Analyze test coverage gaps | Coverage documented |
| 7 | Generate Refactoring Suggestions | Derive suggestions and principles from evaluation | Suggestions documented |
| 8 | Generate Output | Compile all output data models | **Human approves** |

**⛔ BLOCKING RULES:**
- Step 0 MUST check for baseline before analysis starts
- Step 2 MUST iterate until no new related code is discovered
- Step 7 MUST derive actionable suggestions with principles
- Step 8 MUST include all output data models

---

## Execution Procedure

### Step 0: Check Quality Baseline

**Action:** Check if project quality evaluation exists and use as baseline

```
1. CHECK for existing quality evaluation:
   - Path: x-ipe-docs/planning/project-quality-evaluation.md
   
2. IF file exists:
   a. READ the quality report
   b. EXTRACT relevant baseline data:
      - Overall quality score
      - Code alignment violations (file size, SOLID, KISS, modular design)
      - Test coverage metrics
      - Feature-by-feature gaps
      - Files approaching threshold
   c. STORE as quality_baseline:
      quality_baseline:
        exists: true
        evaluated_date: <from report>
        overall_score: <from report>
        code_violations:
          file_size: [<files exceeding 800 lines>]
          approaching_threshold: [<files 500-800 lines>]
        feature_gaps: [<features with violations>]
        test_coverage: <percentage if available>
   d. LOG: "Using existing quality baseline from {evaluated_date}"
   
3. IF file does not exist:
   a. SET quality_baseline.exists = false
   b. LOG: "No quality baseline found, will perform full analysis"
   
4. CONTINUE to Step 1
```

**Output:** quality_baseline (may be empty if no report exists)

**Benefits of Using Baseline:**
- Skip re-evaluating already documented violations
- Focus analysis on scope-specific gaps
- Provide delta comparison in output
- Faster analysis with consistent metrics

---

### Step 1: Parse Initial Scope

**Action:** Validate and normalize the initial refactoring scope

```
1. VALIDATE initial_refactoring_scope:
   - files: Must be valid paths
   - modules: Must be identifiable
   - description: Must describe intent
   
2. IF validation fails:
   → ASK human for clarification
   → Wait for response
   
3. INITIALIZE working scope:
   working_scope:
     files: [<from initial>]
     modules: [<from initial>]
     dependencies: []
     scope_expansion_log: []
```

**Output:** Validated working_scope

---

### Step 2: Scope Reflection Loop

**Action:** Iteratively expand scope until no new related code is found

```
iteration = 0
REPEAT:
  iteration += 1
  new_items_found = false
  
  1. FOR EACH file in working_scope.files:
     a. ANALYZE imports and dependencies
     b. IDENTIFY files that:
        - Import from this file
        - Are imported by this file
        - Share interfaces/types with this file
     c. FOR EACH discovered file:
        IF file NOT in working_scope.files:
          → Add to working_scope.files
          → new_items_found = true
          → Log expansion reason
  
  2. FOR EACH module in working_scope.modules:
     a. IDENTIFY related modules:
        - Sibling modules
        - Parent modules
        - Child modules
     b. ASSESS if module should be included:
        - Tight coupling? → Include
        - Shared state? → Include
        - Independent? → Skip
     c. Add qualifying modules
  
  3. REFLECT on current scope:
     a. Are there hidden dependencies?
     b. Are there configuration files?
     c. Are there test files?
     d. Are there documentation files?
  
  4. LOG expansion:
     scope_expansion_log.append({
       iteration: iteration,
       files_added: [<new files>],
       modules_added: [<new modules>],
       reason: "<why expanded>"
     })

UNTIL new_items_found = false OR iteration > 10

IF iteration > 10:
  → WARN: "Scope expansion exceeded 10 iterations. Review for circular dependencies."
```

**Output:** Finalized refactoring_scope with expansion log

---

### Steps 3-6: Evaluate Quality Perspectives

**Action:** Evaluate code quality across 4 perspectives

**Step 3 - Requirements Alignment:**
```
1. SEARCH x-ipe-docs/requirements/**/*.md for related docs
2. FOR EACH: Extract criteria, compare with code, identify gaps
3. COMPILE requirements_alignment: {status, gaps[], related_docs[]}
```

**Step 4 - Features Alignment:**
```
1. SEARCH x-ipe-docs/requirements/FEATURE-XXX/ for feature specs
2. FOR EACH: Read spec, compare behavior, identify gaps
3. COMPILE feature_alignment: {status, gaps[], feature_ids[]}
```

**Step 5 - Technical Spec Alignment:**
```
1. SEARCH for technical-design.md and architecture docs
2. FOR EACH: Extract structure/interfaces/patterns, compare, identify deviations
3. COMPILE technical_spec_alignment: {status, gaps[], spec_docs[]}
```

**Step 6 - Test Coverage:**
```
1. RUN coverage: pytest --cov | npm test --coverage | go test -cover
2. FOR EACH file: Get line/branch coverage, identify untested functions
3. IDENTIFY critical gaps: business logic, error handlers, edge cases
4. COMPILE test_coverage: {status, current_percentage, critical_gaps[]}
```

**Gap Types by Perspective:**
- Requirements: undocumented | unimplemented | deviated
- Features: missing | extra | deviated
- Tech Spec: structure | interface | data_model | pattern
- Test Coverage: business_logic | error_handling | edge_case

---

### Step 7: Generate Refactoring Suggestions

**Action:** Derive refactoring suggestions and principles based on quality evaluation

```
1. ANALYZE quality gaps to derive suggestions:
   FOR EACH gap in code_quality_evaluated:
     - requirements gaps → Suggest documentation sync or code alignment
     - feature gaps → Suggest feature compliance refactoring
     - tech spec gaps → Suggest structural refactoring
     - test coverage gaps → Suggest test-first refactoring approach
   
2. IDENTIFY applicable principles:
   a. SCAN code for principle violations:
      - Large files/classes → SRP, SOLID
      - Duplicated code → DRY
      - Complex logic → KISS
      - Unused code → YAGNI
      - Mixed concerns → SoC (Separation of Concerns)
   
   b. PRIORITIZE principles:
      - Primary: Core principles that MUST be applied
      - Secondary: Nice-to-have principles
   
3. FORMULATE goals:
   FOR EACH identified improvement:
     - Define specific, measurable goal
     - Assign priority based on impact
     - Document rationale
   
4. DEFINE target structure:
   - Describe desired code organization
   - Note key structural changes needed
   - List preserved elements (what NOT to change)

5. IDENTIFY constraints:
   - Backward compatibility requirements
   - API stability requirements
   - Performance constraints
   - External dependencies to preserve

6. COMPILE:
   refactoring_suggestion:
     summary: "<derived from analysis>"
     goals:
       - goal: "<specific goal>"
         priority: <high | medium | low>
         rationale: "<from gap analysis>"
     target_structure: "<desired end state>"
   
   refactoring_principle:
     primary_principles:
       - principle: <name>
         rationale: "<why applies>"
         applications:
           - area: "<code area>"
             action: "<specific action>"
     secondary_principles:
       - principle: <name>
         rationale: "<supporting reason>"
     constraints:
       - constraint: "<constraint>"
         reason: "<why>"
```

**Output:** refactoring_suggestion and refactoring_principle data models

---

### Step 8: Generate Output

**Action:** Compile final analysis and request human review

```
1. CALCULATE overall_quality_score:
   scores = []
   - requirements_alignment: aligned=10, needs_update=5, not_found=3
   - feature_alignment: aligned=10, needs_update=5, not_found=3
   - technical_spec_alignment: aligned=10, needs_update=5, not_found=3
   - test_coverage: sufficient=10, insufficient=5, no_tests=2
   
   overall_quality_score = average(scores)

2. GENERATE analysis report:
   - Save to x-ipe-docs/refactoring/analysis-{task_id}.md
   - Include full refactoring_scope
   - Include full code_quality_evaluated
   - Include full refactoring_suggestion
   - Include full refactoring_principle

3. PRESENT to human:
   "Refactoring Analysis Complete
   
   Scope: {file_count} files, {module_count} modules
   Expansions: {expansion_count} iterations
   
   Quality Assessment:
   - Requirements: {status}
   - Features: {status}
   - Tech Spec: {status}
   - Test Coverage: {current}% (target: 80%)
   
   Overall Score: {score}/10
   
   Refactoring Suggestion:
   - Summary: {summary}
   - Goals: {goal_count} identified
   - Primary Principles: {principle_list}
   
   Approve to proceed to Improve Code Quality Before Refactoring?"

4. WAIT for human approval
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | initial_refactoring_scope validated | Yes |
| 2 | Scope expansion loop completed (stable) | Yes |
| 3 | Requirements alignment evaluated | Yes |
| 4 | Feature alignment evaluated | Yes |
| 5 | Technical spec alignment evaluated | Yes |
| 6 | Test coverage evaluated | Yes |
| 7 | Refactoring suggestions generated | Yes |
| 8 | Refactoring principles identified | Yes |
| 9 | Analysis report generated | Yes |
| 10 | Human review approved | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

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

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Expanding scope infinitely | Analysis paralysis | Cap at 10 iterations, flag for review |
| Skipping documentation check | Miss alignment issues | Always check all 4 perspectives |
| Assuming test coverage sufficient | Risk in refactoring | Always run actual coverage analysis |
| Manual scope estimation | Miss dependencies | Use automated import analysis |

---

## Example

See [references/examples.md](references/examples.md) for concrete execution examples.
