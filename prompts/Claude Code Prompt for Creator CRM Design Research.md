# Claude Code prompt for creator CRM design research

You are working in the LumeBook repository at:

`/Users/yarinbruner/Claude/Projects/Lumebook`

Read `CLAUDE.md` first. It sets the rules for everything below.

## Goal

Research what a good CRM for LumeBook's creator outreach needs to do and how it should be designed, then compare that with the tool we already have and say what to change, in what order.

This is research and design only. Do not build anything, do not edit the creator map or its data, do not republish any artifact, do not commit.

## The mission the tool serves

LumeBook sells personalised children's books in Israel. Yarin is the only social media manager. The Q4 2026 plan is barter only, with no cash budget: a creator gets a free personalised book in exchange for one agreed video, plus a personal link with one 25% allocation per sale that the creator splits between their own earnings and an automatic audience discount. There is no discount code. Creators are Hebrew-speaking Israeli parents and child professionals with 5,000 to 50,000 followers.

The tool has to help one person find the right creators, contact them in a way that feels personal, keep track of who said what, get a video made, and learn which creators and messages bring sales.

Read these before researching: `shared/facts.json` (offer), `docs/` (product brief and Q4 strategy), `research/creator-content-conversion/` and `research/organic-content-conversion-notes-2026-10-14.md` (what creator content did and did not lead to buying talk), `creators/creator-research/src/README.md`, `creators/creator-research/src/refresh/README.md`, and the memory index at `/Users/yarinbruner/.claude/projects/-Users-yarinbruner-Claude-Projects-Lumebook/memory/MEMORY.md` (read the creator, offer and feedback entries).

## Step 1: describe the tool we have today

Read `creators/creator-research/src/template.html`, `build2.py`, `enrich.py` and `refresh/`, and look at the data in `C_all.json`, `kids.json`, `contacts.json`. Write down, from the code and not from memory:

- the statuses and steps a creator moves through, and what moves them
- how follow-ups are timed and shown
- what is stored per creator and where (the page's database collections, the research files)
- how messages are written, edited and learned from
- what the weekly refresh reads and flags
- what is done by hand today (sending, replying, recording a reply, moving status)
- what the tool cannot do or does badly: say which of these are limits of the current setup (one published page with a small database, one person, manual sending) and which are missing features

Yarin decided in October 2026 that Claude does not read his Instagram DMs or email, and that email automation is out. Treat that as a fixed constraint. Do not propose tools or flows that need access to his DMs or inbox. Sending stays manual.

## Step 2: research how this problem is solved elsewhere

Look for evidence, not opinions. Cover:

1. **Influencer and creator relationship tools**: how they structure a pipeline from discovery to content to results, what data they keep per creator, and what they automate. Examine several, from enterprise platforms down to the lightest tools.
2. **Gifting, seeding and ambassador programmes for small brands**: how small teams run barter and affiliate programmes with micro-creators, what goes wrong (no reply, creator takes the product and never posts, unclear terms) and what fixes it.
3. **General lightweight CRMs and trackers** that solo marketers use (spreadsheet-style databases, kanban boards, simple CRMs): which features people actually use and which they abandon.
4. **Sales and outreach practice**: reply-rate drivers for cold creator outreach, follow-up timing, how many follow-ups before it becomes pushy, and how to measure it. Prefer sources that show data over sources that give rules of thumb.
5. **Israeli context**: WhatsApp and Instagram DM as the main channels, Hebrew right-to-left support in tools, the norms of Israeli creators on payment and barter, and the rules on keeping personal contact details of private people (check what applies to storing creators' phone numbers and emails, and say how sure you are).
6. **Measuring results with no tracking budget**: how small brands connect a creator's post to sales through personal links, UTM tags and store attribution. Check `research/creator-content-conversion/` for what our own store already supports.

Source rules:

- Prefer vendor documentation, published studies, practitioner write-ups with real numbers, and tool pages you actually opened. Search results alone are not sources.
- Label every finding as one of: **verified** (you read the source, with the URL), **vendor claim** (the seller says so), or **inference** (your reading). Never present a vendor claim as fact.
- Record the date you read each page. Check prices on the vendor's own page and write the price with its currency and date, or write "not public".
- WebSearch has a cap of about 200 calls per session, shared with any subagents. Plan your searches, give subagents source lists instead of open searching, and stop searching a thread once new results repeat.
- Do not invent numbers about markets, creators or reply rates. If you cannot find a number, say so.

## Step 3: work out what the tool needs

From steps 1 and 2, write the requirements for one person running a barter creator programme. For each requirement say why it matters here, which evidence supports it, and whether the current tool meets it fully, partly or not at all. Cover at least:

- **Pipeline**: the stages from found to posted to results, what a stage means, what moves a creator on, and what each stage should ask for
- **Per-creator record**: what to keep, what to leave out, and what should be filled in automatically
- **Contact and follow-up**: channel choice, timing, a visible "what to do today" list, and how to stop being annoying
- **Messages**: personalisation without writing each one from scratch, versions, and learning from what worked
- **Terms and deliverables**: what was agreed, what was sent, what is due, usage rights for the video, and a way to see what is stuck
- **Results**: reach, link clicks, orders per creator, and cost of the barter (book cost and shipping), so Yarin can see which creators are worth repeating
- **Creator quality**: signals that predict a good partner (fit, reliability, content quality, risk such as a competitor link) and how to keep those fresh
- **Risk and consent**: personal data, children's images and privacy in what creators post, and a record of what the creator agreed to
- **Everyday use**: speed on a phone, Hebrew right to left, working while on public transport, undo, and no data loss

Add a section called **What not to build**: features that look useful but would not pay off for one person with this budget.

## Step 4: design

Describe the design in plain words and simple pictures (tables, lists, ASCII sketches), not code:

- the data model: the things the tool keeps, how they connect, and which fields are filled in by hand
- the pipeline stages and the exact screen where Yarin spends each day
- the three or four views that matter most (for example "what to do today", "waiting on a creator", "content due", "results")
- what to automate, what to semi-automate with one click, and what to keep manual, with the reason for each
- how it should look and behave: use the LumeBook design system (`shared/design/lumebook.css`, light mode only, Heebo main font with Assistant for labels, `lb-` components first, category colours only for stable categories, 390px phone width must work, Hebrew pages right to left)
- where it should live: stay as one published page with the artifact database, or move somewhere else, with the trade-offs honestly stated, including the limits of the current setup that you found in step 1

## Step 5: gap analysis and plan

Compare the design with the current tool:

- a table of requirement, current state, gap, effort (small, medium, large) and expected payoff
- the top five changes in the order you would do them, each with a one-paragraph description, what "done" looks like, and what could go wrong
- anything you could not decide from evidence, written as a question for Yarin

## Deliverables

Put everything in `research/creator-crm/`:

- `report.md`: the findings, requirements, design, gap analysis and plan, with a one-page summary at the top in plain words
- `sources.md`: every source with URL, the date read, what it was used for, and whether the claim is verified, a vendor claim or an inference
- `tools-compared.md`: one short entry per tool or approach you examined (what it is for, what it does well, what a solo barter programme would use from it, price with date)
- `README.md`: what is in the folder and how it was made

Do not copy pages or long passages from sources. Summarise in your own words and link.

## Rules

- No em dashes anywhere. Brand name is LumeBook, and in Hebrew לומבוק, never לומיבוק.
- Yarin wants plain words: short sentences, no jargon without a one-line explanation.
- Do not touch the creator map's source, its data, its published artifact or its scheduled task. Do not read or write anyone's DMs or email.
- Never delete project files. If something must move, put it in `_to-delete/` and add a line to its README.
- Commit or push nothing. When you finish, say what you wrote, what you could not verify, and what you need Yarin to decide.
