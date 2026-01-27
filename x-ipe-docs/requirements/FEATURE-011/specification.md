# Feature Specification: Stage Toolbox

> Feature ID: FEATURE-011  
> Version: v1.0  
> Status: Completed  
> Last Updated: 01-24-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 01-24-2026 | Initial specification from idea-summary-v2 and mockup v2 |
| v1.0 | 01-24-2026 | Feature completed - all 18 ACs verified |

## Overview

The Stage Toolbox transforms the current Ideation Toolbox (limited to ideation stage only with dropdown/inline UI) into a comprehensive tool management modal that supports all development stages. The modal provides an organized, scalable interface using accordion sections for five development stages: Ideation, Requirement, Feature, Quality, and Refactoring.

Each stage contains sub-phases with configurable tools that can be toggled on/off. The configuration is stored project-wide in `x-ipe-docs/config/tools.json` with immediate persistence on every toggle change. The feature includes automatic migration from the legacy `.ideation-tools.json` format.

This feature is designed for developers and project managers who need to configure which AI-assisted tools are available at each stage of the development lifecycle within X-IPE.

## User Stories

- As a **developer**, I want to **configure which tools are enabled for each development stage**, so that **I only see relevant tools during my workflow**.

- As a **project manager**, I want to **see all available stages and their tools in one place**, so that **I can understand and configure the project's tool configuration**.

- As a **user migrating from older versions**, I want to **have my existing tool configuration preserved**, so that **I don't lose my settings when upgrading**.

## Linked Mockups

| Mockup | Path | Status |
|--------|------|--------|
| Stage Toolbox Modal (Light Theme) | [mockups/stage-toolbox-modal.html](mockups/stage-toolbox-modal.html) | ✅ Approved |

## Acceptance Criteria

### Modal UI
- [x] AC-1.1: Modal opens via top bar toolbox icon button
- [x] AC-1.2: Modal uses light theme matching mockup v2
- [x] AC-1.3: Modal width is 680px with max-height 85vh
- [x] AC-1.4: Modal closes via X button or clicking overlay
- [x] AC-1.5: ESC key closes modal

### Accordion Structure
- [x] AC-2.1: 5 accordion sections (Ideation, Requirement, Feature, Quality, Refactoring)
- [x] AC-2.2: Each section has color-coded icon (💡🟡, 📋🔵, ⚙️🟢, ✅🟣, 🔄🔴)
- [x] AC-2.3: Click header to expand/collapse section
- [x] AC-2.4: Only one section expanded at a time
- [x] AC-2.5: "N active" badge shows enabled tool count per stage

### Ideation Stage (Functional)
- [x] AC-3.1: Three sub-phases: Ideation, Mockup, Sharing
- [x] AC-3.2: Ideation phase has tools: `antv-infographic`, `mermaid`
- [x] AC-3.3: Mockup phase has tool: `frontend-design`
- [x] AC-3.4: Sharing phase shows "No tools configured"
- [x] AC-3.5: Toggle switches enable/disable each tool
- [x] AC-3.6: Toggle changes persist immediately to config file

### Placeholder Stages
- [x] AC-4.1: Requirement, Feature, Quality, Refactoring show "placeholder" badge
- [x] AC-4.2: Sub-phases show "Coming soon..." empty state
- [x] AC-4.3: No functional toggles in placeholder stages

### Configuration
- [x] AC-5.1: Config stored in `x-ipe-docs/config/tools.json`
- [x] AC-5.2: Config uses nested 3-level structure (stage > phase > tool)
- [x] AC-5.3: Auto-create `x-ipe-docs/config/` directory if not exists
- [x] AC-5.4: Auto-migrate from `.ideation-tools.json` if exists
- [x] AC-5.5: Delete old `.ideation-tools.json` after successful migration

### Top Bar Integration
- [x] AC-6.1: Toolbox icon button added to top bar (right side)
- [x] AC-6.2: Green accent color for toolbox button
- [x] AC-6.3: Tooltip shows "Stage Toolbox" on hover
- [x] AC-6.4: Remove toolbox from Workplace panel

## Functional Requirements

### FR-1: Modal Display

**Description:** Display the Stage Toolbox modal when user clicks the top bar icon.

**Details:**
- Input: Click on toolbox icon in top bar
- Process: Render modal overlay with accordion content
- Output: Modal displayed with Ideation stage expanded by default

### FR-2: Accordion Navigation

**Description:** Allow users to expand/collapse stage sections.

**Details:**
- Input: Click on accordion header
- Process: Collapse currently expanded section, expand clicked section
- Output: Only one section visible at a time (accordion behavior)

### FR-3: Tool Toggle

**Description:** Enable/disable individual tools via toggle switches.

**Details:**
- Input: Toggle switch click
- Process: Update tool state in memory, persist to `x-ipe-docs/config/tools.json`
- Output: Toggle visual state changes, badge count updates, file written

### FR-4: Configuration Loading

**Description:** Load tool configuration on application start.

**Details:**
- Input: Application initialization
- Process: 
  1. Check for `x-ipe-docs/config/tools.json`
  2. If not exists, check for `.ideation-tools.json` (legacy)
  3. If legacy exists, migrate and delete old file
  4. If neither exists, create default config
- Output: Configuration loaded into memory

### FR-5: Configuration Migration

**Description:** Migrate legacy `.ideation-tools.json` to new format.

**Details:**
- Input: Legacy config file at `x-ipe-docs/ideas/.ideation-tools.json`
- Process:
  1. Read legacy JSON format
  2. Map to new 3-level structure under `stages.ideation`
  3. Write to `x-ipe-docs/config/tools.json`
  4. Delete legacy file
