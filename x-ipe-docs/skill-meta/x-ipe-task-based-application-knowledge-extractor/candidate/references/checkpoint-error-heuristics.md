# Checkpoint & Error Heuristics

> Reference for Phase 4 (明辨之) of Application Knowledge Extractor
> FEATURE-050-D | Version 1.0

## 1. Manifest State Machine

```
                    ┌──────────────┐
                    │ initialized  │
                    └──────┬───────┘
                           │ Phase 2 start
                    ┌──────▼───────┐
              ┌─────│  extracting  │─────┐
              │     └──────┬───────┘     │
         pause│            │ Phase 3     │ error
              │     ┌──────▼───────┐     │
              │ ┌───│  validating  │───┐ │
              │ │   └──────┬───────┘   │ │
              │ │pause     │ done  error│ │
              ▼ ▼          ▼           ▼ ▼
        ┌─────────┐  ┌──────────┐  ┌───────┐
        │ paused  │  │ complete │  │ error │
        └────┬────┘  └──────────┘  └───────┘
             │ resume
             └──────► extracting OR validating
```

### Valid Transitions

| From | To | Trigger |
|------|----|---------|
| initialized | extracting | Phase 2 begins |
| extracting | validating | All sections extracted, Phase 3 begins |
| extracting | paused | User interruption or error-induced pause |
| extracting | error | Unrecoverable failure during extraction |
| extracting | complete | Skip validation (edge case: no sections to validate) |
| validating | paused | User interruption or error-induced pause |
| validating | error | Unrecoverable failure during validation |
| validating | complete | All validation iterations done |
| paused | extracting | Resume — extraction was incomplete |
| paused | validating | Resume — extraction complete, validation incomplete |
| error | — | Terminal state (start fresh session for retry) |
| complete | — | Terminal state (not resumable per BR-4) |

### Invalid Transition Handling

If a transition is attempted that does not appear in the table above:
1. Log warning: `"Invalid state transition attempted: {from} → {to}, rejected"`
2. Keep current status unchanged
3. Continue execution (do not crash)

---

## 2. Resume Algorithm

### Detection (runs BEFORE Phase 1 Step 1.1)

```
1. SCAN:     Glob .x-ipe-checkpoint/session-*/manifest.yaml
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
   b. Identify sections with status "accepted" → SKIP
   c. Identify sections with status "needs-more-info"|"extracted"|"error" → PROCESS
   d. Set manifest status:
      → "extracting" (if sections still need extraction)
      → "validating" (if all extracted, validation incomplete)
   e. Add event_log entry: {event: "resumed", timestamp: ISO8601, resumed_from: previous_status}
   f. Update manifest.updated_at
   g. Continue from first incomplete section in current phase
```

### No Match

If no resumable checkpoint found → proceed to Phase 1 (fresh session).

### Complete Session

Sessions with status "complete" are NOT resumable (BR-4). Start fresh session.

---

## 3. Checkpoint Save Protocol

### When to Save

- **After each section extraction** (Phase 2 Step 2.1): update section status, content_file, files_read, warnings
- **After each section validation** (Phase 3 Step 3.1): update validation_status, feedback_file
- **On pause**: set overall status → "paused"
- **On error**: set section status → "error", append error_log[]

### What to Save

For each section in `manifest.sections[]`:
```yaml
- section_id: string
  slug: "string"
  status: "pending | extracted | accepted | needs-more-info | error | skipped"
  content_file: "content/section-{NN}-{slug}.md | null"
  validation_status: "accepted | needs-more-info | error | null"
  files_read: ["string"]
  warnings: ["string"]
  updated_at: "ISO 8601"
```

Overall manifest fields updated:
```yaml
status: "initialized | extracting | validating | paused | complete | error"
updated_at: "ISO 8601"
```

### Idempotency

Re-saving the same section is safe — manifest overwrites section entry with identical data. No duplicate content files are created.

---

## 4. Error Classification

### Transient Errors (retry-eligible)

| Error | Example | Retryable |
|-------|---------|-----------|
| LLM API timeout | Request exceeded timeout_seconds | ✅ |
| LLM rate limit | HTTP 429 from API | ✅ |
| Temporary file lock | OS file lock on read | ✅ |
| Empty LLM response | Model returned empty string | ✅ |
| Network transient | Connection reset, DNS timeout | ✅ |

### Permanent Errors (no retry)

| Error | Example | Retryable |
|-------|---------|-----------|
| File not found | Source file deleted or moved | ❌ |
| Permission denied | No read access to source | ❌ |
| Unsupported format | Binary file, encrypted content | ❌ |
| Schema mismatch | Checkpoint schema_version ≠ "1.0" | ❌ |
| Invalid configuration | Missing required config field | ❌ |

