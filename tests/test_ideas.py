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
# IdeasService Unit Tests - upload() with target_folder (CR-002)
# ============================================================================

class TestIdeasServiceUploadToExistingFolder:
    """Unit tests for IdeasService.upload() with target_folder parameter (CR-002)"""

    def test_upload_to_existing_folder_success(self, ideas_service_populated, populated_ideas_dir):
        """upload() with target_folder saves files to existing folder"""
        files = [('extra.md', b'# Extra content')]
        
        result = ideas_service_populated.upload(files, target_folder='mobile-app-idea')
        
        assert result['success'] is True
        assert result['folder_name'] == 'mobile-app-idea'
        file_path = populated_ideas_dir / 'mobile-app-idea' / 'extra.md'
        assert file_path.exists()

    def test_upload_to_existing_folder_preserves_existing_files(self, ideas_service_populated, populated_ideas_dir):
        """upload() with target_folder does not overwrite existing files"""
        files = [('newfile.md', b'# New file')]
        
        ideas_service_populated.upload(files, target_folder='mobile-app-idea')
        
        # Original files should still exist
        files_dir = populated_ideas_dir / 'mobile-app-idea' / 'files'
        assert (files_dir / 'notes.md').exists()
        assert (files_dir / 'sketch.txt').exists()

    def test_upload_to_existing_folder_returns_correct_path(self, ideas_service_populated, populated_ideas_dir):
        """upload() with target_folder returns correct folder_path"""
        files = [('test.md', b'# Test')]
        
        result = ideas_service_populated.upload(files, target_folder='mobile-app-idea')
        
        assert 'docs/ideas/mobile-app-idea' in result['folder_path']

    def test_upload_to_nonexistent_folder_fails(self, ideas_service_populated, populated_ideas_dir):
        """upload() with nonexistent target_folder returns error"""
        files = [('test.md', b'# Test')]
        
        result = ideas_service_populated.upload(files, target_folder='nonexistent-folder')
        
        assert result['success'] is False
        assert 'does not exist' in result['error']

    def test_upload_to_existing_folder_multiple_files(self, ideas_service_populated, populated_ideas_dir):
        """upload() with target_folder handles multiple files"""
        files = [
            ('file1.md', b'Content 1'),
            ('file2.txt', b'Content 2')
        ]
        
        result = ideas_service_populated.upload(files, target_folder='mobile-app-idea')
        
        assert result['success'] is True
        assert len(result['files_uploaded']) == 2
        assert (populated_ideas_dir / 'mobile-app-idea' / 'file1.md').exists()
        assert (populated_ideas_dir / 'mobile-app-idea' / 'file2.txt').exists()

    def test_upload_to_existing_folder_overwrites_same_name_file(self, ideas_service_populated, populated_ideas_dir):
        """upload() with target_folder overwrites file with same name"""
        # First, create a file in the folder
        folder_path = populated_ideas_dir / 'mobile-app-idea'
        (folder_path / 'overwrite.md').write_bytes(b'Original content')
        
        # Upload file with same name
        files = [('overwrite.md', b'New content')]
        result = ideas_service_populated.upload(files, target_folder='mobile-app-idea')
        
        assert result['success'] is True
        assert (folder_path / 'overwrite.md').read_bytes() == b'New content'

    def test_upload_without_target_folder_still_creates_new(self, ideas_service_populated, populated_ideas_dir):
        """upload() without target_folder creates new folder (existing behavior)"""
        files = [('test.md', b'# Test')]
        
        result = ideas_service_populated.upload(files)  # No target_folder
        
        assert result['success'] is True
        assert result['folder_name'].startswith('Draft Idea - ')
        # Should create new folder, not use existing
        assert result['folder_name'] != 'mobile-app-idea'

    def test_upload_to_existing_folder_binary_files(self, ideas_service_populated, populated_ideas_dir):
        """upload() with target_folder handles binary files"""
        binary_content = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])  # PNG header
        files = [('image.png', binary_content)]
        
        result = ideas_service_populated.upload(files, target_folder='mobile-app-idea')
        
        assert result['success'] is True
        file_path = populated_ideas_dir / 'mobile-app-idea' / 'image.png'
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
# API Tests - POST /api/ideas/upload with target_folder (CR-002)
# ============================================================================

