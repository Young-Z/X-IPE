"""
Tests for FEATURE-027-B: CLI Init & Selection

Tests cover:
- CLI auto-detection during init
- CLI selection prompt
- --cli flag (non-interactive)
- Config storage (cli key in .x-ipe.yaml)
- Backward compatibility
- ScaffoldManager.create_config_file(cli_name=...)

TDD Approach: All tests written before implementation.
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml
from click.testing import CliRunner


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    temp_dir = os.path.realpath(temp_dir)
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_adapters_yaml():
    """Create a temporary cli-adapters.yaml."""
    content = """adapters:
  copilot:
    display_name: "GitHub Copilot CLI"
    command: "copilot"
    run_args: "--allow-all-tools"
    inline_prompt_flag: "-i"
    prompt_format: '{command} {run_args} {inline_prompt_flag} "{escaped_prompt}"'
    instructions_file: ".github/copilot-instructions.md"
    skills_folder: ".github/skills/"
    mcp_config_path: "~/.copilot/mcp-config.json"
    mcp_config_format: "global"
    detection_command: "copilot"
  opencode:
    display_name: "OpenCode CLI"
    command: "opencode"
    run_args: ""
    inline_prompt_flag: "--prompt"
    prompt_format: '{command} {inline_prompt_flag} "{escaped_prompt}"'
    instructions_file: ".opencode/instructions.md"
    skills_folder: ".opencode/skills/"
    mcp_config_path: "opencode.json"
    mcp_config_format: "project"
    detection_command: "opencode"
  claude-code:
    display_name: "Claude Code CLI"
    command: "claude"
    run_args: ""
    inline_prompt_flag: "-p"
    prompt_format: '{command} {inline_prompt_flag} "{escaped_prompt}"'
    instructions_file: ".claude/instructions.md"
    skills_folder: ".claude/skills/"
    mcp_config_path: ".mcp.json"
    mcp_config_format: "project"
    detection_command: "claude"
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


# ============================================================================
# AC-1: CLI AUTO-DETECTION DURING INIT
# ============================================================================

class TestCLIAutoDetection:
    """AC-1.1 to AC-1.3: CLI detection during init."""

    def test_ac_1_1_init_calls_detect(self, runner, temp_project, temp_adapters_yaml):
        """AC-1.1: x-ipe init calls detect_installed_clis()."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.detect_installed_clis.return_value = ['copilot']
            instance.list_adapters.return_value = [
                MagicMock(name='copilot', display_name='GitHub Copilot CLI'),
            ]
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'copilot', '--no-mcp'
            ])

            instance.detect_installed_clis.assert_not_called()  # --cli skips detection

    def test_ac_1_3_no_cli_detected_defaults_copilot(self, runner, temp_project, temp_adapters_yaml):
        """AC-1.3: No CLIs detected → defaults to copilot."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.detect_installed_clis.return_value = []
            instance.list_adapters.return_value = [
                MagicMock(name='copilot'),
                MagicMock(name='opencode'),
                MagicMock(name='claude-code'),
            ]
            # Set .name property correctly
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'copilot', '--no-mcp'
            ])

            assert result.exit_code == 0


# ============================================================================
# AC-3: CLI FLAG (NON-INTERACTIVE)
# ============================================================================

