"""
Tests for CR-001: .docx/.msg File Content Preview

Covers:
- _convert_docx() helper: happy path + corrupted file
- _convert_msg() helper: happy path + error handling
- _sanitize_converted_html(): strips scripts/iframes/on* attributes
- GET /api/ideas/file: conversion route integration, 413 size guard, 415 fallback
"""
import json
import os
import pytest
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


# ============================================================================
# UNIT TESTS — Helper Functions
# ============================================================================

class TestConvertDocx:
    """Unit tests for _convert_docx()."""

    def test_convert_docx_returns_html(self, tmp_path):
        """AC-038-C.04a: .docx file returns rendered HTML content."""
        from x_ipe.routes.ideas_routes import _convert_docx
        mock_result = MagicMock()
        mock_result.value = '<h1>Hello</h1><p>World</p>'
        docx_file = tmp_path / 'test.docx'
        docx_file.write_bytes(b'PK\x03\x04dummy')  # minimal file so open() works
        with patch('mammoth.convert_to_html', return_value=mock_result) as mock_conv:
            result = _convert_docx(docx_file)
            assert '<h1>Hello</h1>' in result
            assert '<p>World</p>' in result
            mock_conv.assert_called_once()

    def test_convert_docx_corrupted_raises(self, tmp_path):
        """AC-038-C.04e: Corrupted .docx raises exception."""
        from x_ipe.routes.ideas_routes import _convert_docx
        bad_file = tmp_path / 'bad.docx'
        bad_file.write_bytes(b'not a real docx')
        with pytest.raises(Exception):
            _convert_docx(bad_file)


class TestConvertMsg:
    """Unit tests for _convert_msg()."""

    def test_convert_msg_returns_html_with_headers(self):
        """AC-038-C.04b: .msg file returns HTML with From/To/Subject/Body."""
        from x_ipe.routes.ideas_routes import _convert_msg
        mock_msg = MagicMock()
        mock_msg.sender = 'alice@example.com'
        mock_msg.to = 'bob@example.com'
        mock_msg.cc = 'carol@example.com'
        mock_msg.date = '2025-01-01'
        mock_msg.subject = 'Test Subject'
        mock_msg.htmlBody = None
        mock_msg.body = 'Hello, this is the body.'
        mock_msg.close = MagicMock()

        with patch('extract_msg.openMsg', return_value=mock_msg):
            result = _convert_msg('/fake/path.msg')

        assert 'alice@example.com' in result
        assert 'bob@example.com' in result
        assert 'carol@example.com' in result
        assert 'Test Subject' in result
        assert 'Hello, this is the body.' in result
        assert 'msg-headers' in result
        mock_msg.close.assert_called_once()

    def test_convert_msg_html_body_used_when_present(self):
        """AC-038-C.04g: .msg with HTML body uses htmlBody instead of plain text."""
        from x_ipe.routes.ideas_routes import _convert_msg
        mock_msg = MagicMock()
        mock_msg.sender = 'alice@example.com'
        mock_msg.to = 'bob@example.com'
        mock_msg.cc = ''
        mock_msg.date = '2025-01-01'
        mock_msg.subject = 'HTML Email'
        mock_msg.htmlBody = '<p>Rich <b>HTML</b> body</p>'
        mock_msg.body = 'Fallback plain text'
        mock_msg.close = MagicMock()

        with patch('extract_msg.openMsg', return_value=mock_msg):
            result = _convert_msg('/fake/path.msg')

        assert '<p>Rich <b>HTML</b> body</p>' in result
        assert 'Fallback plain text' not in result

    def test_convert_msg_closes_on_error(self):
        """AC-038-C.04e: .msg close() called even on error."""
        from x_ipe.routes.ideas_routes import _convert_msg
        mock_msg = MagicMock()
        mock_msg.sender = None
        mock_msg.to = None
        mock_msg.cc = None
        mock_msg.date = None
        mock_msg.subject = None
        mock_msg.htmlBody = None
        mock_msg.body = None
        mock_msg.close = MagicMock()

        with patch('extract_msg.openMsg', return_value=mock_msg):
            # Should not raise — None fields handled gracefully
            result = _convert_msg('/fake/path.msg')

        mock_msg.close.assert_called_once()
        assert 'msg-preview' in result


class TestSanitizeConvertedHtml:
    """Unit tests for _sanitize_converted_html()."""

    def test_strips_script_tags(self):
        """AC-038-C.04d: Removes <script> tags from converted HTML."""
        from x_ipe.routes.ideas_routes import _sanitize_converted_html
        html = '<p>Hello</p><script>alert("xss")</script><p>World</p>'
        result = _sanitize_converted_html(html)
        assert '<script>' not in result
        assert 'alert' not in result
        assert '<p>Hello</p>' in result
        assert '<p>World</p>' in result

    def test_strips_iframe_tags(self):
        """AC-038-C.04d: Removes <iframe> tags."""
        from x_ipe.routes.ideas_routes import _sanitize_converted_html
        html = '<div><iframe src="evil.com"></iframe></div>'
        result = _sanitize_converted_html(html)
        assert '<iframe' not in result

    def test_strips_on_event_attributes(self):
        """AC-038-C.04d: Removes on* event handler attributes."""
        from x_ipe.routes.ideas_routes import _sanitize_converted_html
        html = '<p onclick="alert(1)" onmouseover="hack()">Text</p>'
        result = _sanitize_converted_html(html)
        assert 'onclick' not in result
        assert 'onmouseover' not in result
        assert 'Text' in result

    def test_strips_object_embed_tags(self):
        """AC-038-C.04d: Removes <object> and <embed> tags."""
        from x_ipe.routes.ideas_routes import _sanitize_converted_html
        html = '<object data="x"></object><embed src="y"><p>Safe</p>'
        result = _sanitize_converted_html(html)
        assert '<object' not in result
        assert '<embed' not in result
        assert '<p>Safe</p>' in result

    def test_preserves_safe_html(self):
        """Safe HTML elements pass through unchanged."""
        from x_ipe.routes.ideas_routes import _sanitize_converted_html
        html = '<h1>Title</h1><p>Para</p><ul><li>Item</li></ul><table><tr><td>Cell</td></tr></table>'
        result = _sanitize_converted_html(html)
        assert '<h1>Title</h1>' in result
        assert '<p>Para</p>' in result
        assert '<li>Item</li>' in result