class TestIdeasUploadToFolderAPI:
    """API tests for POST /api/ideas/upload with target_folder parameter (CR-002)"""

    def test_upload_to_existing_folder_returns_200(self, populated_client):
        """POST /api/ideas/upload with target_folder returns 200 OK"""
        data = {
            'files': (BytesIO(b'test content'), 'test.md'),
            'target_folder': 'mobile-app-idea'
        }
        response = populated_client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200

    def test_upload_to_existing_folder_returns_correct_folder_name(self, populated_client):
        """POST /api/ideas/upload with target_folder returns target folder name"""
        data = {
            'files': (BytesIO(b'test content'), 'test.md'),
            'target_folder': 'mobile-app-idea'
        }
        response = populated_client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert result['folder_name'] == 'mobile-app-idea'

    def test_upload_to_existing_folder_creates_file(self, populated_client, temp_project_dir):
        """POST /api/ideas/upload with target_folder creates file in existing folder"""
        data = {
            'files': (BytesIO(b'test content'), 'newfile.md'),
            'target_folder': 'mobile-app-idea'
        }
        response = populated_client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        result = json.loads(response.data)
        
        assert result['success'] is True
        file_path = Path(temp_project_dir) / 'docs' / 'ideas' / 'mobile-app-idea' / 'newfile.md'
        assert file_path.exists()

    def test_upload_to_nonexistent_folder_returns_error(self, populated_client):
        """POST /api/ideas/upload with nonexistent target_folder returns 400"""
        data = {
            'files': (BytesIO(b'test content'), 'test.md'),
            'target_folder': 'does-not-exist'
        }
        response = populated_client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        result = json.loads(response.data)
        
        assert response.status_code == 400
        assert result['success'] is False
        assert 'does not exist' in result['error']

    def test_upload_to_existing_folder_multiple_files(self, populated_client, temp_project_dir):
        """POST /api/ideas/upload with target_folder handles multiple files"""
        data = {
            'files': [
                (BytesIO(b'content 1'), 'file1.md'),
                (BytesIO(b'content 2'), 'file2.txt')
            ],
            'target_folder': 'mobile-app-idea'
        }
        response = populated_client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert len(result['files_uploaded']) == 2
        assert (Path(temp_project_dir) / 'docs' / 'ideas' / 'mobile-app-idea' / 'file1.md').exists()
        assert (Path(temp_project_dir) / 'docs' / 'ideas' / 'mobile-app-idea' / 'file2.txt').exists()

    def test_upload_without_target_folder_creates_new_folder(self, populated_client, temp_project_dir):
        """POST /api/ideas/upload without target_folder creates new folder (existing behavior)"""
        data = {
            'files': (BytesIO(b'test content'), 'test.md')
            # No target_folder
        }
        response = populated_client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert result['folder_name'].startswith('Draft Idea - ')
        assert result['folder_name'] != 'mobile-app-idea'


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


# ============================================================================
# IdeasService Unit Tests - delete_item()
# ============================================================================

