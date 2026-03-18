# DAO Decisions — Feature Refinement

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-081 | 2026-03-18T09:00:00Z | TASK-CR005 | x-ipe-task-based-feature-refinement | answer | 0.90 | Resolved 6 specification gaps for FEATURE-049-F folder support in KB intake (CR-005) |

---

## DAO-081
- **Timestamp:** 2026-03-18T09:00:00Z
- **Task ID:** TASK-CR005
- **Feature ID:** FEATURE-049-F
- **Workflow:** cr-005
- **Calling Skill:** x-ipe-task-based-feature-refinement
- **Source:** ai
- **Disposition:** answer
- **Confidence:** 0.90

### Message
> Agent refining FEATURE-049-F specification identified 6 design questions for CR-005 folder support in KB intake: (1) folder status model — explicit vs derived, (2) folder actions — which apply, (3) filter behavior with mixed-status children, (4) lazy loading UX, (5) AI Librarian folder processing, (6) sidebar badge semantics.

### Guidance Returned
> **Q1 — Folder status: Derived from children.** No explicit folder status in `.intake-status.json`. A folder is "pending" if any child is pending, "filed" if all children are filed. Avoids redundant state and sync issues.
>
> **Q2 — Folder actions:** Preview: No (no content). Assign destination: Yes (bulk-assign all children). Remove: Yes (delete folder + all contents). View in KB: No (YAGNI). Undo: Yes (undo-file all children).
>
> **Q3 — Filter behavior: Show folder if ANY child matches filter.** "Pending" filter shows a folder when at least one child is pending. Hiding the folder would hide reachable pending items.
>
> **Q4 — Lazy loading: Pre-load children in initial API response.** Intake folders are small (extracted ZIPs). No lazy loading complexity needed. Add later only if performance requires it (YAGNI).
>
> **Q5 — AI Librarian: Process individual files separately.** AI Librarian assigns KB destinations per file based on content. Files within a folder may belong to different KB sections. The folder is just ZIP structure, not KB taxonomy.
>
> **Q6 — Sidebar badge: Deep-count individual pending files.** Users care about "how many files need attention." A folder with 10 pending files = 10 items of work, not 1.

### Rationale
> All 6 questions are tightly coupled specification gaps for the same feature. Answered as one unit. Each decision follows KISS/YAGNI: derived status avoids state sync, pre-loading avoids premature optimization, per-file processing matches existing AI Librarian design, deep-count reflects actual user workload. Decisions are reversible if user experience testing reveals issues.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-refinement"
>     match_strength: "strong"
>     reason: "Agent is actively refining FEATURE-049-F specification; answers feed directly into spec document"
>     execution_steps:
>       - phase: "3. IMPLEMENT"
>         step: "3.1 Feature Refinement"

### Follow-up
> None — agent should incorporate these decisions into the FEATURE-049-F specification document and proceed with refinement.

---

| DAO-082 | 2026-03-18T01:17:53Z | TASK-CR005 | N/A (post-refinement routing) | instruction | 0.92 | Proceed to Technical Design for FEATURE-049-F CR-005 folder support |

## DAO-082
- **Timestamp:** 2026-03-18T01:17:53Z
- **Task ID:** TASK-CR005
- **Feature ID:** FEATURE-049-F
- **Workflow:** cr-005
- **Calling Skill:** N/A (post-refinement routing)
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.92

### Message
> Feature Refinement for FEATURE-049-F (CR-005 folder support) is complete (commit 076d22a). Specification v1.5 has 85 ACs covering folder tree display, derived status, folder actions, pre-loaded tree, filter propagation, deep-count badge, and AI Librarian per-file processing. The skill output suggests Technical Design as next step. Should the agent proceed, or is there another action first?

### Guidance Returned
> **Proceed to Technical Design for FEATURE-049-F (CR-005 folder support).** The engineering workflow DAG mandates `feature_refinement → technical_design → code_implementation`. With 85 ACs covering non-trivial architectural concerns — folder tree state management with expand/collapse, derived folder status computed from children, filter propagation through tree hierarchy, folder-specific bulk actions (assign/remove/undo), and deep-count badge computation — a focused design pass is essential before implementation.
>
> **Scoping guidance:** The design should focus on the **delta** — what changes/additions are needed for folder support on top of existing code. Do not redesign the entire feature. Key design areas: (1) tree data model and state management, (2) derived status computation algorithm, (3) filter propagation logic through nested structures, (4) folder action handlers that operate on children, (5) API response structure for pre-loaded tree.

