---
title: "Stage Toolbox"
section: "04-core-features"
extraction_round: 2
source_files:
  - src/x_ipe/static/js/features/stage-toolbox.js
  - src/x_ipe/static/js/init.js
---

# Stage Toolbox

## Overview

The Stage Toolbox provides a centralized view of development tools organized by workflow stage. It helps users discover which tools are available for each phase of the engineering lifecycle.

## How to Access

1. Look for the **⚒️ Toolbox** button in the top header bar (labeled "Stage Toolbox - Manage development tools")
2. Click the button to open the Stage Toolbox modal

![Stage Toolbox Button](screenshots/stage-toolbox.png)

## Modal Layout

The modal displays:

- **Header:** "🛠 Toolbox" title with close button
- **Theme Selector:** Dropdown at top to switch visual themes
- **Stage Sections:** Accordion-style sections for each of the 5 stages:
  - 💡 **Ideation** — brainstorming and idea-generation tools
  - 📋 **Requirement** — requirement gathering and analysis tools
  - ⚙️ **Implement** — code implementation tools
  - ✅ **Validation** — testing and acceptance tools
  - 💬 **Feedback** — feedback collection and review tools

## Tool Configuration

Tools are dynamically loaded from the project configuration file:
- **Config file:** `x-ipe-docs/config/tools.json`
- **API endpoint:** `GET /api/config/tools`
- Each tool entry includes: name, description, stage, and phase

## User Flow

1. Click **⚒️ Toolbox** → Modal opens with loading spinner
2. Tools fetched from API and rendered per-stage
3. Expand/collapse stage sections to view tools
4. Optionally switch theme using dropdown
5. Close with **×** button or click outside modal

## UI Elements

| Element | Selector | Purpose |
|---------|----------|---------|
| Trigger button | `#btn-stage-toolbox` | Opens the modal |
| Modal overlay | `.toolbox-modal-overlay` | Backdrop |
| Modal container | `.toolbox-modal` | Main panel |
| Close button | `.toolbox-modal-close` | Dismiss modal |
| Header | `.toolbox-modal-header` | Title area |
