# Acceptance Test Cases: FEATURE-037-A (Compose Idea Modal — Create New)

> Feature: FEATURE-037-A | Version: v1.0
> Tested: 2026-02-19
> Tester: AI Agent (Flux)
> Status: **BLOCKED** — Chrome DevTools MCP unavailable; test cases ready for manual execution
> Target URL: http://localhost:5858

---

## Test Case Summary

| TC ID | AC Coverage | Priority | Description | Status |
|-------|------------|----------|-------------|--------|
| TC-001 | AC-001 | P0 | Modal opens from workflow Compose Idea action | Not Run |
| TC-002 | AC-002, AC-032, AC-033 | P0 | Modal layout: centered, 720px max-width, Slate/Emerald palette | Not Run |
| TC-003 | AC-003 | P0 | Header text "Compose Idea", close button, footer buttons | Not Run |
| TC-004 | AC-004 | P0 | Close via × button, Escape key, Cancel button | Not Run |
| TC-005 | AC-005 | P1 | Overlay backdrop click does NOT close modal | Not Run |
| TC-006 | AC-007, AC-008 | P0 | Toggle buttons: Create New (default active) / Link Existing | Not Run |
| TC-007 | AC-009 | P1 | Link Existing shows placeholder "Available in next update" | Not Run |
| TC-008 | AC-010 | P1 | Name input preserved when toggling modes | Not Run |
| TC-009 | AC-011, AC-012 | P0 | Name input with live word counter (X / 10 words) | Not Run |
| TC-010 | AC-013, AC-014 | P0 | Validation: >10 words shows error, disables submit | Not Run |
| TC-011 | AC-015, AC-016 | P0 | Compose tab default, EasyMDE editor with toolbar | Not Run |
| TC-012 | AC-017 | P2 | Editor placeholder "Write your idea in Markdown..." | Not Run |
| TC-013 | AC-019 | P0 | Upload tab switches to drop zone | Not Run |
| TC-014 | AC-020 | P1 | Upload zone accept types: md, txt, pdf, png, jpg, py, js, docx | Not Run |
| TC-015 | AC-023 | P0 | Submit disabled until name valid AND content present | Not Run |
| TC-016 | AC-024, AC-025 | P0 | Folder name: wf-NNN-sanitized-name format | Not Run |
| TC-017 | AC-026, AC-027, AC-028 | P0 | Full submit flow: upload → auto-complete → close → refresh | Not Run |
| TC-018 | AC-034 | P1 | Interactive elements: toggle, tabs, toolbar, counter all functional | Not Run |
| TC-019 | AC-035, AC-036, AC-037 | P0 | Workplace backward compat: compose/upload still work | Not Run |

---

## Detailed Test Cases

### TC-001: Modal Opens from Workflow Action (AC-001) — P0

**Precondition:** Workflow exists, Ideation stage visible with "Compose Idea" action button.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Navigate to app | `http://localhost:5858` | Page loads |
| 2 | Toggle to Workflow mode | `#mode-toggle-btn` | Workflow view visible |
| 3 | Expand a workflow panel | `.workflow-panel` header click | Stage ribbon visible |
| 4 | Click "Compose Idea" action | `button` with text "📝 Compose Idea" | Modal overlay appears |
| 5 | Verify overlay visible | `.compose-modal-overlay.active` | Element exists, opacity=1 |

---

### TC-002: Modal Layout & Styling (AC-002, AC-032, AC-033) — P0

**Precondition:** Modal is open (TC-001 complete).

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Check overlay z-index | `.compose-modal-overlay` | z-index: 1051 |
| 2 | Check modal max-width | `.compose-modal` | max-width: 720px |
| 3 | Check modal centered | `.compose-modal-overlay` | display: flex, align-items: center, justify-content: center |
| 4 | Check backdrop blur | `.compose-modal-overlay` | backdrop-filter includes blur(4px) |
| 5 | Check border-radius | `.compose-modal` | border-radius: 12px |
| 6 | Check font family | `.compose-modal-overlay` | font-family contains 'DM Sans' |

---

### TC-003: Header & Footer Elements (AC-003) — P0

**Precondition:** Modal is open.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Verify header text | `.compose-modal-header h3` | Text = "Compose Idea" |
| 2 | Verify close button | `.compose-modal-close` | Button exists with "×" text |
| 3 | Verify Cancel button | `.compose-modal-btn-cancel` | Text = "Cancel" |
| 4 | Verify Submit button | `.compose-modal-btn-submit` | Text = "Submit Idea" |

