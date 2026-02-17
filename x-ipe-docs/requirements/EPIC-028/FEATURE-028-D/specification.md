# Feature Specification: Settings Language Switch (Web UI)

> Feature ID: FEATURE-028-D  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-11-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-11-2026 | Initial specification from CR-002 and IDEA-020 |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Settings Language Switch | HTML | [mockups/settings-language-v1.html](mockups/settings-language-v1.html) | Interactive mockup with 4 scenarios: default state, confirmation dialog, success toast, same-language guard | current |

> **Note:** UI/UX requirements and acceptance criteria below are derived from the mockup marked as "current".  
> The mockup was created during TASK-286 and approved by the user before this specification was written. Feature scope has not changed since mockup creation.

## Overview

FEATURE-028-D adds a language switching capability to the X-IPE Settings web page, allowing users to change the project language (English ↔ 中文) directly from the browser instead of running `x-ipe upgrade --lang` from the CLI. This mirrors the existing CLI behavior — switching the language field in `.x-ipe.yaml` and re-extracting copilot instructions — but exposes it through the Settings UI with AJAX and toast notifications.

The motivation is usability: users who interact with X-IPE primarily through the web interface should not need to drop to the terminal for a common configuration change. The language switch is already fully implemented on the backend (FEATURE-028-B via ScaffoldManager); this feature adds a thin web layer on top.

The target user is any developer using X-IPE in a non-English environment who has already set up the project and wants to switch or verify their language setting from the Settings page.

## User Stories

- As a **developer**, I want to **switch the project language from the Settings page**, so that **I don't need to use the CLI for a simple configuration change**.
- As a **developer**, I want to **see the current project language at a glance**, so that **I can verify the active language without opening `.x-ipe.yaml`**.
- As a **developer**, I want to **receive a confirmation before switching language**, so that **I don't accidentally regenerate copilot instructions**.
- As a **developer**, I want to **be notified of the result via toast**, so that **I know the switch succeeded or failed without a page reload**.

## Acceptance Criteria

- [x] AC-1: Settings page MUST display a dedicated "Language" section positioned above the "Project Folders" section (AC-CR2-1)
- [x] AC-2: Language section MUST show the current language as a badge and a dropdown with options "English" and "中文" (AC-CR2-2)
- [x] AC-3: Selecting a different language MUST trigger a confirmation dialog warning that copilot instructions will be regenerated (AC-CR2-3)
- [x] AC-4: Confirming the dialog MUST send `POST /api/config/language` with body `{ "language": "en" | "zh" }` (AC-CR2-4)
- [x] AC-5: Backend MUST extract instructions for the new language BEFORE updating `.x-ipe.yaml` (atomicity — if extraction fails, language stays unchanged) (AC-CR2-5)
- [x] AC-6: On success, a toast notification MUST appear confirming the switch; the page MUST NOT reload (AC-CR2-6)
- [x] AC-7: Selecting the same language that is already active MUST be a no-op with an informational toast "Already using [language]" (AC-CR2-7)
- [x] AC-8: The dropdown MUST be disabled (non-interactive) while a switch operation is in progress (AC-CR2-8)
- [x] AC-9: Custom edits outside X-IPE markers in copilot-instructions files MUST be preserved after the switch (AC-CR2-9)
- [x] AC-10: UI layout MUST match the approved mockup (settings-language-v1.html) for the Language card, confirmation dialog, and toast components
- [x] AC-11: Visual styling (colors, spacing, typography) MUST be consistent with mockup (settings-language-v1.html)
- [x] AC-12: Interactive elements shown in mockup (settings-language-v1.html) — dropdown, confirm/cancel buttons, toast dismiss — MUST be present and functional
- [x] AC-13: On backend error, an error toast MUST display the error message and the dropdown MUST revert to the previous language selection
- [x] AC-14: The current language badge MUST update after a successful switch without page reload

## Functional Requirements

### FR-1: Language Section Rendering

**Description:** The Settings page must render a "Language" card above the "Project Folders" card on page load.

**Details:**
- Input: Current language from `GET /api/config` response (`language` field)
- Process: Render card with globe icon, "Language" header, current language badge, dropdown select pre-populated with active language
- Output: Visible Language section with correct active state

### FR-2: Same-Language Guard

