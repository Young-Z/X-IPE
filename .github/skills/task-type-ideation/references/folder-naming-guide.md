# Folder Naming Guide

This reference document contains the detailed procedure for renaming Draft Idea folders.

---

## When to Rename

- Folder name matches pattern: `Draft Idea - MMDDYYYY HHMMSS`
- Idea has been refined and has a clear identity

---

## Naming Logic

```
1. Check if folder name starts with "Draft Idea - "
2. If YES:
   a. Extract timestamp suffix (MMDDYYYY HHMMSS)
   b. Generate idea name from:
      - Core concept identified in brainstorming
      - Main theme from idea summary
      - Keep it concise (2-5 words)
   c. Format new name: "{Idea Name} - {timestamp}"
   d. Rename folder using filesystem/API
   e. Update any internal references if needed
3. If NO (already has custom name):
   a. Skip renaming
   b. Log: "Folder already has custom name"
```

---

## Naming Guidelines

- Use Title Case for idea name
- Keep name concise but descriptive (2-5 words)
- Avoid special characters (use only alphanumeric, spaces, hyphens)
- Preserve the original timestamp suffix

---

## Examples

| Original Folder | Idea Content | New Folder Name |
|-----------------|--------------|-----------------|
| `Draft Idea - 01232026 143500` | Mobile app for task management | `Task Manager App - 01232026 143500` |
| `Draft Idea - 01222026 091200` | AI-powered code review tool | `AI Code Reviewer - 01222026 091200` |
| `Draft Idea - 01212026 160000` | E-commerce checkout optimization | `Checkout Optimizer - 01212026 160000` |

---

## Output

Folder renamed (or skipped if already named)
