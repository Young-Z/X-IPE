# Feature Specification: Layer 1 — Core Skills (Keeper + Extractors)

> Feature ID: FEATURE-059-B  
> Version: v1.0  
> Status: Refined  
> Last Updated: 07-15-2025

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 07-15-2025 | Initial specification |

## Linked Mockups

N/A — Knowledge skills are non-visual (SKILL.md + scripts).

## Overview

FEATURE-059-B delivers the three foundational knowledge skills that all higher layers depend on: `x-ipe-knowledge-keeper-memory` (the unified write gatekeeper), `x-ipe-knowledge-extractor-web` (web extraction via Chrome DevTools MCP), and `x-ipe-knowledge-extractor-memory` (search/retrieval from persistent memory). These skills follow the `x-ipe-knowledge` template created in FEATURE-059-A, using the Operations+Steps hybrid pattern.

Additionally, this feature retires `x-ipe-tool-ontology` — its search functionality is absorbed into `extractor-memory`'s `scripts/search.py`, and its build functionality moves to later layers (059-C/D).

Each skill ships with a `SKILL.md` (following the knowledge template), plus `scripts/`, `references/`, or `templates/` folders as needed. The skills are stateless services invoked by the Knowledge Librarian assistant (FEATURE-059-E).

## User Stories

1. **As** the Knowledge Librarian assistant, **I want** a single gatekeeper for all memory writes, **so that** persistent storage remains consistent and validated regardless of which upstream skill produced the content.

2. **As** a knowledge constructor skill, **I want** to request web page extraction (overview + details) through a standard interface, **so that** I can gather external knowledge without managing browser interactions directly.

3. **As** a knowledge constructor skill, **I want** to search and retrieve existing knowledge from all memory tiers, **so that** I can build on what's already known before extracting new content.

4. **As** a developer, **I want** the memory folder structure to bootstrap automatically on first use, **so that** I don't need to manually create directories before storing knowledge.

5. **As** the system, **I want** `x-ipe-tool-ontology` retired and its search capability absorbed into `extractor-memory`, **so that** the ontology search is maintained by the knowledge skill that owns memory reads.

## Acceptance Criteria

### AC-059B-01: Keeper-Memory — Store Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059B-01a | GIVEN content with `memory_type=episodic` WHEN `store` operation is invoked THEN content is written to `x-ipe-docs/memory/episodic/` with correct metadata | Unit |
| AC-059B-01b | GIVEN content with `memory_type=semantic` WHEN `store` operation is invoked THEN content is written to `x-ipe-docs/memory/semantic/` | Unit |
| AC-059B-01c | GIVEN content with `memory_type=procedural` WHEN `store` operation is invoked THEN content is written to `x-ipe-docs/memory/procedural/` | Unit |
| AC-059B-01d | GIVEN content with an invalid `memory_type` WHEN `store` operation is invoked THEN the operation rejects with a clear error message AND no file is written | Unit |
| AC-059B-01e | GIVEN content with `tags[]` and `metadata` WHEN `store` is invoked THEN returned `stored_path` and `memory_entry_id` are correct AND metadata is persisted alongside content | Unit |

### AC-059B-02: Keeper-Memory — Promote Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059B-02a | GIVEN a file in `.working/` and `memory_type=semantic` WHEN `promote` operation is invoked THEN the file is moved from `.working/` to `x-ipe-docs/memory/semantic/` AND `promoted_path` is returned | Unit |
| AC-059B-02b | GIVEN a file in `.working/` and `memory_type=procedural` WHEN `promote` is invoked THEN the file is moved to `procedural/` with correct metadata | Unit |
| AC-059B-02c | GIVEN a non-existent `working_path` WHEN `promote` is invoked THEN the operation fails with a clear error AND no files are modified | Unit |
| AC-059B-02d | GIVEN a file in `.working/` WHEN `promote` is invoked AND the target memory folder does not exist THEN the bootstrap script creates the folder structure first AND then completes the promote | Integration |

### AC-059B-03: Keeper-Memory — Bootstrap Script

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059B-03a | GIVEN `x-ipe-docs/memory/` does not exist WHEN `scripts/init_memory.py` is executed THEN all 5 top-level folders are created (`.working/`, `.ontology/`, `episodic/`, `semantic/`, `procedural/`) AND `.ontology/` sub-structure is created (`schema/`, `instances/`, `vocabulary/`) with empty index files | Unit |
| AC-059B-03b | GIVEN `x-ipe-docs/memory/` already exists with all folders WHEN `scripts/init_memory.py` is executed THEN no folders are modified or overwritten (idempotent) | Unit |
| AC-059B-03c | GIVEN `x-ipe-docs/memory/` partially exists (e.g., missing `.ontology/instances/`) WHEN `scripts/init_memory.py` is executed THEN only missing folders/files are created AND existing content is preserved | Unit |

