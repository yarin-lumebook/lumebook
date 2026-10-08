# Claude Code master prompt for the LumeBook nightly carousel pipeline

Paste this prompt into Claude Code from the LumeBook project folder

```text
Build and finish a reliable semi automatic LumeBook Instagram carousel pipeline in this project

Work autonomously inside this repository
Inspect what already exists before creating anything
Extend or repair existing files instead of duplicating them
Do not stop at a plan
Implement the pipeline and verify it end to end with a no cost test run

Project folder
/Users/yarinbruner/Claude/Projects/Lumebook

Core outcome

Every day at 22:00 Asia Jerusalem create one review pack for the following morning
The pack must contain exactly six complete Hebrew carousel candidates around one selected brand topic

Direction one
The child tells the parents what the situation feels like from the child point of view and what may sit behind the visible behavior
Create three genuinely different versions

Direction two
An expert offers a clear useful and evidence based take on the same topic
Create three genuinely different versions

Each version must include

1  A title and strategic angle
2  The target parent and awareness stage
3  Eight complete slides
4  Final Hebrew copy for every slide
5  A production ready image description for every slide
6  A finished Instagram caption
7  One CTA only
8  Source links for factual claims
9  A short reason this version may convert

Do not generate paid images during the nightly run
The nightly result is for human review editing and selection

Read these project files first

carousel/carousel-pipeline/README.md
carousel/carousel-pipeline/voice-profile.md
carousel/carousel-pipeline/topic-bank.md
carousel/carousel-pipeline/pack.schema.json
docs/lumebook-product-brief.md
docs/lumebook-instagram-carousel-playbook-he.md
docs/hebrew-voice-tool.md
.claude/skills/lumebook-carousel/SKILL.md

Also inspect recent output under carousel/carousel-pipeline/drafts so topics hooks and code words are not repeated too soon

Voice system

Natural everyday Israeli Hebrew is the highest priority
The writing must sound like Yarin speaking and not like translated English a therapist a parenting guru or polished brand copy

Use the best free Claude Code setup for this

1  Turn the current project skill into a dedicated version controlled Hebrew voice skill or add a focused voice layer inside it
2  Use Anthropic official skill creator plugin to create and evaluate the skill if it is installed
3  If it is not installed explain the exact official installation step but continue building the local skill
4  Ground the skill in real approved writing samples from carousel/carousel-pipeline/voice-profile.md
5  Add folders for approved and rejected Hebrew examples
6  Never pretend the voice is calibrated if fewer than 15 authentic samples exist
7  When samples are missing use the documented fallback voice and clearly mark the voice status in the review pack
8  Add a deterministic validator for the hard rules

Hard Hebrew rules

Audience facing Hebrew includes slide copy caption CTA and any text rendered on the design

No em dash
No period
No comma
Use line breaks instead
One thought per line
Short spoken sentences
No jargon
No slogans
No guilt
No scare tactics
No fake certainty
No diagnosis
No claim that every child feels the same way
Use correct RTL in every review page and final design with lang he dir rtl direction rtl and right aligned text

The validator must fail the build if audience facing Hebrew contains any forbidden punctuation
It must report the exact field and character
Do not silently delete punctuation because that can break meaning
Rewrite the failed line and validate again

CTA rule

The CTA must preserve this exact idea in natural Hebrew

כתבו X בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור

Replace X with one short topic specific Hebrew code word
Use the same CTA on the last slide and as the final line of the caption
Do not add a second CTA such as link in bio save or share
Keep the CTA free of em dashes periods and commas

Conversion structure

Use the project research as the default formula until real LumeBook data disproves it

Slide 1
A specific familiar moment age or believable child quote
Maximum 8 Hebrew words in the main hook

Slide 2
A second standalone hook because Instagram may resurface a carousel starting from slide 2
It must make sense without slide 1

Slides 3 to 5
Recognition reframe and practical value
One idea per slide
For the child direction reveal the need behind the behavior through concrete child language
For the expert direction explain one sourced idea in plain language and give something the parent can try

Slide 6
Bridge naturally from the insight to story as a gentle conversation tool
Do not claim the book treats fixes or guarantees an outcome

Slide 7
Show the product mechanism clearly
The child is the hero with their name face and story
Show a real preview or an accurate representation of the current product
Use only verified product facts

Slide 8
The single topic specific comment CTA
Make the low risk next step clear
The parent receives a link and can create a book with their child as the hero

Caption formula

Line 1 restates the hook in different words
Then 2 to 4 short lines that deliver the useful idea
Then one natural bridge to the story or product
Final line is the exact same topic specific CTA used on slide 8
No other CTA
No em dash period or comma anywhere in the Hebrew caption

Writing limits

Hook up to 12 words total with no more than 8 words in the main line
Regular slide up to 25 Hebrew words
CTA slide up to 18 Hebrew words
Headlines must make the story understandable even if someone scans only the headlines

Research and factual safety

For expert versions use primary or high trust sources
Prefer official pediatric psychology education or public health sources and original research
Every factual claim must map to a source and state what that source supports
Do not use authority theater or invent an expert identity
If the carousel uses a named expert use a real verifiable person and quote only what the source supports
Otherwise frame it as an evidence based expert take without inventing a persona
Separate sourced facts from LumeBook wording suggestions
Verify time sensitive product facts against the live site before using them

Image descriptions

For every slide write a production ready English image prompt because it performs more reliably in image models
Include

The same child and parent character anchor across all slides in that option
The emotional beat
The action
The setting
Camera distance and angle
Lighting
Wardrobe and relevant objects
LumeBook cream plum violet and muted gold palette
The exact clean negative space reserved for editable Hebrew typography
The important subjects kept away from the text zone
No generated words letters numbers logos watermarks signatures frames or user interface

Use a warm editorial family photography direction with a gentle storybook feeling
Avoid glossy advertising smiles plastic skin and exaggerated sadness
Do not use a photoreal child in a way that could be confused with a real customer or testimonial
Mark AI generated imagery where required

Nightly artifact

Write structured data to
carousel/carousel-pipeline/drafts/YYYY-MM-DD/pack.json

Write a readable RTL review to
carousel/carousel-pipeline/drafts/YYYY-MM-DD/review.html

Also create review.md as a portable fallback

The HTML review must make selection easy
Show all six options in two clearly separated directions
Show slide copy next to the image description
Show caption CTA sources and conversion rationale
Add a simple scorecard for voice strength hook strength usefulness product fit factual confidence and production difficulty
Do not select a winner automatically

Schema and validation

Update the existing schema and scripts to support eight slides and the required fields
Validate exactly two directions exactly three versions per direction exactly eight slides per version unique option IDs and all hard Hebrew rules
Add tests or fixtures that prove the validator catches em dashes periods commas missing Hebrew missing slides repeated IDs and missing expert sources
Run the tests and a dry run before declaring success

Topic selection

Use one topic per nightly pack so the six versions compare voice and angle rather than unrelated subjects
Prefer a timely topic from carousel/carousel-pipeline/topic-bank.md
Avoid a topic used in the previous 14 packs
Avoid the same hook family more than twice in 7 days
Record the selected topic hook family code word and option metadata in a small history file so future runs can rotate intelligently

Scheduling

Create or update a Claude Code Desktop local scheduled task named lumebook-nightly-carousel
Working folder must be /Users/yarinbruner/Claude/Projects/Lumebook
Run daily at 22:00 in the computer local timezone which is Asia Jerusalem
The task instructions must invoke the LumeBook carousel skill in nightly review mode
It must never call fal ai or spend money
It must generate and validate the six option pack then surface the review file path in the completed session
Run the scheduled task once manually after creation to catch permission issues
Local scheduling is preferred because this folder is local and the production workflow uses local files and MCP configuration
Mention clearly that Claude Desktop must be open and the computer awake for the 22:00 run
If the scheduled task tool is unavailable do not fake success
Give the exact Claude Desktop steps under Code then Routines then New routine then Local and provide the final saved task instructions ready to paste

Approved production stage

After Yarin chooses one option such as kid-2 or expert-1 freeze its copy and visual briefs
Never call fal ai before an explicit option choice and explicit generation approval

Use fal ai MCP with these current endpoints

openai/gpt-image-2.5/flare/text-to-image
openai/gpt-image-2.5/flare/edit

Generate one character and style reference first
Then use the edit endpoint with that reference for all eight slide scenes to preserve identity wardrobe palette and visual treatment
Use a 4 by 5 vertical output or a custom 1024 by 1280 generation size when the endpoint supports it
Final exported slides must be 1080 by 1350

Before paid calls show

The selected copy
The number of images
The endpoints
The quality setting
The estimated maximum cost
What will be regenerated if visual QA fails

Ask for approval at that point

After approval generate images without embedded text
Inspect each image at full size for character consistency hands faces anatomy accidental words typography space product accuracy and visual continuity
Regenerate only failed slides
Stop after two failed replacements for the same slide and ask for direction

Final composition

Do not rely on the image model to render Hebrew
Overlay editable Hebrew with deterministic HTML and CSS after the images pass QA
Use project brand assets and fonts
Render 1080 by 1350 PNG files
Keep an editable HTML source
Create a numbered contact sheet and a final ZIP with the slides caption sources and generation log
Run an RTL visual check on mixed Hebrew numerals and any Latin brand terms

Implementation quality

Keep API keys only in environment variables
Never write FAL_KEY to disk or logs
Make reruns idempotent
Do not overwrite an existing nightly pack without creating a versioned backup or asking
Log model endpoint request ID duration and estimated cost but never secrets
Make every paid step resumable so a failed slide does not regenerate the whole carousel

Definition of done

The existing project has one coherent documented pipeline rather than parallel drafts
The voice skill exists and its calibration status is honest
The validator and tests pass
A no cost sample pack with six options and forty eight slides is generated
The RTL review HTML and Markdown open correctly
The selected option preparation step produces valid fal ai jobs without calling them
The final renderer can be tested with placeholder images
The local 22:00 task is created and a manual run succeeds or exact setup instructions are provided if task creation is unavailable
The README explains nightly review selection approval image generation QA final export and how to recover from failure

At the end give me only

1  What you implemented
2  Paths to the nightly review and key files
3  Test results
4  Whether the 22:00 task was actually created
5  Any one time action I still need to take such as adding voice samples approving permissions or setting FAL_KEY
```

