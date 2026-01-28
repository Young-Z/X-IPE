"""
Tests for FEATURE-006: Settings & Configuration

Tests cover:
- SettingsService: CRUD operations with SQLite
- Path validation for project_root
- API endpoints: GET/POST /api/settings
- Settings persistence across sessions
- Integration with sidebar refresh
"""
import os
import json
import pytest
import tempfile
import sqlite3
from pathlib import Path


class TestSettingsServiceUnit:
    """Unit tests for SettingsService class"""

    def test_init_creates_database_file(self, settings_service, temp_db_path):
        """SettingsService creates SQLite database on init"""
        assert os.path.exists(temp_db_path)

    def test_init_creates_settings_table(self, settings_service, temp_db_path):
        """SettingsService creates settings table on init"""
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'settings'

    def test_init_sets_default_project_root(self, settings_service):
        """SettingsService sets default project_root to '.'"""
        project_root = settings_service.get('project_root')
        assert project_root == '.'

    def test_get_returns_setting_value(self, settings_service):
        """get() returns stored setting value"""
        settings_service.set('project_root', '/test/path')
        
        result = settings_service.get('project_root')
        
        assert result == '/test/path'

    def test_get_returns_default_for_missing_key(self, settings_service):
        """get() returns default value for non-existent key"""
        result = settings_service.get('nonexistent', default='fallback')
        
        assert result == 'fallback'

    def test_get_returns_none_for_missing_key_no_default(self, settings_service):
        """get() returns None for non-existent key without default"""
        result = settings_service.get('nonexistent')
        
        assert result is None

    def test_get_all_returns_dict(self, settings_service):
        """get_all() returns dictionary of all settings"""
        result = settings_service.get_all()
        
        assert isinstance(result, dict)
        assert 'project_root' in result

    def test_set_stores_new_value(self, settings_service, temp_db_path):
        """set() stores value in database"""
        settings_service.set('project_root', '/new/path')
        
        # Verify in database directly
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'project_root'")
        result = cursor.fetchone()
        conn.close()
        
        assert result[0] == '/new/path'

    def test_set_updates_existing_value(self, settings_service):
        """set() updates existing setting"""
        settings_service.set('project_root', '/first')
        settings_service.set('project_root', '/second')
        
        result = settings_service.get('project_root')
        
        assert result == '/second'

    def test_set_handles_special_characters(self, settings_service):
        """set() handles paths with spaces and unicode"""
        special_path = '/path/with spaces/日本語'
        settings_service.set('project_root', special_path)
        
        result = settings_service.get('project_root')
        
        assert result == special_path


class TestPathValidation:
    """Tests for project_root path validation"""

    def test_validate_empty_path_returns_error(self, settings_service):
        """AC-5: Empty paths show error message"""
        errors = settings_service.validate_project_root('')
        
        assert 'project_root' in errors
        assert 'required' in errors['project_root'].lower()

    def test_validate_whitespace_path_returns_error(self, settings_service):
        """Whitespace-only paths are rejected"""
        errors = settings_service.validate_project_root('   ')
        
        assert 'project_root' in errors

    def test_validate_nonexistent_path_returns_error(self, settings_service):
        """AC-5: Non-existent paths show error"""
        errors = settings_service.validate_project_root('/nonexistent/path/12345')
        
        assert 'project_root' in errors
        assert 'not exist' in errors['project_root'].lower()

    def test_validate_file_path_returns_error(self, settings_service, temp_project):
        """AC-5: File paths (not directories) show error"""
        test_file = temp_project / 'test.txt'
        test_file.write_text('test')
        
        errors = settings_service.validate_project_root(str(test_file))
        
        assert 'project_root' in errors
        assert 'not a directory' in errors['project_root'].lower()

    def test_validate_valid_directory_returns_empty(self, settings_service, temp_project):
        """AC-4: Valid directory paths pass validation"""
        errors = settings_service.validate_project_root(str(temp_project))
        
        assert errors == {}

    def test_validate_readable_directory_passes(self, settings_service, temp_project):
        """AC-5: Readable directories pass validation"""
        # temp_project is readable by default
        errors = settings_service.validate_project_root(str(temp_project))
        
        assert errors == {}


class TestSettingsAPIGet:
    """Tests for GET /api/settings endpoint"""

    def test_get_settings_returns_200(self, client):
        """GET /api/settings returns 200 OK"""
        response = client.get('/api/settings')
        
        assert response.status_code == 200

    def test_get_settings_returns_json(self, client):
        """GET /api/settings returns JSON"""
        response = client.get('/api/settings')
        
        assert response.content_type == 'application/json'

    def test_get_settings_contains_project_root(self, client):
        """GET /api/settings includes project_root"""
        response = client.get('/api/settings')
        data = json.loads(response.data)
        
        assert 'project_root' in data


