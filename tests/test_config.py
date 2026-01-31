"""
Tests for FEATURE-010: Project Root Configuration

Tests cover:
- ConfigData: Data model for config values
- ConfigService: Discovery, parsing, and validation of .x-ipe.yaml
- API endpoint: GET /api/config
- Integration: ProjectService and SessionManager using config

TDD Approach: All tests written before implementation.
"""
import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_project_structure():
    """Create a temporary project structure with .x-ipe.yaml"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create x-ipe subfolder
        x_ipe_app = project_root / "x-ipe"
        x_ipe_app.mkdir()
        (x_ipe_app / "main.py").write_text("# X-IPE main")
        
        # Create config file
        config_content = """version: 1
paths:
  project_root: "."
  x_ipe_app: "./x-ipe"
defaults:
  file_tree_scope: "project_root"
  terminal_cwd: "project_root"
"""
        (project_root / ".x-ipe.yaml").write_text(config_content)
        
        yield {
            'root': project_root,
            'x_ipe_app': x_ipe_app,
            'config_file': project_root / ".x-ipe.yaml"
        }


@pytest.fixture
def temp_nested_structure():
    """Create nested directory structure for parent traversal tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create nested structure: project/x-ipe/subdir/
        x_ipe_app = project_root / "x-ipe"
        subdir = x_ipe_app / "subdir"
        subdir.mkdir(parents=True)
        (x_ipe_app / "main.py").write_text("# X-IPE main")
        
        # Config at project root
        config_content = """version: 1
paths:
  project_root: "."
  x_ipe_app: "./x-ipe"
defaults:
  file_tree_scope: "project_root"
  terminal_cwd: "x_ipe_app"
"""
        (project_root / ".x-ipe.yaml").write_text(config_content)
        
        yield {
            'root': project_root,
            'x_ipe_app': x_ipe_app,
            'subdir': subdir,
            'config_file': project_root / ".x-ipe.yaml"
        }


