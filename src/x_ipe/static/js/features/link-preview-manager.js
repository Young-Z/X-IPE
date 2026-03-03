/**
 * Link Preview Manager
 * FEATURE-043-A: Link Interception & Preview Modal
 *
 * Intercepts clicks on internal links (x-ipe-docs/, .github/skills/)
 * and displays file content in a preview modal.
 * Reuses DeliverableViewer modal pattern from FEATURE-038-C.
 */
class LinkPreviewManager {
    constructor() {
        this._modal = null;
        this._backdrop = null;
        this._contentArea = null;
        this._titleEl = null;
        this._abortController = null;
        this._isOpen = false;
        this._escHandler = null;
    }

    /**
     * Create modal DOM structure (reuses deliverable-preview CSS pattern).
     */
    _createModal() {
        this._backdrop = document.createElement('div');
        this._backdrop.className = 'link-preview-backdrop';

        const modal = document.createElement('div');
        modal.className = 'link-preview-modal';

        const header = document.createElement('div');
        header.className = 'link-preview-header';

        this._titleEl = document.createElement('span');
        this._titleEl.className = 'link-preview-title';

        const closeBtn = document.createElement('span');
        closeBtn.className = 'link-preview-close';
        closeBtn.textContent = '✕';
        closeBtn.addEventListener('click', () => this.close());

        header.appendChild(this._titleEl);
        header.appendChild(closeBtn);

        this._contentArea = document.createElement('div');
        this._contentArea.className = 'link-preview-content';

        modal.appendChild(header);
        modal.appendChild(this._contentArea);
        this._backdrop.appendChild(modal);
        this._modal = modal;

        // Close on backdrop click (not modal click)
        this._backdrop.addEventListener('click', (e) => {
            if (e.target === this._backdrop) this.close();
        });
    }

    /**
     * Open the preview modal for a given file path.
     * @param {string} filePath - internal file path (e.g. x-ipe-docs/requirements/spec.md)
     */
    async open(filePath) {
        // Strip query params and anchors
        const cleanPath = filePath.split('?')[0].split('#')[0];

        if (!this._backdrop) {
            this._createModal();
            document.body.appendChild(this._backdrop);
        }

        // Update title
        this._titleEl.textContent = cleanPath.split('/').pop();
        this._showLoading(cleanPath);

        // Show modal
        this._isOpen = true;
        requestAnimationFrame(() => {
            this._backdrop.classList.add('active');
        });

        // Escape key handler
        if (!this._escHandler) {
            this._escHandler = (e) => {
                if (e.key === 'Escape') this.close();
            };
            document.addEventListener('keydown', this._escHandler);
        }

        // Fetch and display
        try {
            const data = await this._fetchFile(cleanPath);
            if (data) this._showContent(data);
        } catch (err) {
            if (err.name === 'AbortError') return; // intentional cancel
            if (err.type === 'not_found') {
                this._showError(`File not found: ${cleanPath}`, cleanPath, false);
            } else {
                this._showError(`Failed to load file: ${cleanPath}`, cleanPath, true);
            }
        }
    }

    /**
     * Fetch file content from API with AbortController.
     */
    async _fetchFile(path) {
        if (this._abortController) this._abortController.abort();
        this._abortController = new AbortController();

        const response = await fetch(
            `/api/file/content?path=${encodeURIComponent(path)}`,
            { signal: this._abortController.signal }
        );

        if (!response.ok) {
            const err = new Error(response.status === 404 ? 'not found' : 'server error');
            err.type = response.status === 404 ? 'not_found' : 'network';
            throw err;
        }

        return await response.json();
    }

    /**
     * Show loading state in modal.
     */
    _showLoading(path) {
        this._contentArea.innerHTML = `
            <div class="link-preview-loading">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div style="margin-top: 1rem;">${this._escapeHtml(path)}</div>
            </div>
        `;
    }

    /**
     * Show error state in modal.
     */
    _showError(message, path, retryable) {
        let html = `
            <div class="link-preview-error">
                <div style="font-size: 2rem; margin-bottom: 1rem;">⚠️</div>
                <div>${this._escapeHtml(message)}</div>
                <div class="error-path">${this._escapeHtml(path)}</div>
        `;
        if (retryable) {
            html += `<button class="retry-btn" style="margin-top: 1rem; padding: 6px 16px; border-radius: 6px; border: 1px solid #e2e8f0; background: #f8fafc; cursor: pointer;">Retry</button>`;
        }
        html += `</div>`;
        this._contentArea.innerHTML = html;

        if (retryable) {
            const btn = this._contentArea.querySelector('.retry-btn');
            if (btn) btn.addEventListener('click', () => this.open(path));
        }
    }

    /**
     * Show fetched content in modal.
     */
    _showContent(data) {
        const html = this._renderByType(data.content, data.type, data.extension);
        this._contentArea.innerHTML = html;

        // Highlight code blocks
        if (typeof hljs !== 'undefined') {
            this._contentArea.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });
        }

        // Attach link preview to any markdown-body rendered inside the modal
        const mdBody = this._contentArea.querySelector('.markdown-body');
        if (mdBody && !mdBody._linkPreviewAttached) {
            LinkPreviewManager.attachTo(mdBody);
            mdBody._linkPreviewAttached = true;
        }
    }

    /**
     * Render content by type (markdown, html, code).
     */
    _renderByType(content, type, extension) {
        if (type === 'markdown' && typeof marked !== 'undefined') {
            return `<div class="markdown-body">${marked.parse(content)}</div>`;
        }
        if (type === 'html') {
            return `<div class="html-preview-inline">${content}</div>`;
        }
        if (type === 'binary' || !content) {
            return `<div class="link-preview-error"><div>Cannot preview binary file</div></div>`;
        }
        // Code / text
        const escaped = this._escapeHtml(content);
        return `<pre><code class="language-${extension ? extension.replace('.', '') : 'text'}">${escaped}</code></pre>`;
    }

    /**
     * Close the modal and cleanup.
     */
    close() {
        if (this._backdrop) {
            this._backdrop.classList.remove('active');
        }
        if (this._abortController) {
            this._abortController.abort();
            this._abortController = null;
        }
        this._isOpen = false;
    }

    /**
     * Escape HTML for safe rendering.
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Attach delegated click listener to a container.
     * Static method — uses singleton instance.
     * @param {HTMLElement} container
     */
    static attachTo(container) {
        if (container._linkPreviewAttached) return;

        if (!LinkPreviewManager.instance) {
            LinkPreviewManager.instance = new LinkPreviewManager();
        }

        container.addEventListener('click', (e) => {
            const link = e.target.closest('a[data-preview-path]');
            if (!link) return;
            e.preventDefault();
            LinkPreviewManager.instance.open(link.getAttribute('data-preview-path'));
        });

        container._linkPreviewAttached = true;
    }
}
