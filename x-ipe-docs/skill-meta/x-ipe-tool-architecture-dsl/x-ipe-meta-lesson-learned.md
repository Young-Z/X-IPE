# Lesson Learned — x-ipe-tool-architecture-dsl

---

## LL-001

**Date:** 2026-02-18
**Severity:** major
**Source:** agent_observed
**Status:** raw
**Task ID:** TASK-457

### Context

```yaml
skill_name: x-ipe-tool-architecture-dsl
scenario: |
  During ideation (TASK-457), the agent generated an architecture-dsl code block
  inside idea-summary-v2.md for IDEA-023. The architecture-dsl tool was listed as
  enabled in tools.json (stages.ideation.ideation.x-ipe-tool-architecture-dsl: true),
  but the agent did NOT load the x-ipe-tool-architecture-dsl skill before generating
  the DSL block. It invented freeform syntax from its general knowledge.
inputs:
  enabled_tools: ["mermaid", "x-ipe-tool-architecture-dsl"]
  idea_folder: "023. CR-Compose Idea in Workflow"
```

### Observed Behavior

```
Agent generated invalid architecture-dsl syntax:

  ```architecture-dsl
  view: module
  title: Compose Idea Modal — Module View

  layer UI {
    [Compose Idea Modal] {
      desc: Full-screen modal with toggle, tabs, tree, preview
      tech: JavaScript, HTML, CSS
    }
  }
  ```

Errors:
  1. Used `view: module` instead of `@startuml module-view`
  2. Used `title:` instead of `title "..."`
  3. Used `[Name] { }` bracket notation instead of `module/component` keywords
  4. Used `desc:` and `tech:` which are not valid grammar keywords (silently ignored)
  5. Missing `@enduml`, `grid`, `rows`, `cols` declarations
  6. No layer colors, no module/component structure

Result: IPE renderer failed to parse the block — title "Compose Idea Modal — Module View"
did not render.
```

### Expected Behavior

```
Agent should produce valid Architecture DSL syntax conforming to the grammar:

  ```architecture-dsl
  @startuml module-view
  title "Compose Idea Modal — Module View"
  theme "theme-default"
  direction top-to-bottom
  grid 12 x 6

  layer "UI" {
    color "#dbeafe"
    border-color "#3b82f6"
    rows 2

    module "Compose Idea Modal" {
      cols 5
      rows 2
      grid 1 x 1
      align center center
      gap 8px
      component "Toggle / Tabs / Tree / Preview" { cols 1, rows 1 }
    }
    ...
  }
  @enduml
  ```
```

### Ground Truth

```
The correct syntax was manually produced after loading the architecture-dsl skill
and reviewing a working example (idea-summary-v1.md from idea 101). The fix was
committed in commit 6f161c2.

Root cause: The architecture-dsl skill was never loaded. The ideation skill lists
enabled tools but does NOT require loading the corresponding tool skill before
generating content with it. The agent used its general LLM knowledge to guess
the DSL format, producing entirely invalid syntax.
```

### Improvement Proposal

```yaml
type: update_instruction
target: ".github/skills/x-ipe-tool-architecture-dsl/SKILL.md"
description: |
  The architecture-dsl skill itself already has correct BLOCKING rules and grammar.
  The problem is upstream: skills that USE architecture-dsl (like ideation) don't
  enforce loading this skill before generating DSL content.

  Two-part fix:

  1. Add a "Quick Syntax Reference" section to the architecture-dsl SKILL.md that
     can be referenced by other skills via extra_instructions in tools.json. This
     gives agents a minimal cheat sheet even if they don't fully load the skill.

  2. Update the ideation skill (x-ipe-task-based-ideation-v2) to add a BLOCKING
     constraint: "When generating content with an enabled tool, MUST load that
     tool's skill first (e.g., load x-ipe-tool-architecture-dsl before writing
     architecture-dsl code blocks)."

  The quick reference should include:
  - Required @startuml/@enduml wrapper
  - Required document-level declarations (title, theme, grid)
  - Required layer/module/component structure with cols summing to 12
  - List of INVALID keywords to avoid (view, desc, tech, note, etc.)
```
