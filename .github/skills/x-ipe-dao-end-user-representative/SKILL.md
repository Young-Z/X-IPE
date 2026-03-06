---
name: x-ipe-dao-end-user-representative
description: Represent human intent at end-user-facing touchpoints as an autonomous human representative. Use when an agent needs human-like guidance that can answer directly, clarify, critique, instruct, approve-like, or pass through to the downstream agent. Triggers on requests like "represent human intent", "human representative guidance", "human representative", "approval-like guidance".
---

# End-User Human Representative Skill

## Purpose

AI Agents follow this skill to represent human intent at end-user-facing touchpoints by:
1. Interpreting the user message in workflow and downstream context
2. Choosing the best disposition for the interaction on behalf of the human
3. Returning a bounded, user-safe response with optional human-shadow fallback guidance

---

## Important Notes

BLOCKING: This skill represents the human for only the current end-user touchpoint. It MUST NOT silently expand downstream task scope or rewrite requirements beyond the current interaction.

CRITICAL: This skill is autonomous by default. It should answer, clarify, reframe, critique, instruct, provide approval-like guidance, or pass through without waiting for a real human unless human-shadow fallback is required.

CRITICAL: Output must stay bounded. The skill may return `content` and a brief `rationale_summary`, but it must not expose full inner reasoning.

CRITICAL: `fallback_required` is true ONLY when `human_shadow` is true AND the skill's internal confidence assessment is below its own threshold.

CRITICAL: Semantic decision logging, legacy decision-log migration, and persistent memory are out of scope for this v1 skill.

---

## About

This skill acts as the first concrete human representative layer in X-IPE. It stands in for a human at specific touchpoints where an agent would otherwise stop for clarification, framing, critique, instruction, or approval-like guidance. The skill does not replace the downstream worker agent; when the best outcome is to let the downstream agent answer directly, it can choose `pass_through` and preserve the original task flow.

**CORE Backbone — 道 (DAO):** This skill's internal reasoning follows the 道 decision methodology — a structured 7-step cognitive backbone rooted in Chinese philosophical tradition. The backbone shapes how the skill evaluates context and selects dispositions, but it is not exposed to callers. Callers interact only with the bounded input/output contract.

**Key Concepts:**
- **Disposition** — The posture the skill chooses for the current touchpoint: `answer`, `clarification`, `reframe`, `critique`, `instruction`, `approval`, or `pass_through`
- **Bounded Output** — A compact response contract that helps the caller act without revealing chain-of-thought
- **Human Shadow** — An optional real-human fallback used only when the caller enabled it and confidence is too low
- **Downstream Context** — Information about the active feature, workflow, or worker agent that may make `pass_through` the right disposition
- **Seven-Step Backbone (道)** — The internal decision rhythm: 静虑, 兼听, 审势, 权衡, 谋后而定, 试错, 断

---

## When to Use