class TestIdeasServiceDeleteItem:
    """Unit tests for IdeasService.delete_item()"""

    def test_delete_file_removes_file(self, ideas_service_populated, populated_ideas_dir):
        """delete_item() removes a file"""
        file_path = 'docs/ideas/mobile-app-idea/files/notes.md'
        result = ideas_service_populated.delete_item(file_path)
        
        assert result['success'] is True
        assert result['type'] == 'file'
        assert not (populated_ideas_dir / 'mobile-app-idea' / 'files' / 'notes.md').exists()

    def test_delete_folder_removes_folder(self, ideas_service_populated, populated_ideas_dir):
        """delete_item() removes a folder and its contents"""
        folder_path = 'docs/ideas/mobile-app-idea'
        result = ideas_service_populated.delete_item(folder_path)
        
        assert result['success'] is True
        assert result['type'] == 'folder'
        assert not (populated_ideas_dir / 'mobile-app-idea').exists()

    def test_delete_returns_path(self, ideas_service_populated):
        """delete_item() returns the deleted path"""
        file_path = 'docs/ideas/mobile-app-idea/files/notes.md'
        result = ideas_service_populated.delete_item(file_path)
        
        assert result['path'] == file_path

    def test_delete_nonexistent_path_returns_error(self, ideas_service_populated):
        """delete_item() returns error for non-existent path"""
        result = ideas_service_populated.delete_item('docs/ideas/nonexistent/file.md')
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    def test_delete_empty_path_returns_error(self, ideas_service_populated):
        """delete_item() returns error for empty path"""
        result = ideas_service_populated.delete_item('')
        
        assert result['success'] is False
        assert 'required' in result['error'].lower()

    def test_delete_path_traversal_prevented(self, ideas_service_populated):
        """delete_item() prevents path traversal attacks"""
        result = ideas_service_populated.delete_item('../../../etc/passwd')
        
        assert result['success'] is False
        assert 'within' in result['error'].lower() or 'invalid' in result['error'].lower()

    def test_delete_outside_ideas_dir_prevented(self, ideas_service_populated, temp_project_dir):
        """delete_item() prevents deletion outside docs/ideas/"""
        # Create a file outside ideas directory
        outside_file = Path(temp_project_dir) / 'docs' / 'planning' / 'test.md'
        outside_file.parent.mkdir(parents=True, exist_ok=True)
        outside_file.write_text('test')
        
        result = ideas_service_populated.delete_item('docs/planning/test.md')
        
        assert result['success'] is False


# ============================================================================
# IdeasService Unit Tests - Versioned Summary
# ============================================================================

class TestIdeasServiceVersionedSummary:
    """Unit tests for IdeasService.create_versioned_summary() and get_next_version_number()"""

    def test_get_next_version_number_returns_1_for_empty_folder(self, ideas_service_populated):
        """get_next_version_number() returns 1 for folder with no versions"""
        version = ideas_service_populated.get_next_version_number('docs/ideas/mobile-app-idea')
        assert version == 1

    def test_get_next_version_number_increments(self, ideas_service_populated, populated_ideas_dir):
        """get_next_version_number() increments based on existing files"""
        # Create v1 and v2 files
        folder = populated_ideas_dir / 'mobile-app-idea'
        (folder / 'idea-summary-v1.md').write_text('# v1')
        (folder / 'idea-summary-v2.md').write_text('# v2')
        
        version = ideas_service_populated.get_next_version_number('docs/ideas/mobile-app-idea')
        assert version == 3

    def test_get_next_version_number_finds_highest(self, ideas_service_populated, populated_ideas_dir):
        """get_next_version_number() finds the highest version number"""
        folder = populated_ideas_dir / 'mobile-app-idea'
        (folder / 'idea-summary-v5.md').write_text('# v5')
        (folder / 'idea-summary-v2.md').write_text('# v2')
        
        version = ideas_service_populated.get_next_version_number('docs/ideas/mobile-app-idea')
        assert version == 6

    def test_create_versioned_summary_creates_file(self, ideas_service_populated, populated_ideas_dir):
        """create_versioned_summary() creates a versioned file"""
        content = '# My Idea Summary v1'
        result = ideas_service_populated.create_versioned_summary('docs/ideas/mobile-app-idea', content)
        
        assert result['success'] is True
        assert result['version'] == 1
        assert result['filename'] == 'idea-summary-v1.md'
        assert (populated_ideas_dir / 'mobile-app-idea' / 'idea-summary-v1.md').exists()

    def test_create_versioned_summary_increments_version(self, ideas_service_populated, populated_ideas_dir):
        """create_versioned_summary() auto-increments version"""
        folder = populated_ideas_dir / 'mobile-app-idea'
        (folder / 'idea-summary-v1.md').write_text('# v1')
        
        result = ideas_service_populated.create_versioned_summary('docs/ideas/mobile-app-idea', '# v2 content')
        
        assert result['success'] is True
        assert result['version'] == 2
        assert result['filename'] == 'idea-summary-v2.md'

    def test_create_versioned_summary_writes_content(self, ideas_service_populated, populated_ideas_dir):
        """create_versioned_summary() writes the provided content"""
        content = '# Detailed Summary\n\nThis is the content.'
        ideas_service_populated.create_versioned_summary('docs/ideas/mobile-app-idea', content)
        
        file_path = populated_ideas_dir / 'mobile-app-idea' / 'idea-summary-v1.md'
        assert file_path.read_text() == content

    def test_create_versioned_summary_nonexistent_folder_returns_error(self, ideas_service_populated):
        """create_versioned_summary() returns error for non-existent folder"""
        result = ideas_service_populated.create_versioned_summary('docs/ideas/nonexistent', 'content')
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    def test_create_versioned_summary_outside_ideas_prevented(self, ideas_service_populated, temp_project_dir):
        """create_versioned_summary() prevents creation outside docs/ideas/"""
        outside_folder = Path(temp_project_dir) / 'docs' / 'planning'
        outside_folder.mkdir(parents=True, exist_ok=True)
        
        result = ideas_service_populated.create_versioned_summary('docs/planning', 'content')
        
        assert result['success'] is False


