---
name: x-ipe-knowledge-constructor-app-reverse-engineering
description: Domain expert for application reverse engineering reports. Provides framework scaffolding, rubric design, knowledge-gap analysis, and draft assembly via the 4-operation constructor interface. Triggers on operations like "provide_framework", "design_rubric", "request_knowledge", "fill_structure".
---

# Constructor App Reverse Engineering — Knowledge Skill

## Purpose

AI Agents follow this skill to perform application reverse engineering report construction:
1. Scaffold a domain framework mapping 8 RE sections to `x-ipe-tool-rev-eng-*` sub-skills
2. Design quality rubrics with measurable criteria per RE section
3. Identify knowledge gaps and suggest extraction sub-skills to fill them
4. Assemble gathered RE knowledge into a structured draft report

---

## Important Notes

BLOCKING: Operations are stateless services — the assistant orchestrator passes full context per call. Do NOT maintain internal state across operations.
CRITICAL: Each operation MUST define typed input/output contracts with a `writes_to` field.
CRITICAL: This skill is NOT directly task-matched. It is called by the Knowledge Librarian assistant (`x-ipe-assistant-knowledge-librarian-DAO`) or another assistant orchestrator.
CRITICAL: This skill does NOT write to persistent memory — only to `.working/` paths. Promotion to persistent memory is handled by `x-ipe-knowledge-keeper-memory`.
CRITICAL: This skill does NOT execute RE sub-skills. It generates extraction requests that reference them; the Librarian dispatches.

---

## About

This skill serves as the domain expert for application reverse engineering reports. It understands the 8 standard RE sections, knows which `x-ipe-tool-rev-eng-*` sub-skill handles each section, and provides domain-specific templates (language mixins and repo-type mixins) for framework adaptation.

**Key Concepts:**
- **Operation Contract** — Each operation declares its input types, output types, writes_to path, and constraints. The orchestrator uses this contract to plan execution.
- **Stateless Service** — The skill receives all needed context from the orchestrator per call. No cross-operation memory.
- **writes_to Discipline** — Every operation declares which `.working/` path it writes to, enabling the orchestrator to predict side effects and coordinate parallel operations.
- **Section → Sub-Skill Mapping** — Each of the 8 RE sections maps to a specific `x-ipe-tool-rev-eng-*` sub-skill. This mapping drives both framework scaffolding and extraction planning.
- **Mixin Composition** — Templates are composed from a base playbook + language mixin + repo-type mixin, enabling cross-product coverage (e.g., Python × Microservices).

**RE Section → Sub-Skill Map:**

| # | Section | Sub-Skill |
|---|---------|-----------|
| 1 | Architecture Recovery | `x-ipe-tool-rev-eng-architecture-recovery` |
| 2 | API Contract Extraction | `x-ipe-tool-rev-eng-api-contract-extraction` |
| 3 | Business Logic Mapping | `x-ipe-tool-rev-eng-business-logic-mapping` |
| 4 | Data Model Analysis | `x-ipe-tool-rev-eng-data-model-analysis` |
| 5 | Dependency Analysis | `x-ipe-tool-rev-eng-dependency-analysis` |
| 6 | Infrastructure Analysis | `x-ipe-tool-rev-eng-infrastructure-analysis` |
| 7 | Security & Auth Patterns | `x-ipe-tool-rev-eng-security-auth-pattern` |
| 8 | Testing Strategy | `x-ipe-tool-rev-eng-testing-strategy` |

---

## When to Use

```yaml
triggers:
  - "Build an application reverse engineering report framework"
  - "Design quality rubric for an RE report"
  - "Identify knowledge gaps in a partially-filled RE report"
  - "Assemble gathered RE knowledge into a structured draft"

not_for:
  - "Orchestrating the full extraction pipeline (use x-ipe-assistant-knowledge-librarian-DAO)"
  - "Executing actual code analysis (use x-ipe-tool-rev-eng-* sub-skills)"
  - "Writing to persistent memory (use x-ipe-knowledge-keeper-memory)"
  - "Web or memory search extraction (use extractor-web / extractor-memory)"
```

---

## Input Parameters

```yaml
input:
  operation: "provide_framework | design_rubric | request_knowledge | fill_structure"
  context:
    # provide_framework
    request_context:
      app_name: "string"
      repo_path: "string"
      language: "string"           # go | java | javascript | typescript | python
      repo_type: "string"          # single-module | multi-module | monorepo | microservices
      source_paths: "string[]"
    output_format: "string"        # default: "markdown"
    # design_rubric
    framework: "dict"              # From provide_framework output
    overview: "string"
    user_request: "string"
    # request_knowledge
    framework: "dict"              # From provide_framework output
    current_state: "dict"          # {filled_sections[], empty_sections[], partial_sections[]}
    rubric: "dict"                 # From design_rubric output
    # fill_structure
    framework: "dict"              # From provide_framework output
    gathered_knowledge: "object[]" # [{section_id, content, source, metadata}]
    rubric: "dict"                 # From design_rubric output
```

