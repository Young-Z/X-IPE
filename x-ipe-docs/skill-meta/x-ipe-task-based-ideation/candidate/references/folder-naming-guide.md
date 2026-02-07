# Folder Naming Guide

This reference document describes the logic for renaming draft idea folders.

---

## Draft Folder Pattern

**Pattern:** `Draft Idea - MMDDYYYY HHMMSS`

**Examples:**
- `Draft Idea - 01232026 131611`
- `Draft Idea - 02052026 093045`

---

## Rename Logic

```yaml
rename_rules:
  trigger_condition:
    - Folder name matches "Draft Idea - MMDDYYYY HHMMSS" pattern
    - Idea has been refined and has clear identity
    
  new_name_format: "{Idea Name} - {timestamp}"
  
  naming_guidelines:
    max_length: 50
    allowed_chars: "alphanumeric, spaces, hyphens"
    avoid: "special characters, slashes, quotes"
    
  preserve: "Original timestamp from folder name"
```

---

## Naming Guidelines

| Guideline | Rule | Example |
|-----------|------|---------|
| Be Descriptive | Use clear, meaningful name | "E-Commerce Checkout" not "Project A" |
| Keep Concise | Max 50 characters | "Mobile App Dashboard" |
| Use Title Case | Capitalize first letter of each word | "Knowledge Base System" |
| Preserve Timestamp | Keep original creation timestamp | "Mobile App - 01232026 131611" |

---

## Rename Process

```
1. Check if folder name matches draft pattern
   Pattern: /^Draft Idea - \d{8} \d{6}$/
   
2. If match AND idea has clear name:
   a. Extract timestamp from original name
   b. Generate new name from idea summary
   c. Rename folder: x-ipe-docs/ideas/{new-name}/
   d. Update any internal references
   
3. If no match OR idea unclear:
   a. Skip rename
   b. Set folder_renamed: false
```

---

## Examples

| Before | After | Reason |
|--------|-------|--------|
| `Draft Idea - 01232026 131611` | `E-Commerce Checkout - 01232026 131611` | Idea refined to checkout system |
| `Draft Idea - 02052026 093045` | `Mobile Dashboard - 02052026 093045` | Idea refined to mobile dashboard |
| `My Cool App` | `My Cool App` | Already named, no change |
| `Draft Idea - 01152026 140000` | `Draft Idea - 01152026 140000` | Idea not yet clear, skip rename |
