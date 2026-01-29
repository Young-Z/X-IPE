"""
Tests for FEATURE-011: Stage Toolbox

Tests cover:
- ToolsConfigService: load(), save(), migration
- API endpoints: GET/POST /api/config/tools
- Config validation and edge cases
- Migration from legacy .ideation-tools.json

TDD Approach: All tests written before implementation.
"""
import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Will be imported after implementation
# from x_ipe.services import ToolsConfigService
# from src.app import create_app


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_project_with_config_dir(temp_project_dir):
    """Create temporary project with x-ipe-docs/config/ directory"""
    config_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    return temp_project_dir


@pytest.fixture
def temp_project_with_legacy_config(temp_project_dir):
    """Create temporary project with legacy .ideation-tools.json"""
    # Create legacy config location
    ideas_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'ideas'
    ideas_dir.mkdir(parents=True, exist_ok=True)
    
    legacy_config = {
        "version": "1.0",
        "ideation": {
            "antv-infographic": True,
            "mermaid": False
        },
        "mockup": {
            "frontend-design": True
        },
        "sharing": {}
    }
    
    legacy_path = ideas_dir / '.ideation-tools.json'
    legacy_path.write_text(json.dumps(legacy_config, indent=2))
    
    return {
        'root': temp_project_dir,
        'legacy_path': legacy_path,
        'legacy_config': legacy_config
    }


@pytest.fixture
def default_config():
    """Default tools configuration"""
    return {
        "version": "2.0",
        "stages": {
            "ideation": {
                "ideation": {"antv-infographic": False, "mermaid": False},
                "mockup": {"frontend-design": True},
                "sharing": {}
            },
            "requirement": {"gathering": {}, "analysis": {}},
            "feature": {"design": {}, "implementation": {}},
            "quality": {"testing": {}, "review": {}},
            "refactoring": {"analysis": {}, "execution": {}}
        }
    }


@pytest.fixture
def sample_config():
    """Sample tools configuration with some tools enabled"""
    return {
        "version": "2.0",
        "stages": {
            "ideation": {
                "ideation": {"antv-infographic": True, "mermaid": True},
                "mockup": {"frontend-design": True},
                "sharing": {}
            },
            "requirement": {"gathering": {}, "analysis": {}},
            "feature": {"design": {}, "implementation": {}},
            "quality": {"testing": {}, "review": {}},
            "refactoring": {"analysis": {}, "execution": {}}
        }
    }


@pytest.fixture
def tools_config_service(temp_project_dir):
    """Create ToolsConfigService instance"""
    from x_ipe.services import ToolsConfigService
    return ToolsConfigService(temp_project_dir)


@pytest.fixture
def test_client(temp_project_dir):
    """Create Flask test client"""
    from src.app import create_app
    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': temp_project_dir
    })
    with app.test_client() as client:
        yield client


# ============================================================================
# ToolsConfigService: UNIT TESTS
# ============================================================================

class TestToolsConfigServiceInit:
    """Test ToolsConfigService initialization"""
    
    def test_init_sets_project_root(self, temp_project_dir):
        """ToolsConfigService stores project root as absolute path"""
        from x_ipe.services import ToolsConfigService
        service = ToolsConfigService(temp_project_dir)
        assert service.project_root == Path(temp_project_dir).resolve()
    
    def test_init_sets_config_path(self, temp_project_dir):
        """ToolsConfigService sets config path to x-ipe-docs/config/tools.json"""
        from x_ipe.services import ToolsConfigService
        service = ToolsConfigService(temp_project_dir)
        expected = Path(temp_project_dir).resolve() / 'x-ipe-docs' / 'config' / 'tools.json'
        assert service.config_path == expected
    
    def test_init_sets_legacy_path(self, temp_project_dir):
        """ToolsConfigService sets legacy path to x-ipe-docs/ideas/.ideation-tools.json"""
        from x_ipe.services import ToolsConfigService
        service = ToolsConfigService(temp_project_dir)
        expected = Path(temp_project_dir).resolve() / 'x-ipe-docs' / 'ideas' / '.ideation-tools.json'
        assert service.legacy_path == expected


