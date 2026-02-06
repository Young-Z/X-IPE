---
name: project-quality-board-management
description: Generate and manage project quality evaluation reports from feature perspective. Evaluates requirements, features, test coverage, and code alignment status with gap analysis. Generates consistent markdown reports to x-ipe-docs/quality-evaluation folder. Triggers on requests like "evaluate project quality", "generate quality report", "assess code alignment".
---

# Project Quality Board Management

## Purpose

AI Agents follow this skill to generate and manage project-wide quality evaluation reports. This skill evaluates the project from a **feature perspective**, analyzing:

1. **Requirements Alignment** - Do features match documented requirements?
2. **Feature Coverage** - Are all features properly specified and implemented?
3. **Test Coverage** - Is test coverage sufficient across features?
4. **Code Alignment** - Does code implementation match specifications?

**Operations:**
1. **Generate** quality evaluation report
2. **Update** existing report with new evaluation
3. **Query** quality status for specific features
4. **Compare** quality between evaluation snapshots

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.
- Learn `task-type-refactoring-analysis` skill to understand `refactoring_suggestion` and `refactoring_principle` data models for integration.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Report Output Location

Quality evaluation reports are stored in:
```
x-ipe-docs/quality-evaluation/
```

### File Naming Convention (FEATURE-024 Integration)

The quality evaluation UI displays up to **5 most recent versions** with a timeline interface.

| File | Description |
|------|-------------|
| `project-quality-evaluation.md` | **Current/Latest** evaluation report |
| `project-quality-evaluation-v{N}.md` | Historical version N (v1, v2, v3, etc.) |

**Version Number Calculation:**
- Current version = `max(existing version numbers) + 1`
- Example: If v1, v2, v3 exist → current file displays as "v4"

### Versioning Workflow

When generating a **new report**, follow this workflow:

```
1. CHECK if x-ipe-docs/quality-evaluation/ folder exists
   - IF NOT: Create folder

2. CHECK if project-quality-evaluation.md exists
   - IF YES:
     a. SCAN for existing versioned files (project-quality-evaluation-v*.md)
     b. FIND max version number among existing files
     c. RENAME current file to project-quality-evaluation-v{max+1}.md
     d. IF more than 4 versioned files exist:
        - DELETE the oldest versioned file (lowest version number)
        - Keep only 4 historical + 1 current = 5 total

3. CREATE new project-quality-evaluation.md with fresh evaluation

4. VERIFY: Folder should contain at most:
   - 1 current file: project-quality-evaluation.md
   - Up to 4 historical: project-quality-evaluation-v{N}.md
```

**Example:**
```
Before generating new report:
  project-quality-evaluation.md      (current, displayed as v3)
  project-quality-evaluation-v2.md   (previous)
  project-quality-evaluation-v1.md   (oldest)

After generating new report:
  project-quality-evaluation.md      (NEW, displayed as v4)
  project-quality-evaluation-v3.md   (was current, now versioned)
  project-quality-evaluation-v2.md   (unchanged)
  project-quality-evaluation-v1.md   (unchanged)
```

Report header includes:
- **Project Version**: From `pyproject.toml` version field
- **Evaluated Date**: Timestamp of last evaluation

---

## Quality Evaluation Data Model

```yaml
QualityEvaluation:
  # Metadata
  evaluation_id: QE-{YYYYMMDD}-{sequence}
  generated_at: <ISO timestamp>
  generated_by: <agent nickname>
  scope: project | feature | module
  
  # Summary Metrics
  overall_score: <1-10>
  health_status: healthy | attention_needed | critical
  
  # Feature-Level Evaluations
  # Each dimension scored 1-10 based on principle violations and importance
  # Status derived: 8-10 = aligned, 6-7 = needs_attention, 1-5 = critical
  features:
    - feature_id: FEATURE-XXX
      feature_name: "<name>"
      feature_score: <1-10>
      status: aligned | needs_attention | critical | planned
      
      requirements_alignment:
        score: <1-10>  # Calculated from violations × importance weights
        status: aligned | needs_attention | critical | planned
        requirement_docs: [<paths>]
        gaps:
          - type: undocumented | unimplemented | deviated
            description: "<gap description>"
            severity: high | medium | low
            importance_weight: <0.5-3>  # Based on principle importance
      
      specification_alignment:
        score: <1-10>
        status: aligned | needs_attention | critical | planned
        spec_doc: "<path>"
        gaps:
          - type: missing | outdated | incorrect
            description: "<gap description>"
            severity: high | medium | low
            importance_weight: <0.5-3>
      
      test_coverage:
        score: <1-10>
        status: aligned | needs_attention | critical
        line_coverage: <XX%>
        branch_coverage: <XX%>
        critical_untested:
          - area: "<untested area>"
            risk: high | medium | low
            importance_weight: <0.5-3>
      
      code_alignment:
        score: <1-10>
        status: aligned | needs_attention | critical
        implementation_files: [<paths>]
        gaps:
          - type: structure | behavior | interface
            description: "<gap description>"
            severity: high | medium | low
            importance_weight: <0.5-3>
  
  # Aggregated Gaps
  priority_gaps:
    high: [<gap references>]
    medium: [<gap references>]
    low: [<gap references>]
  
  # Refactoring Suggestions (from task-type-refactoring-analysis)
  refactoring_suggestions:
    has_suggestions: true | false
    source: "<evaluation_id or task_id that generated suggestions>"
    
    suggestions:
      - feature_id: FEATURE-XXX
        summary: "<high-level description>"
        goals:
          - goal: "<specific improvement goal>"
            priority: high | medium | low
            rationale: "<why this goal matters>"
        target_structure: "<description of desired structure>"
        
        principles:
          primary:
            - principle: <SOLID | DRY | KISS | YAGNI | SoC | etc.>
              rationale: "<why this principle applies>"
              applications:
                - area: "<code area>"
                  action: "<specific application>"
          secondary:
            - principle: <name>
              rationale: "<supporting rationale>"
          constraints:
            - constraint: "<what to avoid or preserve>"
              reason: "<why>"
  
  # Recommendations
  recommendations:
    - priority: <1-N>
      category: requirements | specification | testing | code | refactoring
      action: "<recommended action>"
      affected_features: [<feature_ids>]
```

