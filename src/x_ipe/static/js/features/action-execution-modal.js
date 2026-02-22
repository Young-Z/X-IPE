/**
 * FEATURE-038-A: Action Execution Modal
 *
 * Reusable modal for CLI Agent workflow actions.
 * Loads instructions from copilot-prompt.json, accepts extra instructions,
 * constructs CLI command, dispatches to terminal via idle session detection.
 */
class ActionExecutionModal {
    constructor({ actionKey, workflowName, skillName, onComplete, status, triggerBtn }) {
        this.actionKey = actionKey;
        this.workflowName = workflowName;
        this.skillName = skillName || '';
        this.onComplete = onComplete || (() => {});
        this.status = status || null;
        this.triggerBtn = triggerBtn || null;
        this.overlay = null;
        this._loadedInstructions = null;
        this._keyHandler = null;
    }

    /* --- Lifecycle -------------------------------------------------------- */

    async open() {
        await this._loadInstructions();
        this._createDOM();
        this._bindEvents();
        document.body.appendChild(this.overlay);
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

        const configId = this.actionKey.replace(/_/g, '-');
        for (const [, stageData] of Object.entries(config)) {
            if (stageData.prompts) {
                const prompt = stageData.prompts.find(p => p.id === configId);
                if (prompt) {
                    const detail = prompt['prompt-details'].find(d => d.language === 'en')
                        || prompt['prompt-details'][0];
                    let command = detail.command;
                    // Resolve <current-idea-file> placeholder from workflow deliverables
                    if (command.includes('<current-idea-file>') && this.workflowName) {
                        this._ideaFiles = await this._resolveIdeaFiles();
                        this._commandTemplate = command;
                        const selected = this._ideaFiles.length ? this._ideaFiles[0] : null;
                        this._selectedIdeaFile = selected;
                        if (selected) command = command.replace('<current-idea-file>', selected);
                    }
                    this._loadedInstructions = { label: detail.label, command };
                    return;
                }
            }
        }
    }

    async _resolveIdeaFiles() {
        const files = [];
        try {
            const resp = await fetch(`/api/workflow/${encodeURIComponent(this.workflowName)}`);
            if (!resp.ok) return files;
            const json = await resp.json();
            const stages = (json.data || {}).stages || {};
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
                        ${this._ideaFiles && this._ideaFiles.length > 0 ? `
                        <div class="idea-selector-section">
                            <div class="instructions-label">Current Selected Idea</div>
                            <select class="idea-selector">
                                ${this._ideaFiles.map((f, i) => `<option value="${this._escapeHtml(f)}" ${i === 0 ? 'selected' : ''}>${this._escapeHtml(f.split('/').pop())} <span class="idea-path-hint">(${this._escapeHtml(f)})</span></option>`).join('')}
                            </select>
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

        // Idea file selector
        const ideaSelector = this.overlay.querySelector('.idea-selector');
        if (ideaSelector) {
            ideaSelector.addEventListener('change', () => {
                this._selectedIdeaFile = ideaSelector.value;
                const newCommand = this._commandTemplate.replace('<current-idea-file>', this._selectedIdeaFile);
                this._loadedInstructions.command = newCommand;
                const contentEl = this.overlay.querySelector('.instructions-content');
                if (contentEl) contentEl.textContent = newCommand;
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
        // Prefix with --workflow-mode@{name} so the agent knows this was dispatched from the workflow UI
        const wfSuffix = this.workflowName ? `@${this.workflowName}` : '';
        let cmd = `--workflow-mode${wfSuffix} ${prompt}`;
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
