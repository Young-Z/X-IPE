# Skill General Guidelines

Core principles, patterns, and standards for X-IPE skills.

---

# Part 1: Core Principles

## Principle 1: Concise is Key

```yaml
principle:
  name: Concise is Key
  rationale: Context window is shared resource
  
default_assumption: AI Agent is already very smart
rule: Only add context it doesn't already have

guidelines:
  - challenge_each_paragraph: "Does this justify its token cost?"
  - prefer: examples over verbose explanations
  - max_skill_lines: 500
```

## Principle 2: Degrees of Freedom

Match specificity to task fragility and variability.

```yaml
principle:
  name: Degrees of Freedom
  metaphor: "Narrow bridge with cliffs needs guardrails (low freedom), open field allows many routes (high freedom)"

freedom_levels:
  high:
    use_when: Multiple approaches valid, decisions depend on context
    format: Text instructions, prose
    examples: [creative brainstorming, workflow decisions]
    
  medium:
    use_when: Preferred pattern exists, some variation acceptable
    format: Pseudocode with parameters, numbered steps with conditions
    examples: [execution procedures, conditional logic]
    
  low:
    use_when: Operations fragile/error-prone, consistency critical
    format: Specific scripts, YAML schemas, explicit paths
    examples: [data models, file operations, importance signals]
```

## Principle 3: Progressive Disclosure

Three-level loading system to manage context efficiently.

```yaml
principle:
  name: Progressive Disclosure
  
loading_levels:
  level_1:
    content: Metadata (name + description)
    when_loaded: Always in context
    token_budget: ~100 words
    
  level_2:
    content: SKILL.md body
    when_loaded: When skill triggers
    token_budget: <500 lines
    
  level_3:
    content: Bundled resources (scripts/, references/, templates/)
    when_loaded: As needed by AI Agent
    token_budget: Unlimited (can execute without loading)
```

## Principle 4: Agent-Optimized Expression Formats

Match content format to how AI Agents best consume information.

```yaml
principle:
  name: Agent-Optimized Expression Formats
  rationale: Agents parse structured data and keywords more reliably than prose and symbols

format_selection:
  # Low freedom - fragile operations need precision
  data_models:
    freedom: low
    format: YAML with explicit types
    rationale: Agents parse structured data reliably
    
  importance_signals:
    freedom: low
    format: "Keywords: BLOCKING:, MANDATORY:, CRITICAL:"
    rationale: Pattern-matching more reliable than symbol recognition
    avoid: ["⚠️", "⛔", "🔴", "🟢"]
    
  file_operations:
    freedom: low
    format: "Explicit paths with {variable} syntax"
    rationale: Fragile operations need precision

  diagrams:
    freedom: low
    format: Indented lists or YAML with branching
    rationale: Agents struggle to parse 2D ASCII spatial relationships; tokens are expensive
    avoid: ["ASCII Art", "Box drawings", "Mermaid", "PlantUML"]

  llm_model_definitions:
    freedom: low
    format: "Reference via input parameter ({model})"
    rationale: Hardcoding models reduces reusability and adaptability
    avoid: ["Hardcoded model names in instructions"]
    
  # Medium freedom - balance readability and precision
  conditional_logic:
    freedom: medium
    format: IF/THEN/ELSE in prose or pseudocode
    
  execution_procedures:
    freedom: medium
    format: Numbered steps with inline conditions
    
  quality_checklists:
    freedom: medium
    format: Tables with boolean descriptions
    
  # High freedom - multiple valid paths
  examples:
    freedom: high
    format: Prose with code blocks
    
  workflow_decisions:
    freedom: high
    format: Prose with options

importance_keywords:
  BLOCKING: Must not skip, halts execution if violated
  MANDATORY: Required, but can continue with warning
  CRITICAL: High priority, affects correctness
  REQUIRED: Needed for completion
  OPTIONAL: Can skip without impact

variable_syntax:
  pattern: "{variable_name}"
  examples:
    - "{folder_path}"
    - "{feature_id}"
    - "{task_id}"

gate_format:
  pattern: "GATE: {assertion}"
  examples:
    - "GATE: files_analyzed == true"
    - "GATE: tests_passing AND coverage >= 80%"
    - "GATE: human_approval == received"
```

## Principle 5: Sub-Agent Decomposition

