"""Tests for FEATURE-027-D: MCP Configuration Deployment.

Tests the MCPDeployerService which deploys MCP server configuration
to each CLI's native format and location.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from x_ipe.services.mcp_deployer_service import MCPDeployerService, MCPDeployResult
from x_ipe.services.cli_adapter_service import CLIAdapterData


@pytest.fixture
def project_root(tmp_path):
    """Create a project root with a source MCP config."""
    mcp_dir = tmp_path / ".github" / "copilot"
    mcp_dir.mkdir(parents=True)
    mcp_config = {
        "mcpServers": {
            "chrome-devtools": {
                "command": "npx",
                "args": ["@anthropic/chrome-devtools-mcp"]
            },
            "github-mcp": {
                "command": "npx",
                "args": ["@anthropic/github-mcp"]
            }
        }
    }
    (mcp_dir / "mcp-config.json").write_text(json.dumps(mcp_config, indent=2))
    return tmp_path


@pytest.fixture
def copilot_adapter():
    return CLIAdapterData(
        name="copilot",
        display_name="GitHub Copilot CLI",
        command="copilot",
        run_args="--allow-all-tools",
        inline_prompt_flag="-i",
        prompt_format='{command} {run_args} {inline_prompt_flag} "{escaped_prompt}"',
        instructions_file=".github/copilot-instructions.md",
        skills_folder=".github/skills/",
        mcp_config_path="~/.copilot/mcp-config.json",
        mcp_config_format="global",
        detection_command="copilot",
    )


@pytest.fixture
def opencode_adapter():
    return CLIAdapterData(
        name="opencode",
        display_name="OpenCode CLI",
        command="opencode",
        run_args="",
        inline_prompt_flag="-p",
        prompt_format='{command} {inline_prompt_flag} "{escaped_prompt}"',
        instructions_file=".opencode/instructions.md",
        skills_folder=".opencode/skills/",
        mcp_config_path=".opencode.json",
        mcp_config_format="nested",
        detection_command="opencode",
    )


@pytest.fixture
def claude_adapter():
    return CLIAdapterData(
        name="claude-code",
        display_name="Claude Code CLI",
        command="claude",
        run_args="",
        inline_prompt_flag="-p",
        prompt_format='{command} {inline_prompt_flag} "{escaped_prompt}"',
        instructions_file=".claude/instructions.md",
        skills_folder=".claude/skills/",
        mcp_config_path=".mcp.json",
        mcp_config_format="project",
        detection_command="claude",
    )


class TestSourceServerDiscovery:
    """AC-2: MCP Server Discovery."""

    def test_ac_2_1_discovers_servers_from_project(self, project_root):
        service = MCPDeployerService(project_root)
        servers = service.get_source_servers()
        assert "chrome-devtools" in servers
        assert "github-mcp" in servers

    def test_ac_2_2_returns_dict_format(self, project_root):
        service = MCPDeployerService(project_root)
        servers = service.get_source_servers()
        assert isinstance(servers, dict)
        assert servers["chrome-devtools"]["command"] == "npx"

    def test_ac_2_3_returns_empty_if_missing(self, tmp_path):
        service = MCPDeployerService(tmp_path)
        servers = service.get_source_servers()
        assert servers == {}

    def test_ac_2_3_returns_empty_if_malformed(self, tmp_path):
        mcp_dir = tmp_path / ".github" / "copilot"
        mcp_dir.mkdir(parents=True)
        (mcp_dir / "mcp-config.json").write_text("not json{{{")
        service = MCPDeployerService(tmp_path)
        servers = service.get_source_servers()
        assert servers == {}


class TestPathResolution:
    """AC-1: CLI-Aware MCP Path Resolution."""

    def test_ac_1_3_global_path_resolves_to_home(self, project_root, copilot_adapter):
        service = MCPDeployerService(project_root)
        path = service.resolve_target_path(copilot_adapter)
        assert path == Path.home() / ".copilot" / "mcp-config.json"

    def test_ac_1_4_project_path_resolves_to_project_root(self, project_root, opencode_adapter):
        service = MCPDeployerService(project_root)
        path = service.resolve_target_path(opencode_adapter)
        assert path == project_root / ".opencode.json"

    def test_ac_1_4_claude_project_path(self, project_root, claude_adapter):
        service = MCPDeployerService(project_root)
        path = service.resolve_target_path(claude_adapter)
        assert path == project_root / ".mcp.json"


class TestMCPConfigMerge:
    """AC-3: MCP Config Merge."""

    def test_ac_3_1_merges_servers_into_target(self, project_root, opencode_adapter):
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter)
        target = project_root / ".opencode.json"
        assert target.exists()
        config = json.loads(target.read_text())
        assert "chrome-devtools" in config["mcpServers"]
        assert "github-mcp" in config["mcpServers"]

    def test_ac_3_2_creates_file_and_dirs(self, project_root, claude_adapter):
        service = MCPDeployerService(project_root)
        result = service.deploy(claude_adapter)
        target = project_root / ".mcp.json"
        assert target.exists()

    def test_ac_3_3_preserves_non_xipe_entries(self, project_root, opencode_adapter):
        target = project_root / ".opencode.json"
        existing = {
            "mcpServers": {"my-custom-server": {"command": "custom"}},
            "otherKey": "preserved"
        }
        target.write_text(json.dumps(existing))
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter)
        config = json.loads(target.read_text())
        assert "my-custom-server" in config["mcpServers"]
        assert "chrome-devtools" in config["mcpServers"]
        assert config["otherKey"] == "preserved"

    def test_ac_3_4_malformed_target_creates_fresh(self, project_root, opencode_adapter):
        target = project_root / ".opencode.json"
        target.write_text("broken json{{{")
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter)
        config = json.loads(target.read_text())
        assert "chrome-devtools" in config["mcpServers"]

    def test_ac_3_5_selective_merge(self, project_root, opencode_adapter):
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter, servers_to_merge=["chrome-devtools"])
        config = json.loads((project_root / ".opencode.json").read_text())
        assert "chrome-devtools" in config["mcpServers"]
        assert "github-mcp" not in config["mcpServers"]

    def test_ac_3_6_skip_existing_without_force(self, project_root, opencode_adapter):
        target = project_root / ".opencode.json"
        existing = {"mcpServers": {"chrome-devtools": {"command": "old"}}}
        target.write_text(json.dumps(existing))
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter, force=False)
        config = json.loads(target.read_text())
        # Existing entry preserved
        assert config["mcpServers"]["chrome-devtools"]["command"] == "old"
        assert result.skipped_count >= 1

    def test_ac_3_6_overwrite_existing_with_force(self, project_root, opencode_adapter):
        target = project_root / ".opencode.json"
        existing = {"mcpServers": {"chrome-devtools": {"command": "old"}}}
        target.write_text(json.dumps(existing))
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter, force=True)
        config = json.loads(target.read_text())
        assert config["mcpServers"]["chrome-devtools"]["command"] == "npx"
        assert result.merged_count >= 1


class TestCLISpecificConfig:
    """AC-4: CLI-Specific Config Structure."""

    def test_ac_4_1_copilot_format(self, project_root, copilot_adapter, tmp_path):
        # Override to use tmp_path for global config instead of real home
        copilot_adapter.mcp_config_path = str(tmp_path / "copilot-mcp.json")
        copilot_adapter.mcp_config_format = "global"
        service = MCPDeployerService(project_root)
        # For global with absolute path, resolve_target_path should just expanduser
        with patch.object(service, 'resolve_target_path', return_value=tmp_path / "copilot-mcp.json"):
            result = service.deploy(copilot_adapter)
        config = json.loads((tmp_path / "copilot-mcp.json").read_text())
        assert "mcpServers" in config

    def test_ac_4_2_opencode_preserves_other_keys(self, project_root, opencode_adapter):
        target = project_root / ".opencode.json"
        existing = {"theme": "dark", "editor": "vim", "mcpServers": {}}
        target.write_text(json.dumps(existing))
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter)
        config = json.loads(target.read_text())
        assert config["theme"] == "dark"
        assert config["editor"] == "vim"
        assert "chrome-devtools" in config["mcpServers"]

    def test_ac_4_3_claude_code_format(self, project_root, claude_adapter):
        service = MCPDeployerService(project_root)
        result = service.deploy(claude_adapter)
        config = json.loads((project_root / ".mcp.json").read_text())
        assert "mcpServers" in config
        assert "chrome-devtools" in config["mcpServers"]


class TestDryRun:
    """AC-5: Dry Run Support."""

    def test_ac_5_1_no_files_written(self, project_root, opencode_adapter):
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter, dry_run=True)
        target = project_root / ".opencode.json"
        assert not target.exists()

    def test_ac_5_2_returns_what_would_change(self, project_root, opencode_adapter):
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter, dry_run=True)
        assert isinstance(result, MCPDeployResult)
        assert result.merged_count > 0


class TestMCPDeployResult:
    """MCPDeployResult dataclass."""

    def test_result_has_expected_fields(self):
        result = MCPDeployResult(
            created=[Path("/tmp/test.json")],
            skipped=[],
            merged_count=2,
            skipped_count=0,
        )
        assert len(result.created) == 1
        assert result.merged_count == 2
        assert result.skipped_count == 0
