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
            downloadUrl: options.downloadUrl || null,
            renderMode: options.renderMode || 'auto'
        };
        this._currentBlobUrl = null;
        this._requestCounter = 0;
        this._renderMode = this._options.renderMode;
        this._cachedText = null;
        this._cachedFilePath = null;
        this._cachedContainer = null;
        this._cachedIsConverted = false;
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
     * Check if a file type supports text-renderable toggling (preview/raw).
     * @param {string} filePath
     * @returns {boolean}
     */
    static isTextRenderable(filePath) {
        const type = FilePreviewRenderer.detectType(filePath);
        return type === 'markdown' || type === 'code' || type === 'html';
    }

    /**
     * Get the current render mode.
     * @returns {string} 'auto' or 'raw'
     */
    getRenderMode() {
        return this._renderMode;
    }

    /**
     * Switch render mode and re-render cached content.
     * @param {string} mode - 'auto' or 'raw'
     * @param {HTMLElement} container - DOM element to render into
     */
    setRenderMode(mode, container) {
        this._renderMode = mode;
        if (this._cachedText !== null && container) {
            this._renderContent(container, this._cachedText, this._cachedFilePath, this._cachedIsConverted);
        }
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

            let text = await resp.text();
            if (requestId !== this._requestCounter) return;

            // X-Converted header signals server-side conversion (e.g. .docx → HTML).
            const xConverted = resp.headers.get('X-Converted') === 'true';
            let isConverted = xConverted;

            // When running inside the simulator's srcdoc iframe, a fetch interceptor
            // routes requests through /api/proxy which JSON-wraps HTML responses:
            // {"success": true, "html": "...", "content_type": "text/html; ..."}
            // Unwrap the proxy response so the original content is used.
            if (!isConverted && type === 'unknown') {
                const contentType = (resp.headers.get('Content-Type') || '').toLowerCase();
                if (contentType.includes('application/json')) {
                    try {
                        const json = JSON.parse(text);
                        if (json.success && json.html && json.content_type &&
                            json.content_type.includes('text/html')) {
                            text = json.html;
                            isConverted = true;
                        }
                    } catch { /* not JSON, continue */ }
                } else if (contentType.includes('text/html')) {
                    isConverted = true;
                }
            }
            if (isConverted) {
                this._cachedText = text;
                this._cachedFilePath = filePath;
                this._cachedContainer = container;
                this._cachedIsConverted = true;
                this._renderContent(container, text, filePath, true);
                return;
            }

            if (type === 'unknown') {
                this._showError(container, 'Cannot preview this file type', filePath);
                return;
            }

            this._cachedText = text;
            this._cachedFilePath = filePath;
            this._cachedContainer = container;
            this._cachedIsConverted = false;
            this._renderContent(container, text, filePath, false);
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
        this._cachedText = null;
        this._cachedFilePath = null;
        this._cachedContainer = null;
        this._cachedIsConverted = false;
    }

    // --- Private methods ---

    /**
     * Render content based on current renderMode.
     * In 'raw' mode, always renders plain text. In 'auto' mode, uses rich rendering.
     */
    _renderContent(container, text, filePath, isConverted) {
        if (this._renderMode === 'raw' && !isConverted) {
            this._renderRaw(container, text);
            return;
        }

        if (isConverted) {
            this._renderConvertedHtml(container, text);
            return;
        }

        const type = FilePreviewRenderer.detectType(filePath);
        if (type === 'markdown') {
            this._renderMarkdown(container, text);
        } else if (type === 'html') {
            this._renderHtml(container, text);
        } else {
            this._renderCode(container, text, filePath.split('.').pop().toLowerCase());
        }
    }

    /**
     * Render plain text in a <pre> element using textContent (safe, no HTML injection).
     */
    _renderRaw(container, text) {
        container.innerHTML = '';
        const pre = document.createElement('pre');
        pre.className = 'preview-raw-content';
        pre.textContent = text;
        container.appendChild(pre);
    }

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
        const styledHtml = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><style class="docx-preview-base">
body { margin: 0; padding: 16px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #334155; }
p img { max-height: 2em; vertical-align: middle; }
p > img + br { display: none; }
p > img + * > br:first-child { display: none; }
p > img:only-child { max-height: none; max-width: 100%; display: block; margin: 8px auto; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
td, th { border: 1px solid #e2e8f0; padding: 6px 10px; }
</style></head><body>${html}</body></html>`;
        this._createBlobIframe(container, styledHtml, 'text/html', 'allow-same-origin');
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
