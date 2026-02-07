# Idea Summary: Agent-Optimized Skill Expression Guidelines

## Human Summary

This idea extends the X-IPE skill creation guidelines with two new principles:
1. **Agent-Optimized Expression Formats** - Define format rules for different content types based on how AI agents best consume information
2. **Sub-Agent Decomposition** - Define patterns for breaking skills into parallelizable sub-agents with DAG workflows

The goal is to make skills more effective for AI agents to learn and execute, improving reliability and efficiency.

---

## Agent Specification

### Metadata

```yaml
idea_id: 012
idea_name: Agent-Optimized Skill Expression Guidelines
version: 1
status: refined
created: 2026-02-04
related_files:
  - x-ipe-docs/skill-meta/templates/skill-creation-best-practice/skill-general-guidelines.md
research_sources:
  - https://agentskills.io/specification
  - https://www.anthropic.com/news/skills
  - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
  - https://www.anthropic.com/engineering/building-effective-agents
  - https://github.com/anthropics/skills (skill-creator, mcp-builder)
  - https://docs.crewai.com/concepts/agents
  - https://docs.crewai.com/concepts/crews
  - https://docs.crewai.com/concepts/tasks
```

---

### Problem Statement

Current X-IPE skill documents mix human-readable and agent-readable formats without clear guidelines. This leads to:
- Agents parsing symbolic importance signals (⚠️/⛔) less reliably than keywords
- Data models expressed as tables that agents must mentally parse
- Execution procedures in prose that lack clear conditional logic
- No guidance on decomposing complex skills into parallelizable sub-agents

---

### Proposed Solution

Add two new principles to `skill-general-guidelines.md`:

#### Principle 3: Agent-Optimized Expression Formats

Apply **Degrees of Freedom** framework based on content fragility:

| Content Type | Freedom | Format | Rationale |
|--------------|---------|--------|-----------|
| Data Models (input/output) | Low | YAML with explicit types | Agents parse structured data better |
| Importance Signals | Low | Keywords: `BLOCKING`, `MANDATORY`, `CRITICAL` | Pattern-matching more reliable than symbol recognition |
| File/Folder Operations | Low | Explicit paths with `{variable}` syntax | Fragile operations need precision |
| Conditional Logic | Medium | IF/THEN/ELSE in prose | Clearer than prose alone, more flexible than code |
| Execution Procedures | Medium | Numbered steps with inline conditions | Balance readability and precision |
| Quality Checklists | Medium | Markdown checkboxes + boolean descriptions | Human scannable, agent parseable |
| Examples | High | Prose with code blocks | Agents learn from patterns |
| Workflow Decisions | High | Prose with options | Multiple valid paths |

**Format Rules:**

```yaml
format_rules:
  importance_signals:
    avoid: ["⚠️", "⛔", "✅", "🔴", "🟢"]
    use: ["BLOCKING:", "MANDATORY:", "CRITICAL:", "REQUIRED:", "OPTIONAL:"]
    
  variable_syntax:
    pattern: "{variable_name}"
    examples:
      - "{folder_path}"
      - "{feature_id}"
      - "{user_input}"
      
  gate_conditions:
    format: "GATE: {assertion}"
    examples:
      - "GATE: files_analyzed == true"
      - "GATE: tests_passing AND coverage >= 80%"
      
  data_models:
    format: yaml_block
    required_fields: [name, type, description]
    example: |
      inputs:
        folder_path:
          type: string
          description: Path to idea folder
          required: true
        
  anti_patterns:
    format: yaml_list
    fields: [pattern, reason, alternative]
```

---

#### Principle 4: Sub-Agent Decomposition (DAG Workflow)

For complex skills, define parallel and sequential sub-agent workflows:

**When to Apply:**
- Skill has 5+ execution steps
- Steps have no dependencies between them (parallelizable)
- DoD/DoR validation can be isolated
- Different expertise required per step

**Workflow Definition Format:**

