# Feature Specification: Application Reverse Engineering Tool Skill

> Feature ID: FEATURE-053-A
> Epic: EPIC-053
> Version: v1.0
> Status: Refined
> Last Updated: 03-31-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-31-2026 | Initial specification |

## Linked Mockups

N/A — This feature creates a tool skill (templates and references), not a UI component.

## Overview

This feature creates `x-ipe-tool-knowledge-extraction-application-reverse-engineering`, a tool skill that enables the Application Knowledge Extractor to reverse-engineer source code repositories. The skill provides an 8-section phased playbook, collection templates with source-code-specific extraction prompts, validation criteria, a two-dimension mixin system (4 repo-type × 5 language-type), accuracy-focused quality scoring, a verification walkthrough, and source code tests as a Phase 2 knowledge source.

The skill mirrors the structural pattern of `x-ipe-tool-knowledge-extraction-user-manual` — implementing the same 7-operation contract (get_artifacts, get_collection_template, validate_section, get_mixin, pack_section, score_quality, test_walkthrough) — but replaces user-manual-oriented content with reverse engineering analysis. It is discovered by the extractor via `categories: ["application-reverse-engineering"]` in its frontmatter.

Target users are developers inheriting codebases, tech leads onboarding to new projects, migration/modernization teams, and documentation teams needing to produce architecture docs from undocumented code.

## User Stories

- As a **developer inheriting a codebase**, I want the extractor to reverse-engineer the codebase's architecture, so that I can understand its structure without reading every file.
- As a **tech lead onboarding to a new project**, I want dependency maps and design pattern inventories extracted automatically, so that I can assess technical debt and make informed decisions.
- As a **migration team member**, I want comprehensive API contract extraction and data flow analysis, so that I can plan the migration without missing integration points.
- As a **knowledge extractor agent**, I want a tool skill that provides reverse engineering templates and validation, so that I can systematically extract architectural knowledge from any codebase.
- As a **knowledge extractor agent**, I want auto-detected mixins for different repo types and languages, so that my extraction prompts are tailored to the specific codebase.

## Acceptance Criteria

### AC-053-01: Skill Structure & Discovery

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-01a | GIVEN the skill directory `.github/skills/x-ipe-tool-knowledge-extraction-application-reverse-engineering/` WHEN the extractor globs `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md` THEN this skill's SKILL.md is discovered | Unit |
| AC-053-01b | GIVEN the skill's SKILL.md frontmatter WHEN the extractor reads `categories` THEN it contains `["application-reverse-engineering"]` | Unit |
| AC-053-01c | GIVEN the skill WHEN its SKILL.md is loaded THEN it declares all 7 operations: get_artifacts, get_collection_template, validate_section, get_mixin, pack_section, score_quality, test_walkthrough | Unit |
| AC-053-01d | GIVEN the skill directory WHEN listing template files THEN it contains: playbook-template.md, collection-template.md, acceptance-criteria.md, and 9 mixin files (4 repo-type + 5 language-type) | Unit |

### AC-053-02: get_artifacts Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-02a | GIVEN the extractor calls get_artifacts WHEN the operation executes THEN it returns paths to playbook-template.md, collection-template.md, and acceptance-criteria.md relative to skill root | Unit |
| AC-053-02b | GIVEN the extractor calls get_artifacts WHEN the operation executes THEN it returns a mixin map with repo_type_mixins (monorepo, multi-module, single-module, microservices) and language_type_mixins (python, java, javascript, typescript, go) | Unit |
| AC-053-02c | GIVEN the extractor calls get_artifacts WHEN the operation returns artifact paths THEN all referenced template files exist at the declared paths | Unit |

