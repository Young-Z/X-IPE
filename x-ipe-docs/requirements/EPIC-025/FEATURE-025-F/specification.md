# Feature Specification: KB Navigation & Polish

> Feature ID: FEATURE-025-F  
> Version: v1.0  
> Status: Refined  
> Last Updated: 03-03-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-03-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| KB Landing View | HTML | [mockups/knowledge-base-v1.html](mockups/knowledge-base-v1.html) | KB sidebar with section tabs (Landing/Topics), badges, tree views | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".  
> Mockups marked as "outdated" are directional references only — do not use for AC comparison.

## Overview

**What:** FEATURE-025-F adds section tabs ("Landing" and "Topics") to the KB sidebar, item-count badges on tabs, and UX refinements for a polished navigation experience. Currently the KB sidebar shows a single flat tree with both landing files and topic folders mixed together, and the content area auto-routes to either the Landing view (kbLanding) or Topics view (kbTopics) based on whether topics exist. This feature replaces that auto-routing with explicit tab-based navigation, giving users direct control over which section they see.

**Why:** Users currently cannot switch between Landing and Topics views manually — the system decides which view to show. If topics exist, the landing zone becomes inaccessible from the content area (only visible in the sidebar tree). Section tabs provide clear, predictable navigation and surface the item count for each section at a glance, improving discoverability and workflow efficiency.

**Who:**
- End users who upload files to landing and want to easily toggle back to review them after topics are created
- Knowledge managers who need to see both raw uploads and organized topics without losing context
- All KB users who benefit from clearer sidebar navigation structure

## User Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-1 | As a **user**, I want to **see "Landing" and "Topics" tabs in the KB sidebar** so that **I can quickly switch between the two sections without relying on auto-routing** | Must |
| US-2 | As a **user**, I want to **see a badge on the Landing tab showing the file count** so that **I know how many files are awaiting processing at a glance** | Must |
| US-3 | As a **user**, I want the **active tab to be visually highlighted** so that **I always know which section I'm viewing** | Must |
| US-4 | As a **user**, I want **clicking a tab to switch both the sidebar tree and the content panel** so that **each section has its own coherent view** | Must |
| US-5 | As a **user**, I want the **Topics tab to show a badge with the topic count** so that **I can see how many topics exist at a glance** | Should |
| US-6 | As a **user**, I want the **search box to filter items within the active tab's section only** so that **results are contextual to what I'm viewing** | Should |

## Acceptance Criteria

### 1. Section Tabs (AC-1.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-1.1 | Sidebar MUST have two tabs: "Landing" and "Topics" displayed below the sidebar header | Navigate to KB → two tabs visible between header and search box |
| AC-1.2 | Landing tab MUST show an inbox icon (`bi-inbox`) and the label "Landing" | Inspect Landing tab → icon and label present |
| AC-1.3 | Topics tab MUST show a layers icon (`bi-layers`) and the label "Topics" | Inspect Topics tab → icon and label present |
| AC-1.4 | Tabs MUST be arranged horizontally, each taking equal width (flex: 1) | Measure tab widths → both equal |
| AC-1.5 | UI layout of section tabs MUST match the approved mockup (knowledge-base-v1.html) for tab styling, spacing, and color | Visual comparison with mockup |
| AC-1.6 | Visual styling (colors, spacing, typography) of section tabs MUST be consistent with mockup (knowledge-base-v1.html) | Visual comparison with mockup |

### 2. Tab Badges (AC-2.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-2.1 | Landing tab MUST display a badge showing the count of files in `landing/` | Upload 3 files → badge shows "3" |
| AC-2.2 | Topics tab MUST display a badge showing the count of topics | Create 2 topics → badge shows "2" |
| AC-2.3 | Badge counts MUST update dynamically when files are uploaded/deleted or topics change | Upload a file → landing badge increments without page reload |
| AC-2.4 | Badge styling MUST match mockup (knowledge-base-v1.html): pill shape, semi-transparent on active tab | Visual comparison with mockup |

### 3. Tab Switching (AC-3.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-3.1 | Clicking the "Landing" tab MUST show the landing tree in the sidebar and render the Landing content view (kbLanding) | Click Landing tab → landing file grid appears in content area |
| AC-3.2 | Clicking the "Topics" tab MUST show the topics list in the sidebar and render the Topics content view (kbTopics) | Click Topics tab → topics sidebar and detail panel appear in content area |
| AC-3.3 | The active tab MUST have a visually distinct style (filled background, white text) matching the mockup | Click tab → active class applied with accent background |
| AC-3.4 | Inactive tabs MUST have subtle tertiary text color and transparent background | Inspect inactive tab → no background, muted text |
| AC-3.5 | Tab state MUST persist within the same session (switching to another workplace submenu and back should restore the last active tab) | Switch away and back → same tab active |

### 4. Sidebar Tree View Updates (AC-4.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-4.1 | When Landing tab is active, sidebar tree MUST show only landing folder files (same as current `landing/` group) | Activate Landing → only landing files in tree |
| AC-4.2 | When Topics tab is active, sidebar tree MUST show only topic folders with their files | Activate Topics → only topic folders in tree |
| AC-4.3 | Search box MUST filter items within the currently active tab's section | Search in Landing tab → only landing files filtered; search in Topics tab → only topics filtered |
| AC-4.4 | Collapsible folder toggle (chevron icon) MUST continue to work in both tree views | Click chevron → folder expands/collapses |

### 5. Interactive Elements (AC-5.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-5.1 | Interactive elements shown in mockup (knowledge-base-v1.html) for section tabs MUST be present and functional | Tabs clickable, badges visible, hover effects working |
| AC-5.2 | Tab hover MUST show a subtle background highlight (per mockup) | Hover over inactive tab → background changes |
| AC-5.3 | Tab transition MUST be smooth (CSS transition ~150ms) | Click tab → transition is not jarring |

