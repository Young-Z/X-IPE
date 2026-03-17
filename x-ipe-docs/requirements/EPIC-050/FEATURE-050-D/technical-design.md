# Technical Design: Checkpoint, Resume & Error Handling

> Feature ID: FEATURE-050-D | Version: v1.0 | Last Updated: 2026-03-17
> Program Type: skills | Tech Stack: SKILL.md/Prompt Engineering

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents implementing checkpoint, resume, and error handling.
> **📌 AI Coders:** Focus on this section for implementation context.

### What This Feature Does

Implements Phase 4 (明辨之 — Discern Clearly) of the application knowledge extractor — cross-cutting checkpoint persistence, resume-from-pause capability, and 2-tier error handling with retry logic. Unlike Phases 1–3 (which are sequential pipeline steps), Phase 4 behaviors **wrap around** Phases 1–3: resume detection runs BEFORE Phase 1, checkpoint saves run WITHIN Phases 2–3 after each section, and error handling wraps all extraction/validation actions.

### Key Components Implemented

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| `Step 4.1` (SKILL.md procedure step) | Phase 4 cross-cutting checkpoint & error logic | ~20 lines in SKILL.md execution procedure | #checkpoint #phase4 #step |
| `ResumeDetector` (procedure logic) | Scan `.checkpoint/session-*/manifest.yaml` for resumable sessions | Pre-Phase 1 auto-detection by timestamp desc | #resume #checkpoint #detection |
| `CheckpointPersister` (I/O logic) | Save manifest.yaml after each section extraction/validation | Section-level granularity (not phase-level) | #checkpoint #manifest #persistence |
| `ErrorClassifier` (analysis logic) | Classify errors as transient (retry) or permanent (halt) | 2-tier classification drives retry/halt decision | #error #transient #permanent |
| `RetryController` (retry logic) | Immediate retry for transient errors, max 2 retries (3 total) | Wraps Phase 2 + Phase 3 actions | #retry #transient #resilience |
| `RecoveryDecider` (interaction-mode logic) | DAO-autonomous or human-prompted recovery on permanent errors | Mode-aware: dao → autonomous, manual → prompt human | #recovery #dao #interaction |
| `StateMachineEnforcer` (lifecycle logic) | Enforce valid manifest status transitions, reject invalid | Manifest integrity across all phases | #state-machine #transitions |
| `ErrorLogger` (I/O logic) | Append error entries to manifest `error_log[]` | Append-only error audit trail | #error-log #manifest #append |
| `CorruptionHandler` (resilience logic) | Detect corrupted checkpoints, start fresh with warning | Graceful degradation — no crash, no partial state | #corruption #fresh-start |
| `references/checkpoint-error-heuristics.md` | Detailed checkpoint, resume, error, state machine logic | Reference document (keeps SKILL.md concise) | #reference #heuristics |

### Usage Example

```yaml
# Scenario 1: Resume from paused session
invocation:
  target: "./my-app/"
  purpose: "user-manual"

# Agent detects: .checkpoint/session-20260317-143022/manifest.yaml
#   status: "paused", 3/5 sections accepted, 2 remaining
# Agent resumes: extracts section 4 and 5 only
resume_output:
  resumed_from: ".checkpoint/session-20260317-143022/"
  sections_skipped: 3          # already accepted
  sections_remaining: 2
  event_log_entry: "Resumed session at 2026-03-17T15:00:00Z"

# Scenario 2: Transient error with retry
extraction_attempt:
  section: "section-03-installation"
  attempt_1: "LLM API timeout after 15s"     # transient → retry
  attempt_2: "LLM API timeout after 15s"     # transient → retry
  attempt_3: "Success — content extracted"    # 3rd attempt succeeds
  result: "extracted on attempt 3"

# Scenario 3: Permanent error → section skipped (fail-open)
extraction_attempt:
  section: "section-04-troubleshooting"
  error: "Source file not found: docs/TROUBLESHOOT.md"
  classification: "permanent"
  retry_count: 0
  result: "section marked 'error', extraction continues for section-05"
  error_log_entry:
    section_id: 4
    error_type: "permanent"
    message: "Source file not found: docs/TROUBLESHOOT.md"
    retry_count: 0
    timestamp: "2026-03-17T15:02:30Z"
```

### Dependencies

