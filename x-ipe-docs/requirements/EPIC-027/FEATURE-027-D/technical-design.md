# FEATURE-027-D: MCP Configuration Deployment — Technical Design

## Part 1: Agent Summary

### Architecture Decision
Extract and generalize the existing Copilot-only MCP merge logic from `scaffold.py` into a new `MCPDeployerService`. The service reads target path and format from `CLIAdapterData`, resolves the actual filesystem path, and performs an idempotent JSON merge.

### Components
1. **`MCPDeployerService`** — New service in `src/x_ipe/services/mcp_deployer_service.py`
2. **Modified `scaffold.py`** — Existing `merge_mcp_config()` delegates to MCPDeployerService
3. **Modified `main.py`** — Init/upgrade MCP section uses MCPDeployerService with active CLI

### Key Design Decisions
- **Single source of truth for MCP servers:** `.github/copilot/mcp-config.json` in the project root (unchanged from current behavior)
- **Target path comes from adapter registry:** `CLIAdapterData.mcp_config_path` + `mcp_config_format`
- **Tilde expansion:** `~` in paths is expanded via `Path.expanduser()`
- **Project paths:** resolved relative to `project_root`
- **No new CLI args needed:** the active CLI (from `_resolve_cli_selection`) determines the target

---

## Part 2: Implementation Guide

### File: `src/x_ipe/services/mcp_deployer_service.py` (NEW)

```python
@dataclass
class MCPDeployResult:
    created: List[Path]
    skipped: List[Path]
    merged_count: int
    skipped_count: int

class MCPDeployerService:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def get_source_servers(self) -> dict:
        """Read MCP servers from .github/copilot/mcp-config.json"""

    def resolve_target_path(self, adapter: CLIAdapterData) -> Path:
        """Resolve mcp_config_path based on mcp_config_format"""

    def deploy(self, adapter: CLIAdapterData, servers_to_merge: list[str] | None = None,
               force: bool = False, dry_run: bool = False) -> MCPDeployResult:
        """Main entry point: merge MCP servers into target CLI's config"""
```

### Method: `resolve_target_path`
```
if adapter.mcp_config_format == "global":
    return Path(adapter.mcp_config_path).expanduser()
else:  # "project"
    return self.project_root / adapter.mcp_config_path
```

### Method: `deploy`
```
1. Get source servers (get_source_servers)
2. Filter to servers_to_merge if specified
3. If dry_run, return early with MCPDeployResult
4. Resolve target path
5. Load existing target config (handle missing/malformed)
6. Merge: for each server:
   - If exists in target and not force → skip
   - Otherwise → add/overwrite
7. Write merged config
8. Return MCPDeployResult
```

### Integration: `main.py` init command (lines ~240-270)
Replace the hardcoded Copilot MCP merge with:
```python
from x_ipe.services.mcp_deployer_service import MCPDeployerService
adapter = CLIAdapterService().get_adapter(selected_cli)
deployer = MCPDeployerService(project_root)
result = deployer.deploy(adapter, servers_to_merge=servers_to_merge, force=force, dry_run=dry_run)
```

### Dependency Diagram
```
CLIAdapterService.get_adapter(cli_name)
         │
         ▼
    CLIAdapterData  ──────────────────────┐
    (mcp_config_path, mcp_config_format)  │
         │                                │
         ▼                                ▼
MCPDeployerService.resolve_target_path()  MCPDeployerService.deploy()
         │                                │
         ▼                                ▼
    Path (expanded)               JSON read/merge/write
```

### Backward Compatibility
- `scaffold.merge_mcp_config()` remains functional but deprecated — the init command switches to MCPDeployerService
- Existing tests for scaffold MCP methods continue to pass unchanged
