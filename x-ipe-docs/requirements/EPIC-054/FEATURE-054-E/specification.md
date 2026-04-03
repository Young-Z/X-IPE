# Feature Specification: PII Protection & Masking

> Feature ID: FEATURE-054-E
> Version: v1.0
> Status: Refined
> Last Updated: 04-02-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-02-2026 | Initial specification |

## Linked Mockups

_No feature-specific mockups. PII masking is a data processing layer with status badge consumed by FEATURE-054-D toolbox._

## Overview

FEATURE-054-E provides the privacy and data protection layer for the behavior recording pipeline. It ensures that typed content in input fields is masked by default before events enter the recording buffer, password fields are never captured under any circumstance, and element metadata (CSS selectors, a11y tags, class names) is always captured since it carries no PII risk.

Users can opt-in to reveal specific non-sensitive fields via a per-session CSS selector whitelist configured in the toolbox UI. Masking is applied at capture time (before events enter the buffer), not as post-processing, ensuring that unmasked PII never exists in the recording data.

## User Stories

- **US-1:** As a Workplace user, I want typed content automatically masked, so that sensitive data is never recorded by default.
- **US-2:** As a Workplace user, I want password fields completely excluded from capture, so that credentials are never at risk.
- **US-3:** As a Workplace user, I want to whitelist specific non-sensitive fields, so that useful form data (e.g., search queries) can be captured when appropriate.

## Acceptance Criteria

### AC-054E-01: Default Masking

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054E-01a | GIVEN recording is active AND PII masking is on (default) WHEN user types into any input field THEN the captured value is `[MASKED]` instead of actual text | Unit |
| AC-054E-01b | GIVEN recording is active WHEN a typing event is captured with masking THEN element metadata (CSS selector, a11y tags, class names, field type) is still fully captured | Unit |

### AC-054E-02: Password Field Protection

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054E-02a | GIVEN recording is active WHEN user types into a field with `type="password"` THEN the field value is never captured (not even as `[MASKED]` — value field is `[PASSWORD_FIELD]`) | Unit |
| AC-054E-02b | GIVEN recording is active WHEN user types into a field with `autocomplete` attribute containing "password" THEN the field is treated as a password field AND value is `[PASSWORD_FIELD]` | Unit |
| AC-054E-02c | GIVEN a CSS selector whitelist includes a password field selector WHEN the engine processes the whitelist THEN the password field is still excluded (whitelist cannot override password protection) | Unit |

### AC-054E-03: Opt-In Reveal via Whitelist

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054E-03a | GIVEN a per-session CSS selector whitelist is configured WHEN user types into a field matching a whitelisted selector THEN the actual typed value is captured instead of `[MASKED]` | Unit |
| AC-054E-03b | GIVEN the toolbox UI is open WHEN user adds a CSS selector to the whitelist THEN subsequent typing events for matching fields capture actual values | UI |
| AC-054E-03c | GIVEN a whitelist is configured WHEN the session ends THEN the whitelist is stored with the session configuration in the output file | Unit |

### AC-054E-04: Capture-Time Application

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054E-04a | GIVEN masking is active WHEN a typing event is processed THEN masking is applied before the event enters the recording buffer (not as post-processing) | Unit |
| AC-054E-04b | GIVEN masking is active WHEN examining the event buffer at any point THEN no unmasked PII exists for non-whitelisted fields | Unit |

### AC-054E-05: Status Badge

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-054E-05a | GIVEN PII masking is active (default) WHEN the toolbox displays status THEN a PII masking badge is visible indicating masking is on | UI |
| AC-054E-05b | GIVEN CSS selector whitelist has entries WHEN the toolbox displays status THEN the badge indicates partial reveal mode with count of whitelisted selectors | UI |

## Functional Requirements

- **FR-1:** All typed content in input fields shall be masked as `[MASKED]` by default.
- **FR-2:** Password fields (`type="password"` or `autocomplete` containing "password") shall capture `[PASSWORD_FIELD]` as value — never the actual content.
- **FR-3:** Element metadata (selectors, a11y tags, classes, field type) shall always be captured regardless of masking.
- **FR-4:** Per-session CSS selector whitelist shall allow opt-in value capture for non-sensitive fields.
- **FR-5:** Whitelist shall never override password field protection.
- **FR-6:** Masking shall be applied at capture time before events enter buffer.
- **FR-7:** PII masking status shall be exposed for toolbox badge consumption.

## Non-Functional Requirements

- **NFR-1:** Masking check shall add less than 1ms overhead per typing event.
- **NFR-2:** Whitelist matching shall use efficient CSS selector matching (no regex for MVP).

## UI/UX Requirements

_PII badge UI is owned by FEATURE-054-D (Toolbox). This feature exposes the masking status API._

## Dependencies

| Type | Dependency | Impact |
|------|-----------|--------|
| Internal | FEATURE-054-C (Recording Engine) | PII layer intercepts typing events before buffer |
| Consumed by | FEATURE-054-D (Toolbox) | Toolbox shows PII badge + whitelist UI |
| Consumed by | FEATURE-054-F (Output) | Whitelist stored in output session config |

## Business Rules

- **BR-1:** PII masking is ON by default — no opt-out for masking itself, only opt-in for specific field reveals.
- **BR-2:** Password field protection cannot be overridden by any mechanism.
- **BR-3:** Element metadata is never considered PII — always captured in full.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Field changes type dynamically (JS changes `type` attribute) | Re-evaluate on each typing event; if changed to "password", apply password protection |
| Contenteditable div (no `type` attribute) | Apply default masking; not detected as password field |
| Whitelist selector matches multiple fields | All matching fields are revealed |
| Invalid CSS selector in whitelist | Skip invalid selector; log warning; continue with valid selectors |
| Field with `autocomplete="new-password"` | Treated as password field — value is `[PASSWORD_FIELD]` |

## Out of Scope

- Network request body PII scanning
- Image/screenshot PII redaction
- PII detection in non-input elements (e.g., displayed text)
- Regulatory compliance certification (GDPR, CCPA) — masking is a best-effort privacy measure

## Technical Considerations

- Masking hook integrates between event capture and buffer insertion in FEATURE-054-C pipeline
- Password detection should check both `type` attribute and `autocomplete` attribute (including `new-password`, `current-password`)
- Whitelist stored as array of CSS selectors in session config object
- Use `element.matches(selector)` for whitelist matching — efficient native browser API
- Masking status exposed via a simple API: `{ active: true, whitelistCount: N }`

## Open Questions

None — all specification questions resolved via DAO-107.
