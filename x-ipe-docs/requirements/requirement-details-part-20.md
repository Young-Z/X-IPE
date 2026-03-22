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

---

## EPIC-049: Knowledge Base — Integrated Project Knowledge Management

> **Supersedes:** EPIC-025 (Knowledge Base Infrastructure). EPIC-025 is retired — all KB requirements are consolidated here with enhanced scope.

### Project Overview

A project-scoped Knowledge Base (KB) integrated into X-IPE that serves as persistent organizational memory — storing requirement documents, user manuals, design references, market research, and technical patterns. Both humans and AI agents can read from and write to the KB across all workflow phases. Supports legacy application maintenance and knowledge-intensive development alongside X-IPE's existing greenfield workflow.

**Source:** Idea IDEA-036, workflow `wf-007-knowledge-base-implementation`, refined through 13+ rounds of mockup iteration.

### User Request

> "We need a knowledge base in X-IPE to support legacy applications (existing docs, manuals, architecture diagrams) and capture reusable knowledge (market research, design references, technical patterns). It should work like OneDrive/Google Drive with user-defined folders, have predefined 2D tags (lifecycle × domain), support AI-assisted upload via an AI Librarian, and integrate into all workflow phases via a Reference Picker."

### Clarifications

| Question | Answer |
|----------|--------|
| KB scope per project vs per workflow? | **Shared** — one KB per project under `x-ipe-docs/knowledge-base/`, all workflows access the same KB |
| Folder structure predefined or user-defined? | **User-defined** — free-form like OneDrive/Google Drive. No predefined categories. Users create/manage folders freely |
| Tags predefined or user-defined? | **Predefined** — 2D taxonomy in `knowledgebase-config.json`: lifecycle tags (SDLC phases) × domain tags (project topics) |
| Markdown editor type? | **Simple code-editor** with markdown preview panel (reuse EPIC-037 Compose Idea Modal pattern with EasyMDE) |
| Agent auto-write behavior? | Agents wire to **AI Librarian skill** (`x-ipe-tool-kb-librarian`) which auto-handles placement and tagging. No direct KB writes |
| Search implementation? | **Simple first** — filename + frontmatter/tags. Full-text content search deferred to V2 |
| URL bookmarks auto-fetch? | **No** — store URL + optional user notes in `.url.md` file only. No webpage snapshots |
| Relationship to EPIC-025? | **EPIC-049 replaces EPIC-025** — consolidated with enhanced scope (2D tags, AI Librarian, reference picker, markdown editor) |
| Reuse existing modal patterns? | **Yes** — reuse EPIC-037 (Compose Idea Modal) for KB editor + EPIC-039 (Folder Browser Modal) for reference picker |
| Archive uploads (.zip/.7z)? | **Supported** — auto-extract preserving folder structure, skip nested archives within uploaded folders |
| Browse view scalability? | **Dual-mode** — Grid view (cards, editorial, ≤30 files) ↔ List view (sortable table, practical at 50+ files) |
| Lifecycle vs domain tag display? | **Visually differentiated** — lifecycle: amber gradient pill with `▸` prefix; domain: blue outlined pill with `#` prefix |

### High-Level Requirements

#### HR-049.1: KB Storage & Folder Structure
1. KB files stored under `x-ipe-docs/knowledge-base/` within the project repository
2. Folder structure is entirely user-defined (create, rename, move, delete folders)
3. `knowledgebase-config.json` at KB root stores configuration: predefined tags, AI Librarian settings, agent write allowlist
4. Supported file types: Markdown (`.md`, first-class with in-app editing), PDF, images (`.png`, `.jpg`, `.svg`), URL bookmarks (`.url.md`)
5. Maximum file size: 10MB per file
6. YAML frontmatter on all `.md` articles: title, tags (lifecycle + domain), author, created date, auto-generated flag