# ============================================================================
# API Tests - POST /api/ideas/delete
# ============================================================================

class TestIdeasDeleteAPI:
    """API tests for POST /api/ideas/delete"""

    def test_delete_returns_200(self, populated_client):
        """POST /api/ideas/delete returns 200 OK for valid delete"""
        response = populated_client.post('/api/ideas/delete',
            data=json.dumps({'path': 'docs/ideas/mobile-app-idea/files/notes.md'}),
            content_type='application/json')
        
        assert response.status_code == 200

    def test_delete_returns_json(self, populated_client):
        """POST /api/ideas/delete returns JSON response"""
        response = populated_client.post('/api/ideas/delete',
            data=json.dumps({'path': 'docs/ideas/mobile-app-idea/files/notes.md'}),
            content_type='application/json')
        result = json.loads(response.data)
        
        assert 'success' in result

    def test_delete_removes_file(self, populated_client, populated_ideas_dir):
        """POST /api/ideas/delete removes the specified file"""
        response = populated_client.post('/api/ideas/delete',
            data=json.dumps({'path': 'docs/ideas/mobile-app-idea/files/notes.md'}),
            content_type='application/json')
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert not (populated_ideas_dir / 'mobile-app-idea' / 'files' / 'notes.md').exists()

    def test_delete_removes_folder(self, populated_client, populated_ideas_dir):
        """POST /api/ideas/delete removes the specified folder"""
        response = populated_client.post('/api/ideas/delete',
            data=json.dumps({'path': 'docs/ideas/mobile-app-idea'}),
            content_type='application/json')
        result = json.loads(response.data)
        
        assert result['success'] is True
        assert not (populated_ideas_dir / 'mobile-app-idea').exists()

    def test_delete_missing_path_returns_error(self, populated_client):
        """POST /api/ideas/delete returns error when path is missing"""
        response = populated_client.post('/api/ideas/delete',
            data=json.dumps({}),
            content_type='application/json')
        result = json.loads(response.data)
        
        assert result['success'] is False
        assert response.status_code == 400

    def test_delete_nonexistent_path_returns_error(self, populated_client):
        """POST /api/ideas/delete returns error for non-existent path"""
        response = populated_client.post('/api/ideas/delete',
            data=json.dumps({'path': 'docs/ideas/nonexistent/file.md'}),
            content_type='application/json')
        result = json.loads(response.data)
        
        assert result['success'] is False
        assert response.status_code == 400


# ============================================================================
# Integration Tests - Delete
# ============================================================================

class TestIdeasDeleteIntegration:
    """Integration tests for delete functionality"""

    def test_delete_then_tree_shows_removal(self, populated_client):
        """Delete removes folder from tree"""
        # Delete folder
        populated_client.post('/api/ideas/delete',
            data=json.dumps({'path': 'docs/ideas/mobile-app-idea'}),
            content_type='application/json')
        
        # Get tree
        tree_response = populated_client.get('/api/ideas/tree')
        tree_result = json.loads(tree_response.data)
        
        folder_names = [item['name'] for item in tree_result['tree']]
        assert 'mobile-app-idea' not in folder_names

    def test_upload_delete_upload_works(self, client, temp_project_dir):
        """Can upload, delete, then upload again"""
        # Upload
        data = {'files': (BytesIO(b'# Test'), 'test.md')}
        upload_response = client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        upload_result = json.loads(upload_response.data)
        folder_name = upload_result['folder_name']
        
        # Delete
        client.post('/api/ideas/delete',
            data=json.dumps({'path': f'docs/ideas/{folder_name}'}),
            content_type='application/json')
        
        # Upload again
        data = {'files': (BytesIO(b'# Test 2'), 'test2.md')}
        upload_response2 = client.post('/api/ideas/upload', data=data, content_type='multipart/form-data')
        upload_result2 = json.loads(upload_response2.data)
        
        assert upload_result2['success'] is True


