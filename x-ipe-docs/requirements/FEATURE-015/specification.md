# Feature Specification: Architecture DSL Skill

> Feature ID: FEATURE-015  
> Version: v2.0  
> Status: Refined  
> Last Updated: 01-24-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v2.0 | 01-24-2026 | Grid-based layout system (12-column Bootstrap-inspired) |
| v1.0 | 01-24-2026 | Initial specification (flexbox-based) |

---

## Overview

The Architecture DSL Skill is a tool skill that enables AI agents to translate between natural language architecture descriptions and a structured Domain-Specific Language (DSL). This skill provides a precise, human-readable format for defining software architecture that is easy to version control, iteratively refine, and communicate between humans and AI agents.

The skill supports two architecture views:
1. **Module View** - Shows structural decomposition into layers, modules, and components
2. **Application Landscape View** - Shows how applications integrate with action flows between them

**v2.0** introduces a **Bootstrap-inspired 12-column grid system** replacing the previous flexbox-based layout, providing:
- Mathematical certainty for cross-layer alignment
- Nested grids at document, layer, module, and component levels
- Explicit control over visual arrangement at every level

---

## User Stories

### US-1: Natural Language to DSL Translation
As an **AI agent**, I want to **translate natural language architecture descriptions into structured DSL**, so that **I can produce precise, version-controllable architecture definitions**.

### US-2: DSL to Natural Language Explanation
As an **AI agent**, I want to **explain existing DSL code in natural language**, so that **I can help humans understand complex architecture definitions**.

### US-3: DSL Validation
As an **AI agent**, I want to **validate DSL syntax and structure**, so that **I can catch errors before attempting to render diagrams**.

### US-4: Iterative DSL Refinement
As an **AI agent**, I want to **update existing DSL based on feedback**, so that **I can iteratively refine architecture designs with the user**.

### US-5: Grid-Based Layout Control (v2)
As an **architect**, I want to **control the visual layout using a 12-column grid system**, so that **I can achieve precise cross-layer and cross-module alignment**.

### US-6: Component Alignment (v2)
As an **architect**, I want to **align components within modules using nested grids**, so that **sibling modules have visually aligned component rows**.

---

## Acceptance Criteria

### 1. Skill Structure
- [x] AC-1.1: Skill folder exists at `.github/skills/tool-architecture-dsl/`
- [x] AC-1.2: SKILL.md contains complete skill definition with purpose, workflow, and examples
- [x] AC-1.3: DSL grammar reference document included at `references/grammar.md`
- [x] AC-1.4: Example DSL files provided for Module View at `examples/module-view.dsl`
- [x] AC-1.5: Example DSL files provided for Landscape View at `examples/landscape-view.dsl`
- [x] AC-1.6: v1 backup maintained at `.github/skills/tool-architecture-dsl-v1-backup/` (v2)

### 2. DSL Syntax - Core Elements
- [x] AC-2.1: `@startuml <view-type>` / `@enduml` block delimiters are supported
- [x] AC-2.2: `title "string"` property sets diagram title
- [x] AC-2.3: `direction top-to-bottom | left-to-right` property controls overall layout direction
- [x] AC-2.4: Comments are supported with `'` prefix (single line)
- [x] AC-2.5: Multi-line comments supported with `/' ... '/` syntax

### 3. DSL Syntax - Module View Elements
- [x] AC-3.1: `layer "name" as alias { }` defines architectural layers
- [x] AC-3.2: `module "name" { }` defines modules within layers (alias optional)
- [x] AC-3.3: `component "name"` defines components within modules
- [x] AC-3.4: `component "name" <<stereotype>>` supports decorated components (e.g., `<<model>>`, `<<icon>>`, `<<service>>`)
- [x] AC-3.5: Layers can contain multiple modules
- [x] AC-3.6: Modules can contain multiple components