#### HR-049.2: KB Sidebar & Navigation
1. New "Knowledge Base" section in sidebar (between Ideas and Workflows)
2. Collapsible folder tree mirroring file system structure
3. Folder expand/collapse with click; file click opens article in content area
4. "📥 Intake" entry in sidebar for AI Librarian staging area
5. Drag-and-drop files onto sidebar folders for quick move/upload
6. Visual folder highlight (emerald dashed border) on drag-over

#### HR-049.3: KB Browsing & Search
1. **Grid view**: Card-based layout with title, snippet, tags, date — suitable for ≤30 files
2. **List view**: Sortable table with columns: Name, Tags, Modified, Size — suitable for 50+ files
3. View toggle (grid ↔ list) persisted per session
4. **Sort options**: Last Modified (default), Name A→Z, Date Created, Untagged First
5. **Search**: Keyword search matching filename + frontmatter fields (title, tags, author)
6. **Tag filter chips**: 2D taxonomy — lifecycle tags (amber, `▸` prefix) + domain tags (blue, `#` prefix)
7. "⚠ Untagged" quick-filter chip to surface files needing tags
8. "Needs Tags" amber badge on untagged files in both views

#### HR-049.4: KB Article Editor
1. Create new article via "New Article" button → modal editor
2. Reuse EPIC-037 Compose Idea Modal pattern (EasyMDE markdown editor with toolbar)
3. Split-pane or toggle between edit and preview modes
4. YAML frontmatter auto-populated with defaults (author, date); user edits tags and title
5. Save writes `.md` file to selected folder with frontmatter
6. Edit existing articles in-place (same modal, pre-populated)

#### HR-049.5: KB Upload — Normal Mode
1. Drag-and-drop or click-to-browse file upload zone
2. **Folder path selector**: Breadcrumb-style picker above drop zone showing destination path (e.g., `/ research / competitors`)
3. Dropdown folder tree for selecting destination folder
4. "Create new folder" button beside breadcrumb
5. Archive support: `.zip` and `.7z` files auto-extracted preserving internal folder structure
6. Nested archives within uploaded folders are skipped (not recursively extracted)
7. Drag-drop directly onto sidebar folder entries for immediate upload to that folder

#### HR-049.6: KB Upload — AI Librarian Mode
1. Upload mode toggle: "Normal" (direct to folder) ↔ "AI Librarian" (via Intake staging)
2. AI Librarian mode uploads files to `x-ipe-docs/knowledge-base/.intake/` staging folder
3. "📥 Intake" section shows staged files with status: Pending, Processing, Filed
4. Status filter pills: All / Pending / Processing / Filed
5. Per-file actions: Preview, Assign folder manually, Remove
6. "✨ Run AI Librarian" button triggers agent CLI session via `x-ipe-tool-kb-librarian` skill
7. AI Librarian auto-handles: move files to appropriate folders, assign tags, generate frontmatter
8. After processing, files move from Intake to their destination folders with status "Filed"
9. Intake file table columns: Name, Size, Upload Date, Status, Destination, Actions

#### HR-049.7: Reference Picker Modal
1. Cross-workflow modal invoked from any workflow phase (e.g., during ideation, technical design)
2. Reuse EPIC-039 Folder Browser Modal pattern (two-panel: tree left, preview right)
3. Browse KB folder tree on left panel, file preview on right panel
4. Select files AND/OR folders for referencing
5. Search within modal matching filename + tags
6. Tag filter chips within modal (same 2D taxonomy)
7. **"📋 Copy" button**: Copy selected references to clipboard (for manual pasting)
8. **"Insert" button**: Insert references into current workflow context
9. Multi-select support for batch referencing

#### HR-049.8: 2D Tag Taxonomy
1. Tags defined in `knowledgebase-config.json` under `tags.lifecycle` and `tags.domain`
2. **Lifecycle tags** (vertical — SDLC phases): Ideation, Requirement, Design, Implementation, Testing, Deployment, Maintenance
3. **Domain tags** (horizontal — project topics): API, Authentication, UI/UX, Database, Infrastructure, Security, Performance, Integration, Documentation, Analytics
4. Visual differentiation: lifecycle = amber gradient pill with `▸` prefix + left border accent; domain = blue outlined pill with `#` prefix + border-only style
5. Tags are filterable in browse view and reference picker
6. Articles can have multiple lifecycle + domain tags

