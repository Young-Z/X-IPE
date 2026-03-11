# FEATURE-048-C: Bug Fix Delegation — Specification

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 03-10-2026 | Flux 🔄 | Initial specification |

---

## Overview

Replace hardcoded pytest/Vitest references in bug-fix Steps 6-7 with config-filtered tool skill delegation. The orchestrator generates mini AAA scenarios from bug context, routes to matched tool skill with `operation: "fix"`, and preserves the TDD gate.

---

## Acceptance Criteria

### AC-C.1: Tool Routing Before Test/Fix

**Given** bug-fix completes Step 5 (Conflict Analysis)
**When** preparing for Steps 6-7
**Then:**
- [ ] AC-C.1.1: Auto-detect `program_type` and `tech_stack` from affected files
- [ ] AC-C.1.2: Generate mini AAA scenarios (Arrange: preconditions, Act: trigger, Assert: expected)
- [ ] AC-C.1.3: Route via 3-layer config: discover → read `stages.feature.bug_fix` → filter → match

### AC-C.2: TDD Gate Preserved

**Given** tool skill receives `operation: "fix"`
**When** executing Step 6
**Then:**
- [ ] AC-C.2.1: Test MUST fail before fix (orchestrator verifies)
- [ ] AC-C.2.2: Tool skill generates language-specific test using its conventions

### AC-C.3: Fix Implementation

**Given** failing test exists
**When** executing Step 7
**Then:**
- [ ] AC-C.3.1: Same tool skill implements minimal fix
- [ ] AC-C.3.2: `lint_status == "pass"` verified in Step 8

### AC-C.4: Graceful Degradation

**Given** no matching tool skill or config missing
**When** Steps 6-7 execute
**Then:**
- [ ] AC-C.4.1: Fall back to current inline test/fix generation

---

## Out of Scope

- Modifying diagnosis steps (Steps 1-5)
- Changing verification step (Step 8) structure
- Adding new tool-implementation skills
