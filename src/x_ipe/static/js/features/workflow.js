/**
 * FEATURE-036-B: Engineering Workflow View Shell & CRUD
 *
 * Renders workflow list, create modal, delete actions.
 * All API calls go to /api/workflow/* (FEATURE-036-A).
 */
const workflow = {
    container: null,
    expandedPanels: new Set(),
    isSubmitting: false,
    _pollingIntervals: {},
    _lastActivity: {},

    /** Entry point — render the full workflow view into container. */
    render(container) {
        this.container = container;
        container.innerHTML = '';
        container.className = 'workflow-view';

        container.appendChild(this._renderHeader());

        const panelsDiv = document.createElement('div');
        panelsDiv.className = 'workflow-panels';
        panelsDiv.id = 'workflow-panels';
        container.appendChild(panelsDiv);

        this._loadList();
    },

    /** Fetch and render workflow list. */
    async _loadList() {
        const panelsDiv = document.getElementById('workflow-panels');
        if (!panelsDiv) return;
        panelsDiv.innerHTML = '<p style="color:#94a3b8;text-align:center;padding:2rem">Loading…</p>';

        try {
            const resp = await fetch('/api/workflow/list');
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const json = await resp.json();
            const workflows = json.data || [];
            panelsDiv.innerHTML = '';

            if (workflows.length === 0) {
                panelsDiv.appendChild(this._renderEmptyState());
            } else {
                // Auto-expand the most recently active workflow on initial load
                if (this.expandedPanels.size === 0 && workflows.length > 0) {
                    const sorted = [...workflows].filter(w => w.last_activity).sort((a, b) =>
                        new Date(b.last_activity) - new Date(a.last_activity)
                    );
                    if (sorted.length > 0) {
                        this.expandedPanels.add(sorted[0].name);
                    }
                }
                workflows.forEach(wf => panelsDiv.appendChild(this._renderPanel(wf)));
            }
        } catch (e) {
            panelsDiv.innerHTML = '';
            const errDiv = document.createElement('div');
            errDiv.className = 'workflow-empty';
            errDiv.innerHTML = `<i class="bi bi-exclamation-triangle"></i>
                <h5>Cannot load workflows</h5>
                <p>${e.message}</p>
                <button class="workflow-btn-create" style="margin-top:1rem">Retry</button>`;
            errDiv.querySelector('button').onclick = () => this._loadList();
            panelsDiv.appendChild(errDiv);
        }
    },

    _renderHeader() {
        const header = document.createElement('div');
        header.className = 'workflow-header';
        header.innerHTML = `<div><h2>Engineering Workflows</h2><p class="workflow-header-sub">Manage your project delivery lifecycle from ideation to feedback</p></div>`;
        const btn = document.createElement('button');
        btn.className = 'workflow-btn-create';
        btn.innerHTML = '<i class="bi bi-plus-lg"></i> Create Workflow';
        btn.onclick = () => this._showCreateModal();
        header.appendChild(btn);
        return header;
    },

    _renderPanel(wf) {
        const panel = document.createElement('div');
        panel.className = 'workflow-panel';
        if (this.expandedPanels.has(wf.name)) panel.classList.add('expanded');

        // Header
        const header = document.createElement('div');
        header.className = 'workflow-panel-header';

        const info = document.createElement('div');
        info.className = 'workflow-panel-info';

        const icon = document.createElement('div');
        icon.className = 'workflow-panel-icon';
        icon.textContent = '⚡';
        info.appendChild(icon);

        const name = document.createElement('span');
        name.className = 'workflow-panel-name';
        name.textContent = wf.name;
        name.title = wf.name;
        info.appendChild(name);

        const meta = document.createElement('span');
        meta.className = 'workflow-panel-meta';
        const createdDate = wf.created ? new Date(wf.created) : null;
        const fmtDate = createdDate ? `Created ${createdDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}` : '';
        if (fmtDate) meta.innerHTML = `<span>${fmtDate}</span>`;
        const fc = wf.feature_count || 0;
        meta.innerHTML += `<span class="meta-dot">·</span><span>${fc} feature${fc !== 1 ? 's' : ''}</span>`;
        meta.innerHTML += `<span class="meta-dot">·</span><span class="meta-stage">${wf.current_stage} Stage</span>`;
        info.appendChild(meta);
        header.appendChild(info);

        // Auto-Proceed dropdown + Action button (⋮)
        const actionsWrap = document.createElement('div');
        actionsWrap.className = 'workflow-panel-actions';

        // Auto-Proceed dropdown
        const currentMode = wf.auto_proceed || 'manual';
        const modeLabels = { manual: 'Manual', auto: 'Auto', stop_for_question: 'Stop for Q' };
        const modeIcons = { manual: 'bi-hand-index', auto: 'bi-lightning-charge-fill', stop_for_question: 'bi-pause-circle' };
        const modeBadges = { manual: 'text-bg-secondary', auto: 'text-bg-success', stop_for_question: 'text-bg-warning' };
        const apWrap = document.createElement('div');
        apWrap.className = 'dropdown d-inline-block auto-proceed-header';
        apWrap.innerHTML = `
            <button class="btn btn-sm btn-outline-secondary dropdown-toggle auto-proceed-btn" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="bi ${modeIcons[currentMode]}"></i> <span class="badge ${modeBadges[currentMode]}">${modeLabels[currentMode]}</span>
            </button>
            <ul class="dropdown-menu dropdown-menu-dark">
                <li><button class="dropdown-item${currentMode === 'manual' ? ' active' : ''}" data-mode="manual"><i class="bi bi-hand-index"></i> Manual</button></li>
                <li><button class="dropdown-item${currentMode === 'auto' ? ' active' : ''}" data-mode="auto"><i class="bi bi-lightning-charge-fill"></i> Auto</button></li>
                <li><button class="dropdown-item${currentMode === 'stop_for_question' ? ' active' : ''}" data-mode="stop_for_question"><i class="bi bi-pause-circle"></i> Stop for Question</button></li>
            </ul>`;
        const btnLabel = apWrap.querySelector('.dropdown-toggle');
        apWrap.querySelectorAll('.dropdown-item').forEach(item => {
            item.onclick = async (e) => {
                e.stopPropagation();
                const mode = item.dataset.mode;
                try {
                    const resp = await fetch(`/api/workflow/${encodeURIComponent(wf.name)}/settings`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ process_preference: { auto_proceed: mode } })
                    });
                    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                    apWrap.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('active'));
                    item.classList.add('active');
                    btnLabel.innerHTML = `<i class="bi ${modeIcons[mode]}"></i> <span class="badge ${modeBadges[mode]}">${modeLabels[mode]}</span>`;
                } catch (e) { /* revert silently */ }
            };
        });
        apWrap.onclick = (e) => e.stopPropagation();
        actionsWrap.appendChild(apWrap);

        const actBtn = document.createElement('button');
        actBtn.className = 'workflow-action-btn';
        actBtn.innerHTML = '⋮';
        actBtn.title = 'Actions';
        actBtn.onclick = (e) => { e.stopPropagation(); this._toggleMenu(actionsWrap); };
        actionsWrap.appendChild(actBtn);

        const menu = document.createElement('div');
        menu.className = 'workflow-action-menu';
        const delBtn = document.createElement('button');
        delBtn.innerHTML = '<i class="bi bi-trash"></i> Delete';
        delBtn.onclick = (e) => { e.stopPropagation(); menu.classList.remove('open'); this._handleDelete(wf.name); };
        menu.appendChild(delBtn);
        actionsWrap.appendChild(menu);
        header.appendChild(actionsWrap);

        // Body
        const body = document.createElement('div');
        body.className = 'workflow-panel-body';

        header.onclick = async () => {
            const exp = panel.classList.toggle('expanded');
            if (exp) {
                this.expandedPanels.add(wf.name);
                body.innerHTML = '';
                await this._renderPanelBody(wf, body);
                this._startPolling(wf.name, wf, body);
            } else {
                this.expandedPanels.delete(wf.name);
                this._stopPolling(wf.name);
            }
        };
        panel.appendChild(header);
        panel.appendChild(body);

        // Auto-load body if already expanded
        if (this.expandedPanels.has(wf.name)) {
            this._renderPanelBody(wf, body);
            this._startPolling(wf.name, wf, body);
        }

        return panel;
    },

    async _renderPanelBody(wf, body) {
        try {
            const [stateResp, nextResp] = await Promise.all([
                fetch(`/api/workflow/${encodeURIComponent(wf.name)}`).then(r => r.json()),
                fetch(`/api/workflow/${encodeURIComponent(wf.name)}/next-action`).then(r => r.json())
            ]);
            if (stateResp.success && typeof workflowStage !== 'undefined') {
                this._lastActivity[wf.name] = stateResp.data.last_activity || '';
                workflowStage.render(body, stateResp.data, nextResp.data, wf.name);
            }
        } catch (err) {
            body.innerHTML = `<div class="workflow-error">Failed to load workflow details. <button>Retry</button></div>`;
            body.querySelector('button').onclick = () => { body.innerHTML = ''; this._renderPanelBody(wf, body); };
        }
        // Metadata
        const meta = document.createElement('div');
        meta.className = 'workflow-panel-meta-section';
        const created = wf.created ? new Date(wf.created).toLocaleDateString() : 'N/A';
        const lastAct = wf.last_activity ? new Date(wf.last_activity).toLocaleString() : 'N/A';
        meta.innerHTML = `
            <div class="workflow-panel-body-row"><span class="workflow-panel-body-label">Created</span><span>${created}</span></div>
            <div class="workflow-panel-body-row"><span class="workflow-panel-body-label">Last Activity</span><span>${lastAct}</span></div>`;
        body.appendChild(meta);
    },

    _renderEmptyState() {
        const div = document.createElement('div');
        div.className = 'workflow-empty';
        div.innerHTML = `<i class="bi bi-diagram-3"></i>
            <h5>No workflows yet</h5>
            <p>Create one to get started</p>`;
        return div;
    },

    _toggleMenu(wrap) {
        const menu = wrap.querySelector('.workflow-action-menu');
        const opening = !menu.classList.contains('open');
        document.querySelectorAll('.workflow-action-menu.open').forEach(m => m.classList.remove('open'));
        if (opening) menu.classList.add('open');
        const close = (e) => { if (!wrap.contains(e.target)) { menu.classList.remove('open'); document.removeEventListener('click', close); } };
        if (opening) setTimeout(() => document.addEventListener('click', close), 0);
    },

    /** Show create workflow modal. */
    _showCreateModal() {
        const overlay = document.createElement('div');
        overlay.className = 'workflow-modal-overlay';

        const modal = document.createElement('div');
        modal.className = 'workflow-modal';
        modal.innerHTML = `
            <div class="workflow-modal-header">
                <span class="workflow-modal-title">Create New Workflow</span>
                <button class="workflow-modal-close" id="wf-create-close">×</button>
            </div>
            <div class="workflow-modal-body">
                <label class="workflow-modal-label">Workflow Name</label>
                <input type="text" id="wf-create-name" placeholder="e.g., E-Commerce Checkout Flow" maxlength="100" autocomplete="off" />
                <div class="workflow-modal-hint">Choose a descriptive name for your project delivery workflow</div>
                <div class="workflow-modal-error" id="wf-create-error"></div>
            </div>
            <div class="workflow-modal-actions">
                <button id="wf-create-cancel" class="btn-cancel">Cancel</button>
                <button id="wf-create-submit" class="btn-primary">Create Workflow</button>
            </div>`;
        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        const nameInput = document.getElementById('wf-create-name');
        const errDiv = document.getElementById('wf-create-error');
        const submitBtn = document.getElementById('wf-create-submit');
        const cancelBtn = document.getElementById('wf-create-cancel');

        nameInput.focus();

        const namePattern = /^[\p{L}\p{N}_-]+$/u;
        const validate = () => {
            const v = nameInput.value.trim();
            if (!v) { errDiv.textContent = 'Name is required'; return false; }
            if (!namePattern.test(v)) { errDiv.textContent = 'Only letters, numbers, hyphens, and underscores allowed'; return false; }
            if (v.length > 100) { errDiv.textContent = 'Max 100 characters'; return false; }
            errDiv.textContent = '';
            return true;
        };

        nameInput.oninput = validate;
        nameInput.onkeydown = (e) => { if (e.key === 'Enter') submitBtn.click(); };

        cancelBtn.onclick = () => overlay.remove();
        document.getElementById('wf-create-close').onclick = () => overlay.remove();
        overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };

        submitBtn.onclick = async () => {
            if (!validate() || this.isSubmitting) return;
            this.isSubmitting = true;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating…';

            try {
                const resp = await fetch('/api/workflow/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: nameInput.value.trim() }),
                });
                const json = await resp.json();
                if (resp.ok && json.success) {
                    overlay.remove();
                    this._loadList();
                } else {
                    errDiv.textContent = json.message || json.error || 'Failed to create workflow';
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Create';
                }
            } catch (e) {
                let msg = 'Network error — please try again';
                if (e instanceof SyntaxError) {
                    msg = 'Server error — please check logs';
                }
                errDiv.textContent = msg;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create';
            } finally {
                this.isSubmitting = false;
            }
        };
    },

    async _handleDelete(name) {
        const confirmed = await this._showConfirmModal(`Delete workflow '${name}'?`, 'This cannot be undone.');
        if (!confirmed) return;
        try {
            const resp = await fetch(`/api/workflow/${encodeURIComponent(name)}`, { method: 'DELETE' });
            const json = await resp.json();
            if (resp.ok && json.success) {
                this.expandedPanels.delete(name);
                this._loadList();
            } else {
                this._showToast(json.message || 'Failed to delete', 'error');
            }
        } catch (e) {
            this._showToast('Network error', 'error');
        }
    },

    _showToast(msg, type) {
        const toast = document.createElement('div');
        toast.className = `workflow-toast ${type || 'error'}`;
        toast.textContent = msg;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    },

    /** Show a confirm modal (replaces native confirm()). Returns a Promise<boolean>. */
    _showConfirmModal(title, message) {
        return new Promise(resolve => {
            const overlay = document.createElement('div');
            overlay.className = 'workflow-modal-overlay';

            const modal = document.createElement('div');
            modal.className = 'workflow-modal';
            modal.innerHTML = `
                <h3>${title}</h3>
                <p style="color:#94a3b8;margin:8px 0 16px">${message}</p>
                <div class="workflow-modal-actions">
                    <button id="wf-confirm-cancel">Cancel</button>
                    <button id="wf-confirm-ok" class="btn-primary btn-danger">Delete</button>
                </div>`;
            overlay.appendChild(modal);
            document.body.appendChild(overlay);

            const cleanup = (result) => { overlay.remove(); resolve(result); };
            document.getElementById('wf-confirm-cancel').onclick = () => cleanup(false);
            document.getElementById('wf-confirm-ok').onclick = () => cleanup(true);
            overlay.onclick = (e) => { if (e.target === overlay) cleanup(false); };
        });
    },

    /** Start polling for workflow state changes (FEATURE-036-E). */
    _startPolling(wfName, wf, body) {
        this._stopPolling(wfName);
        this._pollingIntervals[wfName] = setInterval(async () => {
            try {
                const resp = await fetch(`/api/workflow/${encodeURIComponent(wfName)}`);
                const json = await resp.json();
                if (!json.success) return;
                const newLA = json.data.last_activity || '';
                if (newLA && newLA !== this._lastActivity[wfName]) {
                    this._lastActivity[wfName] = newLA;
                    body.innerHTML = '';
                    await this._renderPanelBody(wf, body);
                }
            } catch { /* silently skip */ }
        }, 7000);
    },

    /** Stop polling for a workflow (FEATURE-036-E). */
    _stopPolling(wfName) {
        if (this._pollingIntervals[wfName]) {
            clearInterval(this._pollingIntervals[wfName]);
            delete this._pollingIntervals[wfName];
        }
    },

    _stopAllPolling() {
        Object.keys(this._pollingIntervals).forEach(k => this._stopPolling(k));
    },
};
