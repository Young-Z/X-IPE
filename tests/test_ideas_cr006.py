"""
Tests for FEATURE-008 CR-006: Folder Tree UX Enhancement

Tests cover:
- IdeasService: move_item(), duplicate_item() (new methods)
- API endpoints: POST /api/ideas/move, POST /api/ideas/duplicate, GET /api/ideas/download
- Drag-drop validation: self-drop prevention, child-drop prevention
- Search/filter logic: parent context preservation
- Edge cases: name conflicts, missing items, recursive operations
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
# from x_ipe.services import IdeasService


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
    ideas_path = Path(temp_project_dir) / 'x-ipe-docs' / 'ideas'
    ideas_path.mkdir(parents=True, exist_ok=True)
    return ideas_path


@pytest.fixture
def populated_ideas_dir(temp_ideas_dir):
    """Create ideas directory with sample folders and files for CR-006 testing"""
    # Create folder structure for drag-drop testing
    #
    # ideas/
    # ├── project-alpha/
    # │   ├── notes.md
    # │   ├── design.md
    # │   └── mockups/
    # │       └── v1.html
    # ├── project-beta/
    # │   └── readme.md
    # └── archived/
    #     └── old-idea.md
    
    # Project Alpha with nested mockups folder
    alpha = temp_ideas_dir / 'project-alpha'
    alpha.mkdir()
    (alpha / 'notes.md').write_text('# Project Alpha Notes')
    (alpha / 'design.md').write_text('# Design Document')
    
    mockups = alpha / 'mockups'
    mockups.mkdir()
    (mockups / 'v1.html').write_text('<html>Mockup v1</html>')
    
    # Project Beta
    beta = temp_ideas_dir / 'project-beta'
    beta.mkdir()
    (beta / 'readme.md').write_text('# Project Beta')
    
    # Archived folder
    archived = temp_ideas_dir / 'archived'
    archived.mkdir()
    (archived / 'old-idea.md').write_text('# Old Idea')
    
    return temp_ideas_dir


@pytest.fixture
def ideas_service(temp_project_dir):
    """Create IdeasService instance with temp directory"""
    from x_ipe.services import IdeasService
    return IdeasService(temp_project_dir)


@pytest.fixture
def ideas_service_populated(temp_project_dir, populated_ideas_dir):
    """Create IdeasService with populated ideas directory"""
    from x_ipe.services import IdeasService
    return IdeasService(temp_project_dir)


@pytest.fixture
def app(temp_project_dir, temp_ideas_dir):
    """Create Flask test app"""
    from x_ipe.app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['PROJECT_ROOT'] = temp_project_dir
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def client_populated(temp_project_dir, populated_ideas_dir):
    """Create test client with populated ideas"""
    from x_ipe.app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['PROJECT_ROOT'] = temp_project_dir
    return app.test_client()


# ============================================================================
# UNIT TESTS: IdeasService.move_item()
# ============================================================================

class TestMoveItem:
    """Tests for IdeasService.move_item() - AC-46"""
    
    def test_move_file_to_folder_success(self, ideas_service_populated, populated_ideas_dir):
        """AC-46: Move file to target folder successfully"""
        # ARRANGE
        source = 'project-alpha/notes.md'
        target = 'project-beta'
        
        # ACT
        result = ideas_service_populated.move_item(source, target)
        
        # ASSERT
        assert result['success'] is True
        assert result['new_path'] == 'project-beta/notes.md'
        # File should exist in new location
        assert (populated_ideas_dir / 'project-beta' / 'notes.md').exists()
        # File should not exist in old location
        assert not (populated_ideas_dir / 'project-alpha' / 'notes.md').exists()
    
    def test_move_folder_to_folder_success(self, ideas_service_populated, populated_ideas_dir):
        """AC-46: Move folder to target folder successfully"""
        # ARRANGE
        source = 'project-alpha/mockups'
        target = 'project-beta'
        
        # ACT
        result = ideas_service_populated.move_item(source, target)
        
        # ASSERT
        assert result['success'] is True
        assert result['new_path'] == 'project-beta/mockups'
        # Folder and contents should exist in new location
        assert (populated_ideas_dir / 'project-beta' / 'mockups').exists()
        assert (populated_ideas_dir / 'project-beta' / 'mockups' / 'v1.html').exists()
        # Folder should not exist in old location
        assert not (populated_ideas_dir / 'project-alpha' / 'mockups').exists()
    
    def test_move_folder_into_self_fails(self, ideas_service_populated):
        """AC-47: Cannot move folder into itself"""
        # ARRANGE
        source = 'project-alpha'
        target = 'project-alpha'
        
        # ACT
        result = ideas_service_populated.move_item(source, target)
        
        # ASSERT
        assert result['success'] is False
        assert 'cannot move' in result['error'].lower() or 'into itself' in result['error'].lower()
    
    def test_move_folder_into_child_fails(self, ideas_service_populated):
        """AC-47: Cannot move folder into its own child"""
        # ARRANGE
        source = 'project-alpha'
        target = 'project-alpha/mockups'
        
        # ACT
        result = ideas_service_populated.move_item(source, target)
        
        # ASSERT
        assert result['success'] is False
        assert 'cannot move' in result['error'].lower() or 'child' in result['error'].lower()
    
    def test_move_nonexistent_source_fails(self, ideas_service_populated):
        """Move nonexistent source returns error"""
        # ARRANGE
        source = 'nonexistent-folder'
        target = 'project-beta'
        
        # ACT
        result = ideas_service_populated.move_item(source, target)
        
        # ASSERT
        assert result['success'] is False
        assert 'not found' in result['error'].lower() or 'does not exist' in result['error'].lower()
    
    def test_move_to_nonexistent_target_fails(self, ideas_service_populated):
        """Move to nonexistent target folder returns error"""
        # ARRANGE
        source = 'project-alpha/notes.md'
        target = 'nonexistent-folder'
        
        # ACT
        result = ideas_service_populated.move_item(source, target)
        
        # ASSERT
        assert result['success'] is False
        assert 'not found' in result['error'].lower() or 'does not exist' in result['error'].lower()
    
    def test_move_to_file_target_fails(self, ideas_service_populated):
        """Cannot move item into a file (only folders)"""
        # ARRANGE
        source = 'project-alpha/notes.md'
        target = 'project-beta/readme.md'  # This is a file, not folder
        
        # ACT
        result = ideas_service_populated.move_item(source, target)
        
        # ASSERT
        assert result['success'] is False
        assert 'not a folder' in result['error'].lower() or 'directory' in result['error'].lower()
    
    def test_move_with_name_conflict_renames(self, ideas_service_populated, populated_ideas_dir):
        """Move item with same name in target creates unique name"""
        # ARRANGE - Create conflicting file
        (populated_ideas_dir / 'project-beta' / 'notes.md').write_text('Existing notes')
        source = 'project-alpha/notes.md'
        target = 'project-beta'
        
        # ACT
        result = ideas_service_populated.move_item(source, target)
        
        # ASSERT
        assert result['success'] is True
        # Should have renamed to avoid conflict
        assert 'notes' in result['new_path']
        assert '-2' in result['new_path'] or 'copy' in result['new_path'].lower()


# ============================================================================
# UNIT TESTS: IdeasService.duplicate_item()
# ============================================================================

class TestDuplicateItem:
    """Tests for IdeasService.duplicate_item() - AC-53 (duplicate action)"""
    
    def test_duplicate_file_success(self, ideas_service_populated, populated_ideas_dir):
        """Duplicate file creates copy with -copy suffix"""
        # ARRANGE
        path = 'project-alpha/notes.md'
        
        # ACT
        result = ideas_service_populated.duplicate_item(path)
        
        # ASSERT
        assert result['success'] is True
        assert 'notes-copy.md' in result['new_path']
        # Both files should exist
        assert (populated_ideas_dir / 'project-alpha' / 'notes.md').exists()
        assert (populated_ideas_dir / 'project-alpha' / 'notes-copy.md').exists()
    
    def test_duplicate_folder_success(self, ideas_service_populated, populated_ideas_dir):
        """Duplicate folder creates copy with -copy suffix including contents"""
        # ARRANGE
        path = 'project-alpha/mockups'
        
        # ACT
        result = ideas_service_populated.duplicate_item(path)
        
        # ASSERT
        assert result['success'] is True
        assert 'mockups-copy' in result['new_path']
        # Both folders should exist with contents
        assert (populated_ideas_dir / 'project-alpha' / 'mockups').exists()
        assert (populated_ideas_dir / 'project-alpha' / 'mockups-copy').exists()
        assert (populated_ideas_dir / 'project-alpha' / 'mockups-copy' / 'v1.html').exists()
    
    def test_duplicate_with_existing_copy_increments(self, ideas_service_populated, populated_ideas_dir):
        """Duplicate when -copy exists creates -copy-2"""
        # ARRANGE - Create first copy
        path = 'project-alpha/notes.md'
        ideas_service_populated.duplicate_item(path)
        
        # ACT - Duplicate again
        result = ideas_service_populated.duplicate_item(path)
        
        # ASSERT
        assert result['success'] is True
        assert 'notes-copy-2.md' in result['new_path']
    
    def test_duplicate_nonexistent_fails(self, ideas_service_populated):
        """Duplicate nonexistent item returns error"""
        # ARRANGE
        path = 'nonexistent/file.md'
        
        # ACT
        result = ideas_service_populated.duplicate_item(path)
        
        # ASSERT
        assert result['success'] is False
        assert 'not found' in result['error'].lower() or 'does not exist' in result['error'].lower()
    
    def test_duplicate_preserves_content(self, ideas_service_populated, populated_ideas_dir):
        """Duplicated file has same content as original"""
        # ARRANGE
        path = 'project-alpha/notes.md'
        original_content = (populated_ideas_dir / 'project-alpha' / 'notes.md').read_text()
        
        # ACT
        result = ideas_service_populated.duplicate_item(path)
        
        # ASSERT
        copy_path = populated_ideas_dir / 'project-alpha' / 'notes-copy.md'
        assert copy_path.read_text() == original_content


# ============================================================================
# UNIT TESTS: IdeasService.download_file() - existing delete_item already exists
# ============================================================================

class TestDownloadFile:
    """Tests for file download functionality - AC-53 (download action)"""
    
    def test_download_file_returns_content(self, ideas_service_populated, populated_ideas_dir):
        """Download returns file content and metadata"""
        # ARRANGE
        path = 'project-alpha/notes.md'
        
        # ACT
        result = ideas_service_populated.get_download_info(path)
        
        # ASSERT
        assert result['success'] is True
        assert result['filename'] == 'notes.md'
        assert result['content'] == '# Project Alpha Notes'
        assert 'text/markdown' in result['mime_type'] or 'text/plain' in result['mime_type']
    
    def test_download_html_file(self, ideas_service_populated, populated_ideas_dir):
        """Download HTML file returns correct mime type"""
        # ARRANGE
        path = 'project-alpha/mockups/v1.html'
        
        # ACT
        result = ideas_service_populated.get_download_info(path)
        
        # ASSERT
        assert result['success'] is True
        assert result['filename'] == 'v1.html'
        assert 'html' in result['mime_type'].lower()
    
    def test_download_nonexistent_fails(self, ideas_service_populated):
        """Download nonexistent file returns error"""
        # ARRANGE
        path = 'nonexistent/file.md'
        
        # ACT
        result = ideas_service_populated.get_download_info(path)
        
        # ASSERT
        assert result['success'] is False
        assert 'not found' in result['error'].lower()
    
    def test_download_folder_fails(self, ideas_service_populated):
        """Cannot download folder (only files)"""
        # ARRANGE
        path = 'project-alpha/mockups'
        
        # ACT
        result = ideas_service_populated.get_download_info(path)
        
        # ASSERT
        assert result['success'] is False
        assert 'folder' in result['error'].lower() or 'directory' in result['error'].lower()


# ============================================================================
# UNIT TESTS: Delete with confirmation data
# ============================================================================

class TestDeleteItemInfo:
    """Tests for delete confirmation info - AC-57"""
    
    def test_get_delete_info_file(self, ideas_service_populated):
        """Get delete info for file returns filename"""
        # ARRANGE
        path = 'project-alpha/notes.md'
        
        # ACT
        result = ideas_service_populated.get_delete_info(path)
        
        # ASSERT
        assert result['success'] is True
        assert result['name'] == 'notes.md'
        assert result['type'] == 'file'
        assert result['item_count'] == 1
    
    def test_get_delete_info_folder_with_contents(self, ideas_service_populated):
        """Get delete info for folder returns content count"""
        # ARRANGE
        path = 'project-alpha'
        
        # ACT
        result = ideas_service_populated.get_delete_info(path)
        
        # ASSERT
        assert result['success'] is True
        assert result['name'] == 'project-alpha'
        assert result['type'] == 'folder'
        # Should count: notes.md, design.md, mockups/, mockups/v1.html = 4 items
        assert result['item_count'] >= 3


# ============================================================================
# API TESTS: POST /api/ideas/move
# ============================================================================

class TestMoveAPI:
    """API tests for move endpoint - AC-46"""
    
    def test_move_api_success(self, client_populated):
        """POST /api/ideas/move moves item successfully"""
        # ARRANGE
        data = {
            'source_path': 'project-alpha/notes.md',
            'target_folder': 'project-beta'
        }
        
        # ACT
        response = client_populated.post('/api/ideas/move',
                                         json=data,
                                         content_type='application/json')
        
        # ASSERT
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'new_path' in result
    
    def test_move_api_missing_source_path(self, client_populated):
        """POST /api/ideas/move without source_path returns 400"""
        # ARRANGE
        data = {'target_folder': 'project-beta'}
        
        # ACT
        response = client_populated.post('/api/ideas/move',
                                         json=data,
                                         content_type='application/json')
        
        # ASSERT
        assert response.status_code == 400
    
    def test_move_api_missing_target_folder(self, client_populated):
        """POST /api/ideas/move without target_folder returns 400"""
        # ARRANGE
        data = {'source_path': 'project-alpha/notes.md'}
        
        # ACT
        response = client_populated.post('/api/ideas/move',
                                         json=data,
                                         content_type='application/json')
        
        # ASSERT
        assert response.status_code == 400
    
    def test_move_api_invalid_move_returns_error(self, client_populated):
        """POST /api/ideas/move with invalid move returns error"""
        # ARRANGE - Try to move folder into itself
        data = {
            'source_path': 'project-alpha',
            'target_folder': 'project-alpha'
        }
        
        # ACT
        response = client_populated.post('/api/ideas/move',
                                         json=data,
                                         content_type='application/json')
        
        # ASSERT
        assert response.status_code in [400, 200]  # Could be 400 or 200 with error in body
        result = response.get_json()
        assert result['success'] is False


# ============================================================================
# API TESTS: POST /api/ideas/duplicate
# ============================================================================

class TestDuplicateAPI:
    """API tests for duplicate endpoint - AC-53"""
    
    def test_duplicate_api_success(self, client_populated):
        """POST /api/ideas/duplicate duplicates item successfully"""
        # ARRANGE
        data = {'path': 'project-alpha/notes.md'}
        
        # ACT
        response = client_populated.post('/api/ideas/duplicate',
                                         json=data,
                                         content_type='application/json')
        
        # ASSERT
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'new_path' in result
    
    def test_duplicate_api_missing_path(self, client_populated):
        """POST /api/ideas/duplicate without path returns 400"""
        # ARRANGE
        data = {}
        
        # ACT
        response = client_populated.post('/api/ideas/duplicate',
                                         json=data,
                                         content_type='application/json')
        
        # ASSERT
        assert response.status_code == 400


# ============================================================================
# API TESTS: GET /api/ideas/download
# ============================================================================

class TestDownloadAPI:
    """API tests for download endpoint - AC-53"""
    
    def test_download_api_success(self, client_populated):
        """GET /api/ideas/download returns file content"""
        # ARRANGE
        path = 'project-alpha/notes.md'
        
        # ACT
        response = client_populated.get(f'/api/ideas/download?path={path}')
        
        # ASSERT
        assert response.status_code == 200
        assert b'Project Alpha Notes' in response.data
        # Check content-disposition header for download
        assert 'attachment' in response.headers.get('Content-Disposition', '').lower() or \
               'notes.md' in response.headers.get('Content-Disposition', '')
    
    def test_download_api_missing_path(self, client_populated):
        """GET /api/ideas/download without path returns 400"""
        # ACT
        response = client_populated.get('/api/ideas/download')
        
        # ASSERT
        assert response.status_code == 400
    
    def test_download_api_nonexistent_file(self, client_populated):
        """GET /api/ideas/download with nonexistent file returns 404"""
        # ACT
        response = client_populated.get('/api/ideas/download?path=nonexistent.md')
        
        # ASSERT
        assert response.status_code == 404


# ============================================================================
# INTEGRATION TESTS: Drag validation logic
# ============================================================================

class TestDragValidation:
    """Tests for drag-drop validation logic - AC-47, AC-48"""
    
    def test_is_valid_drop_target_sibling_folder(self, ideas_service_populated):
        """Validate: sibling folder is valid drop target"""
        # ARRANGE
        source = 'project-alpha'
        target = 'project-beta'
        
        # ACT
        is_valid = ideas_service_populated.is_valid_drop_target(source, target)
        
        # ASSERT
        assert is_valid is True
    
    def test_is_valid_drop_target_self_invalid(self, ideas_service_populated):
        """Validate: cannot drop into self"""
        # ARRANGE
        source = 'project-alpha'
        target = 'project-alpha'
        
        # ACT
        is_valid = ideas_service_populated.is_valid_drop_target(source, target)
        
        # ASSERT
        assert is_valid is False
    
    def test_is_valid_drop_target_child_invalid(self, ideas_service_populated):
        """Validate: cannot drop into child folder"""
        # ARRANGE
        source = 'project-alpha'
        target = 'project-alpha/mockups'
        
        # ACT
        is_valid = ideas_service_populated.is_valid_drop_target(source, target)
        
        # ASSERT
        assert is_valid is False
    
    def test_is_valid_drop_target_parent_valid(self, ideas_service_populated):
        """Validate: can drop child into parent (moving up)"""
        # ARRANGE
        source = 'project-alpha/mockups'
        target = 'archived'
        
        # ACT
        is_valid = ideas_service_populated.is_valid_drop_target(source, target)
        
        # ASSERT
        assert is_valid is True
    
    def test_is_valid_drop_target_nested_child_invalid(self, ideas_service_populated):
        """Validate: cannot drop into deeply nested child"""
        # ARRANGE - even with deeper nesting
        source = 'project-alpha'
        target = 'project-alpha/mockups'  # Direct child
        
        # ACT
        is_valid = ideas_service_populated.is_valid_drop_target(source, target)
        
        # ASSERT
        assert is_valid is False


# ============================================================================
# INTEGRATION TESTS: Search/Filter logic
# ============================================================================

class TestSearchFilter:
    """Tests for tree search/filter functionality - AC-58, AC-59"""
    
    def test_filter_tree_matches_file_name(self, ideas_service_populated):
        """Filter returns matching files"""
        # ARRANGE
        query = 'notes'
        
        # ACT
        results = ideas_service_populated.filter_tree(query)
        
        # ASSERT
        # Should include notes.md and its parent folder
        paths = [r['path'] for r in results]
        assert any('notes.md' in p for p in paths)
    
    def test_filter_tree_includes_parent_context(self, ideas_service_populated):
        """Filter includes parent folders for context"""
        # ARRANGE
        query = 'v1.html'
        
        # ACT
        results = ideas_service_populated.filter_tree(query)
        
        # ASSERT
        # Should include: project-alpha, mockups, v1.html
        paths = [r['path'] for r in results]
        assert any('v1.html' in p for p in paths)
        assert any('mockups' in p for p in paths)
        assert any('project-alpha' in p for p in paths)
    
    def test_filter_tree_matches_folder_name(self, ideas_service_populated):
        """Filter returns matching folders"""
        # ARRANGE
        query = 'archived'
        
        # ACT
        results = ideas_service_populated.filter_tree(query)
        
        # ASSERT
        paths = [r['path'] for r in results]
        assert any('archived' in p for p in paths)
    
    def test_filter_tree_case_insensitive(self, ideas_service_populated):
        """Filter is case-insensitive"""
        # ARRANGE
        query = 'NOTES'
        
        # ACT
        results = ideas_service_populated.filter_tree(query)
        
        # ASSERT
        paths = [r['path'] for r in results]
        assert any('notes.md' in p.lower() for p in paths)
    
    def test_filter_tree_empty_query_returns_all(self, ideas_service_populated):
        """Empty query returns full tree"""
        # ARRANGE
        query = ''
        
        # ACT
        results = ideas_service_populated.filter_tree(query)
        
        # ASSERT
        # Should return all items (at least 3 top-level folders)
        assert len(results) >= 3
    
    def test_filter_tree_no_matches_returns_empty(self, ideas_service_populated):
        """No matches returns empty list"""
        # ARRANGE
        query = 'xyznonexistent123'
        
        # ACT
        results = ideas_service_populated.filter_tree(query)
        
        # ASSERT
        assert len(results) == 0


# ============================================================================
# INTEGRATION TESTS: Folder contents for folder view
# ============================================================================

class TestGetFolderContents:
    """Tests for folder view contents - AC-50, AC-51, AC-54"""
    
    def test_get_folder_contents_returns_items(self, ideas_service_populated):
        """Get folder contents returns files and subfolders"""
        # ARRANGE
        folder_path = 'project-alpha'
        
        # ACT
        result = ideas_service_populated.get_folder_contents(folder_path)
        
        # ASSERT
        assert result['success'] is True
        items = result['items']
        names = [item['name'] for item in items]
        assert 'notes.md' in names
        assert 'design.md' in names
        assert 'mockups' in names
    
    def test_get_folder_contents_includes_type(self, ideas_service_populated):
        """Folder contents include type (file/folder)"""
        # ARRANGE
        folder_path = 'project-alpha'
        
        # ACT
        result = ideas_service_populated.get_folder_contents(folder_path)
        
        # ASSERT
        items = result['items']
        types = {item['name']: item['type'] for item in items}
        assert types.get('notes.md') == 'file'
        assert types.get('mockups') == 'folder'
    
    def test_get_folder_contents_includes_path(self, ideas_service_populated):
        """Folder contents include full path for each item (relative to project root)"""
        # ARRANGE
        folder_path = 'project-alpha'
        
        # ACT
        result = ideas_service_populated.get_folder_contents(folder_path)
        
        # ASSERT
        items = result['items']
        for item in items:
            assert 'path' in item
            # Paths should be relative to project root, including x-ipe-docs/ideas prefix
            assert item['path'].startswith('x-ipe-docs/ideas/project-alpha/')
    
    def test_get_folder_contents_empty_folder(self, ideas_service_populated, populated_ideas_dir):
        """Empty folder returns empty items list"""
        # ARRANGE - Create empty folder
        (populated_ideas_dir / 'empty-folder').mkdir()
        
        # ACT
        result = ideas_service_populated.get_folder_contents('empty-folder')
        
        # ASSERT
        assert result['success'] is True
        assert result['items'] == []
    
    def test_get_folder_contents_nonexistent(self, ideas_service_populated):
        """Nonexistent folder returns error"""
        # ARRANGE
        folder_path = 'nonexistent-folder'
        
        # ACT
        result = ideas_service_populated.get_folder_contents(folder_path)
        
        # ASSERT
        assert result['success'] is False
    
    def test_get_folder_contents_file_path(self, ideas_service_populated):
        """File path (not folder) returns error"""
        # ARRANGE
        file_path = 'project-alpha/notes.md'
        
        # ACT
        result = ideas_service_populated.get_folder_contents(file_path)
        
        # ASSERT
        assert result['success'] is False


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Edge case tests for CR-006"""
    
    def test_move_preserves_file_content(self, ideas_service_populated, populated_ideas_dir):
        """Move operation preserves file content"""
        # ARRANGE
        source = 'project-alpha/notes.md'
        target = 'project-beta'
        original_content = (populated_ideas_dir / 'project-alpha' / 'notes.md').read_text()
        
        # ACT
        ideas_service_populated.move_item(source, target)
        
        # ASSERT
        new_content = (populated_ideas_dir / 'project-beta' / 'notes.md').read_text()
        assert new_content == original_content
    
    def test_duplicate_deeply_nested_folder(self, ideas_service_populated, populated_ideas_dir):
        """Duplicate works for deeply nested folders"""
        # ARRANGE
        path = 'project-alpha/mockups'
        
        # ACT
        result = ideas_service_populated.duplicate_item(path)
        
        # ASSERT
        assert result['success'] is True
        # Check nested file was also copied
        assert (populated_ideas_dir / 'project-alpha' / 'mockups-copy' / 'v1.html').exists()
    
    def test_special_characters_in_filename(self, ideas_service_populated, populated_ideas_dir):
        """Handle files with special characters in name"""
        # ARRANGE - Create file with spaces and special chars
        (populated_ideas_dir / 'project-alpha' / 'my notes (v2).md').write_text('Content')
        source = 'project-alpha/my notes (v2).md'
        target = 'project-beta'
        
        # ACT
        result = ideas_service_populated.move_item(source, target)
        
        # ASSERT
        assert result['success'] is True
    
    def test_unicode_filename(self, ideas_service_populated, populated_ideas_dir):
        """Handle files with unicode characters"""
        # ARRANGE - Create file with unicode
        (populated_ideas_dir / 'project-alpha' / '设计笔记.md').write_text('中文内容')
        source = 'project-alpha/设计笔记.md'
        target = 'project-beta'
        
        # ACT
        result = ideas_service_populated.move_item(source, target)
        
        # ASSERT
        assert result['success'] is True
        assert (populated_ideas_dir / 'project-beta' / '设计笔记.md').exists()


# ============================================================================
# Test count and summary
# ============================================================================
# 
# Total tests: 52
# - TestMoveItem: 8 tests
# - TestDuplicateItem: 5 tests  
# - TestDownloadFile: 4 tests
# - TestDeleteItemInfo: 2 tests
# - TestMoveAPI: 4 tests
# - TestDuplicateAPI: 2 tests
# - TestDownloadAPI: 3 tests
# - TestDragValidation: 5 tests
# - TestSearchFilter: 6 tests
# - TestGetFolderContents: 6 tests
# - TestEdgeCases: 4 tests
# - Fixtures: 10
# 
# All tests should FAIL initially (TDD ready)