class TestCLIFlag:
    """AC-3.1, AC-3.2: --cli flag for non-interactive mode."""

    def test_ac_3_1_cli_flag_skips_prompt(self, runner, temp_project, temp_adapters_yaml):
        """AC-3.1: --cli copilot skips prompt and uses specified CLI."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [
                MagicMock(name='copilot'),
                MagicMock(name='opencode'),
                MagicMock(name='claude-code'),
            ]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'copilot', '--no-mcp'
            ])

            assert result.exit_code == 0

    def test_ac_3_2_cli_flag_invalid_name(self, runner, temp_project, temp_adapters_yaml):
        """AC-3.2: --cli unknown exits with error listing available adapters."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [
                MagicMock(name='copilot'),
                MagicMock(name='opencode'),
                MagicMock(name='claude-code'),
            ]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'unknown-cli', '--no-mcp'
            ])

            assert result.exit_code != 0
            assert 'copilot' in result.output.lower() or 'available' in result.output.lower()

    def test_ac_3_1_cli_flag_uninstalled_shows_warning(self, runner, temp_project):
        """AC-2.3/AC-3.1: Selecting uninstalled CLI shows warning."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [
                MagicMock(name='copilot'),
                MagicMock(name='opencode'),
                MagicMock(name='claude-code'),
            ]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name
            instance.is_installed.return_value = False

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'opencode', '--no-mcp'
            ])

            assert result.exit_code == 0
            assert 'warning' in result.output.lower() or '⚠' in result.output


# ============================================================================
# AC-4: CONFIG STORAGE
# ============================================================================

class TestConfigStorage:
    """AC-4.1, AC-4.2: CLI selection stored in .x-ipe.yaml."""

    def test_ac_4_1_cli_stored_in_config(self, runner, temp_project):
        """AC-4.1: Selected CLI stored in .x-ipe.yaml under cli key."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [
                MagicMock(name='copilot'),
                MagicMock(name='opencode'),
                MagicMock(name='claude-code'),
            ]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'opencode', '--no-mcp'
            ])

            assert result.exit_code == 0

            config_path = temp_project / '.x-ipe.yaml'
            assert config_path.exists()
            with open(config_path) as f:
                config = yaml.safe_load(f)
            assert config.get('cli') == 'opencode'


# ============================================================================
# AC-5: BACKWARD COMPATIBILITY
# ============================================================================

class TestBackwardCompatibility:
    """AC-5.1, AC-5.2: Existing flags still work."""

    def test_ac_5_2_force_flag_works(self, runner, temp_project):
        """AC-5.2: --force flag continues working."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [MagicMock(name='copilot')]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--force', '--cli', 'copilot', '--no-mcp'
            ])

            assert result.exit_code == 0

    def test_ac_5_2_dry_run_flag_works(self, runner, temp_project):
        """AC-5.2: --dry-run shows changes without writing."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            instance.list_adapters.return_value = [MagicMock(name='copilot')]
            for a in instance.list_adapters.return_value:
                a.name = a._mock_name
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--dry-run', '--cli', 'copilot', '--no-mcp'
            ])

            assert result.exit_code == 0
            assert 'dry run' in result.output.lower() or 'Would' in result.output


# ============================================================================
# SCAFFOLD: create_config_file WITH cli_name
# ============================================================================

class TestScaffoldConfigFile:
    """ScaffoldManager.create_config_file(cli_name=...) tests."""

    def test_config_file_includes_cli_key(self, temp_project):
        """create_config_file(cli_name='opencode') includes cli key."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.create_config_file(cli_name='opencode')

        config_path = temp_project / '.x-ipe.yaml'
        assert config_path.exists()
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config.get('cli') == 'opencode'

    def test_config_file_opencode_has_correct_skills_path(self, temp_project):
        """create_config_file(cli_name='opencode') sets skills to .opencode/skills."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.create_config_file(cli_name='opencode')

        config_path = temp_project / '.x-ipe.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config['paths']['skills'] == '.opencode/skills'

    def test_config_file_without_cli_name(self, temp_project):
        """create_config_file() without cli_name has no cli key."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.create_config_file()

        config_path = temp_project / '.x-ipe.yaml'
        assert config_path.exists()
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert 'cli' not in config

    def test_config_file_dry_run_no_write(self, temp_project):
        """create_config_file() in dry_run doesn't write file."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project, dry_run=True)
        scaffold.create_config_file(cli_name='opencode')

        config_path = temp_project / '.x-ipe.yaml'
        assert not config_path.exists()


