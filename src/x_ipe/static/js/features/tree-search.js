/**
 * TreeSearchManager - Search/filter tree functionality
 * FEATURE-008 CR-006: Folder Tree UX Enhancement
 * 
 * Provides:
 * - Search bar in tree header
 * - Real-time filtering with debounce
 * - Preserves parent folder context for matches
 * - Clear button and keyboard shortcuts
 */
class TreeSearchManager {
    constructor(options) {
        this.treeContainer = options.treeContainer;
        this.onSearch = options.onSearch || null; // Optional callback for API-based search
        this.searchInput = null;
        this.clearBtn = null;
        this.debounceTimer = null;
        this.debounceDelay = 150;
    }

    /**
     * Initialize search functionality
     */
    init() {
        this._createSearchBar();
        this._bindEvents();
    }

    /**
     * Create the search bar UI
     */
    _createSearchBar() {
        const header = this.treeContainer.closest('.workplace-sidebar-content')
            ?.querySelector('.workplace-sidebar-header');
        
        if (!header) {
            console.warn('TreeSearchManager: Could not find sidebar header');
            return;
        }

        // Check if search bar already exists
        if (header.parentElement.querySelector('.tree-search-container')) {
            this.searchInput = header.parentElement.querySelector('.tree-search-input');
            this.clearBtn = header.parentElement.querySelector('.tree-search-clear');
            return;
        }

        const searchHtml = `
            <div class="tree-search-container">
                <div class="tree-search-wrapper">
                    <i class="bi bi-search tree-search-icon"></i>
                    <input type="text" 
                           class="tree-search-input" 
                           placeholder="Filter files and folders..."
                           aria-label="Search files and folders">
                    <button class="tree-search-clear" 
                            type="button" 
                            title="Clear search"
                            style="display: none;">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
            </div>
        `;
        
        header.insertAdjacentHTML('afterend', searchHtml);
        this.searchInput = header.nextElementSibling.querySelector('.tree-search-input');
        this.clearBtn = header.nextElementSibling.querySelector('.tree-search-clear');
    }

    /**
     * Bind event listeners
     */
    _bindEvents() {
        if (!this.searchInput) return;

        // Input handler with debounce
        this.searchInput.addEventListener('input', (e) => {
            const query = e.target.value;
            
            // Show/hide clear button
            this.clearBtn.style.display = query ? 'flex' : 'none';
            
            // Debounce the filter
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this._filterTree(query);
            }, this.debounceDelay);
        });

        // Clear button handler
        this.clearBtn.addEventListener('click', () => {
            this.clear();
        });

        // Keyboard shortcuts
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.clear();
                this.searchInput.blur();
            }
        });
    }

    /**
     * Filter tree items based on query
     * @param {string} query - Search query
     */
    _filterTree(query) {
        const normalizedQuery = query.toLowerCase().trim();
        
        // If callback provided, use API-based search
        if (this.onSearch) {
            this.onSearch(normalizedQuery);
            return;
        }

        // Client-side filtering
        const items = this.treeContainer.querySelectorAll('.tree-item');
        
        if (!normalizedQuery) {
            // Show all items and collapse folders
            items.forEach(item => {
                item.style.display = '';
                item.classList.remove('search-match', 'search-parent', 'expanded');
                const childContainer = item.querySelector('.tree-children');
                if (childContainer) {
                    childContainer.style.display = 'none';
                }
            });
            return;
        }

        // Find matching items and their parent paths
        const matchingPaths = new Set();
        const parentPaths = new Set();

        items.forEach(item => {
            const label = item.querySelector('.tree-label');
            const name = label?.textContent?.toLowerCase() || '';
            const path = item.dataset.path;

            if (name.includes(normalizedQuery)) {
                matchingPaths.add(path);
                
                // Add all parent paths for context
                if (path) {
                    const parts = path.split('/');
                    for (let i = 1; i < parts.length; i++) {
                        parentPaths.add(parts.slice(0, i).join('/'));
                    }
                }
            }
        });

        // Apply visibility and styling
        items.forEach(item => {
            const path = item.dataset.path;
            const isMatch = matchingPaths.has(path);
            const isParent = parentPaths.has(path);
            
            if (isMatch || isParent) {
                item.style.display = '';
                item.classList.toggle('search-match', isMatch);
                item.classList.toggle('search-parent', isParent && !isMatch);
                
                // Expand parent folders
                if (isParent) {
                    const childContainer = item.querySelector('.tree-children');
                    if (childContainer) {
                        childContainer.style.display = 'block';
                    }
                    item.classList.add('expanded');
                }
            } else {
                item.style.display = 'none';
                item.classList.remove('search-match', 'search-parent');
            }
        });
    }

    /**
     * Clear the search
     */
    clear() {
        if (!this.searchInput) return;
        
        this.searchInput.value = '';
        this.clearBtn.style.display = 'none';
        this._filterTree('');
    }

    /**
     * Get current search query
     * @returns {string}
     */
    getQuery() {
        return this.searchInput?.value || '';
    }

    /**
     * Set search query programmatically
     * @param {string} query 
     */
    setQuery(query) {
        if (!this.searchInput) return;
        
        this.searchInput.value = query;
        this.clearBtn.style.display = query ? 'flex' : 'none';
        this._filterTree(query);
    }

    /**
     * Destroy the search manager
     */
    destroy() {
        clearTimeout(this.debounceTimer);
        const container = this.searchInput?.closest('.tree-search-container');
        if (container) {
            container.remove();
        }
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TreeSearchManager;
}
