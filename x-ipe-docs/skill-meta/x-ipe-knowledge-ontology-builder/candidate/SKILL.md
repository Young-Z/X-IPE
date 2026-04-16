---
name: x-ipe-knowledge-ontology-builder
description: Discovers classes, properties, and instances from constructed knowledge and registers them in `.ontology/` with lifecycle flags. Delegates JSONL I/O to scripts/ontology_ops.py. Triggers on operations like "discover_nodes", "discover_properties", "create_instances", "critique_validate", "register_vocabulary".
---

# Ontology Builder — Knowledge Skill

## Purpose

AI Agents follow this skill to perform ontology construction operations:
1. Discover classes/concepts from memory content and register them in `.ontology/schema/`
2. Discover properties for classes via web search and source analysis
3. Create entity instances with lifecycle flags (`Ephemeral` / `Persistent`)
4. Validate ontology entries against vocabulary for consistency
5. Register new vocabulary terms with broader/narrower hierarchy

---

## Important Notes

BLOCKING: Operations are stateless services — the assistant orchestrator passes full context per call. Do NOT maintain internal state across operations.
CRITICAL: Each operation MUST define typed input/output contracts with a `writes_to` field.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.
CRITICAL: This skill writes DIRECTLY to `.ontology/` (not `.working/ontology/`). Ontology data is the persistent structure — there is no staging area.
CRITICAL: Every class meta and instance record MUST include `synthesize_id: null` and `synthesize_message: null` on creation. These fields are populated later by the ontology-synthesizer (FEATURE-059-D).

---

## About

This skill serves as the ontology construction gateway. It discovers domain structure (classes, properties, vocabulary) from memory content and registers the results in `.ontology/`. It absorbs build capabilities from the retired `x-ipe-tool-ontology`.

**Key Concepts:**
- **Operation Contract** — Each operation declares its input types, output types, writes_to path, and constraints. The orchestrator uses this contract to plan execution.
- **Stateless Service** — The skill receives all needed context from the orchestrator per call. No cross-operation memory.
- **writes_to Discipline** — Every operation declares which `.ontology/` sub-path it writes to, enabling the orchestrator to predict side effects.
- **Lifecycle Flag** — Instances referencing `.working/` content are `Ephemeral`; those referencing persistent memory are `Persistent`.
- **JSONL Event Sourcing** — All schema and instance data uses append-only JSONL with `{op, type, id, ts, props}` envelope.

---

## When to Use

```yaml
triggers:
  - "Discover classes/concepts from source content and build ontology schema"
  - "Discover properties for a class using web search and source analysis"
  - "Create entity instances from memory content with lifecycle flags"
  - "Validate ontology consistency against vocabulary"
  - "Register new vocabulary terms with SKOS hierarchy"

not_for:
  - "Relationship/edge creation between entities (use ontology-synthesizer in 059-D)"
  - "Memory file CRUD (use x-ipe-knowledge-keeper-memory)"
  - "Searching/reading ontology (use x-ipe-tool-ontology search ops)"
  - "Orchestration decisions (belong to assistant skills)"
```

---

## Input Parameters

```yaml
input:
  operation: "discover_nodes | discover_properties | create_instances | critique_validate | register_vocabulary"
  context:
    # discover_nodes:
    source_content: "string[]"        # Paths to memory files
    depth_limit: "int"                # Max hierarchy depth (default: 3)
    # discover_properties:
    class_meta: "dict"                # {id, label, description, source_files[]}
    source_content: "string[]"        # Content to analyze
    web_search_template: "string"     # Search template
    # create_instances:
    class_registry: "object[]"        # [{id, label, properties[]}]
    source_content: "string[]"        # Memory file paths
    property_schema: "object[]"       # From discover_properties
    # critique_validate:
    class_registry: "object[]"
    instances: "object[]"
    vocabulary_index: "dict"
    # register_vocabulary:
    new_terms: "object[]"             # [{label, broader?, narrower?[], scheme}]
    target_scheme: "string"           # e.g., "technology"
```

### Input Initialization

BLOCKING: All input fields with non-trivial initialization MUST be documented here.