**Description:** If the user selects the same language that is already active, the system must show an info toast and take no further action.

**Details:**
- Input: User selects language from dropdown
- Process: Compare selected value to current language; if equal, show informational toast
- Output: Toast "Already using {language name}" — no API call, no state change

### FR-3: Confirmation Dialog

**Description:** When the user selects a different language, a modal confirmation dialog must appear.

**Details:**
- Input: Selected language differs from current
- Process: Show modal with current → new language details and warning about instruction regeneration
- Output: User can confirm (proceed to FR-4) or cancel (revert dropdown, no action)

### FR-4: Language Switch API Call

**Description:** On confirmation, send an AJAX request to switch the language.

**Details:**
- Input: Confirmed new language code (`"en"` or `"zh"`)
- Process: `POST /api/config/language` with JSON body `{ "language": "<code>" }`. Dropdown is disabled during the request.
- Output: JSON response `{ "success": true, "language": "<code>" }` or `{ "success": false, "error": "<message>" }`

### FR-5: Backend Language Switch

**Description:** The backend endpoint must switch the language atomically using ScaffoldManager.

**Details:**
- Input: Language code from request body
- Process: 1) Validate language code is in `SUPPORTED_LANGUAGES`; 2) Call ScaffoldManager to extract/copy copilot instructions for new language; 3) Only after success, update `.x-ipe.yaml` language field; 4) Return result
- Output: Success or error response

### FR-6: Success Feedback

**Description:** On success, update the UI and show a success toast.

**Details:**
- Input: Successful API response
- Process: Update current language badge text, re-enable dropdown, show success toast
- Output: Badge shows new language, toast "Language switched to {language name}"

### FR-7: Error Handling

**Description:** On failure, revert UI state and show error toast.

**Details:**
- Input: Error API response or network error
- Process: Revert dropdown to previous language, re-enable dropdown, show error toast with message
- Output: Dropdown back to original value, error toast visible

## Non-Functional Requirements

### NFR-1: Performance

- Language switch API response time: < 3 seconds (instruction extraction involves file I/O)
- UI remains responsive during operation (dropdown disabled but page interactive)
- Toast auto-dismisses after 5 seconds

### NFR-2: Security

- POST endpoint requires same session/authentication as other settings endpoints
- Language code input validated server-side against `SUPPORTED_LANGUAGES` allowlist
- No path traversal possible via language parameter

### NFR-3: Accessibility

- Dropdown must be keyboard-navigable
- Confirmation dialog must trap focus
- Toast must be announced to screen readers (ARIA live region)
- Disabled state must be communicated via `aria-disabled` and visual indicator

## UI/UX Requirements

### Layout

The Language section is a `.settings-card` positioned as the first card in the settings container, above "Project Folders".

### UI Elements

| Element | Type | Details |
|---------|------|---------|
| Language card | `.settings-card` | White background, border, subtle shadow (matches existing cards) |
| Globe icon | Bootstrap Icon | `bi-globe` in emerald-tinted box (matches mockup) |
| "Language" header | `.card-header` | Text "Language" with current language badge |
| Current language badge | `<span class="badge">` | Shows "English" or "中文" with checkmark icon |
| Dropdown | `<select>` | Options: "English" (value="en"), "中文" (value="zh"); custom styled |
| Info note | `.alert-warning` variant | Amber note: "Instructions will be regenerated. Custom edits outside X-IPE sections are preserved." |
| Confirmation modal | Bootstrap Modal | Amber warning icon, "Change Language?" title, from→to detail, Cancel / Proceed buttons |
| Success toast | Bootstrap Toast | Dark background, green checkmark, "Language switched to {name}" |
| Info toast | Bootstrap Toast | Info variant, "Already using {name}" |
| Error toast | Bootstrap Toast | Error variant with error message |

### User Flows

**Flow 1: Successful Language Switch**
1. User opens Settings page → Language card displays with current language
2. User changes dropdown from "English" to "中文"
3. Confirmation dialog appears with warning
4. User clicks "Proceed"
5. Dropdown becomes disabled, loading indicator appears
6. API call completes successfully
7. Badge updates to "中文", dropdown re-enabled, success toast shown

**Flow 2: Cancel Language Switch**
1. User changes dropdown selection
2. Confirmation dialog appears
3. User clicks "Cancel"
4. Dropdown reverts to previous value, no API call

