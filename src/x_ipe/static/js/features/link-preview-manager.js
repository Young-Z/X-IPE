/**
 * Link Preview Manager
 * FEATURE-043-A: Link Interception & Preview Modal
 * FEATURE-043-B: Breadcrumb Navigation & Visual Distinction
 *
 * Intercepts clicks on internal links (x-ipe-docs/, .github/skills/)
 * and displays file content in a preview modal.
 * Supports nested navigation with breadcrumb trail (max depth 5).
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
        // FEATURE-043-B: Navigation stack
        this._navStack = [];
        this._maxDepth = 5;
        this._backBtn = null;
        this._breadcrumbBar = null;
        this._currentPath = null;
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

        // FEATURE-043-B: Back button (left of title)
        this._backBtn = document.createElement('span');
        this._backBtn.className = 'link-preview-back';
        this._backBtn.innerHTML = '← Back';
        this._backBtn.style.display = 'none';
        this._backBtn.addEventListener('click', () => this._goBack());

        const closeBtn = document.createElement('span');
        closeBtn.className = 'link-preview-close';
        closeBtn.textContent = '✕';
        closeBtn.addEventListener('click', () => this.close());

        header.appendChild(this._backBtn);
        header.appendChild(this._titleEl);
        header.appendChild(closeBtn);

        this._contentArea = document.createElement('div');
        this._contentArea.className = 'link-preview-content';

        // FEATURE-043-B: Breadcrumb bar (between header and content)
        this._breadcrumbBar = document.createElement('div');
        this._breadcrumbBar.className = 'link-preview-breadcrumb';
        this._breadcrumbBar.style.display = 'none';

        modal.appendChild(header);
        modal.appendChild(this._breadcrumbBar);
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
        this._currentPath = cleanPath;

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

        // CR-008: Use shared FilePreviewRenderer for consistent preview
        if (typeof FilePreviewRenderer !== 'undefined') {
            this._contentArea.innerHTML = '';
            if (this._filePreviewRenderer) this._filePreviewRenderer.destroy();
            this._filePreviewRenderer = new FilePreviewRenderer({
                apiEndpoint: '/api/file/raw?path={path}',
                endpointStyle: 'query'
            });
            try {
                await this._filePreviewRenderer.renderPreview(cleanPath, this._contentArea);
                this._updateBreadcrumb();
                // Re-attach link preview for rendered markdown
                const mdBody = this._contentArea.querySelector('.markdown-body');
                if (mdBody && !mdBody._linkPreviewAttached) {
                    LinkPreviewManager.attachTo(mdBody);
                    mdBody._linkPreviewAttached = true;
                }
            } catch (err) {
                if (err.name !== 'AbortError') {
                    this._showError(`Failed to load file: ${cleanPath}`, cleanPath, true);
                }
            }
            return;
        }

        // Fallback: original fetch logic if FilePreviewRenderer not loaded
        try {
            const data = await this._fetchFile(cleanPath);
            if (data) {
                this._showContent(data);
                this._updateBreadcrumb();
            }
        } catch (err) {
            if (err.name === 'AbortError') return;
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
        // CR-008: Cleanup FilePreviewRenderer
        if (this._filePreviewRenderer) {
            this._filePreviewRenderer.destroy();
            this._filePreviewRenderer = null;
        }
        this._isOpen = false;
        // FEATURE-043-B: Clear navigation state
        this._navStack = [];
        this._currentPath = null;
        if (this._breadcrumbBar) this._breadcrumbBar.style.display = 'none';
        if (this._backBtn) this._backBtn.style.display = 'none';
    }

    /**
     * FEATURE-043-B: Navigate to a new file from within the modal (preserves stack).
     */
    async _navigateFromModal(path) {
        if (this._currentPath) {
            if (this._navStack.length >= this._maxDepth) {
                this._navStack.shift();
            }
            this._navStack.push({
                path: this._currentPath,
                title: this._currentPath.split('/').pop()
            });
        }
        await this.open(path);
    }

    /**
     * FEATURE-043-B: Go back to previous file in stack.
     */
    async _goBack() {
        if (this._navStack.length === 0) return;
        const prev = this._navStack.pop();
        await this.open(prev.path);
    }

    /**
     * FEATURE-043-B: Navigate to a specific breadcrumb entry (truncates stack).
     */
    async _goToBreadcrumb(index) {
        const entry = this._navStack[index];
        this._navStack = this._navStack.slice(0, index);
        await this.open(entry.path);
    }

    /**
     * FEATURE-043-B: Re-render breadcrumb bar based on current stack.
     */
    _updateBreadcrumb() {
        if (!this._breadcrumbBar) return;
        if (this._navStack.length === 0) {
            this._breadcrumbBar.style.display = 'none';
            if (this._backBtn) this._backBtn.style.display = 'none';
            return;
        }
        this._breadcrumbBar.style.display = 'flex';
        if (this._backBtn) this._backBtn.style.display = '';

        let html = '';
        this._navStack.forEach((entry, i) => {
            html += `<span class="breadcrumb-entry" data-index="${i}">${this._escapeHtml(entry.title)}</span>`;
            html += '<span class="breadcrumb-sep">›</span>';
        });
        html += `<span class="breadcrumb-current">${this._escapeHtml(this._currentPath.split('/').pop())}</span>`;
        this._breadcrumbBar.innerHTML = html;

        this._breadcrumbBar.querySelectorAll('.breadcrumb-entry').forEach(el => {
            el.addEventListener('click', () => {
                this._goToBreadcrumb(parseInt(el.dataset.index));
            });
        });
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
            const path = link.getAttribute('data-preview-path');
            const instance = LinkPreviewManager.instance;
            // FEATURE-043-B: If click is inside modal content, navigate (preserves stack)
            if (instance._isOpen && instance._contentArea && instance._contentArea.contains(link)) {
                instance._navigateFromModal(path);
            } else {
                instance._navStack = [];
                instance.open(path);
            }
        });

        container._linkPreviewAttached = true;
    }
}
