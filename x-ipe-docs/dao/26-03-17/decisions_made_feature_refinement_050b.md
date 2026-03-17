# DAO Decisions — FEATURE-050-B Refinement (Source Extraction Engine)

**Feature:** FEATURE-050-B (Source Extraction Engine — Phase 2: 审问之)
**Epic:** EPIC-050 (Application Knowledge Extraction)
**Agent:** Nova ☄️
**Interaction Mode:** dao-represent-human-to-interact

---

## DAO-109: FEATURE-050-B Specification Design Decisions

**Date:** 2025-07-17
**Context:** Agent refining specification for FEATURE-050-B, which implements Phase 2 of the extractor skill. Five design questions require human-representative guidance.
**Principles Applied:** KISS, YAGNI, v1 scope, consistency with existing patterns.

---

### Q1: Sub-step structure for Phase 2

**Question:** Separate sub-steps per input type (2.1 Read Files, 2.2 Browse Web, 2.3 Inspect App, 2.4 Web Search) OR one generic "Extract Content" step with DECISION branches per input type?

**Decision:** **One generic step with DECISION branches per input type.**

**Rationale:**
- The SKILL.md has a **500-line limit** — separate sub-steps would consume ~4× the space for essentially the same flow pattern (load template → iterate sections → extract → write content file).
- Phase 1 already resolved `input_type`. Phase 2 should branch on that resolved value, not repeat the classification.
- The extraction flow is structurally identical across types: (1) iterate template sections, (2) gather content per section, (3) write section file. Only the **gather** mechanism differs (read file vs browse page vs inspect app).
- KISS: One step, one loop, one DECISION block for the gather mechanism.

**Structure guidance:**
```
Step 2.1 — Extract Source Content
  FOR EACH section in collection_template:
    DECISION on input_type:
      source_code_repo | documentation_folder → read relevant files (glob + view)
      public_url → browse pages (Chrome DevTools snapshot/screenshot)
      running_web_app → browse + inspect (Chrome DevTools navigate/snapshot)
      single_file → read the one file
    Write: .checkpoint/session-{ts}/content/section-{N}-{slug}.md
```

**Web search** is NOT a branch of input_type — it's a **supplementary action** that can run for ANY input type after primary extraction. Handle as a separate sub-step (Step 2.2) or as a final pass within Step 2.1.

---

### Q2: Web search gating mechanism

**Question:** (a) New `stages.extraction` section in tools.json, (b) reuse existing `stages.ideation` web-search flag, or (c) use existing SKILL.md `config_overrides.web_search_enabled` parameter?

**Decision:** **(c) Use the existing `config_overrides.web_search_enabled` SKILL.md parameter.** Do NOT modify tools.json for v1.

**Rationale:**
- **YAGNI:** `config_overrides.web_search_enabled` already exists in the SKILL.md input contract. It works. Adding a tools.json section is a second config surface for the same toggle — unnecessary complexity.
- **KISS:** One place to check, one parameter to document. The extractor skill reads its own inputs; it doesn't need to cross-reference tools.json.
- **Scope:** tools.json stages are for the **workflow orchestrator** to gate which skills are available at which pipeline stage. The extractor is already loaded — this is an **intra-skill** decision, not a workflow-level gate.
- **Future:** If multiple skills need extraction-stage web search gating, promote to tools.json then. Not now.

**Implementation:**
```
IF config_overrides.web_search_enabled == true:
  After primary extraction, run web search for gaps identified in section content
ELSE:
  Skip web search entirely
```

---

### Q3: Chunking strategy for large codebases

**Question:** (a) Chunk by collection template section, (b) chunk file-by-file, or (c) hybrid (sections primary, sub-chunk large sections by file)?

**Decision:** **(a) Chunk by collection template section.** One content file per template section. No sub-chunking in v1.

**Rationale:**
- **Existing convention:** The handoff protocol already defines `content/section-{N}-{slug}.md`. Follow it exactly.
- **Tool skill contract:** Tool skills validate per-section. They expect one file per section, not file-level fragments they'd need to reassemble.
- **KISS:** The extractor reads multiple source files but **synthesizes** them into one section-level knowledge document. This is extraction, not copying. The agent reads files, understands context, and writes a coherent section summary.
- **YAGNI on sub-chunking:** If a section is too large, the agent naturally summarizes. The LLM context window is the practical limit, and modern agents handle large contexts. Don't pre-optimize.
- **Large repo handling:** The extractor doesn't need to read ALL files. It reads files **relevant to each section** (guided by template prompts). For "Installation" section, read README, package.json, Dockerfile — not every source file.

**File naming:** `content/section-{N}-{slug}.md` (e.g., `content/section-01-overview.md`)

---

### Q4: Error handling for unreadable content

**Question:** (a) Skip silently and log, (b) skip with warning in section content, or (c) halt and ask user?

**Decision:** **(b) Skip with inline warning in the section content file.**

