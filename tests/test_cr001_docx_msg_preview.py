"""
Tests for CR-001: .docx/.msg File Content Preview

Covers:
- convert_docx() helper: happy path + corrupted file
- convert_msg() helper: happy path + error handling
- sanitize_converted_html(): strips scripts/iframes/on* attributes
- GET /api/ideas/file: conversion route integration, 413 size guard, 415 fallback
"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
from zipfile import ZIP_DEFLATED, ZipFile

import pytest


# Deliberately invalid bytes are ONLY filesystem placeholders behind converter
# mocks. They are not valid DOCX/MSG fixtures or evidence of parser integration.
MOCK_ONLY_BYTES = b'invalid document: converter must be mocked'
DIRTY_HTML = (
    '<p ONCLICK="alert(1)" onmouseover="hack()">Good</p>'
    '<SCRIPT>alert(2)</SCRIPT><iframe src="https://invalid.example"></iframe>'
    '<object data="x"></object><embed src="y">'
)
SAFE_HTML = '<p>Good</p>'

# NFR-038-C.5: validate parsed attributes, not just a literal prefix in output.
UNSAFE_URIS = [
    'javascript:alert(1)', 'JaVaScRiPt:alert(1)',
    ' &#x09;jav&#x61;script&#58;alert(1)',
    'java\tscript:alert(1)', 'java\nscript:alert(1)',
    '\x00javascript:alert(1)', 'java\x01script:alert(1)',
    'javascript&colon;alert(1)', 'javascript&amp;colon;alert(1)',
    'java%73cript%3Aalert(1)', 'java%2573cript%253Aalert(1)',
    '%26%23x6a%3Bavascript%3Aalert(1)',
    'vbscript:msgbox(1)', 'Vb%09ScRiPt:msgbox(1)',
    'data:text/html,<script>alert(1)</script>',
    'DATA:application/xhtml+xml,<html/>',
    'data:image/svg+xml,<svg onload=alert(1)>',
    'data:image/svg+xml;base64,PHN2ZyBvbmxvYWQ9ImFsZXJ0KDEpIj48L3N2Zz4=',
    'data:image/png;base64,PHN2ZyBvbmxvYWQ9ImFsZXJ0KDEpIj48L3N2Zz4=',
    'file:///etc/passwd', 'unknown:payload',
]
PNG_URI = (
    'data:image/png;base64,'
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='
)
SAFE_LINKS = [
    'https://example.com/doc?q=one&other=two', 'HTTP://example.com/doc',
    'mailto:alice@example.com', 'tel:+123456789',
    '/docs/guide', '../guide.html', 'guide.html', '#heading',
    '//example.com/guide', 'guide%20with%20spaces.html',
    '/guide?next=javascript:example',
]


@pytest.fixture
def minimal_docx(tmp_path):
    """A real ZIP/OOXML package; conversion is performed by installed mammoth."""
    path = tmp_path / 'minimal.docx'
    parts = {
        '[Content_Types].xml': (
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            '</Types>'
        ),
        '_rels/.rels': (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>'
        ),
        'word/_rels/document.xml.rels': (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            '</Relationships>'
        ),
        'word/styles.xml': (
            '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/></w:style>'
            '</w:styles>'
        ),
        'word/document.xml': (
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Audit heading</w:t></w:r></w:p>'
            '<w:p><w:r><w:t xml:space="preserve">Hello </w:t></w:r>'
            '<w:r><w:rPr><w:b/></w:rPr><w:t>bold</w:t></w:r>'
            '<w:r><w:t xml:space="preserve"> and </w:t></w:r>'
            '<w:r><w:rPr><w:i/></w:rPr><w:t>italic</w:t></w:r>'
            '<w:r><w:t>.</w:t></w:r></w:p>'
            '<w:sectPr/></w:body></w:document>'
        ),
    }
    with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    return path


REAL_DOCX_HTML = (
    '<h1>Audit heading</h1>'
    '<p>Hello <strong>bold</strong> and <em>italic</em>.</p>'
)


# ============================================================================
# UNIT TESTS — Helper Functions
# ============================================================================

class TestConvertDocx:
    """Unit tests for convert_docx()."""

    def test_convert_docx_returns_html(self, minimal_docx):
        """Unit boundary: an opened binary stream reaches mammoth, not a parser test."""
        from x_ipe.services.conversion_utils import convert_docx
        mock_result = MagicMock()
        mock_result.value = '<h1>Hello</h1><p>World</p>'

        def convert_stream(stream):
            assert stream.name == str(minimal_docx)
            assert stream.read() == minimal_docx.read_bytes()
            return mock_result

        with patch('mammoth.convert_to_html', side_effect=convert_stream) as mock_conv:
            result = convert_docx(minimal_docx)
        assert result == '<h1>Hello</h1><p>World</p>'
        mock_conv.assert_called_once()
        assert mock_conv.call_args.args[0].closed

    def test_real_docx_conversion(self, minimal_docx):
        """AC-038-C.04a/c: real mammoth converts actual OOXML, no converter mock."""
        from x_ipe.services.conversion_utils import convert_docx
        assert convert_docx(minimal_docx) == REAL_DOCX_HTML

    def test_convert_docx_corrupted_raises(self, tmp_path):
        """AC-038-C.04e: Corrupted .docx raises exception."""
        from x_ipe.services.conversion_utils import convert_docx
        bad_file = tmp_path / 'bad.docx'
        bad_file.write_bytes(b'not a real docx')
        with pytest.raises(Exception):
            convert_docx(bad_file)


class TestConvertMsg:
    """Unit tests for convert_msg()."""

    def test_convert_msg_returns_html_with_headers(self):
        """AC-038-C.04b: .msg file returns HTML with From/To/Subject/Body."""
        from x_ipe.services.conversion_utils import convert_msg
        mock_msg = MagicMock()
        mock_msg.sender = 'alice@example.com'
        mock_msg.to = 'bob@example.com'
        mock_msg.cc = 'carol@example.com'
        mock_msg.date = '2025-01-01'
        mock_msg.subject = 'Test Subject'
        mock_msg.htmlBody = None
        mock_msg.body = 'Hello, this is the body.'
        mock_msg.close = MagicMock()

        with patch('extract_msg.openMsg', return_value=mock_msg) as mock_open:
            result = convert_msg('/fake/path.msg')

        mock_open.assert_called_once_with('/fake/path.msg')
        assert 'alice@example.com' in result
        assert 'bob@example.com' in result
        assert 'carol@example.com' in result
        assert 'Test Subject' in result
        assert 'Hello, this is the body.' in result
        assert 'msg-headers' in result
        mock_msg.close.assert_called_once()

    def test_convert_msg_html_body_used_when_present(self):
        """AC-038-C.04b edge case: .msg with HTML body uses htmlBody instead of plain text."""
        from x_ipe.services.conversion_utils import convert_msg
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
            result = convert_msg('/fake/path.msg')

        assert '<p>Rich <b>HTML</b> body</p>' in result
        assert 'Fallback plain text' not in result

    def test_convert_msg_closes_on_error(self):
        """Empty parser fields are tolerated; this is not an exception-path test."""
        from x_ipe.services.conversion_utils import convert_msg
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
            result = convert_msg('/fake/path.msg')

        mock_msg.close.assert_called_once()
        assert 'msg-preview' in result

    @pytest.mark.parametrize('binding', ['shared', 'route'])
    def test_convert_msg_closes_on_actual_error(self, binding):
        """AC-038-C.04e: both implementations close after metadata access fails."""
        from x_ipe.routes import ideas_routes
        from x_ipe.services import conversion_utils
        converter = (conversion_utils.convert_msg if binding == 'shared'
                     else ideas_routes._convert_msg)
        mock_msg = MagicMock()
        type(mock_msg).sender = PropertyMock(side_effect=ValueError('metadata error'))
        with patch('extract_msg.openMsg', return_value=mock_msg) as mock_open:
            with pytest.raises(ValueError, match='metadata error'):
                converter('/fake/path.msg')
        mock_open.assert_called_once_with('/fake/path.msg')
        mock_msg.close.assert_called_once_with()


class TestSanitizeConvertedHtml:
    """Unit tests for sanitize_converted_html()."""

    @pytest.mark.parametrize('binding', ['shared', 'route'])
    @pytest.mark.parametrize('uri', UNSAFE_URIS)
    @pytest.mark.parametrize('element,attribute', [
        ('a', 'href'), ('img', 'src'), ('form', 'action'),
        ('button', 'formaction'), ('video', 'poster'), ('use', 'xlink:href'),
    ])
    def test_unsafe_uri_attributes_removed(self, binding, uri, element, attribute):
        from bs4 import BeautifulSoup
        from x_ipe.routes import ideas_routes
        from x_ipe.services import conversion_utils
        sanitizer = (conversion_utils.sanitize_converted_html if binding == 'shared'
                     else ideas_routes._sanitize_converted_html)
        dirty = f'<p>Good</p><{element} {attribute}="{uri}">Open</{element}>'
        soup = BeautifulSoup(sanitizer(dirty), 'html.parser')
        assert soup.p.get_text() == 'Good'
        assert attribute not in soup.find(element).attrs

    @pytest.mark.parametrize('binding', ['shared', 'route'])
    @pytest.mark.parametrize('uri', SAFE_LINKS)
    def test_safe_links_preserved(self, binding, uri):
        import html
        from bs4 import BeautifulSoup
        from x_ipe.routes import ideas_routes
        from x_ipe.services import conversion_utils
        sanitizer = (conversion_utils.sanitize_converted_html if binding == 'shared'
                     else ideas_routes._sanitize_converted_html)
        soup = BeautifulSoup(sanitizer(f'<a href="{html.escape(uri)}">Open</a>'), 'html.parser')
        assert soup.a['href'] == uri
        assert soup.a.get_text() == 'Open'

    @pytest.mark.parametrize('binding', ['shared', 'route'])
    @pytest.mark.parametrize('uri', [
        'https://example.com/image.png', '/images/icon.svg', '../image.jpg',
        'cid:email-image@example.com', PNG_URI,
    ])
    def test_safe_images_preserved(self, binding, uri):
        from bs4 import BeautifulSoup
        from x_ipe.routes import ideas_routes
        from x_ipe.services import conversion_utils
        sanitizer = (conversion_utils.sanitize_converted_html if binding == 'shared'
                     else ideas_routes._sanitize_converted_html)
        soup = BeautifulSoup(sanitizer(f'<img src="{uri}" alt="Diagram">'), 'html.parser')
        assert soup.img['src'] == uri
        assert soup.img['alt'] == 'Diagram'

    @pytest.mark.parametrize('binding', ['shared', 'route'])
    def test_raster_data_is_only_allowed_on_image_source(self, binding):
        from bs4 import BeautifulSoup
        from x_ipe.routes import ideas_routes
        from x_ipe.services import conversion_utils
        sanitizer = (conversion_utils.sanitize_converted_html if binding == 'shared'
                     else ideas_routes._sanitize_converted_html)
        soup = BeautifulSoup(sanitizer(f'<a href="{PNG_URI}">Open</a>'), 'html.parser')
        assert 'href' not in soup.a.attrs

    @pytest.mark.parametrize('binding', ['shared', 'route'])
    def test_svg_static_shapes_preserved_but_link_mutation_removed(self, binding):
        from bs4 import BeautifulSoup
        from x_ipe.routes import ideas_routes
        from x_ipe.services import conversion_utils
        sanitizer = (conversion_utils.sanitize_converted_html if binding == 'shared'
                     else ideas_routes._sanitize_converted_html)
        dirty = ('<svg viewBox="0 0 10 10"><circle cx="5" cy="5" r="4"/>'
                 '<a href="https://example.com"><text>Open</text>'
                 '<animate attributeName="href" values="javascript:alert(1)"/>'
                 '<set attributeName="href" to="javascript:alert(1)"/></a></svg>')
        soup = BeautifulSoup(sanitizer(dirty), 'html.parser')
        assert soup.svg is not None
        assert soup.circle['r'] == '4'
        assert soup.a['href'] == 'https://example.com'
        assert not soup.find_all(['animate', 'set'])

    @pytest.mark.parametrize('binding', ['shared', 'route'])
    def test_actual_sanitizer_removes_active_elements_and_events(self, binding):
        from x_ipe.routes import ideas_routes
        from x_ipe.services import conversion_utils
        sanitizer = (conversion_utils.sanitize_converted_html if binding == 'shared'
                     else ideas_routes._sanitize_converted_html)
        assert sanitizer(DIRTY_HTML) == SAFE_HTML

    @pytest.mark.parametrize('binding', ['shared', 'route'])
    def test_javascript_url_is_not_returned(self, binding):
        """NFR-038-C.5 security probe: keep a real vulnerability visibly failing."""
        from bs4 import BeautifulSoup
        from x_ipe.routes import ideas_routes
        from x_ipe.services import conversion_utils
        sanitizer = (conversion_utils.sanitize_converted_html if binding == 'shared'
                     else ideas_routes._sanitize_converted_html)
        result = sanitizer('<p>Good</p><a href="javascript:alert(1)">Open</a>')
        assert '<p>Good</p>' in result
        soup = BeautifulSoup(result, 'html.parser')
        assert not soup.select('a[href^="javascript:"]'), result

    def test_strips_script_tags(self):
        """AC-038-C.04g: Removes <script> tags from converted HTML."""
        from x_ipe.services.conversion_utils import sanitize_converted_html
        html = '<p>Hello</p><script>alert("xss")</script><p>World</p>'
        result = sanitize_converted_html(html)
        assert '<script>' not in result
        assert 'alert' not in result
        assert '<p>Hello</p>' in result
        assert '<p>World</p>' in result

    def test_strips_iframe_tags(self):
        """AC-038-C.04g: Removes <iframe> tags."""
        from x_ipe.services.conversion_utils import sanitize_converted_html
        html = '<div><iframe src="evil.com"></iframe></div>'
        result = sanitize_converted_html(html)
        assert '<iframe' not in result

    def test_strips_on_event_attributes(self):
        """AC-038-C.04g: Removes on* event handler attributes."""
        from x_ipe.services.conversion_utils import sanitize_converted_html
        html = '<p onclick="alert(1)" onmouseover="hack()">Text</p>'
        result = sanitize_converted_html(html)
        assert 'onclick' not in result
        assert 'onmouseover' not in result
        assert 'Text' in result

    def test_strips_object_embed_tags(self):
        """AC-038-C.04g: Removes <object> and <embed> tags."""
        from x_ipe.services.conversion_utils import sanitize_converted_html
        html = '<object data="x"></object><embed src="y"><p>Safe</p>'
        result = sanitize_converted_html(html)
        assert '<object' not in result
        assert '<embed' not in result
        assert '<p>Safe</p>' in result

    def test_preserves_safe_html(self):
        """Safe HTML elements pass through unchanged."""
        from x_ipe.services.conversion_utils import sanitize_converted_html
        html = '<h1>Title</h1><p>Para</p><ul><li>Item</li></ul><table><tr><td>Cell</td></tr></table>'
        result = sanitize_converted_html(html)
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
        from src.app import create_app
        app = create_app({
            'PROJECT_ROOT': temp_project_dir,
            'TESTING': True,
            'SETTINGS_DB_PATH': os.path.join(temp_project_dir, 'test_settings.db')
        })
        with app.test_client() as client:
            yield client

    def _create_file(self, temp_project_dir, rel_path, content=b''):
        path = Path(temp_project_dir) / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_docx_returns_200_with_x_converted(self, temp_project_dir, app_client):
        """AC-038-C.04a: .docx returns 200 with X-Converted: true header."""
        path = self._create_file(temp_project_dir, 'x-ipe-docs/ideas/test-idea/doc.docx', MOCK_ONLY_BYTES)
        with patch('x_ipe.routes.ideas_routes._convert_docx', return_value='<p>Converted</p>') as converter:
            resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/doc.docx')
        converter.assert_called_once_with(path.resolve())
        assert resp.status_code == 200
        assert resp.headers['X-Converted'] == 'true'
        assert resp.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert resp.data == b'<p>Converted</p>'

    def test_msg_returns_200_with_x_converted(self, temp_project_dir, app_client):
        """AC-038-C.04b: .msg returns 200 with X-Converted: true header."""
        path = self._create_file(temp_project_dir, 'x-ipe-docs/ideas/test-idea/email.msg', MOCK_ONLY_BYTES)
        with patch('x_ipe.routes.ideas_routes._convert_msg', return_value='<div>Email</div>') as converter:
            resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/email.msg')
        converter.assert_called_once_with(path.resolve())
        assert resp.status_code == 200
        assert resp.headers['X-Converted'] == 'true'
        assert resp.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert resp.data == b'<div>Email</div>'

    def test_real_docx_route_conversion(self, temp_project_dir, app_client, minimal_docx):
        """Real DOCX through HTTP, route converter, mammoth and real sanitizer."""
        self._create_file(temp_project_dir, 'x-ipe-docs/ideas/test-idea/real.docx', minimal_docx.read_bytes())
        resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/real.docx')
        assert resp.status_code == 200
        assert resp.headers['X-Converted'] == 'true'
        assert resp.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert resp.data == REAL_DOCX_HTML.encode('utf-8')

    def test_msg_parser_boundary_and_sanitized_template(self, temp_project_dir, app_client):
        """Real route/template/sanitizer, mocked parser; NOT a real MSG integration."""
        path = self._create_file(temp_project_dir, 'x-ipe-docs/ideas/test-idea/parser.msg', MOCK_ONLY_BYTES)
        mock_msg = MagicMock(sender='Alice <alice@example.com>', to='Bob & Co',
                             cc='', date='2026-10-14', subject='<Important>')
        mock_msg.htmlBody = DIRTY_HTML.encode('utf-8')
        mock_msg.body = 'Plain text must not be used'
        with patch('extract_msg.openMsg', return_value=mock_msg) as parser:
            resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/parser.msg')
        parser.assert_called_once_with(str(path.resolve()))
        mock_msg.close.assert_called_once_with()
        assert resp.status_code == 200
        assert resp.headers['X-Converted'] == 'true'
        assert resp.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert resp.data == (
            '<div class="msg-preview"><table class="msg-headers">'
            '<tr><td><strong>From:</strong></td><td>Alice &lt;alice@example.com&gt;</td></tr>'
            '<tr><td><strong>To:</strong></td><td>Bob &amp; Co</td></tr>'
            '<tr><td><strong>CC:</strong></td><td></td></tr>'
            '<tr><td><strong>Date:</strong></td><td>2026-10-14</td></tr>'
            '<tr><td><strong>Subject:</strong></td><td>&lt;Important&gt;</td></tr>'
            '</table><hr/><div class="msg-body"><p>Good</p></div></div>'
        ).encode('utf-8')

    @pytest.mark.parametrize('extension,binding', [('docx', '_convert_docx'), ('msg', '_convert_msg')])
    def test_oversized_file_returns_413(self, temp_project_dir, app_client, extension, binding):
        """AC-038-C.04f: File >10MB returns 413."""
        rel_path = f'x-ipe-docs/ideas/test-idea/big.{extension}'
        self._create_file(
            temp_project_dir,
            rel_path,
            b'x' * (10 * 1024 * 1024 + 1)
        )
        with patch(f'x_ipe.routes.ideas_routes.{binding}') as converter:
            resp = app_client.get('/api/ideas/file', query_string={'path': rel_path})
        converter.assert_not_called()
        assert resp.status_code == 413
        assert resp.get_json() == {'error': 'File too large to preview (max 10MB)'}
        assert 'X-Converted' not in resp.headers

    def test_corrupted_docx_returns_415(self, temp_project_dir, app_client):
        """AC-038-C.04e: Corrupted .docx returns 415."""
        path = self._create_file(temp_project_dir, 'x-ipe-docs/ideas/test-idea/bad.docx', b'corrupted')
        with patch('x_ipe.routes.ideas_routes._convert_docx', side_effect=ValueError('parse error')) as converter:
            resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/bad.docx')
        converter.assert_called_once_with(path.resolve())
        assert resp.status_code == 415
        assert resp.get_json() == {'error': 'Preview unavailable for this file'}
        assert resp.headers['Content-Type'] == 'application/json'
        assert 'X-Converted' not in resp.headers
        assert b'parse error' not in resp.data

    def test_corrupted_docx_real_parser_returns_415(self, temp_project_dir, app_client):
        """Separate actual parser failure from the mocked exception contract."""
        self._create_file(temp_project_dir, 'x-ipe-docs/ideas/test-idea/corrupt.docx', b'not a ZIP/OOXML package')
        resp = app_client.get('/api/ideas/file?path=x-ipe-docs/ideas/test-idea/corrupt.docx')
        assert resp.status_code == 415
        assert resp.get_json() == {'error': 'Preview unavailable for this file'}
        assert 'X-Converted' not in resp.headers

    @pytest.mark.parametrize('extension,binding', [('docx', '_convert_docx'), ('msg', '_convert_msg')])
    def test_conversion_read_error_returns_415(self, temp_project_dir, app_client, extension, binding):
        """A read failure is not a successful conversion and leaks no exception."""
        rel_path = f'x-ipe-docs/ideas/test-idea/unreadable.{extension}'
        path = self._create_file(temp_project_dir, rel_path, MOCK_ONLY_BYTES)
        with patch(f'x_ipe.routes.ideas_routes.{binding}', side_effect=PermissionError('private path')) as converter:
            resp = app_client.get('/api/ideas/file', query_string={'path': rel_path})
        converter.assert_called_once_with(path.resolve())
        assert resp.status_code == 415
        assert resp.get_json() == {'error': 'Preview unavailable for this file'}
        assert resp.headers['Content-Type'] == 'application/json'
        assert 'X-Converted' not in resp.headers
        assert b'private path' not in resp.data

    @pytest.mark.parametrize('case,status,error', [
        ('missing', 400, 'path parameter required'),
        ('absent', 404, 'File not found'),
        ('traversal', 403, 'Access denied'),
        ('absolute', 403, 'Access denied'),
    ])
    def test_rejected_paths_do_not_convert(self, temp_project_dir, app_client, tmp_path, case, status, error):
        """Preserve existing missing/unauthorized/path-escape guards before parsing."""
        outside = tmp_path / 'outside.docx'
        outside.write_bytes(MOCK_ONLY_BYTES)
        paths = {
            'missing': None,
            'absent': 'x-ipe-docs/ideas/test-idea/absent.docx',
            'traversal': os.path.relpath(outside, temp_project_dir),
            'absolute': str(outside),
        }
        query = {} if paths[case] is None else {'path': paths[case]}
        with patch('x_ipe.routes.ideas_routes._convert_docx') as docx_converter, \
                patch('x_ipe.routes.ideas_routes._convert_msg') as msg_converter:
            resp = app_client.get('/api/ideas/file', query_string=query)
        docx_converter.assert_not_called()
        msg_converter.assert_not_called()
        assert resp.status_code == status
        assert resp.get_json() == {'error': error}
        assert 'X-Converted' not in resp.headers

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

    @pytest.mark.parametrize('extension,binding', [('docx', '_convert_docx'), ('msg', '_convert_msg')])
    def test_html_sanitization_applied(self, temp_project_dir, app_client, extension, binding):
        """AC-038-C.04g: Converted HTML is sanitized before returning."""
        rel_path = f'x-ipe-docs/ideas/test-idea/evil.{extension}'
        path = self._create_file(temp_project_dir, rel_path, MOCK_ONLY_BYTES)
        with patch(f'x_ipe.routes.ideas_routes.{binding}', return_value=DIRTY_HTML) as converter:
            resp = app_client.get('/api/ideas/file', query_string={'path': rel_path})
        converter.assert_called_once_with(path.resolve())
        assert resp.status_code == 200
        assert resp.headers['X-Converted'] == 'true'
        assert resp.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert resp.data == SAFE_HTML.encode('utf-8')

    @pytest.mark.parametrize('extension,binding', [('docx', '_convert_docx'), ('msg', '_convert_msg')])
    def test_route_does_not_return_javascript_url(self, temp_project_dir, app_client, extension, binding):
        """A residual server-side XSS boundary is a failure, not accepted behavior."""
        rel_path = f'x-ipe-docs/ideas/test-idea/url.{extension}'
        path = self._create_file(temp_project_dir, rel_path, MOCK_ONLY_BYTES)
        dirty_html = '<p>Good</p><a href="javascript:alert(1)">Open</a>'
        with patch(f'x_ipe.routes.ideas_routes.{binding}', return_value=dirty_html) as converter:
            resp = app_client.get('/api/ideas/file', query_string={'path': rel_path})
        converter.assert_called_once_with(path.resolve())
        assert resp.status_code == 200
        assert resp.headers['X-Converted'] == 'true'
        assert resp.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert b'<p>Good</p>' in resp.data
        assert b'javascript:' not in resp.data.lower(), resp.data

    @pytest.mark.parametrize('extension,binding', [('docx', '_convert_docx'), ('msg', '_convert_msg')])
    @pytest.mark.parametrize('uri', UNSAFE_URIS)
    def test_route_removes_obfuscated_uri_and_preserves_safe_content(
            self, temp_project_dir, app_client, extension, binding, uri):
        from bs4 import BeautifulSoup
        rel_path = f'x-ipe-docs/ideas/test-idea/uri.{extension}'
        path = self._create_file(temp_project_dir, rel_path, MOCK_ONLY_BYTES)
        dirty = (f'<a id="bad" href="{uri}">Open</a>'
                 '<a id="safe" href="mailto:alice@example.com">Email</a>'
                 f'<img src="{PNG_URI}" alt="Diagram"><p>Good</p>')
        with patch(f'x_ipe.routes.ideas_routes.{binding}', return_value=dirty) as converter:
            resp = app_client.get('/api/ideas/file', query_string={'path': rel_path})
        converter.assert_called_once_with(path.resolve())
        assert resp.status_code == 200
        assert resp.headers['X-Converted'] == 'true'
        assert resp.headers['Content-Type'] == 'text/html; charset=utf-8'
        soup = BeautifulSoup(resp.data, 'html.parser')
        assert 'href' not in soup.find(id='bad').attrs
        assert soup.find(id='safe')['href'] == 'mailto:alice@example.com'
        assert soup.img['src'] == PNG_URI
        assert soup.p.get_text() == 'Good'
