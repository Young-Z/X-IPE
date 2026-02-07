"""
Tests for FEATURE-027-A: CLI Adapter Registry & Service

Tests cover:
- CLIAdapterData: Data model for adapter configuration
- CLIAdapterService: Load registry, detect CLIs, resolve active adapter, build commands
- API endpoint: GET /api/config/cli-adapter
- Edge cases: malformed YAML, unknown CLI, missing config, shell escaping

TDD Approach: All tests written before implementation.
"""
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


# ============================================================================
# FIXTURES
# ============================================================================

SAMPLE_ADAPTERS_YAML = """adapters:
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
    inline_prompt_flag: "run"
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


@pytest.fixture
def temp_adapters_yaml():
    """Create a temporary cli-adapters.yaml file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(SAMPLE_ADAPTERS_YAML)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_project_with_config():
    """Create temp project with .x-ipe.yaml containing cli key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_content = """version: 1
paths:
  project_root: "."
defaults:
  file_tree_scope: "project_root"
  terminal_cwd: "project_root"
cli: "opencode"
"""
        config_path = Path(tmpdir) / ".x-ipe.yaml"
        config_path.write_text(config_content)
        yield {
            'root': Path(tmpdir),
            'config_file': config_path,
        }


@pytest.fixture
def temp_project_no_cli_key():
    """Create temp project with .x-ipe.yaml without cli key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_content = """version: 1
paths:
  project_root: "."
defaults:
  file_tree_scope: "project_root"
"""
        config_path = Path(tmpdir) / ".x-ipe.yaml"
        config_path.write_text(config_content)
        yield {
            'root': Path(tmpdir),
            'config_file': config_path,
        }


@pytest.fixture
def temp_project_unknown_cli():
    """Create temp project with .x-ipe.yaml with unknown cli key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_content = """version: 1
paths:
  project_root: "."