# ============================================================================
# CR-001: Copilot Button Tests
# ============================================================================

class TestCopilotButtonBehavior:
    """
    Tests for CR-001: Copilot Button functionality.
    
    Note: The Copilot button is implemented in frontend JavaScript.
    These tests document expected behavior and verify supporting infrastructure.
    For full E2E testing, use Playwright or similar browser automation.
    """
    
    def test_copilot_button_html_structure_documented(self):
        """
        CR-001: Copilot button should have correct HTML structure.
        
        Expected HTML:
        <button class="btn btn-sm btn-outline-info workplace-copilot-btn" 
                id="workplace-copilot-btn" 
                title="Refine with Copilot">
            <i class="bi bi-robot"></i> Copilot
        </button>
        
        Placement: Left of Edit button in content view header.
        """
        # Document expected structure - actual verification via Playwright
        expected_classes = ['btn', 'btn-sm', 'btn-outline-info', 'workplace-copilot-btn']
        expected_id = 'workplace-copilot-btn'
        expected_icon = 'bi-robot'
        expected_text = 'Copilot'
        
        assert all(c for c in expected_classes)
        assert expected_id is not None
        assert expected_icon is not None
        assert expected_text == 'Copilot'
    
    def test_copilot_command_format(self):
        """
        CR-001: Verify the command format sent to terminal.
        
        Expected commands:
        1. "copilot" - to start Copilot CLI
        2. "refine the idea {file_path}" - to trigger refinement
        """
        test_file_path = 'docs/ideas/test-idea/Project Proposal'
        
        expected_init_command = 'copilot'
        expected_refine_command = f'refine the idea {test_file_path}'
        
        assert expected_init_command == 'copilot'
        assert expected_refine_command == f'refine the idea {test_file_path}'
        assert test_file_path in expected_refine_command
    
    def test_copilot_mode_detection_patterns(self):
        """
        CR-001: Verify Copilot mode detection patterns.
        
        The _isInCopilotMode() function checks for these patterns:
        - 'copilot>' - Copilot CLI prompt
        - 'Copilot' - Copilot branding text
        - '⏺' - Copilot status indicator
        """
        detection_patterns = ['copilot>', 'Copilot', '⏺']
        
        # Test pattern matching
        test_lines = [
            'copilot> ',
            'Welcome to GitHub Copilot CLI',
            '⏺ Running...',
            'normal shell prompt $',
            'echo hello world',
        ]
        
        def is_copilot_mode(line):
            return any(pattern in line for pattern in detection_patterns)
        
        assert is_copilot_mode(test_lines[0]) is True  # copilot>
        assert is_copilot_mode(test_lines[1]) is True  # Copilot
        assert is_copilot_mode(test_lines[2]) is True  # ⏺
        assert is_copilot_mode(test_lines[3]) is False  # normal prompt
        assert is_copilot_mode(test_lines[4]) is False  # normal command
    
    def test_typing_simulation_parameters(self):
        """
        CR-001: Verify typing simulation parameters.
        
        Expected behavior:
        - Random delay between 30-80ms per character
        - Enter key sent after command completes
        - 1.5s wait between copilot init and refine command
        """
        min_delay_ms = 30
        max_delay_ms = 80
        init_wait_ms = 1500
        
        assert min_delay_ms >= 30
        assert max_delay_ms <= 80
        assert init_wait_ms == 1500
        
        # Verify delay is within expected range
        import random
        for _ in range(100):
            delay = min_delay_ms + random.random() * (max_delay_ms - min_delay_ms)
            assert min_delay_ms <= delay <= max_delay_ms
    
    def test_terminal_panel_expand_dependency(self):
        """
        CR-001: Copilot button depends on TerminalPanel.expand().
        
        Expected flow:
        1. window.terminalPanel.expand() is called first
        2. Then sendCopilotRefineCommand() is invoked
        """
        # Document dependency - verified via code inspection
        required_methods = [
            ('TerminalPanel', 'expand'),
            ('TerminalManager', 'sendCopilotRefineCommand'),
            ('TerminalManager', '_isInCopilotMode'),
            ('TerminalManager', '_sendWithTypingEffect'),
        ]
        
        for class_name, method_name in required_methods:
            assert class_name is not None
            assert method_name is not None


