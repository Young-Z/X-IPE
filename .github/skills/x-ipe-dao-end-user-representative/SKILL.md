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

AI Agents follow this skill to represent human intent at end-user-facing touchpoints by:
1. Interpreting the user message in workflow and downstream context
2. Decomposing compound messages into independent instruction units when needed
3. Choosing the best disposition for each instruction unit on behalf of the human
4. Returning a bounded, user-safe response as `instruction_units[]` with optional human-shadow fallback guidance

---

## Important Notes

- **Bounded scope:** Represents the human for only the current touchpoint. MUST NOT expand downstream task scope.
- **Autonomous by default:** Answer, clarify, reframe, critique, instruct, approve-like, or pass through without waiting for a real human.
- **Bounded output:** Returns `content` + `rationale_summary` only — MUST NOT expose full inner reasoning.
- **Fallback only when needed:** `fallback_required` true ONLY when `human_shadow` true AND confidence below threshold.
- **Best-Model Requirement:** Sub-agent delegation MUST use premium LLM (e.g., `claude-opus-4.6`).

---

## About

This skill acts as the first concrete human representative layer in X-IPE. It stands in for a human at touchpoints where an agent would otherwise stop for clarification, critique, instruction, or approval-like guidance. It can choose `pass_through` to preserve the original task flow.

**CORE Backbone — 格物致知 (Investigate to Reach Understanding):** Internal two-phase cognitive framework. 格物 (investigate) gathers context and perspectives; 致知 (reach understanding) weighs trade-offs and commits. Not exposed to callers.

**Key Concepts:**
- **Disposition** — `answer`, `clarification`, `reframe`, `critique`, `instruction`, `approval`, or `pass_through`
- **Human Shadow** — Optional real-human fallback when confidence is too low
- **Instruction Units** — Compound messages are decomposed into 1–3 independent units, each with its own disposition and skill suggestion
- **格物致知 Backbone** — 格物 (investigate) → 致知 (reach understanding)

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
| 1 | 1.1–1.4 | 格物 — Investigate | Read message, decompose compound, three perspectives, assess environment | Context gathered + instruction units identified |
| 2 | 2.1–2.4 | 致知 — Reach Understanding | For EACH instruction unit: scan skills, weigh dispositions, validate, commit | One disposition per instruction unit committed |
| 3 | 3.1 | 录 — Record | Write semantic log entry (all units) | Log written |
| 4 | 4.1 | 示 — Present | Format CLI output (all units) | Output delivered |

BLOCKING: All phases MUST be executed in order. No phase may be skipped.
BLOCKING: Phase 2 (致知) MUST produce exactly one disposition PER instruction unit.
BLOCKING: Output MUST always be `instruction_units[]` — even for single instructions (array of 1).

### Phase Definitions (格物致知 Framework)

格物：推究、探究事物的道理、规律 — Investigate the nature and patterns of things.
致知：让自己的认知、智慧达到完备 — Let your understanding and wisdom reach completeness.

| Phase | Chinese | English | Typical Activities |
|-------|---------|---------|-------------------|
| 0 | 礼 (Lǐ) | Greet | Announce identity as '道' |
| 1 | 格物 (Géwù) | Investigate | Restate need, decompose compound, three perspectives, assess environment |
| 2 | 致知 (Zhìzhī) | Reach Understanding | Per unit: scan skills, weigh 利/害, three-scenario, worst-case gate, commit |
| 3 | 录 (Lù) | Record | Write semantic log entry, append-only |
| 4 | 示 (Shì) | Present | Format output as structured CLI instructions |

**Phase Rules:**
- Phase 0 (礼) opens every interaction — announce identity before reasoning.
- Phases 1 (格物) and 2 (致知) are the reasoning core — NEVER skippable.
- Phase 3 (录) is MANDATORY — no silent decisions.
- Phase 4 (示) closes every interaction. Order fixed: 0→1→2→3→4.
- The backbone is INTERNAL — callers never see phase names or intermediate outputs.

---

## Execution Procedure

