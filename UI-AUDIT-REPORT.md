# X-IPE UI AUDIT REPORT
## Exact Details for KB Mockup Comparison

---

## 1. SIDEBAR.CSS — Exact CSS Specifications

### File: `/src/x_ipe/static/css/sidebar.css`

#### .sidebar-parent (Lines 298-304)
**Purpose**: Parent container for sidebar sections (no action state)
```css
.sidebar-parent {
    cursor: default;
}

.sidebar-parent[data-no-action="true"]:hover {
    background-color: transparent;
}
```
- **Cursor**: `default` (not clickable)
- **Hover state**: `transparent` (no highlight)

#### .sidebar-child (Lines 317-338)
**Purpose**: Child navigation items under sections
```css
.sidebar-child {
    padding-left: 2rem;
    font-size: 0.9em;
}

.sidebar-child:hover {
    background-color: var(--sidebar-hover, #2a2a3a);
}

.sidebar-child.active,
.sidebar-parent.active-parent {
    background-color: var(--sidebar-active, #3a3a4a);
}
```
- **Padding-left**: `2rem` (32px indentation)
- **Font-size**: `0.9em` (relative sizing)
- **Hover background**: `#2a2a3a`
- **Active background**: `#3a3a4a`

#### .sidebar-submenu (Lines 312-315)
**Purpose**: Container for nested navigation items
```css
.sidebar-submenu {
    display: flex;
    flex-direction: column;
}
```
- **Display**: `flex` column
- **No margins or padding** (inherited from parent)

#### Pin Icon & Expand Chevron (Lines 243-257)
**Purpose**: Visual indicators for pinned and collapsed state
```css
.nav-section-header.pinned::after,
.nav-folder.pinned::after {
    content: '\F588';  /* Bootstrap Icons pin-fill */
    font-family: 'bootstrap-icons';
    font-size: 0.65rem;
    margin-left: auto;
    padding-left: 0.5rem;
    color: var(--bs-warning, #ffc107);
    opacity: 0.9;
}

.nav-section-header.pinned .chevron,
.nav-folder.pinned .chevron {
    display: none;
}
```
- **Pin icon**: Bootstrap icon `\F588` (bi-pin-fill)
- **Size**: `0.65rem` (~10px)
- **Color**: `#ffc107` (warning yellow)
- **Opacity**: `0.9`
- **Position**: Right margin auto (aligns right)

#### Chevron Animation (Lines 150-157)
```css
.nav-section-header .chevron {
    margin-left: auto;
    transition: transform 0.2s;
}

.nav-section-header.collapsed .chevron {
    transform: rotate(-90deg);
}
```
- **Margin**: `auto` on left (positions right)
- **Transition**: `transform 0.2s` (smooth rotation)
- **Collapsed rotation**: `-90deg`

#### Submenu Indicator (Lines 306-310)
```css
.submenu-indicator {
    margin-left: auto;
    font-size: 0.75em;
    opacity: 0.6;
}
```
- **Size**: `0.75em` relative
- **Opacity**: `0.6` (subtle)

#### Core Sidebar Container (Lines 9-20)
```css
.sidebar {
    flex: 0 0 var(--sidebar-width);
    width: var(--sidebar-width);
    min-width: 200px;
    max-width: 500px;
    background-color: var(--sidebar-bg);
    color: var(--sidebar-text);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
}
```
- **Width**: `280px` (var default)
- **Min-width**: `200px`
- **Max-width**: `500px`
- **Background**: `#1e1e2e`
- **Text color**: `#cdd6f4` (light)
- **Min-height**: `0` (allows flex child scrolling)

#### Navigation Section Header (Lines 122-156)
```css
.nav-section-header {
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
    cursor: pointer;
    user-select: none;
    transition: background-color 0.15s;
    background-color: rgba(49, 50, 68, 0.35);
    border-radius: 6px;
    margin: 2px 8px;
}

.nav-section-header:hover {
    background-color: var(--sidebar-hover);
}

.nav-section-header i {
    margin-right: 0.5rem;
    font-size: 0.9rem;
}
```
- **Padding**: `0.5rem 1rem` (8px 16px)
- **Background**: `rgba(49, 50, 68, 0.35)` (semi-transparent)
- **Border-radius**: `6px`
- **Margin**: `2px 8px`
- **Icon margin-right**: `0.5rem`
- **Icon size**: `0.9rem`
- **Transition**: `0.15s` background color

