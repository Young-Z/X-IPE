# Feature Specification: Feedback Capture & Panel

> Feature ID: FEATURE-022-C  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-28-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 01-28-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description |
|--------|------|------|-------------|
| UI/UX Feedback View | HTML | [uiux-feedback-v1.html](../../ideas/005.%20Feature-UIUX%20Feedback/mockups/uiux-feedback-v1.html) | Shows context menu and feedback panel |

---

## Overview

The Feedback Capture & Panel feature provides a context menu for initiating feedback on selected elements and a panel for managing feedback entries. Users can right-click on selected elements to choose "Provide Feedback" or "Feedback with Screenshot", which creates a new entry in the feedback panel with element info and optional screenshot.

**This feature builds on FEATURE-022-B (Element Inspector)** which provides the element selection capability. The Feedback Capture & Panel adds the ability to create and manage feedback entries for those selected elements.

**Key Value Proposition:**
- Quick feedback capture via right-click context menu
- Screenshot cropped to selected element(s) bounding box
- Organized feedback panel with expandable entries
- Rich metadata: URL, elements, screenshot, description

---

## User Stories

- As a **developer**, I want to **right-click on a selected element to provide feedback**, so that **I can quickly capture UI issues**.

- As a **developer**, I want to **capture a screenshot of the selected element**, so that **the feedback includes visual context**.

- As a **developer**, I want to **see a list of my pending feedback entries**, so that **I can manage and submit them**.

- As a **developer**, I want to **add a description to my feedback**, so that **I can explain the issue in detail**.

- As a **developer**, I want to **delete a feedback entry**, so that **I can remove mistakes or duplicates**.

---

## Acceptance Criteria

### Context Menu

- [ ] AC-1: Right-click on selected element(s) shows context menu
- [ ] AC-2: Context menu appears at cursor position
- [ ] AC-3: Menu option "Provide Feedback" creates entry with element info only
- [ ] AC-4: Menu option "Feedback with Screenshot" creates entry with screenshot
- [ ] AC-5: Menu option "Copy Element Selector" copies selector to clipboard
- [ ] AC-6: Context menu has divider between feedback options and copy option
- [ ] AC-7: Context menu disabled when no elements are selected
- [ ] AC-8: Clicking outside menu closes it
- [ ] AC-9: Pressing Escape closes menu

### Screenshot Capture

- [ ] AC-10: Screenshot crops to selected element(s) bounding box
- [ ] AC-11: If multiple elements selected, screenshot includes all bounding boxes
- [ ] AC-12: Use html2canvas library for screenshot capture
- [ ] AC-13: Screenshot captures visible viewport content
- [ ] AC-14: If screenshot fails, entry created without screenshot (with warning)
- [ ] AC-15: Screenshot stored as base64 data URL

### Feedback Panel

- [ ] AC-16: Feedback panel appears on right side (380px width from mockup)
- [ ] AC-17: Panel header shows "Feedback" title and entry count badge
- [ ] AC-18: Panel contains scrollable list of feedback entries
- [ ] AC-19: Empty state shows "No feedback yet" message

### Feedback Entry

- [ ] AC-20: Entry name auto-generates: `Feedback-YYYYMMDD-HHMMSS`
- [ ] AC-21: Entry shows creation time (relative: "Just now", "2 min ago")
- [ ] AC-22: Entry shows URL of page when feedback was captured
- [ ] AC-23: Entry shows list of selected element selectors
- [ ] AC-24: Entry shows screenshot thumbnail (if captured)
- [ ] AC-25: Screenshot thumbnail shows dimensions badge
- [ ] AC-26: Entry has textarea for feedback description (placeholder text)
- [ ] AC-27: Entry has Delete button (trash icon)
- [ ] AC-28: Entry has Submit button

### Entry Behavior

- [ ] AC-29: New entry auto-expands and collapses others
- [ ] AC-30: Clicking collapsed entry expands it
- [ ] AC-31: Delete button removes entry from list
- [ ] AC-32: Delete shows confirmation if description is not empty
- [ ] AC-33: Submit button triggers FEATURE-022-D submission flow
- [ ] AC-34: Entries persist in memory (not localStorage) during session

