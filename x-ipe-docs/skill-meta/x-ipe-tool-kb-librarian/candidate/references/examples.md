# KB AI Librarian — Examples

## Example 1: Batch Processing Markdown Files

**Trigger:** User clicks "✨ Run AI Librarian" in KB Browse Modal

**Scenario:** Three markdown files dropped in `.intake/`:
- `api-auth-guide.md` — A guide about API authentication patterns
- `deploy-checklist.md` — A deployment checklist for production releases
- `react-hooks-notes.md` — Notes on React hooks best practices

**Execution:**

```
Agent: Loading KB config... tag taxonomy: 7 lifecycle, 10 domain tags
Agent: Found 3 pending files in .intake/

Processing api-auth-guide.md...
  → Status: pending → processing
  → Content analysis: API authentication, JWT, OAuth patterns
  → Destination: docs/guides/ (best match for guide-style content)
  → Tags: lifecycle=[Implementation], domain=[API, Authentication, Security]
  → Frontmatter generated: title="API Authentication Guide", auto_generated=true
  → Moved to docs/guides/api-auth-guide.md
  → Status: processing → filed

Processing deploy-checklist.md...
  → Status: pending → processing
  → Content analysis: deployment steps, CI/CD, production checklist
  → Destination: docs/operations/ (best match for operational content)
  → Tags: lifecycle=[Deployment], domain=[Infrastructure]
  → Frontmatter generated: title="Deployment Checklist", auto_generated=true
  → Moved to docs/operations/deploy-checklist.md
  → Status: processing → filed

Processing react-hooks-notes.md...
  → Status: pending → processing
  → Content analysis: React hooks, useState, useEffect, frontend patterns
  → Destination: docs/references/ (best match for reference notes)
  → Tags: lifecycle=[Implementation], domain=[UI-UX]
  → Frontmatter generated: title="React Hooks Notes", auto_generated=true
  → Moved to docs/references/react-hooks-notes.md
  → Status: processing → filed

Summary: 3 files processed → docs/guides/ (1), docs/operations/ (1), docs/references/ (1)
```

---

## Example 2: Mixed File Types with Pre-assigned Destinations

**Scenario:** Two files in `.intake/`, one with a UI-assigned destination:
- `architecture-diagram.png` — destination pre-assigned to `docs/architecture/` via UI
- `security-policy.md` — no destination assigned

**Execution:**

```
Agent: Found 2 pending files in .intake/

Processing architecture-diagram.png...
  → Status: pending → processing
  → Pre-assigned destination: docs/architecture/ (using UI assignment)
  → Non-markdown file: skipping frontmatter generation
  → Moved to docs/architecture/architecture-diagram.png
  → Status: processing → filed

Processing security-policy.md...
  → Status: pending → processing
  → No pre-assigned destination → AI analysis
  → Content analysis: security policies, access control, compliance
  → Destination: docs/policies/ (best match)
  → Tags: lifecycle=[Maintenance], domain=[Security]
  → Frontmatter generated: title="Security Policy", auto_generated=true
  → Moved to docs/policies/security-policy.md
  → Status: processing → filed

Summary: 2 files processed → docs/architecture/ (1), docs/policies/ (1)
```

---

## Example 3: No Pending Files

**Scenario:** All files in `.intake/` already have status "filed".

**Execution:**

```
Agent: Loading KB config...
Agent: No pending files to process.
```

---

## Example 4: Existing Frontmatter Preservation

**Scenario:** A markdown file with existing frontmatter:

```yaml
---
title: My Custom Title
author: jane.doe
---
# Content here...
```

**After processing:**

```yaml
---
title: My Custom Title        # preserved (not overwritten)
author: jane.doe               # preserved (not overwritten)
tags:                          # added (was missing)
  lifecycle:
    - Implementation
  domain:
    - Documentation
created: "2026-03-16"         # added (was missing)
auto_generated: true           # added (was missing)
---
# Content here...
```

Only missing fields are filled in. Existing values are never changed.
