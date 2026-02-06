# Feature Specification: Homepage Infinity Loop

> Feature ID: FEATURE-026  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-05-2026

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 02-05-2026 | Echo | Initial specification |

---

## Linked Mockups

| Mockup Name | Description | Path |
|-------------|-------------|------|
| homepage-infinity-v4 | Interactive infinity loop with stage buttons and overlay preview | [mockups/homepage-infinity-v4.html](mockups/homepage-infinity-v4.html) |

---

## Overview

### What
The Homepage Infinity Loop is an interactive visualization displayed in X-IPE's content panel that represents the AI-powered development lifecycle as an infinity symbol (∞). It contains 8 clickable stage buttons that directly navigate users to corresponding sidebar sections.

### Why
New users need a visual overview to understand X-IPE's development workflow. The infinity loop communicates the continuous, cyclical nature of AI-assisted development and provides quick navigation to all major features without requiring users to search through the sidebar.

### Who
- **Primary:** New X-IPE users learning the platform
- **Secondary:** Experienced users wanting quick navigation to any lifecycle stage

---

## User Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-1 | As a new user, I want to see a visual overview of X-IPE's capabilities so that I understand what stages of development I can use | P0 |
| US-2 | As a user, I want to click on a stage and be guided to the relevant feature so that I can quickly access any part of the workflow | P0 |
| US-3 | As a user, I want the homepage to appear automatically when nothing is selected so that I always have a helpful starting point | P0 |
| US-4 | As a user, I want to see which stages are available vs coming soon so that I know what's currently usable | P1 |

---

## Acceptance Criteria

### AC-1: Entry Points

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-1.1 | Clicking "X-IPE" logo in header MUST display the homepage | P0 | ✅ |
| AC-1.2 | Homepage MUST be default view when no file/folder is selected in sidebar | P0 | ✅ |
| AC-1.3 | Homepage MUST render in content panel (workplace-content-body) | P0 | ✅ |
| AC-1.4 | Homepage MUST replace any previous content when triggered | P0 | ✅ |

