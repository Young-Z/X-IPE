/**
 * FEATURE-023-B: Tracing Dashboard UI
 * 
 * Dashboard component for managing application action tracing.
 * Provides controls for start/stop, countdown timer, and trace list.
 */

// =============================================================================
// TracingDashboard - Main Dashboard Component
// =============================================================================

class TracingDashboard {
    constructor(container) {
        this.container = container;
        this.timerInterval = null;
        this.pollInterval = null;
        this.selectedTraceId = null;
        this.stopAt = null;
        this.config = {};
    }

    // -------------------------------------------------------------------------
    // Lifecycle
    // -------------------------------------------------------------------------

    async init() {
        this.render();
        this.bindEvents();
        await this.fetchStatus();
        await this.refreshTraceList();
        this.startPolling();
    }

    destroy() {
        this.stopCountdown();
        this.stopPolling();
    }

    // -------------------------------------------------------------------------
    // API Methods
    // -------------------------------------------------------------------------

    async fetchStatus() {
        try {
            const response = await fetch('/api/tracing/status');
            if (!response.ok) throw new Error('Failed to fetch status');
            
            this.config = await response.json();
            this.updateUIFromStatus();
        } catch (error) {
            console.error('Error fetching tracing status:', error);
            this.showToast('Failed to load tracing status', 'error');
        }
    }

