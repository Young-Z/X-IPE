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

CRITICAL: **Best-Model Requirement.** When this skill is delegated to a sub-agent (e.g., via the `task` tool), it MUST use the most capable (premium) LLM model available. The 7-step backbone requires nuanced reasoning — weighing three perspectives, analyzing gains/losses, scenario planning — that benefits from the strongest model. Use the `model` parameter to select a premium model (e.g., `claude-opus-4.6`). Do NOT run this skill on fast/cheap models.

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
| 1 | 1.1 | 静虑 — Pause & Restate | Stop. Check readiness (info complete? context sufficient?). Restate the real user need in one sentence | Need is clear + readiness assessed |
| 2 | 2.1 | 兼听 — Listen Broadly | Gather three perspectives: supporting voice, opposing voice, neutral expert | All three voices considered |
| 3 | 3.1 | 审势 — Assess the Situation | Ask three questions: direction (顺势?), timing (时机?), environment (环境?) | Direct guidance vs pass-through decided |
| 4 | 4.1 | 权衡 — Weigh Trade-offs | For each disposition, analyze 利 (gains) vs 害 (losses). Take greater gain, lesser harm | Dispositions ranked by net value |
| 5 | 5.1 | 谋后而定 — Plan Then Decide | Envision best/medium/worst outcomes. Abandon if worst case is unacceptable | One disposition selected + worst-case gate passed |
| 6 | 6.1 | 试错 — Small-Step Validation | Small step, don't go all-in (小步走不梭哈). Test stone first (投石问路). Check reversibility | Response is bounded and reversible |
| 7 | 7.1 | 断 — Commit | Lock it. Counsel is collective, the call is singular (谋贵众断贵独). No flip-flopping | Final output ready |
| 8 | 8.1 | 录 — Record | Write semantic log entry to x-ipe-docs/dao/ | Log entry written |

BLOCKING: All 8 phases MUST be executed in order. No phase may be skipped.
BLOCKING: Phase 7 (断) MUST produce exactly one disposition — not multiple.

### Phase Definitions (道 Seven-Step Backbone + Record)

