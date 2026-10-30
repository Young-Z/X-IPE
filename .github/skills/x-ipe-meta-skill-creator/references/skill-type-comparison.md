# Skill Type Comparison Reference

Quick reference for choosing the right skill type when creating or categorizing X-IPE skills.

---

## Quick Comparison

| Skill Type | Structure | Caller | State Model | When to Use |
|---|---|---|---|---|
| `x-ipe-task-based` | Flat steps or phase scaffold | Human / workflow | Lifecycle-owned task, domain execution context | User-facing project lifecycle workflows |
| `x-ipe-task-category` | Workflow orchestration | Category completion triggers | Aggregation — collects child outputs | Grouping related task completions |
| `x-ipe-tool` | Scripts + Operations | Any skill / agent | Stateless — caller manages context | Utility functions and integrations |
| `x-ipe-workflow-orchestration` | Multi-skill coordination | Workflow triggers | Orchestration — manages child skills | Cross-skill pipelines |
| `x-ipe-meta` | Procedural steps | Developer / agent | Internal — manages creation process | Creating and managing other skills |
| `x-ipe-knowledge` | Operations + Steps (phases inside) | Assistant orchestrator | External — orchestrator passes context | Knowledge pipeline services |
| `x-ipe-assistant` | 格物致知 backbone | General AI / workflow | Manages workflow state | Coordination, orchestration, human representation |
| `x-ipe-dao` ⚠️ | DEPRECATED → use `x-ipe-assistant` | — | — | — |

---

## Detailed Type Descriptions

### task-based (`x-ipe-task-based-*`)

**Structure:** Flat steps or the existing phase scaffold (博学之 → 审问之 → 慎思之 → 明辨之 → 笃行之). Required activities are context gathering, domain execution and verification; named inquiry/reflection phases are proportional, not compulsory ceremony. Preserve domain gates and routing when simplifying.

**Invocation:** Auto-discovered via `x-ipe-task-based-*/SKILL.md` scan. Matched to user requests by trigger keywords in description.

**State:** The lifecycle supplies the task and manages registration/board transitions. Reuse its task ID; do not create duplicate entries. Domain results retain `category`, `next_task_based_skill`, and nested `process_preference.interaction_mode` for the existing caller. This creator update does not modernize the entire application lifecycle.

**When to use:** End-to-end project lifecycle workflows triggered by human requests. Examples: feature refinement, technical design, code implementation, bug fixing.

**Naming:** `x-ipe-task-based-{name}` (e.g., `x-ipe-task-based-code-implementation`)

---

### task-category (`x-ipe+{category}+{name}`)

**Structure:** Workflow orchestration template. Triggered when related tasks in a category complete.

**Invocation:** Category completion triggers, not direct user requests.

**State:** Aggregation — collects outputs from child tasks.

**When to use:** Category-level orchestration when a group of related tasks finish. Example: all features in an epic complete → trigger release orchestration.

**Naming:** `x-ipe+{category}+{name}` (e.g., `x-ipe+feature-stage+all`)

**Exact legacy exception:** `x-ipe+feature+quality-board-management` remains a
category identity but exposes the established reporting Operations + `<operation>`
and `operation_output`, not child-completion workflow output. Updates preserve
that package's domain scaffold and validate as `x-ipe-task-category`. The exception
does not apply to new/lookalike categories or make the name a tool alias.

---

### tool (`x-ipe-tool-*`)

**Structure:** Scripts + Operations pattern. Each operation is a standalone action with `<operation>` blocks.

**Invocation:** Called by any skill or agent that needs the utility. Not auto-discovered for task matching.

**State:** Stateless — the calling skill/agent manages all context.

**When to use:** Utility functions, integrations, or specific tool operations. Examples: task board management, tracing instrumentation, test generation.

**Naming:** `x-ipe-tool-{name}` (e.g., `x-ipe-tool-task-board-manager`)

---

### workflow-orchestration (`x-ipe-workflow-*`)

**Structure:** Multi-skill coordination with workflow steps and action sequences.

**Invocation:** Workflow triggers (manual or automated).

**State:** Orchestration — manages child skill execution order and data flow.

**When to use:** Multi-skill pipelines that need coordinated execution across several skills. Example: full feature pipeline from refinement → design → implementation → testing.

**Naming:** `x-ipe-workflow-{name}` (e.g., `x-ipe-workflow-task-execution`)

---

### meta (`x-ipe-meta-*`)

**Structure:** Procedural steps for skill lifecycle management.

**Invocation:** Developer or agent request to create/manage skills.

**State:** Internal — manages the creation/update process.

**When to use:** Creating, updating, or validating other skills. Example: skill creator, lesson learned capture.

**Naming:** `x-ipe-meta-{name}` (e.g., `x-ipe-meta-skill-creator`)

---

### knowledge (`x-ipe-knowledge-*`) — NEW

**Structure:** Operations as primary structure with phase backbone (博学之→笃行之) **inside** each operation. Hybrid of tool (Operations) and task-based (phases).

**Invocation:** NOT auto-discovered. Called by an assistant orchestrator (e.g., `x-ipe-assistant-knowledge-librarian-DAO`). The orchestrator decides when and which operations to invoke.

**State:** External — the orchestrator passes full context per call. Knowledge skills are stateless services.

**When to use:** Knowledge pipeline services — extraction, synthesis, indexing, ontology management, and other knowledge operations.

**Key feature:** Each operation has a typed contract (input, output, writes_to, constraints) enabling the orchestrator to plan execution and predict side effects.

**Naming:** `x-ipe-knowledge-{sub-category}-{name}` (e.g., `x-ipe-knowledge-extractor-web`)

---

### assistant (`x-ipe-assistant-*`) — NEW

**Structure:** 格物致知 (Investigate to Reach Understanding) backbone — same cognitive framework as the former `x-ipe-dao` type. Phases: 礼→格物→致知→录→示.

**Invocation:** Auto-discovered via `x-ipe-assistant-*/SKILL.md` scan. Matched to user requests by trigger keywords, or called by workflows.

**State:** Manages workflow state — coordinates other skills, makes decisions, orchestrates pipelines.

**When to use:** Coordination and orchestration skills that need nuanced reasoning. Human representation at decision points. Knowledge pipeline orchestration.

**Execution:** Apply the backbone in the same agent loop by default; no model-tier
requirement or automatic specialist handoff. Use the single-loop authoring policy
for concrete delegation or independent-review triggers.

**Naming:** `x-ipe-assistant-{name}` (e.g., `x-ipe-assistant-knowledge-librarian-DAO`)

---

### dao (`x-ipe-dao-*`) — ⚠️ DEPRECATED

**Status:** Deprecated. Use `x-ipe-assistant` instead.

**Migration:** New human representatives use `x-ipe-assistant-{name}`. Rename existing DAO identities only under separately authorized migration; preserve their contracts otherwise.

**Backward compatibility:** Existing `x-ipe-dao-*` skills continue to function. Explicit legacy DAO selection uses `x-ipe-dao.md` and `skill-meta-x-ipe-dao.md`; it is not silently redirected. Assistant selection uses the assistant pair.
