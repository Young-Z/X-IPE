# [RETIRED by EPIC-047] Feature Specification: Decision Making Tool Skill

> Feature ID: FEATURE-044-A
> Epic ID: EPIC-044
> Version: v1.0
> Status: **RETIRED** — Superseded by EPIC-047 (`x-ipe-dao-end-user-representative` replaces `x-ipe-tool-decision-making`)
> Last Updated: 03-06-2026

> ⚠️ **RETIRED:** This specification is superseded by EPIC-047 (DAO End-User Human Proxy Layer).
> The `x-ipe-tool-decision-making` skill is replaced by `x-ipe-dao-end-user-representative`.
> The `decision_made_by_ai.md` audit log is replaced by semantic DAO logs under `x-ipe-docs/dao/`.
> See: [EPIC-047 requirements](x-ipe-docs/requirements/requirement-details-part-19.md),
> [FEATURE-047-A specification](x-ipe-docs/requirements/EPIC-047/FEATURE-047-A/specification.md)

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-04-2026 | Initial specification |
| RETIRED | 03-06-2026 | Superseded by EPIC-047 — `x-ipe-dao-end-user-representative` replaces decision-making tool |

## Linked Mockups

No mockups — this is a tool skill (no UI).

## Overview

FEATURE-044-A creates the `x-ipe-tool-decision-making` tool skill — a lightweight, inline-invocable skill that enables AI agents to autonomously resolve questions, conflicts, and routing decisions during task execution. It is the foundational building block for the 3-mode auto-proceed system (EPIC-044).

When an agent running in `auto` mode encounters a decision point (e.g., a clarifying question, a conflict between requirements, or multiple routing options), it invokes this skill instead of asking the human. The skill analyzes context, optionally searches the web, gets sub-agent critique, and records every decision to a shared audit log (`x-ipe-docs/decision_made_by_ai.md`).

This is a **tool skill** (not task-based) — it has no task board entry, runs inline within the calling skill's execution context, and returns structured decisions for each problem submitted.

## User Stories

1. **As an AI agent in `auto` mode**, I want to resolve within-skill questions autonomously, so that workflow execution continues without human intervention.
2. **As an AI agent facing multiple routing options**, I want a structured decision process for choosing the next task, so that the choice is informed and logged.
3. **As a human reviewer**, I want all AI-made decisions recorded in a structured audit log, so that I can review, approve, or override them asynchronously.
4. **As a project manager**, I want unresolvable decisions flagged as UNRESOLVED in the log, so that I know exactly what needs my attention.

## Acceptance Criteria

### AC Group 1: Skill Structure & Validation

- [ ] AC-044-A.1: `.github/skills/x-ipe-tool-decision-making/SKILL.md` exists with valid tool-skill structure (frontmatter, Purpose, Input Parameters, Execution Procedure, Output Result sections)
- [ ] AC-044-A.2: Skill passes `x-ipe-meta-skill-creator` structural validation for tool-skill type
- [ ] AC-044-A.3: Skill has `references/` folder with any supporting documents
- [ ] AC-044-A.4: Skill has `templates/` folder containing the decision log template

### AC Group 2: Input Contract

- [ ] AC-044-A.5: Skill accepts `decision_context` input with required fields: `calling_skill` (string), `task_id` (string), `workflow_name` (string), and `problems` (array)
- [ ] AC-044-A.6: `feature_id` is an optional field in `decision_context` (default: "N/A")
- [ ] AC-044-A.7: Each problem in `problems` array has required fields: `problem_id` (string), `description` (string), `type` (enum: question|conflict|routing)
- [ ] AC-044-A.8: Each problem has optional fields: `options` (array of strings), `related_files` (array of paths)

### AC Group 3: 6-Step Decision Process

- [ ] AC-044-A.9: Step 1 (Identify & Classify) — skill reads all problems, classifies each by type, identifies quick-resolve candidates
- [ ] AC-044-A.10: Step 2 (Study Context) — skill reads project docs (requirements, specs, technical designs), relevant code files, and test files listed in `related_files`
- [ ] AC-044-A.11: Step 3 (Web Search) — for problems with `type: question` on general topics, skill optionally performs web search. Skipped for project-specific questions.
- [ ] AC-044-A.12: Step 4 (Sub-Agent Critique) — skill invokes a sub-agent to critique each proposed answer/solution with constructive feedback
- [ ] AC-044-A.13: Step 5 (Refine) — skill incorporates critique feedback and refines each answer/solution
- [ ] AC-044-A.14: Step 6 (Record) — skill appends each decision to `x-ipe-docs/decision_made_by_ai.md`

### AC Group 4: Output Contract

