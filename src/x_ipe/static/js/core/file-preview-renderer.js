/**
 * CR-008: Shared File Preview Renderer
 *
 * Unified file preview component extracted from DeliverableViewer.showPreview()
 * and KBBrowseModal._renderArticleScene(). Supports markdown (with DSL),
 * images, PDF, DOCX/MSG (converted), HTML, and code/text files.
 *
 * Consumers: KBBrowseModal (KB browse article scene), DeliverableViewer (file preview modal)
 */
class FilePreviewRenderer {

    static FILE_TYPES = {
        image: new Set(['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'ico']),
        pdf: new Set(['pdf']),
        markdown: new Set(['md']),
        html: new Set(['html', 'htm']),
        code: new Set([
            'py', 'js', 'ts', 'json', 'yaml', 'yml', 'xml', 'css',
            'txt', 'sh', 'bash', 'go', 'java', 'rb', 'rs', 'c', 'cpp', 'h',
            'toml', 'ini', 'cfg', 'log', 'csv', 'sql', 'r', 'kt', 'swift'
        ])
    };

    /**
     * @param {Object} options
     * @param {string} options.apiEndpoint - URL pattern with {path} placeholder,
     *   e.g. '/api/kb/files/{path}/preview' or '/api/ideas/file?path={path}'
     * @param {string} [options.endpointStyle='path'] - 'path' encodes segments individually,
     *   'query' encodes the entire path as one component
     * @param {string} [options.downloadUrl] - URL pattern for download link on unsupported types
     */
    constructor(options = {}) {
        this._options = {
            apiEndpoint: options.apiEndpoint || '/api/ideas/file?path={path}',
            endpointStyle: options.endpointStyle || 'path',
            downloadUrl: options.downloadUrl || null
        };
        this._currentBlobUrl = null;
        this._requestCounter = 0;
    }

    /**
     * Detect file type category from file path extension.
     * @param {string} filePath
     * @returns {string} 'image'|'pdf'|'markdown'|'html'|'code'|'unknown'
     */
    static detectType(filePath) {
        const ext = filePath.split('.').pop().toLowerCase();
        if (FilePreviewRenderer.FILE_TYPES.image.has(ext)) return 'image';
        if (FilePreviewRenderer.FILE_TYPES.pdf.has(ext)) return 'pdf';
        if (FilePreviewRenderer.FILE_TYPES.markdown.has(ext)) return 'markdown';
        if (FilePreviewRenderer.FILE_TYPES.html.has(ext)) return 'html';
        if (FilePreviewRenderer.FILE_TYPES.code.has(ext)) return 'code';
        return 'unknown';
    }

    /**
     * Render a file preview into the given container element.
     * @param {string} filePath - relative file path
     * @param {HTMLElement} container - DOM element to render into
     * @returns {Promise<void>}
     */
    async renderPreview(filePath, container) {
        if (filePath.includes('..')) {
            this._showError(container, 'Invalid file path', filePath);
            return;
        }

        const requestId = ++this._requestCounter;
        this._revokeBlobUrl();
        this._showLoading(container);

        const type = FilePreviewRenderer.detectType(filePath);
        const url = this._buildUrl(filePath);

        if (type === 'image') {
            this._renderImage(container, url, filePath);
            return;
        }

        if (type === 'pdf') {
            this._renderPdf(container, url);
            return;
        }

        try {
            const resp = await fetch(url);
            if (requestId !== this._requestCounter) return;

            if (!resp.ok) {
                const msg = resp.status === 413 ? 'File too large to preview (max 10MB)'
                          : resp.status === 415 ? 'Binary file — cannot preview'
                          : 'Failed to load file';
                this._showError(container, msg, filePath);
                return;
            }

            const text = await resp.text();
            if (requestId !== this._requestCounter) return;

            const isConverted = resp.headers.get('X-Converted') === 'true';
            if (isConverted) {
                this._renderConvertedHtml(container, text);
                return;
            }

            if (type === 'unknown') {
                this._showError(container, 'Cannot preview this file type', filePath);
                return;
            }

            if (type === 'markdown') {
                this._renderMarkdown(container, text);
            } else if (type === 'html') {
                this._renderHtml(container, text);
            } else {
                this._renderCode(container, text, filePath.split('.').pop().toLowerCase());
            }
        } catch {
            if (requestId !== this._requestCounter) return;
            this._showError(container, 'Failed to load file', filePath);
        }
    }

    /**
     * Revoke any tracked blob URL and invalidate in-flight requests.
     */
    destroy() {
        this._revokeBlobUrl();
        this._requestCounter++;
    }

    // --- Private methods ---

    _buildUrl(filePath) {
        const pattern = this._options.apiEndpoint;
        if (this._options.endpointStyle === 'query') {
            return pattern.replace('{path}', encodeURIComponent(filePath));
        }
        const encodedPath = filePath.split('/').map(encodeURIComponent).join('/');
        return pattern.replace('{path}', encodedPath);
    }

    _showLoading(container) {
        container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#888">Loading preview\u2026</div>';
    }

    _showError(container, message, filePath) {
        const name = filePath ? filePath.split('/').pop() : '';
        let html = '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#888;gap:8px">';
        html += `<div>${this._escapeHtml(message)}</div>`;
        if (name) html += `<div style="font-size:0.85em;opacity:0.7">${this._escapeHtml(name)}</div>`;
        if (this._options.downloadUrl && filePath) {
            const dlUrl = this._options.downloadUrl.replace('{path}', encodeURIComponent(filePath));
            html += `<a href="${dlUrl}" download style="font-size:0.85em">Download file</a>`;
        }
        html += '</div>';
        container.innerHTML = html;
    }

    _renderImage(container, url, filePath) {
        container.innerHTML = '';
        const img = document.createElement('img');
        img.src = url;
        img.alt = filePath.split('/').pop();
        img.style.cssText = 'max-width:100%;max-height:100%;object-fit:contain;display:block;margin:auto';
        img.onerror = () => this._showError(container, 'Cannot preview this image', filePath);
        container.appendChild(img);
    }

    _renderPdf(container, url) {
        container.innerHTML = '';
        const iframe = document.createElement('iframe');
        iframe.src = url;
        iframe.style.cssText = 'width:100%;height:100%;border:none';
        container.appendChild(iframe);
    }

    _renderMarkdown(container, text) {
        container.innerHTML = '';
        if (typeof ContentRenderer !== 'undefined') {
            const renderer = new ContentRenderer(container);
            renderer.renderMarkdown(text);
        } else if (typeof marked !== 'undefined' && marked.parse) {
            container.innerHTML = marked.parse(text);
        } else {
            const pre = document.createElement('pre');
            pre.textContent = text;
            container.appendChild(pre);
        }
    }

    _renderConvertedHtml(container, html) {
        this._createBlobIframe(container, html, 'text/html', 'allow-same-origin');
    }

    _renderHtml(container, html) {
        this._createBlobIframe(container, html, 'text/html', 'allow-scripts allow-same-origin');
    }

    _createBlobIframe(container, content, mimeType, sandbox) {
        container.innerHTML = '';
        const blob = new Blob([content], { type: mimeType });
        this._currentBlobUrl = URL.createObjectURL(blob);
        const iframe = document.createElement('iframe');
        iframe.src = this._currentBlobUrl;
        iframe.setAttribute('sandbox', sandbox);
        iframe.style.cssText = 'width:100%;height:100%;border:none';
        container.appendChild(iframe);
    }

    _renderCode(container, text, ext) {
        container.innerHTML = '';
        const pre = document.createElement('pre');
        const code = document.createElement('code');
        code.textContent = text;
        if (typeof hljs !== 'undefined') {
            code.className = `language-${ext}`;
            pre.appendChild(code);
            hljs.highlightElement(code);
        } else {
            pre.appendChild(code);
        }
        container.appendChild(pre);
    }

    _revokeBlobUrl() {
        if (this._currentBlobUrl) {
            URL.revokeObjectURL(this._currentBlobUrl);
            this._currentBlobUrl = null;
        }
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
