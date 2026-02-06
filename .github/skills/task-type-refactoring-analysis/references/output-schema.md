# Output Schema Reference

This document contains the complete output data model schema for the Refactoring Analysis task type.

---

## Complete Output Attributes

```yaml
Output:
  category: code-refactoring-stage
  status: completed | blocked
  next_task_type: Improve Code Quality Before Refactoring
  require_human_review: Yes
  auto_proceed: {from input Auto Proceed}
  task_output_links: [<path to analysis report>]
  
  # Dynamic attributes - MUST be passed to next task
  quality_baseline:
    exists: true | false
    evaluated_date: <date from report if exists>
    overall_score: <1-10 if exists>
    code_violations:
      file_size: [<files exceeding 800 lines>]
      approaching_threshold: [<files 500-800 lines>]
    feature_gaps: [<features with violations>]
    test_coverage: <percentage if available>
  
  refactoring_scope:
    files: [<expanded list of files>]
    modules: [<expanded list of modules>]
    dependencies: [<identified dependencies>]
    scope_expansion_log: [<log of scope expansions>]
    
  code_quality_evaluated:
    # Each dimension uses score grid: 8-10 aligned, 6-7 needs_attention, 1-5 critical
    # Score = 10 - SUM(violations × importance_weight)
    # Importance weights: critical=3, high=2, medium=1, low=0.5
    
    requirements_alignment:
      score: <1-10>  # Calculated from violations × importance
      status: aligned | needs_attention | critical  # Derived: 8-10=aligned, 6-7=needs_attention, 1-5=critical
      gaps: [<list of gaps>]
      related_docs: [<paths to requirement docs>]
      violations:
        - type: <undocumented | unimplemented | deviated>
          importance: critical | high | medium | low
          weight: <3 | 2 | 1 | 0.5>
       
    specification_alignment:
      score: <1-10>
      status: aligned | needs_attention | critical
      gaps: [<list of gaps>]
      feature_ids: [<FEATURE-XXX>]
      spec_docs: [<paths to tech design docs>]
      violations:
        - type: <missing | outdated | incorrect>
          importance: critical | high | medium | low
          weight: <3 | 2 | 1 | 0.5>
       
    test_coverage:
      score: <1-10>
      status: aligned | needs_attention | critical
      line_coverage: <XX%>
      branch_coverage: <XX%>
      target_percentage: 80
      critical_gaps: [<untested areas>]
      external_api_mocked: true | false
      violations:
        - type: <no_tests | low_coverage | critical_untested>
          importance: critical | high | medium | low
          weight: <3 | 2 | 1 | 0.5>
       
    code_alignment:
      score: <1-10>
      status: aligned | needs_attention | critical
      
      # File Size Analysis (threshold: ≤800 lines)
      file_size_violations:
        - file: <path>
          lines: <count>
          severity: high | medium
          recommendation: "<split suggestion>"
      files_approaching_threshold:
        - file: <path>
          lines: <count>
          buffer: <lines remaining>
      
      # SOLID Principles Assessment
      solid_assessment:
        srp: { status: good | partial | violation, notes: "<details>" }
        ocp: { status: good | partial | violation, notes: "<details>" }
        lsp: { status: good | partial | violation, notes: "<details>" }
        isp: { status: good | partial | violation, notes: "<details>" }
        dip: { status: good | partial | violation, notes: "<details>" }
      
      # KISS Principle Assessment
      kiss_assessment:
        over_engineering: { status: good | violation, notes: "<details>" }
        straightforward_logic: { status: good | violation, notes: "<details>" }
        minimal_dependencies: { status: good | violation, notes: "<details>" }
        clear_intent: { status: good | violation, notes: "<details>" }
      
      # Modular Design Assessment
      modular_design_assessment:
        module_cohesion: { status: good | partial | violation, notes: "<details>" }
        module_coupling: { status: good | partial | violation, notes: "<details>" }
        single_entry_point: { status: good | partial | violation, notes: "<details>" }
        folder_structure: { status: good | partial | violation, notes: "<details>" }
        reusability: { status: good | partial | violation, notes: "<details>" }
        testability: { status: good | partial | violation, notes: "<details>" }
      
      # Code Smell Detection
      code_smells:
        - smell: god_class | long_method | large_file | deep_nesting | too_many_params | duplicate_code
          file: <path>
          severity: high | medium | low
          details: "<description>"
      
    overall_quality_score: <1-10>
    
  refactoring_suggestion:
    summary: "<high-level description of suggested refactoring>"
    goals:
      - goal: "<specific improvement goal>"
        priority: high | medium | low
        rationale: "<why this goal matters>"
        principle: "<SOLID | DRY | KISS | YAGNI | Modular Design | etc.>"
    target_structure: "<description of desired structure after refactoring>"
    
  refactoring_principle:
    primary_principles:
      - principle: <SOLID | DRY | KISS | YAGNI | SoC | Modular Design | etc.>
        rationale: "<why this principle applies>"
        applications:
          - area: "<code area>"
            action: "<specific application>"
    secondary_principles:
      - principle: <name>
        rationale: "<supporting rationale>"
    constraints:
      - constraint: "<what to avoid or preserve>"
        reason: "<why this constraint exists>"
```

---

## Evaluation Thresholds

> These thresholds align with `project-quality-board-management` skill.

| Category | Principle | Threshold |
|----------|-----------|-----------|
| Test | Line Coverage | ≥ 80% |
| Test | Branch Coverage | ≥ 70% |
| Test | Mock External APIs | Required |
| Code | File Size | ≤ 800 lines |
| Code | Function Size | ≤ 50 lines |
| Code | Class Size | ≤ 500 lines |
| Code | Cyclomatic Complexity | ≤ 10 |

---

## Gap Types by Perspective

| Perspective | Gap Types |
|-------------|-----------|
| Requirements | undocumented, unimplemented, deviated |
| Features | missing, extra, deviated |
| Tech Spec | structure, interface, data_model, pattern |
| Test Coverage | business_logic, error_handling, edge_case |
| Tracing Coverage | untraced, unredacted, wrong_level |
