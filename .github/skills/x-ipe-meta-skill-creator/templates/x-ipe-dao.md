# Human Representative Skill Template

Use this template for skills (type: `x-ipe-dao`) that act as human representatives at human-required touchpoints while preserving bounded outputs and optional human-shadow fallback. The 道 (DAO) backbone is the CORE internal reasoning methodology for all skills of this type.

**Section Order (Cognitive Flow):**
1. CONTEXT: Purpose → Important Notes → About → When to Use
2. DECISION: Input Parameters → Definition of Ready
3. ACTION: Execution Flow → Execution Procedure
4. VERIFY: Output Result → Definition of Done
5. REFERENCE: Error Handling → Future Extensions → References → Examples

---

```markdown
---
name: x-ipe-dao-{name}
description: {What human-required touchpoints this skill represents, using universally understood language}. Use when {trigger conditions}. Triggers on requests like "{trigger 1}", "{trigger 2}".
---

# {Skill Name — Human Representative Skill}

## Purpose

AI Agents follow this skill to represent human intent at human-required touchpoints by:
1. {Objective 1}
2. {Objective 2}
3. {Objective 3}

---

## Important Notes

BLOCKING: {Critical mediation rule — use common language, avoid "DAO" terminology in external surfaces}
CRITICAL: {Bounded-output or safety rule}
CRITICAL: {Fallback rule}

---

## About

{Explain the skill's mediation role and boundaries using universally understood language}

**CORE Backbone — 道 (DAO):** This skill's internal reasoning follows the 道 decision methodology — a structured 7-step cognitive backbone rooted in Chinese philosophical tradition. The backbone shapes how the skill evaluates context and selects dispositions, but it is not exposed to callers.

**Key Concepts:**
- **Disposition** — {How the skill chooses its response posture}
- **Bounded Output** — {What can be returned without exposing chain-of-thought}
- **Human Shadow** — {Optional real-human fallback behavior}

---

## When to Use

```yaml
triggers:
  - "{trigger phrase 1 — use common language}"
  - "{trigger phrase 2 — use common language}"

not_for:
  - "{out of scope case}"
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
    downstream_context: "{target agent/task context or N/A}"
    messages:
      - content: "{raw user message}"
        preferred_dispositions: [...]        # Optional
  human_shadow: false                        # Standalone, default: false
```

### Input Initialization

```xml
<input_init>
  <field name="message_context.source" source="Caller specifies message origin">
    <validation>MUST be `human` or `ai`. FAIL FAST if missing.</validation>
  </field>

  <field name="message_context.messages" source="Caller provides messages to process">
    <validation>MUST be non-empty array with non-empty `content` in each entry.</validation>
  </field>

  <field name="human_shadow">
    <steps>
      1. IF caller provided a boolean → use it.
      2. ELSE default to false.
    </steps>
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

| Phase | Step | Name (道) | Action | Gate |
|-------|------|-----------|--------|------|
| 1 | 1.1 | 静虑 — Pause & Restate | Pause and restate the real user need in one sentence | Need is clear in one sentence |
| 2 | 2.1 | 兼听 — Listen Broadly | Consider user intent, workflow state, downstream constraints, caller preference hints | All context factors weighed |
| 3 | 3.1 | 审势 — Assess the Situation | Assess whether direct guidance or pass-through best preserves the workflow | Guidance vs pass-through decided |
| 4 | 4.1 | 权衡 — Weigh Trade-offs | Compare supported dispositions against user value, scope safety, and confidence | Candidate dispositions ranked |
| 5 | 5.1 | 谋后而定 — Plan Then Decide | Choose the smallest useful intervention that unblocks the work | One disposition selected |
| 6 | 6.1 | 试错 — Sanity Check | Sanity-check proposed response for tone, clarity, and unintended scope changes | Response validated |
| 7 | 7.1 | 断 — Commit | Commit to one disposition and one bounded response | Final output ready |
| 8 | 8.1 | 录 — Record | Write semantic log entry to x-ipe-docs/dao/ | Log entry written |

BLOCKING: All 8 phases MUST be executed in order. No phase may be skipped.
BLOCKING: Phase 7 (断) MUST produce exactly one disposition — not multiple.

### Phase Definitions (道 Seven-Step Backbone + Record)

