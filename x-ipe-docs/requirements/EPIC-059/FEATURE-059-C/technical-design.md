# Technical Design: Layer 2 — Domain Skills (Constructors + Mimic + Ontology-Builder)

> Feature ID: FEATURE-059-C | Version: v1.4 | Last Updated: 2026-04-27

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating large projects.
> **📌 AI Coders:** Focus on this section for implementation context.

### Key Components Implemented

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| `x-ipe-knowledge-constructor-user-manual` | Domain expert for user manual construction (4 ops: framework, rubric, request_knowledge, fill_structure) | Absorbs `x-ipe-tool-knowledge-extraction-user-manual` | #knowledge #constructor #user-manual #domain-expert |
| `x-ipe-knowledge-constructor-notes` | Domain expert for knowledge notes construction (same 4-op interface) | Absorbs `x-ipe-tool-knowledge-extraction-notes` | #knowledge #constructor #notes #domain-expert |
| `x-ipe-knowledge-constructor-app-reverse-engineering` | Domain expert for RE reports (same 4-op interface, delegates to `x-ipe-tool-rev-eng-*`) | Absorbs `x-ipe-tool-knowledge-extraction-application-reverse-engineering` | #knowledge #constructor #reverse-engineering #domain-expert |
| `x-ipe-knowledge-mimic-web-behavior-tracker` | Observe & record user behavior on websites via Chrome DevTools MCP. **CR-001:** adds active polling/reinject/screenshot support. **CR-002:** `start_active_tracking` owns polling until toolbar Analysis, consolidates observations, then returns payload to DAO. | Absorbs `x-ipe-tool-learning-behavior-tracker-for-web`, writes to `x-ipe-docs/.mimicked/` | #knowledge #mimic #behavior-tracker #chrome-devtools |
| `x-ipe-assistant-knowledge-librarian-DAO` | Central knowledge pipeline router. **CR-002:** classifies behavior-learning requests as mimic tasks, delegates to mimic `start_active_tracking`, and consumes returned observations as gathered knowledge. | Integrates mimic observations into pipeline state | #assistant #dao #librarian #mimic-routing |
| `x-ipe-knowledge-ontology-builder` | Build ontology graph (classes, instances, vocabulary) from source knowledge via iterative discover-critique-implement loop (single `build_ontology` op) | Absorbs build ops from retired `x-ipe-tool-ontology`, writes directly to `.ontology/` with `lifecycle` flag | #knowledge #ontology #builder #graph |
| Deprecation/retirement | Add migration pointers to old extraction tools; retire redundant behavior tracker tool after CR-001 parity | Old extraction tools keep deprecation banners; behavior tracker tool removed | #deprecation #migration |

### Dependencies

| Dependency | Source | Design Link | Usage Description |
|------------|--------|-------------|-------------------|
| `x-ipe-knowledge` template | FEATURE-059-A | [technical-design.md](x-ipe-docs/requirements/EPIC-059/FEATURE-059-A/technical-design.md) | Template for all 5 SKILL.md files — Operations+Steps hybrid pattern |
| `x-ipe-knowledge-keeper-memory` | FEATURE-059-B | [technical-design.md](x-ipe-docs/requirements/EPIC-059/FEATURE-059-B/technical-design.md) | Constructors reference keeper-memory for promotion. Ontology-builder doesn't depend on it |
| `x-ipe-knowledge-extractor-web` | FEATURE-059-B | [technical-design.md](x-ipe-docs/requirements/EPIC-059/FEATURE-059-B/technical-design.md) | Constructors reference as `suggested_extractor` in `request_knowledge` output |
| `x-ipe-knowledge-extractor-memory` | FEATURE-059-B | [technical-design.md](x-ipe-docs/requirements/EPIC-059/FEATURE-059-B/technical-design.md) | Constructors reference as `suggested_extractor` in `request_knowledge` output |
| `x-ipe-meta-skill-creator` | Foundation | [SKILL.md](.github/skills/x-ipe-meta-skill-creator/SKILL.md) | Skill creation workflow — candidate → production merge |
| `x-ipe-tool-rev-eng-*` (8 sub-skills) | Existing | [SKILL.md](.github/skills/x-ipe-tool-rev-eng-api-contract-extraction/SKILL.md) | Referenced by constructor-app-RE for section-level extraction |
| `x-ipe-tool-learning-behavior-tracker-for-web` | Retired | N/A | Removed after CR-001 parity; replaced by `x-ipe-knowledge-mimic-web-behavior-tracker` |
| `x-ipe-tool-ontology/scripts/ontology.py` | Existing | [SKILL.md](.github/skills/x-ipe-tool-ontology/SKILL.md) | Reference for JSONL format, entity CRUD patterns, validation logic |
| Chrome DevTools MCP | External | N/A | Runtime dependency for mimic (navigate_page, evaluate_script) |

### Major Flow

**Constructor Workflow (all 3 constructors share this):**
1. Librarian calls `provide_framework(request_context)` → constructor loads domain template → returns `framework_document` + `toc_structure` → written to `.working/framework/`
2. Librarian calls `design_rubric(framework, overview, user_request)` → constructor defines measurable criteria → returns `rubric_metrics[]` → written to `.working/rubric/`
3. Librarian calls `request_knowledge(framework, current_state, rubric)` → constructor identifies gaps → returns `knowledge_requests[]` (with `suggested_extractor`) → written to `.working/plan/`
4. Librarian dispatches extractors for each knowledge request → gathers knowledge
5. Librarian calls `fill_structure(framework, gathered_knowledge[], rubric)` → constructor maps knowledge to sections → returns `completed_draft` → written to `.working/draft/`
6. Librarian calls `keeper-memory.promote()` to persist the draft

**Mimic Workflow:**
1. Librarian calls `start_tracking(target_app, session_config)` → mimic navigates via Chrome DevTools → injects IIFE → returns `tracking_session_id` → session data in `x-ipe-docs/.mimicked/`
2. User interacts with the website (events captured in circular buffer)
3. Librarian calls `stop_tracking(session_id)` → events collected → post-processed → `observation_summary` + `raw_events[]` written to `x-ipe-docs/.mimicked/`
4. Librarian calls `get_observations(session_id, filter)` → read-only retrieval of observations

**Ontology-Builder Workflow:**
1. Librarian calls `build_ontology(source_content, depth_limit)` → builder reads source content → produces content overview → proposes initial ontology graph (classes, instances, vocabulary)
2. Builder launches critique sub-agent → evaluates existing `.ontology/` for reuse → returns constructive feedback {reuse, modify, create_new, skip}
3. Builder implements changes based on feedback → writes classes to `schema/`, instances to `instances/`, vocabulary to `vocabulary/`
4. Builder selects next unprocessed node → reads linked source_files in depth → discovers finer-grained classes/properties/instances → loops back to step 2
5. Loop terminates when: depth_limit reached (1=flat, 3=standard) or rubric metrics hit 100% (auto mode, safety cap at 10 iterations)
6. Builder returns `build_report` with ontology_summary, rubric_scores, iterations_completed

### Usage Example