| Dependency | Source | Usage |
|------------|--------|-------|
| FEATURE-050-A Phase 1 | Internal | `.checkpoint/session-{timestamp}/` folder, manifest.yaml template with `status`, `sections[]`, `error_log[]` |
| FEATURE-050-B Phase 2 | Internal | Content files, per-section extraction loop (retry target) |
| FEATURE-050-C Phase 3 | Internal | Validation loop, per-section validation dispatch (retry target) |
| Manifest template | `templates/checkpoint-manifest.md` | Existing fields: `status`, `sections[]`, `error_log[]` — Phase 4 operationalizes them |
| Handoff protocol | `references/handoff-protocol.md` | File-based checkpoint I/O, session folder structure |
| `config_overrides.max_retries` | Skill input parameters | Default 3 (= 3 total attempts, 2 retries) |

---

## Part 2: Implementation Guide

> **Purpose:** Detailed guide for implementing Phase 4 in SKILL.md + reference file.
> **📌 Emphasis on SKILL.md prompt engineering, not runtime code.**

### Manifest State Machine Diagram

```
                     ┌──────────────┐
                     │ initialized  │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
              ┌──────│  extracting  │──────┐
              │      └──────┬───────┘      │
              │             │              │
              ▼             ▼              ▼
       ┌──────────┐  ┌──────────────┐  ┌───────┐
       │  paused  │  │  validating  │  │ error │
       └──┬───┬───┘  └──────┬───────┘  └───────┘
          │   │             │              ▲
          │   └─► extracting│              │
          └───►  validating └──► paused    │
                            │──► error ────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   complete   │
                     └──────────────┘
```

**Valid Transitions:**

| From | To | Trigger |
|------|----|---------|
| initialized | extracting | Phase 2 starts |
| extracting | validating | All sections extracted, Phase 3 starts |
| extracting | paused | User pause or error-induced pause |
| extracting | error | All sections fail / unrecoverable |
| extracting | complete | Phases 2–3 skipped to completion |
| validating | paused | User pause or error-induced pause |
| validating | error | Unrecoverable validation failure |
| validating | complete | Validation exits (all criteria met / max iter / plateau) |
| paused | extracting | Resume into Phase 2 |
| paused | validating | Resume into Phase 3 |
| paused | error | Resume fails |
| paused | complete | Resume + immediate completion |

**Any** state → error (unrecoverable). **Any** state → complete (successful finish).
Invalid transitions are **rejected** with a warning logged to manifest.

### Phase 4 Step Structure for SKILL.md

This defines the exact content to add to `SKILL.md` replacing the Phase 4 stub (lines 328–331 in current SKILL.md).

#### Step 4.1 — Resume, Checkpoint & Error Handling

The step follows the CONTEXT/DECISION/ACTION/VERIFY pattern established by Phases 1–3.

**CONTEXT block** — Cross-cutting behavior (Phase 4 wraps Phases 1–3):
- Phase 4 is NOT sequential after Phase 3 — it defines behaviors that **apply across all phases**
- On invocation: scan `.checkpoint/session-*/manifest.yaml` for resumable sessions (status "paused" or "extracting")
- Config: `max_retries` (default 3 = 3 total attempts, 2 retries), `interaction_mode` from `process_preference`
- State machine rules and error classification details live in the reference file

**DECISION block** — Three decision points:
1. **Resume detection:** Auto-detect most recent checkpoint with status "paused"|"extracting" by scanning session folders sorted by timestamp desc. If found and valid → resume (skip accepted sections). If corrupted (YAML parse fail or `schema_version` ≠ "1.0") → log warning, start fresh. If none found → start fresh (Phase 1).
2. **Error classification:** Transient (timeout, rate limit, temp lock) → retry immediately, max 2 retries. Permanent (not found, permission denied, unsupported format) → no retry, mark section "error".
3. **Recovery mode:** DAO mode → autonomous skip/adjust/halt decision. Manual mode → surface error to human with options (skip, provide alternative, abort).

**ACTION block** — Four action domains:
1. **Checkpoint save:** After each section extraction/validation completion, update manifest with section status + `updated_at` + `content_file` path.
2. **Pause handling:** On pause trigger, set manifest status → "paused", preserve all section states. On resume, add `event_log` entry and refresh `updated_at`.
3. **Retry logic:** Transient errors → immediate retry, up to 2 retries (3 total). Exhausted retries → mark section "error", log to `error_log[]`, continue to next section (fail-open per section).
4. **State machine enforcement:** Enforce valid transitions only (see reference). Log warning and reject invalid transitions. Append to `error_log[]` with schema: `{section_id, error_type, message, retry_count, timestamp}`.