#### HR-049.9: Agent Integration
1. Agents access KB via `x-ipe-tool-kb-librarian` skill (tool-type, agent-invoked)
2. Agent write access controlled by `agent_write_allowlist` in `knowledgebase-config.json`
3. Agent-generated articles tagged with `[auto-generated]` flag in frontmatter
4. Workflow integration: `kb-articles` key in action context for referencing KB articles during workflow execution
5. AI Librarian skill handles: file organization, tag assignment, frontmatter generation, folder placement

#### HR-049.10: URL Bookmarks
1. URL bookmarks stored as `.url.md` files with standard frontmatter
2. Frontmatter includes: `url` field, title, tags, optional notes
3. URL bookmarks displayed with link icon (🔗) and "Open URL" action
4. No auto-fetching or webpage snapshot — URL + user notes only

### Non-Functional Requirements

- NFR-049.1: KB operations must be file-system based (git-compatible, no database dependency)
- NFR-049.2: Sidebar folder tree must load within 500ms for up to 500 files
- NFR-049.3: Search results must return within 300ms for filename + frontmatter matching
- NFR-049.4: All KB UI must follow existing X-IPE design system (base.css variables, modal patterns, sidebar styles)
- NFR-049.5: Archive extraction must handle up to 100MB compressed files
- NFR-049.6: Intake staging area must be excluded from regular KB browsing (`.intake/` folder convention)

### Constraints

- File-based storage only — no database, no external search index
- Project-scoped — no cross-project KB sharing in V1
- 10MB max per individual file
- Tags are predefined in `knowledgebase-config.json` — no ad-hoc tag creation from UI in V1
- Full-text content search deferred to V2
- Agent writes MUST go through AI Librarian skill — no direct file writes

### Out of Scope

- Cross-project KB federation or shared libraries
- Full-text content search (V2)
- WYSIWYG markdown editor (using simple code-editor with preview)
- Auto-fetch webpage snapshots for URL bookmarks
- Real-time collaborative editing
- KB versioning / article history (git provides this implicitly)
- KB permissions / role-based access (all project members have full access)

### Open Questions

- None — all questions resolved during ideation (13+ rounds) and requirement clarification

### Dependencies

| EPIC | Dependency Type | Description |
|------|----------------|-------------|
| EPIC-037 | Reuse | Compose Idea Modal pattern for KB Article Editor |
| EPIC-039 | Reuse | Folder Browser Modal pattern for Reference Picker |
| EPIC-043 | Integrate | File Link Preview for internal KB article links |

### Supersedes

| EPIC | Reason |
|------|--------|
| EPIC-025 | KB Infrastructure — fully replaced by EPIC-049 with enhanced scope (2D tags, AI Librarian, reference picker, markdown editor, dual-mode upload) |

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| KB Browse Articles (Grid/List) | [kb-interface-v1.html — Scene 1](EPIC-049/mockups/kb-interface-v1.html) |
| KB Article Detail | [kb-interface-v1.html — Scene 2](EPIC-049/mockups/kb-interface-v1.html) |
| KB Reference Picker Modal | [kb-interface-v1.html — Scene 3](EPIC-049/mockups/kb-interface-v1.html) |
| KB Intake — AI Librarian | [kb-interface-v1.html — Scene 4](EPIC-049/mockups/kb-interface-v1.html) |

---

