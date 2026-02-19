# FEATURE-037-B Acceptance Test Results

**Feature:** Compose Idea Modal — Link Existing & Re-Edit  
**Date:** 2025-02-19  
**Tester:** Zephyr (AI Agent) via Chrome DevTools MCP  
**Server:** Flask on localhost:5858  
**Workflow:** test2

---

## Test Results Summary

| TC | Description | Status | Notes |
|----|------------|--------|-------|
| TC-001 | Modal opens with correct heading and tabs | ✅ PASS | "Compose Idea" heading, "Link Existing" tab visible |
| TC-002 | Link Existing panel renders | ✅ PASS | File tree (2509 items), search input, preview area |
| TC-003 | File preview loads on selection | ✅ PASS | 4206 chars rendered via marked.js, submit enables |
| TC-004 | Search filter works | ✅ PASS | "workflow" → 5 visible, 2504 hidden |
| TC-005 | Re-edit confirm dialog | ✅ PASS | "...already completed. Do you want to re-edit it?" |
| TC-006 | Edit mode UI | ✅ PASS | "Edit Idea" heading, "Update Idea" btn, name disabled, editor pre-filled |
| TC-007 | Gate blocks re-open | ✅ PASS | Error toast: "Cannot re-open: requirement_gathering in requirement stage is already started" |
| TC-008 | Confirm cancel aborts | ✅ PASS | confirm() returns false → modal does not open |

**Result: 8/8 PASS**

---

## Acceptance Criteria Coverage

### Link Existing Mode
- **AC-001** (Tab visible): TC-001 ✅
- **AC-002** (Panel layout): TC-002 ✅
- **AC-003** (File tree): TC-002 ✅
- **AC-004** (Search filter): TC-004 ✅
- **AC-005** (Preview): TC-003 ✅
- **AC-006** (Submit enables): TC-003 ✅

### Re-Edit Mode
- **AC-010** (Confirm dialog): TC-005 ✅
- **AC-011** (Edit heading): TC-006 ✅
- **AC-012** (Name locked): TC-006 ✅
- **AC-013** (Content pre-filled): TC-006 ✅
- **AC-014** (Gate check): TC-007 ✅

---

## Bugs Found & Fixed During Testing

1. **`node.type === 'directory'` bug** — API returns `type: "folder"`, not `"directory"`. Fixed: added `|| node.type === 'folder'` check.
2. **Edit mode submit disabled** — `activeMode` was `'edit'` but `updateSubmitState` only enabled for `'create'`. Fixed: default `activeMode` to `'create'` when `mode='edit'`.