---

## Functional Requirements

### FR-1: Context Menu Manager

**Description:** Show/hide context menu on right-click events.

**Details:**
- Input: Right-click event on selected element
- Process: Check if elements selected, position menu, show options
- Output: Visible context menu at cursor position

### FR-2: Screenshot Capture

**Description:** Capture cropped screenshot of selected elements.

**Details:**
- Input: Selected element(s) bounding boxes
- Process: Use html2canvas on iframe, crop to combined bounding box
- Output: Base64 image data URL

### FR-3: Feedback Entry Creation

**Description:** Create new feedback entry with captured data.

**Details:**
- Input: URL, element selectors, optional screenshot
- Process: Generate entry name, store in entries array
- Output: New entry added to panel, expanded

### FR-4: Feedback Panel Rendering

**Description:** Render feedback entries list with expand/collapse.

**Details:**
- Input: Entries array
- Process: Generate HTML for each entry, bind events
- Output: Updated panel DOM

---

## Non-Functional Requirements

### NFR-1: Screenshot Performance

- Screenshot capture should complete in < 2 seconds
- Large viewports may take longer but should show progress indicator

### NFR-2: Memory Management

- Entries stored in memory only (not persisted)
- Large screenshots may consume memory; limit to 10 concurrent entries

### NFR-3: User Experience

- Context menu appears within 100ms of right-click
- New entry appears immediately after menu selection

---

## UI/UX Requirements

### Context Menu (from mockup)

```
┌────────────────────────────┐
│ 📝 Provide Feedback        │
│ 📸 Feedback with Screenshot│
├────────────────────────────┤
│ 📋 Copy Element Selector   │
└────────────────────────────┘
```

Styling:
- White background, rounded corners (12px)
- Shadow: xl (0 20px 25px -5px rgba(0,0,0,0.1))
- Items: 12px 16px padding, hover highlight
- "Feedback with Screenshot" highlighted as primary action

### Feedback Panel (from mockup)

```
┌─────────────────────────────┐
│ 💬 Feedback              [3]│
│ Today's feedback entries    │
├─────────────────────────────┤
│ ▼ Feedback-20260128-141930  │
│   Just now              [🗑]│
│   ┌─────────────────────┐   │
│   │ URL: localhost:3000 │   │
│   │ Elements: <a.btn>   │   │
│   ├─────────────────────┤   │
│   │ [Screenshot Thumb]  │   │
│   │       170×52        │   │
│   ├─────────────────────┤   │
│   │ [Feedback text...]  │   │
│   ├─────────────────────┤   │
│   │      [Submit]       │   │
│   └─────────────────────┘   │
│ ▶ Feedback-20260128-140512  │
│ ▶ Feedback-20260128-135800  │
└─────────────────────────────┘
```

---

## Dependencies

### Internal Dependencies

- **FEATURE-022-B (Element Inspector):** Required - provides selected elements array
- **FEATURE-022-D (Feedback Storage):** Optional - submit button triggers this

### External Dependencies

- **html2canvas:** NPM package for screenshot capture (CDN or bundled)

---

## Technical Considerations

- html2canvas works on same-origin content; proxied iframe should work
- Screenshot capture may fail on complex pages; provide fallback
- Context menu must handle iframe coordinate translation
- Consider using canvas.toDataURL('image/png') for screenshot format
- Bounding box calculation for multiple elements needs union of rects

---

## Edge Cases

### Edge Case 1: Screenshot Capture Fails

**Scenario:** html2canvas throws error or times out
**Expected:** Create entry without screenshot, show warning icon

### Edge Case 2: Very Large Element

**Scenario:** Selected element is larger than viewport
**Expected:** Capture visible portion, note in entry

### Edge Case 3: Overlapping Elements

**Scenario:** Multiple selected elements overlap
**Expected:** Screenshot captures union of bounding boxes

### Edge Case 4: Dynamic Content

**Scenario:** Page content changes during capture
**Expected:** Capture current state at moment of right-click

---

## Out of Scope

- Screenshot annotation/editing tools
- Multiple screenshot captures per entry
- Entry reordering
- Entry export (before submission)

---
