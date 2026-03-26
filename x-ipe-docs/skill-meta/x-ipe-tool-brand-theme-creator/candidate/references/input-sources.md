# Input Sources Reference

Details on how to extract brand information from each supported input type.

---

## 1. Web Link Input

Extract colors, styles, and UI component patterns from an existing website or brand page.

**Capabilities:**
- Use `web_fetch` tool or similar MCP capability to retrieve page content
- Extract primary brand colors from CSS, meta tags, or visible elements
- Identify font families from stylesheets
- Detect accent colors from buttons, links, and interactive elements
- Parse Open Graph or brand-specific meta tags
- Extract UI component patterns from CSS rules (buttons, cards, inputs, links, badges, navigation)

**Color Extraction Steps:**
1. Fetch the web page using `web_fetch` tool
2. Look for:
   - CSS variables in `:root` or body
   - `<meta name="theme-color" content="...">` tags
   - Primary brand colors in headers, navigation, CTAs
   - Font-family declarations in CSS
   - Button/link colors for accent extraction
3. Build color palette from extracted values

**Component Extraction Steps:**
1. After fetching the page, scan CSS/HTML for component patterns:
   - **Buttons**: Look for `button`, `.btn`, `[class*="button"]` selectors → extract background, border-radius, padding, font-weight, box-shadow, hover styles
   - **Cards**: Look for `.card`, `article`, `[class*="panel"]` selectors → extract border, box-shadow, padding, border-radius
   - **Form Inputs**: Look for `input`, `textarea`, `select`, `.input` selectors → extract border, border-radius, padding, focus ring
   - **Links**: Look for `a` styles → extract color, hover color, text-decoration, transition
   - **Badges**: Look for `.badge`, `.tag`, `.chip` selectors → extract background, padding, border-radius, font-size
   - **Navigation**: Look for `nav`, `header`, `.navbar` selectors → extract height, background, padding
2. For each component found, extract the key visual properties
3. Record which components were successfully extracted

**Common Element Mapping:**
```
Header/Nav background  ->  Primary color candidate
Button backgrounds     ->  Accent color candidate
Body text              ->  Secondary color candidate
Page background        ->  Neutral color candidate
Button border-radius   ->  Border radius candidate
Card box-shadow        ->  Shadow style candidate
```

**CSS Patterns to Search:**
```css
:root {
  --brand-primary: #...;
  --brand-accent: #...;
}
```

**Meta Tag Patterns:**
```html
<meta name="theme-color" content="#0ea5e9">
<meta name="msapplication-TileColor" content="#0ea5e9">
```

---

## 2. Image Input

Extract colors and component patterns from brand assets, logos, or design mockups.

**Capabilities:**
- Analyze images to extract dominant colors
- Use Claude's vision capabilities to identify:
  - Primary brand colors
  - Accent/highlight colors
  - Background colors
  - Color relationships and contrast
- Suggest complementary colors for full palette
- Identify visible UI components in mockups/screenshots and estimate their styles

**Color Extraction Steps:**
1. Accept image file (logo, brand guide, screenshot)
2. Analyze using vision capabilities to identify:
   - Dominant colors (by area coverage)
   - Accent colors (small but prominent)
   - Text colors
   - Background colors
3. Extract hex values and map to theme tokens

**Component Extraction Steps (for screenshots/mockups):**
1. If image contains UI mockups or screenshots:
   - Identify visible buttons → estimate border-radius (square/rounded/pill), padding density, shadow presence
   - Identify cards → estimate border presence, shadow depth, corner rounding
   - Identify form fields → estimate border style, corner rounding
   - Identify navigation bars → estimate height, layout style
2. Map visual observations to nearest standard token values:
   - Square corners → 0-2px, slightly rounded → 4-8px, rounded → 12-16px, pill → 9999px
   - No shadow → none, subtle → sm, moderate → md, prominent → lg
   - Compact padding → 8px, standard → 12-16px, spacious → 20-24px

---

## 3. Text Description Input

Generate colors and component styles from verbal brand descriptions.

**Capabilities:**
- Interpret color descriptions ("ocean blue", "forest green")
- Map adjectives to design characteristics
- Suggest typography based on brand personality
- Map style keywords to component patterns

**Interpretation Guide:**

| Description | Color Direction | Typography | Component Style |
|-------------|-----------------|------------|-----------------|
| Professional, Corporate | Dark blues/grays, subtle accents | Inter, SF Pro | Square corners, subtle shadows, compact |
| Creative, Playful | Vibrant, warm accents | Poppins, Quicksand | Large radius, bold colors, spacious |
| Luxury, Premium | Deep colors, gold/bronze accents | Playfair Display, Cormorant | Small radius, elegant shadows, refined |
| Tech, Modern | Cool blues/purples, clean lines | Space Grotesk, DM Sans | Medium radius, flat design, clean |
| Natural, Organic | Greens, earth tones | Lora, Source Serif | Soft radius, natural shadows, relaxed |
| Minimalist | Neutral grays, single accent | system-ui, Helvetica | No shadows, thin borders, spacious |

**Keyword Mapping:**
- "Professional" - Darker, more saturated primary; square buttons, compact layout
- "Playful" - Brighter accents, larger radius; pill buttons, generous padding
- "Minimalist" - Subtle colors, smaller radius; ghost/outline buttons, lots of whitespace
- "Bold" - High contrast, vibrant accents; large buttons with shadows, thick card borders
- "Rounded" - Pill-shaped buttons, large card radius
- "Flat" - No shadows anywhere, solid backgrounds
- "Elegant" - Thin borders, subtle shadows, serif typography
