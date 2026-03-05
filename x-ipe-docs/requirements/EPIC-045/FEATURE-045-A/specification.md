# Feature Specification: Orchestrator Core + AAA Generator + General Fallback

> Feature ID: FEATURE-045-A  
> Epic ID: EPIC-045  
> Version: v1.0  
> Status: Refined  
> Last Updated: 03-05-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-05-2026 | Initial specification |

## Linked Mockups

N/A — This feature restructures AI skill files (SKILL.md). No UI components.

## Overview

This feature refactors `.github/skills/x-ipe-task-based-code-implementation/SKILL.md` from a monolithic skill that handles all coding inline into a **lightweight orchestrator** that delegates implementation to language-specific tool skills. The orchestrator introduces two new core capabilities: (1) **AAA (Arrange/Act/Assert) test scenario generation** that produces language-agnostic validation contracts from feature specifications and technical designs, and (2) **AI semantic tool routing** that automatically maps `tech_stack` entries to the appropriate `x-ipe-tool-implementation-*` skills without a hardcoded registry.

This is the **Minimum Viable Product (MVP)** for EPIC-045. It also creates `x-ipe-tool-implementation-general` as a fallback tool skill, ensuring the orchestrator has at least one tool skill to route to for any tech stack. All subsequent features (FEATURE-045-B through F) depend on this foundation.

The primary users are **AI agents** executing the X-IPE engineering workflow. Human developers benefit from better-structured implementation output with clearer test-to-requirement traceability. Framework maintainers can extend implementation capabilities by adding new tool skills without modifying the orchestrator.

## User Stories

1. **As an AI agent**, I want to receive AAA test scenarios from the orchestrator before implementing code, so that I have a clear, language-agnostic validation contract to implement against.

2. **As an AI agent**, I want the orchestrator to automatically select the right tool skill for each `tech_stack` entry, so that I don't need manual configuration to route implementation work.

3. **As a framework maintainer**, I want to add a new implementation tool skill by simply creating a folder under `.github/skills/x-ipe-tool-implementation-*/`, so that the orchestrator auto-discovers it without requiring orchestrator changes (Open-Closed Principle).

4. **As an AI agent working on a fullstack feature**, I want the orchestrator to invoke backend and frontend tool skills sequentially and aggregate results, so that multi-tool coordination works seamlessly.

5. **As an AI agent**, I want the orchestrator to retry a failed tool skill with error context before escalating to a human, so that transient failures are handled automatically.

6. **As a human developer**, I want clear traceability from acceptance criteria → AAA scenarios → code-level tests, so that I can verify the implementation covers all requirements.

## Acceptance Criteria

### AC-1: Orchestrator Skeleton

- [ ] AC-1.1: The refactored `x-ipe-task-based-code-implementation/SKILL.md` retains Steps 1–3 (Query Board, Learn Design, Read Architecture) unchanged from the current version
- [ ] AC-1.2: Step 4 is replaced from "Generate Tests via x-ipe-tool-test-generation" to "Generate AAA Scenarios"
- [ ] AC-1.3: Step 5 is replaced from "Implement Code" to "Route & Invoke Tool Skills"
- [ ] AC-1.4: Step 6 is replaced from "Verify" to "Validate Tool Skill Results"
- [ ] AC-1.5: Step 7 (Tracing) and Step 8 (Update Workflow Status) remain unchanged
- [ ] AC-1.6: The skill's Input Parameters section retains all existing fields (`feature_id`, `tech_stack`, `program_type`, `execution_mode`, `workflow`, `git_strategy`)
- [ ] AC-1.7: The skill's Output Result section retains compatible structure (same `task_completion_output` keys)
- [ ] AC-1.8: The `x-ipe-meta-skill-creator` special-case delegation is preserved in Step 5

### AC-2: AAA Scenario Generation