**VERIFY block** — What to check:
- ✅ Manifest status reflects valid state machine transition at every step
- ✅ `error_log[]` entries contain required fields: section_id, error_type, message, retry_count, timestamp
- ✅ Resumed sessions skip already-accepted sections; corrupted checkpoints → fresh start with warning

**REFERENCE:**
- `references/checkpoint-error-heuristics.md` — state machine, resume algorithm, error classification, retry rules, corruption handling
- `references/handoff-protocol.md` — file-based checkpoint I/O

### Proposed SKILL.md Content (~20 lines)

The following is the exact markdown to insert into SKILL.md, replacing lines 328–331:

```markdown
### Phase 4: 明辨之 — Discern Clearly (Checkpoint & Error Handling)

#### Step 4.1 — Resume, Checkpoint & Error Handling

**CONTEXT — Cross-Cutting Behavior:** Phase 4 wraps Phases 1–3 (not sequential). On invocation: scan `.checkpoint/session-*/manifest.yaml` sorted by timestamp desc; select most recent with status "paused"|"extracting". If valid → resume (skip accepted sections). If corrupted (YAML parse fail or schema_version ≠ "1.0") → log warning, start fresh. Config: `max_retries` (default 3 total attempts).

**DECISION — Error Classification & Recovery:**
- Transient error (timeout, rate limit, temp lock) → immediate retry, max 2 retries (3 total)
- Permanent error (not found, permission denied, unsupported) → no retry, mark section "error"
- Exhausted retries → mark "error", log to error_log[], continue next section (fail-open)
- Recovery: DAO mode → autonomous skip/adjust/halt; manual mode → surface options to human

**ACTION — Checkpoint & State Machine:**
1. After each section extraction/validation: persist manifest (status, updated_at, content_file)
2. On pause: status → "paused"; on resume: add event_log entry, refresh updated_at
3. Valid transitions: initialized→extracting, extracting→validating|paused, validating→paused, paused→extracting|validating, any→error|complete. Reject invalid with warning.
4. Append to error_log[]: {section_id, error_type, message, retry_count, timestamp}

**VERIFY:**
- ✅ Manifest status reflects valid state machine transition at every step
- ✅ error_log[] entries have required fields; resumed sessions skip accepted sections
- ✅ Corrupted checkpoints → fresh start with warning logged

**REFERENCE:** `references/checkpoint-error-heuristics.md`, `references/handoff-protocol.md`
```

**Line count of proposed content:** 22 lines (including blank lines and separators).

### Reference File Content Plan

A new reference file is created at:
```
.github/skills/x-ipe-task-based-application-knowledge-extractor/references/checkpoint-error-heuristics.md
```

**Structure:**

```
# Checkpoint & Error Heuristics

## 1. Manifest State Machine
   - Text-based state diagram (same as technical design)
   - Valid transition table (from → to → trigger)
   - Invalid transition handling (reject + log warning)

## 2. Resume Algorithm
   - Detection: scan, filter, sort, select
   - Validation: YAML parse + schema_version check
   - Corruption: fresh start + warning log
   - Resume procedure: load sections, skip accepted, set status, add event_log

## 3. Checkpoint Save Protocol
   - When: after each section extraction (Phase 2) or validation (Phase 3)
   - What: section status, updated_at, content_file path in manifest
   - Idempotency: re-saving same section is safe (overwrites with same data)
   - Pause trigger: user-initiated or error-induced

## 4. Error Classification
   - Transient errors: LLM API timeout, rate limit, temporary file lock, empty response
   - Permanent errors: file not found, permission denied, unsupported format, schema mismatch
   - Ambiguous errors: default to transient (retry is safer than immediate halt)

## 5. Retry Strategy
   - Immediate retry (no backoff in v1)
   - Max 2 retries (3 total attempts, from config_overrides.max_retries)
   - Exhaustion: mark section "error", append to error_log[], continue next section

## 6. error_log[] Schema
   - Field definitions with types
   - Append-only rule (BR-3)
   - Example entries

## 7. Interaction-Mode-Aware Recovery
   - DAO mode: autonomous decision (skip / adjust parameters / halt)
   - Manual mode: surface to human with options (skip / provide alternative / abort)
   - "skip" action: set section status → "skipped", proceed to next

## 8. Pause & Status Transitions
   - Pause trigger: user interruption or error-induced
   - Paused manifest: status → "paused", all section states preserved
   - Resume: event_log entry, updated_at refresh, continue from first incomplete section

## 9. Integration Points with Existing Phases
   - Where resume detection hooks in (before Phase 1)
   - Where checkpoint saves hook in (Phase 2 Step 2.1, Phase 3 Step 3.1)
   - Where error wrapping applies (Phase 2 extraction, Phase 3 validation)

## 10. Edge Cases
   - Table of edge case scenarios and expected behavior
```

