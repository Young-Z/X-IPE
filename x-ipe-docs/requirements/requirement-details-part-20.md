# Requirement Details - Part 20

> Continued from: [requirement-details-part-19.md](x-ipe-docs/requirements/requirement-details-part-19.md)  
> Created: 03-06-2026

---

## EPIC-048: CR — Align Code-Touching Skills with Tool-Implementation Architecture

### Project Overview

A Change Request to align all code-touching skills (technical-design, bug-fix, code-refactor, acceptance-test, human-playground) and the refactoring-analysis tool with the `x-ipe-tool-implementation-*` architecture established in EPIC-045. Currently, only `x-ipe-task-based-code-implementation` leverages tool-implementation skills for language-specific best practices. Other code-touching skills operate independently, potentially producing inconsistent code quality, test patterns, and coding standards.

**Motivation:** EPIC-045 established a powerful architecture where language-specific implementation skills (`x-ipe-tool-implementation-python`, `x-ipe-tool-implementation-html5`, etc.) embed best practices for their stack. However, only the code-implementation orchestrator uses them. When bugs are fixed, code is refactored, acceptance tests are generated, or playground demos are created, these skills are bypassed — meaning a Python bug fix may not follow the same PEP 8/type hints/pytest patterns that a new Python feature implementation does.

**Source:** Analysis of EPIC-045 impact on downstream skills + CR-001 (config filtering & scope extension, 03-10-2026).

### User Request

> "Since EPIC-045, now all the detailed implementation is delegated to tool-implementation-*, so maybe we need to change technical design and bug fixing skills. If anything detail-specific design is required, it should consult these tools as well, so we can make sure the design, implementation, and fixing are using the same capability."

### Clarifications

| Question | Answer |
|----------|--------|
| Scope of "code-touching skills"? | technical-design (consultation), bug-fix (delegation), code-refactor (delegation), refactoring-analysis (consultation) |
| What about human-playground? | Creates demo code, not production code — excluded from this EPIC |
| How does bug-fix delegate without feature context? | Bug-fix generates mini AAA scenarios locally from bug context (reproduction steps → Arrange, trigger action → Act, expected behavior → Assert). Feature context is optional with synthetic fallback. |
| How does code-refactor delegate with incremental pattern? | Code-refactor Step 4 generates per-phase AAA scenarios describing target state. Each phase is delegated to tool skill individually. Checkpointing/commits managed by the refactor orchestrator, not the tool skill. |
| Does refactoring-analysis also delegate? | No — consultation only. It reads tool skill best practices to inform quality evaluation. |
| Do tool skills need new operations? | Yes — extend input contract with `operation: "fix"` and `operation: "refactor"` alongside existing `"implement"`. |

### High-Level Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| HLR-048.1 | Technical-design Step 4 (Research) scans available `x-ipe-tool-implementation-*` skills for built-in capabilities and uses findings to inform Part 2 design | P1 |
| HLR-048.2 | Bug-fix Steps 6-7 (Write Test, Implement Fix) delegate to matched tool-implementation skill using mini AAA scenarios generated from bug context | P1 |
| HLR-048.3 | Code-refactor Step 4 (Execute Refactoring) delegates each refactoring phase to matched tool-implementation skill via per-phase AAA scenarios | P1 |
| HLR-048.4 | Refactoring-analysis consults tool-implementation skills to understand target coding standards during quality evaluation | P2 |
| HLR-048.5 | Tool-implementation skills extend input contract to support `operation: "fix"` and `operation: "refactor"` alongside existing `"implement"` | P1 |
| HLR-048.6 | All code-touching skills use tools.json config-based filtering before semantic routing — same 3-layer pattern as code-implementation (config → discover → filter → route) | P1 |
| HLR-048.7 | Acceptance-test test code generation delegates to matched tool-implementation skill based on project tech_stack | P1 |
| HLR-048.8 | Human-playground replaces Python-only hardcoding with dynamic tool-implementation routing based on project tech_stack | P1 |

### Functional Requirements

#### FR-048.1: Technical Design — Tool Skill Consultation

