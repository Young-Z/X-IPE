/**
 * Toolbox Modal
 * FEATURE-011: Comprehensive tool management modal
 * 
 * Provides a centralized UI for managing tools across all development stages.
 * Dynamically renders tools based on x-ipe-docs/config/tools.json content.
 */
class StageToolboxModal {
    constructor(options = {}) {
        this.containerId = options.containerId || 'stage-toolbox-modal';
        this.apiEndpoint = options.apiEndpoint || '/api/config/tools';
        this.themesApiEndpoint = options.themesApiEndpoint || '/api/themes';
        this.overlay = null;
        this.modal = null;
        this.config = null;
        this.themes = [];
        this.selectedTheme = null;  // null means no theme selected
        this.isLoading = false;
        
        // Stage metadata (display info only - tools come from config)
        // Order matters - this defines display order
        this.stageOrder = ['ideation', 'requirement', 'feature', 'quality', 'refactoring'];
        
        this.stageMeta = {
            ideation: {
                icon: 'bi-lightbulb',
                title: 'Ideation Stage',
                subtitle: 'Brainstorm and visualize ideas'
            },
            requirement: {
                icon: 'bi-clipboard-check',
                title: 'Requirement Stage',
                subtitle: 'Gather and analyze requirements'
            },
            feature: {
                icon: 'bi-code-slash',
                title: 'Feature Stage',
                subtitle: 'Design and implement features'
            },
            quality: {
                icon: 'bi-shield-check',
                title: 'Quality Stage',
                subtitle: 'Testing and validation'
            },
            refactoring: {
                icon: 'bi-arrow-repeat',
                title: 'Refactoring Stage',
                subtitle: 'Optimize and improve code'
            }
        };
        
        // Phase labels for display
        this.phaseLabels = {
            ideation: 'Brainstorming',
            mockup: 'Mockup & Prototyping',
            sharing: 'Sharing & Export',
            architecture: 'Architecture',
            gathering: 'Gathering',
            analysis: 'Analysis',
            design: 'Design',
            implementation: 'Implementation',
            review: 'Review',
            testing: 'Testing',
            execution: 'Execution'
        };
        
        this._init();
    }
    
    _init() {
        this._createModal();
        this._bindEvents();
    }
    
    _createModal() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.id = this.containerId;
        this.overlay.className = 'toolbox-modal-overlay';
        
        this.overlay.innerHTML = `
            <div class="toolbox-modal">
                <div class="toolbox-modal-header">
                    <div class="toolbox-modal-title">
                        <i class="bi bi-tools"></i>
                        Toolbox
                    </div>
                    <button class="toolbox-modal-close" aria-label="Close">&times;</button>
                </div>
                <div class="toolbox-modal-body">
                    <div class="toolbox-themes-section">
                        <div class="toolbox-themes-header">
                            <i class="bi bi-palette2"></i>
                            <span>Design Themes</span>
                        </div>
                        <div class="toolbox-themes-grid" id="themes-grid">
                            <div class="toolbox-themes-loading">Loading themes...</div>
                        </div>
                    </div>
                    <div id="toolbox-stages-container">
                        <div class="toolbox-loading">Loading tools configuration...</div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.overlay);
        this.modal = this.overlay.querySelector('.toolbox-modal');
    }
    
    _renderAccordions() {
        if (!this.config || !this.config.stages) {
            return '<div class="toolbox-empty">No configuration loaded</div>';
        }
        
        // Render stages in defined order
        return this.stageOrder
            .filter(stageKey => this.config.stages[stageKey])
            .map(stageKey => {
                const stageConfig = this.config.stages[stageKey];
                const meta = this.stageMeta[stageKey] || {
                    icon: 'bi-gear',
                    title: stageKey.charAt(0).toUpperCase() + stageKey.slice(1) + ' Stage',
                    subtitle: 'Configure tools for this stage'
                };
            
            const hasTools = this._stageHasTools(stageConfig);
            const isIdeation = stageKey === 'ideation';
            
            return `
                <div class="toolbox-accordion ${isIdeation ? 'expanded' : ''}" 
                     data-stage="${stageKey}">
                    <div class="toolbox-accordion-header">
                        <div class="toolbox-accordion-icon">
                            <i class="bi ${meta.icon}"></i>
                        </div>
                        <div class="toolbox-accordion-info">
                            <div class="toolbox-accordion-title">${meta.title}</div>
                            <div class="toolbox-accordion-subtitle">${meta.subtitle}</div>
                        </div>
                        <div class="toolbox-accordion-badge ${hasTools ? 'active' : ''}">
                            ${hasTools ? '• Active' : 'No Tools'}
                        </div>
                        <i class="bi bi-chevron-down toolbox-accordion-chevron"></i>
                    </div>
                    <div class="toolbox-accordion-content">
                        <div class="toolbox-accordion-body">
                            ${this._renderStageContent(stageKey, stageConfig)}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    _stageHasTools(stageConfig) {
        if (!stageConfig) return false;
        return Object.values(stageConfig).some(phase => 
            typeof phase === 'object' && Object.keys(phase).filter(k => k !== '_order').length > 0
        );
    }
    