### 4. DSL Syntax - Landscape View Elements
- [x] AC-4.1: `zone "name" { }` defines application zones/domains
- [x] AC-4.2: `app "name" as alias { tech: X, platform: Y, status: Z }` defines applications with metadata
- [x] AC-4.3: `database "name" as alias` defines database nodes
- [x] AC-4.4: `source --> target : "action label"` defines action flows between elements
- [x] AC-4.5: Status values supported: `healthy`, `warning`, `critical`
- [x] AC-4.6: Tech and platform are optional properties

### 5. DSL Syntax - Grid-Based Layout Control (v2)
- [x] AC-5.1: `grid 12 x N` at document level defines 12-column grid with N rows
- [x] AC-5.2: `rows N` at layer level specifies how many document rows the layer occupies
- [x] AC-5.3: `cols N` at module level specifies column span (1-12), modules in layer MUST sum to 12
- [x] AC-5.4: `rows N` at module level specifies row span within layer
- [x] AC-5.5: `grid C x R` at module level defines internal component grid
- [x] AC-5.6: `cols N` at component level specifies column span in module's internal grid
- [x] AC-5.7: `rows N` at component level specifies row span in module's internal grid
- [x] AC-5.8: `align H V` at module level controls component alignment (left|center|right, top|center|bottom)
- [x] AC-5.9: `gap Npx` at module level specifies spacing between components
- [x] AC-5.10: `text-align left|center|right` controls title/label alignment
- [x] AC-5.11: `color "#hex"` and `border-color "#hex"` set layer/module colors

### 6. Skill Capabilities
- [x] AC-6.1: Skill can translate natural language descriptions to DSL
- [x] AC-6.2: Skill can explain DSL code in natural language
- [x] AC-6.3: Skill can validate DSL syntax and report errors (including grid validation)
- [x] AC-6.4: Skill can update existing DSL based on user feedback
- [x] AC-6.5: Skill provides clear error messages for invalid syntax
- [x] AC-6.6: Skill can handle partial/incomplete DSL and suggest completions

### 7. Integration
- [x] AC-7.1: Skill registered in `x-ipe-docs/config/tools.json` under `stages.ideation.ideation.tool-architecture-dsl`
- [x] AC-7.2: Skill can be enabled/disabled via Stage Toolbox modal
- [x] AC-7.3: Skill works alongside other ideation tools (mermaid, antv-infographic)
- [x] AC-7.4: DSL output can be embedded in markdown using ```architecture-dsl code blocks

---

## Functional Requirements

### FR-1: DSL Grammar Definition (v2)

**Description:** Define a complete, unambiguous grammar for the Architecture DSL v2.

**Details:**
- Input: DSL text
- Process: Parse according to grammar rules
- Output: Abstract Syntax Tree (AST) or parse errors

**Grammar Rules (v2):**
```
document     := header elements* '@enduml'
header       := '@startuml' view-type
view-type    := 'module-view' | 'landscape-view'
elements     := title | direction | grid | text-align | layer | zone | flow | comment

# Grid System (v2)
grid         := 'grid' number 'x' number
rows         := 'rows' number
cols         := 'cols' number
align        := 'align' h-align v-align
h-align      := 'left' | 'center' | 'right'
v-align      := 'top' | 'center' | 'bottom'
gap          := 'gap' size
size         := number 'px' | number 'rem'

# Module View
layer        := 'layer' string ('as' alias)? '{' layer-content* '}'
layer-content := rows | module | color | border-color | text-align
module       := 'module' string ('as' alias)? '{' module-content* '}'
module-content := cols | rows | grid | align | gap | component | color | text-align
component    := 'component' string ('{' component-props '}')? stereotype?
component-props := cols-prop (',' rows-prop)?
cols-prop    := 'cols' number
rows-prop    := 'rows' number

# Landscape View (unchanged from v1)
zone         := 'zone' string '{' zone-content* '}'
zone-content := app | database
app          := 'app' string ('as' alias)? '{' app-props* '}'
app-props    := ('tech:' value) | ('platform:' value) | ('status:' value)
database     := 'database' string ('as' alias)?
flow         := alias '-->' alias ':' string

