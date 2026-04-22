# Requirement Details - Part 22

> Continued from: [requirement-details-part-21.md](x-ipe-docs/requirements/requirement-details-part-21.md)
> Created: 03-31-2026

---

## [RETIRED by EPIC-059] EPIC-053: Application Reverse Engineering Knowledge Extraction Tool Skill

> **⚠️ RETIRED:** This EPIC is superseded by **EPIC-059 (Rebuild Knowledge Skills)**. The `x-ipe-tool-knowledge-extraction-application-reverse-engineering` is replaced by `x-ipe-knowledge-constructor-app-reverse-engineering`. The 8 `x-ipe-tool-rev-eng-*` tool skills it depends on remain unchanged. See [EPIC-059 requirements](x-ipe-docs/requirements/requirement-details-part-25.md).
> Retired: 2026-04-14

> Version: 1.0
> Source Idea: [IDEA-037 — Application Reverse Engineering](x-ipe-docs/ideas/037.%20Feature-Application%20Reverse%20Engineering/refined-idea/idea-summary-v1.md)
> Depends On: EPIC-050 (Application Knowledge Extractor), EPIC-051 (User Manual Tool Skill — structural reference)

### Project Overview

Create `x-ipe-tool-knowledge-extraction-application-reverse-engineering` — a tool skill that plugs into the Application Knowledge Extractor pipeline to reverse-engineer source code repositories. The skill provides an 8-section phased playbook, collection templates, validation criteria, a two-dimension mixin system (repo-type × language-type), accuracy-focused quality scoring, verification walkthrough, and source code tests as a Phase 2 knowledge source — all mirroring the `x-ipe-tool-knowledge-extraction-user-manual` pattern but focused on extracting architectural knowledge from code.

### User Request

Create a skill `x-ipe-knowledge-extraction-application-reverse-engineering` similar in structure to the user-manual tool skill, but focused on application reverse engineering. Scope: architecture recovery, design pattern detection, API contract extraction, dependency analysis, code structure analysis, data flow analysis, technology stack identification, and source code tests as a knowledge source.

### Clarifications

| Question | Answer |
|----------|--------|
| How many features? | Single feature — all skill artifacts (SKILL.md, templates, references, mixins) are one cohesive deliverable |
| Mirrors user-manual? | Yes — same 7-operation contract (get_artifacts, get_collection_template, validate_section, get_mixin, pack_section, score_quality, test_walkthrough) |
| Mixin scope? | Full — 4 repo-type (monorepo, multi-module, single-module, microservices) + 5 language-type (python, java, javascript, typescript, go) |
| Extractor update needed? | Yes — extractor must accept `application-reverse-engineering` as valid category |
| Test generation scope? | Full — AAA test structure, framework detection, ≥80% coverage target, test-as-knowledge pipeline |

### High-Level Requirements

1. **7-Operation Contract:** Implement all 7 operations matching the user-manual skill interface: get_artifacts, get_collection_template, validate_section, get_mixin, pack_section, score_quality, test_walkthrough.
2. **8-Section Phased Playbook:** Three-phase extraction — Phase 1 Scan (sections 5, 7), Phase 2 Tests (section 8), Phase 3 Deep (sections 1, 2, 3, 4, 6).
3. **Collection Templates:** Source-code-specific extraction prompts for each of the 8 sections.
4. **Two-Dimension Mixin System:** Repo-type (4) × language-type (5) auto-detected mixins with layered composition.
5. **Accuracy-Focused Quality Scoring:** 6 dimensions with section-specific weight profiles (accuracy highest for architecture, coverage highest for tests).
6. **Evidence-Based Pattern Detection:** Confidence levels (high/medium/low) with file:line evidence citations.
7. **Verification Walkthrough:** Dual-source cross-verification against source code AND test-derived knowledge.
8. **Source Code Tests as Knowledge:** Phase 2 pipeline — collect/generate AAA tests, run, validate ≥80% coverage, extract test knowledge for Phase 3.
9. **Minimum Complexity Gate:** Skip full RE for codebases below threshold (< 10 files, < 500 LOC).
10. **Extractor Category Registration:** Update extractor to discover and load skill via `categories: ["application-reverse-engineering"]`.

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-053-A | EPIC-053 | Application Reverse Engineering Tool Skill | v1.0 | Complete tool skill with 8-section phased playbook, collection templates, acceptance criteria, two-dimension mixins, quality scoring, verification walkthrough, source code tests pipeline, and extractor category registration | None |

