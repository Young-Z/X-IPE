# Tool Skill Template

Use this template for utility functions, integrations, or specific tool operations.

**Section Order (Cognitive Flow):**
1. CONTEXT: Purpose → Important Notes → About → When to Use
2. DECISION: Input Parameters → Definition of Ready
3. ACTION: Operations
4. VERIFY: Output Result → Definition of Done
5. REFERENCE: Error Handling → Templates → Examples

> Note: Tool skills use "Operations" instead of "Execution Flow Summary" as they provide a library of capabilities.

---

```markdown
---
name: x-ipe-tool-{name}
description: {What it does}. Use when {trigger conditions}. Triggers on requests like "{trigger 1}", "{trigger 2}".
---

# {Tool Name}

## Purpose

AI Agents follow this skill to {use tool/service} to:
1. {Objective 1}
2. {Objective 2}
3. {Objective 3}

---

## Important Notes

BLOCKING: {Critical rule that must not be skipped}
CRITICAL: {Important consideration}

---

## About

{Brief explanation of what the tool is and key concepts}

**Key Concepts:**
- **{Concept 1}** - {Definition}
- **{Concept 2}** - {Definition}

---

## When to Use

```yaml
triggers:
  - "{trigger phrase 1}"
  - "{trigger phrase 2}"
  
not_for:
  - "{use case handled by another skill}"
```

---

## Input Parameters

```yaml
input:
  operation: "{op1 | op2 | op3}"
  {param_group}:
    {param_1}: "{type/desc}"
    {param_2}: "{type/desc}"
```

### Input Initialization

Describes how to resolve each input field value before execution begins. Acts as the skill's constructor — all resolution logic is centralized here instead of in execution steps.

BLOCKING: All input fields with non-trivial initialization MUST be documented here. Do NOT embed field initialization logic in execution procedure steps.

```xml
<input_init>
  <field name="operation" source="Caller specifies which operation to perform" />

  <field name="{param_1}">
    <steps>
      1. {If condition, resolve value}
      2. {Fallback action}
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

CRITICAL: DoR at most 5 checkpoints. DoD at most 10 checkpoints. Keep only the most critical checks.
```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>{Prerequisite 1}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>{Prerequisite 2}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: {Operation Name}

**When:** {Condition for this operation}

```xml
<operation name="{op_name}">
  <action>
    1. {step_1}
    2. {step_2}
    3. {step_3}
  </action>
  <constraints>
    - BLOCKING: {constraint}
  </constraints>
  <output>{what_is_returned}</output>
</operation>
```

### Operation: {Another Operation}

**When:** {Condition}

```xml
<operation name="{op_name}">
  <action>
    1. {step_1}
  </action>
  <output>{result}</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    {field}: "{value}"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation Completed</name>
    <verification>Success returned true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>{Output Verified}</name>
    <verification>{Verification step}</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `{ERROR_CODE}` | {Cause} | {Resolution} |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/{file}.md` | {Description} |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples.
```
