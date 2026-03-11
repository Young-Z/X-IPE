# X-IPE UI — QUICK REFERENCE FOR KB MOCKUP

## File Locations
- **Sidebar CSS**: `src/x_ipe/static/css/sidebar.css` (339 lines)
- **Sidebar JS**: `src/x_ipe/static/js/features/sidebar.js` (900+ lines)
- **Workplace CSS**: `src/x_ipe/static/css/workplace.css` (1552 lines)
- **Base CSS**: `src/x_ipe/static/css/base.css` (308 lines)
- **Terminal CSS**: `src/x_ipe/static/css/terminal.css` (642 lines)
- **Modal CSS**: `src/x_ipe/static/css/features/compose-idea-modal.css` (509 lines)
- **Workplace JS**: `src/x_ipe/static/js/features/workplace.js` (2800+ lines)
- **Tree Search JS**: `src/x_ipe/static/js/features/tree-search.js` (229 lines)

---

## CRITICAL MEASUREMENTS

### Layout Heights
| Component | Height | Notes |
|-----------|--------|-------|
| Top Menu | **36px** | Fixed, #1e1e1e background |
| Content Header | **50px** | var(--header-height) |
| Terminal Collapsed | **36px** | Icon bar only |
| Terminal Expanded | **300px** | Full console |
| Sidebar Collapsed | **48px** | Icon-only mode |
| Sidebar Expanded | **280px** | Full sidebar |
| Modal | **90vh x 90vw** | 90% screen size |

### Critical Padding/Spacing
| Element | Padding | Notes |
|---------|---------|-------|
| .nav-item | 0.35rem 1rem / L:2rem | 6px v, 16px h, 32px left |
| .sidebar-child | L:2rem | 32px left indent |
| .workplace-tree-item-content | 6px 8px | Per level: +16px |
| .tree-search-input | 6px 32px | Icon padding |
| .compose-modal-header | 16px 24px | Modal header |
| .top-menu | 0 1rem | No v-padding |

---

## KEY INTERACTION PATTERNS

### Pin/Expand System
```
HTML Class          CSS Effect              Icon
.collapsed          chevron visible         ↓ (down)
.expanded           children shown          ↓ expanded
.pinned             pin icon visible        📌 (#ffc107)
                    chevron hidden
```

### Color System
```
Emerald (#10b981):  Primary actions (submit, active tabs, focus)
Blue (#0d6efd):     Secondary actions (hover, nav icons, active)
Yellow (#ffc107):   Pin icon, warnings
Dark (#1e1e2e):     Dark sidebar bg
Light (#f8f9fa):    Light content header bg
```

### Search Behavior
```
Input → Debounce 150ms → Filter tree
Show clear button when text present
Highlight matches with yellow gradient
Dim parent folders (opacity 0.7)
Expand parent folders automatically
```

---

## EXACT CSS VALUES (Copy-Paste Ready)

### Sidebar Parent
```css
.sidebar-parent {
    cursor: default;
}
.sidebar-parent[data-no-action="true"]:hover {
    background-color: transparent;
}
```

### Sidebar Child
```css
.sidebar-child {
    padding-left: 2rem;        /* 32px */
    font-size: 0.9em;
}
.sidebar-child:hover {
    background-color: #2a2a3a;
}
.sidebar-child.active {
    background-color: #3a3a4a;
}
```

### Pin Icon
```css
.nav-section-header.pinned::after {
    content: '\F588';          /* bi-pin-fill */
    font-family: 'bootstrap-icons';
    font-size: 0.65rem;
    margin-left: auto;
    padding-left: 0.5rem;
    color: #ffc107;
    opacity: 0.9;
}
```

### Chevron Rotation
```css
.nav-section-header .chevron {
    margin-left: auto;
    transition: transform 0.2s;
}
.nav-section-header.collapsed .chevron {
    transform: rotate(-90deg);
}
```

### Workplace Sidebar Toggle
```css
.workplace-sidebar {
    width: 48px;               /* Collapsed */
    transition: width 0.2s ease;
}
.workplace-sidebar:hover,
.workplace-sidebar.expanded,
.workplace-sidebar.pinned {
    width: 280px;              /* Expanded */
}
```

### Tree Item Indentation
```javascript
// In workplace.js:
itemContent.style.paddingLeft = `${level * 16 + 8}px`;
// Level 0: 8px,  Level 1: 24px,  Level 2: 40px,  etc.
```

### Modal Structure
```css
.compose-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    z-index: 1051;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease, visibility 0.3s ease;
}
.compose-modal-overlay.active {
    opacity: 1;
    visibility: visible;
}

.compose-modal {
    border-radius: 12px;
    width: 90vw;
    height: 90vh;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    transform: scale(0.95) translateY(10px);
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.compose-modal-overlay.active .compose-modal {
    transform: scale(1) translateY(0);
}
```