### Input Initialization

BLOCKING: All input fields with non-trivial initialization MUST be documented here.

```xml
<input_init>
  <field name="operation" source="Assistant orchestrator specifies which operation to perform">
    <validation>Must be one of: provide_framework, design_rubric, request_knowledge, fill_structure</validation>
  </field>
  <field name="context.request_context" source="Required for provide_framework">
    <validation>Must contain app_name, repo_path, language, repo_type, source_paths[]</validation>
  </field>
  <field name="context.request_context.language" source="Detected or specified by orchestrator">
    <validation>Supported: go, java, javascript, typescript, python. Unsupported languages use base playbook only</validation>
  </field>
  <field name="context.request_context.repo_type" source="Detected or specified by orchestrator">
    <validation>Supported: single-module, multi-module, monorepo, microservices</validation>
  </field>
  <field name="context.framework" source="Required for design_rubric, request_knowledge, fill_structure">
    <validation>Must be a valid framework_document from provide_framework</validation>
  </field>
  <field name="context.rubric" source="Required for request_knowledge, fill_structure">
    <validation>Must be a valid rubric from design_rubric</validation>
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
    <verification>provide_framework: request_context present; design_rubric: framework+overview; request_knowledge: framework+current_state+rubric; fill_structure: framework+gathered_knowledge+rubric</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Language/repo_type valid (provide_framework only)</name>
    <verification>language and repo_type are recognized values or gracefully defaulted</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: provide_framework

> **Contract:**
> - **Input:** request_context: {app_name: string, repo_path: string, language: string, repo_type: string, source_paths: string[]}, output_format: string
> - **Output:** framework_document: dict, toc_structure: {id: string, title: string, sub_skill: string, stubs: string[], depth: int}[]
> - **Writes To:** x-ipe-docs/memory/.working/framework/
> - **Constraints:** Load playbook-template.md; select language mixin + repo-type mixin; map all 8 sections to sub-skills; return framework with section stubs

**When:** Orchestrator needs a domain-specific framework for a new RE report.

```xml
<operation name="provide_framework">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: request_context (app_name, repo_path, language, repo_type, source_paths[])
      2. LOAD base playbook from templates/playbook-template.md
      3. IDENTIFY applicable mixins: language mixin (templates/mixin-{language}.md) + repo-type mixin (templates/mixin-{repo_type}.md)
    </action>
    <output>Base playbook loaded, applicable mixins identified</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE language is supported (go|java|javascript|typescript|python) — if not, skip language mixin
      2. VALIDATE repo_type is supported (single-module|multi-module|monorepo|microservices) — if not, skip repo-type mixin
      3. VALIDATE source_paths[] are non-empty
    </action>
    <constraints>
      - BLOCKING: Empty source_paths → return error INPUT_VALIDATION_FAILED
      - WARNING: Unsupported language → proceed with base playbook only, log warning
    </constraints>
    <output>Inputs validated, mixin selection confirmed</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. COMPOSE framework by merging: base playbook + language mixin overlays + repo-type mixin overlays
      2. For each of the 8 RE sections, BUILD section stub with:
         - Section title and subsection structure from playbook
         - Mapped sub-skill name (from Section → Sub-Skill Map)
         - Language-specific overlay prompts (from language mixin)
         - Repo-type-specific overlay prompts and additional subsections (from repo-type mixin)
      3. BUILD toc_structure[] with {id, title, sub_skill, stubs, depth} per section
      4. ADAPT section emphasis based on request_context (e.g., microservices → weight inter-service sections higher)
    </action>
    <output>Composed framework_document with 8 RE sections and toc_structure</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY all 8 RE sections are present in framework_document
      2. VERIFY each section maps to its correct x-ipe-tool-rev-eng-* sub-skill
      3. VERIFY toc_structure has 8 entries
      4. IF any verification fails → return error with details
    </action>
    <output>Framework validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE framework_document to x-ipe-docs/memory/.working/framework/{app_name}-re-framework.md
      2. RETURN operation_output with success, framework_document, toc_structure
    </action>
    <output>Framework written and returned</output>
  </phase_5>

