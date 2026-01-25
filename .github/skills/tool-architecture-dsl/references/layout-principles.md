# Layout Principles Reference

Detailed layout principles for Architecture DSL v2 (Grid-Based).

## Core Design Philosophy

### The Grid Mental Model

Think of the diagram as a **spreadsheet**:

```
Document: grid 12 x 6 (12 columns, 6 rows)

     Col1  Col2  Col3  Col4  Col5  Col6  Col7  Col8  Col9  Col10 Col11 Col12
    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
Row1│                 Layer 1 (rows 2)                                      │
Row2│  Module A (cols 4)    │        Module B (cols 8)                      │
    ├─────┴─────┴─────┴─────┼─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┤
Row3│                 Layer 2 (rows 2)                                      │
Row4│  Module C (cols 4)    │  Module D (cols 4)    │  Module E (cols 4)    │
    └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

**Key insight**: `cols` values always sum to 12 within a row.

---

## Rectangle Hierarchy Strategy

**Every container at every level should form a perfect rectangle.**

```
┌─────────────────────────────────────────────────────────────┐
│ DIAGRAM = Rectangle (grid 12 x 6)                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ LAYER = Rectangle (rows 2)                             │  │
│  │  ┌─────────────────┐  ┌─────────────────────────────┐ │  │
│  │  │ MODULE (cols 4) │  │ MODULE (cols 8)             │ │  │
│  │  │ grid 1x3        │  │ grid 2x3                    │ │  │
│  │  │ ┌─────┐         │  │ ┌─────┐ ┌─────┐            │ │  │
│  │  │ │COMP │         │  │ │COMP │ │COMP │            │ │  │
│  │  │ └─────┘         │  │ └─────┘ └─────┘            │ │  │
│  │  └─────────────────┘  └─────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Module View Layout Principles

### P1: Layer Width (Automatic)

All layers automatically span full width via document grid.

### P2: Horizontal vs Vertical Layout

| Relationship | Layout | DSL |
|--------------|--------|-----|
| Equal importance | Horizontal | Modules with `cols N` side-by-side |
| Strong dependency | Vertical | Use `grid 1 x N` for vertical stack |

### P3: Cols Sum to 12

```architecture-dsl
layer "Business" {
  rows 2
  ' Sum: 4 + 4 + 4 = 12 (full width)
  module "Orders" { cols 4 }
  module "Inventory" { cols 4 }
  module "Customers" { cols 4 }
}
```

### P4: Nested Grid for Components

```architecture-dsl
module "Frontend JS" {
  cols 8
  rows 2
  grid 2 x 3   ' 2 columns × 3 rows
  align center center
  gap 8px
  
  component "A" { cols 1, rows 1 }
  component "B" { cols 1, rows 1 }
  component "Wide" { cols 2, rows 1 }  ' Spans 2 columns
}
```

### P5: Default Sizes

| Element | Default |
|---------|---------|
| Component | `cols 1, rows 1` |
| Module | Equal share of layer |
| Layer | Full width, specified `rows` |

### P6: Cross-Layer Alignment

Use consistent `cols` values across layers:

```
Layer 1: cols 4 + 8 = 12
         ↑ boundary
Layer 2: cols 4 + 4 + 4 = 12
         ↑ aligns!
```

### P7: Text Wrapping

- 1 line: Single line, centered
- 2 lines: Wrap, centered
- 3+ lines: Truncate with ellipsis

### P8: Fill Before Empty

| Priority | Approach |
|----------|----------|
| 1st | Add real component |
| 2nd | Span to fill |
| 3rd | Use `align center center` |
| Last | Leave empty |

---

## Layer Color Suggestions

| Layer | Background | Border |
|-------|------------|--------|
| Presentation | `#fce7f3` | `#ec4899` |
| Service | `#fef3c7` | `#f97316` |
| Business | `#dbeafe` | `#3b82f6` |
| Data | `#dcfce7` | `#22c55e` |
