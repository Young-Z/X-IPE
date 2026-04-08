# Acceptance Test Cases

> Feature: FEATURE-058-D - KB Librarian Ontology Integration
> Generated: 2026-04-08
> Status: Executed

---

## Overview

| Attribute | Value |
|-----------|-------|
| Feature ID | FEATURE-058-D |
| Feature Title | KB Librarian Ontology Integration |
| Total Test Cases | 22 |
| Priority | P0 (10), P1 (8), P2 (4) |
| Target URL | N/A (backend/CLI feature) |

---

## Prerequisites

- [x] Feature code is implemented and committed
- [x] All 111 existing unit tests pass (96 FEATURE-058-A + 15 FEATURE-058-D)
- [x] SKILL.md files are updated

---

## Unit Tests

### TC-001: Graph Index File Generation

**Acceptance Criteria Reference:** AC-058D-03d, AC-058D-04a
**Priority:** P0
**Test Type:** unit
**Assigned Tool:** pytest (existing tests)

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call `graph_ops.build()` with entities in scope | `.graph-index.json` created in output dir |
| 2 | Parse manifest JSON | Has `version`, `generated_at`, `ontology_dir`, `graphs` fields |
| 3 | Check each graph entry | Has `name`, `file`, `description`, `entity_count`, `relation_count`, `dimensions`, `root_entity_id`, `root_label` |
| 4 | Verify `graph_index` key in build result dict | Present and matches file content |

**Mapped Tests:** `TestGraphIndex::test_build_generates_graph_index_file`, `TestGraphIndex::test_graph_index_has_correct_fields`

**Status:** ⬜ Not Run

---

### TC-002: Graph Index Multiple Clusters

**Acceptance Criteria Reference:** AC-058D-04a
**Priority:** P0
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create 2 unrelated entities (different source files) | Two clusters form |
| 2 | Call `graph_ops.build()` | `.graph-index.json` has 2 graph entries |

**Mapped Tests:** `TestGraphIndex::test_graph_index_multiple_clusters`

**Status:** ⬜ Not Run

---

### TC-003: Graph Index Empty Build

**Acceptance Criteria Reference:** AC-058D-04a, AC-058D-04d
**Priority:** P1
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call `graph_ops.build()` with empty entity store | `graph_index.graphs` is empty array |
| 2 | Verify `.graph-index.json` file exists | File created with empty graphs list |

**Mapped Tests:** `TestGraphIndex::test_graph_index_empty_build`

**Status:** ⬜ Not Run

---

### TC-004: Graph Index Dimension Collection

**Acceptance Criteria Reference:** AC-058D-04a, AC-058D-04c
**Priority:** P1
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create entity with `dimensions: {"technology": "Python", "domain": "Security"}` | Entity stored |
| 2 | Call `graph_ops.build()` | Graph entry has `dimensions: ["domain", "technology"]` |

**Mapped Tests:** `TestGraphIndex::test_graph_index_dimensions_collected`

**Status:** ⬜ Not Run

---

### TC-005: Graph Index Atomic Write

**Acceptance Criteria Reference:** AC-058D-04a
**Priority:** P1
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call `graph_ops.build()` | `.graph-index.json` exists |
| 2 | Check for temp file | `.graph-index.json.tmp` does NOT exist |

**Mapped Tests:** `TestGraphIndex::test_graph_index_atomic_write`

**Status:** ⬜ Not Run

---

### TC-006: Graph Index Rebuild Replaces Old

**Acceptance Criteria Reference:** AC-058D-04b, AC-058D-04d
**Priority:** P0
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Build with 1 entity | 1 graph entry |
| 2 | Add entity, rebuild | 2 graph entries, old manifest replaced |
| 3 | Verify content changed | New content differs from old |

**Mapped Tests:** `TestGraphIndex::test_rebuild_replaces_old_index`

**Status:** ⬜ Not Run

---

### TC-007: Retag Happy Path

**Acceptance Criteria Reference:** AC-058D-06a, AC-058D-06b
**Priority:** P0
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Setup `.intake-status.json` with `filed-untagged` file | Status file exists |
| 2 | Call `retag_files(scope, ont_dir, status_path)` | `retagged: 1`, `failed: 0` |
| 3 | Verify entity created | Entity ID starts with `know_` |
| 4 | Verify status updated | Status changed to `filed` |

**Mapped Tests:** `TestRetag::test_retag_happy_path`

**Status:** ⬜ Not Run

---

### TC-008: Retag No Untagged Files

**Acceptance Criteria Reference:** AC-058D-06c
**Priority:** P0
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Setup `.intake-status.json` with only `filed` entries | No untagged files |
| 2 | Call `retag_files()` | `retagged: 0, failed: 0, files: []` |

**Mapped Tests:** `TestRetag::test_retag_no_untagged_files`

**Status:** ⬜ Not Run

---

### TC-009: Retag File Not Found

**Acceptance Criteria Reference:** AC-058D-05a, AC-058D-05c
**Priority:** P0
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Setup status pointing to missing file | Destination doesn't exist |
| 2 | Call `retag_files()` | `failed: 1`, error contains "not found" |