```yaml
triggers:
  - "represent human intent"
  - "human representative guidance"
  - "human representative"
  - "approval-like guidance"
  - "should the downstream agent answer this"
  - "guidance on behalf of the human"

not_for:
  - "semantic logging rollout — use FEATURE-047-B follow-up work"
  - "instruction-resource interception rollout — use FEATURE-047-C follow-up work"
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
  <field name="message_context.source" source="Caller specifies the message origin">
    <validation>MUST be `human` or `ai`. FAIL FAST with `DAO_INPUT_INVALID` if missing.</validation>
  </field>

  <field name="message_context.messages" source="Caller provides the message(s) to process">
    <validation>MUST be non-empty array. Each message MUST have non-empty `content`. FAIL FAST with `DAO_INPUT_INVALID` if missing.</validation>
  </field>

  <field name="message_context.calling_skill">
    <steps>
      1. IF caller provides skill name → use it.
      2. ELSE omit (optional).
    </steps>
  </field>

  <field name="message_context.task_id" source="Caller provides current task ID">
    <validation>MUST be non-empty string matching TASK-{NNN} format. FAIL FAST if missing.</validation>
  </field>

  <field name="message_context.feature_id">
    <steps>
      1. IF caller provides feature ID → use it.
      2. ELSE default to `N/A`.
    </steps>
  </field>

  <field name="message_context.workflow_name">
    <steps>
      1. IF caller provides workflow name → use it.
      2. ELSE default to `N/A`.
    </steps>
  </field>

  <field name="message_context.downstream_context">
    <steps>
      1. IF caller provides downstream context → use it.
      2. ELSE default to `N/A`.
    </steps>
  </field>

  <field name="message_context.messages[].preferred_dispositions">
    <steps>
      1. IF caller provides a non-empty list → use it as a soft preference order.
      2. ELSE use all supported dispositions in the default order documented by this skill.
    </steps>
  </field>

  <field name="human_shadow">
    <steps>
      1. IF caller provides a boolean → use it.
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
<procedure name="end-user-representative">
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
        - BLOCKING: Fail with `DAO_INPUT_INVALID` if message content is missing or source is invalid
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
        1. List applicable dispositions:
           - `answer` when the skill can respond directly and safely on behalf of the human.
           - `clarification` when the user request is ambiguous and needs narrowing.
           - `reframe` when the user is asking the wrong level of question and needs a better framing.
           - `critique` when the user or agent direction needs constructive challenge.
           - `instruction` when the skill should give concrete next-step guidance.
           - `approval` when the best response is concise approval-like guidance to proceed.
           - `pass_through` when the downstream agent is the best source of the answer.
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
        - CRITICAL: The skill MUST NOT claim human approval occurred; `approval` is approval-like guidance, not a real human authorization record
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
        - CRITICAL: `pass_through` should preserve the user's original intent while routing to downstream
      </constraints>
      <output>Validated response (or loop back to Phase 5)</output>
    </step_6_1>
  </phase_6>

  <phase_7 name="断 — Commit">
    <step_7_1>
      <name>Finalize Output</name>
      <action>
        1. Lock disposition, content, rationale_summary.
        2. Estimate confidence between 0.0 and 1.0 based on clarity, scope safety, and context completeness.
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
        1. DETERMINE semantic_task_type from calling_skill:
           - Extract the skill category (e.g., "bug-fix" → "bug_fix", "feature-refinement" → "feature_refinement")
           - IF calling_skill is unclear, derive from downstream_context
        2. CHECK if `x-ipe-docs/dao/` folder exists:
           - IF NOT: create it
        3. DETERMINE target log file:
           - Scan existing files in `x-ipe-docs/dao/` matching `decisions_made_*.md`
           - IF a file with matching semantic_task_type exists → append to it
           - ELSE → create new file from dao-log-template.md as `decisions_made_{semantic_task_type}.md`
        4. DETERMINE next Entry ID:
           - Read registry table in target file
           - Next ID = DAO-{N+1} where N is the count of existing entries (start at DAO-001)
        5. APPEND to registry table:
           | {Entry ID} | {timestamp} | {task_id} | {calling_skill} | {disposition} | {confidence} | {one-line summary} |
        6. APPEND detail section after the registry table:
           ## {Entry ID}
           - **Timestamp:** {ISO 8601}
           - **Task ID:** {task_id}
           - **Feature ID:** {feature_id or N/A}
           - **Workflow:** {workflow_name or N/A}
           - **Calling Skill:** {calling_skill}
           - **Source:** {source}
           - **Disposition:** {disposition}
           - **Confidence:** {confidence}
           ### Message
           > {original message content}
           ### Guidance Returned
           > {DAO response content}
           ### Rationale
           > {rationale_summary}
           ### Follow-up
           > {follow-up or "None"}
      </action>
      <constraints>
        - MANDATORY: Every DAO interaction MUST produce a log entry — no silent decisions
        - Log entries are append-only — never edit or delete previous entries
        - Semantic task type naming must be human-readable, lowercase with underscores
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
    content: "bounded response for the user or downstream handoff"
    rationale_summary: "brief explanation of why the disposition was chosen"
    confidence: 0.0
    fallback_required: false
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Single disposition selected</name>
    <verification>Result contains exactly one supported disposition</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Bounded response returned</name>
    <verification>content and rationale_summary are concise and do not expose full inner reasoning</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Fallback logic applied correctly</name>
    <verification>fallback_required is true only when human_shadow is true and internal confidence is below threshold</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Semantic log written</name>
    <verification>Log entry appended to x-ipe-docs/dao/decisions_made_{semantic_task_type}.md</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `DAO_INPUT_INVALID` | Missing message content, missing source, or invalid source value | Provide message_context with source and at least one message with content |
| `DAO_DISPOSITION_UNCLEAR` | Competing dispositions remain equally plausible after the CORE backbone | Prefer `clarification` or `pass_through`, or enable human-shadow fallback |
| `DAO_HUMAN_SHADOW_REQUIRED` | Internal confidence is below threshold while human-shadow is enabled | Route the touchpoint to a real human before irreversible action |

---

## Future Extensions

> Reserved for later versions. Do not implement persistence or recall in v1.

- **Reusable Memory:** Deferred. A future version may add cross-task experience recall. The output contract supports adding fields without breaking existing callers.

---

## References

| File | Purpose |
|------|---------|
| `references/dao-disposition-guidelines.md` | Guidance for selecting the right disposition consistently |
| `references/examples.md` | Example scenarios and expected outputs |

---

## Examples

See `.github/skills/x-ipe-dao-end-user-representative/references/examples.md` for usage examples.