```yaml
workflow:
  type: dag  # directed acyclic graph
  
  parallel_groups:
    - name: research_phase
      steps: [step_1, step_2]
      merge_to: step_3
      
  sequential:
    - step_3
    - step_4
    
  dod_validator:
    runs_after: final_step
    agent: dod-checker

steps:
  step_1:
    name: Search Online Feedback
    agent_role: Feedback Researcher
    specialization: Web search and summarization
    inputs: ["{topic}"]
    outputs: [feedback_summary]
    
  step_2:
    name: Analyze Survey Data  
    agent_role: Data Analyst
    specialization: Survey data analysis
    inputs: ["{survey_file}"]
    outputs: [survey_insights]
    parallelizable_with: [step_1]
    
  step_3:
    name: Generate Report
    agent_role: Report Writer
    specialization: Report synthesis
    inputs: [step_1.feedback_summary, step_2.survey_insights]
    outputs: [final_report]
    
sub_agents:
  feedback_researcher:
    model: haiku  # fast/cheap for search
    tools: [web_search, summarize]
    
  data_analyst:
    model: sonnet
    tools: [file_read, data_analysis]
    
  report_writer:
    model: sonnet
    tools: [file_write, formatting]
    
  dod_checker:
    model: haiku
    tools: [validation, checklist]
    isolated: true  # runs in separate context
```

**Benefits:**
- **Parallelization** - Independent steps run concurrently
- **Specialization** - Each sub-agent optimized for specific role
- **Modularity** - DoD checker is isolated, reusable across skills
- **Cost efficiency** - Use cheaper models for simple tasks

---

### Implementation Scope

| Component | Action | Priority |
|-----------|--------|----------|
| `skill-general-guidelines.md` | Add Principle 3 + 4 | Must Have |
| `x-ipe-task-based-skill.md` template | Add workflow section | Should Have |
| Existing task-based skills | Migrate to new format | Could Have |
| Copilot instructions | Reference new principles | Must Have |

---

### Acceptance Criteria

```yaml
acceptance_criteria:
  - name: Principle 3 documented
    condition: skill-general-guidelines.md contains "Agent-Optimized Expression Formats"
    
  - name: Principle 4 documented  
    condition: skill-general-guidelines.md contains "Sub-Agent Decomposition"
    
  - name: Format rules defined
    condition: YAML format rules for all content types specified
    
  - name: DAG workflow format defined
    condition: YAML schema for parallel_groups, steps, sub_agents documented
    
  - name: At least one skill migrated
    condition: One task-based skill updated to demonstrate new format
```

---

### Example Migration

**Before (current format):**
```markdown
### Step 1: Read Idea Files

**Action:** Navigate to the idea folder and read all files

1. Go to x-ipe-docs/ideas/{folder}/
2. Read each file
3. ⚠️ If files are empty, stop and ask user

**Output:** Understanding of the idea
```

**After (agent-optimized format):**
```yaml
step_1:
  name: Read Idea Files
  action: Read all files in idea folder
  
  procedure:
    - read_all: x-ipe-docs/ideas/{folder}/*
    - extract: content, themes, gaps
    
  gate:
    condition: files.count > 0
    on_failure: ask_user("No files found in folder")
    
  outputs:
    - idea_understanding:
        type: object
        fields: [content, themes, gaps]
```

---

### Next Steps

| Task | Description |
|-----------|-------------|
| Feature Refinement | Refine the two principles with detailed specifications |
| Technical Design | Design migration approach for existing skills |
| Code Implementation | Update skill-general-guidelines.md |

---

### Decision Log

| Decision | Rationale | Source |
|----------|-----------|--------|
| Adopt Anthropic Agent Skills format | Maximum compatibility with ecosystem | agentskills.io |
| Use Degrees of Freedom framework | Scenario-based, not one-size-fits-all | Anthropic skill-creator |
| Keywords over symbols for importance | Agents pattern-match keywords better | building-effective-agents |
| YAML for data models | Agents parse structured data more reliably | Prompt engineering best practices |
| DAG workflow for sub-agents | Enables parallelization and specialization | CrewAI, Anthropic orchestrator pattern |
| Isolated DoD checker | Improves modularity and reliability | Human input during ideation |
