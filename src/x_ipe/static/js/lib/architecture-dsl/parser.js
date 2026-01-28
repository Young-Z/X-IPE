/**
 * Architecture DSL Parser (v2 - Grid-Based)
 * 
 * Parses Architecture DSL module-view syntax into an AST.
 * Supports the v2 grid-based layout system with cols/rows/grid properties.
 * 
 * @module architecture-dsl/parser
 */

export class ArchitectureDSLParser {
    constructor() {
        this.errors = [];
        this.warnings = [];
    }

    /**
     * Parse DSL string into AST
     * @param {string} dsl - The DSL source code
     * @returns {Object} AST with document structure
     */
    parse(dsl) {
        this.errors = [];
        this.warnings = [];
        
        const lines = dsl.split('\n');
        const ast = {
            type: 'document',
            viewType: null,
            title: null,
            theme: 'theme-default',
            direction: 'top-to-bottom',
            canvas: null,  // e.g., { width: '1200px', height: '600px' }
            grid: { cols: 12, rows: 6 },
            textAlign: 'left',
            layers: [],
            errors: this.errors,
            warnings: this.warnings
        };

        let currentLayer = null;
        let currentModule = null;
        let lineNum = 0;
        let inMultiLineComment = false;

        for (const rawLine of lines) {
            lineNum++;
            let line = rawLine.trim();

            // Handle multi-line comments
            if (inMultiLineComment) {
                if (line.includes("'/")) {
                    inMultiLineComment = false;
                }
                continue;
            }
            if (line.startsWith("/'")) {
                inMultiLineComment = true;
                continue;
            }

            // Skip single-line comments and empty lines
            if (line.startsWith("'") || line === '') continue;

            // Remove inline comments
            const commentIdx = line.indexOf("'");
            if (commentIdx > 0) {
                line = line.substring(0, commentIdx).trim();
            }

            // Parse header
            if (line.startsWith('@startuml')) {
                const match = line.match(/@startuml\s+(module-view|landscape-view)/);
                if (match) {
                    ast.viewType = match[1];
                } else {
                    this.errors.push({ line: lineNum, message: 'Invalid @startuml header. Use @startuml module-view or @startuml landscape-view' });
                }
                continue;
            }

            if (line === '@enduml') continue;

            // Parse title
            if (line.startsWith('title ')) {
                const match = line.match(/title\s+"([^"]+)"/);
                if (match) ast.title = match[1];
                continue;
            }

            // Parse theme
            if (line.startsWith('theme ')) {
                const match = line.match(/theme\s+"([^"]+)"/);
                if (match) ast.theme = match[1];
                continue;
            }

            // Parse direction
            if (line.startsWith('direction ')) {
                const match = line.match(/direction\s+(top-to-bottom|left-to-right)/);
                if (match) ast.direction = match[1];
                continue;
            }

            // Parse canvas (explicit size: canvas 1200px, 600px or canvas 1200px 600px)
            if (line.startsWith('canvas ')) {
                const match = line.match(/canvas\s+(\d+(?:px|%)?)\s*[,\s]\s*(\d+(?:px|%)?)/);
                if (match) {
                    // Add 'px' unit if not specified
                    const width = match[1].match(/\d+$/) ? match[1] + 'px' : match[1];
                    const height = match[2].match(/\d+$/) ? match[2] + 'px' : match[2];
                    ast.canvas = { width, height };
                }
                continue;
            }

            // Parse document grid
            if (line.startsWith('grid ') && !currentModule) {
                const match = line.match(/grid\s+(\d+)\s*x\s*(\d+)/);
                if (match) {
                    ast.grid = { cols: parseInt(match[1]), rows: parseInt(match[2]) };
                }
                continue;
            }

            // Parse text-align at document level
            if (line.startsWith('text-align ') && !currentLayer && !currentModule) {
                const match = line.match(/text-align\s+(left|center|right)/);
                if (match) ast.textAlign = match[1];
                continue;
            }

