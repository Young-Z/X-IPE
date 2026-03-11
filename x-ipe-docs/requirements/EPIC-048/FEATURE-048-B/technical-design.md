# FEATURE-048-B: Consultation Integration — Technical Design

## Part 1: Agent-Facing Summary

### What This Feature Does
Adds config-filtered tool skill consultation to two skills:
1. **technical-design** Step 2.2 (Research) — discovers tool capabilities to inform Part 2 design
2. **refactoring-analysis** Phase 4 (Generate Suggestions) — compares coding standard gaps against tool built-in practices

### Key Principle
Consultation is **informational only**. Neither skill delegates code execution. Part 2 format remains tool-independent (FR-048.1.5).

### Component Table

| Component | Tag | File | Change Type |
|-----------|-----|------|-------------|
| Technical Design Tool Scan | `td-tool-scan` | `.github/skills/x-ipe-task-based-technical-design/SKILL.md` | Modify Step 2.2 |
| Refactoring Analysis Tool Consult | `ra-tool-consult` | `.github/skills/x-ipe-tool-refactoring-analysis/SKILL.md` | Modify Phase 4 |
| Tools Config — Consultation Section | `tools-config-consultation` | `x-ipe-docs/config/tools.json` | Add `stages.feature.consultation` |

### Usage Example

**Technical Design Step 2.2 (after change):**
```
1. DISCOVER: Scan .github/skills/x-ipe-tool-implementation-*/
2. READ CONFIG: Read tools.json → stages.feature.consultation
3. FILTER: Only ENABLED tools (or all if config missing)
4. READ each enabled tool's "Built-In Practices" and "Operations" sections
5. DOCUMENT tool capability summary
6. [existing research steps continue...]
```

**Refactoring Analysis Phase 4 (after change):**
```
1. [existing gap analysis...]
2. DISCOVER + CONFIG + FILTER tool skills (same 3-layer pattern)
3. FOR tech_stack match: compare detected gaps against tool's Built-In Practices
4. IF tool already enforces a practice → note it as "auto-enforced by tool"
5. Suggestions reference tool capabilities for target patterns
```

---

## Part 2: Implementation Guide

### Change 1: tools.json — Add `stages.feature.consultation`

**File:** `x-ipe-docs/config/tools.json`

Add a new section at the same level as `stages.feature.implementation`:

```json
"consultation": {
  "_order": 3,
  "_extra_instruction": "Consultation mode: read tool capabilities for informational use only. Do not invoke tools for code execution.",
  "x-ipe-tool-implementation-python": true,
  "x-ipe-tool-implementation-typescript": true,
  "x-ipe-tool-implementation-html5": true,
  "x-ipe-tool-implementation-java": true,
  "x-ipe-tool-implementation-mcp": true,
  "x-ipe-tool-implementation-general": true
}
```

**Rationale:** All tools enabled by default for consultation — the cost of reading more skill files is negligible, and having full visibility produces better designs.

### Change 2: technical-design SKILL.md — Update Step 2.2

**File:** `.github/skills/x-ipe-task-based-technical-design/SKILL.md`
**Location:** Phase 2, Step 2.2 (lines ~221-233)

**Before (current):**
```xml
<step_2_2>
  <name>Research Best Practices</name>
  <action>
    1. SEARCH for official documentation
    2. LOOK for existing libraries
    3. CHECK reference implementations
    4. REVIEW API documentation
    5. IF mockup_list provided: analyze mockups
    6. DOCUMENT findings
  </action>
</step_2_2>
```