---

## Feature Details

### FEATURE-053-A: Application Reverse Engineering Tool Skill

**Version:** v1.0
**Brief Description:** Complete `x-ipe-tool-knowledge-extraction-application-reverse-engineering` tool skill that enables the Application Knowledge Extractor to reverse-engineer source code repositories, mirroring the user-manual skill structure but focused on architectural knowledge extraction from code.

**Acceptance Criteria:**
- [ ] SKILL.md created with 7-operation contract matching `x-ipe-tool-knowledge-extraction-user-manual` interface (get_artifacts, get_collection_template, validate_section, get_mixin, pack_section, score_quality, test_walkthrough)
- [ ] Skill frontmatter declares `categories: ["application-reverse-engineering"]` for extractor discovery
- [ ] 8-section playbook template defines phased extraction: Phase 1 Scan (sections 5, 7), Phase 2 Tests (section 8), Phase 3 Deep (sections 1, 2, 3, 4, 6)
- [ ] Collection template provides source-code-specific extraction prompts for all 8 sections
- [ ] Acceptance criteria template provides per-section validation rules
- [ ] 4 repo-type mixins created (monorepo, multi-module, single-module, microservices) with detection signals
- [ ] 5 language-type mixins created (python, java, javascript, typescript, go) with detection signals
- [ ] Mixin auto-detection logic documented — repo-type is primary, language-type is additive overlay
- [ ] score_quality operation implements 6 dimensions (completeness, structure, clarity, accuracy, freshness, coverage) with section-specific weight profiles
- [ ] Accuracy weighted highest (0.35) for architectural sections; coverage weighted highest (0.50) for tests section
- [ ] test_walkthrough operation cross-verifies extracted claims against source code AND test-derived knowledge with ≥80% verification target
- [ ] Pattern detection includes confidence levels (high 🟢, medium 🟡, low 🔴) with file:line evidence citations
- [ ] Source Code Tests section (section 8) templates enforce AAA structure (Arrange/Act/Assert)
- [ ] Test framework detection and matching documented (pytest, vitest, jest, JUnit, go test, etc.)
- [ ] Test coverage threshold ≥80% enforced with per-module breakdown
- [ ] Test-to-knowledge extraction mapping documented (assertions → behaviors, fixtures → data shapes, mocks → boundaries, names → vocabulary)
- [ ] Minimum complexity gate documented (≥10 files, ≥500 LOC, ≥3 directories threshold)
- [ ] Multi-level architecture output uses Architecture DSL (conceptual + logical) and Mermaid (physical + data flow)
- [ ] `x-ipe-task-based-application-knowledge-extractor` updated to accept `application-reverse-engineering` as valid category
- [ ] Extractor discovers skill via glob `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md` matching categories

