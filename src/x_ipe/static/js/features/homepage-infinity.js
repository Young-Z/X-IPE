/**
 * Homepage Infinity Loop - FEATURE-026
 * 
 * Interactive visualization of the X-IPE development lifecycle.
 * Displays 8 stages on an infinity loop (∞) with clickable navigation.
 * Supports drag and drop repositioning with localStorage persistence.
 * Supports color customization via color picker.
 */

class HomepageInfinity {
    static sidebar = null;
    static tooltipTimeout = null;
    static dragState = null;
    static STORAGE_KEY = 'homepage-infinity-positions';
    static COLORS_STORAGE_KEY = 'homepage-infinity-colors';
    static activeColorPicker = null;
    
    static STAGE_MAPPING = {
        ideation: {
            icon: '💡',
            label: 'IDEATION',
            theme: 'control',
            status: 'ready',
            section: 'workplace',
            selector: '[data-path="x-ipe-docs/ideas"]',
            position: { left: '8.5%', top: '68%' }
        },
        requirement: {
            icon: '📋',
            label: 'REQUIREMENT',
            theme: 'control',
            status: 'ready',
            section: 'project',
            selector: '[data-path="x-ipe-docs/requirements"]',
            position: { left: '16%', top: '20.5%' }
        },
        implementation: {
            icon: '⚙️',
            label: 'IMPLEMENT',
            theme: 'control',
            status: 'ready',
            section: 'project',
            selector: '[data-path="x-ipe-docs/requirements"]',
            position: { left: '34%', top: '81.5%' }
        },
        deployment: {
            icon: '🚀',
            label: 'DEPLOY',
            theme: 'control',
            status: 'tbd',
            section: 'management',
            selector: null,
            position: { left: '60%', top: '27.5%' }
        },
        validation: {
            icon: '✅',
            label: 'VALIDATION',
            theme: 'transparency',
            status: 'ready',
            section: 'quality',
            selector: '[data-section="quality-report"]',
            position: { left: '83.8%', top: '21%' }
        },
        monitoring: {
            icon: '📊',
            label: 'MONITORING',
            theme: 'transparency',
            status: 'ready',
            section: 'quality',
            selector: '[data-section="behavior-tracing"]',
            position: { left: '88.7%', top: '73.5%' }
        },
        feedback: {
            icon: '💬',
            label: 'FEEDBACK',
            theme: 'transparency',
            status: 'ready',
            section: 'feedback',
            selector: '[data-section="uiux-feedback"]',
            position: { left: '62%', top: '78%' }
        },
        planning: {
            icon: '📅',
            label: 'PLANNING',
            theme: 'transparency',
            status: 'ready',
            section: 'management',
            selector: '[data-path="x-ipe-docs/planning"]',
            position: { left: '42%', top: '33.5%' }
        }
    };

    /**
     * Get HTML template for homepage
     * @returns {string} HTML template
     */
    static getTemplate() {
        const stageButtons = this._renderStageButtons();
        
        return `
<div class="homepage-infinity-container">
    <header class="homepage-header">
        <h1>X-IPE</h1>
        <p>AI-Powered Development Lifecycle</p>
    </header>
    
    <div class="infinity-loop-container">
        <div class="infinity-loop">
            <img src="/static/img/homepage-infinity-loop.png" 
                 alt="Development Lifecycle" 
                 class="infinity-bg"
                 onerror="this.style.display='none'">
            
            ${stageButtons}
            
            <span class="loop-label control">CONTROL</span>
            <span class="loop-label transparency">TRANSPARENCY</span>
        </div>
    </div>
    
    <footer class="homepage-legend">
        <span class="legend-control">● Control (What AI Does)</span>
        <span class="legend-transparency">● Transparency (What we see)</span>
    </footer>
    
    <div class="homepage-tooltip" id="homepage-tooltip" style="display: none;">
        <span class="tooltip-text"></span>
    </div>
</div>
`;
    }

