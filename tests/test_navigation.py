"""
Tests for FEATURE-001: Project Navigation

Tests cover:
- ProjectService: Directory scanning and structure building
- API endpoint: GET /api/project/structure
- FileWatcher: File system change detection
"""
import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path


class TestProjectService:
    """Unit tests for ProjectService class"""

    def test_get_structure_returns_five_sections(self, app, project_service):
        """AC-2: Five top-level menu sections exist (including Workplace and Themes)"""
        structure = project_service.get_structure()
        
        assert 'sections' in structure
        assert len(structure['sections']) == 5
        
        section_ids = [s['id'] for s in structure['sections']]
        assert 'workplace' in section_ids
        assert 'themes' in section_ids  # FEATURE-012 AC-4.1
        assert 'planning' in section_ids
        assert 'requirements' in section_ids
        assert 'code' in section_ids

    def test_get_structure_themes_section_maps_correctly(self, app, project_service, temp_project):
        """FEATURE-012 AC-4.2: Themes menu shows folder tree of x-ipe-docs/themes/"""
        # Create a theme folder
        themes_dir = temp_project / 'x-ipe-docs' / 'themes' / 'theme-default'
        themes_dir.mkdir(parents=True, exist_ok=True)
        (themes_dir / 'design-system.md').write_text('# Design System')
        
        structure = project_service.get_structure()
        
        themes_section = next(s for s in structure['sections'] if s['id'] == 'themes')
        assert themes_section['path'] == 'x-ipe-docs/themes'
        assert themes_section['label'] == 'Themes'
        assert themes_section['icon'] == 'bi-palette'

    def test_get_structure_planning_section_maps_correctly(self, app, project_service, temp_project):
        """AC-3: Project Plan section maps to x-ipe-docs/planning/ folder"""
        # Create a file in x-ipe-docs/planning
        planning_dir = temp_project / 'x-ipe-docs' / 'planning'
        planning_dir.mkdir(parents=True, exist_ok=True)
        (planning_dir / 'task-board.md').write_text('# Task Board')
        
        structure = project_service.get_structure()
        
        planning_section = next(s for s in structure['sections'] if s['id'] == 'planning')
        assert planning_section['path'] == 'x-ipe-docs/planning'
        assert planning_section['label'] == 'Project Plan'

    def test_get_structure_requirements_section_maps_correctly(self, app, project_service, temp_project):
        """AC-4: Requirements section maps to x-ipe-docs/requirements/ folder"""
        # Create a file in x-ipe-docs/requirements
        req_dir = temp_project / 'x-ipe-docs' / 'requirements'
        req_dir.mkdir(parents=True, exist_ok=True)
        (req_dir / 'requirement-summary.md').write_text('# Requirements')
        
        structure = project_service.get_structure()
        
        req_section = next(s for s in structure['sections'] if s['id'] == 'requirements')
        assert req_section['path'] == 'x-ipe-docs/requirements'
        assert req_section['label'] == 'Requirements'

    def test_get_structure_code_section_maps_correctly(self, app, project_service, temp_project):
        """AC-5: Code section maps to src/ folder"""
        # Create a file in src
        src_dir = temp_project / 'src'
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / 'main.py').write_text('# Main')
        
        structure = project_service.get_structure()
        
        code_section = next(s for s in structure['sections'] if s['id'] == 'code')
        assert code_section['path'] == 'src'
        assert code_section['label'] == 'Code'

    def test_get_structure_includes_nested_folders(self, app, project_service, temp_project):
        """AC-6: Folders can be expanded/collapsed - structure includes nested items"""
        # Create nested structure
        feature_dir = temp_project / 'x-ipe-docs' / 'requirements' / 'FEATURE-001'
        feature_dir.mkdir(parents=True, exist_ok=True)
        (feature_dir / 'specification.md').write_text('# Spec')
        
        structure = project_service.get_structure()
        
        req_section = next(s for s in structure['sections'] if s['id'] == 'requirements')
        # Should have FEATURE-001 folder
        folder_names = [c['name'] for c in req_section.get('children', []) if c['type'] == 'folder']
        assert 'FEATURE-001' in folder_names

    def test_get_structure_returns_file_paths(self, app, project_service, temp_project):
        """AC-7: File items include paths for content loading"""
        planning_dir = temp_project / 'x-ipe-docs' / 'planning'
        planning_dir.mkdir(parents=True, exist_ok=True)
        (planning_dir / 'features.md').write_text('# Features')
        
        structure = project_service.get_structure()
        
        planning_section = next(s for s in structure['sections'] if s['id'] == 'planning')
        file_item = next((c for c in planning_section.get('children', []) if c['name'] == 'features.md'), None)
        
        assert file_item is not None
        assert file_item['type'] == 'file'
        assert file_item['path'] == 'x-ipe-docs/planning/features.md'

    def test_get_structure_excludes_hidden_files(self, app, project_service, temp_project):
        """BR-2: Hidden files (starting with .) are excluded"""
        src_dir = temp_project / 'src'
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / '.hidden').write_text('hidden')
        (src_dir / 'visible.py').write_text('# visible')
        
        structure = project_service.get_structure()
        
        code_section = next(s for s in structure['sections'] if s['id'] == 'code')
        file_names = [c['name'] for c in code_section.get('children', [])]
        
        assert '.hidden' not in file_names
        assert 'visible.py' in file_names

    def test_get_structure_handles_empty_section(self, app, project_service, temp_project):
        """Edge Case 1: Empty directory shows section with no children"""
        # Create empty src folder
        (temp_project / 'src').mkdir(parents=True, exist_ok=True)
        
        structure = project_service.get_structure()
        
        code_section = next(s for s in structure['sections'] if s['id'] == 'code')
        assert code_section.get('children', []) == []

    def test_get_structure_handles_missing_folder(self, app, project_service, temp_project):
        """Edge Case 2: Missing folder shows section with empty state"""
        # Don't create src folder at all
        structure = project_service.get_structure()
        
        code_section = next(s for s in structure['sections'] if s['id'] == 'code')
        assert code_section.get('children', []) == []
        assert code_section.get('exists', True) is False


