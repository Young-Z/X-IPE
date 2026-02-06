/**
 * Homepage Infinity Loop - FEATURE-026
 * 
 * Interactive visualization of the X-IPE development lifecycle.
 * Displays 8 stages on an infinity loop (∞) with clickable navigation.
 */

class HomepageInfinity {
    static sidebar = null;
    static tooltipTimeout = null;
    
    static STAGE_MAPPING = {
        ideation: {
            icon: '📋',
            label: 'REQUIREMENT',
            theme: 'control',
            status: 'ready',
            section: 'requirements',
            selector: '[data-section-id="requirements"]',
            position: { left: '7.33%', top: '68.37%' }
        },
        requirement: {
            icon: '💡',
            label: 'IDEATION',
            theme: 'control',
            status: 'ready',
            section: 'ideation',
            selector: '[data-section-id="ideation"]',
            position: { left: '15%', top: '17.6%' }
        },
        implementation: {
            icon: '⚙️',
            label: 'IMPLEMENT',
            theme: 'control',
            status: 'ready',
            section: 'code',
            selector: '[data-section-id="code"]',
            position: { left: '34.44%', top: '82%' }
        },
        deployment: {
            icon: '🚀',
            label: 'DEPLOY',
            theme: 'control',
            status: 'tbd',
            section: 'management',
            selector: null,
            position: { left: '60.33%', top: '26.69%' }
        },
        validation: {
            icon: '✅',
            label: 'VALIDATION',
            theme: 'transparency',
            status: 'ready',
            section: 'quality-evaluation',
            selector: '[data-section-id="quality-evaluation"]',
            position: { left: '87.11%', top: '19.78%' }
        },
        monitoring: {
            icon: '📊',
            label: 'MONITORING',
            theme: 'transparency',
            status: 'ready',
            section: 'tracing',
            selector: '[data-section-id="tracing"]',
            position: { left: '90.67%', top: '73.9%' }
        },
        feedback: {
            icon: '💬',
            label: 'FEEDBACK',
            theme: 'transparency',
            status: 'ready',
            section: 'uiux-feedbacks',
            selector: '[data-section-id="uiux-feedbacks"]',
            position: { left: '63.33%', top: '79.04%' }
        },
        planning: {
            icon: '📅',
            label: 'PLANNING',
            theme: 'transparency',
            status: 'ready',
            section: 'planning',
            selector: '[data-section-id="planning"]',
            position: { left: '41.56%', top: '30.25%' }
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
        <p>An AI native integrated project environment for end to end business value delivery</p>
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
        <span class="legend-transparency">● Transparency (What We See)</span>
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
        this._bindStageClicks();
    }

    /**
     * Bind click handlers to stage buttons
     */
    static _bindStageClicks() {
        const buttons = document.querySelectorAll('.stage-btn');
        
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
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