For complex skills with 5+ steps, decompose into parallelizable sub-agents.

```yaml
principle:
  name: Sub-Agent Decomposition
  pattern: DAG (Directed Acyclic Graph) Workflow

when_to_apply:
  consider: 5+ execution steps
  yes_parallelize: Independent steps (no data dependencies)
  yes_specialize: Different expertise per step
  yes_isolate: DoD validation is complex
  no_keep_linear: All steps sequential with tight coupling

workflow_definition:
  type: dag
  parallel_groups:
    - name: "{phase_name}"
      steps: [step_1, step_2]
      merge_to: step_3
  sequential:
    - step_3
    - step_4
  dod_validator:
    runs_after: final_step
    agent: dod-checker
    isolated: true

step_definition:
  step_id:
    name: "{step_name}"
    agent_role: "{role}"
    specialization: "{expertise}"
    model_hint: haiku | sonnet  # haiku for simple, sonnet for complex
    inputs: ["{input_variables}"]
    outputs: ["{output_names}"]
    tools: ["{tool_list}"]
    parallelizable_with: ["{other_step_ids}"]  # optional

sub_agent_definition:
  agent_id:
    role: "{role_name}"
    goal: "{agent_goal}"
    model: haiku | sonnet
    tools: ["{tool_list}"]
    isolated: true | false  # true for DoD checker

benefits:
  parallelization: Independent steps run concurrently
  specialization: Each sub-agent optimized for specific role
  modularity: DoD checker reusable across skills
  cost_efficiency: Use cheaper models (haiku) for simple tasks
  reliability: Isolated validation improves quality gate accuracy
```

---

# Part 2: Skill Specification

## Skill Types

```yaml
skill_types:
  task_type:
    purpose: Development lifecycle workflows
    naming_convention: "task-type-{name}"
    examples:
      - task-type-ideation
      - task-type-code-implementation
      - task-type-bug-fix
      
  skill_category:
    purpose: Board management and category-level operations
    naming_convention: "{category}+{operation-name}"
    examples:
      - task-board-management
      - feature-board-management
      
  tool_skill:
    purpose: Utility functions and tool integrations
    naming_convention: "{tool-name}"
    examples:
      - pdf
      - pptx
      - frontend-design
```

## Skill Anatomy

```yaml
skill_structure:
  required:
    SKILL.md:
      frontmatter:
        name: required
        description: required  # Include trigger conditions here
      body: Markdown instructions
      
  optional:
    scripts/:
      purpose: Executable code
      when_to_include: Same code rewritten repeatedly, deterministic reliability needed
      benefit: Token efficient, deterministic
      
    references/:
      purpose: Documentation loaded as needed
      when_to_include: Documentation AI Agent should reference while working
      benefit: Keeps SKILL.md lean
      
    templates/:
      purpose: Document templates for output
      when_to_include: Skill produces standardized documents
      benefit: Consistent output format

directory_structure: |
  skill-name/
  ├── SKILL.md (required)
  │   ├── YAML frontmatter (required)
  │   │   ├── name: (required)
  │   │   └── description: (required)
  │   └── Markdown instructions (required)
  └── Bundled Resources (optional)
      ├── scripts/       - Executable code
      ├── references/    - Documentation loaded as needed
      └── templates/     - Document templates for output
```

## Section Order Reference

See [reference-section-order.md](reference-section-order.md) for full section order by skill type.

**Quick Reference - Cognitive Flow:**
1. CONTEXT → 2. DECISION → 3. ACTION → 4. VERIFY → 5. REFERENCE

| Skill Type | Key Sections |
|------------|--------------|
| task_type_skills | Purpose, Input Parameters, DoR, Execution Flow, Execution Procedure, Output Result, DoD |
| tool_skills | Purpose, About, When to Use, Input Parameters, Operations, Output Result, DoD |
| workflow_orchestration_skills | Purpose, Input Parameters, DoR, Execution Flow, Execution Procedure, Registry |
| meta_skills | Purpose, About, Important Notes, Execution Flow, Execution Procedure |

---

# Part 3: Workflow Patterns

## Pattern Selection Guide

| Pattern | Best For | Complexity | When to Use |
|---------|----------|------------|-------------|
| Simple Workflow (YAML) | Complex branching logic | Medium | If/else, switch cases, multi-path decisions |
| Complex Procedure (XML) | Linear multi-component steps | Low-Medium | Steps need distinct constraints/outputs, no complex branching |
| Long Workflow (Phase Blocks) | Multi-phase processes | High | 5+ phases, domain transitions; nests Pattern 1 or 2 inside |

