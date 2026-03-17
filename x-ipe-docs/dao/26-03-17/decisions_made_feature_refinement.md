# DAO Decisions — Feature Refinement (26-03-17)

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-001 | 2026-03-17T09:00:00Z | TASK-931 | x-ipe-task-based-feature-refinement | instruction | 0.95 | Create FEATURE-050-C specification document |

## DAO-001
- **Timestamp:** 2026-03-17T09:00:00Z
- **Task ID:** TASK-931
- **Feature ID:** FEATURE-050-C
- **Workflow:** Knowledge-Extraction
- **Calling Skill:** x-ipe-task-based-feature-refinement
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.95

### Message
> Create the specification document for FEATURE-050-C (Extract-Validate Loop & Coverage Control) of EPIC-050.

### Guidance Returned
> Create specification following the template from specification-template.md, using context from requirements, idea summary, FEATURE-050-A/B specs, and SKILL.md Phase 3 stub. Use GWT format for ~20-25 ACs across 6 groups.

### Rationale
> Clear instruction with extensive context provided. Single-unit task mapping directly to feature-refinement skill. All design decisions pre-made by user (DAO-autonomous mode). High confidence.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-refinement"
>     match_strength: "strong"
>     reason: "Creating a feature specification document is the core purpose of this skill"
>     execution_steps:
>       - phase: "1. Feature Context Loading"
>         step: "1.1 Load Feature Board Entry"

### Follow-up
> None

---

## FEATURE-050-D: Checkpoint, Resume & Error Handling — Design Decisions

**Date:** 2025-07-25
**Decided by:** DAO (Human Representative, autonomous mode)
**Context:** Phase 4 (明辨之) of EPIC-050, skills-type feature

| Entry ID | Timestamp | Feature ID | Disposition | Confidence | Summary |
|----------|-----------|------------|-------------|------------|---------|
| DAO-002 | 2025-07-25T00:00:00Z | FEATURE-050-D | instruction | 0.92 | 7 design decisions for checkpoint, resume & error handling |

---

### Q1: Checkpoint granularity
**Decision:** (a) Section-level checkpoints only.

**Rationale:** The manifest already tracks per-section status (`extracted | validated | incomplete | error | partial`). Saving after each section extraction is the natural granularity — phase completion is implicitly derived when all sections in a phase reach a terminal status. Adding a separate phase-level checkpoint would be redundant and violate YAGNI. Section-level is sufficient and aligns with the existing `sections[]` array design.

---

### Q2: Resume detection
**Decision:** (a) Auto-detect the most recent checkpoint and resume automatically.

**Rationale:** Since this is a skills-type feature where the AI agent orchestrates the process, auto-detection minimizes friction. The agent scans `.checkpoint/` for `session-{timestamp}/manifest.yaml` files, sorts by timestamp descending, and picks the latest with status `paused` or `extracting` (indicating interrupted work). If multiple sessions exist, the most recent one wins. This is more ergonomic than requiring the user to pass a path, and the timestamp-based naming convention already guarantees deterministic ordering.

---

### Q3: Error classification
**Decision:** 2-tier model — transient (retry) and permanent (halt).

**Rationale:** A 2-tier classification (transient vs. permanent) follows KISS. Transient errors (e.g., file temporarily locked, LLM API timeout) trigger automatic retry. Permanent errors (e.g., file not found, permission denied, unsupported category) halt extraction for that section with an error log entry. The third tier ("recoverable=user-prompt") adds unnecessary complexity — when in DAO mode the agent can autonomously decide recovery strategy, and when in manual mode the halt itself naturally prompts the human. The `error_log[]` array in the manifest captures all error context regardless of tier.

---

### Q4: Retry strategy
**Decision:** (c) Immediate retry with count limit (max 2 retries, 3 total attempts).

**Rationale:** This is prompt engineering driving sequential LLM calls, not a high-throughput network service. Exponential backoff is over-engineering; fixed delay is too rigid and wastes time when the issue is a transient LLM hiccup. Immediate retry with a count limit of 2 retries (3 total attempts) is simple, predictable, and sufficient. If all 3 attempts fail, the error is classified as permanent and the section is marked `error` in the manifest. The retry_count is already part of the `error_log` schema.

---

### Q5: User prompt on error (skills-type)
**Decision:** (b) AI agent makes autonomous decision via DAO when in `dao-represent-human-to-interact` mode; falls back to (a) asking the human in `manual` or `stop_for_question` modes.

**Rationale:** The interaction_mode for this feature is `dao-represent-human-to-interact`, meaning the DAO represents the human for decision-making. When a permanent error occurs, the agent consults the DAO to decide: skip the section, retry with different parameters, or halt entirely. This keeps the extraction flow unblocked without human intervention. When NOT in DAO mode (manual/stop_for_question), the agent surfaces the error to the human and waits for instruction — respecting the interaction_mode contract.

---

### Q6: Checkpoint corruption handling
**Decision:** (a) Start fresh if checkpoint is corrupted, with a warning log.

**Rationale:** Partial recovery from corrupted state risks cascading errors — a half-written manifest or malformed YAML could produce subtly wrong extraction results that are harder to detect than a clean restart. Starting fresh is safest (KISS). The cost of re-extraction is low (LLM calls, typically minutes not hours). The agent logs a warning (`"Corrupted checkpoint detected at {path}, starting fresh session"`) so the human can investigate if needed. Corruption is detected via YAML parse failure or schema_version mismatch.

---

### Q7: Scope boundary for Phase 4
**Decision:** Include "paused" status in Phase 4 scope, but keep it minimal.

**Rationale:** "Paused" status is semantically inseparable from checkpoint/resume — you pause to checkpoint, you resume from paused. The manifest template already lists `paused` as a valid status value (line 60 of `checkpoint-manifest.md`), so this is about implementing the transitions (`extracting → paused`, `paused → extracting`) rather than inventing new schema. Including it in Phase 4 avoids creating a separate micro-task for a tightly coupled concept. Scope is limited to: (1) add `paused` as a status transition, (2) write checkpoint on pause, (3) resume from paused state. No new manifest fields required.
