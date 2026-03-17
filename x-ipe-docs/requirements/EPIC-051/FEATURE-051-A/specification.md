# Feature Specification: User Manual Tool Skill

> Feature ID: FEATURE-051-A  
> Version: v1.0  
> Status: Refined  
> Last Updated: 03-17-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-17-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| N/A — no UI component | N/A | N/A | N/A | N/A | N/A |

## Overview

The **User Manual Tool Skill** (`x-ipe-tool-knowledge-extraction-user-manual`) is a domain-expert tool skill that provides structured guidance, templates, and validation for extracting user manual documentation from applications. Unlike the extractor skill (EPIC-050) which performs hands-on extraction, this tool skill acts as an "instructor" — it defines WHAT content belongs in a user manual, HOW to validate extracted content, and HOW to structure the output.

The skill provides four categories of artifacts: (1) **Playbook template** defining the 7-section structure of a complete user manual, (2) **Collection template** with per-section extraction prompts guiding what to search for, (3) **Acceptance criteria** with per-section validation rules for the extract-validate loop, and (4) **App-type mixins** providing web/CLI/mobile-specific overlays.

This skill is **source-agnostic** — it never touches source files, URLs, or running applications. All content exchange uses file-based handoff via `.checkpoint/` folders. The Application Knowledge Extractor (EPIC-050) discovers this skill via glob pattern, loads its artifacts, and calls its operations during extraction workflow.

**Target users:** AI agents executing `x-ipe-task-based-application-knowledge-extractor` skill  
**Key benefits:** Standardized user manual structure, automated validation, source-agnostic expertise, reusable templates  
**Scope:** Single tool skill supporting user-manual category only (v1)

## User Stories

1. **As an** extractor agent **I want to** discover this tool skill via glob pattern **so that** I can load domain expertise for user-manual extraction without hardcoded dependencies

2. **As an** extractor agent **I want to** receive a playbook template with 7 canonical sections **so that** I know the target structure before I begin extracting content

3. **As an** extractor agent **I want to** receive extraction prompts per section **so that** I know exactly what to search for in source files, README, or running apps

4. **As an** extractor agent **I want to** validate extracted content against acceptance criteria **so that** I can loop until quality standards are met

5. **As an** extractor agent **I want to** request app-type mixins (web/CLI/mobile) **so that** I can augment the base template with platform-specific extraction guidance

6. **As a** tool skill maintainer **I want to** keep detailed templates in `templates/` folder **so that** SKILL.md stays under 500 lines and remains readable

## Acceptance Criteria

### AC-051-01: Skill Structure & Discovery

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-051-01a | GIVEN the extractor globs `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md` WHEN it filters by `categories: ["user-manual"]` in frontmatter THEN this skill is discovered | Unit |
| AC-051-01b | GIVEN the skill is loaded WHEN the extractor reads artifact paths from SKILL.md frontmatter THEN paths for playbook_template, collection_template, acceptance_criteria, and app_type_mixins are returned | Unit |
| AC-051-01c | GIVEN the skill folder structure follows X-IPE conventions WHEN the extractor accesses `references/` and `templates/` THEN all referenced files exist at declared paths | Unit |
| AC-051-01d | GIVEN SKILL.md is the entry point WHEN line count is measured THEN it contains ≤ 500 lines (detailed content extracted to references/templates) | Unit |

### AC-051-02: Playbook Template (Base Structure)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-051-02a | GIVEN the playbook template is loaded WHEN sections are enumerated THEN it contains exactly 7 sections: Overview, Installation & Setup, Getting Started, Core Features, Configuration, Troubleshooting, FAQ & Reference | Unit |
| AC-051-02b | GIVEN each section in the playbook WHEN content structure is inspected THEN each has a heading (H2) and a description of what content belongs in that section | Unit |
| AC-051-02c | GIVEN the playbook template is rendered WHEN read by a human or agent THEN it is valid standalone markdown with no dependencies on external files | Unit |
| AC-051-02d | GIVEN the playbook defines section order WHEN the extractor builds output THEN sections appear in the declared order: 1→Overview, 2→Installation, 3→Getting Started, 4→Core Features, 5→Configuration, 6→Troubleshooting, 7→FAQ | Unit |

