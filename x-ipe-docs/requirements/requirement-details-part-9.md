# Requirement Details - Part 9

> Continued from: [requirement-details-part-8.md](x-ipe-docs/requirements/requirement-details-part-8.md)
> Created: 02-17-2026

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-036-A | EPIC-036 | Workflow Manager & State Persistence | v1.0 | Backend service: workflow CRUD, stage gating logic, dependency evaluation, next-action suggestion; JSON state persistence; new MCP tools | None (depends on FEATURE-033 externally) |
| FEATURE-036-B | EPIC-036 | Workflow View Shell & CRUD | v1.0 | New top-nav entry "Engineering Workflow"; workflow list view with expandable panels; create/delete/archive actions | FEATURE-036-A |
| FEATURE-036-C | EPIC-036 | Stage Ribbon & Action Execution | v1.0 | Horizontal stage progression bar with done/active/pending states; stage-specific action buttons; CLI agent action execution; stage gating enforcement | FEATURE-036-A, FEATURE-036-B |
| FEATURE-036-D | EPIC-036 | Feature Lanes & Dependencies | v1.0 | Horizontal feature swimlanes; per-lane stage progress; SVG dependency arrows; parallel session execution with dependency check | FEATURE-036-A, FEATURE-036-B, FEATURE-036-C |
| FEATURE-036-E | EPIC-036 | Deliverables, Polling & Lifecycle | v1.0 | Collapsible deliverables section; Deliverables Resolver; 7-second polling; auto-archive; error recovery | FEATURE-036-A, FEATURE-036-B |
| FEATURE-035-A | EPIC-035 | Epic Core Workflow Skills | v1.0 | Update requirement-gathering and feature-breakdown skills for Epic folder/naming support | None |
| FEATURE-035-B | EPIC-035 | Feature Board Epic Tracking | v1.0 | Add Epic ID column to features.md, update feature-board-management skill | FEATURE-035-A |
| FEATURE-035-C | EPIC-035 | Feature Lifecycle Skill Updates | v1.0 | Update 10+ lifecycle skills for Epic-aware paths | FEATURE-035-A, FEATURE-035-B |
| FEATURE-035-D | EPIC-035 | Requirement-Details Epic Format | v1.0 | Update requirement-details to use EPIC-{nnn} headers and templates | FEATURE-035-A |
| FEATURE-035-E | EPIC-035 | Retroactive Feature Migration | v1.0 | Migrate all existing features into EPIC-{nnn}/FEATURE-{nnn}-{X} structure | FEATURE-035-A, FEATURE-035-B, FEATURE-035-C, FEATURE-035-D |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| Engineering Workflow View (full interactive) | All FEATURE-036-* | [workflow-view-v1.html](x-ipe-docs/requirements/EPIC-036/mockups/workflow-view-v1.html) |
| Introduce Epic Layer (idea summary) | CR-EPIC | [idea-summary-v2.md](x-ipe-docs/ideas/022. CR-Introduce Epic/idea-summary-v2.md) |

---

## Feature Details

---

## EPIC-036: Engineering Workflow View

**Version:** v1.0
**Brief Description:** A centralized Engineering Workflow view integrated into the X-IPE application that orchestrates the full project value delivery lifecycle — from ideation through requirement, implementation, validation, and feedback — in a single, visual, panel-based interface.

> Source: IDEA-021 (Feature-Engineering-Workflow)
> Status: Proposed
> Priority: High
> Mockup: [workflow-view-v1.html](x-ipe-docs/requirements/EPIC-036/mockups/workflow-view-v1.html)

#### Project Overview

Currently, X-IPE provides powerful skills for each stage of software delivery (ideation, requirements, design, implementation, testing, feedback), but they are accessed in isolation. Users manually navigate between the console, sidebar, knowledge base, and idea views to track progress. There is no unified view that shows where you are in the delivery lifecycle, what to do next, what deliverables exist, or which features can progress in parallel.

The Engineering Workflow View solves this by providing a centralized, visual, panel-based interface that orchestrates the full project delivery lifecycle using existing X-IPE skills and infrastructure.

#### User Request

The user wants:
1. A new "Engineering Workflow" top-nav entry that opens a dedicated workflow management view
2. Workflow panels with stage ribbons, action buttons, and feature lanes
3. Feature dependency tracking and parallel run indicators
4. True parallel agent session execution for independent features
5. Backend Workflow Manager with state persistence in JSON
6. MCP integration for skill-to-workflow communication
7. Auto-archive of completed workflows after 30 days of inactivity

#### Clarifications

| Question | Answer |
|----------|--------|
| Workflow-to-idea folder mapping | No idea folder required upfront at creation. When user clicks Compose/Upload Idea, prompt to create or select an existing idea folder |
| Feature dependency source | Auto-populated from Feature Breakdown skill output via agent skill → MCP → Workflow Manager → persisted in workflow JSON |
| Parallel execution | True parallel agent sessions allowed for independent features. Before starting an action, Workflow Manager checks dependencies; if dependency unfinished → show confirm dialog; if clear → start directly |
| Stage gating granularity | Both: shared stages (Ideation, Requirement) are workflow-level gated; per-feature stages (Implement, Validation, Feedback) are independently gated |
| Workflow end state | Auto-archive after 30 days inactivity; deliverables remain in their original locations |
| Console integration | Reuse existing console function — same pattern as copilot button in ideation view (find idle session, auto-type skill command) |
| State persistence | JSON files only (`x-ipe-docs/engineering-workflow/workflow-{name}.json`) for v1 |
| Real-time updates | Polling with 7-second interval to detect state changes |
| MCP tool ownership | New MCP tools (`update_workflow_status`, `get_workflow_state`) owned by this feature; dependency on FEATURE-033 for MCP infrastructure |

#### High-Level Requirements

##### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-036.1 | **Top-nav entry** — "Engineering Workflow" menu item in top navigation bar, opens dedicated workflow view replacing the middle content area | P0 |
| FR-036.2 | **Workflow CRUD** — Create, view, delete/archive workflows. "+" button opens modal with name input. No idea folder required at creation. | P0 |
| FR-036.3 | **Workflow Panel** — Each workflow displayed as expandable panel with header (name, creation date, feature count, current stage), stage ribbon, action buttons, feature lanes, and deliverables section | P0 |
| FR-036.4 | **Stage Ribbon** — Horizontal progression bar: Ideation → Requirement → Implement → Validation → Feedback. Visual states: completed (✓ green), active (animated dot), pending (numbered) | P0 |
| FR-036.5 | **Action Buttons** — Stage-specific action buttons with three states: Done (green), Suggested (dashed yellow), Normal (default). Each action maps to an X-IPE skill | P0 |
| FR-036.6 | **Stage Gating (Workflow-Level)** — Shared stages (Ideation, Requirement) must complete before per-feature stages unlock. Mandatory actions must complete before next stage. Optional actions can be skipped. | P0 |
| FR-036.7 | **Feature Lanes** — After Feature Breakdown, Implement/Validation/Feedback stages split into horizontal swimlanes per feature. Each lane shows feature ID, name, per-stage progress, and next suggested action | P0 |
| FR-036.8 | **Feature-Level Stage Gating** — Each feature lane has independent stage gating. Feature A can be in Validation while Feature B is in Implement | P0 |
| FR-036.9 | **Feature Dependencies** — Dependency data auto-populated from Feature Breakdown output. Displayed as SVG curved connector arrows between dependent lanes. Dependency tags (`⛓ needs {ID}`) on dependent features. Parallel badges (`⇉ Parallel`) on independent features | P0 |
| FR-036.10 | **Dependencies Toggle** — Button in lanes legend to show/hide dependency visualizations (arrows, tags, badges) | P1 |
| FR-036.11 | **Working Item Selector** — Dropdown panel listing features with current stage and next action. Selecting a feature highlights its lane. Disabled before Feature Breakdown | P1 |
| FR-036.12 | **Action Execution — Modal** — Compose/Upload Idea actions open existing modal UI | P0 |
| FR-036.13 | **Action Execution — CLI Agent** — All other actions: (1) check dependencies via Workflow Manager, (2) if dependency unfinished → confirm dialog, (3) if clear → open console, find idle session, auto-type skill command (user presses Enter to confirm) | P0 |
| FR-036.14 | **True Parallel Execution** — Multiple agent sessions can run simultaneously for independent features. No restriction on concurrent sessions | P0 |
| FR-036.15 | **Idea Folder Linking** — No folder required at workflow creation. When user triggers Compose/Upload Idea, prompt to create new or select existing idea folder. Linked via `idea_folder` field in workflow JSON | P0 |
| FR-036.16 | **Deliverables Section** — Collapsible section showing categorized artifacts (Ideas, Mockups, Requirements, Implementations, Quality Reports) with clickable links. Missing files show "⚠️ not found" | P1 |
| FR-036.17 | **Auto-Archive** — Workflows auto-archive after 30 days of inactivity. Archived workflows move to `engineering-workflow/archive/`. Deliverables remain in original locations | P1 |

##### Backend & Integration Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-036.18 | **Engineering Workflow Manager** — New backend service: workflow CRUD, stage gating logic, dependency evaluation, next-action suggestion, state persistence, notification dispatch | P0 |
| FR-036.19 | **MCP Tools** — New tools on existing app-agent-interaction MCP: `update_workflow_status(workflow_name, action, status, deliverables[])` and `get_workflow_state(workflow_name)` | P0 |
| FR-036.20 | **State Persistence** — Workflow state in `x-ipe-docs/engineering-workflow/workflow-{name}.json` with `schema_version` field for future migrations | P0 |
| FR-036.21 | **Polling Updates** — Frontend polls for workflow state changes every 7 seconds. On change detected, UI refreshes affected panels/lanes | P0 |
| FR-036.22 | **Dependency Check Before Action** — Workflow Manager evaluates feature dependencies before allowing action execution. Blocked features trigger confirm dialog | P0 |
| FR-036.23 | **Deliverables Resolver** — Reads deliverable paths from workflow JSON → verifies file existence → returns resolved links or "⚠️ not found" | P1 |

##### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-036.1 | Workflow View must load within 2 seconds for up to 10 active workflows | P0 |
| NFR-036.2 | Polling must not cause noticeable UI lag or CPU usage | P0 |
| NFR-036.3 | Workflow JSON schema must include `schema_version` for forward-compatible migrations | P0 |
| NFR-036.4 | Only Engineering Workflow Manager (via MCP) writes to workflow JSON — ensures data integrity | P0 |
| NFR-036.5 | No modification to existing X-IPE skills — orchestration only | P0 |
| NFR-036.6 | Console integration reuses existing session APIs without modification | P0 |

#### Acceptance Criteria

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-036.1 | User is on any X-IPE page | User clicks "Engineering Workflow" in top nav | Middle content area replaced with workflow view showing all workflows |
| AC-036.2 | Workflow view is visible | User clicks "+ Create Workflow" and enters a name | New workflow panel created with Ideation stage active, no idea folder linked |
| AC-036.3 | Workflow at Ideation stage | User clicks "Compose Idea" action | Prompt to create/select idea folder, then modal opens for idea composition |
| AC-036.4 | Workflow at Ideation stage, all mandatory actions done | Workflow Manager evaluates stage | Requirement stage unlocks; stage ribbon updates |
| AC-036.5 | Workflow at Requirement stage | User completes Feature Breakdown skill | Feature lanes appear; dependency data auto-populated from skill output via MCP |
| AC-036.6 | Feature lanes visible with dependencies | User looks at the lanes | Dependent features show `⛓ needs {ID}` tags; independent features show `⇉ Parallel` badges; SVG arrows connect dependent lanes |
| AC-036.7 | User clicks Dependencies toggle | Toggle button clicked | All dependency visualizations (arrows, tags, badges) hide/show |
| AC-036.8 | Feature A has no unfinished dependencies | User clicks action on Feature A | Action starts immediately — console opens, idle session found, skill command auto-typed |
| AC-036.9 | Feature B depends on Feature A (unfinished) | User clicks action on Feature B | Confirm dialog warns about unfinished dependency; user can proceed or cancel |
| AC-036.10 | Two independent features | User starts actions on both | Two concurrent agent sessions run in separate console sessions |
| AC-036.11 | Agent skill completes | Skill calls `update_workflow_status` via MCP | Workflow JSON updated; UI refreshes within 7 seconds (next poll); action button turns green |
| AC-036.12 | All features reach Feedback stage completion | 30 days pass with no activity | Workflow auto-archived; deliverables remain accessible in original locations |
| AC-036.13 | Deliverable file has been deleted | Deliverables section renders | Missing file shows "⚠️ not found" instead of broken link |
| AC-036.14 | Working Item Selector opened | User clicks a feature in dropdown | Corresponding feature lane highlights; dropdown closes |