class TestToolsConfigServiceLoad:
    """Test ToolsConfigService.load() method"""
    
    def test_load_returns_existing_config(self, temp_project_with_config_dir, sample_config):
        """load() returns existing config when x-ipe-docs/config/tools.json exists"""
        from x_ipe.services import ToolsConfigService
        
        # Create config file
        config_path = Path(temp_project_with_config_dir) / 'x-ipe-docs' / 'config' / 'tools.json'
        config_path.write_text(json.dumps(sample_config, indent=2))
        
        service = ToolsConfigService(temp_project_with_config_dir)
        config = service.load()
        
        assert config['version'] == '2.0'
        assert config['stages']['ideation']['ideation']['antv-infographic'] == True
        assert config['stages']['ideation']['ideation']['mermaid'] == True
    
    def test_load_creates_default_when_no_config_exists(self, temp_project_dir, default_config):
        """load() creates default config when neither config nor legacy exists"""
        from x_ipe.services import ToolsConfigService
        
        service = ToolsConfigService(temp_project_dir)
        config = service.load()
        
        assert config['version'] == '2.0'
        assert 'stages' in config
        assert config['stages']['ideation']['mockup']['frontend-design'] == True
        
        # Verify file was created
        config_path = Path(temp_project_dir) / 'x-ipe-docs' / 'config' / 'tools.json'
        assert config_path.exists()
    
    def test_load_creates_config_directory_if_missing(self, temp_project_dir):
        """load() creates x-ipe-docs/config/ directory if it doesn't exist"""
        from x_ipe.services import ToolsConfigService
        
        config_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'config'
        assert not config_dir.exists()
        
        service = ToolsConfigService(temp_project_dir)
        service.load()
        
        assert config_dir.exists()
    
    def test_load_handles_corrupted_config(self, temp_project_with_config_dir):
        """load() returns default config when config file is corrupted"""
        from x_ipe.services import ToolsConfigService
        
        # Create corrupted config file
        config_path = Path(temp_project_with_config_dir) / 'x-ipe-docs' / 'config' / 'tools.json'
        config_path.write_text('{ invalid json }}}')
        
        service = ToolsConfigService(temp_project_with_config_dir)
        config = service.load()
        
        # Should return default config
        assert config['version'] == '2.0'
        assert 'stages' in config


class TestToolsConfigServiceMigration:
    """Test ToolsConfigService legacy migration"""
    
    def test_load_migrates_from_legacy_config(self, temp_project_with_legacy_config):
        """load() migrates from .ideation-tools.json when no new config exists"""
        from x_ipe.services import ToolsConfigService
        
        project_root = temp_project_with_legacy_config['root']
        legacy_config = temp_project_with_legacy_config['legacy_config']
        
        service = ToolsConfigService(project_root)
        config = service.load()
        
        # Should have new version
        assert config['version'] == '2.0'
        
        # Should preserve legacy tool states
        assert config['stages']['ideation']['ideation']['antv-infographic'] == True
        assert config['stages']['ideation']['ideation']['mermaid'] == False
        assert config['stages']['ideation']['mockup']['frontend-design'] == True
    
    def test_migration_deletes_legacy_file(self, temp_project_with_legacy_config):
        """load() deletes legacy .ideation-tools.json after migration"""
        from x_ipe.services import ToolsConfigService
        
        project_root = temp_project_with_legacy_config['root']
        legacy_path = temp_project_with_legacy_config['legacy_path']
        
        assert legacy_path.exists()
        
        service = ToolsConfigService(project_root)
        service.load()
        
        # Legacy file should be deleted
        assert not legacy_path.exists()
    
    def test_migration_creates_new_config_file(self, temp_project_with_legacy_config):
        """load() creates x-ipe-docs/config/tools.json after migration"""
        from x_ipe.services import ToolsConfigService
        
        project_root = temp_project_with_legacy_config['root']
        
        service = ToolsConfigService(project_root)
        service.load()
        
        # New config file should exist
        new_config_path = Path(project_root) / 'x-ipe-docs' / 'config' / 'tools.json'
        assert new_config_path.exists()
    
    def test_migration_handles_partial_legacy_config(self, temp_project_dir):
        """load() handles legacy config with missing sections"""
        from x_ipe.services import ToolsConfigService
        
        # Create legacy config with only ideation section
        ideas_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'ideas'
        ideas_dir.mkdir(parents=True, exist_ok=True)
        
        partial_legacy = {
            "version": "1.0",
            "ideation": {"mermaid": True}
            # Missing mockup and sharing sections
        }
        
        legacy_path = ideas_dir / '.ideation-tools.json'
        legacy_path.write_text(json.dumps(partial_legacy, indent=2))
        
        service = ToolsConfigService(temp_project_dir)
        config = service.load()
        
        # Should have migrated value
        assert config['stages']['ideation']['ideation']['mermaid'] == True
        
        # Should have defaults for missing sections
        assert 'mockup' in config['stages']['ideation']
        assert 'sharing' in config['stages']['ideation']
    
    def test_migration_handles_corrupted_legacy_config(self, temp_project_dir):
        """load() returns default config when legacy file is corrupted"""
        from x_ipe.services import ToolsConfigService
        
        # Create corrupted legacy config
        ideas_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'ideas'
        ideas_dir.mkdir(parents=True, exist_ok=True)
        
        legacy_path = ideas_dir / '.ideation-tools.json'
        legacy_path.write_text('{ corrupted json {{{}')
        
        service = ToolsConfigService(temp_project_dir)
        config = service.load()
        
        # Should return default config
        assert config['version'] == '2.0'


