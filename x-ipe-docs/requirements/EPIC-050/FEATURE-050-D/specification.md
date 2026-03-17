# Feature Specification: Checkpoint, Resume & Error Handling

> Feature ID: FEATURE-050-D
> Epic ID: EPIC-050
> Version: v1.0
> Status: Refined
> Last Updated: 03-17-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-17-2026 | Initial specification |

## Linked Mockups

N/A — this feature has no UI component. It is a pure skill-layer feature.

## Overview

FEATURE-050-D implements Phase 4 (明辨之 — Discern Clearly) of the application knowledge extractor skill. Building on the foundation (Phase 1), extraction (Phase 2), and validation (Phase 3), this feature adds checkpoint persistence, resume-from-pause capability, and error handling with retry logic.

The extractor already creates a `.checkpoint/session-{timestamp}/` folder with a `manifest.yaml` tracking extraction state. Phase 4 makes this checkpoint actionable: the agent can pause extraction mid-session (writing checkpoint state), resume from the most recent paused checkpoint (auto-detecting it), and handle errors with a 2-tier classification (transient → retry, permanent → halt/log).

This feature is critical for long-running extraction sessions where interruptions (network issues, LLM API errors, user-initiated pauses) must not lose progress.

## User Stories

1. As an **AI agent**, I want the extractor to **automatically save checkpoint state after each section extraction**, so that **progress is never lost if extraction is interrupted**.

2. As an **AI agent**, I want to **resume extraction from a paused checkpoint**, so that **I don't have to re-extract sections that were already completed**.

3. As an **AI agent**, I want **transient errors to be retried automatically** (up to 2 retries), so that **temporary LLM API hiccups don't block extraction**.

4. As an **AI agent**, I want **permanent errors to be logged and the section marked as error**, so that **extraction continues for other sections while failures are documented**.

5. As a **human user**, I want to **see a clear error log in the manifest**, so that **I can understand what went wrong and decide next steps**.

## Acceptance Criteria

### Group 1: Checkpoint Persistence

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050D-01 | GIVEN extraction is in progress WHEN a section extraction completes successfully THEN manifest.yaml is updated with the section's status, content_file, and updated_at timestamp before proceeding to the next section | Structured-Review |
| AC-050D-02 | GIVEN the manifest.yaml exists WHEN reading it after any successful section THEN schema_version is "1.0" and all completed sections have status "accepted" or "needs-more-info" with valid content_file paths | Structured-Review |
| AC-050D-03 | GIVEN extraction is running WHEN the SKILL.md Phase 4 procedure is followed THEN the checkpoint save happens at section-level granularity (not only at phase boundaries) | Structured-Review |
| AC-050D-04 | GIVEN a checkpoint is being saved WHEN writing manifest.yaml THEN the overall session status field reflects the current state (extracting, validating, paused, complete, error) | Structured-Review |

### Group 2: Pause & Resume

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050D-05 | GIVEN extraction is in progress WHEN a pause is triggered (user-initiated or error-induced) THEN manifest status transitions to "paused" and all in-progress sections are marked with their last known state | Structured-Review |
| AC-050D-06 | GIVEN a paused checkpoint exists in .checkpoint/ WHEN the extractor is invoked with the same target THEN it auto-detects the most recent paused checkpoint by scanning session-{timestamp} folders sorted by timestamp descending | Structured-Review |
| AC-050D-07 | GIVEN a paused checkpoint is detected WHEN resuming THEN only sections not yet completed are extracted; already-accepted sections are skipped | Structured-Review |
| AC-050D-08 | GIVEN multiple checkpoint sessions exist WHEN auto-detecting THEN the most recent session with status "paused" or "extracting" is selected | Structured-Review |
| AC-050D-09 | GIVEN a checkpoint is resumed WHEN extraction continues THEN the manifest updated_at timestamp is refreshed and a resume entry is added to the manifest's event_log | Structured-Review |

### Group 3: Error Classification & Retry

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050D-10 | GIVEN a transient error occurs during section extraction (e.g., LLM API timeout, temporary file lock) WHEN the error is caught THEN the extractor retries immediately up to 2 times (3 total attempts) | Structured-Review |
| AC-050D-11 | GIVEN all retry attempts are exhausted WHEN the error persists THEN the section is marked status "error" in the manifest and the error is logged to error_log[] | Structured-Review |
| AC-050D-12 | GIVEN a permanent error occurs (e.g., file not found, permission denied, unsupported format) WHEN the error is caught THEN no retries are attempted and the section is immediately marked "error" | Structured-Review |
| AC-050D-13 | GIVEN an error is logged WHEN reading error_log[] in manifest THEN each entry contains: section_id, error_type (transient/permanent), message, retry_count, timestamp | Structured-Review |
| AC-050D-14 | GIVEN a section fails with error WHEN other sections remain THEN extraction continues for remaining sections (fail-open per section, not per session) | Structured-Review |

