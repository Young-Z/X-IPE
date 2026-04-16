---
name: x-ipe-knowledge-constructor-notes
description: Domain expert for general knowledge notes construction. Implements the 4-operation constructor interface (provide_framework, design_rubric, request_knowledge, fill_structure) for notes-type knowledge bases with flexible numbered hierarchy. Triggers on operations like "provide_framework", "design_rubric", "request_knowledge", "fill_structure".
---

# Constructor Notes — Knowledge Skill

## Purpose

AI Agents follow this skill to construct general knowledge notes:
1. Scaffold a flexible framework from notes templates (provide_framework)
2. Design measurable quality rubrics per section (design_rubric)
3. Generate gap-driven extraction requests (request_knowledge)
4. Assemble gathered knowledge into a completed draft (fill_structure)

---

## Important Notes

BLOCKING: Operations are stateless services — the assistant orchestrator passes full context per call. Do NOT maintain internal state across operations.
CRITICAL: Each operation MUST define typed input/output contracts with a `writes_to` field.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.
CRITICAL: This skill writes ONLY to `.working/` subdirectories — never to persistent memory. Promotion to persistent tiers is handled by `keeper-memory`.

---

## About

This skill serves as the domain expert for general-purpose knowledge notes. It knows how to structure flexible, numbered section hierarchies covering topics from technical documentation to research summaries. The Librarian assistant calls its operations in sequence to build knowledge notes from raw sources.

**Key Concepts:**
- **Operation Contract** — Each operation declares its input types, output types, writes_to path, and constraints. The orchestrator uses this contract to plan execution.
- **Stateless Service** — The skill receives all needed context from the orchestrator per call. No cross-operation memory.
- **writes_to Discipline** — Every operation declares which `.working/` sub-path it writes to, enabling the orchestrator to predict side effects and coordinate parallel operations.
- **Flexible Hierarchy** — Notes use a numbered section scheme (01–99 top-level, 0101–0199 nested) that adapts to topic complexity rather than a fixed section list.

---

## When to Use

```yaml
triggers:
  - "Scaffold a framework for a notes-type knowledge base"
  - "Design quality rubric for notes sections"
  - "Generate extraction requests to fill notes gaps"
  - "Assemble gathered knowledge into notes draft"

not_for:
  - "User manual construction (use constructor-user-manual)"
  - "App reverse engineering (use constructor-app-reverse-engineering)"
  - "Persistent memory writes (use keeper-memory)"
  - "Orchestration decisions (use x-ipe-assistant-knowledge-librarian-DAO)"
```

---

## Input Parameters

```yaml
input:
  operation: "provide_framework | design_rubric | request_knowledge | fill_structure"
  context:
    # For provide_framework:
    request_context:
      topic: "string"              # Subject of the knowledge base
      scope: "string"              # breadth/depth description
      depth: "string"              # overview | standard | deep-dive
      source_paths: "string[]"     # Paths to source material
    output_format: "string"        # markdown (default)
    # For design_rubric:
    framework: "dict"              # From provide_framework
    overview: "string"             # Summary of the target topic
    user_request: "string"         # Original user goal/emphasis
    # For request_knowledge:
    framework: "dict"              # From provide_framework
    current_state: "dict"          # {filled_sections[], empty_sections[], partial_sections[]}
    rubric: "dict"                 # From design_rubric
    # For fill_structure:
    framework: "dict"              # From provide_framework
    gathered_knowledge: "object[]" # [{section_id, content, source, metadata}]
    rubric: "dict"                 # From design_rubric
```

### Input Initialization

BLOCKING: All input fields with non-trivial initialization MUST be documented here.

