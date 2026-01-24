# Idea Mockup - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Mockup with Frontend-Design Tool

**Scenario:** Create mockups for mobile-app-idea after ideation

**Input:**
- `Current Idea Folder`: `docs/ideas/mobile-app-idea` (from previous Ideation task)

**Config:** `docs/ideas/.ideation-tools.json`
```json
{
  "version": "1.0",
  "mockup": {
    "frontend-design": true,
    "figma-mcp": false
  }
}
```

**Idea Summary Excerpt:**
```markdown
## Key Features
- User dashboard with activity charts
- Settings page for preferences
- Mobile-responsive design
```

**Execution:**
```
1. Execute Task Flow from task-execution-guideline skill

2. Validate Current Idea Folder:
   - Current Idea Folder = docs/ideas/mobile-app-idea
   - Folder exists ✓
   - idea-summary-v1.md exists ✓

3. Load Config:
   - Read .ideation-tools.json
   - mockup.frontend-design: true → enabled
   - mockup.figma-mcp: false → disabled

4. Read Idea Summary:
   - Load docs/ideas/mobile-app-idea/idea-summary-v1.md
   - Extract: dashboard, settings page, mobile-responsive

5. Identify Mockup Needs:
   - Priority 1: User dashboard (charts, mobile)
   - Priority 2: Settings page

6. Create Mockups:
   - Invoke frontend-design skill:
     → Create dashboard-v1.html (responsive, with chart placeholders)
     → Create settings-v1.html (form layout)

7. Save Artifacts:
   - docs/ideas/mobile-app-idea/mockups/dashboard-v1.html
   - docs/ideas/mobile-app-idea/mockups/dashboard-v1.css
   - docs/ideas/mobile-app-idea/mockups/settings-v1.html
   - docs/ideas/mobile-app-idea/mockups/settings-v1.css

8. Update Summary:
   - Create docs/ideas/mobile-app-idea/idea-summary-v2.md with mockup links

9. Human Review:
   - Present mockups for approval
   - "Open docs/ideas/mobile-app-idea/mockups/dashboard-v1.html in browser to preview"

10. Output:
    task_output_links:
      - docs/ideas/mobile-app-idea/mockups/dashboard-v1.html
      - docs/ideas/mobile-app-idea/mockups/settings-v1.html
      - docs/ideas/mobile-app-idea/idea-summary-v2.md

11. Resume Task Flow from task-execution-guideline skill
```

---

## Example 2: Mockup WITHOUT Tools (Manual Mode)

**Input:**
- `Current Idea Folder`: `docs/ideas/simple-idea`

**Config:** `docs/ideas/.ideation-tools.json`
```json
{
  "version": "1.0",
  "mockup": {
    "frontend-design": false,
    "figma-mcp": false
  }
}
```

**Execution:**
```
1. Validate Current Idea Folder:
   - Current Idea Folder = docs/ideas/simple-idea ✓

2. Load Config:
   - All mockup tools disabled
   - Ask human: "No mockup tools enabled. Proceed with manual description?"

3. If human approves manual mode:
   - Create mockup-description.md with:
     - Detailed layout descriptions
     - Component specifications
     - ASCII wireframes (optional)
   - Save to docs/ideas/simple-idea/mockups/mockup-description.md

4. Output:
   task_output_links:
     - docs/ideas/simple-idea/mockups/mockup-description.md

5. If human declines:
   - Skip mockup creation
   - Note in idea summary: "Mockups deferred - no tools available"
   - Proceed to next task
```

---

## Example 3: Missing Idea Folder (Blocked)

**Input:**
- `Current Idea Folder`: N/A (not provided)

**Execution:**
```
1. Check Current Idea Folder:
   - Value is N/A → BLOCKED

2. List available folders:
   $ ls docs/ideas/
   - mobile-app-idea/
   - e-commerce-checkout/
   - simple-tool/

3. Ask human:
   "Which idea folder should I create mockups for?
   
   Available folders:
   1. mobile-app-idea
   2. e-commerce-checkout
   3. simple-tool"

4. Wait for human selection

5. Human selects: "mobile-app-idea"

6. Set Current Idea Folder = docs/ideas/mobile-app-idea

7. Continue with mockup creation...
```

---

## Example 4: No Idea Summary (Blocked)

**Input:**
- `Current Idea Folder`: `docs/ideas/new-project`

**Execution:**
```
1. Validate Current Idea Folder:
   - Folder exists ✓
   - Check for idea-summary-vN.md → NOT FOUND

2. BLOCKED - Missing prerequisite:
   "No idea summary found in docs/ideas/new-project/
    
    Action needed: Run Ideation task first to create idea-summary-v1.md"

3. Return:
   status: blocked
   reason: "Missing idea summary - run Ideation first"
```