### error_log[] Schema

```yaml
error_log:                              # append-only array in manifest.yaml
  - section_id: int                     # section index (matches sections[] entry)
    error_type: "transient | permanent" # 2-tier classification
    message: "string"                   # human-readable error description
    retry_count: int                    # 0 for permanent, 0–2 for transient
    timestamp: "ISO 8601"              # when error was logged
```

**Schema rules:**
- `error_log[]` is append-only — entries are never removed (BR-3)
- One entry per error occurrence (a section that fails 3 times gets 3 entries if logged per retry, or 1 entry with retry_count=2 if logged on exhaustion)
- **Design decision:** Log once on exhaustion (not per retry). `retry_count` indicates how many retries were attempted before failure.
- `section_id` references the section's index in `manifest.sections[]`

**Example:**

```yaml
error_log:
  - section_id: 3
    error_type: "transient"
    message: "LLM API timeout after 15s — exhausted 2 retries"
    retry_count: 2
    timestamp: "2026-03-17T15:02:30Z"
  - section_id: 4
    error_type: "permanent"
    message: "Source file not found: docs/TROUBLESHOOT.md"
    retry_count: 0
    timestamp: "2026-03-17T15:03:15Z"
```

### Resume Algorithm

```
RESUME DETECTION (runs BEFORE Phase 1 Step 1.1):

1. SCAN:     Glob .checkpoint/session-*/manifest.yaml
2. FILTER:   Select manifests where:
               - status IN ("paused", "extracting")
               - target matches current invocation target
3. SORT:     By session-{timestamp} descending (most recent first)
4. SELECT:   First (most recent) matching manifest
5. VALIDATE:
   a. Parse YAML — if parse fails → CORRUPTED
   b. Check schema_version == "1.0" — if mismatch → CORRUPTED
   c. If CORRUPTED:
      → Log warning: "Corrupted checkpoint at {path}, starting fresh session"
      → Fall through to normal Phase 1 (start fresh)
6. RESUME:
   a. Load manifest.sections[]
   b. Identify sections with status "accepted" → mark as SKIP
   c. Identify sections with status "needs-more-info"|"extracted"|"error" → mark as PROCESS
   d. Set manifest status → "extracting" (if incomplete extraction)
                          or "validating" (if extraction complete, validation incomplete)
   e. Add event_log entry: {event: "resumed", timestamp: ISO8601, resumed_from: status}
   f. Update manifest.updated_at
   g. Continue from first incomplete section in current phase

NO MATCH (no resumable checkpoint found):
   → Proceed to Phase 1 (fresh session)

COMPLETE SESSION (status == "complete"):
   → Sessions with status "complete" are NOT resumable (BR-4)
   → Start fresh session
```

### Integration Points with Existing Phases

Phase 4 behaviors integrate into existing phases at these touchpoints:

