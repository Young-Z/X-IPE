"""
Tests for FEATURE-009: File Change Indicator

This feature is frontend-only (JavaScript). These tests verify the API behavior
that the frontend relies on, and document manual testing procedures.

Tests cover:
- API: GET /api/project/structure returns paths for comparison
- Manual: Frontend change indicator behavior

Note: Full JavaScript unit tests would require a JS testing framework (Jest).
Integration tests would use Playwright.
"""
import pytest
import time
from pathlib import Path


class TestProjectStructureAPI:
    """API tests that the change indicator relies on"""

    def test_structure_endpoint_returns_file_paths(self, client, temp_project):
        """FR-1: Structure API returns file paths for change detection"""
        # Create test files
        planning_dir = temp_project / 'x-ipe-docs' / 'planning'
        planning_dir.mkdir(parents=True, exist_ok=True)
        (planning_dir / 'test.md').write_text('# Test')
        
        response = client.get('/api/project/structure')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'sections' in data
        
        # Verify structure includes paths
        planning_section = next(
            (s for s in data['sections'] if s['id'] == 'planning'),
            None
        )
        assert planning_section is not None
        assert 'children' in planning_section
        
    def test_structure_endpoint_returns_consistent_format(self, client, temp_project):
        """Ensure structure format is consistent for hashing"""
        # Create files
        planning_dir = temp_project / 'x-ipe-docs' / 'planning'
        planning_dir.mkdir(parents=True, exist_ok=True)
        (planning_dir / 'file1.md').write_text('# File 1')
        
        response1 = client.get('/api/project/structure')
        response2 = client.get('/api/project/structure')
        
        # Same structure should return same data
        assert response1.get_json() == response2.get_json()
        
    def test_structure_changes_when_file_added(self, client, temp_project):
        """Structure hash changes when new file is added"""
        planning_dir = temp_project / 'x-ipe-docs' / 'planning'
        planning_dir.mkdir(parents=True, exist_ok=True)
        (planning_dir / 'existing.md').write_text('# Existing')
        
        response1 = client.get('/api/project/structure')
        data1 = response1.get_json()
        
        # Add new file
        (planning_dir / 'new_file.md').write_text('# New File')
        
        response2 = client.get('/api/project/structure')
        data2 = response2.get_json()
        
        # Structure should be different
        assert data1 != data2
        
    def test_structure_changes_when_file_deleted(self, client, temp_project):
        """Structure hash changes when file is deleted"""
        planning_dir = temp_project / 'x-ipe-docs' / 'planning'
        planning_dir.mkdir(parents=True, exist_ok=True)
        file_to_delete = planning_dir / 'to_delete.md'
        file_to_delete.write_text('# To Delete')
        (planning_dir / 'keeper.md').write_text('# Keeper')
        
        response1 = client.get('/api/project/structure')
        data1 = response1.get_json()
        
        # Delete file
        file_to_delete.unlink()
        
        response2 = client.get('/api/project/structure')
        data2 = response2.get_json()
        
        # Structure should be different
        assert data1 != data2

    def test_structure_includes_mtime_for_files(self, client, temp_project):
        """BUG FIX: Structure API returns mtime for content change detection"""
        planning_dir = temp_project / 'x-ipe-docs' / 'planning'
        planning_dir.mkdir(parents=True, exist_ok=True)
        test_file = planning_dir / 'test.md'
        test_file.write_text('# Test')
        
        response = client.get('/api/project/structure')
        data = response.get_json()
        
        # Find the file in the response
        planning_section = next(
            (s for s in data['sections'] if s['id'] == 'planning'),
            None
        )
        assert planning_section is not None
        
        # Find test.md in children
        test_file_node = None
        for child in planning_section.get('children', []):
            if child.get('name') == 'test.md':
                test_file_node = child
                break
        
        assert test_file_node is not None
        # mtime should be included for content change detection
        assert 'mtime' in test_file_node
        assert isinstance(test_file_node['mtime'], (int, float))

    def test_structure_mtime_changes_when_content_modified(self, client, temp_project):
        """BUG FIX: mtime changes when file content is modified"""
        import time
        
        planning_dir = temp_project / 'x-ipe-docs' / 'planning'
        planning_dir.mkdir(parents=True, exist_ok=True)
        test_file = planning_dir / 'test.md'
        test_file.write_text('# Initial')
        
        response1 = client.get('/api/project/structure')
        data1 = response1.get_json()
        
        # Wait briefly to ensure mtime differs
        time.sleep(0.1)
        
        # Modify file content
        test_file.write_text('# Modified content')
        
        response2 = client.get('/api/project/structure')
        data2 = response2.get_json()
        
        # Find test.md mtime in both responses
        def get_file_mtime(data, filename):
            for section in data['sections']:
                for child in section.get('children', []):
                    if child.get('name') == filename:
                        return child.get('mtime')
            return None
        
        mtime1 = get_file_mtime(data1, 'test.md')
        mtime2 = get_file_mtime(data2, 'test.md')
        
        assert mtime1 is not None
        assert mtime2 is not None
        assert mtime2 > mtime1  # mtime should increase after modification