- [ ] AC-044-A.15: Skill returns structured `decisions` array with one entry per problem
- [ ] AC-044-A.16: Each decision entry has: `problem_id` (string), `status` (enum: resolved|unresolved), `decision` (string), `rationale` (string)
- [ ] AC-044-A.17: For unresolvable problems, `status` is "unresolved", `decision` contains best-effort analysis, `rationale` explains why resolution failed

### AC Group 5: Unresolved Handling

- [ ] AC-044-A.18: When a problem cannot be resolved, skill logs it as UNRESOLVED in `decision_made_by_ai.md`
- [ ] AC-044-A.19: Execution continues after UNRESOLVED — skill never blocks indefinitely
- [ ] AC-044-A.20: UNRESOLVED entry includes "Follow-up Required: Yes" with description of what human needs to decide

### AC Group 6: Decision Audit Log

- [ ] AC-044-A.21: Decision log template exists at `.github/skills/x-ipe-tool-decision-making/templates/decision-log-template.md`
- [ ] AC-044-A.22: Template includes Decision Registry table with columns: #, Date, Task ID, Feature ID, Skill, Workflow, Problem Type, Status, Section Link
- [ ] AC-044-A.23: Template includes detail section structure with: Decision ID header, Metadata (Task, Skill, Workflow, Feature), Problem Description, Problem Type, Context (files analyzed), Analysis (project docs insight, web research if any, critique feedback), Decision, Rationale, Follow-up Required (Yes/No)
- [ ] AC-044-A.24: Decision IDs follow format `D-{NNN}` (e.g., D-001, D-002) — globally unique per project, auto-incremented from existing registry
- [ ] AC-044-A.25: If `x-ipe-docs/decision_made_by_ai.md` does not exist, skill creates it from template before appending

### AC Group 7: Concurrency & Atomicity

- [ ] AC-044-A.26: Decision log file writes are append-only (no rewriting existing entries)
- [ ] AC-044-A.27: Each decision gets a unique ID even if multiple agents write concurrently (scan existing registry for max ID before writing)

## Functional Requirements

### FR-044-A.1: Skill File Structure

The tool skill MUST be created at `.github/skills/x-ipe-tool-decision-making/` with:
- `SKILL.md` — main skill definition following tool-skill structure
- `templates/decision-log-template.md` — template for `decision_made_by_ai.md`
- `references/` — supporting documentation (decision quality guidelines)

### FR-044-A.2: Input Validation

The skill MUST validate input and fail fast with clear error if:
- `calling_skill` is empty or missing
- `task_id` is empty or missing
- `problems` array is empty
- Any problem is missing `problem_id`, `description`, or `type`
- `type` is not one of: question, conflict, routing

### FR-044-A.3: Problem Type Semantics

| Type | When Used | Example |
|------|-----------|---------|
| `question` | Within-skill clarifying question that would normally go to human | "Should the default timeout be 30s or 60s?" |
| `conflict` | Conflicting requirements, designs, or code patterns detected | "FR-001.3 says 'always cache' but NFR-002.1 says 'no caching in test mode'" |
| `routing` | Multiple next-step options; need to pick one | "Next suggested: [Feature Refinement for A, Feature Refinement for B]" |

### FR-044-A.4: Context Study Scope

Step 2 (Study Context) MUST read:
1. All files in `related_files` (if provided)
2. The calling skill's SKILL.md (for understanding the decision point's context)
3. The feature's `specification.md` (if `feature_id` provided and spec exists)
4. The feature's `technical-design.md` (if exists)
5. The project's `requirement-details` part containing the feature's epic (if discoverable)

### FR-044-A.5: Web Search Criteria

Step 3 (Web Search) MUST:
- Execute ONLY for problems with `type: question`
- Skip if the question is clearly project-specific (references internal files, features, or code)
- Search for: best practices, industry standards, common patterns, compliance requirements
- Limit to 2-3 searches per problem maximum

### FR-044-A.6: Sub-Agent Critique

Step 4 MUST invoke a sub-agent (explore or general-purpose) with:
- The problem description
- The proposed answer/solution from Steps 1-3
- Context from project docs
- Instruction: "Critique this proposed answer. Identify weaknesses, blind spots, and suggest improvements."

### FR-044-A.7: Decision Log Format

Each decision entry in `decision_made_by_ai.md` MUST follow this structure:

