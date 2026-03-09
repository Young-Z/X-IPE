# Feature Specification: Workflow Interaction Mode — Template & Backend API

> Feature ID: FEATURE-044-E
> Epic ID: EPIC-044
> Version: v1.0
> Status: Refined
> Last Updated: 03-09-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-09-2026 | Initial specification — documents target state after CR-002 (interaction_mode with semantic enum keys) |

## Linked Mockups

No standalone mockups — UI element is a dropdown in the workflow panel header, documented in FEATURE-044-F (UI Toggle).

## Overview

FEATURE-044-E provides the backend infrastructure for persisting and validating the workflow **interaction mode** — the setting that controls how AI agents interact with humans during task execution. The interaction mode determines whether the DAO skill represents the human autonomously, represents the human only for inner-skill questions, or whether the human interacts directly.

This feature encompasses:
1. **Workflow template** with default interaction mode configuration
2. **Backend API** (`PATCH /api/workflow/{name}/settings`) for updating the mode at runtime
3. **Persistence** of the mode in `workflow-{name}.json` files across server restarts
4. **Backward compatibility** — accepting legacy `auto_proceed` values and auto-migrating to `interaction_mode`

The primary consumers are: the frontend UI dropdown (FEATURE-044-F), the orchestrator skill (FEATURE-044-D), and the action execution modal's CLI flag builder.

## User Stories

**US-044-E.1:** As a workflow operator, I want to change the interaction mode for a workflow so that I can control how much autonomy the AI agent has during task execution.

**US-044-E.2:** As an AI agent, I want to read the interaction mode from the workflow configuration so that I know whether to call the DAO skill, ask the human directly, or auto-proceed between tasks.

**US-044-E.3:** As a system administrator, I want the interaction mode to persist across server restarts so that I don't have to reconfigure it every time.

**US-044-E.4:** As a developer, I want backward compatibility with legacy `auto_proceed` values so that existing workflows and API consumers continue to work without breaking changes.

## Acceptance Criteria

### Template & Default Configuration

**AC-044-E.1:** The workflow template (`x-ipe-docs/config/workflow-template.json` and `src/x_ipe/resources/config/workflow-template.json`) MUST include `global.process_preference.interaction_mode` with default value `"interact-with-human"`.

**AC-044-E.2:** New workflows created from the template MUST inherit `global.process_preference.interaction_mode: "interact-with-human"` as the default.

**AC-044-E.3:** The template MUST NOT contain the legacy key `auto_proceed`.

### Backend API — Validation

**AC-044-E.4:** `PATCH /api/workflow/{name}/settings` MUST accept a JSON body with `process_preference.interaction_mode` set to one of:
- `"interact-with-human"` — human handles all touchpoints directly
- `"dao-represent-human-to-interact"` — DAO represents the human at ALL touchpoints
- `"dao-represent-human-to-interact-for-questions-in-skill"` — DAO represents human for inner-skill questions only

**AC-044-E.5:** The API MUST return HTTP 400 with error type `INVALID_VALUE` and a descriptive message if `interaction_mode` is set to an unrecognized value (not in the valid set and not in the legacy migration map).

**AC-044-E.6:** The API MUST return HTTP 404 if the workflow `{name}` does not exist.

**AC-044-E.7:** The API MUST return HTTP 200 with the full updated workflow data on success.

### Backend API — Backward Compatibility

**AC-044-E.8:** The backend MUST accept legacy values via a `LEGACY_MAP`:
| Legacy Value | Maps To |
|---|---|
| `"manual"` | `"interact-with-human"` |
| `"auto"` | `"dao-represent-human-to-interact"` |
| `"stop_for_question"` | `"dao-represent-human-to-interact-for-questions-in-skill"` |

**AC-044-E.9:** When a legacy value is received via the API, the backend MUST auto-migrate it to the new value before validation and persistence. The migrated (new) value MUST be persisted — never the legacy value.

**AC-044-E.10:** The backend MUST also accept the legacy key name `auto_proceed` in the request body. If `auto_proceed` is provided instead of `interaction_mode`, the backend MUST treat it as `interaction_mode` (key migration).

**AC-044-E.11:** When reading a persisted workflow that contains the legacy key `auto_proceed`, the backend MUST auto-migrate it to `interaction_mode` on read. The next write MUST persist the new key name.

### Persistence

**AC-044-E.12:** The interaction mode MUST be persisted in `workflow-{name}.json` under `global.process_preference.interaction_mode`.

**AC-044-E.13:** The persisted value MUST survive server restarts — reading the workflow after restart MUST return the same interaction mode that was last set.

**AC-044-E.14:** The `last_activity` timestamp in the workflow JSON MUST be updated whenever the interaction mode is changed.

### CLI Flag Integration

**AC-044-E.15:** The action execution modal MUST read `interaction_mode` from `instance.global.process_preference.interaction_mode` (falling back to `auto_proceed` for backward compat, then defaulting to `"interact-with-human"`).

**AC-044-E.16:** The CLI flag builder MUST generate flags based on the interaction mode:
| Interaction Mode | CLI Flag |
|---|---|
| `"dao-represent-human-to-interact"` | `--interaction@dao-represent-human-to-interact` |
| `"dao-represent-human-to-interact-for-questions-in-skill"` | `--interaction@dao-represent-human-to-interact-for-questions-in-skill` |
| `"interact-with-human"` | *(no flag appended)* |

