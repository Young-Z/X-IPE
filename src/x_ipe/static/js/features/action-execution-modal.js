/**
 * FEATURE-038-A: Action Execution Modal
 *
 * Reusable modal for CLI Agent workflow actions.
 * Loads instructions from copilot-prompt.json, accepts extra instructions,
 * constructs CLI command, dispatches to terminal via idle session detection.
 */
class ActionExecutionModal {
    constructor({ actionKey, workflowName, skillName, onComplete, status, triggerBtn, featureId }) {
        this.actionKey = actionKey;
        this.workflowName = workflowName;
        this.skillName = skillName || '';
        this.onComplete = onComplete || (() => {});
        this.status = status || null;
        this.triggerBtn = triggerBtn || null;
        this.featureId = featureId || null;
        this.overlay = null;
        this._loadedInstructions = null;
        this._keyHandler = null;
        this._templateCache = null;
        this._actionContextDef = null;
    }

    /* --- Lifecycle -------------------------------------------------------- */

    async open() {
        await this._loadInstructions();
        this._createDOM();
        this._bindEvents();
        document.body.appendChild(this.overlay);

        // Template-driven action context (FEATURE-041-F)
        if (this.workflowName) {
            try {
                const template = await this._fetchTemplate();
                const actionDef = this._getActionDef(template, this.actionKey);
                if (actionDef && actionDef.action_context) {
                    this._actionContextDef = actionDef.action_context;
                    // Hide legacy input file section when action_context is present
                    const legacyInput = this.overlay.querySelector('.input-selector-section');
                    if (legacyInput) legacyInput.style.display = 'none';
                    await this._renderActionContext(actionDef.action_context);
                    // Reopen: if action was done, restore previous context
                    const instance = await this._fetchInstance();
                    if (instance) {
                        const ctx = this._getInstanceContext(instance, this.actionKey, this.featureId);
                        if (ctx) await this._restoreContext(ctx);
                    }
                }
            } catch (e) { /* fallback to legacy */ }
        }
    }

    close() {
        if (this._keyHandler) {
            document.removeEventListener('keydown', this._keyHandler);
            this._keyHandler = null;
        }
        if (this.overlay && this.overlay.parentNode) {
            this.overlay.remove();
        }
        this.overlay = null;
    }

    /* --- Instructions Loading --------------------------------------------- */

    async _loadInstructions() {
        let config = window.__copilotPromptConfig;
        if (!config) {
            try {
                const resp = await fetch('/api/config/copilot-prompt');
                if (resp.ok) {
                    config = await resp.json();
                    window.__copilotPromptConfig = config;
                }
            } catch (e) { /* ignore */ }
        }
        if (!config) return;

        const entry = this._getConfigEntry(config);
        if (!entry) return;

        const detail = entry['prompt-details'].find(d => d.language === 'en')
            || entry['prompt-details'][0];
        let command = detail.command;

        // Resolve input files from input_source or legacy <current-idea-file>
        const hasInputPlaceholder = command.includes('<input-file>') || command.includes('<current-idea-file>');
        if (hasInputPlaceholder && this.workflowName) {
            if (entry.input_source) {
                this._inputFiles = await this._resolveInputFiles(entry.input_source);
            } else {
                this._inputFiles = await this._resolveIdeaFiles();
            }
            this._commandTemplate = command;
            const selected = this._inputFiles.length ? this._inputFiles[0] : null;
            this._selectedInputFile = selected;
            if (selected) {
                command = command.replace(/<input-file>|<current-idea-file>/g, selected);
            }
        }

        // Replace <feature-id> placeholder with actual feature ID
        if (this.featureId && command.includes('<feature-id>')) {
            command = command.replace(/<feature-id>/g, this.featureId);
        }

        this._loadedInstructions = { label: detail.label, command };
    }