#### Navigation Items (Lines 173-198)
```css
.nav-item {
    display: flex;
    align-items: center;
    padding: 0.35rem 1rem;
    padding-left: 2rem;
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.15s;
    text-decoration: none;
    color: var(--sidebar-text);
}

.nav-item:hover {
    background-color: var(--sidebar-hover);
    color: var(--sidebar-text);
}

.nav-item.active {
    background-color: var(--sidebar-active);
}

.nav-item i {
    margin-right: 0.5rem;
    font-size: 0.8rem;
    opacity: 0.8;
}
```
- **Padding**: `0.35rem 1rem` vertical, `2rem` left
- **Font-size**: `0.875rem` (14px)
- **Hover bg**: `var(--sidebar-hover)` = `#313244`
- **Active bg**: `var(--sidebar-active)` = `#45475a`
- **Icon margin-right**: `0.5rem`
- **Icon size**: `0.8rem`
- **Icon opacity**: `0.8`

---

## 2. SIDEBAR.JS — Pin/Expand Interaction Details

### File: `/src/x_ipe/static/js/features/sidebar.js`

#### State Tracking (Lines 19-23)
```javascript
this.pinnedSections = new Set();      // Set of section IDs
this.pinnedFolders = new Set();       // Set of folder paths
this.expandedSections = new Set();    // Set of section IDs
this.expandedFolders = new Set();     // Set of folder paths
```
- **Pinned sections**: IDs stored to persist across re-renders
- **Pinned folders**: Full paths stored for folder state

#### Icon Classes Used
- **Pin icon**: Bootstrap `bi-pin` (unpinned) → `bi-pin-fill` (pinned)
- **Chevron**: Bootstrap `bi-chevron-down` (shown) → rotated -90deg (collapsed)

#### Active State Highlighting (Lines 520-551)
```javascript
// FEATURE-022-A: Clear sidebar-child active state when selecting a file
const sidebarChildren = this.container.querySelectorAll('.sidebar-child');
sidebarChildren.forEach(child => child.classList.remove('active'));

// Then add active class to current section
const activeChild = this.container.querySelector(`.sidebar-child[data-section-id="${sectionId}"]`);
if (activeChild) {
    activeChild.classList.add('active');
}
```
**Logic**:
1. Query all `.sidebar-child` elements
2. Remove `.active` class from all
3. Add `.active` to matching `[data-section-id]`
4. Class triggers `background-color: var(--sidebar-active, #3a3a4a)`

#### State Preservation System (Lines 251-330)
**Save phase** (Lines 254-283):
- Query `.nav-section-header:not(.collapsed)` → add to `expandedSections`
- Query `.nav-section-header.pinned` → add to `pinnedSections`
- Query folders with `.expanded` class → add path to `expandedFolders`
- Query folders with `.pinned` class → add path to `pinnedFolders`

**Restore phase** (Lines 289-330):
- For each in `expandedSections`: remove `.collapsed` class
- For each in `pinnedSections`: remove `.collapsed`, add `.pinned`
- For each in `expandedFolders`: add `.expanded` class
- For each in `pinnedFolders`: add `.expanded` and `.pinned` classes

#### Pin/Expand Mechanism
- **HTML classes**:
  - `.collapsed` = section/folder is collapsed
  - `.pinned` = section/folder is pinned (shows pin icon via `::after`)
  - `.expanded` = folder shows children

- **CSS cascading**: `.pinned` removes `.chevron` display, shows pin icon

---

## 3. WORKPLACE.CSS — Sidebar Structure & Button Styles

### File: `/src/x_ipe/static/css/workplace.css`