    async startTracing(durationMinutes) {
        try {
            const response = await fetch('/api/tracing/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ duration_minutes: durationMinutes })
            });
            
            if (!response.ok) throw new Error('Failed to start tracing');
            
            const data = await response.json();
            this.stopAt = new Date(data.stop_at);
            this.startCountdown();
            this.updateDurationButtons(durationMinutes);
            this.showToast(`Tracing started for ${durationMinutes} minutes`, 'success');
        } catch (error) {
            console.error('Error starting tracing:', error);
            this.showToast('Failed to start tracing', 'error');
        }
    }

    async stopTracing() {
        try {
            const response = await fetch('/api/tracing/stop', {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Failed to stop tracing');
            
            this.stopAt = null;
            this.stopCountdown();
            this.updateDurationButtons(null);
            this.updateTimerDisplay();
            this.showToast('Tracing stopped', 'success');
        } catch (error) {
            console.error('Error stopping tracing:', error);
            this.showToast('Failed to stop tracing', 'error');
        }
    }

    async refreshTraceList() {
        try {
            const response = await fetch('/api/tracing/logs');
            if (!response.ok) throw new Error('Failed to fetch trace logs');
            
            const traces = await response.json();
            this.renderTraceList(traces);
        } catch (error) {
            console.error('Error fetching trace logs:', error);
        }
    }

    // -------------------------------------------------------------------------
    // Rendering
    // -------------------------------------------------------------------------

    render() {
        this.container.innerHTML = `
            <div class="tracing-dashboard">
                <div class="tracing-header">
                    <h2>📊 Tracing</h2>
                    <div class="tracing-controls">
                        <button class="btn-config" title="Configuration">⚙️ Config</button>
                        <button class="btn-ignored" title="Ignored APIs">🚫 Ignored APIs</button>
                    </div>
                    <div class="tracing-duration-buttons">
                        <button class="btn-duration" data-minutes="3">3 min</button>
                        <button class="btn-duration" data-minutes="15">15 min</button>
                        <button class="btn-duration" data-minutes="30">30 min</button>
                    </div>
                    <div class="tracing-timer">
                        <span class="timer-display inactive">00:00</span>
                        <button class="btn-stop" style="display: none;">Stop</button>
                    </div>
                </div>
                <div class="tracing-content">
                    <div class="trace-list-sidebar">
                        <div class="trace-list-header">
                            <span>Traces</span>
                            <button class="btn-refresh" title="Refresh">🔄</button>
                        </div>
                        <div class="trace-list-items">
                            <div class="trace-list-empty">
                                <div class="trace-list-empty-icon">📭</div>
                                <div>No traces captured</div>
                                <div>Start tracing to begin</div>
                            </div>
                        </div>
                    </div>
                    <div class="trace-detail-panel">
                        <div class="trace-detail-placeholder">
                            Select a trace to view details
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderTraceList(traces) {
        const listContainer = this.container.querySelector('.trace-list-items');
        
        if (!traces || traces.length === 0) {
            listContainer.innerHTML = `
                <div class="trace-list-empty">
                    <div class="trace-list-empty-icon">📭</div>
                    <div>No traces captured</div>
                    <div>Start tracing to begin</div>
                </div>
            `;
            return;
        }

        // Sort by timestamp descending (newest first)
        traces.sort((a, b) => {
            const timeA = new Date(a.timestamp || a.created || 0);
            const timeB = new Date(b.timestamp || b.created || 0);
            return timeB - timeA;
        });

        listContainer.innerHTML = traces.map(trace => {
            const traceId = trace.trace_id || trace.id || 'unknown';
            const api = trace.api || trace.path || trace.name || 'Unknown API';
            const timestamp = trace.timestamp || trace.created || '';
            const hasError = trace.has_error || trace.status === 'error';
            const statusClass = hasError ? 'error' : 'success';
            const isSelected = traceId === this.selectedTraceId;
            
            // Format timestamp
            let formattedTime = '';
            if (timestamp) {
                const date = new Date(timestamp);
                formattedTime = date.toLocaleTimeString();
            }
            
            // Truncate trace ID
            const shortId = traceId.substring(0, 8);
            
            return `
                <div class="trace-item ${statusClass} ${isSelected ? 'selected' : ''}" 
                     data-trace-id="${traceId}">
                    <div class="trace-item-api">${this.escapeHtml(api)}</div>
                    <div class="trace-item-meta">
                        <span class="trace-item-id">${shortId}...</span>
                        <span class="trace-item-time">${formattedTime}</span>
                    </div>
                </div>
            `;
        }).join('');

        // Rebind click events
        listContainer.querySelectorAll('.trace-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectTrace(item.dataset.traceId);
            });
        });
    }

    // -------------------------------------------------------------------------
    // Timer Logic
    // -------------------------------------------------------------------------

    startCountdown() {
        this.stopCountdown();
        this.updateTimerDisplay();
        
        this.timerInterval = setInterval(() => {
            this.updateTimerDisplay();
            
            // Auto-stop when timer reaches 0
            if (this.stopAt && new Date() >= this.stopAt) {
                this.stopCountdown();
                this.stopAt = null;
                this.updateDurationButtons(null);
                this.updateTimerDisplay();
                this.showToast('Tracing completed', 'success');
            }
        }, 1000);
        
        // Show stop button
        const stopBtn = this.container.querySelector('.btn-stop');
        if (stopBtn) stopBtn.style.display = 'inline-block';
    }

    stopCountdown() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        // Hide stop button
        const stopBtn = this.container.querySelector('.btn-stop');
        if (stopBtn) stopBtn.style.display = 'none';
    }

    updateTimerDisplay() {
        const timerEl = this.container.querySelector('.timer-display');
        if (!timerEl) return;
        
        if (!this.stopAt) {
            timerEl.textContent = '00:00';
            timerEl.className = 'timer-display inactive';
            return;
        }
        
        const now = new Date();
        const remaining = Math.max(0, Math.floor((this.stopAt - now) / 1000));
        
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;
        timerEl.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        
        // Color based on remaining time
        if (remaining <= 0) {
            timerEl.className = 'timer-display inactive';
        } else if (remaining < 60) {
            timerEl.className = 'timer-display warning';
        } else {
            timerEl.className = 'timer-display active';
        }
    }

    updateUIFromStatus() {
        // Check if there's an active tracing session
        const stopAtStr = this.config.stop_at;
        if (stopAtStr && this.config.active) {
            this.stopAt = new Date(stopAtStr);
            if (this.stopAt > new Date()) {
                this.startCountdown();
                // Estimate which duration was selected
                const remaining = (this.stopAt - new Date()) / 1000 / 60;
                if (remaining <= 3) this.updateDurationButtons(3);
                else if (remaining <= 15) this.updateDurationButtons(15);
                else this.updateDurationButtons(30);
            } else {
                this.stopAt = null;
            }
        }
        this.updateTimerDisplay();
    }

    updateDurationButtons(activeMinutes) {
        this.container.querySelectorAll('.btn-duration').forEach(btn => {
            const minutes = parseInt(btn.dataset.minutes);
            btn.classList.toggle('active', minutes === activeMinutes);
        });
    }

    // -------------------------------------------------------------------------
    // Polling
    // -------------------------------------------------------------------------

    startPolling() {
        this.pollInterval = setInterval(() => {
            if (this.stopAt) {
                this.refreshTraceList();
            }
        }, 5000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    // -------------------------------------------------------------------------
    // Event Handling
    // -------------------------------------------------------------------------

    bindEvents() {
        // Duration buttons
        this.container.querySelectorAll('.btn-duration').forEach(btn => {
            btn.addEventListener('click', () => {
                const minutes = parseInt(btn.dataset.minutes);
                this.startTracing(minutes);
            });
        });

        // Stop button
        const stopBtn = this.container.querySelector('.btn-stop');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopTracing());
        }

        // Refresh button
        const refreshBtn = this.container.querySelector('.btn-refresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshTraceList());
        }

        // Config button
        const configBtn = this.container.querySelector('.btn-config');
        if (configBtn) {
            configBtn.addEventListener('click', () => this.openConfigModal());
        }

        // Ignored APIs button
        const ignoredBtn = this.container.querySelector('.btn-ignored');
        if (ignoredBtn) {
            ignoredBtn.addEventListener('click', () => this.openIgnoredModal());
        }
    }

    selectTrace(traceId) {
        this.selectedTraceId = traceId;
        
        // Update selection UI
        this.container.querySelectorAll('.trace-item').forEach(item => {
            item.classList.toggle('selected', item.dataset.traceId === traceId);
        });

        // Update detail panel (placeholder for FEATURE-023-C)
        const detailPanel = this.container.querySelector('.trace-detail-panel');
        if (detailPanel) {
            detailPanel.innerHTML = `
                <div class="trace-detail-placeholder">
                    <div>Trace ID: ${traceId}</div>
                    <div style="margin-top: 0.5rem; font-size: 0.75rem; opacity: 0.6;">
                        DAG visualization coming in FEATURE-023-C
                    </div>
                </div>
            `;
        }
    }

    // -------------------------------------------------------------------------
    // Modals
    // -------------------------------------------------------------------------

    openConfigModal() {
        const modal = new TracingConfigModal(async (config) => {
            await this.updateConfig(config);
        });
        modal.open(this.config);
    }

    async updateConfig(config) {
        try {
            const response = await fetch('/api/tracing/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            
            if (response.ok) {
                this.config = { ...this.config, ...config };
                this.showToast('Configuration saved', 'success');
            } else {
                this.showToast('Failed to save configuration', 'error');
            }
        } catch (error) {
            console.error('Error updating config:', error);
            this.showToast('Failed to save configuration', 'error');
        }
    }

    openIgnoredModal() {
        const modal = new TracingIgnoredModal(async (patterns) => {
            await this.updateIgnoredApis(patterns);
        });
        modal.open(this.config.ignored_apis || []);
    }

    async updateIgnoredApis(patterns) {
        try {
            const response = await fetch('/api/tracing/ignored', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ patterns })
            });
            
            if (response.ok) {
                this.config.ignored_apis = patterns;
                this.showToast('Ignored APIs updated', 'success');
            } else {
                this.showToast('Failed to update ignored APIs', 'error');
            }
        } catch (error) {
            console.error('Error updating ignored APIs:', error);
            this.showToast('Failed to update ignored APIs', 'error');
        }
    }

    // -------------------------------------------------------------------------
    // Utilities
    // -------------------------------------------------------------------------

    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `tracing-toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}


// =============================================================================
// TracingConfigModal - Configuration Modal
// =============================================================================

class TracingConfigModal {
    constructor(onSave) {
        this.onSave = onSave;
        this.overlay = null;
    }

    open(currentConfig) {
        this.overlay = document.createElement('div');
        this.overlay.className = 'tracing-modal-overlay';
        this.overlay.innerHTML = `
            <div class="tracing-modal">
                <div class="tracing-modal-header">
                    <h3>Tracing Configuration</h3>
                    <button class="tracing-modal-close">&times;</button>
                </div>
                <div class="tracing-modal-body">
                    <div class="tracing-form-group">
                        <label>Retention Hours</label>
                        <input type="number" id="retention-hours" min="1" max="168" 
                               value="${currentConfig.retention_hours || 24}">
                    </div>
                    <div class="tracing-form-group">
                        <label>Log Path</label>
                        <input type="text" id="log-path" 
                               value="${currentConfig.log_path || 'instance/traces/'}">
                    </div>
                </div>
                <div class="tracing-modal-footer">
                    <button class="btn-secondary btn-cancel">Cancel</button>
                    <button class="btn-primary btn-save">Save</button>
                </div>
            </div>
        `;

        document.body.appendChild(this.overlay);
        this.bindEvents();
    }

    bindEvents() {
        this.overlay.querySelector('.tracing-modal-close').addEventListener('click', () => this.close());
        this.overlay.querySelector('.btn-cancel').addEventListener('click', () => this.close());
        this.overlay.querySelector('.btn-save').addEventListener('click', () => this.handleSave());
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });
    }

    handleSave() {
        const retentionHours = parseInt(this.overlay.querySelector('#retention-hours').value);
        const logPath = this.overlay.querySelector('#log-path').value;
        
        this.onSave({ retention_hours: retentionHours, log_path: logPath });
        this.close();
    }

    close() {
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }
}


