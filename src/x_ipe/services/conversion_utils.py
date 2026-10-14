"""
Shared file conversion utilities for ideation and KB preview features.

Functions extracted from ideas_routes.py for reuse across the application.
"""
import base64
import binascii
import html
import re
from urllib.parse import unquote, urlsplit

from x_ipe.tracing import x_ipe_tracing


@x_ipe_tracing(level='DEBUG')
def convert_docx(file_path):
    """Convert .docx file to HTML via mammoth. Returns HTML string."""
    import mammoth
    with open(file_path, 'rb') as f:
        result = mammoth.convert_to_html(f)
    return result.value


@x_ipe_tracing(level='DEBUG')
def convert_msg(file_path):
    """Convert .msg file to structured HTML with email metadata and body."""
    import extract_msg
    msg = extract_msg.openMsg(str(file_path))
    try:
        sender = html.escape(str(msg.sender or ''))
        to = html.escape(str(msg.to or ''))
        cc = html.escape(str(msg.cc or ''))
        date = html.escape(str(msg.date or ''))
        subject = html.escape(str(msg.subject or ''))

        if msg.htmlBody:
            body_section = msg.htmlBody if isinstance(msg.htmlBody, str) else msg.htmlBody.decode('utf-8', errors='replace')
        elif msg.body:
            body_section = f'<pre>{html.escape(str(msg.body))}</pre>'
        else:
            body_section = ''

        return (
            f'<div class="msg-preview">'
            f'<table class="msg-headers">'
            f'<tr><td><strong>From:</strong></td><td>{sender}</td></tr>'
            f'<tr><td><strong>To:</strong></td><td>{to}</td></tr>'
            f'<tr><td><strong>CC:</strong></td><td>{cc}</td></tr>'
            f'<tr><td><strong>Date:</strong></td><td>{date}</td></tr>'
            f'<tr><td><strong>Subject:</strong></td><td>{subject}</td></tr>'
            f'</table>'
            f'<hr>'
            f'<div class="msg-body">{body_section}</div>'
            f'</div>'
        )
    finally:
        msg.close()


def _is_safe_conversion_url(value: str, *, image_source: bool = False) -> bool:
    """Classify decoded URLs without rewriting safe original attribute values.

    Fail closed on excessive encoding and unknown schemes. Data URLs are only
    supported for base64 raster images on img.src, never navigation or SVG.
    """
    normalized = value
    for _ in range(10):
        decoded = html.unescape(unquote(normalized))
        if decoded == normalized:
            break
        normalized = decoded
    else:
        return False

    # Browsers ignore tabs/newlines in schemes and leading C0 controls. Be
    # conservative about other controls/whitespace as well when classifying.
    normalized = ''.join(
        char for char in normalized
        if not char.isspace() and ord(char) > 0x20 and ord(char) != 0x7f
    )
    try:
        parsed = urlsplit(normalized)
    except ValueError:
        return False
    if not parsed.scheme:
        # A colon in the first path segment is not an ordinary relative URL;
        # reject malformed/obfuscated schemes rather than treating them as safe.
        return ':' not in re.split(r'[/\\?#]', normalized, maxsplit=1)[0]
    if parsed.scheme in {'http', 'https', 'mailto', 'tel', 'cid'}:
        return True
    if parsed.scheme != 'data' or not image_source:
        return False

    header, separator, payload = normalized.partition(',')
    signatures = {
        'data:image/png;base64': b'\x89PNG\r\n\x1a\n',
        'data:image/jpeg;base64': b'\xff\xd8\xff',
        'data:image/gif;base64': b'GIF8',
        'data:image/bmp;base64': b'BM',
        'data:image/x-icon;base64': b'\x00\x00\x01\x00',
        'data:image/webp;base64': b'RIFF',
    }
    signature = signatures.get(header.lower())
    if not separator or not signature:
        return False
    try:
        decoded_image = base64.b64decode(payload, validate=True)
    except (ValueError, binascii.Error):
        return False
    # Check the signature too: SVG/HTML mislabeled as PNG must not pass.
    return decoded_image.startswith(signature) and (
        header.lower() != 'data:image/webp;base64'
        or decoded_image[8:12] == b'WEBP'
    )


@x_ipe_tracing(level='DEBUG')
def sanitize_converted_html(content: str) -> str:
    """Remove active markup and unsafe URI attributes from conversion output.

    Preserve document formatting, safe links, static SVG and raster images.
    SVG animation/foreign HTML and compound URL attributes are not supported:
    they can bypass a single-URL check or mutate a sanitized link after parsing.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    blocked_tags = {
        'script', 'iframe', 'object', 'embed', 'frame', 'frameset', 'applet',
        'base', 'meta', 'link', 'foreignobject', 'animate', 'animatemotion',
        'animatetransform', 'set',
    }
    # Traverse once: decomposing a parent also destroys its descendants.
    for tag in list(soup.find_all(True)):
        if tag.name and tag.name.lower() in blocked_tags:
            tag.decompose()
    uri_attributes = {
        'href', 'src', 'xlink:href', 'action', 'formaction', 'poster',
        'background', 'cite', 'longdesc', 'usemap', 'profile', 'manifest',
        'data', 'codebase',
    }
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            name = attr.lower()
            if name.startswith('on') or name in {
                'srcdoc', 'srcset', 'imagesrcset', 'ping', 'archive',
            }:
                del tag[attr]
            elif name in uri_attributes and not _is_safe_conversion_url(
                str(tag[attr]), image_source=tag.name == 'img' and name == 'src'
            ):
                del tag[attr]
    return str(soup)
