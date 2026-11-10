# Etty Brunner — Landing Page Design System + Autonomous QA Specification
## Claude Code / Loop-Engineering Brief v2.0

> Build a production-quality Hebrew RTL landing page for Etty Brunner using the existing brand system, with a self-checking implementation loop covering visual design, UX, UI, accessibility, responsiveness, performance, analytics, and conversion.

## 1. DESIGN DECISION

### Quiet Scientific Editorial

Use this as the final visual direction:

**Editorial magazine × scientific publication × quiet luxury**

The page should feel calm, intelligent, human, credible, premium, spacious, emotionally precise, and quietly confident.

It must NOT look like a generic wellness website, therapy template, spiritual/healing website, SaaS landing page, startup template, Instagram influencer site, or aggressive sales funnel.

The existing Etty brand system already establishes this direction. Preserve it rather than inventing a competing identity.

Core positioning:
**Emotional MRI™ — the body communicates before the conscious mind understands.**

Core promise:
**Recognition before advice. Understanding before healing. Trust before conversion.**

---

# 2. SOURCE OF TRUTH

Before coding, inspect the existing implementation and brand files.

Preserve the established:
- calm / scientific / human / editorial / spacious / premium / trustworthy / curious personality
- Hebrew RTL
- Heebo headings
- Assistant body text
- Ultra Violet / Soft Violet / Warm Cream / Stone / Ink / Dark / Ember palette
- 12-column grid
- 8px baseline spacing
- generous whitespace
- minimal scientific visual motifs
- warm, natural, film-like photography
- no wellness clichés
- no heavy gradients
- no glassmorphism
- no neon glow
- WCAG AA minimum contrast

The landing-page funnel is:
**Instagram/Facebook → comment/DM → free 5-minute EFT experience → landing page → WhatsApp → free clarity call → potential paid coaching.**

Page sequence:
**Recognition → Experience → Understanding → Trust → Action**

---

# 3. AUDIT BEFORE CODING

Do not immediately write new UI.

First inspect:
- framework and routing
- existing components
- CSS/Tailwind/tokens
- fonts
- colors
- spacing
- breakpoints
- responsive behavior
- image/video handling
- analytics
- WhatsApp implementation
- accessibility
- SEO
- dependencies
- testing tools

Create an internal map:
`Existing component → Reuse / Modify / Replace`
`Existing token → Preserve / Adjust`
`Missing system → Add`

Do not rebuild an existing system unnecessarily.

---

# 4. DESIGN TOKENS

Use the existing palette:

```css
--color-ultra-violet: #5F4B8B;
--color-soft-violet: #8B7CAF;
--color-warm-cream: #F3F0EA;
--color-stone: #CFC8BC;
--color-ink: #241F2B;
--color-dark: #1A1626;
--color-ember: #C15F3C;
```

Create semantic tokens for background, surface, text, muted text, primary, hover, border and focus.

Never introduce arbitrary colors.

Test actual foreground/background combinations for WCAG contrast.

---

# 5. TYPOGRAPHY

Hebrew:
- Display/H1: Heebo 700–800
- H2: Heebo 700–800
- H3: Heebo 700
- Body: Assistant 400–500
- Labels: Assistant 500

Do not introduce decorative fonts or a second display typeface.

Suggested responsive starting scale:
- Display: 40–48px mobile / 64–80px desktop
- H1: 36–44px / 56–68px
- H2: 30–36px / 44–52px
- H3: 24–28px / 30–36px
- Body: 17–19px / 18–21px
- Small: 14–16px

Use `clamp()` or equivalent tokenized scaling.

Validate Hebrew line breaks visually.

---

# 6. SPACING + GRID

Use an 8px baseline.

Suggested spacing tokens:
`4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96, 128, 160`

Avoid arbitrary values unless justified.

Desktop:
- max width ~1200–1280px
- 12 columns

Tablet:
- 8 columns

Mobile:
- 4 columns

Use Grid/Flexbox for structure. Absolute positioning is for decoration only.

---

# 7. RTL

Use:
```html
<html lang="he" dir="rtl">
```

