# DAO Decisions — Skill Update (26-03-24)

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-004 | 2026-03-24T07:02:37Z | TBD | — | instruction | 0.92 | Two fixes to bug-fix skill: simplify UI detection + add tool to config |

## DAO-004

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-24T07:02:37Z |
| Task ID | TBD |
| Source | human |
| Disposition | instruction |
| Confidence | 0.92 |

**Message:** "let's do two fix for bug fix skill: 1. you only need simple context check to see if it's a UI bug or not, no need base on program type to see if it's required UI validation or reproducing. 2. x-ipe-docs/config/tools.json don't have x-ipe-tool-ui-testing-via-chrome-mcp tool add it and enable it by default, and no required check for chrome-devtools-mcp"

**Need:** (1) Simplify UI bug detection in bug-fix SKILL.md — replace program_type-based routing with simple context check. (2) Add x-ipe-tool-ui-testing-via-chrome-mcp to tools.json under stages.feedback.bug_fix, enabled by default; remove chrome-devtools-mcp required check.

**Rationale:** User wants practical simplification. Current logic over-engineers UI detection by gating on program_type. A simple "is this a UI bug?" context check is sufficient. The tool config is missing an entry that the skill already references. Both changes are low-risk and self-contained.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-meta-skill-creator"
>     match_strength: "strong"
>     reason: "Modifying x-ipe-task-based-bug-fix SKILL.md content (steps 2, 8, DoD)"
>     execution_steps:
>       - phase: "1. Preparation"
>         step: "1.1 Load existing skill"
>       - phase: "2. Update"
>         step: "2.1 Modify skill content"
>       - phase: "3. Validation"
>         step: "3.1 Validate against checklist"

### Follow-up
> None

---

| DAO-005 | 2026-03-24T08:12:35Z | TASK-988 | — | instruction | 0.90 | Migrate auto_proceed → interaction_mode across bug-fix skill + all candidates |

## DAO-005

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-24T08:12:35Z |
| Task ID | TASK-988 |
| Source | human |
| Disposition | instruction |
| Confidence | 0.90 |

**Message:** "for bug-fix skill why it's still using auto_proceed attribute? we should already replace auto_proceed to interaction_mode right? please scan all the area, any other places using auto_proceed?"

**Need:** Replace all `auto_proceed` references with `interaction_mode` across: (1) bug-fix production SKILL.md (7 hits), (2) 8 candidate SKILL.md files (94 hits), (3) templates (8 hits), (4) skill-meta.md files (21 hits). Total ~130 occurrences.

**Rationale:** The migration from `auto_proceed` to `interaction_mode` was completed for most production skills but bug-fix and many candidate/template files were missed. User confirms this is the intended rename. Mapping: auto→dao-represent-human-to-interact, manual→interact-with-human, stop_for_question→dao-represent-human-to-interact-for-questions-in-skill.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-meta-skill-creator"
>     match_strength: "strong"
>     reason: "Modifying multiple skill SKILL.md files (production + candidates)"

### Follow-up
> None

---

| DAO-006 | 2026-03-24T08:24:25Z | TASK-988 | — | instruction | 0.95 | Complete auto_proceed → interaction_mode migration in templates, skill-meta.md, candidate refs |

## DAO-006

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-24T08:24:25Z |
| Task ID | TASK-988 |
| Source | human |
| Disposition | instruction |
| Confidence | 0.95 |

**Message:** "let's update the as well"

**Need:** Complete the auto_proceed → interaction_mode migration for remaining files: .templates/ (8 hits), skill-meta.md files (21 hits), candidate reference docs (17 hits), task-record.yaml (2 hits).

**Rationale:** Direct continuation of TASK-988. User confirmed updating all remaining locations.
