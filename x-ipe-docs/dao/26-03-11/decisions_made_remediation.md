# DAO Decisions — Remediation Phase (26-03-11)

---

## Decision: Audit Implementation & Tests Against Specs

- **Timestamp:** 2026-03-11
- **Task:** TASK-838
- **Workflow:** Knowledge-Base-Implementation
- **Source:** Human
- **Message:** "could you check if the related code has been implemented and also necessary test has been written base on the implementation skill"

### Phase 1: 格物 — Investigation

- **Supporting:** Good practice — specs were created retroactively, verifying alignment ensures consistency.
- **Opposing:** Code was implemented first, specs were written FROM the code, so alignment is nearly guaranteed by construction.
- **Neutral:** Cross-check is reasonable but the real risk is gaps in test coverage vs spec ACs, not code misalignment.
- **Context:** All 6 MVP features (A–G excl. F) have code implemented, tests passing (616 JS + 69 Python), deliverable docs now exist. Workflow shows all features closed in validation stage.

### Phase 2: 致知 — Understanding

- **Skill Match:** `x-ipe-task-based-code-implementation` (DoD checklist as audit rubric)
- **Disposition:** `instruction` — user is commanding a verification action
- **Confidence:** 0.85
- **Rationale:** Specs were written retroactively from code, so code-spec alignment is likely high. The real value is verifying test coverage against spec ACs and confirming the implementation skill's DoD checklist (test coverage, file structure, component completeness) is satisfied for each feature.

### Phase 4: 示 — Instruction

> Audit all 6 MVP features (A–G excl. F) against the `x-ipe-task-based-code-implementation` skill's Definition of Done. For each feature: (1) verify implementation files listed in technical-design.md exist and match described components, (2) verify test files exist with adequate coverage of specification acceptance criteria, (3) report any gaps where spec ACs lack corresponding test cases or where design components lack implementation. READ-ONLY audit — do not modify code, just report findings.

- **Execution Strategy:** `dao-represent-human-to-interact`
- **Fallback Required:** No

---

### DAO Decision — TASK-838: Validate AC Files Against Latest Template

**Timestamp:** 2025-03-11T22:10:00Z
**Source:** human
**Workflow:** Knowledge-Base-Implementation
**Downstream Context:** Agent completed implementation audit of 6 MVP features (A-G excl F). Found 5 gaps in test coverage. User wants to validate/update acceptance-test-cases.md files before writing tests.

**User Message:** "before work on ac testing, let's using latest feature refinement to validate if the ac follow the latest template it missing info, just follow the latest feature refinement to complete the info for each ac"

#### 格物 — Investigation
- **Supporting:** Good practice — ensures AC files are complete and standardized before writing tests
- **Opposing:** ACs already exist and tests already pass, this may be gold-plating
- **Neutral:** Template compliance ensures consistency and makes future maintenance easier; reasonable prep before filling gaps

#### 致知 — Analysis
- **Skill Match:** `x-ipe-task-based-feature-acceptance-test` (strong)
- **Disposition:** instruction
- **Confidence:** 0.85
- **Risk Assessment:** Worst case — minor reformatting effort. Best case — discovers missing AC scenarios. Both acceptable.

#### Decision
**Instruction:** Load the `x-ipe-task-based-feature-acceptance-test` skill and read its acceptance-test-cases template. For each of the 6 MVP features (A, B, C, D, E, G): read the current acceptance-test-cases.md, compare against the latest template structure, identify missing sections or fields, and update the file to comply with the template. Validation-and-update pass only — do NOT write test code yet.

**Rationale:** User wants template compliance validated before writing tests. Ensures all AC files have consistent structure and complete information, making subsequent test-writing phase more efficient and thorough.

---

### DAO Decision — TASK-838 (Spec AC Test Type Column)
**Timestamp:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Source:** Human message
**Downstream Context:** Agent had updated acceptance-test-cases.md files to template. User clarifies that specification.md files themselves need AC tables with Test Type column (UI/API/Unit/Integration).

#### Phase 1 — Interpretation
User is instructing that the **specification.md** files (not acceptance-test-cases) need their Acceptance Criteria tables updated to include a "Test Type" column classifying each AC as UI, API, Unit, or Integration. This is spec template compliance.

#### Phase 2 — Disposition
**Disposition:** `instruction`
**Confidence:** 0.9

#### Phase 3 — Instruction Units
| # | Disposition | Content | Suggested Skill | Match |
|---|-----------|---------|-----------------|-------|
| 1 | instruction | Update AC section in all 6 specification.md files (A, B, C, D, E, G) to include Test Type column. Each AC row: AC ID \| Criterion \| Test Type (UI/API/Unit/Integration). Sub-criteria use letter suffixes (e.g., AC-049-A-01a). | x-ipe-task-based-feature-refinement | strong |

#### Decision
**Instruction:** Update the Acceptance Criteria section in all 6 specification.md files (FEATURE-049-A, B, C, D, E, G) to include a Test Type column. Each AC row should have: AC ID | Criterion | Test Type (UI/API/Unit/Integration). Sub-criteria should use letter suffixes (e.g., AC-049-A-01a, AC-049-A-01b). This is a spec-level change, not test-case level.

**Rationale:** User clarified that spec ACs need test type classification at the specification level, which then flows down to acceptance test case generation. Current specs lack this column.

## DAO-047
- **Timestamp:** 2026-03-11T14:25:09Z
- **Task ID:** TASK-839
- **Feature ID:** FEATURE-049-A through G
- **Workflow:** Knowledge-Base-Implementation
- **Calling Skill:** N/A (direct human message)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.9

### Message
> I have totally updated feature refinement skill today, you can base on the changes to refine the defined specification

### Guidance Returned
> Update all 6 EPIC-049 specification.md files (A,B,C,D,E,G) to conform with the updated feature refinement skill template. Key changes: (1) AC table header → `| AC ID | Criterion (Given/When/Then) | Test Type |`, (2) All AC criteria rewritten to Given/When/Then (GWT) format, (3) Add Linked Mockups section referencing KB mockup, (4) Add Version History table, (5) Add Test Type Legend after ACs, (6) Ensure all template sections present per specification-template.md.

### Rationale
> User explicitly says the feature refinement skill was "totally updated today." The updated skill now mandates GWT format for all ACs, updated table header, and Linked Mockups section. Current specs use descriptive statements without GWT. Re-aligning to the latest template ensures consistency and testability.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-refinement"
>     match_strength: "strong"
>     reason: "User explicitly references this skill's update and wants specs refined to match"
>     execution_steps:
>       - phase: "5. 笃行之 — Practice Earnestly"
>         step: "5.1 Create/Update Feature Specification"

### Follow-up
> After all 6 specs updated, commit and push. Then address remaining 5 missing tests from audit.
