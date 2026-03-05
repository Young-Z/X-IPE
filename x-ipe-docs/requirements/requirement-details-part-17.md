# Requirement Details - Part 17

> Continued from: [requirement-details-part-16.md](x-ipe-docs/requirements/requirement-details-part-16.md)  
> Created: 03-05-2026

---

## EPIC-045: CR — Restructure Implementation Skill into Orchestrator + Language-Specific Tool Skills

### Project Overview

A Change Request to restructure `x-ipe-task-based-code-implementation` from a monolithic skill that handles all coding inline into a **lightweight orchestrator** that delegates implementation to **language/purpose-specific tool skills** (`x-ipe-tool-implementation-{name}`). The orchestrator generates **language-agnostic AAA (Arrange/Act/Assert) test scenarios** from feature specifications and technical designs, then passes them to the appropriate tool skills as validation contracts. This follows the **Strategy Pattern** for Separation of Concerns, Abstraction, and Loose Coupling.

**Source:** [IDEA-032 Refined Summary](x-ipe-docs/ideas/032. CR-Update implementation skill/refined-idea/idea-summary-v1.md)

### User Request

> "For x-ipe-task-based-implementation-skill, provide a basic skeleton focused on task-based flow. For different languages and purposes, have different tool-level implementations. The task-based skill generates natural language test scenarios (AAA format) from spec + technical design. Tool skills implement code and tests against these scenarios. Include HTML5, Python, TypeScript, Java, MCP, and general-purpose fallback tool skills."

### Clarifications

| Question | Answer |
|----------|--------|
| Test scenario format? | YAML-like AAA (Arrange/Act/Assert) — chosen over Gherkin/BDD for simplicity and directness in AI-to-AI handoff |
| Scenario granularity? | `@backend`/`@frontend` → unit-level; `@integration` → functional-level with mocking |
| How does orchestrator select tool skills? | AI semantic mapping — agent auto-maps `tech_stack` from Technical Design to available `x-ipe-tool-implementation-*` skills |
| Tool skill naming? | `x-ipe-tool-implementation-{language/purpose}` (e.g., python, html5, typescript, java, mcp, general) |
| Non-code implementations? | `x-ipe-meta-skill-creator` stays as special-case delegation (different lifecycle). MCP builder becomes `x-ipe-tool-implementation-mcp` |
| Source code entry? | Technical Design defines source paths per tech layer; tool skills learn existing structure or suggest based on best practices |
| Integration test approach? | Mocking/simulation only; real browser-based acceptance testing stays in `x-ipe-task-based-feature-acceptance-test` |
| Linting & formatting? | Each tool skill handles its own language-specific linting/formatting |
| Tracing instrumentation? | Skipped for now — added later as enhancement |
| Rollout scope? | All at once — 6 tool skills + orchestrator refactoring in one EPIC |
| `x-ipe-tool-test-generation` deprecation? | Phased: coexistence → adapter → removal |
| Parallel execution of tool skills? | No — sequential execution (single AI agent). Tool skills invoked one at a time. |

### High-Level Requirements

1. **HLR-045.1: Orchestrator Refactoring** — `x-ipe-task-based-code-implementation` MUST be refactored into a lightweight orchestrator that:
   - Reads feature specification and technical design (unchanged from current)
   - Generates natural-language AAA test scenarios from spec + technical design
   - Routes scenarios to appropriate tool skills based on `tech_stack`
   - Validates that all tool skill outputs satisfy their AAA contract
   - Updates workflow status (unchanged from current)
   - No longer contains inline implementation logic

2. **HLR-045.2: AAA Test Scenario Generation** — The orchestrator MUST generate language-agnostic test scenarios in YAML-like AAA format:
   - Each acceptance criterion → at least one `@integration` scenario
   - Each API endpoint/service method → `@backend` unit scenarios (happy + sad path)
   - Each UI component/event handler → `@frontend` unit scenarios (happy + sad path)
   - Each error condition → sad-path scenario in the relevant layer
   - Scenarios tagged with `@backend`, `@frontend`, `@integration` for routing

3. **HLR-045.3: Language-Specific Tool Skills** — Six implementation tool skills MUST be created following the naming pattern `x-ipe-tool-implementation-{name}`:
   - `x-ipe-tool-implementation-python` — Python (Flask, FastAPI, Django, CLI, libraries)
   - `x-ipe-tool-implementation-html5` — HTML5, CSS3, JavaScript (vanilla and frameworks)
   - `x-ipe-tool-implementation-typescript` — TypeScript (React, Vue, Angular, Node.js)
   - `x-ipe-tool-implementation-java` — Java (Spring Boot, Maven, Gradle)
   - `x-ipe-tool-implementation-mcp` — MCP servers (adapted from existing `mcp-builder`)
   - `x-ipe-tool-implementation-general` — General-purpose fallback for unmapped stacks