### Ambiguous Errors

If an error cannot be clearly classified, **default to transient** (retry is safer than immediate halt). If retries are exhausted, it becomes effectively permanent.

---

## 5. Retry Strategy

- **Method:** Immediate retry (no backoff in v1)
- **Max retries:** 2 (3 total attempts), from `config_overrides.max_retries` (default: 3)
- **Scope:** Per-section (retry only the failing section, not the entire phase)
- **On exhaustion:** Mark section status → "error", append to `error_log[]`, continue next section

### Retry Flow

```
attempt = 1
WHILE attempt <= max_retries:
    TRY: execute section extraction/validation
    ON SUCCESS: break (proceed normally)
    ON TRANSIENT ERROR:
        attempt += 1
        IF attempt > max_retries:
            → mark section "error"
            → append error_log[] entry (retry_count = max_retries - 1)
            → continue to next section
        ELSE:
            → retry immediately
    ON PERMANENT ERROR:
        → mark section "error"
        → append error_log[] entry (retry_count = 0)
        → continue to next section
```

---

## 6. error_log[] Schema

```yaml
error_log:                              # append-only array in manifest.yaml
  - section_id: string                  # "N-slug" format (matches sections[] entry)
    error_type: "transient | permanent" # 2-tier classification
    message: "string"                   # human-readable error description
    retry_count: int                    # 0 for permanent, 0-2 for transient
    timestamp: "ISO 8601"              # when error was logged
```

### Rules

- **Append-only:** Entries are never removed (BR-3)
- **Log once on exhaustion:** A section that fails 3 times gets 1 entry with `retry_count=2`
- **section_id** references the section's index in `manifest.sections[]`

### Example

```yaml
error_log:
  - section_id: "3-getting-started"
    error_type: "transient"
    message: "LLM API timeout after 15s — exhausted 2 retries"
    retry_count: 2
    timestamp: "2026-03-17T15:02:30Z"
  - section_id: "4-core-features"
    error_type: "permanent"
    message: "Source file not found: docs/TROUBLESHOOT.md"
    retry_count: 0
    timestamp: "2026-03-17T15:03:15Z"
```

---

## 7. Interaction-Mode-Aware Recovery

When a permanent error occurs after retry exhaustion:

### DAO Mode (`dao-represent-human-to-interact`)

The agent autonomously decides recovery without human intervention:
1. **Skip section** (default): Mark section "skipped", proceed to next
2. **Adjust parameters**: Modify extraction prompt and retry (counts as new attempt)
3. **Halt session**: Set status → "paused", stop extraction (rare — only if critical)

Decision criteria: If the section is optional (non-core) → skip. If core → attempt adjust. If multiple core sections fail → halt.

### Manual Mode (`interact-with-human` or `stop_for_question`)

Surface the error to the human with these options:
1. **Skip this section** — proceed without it
2. **Provide alternative source** — human gives a different path/URL
3. **Abort extraction** — halt and save checkpoint

---

## 8. Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No existing checkpoint for target | Start fresh extraction (Phase 1) |
| Multiple paused sessions for same target | Resume most recent by timestamp |
| All sections fail with errors | Session status → "error", error_log contains all entries |
| Checkpoint folder deleted mid-extraction | Treat as fresh start on next invocation |
| Resume after tool skill updated | Use current tool skill version (no version pinning) |
| LLM API returns empty response | Classify as transient, retry up to max |
| Manifest has unknown fields (future version) | Ignore unknown fields, preserve them on write |
| Concurrent extraction on same target | Not supported — second invocation creates new session |
| Pause during Phase 3 validation loop | Save iteration progress; resume continues from last iteration |

---

## 9. Integration Points with Existing Phases

| Integration Point | Phase 4 Behavior |
|-------------------|-----------------|
| Before Phase 1 Step 1.1 | Resume detection: scan for paused checkpoint |
| Step 1.4 (Initialize Handoff) | State machine: status "initialized" |
| Step 2.1 (Per-section extraction) | Error wrap: try/retry/log around each section |
| Step 2.1 (After each section) | Checkpoint save: persist manifest |
| Step 3.1 (Per-section validation) | Error wrap: try/retry/log around validation |
| Step 3.1 (After each iteration) | Checkpoint save: persist manifest |
| User interruption (any point) | Pause: status → "paused" |
| Step 5.2 (Complete) | State machine: any → "complete" |

**Key principle:** Phase 4 does NOT add new sequential steps between Phase 3 and Phase 5. It adds behavioral wrappers and pre-invocation logic that augment existing phases.