```xml
<input_init>
  <field name="operation" source="Assistant orchestrator specifies which operation to perform">
    <validation>Must be one of: provide_framework, design_rubric, request_knowledge, fill_structure</validation>
  </field>
  <field name="context.request_context" source="Required for provide_framework">
    <validation>Must contain topic (non-empty string) and source_paths (array)</validation>
  </field>
  <field name="context.framework" source="Required for design_rubric, request_knowledge, fill_structure">
    <validation>Must be a valid framework_document from provide_framework</validation>
  </field>
  <field name="context.current_state" source="Required for request_knowledge">
    <validation>Must contain filled_sections, empty_sections, partial_sections arrays</validation>
  </field>
  <field name="context.gathered_knowledge" source="Required for fill_structure">
    <validation>Array of objects each with section_id, content, source</validation>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Operation specified</name>
    <verification>input.operation matches one of the 4 defined operations</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Operation-specific context present</name>
    <verification>provide_framework: request_context; design_rubric: framework+overview+user_request; request_knowledge: framework+current_state+rubric; fill_structure: framework+gathered_knowledge+rubric</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Working directory accessible</name>
    <verification>x-ipe-docs/memory/.working/ exists or can be created</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: provide_framework

> **Contract:**
> - **Input:** request_context: {topic: string, scope: string, depth: string, source_paths: string[]}, output_format: string
> - **Output:** framework_document: dict, toc_structure: {id: string, title: string, stubs: string, depth: number}[]
> - **Writes To:** x-ipe-docs/memory/.working/framework/
> - **Constraints:** Load general-template.md from templates/; adapt sections to topic complexity; return framework with section stubs (placeholder content); depth "overview" → fewer sections, "deep-dive" → more sub-sections

**When:** Orchestrator needs to scaffold a structural outline for a notes knowledge base.

```xml
<operation name="provide_framework">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: request_context (topic, scope, depth, source_paths), output_format
      2. LOAD general-template.md from templates/ folder
      3. SCAN source_paths (if provided) to understand content scope
    </action>
    <output>Input context understood, template loaded, scope assessed</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE topic is non-empty string
      2. VALIDATE depth is one of: overview, standard, deep-dive
      3. CHECK source_paths exist (if provided)
      4. DETERMINE section count: overview → 3-4 sections, standard → 5-7, deep-dive → 7+
    </action>
    <constraints>
      - BLOCKING: Empty topic → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated, section depth determined</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. GENERATE section hierarchy from general-template.md structure:
         - 01.introduction.md — What is it? Why does it matter?
         - 02.core-concepts.md — Key definitions, terminology
         - 03.key-insights/ — Main findings (hierarchical sub-sections if deep-dive)
         - 04.practical-applications.md — How to apply (skip for overview depth)
         - 05.examples-and-patterns.md — Concrete examples (skip for overview depth)
         - 06.references-and-sources.md — Citations, further reading
         - 07.open-questions.md — Unresolved items
      2. ADAPT hierarchy to topic: add/remove sections, adjust sub-section count
      3. GENERATE toc_structure[] with {id, title, stubs, depth} per section
      4. CREATE framework_document with section stubs containing placeholder descriptions
    </action>
    <output>Framework document and TOC structure generated</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VALIDATE framework_document has at least 3 sections
      2. VALIDATE toc_structure matches framework_document sections
      3. VALIDATE every section has a stub (no empty entries)
      4. IF validation fails → return error with details
    </action>
    <output>Framework validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE framework_document to x-ipe-docs/memory/.working/framework/{topic-slug}-framework.md
      2. RETURN operation_output with framework_document, toc_structure, writes_to path
    </action>
    <output>Framework written, result returned to orchestrator</output>
  </phase_5>

