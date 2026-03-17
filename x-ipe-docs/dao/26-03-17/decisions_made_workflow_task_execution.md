
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

---

## DAO-116 · 2026-03-17T11:36:04Z

**Source:** human | **Workflow:** Knowledge-Extraction
**Trigger:** Two instructions: (1) condense Output Result YAML, (2) start user manual tool skill

### Decomposition — 2 units, sequential groups [[0], [1]]

**Unit 0 — instruction (critique):** Output Result YAML is too verbose (72 lines). Move dynamic output schemas to reference file, keep only essential fields in SKILL.md.
- Suggested skill: direct edit (minor cleanup, not a full refactor)

**Unit 1 — instruction:** Create x-ipe-tool-knowledge-extraction-user-manual skill. ONE feature only (not multi-feature breakdown). ~500 line budget.
- Suggested skill: x-ipe-meta-skill-creator (new skill creation)
- Key constraint: single feature covers all requirements

### 利/害 Analysis
- 利: Cleaner SKILL.md, line budget freed, user manual skill enables end-to-end extraction
- 害: Minimal — unit 0 is low-risk cleanup, unit 1 follows established process

### Confidence: 0.95
