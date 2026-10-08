# Claude Code prompt for LumeBook hook strategy research

You are working in the LumeBook repository at:

`/Users/yarinbruner/Claude/Projects/Lumebook`

Your task is to research and strengthen the hook strategy used by LumeBook’s nightly Instagram carousel pipeline.

## Context

LumeBook sells personalised children’s books. A parent uploads a photo and name and the child becomes the hero of the story.

Every night the pipeline creates six Hebrew carousel options about one real parenting moment:

- 3 `kid` options where the child speaks to the parents
- 3 `expert` options with a plain-language sourced insight
- exactly 7 slides per option
- a different Israeli child name and hook formula for every option
- slides 1–6 provide value without selling
- only slide 7 introduces a personalised story and the comment-word CTA
- the system never chooses the final winner
- nothing is posted and no paid service is called

Hebrew must remain natural, spoken and RTL. Audience-facing Hebrew cannot contain commas, periods or em dashes.

## Start by inspecting the existing system

Read at least:

- `carousel/carousel-pipeline/hook-bank.md`
- `carousel/carousel-pipeline/README.md`
- `carousel/carousel-pipeline/scripts/carousel_lib.py`
- `carousel/carousel-pipeline/scripts/nightly.py`
- `carousel/carousel-pipeline/scripts/validate_pack.py`
- `carousel/carousel-pipeline/pack.schema.json`
- `carousel/carousel-pipeline/history.json`
- `docs/lumebook-instagram-carousel-playbook-he.md`
- `research/carousel-playbook-research/platform.md`
- `research/carousel-playbook-research/psych.md`
- `research/carousel-playbook-research/market.md`
- recent packs under `carousel/carousel-pipeline/drafts/`

Preserve all existing product, sourcing, voice, rotation and validation rules unless the research gives a documented reason to improve them.

## Research question

Which current social-media hook structures are most likely to stop Israeli parents, create an honest reason to swipe and attract the right audience for LumeBook?

Research Instagram carousels first. You may examine TikTok, Reels, Threads or other platforms only when the hook structure clearly transfers to a static carousel.

Focus on:

- Israeli parenting content
- international parenting and child-development creators
- personalised children’s books and children’s gift brands
- emotionally specific parenting moments
- hooks that feel current now
- hooks that generate relevant attention rather than empty engagement
- slide 2 hooks because Instagram may resurface a carousel from its second slide

## Evidence standards

Do not describe a hook as “proven” merely because it is popular or appears in a high-performing post.

Use these evidence labels:

1. `platform_supported`  
   Supported by current first-party Instagram or Meta guidance

2. `external_performance_pattern`  
   Repeated in several relevant posts with visible performance evidence

3. `current_trend`  
   Appearing repeatedly in recent content but not proven to cause performance

4. `research_supported_mechanism`  
   Supported by credible behavioral, attention or communication research

5. `lumebook_hypothesis`  
   A promising adaptation that still requires LumeBook testing

6. `lumebook_validated`  
   Allowed only when LumeBook’s own results support it

Keep “trendy,” “frequently observed,” “high-performing” and “caused better performance” separate.

For every factual claim preserve:

- source title
- source URL
- publication date when available
- access date
- a short verbatim supporting quote or the exact observed data
- evidence label
- limitations

Prefer first-party platform sources, original research and directly inspected posts. Do not rely on generic marketing blogs when the original source is available.

Never invent post metrics, private saves, private shares, reach or conversion data. If Instagram blocks access, document the limitation and continue with the evidence that can actually be verified.

## Current-content sample

Build a documented sample of recent relevant social posts, prioritising the last 90 days and expanding to 12 months only when necessary.

Aim for diversity across:

- Israeli parenting creators
- child-development professionals
- international parenting creators
- children’s book and personalised gift brands
- small and large accounts

For each usable example record:

- account
- URL
- post date
- platform and format
- exact visible hook
- slide 2 hook when available
- hook family
- parenting moment
- emotional mechanism
- curiosity question opened
- where the post answers it
- visible metrics
- account size when verifiable
- why it may or may not transfer to LumeBook
- evidence label

Do not rank posts by raw likes alone. Account size, post age, format and audience differ. Treat visible engagement as observational evidence, not proof of conversion.

## Identify the strongest hook strategies

Look for recurring structures such as:

- a highly specific parent-child moment
- a believable child quote
- the child’s imagined inner voice
- a parent’s private worry in their own words
- a gentle counterintuitive reframe
- a practical question tied to an age
- “what to say instead”
- a numbered set of small actions
- a seasonal or developmental moment
- tension between what the parent sees and what the child may feel
- a concrete desired outcome without an unrealistic promise
- a confession or normalisation that reduces parental shame
- a story opening with an unresolved moment