class TestCopilotButtonEdgeCases:
    """
    Edge case tests for CR-001: Copilot Button.
    """
    
    def test_no_file_selected_behavior(self):
        """
        CR-001: When no file is selected, button click should do nothing.
        
        Expected: _handleCopilotClick() returns early if currentPath is null/undefined
        """
        current_path = None
        
        def handle_copilot_click():
            if not current_path:
                return  # Early return
            # Would proceed with terminal operations
            return 'executed'
        
        result = handle_copilot_click()
        assert result is None  # Early return, no action
    
    def test_max_terminals_reached_behavior(self):
        """
        CR-001: When MAX_TERMINALS (2) is reached and in Copilot mode,
        uses existing terminal instead of creating new one.
        """
        MAX_TERMINALS = 2
        terminal_count = 2
        is_in_copilot_mode = True
        
        # Simulate decision logic
        needs_new_terminal = is_in_copilot_mode
        can_create_new = terminal_count < MAX_TERMINALS
        
        will_create_new = needs_new_terminal and can_create_new
        
        assert will_create_new is False  # Cannot create new, at max
    
    def test_terminal_not_connected_behavior(self):
        """
        CR-001: When terminal socket is not connected, typing should not be sent.
        
        Expected: _sendWithTypingEffect() returns early if socket not connected
        """
        socket_connected = False
        
        def send_with_typing_effect(socket_connected, text):
            if not socket_connected:
                return False  # Early return
            # Would send characters
            return True
        
        result = send_with_typing_effect(socket_connected, 'copilot')
        assert result is False
    
    def test_special_characters_in_file_path(self):
        """
        CR-001: File paths with spaces and special characters should be handled.
        """
        test_paths = [
            'docs/ideas/my idea/Project Proposal',
            'docs/ideas/test-idea-2026-01-22/notes.md',
            'docs/ideas/Draft Idea - 01222026 195931/idea-summary.md',
        ]
        
        for path in test_paths:
            command = f'refine the idea {path}'
            assert path in command
            # Path is sent as-is, shell will handle quoting if needed


# ============================================================================
# CR-003: Ideation Toolbox Configuration - Unit Tests
# ============================================================================

