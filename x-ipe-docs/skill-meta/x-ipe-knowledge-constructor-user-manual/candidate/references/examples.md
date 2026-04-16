# Constructor User Manual — Worked Examples

> One worked example per operation showing input, processing, and output.

---

## Example 1: provide_framework

**Scenario:** Create a user manual framework for a web dashboard application.

### Input

```yaml
operation: provide_framework
context:
  request_context:
    app_name: "DataViz Dashboard"
    app_type: "web"
    user_goal: "Create a comprehensive user manual for end users"
    source_paths:
      - "./src"
      - "./docs"
      - "./README.md"
  output_format: "markdown"
```

### Processing

1. **博学之:** Load `playbook-template.md` (8-section base). Load `mixin-web.md` (adds Authentication, Navigation, Browser Requirements, API Endpoints sections).
2. **审问之:** Validate app_type="web" → valid. app_name="DataViz Dashboard" → non-empty. source_paths → non-empty.
3. **慎思之:** Merge mixin into base: insert Authentication after Section 3, insert Navigation into Section 4 as first subsection, insert Browser Requirements into Section 2, insert API Endpoints into Section 8. Replace `{app_name}` → "DataViz Dashboard". Adapt "Your First {Action}" → "Your First Dashboard".
4. **明辨之:** Verify 8 base sections + 4 mixin additions present. toc_structure has 12 entries. No unresolved placeholders.
5. **笃行之:** Write to `.working/framework/dataviz-dashboard-framework.md`.

### Output

```yaml
operation_output:
  success: true
  operation: "provide_framework"
  result:
    framework_document:
      sections:
        - id: "1-overview"
          title: "Overview"
          stubs: "What is DataViz Dashboard?, Who is it for?, Key Features, How it works"
        - id: "2-installation-setup"
          title: "Installation & Setup"
          stubs: "Prerequisites, Installation, Initial Configuration, Verification, Browser Requirements"
        - id: "3-getting-started"
          title: "Getting Started"
          stubs: "Quick Start, Basic Workflow, Your First Dashboard"
        - id: "3a-authentication"
          title: "Authentication & Login"
          stubs: "Login Methods, Account Creation, Session Management, Password Recovery"
        - id: "4-core-features"
          title: "Core Features"
          stubs: "Navigation & UI Structure, (features to be populated)"
        - id: "5-common-workflows"
          title: "Common Workflow Scenarios"
          stubs: "(workflows to be populated)"
        - id: "6-configuration"
          title: "Configuration"
          stubs: "Configuration File, Environment Variables, Runtime Options, Profiles"
        - id: "7-troubleshooting"
          title: "Troubleshooting"
          stubs: "Common Issues, Error Messages, Diagnostic Steps, Getting Help"
        - id: "8-faq-reference"
          title: "FAQ & Reference"
          stubs: "FAQ, Glossary, Keyboard Shortcuts, Version History, API Endpoints"
    toc_structure:
      - { id: "1-overview", title: "Overview", depth: 1 }
      - { id: "2-installation-setup", title: "Installation & Setup", depth: 1 }
      - { id: "3-getting-started", title: "Getting Started", depth: 1 }
      - { id: "3a-authentication", title: "Authentication & Login", depth: 1 }
      - { id: "4-core-features", title: "Core Features", depth: 1 }
      - { id: "5-common-workflows", title: "Common Workflow Scenarios", depth: 1 }
      - { id: "6-configuration", title: "Configuration", depth: 1 }
      - { id: "7-troubleshooting", title: "Troubleshooting", depth: 1 }
      - { id: "8-faq-reference", title: "FAQ & Reference", depth: 1 }
    writes_to: "x-ipe-docs/memory/.working/framework/"
  errors: []
```

---

## Example 2: design_rubric

**Scenario:** Design quality rubric for the DataViz Dashboard manual, with user emphasis on "getting started" and "core features".

### Input

```yaml
operation: design_rubric
context:
  framework: { ... }  # framework_document from Example 1
  overview: "DataViz Dashboard is a web-based data visualization tool that lets teams create interactive charts, dashboards, and reports from multiple data sources."
  user_request: "I want the manual to really focus on getting started quickly and documenting all core features in detail. Configuration and troubleshooting are less important."
```

### Processing