### 6. Default Tab Selection (AC-6.x)

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-6.1 | On initial KB load, if topics exist, the "Topics" tab MUST be active by default | Load KB with topics → Topics tab selected |
| AC-6.2 | On initial KB load, if no topics exist, the "Landing" tab MUST be active by default | Load KB with no topics → Landing tab selected |

## Functional Requirements

| # | Requirement | Input | Process | Output |
|---|-------------|-------|---------|--------|
| FR-1 | Tab rendering | KB index loaded | Render two tabs in sidebar between header and search box | Tabs visible with icons and labels |
| FR-2 | Badge calculation | KB index files + topics list | Count `landing/` files for Landing badge; count topics array length for Topics badge | Badge numbers displayed |
| FR-3 | Tab switch handler | Tab click event | Update active tab class, re-render sidebar tree for selected section, render corresponding content view | UI updated to show selected section |
| FR-4 | Badge refresh | File upload/delete/topic change | Recalculate badge counts from latest index data | Badge values updated |
| FR-5 | Tab state persistence | Tab selection | Store active tab in kbCore state | Restored on re-navigation |

## Non-Functional Requirements

| # | Requirement | Priority |
|---|-------------|----------|
| NFR-1 | Tab switch MUST complete rendering within 100ms for up to 1000 files | Should |
| NFR-2 | Badge update MUST not cause full page re-render (targeted DOM update only) | Should |
| NFR-3 | Tab CSS MUST support both light and dark themes using existing CSS variables | Must |
| NFR-4 | No new API endpoints required — all data available from existing `/api/kb/index` and `/api/kb/topics` | Must |

## UI/UX Requirements

### Component Inventory (from mockup)

| Component | Location | Description |
|-----------|----------|-------------|
| Section tabs container | Below sidebar header, above search box | Horizontal flex container with 4px gap, 8px/12px padding, bottom border |
| Landing tab button | Left side of tabs container | Icon (bi-inbox) + "Landing" label + badge (file count) |
| Topics tab button | Right side of tabs container | Icon (bi-layers) + "Topics" label + optional badge (topic count) |
| Active tab style | Whichever tab is selected | Accent background color, white text |
| Badge pill | Inside each tab | 10px font, 2px/6px padding, border-radius 10px, semi-transparent white bg on active tab |

### User Interaction Flows

1. **Tab Switch Flow:** User clicks inactive tab → tab becomes active (accent bg) → sidebar tree re-renders for that section → content panel switches to corresponding view
2. **Badge Update Flow:** User uploads/deletes file → index refreshes → badge counts recalculate → badge DOM updated
3. **Search Interaction:** User types in search → filters only items in currently active tab's section

### States

| State | Behavior |
|-------|----------|
| Default (with topics) | Topics tab active, Topics tree in sidebar, kbTopics in content |
| Default (no topics) | Landing tab active, Landing tree in sidebar, kbLanding in content |
| Empty KB | Landing tab active, empty state message in tree and content |
| Search active | Filters within current tab's section only |

## Dependencies

| Dependency | Type | Status | Integration Points |
|------------|------|--------|-------------------|
| FEATURE-025-D | Feature | Complete | Topics data (`kbTopics.render()`, `/api/kb/topics`) |
| FEATURE-025-E | Feature | Complete | Search & Preview (`kbSearch`, sidebar search input) |
| FEATURE-025-A | Feature | Complete | Core infrastructure (`kbCore`, `/api/kb/index`) |
| FEATURE-025-B | Feature | Complete | Landing view (`kbLanding.render()`) |

## Business Rules

| # | Rule |
|---|------|
| BR-1 | Badge count for Landing tab = number of files where `path.startsWith('landing/')` |
| BR-2 | Badge count for Topics tab = length of `kbCore.topics` array |
| BR-3 | Default active tab = Topics (if `topics.length > 0`), else Landing |
| BR-4 | Tab state is session-level only — does not persist across page reloads (resets to default) |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| 0 landing files, 0 topics | Landing tab active, badge shows "0", empty state in content |
| 0 landing files, N topics | Topics tab active by default, Landing badge shows "0" |
| N landing files, 0 topics | Landing tab active by default, Topics badge shows "0" |
| File uploaded while on Topics tab | Landing badge increments; user stays on Topics tab |
| Topic deleted while on Topics tab | Topics badge decrements; if no topics left, auto-switch to Landing tab |
| Rapid tab switching | Debounce not needed — each tab renders from in-memory data (no API calls) |
| Search term active when switching tabs | Search input text preserved; filter re-applied to new section's items |

## Out of Scope

- Drag-and-drop between Landing and Topics tabs (manual file moves)
- Third-party plugin tabs or custom user tabs
- Tab reordering or hiding
- Keyboard shortcut for tab switching (potential future enhancement)
- Nested sub-tabs within Landing or Topics

## Technical Considerations

- Section tabs should be added to the `kbCore.render()` HTML template between the sidebar header and search box
- Tab switching should update `kbCore` state (`activeTab`) and call appropriate render methods (`kbLanding.render()` or `kbTopics.render()`)
- Existing `renderTree()` method in kbCore needs to be aware of the active tab to filter displayed items
- Badge counts derive from already-loaded `kbCore.index.files` and `kbCore.topics` — no new API calls needed
- CSS should use existing KB CSS variables and patterns from `kb-core.css`
- The `renderWelcome()` auto-routing logic should be replaced with explicit tab-driven rendering

## Open Questions

None — all requirements are clear from mockup and existing implementation.
