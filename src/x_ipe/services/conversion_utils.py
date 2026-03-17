"""
Shared file conversion utilities for ideation and KB preview features.

Functions extracted from ideas_routes.py for reuse across the application.
"""
import html
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


@x_ipe_tracing(level='DEBUG')
def sanitize_converted_html(content):
    """Strip dangerous elements from converted HTML using BeautifulSoup."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup.find_all(['script', 'iframe', 'object', 'embed']):
        tag.decompose()
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr.lower().startswith('on'):
                del tag[attr]
    return str(soup)