4. **HLR-045.4: Tool Skill Contract** — Each tool skill MUST:
   - Accept AAA scenarios + source code path as input from the orchestrator
   - Learn existing code structure at the source path before implementing
   - Implement code following language-specific best practices and principles
   - Write code-level tests that map to the AAA scenarios
   - Run tests and return pass/fail results as validation gate to orchestrator
   - Handle its own linting and formatting for its language

5. **HLR-045.5: AI Semantic Tool Routing** — The orchestrator MUST use the AI agent's LLM capability to semantically map `tech_stack` entries from the Technical Design to available `x-ipe-tool-implementation-*` skills. No hardcoded registry — auto-discovery via skill folder scanning + semantic matching.

6. **HLR-045.6: Source Path Management** — The orchestrator MUST:
   - Read source paths per tech layer from the Technical Design document
   - Pass the correct source path to each tool skill
   - If paths are not specified in Technical Design, tool skills MUST suggest paths based on project context and language best practices

7. **HLR-045.7: Multi-Tool Coordination** — For features requiring multiple tech stacks, the orchestrator MUST:
   - Invoke tool skills sequentially (not in parallel)
   - Collect results from each tool skill
   - Validate unit-level AAA assertions per tool skill
   - Run `@integration` scenarios with mocking after all tool skills complete
   - Report aggregated results

8. **HLR-045.8: Failure Handling** — The orchestrator MUST handle:
   - Single tool skill failure → retry once with error context
   - Partial multi-tool failure → preserve passing results, re-invoke failed skill only
   - No matching tool skill AND general fallback insufficient → signal "new tool skill needed"
   - AAA scenario generation failure → fall back to `x-ipe-tool-test-generation` (Phase 1)

9. **HLR-045.9: Test Generation Deprecation** — `x-ipe-tool-test-generation` MUST be deprecated in phases:
   - Phase 1 (Coexistence): Orchestrator generates AAA AND invokes test-generation as fallback
   - Phase 2 (Adapter): Test-generation refactored to consume AAA scenarios as input
   - Phase 3 (Removal): Test-generation removed; all references updated

10. **HLR-045.10: Backward Compatibility** — The refactored orchestrator MUST:
    - Support all current `tech_stack` values and `program_type` combinations
    - Continue to handle `x-ipe-meta-skill-creator` as a special-case delegation
    - Maintain the existing workflow integration (feature board, workflow status updates)
    - Preserve existing input/output parameter interfaces

### Functional Requirements

**FR-045.1: Orchestrator Flow**
- FR-045.1.1: The orchestrator MUST query the feature board for the Feature Data Model (unchanged)
- FR-045.1.2: The orchestrator MUST read technical design and specification (unchanged)
- FR-045.1.3: The orchestrator MUST generate AAA scenarios before invoking any tool skill
- FR-045.1.4: The orchestrator MUST route AAA scenarios to tool skills based on `@tag` + `tech_stack` mapping
- FR-045.1.5: The orchestrator MUST validate all Assert clauses pass before marking implementation complete
- FR-045.1.6: The orchestrator MUST update workflow status on completion (unchanged)

**FR-045.2: AAA Scenario Format**
- FR-045.2.1: Scenarios MUST follow YAML-like AAA structure with Arrange, Act, Assert sections
- FR-045.2.2: Scenarios MUST be tagged with `@backend`, `@frontend`, or `@integration`
- FR-045.2.3: `@backend` and `@frontend` scenarios MUST be unit-level (isolated component tests)
- FR-045.2.4: `@integration` scenarios MUST be functional-level with mocking/simulation
- FR-045.2.5: Each acceptance criterion from specification MUST map to at least one scenario
- FR-045.2.6: Each component from technical design MUST have both happy-path and sad-path scenarios

**FR-045.3: Tool Skill Interface**
- FR-045.3.1: Each tool skill MUST accept `aaa_scenarios` (list of tagged scenarios) as input
- FR-045.3.2: Each tool skill MUST accept `source_code_path` as input
- FR-045.3.3: Each tool skill MUST return `implementation_files` (list of created/modified files)
- FR-045.3.4: Each tool skill MUST return `test_files` (list of test files created)
- FR-045.3.5: Each tool skill MUST return `test_results` (pass/fail per Assert clause)
- FR-045.3.6: Each tool skill MUST return `lint_status` (pass/fail)