---

## Operations

### Operation 1: Generate Quality Report

**When:** Need to evaluate project quality
**Input:** Optional scope filter (all | feature_ids[] | module_paths[])

```
1. DETERMINE scope:
   - Default: all features in project
   - If feature_ids provided: filter to those features
   - If module_paths provided: find features affecting those modules

2. DISCOVER features:
   FOR project scope:
     - SCAN x-ipe-docs/requirements/FEATURE-* directories
     - BUILD feature list with metadata
   
3. FOR EACH feature:
   a. EVALUATE requirements alignment (see Evaluation Procedures)
   b. EVALUATE specification alignment
   c. EVALUATE test coverage
   d. EVALUATE code alignment
   e. COLLECT violations per category (requirements, spec, test, code)
   f. CALCULATE feature status and score

4. AGGREGATE results:
   - Calculate overall_score (weighted average, exclude planned features)
   - Determine health_status
   - Collect priority_gaps
   - Generate recommendations

5. GENERATE report following this structure:
   a. Executive Summary (scores, key findings)
   b. Evaluation Principles (thresholds/methods ONLY - no results)
   c. Feature-by-Feature Evaluation (overview table)
   d. Violation Details by Feature:
      - FOR EACH feature with violations:
        - Requirements Violations section
        - Specification Violations section
        - Test Coverage Violations section
        - Code Alignment Violations section
        - Tracing Coverage Violations section (FEATURE-023-D)
        - Security Violations section
   e. Files Approaching Threshold
   f. Priority Gaps Summary
   g. Recommendations
   h. Appendix (detailed metrics)

6. SAVE report (with versioning):
   a. ENSURE x-ipe-docs/quality-evaluation/ folder exists
   b. IF project-quality-evaluation.md exists:
      - SCAN for existing project-quality-evaluation-v*.md files
      - FIND max version number N
      - RENAME current to project-quality-evaluation-v{N+1}.md
      - IF more than 4 versioned files: DELETE oldest (lowest version)
   c. SAVE new report to x-ipe-docs/quality-evaluation/project-quality-evaluation.md
   d. UPDATE evaluated date in header

7. SELF-REVIEW report:
   a. READ the generated report completely
   b. CHECK for:
      - Missing content or sections
      - Inconsistencies between summary and details
      - Features mentioned but not evaluated
      - Gaps without proper severity assignment
      - Recommendations that don't match identified gaps
   c. IF problems found:
      - FIX the issues in the report
      - Note corrections made

8. RETURN evaluation summary
```

### Report Structure Rules

```
RULE 1: Evaluation Principles section
  - MUST come BEFORE Feature-by-Feature Evaluation
  - MUST only explain what principles are and thresholds
  - MUST NOT contain any evaluation results or status

RULE 2: Violation Details section
  - MUST be organized by feature
  - EACH feature section MUST have 6 subsections:
    - Requirements Violations
    - Specification Violations
    - Test Coverage Violations
    - Code Alignment Violations
    - Tracing Coverage Violations (FEATURE-023-D)
    - Security Violations
  - ONLY show features that have violations
  - Show "No violations" if a category is clean

RULE 3: Separation of concerns
  - Principles = WHAT we evaluate and HOW (thresholds)
  - Violations = RESULTS of evaluation per feature

RULE 4: Tracing Coverage Evaluation (FEATURE-023-D)
  - Threshold: ≥90% of public functions must have @x_ipe_tracing decorator
  - Check: All sensitive parameters (password, token, secret, key) have redact=[]
  - Levels: API endpoints = INFO, Business logic = INFO, Utilities = DEBUG
  - Report: List untraced functions and unredacted sensitive params

RULE 5: Security Coverage Evaluation
  - Check: Input validation on all user-facing endpoints
  - Check: No hardcoded secrets, tokens, or credentials in code
  - Check: Proper authentication/authorization on protected routes
  - Check: SQL injection and XSS prevention measures
  - Check: Secure handling of sensitive data (encryption, hashing)
  - Report: List security violations with severity
```