# ============================================================================
# UNIT TESTS — Constants
# ============================================================================

class TestConstants:
    """Verify CR-001 constants."""

    def test_convertible_extensions(self):
        from x_ipe.routes.ideas_routes import CONVERTIBLE_EXTENSIONS
        assert '.docx' in CONVERTIBLE_EXTENSIONS
        assert '.msg' in CONVERTIBLE_EXTENSIONS
        assert '.zip' not in CONVERTIBLE_EXTENSIONS

    def test_max_conversion_size(self):
        from x_ipe.routes.ideas_routes import MAX_CONVERSION_SIZE
        assert MAX_CONVERSION_SIZE == 10 * 1024 * 1024


# ============================================================================
# INTEGRATION TESTS — GET /api/ideas/file with conversion
# ============================================================================

class TestFileConversionRoute:
    """Integration tests for .docx/.msg conversion in get_idea_file()."""

    @pytest.fixture
    def temp_project_dir(self):
        temp_dir = tempfile.mkdtemp()
        ideas_path = Path(temp_dir) / 'x-ipe-docs' / 'ideas' / 'test-idea'
        ideas_path.mkdir(parents=True)
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def app_client(self, temp_project_dir):
        try:
            from src.app import create_app
            app = create_app({
                'PROJECT_ROOT': temp_project_dir,
                'TESTING': True,
                'SETTINGS_DB_PATH': os.path.join(temp_project_dir, 'test_settings.db')
            })
            with app.test_client() as client:
                yield client
        except ImportError:
            pytest.skip('App not importable yet')

    def _create_file(self, temp_project_dir, rel_path, content=b''):
        path = Path(temp_project_dir) / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_docx_returns_200_with_x_converted(self, temp_project_dir, app_client):
        """AC-038-C.04a: .docx returns 200 with X-Converted: true header."""
        self._create_file(temp_project_dir, 'x-ipe-docs/ideas/test-idea/doc.docx', b'dummy')
        with patch('x_ipe.routes.ideas_routes._convert_docx', return_value='<p>Converted</p>'):
            resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/doc.docx')
        assert resp.status_code == 200
        assert resp.headers.get('X-Converted') == 'true'
        assert 'text/html' in resp.content_type
        assert b'Converted' in resp.data

    def test_msg_returns_200_with_x_converted(self, temp_project_dir, app_client):
        """AC-038-C.04b: .msg returns 200 with X-Converted: true header."""
        self._create_file(temp_project_dir, 'x-ipe-docs/ideas/test-idea/email.msg', b'dummy')
        with patch('x_ipe.routes.ideas_routes._convert_msg', return_value='<div>Email</div>'):
            resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/email.msg')
        assert resp.status_code == 200
        assert resp.headers.get('X-Converted') == 'true'
        assert b'Email' in resp.data

    def test_oversized_file_returns_413(self, temp_project_dir, app_client):
        """AC-038-C.04c: File >10MB returns 413."""
        self._create_file(
            temp_project_dir,
            'x-ipe-docs/ideas/test-idea/big.docx',
            b'x' * (10 * 1024 * 1024 + 1)
        )
        resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/big.docx')
        assert resp.status_code == 413
        data = json.loads(resp.data)
        assert 'too large' in data['error'].lower()

    def test_corrupted_docx_returns_415(self, temp_project_dir, app_client):
        """AC-038-C.04e: Corrupted .docx returns 415."""
        self._create_file(temp_project_dir, 'x-ipe-docs/ideas/test-idea/bad.docx', b'corrupted')
        with patch('x_ipe.routes.ideas_routes._convert_docx', side_effect=Exception('parse error')):
            resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/bad.docx')
        assert resp.status_code == 415

    def test_non_convertible_binary_still_returns_415(self, temp_project_dir, app_client):
        """AC-038-C.04h: .zip and other binaries still return 415 unchanged."""
        # Use bytes that are invalid UTF-8 so the text decode fails
        self._create_file(
            temp_project_dir,
            'x-ipe-docs/ideas/test-idea/archive.zip',
            b'\x80\x81\x82\xff\xfe\xfd' * 100
        )
        resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/archive.zip')
        assert resp.status_code == 415

    def test_text_file_still_works(self, temp_project_dir, app_client):
        """Regression: plain text files still return 200 text/plain."""
        self._create_file(
            temp_project_dir,
            'x-ipe-docs/ideas/test-idea/notes.md',
            b'# Hello\n\nWorld'
        )
        resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/notes.md')
        assert resp.status_code == 200
        assert b'# Hello' in resp.data

    def test_html_sanitization_applied(self, temp_project_dir, app_client):
        """AC-038-C.04d: Converted HTML is sanitized before returning."""
        self._create_file(temp_project_dir, 'x-ipe-docs/ideas/test-idea/evil.docx', b'dummy')
        dirty_html = '<p>Good</p><script>alert(1)</script>'
        with patch('x_ipe.routes.ideas_routes._convert_docx', return_value=dirty_html):
            resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/evil.docx')
        assert resp.status_code == 200
        assert b'<script>' not in resp.data
        assert b'Good' in resp.data