1. **博学之:** Load `acceptance-criteria.md`. Parse user_request: "getting started" + "core features" = emphasis. "configuration" + "troubleshooting" = de-emphasis.
2. **审问之:** Framework valid (has sections). Overview non-empty. user_request non-empty.
3. **慎思之:** Assign weights: Getting Started → 3 (explicit emphasis), Core Features → 3 (explicit emphasis), Overview → 2 (default), Installation → 2 (default), Workflows → 2 (default), Configuration → 1 (user de-emphasized), Troubleshooting → 1 (user de-emphasized), FAQ → 1 (default).
4. **明辨之:** Every section has ≥1 metric. Weights are 1-3. Thresholds are testable.
5. **笃行之:** Write to `.working/rubric/dataviz-dashboard-rubric.md`.

### Output

```yaml
operation_output:
  success: true
  operation: "design_rubric"
  result:
    rubric_metrics:
      - { section_id: "1-overview", criteria: "Application description ≥2 sentences, ≥3 key features listed", weight: 2, threshold: "PASS: all [REQ] met" }
      - { section_id: "3-getting-started", criteria: "Quick start ≤5 steps, happy-path with ≥3 concrete steps, all steps have expected outcomes", weight: 3, threshold: "PASS: all [REQ] met including exact UI actions" }
      - { section_id: "4-core-features", criteria: "≥3 features documented with step-by-step instructions, interaction patterns classified, examples with output", weight: 3, threshold: "PASS: all [REQ] met including screenshots" }
      - { section_id: "6-configuration", criteria: "Config file documented, ≥1 env var, ≥3 settings", weight: 1, threshold: "PASS: all [REQ] met" }
      # ... (remaining sections)
    acceptance_criteria:
      - section_id: "3-getting-started"
        checks: ["GS-01: Quick start ≤5 steps", "GS-02: ≥3 steps with actions", "GS-03: ≥1 example with output", "GS-04: Exact UI actions", "GS-05: Expected outcomes", "GS-06: CLI dispatch Enter noted"]
      # ... (remaining sections)
    writes_to: "x-ipe-docs/memory/.working/rubric/"
  errors: []
```

---

## Example 3: request_knowledge

**Scenario:** Identify knowledge gaps after partial extraction — Overview is filled, Getting Started is empty, Core Features is partial.

### Input

```yaml
operation: request_knowledge
context:
  framework: { ... }  # from Example 1
  current_state:
    filled_sections: ["1-overview", "2-installation-setup", "6-configuration"]
    empty_sections: ["3-getting-started", "5-common-workflows", "7-troubleshooting", "8-faq-reference"]
    partial_sections: ["4-core-features"]
  rubric: { ... }  # from Example 2
```

### Processing

1. **博学之:** Load `collection-template.md` extraction patterns. Build section inventory from framework.
2. **审问之:** Framework valid. current_state has all three arrays. Rubric present.
3. **慎思之:** Walk sections — skip filled (1, 2, 6). For empty section "3-getting-started" (weight=3): generate request for quickstart guide, basic workflow, first dashboard tutorial. suggested_extractor="extractor-web" (needs live source). For partial "4-core-features" (weight=3): generate request for remaining feature details. For empty "5-common-workflows" (weight=2): request workflow patterns. Priority by weight descending.
4. **明辨之:** Each request has target_section, what_needed, suggested_extractor, priority. All specific.
5. **笃行之:** Write to `.working/plan/dataviz-dashboard-plan.md`.

### Output

```yaml
operation_output:
  success: true
  operation: "request_knowledge"
  result:
    knowledge_requests:
      - target_section: "3-getting-started"
        what_needed: "Extract quickstart guide: minimal steps to create first dashboard from a data source. Look for QUICKSTART.md, README 'Getting Started', examples/ directory. Need step-by-step with exact UI actions and expected outcomes."
        suggested_extractor: "extractor-web"
        priority: 3

      - target_section: "4-core-features"
        what_needed: "Complete feature documentation for: chart builder, data source connector, sharing/export. Need interaction patterns, step-by-step instructions, and screenshots for each."
        suggested_extractor: "extractor-web"
        priority: 3

      - target_section: "5-common-workflows"
        what_needed: "Identify ≥3 end-to-end workflows: e.g., 'Create dashboard from CSV', 'Share dashboard with team', 'Schedule report email'. Look for tutorials, integration tests, example scripts."
        suggested_extractor: "extractor-web"
        priority: 2

      - target_section: "7-troubleshooting"
        what_needed: "Extract common issues from TROUBLESHOOTING.md, GitHub Issues, error handling code. Need ≥3 issues with symptoms and solutions."
        suggested_extractor: "extractor-memory"
        priority: 1

      - target_section: "8-faq-reference"
        what_needed: "Extract FAQ from FAQ.md or docs, glossary of DataViz-specific terms, keyboard shortcuts if any, version history from CHANGELOG.md."
        suggested_extractor: "extractor-memory"
        priority: 1
    writes_to: "x-ipe-docs/memory/.working/plan/"
  errors: []
```

