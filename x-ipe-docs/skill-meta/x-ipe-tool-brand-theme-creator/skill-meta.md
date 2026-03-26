# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-brand-theme-creator
skill_type: x-ipe-tool
version: "2.0.0"
status: candidate
created: 2026-03-25
updated: 2026-03-25

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Transform brand colors, typography, and UI component patterns into complete theme packages.
  Now extracts basic UI components (buttons, cards, inputs, links, badges, navigation) from
  reference materials in addition to colors and fonts.

triggers:
  - "create theme"
  - "new brand theme"
  - "generate design system"
  - "add custom theme"

not_for:
  - "application-level CSS or component library code"
  - "runtime theme switching logic"
  - "complex component interactions or JavaScript behavior"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: theme_name
      type: string
      description: "kebab-case name without 'theme-' prefix (e.g., ocean, corporate)"
      validation: "Must be a valid kebab-case identifier"

    - name: accent_color
      type: string
      description: "hex color value (e.g., #3b82f6) OR derived from source"
      validation: "Valid hex color or derivable from source_value"

  optional:
    - name: source_type
      type: string
      default: "direct"
      description: "Input source type: web_link | image | text_description | direct"

    - name: source_value
      type: string
      default: null
      description: "URL, image path, or text description"

    - name: primary_color
      type: string
      default: "derived: darken accent by 40%"
      description: "Primary color hex override"

    - name: secondary_color
      type: string
      default: "derived: desaturate + darken by 20%"
      description: "Secondary color hex override"

    - name: neutral_color
      type: string
      default: "derived: very light tint of accent"
      description: "Neutral color hex override"

    - name: heading_font
      type: string
      default: "Inter"
      description: "Heading font family"

    - name: body_font
      type: string
      default: "system-ui"
      description: "Body font family"

    - name: code_font
      type: string
      default: "JetBrains Mono"
      description: "Code/monospace font family"

    - name: border_radius_md
      type: string
      default: "8px"
      description: "Medium border radius value"

    - name: extract_components
      type: boolean
      default: true
      description: "Whether to extract UI component patterns from source material"

outputs:
  state:
    - name: status
      value: completed | blocked

  artifacts:
    - name: design_system
      type: file
      description: "design-system.md with structured token definitions"
    - name: visualization
      type: file
      description: "component-visualization.html with visual preview and JSON-LD"

  data:
    - name: theme_name
      type: string
      description: "Final theme folder name (with theme- prefix)"
    - name: source_type
      type: string
      description: "web_link | image | text_description | direct"
    - name: colors_confirmed
      type: boolean
      description: "Whether user confirmed the color palette"
    - name: components_extracted
      type: list
      description: "List of component types extracted from source"
    - name: components_derived
      type: list
      description: "List of component types using defaults"

