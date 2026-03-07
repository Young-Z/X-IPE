/**
 * FEATURE-036-C: Stage Ribbon & Action Execution
 * FEATURE-036-D: Feature Lanes & Dependencies
 * FEATURE-036-E: Deliverables, Polling & Lifecycle
 * Renders stage progression ribbon, action buttons, feature lanes, and deliverables.
 */

/**
 * FEATURE-037-B: Stage Gate Checker
 * Determines whether a completed action can be re-opened.
 * Rule: block re-open if ANY action in the NEXT stage is in_progress or done.
 */
class StageGateChecker {
    static STAGE_ORDER = ['ideation', 'requirement', 'implement', 'validation', 'feedback'];

    static canReopen(actionKey, stages) {
        // Find which stage this action belongs to
        let currentStageKey = null;
        for (const [stageKey, stageDef] of Object.entries(stages)) {
            if (stageDef.actions && stageDef.actions[actionKey]) {
                currentStageKey = stageKey;
                break;
            }
        }
        if (!currentStageKey) return { allowed: true };

        const idx = this.STAGE_ORDER.indexOf(currentStageKey);
        if (idx < 0 || idx >= this.STAGE_ORDER.length - 1) return { allowed: true };

        const nextStageKey = this.STAGE_ORDER[idx + 1];
        const nextStage = stages[nextStageKey];
        if (!nextStage || !nextStage.actions) return { allowed: true };

        for (const [key, act] of Object.entries(nextStage.actions)) {
            if (act.status === 'in_progress' || act.status === 'done') {
                return { allowed: false, blocker: key, stage: nextStageKey };
            }
        }
        return { allowed: true };
    }
}

