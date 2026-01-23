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
    window.projectSidebar = new ProjectSidebar('nav-tree');
    window.projectSidebar.load();
    
    // Project switcher with callback to refresh sidebar
    window.projectSwitcher = new ProjectSwitcher('project-select', (project) => {
        window.projectSidebar.load();
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
    
    console.log('[App] Initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApp);
