---
name: x-ipe-tool-rev-eng-test-analysis
version: "1.0"
description: >
  Focused tool skill for Section 8 (Source Code Tests) of application reverse engineering.
  Scans, catalogs, copies, and EXECUTES existing test files to validate reverse-engineered
  understanding. Extracts knowledge from test assertions and generates verifiable claims
  for Phase 3. Use when extracting test knowledge from source code. Triggers on requests
  like "analyze source code tests", "extract test knowledge", "run existing tests",
  "test coverage analysis".
section_id: 8
phase: "2-Tests"
categories:
  - knowledge-extraction
  - reverse-engineering
  - test-analysis
---

# Source Code Tests — Reverse Engineering Tool

## Purpose

AI Agents follow this skill to extract test knowledge from a target repository by:
1. Scanning and cataloging all existing test files with metadata
2. Detecting the test framework, assertion style, and fixture patterns
3. Copying test files to output and executing them to record pass/fail results
4. Measuring line coverage and identifying gaps per module
5. Mapping test assertions to module behaviors as verifiable claims for Phase 3

## Important Notes

**BLOCKING:** Source code is NEVER modified. Source code is ground truth in reverse engineering — the original tests are correct. If tests fail, iterate on execution environment (dependencies, configuration, test runner settings) until all tests pass.

**BLOCKING:** Tests must be COPIED from the source repo to the output `tests/` subfolder before execution. Never run tests in-place in the source repo working directory.

**CRITICAL:** The test framework used for execution MUST match the project's detected framework from Phase 1 Section 7. Do not impose a different framework.

**CRITICAL:** This is Phase 2 — it depends on Phase 1 output (Section 5 file structure, Section 7 tech stack). If Phase 1 output is unavailable, fall back to direct repo scanning.

## About

This tool skill handles the ONLY section in Phase 2 of application reverse engineering. While Phase 1 scans structure and tech stack, Phase 2 validates understanding by actually running the project's tests. The results feed directly into Phase 3's deep analysis.

**Key Concepts:**
- **Copy-First Strategy** — Test files are copied to the output directory, never modified in source
- **Ground Truth Rule** — Source code is correct; iterate on execution environment until tests pass
- **Framework Matching** — Execution uses the project's own test framework
- **Knowledge Extraction** — Each test assertion maps to a module behavior claim
- **Test-Derived Claims** — Verifiable statements generated from test results for Phase 3 cross-validation

## When to Use

```yaml
triggers:
  - "extract test knowledge"
  - "analyze source code tests"
  - "run existing tests"
  - "test coverage analysis"
  - "reverse engineering phase 2"
not_for:
  - "x-ipe-tool-rev-eng-technology-stack: Detecting test frameworks (Section 7)"
  - "x-ipe-tool-rev-eng-code-structure-analysis: File structure scanning (Section 5)"
  - "x-ipe-task-based-feature-acceptance-test: Writing NEW feature tests"
```

## Input Parameters

```yaml
input:
  operation: "extract | collect_tests | execute_tests | analyze_coverage | extract_knowledge | validate | package"
  repo_path: "string — absolute path to target source repository"
  output_path: "string — path for section-08-source-code-tests/ output"
  phase1_output: "string | null — path to Phase 1 scan results"
  test_framework: "string | null — override: pytest | jest | vitest | junit | testify | go-test"
  coverage_threshold: "number — default 80 — minimum line coverage target"
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies which operation to perform" />
  <field name="repo_path" source="Caller provides path to target repository">
    <steps>1. Verify directory exists with source code  2. Check for .git directory</steps>
  </field>
  <field name="output_path" source="Caller provides or defaults to .intake/{project}/section-08-source-code-tests/">
    <steps>1. Create output directory if not exists  2. Create tests/, screenshots/ subdirectories</steps>
  </field>
  <field name="phase1_output">
    <steps>1. If provided, verify Section 5 and Section 7 outputs exist  2. If missing, log warning and proceed with direct repo scanning</steps>
  </field>
  <field name="test_framework">
    <steps>1. If provided, use as override  2. If null, detect from Phase 1 Section 7  3. If Phase 1 unavailable, detect from repo configs and imports</steps>
  </field>
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Repository accessible</name><verification>repo_path exists and contains source files</verification></checkpoint>
  <checkpoint required="true"><name>Output directory writable</name><verification>output_path can be created or exists</verification></checkpoint>
  <checkpoint required="true"><name>Phase 1 available or fallback possible</name><verification>phase1_output exists OR repo can be scanned directly</verification></checkpoint>
  <checkpoint required="false"><name>Test framework pre-detected</name><verification>test_framework provided or detectable from configs</verification></checkpoint>
</definition_of_ready>
```

## Operations