### AC-059B-04: Extractor-Web — Extract Overview

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059B-04a | GIVEN a target URL and `depth=shallow` WHEN `extract_overview` operation is invoked THEN the skill navigates via Chrome DevTools MCP AND returns `overview_content` with page structure (headings, navigation) AND a `source_map` of available content sections | Integration |
| AC-059B-04b | GIVEN a target URL and `depth=medium` WHEN `extract_overview` is invoked THEN `overview_content` includes summaries per section (not just headings) AND `source_map` contains section-level detail | Integration |
| AC-059B-04c | GIVEN a target URL WHEN `extract_overview` completes THEN all output is written to `.working/overview/` only (no persistent writes) | Unit |
| AC-059B-04d | GIVEN an unreachable URL WHEN `extract_overview` is invoked THEN the operation returns an error with diagnostic info AND no partial files are left in `.working/` | Integration |

### AC-059B-05: Extractor-Web — Extract Details

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059B-05a | GIVEN a target URL and `scope=full` WHEN `extract_details` is invoked THEN the full page content is extracted with metadata (title, date, author, URL) AND written to `.working/extracted/` | Integration |
| AC-059B-05b | GIVEN a target URL and `scope=section` with section identifier WHEN `extract_details` is invoked THEN only the specified section is extracted AND `metadata` includes source context | Integration |
| AC-059B-05c | GIVEN a target URL and `scope=specific` with `format_hints` WHEN `extract_details` is invoked THEN extraction follows the format hints (e.g., table data, code blocks) AND output structure matches hints | Integration |
| AC-059B-05d | GIVEN extraction completes WHEN output is checked THEN all files are in `.working/extracted/` only (no persistent folder writes) | Unit |

### AC-059B-06: Extractor-Memory — Extract Overview

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059B-06a | GIVEN a query string and `depth=shallow` WHEN `extract_overview` is invoked THEN the skill searches across `episodic/`, `semantic/`, `procedural/` via glob/grep AND returns `overview_content` summarizing matches AND `source_map` listing file paths with relevance | Unit |
| AC-059B-06b | GIVEN a query string and `depth=medium` WHEN `extract_overview` is invoked THEN the skill also queries `.ontology/` via `scripts/search.py` for graph-based results AND combines with folder search results | Integration |
| AC-059B-06c | GIVEN a query with `knowledge_type=procedural` filter WHEN `extract_overview` is invoked THEN only the `procedural/` tier is searched (not all tiers) | Unit |
| AC-059B-06d | GIVEN a query that matches nothing WHEN `extract_overview` is invoked THEN an empty result set is returned with a descriptive message (not an error) | Unit |
| AC-059B-06e | GIVEN any extractor-memory operation WHEN it completes THEN no files are written (read-only skill) | Unit |

### AC-059B-07: Extractor-Memory — Extract Details

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059B-07a | GIVEN a file path target and `scope=full` WHEN `extract_details` is invoked THEN the full file content is read with metadata (file size, last modified, memory tier) | Unit |
| AC-059B-07b | GIVEN a query target and `scope=section` WHEN `extract_details` is invoked THEN matching sections are extracted from the identified files | Unit |
| AC-059B-07c | GIVEN a query target and `format_hints` WHEN `extract_details` is invoked THEN output follows the format hints (e.g., JSON, table, summary) | Unit |

### AC-059B-08: x-ipe-tool-ontology Retirement

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059B-08a | GIVEN `x-ipe-tool-ontology` SKILL.md exists WHEN this feature is implemented THEN a deprecation header is added at the top indicating it is retired AND pointing to `x-ipe-knowledge-extractor-memory` for search and Layer 2+ for build operations | Unit |
| AC-059B-08b | GIVEN `copilot-instructions.md` references `x-ipe-tool-ontology` as knowledge search WHEN this feature is implemented THEN the instruction is updated to reference `x-ipe-knowledge-extractor-memory` scripts/search.py instead | Unit |

### AC-059B-09: Skill Template Compliance

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-059B-09a | GIVEN each of the 3 new skills WHEN their SKILL.md is inspected THEN it follows the `x-ipe-knowledge` template structure from FEATURE-059-A (Operations as top-level sections, Steps inside each operation, typed contracts with `writes_to`) | Unit |
| AC-059B-09b | GIVEN each skill's SKILL.md WHEN the operations table is checked THEN every operation has `input`, `output`, `writes_to`, and `constraints` defined | Unit |
| AC-059B-09c | GIVEN the keeper-memory skill WHEN its `scripts/` folder is inspected THEN `init_memory.py` exists and is executable | Unit |
| AC-059B-09d | GIVEN the extractor-memory skill WHEN its `scripts/` folder is inspected THEN `search.py` exists for ontology search (absorbing x-ipe-tool-ontology search functionality) | Unit |

## Functional Requirements

**FR-1: Keeper-Memory Store Operation**
- Input: `content` (string/structured), `memory_type` (episodic|semantic|procedural), `metadata` (dict), `tags[]` (list)
- Process: Validate memory_type → bootstrap folders if missing → write content to target folder with metadata sidecar
- Output: `stored_path` (string), `memory_entry_id` (string)

**FR-2: Keeper-Memory Promote Operation**
- Input: `working_path` (path in `.working/`), `memory_type`, `metadata`
- Process: Validate working_path exists → bootstrap target if missing → move file from `.working/` to target tier → update metadata
- Output: `promoted_path` (string)

