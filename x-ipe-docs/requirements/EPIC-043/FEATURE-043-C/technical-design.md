# Technical Design: Skill Path Convention Updates

> Feature ID: FEATURE-043-C
> Epic ID: EPIC-043
> Version: v1.0
> Last Updated: 03-04-2026

## Overview

Add a root-relative path constraint to 12 markdown-generating skills and the skill creator template. This ensures all generated internal links use `x-ipe-docs/...` or `.github/skills/...` paths that the File Link Preview feature can resolve.

## Technical Scope

- **Type:** Documentation-only change
- **Files Modified:** 13 SKILL.md files (12 skills + 1 skill-creator)
- **No frontend, backend, or test changes required**

## Constraint Text

The following constraint will be added to each skill:

```
- MANDATORY: All internal markdown links MUST use full project-root-relative paths (e.g., `x-ipe-docs/requirements/EPIC-XXX/specification.md`, `.github/skills/x-ipe-task-based-XXX/SKILL.md`). Do NOT use relative paths like `../` or `./`.
```

## Implementation Plan

Each row specifies which step's `<constraints>` block receives the new entry. If the target step has no `<constraints>` block, one is created.

| # | Skill | Target Step | Notes |
|---|-------|-------------|-------|
| 1 | `x-ipe-task-based-ideation-v2` | Step 6: Generate Idea Draft | Primary idea output step |
| 2 | `x-ipe-task-based-feature-refinement` | Step 4: Create/Update Feature Specification | Primary spec output step |
| 3 | `x-ipe-task-based-technical-design` | Step 5: Create Technical Design Document | Primary design output step |
| 4 | `x-ipe-task-based-requirement-gathering` | Step 6: Create Requirement Details Document | Primary req output step; add `<constraints>` if absent |
| 5 | `x-ipe-task-based-feature-breakdown` | Step 5: Create Summary | Primary breakdown output step |
| 6 | `x-ipe-task-based-change-request` | Step 5: Execute Path | Primary CR output step |
| 7 | `x-ipe-task-based-idea-to-architecture` | Step 5: Create Architecture Diagrams | Primary diagram output step |
| 8 | `x-ipe-task-based-feature-acceptance-test` | Step 5: Reflect and Refine Test Cases | Primary test-cases output step |
| 9 | `x-ipe-task-based-refactoring-analysis` | Step 7: Generate Refactoring Suggestions | Primary analysis output step |
| 10 | `x-ipe-task-based-improve-code-quality` | Step 5: Sync Tests | Documentation sync step |
| 11 | `x-ipe-task-based-code-implementation` | Step 5: Implement Code | Primary code output step; add constraint about generated docs/comments |
| 12 | `x-ipe-task-based-user-manual` _(deprecated → x-ipe-tool-readme-updator)_ | Step 3: Update README | Primary manual output step; add `<constraints>` if absent |
| 13 | `x-ipe-meta-skill-creator` | Step 4: Round 1 (Meta + Draft) | Template for future skills |

## Verification

After all edits:
1. Grep each modified SKILL.md for `root-relative` to confirm constraint present
2. Verify SKILL.md XML structure not broken (no unclosed tags)
3. Count: exactly 13 files modified
