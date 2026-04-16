---
name: x-ipe-knowledge-constructor-user-manual
description: Domain expert for user manual construction. Provides framework, rubric, knowledge gap analysis, and structure filling via a 4-operation interface. Triggers on operations like "provide_framework", "design_rubric", "request_knowledge", "fill_structure".
---

# Constructor User Manual — Knowledge Skill

## Purpose

AI Agents follow this skill to perform user manual construction operations:
1. Provide a domain-appropriate framework (8-section layout with app-type mixins)
2. Design measurable rubric criteria per framework section
3. Identify knowledge gaps and generate extraction requests
4. Fill the framework structure with gathered knowledge into a completed draft

---

## Important Notes

BLOCKING: Operations are stateless services — the assistant orchestrator passes full context per call. Do NOT maintain internal state across operations.
CRITICAL: Each operation MUST define typed input/output contracts with a `writes_to` field.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.
CRITICAL: This skill writes ONLY to `.working/` paths. Promotion to persistent memory is handled by `x-ipe-knowledge-keeper-memory`.

---

## About

This skill serves as the domain expert for user manual construction. It knows the structure of user manuals (8 standard sections), the quality criteria for each section, and what knowledge is needed to fill them. The Knowledge Librarian orchestrator calls its 4 operations in sequence to drive the construction pipeline.

**Key Concepts:**
- **Operation Contract** — Each operation declares its input types, output types, writes_to path, and constraints. The orchestrator uses this contract to plan execution.
- **Stateless Service** — The skill receives all needed context from the orchestrator per call. No cross-operation memory.
- **writes_to Discipline** — Every operation writes to `x-ipe-docs/memory/.working/{subpath}/` only. No persistent writes.
- **Domain Templates** — 6 templates in `templates/` define the user manual structure, extraction prompts, rubric criteria, and app-type overlays.
- **8-Section Layout** — Standard user manual sections: Overview, Installation & Setup, Getting Started, Core Features, Common Workflows, Configuration, Troubleshooting, FAQ & Reference.

---

## When to Use

```yaml
triggers:
  - "Provide a user manual framework for an application"
  - "Design quality rubric for a user manual"
  - "Identify knowledge gaps in a user manual draft"
  - "Fill user manual structure with gathered knowledge"

not_for:
  - "Orchestration decisions (belongs to x-ipe-assistant-knowledge-librarian-DAO)"
  - "Extracting knowledge from web or memory (belongs to extractor skills)"
  - "Persisting finished drafts (belongs to x-ipe-knowledge-keeper-memory)"
  - "Ontology registration (belongs to x-ipe-knowledge-ontology-builder)"
```

---

## Input Parameters

```yaml
input:
  operation: "provide_framework | design_rubric | request_knowledge | fill_structure"
  context:
    # For provide_framework:
    request_context:
      app_name: "string"
      app_type: "web | cli | mobile"
      user_goal: "string"
      source_paths: "string[]"
    output_format: "markdown | split"
    # For design_rubric:
    framework: "dict"
    overview: "string"
    user_request: "string"
    # For request_knowledge:
    framework: "dict"
    current_state: "dict"
    rubric: "dict"
    # For fill_structure:
    framework: "dict"
    gathered_knowledge: "object[]"
    rubric: "dict"
```

### Input Initialization

BLOCKING: All input fields with non-trivial initialization MUST be documented here.