# Common
comment      := "'" text | "/'" text "'/"
string       := '"' [^"]* '"'
alias        := identifier
identifier   := [a-zA-Z_][a-zA-Z0-9_]*
value        := [^\n,}]+
number       := [0-9]+
```

### FR-2: Natural Language Translation (v2)

**Description:** Translate natural language architecture descriptions to DSL.

**Details:**
- Input: Natural language description of architecture
- Process: Extract entities (layers, modules, components, apps), relationships, and layout preferences
- Output: Valid Architecture DSL v2 with grid layout

**Translation Mapping (v2):**
| NL Pattern | DSL Output |
|------------|------------|
| "three layers: X, Y, Z" | `grid 12 x 6` + 3 layers with `rows 2` each |
| "module A contains B, C" | `module "A" { grid 2 x 1 component "B" { cols 1 } ... }` |
| "split layer into 3 equal parts" | 3 modules with `cols 4` each |
| "one wide, one narrow module" | `cols 8` + `cols 4` |
| "stack components vertically" | `grid 1 x N` |
| "center components" | `align center center` |

### FR-3: DSL Validation (v2)

**Description:** Validate DSL syntax and semantic correctness.

**Details:**
- Input: DSL text
- Process: Parse syntax, check semantic rules including grid validation
- Output: Valid flag + list of errors/warnings

**Validation Rules (v2):**
1. Syntax must match grammar
2. Document must have `grid C x R` declaration
3. Layers must have `rows N` declaration
4. Module `cols` within a layer MUST sum to 12
5. All referenced aliases must be defined
6. Flow targets must exist as app/database aliases
7. Status values must be one of: healthy, warning, critical

### FR-4: DSL Explanation

**Description:** Generate natural language explanation from DSL.

**Details:**
- Input: Valid DSL
- Process: Traverse AST, generate descriptions
- Output: Natural language explanation

**Example (v2):**
```
Input DSL:
  grid 12 x 2
  layer "Presentation" { rows 2 module "Web UI" { cols 12 grid 1 x 1 component "React App" { cols 1, rows 1 } } }

Output:
  "The architecture uses a 12×2 grid with a Presentation layer spanning 2 rows. 
   It contains a full-width Web UI module with a React App component."
```

### FR-5: DSL Refinement

**Description:** Update existing DSL based on user feedback.

**Details:**
- Input: Existing DSL + refinement instructions
- Process: Parse DSL, apply changes, regenerate with grid adjustments
- Output: Updated DSL

**Refinement Operations:**
- Add/remove layers (adjusting document grid rows)
- Add/remove modules (adjusting cols to sum to 12)
- Change grid dimensions
- Add/remove components (adjusting module grid)
- Update alignment and gap

---

## Non-Functional Requirements

### NFR-1: Performance

- DSL parsing: < 100ms for documents up to 500 lines
- Translation: < 2s for complex descriptions
- Validation: < 50ms per validation run

### NFR-2: Usability

- Error messages must include line numbers and specific issues
- Grid validation errors show expected vs actual sums
- Examples provided in skill documentation

### NFR-3: Compatibility

- DSL syntax compatible with PlantUML conventions where possible
- Output embeddable in standard markdown
- Works in X-IPE ideation workflow
- v1 DSL files can be migrated to v2 syntax

---

## UI/UX Requirements

**Not applicable** - This is a tool skill (backend/AI capability), not a frontend feature. The UI for viewing/editing DSL is handled by the content viewer (existing) and the Architecture Diagram Renderer (FEATURE-016).

**Integration Points:**
- DSL files stored in idea folders (`.dsl` extension)
- DSL embedded in markdown via ```architecture-dsl code blocks
- Stage Toolbox toggle for enabling/disabling skill

---

## Dependencies

### Internal Dependencies

- **FEATURE-011: Stage Toolbox** - Required for toolbox modal toggle (✅ Completed)
- **FEATURE-016: Architecture Diagram Renderer** - Will need updates for grid-based rendering

### External Dependencies

- None - This is a pure AI skill with no runtime dependencies

---

## Business Rules