### Group 4: Error Recovery Decisions

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050D-15 | GIVEN interaction_mode is "dao-represent-human-to-interact" WHEN a permanent error occurs THEN the agent autonomously decides recovery (skip section, adjust parameters, or halt) via DAO without human intervention | Structured-Review |
| AC-050D-16 | GIVEN interaction_mode is "interact-with-human" or "stop_for_question" WHEN a permanent error occurs THEN the agent surfaces the error to the human with options: skip section, provide alternative source, or abort | Structured-Review |
| AC-050D-17 | GIVEN a recovery decision is made WHEN the decision is "skip" THEN the section status is set to "skipped" and extraction proceeds to the next section | Structured-Review |

### Group 5: Checkpoint Corruption

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050D-18 | GIVEN a checkpoint manifest exists WHEN it fails YAML parsing or schema_version doesn't match "1.0" THEN it is classified as corrupted | Structured-Review |
| AC-050D-19 | GIVEN a corrupted checkpoint is detected WHEN attempting to resume THEN the extractor starts a fresh session and logs a warning: "Corrupted checkpoint detected at {path}, starting fresh session" | Structured-Review |

### Group 6: Manifest State Machine

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050D-20 | GIVEN the manifest status field WHEN tracking state transitions THEN only these transitions are valid: initialized→extracting, extracting→validating, extracting→paused, validating→paused, paused→extracting, paused→validating, any→error, any→complete | Structured-Review |
| AC-050D-21 | GIVEN the SKILL.md Phase 4 procedure WHEN defining the state machine THEN invalid transitions are explicitly rejected with a logged warning | Structured-Review |

## Functional Requirements

**FR-1: Section-Level Checkpoint Save**
- Input: Completed section extraction result (content_file, status, metadata)
- Process: Update manifest.yaml section entry with final status, set updated_at, write to disk
- Output: Persisted manifest reflecting current extraction progress

**FR-2: Auto-Detect Resume**
- Input: Target path/URL (same as original extraction)
- Process: Scan `.checkpoint/` for `session-*/manifest.yaml`, filter by status in {paused, extracting}, sort by timestamp descending, select most recent
- Output: Restored session state with list of remaining sections to process

**FR-3: 2-Tier Error Classification**
- Input: Exception/error from extraction or validation step
- Process: Classify as transient (retry-eligible: timeout, rate limit, temp lock) or permanent (no retry: not found, permission denied, unsupported). Transient → immediate retry (max 2). Permanent → log and mark error.
- Output: Section marked with final status; error_log[] entry appended

**FR-4: Interaction-Mode-Aware Recovery**
- Input: Permanent error + current interaction_mode
- Process: If DAO mode → autonomous decision. If manual mode → surface to human with options.
- Output: Recovery action (skip, adjust, halt) applied to session

## Non-Functional Requirements

**NFR-1: Checkpoint Overhead** — Manifest write must not add perceptible delay (< 100ms per section save).

**NFR-2: Idempotent Resume** — Resuming from the same checkpoint twice produces identical behavior (no duplicate content files).

**NFR-3: Graceful Degradation** — Corrupted checkpoint = fresh start (no crash, no partial state leakage).

## Dependencies

### Internal
- **FEATURE-050-A** (✅ Implemented) — Foundation, `.checkpoint/` folder structure, manifest.yaml template
- **FEATURE-050-B** (✅ Implemented) — Phase 2 extraction (produces content files that checkpoints track)
- **FEATURE-050-C** (✅ Implemented) — Phase 3 validation (produces feedback files; checkpoint must track validation state too)

### External
- None

## Business Rules

**BR-1:** Checkpoint save is mandatory after each section — no "batch at end" option.

**BR-2:** Maximum 2 retries for transient errors (3 total attempts). This is configurable via `config_overrides.max_retries` (default: 3, meaning 3 total attempts).

**BR-3:** The `error_log[]` array in manifest is append-only — errors are never removed, only added.

**BR-4:** A session with status "complete" cannot be resumed — only "paused" or "extracting" sessions are resumable.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| No existing checkpoint for target | Start fresh extraction (Phase 1) |
| Multiple paused sessions for same target | Resume most recent by timestamp |
| All sections fail with errors | Session status → "error", error_log contains all entries |
| Checkpoint folder deleted mid-extraction | Treat as fresh start on next invocation |
| Resume after tool skill updated | Use current tool skill version (no version pinning in v1) |
| LLM API returns empty response | Classify as transient, retry up to max |
| Manifest has unknown fields (future version) | Ignore unknown fields, preserve them on write (forward compatibility) |

## Out of Scope

- GUI/UI for error prompts or checkpoint management
- Automatic recovery from corrupted content files (only manifest corruption is handled)
- Cross-machine checkpoint sharing or syncing
- Version migration (schema_version "1.0" → "2.0" upgrade path)
- Checkpoint compression or archival

## Technical Considerations

- Phase 4 content in SKILL.md must be ultra-concise (~20 lines) with details in a reference file (`references/checkpoint-error-heuristics.md`)
- The manifest.yaml already has `status`, `sections[]`, and `error_log[]` fields — Phase 4 operationalizes them
- State machine transitions should be documented in the reference file, not in SKILL.md
- Resume detection uses filesystem glob on `.checkpoint/session-*/manifest.yaml`

## Open Questions

None — all design questions resolved via DAO-110 (see `x-ipe-docs/dao/26-03-17/decisions_made_feature_refinement.md`).
