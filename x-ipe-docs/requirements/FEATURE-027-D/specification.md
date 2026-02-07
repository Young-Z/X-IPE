# FEATURE-027-D: MCP Configuration Deployment

## Overview

Deploy MCP server configuration in each CLI's native format and location. The existing codebase has a Copilot-only implementation in `scaffold.py` (methods: `copy_mcp_config`, `get_project_mcp_servers`, `merge_mcp_config`). This feature extracts and generalizes that logic into a CLI-agnostic `MCPDeployerService` that reads target paths/formats from the CLI adapter registry.

**Dependencies:** FEATURE-027-A (CLI Adapter Registry & Service)

---

## Acceptance Criteria

### AC-1: CLI-Aware MCP Path Resolution

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-1.1 | MCPDeployerService reads `mcp_config_path` from CLIAdapterData for the active CLI | MUST |
| AC-1.2 | MCPDeployerService reads `mcp_config_format` ("global" or "project") from CLIAdapterData | MUST |
| AC-1.3 | For `mcp_config_format: "global"`, path is resolved relative to home directory (e.g., `~/.copilot/mcp-config.json`) | MUST |
| AC-1.4 | For `mcp_config_format: "project"`, path is resolved relative to project root (e.g., `./opencode.json`, `./.mcp.json`) | MUST |

### AC-2: MCP Server Discovery

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-2.1 | MCPDeployerService discovers MCP servers from `{project_root}/.github/copilot/mcp-config.json` (source of truth) | MUST |
| AC-2.2 | Returns dict of `server_name -> server_config` | MUST |
| AC-2.3 | Returns empty dict if source file missing or malformed | MUST |

### AC-3: MCP Config Merge

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-3.1 | Merges X-IPE MCP servers into the target CLI's config file | MUST |
| AC-3.2 | Creates target file and parent directories if they don't exist | MUST |
| AC-3.3 | Preserves all non-X-IPE entries in existing target config | MUST |
| AC-3.4 | When target file has malformed JSON, creates fresh config with only X-IPE servers | MUST |
| AC-3.5 | Supports selective merge (specific server names) | SHOULD |
| AC-3.6 | Conflict handling: skip existing server unless `force=True` | MUST |

### AC-4: CLI-Specific Config Structure

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-4.1 | Copilot: writes `{"mcpServers": {...}}` format | MUST |
| AC-4.2 | OpenCode: writes under `mcpServers` key within existing `opencode.json` (preserves other keys) | MUST |
| AC-4.3 | Claude Code: writes `{"mcpServers": {...}}` format to `.mcp.json` | MUST |

### AC-5: Dry Run Support

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-5.1 | With `dry_run=True`, no files are written | MUST |
| AC-5.2 | Dry run returns what would be changed (created/skipped lists) | SHOULD |

### AC-6: Integration with Init/Upgrade Commands

| AC ID | Description | Priority |
|-------|-------------|----------|
| AC-6.1 | `x-ipe init` uses MCPDeployerService instead of direct scaffold methods for MCP merge | MUST |
| AC-6.2 | The active CLI determines which target config is used | MUST |

---

## Functional Requirements

| FR ID | Description |
|-------|-------------|
| FR-1 | MCPDeployerService must be instantiable without Flask context |
| FR-2 | Service must use CLIAdapterService to resolve the active CLI's MCP config details |
| FR-3 | Service must support all 3 CLIs: copilot, opencode, claude-code |
| FR-4 | Service must handle both global and project-scoped config files |
| FR-5 | Service must be idempotent — re-running produces same result |

## Non-Functional Requirements

| NFR ID | Description |
|--------|-------------|
| NFR-1 | No external dependencies beyond stdlib + existing project deps |
| NFR-2 | Method under 50 lines (KISS) |
| NFR-3 | Service uses `@x_ipe_tracing` decorator |

---

## User Stories

| US ID | Story |
|-------|-------|
| US-1 | As a developer using OpenCode, when I run `x-ipe init`, MCP servers are deployed to `opencode.json` in my project root |
| US-2 | As a developer switching from Copilot to Claude Code, when I run init, MCP servers are deployed to `.mcp.json` instead of `~/.copilot/mcp-config.json` |
| US-3 | As a developer with existing MCP servers in my config, the merge preserves my custom entries |

---

## Edge Cases

| EC ID | Description | Expected Behavior |
|-------|-------------|-------------------|
| EC-1 | Target config file doesn't exist | Create file with only X-IPE servers |
| EC-2 | Target config has malformed JSON | Replace with fresh config containing X-IPE servers |
| EC-3 | Source MCP config (`.github/copilot/mcp-config.json`) missing | No-op, return empty |
| EC-4 | OpenCode config has other keys besides `mcpServers` | Preserve all other keys |
| EC-5 | Server name collision with `force=False` | Skip, add to skipped list |
| EC-6 | Server name collision with `force=True` | Overwrite existing entry |
| EC-7 | `mcp_config_path` is `~/.copilot/mcp-config.json` (tilde) | Expand `~` to home directory |
