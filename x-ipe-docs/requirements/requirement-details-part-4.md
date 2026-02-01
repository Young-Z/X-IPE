# Requirement Details - Part 4

> Continued from: [requirement-details-part-3.md](requirement-details-part-3.md)  
> Created: 02-01-2026

---

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-024 | Project Quality Evaluation UI | v1.0 | Dedicated UI for viewing quality evaluations and triggering refactoring actions | FEATURE-008 |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| quality-evaluation-view | FEATURE-024 | [quality-evaluation-v1.html](../ideas/009.%20Project%20Quality%20Check/mockups/quality-evaluation-v1.html) |

---

## Feature Details (Continued)

### FEATURE-024: Project Quality Evaluation UI

**Version:** v1.0  
**Brief Description:** A dedicated UI feature in the Workplace section that provides formal support for project quality evaluation viewing, version history, and refactoring actions triggered via Copilot prompts.

**Source:** [Idea Summary v2](../ideas/009.%20Project%20Quality%20Check/idea-summary-v2.md)  
**Mockup:** [Quality Evaluation View](../ideas/009.%20Project%20Quality%20Check/mockups/quality-evaluation-v1.html)

#### Problem Statement

Currently, project quality evaluation is stored informally in the `x-ipe-docs/planning/` folder. There is no dedicated UI to:
1. View evaluation results in a styled format
2. Trigger quality evaluations via Copilot
3. Execute refactoring actions based on identified gaps
4. Track evaluation history over time

#### Solution Overview

Create a new "Project Quality Evaluation" submenu under Workplace in the sidebar with:
- Dedicated content view showing evaluation markdown in readonly preview
- Action bar with Refactoring dropdown and Evaluate button
- Version timeline for comparing last 5 evaluations
- Dynamic prompts loaded from `copilot-prompt.json` config

#### Acceptance Criteria

**1. Sidebar Integration**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-1.1 | "Project Quality Evaluation" submenu MUST appear under Workplace section in sidebar | Must |
| AC-1.2 | Submenu MUST use icon `bi-clipboard-check` | Must |
| AC-1.3 | Submenu MUST always be visible (even when no evaluation exists) | Must |
| AC-1.4 | Clicking submenu MUST switch content area to Quality Evaluation view | Must |

**2. Quality Evaluation View - Empty State**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-2.1 | When no evaluation file exists, view MUST show empty state | Must |
| AC-2.2 | Empty state MUST display message: "No evaluation yet. Click to evaluate." | Must |
| AC-2.3 | Empty state MUST include icon `bi-clipboard-check` in a circular container | Must |
| AC-2.4 | Empty state MUST include "Evaluate Project Quality" CTA button | Must |
| AC-2.5 | Clicking CTA button MUST open console with evaluate prompt from config | Must |

**3. Quality Evaluation View - With Data**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-3.1 | When evaluation file exists, view MUST show action bar at top | Must |
| AC-3.2 | View MUST show version timeline below action bar | Must |
| AC-3.3 | View MUST show markdown preview of evaluation file in main content area | Must |
| AC-3.4 | Markdown preview MUST be readonly (no editing capability) | Must |
| AC-3.5 | Markdown preview MUST render styled content (headings, tables, lists, code blocks) | Must |

**4. Action Bar Layout**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-4.1 | Action bar MUST display "Refactoring" dropdown button | Must |
| AC-4.2 | Action bar MUST display "Evaluate" button | Must |
| AC-4.3 | "Refactoring" dropdown MUST be positioned to the left of "Evaluate" button | Must |
| AC-4.4 | Both buttons MUST be right-aligned in the action bar | Must |
| AC-4.5 | Action bar MUST have subtle background color to distinguish from content | Should |

**5. Refactoring Dropdown**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-5.1 | Refactoring button MUST NOT trigger any action on click | Must |
| AC-5.2 | Refactoring button MUST show dropdown menu on hover | Must |
| AC-5.3 | Dropdown options MUST be loaded dynamically from `copilot-prompt.json` → `evaluation.refactoring[]` | Must |
| AC-5.4 | Each dropdown option MUST display icon and label from config | Must |
| AC-5.5 | Clicking a dropdown option MUST open console with command from config | Must |
| AC-5.6 | Dropdown MUST include visual dividers between option groups | Should |

**Default Refactoring Options (from config):**

| ID | Label | Command Template |
|----|-------|------------------|
| refactor-all | Refactor All | "Refactor all gaps identified in \<evaluation-file\> with reference to its code" |
| refactor-requirements | Refactor Requirements | "Refactor requirement gaps identified in \<evaluation-file\> with reference to its code" |
| refactor-features | Refactor Features | "Refactor feature gaps identified in \<evaluation-file\> with reference to its code" |
| refactor-tests | Refactor Tests | "Refactor test gaps identified in \<evaluation-file\> with reference to its code" |
| refactor-tracing-tests | Refactor Tracing Decorators + Tests | "Refactor tracing decorator gaps identified in \<evaluation-file\> with reference to its feature" |
| refactor-code-tests | Refactor Code + Tests | "Refactor code gaps identified in \<evaluation-file\> with reference to its feature" |