### AC-051-03: Collection Template & Extraction Prompts

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-051-03a | GIVEN the collection template is loaded WHEN sections are enumerated THEN it contains the same 7 sections as the playbook template | Unit |
| AC-051-03b | GIVEN each section in the collection template WHEN extraction prompts are read THEN each section has at least one HTML comment with specific search guidance (e.g., "look for README install section, Makefile, scripts/setup.*") | Unit |
| AC-051-03c | GIVEN extraction prompts are source-agnostic WHEN applied to local repos, URLs, or running apps THEN prompts work across all three source types without modification | Integration |
| AC-051-03d | GIVEN the extractor reads collection template WHEN it encounters a prompt THEN the prompt specifies both WHERE to look (file patterns) AND WHAT to extract (content types) | Unit |

### AC-051-04: Acceptance Criteria File

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-051-04a | GIVEN the acceptance criteria file is loaded WHEN sections are enumerated THEN it contains validation rules for all 7 playbook sections | Unit |
| AC-051-04b | GIVEN each section has acceptance criteria WHEN criteria are counted THEN each section has 3-5 required pass/fail criteria | Unit |
| AC-051-04c | GIVEN a criterion is evaluated WHEN content is tested THEN the criterion is binary (pass/fail) with no subjective judgment required | Unit |
| AC-051-04d | GIVEN acceptance criteria drive the Phase 3 extract-validate loop WHEN the extractor calls validate_section THEN the operation returns true/false + feedback list referencing specific failed criteria | Integration |

### AC-051-05: App-Type Mixins

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-051-05a | GIVEN app-type mixins exist WHEN the extractor requests a mixin THEN three mixins are available: web, cli, mobile | Unit |
| AC-051-05b | GIVEN the web mixin is loaded WHEN extraction prompts are inspected THEN it adds web-specific prompts for UI flows, authentication, navigation, and screenshot locations | Unit |
| AC-051-05c | GIVEN the CLI mixin is loaded WHEN extraction prompts are inspected THEN it adds CLI-specific prompts for commands, flags, subcommands, shell completion, and exit codes | Unit |
| AC-051-05d | GIVEN the mobile mixin is loaded WHEN extraction prompts are inspected THEN it adds mobile-specific prompts for gestures, permissions, app stores, and device compatibility | Unit |
| AC-051-05e | GIVEN a mixin is applied WHEN merged with the base collection template THEN mixin prompts augment (not replace) base prompts for the same section | Unit |

### AC-051-06: Operations API

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-051-06a | GIVEN the skill exposes operations WHEN operations are enumerated THEN 5 operations are documented: get_artifacts, get_collection_template, validate_section, get_mixin, pack_section | Unit |
| AC-051-06b | GIVEN each operation is documented WHEN operation details are read THEN each includes: input parameters (YAML), action description, and output format (YAML) | Unit |
| AC-051-06c | GIVEN operations follow tool skill template format WHEN SKILL.md is parsed THEN each operation is defined in an XML block with `<operation>`, `<input>`, `<action>`, `<output>` tags | Unit |
| AC-051-06d | GIVEN the extractor calls an operation WHEN inputs are provided THEN the operation returns output in the declared format without side effects (read-only, no file writes) | Integration |

## Functional Requirements

**FR-1: Artifact Discovery**  
**Input:** Glob pattern match on `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md`  
**Process:** SKILL.md frontmatter declares `categories: ["user-manual"]` and artifact paths (playbook_template, collection_template, acceptance_criteria, app_type_mixins)  
**Output:** Extractor loads skill and retrieves artifact file paths

**FR-2: Playbook Template Provision**  
**Input:** Request for playbook template (via get_artifacts operation)  
**Process:** Return file path to `templates/playbook-base.md` containing 7-section structure with headings and descriptions  
**Output:** Markdown file with canonical user manual structure

**FR-3: Extraction Prompt Provision**  
**Input:** Request for collection template (via get_collection_template operation)  
**Process:** Return file path to `templates/collection-template.md` with per-section HTML comment prompts  
**Output:** Markdown file with extraction guidance per section

**FR-4: Content Validation**  
**Input:** Section name + extracted content file path (via validate_section operation)  
**Process:** Load acceptance criteria for the section, evaluate content against each criterion, collect failures  
**Output:** Boolean pass/fail + list of failed criteria with feedback messages

**FR-5: App-Type Mixin Provision**  
**Input:** App type (web | cli | mobile) via get_mixin operation  
**Process:** Return file path to corresponding mixin template (`templates/mixin-web.md`, `templates/mixin-cli.md`, `templates/mixin-mobile.md`)  
**Output:** Markdown file with app-type-specific extraction prompts

