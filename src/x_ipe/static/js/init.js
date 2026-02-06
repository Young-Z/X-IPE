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
window.stageToolboxModal = null; // FEATURE-011

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
    
    // Initialize sidebar resize functionality
    initSidebarResize();
    
    // Setup Create Idea button
    const createIdeaBtn = document.getElementById('btn-create-idea');
    if (createIdeaBtn) {
        createIdeaBtn.addEventListener('click', () => {
            if (window.workplaceManager) {
                window.workplaceManager.showUploadView();
            }
        });
    }
    
    // FEATURE-026: X-IPE Logo click handler - show homepage
    // Support both workplace.html (.top-bar-brand) and index.html (#brand-home-link)
    const logoBrand = document.querySelector('.top-bar-brand') || document.getElementById('brand-home-link');
    if (logoBrand) {
        logoBrand.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent navigation
            
            // Store sidebar reference for homepage navigation
            if (window.workplaceManager) {
                window.workplaceManager.sidebarRef = window.projectSidebar;
            }
            
            // Show homepage in content area
            const contentBody = document.getElementById('content-body');
            if (contentBody && typeof window.HomepageInfinity !== 'undefined') {
                contentBody.innerHTML = window.HomepageInfinity.getTemplate();
                window.HomepageInfinity.init(window.projectSidebar);
                
                // Update breadcrumb
                const breadcrumb = document.getElementById('breadcrumb');
                if (breadcrumb) {
                    breadcrumb.innerHTML = '<li class="breadcrumb-item active">Home</li>';
                }
            } else if (window.workplaceManager) {
                window.workplaceManager.showHomepage();
                
                // Update breadcrumb
                const breadcrumb = document.getElementById('breadcrumb');
                if (breadcrumb) {
                    breadcrumb.innerHTML = '<li class="breadcrumb-item active">Home</li>';
                }
            }
        });
    }
    
    // FEATURE-011: Initialize Stage Toolbox Modal
    if (typeof StageToolboxModal !== 'undefined') {
        window.stageToolboxModal = new StageToolboxModal();
        const toolboxBtn = document.getElementById('btn-stage-toolbox');
        if (toolboxBtn) {
            toolboxBtn.addEventListener('click', () => {
                window.stageToolboxModal.open();
            });
        }
    }
    
    // FEATURE-025-A: Knowledge Base button click handler
    const kbBtn = document.getElementById('btn-knowledge-base');
    if (kbBtn) {
        kbBtn.addEventListener('click', () => {
            console.log('[KB] Knowledge Base button clicked');
            
            // Update breadcrumb
            const breadcrumb = document.getElementById('breadcrumb');
            if (breadcrumb) {
                breadcrumb.innerHTML = '<li class="breadcrumb-item active">Knowledge Base</li>';
            }
            
            // Hide Create Idea button
            const createIdeaBtn = document.getElementById('btn-create-idea');
            if (createIdeaBtn) {
                createIdeaBtn.classList.add('d-none');
            }
            
            // Render Knowledge Base view in content area (two-column layout like Ideation)
            const container = document.getElementById('content-body');
            if (container && window.kbCore) {
                window.kbCore.render(container);
            } else if (container) {
                container.innerHTML = '<div class="p-4 text-muted">Knowledge Base module not loaded</div>';
            }
        });
    }
    
    // Initialize terminal panel (FEATURE-005)
    if (typeof TerminalManager !== 'undefined') {
        window.terminalManager = new TerminalManager('terminal-panes');
        window.terminalManager.initialize();
        window.terminalPanel = new TerminalPanel(window.terminalManager);
    }
    
    // FEATURE-021: Initialize Voice Input Manager
    if (typeof VoiceInputManager !== 'undefined' && window.terminalManager) {
        // Wait for Socket.IO to be ready from terminal manager
        setTimeout(() => {
            const socket = window.terminalManager.socket;
            if (socket) {
                window.voiceInputManager = new VoiceInputManager(socket);
                console.log('[Voice] VoiceInputManager initialized');
            }
        }, 500);
    }
    
    // Initialize skills modal handler
    initSkillsModal();
    
    console.log('[App] Initialized successfully');
}

/**
 * Initialize sidebar resize functionality
 */
function initSidebarResize() {
    const sidebar = document.getElementById('sidebar');
    const resizeHandle = document.getElementById('sidebar-resize-handle');
    
    if (!sidebar || !resizeHandle) return;
    
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;
    
    const minWidth = 200;
    const maxWidth = 500;
    
    resizeHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        startX = e.clientX;
        startWidth = sidebar.offsetWidth;
        resizeHandle.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        
        const delta = e.clientX - startX;
        let newWidth = startWidth + delta;
        
        // Clamp to min/max
        newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
        
        sidebar.style.flex = `0 0 ${newWidth}px`;
        sidebar.style.width = `${newWidth}px`;
    });
    
    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            resizeHandle.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            
            // Save to localStorage for persistence
            localStorage.setItem('sidebar-width', sidebar.offsetWidth);
        }
    });
    
    // Restore saved width
    const savedWidth = localStorage.getItem('sidebar-width');
    if (savedWidth) {
        const width = parseInt(savedWidth, 10);
        if (width >= minWidth && width <= maxWidth) {
            sidebar.style.flex = `0 0 ${width}px`;
            sidebar.style.width = `${width}px`;
        }
    }
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