#### .workplace-sidebar Container (Lines 18-34)
```css
.workplace-sidebar {
    width: 48px;
    min-width: 48px;
    background-color: #f8f9fa;
    border-right: 1px solid #dee2e6;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transition: width 0.2s ease, min-width 0.2s ease;
}

.workplace-sidebar:hover,
.workplace-sidebar.expanded,
.workplace-sidebar.pinned {
    width: 280px;
    min-width: 280px;
}
```
- **Collapsed width**: `48px` (icon-only mode)
- **Expanded width**: `280px` (on hover, .expanded, or .pinned)
- **Background**: `#f8f9fa` (light gray)
- **Border-right**: `1px solid #dee2e6`
- **Transition**: `0.2s ease` width change

#### Icon Button Styles (Lines 44-70)
```css
.workplace-sidebar-icon {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    cursor: pointer;
    color: #6c757d;
    transition: all 0.15s;
    border: none;
    background: none;
}

.workplace-sidebar-icon:hover {
    background-color: #e9ecef;
    color: #0d6efd;
}

.workplace-sidebar-icon.active {
    background-color: #0d6efd;
    color: #fff;
}

.workplace-sidebar-icon i {
    font-size: 1.1rem;
}
```
- **Size**: `36x36px`
- **Border-radius**: `6px`
- **Default color**: `#6c757d` (gray)
- **Icon size**: `1.1rem` (~18px)
- **Hover state**: bg `#e9ecef`, color `#0d6efd` (blue)
- **Active state**: bg `#0d6efd` (blue), color `#fff`
- **Transition**: `all 0.15s`

#### Content Visibility Toggle (Lines 72-89)
```css
.workplace-sidebar-content {
    display: none;
    flex: 1;
    flex-direction: column;
    overflow: hidden;
}

.workplace-sidebar:hover .workplace-sidebar-content,
.workplace-sidebar.expanded .workplace-sidebar-content,
.workplace-sidebar.pinned .workplace-sidebar-content {
    display: flex;
}

.workplace-sidebar:hover .workplace-sidebar-icons,
.workplace-sidebar.expanded .workplace-sidebar-icons,
.workplace-sidebar.pinned .workplace-sidebar-icons {
    display: none;
}
```
- **Content hidden by default**: `display: none`
- **Shown on**: `:hover`, `.expanded`, `.pinned`
- **Icons hidden when**: content shown (one or the other)

#### Sidebar Header (Lines 92-105)
```css
.workplace-sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    border-bottom: 1px solid #e9ecef;
    flex-shrink: 0;
}

.workplace-sidebar-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: #495057;
}
```
- **Padding**: `8px 12px`
- **Border-bottom**: `1px solid #e9ecef`
- **Title font-size**: `0.9rem` (~14px)
- **Title weight**: `600`
- **Title color**: `#495057` (dark gray)

#### Pin Button & Action Buttons (Lines 113-139)
```css
.workplace-create-folder-btn,
.workplace-collapse-all-btn,
.workplace-pin-btn {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: none;
    border-radius: 4px;
    cursor: pointer;
    color: #6c757d;
    transition: all 0.15s;
}

.workplace-create-folder-btn:hover,
.workplace-collapse-all-btn:hover,
.workplace-pin-btn:hover {
    background-color: #e9ecef;
    color: #0d6efd;
}

.workplace-sidebar.pinned .workplace-pin-btn {
    color: #0d6efd;
    background-color: rgba(13, 110, 253, 0.1);
}
```
- **Button size**: `28x28px`
- **Border-radius**: `4px`
- **Default color**: `#6c757d`
- **Hover**: bg `#e9ecef`, color `#0d6efd`
- **Active (pinned)**: bg `rgba(13, 110, 253, 0.1)`, color `#0d6efd`

#### Tree Content Area (Lines 149-153)
```css
.workplace-tree {
    flex: 1;
    overflow-y: auto;
    padding: 0 8px 8px;
}
```
- **Flex**: `1` (fills remaining space)
- **Overflow-y**: `auto` (scrollable)
- **Padding**: `0 8px 8px` (horizontal 8px, bottom 8px)

---

## 4. TOP-BAR CSS — Exact Styling (base.css)

### File: `/src/x_ipe/static/css/base.css`

