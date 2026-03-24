# DAO Decisions — Bug Fix (26-03-24)

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-005 | 2026-03-24T15:30:00Z | TASK-987 | N/A | instruction | 0.95 | Fix language-switch FileNotFoundError caused by config_file_path="package-defaults" regression from TASK-986 |

## DAO-005
- **Timestamp:** 2026-03-24T15:30:00Z
- **Task ID:** TASK-987
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.95

### Message
> Since now we have default .x-ipe.yaml as fallback, but when we switch the language in settings, we still get error message 'Failed to switch language: [Errno 2] No such file or directory: package-defaults'. The expectation is: if no .x-ipe.yaml in project root, the language change in settings should update the value in default .x-ipe.yaml

### Guidance Returned
> Fix the language-switch bug introduced by TASK-986. When ConfigService.load() finds no project-level .x-ipe.yaml and sets config_file_path to the literal string "package-defaults", the settings page language switch attempts to write to that non-existent path, raising FileNotFoundError. The fix should ensure that when writing config changes and no project-level .x-ipe.yaml exists, writes go to the package-bundled default config at src/x_ipe/defaults/.x-ipe.yaml. Use x-ipe-task-based-bug-fix skill — write a failing test first, then implement the minimal fix.

### Rationale
> Clear regression bug from TASK-986 with explicit error and expected behavior. User's intent is an instruction to fix. x-ipe-task-based-bug-fix is the strong skill match — both keyword ("error", "not working") and engineering workflow (FEEDBACK stage → bug_fix action) agree. Single unit, no decomposition needed.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Regression bug with known root cause — keyword match (error, not working) and engineering workflow position (FEEDBACK → bug_fix) both agree"
>     execution_steps:
>       - phase: "1. Understand"
>         step: "1. Read bug description, categorize severity"
>       - phase: "2. Reproduce"
>         step: "2. Follow steps to confirm bug occurs"
>       - phase: "3. Diagnose"
>         step: "3. Trace root cause, check technical design"
>       - phase: "4. Design Fix"
>         step: "4. Identify fix options, choose minimal fix"
>       - phase: "5. Conflict Analysis"
>         step: "5. Detect conflicts with existing logic"
>       - phase: "6. Write Test"
>         step: "6. Create failing test that reproduces bug"
>       - phase: "7. Implement"
>         step: "7. Write minimum code to fix bug"
>       - phase: "8. Verify"
>         step: "8. Confirm bug fixed, all tests pass"

### Follow-up
> None
