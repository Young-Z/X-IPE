# FEATURE-046-C: Technical Design

## Changes

### Change 1: Requirement Gathering — 5-Phase Restructure + Enrich
- Replace Execution Flow table with phase-based format
- Replace Execution Procedure with 5-phase XML structure
- Add step 1.2 Domain & Context Research (★NEW): web search for domain standards, competitor analysis
- Add step 3.1 Feasibility & Risk Reflection (★NEW): assess technical feasibility, identify risks
- Add step 4.2 Scope Decision (★NEW): explicit in/out scope decision before documenting
- Merge steps 5+6 into single 5.1 (check file + create document)
- Condense patterns section to table format

### Change 2: Feature Breakdown — 5-Phase Restructure + Enrich + Trim
- **Must reduce from 505 → ≤500 lines while adding structure**
- Replace Execution Flow + Procedure with 5-phase
- Add step 2.1 Scope Challenge (★NEW): challenge whether features are needed, question assumptions
- Merge steps 3+4 into P3 (Think), extract MVP decision into P4
- Consolidate steps 5-10 into P5 sub-steps (more compact)
- Move detailed patterns to references/patterns.md (already exists)
- Condense anti-patterns table

### Change 3: Feature Refinement — 5-Phase Restructure + Enrich
- Replace Execution Flow + Procedure with 5-phase
- Add step 2.1 Specification Review Questions (★NEW): question spec completeness, challenge assumptions
- Add step 3.1 AC Quality Reflection (★NEW): assess if ACs are testable, measurable, complete
- Extract scope decision from step 4 into explicit P4 step
- Condense patterns to table format

### Change 4: Change Request — 5-Phase Restructure + Enrich + Reorder
- **Key reordering: Classification (old step 3) moves to P4 (after conflict analysis)**
- Replace Execution Flow + Procedure with 5-phase
- Add step 1.2 CR Context Study (★NEW): research context of the change
- Add step 2.1 CR Challenge (★NEW): challenge CR assumptions, question necessity
- Move step 2 (Review Existing) to P2.2 (Analyze Impact)
- Move step 4 (Conflict Analysis) to P3.1
- Move step 3 (Classify CR) to P4.1 (classify AFTER understanding conflicts)
- Move step 5 (Human Approval) to P4.2 (Route Workflow)
- Merge steps 6+7 into P5.1

## File Changes
| File | Action |
|------|--------|
| x-ipe-docs/skill-meta/x-ipe-task-based-requirement-gathering/candidate/SKILL.md | Create candidate, restructure |
| x-ipe-docs/skill-meta/x-ipe-task-based-feature-breakdown/candidate/SKILL.md | Create candidate, restructure + trim |
| x-ipe-docs/skill-meta/x-ipe-task-based-feature-refinement/candidate/SKILL.md | Create candidate, restructure |
| x-ipe-docs/skill-meta/x-ipe-task-based-change-request/candidate/SKILL.md | Create candidate, restructure + reorder |
