---
name: x-ipe-task-based-doc-viewer
description: Generate a web-based documentation viewer for browsing project docs. Use when human wants to view documentation in a web browser. Triggers on requests like "create doc viewer", "documentation viewer", "browse docs in browser", "generate docs site".
---

# Task-Based Skill: Documentation Viewer

## Purpose

Generate a web-based documentation viewer for browsing project docs by:
1. Creating a self-contained doc-viewer folder
2. Building a Python server with auto-detection API
3. Creating an HTML viewer with markdown and Mermaid rendering
4. Providing usage documentation

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Documentation Viewer"

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null
  require_human_review: no

  # Required inputs
  auto_proceed: false
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Documentation folder exists</name>
    <verification>Project has `x-ipe-docs/` folder with documentation</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Create Folder | Create `doc-viewer/` directory | Folder exists |
| 2 | Create Server | Build `server.py` with API endpoint | Server file created |
| 3 | Create Viewer | Build `index.html` with marked.js and mermaid.js | HTML file created |
| 4 | Create README | Write usage instructions | README created |
| 5 | Test | Run server and verify docs display | Server works |

BLOCKING: Step 5 blocked until server runs and displays documentation correctly.

---

## Execution Procedure

```xml
<procedure name="doc-viewer">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Create Doc-Viewer Folder Structure</name>
    <action>
      1. Create `doc-viewer/` folder if it does not exist
    </action>
    <output>
      project-root/
        doc-viewer/
          index.html
          server.py
          README.md
    </output>
  </step_1>

  <step_2>
    <name>Create Python Server</name>
    <action>
      1. Create `doc-viewer/server.py`
      2. Implement static file serving from project root
      3. Implement `GET /api/docs-structure` endpoint returning JSON tree
      4. Dynamically scan `x-ipe-docs/` and `.github/` folders
      5. Add no-cache headers for markdown files
    </action>
    <constraints>
      - CRITICAL: Server must auto-detect docs without manual config
      - CRITICAL: No-cache headers required so content is always fresh
    </constraints>
    <output>doc-viewer/server.py</output>
  </step_2>

  <step_3>
    <name>Create HTML Viewer</name>
    <action>
      1. Create `doc-viewer/index.html`
      2. Add left sidebar with navigation tree fetched from API
      3. Add right-side markdown content display area
      4. Include `marked.js` for markdown rendering via CDN
      5. Include `mermaid.js` for diagram rendering via CDN
    </action>
    <constraints>
      - CRITICAL: Use CDN links for JS libraries, not inline code
    </constraints>
    <output>doc-viewer/index.html</output>
  </step_3>

  <step_4>
    <name>Create README</name>
    <action>
      1. Create `doc-viewer/README.md`
      2. Document usage: `cd doc-viewer and python3 server.py`
      3. Document URL: `http://localhost:8080/doc-viewer/`
      4. Document features: auto-detection, no-caching, mermaid diagrams
    </action>
    <output>doc-viewer/README.md</output>
  </step_4>

  <step_5>
    <name>Test</name>
    <action>
      1. Run server: `cd doc-viewer and python3 server.py`
      2. Verify navigation tree loads from API
      3. Verify markdown renders correctly
      4. Verify mermaid diagrams display
    </action>
    <success_criteria>
      - Server starts on port 8080
      - Navigation tree loads docs from x-ipe-docs/
      - Markdown content renders in viewer
      - Mermaid code blocks render as diagrams
    </success_criteria>
    <output>Server running and documentation displaying correctly</output>
  </step_5>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: completed | blocked
  next_task_based_skill: null
  require_human_review: no
  auto_proceed: "{from input auto_proceed}"
  task_output_links:
    - doc-viewer/server.py
    - doc-viewer/index.html
    - doc-viewer/README.md
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Server created</name>
    <verification>`doc-viewer/server.py` exists with /api/docs-structure endpoint</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Viewer created</name>
    <verification>`doc-viewer/index.html` exists with sidebar and markdown viewer</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>README created</name>
    <verification>`doc-viewer/README.md` exists with usage instructions</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Server functional</name>
    <verification>Server runs and displays documentation correctly</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

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

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Manual doc config | High maintenance | Auto-detect from filesystem |
| Cache markdown files | Shows stale content | Use no-cache headers |
| Skip mermaid.js | Diagrams won't render | Always include mermaid.js |
| Embed CSS/JS inline | Hard to maintain | Use CDN links |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples.
