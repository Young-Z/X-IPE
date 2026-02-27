# Feature Specification: Conditional Block Parsing & Error Handling

> Feature ID: FEATURE-042-B
> Version: v1.0
> Status: Refined
> Last Updated: 02-27-2026
> Dependencies: FEATURE-042-A

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-27-2026 | Initial specification |

---

## Linked Mockups

N/A — This feature extends existing Action Execution Modal behavior; no new UI components are introduced.

---

## Overview

### What
Implement a conditional block parser for `<literal text $variable$>` syntax in workflow-prompt templates, add unresolved-variable warning indicators, and ensure legacy placeholder backward compatibility in free-mode prompts. The parser evaluates `<>` blocks at template resolution time: if any `$variable$` inside the block resolves to N/A or empty, the entire block (including literal text) is skipped; if all variables resolve, the `<>` delimiters are stripped and the content is included. After skipping, whitespace artifacts are collapsed.

### Why
Workflow prompts often contain optional context references (e.g., UIUX references, architecture docs) that may not exist for every action invocation. Without conditional blocks, the resolved prompt would contain meaningless literal text adjacent to unresolved placeholders. The `<>` syntax allows prompt authors to wrap optional sections so that the final prompt sent to the agent is clean, contextually accurate, and free of artifacts.

### Who
- **Prompt authors** (skill developers) who define `workflow-prompts` entries in `copilot-prompt.json`
- **End users** who see the resolved instructions preview in the Action Execution Modal
- **AI agents** that receive the final composed command — clean prompts yield better agent output

---

## User Stories

### US-042-B.1: Conditional Block — Variable Resolves
**As a** user executing a workflow action with all prior deliverables available,
**I want** the conditional block text (e.g., "and uiux reference: /path/to/file") to appear in the resolved instructions,
**So that** the agent receives the full context it needs.

### US-042-B.2: Conditional Block — Variable N/A
**As a** user executing a workflow action where an optional deliverable does not exist,
**I want** the entire conditional block to be silently removed from the resolved instructions,
**So that** the agent does not receive confusing partial text or N/A values.

### US-042-B.3: Unresolved Variable Warning
**As a** user viewing the instructions preview,
**I want** unresolved `$output:tag$` placeholders to remain visible with a warning indicator,
**So that** I can identify which deliverables are missing before sending the command.

### US-042-B.4: Legacy Placeholder Compatibility
**As a** user in free mode,
**I want** existing prompts using `<input-file>` and `<current-idea-file>` to continue working,
**So that** the new conditional block parser does not break backward compatibility.

### US-042-B.5: Clean Whitespace After Skip
**As a** user viewing the instructions preview after a `<>` block is skipped,
**I want** no double-spaces or whitespace artifacts in the output,
**So that** the resolved text reads naturally.

---

## Acceptance Criteria

### AC-042-B.1: Conditional Block Skipped When Variable N/A
**Given** a template containing `<and uiux reference: $output:uiux-reference$>`
**When** the `uiux-reference` deliverable does not exist (resolves to N/A)
**Then** the entire block (including "and uiux reference:") is removed from the resolved output

### AC-042-B.2: Conditional Block Included When Variable Resolves
**Given** a template containing `<and uiux reference: $output:uiux-reference$>`
**When** the `uiux-reference` deliverable resolves to `x-ipe-docs/ideas/.../uiux-ref.md`
**Then** the output contains `and uiux reference: x-ipe-docs/ideas/.../uiux-ref.md` (delimiters stripped)

### AC-042-B.3: Multiple Variables in One Block — Any N/A Skips Block
**Given** a template containing `<context: $output:idea$ and $output:architecture$>`
**When** `idea` resolves but `architecture` is N/A
**Then** the entire block is skipped

### AC-042-B.4: Multiple Variables in One Block — All Resolve
**Given** a template containing `<context: $output:idea$ and $output:architecture$>`
**When** both `idea` and `architecture` resolve to paths
**Then** the output contains `context: /path/idea and /path/architecture` (delimiters stripped)

