# Color Derivation Reference

Rules for deriving a complete theme palette from minimal input.

---

## Derivation from Accent Color

When only the accent color is provided, derive the remaining colors:

```
Given: Accent = #3b82f6 (blue)

1. Primary:   Darken accent by 40%       -> #1e3a5f (dark blue)
2. Secondary: Desaturate + darken by 20% -> #64748b (slate)
3. Neutral:   Very light tint of accent  -> #e0f2fe (light blue)
4. Semantic:  Use standard palette (green/amber/red/blue)
```

For the neutral scale, use the Tailwind color scale closest to the derived colors.

---

## Default Values

| Token | Default | Description |
|-------|---------|-------------|
| Heading Font | `Inter` | Font for headings |
| Body Font | `system-ui` | Font for body text |
| Code Font | `JetBrains Mono` | Font for code |
| Border Radius | `8px` (md) | Default corner rounding |

---

## Semantic Colors (Standard)

| Token | Value | Usage |
|-------|-------|-------|
| Success | `#22c55e` | Positive states |
| Warning | `#f59e0b` | Caution states |
| Error | `#ef4444` | Negative states |
| Info | `#3b82f6` | Informational |

---

## Tailwind Scale Mapping

| Accent Color Family | Recommended Scale |
|---------------------|-------------------|
| Red/Rose/Pink | Rose or Slate |
| Orange/Amber | Orange or Stone |
| Yellow/Lime | Amber or Zinc |
| Green/Emerald/Teal | Emerald or Slate |
| Cyan/Sky | Sky or Slate |
| Blue/Indigo | Indigo or Slate |
| Violet/Purple | Violet or Slate |
| Fuchsia/Pink | Fuchsia or Slate |
| Gray/Slate/Zinc | Same family |

See [color-scales.md](color-scales.md) for full Tailwind scale values.

---

## Contrast Requirements

| Combination | Required Ratio | Check |
|-------------|---------------|-------|
| Primary on White | 4.5:1 | Body text |
| Secondary on White | 4.5:1 | Body text |
| Accent on White | 3:1 | Large text only |
| White on Accent | 4.5:1 | Button text |
