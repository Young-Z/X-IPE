---
name: x-ipe-task-based-general-purpose-executor
description: Execute tasks by following provided instructions with knowledge base guidance. Uses user manuals via x-ipe-tool-user-manual-referencer for step-by-step walkthroughs. Triggers on requests like "execute task", "follow instructions", "run steps", "general purpose", "execute goal", "accomplish task".
---

# Task-Based Skill: General Purpose Executor

## Purpose

Execute a goal by following provided instructions, using knowledge base references (especially user manuals) for guidance:
1. Parsing the goal and discrete execution steps from instructions
2. Loading and indexing the referenced knowledge base
3. Resolving ambiguous steps via `x-ipe-tool-user-manual-referencer` lookups
4. Executing each step with manual-guided precision
5. Escalating unresolvable issues to the human

---

## Important Notes

BLOCKING: Learn `x-ipe-workflow-task-execution` skill before executing this skill.

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

IMPORTANT: When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask the human. Instead, call `x-ipe-assistant-user-representative-Engineer` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue.

---

## Input Parameters

```yaml
input:
  # Task attributes (from task board)
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-general-purpose-executor"

  # Execution context (passed by x-ipe-workflow-task-execution)
  execution_mode: "free-mode | workflow-mode"  # default: free-mode
  workflow:
    name: "N/A"  # workflow name, default: N/A

  # Task type attributes
  category: "standalone"
  next_task_based_skill: null
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"

  # Required inputs
  goal: ""                    # What the executor should accomplish
  execution_instructions: ""  # Step-by-step or high-level instructions to follow
  execution_temperature: ""   # strict | balanced | creative (default: balanced, ask-user if not provided)
    # strict:   High bar for clarity. Confirm with human on ANY ambiguity in goal, instructions,
    #           or manual content. clarity_threshold = 0.8. No guessing or inference.
    # balanced: Standard clarity expectations. Ask human when moderately unclear.
    #           clarity_threshold = 0.6. Light inference allowed for trivial gaps.
    # creative: Tolerant of ambiguity. Only ask human when instructions are very unclear.
    #           clarity_threshold = 0.4. Infer reasonable defaults for minor gaps.

  # Knowledge base reference
  kb_reference:
    path: ""                  # Path to knowledge base folder (e.g., x-ipe-docs/knowledge-base/{app-name}/)
    manual_name: ""           # Name of the user manual to reference (e.g., "x-ipe-workflow-mode-user-manual")
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="x-ipe-tool-task-board-manager (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />
  <field name="goal" source="ask-user: 'What is the goal you want to accomplish?'" />
  <field name="execution_instructions" source="ask-user: 'What instructions should I follow?'" />
  <field name="execution_temperature" source="ask-user if not provided: 'What execution temperature? Strict (confirm every ambiguity), Balanced (standard, default), or Creative (tolerant of ambiguity)?'. Default: balanced.">
    <steps>
      1. Must be one of: strict, balanced, creative
      2. IF null or omitted → ask human with choices: [Balanced (Recommended), Strict, Creative]
      3. Resolve clarity_threshold: strict → 0.8, balanced → 0.6, creative → 0.4
      4. Pass clarity_threshold to x-ipe-tool-user-manual-referencer calls
    </steps>
  </field>
  <field name="kb_reference.manual_name" source="ask-user: 'Which user manual should I reference?'" />
  <field name="kb_reference.path" source="resolve from manual_name → x-ipe-docs/knowledge-base/{manual_name}/. If path not found, ask user." />
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Goal provided</name>
    <verification>Check that a clear goal statement exists in input</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Execution instructions provided</name>
    <verification>Check that execution_instructions contain actionable steps or high-level directions</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>KB reference path exists and is readable</name>
    <verification>Verify kb_reference.path points to an existing directory with readable content</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Task exists on task board</name>
    <verification>Confirm task_id is registered on the task board via x-ipe-tool-task-board-manager</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 0 | Create Task | Register task on board | Task ID assigned |
| 1.1 | Parse Goal & Instructions | Break instructions into discrete steps | Steps identified |
| 1.2 | Load Knowledge Base | Index KB structure and section map | KB indexed |
| 2.1 | Clarify Ambiguities | Resolve unclear steps via referencer or human | All steps clear |
| 5.1 | Execute Instructions | Run each step with manual guidance | Steps executed |
| 5.2 | Complete | Verify all steps, report results | Results reported |
| 5.3 | Update Task | Mark task done on board | Board updated |
| 6.1 | Decide Next Action | DAO-assisted next task decision | Next action decided |
| 6.2 | Execute Next Action | Load skill, generate plan, execute | Execution started |

BLOCKING: Step 2.1 must complete before Step 5.1 — do NOT execute with unresolved ambiguities.
BLOCKING: Step 5.1 must complete before Step 5.2 — do NOT report until all steps are attempted.

---

## Execution Procedure

```xml
<procedure name="general-purpose-executor">
  <!-- CRITICAL: Both DoR/DoD check elements below are MANDATORY -->
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_0>
    <name>Create Task on Board</name>
    <action>
      Call `x-ipe-tool-task-board-manager` → `task_create.py`:
      - task_type: "General Purpose Execution"
      - description: summarize goal and instructions from input context
      - status: "in_progress"
      - role: from input context
      - assignee: from input context
      Store returned task_id for later update.
    </action>
    <output>Task created on board with status in_progress</output>
  </step_0>

  <!-- Phase 1: 博学之 (Study Broadly) -->
  <phase_1 name="博学之（Study Broadly）">
    <step_1_1>
      <name>Parse Goal &amp; Instructions</name>
      <action>
        1. Read goal, execution_instructions, and execution_temperature from input
        2. Resolve clarity_threshold from execution_temperature:
           - strict → 0.8 | balanced → 0.6 | creative → 0.4
        3. Evaluate input clarity against clarity_threshold:
           - Rate goal clarity (0.0–1.0): is goal specific and measurable?
           - Rate instruction clarity (0.0–1.0): are steps actionable?
           - IF goal clarity &lt; clarity_threshold:
             Ask human: "Your goal '{goal}' is not specific enough. Can you clarify what 'done' looks like?"
           - IF instruction clarity &lt; clarity_threshold:
             Ask human: "The instructions are ambiguous. Can you provide more detail for: {vague_parts}?"
        4. Break execution_instructions into discrete, numbered steps
        5. For each step, classify:
           - "direct": can execute without external guidance
           - "manual-guided": references an app feature/UI/workflow needing manual lookup
        6. Produce an ordered step plan with classification tags
      </action>
      <output>clarity_threshold, ordered step plan with classification (direct vs manual-guided)</output>
    </step_1_1>

    <step_1_2>
      <name>Load Knowledge Base</name>
      <action>
        1. Verify kb_reference.path exists
        2. Read top-level structure: scan for .kb-index.json files
        3. Build a section map of available manual content (section titles → file paths)
        4. Log which manual sections are available for reference
      </action>
      <constraints>
        - BLOCKING: If kb_reference.path does not exist, ask human for correct path before proceeding
      </constraints>
      <output>Section map of KB content indexed and ready for lookup</output>
    </step_1_2>
  </phase_1>

  <!-- Phase 2: 审问之 (Inquire Thoroughly) -->
  <phase_2 name="审问之（Inquire Thoroughly）">
    <step_2_1>
      <name>Clarify Ambiguities</name>
      <action>
        For each step in the step plan:
        1. IF step is classified "manual-guided":
           → Call `x-ipe-tool-user-manual-referencer` with operation `lookup_instruction`:
             - query: the step's description
             - manual_name: kb_reference.manual_name
             - kb_path: kb_reference.path
             - clarity_threshold: {from step 1.1}
           → IF referencer returns clarity_score >= clarity_threshold:
             Attach returned instructions to the step (resolved)
           → IF referencer returns clarity_score &lt; clarity_threshold:
             Response source (based on interaction_mode):
             IF process_preference.interaction_mode == "dao-represent-human-to-interact":
               → Resolve via x-ipe-assistant-user-representative-Engineer
             ELSE:
               → Ask human: "The manual says '{instruction_text}' but it's unclear.
                 Can you clarify how to: {step description}?"
             Attach human/DAO clarification to the step
        2. IF step is classified "direct":
           → Verify step is self-contained and executable; if not, reclassify as "manual-guided"
        3. Collect all clarifications before proceeding
      </action>
      <constraints>
        - BLOCKING: ALL ambiguous steps must be resolved before Phase 5
        - CRITICAL: Do not guess or infer missing instructions; always consult manual or human
      </constraints>
      <output>Fully resolved step plan with all ambiguities clarified</output>
    </step_2_1>
  </phase_2>

  <!-- Phase 3: 慎思之 (Think Carefully) — SKIPPED -->
  <!-- Skip: "No design decisions; executor follows provided instructions" -->

  <!-- Phase 4: 明辨之 (Discern Clearly) — SKIPPED -->
  <!-- Skip: "Single valid approach; follow instructions sequentially" -->

  <!-- Phase 5: 笃行之 (Practice Earnestly) -->
  <phase_5 name="笃行之（Practice Earnestly）">
    <step_5_1>
      <name>Execute Instructions</name>
      <action>
        For each step in the resolved step plan (in order):
        1. IF execution_temperature == "strict":
           → Show human the step about to execute and ask: "Proceed with this step? [Yes/Skip/Modify]"
           → IF human modifies → use modified instructions
           → IF human skips → log as skipped and continue
        1. IF step requires user manual guidance (manual-guided):
           → Call `x-ipe-tool-user-manual-referencer` with operation `get_step_by_step`:
             - query: the step's description
             - manual_name: kb_reference.manual_name
             - kb_path: kb_reference.path
             - clarity_threshold: {from step 1.1}
           → IF manual instructions include screenshots:
             Use them as visual reference for UI actions
           → IF clarity_score &lt; clarity_threshold on returned steps:
             Ask human to clarify the unclear steps before executing
           → Follow the detailed walkthrough step by step
        2. Execute the step using the appropriate tool:
           - Web UI actions → Chrome DevTools tools (navigate, click, fill, snapshot)
           - CLI commands → bash tool
           - File operations → view/edit/create tools
           - API calls → bash with curl
        3. Verify expected outcome matches actual result
        4. IF outcome doesn't match expected:
           → Call `x-ipe-tool-user-manual-referencer` with operation `troubleshoot`:
             - issue: description of mismatch
             - step_context: current step details
             - clarity_threshold: {from step 1.1}
           → IF troubleshoot provides resolution: apply it and retry
           → IF troubleshoot doesn't help:
             IF execution_temperature == "creative":
               → Log mismatch, infer best-effort resolution, continue
             ELSE:
               Response source (based on interaction_mode):
               IF process_preference.interaction_mode == "dao-represent-human-to-interact":
                 → Resolve via x-ipe-assistant-user-representative-Engineer
               ELSE:
                 → Ask human for guidance
        5. Log step result:
           - status: success | failure | skipped
           - reason: (for failure/skipped) what went wrong or why skipped
           - manual_ref: (if used) which manual section was referenced
      </action>
      <constraints>
        - CRITICAL: For UI actions, always consult the manual first; do NOT guess button locations
        - CRITICAL: Do not proceed past a failed step that blocks subsequent steps
        - CRITICAL: Log every step result regardless of outcome
      </constraints>
      <output>Step-by-step execution log with results per step</output>
    </step_5_1>

    <step_5_2>
      <name>Complete</name>
      <action>
        1. Verify all instruction steps have been attempted
        2. Count: steps_total, steps_completed, steps_failed
        3. Compile step_results list and manual_references_used list
        4. Determine overall status:
           - IF all steps completed → status: "completed"
           - IF any step failed and unresolved → status: "blocked"
        5. Generate task_completion_output
      </action>
      <output>Execution summary with overall status and step results</output>
    </step_5_2>

    <step_5_3>
      <name>Update Task on Board</name>
      <action>
        Call `x-ipe-tool-task-board-manager` → `task_update.py`:
        - task_id: from Step 0
        - status: "done"
        - output_links: list of deliverables produced (if any)
      </action>
      <output>Task marked done on board</output>
    </step_5_3>
  </phase_5>

  <!-- Phase 6: 继续执行 (Continue Execute) -->
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
          → Present execution summary to human and wait for instruction
      </action>
      <constraints>
        - BLOCKING (interact-with-human): Human MUST confirm or redirect before proceeding
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
  category: "standalone"
  status: completed | blocked
  next_task_based_skill: null
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links: []
  # Dynamic attributes
  goal: "{from input}"
  steps_total: 0
  steps_completed: 0
  steps_failed: 0
  step_results: []
  manual_references_used: []
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>All instruction steps attempted</name>
    <verification>Confirm every step in the resolved plan was executed or explicitly skipped with reason</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Results logged per step</name>
    <verification>Verify step_results contains an entry for each step with status and reason</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Unresolvable issues escalated to human</name>
    <verification>Confirm any failed step that could not be resolved via manual or troubleshooting was escalated</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Task completion output generated</name>
    <verification>Verify task_completion_output contains accurate counts and status</verification>
  </checkpoint>
