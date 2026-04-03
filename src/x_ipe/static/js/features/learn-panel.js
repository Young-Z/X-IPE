/**
 * FEATURE-054-A: Workplace Learn Module GUI
 * 
 * LearnPanelManager — Learn panel for behavior tracking sessions.
 * Renders URL input, session list, and integrates with terminal for skill invocation.
 */
class LearnPanelManager {
    constructor() {
        this.container = null;
        this.sessions = [];
        this.pollTimer = null;
    }

    async render(container) {
        this.container = container;
        container.innerHTML = this._getTemplate();
        this._bindEvents();
        await this._loadSessions();
    }

    destroy() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }

    _getTemplate() {
        return `
        <div class="learn-panel">
            <div class="learn-panel-inner">
                <!-- Left: Configuration Panel -->
                <div class="learn-config" style="width: var(--learn-panel-width, 480px); min-width: 280px; max-width: 600px;">
                    <div class="learn-config-header">
                        <h6><i class="bi bi-mortarboard"></i> Behavior Tracking</h6>
                        <p class="text-muted small mb-0">Record user behavior on any website for AI agent training</p>
                    </div>

                    <div class="learn-config-form">
                        <div class="mb-3">
                            <label class="form-label small fw-semibold">Target URL</label>
                            <input type="url" class="form-control form-control-sm" id="learn-url-input"
                                placeholder="https://example.com" autocomplete="url">
                            <div class="invalid-feedback" id="learn-url-error">Please enter a valid URL with protocol (https://)</div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-semibold">Tracking Purpose</label>
                            <textarea class="form-control form-control-sm" id="learn-purpose-input"
                                placeholder="e.g., Checkout flow for AI agent training" rows="3" maxlength="2000"></textarea>
                            <div class="d-flex justify-content-between mt-1">
                                <div class="invalid-feedback d-block" id="learn-purpose-error" style="display:none !important"></div>
                                <small class="text-muted ms-auto" id="learn-purpose-word-count">0 / 200 words</small>
                            </div>
                        </div>

                        <button class="btn btn-sm btn-success w-100" id="learn-track-btn" disabled>
                            <i class="bi bi-record-circle"></i> Track Behavior
                        </button>
                    </div>
                </div>

                <!-- Draggable Divider -->
                <div class="learn-divider" id="learn-divider" title="Drag to resize">
                    <span class="learn-divider-grip">⋮</span>
                </div>

                <!-- Right: Session List -->
                <div class="learn-sessions" style="flex: 1; min-width: 200px;">
                    <div class="learn-sessions-header">
                        <h6><i class="bi bi-clock-history"></i> Sessions</h6>
                    </div>
                    <div class="learn-sessions-list" id="learn-sessions-list">
                        <div class="learn-empty-state">
                            <i class="bi bi-inbox" style="font-size: 2rem; opacity: 0.3;"></i>
                            <p class="text-muted small mt-2">No sessions yet. Start your first tracking session above.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    }

    _bindEvents() {
        const urlInput = document.getElementById('learn-url-input');
        const purposeInput = document.getElementById('learn-purpose-input');
        const trackBtn = document.getElementById('learn-track-btn');
        const divider = document.getElementById('learn-divider');
        const wordCountEl = document.getElementById('learn-purpose-word-count');
        const purposeErrorEl = document.getElementById('learn-purpose-error');

        const updateTrackButton = () => {
            const urlValid = this._validateURL(urlInput?.value);
            const purposeText = purposeInput?.value?.trim() || '';
            const wordCount = purposeText ? purposeText.split(/\s+/).length : 0;
            const purposeValid = purposeText.length > 0 && wordCount <= 200;
            trackBtn.disabled = !(urlValid && purposeValid);
        };

        // URL validation on input
        if (urlInput) {
            urlInput.addEventListener('input', () => {
                const valid = this._validateURL(urlInput.value);
                urlInput.classList.toggle('is-invalid', urlInput.value.length > 0 && !valid);
                urlInput.classList.toggle('is-valid', valid);
                updateTrackButton();
            });
        }

        // Purpose validation + word count
        if (purposeInput) {
            purposeInput.addEventListener('input', () => {
                const text = purposeInput.value.trim();
                const wordCount = text ? text.split(/\s+/).length : 0;
                if (wordCountEl) {
                    wordCountEl.textContent = `${wordCount} / 200 words`;
                    wordCountEl.classList.toggle('text-danger', wordCount > 200);
                    wordCountEl.classList.toggle('text-muted', wordCount <= 200);
                }
                if (purposeErrorEl) {
                    if (wordCount > 200) {
                        purposeErrorEl.textContent = 'Purpose must be 200 words or fewer';
                        purposeErrorEl.style.cssText = 'display:block !important';
                    } else {
                        purposeErrorEl.style.cssText = 'display:none !important';
                    }
                }
                purposeInput.classList.toggle('is-invalid', wordCount > 200);
                updateTrackButton();
            });
        }

        // Track button click
        if (trackBtn) {
            trackBtn.addEventListener('click', () => this._startTracking());
        }

        // Draggable divider
        if (divider) {
            this._setupDividerDrag(divider);
        }
    }

    _validateURL(url) {
        if (!url || !url.trim()) return false;
        try {
            const parsed = new URL(url.trim());
            return ['http:', 'https:'].includes(parsed.protocol) && parsed.hostname.length > 0;
        } catch {
            return false;
        }
    }

    _startTracking() {
        const url = document.getElementById('learn-url-input')?.value?.trim();
        const purpose = document.getElementById('learn-purpose-input')?.value?.trim() || '';
        if (!this._validateURL(url)) return;
        if (!purpose) return;

        // Build skill invocation command
        const purposeArg = ` --purpose "${purpose.replace(/"/g, '\\"')}"`;
        const command = `Track behavior on ${url}${purposeArg}`;

        // Expand terminal panel
        if (window.terminalPanel) {
            window.terminalPanel.expand();
        }

        // Send command to terminal (user reviews before executing)
        if (window.terminalManager?.sendCopilotPromptCommandNoEnter) {
            window.terminalManager.sendCopilotPromptCommandNoEnter(command);
        } else if (window.terminalManager?.sendCopilotPromptCommand) {
            window.terminalManager.sendCopilotPromptCommand(command);
        } else {
            console.log('[LearnPanel] Terminal not available, command:', command);
        }
    }

    async _loadSessions() {
        const listEl = document.getElementById('learn-sessions-list');
        if (!listEl) return;

        try {
            const resp = await fetch('/api/learn/sessions');
            const data = await resp.json();
            if (data.success && data.sessions) {
                this.sessions = data.sessions;
                this._renderSessions(listEl);
            }
        } catch (err) {
            console.warn('[LearnPanel] Failed to load sessions:', err);
        }
    }

    _renderSessions(listEl) {
        if (!this.sessions.length) {
            listEl.innerHTML = `
                <div class="learn-empty-state">
                    <i class="bi bi-inbox" style="font-size: 2rem; opacity: 0.3;"></i>
                    <p class="text-muted small mt-2">No sessions yet. Start your first tracking session.</p>
                </div>`;
            return;
        }

        listEl.innerHTML = this.sessions.map(s => this._renderSessionCard(s)).join('');

        // Bind "View Recording" click handlers
        listEl.querySelectorAll('[data-session-file]').forEach(el => {
            el.addEventListener('click', () => {
                const fileName = el.dataset.sessionFile;
                if (window.contentRenderer && fileName) {
                    window.contentRenderer.renderFile(fileName);
                }
            });
        });
    }

    _renderSessionCard(session) {
        const statusBadge = {
            'recording': '<span class="badge bg-danger"><i class="bi bi-record-fill"></i> Recording</span>',
            'completed': '<span class="badge bg-success">Completed</span>',
            'error': '<span class="badge bg-warning">Error</span>'
        }[session.status] || '<span class="badge bg-secondary">Unknown</span>';

        const elapsed = session.startedAt && session.stoppedAt
            ? this._formatDuration(new Date(session.stoppedAt) - new Date(session.startedAt))
            : session.startedAt ? 'In progress...' : '';

        return `
        <div class="learn-session-card">
            <div class="d-flex justify-content-between align-items-start mb-1">
                <span class="fw-semibold small text-truncate" title="${session.domain}">${session.domain}</span>
                ${statusBadge}
            </div>
            ${session.purpose ? `<div class="text-muted small text-truncate mb-1">${this._escapeHtml(session.purpose)}</div>` : ''}
            <div class="d-flex gap-3 text-muted small">
                <span><i class="bi bi-cursor-fill"></i> ${session.eventCount} events</span>
                <span><i class="bi bi-file-earmark"></i> ${session.pageCount} pages</span>
                ${elapsed ? `<span><i class="bi bi-clock"></i> ${elapsed}</span>` : ''}
            </div>
            ${session.status === 'completed' ? `<button class="btn btn-link btn-sm p-0 mt-1" data-session-file="${this._escapeHtml(session.fileName)}"><i class="bi bi-eye"></i> View Recording</button>` : ''}
        </div>`;
    }

    _formatDuration(ms) {
        if (!ms || ms < 0) return '';
        const s = Math.floor(ms / 1000);
        const m = Math.floor(s / 60);
        const h = Math.floor(m / 60);
        if (h > 0) return `${h}h ${m % 60}m`;
        if (m > 0) return `${m}m ${s % 60}s`;
        return `${s}s`;
    }

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str || '';
        return div.innerHTML;
    }

    _setupDividerDrag(divider) {
        let startX = 0;
        let startWidth = 480;
        const configPanel = divider.previousElementSibling;

        const onMouseMove = (e) => {
            const delta = e.clientX - startX;
            const newWidth = Math.min(600, Math.max(280, startWidth + delta));
            configPanel.style.width = newWidth + 'px';
        };

        const onMouseUp = () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        };

        divider.addEventListener('mousedown', (e) => {
            e.preventDefault();
            startX = e.clientX;
            startWidth = configPanel.getBoundingClientRect().width;
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });
    }
}