            // Parse layer
            if (line.startsWith('layer ')) {
                const match = line.match(/layer\s+"([^"]+)"(?:\s+as\s+(\w+))?\s*\{?/);
                if (match) {
                    currentLayer = {
                        type: 'layer',
                        name: match[1],
                        alias: match[2] || null,
                        rows: 1,
                        color: null,
                        borderColor: null,
                        textAlign: ast.textAlign,
                        modules: []
                    };
                    ast.layers.push(currentLayer);
                }
                continue;
            }

            // Inside layer
            if (currentLayer && !currentModule) {
                // Parse rows
                if (line.startsWith('rows ')) {
                    const match = line.match(/rows\s+(\d+)/);
                    if (match) currentLayer.rows = parseInt(match[1]);
                    continue;
                }

                // Parse color
                if (line.startsWith('color ')) {
                    const match = line.match(/color\s+"([^"]+)"/);
                    if (match) currentLayer.color = match[1];
                    continue;
                }

                // Parse border-color
                if (line.startsWith('border-color ')) {
                    const match = line.match(/border-color\s+"([^"]+)"/);
                    if (match) currentLayer.borderColor = match[1];
                    continue;
                }

                // Parse text-align
                if (line.startsWith('text-align ')) {
                    const match = line.match(/text-align\s+(left|center|right)/);
                    if (match) currentLayer.textAlign = match[1];
                    continue;
                }

                // Parse module start
                if (line.startsWith('module ')) {
                    const match = line.match(/module\s+"([^"]+)"(?:\s+as\s+(\w+))?\s*\{?/);
                    if (match) {
                        currentModule = {
                            type: 'module',
                            name: match[1],
                            alias: match[2] || null,
                            cols: 12,
                            rows: 1,
                            grid: { cols: 1, rows: 1 },
                            align: { h: 'center', v: 'center' },
                            gap: '8px',
                            color: null,
                            textAlign: currentLayer.textAlign,
                            components: []
                        };
                        currentLayer.modules.push(currentModule);
                    }
                    continue;
                }

                // Close layer
                if (line === '}') {
                    currentLayer = null;
                    continue;
                }
            }

            // Inside module
            if (currentModule) {
                // Parse cols
                if (line.startsWith('cols ')) {
                    const match = line.match(/cols\s+(\d+)/);
                    if (match) currentModule.cols = parseInt(match[1]);
                    continue;
                }

                // Parse rows
                if (line.startsWith('rows ') && !line.includes(',')) {
                    const match = line.match(/rows\s+(\d+)/);
                    if (match) currentModule.rows = parseInt(match[1]);
                    continue;
                }

                // Parse grid
                if (line.startsWith('grid ')) {
                    const match = line.match(/grid\s+(\d+)\s*x\s*(\d+)/);
                    if (match) {
                        currentModule.grid = { cols: parseInt(match[1]), rows: parseInt(match[2]) };
                    }
                    continue;
                }

                // Parse align
                if (line.startsWith('align ')) {
                    const match = line.match(/align\s+(left|center|right)\s+(top|center|bottom)/);
                    if (match) {
                        currentModule.align = { h: match[1], v: match[2] };
                    }
                    continue;
                }

                // Parse gap
                if (line.startsWith('gap ')) {
                    const match = line.match(/gap\s+(\d+(?:px|rem))/);
                    if (match) currentModule.gap = match[1];
                    continue;
                }

                // Parse color
                if (line.startsWith('color ')) {
                    const match = line.match(/color\s+"([^"]+)"/);
                    if (match) currentModule.color = match[1];
                    continue;
                }

                // Parse text-align
                if (line.startsWith('text-align ')) {
                    const match = line.match(/text-align\s+(left|center|right)/);
                    if (match) currentModule.textAlign = match[1];
                    continue;
                }

                // Parse component
                if (line.startsWith('component ')) {
                    const component = this._parseComponent(line, lineNum);
                    if (component) {
                        currentModule.components.push(component);
                    }
                    continue;
                }

                // Close module
                if (line === '}') {
                    currentModule = null;
                    continue;
                }
            }
        }

        // Validation
        this._validate(ast);

        return ast;
    }

    /**
     * Parse a component line
     * @private
     */
    _parseComponent(line, lineNum) {
        // Pattern: component "Name" { cols N, rows N } <<stereotype>>
        const match = line.match(/component\s+"([^"]+)"(?:\s*\{\s*cols\s+(\d+)(?:\s*,\s*rows\s+(\d+))?\s*\})?(?:\s*<<(\w+)>>)?/);
        
        if (match) {
            return {
                type: 'component',
                name: match[1],
                cols: match[2] ? parseInt(match[2]) : 1,
                rows: match[3] ? parseInt(match[3]) : 1,
                stereotype: match[4] || null
            };
        }

        this.errors.push({ line: lineNum, message: `Invalid component syntax: ${line}` });
        return null;
    }

    /**
     * Validate the AST
     * @private
     */
    _validate(ast) {
        // Check view type
        if (!ast.viewType) {
            this.errors.push({ line: 1, message: 'Missing @startuml header with view type' });
        }

        // Validate layers
        for (const layer of ast.layers) {
            // Check module cols sum to 12
            const colsSum = layer.modules.reduce((sum, m) => sum + m.cols, 0);
            if (colsSum !== 12 && layer.modules.length > 0) {
                this.warnings.push({ 
                    layer: layer.name, 
                    message: `Module cols sum to ${colsSum}, expected 12` 
                });
            }

            // Check each module has rows defined
            if (!layer.rows || layer.rows < 1) {
                this.warnings.push({
                    layer: layer.name,
                    message: 'Layer missing rows declaration'
                });
            }
        }
    }

    /**
     * Get validation result
     * @returns {Object} Validation result with isValid, errors, warnings
     */
    validate(dsl) {
        const ast = this.parse(dsl);
        return {
            isValid: ast.errors.length === 0,
            errors: ast.errors,
            warnings: ast.warnings
        };
    }
}

export default ArchitectureDSLParser;
