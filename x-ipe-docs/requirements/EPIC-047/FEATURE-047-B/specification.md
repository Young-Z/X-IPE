# FEATURE-047-B: Semantic DAO Logging & Workflow Migration

> **Version:** v1.0
> **Status:** In Refinement
> **Epic:** EPIC-047
> **Depends On:** FEATURE-047-A (Completed)
> **Blocks:** FEATURE-047-C

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 03-06-2026 | Initial specification from requirement-details-part-19.md (FR-047.16–25, HLR-047.6–8) |

---

## Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| N/A | No mockups — this feature is infrastructure/skill-definition only |

---

## Overview

FEATURE-047-B delivers two workstreams:

1. **Semantic DAO Logging** — Add logging steps to the `x-ipe-assistant-user-representative-Engineer` skill so every DAO interaction is recorded as a semantic log entry under `x-ipe-docs/dao/`. Log files are grouped by semantic task type (e.g., `decisions_made_feature_refinement.md`) with DAO deciding whether to merge into an existing file or create a new one.

2. **Workflow Migration** — Replace all call sites that currently invoke `x-ipe-tool-decision-making` with calls to `x-ipe-assistant-user-representative-Engineer` using the new `message_context` input contract. After migration, delete the old `x-ipe-tool-decision-making` skill entirely and remove the legacy `x-ipe-docs/decision_made_by_ai.md` log file from the active design.

Both workstreams preserve the existing `process_preference.auto_proceed` 3-mode behavior (manual / stop_for_question / auto).

---

## User Stories

### US-1: As an AI agent in auto mode, I want DAO to log every interaction so humans can audit decisions asynchronously.

**Acceptance Criteria:**

- [ ] AC-047-B.1: When DAO completes an interaction, it appends a structured log entry to a file under `x-ipe-docs/dao/`.
- [ ] AC-047-B.2: Each log entry includes: timestamp, task_id, feature_id, workflow_name, calling_skill, source (human/ai), disposition chosen, content summary, rationale_summary, confidence, and follow-up (if any).
- [ ] AC-047-B.3: If `x-ipe-docs/dao/` folder does not exist, DAO creates it before writing.

### US-2: As a human reviewer, I want DAO logs grouped by semantic task type so I can review related decisions together.

**Acceptance Criteria:**

- [ ] AC-047-B.4: Log files follow the naming pattern `decisions_made_{semantic_task_type}.md` (e.g., `decisions_made_feature_refinement.md`, `decisions_made_bug_fix.md`).
- [ ] AC-047-B.5: File names are human-readable, lowercase with underscores, and no longer than 80 characters.
- [ ] AC-047-B.6: DAO determines the semantic task type from the `calling_skill` and `downstream_context` fields — NOT from a hardcoded mapping.
- [ ] AC-047-B.7: When a semantically similar log file already exists, DAO appends to it rather than creating a new file.
- [ ] AC-047-B.8: Each log file has a registry table at the top summarizing all entries, followed by detail sections.

### US-3: As a project maintainer, I want the legacy decision log removed so there's a single source of truth.

**Acceptance Criteria:**

- [ ] AC-047-B.9: The `x-ipe-tool-decision-making` skill folder (`.github/skills/x-ipe-tool-decision-making/`) is deleted entirely.
- [ ] AC-047-B.10: All references to `x-ipe-tool-decision-making` in task-based skills, workflow executor, templates, and guidelines are replaced with `x-ipe-assistant-user-representative-Engineer`.
- [ ] AC-047-B.11: The call pattern in each migrated skill uses the `message_context` input contract (with `source`, `messages`, `calling_skill`, `task_id`, etc.) instead of the old `decision_context` + `problems` pattern.
- [ ] AC-047-B.12: References to `decision_made_by_ai.md` in skill files are replaced with DAO semantic logging references.
- [ ] AC-047-B.13: The `x-ipe-docs/decision_made_by_ai.md` file reference is removed from the active design (skills, templates, guidelines).

### US-4: As an AI agent, I want the migrated call sites to work identically in all 3 process modes so nothing breaks.

**Acceptance Criteria:**

- [ ] AC-047-B.14: In `manual` mode, skills continue to ask the human directly (no DAO call) — behavior unchanged.
- [ ] AC-047-B.15: In `stop_for_question` mode, skills continue to ask the human directly — behavior unchanged.
- [ ] AC-047-B.16: In `auto` mode, skills call `x-ipe-assistant-user-representative-Engineer` instead of `x-ipe-tool-decision-making` — the DAO response drives the same branching logic.
- [ ] AC-047-B.17: The DAO disposition (`answer`, `clarification`, `reframe`, `critique`, `instruction`, `approval`, `pass_through`) maps correctly to the skill's branching (proceed / revise / escalate).
- [ ] AC-047-B.18: No task-based skill changes behavior in `manual` or `stop_for_question` modes after migration.

