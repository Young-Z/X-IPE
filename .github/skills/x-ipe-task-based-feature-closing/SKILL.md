---
name: x-ipe-task-based-feature-closing
description: Close completed feature and create pull request. Use when human has validated the playground and feature is ready to ship. Provides procedures for final verification, PR creation, and documentation. Triggers on requests like "close feature", "create PR", "ship feature".
---

# Task-Based Skill: Feature Closing

## Purpose

Close a completed feature and ship it by:
1. Verifying all acceptance criteria are met
2. Finalizing documentation and changelog
3. Creating a pull request with proper description
4. Outputting completion summary

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
  task_based_skill: "Feature Closing"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill: "User Manual"
  require_human_review: false
  feature_phase: "Feature Closing"

  # Required inputs
  auto_proceed: false
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"

  # Git strategy (from .x-ipe.yaml, passed by workflow)
  git_strategy: "main-branch-only | dev-session-based"
  git_main_branch: "{auto-detected}"
  git_dev_branch: "dev/{git_user_name}"  # Only for dev-session-based; derived from `git config user.name` (sanitized: lowercase, spaces→hyphens)

  # Context (from previous task or project)
  specification_path: "x-ipe-docs/features/{FEATURE-XXX}/specification.md"
  test_results: "all passing"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Code implementation complete</name>
    <verification>All implementation code committed (on main if main-branch-only, on dev/{git_user_name} if dev-session-based)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Feature status is "Implemented"</name>
    <verification>Query feature board - status must be "Implemented"</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All tests passing</name>
    <verification>Run test suite - zero failures</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Verify Criteria | Check all acceptance criteria are met | All criteria met |
| 2 | Finalize Docs | Update README, API docs, CHANGELOG | Docs complete |
| 3 | Ship | Push to main (main-branch-only) or push dev branch & create PR (dev-session-based) | Shipped |
| 4 | Output Summary | Provide completion summary to human | Summary delivered |

BLOCKING: Step 1 to 2 is BLOCKED if any acceptance criterion is not met. STOP and report to human.

---

## Execution Procedure

