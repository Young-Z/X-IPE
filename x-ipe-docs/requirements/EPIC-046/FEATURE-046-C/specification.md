# FEATURE-046-C: Restructure 4 Requirement-Stage Skills with 5-Phase Backbone

## Version History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-05 | Sage 🧠 | Initial specification |

## Overview
Restructure 4 requirement-stage skills (requirement-gathering, feature-breakdown, feature-refinement, change-request) to use the 5-phase 博学之→审问之→慎思之→明辨之→笃行之 backbone. These skills are "enriched" (new steps added) unlike the ideation skills which were "reshuffled" only.

## Phase Mappings

### Requirement Gathering (7 steps → 5 phases, 2 new steps)
| Phase | Steps | Source |
|-------|-------|--------|
| P1 博学之 | 1.1 Understand User Request, 1.2 Domain & Context Research ★NEW | step 1 + new |
| P2 审问之 | 2.1 Ask Clarifying Questions, 2.2 Conflict and Overlap Review | steps 2, 3 |
| P3 慎思之 | 3.1 Feasibility & Risk Reflection ★NEW | new |
| P4 明辨之 | 4.1 Update Impacted Features, 4.2 Scope Decision ★NEW | step 4 + new |
| P5 笃行之 | 5.1 Create Requirement Document, 5.2 Complete & Verify | steps 5+6, 7 |

### Feature Breakdown (10 steps → 5 phases, 1 new step)
| Phase | Steps | Source |
|-------|-------|--------|
| P1 博学之 | 1.1 Analyze Requirements, 1.2 Assess Epic Scope | steps 1, 2 |
| P2 审问之 | 2.1 Scope Challenge ★NEW | new |
| P3 慎思之 | 3.1 Evaluate Complexity, 3.2 Identify Features | steps 3, 4 |
| P4 明辨之 | 4.1 MVP Prioritization Decision | extracted from step 4 |
| P5 笃行之 | 5.1 Process Mockups, 5.2 Create Summary, 5.3 Update Board, 5.4 Update Index, 5.5 Dedup Check, 5.6 Complete | steps 5-10 |

### Feature Refinement (5 steps → 5 phases, 2 new steps)
| Phase | Steps | Source |
|-------|-------|--------|
| P1 博学之 | 1.1 Query Feature Board, 1.2 Gather Context, 1.3 Process Mockups | steps 1, 2, 3 |
| P2 审问之 | 2.1 Specification Review Questions ★NEW | new |
| P3 慎思之 | 3.1 AC Quality Reflection ★NEW | new |
| P4 明辨之 | 4.1 Specification Scope Decision | extracted from step 4 |
| P5 笃行之 | 5.1 Create/Update Feature Specification, 5.2 Complete & Verify | steps 4, 5 |

### Change Request (7 steps → 5 phases, 2 new steps, reordered)
| Phase | Steps | Source |
|-------|-------|--------|
| P1 博学之 | 1.1 Understand Change Request, 1.2 CR Context Study ★NEW | step 1 + new |
| P2 审问之 | 2.1 CR Challenge ★NEW, 2.2 Analyze Impact | new + step 2 |
| P3 慎思之 | 3.1 Detect Conflicts | step 4 |
| P4 明辨之 | 4.1 Classify CR Type, 4.2 Route Workflow | steps 3, 5 (reordered!) |
| P5 笃行之 | 5.1 Execute & Document | steps 6+7 |

## Acceptance Criteria

### AC-1: Phase Structure
- AC-1.1: All 4 skills have 5 phases in strict 1→2→3→4→5 order
- AC-1.2: Phase headers use `<phase_N name="Chinese — English">` format
- AC-1.3: Steps use N.M numbering matching their phase
- AC-1.4: No phases are skipped (all requirement skills have content for all 5 phases)

### AC-2: New Steps (★NEW) Content
- AC-2.1: Each new step has meaningful action items (not placeholder)
- AC-2.2: New steps follow existing step format (action, constraints, output)
- AC-2.3: New steps are appropriately sized (not overwhelming the skill)

### AC-3: Preserved Elements
- AC-3.1: All existing DoD checkpoints preserved
- AC-3.2: All existing constraints preserved
- AC-3.3: Output Result YAML fields unchanged
- AC-3.4: Input Parameters unchanged

### AC-4: Execution Flow Table
- AC-4.1: Table uses phase-based format (Phase | Steps | Action | Gate)

### AC-5: Line Count
- AC-5.1: All 4 skills ≤ 500 lines (feature-breakdown currently 505 — must shrink)

### AC-6: Cross-References
- AC-6.1: All internal links use project-root-relative paths
