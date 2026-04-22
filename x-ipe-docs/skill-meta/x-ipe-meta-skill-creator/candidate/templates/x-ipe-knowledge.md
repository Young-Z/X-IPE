# Knowledge Skill Template

Use this template for skills (type: `x-ipe-knowledge`) that perform knowledge pipeline services — extraction, synthesis, indexing, and other knowledge operations. Knowledge skills are stateless services called by an assistant orchestrator (e.g., `x-ipe-assistant-knowledge-librarian-DAO`). Each skill defines named **Operations** as its primary structure. Inside each operation, the familiar phase backbone (博学之→笃行之) provides internal cognitive flow.

**Section Order (Cognitive Flow):**
1. CONTEXT: Purpose → Important Notes → About → When to Use
2. DECISION: Input Parameters → Definition of Ready
3. ACTION: Operations (each with phase backbone inside)
4. VERIFY: Output Result → Definition of Done
5. REFERENCE: Error Handling → Examples

> Note: Knowledge skills use "Operations" (like tool skills) but with phase backbone inside each operation (unlike tool skills). They are NOT directly task-matched — the assistant orchestrator decides when to call them.

---

```markdown
---
name: x-ipe-knowledge-{sub-category}-{name}
description: {What knowledge operation(s) this skill performs}. Triggers on operations like "{op1}", "{op2}".
---

# {Skill Name — Knowledge Skill}

## Purpose

AI Agents follow this skill to perform knowledge operations:
1. {Objective 1}
2. {Objective 2}
3. {Objective 3}

---

## Important Notes

BLOCKING: Operations are stateless services — the assistant orchestrator passes full context per call. Do NOT maintain internal state across operations.
CRITICAL: Each operation MUST define typed input/output contracts with a `writes_to` field.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.

---

## About

{Brief explanation of what knowledge domain this skill covers and its role in the knowledge pipeline}

**Key Concepts:**
- **Operation Contract** — Each operation declares its input types, output types, writes_to path, and constraints. The orchestrator uses this contract to plan execution.
- **Stateless Service** — The skill receives all needed context from the orchestrator per call. No cross-operation memory.
- **writes_to Discipline** — Every operation declares which path(s) it writes to, enabling the orchestrator to predict side effects and coordinate parallel operations.

---

## When to Use

```yaml
triggers:
  - "{operation trigger 1 — describe what the orchestrator would request}"
  - "{operation trigger 2}"

not_for:
  - "{out of scope — e.g., orchestration decisions belong to assistant skills}"
```

---

## Input Parameters

```yaml
input:
  operation: "{op1 | op2 | op3}"
  context:
    source_path: "{path to input data}"
    output_path: "{path where results should be written}"
    {param_1}: "{type/desc}"
    {param_2}: "{type/desc}"
```

### Input Initialization

BLOCKING: All input fields with non-trivial initialization MUST be documented here. Do NOT embed field initialization logic in operation steps.

```xml
<input_init>
  <field name="operation" source="Assistant orchestrator specifies which operation to perform" />

  <field name="context.source_path" source="Assistant orchestrator provides input location">
    <validation>Path must exist and be readable</validation>
  </field>

  <field name="context.output_path" source="Assistant orchestrator specifies output location">
    <validation>Parent directory must exist</validation>
  </field>
</input_init>
```

---

## Definition of Ready

CRITICAL: DoR at most 5 checkpoints. DoD at most 10 checkpoints. Keep only the most critical checks.
```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Operation specified</name>
    <verification>input.operation matches a defined operation name</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Input context provided</name>
    <verification>All required context fields for the specified operation are present</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: {operation_name}

> **Contract:**
> - **Input:** {typed params — e.g., source_path: string, format: "markdown" | "html"}
> - **Output:** {typed results — e.g., extracted_entities: Entity[], summary: string}
> - **Writes To:** {path — e.g., x-ipe-docs/memory/staging/{domain}/}
> - **Constraints:** {list — e.g., "Must not exceed 5000 tokens per entity"}

**When:** {Condition for this operation — e.g., "Orchestrator needs to extract entities from a web source"}

```xml
<operation name="{op_name}">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: source_path, parameters
      2. GATHER relevant background from knowledge base if needed
      3. UNDERSTAND the scope of what needs to be processed
    </action>
    <output>Input context understood, processing scope defined</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE input data format and completeness
      2. CHECK constraints are satisfiable
      3. IDENTIFY edge cases in the input
    </action>
    <constraints>
      - BLOCKING: {constraint — e.g., "Input must be valid markdown"}
    </constraints>
    <output>Input validated, ready for processing</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. {Core processing step 1}
      2. {Core processing step 2}
      3. {Core processing step 3}
    </action>
    <output>{Processing results}</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VALIDATE output against contract (type check, completeness)
      2. CHECK quality thresholds (if defined)
      3. IF validation fails → return error with details
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE results to {writes_to} path
      2. RETURN operation_output with success status and result data
    </action>
    <output>Results written, operation_output returned</output>
  </phase_5>

</operation>
```

### Operation: {another_operation_name}

> **Contract:**
> - **Input:** {typed params}
> - **Output:** {typed results}
> - **Writes To:** {path}
> - **Constraints:** {list}

**When:** {Condition}

```xml
<operation name="{op_name}">
  <!-- Same phase structure as above -->
  <phase_1 name="博学之 — Study Broadly">
    <action>1. {gather context}</action>
  </phase_1>
  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>1. {validate}</action>
  </phase_2>
  <phase_3 name="慎思之 — Think Carefully">
    <action>1. {process}</action>
  </phase_3>
  <phase_4 name="明辨之 — Discern Clearly">
    <action>1. {validate output}</action>
  </phase_4>
  <phase_5 name="笃行之 — Practice Earnestly">
    <action>1. {write and return}</action>
  </phase_5>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "{operation_name}"
  result:
    {field}: "{value}"
    writes_to: "{actual path written}"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed successfully</name>
    <verification>operation_output.success == true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output written to declared path</name>
    <verification>File exists at writes_to path with expected content</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output matches contract types</name>
    <verification>Returned data matches the operation's declared output types</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | Operation name not recognized | Return error listing valid operations |
| `INPUT_VALIDATION_FAILED` | Required input missing or wrong type | Return error with specific field and expected type |
| `WRITE_FAILED` | Cannot write to writes_to path | Return error; orchestrator decides retry or alternate path |
| `QUALITY_THRESHOLD_NOT_MET` | Output below quality bar | Return partial results with quality metrics; orchestrator decides |

---

## Examples

See `references/examples.md` for usage examples.
```
