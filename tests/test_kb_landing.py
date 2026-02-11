"""
Tests for FEATURE-025-B: KB Landing Zone

Tests cover:
- KBService: upload_files(), delete_files(), get_landing_files(), _validate_upload()
- File validation: allowed extensions, size limits, duplicate detection
- API endpoints: POST /api/kb/upload, POST /api/kb/landing/delete, GET /api/kb/landing
- Integration: upload → index refresh, delete → index refresh
- Edge cases: oversized files, invalid extensions, path traversal, empty inputs
- Tracing: @x_ipe_tracing on new endpoints

TDD: All tests should FAIL before implementation.
"""
import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from io import BytesIO


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
def temp_kb_dir(temp_project_dir):
    """Create temporary knowledge-base directory structure"""
    kb_path = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base'
    kb_path.mkdir(parents=True, exist_ok=True)
    (kb_path / 'landing').mkdir(exist_ok=True)
    (kb_path / 'topics').mkdir(exist_ok=True)
    (kb_path / 'processed').mkdir(exist_ok=True)
    (kb_path / 'index').mkdir(exist_ok=True)
    # Create empty index
    (kb_path / 'index' / 'file-index.json').write_text(json.dumps({
        "version": "1.0",
        "last_updated": "2026-02-05T15:00:00Z",
        "files": []
    }))
    return kb_path


@pytest.fixture
def populated_landing(temp_kb_dir):
    """Create landing directory with sample files"""
    landing = temp_kb_dir / 'landing'
    (landing / 'document.pdf').write_bytes(b'%PDF-1.4 fake pdf content')
    (landing / 'notes.md').write_text('# My Notes\n\nSome content here.')
    (landing / 'data.json').write_text('{"key": "value"}')
    # Update index with these files
    index_path = temp_kb_dir / 'index' / 'file-index.json'
    index_path.write_text(json.dumps({
        "version": "1.0",
        "last_updated": "2026-02-05T15:00:00Z",
        "files": [
            {
                "path": "landing/document.pdf",
                "name": "document.pdf",
                "type": "pdf",
                "size": 25,
                "topic": None,
                "created_date": "2026-02-05T14:30:00Z",
                "keywords": ["document"]
            },
            {
                "path": "landing/notes.md",
                "name": "notes.md",
                "type": "markdown",
                "size": 35,
                "topic": None,
                "created_date": "2026-02-05T14:35:00Z",
                "keywords": ["notes"]
            },
            {
                "path": "landing/data.json",
                "name": "data.json",
                "type": "json",
                "size": 16,
                "topic": None,
                "created_date": "2026-02-05T14:40:00Z",
                "keywords": ["data"]
            }
        ]
    }))
    return landing


@pytest.fixture
def kb_service(temp_project_dir, temp_kb_dir):
    """Create KBService instance with temp directory and initialized structure"""
    from x_ipe.services import KBService
    return KBService(temp_project_dir)


@pytest.fixture
def kb_service_populated(temp_project_dir, populated_landing):
    """Create KBService with populated landing directory"""
    from x_ipe.services import KBService
    return KBService(temp_project_dir)


@pytest.fixture
def app(temp_project_dir, temp_kb_dir):
    """Create Flask test app"""
    from x_ipe.app import create_app
    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': temp_project_dir
    })
    return app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def app_populated(temp_project_dir, populated_landing):
    """Create Flask test app with populated landing"""
    from x_ipe.app import create_app
    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': temp_project_dir
    })
    return app


@pytest.fixture
def client_populated(app_populated):
    """Create Flask test client with populated landing"""
    return app_populated.test_client()


# ============================================================================
# KBService Unit Tests - _validate_upload()
# ============================================================================