- Output: New config file created, legacy file removed

### FR-6: Top Bar Integration

**Description:** Add toolbox button to application top bar.

**Details:**
- Input: Application renders top bar
- Process: Add button with wrench/tool icon, green accent color
- Output: Button visible in top bar, tooltip on hover

### FR-7: Remove Workplace Toolbox

**Description:** Remove toolbox dropdown from Workplace panel.

**Details:**
- Input: Workplace panel render
- Process: Remove existing toolbox dropdown/inline component
- Output: Workplace panel no longer shows toolbox controls

## Non-Functional Requirements

### NFR-1: Performance

- Modal open time: < 100ms
- Toggle persist time: < 200ms (file write)
- Config load time: < 50ms

### NFR-2: Accessibility

- Modal focusable with keyboard navigation
- ESC key closes modal
- Toggle switches keyboard accessible
- ARIA labels for screen readers

### NFR-3: Responsiveness

- Modal centered on all screen sizes
- Scrollable content area for smaller viewports
- Minimum supported width: 768px

## UI/UX Requirements

**Mockup Reference:** [mockups/stage-toolbox-modal.html](mockups/stage-toolbox-modal.html)

**Visual Design:**
- Light theme with white backgrounds
- Modal width: 680px, max-height: 85vh
- Border radius: 16px for modal, 10px for accordions
- Shadow: `0 25px 50px -12px rgba(0, 0, 0, 0.15)`

**Color Scheme (Stage Icons):**
| Stage | Emoji | Color |
|-------|-------|-------|
| Ideation | 💡 | #f59e0b (amber) |
| Requirement | 📋 | #3b82f6 (blue) |
| Feature | ⚙️ | #10b981 (green) |
| Quality | ✅ | #8b5cf6 (purple) |
| Refactoring | 🔄 | #ef4444 (red) |

**Toggle Switch Design:**
- Width: 42px, Height: 24px
- Off: Gray (#d1d5db)
- On: Green (#10b981)
- Knob: White circle with slide animation

**Accordion Behavior:**
- Click header to expand/collapse
- Only one expanded at a time
- Chevron icon rotates 180° when expanded
- Smooth height transition (300ms ease)

## Dependencies

### Internal Dependencies

- None (standalone feature that replaces FEATURE-008 v1.3 toolbox)

### External Dependencies

- None (uses existing Bootstrap/CSS patterns)

## Business Rules

### BR-1: Single Config File

**Rule:** Only one configuration file exists at any time. After migration, legacy file must be deleted.

### BR-2: Immediate Persistence

**Rule:** Every toggle change must be persisted immediately to disk. No "Save" button required.

### BR-3: Hardcoded Tool Registry

**Rule:** Available tools are hardcoded in the application, not discovered dynamically. Tools for v1.0:
- `ideation.ideation.antv-infographic`
- `ideation.ideation.mermaid`
- `ideation.mockup.frontend-design`

### BR-4: Placeholder Stages Read-Only

**Rule:** Placeholder stages (Requirement, Feature, Quality, Refactoring) display "Coming soon" and have no functional toggles until tools are added in future versions.

## Edge Cases & Constraints

### Edge Case 1: Missing config directory

**Scenario:** `x-ipe-docs/config/` directory does not exist  
**Expected Behavior:** Create directory automatically before writing config file

### Edge Case 2: Corrupted config file

**Scenario:** `x-ipe-docs/config/tools.json` contains invalid JSON  
**Expected Behavior:** Log warning, recreate with default config, preserve any readable values if possible

### Edge Case 3: Migration with partial data

**Scenario:** Legacy `.ideation-tools.json` has some but not all expected tools  
**Expected Behavior:** Migrate available values, use defaults for missing tools

### Edge Case 4: Concurrent access

**Scenario:** Two browser tabs toggle tools simultaneously  
**Expected Behavior:** Last write wins (acceptable for single-user app)

### Edge Case 5: Modal open during file change

**Scenario:** External process modifies `x-ipe-docs/config/tools.json` while modal is open  
**Expected Behavior:** Modal shows stale data until reopened (acceptable for v1.0)

## Out of Scope

- Per-tool configuration/settings (e.g., tool-specific options)
- Idea-level overrides (config applies project-wide only)
- Keyboard shortcuts for tool toggles
- Tool search/filter functionality
- Tool descriptions/documentation in modal
- Dynamic tool discovery from `.github/skills/`
- Real-time sync between browser tabs
- Undo/redo for toggle changes

## Technical Considerations

- **Backend:** New `ToolsConfigService` class in `src/services/`
- **API:** `GET/POST /api/config/tools` endpoint
- **Frontend:** `StageToolboxModal` component (vanilla JS, no framework)
- **Storage:** JSON file at `{project_root}/x-ipe-docs/config/tools.json`
- **Migration:** One-time migration logic in config service initialization

**Config File Schema:**
```json
{
  "version": "2.0",
  "stages": {
    "ideation": {
      "ideation": {
        "antv-infographic": false,
        "mermaid": false
      },
      "mockup": {
        "frontend-design": true
      },
      "sharing": {}
    },
    "requirement": {
      "gathering": {},
      "analysis": {}
    },
    "feature": {
      "design": {},
      "implementation": {}
    },
    "quality": {
      "testing": {},
      "review": {}
    },
    "refactoring": {
      "analysis": {},
      "execution": {}
    }
  }
}
```

## Open Questions

- [x] Migration behavior → Delete old file after migration
- [x] Tool discovery → Hardcoded in config schema
- [x] Placeholder stages → Show "Coming soon" disabled state
- [x] Trigger location → Top bar icon only
- [x] Config persistence → Immediate on every toggle

---
