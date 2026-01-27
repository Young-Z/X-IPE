/**
 * Project Switcher
 * FEATURE-006 v2.0: Multi-Project Folder Support
 * 
 * Loads project folders from API and handles switching between projects.
 * When a project is switched, it refreshes the sidebar.
 */
class ProjectSwitcher {
    constructor(selectId, onSwitch) {
        this.select = document.getElementById(selectId);
        this.onSwitch = onSwitch;
        this.projects = [];
        this.activeProjectId = null;
        
        this.bindEvents();
        this.load();
    }
    
    bindEvents() {
        this.select.addEventListener('change', (e) => this.handleSwitch(e));
    }
    
    async load() {
        try {
            const response = await fetch('/api/projects');
            const data = await response.json();
            
            this.projects = data.projects;
            this.activeProjectId = data.active_project_id;
            this.render();
        } catch (error) {
            console.error('Failed to load projects:', error);
            this.select.innerHTML = '<option value="">Failed to load</option>';
        }
    }
    
    render() {
        if (this.projects.length === 0) {
            this.select.innerHTML = '<option value="">No projects</option>';
            return;
        }
        
        this.select.innerHTML = this.projects.map(project => {
            const isActive = project.id === this.activeProjectId;
            return `<option value="${project.id}" ${isActive ? 'selected' : ''}>
                ${isActive ? '✓ ' : ''}${this.escapeHtml(project.name)}
            </option>`;
        }).join('');
    }
    
    async handleSwitch(e) {
        const projectId = parseInt(e.target.value);
        if (!projectId || projectId === this.activeProjectId) return;
        
        try {
            const response = await fetch('/api/projects/switch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_id: projectId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.activeProjectId = data.active_project_id;
                this.render();
                
                // Show toast
                this.showToast(`Switched to ${data.project.name}`);
                
                // Callback to refresh sidebar
                if (this.onSwitch) {
                    this.onSwitch(data.project);
                }
            } else {
                console.error('Switch failed:', data.error);
                this.showToast('Failed to switch project', 'danger');
            }
        } catch (error) {
            console.error('Switch error:', error);
            this.showToast('Network error', 'danger');
        }
    }
    
    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = type === 'success' ? 'refresh-toast' : 'refresh-toast bg-danger';
        toast.innerHTML = `<i class="bi bi-folder-check"></i> ${this.escapeHtml(message)}`;
        container.appendChild(toast);
        
        setTimeout(() => toast.remove(), 2500);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
