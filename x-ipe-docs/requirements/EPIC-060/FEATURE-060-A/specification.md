# Feature Specification: CR Assessment UI/UX and Case Service

> Feature ID: FEATURE-060-A
> Epic ID: EPIC-060
> Version: v1.1
> Status: Refined
> Last Updated: 07-22-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 07-21-2026 | Initial refined specification for case management, Console prompt invocation, polling, and report preview |
| v1.1 | 07-22-2026 | Clarified that AI Court opens inside the existing X-IPE right-hand content area and preserves application chrome |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| CR Assessment View v1 | Interactive HTML | [cr-assessment-view-v1.html](x-ipe-docs/requirements/EPIC-060/FEATURE-060-A/mockups/cr-assessment-view-v1.html) | Authoritative split-view case list, information form, assessment-depth control, and CIO report preview | current | 07-21-2026 |

The current mockup defines the required information hierarchy, component relationships, and primary interactions. Example case values and estimated durations shown in the mockup are illustrative rather than product defaults or performance commitments.

## Overview

FEATURE-060-A provides the X-IPE user interface and case service for creating, maintaining, invoking, and viewing Change Request assessment cases. It delivers a minimum runnable case-management flow: users can preserve assessment evidence, select Quick, Standard, or Deep analysis, populate the existing X-IPE Console with the independent assessment command, and view reports published back into the case folder.

The feature deliberately contains no AI assessment intelligence. It owns the stable case-folder identity, user-entered inputs, immutable invocation snapshots, lifecycle presentation, prompt population, metadata polling, and report preview. FEATURE-060-B consumes this contract, performs AI reasoning, and updates `CaseRecord.html` through its bundled Python publisher.

Project Managers and Technical Leads are the primary interactive users. Vendors do not operate this module in v1; they receive the complete self-contained report bundle generated for a case.

## User Stories

1. **US-060-A-01 — Create Case:** As a Project Manager, I want to create a CR assessment case from the **New Assessment Case** control shown in the current mockup, so that all evidence and reports have one durable location.
2. **US-060-A-02 — Maintain Inputs:** As a Project Manager, I want to enter or update CR details, Vendor estimates, supporting files, and comments in the mockup-aligned information form, so that the assessment uses complete evidence.
3. **US-060-A-03 — Select Repository:** As a Technical Lead, I want to choose and validate a readable local codebase folder using the path field and Browse control, so that the skill can inspect the correct baseline.
4. **US-060-A-04 — Find Cases:** As a Project Manager, I want to search the case rail and see lifecycle badges, so that I can quickly resume the right assessment.
5. **US-060-A-05 — Invoke Assessment:** As a Technical Lead, I want to select Quick, Standard, or Deep and populate a ready-to-run Console command, so that I can invoke the independent assessment skill with correct context.
6. **US-060-A-06 — Observe Progress:** As a Project Manager, I want the case status and report links to refresh using X-IPE's established polling convention, so that I see skill-published changes without reloading the page.
7. **US-060-A-07 — Review Reports:** As a Project Manager or Technical Lead, I want to open the CIO report and navigate its slides and related report files as represented in the current mockup, so that I can inspect and share the result.
8. **US-060-A-08 — Use Without a Mouse:** As a keyboard or assistive-technology user, I want the case list, form, tabs, depth selector, report navigation, and feedback messages to be operable and understandable, so that the full workflow is accessible.
9. **US-060-A-09 — Stay in X-IPE:** As a Project Manager, I want CR Assessment to replace the current right-hand content view while the sidebar, top menu, and Console remain mounted, so that assessment remains part of the integrated workspace.

### AC-060-A-00: Integrated Navigation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-060-A-00a | GIVEN the X-IPE workspace is open WHEN the user activates **CR Assessment** in the Workplace submenu THEN AI Court replaces only the right-hand content body AND the X-IPE top menu, sidebar, breadcrumb header, and Console remain mounted | Integration |
| AC-060-A-00b | GIVEN AI Court is active WHEN the user selects another X-IPE view THEN CR Assessment polling and document-level listeners are released | UI |

## Acceptance Criteria