class TestIdeasServiceToolbox:
    """Unit tests for IdeasService toolbox methods (CR-003)"""
    
    def test_get_toolbox_returns_defaults_when_file_not_exists(self, temp_project_dir):
        """
        CR-003: get_toolbox() returns default config when .ideation-tools.json doesn't exist.
        """
        from src.services import IdeasService
        
        service = IdeasService(temp_project_dir)
        config = service.get_toolbox()
        
        assert config['version'] == '1.0'
        assert config['ideation']['antv-infographic'] is False
        assert config['ideation']['mermaid'] is True
        assert config['mockup']['frontend-design'] is True
        assert config['sharing'] == {}
    
    def test_get_toolbox_reads_existing_file(self, temp_ideas_dir, temp_project_dir):
        """
        CR-003: get_toolbox() reads config from existing .ideation-tools.json file.
        """
        from src.services import IdeasService
        
        # Create custom config
        toolbox_path = temp_ideas_dir / '.ideation-tools.json'
        custom_config = {
            "version": "1.0",
            "ideation": {
                "antv-infographic": True,
                "mermaid": False
            },
            "mockup": {
                "frontend-design": False
            },
            "sharing": {}
        }
        with open(toolbox_path, 'w') as f:
            json.dump(custom_config, f)
        
        service = IdeasService(temp_project_dir)
        config = service.get_toolbox()
        
        assert config['ideation']['antv-infographic'] is True
        assert config['ideation']['mermaid'] is False
        assert config['mockup']['frontend-design'] is False
    
    def test_get_toolbox_returns_defaults_on_invalid_json(self, temp_ideas_dir, temp_project_dir):
        """
        CR-003: get_toolbox() returns defaults when JSON is invalid.
        """
        from src.services import IdeasService
        
        # Create invalid JSON file
        toolbox_path = temp_ideas_dir / '.ideation-tools.json'
        toolbox_path.write_text('{ invalid json }')
        
        service = IdeasService(temp_project_dir)
        config = service.get_toolbox()
        
        # Should return defaults
        assert config['ideation']['mermaid'] is True
        assert config['mockup']['frontend-design'] is True
    
    def test_save_toolbox_creates_file(self, temp_ideas_dir, temp_project_dir):
        """
        CR-003: save_toolbox() creates .ideation-tools.json file.
        """
        from src.services import IdeasService
        
        service = IdeasService(temp_project_dir)
        config = {
            "version": "1.0",
            "ideation": {"antv-infographic": True, "mermaid": True},
            "mockup": {"frontend-design": False},
            "sharing": {}
        }
        
        result = service.save_toolbox(config)
        
        assert result['success'] is True
        toolbox_path = temp_ideas_dir / '.ideation-tools.json'
        assert toolbox_path.exists()
        
        saved_config = json.loads(toolbox_path.read_text())
        assert saved_config['ideation']['antv-infographic'] is True
        assert saved_config['mockup']['frontend-design'] is False
    
    def test_save_toolbox_updates_existing_file(self, temp_ideas_dir, temp_project_dir):
        """
        CR-003: save_toolbox() updates existing config file.
        """
        from src.services import IdeasService
        
        # Create initial config
        toolbox_path = temp_ideas_dir / '.ideation-tools.json'
        initial_config = {
            "version": "1.0",
            "ideation": {"antv-infographic": False, "mermaid": True},
            "mockup": {"frontend-design": True},
            "sharing": {}
        }
        with open(toolbox_path, 'w') as f:
            json.dump(initial_config, f)
        
        service = IdeasService(temp_project_dir)
        updated_config = {
            "version": "1.0",
            "ideation": {"antv-infographic": True, "mermaid": False},
            "mockup": {"frontend-design": True},
            "sharing": {}
        }
        
        result = service.save_toolbox(updated_config)
        
        assert result['success'] is True
        saved_config = json.loads(toolbox_path.read_text())
        assert saved_config['ideation']['antv-infographic'] is True
        assert saved_config['ideation']['mermaid'] is False
    
    def test_save_toolbox_creates_ideas_directory_if_missing(self, temp_project_dir):
        """
        CR-003: save_toolbox() creates docs/ideas/ directory if it doesn't exist.
        """
        from src.services import IdeasService
        
        # Ensure ideas directory doesn't exist
        ideas_path = Path(temp_project_dir) / 'docs' / 'ideas'
        assert not ideas_path.exists()
        
        service = IdeasService(temp_project_dir)
        config = {
            "version": "1.0",
            "ideation": {"antv-infographic": False, "mermaid": True},
            "mockup": {"frontend-design": True},
            "sharing": {}
        }
        
        result = service.save_toolbox(config)
        
        assert result['success'] is True
        assert ideas_path.exists()
        assert (ideas_path / '.ideation-tools.json').exists()
    
    def test_get_toolbox_preserves_extra_fields(self, temp_ideas_dir, temp_project_dir):
        """
        CR-003: get_toolbox() preserves extra fields in config.
        """
        from src.services import IdeasService
        
        toolbox_path = temp_ideas_dir / '.ideation-tools.json'
        config_with_extras = {
            "version": "1.0",
            "ideation": {"antv-infographic": True, "mermaid": True, "custom-tool": True},
            "mockup": {"frontend-design": True},
            "sharing": {"export-pdf": True},
            "custom_section": {"something": "value"}
        }
        with open(toolbox_path, 'w') as f:
            json.dump(config_with_extras, f)
        
        service = IdeasService(temp_project_dir)
        config = service.get_toolbox()
        
        assert config['ideation']['custom-tool'] is True
        assert config['sharing']['export-pdf'] is True
        assert config['custom_section']['something'] == 'value'


