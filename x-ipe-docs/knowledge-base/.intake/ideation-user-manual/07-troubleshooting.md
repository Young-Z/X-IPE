---
section_id: "7-troubleshooting"
title: "Troubleshooting"
quality_score: null
provenance:
  source: "X-IPE source code (ideas_service.py error handling, ideas_routes.py validation) + running application"
  extracted_by: "x-ipe-task-based-application-knowledge-extractor"
  extraction_date: "2026-03-17"
---

# 7. Troubleshooting

## Instructions

This section addresses common issues users may encounter when using the Ideation module, with step-by-step resolution guidance.

## Content

### Common Issues

#### Issue: "Idea folder not appearing in sidebar"

**Symptoms:** You created an idea but it doesn't show up in the sidebar folder tree.

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Sidebar not refreshed | Click the refresh button or navigate away and back to Ideation |
| Search filter active | Clear the search box at the top of the sidebar |
| Wrong project folder | Check Settings → Project Folder path is correct |
| Folder created at wrong level | Check if the folder was created inside another folder (expand parent folders) |

---

#### Issue: "File upload fails"

**Symptoms:** Drag-and-drop or browse upload doesn't work, or shows an error.

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Unsupported file type | Check the supported formats list (Section 4.3). Only text, data, code, image, and document formats are supported |
| File too large | Large files may time out. Try uploading smaller files or splitting large documents |
| Folder name too long | Ensure folder names are under 200 characters |
| Special characters in filename | Rename the file to remove characters like `/ \ : * ? " < > \|` |
| Disk full | Check available disk space on the server |

---

#### Issue: "Markdown not rendering correctly"

**Symptoms:** Markdown content appears as raw text instead of formatted output, or diagrams don't render.

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Invalid Markdown syntax | Check your Markdown formatting — use Preview mode to verify |
| Mermaid syntax error | Verify Mermaid diagram syntax at [mermaid.live](https://mermaid.live). Ensure the code block uses ` ```mermaid ` fencing |
| Architecture DSL error | Ensure DSL blocks follow the X-IPE Architecture DSL specification |
| Browser cache | Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac) |

---

#### Issue: "UIUX Reference capture not working"

**Symptoms:** The UIUX Reference tab doesn't capture elements from the target URL.

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Not authenticated | Log in to the target website first using the Authentication feature |
| URL unreachable | Verify the target URL is accessible from the X-IPE server |
| CORS restrictions | Some websites block cross-origin requests. Try a different URL or use screenshots instead |
| Chrome DevTools not connected | Ensure the browser connection is active (UIUX reference uses Chrome DevTools protocol) |

---

#### Issue: "AI refinement not producing results"

**Symptoms:** You asked the AI to refine an idea but no summary was generated.

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Console not connected | Ensure the Console (bottom panel) is active and connected to an AI agent |
| Idea folder empty | Upload or compose at least one content file before requesting refinement |
| Agent timeout | Try again — complex ideas may require longer processing time |
| Incorrect idea context | Ensure the correct idea folder is selected/active when initiating refinement |

---

#### Issue: "Folder rename or delete fails"

**Symptoms:** Error message when trying to rename or delete a folder.

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Name already exists | Choose a different name — folder names must be unique in the same directory |
| Invalid characters | Remove special characters: `/ \ : * ? " < > \|` |
| Folder linked to workflow | Workflow-linked folders may have restrictions — check if a workflow is active |
| File lock | Close any files open in editors or other applications |

---

### Error Messages Reference

| Error Message | Meaning | Action |
|---------------|---------|--------|
| `"Folder not found"` | The requested idea folder doesn't exist on disk | Refresh the sidebar; folder may have been renamed or deleted |
| `"Invalid folder name"` | Folder name contains prohibited characters or is too long | Use alphanumeric characters, spaces, hyphens, and underscores only |
| `"Path traversal detected"` | A request attempted to access files outside the ideas directory | This is a security check — ensure you're using valid folder paths |
| `"File already exists"` | Upload attempted with a filename that already exists | The system auto-appends `(2)`, `(3)`, etc. — if this fails, rename the file first |
| `"Conversion failed"` | DOCX or MSG file conversion to HTML failed | Verify the file isn't corrupted; try uploading a different format |

---

### Performance Tips

- **Large folder trees:** If you have many idea folders (50+), use the search function to filter instead of scrolling
- **Large files:** Markdown files over 1MB may render slowly — split into smaller documents
- **Many Mermaid diagrams:** Pages with 10+ complex diagrams may load slowly — consider splitting into multiple files
- **Browser performance:** Close unused browser tabs and clear cache periodically

## Screenshots

No additional screenshots for this section.