class TestToolsConfigServiceSave:
    """Test ToolsConfigService.save() method"""
    
    def test_save_writes_config_to_file(self, temp_project_dir, sample_config):
        """save() writes config to x-ipe-docs/config/tools.json"""
        from x_ipe.services import ToolsConfigService
        
        service = ToolsConfigService(temp_project_dir)
        service.save(sample_config)
        
        config_path = Path(temp_project_dir) / 'x-ipe-docs' / 'config' / 'tools.json'
        assert config_path.exists()
        
        saved = json.loads(config_path.read_text())
        assert saved['version'] == '2.0'
        assert saved['stages']['ideation']['ideation']['antv-infographic'] == True
    
    def test_save_creates_config_directory(self, temp_project_dir, sample_config):
        """save() creates x-ipe-docs/config/ directory if missing"""
        from x_ipe.services import ToolsConfigService
        
        config_dir = Path(temp_project_dir) / 'x-ipe-docs' / 'config'
        assert not config_dir.exists()
        
        service = ToolsConfigService(temp_project_dir)
        service.save(sample_config)
        
        assert config_dir.exists()
    
    def test_save_returns_true_on_success(self, temp_project_dir, sample_config):
        """save() returns True on successful save"""
        from x_ipe.services import ToolsConfigService
        
        service = ToolsConfigService(temp_project_dir)
        result = service.save(sample_config)
        
        assert result == True
    
    def test_save_overwrites_existing_config(self, temp_project_with_config_dir, sample_config, default_config):
        """save() overwrites existing config file"""
        from x_ipe.services import ToolsConfigService
        
        config_path = Path(temp_project_with_config_dir) / 'x-ipe-docs' / 'config' / 'tools.json'
        
        # Write initial config
        config_path.write_text(json.dumps(default_config, indent=2))
        
        # Save new config
        service = ToolsConfigService(temp_project_with_config_dir)
        service.save(sample_config)
        
        # Verify overwritten
        saved = json.loads(config_path.read_text())
        assert saved['stages']['ideation']['ideation']['antv-infographic'] == True


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestGetToolsConfigAPI:
    """Test GET /api/config/tools endpoint"""
    
    def test_get_returns_config(self, test_client, temp_project_dir, sample_config):
        """GET /api/config/tools returns current config"""
        # Setup: create config file
        config_path = Path(temp_project_dir) / 'x-ipe-docs' / 'config' / 'tools.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(sample_config, indent=2))
        
        response = test_client.get('/api/config/tools')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'config' in data
        assert data['config']['version'] == '2.0'
    
    def test_get_returns_default_when_no_config(self, test_client):
        """GET /api/config/tools returns default config when no file exists"""
        response = test_client.get('/api/config/tools')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['config']['version'] == '2.0'
        assert 'stages' in data['config']
    
    def test_get_response_structure(self, test_client):
        """GET /api/config/tools response has correct structure"""
        response = test_client.get('/api/config/tools')
        
        data = response.get_json()
        assert 'success' in data
        assert 'config' in data
        
        config = data['config']
        assert 'version' in config
        assert 'stages' in config
        
        stages = config['stages']
        assert 'ideation' in stages
        assert 'requirement' in stages
        assert 'feature' in stages
        assert 'quality' in stages
        assert 'refactoring' in stages