**Mapped Tests:** `TestRetag::test_retag_file_not_found`

**Status:** ⬜ Not Run

---

### TC-010: Retag Mixed Statuses

**Acceptance Criteria Reference:** AC-058D-06a
**Priority:** P1
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Setup 3 files: `filed-untagged`, `filed`, `pending` | Mixed statuses |
| 2 | Call `retag_files()` | Only the `filed-untagged` file processed (1 result) |

**Mapped Tests:** `TestRetag::test_retag_mixed_statuses`

**Status:** ⬜ Not Run

---

### TC-011: Retag Out of Scope

**Acceptance Criteria Reference:** AC-058D-06a
**Priority:** P1
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Setup `filed-untagged` file outside scope path | File in different directory |
| 2 | Call `retag_files(scope=kb_dir)` | `retagged: 0` (out-of-scope ignored) |

**Mapped Tests:** `TestRetag::test_retag_out_of_scope`

**Status:** ⬜ Not Run

---

### TC-012: Retag Updates Existing Entity

**Acceptance Criteria Reference:** AC-058D-06a (edge case from spec)
**Priority:** P1
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Pre-create entity with source_file = destination | Entity exists |
| 2 | Call `retag_files()` | Reuses existing entity ID (update, not duplicate) |

**Mapped Tests:** `TestRetag::test_retag_updates_existing_entity`

**Status:** ⬜ Not Run

---

### TC-013: Retag Invalid Status File

**Acceptance Criteria Reference:** AC-058D-06e
**Priority:** P1
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call `retag_files()` with non-existent status path | Raises ValueError |

**Mapped Tests:** `TestRetag::test_retag_intake_status_not_found`

**Status:** ⬜ Not Run

---

### TC-014: Retag CLI Arguments

**Acceptance Criteria Reference:** AC-058D-06e
**Priority:** P0
**Test Type:** unit

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call `ontology.py retag --scope X --ontology-dir Y --intake-status Z` | Executes and returns JSON result |

**Mapped Tests:** `TestRetag::test_retag_cli_happy_path`

**Status:** ⬜ Not Run

---

## Structured-Review Tests

### TC-015: KB Librarian Skill Contract Declaration

**Acceptance Criteria Reference:** AC-058D-07a, AC-058D-07b
**Priority:** P0
**Test Type:** structured-review

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Read KB Librarian SKILL.md | File accessible |
| 2 | Find "Skill Dependencies" section | Section exists |
| 3 | Verify ontology contract table | Lists `x-ipe-tool-ontology` as dependency |
| 4 | Verify reads/writes documented | Contract mentions entity creation |
| 5 | Verify pre/postconditions | Preconditions and postconditions documented |

**Status:** ⬜ Not Run

---

### TC-016: KB Librarian Ontology Tagging Step

**Acceptance Criteria Reference:** AC-058D-07c, AC-058D-01a, AC-058D-01b
**Priority:** P0
**Test Type:** structured-review

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Read KB Librarian SKILL.md organize_intake operation | Section accessible |
| 2 | Find ontology tagging step (Phase 2 / step h) | Step exists in operation |
| 3 | Verify calls `ontology.py create` with `--type KnowledgeNode` | Command documented |
| 4 | Verify label, node_type, source_files in props | Required properties listed |
| 5 | Verify batch analysis reference | Tagging happens per file during processing |

**Status:** ⬜ Not Run

---

### TC-017: Graceful Degradation in SKILL.md

**Acceptance Criteria Reference:** AC-058D-05a, AC-058D-05b
**Priority:** P0
**Test Type:** structured-review

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Read ontology tagging step in SKILL.md | Step accessible |
| 2 | Verify failure handling | IF creation fails → status set to `filed-untagged` |
| 3 | Verify error recording | Error message recorded in status update |
| 4 | Verify file still moved | File movement happens before tagging (step f before h) |

**Status:** ⬜ Not Run

---

### TC-018: Graph Rebuild Trigger in SKILL.md

**Acceptance Criteria Reference:** AC-058D-03a, AC-058D-03b
**Priority:** P1
**Test Type:** structured-review

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Read SKILL.md organize_intake steps 4-5 | Steps accessible |
| 2 | Verify graph rebuild command | `graph_ops.py build` invoked with --scope, --output, --entities |
| 3 | Verify conditional rebuild | Only runs if entities successfully created |

**Status:** ⬜ Not Run

---

### TC-019: Terminal Summary Format

**Acceptance Criteria Reference:** AC-058D-08d
**Priority:** P2
**Test Type:** structured-review

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Read SKILL.md terminal summary section | Step 5 accessible |
| 2 | Verify untagged count in format | Summary includes `filed-untagged` mention |
| 3 | Verify retag hint | Retag command hint included |

**Status:** ⬜ Not Run

---

### TC-020: Existing Functionality Preservation