Verify:
- right-aligned Hebrew
- RTL flex/grid behavior
- correct icon placement
- correct mobile ordering
- punctuation
- numbers
- mixed Hebrew/English
- navigation direction
- no justified paragraphs

Do not assume `direction: rtl` is sufficient.

---

# 8. VISUAL PRINCIPLES

Apply these explicitly:

1. One focal point per section.
2. Hierarchy before decoration.
3. Use size, position, spacing, contrast and weight before color/decorative effects.
4. Repetition creates professionalism.
5. Remove elements that do not improve comprehension, trust, emotional resonance, navigation or conversion.
6. Prefer subtraction over addition.

Apply Gestalt:
- proximity
- similarity
- common region
- continuity
- figure/ground

The visual path should support:
**recognition → video → CTA → trust → proof → CTA**

---

# 9. COMPONENT SYSTEM

Build reusable components:
- PageShell
- Header
- HeroRecognition
- VideoExperience
- PrimaryCTA
- ClarityCallCTA
- TrustSection
- ExperienceStats
- Testimonial
- AudienceRecognition
- FAQ
- FinalCTA
- Footer
- WhatsAppButton

Do not duplicate repeated UI.

### Buttons
Primary CTA uses Ultra Violet, high-contrast text, consistent sizing, hover/active/focus states, and comfortable touch targets.

Prefer ~48px height and at least 44×44 CSS px interactive area.

### Cards
Use sparingly. Do not turn every section into a card.

### Radius
Use one restrained system, e.g. 8 / 12 / 16px. Avoid excessive pill UI.

---

# 10. LANDING PAGE IA

## 01 — Recognition
Immediately answer why the visitor is here.

Direction:
> אם משהו בתוכך מרגיש אחרת לאחרונה —
> עצרי כאן לכמה דקות.

## 02 — Free 5-minute EFT
This is the main value-delivery experience.
- prominent video
- obvious play
- no sound autoplay
- captions if available
- visible duration
- poster image
- fast loading
- accessible controls

## 03 — Video → Clarity Call
The exercise helped her pause; the conversation helps her understand her specific situation.

Primary CTA:
**לתיאום שיחת בהירות בוואטסאפ**

## 04 — Why Etty
Show verified experience, credentials, methodology and human credibility.

Never invent client counts, credentials, certifications, years or outcomes.

## 05 — Testimonials
Use 3–5 strong testimonials, each answering a trust objection.

## 06 — Recognition
Use real language from DMs/comments where available.

## 07 — FAQ / Objections
Address:
- Will this help me?
- Is this for me?
- I've tried other things.
- I'm embarrassed.
- What happens on the call?
- What exactly does Etty do?
- Is this medical/psychological treatment?

Never imply coaching/EFT replaces appropriate medical or mental-health care.

## 08 — Final CTA
Quiet, human, low pressure.

Direction:
> אולי את לא צריכה עוד עצה.
> אולי קודם צריך להבין מה קורה.

CTA:
**לתיאום שיחת בהירות בוואטסאפ**

---

# 11. CTA SYSTEM

One primary conversion:
**WhatsApp → clarity call**

Use one consistent primary CTA.

Avoid:
- BUY NOW
- CLAIM YOUR SPOT
- START YOUR HEALING
- LIMITED TIME
- TRANSFORM YOUR LIFE

No fake scarcity or deceptive sales framing.

The free clarity call must genuinely provide clarity even if no purchase follows.

---

# 12. WHATSAPP

CTA must:
1. open WhatsApp
2. use the verified destination
3. optionally prefill a short human message
4. preserve attribution where technically possible

Do not invent the phone number.

Track:
- `clarity_cta_click`
- `whatsapp_open`

---

# 13. IMAGERY

Use women approximately 35–65 with:
- authentic appearance
- natural skin
- minimal makeup
- calm expressions
- natural environments
- window light
- neutral clothing
- warm, low-saturation, film-like grading

Avoid:
- spa imagery
- yoga poses
- fake smiles
- influencer aesthetics
- young stock models
- excessive retouching

AI imagery must reserve clean whitespace for Hebrew copy. Never bake Hebrew text into generated images.

---

# 14. SCIENTIFIC VISUAL LANGUAGE

