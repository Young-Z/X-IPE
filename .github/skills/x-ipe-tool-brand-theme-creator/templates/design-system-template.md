# Design System: {Theme Name}

{One-line description - e.g., "A vibrant ocean-inspired theme with calming blue tones."}

---

## Core Tokens

### Color Palette

#### Primary Colors
```
Primary:     {primary_hex}  ({primary_name} - Main text, headings)
Secondary:   {secondary_hex}  ({secondary_name} - Secondary text)
Accent:      {accent_hex}  ({accent_name} - CTAs, highlights)
Neutral:     {neutral_hex}  ({neutral_name} - Backgrounds, borders)
```

#### Neutral Scale ({scale_name})
```
{scale}-50:   {scale_50}   (Lightest background)
{scale}-100:  {scale_100}  (Card backgrounds)
{scale}-200:  {scale_200}  (Borders, dividers)
{scale}-300:  {scale_300}  (Disabled states)
{scale}-400:  {scale_400}  (Placeholder text)
{scale}-500:  {scale_500}  (Muted text)
{scale}-600:  {scale_600}  (Secondary text)
{scale}-700:  {scale_700}  (Body text)
{scale}-800:  {scale_800}  (Headings)
{scale}-900:  {scale_900}  (Primary text)
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
accent-light:   {accent_light}   ({accent_name} 100)
accent-DEFAULT: {accent_hex}     ({accent_name} 500)
accent-dark:    {accent_dark}    ({accent_name} 600)
```

---

### Typography

#### Font Families
```css
--font-heading: '{heading_font}', system-ui, sans-serif;
--font-body: {body_font}, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: '{mono_font}', 'Fira Code', Consolas, monospace;
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
rounded-md:   {radius_md}    (Standard rounding)
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
  background: {accent_hex};
  color: #ffffff;
  padding: 12px 24px;
  border-radius: {radius_md};
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}
.btn-primary:hover {
  background: {accent_dark};
}
```

#### Secondary Button
```css
.btn-secondary {
  background: {scale_100};
  color: {scale_700};
  border: 1px solid {scale_200};
  padding: 12px 24px;
  border-radius: {radius_md};
  font-weight: 500;
}
.btn-secondary:hover {
  background: {scale_200};
}
```

### Cards

```css
.card {
  background: #ffffff;
  border: 1px solid {scale_200};
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}
.card-title {
  font-size: 18px;
  font-weight: 600;
  color: {primary_hex};
  margin-bottom: 8px;
}
.card-body {
  font-size: 14px;
  color: {secondary_hex};
  line-height: 1.5;
}
```

### Form Inputs

```css
.input {
  background: #ffffff;
  border: 1px solid {scale_200};
  border-radius: {radius_md};
  padding: 12px 16px;
  font-size: 14px;
  color: {primary_hex};
  width: 100%;
}
.input:focus {
  border-color: {accent_hex};
  outline: none;
  box-shadow: 0 0 0 3px {accent_hex}26;
}
.input::placeholder {
  color: {scale_400};
}
```

---

## Usage Guidelines

### Accessibility

- Maintain minimum 4.5:1 contrast ratio for body text
- Use 3:1 contrast for large text (18px+ or 14px bold)
- Primary on white: Check contrast
- Accent on white: Use for large text/graphics only if <4.5:1

### Best Practices

1. **Color Usage**
   - Use primary for main headings and important text
   - Use secondary for body text and descriptions
   - Reserve accent for CTAs, links, and interactive elements
   - Use semantic colors consistently

2. **Typography**
   - Limit to 2-3 font sizes per component
   - Maintain readable line lengths (45-75 characters)

3. **Spacing**
   - Use 8px increments for consistency
   - Apply consistent padding within components

---

## CSS Variables

```css
:root {
  /* Colors */
  --color-primary: {primary_hex};
  --color-secondary: {secondary_hex};
  --color-accent: {accent_hex};
  --color-neutral: {neutral_hex};
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
  
  /* Typography */
  --font-heading: '{heading_font}', system-ui, sans-serif;
  --font-body: {body_font}, -apple-system, sans-serif;
  --font-mono: '{mono_font}', monospace;
  
  /* Spacing */
  --space-unit: 4px;
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: {radius_md};
  --radius-lg: 12px;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}
```