| Integration Point | Phase 4 Behavior | Location in SKILL.md |
|-------------------|-----------------|----------------------|
| Skill invocation (before Phase 1) | **Resume detection**: scan for paused checkpoint | Before Step 1.1 — if resume detected, skip Phase 1 init |
| Step 1.4 — Initialize Handoff | **State machine**: status "initialized" → only valid next is "extracting" | Step 1.4 ACTION — manifest creation |
| Step 2.1 — Per-section extraction | **Error wrap**: try/retry/log around each section's extraction action | Step 2.1 ACTION items 1–7 — wrap with error handler |
| Step 2.1 — After each section | **Checkpoint save**: persist manifest after section status update | Step 2.1 ACTION item 8 — already updates manifest |
| Step 2.1 — Status transition | **State machine**: "initialized" → "extracting" at Phase 2 start | Step 2.1 CONTEXT — status update |
| Step 3.1 — Per-section validation | **Error wrap**: try/retry/log around validation dispatch | Step 3.1 ACTION item 1 — wrap with error handler |
| Step 3.1 — After each iteration | **Checkpoint save**: persist manifest with validation results | Step 3.1 ACTION item 8 — already updates manifest |
| Step 3.1 — Status transition | **State machine**: "extracting" → "validating" | Step 3.1 CONTEXT — status update |
| User interruption (any point) | **Pause**: set status → "paused", preserve section states | Cross-cutting — Phase 2 or Phase 3 loop body |
| Step 5.2 — Complete | **State machine**: any → "complete" on successful finish | Step 5.2 ACTION — final status |

**Key principle:** Phase 4 does NOT add new sequential steps between Phase 3 and Phase 5. It adds **behavioral wrappers** and **pre-invocation logic** that augment existing phases.

### Line Budget Analysis

```
Current SKILL.md state:
  Total lines:            500 (exact count verified via wc -l)
  Phase 4 stub:           lines 328–331 (4 lines)
    Line 328: ### Phase 4: Future Implementation Stub
    Line 329: (blank)
    Line 330: **Phase 4 (明辨之):** Error handling & checkpoints — ...
    Line 331: (blank)

Phase 4 Step 4.1 proposed size (in SKILL.md):
  Phase 4 header:         2 lines  (### Phase 4: + blank)
  Step 4.1 header:        2 lines  (#### Step 4.1: + blank)
  CONTEXT block:          2 lines  (paragraph, compact)
  DECISION block:         5 lines  (header + 4 bullets)
  ACTION block:           5 lines  (header + 4 numbered items)
  VERIFY block:           4 lines  (header + 3 checkpoints)
  REFERENCE block:        2 lines
  Subtotal:               ~22 lines

Net change:               +22 - 4 (stub removed) = +18 lines
Projected total:          500 + 18 = 518 lines ⚠️ OVER 500 LIMIT by 18 lines

Resolution strategy — reclaim 18+ lines from existing content:

  a. Phase Definitions section (lines 146–172):
     - Phase 3 (lines 146–153): still says "🔜 NOT IMPLEMENTED"
       but Phase 3 IS implemented → compress to 2-line status
       (same format as Phase 1/2 definitions)
       Savings: ~6 lines (8 lines → 2 lines)
     - Phase 4 (lines 155–162): still says "🔜 NOT IMPLEMENTED"
       → update to match implemented format (2 lines)
       Savings: ~6 lines (8 lines → 2 lines)

  b. 🎯 Implemented Phases (lines 37–43):
     - Add Phase 4, update "NOT Yet Implemented" line
     - Net: ~0 lines (update in place)

  c. DoD section (lines 470–477):
     - Add Phase 4 DoD item (1 line)
     - Net: +1 line

  d. Output Result section (lines 401–466):
     - Add Phase 4 output fields (~3 lines for error_summary)
     - Net: +3 lines

  e. Execution Flow table (lines 104–112):
     - Update Phase 4 status from "🔜" to "✅"
     - Net: 0 lines (in-place edit)

  Total reclaim:          ~12 lines from (a)
  Total additions:        +4 lines from (c, d)
  Net reclaim:            ~8 lines

  Remaining deficit:      18 - 8 = 10 lines still over

  Additional compression:
  f. Step 5.1 stub (lines 336–343):
     Currently 8 lines for a placeholder → compress to 3 lines
     Savings: ~5 lines

  g. Step 5.2 CONTEXT block (lines 349–356):
     Lists Phase 1+2 verification items redundantly → compress
     Savings: ~3 lines

  h. Step 6.1/6.2 (lines 380–398):
     Two steps with minimal content → compress to single block
     Savings: ~4 lines

  Total additional:       ~12 lines from (f, g, h)
  Grand total reclaim:    8 + 12 = ~20 lines

  Final projection:       500 + 18 (Phase 4) + 4 (updates) - 20 (reclaimed)
                        = 502 lines ≈ 500 target ✅

Recommended approach:
  1. Write Phase 4 content (~22 lines, reference-heavy)
  2. Compress Phase Definitions (save ~12 lines)
  3. Compress Phase 5.1 stub (save ~5 lines)
  4. Compress Phase 6 steps (save ~4 lines)
  5. Add Phase 4 fields to Output Result and DoD (+4 lines)
  6. Target: ≤ 503 lines (within acceptable tolerance)
```

