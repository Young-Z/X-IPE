/**
 * Architecture DSL Canvas Renderer (Module View - Corporate Style)
 * 
 * Renders parsed Architecture DSL AST to HTML Canvas.
 * Implements the corporate style with:
 * - White layer backgrounds with colored borders
 * - Dark dashed borders for modules
 * - Pill-shaped component badges
 * - Side labels for layers
 * - Auto-detection of layer colors based on name
 * 
 * References:
 * - .github/skills/tool-draw-layered-architecture/SKILL.md
 * - .github/skills/tool-draw-layered-architecture/references/dsl-to-css.md
 * - .github/skills/tool-draw-layered-architecture/references/grid-system.md
 * 
 * @module architecture-dsl/renderer
 */

export class ArchitectureCanvasRenderer {
    constructor(options = {}) {
        // Layout constants (matching CSS template values)
        this.PADDING = options.padding || 32;
        this.LAYER_GAP = options.layerGap || 16;
        this.MODULE_GAP = options.moduleGap || 14;
        this.COMPONENT_GAP = options.componentGap || 10;
        this.BORDER_RADIUS = options.borderRadius || 8;
        this.COMPONENT_RADIUS = options.componentRadius || 18;
        this.LAYER_LABEL_WIDTH = options.layerLabelWidth || 36;
        this.LAYER_PADDING = options.layerPadding || 20;
        this.MODULE_PADDING = options.modulePadding || 14;
        
        // Component sizing
        this.COMPONENT_MIN_HEIGHT = 36;
        this.COMPONENT_PADDING_H = 16;
        this.COMPONENT_PADDING_V = 8;
        
        // Layer color auto-detection patterns (from dsl-to-css.md)
        this.LAYER_COLOR_PATTERNS = [
            { patterns: ['presentation', 'ui', 'frontend', 'view'], bg: '#fce7f3', border: '#ec4899' },
            { patterns: ['service', 'api', 'gateway'], bg: '#fef3c7', border: '#f97316' },
            { patterns: ['business', 'domain', 'logic', 'core'], bg: '#dbeafe', border: '#3b82f6' },
            { patterns: ['data', 'persistence', 'storage', 'db'], bg: '#dcfce7', border: '#22c55e' },
            { patterns: ['infrastructure', 'infra', 'platform'], bg: '#f3e8ff', border: '#a855f7' }
        ];
        
        // Colors (Corporate theme)
        this.colors = {
            background: '#f8fafc',
            backgroundGradientEnd: '#f1f5f9',
            layerBg: '#ffffff',
            layerBgHighlight: '#eff6ff',
            layerBorder: '#374151',
            moduleBorder: '#d1d5db',
            badgeBg: '#1f2937',
            badgeText: '#ffffff',
            labelBg: '#1f2937',
            labelText: '#ffffff',
            titleText: '#374151',
            moduleTitle: '#374151',
            // Hover/accent colors
            accentBlue: '#3b82f6',
            accentIndigo: '#6366f1',
            ...options.colors
        };
        
        // Fonts
        this.fonts = {
            title: "700 26px 'Inter', sans-serif",
            layerLabel: "600 12px 'Inter', sans-serif",
            moduleTitle: "700 14px 'Inter', sans-serif",
            component: "500 12px 'Inter', sans-serif",
            iconLabel: "500 11px 'Inter', sans-serif",
            ...options.fonts
        };
        
        // Canvas context
        this.ctx = null;
        this.canvas = null;
        this.scale = options.scale || (window.devicePixelRatio || 1);
    }
    
    /**
     * Auto-detect layer colors based on layer name
     * @private
     */
    _detectLayerColors(layerName) {
        const nameLower = layerName.toLowerCase();
        for (const pattern of this.LAYER_COLOR_PATTERNS) {
            if (pattern.patterns.some(p => nameLower.includes(p))) {
                return { bg: pattern.bg, border: pattern.border };
            }
        }
        // Default colors if no pattern matches
        return { bg: this.colors.layerBg, border: this.colors.layerBorder };
    }

