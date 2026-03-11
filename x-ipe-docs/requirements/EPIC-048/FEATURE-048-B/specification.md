# FEATURE-048-B: Consultation Integration (Technical Design + Refactoring Analysis)

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 03-10-2026 | Flux 🔄 | Initial specification |

---

## Overview

Add tool-skill capability awareness with config-based filtering to `x-ipe-task-based-technical-design` (Step 2.2 Research) and `x-ipe-tool-refactoring-analysis` (quality evaluation). Both skills **consult** tool skills for information — they do NOT delegate code execution.

**Key Principle:** Consultation is informational only. Part 2 format remains independent of tool availability (FR-048.1.5).

---

## User Stories

### US-B.1: Technical Design Research
As a **technical designer**, I want the research step to automatically discover available tool-implementation skills and understand their built-in capabilities, so that Part 2 focuses on what tools need (boundaries, APIs, data models) rather than duplicating what they provide (coding standards, linting rules).

### US-B.2: Refactoring Analysis Quality Evaluation
As a **refactoring analyst**, I want quality evaluation to compare detected coding standard gaps against tool skill built-in practices for the project's tech stack, so that refactoring suggestions reference actual tool capabilities and avoid recommending practices that tools already enforce.

---

## Acceptance Criteria

### AC-B.1: Tool Skill Discovery with Config Filtering (Technical Design)

**Given** a technical design execution reaches Step 2.2 (Research)
**When** the designer scans for tool-implementation skills
**Then:**
- [ ] AC-B.1.1: Read `x-ipe-docs/config/tools.json` → `stages.feature.consultation` section
- [ ] AC-B.1.2: Scan `.github/skills/x-ipe-tool-implementation-*/` to discover all available tools
- [ ] AC-B.1.3: IF config section exists → filter to only ENABLED tools (opt-in)
- [ ] AC-B.1.4: IF config section missing/empty → `config_active = false` → all discovered tools enabled (backwards compat)
- [ ] AC-B.1.5: `x-ipe-tool-implementation-general` always force-enabled regardless of config

### AC-B.2: Tool Capability Reading (Technical Design)

**Given** enabled tool skills have been identified
**When** the designer reads tool capabilities
**Then:**
- [ ] AC-B.2.1: Read each enabled tool's "Built-In Practices" section (coding standards, linting, formatting)
- [ ] AC-B.2.2: Read each enabled tool's "Operations" section (implement, fix, refactor)
- [ ] AC-B.2.3: Document findings as "Tool Capability Summary" for design decisions

### AC-B.3: Part 2 Leveraging (Technical Design)

**Given** tool capabilities have been read
**When** writing Part 2 (Implementation Guide)
**Then:**
- [ ] AC-B.3.1: SHOULD reference tool capabilities rather than duplicating (e.g., "Python tool enforces PEP 8" instead of specifying PEP 8 rules)
- [ ] AC-B.3.2: SHOULD focus on what tools NEED: module boundaries, API contracts, data models, component hierarchy
- [ ] AC-B.3.3: Part 2 format MUST remain independent of specific tool availability (FR-048.1.5)

### AC-B.4: Refactoring Analysis Tool Consultation

**Given** a refactoring analysis scans code quality
**When** evaluating coding standard gaps
**Then:**
- [ ] AC-B.4.1: Read `x-ipe-docs/config/tools.json` → `stages.feature.consultation` section (same section as technical design)
- [ ] AC-B.4.2: Scan and filter tool skills using same 3-layer pattern
- [ ] AC-B.4.3: Compare detected gaps against tool skill built-in practices for the detected tech stack
- [ ] AC-B.4.4: Refactoring suggestions reference tool capabilities when proposing target patterns

### AC-B.5: Backward Compatibility

**Given** `stages.feature.consultation` does NOT exist in tools.json
**When** either skill runs
**Then:**
- [ ] AC-B.5.1: All discovered tools treated as enabled (`config_active = false`)
- [ ] AC-B.5.2: Existing behavior preserved — no regression

---

## Functional Requirements

| ID | Requirement | Source |
|----|------------|--------|
| FR-B.1 | Technical design Step 2.2 scans `.github/skills/x-ipe-tool-implementation-*/` | FR-048.1.1 |
| FR-B.2 | Step 2.2 reads "Built-In Practices" and "Operations" sections | FR-048.1.2 |
| FR-B.3 | Part 2 leverages tool capabilities, avoids duplication | FR-048.1.3 |
| FR-B.4 | Part 2 focuses on module boundaries, API contracts, data models | FR-048.1.4 |
| FR-B.5 | Tool scanning is informational — Part 2 format independent | FR-048.1.5 |
| FR-B.6 | Refactoring analysis scans tools during quality evaluation | FR-048.4.1 |
| FR-B.7 | Analysis compares gaps against tool built-in practices | FR-048.4.2 |
| FR-B.8 | Suggestions reference tool capabilities | FR-048.4.3 |
| FR-B.9 | Both skills use config filtering via `stages.feature.consultation` | FR-048.6.1-6.6 |

---

## Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | No tool skills discovered (empty `.github/skills/`) | Skip consultation step, proceed with standard research |
| 2 | tools.json missing entirely | `config_active = false`, all discovered tools enabled |
| 3 | `stages.feature.consultation` empty object `{}` | Treated as "no tools configured" → all enabled |
| 4 | Tool skill has no "Built-In Practices" section | Skip that tool, note in summary |
| 5 | Multiple tools match same tech stack | Include all — consultation is informational, no routing conflict |

---

## Out of Scope

- Delegating code execution to tool skills (that's FEATURE-048-C/D)
- Modifying Part 2 output format
- Changing refactoring-analysis scoring algorithm
- Adding new tool-implementation skills
