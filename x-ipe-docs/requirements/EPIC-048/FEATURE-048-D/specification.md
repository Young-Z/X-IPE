# FEATURE-048-D: Code Refactor Delegation — Specification

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 03-10-2026 | Flux 🔄 | Initial specification |

---

## Overview

Replace hardcoded pytest/Vitest in code-refactor Phase 4 with config-filtered tool skill delegation. For each refactoring phase, generate per-phase AAA scenarios, route to matched tool skill with `operation: "refactor"`. Orchestrator manages git checkpoints and rollback — tool skills handle code writing, test running, and linting.

---

## Acceptance Criteria

### AC-D.1: Tool Routing

- [ ] AC-D.1.1: Route via `stages.refactoring.execution` config section
- [ ] AC-D.1.2: Matched tool skill receives `operation: "refactor"` with per-phase AAA scenarios
- [ ] AC-D.1.3: Orchestrator manages checkpoints/commits — tool skills do NOT manage git

### AC-D.2: Behavior Preservation

- [ ] AC-D.2.1: Tool skill reports test results; orchestrator reverts phase on failure
- [ ] AC-D.2.2: Structure changes only — no functional changes

### AC-D.3: Graceful Degradation

- [ ] AC-D.3.1: No matching tool → fall back to inline refactoring

---

## Out of Scope

- Modifying analysis steps (Phase 1-3)
- Changing sync tool integration
- Adding new refactoring techniques