    /**
     * Render AST to canvas
     * @param {Object} ast - Parsed DSL AST
     * @param {HTMLCanvasElement} canvas - Target canvas element
     * @param {Object} options - Render options
     */
    render(ast, canvas, options = {}) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        
        // Store theme for use in layer drawing
        this.currentTheme = ast.theme || 'default';
        
        // Calculate layout
        const layout = this._calculateLayout(ast);
        
        // Set canvas size
        const width = layout.width + this.PADDING * 2;
        const height = layout.height + this.PADDING * 2;
        
        canvas.width = width * this.scale;
        canvas.height = height * this.scale;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        
        this.ctx.scale(this.scale, this.scale);
        
        // Draw background gradient
        const gradient = this.ctx.createLinearGradient(0, 0, width, height);
        gradient.addColorStop(0, '#f8fafc');
        gradient.addColorStop(1, '#f1f5f9');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, width, height);
        
        // Draw title
        let y = this.PADDING;
        if (ast.title) {
            y = this._drawTitle(ast.title, width, y);
        }
        
        // Draw layers
        for (const layerLayout of layout.layers) {
            this._drawLayer(layerLayout, this.PADDING, y);
            y += layerLayout.height + this.LAYER_GAP;
        }
    }

    /**
     * Calculate layout for all elements
     * @private
     */
    _calculateLayout(ast) {
        // Calculate minimum width needed based on modules
        // Each column needs at least 90px for readable component text
        const minColWidth = 90;
        const maxModulesInLayer = Math.max(...ast.layers.map(l => l.modules.length), 1);
        const totalGaps = (maxModulesInLayer - 1) * this.MODULE_GAP;
        const minContentWidth = 12 * minColWidth + totalGaps + this.LAYER_PADDING * 2;
        const maxWidth = Math.max(1280, minContentWidth + this.LAYER_LABEL_WIDTH);
        const contentWidth = maxWidth - this.LAYER_LABEL_WIDTH;
        
        const layers = [];
        let totalHeight = 0;
        
        // Add title height
        if (ast.title) {
            totalHeight += 50; // Title + margin
        }
        
        for (const layer of ast.layers) {
            const layerLayout = this._calculateLayerLayout(layer, contentWidth);
            layers.push(layerLayout);
            totalHeight += layerLayout.height + this.LAYER_GAP;
        }
        
        // Remove last gap
        if (layers.length > 0) {
            totalHeight -= this.LAYER_GAP;
        }
        
        return {
            width: maxWidth,
            height: totalHeight,
            layers
        };
    }

    /**
     * Calculate layout for a single layer
     * Following grid-system.md Rule 2: Layers Occupy Full Width
     * @private
     */
    _calculateLayerLayout(layer, contentWidth) {
        // Calculate available width for modules (inside layer padding)
        const moduleAreaWidth = contentWidth - this.LAYER_PADDING * 2;
        
        // Calculate module layouts using 12-column grid (Rule 3)
        const modules = [];
        let maxModuleHeight = 0;
        
        // Total gap space between modules
        const totalGapSpace = (layer.modules.length - 1) * this.MODULE_GAP;
        // Width per column unit (12-column grid)
        const colUnitWidth = (moduleAreaWidth - totalGapSpace) / 12;
        
        for (const module of layer.modules) {
            // Module width = cols * colUnitWidth + proportional gaps
            const moduleWidth = colUnitWidth * module.cols;
            
            const moduleLayout = this._calculateModuleLayout(module, moduleWidth - this.MODULE_PADDING * 2);
            modules.push({
                ...moduleLayout,
                module,
                width: moduleWidth
            });
            
            maxModuleHeight = Math.max(maxModuleHeight, moduleLayout.height);
        }
        
        // Layer height: padding + module content + padding
        const layerHeight = this.LAYER_PADDING * 2 + maxModuleHeight;
        
        return {
            layer,
            width: contentWidth,
            height: layerHeight,
            modules
        };
    }

    /**
     * Calculate layout for a single module
     * Following grid-system.md Rule 4: Module Internal Grid
     * @private
     */
    _calculateModuleLayout(module, availableWidth) {
        const titleHeight = 24; // Module title height
        const titleGap = 12;    // Gap between title and content
        
        // Module internal grid (Rule 4)
        const gridCols = module.grid.cols;
        const gridRows = module.grid.rows;
        const gap = parseInt(module.gap) || this.COMPONENT_GAP;
        
        // Calculate component cell dimensions
        const totalHGap = (gridCols - 1) * gap;
        const totalVGap = (gridRows - 1) * gap;
        const cellWidth = (availableWidth - totalHGap) / gridCols;
        const cellHeight = this.COMPONENT_MIN_HEIGHT;
        
        // Layout components following grid placement (Rule 5)
        const components = [];
        let col = 0;
        let row = 0;
        
        for (const comp of module.components) {
            // Component spans (default: 1x1)
            const spanCols = comp.cols || 1;
            const spanRows = comp.rows || 1;
            
            // Check if component fits in current row, if not wrap
            if (col + spanCols > gridCols) {
                col = 0;
                row++;
            }
            
            // Calculate component position and size
            const compX = col * (cellWidth + gap);
            const compY = row * (cellHeight + gap);
            const compWidth = cellWidth * spanCols + gap * (spanCols - 1);
            const compHeight = cellHeight * spanRows + gap * (spanRows - 1);
            
            components.push({
                component: comp,
                x: compX,
                y: compY,
                width: compWidth,
                height: compHeight,
                col,
                row,
                spanCols,
                spanRows
            });
            
            // Move to next position
            col += spanCols;
            if (col >= gridCols) {
                col = 0;
                row++;
            }
        }
        
        // Calculate actual rows used
        const actualRows = Math.max(row + (col > 0 ? 1 : 0), Math.ceil(module.components.length / gridCols), 1);
        const contentHeight = actualRows * cellHeight + (actualRows - 1) * gap;
        
        // Total module height
        const totalHeight = titleHeight + titleGap + contentHeight + this.MODULE_PADDING * 2;
        
        return {
            module,
            titleHeight,
            titleGap,
            contentHeight,
            height: totalHeight,
            components,
            gridCols,
            gridRows: actualRows,
            gap,
            cellWidth,
            cellHeight
        };
    }

    /**
     * Draw diagram title
     * @private
     */
    _drawTitle(title, width, y) {
        this.ctx.font = this.fonts.title;
        this.ctx.fillStyle = this.colors.titleText;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'top';
        
        this.ctx.fillText(title, width / 2, y);
        
        return y + 50; // Title height + margin
    }

    /**
     * Draw a layer with side label
     * Following dsl-to-css.md layer mappings
     * @private
     */
    _drawLayer(layerLayout, x, y) {
        const { layer, width, height, modules } = layerLayout;
        
        // Only use auto-detected colors if theme is not default and layer has no explicit colors
        const useAutoColors = this.currentTheme && 
            this.currentTheme !== 'default' && 
            this.currentTheme !== 'theme-default';
        
        let layerBg, borderColor;
        
        if (layer.color) {
            layerBg = layer.color;
        } else if (useAutoColors) {
            layerBg = this._detectLayerColors(layer.name).bg;
        } else {
            layerBg = this.colors.layerBg;
        }
        
        if (layer.borderColor) {
            borderColor = layer.borderColor;
        } else if (useAutoColors) {
            borderColor = this._detectLayerColors(layer.name).border;
        } else {
            borderColor = this.colors.layerBorder;
        }
        
        // Layer content area (right side) with rounded corners
        this._roundRect(
            x + this.LAYER_LABEL_WIDTH, y,
            width, height,
            { tl: 0, tr: this.BORDER_RADIUS, br: this.BORDER_RADIUS, bl: 0 }
        );
        this.ctx.fillStyle = layerBg;
        this.ctx.fill();
        this.ctx.strokeStyle = borderColor;
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // Side label (left side) - dark background
        this._roundRect(
            x, y,
            this.LAYER_LABEL_WIDTH, height,
            { tl: this.BORDER_RADIUS, tr: 0, br: 0, bl: this.BORDER_RADIUS }
        );
        this.ctx.fillStyle = this.colors.labelBg;
        this.ctx.fill();
        
        // Draw label text (rotated 180° for vertical reading)
        this.ctx.save();
        this.ctx.translate(x + this.LAYER_LABEL_WIDTH / 2, y + height / 2);
        this.ctx.rotate(-Math.PI / 2);
        this.ctx.font = this.fonts.layerLabel;
        this.ctx.fillStyle = this.colors.labelText;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(layer.name.toUpperCase(), 0, 0);
        this.ctx.restore();
        
        // Draw modules using 12-column grid layout
        let moduleX = x + this.LAYER_LABEL_WIDTH + this.LAYER_PADDING;
        const moduleY = y + this.LAYER_PADDING;
        const moduleMaxHeight = height - this.LAYER_PADDING * 2;
        
        for (const moduleLayout of modules) {
            this._drawModule(moduleLayout, moduleX, moduleY, moduleMaxHeight);
            moduleX += moduleLayout.width + this.MODULE_GAP;
        }
    }

    /**
     * Draw a module with components
     * Following dsl-to-css.md module mappings
     * @private
     */
    _drawModule(moduleLayout, x, y, maxHeight) {
        const { module, width, components, titleHeight, titleGap, gap } = moduleLayout;
        const height = maxHeight;
        
        // Module background with dashed border (corporate style)
        this.ctx.beginPath();
        this._roundRectPath(x, y, width, height, this.BORDER_RADIUS);
        this.ctx.fillStyle = this.colors.layerBg;
        this.ctx.fill();
        this.ctx.strokeStyle = this.colors.moduleBorder;
        this.ctx.lineWidth = 1.5;
        this.ctx.setLineDash([5, 5]);
        this.ctx.stroke();
        this.ctx.setLineDash([]);
        
        // Module title (left-aligned per corporate style)
        this.ctx.font = this.fonts.moduleTitle;
        this.ctx.fillStyle = this.colors.moduleTitle;
        this.ctx.textAlign = 'left';
        this.ctx.textBaseline = 'top';
        this.ctx.fillText(module.name, x + this.MODULE_PADDING, y + this.MODULE_PADDING);
        
        // Component content area
        const contentX = x + this.MODULE_PADDING;
        const contentY = y + this.MODULE_PADDING + titleHeight + titleGap;
        
        // Draw components with proper alignment
        for (const compLayout of components) {
            this._drawComponent(
                compLayout.component,
                contentX + compLayout.x,
                contentY + compLayout.y,
                compLayout.width,
                compLayout.height
            );
        }
    }

    /**
     * Draw a component (pill badge)
     * Following dsl-to-css.md component mappings and corporate-style.md
     * @private
     */
    _drawComponent(component, x, y, width, height) {
        // Special handling for icon stereotypes (folder, file, db, icon)
        if (component.stereotype && ['icon', 'folder', 'file', 'db'].includes(component.stereotype)) {
            this._drawIconComponent(component, x, y, width, height);
            return;
        }
        
        // Regular pill badge (corporate style)
        const radius = Math.min(height / 2, this.COMPONENT_RADIUS);
        
        // Draw pill shape
        this.ctx.beginPath();
        this.ctx.moveTo(x + radius, y);
        this.ctx.lineTo(x + width - radius, y);
        this.ctx.arc(x + width - radius, y + height / 2, radius, -Math.PI / 2, Math.PI / 2);
        this.ctx.lineTo(x + radius, y + height);
        this.ctx.arc(x + radius, y + height / 2, radius, Math.PI / 2, -Math.PI / 2);
        this.ctx.closePath();
        
        this.ctx.fillStyle = this.colors.badgeBg;
        this.ctx.fill();
        
        // Draw text (centered, with text wrapping if needed)
        this.ctx.font = this.fonts.component;
        this.ctx.fillStyle = this.colors.badgeText;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        // Truncate text if too long
        let text = component.name;
        const maxTextWidth = width - this.COMPONENT_PADDING_H * 2;
        const metrics = this.ctx.measureText(text);
        
        if (metrics.width > maxTextWidth) {
            // Try to fit by truncating
            while (this.ctx.measureText(text + '...').width > maxTextWidth && text.length > 3) {
                text = text.slice(0, -1);
            }
            text = text + '...';
        }
        
        this.ctx.fillText(text, x + width / 2, y + height / 2);
    }

    /**
     * Draw an icon-style component
     * Following corporate-style.md icon component styling
     * @private
     */
    _drawIconComponent(component, x, y, width, height) {
        const iconSize = 28;
        const labelGap = 6;
        
        // Icon mapping (emoji-based for simplicity)
        const icons = {
            folder: '📁',
            file: '📄',
            db: '🗄️',
            database: '🗄️',
            icon: '⚙️',
            chart: '📊',
            cloud: '☁️'
        };
        
        const icon = icons[component.stereotype] || '📦';
        
        // Calculate vertical centering
        const totalContentHeight = iconSize + labelGap + 14; // icon + gap + text
        const startY = y + (height - totalContentHeight) / 2;
        
        // Draw icon (centered)
        this.ctx.font = `${iconSize}px serif`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'top';
        this.ctx.fillText(icon, x + width / 2, startY);
        
        // Draw label (below icon)
        this.ctx.font = this.fonts.iconLabel;
        this.ctx.fillStyle = '#6b7280';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'top';
        
        // Truncate label if needed
        let text = component.name;
        const maxTextWidth = width - 8;
        while (this.ctx.measureText(text).width > maxTextWidth && text.length > 3) {
            text = text.slice(0, -1);
        }
        if (text !== component.name) {
            text = text.slice(0, -2) + '...';
        }
        
        this.ctx.fillText(text, x + width / 2, startY + iconSize + labelGap);
    }

    /**
     * Draw a rounded rectangle path
     * @private
     */
    _roundRectPath(x, y, width, height, radius) {
        this.ctx.moveTo(x + radius, y);
        this.ctx.lineTo(x + width - radius, y);
        this.ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
        this.ctx.lineTo(x + width, y + height - radius);
        this.ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        this.ctx.lineTo(x + radius, y + height);
        this.ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
        this.ctx.lineTo(x, y + radius);
        this.ctx.quadraticCurveTo(x, y, x + radius, y);
        this.ctx.closePath();
    }

    /**
     * Draw a rounded rectangle with custom corner radii
     * @private
     */
    _roundRect(x, y, width, height, radii) {
        const { tl = 0, tr = 0, br = 0, bl = 0 } = radii;
        
        this.ctx.beginPath();
        this.ctx.moveTo(x + tl, y);
        this.ctx.lineTo(x + width - tr, y);
        this.ctx.quadraticCurveTo(x + width, y, x + width, y + tr);
        this.ctx.lineTo(x + width, y + height - br);
        this.ctx.quadraticCurveTo(x + width, y + height, x + width - br, y + height);
        this.ctx.lineTo(x + bl, y + height);
        this.ctx.quadraticCurveTo(x, y + height, x, y + height - bl);
        this.ctx.lineTo(x, y + tl);
        this.ctx.quadraticCurveTo(x, y, x + tl, y);
        this.ctx.closePath();
    }

    /**
     * Export canvas as PNG blob
     * @returns {Promise<Blob>}
     */
    exportPNG() {
        return new Promise((resolve) => {
            this.canvas.toBlob(resolve, 'image/png');
        });
    }

    /**
     * Export canvas as data URL
     * @returns {string}
     */
    exportDataURL() {
        return this.canvas.toDataURL('image/png');
    }
}

export default ArchitectureCanvasRenderer;
