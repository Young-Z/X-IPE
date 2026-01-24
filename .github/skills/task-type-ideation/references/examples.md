# Ideation - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Business Plan Ideation with Tools Enabled

**Scenario:** User uploads business plan draft to `docs/ideas/mobile-app-idea/files/`

**Config File:** `docs/ideas/.ideation-tools.json`
```json
{
  "version": "1.0",
  "ideation": {
    "antv-infographic": true,
    "mermaid": true
  },
  "mockup": {
    "frontend-design": true
  },
  "sharing": {}
}
```

**Execution:**
```
1. Execute Task Flow from task-execution-guideline skill

2. Load Toolbox Meta:
   - Read docs/ideas/.ideation-tools.json
   - Enabled tools:
     - ideation.antv-infographic: true → will invoke infographic-syntax-creator
     - ideation.mermaid: true → will use mermaid diagrams
     - mockup.frontend-design: true → will invoke frontend-design skill

3. Analyze Files:
   - Read business-plan.md
   - Read user-research.txt
   - Read competitor-notes.md

4. Initialize Tools:
   - infographic-syntax-creator skill → Available
   - mermaid capability → Available  
   - frontend-design skill → Available
   - Status: All enabled tools ready

5. Generate Summary:
   "I understand you want to build a mobile app for..."
   "Enabled tools: antv-infographic, mermaid (visualization), frontend-design (mockups)"
   
6. Brainstorming Questions (with Config-Driven Tool Usage):
   - "Your notes mention both iOS and Android - should v1 target both?"
   - "The user research shows two distinct personas - which is primary?"
   - User describes dashboard flow:
     → config.ideation.mermaid == true
     → Generate mermaid flowchart to visualize
   - User wants to see dashboard layout:
     → config.mockup.frontend-design == true  
     → Invoke frontend-design skill
     → Create HTML mockup, save to docs/ideas/mobile-app-idea/mockup-v1.html
   - Share mockup: "Does this layout match your vision?"
   - Iterate based on feedback

7. Research Common Principles (if applicable):
   - Mobile app → Research: Mobile UX best practices, offline-first patterns
   - User auth → Research: OAuth 2.0, biometric auth standards
   - Document sources for references section

8. Create docs/ideas/mobile-app-idea/idea-summary-v1.md with:
   - Overview and problem statement (text)
   - Key Features (config.ideation.antv-infographic == true → use infographic: list-grid-badge-card)
   - User Flow (config.ideation.mermaid == true → use mermaid flowchart)
   - Implementation Phases (infographic: sequence-roadmap-vertical-simple)
   - Platform Comparison (infographic: compare-binary-horizontal-badge-card-arrow)
   - Ideation Artifacts section with link to mockups created
   - References & Common Principles section with researched sources

9. Resume Task Flow from task-execution-guideline skill
```

---

## Example 2: Ideation WITHOUT Tools (All Disabled)

**Config File:** `docs/ideas/.ideation-tools.json`
```json
{
  "version": "1.0",
  "ideation": {
    "antv-infographic": false,
    "mermaid": false
  },
  "mockup": {
    "frontend-design": false
  },
  "sharing": {}
}
```

**Execution:** 
```
1. Load Toolbox Meta:
   - All tools disabled
   - Inform user: "No visualization tools configured"

2. Skip Step 4 (Initialize Tools) - no tools enabled

3. Proceed with standard brainstorming:
   - Ask clarifying questions
   - Gather requirements through conversation
   - No visual artifacts created during ideation

4. Create idea summary using standard markdown:
   - Bullet lists instead of infographics
   - Tables instead of visual comparisons
   - Text descriptions instead of diagrams

5. Output:
   task_output_links:
     - docs/ideas/{folder}/idea-summary-v1.md
```

---

## Example 3: Missing Config File

**Scenario:** No `.ideation-tools.json` exists

**Execution:**
```
1. Check for docs/ideas/.ideation-tools.json
   → File NOT FOUND

2. Create default config file:
   {
     "version": "1.0",
     "ideation": {
       "antv-infographic": false,
       "mermaid": false
     },
     "mockup": {
       "frontend-design": false
     },
     "sharing": {}
   }

3. Inform user:
   "Created default .ideation-tools.json with all tools disabled.
    To enable visualization tools, update the config file."

4. Proceed with standard text-based ideation
```

---

## Example 4: Draft Folder Rename

**Scenario:** Idea folder is named "Draft Idea - 01232026 131611"

**Execution:**
```
1. Complete ideation process...

2. Idea refined to: "E-Commerce Checkout System"

3. Rename Folder:
   FROM: docs/ideas/Draft Idea - 01232026 131611/
   TO:   docs/ideas/E-Commerce Checkout - 01232026 131611/

4. Update all internal links in idea-summary-v1.md

5. Output includes new folder path
```