### Rationale
> Engineering DAG alignment is unambiguous: feature_refinement → technical_design. 85 ACs is substantial new behavior, not a minor patch. Folder tree state management, derived status, and filter propagation are architectural concerns that benefit from explicit design to avoid inconsistencies during implementation. Existing code provides a foundation — design should target the delta only. High confidence (0.92) because keyword match and engineering-next strongly agree with no competing considerations.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-technical-design"
>     match_strength: "strong"
>     reason: "Engineering workflow DAG: feature_refinement → technical_design. 85 ACs warrant architectural planning before implementation."
>     execution_steps:
>       - phase: "1. Context Loading"
>         step: "1.1 Read feature specification"
>       - phase: "2. Design"
>         step: "2.1 Design solution with KISS/YAGNI/DRY"
>       - phase: "3. Document"
>         step: "3.1 Create technical design document"

### Follow-up
> None

---

## DAO-083 — User Confirmation to Proceed with Technical Design

- **Timestamp:** 2026-03-18
- **Source:** human
- **Disposition:** approval
- **Confidence:** 0.99

### Message
> continue

### Guidance Returned
> **Approved. Proceed with Technical Design for FEATURE-049-F (CR-005 folder support).** This confirms the routing decision from DAO-082. No change in direction — execute `x-ipe-task-based-technical-design` as planned.

### Rationale
> Unambiguous single-word confirmation ("continue") in response to explicit agent question ("Shall I proceed with Technical Design?"). DAO-082 already performed full analysis and selected technical-design as next step. No new information or redirection.

### Suggested Skills
> - `x-ipe-task-based-technical-design` (confirmed from DAO-082)

### Follow-up
> None

---

| DAO-093 | 2026-03-18T14:23:22Z | TASK-974 | N/A | instruction | 0.95 | Proceed with feature refinement for CR-008; DAO represents human for all following tasks |

## DAO-093
- **Timestamp:** 2026-03-18T14:23:22Z
- **Task ID:** TASK-974
- **Feature ID:** FEATURE-049-F
- **Workflow:** N/A
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** instruction
- **Confidence:** 0.95

### Message
> go for it 'DAO' represent me for following tasks

### Guidance Returned
> Proceed with x-ipe-task-based-feature-refinement for CR-008 (FEATURE-049-F). Set interaction_mode to "dao-represent-human-to-interact" for all subsequent tasks in this session. The next task refines the specification for the shared FilePreviewRenderer component (AC-049-F-18, FR-049-F.23).

### Rationale
> Clear instruction to proceed + explicit DAO delegation. High confidence — no ambiguity. Engineering-next after change_request is feature_refinement.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-feature-refinement"
>     match_strength: "strong"
>     reason: "Engineering workflow: change_request → feature_refinement for CR-008"
>     execution_steps:
>       - phase: "1. Understand Feature"
>         step: "1.1 Read specification"

### Follow-up
> None

---

| DAO-094 | 2026-03-18 | TASK-974 | N/A (post-refinement routing) | instruction | 0.93 | Proceed to Technical Design for FEATURE-049-F CR-008 (Shared File Preview); design against interface contracts to decouple from CR-004 in-progress |

### DAO-094 — Routing: Post Feature Refinement (CR-008)

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-18 |
| Trigger | Phase 6 routing after TASK-974 (Feature Refinement) completion |
| Disposition | instruction |
| Confidence | 0.93 |

- **Task ID:** TASK-974
- **Feature ID:** FEATURE-049-F
- **Workflow:** N/A
- **Calling Skill:** N/A (post-refinement routing)
- **Source:** human (DAO-represented)

**Phase 0–4 Summary:**

Three perspectives evaluated:

1. **Engineering DAG** — Unambiguous: `feature_refinement → technical_design`. CR-008 refinement produced 16 ACs, 3 business rules, and 8 edge cases. The `FilePreviewRenderer` extraction touches shared component architecture (core/ module, dual consumer pattern, format registry, memory management via blob URL lifecycle). This warrants explicit design before implementation.

2. **User intent** — DAO-093 established "dao-represent-human-to-interact" mode. User expects continuous forward progress. No reason to pause.

3. **Dependency risk (CR-004)** — CR-004 (TASK-925, Zephyr 🌬️) is `🔄 in_progress` and creates the `/api/kb/files/{path}/preview` endpoint that CR-008's `FilePreviewRenderer` will consume. However, design can proceed safely because: (a) the existing `/api/ideas/file?path=` endpoint provides an analogous pattern to design against, (b) the `FilePreviewRenderer` should be designed with a configurable endpoint abstraction anyway (per AC-049-F-18 spec), and (c) technical design is a planning artifact — no code is committed, so no merge conflict risk. The design should explicitly document the CR-004 interface contract as a dependency boundary.

**Conflict analysis:** No conflict. All three perspectives converge on "proceed now." The dependency is a design consideration, not a blocker.