#### CSS Variables (Lines 6-17)
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
}
```
- **Top menu height**: `36px` ← **EXACT HEIGHT**
- **Sidebar width**: `280px`
- **Content bg**: `#ffffff`
- **Header height**: `50px`

#### .top-menu Container (Lines 41-51)
```css
.top-menu {
    flex: 0 0 var(--top-menu-height);
    height: var(--top-menu-height);
    background: #1e1e1e;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 1rem;
    z-index: 300;
}
```
- **Height**: `36px` (fixed)
- **Background**: `#1e1e1e` (dark)
- **Border-bottom**: `1px solid #333`
- **Padding**: `0 1rem` (0 vertical, 16px horizontal)
- **Z-index**: `300`

#### Brand Logo/Name (Lines 53-78)
```css
.top-menu .brand {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #fff;
    text-decoration: none;
}

.top-menu .brand-name {
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: inherit;
    text-decoration: none;
    cursor: pointer;
}

.top-menu .brand-name:hover {
    color: #3b82f6;
}

.top-menu .brand-subtitle {
    font-size: 0.65rem;
    color: #888;
    margin-left: 0.5rem;
}
```
- **Brand name font-size**: `1rem` (~16px)
- **Brand name weight**: `700` (bold)
- **Letter-spacing**: `0.5px`
- **Brand name hover**: `#3b82f6` (blue)
- **Subtitle font-size**: `0.65rem` (~10px)
- **Subtitle color**: `#888` (gray)
- **Gap between brand items**: `0.5rem` (8px)

#### Menu Actions Container (Lines 128-156)
```css
.top-menu .menu-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.top-menu .menu-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #888;
    text-decoration: none;
    font-size: 0.85rem;
    padding: 0.375rem 0.75rem;
    border-radius: 4px;
    transition: all 0.15s;
    background: none;
    border: none;
    cursor: pointer;
}

.top-menu .menu-link:hover {
    color: #fff;
    background: #333;
}

.top-menu .menu-link i {
    font-size: 1rem;
}
```
- **Menu actions gap**: `1rem` (16px between buttons)
- **Menu link font-size**: `0.85rem` (~14px)
- **Menu link padding**: `0.375rem 0.75rem` (6px 12px)
- **Menu link border-radius**: `4px`
- **Link color**: `#888` (gray)
- **Link hover color**: `#fff`
- **Link hover bg**: `#333`
- **Icon size**: `1rem` (16px)
- **Gap in link**: `0.5rem` (8px between icon and text)

---

## 5. MODAL PATTERNS — Compose Idea Modal Exact Specs

### File: `/src/x_ipe/static/css/features/compose-idea-modal.css`

#### Modal Overlay (Lines 10-28)
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
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Sans', sans-serif;
}

.compose-modal-overlay.active {
    opacity: 1;
    visibility: visible;
}
```
- **Position**: Fixed, full screen (`inset: 0`)
- **Background**: `rgba(0, 0, 0, 0.4)` (40% opacity black)
- **Backdrop-filter**: `blur(4px)` (4px blur)
- **Z-index**: `1051`
- **Default state**: `opacity: 0`, `visibility: hidden`
- **Active state**: `opacity: 1`, `visibility: visible`
- **Transition**: `0.3s ease` for both opacity and visibility
- **Font-family**: `'DM Sans', sans-serif`

#### Modal Dialog (Lines 33-49)
```css
.compose-modal {
    background: #fff;
    border-radius: 12px;
    width: 90vw;
    height: 90vh;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    transform: scale(0.95) translateY(10px);
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    overflow: hidden;
}

.compose-modal-overlay.active .compose-modal {
    transform: scale(1) translateY(0);
}
```
- **Width**: `90vw` (90% viewport width)
- **Height**: `90vh` (90% viewport height)
- **Max-height**: `90vh`
- **Border-radius**: `12px` (rounded corners)
- **Background**: `#fff`
- **Box-shadow**: `0 20px 60px rgba(0, 0, 0, 0.3)` (deep shadow)
- **Initial transform**: `scale(0.95) translateY(10px)` (shrunk & offset)
- **Active transform**: `scale(1) translateY(0)` (normal size)
- **Transition**: `0.3s cubic-bezier(0.34, 1.56, 0.64, 1)` (spring easing)

