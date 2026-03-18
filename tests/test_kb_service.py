"""
FEATURE-049-A: KB Backend & Storage Foundation — Tests

Tests for KBService (unit) and KB API routes (integration).
Covers all 11 acceptance criteria.
"""
import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_project():
    """Create a temporary project directory with KB root."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def kb_service(temp_project):
    """Create a KBService instance pointing at the temp project."""
    from x_ipe.services.kb_service import KBService
    svc = KBService(temp_project)
    svc.ensure_kb_root()
    return svc


@pytest.fixture
def app(temp_project):
    """Create Flask test app with KB service."""
    from x_ipe.app import create_app
    test_app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': temp_project,
        'SETTINGS_DB_PATH': os.path.join(temp_project, 'test_settings.db'),
    })
    return test_app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _create_md_file(kb_root: Path, rel_path: str, body: str = 'Hello',
                    frontmatter: dict = None) -> Path:
    """Write a markdown file with optional frontmatter."""
    target = kb_root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if frontmatter:
        fm_str = yaml.safe_dump(frontmatter, default_flow_style=False).rstrip('\n')
        content = f"---\n{fm_str}\n---\n{body}"
    else:
        content = body
    target.write_text(content, encoding='utf-8')
    return target


# ===========================================================================
# AC-049-A-01: KB Root Initialization
# ===========================================================================

class TestKBRootInitialization:
    """AC-01: Auto-create KB root + knowledgebase-config.json with default tags."""

    def test_ensure_kb_root_creates_directory(self, temp_project):
        from x_ipe.services.kb_service import KBService
        svc = KBService(temp_project)
        svc.ensure_kb_root()
        assert svc.kb_root.is_dir()

    def test_ensure_kb_root_creates_config(self, kb_service):
        config_path = kb_service.config_path
        assert config_path.exists()
        config = json.loads(config_path.read_text())
        assert 'tags' in config
        assert 'lifecycle' in config['tags']
        assert 'domain' in config['tags']

    def test_default_lifecycle_tags(self, kb_service):
        config = json.loads((kb_service.config_path).read_text())
        expected = ['Ideation', 'Requirement', 'Design', 'Implementation',
                    'Testing', 'Deployment', 'Maintenance']
        assert config['tags']['lifecycle'] == expected

    def test_default_domain_tags(self, kb_service):
        config = json.loads((kb_service.config_path).read_text())
        expected = ['API', 'Authentication', 'UI-UX', 'Database',
                    'Infrastructure', 'Security', 'Performance',
                    'Integration', 'Documentation', 'Analytics']
        assert config['tags']['domain'] == expected

    def test_default_agent_write_allowlist(self, kb_service):
        config = json.loads((kb_service.config_path).read_text())
        assert config['agent_write_allowlist'] == []

    def test_default_ai_librarian_settings(self, kb_service):
        config = json.loads((kb_service.config_path).read_text())
        assert config['ai_librarian'] == {'enabled': False, 'intake_folder': '.intake', 'skill': 'x-ipe-tool-kb-librarian'}

    def test_ensure_kb_root_idempotent(self, kb_service):
        """Calling ensure_kb_root again doesn't overwrite existing config."""
        config_path = kb_service.config_path
        original = config_path.read_text()
        kb_service.ensure_kb_root()
        assert config_path.read_text() == original


# ===========================================================================
# AC-049-A-02: Folder Listing API (Tree)
# ===========================================================================

class TestTreeAPI:
    """AC-02: GET /api/kb/tree returns nested tree, excludes .intake."""

    def test_get_tree_empty_kb(self, kb_service):
        tree = kb_service.get_tree()
        assert tree == []

    def test_get_tree_with_files(self, kb_service):
        _create_md_file(kb_service.kb_root, 'guide.md',
                        frontmatter={'title': 'Guide'})
        kb_service._invalidate_cache()
        tree = kb_service.get_tree()
        assert len(tree) == 1
        assert tree[0].name == 'guide.md'
        assert tree[0].type == 'file'

    def test_get_tree_with_folders(self, kb_service):
        (kb_service.kb_root / 'docs').mkdir()
        _create_md_file(kb_service.kb_root, 'docs/readme.md')
        kb_service._invalidate_cache()
        tree = kb_service.get_tree()
        assert len(tree) == 1
        assert tree[0].name == 'docs'
        assert tree[0].type == 'folder'
        assert len(tree[0].children) == 1

    def test_get_tree_excludes_intake(self, kb_service):
        (kb_service.kb_root / '.intake').mkdir()
        _create_md_file(kb_service.kb_root, '.intake/staged.md')
        _create_md_file(kb_service.kb_root, 'visible.md')
        kb_service._invalidate_cache()
        tree = kb_service.get_tree()
        names = [n.name for n in tree]
        assert '.intake' not in names
        assert 'visible.md' in names

    def test_get_tree_excludes_config(self, kb_service):
        """knowledgebase-config.json lives in config/ dir, not in KB tree."""
        tree = kb_service.get_tree()
        names = [n.name for n in tree]
        assert 'knowledgebase-config.json' not in names

    def test_get_tree_file_has_metadata(self, kb_service):
        _create_md_file(kb_service.kb_root, 'test.md',
                        frontmatter={'title': 'Test'})
        kb_service._invalidate_cache()
        tree = kb_service.get_tree()
        node = tree[0]
        assert node.size_bytes is not None
        assert node.modified_date is not None
        assert node.file_type == '.md'

    def test_get_tree_route(self, client, app):
        # Create a test file via service
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        _create_md_file(svc.kb_root, 'test.md', frontmatter={'title': 'T'})
        svc._invalidate_cache()

        resp = client.get('/api/kb/tree')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'tree' in data


# ===========================================================================
# AC-049-A-03: Folder CRUD Operations
# ===========================================================================