**Flow 3: Same Language**
1. User selects the currently active language
2. Info toast appears: "Already using English"
3. No dialog, no API call

**Flow 4: Error**
1. User confirms language switch
2. API call fails
3. Dropdown reverts to previous value, re-enabled
4. Error toast with message

## Dependencies

### Internal Dependencies

- **FEATURE-028-A (Schema & Migration):** Provides the `language` field in `.x-ipe.yaml` schema
- **FEATURE-028-B (CLI & Instructions):** Provides `ScaffoldManager.copy_copilot_instructions(language=...)` and `SUPPORTED_LANGUAGES` — reused by the backend endpoint
- **Existing Settings infrastructure:** `settings_routes.py` provides the route blueprint; `settings.html` provides the page template and JS patterns (`ProjectFoldersManager`, `ConfigManager`)
- **`GET /api/config`:** Already returns the `language` field — used to populate the initial dropdown state

### External Dependencies

- **Bootstrap 5:** Modal and Toast components (already in project)
- **Bootstrap Icons:** `bi-globe` icon (already in project)

## Business Rules

- **BR-1:** Only two languages are supported: `en` (English) and `zh` (中文). The dropdown MUST NOT offer other options.
- **BR-2:** The language setting is project-scoped (stored in `.x-ipe.yaml` per project), not global.
- **BR-3:** Switching language always regenerates copilot instructions from the bilingual template — there is no "keep current instructions" option.
- **BR-4:** If a project has no `language` field in `.x-ipe.yaml`, the default is `en`.

## Edge Cases & Constraints

### Edge Case 1: Missing Language Field

**Scenario:** Project `.x-ipe.yaml` has no `language` key (pre-FEATURE-028-A project).  
**Expected Behavior:** Default to `en`, display "English" as current language. Switching to `zh` adds the `language` field.

### Edge Case 2: Network Error During Switch

**Scenario:** Network connection drops during `POST /api/config/language`.  
**Expected Behavior:** Fetch throws network error → dropdown reverts, error toast displays "Network error — please try again."

### Edge Case 3: Concurrent Switch Attempts

**Scenario:** User rapidly clicks dropdown while a switch is in progress.  
**Expected Behavior:** Dropdown is disabled during operation (AC-8) — prevents concurrent requests.

### Edge Case 4: Instruction Extraction Failure

**Scenario:** ScaffoldManager fails to extract instructions (e.g., template file missing or corrupted).  
**Expected Behavior:** Backend returns error, `.x-ipe.yaml` is NOT updated (atomicity — AC-5), error toast shown.

### Edge Case 5: Settings Page Open in Multiple Tabs

**Scenario:** User has Settings open in two browser tabs and switches language in one.  
**Expected Behavior:** The other tab's badge/dropdown will be stale until refreshed. No real-time sync required for v1.0.

### Edge Case 6: Invalid Language Code

**Scenario:** Malformed or unsupported language code sent to API (e.g., via curl or DevTools).  
**Expected Behavior:** Backend validates against `SUPPORTED_LANGUAGES`, returns 400 error with descriptive message.

## Out of Scope

- **Auto-detection of browser language** — not included in v1.0; language is an explicit project setting
- **Real-time sync across tabs** — stale state in other tabs is acceptable
- **More than two languages** — only `en` and `zh` are supported; adding languages requires schema extension
- **Undo/rollback UI** — once switched, user can switch back manually but there is no "undo" button
- **Language preview** — no preview of what instructions will look like before switching

## Technical Considerations

- The backend endpoint should reuse `ScaffoldManager` logic rather than duplicating it — this is the same operation as `x-ipe upgrade --lang`
- The `POST /api/config/language` endpoint belongs in `settings_routes.py` alongside existing settings routes
- The Language section JS should follow the same class-based pattern (`LanguageManager`) as `ProjectFoldersManager` and `ConfigManager` in `settings.html`
- The confirmation dialog can use the existing reusable `ConfirmDialog` component from `confirm-dialog.js` or use a Bootstrap modal directly within the settings template (either approach is valid)
- The initial language value should come from the existing `GET /api/config` response to avoid an extra API call

## Open Questions

None — all questions were resolved during ideation (IDEA-020) and CR-002 review.