#### Modal Header (Lines 54-84)
```css
.compose-modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    border-bottom: 1px solid #e2e8f0;
}

.compose-modal-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
}

.compose-modal-close {
    background: none;
    border: none;
    font-size: 20px;
    color: #64748b;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    line-height: 1;
    transition: color 0.2s, background-color 0.2s;
}

.compose-modal-close:hover {
    color: #1e293b;
    background-color: #f1f5f9;
}
```
- **Header padding**: `16px 24px` (16px vertical, 24px horizontal)
- **Header border-bottom**: `1px solid #e2e8f0`
- **Title font-size**: `18px`
- **Title weight**: `600`
- **Title color**: `#1e293b`
- **Close button size**: `20px` (font-size)
- **Close button padding**: `4px 8px`
- **Close button border-radius**: `4px`
- **Close button default color**: `#64748b` (gray)
- **Close button hover color**: `#1e293b` (dark)
- **Close button hover bg**: `#f1f5f9` (light gray)
- **Transition**: `0.2s` for color and background

#### Modal Body (Lines 89-92)
```css
.compose-modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
}
```
- **Flex**: `1` (fills available space)
- **Overflow-y**: `auto` (scrollable)
- **Padding**: `24px` (all sides)

#### Name Input Styling (Lines 144-160)
```css
.compose-modal-name input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    color: #1e293b;
    transition: border-color 0.2s;
    font-family: inherit;
    box-sizing: border-box;
}

.compose-modal-name input:focus {
    outline: none;
    border-color: #10b981;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}
```
- **Input padding**: `10px 12px`
- **Input border**: `1px solid #e2e8f0`
- **Input border-radius**: `8px`
- **Input font-size**: `14px`
- **Focus border-color**: `#10b981` (emerald green)
- **Focus box-shadow**: `0 0 0 3px rgba(16, 185, 129, 0.1)` (soft glow)

#### Submit Button (Lines 386-398)
```css
.compose-modal-btn-submit {
    background: #10b981;
    color: #fff;
}

.compose-modal-btn-submit:hover:not(:disabled) {
    background: #059669;
}

.compose-modal-btn-submit:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
```
- **Background**: `#10b981` (emerald)
- **Hover background**: `#059669` (darker emerald)
- **Color**: `#fff` (white text)
- **Disabled opacity**: `0.5`

#### Tab Styling (Lines 194-221)
```css
.compose-modal-tabs {
    display: flex;
    gap: 0;
    margin-bottom: 16px;
    border-bottom: 1px solid #e2e8f0;
}

.compose-modal-tabs button {
    padding: 8px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    background: none;
    color: #64748b;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
}

.compose-modal-tabs button.active {
    color: #10b981;
    border-bottom-color: #10b981;
}

.compose-modal-tabs button:hover:not(.active) {
    color: #334155;
}
```
- **Tab padding**: `8px 20px`
- **Tab border-bottom**: `2px solid transparent` (or `#10b981` when active)
- **Tab font-size**: `14px`
- **Tab weight**: `500`
- **Active color**: `#10b981` (emerald)
- **Hover color**: `#334155` (darker gray)

---

## 6. CONTENT AREA — Header & Body Styling

### File: `/src/x_ipe/static/css/base.css`

#### .content-header (Lines 182-196)
```css
.content-header {
    flex: 0 0 var(--header-height);
    height: var(--header-height);
    padding: 0 1rem;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #f8f9fa;
}

.content-header .breadcrumb {
    margin: 0;
    font-size: 0.875rem;
}
```
- **Height**: `50px` (from `--header-height`)
- **Padding**: `0 1rem` (0 vertical, 16px horizontal)
- **Background**: `#f8f9fa` (light gray)
- **Border-bottom**: `1px solid #e9ecef` (subtle divider)
- **Breadcrumb font-size**: `0.875rem` (~14px)
- **Flex layout**: space-between (aligns children left and right)

#### .content-area (Lines 172-180)
```css
.content-area {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background-color: var(--content-bg);
    min-width: 0;
    min-height: 0;
}
```
- **Flex**: `1 1 auto` (expands to fill space)
- **Background**: `#ffffff` (white)
- **Overflow**: `hidden` (children handle scroll)
- **Min-width/height**: `0` (allows flex children to shrink)