### US-5: As a skill author, I want the task-based template and guidelines updated so new skills use DAO from the start.

**Acceptance Criteria:**

- [ ] AC-047-B.19: The `x-ipe-task-based.md` template references `x-ipe-assistant-user-representative-Engineer` instead of `x-ipe-tool-decision-making`.
- [ ] AC-047-B.20: The `skill-general-guidelines-v2.md` references `x-ipe-assistant-user-representative-Engineer` instead of `x-ipe-tool-decision-making`.
- [ ] AC-047-B.21: The template's auto-proceed call example uses the `message_context` input contract.

---

## Functional Requirements

### Logging

- **FR-047-B.1:** (FR-047.16) DAO MUST write logs under `x-ipe-docs/dao/` only.
- **FR-047-B.2:** (FR-047.17) Log files MUST follow the pattern `decisions_made_{semantic_task_type}.md` with human-readable semantic names.
- **FR-047-B.3:** (FR-047.18) DAO MUST decide whether to append to an existing semantic log file or create a new one, based on its understanding of the calling_skill and downstream_context.
- **FR-047-B.4:** (FR-047.19) Each log entry MUST include: timestamp, task_id, feature_id, workflow_name, calling_skill, source, disposition, content summary, rationale_summary, confidence, and follow-up.
- **FR-047-B.5:** (FR-047.20) The `x-ipe-docs/decision_made_by_ai.md` reference MUST be removed from the active design during rollout.
- **FR-047-B.6:** Each log file MUST have a registry table at the top with columns: Entry ID, Timestamp, Task ID, Calling Skill, Disposition, Confidence, Summary.
- **FR-047-B.7:** Detail sections MUST follow the registry table, one per entry, with full metadata.

### Migration

- **FR-047-B.8:** (FR-047.21) All call sites invoking `x-ipe-tool-decision-making` MUST migrate to `x-ipe-assistant-user-representative-Engineer`.
- **FR-047-B.9:** (FR-047.22) Within-task human-required touchpoints in `auto` mode MUST use DAO.
- **FR-047-B.10:** (FR-047.23) Inter-task routing remains governed by `process_preference.auto_proceed` — DAO replaces only the decision-oriented human substitution mechanism.
- **FR-047-B.11:** (FR-047.24) All task-based skills MUST preserve current manual / stop_for_question / auto behavior contracts after migration.
- **FR-047-B.12:** (FR-047.25) EPIC-046 references mentioning `x-ipe-tool-decision-making` as Phase 2 self-resolution MUST be updated.

### Deletion

- **FR-047-B.13:** The entire `.github/skills/x-ipe-tool-decision-making/` folder MUST be deleted.
- **FR-047-B.14:** The `x-ipe-tool-decision-making` entry MUST be removed from any skill registries or type tables (if present).

---

## Non-Functional Requirements

- **NFR-047-B.1:** (NFR-047.1) Migration MUST preserve backward-compatible workflow semantics for all 3 modes.
- **NFR-047-B.2:** (NFR-047.2) DAO outputs MUST remain human-auditable through semantic log files.
- **NFR-047-B.3:** (NFR-047.4) Semantic log naming must remain stable and understandable to humans reviewing project history.
- **NFR-047-B.4:** Log entries MUST be append-only — no editing or deleting previous entries.
- **NFR-047-B.5:** Migration MUST be atomic — all call sites updated in a single batch, not incrementally.

---

## Migration Scope

### Files to Update (Call Site Migration)

| # | File | Current Refs | Change |
|---|------|-------------|--------|
| 1 | `.github/skills/x-ipe-task-based-bug-fix/SKILL.md` | 1 | Update auto-proceed call to DAO |
| 2 | `.github/skills/x-ipe-task-based-code-implementation/SKILL.md` | 3 | Update auto-proceed calls to DAO |
| 3 | `.github/skills/x-ipe-task-based-code-refactor/SKILL.md` | 3 | Update auto-proceed calls to DAO |
| 4 | `.github/skills/x-ipe-task-based-dev-environment/SKILL.md` | 1 | Update auto-proceed call to DAO |
| 5 | `.github/skills/x-ipe-task-based-feature-closing/SKILL.md` | 2 | Update auto-proceed calls + decision_made_by_ai.md ref |
| 6 | `.github/skills/x-ipe-task-based-idea-mockup/SKILL.md` | 1 | Update auto-proceed call to DAO |
| 7 | `.github/skills/x-ipe-task-based-idea-to-architecture/SKILL.md` | 1 | Update auto-proceed call to DAO |
| 8 | `.github/skills/x-ipe-task-based-ideation/SKILL.md` | 1 | Update auto-proceed call to DAO |
| 9 | `.github/skills/x-ipe-task-based-requirement-gathering/SKILL.md` | 1 | Update auto-proceed call to DAO |
| 10 | `.github/skills/x-ipe-task-based-share-idea/SKILL.md` | 1 | Update auto-proceed call to DAO |
| 11 | `.github/skills/x-ipe-workflow-task-execution/SKILL.md` | 1 | Update routing reference |
| 12 | `.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-task-based.md` | 3 | Update template call pattern |
| 13 | `.github/skills/x-ipe-meta-skill-creator/references/skill-general-guidelines-v2.md` | 2 | Update guidelines references |
| 14 | `.github/skills/x-ipe-tool-web-search/SKILL.md` | 1 | Update reference |

