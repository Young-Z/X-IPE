# Feature Specification: Skill Migration & MCP Removal

> Feature ID: FEATURE-052-D  
> Version: v1.0  
> Status: Refined  
> Last Updated: 03-30-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-30-2026 | Initial specification |

## Linked Mockups

N/A — skill configuration changes, no UI.

## Overview

FEATURE-052-D completes EPIC-052 by migrating all consuming skills from MCP tool invocations to direct script execution, creating the SKILL.md for the new `x-ipe-tool-x-ipe-app-interactor` skill, and marking the MCP server as deprecated.

17 files across 15 skills reference MCP tools: 12 task-based skills reference `update_workflow_action`, 1 workflow orchestration skill references `update_workflow_action`/`get_workflow_state`, 1 KB skill references `set_kb_index_entry`, and 1 UIUX skill references `save_uiux_reference`. Each reference is replaced with the corresponding script invocation via bash.

## User Stories

1. As an **AI agent executing skills**, I want to invoke standalone scripts instead of MCP tools, so that I don't depend on a running Flask backend.
2. As a **skill author**, I want a documented `x-ipe-tool-x-ipe-app-interactor` SKILL.md, so that I know the CLI interface for each script operation.

## Acceptance Criteria

### AC-052D-01: SKILL.md Creation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052D-01a | GIVEN the `x-ipe-tool-x-ipe-app-interactor` skill folder WHEN SKILL.md is created THEN it documents all 6 script operations with CLI args, exit codes, and usage examples | Unit |
| AC-052D-01b | GIVEN the SKILL.md WHEN reviewed THEN each operation lists: script path, arguments, output format, and exit code table | Unit |

### AC-052D-02: Task-Based Skills — update_workflow_action Migration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052D-02a | GIVEN 12 task-based skills with "Workflow Mode" header blocks WHEN migrated THEN each replaces MCP server reference with script invocation via bash | Unit |
| AC-052D-02b | GIVEN each skill's completion step WHEN migrated THEN the `update_workflow_action` MCP call is replaced with `python3 workflow_update_action.py` bash command | Unit |
| AC-052D-02c | GIVEN each skill's DoD checkpoint WHEN migrated THEN the MCP verification text is replaced with script exit code verification | Unit |

### AC-052D-03: Workflow Task Execution — get_workflow_state Migration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052D-03a | GIVEN `x-ipe-workflow-task-execution` SKILL.md WHEN migrated THEN `update_workflow_action` MCP reference in verification is replaced with script reference | Unit |

### AC-052D-04: KB Librarian — KB Tool Migration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052D-04a | GIVEN `x-ipe-tool-kb-librarian` SKILL.md WHEN migrated THEN `set_kb_index_entry` MCP reference is replaced with `kb_set_entry.py` script invocation | Unit |

### AC-052D-05: UIUX Reference — save_uiux_reference Migration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052D-05a | GIVEN `x-ipe-tool-uiux-reference` SKILL.md WHEN migrated THEN `save_uiux_reference` MCP calls are replaced with `uiux_save_reference.py` script invocation | Unit |
| AC-052D-05b | GIVEN `x-ipe-tool-uiux-reference/references/data-schema.md` WHEN migrated THEN MCP references updated to script references | Unit |
| AC-052D-05c | GIVEN `x-ipe-tool-uiux-reference/references/examples.md` WHEN migrated THEN MCP workflow examples updated to script invocations | Unit |

### AC-052D-06: MCP Deprecation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052D-06a | GIVEN `src/x_ipe/mcp/app_agent_interaction.py` WHEN deprecated THEN a deprecation notice is added at the top of the file | Unit |
| AC-052D-06b | GIVEN no consuming skills reference MCP tools WHEN verified THEN grep for "x-ipe-app-and-agent-interaction" in `.github/skills/` returns zero results | Unit |

## Functional Requirements

- **FR-052D.01**: Create SKILL.md documenting all 6 operations with CLI interface
- **FR-052D.02**: Replace all `update_workflow_action` MCP references in 12 task-based skills
- **FR-052D.03**: Replace `get_workflow_state`/`update_workflow_action` MCP references in workflow-task-execution
- **FR-052D.04**: Replace KB MCP references in kb-librarian
- **FR-052D.05**: Replace UIUX MCP references in uiux-reference skill + reference docs
- **FR-052D.06**: Add deprecation notice to MCP server file

## Non-Functional Requirements

- **NFR-052D.01**: All skill files remain valid markdown after edits
- **NFR-052D.02**: Replacement text is consistent across all skills (same script paths, same pattern)

## Dependencies

- FEATURE-052-A: Workflow scripts (workflow_update_action.py, workflow_get_state.py)
- FEATURE-052-B: KB scripts (kb_get_index.py, kb_set_entry.py, kb_remove_entry.py)
- FEATURE-052-C: UIUX script (uiux_save_reference.py)

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Skills with varying MCP reference wording | All variations must be caught and updated |
| Reference docs (data-schema.md, examples.md) | Update alongside SKILL.md |
| MCP server file | Add deprecation notice, don't delete (allows fallback) |

## Out of Scope

- Deleting MCP server files (deferred to post-validation)
- Removing pyproject.toml MCP entry (deferred)
- Updating CLI adapter configs (deferred)

## Technical Considerations

- 17 files across 15 skills need targeted text replacements
- Common Workflow Mode header block appears in 10+ skills (batch replaceable)
- Skill-specific completion steps vary slightly (manual edit per skill)