</definition_of_done>
```

MANDATORY: After completing this skill, return to `x-ipe-workflow-task-execution` to continue the task execution flow.

---

## Patterns & Anti-Patterns

### Pattern: Manual-Guided Execution

**When:** A step says "do X in the app" without specific instructions
**Then:**
```
1. Call x-ipe-tool-user-manual-referencer with operation lookup_instruction
2. Get exact click-by-click instructions from user manual
3. Follow the manual walkthrough using Chrome DevTools or appropriate tool
4. Verify outcome matches expected result from manual
```

### Pattern: Progressive Clarification

**When:** Manual instructions have low clarity score
**Then:**
```
1. Call referencer → get instructions with clarity_score
2. IF clarity_score < 0.6 → ask human for clarification
3. Attach clarification to step before executing
4. Never proceed with ambiguous instructions
```

### Pattern: Troubleshoot-Then-Escalate

**When:** A step's outcome doesn't match expected result
**Then:**
```
1. Call referencer with troubleshoot operation
2. IF troubleshoot provides resolution → apply and retry
3. IF troubleshoot fails → escalate to human
4. Log failure reason regardless of resolution path
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Guessing UI interactions | Wrong clicks waste time, may corrupt state | Always consult the manual first |
| Ignoring unclear instructions | Leads to wrong execution and wasted effort | Ask human when clarity_score < 0.6 |
| Skipping step logging | Cannot diagnose failures or report progress | Log every step result |
| Executing without KB load | No reference material for manual-guided steps | Always load KB in Phase 1 |
| Proceeding past blocking failure | Downstream steps depend on prior outcomes | Stop and escalate |

---

## Examples

See [references/examples.md](x-ipe-docs/skill-meta/x-ipe-task-based-general-purpose-executor/candidate/references/examples.md) for concrete execution examples.
