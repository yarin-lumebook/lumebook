# Claude Code prompt for daily games and books carousels

You are working in the LumeBook repository at:

`/Users/yarinbruner/Claude/Projects/Lumebook`

Extend the nightly carousel pipeline with two additional complete carousels every day:

1. Best games for a developmental stage
2. Best books for a developmental stage

These are additional carousels. Do not replace or weaken the existing `kid` and `expert` carousel system.

## Goal

Every nightly run should produce:

- one games recommendation carousel
- one books recommendation carousel
- each carousel focused on one useful developmental stage, age range or skill
- recommendations that are genuinely popular and available in Israel
- the exact name of every game or book
- a short explanation of why it is valuable for that developmental stage
- a real product or cover image placed in the center of each recommendation slide
- a natural LumeBook mention on the penultimate slide

Do not use image generation or paid APIs for these carousels.

## Inspect the existing project first

Read the existing pipeline, schemas, review pages, renderers, tests, history and Hebrew voice rules before changing anything.

Preserve the current nightly carousel flow and add these two formats in the smallest compatible way.

## Developmental-stage selection

Choose a specific age range and developmental need for each carousel.

Possible areas include:

- language and vocabulary
- fine motor skills
- gross motor skills
- imagination
- early literacy
- problem solving
- memory
- emotional understanding
- turn-taking
- cooperation
- independence
- attention and self-regulation
- early numeracy

Do not treat age boundaries as exact or claim that every child develops at the same pace.

Use reliable child-development sources such as:

- American Academy of Pediatrics
- CDC developmental milestones
- ZERO TO THREE
- Child Mind Institute
- KidsHealth
- original research when necessary

Every developmental claim must have a source.

Use careful wording such as “lets children practise,” “can support” or “creates an opportunity for.” Do not claim that a product guarantees development, treats a difficulty or makes a child smarter.

## Israel popularity requirement

The most important selection rule is that every recommended game and book must be popular or clearly established in Israel.

Do not infer Israeli popularity from international popularity.

Look for Israel-specific evidence such as:

- current Israeli bestseller lists
- Israeli bookstore rankings
- prominent placement at major Israeli retailers
- availability across several independent Israeli retailers
- Hebrew editions from established publishers
- repeated recommendations from credible Israeli parenting, education or library sources
- visible Israeli review volume
- sustained Israeli social-media attention

Useful sources may include major Israeli bookstore chains, toy retailers, publishers, libraries and credible local parenting or education sources.

Avoid affiliate listicles, copied recommendation pages and unsupported “best of” claims.

Use the label `popular_in_israel` only when there is:

- one strong Israel-specific ranking or sales signal, or
- at least two independent Israel-specific popularity signals

If an item is merely stocked locally, label it `available_in_israel`, not popular.

For every candidate record:

- exact Hebrew and original title
- author and publisher for books
- manufacturer for games
- recommended age from the official product source
- Israeli availability
- Israeli popularity evidence
- developmental relevance
- source URLs
- access date
- image source
- confidence level
- any limitations

Never invent sales, rankings, reviews or popularity.

## Recommendation standards

Prioritise products that are:

- currently available in Israel
- age appropriate
- easy for an Israeli parent to identify and buy
- still culturally relevant
- useful beyond a single play session
- visually recognisable
- suitable for a recommendation without a paid relationship

For books, prefer a Hebrew edition when one exists.

For games, prefer Hebrew instructions or language-independent play.

Exclude:

- unavailable or discontinued products
- products supported only by an international trend
- unsafe products
- products whose age recommendation conflicts with the carousel
- paid placements presented as editorial recommendations
- products selected only because an image is easy to find
- several nearly identical recommendations in one carousel

Do not imply that LumeBook has tested or endorsed a product unless that is documented.

## Carousel structure

Each carousel must contain exactly 7 slides.

### Slide 1: Hook

Name the developmental stage, parent need or age range.

The hook should be specific and useful, not clickbait.

Do not name LumeBook here.

### Slide 2: Selection frame

Briefly explain what children are practising at this stage and what makes a game or book suitable.

Use plain spoken Hebrew and avoid therapy jargon.

### Slides 3–5: Recommendations

Recommend one exact game or book per slide.

Each recommendation slide must contain:

- exact product title
- appropriate age range
- real product or cover image centered on the slide
- one concise explanation of why it is valuable
- one practical detail about how a parent and child can use it

Do not write vague lines such as “great for development.”