#### Action-to-Stage Mapping

| Stage | Action | Mandatory | Interaction | Skill |
|-------|--------|-----------|-------------|-------|
| Ideation | Compose/Upload Idea | ✅ | Modal | (built-in) |
| Ideation | Reference UIUX | ❌ | CLI Agent | x-ipe-tool-uiux-reference |
| Ideation | Refine Idea | ✅ | CLI Agent | x-ipe-task-based-ideation-v2 |
| Ideation | Design Mockup | ❌ | CLI Agent | x-ipe-task-based-idea-mockup |
| Requirement | Requirement Gathering | ✅ | CLI Agent | x-ipe-task-based-requirement-gathering |
| Requirement | Feature Breakdown | ✅ | CLI Agent | x-ipe-task-based-feature-breakdown |
| Implement | Feature Refinement | ✅ | CLI Agent | x-ipe-task-based-feature-refinement |
| Implement | Technical Design | ✅ | CLI Agent | x-ipe-task-based-technical-design |
| Implement | Implementation | ✅ | CLI Agent | x-ipe-task-based-code-implementation |
| Validation | Acceptance Testing | ✅ | CLI Agent | x-ipe-task-based-feature-acceptance-test |
| Validation | Feature Quality Evaluation | ❌ | CLI Agent | (deferred to v2 — skill TBD) |
| Feedback | Change Request | ❌ | CLI Agent | x-ipe-task-based-change-request |

#### Stage Completion Rules

| Stage | Mandatory Actions | Optional Actions | Gate to Next |
|-------|-------------------|------------------|--------------|
| Ideation | Compose/Upload Idea, Refine Idea | Reference UIUX, Design Mockup | All mandatory done |
| Requirement | Requirement Gathering, Feature Breakdown | — | All mandatory done |
| Implement (per-feature) | Feature Refinement, Technical Design, Implementation | — | All mandatory done |
| Validation (per-feature) | Acceptance Testing | Feature Quality Evaluation | Acceptance Testing done |
| Feedback (per-feature) | — | Change Request | Stage auto-completes; CR loops back to Implement |

#### Error Handling & Recovery

| Scenario | Behavior |
|----------|----------|
| Skill fails mid-action | Action stays `in_progress`; user sees retry button; error logged in workflow JSON |
| MCP callback never arrives | After 10-minute timeout, action shows "status unknown" with manual override options (mark done / retry) |
| Workflow JSON corrupted | Workflow Manager validates JSON on read; falls back to last known good state |
| Deliverable file missing | Deliverables Resolver marks link as "⚠️ not found" |
| Manual override | User can right-click action → "Mark as Done" or "Reset to Pending" for recovery |

#### Workflow State JSON Schema (v1.0)

```json
{
  "schema_version": "1.0",
  "name": "My Feature Workflow",
  "created": "2026-02-16T08:00:00Z",
  "last_activity": "2026-02-17T09:00:00Z",
  "idea_folder": null,
  "current_stage": "ideation",
  "stages": {
    "ideation": {
      "status": "in_progress",
      "actions": {
        "compose_idea": { "status": "pending", "deliverables": [] },
        "reference_uiux": { "status": "skipped", "deliverables": [] },
        "refine_idea": { "status": "pending", "deliverables": [] },
        "design_mockup": { "status": "pending", "deliverables": [] }
      }
    },
    "requirement": {
      "status": "locked",
      "actions": {
        "requirement_gathering": { "status": "pending", "deliverables": [] },
        "feature_breakdown": { "status": "pending", "deliverables": [], "features_created": [] }
      }
    },
    "implement": {
      "status": "locked",
      "features": {}
    },
    "validation": {
      "status": "locked",
      "features": {}
    },
    "feedback": {
      "status": "locked",
      "features": {}
    }
  }
}
```

**Post-Feature Breakdown, per-feature structure:**

```json
{
  "FEATURE-040": {
    "name": "Login Page",
    "depends_on": [],
    "actions": {
      "feature_refinement": { "status": "pending", "deliverables": [] },
      "technical_design": { "status": "pending", "deliverables": [] },
      "implementation": { "status": "pending", "deliverables": [] },
      "acceptance_testing": { "status": "pending", "deliverables": [] },
      "quality_evaluation": { "status": "skipped", "deliverables": [] },
      "change_request": { "status": "pending", "deliverables": [] }
    }
  }
}
```

#### Dependencies

- **FEATURE-001** (Project Navigation) — top-nav entry positioning
- **FEATURE-005** (Interactive Console) — console session APIs for action execution
- **FEATURE-008** (Workplace/Idea Management) — idea folder creation/selection
- **FEATURE-029-A/B/C/D** (Console Session Explorer) — session management model
- **FEATURE-033** (App-Agent Interaction MCP) — MCP infrastructure for new workflow tools

#### Constraints

- **No skill refactoring** — Existing skills remain unchanged; the Workflow Manager orchestrates them
- **Reuse existing UI** — Console, idea compose/upload, sidebar patterns are reused
- **State file authority** — Only the Engineering Workflow Manager (via MCP) writes to workflow JSON
- **Sequential gating for shared stages** — Ideation and Requirement must complete before per-feature stages unlock
- **Independent gating for feature stages** — Each feature progresses independently through Implement → Validation → Feedback
- **JSON-only persistence** — No database for v1; JSON files are sufficient for single-user scope
- **Console sessions are reused** — Action execution finds idle session or creates new one; multiple concurrent sessions allowed
- **Single-user scope** — Multi-user concurrent access not addressed in v1

