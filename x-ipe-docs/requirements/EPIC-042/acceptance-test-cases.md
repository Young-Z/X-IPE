# EPIC-042 Acceptance Test Cases

## Summary

| Feature | Tests | Passed | Failed |
|---------|-------|--------|--------|
| FEATURE-042-A (Config & Resolution MVP) | 6 | 6 | 0 |
| FEATURE-042-B (Conditional & Error) | 4 | 4 | 0 |
| FEATURE-042-C (Defaults & Preview) | 5 | 5 | 0 |
| FEATURE-042-D (Migration) | 4 | 4 | 0 |
| **Total** | **19** | **19** | **0** |

**Test Environment:** Chrome DevTools MCP against `http://localhost:5858` (Flask app)
**Test Workflow:** `wf-001-greedy-snake` (Refine Idea action)
**Date:** 2025-07-19

---

## FEATURE-042-A: Config & Resolution MVP

### TC-01: Workflow-prompts array exists in config ✅
- **AC:** AC-042.1
- **Priority:** P0
- **Steps:** Fetch `/api/config/copilot-prompt`, check `workflow-prompts` array
- **Result:** API returns 9 entries in workflow-prompts array
- **Status:** PASS

### TC-02: Workflow-mode uses workflow-prompts source ✅
- **AC:** AC-042.2
- **Priority:** P0
- **Steps:** Open Refine Idea modal in workflow mode, verify instructions source
- **Result:** Modal shows resolved workflow-prompt template, not legacy `<current-idea-file>`
- **Status:** PASS

### TC-03: $output:raw-idea$ resolves to dropdown value ✅
- **AC:** AC-042.3
- **Priority:** P0
- **Steps:** Open modal, check instructions text for resolved variable
- **Result:** Resolved to `x-ipe-docs/ideas/wf-001-greedy-snake/new idea.md`
- **Status:** PASS

### TC-04: Free-mode backward compatibility ✅
- **AC:** AC-042.9
- **Priority:** P0
- **Steps:** Switch to FREE mode, open Copilot > Refine Idea on same file
- **Result:** Free-mode bypasses modal entirely, sends legacy command to console directly
- **Status:** PASS

### TC-05: $feature-id$ variable resolution ✅
- **AC:** AC-MVP.2
- **Priority:** P1
- **Steps:** Verified via unit tests (feature-level actions not accessible in current workflow stage)
- **Result:** Unit tests confirm `$feature-id$` resolved from `.feature-id-group` input
- **Status:** PASS

### TC-06: Schema validation (all required fields) ✅
- **AC:** AC-MVP.3
- **Priority:** P1
- **Steps:** Fetch API, check each entry for required fields: id, action, icon, input_source, prompt-details
- **Result:** All 9 entries have all required fields
- **Status:** PASS

---

## FEATURE-042-B: Conditional & Error Handling

### TC-07: Conditional block skipped when N/A ✅
- **AC:** AC-042-B.1
- **Priority:** P0
- **Steps:** Set uiux-reference dropdown to N/A, check instructions
- **Result:** `<and uiux reference: $output:uiux-reference$>` block completely stripped. Clean output: `"refine the idea ...path... with ideation skill"`
- **Status:** PASS

### TC-08: Conditional block included when resolved ✅
- **AC:** AC-042-B.2
- **Priority:** P0
- **Steps:** Set uiux-reference to `auto-detect`, check instructions
- **Result:** Instructions include `"and uiux reference: auto-detect"`
- **Status:** PASS

### TC-09: No whitespace artifacts after skip ✅
- **AC:** AC-042-B.5
- **Priority:** P1
- **Steps:** After conditional skip, inspect for double-spaces or artifacts
- **Result:** Clean single-space output, no artifacts
- **Status:** PASS

### TC-10: Legacy placeholders in free mode ✅
- **AC:** AC-042-B.7
- **Priority:** P0
- **Steps:** In FREE mode, use Copilot > Refine Idea
- **Result:** Free-mode copilot dropdown sends legacy command to console, does not use workflow-prompts
- **Status:** PASS

---

## FEATURE-042-C: Defaults, Preview & Command

### TC-11: Dropdown defaults to deliverable path ✅
- **AC:** AC-042-C
- **Priority:** P0
- **Steps:** Open modal in workflow mode, check raw-idea dropdown default
- **Result:** raw-idea dropdown auto-selected compose_idea deliverable path
- **Status:** PASS

### TC-12: Instructions readonly in workflow mode ✅
- **AC:** AC-042-C
- **Priority:** P0
- **Steps:** Check instructions element attributes
- **Result:** `readonly` attr, `.instructions-readonly` CSS class, `contentEditable=false`
- **Status:** PASS

### TC-13: Live preview updates on dropdown change ✅
- **AC:** AC-042-C
- **Priority:** P0
- **Steps:** Change uiux-reference dropdown from N/A to auto-detect
- **Result:** Instructions update in real-time, conditional block appears/disappears
- **Status:** PASS

### TC-14: Extra instructions stays editable ✅
- **AC:** AC-042-C
- **Priority:** P1
- **Steps:** Check extra-input textarea attributes in workflow mode
- **Result:** No readonly attribute, no instructions-readonly class
- **Status:** PASS

### TC-15: Command composition (resolved + extra) ✅
- **AC:** AC-042-C
- **Priority:** P1
- **Steps:** Verify `_composeCommand()` concatenates resolved instructions with extra
- **Result:** Unit tests + code inspection confirm resolved + "\\n\\n" + extra pattern
- **Status:** PASS

---

## FEATURE-042-D: Migration

### TC-16: All 9 entries present ✅
- **AC:** AC-042-D.1
- **Priority:** P0
- **Steps:** Fetch API, count workflow-prompts array entries
- **Result:** 9 entries: refine_idea, design_mockup, requirement_gathering, feature_breakdown, feature_refinement, technical_design, test_generation, implementation, acceptance_testing
- **Status:** PASS

### TC-17: English translations exist ✅
- **AC:** AC-042-D.2
- **Priority:** P0
- **Steps:** Check each entry has prompt-details with language=en
- **Result:** All 9 entries have English translations
- **Status:** PASS

### TC-18: Chinese translations exist ✅
- **AC:** AC-042-D.3
- **Priority:** P0
- **Steps:** Check each entry has prompt-details with language=zh
- **Result:** All 9 entries have Chinese translations
- **Status:** PASS

### TC-19: Deprecation markers on old entries ✅
- **AC:** AC-042-D.8
- **Priority:** P1
- **Steps:** Check legacy prompt entries for `_deprecated` field
- **Result:** 8 legacy entries have `_deprecated: "superseded by workflow-prompts[action]"` markers
- **Status:** PASS

---

## Screenshot Evidence

![Action Execution Modal - Workflow Mode](x-ipe-docs/requirements/EPIC-042/acceptance-screenshot-modal.png)