Do not assume these categories are correct. Add, merge or reject them according to the evidence.

Reject hook styles that depend on:

- parental shame
- fearmongering
- fake urgency
- fabricated child speech
- medical or developmental certainty
- “you are doing it wrong”
- “the secret”
- “you won’t believe”
- claims that the carousel does not answer
- broad relatable-parent humour with no connection to LumeBook’s audience or product

## Produce a hook strategy

For every recommended hook family provide:

- stable machine-readable ID
- Hebrew name
- eligible direction: `kid`, `expert` or `both`
- Hebrew template with slots
- 3 natural Hebrew examples
- the parenting moments it fits
- the emotional mechanism
- the exact open question
- the slide where that question should be answered
- a compatible standalone slide 2 move
- evidence label
- supporting sources or examples
- likely audience intent
- risks and prohibited uses
- signs that the formula is becoming stale
- variables worth testing

Every Hebrew example must follow LumeBook’s voice rules and read naturally in Israeli Hebrew. Do not translate American hook formulas literally.

## Nightly hook slate

Design a practical method the nightly pipeline can use before writing the six complete carousel options.

For each nightly topic it should generate a private working slate of:

- 6 `kid` hook candidates
- 6 `expert` hook candidates
- several genuinely different hook families
- at least one strong standalone slide 2 hook for each candidate

Score each candidate from 0–2 on:

- stopping power
- specificity
- parent relevance
- honest curiosity
- emotional truth
- swipe promise
- usefulness
- fit with the selected topic
- fit with LumeBook
- freshness compared with recent history

A hook must fail if it contains clickbait, an unsupported claim, a promise the carousel does not fulfil or language that blames the parent.

Use the slate to construct three diverse `kid` options and three diverse `expert` options. Do not announce a winner or recommend which final carousel Yarin should choose.

## Diversity and rotation rules

The six final options must not be cosmetic rewrites of one another.

Create rotation rules covering:

- hook formula
- hook family
- emotional mechanism
- sentence shape
- awareness stage
- slide 2 move
- topic and seasonal moment
- recently used wording

Avoid repeating a formula too soon, but do not force a weak hook merely to satisfy rotation.

Make trend-sensitive hooks expire or require revalidation. Store the research date and evidence status so an old trend is not treated as permanently current.

## Measurement plan

Define how LumeBook can learn what actually works without pretending that external trends prove conversion.

Use LumeBook metrics when available, prioritising:

- comments containing the CTA word per 1,000 reached accounts
- preview visits per 1,000 reached accounts
- preview completions
- purchases
- sends per reach
- saves per reach
- profile visits per reach
- non-follower reach

Recommend a repeated testing method that:

- changes one main hook variable at a time
- repeats a hook family across several comparable posts
- records topic, timing, CTA and audience differences
- requires enough observations before promoting a formula to `lumebook_validated`
- never automatically declares a winner from one post

Do not invent thresholds when the current data cannot support them. Mark proposed thresholds as hypotheses.

## Deliverables

Create:

1. `carousel/carousel-pipeline/research/hook-strategy-YYYY-MM-DD.md`  
   The complete research report, evidence table, current examples, limitations and recommendations

2. An updated `carousel/carousel-pipeline/hook-bank.md`  
   Preserve useful existing formulas, improve weak ones and add only evidence-backed or clearly labelled experimental formulas

3. Any minimal changes needed so the nightly pipeline can use the improved bank, scoring, evidence labels and rotation rules

4. Updated validation and tests covering the new rules

5. A short changelog explaining:

   - what changed
   - what was preserved
   - which hooks are current trends
   - which are research-supported
   - which remain LumeBook hypotheses
   - what LumeBook must measure before calling anything proven

## Verification

Run the existing test suite and validation tools.

Then generate one sample hook slate for a single parenting topic and verify that:

- it contains 6 `kid` and 6 `expert` candidates
- the candidates are structurally different
- every curiosity gap is honestly closed
- slide 2 works as an independent opening
- Hebrew passes all punctuation and voice rules
- no hook sells the product
- no hook contains an unsupported factual claim
- the resulting six carousel options can still satisfy the existing pack schema
- no paid API is called
- nothing is posted

Do not weaken an existing safeguard merely to make validation pass. If research conflicts with an existing rule, document the conflict and make the smallest justified change.
