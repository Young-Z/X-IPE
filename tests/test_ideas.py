"""
Tests for FEATURE-008: Workplace (Idea Management)

Tests cover:
- IdeasService: get_tree(), upload(), rename_folder()
- Path and name validation
- API endpoints: GET /api/ideas/tree, POST /api/ideas/upload, POST /api/ideas/rename
- Edge cases: empty directory, duplicate names, invalid characters
- Integration with file system operations
"""
import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from io import BytesIO

# Will be imported after implementation
# from src.services import IdeasService
# from src.app import create_app


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_ideas_dir(temp_project_dir):
    """Create temporary ideas directory structure"""
    ideas_path = Path(temp_project_dir) / 'docs' / 'ideas'
    ideas_path.mkdir(parents=True, exist_ok=True)
    return ideas_path


@pytest.fixture
def populated_ideas_dir(temp_ideas_dir):
    """Create ideas directory with sample folders and files"""
    # Create first idea folder
    idea1 = temp_ideas_dir / 'mobile-app-idea'
    files1 = idea1 / 'files'
    files1.mkdir(parents=True)
    (files1 / 'notes.md').write_text('# Mobile App Notes')
    (files1 / 'sketch.txt').write_text('UI sketch description')
    
    # Create second idea folder (draft format)
    idea2 = temp_ideas_dir / 'Draft Idea - 01202026 120000'
    idea2.mkdir(parents=True)
    (idea2 / 'brainstorm.md').write_text('# Brainstorming')
    
    return temp_ideas_dir


@pytest.fixture
def ideas_service(temp_project_dir):
    """Create IdeasService instance with temp directory"""
    from src.services import IdeasService
    return IdeasService(temp_project_dir)


@pytest.fixture
def ideas_service_populated(temp_project_dir, populated_ideas_dir):
    """Create IdeasService with populated ideas directory"""
    from src.services import IdeasService
    return IdeasService(temp_project_dir)


@pytest.fixture
def app(temp_project_dir, temp_ideas_dir):
    """Create Flask test app"""
    from src.app import create_app
    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': temp_project_dir,
        'SETTINGS_DB_PATH': os.path.join(temp_project_dir, 'test_settings.db')
    })
    return app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def populated_client(temp_project_dir, populated_ideas_dir):
    """Create Flask test client with populated ideas"""
    from src.app import create_app
    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': temp_project_dir,
        'SETTINGS_DB_PATH': os.path.join(temp_project_dir, 'test_settings.db')
    })
    return app.test_client()


# ============================================================================
# IdeasService Unit Tests - get_tree()
# ============================================================================

class TestIdeasServiceGetTree:
    """Unit tests for IdeasService.get_tree()"""

    def test_get_tree_creates_ideas_dir_if_not_exists(self, ideas_service, temp_project_dir):
        """get_tree() creates docs/ideas/ if it doesn't exist"""
        ideas_path = Path(temp_project_dir) / 'docs' / 'ideas'
        if ideas_path.exists():
            shutil.rmtree(ideas_path)
        
        result = ideas_service.get_tree()
        
        assert ideas_path.exists()
        assert result == []

    def test_get_tree_returns_empty_list_for_empty_dir(self, ideas_service, temp_ideas_dir):
        """get_tree() returns empty list for empty ideas directory"""
        result = ideas_service.get_tree()
        
        assert result == []

    def test_get_tree_returns_folder_structure(self, ideas_service_populated):
        """get_tree() returns correct folder structure"""
        result = ideas_service_populated.get_tree()
        
        assert len(result) == 2
        folder_names = [item['name'] for item in result]
        assert 'mobile-app-idea' in folder_names
        assert 'Draft Idea - 01202026 120000' in folder_names

    def test_get_tree_returns_files_within_folders(self, ideas_service_populated):
        """get_tree() includes files within folders"""
        result = ideas_service_populated.get_tree()
        
        mobile_app = next(item for item in result if item['name'] == 'mobile-app-idea')
        assert mobile_app['type'] == 'folder'
        assert 'children' in mobile_app
        
        # Check files folder
        files_folder = next((c for c in mobile_app['children'] if c['name'] == 'files'), None)
        assert files_folder is not None
        assert files_folder['type'] == 'folder'

    def test_get_tree_returns_correct_path_format(self, ideas_service_populated):
        """get_tree() returns relative paths from project root"""
        result = ideas_service_populated.get_tree()
        
        mobile_app = next(item for item in result if item['name'] == 'mobile-app-idea')
        assert mobile_app['path'] == 'docs/ideas/mobile-app-idea'

    def test_get_tree_sorts_alphabetically(self, ideas_service_populated):
        """get_tree() returns items sorted alphabetically"""
        result = ideas_service_populated.get_tree()
        
        names = [item['name'] for item in result]
        assert names == sorted(names)


