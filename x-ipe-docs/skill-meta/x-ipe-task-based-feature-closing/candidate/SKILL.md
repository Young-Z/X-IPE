---
name: x-ipe-task-based-feature-closing
description: Close completed feature and create pull request. Use when feature is implemented, tested, and ready to ship. Provides procedures for final verification, PR creation, and documentation. Triggers on requests like "close feature", "create PR", "ship feature".
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

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-assistant-user-representative-Engineer` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-feature-closing"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A
    extra_context_reference:  # optional, default: N/A for all refs
      specification: "path | N/A | auto-detect"
      refactor-report: "path | N/A | auto-detect"

  # Task type attributes
  category: "feature-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "Start next feature from backlog"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
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

  # Optional tools (end-user toggles)
  optional_tools:
    readme_updator: false  # when true, invoke x-ipe-tool-readme-updator in Phase 3
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="feature_id" source="previous task (Acceptance Test or Code Refactor) output OR task board OR human input">
    <steps>
      1. IF previous task was "Feature Acceptance Test" → use previous task output's feature_id field
      2. ELIF previous task was "Code Refactor" → use previous task output's feature_id field
      3. ELIF task board has feature_id in task data → use it
      4. ELSE → IF interaction_mode == "dao-represent-human-to-interact": derive from workflow context or x-ipe-assistant-user-representative-Engineer; ELSE: ask human for feature_id
    </steps>
  </field>
  <field name="feature_title" source="feature specification OR features.md">
    <steps>
      1. Query feature board for feature_id → extract title
      2. ELIF x-ipe-docs/features/{feature_id}/specification.md exists → extract title from header
      3. ELSE → IF interaction_mode == "dao-represent-human-to-interact": derive from feature_id context; ELSE: ask human
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
  <field name="optional_tools.readme_updator" source="end-user toggle, default false">
    <steps>
      1. IF caller provides optional_tools.readme_updator → use value
      2. ELSE → default to false (skip README update)
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

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 | Verify all acceptance criteria are met | All criteria met |
| 2. 审问之 — Inquire Thoroughly | 2.1 | Subagent reviews code against spec, design, tests | Review complete |
| 3. 慎思之 — Think Carefully | 3.1, 3.2 | Update project files, run refactoring analysis | Files updated, analysis complete |
| 4. 明辨之 — Discern Clearly | 4.1 | Push to main or create PR based on git strategy | Shipped |
| 5. 笃行之 — Practice Earnestly | 5.1 | Output completion summary with refactoring recommendations | Summary delivered |
| 继续执行 | 6.1 | Decide Next Action | Next action decided |
| 继续执行 | 6.2 | Execute Next Action | Execution started |

BLOCKING: Phase 1 to Phase 2 is BLOCKED if any acceptance criterion is not met. STOP and report to human.

---

## Execution Procedure

```xml
<procedure name="feature-closing">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">
    <step_1_1>
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
          Response source (based on interaction_mode):
          IF process_preference.interaction_mode == "dao-represent-human-to-interact":
            → Resolve via x-ipe-assistant-user-representative-Engineer
          ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
            → Ask human for decision
        - BLOCKING: Do NOT proceed to step_2_1 until all criteria are verified
        - CRITICAL (manual/stop_for_question): Present unmet criteria to human with options
        - CRITICAL (auto): Resolve unmet criteria via x-ipe-assistant-user-representative-Engineer
      </constraints>
      <output>Acceptance criteria verification table with status and evidence</output>
    </step_1_1>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <step_2_1>
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
    </step_2_1>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <step_3_1>
      <name>Update Project Files</name>
      <action>
        1. IF optional_tools.readme_updator == true:
           → Invoke x-ipe-tool-readme-updator with:
             operation: "update_readme"
             config.feature_context: { feature_id, feature_title }
           → Tool identifies, verifies, and documents run/test commands in README
        2. ELSE: Update README manually if feature is user-facing
        3. Update API docs if endpoints were added/changed
        4. Ensure complex logic has code comments
        5. Verify all feature doc artifacts are present in x-ipe-docs/features/{FEATURE-XXX}/
      </action>
      <constraints>
        - CRITICAL: All user-facing changes must be documented in README
      </constraints>
      <output>Updated project files</output>
    </step_3_1>

    <step_3_2>
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
        5. Store analysis result for inclusion in Output Summary (step_5_1)
      </action>
      <constraints>
        - CRITICAL: This is analysis only — do NOT execute any refactoring in this step
        - CRITICAL: The sub-agent should complete the full refactoring-analysis skill but stop at output (do NOT proceed to improve-code-quality or code-refactor)
        - NOTE: If analysis finds no actionable suggestions, record "no refactoring needed" and proceed
      </constraints>
      <output>Refactoring analysis result with quality score and suggestions</output>
    </step_3_2>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <step_4_1>
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
    </step_4_1>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <step_5_1>
      <name>Output Summary</name>
      <action>
        1. IF execution_mode == "workflow-mode":
           a. Run the workflow update script via bash (`python3 .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_update_action.py`) with:
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

          Completion gate (based on interaction_mode):
          IF process_preference.interaction_mode == "dao-represent-human-to-interact":
            → Auto-proceed after DoD verification, log refactoring recommendation via x-ipe-assistant-user-representative-Engineer
          ELSE (interact-with-human/dao-represent-human-to-interact-for-questions-in-skill):
            → Ask human to acknowledge summary
      </action>
      <output>Feature completion summary with refactoring recommendation delivered to human</output>
    </step_5_1>
  </phase_5>

  <phase_6 name="继续执行（Continue Execute）">
    <step_6_1>
      <name>Decide Next Action</name>
      <action>
        Collect the full context and task_completion_output from this skill execution.

        IF process_preference.interaction_mode == "dao-represent-human-to-interact":
          → Invoke x-ipe-assistant-user-representative-Engineer with:
            type: "routing"
            completed_skill_output: {full task_completion_output YAML from this skill}
            next_task_based_skill: "{from output}"
            context: "Skill completed. Study the context and full output to decide best next action."
          → DAO studies the complete context and decides the best next action
        ELSE (interact-with-human):
          → Present next task suggestion to human and wait for instruction
      </action>
      <constraints>
        - BLOCKING (manual): Human MUST confirm or redirect before proceeding
        - BLOCKING (auto): Proceed after DoD verification; auto-select next task via DAO
      </constraints>
      <output>Next action decided with execution context</output>
    </step_6_1>
    <step_6_2>
      <name>Execute Next Action</name>
      <action>
        Based on the decision from Step 6.1:
        1. Load the target task-based skill's SKILL.md
        2. Generate an execution plan from the skill's Execution Flow table
        3. Start execution from the skill's first phase/step
      </action>
      <constraints>
        - MUST load the skill before executing — do not skip skill loading
        - Execution follows the target skill's procedure, not this skill's
      </constraints>
      <output>Next task execution started</output>
    </step_6_2>
  </phase_6>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "Start next feature from backlog"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
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

| Pattern | When | Then |
|---------|------|------|
| All Criteria Met | Every AC passes | Review docs → update files → refactoring analysis → create PR → summary |
| Criteria Not Met | One or more AC fail | STOP → report to human with options (address/modify/defer) → wait for guidance |
| Minor Issues Found | Criteria met with minor fixable issues | Fix inline → re-verify → review docs → continue to PR (flag refactoring) |

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