@pytest.fixture
def temp_dir_no_config():
    """Create temporary directory without config file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def config_service(temp_project_structure):
    """Create ConfigService with temp project"""
    from x_ipe.services import ConfigService
    return ConfigService(str(temp_project_structure['x_ipe_app']))


# ============================================================================
# CONFIGDATA UNIT TESTS
# ============================================================================

class TestConfigDataUnit:
    """Unit tests for ConfigData dataclass"""

    def test_config_data_stores_all_fields(self, temp_project_structure):
        """ConfigData stores all configuration fields"""
        from x_ipe.services import ConfigData
        
        config = ConfigData(
            config_file_path=str(temp_project_structure['config_file']),
            version=1,
            project_root=str(temp_project_structure['root']),
            x_ipe_app=str(temp_project_structure['x_ipe_app']),
            file_tree_scope="project_root",
            terminal_cwd="project_root"
        )
        
        assert config.config_file_path == str(temp_project_structure['config_file'])
        assert config.version == 1
        assert config.project_root == str(temp_project_structure['root'])
        assert config.x_ipe_app == str(temp_project_structure['x_ipe_app'])
        assert config.file_tree_scope == "project_root"
        assert config.terminal_cwd == "project_root"

    def test_get_file_tree_path_returns_project_root(self, temp_project_structure):
        """get_file_tree_path() returns project_root when file_tree_scope is 'project_root'"""
        from x_ipe.services import ConfigData
        
        config = ConfigData(
            config_file_path=str(temp_project_structure['config_file']),
            version=1,
            project_root=str(temp_project_structure['root']),
            x_ipe_app=str(temp_project_structure['x_ipe_app']),
            file_tree_scope="project_root",
            terminal_cwd="project_root"
        )
        
        assert config.get_file_tree_path() == str(temp_project_structure['root'])

    def test_get_file_tree_path_returns_x_ipe_app(self, temp_project_structure):
        """get_file_tree_path() returns x_ipe_app when file_tree_scope is 'x_ipe_app'"""
        from x_ipe.services import ConfigData
        
        config = ConfigData(
            config_file_path=str(temp_project_structure['config_file']),
            version=1,
            project_root=str(temp_project_structure['root']),
            x_ipe_app=str(temp_project_structure['x_ipe_app']),
            file_tree_scope="x_ipe_app",
            terminal_cwd="project_root"
        )
        
        assert config.get_file_tree_path() == str(temp_project_structure['x_ipe_app'])

    def test_get_terminal_cwd_returns_project_root(self, temp_project_structure):
        """get_terminal_cwd() returns project_root when terminal_cwd is 'project_root'"""
        from x_ipe.services import ConfigData
        
        config = ConfigData(
            config_file_path=str(temp_project_structure['config_file']),
            version=1,
            project_root=str(temp_project_structure['root']),
            x_ipe_app=str(temp_project_structure['x_ipe_app']),
            file_tree_scope="project_root",
            terminal_cwd="project_root"
        )
        
        assert config.get_terminal_cwd() == str(temp_project_structure['root'])

    def test_get_terminal_cwd_returns_x_ipe_app(self, temp_project_structure):
        """get_terminal_cwd() returns x_ipe_app when terminal_cwd is 'x_ipe_app'"""
        from x_ipe.services import ConfigData
        
        config = ConfigData(
            config_file_path=str(temp_project_structure['config_file']),
            version=1,
            project_root=str(temp_project_structure['root']),
            x_ipe_app=str(temp_project_structure['x_ipe_app']),
            file_tree_scope="project_root",
            terminal_cwd="x_ipe_app"
        )
        
        assert config.get_terminal_cwd() == str(temp_project_structure['x_ipe_app'])

    def test_to_dict_returns_complete_dict(self, temp_project_structure):
        """to_dict() returns dictionary with all fields"""
        from x_ipe.services import ConfigData
        
        config = ConfigData(
            config_file_path=str(temp_project_structure['config_file']),
            version=1,
            project_root=str(temp_project_structure['root']),
            x_ipe_app=str(temp_project_structure['x_ipe_app']),
            file_tree_scope="project_root",
            terminal_cwd="x_ipe_app"
        )
        
        result = config.to_dict()
        
        assert isinstance(result, dict)
        assert result['config_file'] == str(temp_project_structure['config_file'])
        assert result['version'] == 1
        assert result['project_root'] == str(temp_project_structure['root'])
        assert result['x_ipe_app'] == str(temp_project_structure['x_ipe_app'])
        assert result['file_tree_scope'] == "project_root"
        assert result['terminal_cwd'] == "x_ipe_app"


# ============================================================================
# CONFIGSERVICE DISCOVERY TESTS
# ============================================================================

class TestConfigServiceDiscovery:
    """Tests for ConfigService._discover() method"""

    def test_discover_finds_config_in_cwd(self, temp_project_structure):
        """_discover() finds .x-ipe.yaml in current directory"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        config_path = service._discover()
        
        assert config_path is not None
        assert config_path.name == ".x-ipe.yaml"

    def test_discover_finds_config_in_parent(self, temp_nested_structure):
        """_discover() finds .x-ipe.yaml in parent directory"""
        from x_ipe.services import ConfigService
        
        # Start from subdir, should find config in project root
        service = ConfigService(str(temp_nested_structure['subdir']))
        config_path = service._discover()
        
        assert config_path is not None
        # Use resolve() for consistent path comparison on macOS
        assert config_path.resolve() == temp_nested_structure['config_file'].resolve()

    def test_discover_returns_none_when_not_found(self, temp_dir_no_config):
        """_discover() returns None when no config file exists"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_dir_no_config))
        config_path = service._discover()
        
        assert config_path is None

    def test_discover_stops_at_20_levels(self):
        """_discover() stops searching after 20 parent levels"""
        from x_ipe.services import ConfigService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create deeply nested structure (25 levels)
            deep_path = Path(tmpdir)
            for i in range(25):
                deep_path = deep_path / f"level{i}"
            deep_path.mkdir(parents=True)
            
            service = ConfigService(str(deep_path))
            # Should not find config (no config exists anyway)
            # But important: should not crash or hang
            config_path = service._discover()
            
            assert config_path is None

    def test_discover_stops_at_filesystem_root(self, temp_dir_no_config):
        """_discover() stops at filesystem root"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_dir_no_config))
        # Should complete without infinite loop
        config_path = service._discover()
        
        # Just verify it returns (doesn't hang)
        assert config_path is None or isinstance(config_path, Path)


# ============================================================================
# CONFIGSERVICE PARSING TESTS
# ============================================================================