### AC-053-03: Playbook Template (8 Sections, Phased)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-03a | GIVEN the playbook template WHEN it is parsed THEN it defines exactly 8 sections: (1) Architecture Recovery, (2) Design Pattern Detection, (3) API Contract Extraction, (4) Dependency Analysis, (5) Code Structure Analysis, (6) Data Flow / Protocol Analysis, (7) Technology Stack Identification, (8) Source Code Tests | Unit |
| AC-053-03b | GIVEN the playbook template WHEN extraction phases are evaluated THEN sections are assigned to 3 phases: Phase 1 Scan (sections 5, 7), Phase 2 Tests (section 8), Phase 3 Deep (sections 1, 2, 3, 4, 6) | Unit |
| AC-053-03c | GIVEN the playbook template WHEN Phase 1 sections are read THEN sections 5 (Code Structure) and 7 (Tech Stack) specify inline output format with Markdown tables | Unit |
| AC-053-03d | GIVEN the playbook template WHEN Phase 2 section is read THEN section 8 (Source Code Tests) specifies subfolder output with executable test files | Unit |
| AC-053-03e | GIVEN the playbook template WHEN Phase 3 sections are read THEN sections 1, 2, 3, 4, 6 specify subfolder output with appropriate visualization tools (Architecture DSL and/or Mermaid) | Unit |
| AC-053-03f | GIVEN the playbook template WHEN each section's subsections are listed THEN each section defines: description, required subsections, output type (inline/subfolder), and visualization tool | Unit |

### AC-053-04: Collection Template (Extraction Prompts)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-04a | GIVEN the collection template WHEN it is parsed THEN it contains extraction prompts for all 8 playbook sections | Unit |
| AC-053-04b | GIVEN the collection template section for Architecture Recovery WHEN extraction prompts are read THEN they guide multi-level analysis: conceptual (landscape), logical (module), physical (class), data flow (sequence) | Unit |
| AC-053-04c | GIVEN the collection template section for Design Pattern Detection WHEN extraction prompts are read THEN they include source priority instructions, pattern catalog references, and confidence-level guidance (high/medium/low with file:line evidence) | Unit |
| AC-053-04d | GIVEN the collection template section for Source Code Tests WHEN extraction prompts are read THEN they guide: scan for existing tests, detect test framework, collect/generate AAA-structured tests, run tests, measure coverage | Unit |
| AC-053-04e | GIVEN the collection template WHEN any section's prompts are read THEN each prompt specifies source priority (which files/patterns to look at first) | Unit |

### AC-053-05: Acceptance Criteria Template (Validation Rules)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-05a | GIVEN the acceptance criteria template WHEN it is parsed THEN it provides validation rules for all 8 sections with `[REQ]` and `[OPT]` markers | Unit |
| AC-053-05b | GIVEN the acceptance criteria for Architecture Recovery WHEN validated THEN required rules include: module diagram present, at least 2 architecture levels documented, Architecture DSL used for conceptual/logical levels | Unit |
| AC-053-05c | GIVEN the acceptance criteria for Source Code Tests WHEN validated THEN required rules include: all tests follow AAA structure, all tests pass, coverage ≥ 80%, test framework matches project | Unit |
| AC-053-05d | GIVEN the acceptance criteria for Design Pattern Detection WHEN validated THEN required rules include: each pattern has confidence level, each pattern has file:line evidence citation, pattern inventory table present | Unit |

### AC-053-06: get_collection_template Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-06a | GIVEN the extractor calls get_collection_template with a valid section_id WHEN the operation executes THEN it returns the extraction prompts for that section from collection-template.md | Unit |
| AC-053-06b | GIVEN the extractor calls get_collection_template with an invalid section_id WHEN the operation executes THEN it returns an error indicating the section is not found | Unit |

### AC-053-07: validate_section Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-07a | GIVEN extracted content for a section WHEN validate_section is called THEN it checks content against that section's acceptance criteria | Unit |
| AC-053-07b | GIVEN extracted content that satisfies all `[REQ]` rules for a section WHEN validate_section is called THEN it returns validation_passed: true with a list of satisfied criteria | Unit |
| AC-053-07c | GIVEN extracted content missing required criteria WHEN validate_section is called THEN it returns validation_passed: false with missing_info listing the unsatisfied `[REQ]` rules | Unit |

