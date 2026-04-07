# Extraction Prompts — Section 8: Source Code Tests

> Prompts used by each operation to extract test knowledge from the target repository.
> These prompts guide the AI agent through systematic test analysis.

---

## 8.1 Test Collection Prompts

```
SCAN the repository at {repo_path} for all test files using these patterns:
- Python: *_test.py, test_*.py, conftest.py, tests/**/*.py
- JavaScript/TypeScript: *.test.js, *.test.ts, *.spec.js, *.spec.ts, *.test.tsx, __tests__/**/*
- Java: *Test.java, *Tests.java, *IT.java, src/test/**/*.java
- Go: *_test.go

For EACH test file found, extract:
| Field            | How to extract                                       |
|------------------|------------------------------------------------------|
| File path        | Relative to repo root                                |
| Line count       | wc -l                                                |
| Test count       | Count: def test_ / it( / test( / func Test / @Test   |
| Assertion count  | Count: assert / expect( / .should / assertEqual      |
| Fixture usage    | Presence of: @fixture / beforeEach / setUp / TestMain |
| Last modified    | git log -1 --format=%ci {file}                       |

OUTPUT: Markdown table sorted by module, then file path.
```

## 8.2 Test Framework Detection Prompts

```
DETECT the test framework for {repo_path} using this priority:

1. CHECK Phase 1 Section 7 output at {phase1_output}/section-07-technology-stack/
   → Look for "Testing frameworks" in tech stack inventory

2. CHECK configuration files (stop at first match):
   - pytest.ini, setup.cfg [tool.pytest.ini_options], pyproject.toml [tool.pytest]
   - jest.config.js, jest.config.ts, package.json "jest" key
   - vitest.config.ts, vitest.config.js
   - pom.xml <surefire-plugin>, build.gradle testImplementation
   - go.mod (Go projects use built-in testing)

3. CHECK import statements in test files:
   - import pytest / from pytest → pytest
   - require('jest') / import { describe } from '@jest/globals' → jest
   - import { describe } from 'vitest' → vitest
   - import org.junit → JUnit
   - import "testing" → go-test

EXTRACT:
- Framework name and version
- Assertion library (if separate: chai, assertj, testify)
- Fixture/factory pattern (pytest fixtures, Jest beforeEach, JUnit @BeforeEach)
- Test runner command
- Configuration file path

OUTPUT: Structured detection report with evidence chain.
```

## 8.3 Test Execution Prompts

```
EXECUTE all tests in {repo_path} using the detected framework.

COMMAND BY FRAMEWORK:
- pytest:   cd {repo_path} && python -m pytest --tb=short -v 2>&1
- jest:     cd {repo_path} && npx jest --verbose --no-coverage 2>&1
- vitest:   cd {repo_path} && npx vitest run --reporter=verbose 2>&1
- go-test:  cd {repo_path} && go test ./... -v -count=1 2>&1
- junit:    cd {repo_path} && mvn test -pl . 2>&1  OR  gradle test 2>&1

CAPTURE:
- Full stdout and stderr
- Exit code
- Per-test results: name, file, status (PASS/FAIL/SKIP/ERROR), duration
- For failures: assertion message and relevant stack trace (first 10 lines)

GROUND TRUTH RULES:
⚠️ If tests FAIL → Record the failure as INFORMATION about actual behavior
⚠️ Do NOT modify source code to make tests pass
⚠️ Do NOT modify test code to make tests pass
⚠️ Failing tests are valuable — they reveal actual vs. expected behavior

OUTPUT: 
- Per-test result table with status, duration, failure details
- Summary: total / passed / failed / skipped / errors / duration
```

## 8.4 Coverage Analysis Prompts

```
MEASURE line coverage for {repo_path} using the appropriate tool:

COMMAND BY FRAMEWORK:
- pytest:   cd {repo_path} && python -m pytest --cov=. --cov-report=term-missing --cov-report=html:htmlcov 2>&1
- jest:     cd {repo_path} && npx jest --coverage 2>&1
- vitest:   cd {repo_path} && npx vitest run --coverage 2>&1
- go-test:  cd {repo_path} && go test ./... -coverprofile=coverage.out && go tool cover -func=coverage.out 2>&1
- junit:    Use JaCoCo plugin output

PARSE coverage output to extract per-module:
| Module/File | Statements | Branches | Lines | Line Coverage % | Uncovered Lines |

IDENTIFY:
- Modules BELOW {coverage_threshold}% (default: 80%)
- Completely untested modules (0% coverage)
- Highest-coverage modules (most validated)

IF coverage tool is unavailable:
- Document: "Coverage not measurable — {reason}"
- List known test files and their apparent target modules as proxy

OUTPUT:
- Per-module coverage table
- Gap analysis with uncovered line ranges
- Overall project coverage percentage
```

## 8.5 Knowledge Extraction Prompts

```
ANALYZE test assertions from execution results to extract behavioral knowledge.

For EACH test:
1. IDENTIFY the module under test (from import/require statements)
2. IDENTIFY the behavior being validated (from assertion)
3. CLASSIFY the test type:
   - Unit test: tests single function/method in isolation
   - Integration test: tests interaction between modules
   - End-to-end test: tests complete workflow
4. IDENTIFY mock/stub boundaries → these reveal service seams
5. IDENTIFY fixture data → these reveal valid data shapes

BUILD knowledge mapping:
| Test File:Line | Test Name | Module Under Test | Behavior | Test Type | Confidence |

IDENTIFY PATTERNS:
- Most-tested modules → highest importance
- Untested modules → highest risk
- Mock boundaries → architecture seams
- Fixture shapes → data contracts
- Failed tests → actual vs. expected behavior divergence

OUTPUT: Knowledge mapping table + pattern summary
```

## 8.6 Test-Derived Claims Prompts

```
GENERATE verifiable claims from test execution results for Phase 3.

For each passing test assertion:
  CLAIM-{NNN}: "Module {X} returns {Y} when given {Z}"
  Source: {test_file}:{line}
  Confidence: HIGH (direct assertion)

For each mock setup:
  CLAIM-{NNN}: "Module {X} depends on {Y} for {operation}"
  Source: {test_file}:{line}
  Confidence: MEDIUM (inferred from mock)

For each fixture/factory:
  CLAIM-{NNN}: "Data shape for {entity} includes fields {F1, F2, ...}"
  Source: {test_file}:{line}
  Confidence: MEDIUM (inferred from fixture)

For each FAILING test:
  CLAIM-{NNN}: "Module {X} ACTUALLY {behavior} (expected: {expected})"
  Source: {test_file}:{line}
  Confidence: HIGH (observed actual behavior)

RULES:
- Each claim must cite exact source file and line
- Group claims by module for Phase 3 cross-validation
- Mark failing-test claims distinctly as "actual behavior"

OUTPUT: Numbered claim list with source citations and confidence levels
```

---

## Source Priority

For all prompts, prioritize evidence sources in this order:
1. **Existing test files** — Highest priority, ground truth
2. **Test configuration files** — Framework and runner settings
3. **README testing section** — Developer-documented test instructions
4. **CI/CD test steps** — Automated test commands from pipelines