class TestConfigServiceParsing:
    """Tests for ConfigService._parse() method"""

    def test_parse_valid_yaml_returns_dict(self, temp_project_structure):
        """_parse() returns parsed dict for valid YAML"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        result = service._parse(temp_project_structure['config_file'])
        
        assert isinstance(result, dict)
        assert result['version'] == 1
        assert 'paths' in result
        assert 'defaults' in result

    def test_parse_invalid_yaml_returns_none(self):
        """_parse() returns None for invalid YAML"""
        from x_ipe.services import ConfigService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".x-ipe.yaml"
            config_file.write_text("invalid: yaml: content: [")
            
            service = ConfigService(tmpdir)
            result = service._parse(config_file)
            
            assert result is None
            assert service.error is not None

    def test_parse_nonexistent_file_returns_none(self, temp_dir_no_config):
        """_parse() returns None for non-existent file"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_dir_no_config))
        fake_path = temp_dir_no_config / "nonexistent.yaml"
        result = service._parse(fake_path)
        
        assert result is None
        assert service.error is not None

    def test_parse_empty_file_returns_none(self):
        """_parse() handles empty YAML file"""
        from x_ipe.services import ConfigService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".x-ipe.yaml"
            config_file.write_text("")
            
            service = ConfigService(tmpdir)
            result = service._parse(config_file)
            
            # Empty YAML returns None
            assert result is None


# ============================================================================
# CONFIGSERVICE VALIDATION TESTS
# ============================================================================

