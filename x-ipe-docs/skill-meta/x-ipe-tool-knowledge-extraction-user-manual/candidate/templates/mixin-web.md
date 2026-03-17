# User Manual — Web App Mixin

> Additional sections and extraction prompts for web applications.
> Merge these into the base playbook and collection templates when `app_type: web`.

---

## Additional Sections

### A. Authentication & Login

**Playbook addition** (insert after Section 3 — Getting Started):

- **Login Methods** — Email/password, OAuth providers, SSO
- **Account Creation** — Registration flow and verification
- **Session Management** — Timeout behavior, remember-me, multi-device
- **Password Recovery** — Reset flow and security questions

<!-- EXTRACTION PROMPTS:
- What authentication methods are supported? (look for auth/, login pages, OAuth config, passport strategies)
- How does user registration work? (look for signup routes, registration forms, email verification)
- What session/token mechanism is used? (look for JWT config, session middleware, cookie settings)
- How does password reset work? (look for forgot-password routes, email templates)
-->

### B. Navigation & UI Structure

**Playbook addition** (insert into Section 4 — Core Features as first subsection):

- **Main Navigation** — Primary menu structure and page hierarchy
- **Dashboard / Home** — What the user sees after login
- **Search & Filtering** — How to find content within the app
- **Responsive Behavior** — Mobile vs desktop layout differences

<!-- EXTRACTION PROMPTS:
- What is the main navigation structure? (look for nav components, router config, sitemap)
- What does the main dashboard show? (look for dashboard components, home page layout)
- Is there search functionality? (look for search components, search API endpoints)
- Is the UI responsive? (look for media queries, responsive breakpoints, mobile components)
-->

### C. Browser Requirements

**Playbook addition** (insert into Section 2 — Installation & Setup):

- **Supported Browsers** — Chrome, Firefox, Safari, Edge with minimum versions
- **Required Browser Features** — JavaScript, cookies, WebSocket, etc.
- **Browser Extensions** — Any required or recommended extensions

<!-- EXTRACTION PROMPTS:
- What browsers are supported? (look for browserslist config, .browserslistrc, compatibility notes)
- Are there browser-specific requirements? (look for polyfills, feature detection, browser warnings)
- Are browser extensions needed? (look for extension references in docs)
-->

### D. API Endpoints (User-Facing)

**Playbook addition** (insert into Section 7 — FAQ & Reference):

- **Public API Overview** — Base URL, versioning, authentication
- **Common Endpoints** — Table of frequently used API calls
- **Rate Limits** — Request limits and throttling behavior

<!-- EXTRACTION PROMPTS:
- Is there a user-facing API? (look for /api/ routes, OpenAPI spec, swagger.json, API docs)
- What are the main API endpoints? (look for route definitions, controller files)
- Are there rate limits? (look for rate limiter middleware, throttle config)
-->

---

## Section Overlay Prompts

These prompts augment the base collection template when `app_type: web`:

### For Section 2 (Installation & Setup)
<!-- ADDITIONAL PROMPTS:
- What is the application URL? (look for deployed URL, homepage in package.json)
- Is there a self-hosted option? (look for deployment docs, docker-compose for self-hosting)
-->

### For Section 4 (Core Features)
<!-- ADDITIONAL PROMPTS:
- Are there screenshots or visual guides? (look for docs/images/, screenshots/, .png/.gif references)
- What UI frameworks are used? (look for React/Vue/Angular components, CSS framework)
-->

### For Section 6 (Troubleshooting)
<!-- ADDITIONAL PROMPTS:
- How to clear browser cache/cookies for this app?
- Common CORS or network errors?
- Browser console errors to look for?
-->
