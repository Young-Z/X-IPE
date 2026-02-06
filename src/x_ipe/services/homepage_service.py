"""
Homepage Service
FEATURE-026: Homepage Infinity Loop

Provides stage mapping configuration and template generation
for the interactive homepage infinity loop visualization.
"""
from x_ipe.services.tracing_service import x_ipe_tracing


class HomepageService:
    """Service for homepage infinity loop functionality"""
    
    # Stage-to-sidebar mapping configuration
    STAGE_MAPPING = {
        'ideation': {
            'icon': '💡',
            'label': 'IDEATION',
            'theme': 'control',
            'status': 'ready',
            'section': 'workplace',
            'selector': '[data-path="x-ipe-docs/ideas"]',
            'position': {'left': '4.5%', 'top': '60%'}
        },
        'requirement': {
            'icon': '📋',
            'label': 'REQUIREMENT',
            'theme': 'control',
            'status': 'ready',
            'section': 'project',
            'selector': '[data-path="x-ipe-docs/requirements"]',
            'position': {'left': '12%', 'top': '12%'}
        },
        'implementation': {
            'icon': '⚙️',
            'label': 'IMPLEMENT',
            'theme': 'control',
            'status': 'ready',
            'section': 'project',
            'selector': '[data-path="x-ipe-docs/requirements"]',
            'position': {'left': '30%', 'top': '73%'}
        },
        'deployment': {
            'icon': '🚀',
            'label': 'DEPLOY',
            'theme': 'control',
            'status': 'tbd',
            'section': 'management',
            'selector': None,
            'position': {'left': '56%', 'top': '19%'}
        },
        'validation': {
            'icon': '✅',
            'label': 'VALIDATION',
            'theme': 'transparency',
            'status': 'ready',
            'section': 'quality',
            'selector': '[data-section="quality-report"]',
            'position': {'left': '80%', 'top': '13%'}
        },
        'monitoring': {
            'icon': '📊',
            'label': 'MONITORING',
            'theme': 'transparency',
            'status': 'ready',
            'section': 'quality',
            'selector': '[data-section="behavior-tracing"]',
            'position': {'left': '85%', 'top': '65%'}
        },
        'feedback': {
            'icon': '💬',
            'label': 'FEEDBACK',
            'theme': 'transparency',
            'status': 'ready',
            'section': 'feedback',
            'selector': '[data-section="uiux-feedback"]',
            'position': {'left': '58%', 'top': '70%'}
        },
        'planning': {
            'icon': '📅',
            'label': 'PLANNING',
            'theme': 'transparency',
            'status': 'ready',
            'section': 'management',
            'selector': '[data-path="x-ipe-docs/planning"]',
            'position': {'left': '38%', 'top': '25%'}
        }
    }
    
    @x_ipe_tracing(level="INFO")
    def get_stage_mapping(self) -> dict:
        """
        Get the stage-to-sidebar mapping configuration.
        
        Returns:
            dict: Stage mapping with icons, labels, themes, selectors, and positions
        """
        return self.STAGE_MAPPING.copy()
    
    @x_ipe_tracing(level="INFO")
    def get_template(self) -> str:
        """
        Generate HTML template for homepage infinity loop.
        
        Returns:
            str: HTML template string
        """
        stage_buttons = self._render_stage_buttons()
        
        return f'''
<div class="homepage-infinity-container">
    <header class="homepage-header">
        <h1>X-IPE</h1>
        <p>AI-Powered Development Lifecycle</p>
    </header>
    
    <div class="infinity-loop-container">
        <div class="infinity-loop">
            <img src="/api/file/content?path=x-ipe-docs%2Fideas%2FTBC008.%20Feature-Homepage%2FControl%26Transparency.png&raw=true" 
                 alt="Development Lifecycle" 
                 class="infinity-bg"
                 onerror="this.style.display='none'">
            
            {stage_buttons}
            
            <span class="loop-label control">CONTROL</span>
            <span class="loop-label transparency">TRANSPARENCY</span>
        </div>
    </div>
    
    <footer class="homepage-legend">
        <span>Control (What we decide)</span>
        <span>Transparency (What we see)</span>
    </footer>
</div>
'''
    
    def _render_stage_buttons(self) -> str:
        """Render HTML for all stage buttons"""
        buttons = []
        for stage_id, config in self.STAGE_MAPPING.items():
            tbd_class = ' tbd' if config['status'] == 'tbd' else ''
            tbd_attr = ' data-tbd="true"' if config['status'] == 'tbd' else ''
            tbd_badge = '<span class="tbd-badge">TBD</span>' if config['status'] == 'tbd' else ''
            
            button = f'''
            <button class="stage-btn {config['theme']}{tbd_class}"
                    data-stage="{stage_id}"
                    data-section="{config['section']}"
                    data-selector="{config['selector'] or ''}"
                    style="left: {config['position']['left']}; top: {config['position']['top']};"
                    {tbd_attr}>
                <span class="stage-icon">{config['icon']}</span>
                <span class="stage-label">{config['label']}</span>
                {tbd_badge}
            </button>
'''
            buttons.append(button)
        
        return '\n'.join(buttons)
