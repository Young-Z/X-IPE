# Specification: FEATURE-048-A — Tool Skill Contract Extension

> Feature ID: FEATURE-048-A
> Epic: EPIC-048
> Status: In Refinement
> Created: 03-10-2026

## Version History

| Version | Date | Changes | CR |
|---------|------|---------|----|
| v1.0 | 03-10-2026 | Initial specification | - |

## Linked Mockups

N/A — This feature modifies skill definition files, not UI components.

## Overview

Extend the input contract of all 6 `x-ipe-tool-implementation-*` skills to support `operation: "fix"` and `operation: "refactor"` alongside the existing `operation: "implement"`. This is the MVP foundation that all delegation features (FEATURE-048-C, D) depend on. Additionally, make `feature_context` optional for `fix` and `refactor` operations to support maintenance workflows where bugs/refactoring may not be associated with a specific feature.

## User Stories

- **US-048-A.1:** As a bug-fix orchestrator, I want to delegate test writing and fix implementation to a language-specific tool skill with `operation: "fix"`, so that bug fixes follow the same coding standards as new implementations.
- **US-048-A.2:** As a code-refactor orchestrator, I want to delegate per-phase code changes to a language-specific tool skill with `operation: "refactor"`, so that refactored code adheres to language-specific best practices.
- **US-048-A.3:** As a maintenance workflow, I want to invoke tool skills without a full `feature_context` when fixing bugs or refactoring outside a feature pipeline, so that tool skills remain usable in all contexts.

## Acceptance Criteria

### AC-048-A.1: Fix Operation Support

- AC-048-A.1.1: All 6 tool skills accept `operation: "fix"` in their input contract
- AC-048-A.1.2: When `operation: "fix"`, tool skill receives 1-2 narrow AAA scenarios describing the bug
- AC-048-A.1.3: Fix operation writes a failing test FIRST, then implements the minimal fix
- AC-048-A.1.4: Fix operation preserves TDD gate: test must fail before fix, pass after
- AC-048-A.1.5: Fix operation returns standard output (implementation_files, test_files, test_results, lint_status)

### AC-048-A.2: Refactor Operation Support

- AC-048-A.2.1: All 6 tool skills accept `operation: "refactor"` in their input contract
- AC-048-A.2.2: When `operation: "refactor"`, tool skill receives per-phase AAA scenarios describing the target state
- AC-048-A.2.3: Refactor operation restructures code while preserving existing behavior
- AC-048-A.2.4: Refactor operation runs tests after changes — reports pass/fail per scenario
- AC-048-A.2.5: Refactor operation does NOT manage git commits (orchestrator responsibility)
- AC-048-A.2.6: Refactor operation returns standard output (implementation_files, test_files, test_results, lint_status)

### AC-048-A.3: Optional Feature Context

- AC-048-A.3.1: `feature_context` is optional when `operation` is `"fix"` or `"refactor"`
- AC-048-A.3.2: When `feature_context` is omitted, tool skill uses synthetic fallback: `feature_id: "BUG-{task_id}"` or `"REFACTOR-{task_id}"`, `technical_design_link: "N/A"`
- AC-048-A.3.3: `feature_context` remains required for `operation: "implement"` (no change to existing behavior)

### AC-048-A.4: Backward Compatibility

- AC-048-A.4.1: Existing `operation: "implement"` behavior is unchanged across all 6 tool skills
- AC-048-A.4.2: No changes to the standard output contract structure
- AC-048-A.4.3: implementation-guidelines.md reference document is updated with new operations

## Functional Requirements

- **FR-048-A.1:** Each tool skill MUST add two new `<operation>` blocks (`fix` and `refactor`) alongside the existing `implement` block
- **FR-048-A.2:** The `fix` operation block MUST enforce TDD order: write failing test → implement fix → verify test passes
- **FR-048-A.3:** The `refactor` operation block MUST enforce behavior preservation: run tests before, apply changes, run tests after
- **FR-048-A.4:** Input validation MUST accept `operation: "implement" | "fix" | "refactor"` — reject unknown values
- **FR-048-A.5:** When `operation` is `"fix"` or `"refactor"` and `feature_context` is absent, tool skill MUST generate synthetic context without error
- **FR-048-A.6:** Each language-specific tool skill (python, typescript, html5, java, mcp) MUST define language-appropriate behaviors for fix and refactor:
  - Python: pytest patterns, PEP 8/type hints for fixes
  - TypeScript: Vitest/Jest patterns, ESLint compliance for fixes
  - HTML5: DOM testing patterns, CSS validation for fixes
  - Java: JUnit patterns, code style for fixes
  - MCP: Protocol-specific test patterns
  - General: Generic patterns (fallback)

## Non-Functional Requirements

- **NFR-048-A.1:** Adding new operations MUST NOT increase tool skill SKILL.md beyond 500 lines
- **NFR-048-A.2:** All changes MUST go through `x-ipe-meta-skill-creator` candidate workflow
- **NFR-048-A.3:** Skills MUST remain functional with only `operation: "implement"` if fix/refactor blocks are somehow missing (graceful degradation)

## Dependencies

### Internal
- EPIC-045 tool-implementation architecture (completed) — provides the base skills to extend
- implementation-guidelines.md — must be updated with new operation specs

### External
- None

## Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | `operation: "fix"` with empty AAA scenarios | Reject with clear error: "Fix operation requires at least 1 AAA scenario" |
| 2 | `operation: "refactor"` with no test files in project | Tool skill creates initial test files, then refactors |
| 3 | `operation: "fix"` test doesn't fail before fix | Tool skill reports: "TDD gate violation — test already passes, review scenario" |
| 4 | Unknown operation value (e.g., `"deploy"`) | Reject with clear error: "Unknown operation: {value}. Supported: implement, fix, refactor" |
| 5 | `operation: "implement"` without feature_context | Reject (unchanged behavior — implement still requires feature_context) |

## Out of Scope

- Config-based tool filtering (covered by FR-048.6, consumed by FEATURE-048-B through F)
- Consuming skills (bug-fix, code-refactor) — covered by FEATURE-048-C and D
- New tool skills for new languages — separate effort
- Changes to AAA scenario format itself

## Technical Considerations

- The 6 tool skills share a common structure — changes can be templated across all 6
- implementation-guidelines.md serves as the canonical I/O contract reference and must be updated first
- Each language skill has distinct built-in practices — fix/refactor blocks must be language-aware, not copy-pasted
- The general skill serves as safety-net fallback — its fix/refactor must be broadly applicable

---

## Change History

| Date | Change | By |
|------|--------|----|
| 03-10-2026 | Initial specification created | Flux |