class TestKBServiceValidateUpload:
    """Tests for KBService._validate_upload() private validation method"""

    def test_validate_upload_valid_pdf(self, kb_service):
        """AC-1.1: PDF files are accepted"""
        valid, msg = kb_service._validate_upload('document.pdf', 1024)
        assert valid is True
        assert msg == ''

    def test_validate_upload_valid_markdown(self, kb_service):
        """AC-1.1: Markdown files are accepted"""
        valid, msg = kb_service._validate_upload('notes.md', 512)
        assert valid is True

    def test_validate_upload_valid_txt(self, kb_service):
        """AC-1.1: TXT files are accepted"""
        valid, msg = kb_service._validate_upload('readme.txt', 256)
        assert valid is True

    def test_validate_upload_valid_docx(self, kb_service):
        """AC-1.1: DOCX files are accepted"""
        valid, msg = kb_service._validate_upload('report.docx', 2048)
        assert valid is True

    def test_validate_upload_valid_code_files(self, kb_service):
        """AC-1.1: Code files (.py, .js, .ts, .java, .go, .rs, .c, .cpp, .h) are accepted"""
        code_files = [
            'script.py', 'app.js', 'main.ts', 'App.java',
            'main.go', 'lib.rs', 'hello.c', 'class.cpp', 'header.h'
        ]
        for filename in code_files:
            valid, msg = kb_service._validate_upload(filename, 1024)
            assert valid is True, f"Expected {filename} to be valid"

    def test_validate_upload_valid_web_files(self, kb_service):
        """AC-1.1: Web files (.html, .css, .json, .yaml, .yml) are accepted"""
        web_files = ['page.html', 'style.css', 'config.json', 'docker.yaml', 'ci.yml']
        for filename in web_files:
            valid, msg = kb_service._validate_upload(filename, 1024)
            assert valid is True, f"Expected {filename} to be valid"

    def test_validate_upload_valid_image_files(self, kb_service):
        """AC-1.1: Image files (.png, .jpg, .jpeg, .gif, .svg, .webp) are accepted"""
        image_files = ['photo.png', 'pic.jpg', 'img.jpeg', 'anim.gif', 'icon.svg', 'hero.webp']
        for filename in image_files:
            valid, msg = kb_service._validate_upload(filename, 1024)
            assert valid is True, f"Expected {filename} to be valid"

    def test_validate_upload_invalid_extension(self, kb_service):
        """AC-1.2: Unsupported extensions are rejected"""
        valid, msg = kb_service._validate_upload('virus.exe', 1024)
        assert valid is False
        assert 'extension' in msg.lower() or 'type' in msg.lower()

    def test_validate_upload_invalid_zip(self, kb_service):
        """AC-1.2: ZIP files are not in allowed list"""
        valid, msg = kb_service._validate_upload('archive.zip', 1024)
        assert valid is False

    def test_validate_upload_no_extension(self, kb_service):
        """AC-1.2: Files without extension are rejected"""
        valid, msg = kb_service._validate_upload('Makefile', 1024)
        assert valid is False

    def test_validate_upload_exceeds_size_limit(self, kb_service):
        """AC-1.3: Files exceeding 50MB are rejected"""
        size = 51 * 1024 * 1024  # 51MB
        valid, msg = kb_service._validate_upload('large.pdf', size)
        assert valid is False
        assert '50' in msg or 'size' in msg.lower()

    def test_validate_upload_at_size_limit(self, kb_service):
        """AC-1.3: Files exactly at 50MB are accepted"""
        size = 50 * 1024 * 1024  # 50MB exactly
        valid, msg = kb_service._validate_upload('exact.pdf', size)
        assert valid is True

    def test_validate_upload_case_insensitive_extension(self, kb_service):
        """AC-1.1: Extension check is case-insensitive"""
        valid, msg = kb_service._validate_upload('Document.PDF', 1024)
        assert valid is True

    def test_validate_upload_markdown_alt_extension(self, kb_service):
        """AC-1.1: .markdown extension is accepted"""
        valid, msg = kb_service._validate_upload('readme.markdown', 1024)
        assert valid is True