    async _resolveIdeaFiles() {
        const files = [];
        try {
            const resp = await fetch(`/api/workflow/${encodeURIComponent(this.workflowName)}`);
            if (!resp.ok) return files;
            const json = await resp.json();
            const data = json.data || {};
            const stages = data.stages || data.shared || {};
            const composeAction = (stages.ideation && stages.ideation.actions && stages.ideation.actions.compose_idea) || {};
            const deliverables = composeAction.deliverables || [];
            // Add compose_idea .md deliverable as primary option
            const primaryMd = deliverables.find(d => d.endsWith('.md'));
            if (primaryMd) files.push(primaryMd);
            // Find the idea folder and look for refined-idea/ subfolder
            const ideaFolder = deliverables.find(d => !d.endsWith('.md')) || (primaryMd ? primaryMd.substring(0, primaryMd.lastIndexOf('/')) : null);
            if (ideaFolder) {
                const refinedPath = ideaFolder.endsWith('/') ? `${ideaFolder}refined-idea` : `${ideaFolder}/refined-idea`;
                try {
                    const treeResp = await fetch(`/api/workflow/${encodeURIComponent(this.workflowName)}/deliverables/tree?path=${encodeURIComponent(refinedPath)}`);
                    if (treeResp.ok) {
                        const treeJson = await treeResp.json();
                        const entries = Array.isArray(treeJson) ? treeJson : (treeJson.data || treeJson.entries || []);
                        for (const entry of entries) {
                            if (entry.type === 'file' && entry.path && entry.path.endsWith('.md')) {
                                if (!files.includes(entry.path)) files.push(entry.path);
                            }
                        }
                    }
                } catch (e) { /* refined-idea folder may not exist */ }
            }
        } catch (e) { /* ignore */ }
        return files;
    }

    _getConfigEntry(config) {
        const configId = this.actionKey.replace(/_/g, '-');
        for (const [, sectionData] of Object.entries(config)) {
            if (sectionData && sectionData.prompts) {
                const found = sectionData.prompts.find(p => p.id === configId);
                if (found) return found;
            }
            if (sectionData && sectionData.id === configId) return sectionData;
            if (Array.isArray(sectionData)) {
                const found = sectionData.find(p => p.id === configId);
                if (found) return found;
            }
        }
        return null;
    }

    async _resolveInputFiles(inputSource) {
        const files = [];
        try {
            const resp = await fetch(`/api/workflow/${encodeURIComponent(this.workflowName)}`);
            if (!resp.ok) return files;
            const json = await resp.json();
            const data = json.data || {};
            const shared = data.stages || data.shared || {};
            const featureData = this.featureId && data.features
                ? (Array.isArray(data.features)
                    ? data.features.find(f => f.feature_id === this.featureId)
                    : data.features[this.featureId])
                : null;

            for (const sourceAction of inputSource) {
                let actionObj = null;

                // 1. Per-feature stages (if featureId present)
                if (featureData) {
                    for (const stage of ['implement', 'validation', 'feedback']) {
                        const stageData = featureData[stage];
                        actionObj = (stageData && stageData.actions || {})[sourceAction];
                        if (actionObj && actionObj.deliverables && actionObj.deliverables.length) break;
                        actionObj = null;
                    }
                }

                // 2. Fallback to shared stages
                if (!actionObj) {
                    for (const [, stageData] of Object.entries(shared)) {
                        actionObj = (stageData.actions || {})[sourceAction];
                        if (actionObj && actionObj.deliverables && actionObj.deliverables.length) break;
                        actionObj = null;
                    }
                }

                if (!actionObj || !actionObj.deliverables) continue;

                for (const d of actionObj.deliverables) {
                    if (d.endsWith('.md') && !files.includes(d)) {
                        files.push(d);
                    }
                    // Scan folder deliverables
                    if (!d.includes('.')) {
                        try {
                            const treeResp = await fetch(
                                `/api/workflow/${encodeURIComponent(this.workflowName)}/deliverables/tree?path=${encodeURIComponent(d)}`
                            );
                            if (treeResp.ok) {
                                const treeJson = await treeResp.json();
                                const entries = Array.isArray(treeJson) ? treeJson : (treeJson.data || treeJson.entries || []);
                                for (const entry of entries) {
                                    if (entry.type === 'file' && entry.path && entry.path.endsWith('.md')) {
                                        if (!files.includes(entry.path)) files.push(entry.path);
                                    }
                                }
                            }
                        } catch (e) { /* folder may not exist */ }
                    }
                }
            }
        } catch (e) { /* ignore */ }
        return files;
    }