```markdown
### D-{NNN}: {Short Title}

| Field | Value |
|-------|-------|
| Date | YYYY-MM-DD HH:MM |
| Task ID | TASK-XXX |
| Feature ID | FEATURE-XXX or N/A |
| Calling Skill | {skill name} |
| Workflow | {workflow name or N/A} |
| Problem Type | question / conflict / routing |
| Status | ✅ Resolved / ⚠️ Unresolved |

**Problem:** {description}

**Context:** {files analyzed, relevant findings}

**Analysis:**
- Project docs insight: {what was found}
- Web research: {if applicable, key findings}
- Critique feedback: {sub-agent's feedback and how it was addressed}

**Decision:** {the chosen answer/solution}

**Rationale:** {why this decision was made}

**Follow-up Required:** Yes/No — {if yes, what human needs to review}
```

### FR-044-A.8: Decision Registry Table

The registry table at the top of `decision_made_by_ai.md` MUST be maintained:

```markdown
| # | Date | Task ID | Feature ID | Skill | Workflow | Type | Status | Link |
|---|------|---------|------------|-------|----------|------|--------|------|
| D-001 | 2026-03-04 | TASK-722 | FEATURE-044-A | Feature Refinement | N/A | question | ✅ Resolved | [D-001](#d-001-short-title) |
```

### FR-044-A.9: Auto-Creation of Decision Log

If `x-ipe-docs/decision_made_by_ai.md` does not exist when the skill is invoked, the skill MUST:
1. Copy the template from `.github/skills/x-ipe-tool-decision-making/templates/decision-log-template.md`
2. Place it at `x-ipe-docs/decision_made_by_ai.md`
3. Then append the decision entries

### FR-044-A.10: ID Auto-Increment

To determine the next Decision ID:
1. Read `x-ipe-docs/decision_made_by_ai.md`
2. Find the highest existing `D-{NNN}` in the registry table
3. Increment by 1 for the new decision
4. If file is new/empty, start at D-001

## Non-Functional Requirements

- **NFR-044-A.1:** Decision log writes MUST be append-only — no modification of existing entries.
- **NFR-044-A.2:** Skill execution MUST complete within the calling skill's time budget (no unbounded web searches or critique loops).
- **NFR-044-A.3:** Web search MUST NOT be used for project-specific questions (internal code, feature-specific logic).
- **NFR-044-A.4:** All skill text (SKILL.md, templates, references) MUST be in English.

## UI/UX Requirements

Not applicable — this is a tool skill with no user interface.

## Dependencies

### Internal Dependencies
- None (this is the foundation feature with no prerequisites)

### External Dependencies
- Sub-agent capability (explore or general-purpose agents) for Step 4 critique
- Web search capability (optional, for Step 3)
- File system access for reading project docs and writing decision log

## Business Rules

- **BR-044-A.1:** Every AI-made decision MUST be logged — no silent decisions.
- **BR-044-A.2:** UNRESOLVED decisions MUST NOT block execution — the calling skill continues with best-effort information.
- **BR-044-A.3:** Decision IDs MUST be globally unique per project — no duplicates even across concurrent agents.
- **BR-044-A.4:** The decision log is append-only — agents MUST NOT modify or delete existing entries.
- **BR-044-A.5:** Web search is ONLY for general knowledge questions — never for internal project queries.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty `problems` array | Fail fast with clear error message |
| All problems unresolvable | Log all as UNRESOLVED, return array with all `status: "unresolved"`, execution continues |
| `decision_made_by_ai.md` does not exist | Create from template, then append |
| Concurrent agents writing to same decision log | Each reads max ID independently; if ID collision detected on write, re-read and retry with next available ID |
| `related_files` contains non-existent paths | Skip missing files with warning in analysis, continue with available context |
| Problem has no `options` provided | Skill generates options based on context analysis (Steps 1-3) |
| `feature_id` is "N/A" | Valid — some decisions are project-level, not feature-specific |
| Sub-agent critique unavailable | Proceed without critique (log warning), still record decision |
| Web search fails or returns no results | Proceed without web context (log warning), continue to Step 4 |

## Out of Scope

- **Human approval workflow** — this skill makes autonomous decisions; human review is asynchronous via the log
- **Decision reversal/rollback** — the log is append-only; corrections are new entries
- **Per-decision confidence scoring** — may be added in future versions
- **Integration with external decision systems** — file-based log only
- **Decision analytics/dashboards** — reading the log is manual for now

## Technical Considerations

- The skill is a **tool skill** — it follows the `x-ipe-tool` template structure, not `x-ipe-task-based`
- The 6-step process should be documented as a clear procedure in SKILL.md with gates between steps
- The decision log template should be self-documenting (include column descriptions)
- ID auto-increment must be robust against concurrent writes (read-increment-write pattern)
- The skill should be invocable by ANY task-based skill — no coupling to specific callers
- `routing` type problems may receive `next_actions_suggested` as options from the orchestrator

## Open Questions

None — all clarified during ideation (TASK-714).