class TestFolderCRUD:
    """AC-03: Folder create, rename, move, delete with error codes."""

    def test_create_folder(self, kb_service):
        result = kb_service.create_folder('new-folder')
        assert result['type'] == 'folder'
        assert result['name'] == 'new-folder'
        assert (kb_service.kb_root / 'new-folder').is_dir()

    def test_create_folder_nested(self, kb_service):
        result = kb_service.create_folder('parent/child')
        assert (kb_service.kb_root / 'parent' / 'child').is_dir()

    def test_create_folder_duplicate_409(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        svc.create_folder('dup')

        resp = client.post('/api/kb/folders',
                           json={'path': 'dup'})
        assert resp.status_code == 409

    def test_rename_folder(self, kb_service):
        kb_service.create_folder('old-name')
        result = kb_service.rename_folder('old-name', 'new-name')
        assert result['name'] == 'new-name'
        assert not (kb_service.kb_root / 'old-name').exists()
        assert (kb_service.kb_root / 'new-name').is_dir()

    def test_move_folder(self, kb_service):
        kb_service.create_folder('source')
        kb_service.create_folder('dest')
        result = kb_service.move_folder('source', 'dest')
        assert (kb_service.kb_root / 'dest' / 'source').is_dir()

    def test_move_folder_into_self_400(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        svc.create_folder('parent')
        svc.create_folder('parent/child')

        resp = client.put('/api/kb/folders/move',
                          json={'source': 'parent', 'destination': 'parent/child'})
        assert resp.status_code == 400

    def test_delete_folder(self, kb_service):
        kb_service.create_folder('to-delete')
        _create_md_file(kb_service.kb_root, 'to-delete/f1.md')
        _create_md_file(kb_service.kb_root, 'to-delete/f2.md')
        result = kb_service.delete_folder('to-delete')
        assert result['deleted_count'] == 2
        assert not (kb_service.kb_root / 'to-delete').exists()

    def test_delete_root_403(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.delete('/api/kb/folders',
                             json={'path': '.'})
        assert resp.status_code == 403


# ===========================================================================
# AC-049-A-04: File Listing with Metadata
# ===========================================================================

class TestFileListing:
    """AC-04: File listing with frontmatter, sortable."""

    def test_list_files_in_root(self, kb_service):
        _create_md_file(kb_service.kb_root, 'a.md', frontmatter={'title': 'A'})
        _create_md_file(kb_service.kb_root, 'b.md', frontmatter={'title': 'B'})
        kb_service._invalidate_cache()
        files = kb_service.list_files()
        assert len(files) == 2

    def test_list_files_in_subfolder(self, kb_service):
        (kb_service.kb_root / 'sub').mkdir()
        _create_md_file(kb_service.kb_root, 'sub/doc.md')
        kb_service._invalidate_cache()
        files = kb_service.list_files(folder='sub')
        assert len(files) == 1
        assert files[0].name == 'doc.md'

    def test_list_files_with_frontmatter(self, kb_service):
        _create_md_file(kb_service.kb_root, 'tagged.md',
                        frontmatter={'title': 'Tagged', 'tags': {'lifecycle': ['Design'], 'domain': ['API']}})
        kb_service._invalidate_cache()
        files = kb_service.list_files()
        assert files[0].frontmatter is not None
        assert files[0].frontmatter.title == 'Tagged'

    def test_list_files_no_frontmatter_returns_null(self, kb_service):
        _create_md_file(kb_service.kb_root, 'plain.md', body='No frontmatter')
        kb_service._invalidate_cache()
        files = kb_service.list_files()
        assert files[0].frontmatter is None

    def test_list_files_sort_by_name(self, kb_service):
        _create_md_file(kb_service.kb_root, 'zebra.md')
        _create_md_file(kb_service.kb_root, 'alpha.md')
        kb_service._invalidate_cache()
        files = kb_service.list_files(sort='name')
        assert files[0].name == 'alpha.md'
        assert files[1].name == 'zebra.md'

    def test_list_files_sort_by_created(self, kb_service):
        _create_md_file(kb_service.kb_root, 'older.md',
                        frontmatter={'title': 'Older', 'created': '2026-01-01'})
        _create_md_file(kb_service.kb_root, 'newer.md',
                        frontmatter={'title': 'Newer', 'created': '2026-03-01'})
        kb_service._invalidate_cache()
        files = kb_service.list_files(sort='created')
        assert files[0].name == 'newer.md'
        assert files[1].name == 'older.md'

    def test_list_files_sort_untagged_first(self, kb_service):
        _create_md_file(kb_service.kb_root, 'tagged.md',
                        frontmatter={'title': 'T', 'tags': {'lifecycle': ['Design'], 'domain': []}})
        _create_md_file(kb_service.kb_root, 'untagged.md', body='No tags')
        kb_service._invalidate_cache()
        files = kb_service.list_files(sort='untagged')
        assert files[0].name == 'untagged.md'

    def test_list_files_nonexistent_folder_404(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.get('/api/kb/files?folder=nonexistent')
        assert resp.status_code == 404

    def test_non_markdown_file_no_frontmatter(self, kb_service):
        (kb_service.kb_root / 'image.png').write_bytes(b'\x89PNG')
        kb_service._invalidate_cache()
        files = kb_service.list_files()
        assert files[0].frontmatter is None
        assert files[0].file_type == '.png'


# ===========================================================================
# AC-049-A-05: File CRUD Operations
# ===========================================================================

class TestFileCRUD:
    """AC-05: File create/read/update/delete with auto-populate frontmatter."""

    def test_create_file_with_frontmatter(self, kb_service):
        result = kb_service.create_file('new-article.md', 'Body text', {
            'title': 'New Article',
            'tags': {'lifecycle': ['Design'], 'domain': ['API']},
            'author': 'echo',
        })
        assert result['name'] == 'new-article.md'
        assert result['frontmatter']['title'] == 'New Article'
        assert result['frontmatter']['author'] == 'echo'

    def test_create_file_auto_populate(self, kb_service):
        result = kb_service.create_file('my-guide.md', 'Content')
        fm = result['frontmatter']
        assert fm['title'] == 'My Guide'
        assert fm['author'] == 'unknown'
        assert fm['tags'] == {'lifecycle': [], 'domain': []}

    def test_get_file(self, kb_service):
        kb_service.create_file('test.md', 'Body', {'title': 'Test'})
        result = kb_service.get_file('test.md')
        assert result['content'] == 'Body'
        assert result['frontmatter']['title'] == 'Test'

    def test_update_file_content(self, kb_service):
        kb_service.create_file('update-me.md', 'Old body')
        result = kb_service.update_file('update-me.md', content='New body')
        assert result['content'] == 'New body'

    def test_update_file_frontmatter(self, kb_service):
        kb_service.create_file('update-fm.md', 'Body', {'title': 'Old'})
        result = kb_service.update_file('update-fm.md',
                                         frontmatter={'title': 'New Title'})
        assert result['frontmatter']['title'] == 'New Title'

    def test_delete_file(self, kb_service):
        kb_service.create_file('to-delete.md', 'Gone')
        kb_service.delete_file('to-delete.md')
        assert not (kb_service.kb_root / 'to-delete.md').exists()

    def test_create_file_size_limit(self, kb_service):
        large_content = 'x' * (11 * 1024 * 1024)
        with pytest.raises(ValueError, match='maximum size'):
            kb_service.create_file('big.md', large_content)

    def test_create_file_route_201(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.post('/api/kb/files', json={
            'path': 'article.md',
            'content': 'Hello',
            'frontmatter': {'title': 'Hello'},
        })
        assert resp.status_code == 201


# ===========================================================================
# AC-049-A-06: File Move
# ===========================================================================

class TestFileMove:
    """AC-06: File move with 404 checks."""

    def test_move_file(self, kb_service):
        kb_service.create_file('old/doc.md', 'Hi')
        kb_service.create_folder('new')
        result = kb_service.move_file('old/doc.md', 'new/doc.md')
        assert result['new_path'] == 'new/doc.md'
        assert not (kb_service.kb_root / 'old' / 'doc.md').exists()
        assert (kb_service.kb_root / 'new' / 'doc.md').is_file()

    def test_move_file_to_nonexistent_folder_404(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        svc.create_file('movable.md', 'Content')
        resp = client.put('/api/kb/files/move', json={
            'source': 'movable.md',
            'destination': 'nonexistent/movable.md',
        })
        assert resp.status_code == 404


# ===========================================================================
# AC-049-A-07: YAML Frontmatter Parsing
# ===========================================================================

class TestFrontmatterParsing:
    """AC-07: Frontmatter parsing with graceful degradation."""

    def test_valid_frontmatter(self, kb_service):
        _create_md_file(kb_service.kb_root, 'valid.md',
                        frontmatter={'title': 'Valid', 'tags': {'lifecycle': ['Design'], 'domain': []}})
        fm = kb_service._parse_frontmatter(kb_service.kb_root / 'valid.md')
        assert fm is not None
        assert fm.title == 'Valid'
        assert fm.tags.lifecycle == ['Design']

    def test_no_frontmatter_returns_none(self, kb_service):
        _create_md_file(kb_service.kb_root, 'no-fm.md', body='Just content')
        fm = kb_service._parse_frontmatter(kb_service.kb_root / 'no-fm.md')
        assert fm is None

    def test_malformed_yaml_returns_none(self, kb_service):
        path = kb_service.kb_root / 'bad.md'
        path.write_text("---\ntitle: [invalid yaml\n---\nBody", encoding='utf-8')
        fm = kb_service._parse_frontmatter(path)
        assert fm is None

    def test_frontmatter_preserves_body_on_update(self, kb_service):
        kb_service.create_file('preserve.md', 'My important body',
                               {'title': 'Original'})
        result = kb_service.update_file('preserve.md',
                                         frontmatter={'title': 'Updated'})
        assert result['content'] == 'My important body'
        assert result['frontmatter']['title'] == 'Updated'


# ===========================================================================
# AC-049-A-08: Tag Taxonomy API
# ===========================================================================

class TestTagTaxonomy:
    """AC-08: GET /api/kb/config returns tag taxonomy."""

    def test_get_config(self, kb_service):
        config = kb_service.get_config()
        assert 'tags' in config
        assert 'lifecycle' in config['tags']
        assert 'domain' in config['tags']

    def test_get_config_includes_ai_librarian(self, kb_service):
        config = kb_service.get_config()
        assert 'ai_librarian' in config
        assert 'agent_write_allowlist' in config

    def test_get_config_route(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.get('/api/kb/config')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['tags']['lifecycle'][0] == 'Ideation'

    def test_corrupt_config_500(self, kb_service):
        config_path = kb_service.config_path
        config_path.write_text('not valid json!!!')
        with pytest.raises(RuntimeError, match='Invalid knowledgebase-config.json'):
            kb_service.get_config()


# ===========================================================================
# AC-049-A-09: Search API
# ===========================================================================

class TestSearchAPI:
    """AC-09: Search by query + tag filter, case-insensitive."""

    def test_search_by_filename(self, kb_service):
        _create_md_file(kb_service.kb_root, 'api-guide.md',
                        frontmatter={'title': 'API Guide'})
        kb_service._invalidate_cache()
        results = kb_service.search(query='api')
        assert len(results) == 1

    def test_search_by_title(self, kb_service):
        _create_md_file(kb_service.kb_root, 'doc.md',
                        frontmatter={'title': 'Authentication Guide'})
        kb_service._invalidate_cache()
        results = kb_service.search(query='authentication')
        assert len(results) == 1

    def test_search_by_author(self, kb_service):
        _create_md_file(kb_service.kb_root, 'authored.md',
                        frontmatter={'title': 'Doc', 'author': 'TestAuthor'})
        kb_service._invalidate_cache()
        results = kb_service.search(query='TestAuthor')
        assert len(results) == 1
        assert results[0].name == 'authored.md'

    def test_search_case_insensitive(self, kb_service):
        _create_md_file(kb_service.kb_root, 'test.md',
                        frontmatter={'title': 'Design Pattern'})
        kb_service._invalidate_cache()
        results = kb_service.search(query='DESIGN')
        assert len(results) == 1

    def test_search_by_tag_lifecycle(self, kb_service):
        _create_md_file(kb_service.kb_root, 'tagged.md',
                        frontmatter={'title': 'T', 'tags': {'lifecycle': ['Design'], 'domain': []}})
        _create_md_file(kb_service.kb_root, 'untagged.md',
                        frontmatter={'title': 'U'})
        kb_service._invalidate_cache()
        results = kb_service.search(tag='Design', tag_type='lifecycle')
        assert len(results) == 1
        assert results[0].name == 'tagged.md'

    def test_search_by_tag_domain(self, kb_service):
        _create_md_file(kb_service.kb_root, 'api.md',
                        frontmatter={'title': 'T', 'tags': {'lifecycle': [], 'domain': ['API']}})
        kb_service._invalidate_cache()
        results = kb_service.search(tag='API', tag_type='domain')
        assert len(results) == 1

    def test_search_combined_query_and_tag(self, kb_service):
        _create_md_file(kb_service.kb_root, 'api-v1.md',
                        frontmatter={'title': 'API V1', 'tags': {'lifecycle': ['Design'], 'domain': ['API']}})
        _create_md_file(kb_service.kb_root, 'api-v2.md',
                        frontmatter={'title': 'API V2', 'tags': {'lifecycle': ['Implementation'], 'domain': ['API']}})
        kb_service._invalidate_cache()
        results = kb_service.search(query='v1', tag='API', tag_type='domain')
        assert len(results) == 1
        assert results[0].name == 'api-v1.md'

    def test_search_empty_query_returns_all(self, kb_service):
        _create_md_file(kb_service.kb_root, 'a.md', frontmatter={'title': 'A'})
        _create_md_file(kb_service.kb_root, 'b.md', frontmatter={'title': 'B'})
        kb_service._invalidate_cache()
        results = kb_service.search()
        assert len(results) == 2

    def test_search_route(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        _create_md_file(svc.kb_root, 'searchable.md',
                        frontmatter={'title': 'Searchable'})
        svc._invalidate_cache()
        resp = client.get('/api/kb/search?q=search')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['results']) == 1


# ===========================================================================
# AC-049-A-10: URL Bookmark Format
# ===========================================================================

class TestURLBookmarks:
    """AC-10: .url.md files with url field in frontmatter."""

    def test_create_url_bookmark(self, kb_service):
        result = kb_service.create_file('link.url.md', '', {
            'title': 'Flask Docs',
            'url': 'https://flask.palletsprojects.com',
        })
        assert result['frontmatter']['url'] == 'https://flask.palletsprojects.com'
        assert result['file_type'] == 'url_bookmark'

    def test_create_url_bookmark_missing_url_400(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.post('/api/kb/files', json={
            'path': 'bad-link.url.md',
            'content': '',
            'frontmatter': {'title': 'No URL'},
        })
        assert resp.status_code == 400

    def test_url_bookmark_in_search(self, kb_service):
        kb_service.create_file('ref.url.md', '', {
            'title': 'Reference',
            'url': 'https://example.com',
        })
        kb_service._invalidate_cache()
        results = kb_service.search(query='reference')
        assert len(results) == 1
        assert results[0].file_type == 'url_bookmark'


# ===========================================================================
# AC-049-A-11: File Type Validation
# ===========================================================================

class TestFileTypeValidation:
    """AC-11: Accepted extensions, 415 for unsupported types."""

    def test_accepted_md(self, kb_service):
        result = kb_service.create_file('test.md', 'Content')
        assert result['name'] == 'test.md'

    def test_unsupported_type_415(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.post('/api/kb/files', json={
            'path': 'hack.exe',
            'content': 'bad',
        })
        assert resp.status_code == 415

    def test_url_md_accepted(self, kb_service):
        result = kb_service.create_file('link.url.md', '', {
            'url': 'https://example.com',
        })
        assert result['file_type'] == 'url_bookmark'


# ===========================================================================
# Path Traversal Security
# ===========================================================================

class TestPathTraversal:
    """Path traversal attempts must return 400."""

    def test_traversal_attempt_400(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.get('/api/kb/files/../../etc/passwd')
        assert resp.status_code == 400

    def test_traversal_in_create_400(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.post('/api/kb/files', json={
            'path': '../../../outside.md',
            'content': 'escape',
        })
        assert resp.status_code == 400


# ===========================================================================
# Route-level error handling
# ===========================================================================

class TestRouteErrors:
    """Standard JSON error response format (NFR-049-A-04)."""

    def test_error_format(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.get('/api/kb/files/nonexistent.md')
        assert resp.status_code == 404
        data = resp.get_json()
        assert 'error' in data
        assert 'message' in data

    def test_delete_root_403(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.delete('/api/kb/folders', json={'path': '.'})
        assert resp.status_code == 403
        data = resp.get_json()
        assert data['error'] == 'FORBIDDEN'

    def test_file_413(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.post('/api/kb/files', json={
            'path': 'huge.md',
            'content': 'x' * (11 * 1024 * 1024),
        })
        assert resp.status_code == 413


# ===========================================================================
# AC-049-E-07/08/09: Archive Extraction (.zip / .7z / nested)
# ===========================================================================

class TestZipExtraction:
    """AC-049-E-07: .zip archive auto-extraction into KB."""

    def test_extract_zip_creates_files(self, kb_service):
        import zipfile
        import io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('readme.md', '# Hello')
            zf.writestr('docs/guide.md', '# Guide')
        results = kb_service.extract_zip(buf.getvalue())
        assert len(results) == 2
        paths = {r['path'] for r in results}
        assert 'readme.md' in paths
        assert 'docs/guide.md' in paths
        assert (kb_service.kb_root / 'readme.md').is_file()
        assert (kb_service.kb_root / 'docs' / 'guide.md').is_file()

    def test_extract_zip_into_dest_folder(self, kb_service):
        import zipfile
        import io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('notes.md', 'Notes')
        results = kb_service.extract_zip(buf.getvalue(), dest_folder='archive')
        assert results[0]['path'] == 'archive/notes.md'
        assert (kb_service.kb_root / 'archive' / 'notes.md').is_file()

    def test_extract_zip_skips_nested_archives(self, kb_service):
        import zipfile
        import io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('ok.md', 'good file')
            zf.writestr('nested.zip', b'fake zip data')
            zf.writestr('nested.7z', b'fake 7z data')
        results = kb_service.extract_zip(buf.getvalue())
        paths = {r['path'] for r in results}
        assert 'ok.md' in paths
        assert 'nested.zip' not in paths
        assert 'nested.7z' not in paths

    def test_extract_zip_preserves_folder_structure(self, kb_service):
        import zipfile
        import io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('a/b/c/deep.md', 'Deep file')
        results = kb_service.extract_zip(buf.getvalue())
        assert results[0]['path'] == 'a/b/c/deep.md'
        assert (kb_service.kb_root / 'a' / 'b' / 'c' / 'deep.md').is_file()


class TestSevenZipExtraction:
    """AC-049-E-08: .7z archive auto-extraction into KB."""

    def test_extract_7z_creates_files(self, kb_service):
        py7zr = pytest.importorskip('py7zr')
        import io
        buf = io.BytesIO()
        with py7zr.SevenZipFile(buf, 'w') as z:
            z.writestr(b'# Seven-Zip Doc', 'readme.md')
        results = kb_service.extract_7z(buf.getvalue())
        assert len(results) >= 1
        assert (kb_service.kb_root / 'readme.md').is_file()

    def test_extract_7z_missing_library_raises(self, kb_service, monkeypatch):
        import builtins
        real_import = builtins.__import__
        def mock_import(name, *args, **kwargs):
            if name == 'py7zr':
                raise ImportError('No module named py7zr')
            return real_import(name, *args, **kwargs)
        monkeypatch.setattr(builtins, '__import__', mock_import)
        with pytest.raises(ValueError, match=r'py7zr'):
            kb_service.extract_7z(b'fake data')


class TestNestedArchiveHandling:
    """AC-049-E-09: Nested .zip/.7z inside archives are skipped."""

    def test_nested_zip_inside_zip_skipped(self, kb_service):
        import zipfile
        import io
        # Create inner zip
        inner = io.BytesIO()
        with zipfile.ZipFile(inner, 'w') as zf:
            zf.writestr('inner.md', 'inner content')
        # Create outer zip containing inner.zip + a normal file
        outer = io.BytesIO()
        with zipfile.ZipFile(outer, 'w') as zf:
            zf.writestr('normal.md', 'normal content')
            zf.writestr('inner.zip', inner.getvalue())
        results = kb_service.extract_zip(outer.getvalue())
        paths = {r['path'] for r in results}
        assert 'normal.md' in paths
        assert 'inner.zip' not in paths

    def test_nested_7z_inside_zip_skipped(self, kb_service):
        import zipfile
        import io
        outer = io.BytesIO()
        with zipfile.ZipFile(outer, 'w') as zf:
            zf.writestr('doc.md', 'content')
            zf.writestr('archive.7z', b'fake 7z bytes')
        results = kb_service.extract_zip(outer.getvalue())
        paths = {r['path'] for r in results}
        assert 'doc.md' in paths
        assert 'archive.7z' not in paths


# ===========================================================================
# Route Integration Tests — Coverage Gap Remediation
# ===========================================================================

class TestRouteUpdateFile:
    """Route-level tests for PUT /api/kb/files/{path}."""

    def test_update_file_content(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        svc.create_file('doc.md', 'Original')
        resp = client.put('/api/kb/files/doc.md', json={'content': 'Updated'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['path'] == 'doc.md'

    def test_update_file_not_found(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.put('/api/kb/files/missing.md', json={'content': 'x'})
        assert resp.status_code == 404

    def test_update_file_no_json(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        svc.create_file('doc.md', 'Original')
        resp = client.put('/api/kb/files/doc.md', data='not json')
        assert resp.status_code == 400


class TestRouteDeleteFile:
    """Route-level tests for DELETE /api/kb/files/{path}."""

    def test_delete_file_success(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        svc.create_file('to-delete.md', 'Bye')
        resp = client.delete('/api/kb/files/to-delete.md')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['deleted'] == 'to-delete.md'

    def test_delete_file_not_found(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.delete('/api/kb/files/ghost.md')
        assert resp.status_code == 404


class TestRouteRenameFolder:
    """Route-level tests for PATCH /api/kb/folders."""

    def test_rename_folder_success(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        svc.create_folder('old-name')
        resp = client.patch('/api/kb/folders', json={
            'path': 'old-name', 'new_name': 'new-name'
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['path'] == 'new-name'

    def test_rename_folder_missing_params(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.patch('/api/kb/folders', json={'path': ''})
        assert resp.status_code == 400

    def test_rename_folder_not_found(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.patch('/api/kb/folders', json={
            'path': 'nonexistent', 'new_name': 'whatever'
        })
        assert resp.status_code == 404


class TestRouteUpload:
    """Route-level tests for POST /api/kb/upload."""

    def test_upload_single_file(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        import io
        data = {
            'files': (io.BytesIO(b'# My Doc'), 'readme.md'),
        }
        resp = client.post('/api/kb/upload', data=data,
                           content_type='multipart/form-data')
        assert resp.status_code == 201
        result = resp.get_json()
        assert result['total'] == 1
        assert result['failed'] == 0

    def test_upload_into_subfolder(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        import io
        data = {
            'files': (io.BytesIO(b'content'), 'notes.md'),
            'folder': 'guides',
        }
        resp = client.post('/api/kb/upload', data=data,
                           content_type='multipart/form-data')
        assert resp.status_code == 201
        result = resp.get_json()
        assert result['total'] == 1

    def test_upload_zip_auto_extracts(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        import io, zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('a.md', '# A')
            zf.writestr('b.md', '# B')
        buf.seek(0)
        data = {
            'files': (buf, 'archive.zip'),
        }
        resp = client.post('/api/kb/upload', data=data,
                           content_type='multipart/form-data')
        assert resp.status_code == 201
        result = resp.get_json()
        assert result['total'] == 2

    def test_upload_no_files_400(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.post('/api/kb/upload', data={},
                           content_type='multipart/form-data')
        assert resp.status_code == 400


# ===========================================================================
# FEATURE-049-F: Intake Status Management
# ===========================================================================

class TestIntakeReadStatus:
    """Tests for _read_intake_status() and _write_intake_status()."""

    def test_read_status_missing_file(self, kb_service):
        """Missing .intake-status.json returns empty dict."""
        result = kb_service._read_intake_status()
        assert result == {}

    def test_read_status_corrupted_json(self, kb_service):
        """Corrupted JSON returns empty dict."""
        intake_dir = kb_service.kb_root / '.intake'
        intake_dir.mkdir(parents=True, exist_ok=True)
        status_path = intake_dir / '.intake-status.json'
        status_path.write_text('NOT VALID JSON {{{', encoding='utf-8')
        result = kb_service._read_intake_status()
        assert result == {}

    def test_read_status_not_dict(self, kb_service):
        """Non-dict JSON returns empty dict."""
        intake_dir = kb_service.kb_root / '.intake'
        intake_dir.mkdir(parents=True, exist_ok=True)
        status_path = intake_dir / '.intake-status.json'
        status_path.write_text('["a list"]', encoding='utf-8')
        result = kb_service._read_intake_status()
        assert result == {}

    def test_write_and_read_status(self, kb_service):
        """Write status and read it back."""
        intake_dir = kb_service.kb_root / '.intake'
        intake_dir.mkdir(parents=True, exist_ok=True)
        data = {'test.md': {'status': 'pending', 'destination': None, 'updated_at': '2026-01-01T00:00:00Z'}}
        kb_service._write_intake_status(data)
        result = kb_service._read_intake_status()
        assert result == data


class TestGetIntakeFiles:
    """Tests for get_intake_files()."""

    def test_empty_intake_no_folder(self, kb_service):
        """No .intake/ folder returns empty result."""
        result = kb_service.get_intake_files()
        assert result == {
            'items': [], 'stats': {'total': 0, 'pending': 0, 'processing': 0, 'filed': 0},
            'pending_deep_count': 0,
        }

    def test_empty_intake_folder(self, kb_service):
        """Empty .intake/ folder returns empty result."""
        (kb_service.kb_root / '.intake').mkdir(parents=True)
        result = kb_service.get_intake_files()
        assert result['items'] == []
        assert result['stats']['total'] == 0
        assert result['pending_deep_count'] == 0

    def test_files_without_status(self, kb_service):
        """Files in .intake/ with no status.json default to pending."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        (intake / 'notes.md').write_text('Hello', encoding='utf-8')
        (intake / 'doc.txt').write_text('World', encoding='utf-8')
        result = kb_service.get_intake_files()
        assert result['stats']['total'] == 2
        assert result['stats']['pending'] == 2
        files_only = [i for i in result['items'] if i['type'] == 'file']
        assert all(f['status'] == 'pending' for f in files_only)
        assert all(f['destination'] is None for f in files_only)

    def test_files_with_status(self, kb_service):
        """Files merged with .intake-status.json entries."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        (intake / 'a.md').write_text('A', encoding='utf-8')
        (intake / 'b.pdf').write_bytes(b'\x00' * 100)
        kb_service._write_intake_status({
            'a.md': {'status': 'filed', 'destination': 'guides/', 'updated_at': '2026-01-01T00:00:00Z'},
            'b.pdf': {'status': 'processing', 'destination': None, 'updated_at': '2026-01-01T00:00:00Z'},
        })
        result = kb_service.get_intake_files()
        assert result['stats']['total'] == 2
        assert result['stats']['filed'] == 1
        assert result['stats']['processing'] == 1
        by_name = {i['name']: i for i in result['items']}
        assert by_name['a.md']['status'] == 'filed'
        assert by_name['a.md']['destination'] == 'guides/'
        assert by_name['b.pdf']['status'] == 'processing'

    def test_stale_status_entries_ignored(self, kb_service):
        """Status entries for deleted files are silently ignored."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        (intake / 'exists.md').write_text('Hi', encoding='utf-8')
        kb_service._write_intake_status({
            'exists.md': {'status': 'pending', 'destination': None},
            'deleted.md': {'status': 'filed', 'destination': 'archive/'},
        })
        result = kb_service.get_intake_files()
        assert result['stats']['total'] == 1
        assert result['items'][0]['name'] == 'exists.md'

    def test_status_json_excluded_from_files(self, kb_service):
        """.intake-status.json is not listed as a file."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        (intake / 'note.md').write_text('Note', encoding='utf-8')
        kb_service._write_intake_status({'note.md': {'status': 'pending'}})
        result = kb_service.get_intake_files()
        names = [i['name'] for i in result['items']]
        assert '.intake-status.json' not in names

    def test_file_metadata_fields(self, kb_service):
        """Each file has expected metadata fields."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        (intake / 'readme.md').write_text('Hello World', encoding='utf-8')
        result = kb_service.get_intake_files()
        f = result['items'][0]
        assert f['name'] == 'readme.md'
        assert f['path'] == 'readme.md'
        assert f['type'] == 'file'
        assert f['size_bytes'] > 0
        assert f['file_type'] == 'md'
        assert 'modified_date' in f


class TestUpdateIntakeStatus:
    """Tests for update_intake_status()."""

    def test_update_valid_file(self, kb_service):
        """Successfully update status of existing intake file."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        (intake / 'doc.md').write_text('Content', encoding='utf-8')
        result = kb_service.update_intake_status('doc.md', 'processing', 'guides/')
        assert result['ok'] is True
        assert result['status'] == 'processing'
        assert result['destination'] == 'guides/'
        # Verify persisted
        status = kb_service._read_intake_status()
        assert status['doc.md']['status'] == 'processing'

    def test_update_nonexistent_file_raises(self, kb_service):
        """Updating status of a missing path raises ValueError."""
        (kb_service.kb_root / '.intake').mkdir(parents=True)
        with pytest.raises(ValueError, match='Path not in .intake'):
            kb_service.update_intake_status('missing.md', 'pending')

    def test_update_multiple_times(self, kb_service):
        """Multiple status updates accumulate correctly."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        (intake / 'a.md').write_text('A', encoding='utf-8')
        (intake / 'b.md').write_text('B', encoding='utf-8')
        kb_service.update_intake_status('a.md', 'processing')
        kb_service.update_intake_status('b.md', 'filed', 'docs/')
        status = kb_service._read_intake_status()
        assert status['a.md']['status'] == 'processing'
        assert status['b.md']['status'] == 'filed'
        assert status['b.md']['destination'] == 'docs/'


# CR-005: Folder Support Tests
class TestIntakeFolderTree:
    """CR-005: Tree builder, derived status, deep count, folder cascade."""

    def test_tree_with_nested_directory(self, kb_service):
        """Nested directories produce tree with children."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        sub = intake / 'docs'
        sub.mkdir()
        (sub / 'api.md').write_text('API', encoding='utf-8')
        (sub / 'setup.md').write_text('Setup', encoding='utf-8')
        (intake / 'readme.md').write_text('Readme', encoding='utf-8')
        result = kb_service.get_intake_files()
        # Folders sort before files
        assert result['items'][0]['type'] == 'folder'
        assert result['items'][0]['name'] == 'docs'
        assert result['items'][0]['item_count'] == 2
        assert len(result['items'][0]['children']) == 2
        assert result['items'][1]['type'] == 'file'
        assert result['items'][1]['name'] == 'readme.md'

    def test_tree_skips_hidden_files(self, kb_service):
        """Hidden files (starting with .) are excluded from tree."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        (intake / '.hidden').write_text('secret', encoding='utf-8')
        (intake / 'visible.md').write_text('Hello', encoding='utf-8')
        result = kb_service.get_intake_files()
        names = [i['name'] for i in result['items']]
        assert '.hidden' not in names
        assert 'visible.md' in names

    def test_tree_uses_relative_paths(self, kb_service):
        """File paths are relative to .intake/ root."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        sub = intake / 'sub'
        sub.mkdir()
        (sub / 'file.md').write_text('Nested', encoding='utf-8')
        result = kb_service.get_intake_files()
        folder = result['items'][0]
        assert folder['path'] == 'sub'
        child = folder['children'][0]
        assert child['path'] == 'sub/file.md'

    def test_derive_folder_status_pending_priority(self, kb_service):
        """If any child is pending, folder status is pending."""
        from x_ipe.services.kb_service import KBService
        children = [
            {'status': 'filed'},
            {'status': 'pending'},
            {'status': 'processing'},
        ]
        assert KBService._derive_folder_status(children) == 'pending'

    def test_derive_folder_status_processing_priority(self, kb_service):
        """If no pending but processing, folder status is processing."""
        from x_ipe.services.kb_service import KBService
        children = [
            {'status': 'filed'},
            {'status': 'processing'},
        ]
        assert KBService._derive_folder_status(children) == 'processing'

    def test_derive_folder_status_all_filed(self, kb_service):
        """If all children filed, folder status is filed."""
        from x_ipe.services.kb_service import KBService
        children = [
            {'status': 'filed'},
            {'status': 'filed'},
        ]
        assert KBService._derive_folder_status(children) == 'filed'

    def test_derive_folder_status_empty(self, kb_service):
        """Empty folder defaults to pending."""
        from x_ipe.services.kb_service import KBService
        assert KBService._derive_folder_status([]) == 'pending'

    def test_count_pending_deep(self, kb_service):
        """Recursively counts only pending files."""
        items = [
            {'type': 'file', 'status': 'pending'},
            {'type': 'file', 'status': 'filed'},
            {'type': 'folder', 'status': 'pending', 'children': [
                {'type': 'file', 'status': 'pending'},
                {'type': 'file', 'status': 'processing'},
            ]},
        ]
        assert kb_service._count_pending_deep(items) == 2

    def test_count_pending_deep_empty(self, kb_service):
        """No items returns 0."""
        assert kb_service._count_pending_deep([]) == 0

    def test_update_folder_cascade(self, kb_service):
        """Updating a folder cascades status to all child files."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        sub = intake / 'docs'
        sub.mkdir()
        (sub / 'a.md').write_text('A', encoding='utf-8')
        (sub / 'b.md').write_text('B', encoding='utf-8')
        result = kb_service.update_intake_status('docs', 'processing', 'guides/')
        assert result['ok'] is True
        status = kb_service._read_intake_status()
        assert status['docs/a.md']['status'] == 'processing'
        assert status['docs/b.md']['status'] == 'processing'
        assert status['docs/a.md']['destination'] == 'guides/'

    def test_update_relative_path_file(self, kb_service):
        """Can update status using relative path for nested files."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        sub = intake / 'sub'
        sub.mkdir()
        (sub / 'nested.md').write_text('Nested', encoding='utf-8')
        result = kb_service.update_intake_status('sub/nested.md', 'filed', 'archive/')
        assert result['ok'] is True
        status = kb_service._read_intake_status()
        assert status['sub/nested.md']['status'] == 'filed'

    def test_pending_deep_count_in_response(self, kb_service):
        """get_intake_files includes pending_deep_count with correct value."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        sub = intake / 'docs'
        sub.mkdir()
        (sub / 'a.md').write_text('A', encoding='utf-8')
        (sub / 'b.md').write_text('B', encoding='utf-8')
        (intake / 'readme.md').write_text('Readme', encoding='utf-8')
        kb_service._write_intake_status({
            'docs/a.md': {'status': 'filed', 'destination': 'guides/'},
        })
        result = kb_service.get_intake_files()
        # b.md and readme.md are pending, a.md is filed
        assert result['pending_deep_count'] == 2

    def test_folder_cascade_nested(self, kb_service):
        """Folder cascade works for deeply nested structures."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        sub = intake / 'level1'
        sub.mkdir()
        sub2 = sub / 'level2'
        sub2.mkdir()
        (sub2 / 'deep.md').write_text('Deep', encoding='utf-8')
        result = kb_service.update_intake_status('level1', 'filed', 'archive/')
        status = kb_service._read_intake_status()
        assert status['level1/level2/deep.md']['status'] == 'filed'

    def test_path_traversal_rejected(self, kb_service):
        """Path traversal attempts are rejected."""
        intake = kb_service.kb_root / '.intake'
        intake.mkdir(parents=True)
        with pytest.raises(ValueError, match='Path not in .intake'):
            kb_service.update_intake_status('../../../etc/passwd', 'pending')


class TestIntakeRoutes:
    """Tests for GET /api/kb/intake and PUT /api/kb/intake/status."""

    def test_get_intake_empty(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.get('/api/kb/intake')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['items'] == []
        assert data['stats']['total'] == 0
        assert data['pending_deep_count'] == 0

    def test_get_intake_with_files(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        intake = svc.kb_root / '.intake'
        intake.mkdir(parents=True)
        (intake / 'test.md').write_text('Hello', encoding='utf-8')
        resp = client.get('/api/kb/intake')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['stats']['total'] == 1
        assert data['stats']['pending'] == 1

    def test_put_intake_status_valid(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        intake = svc.kb_root / '.intake'
        intake.mkdir(parents=True)
        (intake / 'note.md').write_text('Note', encoding='utf-8')
        resp = client.put('/api/kb/intake/status',
                          json={'filename': 'note.md', 'status': 'processing', 'destination': 'guides/'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['ok'] is True

    def test_put_intake_status_invalid(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.put('/api/kb/intake/status',
                          json={'filename': '', 'status': 'invalid'})
        assert resp.status_code == 400

    def test_put_intake_status_missing_file(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        (svc.kb_root / '.intake').mkdir(parents=True)
        resp = client.put('/api/kb/intake/status',
                          json={'filename': 'missing.md', 'status': 'pending'})
        assert resp.status_code == 404


# ===========================================================================
# CR-003: KB Index API Routes
# ===========================================================================

class TestKBIndexRoutes:
    """CR-003: REST API routes for .kb-index.json CRUD."""

    def test_get_index_empty(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.get('/api/kb/index')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['index']['entries'] == {}

    def test_get_index_with_entries(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        svc._set_index_entry(svc.kb_root, 'doc.md', {'title': 'Doc', 'type': 'markdown'})
        resp = client.get('/api/kb/index')
        data = resp.get_json()
        assert 'doc.md' in data['index']['entries']
        assert data['index']['entries']['doc.md']['title'] == 'Doc'

    def test_get_index_subfolder(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        sub = svc.kb_root / 'guides'
        sub.mkdir()
        svc._set_index_entry(sub, 'setup.md', {'title': 'Setup'})
        resp = client.get('/api/kb/index?folder=guides')
        data = resp.get_json()
        assert data['success'] is True
        assert 'setup.md' in data['index']['entries']

    def test_get_index_nonexistent_folder(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.get('/api/kb/index?folder=nonexistent')
        assert resp.status_code == 404

    def test_set_index_entry(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.put('/api/kb/index/entry', json={
            'name': 'photo.png',
            'entry': {'title': 'Team Photo', 'type': 'image', 'description': 'Team meeting'},
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['name'] == 'photo.png'
        # Verify actually written
        entry = svc._get_index_entry(svc.kb_root, 'photo.png')
        assert entry['title'] == 'Team Photo'

    def test_set_index_entry_in_subfolder(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        (svc.kb_root / 'docs').mkdir()
        resp = client.put('/api/kb/index/entry', json={
            'folder': 'docs',
            'name': 'readme.md',
            'entry': {'title': 'README', 'type': 'markdown'},
        })
        assert resp.status_code == 200
        entry = svc._get_index_entry(svc.kb_root / 'docs', 'readme.md')
        assert entry['title'] == 'README'

    def test_set_index_entry_missing_name(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.put('/api/kb/index/entry', json={
            'entry': {'title': 'No Name'},
        })
        assert resp.status_code == 400

    def test_set_index_entry_missing_entry(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.put('/api/kb/index/entry', json={
            'name': 'test.md',
        })
        assert resp.status_code == 400

    def test_remove_index_entry(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        svc._set_index_entry(svc.kb_root, 'doomed.md', {'title': 'Doomed'})
        resp = client.delete('/api/kb/index/entry', json={
            'name': 'doomed.md',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['removed'] is True
        assert svc._get_index_entry(svc.kb_root, 'doomed.md') is None

    def test_remove_index_entry_missing_name(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.delete('/api/kb/index/entry', json={})
        assert resp.status_code == 400

    def test_set_folder_entry(self, client, app):
        svc = app.config['KB_SERVICE']
        svc.ensure_kb_root()
        resp = client.put('/api/kb/index/entry', json={
            'name': 'guides/',
            'entry': {'title': 'Guides', 'description': 'How-to guides'},
        })
        assert resp.status_code == 200
        entry = svc._get_index_entry(svc.kb_root, 'guides/')
        assert entry['title'] == 'Guides'

class TestKBIndex:
    """CR-002: .kb-index.json per-folder metadata registry."""

    def test_read_kb_index_missing_returns_empty(self, kb_service):
        idx = kb_service._read_kb_index(kb_service.kb_root)
        assert idx['version'] == '1.0'
        assert idx['entries'] == {}

    def test_write_and_read_kb_index(self, kb_service):
        data = {'version': '1.0', 'entries': {'test.md': {'title': 'Test'}}}
        kb_service._write_kb_index(kb_service.kb_root, data)
        result = kb_service._read_kb_index(kb_service.kb_root)
        assert result['entries']['test.md']['title'] == 'Test'

    def test_read_kb_index_corrupted_returns_empty(self, kb_service):
        idx_path = kb_service.kb_root / '.kb-index.json'
        idx_path.write_text('not valid json!!!', encoding='utf-8')
        idx = kb_service._read_kb_index(kb_service.kb_root)
        assert idx['entries'] == {}

    def test_set_and_get_index_entry(self, kb_service):
        entry = {'title': 'Hello', 'type': 'markdown'}
        kb_service._set_index_entry(kb_service.kb_root, 'hello.md', entry)
        result = kb_service._get_index_entry(kb_service.kb_root, 'hello.md')
        assert result['title'] == 'Hello'
        assert result['type'] == 'markdown'

    def test_get_index_entry_missing_returns_none(self, kb_service):
        result = kb_service._get_index_entry(kb_service.kb_root, 'nope.md')
        assert result is None

    def test_remove_index_entry(self, kb_service):
        kb_service._set_index_entry(kb_service.kb_root, 'bye.md', {'title': 'Bye'})
        kb_service._remove_index_entry(kb_service.kb_root, 'bye.md')
        assert kb_service._get_index_entry(kb_service.kb_root, 'bye.md') is None

    def test_remove_index_entry_missing_noop(self, kb_service):
        # Should not raise
        kb_service._remove_index_entry(kb_service.kb_root, 'nonexistent.md')

    def test_detect_kb_file_type(self, kb_service):
        assert kb_service._detect_kb_file_type('doc.md') == 'markdown'
        assert kb_service._detect_kb_file_type('pic.png') == 'image'
        assert kb_service._detect_kb_file_type('vid.mp4') == 'video'
        assert kb_service._detect_kb_file_type('report.pdf') == 'pdf'
        assert kb_service._detect_kb_file_type('slides.pptx') == 'document'
        assert kb_service._detect_kb_file_type('data.csv') == 'other'

    def test_auto_populate_index_entry_defaults(self, kb_service):
        entry = kb_service._auto_populate_index_entry('my-notes.md')
        assert entry['title'] == 'My Notes'
        assert entry['author'] == 'unknown'
        assert entry['type'] == 'markdown'
        assert entry['description'] == ''
        assert entry['tags'] == {'lifecycle': [], 'domain': []}
        assert entry['auto_generated'] is False

    def test_auto_populate_index_entry_with_metadata(self, kb_service):
        entry = kb_service._auto_populate_index_entry('photo.jpg', {
            'title': 'Team Photo',
            'description': 'Team meeting 2026',
            'author': 'alice',
        })
        assert entry['title'] == 'Team Photo'
        assert entry['description'] == 'Team meeting 2026'
        assert entry['author'] == 'alice'
        assert entry['type'] == 'image'

    def test_index_entry_to_frontmatter_conversion(self, kb_service):
        entry = {
            'title': 'Test',
            'description': 'A test file',
            'tags': {'lifecycle': ['Draft'], 'domain': ['API']},
            'author': 'bob',
            'created': '2026-03-17',
            'auto_generated': False,
        }
        fm = kb_service._index_entry_to_frontmatter(entry)
        assert fm.title == 'Test'
        assert fm.description == 'A test file'
        assert fm.tags.lifecycle == ['Draft']
        assert fm.author == 'bob'

    def test_create_file_writes_index_entry(self, kb_service):
        kb_service.create_file('indexed.md', 'Body', {'title': 'Indexed'})
        entry = kb_service._get_index_entry(kb_service.kb_root, 'indexed.md')
        assert entry is not None
        assert entry['title'] == 'Indexed'
        assert entry['type'] == 'markdown'

    def test_create_file_no_frontmatter_in_content(self, kb_service):
        """New files should NOT have YAML frontmatter injected into content."""
        kb_service.create_file('clean.md', 'Just body', {'title': 'Clean'})
        raw = (kb_service.kb_root / 'clean.md').read_text(encoding='utf-8')
        assert not raw.startswith('---')
        assert raw == 'Just body'

    def test_create_binary_file_writes_index_entry(self, kb_service):
        result = kb_service.create_binary_file('photo.png', b'\x89PNG\r\n',
                                                metadata={'title': 'Photo'})
        entry = kb_service._get_index_entry(kb_service.kb_root, 'photo.png')
        assert entry is not None
        assert entry['title'] == 'Photo'
        assert entry['type'] == 'image'
        assert result['frontmatter']['title'] == 'Photo'

    def test_delete_file_removes_index_entry(self, kb_service):
        kb_service.create_file('doomed.md', 'Gone')
        assert kb_service._get_index_entry(kb_service.kb_root, 'doomed.md') is not None
        kb_service.delete_file('doomed.md')
        assert kb_service._get_index_entry(kb_service.kb_root, 'doomed.md') is None

    def test_move_file_transfers_index_entry(self, kb_service):
        kb_service.create_file('src/doc.md', 'Hi', {'title': 'Doc'})
        kb_service.create_folder('dst')
        kb_service.move_file('src/doc.md', 'dst/doc.md')
        # Source folder should NOT have the entry
        src_folder = kb_service.kb_root / 'src'
        assert kb_service._get_index_entry(src_folder, 'doc.md') is None
        # Destination folder SHOULD have it
        dst_folder = kb_service.kb_root / 'dst'
        entry = kb_service._get_index_entry(dst_folder, 'doc.md')
        assert entry is not None
        assert entry['title'] == 'Doc'

    def test_update_file_updates_index_entry(self, kb_service):
        kb_service.create_file('evolve.md', 'V1', {'title': 'V1'})
        kb_service.update_file('evolve.md', frontmatter={'title': 'V2'})
        entry = kb_service._get_index_entry(kb_service.kb_root, 'evolve.md')
        assert entry['title'] == 'V2'

    def test_get_file_returns_index_metadata(self, kb_service):
        kb_service.create_file('meta.md', 'Body', {
            'title': 'Meta Test',
            'description': 'Testing index metadata',
        })
        result = kb_service.get_file('meta.md')
        assert result['frontmatter']['title'] == 'Meta Test'
        assert result['frontmatter']['description'] == 'Testing index metadata'

    def test_tree_excludes_kb_index_file(self, kb_service):
        kb_service.create_file('visible.md', 'Hi')
        tree = kb_service.get_tree()
        names = [n.name for n in tree]
        assert '.kb-index.json' not in names
        assert 'visible.md' in names

    def test_description_field_in_to_dict(self, kb_service):
        result = kb_service.create_file('desc.md', 'Body', {
            'title': 'Desc Test',
            'description': 'Short description',
        })
        assert result['frontmatter']['description'] == 'Short description'

    def test_locally_scoped_index_per_folder(self, kb_service):
        """Each folder has its own .kb-index.json — not shared."""
        kb_service.create_file('root-file.md', 'Root')
        kb_service.create_file('sub/nested.md', 'Nested')
        # Root index should have root-file.md but NOT nested.md
        root_entry = kb_service._get_index_entry(kb_service.kb_root, 'root-file.md')
        assert root_entry is not None
        root_nested = kb_service._get_index_entry(kb_service.kb_root, 'nested.md')
        assert root_nested is None
        # Sub index should have nested.md
        sub_folder = kb_service.kb_root / 'sub'
        sub_entry = kb_service._get_index_entry(sub_folder, 'nested.md')
        assert sub_entry is not None


class TestKBIndexMigration:
    """CR-002: Migration from frontmatter to .kb-index.json."""

    def test_migrate_reads_frontmatter_from_md(self, kb_service):
        """Migration extracts YAML frontmatter and writes to index."""
        _create_md_file(kb_service.kb_root, 'legacy.md',
                        frontmatter={'title': 'Legacy', 'author': 'old-author'},
                        body='Legacy content')
        kb_service._migrate_frontmatter_to_index(kb_service.kb_root)
        entry = kb_service._get_index_entry(kb_service.kb_root, 'legacy.md')
        assert entry is not None
        assert entry['title'] == 'Legacy'
        assert entry['author'] == 'old-author'
        assert entry['type'] == 'markdown'

    def test_migrate_skips_if_index_exists(self, kb_service):
        """Migration is a no-op if .kb-index.json already exists."""
        kb_service._set_index_entry(kb_service.kb_root, 'existing.md', {'title': 'Existing'})
        _create_md_file(kb_service.kb_root, 'new.md',
                        frontmatter={'title': 'New'}, body='Content')
        kb_service._migrate_frontmatter_to_index(kb_service.kb_root)
        # Should NOT have migrated new.md since index already existed
        entry = kb_service._get_index_entry(kb_service.kb_root, 'new.md')
        assert entry is None

    def test_migrate_handles_md_without_frontmatter(self, kb_service):
        """MD files without frontmatter get auto-populated entries."""
        _create_md_file(kb_service.kb_root, 'plain.md', body='No frontmatter here')
        kb_service._migrate_frontmatter_to_index(kb_service.kb_root)
        entry = kb_service._get_index_entry(kb_service.kb_root, 'plain.md')
        assert entry is not None
        assert entry['title'] == 'Plain'  # auto-populated from filename

    def test_migrate_handles_non_markdown_files(self, kb_service):
        """Non-markdown files get auto-populated entries during migration."""
        (kb_service.kb_root / 'photo.png').write_bytes(b'\x89PNG')
        kb_service._migrate_frontmatter_to_index(kb_service.kb_root)
        entry = kb_service._get_index_entry(kb_service.kb_root, 'photo.png')
        assert entry is not None
        assert entry['type'] == 'image'

    def test_build_tree_fallback_to_frontmatter(self, kb_service):
        """When no .kb-index.json exists, _build_tree falls back to frontmatter."""
        _create_md_file(kb_service.kb_root, 'old-style.md',
                        frontmatter={'title': 'Old Style'}, body='Content')
        kb_service._invalidate_cache()
        tree = kb_service.get_tree()
        file_node = [n for n in tree if n.name == 'old-style.md']
        assert len(file_node) == 1
        assert file_node[0].frontmatter.title == 'Old Style'