- FR-048.1.1: Step 4 (Research) MUST scan `.github/skills/x-ipe-tool-implementation-*/` to discover available tool skills
- FR-048.1.2: Step 4 MUST read each discovered tool skill's "Built-In Practices" and "Operations" sections
- FR-048.1.3: Part 2 (Implementation Guide) SHOULD leverage tool skill capabilities rather than duplicating them (e.g., no need to specify "use PEP 8" when Python tool skill already enforces it)
- FR-048.1.4: Part 2 SHOULD focus on what tool skills NEED from the design: module boundaries, API contracts, data models, component hierarchy
- FR-048.1.5: Tool skill scanning is informational only — Part 2 format MUST remain independent of specific tool skill availability

#### FR-048.2: Bug Fix — Tool Skill Delegation

- FR-048.2.1: After Step 5 (Conflict Analysis), bug-fix MUST determine `program_type` and `tech_stack` from affected files (auto-detect from file extensions and project config)
- FR-048.2.2: Bug-fix MUST generate mini AAA scenario(s) from bug context:
  - Arrange: reproduction preconditions
  - Act: action that triggers the bug
  - Assert: expected correct behavior (what SHOULD happen)
- FR-048.2.3: Bug-fix Step 6 (Write Test) MUST route to matched `x-ipe-tool-implementation-*` skill with `operation: "fix"`, passing the AAA scenario for test generation
- FR-048.2.4: Bug-fix Step 7 (Implement Fix) MUST route to the same tool skill with the fix context, leveraging language-specific best practices
- FR-048.2.5: `feature_context` input is optional for tool skills when `operation: "fix"` — tool skills MUST support a synthetic fallback (`feature_id: "BUG-{task_id}"`, `technical_design_link: "N/A"`)
- FR-048.2.6: Bug-fix MUST verify tool skill output `lint_status == "pass"` as part of Step 8 (Verify) DoD
- FR-048.2.7: Bug-fix MUST preserve the TDD gate: test MUST fail before fix (tool skill handles both, but orchestrator verifies)

#### FR-048.3: Code Refactor — Tool Skill Delegation

- FR-048.3.1: Code-refactor Step 4 (Execute Refactoring) MUST route code changes through matched `x-ipe-tool-implementation-*` skill with `operation: "refactor"`
- FR-048.3.2: For each phase in the refactoring plan, code-refactor MUST generate AAA scenarios describing the target state for that phase
- FR-048.3.3: Code-refactor manages checkpointing (git commits) between phases — tool skills do NOT manage commits
- FR-048.3.4: Tool skill handles: code writing, test running, linting for each phase
- FR-048.3.5: Code-refactor maintains the incremental rollback pattern: if tool skill reports test failure for a phase, refactor orchestrator reverts that phase
- FR-048.3.6: Code-refactor MUST still read and apply `refactoring_suggestion` and `refactoring_principle` from analysis — tool skill implements the code, refactor orchestrator decides WHAT to change

#### FR-048.4: Refactoring Analysis — Tool Skill Consultation

- FR-048.4.1: Refactoring analysis SHOULD scan available `x-ipe-tool-implementation-*` skills during quality evaluation
- FR-048.4.2: When evaluating coding standards gaps, analysis SHOULD compare against tool skill built-in practices for the detected tech stack
- FR-048.4.3: Refactoring suggestions SHOULD reference tool skill capabilities when proposing target patterns

#### FR-048.5: Tool Skill Contract Extension

- FR-048.5.1: All `x-ipe-tool-implementation-*` skills MUST accept `operation: "implement" | "fix" | "refactor"` in input
- FR-048.5.2: `operation: "fix"` — tool skill receives narrow AAA scenario (1-2 scenarios), writes failing test first, then implements minimal fix
- FR-048.5.3: `operation: "refactor"` — tool skill receives per-phase AAA scenario describing target state, restructures code while preserving behavior
- FR-048.5.4: `operation: "fix"` and `"refactor"` MUST support optional `feature_context` (unlike `"implement"` which requires it)
- FR-048.5.5: All 6 tool skills (python, html5, typescript, java, mcp, general) MUST be updated with new operations
- FR-048.5.6: Standard output contract (implementation_files, test_files, test_results, lint_status) applies to all operations

#### FR-048.6: Config-Based Tool Filtering (CR-001)

- FR-048.6.1: All code-touching skills MUST read `x-ipe-docs/config/tools.json` to determine which tool-implementation skills are enabled before semantic routing
- FR-048.6.2: Each consuming stage MUST have its own config section in tools.json:
  - `stages.feature.bug_fix` — for bug-fix tool selection
  - `stages.refactoring.execution` — for code-refactor tool selection
  - `stages.feature.consultation` — for technical-design and refactoring-analysis tool scanning
  - `stages.quality.testing` — for acceptance-test tool selection
  - `stages.feature.playground` — for human-playground tool selection