</operation>
```

### Operation: design_rubric

> **Contract:**
> - **Input:** framework: dict, overview: string, user_request: string
> - **Output:** rubric_metrics: {section_id: string, criteria: string, weight: float, threshold: string}[], acceptance_criteria: {section_id: string, checks: string[]}[]
> - **Writes To:** x-ipe-docs/memory/.working/rubric/
> - **Constraints:** Per-section measurable criteria; weight by user emphasis; higher weight = higher extraction priority

**When:** Orchestrator needs quality criteria for evaluating the RE report.

```xml
<operation name="design_rubric">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: framework (8 RE sections with sub-skill mappings), overview, user_request
      2. UNDERSTAND user emphasis — which sections matter most (from user_request keywords)
      3. GATHER section depth info from framework stubs
    </action>
    <output>Framework sections and user priorities understood</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE framework contains 8 RE sections
      2. VALIDATE overview is non-empty
      3. VALIDATE user_request is non-empty
    </action>
    <constraints>
      - BLOCKING: Missing framework → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Inputs validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. For each RE section, DEFINE measurable criteria:
         - Completeness: all subsections populated with substantive content
         - Accuracy: claims backed by code citations (file:line)
         - Depth: appropriate detail level for section type (e.g., architecture diagrams for section 1)
      2. ASSIGN weights based on user emphasis (default: equal; emphasized sections get 1.5× weight)
      3. BUILD rubric_metrics[] with {section_id, criteria, weight, threshold}
      4. BUILD acceptance_criteria[] with {section_id, checks[]} — testable boolean checks per section
    </action>
    <output>Rubric metrics and acceptance criteria defined</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY rubric_metrics has entries for all 8 sections
      2. VERIFY weights sum to a reasonable total (normalized)
      3. VERIFY each criterion is measurable (not vague)
    </action>
    <output>Rubric validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE rubric to x-ipe-docs/memory/.working/rubric/{app_name}-re-rubric.md
      2. RETURN operation_output with success, rubric_metrics, acceptance_criteria
    </action>
    <output>Rubric written and returned</output>
  </phase_5>

</operation>
```

### Operation: request_knowledge

> **Contract:**
> - **Input:** framework: dict, current_state: {filled_sections: string[], empty_sections: string[], partial_sections: string[]}, rubric: dict
> - **Output:** knowledge_requests: {target_section: string, what_needed: string, suggested_extractor: string, priority: float}[]
> - **Writes To:** x-ipe-docs/memory/.working/plan/
> - **Constraints:** suggested_extractor can be an `x-ipe-tool-rev-eng-*` sub-skill name OR extractor-web/extractor-memory; prioritize by rubric weight; return empty array if no gaps

**When:** Orchestrator needs to know what knowledge is still missing and which extractor can fill it.

```xml
<operation name="request_knowledge">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: framework, current_state, rubric
      2. IDENTIFY the Section → Sub-Skill Map from the framework
      3. UNDERSTAND which sections are filled, empty, or partial
    </action>
    <output>Gap landscape understood</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE framework contains 8 RE sections
      2. VALIDATE current_state has at least one of filled/empty/partial arrays
      3. VALIDATE rubric contains metrics for each section
    </action>
    <constraints>
      - BLOCKING: Missing framework or rubric → return error INPUT_VALIDATION_FAILED
    </constraints>
    <output>Inputs validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. WALK each framework section and compare against current_state:
         - If section in filled_sections and meets rubric threshold → skip
         - If section in empty_sections → generate full extraction request
         - If section in partial_sections → generate targeted extraction request for missing subsections
      2. For each gap, DETERMINE suggested_extractor:
         - Primary: the mapped x-ipe-tool-rev-eng-* sub-skill for that section
         - Fallback: extractor-memory (for existing knowledge) or extractor-web (for external docs)
      3. For each gap, GENERATE specific what_needed description (not vague — e.g., "Extract all REST endpoints with request/response schemas from src/api/")
      4. ASSIGN priority from rubric weight (high-weight sections first)
      5. SORT knowledge_requests by priority descending
      6. IF no gaps remain → return empty knowledge_requests[]
    </action>
    <output>Knowledge requests generated</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY each request has target_section, what_needed, suggested_extractor, priority
      2. VERIFY suggested_extractor is a valid skill name
      3. VERIFY what_needed is specific (≥10 words, references code paths or section IDs)
    </action>
    <output>Requests validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE knowledge_requests to x-ipe-docs/memory/.working/plan/{app_name}-re-plan.md
      2. RETURN operation_output with success, knowledge_requests
    </action>
    <output>Plan written and returned</output>
  </phase_5>