```xml
<procedure name="feature-closing">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Verify Acceptance Criteria</name>
    <action>
      1. Read acceptance criteria from feature specification
      2. Check each criterion against implementation
      3. IF Technical Scope includes [Frontend] or [Full Stack]:
         Also verify UI against linked mockups — layout matches design, all UI elements present, interactions work as shown, visual styling is consistent, document any approved deviations
      4. Document verification results in table format (see references/examples.md)
      5. Flag any unmet criteria
    </action>
    <constraints>
      - BLOCKING: If ANY criterion is not met, STOP and report to human
      - BLOCKING: Do NOT proceed to Step 2 until all criteria are verified
      - CRITICAL: Present unmet criteria with options: (a) address gap, (b) modify criterion, (c) defer
    </constraints>
    <output>Acceptance criteria verification table with status and evidence</output>
  </step_1>

  <step_2>
    <name>Finalize Documentation</name>
    <action>
      1. Update README if feature is user-facing
      2. Update API docs if endpoints were added/changed
      3. Ensure complex logic has code comments
      4. Add changelog entry using template from references/templates/changelog-template.md
      5. Verify all feature doc artifacts are present in x-ipe-docs/features/{FEATURE-XXX}/
    </action>
    <constraints>
      - MANDATORY: Changelog entry must follow Keep a Changelog format
      - CRITICAL: All user-facing changes must be documented
    </constraints>
    <output>Updated documentation files and changelog entry</output>
  </step_2>

  <step_3>
    <name>Create Pull Request (conditional)</name>
    <action>
      IF git_strategy == "main-branch-only":
        1. CRITICAL: Do NOT create any branches — code is already on main
        2. Ensure agent is on {git_main_branch}: git checkout {git_main_branch}
        3. Stage and commit any remaining changes on {git_main_branch}
        4. Push to main: git push origin {git_main_branch}
        5. Skip PR creation — no PR needed for main-branch-only
        6. Log: "Strategy is main-branch-only — pushed directly to {git_main_branch}, no PR created"

      ELSE IF git_strategy == "dev-session-based":
        1. Resolve dev branch name:
           → Run: git config user.name (or git config user.email if user.name is empty)
           → Sanitize: lowercase, replace spaces with hyphens, remove special chars
           → Branch name: dev/{sanitized_git_user_name}
        2. Stage all feature changes
        3. Push dev branch to remote: git push origin dev/{git_user_name}
        4. Create PR from dev/{git_user_name} → {git_main_branch}
        5. Use PR template from references/templates/pr-template.md
        6. Title format: feat: [Feature Name] - [Brief Description]
        7. Link feature ID and design doc in PR description
        8. Include testing checklist status
    </action>
    <constraints>
      - BLOCKING (dev-session-based only): PR description must not be empty
      - CRITICAL: PR must be scoped to single feature
      - CRITICAL (dev-session-based): Branch name MUST use git user identity, NOT agent nickname
      - BLOCKING (main-branch-only): Do NOT create branches or PRs
    </constraints>
    <output>Pull request URL and number (dev-session-based) or push confirmation (main-branch-only)</output>
  </step_3>

  <step_4>
    <name>Output Summary</name>
    <action>
      1. Compile completion summary (see references/examples.md for template)
      2. Include: deliverables, files changed, criteria status, PR link
      3. Present summary to human
    </action>
    <output>Feature completion summary delivered to human</output>
  </step_4>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill: "User Manual"
  require_human_review: false
  auto_proceed: "{from input auto_proceed}"
  task_output_links:
    - "{PR link (dev-session-based) or 'pushed to main' (main-branch-only)}"
    - "CHANGELOG.md"
    - "x-ipe-docs/features/{FEATURE-XXX}/changelog.md"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Feature Closing"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Acceptance criteria verified</name>
    <verification>Verification table shows all criteria met with evidence</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Documentation finalized</name>
    <verification>README, API docs, and changelog updated where applicable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>PR created or code pushed to main</name>
    <verification>If dev-session-based: PR exists with title, description, linked feature, and checklist; branch name uses git user identity. If main-branch-only: code pushed to main, no branches or PRs created.</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Summary provided to human</name>
    <verification>Completion summary with deliverables, files, and PR link presented</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: All Criteria Met

**When:** Every acceptance criterion passes verification
**Then:**
```
1. Verify criteria - all met
2. Update docs - complete
3. Create PR - PR #123
4. Output summary
5. DONE
```

### Pattern: Criteria Not Met

**When:** One or more acceptance criteria fail verification
**Then:**
```
1. Verify criteria - 1 not met
2. STOP
3. Report to human with options:
   a) Address the gap
   b) Modify criterion
   c) Defer to future
4. Wait for guidance
```

### Pattern: Minor Issues Found

**When:** Criteria met but with minor fixable issues
**Then:**
```
1. Verify criteria - met with minor issues
2. Fix minor issues inline
3. Re-verify - all met
4. Continue to PR
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| PR without testing | Broken code merged | Ensure all tests pass first |
| Empty PR description | Reviewer cannot understand changes | Use PR template from references/ |
| Skipping criteria check | Incomplete feature shipped | Verify each criterion with evidence |
| Giant multi-feature PR | Hard to review and revert | Keep PR scoped to single feature |
| No changelog entry | Lost version history | Always update CHANGELOG.md |
| Creating feature branches in main-branch-only mode | Unnecessary complexity, violates strategy | BLOCKING: Check git_strategy BEFORE any branch operations; if main-branch-only, stay on main |
| Using agent nickname for dev branch name | Branch not tied to git identity | Use `git config user.name` (sanitized) for dev branch name, NOT agent nickname |

---

## Examples

See [references/examples.md](references/examples.md) for concrete execution examples, verification templates, and human communication templates.
