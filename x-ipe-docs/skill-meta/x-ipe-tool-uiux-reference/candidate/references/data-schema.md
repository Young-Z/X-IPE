# Data Schema — referenced-elements.json

Version 3.0 schema for the single source of truth analysis output.

**File path:** `{idea_folder}/uiux-references/page-element-references/referenced-elements.json`

---

## Full Schema

```json
{
  "version": "3.0",
  "source_url": "https://example.com",
  "timestamp": "2026-02-15T10:30:00Z",
  "areas": [
    {
      "area_id": "area-1",
      "selected_area_bounding_box": {
        "x": 100,
        "y": 200,
        "width": 800,
        "height": 600
      },
      "instruction": "User-provided instruction for this area (optional)",
      "key_elements_identified_from_screenshot": [
        {
          "element": "hero-heading",
          "purpose": "Large centered heading text",
          "examined_from_screenshot": "area-1.png"
        },
        {
          "element": "gradient-background",
          "purpose": "Dark navy-to-black gradient behind the hero section, inherited from ancestor",
          "examined_from_screenshot": "full-page.png"
        }
      ],
      "elements": [
        {
          "element_name": "hero-heading",
          "purpose_of_the_element": "Main brand heading that communicates the platform value proposition",
          "relationships_to_other_elements": [
            {
              "element": "hero-description",
              "relationship": "sibling-below",
              "mimic_tips": "to_element_itself: font-size:48px, font-weight:700, color:#fff, text-align:center, margin:0, to_relevant_elements: 20px vertical spacing above hero-description, centered in flex-column container"
            },
            {
              "element": "hero-container",
              "relationship": "contained-in",
              "mimic_tips": "to_element_itself: font-size:48px, font-weight:700, color:#fff, display:block, to_relevant_elements: contained inside hero-container, centered via flexbox align-items:center"
            }
          ],
          "element_details": {
            "tag": "h1",
            "text_content": "Build Something Amazing",
            "classes": ["hero-title", "text-center"],
            "styles": {
              "font-family": "'Inter', sans-serif",
              "font-size": "48px",
              "font-weight": "700",
              "line-height": "1.2",
              "letter-spacing": "-0.02em",
              "color": "#1a1a2e",
              "text-align": "center",
              "margin": "0 0 20px 0",
              "padding": "0",
              "display": "block",
              "position": "relative",
              "width": "100%",
              "height": "auto"
            },
            "resources": [
              {
                "type": "font",
                "src": "https://fonts.gstatic.com/s/inter/v12/abc123.woff2",
                "local_path": "resources/area-1-font-1.woff2",
                "usage": "Primary heading font"
              }
            ]
          }
        }
      ]
    }
  ],
  "static_resources": [
    {
      "type": "font",
      "src": "https://fonts.gstatic.com/s/inter/v12/abc123.woff2",
      "local_path": "resources/area-1-font-1.woff2",
      "usage": "Primary heading font"
    },
    {
      "type": "image",
      "src": "https://example.com/hero-bg.webp",
      "local_path": "resources/area-1-img-1.webp",
      "usage": "Hero section background image"
    }
  ]
}
```

---

## Field Reference

### Root Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Schema version, currently "3.0" |
| `source_url` | string | Yes | URL the reference was captured from |
| `timestamp` | string | Yes | ISO 8601 timestamp of capture |
| `areas` | array | Yes | List of analyzed areas |
| `static_resources` | array | Yes | Deduplicated list of all downloaded resources |

### Area Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `area_id` | string | Yes | Unique identifier (e.g., "area-1") |
| `selected_area_bounding_box` | object | Yes | `{x, y, width, height}` in viewport coordinates |
| `instruction` | string | No | User-provided instruction for the area |
| `key_elements_identified_from_screenshot` | array | Yes | Visual elements identified by examining screenshots before DOM discovery. Each: `{element, purpose, examined_from_screenshot}`. Used to validate and refine DOM-discovered elements. |
| `elements` | array | Yes | Enriched elements discovered within bounding box |

### Element Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `element_name` | string | Yes | Short descriptive name assigned by agent (e.g., "hero-heading") |
| `purpose_of_the_element` | string | Yes | One sentence describing visual/functional role |
| `relationships_to_other_elements` | array | Yes | Spatial/structural relationships to other elements |
| `element_details` | object | Yes | Tag, text, classes, computed styles, and resources |

### Relationship Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `element` | string | Yes | Name of the related element |
| `relationship` | string | Yes | One of: parent, child, sibling-above, sibling-below, sibling-left, sibling-right, container, contained-in |
| `mimic_tips` | string | Yes | Two-part template: "to_element_itself: {own styles: color, font, size, margin, padding, border, bg...}, to_relevant_elements: {spatial/structural relationship to the named element}" |

### Element Details Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tag` | string | Yes | HTML tag name |
| `text_content` | string | No | Text content (first 200 chars) |
| `classes` | array | No | CSS class names |
| `styles` | object | Yes | Computed CSS properties (see style fields below) |
| `resources` | array | No | Referenced static resources with local paths |

### Style Fields

All values are strings as returned by `getComputedStyle()`:

`display`, `position`, `color`, `backgroundColor`, `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `fontStyle`, `margin`, `padding`, `width`, `height`, `textAlign`, `letterSpacing`, `borderRadius`, `boxShadow`, `backgroundImage`, `opacity`, `gap`, `flexDirection`, `alignItems`, `justifyContent`

### Resource Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | One of: font, image, svg, icon, video |
| `src` | string | Yes | Original source URL |
| `local_path` | string | No | Local path after download (e.g., "resources/area-1-font-1.woff2") |
| `usage` | string | Yes | Description of how the resource is used |

---

## Notes

- This file is the **single source of truth** for analysis data — do NOT create `reference-data.json` or session files.
- The `save_uiux_reference` MCP tool also generates derivative files from this data:
  - `page-element-references/summarized-uiux-reference.md`
  - `page-element-references/resources/{area-id}-structure.html`
  - `page-element-references/resources/{area-id}-styles.css`
  - `mimic-strategy.md`
