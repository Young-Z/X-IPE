# Technical Design: Conditional Block Parsing & Error Handling

> Feature ID: FEATURE-042-B | Epic ID: EPIC-042 | Version: v1.0 | Last Updated: 02-27-2026

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating large projects.
> **📌 AI Coders:** Focus on this section for implementation context.

### Key Components Implemented

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| `ActionExecutionModal._resolveConditionalBlocks(template, resolvedValues)` | Parse `<>` blocks, skip when any `$var$` is N/A, strip delimiters when all resolve | Frontend JS — template post-processing | #modal #conditional-blocks #parser #frontend |
| `ActionExecutionModal._formatUnresolvedWarning(tagName)` | Wrap remaining unresolved `$output:tag$` tokens in warning-styled `<span>` | Frontend JS — unresolved variable display | #modal #unresolved-warning #frontend |
| CSS `.unresolved-warning` class | Visual indicator (yellow/orange background) for unresolved variables in preview | Frontend CSS — warning styling | #css #warning #frontend |

### Dependencies

| Dependency | Source | Design Link | Usage Description |
|------------|--------|-------------|-------------------|
| `ActionExecutionModal._resolveTemplate()` | FEATURE-042-A | (same epic) | Basic `$output:tag$` / `$output-folder:tag$` / `$feature-id$` resolution — runs BEFORE conditional block parsing |
| `ActionExecutionModal` | FEATURE-041-F | [technical-design.md](x-ipe-docs/requirements/EPIC-041/FEATURE-041-F/technical-design.md) | Base modal class with action context dropdowns, mode detection, and context persistence |
| `workflow-template.json` (action_context) | FEATURE-041-E | [technical-design.md](x-ipe-docs/requirements/EPIC-041/FEATURE-041-E/technical-design.md) | Template schema providing context ref definitions |

### Major Flow

1. **FEATURE-042-A's `_resolveTemplate()`** resolves `$output:tag$`, `$output-folder:tag$`, and `$feature-id$` tokens → values come from action context dropdowns
2. **`_resolveConditionalBlocks()`** processes all `<…>` blocks in the resolved string:
   - For each `<…>` block, extract any remaining `$var$` references
   - If **any** `$var$` inside the block resolved to N/A / empty / null / undefined → **skip** (remove entire block)
   - If **all** variables resolved to real values → **strip** `<>` delimiters, keep inner content
3. **Whitespace cleanup** — collapse consecutive whitespace (`\s{2,}` → single space), trim edges
4. **`_formatUnresolvedWarning()`** — scan for any remaining `$output:…$` or `$output-folder:…$` tokens outside blocks, wrap in `<span class="unresolved-warning">` for visual feedback
5. **Mode guard** — steps 2–4 only execute in workflow mode; free-mode prompts skip conditional block parsing entirely, preserving legacy `<input-file>` / `<current-idea-file>` behavior

### Usage Example

```javascript
// Inside _resolveTemplate() — after basic variable substitution (042-A)
// resolvedValues = { 'raw-idea': 'x-ipe-docs/.../raw-idea.md', 'uiux-reference': 'N/A' }

let text = 'Refine $output:raw-idea$ <and uiux reference: $output:uiux-reference$> with ideation skill';

// Step 1 (042-A): basic resolution
// text → 'Refine x-ipe-docs/.../raw-idea.md <and uiux reference: N/A> with ideation skill'

// Step 2 (042-B): conditional blocks
text = this._resolveConditionalBlocks(text, resolvedValues);
// text → 'Refine x-ipe-docs/.../raw-idea.md with ideation skill'
//   (block removed because uiux-reference is N/A, whitespace collapsed)

// Step 3 (042-B): unresolved warning formatting (for preview HTML)
text = this._formatUnresolvedWarnings(text);
// Any remaining $output:missing$ → <span class="unresolved-warning">$output:missing$</span>
```

---

## Part 2: Implementation Guide

> **Purpose:** Human-readable details for developers.

### Workflow Diagram

```mermaid
flowchart TD
    A[Start: template string after 042-A variable resolution] --> B{Workflow mode?}
    B -- No --> Z[Return text as-is — legacy free-mode]
    B -- Yes --> C[Find all &lt;…&gt; blocks via regex]
    C --> D{Any blocks found?}
    D -- No --> G
    D -- Yes --> E[For each block]
    E --> E1[Extract inner content between &lt; and &gt;]
    E1 --> E2[Find all $var$ references in inner content]
    E2 --> E3{Any $var$ resolved to N/A / empty / null / undefined?}
    E3 -- Yes --> E4[Remove entire block including delimiters]
    E3 -- No --> E5[Strip &lt; and &gt; delimiters, keep inner content]
    E4 --> E6{More blocks?}
    E5 --> E6
    E6 -- Yes --> E
    E6 -- No --> G[Collapse whitespace: text.replace /\s{2,}/g, ' ' then trim]
    G --> H[Scan for remaining $output:…$ or $output-folder:…$ tokens]
    H --> I{Any unresolved tokens?}
    I -- No --> J[Return clean text]
    I -- Yes --> K[Wrap each in span.unresolved-warning]
    K --> J
```