# ─────────────────────────────────────────────────────────────
# CHANGE DESCRIPTION (v1.0 → v2.0.0)
# ─────────────────────────────────────────────────────────────
change_description: |
  Add UI component extraction from reference materials. The skill now extracts basic
  UI component patterns (buttons, cards, inputs, links, badges, navigation) from web
  links, images, and text descriptions in addition to colors and fonts. Component
  extraction is best-effort with sensible defaults as fallback. New reference file
  references/component-extraction.md documents extraction patterns, defaults, and
  merge logic. Templates updated with component placeholders.

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    # STRUCTURE
    - id: AC-S01
      category: structure
      criterion: SKILL.md updated with component extraction steps and references
      test: content_check
      expected: "SKILL.md contains extract_components input, component extraction in Step 1, and references/component-extraction.md link"

    - id: AC-S02
      category: structure
      criterion: references/component-extraction.md exists with extraction patterns
      test: file_exists
      expected: "file at .github/skills/x-ipe-tool-brand-theme-creator/references/component-extraction.md"

    - id: AC-S03
      category: structure
      criterion: design-system-template.md includes component specs for all 6 types
      test: content_check
      expected: "template contains sections for Buttons, Cards, Form Inputs, Links, Badges, Navigation"

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Theme generation still works with extract_components=false (backward compatible)
      test: execution
      expected: "Theme generates with only color/font tokens when components disabled"

    - id: AC-B02
      category: behavior
      criterion: Component extraction produces at least buttons, cards, inputs specs when source contains visible components
      test: execution
      expected: "Generated design-system.md contains Buttons, Cards, Form Inputs sections with extracted values"

    - id: AC-B03
      category: behavior
      criterion: Missing components fall back to derived defaults without blocking
      test: execution
      expected: "Theme generates successfully even when no components can be extracted"

    # CONTRACT
    - id: AC-C01
      category: contract
      criterion: design-system.md generated at x-ipe-docs/themes/theme-{name}/
      test: file_exists
      expected: "design-system.md exists with all token sections"

    - id: AC-C02
      category: contract
      criterion: component-visualization.html generated with no unreplaced placeholders
      test: content_check
      expected: "No {{PLACEHOLDER}} strings remain in output"

    - id: AC-C03
      category: contract
      criterion: JSON-LD block present in visualization
      test: content_check
      expected: "component-visualization.html contains JSON-LD structured data"

    - id: AC-C04
      category: contract
      criterion: All colors in hex format
      test: content_check
      expected: "No RGB or HSL color values in token definitions"

    - id: AC-C05
      category: contract
      criterion: Contrast ratios meet accessibility requirements
      test: validation
      expected: "Primary/secondary on white >= 4.5:1, accent on white >= 3:1"

    - id: AC-C06
      category: contract
      criterion: User confirmed palette before generation
      test: process_check
      expected: "Colors presented to and confirmed by user in Step 2"

    - id: AC-C07
      category: contract
      criterion: Theme folder uses theme- prefix
      test: validation
      expected: "Folder name starts with theme-"

    - id: AC-C08
      category: contract
      criterion: Component Specs section includes extracted values with fallback defaults
      test: content_check
      expected: "design-system.md Component Specs has at least buttons, cards, inputs with either extracted or default values"

  should:
    - id: AC-B04
      category: behavior
      criterion: Web link extraction identifies button, card, and input patterns from CSS
      test: execution
      expected: "CSS selectors for buttons, cards, inputs are scanned and properties extracted"

    - id: AC-B05
      category: behavior
      criterion: Image input estimates component styles from visual appearance
      test: execution
      expected: "Vision analysis maps visible UI components to token values"

  could:
    - id: AC-B06
      category: behavior
      criterion: Text description maps style keywords to component patterns
      test: execution
      expected: "Keywords like 'modern', 'playful' produce distinct component styles"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Web link with component extraction"
      given: "URL with visible buttons, cards, and form inputs"
      when: "Theme created with extract_components=true"
      then: "design-system.md contains extracted component values for buttons, cards, inputs"

    - name: "Direct hex input with default components"
      given: "Accent color #3b82f6, no source material"
      when: "Theme created with extract_components=true"
      then: "design-system.md contains derived default component values"

    - name: "Image input with component identification"
      given: "Screenshot showing UI mockup with buttons and cards"
      when: "Theme created from image"
      then: "Components estimated from visual appearance and mapped to tokens"

  error_cases:
    - name: "Component extraction disabled"
      given: "extract_components=false"
      when: "Theme created"
      then: "Component Specs section uses all defaults, no extraction attempted"

    - name: "Source has no visible components"
      given: "Logo image with no UI elements"
      when: "Theme created with extract_components=true"
      then: "All components use defaults, theme generates successfully"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "Both design-system.md and component-visualization.html generated"
    - "No unreplaced {{PLACEHOLDER}} strings in output"
    - "JSON-LD block present in HTML"
    - "Component Specs section has at least buttons, cards, inputs"
    - "Extracted values take precedence over defaults"
    - "Theme folder uses theme- prefix"