    /* --- Template-Driven Action Context (FEATURE-041-F) -------------------- */

    async _fetchTemplate() {
        if (this._templateCache) return this._templateCache;
        const resp = await fetch('/api/workflow/template');
        if (resp.ok) this._templateCache = await resp.json();
        return this._templateCache || {};
    }

    _getActionDef(template, actionKey) {
        if (!template || !template.stages) return null;
        for (const stage of Object.values(template.stages)) {
            if (stage.actions && stage.actions[actionKey]) {
                return stage.actions[actionKey];
            }
        }
        return null;
    }

    async _fetchInstance() {
        try {
            const resp = await fetch(`/api/workflow/${encodeURIComponent(this.workflowName)}`);
            if (!resp.ok) return null;
            const json = await resp.json();
            return json.data || json;
        } catch { return null; }
    }

    _getInstanceContext(instance, actionKey, featureId) {
        if (!instance) return null;
        const shared = instance.shared || {};
        // Search shared stages
        for (const stageData of Object.values(shared)) {
            const action = (stageData.actions || {})[actionKey];
            if (action && action.context) return action.context;
        }
        // Search feature lanes
        if (featureId && instance.features) {
            const feat = Array.isArray(instance.features)
                ? instance.features.find(f => f.feature_id === featureId)
                : instance.features[featureId];
            if (feat) {
                for (const stage of ['implement', 'validation', 'feedback']) {
                    const action = (feat[stage] && feat[stage].actions || {})[actionKey];
                    if (action && action.context) return action.context;
                }
            }
        }
        return null;
    }

    async _renderActionContext(actionContextDef) {
        // Find or create the action context section
        let container = this.overlay.querySelector('.input-files-section, .action-context-section');
        if (!container) {
            container = document.createElement('div');
            container.className = 'action-context-section';
            const body = this.overlay.querySelector('.modal-body');
            if (body) {
                const instrSection = body.querySelector('.instructions-section');
                if (instrSection) body.insertBefore(container, instrSection);
                else body.appendChild(container);
            }
        }
        container.className = 'action-context-section';
        container.innerHTML = '';

        const heading = document.createElement('h4');
        heading.textContent = 'Action Context';
        container.appendChild(heading);

        for (const [refName, refDef] of Object.entries(actionContextDef)) {
            const group = this._createDropdownGroup(refName, refDef);
            container.appendChild(group);

            if (refDef.candidates) {
                await this._populateDropdown(group.querySelector('select'), refDef.candidates);
            }
        }
    }

    _createDropdownGroup(refName, refDef) {
        const group = document.createElement('div');
        group.className = 'context-ref-group';
        group.dataset.refName = refName;

        const label = document.createElement('label');
        label.textContent = refName.replace(/-/g, ' ');
        if (refDef.required) {
            label.innerHTML += ' <span class="required">*</span>';
        } else {
            label.innerHTML += ' <span class="optional">(optional)</span>';
        }
        group.appendChild(label);

        const select = document.createElement('select');
        select.name = refName;
        select.required = refDef.required;
        select.add(new Option('auto-detect', 'auto-detect'));
        if (!refDef.required) {
            select.add(new Option('N/A', 'N/A'));
        }
        group.appendChild(select);
        return group;
    }

    async _populateDropdown(selectEl, candidatesName) {
        try {
            const url = `/api/workflow/${encodeURIComponent(this.workflowName)}/candidates/${encodeURIComponent(this.actionKey)}/${encodeURIComponent(candidatesName)}`;
            const params = this.featureId ? `?feature_id=${encodeURIComponent(this.featureId)}` : '';
            const resp = await fetch(url + params);
            if (!resp.ok) return;
            const results = await resp.json();

            for (const result of results) {
                if (result.type === 'file') {
                    selectEl.add(new Option(result.path, result.path));
                } else if (result.type === 'folder') {
                    const files = await this._listFolderContents(result.path);
                    for (const file of files) {
                        selectEl.add(new Option(file, file));
                    }
                }
            }
        } catch (e) { /* ignore */ }
    }