Approved motifs:
- MRI slices
- body contours
- neural constellations
- breath waves
- topographic contours
- cellular textures
- scientific annotations
- observation grids
- concentric rings
- botanical anatomy

Use one motif per composition.

Style:
thin, restrained, low-opacity, editorial, museum-like.

Avoid cartoonish graphics.

Allowed texture:
- subtle paper grain
- fine noise
- microscopic particles
- fine fibers

Avoid:
- heavy gradients
- glassmorphism
- neon glow
- excessive shadows
- floating blobs
- generic purple gradients
- excessive 3D

---

# 15. ANIMATION

Animation is progressive enhancement.

Use subtle transitions only.

Respect:
```css
@media (prefers-reduced-motion: reduce)
```

Do not animate every section.

Never use animation to compensate for weak hierarchy.

---

# 16. WCAG 2.2 AA

Target WCAG 2.2 AA.

Check:

### Perceivable
- contrast
- alt text
- captions/transcripts where applicable
- no color-only information
- scalable text
- responsive reflow

### Operable
- keyboard navigation
- visible focus
- adequate touch targets
- no traps
- skip link where appropriate
- no hover-only content

### Understandable
- predictable navigation
- clear labels
- clear error states
- clear CTA language

### Robust
- semantic HTML
- accessible names
- logical heading hierarchy
- landmarks
- ARIA only when necessary

---

# 17. ACCESSIBLE VIDEO

Ensure:
- keyboard-operable controls
- captions if available
- transcript if practical
- accessible title/label
- no forced autoplay with sound
- visible controls
- adequate contrast
- mobile usability

If using a third-party player, verify its actual accessibility.

---

# 18. RESPONSIVE QA

Test:
`320, 375, 390, 430, 768, 1024, 1280, 1440`

Check:
- no horizontal scroll
- no clipping
- no overlaps
- natural Hebrew wrapping
- CTA remains obvious
- video usable
- image focal points preserved
- sticky CTA does not obscure content
- FAQ usable
- typography comfortable

Mobile is the primary conversion environment. Do not simply shrink desktop.

---

# 19. PERFORMANCE

Optimize:
- LCP
- INP
- CLS
- hero image
- video loading
- fonts
- image dimensions
- lazy loading
- JavaScript
- dependencies
- responsive images

The video is the major heavy asset. Implement it carefully.

---

# 20. SEO

Implement:
- title
- meta description
- canonical
- Open Graph
- language/RTL
- semantic headings
- descriptive URL
- favicon
- structured data only where factually appropriate

Do not keyword-stuff.

---

# 21. ANALYTICS

Track:
```text
landing_page_view
video_play
video_25
video_50
video_75
video_complete
clarity_cta_click
whatsapp_open
faq_expand
scroll_50
scroll_90
```

Preserve:
- UTM source
- UTM medium
- UTM campaign
- content/Reel identifier
- DM keyword where available

Primary metrics:
1. WhatsApp CTR
2. clarity-call booking rate

Secondary:
- video start
- video completion
- CTA CTR
- scroll depth
- conversion by source/content

---

# 22. LOOP ENGINEERING

Claude must NOT use:
**prompt → code → done**

Use:
**inspect → plan → implement → build → test → render → observe → critique → fix → verify → repeat**

Every meaningful UI change must go through this loop.

---

# 23. LOOP CHECKLIST

Maintain:

```text
[ ] Existing implementation audited
[ ] Tokens audited
[ ] Components audited
[ ] Funnel implemented
[ ] Mobile implemented
[ ] Desktop adapted
[ ] RTL verified
[ ] Accessibility checked
[ ] Contrast checked
[ ] Keyboard checked
[ ] Video checked
[ ] WhatsApp checked
[ ] Analytics checked
[ ] Performance checked
[ ] Screenshots reviewed
[ ] Conversion review completed
```

Never mark an item complete from assumption. Verify it.

---

# 24. AFTER EVERY MAJOR CHANGE

Run:

### A. Build
Confirm successful build.

### B. Tests
Run existing unit/integration/browser tests.

### C. Screenshots
Capture:
- 390×844
- 768×1024
- 1440×900

