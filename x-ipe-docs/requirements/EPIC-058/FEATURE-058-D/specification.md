# Feature Specification: KB Librarian Ontology Integration

> Feature ID: FEATURE-058-D
> Version: v1.0
> Status: Refined
> Last Updated: 04-08-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-08-2026 | Initial specification |

## Linked Mockups

No mockups linked — this is a backend integration feature with no UI changes.

## Overview

FEATURE-058-D integrates the newly built Ontology Tool (`x-ipe-tool-ontology`, FEATURE-058-A) into the existing KB Librarian (`x-ipe-tool-kb-librarian`) intake workflow. Today the Librarian processes files from `.intake/`, assigns basic 2D tags (lifecycle × domain), moves files to destination folders, and generates metadata index entries. This feature upgrades the Librarian to call the Ontology Tool's tagging and graph-building operations, replacing the shallow 2D domain assignment with rich multi-dimensional knowledge entities.

The integration is designed to be additive — all existing Librarian functionality (file moving, frontmatter generation, intake status tracking, lifecycle tags in `.kb-index.json`) is preserved. The ontology layer adds deep tagging via `KnowledgeNode` entities with dynamically discovered dimensions, typed inter-document relations, and automatically clustered knowledge graphs. A new `.graph-index.json` manifest provides AI agents with a high-level index of all knowledge graphs for quick relevance lookup.

A new `retag` CLI operation is added to the Ontology Tool, allowing manual re-tagging of files that were previously marked `filed-untagged` due to ontology failures.

## User Stories

1. **As an AI Librarian agent**, I want to call the Ontology Tool's tag operation during intake processing, so that each ingested file receives rich multi-dimensional knowledge tagging beyond basic 2D classification.

2. **As an AI Librarian agent**, I want to trigger graph rebuilding after a tagging batch completes, so that knowledge graphs stay current with newly ingested content, and I can identify which graphs are affected by the new content.

3. **As an AI agent browsing knowledge**, I want a `.graph-index.json` manifest listing all graphs with metadata (name, description, entity count, dimensions), so that I can quickly find relevant graphs without reading every JSONL file.

4. **As an AI agent**, I want the KB Librarian to declare an ontology skill contract in its SKILL.md, so that I understand the reads/writes/pre/postconditions for ontology operations.

5. **As an AI agent**, I want graceful degradation when the ontology tool fails, so that file intake continues even if tagging fails — with files marked `filed-untagged` for later manual re-tagging.

6. **As an AI agent**, I want a `retag` CLI operation in the ontology tool, so that I can manually re-tag files that were previously untagged due to errors.

## Acceptance Criteria

### AC-058D-01: Ontology Tagging During Intake

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058D-01a | GIVEN the KB Librarian processes pending intake files WHEN tagging begins THEN the Librarian invokes `ontology.py create` per file (after filing each file) to create `KnowledgeNode` entities; cross-file relations and batch-level analysis are the AI agent's responsibility during the organize_intake operation | Unit |
| AC-058D-01b | GIVEN the Librarian invokes ontology tagging WHEN creating entities THEN it calls `ontology.py create` with type `KnowledgeNode` and properties: label, node_type, description, dimensions (object), source_files (string[]), weight (number) | Unit |
| AC-058D-01c | GIVEN the Librarian discovers dimensions during batch analysis WHEN a new dimension name appears THEN it calls `dimension_registry.py resolve` to check for aliases, and `dimension_registry.py register` if the dimension is new | Unit |
| AC-058D-01d | GIVEN the Librarian analyzes cross-file relationships WHEN two files share conceptual dependencies THEN it calls `ontology.py relate` with the appropriate relation type (`related_to`, `depends_on`, `is_type_of`, `part_of`, or `described_by`) | Unit |
| AC-058D-01e | GIVEN a folder-level tagging scope WHEN all files in a folder share the same topic THEN a single `KnowledgeNode` entity is created for the folder with `source_files` listing all files | Unit |
| AC-058D-01f | GIVEN a folder-level tagging scope WHEN files in a folder cover diverse topics THEN individual `KnowledgeNode` entities are created per file or per topic cluster | Unit |

### AC-058D-02: Lifecycle Tag Preservation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058D-02a | GIVEN a file is processed during intake WHEN lifecycle tags are assigned (draft/active/deprecated/archived) THEN they are stored in `.kb-index.json` as before AND NOT duplicated in ontology entities | Unit |
| AC-058D-02b | GIVEN the old 2D domain tag was assigned WHEN ontology tagging is active THEN the domain classification is captured as a dynamically discovered ontology dimension instead of a static 2D tag | Unit |
| AC-058D-02c | GIVEN existing files with 2D domain tags in `.kb-index.json` WHEN ontology integration is active THEN existing lifecycle tags in `.kb-index.json` remain unchanged — only new ontology entities are added | Unit |