### AC-053-08: Mixin System (get_mixin Operation)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-08a | GIVEN a repo-type mixin key (e.g., "monorepo") WHEN get_mixin is called THEN it returns the mixin overlay from `templates/mixin-monorepo.md` with additional extraction prompts and detection signals | Unit |
| AC-053-08b | GIVEN a language-type mixin key (e.g., "python") WHEN get_mixin is called THEN it returns the mixin overlay from `templates/mixin-python.md` with language-specific extraction prompts | Unit |
| AC-053-08c | GIVEN the monorepo mixin WHEN its content is read THEN it includes detection signals (`lerna.json`, `pnpm-workspace.yaml`, `nx.json`, multiple `package.json`) AND additional prompts for cross-package dependency analysis and shared module identification | Unit |
| AC-053-08d | GIVEN the multi-module mixin WHEN its content is read THEN it includes detection signals (`pom.xml` with modules, `settings.gradle`, workspace `Cargo.toml`) AND additional prompts for module boundary analysis | Unit |
| AC-053-08e | GIVEN the single-module mixin WHEN its content is read THEN it includes detection signals (single `package.json`, single `pyproject.toml`) AND additional prompts for internal layering analysis | Unit |
| AC-053-08f | GIVEN the microservices mixin WHEN its content is read THEN it includes detection signals (`docker-compose.yml`, multiple Dockerfiles, k8s manifests) AND additional prompts for service boundary and inter-service communication analysis | Unit |
| AC-053-08g | GIVEN the python mixin WHEN its content is read THEN it includes detection signals (`*.py`, `pyproject.toml`, `requirements.txt`) AND additional prompts for module/package patterns, decorator usage, metaclass patterns | Unit |
| AC-053-08h | GIVEN the java mixin WHEN its content is read THEN it includes detection signals (`*.java`, `pom.xml`, `build.gradle`) AND additional prompts for Spring patterns, annotation-driven config, interface hierarchies | Unit |
| AC-053-08i | GIVEN the javascript mixin WHEN its content is read THEN it includes detection signals (`*.js`, `*.jsx`, `package.json`) AND additional prompts for module system (CJS/ESM), React patterns, event-driven patterns | Unit |
| AC-053-08j | GIVEN the typescript mixin WHEN its content is read THEN it includes detection signals (`*.ts`, `*.tsx`, `tsconfig.json`) AND additional prompts for type hierarchy analysis, generic patterns, decorator metadata | Unit |
| AC-053-08k | GIVEN the go mixin WHEN its content is read THEN it includes detection signals (`*.go`, `go.mod`) AND additional prompts for interface satisfaction, goroutine patterns, package layout | Unit |
| AC-053-08l | GIVEN an invalid mixin key WHEN get_mixin is called THEN it returns an error indicating the mixin is not found | Unit |
| AC-053-08m | GIVEN the mixin system documentation WHEN mixin composition is described THEN it specifies repo-type is primary (applied first) and language-type is additive overlay (merged on top) | Unit |

### AC-053-09: pack_section Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-09a | GIVEN validated section content WHEN pack_section is called THEN it formats the content according to the playbook template's output structure for that section | Unit |
| AC-053-09b | GIVEN a section with inline output type WHEN pack_section is called THEN the formatted content uses Markdown tables and inline text | Unit |
| AC-053-09c | GIVEN a section with subfolder output type WHEN pack_section is called THEN the output specifies the expected subfolder structure with _index.md and per-item files | Unit |

### AC-053-10: score_quality Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-10a | GIVEN extracted content for any section WHEN score_quality is called THEN it evaluates 6 dimensions: completeness, structure, clarity, accuracy, freshness, coverage | Unit |
| AC-053-10b | GIVEN an architectural section (Architecture Recovery, Design Pattern Detection, Data Flow) WHEN score_quality is called THEN accuracy is weighted highest at 0.35 | Unit |
| AC-053-10c | GIVEN the Source Code Tests section WHEN score_quality is called THEN coverage is weighted highest at 0.50 | Unit |
| AC-053-10d | GIVEN any other section (Code Structure, Tech Stack, API Contracts, Dependencies) WHEN score_quality is called THEN completeness is weighted highest at 0.30 | Unit |
| AC-053-10e | GIVEN score_quality returns a score WHEN the score is below the passing threshold THEN it includes improvement hints describing what is missing or weak per dimension | Unit |