- FR-048.6.3: Config filtering follows the same 3-layer pattern as code-implementation Step 3.1:
  1. DISCOVER: Scan `.github/skills/x-ipe-tool-implementation-*/`
  2. READ CONFIG: Extract the stage-specific section from tools.json
  3. FILTER: Only ENABLED tools participate in semantic matching (opt-in model)
  4. FORCE-ENABLE: `x-ipe-tool-implementation-general` always enabled (safety net)
- FR-048.6.4: IF config section missing or empty → `config_active = false` → all discovered tools treated as ENABLED (backwards compatibility)
- FR-048.6.5: IF config section exists → opt-in model: only explicitly enabled tools participate
- FR-048.6.6: `_extra_instruction` field supported per stage for supplementary semantic routing context

#### FR-048.7: Acceptance Test — Tool Skill Delegation (CR-001)

- FR-048.7.1: Acceptance-test Step 1.2 (Generate Test Plan) MUST determine `tech_stack` from specification and implementation files
- FR-048.7.2: Acceptance-test Step 3 (test code generation) MUST route to matched `x-ipe-tool-implementation-*` skill with `operation: "implement"` for language-specific test file creation
- FR-048.7.3: Tool skill generates test scaffolding following language-specific test conventions (pytest for Python, Vitest/Jest for JS/TS, JUnit for Java)
- FR-048.7.4: Chrome DevTools MCP integration for web UI testing remains unchanged — tool delegation handles test CODE generation, not browser interaction
- FR-048.7.5: `feature_context` is available from acceptance-test workflow (specification, implementation files)
- FR-048.7.6: IF no matching tool skill enabled → fall back to current inline test generation (graceful degradation)

#### FR-048.8: Human Playground — Tool Skill Delegation (CR-001)

- FR-048.8.1: Human-playground Step 1 (Create Examples) MUST determine `tech_stack` from feature's implementation files and project config
- FR-048.8.2: Human-playground MUST route playground file creation to matched `x-ipe-tool-implementation-*` skill with `operation: "implement"`
- FR-048.8.3: Playground file naming MUST be dynamic based on tool skill language: `playground_{feature_name}.{ext}` where `{ext}` is determined by the matched tool skill (`.py`, `.ts`, `.js`, `.java`, etc.)
- FR-048.8.4: Playground execution command MUST be dynamic: tool skill returns the appropriate run command (e.g., `uv run python`, `npx tsx`, `node`, `java`)
- FR-048.8.5: Playground test file naming follows the same dynamic pattern: `test_playground_{feature_name}.{ext}`
- FR-048.8.6: `feature_context` is available from playground workflow (specification, implementation files)
- FR-048.8.7: IF no matching tool skill enabled → fall back to current Python behavior (backwards compatibility)

### Conflict Analysis Summary

| # | Type | Affected Skill | Severity | Resolution |
|---|------|---------------|----------|------------|
| 1 | Dependency | Bug fix — missing feature_context | HIGH | Optional feature_context with synthetic fallback (FR-048.2.5) |
| 2 | Specification | Bug fix — no lint verification | MEDIUM | Integrate lint_status into verification (FR-048.2.6) |
| 3 | Design | Tool skills — only `implement` operation | CRITICAL | Extend contract with `fix` and `refactor` (FR-048.5) |
| 4 | Design | Code refactor — incremental vs greenfield | CRITICAL | Per-phase delegation; orchestrator manages checkpoints (FR-048.3) |
| 5 | Specification | Bug fix — no spec for AAA generation | HIGH | Local mini AAA from bug context (FR-048.2.2) |
| 6 | Dependency | Technical design — Part 2 format coupling | MEDIUM | Informational-only scanning (FR-048.1.5) |
| 7 | Design | Tool skills — feature-only architecture | HIGH | Optional feature_context for fix/refactor operations (FR-048.5.4) |
| 8 | Specification | EPIC-048 Out of Scope — acceptance-test, human-playground | LOW | Moved to in-scope by CR-001 (FR-048.7, FR-048.8) |
| 9 | Design | Human-playground — Python-only hardcoding | MEDIUM | Dynamic tool routing replaces hardcoded paths (FR-048.8.3, FR-048.8.4) |
| 10 | Specification | All delegation features — no config filtering | MEDIUM | 3-layer config pattern added to all consuming skills (FR-048.6) |

