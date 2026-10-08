# LumeBook (לומבוק) Hebrew Instagram carousels: visual design evidence review

Prepared 2026-10-06 for one SMM working in Canva. Audience: Israeli parents reading on phones, Hebrew RTL. Goal: stop on slide 1, understand fast, swipe to the end, create a free preview.

## How to read this file

Every claim carries an evidence tag:

- **L1 Research / standard**: peer-reviewed study or formal standard (WCAG, Unicode). Note that almost none of this research was run on Instagram carousels, so "transfer" to carousels is an inference, marked as such.
- **L2 Practitioner**: credible expert or platform guidance (NN/g, Apple HIG, Material, W3C notes, BDA, Meta/Instagram/Google docs). Usually based on usability studies or proprietary data, not peer review.
- **L3 Convention**: widely repeated in the industry, no evidence found.
- **L4 Hypothesis**: plausible, worth testing on LumeBook's own posts.

Verification marks: **[opened]** = I read the primary page or PDF this session. **[abstract]** = only the abstract or a reliable summary was read. **[secondary]** = reported by a secondary source, primary not opened. **[unverified]** = could not open; treat as a lead, not a fact. **[derived]** = my own calculation from the cited numbers.

Budget used: 40 WebSearch calls plus direct page fetches (some pages read through the in-app browser because they block plain fetches).

---

## 0. The short version (what changes in practice)

1. Body text on a 1080 px canvas should be at least about 48 px, and 56 px is a safer default for Hebrew; the cover headline needs about 110 px or more if it must survive the profile grid. Math in section 1.3. (L2 derived)
2. Gold #E6B762 text on cream #F8F0E1 is 1.64:1 and fails WCAG at any size. Gold works only on ink. Table in 2.3. (L1 derived)
3. Hebrew readers map "earlier" to the right and "later" to the left. Put "before" on the right and "after" on the left inside a slide. (L1 transfer, section 3.7)
4. I could not verify whether Instagram's Hebrew UI mirrors the carousel swipe direction. Do not commit to an arrow direction until it is tested on a Hebrew-UI phone and an English-UI phone. (L4, section 3.8)
5. The "image that runs over the slide edge" trick has no published evidence, only vendor claims. Instagram's own swipe cue (dots below the image) is the kind of cue NN/g found users miss, so an in-image cue is a reasonable test. (L3/L4, section 4.4)
6. Faces lift likes and comments; a book held in hands (face not dominant) lifts expressed purchase intent. Use faces for slide 1, hands-plus-book for the conversion slides. (L1, section 5)
7. One CTA, verb first, specific, repeated in the caption. A button-shaped graphic on a static image is a false affordance; test it, do not assume it helps. (L2/L4, section 7)

---

## 1. Mobile text legibility

### 1.1 Platform minimums