### Operation 2: Update Existing Report

**When:** Need to re-evaluate specific features
**Input:** feature_ids to re-evaluate

```
1. LOAD latest report from x-ipe-docs/quality-evaluation/project-quality-evaluation.md
2. FOR EACH feature_id:
   - RE-EVALUATE all 4 perspectives
   - UPDATE feature entry in report
3. RE-CALCULATE aggregates (overall_score, health_status)
4. UPDATE priority_gaps and recommendations
5. SAVE using versioning workflow (see "Versioning Workflow" section above)
```

### Operation 3: Query Quality Status

**When:** Need to check quality for specific features
**Input:** feature_ids or query criteria

```
1. LOAD latest report from x-ipe-docs/quality-evaluation/project-quality-evaluation.md
2. FILTER features by criteria
3. RETURN filtered evaluation data
```

### Operation 4: Compare Evaluations

**When:** Need to track quality changes over time
**Input:** Two version numbers (e.g., "v3 vs v4") or "latest vs previous"

```
1. LOAD both evaluation reports:
   - Latest: project-quality-evaluation.md
   - Previous: project-quality-evaluation-v{N}.md
2. FOR EACH feature in both:
   - COMPARE status changes
   - CALCULATE score deltas
   - IDENTIFY new/resolved gaps
3. GENERATE comparison summary:
   - Improved features
   - Degraded features
   - New gaps introduced
   - Gaps resolved
4. RETURN comparison data
```

---

## Evaluation Principles

See [references/evaluation-principles.md](references/evaluation-principles.md) for complete evaluation principles, thresholds, and score calculation formulas.

**Key Thresholds:**
- Test Line Coverage: ≥ 80%
- File Size: ≤ 800 lines
- Function Size: ≤ 50 lines
- Tracing Coverage: ≥ 90%

---

## Evaluation Procedures

See [references/evaluation-procedures.md](references/evaluation-procedures.md) for detailed step-by-step procedures for each evaluation perspective:
- Requirements Alignment
- Specification Alignment
- Test Coverage
- Code Alignment
- Tracing Coverage
- Security Evaluation
- Refactoring Suggestions

---

## Report Template

The skill uses template at `templates/quality-report.md` for consistent report generation.

Template structure:
1. Header with metadata
2. Executive Summary
3. Feature-by-Feature Evaluation
4. Priority Gaps
5. Recommendations
6. Appendix (detailed data)

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | All features in scope evaluated | Yes |
| 2 | All 4 perspectives evaluated per feature | Yes |
| 3 | Gaps identified and prioritized | Yes |
| 4 | Overall score calculated | Yes |
| 5 | Report generated in correct location | Yes |
| 6 | Latest report link updated | Yes |
| 7 | Report self-review completed (check for problems or missing content) | Yes |

---

## Patterns

### Pattern: First-Time Evaluation

**When:** No previous quality reports exist
**Then:**
```
1. Generate full project evaluation
2. Set baseline metrics
3. Create recommendations for initial improvements
4. Flag features needing immediate attention
```

### Pattern: Post-Refactoring Evaluation

**When:** After code-refactoring-stage tasks complete
**Then:**
```
1. Load code_quality_evaluated from refactoring task
2. Use as input for targeted re-evaluation
3. Compare with pre-refactoring state
4. Generate delta report showing improvements
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip features without specs | Miss coverage gaps | Evaluate, mark as not_found |
| Assume passing tests = quality | Tests may not cover all | Always check all 4 perspectives |
| Only evaluate after problems | Reactive, not proactive | Regular scheduled evaluations |
| Ignore low-severity gaps | They accumulate | Track all, prioritize by severity |

---

## Integration with Code Refactoring Stage

This skill integrates with the code-refactoring-stage workflow:

1. **Before Refactoring Analysis**: Generate baseline quality report
2. **After Improve Quality**: Generate comparison showing documentation alignment
3. **After Code Refactor V2**: Generate final quality report showing improvements

```
Quality Report (baseline)
    ↓
task-type-refactoring-analysis
    ↓
task-type-improve-code-quality-before-refactoring
    ↓
Quality Report (mid-point)
    ↓
task-type-code-refactor-v2
    ↓
Quality Report (final) + Comparison
```
