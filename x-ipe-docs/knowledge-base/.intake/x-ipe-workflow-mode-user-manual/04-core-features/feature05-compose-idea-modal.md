---
title: "Compose Idea Modal"
section: "04-core-features"
extraction_round: 2
source_files:
  - src/x_ipe/static/js/features/compose-idea-modal.js
---

# Compose Idea Modal

## Overview

The Compose Idea Modal is the primary interface for creating new ideas in the Ideation stage. It provides a markdown editor, file upload, and KB reference linking.

## How to Access

1. In workflow mode, expand a workflow card
2. In the Ideation stage, click **📝 Compose Idea** action button
3. The Compose Idea modal opens

## Modal Layout

### 1. Name Input
- Text field: "Enter a short, descriptive name (max 10 words)"
- **Live validation:** Word counter shows "N / 10 words" and turns red if exceeded
- **Folder preview:** Shows generated folder path: `x-ipe-docs/ideas/wf-NNN-{sanitized-name}/`
- **Sanitization:** Name converted to lowercase, alphanumeric + hyphens, max 50 chars

### 2. Tab Bar
Three tabs for content input:

| Tab | Description |
|-----|-------------|
| **Compose** | Markdown editor (EasyMDE) with formatting toolbar |
| **Upload** | Drag-and-drop file upload zone |
| **📚 KB Reference** | Link existing KB articles as references |

### 3. Compose Tab (EasyMDE Editor)
- Full markdown editor with toolbar (bold, italic, lists, code blocks, headings)
- Placeholder: "Write your idea in Markdown..."
- Supports live preview and syntax highlighting

### 4. Upload Tab
- Drag-and-drop area or click to browse
- **Accepted formats:** `.md`, `.txt`, `.pdf`, `.png`, `.jpg`, `.py`, `.js`, `.docx`
- Shows file list with remove buttons
- Auto-preview of uploaded files

### 5. KB Reference
- Click 📚 KB Reference button → opens KBReferencePicker modal
- Select KB articles → stored as `kb-references` in deliverables
- Shows count badge on KB button (e.g., "📚 2")

## Submission Flow

1. Enter idea name (required, 1–10 words)
2. Write markdown content OR upload files OR link KB references
3. Click **"Submit Idea"** button
4. Backend creates:
   - Idea file at `x-ipe-docs/ideas/wf-NNN-{name}/idea.md`
   - Ideas folder at `x-ipe-docs/ideas/wf-NNN-{name}/`
5. Action status → "done", deliverables recorded in workflow state
6. Modal closes, workflow view re-renders

## Edit Mode

If you click on a completed Compose Idea action (when allowed):
- Modal opens in **edit mode** with existing content loaded
- Existing folder and file paths shown
- Submit button text: "Update Idea"
- Allows modifying the idea without creating a new folder

## Error States

| Condition | Behavior |
|-----------|----------|
| Empty name | "Value is required" error below input |
| Name > 10 words | Word counter turns red, submit blocked |
| Network error on submit | Toast: "Error creating idea..." |
| File too large | Toast: "File too large" |

## UI Elements

| Element | Selector | Purpose |
|---------|----------|---------|
| Modal overlay | `.compose-modal-overlay` | Backdrop |
| Modal container | `.compose-modal` | Main panel |
| Name input | Text field | Idea name entry |
| Submit button | Primary button | Create/update idea |
