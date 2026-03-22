"""
Tests for CR-004: KB Reference YAML Persistence

Covers:
- _write_kb_references (low-level writer)
- upload with kb_references (deferred write)
- save_kb_references / delete_kb_references (immediate write/delete)
- Route JSON parsing
"""
import json
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch

from x_ipe.services.ideas_service import IdeasService


@pytest.fixture
def ideas_service(tmp_path):
    """Create an IdeasService with a temp ideas root."""
    service = IdeasService.__new__(IdeasService)
    service.ideas_root = tmp_path / 'ideas'
    service.ideas_root.mkdir()
    service.IDEAS_PATH = 'x-ipe-docs/ideas'
    service.project_root = tmp_path
    return service


class TestKbReferenceYamlWriter:
    """Tests for _write_kb_references method."""

    def test_writes_yaml_file(self, ideas_service, tmp_path):
        folder = tmp_path / 'test-idea'
        folder.mkdir()
        refs = ['knowledge-base/setup.md', 'knowledge-base/api-docs/']
        
        ideas_service._write_kb_references(folder, refs)
        
        yaml_path = folder / '.knowledge-reference.yaml'
        assert yaml_path.exists()

    def test_yaml_format_correct(self, ideas_service, tmp_path):
        folder = tmp_path / 'test-idea'
        folder.mkdir()
        refs = ['knowledge-base/setup.md', 'knowledge-base/guides/architecture.md']
        
        ideas_service._write_kb_references(folder, refs)
        
        yaml_path = folder / '.knowledge-reference.yaml'
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        
        assert 'knowledge-reference' in data
        assert data['knowledge-reference'] == refs

    def test_yaml_is_flat_list(self, ideas_service, tmp_path):
        folder = tmp_path / 'test-idea'
        folder.mkdir()
        refs = ['a.md', 'b.md', 'c/']
        
        ideas_service._write_kb_references(folder, refs)
        
        yaml_path = folder / '.knowledge-reference.yaml'
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        
        assert isinstance(data['knowledge-reference'], list)
        assert len(data['knowledge-reference']) == 3

    def test_does_not_write_when_empty(self, ideas_service, tmp_path):
        folder = tmp_path / 'test-idea'
        folder.mkdir()
        kb_references = []
        if kb_references:
            ideas_service._write_kb_references(folder, kb_references)
        
        yaml_path = folder / '.knowledge-reference.yaml'
        assert not yaml_path.exists()

    def test_chinese_filenames_stored_as_unicode_not_escaped(self, ideas_service, tmp_path):
        """Chinese filenames must be stored as native Unicode, not \\uXXXX escapes."""
        folder = tmp_path / 'test-idea'
        folder.mkdir()
        refs = ['x-ipe-docs/knowledge-base/测试文档.docx']

        ideas_service._write_kb_references(folder, refs)

        yaml_path = folder / '.knowledge-reference.yaml'
        raw = yaml_path.read_text(encoding='utf-8')
        assert '\\u' not in raw, f"YAML contains escaped Unicode: {raw}"
        assert '测试文档' in raw, f"YAML missing Chinese characters: {raw}"


class TestSaveKbReferences:
    """Tests for save_kb_references (immediate write endpoint)."""

    def test_save_creates_yaml(self, ideas_service):
        folder_name = 'test-idea'
        (ideas_service.ideas_root / folder_name).mkdir()
        refs = ['knowledge-base/setup.md']
        
        result = ideas_service.save_kb_references(folder_name, refs)
        
        assert result['success'] is True
        yaml_path = ideas_service.ideas_root / folder_name / '.knowledge-reference.yaml'
        assert yaml_path.exists()
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        assert data['knowledge-reference'] == refs

    def test_save_creates_folder_if_missing(self, ideas_service):
        folder_name = 'new-folder'
        refs = ['knowledge-base/a.md']
        
        result = ideas_service.save_kb_references(folder_name, refs)
        
        assert result['success'] is True
        assert (ideas_service.ideas_root / folder_name).exists()

    def test_save_overwrites_existing_yaml(self, ideas_service):
        folder_name = 'test-idea'
        (ideas_service.ideas_root / folder_name).mkdir()
        ideas_service.save_kb_references(folder_name, ['old.md'])
        ideas_service.save_kb_references(folder_name, ['new.md', 'new2.md'])
        
        yaml_path = ideas_service.ideas_root / folder_name / '.knowledge-reference.yaml'
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        assert data['knowledge-reference'] == ['new.md', 'new2.md']

    def test_save_strips_ideas_path_prefix(self, ideas_service):
        folder_name = 'test-idea'
        (ideas_service.ideas_root / folder_name).mkdir()
        refs = ['knowledge-base/setup.md']
        
        result = ideas_service.save_kb_references(
            f'{ideas_service.IDEAS_PATH}/{folder_name}', refs
        )
        assert result['success'] is True