---

### TC-004: Close Modal Methods (AC-004) — P0

**Precondition:** Modal is open.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Click × button | `.compose-modal-close` | Modal closes (overlay removed/hidden) |
| 2 | Re-open modal | Compose Idea action button | Modal open again |
| 3 | Press Escape key | keyboard Escape | Modal closes |
| 4 | Re-open modal | Compose Idea action button | Modal open again |
| 5 | Click Cancel | `.compose-modal-btn-cancel` | Modal closes |

---

### TC-005: Overlay Click Does NOT Close (AC-005) — P1

**Precondition:** Modal is open.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Click overlay area (outside modal) | `.compose-modal-overlay` (but NOT `.compose-modal`) | Modal remains open |
| 2 | Verify modal still visible | `.compose-modal-overlay.active` | Still has .active class |

---

### TC-006: Toggle Buttons Default State (AC-007, AC-008) — P0

**Precondition:** Modal just opened.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Check "Create New" active | `.compose-modal-toggle button[data-mode="create"]` | Has .active class |
| 2 | Check "Link Existing" inactive | `.compose-modal-toggle button[data-mode="link"]` | Does NOT have .active class |
| 3 | Verify create content visible | `.compose-modal-create-content` | display != none |

---

### TC-007: Link Existing Placeholder (AC-009) — P1

**Precondition:** Modal is open.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Click "Link Existing" toggle | `.compose-modal-toggle button[data-mode="link"]` | Toggle switches |
| 2 | Verify placeholder visible | `.compose-modal-placeholder` | Contains text "Available in next update" |
| 3 | Verify create content hidden | `.compose-modal-create-content` | display = none |

---

### TC-008: Name Preserved on Toggle (AC-010) — P1

**Precondition:** Modal is open in Create New mode.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Type name "Test Idea" | `#compose-idea-name` | Input shows "Test Idea" |
| 2 | Click "Link Existing" | `.compose-modal-toggle button[data-mode="link"]` | Mode switches |
| 3 | Click "Create New" | `.compose-modal-toggle button[data-mode="create"]` | Mode switches back |
| 4 | Verify name preserved | `#compose-idea-name` | Value = "Test Idea" |

---

### TC-009: Name Input with Word Counter (AC-011, AC-012) — P0

**Precondition:** Modal is open.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Verify label "Idea Name" | `.compose-modal-name label` | Text contains "Idea Name" |
| 2 | Verify counter starts at 0 | `.compose-modal-word-counter` | Text = "0 / 10 words" |
| 3 | Type "My Great Idea" | `#compose-idea-name` | Text entered |
| 4 | Verify counter updates | `.compose-modal-word-counter` | Text = "3 / 10 words" |

---

### TC-010: Validation — Name Too Long (AC-013, AC-014) — P0

**Precondition:** Modal is open.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Type 11-word name | `#compose-idea-name` | "one two three four five six seven eight nine ten eleven" |
| 2 | Verify counter shows over-limit | `.compose-modal-word-counter` | Has .over-limit class, text = "11 / 10 words" |
| 3 | Verify error message | `.compose-modal-name-error` | Contains "10 words or fewer" |
| 4 | Verify submit disabled | `.compose-modal-btn-submit` | disabled = true |

---

### TC-011: Compose Tab Default with EasyMDE (AC-015, AC-016) — P0

**Precondition:** Modal is open in Create New mode.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Verify Compose tab active | `.compose-modal-tabs button[data-tab="compose"]` | Has .active class |
| 2 | Verify editor area visible | `.compose-modal-editor` | display != none |
| 3 | Verify EasyMDE loaded | `.compose-modal-editor .EasyMDEContainer` | Element exists |
| 4 | Verify toolbar present | `.compose-modal-editor .editor-toolbar` | Element exists |

---

### TC-012: Editor Placeholder (AC-017) — P2

**Precondition:** Modal open, compose tab active.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Check placeholder | `.compose-modal-editor .CodeMirror-placeholder` or CodeMirror content | Contains "Write your idea in Markdown" |

---

### TC-013: Upload Tab Switch (AC-019) — P0

**Precondition:** Modal open, compose tab active.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Click Upload tab | `.compose-modal-tabs button[data-tab="upload"]` | Tab becomes active |
| 2 | Verify upload zone visible | `.compose-modal-upload.active` | Element visible |
| 3 | Verify compose hidden | `[data-content="compose"]` | display = none |
| 4 | Verify drop zone present | `.compose-modal-dropzone` | Element exists |