### AC-060-A-01: Case Identity and Creation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-060-A-01a | GIVEN the CR Assessment view is open WHEN the user activates **New Assessment Case** in the case rail THEN an empty information form is displayed with focus placed on Case Name | UI |
| AC-060-A-01b | GIVEN valid mandatory inputs WHEN a new case is saved THEN the service assigns a unique immutable ID matching `CR-YYYY-NNN` AND creates `x-ipe-docs/cr-cases/{case-id}/` | Integration |
| AC-060-A-01c | GIVEN an existing case WHEN its Case Name is changed and saved THEN its display name changes AND its case ID and folder path remain unchanged | Integration |
| AC-060-A-01d | GIVEN two creation requests that resolve to the same next sequence WHEN they are processed concurrently THEN exactly one case receives each generated ID AND neither case overwrites the other | Integration |

### AC-060-A-02: Input Persistence

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-060-A-02a | GIVEN a case with valid Case Name and CR Description WHEN the user activates **Save Update** THEN current form values and file references are persisted AND a success status message is announced | Integration |
| AC-060-A-02b | GIVEN CR Description was supplied as an uploaded file WHEN the case is saved THEN the original filename and file bytes are preserved without transformation | Integration |
| AC-060-A-02c | GIVEN multiple supporting documents WHEN the case is saved THEN each original file is preserved and listed in the case form | Integration |
| AC-060-A-02d | GIVEN a Vendor estimate artifact WHEN the case is saved THEN its original representation is preserved and referenced in case metadata | Integration |
| AC-060-A-02e | GIVEN the user has unsaved edits WHEN the user selects a different case THEN the UI prevents silent loss by requiring an explicit save-or-discard decision | UI |
| AC-060-A-02f | GIVEN a persistence operation fails WHEN the user saves THEN the prior valid case record remains readable AND an actionable non-sensitive error is displayed | Integration |

### AC-060-A-03: Input Validation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-060-A-03a | GIVEN Case Name or CR Description is empty WHEN the form is validated THEN the missing field is identified inline AND AI Estimation is unavailable | UI |
| AC-060-A-03b | GIVEN Codebase Path does not exist, is not a directory, or is unreadable WHEN the form is validated THEN the path is rejected with a corrective message AND AI Estimation is unavailable | Integration |
| AC-060-A-03c | GIVEN Codebase Path contains a remote Git URL WHEN the form is validated THEN it is rejected as unsupported in v1 | Unit |
| AC-060-A-03d | GIVEN a valid readable local directory WHEN the path is validated THEN the readiness indicator marks Codebase as ready | Integration |
| AC-060-A-03e | GIVEN no Vendor effort artifact is present WHEN readiness is evaluated THEN Vendor Estimate is marked missing AND AI Estimation remains unavailable | UI |
| AC-060-A-03f | GIVEN invalid input WHEN the user corrects it THEN the associated error is cleared without discarding other form values | UI |

### AC-060-A-04: Assessment Depth and Prompt Population

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-060-A-04a | GIVEN an assessment-ready case WHEN the depth menu opens THEN Quick, Standard, and Deep are displayed with scope descriptions AND Standard is selected by default | UI |
| AC-060-A-04b | GIVEN a user selects Quick, Standard, or Deep WHEN the menu closes THEN the selected depth remains visible on the AI Estimation control | UI |
| AC-060-A-04c | GIVEN valid unsaved form changes WHEN the user activates AI Estimation THEN the service validates and saves the case AND creates an immutable input snapshot before preparing the prompt | Integration |
| AC-060-A-04d | GIVEN snapshot creation succeeds WHEN AI Estimation continues THEN case status becomes `Evaluating` AND the existing X-IPE Console is populated with `evaluate-cr-effort`, the immutable case-folder path, and selected analysis depth | Integration |
| AC-060-A-04e | GIVEN the Console prompt has been populated WHEN the user does not submit it THEN the case remains `Evaluating` until the skill or an explicit metadata edit changes its status | Integration |
| AC-060-A-04f | GIVEN validation, save, or snapshot creation fails WHEN AI Estimation is activated THEN no Console prompt is populated AND the case does not transition to `Evaluating` | Integration |
| AC-060-A-04g | GIVEN a case is already `Evaluating` WHEN its form is displayed THEN AI Estimation and assessment input controls are disabled | UI |