```yaml
# Librarian calling constructor-user-manual.provide_framework
operation: provide_framework
context:
  request_context:
    app_name: "MyFlaskApp"
    app_type: "web"
    user_goal: "Create comprehensive user manual"
  output_format: "manual"
# Returns:
#   framework_document: { sections: [Overview, Getting Started, Features, ...], template: "user-manual-web" }
#   toc_structure: [{ id: "01", title: "Overview", stubs: [...] }, ...]

# Librarian calling constructor-user-manual.request_knowledge
operation: request_knowledge
context:
  framework: { ... }  # from provide_framework
  current_state: { filled_sections: ["01.Overview"], empty: ["02.Getting Started", "03.Features"] }
  rubric: { ... }  # from design_rubric
# Returns:
#   knowledge_requests:
#     - { target_section: "02", what_needed: "Setup instructions with prerequisites", suggested_extractor: "extractor-web" }
#     - { target_section: "03", what_needed: "List of app features from source code", suggested_extractor: "extractor-memory" }

# Librarian calling ontology-builder.build_ontology
operation: build_ontology
context:
  source_content:
    - "x-ipe-docs/memory/semantic/flask-jinja2-templating.md"
    - "x-ipe-docs/memory/semantic/python-web-frameworks.md"
  depth_limit: "auto"
# Returns:
#   build_report:
#     ontology_summary: { classes_created: 5, instances_created: 12, vocabulary_terms_added: 8, classes_reused: 2 }
#     rubric_scores: { concept_coverage: 1.0, instance_coverage: 1.0, vocabulary_coverage: 1.0, hierarchy_coherence: 1.0 }
#     iterations_completed: 3
#     depth_reached: 3
```

---

## Part 2: Implementation Guide

> **Purpose:** Human-readable details for developers.
> **📌 Emphasis on visual diagrams for comprehension.**

### Deliverables

| ID | Deliverable | Type | Path | ACs Covered |
|----|-------------|------|------|-------------|
| D1 | constructor-user-manual SKILL.md | Knowledge Skill | `.github/skills/x-ipe-knowledge-constructor-user-manual/SKILL.md` | AC-059C-01a, 02, 03, 04, 15 |
| D1t | constructor-user-manual templates/ | Templates | `.github/skills/x-ipe-knowledge-constructor-user-manual/templates/` | AC-059C-05a |
| D1r | constructor-user-manual references/ | Examples | `.github/skills/x-ipe-knowledge-constructor-user-manual/references/examples.md` | AC-059C-05d |
| D2 | constructor-notes SKILL.md | Knowledge Skill | `.github/skills/x-ipe-knowledge-constructor-notes/SKILL.md` | AC-059C-01b, 02, 03, 04, 15 |
| D2t | constructor-notes templates/ | Templates | `.github/skills/x-ipe-knowledge-constructor-notes/templates/` | AC-059C-05b |
| D2r | constructor-notes references/ | Examples | `.github/skills/x-ipe-knowledge-constructor-notes/references/examples.md` | AC-059C-05d |
| D3 | constructor-app-RE SKILL.md | Knowledge Skill | `.github/skills/x-ipe-knowledge-constructor-app-reverse-engineering/SKILL.md` | AC-059C-01c, 02, 03, 04, 15 |
| D3t | constructor-app-RE templates/ | Templates | `.github/skills/x-ipe-knowledge-constructor-app-reverse-engineering/templates/` | AC-059C-05c |
| D3r | constructor-app-RE references/ | Examples | `.github/skills/x-ipe-knowledge-constructor-app-reverse-engineering/references/examples.md` | AC-059C-05d |
| D4 | mimic-web-behavior-tracker SKILL.md | Knowledge Skill | `.github/skills/x-ipe-knowledge-mimic-web-behavior-tracker/SKILL.md` | AC-059C-06, 07, 08, 15 |
| D4s | mimic scripts/ | Python + JS | `.github/skills/x-ipe-knowledge-mimic-web-behavior-tracker/scripts/` | AC-059C-06, 07, 15d |
| D4r | mimic references/ | Examples | `.github/skills/x-ipe-knowledge-mimic-web-behavior-tracker/references/examples.md` | AC-059C-05d equivalent |
| D5 | ontology-builder SKILL.md | Knowledge Skill | `.github/skills/x-ipe-knowledge-ontology-builder/SKILL.md` | AC-059C-09–13, 14, 15 |
| D5s | ontology-builder scripts/ | Python | `.github/skills/x-ipe-knowledge-ontology-builder/scripts/` | AC-059C-09c, 11, 13, 14, 15e |
| D5r | ontology-builder references/ | Examples | `.github/skills/x-ipe-knowledge-ontology-builder/references/examples.md` | AC-059C-05d equivalent |
| D6 | Deprecation: knowledge-extraction-user-manual | Edit | `.github/skills/x-ipe-tool-knowledge-extraction-user-manual/SKILL.md` | AC-059C-16a |
| D7 | Deprecation: knowledge-extraction-notes | Edit | `.github/skills/x-ipe-tool-knowledge-extraction-notes/SKILL.md` | AC-059C-16b |
| D8 | Deprecation: knowledge-extraction-app-RE | Edit | `.github/skills/x-ipe-tool-knowledge-extraction-application-reverse-engineering/SKILL.md` | AC-059C-16c |
| D9 | Retirement: learning-behavior-tracker | Remove | `.github/skills/x-ipe-tool-learning-behavior-tracker-for-web/` | Superseded by AC-059C-17 |

### Workflow Diagram — Librarian ↔ Domain Skills

```mermaid
sequenceDiagram
    participant L as Librarian (Orchestrator)
    participant CUM as constructor-user-manual
    participant EW as extractor-web
    participant EM as extractor-memory
    participant KM as keeper-memory
    participant OB as ontology-builder

    Note over L: Phase 1: Framework
    L->>CUM: provide_framework(request_context)
    CUM-->>L: framework_document + toc_structure
    Note right of CUM: writes to .working/framework/

    Note over L: Phase 2: Rubric
    L->>CUM: design_rubric(framework, overview, user_request)
    CUM-->>L: rubric_metrics[]
    Note right of CUM: writes to .working/rubric/

    Note over L: Phase 3: Knowledge Requests
    L->>CUM: request_knowledge(framework, current_state, rubric)
    CUM-->>L: knowledge_requests[]
    Note right of CUM: writes to .working/plan/

    Note over L: Phase 4: Dispatch Extractors
    par For each knowledge request
        L->>EW: extract_details(url, scope)
        EW-->>L: extracted_content
    and
        L->>EM: extract_overview(query)
        EM-->>L: overview_content
    end

    Note over L: Phase 5: Fill Structure
    L->>CUM: fill_structure(framework, gathered_knowledge[], rubric)
    CUM-->>L: completed_draft
    Note right of CUM: writes to .working/draft/

    Note over L: Phase 6: Persist
    L->>KM: promote(working_path, memory_type)
    KM-->>L: promoted_path

    Note over L: Phase 7: Ontology
    L->>OB: build_ontology(source_content, depth_limit="auto")
    OB-->>L: build_report {ontology_summary, rubric_scores, iterations}
```

### Workflow Diagram — Mimic Tracking Session

