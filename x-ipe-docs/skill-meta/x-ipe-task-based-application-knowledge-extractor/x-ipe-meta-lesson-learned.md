---
skill: x-ipe-task-based-application-knowledge-extractor
created: 2026-03-17
last_updated: 2026-03-17
---

# Lessons Learned — x-ipe-task-based-application-knowledge-extractor

---

## LL-001

| Field | Value |
|-------|-------|
| **ID** | LL-001 |
| **Date** | 2026-03-17 |
| **Severity** | major |
| **Source** | human_feedback |
| **Status** | raw |
| **Task** | TASK-949 |
| **Scenario** | User ran a full knowledge extraction and observed screenshots saved to wrong location and no session cleanup |

### Observed Behavior

1. **Screenshots saved to flat folder:** Screenshots captured during extraction (e.g., via Chrome DevTools) were saved directly under `.x-ipe-checkpoint/screenshots/` with no session isolation. Multiple concurrent extractions would collide.
2. **No session cleanup:** After generation completed, the `.x-ipe-checkpoint/` session data (screenshots, manifests, intermediate files) was left behind. The checkpoint folder accumulated stale data across runs.

### Expected Behavior

1. **Session-scoped screenshots:** Screenshots should be stored in session-specific subfolders: `.x-ipe-checkpoint/screenshots/{session-id}/` (where `{session-id}` is the extraction_id or equivalent). This prevents collisions between concurrent extractions and makes cleanup trivial.
2. **Post-generation cleanup:** After the extraction completes successfully (all phases done, intake folder populated), the skill should clean up its session data from `.x-ipe-checkpoint/`. Specifically: remove `.x-ipe-checkpoint/screenshots/{session-id}/`, `.x-ipe-checkpoint/manifest.md`, and any other session-specific artifacts.

### Ground Truth

```
Screenshot storage path:
  .x-ipe-checkpoint/screenshots/{extraction_id}/screenshot-001.png
  .x-ipe-checkpoint/screenshots/{extraction_id}/screenshot-002.png

Cleanup trigger: After Phase 5 (quality scoring) completes and intake folder is finalized.
Cleanup scope: All files under .x-ipe-checkpoint/ that belong to the current session.
Cleanup method: Remove session subfolder and session-specific manifests.
Exception: Do NOT clean up if extraction failed — preserve for debugging.
```

### Proposed Improvements

**Improvement 1: Session-scoped screenshot storage**
- **Type:** update_instruction
- **Target:** `references/execution-procedures.md` — Phase 2 (Study Broadly) screenshot capture steps; `references/handoff-protocol.md` — checkpoint folder structure
- **Description:** Update screenshot save path from `.x-ipe-checkpoint/screenshots/` to `.x-ipe-checkpoint/screenshots/{extraction_id}/`. Update checkpoint manifest template to reflect session subfolder. Update handoff-protocol to document the session-scoped structure.
- **Proposed AC:**
  - id: AC-NEW-1
  - description: "Screenshots are stored in session-specific subfolder under .x-ipe-checkpoint/screenshots/{extraction_id}/"
  - test_method: path_validation
  - expected: "No screenshots exist directly under .x-ipe-checkpoint/screenshots/"

**Improvement 2: Post-generation cleanup**
- **Type:** new_ac
- **Target:** `SKILL.md` — Execution Flow (add cleanup phase or final step); `references/execution-procedures.md` — add cleanup step after Phase 5
- **Description:** Add a cleanup step that runs after successful extraction completion. Remove all session-specific files from `.x-ipe-checkpoint/`. Skip cleanup on failure to preserve debug artifacts.
- **Proposed AC:**
  - id: AC-NEW-2
  - description: "Skill cleans up .x-ipe-checkpoint/ session data after successful completion"
  - test_method: post_execution_check
  - expected: "No session-specific files remain in .x-ipe-checkpoint/ after success; files preserved on failure"
