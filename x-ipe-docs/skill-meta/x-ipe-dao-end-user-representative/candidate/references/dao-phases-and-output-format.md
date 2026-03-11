# DAO Phases & CLI Output Format

## Phase Definitions (格物致知 Framework)

格物：推究、探究事物的道理、规律 — Investigate the nature and patterns of things.
致知：让自己的认知、智慧达到完备 — Let your understanding and wisdom reach completeness.

| Phase | Chinese | English | 心法 | Activities |
|-------|---------|---------|------|------------|
| 0 | 礼 (Lǐ) | Greet | 有朋自远方来 | Print "道 · Human Representative — ready." |
| 1 | 格物 (Géwù) | Investigate | 静→安→虑→得; 兼听则明; 顺势者昌 | Restate need, decompose compound, analyze unit dependencies, three perspectives, assess direction/timing/environment |
| 2 | 致知 (Zhìzhī) | Reach Understanding | 两利取重，两害取轻; 谋贵众，断贵独 | Per unit: scan skills, weigh 利/害, three-scenario, worst-case gate, commit. Then: assemble execution_plan from dependencies |
| 3 | 录 (Lù) | Record | — | Write semantic log entry (append-only) |
| 4 | 示 (Shì) | Present | 言之有文，行而远 | Format structured CLI output |

**Phase Rules:** Order fixed: 0→1→2→3→4. Phases 1–2 are NEVER skippable. Phase 3 is MANDATORY. Backbone is INTERNAL — callers never see phase names.

## CLI Output Format (Phase 4)

Per instruction unit:
```
道 · Instruction Unit {N}/{total}
Disposition: {disposition}
Content: {content}
Rationale: {rationale_summary}
Skills: {suggested_skills summary or "none"}
Dependencies: {depends_on indices or "none"}
```

After all units, show execution plan:
```
道 · Execution Plan: {strategy}
  Group 1 (parallel): Unit {indices} — {brief description}
  Group 2 (after group 1): Unit {indices} — {brief description}
```

After execution plan:
```
道 · Total: {N} instruction unit(s) | Confidence: {confidence} | Fallback: {fallback_required}
道 · Complete.
```

IF any unit has suggested_skills non-empty, APPEND:
```
⚠️ Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
⚠️ Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
⚠️ Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
```

## Decomposition Criteria (Step 1.1b)

Split ONLY when:
- Sub-instructions target different domains (e.g., skill update vs code fix)
- They could reasonably be separate user messages
- They require different task-based skills

Do NOT split when:
- Parts are tightly coupled steps of ONE task
- Second part is natural consequence of the first
- Splitting loses important linking context

Default: 1 unit. Maximum: 3 units. Order: first mentioned = first unit.

## Dependency Analysis Criteria (Step 1.1b)

After decomposition, analyze dependencies between units:

**Units are DEPENDENT when:**
- One unit creates a file/resource that another unit modifies or reads
- One unit changes a schema/interface that another unit implements against
- One unit's output (e.g., a specification) is an input to another (e.g., implementation)
- Both units modify the same file (write conflict)

**Units are INDEPENDENT when:**
- They target different files, features, or skill domains
- Neither unit's output feeds the other's input
- They can be executed by separate agents without coordination
- They operate on different parts of the codebase with no shared state

**Execution Plan Strategy:**
- `parallel` — ALL units are independent; consuming agent should run them concurrently (e.g., background sub-agents)
- `sequential` — Units form a dependency chain; must execute in order
- `mixed` — Some units are independent (same group), others depend on earlier groups

**Single unit:** Always `strategy: "sequential"` with `groups: [[0]]` — no parallelism analysis needed.
