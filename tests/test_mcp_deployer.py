"""Tests for FEATURE-027-D: MCP Configuration Deployment.

Tests the MCPDeployerService which deploys MCP server configuration
to each CLI's native format and location.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

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
        run_args="--allow-all-tools --allow-all-paths",
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
        inline_prompt_flag="--prompt",
        prompt_format='{command} {inline_prompt_flag} "{escaped_prompt}"',
        instructions_file=".opencode/instructions.md",
        skills_folder=".opencode/skills/",
        mcp_config_path="opencode.json",
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
        inline_prompt_flag="--prompt",
        prompt_format='{command} {inline_prompt_flag} "{escaped_prompt}"',
        instructions_file=".claude/CLAUDE.md",
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
        assert path == project_root / "opencode.json"

    def test_ac_1_4_claude_project_path(self, project_root, claude_adapter):
        service = MCPDeployerService(project_root)
        path = service.resolve_target_path(claude_adapter)
        assert path == project_root / ".mcp.json"


class TestMCPConfigMerge:
    """AC-3: MCP Config Merge."""

    def test_ac_3_1_merges_servers_into_target(self, project_root, opencode_adapter):
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter)
        target = project_root / "opencode.json"
        assert target.exists()
        config = json.loads(target.read_text())
        assert config["$schema"] == "https://opencode.ai/config.json"
        assert "chrome-devtools" in config["mcp"]
        assert "github-mcp" in config["mcp"]
        # Verify opencode format: command is array, has enabled flag
        assert config["mcp"]["chrome-devtools"]["enabled"] is True
        assert isinstance(config["mcp"]["chrome-devtools"]["command"], list)

    def test_ac_3_2_creates_file_and_dirs(self, project_root, claude_adapter):
        service = MCPDeployerService(project_root)
        result = service.deploy(claude_adapter)
        target = project_root / ".mcp.json"
        assert target.exists()

    def test_ac_3_3_preserves_non_xipe_entries(self, project_root, opencode_adapter):
        target = project_root / "opencode.json"
        existing = {
            "mcp": {"my-custom-server": {"command": ["custom"], "type": "local", "enabled": True}},
            "otherKey": "preserved"
        }
        target.write_text(json.dumps(existing))
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter)
        config = json.loads(target.read_text())
        assert "my-custom-server" in config["mcp"]
        assert "chrome-devtools" in config["mcp"]
        assert config["otherKey"] == "preserved"

    def test_ac_3_4_malformed_target_creates_fresh(self, project_root, opencode_adapter):
        target = project_root / "opencode.json"
        target.write_text("broken json{{{")
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter)
        config = json.loads(target.read_text())
        assert "chrome-devtools" in config["mcp"]

    def test_ac_3_5_selective_merge(self, project_root, opencode_adapter):
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter, servers_to_merge=["chrome-devtools"])
        config = json.loads((project_root / "opencode.json").read_text())
        assert "chrome-devtools" in config["mcp"]
        assert "github-mcp" not in config["mcp"]

    def test_ac_3_6_skip_existing_without_force(self, project_root, opencode_adapter):
        target = project_root / "opencode.json"
        existing = {"mcp": {"chrome-devtools": {"command": ["old"], "type": "local", "enabled": True}}}
        target.write_text(json.dumps(existing))
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter, force=False)
        config = json.loads(target.read_text())
        assert config["mcp"]["chrome-devtools"]["command"] == ["old"]
        assert result.skipped_count >= 1

    def test_ac_3_6_overwrite_existing_with_force(self, project_root, opencode_adapter):
        target = project_root / "opencode.json"
        existing = {"mcp": {"chrome-devtools": {"command": ["old"], "type": "local", "enabled": True}}}
        target.write_text(json.dumps(existing))
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter, force=True)
        config = json.loads(target.read_text())
        assert isinstance(config["mcp"]["chrome-devtools"]["command"], list)
        assert config["mcp"]["chrome-devtools"]["command"][0] == "npx"
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
        target = project_root / "opencode.json"
        existing = {"theme": "dark", "editor": "vim", "mcp": {}}
        target.write_text(json.dumps(existing))
        service = MCPDeployerService(project_root)
        result = service.deploy(opencode_adapter)
        config = json.loads(target.read_text())
        assert config["theme"] == "dark"
        assert config["editor"] == "vim"
        assert "chrome-devtools" in config["mcp"]

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
        target = project_root / "opencode.json"
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


# ============================================================================
# FEATURE-027-F: CODEX TOML DEPLOYMENT TESTS
# ============================================================================

@pytest.fixture
def codex_adapter():
    return CLIAdapterData(
        name="codex",
        display_name="Codex CLI",
        command="codex",
        run_args="exec --dangerously-bypass-approvals-and-sandbox",
        inline_prompt_flag="",
        prompt_format='{command} {run_args} "{escaped_prompt}"',
        instructions_file="AGENTS.md",
        skills_folder=".codex/skills/",
        mcp_config_path="~/.codex/config.toml",
        mcp_config_format="codex-toml",
        detection_command="codex",
    )


def _fake_codex_run(calls, get_rc=1, add_rc=0, add_exc=None):
    """Build a subprocess.run mock that records calls and scripts results."""
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if "get" in cmd:
            return MagicMock(returncode=get_rc, stderr=b"", stdout=b"")
        if "add" in cmd:
            if add_exc is not None:
                raise add_exc
            return MagicMock(returncode=add_rc, stderr=b"" if add_rc == 0 else b"boom")
        return MagicMock(returncode=0, stderr=b"", stdout=b"")
    return fake_run


class TestCodexTomlDeploy:
    """FEATURE-027-F: codex-toml format deploys via `codex mcp add`."""

    def test_resolve_target_path_expands_home(self, tmp_path, codex_adapter):
        service = MCPDeployerService(tmp_path)
        assert service.resolve_target_path(codex_adapter) == Path("~/.codex/config.toml").expanduser()

    def test_deploy_adds_new_server(self, project_root, codex_adapter):
        """AC-3.1: server registered via `codex mcp add <name> -- <command> <args>`."""
        service = MCPDeployerService(project_root)
        calls = []
        with patch("shutil.which", return_value="/usr/local/bin/codex"), \
             patch("x_ipe.services.mcp_deployer_service.subprocess.run",
                   side_effect=_fake_codex_run(calls, get_rc=1, add_rc=0)):
            result = service.deploy(codex_adapter, servers_to_merge=["chrome-devtools"])

        assert result.merged_count == 1
        add_calls = [c for c in calls if "add" in c]
        assert len(add_calls) == 1
        assert add_calls[0][:4] == ["codex", "mcp", "add", "chrome-devtools"]
        assert add_calls[0][-3:] == ["--", "npx", "@anthropic/chrome-devtools-mcp"]

    def test_deploy_passes_env_flags(self, project_root, codex_adapter):
        """AC-3.1: env entries become --env KEY=VALUE flags."""
        service = MCPDeployerService(project_root)
        calls = []
        servers = {"fake": {"command": "npx", "args": ["srv"], "env": {"API_KEY": "secret"}}}
        with patch("shutil.which", return_value="/usr/local/bin/codex"), \
             patch("x_ipe.services.mcp_deployer_service.subprocess.run",
                   side_effect=_fake_codex_run(calls, get_rc=1, add_rc=0)):
            result = service.deploy(codex_adapter, source_servers=servers)

        assert result.merged_count == 1
        add_call = next(c for c in calls if "add" in c)
        assert "--env" in add_call
        assert "API_KEY=secret" in add_call

    def test_deploy_skips_existing_server(self, project_root, codex_adapter):
        """AC-3.2: existing server (mcp get rc 0) is skipped without force."""
        service = MCPDeployerService(project_root)
        calls = []
        with patch("shutil.which", return_value="/usr/local/bin/codex"), \
             patch("x_ipe.services.mcp_deployer_service.subprocess.run",
                   side_effect=_fake_codex_run(calls, get_rc=0)):
            result = service.deploy(codex_adapter, servers_to_merge=["chrome-devtools"])

        assert result.merged_count == 0
        assert result.skipped_count == 1
        assert not any("add" in c for c in calls)

    def test_deploy_force_removes_then_readds(self, project_root, codex_adapter):
        """AC-3.2: force removes the existing entry before re-adding."""
        service = MCPDeployerService(project_root)
        calls = []
        with patch("shutil.which", return_value="/usr/local/bin/codex"), \
             patch("x_ipe.services.mcp_deployer_service.subprocess.run",
                   side_effect=_fake_codex_run(calls, get_rc=0, add_rc=0)):
            result = service.deploy(codex_adapter, servers_to_merge=["chrome-devtools"], force=True)

        assert result.merged_count == 1
        assert any("remove" in c for c in calls)
        assert any("add" in c for c in calls)

    def test_deploy_not_installed_skips(self, project_root, codex_adapter):
        """AC-3.3: missing codex binary skips deployment without crashing."""
        service = MCPDeployerService(project_root)
        with patch("shutil.which", return_value=None), \
             patch("x_ipe.services.mcp_deployer_service.subprocess.run",
                   side_effect=AssertionError("must not invoke codex")):
            result = service.deploy(codex_adapter, servers_to_merge=["chrome-devtools"])

        assert result.merged_count == 0
        assert result.skipped == [Path("~/.codex/config.toml").expanduser()]

    def test_deploy_dry_run_does_not_invoke_codex(self, project_root, codex_adapter):
        """AC-3.5: dry-run reports intended registration without subprocess calls."""
        service = MCPDeployerService(project_root)
        with patch("shutil.which", return_value="/usr/local/bin/codex"), \
             patch("x_ipe.services.mcp_deployer_service.subprocess.run",
                   side_effect=AssertionError("dry-run must not invoke codex")):
            result = service.deploy(codex_adapter, servers_to_merge=["chrome-devtools"], dry_run=True)

        assert result.merged_count == 1
        assert result.created == [Path("~/.codex/config.toml").expanduser()]

    def test_deploy_failed_add_continues_remaining(self, project_root, codex_adapter):
        """EC-2: a failing server records an error; remaining servers still deploy."""
        service = MCPDeployerService(project_root)
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            if "get" in cmd:
                return MagicMock(returncode=1, stderr=b"", stdout=b"")
            if "add" in cmd:
                rc = 1 if "chrome-devtools" in cmd else 0
                return MagicMock(returncode=rc, stderr=b"boom" if rc else b"")
            return MagicMock(returncode=0, stderr=b"", stdout=b"")

        with patch("shutil.which", return_value="/usr/local/bin/codex"), \
             patch("x_ipe.services.mcp_deployer_service.subprocess.run", side_effect=fake_run):
            result = service.deploy(codex_adapter)

        assert result.merged_count == 1
        assert len(result.errors) == 1
        assert "chrome-devtools" in result.errors[0]

    def test_deploy_timeout_recorded(self, project_root, codex_adapter):
        """EC-2: subprocess timeout is recorded as an error, not raised."""
        import subprocess as sp
        service = MCPDeployerService(project_root)
        calls = []
        with patch("shutil.which", return_value="/usr/local/bin/codex"), \
             patch("x_ipe.services.mcp_deployer_service.subprocess.run",
                   side_effect=_fake_codex_run(calls, get_rc=1,
                                               add_exc=sp.TimeoutExpired(["codex"], 30))):
            result = service.deploy(codex_adapter, servers_to_merge=["chrome-devtools"])

        assert result.merged_count == 0
        assert len(result.errors) == 1
        assert "timed out" in result.errors[0]