---

## Example 4: fill_structure

**Scenario:** Assemble the final draft with gathered knowledge. Most sections covered, but troubleshooting is thin.

### Input

```yaml
operation: fill_structure
context:
  framework: { ... }  # from Example 1
  gathered_knowledge:
    - section_id: "3-getting-started"
      content: "## Quick Start\n1. Navigate to https://app.dataviz.io\n2. Click 'New Dashboard'..."
      source: "extractor-web: README.md + live app walkthrough"
      metadata: { extracted_at: "2025-07-16", completeness: "full" }
    - section_id: "4-core-features"
      content: "### Feature 01: Chart Builder\n**Interaction Pattern:** FORM\n..."
      source: "extractor-web: source code + live app"
      metadata: { extracted_at: "2025-07-16", completeness: "full" }
    - section_id: "5-common-workflows"
      content: "### Workflow 01: Create Dashboard from CSV\n**Goal:** Import CSV data..."
      source: "extractor-web: tutorials/ + examples/"
      metadata: { extracted_at: "2025-07-16", completeness: "full" }
    - section_id: "7-troubleshooting"
      content: "## Common Issues\n1. Connection timeout..."
      source: "extractor-memory: existing troubleshooting notes"
      metadata: { extracted_at: "2025-07-16", completeness: "partial" }
    - section_id: "8-faq-reference"
      content: "## FAQ\n**Q: What data sources are supported?** ..."
      source: "extractor-memory: FAQ.md"
      metadata: { extracted_at: "2025-07-16", completeness: "full" }
  rubric: { ... }  # from Example 2
```

### Processing

1. **博学之:** Index gathered_knowledge by section_id. Load framework toc_structure for ordering.
2. **审问之:** Framework valid. gathered_knowledge has 5 entries. Rubric present.
3. **慎思之:** Map each section — Sections 1, 2, 6 already filled from earlier. Section 3 (Getting Started) → map content, validate against rubric GS-01 through GS-06 → PASS. Section 4 (Core Features) → PASS. Section 5 → PASS. Section 7 (Troubleshooting) → check rubric TS-01: ≥3 issues? Only 1 found → mark `[INCOMPLETE: Only 1 of 3 required common issues documented. Need ≥2 more issues with symptoms and solutions.]`. Section 8 → PASS.
4. **明辨之:** All sections present. 1 incomplete section marked. TOC links match sections. Completeness: 8/9 sections complete = 88%.
5. **笃行之:** Write to `.working/draft/dataviz-dashboard-user-manual.md`.

### Output

```yaml
operation_output:
  success: true
  operation: "fill_structure"
  result:
    completed_draft: |
      # DataViz Dashboard — User Manual

      ## Table of Contents
      1. [Overview](#1-overview)
      2. [Installation & Setup](#2-installation-setup)
      3. [Getting Started](#3-getting-started)
      ...

      ## 1. Overview
      (previously filled content)

      ## 3. Getting Started
      ### Quick Start
      1. Navigate to https://app.dataviz.io
      2. Click 'New Dashboard'
      ...

      ## 7. Troubleshooting
      ### Common Issues
      1. Connection timeout...
      [INCOMPLETE: Only 1 of 3 required common issues documented. Need ≥2 more issues with symptoms and solutions.]
      ...
    completeness_score: 0.88
    writes_to: "x-ipe-docs/memory/.working/draft/"
  errors: []
```

**Next step for orchestrator:** The Librarian sees the `[INCOMPLETE]` marker and the 88% score, and may call `request_knowledge` again to fill the gap, or accept the draft as-is and call `keeper-memory.promote()` to persist it.
