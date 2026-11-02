"""Saved HTML previews must retain their project directory in real browsers."""
import json
import os
from html import unescape
from pathlib import Path
import re
import shutil
import subprocess
import threading
from urllib.parse import quote, urljoin

from flask import Flask
import pytest
from werkzeug.serving import make_server

from x_ipe.routes.main_routes import main_bp
from x_ipe.routes.kb_routes import kb_bp
from x_ipe.services.kb_service import KBService, KB_ROOT_DIR


HTML = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="assets/theme.css">
<script type="module" src="assets/app.js"></script></head><body>
<div id="app"></div><a id="next" href="next.html">Next page</a>
</body></html>"""

HARNESS = """<!doctype html><html><head><meta charset="utf-8">
<title>Saved HTML preview regression</title></head><body>
<button id="open">Open saved HTML</button><div id="workplace-content"></div>
<pre id="result">waiting</pre>
<script src="/static/js/core/content-renderer.js"></script>
<script src="/static/js/core/file-preview-renderer.js"></script>
<script src="/static/js/features/workplace.js"></script>
<script>
const params = new URLSearchParams(location.search);
const mode = params.get('mode');
const path = params.get('path');
const container = document.getElementById('workplace-content');
window.runPreview = async () => {
    if (mode === 'raw') {
        const iframe = document.createElement('iframe');
        iframe.src = '/api/file/content?raw=true&path=' + encodeURIComponent(path);
        container.appendChild(iframe);
    } else if (mode === 'workplace') {
        const manager = Object.create(WorkplaceManager.prototype);
        manager._highlightParentFolder = () => {};
        manager._renderCopilotButton = () => '';
        manager._bindCopilotButton = () => {};
        await manager.openFile(path);
    } else if (mode === 'content') {
        const metadata = await (await fetch('/api/file/content?path=' +
            encodeURIComponent(path))).json();
        new ContentRenderer(container).render(metadata);
    } else {
        const memory = mode === 'memory';
        const renderer = new FilePreviewRenderer({
            apiEndpoint: memory ? '/api/kb/files/{path}/raw' : '/api/file/raw?path={path}',
            endpointStyle: memory ? 'path' : 'query'
        });
        await renderer.renderPreview(path, container);
    }
};
document.getElementById('open').addEventListener('click', window.runPreview);
let attempts = 0;
const timer = setInterval(() => {
    const iframe = container.querySelector('iframe');
    const doc = iframe && iframe.contentDocument;
    const app = doc && doc.getElementById('app');
    if (app && app.textContent === 'Relative module executed') {
        const image = doc.getElementById('asset');
        const output = {
            text: app.textContent, color: getComputedStyle(app).color,
            imageLoaded: image.complete && image.naturalWidth === 3,
            background: getComputedStyle(app).backgroundImage,
            next: doc.getElementById('next').href,
            url: doc.URL
        };
        document.getElementById('result').textContent = JSON.stringify(output);
        if (output.imageLoaded) clearInterval(timer);
    } else if (iframe && ++attempts > 100) {
        document.getElementById('result').textContent = 'FAILED: empty app';
        clearInterval(timer);
    }
}, 20);
if (params.has('auto')) document.getElementById('open').click();
</script></body></html>"""


def create_preview_app(project: Path) -> Flask:
    """Use production routes and scripts with disposable project content."""
    package = Path(__file__).resolve().parents[1] / 'src' / 'x_ipe'
    app = Flask(__name__, static_folder=str(package / 'static'))
    app.config.update(TESTING=True, PROJECT_ROOT=str(project), KB_SERVICE=KBService(str(project)))
    app.register_blueprint(main_bp)
    app.register_blueprint(kb_bp)
    app.add_url_rule('/_preview_test', view_func=lambda: HARNESS)
    return app


def write_preview_files(folder: Path) -> None:
    """Create separate dependencies; HTML itself has no visible app content."""
    assets = folder / 'assets'
    assets.mkdir(parents=True)
    (folder / 'index.html').write_text(HTML, encoding='utf-8')
    (folder / 'next.html').write_text('<h1>Relative navigation works</h1>', encoding='utf-8')
    (assets / 'app.js').write_text(
        "import {message} from './message.js';"
        "document.getElementById('app').textContent = message;"
        "const image = new Image(); image.id = 'asset';"
        "image.src = 'assets/pixel.svg'; document.body.appendChild(image);",
        encoding='utf-8',
    )
    (assets / 'message.js').write_text(
        "export const message = 'Relative module executed';", encoding='utf-8',
    )
    (assets / 'theme.css').write_text(
        '@import "./colors.css"; #app {background-image: url("./pixel.svg");}',
        encoding='utf-8',
    )
    (assets / 'colors.css').write_text('#app {color: rgb(12, 34, 56);}', encoding='utf-8')
    (assets / 'pixel.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="3" height="3"/>', encoding='utf-8',
    )


@pytest.fixture
def preview_app(tmp_path):
    project = tmp_path / 'project'
    project.mkdir()
    write_preview_files(project / 'mockups')
    write_preview_files(project / 'space # & \u6d4b\u8bd5')
    write_preview_files(project / KB_ROOT_DIR / 'example')
    return create_preview_app(project)


def test_raw_html_redirect_preserves_relative_assets_and_metadata(preview_app):
    client = preview_app.test_client()
    metadata = client.get('/api/file/content?path=mockups/index.html')
    assert metadata.json['content'] == HTML
    assert metadata.json['type'] == 'html'
    assert metadata.json['path'] == 'mockups/index.html'
    response = client.get('/api/file/content?path=mockups/index.html&raw=true')
    assert response.status_code == 302
    assert response.location.endswith('/api/file/preview/mockups/index.html')
    final = client.get(response.location)
    assert final.mimetype == 'text/html'
    assert final.get_data(as_text=True) == HTML
    script = client.get(urljoin(response.location, 'assets/app.js'))
    assert script.mimetype == 'application/javascript'
    assert b'import {message}' in script.data
    css = client.get(urljoin(response.location, 'assets/theme.css'))
    assert css.mimetype == 'text/css'
    assert b'background-image' in css.data


@pytest.mark.parametrize('path', ['missing.html', 'mockups'])
def test_preview_invalid_targets(preview_app, path):
    response = preview_app.test_client().get('/api/file/preview/' + path)
    assert response.status_code == 404


@pytest.mark.parametrize('endpoint', ['/api/file/preview/', '/api/file/content?raw=true&path='])
@pytest.mark.parametrize('escape', ['../project-other/secret.html', 'escape/secret.html'])
def test_preview_rejects_traversal_and_escaped_symlinks(preview_app, endpoint, escape):
    project = Path(preview_app.config['PROJECT_ROOT'])
    outside = project.parent / 'project-other'
    outside.mkdir()
    (outside / 'secret.html').write_text('external secret')
    (project / 'escape').symlink_to(outside, target_is_directory=True)
    response = preview_app.test_client().get(endpoint + quote(escape, safe='/'))
    assert response.status_code == 403
    assert b'external secret' not in response.data


def test_preview_encoded_paths_and_non_html_raw_compatibility(preview_app):
    project = Path(preview_app.config['PROJECT_ROOT'])
    name = 'mockups/space # & \u6d4b\u8bd5.htm'
    (project / name).write_text(HTML, encoding='utf-8')
    client = preview_app.test_client()
    response = client.get('/api/file/content', query_string={'path': name, 'raw': 'true'},
                          follow_redirects=True)
    assert response.status_code == 200
    assert response.get_data(as_text=True) == HTML
    for path, mime in [('assets/app.js', 'application/javascript'), ('assets/theme.css', 'text/css'),
                       ('assets/pixel.svg', 'image/svg+xml'), ('next.html', 'text/html')]:
        response = client.get('/api/file/preview/mockups/' + path)
        assert response.status_code == 200
        assert response.mimetype == mime
    old = client.get('/api/file/content?raw=true&path=mockups/assets/app.js')
    assert old.status_code == 200
    assert old.data == (project / 'mockups/assets/app.js').read_bytes()
    assert old.mimetype == 'application/javascript'
    for name, mime in [('module.mjs', 'text/javascript'), ('font.woff2', 'font/woff2')]:
        (project / name).write_bytes(b'asset')
        response = client.get('/api/file/preview/' + name)
        assert response.status_code == 200
        assert response.mimetype in {mime, 'application/javascript'}


@pytest.mark.parametrize('path', ['missing.html', 'mockups'])
def test_query_content_invalid_targets(preview_app, path):
    response = preview_app.test_client().get('/api/file/content', query_string={'path': path})
    assert response.status_code == 404


@pytest.mark.parametrize('mode', ['raw', 'workplace', 'content', 'shared', 'memory'])
@pytest.mark.parametrize('folder', ['mockups', 'space # & \u6d4b\u8bd5'])
def test_browser_saved_html_executes_relative_script_and_styles(preview_app, tmp_path, mode, folder):
    chrome = (os.environ.get('CHROME_BIN') or shutil.which('chromium') or
              shutil.which('chromium-browser') or shutil.which('google-chrome'))
    mac_chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    if not chrome and mac_chrome.is_file():
        chrome = str(mac_chrome)
    if not chrome:
        pytest.skip('Chrome/Chromium required; set CHROME_BIN for browser regression')
    server = make_server('127.0.0.1', 0, preview_app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    path = 'example/index.html' if mode == 'memory' else folder + '/index.html'
    url = f'http://127.0.0.1:{server.server_port}/_preview_test?auto&mode={mode}&path={quote(path)}'
    try:
        process = subprocess.run(
            [chrome, '--headless', '--disable-gpu', '--no-first-run',
             f'--user-data-dir={tmp_path / "chrome"}', '--dump-dom',
             '--virtual-time-budget=5000', url],
            capture_output=True, text=True, timeout=30, check=True,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    result = re.search(r'<pre id="result">(.*?)</pre>', process.stdout, re.S)
    assert result is not None, process.stdout
    rendered = unescape(result.group(1))
    assert rendered.startswith('{'), rendered
    output = json.loads(rendered)
    assert output['text'] == 'Relative module executed'
    assert output['color'] == 'rgb(12, 34, 56)'
    assert output['imageLoaded'] is True
    assert '/api/file/preview/' in output['url']
    assert '/assets/pixel.svg' in output['background']
    assert output['next'].endswith('/next.html')
    assert preview_app.test_client().get('/' + output['next'].split('/', 3)[3]).status_code == 200