### AC-042-B.5: No Whitespace Artifacts After Skip
**Given** a template `Please review $output:idea$ <and uiux reference: $output:uiux-reference$> carefully`
**When** the `<>` block is skipped
**Then** the output is `Please review /path/idea carefully` with exactly one space between words

### AC-042-B.6: Unresolved Variable Shows Warning
**Given** a template containing `$output:missing-tag$` outside any `<>` block
**When** the deliverable does not exist
**Then** the preview shows the raw text `$output:missing-tag$` with a visual warning indicator (e.g., warning CSS class)

### AC-042-B.7: Legacy Placeholders in Free Mode
**Given** a free-mode prompt containing `<input-file>` or `<current-idea-file>`
**When** the modal renders in free mode
**Then** the placeholders are resolved as before (not treated as conditional blocks)

### AC-042-B.8: No Double-Spaces After Consecutive Skipped Blocks
**Given** a template `Read $output:idea$ <optional A: $output:a$> <optional B: $output:b$> then proceed`
**When** both `<>` blocks are skipped
**Then** the output is `Read /path/idea then proceed` with single spaces only

### AC-042-B.9: Performance — Resolution Under 50ms
**Given** a template with multiple `<>` blocks and `$output:tag$` variables
**When** template resolution executes
**Then** the total time for placeholder substitution + conditional parsing + whitespace cleanup completes in < 50ms

---

## Functional Requirements

### FR-042.12: Unresolved Variable Warning Display

| Aspect | Detail |
|--------|--------|
| **Input** | A resolved template string where one or more `$output:tag$` or `$output-folder:tag$` variables could not be resolved (no matching deliverable) |
| **Process** | 1. After variable substitution, scan the output for any remaining `$output:...$` or `$output-folder:...$` tokens. 2. For each unresolved token, wrap it in a warning indicator element (e.g., `<span class="unresolved-var">$output:tag$</span>`). 3. The warning indicator MUST be visually distinct (e.g., orange/yellow background or border) so the user notices missing context. |
| **Output** | The instructions preview displays raw placeholder text with warning styling for each unresolved variable |

### FR-042.13: `$output:` Prefix Convention

| Aspect | Detail |
|--------|--------|
| **Input** | Prompt template strings in `workflow-prompts` entries |
| **Process** | All `action_context` ref names (e.g., `raw-idea`, `uiux-reference`, `architecture`) MUST use the `$output:` prefix in templates (e.g., `$output:raw-idea$`). There is NO separate syntax for non-deliverable context refs. The parser treats every `$output:name$` token identically — resolving by looking up the `action_context` ref with matching name and reading the dropdown's selected value. |
| **Output** | Consistent, single syntax for all template variables referencing action context |

### FR-042.14: Legacy Placeholder Backward Compatibility

| Aspect | Detail |
|--------|--------|
| **Input** | Free-mode prompts that use `<input-file>`, `<current-idea-file>`, or `<feature-id>` placeholders |
| **Process** | 1. The conditional block parser MUST only activate in **workflow mode**. 2. In **free mode**, `<` and `>` characters are treated as literal angle brackets (legacy placeholder delimiters), not conditional block markers. 3. Legacy placeholders (`<input-file>`, `<current-idea-file>`, `<feature-id>`) continue to be resolved by the existing legacy resolver before any new parsing logic runs. |
| **Output** | Free-mode prompts behave identically to pre-FEATURE-042 behavior; no regression |

### FR-042.15: Conditional Block Syntax — `<literal text $variable$>`

| Aspect | Detail |
|--------|--------|
| **Input** | A prompt template string containing zero or more `<...>` blocks, where content between `<` and `>` is a mix of literal text and `$variable$` references |
| **Process** | 1. Parse the template to identify all `<...>` blocks using flat delimiter matching. 2. For each block, extract the content between `<` and `>`. 3. Identify all `$...$` variable references within the block content. 4. Evaluate each variable against the resolved context map. |
| **Output** | A list of parsed conditional blocks, each with its literal text, variable references, and their resolution status |