Explain the actual activity, for example matching, retelling, taking turns, naming feelings, predicting, building, sorting or planning.

### Slide 6: Natural LumeBook integration

The penultimate slide must always include LumeBook in a nonchalant way.

Present it as one more relevant option connected to the same developmental need, not as a sales interruption.

The slide may explain that a personalised story in which the child is the hero can create another opportunity to practise the same skill, discuss the same feeling or engage with books.

Rules:

- mention LumeBook only once
- keep the tone editorial and relaxed
- do not use urgency, discounts or exaggerated promises
- do not claim that personalisation guarantees a developmental result
- use an existing approved LumeBook image or real preview asset
- do not generate a new image
- keep the product connection relevant to the carousel’s developmental theme

### Slide 7: Useful close

Finish with a useful summary and a light save, share or comment prompt.

Do not turn this slide into another sales slide.

## Image rules

Do not generate images.

Use real images of the recommended books and games from authoritative sources such as:

- the publisher
- the manufacturer
- an official product page
- an established Israeli retailer

Do not take images from Google Images or an unattributed repost.

For every image:

- preserve the original aspect ratio
- do not distort or aggressively crop the product
- place it prominently in the center of the slide
- keep text above and below the image
- use the highest-quality verified source available
- save the original source URL and access date
- record whether publication rights are clear

An image being online does not automatically mean it is cleared for reuse. If usage rights cannot be established, flag the image as `rights_unverified` in the review page instead of pretending the carousel is publish-ready.

For LumeBook, reuse approved assets already present in the repository or taken from the verified live site.

## Hebrew and RTL

All audience-facing copy must:

- be written in natural spoken Israeli Hebrew
- render RTL correctly
- contain one thought per line
- avoid commas, periods and em dashes
- avoid literal translations of English marketing language
- speak to mom or both parents and never specifically to dad
- avoid parental blame
- avoid fake certainty
- avoid medical or therapeutic claims

Research notes and metadata may use normal punctuation. The punctuation restriction applies to audience-facing carousel copy.

## Rotation

Maintain history so the pipeline does not repeatedly recommend the same:

- developmental stage
- age range
- skill
- game
- book
- author
- publisher
- manufacturer
- hook structure

Do not repeat the same product within 30 days unless there is a documented seasonal reason.

Rotate across different types of play and reading experiences rather than producing nearly identical lists.

## Review page

Add both new carousels to the nightly review page.

For every recommendation show:

- slide preview
- exact title
- age range
- developmental reason
- popularity evidence
- availability evidence
- factual sources
- image source
- image-rights status
- confidence level
- editable Hebrew copy

Clearly flag:

- missing Israeli popularity evidence
- weak developmental sourcing
- incorrect age fit
- unavailable products
- missing images
- unverified image rights
- repeated products
- unsupported claims
- Hebrew voice violations

Do not automatically post anything.

## Validation

The validator must refuse to mark a carousel valid unless:

- there are exactly 7 slides
- slide 6 contains the natural LumeBook integration
- LumeBook does not appear on slides 1–5 or slide 7
- slides 3–5 contain exact product names
- every recommendation has Israel-specific availability evidence
- every `popular_in_israel` claim has sufficient evidence
- every developmental claim has a credible source
- every recommendation has a real image and source URL
- image-rights status is recorded
- all audience-facing Hebrew passes the existing voice and punctuation rules
- no medical, developmental or commercial claim is unsupported
- no paid API was called
- no image was generated
- nothing was posted

## Files and implementation

Create the smallest maintainable extension to the existing system.

Add or update:

- schemas for the two new carousel types
- nightly generation instructions
- product and recommendation history
- source metadata
- review-page rendering
- slide rendering
- validation
- tests
- documentation

Store the daily outputs alongside the existing nightly draft using clear names such as:

- `games-carousel.json`
- `books-carousel.json`
- their rendered review assets

Do not break existing packs or historical drafts.

## Verification task

Generate one example games carousel and one example books carousel for the same age range.

Verify that:

- every recommendation is identifiable by exact name
- every recommendation is currently available in Israel
- popularity claims are supported rather than assumed
- the developmental explanation is specific and sourced
- every recommendation uses a real centered product image
- slide 6 includes LumeBook naturally
- slide 7 remains useful rather than promotional
- the Hebrew is natural and RTL
- all validation and existing tests pass

At the end report:

- files changed
- sources used
- games and books selected
- evidence that they are popular in Israel
- any image-rights limitations
- tests and validation results
- anything that still requires human review