### AC-053-11: test_walkthrough Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-11a | GIVEN fully extracted knowledge and a repo path WHEN test_walkthrough is called THEN it parses claims from the extracted content and categorizes them (module exists, pattern detected, API contract, dependency link, tech stack item) | Unit |
| AC-053-11b | GIVEN parsed claims WHEN verification runs THEN each claim type is verified against source code using appropriate methods (glob for modules, file:line for patterns, import trace for dependencies, config files for tech stack) | Unit |
| AC-053-11c | GIVEN parsed claims AND test knowledge from Phase 2 WHEN verification runs THEN claims are cross-checked against test-derived knowledge (assertions confirm behaviors, fixtures confirm data shapes, mocks confirm integration boundaries) | Unit |
| AC-053-11d | GIVEN all claims have been verified WHEN the walkthrough completes THEN it returns a score (claims_verified / claims_total) AND a pass/fail result (pass if score ≥ 0.8) | Unit |
| AC-053-11e | GIVEN the walkthrough score is below 0.8 WHEN the result is returned THEN it includes a list of unverified claims with reasons for failure | Unit |

### AC-053-12: Source Code Tests Knowledge Pipeline (Section 8)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-12a | GIVEN the section 8 collection template WHEN test collection begins THEN the extractor first scans the repo for existing tests before generating any new tests | Unit |
| AC-053-12b | GIVEN existing tests are found in the repo WHEN they are collected THEN they are copied preserving original filenames and test framework | Unit |
| AC-053-12c | GIVEN tests need to be generated WHEN the extractor generates them THEN all generated tests follow AAA structure (Arrange/Act/Assert) | Unit |
| AC-053-12d | GIVEN the collection template section for tests WHEN framework detection is described THEN it lists detection signals for at least: pytest, vitest, jest, JUnit, go test | Unit |
| AC-053-12e | GIVEN all tests (collected + generated) are assembled WHEN they are run THEN all tests must pass AND source code is never modified to fix failing tests | Unit |
| AC-053-12f | GIVEN all tests pass WHEN coverage is measured THEN the acceptance criteria require ≥ 80% line coverage | Unit |
| AC-053-12g | GIVEN the section 8 acceptance criteria WHEN test-to-knowledge extraction is described THEN it maps: assertions → expected behaviors, fixtures → data shapes, mocks → integration boundaries, test names → domain vocabulary, exception assertions → error handling contracts, async patterns → concurrency assumptions | Unit |
| AC-053-12h | GIVEN section 8 is complete WHEN Phase 3 sections begin extraction THEN test-derived knowledge is available as a second knowledge source alongside source code | Unit |
| AC-053-12i | GIVEN the section 8 playbook subsection WHEN output structure is defined THEN it specifies: `_index.md` (overview), `tests/` subfolder (executable files), `coverage-report.md` (per-module breakdown) | Unit |

### AC-053-13: Minimum Complexity Gate

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-13a | GIVEN the skill documentation WHEN minimum complexity thresholds are specified THEN they require: ≥ 10 source files, ≥ 500 LOC, ≥ 3 source directories | Unit |
| AC-053-13b | GIVEN a codebase below any threshold WHEN the complexity gate is evaluated THEN the skill recommends skipping full reverse engineering | Unit |

