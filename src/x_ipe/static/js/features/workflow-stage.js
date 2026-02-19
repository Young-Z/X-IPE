/**
 * FEATURE-036-C: Stage Ribbon & Action Execution
 * FEATURE-036-D: Feature Lanes & Dependencies
 * FEATURE-036-E: Deliverables, Polling & Lifecycle
 * Renders stage progression ribbon, action buttons, feature lanes, and deliverables.
 */
const workflowStage = {
    STAGE_ORDER: ['ideation', 'requirement', 'implement', 'validation', 'feedback'],

    FEATURE_LANE_ACTIONS: [
        { key: 'feature_refinement', label: 'Refinement',  icon: '📐' },
        { key: 'technical_design',   label: 'Tech Design', icon: '⚙' },
        { key: 'implementation',     label: 'Implement',   icon: '💻' },
        { key: 'acceptance_testing', label: 'Testing',     icon: '✅' },
        { key: 'quality_evaluation', label: 'Quality',     icon: '📊' },
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

    /** Main entry: render stage ribbon + actions (or feature lanes) + deliverables into container. */
    render(container, workflowState, nextAction, workflowName) {
        container.appendChild(this._renderRibbon(workflowState.stages));
        if (this._hasFeatures(workflowState.stages)) {
            container.appendChild(this._renderFeatureSelector(workflowState.stages, nextAction, workflowName));
            container.appendChild(this._renderFeatureLanes(workflowState.stages, nextAction, workflowName));
        } else {
            container.appendChild(this._renderActionsArea(workflowState.stages, nextAction, workflowName));
        }
        this._renderDeliverables(container, workflowName);
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
                this._showToast(`${actionDef.label} is already completed`, 'info');
                return;
            }
            if (actionDef.interaction === 'modal') {
                this._dispatchModalAction(wfName, actionKey);
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

    /** Render feature selector dropdown. */
    _renderFeatureSelector(stages, nextAction, wfName) {
        const wrap = document.createElement('div');
        wrap.className = 'feature-selector-wrap';

        const btn = document.createElement('button');
        btn.className = 'feature-selector-btn';
        btn.innerHTML = 'Select Feature to Work On ▼';

        const dropdown = document.createElement('div');
        dropdown.className = 'feature-selector-dropdown';

        const header = document.createElement('div');
        header.className = 'feature-selector-header';
        header.textContent = 'Select Feature to Work On';
        dropdown.appendChild(header);

        const feats = this._collectFeatures(stages);
        Object.entries(feats).forEach(([id, data], idx) => {
            const item = document.createElement('div');
            item.className = 'feature-selector-item';
            item.dataset.featureId = id;
            if (idx === 0) item.classList.add('selected');

            const icon = this._getFeatureStatusIcon(data);
            const stageName = this._getFeatureCurrentStage(data);
            const nextAct = nextAction && nextAction.feature_id === id ? nextAction.action : '';

            item.innerHTML = `
                <span class="feature-selector-icon">${icon}</span>
                <div class="feature-selector-info">
                    <div class="feature-selector-name">${id} · ${data.name || id}</div>
                    <div class="feature-selector-stage">${stageName}</div>
                </div>
                ${nextAct ? `<span class="feature-selector-next">→ ${nextAct.replace(/_/g, ' ')}</span>` : ''}`;

            item.onclick = (e) => {
                e.stopPropagation();
                dropdown.querySelectorAll('.feature-selector-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                const lanes = wrap.parentElement.querySelectorAll('.feature-lane');
                lanes.forEach((lane, i) => {
                    lane.classList.toggle('highlighted', lane.dataset.feature === id);
                });
                dropdown.classList.remove('open');
            };
            dropdown.appendChild(item);
        });

        btn.onclick = (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('open');
        };
        document.addEventListener('click', () => dropdown.classList.remove('open'));

        wrap.appendChild(btn);
        wrap.appendChild(dropdown);

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

        return container;
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

    /** Draw SVG dependency arrows between lanes. */
    _drawDepArrows(container) {
        const svg = container.querySelector('.dep-svg-overlay');
        if (!svg) return;
        svg.innerHTML = '';
        const cRect = container.getBoundingClientRect();

        const lanes = container.querySelectorAll('.feature-lane[data-feature]');
        const laneMap = {};
        lanes.forEach(lane => { laneMap[lane.dataset.feature] = lane; });

        lanes.forEach(lane => {
            const deps = lane.dataset.dependsOn;
            if (!deps) return;
            deps.split(',').forEach(dep => {
                const srcLane = laneMap[dep.trim()];
                if (!srcLane) return;

                const srcLabel = srcLane.querySelector('.lane-label');
                const tgtLabel = lane.querySelector('.lane-label');
                const srcRect = srcLabel.getBoundingClientRect();
                const tgtRect = tgtLabel.getBoundingClientRect();

                const x1 = srcRect.left + srcRect.width / 2 - cRect.left;
                const y1 = srcRect.bottom - cRect.top;
                const x2 = tgtRect.left + tgtRect.width / 2 - cRect.left;
                const y2 = tgtRect.top - cRect.top;
                const midY = (y1 + y2) / 2;

                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.setAttribute('d', `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2 - 4}`);
                path.setAttribute('class', 'dep-arrow-line');
                svg.appendChild(path);

                const arrowSize = 5;
                const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
                arrow.setAttribute('points', `${x2},${y2} ${x2 - arrowSize},${y2 - arrowSize * 1.6} ${x2 + arrowSize},${y2 - arrowSize * 1.6}`);
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
            this._dispatchCliAction(wfName, actionKey, skill);
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
                items.forEach(item => grid.appendChild(this._renderDeliverableCard(item)));
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
        pathEl.textContent = item.path;
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