```xml
<input_init>
  <field name="operation" source="Assistant orchestrator specifies which operation to perform">
    <validation>Must be one of: provide_framework, design_rubric, request_knowledge, fill_structure</validation>
  </field>
  <field name="context.request_context" source="Required for provide_framework">
    <validation>Must contain app_name, app_type, user_goal, source_paths[]</validation>
  </field>
  <field name="context.request_context.app_type" source="Determines which mixin template to apply">
    <validation>Must be one of: web, cli, mobile</validation>
  </field>
  <field name="context.framework" source="Required for design_rubric, request_knowledge, fill_structure">
    <validation>Must be a valid framework_document from provide_framework</validation>
  </field>
  <field name="context.rubric" source="Required for request_knowledge and fill_structure">
    <validation>Must be a valid rubric from design_rubric</validation>
  </field>
  <field name="context.gathered_knowledge" source="Required for fill_structure">
    <validation>Array of {section_id, content, source, metadata} objects</validation>
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
    <name>Operation-specific context provided</name>
    <verification>All required context fields for the specified operation are present</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Working directory accessible</name>
    <verification>x-ipe-docs/memory/.working/ exists and is writable</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: provide_framework

> **Contract:**
> - **Input:** request_context: {app_name: string, app_type: "web"|"cli"|"mobile", user_goal: string, source_paths: string[]}, output_format: "markdown"|"split"
> - **Output:** framework_document: dict, toc_structure: {id: string, title: string, stubs: string, depth: number}[]
> - **Writes To:** x-ipe-docs/memory/.working/framework/
> - **Constraints:** Load playbook-template.md; select mixin by app_type; adapt to request_context; return framework with section stubs

**When:** Orchestrator needs a structured user manual outline tailored to the target application.

```xml
<operation name="provide_framework">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: request_context (app_name, app_type, user_goal, source_paths[]), output_format
      2. LOAD templates/playbook-template.md as the base 8-section layout
      3. DETERMINE which mixin to apply based on app_type:
         - web → LOAD templates/mixin-web.md
         - cli → LOAD templates/mixin-cli.md
         - mobile → LOAD templates/mixin-mobile.md
    </action>
    <output>Base template and mixin loaded, request context understood</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE app_type is one of: web, cli, mobile
      2. VALIDATE app_name is non-empty
      3. VALIDATE source_paths[] is non-empty array
      4. CHECK output_format defaults to "markdown" if not specified
    </action>
    <constraints>
      - BLOCKING: Invalid app_type → return error INVALID_APP_TYPE
      - BLOCKING: Missing app_name → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated, template selection confirmed</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. MERGE mixin sections into base playbook template:
         - Insert mixin Additional Sections at specified positions
         - Apply mixin Section Overlay Prompts to augment existing sections
      2. ADAPT section titles and stubs to request_context:
         - Replace {App Name} placeholders with app_name
         - Tailor subsection guidance to user_goal
      3. BUILD toc_structure array with {id, title, stubs, depth} per section
      4. FORMAT as output_format (inline markdown or split file references)
    </action>
    <output>framework_document with adapted sections, toc_structure array</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY framework contains all 8 base sections plus mixin additions
      2. VERIFY toc_structure entries match framework sections
      3. VERIFY no {placeholder} tokens remain unresolved
      4. IF any check fails → return error with details
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE framework_document to x-ipe-docs/memory/.working/framework/{app_name}-framework.md
      2. RETURN operation_output:
         - success: true
         - operation: "provide_framework"
         - result: { framework_document, toc_structure }
         - writes_to: "x-ipe-docs/memory/.working/framework/"
         - errors: []
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
> - **Constraints:** Load acceptance-criteria.md; define measurable criteria per section; weight by user emphasis

**When:** Orchestrator needs measurable quality criteria to evaluate extracted knowledge.

```xml
<operation name="design_rubric">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: framework (from provide_framework), overview, user_request
      2. LOAD templates/acceptance-criteria.md as base rubric definitions
      3. IDENTIFY which sections the user emphasizes in user_request
    </action>
    <output>Framework sections and base criteria loaded, user priorities identified</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE framework is a valid framework_document (has sections)
      2. VALIDATE overview is non-empty
      3. VALIDATE user_request is non-empty
    </action>
    <constraints>
      - BLOCKING: Invalid or empty framework → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. FOR EACH section in framework:
         a. MAP [REQ] items from acceptance-criteria.md to measurable rubric_metrics
         b. SET weight based on user emphasis (high=3, normal=2, low=1)
         c. SET threshold from acceptance criteria (e.g., "≥3 features documented")
         d. COMPILE acceptance_criteria checks from [REQ] + [OPT] items
      2. ADJUST weights: sections explicitly mentioned in user_request get weight=3
      3. ENSURE all rubric_metrics have numeric weight and testable threshold
    </action>
    <output>rubric_metrics[] and acceptance_criteria[] per section</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY every framework section has at least one rubric_metric entry
      2. VERIFY weights are numeric (1-3 range)
      3. VERIFY thresholds are testable (not vague)
      4. IF any check fails → return error with details
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE rubric to x-ipe-docs/memory/.working/rubric/{app_name}-rubric.md
      2. RETURN operation_output:
         - success: true
         - operation: "design_rubric"
         - result: { rubric_metrics, acceptance_criteria }
         - writes_to: "x-ipe-docs/memory/.working/rubric/"
         - errors: []
    </action>
    <output>Rubric written, result returned to orchestrator</output>
  </phase_5>

</operation>
```

### Operation: request_knowledge

> **Contract:**
> - **Input:** framework: dict, current_state: {filled_sections: string[], empty_sections: string[], partial_sections: string[]}, rubric: dict
> - **Output:** knowledge_requests: {target_section: string, what_needed: string, suggested_extractor: "extractor-web"|"extractor-memory", priority: number}[]
> - **Writes To:** x-ipe-docs/memory/.working/plan/
> - **Constraints:** Walk framework sections; compare to current_state; generate specific requests per gap; set suggested_extractor; prioritize by rubric weight; return empty array if no gaps

**When:** Orchestrator needs to know what knowledge to gather next.

