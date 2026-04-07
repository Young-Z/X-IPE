# Examples — x-ipe-tool-rev-eng-test-analysis

> Usage examples showing the full test analysis flow for different project types.

---

## Example 1: Python/pytest Project

**Scenario:** Reverse engineering a Python CLI application with pytest test suite.

### Step 1: Extract — Catalog test files

```yaml
input:
  operation: extract
  repo_path: /workspace/target-repo
  output_path: /workspace/output
  phase1_output: /workspace/output/section-05-code-structure-analysis
```

**Agent executes:**
```bash
# Scan for test files
find /workspace/target-repo -name "test_*.py" -o -name "*_test.py" -o -name "conftest.py"
```

**Output → `01-test-collection.md`:**
```markdown
# 8.1 Test Collection

## Test File Catalog

| File Path | Lines | Tests | Assertions | Fixtures | Last Modified |
|-----------|-------|-------|------------|----------|---------------|
| tests/test_cli.py | 145 | 12 | 28 | 3 | 2024-03-15 |
| tests/test_parser.py | 89 | 8 | 19 | 1 | 2024-03-10 |
| tests/test_config.py | 56 | 5 | 11 | 2 | 2024-02-28 |
| tests/conftest.py | 34 | 0 | 0 | 4 | 2024-03-15 |

**Summary:** 4 test files, 25 tests, 58 assertions, 10 fixtures
```

**Output → `02-test-framework.md`:**
```markdown
# 8.2 Test Framework Detection

- **Framework:** pytest 7.4.3
- **Detection source:** pyproject.toml [tool.pytest.ini_options]
- **Assertion style:** plain assert (pytest-native)
- **Fixtures:** pytest fixtures via conftest.py
- **Runner command:** `python -m pytest`
- **Config file:** pyproject.toml
```

### Step 2: Collect Tests

```yaml
input:
  operation: collect_tests
  repo_path: /workspace/target-repo
  output_path: /workspace/output
```

**Result:** Copies test files to `output/section-08-source-code-tests/tests/`:
```
tests/
├── tests/
│   ├── test_cli.py
│   ├── test_parser.py
│   ├── test_config.py
│   └── conftest.py
└── pyproject.toml (test config section)
```

### Step 3: Execute Tests

```yaml
input:
  operation: execute_tests
  repo_path: /workspace/target-repo
  output_path: /workspace/output
```

**Agent executes:**
```bash
cd /workspace/target-repo && python -m pytest --tb=short -v 2>&1
```

**Output → `03-test-execution.md`:**
```markdown
# 8.3 Test Execution Results

## Summary
- **Total:** 25 | **Passed:** 22 | **Failed:** 2 | **Skipped:** 1
- **Duration:** 4.2s
- **Exit code:** 1 (failures present)

## Per-Test Results

| Test | File | Status | Duration | Failure Detail |
|------|------|--------|----------|----------------|
| test_parse_valid_input | test_parser.py | ✅ PASS | 0.01s | — |
| test_parse_empty_string | test_parser.py | ✅ PASS | 0.01s | — |
| test_cli_help_flag | test_cli.py | ✅ PASS | 0.12s | — |
| test_cli_invalid_flag | test_cli.py | ❌ FAIL | 0.08s | AssertionError: Expected exit code 2, got 1 |
| test_config_missing_file | test_config.py | ❌ FAIL | 0.02s | FileNotFoundError not raised |
| test_cli_version | test_cli.py | ⏭️ SKIP | — | Marked skip: "version TBD" |
| ... | ... | ... | ... | ... |

⚠️ **Ground Truth:** 2 failures recorded as-is. Source code NOT modified.
```

### Step 4: Analyze Coverage

```yaml
input:
  operation: analyze_coverage
  repo_path: /workspace/target-repo
  output_path: /workspace/output
  coverage_threshold: 80
```

**Output → `04-coverage-analysis.md`:**
```markdown
# 8.4 Coverage Analysis

## Overall: 73% line coverage

| Module | Lines | Covered | Coverage | Status |
|--------|-------|---------|----------|--------|
| src/cli.py | 120 | 102 | 85% | ✅ Above threshold |
| src/parser.py | 89 | 81 | 91% | ✅ Above threshold |
| src/config.py | 45 | 28 | 62% | ⚠️ Below 80% |
| src/utils.py | 34 | 0 | 0% | ❌ No tests |

## Gap Analysis
- **src/config.py** (62%): Missing coverage for lines 31-38 (error handling), 42-45 (env vars)
- **src/utils.py** (0%): Completely untested — contains helper functions
```

### Step 5: Extract Knowledge

```yaml
input:
  operation: extract_knowledge
  repo_path: /workspace/target-repo
  output_path: /workspace/output
```

**Output → `05-knowledge-extraction.md`:**
```markdown
# 8.5 Knowledge Extraction

## Test → Module → Behavior Mapping

| Test File:Line | Test Name | Module | Behavior | Confidence |
|----------------|-----------|--------|----------|------------|
| test_parser.py:12 | test_parse_valid_input | parser.parse() | Returns AST for valid input | HIGH |
| test_cli.py:45 | test_cli_invalid_flag | cli.main() | Actually returns exit code 1 for invalid flags (not 2) | HIGH |
| test_config.py:23 | test_config_missing_file | config.load() | Does NOT raise FileNotFoundError for missing file | HIGH |

## Patterns
- **Most tested:** parser module (91% coverage, 8 tests) → core functionality
- **Untested:** utils module → low-risk helper functions OR undocumented behavior
- **Mock boundaries:** None found → monolithic architecture (no service seams)
```