# ============================================================================
# IdeasService Unit Tests - upload()
# ============================================================================

class TestIdeasServiceUpload:
    """Unit tests for IdeasService.upload()"""

    def test_upload_creates_folder_with_date_format(self, ideas_service, temp_ideas_dir):
        """upload() creates folder with 'Draft Idea - MMDDYYYY HHMMSS' format"""
        files = [('test.md', b'# Test content')]
        
        result = ideas_service.upload(files)
        
        assert result['success'] is True
        # Check folder starts with 'Draft Idea - ' and contains date
        assert result['folder_name'].startswith('Draft Idea - ')

    def test_upload_stores_files_directly_in_folder(self, ideas_service, temp_ideas_dir):
        """upload() stores files directly in idea folder (not in subfolder)"""
        files = [('test.md', b'# Test content')]
        
        result = ideas_service.upload(files)
        
        # Files should be directly in folder, not in 'files' subfolder
        file_path = temp_ideas_dir / result['folder_name'] / 'test.md'
        assert file_path.exists()
        assert file_path.is_file()

    def test_upload_stores_file_content(self, ideas_service, temp_ideas_dir):
        """upload() correctly saves file content"""
        content = b'# My Test Notes\n\nSome content here.'
        files = [('notes.md', content)]
        
        result = ideas_service.upload(files)
        
        file_path = temp_ideas_dir / result['folder_name'] / 'notes.md'
        assert file_path.exists()
        assert file_path.read_bytes() == content

    def test_upload_multiple_files(self, ideas_service, temp_ideas_dir):
        """upload() handles multiple files"""
        files = [
            ('file1.md', b'Content 1'),
            ('file2.txt', b'Content 2'),
            ('file3.py', b'print("hello")')
        ]
        
        result = ideas_service.upload(files)
        
        assert result['success'] is True
        assert len(result['files_uploaded']) == 3
        assert 'file1.md' in result['files_uploaded']
        assert 'file2.txt' in result['files_uploaded']
        assert 'file3.py' in result['files_uploaded']

    def test_upload_generates_unique_folder_name(self, ideas_service, temp_ideas_dir):
        """upload() generates unique name if folder exists"""
        # Create first folder with specific datetime
        timestamp = '01222026 114800'
        first_folder = temp_ideas_dir / f'Draft Idea - {timestamp}'
        first_folder.mkdir(parents=True)
        
        # Upload with same datetime
        files = [('test.md', b'# Test')]
        result = ideas_service.upload(files, date=timestamp)
        
        assert result['success'] is True
        assert result['folder_name'] == f'Draft Idea - {timestamp} (2)'

    def test_upload_returns_folder_path(self, ideas_service, temp_ideas_dir):
        """upload() returns relative folder path"""
        files = [('test.md', b'# Test')]
        
        result = ideas_service.upload(files)
        
        assert result['folder_path'].startswith('docs/ideas/')

    def test_upload_handles_binary_files(self, ideas_service, temp_ideas_dir):
        """upload() handles binary files (images, etc.)"""
        binary_content = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])  # PNG header
        files = [('image.png', binary_content)]
        
        result = ideas_service.upload(files)
        
        assert result['success'] is True
        file_path = temp_ideas_dir / result['folder_name'] / 'image.png'
        assert file_path.read_bytes() == binary_content


# ============================================================================
# IdeasService Unit Tests - rename_folder()
# ============================================================================