**After (new):**
```xml
<step_2_2>
  <name>Research Best Practices</name>
  <action>
    1. CONSULT TOOL SKILLS (config-filtered):
       a. DISCOVER: Scan .github/skills/x-ipe-tool-implementation-*/ for available tools
       b. READ CONFIG: Read x-ipe-docs/config/tools.json → stages.feature.consultation
          - IF section missing/empty → config_active = false (all tools enabled)
          - ELSE → config_active = true (opt-in filtering)
       c. FILTER: IF config_active → only ENABLED tools; always force-enable general
       d. FOR EACH enabled tool: read "Built-In Practices" and "Operations" sections
       e. DOCUMENT as "Tool Capability Summary" (informational only)
    2. SEARCH for official documentation
    3. LOOK for existing libraries (don't reinvent the wheel)
    4. CHECK reference implementations
    5. REVIEW API documentation for planned libraries
    6. IF mockup_list provided AND scope includes [Frontend] or [Full Stack]:
       [existing mockup analysis - unchanged]
    7. DOCUMENT findings for design decisions (include tool capability summary)
  </action>
  <constraints>
    - Tool consultation is INFORMATIONAL ONLY — do not invoke tool skills for code execution
    - Part 2 format MUST remain independent of tool availability (FR-048.1.5)
  </constraints>
  <output>Research findings including tool capability summary</output>
</step_2_2>
```

**Impact on Step 3.1 (Part 2 writing):** Add guidance to leverage tool capabilities:
- After line `6. IDENTIFY and record program_type and tech_stack:` add:
```
7. LEVERAGE tool capability summary from Step 2.2:
   - Reference tool built-in practices instead of duplicating them
   - Focus Part 2 on what tools NEED: module boundaries, API contracts, data models
   - Note: Part 2 format remains independent of tool availability
```

### Change 3: refactoring-analysis SKILL.md — Update Phase 4

**File:** `.github/skills/x-ipe-tool-refactoring-analysis/SKILL.md`
**Location:** Phase 4 — Generate Suggestions (lines ~158-164)

**Before (current):**
```
Phase 4 — Generate Suggestions:
  1. ANALYZE quality gaps → derive suggestion categories
  2. SCAN code for principle violations (SRP, DRY, KISS, YAGNI, SoC)
  3. PRIORITIZE into primary (MUST) and secondary (nice-to-have) principles
  4. FORMULATE specific, measurable goals with priority and rationale
  5. DEFINE target structure and constraints
  BLOCKING: Every suggestion must trace back to a documented gap
```

**After (new):**
```
Phase 4 — Generate Suggestions:
  1. CONSULT TOOL SKILLS (config-filtered):
     a. DISCOVER: Scan .github/skills/x-ipe-tool-implementation-*/ for available tools
     b. READ CONFIG: Read x-ipe-docs/config/tools.json → stages.feature.consultation
        - IF section missing/empty → config_active = false (all tools enabled)
        - ELSE → config_active = true (opt-in filtering)
     c. FILTER: IF config_active → only ENABLED tools; always force-enable general
     d. FOR detected tech_stack: read matched tool's "Built-In Practices"
  2. ANALYZE quality gaps → derive suggestion categories
  3. SCAN code for principle violations (SRP, DRY, KISS, YAGNI, SoC)
  4. CROSS-REFERENCE gaps against tool built-in practices:
     - IF tool already enforces a practice → mark gap as "auto-enforced"
     - IF tool provides conventions → reference them in suggestion
  5. PRIORITIZE: primary (MUST) and secondary (nice-to-have)
  6. FORMULATE specific, measurable goals with priority and rationale
  7. DEFINE target structure and constraints
  BLOCKING: Every suggestion must trace back to a documented gap
```

### Line Budget Impact

| File | Current Lines | Added Lines | Est. New Total | Under 500? |
|------|--------------|-------------|----------------|------------|
| technical-design SKILL.md | 504 | +8 (step 2.2) +3 (step 3.1) = +11 | ~515 | ⚠️ Need trim |
| refactoring-analysis SKILL.md | 260 | +6 (phase 4) = +6 | ~266 | ✅ |

**Technical-design is at 504 lines.** Adding ~11 lines pushes it to ~515. To stay under 500:
- Consolidate mockup analysis text in Step 2.2 (currently verbose at ~3 lines → compress to 1)
- Combine items 2-5 in Step 2.2 into a single enumeration

### Design Change Log

| Date | Change | Reason |
|------|--------|--------|
| 03-10-2026 | Initial design | FEATURE-048-B specification |