### FR-042.16: Skip Block When Any Variable Is N/A

| Aspect | Detail |
|--------|--------|
| **Input** | A parsed `<>` block containing one or more `$variable$` references |
| **Process** | 1. For each `$variable$` in the block, check if it resolved to a real value. 2. If ANY variable resolved to N/A, empty string, `undefined`, or `null` → mark the entire block for removal. 3. Remove the block (including `<` and `>` delimiters and all enclosed content) from the output. |
| **Output** | The block is entirely absent from the resolved template output |

### FR-042.17: Strip Delimiters When All Variables Resolve

| Aspect | Detail |
|--------|--------|
| **Input** | A parsed `<>` block where ALL `$variable$` references resolved to real values |
| **Process** | 1. Verify every `$variable$` in the block has a non-empty, non-N/A value. 2. Replace each `$variable$` with its resolved value. 3. Remove the `<` and `>` delimiters, keeping the inner content (literal text + resolved values). |
| **Output** | The block content appears in the output without `<>` delimiters, with all variables replaced by their values |

### FR-042.18: Flat Parsing — No Nesting

| Aspect | Detail |
|--------|--------|
| **Input** | A template string that may contain `<` and `>` characters |
| **Process** | 1. The parser MUST use flat (non-recursive) delimiter matching: the first `<` pairs with the first `>` encountered after it. 2. Nested `<>` blocks are NOT supported and MUST NOT be parsed recursively. 3. If a `<` is found inside an already-opened `<>` block, it is treated as literal text within the outer block. |
| **Output** | A flat list of `<>` blocks, each spanning from one `<` to its nearest subsequent `>` |

### FR-042.19: Whitespace Cleanup After Block Removal

| Aspect | Detail |
|--------|--------|
| **Input** | The template string after all `<>` blocks have been evaluated (skipped or stripped) |
| **Process** | 1. Replace all occurrences of two or more consecutive whitespace characters (`\s{2,}`) with a single space. 2. Trim leading and trailing whitespace from the final output. 3. This cleanup applies to the entire resolved string, not just areas adjacent to removed blocks. |
| **Output** | A clean string with no double-spaces, no leading/trailing whitespace, and no artifacts from skipped blocks |

---

## Non-Functional Requirements

### NFR-042.1: Template Resolution Performance
Template resolution (placeholder substitution + conditional block parsing + whitespace cleanup) MUST complete in < 50ms for any prompt template, regardless of the number of `<>` blocks or `$variable$` references.

### NFR-042.2: Frontend-Only Parsing
The `<>` conditional block parser MUST execute entirely in the frontend (JavaScript). No backend API calls are made during template resolution. All data required for resolution (variable values from dropdowns) is already available in the modal's local state.

---

## UI/UX Requirements

### UIX-042-B.1: Unresolved Variable Indicator
- Unresolved `$output:tag$` tokens in the instructions preview MUST be visually distinct from normal text
- Use a warning style (e.g., `background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 3px; padding: 0 4px;`) or equivalent that is consistent with the application's existing warning patterns
- The raw placeholder text (e.g., `$output:missing-ref$`) MUST remain readable inside the warning indicator

### UIX-042-B.2: Seamless Block Removal
- When a `<>` block is skipped, there MUST be no visible artifacts (extra spaces, orphaned punctuation) in the preview
- The resolved text MUST read as a natural sentence/paragraph