### Parser Algorithm

The conditional block parser uses a **single regex pass** with `String.replace()`:

```javascript
_resolveConditionalBlocks(text, resolvedValues) {
    // Regex: match <...> blocks (flat — first < to first >)
    return text.replace(/<([^<>]+)>/g, (match, innerContent) => {
        // Find all $var$ references inside this block
        const varPattern = /\$([^$]+)\$/g;
        let varMatch;
        let hasUnresolved = false;

        while ((varMatch = varPattern.exec(innerContent)) !== null) {
            const varName = varMatch[1];
            // Extract tag name from 'output:tag' or 'output-folder:tag'
            const tagName = varName.includes(':') ? varName.split(':')[1] : varName;
            const value = resolvedValues[tagName];

            if (!value || value === 'N/A' || value === '') {
                hasUnresolved = true;
                break;
            }
        }

        // Skip block if any variable is N/A; otherwise strip delimiters
        return hasUnresolved ? '' : innerContent;
    });
}
```

**Key design decisions:**
- **Regex `/<([^<>]+)>/g`** — flat matching: `[^<>]+` prevents matching across nested `<>`, pairing first `<` with its nearest `>`
- **resolvedValues map** — passed from 042-A's resolver; keys are tag names (e.g., `"raw-idea"`), values are resolved paths or `"N/A"`
- **N/A check** — a variable is considered unresolved if its value is `null`, `undefined`, empty string `""`, or the literal string `"N/A"` (per BR-042-B.4)
- **Return `''`** for skipped blocks — the surrounding whitespace is cleaned up in the next step

### Resolution Pipeline Order

| Step | Responsibility | Feature |
|------|----------------|---------|
| 1. Variable substitution | Replace `$output:tag$`, `$output-folder:tag$`, `$feature-id$` with dropdown values or `"N/A"` | FEATURE-042-A |
| 2. Conditional block evaluation | Process `<…>` blocks — skip or strip | FEATURE-042-B |
| 3. Whitespace cleanup | `text.replace(/\s{2,}/g, ' ').trim()` | FEATURE-042-B |
| 4. Unresolved warning formatting | Wrap remaining `$output:…$` tokens in `.unresolved-warning` spans | FEATURE-042-B |

### Unresolved Variable Display

```javascript
_formatUnresolvedWarnings(text) {
    // Match $output:tag$ and $output-folder:tag$ tokens remaining after resolution
    return text.replace(
        /\$(output(?:-folder)?:[a-zA-Z0-9-]+)\$/g,
        '<span class="unresolved-warning">$$$1$$</span>'
    );
}
```

**CSS class:**

```css
.unresolved-warning {
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 3px;
    padding: 0 4px;
    color: #856404;
    font-family: monospace;
    font-size: 0.9em;
}
```

- Yellow/orange background consistent with the application's existing warning patterns (UIX-042-B.1)
- Raw placeholder text remains readable inside the indicator
- Slightly dimmed text color (`#856404`) to indicate "not yet resolved" without hiding content

### Legacy Compatibility

Free-mode prompts use `<input-file>`, `<current-idea-file>`, and `<feature-id>` — these look syntactically like `<>` blocks but must **not** be parsed as conditional blocks.

**Guard logic:**

```javascript
// In _resolveTemplate() — the orchestrating method
_resolveTemplate(template, contextMap) {
    // Step 1: basic variable substitution (042-A)
    let text = this._substituteVariables(template, contextMap);

    // Step 2–4: conditional blocks + cleanup — ONLY in workflow mode
    if (this.workflowName) {
        text = this._resolveConditionalBlocks(text, contextMap);
        text = text.replace(/\s{2,}/g, ' ').trim();
        text = this._formatUnresolvedWarnings(text);
    }

    return text;
}
```

The `this.workflowName` check (truthy in workflow mode, null/undefined in free mode) gates the entire conditional block pipeline. In free mode, the legacy `_resolveInputFiles()` and `_resolveIdeaFiles()` methods from FEATURE-038-A continue to handle `<input-file>` / `<current-idea-file>` resolution as before.

### Implementation Steps

