# DAO Decisions — Feature Refinement (26-03-16)

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-001 | 2026-03-16T13:48:43Z | TBD | N/A | instruction | 0.90 | User commands work on FEATURE-049-F; route to feature refinement |
| DAO-098 | 2026-03-16T15:00:24Z | TBD | x-ipe-task-based-feature-refinement | instruction | 0.88 | Design guidance for FEATURE-049-F kb-librarian skill: batch-all, UI-destination-then-AI, skip-frontmatter-for-non-md, terminal-summary, auto-create-folders |

## DAO-001
- **Timestamp:** 2026-03-16T13:48:43Z
- **Task ID:** TBD (to be created on task board)
- **Feature ID:** FEATURE-049-F
- **Workflow:** Knowledge-Base-Implementation
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.90

### Message
> let's work on it

### Guidance Returned
> User wants to implement FEATURE-049-F (KB AI Librarian & Intake). Feature currently LOCKED in workflow, no specification.md exists. Begin with feature refinement to create the specification, then proceed through engineering workflow: technical_design → code_implementation → acceptance_test → feature_closing.

### Rationale
> Clear directive to start work on a previously-discussed feature. No specification exists (FEATURE-049-F dir is empty), so the engineering workflow mandates starting with feature refinement. The requirement-details-part-20.md has enough high-level detail to refine from.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-refinement"
>     match_strength: "strong"
>     reason: "FEATURE-049-F has no specification.md — refinement creates the spec from requirement details"
>     execution_steps:
>       - phase: "1. Context Gathering"
>         step: "1.1 Query feature board for context"
>       - phase: "2. Specification Creation"
>         step: "2.1 Create/update specification document"

### Follow-up
> After refinement completes, proceed to technical_design for FEATURE-049-F.

## DAO-098
- **Timestamp:** 2026-03-16T15:00:24Z
- **Task ID:** TBD (agent Zephyr to assign)
- **Feature ID:** FEATURE-049-F
- **Workflow:** Knowledge-Base-Implementation
- **Calling Skill:** x-ipe-task-based-feature-refinement
- **Source:** ai (agent Zephyr)
- **Disposition:** instruction
- **Confidence:** 0.88

### Message
> Batch of 5 design questions for x-ipe-tool-kb-librarian skill spec (FEATURE-049-F, CR-001): (1) processing mode — batch vs selective, (2) folder determination — AI-only vs UI-destination-first vs always-confirm, (3) non-markdown file handling — skip frontmatter vs sidecar .meta.json vs skip entirely, (4) summary output — terminal vs report file vs silent, (5) folder creation — auto-create vs closest-existing vs ask user.

### Guidance Returned
> **Q1 — Processing mode: Batch all pending files.** KISS. User clicked "✨ Run AI Librarian" — that IS the intent signal to process everything. Adding file selection adds UI complexity with no clear value. If user wants selective, they remove files from .intake/ first.
>
> **Q2 — Folder determination: Option B (UI destination first, AI fallback).** Respect user's pre-assigned destination from the UI if present in .intake-status.json; otherwise AI analyzes content + existing KB structure and picks best match. This leverages existing UI investment while keeping AI as smart default.
>
> **Q3 — Non-markdown files: Option A (move, update status, skip frontmatter).** YAGNI — sidecar .meta.json adds schema complexity, query overhead, and maintenance burden for a feature with no current consumer. Move the file, update .intake-status.json status, assign tags in the status record (not in the file). If sidecar metadata is ever needed, it's a clean CR.
>
> **Q4 — Summary output: Option A (terminal summary).** Users need feedback. "3 files processed → docs/guides/, docs/references/, docs/tutorials/" is simple and sufficient. Report files are YAGNI. Silent is bad UX.
>
> **Q5 — Folder creation: Option A (create automatically).** Cheap, reversible, deliberate. Forcing into wrong folder (B) loses classification accuracy. Asking user (C) breaks batch flow and contradicts Q1's batch philosophy.

### Rationale
> All 5 questions have clear KISS/YAGNI-aligned answers. The skill is a batch processor triggered by explicit user action — simplicity and autonomy are the right defaults. Every decision favors "do the obvious thing, make it reversible" over "add options and ask." Confidence 0.88 reflects slight uncertainty on Q3 (non-markdown handling could justify sidecar approach in future), but YAGNI clearly favors skip-frontmatter-and-track-in-status for now.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-refinement"
>     match_strength: "strong"
>     reason: "Agent is actively writing FEATURE-049-F specification — these design decisions become ACs in the spec"
>     execution_steps:
>       - phase: "2. Specification Creation"
>         step: "2.1 Write acceptance criteria incorporating DAO guidance"

### Follow-up
> Agent should incorporate these 5 decisions as specific ACs in the FEATURE-049-F specification. After spec is complete, proceed to technical_design.