```xml
<input_init>
  <field name="operation" source="Assistant orchestrator specifies which operation to perform">
    <validation>Must be one of: discover_nodes, discover_properties, create_instances, critique_validate, register_vocabulary</validation>
  </field>
  <field name="context.source_content" source="Orchestrator provides paths to memory files">
    <validation>Non-empty string array; each path must exist</validation>
  </field>
  <field name="context.depth_limit" source="Orchestrator or default" default="3">
    <validation>Positive integer, max 10</validation>
  </field>
  <field name="context.class_meta" source="Orchestrator provides class to enrich (discover_properties)">
    <validation>Must contain id, label, description, source_files</validation>
  </field>
  <field name="context.target_scheme" source="Orchestrator specifies vocabulary scheme (register_vocabulary)">
    <validation>Non-empty string, kebab-case</validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Operation specified</name>
    <verification>input.operation matches one of the 5 defined operation names</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Operation-specific context provided</name>
    <verification>All required context fields for the specified operation are present</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Ontology directory accessible</name>
    <verification>x-ipe-docs/memory/.ontology/ exists or can be created</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: discover_nodes

> **Contract:**
> - **Input:** source_content: string[], depth_limit: int (default: 3)
> - **Output:** node_tree: object[] [{label, description, source_files[], parent?, children[]}], discovery_report: string
> - **Writes To:** x-ipe-docs/memory/.ontology/schema/
> - **Delegates To:** `scripts/ontology_ops.py register_class`
> - **Constraints:** Breadth-first scan; depth-limited; class IDs are kebab-case slugs

**When:** Orchestrator needs to discover domain classes/concepts from memory content.

```xml
<operation name="discover_nodes">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ source_content paths — load each memory file
      2. DETERMINE depth_limit (default 3 if not specified)
      3. GATHER existing class-registry.jsonl to avoid duplicates
    </action>
    <output>Source content loaded, existing classes known</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE source_content is non-empty string array
      2. VALIDATE each path exists and is readable
      3. VALIDATE depth_limit is positive integer ≤ 10
    </action>
    <constraints>
      - BLOCKING: Empty source_content → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. SCAN source content breadth-first: identify top-level domain nouns/concepts
      2. For each concept, BUILD class node: {label, description, source_files, parent, children}
      3. LIMIT hierarchy depth to depth_limit
      4. For each class node, RUN:
         `python3 scripts/ontology_ops.py register_class --label "{label}" --description "{desc}" --source-files '{json_paths}' --parent "{parent_id}" --ontology-dir x-ipe-docs/memory/.ontology`
      5. COMPILE node_tree and discovery_report
    </action>
    <output>Classes registered, node_tree built</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY each class exists in class-registry.jsonl
      2. VERIFY node_tree entries have required fields (label, description, source_files)
      3. IF verification fails → return error with details
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "discover_nodes"
         - result: { node_tree, discovery_report }
         - writes_to: "x-ipe-docs/memory/.ontology/schema/"
         - errors: []
    </action>
    <output>discover_nodes complete</output>
  </phase_5>

</operation>
```

### Operation: discover_properties

> **Contract:**
> - **Input:** class_meta: dict {id, label, description, source_files[]}, source_content: string[], web_search_template: string
> - **Output:** proposed_properties: object[] [{name, kind, range, cardinality, vocabulary_scheme?}], search_results: string
> - **Writes To:** x-ipe-docs/memory/.ontology/schema/
> - **Delegates To:** `scripts/ontology_ops.py add_properties`
> - **Constraints:** Web search first, then context analysis; vocabulary-linked properties must reference existing scheme

**When:** Orchestrator needs to enrich a class with property definitions.

```xml
<operation name="discover_properties">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ class_meta: id, label, description, source_files
      2. READ source_content files for domain context
      3. PREPARE web_search_template (default: "What are common attributes of a {class_label}?")
    </action>
    <output>Class context and source content loaded</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE class_meta has id, label, description, source_files
      2. VALIDATE class_meta.id exists in class-registry.jsonl
      3. VALIDATE source_content is non-empty
    </action>
    <constraints>
      - BLOCKING: class_meta.id not in registry → return error CLASS_NOT_FOUND
    </constraints>
    <output>Input validated, class exists</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. WEB SEARCH using template with class label for general attributes
      2. ANALYZE source_content for context-specific properties
      3. PROPOSE property schema: [{name, kind, range, cardinality, vocabulary_scheme?}]
         - kind: "datatype" | "vocabulary" | "object"
         - range: data type or vocabulary scheme reference
         - cardinality: "single" | "multi"
      4. RUN `python3 scripts/ontology_ops.py add_properties --class-id "{id}" --properties '{json_props}' --ontology-dir x-ipe-docs/memory/.ontology`
    </action>
    <output>Properties proposed and registered</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY properties written to class-registry.jsonl
      2. VERIFY vocabulary-linked properties reference existing schemes
      3. IF issues found → include in output but don't fail
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "discover_properties"
         - result: { proposed_properties, search_results }
         - writes_to: "x-ipe-docs/memory/.ontology/schema/"
         - errors: []
    </action>
    <output>discover_properties complete</output>
  </phase_5>