#### Feature Breakdown (EPIC-036)

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-036-A | EPIC-036 | Workflow Manager & State Persistence | v1.0 | Backend service: workflow CRUD, stage gating logic, dependency evaluation, next-action suggestion; JSON state persistence in `engineering-workflow/workflow-{name}.json`; new MCP tools (`update_workflow_status`, `get_workflow_state`) | None (depends on FEATURE-033 externally) |
| FEATURE-036-B | EPIC-036 | Workflow View Shell & CRUD | v1.0 | New top-nav entry "Engineering Workflow"; workflow list view with expandable panels; "+" Create Workflow modal; workflow header with name, date, feature count, stage indicator; delete/archive actions | FEATURE-036-A |
| FEATURE-036-C | EPIC-036 | Stage Ribbon & Action Execution | v1.0 | Horizontal stage progression bar (Ideation→Feedback) with done/active/pending states; stage-specific action buttons (done/suggested/normal); CLI agent action execution (find idle session, auto-type command); modal actions for Compose/Upload; stage gating enforcement | FEATURE-036-A, FEATURE-036-B |
| FEATURE-036-D | EPIC-036 | Feature Lanes & Dependencies | v1.0 | Horizontal feature swimlanes after Feature Breakdown; per-lane stage progress; SVG dependency arrows, `⛓ needs` tags, `⇉ Parallel` badges; dependencies toggle; Working Item Selector dropdown; true parallel session execution with dependency check + confirm dialog | FEATURE-036-A, FEATURE-036-B, FEATURE-036-C |
| FEATURE-036-E | EPIC-036 | Deliverables, Polling & Lifecycle | v1.0 | Collapsible deliverables section with categorized artifacts and "⚠️ not found" handling; Deliverables Resolver; 7-second polling for state updates; auto-archive after 30 days inactivity; error recovery (retry button, manual override) | FEATURE-036-A, FEATURE-036-B |

**Implementation Order:** A (foundation) → B (UI shell) → C (stage execution) → D (feature lanes) → E (deliverables & lifecycle)

#### Linked Mockups

| Mockup Function Name | Feature | Mockup List |
|---------------------|---------|-------------|
| Engineering Workflow View (Full) | All FEATURE-036-* | [workflow-view-v1.html](x-ipe-docs/requirements/EPIC-036/mockups/workflow-view-v1.html) |

---

### FEATURE-036-A: Workflow Manager & State Persistence

**Version:** v1.0
**Brief Description:** Backend foundation — Engineering Workflow Manager service with workflow CRUD, stage gating logic, dependency evaluation, next-action suggestion, and JSON state persistence. Includes new MCP tools for skill-to-workflow communication.

**Acceptance Criteria:**
- [ ] Engineering Workflow Manager service initializes on app startup
- [ ] Create workflow: generates `engineering-workflow/workflow-{name}.json` with schema_version 1.0, all stages locked except Ideation
- [ ] Read workflow: returns parsed state with action statuses, feature data, and dependencies
- [ ] Delete workflow: removes JSON file from disk
- [ ] Stage gating: evaluates mandatory action completion to determine if next stage unlocks
- [ ] Dependency evaluation: given a feature ID, returns list of blocking dependencies and their completion status
- [ ] Next-action suggestion: determines which action across all features should be worked on next
- [ ] MCP tool `update_workflow_status`: accepts workflow name, action, status, deliverables; updates JSON atomically
- [ ] MCP tool `get_workflow_state`: returns current workflow state for agent context
- [ ] State file validation: detects corrupted JSON, falls back to last known good state
- [ ] `last_activity` timestamp updated on every write operation

**Dependencies:**
- FEATURE-033 (App-Agent Interaction MCP) — MCP infrastructure for registering new tools

**Technical Considerations:**
- State writes must be atomic (write to temp file, then rename) to prevent corruption
- JSON schema includes `schema_version` for forward-compatible migrations
- Only Workflow Manager writes to state files — no direct file access from frontend
- Stage gating rules defined as configuration, not hardcoded logic

---

### FEATURE-036-B: Workflow View Shell & CRUD

**Version:** v1.0
**Brief Description:** Frontend workflow view — new top-nav entry, workflow list with expandable panels, create/delete workflows via modal, workflow header with metadata display.

**Acceptance Criteria:**
- [ ] "Engineering Workflow" menu item visible in top navigation bar
- [ ] Clicking menu item replaces middle content area with workflow view
- [ ] Workflow view displays all active workflows as vertically stacked expandable panels
- [ ] Each panel header shows: workflow name, creation date, feature count, current stage indicator
- [ ] "+ Create Workflow" button opens modal with name input field
- [ ] Creating workflow calls Workflow Manager API; new panel appears in list
- [ ] No idea folder required at creation; `idea_folder` field is null initially
- [ ] Delete/archive workflow via panel header action menu
- [ ] Panels expand/collapse on click

**Dependencies:**
- FEATURE-036-A (Workflow Manager — provides CRUD API)

**Technical Considerations:**
- Follows existing X-IPE top-nav pattern (positioned alongside Knowledge, Toolbox, Skills)
- Reuses existing modal dialog component patterns
- Panel list rendered from Workflow Manager API response

---

### FEATURE-036-C: Stage Ribbon & Action Execution

**Version:** v1.0
**Brief Description:** Stage progression visualization and action execution — horizontal stage ribbon with gating, action buttons with skill mapping, console integration for CLI agent actions, modal actions for Compose/Upload Idea.

**Acceptance Criteria:**
- [ ] Stage ribbon shows 5 stages: Ideation → Requirement → Implement → Validation → Feedback
- [ ] Stage visual states: completed (✓ green), active (animated dot), pending (numbered), locked (grayed)
- [ ] Stage gating enforced: locked stages show "complete {previous} to unlock" message
- [ ] Action buttons displayed per-stage with three states: Done (green), Suggested (dashed yellow), Normal (default)
- [ ] Clicking CLI Agent action: calls Workflow Manager to check if action is allowed → opens console → finds idle session → auto-types skill command
- [ ] Clicking Compose/Upload Idea action: prompts to create/select idea folder (if not linked) → opens existing modal UI
- [ ] After idea folder linked, `idea_folder` field updated in workflow JSON
- [ ] Action-to-skill mapping follows the defined table (12 actions across 5 stages)

> **⚠️ CR Impact Note** (added 2026-02-19, ref: EPIC-037)
> - **Change:** The "existing modal UI" for Compose/Upload Idea is now fully specified in EPIC-037 as a rich modal with Create New / Link Existing toggle, file tree browser with preview, auto-naming (wf-NNN), and re-edit capability
> - **Affected FRs:** FR-036.12 (Modal Action Execution), FR-036.15 (Idea Folder Linking), AC-036.3
> - **Action Required:** FEATURE-036-C specification update needed to reference EPIC-037 modal spec instead of generic "opens existing modal UI"
> - **New Feature Ref:** EPIC-037 — see requirement-details-part-10.md