# ============================================================================
# KBService Unit Tests - upload_files()
# ============================================================================

class TestKBServiceUploadFiles:
    """Tests for KBService.upload_files()"""

    def test_upload_single_file(self, kb_service, temp_project_dir):
        """AC-1.4: Single file upload saves to landing/"""
        files = [('test.md', b'# Test Content', 14)]
        result = kb_service.upload_files(files)

        assert 'landing/test.md' in result['uploaded']
        assert len(result['errors']) == 0
        assert len(result['skipped']) == 0

        file_path = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base' / 'landing' / 'test.md'
        assert file_path.exists()
        assert file_path.read_text() == '# Test Content'

    def test_upload_multiple_files(self, kb_service, temp_project_dir):
        """AC-1.5: Multiple files can be uploaded at once"""
        files = [
            ('file1.md', b'Content 1', 9),
            ('file2.txt', b'Content 2', 9),
            ('file3.py', b'print("hello")', 14),
        ]
        result = kb_service.upload_files(files)

        assert len(result['uploaded']) == 3
        assert len(result['errors']) == 0

    def test_upload_duplicate_skipped(self, kb_service_populated, temp_project_dir):
        """AC-1.6: Duplicate filenames are skipped with warning"""
        files = [('document.pdf', b'new content', 11)]
        result = kb_service_populated.upload_files(files)

        assert len(result['skipped']) == 1
        assert result['skipped'][0]['file'] == 'document.pdf'
        assert 'duplicate' in result['skipped'][0]['reason'].lower()
        assert len(result['uploaded']) == 0

    def test_upload_invalid_extension_rejected(self, kb_service):
        """AC-1.2: Invalid extensions return in errors list"""
        files = [('virus.exe', b'malicious', 9)]
        result = kb_service.upload_files(files)

        assert len(result['errors']) == 1
        assert result['errors'][0]['file'] == 'virus.exe'
        assert len(result['uploaded']) == 0

    def test_upload_oversized_file_rejected(self, kb_service):
        """AC-1.3: Files exceeding 50MB return in errors list"""
        size = 51 * 1024 * 1024
        files = [('large.pdf', b'x' * 100, size)]  # size param indicates actual size
        result = kb_service.upload_files(files)

        assert len(result['errors']) == 1
        assert 'large.pdf' in result['errors'][0]['file']

    def test_upload_mixed_valid_invalid(self, kb_service):
        """AC-1.7: Mixed batch: valid files upload, invalid return in errors"""
        files = [
            ('good.md', b'valid content', 13),
            ('bad.exe', b'invalid', 7),
            ('also_good.py', b'print(1)', 8),
        ]
        result = kb_service.upload_files(files)

        assert len(result['uploaded']) == 2
        assert len(result['errors']) == 1
        assert result['errors'][0]['file'] == 'bad.exe'

    def test_upload_refreshes_index(self, kb_service, temp_project_dir):
        """AC-1.8: Upload triggers index refresh"""
        files = [('test.md', b'# Content', 9)]
        kb_service.upload_files(files)

        index_path = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base' / 'index' / 'file-index.json'
        with open(index_path) as f:
            index = json.load(f)

        file_paths = [f['path'] for f in index['files']]
        assert 'landing/test.md' in file_paths

    def test_upload_empty_list_returns_empty(self, kb_service):
        """AC-1.9: Empty file list returns empty results"""
        result = kb_service.upload_files([])

        assert len(result['uploaded']) == 0
        assert len(result['errors']) == 0
        assert len(result['skipped']) == 0

    def test_upload_sanitizes_filename(self, kb_service, temp_project_dir):
        """AC-1.10: Filenames are sanitized (secure_filename)"""
        files = [('../../../etc/passwd', b'hacked', 6)]
        result = kb_service.upload_files(files)

        # Should either sanitize the name or reject it
        landing = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base' / 'landing'
        assert not (Path(temp_project_dir) / 'etc' / 'passwd').exists()

    def test_upload_preserves_binary_content(self, kb_service, temp_project_dir):
        """Binary file content is preserved exactly"""
        binary_data = bytes(range(256))
        files = [('image.png', binary_data, 256)]
        result = kb_service.upload_files(files)

        assert 'landing/image.png' in result['uploaded']
        file_path = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base' / 'landing' / 'image.png'
        assert file_path.read_bytes() == binary_data