    _renderStageContent(stageKey, stageConfig) {
        if (!stageConfig || Object.keys(stageConfig).length === 0) {
            return `<div class="toolbox-empty">No phases configured for this stage</div>`;
        }
        
        const phases = Object.entries(stageConfig)
            .filter(([_, phase]) => typeof phase === 'object')
            .sort((a, b) => {
                // Sort by _order field, default to 999 if not specified
                const orderA = a[1]._order ?? 999;
                const orderB = b[1]._order ?? 999;
                return orderA - orderB;
            });
        
        if (phases.length === 0) {
            return `<div class="toolbox-empty">No tools configured for this stage</div>`;
        }
        
        return phases.map(([phaseKey, phaseTools]) => {
            // Filter out _order from tool names
            const toolNames = Object.keys(phaseTools).filter(key => key !== '_order' && key !== '_extra_instruction');
            const phaseLabel = this.phaseLabels[phaseKey] || 
                (phaseKey.charAt(0).toUpperCase() + phaseKey.slice(1));
            const existingInstruction = phaseTools._extra_instruction || '';
            
            if (toolNames.length === 0) {
                return `
                    <div class="toolbox-phase" data-phase="${phaseKey}">
                        <div class="toolbox-phase-label">${phaseLabel}</div>
                        <div class="toolbox-empty">No tools available yet</div>
                        ${this._renderExtraInstruction(stageKey, phaseKey, existingInstruction)}
                    </div>
                `;
            }
            
            return `
                <div class="toolbox-phase" data-phase="${phaseKey}">
                    <div class="toolbox-phase-label">${phaseLabel}</div>
                    <div class="toolbox-phase-tools">
                        ${toolNames.map(tool => `
                            <div class="toolbox-tool" data-stage="${stageKey}" data-phase="${phaseKey}" data-tool="${tool}">
                                <span class="toolbox-tool-name">${this._formatToolName(tool)}</span>
                                <label class="toolbox-toggle">
                                    <input type="checkbox" data-tool="${tool}" ${phaseTools[tool] ? 'checked' : ''}>
                                    <span class="toolbox-toggle-slider"></span>
                                </label>
                            </div>
                        `).join('')}
                    </div>
                    ${this._renderExtraInstruction(stageKey, phaseKey, existingInstruction)}
                </div>
            `;
        }).join('');
    }
    
