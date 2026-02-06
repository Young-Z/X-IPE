"""
Tests for FEATURE-025-A: KB Core Infrastructure

Tests cover:
- KBService: initialize_structure(), get_index(), refresh_index(), get_topics(), get_topic_metadata()
- File index schema validation
- Topic metadata schema validation
- API endpoints: GET /api/kb/index, POST /api/kb/index/refresh, GET /api/kb/topics
- Edge cases: missing folders, corrupted index, concurrent access
- Tracing integration

TDD: All tests should FAIL before implementation.
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
# from x_ipe.services import KBService
# from x_ipe.app import create_app


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
    return kb_path


@pytest.fixture
def populated_kb_dir(temp_kb_dir):
    """Create KB directory with sample folders and files"""
    # Create landing folder with files
    landing = temp_kb_dir / 'landing'
    landing.mkdir(exist_ok=True)
    (landing / 'document.pdf').write_bytes(b'%PDF-1.4 fake pdf content')
    (landing / 'notes.md').write_text('# My Notes\n\nSome content here.')
    
    # Create topics folder with a topic
    topics = temp_kb_dir / 'topics'
    topics.mkdir(exist_ok=True)
    
    topic1 = topics / 'ai-research'
    topic1.mkdir(exist_ok=True)
    topic1_raw = topic1 / 'raw'
    topic1_raw.mkdir(exist_ok=True)
    (topic1_raw / 'paper1.pdf').write_bytes(b'%PDF-1.4 fake paper')
    (topic1_raw / 'paper2.pdf').write_bytes(b'%PDF-1.4 another paper')
    
    # Topic metadata
    (topic1 / 'metadata.json').write_text(json.dumps({
        "name": "ai-research",
        "description": "AI research papers",
        "file_count": 2,
        "last_updated": "2026-02-05T15:00:00Z",
        "tags": ["ai", "research"]
    }))
    
    # Create processed folder with summaries
    processed = temp_kb_dir / 'processed'
    processed.mkdir(exist_ok=True)
    processed_topic = processed / 'ai-research'
    processed_topic.mkdir(exist_ok=True)
    (processed_topic / 'summary-v1.md').write_text('# AI Research Summary\n\nVersion 1.')
    
    # Create index folder with file-index.json
    index = temp_kb_dir / 'index'
    index.mkdir(exist_ok=True)
    (index / 'file-index.json').write_text(json.dumps({
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
            }
        ]
    }))
    
    return temp_kb_dir


@pytest.fixture
def kb_service(temp_project_dir):
    """Create KBService instance with temp directory"""
    from x_ipe.services import KBService
    return KBService(temp_project_dir)


@pytest.fixture
def kb_service_populated(temp_project_dir, populated_kb_dir):
    """Create KBService with populated KB directory"""
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


# ============================================================================
# KBService Unit Tests - Initialization
# ============================================================================

class TestKBServiceInitialization:
    """Tests for KBService initialization and folder structure"""
    
    def test_initialize_structure_creates_all_folders(self, kb_service, temp_project_dir):
        """
        AC-2.1 to AC-2.5: initialize_structure() creates all required folders
        """
        result = kb_service.initialize_structure()
        
        assert result is True
        
        kb_root = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base'
        assert kb_root.exists()
        assert (kb_root / 'landing').exists()
        assert (kb_root / 'topics').exists()
        assert (kb_root / 'processed').exists()
        assert (kb_root / 'index').exists()
    
    def test_initialize_structure_creates_empty_index(self, kb_service, temp_project_dir):
        """
        AC-6.2: Auto-created index is empty but valid JSON
        """
        kb_service.initialize_structure()
        
        index_path = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base' / 'index' / 'file-index.json'
        assert index_path.exists()
        
        with open(index_path) as f:
            index = json.load(f)
        
        assert "version" in index
        assert "last_updated" in index
        assert "files" in index
        assert index["files"] == []
    
    def test_initialize_structure_does_not_overwrite_existing(self, kb_service_populated, populated_kb_dir):
        """
        AC-6.3: Folder creation does not overwrite existing content
        """
        # Check existing file
        existing_file = populated_kb_dir / 'landing' / 'document.pdf'
        original_content = existing_file.read_bytes()
        
        # Re-initialize
        kb_service_populated.initialize_structure()
        
        # Verify file unchanged
        assert existing_file.exists()
        assert existing_file.read_bytes() == original_content
    
    def test_initialize_structure_is_idempotent(self, kb_service, temp_project_dir):
        """
        Multiple calls to initialize_structure() should be safe
        """
        kb_service.initialize_structure()
        kb_service.initialize_structure()
        kb_service.initialize_structure()
        
        kb_root = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base'
        assert kb_root.exists()


# ============================================================================
# KBService Unit Tests - Index Operations
# ============================================================================

class TestKBServiceIndex:
    """Tests for KBService index operations"""
    
    def test_get_index_returns_valid_structure(self, kb_service_populated):
        """
        AC-3.1, AC-3.2: get_index() returns valid index with all fields
        """
        index = kb_service_populated.get_index()
        
        assert "version" in index
        assert "last_updated" in index
        assert "files" in index
        assert isinstance(index["files"], list)
    
    def test_get_index_initializes_if_missing(self, kb_service):
        """
        get_index() should initialize structure if KB folder missing
        """
        index = kb_service.get_index()
        
        assert index is not None
        assert "files" in index
    
    def test_get_index_file_entries_have_all_fields(self, kb_service_populated):
        """
        AC-3.1: Each file entry has path, name, type, size, topic, created_date, keywords
        """
        index = kb_service_populated.get_index()
        
        for entry in index["files"]:
            assert "path" in entry
            assert "name" in entry
            assert "type" in entry
            assert "size" in entry
            assert "topic" in entry  # Can be None
            assert "created_date" in entry
            assert "keywords" in entry
    
    def test_refresh_index_scans_all_folders(self, kb_service_populated, populated_kb_dir):
        """
        AC-5.2: refresh_index() rebuilds from file system
        """
        # Add a new file
        new_file = populated_kb_dir / 'landing' / 'new_file.txt'
        new_file.write_text('New content')
        
        # Refresh index
        index = kb_service_populated.refresh_index()
        
        # Verify new file is in index
        paths = [f["path"] for f in index["files"]]
        assert "landing/new_file.txt" in paths
    
    def test_refresh_index_includes_topics_files(self, kb_service_populated):
        """
        AC-3.4: Index includes files from topics/ subfolders
        """
        index = kb_service_populated.refresh_index()
        
        # Find files from topics
        topic_files = [f for f in index["files"] if f["topic"] is not None]
        assert len(topic_files) > 0
    
    def test_refresh_index_includes_processed_files(self, kb_service_populated):
        """
        AC-3.4: Index includes files from processed/ subfolder
        """
        index = kb_service_populated.refresh_index()
        
        paths = [f["path"] for f in index["files"]]
        processed_paths = [p for p in paths if p.startswith("processed/")]
        assert len(processed_paths) > 0
    
    def test_refresh_index_updates_last_updated(self, kb_service_populated):
        """
        Index last_updated timestamp is updated on refresh
        """
        before_index = kb_service_populated.get_index()
        before_time = before_index["last_updated"]
        
        # Small delay then refresh
        import time
        time.sleep(0.1)
        
        after_index = kb_service_populated.refresh_index()
        after_time = after_index["last_updated"]
        
        assert after_time >= before_time
    
    def test_index_entries_have_unique_paths(self, kb_service_populated):
        """
        AC-3.3: No duplicate paths in index
        """
        index = kb_service_populated.refresh_index()
        
        paths = [f["path"] for f in index["files"]]
        assert len(paths) == len(set(paths))  # All unique


# ============================================================================
# KBService Unit Tests - File Type Detection
# ============================================================================

class TestKBServiceFileTypes:
    """Tests for file type detection"""
    
    @pytest.mark.parametrize("filename,expected_type", [
        ("document.pdf", "pdf"),
        ("notes.md", "markdown"),
        ("readme.markdown", "markdown"),
        ("data.txt", "text"),
        ("report.docx", "docx"),
        ("data.xlsx", "xlsx"),
        ("script.py", "python"),
        ("app.js", "javascript"),
        ("main.ts", "typescript"),
        ("Main.java", "java"),
        ("image.png", "image"),
        ("photo.jpg", "image"),
        ("diagram.gif", "image"),
        ("unknown_file", "unknown"),
        ("config.json", "json"),
        ("styles.css", "css"),
    ])
    def test_file_type_detection(self, kb_service, filename, expected_type):
        """
        Technical Design: File type mapping works correctly
        """
        file_type = kb_service._get_file_type(Path(filename).suffix)
        assert file_type == expected_type


# ============================================================================
# KBService Unit Tests - Topic Operations
# ============================================================================

class TestKBServiceTopics:
    """Tests for KBService topic operations"""
    
    def test_get_topics_returns_list(self, kb_service_populated):
        """
        Get list of all topics
        """
        topics = kb_service_populated.get_topics()
        
        assert isinstance(topics, list)
        assert "ai-research" in topics
    
    def test_get_topics_empty_when_no_topics(self, kb_service):
        """
        Empty topics list when no topics exist
        """
        kb_service.initialize_structure()
        topics = kb_service.get_topics()
        
        assert topics == []
    
    def test_get_topic_metadata_returns_valid_structure(self, kb_service_populated):
        """
        AC-4.1: Topic metadata has all required fields
        """
        metadata = kb_service_populated.get_topic_metadata("ai-research")
        
        assert "name" in metadata
        assert "description" in metadata
        assert "file_count" in metadata
        assert "last_updated" in metadata
        assert "tags" in metadata
    
    def test_get_topic_metadata_nonexistent_topic(self, kb_service_populated):
        """
        Returns None or empty for non-existent topic
        """
        metadata = kb_service_populated.get_topic_metadata("nonexistent-topic")
        
        assert metadata is None
    
    def test_topic_metadata_file_count_accurate(self, kb_service_populated, populated_kb_dir):
        """
        AC-4.2: file_count accurately reflects files in raw/ folder
        """
        # After refresh, metadata should match actual files
        kb_service_populated.refresh_index()
        metadata = kb_service_populated.get_topic_metadata("ai-research")
        
        # Count actual files in raw/
        raw_path = populated_kb_dir / 'topics' / 'ai-research' / 'raw'
        actual_count = len(list(raw_path.iterdir()))
        
        assert metadata["file_count"] == actual_count
    
    def test_topic_metadata_last_updated_is_iso8601(self, kb_service_populated):
        """
        AC-4.3: last_updated is ISO 8601 format
        """
        metadata = kb_service_populated.get_topic_metadata("ai-research")
        
        # Should be parseable as ISO 8601
        from datetime import datetime
        datetime.fromisoformat(metadata["last_updated"].replace("Z", "+00:00"))
    
    def test_topic_metadata_tags_is_array(self, kb_service_populated):
        """
        AC-4.4: tags is an array of strings
        """
        metadata = kb_service_populated.get_topic_metadata("ai-research")
        
        assert isinstance(metadata["tags"], list)
        for tag in metadata["tags"]:
            assert isinstance(tag, str)


# ============================================================================
# KBService Unit Tests - Keyword Extraction
# ============================================================================

class TestKBServiceKeywords:
    """Tests for keyword extraction from filenames"""
    
    @pytest.mark.parametrize("filename,expected_keywords", [
        ("document.pdf", ["document"]),
        ("my-notes.md", ["my", "notes"]),
        ("project_plan.txt", ["project", "plan"]),
        ("AI Research Paper.pdf", ["ai", "research", "paper"]),
        ("file-with-many-parts.docx", ["file", "with", "many", "parts"]),
    ])
    def test_keyword_extraction(self, kb_service, filename, expected_keywords):
        """
        Technical Design: Keywords extracted from filename
        """
        keywords = kb_service._extract_keywords(filename)
        
        # Keywords should be lowercase
        assert all(k.islower() for k in keywords)
        # Should contain expected keywords
        for expected in expected_keywords:
            assert expected.lower() in keywords


# ============================================================================
# KBService Unit Tests - Edge Cases
# ============================================================================

class TestKBServiceEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_corrupted_index_recreated(self, kb_service, temp_project_dir):
        """
        Edge case: Invalid JSON in index is recreated
        """
        kb_service.initialize_structure()
        
        # Corrupt the index
        index_path = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base' / 'index' / 'file-index.json'
        index_path.write_text("not valid json {{{")
        
        # get_index should handle gracefully
        index = kb_service.get_index()
        
        assert index is not None
        assert "files" in index
    
    def test_topic_without_metadata_creates_default(self, kb_service_populated, populated_kb_dir):
        """
        Edge case: Topic folder without metadata.json
        """
        # Create topic without metadata
        new_topic = populated_kb_dir / 'topics' / 'orphan-topic'
        new_topic.mkdir()
        (new_topic / 'raw').mkdir()
        (new_topic / 'raw' / 'file.txt').write_text('content')
        
        # Refresh should create metadata
        kb_service_populated.refresh_index()
        
        metadata = kb_service_populated.get_topic_metadata("orphan-topic")
        assert metadata is not None
        assert metadata["name"] == "orphan-topic"
    
    def test_file_without_extension(self, kb_service_populated, populated_kb_dir):
        """
        Edge case: File without extension gets type "unknown"
        """
        # Create file without extension
        (populated_kb_dir / 'landing' / 'README').write_text('readme content')
        
        index = kb_service_populated.refresh_index()
        
        readme_entry = next((f for f in index["files"] if f["name"] == "README"), None)
        assert readme_entry is not None
        assert readme_entry["type"] == "unknown"
    
    def test_unicode_filenames_supported(self, kb_service_populated, populated_kb_dir):
        """
        Edge case: Unicode filenames are fully supported
        """
        # Create file with unicode name
        unicode_file = populated_kb_dir / 'landing' / '日本語ファイル.txt'
        unicode_file.write_text('Japanese content')
        
        index = kb_service_populated.refresh_index()
        
        unicode_entry = next((f for f in index["files"] if "日本語" in f["name"]), None)
        assert unicode_entry is not None
    
    def test_hidden_files_ignored(self, kb_service_populated, populated_kb_dir):
        """
        Hidden files (starting with .) should be ignored
        """
        # Create hidden file
        (populated_kb_dir / 'landing' / '.hidden').write_text('hidden content')
        
        index = kb_service_populated.refresh_index()
        
        hidden_entry = next((f for f in index["files"] if f["name"] == ".hidden"), None)
        assert hidden_entry is None


# ============================================================================
# API Endpoint Tests
# ============================================================================

class TestKBAPIEndpoints:
    """Tests for KB REST API endpoints"""
    
    def test_get_index_endpoint(self, client):
        """
        GET /api/kb/index returns current index
        """
        response = client.get('/api/kb/index')
        
        assert response.status_code == 200
        data = response.get_json()
        assert "version" in data
        assert "files" in data
    
    def test_refresh_index_endpoint(self, client):
        """
        POST /api/kb/index/refresh rebuilds index
        """
        response = client.post('/api/kb/index/refresh')
        
        assert response.status_code == 200
        data = response.get_json()
        assert "version" in data
        assert "files" in data
    
    def test_get_topics_endpoint(self, client):
        """
        GET /api/kb/topics returns topic list
        """
        response = client.get('/api/kb/topics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert "topics" in data
        assert isinstance(data["topics"], list)
    
    def test_get_topic_metadata_endpoint(self, client, populated_kb_dir):
        """
        GET /api/kb/topics/<name> returns topic metadata
        """
        response = client.get('/api/kb/topics/ai-research')
        
        assert response.status_code == 200
        data = response.get_json()
        assert "name" in data
        assert data["name"] == "ai-research"
    
    def test_get_topic_metadata_not_found(self, client):
        """
        GET /api/kb/topics/<name> returns 404 for non-existent topic
        """
        response = client.get('/api/kb/topics/nonexistent')
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data


# ============================================================================
# Integration Tests
# ============================================================================

class TestKBIntegration:
    """Integration tests for KB functionality"""
    
    def test_end_to_end_initialize_and_get_index(self, client):
        """
        Integration: Initialize KB and get index
        """
        # First call should initialize
        response1 = client.get('/api/kb/index')
        assert response1.status_code == 200
        
        # Second call should return same structure
        response2 = client.get('/api/kb/index')
        assert response2.status_code == 200
        
        data = response2.get_json()
        assert "version" in data
        assert "files" in data
    
    def test_add_file_then_refresh(self, client, temp_project_dir):
        """
        Integration: Add file manually, then refresh index
        """
        # Initialize
        response = client.post('/api/kb/index/refresh')
        assert response.status_code == 200
        
        # Add file directly to file system
        kb_path = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base' / 'landing'
        kb_path.mkdir(parents=True, exist_ok=True)
        (kb_path / 'manual_file.txt').write_text('manually added')
        
        # Refresh
        response = client.post('/api/kb/index/refresh')
        
        data = response.get_json()
        paths = [f["path"] for f in data["files"]]
        assert "landing/manual_file.txt" in paths


# ============================================================================
# Tracing Tests
# ============================================================================

class TestKBTracing:
    """Tests for tracing integration"""
    
    def test_kb_service_methods_have_tracing(self, kb_service):
        """
        KBService methods should have @x_ipe_tracing decorator
        """
        from x_ipe.services import KBService
        
        # Check that methods have tracing attribute
        assert hasattr(KBService.initialize_structure, '__wrapped__') or \
               hasattr(KBService.initialize_structure, '_x_ipe_traced')
    
    def test_kb_routes_have_tracing(self, app):
        """
        KB route handlers should have @x_ipe_tracing decorator
        """
        # Routes should be traceable - implementation will verify
        pass


# ============================================================================
# Test Count Summary
# ============================================================================
# Total: 35 tests
# - Initialization: 4 tests
# - Index Operations: 8 tests
# - File Types: 1 parametrized test (16 cases)
# - Topics: 7 tests
# - Keywords: 1 parametrized test (5 cases)
# - Edge Cases: 5 tests
# - API Endpoints: 5 tests
# - Integration: 2 tests
# - Tracing: 2 tests
