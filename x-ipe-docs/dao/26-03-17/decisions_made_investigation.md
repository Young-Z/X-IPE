# DAO Decisions — Investigation

## Entry 1 — Workflow Action Naming Inconsistency Question

- **Timestamp:** 2026-03-17T07:14:33Z
- **Source:** human
- **Task ID:** N/A (ad-hoc investigation)
- **Disposition:** answer
- **Confidence:** 0.95
- **Summary:** User observed naming mismatch between `code_implementation` (used in skills/DAO references) and `implementation` (used in backend workflow engine). Investigated and confirmed the inconsistency exists across multiple layers.
- **Content:** Provided detailed breakdown of where each name is used and identified it as a real inconsistency requiring alignment.

## Entry 2 — Fix All Naming Inconsistencies

- **Timestamp:** 2026-03-17T07:21:47Z
- **Source:** human
- **Task ID:** TBD (to be created on task-board)
- **Disposition:** instruction
- **Confidence:** 0.92
- **Summary:** User instructs to fix all workflow action naming inconsistencies across the codebase. Classified as bug fix — naming mismatches between backend (`implementation`, `acceptance_testing`) and skills/MCP/docs layer (`code_implementation`, `acceptance_test`) can cause silent runtime failures.
- **Suggested Skill:** x-ipe-task-based-bug-fix (strong match)
- **Content:** Align all action names to be consistent across workflow-template.json, workflow_manager_service.py, MCP docstrings, engineering-workflow.md, skills, frontend JS, and workflow state files.