### Additional SKILL.md Updates Required

Beyond the Phase 4 step replacement, these sections must be updated:

| Section | Current State | Required Update |
|---------|--------------|-----------------|
| Frontmatter (line 16) | `Feature: FEATURE-050-C` | → `Feature: FEATURE-050-D` |
| Version (line 16) | `Version: 1.2.0` | → `Version: 1.3.0` |
| 🎯 Implemented Phases (line 43) | Phase 4 listed as "NOT Yet Implemented" | → Add ✅ Phase 4, update NOT list |
| Execution Flow table (line 110) | Phase 4: `FEATURE-050-D 🔜` | → `FEATURE-050-D ✅` |
| Phase 3 Definition (lines 146–153) | `🔜 NOT IMPLEMENTED` (8 lines) | → Implemented status (2 lines) |
| Phase 4 Definition (lines 155–162) | `🔜 NOT IMPLEMENTED` (8 lines) | → Implemented status (2 lines) |
| Output Result (lines 401–466) | No Phase 4 fields | → Add `checkpoint_summary` fields |
| DoD (lines 470–477) | No Phase 4 checkpoint | → Add Phase 4 DoD item |

### Output Result Phase 4 Additions

```yaml
# Add after validation_summary (line ~462) in Output Result:
checkpoint_summary:
  resumed: bool                      # true if session was resumed from checkpoint
  resumed_from: "string | null"      # session path if resumed
  errors_total: int                  # count of error_log[] entries
  sections_error: int                # sections with final status "error"
  sections_skipped: int              # sections with final status "skipped"
```

### DoD Phase 4 Addition

```markdown
- [ ] **Phase 4 Active:** Checkpoint saves after each section, resume detection works, error classification + retry operational
```

### Implementation Sequence

Step-by-step order of edits to implement FEATURE-050-D:

```
Step 1: Create reference file
  → .github/skills/.../references/checkpoint-error-heuristics.md
  → Contains: state machine, resume algorithm, error classification,
    retry strategy, error_log schema, corruption handling, integration points,
    edge cases (no line limit)

Step 2: Replace Phase 4 stub in SKILL.md (lines 328–331)
  → Delete: "### Phase 4: Future Implementation Stub" block
  → Insert: Phase 4 Step 4.1 content (~22 lines)

Step 3: Compress Phase Definitions section (lines 146–162)
  → Compress Phase 3 definition from 8 → 2 lines (update to implemented)
  → Compress Phase 4 definition from 8 → 2 lines (update to implemented)
  → Save ~12 lines

Step 4: Update metadata sections
  → Frontmatter: Version 1.2.0 → 1.3.0, Feature → FEATURE-050-D
  → 🎯 Implemented Phases: add Phase 4, update NOT list
  → Execution Flow table: Phase 4 status → ✅

Step 5: Add Phase 4 fields to Output Result
  → Add checkpoint_summary block (~5 lines)

Step 6: Add Phase 4 DoD item
  → Add 1 line to Definition of Done

Step 7: Compress Phase 5.1 stub + Phase 6 (reclaim ~9 lines)
  → Phase 5.1: 8 lines → 3 lines
  → Phase 6.1/6.2: compress redundant blocks

Step 8: Verify line count
  → Target: ≤ 503 lines (500 ± 3 tolerance)
  → Run: wc -l SKILL.md

Step 9: Validate coherence
  → Phase 4 step references reference file correctly
  → State machine diagram in reference matches transition table
  → error_log schema matches AC-050D-13
  → Resume algorithm matches AC-050D-06 through AC-050D-09
  → All 21 ACs traceable to deliverables
```

### Acceptance Criteria Traceability