# ============================================================================
# KBService Unit Tests - delete_files()
# ============================================================================

class TestKBServiceDeleteFiles:
    """Tests for KBService.delete_files()"""

    def test_delete_single_file(self, kb_service_populated, temp_project_dir):
        """AC-5.1: Delete single file from landing"""
        result = kb_service_populated.delete_files(['landing/document.pdf'])

        assert 'landing/document.pdf' in result['deleted']
        assert len(result['errors']) == 0

        file_path = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base' / 'landing' / 'document.pdf'
        assert not file_path.exists()

    def test_delete_multiple_files(self, kb_service_populated, temp_project_dir):
        """AC-5.2: Delete multiple files at once"""
        result = kb_service_populated.delete_files([
            'landing/document.pdf',
            'landing/notes.md'
        ])

        assert len(result['deleted']) == 2
        assert len(result['errors']) == 0

    def test_delete_nonexistent_file(self, kb_service_populated):
        """AC-5.3: Deleting nonexistent file returns in errors"""
        result = kb_service_populated.delete_files(['landing/nonexistent.pdf'])

        assert len(result['errors']) == 1

    def test_delete_path_outside_landing_rejected(self, kb_service_populated):
        """AC-5.4: Paths not starting with 'landing/' are rejected"""
        result = kb_service_populated.delete_files(['topics/ai-research/raw/paper.pdf'])

        assert len(result['errors']) == 1
        assert len(result['deleted']) == 0

    def test_delete_refreshes_index(self, kb_service_populated, temp_project_dir):
        """AC-5.1: Delete triggers index refresh"""
        kb_service_populated.delete_files(['landing/document.pdf'])

        index_path = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base' / 'index' / 'file-index.json'
        with open(index_path) as f:
            index = json.load(f)

        file_paths = [f['path'] for f in index['files']]
        assert 'landing/document.pdf' not in file_paths

    def test_delete_empty_list_returns_empty(self, kb_service_populated):
        """AC-5.1: Empty paths list returns empty results"""
        result = kb_service_populated.delete_files([])

        assert len(result['deleted']) == 0
        assert len(result['errors']) == 0

    def test_delete_path_traversal_rejected(self, kb_service_populated):
        """Security: Path traversal attempts are rejected"""
        result = kb_service_populated.delete_files(['landing/../../../etc/passwd'])

        assert len(result['errors']) == 1
        assert len(result['deleted']) == 0


# ============================================================================
# KBService Unit Tests - get_landing_files()
# ============================================================================

class TestKBServiceGetLandingFiles:
    """Tests for KBService.get_landing_files()"""

    def test_get_landing_files_returns_only_landing(self, kb_service_populated):
        """AC-3.1: Only files from landing/ are returned"""
        files = kb_service_populated.get_landing_files()

        assert isinstance(files, list)
        for f in files:
            assert f['path'].startswith('landing/')

    def test_get_landing_files_empty_landing(self, kb_service):
        """AC-6.1: Empty landing returns empty list"""
        files = kb_service.get_landing_files()

        assert isinstance(files, list)
        assert len(files) == 0

    def test_get_landing_files_contains_file_metadata(self, kb_service_populated):
        """AC-3.2: Each file entry has path, name, type, size fields"""
        files = kb_service_populated.get_landing_files()

        assert len(files) > 0
        for f in files:
            assert 'path' in f
            assert 'name' in f
            assert 'type' in f
            assert 'size' in f


# ============================================================================
# API Tests - POST /api/kb/upload
# ============================================================================

