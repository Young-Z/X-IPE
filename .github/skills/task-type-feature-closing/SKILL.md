---
name: task-type-feature-closing
description: Close completed feature and create pull request. Use when human has validated the playground and feature is ready to ship. Provides procedures for final verification, PR creation, and documentation.
---

# Task Type: Feature Closing

## Purpose

Execute **Feature Closing** tasks by:
1. Verifying acceptance criteria
2. Finalizing documentation
3. Creating pull request
4. Outputting summary

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Feature Closing |
| Category | feature-stage |
| Next Task Type | User Manual |
| Require Human Review | No |
| Feature Phase | Feature Closing |

---

## Skill Output

This skill MUST return these attributes to the Task Data Model:

```yaml
Output:
  status: completed | blocked
  next_task_type: User Manual
  require_human_review: No
  task_output_links: [PR link, changelog]
  
  # Feature stage dynamic attributes (REQUIRED)
  category: feature-stage
  feature_id: FEATURE-XXX
  feature_title: {title}
  feature_version: {version}
  feature_phase: Feature Closing
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Human has tested playground | Yes |
| 2 | Feature status is "Done Human Playground" | Yes |
| 3 | All tests passing | Yes |

---

## Execution Procedure

### Step 1: Verify Acceptance Criteria

**Action:** Confirm all criteria are met

```
1. Get acceptance criteria from feature scope
2. Check each criterion
3. Document verification results
4. Flag any unmet criteria
```

**Verification Template:**

```markdown
## Acceptance Criteria Verification

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | [Criterion 1] | ✓ Met | [How verified] |
| 2 | [Criterion 2] | ✓ Met | [How verified] |
| 3 | [Criterion 3] | ✗ Not Met | [What's missing] |
```

**If criteria not met:**
- Stop and report to human
- Do not proceed to PR creation
- Wait for guidance

### Step 2: Finalize Documentation

**Action:** Ensure all docs are complete and current

**Documentation Checklist:**

| Document | Status Check |
|----------|--------------|
| README (if user-facing) | Updated with new feature |
| API docs | Endpoints documented |
| Code comments | Complex logic explained |
| Changelog | Entry added |
| Feature docs | All artifacts present |

**Changelog Entry Format:**

```markdown
## [Version] - YYYY-MM-DD

### Added
- [Feature name]: [Brief description]

### Changed
- [Any changes to existing behavior]

### Fixed
- [Any bugs fixed during implementation]
```

### Step 3: Create Pull Request

**Action:** Create PR with proper description

**PR Title Format:**
```
feat: [Feature Name] - [Brief Description]
```

**PR Description Template:**

```markdown
## Summary
[1-2 sentences describing what this PR adds]

## Related
- Feature: FEATURE-XXX
- Design: [link to design doc]

## Changes
- [Major change 1]
- [Major change 2]
- [Major change 3]

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Human playground tested

## Screenshots/Demo
[If applicable]

## Checklist
- [ ] Code follows project conventions
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Step 4: Output Summary

**Action:** Provide completion summary

**Summary Template:**

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

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Acceptance criteria verified | Yes |
| 2 | Documentation finalized | Yes |
| 3 | PR created with proper description | Yes |
| 4 | Summary provided to human | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Task Completion Output

Upon completion, return:
```yaml
feature_id: {Feature ID}
feature_status: {In|Done} {Feature Phase}
category: {Category}
next_task_type: {Next Task Type}
require_human_review: {Require Human Review}
task_output_links:
  - PR #{number}
  - CHANGELOG.md
  - docs/features/{FEATURE-ID}/
```

---

## Output Artifacts

| Artifact | Location | Description |
|----------|----------|-------------|
| PR | GitHub/GitLab | Pull request |
| Changelog | `CHANGELOG.md` | Version entry |
| Summary | (in chat) | Completion report |
| Status Log | `docs/features/FEATURE-XXX/changelog.md` | Feature history |

---

## Patterns

### Pattern: All Criteria Met

```
1. Verify criteria → All met ✓
2. Update docs → Complete ✓
3. Create PR → PR #123
4. Output summary
5. DONE
```

### Pattern: Criteria Not Met

```
1. Verify criteria → 1 not met
2. STOP
3. Report to human:
   "Criterion X not met: [details]
    Options:
    a) Address the gap
    b) Modify criterion
    c) Defer to future"
4. Wait for guidance
```

### Pattern: Minor Issues Found

```
1. Verify criteria → Met with minor issues
2. Fix minor issues
3. Re-verify → All met ✓
4. Continue to PR
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Instead |
|--------------|---------|---------|
| PR without testing | Broken code merged | Ensure tests pass |
| Empty PR description | Reviewer confused | Write complete description |
| Skipping criteria check | Incomplete feature | Verify each criterion |
| Giant PR | Hard to review | Keep focused on one feature |
| No changelog | Lost history | Always update changelog |

---

## Example

**Feature:** FEATURE-002 Email/Password Login

```
1. Execute Task Flow from task-execution-guideline skill

2. DoR Check:
   - Human tested playground ✓
   - Feature status: Done Human Playground ✓
   - Tests passing ✓

3. Step 1 - Verify Criteria:
   Acceptance Criteria:
   - [x] User can login with email/password
   - [x] Invalid credentials show error
   - [x] Token returned on success
   - [x] Rate limiting works
   
   All 4/4 met ✓

4. Step 2 - Documentation:
   - README.md updated ✓
   - API docs added ✓
   - CHANGELOG.md entry added ✓

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
   next_task_type: N/A
   require_human_review: No
   task_output_links:
     - PR #42
     - CHANGELOG.md
     - docs/features/FEATURE-002/

8. Resume Task Flow from task-execution-guideline skill
   (Feature chain COMPLETE)
```

---

## Human Communication

When closing is complete:

```
Feature [Name] is complete! 🎉

PR: #XXX - [Title]
[Link to PR]

Summary:
- [Key point 1]
- [Key point 2]

All acceptance criteria verified. Ready for review/merge.
```
