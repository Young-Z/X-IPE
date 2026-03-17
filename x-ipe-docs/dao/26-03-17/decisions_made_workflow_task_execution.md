
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

---

## DAO-117 · 2026-03-17T11:41:12Z

**Source:** human (correction) | **Workflow:** Knowledge-Extraction
**Trigger:** Agent skipped requirement→design→implement lifecycle, jumped directly to skill-creator

### Disposition: critique
Agent violated the workflow: attempted to create the user manual tool skill directly without going through requirement gathering → feature breakdown → refinement → technical design → implementation. Even with "one feature" constraint, the full lifecycle must be followed.

### Corrective Action
1. Stop the rogue skill creation agent
2. Remove any premature candidate files
3. Start properly: requirement gathering for the tool skill
4. Follow: requirements → breakdown (1 feature) → refinement → design → implement via skill-creator → AC test → close

### Confidence: 1.0 (user explicit correction)

---

### DAO-118

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-17T12:27:09Z |
| Source | human |
| Task ID | TASK-944 (EPIC-051 context) |
| Feature ID | FEATURE-051-A |
| Workflow | Knowledge-Extraction |
| Calling Skill | x-ipe-workflow-task-execution |

**Need:** Optimize user manual tool skill templates with 5 structural improvements: (1) Table of Contents linking to scenarios, (2) content splitting when playbook > 800 lines, (3) ToC cross-linking to sub-files, (4) scenario-level markdown with instructions + images, (5) naming conventions for sub-files and images.

**Perspectives:**
- Supporting: Practical improvements for real-world large manuals. ToC + splitting + naming conventions are industry standard.
- Opposing: Adds complexity to recently completed skill. But these are quality-of-life improvements, not scope creep.
- Neutral: This is a Change Request on EPIC-051. All 5 points target the same artifact set (templates in user manual tool skill).

**Disposition:** instruction
**Confidence:** 0.90
**Rationale:** User is commanding enhancement of existing templates. Single unit — all 5 points are cohesive improvements to the same deliverable. Route through CR skill to assess impact, then implement.

**Suggested Skills:** x-ipe-task-based-change-request (strong — modifying existing delivered feature)

---

### DAO-119

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-17T13:08:33Z |
| Source | human |
| Task ID | pending (TASK-947) |
| Feature ID | FEATURE-050-* (EPIC-050) + FEATURE-051-A (EPIC-051) |
| Workflow | Knowledge-Extraction |
| Calling Skill | x-ipe-workflow-task-execution |

**Need:** Refocus the Application Knowledge Extractor skill on its core responsibility (learn knowledge → leverage tool skills). 5 improvements: (1) Study Broadly should guide knowledge extraction techniques including chrome devtools screenshots, (2) Enable chrome devtools as option, (3) Inquire/Think phases should call tool skills for feedback on extracted info, (4) Quality scoring in Discern Clearly should delegate to tool skills (not self-score), (5) Ensure tool skill has quality scoring capability.

**Perspectives:**
- Supporting: This correctly refocuses the extractor as an orchestrator that delegates domain expertise to tool skills. Current skill does too much domain-specific work itself. Chrome devtools integration adds real value for UI-heavy apps.
- Opposing: Significant restructuring of a recently completed skill. But the user's points are architecturally sound — the two-tier design was always intended to have tool skills own domain validation.
- Neutral: This is a CR on EPIC-050 (extractor) + potentially EPIC-051 (tool skill quality scoring). Multi-unit: Unit 0 = CR on extractor skill, Unit 1 = capability check/addition on tool skill.

**Disposition:** instruction
**Confidence:** 0.92
**Rationale:** User is commanding architectural improvement to align with original two-tier design intent. Route through CR skill for both EPICs.

**Instruction Units:**
- Unit 0: CR on EPIC-050 extractor skill — refocus phases, add chrome devtools option, delegate quality scoring to tool skills (points 1-4)
- Unit 1: Check/add quality scoring capability to tool skill EPIC-051 (point 5)

**Execution Plan:** sequential [[0], [1]] — extractor CR first (defines the interface), then tool skill update (implements the interface)

**Suggested Skills:** x-ipe-task-based-change-request (both units)