cli: "unknown-cli"
"""
        config_path = Path(tmpdir) / ".x-ipe.yaml"
        config_path.write_text(config_content)
        yield {
            'root': Path(tmpdir),
            'config_file': config_path,
        }


@pytest.fixture
def cli_adapter_service(temp_adapters_yaml):
    """Create CLIAdapterService with temp adapters config."""
    from x_ipe.services.cli_adapter_service import CLIAdapterService
    return CLIAdapterService(config_file_path=temp_adapters_yaml)


# ============================================================================
# AC-1: ADAPTER CONFIGURATION TESTS
# ============================================================================

class TestAdapterConfiguration:
    """AC-1.1, AC-1.2, AC-1.3: cli-adapters.yaml structure and content."""

    def test_ac_1_1_config_file_loads_valid_yaml(self, cli_adapter_service):
        """AC-1.1: cli-adapters.yaml exists and is valid YAML."""
        adapters = cli_adapter_service.list_adapters()
        assert len(adapters) > 0

    def test_ac_1_2_each_adapter_has_all_required_fields(self, cli_adapter_service):
        """AC-1.2: Each adapter has all 10 required fields."""
        required_fields = [
            'display_name', 'command', 'run_args', 'inline_prompt_flag',
            'prompt_format', 'instructions_file', 'skills_folder',
            'mcp_config_path', 'mcp_config_format', 'detection_command'
        ]
        for adapter in cli_adapter_service.list_adapters():
            adapter_dict = adapter.to_dict()
            for field in required_fields:
                assert field in adapter_dict, f"Missing field '{field}' in adapter '{adapter.name}'"

    def test_ac_1_3_registry_includes_three_adapters(self, cli_adapter_service):
        """AC-1.3: Registry includes copilot, opencode, claude-code."""
        adapters = cli_adapter_service.list_adapters()
        names = [a.name for a in adapters]
        assert 'copilot' in names
        assert 'opencode' in names
        assert 'claude-code' in names

    def test_malformed_yaml_raises_error(self):
        """Edge case: malformed YAML raises error at init."""
        from x_ipe.services.cli_adapter_service import CLIAdapterService
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: [unclosed")
            f.flush()
            path = f.name
        try:
            with pytest.raises(Exception):
                CLIAdapterService(config_file_path=path)
        finally:
            os.unlink(path)

    def test_missing_config_file_raises_error(self):
        """Edge case: missing config file raises FileNotFoundError."""
        from x_ipe.services.cli_adapter_service import CLIAdapterService
        with pytest.raises(FileNotFoundError):
            CLIAdapterService(config_file_path="/nonexistent/cli-adapters.yaml")


# ============================================================================
# AC-2: SERVICE LAYER TESTS
# ============================================================================

class TestServiceLayer:
    """AC-2.1 to AC-2.5: CLIAdapterService methods."""

    def test_ac_2_1_get_active_adapter_returns_adapter(self, cli_adapter_service):
        """AC-2.1: get_active_adapter() returns adapter with all required fields."""
        # Without .x-ipe.yaml accessible, should fallback to copilot
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=None):
            with patch.object(cli_adapter_service, 'is_installed', return_value=False):
                adapter = cli_adapter_service.get_active_adapter()
                assert adapter.name == 'copilot'
                assert adapter.display_name is not None
                assert adapter.command is not None

    def test_ac_2_2_list_adapters_returns_all(self, cli_adapter_service):
        """AC-2.2: list_adapters() returns all 3 registered adapters."""
        adapters = cli_adapter_service.list_adapters()
        assert len(adapters) == 3
        names = [a.name for a in adapters]
        assert set(names) == {'copilot', 'opencode', 'claude-code'}

    def test_ac_2_3_detect_installed_clis(self, cli_adapter_service):
        """AC-2.3: detect_installed_clis() returns list of detected CLIs."""
        with patch('shutil.which', return_value=None):
            installed = cli_adapter_service.detect_installed_clis()
            assert isinstance(installed, list)
            assert len(installed) == 0

    def test_ac_2_3_detect_installed_clis_finds_copilot(self, cli_adapter_service):
        """AC-2.3: detect_installed_clis() finds copilot when installed."""
        def mock_which(cmd):
            return '/usr/local/bin/copilot' if cmd == 'copilot' else None

        with patch('shutil.which', side_effect=mock_which):
            installed = cli_adapter_service.detect_installed_clis()
            assert 'copilot' in installed

    def test_ac_2_4_switch_cli_updates_config(self, cli_adapter_service, temp_project_with_config):
        """AC-2.4: switch_cli() updates .x-ipe.yaml."""
        config_path = temp_project_with_config['config_file']
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=config_path):
            cli_adapter_service.switch_cli('claude-code')

        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config['cli'] == 'claude-code'

    def test_ac_2_5_switch_cli_invalid_name_raises(self, cli_adapter_service):
        """AC-2.5: switch_cli() raises ValueError for unknown adapter."""
        with pytest.raises(ValueError, match="Unknown CLI adapter"):
            cli_adapter_service.switch_cli('nonexistent-cli')


# ============================================================================
# AC-3: ACTIVE CLI SELECTION TESTS
# ============================================================================

class TestActiveCLISelection:
    """AC-3.1 to AC-3.3: Active CLI resolution logic."""

    def test_ac_3_1_active_cli_from_config(self, cli_adapter_service, temp_project_with_config):
        """AC-3.1: Active CLI read from .x-ipe.yaml 'cli' key."""
        config_path = temp_project_with_config['config_file']
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=config_path):
            adapter = cli_adapter_service.get_active_adapter()
            assert adapter.name == 'opencode'

    def test_ac_3_2_auto_detect_priority(self, cli_adapter_service, temp_project_no_cli_key):
        """AC-3.2: Without cli key, auto-detect with Copilot > OpenCode > Claude."""
        config_path = temp_project_no_cli_key['config_file']

        def mock_which(cmd):
            # Only opencode is installed
            return '/usr/local/bin/opencode' if cmd == 'opencode' else None

        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=config_path):
            with patch('shutil.which', side_effect=mock_which):
                adapter = cli_adapter_service.get_active_adapter()
                assert adapter.name == 'opencode'

    def test_ac_3_2_auto_detect_copilot_first(self, cli_adapter_service, temp_project_no_cli_key):
        """AC-3.2: Copilot wins when both copilot and opencode are installed."""
        config_path = temp_project_no_cli_key['config_file']

        def mock_which(cmd):
            return f'/usr/local/bin/{cmd}' if cmd in ('copilot', 'opencode') else None

        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=config_path):
            with patch('shutil.which', side_effect=mock_which):
                adapter = cli_adapter_service.get_active_adapter()
                assert adapter.name == 'copilot'

    def test_ac_3_3_default_to_copilot_when_none_detected(self, cli_adapter_service):
        """AC-3.3: Default to copilot when no CLI detected and no config."""
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=None):
            with patch('shutil.which', return_value=None):
                adapter = cli_adapter_service.get_active_adapter()
                assert adapter.name == 'copilot'

    def test_unknown_cli_in_config_raises(self, cli_adapter_service, temp_project_unknown_cli):
        """Edge case: unknown cli value in .x-ipe.yaml raises ValueError."""
        config_path = temp_project_unknown_cli['config_file']
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=config_path):
            with pytest.raises(ValueError, match="Unknown CLI adapter"):
                cli_adapter_service.get_active_adapter()


# ============================================================================
# AC-4: API ENDPOINT TESTS
# ============================================================================

class TestAPIEndpoint:
    """AC-4.1, AC-4.2: GET /api/config/cli-adapter."""

    @pytest.fixture
    def app(self, temp_adapters_yaml):
        """Create Flask test app with CLI adapter service."""
        from flask import Flask
        from x_ipe.services.cli_adapter_service import CLIAdapterService
        from x_ipe.routes.config_routes import config_bp

        app = Flask(__name__)
        app.config['TESTING'] = True

        service = CLIAdapterService(config_file_path=temp_adapters_yaml)
        app.config['CLI_ADAPTER_SERVICE'] = service

        app.register_blueprint(config_bp)
        return app

    @pytest.fixture
    def client(self, app):
        """Flask test client."""
        return app.test_client()

    def test_ac_4_1_get_cli_adapter_returns_json(self, client):
        """AC-4.1: GET /api/config/cli-adapter returns active adapter info."""
        with patch('shutil.which', return_value=None):
            response = client.get('/api/config/cli-adapter')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'adapter_name' in data

    def test_ac_4_2_response_has_required_fields(self, client):
        """AC-4.2: Response includes all 5 required fields."""
        with patch('shutil.which', return_value=None):
            response = client.get('/api/config/cli-adapter')
            data = response.get_json()
            assert 'adapter_name' in data
            assert 'display_name' in data
            assert 'command' in data
            assert 'prompt_format' in data
            assert 'is_installed' in data

    def test_no_service_returns_503(self):
        """Edge case: No service configured returns 503."""
        from flask import Flask
        from x_ipe.routes.config_routes import config_bp

        app = Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(config_bp)
        client = app.test_client()

        response = client.get('/api/config/cli-adapter')
        assert response.status_code == 503


# ============================================================================
# AC-5: PROMPT ESCAPING TESTS
# ============================================================================

class TestPromptEscaping:
    """AC-5.1 to AC-5.3: build_command() prompt escaping."""

    def test_ac_5_1_escapes_double_quotes(self, cli_adapter_service):
        """AC-5.1: build_command() escapes double quotes."""
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=None):
            with patch('shutil.which', return_value=None):
                cmd = cli_adapter_service.build_command('say "hello"')
                assert '\\"hello\\"' in cmd

    def test_ac_5_2_escapes_backticks_and_dollar(self, cli_adapter_service):
        """AC-5.2: build_command() escapes backticks, dollar signs, newlines."""
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=None):
            with patch('shutil.which', return_value=None):
                cmd = cli_adapter_service.build_command('run `ls` and $HOME\nnewline')
                assert '\\`ls\\`' in cmd
                assert '\\$HOME' in cmd
                assert '\\n' in cmd

    def test_ac_5_3_uses_adapter_prompt_format(self, cli_adapter_service):
        """AC-5.3: Command uses the adapter's prompt_format template."""
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=None):
            with patch('shutil.which', return_value=None):
                # Default is copilot: '{command} {run_args} {inline_prompt_flag} "{escaped_prompt}"'
                cmd = cli_adapter_service.build_command('fix bug')
                assert cmd.startswith('copilot')
                assert '--allow-all-tools' in cmd
                assert '-i' in cmd

    def test_empty_prompt(self, cli_adapter_service):
        """Edge case: Empty prompt produces valid command."""
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=None):
            with patch('shutil.which', return_value=None):
                cmd = cli_adapter_service.build_command('')
                assert 'copilot' in cmd