class TestConfigServiceValidation:
    """Tests for ConfigService._validate() method"""

    def test_validate_valid_config_returns_config_data(self, temp_project_structure):
        """_validate() returns ConfigData for valid config"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 1,
            'paths': {
                'project_root': '.',
                'x_ipe_app': './x-ipe'
            },
            'defaults': {
                'file_tree_scope': 'project_root',
                'terminal_cwd': 'project_root'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is not None
        assert result.version == 1

    def test_validate_missing_version_fails(self, temp_project_structure):
        """_validate() fails when version is missing"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'paths': {
                'project_root': '.',
                'x_ipe_app': './x-ipe'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is None
        assert 'version' in service.error.lower()

    def test_validate_wrong_version_fails(self, temp_project_structure):
        """_validate() fails when version is not 1"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 99,
            'paths': {
                'project_root': '.',
                'x_ipe_app': './x-ipe'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is None
        assert 'version' in service.error.lower()

    def test_validate_missing_project_root_fails(self, temp_project_structure):
        """_validate() fails when paths.project_root is missing"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 1,
            'paths': {
                'x_ipe_app': './x-ipe'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is None
        assert 'project_root' in service.error.lower()

    def test_validate_missing_x_ipe_app_uses_default(self, temp_project_structure):
        """_validate() uses project_root as default when paths.x_ipe_app is missing"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 1,
            'paths': {
                'project_root': '.'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        # x_ipe_app is now optional - defaults to project_root
        assert result is not None
        assert result.x_ipe_app == result.project_root

    def test_validate_nonexistent_project_root_fails(self, temp_project_structure):
        """_validate() fails when project_root path doesn't exist"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 1,
            'paths': {
                'project_root': './nonexistent',
                'x_ipe_app': './x-ipe'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is None
        assert 'exist' in service.error.lower()

    def test_validate_nonexistent_x_ipe_app_fails(self, temp_project_structure):
        """_validate() fails when x_ipe_app path doesn't exist"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 1,
            'paths': {
                'project_root': '.',
                'x_ipe_app': './nonexistent'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is None
        assert 'exist' in service.error.lower()

    def test_validate_file_instead_of_dir_fails(self, temp_project_structure):
        """_validate() fails when path is file instead of directory"""
        from x_ipe.services import ConfigService
        
        # Create a file instead of directory
        file_path = temp_project_structure['root'] / "not_a_dir"
        file_path.write_text("I am a file")
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 1,
            'paths': {
                'project_root': '.',
                'x_ipe_app': './not_a_dir'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is None

    def test_validate_invalid_file_tree_scope_fails(self, temp_project_structure):
        """_validate() fails when file_tree_scope is invalid"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 1,
            'paths': {
                'project_root': '.',
                'x_ipe_app': './x-ipe'
            },
            'defaults': {
                'file_tree_scope': 'invalid_value'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is None
        assert 'file_tree_scope' in service.error.lower()

    def test_validate_invalid_terminal_cwd_fails(self, temp_project_structure):
        """_validate() fails when terminal_cwd is invalid"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 1,
            'paths': {
                'project_root': '.',
                'x_ipe_app': './x-ipe'
            },
            'defaults': {
                'file_tree_scope': 'project_root',
                'terminal_cwd': 'invalid_value'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is None
        assert 'terminal_cwd' in service.error.lower()

    def test_validate_resolves_relative_paths(self, temp_project_structure):
        """_validate() resolves relative paths to absolute"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 1,
            'paths': {
                'project_root': '.',
                'x_ipe_app': './x-ipe'
            }
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is not None
        assert os.path.isabs(result.project_root)
        assert os.path.isabs(result.x_ipe_app)

    def test_validate_defaults_optional_fields(self, temp_project_structure):
        """_validate() uses defaults for optional fields"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        raw = {
            'version': 1,
            'paths': {
                'project_root': '.',
                'x_ipe_app': './x-ipe'
            }
            # No 'defaults' section
        }
        
        result = service._validate(temp_project_structure['config_file'], raw)
        
        assert result is not None
        assert result.file_tree_scope == "project_root"
        assert result.terminal_cwd == "project_root"


# ============================================================================
# CONFIGSERVICE LOAD INTEGRATION TESTS
# ============================================================================

class TestConfigServiceLoad:
    """Tests for ConfigService.load() method (full integration)"""

    def test_load_returns_config_data_when_valid(self, temp_project_structure):
        """load() returns ConfigData when config is valid"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        result = service.load()
        
        assert result is not None
        assert result.version == 1
        assert result.file_tree_scope == "project_root"

    def test_load_returns_none_when_no_config(self, temp_dir_no_config):
        """load() returns None when no config file exists"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_dir_no_config))
        result = service.load()
        
        assert result is None

    def test_load_stores_config_in_property(self, temp_project_structure):
        """load() stores result in config property"""
        from x_ipe.services import ConfigService
        
        service = ConfigService(str(temp_project_structure['root']))
        result = service.load()
        
        assert service.config == result

    def test_load_from_nested_directory(self, temp_nested_structure):
        """load() finds config when started from nested directory"""
        from x_ipe.services import ConfigService
        
        # Start from x-ipe subdir
        service = ConfigService(str(temp_nested_structure['subdir']))
        result = service.load()
        
        assert result is not None
        assert result.terminal_cwd == "x_ipe_app"  # As per fixture

    def test_error_property_contains_message_on_failure(self):
        """error property contains error message on validation failure"""
        from x_ipe.services import ConfigService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create invalid config
            config_file = Path(tmpdir) / ".x-ipe.yaml"
            config_file.write_text("version: 99")
            
            service = ConfigService(tmpdir)
            result = service.load()
            
            assert result is None
            assert service.error is not None
            assert len(service.error) > 0


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestConfigAPIEndpoint:
    """Tests for GET /api/config endpoint"""

    @pytest.fixture
    def app_with_config(self, temp_project_structure):
        """Create Flask app with config loaded"""
        from src.app import create_app
        from x_ipe.services import ConfigService
        
        app = create_app()
        app.config['TESTING'] = True
        
        # Load config
        config_service = ConfigService(str(temp_project_structure['root']))
        config_data = config_service.load()
        app.config['X_IPE_CONFIG'] = config_data
        app.config['PROJECT_ROOT'] = config_data.get_file_tree_path() if config_data else str(temp_project_structure['root'])
        
        return app

    @pytest.fixture
    def app_without_config(self, temp_dir_no_config):
        """Create Flask app without config"""
        from src.app import create_app
        
        app = create_app()
        app.config['TESTING'] = True
        app.config['X_IPE_CONFIG'] = None
        app.config['PROJECT_ROOT'] = str(temp_dir_no_config)
        
        return app

    @pytest.fixture
    def client_with_config(self, app_with_config):
        """Flask test client with config"""
        return app_with_config.test_client()

    @pytest.fixture
    def client_without_config(self, app_without_config):
        """Flask test client without config"""
        return app_without_config.test_client()

    def test_get_config_returns_200(self, client_with_config):
        """GET /api/config returns 200 status"""
        response = client_with_config.get('/api/config')
        
        assert response.status_code == 200

    def test_get_config_returns_json(self, client_with_config):
        """GET /api/config returns JSON content type"""
        response = client_with_config.get('/api/config')
        
        assert 'application/json' in response.content_type

    def test_get_config_with_detected_config(self, client_with_config):
        """GET /api/config returns config details when detected"""
        response = client_with_config.get('/api/config')
        data = json.loads(response.data)
        
        assert data['detected'] is True
        assert data['config_file'] is not None
        assert data['version'] == 1
        assert 'project_root' in data
        assert 'x_ipe_app' in data
        assert 'file_tree_scope' in data
        assert 'terminal_cwd' in data

    def test_get_config_without_config_file(self, client_without_config):
        """GET /api/config returns defaults when no config detected"""
        response = client_without_config.get('/api/config')
        data = json.loads(response.data)
        
        assert data['detected'] is False
        assert data['config_file'] is None
        assert data['using_defaults'] is True
        assert 'project_root' in data


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestConfigIntegration:
    """Integration tests for config with other services"""

    def test_project_service_uses_config_path(self, temp_project_structure):
        """ProjectService uses configured project_root path"""
        from x_ipe.services import ConfigService, ProjectService
        
        config_service = ConfigService(str(temp_project_structure['x_ipe_app']))
        config_data = config_service.load()
        
        # Use config's file tree path
        project_root = config_data.get_file_tree_path()
        project_service = ProjectService(project_root)
        
        assert project_service.project_root == Path(temp_project_structure['root']).resolve()

    def test_backward_compatibility_without_config(self, temp_dir_no_config):
        """App works normally without config file (backward compatible)"""
        from x_ipe.services import ConfigService, ProjectService
        
        config_service = ConfigService(str(temp_dir_no_config))
        config_data = config_service.load()
        
        assert config_data is None
        
        # Should still be able to create ProjectService with cwd
        project_service = ProjectService(str(temp_dir_no_config))
        assert project_service.project_root == temp_dir_no_config.resolve()


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestConfigEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_config_with_spaces_in_path(self):
        """Config handles paths with spaces correctly"""
        from x_ipe.services import ConfigService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "My Project"
            project_root.mkdir()
            x_ipe_app = project_root / "x-ipe app"
            x_ipe_app.mkdir()
            (x_ipe_app / "main.py").write_text("# main")
            
            config_content = """version: 1
paths:
  project_root: "."
  x_ipe_app: "./x-ipe app"
"""
            (project_root / ".x-ipe.yaml").write_text(config_content)
            
            service = ConfigService(str(project_root))
            result = service.load()
            
            assert result is not None
            assert "x-ipe app" in result.x_ipe_app

    def test_config_with_symlinked_directory(self):
        """Config handles symlinked directories"""
        from x_ipe.services import ConfigService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            real_app = project_root / "real-x-ipe"
            real_app.mkdir()
            (real_app / "main.py").write_text("# main")
            
            # Create symlink
            symlink_app = project_root / "x-ipe"
            try:
                symlink_app.symlink_to(real_app)
            except OSError:
                pytest.skip("Symlinks not supported on this system")
            
            config_content = """version: 1
paths:
  project_root: "."
  x_ipe_app: "./x-ipe"
"""
            (project_root / ".x-ipe.yaml").write_text(config_content)
            
            service = ConfigService(str(project_root))
            result = service.load()
            
            assert result is not None

    def test_config_missing_defaults_section(self, temp_project_structure):
        """Config works when defaults section is missing"""
        from x_ipe.services import ConfigService
        
        config_content = """version: 1
paths:
  project_root: "."
  x_ipe_app: "./x-ipe"
"""
        temp_project_structure['config_file'].write_text(config_content)
        
        service = ConfigService(str(temp_project_structure['root']))
        result = service.load()
        
        assert result is not None
        assert result.file_tree_scope == "project_root"
        assert result.terminal_cwd == "project_root"

    def test_config_partial_defaults_section(self, temp_project_structure):
        """Config works when defaults section has only some values"""
        from x_ipe.services import ConfigService
        
        config_content = """version: 1
paths:
  project_root: "."
  x_ipe_app: "./x-ipe"
defaults:
  file_tree_scope: "x_ipe_app"
"""
        temp_project_structure['config_file'].write_text(config_content)
        
        service = ConfigService(str(temp_project_structure['root']))
        result = service.load()
        
        assert result is not None
        assert result.file_tree_scope == "x_ipe_app"
        assert result.terminal_cwd == "project_root"  # Default value
