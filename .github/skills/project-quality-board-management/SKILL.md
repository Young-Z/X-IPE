---
name: project-quality-board-management
description: Generate and manage project quality evaluation reports from feature perspective. Evaluates requirements, features, test coverage, and code alignment status with gap analysis. Generates consistent markdown reports to x-ipe-docs/planning folder. Triggers on requests like "evaluate project quality", "generate quality report", "assess code alignment".
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

Quality evaluation report is stored in:
```
x-ipe-docs/planning/project-quality-evaluation.md
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
  features:
    - feature_id: FEATURE-XXX
      feature_name: "<name>"
      status: aligned | needs_attention | critical | planned | not_evaluated
      
      requirements_alignment:
        status: aligned | needs_update | not_found | planned
        requirement_docs: [<paths>]
        gaps:
          - type: undocumented | unimplemented | deviated
            description: "<gap description>"
            severity: high | medium | low
      
      specification_alignment:
        status: aligned | needs_update | not_found | planned
        spec_doc: "<path>"
        gaps:
          - type: missing | outdated | incorrect
            description: "<gap description>"
            severity: high | medium | low
      
      test_coverage:
        status: sufficient | insufficient | no_tests
        line_coverage: <XX%>
        branch_coverage: <XX%>
        critical_untested:
          - area: "<untested area>"
            risk: high | medium | low
      
      code_alignment:
        status: aligned | drifted | major_drift
        implementation_files: [<paths>]
        gaps:
          - type: structure | behavior | interface
            description: "<gap description>"
            severity: high | medium | low
  
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
   e. Files Approaching Threshold
   f. Priority Gaps Summary
   g. Recommendations
   h. Appendix (detailed metrics)

6. SAVE report:
   - Save to x-ipe-docs/planning/project-quality-evaluation.md
   - Update version and evaluated date in header

7. RETURN evaluation summary
```

### Report Structure Rules

```
RULE 1: Evaluation Principles section
  - MUST come BEFORE Feature-by-Feature Evaluation
  - MUST only explain what principles are and thresholds
  - MUST NOT contain any evaluation results or status

RULE 2: Violation Details section
  - MUST be organized by feature
  - EACH feature section MUST have 4 subsections:
    - Requirements Violations
    - Specification Violations
    - Test Coverage Violations
    - Code Alignment Violations
  - ONLY show features that have violations
  - Show "No violations" if a category is clean

RULE 3: Separation of concerns
  - Principles = WHAT we evaluate and HOW (thresholds)
  - Violations = RESULTS of evaluation per feature
```

### Operation 2: Update Existing Report

**When:** Need to re-evaluate specific features
**Input:** feature_ids to re-evaluate

```
1. LOAD latest report from quality-evaluation-latest.md
2. FOR EACH feature_id:
   - RE-EVALUATE all 4 perspectives
   - UPDATE feature entry in report
3. RE-CALCULATE aggregates (overall_score, health_status)
4. UPDATE priority_gaps and recommendations
5. SAVE as new timestamped report
6. UPDATE quality-evaluation-latest.md
```

### Operation 3: Query Quality Status

**When:** Need to check quality for specific features
**Input:** feature_ids or query criteria

```
1. LOAD latest report
2. FILTER features by criteria
3. RETURN filtered evaluation data
```

### Operation 4: Compare Evaluations

**When:** Need to track quality changes over time
**Input:** Two evaluation_ids or "latest vs previous"