### AC-060-A-05: Case List and Selection

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-060-A-05a | GIVEN stored cases exist WHEN the view loads THEN the left rail lists case name, immutable case ID, relative update time, and lifecycle badge following the current mockup hierarchy | UI |
| AC-060-A-05b | GIVEN text is entered in the case search control WHEN the list filters THEN only cases whose name or ID contains the text case-insensitively remain visible | UI |
| AC-060-A-05c | GIVEN no case matches the search WHEN filtering completes THEN an explicit no-results state is displayed without hiding the New Assessment Case control | UI |
| AC-060-A-05d | GIVEN no cases exist WHEN the view loads THEN an empty state explains how to create the first case AND the creation control remains available | UI |
| AC-060-A-05e | GIVEN a case is selected WHEN its data loads THEN the selected rail item is visually and programmatically identified AND the detail header shows the same case name and ID | UI |
| AC-060-A-05f | GIVEN case loading is in progress WHEN the user changes selection THEN the detail area exposes a loading state and does not display stale data under the new case heading | UI |

### AC-060-A-06: Metadata Polling and Notifications

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-060-A-06a | GIVEN the CR Assessment view is open WHEN five seconds elapse THEN the UI checks case-record change markers using the established X-IPE HTTP polling convention | Integration |
| AC-060-A-06b | GIVEN a poll reports no change WHEN the response is processed THEN the current form and report preview are not re-rendered | Unit |
| AC-060-A-06c | GIVEN the assessment skill changes status or latest report metadata WHEN the next poll completes THEN the affected case badge and detail metadata update AND an accessible status notification is shown | Integration |
| AC-060-A-06d | GIVEN the user has unsaved form edits WHEN polling detects external metadata changes THEN the edits are preserved AND the user is warned before any conflicting fields are replaced | UI |
| AC-060-A-06e | GIVEN the CR Assessment view is closed or hidden WHEN its lifecycle cleanup runs THEN its polling interval is stopped | Unit |
| AC-060-A-06f | GIVEN polling temporarily fails WHEN a later poll succeeds THEN the UI recovers without a full-page reload AND does not change the case to `Failed` | Integration |
| AC-060-A-06g | GIVEN a case remains `Evaluating` indefinitely WHEN polling continues THEN FEATURE-060-A does not impose a timeout or automatically change its lifecycle status | Integration |

### AC-060-A-07: Report Preview and History

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-060-A-07a | GIVEN a case has a current `CaseRecord.html` WHEN the user activates **View Latest Report** or the **AI Verdict Report** tab THEN the report preview shown in the current mockup opens for that case | UI |
| AC-060-A-07b | GIVEN report metadata lists effort and technical-design outputs WHEN the report view loads THEN the latest files and all preserved historical versions are reachable from the case detail | Integration |
| AC-060-A-07c | GIVEN the CIO report contains multiple slides WHEN the user activates previous, next, or a slide indicator THEN the requested slide becomes visible AND navigation state is updated | UI |
| AC-060-A-07d | GIVEN focus is not in an editable control WHEN the user presses Left Arrow or Right Arrow in the report view THEN the preceding or following slide is displayed | UI |
| AC-060-A-07e | GIVEN a module summary is displayed in the report preview WHEN its disclosure control is activated THEN its detail expands or collapses AND exposes the corresponding accessibility state | UI |
| AC-060-A-07f | GIVEN no generated report exists WHEN the report tab is selected THEN an empty state explains that assessment output is not yet available | UI |
| AC-060-A-07g | GIVEN a referenced report file is missing or unreadable WHEN preview is requested THEN the UI shows a local error and retains access to other valid versions | Integration |

### AC-060-A-08: Mockup Fidelity and Responsive Layout

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-060-A-08a | GIVEN a desktop viewport of at least 1024 CSS pixels WHEN the module renders THEN it preserves the current mockup's top bar, left case rail, detail header, information/report tabs, and main content hierarchy | UI |
| AC-060-A-08b | GIVEN the information tab is active on desktop WHEN the form renders THEN the primary form and assessment-readiness card use the two-column relationship shown in the current mockup | UI |
| AC-060-A-08c | GIVEN a viewport between 768 and 1023 CSS pixels WHEN the module renders THEN content remains readable and operable without horizontal page scrolling | UI |
| AC-060-A-08d | GIVEN a viewport below 768 CSS pixels WHEN the module renders THEN the case rail and detail content adapt to a single-primary-pane experience without losing any action | UI |
| AC-060-A-08e | GIVEN status badges, active cases, selected tabs, readiness indicators, and primary actions are rendered WHEN compared with the current mockup THEN their semantic hierarchy and distinct states remain recognizable without relying on color alone | UI |