### UIX-042-B.3: Real-Time Preview Updates
- Conditional block evaluation MUST update in real-time as the user changes dropdown selections (integrated with FEATURE-042-C's live preview)
- There MUST be no perceptible delay (< 50ms per NFR-042.1)

---

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-042-A | Hard (must exist) | Provides the `workflow-prompts` array structure, `$output:tag$` / `$output-folder:tag$` / `$feature-id$` variable resolution, and the template resolver function in `action-execution-modal.js` that this feature extends |
| FEATURE-042-C | Soft (integrates with) | The read-only instructions preview and live dropdown updates consume the output of conditional block parsing; FEATURE-042-B provides the parsing logic, FEATURE-042-C provides the UI binding |

---

## Business Rules

### BR-042-B.1: Block Evaluation Is All-or-Nothing
A `<>` block is either fully included (all variables resolve) or fully removed (any variable is N/A). There is no partial inclusion — even if 3 out of 4 variables resolve, the block is skipped.

### BR-042-B.2: Variables Outside Blocks Are Always Resolved
`$output:tag$` references that appear outside any `<>` block are resolved normally. If they cannot be resolved, they remain as raw placeholder text with a warning indicator (FR-042.12). They are NOT removed.

### BR-042-B.3: Free Mode Is Exempt
The conditional block parser does NOT run in free mode. In free mode, `<` and `>` are treated as literal characters for legacy placeholder resolution (e.g., `<input-file>`).

### BR-042-B.4: Empty Resolution Equals N/A
For the purpose of block evaluation, a variable that resolves to an empty string (`""`), `null`, `undefined`, or the literal string `"N/A"` is treated as unresolved (N/A).

---

## Edge Cases & Constraints

### EC-042-B.1: Multiple `<>` Blocks in One Template
**Scenario:** Template contains `Read $output:idea$ <and ref: $output:ref-a$> <and doc: $output:ref-b$> then act`
**Expected:** Each `<>` block is evaluated independently. If `ref-a` resolves but `ref-b` is N/A, output is `Read /path/idea and ref: /path/ref-a then act`.

### EC-042-B.2: `<>` Block With All Variables Resolved
**Scenario:** `<context: $output:idea$ and $output:arch$>` where both resolve
**Expected:** Output is `context: /path/idea and /path/arch` (delimiters stripped, content included)

### EC-042-B.3: `<>` Block With Some Variables N/A
**Scenario:** `<context: $output:idea$ and $output:arch$>` where `arch` is N/A
**Expected:** Entire block removed from output

### EC-042-B.4: Empty `<>` Block
**Scenario:** Template contains `<>` (empty block, no content)
**Expected:** The empty block is removed. It contains no variables, so technically "all zero variables resolve" — but there is no content to include, so the block produces no output and the delimiters are stripped.

### EC-042-B.5: `<>` Block With Only Literal Text (No Variables)
**Scenario:** `<this is just literal text>` with no `$variable$` references
**Expected:** Since there are no variables, all zero variables trivially resolve. The delimiters are stripped and the literal text is included: `this is just literal text`.

### EC-042-B.6: Malformed `<>` — Missing Closing `>`
**Scenario:** Template contains `<and ref: $output:ref$` without a closing `>`
**Expected:** The parser finds no matching `>` for the `<`. The `<` is treated as a literal character. The text remains as-is (including the `<` character). The `$output:ref$` variable is resolved normally as if it were outside a block.

### EC-042-B.7: Malformed `<>` — Missing Opening `<`
**Scenario:** Template contains `and ref: $output:ref$>` without an opening `<`
**Expected:** The `>` is treated as a literal character. No conditional block is formed. Variables are resolved normally.

### EC-042-B.8: Consecutive `<>` Blocks With No Space Between
**Scenario:** `$output:idea$<A: $output:a$><B: $output:b$>end`
**Expected:** Each block evaluated independently. If both skip: `$output:idea$ end` → after whitespace cleanup: `/path/idea end`. If both resolve: `/path/idea A: /val-a B: /val-b end`.

### EC-042-B.9: Whitespace Around `<>` Blocks
**Scenario:** `text  <block: $output:x$>  more` (extra spaces around block)
**Expected:** If block skipped: `text more` (whitespace collapsed). If block resolves: `text block: /val more` (whitespace collapsed).

### EC-042-B.10: `<>` Block at Start or End of Template
**Scenario:** `<optional: $output:x$> main content` or `main content <optional: $output:x$>`
**Expected:** If skipped, leading/trailing whitespace is trimmed. Output is `main content` in both cases.

### EC-042-B.11: Legacy Placeholder Inside `<>` in Free Mode
**Scenario:** Free-mode prompt with `<input-file>` — this looks like a `<>` block
**Expected:** In free mode, conditional block parser is NOT active. `<input-file>` is handled by the legacy resolver as before.

### EC-042-B.12: `$feature-id$` Inside a `<>` Block
**Scenario:** `<for feature $feature-id$>` where feature ID is available from modal context
**Expected:** `$feature-id$` resolves to the current feature ID. Delimiters stripped, output: `for feature FEATURE-042-B`.

### EC-042-B.13: Nested `<>` Attempt
**Scenario:** `<outer <inner $output:x$> text>` — user accidentally nests blocks
**Expected:** Flat parsing pairs first `<` with first `>`: block is `outer <inner $output:x$`. The remaining ` text>` has a stray `>` treated as literal. The inner `<` inside the block is literal text.

### Constraints Summary
- `<>` blocks are flat — no nesting supported
- Template parser is frontend-only — no backend calls
- Legacy placeholders (`<input-file>`, `<current-idea-file>`, `<feature-id>`) MUST continue to work in free-mode prompts
- The conditional block parser MUST only activate in workflow mode

---

## Out of Scope

- **Nested `<>` blocks** — explicitly not supported; flat parsing only (FR-042.18)
- **Backend template resolution** — all parsing is frontend-only (NFR-042.2)
- **New UI components** — this feature extends existing modal behavior, no new screens
- **Dropdown defaulting logic** — handled by FEATURE-042-C
- **Read-only preview binding** — handled by FEATURE-042-C (this feature provides the parsing function)
- **Migration of prompts** — handled by FEATURE-042-D
- **`workflow-prompts` array structure** — defined in FEATURE-042-A
- **Custom conditional logic** (e.g., if-else, OR conditions) — only all-or-nothing skip is supported

---

## Technical Considerations

> **Note:** This section describes WHAT the system must do, not HOW it should be implemented.

### TC-042-B.1: Parser Input/Output Contract
The conditional block parser receives a template string (with `$variable$` references already resolved or marked N/A by FEATURE-042-A's resolver) and returns a clean string with all `<>` blocks evaluated and whitespace normalized.

### TC-042-B.2: Resolution Pipeline Order
The template resolution pipeline MUST follow this order:
1. **Variable substitution** (FEATURE-042-A) — replace `$output:tag$`, `$output-folder:tag$`, `$feature-id$` with values or mark as N/A
2. **Conditional block evaluation** (this feature) — evaluate `<>` blocks based on variable resolution status
3. **Unresolved variable detection** (this feature) — scan for remaining `$...$` tokens and apply warning indicators
4. **Whitespace cleanup** (this feature) — collapse double-spaces, trim edges

### TC-042-B.3: Mode Detection
The system MUST determine whether to activate conditional block parsing based on the current execution mode (workflow vs. free). The mode is already available in the modal context from existing infrastructure.

### TC-042-B.4: Whitespace Normalization Pattern
After all block evaluation, consecutive whitespace characters (spaces, tabs, newlines that result from block removal) MUST be collapsed to a single space, and the final string MUST be trimmed of leading/trailing whitespace.

### TC-042-B.5: Key Files
- `src/frontend/js/action-execution-modal.js` — Template resolver (from FEATURE-042-A) extended with conditional block parsing, unresolved variable warning, and whitespace cleanup
- `src/frontend/js/copilot-prompt.json` — Prompt templates that use `<>` block syntax

---

## Open Questions

None — all clarifications were resolved during ideation and requirement gathering (see requirement-details-part-14.md Clarifications table).
