# Acceptance Test Cases

> Feature: FEATURE-060-A — CR Assessment UI/UX and Case Service  
> Generated: 2026-07-22  
> Status: Re-executed — Automated Gaps Resolved; Browser Verification Blocked

## Overview

| Attribute | Value |
|---|---|
| Specification | [specification.md](x-ipe-docs/requirements/EPIC-060/FEATURE-060-A/specification.md) |
| Technical design | [technical-design.md](x-ipe-docs/requirements/EPIC-060/FEATURE-060-A/technical-design.md) |
| Current mockup | [cr-assessment-view-v1.html](x-ipe-docs/requirements/EPIC-060/FEATURE-060-A/mockups/cr-assessment-view-v1.html) |
| Target URL | `http://127.0.0.1:5858/cr-assessment` |
| Stack | Flask/Python, HTML5/CSS3, vanilla JavaScript |
| Test data | Generated local defaults; temporary directories and in-memory uploads |

## Enabled Tools

`tools.json` enables Chrome DevTools MCP, the Chrome UI-testing skill, and the Python/HTML5 implementation skills. Browser-only execution requires Chrome DevTools MCP; it must not be substituted by another browser driver.

## Frontend-UI Tests

| TC | AC coverage | Priority | Selectors and steps | Expected outcome | Assigned tool | Status |
|---|---|---:|---|---|---|---|
| TC-UI-01 New case and required evidence | 01a, 03a, 03e, 03f, 05d | P0 | Open target; click `#cr-new-case`; inspect `#cr-case-form`, `[data-error]`, `#cr-readiness-list`, `#cr-estimate` | Empty form focuses Case Name; missing evidence is explicit; Estimation stays disabled; corrections preserve other fields | Chrome DevTools MCP | Blocked |
| TC-UI-02 Unsaved-change protection | 02e | P0 | Modify `#cr-case-name`; click a `.cr-case-card`; handle confirmation | Switching cannot silently discard edits | Chrome DevTools MCP | Blocked |
| TC-UI-03 Depth selection and evaluating lock | 04a, 04b, 04g | P0 | Open `#cr-estimate`; inspect `#cr-depth-menu`; choose `[data-depth="deep"]`; load Evaluating case | Three described depths appear, Standard defaults, selection remains visible, Evaluating inputs are disabled | Chrome DevTools MCP | Blocked |
| TC-UI-04 Case discovery | 05a, 05b, 05c, 05e, 05f | P0 | Use `#cr-search`; inspect `.cr-case-card`, selected state, header, loading transition | Search is case-insensitive; empty/no-result and selected/loading states are explicit; card shows required summary data | Chrome DevTools MCP | Blocked |
| TC-UI-05 Polling conflict and notification | 06d | P0 | Edit a field; simulate changed marker; inspect `#cr-alert` and `#cr-toast` | Local edits remain and an accessible warning is announced | Chrome DevTools MCP | Blocked |
| TC-UI-06 Report interactions | 07a, 07c, 07d, 07e, 07f | P0 | Open `#cr-tab-report`; use `#cr-prev-slide`, `#cr-next-slide`, `#cr-slide-dots`, arrow keys, disclosure; test no-report case | Correct report/empty state, slide state and accessible disclosure behavior | Chrome DevTools MCP | Blocked |
| TC-UI-07 Desktop and tablet fidelity | 08a, 08b, 08c, 08e | P1 | Compare app at 1280×720 and 900×800 with current mockup | Required hierarchy and two-column desktop relationship remain; tablet has no page-level horizontal scroll; state meaning is not color-only | Chrome DevTools MCP | Blocked |
| TC-UI-08 Mobile adaptation | 08d | P1 | Render at 390×844; activate `#cr-mobile-list` | Single-primary-pane layout retains all actions and case discovery | Chrome DevTools MCP | Blocked |
| TC-UI-09 Keyboard and semantics | 09a, 09b, 09c, 09d, 09f | P0 | Traverse controls; operate `role=tablist` with arrows/Home/End/Enter/Space; inspect live regions and target sizes | Logical keyboard order, visible focus, WAI-ARIA tab relationship, live announcements and ≥24px compact targets | Chrome DevTools MCP | Blocked |
| TC-UI-10 Contrast | 09e | P1 | Measure computed foreground/background pairs in primary states | Normal text and controls meet WCAG 2.1 AA | Chrome DevTools MCP | Blocked |

## Backend-API and Integration Tests

