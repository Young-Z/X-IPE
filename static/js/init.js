/**
 * Application Bootstrap
 * 
 * Initializes all components when DOM is ready.
 * Individual feature classes are loaded from separate files.
 * 
 * Load order:
 * 1. core/content-renderer.js - ContentRenderer
 * 2. features/content-editor.js - ContentEditor  
 * 3. features/live-refresh.js - ContentRefreshManager, PlanningFilePoller
 * 4. features/project-switcher.js - ProjectSwitcher
 * 5. features/sidebar.js - ProjectSidebar
 * 6. features/workplace.js - WorkplaceManager
 * 7. init.js - This file (initialization)
 */

// Global references for cross-component communication
window.contentRenderer = null;
window.contentEditor = null;
window.refreshManager = null;
window.projectSidebar = null;
window.workplaceManager = null;
window.projectSwitcher = null;
window.planningPoller = null;
window.terminalManager = null;
window.terminalPanel = null;

/**
 * Initialize all application components
 */
function initializeApp() {
    // Core content renderer
    window.contentRenderer = new ContentRenderer('content-body');
    
    // Content editor with reference to renderer
    window.contentEditor = new ContentEditor({
        containerId: 'content-body',
        contentRenderer: window.contentRenderer
    });
    
    // Auto-refresh manager
    window.refreshManager = new ContentRefreshManager({
        contentRenderer: window.contentRenderer
    });
    
    // Planning file poller for task-board.md etc.
    window.planningPoller = new PlanningFilePoller({
        pollInterval: 5000
    });
    
    // Workplace manager for idea management
    window.workplaceManager = new WorkplaceManager();
    
    // Project sidebar navigation
    window.projectSidebar = new ProjectSidebar('sidebar-content');
    window.projectSidebar.load();
    
    // Project switcher with callback to refresh sidebar
    window.projectSwitcher = new ProjectSwitcher('project-select', (project) => {
        window.projectSidebar.load();
        window.contentRenderer.container.innerHTML = `
            <div class="content-placeholder">
                <i class="bi bi-folder-check"></i>
                <h5>Switched to ${window.projectSwitcher.escapeHtml(project.name)}</h5>
                <p class="text-muted">Select a file from the sidebar to view</p>
            </div>
        `;
    });
    
    // Setup Create Idea button
    const createIdeaBtn = document.getElementById('btn-create-idea');
    if (createIdeaBtn) {
        createIdeaBtn.addEventListener('click', () => {
            if (window.workplaceManager) {
                window.workplaceManager.showUploadView();
            }
        });
    }
    
    // Initialize terminal panel (FEATURE-005)
    if (typeof TerminalManager !== 'undefined') {
        window.terminalManager = new TerminalManager('terminal-panes');
        window.terminalManager.initialize();
        window.terminalPanel = new TerminalPanel(window.terminalManager);
    }
    
    // Initialize skills modal handler
    initSkillsModal();
    
    console.log('[App] Initialized successfully');
}

/**
 * Initialize skills modal functionality
 */
function initSkillsModal() {
    const skillsBtn = document.getElementById('skills-btn');
    const skillsModalEl = document.getElementById('skills-modal');
    const skillsModalBody = document.getElementById('skills-modal-body');
    
    if (!skillsBtn || !skillsModalEl || !skillsModalBody) return;
    
    const skillsModal = new bootstrap.Modal(skillsModalEl);
    
    skillsBtn.addEventListener('click', async () => {
        // Show loading state
        skillsModalBody.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        skillsModal.show();
        
        try {
            const response = await fetch('/api/skills');
            const data = await response.json();
            
            if (data.success && data.skills.length > 0) {
                skillsModalBody.innerHTML = `
                    <div class="list-group list-group-flush">
                        ${data.skills.map(skill => `
                            <div class="list-group-item">
                                <div class="d-flex w-100 justify-content-between align-items-start">
                                    <div>
                                        <h6 class="mb-1 fw-semibold">
                                            <i class="bi bi-lightning-charge text-warning me-1"></i>
                                            ${escapeHtml(skill.name)}
                                        </h6>
                                        <p class="mb-0 text-muted small">${escapeHtml(skill.description || 'No description available')}</p>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else if (data.success && data.skills.length === 0) {
                skillsModalBody.innerHTML = `
                    <div class="text-center py-4 text-muted">
                        <i class="bi bi-inbox fs-1"></i>
                        <p class="mt-2">No skills found</p>
                    </div>
                `;
            } else {
                skillsModalBody.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        ${escapeHtml(data.error || 'Failed to load skills')}
                    </div>
                `;
            }
        } catch (error) {
            skillsModalBody.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Error loading skills: ${escapeHtml(error.message)}
                </div>
            `;
        }
    });
}

/**
 * HTML escape utility
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApp);
