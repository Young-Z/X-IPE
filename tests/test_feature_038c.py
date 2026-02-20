"""
TDD Tests for FEATURE-038-C: Enhanced Deliverable Viewer (Backend)
Tests: GET /api/workflow/{name}/deliverables/tree endpoint
"""
import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock


class TestDeliverableTreeEndpoint:
    """Test the folder contents API endpoint for deliverable viewer."""

    def test_tree_returns_folder_contents(self, client, tmp_path):
        """Endpoint returns list of files and dirs in a deliverable folder."""
        # Create test folder structure
        folder = tmp_path / "ideas" / "test-idea" / "refined-idea"
        folder.mkdir(parents=True)
        (folder / "idea-summary.md").write_text("# Summary")
        (folder / "notes.txt").write_text("notes")
        sub = folder / "mockups"
        sub.mkdir()
        (sub / "mockup.html").write_text("<html>")

        with patch('x_ipe.routes.workflow_routes.get_project_root', return_value=str(tmp_path)):
            resp = client.get(f'/api/workflow/test/deliverables/tree?path=ideas/test-idea/refined-idea/')
        
        assert resp.status_code == 200
        data = resp.get_json()
        names = [e['name'] for e in data]
        assert 'idea-summary.md' in names
        assert 'notes.txt' in names
        assert 'mockups' in names

    def test_tree_returns_type_for_each_entry(self, client, tmp_path):
        """Each entry has 'type' field: 'file' or 'dir'."""
        folder = tmp_path / "ideas" / "test"
        folder.mkdir(parents=True)
        (folder / "readme.md").write_text("# Test")
        (folder / "sub").mkdir()

        with patch('x_ipe.routes.workflow_routes.get_project_root', return_value=str(tmp_path)):
            resp = client.get(f'/api/workflow/test/deliverables/tree?path=ideas/test/')

        data = resp.get_json()
        types_map = {e['name']: e['type'] for e in data}
        assert types_map['readme.md'] == 'file'
        assert types_map['sub'] == 'dir'

    def test_tree_returns_full_path(self, client, tmp_path):
        """Each entry has a 'path' field with full relative path."""
        folder = tmp_path / "ideas" / "test"
        folder.mkdir(parents=True)
        (folder / "file.md").write_text("content")

        with patch('x_ipe.routes.workflow_routes.get_project_root', return_value=str(tmp_path)):
            resp = client.get(f'/api/workflow/test/deliverables/tree?path=ideas/test/')

        data = resp.get_json()
        paths = [e['path'] for e in data]
        assert any('ideas/test/file.md' in p for p in paths)

    def test_tree_rejects_path_traversal(self, client, tmp_path):
        """Path traversal attempts (../) are rejected with 403."""
        with patch('x_ipe.routes.workflow_routes.get_project_root', return_value=str(tmp_path)):
            resp = client.get('/api/workflow/test/deliverables/tree?path=../../etc/')

        assert resp.status_code == 403

    def test_tree_returns_404_for_missing_folder(self, client, tmp_path):
        """Nonexistent folder returns 404."""
        with patch('x_ipe.routes.workflow_routes.get_project_root', return_value=str(tmp_path)):
            resp = client.get('/api/workflow/test/deliverables/tree?path=nonexistent/')

        assert resp.status_code == 404

    def test_tree_requires_path_parameter(self, client):
        """Missing path parameter returns 400."""
        resp = client.get('/api/workflow/test/deliverables/tree')
        assert resp.status_code == 400

    def test_tree_limits_to_50_entries(self, client, tmp_path):
        """Folders with >50 entries return max 50."""
        folder = tmp_path / "ideas" / "big"
        folder.mkdir(parents=True)
        for i in range(60):
            (folder / f"file-{i:03d}.txt").write_text(f"content {i}")

        with patch('x_ipe.routes.workflow_routes.get_project_root', return_value=str(tmp_path)):
            resp = client.get(f'/api/workflow/test/deliverables/tree?path=ideas/big/')

        data = resp.get_json()
        assert len(data) <= 50

    def test_tree_empty_folder(self, client, tmp_path):
        """Empty folder returns empty list."""
        folder = tmp_path / "ideas" / "empty"
        folder.mkdir(parents=True)

        with patch('x_ipe.routes.workflow_routes.get_project_root', return_value=str(tmp_path)):
            resp = client.get(f'/api/workflow/test/deliverables/tree?path=ideas/empty/')

        assert resp.status_code == 200
        assert resp.get_json() == []


@pytest.fixture
def client(tmp_path):
    """Create Flask test client."""
    from src.x_ipe.app import create_app
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