## Feature List — EPIC-049

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-049-A | EPIC-049 | KB Backend & Storage Foundation | v1.0 | Backend APIs for file/folder CRUD, knowledgebase-config.json, YAML frontmatter parsing, 2D tag taxonomy model, URL bookmark format | None |
| FEATURE-049-B | EPIC-049 | KB Sidebar & Navigation | v1.0 | New sidebar section with collapsible folder tree, expand/collapse, drag-drop folder highlight | FEATURE-049-A |
| FEATURE-049-C | EPIC-049 | KB Browse & Search | v1.0 | Grid view with cards, sort dropdown, keyword search (filename+tags), 2D tag filter chips, untagged badge | FEATURE-049-A, FEATURE-049-B |
| FEATURE-049-D | EPIC-049 | KB Article Editor | v1.0 | Create/edit markdown articles via modal (reuse EPIC-037 pattern), EasyMDE editor, frontmatter editing | FEATURE-049-A |
| FEATURE-049-E | EPIC-049 | KB File Upload | v1.0 | Normal mode upload zone, folder path selector breadcrumb, .zip/.7z archive extraction, sidebar drag-drop upload | FEATURE-049-A, FEATURE-049-B |
| FEATURE-049-F | EPIC-049 | KB AI Librarian & Intake | v1.0 | Upload mode toggle, intake staging area, AI Librarian skill integration, agent write access, workflow kb-articles key | FEATURE-049-A, FEATURE-049-E |
| FEATURE-049-G | EPIC-049 | KB Reference Picker | v1.0 | Cross-workflow modal (reuse EPIC-039 pattern), file+folder selection, copy to clipboard, insert reference, multi-select | FEATURE-049-A, FEATURE-049-C |

> **MVP Scope:** Features A, B, C, D, E, G — **Post-MVP:** Feature F (AI Librarian & Intake)
> **Note:** Feature C ships with grid view only for MVP; list view added as enhancement post-MVP.

---

## Feature Details — EPIC-049

### FEATURE-049-A: KB Backend & Storage Foundation

**Version:** v1.0
**Brief Description:** Core backend service providing file-based KB storage, folder management, configuration, and metadata handling.

**Acceptance Criteria:**
- [ ] KB root folder `x-ipe-docs/knowledge-base/` created on project init (or first KB access)
- [ ] `knowledgebase-config.json` schema supports: `tags.lifecycle[]`, `tags.domain[]`, `agent_write_allowlist[]`, `ai_librarian` settings
- [ ] Backend API: list folders, create folder, rename folder, delete folder (with contents confirmation)
- [ ] Backend API: list files in folder (with frontmatter metadata), get file content, create file, update file, delete file
- [ ] Backend API: move file/folder to new parent folder
- [ ] YAML frontmatter parsing for `.md` files: title, tags (lifecycle + domain), author, created, auto_generated
- [ ] URL bookmark format: `.url.md` files with `url`, `title`, `tags`, `notes` frontmatter fields
- [ ] File type validation: `.md`, `.pdf`, `.png`, `.jpg`, `.svg`, `.url.md` accepted; 10MB max per file
- [ ] 2D tag taxonomy model: lifecycle tags (7 SDLC phases) × domain tags (10 topics) from knowledgebase-config.json
- [ ] API endpoint to read/update knowledgebase-config.json tag definitions

**Dependencies:**
- None (foundation feature)

**Technical Considerations:**
- File-based storage only — no database, git-compatible
- Reuse existing X-IPE file service patterns (see `src/x_ipe/services/`)
- Frontmatter parsing via Python `yaml` module (already a project dependency)
- All paths relative to project root

---

### FEATURE-049-B: KB Sidebar & Navigation

**Version:** v1.0
**Brief Description:** New "Knowledge Base" sidebar section with interactive folder tree and drag-drop support.

**Acceptance Criteria:**
- [ ] New "Knowledge Base" section appears in sidebar between Ideas and Workflows
- [ ] Folder tree mirrors `x-ipe-docs/knowledge-base/` file system structure
- [ ] Folders expand/collapse on click; files open in content area on click
- [ ] Folder tree auto-refreshes after file/folder operations (create, move, delete, upload)
- [ ] Drag-over on sidebar folders shows emerald dashed border + "DROP HERE" visual
- [ ] Drop event on sidebar folder triggers file move/upload to that folder
- [ ] "📥 Intake" entry visible in sidebar (navigates to Intake view when Feature F is implemented; placeholder until then)

**Dependencies:**
- FEATURE-049-A: Needs folder/file listing APIs