</operation>
```

### Operation: design_rubric

> **Contract:**
> - **Input:** framework: dict, overview: string, user_request: string
> - **Output:** rubric_metrics: {section_id: string, criteria: string, weight: number, threshold: string}[], acceptance_criteria: {section_id: string, checks: string[]}[]
> - **Writes To:** x-ipe-docs/memory/.working/rubric/
> - **Constraints:** Measurable criteria per section; weight by user emphasis; weights sum to 1.0; each criterion must be testable

**When:** Orchestrator needs quality criteria to evaluate the completed notes.

```xml
<operation name="design_rubric">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: framework (section list), overview (topic summary), user_request
      2. IDENTIFY which sections the user emphasizes in user_request
      3. NOTE framework depth and section count
    </action>
    <output>Input context understood, user priorities identified</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE framework is non-empty dict with sections
      2. VALIDATE overview is non-empty string
      3. VALIDATE user_request is non-empty string
    </action>
    <constraints>
      - BLOCKING: Missing framework → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. FOR EACH section in framework:
         a. DEFINE completeness criteria (e.g., "≥3 key terms defined" for core-concepts)
         b. DEFINE accuracy criteria (e.g., "All claims cite a source")
         c. ASSIGN weight: higher for user-emphasized sections, baseline for others
         d. SET threshold: minimum acceptable level
      2. GENERATE acceptance_criteria[] with testable checks per section
      3. NORMALIZE weights to sum to 1.0
    </action>
    <output>Rubric metrics and acceptance criteria generated</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VALIDATE every framework section has at least one rubric metric
      2. VALIDATE weights sum to approximately 1.0
      3. VALIDATE each criterion is measurable (not vague)
      4. IF validation fails → return error with details
    </action>
    <output>Rubric validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE rubric to x-ipe-docs/memory/.working/rubric/{topic-slug}-rubric.md
      2. RETURN operation_output with rubric_metrics[], acceptance_criteria[], writes_to path
    </action>
    <output>Rubric written, result returned to orchestrator</output>
  </phase_5>

</operation>
```

### Operation: request_knowledge

> **Contract:**
> - **Input:** framework: dict, current_state: {filled_sections: string[], empty_sections: string[], partial_sections: string[]}, rubric: dict
> - **Output:** knowledge_requests: {target_section: string, what_needed: string, suggested_extractor: string, priority: number}[]
> - **Writes To:** x-ipe-docs/memory/.working/plan/
> - **Constraints:** Walk all framework sections; compare to current_state; suggested_extractor is "extractor-web" or "extractor-memory"; prioritize by rubric weight; return empty array if no gaps

**When:** Orchestrator needs to know what knowledge is missing and how to obtain it.

```xml
<operation name="request_knowledge">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: framework (all sections), current_state, rubric
      2. LIST all framework section IDs
      3. CATEGORIZE sections: filled, empty, partial (from current_state)
    </action>
    <output>Section status mapped</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE framework contains sections
      2. VALIDATE current_state has filled/empty/partial arrays
      3. VALIDATE rubric has metrics for framework sections
      4. IF all sections in filled_sections → return empty knowledge_requests[]
    </action>
    <constraints>
      - BLOCKING: Missing framework or current_state → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated, gap analysis ready</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. FOR EACH section in empty_sections + partial_sections:
         a. DETERMINE what_needed: specific description of missing content
         b. SELECT suggested_extractor:
            - "extractor-web" if section needs external sources (references, examples from web)
            - "extractor-memory" if section can be filled from existing KB
         c. SET priority from rubric weight (higher weight → higher priority)
      2. SORT knowledge_requests by priority (descending)
    </action>
    <output>Knowledge requests generated and prioritized</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VALIDATE each request has target_section, what_needed, suggested_extractor, priority
      2. VALIDATE suggested_extractor is "extractor-web" or "extractor-memory"
      3. VALIDATE no duplicate target_section entries
      4. IF validation fails → return error with details
    </action>
    <output>Requests validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE requests to x-ipe-docs/memory/.working/plan/{topic-slug}-plan.md
      2. RETURN operation_output with knowledge_requests[], writes_to path
    </action>
    <output>Plan written, result returned to orchestrator</output>
  </phase_5>