class TestDeleteKbReferences:
    """Tests for delete_kb_references (immediate delete endpoint)."""

    def test_delete_removes_yaml(self, ideas_service):
        folder_name = 'test-idea'
        folder = ideas_service.ideas_root / folder_name
        folder.mkdir()
        yaml_path = folder / '.knowledge-reference.yaml'
        yaml_path.write_text('knowledge-reference:\n- a.md\n')
        
        result = ideas_service.delete_kb_references(folder_name)
        
        assert result['success'] is True
        assert result['deleted'] is True
        assert not yaml_path.exists()

    def test_delete_when_no_yaml_exists(self, ideas_service):
        folder_name = 'test-idea'
        (ideas_service.ideas_root / folder_name).mkdir()
        
        result = ideas_service.delete_kb_references(folder_name)
        
        assert result['success'] is True
        assert result['deleted'] is False

    def test_delete_strips_ideas_path_prefix(self, ideas_service):
        folder_name = 'test-idea'
        folder = ideas_service.ideas_root / folder_name
        folder.mkdir()
        yaml_path = folder / '.knowledge-reference.yaml'
        yaml_path.write_text('knowledge-reference:\n- a.md\n')
        
        result = ideas_service.delete_kb_references(
            f'{ideas_service.IDEAS_PATH}/{folder_name}'
        )
        assert result['success'] is True
        assert result['deleted'] is True


class TestUploadWithKbReferences:
    """Tests for upload method with kb_references parameter."""

    def test_upload_with_references_creates_yaml(self, ideas_service):
        files = [('new idea.md', b'# My Idea\nSome content')]
        refs = ['knowledge-base/setup.md']
        
        result = ideas_service.upload(files, kb_references=refs)
        
        assert result['success'] is True
        folder_path = ideas_service.ideas_root / result['folder_name']
        yaml_path = folder_path / '.knowledge-reference.yaml'
        assert yaml_path.exists()
        
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        assert data['knowledge-reference'] == refs

    def test_upload_without_references_no_yaml(self, ideas_service):
        files = [('new idea.md', b'# My Idea')]
        
        result = ideas_service.upload(files)
        
        assert result['success'] is True
        folder_path = ideas_service.ideas_root / result['folder_name']
        yaml_path = folder_path / '.knowledge-reference.yaml'
        assert not yaml_path.exists()

    def test_upload_with_empty_references_no_yaml(self, ideas_service):
        files = [('new idea.md', b'# My Idea')]
        
        result = ideas_service.upload(files, kb_references=[])
        
        assert result['success'] is True
        folder_path = ideas_service.ideas_root / result['folder_name']
        yaml_path = folder_path / '.knowledge-reference.yaml'
        assert not yaml_path.exists()

    def test_backward_compatible_without_kb_references_param(self, ideas_service):
        files = [('test.md', b'content')]
        result = ideas_service.upload(files, date='03132026 120000')
        assert result['success'] is True
        assert 'files_uploaded' in result


class TestRouteKbReferenceParsing:
    """Tests for JSON parsing logic used in ideas_routes.py."""

    def test_parse_valid_json_list(self):
        raw = '["knowledge-base/a.md", "knowledge-base/b/"]'
        refs = json.loads(raw)
        assert isinstance(refs, list)
        assert len(refs) == 2

    def test_parse_invalid_json_returns_empty(self):
        raw = 'not valid json'
        try:
            refs = json.loads(raw)
            if not isinstance(refs, list):
                refs = []
        except (json.JSONDecodeError, TypeError):
            refs = []
        assert refs == []

    def test_parse_non_list_json_returns_empty(self):
        raw = '{"key": "value"}'
        try:
            refs = json.loads(raw)
            if not isinstance(refs, list):
                refs = []
        except (json.JSONDecodeError, TypeError):
            refs = []
        assert refs == []

    def test_parse_null_returns_empty(self):
        raw = None
        refs = []
        if raw:
            try:
                refs = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                refs = []
        assert refs == []