#### .content-body (Lines 198-204)
```css
.content-body {
    flex: 1 1 auto;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 1.5rem;
    min-height: 0;
}
```
- **Flex**: `1 1 auto` (fills remaining space)
- **Overflow-y**: `auto` (vertical scroll)
- **Overflow-x**: `hidden` (no horizontal scroll)
- **Padding**: `1.5rem` (24px all sides)
- **Min-height**: `0` (allows scroll)

---

## 7. TERMINAL PANEL — Exact CSS Specifications

### File: `/src/x_ipe/static/css/terminal.css`

#### .terminal-panel States (Lines 11-40)
```css
.terminal-panel {
    background-color: #1e1e1e;
    border-top: 1px solid #333;
    display: flex;
    flex-direction: column;
    z-index: 450;
    position: relative;
}

.terminal-panel.collapsed {
    height: 36px;
}

.terminal-panel.expanded {
    height: 300px;
    flex-shrink: 0;
}

.terminal-panel.zen-mode {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    height: 100vh !important;
    z-index: 9999;
}
```
- **Normal background**: `#1e1e1e` (dark)
- **Border-top**: `1px solid #333`
- **Collapsed height**: `36px`
- **Expanded height**: `300px`
- **Expanded flex-shrink**: `0` (no shrinking)
- **Zen mode**: full screen (`100vh`), z-index `9999`

#### .terminal-header (Lines 88-107)
```css
.terminal-header {
    height: 36px;
    min-height: 36px;
    max-height: 36px;
    display: flex;
    align-items: center;
    padding: 0 10px;
    background-color: #252526;
    cursor: pointer;
    -webkit-user-select: none;
    user-select: none;
    color: #ccc;
    font-size: 13px;
    gap: 10px;
}

.terminal-header:hover {
    background: #2d2d2d;
}
```
- **Height**: `36px` (fixed, min and max)
- **Padding**: `0 10px` (0 vertical, 10px horizontal)
- **Background**: `#252526` (slightly lighter dark)
- **Font-size**: `13px`
- **Color**: `#ccc` (light gray)
- **Gap**: `10px` between children
- **Hover bg**: `#2d2d2d` (lighter on hover)
- **User-select**: `none` (not selectable)

#### Session Tabs (Lines 314-333)
```css
.session-bar {
    display: flex;
    align-items: center;
    padding: 6px 12px;
    cursor: pointer;
    gap: 8px;
    font-size: 13px;
    color: #ccc;
    border-left: 3px solid transparent;
    transition: background-color 0.15s;
}

.session-bar:hover {
    background: #2a2d2e;
}

.session-bar[data-active="true"] {
    border-left-color: #4ec9b0;
    background: #37373d;
    color: #fff;
}
```
- **Padding**: `6px 12px`
- **Font-size**: `13px`
- **Gap**: `8px`
- **Border-left**: `3px solid transparent`
- **Active border-left**: `#4ec9b0` (teal)
- **Active background**: `#37373d`
- **Active color**: `#fff`
- **Hover background**: `#2a2d2e`

---

## 8. TREE ITEMS — Rendering & Styling Details

### File: `/src/x_ipe/static/js/features/workplace.js` (rendering)
### File: `/src/x_ipe/static/css/workplace.css` (styling)

#### HTML Structure (Lines 526-550 workplace.js)
```javascript
const li = document.createElement('li');
li.className = 'workplace-tree-item tree-item';
li.dataset.path = node.path;
li.dataset.type = node.type;  // 'folder' or 'file'
li.dataset.name = node.name;
li.setAttribute('draggable', 'true');

const itemContent = document.createElement('div');
itemContent.className = 'workplace-tree-item-content';
itemContent.style.paddingLeft = `${level * 16 + 8}px`;

const icon = document.createElement('i');
icon.className = node.type === 'folder' ? 'bi bi-folder' : 'bi bi-file-earmark';

const nameSpan = document.createElement('span');
nameSpan.className = 'workplace-tree-name tree-label';
nameSpan.textContent = node.name;

const actionBtns = document.createElement('div');
actionBtns.className = 'workplace-tree-actions';
```