</operation>
```

### Operation: create_instances

> **Contract:**
> - **Input:** class_registry: object[], source_content: string[], property_schema: object[]
> - **Output:** instances: object[] [{id, class, label, props, lifecycle}]
> - **Writes To:** x-ipe-docs/memory/.ontology/instances/
> - **Delegates To:** `scripts/ontology_ops.py create_instance`
> - **Constraints:** Lifecycle from source_files; chunk rotation at 5000 lines; synthesize fields null

**When:** Orchestrator needs to create entity instances from source content.

```xml
<operation name="create_instances">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ class_registry and property_schema
      2. READ source_content files to identify entities
      3. CHECK current instance chunk status (line count)
    </action>
    <output>Source content and schemas loaded</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE class_registry is non-empty
      2. VALIDATE source_content paths exist
      3. VALIDATE property_schema matches class_registry classes
    </action>
    <constraints>
      - BLOCKING: Empty class_registry → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. For each entity in source_content:
         a. DETERMINE class from class_registry
         b. FILL properties from property_schema (null if N/A)
         c. DETERMINE lifecycle: Ephemeral if any source_file contains ".working/", else Persistent
         d. RUN `python3 scripts/ontology_ops.py create_instance --class "{class_id}" --label "{label}" --source-files '{json_paths}' --properties '{json_props}' --ontology-dir x-ipe-docs/memory/.ontology`
      2. Script handles chunk rotation (new chunk at 5000 lines)
    </action>
    <output>Instances created with lifecycle flags</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY each instance exists in instance chunk files
      2. VERIFY lifecycle flags are correct (Ephemeral for .working/, Persistent otherwise)
      3. VERIFY synthesize_id and synthesize_message are null
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "create_instances"
         - result: { instances }
         - writes_to: "x-ipe-docs/memory/.ontology/instances/"
         - errors: []
    </action>
    <output>create_instances complete</output>
  </phase_5>

</operation>
```

### Operation: critique_validate

> **Contract:**
> - **Input:** class_registry: object[], instances: object[], vocabulary_index: dict
> - **Output:** critique_report: dict {accuracy_score, completeness_score, suggestions[]}, term_issues: object[]
> - **Writes To:** x-ipe-docs/memory/.ontology/ (feedback file only)
> - **Constraints:** Sub-agent reviews; constructive feedback; flags unknown vocabulary terms

**When:** Orchestrator needs to validate ontology quality and term consistency.

```xml
<operation name="critique_validate">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ class_registry, instances, vocabulary_index
      2. LOAD vocabulary schemes from .ontology/vocabulary/
    </action>
    <output>All ontology data loaded for review</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE class_registry is non-empty
      2. VALIDATE instances is non-empty
      3. VALIDATE vocabulary_index is a dict
    </action>
    <constraints>
      - BLOCKING: Empty class_registry or instances → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. REVIEW property accuracy: do instance values match class property ranges?
      2. CHECK term consistency: do vocabulary-linked values exist in their scheme?
      3. RUN `python3 scripts/ontology_ops.py validate_terms --terms '{json_terms}' --ontology-dir x-ipe-docs/memory/.ontology` for batch term validation
      4. SCORE accuracy (0–100) and completeness (0–100)
      5. COMPILE suggestions[] and term_issues[]
    </action>
    <output>Critique report compiled</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY critique_report has accuracy_score, completeness_score, suggestions
      2. VERIFY term_issues each have {term, issue, suggestion}
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE feedback summary to x-ipe-docs/memory/.ontology/_critique-feedback.md
      2. RETURN operation_output:
         - success: true
         - operation: "critique_validate"
         - result: { critique_report, term_issues }
         - writes_to: "x-ipe-docs/memory/.ontology/"
         - errors: []
    </action>
    <output>critique_validate complete</output>
  </phase_5>

