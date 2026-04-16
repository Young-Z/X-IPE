---
name: x-ipe-knowledge-keeper-memory
description: Unified write gatekeeper for persistent memory. Stores new knowledge entries and promotes working drafts to episodic, semantic, or procedural tiers. Delegates file I/O to scripts/memory_ops.py. Triggers on operations like "store", "promote".
---

# Keeper Memory — Knowledge Skill

## Purpose

AI Agents follow this skill to perform memory write operations:
1. Store new knowledge content to a persistent memory tier (episodic, semantic, procedural)
2. Promote working drafts from `.working/` to a persistent memory tier
3. Bootstrap memory folder structure when missing (auto-init)

---

## Important Notes

BLOCKING: Operations are stateless services — the assistant orchestrator passes full context per call. Do NOT maintain internal state across operations.
CRITICAL: Each operation MUST define typed input/output contracts with a `writes_to` field.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.
CRITICAL: This skill handles FILE I/O ONLY. Ontology entity registration is performed by `ontology-builder` (FEATURE-059-C). Relationship maintenance is performed by `ontology-synthesizer` (FEATURE-059-D).

---

## About

This skill serves as the single write gateway to persistent memory. All knowledge that needs to survive beyond a conversation session flows through keeper-memory's `store` or `promote` operations.

**Key Concepts:**
- **Operation Contract** — Each operation declares its input types, output types, writes_to path, and constraints. The orchestrator uses this contract to plan execution.
- **Stateless Service** — The skill receives all needed context from the orchestrator per call. No cross-operation memory.
- **writes_to Discipline** — Every operation declares `x-ipe-docs/memory/{memory_type}/` as its write target, enabling the orchestrator to predict side effects.
- **File-Only CRUD** — This skill writes/moves `.md` content files. Ontology registration is a separate downstream step.
- **Meaningful Slugs** — Filenames derived from title (lowercase, hyphenated, max 60 chars), not from IDs.

---

## When to Use

```yaml
triggers:
  - "Store new knowledge content to persistent memory"
  - "Promote a working draft from .working/ to a memory tier"
  - "Bootstrap memory folder structure"

not_for:
  - "Searching or reading memory (use x-ipe-knowledge-extractor-memory)"
  - "Ontology entity registration (use ontology-builder in 059-C)"
  - "Web content extraction (use x-ipe-knowledge-extractor-web)"
```

---

## Input Parameters

```yaml
input:
  operation: "store | promote"
  context:
    # For store:
    content: "string | structured"    # Knowledge content to persist
    memory_type: "episodic | semantic | procedural"
    metadata: "dict"                  # source, extracted_by, date, etc.
    tags: "string[]"                  # Searchable tags
    title: "string"                   # Title for slug generation
    # For promote:
    working_path: "string"            # Path within .working/
    memory_type: "episodic | semantic | procedural"
    metadata: "dict"                  # Additional metadata
    title: "string"                   # Title for slug generation
```

### Input Initialization

BLOCKING: All input fields with non-trivial initialization MUST be documented here. Do NOT embed field initialization logic in operation steps.

```xml
<input_init>
  <field name="operation" source="Assistant orchestrator specifies which operation to perform">
    <validation>Must be one of: store, promote</validation>
  </field>
  <field name="context.memory_type" source="Assistant orchestrator specifies target tier">
    <validation>Must be one of: episodic, semantic, procedural</validation>
  </field>
  <field name="context.title" source="Assistant orchestrator provides title for slug generation">
    <validation>Non-empty string</validation>
  </field>
  <field name="context.content" source="Required for store operation">
    <validation>Non-empty string or structured data</validation>
  </field>
  <field name="context.working_path" source="Required for promote operation">
    <validation>Must exist and be within x-ipe-docs/memory/.working/</validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Operation specified</name>
    <verification>input.operation is "store" or "promote"</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Memory type valid</name>
    <verification>context.memory_type is one of: episodic, semantic, procedural</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Operation-specific inputs present</name>
    <verification>store: content + title present; promote: working_path + title present</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: store

> **Contract:**
> - **Input:** content: string|structured, memory_type: "episodic"|"semantic"|"procedural", metadata: dict, tags: string[], title: string
> - **Output:** stored_path: string, memory_entry_id: string
> - **Writes To:** x-ipe-docs/memory/{memory_type}/
> - **Constraints:** memory_type must be valid; bootstrap folders if missing; generate ID as {type_prefix}-{YYYYMMDD}-{sequence}; derive filename slug from title

**When:** Orchestrator needs to persist new knowledge content to a memory tier.

```xml
<operation name="store">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: content, memory_type, metadata, tags, title
      2. DETERMINE target folder: x-ipe-docs/memory/{memory_type}/
      3. CHECK if memory folder structure exists
    </action>
    <output>Input context understood, target folder identified</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE memory_type is one of: episodic, semantic, procedural
      2. VALIDATE content is non-empty
      3. VALIDATE title is non-empty string
      4. IF memory folder missing → RUN `python3 scripts/init_memory.py` to bootstrap
    </action>
    <constraints>
      - BLOCKING: Invalid memory_type → return error INVALID_MEMORY_TYPE with valid options
      - BLOCKING: Empty content → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated, folders ready</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. DERIVE filename slug from title: lowercase, replace spaces/special chars with hyphens, max 60 chars
      2. WRITE content to a temporary content file
      3. RUN `python3 scripts/memory_ops.py create --type {memory_type} --title "{title}" --tags '{json_tags}' --metadata '{json_metadata}' --content-file {content_file} --memory-dir x-ipe-docs/memory`
      4. CAPTURE output: stored_path, memory_entry_id
    </action>
    <output>Content file written, ID generated</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY file exists at stored_path
      2. VERIFY file content matches input content
      3. VERIFY memory_entry_id format matches {type_prefix}-{YYYYMMDD}-{sequence}
      4. IF any verification fails → return error with details
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "store"
         - result: { stored_path, memory_entry_id }
         - writes_to: "x-ipe-docs/memory/{memory_type}/"
         - errors: []
    </action>
    <output>Store operation complete, result returned to orchestrator</output>
  </phase_5>