All conflicts are classified as **expected** — they are natural consequences of extending the tool-implementation architecture to maintenance workflows. All have documented mitigations in the functional requirements above.

### Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|--------------------|
| FEATURE-048-A | EPIC-048 | Tool Skill Contract Extension | v1.0 | Extend all 6 tool-implementation skills with `operation: "fix"` and `"refactor"`, optional feature_context for maintenance ops | - |
| FEATURE-048-B | EPIC-048 | Consultation Integration (Technical Design + Refactoring Analysis) | v1.0 | Add tool skill capability awareness with config-based filtering to technical-design Step 4 and refactoring-analysis quality evaluation | - |
| FEATURE-048-C | EPIC-048 | Bug Fix Delegation | v1.0 | Delegate bug-fix Steps 6-7 to matched tool-implementation skill with config filtering and mini AAA scenarios | FEATURE-048-A |
| FEATURE-048-D | EPIC-048 | Code Refactor Delegation | v1.0 | Delegate code-refactor Step 4 to matched tool-implementation skill with config filtering and per-phase AAA scenarios | FEATURE-048-A |
| FEATURE-048-E | EPIC-048 | Acceptance Test Tool Selection (CR-001) | v1.0 | Acceptance-test delegates test code generation to tool-implementation skill based on tech_stack with config filtering | - |
| FEATURE-048-F | EPIC-048 | Human Playground Tool Selection (CR-001) | v1.0 | Human-playground replaces Python-only with dynamic tool-implementation routing based on tech_stack with config filtering | - |

### Feature Details

#### FEATURE-048-A: Tool Skill Contract Extension (MVP)

**Version:** v1.0
**Priority:** P1
**Dependency:** None (foundation — all delegation features depend on this)

**Scope:**
- Extend input contract of all 6 `x-ipe-tool-implementation-*` skills (python, html5, typescript, java, mcp, general) with `operation: "implement" | "fix" | "refactor"`
- `operation: "fix"` — receives narrow AAA scenario (1-2 scenarios), writes failing test first, implements minimal fix
- `operation: "refactor"` — receives per-phase AAA scenario describing target state, restructures code while preserving behavior
- Make `feature_context` optional for `fix` and `refactor` operations (unlike `implement` which requires it)
- Standard output contract (implementation_files, test_files, test_results, lint_status) applies to all operations

**Key Deliverables:**
- 6 updated SKILL.md files (one per tool-implementation skill)
- Updated implementation-guidelines.md with new operation specifications

**Requirement Coverage:** FR-048.5.1 through FR-048.5.6

#### FEATURE-048-B: Consultation Integration (Technical Design + Refactoring Analysis)

**Version:** v1.0
**Priority:** P1
**Dependency:** None (consultation reads existing skill definitions, no new operations needed)

**Scope:**
- Update `x-ipe-task-based-technical-design` Step 4 (Research) to scan `.github/skills/x-ipe-tool-implementation-*/` and understand built-in capabilities
- Part 2 (Implementation Guide) leverages tool skill capabilities — focuses on what tool skills NEED (module boundaries, API contracts) rather than duplicating what they PROVIDE (coding standards)
- Tool skill scanning is informational only — Part 2 format remains independent of tool skill availability
- Update `x-ipe-tool-refactoring-analysis` to consult tool skills during quality evaluation and reference their best practices in refactoring suggestions

**Key Deliverables:**
- Updated x-ipe-task-based-technical-design/SKILL.md
- Updated x-ipe-tool-refactoring-analysis/SKILL.md

**Requirement Coverage:** FR-048.1.1 through FR-048.1.5, FR-048.4.1 through FR-048.4.3

#### FEATURE-048-C: Bug Fix Delegation

**Version:** v1.0
**Priority:** P1
**Dependency:** FEATURE-048-A (requires `operation: "fix"` in tool skills)