    async _listFolderContents(folderPath) {
        try {
            const resp = await fetch(`/api/workflow/${encodeURIComponent(this.workflowName)}/folder-contents?path=${encodeURIComponent(folderPath)}`);
            if (resp.ok) return await resp.json();
        } catch { /* ignore */ }
        return [];
    }

    async _saveContext() {
        const context = {};
        const groups = this.overlay ? this.overlay.querySelectorAll('.context-ref-group') : [];
        for (const group of groups) {
            const refName = group.dataset.refName;
            const select = group.querySelector('select');
            if (select) context[refName] = select.value;
        }

        await fetch(`/api/workflow/${encodeURIComponent(this.workflowName)}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: this.actionKey,
                status: 'in_progress',
                feature_id: this.featureId,
                context: context
            })
        });

        return context;
    }

    async _restoreContext(instanceContext) {
        if (!instanceContext) return;
        for (const [refName, value] of Object.entries(instanceContext)) {
            const group = this.overlay.querySelector(`[data-ref-name="${refName}"]`);
            if (!group) continue;
            const select = group.querySelector('select');
            if (!select) continue;
            const option = Array.from(select.options).find(o => o.value === value);
            if (option) {
                select.value = value;
            } else if (value && value !== 'auto-detect' && value !== 'N/A') {
                const missingOpt = new Option(`${value} (missing)`, value);
                select.add(missingOpt);
                select.value = value;
            }
        }
    }

    /* --- DOM Creation ----------------------------------------------------- */

    _createDOM() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'modal-overlay';

        const isInProgress = this.status === 'in_progress';
        const hasInstructions = !!this._loadedInstructions;
        const title = this._loadedInstructions
            ? this._loadedInstructions.label
            : this._formatActionKey(this.actionKey);

        this.overlay.innerHTML = `
            <div class="modal-container">
                <div class="modal-header">
                    <span class="modal-title">${this._escapeHtml(title)}</span>
                    <button class="modal-close-btn" title="Close">&times;</button>
                </div>
                <div class="modal-body">
                    ${isInProgress ? `
                        <div class="in-progress-message">
                            <i class="bi bi-arrow-repeat spin"></i>
                            <span>Execution in progress…</span>
                        </div>
                    ` : `
                        ${this._inputFiles && this._inputFiles.length > 0 ? `
                        <div class="input-selector-section">
                            <div class="instructions-label">Input File</div>
                            <select class="input-selector">
                                ${this._inputFiles.map((f, i) => `<option value="${this._escapeHtml(f)}" ${i === 0 ? 'selected' : ''}>${this._escapeHtml(f.split('/').pop())} <span class="path-hint">(${this._escapeHtml(f)})</span></option>`).join('')}
                            </select>
                        </div>
                        ` : this._commandTemplate && (this._commandTemplate.includes('<input-file>') || this._commandTemplate.includes('<current-idea-file>')) ? `
                        <div class="input-selector-section">
                            <div class="instructions-label">Input File</div>
                            <input type="text" class="input-path-manual" placeholder="Enter file path...">
                        </div>
                        ` : ''}
                        <div class="instructions-section">
                            <div class="instructions-label">Instructions</div>
                            <div class="instructions-content">${hasInstructions
                                ? this._escapeHtml(this._loadedInstructions.command)
                                : '<em>No instructions available for this action.</em>'}</div>
                        </div>
                        <div class="extra-instructions-section">
                            <div class="extra-label">Extra Instructions</div>
                            <textarea class="extra-input" maxlength="500" placeholder="Optional: add context or constraints…"></textarea>
                            <div class="char-counter">0/500</div>
                        </div>
                    `}
                </div>
                <div class="modal-footer">
                    <button class="cancel-btn">Cancel</button>
                    ${!isInProgress ? `<button class="copilot-btn" ${!hasInstructions ? 'disabled' : ''}>🤖 Copilot</button>` : ''}
                </div>
            </div>
        `;
    }

    /* --- Event Binding ---------------------------------------------------- */

    _bindEvents() {
        // Close button
        this.overlay.querySelector('.modal-close-btn').addEventListener('click', () => this.close());
        this.overlay.querySelector('.cancel-btn').addEventListener('click', () => this.close());

        // Overlay backdrop click
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });

        // Escape key
        this._keyHandler = (e) => {
            if (e.key === 'Escape') this.close();
        };
        document.addEventListener('keydown', this._keyHandler);

        // Input file selector (dropdown)
        const inputSelector = this.overlay.querySelector('.input-selector');
        if (inputSelector) {
            inputSelector.addEventListener('change', () => {
                this._selectedInputFile = inputSelector.value;
                const newCommand = this._commandTemplate.replace(/<input-file>|<current-idea-file>/g, this._selectedInputFile);
                this._loadedInstructions.command = newCommand;
                const contentEl = this.overlay.querySelector('.instructions-content');
                if (contentEl) contentEl.textContent = newCommand;
            });
        }

        // Manual path input (fallback when no files auto-resolved)
        const manualInput = this.overlay.querySelector('.input-path-manual');
        if (manualInput) {
            manualInput.addEventListener('input', () => {
                this._selectedInputFile = manualInput.value;
                if (manualInput.value.trim()) {
                    const newCommand = this._commandTemplate.replace(/<input-file>|<current-idea-file>/g, manualInput.value.trim());
                    this._loadedInstructions.command = newCommand;
                    const contentEl = this.overlay.querySelector('.instructions-content');
                    if (contentEl) contentEl.textContent = newCommand;
                }
            });
        }

        // Extra instructions counter
        const textarea = this.overlay.querySelector('.extra-input');
        if (textarea) {
            textarea.addEventListener('input', () => {
                if (textarea.value.length > 500) {
                    textarea.value = textarea.value.substring(0, 500);
                }
                const counter = this.overlay.querySelector('.char-counter');
                if (counter) counter.textContent = `${textarea.value.length}/500`;
            });
        }

        // Copilot execute button
        const copilotBtn = this.overlay.querySelector('.copilot-btn');
        if (copilotBtn) {
            copilotBtn.addEventListener('click', () => this._handleExecute());
        }
    }

    /* --- Command Construction --------------------------------------------- */

    _buildCommand(extraInstructions) {
        if (!this._loadedInstructions) return '';
        let prompt = this._loadedInstructions.command;
        const wfSuffix = this.workflowName ? `@${this.workflowName}` : '';
        let cmd = `--workflow-mode${wfSuffix} ${prompt}`;
        if (this.featureId) {
            cmd += ` --feature-id ${this.featureId}`;
        }
        if (extraInstructions && extraInstructions.trim()) {
            cmd += ` --extra-instructions ${extraInstructions.trim()}`;
        }
        return cmd;
    }

    /* --- Execution Dispatch ----------------------------------------------- */

    async _handleExecute() {
        const textarea = this.overlay ? this.overlay.querySelector('.extra-input') : null;
        const extraText = textarea ? textarea.value : '';
        const cmd = this._buildCommand(extraText);
        if (!cmd) return;

        const tm = window.terminalManager;
        if (!tm) return;

        // Expand console if collapsed
        const terminalPanel = document.getElementById('terminal-panel');
        if (terminalPanel && terminalPanel.classList.contains('collapsed')) {
            const toggle = document.getElementById('terminal-toggle');
            if (toggle) toggle.click();
        }

        try {
            const idle = await tm.findIdleSession();
            if (idle) {
                await tm.claimSessionForAction(idle.sessionId, this.workflowName, this.actionKey);
                tm.switchSession(idle.key);
                tm.sendCopilotPromptCommandNoEnter(cmd);
            } else {
                const newKey = tm.addSession();
                if (newKey) {
                    setTimeout(() => tm.sendCopilotPromptCommandNoEnter(cmd), 500);
                }
            }
        } catch (err) {
            console.error('Action execution failed:', err);
        }

        // Set trigger button to in-progress
        if (this.triggerBtn) {
            this.triggerBtn.classList.add('in-progress');
        }

        this.close();
        this.onComplete();
    }

    /* --- Helpers ---------------------------------------------------------- */

    _formatActionKey(key) {
        return (key || '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