**Dependencies:**
- FEATURE-036-A (Workflow Manager — gating logic, action validation)
- FEATURE-036-B (Workflow View Shell — panel container for ribbon and buttons)

**Technical Considerations:**
- Console integration reuses existing session APIs (same pattern as copilot button in ideation view)
- Action execution does NOT auto-press Enter — user confirms
- Stage gating queries Workflow Manager API for allowed actions

> **⚠️ CR Impact Note** (added 2026-02-20, ref: EPIC-038)
> - **Change:** CLI Agent actions now open a modal first (with readonly instructions from copilot-prompt.json + editable extra instructions, max 500 chars) before triggering the console session. This is a reusable pattern for all CLI Agent actions, not just Refine Idea.
> - **Affected FRs:** FR-036.13 (CLI Agent Action Execution)
> - **Action Required:** FEATURE-036-C specification update needed to add modal-before-CLI pattern, session idle detection (via `is_idle()`), and agent tool auto-detection from config
> - **New Feature Ref:** EPIC-038 — see requirement-details-part-11.md

---

### FEATURE-036-D: Feature Lanes & Dependencies

**Version:** v1.0
**Brief Description:** Feature swimlanes, dependency visualization, and parallel execution — horizontal feature lanes after Feature Breakdown, SVG dependency arrows, parallel/blocked badges, Working Item Selector, true parallel agent session support.

**Acceptance Criteria:**
- [ ] After Feature Breakdown completes (via MCP callback), feature lanes appear in workflow panel
- [ ] Each lane shows: feature ID, feature name, per-stage progress (done/active/pending), next suggested action
- [ ] Feature-level stage gating: each feature progresses independently through Implement → Validation → Feedback
- [ ] Dependency data auto-populated from Feature Breakdown output (persisted in workflow JSON `depends_on` arrays)
- [ ] SVG curved connector arrows drawn between dependent feature lanes (source → target)
- [ ] Dependent features show `⛓ needs {ID}` tag in lane label
- [ ] Independent features show `⇉ Parallel` badge in lane label
- [ ] Dependencies toggle button shows/hides all dependency visualizations
- [ ] Working Item Selector dropdown: lists features with current stage and next action; selecting highlights lane
- [ ] Clicking action on independent feature: starts immediately (no dependency check needed)
- [ ] Clicking action on dependent feature with unfinished dependency: confirm dialog with warning
- [ ] True parallel execution: multiple concurrent agent sessions allowed for independent features

**Dependencies:**
- FEATURE-036-A (Workflow Manager — dependency data, feature state)
- FEATURE-036-B (Workflow View Shell — panel container)
- FEATURE-036-C (Stage Ribbon & Action Execution — action button mechanics)

**Technical Considerations:**
- SVG arrows rendered dynamically based on lane positions; re-drawn on window resize
- Dependency check is synchronous API call before action dispatch
- Working Item Selector disabled before Feature Breakdown (no features to show)

---

### FEATURE-036-E: Deliverables, Polling & Lifecycle

**Version:** v1.0
**Brief Description:** Deliverables display, real-time polling, and workflow lifecycle management — categorized artifact links, file existence verification, 7-second polling for state updates, auto-archive after 30 days, error recovery.

**Acceptance Criteria:**
- [ ] Collapsible deliverables section shows categorized artifacts: Ideas, Mockups, Requirements, Implementations, Quality Reports
- [ ] Each deliverable links to original file location; missing files show "⚠️ not found"
- [ ] Deliverables Resolver reads paths from workflow JSON, verifies file existence on disk
- [ ] Frontend polls Workflow Manager API every 7 seconds for state changes
- [ ] On state change detected, UI refreshes affected panels/lanes without full page reload
- [ ] Polling does not cause noticeable UI lag or CPU usage
- [ ] Workflows with no activity for 30 days auto-archived to `engineering-workflow/archive/`
- [ ] Archived workflows not shown in active list (separate archive view optional for v2)
- [ ] Error recovery: failed actions show retry button; status unknown after 10min shows manual override
- [ ] Manual override: right-click action → "Mark as Done" or "Reset to Pending"

**Dependencies:**
- FEATURE-036-A (Workflow Manager — state API, deliverable paths)
- FEATURE-036-B (Workflow View Shell — panel container for deliverables section)

**Technical Considerations:**
- Polling uses `setInterval` with change detection (compare JSON hash or `last_activity` timestamp)
- Auto-archive runs on app startup and periodically (check `last_activity` vs current time)
- Deliverables Resolver is a backend endpoint, not frontend file system access

> **⚠️ CR Impact Note** (added 2026-02-20, ref: EPIC-038)
> - **Change:** Deliverable viewer enhanced from basic artifact links to file-tree listing with clickable files and inline markdown preview for folder-type deliverables
> - **Affected FRs:** FR-036.16 (Deliverables Section), FR-036.23 (Deliverables Resolver)
> - **Action Required:** FEATURE-036-E specification update needed to add file-tree browsing and inline markdown preview capability for deliverable folders
> - **New Feature Ref:** EPIC-038 — see requirement-details-part-11.md

---

## Conflict Review Summary

| Existing Feature | Overlap Type | Decision | Rationale |
|-----------------|--------------|----------|-----------|
| FEATURE-008 (Workplace/Idea Management) | Navigation competition — both occupy middle content area | **New standalone feature** | Different lifecycle: Workplace creates ideas; Engineering Workflow orchestrates delivery of those ideas. Coexist as separate top-nav entries. |
| FEATURE-033 (App-Agent Interaction MCP) | Infrastructure reuse — both use app↔agent MCP communication | **New standalone feature with dependency** | New MCP tools (`update_workflow_status`, `get_workflow_state`) owned by this feature; depends on FEATURE-033 for MCP infrastructure. No CR on FEATURE-033. |