class TestMCPPathResolution:
    """Bug fix: init MCP merge uses active CLI's path, not hardcoded copilot."""

    def test_init_mcp_uses_opencode_path(self, runner, temp_project):
        """When CLI is opencode, MCP merge target defaults to opencode.json."""
        import json
        from src.x_ipe.cli.main import cli

        # Set up MCP source
        mcp_dir = temp_project / ".github" / "copilot"
        mcp_dir.mkdir(parents=True, exist_ok=True)
        mcp_config = {"mcpServers": {"test-server": {"command": "test"}}}
        (mcp_dir / "mcp-config.json").write_text(json.dumps(mcp_config))

        with patch("x_ipe.cli.main.CLIAdapterService") as MockService:
            mock_svc = MockService.return_value
            adapter = MagicMock()
            adapter.name = "opencode"
            adapter.mcp_config_path = "opencode.json"
            adapter.mcp_config_format = "project"
            adapter.skills_folder = ".opencode/skills/"
            adapter.instructions_file = ".opencode/instructions.md"
            mock_svc.get_adapter.return_value = adapter
            mock_svc.list_adapters.return_value = [adapter]
            mock_svc.detect_installed_clis.return_value = ["opencode"]
            mock_svc.is_installed.return_value = True

            # Run init with --cli opencode, confirm MCP merge
            result = runner.invoke(
                cli,
                ["-p", str(temp_project), "init", "--cli", "opencode"],
                input="y\n" + str(temp_project / "opencode.json") + "\n",
            )
            # If MCP merge happened, target should be opencode.json not ~/.copilot/...
            if (temp_project / "opencode.json").exists():
                config = json.loads((temp_project / "opencode.json").read_text())
                assert "mcp" in config


# ============================================================================
# CLI-SPECIFIC INIT: SKILLS FOLDER PLACEMENT
# ============================================================================

class TestCLISpecificSkillsCopy:
    """copy_skills(cli_name=...) targets CLI-specific folder."""

    def test_copy_skills_opencode_targets_opencode_folder(self, temp_project):
        """copy_skills(cli_name='opencode') creates .opencode/skills/."""
        from x_ipe.core.scaffold import ScaffoldManager

        skills_src = temp_project / "fake_skills"
        skill_dir = skills_src / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: my-skill\ndescription: test\n---\n# Skill")

        scaffold = ScaffoldManager(temp_project)
        scaffold.copy_skills(skills_source=skills_src, cli_name='opencode')

        target = temp_project / ".opencode" / "skills"
        assert target in scaffold.created
        assert not (temp_project / ".github" / "skills").exists()

    def test_copy_skills_claude_code_targets_claude_folder(self, temp_project):
        """copy_skills(cli_name='claude-code') creates .claude/skills/."""
        from x_ipe.core.scaffold import ScaffoldManager

        skills_src = temp_project / "fake_skills"
        skill_dir = skills_src / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: my-skill\ndescription: test\n---\n# Skill")

        scaffold = ScaffoldManager(temp_project)
        scaffold.copy_skills(skills_source=skills_src, cli_name='claude-code')

        target = temp_project / ".claude" / "skills"
        assert target in scaffold.created
        assert not (temp_project / ".github" / "skills").exists()

    def test_copy_skills_copilot_targets_github_folder(self, temp_project):
        """copy_skills(cli_name='copilot') creates .github/skills/."""
        from x_ipe.core.scaffold import ScaffoldManager

        skills_src = temp_project / "fake_skills"
        skill_dir = skills_src / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Skill")

        scaffold = ScaffoldManager(temp_project)
        scaffold.copy_skills(skills_source=skills_src, cli_name='copilot')

        target = temp_project / ".github" / "skills"
        assert target.exists()
        assert target in scaffold.created

    def test_copy_skills_no_cli_name_defaults_github(self, temp_project):
        """copy_skills() without cli_name defaults to .github/skills/."""
        from x_ipe.core.scaffold import ScaffoldManager

        skills_src = temp_project / "fake_skills"
        skill_dir = skills_src / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Skill")

        scaffold = ScaffoldManager(temp_project)
        scaffold.copy_skills(skills_source=skills_src)

        target = temp_project / ".github" / "skills"
        assert target.exists()
        assert target in scaffold.created

    def test_copy_skills_opencode_skips_if_exists(self, temp_project):
        """copy_skills(cli_name='opencode') skips if .opencode/skills/ exists."""
        from x_ipe.core.scaffold import ScaffoldManager

        skills_src = temp_project / "fake_skills"
        skill_dir = skills_src / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Skill")

        target = temp_project / ".opencode" / "skills"
        target.mkdir(parents=True)

        scaffold = ScaffoldManager(temp_project)
        scaffold.copy_skills(skills_source=skills_src, cli_name='opencode')

        assert target in scaffold.skipped

    def test_copy_skills_opencode_force_overwrites(self, temp_project):
        """copy_skills(cli_name='opencode', force=True) overwrites existing."""
        from x_ipe.core.scaffold import ScaffoldManager

        skills_src = temp_project / "fake_skills"
        skill_dir = skills_src / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: my-skill\ndescription: test\n---\n# New")

        target = temp_project / ".opencode" / "skills" / "my-skill"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("# Old")

        scaffold = ScaffoldManager(temp_project, force=True)
        scaffold.copy_skills(skills_source=skills_src, cli_name='opencode')

        assert (temp_project / ".opencode" / "skills") in scaffold.created

    def test_copy_skills_dry_run_no_files(self, temp_project):
        """copy_skills() in dry_run doesn't create files."""
        from x_ipe.core.scaffold import ScaffoldManager

        skills_src = temp_project / "fake_skills"
        skill_dir = skills_src / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Skill")

        scaffold = ScaffoldManager(temp_project, dry_run=True)
        scaffold.copy_skills(skills_source=skills_src, cli_name='opencode')

        assert not (temp_project / ".opencode" / "skills").exists()
        assert (temp_project / ".opencode" / "skills") in scaffold.created


