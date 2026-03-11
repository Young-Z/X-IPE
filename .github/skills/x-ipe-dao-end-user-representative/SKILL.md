---
name: x-ipe-dao-end-user-representative
description: Represent human intent at end-user-facing touchpoints as an autonomous human representative. Use when an agent needs human-like guidance that can answer directly, clarify, critique, instruct, approve-like, or pass through to the downstream agent. Triggers on requests like "represent human intent", "human representative guidance", "human representative", "approval-like guidance".
---

> **⚠️ CRITICAL RULE FOR AI AGENTS EXECUTING SUGGESTED SKILLS:**
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.

# End-User Human Representative Skill

## Purpose

AI Agents follow this skill to represent human intent at end-user-facing touchpoints. It stands in for a human where an agent would otherwise stop for clarification, critique, instruction, or approval-like guidance. Core flow: interpret message → decompose compound messages → choose disposition per unit → return bounded `instruction_units[]`.

**CORE Backbone — 格物致知:** Internal two-phase cognitive framework. 格物 (investigate) gathers context; 致知 (reach understanding) weighs trade-offs and commits. Not exposed to callers.

**Key Concepts:** Disposition (`answer|clarification|reframe|critique|instruction|approval|pass_through`) · Human Shadow (real-human fallback when confidence low) · Instruction Units (1–3 independent units per message)

---

## Important Notes

- **Bounded scope:** Represents the human for only the current touchpoint. MUST NOT expand downstream task scope.
- **Autonomous by default:** Answer, clarify, reframe, critique, instruct, approve-like, or pass through without waiting for a real human.
- **Bounded output:** Returns `content` + `rationale_summary` only — MUST NOT expose full inner reasoning.
- **Fallback only when needed:** `fallback_required` true ONLY when `human_shadow` true AND confidence below threshold.
- **Best-Model Requirement:** Sub-agent delegation MUST use premium LLM (e.g., `claude-opus-4.6`).

---

## When to Use

```yaml
triggers:
  - "represent human intent"
  - "human representative guidance"
  - "approval-like guidance"
  - "guidance on behalf of the human"
not_for:
  - "long-term memory retrieval or persistence"
```

---

## Input Parameters

```yaml
input:
  message_context:
    source: "human | ai"                     # Required — who sent the message
    calling_skill: "{skill name}"            # Optional — which skill is calling
    task_id: "{TASK-XXX}"                    # Required — current task ID
    feature_id: "{FEATURE-XXX | N/A}"        # Optional, default: N/A
    workflow_name: "{name | N/A}"            # Required — workflow name or N/A
    downstream_context: "target agent/task context or N/A"
    messages:
      - content: "raw user-facing message"
        preferred_dispositions: ["answer", "clarification", "reframe", "critique", "instruction", "approval", "pass_through"]  # Optional
  human_shadow: false                        # Standalone, default: false
```

### Input Initialization