**FR-6: Content Packing Guidance**  
**Input:** Section name + validated content file path (via pack_section operation)  
**Process:** Apply formatting rules (heading hierarchy, code block conventions, cross-references) to prepare content for final output  
**Output:** Formatted section content file path

**FR-7: File-Based Handoff**  
**Input:** All operations receive file paths, not inline content  
**Process:** Read from `.checkpoint/` folder, write results back to `.checkpoint/`  
**Output:** File paths to results (never inline text to prevent context overflow)

## Non-Functional Requirements

**NFR-1: Performance**  
- All operations must complete within 5 seconds for typical user manual extraction (7 sections, 50 files)
- Validation operations must be stateless and parallelizable across sections

**NFR-2: Maintainability**  
- SKILL.md must remain ≤ 500 lines (detailed templates in `templates/`, guidance in `references/`)
- All file paths must use full project-root-relative paths (no relative `../` paths)
- Template updates must not break extractor skill interface contract

**NFR-3: Compatibility**  
- Source-agnostic design: prompts work equally for local repos, public URLs, and running apps
- App-type mixins must compose cleanly with base template (no conflicts)

## UI/UX Requirements

N/A — This is a backend tool skill with no user interface. All interaction is file-based via `.checkpoint/` folder.

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| EPIC-050 (Application Knowledge Extractor) | External | Consumes this skill's artifacts and operations |
| X-IPE skill framework | Internal | SKILL.md conventions, folder structure (`references/`, `templates/`) |
| `.checkpoint/` handoff protocol | Internal | File-based communication between extractor and tool skill |

## Business Rules

**BR-1:** The 7-section structure is canonical for v1. Future versions may add sections but must not reorder or remove existing sections.

**BR-2:** Acceptance criteria are pass/fail only. No scoring, no subjective ratings. This enables deterministic validation loops.

**BR-3:** App-type mixins augment, not replace. If a section has both base prompts and mixin prompts, both are active.

**BR-4:** This skill is read-only. It never writes to the target application, never modifies source files. All outputs go to `.checkpoint/`.

**BR-5:** Tool skill loading is by category match only. If multiple tool skills declare `categories: ["user-manual"]`, the extractor takes the first alphabetical match.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Extractor requests a mixin for an unsupported app type (e.g., "desktop") | Return error: "Unsupported app_type. Supported: web, cli, mobile" |
| Acceptance criteria file is missing for a section | Fail validation with error: "No acceptance criteria defined for section '{name}'" |
| Collection template prompts reference files that don't exist in target | Extraction continues (prompts are guidance, not hard requirements); extractor adapts search |
| Playbook and collection template have mismatched section counts | Fail DoR check: "Playbook has N sections, collection template has M sections. Must match." |
| Operation called with inline content instead of file path | Return error: "Expected file path, received inline content. Use .checkpoint/ handoff protocol." |
| validate_section called before content is extracted | Return error: "Content file path does not exist: {path}" |
| pack_section called on content that failed validation | Allow (packing may be for diagnostic purposes); log warning |

## Out of Scope

- API-reference, architecture, runbook, configuration extraction categories (future EPICs)
- Multi-version playbook templates (v1 has single canonical template)
- LLM-based adaptive prompt generation (v1 uses static templates)
- Custom section addition by user (v1 enforces 7-section structure)
- Cross-section content linking automation (future enhancement)
- Standalone CLI for tool skill testing (testing via extractor integration only)

## Technical Considerations

- **File structure:** Skill folder must contain SKILL.md (entry point), `references/` (acceptance-criteria.md, examples.md), `templates/` (playbook-base.md, collection-template.md, mixin-web.md, mixin-cli.md, mixin-mobile.md)
- **program_type:** skills (no runtime Python/Node.js code, only markdown templates and SKILL.md procedure)
- **Artifact paths:** Declared in SKILL.md frontmatter, resolved relative to skill folder root
- **Operations format:** Each operation defined as XML block in SKILL.md following tool skill template pattern
- **Validation implementation:** validate_section reads acceptance criteria markdown, parses criteria list, evaluates content presence/format, returns pass/fail + feedback
- **Mixin merge strategy:** When extractor applies mixin, prompts are concatenated (base + mixin) preserving HTML comment format
- **Line budget:** SKILL.md ≤ 500 lines enforced by moving detailed content to `templates/` and `references/`
- **Delivery:** via x-ipe-meta-skill-creator candidate workflow (skill-meta.md → candidate/ → validation → merge to production)

## Open Questions

- None — scope is well-defined by EPIC-050 interface contract and requirements document
