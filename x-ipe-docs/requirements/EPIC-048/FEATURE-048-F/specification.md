# FEATURE-048-F: Human Playground Tool Selection — Specification

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 03-10-2026 | Flux 🔄 | Initial specification |

---

## Overview

Replace Python-only hardcoding in human-playground with dynamic tool skill routing. File naming (`.py`→`.{ext}`), execution commands (`uv run python`→dynamic), and test file naming all become tool-dependent.

---

## Acceptance Criteria

### AC-F.1: Dynamic File Naming

**Given** playground creation reaches Step 1
**When** creating playground files
**Then:**
- [ ] AC-F.1.1: Detect tech_stack from feature implementation files
- [ ] AC-F.1.2: Route to matched tool skill using 3-layer config pattern (`stages.feature.playground`)
- [ ] AC-F.1.3: File naming dynamic: `playground_{feature_name}.{ext}` where ext from tool skill
- [ ] AC-F.1.4: Test file naming dynamic: `test_playground_{feature_name}.{ext}`

### AC-F.2: Dynamic Execution

**Given** playground files exist
**When** executing playground
**Then:**
- [ ] AC-F.2.1: Execution command dynamic from tool skill (not hardcoded `uv run python`)

### AC-F.3: Backward Compatibility

**Given** no matching tool skill or config missing
**When** creating playground
**Then:**
- [ ] AC-F.3.1: Fall back to Python behavior (`.py`, `uv run python`)

---

## Out of Scope

- Modifying playground directory structure
- Changing human validation workflow