### AC-2: Infinity Loop Visualization

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-2.1 | Infinity loop (∞) shape MUST be displayed with 8 stage buttons positioned on it | P0 | ✅ |
| AC-2.2 | Left loop MUST be labeled "CONTROL" with blue theme (#3b82f6 → #60a5fa) | P0 | ✅ |
| AC-2.3 | Right loop MUST be labeled "TRANSPARENCY" with purple theme (#8b5cf6 → #a78bfa) | P0 | ✅ |
| AC-2.4 | Loop SHOULD be rendered as SVG/CSS if visual quality matches mockup | P1 | ✅ |
| AC-2.5 | Loop MAY fall back to PNG background if SVG insufficient | P2 | ✅ |

### AC-3: Stage Buttons

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-3.1 | Each stage button MUST display emoji icon + uppercase label (e.g., "💡 IDEATION") | P0 | ✅ |
| AC-3.2 | Buttons MUST be positioned on the infinity loop path at defined locations | P0 | ✅ |
| AC-3.3 | Hover effect MUST include: scale up (1.1x), glow effect, pointer cursor | P1 | ✅ |
| AC-3.4 | Control stages (Ideation, Requirement, Implementation, Deployment) MUST use blue gradient | P0 | ✅ |
| AC-3.5 | Transparency stages (Validation, Monitoring, Feedback, Planning) MUST use purple gradient | P0 | ✅ |
| AC-3.6 | TBD stages (Deployment) MUST show disabled state with "TBD" badge | P1 | ✅ |

### AC-4: Click Behavior

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-4.1 | Clicking an active stage MUST highlight corresponding sidebar menu item | P0 | ✅ |
| AC-4.2 | Highlight MUST include visual indicator (background color, left border, animation) | P0 | ✅ |
| AC-4.3 | Sidebar MUST auto-scroll to highlighted item if not visible in viewport | P1 | ✅ |
| AC-4.4 | Parent folders MUST expand to show target item | P0 | ✅ |
| AC-4.5 | Clicking TBD stage MUST show tooltip "Coming Soon" without navigation | P1 | ✅ |
| AC-4.6 | Highlight animation MUST be temporary (fade after 2-3 seconds) | P1 | ✅ |

### AC-5: Responsive Behavior

| # | Acceptance Criteria | Priority | Testable |
|---|---------------------|----------|----------|
| AC-5.1 | Homepage MUST be hidden on screens < 768px width | P0 | ✅ |
| AC-5.2 | On mobile, MAY show simple text fallback with stage list | P2 | ✅ |

---

## Functional Requirements

### FR-1: Homepage Display Trigger

**Input:** User clicks X-IPE logo OR no file/folder selected in sidebar tree
**Process:**
1. Detect trigger event (logo click or empty selection state)
2. Clear current content panel
3. Render homepage component with infinity loop

**Output:** Homepage displayed in content panel

### FR-2: Stage-to-Sidebar Mapping

**Input:** Stage button click event
**Process:**
1. Look up sidebar target path for clicked stage
2. Expand all parent folders in path
3. Scroll sidebar to target item
4. Apply highlight animation to target item
5. Remove highlight after delay (2-3 seconds)

**Output:** Sidebar item highlighted and visible

**Stage Mapping Table:**

| Stage | Sidebar Section | Target Path |
|-------|-----------------|-------------|
| Ideation | Workplace | `Workplace > Ideation` |
| Requirement | Project | `Project > Requirements` |
| Implementation | Project | `Project > Features` (also highlights Code src/) |
| Deployment | Management | `Management > Deployment` (TBD) |
| Validation | Quality | `Quality > Project Quality Report` |
| Monitoring | Quality | `Quality > Behavior Tracing` |
| Feedback | Feedback | `Feedback > UI/UX Feedback` |
| Planning | Management | `Management > Planning` |

### FR-3: TBD Stage Handling

**Input:** Click on Deployment stage (or any future TBD stage)
**Process:**
1. Detect TBD status from stage configuration
2. Display tooltip with "Coming Soon" message
3. Do NOT navigate or highlight sidebar

**Output:** Tooltip shown, no navigation occurs

---

## Non-Functional Requirements

| ID | Requirement | Priority | Metric |
|----|-------------|----------|--------|
| NFR-1 | Homepage MUST render within 200ms | P0 | Time to first paint |
| NFR-2 | Sidebar highlight animation MUST be smooth (60fps) | P1 | Frame rate |
| NFR-3 | Homepage MUST use X-IPE design system colors | P0 | Color compliance |
| NFR-4 | Homepage MUST be accessible (keyboard navigation, ARIA labels) | P1 | WCAG 2.1 AA |
| NFR-5 | SVG/CSS implementation MUST not exceed 50KB | P2 | Bundle size |

---

## UI/UX Requirements

### UX-1: Visual Layout

Based on mockup analysis:

| Element | Specification |
|---------|---------------|
| Container | Centered in content panel, max-width 900px |
| Header | "X-IPE" title + "AI-Powered Development Lifecycle" subtitle |
| Infinity Loop | Full-width, aspect ratio ~2:1 |
| Stage Buttons | 8 buttons positioned on loop path |
| Labels | "CONTROL" (left), "TRANSPARENCY" (right) |
| Legend | Bottom hint: "Control (What we decide)" / "Transparency (What we see)" |

### UX-2: Stage Button Positions

Buttons positioned at specific percentages on infinity loop:

| Stage | Left % | Top % |
|-------|--------|-------|
| Ideation | 4.5% | 60% |
| Requirement | 12% | 12% |
| Implementation | 30% | 73% |
| Deployment | 56% | 19% |
| Validation | 80% | 13% |
| Monitoring | 85% | 65% |
| Feedback | 58% | 70% |
| Planning | 38% | 25% |

### UX-3: Color Palette

| Element | Color | Hex |
|---------|-------|-----|
| Control Loop | Blue Gradient | #3b82f6 → #60a5fa |
| Transparency Loop | Purple Gradient | #8b5cf6 → #a78bfa |
| Control Button Background | Blue | rgba(59, 130, 246, 0.9) |
| Transparency Button Background | Purple | rgba(139, 92, 246, 0.9) |
| TBD Button | Muted Gray | #94a3b8 |
| Text | White | #ffffff |
| Glow Effect | Theme color at 50% opacity | - |

### UX-4: Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Title | Syne | 2rem | 700 |
| Subtitle | DM Sans | 1rem | 400 |
| Loop Labels | Syne | 1.1rem | 700 |
| Stage Button Label | DM Sans | 0.65rem | 600 |
| Legend | DM Sans | 0.75rem | 400 |

### UX-5: Interactions

| Interaction | Behavior |
|-------------|----------|
| Button Hover | Scale 1.1x, box-shadow glow, cursor pointer |
| Button Click | Brief press effect, then trigger sidebar navigation |
| TBD Button Hover | Show "Coming Soon" tooltip, no scale effect |
| Sidebar Highlight | Cyan/accent background, left border, fade after 2-3s |

---

## Dependencies

### Internal Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-001 | Feature | Project Navigation - sidebar tree structure |
| Content Panel | Component | workplace-content-body container |
| Sidebar API | API | Expand/collapse/scroll functions |

### External Dependencies

None - all assets self-contained.

---

## Business Rules

| ID | Rule |
|----|------|
| BR-1 | Homepage is ALWAYS accessible via logo click, regardless of current state |
| BR-2 | TBD stages MUST NOT navigate until feature is implemented |
| BR-3 | Stage order follows development lifecycle: Ideation → Requirement → Implementation → Deployment → Validation → Monitoring → Feedback → Planning → (loop) |
| BR-4 | Homepage MUST show current status of each stage (Ready/TBD) |

---

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Sidebar collapsed when stage clicked | Expand sidebar first, then highlight item |
| Target item in collapsed folder | Expand all parent folders, then highlight |
| User clicks same stage twice | Re-trigger highlight animation |
| User rapidly clicks multiple stages | Process most recent click only (debounce) |
| Sidebar section not visible (scrolled) | Auto-scroll to make item visible |
| Screen resize below 768px while viewing | Hide homepage, show fallback if implemented |
| Logo click while homepage already shown | Refresh homepage (no-op or subtle animation) |

---

## Out of Scope

| Item | Reason |
|------|--------|
| Stage tooltips with detailed descriptions | Simplicity - mockup shows direct navigation |
| Animated flow along infinity path | Performance - can be v2 enhancement |
| Customizable stage order | Fixed by business rules |
| Multiple themes for homepage | Use system theme colors only |
| Stage completion progress | Separate feature (Project Quality Report) |

---

## Technical Considerations

1. **Homepage Component:** Create reusable component that can be rendered in content panel
2. **Event Handling:** Listen for logo click and tree selection changes
3. **Sidebar Integration:** Use existing sidebar.js expand/scroll APIs
4. **State Management:** Track homepage visibility state
5. **SVG vs PNG Decision:** Attempt SVG first, measure quality vs mockup, fallback if needed

---

## Open Questions

| # | Question | Status |
|---|----------|--------|
| 1 | Should highlight persist until user clicks elsewhere, or auto-fade? | Resolved: Auto-fade after 2-3s |
| 2 | Should there be a close button on homepage? | Resolved: No, selecting any file replaces it |
| 3 | Should Implementation highlight both Features AND Code? | Open: TBD during implementation |

---

## Test Cases (Preview)

| TC | Description | Expected Result |
|----|-------------|-----------------|
| TC-1 | Click X-IPE logo | Homepage displays |
| TC-2 | Clear file selection | Homepage displays |
| TC-3 | Click Ideation stage | "Workplace > Ideation" highlighted |
| TC-4 | Click Deployment stage | "Coming Soon" tooltip shown |
| TC-5 | Resize window to < 768px | Homepage hidden |
| TC-6 | Select file while on homepage | Homepage replaced with file content |

---

*Specification created by Echo | TASK-200 | 02-05-2026*