**Technical Considerations:**
- Follow existing sidebar patterns (`sidebar.css`, `.nav-section-header` style)
- HTML5 drag events: dragover, dragleave, drop
- Sidebar tree should load within 500ms for up to 500 files (NFR-049.2)

---

### FEATURE-049-C: KB Browse & Search

**Version:** v1.0
**Brief Description:** Main content area for browsing KB articles with grid view, search, sort, and tag filtering.

**Acceptance Criteria:**
- [ ] Grid view: card-based layout showing title, snippet (first 100 chars), tags, last modified date
- [ ] Tag display: lifecycle tags as amber gradient pill with `▸` prefix; domain tags as blue outlined pill with `#` prefix
- [ ] Sort dropdown with options: Last Modified (default), Name A→Z, Date Created, Untagged First
- [ ] Keyword search bar matching filename + frontmatter fields (title, tags, author)
- [ ] Search results update as user types (debounced 300ms)
- [ ] 2D tag filter chips below search bar — click to toggle filter; active chip highlighted
- [ ] "⚠ Untagged" quick-filter chip surfaces files missing tags
- [ ] "Needs Tags" amber badge displayed on untagged file cards
- [ ] Click on article card navigates to article detail view (Scene 2 from mockup)
- [ ] URL bookmark cards display 🔗 icon and "Open URL" action

**Dependencies:**
- FEATURE-049-A: Needs file listing + frontmatter APIs
- FEATURE-049-B: Needs sidebar for folder-scoped browsing

**Technical Considerations:**
- Search within 300ms for filename+frontmatter matching (NFR-049.3)
- Grid view only for MVP; list view (sortable table) deferred to post-MVP enhancement
- Follow X-IPE design system (base.css variables, card patterns)

---

### FEATURE-049-D: KB Article Editor

**Version:** v1.0
**Brief Description:** Modal-based markdown editor for creating and editing KB articles, reusing EPIC-037 Compose Idea Modal pattern.

**Acceptance Criteria:**
- [ ] "New Article" button in browse view opens editor modal
- [ ] Editor modal reuses EPIC-037 Compose Idea Modal shell (90vw×90vh, backdrop blur, spring animation)
- [ ] EasyMDE markdown editor with toolbar (Bold, Italic, Heading, Lists, Link, Image, Code)
- [ ] Split-pane or toggle between edit and preview modes
- [ ] Frontmatter form fields above editor: Title (text), Lifecycle tags (multi-select from kb-config), Domain tags (multi-select from kb-config)
- [ ] Author and created date auto-populated; auto_generated defaults to false for human-created articles
- [ ] Save button writes `.md` file with YAML frontmatter to selected folder
- [ ] Edit existing article: same modal pre-populated with current content and frontmatter
- [ ] Cancel/close discards unsaved changes (with confirmation if content modified)

**Dependencies:**
- FEATURE-049-A: Needs file create/update APIs and tag definitions

**Technical Considerations:**
- EasyMDE already used in EPIC-037 — reuse same library instance
- Modal pattern from `compose-idea-modal.css` (border-radius 12px, z-index 1051, overlay blur)
- Frontmatter serialized via JS before save; parsed via Python on backend

---

### FEATURE-049-E: KB File Upload

**Version:** v1.0
**Brief Description:** Normal mode file upload with folder destination picker, archive extraction, and sidebar drag-drop.

**Acceptance Criteria:**
- [ ] Upload zone: drag-and-drop area + click-to-browse file picker
- [ ] Folder path selector: breadcrumb-style picker above drop zone (e.g., `/ research / competitors`)
- [ ] Dropdown folder tree for selecting destination folder with indented sub-folders
- [ ] "Create new folder" button beside breadcrumb — inline folder name input
- [ ] Multi-file upload support with progress indicators
- [ ] Archive support: `.zip` files auto-extracted preserving internal folder structure
- [ ] Archive support: `.7z` files auto-extracted preserving internal folder structure
- [ ] Nested archives within uploaded folder contents are skipped (not recursively extracted)
- [ ] File type validation: reject unsupported types with error message
- [ ] File size validation: reject files >10MB with error message
- [ ] Sidebar drag-drop: drop files onto any sidebar folder to upload directly to that folder
- [ ] Upload zone hint text dynamically shows selected destination path