### D. Visual inspection
Inspect the rendered result.

### E. Accessibility
Run automated checks.

### F. Performance
Run Lighthouse or equivalent.

### G. UX critique
Evaluate hierarchy and task completion.

### H. Fix
Fix highest-impact issues.

### I. Retest
Repeat.

---

# 25. VISUAL SELF-CRITIQUE

For every major visual iteration, ask:

### Hierarchy
- What does the eye see first?
- Is that intended?
- Is the primary CTA obvious?
- Is the video obviously the promised resource?

### Alignment
- Do major elements share consistent edges?
- Is RTL alignment consistent?
- Are components aligned to the grid?

### Spacing
- Are sections compressed?
- Are they unnecessarily large?
- Are related elements grouped?

### Typography
- Are Hebrew line breaks natural?
- Are headings dominant?
- Is body copy readable?
- Are paragraphs too wide?
- Does hierarchy work without color?

### Composition
- One focal point per section?
- Unnecessary decoration?
- Consistent rhythm?

### Brand
- Does this feel unmistakably Etty?
- Scientific + human?
- Premium without becoming fashion/luxury?
- Calm without becoming bland?

---

# 26. FIVE-SECOND TEST

Inspect only the first viewport.

Answer:
1. Why am I here?
2. What do I get?
3. What should I do?
4. Who is this for?
5. Why should I trust it?

If any answer is unclear, identify the visual/copy reason and fix it before polishing.

---

# 27. BLUR / GRAYSCALE / SQUINT TESTS

### Blur
Hierarchy should still roughly communicate:
**recognition → video → CTA → trust**

### Grayscale
Hierarchy must survive without color using:
- size
- weight
- position
- spacing
- contrast

### Squint
The main visual path should remain:
**woman/problem → EFT → next step**

Not:
**decorative graphic → logo → random card → testimonial**

---

# 28. COGNITIVE LOAD

The visitor should make very few decisions.

Primary decision:
**Do I want to start a WhatsApp conversation about a clarity call?**

Do not add competing goals such as:
- newsletter
- unrelated download
- follow Instagram
- email form
- second lead magnet
- product purchase

The funnel has one job.

---

# 29. COPY SELF-CHECK

Every section must pass:

### Relevance
Does this speak to her actual situation?

### Specificity
Could this copy belong to any wellness coach?
If yes, rewrite.

### Credibility
Is the claim supported?

### Voice
Would Etty actually say this?

### Restraint
Is any copy unnecessary?

### CTA temperature
Does the CTA match the visitor's trust level?

Prefer exact language from DMs/comments over invented marketing language.

---

# 30. CLAIM SAFETY

Never invent or imply:
- medical outcomes
- guaranteed emotional healing
- cures
- diagnoses
- clinical credentials
- unverified scientific evidence
- exact client numbers
- exact success rates

Use explicit placeholders when facts are missing:
`[VERIFY: certification]`
`[VERIFY: client count]`
`[VERIFY: 30-year wording]`

---

# 31. AUTOMATED QA

Use available tooling, preferably:

### Lighthouse
Performance, accessibility, SEO, best practices.

### axe
Automated accessibility/WCAG checks.

### Playwright
Browser, responsive, interaction and regression testing.

If unavailable:
- inspect package manager
- install only what is necessary
- avoid unnecessary dependencies

---

# 32. PLAYWRIGHT CORE FLOW

Test:

```text
open page
→ verify Hebrew RTL
→ verify hero
→ verify video
→ interact with video where testable
→ scroll
→ verify clarity CTA
→ click CTA
→ verify WhatsApp destination
```

Also test:
- keyboard navigation
- mobile viewport
- desktop viewport

---

# 33. REGRESSION PROTECTION

Once approved:
- capture baseline screenshots
- compare future changes
- protect layout, typography, spacing, colors, CTA, video and responsive behavior

Do not allow unrelated changes to silently alter the design system.

---

# 34. ISSUE SEVERITY

### P0 — Blocker
Page fails, CTA/video broken, major mobile failure, inaccessible primary task.