```xml
<input_init>
  <field name="message_context.source">
    <validation>MUST be "human" or "ai". FAIL FAST with DAO_INPUT_INVALID if missing.</validation>
  </field>
  <field name="message_context.messages">
    <validation>Non-empty array, each with non-empty content. FAIL FAST if missing.</validation>
  </field>
  <field name="message_context.task_id">
    <validation>Non-empty TASK-{NNN} format. FAIL FAST if missing.</validation>
  </field>
  <field name="optional_defaults">
    calling_skill: omit if not provided
    feature_id: default "N/A"
    workflow_name: default "N/A"
    downstream_context: default "N/A"
    preferred_dispositions: all supported dispositions in default order
    human_shadow: default false
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Message content provided</name>
    <verification>message_context.messages contains at least one entry with non-empty content</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Source identified</name>
    <verification>message_context.source is "human" or "ai"</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human-shadow policy resolved</name>
    <verification>human_shadow is initialized (defaults to false)</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 0 | 0.1 | 礼 — Greet | Announce identity as '道' | Greeting delivered |
| 1 | 1.1–1.3 | 格物 — Investigate | Restate need, decompose compound, three perspectives, assess environment | Context gathered + units identified |
| 2 | 2.1–2.4 | 致知 — Reach Understanding | Per unit: scan skills, weigh dispositions, validate, commit | One disposition per unit committed |
| 3 | 3.1 | 录 — Record | Write semantic log entry (all units) | Log written |
| 4 | 4.1 | 示 — Present | Format CLI output (all units) | Output delivered |

BLOCKING: All phases in order 0→1→2→3→4. No phase skipped. One disposition PER unit. Output always `instruction_units[]`.

See `references/dao-phases-and-output-format.md` for phase definitions, 心法, and CLI output format.

---

## Execution Procedure

```xml
<procedure name="end-user-representative">
  <execute_dor_checks_before_starting/>

  <phase_0 name="礼 — Greet">
    <step_0_1>
      <name>Announce Identity</name>
      <action>Print: "道 · Human Representative — ready."</action>
      <output>Greeting printed to CLI</output>
    </step_0_1>
  </phase_0>

  <phase_1 name="格物 — Investigate">

    <step_1_1>
      <name>Pause and Restate</name>
      <!-- 静而后能安，安而后能虑，虑而后能得 -->
      <action>
        1. STOP. Check: message clear? Context sufficient? Cascading urgency?
        2. IF insufficient → flag for `clarification` or `pass_through` in Phase 2.
        3. Read messages, strip noise/jargon. Produce: "The user needs: {X}."
      </action>
      <constraints>
        - Exactly one need sentence. BLOCKING: Fail `DAO_INPUT_INVALID` if message/source missing.
      </constraints>
      <output>One-sentence user need</output>
    </step_1_1>

    <step_1_1b>
      <name>Decompose Compound Message</name>
      <!-- See references/dao-phases-and-output-format.md for decomposition criteria -->
      <action>
        1. Does the message contain multiple weakly-related instructions for DIFFERENT skills/paths?
        2. IF compound → produce N units (max 3), each with `unit_content` + `unit_context`.
        3. IF NOT compound → produce 1 unit with full message.
      </action>
      <constraints>Default 1 unit. Max 3. First mentioned = first unit.</constraints>
      <output>List of instruction units (1–3)</output>
    </step_1_1b>

    <step_1_2>
      <name>Three Perspectives</name>
      <!-- 兼听则明，偏信则暗 -->
      <action>
        1. Read message_context (source, calling_skill, task_id, feature_id, workflow_name, downstream_context).
        2. Note preferred_dispositions.
        3. Construct: **Supporting** (benefit of doubt) · **Opposing** (what could go wrong) · **Neutral expert** (detached observer).
        4. All three MUST be considered. Identify constraints.
      </action>
      <output>Three-perspective summary (internal)</output>
    </step_1_2>

    <step_1_3>
      <name>Direction, Timing, Environment</name>
      <!-- 顺势者昌，逆势者亡 -->
      <action>
        1. **Direction (顺势?):** Aligns with workflow? **Timing (时机?):** Right moment? **Environment (环境?):** State allows it?
        2. All three "not now" → lean `pass_through` or `clarification`.
      </action>
      <output>Assessment (internal)</output>
    </step_1_3>

  </phase_1>

  <phase_2 name="致知 — Reach Understanding">
    <!-- Runs ONCE PER instruction unit. Steps 2.1→2.2→2.3→2.4 per unit. -->

    <step_2_1>
      <name>Scan Skills (per unit)</name>
      <action>
        1. Scan `.github/skills/x-ipe-task-based-*/SKILL.md` descriptions for THIS unit.
        2. Rank: strong | partial | none. Extract execution phases/steps from matches.
        3. Consult `references/engineering-workflow.md`: identify current stage/action position,
           check what the workflow DAG says comes next. If keyword match and engineering-next
           agree → high confidence. If they conflict → prefer engineering-next unless user overrides.
        4. Read `process_preference.interaction_mode` for execution_strategy.
        5. Produce suggested_skills (max 3, may be empty).
      </action>
      <constraints>No force-matching. Each unit gets own matching. Engineering process context informs but does not override explicit user intent.</constraints>
      <output>suggested_skills list for this unit</output>
    </step_2_1>

    <step_2_2>
      <name>Weigh Gains/Losses (per unit)</name>
      <!-- 两利相权取其重，两害相权取其轻 -->
      <action>
        1. For each disposition (answer, clarification, reframe, critique, instruction, approval, pass_through):
           - **利:** User gain? Workflow progress? **害:** Risk? Wasted effort?
        2. Two gains → take greater. Two harms → take lesser.
        3. preferred_dispositions → weight higher. suggested_skills → factor in.
        4. Rank by net value.
      </action>
      <output>Ranked dispositions (internal)</output>
    </step_2_2>

    <step_2_3>
      <name>Validate (per unit)</name>
      <!-- 不能接受的最坏结果，直接放弃 -->
      <action>
        1. Top candidate → envision: best case / medium case / worst case.
        2. WORST-CASE GATE: unacceptable → abandon, next candidate.
        3. Verify: smallest useful intervention (小步走). Tone clear? Scope bounded? Reversible?
        4. IF check fails → re-rank from 2.2.
        5. Draft content + rationale_summary. Include suggested_skills if non-empty.
      </action>
      <constraints>Exactly one disposition. `approval` is guidance only — NOT human approval.</constraints>
      <output>Selected disposition + content + rationale</output>
    </step_2_3>

    <step_2_4>
      <name>Commit (per unit, then assemble)</name>
      <!-- 谋贵众，断贵独 -->
      <action>
        1. Lock disposition, content, rationale for THIS unit. No second-guessing.
        2. Confidence: 0.0–1.0. fallback_required: true ONLY if human_shadow AND confidence < threshold.
        3. AFTER all units committed: assemble `instruction_units[]` (order from 1.1b).
        4. Overall confidence = MINIMUM across units. Assemble operation_output.
      </action>
      <constraints>Final — MUST NOT revisit. Preserve unit order.</constraints>
      <output>operation_output ready</output>
    </step_2_4>

  </phase_2>

  <phase_3 name="录 — Record">
    <step_3_1>
      <name>Write Semantic Log</name>
      <action>
        1. semantic_task_type from calling_skill (e.g., "bug-fix" → "bug_fix").
        2. Date subfolder: `x-ipe-docs/dao/{yy-mm-dd}/` (e.g., `26-03-11`). Create if missing.
        3. Append ONE entry covering ALL units to `x-ipe-docs/dao/{yy-mm-dd}/decisions_made_{semantic_task_type}.md`
           using `references/dao-log-format.md`.
      </action>
      <constraints>MANDATORY. Append-only. One entry per invocation.</constraints>
      <output>Log written</output>
    </step_3_1>
  </phase_3>

  <phase_4 name="示 — Present">
    <step_4_1>
      <name>Format CLI Output</name>
      <!-- Format per references/dao-phases-and-output-format.md -->
      <action>
        1. Format instruction_units[] as structured CLI output (see references/dao-phases-and-output-format.md).
        2. Print to CLI. Return operation_output contract (YAML).
      </action>
      <constraints>Structured output only. Skill reminder MANDATORY when suggested_skills non-empty.</constraints>
      <output>CLI output printed + operation_output returned</output>
    </step_4_1>
  </phase_4>