### AC-053-14: Evidence-Based Pattern Detection

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-14a | GIVEN the Design Pattern Detection collection template WHEN a pattern is detected THEN the template requires a confidence level: high 🟢 (canonical form), medium 🟡 (partial match), or low 🔴 (structural similarity) | Unit |
| AC-053-14b | GIVEN a detected pattern with high confidence WHEN it is documented THEN it must include a file:line evidence citation (e.g., `src/config.py:15`) | Unit |
| AC-053-14c | GIVEN the acceptance criteria for pattern detection WHEN patterns are validated THEN each pattern must have both a confidence level AND at least one evidence citation | Unit |

### AC-053-15: Multi-Level Architecture Output

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-15a | GIVEN the Architecture Recovery collection template WHEN extraction prompts are read THEN they guide 4-level analysis: conceptual (system landscape), logical (module/component), physical (class diagrams), data flow (sequence diagrams) | Unit |
| AC-053-15b | GIVEN conceptual and logical levels WHEN architecture output is produced THEN Architecture DSL is specified as the visualization tool | Unit |
| AC-053-15c | GIVEN physical and data flow levels WHEN architecture output is produced THEN Mermaid is specified as the visualization tool (classDiagram for physical, sequenceDiagram for data flow) | Unit |
| AC-053-15d | GIVEN the skill documentation WHEN Architecture DSL usage is described THEN it states rendering is delegated to `x-ipe-tool-architecture-dsl` — this skill produces textual knowledge only | Unit |

### AC-053-16: Extractor Category Registration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-053-16a | GIVEN the `x-ipe-task-based-application-knowledge-extractor` SKILL.md WHEN it lists supported categories THEN `application-reverse-engineering` is included as a valid category | Unit |
| AC-053-16b | GIVEN the extractor WHEN it receives `purpose: "application-reverse-engineering"` THEN it discovers this skill via the glob pattern `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md` and matches `categories: ["application-reverse-engineering"]` | Unit |
| AC-053-16c | GIVEN the extractor discovers this skill WHEN it calls get_artifacts THEN it receives valid paths and can proceed with extraction using this skill's templates | Unit |

## Functional Requirements

### FR-1: 7-Operation Contract

**Description:** The skill MUST implement all 7 operations defined by the knowledge extraction tool skill interface.

**Details:**
- Input: Operation name + operation-specific parameters (section_id, content_path, mixin_key, etc.)
- Process: Each operation reads templates/references and returns structured results
- Output: Operation-specific response (artifact paths, extraction prompts, validation results, mixin overlays, formatted output, quality scores, walkthrough results)

### FR-2: Phased Playbook Enforcement

**Description:** The playbook MUST enforce a 3-phase extraction order.

**Details:**
- Input: 8 sections assigned to 3 phases
- Process: Phase 1 (Scan: 5, 7) → Phase 2 (Tests: 8) → Phase 3 (Deep: 1, 2, 3, 4, 6). Phase 2 test knowledge feeds Phase 3.
- Output: Playbook template with phase annotations and dependency markers

### FR-3: Mixin Auto-Detection Signals

**Description:** Each mixin MUST document detection signals so the extractor can auto-select appropriate mixins.

**Details:**
- Input: Project file listing
- Process: Match detection signals (file patterns, config files) against project
- Output: Selected repo-type mixin (primary) + language-type mixin(s) (additive overlay)

### FR-4: Quality Scoring Weight Profiles

**Description:** The score_quality operation MUST apply different weight profiles based on section type.

**Details:**
- Input: Section content + section_id
- Process: Select weight profile (architecture, tests, or other), evaluate 6 dimensions
- Output: Weighted score per dimension + overall score + improvement hints

### FR-5: Source Code Tests Pipeline

**Description:** Section 8 MUST produce executable, validated tests that serve as a knowledge source.

**Details:**
- Input: Target codebase
- Process: Scan existing tests → detect framework → collect/generate AAA tests → run → measure coverage → extract knowledge
- Output: Test suite (all passing, ≥80% coverage) + test knowledge base for Phase 3

## Non-Functional Requirements

### NFR-1: Structural Consistency

- Skill file structure MUST mirror `x-ipe-tool-knowledge-extraction-user-manual`: SKILL.md + templates/ + references/
- Template naming convention MUST follow: playbook-template.md, collection-template.md, acceptance-criteria.md, mixin-{name}.md
- All mixin files stored flat under `templates/`

