# Documentation Viewer - Examples

## Example: Standard Project Documentation Viewer

**Request:** "Create documentation viewer for my project"

**Execution:**
```
1. Execute Task Flow from x-ipe-workflow-task-execution skill

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

   - Navigation tree loads
   - Markdown renders correctly
   - Mermaid diagrams display

7. Return Task Completion Output:
   category: standalone
   next_task_based_skill: null
   require_human_review: no
   task_output_links:
     - doc-viewer/server.py
     - doc-viewer/index.html
     - doc-viewer/README.md

8. Resume Task Flow from x-ipe-workflow-task-execution skill
```
