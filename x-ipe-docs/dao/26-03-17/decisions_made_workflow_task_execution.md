
---

## DAO-115 · 2026-03-17T10:23:58Z

**Task:** TASK-942 (completed) | **Feature:** FEATURE-050-E | **Workflow:** Knowledge-Extraction
**Source:** human | **Calling Skill:** x-ipe-workflow-task-execution
**Trigger:** User critique — skill not following standard template structure + suggestion to extract to references/templates

### Decomposition
Two related units: (1) Why the structural gap exists (critique), (2) Instruction to refactor using skill-creator (instruction). Sequential — unit 1 depends on unit 0.

### Disposition Selection
- **Unit 0 — critique:** User correctly identifies that SKILL.md was hand-crafted across 5 features without passing through skill-creator's candidate→validate→merge workflow. Template requires XML `<procedure>/<phase_N>/<step_N_M>` tags, XML DoR/DoD, structured phase definitions. None present.
- **Unit 1 — instruction:** Extract 236 lines of inline execution detail to references, restructure to template format via skill-creator. This is a mandatory skill update per copilot instructions.

### 利/害 Analysis
- **利 (gain):** Structural consistency, machine-parseable phases, line budget freed by extraction, future maintainability
- **害 (risk):** Refactor may introduce regressions — mitigated by re-running AC tests after restructure

### Confidence: 0.92

### DAO-115 Addendum (10:27)
**Additional critique:** Remove all FEATURE-050-* references from SKILL.md. These are development tracking artifacts (20+ occurrences), not runtime instructions. Folded into Unit 1 refactor scope.