class TestIdeasServiceRenameFolder:
    """Unit tests for IdeasService.rename_folder()"""

    def test_rename_folder_changes_directory_name(self, ideas_service_populated, populated_ideas_dir):
        """rename_folder() changes physical directory name"""
        result = ideas_service_populated.rename_folder('mobile-app-idea', 'new-name')
        
        assert result['success'] is True
        assert not (populated_ideas_dir / 'mobile-app-idea').exists()
        assert (populated_ideas_dir / 'new-name').exists()

    def test_rename_folder_preserves_contents(self, ideas_service_populated, populated_ideas_dir):
        """rename_folder() preserves folder contents"""
        ideas_service_populated.rename_folder('mobile-app-idea', 'renamed-idea')
        
        new_path = populated_ideas_dir / 'renamed-idea' / 'files' / 'notes.md'
        assert new_path.exists()
        assert new_path.read_text() == '# Mobile App Notes'

    def test_rename_folder_returns_new_path(self, ideas_service_populated):
        """rename_folder() returns new relative path"""
        result = ideas_service_populated.rename_folder('mobile-app-idea', 'renamed')
        
        assert result['new_path'] == 'docs/ideas/renamed'

    def test_rename_folder_invalid_name_slash(self, ideas_service_populated):
        """rename_folder() rejects names with slash"""
        result = ideas_service_populated.rename_folder('mobile-app-idea', 'invalid/name')
        
        assert result['success'] is False
        assert 'invalid characters' in result['error'].lower()

    def test_rename_folder_invalid_name_backslash(self, ideas_service_populated):
        """rename_folder() rejects names with backslash"""
        result = ideas_service_populated.rename_folder('mobile-app-idea', 'invalid\\name')
        
        assert result['success'] is False
        assert 'invalid characters' in result['error'].lower()

    def test_rename_folder_invalid_name_colon(self, ideas_service_populated):
        """rename_folder() rejects names with colon"""
        result = ideas_service_populated.rename_folder('mobile-app-idea', 'invalid:name')
        
        assert result['success'] is False
        assert 'invalid characters' in result['error'].lower()

    def test_rename_folder_invalid_name_special_chars(self, ideas_service_populated):
        """rename_folder() rejects names with special characters (* ? \" < > |)"""
        invalid_names = ['name*star', 'name?question', 'name"quote', 'name<less', 'name>more', 'name|pipe']
        
        for invalid_name in invalid_names:
            result = ideas_service_populated.rename_folder('mobile-app-idea', invalid_name)
            assert result['success'] is False

    def test_rename_folder_nonexistent_folder(self, ideas_service_populated):
        """rename_folder() returns error for non-existent folder"""
        result = ideas_service_populated.rename_folder('nonexistent-folder', 'new-name')
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower() or 'does not exist' in result['error'].lower()

    def test_rename_folder_generates_unique_name(self, ideas_service_populated, populated_ideas_dir):
        """rename_folder() appends counter if target name exists"""
        result = ideas_service_populated.rename_folder('mobile-app-idea', 'Draft Idea - 01202026 120000')
        
        assert result['success'] is True
        assert result['new_name'] == 'Draft Idea - 01202026 120000 (2)'

    def test_rename_folder_max_length(self, ideas_service_populated):
        """rename_folder() rejects names > 255 characters"""
        long_name = 'a' * 256
        
        result = ideas_service_populated.rename_folder('mobile-app-idea', long_name)
        
        assert result['success'] is False
        assert 'too long' in result['error'].lower()

    def test_rename_folder_strips_whitespace(self, ideas_service_populated, populated_ideas_dir):
        """rename_folder() strips leading/trailing whitespace"""
        result = ideas_service_populated.rename_folder('mobile-app-idea', '  clean-name  ')
        
        assert result['success'] is True
        assert result['new_name'] == 'clean-name'
        assert (populated_ideas_dir / 'clean-name').exists()


# ============================================================================
# API Tests - GET /api/ideas/tree
# ============================================================================

class TestIdeasTreeAPI:
    """API tests for GET /api/ideas/tree"""

    def test_get_tree_returns_200(self, client):
        """GET /api/ideas/tree returns 200 OK"""
        response = client.get('/api/ideas/tree')
        
        assert response.status_code == 200

    def test_get_tree_returns_json(self, client):
        """GET /api/ideas/tree returns JSON response"""
        response = client.get('/api/ideas/tree')
        data = json.loads(response.data)
        
        assert 'success' in data
        assert 'tree' in data

    def test_get_tree_empty_directory(self, client):
        """GET /api/ideas/tree returns empty array for empty directory"""
        response = client.get('/api/ideas/tree')
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['tree'] == []

    def test_get_tree_with_folders(self, populated_client):
        """GET /api/ideas/tree returns folder structure"""
        response = populated_client.get('/api/ideas/tree')
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert len(data['tree']) == 2


# ============================================================================
# API Tests - POST /api/ideas/upload
# ============================================================================

class TestIdeasUploadAPI:
    """API tests for POST /api/ideas/upload"""

    def test_upload_returns_200(self, client):
        """POST /api/ideas/upload returns 200 OK"""
        data = {'files': (BytesIO(b'test content'), 'test.md')}
        response = client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200

    def test_upload_returns_json(self, client):
        """POST /api/ideas/upload returns JSON response"""
        data = {'files': (BytesIO(b'test content'), 'test.md')}
        response = client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        result = json.loads(response.data)
        
        assert 'success' in result

    def test_upload_creates_folder(self, client, temp_project_dir):
        """POST /api/ideas/upload creates idea folder"""
        data = {'files': (BytesIO(b'test content'), 'test.md')}
        response = client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        result = json.loads(response.data)
        
        assert result['success'] is True
        folder_path = Path(temp_project_dir) / 'docs' / 'ideas' / result['folder_name']
        assert folder_path.exists()

    def test_upload_multiple_files(self, client):
        """POST /api/ideas/upload handles multiple files"""
        data = {
            'files': [
                (BytesIO(b'content 1'), 'file1.md'),
                (BytesIO(b'content 2'), 'file2.txt')
            ]
        }
        response = client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert len(result['files_uploaded']) == 2

    def test_upload_no_files_returns_error(self, client):
        """POST /api/ideas/upload returns error when no files provided"""
        response = client.post('/api/ideas/upload', data={}, content_type='multipart/form-data')
        result = json.loads(response.data)
        
        assert result['success'] is False
        assert 'no files' in result['error'].lower()


