---
skill_name: x-ipe-tool-reference-user-manual
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
summary: >
  Look up, retrieve, and interpret instructions from user manuals stored in the
  knowledge base. Use when an executor needs manual guidance to perform a step.
triggers:
  - "lookup user manual instruction"
  - "get step-by-step from manual"
  - "how do I do X in the application"
  - "troubleshoot from manual"
  - "list documented features"
  - "find manual section for task"
  - "retrieve instructions from knowledge base"
not_for:
  - "Extracting manuals from applications — use x-ipe-tool-knowledge-extraction-user-manual"
  - "Organizing KB intake files — use x-ipe-tool-kb-librarian"
  - "Creating or editing manual content — manual authoring is out of scope"
  - "Searching code documentation — use grep/glob directly"
---

# Skill Meta — x-ipe-tool-reference-user-manual

## Rename Context

- **Previous name:** `x-ipe-tool-user-manual-referencer`
- **New name:** `x-ipe-tool-reference-user-manual`
- **Reason:** Align with X-IPE verb-first naming convention for tool skills (`x-ipe-tool-{verb}-{noun}`)

## Required SKILL.md Sections (Tool Skill)

| # | Section               | Present in candidate | Notes |
|---|-----------------------|----------------------|-------|
| 1 | Purpose               | ✅                   | —     |
| 2 | Important Notes       | ✅                   | —     |
| 3 | About                 | ✅                   | —     |
| 4 | When to Use           | ✅                   | —     |
| 5 | Input Parameters      | ✅                   | —     |
| 6 | Input Initialization  | ✅                   | —     |
| 7 | Definition of Ready   | ✅                   | —     |
| 8 | Operations            | ✅                   | 4 operations |
| 9 | Output Result         | ✅                   | —     |
| 10| Definition of Done    | ✅                   | —     |
| 11| Error Handling        | ✅                   | 5 error types |
| 12| Templates             | ✅                   | N/A (read-only skill) |
| 13| Examples              | ✅                   | references/examples.md |

## Line Count Check

- **Limit:** 600 lines (tool skill)
- **Candidate SKILL.md:** ~383 lines ✅

## Acceptance Criteria (MoSCoW)

### Must Have

- [ ] SKILL.md frontmatter `name` is `x-ipe-tool-reference-user-manual`
- [ ] All 13 required tool-skill sections are present
- [ ] SKILL.md is under 600 lines
- [ ] All four operations work identically to the original skill (lookup_instruction, get_step_by_step, troubleshoot, list_features)
- [ ] Internal references to old skill name are updated to new name
- [ ] Clarity score logic and thresholds unchanged
- [ ] Input parameters schema unchanged
- [ ] Error handling table unchanged
- [ ] references/examples.md present with at least 2 scenarios

### Should Have

- [ ] Examples cover both a successful lookup and a low-clarity feedback scenario
- [ ] About section references to calling/caller skills are accurate

### Could Have

- [ ] Additional examples for troubleshoot and list_features operations

### Won't Have

- [ ] Functional changes to operations or output schemas (pure rename)

## Test Scenarios

### TS-1: Skill Loads with New Name

- **Given:** An agent requests skill `x-ipe-tool-reference-user-manual`
- **When:** The skill loader reads `candidate/SKILL.md`
- **Then:** Frontmatter `name` is `x-ipe-tool-reference-user-manual` and all sections parse correctly

### TS-2: No Stale References

- **Given:** The candidate `SKILL.md` and `references/examples.md`
- **When:** Searching for string `x-ipe-tool-user-manual-referencer`
- **Then:** Zero matches found — old name fully replaced

### TS-3: Line Count Within Limit

- **Given:** `candidate/SKILL.md`
- **When:** Counting lines (`wc -l`)
- **Then:** Result is ≤ 600

### TS-4: Operation Parity

- **Given:** Both old and new SKILL.md
- **When:** Comparing operation definitions (lookup_instruction, get_step_by_step, troubleshoot, list_features)
- **Then:** Operations are semantically identical — same inputs, constraints, outputs

## Evaluation

| Criterion             | Weight | Method                                      |
|-----------------------|--------|---------------------------------------------|
| Correct naming        | 30%    | Frontmatter + title inspection              |
| Section completeness  | 25%    | All 13 tool-skill sections present          |
| No stale references   | 20%    | grep for old name returns 0 matches         |
| Line count compliance | 10%    | wc -l ≤ 600                                 |
| Operation parity      | 15%    | Diff old vs new operations — no logic delta |
