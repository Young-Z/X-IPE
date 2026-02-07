# Feature Closing Examples

## Example: Email/Password Login (FEATURE-002)

```
1. Execute Task Flow from x-ipe-workflow-task-execution skill

2. DoR Check:
   - Code implementation complete
   - Feature status: Implemented
   - Tests passing

3. Step 1 - Verify Criteria:
   Acceptance Criteria:
   - [x] User can login with email/password
   - [x] Invalid credentials show error
   - [x] Token returned on success
   - [x] Rate limiting works
   
   All 4/4 met

4. Step 2 - Documentation:
   - README.md updated
   - API docs added
   - CHANGELOG.md entry added

5. Step 3 - Create PR:
   Created PR #42:
   "feat: Email/Password Authentication"
   
   Description includes:
   - Summary of changes
   - Files changed
   - Test coverage
   - Screenshots

6. Step 4 - Summary:
   
   ## Feature Complete: Email/Password Login
   
   ### Delivered
   - User registration
   - Login/logout endpoints
   - JWT token management
   - Rate limiting
   
   ### Files
   - 8 files added
   - 2 files modified
   - 15 tests added
   
   ### PR
   - PR #42: feat: Email/Password Authentication

7. Return Task Completion Output:
   feature_id: FEATURE-002
   feature_status: Done Feature Closing
   category: feature-stage
   next_task_based_skill: User Manual
   require_human_review: No
   task_output_links:
     - PR #42
     - CHANGELOG.md
     - x-ipe-docs/features/FEATURE-002/

8. Resume Task Flow from x-ipe-workflow-task-execution skill
   (Feature chain COMPLETE)
```

## Verification Template

Use this table format when documenting acceptance criteria verification:

```markdown
## Acceptance Criteria Verification

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | [Criterion 1] | Met | [How verified] |
| 2 | [Criterion 2] | Met | [How verified] |
| 3 | [Criterion 3] | Not Met | [What's missing] |
| 4 | UI matches mockup (if applicable) | Met | Visual comparison |
```

## Completion Summary Template

```markdown
## Feature Complete: [Feature Name]

### Delivered
- [Key deliverable 1]
- [Key deliverable 2]

### Files Changed
- X files added
- Y files modified
- Z tests added

### Acceptance Criteria
- [X/Y] criteria met

### Pull Request
- PR #XXX: [Title]
- [Link to PR]

### Notes
- [Any important notes for reviewer]
```

## Human Communication Template

When closing is complete:

```
Feature [Name] is complete!

PR: #XXX - [Title]
[Link to PR]

Summary:
- [Key point 1]
- [Key point 2]

All acceptance criteria verified. Ready for review/merge.
```
