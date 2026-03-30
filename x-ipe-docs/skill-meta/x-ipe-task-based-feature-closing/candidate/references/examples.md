# Feature Closing Examples

> **Legacy Note:** Examples below use the Epic-aware folder structure (`EPIC-{nnn}/FEATURE-{nnn}-{X}/`). Projects created before the Epic migration may still use the legacy format (`FEATURE-{nnn}/`). Both formats are supported during the transition period.

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

4. Step 2 - Code-to-Docs Review:
   - Sub-agent reviewed code against spec, design, tests
   - No significant gaps found
   - Minor: added missing rate-limit edge case to specification

5. Step 3 - Update Project Files:
   - README.md updated
   - API docs added

6. Step 4 - Refactoring Analysis:
   - Sub-agent ran refactoring analysis on FEATURE-002
   - Scope: 8 files, 2 modules
   - Overall quality score: 8/10
   - No urgent refactoring needed
   - Optional: extract token management into separate module (medium priority)

7. Step 5 - Create PR:
   Created PR #42:
   "feat: Email/Password Authentication"
   
   Description includes:
   - Summary of changes
   - Files changed
   - Test coverage
   - Screenshots

8. Step 6 - Summary:
   
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
   
   ### Refactoring Assessment
   - Quality Score: 8/10
   - Refactoring recommended: No (optional improvements only)
   - Suggestion: extract token management into separate module (medium priority)

9. Return Task Completion Output:
   feature_id: FEATURE-002
   feature_status: Done Feature Closing
   category: feature-stage
   next_task_based_skill: User Manual
   require_human_review: No
   task_output_links:
     - PR #42
     - x-ipe-docs/features/EPIC-002/FEATURE-002-A/
   refactoring_analysis:
     overall_quality_score: 8
     refactoring_recommended: false
     top_suggestions: ["extract token management module"]

10. Resume Task Flow from x-ipe-workflow-task-execution skill
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

### Refactoring Assessment
- Quality Score: [X/10]
- Refactoring recommended: [Yes/No]
- Top suggestions: [list if any]

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
