# Requirement Gathering - Examples

## Example: Add User Authentication

**Request:** "Add user authentication"

**Execution:**
```
1. Execute Task Flow from x-ipe-workflow-task-execution skill

2. Understand Request:
   - WHAT: User authentication system
   - WHO: End users of the application
   - WHY: Security, user management

3. Ask Clarifying Questions:
   - "Should we support OAuth (Google/GitHub)?" -> Yes, Google
   - "Password reset needed?" -> Yes, via email
   - "Remember me functionality?" -> Yes

4. Create x-ipe-docs/requirements/requirement-details.md:
   # Requirement Summary
   ... (fill all sections) ...

5. Return Task Completion Output:
   category: requirement-stage
   status: completed
   next_task_based_skill: Feature Breakdown
   require_human_review: Yes
   task_output_links:
     - x-ipe-docs/requirements/requirement-details.md

6. Resume Task Flow from x-ipe-workflow-task-execution skill
```
