# Technical Design: Test Generation Deprecation Migration

> Feature ID: FEATURE-045-F | Version: v1.0 | Last Updated: 2025-07-15

> Specification: [specification.md](specification.md)

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents planning the migration.
> **Status:** DEFERRED — this documents the future migration path.

### Migration Overview

| Phase | Trigger | Key Change | Files Affected |
|-------|---------|------------|----------------|
| 1 (Done) | N/A | AAA primary, test-gen fallback | Orchestrator SKILL.md |
| 2 (Deferred) | ≥95% AAA success / 10+ features | test-gen consumes AAA input | test-gen SKILL.md, orchestrator |
| 3 (Deferred) | 100% AAA success / 20+ features | test-gen removed entirely | All files referencing test-gen |

### Program Type & Tech Stack

| Attribute | Value |
|-----------|-------|
| program_type | skills |
| tech_stack | Markdown/SKILL.md |
| primary_language | N/A (documentation + skill file edits) |

### Dependencies

| Dependency | Source | Usage |
|------------|--------|-------|
| FEATURE-045-A orchestrator | `.github/skills/x-ipe-task-based-code-implementation/SKILL.md` | Base file with Phase 1 coexistence |
| x-ipe-tool-test-generation | `.github/skills/x-ipe-tool-test-generation/SKILL.md` | Skill being deprecated |

---

## Part 2: Detailed Technical Design

### 1. Success Metrics Tracking

AAA success rate drives phase transitions. Tracking approach:

```
File: x-ipe-docs/metrics/aaa-success-log.md

| Feature ID | Date | AAA Generated? | Fallback Used? | Notes |
|------------|------|----------------|----------------|-------|
| FEATURE-XXX | YYYY-MM-DD | Yes/No | Yes/No | ... |
```

**Calculation:** `success_rate = features_without_fallback / total_features * 100`

The orchestrator appends a row after each feature implementation completes (Step 6 validation gate). This is a manual-friendly format; no automation required initially.

### 2. Phase 2 Adapter Design

When Phase 2 is triggered, `x-ipe-tool-test-generation/SKILL.md` is modified to accept AAA scenarios:

**Input mapping:**
```
Current input:  specification.md + technical-design.md → test-gen generates tests
New input:      aaa_scenarios (JSON array of Arrange/Act/Assert blocks) → test-gen maps to test cases
```

**Output mapping:**
```
Each generated test includes:
  - test_name: derived from AAA scenario ID
  - source_assert: reference to the AAA Assert clause
  - test_body: language-specific test code
```

**SKILL.md changes for test-gen:**
- Add new input field: `aaa_scenarios` (optional, takes precedence over spec-based generation)
- Add output field: `assert_mapping` (maps test → AAA Assert clause)
- Preserve existing spec-based path as fallback within test-gen itself

### 3. Phase 3 Removal Checklist

Files and references to update when removing `x-ipe-tool-test-generation`:

| Location | Action |
|----------|--------|
| `.github/skills/x-ipe-tool-test-generation/` | Archive or delete entire folder |
| `.github/skills/x-ipe-task-based-code-implementation/SKILL.md` | Remove fallback path (Step 4 AAA failure handler) |
| `.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md` | Remove test-gen references |
| `x-ipe-docs/requirements/EPIC-045/FEATURE-045-A/specification.md` | Mark Phase 1 coexistence as superseded |
| Any skill referencing `x-ipe-tool-test-generation` | Find via `grep -r "x-ipe-tool-test-generation" .github/skills/` |
| `.github/copilot-instructions.md` (if referenced) | Remove test-gen mentions |

### 4. Rollback Procedure

Each phase transition is a git commit (or series of commits) that can be reverted:

| Rollback | Method |
|----------|--------|
| Phase 2 → Phase 1 | `git revert` the adapter commits; orchestrator fallback still works |
| Phase 3 → Phase 2 | `git revert` the removal commits; restore test-gen folder from git history |

**Safety net:** Before each phase transition, create a git tag:
- `deprecation/phase-2-start`
- `deprecation/phase-3-start`

### 5. Decision Criteria Summary

```
Phase 1 → Phase 2:
  ✅ AAA success rate ≥95% over last 10+ features
  ✅ No critical bugs in AAA generation
  ✅ Human approval

Phase 2 → Phase 3:
  ✅ AAA success rate 100% over last 20+ features
  ✅ Zero fallback invocations in last 20 features
  ✅ Adapter has been stable for ≥1 iteration cycle
  ✅ Human approval
```

### Error Handling

| Scenario | Response |
|----------|----------|
| AAA success rate drops below threshold after Phase 2 | Halt further migration; do NOT proceed to Phase 3 |
| Phase 3 removal breaks a workflow | Immediate rollback via git revert to Phase 2 state |
| New skill references test-gen after Phase 3 | `grep` check in CI/PR review catches stale references |

---

> **Reminder:** This entire design is DEFERRED. No implementation work should begin until Phase 2 transition criteria are met.
