"""MCP Configuration Deployment Service.

Deploys MCP server configuration to each CLI's native format and location,
reading target paths from the CLI adapter registry.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from x_ipe.services.cli_adapter_service import CLIAdapterData
from x_ipe.tracing import x_ipe_tracing


@dataclass
class MCPDeployResult:
    """Result of an MCP deployment operation."""
    created: List[Path] = field(default_factory=list)
    skipped: List[Path] = field(default_factory=list)
    merged_count: int = 0
    skipped_count: int = 0


class MCPDeployerService:
    """Deploys MCP server config to CLI-specific locations."""

    SOURCE_PATH = Path(".github") / "copilot" / "mcp-config.json"

    def __init__(self, project_root: Path):
        self.project_root = project_root

    @x_ipe_tracing()
    def get_source_servers(self) -> dict:
        """Read MCP servers from project's .github/copilot/mcp-config.json."""
        source = self.project_root / self.SOURCE_PATH
        if not source.exists():
            return {}
        try:
            config = json.loads(source.read_text())
            return config.get("mcpServers", {})
        except (json.JSONDecodeError, IOError):
            return {}

    @x_ipe_tracing()
    def resolve_target_path(self, adapter: CLIAdapterData) -> Path:
        """Resolve the target MCP config path based on adapter format."""
        raw = adapter.mcp_config_path
        if adapter.mcp_config_format == "global":
            return Path(raw).expanduser()
        return self.project_root / raw

    @x_ipe_tracing()
    def deploy(
        self,
        adapter: CLIAdapterData,
        servers_to_merge: Optional[List[str]] = None,
        force: bool = False,
        dry_run: bool = False,
    ) -> MCPDeployResult:
        """Merge MCP servers into the target CLI's config file.

        Handles three MCP config formats:
        - "global": Standalone file with {"mcpServers": {...}} (copilot)
        - "project": Standalone file with {"mcpServers": {...}} (claude-code)
        - "nested": mcpServers key inside a larger config file (opencode)
        """
        source_servers = self.get_source_servers()
        if not source_servers:
            return MCPDeployResult()

        if servers_to_merge is not None:
            source_servers = {
                k: v for k, v in source_servers.items() if k in servers_to_merge
            }
            if not source_servers:
                return MCPDeployResult()

        target_path = self.resolve_target_path(adapter)

        if dry_run:
            return MCPDeployResult(
                created=[target_path],
                merged_count=len(source_servers),
            )

        # Load existing target config
        use_nested = (adapter.mcp_config_format == 'nested')
        config_key = "mcp" if use_nested else "mcpServers"
        
        target_config = {}
        if target_path.exists():
            try:
                target_config = json.loads(target_path.read_text())
            except (json.JSONDecodeError, IOError):
                target_config = {}

        if config_key not in target_config:
            target_config[config_key] = {}
        if use_nested and "$schema" not in target_config:
            target_config["$schema"] = "https://opencode.ai/config.json"

        # Transform server configs for nested (opencode) format
        if use_nested:
            transformed = {}
            for name, cfg in source_servers.items():
                entry = {
                    "type": cfg.get("type", "local"),
                    "enabled": True,
                }
                cmd = cfg.get("command", "")
                args = cfg.get("args", [])
                if cmd or args:
                    entry["command"] = [cmd] + args if args else [cmd]
                if cfg.get("env"):
                    entry["environment"] = cfg["env"]
                transformed[name] = entry
            source_servers = transformed

        # Merge
        merged_count = 0
        skipped_count = 0
        for name, config in source_servers.items():
            if name in target_config[config_key] and not force:
                skipped_count += 1
            else:
                target_config[config_key][name] = config
                merged_count += 1

        result = MCPDeployResult(
            merged_count=merged_count,
            skipped_count=skipped_count,
        )

        if merged_count > 0:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(json.dumps(target_config, indent=2) + "\n")
            result.created.append(target_path)
        elif skipped_count > 0:
            result.skipped.append(target_path)

        return result