### AC-060-A-09: Accessibility

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-060-A-09a | GIVEN a keyboard-only user WHEN they traverse the module THEN every interactive control is reachable in a logical order and has a visible focus indicator | UI |
| AC-060-A-09b | GIVEN focus is on the information/report tab list WHEN Left Arrow, Right Arrow, Home, End, Enter, or Space is used THEN focus and selection follow the WAI-ARIA tabs interaction pattern | UI |
| AC-060-A-09c | GIVEN validation or asynchronous status changes occur WHEN assistive technology is active THEN the message is programmatically associated or announced without requiring focus movement | UI |
| AC-060-A-09d | GIVEN an icon-only, slide-dot, or compact disclosure control is displayed WHEN target size is measured THEN it is at least 24 by 24 CSS pixels or has equivalent non-overlapping target spacing | UI |
| AC-060-A-09e | GIVEN the interface is checked at normal text size WHEN foreground and background contrast are measured THEN text and controls meet WCAG 2.1 AA contrast requirements | UI |
| AC-060-A-09f | GIVEN the detail tab changes WHEN the new panel is displayed THEN tab, tablist, and tabpanel semantics expose the active relationship to assistive technology | UI |

## Functional Requirements

### FR-060-A-01: Case Identity

- **Input:** New case request with Case Name and CR Description.
- **Process:** Allocate a concurrency-safe, human-readable `CR-YYYY-NNN` identifier and immutable case folder.
- **Output:** Stable case ID, folder, timestamps, lifecycle status, and initial `CaseRecord.html` metadata.

### FR-060-A-02: Case Record Management

- **Input:** Form fields, original uploaded artifacts, comments, and existing case metadata.
- **Process:** Validate and atomically persist current case data while retaining report references and history written by FEATURE-060-B.
- **Output:** Updated machine-readable metadata and human-readable case record without partial writes.

### FR-060-A-03: Local Path Validation

- **Input:** User-entered or browsed Codebase Path.
- **Process:** Confirm that the value is a local path that exists, is a directory, and is readable; reject URL-shaped remote repository inputs.
- **Output:** Ready/not-ready state and a corrective validation message when invalid.

### FR-060-A-04: Evidence File Handling

- **Input:** CR source file, multiple supporting documents, and Vendor effort artifact.
- **Process:** Preserve original filename and bytes, reject unsafe path traversal, and associate the stored artifacts with the case.
- **Output:** Durable evidence references included in case metadata and invocation snapshots.

### FR-060-A-05: Assessment Invocation Preparation

- **Input:** Assessment-ready case and chosen depth.
- **Process:** Validate, auto-save, create an immutable snapshot, change status to `Evaluating`, and populate the existing X-IPE Console prompt.
- **Output:** A ready-to-submit `evaluate-cr-effort` command containing the stable case-folder path and `quick`, `standard`, or `deep` depth.

The UI only populates the Console. It does not submit the command, launch the skill, inspect source code for assessment, or monitor a child process.

### FR-060-A-06: Case Discovery

- **Input:** Stored case records and optional search text.
- **Process:** Load summaries, sort by most recently updated by default, and filter by case name or ID.
- **Output:** Case rail with count, lifecycle badge, selected state, and empty/no-results states.

### FR-060-A-07: External Metadata Refresh

- **Input:** Case-record modification/version markers observed through the existing HTTP interface.
- **Process:** Poll every five seconds while the view is active, compare markers, and fetch/re-render only changed cases.
- **Output:** Updated lifecycle/report metadata and an accessible notification without disturbing unrelated unsaved form values.

### FR-060-A-08: Report Presentation

- **Input:** Current and historical report references stored in `CaseRecord.html` metadata.
- **Process:** Reuse X-IPE's HTML deliverable preview capability and expose the CIO slide navigation and related report links represented by the current mockup.
- **Output:** Read-only preview with previous/next, slide indicators, keyboard navigation, expandable details, and missing-report handling.

## Non-Functional Requirements

### NFR-060-A-01: Performance

- Initial case summaries for up to 500 cases must render within 2 seconds on the supported local development environment.
- Search filtering must update within 100 milliseconds after input processing for up to 500 loaded summaries.
- Unchanged polling responses must not trigger full detail or preview re-rendering.

### NFR-060-A-02: Data Integrity

