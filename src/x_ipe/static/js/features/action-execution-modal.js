/**
 * FEATURE-038-A: Action Execution Modal
 *
 * Reusable modal for CLI Agent workflow actions.
 * Loads instructions from copilot-prompt.json, accepts extra instructions,
 * constructs CLI command, dispatches to terminal via idle session detection.
 */
class ActionExecutionModal {
    /* --- i18n Label Map --------------------------------------------------- */
    static _I18N = {
        en: {
            actionContext: 'Action Context',
            instructions: 'Instructions',
            extraInstructions: 'Extra Instructions',
            inputFile: 'Input File',
            inProgress: 'Execution in progress…',
            cancel: 'Cancel',
            noInstructions: 'No instructions available for this action.',
            extraPlaceholder: 'Optional: add context or constraints…',
            filePathPlaceholder: 'Enter file path...',
            close: 'Close',
            optional: '(optional)',
            required: '*',
        },
        zh: {
            actionContext: '操作上下文',
            instructions: '指令',
            extraInstructions: '额外指令',
            inputFile: '输入文件',
            inProgress: '执行中…',
            cancel: '取消',
            noInstructions: '此操作没有可用的指令。',
            extraPlaceholder: '可选：添加上下文或约束…',
            filePathPlaceholder: '输入文件路径…',
            close: '关闭',
            optional: '(可选)',
            required: '*',
        }
    };

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
        this._interactionMode = 'interact-with-human';
        this._language = 'en';
    }

    _i18n(key) {
        const labels = ActionExecutionModal._I18N[this._language] || ActionExecutionModal._I18N.en;
        return labels[key] ?? (ActionExecutionModal._I18N.en[key] || key);
    }

    /* --- Lifecycle -------------------------------------------------------- */

    async open() {
        await this._loadInstructions();
        await this._loadInteractionMode();
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

                    // FEATURE-042-C: Cache deliverables & set dropdown defaults (before restore)
                    await this._cacheDeliverables();
                    this._setDeliverableDefaults();

                    // Reopen: if action was done, restore previous context (overrides defaults)
                    const instance = this._cachedInstance || await this._fetchInstance();
                    this._cachedInstance = instance;
                    if (instance) {
                        const ctx = this._getInstanceContext(instance, this.actionKey, this.featureId);
                        if (ctx) await this._restoreContext(ctx);
                    }

                    // FEATURE-042-A/C: Resolve workflow prompt with context values
                    if (this._workflowCommandTemplate) {
                        this._resolveAndDisplayWorkflowPrompt();
                        this._makeInstructionsReadOnly();
                        // Add change listeners for live preview
                        const selects = this.overlay.querySelectorAll('.context-ref-group select');
                        for (const sel of selects) {
                            sel.addEventListener('change', () => this._resolveAndDisplayWorkflowPrompt());
                        }
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

        // Load project language from config (default 'en')
        let language = 'en';
        try {
            const cfgResp = await fetch('/api/config');
            if (cfgResp.ok) {
                const cfgData = await cfgResp.json();
                language = cfgData.language || 'en';
            }
        } catch (e) { /* ignore — fall back to 'en' */ }
        this._language = language;

        // FEATURE-042-A: Workflow-mode branch — use workflow-prompts array
        if (this.workflowName) {
            const wpEntry = this._getWorkflowPrompt(this.actionKey);
            if (wpEntry && wpEntry['prompt-details']) {
                const detail = wpEntry['prompt-details'].find(d => d.language === language)
                    || wpEntry['prompt-details'].find(d => d.language === 'en')
                    || wpEntry['prompt-details'][0];
                if (detail) {
                    this._workflowCommandTemplate = detail.command;
                    this._loadedInstructions = { label: detail.label, command: detail.command };
                    return;
                }
            }
            // No workflow-prompt found → fall through to legacy path
        }

        // Legacy prompt path (unchanged)
        const entry = this._getConfigEntry(config);
        if (!entry) return;

        const detail = entry['prompt-details'].find(d => d.language === language)
            || entry['prompt-details'].find(d => d.language === 'en')
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

    /* --- CR-001/CR-002: Interaction Mode Loading ----------------------------- */

    async _loadInteractionMode() {
        if (!this.workflowName) return;
        try {
            const instance = this._cachedInstance || await this._fetchInstance();
            this._cachedInstance = instance;
            if (instance) {
                const pref = (instance.global || {}).process_preference || {};
                this._interactionMode = pref.interaction_mode || 'interact-with-human';
            }
        } catch { /* keep default 'interact-with-human' */ }
    }

    _buildExecutionFlag() {
        if (this._interactionMode === 'interact-with-human') return '';
        return ` --interaction@${this._interactionMode}`;
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
            const rawDeliverables = composeAction.deliverables || {};
            let deliverables;
            if (Array.isArray(rawDeliverables)) {
                deliverables = rawDeliverables;
            } else if (typeof rawDeliverables === 'object') {
                deliverables = [];
                for (const val of Object.values(rawDeliverables)) {
                    if (Array.isArray(val)) deliverables.push(...val);
                    else if (typeof val === 'string') deliverables.push(val);
                }
            } else {
                deliverables = [];
            }
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
        for (const [key, sectionData] of Object.entries(config)) {
            if (key === 'workflow-prompts' || key === 'version') continue;
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

    /* --- FEATURE-042-A: Workflow Prompt Lookup & Template Resolution ------ */

    _getWorkflowPrompt(actionKey) {
        const config = window.__copilotPromptConfig;
        const prompts = config?.['workflow-prompts'];
        if (!Array.isArray(prompts) || prompts.length === 0) {
            return null;
        }
        return prompts.find(p => p.action === actionKey) || null;
    }

    _resolveTemplate(template, contextValues) {
        if (!template) return '';
        let resolved = template;

        // CR-003: Helper — format value for template display
        const toDisplay = (val, tag) => Array.isArray(val) ? `tag:${tag}` : val;

        // $output:tag-name$
        resolved = resolved.replace(/\$output:([a-z0-9-]+)\$/g, (match, tag) => {
            const val = contextValues[tag];
            return val != null ? toDisplay(val, tag) : match;
        });

        // $output-folder:tag-name$
        resolved = resolved.replace(/\$output-folder:([a-z0-9-]+)\$/g, (match, tag) => {
            const val = contextValues[tag];
            return val != null ? toDisplay(val, tag) : match;
        });

        // $feature-id$
        resolved = resolved.replace(/\$feature-id\$/g, () => {
            const fid = contextValues['$feature-id'];
            return (fid !== undefined && fid !== null) ? fid : '';
        });

        return resolved;
    }

    _collectContextValues() {
        const values = {};
        if (this.overlay) {
            const groups = this.overlay.querySelectorAll('.context-ref-group');
            for (const group of groups) {
                const refName = group.dataset.refName;
                const select = group.querySelector('select');
                if (refName && select) {
                    let val = select.value;
                    // Parse JSON array values stored by _setDeliverableDefaults
                    if (val.startsWith('[')) {
                        try { val = JSON.parse(val); } catch { /* keep as string */ }
                    }
                    values[refName] = val;
                }
            }
        }
        if (this.featureId) {
            values['$feature-id'] = this.featureId;
        }
        return values;
    }

    /* --- FEATURE-042-B: Conditional Block Parsing & Error Handling -------- */

    _resolveConditionalBlocks(template, contextValues) {
        if (!template) return '';
        let resolved = template.replace(/<([^<>]*)>/g, (match, content) => {
            const varRefs = content.match(/\$(?:output:|output-folder:|feature-id)[a-z0-9-]*\$/g);
            if (!varRefs || varRefs.length === 0) return content;

            for (const ref of varRefs) {
                let tag = null;
                const outputMatch = ref.match(/\$output:([a-z0-9-]+)\$/);
                const folderMatch = ref.match(/\$output-folder:([a-z0-9-]+)\$/);
                if (outputMatch) tag = outputMatch[1];
                else if (folderMatch) tag = folderMatch[1];
                else if (ref === '$feature-id$') tag = '$feature-id';

                const val = tag ? contextValues[tag] : undefined;
                if (!val || val === 'N/A' || val === '') return '';
            }
            return content;
        });

        // Collapse double-spaces and trim
        resolved = resolved.replace(/\s{2,}/g, ' ').trim();
        return resolved;
    }

    _formatUnresolvedWarnings(html) {
        if (!html) return '';
        return html.replace(/\$output:([a-z0-9-]+)\$/g,
            '<span class="unresolved-warning">$output:$1$</span>');
    }

    /* --- FEATURE-042-C: Deliverable Defaults & Preview ------------------- */

    async _cacheDeliverables() {
        this._deliverableCache = {};
        if (!this.workflowName) { this._deliverableCache = undefined; return; }

        // Reuse already-fetched instance to avoid extra API call
        if (!this._cachedInstance) {
            this._cachedInstance = await this._fetchInstance();
        }
        const instance = this._cachedInstance;
        if (!instance) return;

        // Collect deliverables from all shared stage actions
        const shared = instance.shared || {};
        for (const stageData of Object.values(shared)) {
            const actions = stageData.actions || {};
            for (const actionDef of Object.values(actions)) {
                const deliverables = actionDef.deliverables || {};
                if (typeof deliverables === 'object' && !Array.isArray(deliverables)) {
                    for (const [tag, path] of Object.entries(deliverables)) {
                        this._deliverableCache[tag] = path || null;
                    }
                }
            }
        }

        // Collect from feature lanes if applicable
        if (this.featureId && instance.features) {
            const features = Array.isArray(instance.features)
                ? instance.features
                : Object.values(instance.features);
            for (const feat of features) {
                if (feat.feature_id === this.featureId) {
                    for (const stage of ['implement', 'validation', 'feedback']) {
                        const stageData = feat[stage] || {};
                        const actions = stageData.actions || {};
                        for (const actionDef of Object.values(actions)) {
                            const deliverables = actionDef.deliverables || {};
                            if (typeof deliverables === 'object' && !Array.isArray(deliverables)) {
                                for (const [tag, path] of Object.entries(deliverables)) {
                                    this._deliverableCache[tag] = path || null;
                                }
                            }
                        }
                    }
                }
            }
        }

        // For action_context refs that have no cached deliverable, set to null
        if (this._actionContextDef) {
            for (const refName of Object.keys(this._actionContextDef)) {
                if (!(refName in this._deliverableCache)) {
                    this._deliverableCache[refName] = null;
                }
            }
        }
    }

    _setDeliverableDefaults() {
        if (!this._deliverableCache || !this.overlay) return;
        const groups = this.overlay.querySelectorAll('.context-ref-group');
        for (const group of groups) {
            const refName = group.dataset.refName;
            const select = group.querySelector('select');
            if (!refName || !select) continue;

            // Only set default if dropdown is still at auto-detect (not already restored)
            if (select.value !== 'auto-detect') continue;

            const cached = this._deliverableCache[refName];
            if (cached) {
                if (Array.isArray(cached)) {
                    // Multiple files — show compact tag label
                    const tagLabel = `tag:${refName}`;
                    const tagValue = JSON.stringify(cached);
                    select.add(new Option(tagLabel, tagValue));
                    select.value = tagValue;
                } else {
                    let opt = Array.from(select.options).find(o => o.value === cached);
                    if (!opt) {
                        select.add(new Option(cached, cached));
                        opt = select.options[select.options.length - 1];
                    }
                    select.value = opt.value;
                }
            }
        }
    }

    _resolveAndDisplayWorkflowPrompt() {
        if (!this._workflowCommandTemplate || !this.overlay) return;

        const contextValues = this._collectContextValues();
        // Resolve conditionals first (needs raw $output:tag$ tokens to detect N/A)
        let resolved = this._resolveConditionalBlocks(this._workflowCommandTemplate, contextValues);
        // Then substitute remaining tokens with actual values
        resolved = this._resolveTemplate(resolved, contextValues);

        this._loadedInstructions.command = resolved;
        const contentEl = this.overlay.querySelector('.instructions-content');
        if (contentEl) {
            // Build full preview including CLI flags
            let preview = resolved;
            if (this.featureId) preview += ` --feature-id ${this.featureId}`;
            const wfSuffix = this.workflowName ? `@${this.workflowName}` : '';
            preview += ` --workflow-mode${wfSuffix}`;
            preview += this._buildExecutionFlag();
            const formatted = this._formatUnresolvedWarnings(this._escapeHtml(preview));
            contentEl.innerHTML = formatted;
        }
    }

    _updatePreview() {
        return this._resolveAndDisplayWorkflowPrompt();
    }

    _composeCommand() {
        if (!this._loadedInstructions) return '';
        const resolved = this._loadedInstructions.command;
        const textarea = this.overlay ? this.overlay.querySelector('.extra-input') : null;
        const extra = textarea ? textarea.value.trim() : '';
        if (extra) {
            return resolved + '\n\n' + extra;
        }
        return resolved;
    }

    _makeInstructionsReadOnly() {
        if (!this.overlay) return;
        const contentEl = this.overlay.querySelector('.instructions-content');
        if (contentEl) {
            contentEl.setAttribute('readonly', '');
            contentEl.classList.add('instructions-readonly');
            contentEl.contentEditable = 'false';
        }
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
        heading.textContent = this._i18n('actionContext');
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
            label.innerHTML += ` <span class="required">${this._i18n('required')}</span>`;
        } else {
            label.innerHTML += ` <span class="optional">${this._escapeHtml(this._i18n('optional'))}</span>`;
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
                    <button class="modal-close-btn" title="${this._escapeHtml(this._i18n('close'))}">&times;</button>
                </div>
                <div class="modal-body">
                    ${isInProgress ? `
                        <div class="in-progress-message">
                            <i class="bi bi-arrow-repeat spin"></i>
                            <span>${this._escapeHtml(this._i18n('inProgress'))}</span>
                        </div>
                    ` : `
                        ${this._inputFiles && this._inputFiles.length > 0 ? `
                        <div class="input-selector-section">
                            <div class="instructions-label">${this._escapeHtml(this._i18n('inputFile'))}</div>
                            <select class="input-selector">
                                ${this._inputFiles.map((f, i) => `<option value="${this._escapeHtml(f)}" ${i === 0 ? 'selected' : ''}>${this._escapeHtml(f.split('/').pop())} <span class="path-hint">(${this._escapeHtml(f)})</span></option>`).join('')}
                            </select>
                        </div>
                        ` : this._commandTemplate && (this._commandTemplate.includes('<input-file>') || this._commandTemplate.includes('<current-idea-file>')) ? `
                        <div class="input-selector-section">
                            <div class="instructions-label">${this._escapeHtml(this._i18n('inputFile'))}</div>
                            <input type="text" class="input-path-manual" placeholder="${this._escapeHtml(this._i18n('filePathPlaceholder'))}">
                        </div>
                        ` : ''}
                        <div class="instructions-section">
                            <div class="instructions-label">${this._escapeHtml(this._i18n('instructions'))}</div>
                            <div class="instructions-content">${hasInstructions
                                ? this._escapeHtml(this._buildPreviewText())
                                : `<em>${this._escapeHtml(this._i18n('noInstructions'))}</em>`}</div>
                        </div>
                        <div class="extra-instructions-section">
                            <div class="extra-label">${this._escapeHtml(this._i18n('extraInstructions'))}</div>
                            <textarea class="extra-input" maxlength="500" placeholder="${this._escapeHtml(this._i18n('extraPlaceholder'))}"></textarea>
                            <div class="char-counter">0/500</div>
                        </div>
                    `}
                </div>
                <div class="modal-footer">
                    <button class="cancel-btn">${this._escapeHtml(this._i18n('cancel'))}</button>
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
        let cmd = prompt;
        if (this.featureId) {
            cmd += ` --feature-id ${this.featureId}`;
        }
        if (extraInstructions && extraInstructions.trim()) {
            cmd += ` --extra-instructions ${extraInstructions.trim()}`;
        }
        cmd += ` --workflow-mode${wfSuffix}`;
        cmd += this._buildExecutionFlag();
        return cmd;
    }

    /* --- Execution Dispatch ----------------------------------------------- */

    async _handleExecute() {
        const textarea = this.overlay ? this.overlay.querySelector('.extra-input') : null;
        const extraText = textarea ? textarea.value : '';

        // FEATURE-042-C: Use workflow command composition in workflow mode
        let cmd;
        if (this._workflowCommandTemplate) {
            const composed = this._composeCommand();
            const wfSuffix = this.workflowName ? `@${this.workflowName}` : '';
            cmd = composed;
            if (this.featureId) {
                cmd += ` --feature-id ${this.featureId}`;
            }
            cmd += ` --workflow-mode${wfSuffix}`;
            cmd += this._buildExecutionFlag();
        } else {
            cmd = this._buildCommand(extraText);
        }
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

    _buildPreviewText() {
        if (!this._loadedInstructions) return '';
        let preview = this._loadedInstructions.command;
        if (this.featureId) preview += ` --feature-id ${this.featureId}`;
        const wfSuffix = this.workflowName ? `@${this.workflowName}` : '';
        preview += ` --workflow-mode${wfSuffix}`;
        preview += this._buildExecutionFlag();
        return preview;
    }

    _formatActionKey(key) {
        const ACRONYMS = new Set(['uiux', 'api', 'ui', 'ux', 'cr', 'dao', 'cli', 'mcp']);
        return (key || '').split('_').map(w =>
            ACRONYMS.has(w) ? w.toUpperCase() : w.charAt(0).toUpperCase() + w.slice(1)
        ).join(' ');
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