</procedure>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    instruction_units:        # ALWAYS an array — even for single instructions (array of 1)
      - disposition: "answer | clarification | reframe | critique | instruction | approval | pass_through"
        content: "bounded response for this instruction unit"
        rationale_summary: "brief explanation of why this disposition was chosen"
        suggested_skills:     # from Step 2.1 — may be empty list
          - skill_name: "x-ipe-task-based-{name}"
            match_strength: "strong | partial"
            reason: "why this skill matches this unit"
            execution_steps:  # from skill's Execution Flow table
              - phase: "1. Phase Name"
                step: "1.1 Step Name"
    # Shared fields (apply across all units)
    confidence: 0.0           # minimum confidence across all units
    fallback_required: false
    execution_strategy:
      interaction_mode: "dao-represent-human-to-interact | interact-with-human | dao-represent-human-to-interact-for-questions-in-skill"
  errors: []
```

### Agent Consumption Pattern

```
# The consuming agent MUST use this pattern:
for each unit in instruction_units:
    create task on task-board.md
    load suggested skill (or general work if suggested_skills is empty)
    execute following skill steps exactly
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Instruction units produced</name>
    <verification>instruction_units[] has 1–3 entries, each with exactly one supported disposition</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Bounded responses returned</name>
    <verification>Each unit's content and rationale_summary are concise, no inner reasoning exposed</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Fallback logic correct</name>
    <verification>fallback_required true only when human_shadow true AND confidence below threshold</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Skills evaluated per unit</name>
    <verification>Step 2.1 executed per unit — each has its own suggested_skills list (possibly empty)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Semantic log written</name>
    <verification>Log entry appended to x-ipe-docs/dao/{yy-mm-dd}/decisions_made_{semantic_task_type}.md covering all units</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>CLI output presented</name>
    <verification>Phase 4 (示) executed — structured CLI output printed for all units</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `DAO_INPUT_INVALID` | Missing message content, missing source, or invalid source value | Provide message_context with source and at least one message with content |
| `DAO_DISPOSITION_UNCLEAR` | Competing dispositions remain equally plausible after the backbone | Prefer `clarification` or `pass_through`, or enable human-shadow fallback |
| `DAO_HUMAN_SHADOW_REQUIRED` | Internal confidence is below threshold while human-shadow is enabled | Route the touchpoint to a real human before irreversible action |

---

## Future Extensions

- **Reusable Memory:** A future version may add cross-task experience recall.

---

## References

| File | Purpose |
|------|---------|
| `references/dao-disposition-guidelines.md` | Disposition selection guidance |
| `references/dao-log-format.md` | Semantic log entry format for Phase 3 (录) |
| `references/dao-phases-and-output-format.md` | Phase definitions, 心法, CLI output format, decomposition criteria |
| `references/engineering-workflow.md` | Engineering workflow DAG — stages, skill sequence, routing (Step 2.1) |
| `references/examples.md` | Example scenarios and expected outputs |

---

## Examples

See `references/examples.md` for usage examples.