### Operation: extract

**When:** First operation — scan and catalog all test files in the repository.

```xml
<operation name="extract">
  <action>
    1. Scan repo_path for test files using language-aware glob patterns:
       - Python: *_test.py, test_*.py, tests/**/*.py, conftest.py
       - JavaScript/TypeScript: *.test.js, *.spec.ts, *.test.tsx, __tests__/**
       - Java: *Test.java, *Tests.java, src/test/**
       - Go: *_test.go
    2. For each test file found, extract metadata:
       - File path (relative to repo root)
       - File size, line count
       - Test function/method count (grep for test_ / it( / test( / func Test / @Test)
       - Assertion count (grep for assert / expect / should)
       - Fixture/setup usage (grep for fixture / beforeEach / setUp / TestMain)
    3. Detect test framework from (in priority order):
       a. Phase 1 Section 7 output (if available)
       b. Config files: pytest.ini, setup.cfg [tool.pytest], jest.config.*, vitest.config.*, pom.xml, go.mod
       c. Import statements in test files
    4. Detect assertion style and fixture patterns
    5. Write 01-test-collection.md with full catalog table
    6. Write 02-test-framework.md with detection results
  </action>
  <constraints>
    - BLOCKING: Do NOT modify any files in repo_path
    - Use Phase 1 output when available to avoid redundant scanning
  </constraints>
  <output>
    catalog: array of {path, test_count, assertion_count, fixture_usage}
    framework: {name, version, config_file, assertion_style}
  </output>
</operation>
```

### Operation: collect_tests

**When:** After `extract` — copy test files to output directory.

```xml
<operation name="collect_tests">
  <action>
    1. Read catalog from extract output (01-test-collection.md)
    2. Create {output_path}/section-08-source-code-tests/tests/ directory
    3. For each cataloged test file:
       a. Copy file preserving directory structure relative to repo root
       b. Record original source path for each copied file
       c. Copy associated fixture/conftest files
       d. Copy test configuration files (pytest.ini, jest.config.*, etc.)
    4. Copy any test data files referenced by test imports
    5. Verify all copied files are readable
    6. Generate test-manifest.md with table:
       | Original Path | Copied Path | Test Count | Framework |
       Each entry references the original location for traceability
  </action>
  <constraints>
    - BLOCKING: Copy only — NEVER modify source repository
    - Preserve relative paths so imports resolve correctly
    - Include fixture and config files needed for execution
    - Every copied file must have its original source path recorded in manifest
  </constraints>
  <output>
    copied_files: array of {original_path, dest_path, size}
    manifest_path: string — path to test-manifest.md
  </output>
</operation>
```

### Operation: execute_tests

**When:** After `collect_tests` — run tests and record results.

```xml
<operation name="execute_tests">
  <action>
    1. Determine test runner command based on detected framework:
       - pytest: `cd {repo_path} && python -m pytest --tb=short -v`
       - jest: `cd {repo_path} && npx jest --verbose`
       - vitest: `cd {repo_path} && npx vitest run --reporter=verbose`
       - go-test: `cd {repo_path} && go test ./... -v`
       - junit: `cd {repo_path} && mvn test` or `gradle test`
    2. Execute tests from the REPO directory (tests need project context)
    3. Capture stdout/stderr and exit code
    4. Parse output to extract per-test results:
       - Test name, file, status (pass/fail/skip/error)
       - Duration per test
       - Failure message and stack trace (if failed)
    5. IF any tests FAILED:
       a. Analyze failure output to categorize root cause:
          - Missing dependency → install it
          - Config issue → adjust test runner config flags
          - Environment variable missing → set it
          - Timeout → increase timeout limit
          - Flaky test → re-run with retry flag
       b. Apply fix to execution environment (NEVER modify source code)
       c. Re-run only the failed tests
       d. Repeat steps 5a-5c up to 3 iterations
       e. If still failing after 3 iterations → document as unfixable with detailed analysis
    6. GATE: Proceed only when all tests pass OR remaining failures are documented with unfixable rationale
    7. Write 03-test-execution.md with per-test result table including:
       - Original source path reference for each test
       - Pass/fail status
       - Any refinement iterations performed
    8. Write test-results.md with machine-readable summary:
       - Total tests, passed, failed, skipped, errored
       - Refinement iterations count
       - Execution time
       - Per-file breakdown
  </action>
  <constraints>
    - BLOCKING: Source code NEVER modified — only execution environment can be adjusted
    - BLOCKING: GATE — all tests must pass before proceeding to extract_knowledge
    - Iterate up to 3 times on execution environment for failing tests
    - Execute in repo_path where project dependencies are installed
    - Capture both stdout and stderr for diagnostic value
    - Set timeout per test suite (default: 300 seconds)
    - Document all refinement iterations in execution log
  </constraints>
  <output>
    summary: {total, passed, failed, skipped, error_count, duration, refinement_iterations}
    per_test: array of {name, file, original_path, status, duration, failure_message}
  </output>
</operation>
```