#### Step 1: Create `_resolveConditionalBlocks()` in `action-execution-modal.js`

Add the method to the `ActionExecutionModal` class. It takes the template string (after 042-A variable resolution) and the resolved-values map, returns a clean string with all `<>` blocks evaluated.

```javascript
// action-execution-modal.js — new method
_resolveConditionalBlocks(text, resolvedValues) {
    return text.replace(/<([^<>]+)>/g, (match, innerContent) => {
        const varPattern = /\$([^$]+)\$/g;
        let varMatch;
        let hasUnresolved = false;

        while ((varMatch = varPattern.exec(innerContent)) !== null) {
            const varName = varMatch[1];
            const tagName = varName.includes(':') ? varName.split(':')[1] : varName;
            const value = resolvedValues[tagName];

            if (value === undefined || value === null || value === '' || value === 'N/A') {
                hasUnresolved = true;
                break;
            }
        }

        return hasUnresolved ? '' : innerContent;
    });
}
```

#### Step 2: Add CSS class `.unresolved-warning`

Add the warning style to the modal's stylesheet (or inline within the modal's CSS block):

```css
.unresolved-warning {
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 3px;
    padding: 0 4px;
    color: #856404;
    font-family: monospace;
    font-size: 0.9em;
}
```

#### Step 3: Modify `_resolveTemplate()` (from 042-A) to call conditional block resolver

After 042-A's basic variable substitution, add the conditional block + whitespace + warning pipeline gated by workflow mode:

```javascript
_resolveTemplate(template, contextMap) {
    let text = this._substituteVariables(template, contextMap);

    if (this.workflowName) {
        text = this._resolveConditionalBlocks(text, contextMap);
        text = text.replace(/\s{2,}/g, ' ').trim();
        text = this._formatUnresolvedWarnings(text);
    }

    return text;
}
```

#### Step 4: Add whitespace normalization post-processing

Already included in Step 3 as `text.replace(/\s{2,}/g, ' ').trim()`. This single line handles:
- Double spaces left by removed blocks
- Leading/trailing whitespace from blocks at string edges
- Consecutive blocks that both get skipped

#### Step 5: Ensure legacy placeholders work in free mode

No code change needed — the `if (this.workflowName)` guard ensures the conditional block parser never runs in free mode. Verify during testing that:
- `<input-file>` resolves correctly in free mode
- `<current-idea-file>` resolves correctly in free mode
- `<feature-id>` resolves correctly in free mode

### Edge Cases & Error Handling

| Scenario | Handling |
|----------|----------|
| Block with all variables resolved | Strip `<>` delimiters, include inner content (AC-042-B.2) |
| Block with any variable N/A | Remove entire block including delimiters (AC-042-B.1) |
| Multiple variables in one block, one N/A | Skip entire block — all-or-nothing (AC-042-B.3, BR-042-B.1) |
| Empty `<>` block | No variables → all zero trivially resolve → delimiters stripped, no content emitted (EC-042-B.4) |
| Block with only literal text (no `$var$`) | All zero variables resolve → delimiters stripped, literal text included (EC-042-B.5) |
| Malformed `<` without closing `>` | Regex `/<([^<>]+)>/g` does not match → `<` treated as literal character (EC-042-B.6) |
| Malformed `>` without opening `<` | Regex does not match → `>` treated as literal character (EC-042-B.7) |
| Consecutive `<>` blocks, both skipped | Both replaced with `''`, whitespace collapsed to single space (AC-042-B.8) |
| Block at start or end of template | After removal, `trim()` cleans leading/trailing whitespace (EC-042-B.10) |
| Nested `<>` attempt: `<outer <inner $x$> text>` | Flat parsing: first `<` pairs with first `>` → block is `outer <inner $x$`, remainder ` text>` has stray `>` as literal (EC-042-B.13) |
| `$feature-id$` inside a `<>` block | Resolved in step 1 (042-A) before block evaluation; block evaluates normally (EC-042-B.12) |
| Legacy `<input-file>` in free mode | Conditional block parser skipped; legacy resolver handles it (AC-042-B.7, EC-042-B.11) |
| Template with no `<>` blocks | Regex finds no matches; text passes through unchanged to whitespace cleanup |
| Performance concern (many blocks) | Single regex pass + single whitespace pass = O(n); well under 50ms for any prompt (NFR-042.1) |

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 02-27-2026 | Initial Design | Technical design for conditional block parsing (`_resolveConditionalBlocks`), unresolved variable warning display (`_formatUnresolvedWarnings`, `.unresolved-warning` CSS), whitespace normalization, and legacy compatibility guard. Extends FEATURE-042-A's `_resolveTemplate()` pipeline. |