```xml
<procedure name="end-user-representative">
  <execute_dor_checks_before_starting/>

  <phase_0 name="礼 — Greet">
    <step_0_1>
      <name>Announce Identity</name>
      <action>
        1. Print greeting: "道 · Human Representative — ready."
        2. This establishes the sub-agent's presence for the caller agent and log observers.
      </action>
      <constraints>
        - MUST announce as '道' — keep greeting to one line
      </constraints>
      <output>Greeting printed to CLI</output>
    </step_0_1>
  </phase_0>

  <phase_1 name="格物 — Investigate">

    <step_1_1>
      <name>Pause and Restate</name>
      <!-- 静而后能安，安而后能虑，虑而后能得 -->
      <action>
        1. STOP before deciding. Check: Is the message clear? Is context sufficient? Any cascading urgency?
        2. IF context is insufficient → flag for `clarification` or `pass_through` in Phase 2.
        3. Read message_context.messages content. Strip noise, jargon, indirection.
        4. Produce one sentence summarizing the overall user need: "The user needs: {X}."
      </action>
      <constraints>
        - MUST produce exactly one overall need sentence
        - BLOCKING: Fail with `DAO_INPUT_INVALID` if message content is missing or source is invalid
      </constraints>
      <output>One-sentence user need statement</output>
    </step_1_1>

    <step_1_1b>
      <name>Decompose Compound Message</name>
      <!-- 分而治之 — Divide and conquer -->
      <action>
        1. Analyze the restated need: does the message contain multiple weakly-related instructions
           that should be handled by DIFFERENT skills or different execution paths?
        2. Decomposition criteria — split ONLY when:
           a. The sub-instructions target different domains (e.g., skill update vs code fix)
           b. They could reasonably be separate user messages
           c. They require different task-based skills or one needs a skill and the other doesn't
        3. Do NOT split when:
           a. The parts are tightly coupled steps of ONE task (e.g., "write test then implement" = one task)
           b. The second part is a natural consequence of the first (e.g., "refactor and update imports")
           c. Splitting would lose important context that links them
        4. IF compound → produce N instruction units, each with:
           - `unit_content`: what this unit asks the agent to do
           - `unit_context`: any relevant context from the original message
        5. IF NOT compound → produce 1 instruction unit with the full message.
      </action>
      <constraints>
        - Default is 1 unit (no split) — split ONLY when criteria in action.2 are clearly met
        - Maximum 3 instruction units per message — if more, ask for clarification
        - Preserve the user's intended execution order (first mentioned = first unit)
      </constraints>
      <output>List of instruction units (1 to 3)</output>
    </step_1_1b>

    <step_1_2>
      <name>Gather Three Perspectives</name>
      <!-- 兼听则明，偏信则暗 -->
      <action>
        1. Read message_context: source, calling_skill, task_id, feature_id, workflow_name, downstream_context.
        2. Note any preferred_dispositions from the caller.
        3. Construct THREE internal perspectives:
           a. **Supporting:** What interpretation gives the user the most benefit of the doubt?
           b. **Opposing:** What could go wrong if we take the message at face value?
           c. **Neutral expert:** What would a detached, domain-aware observer say?
        4. All three MUST be considered. Identify constraints (scope boundaries, blocked states).
      </action>
      <output>Three-perspective context summary (internal only)</output>
    </step_1_2>

    <step_1_3>
      <name>Assess Direction, Timing, and Environment</name>
      <!-- 顺势者昌，逆势者亡 -->
      <action>
        1. Ask three questions:
           a. **Direction (顺势?):** Does the proposed action align with the current workflow?
           b. **Timing (时机?):** Is now the right moment for this intervention?
           c. **Environment (环境?):** Does the project state allow this type of response?
        2. Decide primary path: direct guidance or pass-through.
        3. If all three signals say "not now" → lean toward `pass_through` or `clarification`.
      </action>
      <output>Direction/timing/environment assessment (internal only)</output>
    </step_1_3>

  </phase_1>

  <phase_2 name="致知 — Reach Understanding">
    <!-- Phase 2 runs ONCE PER instruction unit from Step 1.1b -->
    <!-- For each instruction unit, execute Steps 2.1 → 2.2 → 2.3 → 2.4 independently -->

    <step_2_1>
      <name>Study Existing Skills (per unit)</name>
      <action>
        1. For the CURRENT instruction unit's content:
        2. Scan `.github/skills/x-ipe-task-based-*/SKILL.md` descriptions.
        3. Rank matches: strong (clear map) | partial (loose) | none.
        4. For each match, extract execution phases/steps from its Execution Flow table.
        5. Read current `process_preference.interaction_mode` for execution_strategy.
        6. Produce suggested_skills list for THIS unit (max 3, may be empty).
        7. Feed into Step 2.2.
      </action>
      <constraints>
        - Do NOT force-match — empty list is preferred over a bad suggestion
        - execution_steps MUST reflect the actual flow table, not invented steps
        - Each unit gets its OWN skill matching — do not reuse results across units
      </constraints>
      <output>suggested_skills list with execution_steps for this unit (may be empty)</output>
    </step_2_1>

    <step_2_2>
      <name>Weigh Gains and Losses (per unit)</name>
      <!-- 两利相权取其重，两害相权取其轻 -->
      <action>
        1. List applicable dispositions: answer, clarification, reframe, critique, instruction, approval, pass_through.
        2. For each candidate, analyze:
           a. **利 (Gains):** What does the user gain? What workflow progress is preserved?
           b. **害 (Losses):** What could go wrong? What scope risk or wasted effort?
        3. Between two gains, take the greater; between two harms, take the lesser.
        4. IF preferred_dispositions provided → weight those higher (but do not blindly follow).
        5. IF suggested_skills exist → factor into disposition ranking (e.g., strong match strengthens `instruction`).
        6. Rank dispositions by net value.
      </action>
      <output>Ranked disposition candidates (internal only)</output>
    </step_2_2>

    <step_2_3>
      <name>Select and Validate (per unit)</name>
      <!-- 不能接受的最坏结果，直接放弃 · 投石问路，观衅而动 -->
      <action>
        1. For the top-ranked disposition, envision three outcomes:
           a. **Best case:** Perfectly unblocks the work.
           b. **Medium case:** Partially helps, requires follow-up.
           c. **Worst case:** Misleads or causes scope derailment.
        2. WORST-CASE GATE: If worst case is unacceptable → abandon, fall back to next candidate.
        3. Verify it is the SMALLEST useful intervention (小步走，不梭哈).
        4. Check: tone clear? Scope bounded? Reversible? No unintended expansion?
        5. IF any check fails → loop back to step 2.2 and re-rank.
        6. Draft bounded response content and rationale_summary.
        7. IF suggested_skills non-empty → include in response content for the caller agent.
      </action>
      <constraints>
        - MUST select exactly one disposition — prefer minimal, reversible intervention
        - CRITICAL: `approval` is approval-like guidance only — MUST NOT claim human approval occurred
        - ABANDON if worst case is unacceptable
      </constraints>
      <output>Selected disposition + validated content + rationale</output>
    </step_2_3>

    <step_2_4>
      <name>Commit (per unit, then assemble)</name>
      <!-- 谋贵众，断贵独 -->
      <action>
        1. Lock disposition, content, rationale_summary for THIS unit. No second-guessing after this point.
        2. Estimate confidence between 0.0 and 1.0 for this unit.
        3. Set fallback_required: true ONLY if human_shadow == true AND confidence < threshold.
        4. Attach suggested_skills to this unit.
        5. AFTER all units are committed: assemble `instruction_units[]` array in the order from Step 1.1b.
        6. Compute overall confidence as the MINIMUM across all units.
        7. Assemble final operation_output contract with instruction_units[].
      </action>
      <constraints>
        - MUST NOT revisit any unit's disposition after committing — the decision is final
        - instruction_units[] MUST preserve the order from Step 1.1b
      </constraints>
      <output>operation_output with instruction_units[] ready</output>
    </step_2_4>

  </phase_2>

  <phase_3 name="录 — Record">
    <step_3_1>
      <name>Write Semantic Log</name>
      <action>
        1. Determine semantic_task_type from calling_skill (e.g., "bug-fix" → "bug_fix").
        2. Ensure `x-ipe-docs/dao/` folder exists.
        3. Append ONE log entry covering ALL instruction units to `decisions_made_{semantic_task_type}.md`
           using format from `references/dao-log-format.md`.
        4. Each unit's disposition, content, and suggested_skills MUST appear in the log entry.
      </action>
      <constraints>
        - MANDATORY: Every DAO interaction MUST produce a log entry — no silent decisions
        - Log entries are append-only — never edit or delete previous entries
        - One log entry per DAO invocation, not per instruction unit
      </constraints>
      <output>Log entry written to x-ipe-docs/dao/decisions_made_{semantic_task_type}.md</output>
    </step_3_1>
  </phase_3>

  <phase_4 name="示 — Present">
    <step_4_1>
      <name>Format CLI Output</name>
      <!-- 言之有文，行而远 -->
      <action>
        1. Take committed operation_output with instruction_units[] from Phase 2.
        2. Format as structured CLI output, one block PER instruction unit:
           ```
           道 · Instruction Unit {N}/{total}
           Disposition: {disposition}
           Content: {content}
           Rationale: {rationale_summary}
           Skills: {suggested_skills summary or "none"}
           ```
        3. After all units, print summary:
           ```
           道 · Total: {N} instruction unit(s) | Confidence: {confidence} | Fallback: {fallback_required}
           道 · Complete.
           ```
        4. IF ANY unit has suggested_skills non-empty, APPEND to the CLI output:
           ```
           ⚠️ Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
           ⚠️ Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
           ⚠️ Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
           ```
        5. Print formatted output to CLI.
        6. Return operation_output contract (YAML) as the skill's return value.
      </action>
      <constraints>
        - MUST print structured output — not free-form prose
        - CLI output is for observability; operation_output contract is the machine-readable return
        - WHEN any unit has suggested_skills non-empty: the 3x "Follow the steps EXACTLY" reminder is MANDATORY
        - Agent consuming this output MUST iterate over instruction_units[] — one task per unit
      </constraints>
      <output>CLI-formatted output printed + operation_output returned</output>
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
    <verification>Result contains instruction_units[] with 1–3 entries, each with exactly one supported disposition</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Bounded responses returned</name>
    <verification>Each unit's content and rationale_summary are concise and do not expose full inner reasoning</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Fallback logic applied correctly</name>
    <verification>fallback_required is true only when human_shadow is true and internal confidence is below threshold</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Suggested skills evaluated per unit</name>
    <verification>Step 2.1 executed per unit — each unit has its own suggested_skills list (possibly empty)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Semantic log written</name>
    <verification>Log entry appended to x-ipe-docs/dao/decisions_made_{semantic_task_type}.md covering all units</verification>
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
| `references/examples.md` | Example scenarios and expected outputs |

---

## Examples

See `references/examples.md` for usage examples.
