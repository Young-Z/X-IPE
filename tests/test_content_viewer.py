"""
Tests for FEATURE-002: Content Viewer

Tests cover:
- File content API endpoint
- File type detection
- Content rendering integration
"""
import os
import json
import pytest
from pathlib import Path


class TestFileContentAPI:
    """API tests for GET /api/file/content"""

    def test_get_content_returns_200_for_valid_file(self, client, temp_project):
        """API returns 200 for existing file"""
        # Create a test file
        test_file = temp_project / 'x-ipe-docs' / 'planning' / 'test.md'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text('# Test Content')
        
        response = client.get('/api/file/content?path=x-ipe-docs/planning/test.md')
        assert response.status_code == 200

    def test_get_content_returns_json(self, client, temp_project):
        """API returns valid JSON"""
        test_file = temp_project / 'test.md'
        test_file.write_text('# Hello')
        
        response = client.get('/api/file/content?path=test.md')
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert 'content' in data

    def test_get_content_returns_file_content(self, client, temp_project):
        """API returns actual file content"""
        content = '# Task Board\n\nThis is a test.'
        test_file = temp_project / 'x-ipe-docs' / 'planning' / 'task-board.md'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(content)
        
        response = client.get('/api/file/content?path=x-ipe-docs/planning/task-board.md')
        data = json.loads(response.data)
        
        assert data['content'] == content
        assert data['path'] == 'x-ipe-docs/planning/task-board.md'

    def test_get_content_returns_file_type_markdown(self, client, temp_project):
        """API returns correct type for markdown files"""
        test_file = temp_project / 'readme.md'
        test_file.write_text('# README')
        
        response = client.get('/api/file/content?path=readme.md')
        data = json.loads(response.data)
        
        assert data['type'] == 'markdown'
        assert data['extension'] == '.md'

    def test_get_content_returns_file_type_python(self, client, temp_project):
        """API returns correct type for Python files"""
        src_dir = temp_project / 'src'
        src_dir.mkdir(exist_ok=True)
        test_file = src_dir / 'main.py'
        test_file.write_text('print("hello")')
        
        response = client.get('/api/file/content?path=src/main.py')
        data = json.loads(response.data)
        
        assert data['type'] == 'python'
        assert data['extension'] == '.py'

    def test_get_content_returns_file_type_javascript(self, client, temp_project):
        """API returns correct type for JavaScript files"""
        test_file = temp_project / 'app.js'
        test_file.write_text('console.log("hello");')
        
        response = client.get('/api/file/content?path=app.js')
        data = json.loads(response.data)
        
        assert data['type'] == 'javascript'
        assert data['extension'] == '.js'

    def test_get_content_returns_file_type_json(self, client, temp_project):
        """API returns correct type for JSON files"""
        test_file = temp_project / 'config.json'
        test_file.write_text('{"key": "value"}')
        
        response = client.get('/api/file/content?path=config.json')
        data = json.loads(response.data)
        
        assert data['type'] == 'json'

    def test_get_content_returns_file_type_yaml(self, client, temp_project):
        """API returns correct type for YAML files"""
        test_file = temp_project / 'config.yaml'
        test_file.write_text('key: value')
        
        response = client.get('/api/file/content?path=config.yaml')
        data = json.loads(response.data)
        
        assert data['type'] == 'yaml'

    def test_get_content_returns_400_without_path(self, client):
        """API returns 400 when path parameter missing"""
        response = client.get('/api/file/content')
        assert response.status_code == 400

    def test_get_content_returns_404_for_missing_file(self, client, temp_project):
        """API returns 404 for non-existent file"""
        response = client.get('/api/file/content?path=nonexistent.md')
        assert response.status_code == 404

    def test_get_content_prevents_path_traversal(self, client, temp_project):
        """API blocks path traversal attacks"""
        response = client.get('/api/file/content?path=../../../etc/passwd')
        assert response.status_code == 403

    def test_get_content_returns_file_size(self, client, temp_project):
        """API returns file size in bytes"""
        content = 'Hello World!'
        test_file = temp_project / 'test.txt'
        test_file.write_text(content)
        
        response = client.get('/api/file/content?path=test.txt')
        data = json.loads(response.data)
        
        assert 'size' in data
        assert data['size'] == len(content)


class TestFileTypeDetection:
    """Unit tests for file type detection"""

    def test_detect_markdown(self, app):
        """Detect .md as markdown"""
        from x_ipe.services import ContentService
        service = ContentService('')
        assert service.detect_file_type('.md') == 'markdown'

    def test_detect_python(self, app):
        """Detect .py as python"""
        from x_ipe.services import ContentService
        service = ContentService('')
        assert service.detect_file_type('.py') == 'python'

    def test_detect_javascript(self, app):
        """Detect .js as javascript"""
        from x_ipe.services import ContentService
        service = ContentService('')
        assert service.detect_file_type('.js') == 'javascript'

    def test_detect_html(self, app):
        """Detect .html as html"""
        from x_ipe.services import ContentService
        service = ContentService('')
        assert service.detect_file_type('.html') == 'html'

    def test_detect_css(self, app):
        """Detect .css as css"""
        from x_ipe.services import ContentService
        service = ContentService('')
        assert service.detect_file_type('.css') == 'css'

    def test_detect_unknown_as_text(self, app):
        """Detect unknown extension as text"""
        from x_ipe.services import ContentService
        service = ContentService('')
        assert service.detect_file_type('.xyz') == 'text'


# Fixtures
@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


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