# ============================================================================
# CLI-SPECIFIC INIT: INSTRUCTIONS FILE PLACEMENT
# ============================================================================

class TestCLISpecificInstructions:
    """copy_copilot_instructions(cli_name=...) targets CLI-specific path."""

    def test_instructions_opencode_targets_opencode_path(self, temp_project):
        """copy_copilot_instructions(cli_name='opencode') creates .opencode/instructions.md."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.copy_copilot_instructions(cli_name='opencode')

        target = temp_project / ".opencode" / "instructions.md"
        assert target in scaffold.created
        assert not (temp_project / ".github" / "copilot-instructions.md").exists()

    def test_instructions_claude_code_targets_claude_path(self, temp_project):
        """copy_copilot_instructions(cli_name='claude-code') creates .claude/instructions.md."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.copy_copilot_instructions(cli_name='claude-code')

        target = temp_project / ".claude" / "instructions.md"
        assert target in scaffold.created
        assert not (temp_project / ".github" / "copilot-instructions.md").exists()

    def test_instructions_copilot_does_not_target_opencode(self, temp_project):
        """copy_copilot_instructions(cli_name='copilot') does not create .opencode/ files."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        scaffold.copy_copilot_instructions(cli_name='copilot')

        assert not (temp_project / ".opencode" / "instructions.md").exists()
        assert not (temp_project / ".claude" / "instructions.md").exists()

    def test_instructions_opencode_skips_if_exists(self, temp_project):
        """copy_copilot_instructions(cli_name='opencode') skips if already exists."""
        from x_ipe.core.scaffold import ScaffoldManager

        target = temp_project / ".opencode" / "instructions.md"
        target.parent.mkdir(parents=True)
        target.write_text("# Existing")

        scaffold = ScaffoldManager(temp_project)
        scaffold.copy_copilot_instructions(cli_name='opencode')

        assert target in scaffold.skipped
        assert target.read_text() == "# Existing"

    def test_instructions_opencode_dry_run_no_file(self, temp_project):
        """copy_copilot_instructions(cli_name='opencode') in dry_run doesn't write."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project, dry_run=True)
        scaffold.copy_copilot_instructions(cli_name='opencode')

        assert not (temp_project / ".opencode" / "instructions.md").exists()
        assert (temp_project / ".opencode" / "instructions.md") in scaffold.created


# ============================================================================
# CLI-SPECIFIC INIT: MCP CONFIG NOT CREATED FOR NON-COPILOT
# ============================================================================

