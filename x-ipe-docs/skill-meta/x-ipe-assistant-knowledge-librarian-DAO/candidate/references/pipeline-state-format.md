# Pipeline State Format — Knowledge Librarian

## Overview

Each pipeline execution maintains a `pipeline_state` object that tracks step-level progress. This enables graceful degradation — if one step fails, subsequent steps can still execute with partial data.

## Schema

```yaml
pipeline_state:
  session_id: "librarian-{ISO-8601-timestamp}"
  request_type: "construction | extraction | ontology_only | presentation | storage | classification_failed"
  selected_constructor: "x-ipe-knowledge-constructor-{name} | null"
  iteration_count: 0
  max_iterations: 3
  steps:
    discovery:        { status: "pending | done | failed", output_ref: null }
    classification:   { status: "pending | done | failed", output_ref: null }
    格物_1_framework: { status: "pending | done | skipped | failed", output_ref: null }
    格物_2_overview:  { status: "pending | done | skipped | failed", output_ref: null }
    格物_3_rubric:    { status: "pending | done | skipped | failed", output_ref: null }
    格物_4_plan:      { status: "pending | done | skipped | failed", output_ref: null }
    致知_1_execute:   { status: "pending | done | skipped | failed", output_ref: null }
    致知_2_fill:      { status: "pending | done | skipped | failed", output_ref: null }
    致知_3_critique:  { status: "pending | done | skipped | failed", output_ref: null }
    致知_4_ontology:  { status: "pending | done | skipped | failed", output_ref: null }
    致知_5_store:     { status: "pending | done | skipped | failed", output_ref: null }
    致知_6_present:   { status: "pending | done | skipped | failed", output_ref: null }
  pipeline_status: "pending | success | partial | failed"
```

## Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Step not yet executed |
| `done` | Step completed successfully |
| `skipped` | Step not applicable for this request_type |
| `failed` | Step attempted but failed (error logged) |

## Pipeline Status Computation

```
IF all steps are "done" or "skipped" → pipeline_status = "success"
IF any step is "failed" but pipeline continued → pipeline_status = "partial"
IF Phase 1 (discovery or classification) failed → pipeline_status = "failed"
```

## Working Directory Layout

```
x-ipe-docs/memory/.working/
└── librarian-2026-04-20T071834/
    ├── framework/        # 格物.1 output
    ├── overview/         # 格物.2 output
    ├── rubric/           # 格物.3 output
    ├── plan/             # 格物.4 output
    ├── extracted/        # 致知.1 output
    ├── draft/            # 致知.2 output
    └── critique/         # 致知.3 output
```

Session ID format: `librarian-{ISO-8601-compact}` (e.g., `librarian-2026-04-20T071834`).
