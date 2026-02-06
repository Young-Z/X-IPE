# Tool Usage Guide

This reference document contains detailed tool configuration, mapping, and usage examples for the Ideation skill.

---

## Tool Behavior by Section

When tools are enabled in the meta file, the agent MUST attempt to use them during the ideation process:

| Tool Type | When to Use | Example Tools |
|-----------|-------------|---------------|
| Design Tools | Visual mockups, wireframes | `frontend-design`, Figma MCP |
| Diagram Tools | Flowcharts, architecture diagrams | `mermaid`, `antv-infographic` |
| Research Tools | Market analysis, competitor research | Web search, databases |
| Prototyping Tools | Quick demos, proof of concepts | Code generation, no-code tools |

**Usage Rules:**
1. Read `x-ipe-docs/config/tools.json` at start of ideation task
2. For each section (`stages.ideation.ideation`, `stages.ideation.mockup`, `stages.ideation.sharing`), check enabled tools
3. If tool is enabled (`true`) → Attempt to use during relevant steps
4. If tool is unavailable or fails → Document the limitation and proceed manually
5. Always inform user which tools are active based on config

---

## Tool Mapping & Skill Invocation

| Config Key | Skill/Capability | How to Invoke |
|------------|------------------|---------------|
| `stages.ideation.ideation.antv-infographic` | `infographic-syntax-creator` skill | Call skill to generate infographic DSL syntax |
| `stages.ideation.ideation.mermaid` | Mermaid code blocks | Generate mermaid diagrams directly in markdown |
| `stages.ideation.ideation.tool-architecture-dsl` | `tool-architecture-dsl` skill | Generate Architecture DSL directly in markdown (IPE renders it) |
| `stages.ideation.mockup.frontend-design` | `frontend-design` skill | Call skill to create HTML/CSS mockups |
| `stages.ideation.mockup.figma-mcp` | Figma MCP server | Use MCP tools for Figma integration |

---

## Skill Invocation Rules

```
For each enabled tool in config:
  IF config.stages.ideation.ideation["antv-infographic"] == true:
    → Load and invoke `infographic-syntax-creator` skill for visual summaries
    → Use infographic DSL in idea-summary document
    
  IF config.stages.ideation.ideation["mermaid"] == true:
    → Generate mermaid diagrams for flowcharts, sequences
    → Embed as ```mermaid code blocks in documents
    
  IF config.stages.ideation.ideation["tool-architecture-dsl"] == true:
    → Load `tool-architecture-dsl` skill for layered architecture diagrams
    → Generate Architecture DSL directly in markdown
    → Embed as ```architecture-dsl code blocks (IPE renders natively)
    → Use for: module view (layers, services), landscape view (integrations)
    
  IF config.stages.ideation.mockup["frontend-design"] == true:
    → Load and invoke `frontend-design` skill during brainstorming
    → Create interactive HTML mockups when discussing UI concepts
    → Save mockups to x-ipe-docs/ideas/{folder}/mockup-vN.html (version aligned with idea-summary)
    
  IF config.stages.ideation.mockup["figma-mcp"] == true:
    → Use Figma MCP tools if available
    → Create/update designs in connected Figma files
```

---

## Tool-Enhanced Brainstorming

When tools are enabled in `x-ipe-docs/config/tools.json`, invoke corresponding skills during brainstorming:

| Config Enabled | Skill to Invoke | When to Use |
|----------------|-----------------|-------------|
| `stages.ideation.mockup.frontend-design: true` | `frontend-design` skill | User describes UI → Create HTML mockup |
| `stages.ideation.ideation.mermaid: true` | Mermaid syntax | User describes flow → Generate diagram |
| `stages.ideation.ideation.antv-infographic: true` | `infographic-syntax-creator` skill | Visualize lists, comparisons |
| `stages.ideation.ideation.tool-architecture-dsl: true` | `tool-architecture-dsl` skill | User describes layers/services → Generate architecture DSL |

---

## Example: Config-Driven Tool Usage

```
Config: { "stages": { "ideation": { "mockup": { "frontend-design": true } } } }

User: "I want a dashboard with charts and filters"
Agent Action:
  1. Ask clarifying questions about chart types, layout preferences
  2. IF stages.ideation.mockup.frontend-design == true:
     → Invoke `frontend-design` skill
     → Create interactive HTML mockup
     → Save to x-ipe-docs/ideas/{folder}/mockup-vN.html (aligned with idea-summary version)
  3. Share mockup: "I've created a mockup - does this match your vision?"
  4. Iterate based on feedback
```