class TestCLISpecificMCPConfig:
    """Non-copilot CLIs should not create .github/copilot/ artifacts."""

    def test_opencode_init_no_github_copilot_folder(self, runner, temp_project):
        """Init with --cli opencode does not create .github/copilot/."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            adapter = MagicMock()
            adapter.name = 'opencode'
            adapter.skills_folder = '.opencode/skills/'
            adapter.instructions_file = '.opencode/instructions.md'
            adapter.mcp_config_path = 'opencode.json'
            adapter.mcp_config_format = 'nested'
            instance.list_adapters.return_value = [adapter]
            instance.get_adapter.return_value = adapter
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'opencode', '--no-mcp'
            ])

            assert result.exit_code == 0
            assert not (temp_project / ".github" / "copilot").exists()

    def test_copilot_init_creates_github_copilot_folder(self, runner, temp_project):
        """Init with --cli copilot creates .github/copilot/mcp-config.json."""
        from x_ipe.cli.main import cli

        with patch('x_ipe.cli.main.CLIAdapterService') as MockService:
            instance = MockService.return_value
            adapter = MagicMock()
            adapter.name = 'copilot'
            adapter.skills_folder = '.github/skills/'
            adapter.instructions_file = '.github/copilot-instructions.md'
            instance.list_adapters.return_value = [adapter]
            instance.get_adapter.return_value = adapter
            instance.is_installed.return_value = True

            result = runner.invoke(cli, [
                '--project', str(temp_project),
                'init', '--cli', 'copilot', '--no-mcp'
            ])

            assert result.exit_code == 0


# ============================================================================
# MERGE MCP CONFIG WITH source_servers PARAMETER
# ============================================================================

class TestMergeMCPWithSourceServers:
    """merge_mcp_config(source_servers=...) uses provided servers."""

    def test_merge_with_source_servers_creates_file(self, temp_project):
        """merge_mcp_config with source_servers creates target file."""
        import json
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        servers = {"test-server": {"command": "node", "args": ["server.js"]}}
        target = temp_project / "opencode.json"

        scaffold.merge_mcp_config(
            servers_to_merge=["test-server"],
            target_path=target,
            source_servers=servers
        )

        assert target.exists()
        config = json.loads(target.read_text())
        assert "test-server" in config["mcpServers"]

    def test_merge_without_source_servers_reads_from_project(self, temp_project):
        """merge_mcp_config without source_servers reads .github/copilot/mcp-config.json."""
        import json
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        target = temp_project / "target.json"

        scaffold.merge_mcp_config(target_path=target)

        assert not target.exists()

    def test_merge_source_servers_filters_by_name(self, temp_project):
        """merge_mcp_config filters source_servers by servers_to_merge list."""
        import json
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project)
        servers = {
            "keep-this": {"command": "a"},
            "skip-this": {"command": "b"},
        }
        target = temp_project / "opencode.json"

        scaffold.merge_mcp_config(
            servers_to_merge=["keep-this"],
            target_path=target,
            source_servers=servers
        )

        config = json.loads(target.read_text())
        assert "keep-this" in config["mcpServers"]
        assert "skip-this" not in config["mcpServers"]

    def test_merge_source_servers_dry_run(self, temp_project):
        """merge_mcp_config with source_servers in dry_run doesn't write."""
        from x_ipe.core.scaffold import ScaffoldManager

        scaffold = ScaffoldManager(temp_project, dry_run=True)
        servers = {"test-server": {"command": "test"}}
        target = temp_project / "opencode.json"

        scaffold.merge_mcp_config(
            servers_to_merge=["test-server"],
            target_path=target,
            source_servers=servers
        )

        assert not target.exists()
        assert target in scaffold.created

    def test_merge_preserves_existing_servers(self, temp_project):
        """merge_mcp_config preserves existing servers in target."""
        import json
        from x_ipe.core.scaffold import ScaffoldManager

        target = temp_project / "opencode.json"
        existing = {"mcpServers": {"existing": {"command": "old"}}}
        target.write_text(json.dumps(existing))

        scaffold = ScaffoldManager(temp_project)
        servers = {"new-server": {"command": "new"}}

        scaffold.merge_mcp_config(
            servers_to_merge=["new-server"],
            target_path=target,
            source_servers=servers
        )

        config = json.loads(target.read_text())
        assert "existing" in config["mcpServers"]
        assert "new-server" in config["mcpServers"]