- Case identity allocation, metadata changes, and input snapshot publication must be atomic.
- A failed write must leave the previous valid case record available.
- FEATURE-060-A must preserve unknown forward-compatible metadata owned by FEATURE-060-B.

### NFR-060-A-03: Security

- All case paths must remain under the configured CR case root after canonicalization.
- Uploaded filenames must not permit path traversal or overwrite metadata/templates outside their case folder.
- Error messages and UI metadata must not expose credentials, secret values, or unnecessary source content.
- Generated HTML previews must use the existing X-IPE sandboxing and content-safety boundary.

### NFR-060-A-04: Accessibility

- Primary flows must meet WCAG 2.1 AA expectations for keyboard operation, focus visibility, semantics, labels, status messages, and contrast.
- Pointer targets must meet the WCAG 2.2 Level AA 24-by-24 CSS pixel minimum or its spacing exception.
- Tab interactions must follow the WAI-ARIA Authoring Practices tabs pattern.

### NFR-060-A-05: Responsiveness

- The module must support desktop and tablet widths and remain fully operable below 768 CSS pixels through an adaptive single-primary-pane presentation.
- No mandatory input, action, status, or report link may be available only on hover.

### NFR-060-A-06: Reliability

- Temporary polling failure must not corrupt case state or disable manual navigation.
- The service must tolerate a `CaseRecord.html` changed by FEATURE-060-B between read and write without silently overwriting newer report metadata.
- No timeout or automatic recovery is applied to cases that remain `Evaluating`.

## UI/UX Requirements

### Layout and Visual Hierarchy

- Preserve the current mockup's top application bar, dark left case rail, light detail workspace, case heading, lifecycle badge hierarchy, and two primary tabs.
- On desktop, the information view uses a main form beside an assessment-readiness card; the report view uses the full content width.
- Preserve the visual distinction among `Created`, `Evaluating`, `Completed`, and `Failed` without relying on color alone.
- Adapt the layout below 768 CSS pixels so users can switch between case discovery and case detail without losing state.

### Case Rail

- Show case count, labelled search input, case name, immutable ID, relative update time, lifecycle badge, selected state, and New Assessment Case control.
- Provide explicit initial-empty, search-no-results, loading, and load-error states.
- Case selection must not silently discard unsaved edits.

### Information Form

- Include Case Name, read-only Case ID, CR Description, Codebase Path with Browse control, Supporting Documents, Vendor Effort Estimation, and Comments.
- Indicate required fields in text/semantics as well as visually.
- Show stored file chips with filename and removal/replacement actions where allowed.
- Present inline validation near the relevant control and a summary/status message for failed save or invocation operations.

### Assessment Readiness and Depth

- Present readiness for CR Brief, Codebase, and Vendor Estimate, matching the mockup's compact readiness-card hierarchy.
- Expose Quick, Standard, and Deep with concise scope descriptions; Standard is the default.
- AI Estimation is disabled until readiness passes and disabled while the case is `Evaluating`.
- Activating AI Estimation auto-saves, snapshots, changes status, and populates the Console; success feedback must make clear that the command is ready but has not been submitted by the UI.

### Report View

- Provide Information and AI Verdict Report tabs with complete tab semantics and keyboard behavior.
- Preserve the CIO report's toolbar, slide indicators, slide stage, previous/next controls, and arrow-key navigation from the mockup.
- Provide current and historical links for CaseRecord, Effort Estimation, and Suggested Technical Design outputs.
- Module disclosures must expose expanded/collapsed state; report loading, absent output, and unreadable-file states must be explicit.

### Feedback

- Use X-IPE's established toast/status pattern for saves and externally detected report/status changes.
- Status messages must be perceivable by assistive technology and must not rely only on transient color or animation.
- Polling must not steal focus or reset the user's current slide, scroll position, or unsaved input.

## Dependencies

### Internal Dependencies

- **FEATURE-001-A — Project Navigation:** Provides the established five-second HTTP filesystem-change polling convention and project path context.
- **FEATURE-002-A — Content Viewer:** Provides HTML preview and existing Mermaid/content rendering precedent.
- **EPIC-043 — Deliverable Preview:** Provides the in-app deliverable preview surface reused for case reports.
- **FEATURE-038-A / X-IPE Console:** Provides prompt population and Console execution interaction.
- **`copilot-prompt.json`:** Supplies the `cr-assessment` / `evaluate-cr-effort` prompt definition and placeholders.
- **FEATURE-060-B — AI Change Request Assessment Skill:** Consumes the case/snapshot contract and publishes status/report metadata back to the case record. FEATURE-060-A remains usable for case management before FEATURE-060-B is available.