```mermaid
sequenceDiagram
    participant L as Librarian
    participant M as mimic-web-behavior-tracker
    participant CD as Chrome DevTools MCP
    participant FS as File System (.mimicked/)

    L->>M: start_tracking(target_app, session_config)
    M->>CD: navigate_page(url)
    CD-->>M: Page loaded
    M->>CD: evaluate_script(tracker-toolbar.mini.js)
    CD-->>M: IIFE injected (guard set)
    M->>FS: Create session directory
    M-->>L: tracking_session_id

    Note over CD: User interacts (events in circular buffer)

    L->>M: stop_tracking(session_id)
    M->>CD: evaluate_script(collectEvents())
    CD-->>M: raw_events[]
    M->>M: post_processor.py (flow narrative, key paths, pain points)
    M->>FS: Write observation_summary + raw_events
    M-->>L: observation_summary + raw_events[]

    L->>M: get_observations(session_id, filter)
    M->>FS: Read observations
    M-->>L: observations[] (read-only)
```

### Workflow Diagram — Ontology-Builder Pipeline

```mermaid
sequenceDiagram
    participant L as Librarian
    participant OB as ontology-builder
    participant C as Critique Sub-Agent
    participant O as .ontology/

    Note over L: Single call: build_ontology
    L->>OB: build_ontology(source_content, depth_limit)

    Note over OB: Step 1: Learn Content
    OB->>OB: Read source_content → content overview
    OB->>O: Load existing classes, instances, vocabulary

    Note over OB: Step 2: Suggest Basic Ontology Graph
    OB->>OB: Propose classes[], instances[], vocabulary[]

    loop Iterative Refinement (Steps 3–6)
        Note over OB: Step 3: Critique
        OB->>C: Evaluate proposed graph vs existing .ontology/
        C-->>OB: feedback {reuse[], modify[], create_new[], skip[]}

        Note over OB: Step 4: Implement
        OB->>O: register_class, create_instance, add_vocabulary
        OB->>O: validate_terms (consistency check)

        Note over OB: Depth Check
        alt depth_limit reached OR rubric 100%
            OB->>OB: Break loop
        else More nodes to explore
            Note over OB: Step 5: Select next node
            OB->>OB: Pick node with richest unexplored content

            Note over OB: Step 6: Learn details
            OB->>OB: Read source_files for selected node
            OB->>OB: Discover finer-grained classes/properties/instances
        end
    end

    OB-->>L: build_report {ontology_summary, rubric_scores, iterations}
```

### Class Diagram — Skill Structure

```mermaid
classDiagram
    class ConstructorInterface {
        <<Interface>>
        +provide_framework(request_context, output_format) FrameworkResult
        +design_rubric(framework, overview, user_request) RubricResult
        +request_knowledge(framework, current_state, rubric) KnowledgeRequests
        +fill_structure(framework, gathered_knowledge[], rubric) DraftResult
    }

    class ConstructorUserManual {
        <<Knowledge Skill>>
        templates/playbook-template.md
        templates/collection-template.md
        templates/acceptance-criteria.md
        templates/mixin-web.md
        templates/mixin-cli.md
        templates/mixin-mobile.md
        references/examples.md
    }

    class ConstructorNotes {
        <<Knowledge Skill>>
        templates/general-template.md
        templates/overview-template.md
        references/examples.md
    }

    class ConstructorAppRE {
        <<Knowledge Skill>>
        templates/playbook-template.md
        templates/mixin-*.md (repo/lang)
        references/examples.md
    }

    class MimicWebBehaviorTracker {
        <<Knowledge Skill>>
        +start_tracking(target_app, session_config) SessionId
        +stop_tracking(session_id) ObservationResult
        +get_observations(session_id, filter) Observations
        scripts/tracker-toolbar.js
        scripts/tracker-toolbar.mini.js
        scripts/post_processor.py
        references/examples.md
    }

    class OntologyBuilder {
        <<Knowledge Skill>>
        +build_ontology(source_content[], depth_limit) BuildReport
        scripts/ontology_ops.py
        references/examples.md
    }

    ConstructorInterface <|.. ConstructorUserManual
    ConstructorInterface <|.. ConstructorNotes
    ConstructorInterface <|.. ConstructorAppRE

    class WorkingFolder {
        <<File System>>
        .working/framework/
        .working/rubric/
        .working/plan/
        .working/draft/
    }

    class MimickedFolder {
        <<File System>>
        x-ipe-docs/.mimicked/
    }

    class OntologyFolder {
        <<File System>>
        .ontology/schema/
        .ontology/instances/
        .ontology/vocabulary/
    }

    ConstructorUserManual ..> WorkingFolder : writes to
    ConstructorNotes ..> WorkingFolder : writes to
    ConstructorAppRE ..> WorkingFolder : writes to
    MimicWebBehaviorTracker ..> MimickedFolder : writes to
    OntologyBuilder ..> OntologyFolder : writes to
```

---

### D1–D3: Constructor Skills (Shared 4-Operation Interface)

All three constructors implement the same 4-operation interface with domain-specific templates. The SKILL.md structure is identical — only the domain content differs.

**Common SKILL.md structure (x-ipe-knowledge template):**

```
SKILL.md
├── Purpose
├── Important Notes
├── About (domain description)
├── When to Use
├── Input Parameters (per-operation)
├── Definition of Ready
├── Operations
│   ├── Operation 1: provide_framework
│   │   ├── Contract (input/output/writes_to/constraints)
│   │   └── Steps (博学之→笃行之 backbone)
│   ├── Operation 2: design_rubric
│   ├── Operation 3: request_knowledge
│   └── Operation 4: fill_structure
├── Output Result
├── Definition of Done
├── Error Handling
└── Examples → references/examples.md
```

**Operation contracts (shared across all 3 constructors):**

```yaml
operation: provide_framework
input:
  request_context: dict          # {app_name, app_type, user_goal, source_paths[]}
  output_format: string          # Domain-specific format hint
output:
  framework_document: dict       # Complete structural outline
  toc_structure: object[]        # [{id, title, stubs, depth}]
writes_to: x-ipe-docs/memory/.working/framework/
constraints:
  - Load domain template from templates/ folder
  - Adapt template to request context (e.g., CLI app → add Commands section)
  - Return framework with section stubs (placeholder content)
```

```yaml
operation: design_rubric
input:
  framework: dict                # From provide_framework
  overview: string               # Overview/summary of the target app
  user_request: string           # Original user goal/emphasis
output:
  rubric_metrics: object[]       # [{section_id, criteria, weight, threshold}]
  acceptance_criteria: object[]  # [{section_id, checks[]}]
writes_to: x-ipe-docs/memory/.working/rubric/
constraints:
  - Per-section completeness criteria (measurable)
  - Per-section accuracy criteria
  - Weight by user emphasis (higher weight = higher priority for extraction)
```

```yaml
operation: request_knowledge
input:
  framework: dict                # From provide_framework
  current_state: dict            # {filled_sections[], empty_sections[], partial_sections[]}
  rubric: dict                   # From design_rubric
output:
  knowledge_requests: object[]   # [{target_section, what_needed, suggested_extractor, priority}]
writes_to: x-ipe-docs/memory/.working/plan/
constraints:
  - Walk framework sections, compare to current_state
  - For each gap, generate specific request (not vague)
  - suggested_extractor: "extractor-web" or "extractor-memory"
  - Prioritize by rubric weight (high-weight gaps first)
  - Return empty array if no gaps
```