**Scope:**
- Update `x-ipe-task-based-bug-fix` Steps 6-7 to delegate to matched `x-ipe-tool-implementation-*` skill
- Auto-detect `program_type` and `tech_stack` from affected files
- Generate mini AAA scenario(s) from bug context: reproduction steps → Arrange, trigger action → Act, expected behavior → Assert
- Route to matched tool skill with `operation: "fix"` for test generation and fix implementation
- Preserve TDD gate: tool skill must confirm test fails before fix, passes after
- Integrate `lint_status` verification into Step 8 (Verify) DoD
- Support synthetic `feature_context` fallback when bug is not feature-associated

**Key Deliverables:**
- Updated x-ipe-task-based-bug-fix/SKILL.md

**Requirement Coverage:** FR-048.2.1 through FR-048.2.7

#### FEATURE-048-D: Code Refactor Delegation

**Version:** v1.0
**Priority:** P1
**Dependency:** FEATURE-048-A (requires `operation: "refactor"` in tool skills)

**Scope:**
- Update `x-ipe-task-based-code-refactor` Step 4 (Execute Refactoring) to route code changes through matched `x-ipe-tool-implementation-*` skill
- For each phase in the refactoring plan, generate AAA scenarios describing the target state
- Each phase is delegated individually — tool skill handles code writing, test running, linting
- Code-refactor orchestrator manages checkpointing (git commits) between phases
- If tool skill reports test failure for a phase, refactor orchestrator reverts that phase
- Refactor orchestrator still decides WHAT to change (from analysis/suggestions); tool skill decides HOW to write it

**Key Deliverables:**
- Updated x-ipe-task-based-code-refactor/SKILL.md

**Requirement Coverage:** FR-048.3.1 through FR-048.3.6

#### FEATURE-048-E: Acceptance Test Tool Selection (CR-001)

**Version:** v1.0
**Priority:** P1
**Dependency:** None (uses existing `operation: "implement"` — no contract extension needed)

**Scope:**
- Update `x-ipe-task-based-feature-acceptance-test` to route test code generation to matched `x-ipe-tool-implementation-*` skill
- Determine `tech_stack` from specification and implementation files in Step 1.2
- Read config from `tools.json` → `stages.quality.testing` section for enabled tools
- Route test scaffolding to matched tool skill with `operation: "implement"` — tool skill generates language-specific test files (pytest, Vitest/Jest, JUnit)
- Chrome DevTools MCP integration for web UI testing remains unchanged (tool delegation handles test CODE, not browser interaction)
- Graceful fallback to current inline test generation if no matching tool skill enabled

**Key Deliverables:**
- Updated x-ipe-task-based-feature-acceptance-test/SKILL.md
- tools.json `stages.quality.testing` section (added during implementation)

**Requirement Coverage:** FR-048.6.1 through FR-048.6.6, FR-048.7.1 through FR-048.7.6

#### FEATURE-048-F: Human Playground Tool Selection (CR-001)

**Version:** v1.0
**Priority:** P1
**Dependency:** None (uses existing `operation: "implement"` — no contract extension needed)

**Scope:**
- Update `x-ipe-task-based-human-playground` to route playground file creation to matched `x-ipe-tool-implementation-*` skill
- Determine `tech_stack` from feature's implementation files and project config in Step 1
- Read config from `tools.json` → `stages.feature.playground` section for enabled tools
- Replace hardcoded Python paths: file naming (`playground_{feature}.{ext}`), execution commands, test file naming — all dynamic based on matched tool skill
- Tool skill returns: file extension, run command, test framework
- Graceful fallback to current Python behavior if no matching tool skill enabled

**Key Deliverables:**
- Updated x-ipe-task-based-human-playground/SKILL.md
- tools.json `stages.feature.playground` section (added during implementation)

**Requirement Coverage:** FR-048.6.1 through FR-048.6.6, FR-048.8.1 through FR-048.8.7

### Non-Functional Requirements

- NFR-048.1: Tool skill consultation/delegation MUST NOT add more than 1 additional step to existing skill execution flows
- NFR-048.2: Skills MUST remain functional if tool-implementation skills are unavailable (graceful fallback to current inline behavior)
- NFR-048.3: All changes MUST go through `x-ipe-meta-skill-creator` candidate workflow — no direct SKILL.md edits

### Out of Scope

- ~~Human Playground skill (creates demo code, not production code)~~ **[Moved to in-scope by CR-001]**
- ~~Feature Acceptance Test skill (tests via Chrome DevTools, doesn't write production code)~~ **[Moved to in-scope by CR-001]**
- Creating new tool-implementation skills for new languages
- Changing the AAA scenario format itself