### External Standards

- **WCAG 2.1 AA / applicable WCAG 2.2 controls:** Accessibility quality target.
- **WAI-ARIA Authoring Practices:** Keyboard and semantic behavior for tabs, disclosures, buttons, and status feedback.

## Business Rules

1. **BR-060-A-01:** A case folder is identified by its generated immutable `CR-YYYY-NNN` case ID, never by its editable display name.
2. **BR-060-A-02:** Case Name and CR Description are mandatory for saving a new case.
3. **BR-060-A-03:** A readable local codebase directory and Vendor effort artifact are additionally mandatory for AI Estimation.
4. **BR-060-A-04:** Remote Git URLs and automatic repository cloning are not supported in v1.
5. **BR-060-A-05:** Standard is the default analysis depth; the user's explicit Quick or Deep selection is preserved in the snapshot and prompt.
6. **BR-060-A-06:** AI Estimation validates and auto-saves before snapshot and prompt population.
7. **BR-060-A-07:** Successful prompt population changes the case to `Evaluating`, even if the user never submits the Console command.
8. **BR-060-A-08:** FEATURE-060-A never applies an evaluation timeout or automatic stale-case recovery.
9. **BR-060-A-09:** `Completed` and `Failed` transitions are read from metadata published by FEATURE-060-B or an explicit user metadata edit; human review is independent.
10. **BR-060-A-10:** Existing valid report history must never be deleted or replaced by a failed case-service operation.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Case-name collision | Both cases are allowed because generated IDs and folders are unique. |
| Case name contains path separators or reserved characters | Preserve the display value as safe metadata; it does not determine the folder path. |
| Concurrent case creation | Allocate distinct IDs atomically without overwriting either case. |
| Local codebase path becomes unreadable after save | Revalidation blocks the next AI Estimation and explains the path problem. |
| Uploaded filename attempts path traversal | Reject or safely normalize it; never write outside the case folder. |
| AI Estimation prompt is populated but never submitted | Case remains `Evaluating`; no timeout or automatic recovery occurs. |
| Skill writes metadata while form has unsaved changes | Refresh non-conflicting status/report fields; preserve edits and require an explicit resolution for conflicts. |
| Case record is temporarily malformed during an external write | Retain the last valid UI state and retry on the next poll; do not display partial metadata. |
| Polling endpoint is unavailable | Show non-blocking degraded status and recover on a later successful poll. |
| Latest report missing but older version exists | Show a latest-report error while keeping valid historical versions accessible. |
| No cases exist | Show the empty-state creation guidance from the case rail. |
| Search has no match | Show no-results feedback and retain the creation control. |
| User presses slide arrow key inside a text input | Preserve native caret behavior; do not change slides. |
| View is hidden or destroyed | Stop the feature's polling interval and release event listeners. |

## Out of Scope

- AI code inspection, effort estimation, benchmark application, or technical-design reasoning.
- Creation or modification of the `x-ipe-task-based-evaluate-change-request-efforts` skill.
- Service-side skill API, subprocess launch, command submission, or execution monitoring.
- Automatic timeout, retry, cancellation, or stale-`Evaluating` recovery.
- Remote Git clone, checkout, credentials, or repository-host integrations.
- Editing generated assessment/design report content in the module.
- Separate Vendor-sanitized report editions or an external Vendor portal.
- Knowledge-graph writeback, code remediation, procurement approval, or contract decision automation.

## Technical Considerations

- Define and version a shared case metadata and immutable snapshot contract that FEATURE-060-B can consume and update without lossy rewrites.
- Preserve unknown metadata fields to support forward compatibility between independently delivered features.
- Reuse the established X-IPE HTTP polling, Console prompt, folder selection, toast, and deliverable preview capabilities.
- Ensure prompt preparation exposes enough context to distinguish “prompt populated” from “command submitted,” since lifecycle status intentionally changes at population time.
- Keep lifecycle/status rules independent from report rendering and keep all assessment decisions outside this service.
- Treat HTML reports as untrusted local deliverables and preserve the existing preview sandbox boundary.

## Open Questions

None. Scope and edge-case decisions were confirmed on 07-21-2026.
