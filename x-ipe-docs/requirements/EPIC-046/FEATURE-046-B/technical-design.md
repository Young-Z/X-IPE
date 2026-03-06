# Technical Design — FEATURE-046-B: Restructure 4 Ideation-Stage Skills

> Feature: FEATURE-046-B
> Epic: EPIC-046
> Spec: x-ipe-docs/requirements/EPIC-046/FEATURE-046-B/specification.md
> program_type: skills
> tech_stack: [Markdown, XML]

---

## Part 1: Agent Summary

### What Changes

4 skill SKILL.md files restructured from flat `<step_N>` to `<phase_N>` → `<step_N_M>` hierarchy, plus 1 folder rename.

### Change Impact

| # | File | Change Type | Lines Affected |
|---|------|-------------|---------------|
| 1 | `.github/skills/x-ipe-task-based-ideation-v2/` → `x-ipe-task-based-ideation/` | Rename folder + rewrite SKILL.md | ~488 lines |
| 2 | `.github/skills/x-ipe-task-based-idea-mockup/SKILL.md` | Rewrite Execution Flow + Procedure | ~482 lines |
| 3 | `.github/skills/x-ipe-task-based-idea-to-architecture/SKILL.md` | Rewrite Execution Flow + Procedure | ~395 lines |
| 4 | `.github/skills/x-ipe-task-based-share-idea/SKILL.md` | Rewrite Execution Flow + Procedure | ~397 lines |

### Approach

For each skill:
1. Copy production SKILL.md to candidate folder
2. Replace Execution Flow table with phase-based format
3. Replace Execution Procedure `<step_N>` with `<phase_N>` → `<step_N_M>`
4. Add skip markers for non-applicable phases
5. Validate line count < 500
6. Merge candidate → production

---

## Part 2: Implementation Guide

### Change 1: Rename ideation-v2 → ideation

**Action:**
```bash
# Rename production folder
mv .github/skills/x-ipe-task-based-ideation-v2 .github/skills/x-ipe-task-based-ideation

# Update candidate folder
mv x-ipe-docs/skill-meta/x-ipe-task-based-ideation-v2 x-ipe-docs/skill-meta/x-ipe-task-based-ideation
```

**In SKILL.md frontmatter:**
```yaml
# Before
name: x-ipe-task-based-ideation-v2
# After
name: x-ipe-task-based-ideation
```

**References to update:**
- Frontmatter `name:` field
- Any self-references in the file
- All paths referencing `ideation-v2` → `ideation`

### Change 2: Ideation — Phase Structure

**Execution Flow table:**

| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 1. 博学之 (Study Broadly) | 1.1 | Load Ideation Toolbox Meta | Parse tools.json, load skill configs | config loaded |
| | 1.2 | Analyze Idea Files | Read uploaded files, identify themes/gaps | files analyzed |
| | 1.3 | Research Common Principles | Search industry best practices | research complete |
| 2. 审问之 (Inquire Thoroughly) | 2.1 | Generate Understanding Summary | Share initial summary for validation | summary shared |
| | 2.2 | Brainstorming Session | Ask clarifying questions, iterate | idea refined |
| 3. 慎思之 (Think Carefully) | 3.1 | Critique and Feedback | Sub-agent reviews against quality criteria | feedback received |
| 4. 明辨之 (Discern Clearly) | 4.1 | Improve and Deliver Summary | Address critique, decide final direction | summary finalized |
| 5. 笃行之 (Practice Earnestly) | 5.1 | Generate Idea Draft | Create idea-summary-vN.md | draft created |
| | 5.2 | Complete and Request Review | Mode-aware completion | human approves |

**Procedure structure:**

