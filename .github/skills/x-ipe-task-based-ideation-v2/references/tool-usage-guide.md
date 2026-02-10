# Tool Usage Guide

This reference document contains detailed tool configuration, mapping, and usage examples for the Ideation skill.

---

## Tool Configuration File

**Location:** `x-ipe-docs/config/tools.json`

**Format:**
```json
{
  "version": "2.0",
  "stages": {
    "ideation": {
      "ideation": {
        "antv-infographic": false,
        "mermaid": true,
        "x-ipe-tool-architecture-dsl": false,
        "_extra_instruction": "Optional extra instructions"
      },
      "mockup": {
        "frontend-design": true,
        "figma-mcp": false
      },
      "sharing": {}
    }
  }
}
```

---

## Tool Mapping & Skill Invocation

| Config Key | Skill/Capability | How to Invoke |
|------------|------------------|---------------|
| `stages.ideation.ideation.antv-infographic` | `x-ipe-tool-infographic-syntax` skill | Call skill to generate infographic DSL syntax |
| `stages.ideation.ideation.mermaid` | Mermaid code blocks | Generate mermaid diagrams directly in markdown |
| `stages.ideation.ideation.x-ipe-tool-architecture-dsl` | `x-ipe-tool-architecture-dsl` skill | Generate Architecture DSL directly in markdown |
| `stages.ideation.mockup.frontend-design` | `frontend-design` skill | Call skill to create HTML/CSS mockups |
| `stages.ideation.mockup.figma-mcp` | Figma MCP server | Use MCP tools for Figma integration |

---

## Skill Invocation Rules

```yaml
invocation_rules:
  antv_infographic:
    config_key: "stages.ideation.ideation.antv-infographic"
    when_true: "Load and invoke x-ipe-tool-infographic-syntax skill"
    use_for: "Visual summaries, feature lists, roadmaps, comparisons"
    output: "Infographic DSL code blocks"
    
  mermaid:
    config_key: "stages.ideation.ideation.mermaid"
    when_true: "Generate mermaid diagrams"
    use_for: "Flowcharts, sequences, state diagrams"
    output: "```mermaid code blocks"
    
  architecture_dsl:
    config_key: "stages.ideation.ideation.x-ipe-tool-architecture-dsl"
    when_true: "Load x-ipe-tool-architecture-dsl skill"
    use_for: "Layered architecture, module views, landscape views"
    output: "```architecture-dsl code blocks"
    
  frontend_design:
    config_key: "stages.ideation.mockup.frontend-design"
    when_true: "Load and invoke frontend-design skill"
    use_for: "Interactive HTML mockups during brainstorming"
    output: "HTML files in x-ipe-docs/ideas/{folder}/mockups/"
```

---

## Tool-Enhanced Brainstorming

When tools are enabled, invoke corresponding skills during brainstorming:

| User Describes | Config Check | Tool Action |
|----------------|--------------|-------------|
| UI layout | `mockup.frontend-design == true` | Invoke frontend-design, create mockup |
| User flow | `ideation.mermaid == true` | Generate mermaid flowchart |
| Feature list | `ideation.antv-infographic == true` | Use infographic DSL |
| System layers | `ideation.x-ipe-tool-architecture-dsl == true` | Generate architecture DSL |

---

## Config-Driven Visualization (for Idea Summary)

```yaml
visualization_rules:
  priority_order:
    1: "Check antv-infographic for features/roadmaps"
    2: "Check mermaid for flowcharts/sequences"
    3: "Check x-ipe-tool-architecture-dsl for architecture"
    4: "Fall back to standard markdown"
    
  antv_infographic_templates:
    feature_list: "list-grid-badge-card"
    roadmap: "sequence-roadmap-vertical-simple"
    comparison: "compare-binary-horizontal-badge-card-arrow"
    
  fallback_when_disabled:
    features: "Bullet list with bold headers"
    roadmap: "Numbered list with phases"
    comparison: "Markdown table"
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

- Topic touches well-known domains (auth, e-commerce, data pipelines)
- Industry best practices exist
- Established patterns or frameworks are relevant

### Common Topics & Principles

| Topic | Common Principles to Research |
|-------|------------------------------|
| Authentication | OAuth 2.0, JWT best practices, MFA patterns |
| API Design | REST conventions, OpenAPI, rate limiting |
| Data Storage | ACID properties, CAP theorem, data modeling |
| UI/UX | Nielsen heuristics, accessibility (WCAG), mobile-first |
| Security | OWASP Top 10, zero-trust, encryption standards |
| Scalability | Horizontal scaling, caching strategies, CDN usage |
| DevOps | CI/CD pipelines, IaC, observability |