> **⚠️ CR Impact Note** (added 2026-03-30, ref: EPIC-052 / IDEA-036)
> - **Change:** The MCP tools `update_workflow_action` and `get_workflow_state` (registered on `x-ipe-app-and-agent-interaction` MCP server) are being replaced by standalone scripts `workflow_update_action.py` and `workflow_get_state.py` in `x-ipe-tool-x-ipe-app-interactor` skill. Scripts perform direct JSON file I/O with fcntl locking — no Flask backend dependency.
> - **Affected FRs:** FR-036.34 (MCP tool registration), FR-036.35 (Workflow state persistence via MCP)
> - **Action Required:** All 13 task-based skills that call `update_workflow_action` MCP tool must be updated to invoke the replacement script. FEATURE-036-A's MCP dependency on FEATURE-033 becomes obsolete after migration.
> - **New Feature Ref:** EPIC-052 — see [requirement-details-part-21.md](x-ipe-docs/requirements/requirement-details-part-21.md)
| FEATURE-005/029 (Console/Terminal) | Session management — both create/manage console sessions | **New standalone feature with dependency** | Engineering Workflow reuses console APIs without modification. Dependency ensures console refactoring is flagged. |

---

### CR-EPIC: Introduce Epic Layer

**Version:** v1.0
**Brief Description:** Introduce an Epic grouping layer into X-IPE's requirement management workflow. Epics sit above Features, providing a formal hierarchy (`EPIC-{nnn}` → `FEATURE-{nnn}-{A|B|C}`) that replaces ad-hoc sub-feature patterns. This is a **process/skill Change Request** affecting the entire requirement-to-feature workflow.

> Source: IDEA-022 (CR-Introduce Epic)
> Status: Proposed
> Priority: High
> Idea Summary: [idea-summary-v2.md](x-ipe-docs/ideas/022. CR-Introduce Epic/idea-summary-v2.md)

#### Project Overview

Currently, X-IPE uses a flat feature structure (`FEATURE-{nnn}`) that organically splits into sub-features when scope grows (e.g., `FEATURE-030-B-THEME`, `FEATURE-030-B-MOCKUP`). This ad-hoc splitting lacks a formal parent concept, shared artifact storage, and consistent naming. The Epic layer formalizes this grouping.

#### User Request

The user wants:
1. An Epic layer above Features in the requirement management workflow
2. Requirement Gathering creates Epic folders (not Feature folders)
3. Feature Breakdown creates Feature sub-folders under Epics
4. Mockups stored at Epic level, referenced (not duplicated) by Features
5. Every requirement always gets an Epic (even single-feature requirements)
6. All existing features retroactively organized under Epics
7. All related skills updated to support the Epic hierarchy

#### Clarifications

| Question | Answer |
|----------|--------|
| Migration of existing features | Update all skills first, then retroactively re-organize all existing features under Epics |
| Epic-level artifacts | Epic folder holds mockups only; no specification.md at Epic level; all functional specs live in Features |
| Standalone features | Always Epic — every requirement creates an Epic, even for single-feature work (consistency) |
| Feature folder naming inside Epic | Full ID: `EPIC-030/FEATURE-030-A/` (not abbreviated) |
| features.md tracking | Add Epic ID column to flat table, sorted by Epic ID |
| Skills to update | All skills that reference FEATURE- patterns, plus requirement-details templates, change-request skill, git commit format |

#### High-Level Requirements

##### Folder Structure Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EPIC.1 | **Epic folder creation** — Requirement Gathering skill creates `EPIC-{nnn}/` folder under `x-ipe-docs/requirements/` with `mockups/` sub-directory | P0 |
| FR-EPIC.2 | **Feature sub-folders** — Feature Breakdown skill creates `FEATURE-{nnn}-{X}/` sub-folders under `EPIC-{nnn}/` | P0 |
| FR-EPIC.3 | **Mockup storage** — Mockups created during Requirement Gathering stored in `EPIC-{nnn}/mockups/`; Features reference `../mockups/` | P0 |
| FR-EPIC.4 | **No Epic-level specification** — No `specification.md` at Epic level; all functional specs live in Feature sub-folders | P0 |

##### Naming Convention Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EPIC.5 | **Epic naming** — Epics use `EPIC-{nnn}` format (e.g., `EPIC-030`) | P0 |
| FR-EPIC.6 | **Feature naming** — Features use `FEATURE-{nnn}-{A|B|C...}` format where `{nnn}` matches parent Epic | P0 |
| FR-EPIC.7 | **Always Epic** — Every requirement creates an Epic, including single-feature requirements | P0 |

##### Tracking Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EPIC.8 | **features.md Epic column** — Add `Epic ID` column to features.md flat table; sort rows by Epic ID | P0 |
| FR-EPIC.9 | **Epic status derivation** — Epic status computed dynamically from constituent Feature statuses (all completed → completed; any in_progress → in_progress; etc.) | P1 |

##### Skill Update Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EPIC.10 | **Requirement Gathering skill** — Create `EPIC-{nnn}/` folder; define Epic-level ACs in requirement-details; store mockups at Epic level | P0 |
| FR-EPIC.11 | **Feature Breakdown skill** — Create `FEATURE-{nnn}-{X}/` sub-folders under Epic; distribute Epic ACs to Features | P0 |
| FR-EPIC.12 | **Feature Board Management skill** — Support Epic ID column in features.md; Epic-based sorting | P0 |
| FR-EPIC.13 | **Change Request skill** — Support Epic-aware CR handling; CRs reference `EPIC-{nnn}/FEATURE-{nnn}-{X}/` paths | P0 |
| FR-EPIC.14 | **Feature lifecycle skills** — Update path references in: feature-refinement, technical-design, test-generation, code-implementation, feature-acceptance-test, feature-closing | P0 |
| FR-EPIC.15 | **Git version control skill** — Update commit message format to support Epic references | P1 |

##### Requirement-Details Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EPIC.16 | **Epic headers** — requirement-details files use `## EPIC-{nnn}` headers instead of `## FEATURE-{nnn}` | P0 |
| FR-EPIC.17 | **Splitting heuristic** — Keep range-based splitting but with Epic headers | P0 |
| FR-EPIC.18 | **Index update** — requirement-details-index.md references Epic ranges, not Feature ranges | P0 |

##### Migration Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EPIC.19 | **Retroactive migration** — All existing features organized under Epics after skill updates complete | P0 |
| FR-EPIC.20 | **Legacy grouping** — Standalone features (e.g., `FEATURE-001`) → `EPIC-001/FEATURE-001-A/`; existing sub-features (e.g., `FEATURE-022-A/B/C/D`) → `EPIC-022/FEATURE-022-A/B/C/D/` | P0 |
| FR-EPIC.21 | **Link integrity** — All spec links in features.md and skill examples must resolve after migration | P0 |
| FR-EPIC.22 | **Archive preservation** — Task board archives (`task-board-archive-*.md`) are NOT modified; historical `FEATURE-XXX` references preserved | P0 |

