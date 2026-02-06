# Evaluation Procedures Reference

This document contains detailed evaluation procedures for each perspective.

---

## Procedure: Evaluate Requirements Alignment

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

---

## Procedure: Evaluate Specification Alignment

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

---

## Procedure: Evaluate Test Coverage

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

---

## Procedure: Evaluate Code Alignment

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

---

## Procedure: Evaluate Tracing Coverage

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

## Procedure: Evaluate Security

```
1. SCAN for hardcoded secrets:
   - grep for password=, secret=, token=, api_key=
   - Check for base64-encoded strings that look like keys

2. CHECK input validation:
   - Identify user-facing endpoints
   - Verify input validation exists

3. CHECK authentication/authorization:
   - Protected routes have auth decorators
   - Role-based access control where needed

4. CHECK injection prevention:
   - Parameterized queries (no string concatenation for SQL)
   - XSS prevention (output encoding)

5. COMPILE security_evaluation: {
     status: passed|warning|failed,
     violations: []
   }
```

---

## Procedure: Generate Refactoring Suggestions

**Integrates with:** `task-type-refactoring-analysis` skill

```
1. ANALYZE gaps from all perspectives:
   - Collect all gaps with severity high/medium
   - Group gaps by feature

2. FOR EACH feature with gaps:
   a. IDENTIFY applicable principles:
      - Large files/classes → SRP, SOLID
      - Duplicated code → DRY
      - Complex logic → KISS
      - Unused code → YAGNI
      - Mixed concerns → SoC
   
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