| Design Component | ACs Covered |
|-----------------|-------------|
| CheckpointPersister (section-level save) | AC-050D-01, AC-050D-03 |
| Manifest schema enforcement (schema_version, status) | AC-050D-02, AC-050D-04 |
| Pause trigger + status transition | AC-050D-05 |
| ResumeDetector (auto-detect by timestamp desc) | AC-050D-06, AC-050D-08 |
| Resume logic (skip accepted sections) | AC-050D-07 |
| Resume event_log + updated_at | AC-050D-09 |
| RetryController (transient → retry, max 2) | AC-050D-10 |
| Retry exhaustion → error + error_log | AC-050D-11 |
| Permanent error → immediate error, no retry | AC-050D-12 |
| error_log[] schema (5 required fields) | AC-050D-13 |
| Fail-open per section (continue on error) | AC-050D-14 |
| RecoveryDecider — DAO mode (autonomous) | AC-050D-15 |
| RecoveryDecider — Manual mode (human prompt) | AC-050D-16 |
| "Skip" recovery action | AC-050D-17 |
| CorruptionHandler — detection rules | AC-050D-18 |
| CorruptionHandler — fresh start + warning | AC-050D-19 |
| StateMachineEnforcer — valid transitions | AC-050D-20 |
| StateMachineEnforcer — reject invalid + log | AC-050D-21 |

### Edge Cases & Error Handling

| Edge Case | Expected Behavior | AC Reference |
|-----------|-------------------|--------------|
| No existing checkpoint for target | Start fresh extraction (Phase 1) | AC-050D-06 (no match path) |
| Multiple paused sessions for same target | Resume most recent by timestamp | AC-050D-08 |
| All sections fail with errors | Session status → "error", error_log contains all entries | AC-050D-04, AC-050D-14 |
| Checkpoint folder deleted mid-extraction | Treat as fresh start on next invocation | spec edge case |
| Resume after tool skill updated | Use current tool skill version (no version pinning in v1) | spec edge case |
| LLM API returns empty response | Classify as transient, retry up to max | spec edge case |
| Manifest has unknown fields (future version) | Ignore unknown fields, preserve on write (forward compat) | spec edge case |
| Session with status "complete" | NOT resumable — start fresh (BR-4) | AC-050D-06 (filter excludes complete) |
| Corrupted manifest (invalid YAML) | Log warning, start fresh | AC-050D-18, AC-050D-19 |
| Corrupted manifest (wrong schema_version) | Log warning, start fresh | AC-050D-18, AC-050D-19 |
| Invalid state transition attempted | Reject transition, log warning | AC-050D-21 |
| Transient error on retry attempt 3 | Mark section "error" (exhausted), continue | AC-050D-11, AC-050D-14 |
| Permanent error in DAO mode | Autonomous skip/halt decision | AC-050D-15 |
| Permanent error in manual mode | Surface to human with options | AC-050D-16 |

### New Reference File Location

```
.github/skills/x-ipe-task-based-application-knowledge-extractor/
├── SKILL.md
├── references/
│   ├── input-detection-heuristics.md       # existing (FEATURE-050-A)
│   ├── handoff-protocol.md                 # existing (FEATURE-050-A)
│   ├── category-taxonomy.md                # existing (FEATURE-050-A)
│   ├── examples.md                         # existing (FEATURE-050-A)
│   ├── extraction-engine-heuristics.md     # existing (FEATURE-050-B)
│   ├── validation-loop-heuristics.md       # existing (FEATURE-050-C)
│   └── checkpoint-error-heuristics.md      # NEW (FEATURE-050-D)
└── templates/
    ├── checkpoint-manifest.md              # existing (FEATURE-050-A)
    └── input-analysis-output.md            # existing (FEATURE-050-A)
```

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 2026-03-17 | Initial Design | Technical design for Checkpoint, Resume & Error Handling (Phase 4). Defines Step 4.1 cross-cutting structure with CONTEXT/DECISION/ACTION/VERIFY pattern. Key components: ResumeDetector (auto-detect paused checkpoint by timestamp desc), CheckpointPersister (section-level manifest saves), ErrorClassifier (2-tier: transient→retry, permanent→halt), RetryController (immediate retry, max 2, 3 total), RecoveryDecider (DAO-autonomous or human-prompted), StateMachineEnforcer (6 states, 12 valid transitions, reject invalid), CorruptionHandler (YAML parse + schema_version check, fresh start on fail). Line budget: +18 lines for Phase 4 step, reclaim ~20 lines via Phase Definition compression + stub reduction = target ≤503 lines. New reference file `checkpoint-error-heuristics.md` holds all detailed logic. Design decisions: section-level checkpoint granularity, auto-detect resume by timestamp, 2-tier error classification, immediate retry (no backoff), fail-open per section, append-only error_log[], log-once-on-exhaustion. |