---

## Pattern 1: Simple Workflow (YAML Format)

**Use for:** Steps with complex branching logic (if/else, switch cases, multi-path decisions).

### Template

```yaml
workflow:
  name: "{workflow_name}"
  steps:
    - step: 1
      name: "{step_name}"
      action: "{what to do}"
      gate: "{condition to proceed}"
      
    - step: 2
      name: "{step_name}"
      action: "{what to do}"
      branch:
        if: "{condition}"
        then: "{action_a}"
        else: "{action_b}"
      gate: "{condition to proceed}"

  blocking_rules:
    - "{rule that must not be skipped}"
  
  critical_notes:
    - "{important caution}"
```

### Examples

See examples in this folder:
- [example-pattern1-file-validation.md](example-pattern1-file-validation.md) - File validation with parser branching
- [example-pattern1-task-status.md](example-pattern1-task-status.md) - Task status update with transition validation

---

## Pattern 2: Complex Procedure (XML-Tagged)

**Use for:** Procedures with no or very simple branching logic, but requiring distinct constraints, outputs, and success criteria per step.

CRITICAL: Claude is fine-tuned to recognize XML tags. Use this pattern when steps have multiple components that must be clearly separated. Avoid for complex branching - use Pattern 1 (YAML) instead.

### Template

```xml
<procedure name="{procedure_name}">
  
  <step_1>
    <name>{Step Name}</name>
    <action>
      1. {sub_action_1}
      2. {sub_action_2}
    </action>
    <constraints>
      - BLOCKING: {must_not_violate}
      - CRITICAL: {important_consideration}
    </constraints>
    <success_criteria>
      - {criterion_1}
      - {criterion_2}
    </success_criteria>
    <output>{what_this_step_produces}</output>
  </step_1>

  <step_2>
    <name>{Next Step}</name>
    <requires>{output_from_step_1}</requires>
    <action>
      1. {action}
    </action>
    <constraints>
      - {constraint}
    </constraints>
    <success_criteria>
      - {criterion}
    </success_criteria>
    <output>{output}</output>
  </step_2>

</procedure>
```

### Examples

See examples in this folder:
- [example-pattern2-code-review.md](example-pattern2-code-review.md) - Code review with multi-component steps
- [example-pattern2-feature-implementation.md](example-pattern2-feature-implementation.md) - TDD-based feature implementation

---

## Pattern 3: Long Workflow (Phase Blocks)

**Use for:** Workflows with 5+ distinct phases or multi-domain processes.

Use `## Phase N` headers to organize long workflows. Each phase should have clear entry/exit criteria.

**Nesting Rule:** Within each phase, nest Pattern 1 (YAML) or Pattern 2 (XML) based on the phase's internal complexity:
- If phase has complex branching logic → use Pattern 1 (YAML) inside the phase
- If phase has linear steps with distinct constraints/outputs → use Pattern 2 (XML) inside the phase
- If phase is simple → use plain markdown numbered list

### Template

```markdown
## Phase 1: {Phase Name} (Simple - Plain List)

**Entry Criteria:** {what must be true to start this phase}

Perform the following:
1. {action_1}
2. {action_2}
3. {action_3}

CRITICAL: {important constraint for this phase}

**Exit Criteria:** {what must be true to complete this phase}

---

## Phase 2: {Phase Name} (Complex Branching - Nested YAML)

**Entry Criteria:** Phase 1 complete + {additional requirements}

{yaml}
workflow:
  name: "{phase_workflow_name}"
  steps:
    - step: 1
      name: "{step_name}"
      action: "{what to do}"
      branch:
        if: "{condition_a}"
        then: "{action_if_true}"
        else_if: "{condition_b}"
        then: "{action_if_b}"
        else: "{default_action}"
      gate: "{condition to proceed}"
      
    - step: 2
      name: "{step_name}"
      action: "{what to do}"
      gate: "{condition to proceed}"
{/yaml}

BLOCKING: {rule that must not be violated}

**Exit Criteria:** {completion criteria}

---

## Phase 3: {Phase Name} (Linear with Constraints - Nested XML)

**Entry Criteria:** Phase 2 complete + {additional requirements}

{xml}
<procedure name="{phase_procedure_name}">
  <step_1>
    <name>{Step Name}</name>
    <action>
      1. {sub_action_1}
      2. {sub_action_2}
    </action>
    <constraints>
      - BLOCKING: {must_not_violate}
    </constraints>
    <success_criteria>
      - {criterion_1}
    </success_criteria>
    <output>{what_this_step_produces}</output>
  </step_1>
</procedure>
{/xml}

**Exit Criteria:** {completion criteria}
```

