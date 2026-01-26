# Design System: Default Theme

A clean, neutral design system that serves as the foundation for X-IPE mockups.
This theme provides a professional baseline suitable for any project type.

---

## Core Tokens

### Color Palette

#### Primary Colors
```
Primary:     #0f172a  (Slate 900 - Main text, headings)
Secondary:   #475569  (Slate 600 - Secondary text)
Accent:      #10b981  (Emerald 500 - CTAs, highlights)
Neutral:     #e2e8f0  (Slate 200 - Backgrounds, borders)
```

#### Neutral Scale (Slate)
```
slate-50:   #f8fafc   (Lightest background)
slate-100:  #f1f5f9   (Card backgrounds)
slate-200:  #e2e8f0   (Borders, dividers)
slate-300:  #cbd5e1   (Disabled states)
slate-400:  #94a3b8   (Placeholder text)
slate-500:  #64748b   (Muted text)
slate-600:  #475569   (Secondary text)
slate-700:  #334155   (Body text)
slate-800:  #1e293b   (Headings)
slate-900:  #0f172a   (Primary text)
slate-950:  #020617   (Darkest)
```

#### Semantic Colors
```
Success:    #22c55e   (Green 500 - Confirmations)
Warning:    #f59e0b   (Amber 500 - Warnings)
Error:      #ef4444   (Red 500 - Errors)
Info:       #3b82f6   (Blue 500 - Information)
```

#### Accent Variants
```
accent-light:   #d1fae5   (Emerald 100)
accent-DEFAULT: #10b981   (Emerald 500)
accent-dark:    #059669   (Emerald 600)
```

---

### Typography

#### Font Families
```css
--font-heading: 'Inter', system-ui, sans-serif;
--font-body: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
```

#### Font Sizes (rem scale)
```
text-xs:    0.75rem   (12px)  - Captions, labels
text-sm:    0.875rem  (14px)  - Secondary text
text-base:  1rem      (16px)  - Body text
text-lg:    1.125rem  (18px)  - Lead text
text-xl:    1.25rem   (20px)  - H4
text-2xl:   1.5rem    (24px)  - H3
text-3xl:   1.875rem  (30px)  - H2
text-4xl:   2.25rem   (36px)  - H1
text-5xl:   3rem      (48px)  - Hero
```

#### Font Weights
```
font-normal:    400   (Body text)
font-medium:    500   (Emphasis)
font-semibold:  600   (Headings)
font-bold:      700   (Strong emphasis)
```

#### Line Heights
```
leading-tight:  1.25  (Headings)
leading-snug:   1.375 (Compact text)
leading-normal: 1.5   (Body text)
leading-relaxed: 1.625 (Readable prose)
```

---

### Spacing

#### Base Unit
4px base unit with 8-step geometric scale.

#### Spacing Scale
```
space-1:   4px    (0.25rem)  - Tight gaps
space-2:   8px    (0.5rem)   - Small gaps
space-3:   12px   (0.75rem)  - Compact padding
space-4:   16px   (1rem)     - Standard padding
space-5:   20px   (1.25rem)  - Medium gaps
space-6:   24px   (1.5rem)   - Section padding
space-8:   32px   (2rem)     - Large gaps
space-10:  40px   (2.5rem)   - Extra large
space-12:  48px   (3rem)     - Section margins
space-16:  64px   (4rem)     - Page margins
```

---

### Border Radius

```
rounded-sm:   4px    (Subtle rounding)
rounded-md:   8px    (Standard rounding)
rounded-lg:   12px   (Card corners)
rounded-xl:   16px   (Large elements)
rounded-2xl:  24px   (Modals, panels)
rounded-full: 9999px (Pills, avatars)
```

---

### Shadows

```css
/* Small - Subtle elevation */
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);

/* Medium - Cards, dropdowns */
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1),
             0 2px 4px -2px rgb(0 0 0 / 0.1);

/* Large - Modals, popovers */
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1),
             0 4px 6px -4px rgb(0 0 0 / 0.1);

/* XL - Floating elements */
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1),
             0 8px 10px -6px rgb(0 0 0 / 0.1);
```

---

## Component Specs

### Buttons

#### Primary Button
```css
.btn-primary {
  background: #10b981;
  color: #ffffff;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}
.btn-primary:hover {
  background: #059669;
}
```

#### Secondary Button
```css
.btn-secondary {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #e2e8f0;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
}
.btn-secondary:hover {
  background: #e2e8f0;
}
```

### Cards

```css
.card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}
.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 8px;
}
.card-body {
  font-size: 14px;
  color: #475569;
  line-height: 1.5;
}
```

### Form Inputs

```css
.input {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  color: #0f172a;
  width: 100%;
}
.input:focus {
  border-color: #10b981;
  outline: none;
  box-shadow: 0 0 0 3px rgb(16 185 129 / 0.15);
}
.input::placeholder {
  color: #94a3b8;
}
```

---

## Usage Guidelines

### Accessibility

- Maintain minimum 4.5:1 contrast ratio for body text
- Use 3:1 contrast for large text (18px+ or 14px bold)
- Primary (#0f172a) on white: 15.98:1 ✓
- Secondary (#475569) on white: 5.91:1 ✓
- Accent (#10b981) on white: 3.03:1 (use for large text/graphics only)

### Best Practices

1. **Color Usage**
   - Use primary for main headings and important text
   - Use secondary for body text and descriptions
   - Reserve accent for CTAs, links, and interactive elements
   - Use semantic colors consistently (green=success, red=error)

2. **Typography**
   - Limit to 2-3 font sizes per component
   - Use Inter for headings, system fonts for body (faster loading)
   - Maintain readable line lengths (45-75 characters)

3. **Spacing**
   - Use 8px increments for consistency
   - Apply consistent padding within components
   - Increase spacing for visual hierarchy between sections

4. **Components**
   - Round corners consistently (8px for buttons, 12px for cards)
   - Use subtle shadows for elevation, not heavy borders
   - Ensure interactive elements have clear hover/focus states

---

## CSS Variables

```css
:root {
  /* Colors */
  --color-primary: #0f172a;
  --color-secondary: #475569;
  --color-accent: #10b981;
  --color-neutral: #e2e8f0;
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
  
  /* Typography */
  --font-heading: 'Inter', system-ui, sans-serif;
  --font-body: system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Spacing */
  --space-unit: 4px;
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}
```