| Phase | Chinese | English | Purpose | Typical Activities |
|-------|---------|---------|---------|-------------------|
| 1 | 静虑 (Jìnglǜ) | Pause & Restate | Ground the interaction | Strip noise, restate what the user actually needs |
| 2 | 兼听 (Jiāntīng) | Listen Broadly | Gather all signal | Read intent, workflow state, constraints, caller hints |
| 3 | 审势 (Shěnshì) | Assess the Situation | Evaluate the landscape | Direct guidance vs pass-through, risk assessment |
| 4 | 权衡 (Quánhéng) | Weigh Trade-offs | Compare options | Score dispositions on value, safety, confidence |
| 5 | 谋后而定 (Móuhòu'érdìng) | Plan Then Decide | Select intervention | Smallest useful action that unblocks work |
| 6 | 试错 (Shìcuò) | Sanity Check | Validate before commit | Check tone, clarity, scope safety of draft response |
| 7 | 断 (Duàn) | Commit | Finalize output | Lock disposition, content, rationale, confidence |
| 8 | 录 (Lù) | Record | Persist the decision | Write semantic log entry |

**Phase Rules:**
- All 7 reasoning phases (静虑 through 断) are NEVER skippable.
- Phase 8 (录) is MANDATORY for every interaction — no silent decisions.
- Phase order is fixed: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8. No reordering.
- The backbone is INTERNAL — callers never see phase names or intermediate outputs.

---

## Execution Procedure

```xml
<procedure name="{skill-name}">
  <execute_dor_checks_before_starting/>

  <phase_1 name="静虑 — Pause & Restate">
    <step_1_1>
      <name>Restate the User Need</name>
      <action>
        1. Read message_context.messages content.
        2. Strip noise, jargon, and indirection.
        3. Produce a single clear sentence: "The user needs: {X}."
      </action>
      <constraints>
        - MUST produce exactly one sentence
        - MUST NOT interpret beyond what the message says
      </constraints>
      <output>One-sentence user need statement</output>
    </step_1_1>
  </phase_1>

  <phase_2 name="兼听 — Listen Broadly">
    <step_2_1>
      <name>Gather All Context Signals</name>
      <action>
        1. Read message_context: source, calling_skill, task_id, feature_id, workflow_name, downstream_context.
        2. Note any preferred_dispositions from the caller.
        3. Consider what the downstream agent/skill is currently doing.
        4. Identify any constraints (scope boundaries, blocked states, pending decisions).
      </action>
      <output>Context signal summary (internal only)</output>
    </step_2_1>
  </phase_2>

  <phase_3 name="审势 — Assess the Situation">
    <step_3_1>
      <name>Direct Guidance vs Pass-Through</name>
      <action>
        1. Evaluate: can this skill answer directly and safely?
        2. Evaluate: would the downstream agent provide a better answer?
        3. Assess risk of direct guidance: scope creep, incorrect assumptions, missing context.
        4. Decide the primary path: direct guidance or pass-through.
      </action>
      <output>Primary path decision (internal only)</output>
    </step_3_1>
  </phase_3>

  <phase_4 name="权衡 — Weigh Trade-offs">
    <step_4_1>
      <name>Score Candidate Dispositions</name>
      <action>
        1. List applicable dispositions: answer, clarification, reframe, critique, instruction, approval, pass_through.
        2. Score each against: user value, scope safety, confidence level.
        3. IF preferred_dispositions provided → weight those higher (but do not blindly follow).
        4. Rank dispositions by composite score.
      </action>
      <output>Ranked disposition candidates (internal only)</output>
    </step_4_1>
  </phase_4>

  <phase_5 name="谋后而定 — Plan Then Decide">
    <step_5_1>
      <name>Select Smallest Useful Intervention</name>
      <action>
        1. From ranked candidates, select the top disposition.
        2. Verify it is the SMALLEST useful intervention — prefer pass_through over answer when downstream can handle it.
        3. Draft the bounded response content.
        4. Draft the rationale_summary (one sentence).
      </action>
      <constraints>
        - MUST select exactly one disposition
        - MUST prefer minimal intervention
      </constraints>
      <output>Selected disposition + draft content + draft rationale</output>
    </step_5_1>
  </phase_5>

  <phase_6 name="试错 — Sanity Check">
    <step_6_1>
      <name>Validate Response Before Commit</name>
      <action>
        1. Check tone: is the response respectful and clear?
        2. Check clarity: would the caller understand what to do next?
        3. Check scope: does the response introduce unintended scope changes?
        4. Check boundaries: does the response stay within this skill's bounded role?
        5. IF any check fails → return to Phase 5 and adjust.
      </action>
      <constraints>
        - MUST NOT pass a response that expands downstream task scope
        - MUST NOT claim human approval occurred (approval = approval-like guidance)
      </constraints>
      <output>Validated response (or loop back to Phase 5)</output>
    </step_6_1>
  </phase_6>

  <phase_7 name="断 — Commit">
    <step_7_1>
      <name>Finalize Output</name>
      <action>
        1. Lock disposition, content, rationale_summary.
        2. Estimate confidence between 0.0 and 1.0.
        3. Set fallback_required:
           - true ONLY if human_shadow == true AND confidence < internal threshold.
           - false otherwise.
        4. Assemble operation_output contract.
      </action>
      <output>operation_output ready for return</output>
    </step_7_1>
  </phase_7>

  <phase_8 name="录 — Record">
    <step_8_1>
      <name>Write Semantic Log</name>
      <action>
        1. DETERMINE semantic_task_type from calling_skill.
        2. CHECK if x-ipe-docs/dao/ folder exists; create if not.
        3. DETERMINE target log file: decisions_made_{semantic_task_type}.md.
        4. DETERMINE next Entry ID (DAO-{N+1}).
        5. APPEND registry table row and detail section.
      </action>
      <constraints>
        - MANDATORY: Every interaction MUST produce a log entry — no silent decisions
        - Log entries are append-only — never edit or delete previous entries
      </constraints>
      <output>Log entry written to x-ipe-docs/dao/decisions_made_{semantic_task_type}.md</output>
    </step_8_1>
  </phase_8>

</procedure>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    disposition: "answer | clarification | reframe | critique | instruction | approval | pass_through"
    content: "bounded response"
    rationale_summary: "brief explanation"
    confidence: 0.0
    fallback_required: false
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Disposition Selected</name>
    <verification>A supported disposition is returned</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Bounded Output Returned</name>
    <verification>No full inner reasoning is exposed</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Semantic Log Written</name>
    <verification>Log entry appended to x-ipe-docs/dao/decisions_made_{semantic_task_type}.md</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `{ERROR_CODE}` | {Cause} | {Resolution} |

---

## Future Extensions

> Reserved for later versions. Do not implement persistence or recall in v1.

- **Reusable Memory:** A future version may add cross-task experience recall. The output contract already supports adding fields (backward-compatible).

---

## References

| File | Purpose |
|------|---------|
| `references/{file}.md` | {Reference guidance} |

---

## Examples

See `.github/skills/x-ipe-dao-{name}/references/examples.md` for usage examples.
```
