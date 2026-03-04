# FEATURE-036-C: Stage Ribbon & Action Execution — Acceptance Test Cases

## Execution Summary

| Metric | Value |
|--------|-------|
| Total Test Cases | 14 |
| Passed | 14 |
| Failed | 0 |
| Pass Rate | 100% |
| Executed By | Spark (Agent) |
| Execution Date | 2026-02-17 |
| Environment | http://localhost:5858 via Chrome DevTools MCP |

---

## Test Cases

### TC-001: Stage Ribbon Renders in Expanded Panel
**ACs Covered:** AC-001, AC-002
**Steps:** Navigate to Workflow view → Click workflow panel to expand
**Expected:** Stage ribbon appears with 5 stages separated by › arrows
**Result:** ✅ PASS — Ribbon shows: Ideation › Requirement › Implement › Validation › Feedback

### TC-002: Stage Visual States — New Workflow
**ACs Covered:** AC-003, AC-004, AC-024
**Steps:** Create new workflow → Expand panel → Inspect stage pill CSS classes
**Expected:** Ideation=active (pulsing dot), others=locked (🔒, opacity 0.5)
**Result:** ✅ PASS — `stage-item active` for Ideation, `stage-item locked` with opacity 0.5 for others

### TC-003: Stage Visual States — Completed + Active
**ACs Covered:** AC-003, AC-004
**Steps:** Complete ideation mandatory actions → Re-expand panel
**Expected:** Ideation=completed (✓), Requirement=active, others=locked
**Result:** ✅ PASS — `stage-item completed` with ✓, `stage-item active` with pulsing dot

### TC-004: Stage Ribbon Updates on Re-render
**ACs Covered:** AC-005
**Steps:** Mark action done via API → Collapse and re-expand panel
**Expected:** Button states update (done=green, new suggested action highlighted)
**Result:** ✅ PASS — Compose Idea changed from `suggested` to `done`, Refine Idea became `suggested`

### TC-005: Action Group Labels
**ACs Covered:** AC-007, AC-008, AC-009
**Steps:** Expand workflow with completed ideation + active requirement
**Expected:** "COMPLETED ACTIONS", "REQUIREMENT ACTIONS", "IMPLEMENT ACTIONS — complete Requirement to unlock"
**Result:** ✅ PASS — Labels match mockup pattern exactly

### TC-006: Action Button Visual States
**ACs Covered:** AC-010, AC-012
**Steps:** Expand workflow → Inspect button CSS classes and animations
**Expected:** done=green, suggested=amber dashed border + gentle-glow, normal=gray, locked=not-allowed
**Result:** ✅ PASS — `action-btn done/suggested/normal/locked` classes applied; `gentle-glow` animation on suggested

### TC-007: Action-to-Skill Mapping Completeness
**ACs Covered:** AC-011, AC-013
**Steps:** Expand panel → Verify all action buttons have correct emoji icons and names
**Expected:** 12 actions across 5 stages with correct icons (📝🎨💡🖼📋🔀📐⚙💻✅📊🔄)
**Result:** ✅ PASS — All icons and labels match the mapping table. Verified via unit tests (27/27 pass).

### TC-008: Locked Button Toast
**ACs Covered:** AC-018, AC-025
**Steps:** Click a locked action button (e.g., Requirement Gathering when stage is locked)
**Expected:** Toast: "Complete previous stages to unlock {action}"
**Result:** ✅ PASS — Toast shown with correct message, button has `cursor: not-allowed`

### TC-009: Done Button Toast
**ACs Covered:** AC-018
**Steps:** Click an action button with "done" status
**Expected:** Toast: "{Action} is already completed"
**Result:** ✅ PASS — Toast "Compose Idea is already completed" shown

### TC-010: CLI Action Dispatch
**ACs Covered:** AC-015, AC-016
**Steps:** Click "Reference UIUX" (CLI action) → Observe console
**Expected:** Console opens, skill name typed into session (no Enter pressed)
**Result:** ✅ PASS — Console became visible, `sendCopilotPromptCommandNoEnter` called successfully

### TC-011: Compose Idea Modal Prompt
**ACs Covered:** AC-019, AC-020, AC-021
**Steps:** Click "Compose Idea" on workflow without idea_folder → Enter folder name
**Expected:** Custom modal prompt (not browser native) appears asking for folder name → POST /api/workflow/{name}/link-idea called
**Result:** ✅ PASS — Custom `workflow-modal` appeared with input, OK/Cancel buttons. API called correctly.

