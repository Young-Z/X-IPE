"""MCP Configuration Deployment Service.

Deploys MCP server configuration to each CLI's native format and location,
reading target paths from the CLI adapter registry.
"""

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from x_ipe.services.cli_adapter_service import CLIAdapterData
from x_ipe.tracing import x_ipe_tracing

logger = logging.getLogger(__name__)

CODEX_TOML_FORMAT = "codex-toml"
SUBPROCESS_TIMEOUT = 30


@dataclass
class MCPDeployResult:
    """Result of an MCP deployment operation."""
    created: List[Path] = field(default_factory=list)
    skipped: List[Path] = field(default_factory=list)
    merged_count: int = 0
    skipped_count: int = 0
    errors: List[str] = field(default_factory=list)


class MCPDeployerService:
    """Deploys MCP server config to CLI-specific locations."""

    SOURCE_PATH = Path(".github") / "copilot" / "mcp-config.json"

    def __init__(self, project_root: Path):
        self.project_root = project_root

    @x_ipe_tracing()
    def get_source_servers(self) -> dict:
        """Read MCP servers from project's .github/copilot/mcp-config.json.

        Resolves ``${workspaceFolder}`` placeholders to ``self.project_root``.
        """
        source = self.project_root / self.SOURCE_PATH
        if not source.exists():
            return {}
        try:
            raw = source.read_text().replace(
                "${workspaceFolder}", str(self.project_root)
            )
            config = json.loads(raw)
            return config.get("mcpServers", {})
        except (json.JSONDecodeError, IOError):
            return {}

    @x_ipe_tracing()
    def resolve_target_path(self, adapter: CLIAdapterData) -> Path:
        """Resolve the target MCP config path based on adapter format."""
        raw = adapter.mcp_config_path
        if adapter.mcp_config_format in ("global", CODEX_TOML_FORMAT):
            return Path(raw).expanduser()
        return self.project_root / raw

    @x_ipe_tracing()
    def deploy(
        self,
        adapter: CLIAdapterData,
        servers_to_merge: Optional[List[str]] = None,
        force: bool = False,
        dry_run: bool = False,
        source_servers: Optional[dict] = None,
    ) -> MCPDeployResult:
        """Merge MCP servers into the target CLI's config file.

        Handles four MCP config formats:
        - "global": Standalone file with {"mcpServers": {...}} (copilot)
        - "project": Standalone file with {"mcpServers": {...}} (claude-code)
        - "nested": mcpServers key inside a larger config file (opencode)
        - "codex-toml": Global ~/.codex/config.toml, managed via `codex mcp add` (codex)

        Args:
            adapter: Target CLI adapter.
            servers_to_merge: Server names to deploy. If None, deploys all.
            force: Overwrite existing entries.
            dry_run: Report without writing.
            source_servers: Explicit server configs. If None, reads the
                project's .github/copilot/mcp-config.json (init passes the
                package-resource servers because the project file may not
                exist yet).
        """
        source_servers = source_servers if source_servers is not None else self.get_source_servers()
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

        if adapter.mcp_config_format == CODEX_TOML_FORMAT:
            return self._deploy_codex_cli(adapter, source_servers, force)

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
        else:
            # Standardize to standard MCP format for project/global targets
            # Strip Copilot-specific fields: "tools" and "type": "local"
            standardized = {}
            for name, cfg in source_servers.items():
                entry = {k: v for k, v in cfg.items() if k != "tools"}
                if entry.get("type") == "local":
                    del entry["type"]
                standardized[name] = entry
            source_servers = standardized

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
            target_path.write_text(json.dumps(target_config, indent=2, ensure_ascii=False) + "\n")
            result.created.append(target_path)
        elif skipped_count > 0:
            result.skipped.append(target_path)

        return result

    @x_ipe_tracing()
    def _deploy_codex_cli(
        self,
        adapter: CLIAdapterData,
        servers: dict,
        force: bool = False,
    ) -> MCPDeployResult:
        """Register MCP servers via the codex CLI (FEATURE-027-F).

        Codex keeps MCP servers in the global ~/.codex/config.toml shared with
        user settings, so we delegate to `codex mcp add` and let codex mutate
        its own config rather than rewriting the TOML file ourselves.

        Args:
            adapter: The codex CLI adapter.
            servers: Server configs (standard mcpServers entries).
            force: Re-register servers that already exist.

        Returns:
            MCPDeployResult with per-server merged/skipped counts.
        """
        result = MCPDeployResult()

        if shutil.which(adapter.detection_command) is None:
            logger.warning(
                "Codex CLI not installed — skipped MCP deployment to %s",
                adapter.mcp_config_path,
            )
            result.skipped.append(self.resolve_target_path(adapter))
            return result

        target_path = self.resolve_target_path(adapter)

        for name, cfg in servers.items():
            returncode, _ = self._run_codex(
                adapter, ["mcp", "get", name]
            )
            if returncode == 0 and not force:
                result.skipped_count += 1
                continue

            if returncode == 0:
                self._run_codex(adapter, ["mcp", "remove", name])

            args = ["mcp", "add", name]
            for key, value in (cfg.get("env") or {}).items():
                args += ["--env", f"{key}={value}"]
            args += ["--", cfg.get("command", "")] + list(cfg.get("args", []))

            add_code, stderr = self._run_codex(adapter, args)
            if add_code == 0:
                result.merged_count += 1
                if target_path not in result.created:
                    result.created.append(target_path)
            else:
                detail = stderr or f"exit code {add_code}"
                logger.warning("codex mcp add '%s' failed: %s", name, detail)
                result.errors.append(f"{name}: {detail}")

        return result

    @staticmethod
    def _run_codex(adapter: CLIAdapterData, args: List[str]) -> tuple[int, str]:
        """Run a codex CLI command, returning (returncode, stderr)."""
        try:
            proc = subprocess.run(
                [adapter.command] + args,
                capture_output=True,
                timeout=SUBPROCESS_TIMEOUT,
                check=False,
            )
            stderr = proc.stderr.decode(errors="replace").strip()
            return proc.returncode, stderr
        except subprocess.TimeoutExpired:
            return 124, f"timed out after {SUBPROCESS_TIMEOUT}s"
        except OSError as exc:
            return 1, str(exc)