class TestProjectStructureAPI:
    """API tests for GET /api/project/structure"""

    def test_get_structure_returns_200(self, client):
        """API returns 200 OK"""
        response = client.get('/api/project/structure')
        assert response.status_code == 200

    def test_get_structure_returns_json(self, client):
        """API returns valid JSON"""
        response = client.get('/api/project/structure')
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert 'sections' in data

    def test_get_structure_sections_have_required_fields(self, client):
        """Each section has id, label, path, children"""
        response = client.get('/api/project/structure')
        data = json.loads(response.data)
        
        for section in data['sections']:
            assert 'id' in section
            assert 'label' in section
            assert 'path' in section
            assert 'children' in section

    def test_get_structure_files_have_required_fields(self, client, temp_project):
        """Each file node has name, type, path"""
        # Create a test file
        planning_dir = temp_project / 'x-ipe-docs' / 'planning'
        planning_dir.mkdir(parents=True, exist_ok=True)
        (planning_dir / 'test.md').write_text('# Test')
        
        response = client.get('/api/project/structure')
        data = json.loads(response.data)
        
        planning = next(s for s in data['sections'] if s['id'] == 'planning')
        if planning['children']:
            file_node = planning['children'][0]
            assert 'name' in file_node
            assert 'type' in file_node
            assert 'path' in file_node


class TestPathSecurity:
    """Security tests for path traversal prevention"""

    def test_paths_are_within_project_root(self, app, project_service, temp_project):
        """BR-3: Only allow access to files within project root"""
        structure = project_service.get_structure()
        
        def check_paths(items, project_root):
            for item in items:
                if 'path' in item:
                    # Path should not contain ..
                    assert '..' not in item['path']
                if 'children' in item:
                    check_paths(item['children'], project_root)
        
        check_paths(structure['sections'], str(temp_project))


class TestFileWatcherGitignore:
    """Tests for FileWatcher ignoring .gitignore patterns"""

    def test_filewatcher_ignores_venv_directory(self, temp_project):
        """BUG FIX: FileWatcher should not monitor .venv/ folder"""
        from x_ipe.services import FileWatcher
        import time
        
        # Create .gitignore with .venv
        (temp_project / '.gitignore').write_text('.venv/\n__pycache__/\n')
        
        # Create .venv folder
        venv_dir = temp_project / '.venv'
        venv_dir.mkdir()
        
        events = []
        
        class MockSocketIO:
            def emit(self, event, data):
                events.append((event, data))
        
        watcher = FileWatcher(str(temp_project), MockSocketIO())
        watcher.start()
        
        try:
            time.sleep(0.2)
            
            # Create a file in .venv - should NOT trigger event
            (venv_dir / 'test.txt').write_text('test')
            time.sleep(0.3)
            
            # No events should be emitted for .venv files
            venv_events = [e for e in events if '.venv' in str(e[1].get('path', ''))]
            assert len(venv_events) == 0, f"Should not emit events for .venv files, got: {venv_events}"
        finally:
            watcher.stop()

    def test_filewatcher_ignores_pycache_directory(self, temp_project):
        """BUG FIX: FileWatcher should not monitor __pycache__/ folder"""
        from x_ipe.services import FileWatcher
        import time
        
        # Create .gitignore
        (temp_project / '.gitignore').write_text('__pycache__/\n')
        
        # Create __pycache__ folder
        pycache_dir = temp_project / '__pycache__'
        pycache_dir.mkdir()
        
        events = []
        
        class MockSocketIO:
            def emit(self, event, data):
                events.append((event, data))
        
        watcher = FileWatcher(str(temp_project), MockSocketIO())
        watcher.start()
        
        try:
            time.sleep(0.2)
            
            # Create a file in __pycache__ - should NOT trigger event
            (pycache_dir / 'test.pyc').write_text('test')
            time.sleep(0.3)
            
            # No events should be emitted for __pycache__ files
            pycache_events = [e for e in events if '__pycache__' in str(e[1].get('path', ''))]
            assert len(pycache_events) == 0, f"Should not emit events for __pycache__ files, got: {pycache_events}"
        finally:
            watcher.stop()

    def test_filewatcher_still_monitors_normal_files(self, temp_project):
        """FileWatcher should still monitor non-ignored files"""
        from x_ipe.services import FileWatcher
        import time
        
        # Create .gitignore
        (temp_project / '.gitignore').write_text('.venv/\n')
        
        # Create src folder (not ignored)
        src_dir = temp_project / 'src'
        src_dir.mkdir()
        
        events = []
        
        class MockSocketIO:
            def emit(self, event, data):
                events.append((event, data))
        
        watcher = FileWatcher(str(temp_project), MockSocketIO())
        watcher.start()
        
        try:
            time.sleep(0.2)
            
            # Create a file in src - SHOULD trigger event
            (src_dir / 'test.py').write_text('test')
            time.sleep(0.3)
            
            # Should have at least one event for src/test.py
            src_events = [e for e in events if 'test.py' in str(e[1].get('path', ''))]
            assert len(src_events) > 0, f"Should emit events for src files, events: {events}"
        finally:
            watcher.stop()


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


@pytest.fixture
def project_service(app, temp_project):
    """Create ProjectService instance"""
    from x_ipe.services import ProjectService
    return ProjectService(str(temp_project))