const workflowStage = {
    STAGE_ORDER: ['ideation', 'requirement', 'implement', 'validation', 'feedback'],

    // CR-001: Client-side running state — resets on page refresh
    _runningActions: new Set(),

    FEATURE_LANE_ACTIONS: [
        { key: 'feature_refinement', label: 'Refinement',  icon: '📐' },
        { key: 'technical_design',   label: 'Tech Design', icon: '⚙' },
        { key: 'implementation',     label: 'Implement',   icon: '💻' },
        { key: 'acceptance_testing', label: 'Testing',     icon: '✅' },
        { key: 'code_refactor',      label: 'Refactor',    icon: '🔧' },
        { key: 'feature_closing',    label: 'Closing',     icon: '🏁' },
        { key: 'human_playground',   label: 'Playground',  icon: '🎮' },
        { key: 'change_request',     label: 'CR',          icon: '🔄' },
    ],

    DELIVERABLE_ICONS: {
        ideas:           { icon: '💡', label: 'Ideas' },
        mockups:         { icon: '🎨', label: 'Mockups' },
        requirements:    { icon: '📋', label: 'Requirements' },
        implementations: { icon: '💻', label: 'Implementations' },
        quality:         { icon: '📊', label: 'Quality' },
    },

    ACTION_MAP: {
        ideation: {
            label: 'Ideation',
            actions: {
                compose_idea:   { label: 'Compose Idea',   icon: '📝', mandatory: true,  interaction: 'modal' },
                reference_uiux: { label: 'Reference UIUX', icon: '🎨', mandatory: false, interaction: 'cli', skill: 'x-ipe-tool-uiux-reference' },
                refine_idea:    { label: 'Refine Idea',    icon: '💡', mandatory: true,  interaction: 'cli', skill: 'x-ipe-task-based-ideation' },
                design_mockup:  { label: 'Design Mockup',  icon: '🖼', mandatory: false, interaction: 'cli', skill: 'x-ipe-task-based-idea-mockup' },
            }
        },
        requirement: {
            label: 'Requirement',
            actions: {
                requirement_gathering: { label: 'Requirement Gathering', icon: '📋', mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-requirement-gathering' },
                feature_breakdown:     { label: 'Feature Breakdown',     icon: '🔀', mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-feature-breakdown' },
            }
        },
        implement: {
            label: 'Implement',
            actions: {
                feature_refinement: { label: 'Feature Refinement', icon: '📐', mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-feature-refinement' },
                technical_design:   { label: 'Technical Design',   icon: '⚙',  mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-technical-design' },
                implementation:     { label: 'Implementation',     icon: '💻', mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-code-implementation' },
            }
        },
        validation: {
            label: 'Validation',
            actions: {
                acceptance_testing: { label: 'Acceptance Testing', icon: '✅', mandatory: true,  interaction: 'cli', skill: 'x-ipe-task-based-feature-acceptance-test' },
                code_refactor:      { label: 'Code Refactor',      icon: '🔧', mandatory: true,  interaction: 'cli', skill: 'x-ipe-task-based-code-refactor' },
                feature_closing:    { label: 'Feature Closing',    icon: '🏁', mandatory: true,  interaction: 'cli', skill: 'x-ipe-task-based-feature-closing' },
            }
        },
        feedback: {
            label: 'Feedback',
            actions: {
                human_playground: { label: 'Human Playground', icon: '🎮', mandatory: false, interaction: 'cli', skill: 'x-ipe-task-based-human-playground' },
                change_request:   { label: 'Change Request',   icon: '🔄', mandatory: false, interaction: 'cli', skill: 'x-ipe-task-based-change-request' },
            }
        }
    },

    /** Main entry: render stage ribbon + actions (or feature lanes) + deliverables into container. */
    render(container, workflowState, nextAction, workflowName) {
        const stages = this._buildStagesView(workflowState);
        container.appendChild(this._renderRibbon(stages));
        if (this._hasFeatures(stages)) {
            // Show shared (non-feature) stage actions first
            const sharedStageNames = this.STAGE_ORDER.filter(s => {
                const st = stages[s] || {};
                return !st.features || Object.keys(st.features).length === 0;
            });
            if (sharedStageNames.length > 0) {
                container.appendChild(this._renderActionsArea(stages, nextAction, workflowName, sharedStageNames));
            }
            container.appendChild(this._renderToolbar(stages, nextAction, workflowName, workflowState));
            container.appendChild(this._renderFeatureLanes(stages, nextAction, workflowName));
        } else {
            container.appendChild(this._renderActionsArea(stages, nextAction, workflowName));
        }
        this._renderDeliverables(container, workflowName);
    },

    /**
     * Build a backward-compatible stages view from the new shared + features structure.
     * If the state already has 'stages' (v1 format), return as-is.
     */
    _buildStagesView(workflowState) {
        if (workflowState.stages) return workflowState.stages;
        const stages = {};
        if (workflowState.shared) {
            for (const [name, data] of Object.entries(workflowState.shared)) {
                stages[name] = data;
            }
        }
        const featuresList = workflowState.features || [];
        for (const stageName of ['implement', 'validation', 'feedback']) {
            const features = {};
            let stageStatus = 'locked';
            for (const feat of featuresList) {
                const featStage = feat[stageName] || {};
                const mergedActions = {};
                for (const s of ['implement', 'validation', 'feedback']) {
                    Object.assign(mergedActions, (feat[s] || {}).actions || {});
                }
                features[feat.feature_id] = {
                    name: feat.name,
                    depends_on: feat.depends_on || [],
                    actions: mergedActions,
                };
                if (featStage.status === 'in_progress' || featStage.status === 'done') {
                    stageStatus = 'in_progress';
                }
            }
            stages[stageName] = { status: stageStatus, features };
        }
        return stages;
    },

    /**
     * Return the set of action keys suggested by the latest done action
     * (last in ACTION_MAP order within the latest stage that has done actions).
     */
    _getLatestSuggestions(stages) {
        let latestSuggestions = [];
        for (const stageName of this.STAGE_ORDER) {
            const stageConfig = this.ACTION_MAP[stageName];
            if (!stageConfig) continue;
            const apiActions = (stages[stageName] || {}).actions || {};
            for (const key of Object.keys(stageConfig.actions)) {
                const a = apiActions[key];
                if (a && a.status === 'done' && Array.isArray(a.next_actions_suggested) && a.next_actions_suggested.length > 0) {
                    latestSuggestions = a.next_actions_suggested;
                }
            }
        }
        return new Set(latestSuggestions);
    },

    /** Check if all mandatory actions in a stage are done. */
    _isStageMandatoryDone(stages, stageName) {
        const stageConfig = this.ACTION_MAP[stageName];
        if (!stageConfig) return false;
        const apiActions = (stages[stageName] || {}).actions || {};
        return Object.entries(stageConfig.actions)
            .filter(([_, def]) => def.mandatory)
            .every(([key]) => (apiActions[key] || {}).status === 'done');
    },

    /** Check if any stage has features. */
    _hasFeatures(stages) {
        return this.STAGE_ORDER.some(s => {
            const st = stages[s] || {};
            return st.features && Object.keys(st.features).length > 0;
        });
    },

    _renderRibbon(stages) {
        const ribbon = document.createElement('div');
        ribbon.className = 'stage-ribbon';

        this.STAGE_ORDER.forEach((name, i) => {
            if (i > 0) {
                const arrow = document.createElement('span');
                arrow.className = 'stage-arrow';
                arrow.textContent = '›';
                ribbon.appendChild(arrow);
            }
            const stageData = stages[name] || {};
            ribbon.appendChild(this._renderStagePill(name, stageData.status || 'locked', i));
        });
        return ribbon;
    },

    _renderStagePill(name, status, index) {
        const pill = document.createElement('span');
        const stateClass = status === 'in_progress' ? 'active'
            : status === 'completed' ? 'completed'
            : status === 'locked' ? 'locked' : 'pending';
        pill.className = `stage-item ${stateClass}`;

        const stageConfig = this.ACTION_MAP[name] || {};
        const label = stageConfig.label || name;

        if (status === 'completed') {
            pill.innerHTML = `<span class="stage-check">✓</span> ${label}`;
        } else if (status === 'in_progress') {
            pill.innerHTML = `<span class="stage-dot"></span> ${label}`;
        } else {
            pill.innerHTML = `<span class="stage-num">${index + 1}</span> ${label}`;
        }
        return pill;
    },

    _renderActionsArea(stages, nextAction, wfName, stageFilter = null) {
        const area = document.createElement('div');
        area.className = 'actions-area';

        const stageOrder = stageFilter || this.STAGE_ORDER;
        const latestSuggestions = this._getLatestSuggestions(stages);

        // Group completed stages together under "COMPLETED ACTIONS"
        const completedStages = stageOrder.filter(s => (stages[s] || {}).status === 'completed');
        if (completedStages.length > 0) {
            const group = document.createElement('div');
            group.className = 'action-group';
            const label = document.createElement('div');
            label.className = 'actions-label';
            label.textContent = 'Completed Actions';
            group.appendChild(label);
            const grid = document.createElement('div');
            grid.className = 'actions-grid';
            completedStages.forEach(stageName => {
                const stageConfig = this.ACTION_MAP[stageName];
                if (!stageConfig) return;
                const apiActions = (stages[stageName] || {}).actions || {};
                Object.entries(stageConfig.actions).forEach(([key, def]) => {
                    const apiAction = apiActions[key] || {};
                    const apiStatus = apiAction.status || 'pending';
                    const isOptional = apiAction.optional === true;
                    const isSuggestedByLatest = latestSuggestions.has(key);
                    grid.appendChild(this._renderActionButton(key, def, apiStatus, isSuggestedByLatest, false, wfName, isOptional));
                });
            });
            group.appendChild(grid);
            area.appendChild(group);
        }

        // Active stage with "{STAGE_NAME} Actions" label
        const activeStage = stageOrder.find(s => (stages[s] || {}).status === 'in_progress');
        if (activeStage) {
            const stageConfig = this.ACTION_MAP[activeStage];
            if (stageConfig) {
                area.appendChild(this._renderActionGroup(activeStage, (stages[activeStage] || {}).actions || {}, nextAction, wfName, false, null, latestSuggestions));
            }
        }

        // First locked stage — render as ready (clickable) or locked
        const firstLocked = stageOrder.find(s => (stages[s] || {}).status === 'locked');
        if (firstLocked) {
            const lockedIdx = stageOrder.indexOf(firstLocked);
            const prevStageKey = lockedIdx > 0 ? stageOrder[lockedIdx - 1] : null;
            const prevReady = prevStageKey && this._isStageMandatoryDone(stages, prevStageKey);

            if (prevReady) {
                // Previous stage mandatory done — show next stage as clickable
                area.appendChild(this._renderActionGroup(
                    firstLocked,
                    (stages[firstLocked] || {}).actions || {},
                    nextAction, wfName, false, null, latestSuggestions));
            } else {
                const prevLabel = lockedIdx > 0 ? (this.ACTION_MAP[stageOrder[lockedIdx - 1]] || {}).label || stageOrder[lockedIdx - 1] : '';
                area.appendChild(this._renderActionGroup(firstLocked, {}, nextAction, wfName, true, prevLabel, latestSuggestions));
            }
        }

        return area;
    },

    _renderActionGroup(stageName, apiActions, nextAction, wfName, locked, prevStageName, latestSuggestions) {
        const group = document.createElement('div');
        group.className = 'action-group';

        const stageConfig = this.ACTION_MAP[stageName];
        if (!stageConfig) return group;

        const label = document.createElement('div');
        label.className = 'actions-label';
        label.textContent = `${stageConfig.label} Actions`;
        if (locked && prevStageName) {
            const sub = document.createElement('span');
            sub.className = 'actions-label-sub';
            sub.textContent = ` — complete ${prevStageName} to unlock`;
            label.appendChild(sub);
        }
        group.appendChild(label);

        const grid = document.createElement('div');
        grid.className = 'actions-grid';

        const suggestions = latestSuggestions || new Set();
        Object.entries(stageConfig.actions).forEach(([key, def]) => {
            const apiAction = apiActions[key] || {};
            const apiStatus = apiAction.status || 'pending';
            const isSuggested = nextAction && nextAction.action === key && nextAction.stage === stageName;
            const isOptional = apiAction.optional === true;
            const isSuggestedByLatest = suggestions.has(key);
            grid.appendChild(this._renderActionButton(key, def, apiStatus, isSuggested || isSuggestedByLatest, locked, wfName, isOptional));
        });

        group.appendChild(grid);
        return group;
    },

    _renderActionButton(actionKey, actionDef, status, isSuggested, locked, wfName, isOptional) {
        const btn = document.createElement('button');

        let stateClass;
        if (locked) stateClass = 'locked';
        else if (status === 'done') {
            stateClass = 'done';
            this._runningActions.delete(actionKey);
        }
        else if (isOptional) stateClass = 'optional';
        else stateClass = 'normal';

        btn.className = `action-btn ${stateClass}`;
        if (isSuggested && stateClass !== 'done' && stateClass !== 'locked') btn.classList.add('suggested');
        // CR-001: Apply .running class from client-side running state
        if (this._runningActions.has(actionKey)) btn.classList.add('running');

        if (actionDef.deferred) {
            btn.classList.add('locked');
            btn.title = 'Coming Soon';
        } else if (locked) {
            btn.title = 'Complete previous stages to unlock this action';
        }

        btn.innerHTML = `<span class="action-icon">${actionDef.icon}</span> ${actionDef.label}`;

        // Context menu for manual override (FEATURE-036-E)
        btn.oncontextmenu = (e) => {
            e.preventDefault();
            e.stopPropagation();
            this._renderContextMenu(e.clientX, e.clientY, actionKey, wfName, null);
        };

        btn.onclick = (e) => {
            e.stopPropagation();
            if (locked || actionDef.deferred) {
                this._showToast(locked ? `Complete previous stages to unlock ${actionDef.label}` : 'This action is coming soon', 'info');
                return;
            }
            if (status === 'done') {
                this._handleCompletedAction(wfName, actionKey, actionDef);
                return;
            }
            // CR-001: Mark running before dispatch (client-side only)
            this._markRunning(actionKey, btn);
            if (actionDef.interaction === 'modal') {
                this._dispatchModalAction(wfName, actionKey);
            } else {
                this._dispatchCliAction(wfName, actionKey, actionDef.skill, btn);
            }
        };

        return btn;
    },

    // CR-001: Mark action as running (client-side only, resets on page refresh)
    _markRunning(actionKey, btnElement) {
        this._runningActions.add(actionKey);
        btnElement.classList.add('running');
    },

    /**
     * FEATURE-037-B: Handle click on a completed action.
     * Checks stage gate, shows confirm dialog, then re-opens in edit mode.
     */
    async _handleCompletedAction(wfName, actionKey, actionDef) {
        try {
            const resp = await fetch(`/api/workflow/${encodeURIComponent(wfName)}`);
            const json = await resp.json();
            const wfData = json.data || {};
            const stages = this._buildStagesView(wfData);

            const gate = StageGateChecker.canReopen(actionKey, stages);
            if (!gate.allowed) {
                this._showToast(`Cannot re-open: ${gate.blocker} in ${gate.stage} stage is already started`, 'error');
                return;
            }

            const confirmed = await this._showConfirmModal(
                'Re-edit Action',
                `<strong>${actionDef.label}</strong> is already completed. Do you want to re-edit it?`
            );
            if (!confirmed) return;

            // Rollback action status to pending
            await fetch(`/api/workflow/${encodeURIComponent(wfName)}/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: actionKey, status: 'pending' })
            });

            // Open in edit mode for modal actions, re-dispatch for CLI
            if (actionDef.interaction === 'modal') {
                this._dispatchEditModalAction(wfName, actionKey, wfData);
            } else {
                this._dispatchCliAction(wfName, actionKey, actionDef.skill);
            }
        } catch (err) {
            this._showToast('Failed to check action status', 'error');
        }
    },

    /**
     * FEATURE-037-B: Show Bootstrap confirm modal, returns Promise<boolean>.
     */
    _showConfirmModal(title, bodyHtml) {
        return new Promise(resolve => {
            let modal = document.getElementById('wf-confirm-modal');
            if (!modal) {
                modal = document.createElement('div');
                modal.id = 'wf-confirm-modal';
                modal.className = 'modal fade';
                modal.tabIndex = -1;
                modal.innerHTML = `
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title"></h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body"></div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary wf-confirm-yes">Confirm</button>
                            </div>
                        </div>
                    </div>`;
                document.body.appendChild(modal);
            }
            modal.querySelector('.modal-title').textContent = title;
            modal.querySelector('.modal-body').innerHTML = bodyHtml;

            const bsModal = new bootstrap.Modal(modal, { backdrop: 'static' });
            let resolved = false;

            const confirmBtn = modal.querySelector('.wf-confirm-yes');
            const onConfirm = () => { resolved = true; bsModal.hide(); };
            confirmBtn.addEventListener('click', onConfirm, { once: true });

            modal.addEventListener('hidden.bs.modal', () => {
                confirmBtn.removeEventListener('click', onConfirm);
                resolve(resolved);
            }, { once: true });

            bsModal.show();
        });
    },

    /**
     * FEATURE-037-B: Open modal in edit mode with existing deliverables.
     */
    _dispatchEditModalAction(wfName, actionKey, wfData) {
        if (actionKey === 'compose_idea' && typeof ComposeIdeaModal !== 'undefined') {
            const stages = wfData.stages || {};
            const action = (stages.ideation && stages.ideation.actions && stages.ideation.actions.compose_idea) || {};
            const deliverables = action.deliverables || [];

            // Auto-detect folder path and file from deliverables
            let folderPath = '';
            let folderName = '';
            let filePath = '';
            for (const d of deliverables) {
                if (d.endsWith('.md')) {
                    filePath = d;
                    const parts = d.split('/');
                    parts.pop(); // remove filename
                    folderPath = parts.join('/');
                    folderName = parts[parts.length - 1] || '';
                }
            }

            const modal = new ComposeIdeaModal({
                workflowName: wfName,
                mode: 'edit',
                filePath: filePath,
                folderPath: folderPath,
                folderName: folderName,
                onComplete: () => {
                    const container = document.getElementById('workflow-view');
                    if (container && window.workflowView) {
                        window.workflowView.render(container);
                    }
                }
            });
            modal.open();
            return;
        }
        // Fallback: re-dispatch as normal modal action
        this._dispatchModalAction(wfName, actionKey);
    },

    async _dispatchCliAction(wfName, actionKey, skillName, triggerBtn, featureId) {
        if (!skillName) {
            this._showToast('This action is not yet available', 'error');
            return;
        }

        // FEATURE-038-A: Use ActionExecutionModal if available
        if (typeof ActionExecutionModal !== 'undefined') {
            const modal = new ActionExecutionModal({
                actionKey,
                workflowName: wfName,
                skillName,
                featureId,
                triggerBtn,
                onComplete: () => {
                    const container = document.getElementById('workflow-view');
                    if (container && window.workflowView) {
                        window.workflowView.render(container);
                    }
                }
            });
            modal.open();
            return;
        }

        // Fallback: direct terminal dispatch
        const consoleEl = document.querySelector('.console-container');
        if (consoleEl && consoleEl.classList.contains('hidden')) {
            const toggle = document.querySelector('[title*="Toggle terminal"]');
            if (toggle) toggle.click();
        }

        setTimeout(() => {
            if (window.terminalManager && window.terminalManager.sendCopilotPromptCommandNoEnter) {
                window.terminalManager.sendCopilotPromptCommandNoEnter(skillName);
            } else if (window.terminalManager && window.terminalManager.sendCopilotPromptCommand) {
                window.terminalManager.sendCopilotPromptCommand(skillName);
            } else {
                this._showToast('Console not available', 'error');
            }
        }, 300);
    },

    async _dispatchModalAction(wfName, actionKey) {
        // FEATURE-037-A: Compose Idea Modal
        if (actionKey === 'compose_idea' && typeof ComposeIdeaModal !== 'undefined') {
            const modal = new ComposeIdeaModal({
                workflowName: wfName,
                onComplete: () => {
                    // Re-render workflow view to reflect updated action state
                    const container = document.getElementById('workflow-view');
                    if (container && window.workflowView) {
                        window.workflowView.render(container);
                    }
                }
            });
            modal.open();
            return;
        }

        try {
            const resp = await fetch(`/api/workflow/${encodeURIComponent(wfName)}`);
            const json = await resp.json();
            const state = json.data || {};

            if (!state.idea_folder) {
                const folder = await this._showPromptModal('Link Idea Folder', 'Enter idea folder name to link:', 'my-app-idea');
                if (!folder) return;
                const linkResp = await fetch(`/api/workflow/${encodeURIComponent(wfName)}/link-idea`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ idea_folder: folder.trim() })
                });
                if (!linkResp.ok) {
                    const err = await linkResp.json();
                    this._showToast(err.message || 'Failed to link idea folder', 'error');
                    return;
                }
            }
            const wpBtn = document.getElementById('btn-workplace');
            if (wpBtn) wpBtn.click();
        } catch (e) {
            this._showToast('Failed to check idea folder', 'error');
        }
    },

    /** Show a prompt modal (replaces native prompt()). Returns a Promise<string|null>. */
    _showPromptModal(title, message, placeholder) {
        return new Promise(resolve => {
            const overlay = document.createElement('div');
            overlay.className = 'workflow-modal-overlay';

            const modal = document.createElement('div');
            modal.className = 'workflow-modal';
            modal.innerHTML = `
                <h3>${title}</h3>
                <p style="color:#94a3b8;margin:8px 0 12px">${message}</p>
                <input type="text" id="wf-prompt-input" placeholder="${placeholder || ''}" autocomplete="off" />
                <div class="workflow-modal-error" id="wf-prompt-error"></div>
                <div class="workflow-modal-actions">
                    <button id="wf-prompt-cancel">Cancel</button>
                    <button id="wf-prompt-ok" class="btn-primary">OK</button>
                </div>`;
            overlay.appendChild(modal);
            document.body.appendChild(overlay);

            const input = document.getElementById('wf-prompt-input');
            const errDiv = document.getElementById('wf-prompt-error');
            input.focus();

            const cleanup = (val) => { overlay.remove(); resolve(val); };

            document.getElementById('wf-prompt-cancel').onclick = () => cleanup(null);
            overlay.onclick = (e) => { if (e.target === overlay) cleanup(null); };
            input.onkeydown = (e) => { if (e.key === 'Enter') document.getElementById('wf-prompt-ok').click(); };
            document.getElementById('wf-prompt-ok').onclick = () => {
                const v = input.value.trim();
                if (!v) { errDiv.textContent = 'Value is required'; return; }
                cleanup(v);
            };
        });
    },

    // ─── FEATURE-036-D: Feature Lanes & Dependencies ────────────

    /** Collect all features from per-feature stages. */
    _collectFeatures(stages) {
        const feats = {};
        for (const s of ['implement', 'validation', 'feedback']) {
            const st = stages[s] || {};
            if (st.features) {
                Object.entries(st.features).forEach(([id, data]) => {
                    if (!feats[id]) feats[id] = { ...data, _id: id };
                });
            }
        }
        return feats;
    },

    /** Render toolbar with Dependencies toggle. */
    _renderToolbar(stages, nextAction, wfName, workflowState) {
        const wrap = document.createElement('div');
        wrap.className = 'feature-selector-wrap';

        // Dependencies toggle
        const depToggle = document.createElement('span');
        depToggle.className = 'dep-toggle active';
        depToggle.innerHTML = '<span class="dep-toggle-icon">⑆</span> Dependencies';
        depToggle.onclick = () => this._toggleDeps(wrap.parentElement, depToggle);
        wrap.appendChild(depToggle);

        return wrap;
    },

    /** Toggle dependency visibility. */
    _toggleDeps(parent, toggle) {
        const container = parent.querySelector('.lanes-container');
        if (container) container.classList.toggle('deps-hidden');
        toggle.classList.toggle('active');
    },

    /** Render feature lanes container with SVG overlay. */
    _renderFeatureLanes(stages, nextAction, wfName) {
        const wrapper = document.createElement('div');
        wrapper.className = 'feature-lanes-area';

        // Header with title and legend
        const hdr = document.createElement('div');
        hdr.className = 'feature-lanes-header';
        hdr.innerHTML = `
            <span class="feature-lanes-title">Feature Lanes — Per-Feature Progress</span>
            <div class="feature-lanes-legend">
                <div class="feature-lanes-legend-item"><span class="feature-lanes-legend-dot done"></span> Done</div>
                <div class="feature-lanes-legend-item"><span class="feature-lanes-legend-dot active"></span> Active</div>
                <div class="feature-lanes-legend-item"><span class="feature-lanes-legend-dot pending"></span> Pending</div>
            </div>`;
        wrapper.appendChild(hdr);

        const container = document.createElement('div');
        container.className = 'lanes-container';

        const feats = this._collectFeatures(stages);
        const entries = Object.entries(feats);

        entries.forEach(([id, data], idx) => {
            container.appendChild(this._renderLane(id, data, stages, nextAction, wfName, idx === 0));
        });

        // SVG overlay
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'dep-svg-overlay');
        svg.id = 'dep-svg-' + wfName;
        container.appendChild(svg);

        // Draw arrows after render
        setTimeout(() => this._drawDepArrows(container), 100);
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => this._drawDepArrows(container), 200);
        });

        wrapper.appendChild(container);
        return wrapper;
    },

    /** Render a single feature lane. */
    _renderLane(featureId, featureData, stages, nextAction, wfName, highlighted) {
        const lane = document.createElement('div');
        lane.className = 'feature-lane' + (highlighted ? ' highlighted' : '');
        lane.dataset.feature = featureId;
        if (featureData.depends_on && featureData.depends_on.length > 0) {
            lane.dataset.dependsOn = featureData.depends_on.join(',');
        }

        // Label
        const label = document.createElement('div');
        label.className = 'lane-label';
        label.innerHTML = `
            <div class="lane-feature-id">${featureId}</div>
            <div class="lane-feature-name">${featureData.name || featureId}</div>`;
        label.appendChild(this._renderDepBadge(featureData));
        lane.appendChild(label);

        // Stages
        const stagesDiv = document.createElement('div');
        stagesDiv.className = 'lane-stages';
        const actions = featureData.actions || {};

        this.FEATURE_LANE_ACTIONS.forEach((act, i) => {
            if (i > 0) {
                const arrow = document.createElement('span');
                arrow.className = 'lane-arrow';
                arrow.textContent = '›';
                stagesDiv.appendChild(arrow);
            }
            const status = (actions[act.key] || {}).status || 'pending';
            const isSuggested = nextAction && nextAction.feature_id === featureId && nextAction.action === act.key;

            const dot = document.createElement('span');
            if (status === 'done') {
                dot.className = 'lane-stage done';
                dot.innerHTML = `<span>✓</span> ${act.label}`;
            } else if (status === 'in_progress' || isSuggested) {
                dot.className = 'lane-stage active';
                dot.innerHTML = `<span class="stage-dot"></span> ${act.label}`;
            } else {
                dot.className = 'lane-stage pending';
                dot.textContent = act.label;
            }

            dot.style.cursor = 'pointer';
            dot.onclick = (e) => {
                e.stopPropagation();
                if (status === 'done') {
                    this._showToast(`${act.label} is already completed for ${featureId}`, 'info');
                    return;
                }
                this._dispatchFeatureAction(wfName, featureId, act.key, featureData);
            };

            stagesDiv.appendChild(dot);
        });
        lane.appendChild(stagesDiv);

        lane.onclick = () => {
            lane.parentElement.querySelectorAll('.feature-lane').forEach(l => l.classList.remove('highlighted'));
            lane.classList.add('highlighted');
        };

        return lane;
    },

    /** Render dependency badge: ⛓ needs or ⇉ Parallel. */
    _renderDepBadge(featureData) {
        const badge = document.createElement('span');
        if (featureData.depends_on && featureData.depends_on.length > 0) {
            badge.className = 'dep-tag depends';
            badge.textContent = `⛓ needs ${featureData.depends_on.join(', ')}`;
        } else {
            badge.className = 'dep-tag parallel';
            badge.textContent = '⇉ Parallel';
        }
        return badge;
    },

    /** Draw SVG dependency arrows in left gutter between lanes. */
    _drawDepArrows(container) {
        const svg = container.querySelector('.dep-svg-overlay');
        if (!svg) return;
        svg.innerHTML = '';
        const cRect = container.getBoundingClientRect();
        const gutterX = 12;

        const lanes = container.querySelectorAll('.feature-lane[data-feature]');
        const laneMap = {};
        lanes.forEach(lane => { laneMap[lane.dataset.feature] = lane; });

        lanes.forEach(lane => {
            const deps = lane.dataset.dependsOn;
            if (!deps) return;
            deps.split(',').forEach(dep => {
                const srcLane = laneMap[dep.trim()];
                if (!srcLane) return;

                const srcRect = srcLane.getBoundingClientRect();
                const tgtRect = lane.getBoundingClientRect();

                const y1 = srcRect.bottom - cRect.top;
                const y2 = tgtRect.top - cRect.top;

                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.setAttribute('d', `M ${gutterX} ${y1} L ${gutterX} ${y2 - 4}`);
                path.setAttribute('class', 'dep-arrow-line');
                svg.appendChild(path);

                const arrowSize = 5;
                const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
                arrow.setAttribute('points', `${gutterX},${y2} ${gutterX - arrowSize},${y2 - arrowSize * 1.6} ${gutterX + arrowSize},${y2 - arrowSize * 1.6}`);
                arrow.setAttribute('class', 'dep-arrow-head');
                svg.appendChild(arrow);
            });
        });
    },

    /** Dispatch feature-level action with dependency check. */
    async _dispatchFeatureAction(wfName, featureId, actionKey, featureData) {
        // Check dependencies first
        if (featureData.depends_on && featureData.depends_on.length > 0) {
            try {
                const resp = await fetch(`/api/workflow/${encodeURIComponent(wfName)}/dependencies/${encodeURIComponent(featureId)}`);
                const json = await resp.json();
                if (json.data && json.data.blocked) {
                    const blockerList = json.data.blockers.map(b => `${b.feature_id} (${b.current_stage})`).join(', ');
                    const proceed = await this._showDependencyConfirm(featureId, blockerList);
                    if (!proceed) return;
                }
            } catch (e) {
                // If check fails, proceed with warning
            }
        }

        // Find the skill for this action from ACTION_MAP
        const skillMap = {};
        for (const stage of Object.values(this.ACTION_MAP)) {
            for (const [k, v] of Object.entries(stage.actions || {})) {
                if (v.skill) skillMap[k] = v.skill;
            }
        }
        const skill = skillMap[actionKey];
        if (skill) {
            this._dispatchCliAction(wfName, actionKey, skill, null, featureId);
        } else {
            this._showToast(`Action ${actionKey} not yet available`, 'info');
        }
    },

    /** Show dependency confirmation modal (custom, NOT native). */
    _showDependencyConfirm(featureId, blockerList) {
        return new Promise(resolve => {
            const overlay = document.createElement('div');
            overlay.className = 'workflow-modal-overlay';

            const modal = document.createElement('div');
            modal.className = 'workflow-modal';
            modal.innerHTML = `
                <h3>⚠️ Dependency Warning</h3>
                <p style="color:#94a3b8;margin:8px 0 12px">
                    <strong>${featureId}</strong> has unfinished dependencies:<br/>
                    <span style="color:#f59e0b">${blockerList}</span>
                </p>
                <p style="color:#64748b;font-size:12px">Proceeding may cause issues if dependent features are not complete.</p>
                <div class="workflow-modal-actions">
                    <button id="wf-dep-cancel">Cancel</button>
                    <button id="wf-dep-proceed" class="btn-primary" style="background:#f59e0b">Proceed Anyway</button>
                </div>`;
            overlay.appendChild(modal);
            document.body.appendChild(overlay);

            const cleanup = (val) => { overlay.remove(); resolve(val); };
            document.getElementById('wf-dep-cancel').onclick = () => cleanup(false);
            document.getElementById('wf-dep-proceed').onclick = () => cleanup(true);
            overlay.onclick = (e) => { if (e.target === overlay) cleanup(false); };
        });
    },

    /** Get status icon for a feature. */
    _getFeatureStatusIcon(data) {
        const actions = data.actions || {};
        const statuses = Object.values(actions).map(a => a.status || 'pending');
        if (statuses.length > 0 && statuses.every(s => s === 'done')) return '✅';
        if (statuses.some(s => s === 'in_progress' || s === 'done')) return '🔄';
        return '⏳';
    },

    /** Get current stage label for a feature. */
    _getFeatureCurrentStage(data) {
        const actions = data.actions || {};
        for (const act of this.FEATURE_LANE_ACTIONS) {
            const status = (actions[act.key] || {}).status || 'pending';
            if (status !== 'done') return act.label;
        }
        return 'Completed';
    },

    /** Render deliverables section (FEATURE-036-E). */
    async _renderDeliverables(container, wfName) {
        const area = document.createElement('div');
        area.className = 'deliverables-area';

        const header = document.createElement('div');
        header.className = 'deliverables-header';
        const title = document.createElement('span');
        title.className = 'deliverables-title';
        title.textContent = 'Deliverables';
        const countBadge = document.createElement('span');
        countBadge.className = 'deliverables-count';
        countBadge.textContent = '…';
        title.appendChild(countBadge);
        header.appendChild(title);
        const toggle = document.createElement('span');
        toggle.className = 'deliverables-toggle';
        toggle.textContent = '▾';
        header.appendChild(toggle);
        area.appendChild(header);

        const grid = document.createElement('div');
        grid.className = 'deliverables-grid';
        area.appendChild(grid);

        header.onclick = () => {
            const hidden = grid.style.display === 'none';
            grid.style.display = hidden ? '' : 'none';
            toggle.textContent = hidden ? '▾' : '▸';
        };

        container.appendChild(area);

        try {
            const resp = await fetch(`/api/workflow/${encodeURIComponent(wfName)}/deliverables`);
            const json = await resp.json();
            const data = json.data || {};
            const items = data.deliverables || [];
            countBadge.textContent = items.length;
            if (items.length === 0) {
                const empty = document.createElement('div');
                empty.className = 'deliverables-empty';
                empty.textContent = 'No deliverables yet';
                grid.appendChild(empty);
            } else {
                const viewer = typeof DeliverableViewer !== 'undefined'
                    ? new DeliverableViewer({ workflowName: wfName }) : null;
                const folderModal = typeof FolderBrowserModal !== 'undefined'
                    ? new FolderBrowserModal({ workflowName: wfName }) : null;

                // CR-001: Group deliverables by feature instead of by stage
                const shared = [];
                const byFeature = {};
                items.forEach(item => {
                    if (!item.feature_id) {
                        shared.push(item);
                    } else {
                        const fid = item.feature_id;
                        if (!byFeature[fid]) byFeature[fid] = { name: item.feature_name || fid, items: [] };
                        byFeature[fid].items.push(item);
                    }
                });

                const renderCard = (item) => {
                    if (viewer && DeliverableViewer.isFolderType(item.path)) {
                        const card = viewer.renderFolderDeliverable(item);
                        if (folderModal) {
                            card.addEventListener('click', () => folderModal.open(item.path));
                        }
                        return card;
                    } else {
                        const card = this._renderDeliverableCard(item);
                        if (viewer && item.exists) {
                            viewer.makeClickableForPreview(card, item.path, { exists: item.exists });
                        }
                        return card;
                    }
                };

                // CR-001: Render shared section, then per-feature sections
                const createSection = (titleText, sectionItems) => {
                    const section = document.createElement('div');
                    section.className = 'deliverables-feature-section';
                    const sTitle = document.createElement('div');
                    sTitle.className = 'deliverables-feature-section-title';
                    sTitle.textContent = titleText;
                    section.appendChild(sTitle);
                    const row = document.createElement('div');
                    row.className = 'deliverables-row';
                    sectionItems.forEach(item => row.appendChild(renderCard(item)));
                    section.appendChild(row);
                    return section;
                };

                if (shared.length > 0) {
                    grid.appendChild(createSection('Shared Deliverables', shared));
                }
                for (const [fid, fdata] of Object.entries(byFeature)) {
                    const sectionTitle = fdata.name === fid ? fid : `${fid} — ${fdata.name}`;
                    grid.appendChild(createSection(sectionTitle, fdata.items));
                }
            }
        } catch {
            countBadge.textContent = '!';
            const err = document.createElement('div');
            err.className = 'deliverables-empty';
            err.textContent = 'Failed to load deliverables';
            grid.appendChild(err);
        }
    },

    /** Render a single deliverable card. */
    _renderDeliverableCard(item) {
        const card = document.createElement('div');
        card.className = `deliverable-card${item.exists ? '' : ' missing'}`;

        const catConfig = this.DELIVERABLE_ICONS[item.category] || { icon: '📄', label: 'Other' };
        const iconEl = document.createElement('div');
        iconEl.className = `deliverable-icon ${item.category || ''}`;
        iconEl.textContent = catConfig.icon;
        card.appendChild(iconEl);

        const info = document.createElement('div');
        info.className = 'deliverable-info';
        const nameEl = document.createElement('div');
        nameEl.className = 'deliverable-name';
        nameEl.textContent = item.name;
        info.appendChild(nameEl);
        const pathEl = document.createElement('div');
        pathEl.className = 'deliverable-path';
        pathEl.textContent = (item.path || '').replace(/^x-ipe-docs\//, '');
        info.appendChild(pathEl);
        if (!item.exists) {
            const badge = document.createElement('div');
            badge.className = 'deliverable-missing-badge';
            badge.textContent = '⚠️ not found';
            info.appendChild(badge);
        }
        card.appendChild(info);
        return card;
    },

    /** Render context menu for manual override (FEATURE-036-E). */
    _renderContextMenu(x, y, actionKey, wfName, featureId) {
        // Remove any existing context menu
        document.querySelectorAll('.wf-context-menu').forEach(m => m.remove());

        const menu = document.createElement('div');
        menu.className = 'wf-context-menu';
        menu.style.left = `${Math.min(x, window.innerWidth - 180)}px`;
        menu.style.top = `${Math.min(y, window.innerHeight - 80)}px`;

        const items = [
            { label: '✅ Mark as Done', status: 'done' },
            { label: '🔄 Reset to Pending', status: 'pending' },
        ];
        items.forEach(opt => {
            const item = document.createElement('button');
            item.className = 'wf-context-menu-item';
            item.textContent = opt.label;
            item.onclick = async (e) => {
                e.stopPropagation();
                menu.remove();
                const body = { action: actionKey, status: opt.status };
                if (featureId) body.feature_id = featureId;
                try {
                    const resp = await fetch(`/api/workflow/${encodeURIComponent(wfName)}/action`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(body),
                    });
                    if (resp.ok) {
                        this._showToast(`${actionKey} → ${opt.status}`, 'success');
                    } else {
                        const err = await resp.json();
                        this._showToast(err.message || 'Failed', 'error');
                    }
                } catch {
                    this._showToast('Network error', 'error');
                }
            };
            menu.appendChild(item);
        });

        document.body.appendChild(menu);
        const closeHandler = (e) => {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', closeHandler);
            }
        };
        setTimeout(() => document.addEventListener('click', closeHandler), 10);
    },

    _showToast(msg, type) {
        const toast = document.createElement('div');
        toast.className = `workflow-toast ${type || 'info'}`;
        toast.textContent = msg;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }
};
