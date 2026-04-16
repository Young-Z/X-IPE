# User Manual — Web App Mixin

> Additional sections and extraction patterns for web applications.
> The `provide_framework` operation merges these into the base playbook when `app_type: web`.

---

## Additional Sections

### A. Authentication & Login

**Insert after Section 3 — Getting Started.**

- **Login Methods** — Email/password, OAuth providers, SSO
- **Account Creation** — Registration flow and verification
- **Session Management** — Timeout behavior, remember-me, multi-device
- **Password Recovery** — Reset flow and security questions

**Knowledge request patterns (for request_knowledge):**
- "Extract authentication methods from auth/, login pages, OAuth config, passport strategies"
- "Find registration flow from signup routes, registration forms, email verification"
- "Identify session/token mechanism from JWT config, session middleware, cookie settings"
- "Extract password reset flow from forgot-password routes, email templates"

### B. Navigation & UI Structure

**Insert into Section 4 — Core Features as first subsection.**

- **Main Navigation** — Primary menu structure and page hierarchy
- **Dashboard / Home** — What the user sees after login
- **Search & Filtering** — How to find content within the app
- **Responsive Behavior** — Mobile vs desktop layout differences

**Knowledge request patterns:**
- "Extract navigation structure from nav components, router config, sitemap"
- "Describe main dashboard from dashboard components, home page layout"
- "Find search functionality from search components, search API endpoints"
- "Check responsive behavior from media queries, responsive breakpoints"

### C. Browser Requirements

**Insert into Section 2 — Installation & Setup.**

- **Supported Browsers** — Chrome, Firefox, Safari, Edge with minimum versions
- **Required Browser Features** — JavaScript, cookies, WebSocket, etc.
- **Browser Extensions** — Any required or recommended extensions

**Knowledge request patterns:**
- "Find supported browsers from browserslist config, .browserslistrc, compatibility notes"
- "Identify browser-specific requirements from polyfills, feature detection"
- "Check for required browser extensions from extension references in docs"

### D. API Endpoints (User-Facing)

**Insert into Section 8 — FAQ & Reference.**

- **Public API Overview** — Base URL, versioning, authentication
- **Common Endpoints** — Table of frequently used API calls
- **Rate Limits** — Request limits and throttling behavior

**Knowledge request patterns:**
- "Find user-facing API from /api/ routes, OpenAPI spec, swagger.json"
- "List main API endpoints from route definitions, controller files"
- "Extract rate limits from rate limiter middleware, throttle config"

---

## Section Overlay Patterns

These augment the base collection template when `app_type: web`:

### For Section 2 (Installation & Setup)
- "Find application URL from deployed URL, homepage in package.json"
- "Check for self-hosted option from deployment docs, docker-compose"

### For Section 4 (Core Features)
- "Find screenshots or visual guides from docs/images/, screenshots/"
- "Identify UI frameworks from React/Vue/Angular components, CSS framework"

### For Section 7 (Troubleshooting)
- "Document how to clear browser cache/cookies for this app"
- "List common CORS or network errors"
- "Identify browser console errors to look for"