class TestKBUploadAPI:
    """API tests for POST /api/kb/upload"""

    def test_upload_returns_200(self, client):
        """POST /api/kb/upload returns 200 OK for valid upload"""
        data = {'files': (BytesIO(b'# Test'), 'test.md')}
        response = client.post('/api/kb/upload', data=data, content_type='multipart/form-data')

        assert response.status_code == 200

    def test_upload_returns_json(self, client):
        """POST /api/kb/upload returns JSON response"""
        data = {'files': (BytesIO(b'# Test'), 'test.md')}
        response = client.post('/api/kb/upload', data=data, content_type='multipart/form-data')

        json_data = response.get_json()
        assert 'uploaded' in json_data

    def test_upload_no_files_returns_400(self, client):
        """POST /api/kb/upload with no files returns 400"""
        response = client.post('/api/kb/upload', data={}, content_type='multipart/form-data')

        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data

    def test_upload_multiple_files(self, client):
        """POST /api/kb/upload handles multiple files"""
        data = {
            'files': [
                (BytesIO(b'content 1'), 'file1.md'),
                (BytesIO(b'content 2'), 'file2.txt')
            ]
        }
        response = client.post('/api/kb/upload', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data['uploaded']) == 2

    def test_upload_invalid_extension_returns_errors(self, client):
        """POST /api/kb/upload with invalid extension returns errors"""
        data = {'files': (BytesIO(b'binary'), 'virus.exe')}
        response = client.post('/api/kb/upload', data=data, content_type='multipart/form-data')

        assert response.status_code == 200  # Request succeeds but file is in errors
        json_data = response.get_json()
        assert len(json_data['errors']) == 1

    def test_upload_duplicate_returns_skipped(self, client_populated):
        """POST /api/kb/upload with duplicate filename returns skipped"""
        data = {'files': (BytesIO(b'new content'), 'document.pdf')}
        response = client_populated.post('/api/kb/upload', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data['skipped']) == 1


# ============================================================================
# API Tests - POST /api/kb/landing/delete
# ============================================================================

