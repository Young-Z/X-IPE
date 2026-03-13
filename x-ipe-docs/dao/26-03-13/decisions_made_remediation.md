# DAO Decisions — 26-03-13 — Remediation

## DAO-062

### Context
> **Source:** human | **Task:** TASK-852 (pending) | **Feature:** FEATURE-049-E | **Workflow:** Knowledge-Base-Implementation

### Message
> "I have uploaded a file to intake mode, but I cannot see it in the intake view"

### Instruction Units

#### Unit 0 — `instruction`
> **Content:** Fix the intake view so uploaded files are visible. Root causes: (1) `_renderIntakeScene()` rebuilds HTML with hardcoded zeros — never loads existing files from `.intake/` or `_intakeFiles`; (2) `trigger-intake-upload` closes the modal and opens generic uploader without intake destination; (3) `_handleIntakeDrop()` only adds ephemeral DOM nodes that get wiped on scene re-render. Fix: load intake files from server (or in-memory store) when rendering intake scene, and ensure upload button targets `.intake/` folder.
> **Rationale:** Clear functional bug — user uploaded a file but the view doesn't reflect it. Single unit, single skill.
> **Suggested skill:** `x-ipe-task-based-bug-fix` (strong match)

### Execution Plan
> **Strategy:** sequential | **Groups:** [[0]]

### Confidence: 0.92 | Fallback: No