```
1. LOAD both evaluation reports
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

### Requirements Evaluation Principles

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| Completeness | 100% | Every implemented feature must have documented requirements |
| Traceability | Required | Requirements should trace to features and code |
| Clarity | No ambiguity | Requirements should be specific and testable |
| Currency | < 30 days | Requirements updated within 30 days of code changes |

### Specification Evaluation Principles

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| API Documentation | Required | All public APIs must be documented |
| Behavior Specification | Required | Expected behaviors clearly defined |
| Edge Cases | Documented | Error handling and edge cases specified |
| Version Alignment | Match | Spec version should match implementation version |

### Test Coverage Evaluation Principles

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| Line Coverage | ≥ 80% | Minimum line coverage for production code |
| Branch Coverage | ≥ 70% | Minimum branch/decision coverage |
| Critical Path Coverage | 100% | Core business logic must be fully tested |
| Error Handler Coverage | ≥ 90% | Exception and error paths tested |
| Test Isolation | Required | Tests should not depend on external services |
| Mock External APIs | Required | External API calls must be mocked in tests |

### Code Alignment Evaluation Principles

| Principle | Threshold | Description |
|-----------|-----------|-------------|
| **File Size** | ≤ 800 lines | Single file should not exceed 800 lines |
| **Function Size** | ≤ 50 lines | Single function should not exceed 50 lines |
| **Class Size** | ≤ 500 lines | Single class should not exceed 500 lines |
| **Cyclomatic Complexity** | ≤ 10 | Function complexity should be manageable |
| **SRP (Single Responsibility)** | 1 reason to change | Each module/class has one responsibility |
| **OCP (Open/Closed)** | Extensible | Open for extension, closed for modification |
| **LSP (Liskov Substitution)** | Substitutable | Subtypes must be substitutable for base types |
| **ISP (Interface Segregation)** | Focused | Clients shouldn't depend on unused interfaces |
| **DIP (Dependency Inversion)** | Abstracted | Depend on abstractions, not concretions |
| **DRY (Don't Repeat Yourself)** | No duplication | Avoid code duplication across modules |
| **KISS (Keep It Simple)** | Simple solutions | Prefer simple over complex implementations |
| **YAGNI** | No unused code | Don't implement features until needed |
| **Modular Design** | Cohesive modules | Code organized into focused, reusable modules |
| **Naming Conventions** | Consistent | Follow language-specific naming conventions |
| **Import Organization** | Grouped | Imports organized by type (stdlib, external, internal) |

### KISS Principle Assessment

| Check | Threshold | Description |
|-------|-----------|-------------|
| Avoid Over-Engineering | No unnecessary abstractions | Don't add layers without clear benefit |
| Straightforward Logic | Linear flow preferred | Avoid convoluted control flow |
| Minimal Dependencies | Only necessary imports | Don't import unused libraries |
| Clear Intent | Self-documenting code | Code should express intent without excessive comments |
| Simple Data Structures | Use built-in types | Avoid custom types when built-ins suffice |

### Modular Design Assessment

| Check | Threshold | Description |
|-------|-----------|-------------|
| **Module Cohesion** | High cohesion | Related functions grouped in same module |
| **Module Coupling** | Loose coupling | Modules minimize dependencies on each other |
| **Single Entry Point** | One public API | Each module has clear public interface |
| **Folder Structure** | Logical grouping | Files organized by feature or layer |
| **Reusability** | Portable modules | Modules can be reused in different contexts |
| **Testability** | Independently testable | Each module can be tested in isolation |

**Modular Design Patterns:**

| Pattern | When to Apply | Example |
|---------|---------------|---------|
| Feature Modules | Large files > 800 lines | Split `app.py` → `routes/api.py`, `routes/views.py` |
| Service Layer | Business logic mixed with routes | Extract to `services/` folder |
| Component Split | UI file > 500 lines | Split into sub-components |
| Utility Extraction | Repeated helper functions | Create `utils/` or `lib/` folder |

### Code Smell Detection

| Smell | Detection Rule | Severity |
|-------|----------------|----------|
| God Class | Class > 500 lines OR > 20 methods | High |
| Long Method | Function > 50 lines | Medium |
| Large File | File > 800 lines | Medium |
| Deep Nesting | > 4 levels of indentation | Medium |
| Too Many Parameters | Function > 5 parameters | Low |
| Magic Numbers | Hardcoded values without constants | Low |
| Dead Code | Unused functions/variables | Low |
| Duplicate Code | Similar code blocks > 10 lines | Medium |

---

## Evaluation Procedures

### Procedure: Evaluate Requirements Alignment

```
1. LOCATE requirement docs:
   - x-ipe-docs/requirements/requirement-summary.md
   - x-ipe-docs/requirements/requirement-details.md
   - Any docs referencing feature

2. FOR EACH requirement related to feature:
   a. CHECK if requirement is documented
   b. CHECK if requirement is implemented in code
   c. IDENTIFY deviations between doc and implementation

3. CLASSIFY gaps:
   - undocumented: Implemented but not in requirements
   - unimplemented: In requirements but not implemented
   - deviated: Implementation differs from requirement

4. ASSIGN severity:
   - high: Core functionality affected
   - medium: Secondary functionality affected
   - low: Minor/edge cases