- [ ] AC-2.1: The orchestrator generates AAA scenarios in YAML-like format with `Arrange`, `Act`, `Assert` sections
- [ ] AC-2.2: Each scenario is tagged with exactly one of `@backend`, `@frontend`, or `@integration`
- [ ] AC-2.3: Every acceptance criterion from `specification.md` maps to at least one `@integration` scenario
- [ ] AC-2.4: Every API endpoint / service method from technical design maps to at least one `@backend` unit scenario (happy-path + error-path)
- [ ] AC-2.5: Every UI component / event handler from technical design maps to at least one `@frontend` unit scenario (happy-path + error-path)
- [ ] AC-2.6: Every error condition / edge case from technical design maps to a sad-path scenario in the relevant layer
- [ ] AC-2.7: Every data model / validation rule maps to at least one `@backend` unit scenario
- [ ] AC-2.8: The generation algorithm is documented in the skill as a step-by-step procedure (not left to agent interpretation)
- [ ] AC-2.9: The generated scenarios are stored/passed as structured data (not embedded in prose)

### AC-3: AI Semantic Tool Routing

- [ ] AC-3.1: The orchestrator scans `.github/skills/x-ipe-tool-implementation-*/` to discover available tool skills
- [ ] AC-3.2: The orchestrator uses LLM semantic understanding (not string matching) to map each `tech_stack` entry to a tool skill
- [ ] AC-3.3: If no specific tool skill matches a `tech_stack` entry, the orchestrator falls back to `x-ipe-tool-implementation-general`
- [ ] AC-3.4: If the general fallback is also insufficient (tech stack too exotic), the orchestrator signals to the human: "This feature requires a new tool skill"
- [ ] AC-3.5: Adding a new `x-ipe-tool-implementation-*` folder does NOT require any changes to the orchestrator SKILL.md

### AC-4: Tool Skill Invocation Interface