| TC | AC coverage | Priority | Endpoint/service reference and generated data | Expected outcome | Assigned tool | Status |
|---|---|---:|---|---|---|---|
| TC-API-01 Case lifecycle and identity | 01b, 01c, 01d | P0 | `POST /api/cr-assessments`, `PUT /api/cr-assessments/{id}`; concurrent generated cases | Unique immutable `CR-YYYY-NNN` folders; rename never changes ID/folder | Python/pytest | Pass |
| TC-API-02 Evidence persistence and failure safety | 02a, 02b, 02c, 02d, 02f | P0 | Multipart create/update with byte fixtures and forced write/conflict errors | Fields and original bytes persist; prior valid record remains readable on failure | Python/pytest | Pass |
| TC-API-03 Path validation | 03b, 03d | P0 | `POST /api/cr-assessments/validate-path`; missing/file/unreadable/readable temp paths | Invalid paths have corrective reasons; readable directory is ready | Python/pytest | Pass |
| TC-API-04 Invocation transaction | 04c, 04d, 04e, 04f | P0 | `POST /api/cr-assessments/{id}/prepare` with each depth and failure fixtures | Auto-save and immutable snapshot precede Evaluating; command is populated, not executed; failure does not transition | Python/pytest | Pass |
| TC-API-05 Polling lifecycle | 06a, 06c, 06f, 06g | P0 | `POST /api/cr-assessments/changes`; changed/unchanged/malformed/recovery cases | Five-second-compatible marker contract returns only changes; failures are recoverable; Evaluating has no timeout | Python/pytest + Vitest | Pass |
| TC-API-06 Report history and missing files | 07b, 07g | P1 | Seed latest/history report metadata including a missing file; fetch case and preview links | Current and historical outputs remain reachable; missing file does not hide valid versions | Python/pytest + structured review | Pass |

## Unit Tests

| TC | AC coverage | Priority | Function/class reference | Expected outcome | Assigned tool | Status |
|---|---|---:|---|---|---|---|
| TC-UNIT-01 Local URL rejection | 03c | P0 | `CrAssessmentService.validate_codebase()` with HTTPS and SSH Git URLs | Remote repositories are rejected | Python/pytest | Pass |
| TC-UNIT-02 No-change polling and cleanup | 06b, 06e | P1 | `CrAssessmentView._poll()`, `CrAssessmentPoller`, `destroy()` | Unchanged response does not rerender; cleanup stops interval and listener | Vitest | Pass |

## Structured Review Tests

| TC | AC coverage | Priority | Review target | Expected outcome | Assigned tool | Status |
|---|---|---:|---|---|---|---|
| TC-REV-01 Complete AC implementation trace | All ACs | P1 | Specification ↔ template/JS/routes/services/tests | Every criterion has an implementation point or a documented gap | Agent structured review | Pass |

## Reflection Checklist

- Every AC sub-criterion from AC-060-A-01a through AC-060-A-09f maps to at least one TC.
- UI selectors use stable IDs, ARIA roles, or stable case-card attributes; no positional selector is required.
- API cases name the method and endpoint; unit cases name the callable under test.
- Generated data is local, disposable, non-sensitive, and independent per case.
- Dynamic UI checks require a fresh page snapshot after navigation or mutation.
- Tests continue after failures; browser-only cases become Blocked if the mandated MCP is unavailable.

## Test Execution Summary

| Type | Total | Passed | Failed | Blocked |
|---|---:|---:|---:|---:|
| Frontend UI | 10 | 0 | 0 | 10 |
| Backend API / Integration | 6 | 6 | 0 | 0 |
| Unit | 2 | 2 | 0 | 0 |
| Structured review | 1 | 1 | 0 | 0 |
| **Total** | **19** | **9** | **0** | **10** |

- Overall pass rate: **47.4%** (9/19); the remaining 10 cases are blocked, not failed.
- Executed, non-blocked pass rate: **100%** (9/9).
- Automated runner result: **29/29 underlying tests passed** (22 pytest + 7 Vitest).
- New Python component coverage: **83%** overall (codec 91%, service 84%, routes 70%).

## Execution Notes and Gaps

1. **Frontend execution blocked:** `tools.json` mandates Chrome DevTools MCP, but no Chrome DevTools MCP tools were available. Per the acceptance skill, no alternative browser driver was substituted.
2. **TC-API-02 resolved:** stale revisions are rejected before artifact storage, and stored supporting/vendor evidence is presented as named chips.
3. **TC-API-06 resolved:** current/history links remain available, report modules expose native accessible disclosures, and preview failure produces a local message without removing other versions.
4. **TC-UNIT-02 resolved:** unchanged marker responses return before list/detail rendering; cleanup still stops polling and removes its visibility listener.
5. **TC-REV-01 resolved:** case cards now include relative update time, selection exposes `aria-busy` and a loading heading, stored files are visible, and report disclosure/error states are implemented. Native button behavior supplies Enter/Space activation; formal contrast and responsive execution remain in the blocked browser group.

## Recommended Action

The executable and structured-review acceptance gates pass. Run the 10 blocked UI cases through the mandated Chrome DevTools MCP when it becomes available; do not declare fully verified visual/accessibility acceptance before that batch completes.
