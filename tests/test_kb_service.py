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
    """AC-01: Auto-create KB root + kb-config.json with default tags."""

    def test_ensure_kb_root_creates_directory(self, temp_project):
        from x_ipe.services.kb_service import KBService
        svc = KBService(temp_project)
        svc.ensure_kb_root()
        assert svc.kb_root.is_dir()

    def test_ensure_kb_root_creates_config(self, kb_service):
        config_path = kb_service.kb_root / 'kb-config.json'
        assert config_path.exists()
        config = json.loads(config_path.read_text())
        assert 'tags' in config
        assert 'lifecycle' in config['tags']
        assert 'domain' in config['tags']

    def test_default_lifecycle_tags(self, kb_service):
        config = json.loads((kb_service.kb_root / 'kb-config.json').read_text())
        expected = ['Ideation', 'Requirement', 'Design', 'Implementation',
                    'Testing', 'Deployment', 'Maintenance']
        assert config['tags']['lifecycle'] == expected

    def test_default_domain_tags(self, kb_service):
        config = json.loads((kb_service.kb_root / 'kb-config.json').read_text())
        expected = ['API', 'Authentication', 'UI-UX', 'Database',
                    'Infrastructure', 'Security', 'Performance',
                    'Integration', 'Documentation', 'Analytics']
        assert config['tags']['domain'] == expected

    def test_default_agent_write_allowlist(self, kb_service):
        config = json.loads((kb_service.kb_root / 'kb-config.json').read_text())
        assert config['agent_write_allowlist'] == []

    def test_default_ai_librarian_settings(self, kb_service):
        config = json.loads((kb_service.kb_root / 'kb-config.json').read_text())
        assert config['ai_librarian'] == {'enabled': False, 'intake_folder': '.intake'}

    def test_ensure_kb_root_idempotent(self, kb_service):
        """Calling ensure_kb_root again doesn't overwrite existing config."""
        config_path = kb_service.kb_root / 'kb-config.json'
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
        """kb-config.json should not appear in tree."""
        tree = kb_service.get_tree()
        names = [n.name for n in tree]
        assert 'kb-config.json' not in names

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
        config_path = kb_service.kb_root / 'kb-config.json'
        config_path.write_text('not valid json!!!')
        with pytest.raises(RuntimeError, match='Invalid kb-config.json'):
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