```yaml
operation: fill_structure
input:
  framework: dict                # From provide_framework
  gathered_knowledge: object[]   # [{section_id, content, source, metadata}]
  rubric: dict                   # From design_rubric
output:
  completed_draft: string        # Full document mapped to framework
writes_to: x-ipe-docs/memory/.working/draft/
constraints:
  - Map gathered knowledge to framework sections
  - Mark incomplete sections with [INCOMPLETE: reason]
  - Validate against rubric criteria
  - Do NOT write to persistent memory (keeper-memory handles promotion)
```

#### D1: constructor-user-manual — Domain Specifics

**Domain template structure:** User manual with 8 standard sections:
1. Overview / Introduction
2. Getting Started (prerequisites, installation, first-use)
3. Core Features / Functionality
4. UI Walkthrough (web) / Commands (CLI) / Screens (mobile)
5. API Reference (if applicable)
6. Configuration & Customization
7. Troubleshooting & FAQ
8. Appendix / Glossary

**templates/ folder** — migrate and adapt from `x-ipe-tool-knowledge-extraction-user-manual/templates/`:

| File | Source | Adaptation |
|------|--------|------------|
| `playbook-template.md` | `x-ipe-tool-knowledge-extraction-user-manual/templates/playbook-template.md` | Rewrite as `provide_framework` input template. Keep 8-section layout |
| `collection-template.md` | Same source path | Rewrite as `request_knowledge` prompt templates per section |
| `acceptance-criteria.md` | Same source path | Rewrite as `design_rubric` criteria definitions per section |
| `mixin-web.md` | Same source path | App-type overlay for web apps (adds UI Walkthrough section) |
| `mixin-cli.md` | Same source path | App-type overlay for CLI apps (adds Commands section) |
| `mixin-mobile.md` | Same source path | App-type overlay for mobile apps (adds Screens section) |

#### D2: constructor-notes — Domain Specifics

**Domain template structure:** General knowledge notes with flexible hierarchy:
1. Overview (linked table of contents)
2. Key Insights / Main Sections (numbered: 01–99)
3. Sub-sections (nested: 0101–0199)
4. References (source URLs per section)

**templates/ folder** — migrate and adapt from `x-ipe-tool-knowledge-extraction-notes/templates/`:

| File | Source | Adaptation |
|------|--------|------------|
| `general-template.md` | `x-ipe-tool-knowledge-extraction-notes/templates/general-template.md` | Rewrite as `provide_framework` flexible template with numbered sections |
| `overview-template.md` | Same source path | Rewrite as overview generation template for `fill_structure` |

#### D3: constructor-app-reverse-engineering — Domain Specifics

**Domain template structure:** Reverse engineering report with 8 sections delegated to sub-skills:
1. Architecture Recovery → `x-ipe-tool-rev-eng-architecture-recovery`
2. API Contract Extraction → `x-ipe-tool-rev-eng-api-contract-extraction`
3. ... (6 more sections mapped to their respective sub-skills)

**templates/ folder** — migrate and adapt from `x-ipe-tool-knowledge-extraction-application-reverse-engineering/templates/`:

| File | Source | Adaptation |
|------|--------|------------|
| `playbook-template.md` | `x-ipe-tool-knowledge-extraction-application-reverse-engineering/templates/playbook-template.md` | Rewrite as `provide_framework` template mapping sections → sub-skills |
| `mixin-*.md` (all 10) | Same source folder (mixin-go, mixin-python, mixin-javascript, mixin-typescript, mixin-java, mixin-single-module, mixin-multi-module, mixin-monorepo, mixin-microservices) | Keep as-is — these are repo-type × language-type overlays for `provide_framework` adaptation |

**Key difference from other constructors:** The `request_knowledge` operation generates requests that may specify `x-ipe-tool-rev-eng-*` sub-skills as the extraction mechanism (not just extractor-web/extractor-memory). The Librarian dispatches to the appropriate sub-skill.

---

### D4: mimic-web-behavior-tracker

**Migration from `x-ipe-tool-learning-behavior-tracker-for-web`:**

The existing behavior tracker is a tool skill with 4 operations (inject, collect, stop, post_process). The new knowledge skill restructures into 3 operations (start_tracking, stop_tracking, get_observations) following the knowledge skill template.

**Folder structure:**
```
.github/skills/x-ipe-knowledge-mimic-web-behavior-tracker/
├── SKILL.md                    # Knowledge skill template (Operations+Steps)
├── scripts/
│   ├── tracker-toolbar.js      # Migrated from old skill — readable source
│   ├── tracker-toolbar.mini.js # Migrated from old skill — injection target
│   └── post_processor.py       # Migrated from old skill — generates flow narrative
└── references/
    └── examples.md             # Worked examples for each operation
```

**Operation contracts:**

```yaml
operation: start_tracking
input:
  target_app: string             # URL to track
  session_config:
    pii_whitelist: string[]      # CSS selectors to reveal (default: [])
    buffer_capacity: int         # Max events (default: 10000)
    purpose: string              # Tracking purpose (≤200 words, required)
output:
  tracking_session_id: string    # Unique session identifier
writes_to: x-ipe-docs/.mimicked/
constraints:
  - Navigate via Chrome DevTools MCP (navigate_page)
  - Inject tracker-toolbar.mini.js via evaluate_script
  - IIFE guard: window.__xipeBehaviorTrackerInjected prevents double injection
  - If guard already set → return existing session ID (no error)
  - PII masking: mask-everything default, whitelist opt-in, passwords NEVER revealed
  - Create session directory: x-ipe-docs/.mimicked/{session_id}/
```

```yaml
operation: stop_tracking
input:
  tracking_session_id: string
output:
  observation_summary: dict      # {flow_narrative, key_paths[], pain_points[], ai_annotations[]}
  raw_events: object[]           # Structured event records
writes_to: x-ipe-docs/.mimicked/
constraints:
  - Collect events via evaluate_script (call collectEvents on IIFE)
  - Run post_processor.py to generate observation_summary
  - Write summary + events to x-ipe-docs/.mimicked/{session_id}/
  - If session_id not found → error: SESSION_NOT_FOUND
```

```yaml
operation: get_observations
input:
  tracking_session_id: string
  filter: dict?                  # Optional: {event_type, time_range, element_selector}
output:
  observations: object[]
writes_to: null                  # READ-ONLY
constraints:
  - Read from x-ipe-docs/.mimicked/{session_id}/
  - Apply filter criteria if provided
  - If session_id not found → error: SESSION_NOT_FOUND
```

**Script migration notes:**
- `tracker-toolbar.js` / `tracker-toolbar.mini.js` — Copy as-is from old skill. The JavaScript IIFE is browser-injected and doesn't depend on skill namespace.
- `post_processor.py` — Copy from old skill. Adjust import paths if needed. The processor generates flow narrative, key paths, pain points, and AI annotations from raw events.
- Old `track_behavior.py` — NOT migrated. Its orchestration logic is now handled by the SKILL.md operation steps.

---

#### D4-CR1: start_active_tracking + poll_tick (CR-001 v1.3)

**Purpose:** Port the deprecated tool's polling/reinject/screenshot capabilities into the knowledge skill as an opt-in, agent-driven loop. Existing 3 ops (start_tracking / stop_tracking / get_observations) remain unchanged.

