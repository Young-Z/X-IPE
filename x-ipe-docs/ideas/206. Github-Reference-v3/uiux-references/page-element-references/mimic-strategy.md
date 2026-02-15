# Mimic Strategy — GitHub Hero Section

## 6-Dimension Validation Rubric

### 1. Layout ✅ Confident
- **Structure:** Flex column, centered content
- **Hierarchy:** H1 heading → subtitle paragraph → CTA form row
- **CTA Row:** Flex row with 16px gap: [email-container (476px)] [copilot-btn (239px)]
- **Email Container:** Flex row, 3px padding, 8px border-radius, contains input (260px) + green button (202px)
- **Key:** Section is 972px wide, centered on page with 24px horizontal padding

### 2. Typography ✅ Confident
- **Primary Font:** "Mona Sans" (variable font, woff2)
- **Heading:** 56px, weight 440, line-height 61.6px, color #ffffff, text-align center
- **Subtext:** 18px, weight 400, line-height 27px, color #ffffff, max-width 600px, margin-top 20px
- **Buttons:** 16px, weight 500, line-height 20.8px
- **Input:** 16px, weight 400, color #24292f

### 3. Color Palette ✅ Confident
- **Background:** linear-gradient(rgb(0,2,64), rgb(13,17,23) 117%) — deep navy to near-black
- **Overlay:** linear-gradient(transparent -8.14%, rgba(255,255,255,0.1) 62.09%) — subtle white wash
- **Text:** #ffffff (pure white)
- **Primary CTA:** rgb(26,127,55) / #1a7f37 — GitHub green
- **Secondary CTA:** rgba(31,35,40,0.4) bg, 2px solid #fff border, rgb(121,192,255) text
- **Input Container:** linear-gradient(90deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.57) 300%)
- **Input Text:** #24292f, Label: rgba(36,41,47,0.9)

### 4. Spacing ✅ Confident
- **Section padding:** 0px 24px
- **Heading to subtext:** 20px (margin-top on paragraph)
- **Subtext to CTA row:** 32px (margin-top on CtaForm)
- **Email container internal padding:** 3px
- **Input padding:** 18px 12px 0px 18px
- **Button padding:** 6px 28px
- **CTA row gap:** 16px between email-container and copilot button

### 5. Visual Effects ✅ Confident
- **Background gradient:** Two-layer gradient system (base + overlay)
- **Canvas animation:** Behind hero content (particle/constellation effect — NOT mimicable as static)
- **Email container:** Gradient border effect via white border + gradient background
- **No box-shadows** on hero elements
- **No border-radius** on heading/text, 8px on containers, 6px on primary button

### 6. Static Resources ✅ Confident
- **Mona Sans Variable Font:** https://github.com/assets/MonaSansVF[wdth,wght,opsz]-902d64c7ad02.woff2
- **Mona Sans Mono:** https://github.com/assets/MonaSansMonoVF[wght]-04a1e3036ddf.woff2
- **Hubot Sans:** https://github.com/assets/hubot-sans-597e45ee1797.woff2
- **Canvas animation:** Not a static resource (dynamically generated)

## Overall Confidence: 6/6 dimensions confident
