/**
 * FEATURE-036-C: Stage Ribbon & Action Execution
 * Renders stage progression ribbon and action buttons inside workflow panels.
 */
const workflowStage = {
    STAGE_ORDER: ['ideation', 'requirement', 'implement', 'validation', 'feedback'],

    ACTION_MAP: {
        ideation: {
            label: 'Ideation',
            actions: {
                compose_idea:   { label: 'Compose Idea',   icon: '📝', mandatory: true,  interaction: 'modal' },
                reference_uiux: { label: 'Reference UIUX', icon: '🎨', mandatory: false, interaction: 'cli', skill: 'x-ipe-tool-uiux-reference' },
                refine_idea:    { label: 'Refine Idea',    icon: '💡', mandatory: true,  interaction: 'cli', skill: 'x-ipe-task-based-ideation-v2' },
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
                quality_evaluation: { label: 'Quality Evaluation', icon: '📊', mandatory: false, interaction: 'cli', skill: null, deferred: true },
            }
        },
        feedback: {
            label: 'Feedback',
            actions: {
                change_request: { label: 'Change Request', icon: '🔄', mandatory: false, interaction: 'cli', skill: 'x-ipe-task-based-change-request' },
            }
        }
    },

    /** Main entry: render stage ribbon + actions into container. */
    render(container, workflowState, nextAction, workflowName) {
        container.appendChild(this._renderRibbon(workflowState.stages));
        container.appendChild(this._renderActionsArea(workflowState.stages, nextAction, workflowName));
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
        } else if (status === 'locked') {
            pill.innerHTML = `<span class="stage-num">🔒</span> ${label}`;
        } else {
            pill.innerHTML = `<span class="stage-num">${index + 1}</span> ${label}`;
        }
        return pill;
    },

    _renderActionsArea(stages, nextAction, wfName) {
        const area = document.createElement('div');
        area.className = 'actions-area';

        // Group completed stages together under "COMPLETED ACTIONS"
        const completedStages = this.STAGE_ORDER.filter(s => (stages[s] || {}).status === 'completed');
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
                    const apiStatus = (apiActions[key] || {}).status || 'pending';
                    grid.appendChild(this._renderActionButton(key, def, apiStatus, false, false, wfName));
                });
            });
            group.appendChild(grid);
            area.appendChild(group);
        }

        // Active stage with "{STAGE_NAME} Actions" label
        const activeStage = this.STAGE_ORDER.find(s => (stages[s] || {}).status === 'in_progress');
        if (activeStage) {
            const stageConfig = this.ACTION_MAP[activeStage];
            if (stageConfig) {
                area.appendChild(this._renderActionGroup(activeStage, (stages[activeStage] || {}).actions || {}, nextAction, wfName, false, null));
            }
        }

        // First locked stage as preview
        const firstLocked = this.STAGE_ORDER.find(s => (stages[s] || {}).status === 'locked');
        if (firstLocked) {
            // Find the previous stage name for the unlock hint
            const lockedIdx = this.STAGE_ORDER.indexOf(firstLocked);
            const prevStageName = lockedIdx > 0 ? (this.ACTION_MAP[this.STAGE_ORDER[lockedIdx - 1]] || {}).label || this.STAGE_ORDER[lockedIdx - 1] : '';
            area.appendChild(this._renderActionGroup(firstLocked, {}, nextAction, wfName, true, prevStageName));
        }

        return area;
    },

    _renderActionGroup(stageName, apiActions, nextAction, wfName, locked, prevStageName) {
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

        Object.entries(stageConfig.actions).forEach(([key, def]) => {
            const apiStatus = (apiActions[key] || {}).status || 'pending';
            const isSuggested = nextAction && nextAction.action === key && nextAction.stage === stageName;
            grid.appendChild(this._renderActionButton(key, def, apiStatus, isSuggested, locked, wfName));
        });

        group.appendChild(grid);
        return group;
    },

    _renderActionButton(actionKey, actionDef, status, isSuggested, locked, wfName) {
        const btn = document.createElement('button');

        let stateClass;
        if (locked) stateClass = 'locked';
        else if (status === 'done') stateClass = 'done';
        else if (isSuggested) stateClass = 'suggested';
        else stateClass = 'normal';

        btn.className = `action-btn ${stateClass}`;

        if (actionDef.deferred) {
            btn.classList.add('locked');
            btn.title = 'Coming Soon';
        } else if (locked) {
            btn.title = 'Complete previous stages to unlock this action';
        }

        btn.innerHTML = `<span class="action-icon">${actionDef.icon}</span> ${actionDef.label}`;

        btn.onclick = (e) => {
            e.stopPropagation();
            if (locked || actionDef.deferred) {
                this._showToast(locked ? `Complete previous stages to unlock ${actionDef.label}` : 'This action is coming soon', 'info');
                return;
            }
            if (status === 'done') {
                this._showToast(`${actionDef.label} is already completed`, 'info');
                return;
            }
            if (actionDef.interaction === 'modal') {
                this._dispatchModalAction(wfName);
            } else {
                this._dispatchCliAction(wfName, actionKey, actionDef.skill);
            }
        };

        return btn;
    },

    async _dispatchCliAction(wfName, actionKey, skillName) {
        if (!skillName) {
            this._showToast('This action is not yet available', 'error');
            return;
        }

        // Open console if hidden
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

    async _dispatchModalAction(wfName) {
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

    _showToast(msg, type) {
        const toast = document.createElement('div');
        toast.className = `workflow-toast ${type || 'info'}`;
        toast.textContent = msg;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }
};