// =============================================================================
// TracingIgnoredModal - Ignored APIs Modal
// =============================================================================

class TracingIgnoredModal {
    constructor(onSave) {
        this.onSave = onSave;
        this.overlay = null;
        this.patterns = [];
    }

    open(patterns) {
        this.patterns = [...patterns];
        
        this.overlay = document.createElement('div');
        this.overlay.className = 'tracing-modal-overlay';
        this.render();
        document.body.appendChild(this.overlay);
        this.bindEvents();
    }

    render() {
        this.overlay.innerHTML = `
            <div class="tracing-modal">
                <div class="tracing-modal-header">
                    <h3>Ignored APIs</h3>
                    <button class="tracing-modal-close">&times;</button>
                </div>
                <div class="tracing-modal-body">
                    <p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 1rem;">
                        API patterns that will be excluded from tracing.
                    </p>
                    <div class="ignored-apis-list">
                        ${this.patterns.map((pattern, i) => `
                            <div class="ignored-api-item">
                                <span>${this.escapeHtml(pattern)}</span>
                                <button data-index="${i}" title="Remove">×</button>
                            </div>
                        `).join('')}
                    </div>
                    <div class="add-ignored-api">
                        <input type="text" id="new-pattern" placeholder="/api/health/*">
                        <button class="btn-secondary btn-add">Add</button>
                    </div>
                </div>
                <div class="tracing-modal-footer">
                    <button class="btn-secondary btn-cancel">Cancel</button>
                    <button class="btn-primary btn-save">Save</button>
                </div>
            </div>
        `;
    }

