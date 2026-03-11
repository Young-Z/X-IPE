# FEATURE-048-E: Acceptance Test Tool Selection — Specification

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 03-10-2026 | Flux 🔄 | Initial specification |

---

## Overview

Add config-filtered tool skill routing to acceptance-test Step 1.2 (tech_stack detection) and Step 3.1 (test code generation). Tool delegation handles test CODE generation using language-specific conventions, while Chrome DevTools MCP browser interaction remains unchanged.

---

## Acceptance Criteria

### AC-E.1: Tech Stack Detection

**Given** acceptance-test reaches Step 1.2 (Generate Test Plan)
**When** determining tech_stack
**Then:**
- [ ] AC-E.1.1: Detect `tech_stack` from specification and implementation files
- [ ] AC-E.1.2: Use 3-layer config pattern: discover → read `stages.quality.testing` → filter enabled tools
- [ ] AC-E.1.3: Semantically match tech_stack to enabled tool skill

### AC-E.2: Test Code Routing

**Given** Step 3.1 refines test cases
**When** generating actual test code files
**Then:**
- [ ] AC-E.2.1: Route to matched tool skill with `operation: "implement"` and AAA scenarios derived from test cases
- [ ] AC-E.2.2: Tool skill generates test scaffolding using language-specific conventions
- [ ] AC-E.2.3: Chrome DevTools MCP remains unchanged for browser interaction

### AC-E.3: Graceful Degradation

**Given** no matching tool skill enabled
**When** Step 3.1 tries to route
**Then:**
- [ ] AC-E.3.1: Fall back to current inline test generation
- [ ] AC-E.3.2: No regression in existing behavior

---

## Out of Scope

- Modifying Chrome DevTools MCP integration
- Changing test case template format
- Modifying test execution (Phase 4)