### Operation: analyze_coverage

**When:** After `execute_tests` — measure line coverage.

```xml
<operation name="analyze_coverage">
  <action>
    1. Determine coverage tool based on framework:
       - Python: `python -m pytest --cov={src} --cov-report=term-missing --cov-report=html`
       - JavaScript: `npx jest --coverage` or `npx vitest run --coverage`
       - Go: `go test ./... -coverprofile=coverage.out && go tool cover -func=coverage.out`
       - Java: JaCoCo via maven/gradle plugin
    2. Execute coverage command from repo_path
    3. Parse coverage output to extract per-module metrics:
       - Module/file path
       - Statements, branches, functions, lines covered
       - Line coverage percentage
       - Uncovered line ranges
    4. Identify modules below coverage_threshold (default 80%)
    5. If HTML coverage report generated, copy to screenshots/
    6. Write 04-coverage-analysis.md with:
       - Summary table (module, lines, coverage %)
       - Gap analysis (modules below threshold with uncovered line ranges)
       - Overall project coverage
  </action>
  <constraints>
    - Coverage tool must match the project ecosystem
    - If coverage tool unavailable or fails, document as "coverage not measurable" with reason
    - Do NOT install coverage tools not already in project dependencies
  </constraints>
  <output>
    overall_coverage: number (percentage)
    per_module: array of {module, lines_total, lines_covered, percentage, gaps}
    below_threshold: array of module names
  </output>
</operation>
```

### Operation: extract_knowledge

**When:** After `execute_tests` passes gate (all tests pass or documented) and optionally `analyze_coverage` — derive behavioral knowledge.

```xml
<operation name="extract_knowledge">
  <action>
    1. For each test file, analyze assertions to extract behavioral claims:
       - What module/function is being tested
       - What behavior the assertion validates
       - What inputs produce what outputs (from arrange/act/assert)
       - Integration boundaries revealed (mocks show service boundaries)
    2. Build knowledge mapping table:
       | Test File | Test Name | Module Under Test | Behavior Validated | Confidence |
    3. Identify patterns across tests:
       - Most-tested modules (highest importance signal)
       - Untested modules (risk signal)
       - Mock boundaries (reveal architecture seams)
       - Fixture data (reveal valid data shapes)
    4. Generate verifiable claims from test assertions:
       - "Module X returns Y when given input Z" (from assertion)
       - "Service A depends on Service B" (from mock setup)
       - "Data must match schema S" (from fixture/factory)
    5. Write 05-knowledge-extraction.md with mapping table
    6. Write 06-test-derived-claims.md with numbered claims for Phase 3
  </action>
  <constraints>
    - Claims must trace back to specific test assertions (cite test_file:line)
    - Confidence levels: HIGH (direct assertion), MEDIUM (inferred from mock), LOW (inferred from fixture)
    - Failed tests generate claims about ACTUAL behavior (not expected behavior)
  </constraints>
  <output>
    knowledge_map: array of {test, module, behavior, confidence}
    claims: array of {id, claim, source_test, confidence}
  </output>
</operation>
```

### Operation: validate

**When:** After extraction operations — validate content against acceptance criteria.

```xml
<operation name="validate">
  <action>
    1. Load acceptance criteria from templates/acceptance-criteria.md
    2. Check each [REQ] criterion:
       a. All existing test files cataloged with metadata → verify 01-test-collection.md
       b. Test framework correctly detected → verify 02-test-framework.md
       c. Tests copied to output tests/ subfolder → verify tests/ directory
       d. Tests executed with pass/fail per test → verify 03-test-execution.md
       e. Source code never modified → verify no git diff in repo_path
       f. Test knowledge extraction documented → verify 05-knowledge-extraction.md
    3. Check each [OPT] criterion and record status
    4. Calculate quality score using Tests Section weights:
       Completeness=0.10, Structure=0.05, Clarity=0.10,
       Accuracy=0.15, Freshness=0.10, Coverage=0.50
    5. Return validation result with pass/fail per criterion
  </action>
  <constraints>
    - All [REQ] criteria must pass for overall success
    - Quality score must meet minimum threshold (0.60)
  </constraints>
  <output>
    valid: true | false
    criteria_results: array of {id, status, message}
    quality_score: number (0.0–1.0)
  </output>
</operation>
```

### Operation: package

**When:** After `validate` passes — assemble final output subfolder.

