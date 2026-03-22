# DAO Decisions — Bug Fix (26-03-22)

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-103 | 2026-03-22T14:01:37Z | TASK-983 | N/A | instruction | 0.90 | Fix instruction modal localization: when .x-ipe.yaml language=zh, generate instruction text in Chinese while preserving technical flags (--workflow-mode, etc.) in English |

## DAO-103
- **Timestamp:** 2026-03-22T14:01:37Z
- **Task ID:** TBD
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> Get uiux feedback, please visit feedback folder x-ipe-docs/uiux-feedback/Feedback-20260322-215956 to get details. Feedback: "when the language in .x-ipe.yaml set to zh, the instruction should be in chinese, expect [--instructions] for example --workflow-mode..."

### Guidance Returned
> Proceed with bug fix: The "Refine Idea" modal's INSTRUCTIONS text is generated in English even when .x-ipe.yaml language is set to "zh". The instruction text should be localized to Chinese while preserving technical identifiers (e.g., --workflow-mode, --instructions, file paths) in English. This is a localization defect in the instruction generation logic.

### Rationale
> Clear UIUX feedback with screenshot evidence. The user identified a specific UI element (div.instructions-content in the modal), the config that controls language (.x-ipe.yaml language=zh), and the expected behavior (Chinese text except CLI flags). This is a bug in existing localization behavior — maps to bug-fix skill with strong confidence.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-bug-fix"
>     match_strength: "strong"
>     reason: "Reported defect in existing localization behavior — instruction text not respecting language=zh config"
>     execution_steps:
>       - phase: "1. Diagnose"
>         step: "1.1 Reproduce and identify root cause"
>       - phase: "2. Fix"
>         step: "2.1 Write failing test, implement fix, verify"

### Follow-up
> None

---

### DAO-104

| Field | Value |
|-------|-------|
| ID | DAO-104 |
| Timestamp | 2026-03-22T14:19:25Z |
| Task ID | TASK-983 |
| Feature ID | N/A |
| Disposition | answer |
| Confidence | 0.90 |
| Content | User asks if copilot button dropdown in ideation view uses same i18n approach — answer with codebase facts |

---

### DAO-105

| Field | Value |
|-------|-------|
| ID | DAO-105 |
| Timestamp | 2026-03-22T14:39:02Z |
| Task ID | TASK-984 |
| Feature ID | N/A |
| Disposition | instruction |
| Confidence | 0.92 |
| Content | Refactor action-execution-modal i18n from static _I18N code map to data-driven config approach (matching copilot button dropdown pattern in workplace.js). Move labels to copilot-prompt.json ui-labels section. |
