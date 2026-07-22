skill_name: x-ipe-task-based-evaluate-change-request-efforts
skill_type: x-ipe-task-based
version: "1.0.0"
status: candidate
created: 2026-07-22
updated: 2026-07-22
summary: Assess a local Change Request case and publish auditable effort, CIO, and Vendor-executable technical-design reports.
triggers:
  - evaluate change request effort
  - assess vendor CR estimate
  - generate AI CR technical design
not_for:
  - "x-ipe-task-based-change-request: managing implementation changes rather than independently assessing Vendor effort"
workflow:
  category: standalone
  phase: CR Assessment
  next_task_based_skill: null
  human_review: true
inputs:
  required:
    - {name: interaction_mode, type: string, default: interact-with-human, description: Interaction mode}
    - {name: case_folder, type: string, default: null, description: FEATURE-060-A case folder}
    - {name: analysis_depth, type: string, default: standard, description: "quick | standard | deep"}
outputs:
  state:
    - {name: category, value: standalone}
    - {name: status, value: "completed | blocked"}
    - {name: next_task_based_skill, value: null}
  artifacts:
    - {name: case_record, type: file, path: "{case_folder}/CaseRecord.html", description: CIO report and metadata}
    - {name: effort_report, type: file, path: "{case_folder}/EffortEstimation_AI_vN.html", description: Evidence-based estimate}
    - {name: design_report, type: file, path: "{case_folder}/SuggestedTechnicalDesign_AI_vN.html", description: Vendor implementation blueprint}
    - {name: report_model, type: file, path: "{case_folder}/reports/report-model-vN.json", description: Auditable source model}
acceptance_criteria:
  must:
    - {id: AC-M01, category: structure, criterion: Candidate includes all referenced resources, test: file_exists, expected: all present}
    - {id: AC-M02, category: content, criterion: Skill follows five-phase task-based structure, test: section_parse, expected: all phases present}
    - {id: AC-M03, category: behavior, criterion: Publisher validates and atomically exposes a complete version, test: pytest, expected: pass}
    - {id: AC-M04, category: behavior, criterion: Invalid publication preserves latest valid version, test: pytest, expected: pass}
    - {id: AC-M05, category: security, criterion: Template data is escaped and paths remain case-local, test: pytest, expected: pass}
  should:
    - {id: AC-S01, category: content, criterion: Examples cover all three depths and qualified results, test: content_check, expected: present}
    - {id: AC-S02, category: UI, criterion: Templates trace to approved mockups and share offline assets, test: structure_review, expected: pass}
test_scenarios:
  happy_path:
    - {name: publish standard result, given: valid case and model, when: publisher runs, then: four versioned/current artifacts and Completed metadata exist}
  edge_cases:
    - {name: qualified deep result, given: unreachable dependency scope, when: analysis completes, then: reports publish with gaps and reduced confidence}
  error_cases:
    - {name: invalid totals, given: inconsistent model totals, when: publisher validates, then: publication fails without replacing latest}
  blocking:
    - {name: unreadable repository, given: invalid codebase path, when: skill starts, then: BLOCKED before reasoning}
evaluation:
  self_check:
    - All referenced candidate resources exist
    - Publisher tests pass
    - Candidate and production trees have parity after merge
  judge_agent:
    - {criterion: Production readiness, rubric: "5 ready; 4 minor issues; 3 gaps; 2 major issues; 1 fail"}