### AC-058D-03: Graph Rebuild After Batch

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058D-03a | GIVEN a tagging batch completes successfully WHEN all files have been tagged THEN the Librarian triggers `graph_ops.py build` to rebuild knowledge graphs | Unit |
| AC-058D-03b | GIVEN the graph rebuild is triggered WHEN identifying scope THEN the AI agent identifies which graphs are related to the newly tagged entities (via source_files paths and existing graph provenance) AND only rebuilds related graphs | Unit |
| AC-058D-03c | GIVEN graph rebuilding succeeds WHEN graphs are generated THEN each disconnected cluster produces a named `.jsonl` graph file in `.ontology/` | Unit |
| AC-058D-03d | GIVEN graph rebuilding completes WHEN output is produced THEN a `.graph-index.json` manifest file is created/updated in the `.ontology/` directory | Unit |

### AC-058D-04: Graph Index Manifest

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058D-04a | GIVEN graphs exist in `.ontology/` WHEN `.graph-index.json` is generated THEN it contains an array of graph entries, each with: `name` (string), `file` (string path), `description` (string summary), `entity_count` (number), `dimensions` (string[] of dimension names used), `root_entity_id` (string) | Unit |
| AC-058D-04b | GIVEN a graph is rebuilt WHEN `.graph-index.json` is updated THEN the entire manifest is regenerated from current graph files (per FR-4) — all entries reflect the current state of the `.ontology/` directory | Unit |
| AC-058D-04c | GIVEN an AI agent queries `.graph-index.json` WHEN searching for relevant graphs THEN the manifest provides enough metadata to determine graph relevance without reading the full graph JSONL | Unit |
| AC-058D-04d | GIVEN graphs are deleted during rebuild (cluster merged or removed) WHEN `.graph-index.json` is updated THEN stale entries are removed from the manifest | Unit |

### AC-058D-05: Graceful Degradation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058D-05a | GIVEN the ontology tool encounters an error (script failure, corrupt registry, invalid entity) WHEN tagging fails for a file THEN the file is still moved to its destination folder AND intake status is set to `filed-untagged` | Unit |
| AC-058D-05b | GIVEN an ontology error occurs WHEN the error is logged THEN a structured error entry is written with: timestamp, file_path, error_type, error_message | Unit |
| AC-058D-05c | GIVEN some files in a batch succeed and others fail WHEN the batch completes THEN successfully tagged files have status `filed` AND failed files have status `filed-untagged` AND graph rebuild runs only for successfully tagged entities | Unit |
| AC-058D-05d | GIVEN graph rebuild fails after a successful tagging batch WHEN the error is caught THEN all file statuses remain `filed` (not reverted) AND the graph error is logged separately | Unit |

### AC-058D-06: Retag CLI Operation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058D-06a | GIVEN files exist with intake status `filed-untagged` WHEN the `retag` operation is invoked with a scope path THEN the ontology tool reads all untagged files under that path, performs batch analysis, and creates `KnowledgeNode` entities | Unit |
| AC-058D-06b | GIVEN the `retag` operation succeeds for a file WHEN tagging completes THEN the file's intake status is updated from `filed-untagged` to `filed` | Unit |
| AC-058D-06c | GIVEN the `retag` operation is invoked WHEN no `filed-untagged` files exist in the scope THEN it returns a JSON response indicating zero files processed | Unit |
| AC-058D-06d | GIVEN the `retag` operation succeeds for one or more files WHEN all tagging is complete THEN the AI agent is responsible for triggering graph rebuild for affected graphs (the `retag` subcommand itself does not trigger rebuild) | Unit |
| AC-058D-06e | GIVEN the `retag` CLI WHEN invoked THEN it accepts `--scope` (path), `--ontology-dir` (path to .ontology/), and `--intake-status` (path to .intake-status.json) as arguments | Unit |

### AC-058D-07: Skill Contract Declaration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058D-07a | GIVEN the KB Librarian SKILL.md WHEN updated with ontology contract THEN it declares an ontology skill dependency with purpose, contract details (entity creation, fallback status, retag recovery), and supported statuses in a skill dependencies section | Unit |
| AC-058D-07b | GIVEN the skill contract WHEN declared THEN it specifies preconditions: "Files exist in intake folder or KB folder" AND postconditions: "All successfully processed files have KnowledgeNode entities with dimensions" | Unit |
| AC-058D-07c | GIVEN the KB Librarian SKILL.md WHEN updated THEN the `organize_intake` operation description reflects the new ontology tagging step and graph rebuild trigger | Unit |

### AC-058D-08: Existing Functionality Preservation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058D-08a | GIVEN an intake file is processed WHEN moved to destination THEN the file moving behavior is unchanged — same destination logic, same folder structure | Unit |
| AC-058D-08b | GIVEN a markdown file is processed WHEN frontmatter is generated THEN YAML frontmatter generation behavior is unchanged — merges missing fields only | Unit |
| AC-058D-08c | GIVEN a non-markdown file (PDF, image) WHEN processed THEN it is moved without frontmatter AND receives ontology tagging like any other file | Unit |
| AC-058D-08d | GIVEN intake processing completes WHEN the terminal summary is displayed THEN the summary format includes ontology tagging counts: `"{N} files processed → {folder}/ ({count}), {tagged} tagged, {untagged} untagged"` | Unit |