#### Acceptance Criteria

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-EPIC.1 | Requirement Gathering skill is invoked | Agent creates new requirement | `EPIC-{nnn}/` folder created with `mockups/` sub-directory |
| AC-EPIC.2 | Epic folder exists | Feature Breakdown skill runs | `FEATURE-{nnn}-{A}/` sub-folder created under `EPIC-{nnn}/` |
| AC-EPIC.3 | Features exist under Epic | User opens features.md | Epic ID column visible, rows sorted by Epic ID |
| AC-EPIC.4 | Single-feature requirement created | Requirement Gathering completes | Epic folder created even for single feature (consistency) |
| AC-EPIC.5 | Feature spec references mockup | Agent opens specification | Path resolves to `../mockups/` in parent Epic folder |
| AC-EPIC.6 | Change Request filed on existing feature | CR skill runs | CR references `EPIC-{nnn}/FEATURE-{nnn}-{X}/` paths correctly |
| AC-EPIC.7 | All skills updated | Migration runs | All existing features reorganized under `EPIC-{nnn}/` folders |
| AC-EPIC.8 | Migration completed | All links in features.md checked | Every specification link resolves to correct file |
| AC-EPIC.9 | Migration completed | Task board archives inspected | Historical `FEATURE-XXX` references unchanged |
| AC-EPIC.10 | requirement-details file opened | Reader inspects headers | `## EPIC-{nnn}` headers used instead of `## FEATURE-{nnn}` |

#### Migration Strategy

**Phase 1:** Update all skills to support Epic-based folder structure for new requirements (backward-compatible — can still read old `FEATURE-XXX/` paths)

**Phase 2:** Migrate existing feature folders:
- `FEATURE-001/` → `EPIC-001/FEATURE-001-A/`
- `FEATURE-022-A/B/C/D/` → `EPIC-022/FEATURE-022-A/B/C/D/`
- `FEATURE-030-B/`, `FEATURE-030-B-THEME/`, `FEATURE-030-B-MOCKUP/` → `EPIC-030/FEATURE-030-B/`, `EPIC-030/FEATURE-030-B-THEME/`, `EPIC-030/FEATURE-030-B-MOCKUP/`

**Phase 3:** Update references in features.md, requirement-details-index.md, requirement-details parts

**Phase 4:** Validate all links resolve correctly

**Phase 5:** (Deferred) Remove old-path compatibility from skills

**Rollback:** Each phase is a single atomic commit; revert restores previous state.

#### Skills Blast Radius

| Impact Level | Skills | Changes Needed |
|--------------|--------|----------------|
| Critical | requirement-gathering, feature-breakdown, feature-board-management, change-request | Core workflow changes: Epic folder creation, Feature sub-folder creation, features.md column, CR paths |
| High | feature-refinement, feature-acceptance-test, feature-closing, technical-design, code-implementation, test-generation | Path updates: `FEATURE-XXX/` → `EPIC-XXX/FEATURE-XXX-X/` |
| Medium | git-version-control, requirement-details templates | Commit message format, file-splitting heuristic |
| Low | Various skill references/examples | Pattern updates in documentation |

#### Dependencies

- All existing features (source data for migration)
- EPIC-036 (Engineering Workflow View) — should incorporate Epic concept in its feature lanes when designed

#### Constraints

- **Phased rollout** — Skills updated first, then data migrated (never simultaneously)
- **No archive modification** — Task board archives preserve historical `FEATURE-XXX` references
- **Single-feature Epics** — Consistency rule: every requirement gets an Epic, no exceptions
- **In-flight features** — Features with active tasks should complete current workflow before migration
- **Epic is a namespace, not a spec** — No specification.md at Epic level; Epic folder is a container for mockups and Feature sub-folders

#### Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-035-A | EPIC-035 | Epic Core Workflow Skills | v1.0 | Update requirement-gathering and feature-breakdown skills to create Epic folders, Feature sub-folders, and Epic-level naming conventions | None |
| FEATURE-035-B | EPIC-035 | Feature Board Epic Tracking | v1.0 | Add Epic ID column to features.md, update feature-board-management skill, Epic-based sorting and derived status | FEATURE-035-A |
| FEATURE-035-C | EPIC-035 | Feature Lifecycle Skill Updates | v1.0 | Update change-request, feature-refinement, technical-design, test-generation, code-implementation, feature-acceptance-test, feature-closing, and git-version-control skills for Epic-aware paths | FEATURE-035-A, FEATURE-035-B |
| FEATURE-035-D | EPIC-035 | Requirement-Details Epic Format | v1.0 | Update requirement-details files to use EPIC-{nnn} headers, update splitting heuristic, update index format | FEATURE-035-A |
| FEATURE-035-E | EPIC-035 | Retroactive Feature Migration | v1.0 | Migrate all existing features into EPIC-{nnn}/FEATURE-{nnn}-{X} folder structure, update all references, validate link integrity | FEATURE-035-A, FEATURE-035-B, FEATURE-035-C, FEATURE-035-D |

#### Feature Details

---

##### FEATURE-035-A: Epic Core Workflow Skills

**Version:** v1.0
**Brief Description:** Update the two core workflow skills (requirement-gathering and feature-breakdown) to support the Epic layer. This is the foundation — all other features depend on it.

**Acceptance Criteria:**
- [ ] Requirement Gathering skill creates `EPIC-{nnn}/` folder with `mockups/` sub-directory
- [ ] Requirement Gathering skill defines Epic-level ACs in requirement-details using `## EPIC-{nnn}` headers
- [ ] Requirement Gathering stores mockups in `EPIC-{nnn}/mockups/`
- [ ] Feature Breakdown skill creates `FEATURE-{nnn}-{X}/` sub-folders under `EPIC-{nnn}/`
- [ ] Every requirement always creates an Epic (single-feature Epics for simple requirements)
- [ ] Epic naming follows `EPIC-{nnn}` format; Feature naming follows `FEATURE-{nnn}-{A|B|C}` format
- [ ] Feature `{nnn}` always matches parent Epic's number

**Dependencies:** None (foundation)