#### Indentation Formula
```javascript
paddingLeft = level * 16 + 8  // Level 0 = 8px, Level 1 = 24px, Level 2 = 40px, etc.
```
- **Per-level increment**: `16px`
- **Base padding**: `8px` (level 0)
- **Level 0**: 8px
- **Level 1**: 24px
- **Level 2**: 40px
- **Pattern**: Each nested level adds 16px

#### Tree Item CSS (Lines 165-202 workplace.css)
```css
.workplace-tree-item-content {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 8px;
    border-radius: 4px;
    font-size: 0.85rem;
    transition: background-color 0.15s;
}

.workplace-tree-item-content:hover {
    background-color: #e9ecef;
}

.workplace-tree-item-content i {
    color: #6c757d;
    flex-shrink: 0;
}
```
- **Padding**: `6px 8px` (6px vertical, 8px horizontal)
- **Border-radius**: `4px`
- **Font-size**: `0.85rem` (~13px)
- **Gap**: `6px` between elements
- **Hover bg**: `#e9ecef`
- **Icon color**: `#6c757d`
- **Icon flex-shrink**: `0` (maintains size)

#### Chevron/Expand Icon (Lines 192-202)
```css
.workplace-tree-item.has-children > .workplace-tree-item-content::before {
    content: '\F229';
    font-family: 'bootstrap-icons';
    font-size: 0.7rem;
    margin-right: 2px;
    transition: transform 0.15s;
}

.workplace-tree-item.has-children.expanded > .workplace-tree-item-content::before {
    transform: rotate(90deg);
}
```
- **Chevron icon**: Bootstrap `\F229` (bi-chevron-right)
- **Size**: `0.7rem` (~11px)
- **Margin-right**: `2px`
- **Rotation**: `90deg` when expanded
- **Transition**: `transform 0.15s`

---

## 9. TREE SEARCH — Input & Behavior Details

### File: `/src/x_ipe/static/js/features/tree-search.js`
### File: `/src/x_ipe/static/css/workplace.css`

#### HTML Structure (Lines 48-64 tree-search.js)
```html
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
```

#### CSS Styles (Lines 969-1027 workplace.css)
```css
.tree-search-container {
    padding: 8px 12px;
    border-bottom: 1px solid var(--cr006-color-border);  /* #e2e8f0 */
}

.tree-search-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.tree-search-icon {
    position: absolute;
    left: 10px;
    color: var(--cr006-color-secondary);  /* #475569 */
    font-size: 14px;
    pointer-events: none;
}

.tree-search-input {
    width: 100%;
    padding: 6px 32px 6px 32px;
    border: 1px solid var(--cr006-color-border);  /* #e2e8f0 */
    border-radius: var(--cr006-radius-md);  /* 8px */
    font-size: 13px;
    background: white;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.tree-search-input:focus {
    outline: none;
    border-color: var(--cr006-color-accent);  /* #10b981 */
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.tree-search-input::placeholder {
    color: #94a3b8;
}

.tree-search-clear {
    position: absolute;
    right: 6px;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    color: var(--cr006-color-secondary);  /* #475569 */
    border-radius: 50%;
    cursor: pointer;
    transition: background 0.15s ease;
}

.tree-search-clear:hover {
    background: var(--cr006-color-border);  /* #e2e8f0 */
    color: var(--cr006-color-primary);  /* #0f172a */
}
```

#### Search Behavior (Lines 78-88 tree-search.js)
```javascript
// Input handler with debounce
this.searchInput.addEventListener('input', (e) => {
    const query = e.target.value;
    
    // Show/hide clear button
    this.clearBtn.style.display = query ? 'flex' : 'none';
    
    // Debounce the filter
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
        this._filterTree(query);
    }, this.debounceDelay);  // 150ms
});
```
- **Debounce delay**: `150ms`
- **Clear button**: hidden by default, shown when input has text
- **Keyboard shortcut**: `Escape` to clear and blur

