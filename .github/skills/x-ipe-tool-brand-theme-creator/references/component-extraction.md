# Component Extraction Reference

Patterns for extracting UI component styles from different source types, with sensible defaults for when extraction is not possible.

---

## Extractable Components

| Component | Key Properties | Default When Not Extracted |
|-----------|---------------|---------------------------|
| Buttons | background, border-radius, padding, font-weight, font-size, hover style, shadow | accent bg, radius_md, 12px 24px, 600, 14px, darken hover, sm shadow |
| Cards | border, shadow, padding, border-radius, background | scale-200 border, sm shadow, 24px, 12px, white bg |
| Form Inputs | border, border-radius, padding, focus ring, placeholder color | scale-200 border, radius_md, 12px 16px, accent ring, scale-400 |
| Links | color, hover color, underline, transition | accent, accent-dark, none/hover, 150ms |
| Badges | background, padding, border-radius, font-size, font-weight | accent-light bg, 2px 8px, full, 12px, 500 |
| Navigation | height, background, padding, item spacing, active indicator | 64px, white/primary, 0 16px, 24px, accent underline |

---

## Extraction by Source Type

### Web Link Extraction

When fetching a website, look for these component patterns in the page CSS and HTML:

**Buttons:**
```
CSS selectors: button, [class*="btn"], [class*="button"], [role="button"], a[class*="cta"]
Properties: background-color, border-radius, padding, font-weight, font-size, box-shadow
Hover: :hover pseudo-class styles
States: also check for secondary/outline button variants
```

**Cards:**
```
CSS selectors: [class*="card"], article, [class*="panel"], [class*="tile"]
Properties: border, box-shadow, padding, border-radius, background
Look for: elevation patterns (shadow depth indicates card hierarchy)
```

**Form Inputs:**
```
CSS selectors: input[type="text"], textarea, select, [class*="input"], [class*="field"]
Properties: border, border-radius, padding, outline/box-shadow on focus
Focus: :focus or :focus-visible pseudo-class styles
```

**Links:**
```
CSS selectors: a, [class*="link"]
Properties: color, text-decoration, transition
Hover: :hover color and underline changes
```

**Badges/Tags:**
```
CSS selectors: [class*="badge"], [class*="tag"], [class*="chip"], [class*="label"]
Properties: background-color, padding, border-radius, font-size, font-weight
```

**Navigation:**
```
CSS selectors: nav, header, [class*="navbar"], [class*="nav"]
Properties: height, background-color, padding
Items: gap/margin between nav items, active state indicator
```

### Image Input Extraction

When analyzing brand images or design mockups via vision:

1. **Identify visible UI components** in screenshots or mockups
2. **Estimate properties** from visual appearance:
   - Button shape: square corners → 0-2px, slightly rounded → 4-8px, rounded → 12-16px, pill → 9999px
   - Card elevation: flat → no shadow, subtle → sm shadow, elevated → md shadow, floating → lg shadow
   - Input treatment: minimal → border only, outlined → colored border, filled → gray background
   - Spacing density: compact → 8px padding, standard → 12-16px, spacious → 20-24px
3. **Map to CSS values** using the estimation table above

### Text Description Extraction

Map descriptive keywords to component styles:

| Keyword | Button Style | Card Style | Input Style | Overall |
|---------|-------------|------------|-------------|---------|
| Modern | Flat, no shadow, medium radius | Borderless, subtle shadow | Clean borders, rounded | Clean lines |
| Playful | Large radius or pill, bold colors | Large radius, colorful borders | Large radius, accent borders | Generous spacing |
| Corporate | Square or small radius, subtle | Bordered, small radius | Standard, square | Compact |
| Minimal | Ghost or outline, no shadow | No border, no shadow | Underline only | Lots of whitespace |
| Bold | High contrast, large, shadow | Strong shadow, thick borders | Thick borders | Dense, impactful |
| Luxury | Small radius, subtle shadow, serif text | Thin borders, elegant shadow | Thin borders, refined | Refined spacing |
| Rounded | Pill or large radius | Large radius (16px+) | Large radius | Soft edges |
| Flat | No shadows, solid colors | No shadows, solid backgrounds | No shadows | 2D aesthetic |

---

## Merge Logic

When both extracted and default values exist:

1. **Extracted values always take precedence** over defaults
2. For partially extracted components (e.g., button background extracted but not padding), fill remaining properties from defaults
3. Record which values were extracted vs derived in the output metadata

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Blocking on failed extraction | Theme generation fails unnecessarily | Fall back to defaults, note in metadata |
| Extracting complex interactions | JavaScript behavior can't be represented in tokens | Only extract visual/CSS properties |
| Copying exact pixel values from screenshots | Inaccurate, doesn't scale | Map to nearest standard token value |
| Ignoring component states | Hover/focus states are essential for usability | Always extract or derive hover + focus |