# ============================================================================
# API Tests - POST /api/ideas/rename
# ============================================================================

class TestIdeasRenameAPI:
    """API tests for POST /api/ideas/rename"""

    def test_rename_returns_200(self, populated_client):
        """POST /api/ideas/rename returns 200 OK"""
        response = populated_client.post('/api/ideas/rename', 
            data=json.dumps({'old_name': 'mobile-app-idea', 'new_name': 'renamed'}),
            content_type='application/json')
        
        assert response.status_code == 200

    def test_rename_returns_json(self, populated_client):
        """POST /api/ideas/rename returns JSON response"""
        response = populated_client.post('/api/ideas/rename',
            data=json.dumps({'old_name': 'mobile-app-idea', 'new_name': 'renamed'}),
            content_type='application/json')
        result = json.loads(response.data)
        
        assert 'success' in result

    def test_rename_changes_folder(self, populated_client, temp_project_dir, populated_ideas_dir):
        """POST /api/ideas/rename renames folder on disk"""
        response = populated_client.post('/api/ideas/rename',
            data=json.dumps({'old_name': 'mobile-app-idea', 'new_name': 'new-idea-name'}),
            content_type='application/json')
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert not (populated_ideas_dir / 'mobile-app-idea').exists()
        assert (populated_ideas_dir / 'new-idea-name').exists()

    def test_rename_invalid_name_returns_error(self, populated_client):
        """POST /api/ideas/rename returns error for invalid name"""
        response = populated_client.post('/api/ideas/rename',
            data=json.dumps({'old_name': 'mobile-app-idea', 'new_name': 'invalid/name'}),
            content_type='application/json')
        result = json.loads(response.data)
        
        assert result['success'] is False

    def test_rename_missing_params_returns_error(self, populated_client):
        """POST /api/ideas/rename returns error when params missing"""
        response = populated_client.post('/api/ideas/rename',
            data=json.dumps({'old_name': 'mobile-app-idea'}),
            content_type='application/json')
        result = json.loads(response.data)
        
        assert result['success'] is False


# ============================================================================
# Integration Tests
# ============================================================================

class TestIdeasIntegration:
    """Integration tests for Workplace feature"""

    def test_upload_then_tree_shows_new_folder(self, client, temp_project_dir):
        """Upload creates folder that appears in tree"""
        # Upload a file
        data = {'files': (BytesIO(b'# New Idea'), 'idea.md')}
        upload_response = client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        upload_result = json.loads(upload_response.data)
        
        # Get tree
        tree_response = client.get('/api/ideas/tree')
        tree_result = json.loads(tree_response.data)
        
        folder_names = [item['name'] for item in tree_result['tree']]
        assert upload_result['folder_name'] in folder_names

    def test_rename_then_tree_shows_new_name(self, populated_client):
        """Rename updates folder name in tree"""
        # Rename folder
        rename_response = populated_client.post('/api/ideas/rename',
            data=json.dumps({'old_name': 'mobile-app-idea', 'new_name': 'my-great-idea'}),
            content_type='application/json')
        
        # Get tree
        tree_response = populated_client.get('/api/ideas/tree')
        tree_result = json.loads(tree_response.data)
        
        folder_names = [item['name'] for item in tree_result['tree']]
        assert 'my-great-idea' in folder_names
        assert 'mobile-app-idea' not in folder_names

    def test_upload_then_read_file_content(self, client, temp_project_dir):
        """Uploaded file can be read via content API"""
        content = b'# My Test Idea\n\nThis is the content.'
        data = {'files': (BytesIO(content), 'notes.md')}
        upload_response = client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        upload_result = json.loads(upload_response.data)
        
        # Read the file via existing content API (files directly in folder, not in subfolder)
        file_path = f"docs/ideas/{upload_result['folder_name']}/notes.md"
        content_response = client.get(f'/api/file/content?path={file_path}')
        content_result = json.loads(content_response.data)
        
        # Existing content API returns content directly, not success field
        assert 'content' in content_result
        assert '# My Test Idea' in content_result['content']