**Decision:**

**Proceed to Technical Design for CR-008 (Shared File Preview).** The design should:
- Define `FilePreviewRenderer` as a format-agnostic component with a pluggable endpoint strategy (existing `/api/ideas/file?path=` for deliverable viewer, future `/api/kb/files/{path}/preview` from CR-004 for KB browse)
- Document the CR-004 interface contract boundary explicitly — what the component expects from the preview endpoint (response format, content-type headers, error codes)
- Focus on the extraction/unification architecture: how two consumers (KB browse, deliverable viewer) share one renderer without coupling
- Address memory management (blob URLs, iframe cleanup) and error handling patterns from the 8 edge cases

**Instruction Units:**
1. Execute `x-ipe-task-based-technical-design` for FEATURE-049-F CR-008, using specification v1.8 as input. Design the `FilePreviewRenderer` component architecture with endpoint abstraction to decouple from CR-004's in-progress implementation. Mark CR-004's endpoint as an interface dependency boundary in the design document.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-technical-design"
>     match_strength: "strong"
>     reason: "Engineering DAG: feature_refinement → technical_design. 16 ACs + shared component extraction architecture warrants design pass."
>     execution_steps:
>       - phase: "1. Context Loading"
>         step: "1.1 Read FEATURE-049-F specification v1.8 (CR-008 section)"
>       - phase: "2. Design"
>         step: "2.1 Design FilePreviewRenderer with pluggable endpoint strategy"
>       - phase: "3. Document"
>         step: "3.1 Create/update technical-design.md with CR-008 design"

### Follow-up
> None

---

### DAO-095 — Routing: Post Technical Design (CR-008)

| Field | Value |
|-------|-------|
| Timestamp | 2026-03-18 |
| Trigger | Phase 6 routing after TASK-975 (Technical Design) completion |
| Disposition | instruction |
| Confidence | 0.95 |

**Decision:**

**Proceed to Code Implementation for CR-008 (FilePreviewRenderer shared component).** All prerequisites are satisfied:
- ✅ Specification v1.8 with 16 ACs for CR-008 (TASK-974)
- ✅ Technical Design v1.5 with Step 13 detailing `FilePreviewRenderer` architecture (TASK-975)
- ✅ CR-004 dependency mitigated — design uses configurable endpoint constructor, so implementation can target existing `/api/ideas/file?path=` first; KB browse switches to `/api/kb/files/{path}/preview` when CR-004 (TASK-925, Zephyr 🌬️) completes
- ✅ Net code reduction ~100 LOC — extraction refactoring, not net-new complexity

**Three-perspective convergence:**
1. **Conservative** — Design is locked, dependency is abstracted, low risk. Proceed.
2. **Progressive** — Shared component unlocks preview consistency across KB browse + deliverable viewer. Ship it.
3. **Balanced** — Implementation against existing endpoint first is the safest incremental path. CR-004 integration is a follow-up wiring change.

**Instruction Units:**
1. Execute `x-ipe-task-based-code-implementation` for FEATURE-049-F CR-008. Create `src/x_ipe/static/js/core/file-preview-renderer.js` (~180 LOC) per Step 13 of technical-design.md v1.5. Wire KB browse modal and deliverable viewer to delegate to the shared renderer. Test against `/api/ideas/file?path=` endpoint initially. Validate all 16 CR-008 ACs pass.

### Suggested Skills
> suggested_skills:
>   - skill_name: "x-ipe-task-based-code-implementation"
>     match_strength: "strong"
>     reason: "Engineering DAG: technical_design → implementation. Design is complete (Step 13), spec has 16 ACs, all prerequisites met."
>     execution_steps:
>       - phase: "1. Context Loading"
>         step: "1.1 Read technical-design.md v1.5 Step 13 (FilePreviewRenderer)"
>       - phase: "2. Implementation"
>         step: "2.1 Create core/file-preview-renderer.js with class, type detection, format handlers"
>         step: "2.2 Refactor KB browse modal to delegate preview to FilePreviewRenderer"
>         step: "2.3 Refactor deliverable viewer to delegate preview to FilePreviewRenderer"
>       - phase: "3. Testing"
>         step: "3.1 Write tests covering type detection, blob lifecycle, error states"
>       - phase: "4. Validation"
>         step: "4.1 Verify all 16 CR-008 ACs pass"

### Follow-up
> After implementation completes, route to `x-ipe-task-based-feature-acceptance-test` for CR-008 AC validation.
> When CR-004 (TASK-925) completes, wire KB browse to use `/api/kb/files/{path}/preview` endpoint — this is a one-line config change in the FilePreviewRenderer constructor call.
