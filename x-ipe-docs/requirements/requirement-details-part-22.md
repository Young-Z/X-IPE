# Requirement Details - Part 22

> Continued from: [requirement-details-part-21.md](x-ipe-docs/requirements/requirement-details-part-21.md)
> Created: 03-31-2026

---

## EPIC-053: Application Reverse Engineering Knowledge Extraction Tool Skill

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