**Note:** Replace `{yaml}` with triple backticks + yaml, and `{xml}` with triple backticks + xml when using in actual skills.

### Examples

See examples in this folder:
- [example-pattern3-requirement-gathering.md](example-pattern3-requirement-gathering.md) - 5-phase workflow with nested YAML and XML
- [example-pattern3-refactoring-analysis.md](example-pattern3-refactoring-analysis.md) - 6-phase analysis workflow with mixed patterns

---

# Part 4: Common Skill Section Patterns

## Task Input

```yaml
task_input:
  # Required attributes (from task board or previous task)
  task_id: "{TASK-XXX}"
  task_type: "{task_type}"
  
  # Context attributes (loaded from project)
  "{context_attr_1}": "{value or path}"
  "{context_attr_2}": "{value or path}"
  
  # Dynamic attributes (from previous task output)
  "{dynamic_attr}": "{value}"
```

## Task Completion Output

```yaml
task_completion_output:
  category: "{standalone | feature-stage | requirement-stage | ideation-stage}"
  status: "{completed | blocked}"
  next_task_type: "{next_task_type}"
  require_human_review: "{yes | no}"
  task_output_links:
    - "{output_file_path_1}"
    - "{output_file_path_2}"
  # Dynamic attributes
  "{attr_name}": "{value}"
```

See [example-task-io-code-implementation.md](example-task-io-code-implementation.md) for complete input/output example.

## Structured Summary

Use markdown table for skill outputs that summarize multiple items with consistent attributes.

### Template

```markdown
| {Column1} | {Column2} | {Column3} | {Column4} |
|-----------|-----------|-----------|-----------|
| {value}   | {value}   | {value}   | {value}   |
```

See [example-structured-summary.md](example-structured-summary.md) for examples (Feature, Dependency, Requirement, Test Coverage).

## DoR/DoD Pattern

Use XML format for Definition of Ready (DoR) and Definition of Done (DoD) sections.

### Template

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>{Prerequisite Name}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>{Another Prerequisite}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>{Optional Prerequisite}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
</definition_of_ready>
```

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>{Output Name}</name>
    <verification>{How to verify}</verification>
  </checkpoint>
</definition_of_done>
```

See [example-dor-dod.md](example-dor-dod.md) for examples (Code Implementation, Feature Refinement).

## Gate Conditions

Use Gate Conditions as an alternative to DoR/DoD when you have complex branching logic in entry/exit criteria.

### Simple Gates (Inline)

For simple pass/fail conditions, use inline format:

```
GATE: document_created == true
GATE: all_tests_pass == true
GATE: human_review == approved
```

### Complex Gates (YAML)

For gates with multiple conditions, thresholds, or branching logic:

```yaml
gate:
  name: "{Gate Name}"
  conditions:
    logic: AND | OR
    checks:
      - type: completion
        condition: "{condition_1} == true"
      - type: threshold
        condition: "{metric} >= {value}"
      - type: approval
        condition: "{approver} == approved"
  on_pass: "{action_if_pass}"
  on_fail: "{action_if_fail}"
```

See [example-gate-conditions.md](example-gate-conditions.md) for examples (Quality Gate, Approval Gate, Release Gate).

---

# Part 5: Quality Reference

CRITICAL: Use keywords (BLOCKING, CRITICAL, MANDATORY) for importance signals in skill content. Agents pattern-match keywords more reliably than Unicode symbols.

| Keyword | Meaning |
|---------|---------|
| `BLOCKING:` | Must not skip, halts execution |
| `CRITICAL:` | High priority, affects correctness |
| `MANDATORY:` | Required, continue with warning if missing |

See [reference-quality-standards.md](reference-quality-standards.md) for:
- Full importance keywords reference
- Common mistakes (anti-patterns)
- What NOT to include in skills