**Execution model:** Agent-driven loop (matches deprecated `x-ipe-tool-learning-behavior-tracker-for-web` exactly). The skill exposes building blocks; the orchestrating agent runs the 5s timing via Chrome DevTools MCP.

**New script:** `scripts/active_tracking.py` — pure helpers (no I/O loop), provides:
- `build_poll_script() → str` — JS to drain in-page buffer (returns `{events, eventCount, url}`)
- `merge_events(track_list_path, new_events) → dict` — merges into accumulating `track-list.json` (schema_version 2.0; matches old skill's `write_track_list`)
- `detect_url_change(session_dir, current_url) → bool` — reads `session.json::navigation_history`, compares last URL
- `record_navigation(session_dir, url) → None` — appends to `navigation_history`
- `should_screenshot(event_count, last_event_count) → bool` — returns `event_count > last_event_count`
- `screenshot_path(session_dir, tick_n) → Path` — `screenshots/tick-{n}.png`

The poll loop itself is documented in SKILL.md operation steps (no Python loop), so the agent drives timing.

**Operation contracts:**

```yaml
operation: start_active_tracking
input:
  target_app: string                # URL to track
  session_config:                   # Same as start_tracking
    pii_whitelist: string[]
    buffer_capacity: int
    purpose: string
  active_config:
    polling_interval_s: int         # default: 5
    auto_screenshot: bool           # default: true
    auto_reinject: bool             # default: true
output:
  tracking_session_id: string
  polling_started: true
  sub_op_contract:                  # Hands the agent the poll_tick contract
    name: poll_tick
    interval_s: 5
    until: "stop_tracking called for tracking_session_id"  # Superseded by CR-002 for DAO-routed learning flows
writes_to: x-ipe-docs/.mimicked/{session_id}/
constraints:
  - Reuses start_tracking's injection logic (DRY)
  - Persists active_config to session.json so poll_tick can read it
  - Initializes navigation_history: [target_app] in session.json
  - Returns control to agent; does NOT block or spawn subprocess
```

```yaml
operation: poll_tick                # Sub-op invoked by agent every polling_interval_s
input:
  tracking_session_id: string
  tick_n: int                       # Monotonic counter from agent
output:
  event_count: int
  new_events: bool
  url_changed: bool
  screenshot_path: string?          # null if no screenshot taken
writes_to: x-ipe-docs/.mimicked/{session_id}/
constraints:
  - evaluate_script(build_poll_script()) → drain buffer
  - merge_events into track-list.json (single accumulating file)
  - IF active_config.auto_reinject AND detect_url_change:
      → clear window.__xipeBehaviorTrackerInjected via evaluate_script
      → re-inject IIFE (delegate to start_tracking's injection logic)
      → record_navigation(session_dir, current_url)
  - IF active_config.auto_screenshot AND should_screenshot:
      → Chrome DevTools MCP take_screenshot → screenshot_path(session_dir, tick_n)
      → append to track-list.json::screenshots array
  - Empty ticks (no new events): NO screenshot, NO extra files (matches old skill's `if new_events:` gate)
  - If session_id not found → error: SESSION_NOT_FOUND
  - If IIFE not injected AND auto_reinject=false → error: TRACKER_LOST
```

**[RETIRED by CR-002] stop_tracking interaction:** CR-001 treated `stop_tracking` / `TRACKER_LOST` as loop-exit signals. For DAO-routed behavior learning, this is superseded: `start_active_tracking` owns polling until the tracker toolbar **Analysis** button is clicked, then stops tracking, consolidates observations, and returns them to the Knowledge Librarian DAO. Direct/degraded callers may still use `stop_tracking`, but the supported learning flow is Analysis-button termination through `start_active_tracking`.

**Session directory layout (active session):**
```
x-ipe-docs/.mimicked/{session_id}/
├── session.json              # metadata + navigation_history[] + active_config
├── track-list.json           # accumulating events (schema 2.0); screenshots[] array
└── screenshots/
    ├── tick-3.png            # tick where new events first detected
    ├── tick-7.png
    └── ...                   # only ticks with new_events=true
```

**Decision rationale:**
- **Why agent-driven, not subprocess?** The deprecated skill is agent-driven. Subprocess would (a) require new PID/signal handling, (b) duplicate Chrome DevTools MCP session ownership, (c) violate stateless-skill principle from 059-C. Agent loop is simpler, matches existing orchestration model, no new failure modes.
- **Why poll_tick as separate sub-op?** Keeps `start_active_tracking` idempotent (single setup call) while making the per-tick contract explicit and testable in isolation.
- **Why single `track-list.json` not per-tick files?** Matches old skill's proven format; downstream `post_processor.py` already consumes this shape; avoids file-count explosion in long sessions.
- **Why screenshots only on new events?** Direct port of old skill's `if new_events: take_screenshot` line. Empty ticks would produce identical images (no visual change without DOM events).

---

#### D4-CR2: DAO-routed, mimic-owned active learning + Analysis handoff (CR-002 v1.5)

**Purpose:** Make the Knowledge Librarian DAO the entry point/router for behavior learning while `x-ipe-knowledge-mimic-web-behavior-tracker.start_active_tracking` owns active polling and consolidation. The user controls completion by clicking **Analysis** in the tracker toolbar; `start_active_tracking` detects this through `poll_tick`, stops tracking, consolidates observations, and returns them to DAO.

**Supersedes:** CR-001 loop ownership and termination semantics:
- CR-001: generic agent owns loop; stop condition is `stop_tracking` or `TRACKER_LOST`.
- CR-002: Knowledge Librarian DAO classifies and delegates; `start_active_tracking` owns the loop; stop condition is `analysis_requested=true` from the toolbar Analysis button.

**DAO orchestration contract:**

```yaml
dao_flow: active_behavior_learning
entrypoint: x-ipe-assistant-knowledge-librarian-DAO
loop_owner: x-ipe-knowledge-mimic-web-behavior-tracker.start_active_tracking
steps:
  - classify request as behavior learning
  - call x-ipe-knowledge-mimic-web-behavior-tracker.start_active_tracking
  - start_active_tracking loops every polling_interval_s:
      internally call poll_tick(tracking_session_id, tick_n)
      continue while analysis_requested == false
  - start_active_tracking detects analysis_requested == true:
      stop tracking
      consolidate collected info
      return observation_summary / observations to DAO
  - DAO consumes returned mimic observations as gathered knowledge
```

**Updated `start_active_tracking` contract (target state):**

```yaml
output:
  tracking_session_id: string
  polling_started: true
  loop_owner: x-ipe-knowledge-mimic-web-behavior-tracker.start_active_tracking
  sub_op_contract:
    name: poll_tick
    interval_s: 5
    until: "tracker toolbar Analysis button clicked"
  final_result:
    returned_to: x-ipe-assistant-knowledge-librarian-DAO
    fields: [tracking_session_id, event_count, observation_summary, observations]
constraints:
  - Supported behavior-learning path MUST enter through Knowledge Librarian DAO
  - DAO delegates once and waits for start_active_tracking final result
  - start_active_tracking owns tick scheduling and consolidation
  - Direct invocation remains degraded-mode only
```

**Updated internal `poll_tick` contract (target state):**

```yaml
output:
  event_count: int
  new_events: bool
  url_changed: bool
  screenshot_path: string?
  reinjected: bool
  analysis_requested: bool
  analysis_payload_ready: bool       # true only when analysis_requested=true and latest events are merged
constraints:
  - Always merge latest events before returning Analysis signal to start_active_tracking
  - Analysis request must survive URL-change reinjection until start_active_tracking consumes it
  - poll_tick returns signal/event state to start_active_tracking, not directly to DAO
  - Empty ticks still do not create screenshots unless Analysis finalization explicitly needs a final-state screenshot
```

**Implementation considerations for later phases:**
- `build_poll_script()` should include the toolbar Analysis flag in the returned JSON (`analysisRequested`).
- `poll_tick` should surface `analysis_requested`; `start_active_tracking` performs stop/consolidation and prepares the final DAO return payload.
- Sticky Analysis state may be stored in `session.json` or preserved through browser storage so reinjection does not drop the user request.
- `start_active_tracking` should reset the toolbar Analysis UI only after the final observation payload is prepared for DAO.

**Component changes:**

| Component | Change | Reason | AC |
|-----------|--------|--------|----|
| `x-ipe-assistant-knowledge-librarian-DAO/SKILL.md` | Add request classification branch for behavior-learning/mimic tasks; delegate to mimic `start_active_tracking`; receive final mimic payload as `gathered_knowledge[]` input | User requests enter DAO first; DAO routes but does not own polling | AC-059C-18a |
| `x-ipe-knowledge-mimic-web-behavior-tracker/SKILL.md` | Rewrite `start_active_tracking` as the owner of the active loop; it internally invokes `poll_tick` until Analysis, then consolidates and returns to DAO | Matches corrected CR-002 flow | AC-059C-18b/c |
| `x-ipe-knowledge-mimic-web-behavior-tracker/SKILL.md` | Redefine `poll_tick` as an internal sub-operation returning tick state to `start_active_tracking`, not directly to DAO | Keeps public DAO handoff at one boundary: `start_active_tracking` final output | AC-059C-18c |
| `scripts/active_tracking.py` | Add helpers for Analysis flag handling and final payload preparation | Keeps SKILL.md steps simple and testable | AC-059C-18c/d |
| `references/tracker-toolbar.js` + `.mini.js` | Make Analysis request sticky until consumed; expose reset/consume semantics safely | Prevents Analysis click from being lost across reinject/navigation | AC-059C-18d |
| Tests | Add structural + helper tests for DAO classification text, mimic loop ownership, Analysis sticky handoff, final payload shape | Acceptance coverage for CR-002 | AC-059C-18a-d |

**Corrected ownership sequence:**

```mermaid
sequenceDiagram
    participant U as User
    participant DAO as Knowledge Librarian DAO
    participant M as Mimic start_active_tracking
    participant T as poll_tick
    participant B as Browser Toolbar

    U->>DAO: "learn behavior from <target>"
    DAO->>DAO: classify as mimic behavior-learning task
    DAO->>M: start_active_tracking(target_app, purpose, active_config)
    M->>B: inject tracker IIFE and toolbar
    loop every polling_interval_s until Analysis
        M->>T: poll_tick(tracking_session_id, tick_n)
        T->>B: collect events + url + analysisRequested
        T-->>M: tick_state(analysis_requested=false, events, url)
        M->>M: merge events, reinject if URL changed, screenshot if new events
    end
    U->>B: click Analysis
    M->>T: next poll_tick(...)
    T-->>M: tick_state(analysis_requested=true, latest events)
    M->>M: stop tracking + consolidate via post_processor
    M-->>DAO: mimic_observations payload
    DAO->>DAO: use observations as gathered knowledge
```

**Target `start_active_tracking` procedure:**

```xml
<operation name="start_active_tracking">
  <phase_1>
    <action>
      1. Validate target_app, session_config, active_config.
      2. Navigate and inject tracker IIFE using existing start_tracking injection steps.
      3. Initialize session.json with active_config, navigation_history, last_event_count=0, analysis_requested=false.
    </action>
  </phase_1>
  <phase_2>
    <action>
      1. LOOP with tick_n starting at 1:
         a. Invoke internal poll_tick(tracking_session_id, tick_n).
         b. Merge events and update last_event_count.
         c. If URL changed, clear guard, reinject, and preserve sticky Analysis state.
         d. If new events, take screenshot and record it.
         e. If analysis_requested=false, wait polling_interval_s and continue.
         f. If analysis_requested=true, break loop.
    </action>
  </phase_2>
  <phase_3>
    <action>
      1. Stop in-page tracker via existing stop script semantics.
      2. Run post_processor on accumulated track-list.json.
      3. Write observation-summary.json/raw-events.json as existing stop_tracking does.
      4. Mark Analysis handoff consumed and reset toolbar UI.
    </action>
  </phase_3>
  <phase_4>
    <action>
      1. Return final operation_output to DAO:
         result: {
           tracking_session_id,
           analysis_requested: true,
           event_count,
           observation_summary,
           observations,
           writes_to
         }
    </action>
  </phase_4>
</operation>
```

**Target helper additions (`scripts/active_tracking.py`):**

| Helper | Signature | Behavior |
|--------|-----------|----------|
| `mark_analysis_requested` | `(session_dir: Path) -> dict` | Sets `session.json::analysis_requested = true` and timestamp. Idempotent. |
| `consume_analysis_request` | `(session_dir: Path) -> dict` | Sets `analysis_handoff_consumed = true` after final payload is prepared. |
| `build_reset_analysis_ui_script` | `() -> str` | JS that calls `window.__xipeBehaviorTracker.resetAnalysisUI()` if available. |
| `build_stop_script` | `() -> str` | JS that stops the in-page tracker and returns final collected events. |
| `build_observation_payload` | `(track_list_path: Path, observation_summary: dict) -> dict` | Builds final DAO return payload from accumulated events + post-processor output. |

**Target `build_poll_script()` response shape:**

```json
{
  "events": [],
  "eventCount": 0,
  "url": "https://target.example/path",
  "analysisRequested": false,
  "status": "recording",
  "error": null
}
```

**Analysis persistence rule:**

1. Browser `getAnalysisFlag()` may reset the in-page flag after read.
2. Therefore the first poll tick that sees `analysisRequested=true` MUST immediately persist it via `mark_analysis_requested(session_dir)`.
3. URL-change reinjection MUST preserve the persisted `session.json::analysis_requested` state.
4. `start_active_tracking` treats either browser flag OR persisted session flag as authoritative until `consume_analysis_request()` runs.

**DAO integration design:**

Add a behavior-learning branch to Librarian classification:

```yaml
classification:
  behavior_learning:
    triggers:
      - "learn behavior"
      - "track behavior"
      - "observe user flow"
      - "mimic website behavior"
    route:
      skill: x-ipe-knowledge-mimic-web-behavior-tracker
      operation: start_active_tracking
```

Execution behavior:
- If request_type is `behavior_learning`, skip constructor framework/rubric planning.
- Invoke mimic `start_active_tracking` and wait for its final return.
- Convert returned `observation_summary`/`observations` into `gathered_knowledge[]`.
- Continue with ontology/store/present steps when requested by caller; otherwise return mimic observation summary.

**Acceptance test mapping:**

| AC | Test approach |
|----|---------------|
| AC-059C-18a | Structural test: Librarian SKILL.md contains behavior_learning classification and delegates to mimic `start_active_tracking`. |
| AC-059C-18b | Helper/procedure test: mimic SKILL.md states `start_active_tracking` owns loop and continues until Analysis. |
| AC-059C-18c | Unit tests for `mark_analysis_requested`, `consume_analysis_request`, `build_observation_payload`; structural test for stop/consolidate/return phases. |
| AC-059C-18d | Unit simulation: Analysis marked, URL changes, navigation recorded/reinject path runs, persisted Analysis remains true until consumed. |

---

### D5: ontology-builder

**New skill that absorbs build/CRUD capabilities from retired `x-ipe-tool-ontology`.**

**Folder structure:**
```
.github/skills/x-ipe-knowledge-ontology-builder/
├── SKILL.md                    # Knowledge skill — single build_ontology operation
├── scripts/
│   └── ontology_ops.py         # JSONL write utilities (entity, class, vocabulary)
└── references/
    └── examples.md             # Worked examples for build_ontology
```

**Single operation design:** Unlike constructors (which expose 4 operations for the orchestrator to call sequentially), ontology-builder exposes a single `build_ontology` operation. The orchestrator calls it once with `source_content` + `depth_limit`, and the builder runs an internal iterative loop (Steps 1–6) that handles discovery, critique, implementation, and drill-down autonomously.

**ontology_ops.py — Low-level JSONL script:**

This script provides low-level JSONL operations for the builder's internal loop to delegate to. It draws patterns from the existing `x-ipe-tool-ontology/scripts/ontology.py` (825 lines) but is simplified to handle only the operations the builder needs.

| Command | Purpose | Target File |
|---------|---------|-------------|
| `register_class` | Add/update class meta entry | `.ontology/schema/class-registry.jsonl` |
| `add_properties` | Add property definitions to a class | `.ontology/schema/class-registry.jsonl` (properties field) |
| `create_instance` | Create entity instance with properties + lifecycle | `.ontology/instances/instance.NNN.jsonl` |
| `add_vocabulary` | Add term to vocabulary scheme | `.ontology/vocabulary/{scheme}.json` |
| `validate_terms` | Check terms against vocabulary index | `.ontology/vocabulary/` (read-only) |

**Key design decisions:**

1. **Direct writes to `.ontology/`** — Unlike constructors that write to `.working/`, ontology-builder writes directly to `.ontology/` because ontology data IS the persistent structure. There's no "staging" for ontology entries.

2. **Lifecycle flag** — Every entity instance includes a `lifecycle` field:
   - `"Ephemeral"` — entity references `.working/` content (may be cleaned up)
   - `"Persistent"` — entity references persistent memory (`semantic/`, `procedural/`, `episodic/`)
   
   The builder determines lifecycle by inspecting `source_files[]` paths:
   ```python
   def determine_lifecycle(source_files: list[str]) -> str:
       for path in source_files:
           if ".working/" in path:
               return "Ephemeral"
       return "Persistent"
   ```

3. **Synthesize tracking** — Every class meta and instance record includes two fields for ontology-synthesizer traceability:
   - `synthesize_id` — ISO-8601 timestamp of the last synthesizer run (e.g., `"20260416T031759Z"`). Set by ontology-synthesizer when it processes the record. `null` means never synthesized.
   - `synthesize_message` — Free-text reason/purpose for the synthesize run (e.g., `"Initial relationship discovery for Flask ecosystem"`). Helps determine whether a re-run is needed (if the purpose has changed or new source content was added).
   
   The builder sets both fields to `null` on creation. The synthesizer (FEATURE-059-D) populates them on each run.

4. **JSONL append-only format** — Follows existing pattern from `ontology.py`:
   ```jsonl
   {"op":"create","type":"KnowledgeNode","id":"web-framework","ts":"2026-04-16T...","props":{"label":"WebFramework","description":"Web application frameworks","source_files":["semantic/flask.md"],"weight":5,"lifecycle":"Persistent","synthesize_id":null,"synthesize_message":null}}
   ```

5. **Chunk management** — `ontology_ops.py` handles instance chunk rotation. When `instance.NNN.jsonl` exceeds 5000 lines, the script creates `instance.{NNN+1}.jsonl` and updates `_index.json`.

6. **Vocabulary deduplication** — `add_vocabulary` checks existing terms before adding. Uses `broader`/`narrower` hierarchy from SKOS-like structure.

7. **Iterative critique-implement loop** — The builder's 6-step workflow runs inside the single `build_ontology` operation:
   - **Step 1 (Learn):** Read source content, load existing `.ontology/` state, produce content overview
   - **Step 2 (Suggest):** Propose initial ontology graph (classes, instances, vocabulary) from overview
   - **Step 3 (Critique):** Sub-agent evaluates proposed graph against existing `.ontology/`, suggests reuse/modify/create_new/skip
   - **Step 4 (Implement):** Write changes via ontology_ops.py commands
   - **Step 5 (Drill-down):** Select next unprocessed node with richest unexplored source content
   - **Step 6 (Learn details):** Read source_files for selected node, discover finer-grained graph elements, loop back to Step 3
   
   Loop termination: `depth_limit=1` → single pass; `depth_limit=3` → max 3 iterations; `depth_limit="auto"` → rubric-driven (concept_coverage, instance_coverage, vocabulary_coverage, hierarchy_coherence) targeting 100%, safety cap at 10 iterations.

---

#### Complete Meta Field Reference

**JSONL Event Envelope** (wrapper for all records):

| Field | Type | Description |
|-------|------|-------------|
| `op` | `"create" \| "update" \| "delete"` | Event-sourcing operation type |
| `type` | `string` | Entity type (e.g., `"KnowledgeNode"`) |
| `id` | `string` | Unique record identifier. Classes use kebab-case slug of the label (e.g., `"web-framework"`). Instances use `"inst-"` prefix with sequential number (e.g., `"inst-001"`) |
| `ts` | `ISO-8601` | Timestamp of this event |
| `props` | `object` | Record properties (see below) |

**Class Meta** (in `.ontology/schema/class-registry.jsonl`):

| Field | Type | Required | Set By | Description |
|-------|------|----------|--------|-------------|
| `label` | `string` | ✅ | Builder | Human-readable class name (e.g., `"WebFramework"`) |
| `description` | `string` | ✅ | Builder | What this class represents |
| `source_files` | `string[]` | ✅ | Builder | Paths to source knowledge files |
| `weight` | `int (1–10)` | ❌ (default: 5) | Builder | Importance score |
| `parent` | `string \| null` | ❌ | Builder | Parent class ID (for hierarchy) |
| `properties` | `object[]` | ❌ | Builder | Property schema definitions `[{name, kind, range, cardinality, vocabulary_scheme?}]` |
| `lifecycle` | `"Ephemeral" \| "Persistent"` | ✅ | Builder | Derived from `source_files` paths |
| `synthesize_id` | `ISO-8601 \| null` | ✅ | Synthesizer | Timestamp of last synthesizer run (`null` = never synthesized) |
| `synthesize_message` | `string \| null` | ✅ | Synthesizer | Purpose/reason for the synthesize run (`null` = never synthesized) |

**Instance Data** (in `.ontology/instances/instance.NNN.jsonl`):

| Field | Type | Required | Set By | Description |
|-------|------|----------|--------|-------------|
| `label` | `string` | ✅ | Builder | Human-readable instance name (e.g., `"Flask"`) |
| `class` | `string` | ✅ | Builder | Class ID reference — kebab-case slug (e.g., `"web-framework"`) |
| `source_files` | `string[]` | ✅ | Builder | Paths to source knowledge files |
| `lifecycle` | `"Ephemeral" \| "Persistent"` | ✅ | Builder | Derived from `source_files` paths |
| `synthesize_id` | `ISO-8601 \| null` | ✅ | Synthesizer | Timestamp of last synthesizer run (`null` = never synthesized) |
| `synthesize_message` | `string \| null` | ✅ | Synthesizer | Purpose/reason for the synthesize run (`null` = never synthesized) |
| `{prop_name}` | `varies` | ❌ | Builder | Dynamic properties from class property schema (e.g., `language: "Python"`) — `null` if N/A |

**Vocabulary Term** (in `.ontology/vocabulary/{scheme}.json`):

| Field | Type | Required | Set By | Description |
|-------|------|----------|--------|-------------|
| `label` | `string` | ✅ | Builder | Canonical term label |
| `broader` | `string \| null` | ❌ | Builder | Parent term (SKOS hierarchy) |
| `narrower` | `string[]` | ❌ | Builder | Child terms (SKOS hierarchy) |

**Operation contract:**

```yaml
operation: build_ontology
input:
  source_content: string[]         # Paths to memory files to analyze
  depth_limit: 1 | 3 | "auto"     # 1=flat, 3=standard, auto=rubric-driven (default: "auto")
output:
  build_report:
    ontology_summary:
      classes_created: int
      instances_created: int
      vocabulary_terms_added: int
      classes_reused: int
    rubric_scores:                   # Present when depth_limit == "auto"
      concept_coverage: float (0-1)
      instance_coverage: float (0-1)
      vocabulary_coverage: float (0-1)
      hierarchy_coherence: float (0-1)
    iterations_completed: int
    depth_reached: int
writes_to: x-ipe-docs/memory/.ontology/ (schema/, instances/, vocabulary/)
delegates_to: scripts/ontology_ops.py (register_class, add_properties, create_instance, add_vocabulary, validate_terms)
constraints:
  - Single operation — orchestrator calls once, builder handles all steps internally
  - Critique sub-agent runs before every write (never bypass)
  - Lifecycle determined automatically from source_files paths
  - synthesize_id and synthesize_message set to null on creation
  - Auto mode: rubric evaluation targets 100% on all 4 metrics, safety cap at 10 iterations
```

---

### D6–D9: Deprecation Headers

Each old skill gets a deprecation banner at the top of its SKILL.md, following the same pattern used for `x-ipe-tool-ontology` in 059-B.

**Template:**
```markdown
---
name: {old-skill-name}
description: "⚠️ DEPRECATED — Migrated to {new-skill-name} (FEATURE-059-C). Use the new knowledge skill instead."
---

> **⚠️ DEPRECATED:** This skill has been superseded by [`{new-skill-name}`](.github/skills/{new-skill-name}/SKILL.md).
> Migrate to the new skill for continued support.
```

**Mapping:**

| Old Skill | New Skill | Deliverable |
|-----------|-----------|-------------|
| `x-ipe-tool-knowledge-extraction-user-manual` | `x-ipe-knowledge-constructor-user-manual` | D6 |
| `x-ipe-tool-knowledge-extraction-notes` | `x-ipe-knowledge-constructor-notes` | D7 |
| `x-ipe-tool-knowledge-extraction-application-reverse-engineering` | `x-ipe-knowledge-constructor-app-reverse-engineering` | D8 |
| `x-ipe-tool-learning-behavior-tracker-for-web` | `x-ipe-knowledge-mimic-web-behavior-tracker` | D9 (removed after CR-001 parity) |

---

### Implementation Notes

**program_type:** `skills` — All deliverables are agent skill definitions (SKILL.md, templates, prompt engineering). Python scripts in D4s and D5s are supporting utilities.

**tech_stack:** `["Markdown/SKILL.md", "Python", "JavaScript (IIFE)"]`

**Skill creation workflow:**
1. All 5 skills created via `x-ipe-meta-skill-creator` (candidate → validate → merge)
2. Candidate files go to `x-ipe-docs/skill-meta/{skill-name}/candidate/`
3. After validation, merge to `.github/skills/{skill-name}/`
4. Each skill gets a `skill-meta.md` in `x-ipe-docs/skill-meta/{skill-name}/`

**Constructor template migration:** Templates are ADAPTED, not copy-pasted. The old templates were designed for a different operation model (direct extraction). The new templates support the 4-operation constructor pattern:
- `playbook-template.md` → `provide_framework` structural input
- `collection-template.md` → `request_knowledge` prompt patterns
- `acceptance-criteria.md` → `design_rubric` criteria definitions
- `mixin-*.md` → `provide_framework` adaptation overlays (these can stay mostly as-is)

**Mimic script migration:** `tracker-toolbar.js`, `tracker-toolbar.mini.js`, and `post_processor.py` are copied from the old skill with minimal changes. The JavaScript IIFE is browser-injected and namespace-independent. `track_behavior.py` is NOT migrated — its orchestration logic is replaced by the SKILL.md operation steps.

**Ontology JSONL format** — Follows existing `ontology.py` event-sourcing pattern:
```jsonl
{"op":"create","type":"KnowledgeNode","id":"web-framework","ts":"ISO-8601","props":{"label":"WebFramework","description":"Web application frameworks","source_files":["semantic/flask.md"],"weight":5,"lifecycle":"Persistent","synthesize_id":null,"synthesize_message":null}}
{"op":"update","type":"KnowledgeNode","id":"web-framework","ts":"ISO-8601","props":{"synthesize_id":"20260416T031759Z","synthesize_message":"Initial relationship discovery"}}
```
The `lifecycle`, `synthesize_id`, and `synthesize_message` fields are added to the `props` alongside existing fields (`label`, `source_files`, `weight`, etc.). Builder sets `synthesize_id`/`synthesize_message` to `null`; the synthesizer (059-D) populates them.

---

### Design Change Log

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-04-16 | Initial design |
| v1.1 | 2026-04-16 | Added `synthesize_id` and `synthesize_message` fields to class meta and instance data; added Complete Meta Field Reference tables |
| v1.2 | 2026-04-23 | [CR-001](x-ipe-docs/requirements/EPIC-059/FEATURE-059-C/CR-001.md) — Added D4-CR1 section: `start_active_tracking` + `poll_tick` sub-op design (agent-driven loop, single accumulating `track-list.json`, screenshot only on new events). Adds `scripts/active_tracking.py` helper module. |
| v1.3 | 2026-04-27 | [CR-002](x-ipe-docs/requirements/EPIC-059/FEATURE-059-C/CR-002.md) — Added D4-CR2 design: DAO classifies/delegates mimic behavior-learning requests; mimic `start_active_tracking` owns polling/consolidation until toolbar Analysis; final observations returned to DAO. |