**6. Evaluate Button**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-6.1 | Evaluate button MUST trigger action on click | Must |
| AC-6.2 | Clicking Evaluate MUST open console with evaluate command from config | Must |
| AC-6.3 | Evaluate command MUST use `evaluation.evaluate.command` from `copilot-prompt.json` | Must |
| AC-6.4 | Button MUST have primary styling (filled, teal color) | Should |

**7. Version Timeline**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-7.1 | Timeline MUST display as horizontal tabs below action bar | Must |
| AC-7.2 | Timeline MUST show last 5 evaluation versions | Must |
| AC-7.3 | Most recent version MUST appear on the left | Must |
| AC-7.4 | Each tab MUST show version number (e.g., "v5") and date | Must |
| AC-7.5 | Active version tab MUST have visual indicator (underline) | Must |
| AC-7.6 | Clicking a version tab MUST load that version's markdown file | Must |
| AC-7.7 | If fewer than 5 versions exist, only show existing versions | Must |

**8. File Storage & Versioning**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-8.1 | Evaluation files MUST be stored in `x-ipe-docs/quality-evaluation/` folder | Must |
| AC-8.2 | Latest evaluation MUST be named `project-quality-evaluation.md` | Must |
| AC-8.3 | Historical versions MUST be named `project-quality-evaluation-vN.md` | Must |
| AC-8.4 | System MUST keep maximum of 5 versions (auto-cleanup older) | Should |
| AC-8.5 | When new evaluation is created, current MUST be versioned before overwriting | Must |

**9. Config File Structure**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-9.1 | `copilot-prompt.json` MUST be restructured with top-level sections | Must |
| AC-9.2 | `ideation` section MUST contain existing prompts for idea workflow | Must |
| AC-9.3 | `evaluation` section MUST contain `evaluate` and `refactoring[]` configs | Must |
| AC-9.4 | `placeholder` section MUST include `evaluation-file` placeholder definition | Must |
| AC-9.5 | Ideation functionality MUST continue working after restructure | Must |

**Updated Config Structure:**
```json
{
  "version": "2.0",
  "ideation": {
    "prompts": [...]
  },
  "evaluation": {
    "evaluate": {
      "label": "Evaluate Project Quality",
      "icon": "bi-clipboard-check",
      "command": "Evaluate project quality and generate report to <evaluation-file>"
    },
    "refactoring": [
      { "id": "...", "label": "...", "icon": "...", "command": "..." }
    ]
  },
  "placeholder": {
    "current-idea-file": "...",
    "evaluation-file": "Replaced with current quality evaluation file path"
  }
}
```

**10. Placeholder Resolution**

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-10.1 | `<evaluation-file>` MUST be replaced with actual file path at runtime | Must |
| AC-10.2 | Path MUST resolve to `x-ipe-docs/quality-evaluation/project-quality-evaluation.md` | Must |
| AC-10.3 | If viewing historical version, path MUST resolve to that version's file | Should |

#### Non-Functional Requirements

| # | Requirement | Priority |
|---|-------------|----------|
| NFR-1 | Markdown preview MUST render within 200ms of loading | Should |
| NFR-2 | Dropdown menu MUST appear within 100ms of hover | Should |
| NFR-3 | Version switching MUST complete within 500ms | Should |
| NFR-4 | Config file changes MUST take effect on next view load (no restart) | Should |

#### Out of Scope

- Generating the quality evaluation report (handled by skill/agent)
- Executing refactoring (handled by Copilot after console prompt)
- Quality scoring algorithms
- Diff comparison between versions
- Export/share functionality

#### Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-008 | Feature | Workplace framework for sidebar and content area |
| Console | System | Console component for executing Copilot prompts |
| copilot-prompt.json | Config | Configuration file for prompt templates |

#### Migration Requirements

| # | Migration Task | Priority |
|---|---------------|----------|
| MIG-1 | Move existing `x-ipe-docs/planning/project-quality-evaluation*.md` files to `x-ipe-docs/quality-evaluation/` | Must |
| MIG-2 | Update existing code that references old location | Must |
| MIG-3 | Restructure `copilot-prompt.json` to new format | Must |
| MIG-4 | Update ideation code to read from new config structure | Must |

---

## Change Log

| Date | Feature | Change |
|------|---------|--------|
| 02-01-2026 | FEATURE-024 | Initial requirement documentation |