**FR-045.4: Language Best Practices**
- FR-045.4.1: Python tool skill MUST enforce PEP 8, type hints, pytest patterns
- FR-045.4.2: HTML5 tool skill MUST enforce semantic HTML, accessibility, responsive design, ES6+
- FR-045.4.3: TypeScript tool skill MUST enforce strict mode, interface-first design, vitest/jest
- FR-045.4.4: Java tool skill MUST enforce clean architecture, JUnit 5, SOLID principles
- FR-045.4.5: MCP tool skill MUST enforce protocol compliance, tool schemas, transport types
- FR-045.4.6: General tool skill MUST research language-specific best practices before implementing

**FR-045.5: Semantic Routing**
- FR-045.5.1: The orchestrator MUST scan `.github/skills/x-ipe-tool-implementation-*/` to discover available tool skills
- FR-045.5.2: The orchestrator MUST use LLM semantic understanding to match `tech_stack` entries to tool skills
- FR-045.5.3: If no tool skill matches, the orchestrator MUST fall back to `x-ipe-tool-implementation-general`
- FR-045.5.4: If general fallback is insufficient, the orchestrator MUST signal to human

### Non-Functional Requirements

- **NFR-045.1: Extensibility** — Adding a new implementation tool skill MUST NOT require changes to the orchestrator
- **NFR-045.2: Performance** — The orchestrator overhead (AAA generation + routing) MUST NOT add more than ~10% to total implementation time
- **NFR-045.3: Context Efficiency** — For complex features, AAA scenarios MUST be generated per-layer to avoid exceeding agent context limits

### Constraints

- All implementation tool skills follow naming pattern `x-ipe-tool-implementation-{language/purpose}`
- `x-ipe-meta-skill-creator` remains a special-case delegation (different lifecycle — candidate/production staging)
- Integration test scenarios use mocking only — no real browser automation
- Tracing instrumentation is out of scope for this EPIC (future enhancement)
- Tool skills are invoked sequentially by the orchestrator (single AI agent model)
- This is a CR — existing workflow integration must be preserved

### Open Questions

- None — all questions resolved during ideation and requirement clarification

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| N/A | No mockups — this is an AI skill restructuring with no UI components |

---

### Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|--------------------|
| FEATURE-045-A | EPIC-045 | Orchestrator Core + AAA Generator + General Fallback | v1.0 | Refactor code-implementation into lightweight orchestrator with AAA scenario generation, semantic routing, multi-tool coordination, failure handling, and general fallback tool skill | None |
| FEATURE-045-B | EPIC-045 | Python Implementation Tool Skill | v1.0 | Create x-ipe-tool-implementation-python — PEP 8, type hints, pytest, Flask/FastAPI/Django/CLI support | FEATURE-045-A |
| FEATURE-045-C | EPIC-045 | HTML5 Implementation Tool Skill | v1.0 | Create x-ipe-tool-implementation-html5 — semantic HTML, CSS3, accessibility, responsive design, vanilla JS and frameworks | FEATURE-045-A |
| FEATURE-045-D | EPIC-045 | TypeScript Implementation Tool Skill | v1.0 | Create x-ipe-tool-implementation-typescript — strict mode, interface-first, React/Vue/Angular/Node.js, vitest/jest | FEATURE-045-A |
| FEATURE-045-E | EPIC-045 | Java & MCP Implementation Tool Skills | v1.0 | Create x-ipe-tool-implementation-java (Spring Boot, JUnit 5, SOLID) and x-ipe-tool-implementation-mcp (protocol compliance, tool schemas) | FEATURE-045-A |
| FEATURE-045-F | EPIC-045 | Test Generation Deprecation Migration | v1.0 | 3-phase deprecation of x-ipe-tool-test-generation: coexistence → adapter → removal | FEATURE-045-A |

---

### Feature Details

#### FEATURE-045-A: Orchestrator Core + AAA Generator + General Fallback (MVP)

**Minimum Runnable Feature** — This is the foundation that all other features depend on.

**Scope:**
- Refactor `.github/skills/x-ipe-task-based-code-implementation/SKILL.md` from monolithic implementation to lightweight orchestrator
- Remove inline code implementation logic
- Add AAA (Arrange/Act/Assert) test scenario generation step: spec + technical design → tagged YAML-like scenarios
- Add AI semantic tool routing: scan `.github/skills/x-ipe-tool-implementation-*/` and match `tech_stack` entries
- Add multi-tool sequential coordination: invoke tool skills one at a time, collect results
- Add failure handling: single-skill retry, partial multi-tool recovery, "new tool skill needed" signal
- Create `.github/skills/x-ipe-tool-implementation-general/SKILL.md` as fallback for unmapped stacks
- Preserve backward compatibility: `x-ipe-meta-skill-creator` delegation, workflow integration, existing input/output interfaces

**Relevant HLRs:** HLR-045.1, HLR-045.2, HLR-045.4 (for general), HLR-045.5, HLR-045.6, HLR-045.7, HLR-045.8, HLR-045.10