</operation>
```

### Operation: fill_structure

> **Contract:**
> - **Input:** framework: dict, gathered_knowledge: {section_id: string, content: string, source: string, metadata: dict}[], rubric: dict
> - **Output:** completed_draft: string
> - **Writes To:** x-ipe-docs/memory/.working/draft/
> - **Constraints:** Map knowledge to framework sections; mark gaps with [INCOMPLETE: reason]; validate against rubric; generate overview.md using overview-template.md; do NOT write to persistent memory

**When:** Orchestrator has gathered knowledge and needs it assembled into a draft.

```xml
<operation name="fill_structure">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: framework, gathered_knowledge[], rubric
      2. LOAD overview-template.md from templates/ folder
      3. MAP each gathered_knowledge item to its target section_id
    </action>
    <output>Input loaded, knowledge-to-section mapping created</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE framework is non-empty
      2. VALIDATE gathered_knowledge is array with section_id and content per item
      3. VALIDATE rubric has acceptance criteria
      4. IDENTIFY sections with no matching gathered knowledge
    </action>
    <constraints>
      - BLOCKING: Missing framework → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated, gap sections identified</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. FOR EACH section in framework:
         a. IF gathered_knowledge covers section → FILL section with content
         b. IF section partially covered → FILL available content + mark [INCOMPLETE: {reason}]
         c. IF section has no knowledge → mark entire section [INCOMPLETE: no knowledge gathered]
      2. APPEND references footer to each section file (source URLs per section)
      3. GENERATE overview.md using overview-template.md:
         - Title, description, table of contents, summary stats, consolidated references
      4. VALIDATE each filled section against rubric criteria
      5. ASSEMBLE completed_draft as full document string
    </action>
    <output>Draft assembled with gaps marked</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VALIDATE completed_draft is non-empty string
      2. CHECK rubric acceptance criteria per section → note pass/fail
      3. COUNT incomplete sections → include in output metadata
      4. IF completed_draft is entirely incomplete → return error INSUFFICIENT_KNOWLEDGE
    </action>
    <output>Draft validated against rubric</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE completed_draft to x-ipe-docs/memory/.working/draft/{topic-slug}/
         - overview.md + individual section files
      2. RETURN operation_output with completed_draft, rubric_score, incomplete_count, writes_to path
    </action>
    <output>Draft written, result returned to orchestrator</output>
  </phase_5>

</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  operation: "provide_framework | design_rubric | request_knowledge | fill_structure"
  result:
    # provide_framework:
    framework_document: dict
    toc_structure: object[]
    # design_rubric:
    rubric_metrics: object[]
    acceptance_criteria: object[]
    # request_knowledge:
    knowledge_requests: object[]
    # fill_structure:
    completed_draft: string
    rubric_score: number
    incomplete_count: number
    writes_to: "x-ipe-docs/memory/.working/{sub-path}/"
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
    <name>Output written to declared .working/ path</name>
    <verification>File exists at writes_to path with expected content</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output matches contract types</name>
    <verification>Returned data matches the operation's declared output types</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No persistent memory writes</name>
    <verification>All writes are within x-ipe-docs/memory/.working/ only</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | Operation name not one of the 4 defined | Return error listing valid operations |
| `INPUT_VALIDATION_FAILED` | Required input missing or wrong type | Return error with specific field and expected type |
| `TEMPLATE_NOT_FOUND` | Template file missing from templates/ | Return error with expected path |
| `WRITE_FAILED` | Cannot write to .working/ path | Return error; orchestrator decides retry or alternate path |
| `INSUFFICIENT_KNOWLEDGE` | fill_structure received no usable knowledge | Return error; orchestrator may re-run request_knowledge |
| `QUALITY_THRESHOLD_NOT_MET` | Draft fails rubric criteria | Return partial results with rubric_score; orchestrator decides |

---

## Patterns & Anti-Patterns

| Pattern | When | Key Actions |
|---------|------|-------------|
| Incremental fill | Large knowledge base | Fill sections iteratively, validate rubric after each pass |
| Depth adaptation | Varying complexity | Let provide_framework auto-select overview/standard/deep-dive |
| Gap-first planning | Cold start | Run request_knowledge before any extraction to prioritize |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip rubric | No quality gate | Always design_rubric before fill_structure |
| Persist from constructor | Bypasses librarian | Write to .working/ only; let librarian promote |
| Fixed depth | Over/under-engineering | Use depth adaptation rules from general-template |

---

## Examples

See `references/examples.md` for worked examples of each operation.