**Technical Considerations:**
- Modify SKILL.md files for both skills
- Update references, templates, and examples in both skills
- Backward compatibility: skills should still work with old `FEATURE-XXX/` paths during transition

---

##### [RETIRED by EPIC-055/EPIC-056] FEATURE-035-B: Feature Board Epic Tracking

> **⚠️ CR Impact Note** (added 04-03-2026, ref: EPIC-055/EPIC-056)
> - **Change:** EPIC-055 (Task Board Manager) and EPIC-056 (Feature Board Manager) replace the markdown-based features.md with a JSON data layer (`features.json`). The `feature-board-management` skill is being replaced by `x-ipe-tool-feature-board-manager` with CRUD scripts.
> - **Retirement Reason:** Adding an Epic ID column to markdown is superseded by the full JSON migration — `features.json` includes `epic_id` natively in its schema.
> - **Replacement:** See EPIC-055/EPIC-056 in [requirement-details-part-23.md](x-ipe-docs/requirements/requirement-details-part-23.md)

**Version:** v1.0
**Brief Description:** ~~Add Epic ID column to the features.md tracking table and update the feature-board-management skill to support Epic-based organization.~~

**Acceptance Criteria:**
- [ ] ~~features.md table includes `Epic ID` column~~ → Superseded by EPIC-056 `features.json` schema
- [ ] ~~features.md rows sorted by Epic ID~~ → Superseded by EPIC-056 query scripts
- [ ] ~~feature-board-management skill populates Epic ID when creating features~~ → Superseded by `x-ipe-tool-feature-board-manager`
- [ ] Epic status derivable from constituent Feature statuses (all completed → completed, any in_progress → in_progress) → **Carried forward** into EPIC-056
- [ ] ~~Specification links updated to `EPIC-{nnn}/FEATURE-{nnn}-{X}/specification.md` paths~~ → Superseded by EPIC-056 JSON schema

**Dependencies:** FEATURE-035-A

**Technical Considerations:**
- Epic status is computed, not stored — no separate column needed
- Sort order: primary by Epic ID, secondary by Feature suffix letter

---

##### [RETIRED by EPIC-057] FEATURE-035-C: Feature Lifecycle Skill Updates

> **⚠️ CR Impact Note** (added 04-03-2026, ref: EPIC-057)
> - **Change:** EPIC-057 (Web Pages + Migration) includes updating ~34 referencing skills to use the new JSON-based board managers instead of markdown editing. This subsumes the 10+ skill updates planned here.
> - **Retirement Reason:** Updating skills for Epic-aware markdown paths is superseded by updating them to use JSON APIs/scripts entirely — a more complete migration.
> - **Replacement:** See EPIC-057 in [requirement-details-part-23.md](x-ipe-docs/requirements/requirement-details-part-23.md)

**Version:** v1.0
**Brief Description:** ~~Update all feature lifecycle skills to use Epic-aware paths (`EPIC-{nnn}/FEATURE-{nnn}-{X}/`) instead of flat `FEATURE-{nnn}/` paths.~~

**Acceptance Criteria:**
- [ ] ~~Change Request skill uses `EPIC-{nnn}/FEATURE-{nnn}-{X}/` paths for CR files~~ → Superseded by EPIC-057 JSON migration
- [ ] ~~Feature Refinement skill reads/writes specs at `EPIC-{nnn}/FEATURE-{nnn}-{X}/specification.md`~~ → Superseded
- [ ] ~~Technical Design skill uses Epic-aware paths~~ → Superseded
- [ ] ~~Test Generation skill uses Epic-aware paths~~ → Superseded
- [ ] ~~Code Implementation skill uses Epic-aware paths~~ → Superseded
- [ ] ~~Feature Acceptance Test skill uses Epic-aware paths~~ → Superseded
- [ ] ~~Feature Closing skill uses Epic-aware paths~~ → Superseded
- [ ] ~~Git version control skill supports Epic references in commit messages~~ → **Carried forward** into EPIC-057

**Dependencies:** FEATURE-035-A, FEATURE-035-B

**Technical Considerations:**
- 10+ skills to update — mostly path references in SKILL.md files and examples
- All changes are to agent skills (SKILL.md), not application code
- Commit message format may include `[EPIC-{nnn}]` prefix

---

##### FEATURE-035-D: Requirement-Details Epic Format

**Version:** v1.0
**Brief Description:** Update requirement-details files and templates to use `EPIC-{nnn}` headers instead of `FEATURE-{nnn}` headers. Update the splitting heuristic and index format.

**Acceptance Criteria:**
- [ ] requirement-details files use `## EPIC-{nnn}` section headers
- [ ] requirement-details-template.md updated for Epic format
- [ ] File splitting heuristic works with Epic-based grouping
- [ ] requirement-details-index.md references Epic ranges instead of Feature ranges
- [ ] Feature sub-sections nest under Epic headers

**Dependencies:** FEATURE-035-A

**Technical Considerations:**
- Update the requirement-gathering skill's template reference
- Update the feature-breakdown skill's file-splitting reference
- Index format: `EPIC-001 to EPIC-011` instead of `FEATURE-001 to FEATURE-011`

---

##### FEATURE-035-E: Retroactive Feature Migration

**Version:** v1.0
**Brief Description:** Migrate all existing features into the `EPIC-{nnn}/FEATURE-{nnn}-{X}/` folder structure. Update features.md, requirement-details files, and validate all links.

**Acceptance Criteria:**
- [ ] All standalone features (e.g., `FEATURE-001/`) moved to `EPIC-001/FEATURE-001-A/`
- [ ] All existing sub-features (e.g., `FEATURE-022-A/B/C/D/`) moved to `EPIC-022/FEATURE-022-A/B/C/D/`
- [ ] features.md updated with Epic ID column for all existing features
- [ ] requirement-details parts 1-9 updated with Epic headers
- [ ] requirement-details-index.md updated with Epic ranges
- [ ] All specification links in features.md resolve correctly after migration
- [ ] Task board archives (`task-board-archive-*.md`) are NOT modified
- [ ] Active task board references updated for in-progress features only

**Dependencies:** FEATURE-035-A, FEATURE-035-B, FEATURE-035-C, FEATURE-035-D

**Technical Considerations:**
- This is a data migration, not a code change
- Must be executed after ALL skill updates are complete
- Atomic commit per migration phase for rollback safety
- In-flight features should complete current workflow before migration