**FR-3: Keeper-Memory Bootstrap**
- Input: None (self-contained)
- Process: Check each required folder/file → create only missing ones → preserve existing
- Output: Fully initialized memory folder structure

**FR-4: Extractor-Web Extract Overview**
- Input: `target` (URL), `depth` (shallow|medium)
- Process: Navigate via Chrome DevTools MCP → scan page structure → build source map → write to `.working/overview/`
- Output: `overview_content`, `source_map`

**FR-5: Extractor-Web Extract Details**
- Input: `target` (URL), `scope` (full|section|specific), `format_hints` (optional)
- Process: Navigate to target → extract per scope → capture metadata → write to `.working/extracted/`
- Output: `extracted_content`, `metadata`

**FR-6: Extractor-Memory Extract Overview**
- Input: `target` (query string or path), `depth` (shallow|medium), `knowledge_type` (optional filter)
- Process: Search memory tiers via glob/grep (shallow) → add ontology search via scripts/search.py (medium) → compile results
- Output: `overview_content`, `source_map`

**FR-7: Extractor-Memory Extract Details**
- Input: `target` (path or query), `scope` (full|section|specific), `format_hints` (optional)
- Process: Read file content → extract per scope → apply format hints
- Output: `extracted_content`, `metadata`

**FR-8: Ontology Search Script**
- Input: Query string, optional class filter, optional relation type filter
- Process: Search `.ontology/instances/` JSONL files and `_relations.*.jsonl` chunks → rank results
- Output: Matching entities with relationships and metadata

**FR-9: x-ipe-tool-ontology Retirement**
- Process: Add deprecation header to SKILL.md → update copilot-instructions.md references
- Output: Deprecated skill with clear migration pointers

## Non-Functional Requirements

**NFR-1: Idempotency** — Bootstrap script and store operations must be safe to call repeatedly without side effects on existing data.

**NFR-2: Write Discipline** — Only keeper-memory writes to persistent folders. Extractors write to `.working/` (extractor-web) or are read-only (extractor-memory). This invariant must be enforced in each skill's `writes_to` contract.

**NFR-3: Statelessness** — All three skills are stateless services. No session state is retained between calls. The orchestrator (Librarian) passes full context per invocation.

**NFR-4: Template Compliance** — All SKILL.md files must follow the `x-ipe-knowledge` template from FEATURE-059-A. Skill creation must go through `x-ipe-meta-skill-creator`.

## UI/UX Requirements

N/A — These are backend/skills with no UI components.

## Dependencies

**Internal:**
- FEATURE-059-A (Implemented) — `x-ipe-knowledge` template must exist in skill-creator
- `x-ipe-meta-skill-creator` — Used to create all 3 skill SKILL.md files
- Chrome DevTools MCP — Required by extractor-web at runtime (not created here, assumed available)

**External:**
- None

## Business Rules

**BR-1:** Only `keeper-memory` may write to persistent memory folders (`episodic/`, `semantic/`, `procedural/`). All other skills must use `.working/` for writes or be read-only.

**BR-2:** The two-phase extraction pattern (overview → details) is the standard interface for both extractors. Callers always request overview first, then details for specific sections.

**BR-3:** Extractor-memory is read-only. It must never modify any file in the memory folder.

**BR-4:** The `.ontology/` search functionality currently in `x-ipe-tool-ontology` is absorbed by `extractor-memory`'s `scripts/search.py`. No other skill should provide ontology search.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Store to non-existent memory folder | Bootstrap script runs automatically, then store completes |
| Promote from non-existent working path | Error returned with clear message, no side effects |
| Extract from unreachable URL | Error with diagnostics, no partial files left |
| Empty search results in extractor-memory | Return empty result set with message, not an error |
| Ontology search with no `.ontology/` folder | Return empty results, do not error |
| Relations chunk file reaches 5000 lines | Keeper should NOT manage chunk creation — that's ontology-builder's concern (Layer 2) |

## Out of Scope

- **Ontology build operations** (class creation, relation insertion, vocabulary management) — deferred to FEATURE-059-C/D
- **Constructor skills** — deferred to FEATURE-059-C
- **Orchestrator/Librarian** — deferred to FEATURE-059-E
- **Migration of existing knowledge-base content** — deferred to FEATURE-059-F
- **Web app UI changes** — deferred to FEATURE-059-F
- **Chunk management for relations files** — owned by ontology-builder (Layer 2+)

## Technical Considerations

- Each skill is a `.github/skills/x-ipe-knowledge-{name}/` directory with SKILL.md + supporting folders
- Scripts are Python-based, placed in each skill's `scripts/` folder
- The bootstrap script (`init_memory.py`) should create the full folder structure including `.ontology/` sub-folders and empty index files
- `scripts/search.py` in extractor-memory absorbs the search capability from `x-ipe-tool-ontology` — it should be able to search JSONL files, class registries, and chunked relation files
- Chrome DevTools MCP integration in extractor-web is defined in the SKILL.md operations (the agent executing the skill uses Chrome DevTools tools at runtime)
- Memory entry IDs should be deterministic or UUID-based — exact format is a design decision

## Open Questions

None — all questions resolved during refinement.