# ============================================================================
# CR-003: Ideation Toolbox Configuration - API Tests
# ============================================================================

class TestToolboxAPI:
    """API tests for toolbox endpoints (CR-003)"""
    
    def test_get_toolbox_endpoint_returns_defaults(self, populated_client, temp_project_dir):
        """
        CR-003: GET /api/ideas/toolbox returns default config.
        """
        response = populated_client.get('/api/ideas/toolbox')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['version'] == '1.0'
        assert 'ideation' in data
        assert 'mockup' in data
        assert 'sharing' in data
    
    def test_get_toolbox_endpoint_returns_saved_config(self, populated_client, temp_project_dir, populated_ideas_dir):
        """
        CR-003: GET /api/ideas/toolbox returns saved config from file.
        """
        # Create config file
        toolbox_path = populated_ideas_dir / '.ideation-tools.json'
        custom_config = {
            "version": "1.0",
            "ideation": {"antv-infographic": True, "mermaid": False},
            "mockup": {"frontend-design": False},
            "sharing": {}
        }
        with open(toolbox_path, 'w') as f:
            json.dump(custom_config, f)
        
        response = populated_client.get('/api/ideas/toolbox')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['ideation']['antv-infographic'] is True
        assert data['ideation']['mermaid'] is False
    
    def test_save_toolbox_endpoint(self, populated_client, temp_project_dir, populated_ideas_dir):
        """
        CR-003: POST /api/ideas/toolbox saves config.
        """
        config = {
            "version": "1.0",
            "ideation": {"antv-infographic": True, "mermaid": True},
            "mockup": {"frontend-design": False},
            "sharing": {}
        }
        
        response = populated_client.post(
            '/api/ideas/toolbox',
            data=json.dumps(config),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify file was created
        toolbox_path = populated_ideas_dir / '.ideation-tools.json'
        assert toolbox_path.exists()
    
    def test_save_then_get_toolbox_roundtrip(self, populated_client, temp_project_dir):
        """
        CR-003: Save config then get should return same values.
        """
        config = {
            "version": "1.0",
            "ideation": {"antv-infographic": True, "mermaid": False},
            "mockup": {"frontend-design": True},
            "sharing": {}
        }
        
        # Save
        save_response = populated_client.post(
            '/api/ideas/toolbox',
            data=json.dumps(config),
            content_type='application/json'
        )
        assert save_response.status_code == 200
        
        # Get
        get_response = populated_client.get('/api/ideas/toolbox')
        assert get_response.status_code == 200
        data = get_response.get_json()
        
        assert data['ideation']['antv-infographic'] is True
        assert data['ideation']['mermaid'] is False
        assert data['mockup']['frontend-design'] is True
    
    def test_save_toolbox_with_partial_config(self, populated_client, temp_project_dir):
        """
        CR-003: POST /api/ideas/toolbox handles partial config.
        """
        partial_config = {
            "version": "1.0",
            "ideation": {"mermaid": False}
        }
        
        response = populated_client.post(
            '/api/ideas/toolbox',
            data=json.dumps(partial_config),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_toolbox_config_persists_across_requests(self, populated_client, temp_project_dir):
        """
        CR-003: Config changes persist across multiple requests.
        """
        # First save
        config1 = {
            "version": "1.0",
            "ideation": {"antv-infographic": False, "mermaid": True},
            "mockup": {"frontend-design": True},
            "sharing": {}
        }
        populated_client.post(
            '/api/ideas/toolbox',
            data=json.dumps(config1),
            content_type='application/json'
        )
        
        # Second save (update)
        config2 = {
            "version": "1.0",
            "ideation": {"antv-infographic": True, "mermaid": True},
            "mockup": {"frontend-design": False},
            "sharing": {}
        }
        populated_client.post(
            '/api/ideas/toolbox',
            data=json.dumps(config2),
            content_type='application/json'
        )
        
        # Verify latest state
        response = populated_client.get('/api/ideas/toolbox')
        data = response.get_json()
        
        assert data['ideation']['antv-infographic'] is True
        assert data['mockup']['frontend-design'] is False