---

### TC-014: Upload Accepts File Types (AC-020) — P1

**Precondition:** Modal open, upload tab active.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Check file input accept attr | `.compose-modal-file-input` | accept contains ".md,.txt,.pdf,.png,.jpg,.py,.js,.docx" |
| 2 | Verify hint text | `.compose-modal-dropzone-hint` | Contains "md, txt, pdf, png, jpg, py, js, docx" |

---

### TC-015: Submit Button Disabled Logic (AC-023) — P0

**Precondition:** Modal open.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Verify submit disabled (no name, no content) | `.compose-modal-btn-submit` | disabled = true |
| 2 | Type valid name "Auth Flow" | `#compose-idea-name` | Name entered |
| 3 | Verify still disabled (no content) | `.compose-modal-btn-submit` | disabled = true |
| 4 | Type content in editor | EasyMDE CodeMirror | "Some idea content" |
| 5 | Verify submit enabled | `.compose-modal-btn-submit` | disabled = false |

---

### TC-016: Folder Name Generation (AC-024, AC-025) — P0

**Precondition:** This is validated by unit tests (AutoFolderNamer). Browser test validates the sanitized preview.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Type name "My GREAT Idea!!" | `#compose-idea-name` | Name entered |
| 2 | Check folder preview | `.compose-modal-folder-preview` | Contains "wf-???-my-great-idea" (sanitized, lowercase, no special chars) |

---

### TC-017: Full Submit Flow (AC-026, AC-027, AC-028) — P0

**Precondition:** Workflow exists, modal open, valid name + content entered.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Type name "Test Submit" | `#compose-idea-name` | Entered |
| 2 | Type content | EasyMDE | "# Test\n\nContent" |
| 3 | Click Submit Idea | `.compose-modal-btn-submit` | Button text changes to "Submitting..." |
| 4 | Wait for response | — | Modal closes |
| 5 | Verify overlay removed | `.compose-modal-overlay` | Not in DOM or hidden |
| 6 | Verify folder created | Navigate to ideas tree or check `/api/ideas/tree` | Folder matching `wf-NNN-test-submit` exists |

---

### TC-018: Interactive Elements Functional (AC-034) — P1

**Precondition:** Modal open.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Toggle buttons respond | `.compose-modal-toggle button` | Click toggles .active class |
| 2 | Tab switching works | `.compose-modal-tabs button` | Click switches tab content |
| 3 | Word counter updates | `#compose-idea-name` + `.compose-modal-word-counter` | Counter changes on input |
| 4 | EasyMDE toolbar clickable | `.editor-toolbar button` | Bold/italic/etc buttons respond |

---

### TC-019: Workplace Backward Compatibility (AC-035, AC-036, AC-037) — P0

**Precondition:** App loaded, no workflow active, Workplace panel accessible.

| Step | Action | Selector | Expected Result |
|------|--------|----------|-----------------|
| 1 | Navigate to Workplace | Click Workplace sidebar item | Workplace view loads |
| 2 | Verify compose textarea | `#workplace-compose-textarea` | EasyMDE initializes |
| 3 | Verify submit button | `#workplace-submit-idea` | Button exists and clickable |
| 4 | Verify upload dropzone | `#workplace-dropzone` | Drop zone exists |
| 5 | Verify file input | `#workplace-file-input` | File input exists |

---

## Execution Results

> **Status: BLOCKED**
> **Reason:** Chrome DevTools MCP connection unavailable — browser session already in use.
> **Action Required:** Execute test cases manually via browser, or re-run when MCP is available.

| Metric | Value |
|--------|-------|
| Total Test Cases | 19 |
| Passed | 0 |
| Failed | 0 |
| Blocked | 19 |
| Not Run | 19 |
| Pass Rate | N/A |

---

## Mockup Validation

**Mockup:** [compose-idea-modal-v1.html](../mockups/compose-idea-modal-v1.html) — Status: **current**

> Visual validation deferred (MCP unavailable). When executed, compare:
> - Layout structure: modal container, toggle, name input, tabs, editor, footer
> - Colors: Slate palette (#1e293b, #334155, #64748b, #94a3b8, #e2e8f0), Emerald (#10b981)
> - Typography: DM Sans font family
> - Spacing: 8px unit system, 12px border-radius
> - Interactive states: hover, active, disabled for buttons/tabs