    /**
     * Render stage buttons HTML
     * @returns {string} Stage buttons HTML
     */
    static _renderStageButtons() {
        const buttons = [];
        
        for (const [stageId, config] of Object.entries(this.STAGE_MAPPING)) {
            const tbdClass = config.status === 'tbd' ? ' tbd' : '';
            const tbdAttr = config.status === 'tbd' ? ' data-tbd="true"' : '';
            const tbdBadge = config.status === 'tbd' ? '<span class="tbd-badge">TBD</span>' : '';
            
            buttons.push(`
            <button class="stage-btn ${config.theme}${tbdClass}"
                    data-stage="${stageId}"
                    data-section="${config.section}"
                    data-selector="${config.selector || ''}"
                    style="left: ${config.position.left}; top: ${config.position.top};"
                    ${tbdAttr}>
                <span class="stage-icon">${config.icon}</span>
                <span class="stage-label">${config.label}</span>
                ${tbdBadge}
            </button>
            `);
        }
        
        return buttons.join('\n');
    }

    /**
     * Initialize homepage with sidebar reference
     * @param {ProjectSidebar} sidebar - Sidebar instance for navigation
     */
    static init(sidebar) {
        this.sidebar = sidebar;
        this._loadSavedPositions();
        this._loadSavedColors();
        this._bindStageClicks();
        this._bindDragAndDrop();
        this._bindColorPicker();
        this._createColorPickerElement();
    }

    /**
     * Load saved positions from localStorage
     */
    static _loadSavedPositions() {
        try {
            const saved = localStorage.getItem(this.STORAGE_KEY);
            if (saved) {
                const positions = JSON.parse(saved);
                // Apply saved positions to buttons
                Object.entries(positions).forEach(([stage, pos]) => {
                    const btn = document.querySelector(`[data-stage="${stage}"]`);
                    if (btn) {
                        btn.style.left = pos.left;
                        btn.style.top = pos.top;
                    }
                });
            }
        } catch (e) {
            console.warn('Failed to load saved positions:', e);
        }
    }

