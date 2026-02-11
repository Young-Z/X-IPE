# Requirement Gathering - Examples

## Example 1: New Feature — No Conflicts

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

4. Conflict Review:
   - Scanned requirement-details-part-1.md through part-3.md
   - No existing features cover authentication
   - Result: "No conflicts found with existing requirements"

5. (Skipped — no conflicts)

6. Create x-ipe-docs/requirements/requirement-details.md:
   # Requirement Summary
   ... (fill all sections) ...

7. Return Task Completion Output:
   category: requirement-stage
   status: completed
   next_task_based_skill: Feature Breakdown
   require_human_review: Yes
   conflict_review_completed: true
   conflicts_found: 0
   impacted_features: []

8. Resume Task Flow from x-ipe-workflow-task-execution skill
```

## Example 2: New Feature — Overlap Found → CR Decision

**Request:** "Add session explorer sidebar to the console"

**Execution:**
```
1. Understand Request:
   - WHAT: Session explorer with sidebar for managing multiple terminal sessions
   - WHO: Developers using the console
   - WHY: Replace limited 2-pane split with up to 10 sessions

2. Ask Clarifying Questions:
   - "Right-side or left-side?" → Right-side, collapsible
   - "Max sessions?" → 10
   - "Preview on hover?" → Yes, live mini-terminal

3. Conflict Review:
   - Scanned all requirement-details files
   - Found overlap with FEATURE-005 (Console Terminal):
   
   | Aspect | New Requirement | Existing Feature (FEATURE-005) | Overlap Type |
   |--------|----------------|-------------------------------|--------------|
   | Terminal management | Session explorer with 10 sessions | 2-pane split terminal | Scope overlap |
   | Terminal switching | Click to switch active session | Split-pane layout | Functional overlap |
   
   - Recommendation: "The session explorer is an INDEPENDENT feature with its
     own lifecycle (new UI component, new interaction patterns). FEATURE-005
     handles terminal I/O and PTY management which remains unchanged.
     Recommend: New standalone feature."
   - Human decision: "Agreed, new standalone feature FEATURE-029"

4. Update Impacted Features:
   - No CR markers needed (human chose "new feature")
   - Added cross-reference dependency note for Step 6

5. Check File: part-6 has 473 lines → create part-7

6. Document in requirement-details-part-7.md:
   - FEATURE-029: Console Session Explorer
   - Related Features section: "Related to FEATURE-005 (Console Terminal)
     but independent lifecycle. FEATURE-005 provides terminal I/O;
     FEATURE-029 provides session management UI."

7. Complete: DoD verified, human approved
```

## Example 3: New Feature — Overlap Found → CR Decision

**Request:** "Add dark mode toggle to settings"

**Execution:**
```
1. Understand: Dark mode toggle in settings panel

2. Clarify: Theme applies globally, persists in localStorage

3. Conflict Review:
   - Found overlap with FEATURE-028-B (Settings Theme):
   
   | Aspect | New Requirement | Existing Feature (FEATURE-028-B) | Overlap Type |
   |--------|----------------|--------------------------------|--------------|
   | Theme switching | Dark mode toggle | Theme configuration panel | Scope overlap |
   
   - Recommendation: "Dark mode is part of the SAME responsibility as
     theme configuration (single responsibility principle). It shares
     the same UI location, same user, same data store. High cohesion
     with existing feature. Recommend: CR on FEATURE-028-B."
   - Human decision: "Agreed, CR on FEATURE-028-B"

4. Update Impacted Features:
   - Located FEATURE-028-B in requirement-details-part-6.md
   - Appended CR impact marker:
     > **⚠️ CR Impact Note** (added 2026-02-11, ref: dark-mode-toggle)
     > - **Change:** Add dark/light mode toggle to theme settings
     > - **Affected FRs:** FR-028-B.1, FR-028-B.3
     > - **Action Required:** Feature specification refactoring needed
     > - **New Feature Ref:** See requirement-details-part-7.md

5. Check File: part-6 at 473 lines → create part-7

6. Document: New requirement with "Related Features" section
   referencing CR on FEATURE-028-B

7. Complete: DoD verified, human approved
   impacted_features: [FEATURE-028-B]
```