class TestPathUtilityLogic:
    """Test utility functions that would be used in frontend
    
    These tests document the expected behavior for JavaScript implementation.
    """

    def test_extract_parent_paths(self):
        """FR-3: Extract parent paths for bubble-up"""
        def get_parent_paths(path):
            """Python equivalent of JS _getParentPaths()"""
            parts = path.split('/')
            parents = []
            for i in range(len(parts) - 1, 0, -1):
                parents.append('/'.join(parts[:i]))
            return parents
        
        # Test cases
        assert get_parent_paths('x-ipe-docs/planning/features.md') == ['x-ipe-docs/planning', 'x-ipe-docs']
        assert get_parent_paths('src/app.py') == ['src']
        assert get_parent_paths('README.md') == []
        
    def test_has_changed_children(self):
        """FR-3: Check if folder has changed children"""
        def has_changed_children(folder_path, changed_paths):
            """Python equivalent of JS _hasChangedChildren()"""
            prefix = folder_path + '/'
            return any(p.startswith(prefix) for p in changed_paths)
        
        changed = {'x-ipe-docs/planning/features.md', 'x-ipe-docs/planning', 'x-ipe-docs'}
        
        assert has_changed_children('x-ipe-docs', changed) == True
        assert has_changed_children('x-ipe-docs/planning', changed) == True
        assert has_changed_children('src', changed) == False
        
    def test_detect_new_paths(self):
        """FR-1: Detect newly added paths"""
        old_paths = {'x-ipe-docs/planning/task-board.md', 'x-ipe-docs/planning'}
        new_paths = {'x-ipe-docs/planning/task-board.md', 'x-ipe-docs/planning/features.md', 'x-ipe-docs/planning'}
        
        added = new_paths - old_paths
        
        assert added == {'x-ipe-docs/planning/features.md'}
        
    def test_detect_removed_paths(self):
        """FR-1: Detect removed paths"""
        old_paths = {'x-ipe-docs/planning/task-board.md', 'x-ipe-docs/planning/old.md', 'x-ipe-docs/planning'}
        new_paths = {'x-ipe-docs/planning/task-board.md', 'x-ipe-docs/planning'}
        
        removed = old_paths - new_paths
        
        assert removed == {'x-ipe-docs/planning/old.md'}


class TestChangeIndicatorIntegration:
    """Integration test scenarios for manual/Playwright testing
    
    These tests document expected behavior but require browser testing.
    """

    def test_scenario_file_created_shows_dot(self):
        """
        MANUAL TEST - AC-1, AC-2, AC-3:
        
        Steps:
        1. Open app in browser
        2. In terminal, create file: touch x-ipe-docs/planning/new-file.md
        3. Wait 5 seconds for poll
        
        Expected:
        - Yellow dot appears on new-file.md
        - Yellow dot appears on planning/ folder
        - Yellow dot appears on x-ipe-docs/ folder (if visible)
        """
        pass  # Manual test marker
        
    def test_scenario_click_clears_dot(self):
        """
        MANUAL TEST - AC-4:
        
        Steps:
        1. Complete test_scenario_file_created_shows_dot
        2. Click on the new-file.md in sidebar
        
        Expected:
        - Yellow dot disappears from new-file.md
        """
        pass  # Manual test marker
        
    def test_scenario_parent_clears_when_empty(self):
        """
        MANUAL TEST - AC-5:
        
        Steps:
        1. Create two files in same folder
        2. Wait for dots to appear on both
        3. Click first file - its dot disappears
        4. Click second file - its dot AND parent folder dot disappears
        
        Expected:
        - Parent folder dot clears only when all children cleared
        """
        pass  # Manual test marker
        
    def test_scenario_page_refresh_clears_all(self):
        """
        MANUAL TEST - AC-7:
        
        Steps:
        1. Create file, wait for dot
        2. Refresh page (F5)
        
        Expected:
        - All dots are cleared
        - No dots visible after refresh
        """
        pass  # Manual test marker


# Fixtures for API tests
@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create base directories
    (project_dir / 'x-ipe-docs' / 'planning').mkdir(parents=True)
    (project_dir / 'x-ipe-docs' / 'requirements').mkdir(parents=True)
    (project_dir / 'x-ipe-docs' / 'ideas').mkdir(parents=True)
    (project_dir / 'src').mkdir(parents=True)
    
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
    """Test client fixture"""
    return app.test_client()