### P1 — High
Unclear hero, poor mobile hierarchy, major contrast failure, keyboard trap, broken RTL, serious conversion friction.

### P2 — Medium
Inconsistent spacing, awkward line break, secondary accessibility/responsive issue.

### P3 — Low
Minor cosmetic refinement.

Always fix P0/P1 before P2/P3.

---

# 35. DO NOT POLISH THE WRONG THING

If the 5-second test fails, do not tweak shadows.

If CTA is unclear, do not redesign icons.

If mobile is broken, do not optimize desktop.

If accessibility fails, do not add animation.

If funnel is confusing, do not add sections.

Fix the highest-leverage problem first.

---

# 36. DESIGN DECISION LOG

For significant decisions record:

```text
Decision:
Reason:
Evidence:
Tradeoff:
Result:
```

This prevents random design drift.

---

# 37. AI IMAGE WORKFLOW

For every generated visual:

1. define purpose
2. define emotional state
3. define subject
4. define composition
5. reserve Hebrew whitespace
6. define lighting
7. define grading
8. generate candidates
9. select based on brand fit, not novelty
10. optimize asset
11. add website text in HTML/CSS

Never bake Hebrew copy into generated imagery.

---

# 38. AI IMPLEMENTATION BEHAVIOR

Claude should challenge instructions that conflict with:
- usability
- accessibility
- conversion
- brand consistency
- technical correctness

When a request conflicts with the system:
1. identify the conflict
2. explain it briefly
3. propose the closest compliant alternative
4. implement the better option unless explicit approval is required

---

# 39. FINAL ACCEPTANCE GATE

## Brand
- [ ] calm
- [ ] scientific
- [ ] human
- [ ] editorial
- [ ] premium
- [ ] trustworthy
- [ ] no wellness clichés

## UX
- [ ] five-second test passes
- [ ] funnel is obvious
- [ ] video easy to find/use
- [ ] CTA obvious
- [ ] no competing conversion goal
- [ ] cognitive load low
- [ ] mobile-first flow works

## UI
- [ ] design tokens used
- [ ] grid consistent
- [ ] spacing consistent
- [ ] typography consistent
- [ ] component states complete
- [ ] visual hierarchy strong
- [ ] no unnecessary decoration

## Accessibility
- [ ] WCAG 2.2 AA target
- [ ] contrast tested
- [ ] keyboard tested
- [ ] visible focus
- [ ] semantic HTML
- [ ] alt text
- [ ] video accessibility
- [ ] reduced motion
- [ ] zoom/reflow checked
- [ ] screen-reader sanity check

## Technical
- [ ] build passes
- [ ] tests pass
- [ ] no console errors
- [ ] no broken links
- [ ] WhatsApp works
- [ ] analytics fire
- [ ] performance checked
- [ ] responsive screenshots checked

## Conversion
- [ ] primary CTA works
- [ ] CTA appears at logical points
- [ ] testimonials reduce objections
- [ ] clarity call clearly explained
- [ ] no deceptive sales framing
- [ ] no fake urgency

---

# 40. THE AUTONOMOUS LOOP

```text
AUDIT
  ↓
DEFINE
  ↓
DESIGN
  ↓
IMPLEMENT
  ↓
BUILD
  ↓
TEST
  ↓
SCREENSHOT
  ↓
VISUAL CRITIQUE
  ↓
UX CRITIQUE
  ↓
ACCESSIBILITY AUDIT
  ↓
PERFORMANCE AUDIT
  ↓
FIX HIGHEST-SEVERITY ISSUE
  ↓
RETEST
  ↓
REPEAT
  ↓
FINAL HUMAN REVIEW
```

Never stop at the first successful build.

The page is finished only when:
- implementation works
- visual system is coherent
- user can complete the intended task
- accessibility is acceptable
- performance is strong
- design survives critical review

# NORTH STAR

The visitor should think:

> "She understands what I'm going through."
>
> "I can try something right now."
>
> "This feels different from generic wellness content."
>
> "Etty seems experienced and trustworthy."
>
> "I understand what the call is."
>
> "Talking to her is a reasonable next step."

The goal is not to convince everyone.

The goal is to make the right woman think:

# "I want to talk to her."