**Relevant FRs:** FR-045.1.1–6, FR-045.2.1–6, FR-045.3.1–6 (for general), FR-045.5.1–4

**Relevant NFRs:** NFR-045.1 (extensibility), NFR-045.2 (performance), NFR-045.3 (context efficiency)

---

#### FEATURE-045-B: Python Implementation Tool Skill

**Scope:**
- Create `.github/skills/x-ipe-tool-implementation-python/SKILL.md`
- Accept AAA scenarios + source code path from orchestrator
- Learn existing Python code structure before implementing
- Implement code following Python best practices: PEP 8, type hints, docstrings
- Write pytest tests that map to AAA scenarios
- Run tests and return pass/fail results per Assert clause
- Handle linting (ruff/flake8) and formatting (black/ruff format)
- Support Flask, FastAPI, Django, CLI applications, and general libraries

**Relevant HLRs:** HLR-045.3 (python), HLR-045.4

**Relevant FRs:** FR-045.3.1–6, FR-045.4.1

---

#### FEATURE-045-C: HTML5 Implementation Tool Skill

**Scope:**
- Create `.github/skills/x-ipe-tool-implementation-html5/SKILL.md`
- Accept AAA scenarios + source code path from orchestrator
- Learn existing web project structure before implementing
- Implement code following web best practices: semantic HTML5, CSS3, ES6+
- Enforce accessibility (ARIA, keyboard navigation), responsive design
- Write browser-compatible tests that map to AAA scenarios
- Handle linting (ESLint) and formatting (Prettier)
- Support vanilla JS, lightweight frameworks, and progressive enhancement

**Relevant HLRs:** HLR-045.3 (html5), HLR-045.4

**Relevant FRs:** FR-045.3.1–6, FR-045.4.2

---

#### FEATURE-045-D: TypeScript Implementation Tool Skill

**Scope:**
- Create `.github/skills/x-ipe-tool-implementation-typescript/SKILL.md`
- Accept AAA scenarios + source code path from orchestrator
- Learn existing TypeScript project structure (tsconfig, package.json) before implementing
- Implement code following TypeScript best practices: strict mode, interface-first design
- Write vitest/jest tests that map to AAA scenarios
- Handle linting (ESLint + typescript-eslint) and formatting (Prettier)
- Support React, Vue, Angular, Node.js backend, and full-stack applications

**Relevant HLRs:** HLR-045.3 (typescript), HLR-045.4

**Relevant FRs:** FR-045.3.1–6, FR-045.4.3

---

#### FEATURE-045-E: Java & MCP Implementation Tool Skills

**Scope:**
This feature creates two tool skills that share a common dependency on FEATURE-045-A:

**x-ipe-tool-implementation-java:**
- Create `.github/skills/x-ipe-tool-implementation-java/SKILL.md`
- Accept AAA scenarios + source code path from orchestrator
- Learn existing Java project structure (pom.xml/build.gradle, package layout) before implementing
- Implement code following Java best practices: clean architecture, SOLID principles
- Write JUnit 5 tests that map to AAA scenarios
- Handle linting (Checkstyle) and formatting (Google Java Format)
- Support Spring Boot, Maven, Gradle projects

**x-ipe-tool-implementation-mcp:**
- Create `.github/skills/x-ipe-tool-implementation-mcp/SKILL.md` (adapted from existing `mcp-builder` skill)
- Accept AAA scenarios + source code path from orchestrator
- Implement MCP server code following protocol compliance: tool schemas, resource definitions, transport types
- Write protocol-level tests that map to AAA scenarios
- Support Python (FastMCP) and TypeScript (MCP SDK) MCP implementations

**Relevant HLRs:** HLR-045.3 (java, mcp), HLR-045.4

**Relevant FRs:** FR-045.3.1–6, FR-045.4.4, FR-045.4.5

---

#### FEATURE-045-F: Test Generation Deprecation Migration

**Scope:**
- **Phase 1 (Coexistence):** Orchestrator generates AAA scenarios AND invokes `x-ipe-tool-test-generation` as fallback if AAA generation fails
- **Phase 2 (Adapter):** Refactor `x-ipe-tool-test-generation` to consume AAA scenarios as input instead of generating from scratch
- **Phase 3 (Removal):** Remove `x-ipe-tool-test-generation`; update all references in skills, workflows, and documentation
- Each phase is a version increment (v1.0 → v1.1 → v2.0)
- Phase transitions triggered by confidence threshold: ≥95% AAA success rate over 10+ features

**Relevant HLRs:** HLR-045.9

**Relevant FRs:** (New FRs to be defined during refinement)

**Note:** Phase 1 is part of the initial rollout (implemented alongside FEATURE-045-A). Phases 2 and 3 are deferred to future iterations.