#### Search Result Highlighting (Lines 1030-1035)
```css
.tree-item.search-match .tree-label {
    background: linear-gradient(transparent 60%, #fef08a 60%);  /* Yellow highlight */
}

.tree-item.search-parent {
    opacity: 0.7;
}
```
- **Match highlight**: Yellow gradient `#fef08a` (bottom 40%)
- **Parent opacity**: `0.7` (dimmed)

---

## 10. COLOR ACCENT USAGE — Exact Colors & Locations

### Primary Action Color: #10b981 (Emerald Green)

**Used for**:
- Compose modal submit button (background)
- Submit button hover state (darker: #059669)
- Tab active underline
- Search input focus border
- Focus box-shadow (with 0.1 opacity)
- Terminal active session indicator (#4ec9b0 — alternative teal)

**CSS Variables**:
```css
--wf-accent: #10b981;              /* workflow.css line 7 */
--uiux-accent: #10b981;            /* uiux-feedback.css line 20 */
--cr006-color-accent: #10b981;     /* workplace.css line 955 */
--tracing-status-success: #10b981; /* tracing-dashboard.css line 17 */
```

### Secondary Action Color: #0d6efd (Bootstrap Blue)

**Used for**:
- Workplace sidebar icon hover/active states
- Download button color
- Menu link hover color
- Pin button active state (and hover)
- Sidebar resize handle on hover
- Input border focus (sometimes #10b981 preferred)

**CSS Pattern**:
```css
background-color: #0d6efd;
color: #0d6efd;
border-color: #0d6efd;
```

**Files using #0d6efd**:
- `workplace.css` (lines 60, 64, 133, 137, 250, 553, 800, 807, 876, 887, 927, 1413)
- `sidebar.css` (line 34)
- `editor.css` (line 25)

### Primary vs Secondary Summary
| Use Case | Color | Hex | Where |
|----------|-------|-----|-------|
| **Primary action (create/submit)** | Emerald | #10b981 | Submit buttons, active tabs |
| **Hover/Active UI state** | Blue | #0d6efd | Icons, buttons, nav items |
| **Destructive actions** | Red | #dc3545 | Delete buttons, errors |
| **Success/Status** | Green | #28a745 | Auto-refresh, success states |
| **Warning** | Yellow | #ffc107 | Pin icon, change indicators |

---

## SUMMARY CHECKLIST FOR KB MOCKUP

✅ **Sidebar structure**: 3-level hierarchy (parent → section → child items)
✅ **Pin mechanism**: Bootstrap icon `\F588`, yellow (#ffc107), replaces chevron
✅ **Expand/collapse**: Chevron rotates -90deg when collapsed
✅ **Workplace sidebar**: 48px collapsed → 280px expanded
✅ **Icon buttons**: 36x36px, radius 6px, blue on active
✅ **Top bar**: 36px fixed height, #1e1e1e background
✅ **Brand font-size**: 1rem (16px) bold, gap 0.5rem between elements
✅ **Modal overlay**: rgba(0,0,0,0.4), blur(4px), spring animation
✅ **Modal dialog**: 90vw x 90vh, border-radius 12px, shadow 0 20px 60px
✅ **Modal header**: 16px vertical / 24px horizontal padding
✅ **Modal close button**: 20px, padding 4px 8px, hover bg #f1f5f9
✅ **Content header**: 50px height, bg #f8f9fa, border-bottom #e9ecef
✅ **Terminal panel**: 36px collapsed / 300px expanded
✅ **Terminal header**: 36px, #252526 bg, #ccc text, 13px font
✅ **Tree indentation**: level * 16 + 8px (8px base, 16px per level)
✅ **Tree item padding**: 6px 8px, hover bg #e9ecef
✅ **Tree chevron**: #229, size 0.7rem, rotates 90deg
✅ **Search bar**: 8px 12px padding, input 6px 32px, icon 14px left 10px
✅ **Search focus**: border #10b981, shadow 0 0 0 3px rgba(16,185,129,0.1)
✅ **Debounce**: 150ms
✅ **Primary action**: #10b981 (emerald) for submit/active
✅ **Secondary action**: #0d6efd (blue) for hover/nav

