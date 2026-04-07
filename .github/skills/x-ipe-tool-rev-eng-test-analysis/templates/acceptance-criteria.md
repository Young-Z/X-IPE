# Acceptance Criteria — Section 8: Source Code Tests

> Validation checklist for the test analysis extraction. Each criterion is marked
> `[REQ]` (required — must pass) or `[OPT]` (optional — should pass when applicable).

---

## 8.1 Test Collection

- [ ] `[REQ]` All test files cataloged with file path, line count, test count
- [ ] `[REQ]` Assertion count recorded per test file
- [ ] `[REQ]` Fixture/setup usage identified per test file
- [ ] `[OPT]` Test files grouped by module/component they test
- [ ] `[OPT]` Edge case tests explicitly flagged

## 8.2 Test Framework Detection

- [ ] `[REQ]` Test framework name and version identified
- [ ] `[REQ]` Detection source cited (config file, import, or Phase 1 Section 7)
- [ ] `[REQ]` Assertion style documented (assert, expect, should, etc.)
- [ ] `[OPT]` Fixture/factory patterns documented
- [ ] `[OPT]` Test runner configuration summarized

## 8.3 Test Execution & Results

- [ ] `[REQ]` All cataloged tests executed
- [ ] `[REQ]` Per-test pass/fail/skip status recorded
- [ ] `[REQ]` Failure messages and stack traces captured for failing tests
- [ ] `[REQ]` Source code was NEVER modified to fix failing tests
- [ ] `[REQ]` Execution duration recorded
- [ ] `[OPT]` Flaky test patterns identified (if multiple runs performed)

## 8.4 Coverage Analysis

- [ ] `[REQ]` Line coverage measured per module (or documented as unavailable with reason)
- [ ] `[REQ]` Modules below coverage threshold identified with gap ranges
- [ ] `[OPT]` Branch coverage measured
- [ ] `[OPT]` Coverage visualization (HTML report or screenshot) included
- [ ] `[OPT]` Trend analysis if historical coverage data exists

## 8.5 Knowledge Extraction

- [ ] `[REQ]` Each test mapped to module under test
- [ ] `[REQ]` Behavior validated by each test documented
- [ ] `[REQ]` Mock boundaries identified (reveal service seams)
- [ ] `[OPT]` Most-tested modules ranked (importance signal)
- [ ] `[OPT]` Untested modules identified (risk signal)
- [ ] `[OPT]` Fixture data shapes documented (valid data contracts)

## 8.6 Test-Derived Claims

- [ ] `[REQ]` Numbered claims generated from test assertions
- [ ] `[REQ]` Each claim cites source test file and line
- [ ] `[REQ]` Confidence level assigned (HIGH/MEDIUM/LOW)
- [ ] `[OPT]` Claims grouped by module for Phase 3 cross-validation
- [ ] `[OPT]` Failed-test claims clearly marked as "actual behavior" claims

---

## Overall Section Criteria

- [ ] `[REQ]` index.md links all subsection files
- [ ] `[REQ]` test-results.md contains machine-readable summary
- [ ] `[REQ]` tests/ subfolder contains copied test files
- [ ] `[REQ]` Test framework matches project's detected framework
- [ ] `[OPT]` screenshots/ contains coverage visualization
