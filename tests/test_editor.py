"""
Tests for FEATURE-003: Content Editor

Tests cover:
- ContentService save_content method
- Path validation for file writes
- API endpoint POST /api/file/save
- Security: path traversal prevention
"""
import os
import json
import pytest
from pathlib import Path


class TestContentServiceSaveUnit:
    """Unit tests for ContentService.save_content()"""

    def test_save_content_writes_file(self, content_service, temp_project):
        """save_content() writes content to file"""
        # Create test file
        test_file = temp_project / 'test.md'
        test_file.write_text('original content')
        
        result = content_service.save_content('test.md', 'new content')
        
        assert result['success'] is True
        assert test_file.read_text() == 'new content'

    def test_save_content_returns_success_message(self, content_service, temp_project):
        """save_content() returns success message"""
        test_file = temp_project / 'test.md'
        test_file.write_text('original')
        
        result = content_service.save_content('test.md', 'updated')
        
        assert result['success'] is True
        assert 'saved' in result['message'].lower()
        assert result['path'] == 'test.md'

    def test_save_content_nested_path(self, content_service, temp_project):
        """save_content() works with nested paths"""
        nested_dir = temp_project / 'x-ipe-docs' / 'planning'
        nested_dir.mkdir(parents=True, exist_ok=True)
        test_file = nested_dir / 'task-board.md'
        test_file.write_text('# Original')
        
        result = content_service.save_content('x-ipe-docs/planning/task-board.md', '# Updated')
        
        assert result['success'] is True
        assert test_file.read_text() == '# Updated'

    def test_save_content_preserves_encoding(self, content_service, temp_project):
        """save_content() preserves UTF-8 encoding"""
        test_file = temp_project / 'unicode.md'
        test_file.write_text('Hello', encoding='utf-8')
        
        unicode_content = '日本語テスト 🚀 émoji'
        result = content_service.save_content('unicode.md', unicode_content)
        
        assert result['success'] is True
        assert test_file.read_text(encoding='utf-8') == unicode_content

    def test_save_content_empty_content(self, content_service, temp_project):
        """save_content() allows empty content"""
        test_file = temp_project / 'empty.md'
        test_file.write_text('not empty')
        
        result = content_service.save_content('empty.md', '')
        
        assert result['success'] is True
        assert test_file.read_text() == ''


class TestPathValidation:
    """Tests for path validation in save operations"""

    def test_empty_path_rejected(self, content_service):
        """AC: Empty path returns error"""
        result = content_service.save_content('', 'content')
        
        assert result['success'] is False
        assert 'required' in result['error'].lower()

    def test_path_traversal_rejected(self, content_service, temp_project):
        """Security: Path with .. is rejected"""
        # Create file that exists but path uses traversal
        test_file = temp_project / 'test.md'
        test_file.write_text('content')
        
        result = content_service.save_content('../test.md', 'malicious')
        
        assert result['success'] is False
        assert 'traversal' in result['error'].lower() or 'invalid' in result['error'].lower()

    def test_absolute_path_rejected(self, content_service):
        """Security: Absolute paths are rejected"""
        result = content_service.save_content('/etc/passwd', 'malicious')
        
        assert result['success'] is False
        assert 'invalid' in result['error'].lower() or 'traversal' in result['error'].lower()

    def test_nonexistent_file_rejected(self, content_service):
        """v1.0: Cannot create new files"""
        result = content_service.save_content('nonexistent.md', 'content')
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    def test_directory_path_rejected(self, content_service, temp_project):
        """Cannot save to directory path"""
        dir_path = temp_project / 'mydir'
        dir_path.mkdir()
        
        result = content_service.save_content('mydir', 'content')
        
        assert result['success'] is False
        assert 'director' in result['error'].lower()

    def test_outside_project_rejected(self, content_service, temp_project, tmp_path):
        """Security: Paths outside project root rejected"""
        # Create file outside project
        outside_file = tmp_path / 'outside.txt'
        outside_file.write_text('outside')
        
        # Try to access via relative path that resolves outside
        result = content_service.save_content('../../outside.txt', 'malicious')
        
        assert result['success'] is False