**Dependencies:**
- None (foundation feature — extractor update is included in this feature's scope)

**Technical Considerations:**
- Skill structure mirrors `x-ipe-tool-knowledge-extraction-user-manual` — same folder layout: SKILL.md, templates/, references/
- Mixin files stored under `references/mixins/repo-type/` and `references/mixins/language-type/`
- Architecture DSL delegation: this skill produces textual knowledge; rendering delegated to `x-ipe-tool-architecture-dsl`
- No PlantUML — physical-level class diagrams use Mermaid `classDiagram`
- Source code is ground truth — when tests fail, fix tests not source code
- Extractor update is minimal — add category to allowed list and ensure discovery pattern matches

---

## Linked Mockups

N/A

---

## Notes

- This EPIC creates a new tool skill under `.github/skills/x-ipe-tool-knowledge-extraction-application-reverse-engineering/`
- The skill is consumed by `x-ipe-task-based-application-knowledge-extractor` during extraction
- Single feature is appropriate because all deliverables are skill artifacts (SKILL.md, templates, references) — no source code changes
- Detailed idea summary with full technical design available at [idea-summary-v1.md](x-ipe-docs/ideas/037.%20Feature-Application%20Reverse%20Engineering/refined-idea/idea-summary-v1.md)

---

## [RETIRED by EPIC-059] EPIC-054: Web Behavior Learning & Tracking Module

> **⚠️ RETIRED:** This EPIC is superseded by **EPIC-059 (Rebuild Knowledge Skills)**. The `x-ipe-learning-behavior-tracker-for-web` is replaced by `x-ipe-knowledge-mimic-web-behavior-tracker` under the new knowledge namespace with Operations + Steps pattern (start_tracking, stop_tracking, get_observations). See [EPIC-059 requirements](x-ipe-docs/requirements/requirement-details-part-25.md).
> Retired: 2026-04-14

> Version: 1.0
> Source Idea: [IDEA-038 — Feature-Learn Module](x-ipe-docs/ideas/038.%20Feature-Learn%20module/refined-idea/idea-summary-v1.md)
> Depends On: EPIC-030-B (Chrome DevTools injection infrastructure — shared utility extraction via CR)

### Project Overview

Create a **Learning Module** within X-IPE's Workplace ideation area that enables users to track and record their behavior on external websites, with AI-assisted annotation. The module captures user interaction events (clicks, double-clicks, right-clicks, drags, typing, scrolling, navigation), enriches them with element metadata and accessibility information, and produces structured `behavior-recording.json` files that feed into X-IPE's downstream pipeline for AI agent training and knowledge capture.

The module is implemented as a new standalone skill (`x-ipe-learning-behavior-tracker-for-web`) that shares Chrome DevTools injection infrastructure with the existing UIUX reference skill (DRY) while maintaining a separate data model and output format.

### User Request

Build a Learn module for X-IPE's Workplace that lets users track their behavior on any external website. The system should capture all user interactions (clicks, drags, typing, scrolling, right-clicks, navigation), annotate them with AI-generated context (purpose, relevance, key-path classification), and export structured behavior recordings for consumption by requirement gathering and code implementation skills.

### Clarifications

| Question | Answer |
|----------|--------|
| Primary purpose? | AI agent training data + knowledge capture (NOT UX analytics) |
| Architecture? | New standalone skill, share Chrome DevTools injection infra as reusable utility (DRY) |
| Scope? | Web behavior tracking only for v1 — CLI/API tracking deferred (YAGNI) |
| Output format? | Structured `behavior-recording.json` with AI annotations — no visual replay for v1 |
| AI annotation model? | MVP: post-processing only. Real-time annotation deferred (upgrade path preserved in schema) |
| PII handling? | Auto-masking by default, password fields never captured, opt-in for non-sensitive fields |
| Tracking purpose? | Freeform text with placeholder examples (KISS) |
| Not-On-Key-Path events? | Visible but de-emphasized — greyed out, collapsed by default, user overridable |
| Concurrent sessions? | Single active session for v1. Explicit stop required before starting new session (KISS) |
| Data retention? | Stored in project folder alongside other artifacts. No auto-deletion. Project lifecycle retention |
| Crash recovery? | Deferred from MVP (YAGNI). Incremental save via LocalStorage serves as basic safeguard |
| DevTools infra overlap with EPIC-030-B? | CR on EPIC-030-B to extract shared utility `x-ipe-util-chrome-devtools-integration` |
| Injected UI panel coexistence? | Must coexist with EPIC-030-B toolbar. Z-index strategy deferred to technical design |
| Downstream integration? | Requirement defines output schema + consuming skills. Detailed integration API deferred to technical design |

### High-Level Requirements

1. **Workplace GUI Entry Point:** New "Learn" menu item under Workplace ideation with target URL input, freeform tracking purpose field, and session management controls (start, view history).
2. **Chrome DevTools Script Injection:** Reuse shared `navigate_page` + `evaluate_script` infrastructure (extracted from EPIC-030-B via CR). Inject `tracker-toolbar.js` as IIFE. Guard against double injection via `window.__xipeBehaviorTrackerInjected`.
3. **Event Recording Engine:** Capture 7 event types — click, double-click, right-click, drag, typing, scrolling, navigation — with full element metadata (selector, tag, text, a11y role/name, classes, bounding box) and coordinates.
4. **Cross-Page Persistence:** DevTools page lifecycle monitoring detects navigations and re-injects script automatically. LocalStorage backup for data recovery during brief re-injection gaps. Session ID correlates events across pages.
5. **Injected Toolbox (Shadow DOM):** Floating panel rendered inside target website via Shadow DOM for CSS isolation. Displays chronological event list, recording controls (start/stop/pause), event status indicators (Key-Path vs. Not-On-Key-Path), and session info (purpose, page count, event count, elapsed time). Must coexist with EPIC-030-B toolbar.
6. **PII Protection:** Default-on masking for typed content. Password fields (`type="password"`, autocomplete attributes) never captured. Element metadata (selectors, a11y tags) always captured (no PII risk). Opt-in reveal for explicitly non-sensitive fields.
7. **Structured Output:** `behavior-recording.json` following defined schema (session, pages, events with annotations, flow_narrative, key_path_summary, pain_points). Schema supports future upgrade to real-time annotation without breaking changes.

### Scope

**In Scope (MVP):**
- Workplace GUI entry point (Feature 1)
- Chrome DevTools script injection (Feature 2)
- Event recording engine — all 7 event types (Feature 3)
- Cross-page persistence (Feature 4)
- Injected toolbox with Shadow DOM (Feature 5)
- PII protection (Feature 6)
- Structured output with `behavior-recording.json` schema (Feature 7)

**Out of Scope (Deferred):**
- Real-time AI annotation during recording (deferred to post-v1; post-processing annotation acceptable for MVP)
- Crash recovery with session resume (basic LocalStorage save provides safeguard)
- Visual session replay
- CLI/API behavior tracking
- Concurrent multi-session recording
- Cross-origin OAuth redirect handling (document as known limitation)
- IndexedDB/large-scale storage (LocalStorage sufficient for v1 event metadata)

### Constraints

- **CSP Bypass:** Script injection via `evaluate_script` bypasses Content Security Policy by design (same as UIUX reference skill)
- **Shadow DOM Required:** Injected toolbox must use Shadow DOM to prevent style leakage to/from target site
- **Performance Throttling:** Event listeners must use throttling — scroll: 200ms, mousemove during drag: 50ms
- **Storage Limit:** LocalStorage ~5MB limit — implement circular buffer pruning for long sessions
- **Single Tab:** One browser tab tracked at a time (v1)
- **Single Session:** One active recording session at a time; explicit stop before starting new (v1)
- **Schema Stability:** `behavior-recording.json` v1 schema must support additive fields for real-time annotations without breaking changes

### Feasibility & Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Cross-page re-injection timing gap causes event loss | Medium | LocalStorage backup captures events during gap; session ID correlates data |
| LocalStorage 5MB limit exceeded in long sessions | Medium | Circular buffer pruning; monitor buffer size; warn user at threshold |
| Shadow DOM CSS isolation may not cover all edge cases | Low | Test on diverse target sites; fallback to scoped styles if needed |
| Shared DevTools utility extraction (CR on EPIC-030-B) may delay EPIC-054 | Medium | EPIC-054 can implement inline initially and refactor when shared utility is ready |
| Target site modifies DOM in ways that break event listeners | Low | Use capture phase listeners on document; re-attach on MutationObserver changes |

### Assumptions

- Chrome DevTools MCP `evaluate_script` and `navigate_page` tools remain stable and available
- Target websites are rendered in standard Chromium-based browser
- X-IPE Workplace UI supports adding new menu items via existing extension patterns
- LocalStorage is available on target sites (not disabled by user/enterprise policy)

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-054-A | EPIC-054 | Workplace Learn Module GUI | v1.0 | Learn menu entry point with URL input, tracking purpose, session list, Track Behavior CTA | None |
| FEATURE-054-B | EPIC-054 | Chrome DevTools Injection & Page Lifecycle | v1.0 | Shared injection infra consumption, script injection, double-inject guard, cross-page re-injection, LocalStorage backup | EPIC-030-B (CR: shared utility extraction) |
| FEATURE-054-C | EPIC-054 | Event Recording Engine | v1.0 | 7-type event capture with element metadata, a11y info, coordinates, throttling | FEATURE-054-B |
| FEATURE-054-D | EPIC-054 | Injected Tracker Toolbox (Shadow DOM) | v1.0 | Floating overlay with event list, recording controls, key-path indicators, session stats, PII badge | FEATURE-054-B, FEATURE-054-C |
| FEATURE-054-E | EPIC-054 | PII Protection & Masking | v1.0 | Default-on masking, password detection, opt-in reveal, element metadata passthrough | FEATURE-054-C |
| FEATURE-054-F | EPIC-054 | behavior-recording.json Output & Post-Processing | v1.0 | Structured output schema, flow narrative generation, key-path summary, pain point detection | FEATURE-054-C, FEATURE-054-E |

---

## Feature Details

> **MVP Implementation Order (DAO-106):** A → B → C → E → F → D
> A-first avoids day-one pipeline stall on EPIC-030-B CR external dependency. B starts after CR interface is defined.

### FEATURE-054-A: Workplace Learn Module GUI

**Version:** v1.0 | **MVP Priority:** 1 (zero dependencies — immediate start) | **Dependencies:** None

New "Learn" menu item under Workplace ideation area. Provides target URL input, freeform tracking purpose field, session management, and "Track Behavior" CTA that initiates a recording session via terminal skill invocation.

**Acceptance Criteria:**

| # | Criterion |
|---|-----------|
| AC-1 | "Learn" menu item appears under Workplace ideation area navigation |
| AC-2 | Target URL input field accepts and validates URLs (protocol + domain minimum) |
| AC-3 | Tracking Purpose freeform text field displays placeholder examples (e.g., "e.g., Checkout flow for AI agent training") |
| AC-4 | "Track Behavior" button triggers terminal session and invokes `x-ipe-learning-behavior-tracker-for-web` skill |
| AC-5 | Session list displays recent recording sessions with status indicators (recording / paused / completed) |
| AC-6 | Session cards show domain, elapsed time, event count, page count |
| AC-7 | Active session highlighted with live recording indicator (pulsing emerald dot) |

**Mockup Reference:** [learn-panel-v1.html](x-ipe-docs/requirements/EPIC-054/mockups/learn-panel-v1.html) — left panel layout with session list and event timeline

---

### FEATURE-054-B: Chrome DevTools Injection & Page Lifecycle

**Version:** v1.0 | **MVP Priority:** 2 (foundation) | **Dependencies:** EPIC-030-B (CR: shared utility extraction)

Consumes shared Chrome DevTools injection infrastructure to open target URL, inject `tracker-toolbar.js` as IIFE, guard against double injection, detect page navigation via lifecycle monitoring, and auto-re-inject across page transitions with LocalStorage backup.

**Acceptance Criteria:**

| # | Criterion |
|---|-----------|
| AC-1 | Skill uses `navigate_page` to open target URL in Chrome DevTools browser |
| AC-2 | `evaluate_script` injects `tracker-toolbar.js` as IIFE into target page |
| AC-3 | Double injection guard via `window.__xipeBehaviorTrackerInjected` flag prevents duplicate initialization |
| AC-4 | Page navigation detected via DevTools page lifecycle monitoring |
| AC-5 | Script auto-re-injected after page navigation completes (new document ready) |
| AC-6 | LocalStorage backup preserves accumulated event data during re-injection gap |
| AC-7 | Session ID assigned at recording start, correlates events across page transitions |
| AC-8 | Consumes shared Chrome DevTools utility from EPIC-030-B CR (or inline fallback if CR not yet merged) |

**Technical Consideration:** If EPIC-030-B CR is not yet available, implement injection inline and refactor when shared utility is extracted. Flag on feature board as blocked-until.

---

### FEATURE-054-C: Event Recording Engine

**Version:** v1.0 | **MVP Priority:** 3 (core value) | **Dependencies:** FEATURE-054-B

Captures 7 event types — click, double-click, right-click, drag, typing, scroll, navigation — with full element metadata (selector, tag, text, a11y role/name, classes, bounding box), coordinates, and timestamps. Uses capture-phase listeners and circular buffer for long sessions.

**Acceptance Criteria:**

| # | Criterion |
|---|-----------|
| AC-1 | Click events captured with target CSS selector, element text, a11y role/name, bounding box, page coordinates |
| AC-2 | Double-click events captured with double-click flag and full target metadata |
| AC-3 | Right-click (contextmenu) events captured with target metadata |
| AC-4 | Drag events captured with start/end positions, delta, duration, target element |
| AC-5 | Typing events captured with field selector, masked value (default PII), field type attribute |
| AC-6 | Scroll events captured with 200ms throttle, scrollX/Y, viewport dimensions |
| AC-7 | Navigation events captured with source URL, destination URL, trigger element selector |
| AC-8 | All events include timestamp — absolute ISO 8601 and relative ms since session start |
| AC-9 | Event listeners attached via capture phase on document for reliability across DOM changes |
| AC-10 | Circular buffer maintains events with configurable size limit; oldest events pruned in long sessions |

---

### FEATURE-054-E: PII Protection & Masking

**Version:** v1.0 | **MVP Priority:** 4 (safety gate before output) | **Dependencies:** FEATURE-054-C

Default-on masking for typed content in input fields. Password fields never captured. Element metadata (selectors, a11y tags) always captured. Opt-in mechanism for non-sensitive field reveal. Masking applied at capture time before events enter buffer.

**Acceptance Criteria:**

| # | Criterion |
|---|-----------|
| AC-1 | Typed content in input fields captured as `[MASKED]` by default |
| AC-2 | Password fields (`type="password"`, `autocomplete` containing "password") never captured under any circumstance |
| AC-3 | Element metadata (CSS selectors, a11y tags, class names) always captured regardless of masking (no PII risk) |
| AC-4 | Opt-in mechanism allows user to mark specific fields as non-sensitive for value capture |
| AC-5 | Masking applied at capture time before events enter buffer — not as post-processing |
| AC-6 | PII masking active status reflected in toolbox UI badge (consumed by FEATURE-054-D) |

---

### FEATURE-054-F: behavior-recording.json Output & Post-Processing

**Version:** v1.0 | **MVP Priority:** 5 (deliverable) | **Dependencies:** FEATURE-054-C, FEATURE-054-E

Produces structured `behavior-recording.json` following defined schema with session metadata, pages, events with AI annotations, flow narrative, key-path summary, and pain point detection. Schema v1.0 supports additive upgrade for future real-time annotation.

**Acceptance Criteria:**

| # | Criterion |
|---|-----------|
| AC-1 | Output follows schema: `session` (metadata), `pages[]`, `events[]` (with annotations), `flow_narrative`, `key_path_summary`, `pain_points` |
| AC-2 | Schema `version` field set to `"1.0"` with documented additive upgrade path |
| AC-3 | Post-processing generates `flow_narrative` — natural language summary of user journey |
| AC-4 | Post-processing generates `key_path_summary` — ordered key steps user took toward goal |
| AC-5 | `pain_points` detected: repeated actions, back-and-forth navigation, hesitation patterns |
| AC-6 | Events include AI annotations: `comment`, `is_key_path`, `intent_category`, `confidence` |
| AC-7 | Output saved to project folder alongside other recording artifacts |
| AC-8 | Schema supports additive fields for future real-time annotation without breaking changes |

---

### FEATURE-054-D: Injected Tracker Toolbox (Shadow DOM)

**Version:** v1.0 | **MVP Priority:** 6 (enhancement UX — last) | **Dependencies:** FEATURE-054-B, FEATURE-054-C

Floating panel rendered inside target website via Shadow DOM for CSS isolation. Displays chronological event list, recording controls (start/stop/pause), key-path vs not-on-key-path indicators, session info, and PII badge. Draggable, collapsible, coexists with EPIC-030-B toolbar.

**Acceptance Criteria:**

| # | Criterion |
|---|-----------|
| AC-1 | Toolbox rendered inside Shadow DOM for complete CSS isolation from target site |
| AC-2 | Chronological event list displays captured events with type icons and timestamps |
| AC-3 | Recording controls (Start, Stop, Pause) functional and visually reflect current recording state |
| AC-4 | Key-Path events highlighted; Not-On-Key-Path events greyed out and collapsed by default |
| AC-5 | Session info displays: tracking purpose, page count, event count, elapsed time |
| AC-6 | PII masking badge visible when masking is active (consumes FEATURE-054-E status) |
| AC-7 | Toolbox is draggable — repositionable anywhere on target page |
| AC-8 | Toolbox is collapsible/minimizable to reduce visual intrusion on target site |
| AC-9 | Coexists with EPIC-030-B UIUX toolbar without z-index or interaction conflicts |

**Mockup Reference:** [tracker-toolbox-v1.html](x-ipe-docs/requirements/EPIC-054/mockups/tracker-toolbox-v1.html) — glass-morphism floating overlay with recording controls and event list

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| Learn Module Panel — Workplace sidebar with URL input, session list, event timeline | FEATURE-054-A, FEATURE-054-D | [learn-panel-v1.html](x-ipe-docs/requirements/EPIC-054/mockups/learn-panel-v1.html) |
| Injected Tracker Toolbox — Floating overlay with recording controls, event list, AI annotations | FEATURE-054-D, FEATURE-054-C | [tracker-toolbox-v1.html](x-ipe-docs/requirements/EPIC-054/mockups/tracker-toolbox-v1.html) |

---

## Related Features

| Related EPIC/Feature | Relationship | Impact |
|---------------------|-------------|--------|
| EPIC-030-B (UIUX Reference Agent Skill) | **CR filed** — Extract shared Chrome DevTools injection utility | FEATURE-030-B marked with CR impact note. Shared utility `x-ipe-util-chrome-devtools-integration` to be extracted. EPIC-054 depends on this for DRY compliance. |
| EPIC-005 (Application Action Tracing) | Opportunity — PII detection patterns may converge | No immediate action. Both implement password/sensitive field detection independently. Refactor later if patterns align. |
| EPIC-022-A (Browser Simulator) | Coexistence — Both add Workplace sub-menu entries | No conflict. Follow existing Workplace menu extension patterns. |

---

## Notes

- This EPIC creates a new skill under `.github/skills/x-ipe-learning-behavior-tracker-for-web/`
- The skill is consumed via Workplace UI → Terminal → Skill invocation flow
- 6 features identified for Feature Breakdown: GUI entry point, injection infra, recording engine, toolbox, PII protection, output/post-processing
- MVP excludes real-time AI annotation (post-processing only) and crash recovery — schema designed for additive upgrade
- Detailed idea summary with architecture diagrams, data model, and sequence flows at [idea-summary-v1.md](x-ipe-docs/ideas/038.%20Feature-Learn%20module/refined-idea/idea-summary-v1.md)
