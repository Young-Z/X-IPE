# UIUX Reference Summary

**Source:** https://github.com
**Date:** 2026-02-15
**Areas:** 1

## Area 1: Hero Section
- **Selector:** `section.lp-IntroHero-hero`
- **Bounding Box:** 972×326px

### Colors
| Role | Hex | Usage |
|------|-----|-------|
| Background | `#000240` → `#0d1117` | Section background gradient |
| Text Primary | `#ffffff` | Heading and body text |
| Primary CTA | `#1a7f37` | Sign up button |
| Secondary CTA BG | `rgba(31,35,40,0.4)` | Try Copilot button |
| Secondary CTA Border | `#ffffff` | Button border |
| Input Text | `#24292f` | Email input text color |
| Link Blue | `#79c0ff` | Secondary link color |

### Typography
| Element | Font | Size | Weight | Line Height |
|---------|------|------|--------|-------------|
| Hero Heading | Mona Sans | 56px | 440 | 61.6px |
| Hero Subtext | Mona Sans | 18px | 400 | 27px |
| Button Text | Mona Sans | 16px | 500 | 20.8px |
| Input/Label | Mona Sans | 16px | 400 | 24px |

### Elements (11 discovered)

#### hero-heading
- **Purpose:** Main hero heading that communicates GitHub's core value proposition about collaborative building
- **Tag:** `h1`
- **Text:** "The future of building happens together"

#### hero-subtext
- **Purpose:** Supporting paragraph that elaborates on the heading, explaining GitHub's role for developers and agents
- **Tag:** `p`
- **Text:** "Tools and trends evolve, but collaboration endures. With GitHub, developers, agents, and code come together on one platform."

#### cta-form
- **Purpose:** Horizontal flex row containing the email signup form and secondary CTA button
- **Tag:** `div`

#### email-input-container
- **Purpose:** White gradient container wrapping the email input field and sign-up button
- **Tag:** `div`

#### email-input
- **Purpose:** Text input field for email address entry with floating label 'Enter your email'
- **Tag:** `input`

#### email-label
- **Purpose:** Floating placeholder label 'Enter your email' that sits absolutely positioned over the input
- **Tag:** `label`
- **Text:** "Enter your email"

#### signup-button
- **Purpose:** Primary CTA button 'Sign up for GitHub' with green background to drive user registration
- **Tag:** `button`
- **Text:** "Sign up for GitHub"

#### copilot-cta-button
- **Purpose:** Secondary CTA link button 'Try GitHub Copilot free' with dark background and white border
- **Tag:** `a`
- **Text:** "Try GitHub Copilot free"

#### section-background
- **Purpose:** Dark navy-to-near-black gradient background inherited from ancestor .lp-Intro that provides the hero section's atmospheric backdrop
- **Tag:** `div`

#### gradient-overlay
- **Purpose:** Subtle white gradient overlay on top of the main background, adding depth and atmosphere
- **Tag:** `div`

#### canvas-animation
- **Purpose:** Background canvas element rendering animated visual effects (particle/constellation graphics) behind the hero content
- **Tag:** `canvas`

### Fonts
| Font | Source | Usage |
|------|--------|-------|
| Mona Sans | /assets/MonaSansVF.woff2 | Primary heading/body |
| Mona Sans Mono | /assets/MonaSansMonoVF.woff2 | Monospace/code |
| Hubot Sans | /assets/hubot-sans.woff2 | Secondary display |