class TestSettingsAPIPost:
    """Tests for POST /api/settings endpoint"""

    def test_post_settings_returns_200_on_success(self, client, temp_project):
        """POST /api/settings returns 200 on valid data"""
        response = client.post(
            '/api/settings',
            json={'project_root': str(temp_project)},
            content_type='application/json'
        )
        
        assert response.status_code == 200

    def test_post_settings_returns_success_true(self, client, temp_project):
        """POST /api/settings returns success: true on valid data"""
        response = client.post(
            '/api/settings',
            json={'project_root': str(temp_project)},
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert data['success'] is True

    def test_post_settings_returns_400_on_invalid_path(self, client):
        """POST /api/settings returns 400 on invalid path"""
        response = client.post(
            '/api/settings',
            json={'project_root': '/nonexistent/path/xyz'},
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_post_settings_returns_error_message(self, client):
        """POST /api/settings returns error details on failure"""
        response = client.post(
            '/api/settings',
            json={'project_root': '/nonexistent/path/xyz'},
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'errors' in data
        assert 'project_root' in data['errors']

    def test_post_settings_persists_valid_path(self, client, temp_project):
        """AC-6: Settings are persisted to SQLite database"""
        # Save new setting
        client.post(
            '/api/settings',
            json={'project_root': str(temp_project)},
            content_type='application/json'
        )
        
        # Retrieve and verify
        response = client.get('/api/settings')
        data = json.loads(response.data)
        
        assert data['project_root'] == str(temp_project)

    def test_post_settings_returns_400_on_empty_path(self, client):
        """AC-5: Empty paths return validation error"""
        response = client.post(
            '/api/settings',
            json={'project_root': ''},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['errors']['project_root'].lower()


class TestSettingsPage:
    """Tests for /settings page"""

    def test_settings_page_returns_200(self, client):
        """AC-1: Settings page is accessible"""
        response = client.get('/settings')
        
        assert response.status_code == 200

    def test_settings_page_returns_html(self, client):
        """Settings page returns HTML"""
        response = client.get('/settings')
        
        assert 'text/html' in response.content_type

    def test_settings_page_contains_form(self, client):
        """Settings page contains settings form"""
        response = client.get('/settings')
        
        assert b'form' in response.data.lower() or b'settingsForm' in response.data

    def test_settings_page_shows_current_value(self, client):
        """AC-2: Settings page displays current project root"""
        response = client.get('/settings')
        
        # Should contain input field with project root value
        assert b'projectRoot' in response.data or b'project_root' in response.data


class TestSettingsPersistence:
    """Tests for settings persistence across sessions"""

    def test_settings_persist_after_service_restart(self, temp_db_path):
        """AC-7: Settings persist across application restarts"""
        from x_ipe.services import SettingsService
        
        # First session: save setting
        service1 = SettingsService(temp_db_path)
        service1.set('project_root', '/persistent/path')
        
        # Second session: new service instance
        service2 = SettingsService(temp_db_path)
        
        result = service2.get('project_root')
        
        assert result == '/persistent/path'

    def test_settings_survive_database_reopen(self, temp_db_path):
        """Settings survive database connection close/reopen"""
        from x_ipe.services import SettingsService
        
        service = SettingsService(temp_db_path)
        service.set('project_root', '/test/path')
        
        # Force reconnection by creating new instance
        new_service = SettingsService(temp_db_path)
        
        assert new_service.get('project_root') == '/test/path'


class TestSettingsIntegration:
    """Integration tests for settings with other components"""

    def test_changing_project_root_updates_config(self, app, client, temp_project):
        """AC-11: Changing project root updates app config"""
        new_path = str(temp_project)
        
        client.post(
            '/api/settings',
            json={'project_root': new_path},
            content_type='application/json'
        )
        
        # Config should reflect new value
        with app.app_context():
            assert app.config.get('PROJECT_ROOT') == new_path

    def test_project_structure_uses_new_root(self, client, temp_project):
        """After changing root, /api/project/structure uses new path"""
        # Create structure in temp project
        docs_dir = temp_project / 'docs' / 'planning'
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / 'test-file.md').write_text('# Test')
        
        # Change project root
        client.post(
            '/api/settings',
            json={'project_root': str(temp_project)},
            content_type='application/json'
        )
        
        # Get structure
        response = client.get('/api/project/structure')
        data = json.loads(response.data)
        
        # Should see our test file
        planning_section = next(
            (s for s in data['sections'] if s['id'] == 'planning'),
            None
        )
        assert planning_section is not None
        # Verify children exist (structure from new root)
        assert 'children' in planning_section


class TestEdgeCases:
    """Edge case tests"""

    def test_path_with_trailing_slash(self, settings_service, temp_project):
        """Paths with trailing slashes are handled"""
        path_with_slash = str(temp_project) + '/'
        
        errors = settings_service.validate_project_root(path_with_slash)
        
        assert errors == {}

    def test_path_with_tilde_expansion(self, settings_service):
        """Tilde paths (~) are handled"""
        # This test may behave differently on different systems
        home_path = os.path.expanduser('~')
        if os.path.exists(home_path):
            errors = settings_service.validate_project_root(home_path)
            assert errors == {}

    def test_relative_path_handling(self, settings_service):
        """Relative paths are handled (if current dir exists)"""
        # '.' should be valid if cwd exists
        errors = settings_service.validate_project_root('.')
        
        # Either valid or explicit error about absolute paths
        # Implementation can choose to accept or reject relative paths
        assert isinstance(errors, dict)


# Fixtures

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path"""
    return str(tmp_path / "test_settings.db")


@pytest.fixture
def settings_service(temp_db_path):
    """Create SettingsService instance with temp database"""
    from x_ipe.services import SettingsService
    return SettingsService(temp_db_path)


@pytest.fixture
def app(temp_project, temp_db_path):
    """Create Flask app with test configuration"""
    from src.app import create_app
    
    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': str(temp_project),
        'SETTINGS_DB_PATH': temp_db_path
    })
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()