**Dependencies:**
- FEATURE-049-A: Needs file create API and folder structure
- FEATURE-049-B: Needs sidebar folder tree for drag-drop target

**Technical Considerations:**
- Archive extraction: Python `zipfile` (stdlib) for .zip; `py7zr` library for .7z
- Handle up to 100MB compressed files (NFR-049.5)
- Preserve folder structure within archives when extracting
- HTML5 File API + FormData for upload

---

### FEATURE-049-F: KB AI Librarian & Intake

**Version:** v1.0 (Post-MVP)
**Brief Description:** AI-assisted upload mode with intake staging area, file processing status tracking, and AI Librarian skill integration.

**Acceptance Criteria:**
- [ ] Upload mode toggle bar: "Normal" (direct) ↔ "AI Librarian" (via Intake)
- [ ] AI Librarian mode uploads to `x-ipe-docs/knowledge-base/.intake/` staging folder
- [ ] Intake view: file table with columns — Name, Size, Upload Date, Status, Destination, Actions
- [ ] Status badges: Pending (default), Processing (during AI run), Filed (after placement)
- [ ] Status filter pills: All / Pending / Processing / Filed
- [ ] Per-file actions: Preview, Assign folder manually, Remove
- [ ] "✨ Run AI Librarian" button triggers CLI agent session via `x-ipe-tool-kb-librarian` skill
- [ ] AI Librarian auto-handles: move files to folders, assign lifecycle+domain tags, generate frontmatter
- [ ] Filed files disappear from Intake and appear in destination folders
- [ ] Agent write access controlled by `agent_write_allowlist` in knowledgebase-config.json
- [ ] Agent-generated articles tagged with `auto_generated: true` in frontmatter
- [ ] Workflow context integration: `kb-articles` key in action context for referencing KB articles
- [ ] `x-ipe-tool-kb-librarian` skill created (tool-type, agent-invoked)

**Dependencies:**
- FEATURE-049-A: Needs storage APIs and config
- FEATURE-049-E: Needs upload infrastructure

**Technical Considerations:**
- `.intake/` folder excluded from regular KB browsing (NFR-049.6)
- AI Librarian skill is tool-type (not task-based) — invoked by agent during CLI session
- Requires new skill file: `.github/skills/x-ipe-tool-kb-librarian/SKILL.md`

---

### FEATURE-049-G: KB Reference Picker

**Version:** v1.0
**Brief Description:** Cross-workflow modal for selecting and referencing KB articles/folders, reusing EPIC-039 Folder Browser Modal pattern.

**Acceptance Criteria:**
- [ ] Reference Picker modal invocable from any workflow phase (ideation, design, implementation, etc.)
- [ ] Modal reuses EPIC-039 Folder Browser Modal shell (80vw, two-panel layout)
- [ ] Left panel: KB folder tree browser with expand/collapse
- [ ] Right panel: file preview (markdown rendered, images displayed, PDF placeholder)
- [ ] Select individual files AND/OR entire folders for referencing
- [ ] Search bar within modal matching filename + tags
- [ ] 2D tag filter chips within modal (lifecycle amber + domain blue)
- [ ] "📋 Copy" button: copies selected reference paths to clipboard
- [ ] "Insert" button: inserts references into current workflow action context
- [ ] Multi-select support: checkbox per file/folder, batch copy/insert
- [ ] "✅ Copied!" animation feedback on clipboard copy

**Dependencies:**
- FEATURE-049-A: Needs file/folder listing APIs
- FEATURE-049-C: Needs search and tag filter logic

**Technical Considerations:**
- Reuse EPIC-039 Folder Browser Modal component with KB-specific configuration
- Clipboard API (`navigator.clipboard.writeText`) for copy function
- Reference format: project-root-relative paths (e.g., `x-ipe-docs/knowledge-base/research/competitor-analysis.md`)