    _formatToolName(tool) {
        // Convert "tool-frontend-design" to "Frontend Design"
        return tool
            .replace(/^tool-/, '')
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    _renderExtraInstruction(stageKey, phaseKey, existingInstruction) {
        return `
            <div class="toolbox-extra-instruction" data-stage="${stageKey}" data-phase="${phaseKey}">
                <label class="toolbox-extra-instruction-label">Extra Instruction</label>
                <textarea 
                    class="toolbox-extra-instruction-input" 
                    data-stage="${stageKey}" 
                    data-phase="${phaseKey}"
                    placeholder="Add custom instructions for this phase (max 200 words)..."
                    maxlength="2000"
                >${existingInstruction}</textarea>
                <div class="toolbox-extra-instruction-counter">
                    <span class="word-count">${this._countWords(existingInstruction)}</span> / 200 words
                </div>
            </div>
        `;
    }
    
    _countWords(text) {
        if (!text || text.trim() === '') return 0;
        return text.trim().split(/\s+/).length;
    }
    
    _bindEvents() {
        // Close button
        const closeBtn = this.overlay.querySelector('.toolbox-modal-close');
        closeBtn.addEventListener('click', () => this.close());
        
        // Overlay click
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });
        
        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });
    }
    
    _bindAccordionEvents() {
        // Accordion headers
        this.overlay.querySelectorAll('.toolbox-accordion-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const accordion = header.closest('.toolbox-accordion');
                
                accordion.classList.toggle('expanded');
                
                // Collapse other accordions
                this.overlay.querySelectorAll('.toolbox-accordion').forEach(other => {
                    if (other !== accordion) {
                        other.classList.remove('expanded');
                    }
                });
            });
        });
        
        // Toggle switches
        this.overlay.querySelectorAll('.toolbox-toggle input').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                this._handleToggle(e.target);
            });
        });
        
        // Extra instruction textareas
        this.overlay.querySelectorAll('.toolbox-extra-instruction-input').forEach(textarea => {
            textarea.addEventListener('input', (e) => {
                this._handleExtraInstructionInput(e.target);
            });
            textarea.addEventListener('blur', (e) => {
                this._handleExtraInstructionSave(e.target);
            });
        });
    }
    
    async _handleToggle(toggleInput) {
        if (!this.config || this.isLoading) return;
        
        const toolItem = toggleInput.closest('.toolbox-tool');
        const stage = toolItem.dataset.stage;
        const phase = toolItem.dataset.phase;
        const tool = toolItem.dataset.tool;
        const enabled = toggleInput.checked;
        
        // Update local config
        if (!this.config.stages[stage]) {
            this.config.stages[stage] = {};
        }
        if (!this.config.stages[stage][phase]) {
            this.config.stages[stage][phase] = {};
        }
        this.config.stages[stage][phase][tool] = enabled;
        
        // Save immediately
        await this._saveConfig();
        
        // Update badge counts
        this._updateBadges();
    }
    
    _handleExtraInstructionInput(textarea) {
        const text = textarea.value;
        const wordCount = this._countWords(text);
        const container = textarea.closest('.toolbox-extra-instruction');
        const counter = container.querySelector('.word-count');
        
        counter.textContent = wordCount;
        
        // Visual feedback for word limit
        if (wordCount > 200) {
            container.classList.add('over-limit');
            // Trim to 200 words
            const words = text.trim().split(/\s+/).slice(0, 200);
            textarea.value = words.join(' ');
            counter.textContent = 200;
        } else {
            container.classList.remove('over-limit');
        }
    }
    
    async _handleExtraInstructionSave(textarea) {
        if (!this.config || this.isLoading) return;
        
        const stage = textarea.dataset.stage;
        const phase = textarea.dataset.phase;
        const instruction = textarea.value.trim();
        
        // Update local config
        if (!this.config.stages[stage]) {
            this.config.stages[stage] = {};
        }
        if (!this.config.stages[stage][phase]) {
            this.config.stages[stage][phase] = {};
        }
        
        if (instruction) {
            this.config.stages[stage][phase]._extra_instruction = instruction;
        } else {
            delete this.config.stages[stage][phase]._extra_instruction;
        }
        
        // Save config
        await this._saveConfig();
    }
    
    _updateBadges() {
        if (!this.config || !this.config.stages) return;
        
        Object.entries(this.config.stages).forEach(([stageKey, stageConfig]) => {
            const accordion = this.overlay.querySelector(`.toolbox-accordion[data-stage="${stageKey}"]`);
            if (!accordion) return;
            
            const badge = accordion.querySelector('.toolbox-accordion-badge');
            const { enabled, total } = this._countTools(stageConfig);
            
            if (enabled > 0) {
                badge.textContent = `${enabled} / ${total} Active`;
                badge.classList.add('active');
            } else if (total > 0) {
                badge.textContent = '• Inactive';
                badge.classList.remove('active');
            } else {
                badge.textContent = 'No Tools';
                badge.classList.remove('active');
            }
        });
    }
    
    _countTools(stageConfig) {
        let enabled = 0;
        let total = 0;
        
        if (!stageConfig) return { enabled, total };
        
        Object.values(stageConfig).forEach(phase => {
            if (typeof phase === 'object') {
                Object.entries(phase).forEach(([key, value]) => {
                    // Skip _order and _extra_instruction fields
                    if (key === '_order' || key === '_extra_instruction') return;
                    total++;
                    if (value === true) enabled++;
                });
            }
        });
        
        return { enabled, total };
    }
    
    async _loadConfig() {
        this.isLoading = true;
        try {
            // Load tools config and themes in parallel
            const [configResponse, themesResponse] = await Promise.all([
                fetch(this.apiEndpoint),
                fetch(this.themesApiEndpoint)
            ]);
            
            const configData = await configResponse.json();
            const themesData = await themesResponse.json();
            
            if (configData.success && configData.config) {
                this.config = configData.config;
                this._renderStagesFromConfig();
                
                // Load selected theme from config
                const selectedThemeConfig = this.config['selected-theme'];
                if (selectedThemeConfig && selectedThemeConfig['theme-name']) {
                    this.selectedTheme = selectedThemeConfig['theme-name'];
                } else {
                    this.selectedTheme = null;  // No theme selected
                }
            } else {
                console.error('Failed to load tools config:', configData.error);
            }
            
            // Load available themes
            this.themes = themesData.themes || [];
            this._renderThemesSection();
            
        } catch (error) {
            console.error('Error loading config:', error);
        } finally {
            this.isLoading = false;
        }
    }
    
    _renderStagesFromConfig() {
        const container = this.overlay.querySelector('#toolbox-stages-container');
        if (!container) return;
        
        container.innerHTML = this._renderAccordions();
        this._bindAccordionEvents();
        this._updateBadges();
    }
    
    _renderThemesSection() {
        const grid = this.overlay.querySelector('#themes-grid');
        if (!grid) return;
        
        if (this.themes.length === 0) {
            grid.innerHTML = '<div class="toolbox-themes-empty">No themes available</div>';
            return;
        }
        
        grid.innerHTML = this.themes.map(theme => {
            const isSelected = theme.name === this.selectedTheme;
            return `
                <div class="toolbox-theme-card ${isSelected ? 'selected' : ''}" 
                     data-theme="${theme.name}"
                     title="${theme.description || theme.name}">
                    <div class="theme-card-swatches">
                        ${this._generateColorSwatches(theme.colors)}
                    </div>
                    <div class="theme-card-info">
                        <div class="theme-card-name">${this._formatThemeName(theme.name)}</div>
                        <div class="theme-card-desc">${theme.description ? theme.description.slice(0, 50) : 'No description'}</div>
                    </div>
                    ${isSelected ? '<div class="theme-card-check"><i class="bi bi-check-circle-fill"></i></div>' : ''}
                </div>
            `;
        }).join('');
        
        // Bind theme card click handlers
        grid.querySelectorAll('.toolbox-theme-card').forEach(card => {
            card.addEventListener('click', () => this._handleThemeSelect(card.dataset.theme));
        });
    }
    
    _generateColorSwatches(colors) {
        if (!colors) return '<div class="theme-swatch" style="background: #888"></div>';
        
        return ['primary', 'secondary', 'accent', 'neutral']
            .map(key => colors[key] ? `<div class="theme-swatch" style="background: ${colors[key]}"></div>` : '')
            .join('');
    }
    
    _formatThemeName(name) {
        // Convert "theme-dark-mode" to "Dark Mode"
        return name.replace(/^theme-/, '')
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    async _handleThemeSelect(themeName) {
        if (this.isLoading) return;
        
        // Find the theme to get folder path
        const theme = this.themes.find(t => t.name === themeName);
        if (!theme) return;
        
        // Toggle selection: if already selected, deselect; otherwise select
        if (themeName === this.selectedTheme) {
            this.selectedTheme = null;
            delete this.config['selected-theme'];
        } else {
            this.selectedTheme = themeName;
            
            // Update config with new theme selection format
            this.config['selected-theme'] = {
                'theme-name': themeName,
                'theme-folder-path': `x-ipe-docs/themes/${themeName}`
            };
        }
        
        // Re-render themes to update checkmark
        this._renderThemesSection();
        
        // Save config
        await this._saveConfig();
    }
    
    async _saveConfig() {
        if (!this.config) return;
        
        this.isLoading = true;
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.config)
            });
            const data = await response.json();
            
            if (!data.success) {
                console.error('Failed to save tools config:', data.error);
            }
        } catch (error) {
            console.error('Error saving tools config:', error);
        } finally {
            this.isLoading = false;
        }
    }
    
    // Public API
    async open() {
        await this._loadConfig();
        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    close() {
        this.overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    isOpen() {
        return this.overlay.classList.contains('active');
    }
    
    toggle() {
        if (this.isOpen()) {
            this.close();
        } else {
            this.open();
        }
    }
    
    /**
     * Check if a specific tool is enabled
     * @param {string} stage - Stage name (e.g., 'ideation')
     * @param {string} phase - Phase name (e.g., 'mockup')
     * @param {string} tool - Tool name (e.g., 'tool-frontend-design')
     * @returns {boolean}
     */
    isToolEnabled(stage, phase, tool) {
        return this.config?.stages?.[stage]?.[phase]?.[tool] ?? false;
    }
}

// Export for use
window.StageToolboxModal = StageToolboxModal;
