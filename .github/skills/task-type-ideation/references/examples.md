# Ideation - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Business Plan Ideation with Tools Enabled

**Scenario:** User uploads business plan draft to `x-ipe-docs/ideas/mobile-app-idea/files/`

**Config File:** `x-ipe-docs/config/tools.json`
```json
{
  "version": "2.0",
  "stages": {
    "ideation": {
      "ideation": {
        "antv-infographic": true,
        "mermaid": true
      },
      "mockup": {
        "frontend-design": true
      },
      "sharing": {}
    }
  }
}
```

**Execution:**
```
1. Execute Task Flow from task-execution-guideline skill

2. Load Toolbox Meta:
   - Read x-ipe-docs/config/tools.json
   - Enabled tools:
     - stages.ideation.ideation.antv-infographic: true → will invoke infographic-syntax-creator
     - stages.ideation.ideation.mermaid: true → will use mermaid diagrams
     - stages.ideation.mockup.frontend-design: true → will invoke frontend-design skill

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
     → config.stages.ideation.ideation.mermaid == true
     → Generate mermaid flowchart to visualize
   - User wants to see dashboard layout:
     → config.stages.ideation.mockup.frontend-design == true  
     → Invoke frontend-design skill
     → Create HTML mockup, save to x-ipe-docs/ideas/mobile-app-idea/mockup-v1.html
   - Share mockup: "Does this layout match your vision?"
   - Iterate based on feedback

7. Research Common Principles (if applicable):
   - Mobile app → Research: Mobile UX best practices, offline-first patterns
   - User auth → Research: OAuth 2.0, biometric auth standards
   - Document sources for references section

8. Create x-ipe-docs/ideas/mobile-app-idea/idea-summary-v1.md with:
   - Overview and problem statement (text)
   - Key Features (config.stages.ideation.ideation.antv-infographic == true → use infographic: list-grid-badge-card)
   - User Flow (config.stages.ideation.ideation.mermaid == true → use mermaid flowchart)
   - Implementation Phases (infographic: sequence-roadmap-vertical-simple)
   - Platform Comparison (infographic: compare-binary-horizontal-badge-card-arrow)
   - Ideation Artifacts section with link to mockups created
   - References & Common Principles section with researched sources

9. Resume Task Flow from task-execution-guideline skill
```

---

## Example 2: Ideation WITHOUT Tools (All Disabled)

**Config File:** `x-ipe-docs/config/tools.json`
```json
{
  "version": "2.0",
  "stages": {
    "ideation": {
      "ideation": {
        "antv-infographic": false,
        "mermaid": false
      },
      "mockup": {
        "frontend-design": false
      },
      "sharing": {}
    }
  }
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
     - x-ipe-docs/ideas/{folder}/idea-summary-v1.md
```

---

## Example 3: Missing Config File

**Scenario:** No `x-ipe-docs/config/tools.json` exists

**Execution:**
```
1. Check for x-ipe-docs/config/tools.json
   → File NOT FOUND

2. Create default config file:
   {
     "version": "2.0",
     "stages": {
       "ideation": {
         "ideation": {
           "antv-infographic": false,
           "mermaid": false
         },
         "mockup": {
           "frontend-design": false
         },
         "sharing": {}
       }
     }
   }

3. Inform user:
   "Created default x-ipe-docs/config/tools.json with all tools disabled.
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
   FROM: x-ipe-docs/ideas/Draft Idea - 01232026 131611/
   TO:   x-ipe-docs/ideas/E-Commerce Checkout - 01232026 131611/

4. Update all internal links in idea-summary-v1.md

5. Output includes new folder path
```