### NFR-2: Extractor Compatibility

- Skill MUST be discoverable by extractor's existing glob pattern without extractor code changes (only SKILL.md category list update needed)
- All operations MUST return data structures compatible with extractor's existing processing pipeline

### NFR-3: Source Code Ground Truth

- Source code being analyzed is ALWAYS the ground truth
- When tests fail, tests MUST be updated — source code MUST NEVER be modified
- Extraction claims MUST be evidence-backed with file:line citations

## UI/UX Requirements

N/A — This feature creates a tool skill (templates and references), not a UI component.

## Dependencies

### Internal Dependencies

- **`x-ipe-tool-knowledge-extraction-user-manual`**: Structural reference — new skill mirrors this skill's 7-operation contract, folder layout, and template patterns
- **`x-ipe-task-based-application-knowledge-extractor`**: Consumer — the extractor discovers and loads this skill; needs category list update to accept `application-reverse-engineering`
- **`x-ipe-tool-architecture-dsl`**: Delegation — Architecture DSL rendering is delegated to this skill for conceptual and logical architecture levels

### External Dependencies

- None — all dependencies are internal X-IPE skills

## Business Rules

- BR-1: The extractor MUST only discover this skill when `purpose: "application-reverse-engineering"` is requested — not for other purposes like `user-manual`
- BR-2: Repo-type mixin is primary (applied first); language-type mixin is additive overlay (merged on top, does not replace)
- BR-3: Codebases below minimum complexity thresholds (< 10 files, < 500 LOC, < 3 directories) should skip full reverse engineering
- BR-4: Pattern detection confidence MUST be honest — low confidence patterns are acceptable as long as they are clearly marked
- BR-5: Phase ordering MUST be enforced — Phase 2 tests cannot begin before Phase 1, Phase 3 cannot begin before Phase 2

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Codebase has no tests | Section 8 generates tests from scratch using detected framework; if no framework detected, default to project's primary language standard (pytest for Python, vitest for JS/TS, etc.) |
| Codebase uses multiple languages | Multiple language-type mixins applied additively; repo-type mixin selected based on dominant project structure |
| Test coverage below 80% after initial generation | Additional AAA tests generated for uncovered paths; iterate until ≥80% or max iterations reached |
| No design patterns detected | Pattern Detection section documents "no canonical patterns found" with structural observations; validation still passes if documented |
| Codebase has no clear architecture layers | Architecture Recovery reports flat/monolithic structure; conceptual level still produced showing system boundaries |
| Invalid mixin key requested | get_mixin returns error with list of valid mixin keys |
| Section content fails validation | validate_section returns missing_info list; extractor re-extracts with corrections |

## Out of Scope

- Binary analysis, decompilation, or disassembly — requires readable source code
- Runtime profiling or dynamic analysis — static analysis only
- PlantUML diagram generation — uses Mermaid and Architecture DSL only
- Database schema reverse engineering (separate potential skill)
- Generating deployment/infrastructure documentation
- Supporting additional mixin types beyond the 9 defined (future enhancement)
- UI for displaying extraction results (handled by KB viewer)

## Technical Considerations

- The skill is a **template and reference artifact** — it contains no executable code. All runtime behavior is driven by the extractor loading and interpreting these templates.
- The 8-section playbook covers the same scope areas as established reverse engineering methodologies (4+1 View Model, static analysis best practices).
- Mixin detection signals should be specific enough to avoid false positives (e.g., presence of `pom.xml` alone doesn't mean multi-module — must check for `<modules>` element).
- Quality scoring weight profiles should be documented as tables within SKILL.md so the extractor can parse them programmatically.
- The verification walkthrough depends on Phase 2 test knowledge being available — the extractor must pass test-derived knowledge context to this operation.

## Open Questions

None — all questions resolved during ideation (v1.1) and feature breakdown.