**Rationale:**
- **v1 scope:** FEATURE-050-D (Checkpoint/Resume/Retry) handles sophisticated error recovery. FEATURE-050-B should not duplicate that logic.
- **NOT silent (a):** Tool skills need to know what's missing. If the extractor silently skips binary files, the tool skill can't assess coverage gaps. Inline warnings are visible to the downstream consumer.
- **NOT halt (c):** Halting on every binary file or permission error would make the extractor unusable on real repos with node_modules, .git, images, etc. This violates KISS.
- **Inline warnings** provide a natural signal for FEATURE-050-C's validation loop to detect gaps.

**Format:**
```markdown
<!-- EXTRACTION_WARNING: Skipped {filepath} — {reason: binary_file|permission_denied|file_locked|encoding_error} -->
```

**Common skip rules (hardcoded for v1):**
- Binary files (detected by file extension or null bytes)
- Known non-content directories: `node_modules/`, `.git/`, `dist/`, `build/`, `__pycache__/`
- Files > 1MB (likely generated/binary)

---

### Q5: Extraction depth limit

**Question:** (a) Max files per session, (b) total content size, (c) extraction rounds, or (d) rely on tool skill acceptance criteria as natural stop?

**Decision:** **(d) No artificial limit. Rely on the collection template as the natural scope boundary.** Add one simple safety valve.

**Rationale:**
- **YAGNI:** FEATURE-050-C implements coverage-based depth/breadth control. FEATURE-050-B is a single-pass extraction engine — it doesn't loop. There's nothing to "limit rounds" of.
- **Natural scope:** The collection template defines N sections. The extractor processes each section once. The template IS the scope boundary. It won't read infinite files because it only reads files relevant to the current section prompt.
- **KISS safety valve:** Add `config_overrides.max_files_per_section` (default: **50**) as a circuit breaker. If the extractor would need to read more than 50 files for a single section, it reads the first 50 (prioritized by relevance to the section prompt) and adds an inline note: `<!-- EXTRACTION_NOTE: {M} additional files available but not read (max_files_per_section limit). -->`.
- **Why 50:** Enough for thorough extraction of any single section (e.g., "Core Features" in a medium repo), but prevents runaway reading of 10K files in a monorepo.

**Do NOT add:**
- Total content size limit (LLM context handles this naturally)
- Session-level file limit (sections are independent; limiting globally penalizes later sections)
- Round limits (no rounds in 050-B; that's 050-C)

---

## Summary

| Question | Decision | Principle |
|----------|----------|-----------|
| Q1: Sub-step structure | Generic step + DECISION branches per input_type | KISS (500-line limit, DRY) |
| Q2: Web search gating | Use existing `config_overrides.web_search_enabled` | YAGNI (param already exists) |
| Q3: Chunking strategy | By section (one file per template section) | KISS (follow handoff protocol) |
| Q4: Error handling | Skip + inline warning in content | v1 scope (050-D handles retry) |
| Q5: Depth limit | No artificial limit; template = scope; safety max 50 files/section | YAGNI (050-C handles coverage loop) |

---

**Disposition:** `instruction` — Agent should proceed with feature refinement using these decisions.
**Next Action:** Nova ☄️ creates/updates FEATURE-050-B specification incorporating all five decisions.

---

## DAO-110: Specification Creation for FEATURE-050-B

- **Timestamp:** 2025-07-17T12:00:00Z
- **Task ID:** TASK-NEW (to be assigned)
- **Feature ID:** FEATURE-050-B
- **Workflow:** N/A
- **Calling Skill:** x-ipe-task-based-feature-refinement
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.95

### Message
> User requests creation of the specification file for FEATURE-050-B (Source Extraction Engine) of EPIC-050. Extremely detailed context provided including: feature context, design decisions from DAO-109, Phase 1 output (FEATURE-050-A), extraction capabilities, handoff protocol, exact specification format template with all AC groups, and critical rules.

### Guidance Returned
> Proceed with feature refinement. The user has provided comprehensive, unambiguous instructions for creating `x-ipe-docs/requirements/EPIC-050/FEATURE-050-B/specification.md`. All design decisions were pre-resolved in DAO-109. No clarification needed — execute the specification creation following the provided template exactly.

### Rationale
> Single, clear instruction with exhaustive context. The user has already resolved all design ambiguities through DAO-109. The task maps directly to `x-ipe-task-based-feature-refinement` which handles specification document creation. High confidence due to: (1) explicit file path target, (2) complete template provided, (3) all AC groups defined, (4) critical rules specified, (5) prior design decisions documented.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-refinement"
>     match_strength: "strong"
>     reason: "User is creating a specification document for a feature — this is the core purpose of the feature-refinement skill"
>     execution_steps:
>       - phase: "1. Preparation"
>         step: "1.1 Load feature context from EPIC-050/FEATURE-050-B"
>       - phase: "2. Specification Creation"
>         step: "2.1 Create specification.md following provided template"
>       - phase: "3. Validation"
>         step: "3.1 Verify all AC groups are present and complete"

### Follow-up
> None — all context provided. Proceed directly to specification creation.