</operation>
```

### Operation: fill_structure

> **Contract:**
> - **Input:** framework: dict, gathered_knowledge: {section_id: string, content: string, source: string, metadata: dict}[], rubric: dict
> - **Output:** completed_draft: string
> - **Writes To:** x-ipe-docs/memory/.working/draft/
> - **Constraints:** Map knowledge to framework sections; mark incomplete sections with [INCOMPLETE: reason]; validate against rubric; do NOT write to persistent memory

**When:** Orchestrator has gathered knowledge and needs it assembled into a structured draft.

```xml
<operation name="fill_structure">

  <phase_1 name="博学之 — Study Broadly">
    <action>
      1. READ input: framework (8 sections), gathered_knowledge[], rubric
      2. INDEX gathered_knowledge by section_id for efficient lookup
      3. UNDERSTAND framework section structure and expected content per section
    </action>
    <output>Inputs indexed and understood</output>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <action>
      1. VALIDATE framework contains 8 RE sections
      2. VALIDATE gathered_knowledge is non-empty array
      3. VALIDATE each item has section_id, content fields
      4. VALIDATE rubric contains criteria for each section
    </action>
    <constraints>
      - BLOCKING: Missing framework or rubric → return error INPUT_VALIDATION_FAILED
      - WARNING: Empty gathered_knowledge → proceed but mark all sections [INCOMPLETE]
    </constraints>
    <output>Inputs validated</output>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <action>
      1. For each framework section:
         a. FIND matching gathered_knowledge entries by section_id
         b. MERGE content into the section stub, preserving subsection structure
         c. EVALUATE against rubric criteria for that section
         d. IF content insufficient → mark with [INCOMPLETE: {reason}]
         e. IF content meets rubric → mark section as complete
      2. COMPOSE completed_draft by assembling all 8 sections in order
      3. ADD metadata header (app_name, generation date, completeness summary)
      4. ADD source attribution per section (from gathered_knowledge.source)
    </action>
    <output>Draft assembled with completeness markers</output>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <action>
      1. VERIFY completed_draft contains all 8 sections
      2. VERIFY each section either has content or [INCOMPLETE: reason] marker
      3. VERIFY source attribution is present for filled sections
      4. COUNT completeness ratio (filled / total sections)
    </action>
    <output>Draft validated</output>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <action>
      1. WRITE completed_draft to x-ipe-docs/memory/.working/draft/{app_name}-re-draft.md
      2. RETURN operation_output with success, completed_draft, completeness_ratio
    </action>
    <output>Draft written and returned</output>
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
    # provide_framework
    framework_document: "dict"
    toc_structure: "object[]"
    # design_rubric
    rubric_metrics: "object[]"
    acceptance_criteria: "object[]"
    # request_knowledge
    knowledge_requests: "object[]"
    # fill_structure
    completed_draft: "string"
    completeness_ratio: "float"
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
    <verification>No files written outside x-ipe-docs/memory/.working/</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Sub-skill mapping integrity</name>
    <verification>provide_framework maps all 8 sections to correct rev-eng sub-skills</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_OPERATION` | Operation name not one of the 4 defined | Return error listing valid operations |
| `INPUT_VALIDATION_FAILED` | Required input missing or wrong type | Return error with specific field and expected type |
| `TEMPLATE_NOT_FOUND` | Mixin template file missing | Log warning, proceed with base playbook only |
| `MIXIN_UNSUPPORTED` | Language or repo_type not in supported set | Log warning, skip mixin, use base playbook |
| `FRAMEWORK_INCOMPLETE` | Framework missing expected sections | Return error with list of missing sections |
| `WRITE_FAILED` | Cannot write to .working/ path | Return error; orchestrator decides retry or alternate path |
| `QUALITY_THRESHOLD_NOT_MET` | Draft below rubric quality bar | Return partial results with completeness_ratio; orchestrator decides |

---

## Patterns & Anti-Patterns

| Pattern | When | Key Actions |
|---------|------|-------------|
| Incremental fill | Large codebase | Fill sections iteratively via rev-eng sub-skills |
| Mixin composition | Polyglot repo | Stack language + repo-type mixins in provide_framework |
| Sub-skill delegation | Specialized analysis | Map each section to its x-ipe-tool-rev-eng-* sub-skill |

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip rubric | No quality gate | Always design_rubric before fill_structure |
| Persist from constructor | Bypasses librarian | Write to .working/ only; let librarian promote |
| Generic extraction | Misses domain detail | Use domain-specific rev-eng sub-skills, not generic extractors |

---

## Examples

See `references/examples.md` for worked examples of each operation.
