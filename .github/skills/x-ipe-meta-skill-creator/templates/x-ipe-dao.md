# Human Representative Skill Template

Use this template for skills (type: `x-ipe-dao`) that act as human representatives at human-required touchpoints while preserving bounded outputs and optional human-shadow fallback. The 道 (DAO) backbone is the CORE internal reasoning methodology for all skills of this type.

**Section Order (Cognitive Flow):**
1. CONTEXT: Purpose → Important Notes → About → When to Use
2. DECISION: Input Parameters → Definition of Ready
3. ACTION: Operations
4. VERIFY: Output Result → Definition of Done
5. REFERENCE: Error Handling → References → Examples

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

BLOCKING: {Critical mediation rule — use common language, avoid "DAO" terminology}
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
</definition_of_ready>
```

---

## Operations

### Operation: {Operation Name}

**When:** {Condition for representing human intent at this touchpoint}

```xml
<operation name="{operation_name}">
  <action>
    1. Frame the touchpoint:
       - Read the message content, source, workflow context, and downstream context.
       - Decide whether the touchpoint is best handled directly or by the downstream agent.

    2. Run the CORE backbone (道 seven-step reasoning):
       - 静虑: pause and restate the real user need in one sentence.
       - 兼听: consider the user intent, workflow state, downstream constraints, and any caller preference hints.
       - 审势: assess whether direct guidance or pass-through best preserves the workflow.
       - 权衡: compare supported dispositions against user value, scope safety, and confidence.
       - 谋后而定: choose the smallest useful intervention that unblocks the work.
       - 试错: sanity-check the proposed response for tone, clarity, and unintended scope changes.
       - 断: commit to one disposition and one bounded response.

    3. Select a disposition and draft bounded response.
    4. Score confidence and set fallback flag.
    5. Return the bounded result.
  </action>
  <constraints>
    - BLOCKING: {constraint}
  </constraints>
  <output>{what_is_returned}</output>
</operation>
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

- **Semantic Logging:** Deferred to FEATURE-047-B. This skill does not write semantic logs.
- **Reusable Memory:** Deferred. A future version may add cross-task experience recall. The output contract already supports adding fields (backward-compatible).
- **Instruction-Resource Interception:** Deferred to FEATURE-047-C.

---

## References

| File | Purpose |
|------|---------|
| `references/{file}.md` | {Reference guidance} |

---

## Examples

See `.github/skills/x-ipe-dao-{name}/references/examples.md` for usage examples.
```
