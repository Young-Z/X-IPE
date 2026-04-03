# DAO Decisions: Change Request

> Semantic log of human representative interactions grouped by task type.
> Each entry records a DAO interaction with full context and rationale.

| Entry | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|-------|-----------|---------|---------------|-------------|------------|---------|
| DAO-109 | 2026-04-03T00:30:00Z | TASK-1055 | x-ipe-task-based-change-request | answer + approval | 0.88 | CR challenge questions answered; MODIFICATION classification confirmed for EPIC-054 behavior tracker redesign |

---

<!-- Detail sections are appended below this line -->

## DAO-109
- **Timestamp:** 2026-04-03T00:30:00Z
- **Task ID:** TASK-1055
- **Feature ID:** FEATURE-054-B, C, D, E, F
- **Workflow:** N/A (free-mode)
- **Calling Skill:** x-ipe-task-based-change-request
- **Source:** ai
- **Disposition:** Unit 0: answer | Unit 1: approval
- **Confidence:** 0.88

### Message
> **Unit 1 — CR Challenge Questions (Q1–Q5):**
> Q1: Is this change truly necessary? The existing 573-line IIFE is overengineered for a training data collector.
> Q2: Should existing ACs (glass-morphism, PII badge, virtual scrolling) be treated as immovable or accept user wants simpler approach?
> Q3: Polling by track_behavior.py — Python uses Chrome DevTools MCP evaluate_script every 5s to collect events. JS just captures into buffer. Correct?
> Q4: Screenshots — skill script via Chrome DevTools MCP take_screenshot, or IIFE itself?
> Q5: Analysis button — (a) signal skill script for LLM post-processing, or (b) IIFE triggers LLM?
>
> **Unit 2 — Classification Confirmation:**
> Classification: MODIFICATION. Affected: FEATURE-054-B through F. Many ACs retired, new ACs added. Large-scope across 5 features.

### Guidance Returned

> **Unit 0 — CR Challenge Answers:**
>
> **Q1 — YES, this change is necessary.** The original 573-line IIFE with Shadow DOM, glass-morphism, and virtual scrolling was built to spec — but the spec optimized for end-user experience when the actual consumer is a developer/trainer collecting AI training data. A 23KB IIFE is overengineered for a tool whose job is: capture DOM events → buffer → hand to Python. The complexity hinders maintainability and obscures the core mission. Simplification to <5KB is not cutting corners; it is right-sizing the tool to its actual use case.
>
> **Q2 — Existing ACs are NOT immovable.** The user is explicitly requesting to retire glass-morphism, PII badge, virtual scrolling, and other UX-heavy ACs. ACs serve the user's intent — when that intent evolves, ACs evolve with it. The impact study correctly flags that <5KB "breaks critical ACs," but breaking *retired* ACs is the intended outcome, not a risk. The CR process exists precisely for this: the user's understanding of what they need has matured, and the spec must follow.
>
> **Q3 — Correct interpretation.** The architecture is: (1) Lightweight JS event listeners capture DOM events into a buffer array (e.g., `window.__xipe_event_buffer`). (2) Python skill script (`track_behavior.py`) polls every 5 seconds via Chrome DevTools MCP `evaluate_script`, harvesting the buffer and clearing it. (3) JS is passive (capture only), Python is active (poll + store + decide). This inverts the original IIFE-controls-everything model to a script-controls-page model — which is the correct architecture when the controlling agent already has Chrome DevTools MCP access.
>
> **Q4 — Skill script via Chrome DevTools MCP `take_screenshot`.** The JS IIFE should NOT take screenshots — it has no access to MCP tools and adding screenshot capability to browser JS would require complex workarounds. The Python skill script detects changes in the tracking list (via polling diff) and triggers `take_screenshot` through Chrome DevTools MCP. This keeps the IIFE thin and leverages the agent's existing tooling.
>
> **Q5 — Option (A): Signal the skill script.** When the user clicks "Analysis," the IIFE sets a flag (e.g., `window.__xipe_analysis_requested = true`). The Python polling loop detects this flag on the next cycle and triggers LLM post-processing. The IIFE has no backend access and should not invoke LLM directly. This maintains the "pure script control" principle: all intelligence lives in Python, JS is a passive capture + UI layer.
>
> **Unit 1 — Classification CONFIRMED: MODIFICATION.**
>
> The classification is correct:
> - **MODIFICATION, not NEW:** The behavior tracking capability (EPIC-054) already exists. This changes HOW it works, not WHAT it does.
> - **MODIFICATION, not BUG FIX:** The current implementation works as designed — the design itself is being reconsidered.
> - **Scope is correct:** 5 features affected (B: injection, C: recording engine, D: toolbox UI, E: PII masking, F: output/post-processing).
> - **AC retirement is valid:** Glass-morphism, virtual scrolling, PII badge, Shadow DOM complexity — all are explicitly retired by user intent.
> - **New ACs are well-defined:** <5KB constraint, 5-second polling model, screenshot via MCP, `x-ipe-docs/learning/{name}/track/` folder structure.
> - **Large-scope designation is accurate:** 5 features × (retired ACs + new ACs) = significant spec rewrite.
>
> **Proceed with MODIFICATION classification. Route to feature_refinement for each affected feature (B through F).**

### Rationale
> **Unit 0 (answer):** All five questions had sufficient context to answer directly. The user's architectural intent is clear: invert control from IIFE to Python skill script via Chrome DevTools MCP. Each answer aligns JS-as-passive-capture with Python-as-active-controller. No ambiguity requiring clarification; no flaws requiring critique.
>
> **Unit 1 (approval):** MODIFICATION is the only correct classification — same EPIC, same features, different implementation. The user is not adding new capability (→ not NEW), not fixing broken behavior (→ not BUG FIX), and is explicitly retiring old ACs while defining new ones. The large-scope flag is warranted given 5 features affected.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-change-request"
>     match_strength: "strong"
>     reason: "This is literally the calling skill — CR classification and impact analysis are its core domain"
>     execution_steps:
>       - phase: "3. Impact Analysis"
>         step: "3.2 Update affected feature specifications"
>   - skill_name: "x-ipe-task-based-feature-refinement"
>     match_strength: "strong"
>     reason: "After CR is classified, each affected feature (B–F) needs spec updates with retired/new ACs"
>     execution_steps:
>       - phase: "1. Feature Refinement"
>         step: "1.1 Update specification with CR changes"

### Follow-up
> After CR classification is finalized, the calling skill should proceed to update specifications for FEATURE-054-B through F. Each feature enters feature_refinement with the retired ACs removed and new ACs added. Recommend processing in order: B (injection) → C (recording engine) → D (toolbox UI) → E (PII masking) → F (output/post-processing), as later features depend on earlier architectural decisions.