- **Apple HIG Typography** (Apple, page change log 2025-12-16) [opened via Apple's JSON data endpoint]. URL: https://developer.apple.com/design/human-interface-guidelines/typography
  - iOS/iPadOS default text size 17 pt, minimum 11 pt. **L2**
  - Dynamic Type "Large (default)": Large Title 34/41, Title 1 28/34, Title 2 22/28, Title 3 20/25, Headline 17 semibold/22, Body 17/22, Callout 16/21, Subhead 15/20, Footnote 13/18, Caption 1 12/16, Caption 2 11/13 (size/leading in pt). **L2**
  - Avoid Ultralight, Thin and Light weights, especially at small sizes. **L2**
  - Avoid tight leading when showing three or more lines. **L2**
- **Material 3 type scale tokens** (Google, material-components/material-web, token file `_md-sys-typescale.scss` v0_192) [opened]. URL: https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-typescale.scss
  - In rem (1 rem = 16 px/sp): body-large 1/1.5 (16/24), body-medium 0.875/1.25 (14/20), body-small 0.75/1 (12/16), label-small 0.6875/1 (11/16), title-large 1.375/1.75 (22/28), headline-small 1.5/2 (24/32), headline-medium 1.75/2.25 (28/36), display-small 2.25/2.75 (36/44). **L2**
  - The m3.material.io pages did not render for fetching; the token file is the source of truth they are generated from.

### 1.2 Assumptions for the canvas math

- The user stated phones display the post at about 360 to 430 points wide. I did not re-verify device widths. [unverified device list]
- Assumes a feed post spans the full screen width (true for Instagram feed images as far as I know; check on device). [unverified]
- iOS points and Android dp are both close to a CSS px; WCAG's "18 pt" is a print point, about 24 CSS px. So Apple's "17 pt body" is about 17 CSS px, well below WCAG's "large text" (24 CSS px). Do not mix the two "pt" units.
- Assumes Canva's font-size number equals canvas pixels for a pixel-sized design. **Not verified.** Calibration test: set a Latin "H" in Heebo at size 100 on a 1080-wide design, export PNG, measure the letter height in pixels. If cap height is roughly 70 px, the unit is px (cap height is roughly 0.7 em in most sans fonts). [unverified, L4]
- Hebrew glyphs look smaller than Latin capitals at the same font size (Apple RTL guidance, section 3.5), so Hebrew needs a small upward correction.

### 1.3 Translation table [derived]

Canvas px needed = target size x 1080 / display width. Scale factor: 360 pt wide = 0.333 pt per px; 393 = 0.364; 430 = 0.398.

| Target on phone | Source | At 360 pt | At 393 pt | At 430 pt |
|---|---|---|---|---|
| 11 pt | Apple absolute minimum | 33 px | 30 px | 28 px |
| 12 pt | Apple Caption 1, Material body-small | 36 px | 33 px | 30 px |
| 13 pt | Apple Footnote | 39 px | 36 px | 33 px |
| 16 pt | Material body-large; BDA 16 px floor | 48 px | 44 px | 40 px |
| 17 pt | Apple Body | 51 px | 47 px | 43 px |
| 19 pt | Apple Body + 2 pt Hebrew correction; BDA 19 px ceiling | 57 px | 52 px | 48 px |
| 18.7 CSS px bold | WCAG "large" bold threshold (14 pt bold) | 56 px | 51 px | 47 px |
| 24 CSS px | WCAG "large" regular threshold (18 pt) | 72 px | 66 px | 60 px |
| 28 pt | Apple Title 1 | 84 px | 77 px | 70 px |
| 34 pt | Apple Large Title | 102 px | 93 px | 85 px |

Profile grid: a tile is about one third of the screen width (120 to 143 pt). To reach 11 pt there: 11 x 1080 / 120 = **99 px** on the canvas (83 px at 430 pt). So a cover headline of about 110 px or more stays readable as a grid tile on small phones. [derived]

Line length check: a 888 px text column (96 px side margins) at 56 px Hebrew body fits roughly 30 to 35 characters per line, assuming an average advance of about 0.5 em per character including spaces. Measure in your actual font. [derived, estimate]

### 1.4 Line length and spacing research

- **Dyson, M. C. (2004). How physical text layout affects reading from screen.** Behaviour & Information Technology 23(6), 377-393. URL: https://www.ingentaconnect.com/content/tandf/tbit/2004/00000023/00000006/art00002 (full text read from a hosted PDF: https://stu.westga.edu/~ssynan1/literacy/Dyson.pdf) [opened]
  - Characters per line is the critical variable, not physical width. **L1**
  - Longer lines (up to about 100 characters) were often read faster on screen, partly due to less scrolling; Dyson & Haselgrove (2001) found 55 characters per line gave better comprehension than 100; Dyson & Kipping (1998) found readers rated 55 cpl easiest although it was not fastest. **L1**
  - Double line spacing was marginally to clearly faster than single in older studies (Kolers et al. 1981; Kruk & Muter 1984). **L1**
  - Applicability: these are long passages on desktop monitors. A carousel slide has 1 to 6 short lines, which the studies did not test. Do not read "55 cpl" as a target for slides. **Transfer: L4**
- **WCAG 2.2 SC 1.4.8 Visual Presentation (Level AAA)** (W3C). URL: https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html [opened]
  - Lines no wider than 80 characters (40 for CJK), text not justified, line spacing at least 1.5 within paragraphs, paragraph spacing at least 1.5 times line spacing. Note 2: a setting a writing system does not use need not apply. **L1 (AAA)**
- **BDA Dyslexia Style Guide 2018** (British Dyslexia Association). Hosted copy: https://iped-editors.org/wp-content/uploads/2021/05/British-Dyslexia-Association-Style-Guide-2018.pdf [opened; the bdadyslexia.org.uk page URL returned 404]
  - Lines 60 to 70 characters; line spacing 1.5; left align without justification (for Hebrew the equivalent is right align, ragged left). **L2**

### 1.5 How much people read on small screens

- **Moran, K. (2016-12-11). Reading Content on Mobile Devices.** NN/g. URL: https://www.nngroup.com/articles/mobile-content/ [opened]
  - Four study phases, 1,629 cases: no practical comprehension difference between phone and computer; difficult articles were read about 30 ms per word slower on mobile. Recommends brevity and simple language. **L2**
  - Paraphrase: comprehension holds on phones, but hard text costs more time there.
- **Nielsen, J. (2011-02-27). Mobile Content Is Twice as Difficult.** NN/g. URL: https://www.nngroup.com/articles/mobile-content-is-twice-as-difficult-2011/ [opened]
  - Cloze test on privacy policies: 18.93% on an iPhone-sized screen vs 39.18% on desktop. Superseded for easy text by the 2016 study; still a warning for complex text. **L2**
- **Moran, K. (2020-04-05). How People Read Online: New and Old Findings.** NN/g. URL: https://www.nngroup.com/articles/how-people-read-online/ [opened]
  - 13 years, 500+ participants: people scan (F-pattern, layer-cake, spotted, commitment); front-load key words, use headings, bold, lists. **L2**
- **Nielsen, J. (2015-11-15). Legibility, Readability, and Comprehension.** NN/g. URL: https://www.nngroup.com/articles/legibility-readability-comprehension/ [opened]
  - Users read about 28% of words on an average page; target an 8th-grade reading level for broad audiences. **L2**

### 1.6 Text amount per slide

- **Meta, Best practices for image ads** (Meta Business Help Center, read 2026-10-06). URL: https://www.facebook.com/business/help/388369961318508 [opened in browser]
  - No longer any limit on text in ad images. Advice: text overlays should not obstruct visuals; "a modern, clean font in a large enough type size and a contrasting hue." **L2**
- **Meta, About text overlays and the safe zone** URL: https://www.facebook.com/business/help/980593475366490 [opened in browser]
  - "Don't communicate too many messages because ads usually only have one call to action." **L2**
  - The often-quoted "images with less than 20% text perform better" appeared in a search snippet of older Meta copy but is **not** on the current pages I opened. **L3** for the 20% number.
- No study found that sets a maximum number of words per slide or per social image. Any word cap is **L3/L4**. The spec sheet below uses caps derived from the type sizes (what physically fits at a legible size) plus COGA's "keep text succinct" (section 2.7).

---

## 2. Contrast and accessibility

### 2.1 WCAG contrast

- **WCAG 2.2 SC 1.4.3 Contrast (Minimum), Level AA** (W3C). URL: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html [opened]
  - Text and images of text: at least 4.5:1; large-scale text at least 3:1. **L1**
  - Large scale = at least 18 pt, or 14 pt bold; W3C gives approximately 24 px and 18.5 px CSS equivalents. **L1**
  - Applies to images of text (so it applies to a carousel slide). Logotypes are exempt. Fonts with very thin strokes are harder to read, especially at lower contrast. **L1**
  - Level AAA (SC 1.4.6) raises this to 7:1 and 4.5:1. [page not opened this session; widely known] **L1 [unverified]**
- **WCAG 2.2 SC 1.4.11 Non-text Contrast, Level AA**. URL: https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html [opened]
  - Visual information needed to identify UI components, and graphics needed to understand content, need 3:1 against adjacent colours; ratios are not rounded up (2.999:1 fails). **L1**
  - Relevance: if a CTA "pill" or an arrow carries meaning, its shape should hit 3:1.

### 2.2 Text over photos

- **Harley, A. (2015-10-18, reviewed 2026-01-13). Ensure High Contrast for Text Over Images.** NN/g. URL: https://www.nngroup.com/articles/text-over-images/ [opened]
  - Techniques: semi-transparent overlay or gradient scrim, blur part of the image, text shadow, place text on plain areas, semi-opaque box behind text; still meet 4.5:1 (3:1 large). **L2**
- **Scrim calculation** [derived from the WCAG luminance formula, assuming normal sRGB alpha blending, which I did not verify for Canva]:
  - Worst case (pure white area behind the text), white text needs: black overlay at 55% gives 4.76:1, at 60% gives 5.74:1; LumeBook ink #0B0518 overlay at 55% gives 4.48:1 (fails), at 60% gives 5.36:1.
  - Cream #F8F0E1 text over an ink scrim: 60% gives 4.73:1, 65% gives 5.70:1.
  - Rule: a scrim of at least 60% (65% for cream text) behind body text guarantees AA whatever the photo shows. Verify by sampling the exported PNG. **L1 derived, L4 for Canva behaviour**

### 2.3 LumeBook palette contrast [derived, WCAG formula, palette from project memory note "LumeBook design tokens"]

| Text on background | Ratio | Verdict |
|---|---|---|
| Ink #0B0518 on cream #F8F0E1 | 17.67:1 | Pass AAA |
| Ink #0B0518 on light cream #FBF7F0 | 18.74:1 | Pass AAA |
| Ink-2 #1D1039 on cream | 15.64:1 | Pass AAA |
| Gold #E6B762 on ink #0B0518 | 10.78:1 | Pass AAA |
| Gold #E6B762 on ink-3 #291852 | 8.40:1 | Pass AAA |
| Soft gold #F3D9A1 on ink | 14.54:1 | Pass AAA |
| Ink on gold #E6B762 (gold button, ink label) | 10.78:1 | Pass AAA |
| Cream on ink-3 #291852 | 13.77:1 | Pass AAA |
| Violet #5B2BD6 on cream | 6.71:1 | Pass AA |
| White on violet #5B2BD6 | 7.60:1 | Pass AAA |
| Dark gold #C9954A on ink | 7.51:1 | Pass AAA |
| **Gold #E6B762 on cream** | **1.64:1** | **Fails, even for large text** |
| **Dark gold #C9954A on cream** | **2.35:1** | **Fails** |
| **Dark gold #C9954A on white** | **2.66:1** | **Fails** |
| **White on gold #E6B762** | **1.86:1** | **Fails** |

Practical meaning: on light slides, gold is decoration only (lines, shapes, highlights behind ink text), never text. A gold CTA button needs an ink label, not white.

### 2.4 Alt text, captions, emoji, hashtags

- **Instagram Help Center: Edit the alternative text for a post** (Meta, read 2026-10-06). URL: https://help.instagram.com/503708446705527 [opened in browser]
  - Automatic alt text uses object recognition; you can replace it; it is only read to screen-reader users. Edit before sharing (Accessibility, write alt text) or after posting (Edit, Accessibility). **L2**
  - The page does not say whether each carousel slide gets its own alt-text field. [unverified; check in app]
- **Instagram Help Center: Share a post with multiple photos or videos** URL: https://help.instagram.com/269314186824048 [opened in browser]
  - Up to 20 items per carousel; one orientation applies to all items; one caption per post; you can tag someone in each photo; you can reorder or remove items after posting. **L2**
- **NSW Government Digital, Accessibility and inclusivity toolkit: Social media** (no date shown). URL: https://www.digital.nsw.gov.au/delivery/accessibility-and-inclusivity-toolkit/communication/social-media [opened]
  - Camel-case hashtags for screen readers; at most one emoji per location, never carry essential meaning by emoji alone; when an image contains text, put that text in the caption too; contrast 4.5:1 minimum, aim for 7:1. **L2**
- **Tigwell, G. W., Gorman, B. M., Menzies, R. (2020). Emoji Accessibility for Visually Impaired People.** CHI 2020. URL: https://dl.acm.org/doi/10.1145/3313831.3376267 [abstract]
  - Survey of 58 visually impaired people plus 11 screen-reader interviews: emoji descriptors read aloud can hinder communication. **L1**

### 2.5 Low vision

- **W3C, Accessibility Requirements for People with Low Vision** (First Public Working Draft, 2016-03-17). URL: https://www.w3.org/TR/low-vision-needs/ [opened]
  - Users need to change text size, spacing, line length and colours themselves, and information must not depend on colour alone. An image of text cannot be adapted, so the same words must also exist as real text (caption, alt text). **L2**
- Note: parents of young children are often in their 30s and 40s, when near-focus starts to decline. This supports erring larger. [unverified, not researched this session] **L4**

### 2.6 Dyslexia

- **BDA Dyslexia Style Guide 2018** [opened] (URL in 1.4). **L2**
  - Sans serif; 12 to 14 pt or 16 to 19 px; letter spacing ideally about 35% of average letter width, word spacing at least 3.5 times letter spacing; line spacing 1.5.
  - Bold for emphasis; avoid underline, italics, all caps.
  - Headings at least 20% larger than body.
  - Single-colour backgrounds; avoid patterns or pictures behind text; dark text on light, not pure white (cream or soft pastel); avoid green and red/pink pairings.
  - No justification; avoid multiple columns; use white space; short sentences, active voice; bullets over prose; flow charts for procedures.
  - Fit with LumeBook: the cream ground (#F8F0E1) and ink text already match the BDA advice.

### 2.7 Attention and cognitive load (accessibility view)

- **W3C, Making Content Usable for People with Cognitive and Learning Disabilities** (W3C Working Group Note, 2021-04-29). URL: https://www.w3.org/TR/coga-usable/ [opened]
  - Relevant patterns: use clear words; keep text succinct; separate each instruction; use white spacing; avoid too much content; make the purpose clear; use a consistent visual design; clearly identify controls; use icons that help; use clear formatting and punctuation. **L2**

---

## 3. Hebrew typography and RTL

### 3.1 Reading direction shapes attention while reading

- **Pollatsek, A., Bolozky, S., Well, A. D., Rayner, K. (1981). Asymmetries in the perceptual span for Israeli readers.** Brain and Language 14, 174-180. URL: https://www.researchgate.net/publication/222635478_Asymmetries_in_the_perceptual_span_for_Israeli_Readers [abstract]
  - Israeli readers' perceptual span was asymmetric to the left when reading Hebrew and to the right when reading English. Attention follows the script being read. **L1**
  - Implication: Israeli parents are bidirectional readers; direction effects will be real but flexible (see 3.7).

### 3.2 Unpointed Hebrew

- **Weiss, Y., Katzir, T., Bitan, T. (2015). Many ways to read your vowels: neural processing of diacritics and vowel letters in Hebrew.** NeuroImage 121, 10-19. URL: https://www.sciencedirect.com/science/article/abs/pii/S1053811915006400 (PDF: https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/Weiss-Katzir-and-Bitan-2015NI.pdf) [opened, abstract and intro]
  - fMRI, 18 adults, single words: vowel letters (familiar) and diacritics (transparent but less familiar) had opposite effects; familiarity outweighed transparency. **L1**
  - Implication: write in ktiv male (full spelling with vowel letters), no niqqud, for adult readers; add niqqud only where a word is genuinely ambiguous. **L4 for the carousel rule**

### 3.3 Hebrew font legibility research

- Two targeted searches found **no peer-reviewed comparison of Hebrew screen fonts**. General Latin research on serif vs sans shows small or no differences. **Gap: no L1 basis for choosing one Hebrew font over another.**
- Practical risk to check by eye: letter pairs that differ by small details, such as ד/ר, ה/ח/ת, ו/ז/ן, ס/ם, ב/כ. Pick a font and weight where these stay distinct after Instagram compression. **L4**

### 3.4 Hebrew fonts available

- **Google Fonts metadata API** (fonts.google.com/metadata/fonts, read 2026-10-06) [opened]. Sans and rounded families with the Hebrew subset, by popularity, with designers and number of styles:
  - Open Sans (Steve Matteson; 12 styles incl. italics), Rubik (Hubert and Fischer, Meir Sadan and others; 14 incl. italics), **Heebo** (Oded Ezer; 9 weights), Assistant (Adobe, Ben Nathan; 7), Fredoka (Milena Brandão, Hafontia; 5, rounded), Varela Round (1 weight), Noto Sans Hebrew (Google; 9), Secular One (Michal Sahar; 1, display), Alef (2), IBM Plex Sans Hebrew (Mike Abbink, Bold Monday; 7), Miriam Libre (4), Playpen Sans Hebrew (TypeTogether; 8, handwriting). Serif: Frank Ruhl Libre (7), David Libre (3), Suez One (1). Display: Karantina (3).
  - Popularity rank is not a legibility measure. **L3**
- **Ploni** (AlefAlefAlef foundry page). URL: https://alefalefalef.co.il/font/ploni/ [opened]
  - Commercial, 8 weights (Ultra-Light to Black), released 2018, v2.0.3 November 2020, Hebrew plus Latin and Cyrillic, licences from about 650 NIS per weight. Usable in Canva only by uploading to a Brand Kit with a licence that allows it. [licence terms unverified] **L2 for facts, L3 for "good UI font"**
- **Canva Help Center: Text doesn't display properly** URL: https://www.canva.com/help/text-display/ [opened in browser]
  - Boxes like ☒ or ▯ mean the font does not support your language; the font list has a "Fonts in your language" section; the font search has a language filter. **L2**
  - Which Google Hebrew fonts exist inside Canva was not verified (needs a logged-in Canva). [unverified]
- LumeBook's web tokens already use Heebo (project memory: sites/lumebook-ambassadors/index.html). Heebo is a reasonable default for brand consistency. **L3**

### 3.5 Apple RTL guidance (applies to any RTL layout)

- **Apple HIG: Right to left** (Apple). URL: https://developer.apple.com/design/human-interface-guidelines/right-to-left [opened via JSON endpoint]
  - Hebrew and Arabic have no uppercase, so they can look too small next to uppercase Latin; Apple suggests increasing the RTL font size by about 2 points. **L2**
  - "Align a paragraph based on its language, not on the current context." Mismatched alignment of 3+ line paragraphs is hard to read. **L2**
  - Flip controls that show progress, and next/previous controls for ordered items, to match RTL reading order. **L2**
  - Do not flip photos, illustrations, logos, universal signs, or real-world objects. Do not reverse the digits inside a number; Hebrew uses Western Arabic numerals. **L2**

### 3.6 Mixed Hebrew, Latin, numbers: why punctuation jumps

- **W3C Internationalization: Unicode Bidirectional Algorithm basics** (W3C). URL: https://www.w3.org/International/articles/inline-bidi-markup/uba-basics [opened]
  - Hebrew and Latin letters are strong (fixed direction); digits are weak; spaces and punctuation are neutral and take direction from their neighbours and the paragraph's base direction. If the base direction is LTR, an exclamation mark ending a Hebrew phrase displays on the wrong side. Fix: set the base direction to RTL (in markup) or use direction marks. **L1 (the standard, explained by W3C)**
- Many text engines guess the base direction from the **first strong character** in the paragraph, so a line starting with "LumeBook" can be treated as LTR and push the final period to the wrong side. Example of this exact bug pattern in another app: https://github.com/NuvioMedia/NuvioDesktop/issues/664 [opened via search summary] **L3 anecdote**
- **Canva**: I found no Canva Help article on Hebrew punctuation or bidi bugs. The only RTL feature documented is in Translate: "Mirror page to match text direction to support right-to-left languages." URL: https://www.canva.com/help/translate-canva-designs/ [opened in browser] **L2**
- Workarounds to test in Canva (none verified for Canva specifically) **L4**:
  1. Start every text box with a Hebrew word, never with "LumeBook", a number, a price, or an emoji.
  2. After export, inspect every line end and every number, price, %, date, and Latin word.
  3. If punctuation lands on the wrong side, reword so the line ends in a Hebrew word, or paste a Right-to-Left Mark (U+200F) right after the punctuation.
  4. Write "LumeBook" in Latin only where it is the logo; in running Hebrew text use לומבוק (brand rule in project memory).

### 3.7 Direction and visual preference

- **Chokron, S., De Agostini, M. (2000). Reading habits influence aesthetic preference.** Cognitive Brain Research 10(1-2), 45-49. URL: https://www.researchgate.net/publication/12342946_Reading_habits_influence_aesthetic_preference [abstract via search summary and the 2023 review below]
  - 162 participants, mirror-image pairs: French (LTR) readers preferred pictures with rightward directionality; Hebrew (RTL) readers preferred the leftward version. Landscapes behaved differently. **L1**
- **Fuhrman, O., Boroditsky, L. (2010). Cross-cultural differences in mental representations of time.** Cognitive Science. URL: https://onlinelibrary.wiley.com/doi/10.1111/j.1551-6709.2010.01105.x (PDF: http://language.ucsd.edu/papers/hebrew-time.pdf) [abstract]
  - Hebrew speakers laid out time sequences right to left and answered faster with the right key for earlier events; English speakers the reverse, even with non-linguistic stimuli. **L1**
- **Faghihi, N., Vaid, J. (2023-01-05). Reading/writing direction as a source of directional bias in spatial cognition: possible mechanisms and scope.** Psychonomic Bulletin & Review. URL: https://link.springer.com/article/10.3758/s13423-022-02239-1 [opened in browser, full text]
  - Reviews aesthetic, temporal, agency and number-line biases; calls the effect well documented but malleable. **L1**
  - Reports **Chae & Hoegg (2013), Journal of Consumer Research**: before/after ad images were rated more favourably when congruent with the reader's mental timeline (past left, future right for English readers). In a follow-up with English and Hebrew readers, the patterns reversed: Hebrew readers favoured an antique product shown on the right. **L1 [secondary, original not opened]**
  - Reports **Shaki & Fischer (2008)**: Russian-Hebrew bilinguals flipped their number-line direction depending on which language they had just read. Bias follows recent reading context. **L1 [secondary]**
  - Reports **Maass & Russo (2003)**: Italian vs Arabic readers responded faster to pictures of events moving in their reading direction. **L1 [secondary]**
- Implications for LumeBook slides **(L4, inferred from L1)**:
  - Before/after inside one slide: "before" on the right, "after" on the left.
  - A subject in motion or a child "heading into" the story: facing or moving leftward reads as forward for Hebrew readers.
  - A Hebrew caption context primes RTL; an English-heavy slide could weaken it. Keep slides fully Hebrew.

### 3.8 Instagram's carousel direction in Hebrew: unresolved

- Instagram added Hebrew, Arabic and Farsi UI support on 2017-10-31 (TechCrunch, https://techcrunch.com/2017/10/31/instagram-now-supports-right-to-left-languages-like-hebrew-and-arabic ; Engadget, Rob LeFebvre, same date) [opened]. Neither article says how carousels or swipes behave. **L2**
- Apple's guidance says next/previous navigation through ordered items should flip in RTL (3.5). A well-localised app would therefore advance a carousel leftward in Hebrew UI. Whether Instagram does so: **[unverified]**.
- Two searches found only generic "RTL apps should mirror carousels" advice, nothing Instagram-specific. **L3**
- Required test (5 minutes): open the same carousel on a phone set to Hebrew and on one set to English. Note (a) which way the finger moves to advance, (b) which side the dots fill from, (c) where the "1/7" counter sits. Until then, use direction-neutral cues (see spec sheet). **L4**

---

## 4. Visual hierarchy and cognitive load

### 4.1 Multimedia learning evidence

- **Noetel, M., et al. (2022). Multimedia Design for Learning: An Overview of Reviews With Meta-Meta-Analysis.** Review of Educational Research 92(3), 413-454. URL: https://eric.ed.gov/?id=EJ1338120 [opened abstract]
  - 29 reviews, 1,189 studies, 78,177 participants; 11 principles with positive effects on learning. Largest: captioning second-language video, temporal/spatial contiguity, signalling. Robust evidence also for coherence (removing seductive details) and segmentation. **L1**
  - Caveat in the abstract: good design mattered more for complex material and system-paced settings (lectures) than self-paced ones (websites). A carousel is self-paced and simple, so expect smaller effects. **L1**
- **Alpizar, D., Adesope, O. O., Wong, R. M. (2020). A meta-analysis of signaling principle in multimedia learning environments.** Educational Technology Research and Development. URL: https://link.springer.com/article/10.1007/s11423-020-09748-7 [abstract via search; page redirected to login]
  - Signalling associated with better learning, d = 0.38, with moderators. **L1 [abstract]**
- Translation to a slide **(L1 transfer, so L4 until tested)**:
  - One idea per slide (segmenting).
  - Labels sit next to what they label, not in a legend (spatial contiguity).
  - Signal the 1 to 3 key words with weight or colour, not whole sentences (signalling).
  - Cut decorative elements that compete with the message (coherence).

### 4.2 Colours, whitespace, consistency

- Number of colours: no study found giving a number. "60-30-10" and "max three colours" are **L3**. The binding constraints are contrast (section 2) and BDA's avoid red/green pairing **(L2)**.
- Whitespace: COGA "use white spacing" and BDA "use white space to remove clutter" **(L2)**. No research found on whitespace amount on social images. **L3**
- Consistency: COGA "use a consistent visual design" **(L2)**; distinctive brand assets (section 8) **(L2)**.
- Variety across slides to avoid habituation or "same-looking" fatigue: no evidence found. **L4**

### 4.3 Attention in ads: what captures the eye

- **Pieters, R., Wedel, M. (2004). Attention Capture and Transfer in Advertising: Brand, Pictorial, and Text-Size Effects.** Journal of Marketing 68(2), 36-50. URL: https://www.researchgate.net/publication/228599518_Attention_Capture_and_Transfer_in_Advertising_Brand_Pictorial_and_Text-Size_Effects [abstract via search summary]
  - Eye tracking of magazine ads: brand, pictorial and text elements each have their own attention-capture effects; the brand element best transfers attention to other elements; only increases in the text element's surface size produced a net gain in attention to the ad as a whole. **L1**
  - Transfer: bigger text area pulls attention, which supports large headline type on slide 1. **L4**

### 4.4 Continuity across slides (image running over the edge)

- No peer-reviewed or platform study found on "seamless" or "panoramic" carousels. Vendor blogs (e.g., https://zaps.design/blog/seamless-instagram-carousel-guide , https://postplanify.com/blog/instagram-carousel-guide) claim higher swipe-through, including an uncited "500 e-commerce posts, 2x" figure. **L3**
- **Budiu, R. (2018-08-19). Carousels on Mobile Devices.** NN/g. URL: https://www.nngroup.com/articles/mobile-carousels/ [opened]
  - In-app carousels: dots are weak signifiers and often missed; a partially visible next item is a stronger cue; most users stop after 3 to 4 items; put the best content first. **L2** (app UI carousels, not Instagram posts)
- Instagram's own cue for a feed carousel is "a row of dots below it" (Instagram Help, 2.4), the weak kind in NN/g's terms. **L2**
- Gestalt good continuation is a classic perception principle [not opened this session]. That it makes people swipe is untested. **L4**
- Conclusion: continuity cues are convention plus a plausible mechanism. Worth an A/B-style test (section 10). Keep the crossing element non-essential so slides still work alone (shares and saves show the first slide).

---

## 5. Images

### 5.1 Faces

- **Bakhshi, S., Shamma, D. A., Gilbert, E. (2014). Faces engage us: photos with faces attract more likes and comments on Instagram.** CHI 2014, 965-974. URL: https://www.semanticscholar.org/paper/Faces-engage-us:-photos-with-faces-attract-more-and-Bakhshi-Shamma/4eea0ae045333afdb02e709cf7b7ac99ca88cd73 [abstract]
  - 1 million Instagram photos, controlling for audience: photos with faces were 38% more likely to get likes and 32% more likely to get comments. Observational. **L1**
- **Li, Y., Xie, Y. (2020). Is a Picture Worth a Thousand Words? An Empirical Study of Image Content and Social Media Engagement.** Journal of Marketing Research 57(1), 1-19. URL: https://www.jstor.org/stable/26967290 ; summary by Baylor's Keller Center: https://kellercenter.hankamer.baylor.edu/news/story/2021/using-images-increase-social-media-engagement [summary opened]
  - Faces raised engagement on Twitter but showed **no effect on Instagram**; high-quality, professional images raised engagement consistently; image-text fit mattered on Twitter, not Instagram; colourfulness depended on product category. **L1 (via summary)**
  - The two studies disagree on Instagram faces (different samples and eras). Faces are a reasonable default, not a guarantee.

### 5.2 Product in hands vs faces (purchase intent)

- **Hartmann, J., Heitmann, M., Schamp, C., Netzer, O. (2021). The Power of Brand Selfies.** Journal of Marketing Research 58(6), 1159-1177. URL: https://research.wu.ac.at/en/publications/dde8830d-27f1-4e3f-8381-30edf5e99c48 [abstract opened]
  - Three image types: packshots, consumer selfies (face plus brand), brand selfies (unseen consumer holding the product). Consumer selfies get more likes and comments; brand selfies generate more expressed purchase intentions in comments. **L1**
  - Secondary sources quote +78% (Twitter) and +70% (Instagram) purchase-intent figures; not in the abstract I read. [unverified numbers]
- **Elder, R. S., Krishna, A. (2012). The "Visual Depiction Effect" in Advertising.** Journal of Consumer Research 38, 988-1003. URL: https://ideas.repec.org/a/oup/jconrs/doi10.1086-661531.html [abstract]
  - Four studies: depicting a product so the viewer can mentally simulate using it (e.g., oriented toward the dominant hand) increased purchase intentions. **L1**
- Implication **(L4)**: conversion slides show the open book in hands, from the reader's point of view, pages facing the viewer. Faces fit slide 1 (stopping power).

### 5.3 Gaze direction

- **Sajjacholapunt, P., Ball, L. J. (2014). The influence of banner advertisements on attention and memory: human faces with averted gaze can enhance advertising effectiveness.** Frontiers in Psychology 5:166. URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3941030/ [abstract]
  - Faces gazing toward the product region raised looking at the product and memory for brand and message, compared with direct gaze. **L1**
- **Adil, S., Lacoste-Badie, S., Droulers, O. (2018). Face presence and gaze direction in print advertisements.** Journal of Advertising Research 58(4), 443-455. URL: https://shs.hal.science/halshs-01910205 [abstract]
  - Face present plus gaze toward the product, vs no face or gaze at the viewer: more attention and memorisation, better ad and brand evaluation, higher purchase intention. **L1**
- The widely shared baby eye-tracking heatmap (a blog post circa 2009 by an Australian usability firm) is a demo, not a study. [unverified] **L3**
- Implication **(L4)**: when a child or parent is in frame with text or the book, have them look at the book or toward the headline. A direct-to-camera gaze may still be a stronger thumb-stopper on slide 1; that trade-off is untested.

### 5.4 Real photos vs mockups, illustration vs photo, UGC

- Real photography vs rendered mockups: no peer-reviewed comparison found. Meta advises "Avoid overly photoshopped images" and "Show people using your product or service... in realistic settings" (Meta image ads page, 1.6). Li & Xie found professional quality matters. **L1/L2 for quality, L4 for real vs mockup**
- Illustration vs photo: no direct evidence found. For LumeBook the illustrations are the product, so show them, ideally inside a photographed physical book. **L4**
- **Mayrhofer, M., Matthes, J., Einwiller, S., Naderer, B. (2020). User generated content presenting brands on social media increases young adults' purchase intention.** International Journal of Advertising 39(1), 166-186. URL: https://ucrisportal.univie.ac.at/en/publications/user-generated-content-presenting-brands-on-social-media-increase/ [abstract via search]
  - UGC did not trigger persuasion knowledge and the negative affect that follows, so it produced higher purchase intention than disclosed ads and brand posts. Young adults, not parents. **L1**
- Before/after: see 3.7 (Chae & Hoegg). Across slides, "earlier slide = before" works regardless of screen direction. **L1 transfer / L4**

---

## 6. Data visuals: lists, tables, quotes, diagrams

- **Nielsen, J. (1997). Concise, SCANNABLE, and Objective: How to Write for the Web.** NN/g. URL: https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/ [search summary]
  - Concise text +58% usability, scannable layout +47%, objective language +27%, all three +124%. **L2**
- **Loranger, H. (2017-04-09). 7 Tips for Presenting Bulleted Lists in Digital Content.** NN/g. URL: https://www.nngroup.com/articles/presenting-bulleted-lists/ [opened]
  - Use lists for 3+ related items; similar item lengths; parallel phrasing; numbers only for sequences or counts; no repeated lead words; a clear lead-in; avoid nested lists; do not overuse. **L2**
- **Schade, A. (2017-09-17). Mobile Tables.** NN/g. URL: https://www.nngroup.com/articles/mobile-tables/ [opened]
  - On narrow screens only about 2 columns of complex data fit legibly; items must be legible without zoom. **L2**. On a static slide that cannot scroll: 2 to 3 columns, about 5 rows maximum. **L4**
- BDA: flow charts are ideal for procedures; pictograms help locate information (2.6). **L2**
- Diagrams: put labels on or beside the parts (spatial contiguity, 4.1). **L1 transfer**
- Quotes and reviews: no study on quote formatting found. UGC evidence (5.4) supports real customer words with name and city. **L1 transfer / L4**
- Numbers: keep digits LTR, never reverse (Apple RTL, 3.5). Check prices like ₪149 and ranges like 3-8 in the exported PNG. **L2**

---

## 7. Last slide and CTA

- **Google, YouTube ABCD reference guide** (Think with Google, undated). URL: https://services.google.com/fh/files/misc/youtube_google_abcd_reference_guide_en.pdf [opened]
  - Based on more than 5,000 TrueView in-stream ads, explicitly correlational ("does not guarantee future performance"). A strong CTA is specific about what to do ("visit site", "sign up", "buy now"); making it both visible and audible helps; "limited" offers work well. **L2 (video ads)**
- **Meta overlay guidance** (1.6): one message, one CTA. **L2**
- **Choice overload context**: Chernev, A., Böckenholt, U., Goodman, J. (2015). Choice overload: A conceptual review and meta-analysis. Journal of Consumer Psychology 25, 333-358. URL: https://myscp.onlinelibrary.wiley.com/doi/abs/10.1016/j.jcps.2014.08.002 [abstract via search]. Scheibehenne et al. (2010) found a mean effect near zero; Chernev et al. found overload when sets are complex, tasks difficult, preferences uncertain, or there is no clear goal. **L1**. So "one CTA" is justified by clarity and Meta/Google guidance, not by a strong choice-overload effect.
- **Button shapes on a static image**:
  - **Moran, K. (2017-09-03). Flat UI Elements Attract Less Attention and Cause Uncertainty.** NN/g. URL: https://www.nngroup.com/articles/flat-ui-less-attention-cause-uncertainty/ [opened]. 71 participants: weak signifiers cost 22% more time and 25% more fixations; strong button styling is read as clickable. **L2**
  - On a static slide a button shape is therefore a false affordance: people may tap it and nothing useful happens. Whether that hurts or helps conversion is unknown. **L4**
  - If used, the shape needs 3:1 against the background and its label 4.5:1 (WCAG 1.4.11 and 1.4.3). **L1**
- Placement: no evidence on CTA position within a slide. Keep it inside the safe zone and away from the bottom band (section 9). **L2/L3**
- Caption repetition: putting the image's key text and the CTA in the caption is accessibility guidance (NSW, 2.4) **(L2)**; as a conversion tactic it is **L3**.
- Mechanics: Instagram feed captions do not have clickable links, hence "link in bio" or comment-keyword-to-DM flows. [not verified this session] **L3**

---

## 8. Branding

- **Teixeira, T. S., Wedel, M., Pieters, R. (2010). Moment-to-Moment Optimal Branding in TV Commercials: Preventing Avoidance by Pulsing.** Marketing Science 29(5), 783-804. URL: https://ideas.repec.org/a/inm/ormksc/v29y2010i5p783-804.html ; HBS Working Knowledge summary, Julia Hanna, 2010-06-07: https://www.library.hbs.edu/working-knowledge/improving-brand-recognition-in-tv-ads [summary opened]
  - Eye tracking, about 2,000 viewers, 31 commercials: long, prominent brand exposure increases zapping; brief, intermittent "pulsing" of the brand reduced zapping by 8 to 10% on average (up to 25%). **L1 (TV)**
- **Google ABCD** (section 7): introduce brand or product in the first five seconds; logo as a persistent watermark in brand colours supports consideration. **L2 (video, correlational)**
- **Meta image ads** (1.6): "Show your brand or logo: People engage more with brands they know." **L2**
- **Pieters & Wedel (2004)**: the brand element transfers attention to the rest of the ad. **L1**
- **Distinctive brand assets (Romaniuk, Ehrenberg-Bass Institute)**: assets (colour, logo, character, font) are judged on fame (share of category buyers linking it to the brand) and uniqueness (share linking it only to you). Framework summary: https://www.distinctivebat.com/blog/distinctive-brand-asset-grid/ [secondary]. Book: Romaniuk, J. (2018), Building Distinctive Brand Assets, Oxford University Press [not opened]. **L2 (marketing science)**
- **Carroll, N. (2025-07-23). Marketers' judgement of brand asset strength "rarely accurate", study finds.** Marketing Week, reporting Brus, Hartnett, Faulkner, Driesener (Ehrenberg-Bass) in Journal of Brand Management. URL: https://www.marketingweek.com/marketers-judgement-strength-brand-assets-rarely-accurate/ [opened]
  - Marketers overestimate how famous their assets are and underestimate uniqueness; use consumer checks, deploy assets consistently. **L2 [secondary report of a peer-reviewed paper]**
- Static carousels specifically: no evidence found on how much branding helps or hurts. Inference: a small, constant brand mark on every slide (the static analogue of pulsing) plus fixed colours and font, rather than a big logo on slide 1. **L4**

---

## 9. Instagram UI: sizes, overlays, grid crop

- **Instagram Help: Image resolution of photos** URL: https://help.instagram.com/1631821640426723 [opened in browser 2026-10-06]
  - Stored up to 1080 px wide; aspect ratios from 1.91:1 to 3:4 are kept (1080 x 566 to 1080 x 1440); other ratios are cropped; wider uploads are downsized to 1080. **L2**
- **Instagram Help: carousel** (2.4): up to 20 items; one orientation for all; the feed shows the first item "with a row of dots below it" (dots sit below the image, not on it); on the profile the first item shows a carousel icon top right. **L2**
- **Profile grid 3:4**: the grid switched to 3:4 vertical tiles in January 2025, announced by Adam Mosseri (Planoly, updated 2025-04-03: https://www.planoly.com/blog/instagram-updates-jan-2025 ; Tribune 2025-01-20). [secondary; Mosseri's own post not opened] **L2**
  - Crop math [derived]: a 1080 x 1350 (4:5) cover shown at 3:4 keeps a central 1012 px width, losing about 34 px per side. A 1:1 post loses 135 px per side. A 1080 x 1440 (3:4) post is not cropped.
  - An "Adjust preview" control for the grid tile is reported by https://www.igcompressor.com/blog/instagram-grid-3-4-size-explained [secondary, unverified].
- **Meta: text overlays and safe zone** (1.6) [opened]: for Instagram Feed ads in 1:1 or 4:5, keep the bottom and side edges free of key creative elements, text and logos (profile icon, CTA). **L2 (ads; organic UI is similar but not identical)**
- In-image overlays on organic posts (slide counter top corner, tag icon bottom-left when people are tagged, product tags, music label) are not documented in the Help Center pages I read. Vendor "safe zone" guides give inconsistent pixel numbers and some describe UI that sits outside the image. **L3**
- Required device check **(L4)**: post a test carousel to a private test account (or screenshot the share preview) on a Hebrew-UI and an English-UI phone; mark where the counter and tag icon land; confirm the 1080 x 1440 upload stays uncropped through the carousel flow.

---

## 10. Hypotheses worth testing (L4)

Solo SMM reality: Instagram does not offer A/B tests for organic carousels, so alternate variants across comparable posts and compare saves, shares, profile visits and link taps per reach. Run each test for at least 4 to 6 posts per arm before reading anything into it.

1. Cover with a child's face looking at the book vs looking at camera (stop rate proxied by reach from non-followers and swipe-through if Insights shows it).
2. In-image swipe cue (partial element entering from the side where the next slide appears) vs no cue, after the RTL direction test.
3. Hands-plus-open-book POV photo vs flat mockup on the "here is the product" slide.
4. Button-shaped CTA vs plain instruction line ("הקישור בביו", or a comment keyword) on the last slide.
5. Before/after: right-to-left order vs left-to-right order inside one slide.
6. Small persistent logo on every slide vs logo only on first and last slides.
7. 3:4 (1080 x 1440) vs 4:5 (1080 x 1350) canvas.
8. Text-heavy slide (35 to 45 words) vs lean slide (15 to 25 words) with the same message.

---

## 11. Canva spec sheet (one-page)

Tag key: L1 research/standard, L2 practitioner, L3 convention, L4 hypothesis. "derived" = calculated from the cited source.

**Canvas**
- Size: 1080 x 1440 px (3:4) as first choice: the tallest ratio Instagram keeps, no grid crop. Confirm in the upload preview that it is not cropped. Fallback: 1080 x 1350 (4:5). All slides in one post must share the ratio. [L2 Instagram Help; L4 for "taller performs better"]
- Export: PNG, at 1080 px wide. [L3]

**Safe margins**
- Sides: 96 px each (covers the 34 px grid crop on 4:5 plus breathing room; Meta says keep side edges clear). Text column 888 px. [L2 Meta + derived; exact px L3]
- Top: 96 px. Bottom: 144 px kept free of text and logos (Meta bottom-edge guidance; tag icon area). [L2/L3]
- Cover slide: keep the headline inside the central 1012 x 1350 area even on 3:4, so a later switch to 4:5 cannot clip it. [derived]
- Use an 8 px grid for all spacing (96, 144, 48, 24). [L3; matches brand tokens]

**Font**
- Heebo (brand font, Google Fonts). Alternatives: Assistant, Rubik, Noto Sans Hebrew, IBM Plex Sans Hebrew; Ploni only if licensed and uploaded. One family per carousel. [L3]
- Weights: Regular or Medium for body; Bold or Black for headlines. Never Thin, ExtraLight or Light. [L2 Apple; L1 WCAG note on thin strokes]
- Check ד/ר, ה/ח/ת, ו/ז/ן at body size in the exported PNG. [L4]

**Minimum sizes (Canva font size on the 1080-wide canvas; calibrate first, see 1.2)**
- Cover headline: 110 px minimum, 120 to 150 typical (legible as a profile-grid tile). [L2 derived]
- Slide headline: 72 px minimum (WCAG large-text threshold at a 360 pt screen), 80 to 96 typical. [L1/L2 derived]
- Body: 48 px absolute floor (16 pt at 360 pt), **56 px default** (17 pt body + Hebrew correction). [L2 derived]
- Footnote, source, small print: 36 px floor (12 pt at 360 pt); never below 33 px (Apple 11 pt). Prefer moving small print to the caption. [L2 derived]
- Headline at least 1.2 x body (BDA); in practice 1.4 to 2 x for clear hierarchy. [L2; ratio above 1.2 is L3]
- If an uppercase Latin word sits next to Hebrew, make the Hebrew about 2 pt larger (about 6 px) or set the Latin in sentence case. [L2 Apple RTL]

**Spacing**
- Body line spacing 1.4 to 1.5 (Canva "line spacing"; check what the number means in Canva). [L1 WCAG 1.4.8 AAA; L2 BDA]
- Headline line spacing 1.1 to 1.25, only for 1 to 2 lines. [L2 Apple leading guidance]
- Space between paragraphs or list items at least 1.5 x the line spacing. [L1 WCAG 1.4.8]
- Letter spacing: default to slightly positive for body; do not track Hebrew widely, test. [L2 BDA; L4 for Hebrew]

**Text amount**
- One idea per slide. [L1 transfer (segmenting); L2 COGA, Meta]
- Headline: up to about 8 words, at most 2 lines. [L3/L4]
- Body: up to about 25 words, at most 4 lines per block, at most 2 blocks; whole slide about 35 words maximum. [L3/L4; consistent with what fits at 56 px]
- Line length: falls naturally at about 30 to 35 Hebrew characters; never above 60 to 70. [L2 BDA ceiling; L1 WCAG 80 ceiling; derived]
- Lists: 3 to 5 parallel items, one line each, no nesting. [L2 NN/g]
- Tables: 2 to 3 columns, about 5 rows. [L2 NN/g derived; L4]
- Reading level: everyday words, short active sentences, ktiv male, no niqqud except for ambiguity. [L2 NN/g, BDA; L1 Weiss 2015; L4 rule]

**Contrast checks (every slide, on the exported PNG)**
- Body and small text: at least 4.5:1; aim 7:1. [L1 WCAG 1.4.3; 7:1 is L1 AAA / L2 NSW]
- Headlines 72 px+ regular or 56 px+ bold: at least 3:1, but aim 4.5:1. [L1 derived]
- CTA shape and any meaningful arrow or icon: at least 3:1 against its background. [L1 WCAG 1.4.11]
- Never: gold #E6B762 or #C9954A text on cream or white; white text on gold. Gold text only on ink. [L1 derived]
- Text on photos: at least 60% ink or black scrim (65% for cream text), or a solid box; sample the lightest pixel behind the text. [L1 derived; L2 NN/g]
- Do not mark the key word by colour alone: colour plus weight. [L2 W3C low vision, BDA]
- Tool: any WCAG contrast checker with an eyedropper on the exported PNG. [L2]

**RTL checks (every slide, on the exported PNG)**
- Hebrew body right-aligned, ragged left; never justified; centred only for 1 to 2 line headlines. [L1 WCAG 1.4.8; L2 BDA, Apple]
- Every text box starts with a Hebrew word (not "LumeBook", a number, a price or an emoji). [L1 bidi mechanism; L4 Canva behaviour]
- Check end punctuation, prices (₪), percentages, dates, ranges and Latin words for flipped order; fix by rewording or an RLM (U+200F). [L1 Unicode bidi; L4 Canva]
- In Hebrew text write לומבוק; Latin "LumeBook" only as the logo. [project brand rule]
- Do not mirror photos, illustrations or the logo. [L2 Apple]
- Before/after inside one slide: before on the right, after on the left. [L1 transfer; L4]
- Subjects face or move leftward when they should feel "forward". [L1 transfer; L4]
- Swipe cue: until the Hebrew-UI test is done, use a direction-neutral cue ("החליקו", "1/7", a partial element peeking in). After the test, point arrows the way the next slide actually enters. [L4]

**Images**
- Slide 1: a real face (child or parent) plus the headline; faces looking at the book or headline. [L1 Bakhshi; L1 gaze studies; Li & Xie null on Instagram]
- Product slides: the real book held in hands, POV, pages toward the viewer. [L1 Hartmann; L1 Elder & Krishna]
- Proof slides: real customer photos and words (with permission). [L1 Mayrhofer]
- High-quality, well-lit, not over-retouched photos. [L1 Li & Xie; L2 Meta]
- No busy photo behind body text; use a solid cream or ink panel. [L2 BDA, NN/g]

**Branding**
- Small logo or wordmark on every slide, same position (inside the top margin, not the bottom band). [L1 Teixeira pulsing, by analogy, so L4; L2 Google ABCD watermark]
- Same 2 to 3 brand colours (ink, cream, gold) and Heebo on every carousel. [L2 Romaniuk distinctive assets; L2 COGA consistency]

**Last slide**
- One CTA, verb first, specific: e.g., "צרו תצוגה מקדימה בחינם". [L2 Google ABCD, Meta]
- Say where to act (link in bio, or a comment keyword), because the image is not clickable. [L3]
- Button-shaped graphic: optional and to be tested; if used, 3:1 shape contrast and 4.5:1 label. [L4; L1 for contrast]
- Repeat the CTA in the first caption line and repeat the slides' key text in the caption. [L2 NSW accessibility; L3 conversion]

**Accessibility per post**
- Alt text per slide in Instagram's Accessibility settings (confirm each slide has its own field). [L2 Instagram Help; per-slide unverified]
- Camel-case hashtags; at most one emoji per spot, at line ends, never as the only carrier of meaning. [L2 NSW; L1 Tigwell]

**Final QA**
- View on the smallest phone available, at arm's length, in bright light. [L4]
- View slide 1 at one-third width (grid size): can you read the headline? [derived]
- Run the Hebrew-UI vs English-UI swipe-direction check once and record the result in the project notes. [L4]

---

## 12. Gaps and what I could not verify

- Instagram carousel swipe direction and in-image overlays (counter, tag icon) in Hebrew UI: not documented anywhere I could find.
- Canva's font-size unit and its handling of bidi punctuation: no Canva documentation found; Canva's help pages block plain fetches, read via browser.
- Hebrew-specific font legibility research: none found.
- Any evidence on words per slide, number of colours, whitespace amounts, seamless carousels, real-vs-mockup photos, or illustration-vs-photo for social posts.
- WCAG SC 1.4.6 (AAA 7:1) page and Mosseri's own grid announcement were not opened.
- Pieters & Wedel (2004), Chae & Hoegg (2013), Alpizar et al. (2020), Mayrhofer et al. (2020): abstracts or reviews only.