    /**
     * Save positions to localStorage
     */
    static _savePositions() {
        try {
            const positions = {};
            const buttons = document.querySelectorAll('.stage-btn');
            buttons.forEach(btn => {
                const stage = btn.dataset.stage;
                positions[stage] = {
                    left: btn.style.left,
                    top: btn.style.top
                };
            });
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(positions));
        } catch (e) {
            console.warn('Failed to save positions:', e);
        }
    }

    /**
     * Reset positions to defaults
     */
    static resetPositions() {
        localStorage.removeItem(this.STORAGE_KEY);
        // Reapply default positions
        Object.entries(this.STAGE_MAPPING).forEach(([stage, config]) => {
            const btn = document.querySelector(`[data-stage="${stage}"]`);
            if (btn) {
                btn.style.left = config.position.left;
                btn.style.top = config.position.top;
            }
        });
    }

    /**
     * Load saved colors from localStorage
     */
    static _loadSavedColors() {
        try {
            const saved = localStorage.getItem(this.COLORS_STORAGE_KEY);
            if (saved) {
                const colors = JSON.parse(saved);
                Object.entries(colors).forEach(([stage, color]) => {
                    const btn = document.querySelector(`[data-stage="${stage}"]`);
                    if (btn) {
                        btn.style.background = color;
                    }
                });
            }
        } catch (e) {
            console.warn('Failed to load saved colors:', e);
        }
    }

    /**
     * Save colors to localStorage
     */
    static _saveColors() {
        try {
            const colors = {};
            const buttons = document.querySelectorAll('.stage-btn');
            buttons.forEach(btn => {
                const stage = btn.dataset.stage;
                if (btn.style.background) {
                    colors[stage] = btn.style.background;
                }
            });
            localStorage.setItem(this.COLORS_STORAGE_KEY, JSON.stringify(colors));
        } catch (e) {
            console.warn('Failed to save colors:', e);
        }
    }

    /**
     * Reset colors to defaults
     */
    static resetColors() {
        localStorage.removeItem(this.COLORS_STORAGE_KEY);
        // Remove inline background styles to use CSS defaults
        const buttons = document.querySelectorAll('.stage-btn');
        buttons.forEach(btn => {
            btn.style.background = '';
        });
    }

    /**
     * Create color picker element
     */
    static _createColorPickerElement() {
        // Remove existing picker if any
        const existing = document.getElementById('homepage-color-picker');
        if (existing) existing.remove();

        const picker = document.createElement('div');
        picker.id = 'homepage-color-picker';
        picker.className = 'homepage-color-picker';
        picker.innerHTML = `
            <div class="color-picker-header">
                <span class="color-picker-title">Pick Color</span>
                <button class="color-picker-close">&times;</button>
            </div>
            <div class="color-picker-row">
                <input type="color" class="color-picker-input" value="#6935c0">
                <button class="color-picker-eyedropper" title="Pick color from screen">💧</button>
            </div>
            <div class="color-picker-presets">
                <button class="color-preset" data-color="rgb(105, 53, 192)" style="background: rgb(105, 53, 192)"></button>
                <button class="color-preset" data-color="rgb(45, 158, 235)" style="background: rgb(45, 158, 235)"></button>
                <button class="color-preset" data-color="rgb(108, 42, 193)" style="background: rgb(108, 42, 193)"></button>
                <button class="color-preset" data-color="rgb(67, 161, 231)" style="background: rgb(67, 161, 231)"></button>
                <button class="color-preset" data-color="rgb(79, 100, 210)" style="background: rgb(79, 100, 210)"></button>
                <button class="color-preset" data-color="rgb(142, 45, 198)" style="background: rgb(142, 45, 198)"></button>
                <button class="color-preset" data-color="rgb(105, 71, 221)" style="background: rgb(105, 71, 221)"></button>
                <button class="color-preset" data-color="rgb(76, 68, 200)" style="background: rgb(76, 68, 200)"></button>
            </div>
            <div class="color-picker-actions">
                <button class="color-picker-reset">Reset</button>
                <button class="color-picker-apply">Apply</button>
            </div>
        `;
        document.body.appendChild(picker);

        // Bind picker events
        picker.querySelector('.color-picker-close').addEventListener('click', () => this._hideColorPicker());
        picker.querySelector('.color-picker-apply').addEventListener('click', () => this._applyColor());
        picker.querySelector('.color-picker-reset').addEventListener('click', () => this._resetButtonColor());
        picker.querySelector('.color-picker-input').addEventListener('input', (e) => this._previewColor(e.target.value));
        picker.querySelector('.color-picker-eyedropper').addEventListener('click', () => this._openEyeDropper());
        
        picker.querySelectorAll('.color-preset').forEach(preset => {
            preset.addEventListener('click', () => {
                const color = preset.dataset.color;
                picker.querySelector('.color-picker-input').value = this._rgbToHex(color);
                this._previewColor(color);
            });
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (this.activeColorPicker && !picker.contains(e.target) && !e.target.closest('.stage-btn')) {
                this._hideColorPicker();
            }
        });
    }

    /**
     * Bind color picker to buttons (right-click)
     */
    static _bindColorPicker() {
        const buttons = document.querySelectorAll('.stage-btn');
        buttons.forEach(btn => {
            btn.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this._showColorPicker(btn, e);
            });
        });
    }

    /**
     * Show color picker near button
     */
    static _showColorPicker(btn, event) {
        const picker = document.getElementById('homepage-color-picker');
        if (!picker) return;

        this.activeColorPicker = btn;
        
        // Get current color
        const currentColor = btn.style.background || getComputedStyle(btn).background;
        const colorInput = picker.querySelector('.color-picker-input');
        colorInput.value = this._rgbToHex(currentColor);

        // Position picker near click
        picker.style.left = `${event.clientX}px`;
        picker.style.top = `${event.clientY}px`;
        picker.classList.add('visible');
    }

    /**
     * Hide color picker
     */
    static _hideColorPicker() {
        const picker = document.getElementById('homepage-color-picker');
        if (picker) {
            picker.classList.remove('visible');
        }
        this.activeColorPicker = null;
    }

    /**
     * Preview color on button
     */
    static _previewColor(color) {
        if (this.activeColorPicker) {
            this.activeColorPicker.style.background = color;
        }
    }

    /**
      * Apply color and save
     */
    static _applyColor() {
        this._saveColors();
        this._hideColorPicker();
    }

    /**
     * Reset single button color
     */
    static _resetButtonColor() {
        if (this.activeColorPicker) {
            this.activeColorPicker.style.background = '';
            this._saveColors();
            this._hideColorPicker();
        }
    }

    /**
     * Open EyeDropper to pick color from screen
     */
    static async _openEyeDropper() {
        // Check if EyeDropper API is supported
        if (!window.EyeDropper) {
            alert('EyeDropper is not supported in this browser. Please use Chrome 95+.');
            return;
        }

        try {
            const eyeDropper = new EyeDropper();
            const result = await eyeDropper.open();
            const color = result.sRGBHex;
            
            // Update color picker input and preview
            const picker = document.getElementById('homepage-color-picker');
            if (picker) {
                picker.querySelector('.color-picker-input').value = color;
            }
            this._previewColor(color);
        } catch (e) {
            // User cancelled or error
            console.log('EyeDropper cancelled or error:', e);
        }
    }

    /**
     * Convert RGB to Hex
     */
    static _rgbToHex(rgb) {
        if (!rgb || rgb.startsWith('#')) return rgb || '#6935c0';
        
        const match = rgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
        if (match) {
            const r = parseInt(match[1]).toString(16).padStart(2, '0');
            const g = parseInt(match[2]).toString(16).padStart(2, '0');
            const b = parseInt(match[3]).toString(16).padStart(2, '0');
            return `#${r}${g}${b}`;
        }
        return '#6935c0';
    }

    /**
     * Bind drag and drop handlers to stage buttons
     */
    static _bindDragAndDrop() {
        const container = document.querySelector('.infinity-loop');
        if (!container) return;

        const buttons = document.querySelectorAll('.stage-btn');
        
        buttons.forEach(btn => {
            // Mouse events
            btn.addEventListener('mousedown', (e) => this._startDrag(e, btn, container));
            
            // Touch events for mobile
            btn.addEventListener('touchstart', (e) => this._startDrag(e, btn, container), { passive: false });
        });

        // Global mouse/touch move and up handlers
        document.addEventListener('mousemove', (e) => this._onDrag(e, container));
        document.addEventListener('mouseup', () => this._endDrag());
        document.addEventListener('touchmove', (e) => this._onDrag(e, container), { passive: false });
        document.addEventListener('touchend', () => this._endDrag());
    }

    /**
     * Start dragging a button
     */
    static _startDrag(e, btn, container) {
        // Prevent default to avoid text selection
        e.preventDefault();
        
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        
        const rect = btn.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        
        this.dragState = {
            btn: btn,
            container: container,
            containerRect: containerRect,
            offsetX: clientX - rect.left - rect.width / 2,
            offsetY: clientY - rect.top - rect.height / 2,
            startX: clientX,
            startY: clientY,
            isDragging: false
        };
        
        btn.classList.add('dragging');
    }

    /**
     * Handle drag movement
     */
    static _onDrag(e, container) {
        if (!this.dragState) return;
        
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        
        // Check if we've moved enough to consider it a drag (5px threshold)
        const dx = Math.abs(clientX - this.dragState.startX);
        const dy = Math.abs(clientY - this.dragState.startY);
        
        if (!this.dragState.isDragging && (dx > 5 || dy > 5)) {
            this.dragState.isDragging = true;
        }
        
        if (!this.dragState.isDragging) return;
        
        e.preventDefault();
        
        const containerRect = this.dragState.containerRect;
        const btn = this.dragState.btn;
        
        // Calculate position relative to container
        const x = clientX - containerRect.left;
        const y = clientY - containerRect.top;
        
        // Convert to percentage
        const leftPercent = (x / containerRect.width) * 100;
        const topPercent = (y / containerRect.height) * 100;
        
        // Clamp within bounds (0-100%)
        const clampedLeft = Math.max(0, Math.min(100, leftPercent));
        const clampedTop = Math.max(0, Math.min(100, topPercent));
        
        btn.style.left = `${clampedLeft}%`;
        btn.style.top = `${clampedTop}%`;
    }

    /**
     * End dragging
     */
    static _endDrag() {
        if (!this.dragState) return;
        
        const btn = this.dragState.btn;
        const wasDragging = this.dragState.isDragging;
        
        btn.classList.remove('dragging');
        
        // Save positions if we actually dragged
        if (wasDragging) {
            this._savePositions();
        }
        
        this.dragState = null;
    }

    /**
     * Bind click handlers to stage buttons
     */
    static _bindStageClicks() {
        const buttons = document.querySelectorAll('.stage-btn');
        
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Don't navigate if we just finished dragging
                if (this.dragState?.isDragging) return;
                
                const stage = e.currentTarget.dataset.stage;
                this.navigateToStage(stage);
            });
        });
    }

    /**
     * Navigate to a stage's corresponding sidebar item
     * @param {string} stage - Stage name (e.g., 'ideation')
     */
    static navigateToStage(stage) {
        const config = this.STAGE_MAPPING[stage];
        
        if (!config) {
            console.warn(`Unknown stage: ${stage}`);
            return;
        }
        
        // Handle TBD stages
        if (config.status === 'tbd') {
            this._showTooltip(stage, 'Coming Soon');
            return;
        }
        
        // Navigate to sidebar item
        if (config.selector && this.sidebar) {
            // Expand the section first
            this._expandSection(config.section);
            
            // Then highlight and scroll to item
            this._highlightItem(config.selector);
        }
    }

    /**
     * Expand a sidebar section
     * @param {string} sectionId - Section ID to expand
     */
    static _expandSection(sectionId) {
        // Main app uses data-section-id, workplace uses data-section
        const sectionHeader = document.querySelector(`[data-section-id="${sectionId}"] .nav-section-header`) ||
                              document.querySelector(`[data-section="${sectionId}"] .section-header`);
        if (sectionHeader) {
            const section = sectionHeader.closest('.nav-section, .sidebar-section');
            // Check if section is collapsed (submenu hidden)
            const submenu = section?.querySelector('.sidebar-submenu');
            if (submenu && submenu.style.display === 'none') {
                sectionHeader.click();
            }
        }
        
        // Also try using sidebar API if available
        if (this.sidebar && typeof this.sidebar.expandSection === 'function') {
            this.sidebar.expandSection(sectionId);
        }
    }

    /**
     * Highlight a sidebar item
     * @param {string} selector - CSS selector for target item
     */
    static _highlightItem(selector) {
        // Try multiple selector patterns
        let item = document.querySelector(selector);
        
        // If not found, try finding by text content in sidebar
        if (!item && selector.includes('ideas')) {
            item = document.querySelector('[data-section-id="workplace"] .nav-section-header');
        } else if (!item && selector.includes('requirements')) {
            item = document.querySelector('[data-section-id="project"] .nav-section-header');
        } else if (!item && selector.includes('planning')) {
            item = document.querySelector('[data-section-id="management"] .nav-section-header');
        }
        
        if (!item) {
            console.warn(`Sidebar item not found: ${selector}`);
            return;
        }
        
        // Remove any existing highlights
        document.querySelectorAll('.homepage-highlight').forEach(el => {
            el.classList.remove('homepage-highlight');
        });
        
        // Add highlight class
        item.classList.add('homepage-highlight');
        
        // Scroll into view
        item.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Remove highlight after delay (3 seconds)
        setTimeout(() => {
            item.classList.remove('homepage-highlight');
        }, 3000);
    }

    /**
     * Show tooltip near a stage button
     * @param {string} stage - Stage name
     * @param {string} message - Tooltip message
     */
    static _showTooltip(stage, message) {
        const tooltip = document.getElementById('homepage-tooltip');
        const button = document.querySelector(`[data-stage="${stage}"]`);
        
        if (!tooltip || !button) return;
        
        // Set message
        tooltip.querySelector('.tooltip-text').textContent = message;
        
        // Position near button
        const rect = button.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.bottom + 8}px`;
        tooltip.style.display = 'block';
        
        // Clear existing timeout
        if (this.tooltipTimeout) {
            clearTimeout(this.tooltipTimeout);
        }
        
        // Hide after 2 seconds
        this.tooltipTimeout = setTimeout(() => {
            this._hideTooltip();
        }, 2000);
    }

    /**
     * Hide tooltip
     */
    static _hideTooltip() {
        const tooltip = document.getElementById('homepage-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    }
}

// Export for use in workplace.js
if (typeof window !== 'undefined') {
    window.HomepageInfinity = HomepageInfinity;
}