### Files to Delete

| File/Folder | Reason |
|------------|--------|
| `.github/skills/x-ipe-tool-decision-making/` (entire folder) | Superseded by DAO |

### Call Pattern Migration

**Old pattern (x-ipe-tool-decision-making):**
```yaml
CALL x-ipe-tool-decision-making with decision_context:
  calling_skill: "{skill-name}"
  task_id: "{task_id}"
  problems:
    - description: "..."
      type: "conflict | question"
      options: ["option A", "option B"]
```

**New pattern (x-ipe-assistant-user-representative-Engineer):**
```yaml
CALL x-ipe-assistant-user-representative-Engineer with:
  message_context:
    source: "ai"
    calling_skill: "{skill-name}"
    task_id: "{task_id}"
    feature_id: "{feature_id | N/A}"
    workflow_name: "{workflow_name | N/A}"
    downstream_context: "{brief description of what the skill is doing}"
    messages:
      - content: "..."
        preferred_dispositions: ["answer", "clarification"]
  human_shadow: false
```

---

## Log Entry Template

### Registry Table (top of each log file)

```markdown
# DAO Decisions: {Semantic Task Type}

| Entry | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|-------|-----------|---------|---------------|-------------|------------|---------|
| DAO-001 | 2026-03-06T12:30:00Z | TASK-779 | feature-refinement | answer | 0.85 | Resolved scope question about ... |
```

### Detail Section (per entry)

```markdown
---

## DAO-001

- **Timestamp:** 2026-03-06T12:30:00Z
- **Task ID:** TASK-779
- **Feature ID:** FEATURE-047-B
- **Workflow:** N/A
- **Calling Skill:** x-ipe-task-based-feature-refinement
- **Source:** ai
- **Disposition:** answer
- **Confidence:** 0.85

### Message
> {Original message content}

### Guidance Returned
> {DAO's response content}

### Rationale
> {rationale_summary from DAO output}

### Follow-up
> None
```

---

## Dependencies

### Internal
- **FEATURE-047-A** (Completed) — DAO skill type, end-user representative skill, message_context contract
- **EPIC-044** — 3-mode `process_preference.auto_proceed` semantics (preserved, not changed)

### External
- None

---

## Business Rules

- **BR-047-B.1:** DAO logging is mandatory — every DAO interaction MUST produce a log entry. No silent decisions.
- **BR-047-B.2:** Log file semantic grouping is DAO-determined — no hardcoded mapping from skill name to file name.
- **BR-047-B.3:** The 3-mode behavior contract is inviolable — migration MUST NOT change how manual or stop_for_question modes work.
- **BR-047-B.4:** Existing `decision_made_by_ai.md` content is historical — it should not be deleted from disk (may contain valuable history), but all skill/template references to it must be removed.

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `x-ipe-docs/dao/` folder does not exist | DAO creates it before writing first entry |
| No existing log file matches semantic task type | DAO creates a new `decisions_made_{type}.md` file |
| Multiple DAO calls in same task with same semantic type | All entries appended to same file |
| DAO called with `human_shadow: true` and fallback triggers | Log entry still written with `fallback_required: true` noted |
| Skill has multiple auto-proceed decision points | Each point independently calls DAO — each gets a log entry |
| Log file exceeds reasonable size (>500 entries) | Out of scope for v1 — no file rotation in this feature |

---

## Out of Scope

- Semantic log file rotation or archival (future)
- Log file search or querying tools (future)
- Deletion of `x-ipe-docs/decision_made_by_ai.md` from disk (keep as historical artifact — only remove references from active design)
- Changes to `manual` or `stop_for_question` mode behavior
- DAO memory/experience features (FEATURE-047-C scope or later)
- Changes to the DAO disposition set or output contract (established in FEATURE-047-A)

---

## Technical Considerations

- The DAO skill is markdown-based — logging steps are procedural instructions in SKILL.md, not executable code
- The agent executing the DAO skill is responsible for creating folders and writing files
- Semantic task type naming should be derived from `calling_skill` context (e.g., `bug-fix` → `bug_fix`, `feature-refinement` → `feature_refinement`)
- Log entry IDs should be sequential within each file (DAO-001, DAO-002, etc.)
- The migration is a batch text replacement with contract shape update — each skill's auto-proceed branch changes from `decision_context` to `message_context`