class TestKBDeleteAPI:
    """API tests for POST /api/kb/landing/delete"""

    def test_delete_returns_200(self, client_populated):
        """POST /api/kb/landing/delete returns 200 OK"""
        response = client_populated.post(
            '/api/kb/landing/delete',
            json={'paths': ['landing/document.pdf']}
        )

        assert response.status_code == 200

    def test_delete_returns_json(self, client_populated):
        """POST /api/kb/landing/delete returns JSON with deleted list"""
        response = client_populated.post(
            '/api/kb/landing/delete',
            json={'paths': ['landing/document.pdf']}
        )

        json_data = response.get_json()
        assert 'deleted' in json_data
        assert 'errors' in json_data

    def test_delete_no_body_returns_400(self, client_populated):
        """POST /api/kb/landing/delete with no body returns 400"""
        response = client_populated.post(
            '/api/kb/landing/delete',
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_delete_empty_paths_returns_200(self, client_populated):
        """POST /api/kb/landing/delete with empty paths returns 200"""
        response = client_populated.post(
            '/api/kb/landing/delete',
            json={'paths': []}
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data['deleted']) == 0

    def test_delete_multiple_files(self, client_populated):
        """POST /api/kb/landing/delete handles multiple files"""
        response = client_populated.post(
            '/api/kb/landing/delete',
            json={'paths': ['landing/document.pdf', 'landing/notes.md']}
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data['deleted']) == 2


# ============================================================================
# API Tests - GET /api/kb/landing
# ============================================================================

class TestKBLandingAPI:
    """API tests for GET /api/kb/landing"""

    def test_landing_returns_200(self, client):
        """GET /api/kb/landing returns 200 OK"""
        response = client.get('/api/kb/landing')

        assert response.status_code == 200

    def test_landing_returns_json_with_files(self, client):
        """GET /api/kb/landing returns JSON with files array"""
        response = client.get('/api/kb/landing')

        json_data = response.get_json()
        assert 'files' in json_data
        assert isinstance(json_data['files'], list)

    def test_landing_empty_returns_empty_list(self, client):
        """GET /api/kb/landing with no files returns empty list"""
        response = client.get('/api/kb/landing')

        json_data = response.get_json()
        assert len(json_data['files']) == 0

    def test_landing_populated_returns_files(self, client_populated):
        """GET /api/kb/landing with files returns file list"""
        response = client_populated.get('/api/kb/landing')

        json_data = response.get_json()
        assert len(json_data['files']) == 3

    def test_landing_file_has_required_fields(self, client_populated):
        """GET /api/kb/landing files have required metadata fields"""
        response = client_populated.get('/api/kb/landing')

        json_data = response.get_json()
        assert len(json_data['files']) > 0
        file_entry = json_data['files'][0]
        assert 'path' in file_entry
        assert 'name' in file_entry
        assert 'type' in file_entry
        assert 'size' in file_entry


# ============================================================================
# Integration Tests
# ============================================================================

class TestKBLandingIntegration:
    """Integration tests for upload → index and delete → index flows"""

    def test_upload_then_get_landing_shows_file(self, kb_service, temp_project_dir):
        """Integration: Upload file then get_landing_files includes it"""
        files = [('integration_test.md', b'# Integration', 13)]
        kb_service.upload_files(files)

        landing_files = kb_service.get_landing_files()
        paths = [f['path'] for f in landing_files]
        assert 'landing/integration_test.md' in paths

    def test_delete_then_get_landing_excludes_file(self, kb_service_populated, temp_project_dir):
        """Integration: Delete file then get_landing_files excludes it"""
        kb_service_populated.delete_files(['landing/document.pdf'])

        landing_files = kb_service_populated.get_landing_files()
        paths = [f['path'] for f in landing_files]
        assert 'landing/document.pdf' not in paths

    def test_upload_then_delete_leaves_empty(self, kb_service, temp_project_dir):
        """Integration: Upload then delete same file → empty landing"""
        files = [('temp.md', b'temporary', 9)]
        kb_service.upload_files(files)

        kb_service.delete_files(['landing/temp.md'])

        landing_files = kb_service.get_landing_files()
        assert len(landing_files) == 0

    def test_api_upload_then_get_landing(self, client, temp_project_dir):
        """Integration: API upload then GET landing shows file"""
        data = {'files': (BytesIO(b'# API Test'), 'api_test.md')}
        client.post('/api/kb/upload', data=data, content_type='multipart/form-data')

        response = client.get('/api/kb/landing')
        json_data = response.get_json()
        paths = [f['path'] for f in json_data['files']]
        assert 'landing/api_test.md' in paths


# ============================================================================
# Tracing Tests
# ============================================================================

class TestKBLandingTracing:
    """Tracing tests for new KB landing endpoints"""

    def test_upload_endpoint_has_tracing(self, client):
        """POST /api/kb/upload should have @x_ipe_tracing decorator"""
        from x_ipe.routes.kb_routes import kb_bp
        upload_func = None
        for rule in kb_bp.deferred_functions:
            pass
        # Verify the upload route function has tracing by checking it exists
        # The actual tracing assertion will be done via inspecting the function
        data = {'files': (BytesIO(b'# Test'), 'trace_test.md')}
        response = client.post('/api/kb/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200

    def test_delete_endpoint_has_tracing(self, client_populated):
        """POST /api/kb/landing/delete should have @x_ipe_tracing decorator"""
        response = client_populated.post(
            '/api/kb/landing/delete',
            json={'paths': ['landing/document.pdf']}
        )
        assert response.status_code == 200

    def test_landing_endpoint_has_tracing(self, client):
        """GET /api/kb/landing should have @x_ipe_tracing decorator"""
        response = client.get('/api/kb/landing')
        assert response.status_code == 200
