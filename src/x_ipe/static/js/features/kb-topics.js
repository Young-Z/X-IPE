/**
 * FEATURE-025-D: KB Topics & Summaries
 *
 * Frontend module for topics sidebar, topic detail view with AI summary card,
 * version history, source files, and knowledge graph preview.
 */

const kbTopics = {
    topics: [],
    selectedTopic: null,
    currentDetail: null,
    summaryCache: new Map(),
    contentContainer: null,

    /* ── Topic icon map ────────────────────────────────────────── */
    TOPIC_ICONS: ['bi-cpu', 'bi-braces', 'bi-trophy', 'bi-diagram-3', 'bi-book', 'bi-gear', 'bi-lightning', 'bi-globe'],

    _getTopicIcon(index) {
        return this.TOPIC_ICONS[index % this.TOPIC_ICONS.length];
    },

    /* ── Main entry point ──────────────────────────────────────── */

    /**
     * Render the topics sidebar + content panel.
     * Called by kbCore when topics exist.
     * @param {Element} container - the kb-content element to render into
     * @param {string[]} topics - list of topic names
     */
    render(container, topics) {
        this.topics = topics;
        this.contentContainer = container;
        this.summaryCache.clear();
        this.selectedTopic = null;

        container.innerHTML = `
            <div style="display:flex;height:100%;overflow:hidden;">
                <div class="kb-topics-sidebar" id="kb-topics-sidebar">
                    <div class="kb-topics-sidebar-header">
                        <span class="kb-topics-sidebar-title">Topics</span>
                        <button class="kb-topics-sidebar-btn" title="Add topic (coming soon)">
                            <i class="bi bi-plus"></i>
                        </button>
                    </div>
                    <div class="kb-topic-list" id="kb-topic-list"></div>
                </div>
                <div class="kb-topic-content-panel" id="kb-topic-detail"></div>
            </div>
        `;

        this._renderSidebar(topics);

        if (topics.length > 0) {
            this.showTopicDetail(topics[0]);
        } else {
            this._renderEmptyContent();
        }
    },

    /* ── Sidebar ───────────────────────────────────────────────── */

    _renderSidebar(topics) {
        const list = document.getElementById('kb-topic-list');
        if (!list) return;

        if (topics.length === 0) {
            list.innerHTML = `
                <div class="kb-topics-empty">
                    <i class="bi bi-archive"></i>
                    No topics yet.<br>Upload and classify files to create topics.
                </div>
            `;
            return;
        }

        list.innerHTML = topics.map((name, i) => `
            <div class="kb-topic-item" data-topic="${this._esc(name)}">
                <div class="kb-topic-icon color-${i % 4}">
                    <i class="bi ${this._getTopicIcon(i)}"></i>
                </div>
                <div class="kb-topic-info">
                    <div class="kb-topic-name">${this._esc(name)}</div>
                    <div class="kb-topic-meta" id="kb-topic-meta-${this._esc(name)}">Loading...</div>
                </div>
                <span class="kb-topic-badge" id="kb-topic-badge-${this._esc(name)}">—</span>
            </div>
        `).join('');

        // Bind click events
        list.querySelectorAll('.kb-topic-item').forEach(item => {
            item.addEventListener('click', () => {
                const topic = item.dataset.topic;
                if (topic !== this.selectedTopic) {
                    this.showTopicDetail(topic);
                }
            });
        });

        // Load metadata for sidebar (async, no blocking)
        this._loadSidebarMeta(topics);
    },

    async _loadSidebarMeta(topics) {
        for (const name of topics) {
            try {
                const resp = await fetch(`/api/kb/topics/${encodeURIComponent(name)}/detail`);
                if (!resp.ok) continue;
                const detail = resp.ok ? await resp.json() : null;
                if (!detail) continue;
                const metaEl = document.getElementById(`kb-topic-meta-${this._esc(name)}`);
                const badgeEl = document.getElementById(`kb-topic-badge-${this._esc(name)}`);
                if (metaEl) metaEl.textContent = `${detail.file_count || 0} items • ${detail.summary_count || 0} summaries`;
                if (badgeEl) badgeEl.textContent = detail.file_count || 0;
            } catch { /* ignore */ }
        }
    },

    _highlightSidebarItem(topicName) {
        const list = document.getElementById('kb-topic-list');
        if (!list) return;
        list.querySelectorAll('.kb-topic-item').forEach(item => {
            item.classList.toggle('active', item.dataset.topic === topicName);
        });
    },

    /* ── Topic Detail ──────────────────────────────────────────── */

    async showTopicDetail(topicName) {
        this.selectedTopic = topicName;
        this._highlightSidebarItem(topicName);

        const panel = document.getElementById('kb-topic-detail');
        if (!panel) return;

        // Show loading
        panel.innerHTML = `
            <div class="kb-summary-loading" style="padding-top:80px;">
                <i class="bi bi-hourglass-split"></i>
                Loading topic...
            </div>
        `;

        try {
            const resp = await fetch(`/api/kb/topics/${encodeURIComponent(topicName)}/detail`);
            if (!resp.ok) {
                this._showToast('Failed to load topic', 'error');
                return;
            }
            const detail = await resp.json();
            this.currentDetail = detail;

            // Load latest summary
            let summary = null;
            const sumResp = await fetch(`/api/kb/topics/${encodeURIComponent(topicName)}/summary?version=latest`);
            if (sumResp.ok) {
                summary = await sumResp.json();
                this.summaryCache.set(`${topicName}-v${summary.version}`, summary);
            }

            // Check we're still viewing this topic
            if (this.selectedTopic !== topicName) return;

            this._renderDetail(panel, detail, summary);
        } catch (err) {
            console.error('[KBTopics] Error loading topic detail:', err);
            this._showToast('Error loading topic', 'error');
        }
    },

    _renderDetail(panel, detail, summary) {
        const topicIdx = this.topics.indexOf(detail.name);
        const iconClass = this._getTopicIcon(topicIdx >= 0 ? topicIdx : 0);
        const iconColorIdx = (topicIdx >= 0 ? topicIdx : 0) % 4;
        const colors = ['#f59e0b', '#3b82f6', '#10b981', '#a78bfa'];
        const iconColor = colors[iconColorIdx];

        const hasSummary = summary && summary.content;
        const lastUpdated = detail.last_updated ? this._relativeTime(detail.last_updated) : '—';

        panel.innerHTML = `
            <div class="kb-content-header">
                <div class="kb-content-header-top">
                    <div class="kb-content-title">
                        <h2><i class="bi ${iconClass}" style="color:${iconColor};"></i> ${this._titleCase(detail.name)}</h2>
                        ${detail.summary_count > 0 ? '<span class="kb-topic-badge-lg success"><i class="bi bi-check-circle"></i> Processed</span>' : ''}
                    </div>
                    <div class="kb-content-actions">
                        <button class="kb-btn kb-btn-ghost" id="kb-btn-reprocess">
                            <i class="bi bi-arrow-clockwise"></i> Reprocess
                        </button>
                        <button class="kb-btn kb-btn-primary" id="kb-btn-add-knowledge">
                            <i class="bi bi-plus-lg"></i> Add Knowledge
                        </button>
                    </div>
                </div>
                <div class="kb-topic-stats">
                    <div class="kb-stat-item">
                        <div class="kb-stat-icon"><i class="bi bi-files"></i></div>
                        <div class="kb-stat-info">
                            <span class="kb-stat-value">${detail.file_count || detail.files?.length || 0}</span>
                            <span class="kb-stat-label">Raw Files</span>
                        </div>
                    </div>
                    <div class="kb-stat-item">
                        <div class="kb-stat-icon"><i class="bi bi-file-text"></i></div>
                        <div class="kb-stat-info">
                            <span class="kb-stat-value">${detail.summary_count || 0}</span>
                            <span class="kb-stat-label">Summaries</span>
                        </div>
                    </div>
                    <div class="kb-stat-item">
                        <div class="kb-stat-icon"><i class="bi bi-clock-history"></i></div>
                        <div class="kb-stat-info">
                            <span class="kb-stat-value">${lastUpdated}</span>
                            <span class="kb-stat-label">Last Updated</span>
                        </div>
                    </div>
                    <div class="kb-stat-item">
                        <div class="kb-stat-icon"><i class="bi bi-link-45deg"></i></div>
                        <div class="kb-stat-info">
                            <span class="kb-stat-value">${detail.related_topics?.length || 0}</span>
                            <span class="kb-stat-label">Related Topics</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="kb-content-body">
                ${this._renderSummaryCard(detail, summary)}
                ${this._renderGraphPreview(detail)}
                ${this._renderSourceFiles(detail)}
            </div>
        `;

        this._bindDetailEvents(detail);
    },

    /* ── Summary Card ──────────────────────────────────────────── */

    _renderSummaryCard(detail, summary) {
        if (!summary || !summary.content) {
            return `
                <div class="kb-summary-card">
                    <div class="kb-summary-card-header">
                        <div class="kb-summary-card-title">
                            <i class="bi bi-stars"></i>
                            <h3>AI-Generated Summary</h3>
                        </div>
                    </div>
                    <div class="kb-summary-card-body">
                        <div class="kb-summary-empty">
                            <i class="bi bi-file-text"></i>
                            No summary generated yet. Click <strong>Reprocess</strong> to generate one.
                        </div>
                    </div>
                </div>
            `;
        }

        const versionLabel = `v${summary.version} • ${this._formatDate(summary.date)}`;

        return `
            <div class="kb-summary-card" id="kb-summary-card">
                <div class="kb-summary-card-header">
                    <div class="kb-summary-card-title">
                        <i class="bi bi-stars"></i>
                        <h3>AI-Generated Summary</h3>
                    </div>
                    <span class="kb-summary-version">${versionLabel}</span>
                </div>
                <div class="kb-summary-card-body">
                    <div class="kb-markdown-content" id="kb-summary-content">
                        ${this._renderMarkdown(summary.content)}
                    </div>
                    ${this._renderSourceReference(detail.files)}
                    ${this._renderVersionHistory(detail.summaries, summary.version)}
                </div>
            </div>
        `;
    },

    _renderSourceReference(files) {
        if (!files || files.length === 0) return '';
        const links = files.slice(0, 3).map(f =>
            `<a href="#" class="kb-src-link" data-path="${this._esc(f.path)}">${this._esc(f.name)}</a>`
        ).join(', ');
        const more = files.length > 3 ? `, +${files.length - 3} more` : '';
        return `
            <div class="kb-source-reference">
                <i class="bi bi-link-45deg"></i>
                <span>Sources:</span>
                ${links}${more}
            </div>
        `;
    },

    /* ── Version History ───────────────────────────────────────── */

    _renderVersionHistory(summaries, currentVersion) {
        if (!summaries || summaries.length === 0) return '';
        return `
            <div class="kb-version-history">
                <div class="kb-version-history-title">
                    <i class="bi bi-clock-history"></i> Version History
                </div>
                ${summaries.map(s => `
                    <div class="kb-version-item ${s.version === currentVersion ? 'current' : ''}" data-version="${s.version}">
                        <span class="kb-version-dot"></span>
                        <div class="kb-version-info">
                            <span class="kb-version-label">v${s.version}${s.current ? ' (Current)' : ''}</span>
                            <span class="kb-version-date">${this._formatDate(s.date)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    /* ── Source Files ───────────────────────────────────────────── */

    _renderSourceFiles(detail) {
        const files = detail.files || [];
        return `
            <div class="kb-raw-files-section">
                <div class="kb-section-title">
                    <i class="bi bi-folder2-open"></i>
                    Source Files (${files.length})
                </div>
                <div class="kb-raw-file-list">
                    ${files.length === 0 ? '<div class="kb-topics-empty" style="padding:16px;">No source files</div>' : ''}
                    ${files.map(f => this._renderFileItem(f)).join('')}
                </div>
            </div>
        `;
    },

    _renderFileItem(file) {
        const iconInfo = this._getFileIconInfo(file.type);
        return `
            <div class="kb-raw-file-item" data-path="${this._esc(file.path)}">
                <div class="kb-raw-file-icon ${iconInfo.cssClass}">
                    <i class="bi ${iconInfo.icon}"></i>
                </div>
                <div class="kb-raw-file-info">
                    <div class="kb-raw-file-name">${this._esc(file.name)}</div>
                    <div class="kb-raw-file-meta">${this._formatSize(file.size)}</div>
                </div>
                <div class="kb-raw-file-actions">
                    <button class="kb-btn-icon" title="View"><i class="bi bi-eye"></i></button>
                    <button class="kb-btn-icon" title="Download"><i class="bi bi-download"></i></button>
                </div>
            </div>
        `;
    },

    _getFileIconInfo(type) {
        const map = {
            'pdf': { icon: 'bi-file-pdf', cssClass: 'pdf' },
            'markdown': { icon: 'bi-markdown', cssClass: 'markdown' },
            'python': { icon: 'bi-filetype-py', cssClass: 'code' },
            'javascript': { icon: 'bi-filetype-js', cssClass: 'code' },
            'text': { icon: 'bi-file-text', cssClass: 'default' },
        };
        return map[type] || { icon: 'bi-file-earmark', cssClass: 'default' };
    },

    /* ── Knowledge Graph Preview ───────────────────────────────── */

    _renderGraphPreview(detail) {
        const related = detail.related_topics || [];
        const graphIcons = ['bi-braces', 'bi-graph-up', 'bi-database', 'bi-cloud'];
        const topicIdx = this.topics.indexOf(detail.name);
        const centerIcon = this._getTopicIcon(topicIdx >= 0 ? topicIdx : 0);

        const nodes = related.slice(0, 4).map((_, i) =>
            `<div class="kb-graph-node n${i}"><i class="bi ${graphIcons[i % graphIcons.length]}"></i></div>`
        ).join('');

        const positions = [[80,60],[300,50],[60,140],[320,130]];
        const lines = related.slice(0, 4).map((_, i) =>
            `<line x1="200" y1="100" x2="${positions[i][0]}" y2="${positions[i][1]}"/>`
        ).join('');

        return `
            <div class="kb-graph-preview">
                <div class="kb-graph-preview-header">
                    <div class="kb-graph-preview-title">
                        <i class="bi bi-diagram-3"></i>
                        Related Knowledge Graph
                    </div>
                    <button class="kb-btn kb-btn-ghost" style="padding:4px 10px;font-size:12px;" title="Coming in Phase 2">
                        <i class="bi bi-arrows-fullscreen"></i> Expand
                    </button>
                </div>
                <div class="kb-graph-canvas">
                    <svg class="kb-graph-lines" viewBox="0 0 400 200">
                        ${lines}
                    </svg>
                    <div class="kb-graph-node center"><i class="bi ${centerIcon}"></i></div>
                    ${nodes}
                </div>
            </div>
        `;
    },

    /* ── Event Binding ─────────────────────────────────────────── */

    _bindDetailEvents(detail) {
        // Reprocess button
        const reprocessBtn = document.getElementById('kb-btn-reprocess');
        if (reprocessBtn) {
            reprocessBtn.addEventListener('click', () => this._reprocess(detail.name));
        }

        // Add Knowledge button
        const addBtn = document.getElementById('kb-btn-add-knowledge');
        if (addBtn) {
            addBtn.addEventListener('click', () => this._addKnowledge(detail.name));
        }

        // Version switching
        document.querySelectorAll('.kb-version-item').forEach(item => {
            item.addEventListener('click', () => {
                const version = parseInt(item.dataset.version);
                this._switchVersion(detail.name, version);
            });
        });
    },

    /* ── Version Switching ─────────────────────────────────────── */

    async _switchVersion(topicName, version) {
        const cacheKey = `${topicName}-v${version}`;
        let summary = this.summaryCache.get(cacheKey);

        if (!summary) {
            try {
                const resp = await fetch(`/api/kb/topics/${encodeURIComponent(topicName)}/summary?version=${version}`);
                if (!resp.ok) {
                    this._showToast('Version not found', 'error');
                    return;
                }
                summary = await resp.json();
                this.summaryCache.set(cacheKey, summary);
            } catch {
                this._showToast('Error loading version', 'error');
                return;
            }
        }

        // Update summary content
        const contentEl = document.getElementById('kb-summary-content');
        if (contentEl) {
            contentEl.innerHTML = this._renderMarkdown(summary.content);
        }

        // Update version badge
        const card = document.getElementById('kb-summary-card');
        if (card) {
            const badge = card.querySelector('.kb-summary-version');
            if (badge) badge.textContent = `v${summary.version} • ${this._formatDate(summary.date)}`;
        }

        // Update version highlight
        document.querySelectorAll('.kb-version-item').forEach(item => {
            item.classList.toggle('current', parseInt(item.dataset.version) === version);
        });
    },

    /* ── Reprocess ─────────────────────────────────────────────── */

    async _reprocess(topicName) {
        const card = document.getElementById('kb-summary-card');
        const body = card?.querySelector('.kb-summary-card-body');
        if (body) {
            body.innerHTML = `
                <div class="kb-summary-loading">
                    <i class="bi bi-arrow-clockwise"></i>
                    Reprocessing...
                </div>
            `;
        }

        try {
            const detail = this.currentDetail;
            const paths = (detail?.files || []).map(f => f.path);
            if (paths.length === 0) {
                this._showToast('No files to process', 'warning');
                this.showTopicDetail(topicName);
                return;
            }

            const resp = await fetch('/api/kb/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paths })
            });

            if (!resp.ok) {
                this._showToast('Reprocess failed', 'error');
                this.showTopicDetail(topicName);
                return;
            }

            const result = await resp.json();

            // Auto-confirm
            if (result.session_id) {
                const confirmResp = await fetch('/api/kb/process/confirm', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: result.session_id,
                        classifications: result.suggestions
                    })
                });
                if (confirmResp.ok) {
                    this._showToast('Reprocessing complete', 'success');
                }
            }

            // Refresh detail
            this.summaryCache.clear();
            this.showTopicDetail(topicName);
        } catch (err) {
            console.error('[KBTopics] Reprocess error:', err);
            this._showToast('Reprocess error', 'error');
            this.showTopicDetail(topicName);
        }
    },

    /* ── Add Knowledge ─────────────────────────────────────────── */

    _addKnowledge(topicName) {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = '.pdf,.md,.txt,.py,.js,.ts,.json,.html,.css,.java,.docx,.xlsx';
        input.addEventListener('change', async () => {
            if (!input.files || input.files.length === 0) return;
            const formData = new FormData();
            for (const file of input.files) {
                formData.append('files', file);
            }
            formData.append('topic', topicName);

            try {
                const resp = await fetch('/api/kb/upload', {
                    method: 'POST',
                    body: formData
                });
                if (resp.ok) {
                    const result = await resp.json();
                    this._showToast(`${result.uploaded?.length || 0} files uploaded`, 'success');
                    this.showTopicDetail(topicName);
                    if (typeof kbCore !== 'undefined') kbCore.refreshIndex();
                } else {
                    this._showToast('Upload failed', 'error');
                }
            } catch {
                this._showToast('Upload error', 'error');
            }
        });
        input.click();
    },

    /* ── Empty State ───────────────────────────────────────────── */

    _renderEmptyContent() {
        const panel = document.getElementById('kb-topic-detail');
        if (!panel) return;
        panel.innerHTML = `
            <div class="kb-summary-empty" style="padding-top:80px;">
                <i class="bi bi-archive"></i>
                <p>No topics yet.<br>Upload and classify files to create topics.</p>
            </div>
        `;
    },

    /* ── Markdown Rendering ────────────────────────────────────── */

    _renderMarkdown(content) {
        if (!content) return '';
        // Use marked if available, else basic rendering
        if (typeof marked !== 'undefined') {
            try {
                return marked.parse(content);
            } catch { /* fallback below */ }
        }
        // Basic markdown: headings, bold, code, lists, blockquotes
        return this._basicMarkdown(content);
    },

    _basicMarkdown(text) {
        return text
            .split('\n')
            .map(line => {
                if (line.startsWith('#### ')) return `<h4>${this._esc(line.slice(5))}</h4>`;
                if (line.startsWith('### ')) return `<h4>${this._esc(line.slice(4))}</h4>`;
                if (line.startsWith('## ')) return `<h4>${this._esc(line.slice(3))}</h4>`;
                if (line.startsWith('# ')) return `<h4>${this._esc(line.slice(2))}</h4>`;
                if (line.startsWith('> ')) return `<blockquote>${this._esc(line.slice(2))}</blockquote>`;
                if (line.startsWith('- ')) return `<ul><li>${this._inlineFormat(line.slice(2))}</li></ul>`;
                if (line.trim() === '') return '<br>';
                return `<p>${this._inlineFormat(line)}</p>`;
            })
            .join('\n');
    },

    _inlineFormat(text) {
        return this._esc(text)
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    },

    /* ── Toast ─────────────────────────────────────────────────── */

    _showToast(message, type = 'success') {
        const existing = document.querySelector('.kb-topics-toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = `kb-topics-toast ${type}`;
        toast.innerHTML = `<i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : 'exclamation-triangle'}"></i> ${message}`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    },

    /* ── Helpers ────────────────────────────────────────────────── */

    _esc(str) {
        const div = document.createElement('div');
        div.textContent = str || '';
        return div.innerHTML;
    },

    _titleCase(str) {
        return (str || '').split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    },

    _formatSize(bytes) {
        if (!bytes || bytes < 1024) return (bytes || 0) + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },

    _formatDate(isoStr) {
        if (!isoStr) return '—';
        try {
            const d = new Date(isoStr);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        } catch { return isoStr; }
    },

    _relativeTime(isoStr) {
        if (!isoStr) return '—';
        try {
            const d = new Date(isoStr);
            const diff = Date.now() - d.getTime();
            const mins = Math.floor(diff / 60000);
            if (mins < 1) return 'just now';
            if (mins < 60) return `${mins}m ago`;
            const hours = Math.floor(mins / 60);
            if (hours < 24) return `${hours}h ago`;
            const days = Math.floor(hours / 24);
            if (days < 30) return `${days}d ago`;
            return this._formatDate(isoStr);
        } catch { return '—'; }
    }
};

window.kbTopics = kbTopics;