| Phase | Chinese | English | 心法 (Heart Method) | Typical Activities |
|-------|---------|---------|---------------------|-------------------|
| 1 | 静虑 (Jìnglǜ) | Pause & Restate | 静而后能安，安而后能虑，虑而后能得 | Check readiness (info? context? urgency?), strip noise, one-sentence restatement |
| 2 | 兼听 (Jiāntīng) | Listen Broadly | 兼听则明，偏信则暗 | Three voices: supporting, opposing, neutral expert. One opinion = guaranteed misstep |
| 3 | 审势 (Shěnshì) | Assess the Situation | 顺势者昌，逆势者亡 | Three questions: direction (顺势?), timing (时机?), environment (环境?) |
| 4 | 权衡 (Quánhéng) | Weigh Trade-offs | 两利相权取其重，两害相权取其轻 | Two columns per disposition: 利 (gains) vs 害 (losses). Rank by net value |
| 5 | 谋后而定 (Móuhòu'érdìng) | Plan Then Decide | 不能接受的最坏结果，直接放弃 | Three scenarios: best/medium/worst. Worst-case gate: abandon if intolerable |
| 6 | 试错 (Shìcuò) | Small-Step Validation | 投石问路，观衅而动 | Small step, don't go all-in. Test stone first. Effective → proceed, ineffective → stop |
| 7 | 断 (Duàn) | Commit | 谋贵众，断贵独 | Lock it. Deliberate before, don't second-guess after. No flip-flopping |
| 8 | 录 (Lù) | Record | — | Write semantic log entry, append-only |

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
    <!-- 心法：静而后能安，安而后能虑，虑而后能得 -->
    <!-- 不急着定，先"停一停" -->
    <step_1_1>
      <name>Pause and Check Readiness</name>
      <action>
        1. STOP before deciding anything. Check readiness:
           - Is the message content clear enough to act on? (info completeness)
           - Is there sufficient context (task_id, workflow state) to make a sound judgment?
           - Are there signs of cascading urgency that might rush a poor decision?
        2. IF context is insufficient → disposition should lean toward `clarification` or `pass_through`
           (flag this for Phase 4, do not decide yet)
        3. Read message_context.messages content.
        4. Strip noise, jargon, and indirection.
        5. Produce a single clear sentence: "The user needs: {X}."
      </action>
      <constraints>
        - MUST produce exactly one sentence
        - MUST NOT interpret beyond what the message says
        - BLOCKING: Fail with `DAO_INPUT_INVALID` if message content is missing or source is invalid
        - If info is incomplete, do NOT guess — carry the uncertainty forward
      </constraints>
      <output>One-sentence user need statement + readiness assessment</output>
    </step_1_1>
  </phase_1>

  <phase_2 name="兼听 — Listen Broadly">
    <!-- 心法：兼听则明，偏信则暗 -->
    <!-- 至少找三种声音：支持、反对、中立旁观 -->
    <step_2_1>
      <name>Gather Three Perspectives</name>
      <action>
        1. Read message_context: source, calling_skill, task_id, feature_id, workflow_name, downstream_context.
        2. Note any preferred_dispositions from the caller.
        3. Construct THREE internal perspectives on the message:
           a. **Supporting voice:** What interpretation gives the user the most benefit of the doubt?
           b. **Opposing voice:** What could go wrong if we take the message at face value? What's the risk?
           c. **Neutral expert voice:** What would a detached, domain-aware observer say about the right response?
        4. Only hearing one perspective guarantees a misstep. All three MUST be considered.
        5. Identify any constraints (scope boundaries, blocked states, pending decisions).
      </action>
      <constraints>
        - MUST consider all three voices — do not shortcut to one perspective
      </constraints>
      <output>Three-perspective context summary (internal only)</output>
    </step_2_1>
  </phase_2>

  <phase_3 name="审势 — Assess the Situation">
    <!-- 心法：顺势者昌，逆势者亡 -->
    <!-- 问三句：顺大势？时机对？环境允许？ -->
    <step_3_1>
      <name>Assess Direction, Timing, and Environment</name>
      <action>
        1. Ask three questions:
           a. **Direction (顺势?):** Does the proposed action align with the current workflow direction,
              or does it fight against the established flow? Prefer responses that work WITH the workflow.
           b. **Timing (时机?):** Is now the right moment for this intervention? Is the downstream
              skill at a stage where guidance is useful, or is it too early / too late?
           c. **Environment (环境?):** Does the current project state, feature phase, and agent
              capability allow for this type of response? Are there blockers?
        2. Based on these three assessments, decide the primary path:
           - Direct guidance (this skill answers)
           - Pass-through (downstream agent handles it)
        3. If all three signals say "not now" → lean toward `pass_through` or `clarification`.
      </action>
      <output>Direction/timing/environment assessment + primary path decision (internal only)</output>
    </step_3_1>
  </phase_3>

  <phase_4 name="权衡 — Weigh Trade-offs">
    <!-- 心法：两利相权取其重，两害相权取其轻 -->
    <!-- 只算两件事：利、害 -->
    <step_4_1>
      <name>Analyze Gains and Losses for Each Disposition</name>
      <action>
        1. List applicable dispositions: answer, clarification, reframe, critique, instruction, approval, pass_through.
        2. For each candidate, analyze TWO columns:
           a. **利 (Gains):** What does the user gain? What workflow progress is preserved?
              What short-term and long-term value does this create?
           b. **害 (Losses):** What could go wrong? What scope risk, misinterpretation risk,
              or wasted effort might result? Is there a fallback/exit if this fails?
        3. Apply the principle: between two gains, take the greater; between two harms, take the lesser.
        4. IF preferred_dispositions provided → weight those higher (but do not blindly follow).
        5. Rank dispositions by net value (gains minus harms).
      </action>
      <output>Gains/losses analysis + ranked disposition candidates (internal only)</output>
    </step_4_1>
  </phase_4>

  <phase_5 name="谋后而定 — Plan Then Decide">
    <!-- 想清楚三种结局：最好、中等、最坏 -->
    <!-- 不能接受的最坏结果，直接放弃 -->
    <step_5_1>
      <name>Three-Scenario Planning</name>
      <action>
        1. For the top-ranked disposition, envision three outcomes:
           a. **Best case:** The response perfectly unblocks the work and the user proceeds smoothly.
           b. **Medium case:** The response partially helps but requires follow-up clarification.
           c. **Worst case:** The response misleads, expands scope, or causes the downstream agent to go off-track.
        2. WORST-CASE GATE: If the worst case is unacceptable (irreversible harm, major scope derailment)
           → abandon this disposition, fall back to the next-ranked candidate.
        3. Select the disposition whose worst case is still tolerable.
        4. Verify it is the SMALLEST useful intervention — prefer pass_through over answer when downstream can handle it.
        5. Draft the bounded response content.
        6. Draft the rationale_summary (one sentence).
      </action>
      <constraints>
        - MUST select exactly one disposition
        - MUST prefer minimal intervention
        - CRITICAL: The skill MUST NOT claim human approval occurred; `approval` is approval-like guidance only
        - ABANDON if worst case is unacceptable — do not push through
      </constraints>
      <output>Selected disposition + draft content + draft rationale</output>
    </step_5_1>
  </phase_5>

  <phase_6 name="试错 — Small-Step Validation">
    <!-- 心法：投石问路，观衅而动 -->
    <!-- 小步走，不梭哈 -->
    <step_6_1>
      <name>Validate with Small-Step Principle</name>
      <action>
        1. Apply the small-step principle (小步走，不梭哈):
           - Does the response commit to the MINIMUM necessary? No over-answering.
           - Is the response reversible? If the caller needs to course-correct, can they?
           - Is this a "test stone" (投石问路) — providing just enough to see the reaction?
        2. Check tone: is the response respectful and clear?
        3. Check clarity: would the caller understand what to do next?
        4. Check scope: does the response introduce unintended scope changes?
        5. Check boundaries: does the response stay within this skill's bounded role?
        6. IF any check fails → return to Phase 5 and adjust.
           Effective → proceed. Ineffective → stop and revise immediately.
      </action>
      <constraints>
        - MUST NOT pass a response that expands downstream task scope
        - MUST prefer bounded, reversible responses over sweeping ones
        - CRITICAL: `pass_through` should preserve the user's original intent while routing to downstream
      </constraints>
      <output>Validated response (or loop back to Phase 5)</output>
    </step_6_1>
  </phase_6>

  <phase_7 name="断 — Commit">
    <!-- 心法：谋贵众，断贵独 -->
    <!-- 决策前多犹豫，决策后少纠结 -->
    <step_7_1>
      <name>Commit with Conviction</name>
      <action>
        1. Lock disposition, content, rationale_summary.
           Deliberation is over — do NOT second-guess after this point.
        2. Estimate confidence between 0.0 and 1.0 based on clarity, scope safety, and context completeness.
        3. Set fallback_required:
           - true ONLY if human_shadow == true AND confidence < internal threshold.
           - false otherwise.
        4. Assemble operation_output contract.
        5. Once committed, this decision stands. "谋贵众，断贵独" — counsel is collective, but the final call is singular.
      </action>
      <constraints>
        - MUST NOT revisit the disposition after committing
        - The decision is final for this interaction — no flip-flopping
      </constraints>
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