class TestFileSaveAPI:
    """Tests for POST /api/file/save endpoint"""

    def test_save_returns_200_on_success(self, client, temp_project):
        """POST /api/file/save returns 200 on success"""
        test_file = temp_project / 'test.md'
        test_file.write_text('original')
        
        response = client.post(
            '/api/file/save',
            json={'path': 'test.md', 'content': 'updated'},
            content_type='application/json'
        )
        
        assert response.status_code == 200

    def test_save_returns_success_json(self, client, temp_project):
        """POST /api/file/save returns success JSON"""
        test_file = temp_project / 'test.md'
        test_file.write_text('original')
        
        response = client.post(
            '/api/file/save',
            json={'path': 'test.md', 'content': 'updated'},
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'path' in data

    def test_save_actually_writes_file(self, client, temp_project):
        """POST /api/file/save writes to filesystem"""
        test_file = temp_project / 'test.md'
        test_file.write_text('original')
        
        client.post(
            '/api/file/save',
            json={'path': 'test.md', 'content': 'API updated'},
            content_type='application/json'
        )
        
        assert test_file.read_text() == 'API updated'

    def test_save_missing_path_returns_400(self, client):
        """POST /api/file/save returns 400 if path missing"""
        response = client.post(
            '/api/file/save',
            json={'content': 'no path'},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_save_missing_content_returns_400(self, client, temp_project):
        """POST /api/file/save returns 400 if content missing"""
        test_file = temp_project / 'test.md'
        test_file.write_text('original')
        
        response = client.post(
            '/api/file/save',
            json={'path': 'test.md'},
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_save_empty_body_returns_400(self, client):
        """POST /api/file/save returns 400 with empty body"""
        response = client.post(
            '/api/file/save',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_save_invalid_path_returns_400(self, client):
        """POST /api/file/save returns 400 for invalid path"""
        response = client.post(
            '/api/file/save',
            json={'path': '../../../etc/passwd', 'content': 'malicious'},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_save_nonexistent_file_returns_400(self, client):
        """POST /api/file/save returns 400 for nonexistent file"""
        response = client.post(
            '/api/file/save',
            json={'path': 'does_not_exist.md', 'content': 'content'},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'not found' in data['error'].lower()


class TestSecurityEdgeCases:
    """Security-focused edge case tests"""

    def test_null_byte_in_path_rejected(self, content_service, temp_project):
        """Security: Null byte injection rejected"""
        test_file = temp_project / 'test.md'
        test_file.write_text('content')
        
        result = content_service.save_content('test.md\x00.txt', 'malicious')
        
        # Should either reject or fail to find file
        assert result['success'] is False

    def test_symlink_outside_project(self, content_service, temp_project, tmp_path):
        """Security: Symlink pointing outside project"""
        # Create file outside project
        outside_file = tmp_path / 'secret.txt'
        outside_file.write_text('secret data')
        
        # Create symlink inside project pointing outside
        symlink = temp_project / 'link.txt'
        try:
            symlink.symlink_to(outside_file)
        except OSError:
            pytest.skip("Cannot create symlinks on this system")
        
        result = content_service.save_content('link.txt', 'overwrite')
        
        # Should reject - resolved path is outside project
        assert result['success'] is False

    def test_very_long_path_handled(self, content_service):
        """Edge case: Very long path"""
        long_path = 'a' * 1000 + '.md'
        result = content_service.save_content(long_path, 'content')
        
        assert result['success'] is False


class TestEditorIntegration:
    """Integration tests for editor workflow"""

    def test_edit_save_cycle(self, client, temp_project):
        """Full edit-save cycle works"""
        # Create file
        test_file = temp_project / 'x-ipe-docs' / 'test.md'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        original = '# Original Title\n\nOriginal content.'
        test_file.write_text(original)
        
        # Read file
        response = client.get('/api/file/content?path=x-ipe-docs/test.md')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['content'] == original
        
        # Save modified content
        modified = '# Modified Title\n\nModified content.'
        response = client.post(
            '/api/file/save',
            json={'path': 'x-ipe-docs/test.md', 'content': modified},
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Read again to verify
        response = client.get('/api/file/content?path=x-ipe-docs/test.md')
        data = json.loads(response.data)
        assert data['content'] == modified

    def test_save_triggers_file_change(self, client, temp_project):
        """Save should be detectable by file watcher (file mtime changes)"""
        test_file = temp_project / 'watched.md'
        test_file.write_text('original')
        
        import time
        mtime_before = test_file.stat().st_mtime
        
        time.sleep(0.1)  # Ensure time difference
        
        client.post(
            '/api/file/save',
            json={'path': 'watched.md', 'content': 'updated'},
            content_type='application/json'
        )
        
        mtime_after = test_file.stat().st_mtime
        assert mtime_after > mtime_before


class TestSpecialContent:
    """Tests for special content handling"""

    def test_save_content_with_newlines(self, content_service, temp_project):
        """Content with various newline styles preserved"""
        test_file = temp_project / 'newlines.md'
        test_file.write_text('original')
        
        content_unix = 'line1\nline2\nline3'
        result = content_service.save_content('newlines.md', content_unix)
        
        assert result['success'] is True
        assert test_file.read_text() == content_unix

    def test_save_content_with_tabs(self, content_service, temp_project):
        """Content with tabs preserved"""
        test_file = temp_project / 'tabs.py'
        test_file.write_text('original')
        
        content = 'def foo():\n\treturn True'
        result = content_service.save_content('tabs.py', content)
        
        assert result['success'] is True
        assert '\t' in test_file.read_text()

    def test_save_large_content(self, content_service, temp_project):
        """Large content can be saved"""
        test_file = temp_project / 'large.md'
        test_file.write_text('original')
        
        large_content = 'x' * 100000  # 100KB
        result = content_service.save_content('large.md', large_content)
        
        assert result['success'] is True
        assert len(test_file.read_text()) == 100000


# Fixtures

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def content_service(temp_project):
    """Create ContentService instance"""
    from x_ipe.services import ContentService
    return ContentService(str(temp_project))


@pytest.fixture
def app(temp_project):
    """Create Flask app with test configuration"""
    from src.app import create_app
    
    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': str(temp_project)
    })
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()