```xml
<operation name="package">
  <action>
    1. Verify all subsection files exist in output_path:
       - 01-test-collection.md
       - 02-test-framework.md
       - 03-test-execution.md
       - 04-coverage-analysis.md
       - 05-knowledge-extraction.md
       - 06-test-derived-claims.md
       - test-results.md
       - test-manifest.md
       - tests/ directory
    2. Generate index.md with:
       - Section title and overview
       - Test framework and version
       - Execution summary (total/passed/failed/skipped)
       - Coverage summary (overall percentage)
       - Links to all subsection files
       - Links to tests/ and screenshots/
    3. Verify directory structure matches expected layout:
       section-08-source-code-tests/
       ├── index.md
       ├── 01-test-collection.md
       ├── 02-test-framework.md
       ├── 03-test-execution.md
       ├── 04-coverage-analysis.md
       ├── 05-knowledge-extraction.md
       ├── 06-test-derived-claims.md
       ├── test-results.md
       ├── test-manifest.md
       ├── screenshots/
       └── tests/
    4. Return package path
  </action>
  <constraints>
    - All subsection files must exist before packaging
    - index.md must link every subsection file
  </constraints>
  <output>
    package_path: string
    file_count: number
    total_size: string
  </output>
</operation>
```

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "extract | collect_tests | execute_tests | analyze_coverage | extract_knowledge | validate | package"
  result:
    catalog: [{path, test_count, assertion_count, fixture_usage}]       # extract
    framework: {name, version, config_file, assertion_style}            # extract
    copied_files: [{original_path, dest_path}]                          # collect_tests
    summary: {total, passed, failed, skipped, duration, refinement_iterations}  # execute_tests
    per_test: [{name, file, original_path, status, duration, failure_message}]  # execute_tests
    overall_coverage: number                                            # analyze_coverage
    per_module: [{module, percentage, gaps}]                            # analyze_coverage
    knowledge_map: [{test, module, behavior, confidence}]               # extract_knowledge
    claims: [{id, claim, source_test, confidence}]                      # extract_knowledge
    valid: boolean                                                      # validate
    quality_score: number                                               # validate
    package_path: string                                                # package
  errors: []
```

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Test files cataloged</name>
    <verification>01-test-collection.md exists with test file metadata table</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Framework detected</name>
    <verification>02-test-framework.md identifies framework, version, assertion style</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tests copied</name>
    <verification>tests/ subfolder contains all cataloged test files</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tests executed and pass gate</name>
    <verification>03-test-execution.md contains per-test pass/fail; all tests pass OR remaining failures documented with unfixable rationale after max 3 refinement iterations</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Source unchanged</name>
    <verification>No modifications to repo_path (git diff is clean)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Knowledge extracted</name>
    <verification>05-knowledge-extraction.md maps test → module → behavior</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Claims generated</name>
    <verification>06-test-derived-claims.md contains numbered verifiable claims</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Index complete</name>
    <verification>index.md links all subsection files with summary</verification>
  </checkpoint>
  <checkpoint required="false">
    <name>Coverage measured</name>
    <verification>04-coverage-analysis.md contains per-module coverage or gap rationale</verification>
  </checkpoint>
  <checkpoint required="false">
    <name>Quality score met</name>
    <verification>Validation quality score ≥ 0.60</verification>
  </checkpoint>
</definition_of_done>
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `NO_TEST_FILES` | Repository contains no test files | Record as "no tests found" in catalog; skip execute/coverage; document in index.md |
| `FRAMEWORK_UNDETECTED` | Cannot determine test framework | Check imports in test files; if still unknown, ask caller for test_framework override |
| `EXECUTION_TIMEOUT` | Test suite exceeds 300s timeout | Record partial results; mark timed-out tests as "timeout" status |
| `EXECUTION_FAILURE` | Test runner crashes (not test failures) | Log error; attempt with `--no-header` or minimal flags; record as "runner error" |
| `COVERAGE_UNAVAILABLE` | Coverage tool not installed or fails | Document as "coverage not measurable" with reason; skip 04-coverage-analysis.md |
| `TESTS_STILL_FAILING` | Tests fail after 3 refinement iterations | Document failures with analysis; proceed with warnings; flag in extraction report |
| `PHASE1_MISSING` | Phase 1 output not found | Fall back to direct repo scanning with warning |
| `PERMISSION_DENIED` | Cannot read repo files or write output | Fail with clear error message citing the path |

## Templates

| File | Purpose |
|------|---------|
| `templates/acceptance-criteria.md` | Section 8 validation criteria with [REQ] and [OPT] markers |
| `templates/extraction-prompts.md` | Extraction prompts for each subsection |

## Examples

See [references/examples.md](references/examples.md) for usage examples showing Python/pytest and JavaScript/Jest flows.
