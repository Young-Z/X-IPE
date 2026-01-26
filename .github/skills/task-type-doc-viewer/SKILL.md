---
name: task-type-doc-viewer
description: Generate a web-based documentation viewer for browsing project docs. Use when human wants to view documentation in a web browser. Triggers on requests like "create doc viewer", "documentation viewer", "browse docs in browser", "generate docs site".
---

# Task Type: Documentation Viewer

## Purpose

Generate a web-based documentation viewer for browsing project docs by:
1. Creating a self-contained doc-viewer folder
2. Building a Python server with auto-detection API
3. Creating an HTML viewer with markdown and Mermaid rendering
4. Providing usage documentation

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` and `task-board-management` skill, please learn them first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Documentation Viewer |
| Category | Standalone |
| Next Task Type | N/A |
| Require Human Review | No |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Project has `x-ipe-docs/` folder with documentation | Yes |

---

## Execution Flow

Execute Documentation Viewer by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Create Folder | Create `doc-viewer/` directory | Folder exists |
| 2 | Create Server | Build `server.py` with API endpoint | Server file created |
| 3 | Create Viewer | Build `index.html` with marked.js and mermaid.js | HTML file created |
| 4 | Create README | Write usage instructions | README created |
| 5 | Test | Run server and verify docs display | Server works |

**⛔ BLOCKING RULES:**
- Step 5: BLOCKED until server runs and displays documentation correctly

---

## Execution Procedure

### Step 1: Create Doc-Viewer Folder Structure

**Target Structure:**
```
project-root/
  doc-viewer/
    index.html    # The documentation viewer web page
    server.py     # Python server with API for auto-detecting docs
    README.md     # Usage instructions
```

**Actions:**
```
1. Create `doc-viewer/` folder if not exist
```

### Step 2: Create Python Server

**Create `doc-viewer/server.py` with:**

```python
# Key features:
# - Static file serving from project root
# - /api/docs-structure endpoint that dynamically scans x-ipe-docs/ and .github/
# - No-cache headers for always showing latest content
```

**Server Requirements:**
| Feature | Description |
|---------|-------------|
| Static Files | Serve files from project root |
| API Endpoint | `GET /api/docs-structure` returns JSON tree |
| Auto-Detection | Dynamically scan `x-ipe-docs/` and `.github/` folders |
| No Caching | Markdown files served with no-cache headers |

### Step 3: Create HTML Viewer

**Create `doc-viewer/index.html` with:**

| Component | Description |
|-----------|-------------|
| Left Sidebar | Navigation tree (fetched from API) |
| Right Side | Markdown content display area |
| Markdown Rendering | Use `marked.js` for markdown |
| Diagram Rendering | Use `mermaid.js` for flowcharts, class diagrams |

### Step 4: Create README

**Create `doc-viewer/README.md` with:**

```markdown
# Documentation Viewer

## Usage
cd doc-viewer && python3 server.py
# Open: http://localhost:8080/doc-viewer/

## Features
- Auto-detection: No manual config - just refresh to see new docs
- No caching: Always shows latest content
- Mermaid diagrams: Renders ```mermaid code blocks as interactive diagrams
```

---

## Skill/Task Completion Output Attributes

This skill MUST return these attributes to the Task Data Model upon task completion:
```yaml
Output:
  category: standalone
  status: completed | blocked
  next_task_type: null
  require_human_review: No
  auto_proceed: {from input Auto Proceed}
  task_output_links:
    - doc-viewer/server.py
    - doc-viewer/index.html
    - doc-viewer/README.md
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | `doc-viewer/server.py` created with API endpoint | Yes |
| 2 | `doc-viewer/index.html` created with sidebar and markdown viewer | Yes |
| 3 | `doc-viewer/README.md` created with usage instructions | Yes |
| 4 | Server runs and displays documentation | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: Basic Documentation Viewer

**When:** Standard project with x-ipe-docs/ folder
**Then:**
```
1. Create doc-viewer/ folder
2. Create server.py with /api/docs-structure
3. Create index.html with marked.js and mermaid.js
4. Create README.md
5. Test by running server
```

### Pattern: GitHub Skills Integration

**When:** Project uses .github/skills/ folder
**Then:**
```
1. Extend server.py to also scan .github/skills/
2. Add skills section to navigation tree
3. Group by skill category
```

### Pattern: Multiple Doc Folders

**When:** Docs split across multiple folders
**Then:**
```
1. Configure server.py to scan all relevant folders
2. Add folder filters to API
3. Display folder groupings in sidebar
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Manual doc config | High maintenance | Auto-detect from filesystem |
| Cache markdown files | Shows stale content | Use no-cache headers |
| Skip mermaid.js | Diagrams won't render | Always include mermaid.js |
| Embed CSS/JS inline | Hard to maintain | Use CDN links |

---

## Example

**Request:** "Create documentation viewer for my project"

**Execution:**
```
1. Execute Task Flow from task-execution-guideline skill

2. Create doc-viewer/ folder

3. Create server.py:
   - Serve static files from project root
   - /api/docs-structure scans x-ipe-docs/ and .github/
   - Returns JSON tree structure
   - No-cache headers for markdown

4. Create index.html:
   - Left sidebar with navigation tree
   - Right side markdown display
   - marked.js for markdown rendering
   - mermaid.js for diagram rendering

5. Create README.md:
   # Documentation Viewer
   
   ## Usage
   cd doc-viewer && python3 server.py
   # Open: http://localhost:8080/doc-viewer/

6. Test:
   $ cd doc-viewer && python3 server.py
   Server running at http://localhost:8080/doc-viewer/
   
   ✓ Navigation tree loads
   ✓ Markdown renders correctly
   ✓ Mermaid diagrams display

7. Return Task Completion Output:
   category: Standalone
   next_task_type: N/A
   require_human_review: No
   task_output_links:
     - doc-viewer/server.py
     - doc-viewer/index.html
     - doc-viewer/README.md

8. Resume Task Flow from task-execution-guideline skill
```