**Output → `06-test-derived-claims.md`:**
```markdown
# 8.6 Test-Derived Claims

## Verifiable Claims for Phase 3

CLAIM-001: "parser.parse() returns a valid AST node for well-formed input strings"
  Source: test_parser.py:12 | Confidence: HIGH

CLAIM-002: "parser.parse() raises ParseError for malformed input"
  Source: test_parser.py:28 | Confidence: HIGH

CLAIM-003: "cli.main() ACTUALLY returns exit code 1 for invalid flags (test expected 2)"
  Source: test_cli.py:45 | Confidence: HIGH | ⚠️ ACTUAL BEHAVIOR

CLAIM-004: "config.load() ACTUALLY does not raise FileNotFoundError for missing config"
  Source: test_config.py:23 | Confidence: HIGH | ⚠️ ACTUAL BEHAVIOR
```

---

## Example 2: JavaScript/Jest Project

**Scenario:** Reverse engineering a Node.js web API with Jest test suite.

### Step 1: Extract

```yaml
input:
  operation: extract
  repo_path: /workspace/express-api
  output_path: /workspace/output
  phase1_output: null  # Phase 1 not available — direct scan
```

**Agent executes:**
```bash
find /workspace/express-api -name "*.test.js" -o -name "*.spec.js" -o -name "*.test.ts"
```

**Output → `01-test-collection.md`:**
```markdown
# 8.1 Test Collection

| File Path | Lines | Tests | Assertions | Fixtures |
|-----------|-------|-------|------------|----------|
| src/__tests__/auth.test.js | 210 | 18 | 42 | beforeEach: 3 |
| src/__tests__/users.test.js | 156 | 14 | 31 | beforeEach: 2, afterAll: 1 |
| src/__tests__/middleware.test.js | 78 | 6 | 15 | jest.mock: 2 |

**Summary:** 3 test files, 38 tests, 88 assertions
```

**Output → `02-test-framework.md`:**
```markdown
# 8.2 Test Framework Detection

- **Framework:** Jest 29.7.0
- **Detection source:** package.json "jest" key + jest.config.js
- **Assertion style:** expect().toBe / expect().toEqual (Jest built-in)
- **Mock system:** jest.mock(), jest.fn()
- **Runner command:** `npx jest --verbose`
```

### Step 3: Execute Tests

**Agent executes:**
```bash
cd /workspace/express-api && npx jest --verbose --no-coverage 2>&1
```

**Output → `03-test-execution.md`:**
```markdown
# 8.3 Test Execution Results

## Summary
- **Total:** 38 | **Passed:** 35 | **Failed:** 3 | **Skipped:** 0
- **Duration:** 8.1s

## Key Failures

| Test | File | Failure |
|------|------|---------|
| should return 401 for expired token | auth.test.js | Expected 401, received 403 |
| should paginate results | users.test.js | Timeout — async operation exceeded 5s |
| should log request duration | middleware.test.js | console.log not called |

⚠️ Ground Truth: Failures reveal actual API behavior.
```

### Step 5: Extract Knowledge

**Output → `05-knowledge-extraction.md`:**
```markdown
# 8.5 Knowledge Extraction

## Key Insights from Jest Mocks

| Mock Target | Mocked In | Reveals |
|-------------|-----------|---------|
| jest.mock('../services/db') | auth.test.js | Auth module depends on db service |
| jest.mock('../services/cache') | users.test.js | Users module depends on cache service |

## Architecture Seams (from mock boundaries)
- auth → db (database dependency)
- users → cache (caching layer)
- middleware is standalone (no mocks)
```

**Output → `06-test-derived-claims.md`:**
```markdown
# 8.6 Test-Derived Claims

CLAIM-001: "Auth endpoint ACTUALLY returns 403 (not 401) for expired tokens"
  Source: auth.test.js:45 | Confidence: HIGH | ⚠️ ACTUAL BEHAVIOR

CLAIM-002: "Auth module depends on db service for token validation"
  Source: auth.test.js:3 (jest.mock) | Confidence: MEDIUM

CLAIM-003: "Users endpoint has async pagination that may exceed 5s under load"
  Source: users.test.js:89 | Confidence: HIGH | ⚠️ ACTUAL BEHAVIOR

CLAIM-004: "Users module depends on cache service"
  Source: users.test.js:4 (jest.mock) | Confidence: MEDIUM
```

---

## Common Patterns

### No Test Files Found
When `extract` finds zero test files:
```markdown
# 8.1 Test Collection
**Result:** No test files found in repository.
Patterns searched: test_*.py, *.test.js, *.spec.ts, *Test.java, *_test.go
**Impact:** Cannot execute Phase 2 test analysis. Phase 3 proceeds without test-derived claims.
```

### Coverage Tool Unavailable
When coverage cannot be measured:
```markdown
# 8.4 Coverage Analysis
**Result:** Coverage not measurable — pytest-cov not in project dependencies.
**Proxy:** 3 of 5 source modules have corresponding test files (60% file-level coverage estimate).
```