### Search Input Styling
```css
.tree-search-input {
    width: 100%;
    padding: 6px 32px;         /* Space for icons */
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 13px;
}
.tree-search-input:focus {
    outline: none;
    border-color: #10b981;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}
```

### Top Bar
```css
.top-menu {
    height: 36px;              /* EXACT */
    background: #1e1e1e;
    border-bottom: 1px solid #333;
    padding: 0 1rem;
    z-index: 300;
}
.top-menu .brand-name {
    font-size: 1rem;           /* 16px */
    font-weight: 700;
    letter-spacing: 0.5px;
}
```

---

## BUTTONS & ICON SPECIFICATIONS

### Workplace Sidebar Icons
```css
.workplace-sidebar-icon {
    width: 36px;               /* Square buttons */
    height: 36px;
    border-radius: 6px;
    color: #6c757d;
    transition: all 0.15s;
}
.workplace-sidebar-icon:hover {
    background-color: #e9ecef;
    color: #0d6efd;            /* Blue highlight */
}
.workplace-sidebar-icon.active {
    background-color: #0d6efd;
    color: #fff;
}
```

### Modal Close Button
```css
.compose-modal-close {
    font-size: 20px;
    color: #64748b;
    padding: 4px 8px;
    border-radius: 4px;
    transition: color 0.2s, background-color 0.2s;
}
.compose-modal-close:hover {
    color: #1e293b;
    background-color: #f1f5f9;
}
```

### Submit Button
```css
.compose-modal-btn-submit {
    background: #10b981;       /* Emerald */
    color: #fff;
    border-radius: 8px;
    padding: 8px 20px;
}
.compose-modal-btn-submit:hover:not(:disabled) {
    background: #059669;       /* Darker emerald */
}
```

---

## BROWSER COMPATIBILITY NOTES

- **Backdrop-filter**: `blur(4px)` on modal overlay (may need vendor prefix)
- **Scrollbar styling**: `-webkit-scrollbar` custom colors in dark areas
- **CSS Variables**: `--sidebar-bg`, `--sidebar-text`, `--sidebar-hover`, `--sidebar-active`, `--content-bg`, `--header-height`
- **Grid/Flex**: All modern layout uses flexbox (no CSS Grid)
- **Transitions**: All 0.15s or 0.2s ease for consistency
- **Z-index stack**: 
  - Modal: 1051
  - Terminal: 450
  - Middle section: 400
  - Top menu: 300

---

## ACCESSIBILITY FEATURES

- **Aria labels**: Search inputs have `aria-label="Search files and folders"`
- **User-select**: Terminal header is `user-select: none`
- **Focus states**: Blue focus rings on inputs (#10b981 border + shadow)
- **Keyboard shortcuts**: Escape to clear search and blur
- **Color contrast**: Dark text on light (#fff on #0d6efd), light on dark (#ccc on #1e1e1e)

---

## ANIMATION TIMINGS

| Animation | Duration | Easing |
|-----------|----------|--------|
| Sidebar width | 0.2s | ease |
| Background color | 0.15s | default |
| Modal overlay | 0.3s | ease |
| Modal transform | 0.3s | cubic-bezier(0.34, 1.56, 0.64, 1) (spring) |
| Chevron rotation | 0.2s | default |
| Search focus | 0.15s | ease |
| Transition delay | 150ms | debounce |

---

## CSS VARIABLES REFERENCE

```css
:root {
    --top-menu-height: 36px;
    --sidebar-width: 280px;
    --console-collapsed-height: 36px;
    --console-expanded-height: 300px;
    --sidebar-bg: #1e1e2e;
    --sidebar-text: #cdd6f4;
    --sidebar-hover: #313244;
    --sidebar-active: #45475a;
    --content-bg: #ffffff;
    --header-height: 50px;
    
    /* CR-006 Design System */
    --cr006-color-primary: #0f172a;
    --cr006-color-secondary: #475569;
    --cr006-color-accent: #10b981;
    --cr006-color-accent-light: #d1fae5;
    --cr006-color-border: #e2e8f0;
    --cr006-color-bg: #f8fafc;
    --cr006-color-error: #ef4444;
    --cr006-color-error-light: #fee2e2;
    --cr006-radius-sm: 4px;
    --cr006-radius-md: 8px;
    --cr006-radius-lg: 12px;
}
```

---

## COMMON ISSUES & SOLUTIONS

### Issue: Sidebar text cut off in collapsed mode
**Solution**: Content hidden with `display: none` on `.workplace-sidebar-content` when width is 48px

### Issue: Tree items misaligned at different levels
**Solution**: Dynamic padding: `level * 16 + 8px` ensures consistent indentation

### Issue: Modal doesn't scroll
**Solution**: `.compose-modal-body` has `flex: 1; overflow-y: auto; padding: 24px;`

### Issue: Terminal sessions not showing
**Solution**: `.terminal-body` is `display: flex` only when `.terminal-panel.expanded`

### Issue: Search doesn't work on first character
**Solution**: Debounce delay is 150ms, waits before filtering

