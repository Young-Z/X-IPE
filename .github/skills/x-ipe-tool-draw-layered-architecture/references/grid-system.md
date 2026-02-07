# Grid System Rules

The 12-column grid system ensures predictable, mathematically aligned layouts.

## Hierarchy Overview

| Level | DSL Property | CSS Implementation | Purpose |
|-------|--------------|-------------------|---------|
| Document | `grid 12 x N` | `grid-template-columns: repeat(12, 1fr)` | Canvas size |
| Layer | `rows N` | `grid-row: span N; grid-column: 1 / -1` | Vertical space allocation |
| Module | `cols N` | `grid-column: span N` | Horizontal space within layer |
| Component | `cols N, rows N` | `grid-column: span N; grid-row: span N` | Position in module grid |

---

## Rule 1: Document Grid Defines Canvas

The document grid establishes the overall diagram dimensions.

**DSL**: `grid 12 x 6`
- First number (12): Always 12 columns (Bootstrap convention)
- Second number (6): Total rows, should equal sum of all layer `rows` values

**CSS**:
```css
.diagram-content {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    grid-template-rows: repeat(6, auto);
    gap: 16px;
}
```

---

## Rule 2: Layers Occupy Full Width

Layers always span all 12 columns and use `rows` to control vertical space.

**DSL**:
```
layer "Presentation" {
    rows 2
}
```

**CSS**:
```css
.layer {
    grid-column: 1 / -1;  /* Full width */
    grid-row: span 2;     /* From 'rows 2' */
    display: grid;
    grid-template-columns: repeat(12, 1fr);  /* Inner grid */
    gap: 12px;
}
```

---

## Rule 3: Module Cols Must Sum to 12

All modules within a layer must have `cols` values that sum to exactly 12.

**Valid Examples**:
- `cols 12` (single full-width module)
- `cols 6 + cols 6` (two equal modules)
- `cols 4 + cols 4 + cols 4` (three equal modules)
- `cols 4 + cols 8` (one narrow, one wide)
- `cols 3 + cols 3 + cols 3 + cols 3` (four equal modules)

**Invalid**: `cols 4 + cols 4` = 8 (missing 4 columns)

**CSS**:
```css
.module-narrow { grid-column: span 4; }
.module-wide { grid-column: span 8; }
```

---

## Rule 4: Module Internal Grid

Each module defines its own grid for component layout using `grid C x R`.

**DSL**:
```
module "Services" {
    cols 8
    grid 2 x 3    /* 2 columns, 3 rows */
    align center center
    gap 8px
}
```

**CSS**:
```css
.module-services {
    grid-column: span 8;
}

.module-services .module-content {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, 1fr);
    justify-items: center;
    align-items: center;
    gap: 8px;
}
```

---

## Rule 5: Component Positioning

Components use `cols` and `rows` to span cells within the module's internal grid.

**Default**: `cols 1, rows 1` (single cell)

**Spanning Examples**:
- `cols 2, rows 1`: Spans 2 columns horizontally
- `cols 1, rows 2`: Spans 2 rows vertically
- `cols 2, rows 2`: Spans a 2×2 block

**CSS**:
```css
.component { grid-column: span 1; grid-row: span 1; }
.component.span-cols-2 { grid-column: span 2; }
.component.span-rows-2 { grid-row: span 2; }
```

---

## Rule 6: Cross-Layer Vertical Alignment

Modules with matching column boundaries across layers automatically align vertically.

**Example**: 
- Layer 1: Module A (`cols 4`) + Module B (`cols 8`)
- Layer 2: Module C (`cols 4`) + Module D (`cols 4`) + Module E (`cols 4`)

Result: Module A aligns vertically with Module C. The boundary between A and B aligns with the boundary between C and D.

**Key insight**: Use consistent `cols` values across layers to create visual coherence.

---

## Rule 7: Fill Before Gap

The grid system automatically fills available space. Modules expand to their allocated columns without leaving gaps.

- No explicit `justify-content` needed
- No manual width calculations
- The `cols` property handles proportional sizing

---

## Spacing Defaults

| Element | Gap | Customizable |
|---------|-----|--------------|
| Between layers | 16px | No (fixed) |
| Between modules | 12px | No (fixed) |
| Between components | 8px | Yes (`gap` property) |

---

## Common Patterns

### Equal Distribution (3 modules)
```
module "A" { cols 4 }
module "B" { cols 4 }
module "C" { cols 4 }
```

### Sidebar + Main Content
```
module "Sidebar" { cols 3 }
module "Main" { cols 9 }
```

### Two-Column with Detail
```
module "Left" { cols 4 }
module "Center" { cols 4 }
module "Right" { cols 4 }
```

### Vertical Stack in Module
```
module "Stack" {
    cols 4
    grid 1 x 3   /* 1 column, 3 rows = vertical stack */
}
```

### Wide Component Spanning
```
module "Grid" {
    cols 8
    grid 2 x 3
    component "A" { cols 1, rows 1 }
    component "B" { cols 1, rows 1 }
    component "C" { cols 1, rows 1 }
    component "D" { cols 1, rows 1 }
    component "Footer" { cols 2, rows 1 }  /* Spans full width */
}
```