```xml
<procedure name="ideation">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <phase_1 name="博学之 — Study Broadly">
    <step_1_1> (old step 1: Load Ideation Toolbox Meta) </step_1_1>
    <step_1_2> (old step 2: Analyze Idea Files) </step_1_2>
    <step_1_3> (old step 5: Research Common Principles — MOVED UP) </step_1_3>
  </phase_1>

  <phase_2 name="审问之 — Inquire Thoroughly">
    <step_2_1> (old step 3: Generate Understanding Summary) </step_2_1>
    <step_2_2> (old step 4: Brainstorming Session) </step_2_2>
  </phase_2>

  <phase_3 name="慎思之 — Think Carefully">
    <step_3_1> (old step 7: Critique and Feedback) </step_3_1>
  </phase_3>

  <phase_4 name="明辨之 — Discern Clearly">
    <step_4_1> (old step 8: Improve and Deliver Summary) </step_4_1>
  </phase_4>

  <phase_5 name="笃行之 — Practice Earnestly">
    <step_5_1> (old step 6: Generate Idea Draft — MOVED DOWN) </step_5_1>
    <step_5_2> (old step 9: Complete and Request Review) </step_5_2>
  </phase_5>
</procedure>
```

### Change 3: Idea Mockup — Phase Structure

| Phase | Step | Name | Gate |
|-------|------|------|------|
| 1. 博学之 (Study Broadly) | 1.1 | Validate Folder | folder validated |
| | 1.2 | Load Config | config loaded |
| | 1.3 | Read Idea Summary | summary loaded |
| | 1.4 | Research Design References | references gathered |
| 2. 审问之 (Inquire Thoroughly) | 2.1 | Identify Mockup Needs | needs identified |
| 3. 慎思之 (Think Carefully) | 3.1 | Load Brand Theme and Plan | theme loaded, plan ready |
| 4. 明辨之 (Discern Clearly) | — | SKIP | single approach |
| 5. 笃行之 (Practice Earnestly) | 5.1 | Create Mockups | mockups created |
| | 5.2 | Save Artifacts | artifacts saved |
| | 5.3 | Update Idea Summary | summary updated |
| | 5.4 | Complete | DoD verified |

**Step mapping:** old 1→1.1, 2→1.2, 3→1.3, 5→1.4, 4→2.1, 6→3.1, 7→5.1, 8→5.2, 9→5.3, 10→5.4

### Change 4: Idea to Architecture — Phase Structure

| Phase | Step | Name | Gate |
|-------|------|------|------|
| 1. 博学之 (Study Broadly) | 1.1 | Validate Folder | folder validated |
| | 1.2 | Load Config | config loaded |
| | 1.3 | Read Idea Summary | summary parsed |
| 2. 审问之 (Inquire Thoroughly) | 2.1 | Identify Architecture Needs | needs identified |
| 3. 慎思之 (Think Carefully) | — | SKIP | idea-level only |
| 4. 明辨之 (Discern Clearly) | 4.1 | Select Diagram Types | types selected |
| 5. 笃行之 (Practice Earnestly) | 5.1 | Create Diagrams | diagrams created |
| | 5.2 | Save Artifacts | artifacts saved |
| | 5.3 | Update Idea Summary | summary updated |
| | 5.4 | Complete | human approves |

**Step mapping:** old 1→1.1, 2→1.2, 3→1.3, 4→2.1+4.1(split), 5→5.1, 6→5.2, 7→5.3, 8→5.4

### Change 5: Share Idea — Phase Structure

| Phase | Step | Name | Gate |
|-------|------|------|------|
| 1. 博学之 (Study Broadly) | 1.1 | Load Config and Detect Tools | config loaded |
| | 1.2 | Identify Source File | source found |
| 2. 审问之 (Inquire Thoroughly) | 2.1 | Confirm Target Formats | formats confirmed |
| 3. 慎思之 (Think Carefully) | — | SKIP | no trade-offs |
| 4. 明辨之 (Discern Clearly) | — | SKIP | format confirmed |
| 5. 笃行之 (Practice Earnestly) | 5.1 | Prepare Content Structure | content ready |
| | 5.2 | Execute Conversion | files generated |
| | 5.3 | Verify and Complete | DoD validated |

**Step mapping:** old 1→1.1, 2→1.2, 3→2.1, 4→5.1, 5→5.2, 6→5.3

---

## Constraints

- Each SKILL.md must stay under 500 lines
- All changes through candidate workflow
- Reshuffle only — no new logic, no new steps
- Preserve all DoR/DoD, Input Parameters, Output Result, References, Sub-agent sections