- [ ] AC-4.1: The orchestrator passes to each tool skill: (a) filtered AAA scenarios (matching the tool's layer tag), (b) source code path from technical design, (c) feature context (feature_id, title)
- [ ] AC-4.2: Each tool skill is expected to return: (a) implementation_files, (b) test_files, (c) test_results per Assert clause, (d) lint_status
- [ ] AC-4.3: The orchestrator validates that every Assert clause from the AAA scenarios has a corresponding pass/fail result
- [ ] AC-4.4: The orchestrator does NOT implement code itself — it only coordinates and validates

### AC-5: Sequential Multi-Tool Coordination

- [ ] AC-5.1: For features with multiple `tech_stack` entries, the orchestrator invokes tool skills one at a time (sequential, not parallel)
- [ ] AC-5.2: After all unit-level tool skills complete, the orchestrator runs `@integration` scenarios (with mocking/simulation)
- [ ] AC-5.3: The orchestrator produces an aggregated validation report covering all tool skills
- [ ] AC-5.4: Integration scenarios use mocking/simulation only (no real browser automation — that's Feature Acceptance Test)

### AC-6: Failure Handling

- [ ] AC-6.1: If a single tool skill fails, the orchestrator retries once with error context included in the prompt
- [ ] AC-6.2: If retry fails, the orchestrator reports to human with specific failure details
- [ ] AC-6.3: For partial multi-tool failure (e.g., Python passes, HTML5 fails), the orchestrator preserves passing results and re-invokes only the failed tool skill
- [ ] AC-6.4: If AAA scenario generation fails (spec too ambiguous), the orchestrator falls back to `x-ipe-tool-test-generation` (Phase 1 coexistence)
- [ ] AC-6.5: If integration scenarios fail after unit scenarios pass, the orchestrator provides both tool skill outputs to human for cross-layer contract mismatch diagnosis

### AC-7: General Fallback Tool Skill

- [ ] AC-7.1: `x-ipe-tool-implementation-general/SKILL.md` is created under `.github/skills/`
- [ ] AC-7.2: The general skill accepts the same interface as all tool skills (AAA scenarios + source code path)
- [ ] AC-7.3: The general skill researches language-specific best practices (via web search or LLM knowledge) before implementing
- [ ] AC-7.4: The general skill implements code and tests following the AAA contract
- [ ] AC-7.5: The general skill runs tests and returns results in the standard tool skill output format

### AC-8: Backward Compatibility

- [ ] AC-8.1: The refactored orchestrator supports all current `tech_stack` values (Python/Flask, JavaScript/Vanilla, TypeScript/React, Java/Spring, HTML/CSS, etc.)
- [ ] AC-8.2: The refactored orchestrator preserves `x-ipe-meta-skill-creator` delegation for `program_type: skills`
- [ ] AC-8.3: The refactored orchestrator preserves MCP builder delegation for MCP server features
- [ ] AC-8.4: The refactored orchestrator maintains existing workflow integration (feature board queries, workflow status updates)
- [ ] AC-8.5: The refactored orchestrator preserves existing input/output parameter interfaces
- [ ] AC-8.6: Existing projects with `x-ipe-tool-test-generation`-based test suites continue to work (Phase 1 coexistence)

### AC-9: Context Efficiency

- [ ] AC-9.1: For complex features, AAA scenarios are generated per-layer (not all at once) to avoid exceeding agent context limits
- [ ] AC-9.2: The skill documents a context budget management strategy (per-layer generation, chunking by component)

## Functional Requirements

### FR-1: Orchestrator SKILL.md Restructuring

**Description:** Refactor the execution procedure of `x-ipe-task-based-code-implementation/SKILL.md`.

**Details:**
- Input: Current SKILL.md with 8 steps (Query Board → Learn Design → Read Architecture → Generate Tests → Implement → Verify → Tracing → Update Status)
- Process: Replace Steps 4-6 with new orchestration logic; preserve Steps 1-3, 7-8
- Output: Refactored SKILL.md with Steps: Query Board → Learn Design → Read Architecture → Generate AAA Scenarios → Route & Invoke Tool Skills → Validate Results → Tracing → Update Status

### FR-2: AAA Scenario Generation Procedure

**Description:** Define the step-by-step algorithm for generating AAA scenarios from specification + technical design.

**Details:**
- Input: Feature specification (acceptance criteria, user stories, business rules) + Technical design (components, endpoints, models, error conditions)
- Process:
  1. Parse specification acceptance criteria → create `@integration` scenarios
  2. Parse technical design Part 2 → extract endpoints, components, models
  3. For each endpoint/component → create happy-path `@backend`/`@frontend` unit scenario
  4. For each error condition → create sad-path scenario in matching layer
  5. For each data model/validation rule → create `@backend` validation scenarios
  6. Tag each scenario with `@backend`, `@frontend`, or `@integration`
  7. Validate coverage: every AC has ≥1 scenario; every component has happy + sad path
- Output: List of tagged AAA scenarios in YAML-like format

### FR-3: Semantic Tool Skill Discovery and Routing

**Description:** Define the procedure for discovering and selecting tool skills at runtime.

**Details:**
- Input: `tech_stack` array from technical design (e.g., `["Python/Flask", "HTML/CSS/JavaScript"]`)
- Process:
  1. Scan `.github/skills/x-ipe-tool-implementation-*/` for available tool skills
  2. Read each tool skill's description/frontmatter to understand its coverage
  3. Use LLM semantic matching to map each `tech_stack` entry to a tool skill
  4. If no match → assign to `x-ipe-tool-implementation-general`
  5. If general is insufficient → signal "new tool skill needed"
- Output: Mapping of `tech_stack` entry → tool skill name

### FR-4: Tool Skill Input/Output Contract

**Description:** Define the standardized interface between orchestrator and tool skills.

**Details:**
- Input contract (orchestrator → tool skill):
  ```yaml
  aaa_scenarios: [list of tagged AAA scenarios filtered for this skill's layer]
  source_code_path: "path from technical design"
  feature_context:
    feature_id: "FEATURE-XXX-X"
    feature_title: "..."
    technical_design_link: "path to technical-design.md"
    specification_link: "path to specification.md"
  ```
- Output contract (tool skill → orchestrator):
  ```yaml
  implementation_files: [list of created/modified file paths]
  test_files: [list of test file paths]
  test_results:
    - scenario: "scenario name"
      assert_clause: "specific assert"
      status: "pass | fail"
      details: "error message if fail"
  lint_status: "pass | fail"
  lint_details: "linter output if fail"
  ```

### FR-5: Sequential Multi-Tool Execution Logic

**Description:** Define how the orchestrator coordinates multiple tool skill invocations.

**Details:**
- Input: Tech stack mapping from FR-3, AAA scenarios from FR-2
- Process:
  1. Split AAA scenarios by `@tag`: group `@backend` and `@frontend` by matched tool skill
  2. Invoke tool skills sequentially: first all `@backend`-tagged skills, then `@frontend`-tagged skills
  3. Collect results from each invocation
  4. After all unit-level skills complete, verify all unit Assert clauses pass
  5. If all unit asserts pass → run `@integration` scenarios (orchestrator handles these with mocking)
  6. Aggregate final validation report
- Output: Aggregated result with per-skill + per-scenario pass/fail

### FR-6: Failure Handling Procedures

**Description:** Define orchestrator behavior for each failure mode.

**Details:**
- Single skill failure → retry once with appended error context
- Partial multi-tool failure → preserve passing results, re-invoke only failed skill
- AAA generation failure → fall back to `x-ipe-tool-test-generation` (Phase 1)
- No matching skill + general insufficient → signal human
- Integration failure after unit pass → provide cross-layer diagnosis

### FR-7: General Fallback Tool Skill Creation

**Description:** Create `x-ipe-tool-implementation-general/SKILL.md`.

**Details:**
- Input: AAA scenarios + source code path (same interface as all tool skills)
- Process: Research language best practices → implement code → write tests → run tests → lint
- Output: Standard tool skill output (implementation_files, test_files, test_results, lint_status)
- Special behavior: Must perform web research or use LLM knowledge for unfamiliar languages before implementing

## Non-Functional Requirements

### NFR-1: Extensibility

Adding a new implementation tool skill (e.g., `x-ipe-tool-implementation-rust`) MUST NOT require any changes to the orchestrator SKILL.md. The new skill is auto-discovered by folder scanning + semantic matching.

### NFR-2: Performance Overhead

The orchestrator overhead (AAA generation + routing logic) MUST NOT add more than ~10% to the total implementation time compared to the current direct implementation approach.

### NFR-3: Context Efficiency

For complex features with >20 components, AAA scenarios MUST be generated per-layer to avoid exceeding agent context limits. The skill MUST document a context budget management strategy.

### NFR-4: Backward Compatibility

The refactored skill MUST preserve all existing input parameters, output format, and workflow integration. Existing features in progress MUST not be broken by this change.

## UI/UX Requirements

N/A — This feature modifies AI skill definition files (SKILL.md). No user interface changes.

## Dependencies

### Internal Dependencies

- **Current `x-ipe-task-based-code-implementation/SKILL.md`** — The file being refactored. Must understand current structure to preserve backward compatibility.
- **`x-ipe-tool-test-generation/SKILL.md`** — Must coexist as fallback during Phase 1. The orchestrator references it when AAA generation fails.
- **`x-ipe+feature+feature-board-management`** — Orchestrator queries this for Feature Data Model (unchanged from current).
- **`x-ipe-meta-skill-creator`** — Retained as special-case delegation for `program_type: skills`.
- **`mcp-builder`** — Retained as special-case delegation for MCP server features (until `x-ipe-tool-implementation-mcp` is created in FEATURE-045-E).

### External Dependencies

None — This feature modifies skill definition files only. No external libraries or services required.

## Business Rules

- **BR-1:** Every acceptance criterion from the specification MUST have at least one corresponding AAA scenario. Zero-coverage criteria are a validation failure.
- **BR-2:** Tool skills are NEVER modified by the orchestrator — they are invoked as black boxes with a defined interface.
- **BR-3:** `x-ipe-meta-skill-creator` delegation is NOT converted to a tool skill. It follows a different lifecycle (candidate/production staging, template compliance).
- **BR-4:** Integration scenarios use mocking/simulation ONLY. Real browser-based acceptance testing remains in `x-ipe-task-based-feature-acceptance-test`.
- **BR-5:** The orchestrator does NOT implement code itself. It only generates scenarios, routes, invokes, and validates.

## Edge Cases & Constraints

### Edge Case 1: Single-Stack Feature
**Scenario:** Feature has only one `tech_stack` entry (e.g., `["Python/Flask"]`).
**Expected Behavior:** Orchestrator invokes only one tool skill. `@integration` scenarios may be skipped if no cross-layer interaction exists.

### Edge Case 2: No Matching Tool Skill
**Scenario:** `tech_stack` contains an entry like `"Rust/Actix"` and no `x-ipe-tool-implementation-rust` exists.
**Expected Behavior:** Falls back to `x-ipe-tool-implementation-general`. If general cannot handle it, signals human: "This feature requires a new tool skill: x-ipe-tool-implementation-rust."

### Edge Case 3: Specification with No Acceptance Criteria
**Scenario:** Specification exists but has no explicit acceptance criteria section.
**Expected Behavior:** Orchestrator derives scenarios from functional requirements and user stories instead. Logs a warning that explicit ACs should be added.

### Edge Case 4: Very Large Technical Design
**Scenario:** Technical design has >20 components across multiple layers.
**Expected Behavior:** Per-layer AAA generation (generate @backend first, invoke backend tool skill, then generate @frontend, invoke frontend tool skill) to manage context budget.

### Edge Case 5: Tool Skill Fails on Retry
**Scenario:** A tool skill fails both initial invocation and retry.
**Expected Behavior:** Orchestrator preserves any passing tool skill results, marks the feature as partially implemented, and escalates to human with: (a) which tool skill failed, (b) error details from both attempts, (c) list of passing tool skills.

### Edge Case 6: Existing Test Suite Conflicts
**Scenario:** Project has existing tests from `x-ipe-tool-test-generation` that overlap with new AAA-derived tests.
**Expected Behavior:** Tool skills follow existing test file naming conventions. If conflicts arise, tool skills create a subfolder (e.g., `tests/feature-{id}/`) to isolate new tests.

### Edge Case 7: `program_type: skills`
**Scenario:** Feature requires creating skill files (`.github/skills/*/SKILL.md`).
**Expected Behavior:** Orchestrator delegates to `x-ipe-meta-skill-creator` as a special case (unchanged from current behavior). AAA scenarios are NOT generated for skill files.

### Edge Case 8: `program_type: mcp`
**Scenario:** Feature requires building an MCP server.
**Expected Behavior:** Until FEATURE-045-E creates `x-ipe-tool-implementation-mcp`, orchestrator delegates to existing `mcp-builder` skill. After FEATURE-045-E, routing goes through the standard semantic mapping.

## Out of Scope

- **Individual language-specific tool skills** (Python, HTML5, TypeScript, Java, MCP) — These are FEATURE-045-B through FEATURE-045-E
- **Test generation deprecation** (Phases 2 and 3) — This is FEATURE-045-F
- **Tracing instrumentation changes** — Tracing remains as a post-implementation step, not delegated to tool skills
- **Workflow template changes** — No changes to `workflow-template.json` in this feature
- **Real browser-based acceptance testing** — Remains in `x-ipe-task-based-feature-acceptance-test`
- **Parallel tool skill execution** — Out of scope; sequential only
- **Automatic test suite migration** — Existing tests from `x-ipe-tool-test-generation` are not automatically converted

## Technical Considerations

- The orchestrator SKILL.md is a markdown file (~500-600 lines). The refactoring modifies approximately 40% of the file (Steps 4-6 and related sections).
- The AAA scenario format should be defined as a clear YAML-like syntax within the SKILL.md so tool skills know exactly what to expect.
- The semantic routing logic should be defined as a procedure (not code), since AI agents execute it via LLM understanding.
- The general fallback skill is a separate SKILL.md file created alongside the orchestrator refactoring.
- References to `x-ipe-tool-test-generation` in the orchestrator should be preserved for Phase 1 coexistence but clearly marked as fallback.
- The `references/implementation-guidelines.md` file may need minor updates to reflect the new step structure.

## Open Questions

None — all design decisions resolved during ideation (IDEA-032) and requirement gathering (EPIC-045).