</operation>
```

### Operation: promote

> **Contract:**
> - **Input:** working_path: string, memory_type: "episodic"|"semantic"|"procedural", metadata: dict, title: string
> - **Output:** promoted_path: string
> - **Writes To:** x-ipe-docs/memory/{memory_type}/
> - **Constraints:** working_path must exist in .working/; original removed after move; target folder bootstrapped if missing

**When:** Orchestrator needs to promote a working draft to persistent storage.

```xml
<operation name="promote">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input context: working_path, memory_type, metadata, title
      2. DETERMINE source: x-ipe-docs/memory/.working/{working_path} or absolute path within .working/
      3. DETERMINE target folder: x-ipe-docs/memory/{memory_type}/
    </action>
    <output>Input context understood, source and target identified</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE working_path exists within x-ipe-docs/memory/.working/
      2. VALIDATE memory_type is one of: episodic, semantic, procedural
      3. VALIDATE title is non-empty
      4. IF target folder missing → RUN `python3 scripts/init_memory.py` to bootstrap
    </action>
    <constraints>
      - BLOCKING: working_path not found → return error PATH_NOT_FOUND
      - BLOCKING: working_path not within .working/ → return error INVALID_PATH
    </constraints>
    <output>Input validated, paths confirmed</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. RUN `python3 scripts/memory_ops.py promote --path {working_path} --type {memory_type} --title "{title}" --metadata '{json_metadata}' --memory-dir x-ipe-docs/memory`
      2. CAPTURE output: promoted_path
    </action>
    <output>File moved to target tier</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY file exists at promoted_path
      2. VERIFY original file removed from .working/
      3. IF any verification fails → return error with details
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "promote"
         - result: { promoted_path }
         - writes_to: "x-ipe-docs/memory/{memory_type}/"
         - errors: []
    </action>
    <output>Promote operation complete, result returned to orchestrator</output>
  </phase_5>

</operation>
```

**Note on operations vs scripts:** The `store` and `promote` operations define the cognitive flow (phases 博学之→笃行之) that the agent follows. The actual file I/O is performed by `scripts/memory_ops.py`. Additional CRUD operations (read, update, delete, list) are available directly via the script for programmatic use by other skills or the orchestrator, without needing a full SKILL.md operation wrapper.

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "store | promote"
  result:
    stored_path: "x-ipe-docs/memory/{type}/{slug}.md"     # store
    memory_entry_id: "{prefix}-{YYYYMMDD}-{seq}"           # store
    promoted_path: "x-ipe-docs/memory/{type}/{slug}.md"    # promote
    writes_to: "x-ipe-docs/memory/{memory_type}/"
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
    <verification>stored_path/promoted_path is string; memory_entry_id matches pattern</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Scripts functional</name>
    <verification>init_memory.py and memory_ops.py execute without error</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | Operation name not "store" or "promote" | Return error listing valid operations |
| `INVALID_MEMORY_TYPE` | memory_type not episodic/semantic/procedural | Return error listing valid types |
| `INPUT_VALIDATION_FAILED` | Required input missing or wrong type | Return error with specific field |
| `PATH_NOT_FOUND` | working_path doesn't exist (promote) | Return error with path details |
| `INVALID_PATH` | Path not within .working/ (promote) | Return error explaining constraint |
| `WRITE_FAILED` | Cannot write to target folder | Return error; orchestrator decides retry |
| `SLUG_CONFLICT` | Generated filename already exists | Append numeric suffix (e.g., -2) |

---

## Examples

See `references/examples.md` for usage examples.