### BR-1: Single View Per Document

**Rule:** Each DSL document contains exactly one view type (module-view OR landscape-view).

**Example:** Cannot mix layers and zones in the same document.

### BR-2: Alias Uniqueness

**Rule:** All aliases within a document must be unique.

**Example:** Cannot have `app "Web" as web` and `database "WebDB" as web`.

### BR-3: Flow Target Existence

**Rule:** Flow targets must reference defined aliases.

**Example:** `web --> hrm` requires both `web` and `hrm` to be defined.

### BR-4: Column Sum Validation (v2)

**Rule:** Module `cols` values within a layer MUST sum to exactly 12.

**Example:** `cols 4` + `cols 4` + `cols 4` = 12 ✓

### BR-5: Grid Hierarchy (v2)

**Rule:** Grid dimensions propagate down: document → layer → module → component.

**Example:** Document `grid 12 x 6`, layers must total 6 rows.

---

## Edge Cases & Constraints

### Edge Case 1: Empty Containers

**Scenario:** Layer, module, zone with no children.  
**Expected Behavior:** Valid DSL, renders as empty container.

### Edge Case 2: Deeply Nested Structures

**Scenario:** Layer > Module > Component with many levels.  
**Expected Behavior:** Maximum nesting: Layer → Module → Component (3 levels).

### Edge Case 3: Special Characters in Names

**Scenario:** Names containing quotes, special chars.  
**Expected Behavior:** Escape quotes with backslash: `"Module \"Core\""`

### Edge Case 4: Missing Alias in Flow

**Scenario:** Flow references undefined alias.  
**Expected Behavior:** Validation error with suggestion to define alias.

### Edge Case 5: Column Sum Mismatch (v2)

**Scenario:** Module `cols` sum to 10 instead of 12.  
**Expected Behavior:** Validation error: "Module cols sum to 10, expected 12".

### Edge Case 6: Component Overflow (v2)

**Scenario:** Component `cols` exceeds module grid columns.  
**Expected Behavior:** Validation error or wrap to next row.

---

## Out of Scope

- **Component diagrams** - Only Module View and Landscape View
- **Sequence diagrams** - Use Mermaid for sequence diagrams
- **Deployment diagrams** - Future version consideration
- **Real-time collaboration** - Single-user editing only
- **Interactive canvas editing** - DSL is text-based; diagram editing is view-only
- **Custom themes/colors** - Default styling only (colors specified per-element)
- **Import from other formats** - No import from PlantUML, Mermaid, etc.
- **Landscape View grid system** - v2 grid applies to Module View only

---

## Technical Considerations

- **Learning from `infographic-syntax-creator`**: Follow similar skill structure with grammar reference and examples
- **Grid validation**: Ensure `cols` sum to 12 at parse time
- **Migration path**: v1 DSL can be converted to v2 using migration guide
- **Syntax highlighting**: Frontend should highlight DSL keywords in editor
- **Code blocks**: Support ```architecture-dsl fenced code blocks in markdown
- **File extension**: Use `.dsl` for standalone DSL files

---

## Open Questions

- [x] ~~What file extension for standalone DSL files?~~ → Use `.dsl`
- [x] ~~Should we support themes/colors in v1.0?~~ → No, default styling only
- [x] ~~Maximum nesting depth?~~ → 3 levels (Layer → Module → Component)
- [x] ~~How to handle cross-layer alignment?~~ → 12-column grid ensures alignment (v2)
- [ ] Should Landscape View adopt grid system in future version?

---

## Linked Mockups

| Mockup | Description | Path |
|--------|-------------|------|
| Architecture DSL Demo v4 | DSL editor + rendered diagram | [mockups/architecture-dsl-demo.html](mockups/architecture-dsl-demo.html) |

---

## Specification Quality Checklist

- [x] All acceptance criteria are testable
- [x] User stories provide clear value
- [x] Functional requirements are complete
- [x] Non-functional requirements defined
- [x] Dependencies clearly stated
- [x] Edge cases identified
- [x] Out of scope explicitly listed
