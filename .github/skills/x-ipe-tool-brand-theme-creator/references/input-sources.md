# Input Sources Reference

Details on how to extract brand information from each supported input type.

---

## 1. Web Link Input

Extract colors and styles from an existing website or brand page.

**Capabilities:**
- Use `web_fetch` tool or similar MCP capability to retrieve page content
- Extract primary brand colors from CSS, meta tags, or visible elements
- Identify font families from stylesheets
- Detect accent colors from buttons, links, and interactive elements
- Parse Open Graph or brand-specific meta tags

**Extraction Steps:**
1. Fetch the web page using `web_fetch` tool
2. Look for:
   - CSS variables in `:root` or body
   - `<meta name="theme-color" content="...">` tags
   - Primary brand colors in headers, navigation, CTAs
   - Font-family declarations in CSS
   - Button/link colors for accent extraction
3. Build color palette from extracted values

**Common Element Mapping:**
```
Header/Nav background  ->  Primary color candidate
Button backgrounds     ->  Accent color candidate
Body text              ->  Secondary color candidate
Page background        ->  Neutral color candidate
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

Extract colors from brand assets, logos, or design mockups.

**Capabilities:**
- Analyze images to extract dominant colors
- Use Claude's vision capabilities to identify:
  - Primary brand colors
  - Accent/highlight colors
  - Background colors
  - Color relationships and contrast
- Suggest complementary colors for full palette

**Extraction Steps:**
1. Accept image file (logo, brand guide, screenshot)
2. Analyze using vision capabilities to identify:
   - Dominant colors (by area coverage)
   - Accent colors (small but prominent)
   - Text colors
   - Background colors
3. Extract hex values and map to theme tokens

---

## 3. Text Description Input

Generate colors from verbal brand descriptions.

**Capabilities:**
- Interpret color descriptions ("ocean blue", "forest green")
- Map adjectives to design characteristics
- Suggest typography based on brand personality

**Interpretation Guide:**

| Description | Color Direction | Typography |
|-------------|-----------------|------------|
| Professional, Corporate | Dark blues/grays, subtle accents | Inter, SF Pro |
| Creative, Playful | Vibrant, warm accents | Poppins, Quicksand |
| Luxury, Premium | Deep colors, gold/bronze accents | Playfair Display, Cormorant |
| Tech, Modern | Cool blues/purples, clean lines | Space Grotesk, DM Sans |
| Natural, Organic | Greens, earth tones | Lora, Source Serif |
| Minimalist | Neutral grays, single accent | system-ui, Helvetica |

**Keyword Mapping:**
- "Professional" - Darker, more saturated primary
- "Playful" - Brighter accents, larger radius
- "Minimalist" - Subtle colors, smaller radius
- "Bold" - High contrast, vibrant accents