## Functional Requirements

- **FR-1:** The KB Librarian SHALL call ontology tool scripts (`ontology.py`, `dimension_registry.py`, `graph_ops.py`) during the `organize_intake` operation
- **FR-2:** Tagging SHALL use per-file entity creation during the organize_intake loop; the AI agent may perform batch-level analysis (cross-file relations, dimension discovery) as part of its organize_intake reasoning
- **FR-3:** The `graph_ops.py build` operation SHALL generate a `.graph-index.json` manifest alongside graph JSONL files
- **FR-4:** The `.graph-index.json` SHALL be regenerated on every graph build, with entries for current graphs only (stale entries removed)
- **FR-5:** A new `retag` CLI operation SHALL be added to the ontology tool for manual re-tagging of `filed-untagged` files
- **FR-6:** The KB Librarian SKILL.md SHALL declare an ontology skill contract with reads/writes/preconditions/postconditions
- **FR-7:** The `.intake-status.json` SHALL support a new status value: `filed-untagged`

## Non-Functional Requirements

- **NFR-1:** Ontology tagging failure SHALL NOT block file intake — graceful degradation is mandatory
- **NFR-2:** The `.graph-index.json` manifest SHALL be small enough for AI agents to read in full (< 100 KB for typical KB sizes)
- **NFR-3:** Graph rebuild SHALL complete within 30 seconds for KB sizes up to 1000 entities
- **NFR-4:** All ontology tool calls SHALL produce JSON stdout output with exit code 0 on success, 1 on error

## UI/UX Requirements

No UI changes — this is a backend integration feature. All interactions are via AI agent CLI.

## Dependencies

### Internal Dependencies

- **FEATURE-058-A (Ontology Tool Skill):** Provides `ontology.py`, `dimension_registry.py`, `graph_ops.py`, `search.py` — all CLI operations called by the Librarian
- **x-ipe-tool-kb-librarian:** The existing skill being modified — file moving, frontmatter, intake status
- **x-ipe-tool-x-ipe-app-interactor:** Provides `kb_set_entry.py` for metadata index management (unchanged)

### External Dependencies

- **Python 3.10+:** Required for ontology scripts
- **Python stdlib only:** No additional external packages

## Business Rules

- **BR-1:** Lifecycle tags (draft/active/deprecated/archived) REMAIN in `.kb-index.json` — they are operational metadata, not ontology data
- **BR-2:** Domain classification MIGRATES from static 2D tags into ontology as a dynamically discovered dimension
- **BR-3:** Graph rebuild after tagging SHALL only rebuild related graphs — the AI agent identifies affected graphs via source_files paths and graph provenance
- **BR-4:** `filed-untagged` files are only re-tagged via explicit manual `retag` invocation — NOT automatically on next intake run
- **BR-5:** The `.graph-index.json` manifest is a derived view — always regenerated from actual graph files during build
- **BR-6:** Batch analysis mode: all files in a batch are read and analyzed together before any entities are created, enabling cross-file relationship discovery

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Ontology tool script not found (missing file) | Log error, mark file as `filed-untagged`, continue batch |
| Corrupt `.dimension-registry.json` | Log error, skip dimension resolution, create entities without dimension normalization |
| All files in batch fail tagging | All marked `filed-untagged`, skip graph rebuild, log batch error summary |
| Re-tagging a file that already has a `KnowledgeNode` | Update existing entity (via `ontology.py update`) rather than creating duplicate |
| `.graph-index.json` is manually deleted | Fully regenerated on next graph build |
| Empty intake batch (no pending files) | No ontology operations called, no graph rebuild triggered |
| Mixed file types (markdown + PDF + images) | All receive ontology tagging; only markdown gets frontmatter (unchanged behavior) |

## Out of Scope

- **UI changes** — Graph Viewer UI is FEATURE-058-E
- **Search integration** — Graph Search is FEATURE-058-F
- **Ontology tool core changes** — Entity model and graph clustering are stable from FEATURE-058-A (except adding `retag` CLI and `.graph-index.json` generation)
- **Migration of existing 2D tags** — Existing `.kb-index.json` entries are not retroactively tagged with ontology
- **Automatic re-tagging** — No background jobs or scheduled re-tagging

## Technical Considerations

- The KB Librarian SKILL.md is the primary deliverable — it's an AI skill instruction file, not a Python codebase
- The ontology tool scripts are called as subprocess commands by the AI agent following the SKILL.md instructions
- The `.graph-index.json` manifest generation should be added to `graph_ops.py build` output (extending FEATURE-058-A code)
- The `retag` operation can be a new subcommand in `ontology.py` or a separate script
- Intake status tracking (`.intake-status.json`) needs a new `filed-untagged` status value
- Error logging format should be consistent with existing X-IPE conventions (JSON to stdout)

## Open Questions

None — all design questions resolved during refinement.
