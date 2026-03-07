---
name: x-ipe-task-based-feature-closing
description: Close completed feature and create pull request. Use when human has validated the playground and feature is ready to ship. Provides procedures for final verification, PR creation, and documentation. Triggers on requests like "close feature", "create PR", "ship feature".
---

# Task-Based Skill: Feature Closing

## Purpose

Close a completed feature and ship it by:
1. Verifying all acceptance criteria are met
2. Reviewing code to sync documentation artifacts (specification, technical design, tests)
3. Updating project files (e.g., README) if needed
4. Running refactoring analysis scoped to the feature
5. Creating a pull request with proper description
6. Outputting completion summary with refactoring recommendations

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

**BLOCKING: Single Feature Only.** This skill operates on exactly ONE feature at a time. Do NOT batch or combine multiple features in a single execution. If multiple features need processing, run this skill separately for each feature.

IMPORTANT: When `process_preference.auto_proceed == "auto"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "Feature Closing"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      specification: "path | N/A | auto-detect"
      refactor-report: "path | N/A | auto-detect"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill: "User Manual"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  feature_phase: "Feature Closing"

  # Required inputs
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

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.auto_proceed" source="from caller (x-ipe-workflow-task-execution) or default 'manual'" />
  <field name="feature_id" source="previous task (Acceptance Test) output OR task board OR human input">
    <steps>
      1. IF previous task was "Feature Acceptance Test" → extract from task_output_links.feature_id
      2. ELIF task board has feature_id in task data → use it
      3. ELSE → IF auto_proceed == "auto": derive from workflow context or x-ipe-dao-end-user-representative; ELSE: ask human for feature_id
    </steps>
  </field>
  <field name="feature_title" source="feature specification OR features.md">
    <steps>
      1. Query feature board for feature_id → extract title
      2. ELIF x-ipe-docs/features/{feature_id}/specification.md exists → extract title from header
      3. ELSE → IF auto_proceed == "auto": derive from feature_id context; ELSE: ask human
    </steps>
  </field>
  <field name="feature_version" source="features.md OR default '1.0.0'">
    <steps>
      1. Query feature board for feature_id → extract version
      2. ELIF not found → default to "1.0.0"
    </steps>
  </field>
  <field name="git_strategy" source=".x-ipe.yaml configuration">
    <steps>
      1. Read .x-ipe.yaml → extract git.strategy value
      2. Expected values: "main-branch-only" | "dev-session-based"
    </steps>
  </field>
  <field name="git_main_branch" source="auto-detect from git">
    <steps>
      1. Run: git symbolic-ref refs/remotes/origin/HEAD → extract branch name
      2. Fallback: "main"
    </steps>
  </field>
  <field name="git_dev_branch" source="derived from git config user.name (sanitized)">
    <steps>
      1. Run: git config user.name → sanitize (lowercase, spaces→hyphens, remove special chars)
      2. Branch name: dev/{sanitized_git_user_name}
      3. Only used when git_strategy == "dev-session-based"
    </steps>
  </field>
  <field name="specification_path" source="auto-detect from feature folder">
    <steps>
      1. Check x-ipe-docs/features/{feature_id}/specification.md
      2. IF exists → use path
      3. ELSE → check x-ipe-docs/requirements/{feature_id}/specification.md (legacy)
    </steps>
  </field>
</input_init>
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
| 2 | Code-to-Docs Review | Subagent reviews code and suggests updates to specification, technical design, and tests | Review complete |
| 3 | Update Project Files | Update README or other project files if needed | Files updated |
| 4 | Refactoring Analysis | Subagent runs refactoring analysis scoped to feature | Analysis complete |
| 5 | Ship | Push to main (main-branch-only) or push dev branch & create PR (dev-session-based) | Shipped |
| 6 | Output Summary | Provide completion summary with refactoring recommendations | Summary delivered |
| 7.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| 7.2 | Execute Next Action | Delegate to x-ipe-workflow-task-execution sub-agent | Sub-agent started |

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
         Also verify UI against linked mockups — layout matches design, all UI elements present, interactions work as shown, visual styling is consistent, document any approved deviations.
         TIP: Use Chrome DevTools MCP with multi-session mode to perform UI validation (navigate pages, take screenshots, inspect elements, verify interactions). Chrome must be launched with `--user-data-dir` (dedicated profile) or the MCP server configured with `--user-data-dir` or `--isolated=true` to avoid conflicts with existing Chrome sessions.
      4. Document verification results in table format (see references/examples.md)
      5. Flag any unmet criteria
    </action>
    <constraints>
      - BLOCKING: If ANY criterion is not met, present options: (a) address gap, (b) modify criterion, (c) defer
        Response source (based on auto_proceed):
        IF process_preference.auto_proceed == "auto":
          → Resolve via x-ipe-dao-end-user-representative
        ELSE (manual/stop_for_question):
          → Ask human for decision
      - BLOCKING: Do NOT proceed to Step 2 until all criteria are verified
      - CRITICAL (manual/stop_for_question): Present unmet criteria to human with options
      - CRITICAL (auto): Resolve unmet criteria via x-ipe-dao-end-user-representative
    </constraints>
    <output>Acceptance criteria verification table with status and evidence</output>
  </step_1>

  <step_2>
    <name>Code-to-Docs Review</name>
    <action>
      1. Launch a sub-agent to perform a constructive critique of the implemented code
      2. The sub-agent compares actual code against:
         - Feature specification (x-ipe-docs/features/{FEATURE-XXX}/specification.md)
         - Technical design (x-ipe-docs/features/{FEATURE-XXX}/technical-design.md)
         - Test cases (test files referenced in technical design)
      3. For each artifact, the sub-agent identifies:
         - Behavioral differences: code does something the doc doesn't describe, or vice versa
         - Missing coverage: code paths or edge cases not reflected in tests
         - Stale references: renamed functions, changed APIs, removed parameters
      4. Sub-agent produces a change report with concrete suggestions per artifact
      5. Apply necessary updates to specification, technical design, and test files so they accurately reflect the shipped code
      6. Skip trivial or cosmetic differences — only update when the doc would mislead a future reader
    </action>
    <constraints>
      - CRITICAL: This is a constructive review, not a refactoring step — do NOT change implementation code
      - CRITICAL: Only update docs/tests to match what the code actually does, not the other way around
      - MANDATORY: Use a sub-agent for the review to get an independent perspective
    </constraints>
    <output>Change report listing updated artifacts and what changed in each</output>
  </step_2>

  <step_3>
    <name>Update Project Files</name>
    <action>
      1. Update README if feature is user-facing
      2. Update API docs if endpoints were added/changed
      3. Ensure complex logic has code comments
      4. Verify all feature doc artifacts are present in x-ipe-docs/features/{FEATURE-XXX}/
    </action>
    <constraints>
      - CRITICAL: All user-facing changes must be documented in README
    </constraints>
    <output>Updated project files</output>
  </step_3>

  <step_4>
    <name>Refactoring Analysis</name>
    <action>
      1. Launch a sub-agent to execute x-ipe-tool-refactoring-analysis with:
         - initial_refactoring_scope:
             scope_level: "feature"
             feature_id: "{feature_id}"
             refactoring_purpose: "Optimize technical design and code maintainability based on best coding practices at project-wide level"
      2. The sub-agent resolves feature files from x-ipe-docs/features/{feature_id}/
      3. Sub-agent performs scope expansion, quality evaluation, and generates suggestions
      4. Collect the analysis result:
         - overall_quality_score
         - refactoring_suggestion (goals, priorities)
         - key gaps identified
      5. Store analysis result for inclusion in Output Summary (step 6)
    </action>
    <constraints>
      - CRITICAL: This is analysis only — do NOT execute any refactoring in this step
      - CRITICAL: The sub-agent should complete the full refactoring-analysis skill but stop at output (do NOT proceed to improve-code-quality or code-refactor)
      - NOTE: If analysis finds no actionable suggestions, record "no refactoring needed" and proceed
    </constraints>
    <output>Refactoring analysis result with quality score and suggestions</output>
  </step_4>

  <step_5>
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
  </step_5>

  <step_6>
    <name>Output Summary</name>
    <action>
      1. IF execution_mode == "workflow-mode":
         a. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with:
            - workflow_name: {from context}
            - action: "feature_closing"
            - status: "done"
            - feature_id: {feature_id}
            - deliverables: {"closing-report": "{path}"}
         b. Log: "Workflow action status updated to done"
      2. Compile completion summary (see references/examples.md for template)
      3. Include: deliverables, files changed, criteria status, PR link
      4. Include refactoring analysis results:
         - Overall quality score from analysis
         - IF refactoring suggestions exist: list top suggestions with priority
         - IF overall_quality_score < 7: flag "Refactoring recommended" with summary of key improvements
         - IF overall_quality_score >= 7: note "Code quality is acceptable, optional improvements listed"
      5. Present summary with clear recommendation on whether refactoring is needed
      6. IF refactoring_score < 7: flag "Refactoring recommended"

        Completion gate (based on auto_proceed):
        IF process_preference.auto_proceed == "auto":
          → Auto-proceed after DoD verification, log refactoring recommendation via x-ipe-dao-end-user-representative
        ELSE (manual/stop_for_question):
          → Ask human to acknowledge summary
    </action>
    <output>Feature completion summary with refactoring recommendation delivered to human</output>
  </step_6>

  <phase_7 name="继续执行（Continue Execute）">
    <step_7_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.auto_proceed == "auto":
          → Invoke x-ipe-dao-end-user-representative with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the context and full output to decide best next action."
          → DAO studies the complete context and decides the best next action
        ELSE (manual):
          → Present next task suggestion to human and wait for instruction
      </action>
      <constraints>
        - BLOCKING (manual): Human MUST confirm or redirect before proceeding
        - BLOCKING (auto): Proceed after DoD verification; auto-select next task via DAO
      </constraints>
      <output>Next action decided with execution context</output>
    </step_7_1>
    <step_7_2>
      <name>Execute Next Action</name>
      <action>
        Based on the decision from Step 7.1, delegate execution to a sub-agent:
        1. Invoke x-ipe-workflow-task-execution as a sub-agent (use premium model)
        2. Pass the decided next task and full context from Step 7.1
        3. The workflow skill handles: skill loading, execution plan generation, and execution
      </action>
      <constraints>
        - MUST delegate to x-ipe-workflow-task-execution — do not execute the next skill directly
        - Sub-agent MUST use premium model (Best-Model Requirement)
        - Execution follows the workflow skill's 6-step orchestration
      </constraints>
      <output>Sub-agent started with x-ipe-workflow-task-execution</output>
    </step_7_2>
  </phase_7>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill: "User Manual"
  process_preference:
    auto_proceed: "{from input process_preference.auto_proceed}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "{PR link (dev-session-based) or 'pushed to main' (main-branch-only)}"
    - "x-ipe-docs/features/{FEATURE-XXX}/"
    - "x-ipe-docs/refactoring/analysis-{task_id}.md"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Feature Closing"
  refactoring_analysis:
    overall_quality_score: "{1-10}"
    refactoring_recommended: "true | false"
    top_suggestions: ["{summary of key suggestions}"]
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
    <name>Code-to-docs review completed</name>
    <verification>Sub-agent reviewed code against specification, technical design, and tests; necessary updates applied</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Project files updated</name>
    <verification>README and other project files updated where applicable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Refactoring analysis completed</name>
    <verification>Sub-agent ran refactoring analysis on feature scope; results stored for summary</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>PR created or code pushed to main</name>
    <verification>If dev-session-based: PR exists with title, description, linked feature, and checklist; branch name uses git user identity. If main-branch-only: code pushed to main, no branches or PRs created.</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Summary provided to human</name>
    <verification>Completion summary with deliverables, files, PR link, and refactoring recommendation presented</verification>
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
2. Code-to-docs review - no gaps found
3. Update project files - complete
4. Refactoring analysis - score 8/10, no urgent issues
5. Create PR - PR #123
6. Output summary (refactoring: optional improvements only)
7. DONE
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
4. Code-to-docs review - updated spec
5. Refactoring analysis - score 5/10, refactoring recommended
6. Continue to PR (with refactoring flag in summary)
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| PR without testing | Broken code merged | Ensure all tests pass first |
| Empty PR description | Reviewer cannot understand changes | Use PR template from references/ |
| Skipping criteria check | Incomplete feature shipped | Verify each criterion with evidence |
| Giant multi-feature PR | Hard to review and revert | Keep PR scoped to single feature |
| Creating feature branches in main-branch-only mode | Unnecessary complexity, violates strategy | BLOCKING: Check git_strategy BEFORE any branch operations; if main-branch-only, stay on main |
| Using agent nickname for dev branch name | Branch not tied to git identity | Use `git config user.name` (sanitized) for dev branch name, NOT agent nickname |

---

## Examples

See [references/examples.md](.github/skills/x-ipe-task-based-feature-closing/references/examples.md) for concrete execution examples, verification templates, and human communication templates.