**Acceptance Criteria Reference:** AC-058D-08a, AC-058D-08b, AC-058D-08c
**Priority:** P2
**Test Type:** structured-review

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Read SKILL.md steps a-g | Steps a-g unchanged from original |
| 2 | Verify file moving step (f) | Same as before — no ontology dependency |
| 3 | Verify frontmatter step (e) | Same as before — unchanged |
| 4 | Verify non-markdown handling | Same — moved without frontmatter |

**Status:** ⬜ Not Run

---

### TC-021: Ontology SKILL.md Updated

**Acceptance Criteria Reference:** AC-058D-06e, AC-058D-04a
**Priority:** P2
**Test Type:** structured-review

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Read Ontology SKILL.md | File accessible |
| 2 | Find `retag` command in Entity Operations table | Present with args |
| 3 | Find Operation D: Retag section | Section exists with example |
| 4 | Find `.graph-index.json` in Data Storage table | Listed |
| 5 | Find build output documentation | Mentions manifest generation |

**Status:** ⬜ Not Run

---

### TC-022: Error Handling in KB Librarian

**Acceptance Criteria Reference:** AC-058D-05a, AC-058D-05b
**Priority:** P2
**Test Type:** structured-review

**Test Steps:**

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Read SKILL.md Error Handling table | Table accessible |
| 2 | Find `ONTOLOGY_TAG_FAILED` entry | Present with resolution |
| 3 | Find `ONTOLOGY_NOT_AVAILABLE` entry | Present with resolution |

**Status:** ⬜ Not Run

---

## Test Execution Summary

| Test Case | Title | Priority | Type | Status | Notes |
|-----------|-------|----------|------|--------|-------|
| TC-001 | Graph Index File Generation | P0 | unit | ✅ Pass | pytest: test_build_generates_graph_index_file, test_graph_index_has_correct_fields |
| TC-002 | Graph Index Multiple Clusters | P0 | unit | ✅ Pass | pytest: test_graph_index_multiple_clusters |
| TC-003 | Graph Index Empty Build | P1 | unit | ✅ Pass | pytest: test_graph_index_empty_build |
| TC-004 | Graph Index Dimension Collection | P1 | unit | ✅ Pass | pytest: test_graph_index_dimensions_collected |
| TC-005 | Graph Index Atomic Write | P1 | unit | ✅ Pass | pytest: test_graph_index_atomic_write |
| TC-006 | Graph Index Rebuild Replaces Old | P0 | unit | ✅ Pass | pytest: test_rebuild_replaces_old_index |
| TC-007 | Retag Happy Path | P0 | unit | ✅ Pass | pytest: test_retag_happy_path |
| TC-008 | Retag No Untagged Files | P0 | unit | ✅ Pass | pytest: test_retag_no_untagged_files |
| TC-009 | Retag File Not Found | P0 | unit | ✅ Pass | pytest: test_retag_file_not_found |
| TC-010 | Retag Mixed Statuses | P1 | unit | ✅ Pass | pytest: test_retag_mixed_statuses |
| TC-011 | Retag Out of Scope | P1 | unit | ✅ Pass | pytest: test_retag_out_of_scope |
| TC-012 | Retag Updates Existing Entity | P1 | unit | ✅ Pass | pytest: test_retag_updates_existing_entity |
| TC-013 | Retag Invalid Status File | P1 | unit | ✅ Pass | pytest: test_retag_intake_status_not_found |
| TC-014 | Retag CLI Arguments | P0 | unit | ✅ Pass | pytest: test_retag_cli_happy_path |
| TC-015 | KB Librarian Skill Contract | P0 | structured-review | ✅ Pass | Skill Dependencies section with ontology contract |
| TC-016 | KB Librarian Ontology Step | P0 | structured-review | ✅ Pass | Step h with ontology.py create --type KnowledgeNode |
| TC-017 | Graceful Degradation SKILL.md | P0 | structured-review | ✅ Pass | filed-untagged fallback, move-before-tag ordering |
| TC-018 | Graph Rebuild Trigger | P1 | structured-review | ✅ Pass | graph_ops.py build with conditional rebuild |
| TC-019 | Terminal Summary Format | P2 | structured-review | ✅ Pass | filed-untagged count + retag hint |
| TC-020 | Existing Functionality Preserved | P2 | structured-review | ✅ Pass | Steps a-g unchanged, step h additive |
| TC-021 | Ontology SKILL.md Updated | P2 | structured-review | ✅ Pass | retag command, Operation D, .graph-index.json |
| TC-022 | Error Handling in KB Librarian | P2 | structured-review | ✅ Pass | ONTOLOGY_TAG_FAILED + ONTOLOGY_NOT_AVAILABLE |

---

## Execution Results

**Execution Date:** 2026-04-08
**Executed By:** Ember 🔥
**Environment:** local dev

| Metric | Value |
|--------|-------|
| Total Tests | 22 |
| Passed | 22 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

### Results by Type

| Type | Passed | Failed | Blocked | Total |
|------|--------|--------|---------|-------|
| unit | 14 | 0 | 0 | 14 |
| structured-review | 8 | 0 | 0 | 8 |