# ============================================================================
# AC-6: BACKWARD COMPATIBILITY TESTS
# ============================================================================

class TestBackwardCompatibility:
    """AC-6.1, AC-6.2: Existing Copilot projects work without changes."""

    def test_ac_6_1_works_without_cli_key(self, cli_adapter_service):
        """AC-6.1: Service works without .x-ipe.yaml cli key (defaults to copilot)."""
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=None):
            with patch('shutil.which', return_value=None):
                adapter = cli_adapter_service.get_active_adapter()
                assert adapter.name == 'copilot'

    def test_ac_6_2_copilot_adapter_has_correct_paths(self, cli_adapter_service):
        """AC-6.2: Copilot adapter uses .github/skills/ and copilot-instructions.md."""
        adapters = cli_adapter_service.list_adapters()
        copilot = next(a for a in adapters if a.name == 'copilot')
        assert copilot.skills_folder == '.github/skills/'
        assert 'copilot-instructions.md' in copilot.instructions_file


# ============================================================================
# CLIADAPTERDATA UNIT TESTS
# ============================================================================

class TestCLIAdapterData:
    """Unit tests for the CLIAdapterData dataclass."""

    def test_to_dict_returns_all_fields(self, cli_adapter_service):
        """to_dict() returns dictionary with all fields."""
        adapter = cli_adapter_service.list_adapters()[0]
        d = adapter.to_dict()
        assert isinstance(d, dict)
        assert 'name' in d
        assert 'display_name' in d
        assert 'command' in d

    def test_adapter_is_immutable_dataclass(self, cli_adapter_service):
        """Adapter instances are dataclass objects."""
        adapter = cli_adapter_service.list_adapters()[0]
        assert hasattr(adapter, 'name')
        assert hasattr(adapter, 'command')
        assert hasattr(adapter, 'prompt_format')


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for end-to-end flows."""

    def test_switch_then_get_active(self, cli_adapter_service, temp_project_with_config):
        """Switch CLI then verify get_active_adapter returns new adapter."""
        config_path = temp_project_with_config['config_file']
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=config_path):
            cli_adapter_service.switch_cli('claude-code')
            adapter = cli_adapter_service.get_active_adapter()
            assert adapter.name == 'claude-code'

    def test_build_command_for_each_adapter(self, cli_adapter_service, temp_project_with_config):
        """Build command works correctly for each adapter type."""
        config_path = temp_project_with_config['config_file']

        for adapter_name in ['copilot', 'opencode', 'claude-code']:
            with patch.object(cli_adapter_service, '_find_config_yaml', return_value=config_path):
                cli_adapter_service.switch_cli(adapter_name)
                cmd = cli_adapter_service.build_command('test prompt')
                adapter = cli_adapter_service.get_active_adapter()
                assert adapter.command in cmd

    def test_switch_cli_no_config_file_raises(self, cli_adapter_service):
        """switch_cli() raises when no .x-ipe.yaml exists."""
        with patch.object(cli_adapter_service, '_find_config_yaml', return_value=None):
            with pytest.raises(FileNotFoundError):
                cli_adapter_service.switch_cli('opencode')

    def test_is_installed_unknown_adapter(self, cli_adapter_service):
        """is_installed() returns False for unknown adapter name."""
        assert cli_adapter_service.is_installed('nonexistent') is False
