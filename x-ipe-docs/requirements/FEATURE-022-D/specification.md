# FEATURE-022-D: Feedback Storage & Submission

**Feature ID:** FEATURE-022-D  
**Version:** v1.0  
**Status:** Refined  
**Created:** 01-28-2026  
**Updated:** 01-28-2026 17:10:00

## Overview

Backend API for saving feedback to structured folder format and frontend workflow for submission with terminal command generation.

## Dependencies

- **FEATURE-022-C:** Requires feedback entries to submit

## Acceptance Criteria

### 1. Backend API

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-1.1 | Backend route: `POST /api/uiux-feedback` | Must |
| AC-1.2 | Request body MUST include entry JSON (id, name, url, elements, screenshot, description) | Must |
| AC-1.3 | API MUST validate required fields (name, url, elements) | Must |
| AC-1.4 | API MUST return 400 for invalid/missing required fields | Must |
| AC-1.5 | API MUST return 201 on successful save | Must |
| AC-1.6 | API MUST return folder path in response | Must |

### 2. Folder Structure

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-2.1 | Creates folder: `{project_root}/x-ipe-docs/uiux-feedback/{entry-name}/` | Must |
| AC-2.2 | Saves `feedback.md` with structured content | Must |
| AC-2.3 | Saves `page-screenshot.png` if screenshot captured | Must |
| AC-2.4 | Handle duplicate entry names (append `-1`, `-2` suffix) | Must |
| AC-2.5 | Create parent `uiux-feedback` folder if not exists | Must |

### 3. Feedback.md Template

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-3.1 | Include entry ID in document | Must |
| AC-3.2 | Include target URL | Must |
| AC-3.3 | Include submission date/time | Must |
| AC-3.4 | List selected elements with CSS selectors | Must |
| AC-3.5 | Include user feedback description | Must |
| AC-3.6 | Include screenshot reference if available | Must |
| AC-3.7 | Use proper markdown formatting | Must |

### 4. Frontend Submit Flow

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-4.1 | Submit button in feedback entry triggers API call | Must |
| AC-4.2 | On success: toast notification "Feedback saved" | Must |
| AC-4.3 | On success: entry status changes to "submitted" | Must |
| AC-4.4 | On success: terminal command typed (not executed) | Must |
| AC-4.5 | On success: clear element selection | Must |
| AC-4.6 | On failure: entry status "failed" with error | Must |
| AC-4.7 | On failure: show error toast with message | Must |
| AC-4.8 | Disable submit button while submitting | Must |
| AC-4.9 | Allow submit with empty description | Must |
| AC-4.10 | Allow submit if screenshot capture failed | Must |

### 5. Terminal Command

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-5.1 | After successful submit, type command into terminal | Must |
| AC-5.2 | Command format: `Get uiux feedback, please visit feedback folder {path} to get details.` | Must |
| AC-5.3 | Command MUST NOT be executed automatically | Must |
| AC-5.4 | User can review and press Enter to execute | Should |

### 6. Entry Status Management

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-6.1 | Entry status: "draft" → "submitting" → "submitted" | Must |
| AC-6.2 | Entry status: "draft" → "submitting" → "failed" on error | Must |
| AC-6.3 | Visual indicator for each status | Must |
| AC-6.4 | Submitted entries MAY be re-submitted | Could |
| AC-6.5 | Delete button available in all states | Must |

### 7. Error Handling

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-7.1 | Handle network errors gracefully | Must |
| AC-7.2 | Handle file system errors (permissions, disk full) | Must |
| AC-7.3 | Show meaningful error messages to user | Must |
| AC-7.4 | Log detailed errors to console | Must |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | System SHALL provide POST /api/uiux-feedback endpoint | Must |
| FR-2 | System SHALL create feedback folder structure | Must |
| FR-3 | System SHALL save feedback.md with structured content | Must |
| FR-4 | System SHALL save screenshot as PNG file | Must |
| FR-5 | System SHALL update entry status on success/failure | Must |
| FR-6 | System SHALL type terminal command on success | Must |
| FR-7 | System SHALL handle duplicate folder names | Must |

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | API response time | < 2 seconds |
| NFR-2 | Screenshot file size | < 2MB |
| NFR-3 | Max feedback text length | 10,000 characters |

## Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| EC-1 | Screenshot is null | Save feedback.md without screenshot reference |
| EC-2 | Description is empty | Save with empty feedback section |
| EC-3 | Folder name already exists | Append `-1`, `-2`, etc. |
| EC-4 | File system permission denied | Return 500 with error message |
| EC-5 | Invalid base64 screenshot | Log warning, save without screenshot |
| EC-6 | Network disconnect during submit | Show error, keep entry in draft |

## Technical Considerations

- Use Python's `pathlib` for cross-platform path handling
- Validate base64 screenshot before decoding
- Use Flask's jsonify for API responses
- Consider rate limiting for API endpoint

## Feedback.md Template

```markdown
# UI/UX Feedback

**ID:** Feedback-YYYYMMDD-HHMMSS
**URL:** http://localhost:3000/dashboard
**Date:** YYYY-MM-DD HH:MM:SS

## Selected Elements

- `button.submit` - CSS selector
- `div.form-group` - CSS selector

## Feedback

{User's feedback text}

## Screenshot

![Screenshot](./page-screenshot.png)
```

## Out of Scope (v1)

- Edit submitted feedback
- Export all feedback as ZIP
- Batch submit multiple entries
- Feedback categories/tags