**AC-044-E.17:** The method `_loadAutoProceed()` MUST be renamed to `_loadInteractionMode()`.

**AC-044-E.18:** The method `_buildExecutionFlag()` MUST use the `--interaction@` prefix instead of `--execute@`.

## Functional Requirements

**FR-044-E.1:** The system MUST provide a `PATCH /api/workflow/{name}/settings` endpoint that accepts `process_preference` with `interaction_mode`.

**FR-044-E.2:** The system MUST validate that `interaction_mode` is one of the three valid values or a legacy value that can be mapped.

**FR-044-E.3:** The system MUST persist the interaction mode to the workflow JSON file immediately on successful update.

**FR-044-E.4:** The system MUST maintain a `LEGACY_MAP` constant that maps old enum values to new enum values for backward compatibility.

**FR-044-E.5:** The system MUST maintain a `LEGACY_KEY_MAP` that recognizes `auto_proceed` as an alias for `interaction_mode` in API requests.

**FR-044-E.6:** The system MUST auto-migrate legacy values on read (when loading persisted workflow files) so that the in-memory representation always uses the new key and values.

## Non-Functional Requirements

**NFR-044-E.1 (Performance):** Settings update API response time MUST be under 200ms for file-based persistence.

**NFR-044-E.2 (Reliability):** The workflow JSON file MUST NOT be corrupted if the server crashes during a write — use atomic write patterns (write-to-temp then rename).

**NFR-044-E.3 (Backward Compatibility):** All existing API consumers, test suites, and CLI tools that use legacy values MUST continue to work without modification during the migration period.

**NFR-044-E.4 (Semantic Clarity):** Enum values MUST be self-describing — an AI agent reading the value without documentation should understand the intended behavior from the key name alone.

## UI/UX Requirements

UI rendering is owned by FEATURE-044-F. This feature provides the backend data contract that the UI consumes. The API response format is:

```json
{
  "global": {
    "process_preference": {
      "interaction_mode": "interact-with-human"
    }
  }
}
```

## Dependencies

### Internal Dependencies

| Dependency | Feature | Impact |
|------------|---------|--------|
| Workflow JSON persistence | Core infrastructure | Must support key rename in persisted files |
| FEATURE-044-B | Skill template update | Templates reference `interaction_mode` in skill YAML |
| FEATURE-044-C | Bulk skill update | 19 skills use `interaction_mode` in conditional blocks |
| FEATURE-044-D | Orchestrator update | Reads `interaction_mode` for routing decisions |
| FEATURE-044-F | UI toggle | Calls this API, renders dropdown |
| EPIC-047 | DAO skill | `dao-represent-human-to-interact` mode invokes DAO |

### External Dependencies

None.

## Business Rules

**BR-044-E.1:** The default interaction mode for all new workflows MUST be `"interact-with-human"` (safest mode — human controls all touchpoints).

**BR-044-E.2:** Legacy values MUST be silently migrated — no error, no warning to the user. The migration is transparent.

**BR-044-E.3:** The system MUST never persist a legacy value. All writes MUST use the new enum values.

**BR-044-E.4:** The three interaction modes are mutually exclusive — exactly one mode is active per workflow at any time.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Workflow JSON has `auto_proceed: "auto"` (legacy) | On read: migrate to `interaction_mode: "dao-represent-human-to-interact"` |
| API receives `auto_proceed: "manual"` (legacy key + value) | Migrate key to `interaction_mode`, migrate value to `"interact-with-human"`, persist new |
| API receives unknown value `"turbo"` | Return HTTP 400, error type `INVALID_VALUE` |
| API receives both `auto_proceed` and `interaction_mode` | `interaction_mode` takes precedence, ignore `auto_proceed` |
| Workflow JSON missing `process_preference` entirely | Default to `interaction_mode: "interact-with-human"` |
| Concurrent settings updates | Last-write-wins (file-based, single-server) |
| Empty request body | Return HTTP 400 |

## Out of Scope

- **UI dropdown rendering** — owned by FEATURE-044-F
- **Skill template content** — owned by FEATURE-044-B
- **Bulk skill updates** — owned by FEATURE-044-C
- **Orchestrator routing logic** — owned by FEATURE-044-D
- **DAO skill behavior** — owned by EPIC-047
- **Multi-server concurrency** — system is single-server
- **Deprecation timeline for legacy values** — to be decided in future CR

## Technical Considerations

- The backend validation logic lives in `workflow_manager_service.py` `update_settings()` method
- The `LEGACY_MAP` and `LEGACY_KEY_MAP` should be module-level constants for easy maintenance
- The migration-on-read pattern ensures that even if the JSON file was last written by an old version, the next read normalizes it
- The CLI flag format uses `--interaction@{mode}` where `{mode}` is the exact enum value — this makes parsing trivial for the receiving agent
- Template files exist in two locations: `x-ipe-docs/config/` (development) and `src/x_ipe/resources/config/` (PyPI package) — both must stay synchronized

## Open Questions

None — all questions resolved via CR-002 and user feedback during ideation.
