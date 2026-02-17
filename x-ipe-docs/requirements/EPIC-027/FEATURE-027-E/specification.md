# FEATURE-027-E: CLI Migration & Upgrade — Specification

## Overview

Add a `--cli <name>` option to the existing `x-ipe upgrade` command that triggers CLI migration: backs up current CLI-specific artifacts, updates the active CLI in `.x-ipe.yaml`, and redeploys skills and MCP config for the new target CLI.

**Dependencies:** FEATURE-027-B (init/selection), FEATURE-027-C (skill translation), FEATURE-027-D (MCP deployment)

---

## Acceptance Criteria

### AC-1: --cli Flag on Upgrade Command

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-1.1 | `x-ipe upgrade --cli <name>` accepts a CLI name from the adapter registry | MUST |
| AC-1.2 | If `--cli` matches the current active CLI, skip migration and log "already using <cli>" | MUST |
| AC-1.3 | If `--cli` is an unknown name, raise BadParameter with available options | MUST |

### AC-2: Backup Old Artifacts

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-2.1 | Before migration, back up the old CLI's skills folder to `.x-ipe/backup/{old_cli}-{timestamp}/` | MUST |
| AC-2.2 | Back up the old CLI's instructions file if it exists | MUST |
| AC-2.3 | Back up the old CLI's MCP config file if it exists and is project-scoped | SHOULD |
| AC-2.4 | With `--dry-run`, show what would be backed up without writing | MUST |

### AC-3: Config Update

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-3.1 | Update `cli` key in `.x-ipe.yaml` to the new CLI name | MUST |
| AC-3.2 | With `--dry-run`, skip config write | MUST |

### AC-4: Redeploy Artifacts

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-4.1 | After backup, deploy MCP config via MCPDeployerService for the new CLI | MUST |
| AC-4.2 | Log summary of backed-up and created files | MUST |

### AC-5: No-CLI-Flag Behavior

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-5.1 | When `--cli` is not provided, upgrade runs the existing skills sync flow (no migration) | MUST |

---

## Edge Cases

| EC ID | Description | Expected Behavior |
|-------|-------------|-------------------|
| EC-1 | No `.x-ipe.yaml` exists (never initialized) | Error: "Run `x-ipe init` first" |
| EC-2 | Current CLI has no artifacts to back up | Proceed with deploy only, log "no artifacts to back up" |
| EC-3 | Target CLI skills folder already exists | Back up existing, then deploy new |