class TestPostToolsConfigAPI:
    """Test POST /api/config/tools endpoint"""
    
    def test_post_saves_config(self, test_client, temp_project_dir, sample_config):
        """POST /api/config/tools saves config to file"""
        response = test_client.post(
            '/api/config/tools',
            data=json.dumps(sample_config),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        # Verify file was written
        config_path = Path(temp_project_dir) / 'x-ipe-docs' / 'config' / 'tools.json'
        assert config_path.exists()
    
    def test_post_returns_error_for_invalid_json(self, test_client):
        """POST /api/config/tools returns 400 for invalid JSON"""
        response = test_client.post(
            '/api/config/tools',
            data='not valid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_post_returns_error_for_missing_stages(self, test_client):
        """POST /api/config/tools returns 400 when stages key is missing"""
        invalid_config = {"version": "2.0"}  # Missing 'stages'
        
        response = test_client.post(
            '/api/config/tools',
            data=json.dumps(invalid_config),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        assert 'error' in data
    
    def test_post_returns_error_for_empty_body(self, test_client):
        """POST /api/config/tools returns 400 for empty body"""
        response = test_client.post(
            '/api/config/tools',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestToolsConfigIntegration:
    """Integration tests for tools config feature"""
    
    def test_full_flow_load_modify_save(self, temp_project_dir):
        """Full flow: load default → modify → save → reload"""
        from x_ipe.services import ToolsConfigService
        
        service = ToolsConfigService(temp_project_dir)
        
        # Load default config
        config = service.load()
        assert config['stages']['ideation']['ideation']['mermaid'] == False
        
        # Modify
        config['stages']['ideation']['ideation']['mermaid'] = True
        
        # Save
        service.save(config)
        
        # Reload and verify
        new_service = ToolsConfigService(temp_project_dir)
        reloaded = new_service.load()
        assert reloaded['stages']['ideation']['ideation']['mermaid'] == True
    
    def test_api_roundtrip(self, test_client, sample_config):
        """API roundtrip: POST config → GET returns same config"""
        # POST new config
        post_response = test_client.post(
            '/api/config/tools',
            data=json.dumps(sample_config),
            content_type='application/json'
        )
        assert post_response.status_code == 200
        
        # GET config back
        get_response = test_client.get('/api/config/tools')
        data = get_response.get_json()
        
        assert data['config']['stages']['ideation']['ideation']['antv-infographic'] == True
        assert data['config']['stages']['ideation']['ideation']['mermaid'] == True
    
    def test_migration_preserves_existing_config(self, temp_project_with_legacy_config):
        """Migration does not run if x-ipe-docs/config/tools.json already exists"""
        from x_ipe.services import ToolsConfigService
        
        project_root = temp_project_with_legacy_config['root']
        
        # Create new config file first
        config_dir = Path(project_root) / 'x-ipe-docs' / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        new_config = {
            "version": "2.0",
            "stages": {
                "ideation": {
                    "ideation": {"antv-infographic": False, "mermaid": False},
                    "mockup": {"frontend-design": False},
                    "sharing": {}
                },
                "requirement": {"gathering": {}, "analysis": {}},
                "feature": {"design": {}, "implementation": {}},
                "quality": {"testing": {}, "review": {}},
                "refactoring": {"analysis": {}, "execution": {}}
            }
        }
        
        config_path = config_dir / 'tools.json'
        config_path.write_text(json.dumps(new_config, indent=2))
        
        # Load should use existing config, not migrate
        service = ToolsConfigService(project_root)
        config = service.load()
        
        # Should have new config values (not migrated legacy values)
        assert config['stages']['ideation']['ideation']['antv-infographic'] == False
        assert config['stages']['ideation']['mockup']['frontend-design'] == False
        
        # Legacy file should still exist (not deleted since migration didn't run)
        legacy_path = temp_project_with_legacy_config['legacy_path']
        assert legacy_path.exists()


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestToolsConfigEdgeCases:
    """Edge case tests for tools config"""
    
    def test_concurrent_save_last_write_wins(self, temp_project_dir, sample_config, default_config):
        """Concurrent saves: last write wins (acceptable for single-user)"""
        from x_ipe.services import ToolsConfigService
        
        service1 = ToolsConfigService(temp_project_dir)
        service2 = ToolsConfigService(temp_project_dir)
        
        # Both load default
        service1.load()
        service2.load()
        
        # Service1 saves sample config
        service1.save(sample_config)
        
        # Service2 saves default config (last write)
        service2.save(default_config)
        
        # Verify last write wins
        config_path = Path(temp_project_dir) / 'x-ipe-docs' / 'config' / 'tools.json'
        saved = json.loads(config_path.read_text())
        
        # default_config has mermaid=False, sample_config has mermaid=True
        # Last write (default_config) should win
        assert saved['stages']['ideation']['ideation']['mermaid'] == False
    
    def test_load_with_extra_fields_preserves_them(self, temp_project_with_config_dir):
        """load() preserves extra/unknown fields in config"""
        from x_ipe.services import ToolsConfigService
        
        config_with_extra = {
            "version": "2.0",
            "custom_field": "custom_value",
            "stages": {
                "ideation": {
                    "ideation": {"antv-infographic": False, "mermaid": False, "extra-tool": True},
                    "mockup": {"frontend-design": True},
                    "sharing": {}
                },
                "requirement": {"gathering": {}, "analysis": {}},
                "feature": {"design": {}, "implementation": {}},
                "quality": {"testing": {}, "review": {}},
                "refactoring": {"analysis": {}, "execution": {}}
            }
        }
        
        config_path = Path(temp_project_with_config_dir) / 'x-ipe-docs' / 'config' / 'tools.json'
        config_path.write_text(json.dumps(config_with_extra, indent=2))
        
        service = ToolsConfigService(temp_project_with_config_dir)
        config = service.load()
        
        # Extra fields should be preserved
        assert config.get('custom_field') == 'custom_value'
        assert config['stages']['ideation']['ideation'].get('extra-tool') == True
    
    def test_save_with_unicode_content(self, temp_project_dir):
        """save() handles unicode content correctly"""
        from x_ipe.services import ToolsConfigService
        
        config_with_unicode = {
            "version": "2.0",
            "stages": {
                "ideation": {
                    "ideation": {"工具-中文": True, "mermaid": False},
                    "mockup": {"frontend-design": True},
                    "sharing": {}
                },
                "requirement": {"gathering": {}, "analysis": {}},
                "feature": {"design": {}, "implementation": {}},
                "quality": {"testing": {}, "review": {}},
                "refactoring": {"analysis": {}, "execution": {}}
            }
        }
        
        service = ToolsConfigService(temp_project_dir)
        service.save(config_with_unicode)
        
        # Reload and verify unicode preserved
        reloaded = service.load()
        assert reloaded['stages']['ideation']['ideation'].get('工具-中文') == True


# ============================================================================
# TEST COVERAGE SUMMARY
# ============================================================================
"""
Test Coverage for FEATURE-011: Stage Toolbox

| Component | Unit Tests | Integration | API Tests |
|-----------|------------|-------------|-----------|
| ToolsConfigService.__init__ | 3 | - | - |
| ToolsConfigService.load | 4 | 1 | - |
| ToolsConfigService.save | 4 | - | - |
| Migration logic | 5 | 1 | - |
| GET /api/config/tools | - | - | 3 |
| POST /api/config/tools | - | - | 4 |
| Edge cases | 3 | - | - |
| **TOTAL** | **19** | **2** | **7** |

Total tests: 28

TDD Baseline: 28 tests failing, 0 passing (implementation not yet created)
"""