```

### Procedure: Evaluate Specification Alignment

```
1. LOCATE specification:
   - x-ipe-docs/requirements/FEATURE-XXX/specification.md

2. IF specification exists:
   a. EXTRACT expected behaviors
   b. COMPARE with actual implementation
   c. IDENTIFY gaps (missing | outdated | incorrect)
   
3. IF specification missing (empty feature folder):
   a. CHECK if any related implementation exists in codebase
   b. IF no implementation found:
      - status: planned
      - NOT a gap - just indicates future work needed
      - Do NOT count as critical or high priority gap
   c. IF implementation exists without specification:
      - status: not_found
      - Add gap: "Implementation exists but specification missing"
      - severity: medium (documentation debt)
```

### Procedure: Evaluate Test Coverage

```
1. IDENTIFY test files for feature:
   - tests/**/test_*{feature_name}*
   - tests/**/*{feature_name}*_test.*

2. RUN coverage analysis:
   - Python: pytest --cov
   - Node.js: npm test -- --coverage
   - Go: go test -cover

3. EXTRACT metrics:
   - Line coverage %
   - Branch coverage %
   - Untested functions/areas

4. IDENTIFY critical untested areas:
   - Business logic paths
   - Error handlers
   - Edge cases

5. DETERMINE status:
   - sufficient: ≥80% line coverage, no critical gaps
   - insufficient: <80% or has critical gaps
   - no_tests: No test files found
```

### Procedure: Evaluate Code Alignment

```
1. LOCATE technical design:
   - x-ipe-docs/requirements/FEATURE-XXX/technical-design.md

2. IF technical design exists:
   a. EXTRACT expected:
      - File structure
      - Component interfaces
      - Data models
   b. COMPARE with actual implementation
   c. IDENTIFY gaps:
      - structure: File/folder organization differs
      - behavior: Logic differs from design
      - interface: API/interface differs

3. DETERMINE status:
   - aligned: No significant gaps
   - drifted: Minor gaps exist
   - major_drift: Critical gaps exist
```

### Procedure: Generate Refactoring Suggestions

**Integrates with:** `task-type-refactoring-analysis` skill

```
1. ANALYZE gaps from all 4 perspectives:
   - Collect all gaps with severity high/medium
   - Group gaps by feature

2. FOR EACH feature with gaps:
   a. IDENTIFY applicable principles (from task-type-refactoring-analysis):
      - Large files/classes → SRP, SOLID
      - Duplicated code → DRY
      - Complex logic → KISS
      - Unused code → YAGNI
      - Mixed concerns → SoC (Separation of Concerns)
   
   b. FORMULATE goals based on gaps:
      - requirements gaps → Suggest documentation sync or code alignment
      - specification gaps → Suggest spec update or implementation fix
      - test coverage gaps → Suggest test-first approach
      - code alignment gaps → Suggest structural refactoring
   
   c. DEFINE target structure:
      - Describe desired code organization after fixes
      - Note key structural changes needed
   
   d. IDENTIFY constraints:
      - Backward compatibility requirements
      - API stability requirements
      - Dependencies to preserve

3. COMPILE refactoring_suggestion for feature:
   summary: "<derived from gap analysis>"
   goals:
     - goal: "<specific goal from gap>"
       priority: <based on gap severity>
       rationale: "<from gap description>"
   target_structure: "<desired end state>"
   
   principles:
     primary: [<principles with applications>]
     secondary: [<supporting principles>]
     constraints: [<identified constraints>]

4. IF no gaps found for feature:
   - Set has_suggestions: false for that feature
   - Skip suggestion generation
```

---

## Score Calculation

### Feature Score (1-10)

```
feature_score = weighted_average(
  requirements_alignment: weight=0.25,
  specification_alignment: weight=0.25,
  test_coverage: weight=0.25,
  code_alignment: weight=0.25
)

Status to score mapping:
- aligned/sufficient: 10
- planned: N/A (exclude from scoring - future work)
- needs_update/insufficient: 5
- not_found/no_tests/major_drift: 2
- critical: 1

Note: Features with status "planned" (empty folder, no implementation) 
are EXCLUDED from overall score calculation as they represent future 
work, not quality issues.
```

### Overall Score (1-10)

```
overall_score = average(all feature_scores WHERE status != "planned")
```

### Health Status

```
IF overall_score >= 8: healthy
ELSE IF overall_score >= 5: attention_needed
ELSE: critical
```

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
