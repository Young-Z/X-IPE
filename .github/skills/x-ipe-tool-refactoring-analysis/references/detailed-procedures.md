# Detailed Procedures Reference

This document contains detailed step-by-step procedures for the Refactoring Analysis skill.
Content moved from SKILL.md to keep the main file under 500 lines.

---

## Step 0: Check Quality Baseline - Detailed Procedure

**Action:** Check if project quality evaluation exists and use as baseline.

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

**Benefits of Using Baseline:**
- Skip re-evaluating already documented violations
- Focus analysis on scope-specific gaps
- Provide delta comparison in output
- Faster analysis with consistent metrics

---

## Step 2: Scope Reflection Loop - Detailed Procedure

**Action:** Iteratively expand scope until no new related code is found.

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
          - Add to working_scope.files
          - new_items_found = true
          - Log expansion reason

  2. FOR EACH module in working_scope.modules:
     a. IDENTIFY related modules:
        - Sibling modules
        - Parent modules
        - Child modules
     b. ASSESS if module should be included:
        - Tight coupling? -> Include
        - Shared state? -> Include
        - Independent? -> Skip
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
  - WARN: "Scope expansion exceeded 10 iterations. Review for circular dependencies."
```

---

## Steps 3-6: Quality Evaluation - Detailed Procedures

### Step 3 - Requirements Alignment

```
1. SEARCH x-ipe-docs/requirements/**/*.md for related docs
2. FOR EACH: Extract criteria, compare with code, identify gaps
3. COMPILE requirements_alignment: {status, gaps[], related_docs[]}
```

### Step 4 - Features Alignment

```
1. SEARCH x-ipe-docs/requirements/FEATURE-XXX/ for feature specs
2. FOR EACH: Read spec, compare behavior, identify gaps
3. COMPILE feature_alignment: {status, gaps[], feature_ids[]}
```

### Step 5 - Technical Spec Alignment

```
1. SEARCH for technical-design.md and architecture docs
2. FOR EACH: Extract structure/interfaces/patterns, compare, identify deviations
3. COMPILE technical_spec_alignment: {status, gaps[], spec_docs[]}
```

### Step 6 - Test Coverage

```
1. RUN coverage: pytest --cov | npm test --coverage | go test -cover
2. FOR EACH file: Get line/branch coverage, identify untested functions
3. IDENTIFY critical gaps: business logic, error handlers, edge cases
4. COMPILE test_coverage: {status, current_percentage, critical_gaps[]}
```

### Step 6b - Tracing Coverage (FEATURE-023-D)

```
1. SCAN code files for @x_ipe_tracing decorator usage:
   - grep -r "@x_ipe_tracing" src/
   - Count decorated vs total public functions

2. FOR EACH file in scope:
   - List public functions (def/async def at module level, class methods)
   - Check if decorated with @x_ipe_tracing
   - Flag missing decorators

3. CHECK sensitive parameter redaction:
   - Search for password, token, secret, key, auth parameters
   - Verify redact=[] is specified for these

4. COMPILE tracing_coverage: {
     status: passed|warning|failed,
     coverage_percentage: X%,
     untraced_functions: [],
     unredacted_params: []
   }
```

---

## Gap Types by Perspective

| Perspective | Gap Types |
|-------------|-----------|
| Requirements | undocumented, unimplemented, deviated |
| Features | missing, extra, deviated |
| Tech Spec | structure, interface, data_model, pattern |
| Test Coverage | business_logic, error_handling, edge_case |
| Tracing Coverage | untraced, unredacted, wrong_level |

---

## Step 7: Generate Refactoring Suggestions - Detailed Procedure

```
1. ANALYZE quality gaps to derive suggestions:
   FOR EACH gap in code_quality_evaluated:
     - requirements gaps -> Suggest documentation sync or code alignment
     - feature gaps -> Suggest feature compliance refactoring
     - tech spec gaps -> Suggest structural refactoring
     - test coverage gaps -> Suggest test-first refactoring approach

2. IDENTIFY applicable principles:
   a. SCAN code for principle violations:
      - Large files/classes -> SRP, SOLID
      - Duplicated code -> DRY
      - Complex logic -> KISS
      - Unused code -> YAGNI
      - Mixed concerns -> SoC (Separation of Concerns)

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
```

---

## Step 8: Scoring and Output - Detailed Procedure

### Dimension Scoring

```
1. CALCULATE dimension scores (1-10 each):
   FOR EACH dimension (requirements, features, tech_spec, test_coverage, tracing):
     score = 10 - SUM(violations x importance_weights)
     score = MAX(1, MIN(10, score))  # Clamp to 1-10

     # Derive status from score
     IF score >= 8: status = "aligned"
     ELSE IF score >= 6: status = "needs_attention"
     ELSE: status = "critical"

   Importance weights:
   - Critical (no tests, hardcoded secrets): 3
   - High (missing coverage, SRP/DRY violations): 2
   - Medium (outdated specs, missing docs): 1
   - Low (minor style issues): 0.5

2. CALCULATE overall_quality_score:
   overall_quality_score = weighted_average(
     requirements_score x 0.20,
     features_score x 0.20,
     tech_spec_score x 0.20,
     test_coverage_score x 0.20,
     tracing_score x 0.10,
     code_alignment_score x 0.10
   )
```

### Self-Review Checklist

```
1. READ the generated report completely
2. CHECK for:
   - Missing content or sections
   - Inconsistencies between summary and details
   - Scope items not evaluated
   - Gaps without proper severity assignment
   - Suggestions that don't match identified gaps
   - Principles without clear applications
3. IF problems found:
   - FIX the issues in the report
   - Note corrections made
```

### Human Presentation Format

```
Refactoring Analysis Complete

Scope: {file_count} files, {module_count} modules
Expansions: {expansion_count} iterations

Quality Assessment (Score -> Status):
- Requirements: {req_score}/10 -> {status}
- Features: {feature_score}/10 -> {status}
- Tech Spec: {tech_score}/10 -> {status}
- Test Coverage: {test_score}/10 ({current}%)
- Tracing: {tracing_score}/10

Score-to-Status: 8-10 aligned, 6-7 needs_attention, 1-5 critical

Overall Score: {score}/10

Refactoring Suggestion:
- Summary: {summary}
- Goals: {goal_count} identified
- Primary Principles: {principle_list}

Approve to proceed to Improve Code Quality Before Refactoring?
```