</operation>
```

### Operation: register_vocabulary

> **Contract:**
> - **Input:** new_terms: object[] [{label, broader?, narrower?[], scheme}], target_scheme: string
> - **Output:** updated_vocabulary: dict, added_terms: string[]
> - **Writes To:** x-ipe-docs/memory/.ontology/vocabulary/
> - **Delegates To:** `scripts/ontology_ops.py add_vocabulary`
> - **Constraints:** Deduplicate before adding; maintain broader/narrower hierarchy; create scheme if missing

**When:** Orchestrator needs to register new controlled vocabulary terms.

```xml
<operation name="register_vocabulary">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ new_terms and target_scheme
      2. LOAD existing vocabulary scheme from .ontology/vocabulary/{target_scheme}.json (if exists)
    </action>
    <output>Terms and existing vocabulary loaded</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE new_terms is non-empty array
      2. VALIDATE each term has a label
      3. VALIDATE target_scheme is non-empty kebab-case string
    </action>
    <constraints>
      - BLOCKING: Empty new_terms → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. DEDUPLICATE: filter out terms already in the scheme
      2. For each new term, RUN:
         `python3 scripts/ontology_ops.py add_vocabulary --scheme "{target_scheme}" --label "{label}" --broader "{broader}" --narrower '{json_narrower}' --ontology-dir x-ipe-docs/memory/.ontology`
      3. Script handles hierarchy updates (broader's narrower list, etc.)
    </action>
    <output>Terms registered</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY scheme file exists at .ontology/vocabulary/{target_scheme}.json
      2. VERIFY added terms appear in the scheme
      3. VERIFY broader/narrower references are bidirectional
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. RETURN operation_output:
         - success: true
         - operation: "register_vocabulary"
         - result: { updated_vocabulary, added_terms }
         - writes_to: "x-ipe-docs/memory/.ontology/vocabulary/"
         - errors: []
    </action>
    <output>register_vocabulary complete</output>
  </phase_5>

</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "discover_nodes | discover_properties | create_instances | critique_validate | register_vocabulary"
  result:
    node_tree: "object[]"              # discover_nodes
    discovery_report: "string"         # discover_nodes
    proposed_properties: "object[]"    # discover_properties
    search_results: "string"           # discover_properties
    instances: "object[]"              # create_instances
    critique_report: "dict"            # critique_validate
    term_issues: "object[]"            # critique_validate
    updated_vocabulary: "dict"         # register_vocabulary
    added_terms: "string[]"            # register_vocabulary
    writes_to: "string"               # Actual path written
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
  <checkpoint required="true">
    <name>Lifecycle flags correct</name>
    <verification>Instances with .working/ sources have Ephemeral; others have Persistent</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Synthesize fields initialized</name>
    <verification>All new records have synthesize_id: null and synthesize_message: null</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | Operation name not recognized | Return error listing valid operations |
| `INPUT_VALIDATION_FAILED` | Required input missing or wrong type | Return error with specific field and expected type |
| `CLASS_NOT_FOUND` | Class ID not in registry (discover_properties) | Return error; orchestrator should run discover_nodes first |
| `WRITE_FAILED` | Cannot write to .ontology/ path | Return error; orchestrator decides retry |
| `VOCABULARY_SCHEME_NOT_FOUND` | Referenced scheme doesn't exist (validation) | Flag in term_issues; suggest register_vocabulary |
| `CHUNK_ROTATION_FAILED` | Cannot create next instance chunk | Return error with current chunk details |

---

## Patterns & Anti-Patterns

| Pattern | When | Key Actions |
|---------|------|-------------|
| Top-down discovery | New domain | discover_nodes first, then properties, then instances |
| Vocabulary-first | Controlled terms needed | register_vocabulary before create_instances |
| Critique loop | Quality gate | Run critique_validate after each batch of instances |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip validation | Inconsistent ontology | Always critique_validate before declaring done |
| Deep hierarchies | Over-engineering | Keep depth_limit <= 3 unless domain requires it |
| Manual ID assignment | ID collision risk | Let ontology_ops.py generate IDs automatically |

---

## Examples

See `references/examples.md` for worked examples of each operation.