---

## Example: Mermaid Diagram Generation

```
Config: { "stages": { "ideation": { "ideation": { "mermaid": true } } } }

User: "The user flow goes from login to dashboard to settings"
Agent Action:
  1. IF stages.ideation.ideation.mermaid == true:
     → Generate mermaid flowchart
     → Share in conversation:
     
     ```mermaid
     flowchart LR
       Login --> Dashboard --> Settings
     ```
  2. Ask: "Does this capture the flow correctly?"
```

---

## Example: Architecture DSL Generation

```
Config: { "stages": { "ideation": { "ideation": { "tool-architecture-dsl": true } } } }

User: "The system has 3 layers: frontend, backend services, and database"
Agent Action:
  1. IF stages.ideation.ideation.tool-architecture-dsl == true:
     → Load `tool-architecture-dsl` skill
     → Generate Architecture DSL directly in markdown
     → Embed in idea-summary as:
     
     ```architecture-dsl
     @startuml module-view
     title "System Architecture"
     theme "theme-default"
     direction top-to-bottom
     grid 12 x 6
     
     layer "Frontend" {
       color "#fce7f3"
       border-color "#ec4899"
       rows 2
       module "Web" { cols 12, rows 2, grid 1 x 1, component "React App" { cols 1, rows 1 } }
     }
     
     layer "Backend" {
       color "#dbeafe"
       border-color "#3b82f6"
       rows 2
       module "Services" { cols 12, rows 2, grid 2 x 1, component "API" { cols 1, rows 1 }, component "Workers" { cols 1, rows 1 } }
     }
     
     layer "Data" {
       color "#dcfce7"
       border-color "#22c55e"
       rows 2
       module "Storage" { cols 12, rows 2, grid 1 x 1, component "PostgreSQL" { cols 1, rows 1 } }
     }
     
     @enduml
     ```
  2. IPE renders this as interactive diagram in the browser
  3. Ask: "Does this architecture structure match your vision?"
```

---

## Question Categories

| Category | Example Questions |
|----------|-------------------|
| Problem Space | "What problem does this solve?" |
| Target Users | "Who will benefit from this?" |
| Scope | "What should be included in v1?" |
| Constraints | "Are there any technical limitations?" |
| Success Criteria | "How will we know it's successful?" |
| Alternatives | "Have you considered approach X?" |

---

## Research Common Principles

### When to Research

- The idea touches well-known domains (e.g., authentication, e-commerce, data pipelines)
- Industry best practices exist for the problem space
- Established patterns or frameworks are relevant
- The idea could benefit from proven approaches

### Research Process

```
1. Identify if topic is common/established
2. Use web_search tool to research:
   - Industry best practices
   - Common design patterns
   - Established principles
   - Reference implementations
3. Document findings as "Common Principles"
4. Note authoritative sources for references
```

### Example Common Topics & Principles

| Topic | Common Principles to Research |
|-------|------------------------------|
| Authentication | OAuth 2.0, JWT best practices, MFA patterns |
| API Design | REST conventions, OpenAPI, rate limiting |
| Data Storage | ACID properties, CAP theorem, data modeling |
| UI/UX | Nielsen heuristics, accessibility (WCAG), mobile-first |
| Security | OWASP Top 10, zero-trust, encryption standards |
| Scalability | Horizontal scaling, caching strategies, CDN usage |
| DevOps | CI/CD pipelines, IaC, observability |

---

## Config-Driven Visualization (for Idea Summary)

```
When creating idea summary, check x-ipe-docs/config/tools.json config:

IF config.stages.ideation.ideation["antv-infographic"] == true:
  → Invoke `infographic-syntax-creator` skill
  → Use infographic DSL for: feature lists, roadmaps, comparisons

IF config.stages.ideation.ideation["mermaid"] == true:
  → Use mermaid syntax for: flowcharts, sequences, state diagrams

IF config.stages.ideation.ideation["tool-architecture-dsl"] == true:
  → Use Architecture DSL for: layered architecture, module views, landscape views
  → Embed directly in markdown as ```architecture-dsl code blocks
  → IPE renders these natively as interactive diagrams

IF ALL are false:
  → Use standard markdown (bullet lists, tables)
```
