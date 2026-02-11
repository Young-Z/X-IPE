"""
Tests for FEATURE-028-D: Settings Language Switch (Web UI)

Tests cover:
- ConfigData.language field and to_dict inclusion
- POST /api/config/language endpoint: validation, atomicity, success
- Same-language guard (no-op)
- Error handling: missing field, unsupported language, extraction failure
- YAML update after successful switch

TDD: All tests should FAIL before implementation.
"""
import os
import json
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock


# --- Fixtures ---

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project with .x-ipe.yaml and copilot instructions."""
    # Create .x-ipe.yaml
    config = {
        'version': 1,
        'language': 'en',
        'cli': 'copilot',
        'paths': {
            'project_root': '.',
        }
    }
    config_path = tmp_path / '.x-ipe.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    # Create .github directory for copilot instructions
    github_dir = tmp_path / '.github'
    github_dir.mkdir(parents=True, exist_ok=True)
    (github_dir / 'copilot-instructions.md').write_text('# Instructions (English)')

    return tmp_path


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    return str(tmp_path / 'test_settings.db')


@pytest.fixture
def app(temp_project, temp_db_path):
    """Create Flask app with test configuration and mocked config data."""
    from src.app import create_app
    from x_ipe.services.config_service import ConfigData

    config_data = ConfigData(
        config_file_path=str(temp_project / '.x-ipe.yaml'),
        version=1,
        project_root=str(temp_project),
        x_ipe_app=str(temp_project),
        file_tree_scope='project_root',
        terminal_cwd='project_root',
        language='en',
    )

    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': str(temp_project),
        'SETTINGS_DB_PATH': temp_db_path,
        'X_IPE_CONFIG': config_data,
    })
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


# --- Unit Tests: ConfigData.language ---

class TestConfigDataLanguage:
    """Unit tests for ConfigData language field (AC-CR2-2 prerequisite)."""

    def test_config_data_has_language_field(self):
        """ConfigData includes language field."""
        from x_ipe.services.config_service import ConfigData

        config = ConfigData(
            config_file_path='/test/.x-ipe.yaml',
            version=1,
            project_root='/test',
            x_ipe_app='/test',
            file_tree_scope='project_root',
            terminal_cwd='project_root',
            language='zh',
        )
        assert config.language == 'zh'

    def test_config_data_language_defaults_to_en(self):
        """ConfigData language defaults to 'en' if not specified."""
        from x_ipe.services.config_service import ConfigData

        config = ConfigData(
            config_file_path='/test/.x-ipe.yaml',
            version=1,
            project_root='/test',
            x_ipe_app='/test',
            file_tree_scope='project_root',
            terminal_cwd='project_root',
        )
        assert config.language == 'en'

    def test_config_data_to_dict_includes_language(self):
        """ConfigData.to_dict() includes language field."""
        from x_ipe.services.config_service import ConfigData

        config = ConfigData(
            config_file_path='/test/.x-ipe.yaml',
            version=1,
            project_root='/test',
            x_ipe_app='/test',
            file_tree_scope='project_root',
            terminal_cwd='project_root',
            language='zh',
        )
        result = config.to_dict()
        assert 'language' in result
        assert result['language'] == 'zh'


# --- API Tests: POST /api/config/language ---

class TestSwitchLanguageEndpoint:
    """API tests for POST /api/config/language."""

    def test_switch_language_returns_200_on_success(self, client, temp_project):
        """POST /api/config/language returns 200 with valid language. (AC-CR2-4)"""
        response = client.post(
            '/api/config/language',
            data=json.dumps({'language': 'zh'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['language'] == 'zh'

    def test_switch_language_updates_yaml_file(self, client, temp_project):
        """POST /api/config/language updates .x-ipe.yaml language field. (AC-CR2-5)"""
        client.post(
            '/api/config/language',
            data=json.dumps({'language': 'zh'}),
            content_type='application/json'
        )

        config_path = temp_project / '.x-ipe.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config['language'] == 'zh'

    def test_switch_language_missing_field_returns_400(self, client):
        """POST /api/config/language with missing language field returns 400. (AC-CR2-4)"""
        response = client.post(
            '/api/config/language',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data

    def test_switch_language_unsupported_returns_400(self, client):
        """POST /api/config/language with unsupported language returns 400. (AC-CR2-4)"""
        response = client.post(
            '/api/config/language',
            data=json.dumps({'language': 'fr'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'fr' in data['error']

    def test_switch_language_empty_body_returns_400(self, client):
        """POST /api/config/language with no body returns 400."""
        response = client.post(
            '/api/config/language',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_switch_to_en_succeeds(self, client, temp_project):
        """POST /api/config/language switching to 'en' succeeds."""
        # First switch to zh
        client.post(
            '/api/config/language',
            data=json.dumps({'language': 'zh'}),
            content_type='application/json'
        )
        # Then switch back to en
        response = client.post(
            '/api/config/language',
            data=json.dumps({'language': 'en'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['language'] == 'en'


# --- Integration Tests: Atomicity ---

class TestLanguageSwitchAtomicity:
    """Integration tests for atomic language switch behavior. (AC-CR2-5)"""

    def test_yaml_unchanged_on_extraction_failure(self, client, temp_project):
        """If instruction extraction fails, .x-ipe.yaml language must NOT change. (AC-CR2-5)"""
        with patch('x_ipe.routes.settings_routes.ScaffoldManager') as MockScaffold:
            instance = MockScaffold.return_value
            instance.copy_copilot_instructions.side_effect = Exception('Extraction failed')

            response = client.post(
                '/api/config/language',
                data=json.dumps({'language': 'zh'}),
                content_type='application/json'
            )

            # Should return error
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] is False

            # YAML should still have 'en'
            config_path = temp_project / '.x-ipe.yaml'
            with open(config_path) as f:
                config = yaml.safe_load(f)
            assert config.get('language', 'en') == 'en'

    def test_scaffold_called_with_force_true(self, client, temp_project):
        """ScaffoldManager must be called with force=True to overwrite existing instructions."""
        with patch('x_ipe.routes.settings_routes.ScaffoldManager') as MockScaffold:
            instance = MockScaffold.return_value
            instance.copy_copilot_instructions.return_value = None

            client.post(
                '/api/config/language',
                data=json.dumps({'language': 'zh'}),
                content_type='application/json'
            )

            MockScaffold.assert_called_once()
            call_kwargs = MockScaffold.call_args
            # force=True should be passed
            assert call_kwargs[1].get('force') is True or (len(call_kwargs[0]) > 2 and call_kwargs[0][2] is True)

    def test_scaffold_called_before_yaml_update(self, client, temp_project):
        """Instructions must be extracted BEFORE updating .x-ipe.yaml. (AC-CR2-5)"""
        call_order = []

        original_yaml_dump = yaml.dump

        def track_yaml_write(*args, **kwargs):
            call_order.append('yaml_write')
            return original_yaml_dump(*args, **kwargs)

        with patch('x_ipe.routes.settings_routes.ScaffoldManager') as MockScaffold:
            instance = MockScaffold.return_value

            def track_extract(*args, **kwargs):
                call_order.append('extract')

            instance.copy_copilot_instructions.side_effect = track_extract

            with patch('x_ipe.routes.settings_routes.yaml.dump', side_effect=track_yaml_write):
                client.post(
                    '/api/config/language',
                    data=json.dumps({'language': 'zh'}),
                    content_type='application/json'
                )

            # Extract must happen before yaml write
            assert 'extract' in call_order
            assert 'yaml_write' in call_order
            assert call_order.index('extract') < call_order.index('yaml_write')


# --- Integration Tests: Config API ---

class TestConfigApiLanguage:
    """Tests for GET /api/config returning language field. (AC-CR2-2)"""

    def test_get_config_returns_language_field(self, client):
        """GET /api/config response must include language field."""
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.get_json()
        assert 'language' in data

    def test_get_config_language_defaults_to_en(self, client):
        """GET /api/config returns language 'en' by default."""
        response = client.get('/api/config')
        data = response.get_json()
        assert data.get('language') == 'en'


# --- Edge Case Tests ---

class TestLanguageSwitchEdgeCases:
    """Edge case tests from specification."""

    def test_no_config_file_returns_error(self, tmp_path, temp_db_path):
        """Endpoint returns error when no .x-ipe.yaml exists."""
        from src.app import create_app

        app = create_app({
            'TESTING': True,
            'PROJECT_ROOT': str(tmp_path),
            'SETTINGS_DB_PATH': temp_db_path,
            # No X_IPE_CONFIG — simulates missing config
        })
        client = app.test_client()

        response = client.post(
            '/api/config/language',
            data=json.dumps({'language': 'zh'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_config_without_language_field_defaults_en(self, tmp_path, temp_db_path):
        """Projects without language in .x-ipe.yaml should default to 'en'."""
        # Create .x-ipe.yaml without language field
        config = {
            'version': 1,
            'paths': {'project_root': '.'},
        }
        config_path = tmp_path / '.x-ipe.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        from src.app import create_app
        from x_ipe.services.config_service import ConfigData

        config_data = ConfigData(
            config_file_path=str(config_path),
            version=1,
            project_root=str(tmp_path),
            x_ipe_app=str(tmp_path),
            file_tree_scope='project_root',
            terminal_cwd='project_root',
        )

        app = create_app({
            'TESTING': True,
            'PROJECT_ROOT': str(tmp_path),
            'SETTINGS_DB_PATH': temp_db_path,
            'X_IPE_CONFIG': config_data,
        })
        client = app.test_client()

        response = client.get('/api/config')
        data = response.get_json()
        assert data.get('language') == 'en'

    def test_switch_preserves_other_yaml_fields(self, client, temp_project):
        """Language switch must not remove other fields from .x-ipe.yaml."""
        response = client.post(
            '/api/config/language',
            data=json.dumps({'language': 'zh'}),
            content_type='application/json'
        )
        assert response.status_code == 200

        config_path = temp_project / '.x-ipe.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Original fields must still exist
        assert config.get('version') == 1
        assert config.get('cli') == 'copilot'
        assert config.get('language') == 'zh'