```xml
<operation name="request_knowledge">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: framework, current_state, rubric
      2. LOAD templates/collection-template.md for per-section extraction prompt patterns
      3. BUILD section inventory from framework toc_structure
    </action>
    <output>Framework sections, current state, and extraction prompts loaded</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE framework has sections
      2. VALIDATE current_state has filled_sections, empty_sections, partial_sections
      3. VALIDATE rubric has metrics for each section
    </action>
    <constraints>
      - BLOCKING: Missing current_state → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. FOR EACH section in framework:
         a. IF section in current_state.filled_sections → SKIP
         b. IF section in empty_sections or partial_sections:
            - READ extraction prompts from collection-template.md for this section
            - GENERATE specific what_needed description (not vague)
            - SET suggested_extractor:
              * "extractor-web" for content needing live source analysis (code, UI, API)
              * "extractor-memory" for content that may exist in existing knowledge base
            - SET priority from rubric weight (higher weight = higher priority)
            - ADD to knowledge_requests[]
      2. SORT knowledge_requests by priority descending
      3. IF no gaps found → return empty knowledge_requests[]
    </action>
    <output>knowledge_requests[] with targeted extraction requests</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY each request has target_section, what_needed, suggested_extractor, priority
      2. VERIFY suggested_extractor is "extractor-web" or "extractor-memory"
      3. VERIFY what_needed is specific (not "get more info")
      4. IF any check fails → return error with details
    </action>
    <output>Output validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE plan to x-ipe-docs/memory/.working/plan/{app_name}-plan.md
      2. RETURN operation_output:
         - success: true
         - operation: "request_knowledge"
         - result: { knowledge_requests }
         - writes_to: "x-ipe-docs/memory/.working/plan/"
         - errors: []
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
> - **Constraints:** Map gathered knowledge to framework sections; mark incomplete sections with [INCOMPLETE: reason]; validate against rubric; do NOT write to persistent memory

**When:** Orchestrator has gathered knowledge and needs it assembled into the user manual structure.

```xml
<operation name="fill_structure">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: framework, gathered_knowledge[], rubric
      2. INDEX gathered_knowledge by section_id for fast lookup
      3. LOAD framework toc_structure for section ordering
    </action>
    <output>Knowledge indexed, framework structure loaded</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE framework has sections
      2. VALIDATE gathered_knowledge is non-empty array with section_id and content
      3. VALIDATE rubric has acceptance_criteria for evaluation
    </action>
    <constraints>
      - BLOCKING: Empty gathered_knowledge → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Input validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. FOR EACH section in framework (ordered by toc_structure):
         a. FIND matching entries in gathered_knowledge by section_id
         b. IF content found:
            - MAP content into the section template from playbook-template.md
            - VALIDATE against rubric acceptance_criteria for this section
            - IF rubric threshold NOT met → append [INCOMPLETE: {specific reason}]
         c. IF no content found:
            - INSERT section stub with [INCOMPLETE: No knowledge gathered for this section]
      2. ASSEMBLE completed_draft following playbook-template.md structure
      3. ADD Table of Contents at top with section links
    </action>
    <output>completed_draft with all sections mapped</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY completed_draft contains all framework sections
      2. VERIFY incomplete sections are marked with [INCOMPLETE: reason]
      3. VERIFY Table of Contents links match actual sections
      4. COUNT completeness: sections_complete / total_sections
      5. IF any structural check fails → return error with details
    </action>
    <output>Output validated, completeness score calculated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE draft to x-ipe-docs/memory/.working/draft/{app_name}-user-manual.md
      2. RETURN operation_output:
         - success: true
         - operation: "fill_structure"
         - result: { completed_draft, completeness_score }
         - writes_to: "x-ipe-docs/memory/.working/draft/"
         - errors: []
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
    framework_document: "dict"
    toc_structure: "object[]"
    # design_rubric:
    rubric_metrics: "object[]"
    acceptance_criteria: "object[]"
    # request_knowledge:
    knowledge_requests: "object[]"
    # fill_structure:
    completed_draft: "string"
    completeness_score: "number"
    writes_to: "x-ipe-docs/memory/.working/{subpath}/"
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
    <name>No persistent writes</name>
    <verification>No files written outside x-ipe-docs/memory/.working/</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | Operation name not one of the 4 defined | Return error listing valid operations |
| `INVALID_APP_TYPE` | app_type not web/cli/mobile (provide_framework) | Return error listing valid types |
| `INPUT_VALIDATION_FAILED` | Required input missing or wrong type | Return error with specific field and expected type |
| `TEMPLATE_NOT_FOUND` | Domain template file missing from templates/ | Return error with expected template path |
| `WRITE_FAILED` | Cannot write to .working/ path | Return error; orchestrator decides retry or alternate path |
| `QUALITY_THRESHOLD_NOT_MET` | Output below rubric quality bar | Return partial results with quality metrics; orchestrator decides |

---

## Patterns & Anti-Patterns

| Pattern | When | Key Actions |
|---------|------|-------------|
| Incremental fill | Large knowledge base | Fill sections iteratively, validate rubric after each pass |
| Mixin composition | Multi-platform app | Stack platform mixins (web+mobile) in provide_framework |
| Gap-first planning | Cold start | Run request_knowledge before any extraction to prioritize |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip rubric | No quality gate | Always design_rubric before fill_structure |
| Persist from constructor | Bypasses librarian | Write to .working/ only; let librarian promote |
| Monolithic fill | Hard to iterate | Fill per-section, validate incrementally |

---

## Examples

See `references/examples.md` for worked examples of each operation.