    bindEvents() {
        this.overlay.querySelector('.tracing-modal-close').addEventListener('click', () => this.close());
        this.overlay.querySelector('.btn-cancel').addEventListener('click', () => this.close());
        this.overlay.querySelector('.btn-save').addEventListener('click', () => this.handleSave());
        this.overlay.querySelector('.btn-add').addEventListener('click', () => this.addPattern());
        
        // Remove buttons
        this.overlay.querySelectorAll('.ignored-api-item button').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.index);
                this.removePattern(index);
            });
        });

        // Enter key to add
        this.overlay.querySelector('#new-pattern').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addPattern();
        });

        // Click outside to close
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });
    }

    addPattern() {
        const input = this.overlay.querySelector('#new-pattern');
        const pattern = input.value.trim();
        if (pattern && !this.patterns.includes(pattern)) {
            this.patterns.push(pattern);
            this.render();
            this.bindEvents();
        }
    }

    removePattern(index) {
        this.patterns.splice(index, 1);
        this.render();
        this.bindEvents();
    }

    handleSave() {
        this.onSave(this.patterns);
        this.close();
    }

    close() {
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}


// =============================================================================
// Export for module usage
// =============================================================================

if (typeof window !== 'undefined') {
    window.TracingDashboard = TracingDashboard;
    window.TracingConfigModal = TracingConfigModal;
    window.TracingIgnoredModal = TracingIgnoredModal;
}