### TC-012: Delete Confirm Modal
**ACs Covered:** (FEATURE-036-B regression — native confirm replaced)
**Steps:** Click ⋮ → Delete → Observe modal
**Expected:** Custom confirm modal with "Delete workflow '...'" heading, "This cannot be undone." message, Cancel/Delete buttons
**Result:** ✅ PASS — Custom modal with red Delete button, Cancel closes without action

### TC-013: Locked Button Tooltip
**ACs Covered:** AC-026
**Steps:** Hover/inspect locked action buttons → Check title attribute
**Expected:** title="Complete previous stages to unlock this action"
**Result:** ✅ PASS — All locked buttons have the correct tooltip text

### TC-014: Mockup Alignment
**ACs Covered:** AC-027, AC-028, AC-029
**Steps:** Compare actual UI screenshots with `workflow-view-v1.html` mockup
**Expected:** Horizontal stage pills with arrow separators, grid action buttons, state-based colors
**Result:** ✅ PASS — Layout matches: horizontal ribbon, grid actions, color-coded states (dark theme adapted from mockup's light theme)

---

## Screenshots

| Screenshot | Description |
|------------|-------------|
| `screenshots/stage-ribbon-expanded.png` | Initial stage ribbon with active + locked states |
| `screenshots/delete-confirm-modal.png` | Custom delete confirmation modal |
| `screenshots/final-with-labels.png` | Full view with COMPLETED/ACTIVE/LOCKED labels |
| `screenshots/actual-with-stages.png` | Workflow with completed ideation + active requirement |
| `screenshots/mockup-reference.png` | Mockup reference for comparison |

---

## Notes

- All native browser popups (`confirm()`, `prompt()`) replaced with custom `workflow-modal` modals per user feedback
- Dark theme colors adapted from mockup's light theme design system
- Quality Evaluation action renders as locked with "Coming Soon" tooltip (deferred to v2)
- AC-014 (verify action allowed before dispatch): Implementation checks status client-side from already-fetched state rather than making a separate API call — functionally equivalent
- AC-017 (no idle session toast): Covered by code path but not directly testable since terminal manager is always available in the test environment
- AC-022/AC-023 (workplace opens after idea link): Code path verified; full integration requires valid idea folder in project workspace

---

## CR-001: Action Running State Test Cases (v1.1)

> Added: 03-04-2026 | CR: [CR-001](x-ipe-docs/requirements/EPIC-036/FEATURE-036-C/CR-001.md)

### CR-001 Summary

| Metric | Value |
|--------|-------|
| Total Test Cases | 6 |
| Passed | 6 |
| Failed | 0 |
| Pass Rate | 100% |

### TC-CR-001: Action button remains clickable during execution (AC-030) — P0

**Status:** ✅ Pass — Clicked "Reference UIUX" button, click handler fired, `.running` class added. No `pointer-events: none` blocking.

### TC-CR-002: Running action displays pulse-ring animation (AC-031) — P0

**Status:** ✅ Pass — After click, button class became `action-btn optional running`. CSS `::after` pseudo with `border: 2px solid #38bdf8` and `animation: action-running-pulse 1.5s` confirmed via stylesheet inspection.

### TC-CR-003: Running state tracked client-side, resets on refresh (AC-032) — P0

**Status:** ✅ Pass — `_runningActions` is a Set, contained `reference_uiux` after click (size=1). After page refresh, `_runningActions.size` returned 0 and zero `.action-btn.running` elements found.

### TC-CR-004: Multiple actions can run simultaneously (AC-033) — P1

**Status:** ✅ Pass — Clicked "Refine Idea" then "Design Mockup". Both got `.running` class. `_runningActions` contained `['refine_idea', 'design_mockup']` (size=2). Both showed pulse-ring animation simultaneously.

### TC-CR-005: Running CSS rules exist in stylesheet (AC-031, UIR-007) — P1

**Status:** ✅ Pass — `.action-btn.running` ✓, `.action-btn.running::after` ✓, `@keyframes action-running-pulse` ✓. No `pointer-events: none` on `.running` or `.in-progress` rules.

### TC-CR-006: Only locked buttons block clicks (AC-030, AC-014) — P2

**Status:** ✅ Pass — Locked "Requirement Gathering" button has `cursor: not-allowed`, clicking it showed toast, did NOT add `.running`. Normal "Reference UIUX" button has `cursor: pointer` and is clickable.
