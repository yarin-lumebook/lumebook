# LumeBook creator map: project summary

Status date: 11 Oct 2026 (evening). Outreach numbers were read from the map's database on 11 Oct. Everything else comes from the files named next to it. The outreach tactic update of 11 Oct (tracks, reasons, fit check, new sequence, follow-up timing, steps, measurement) is built and verified locally. It is not republished yet: see section 10.

## 1. What this is

A verified list of 243 Hebrew-speaking Israeli creators (5K to 50K followers for anyone not yet contacted; 204 from 3 Oct, 100 added 11 Oct, 61 never-contacted under-5K creators removed 12 Oct) who could make credible UGC for LumeBook, plus the outreach tool Yarin uses every day to contact them. The first goal was the research; the map became the main working tool.

- Published map (private artifact): https://claude.ai/artifact/DCJ2ZT1Y4K8MrcH5bot2Hj
- Code: `creators/creator-research/` in the monorepo github.com/yarin-lumebook/lumebook (since 8 Oct; the old `lumebook-creator-map` repo is archived, history kept)
- Component id in `lumebook.json`: `creator-map`

## 2. Rules that apply to everything here

| Rule | Source |
|---|---|
| No em dashes or en dashes in anything written for Yarin or the audience | CLAUDE.md, user |
| Brand is LumeBook in messages (Hebrew לומיבוק elsewhere, since 20 Nov 2026), never לומבוק | CLAUDE.md, user |
| Offer: one 25% allocation per sale through the creator's personal link. The creator decides how much is their earnings and how much is an audience discount (for example 15% and 10%); the discount is applied automatically through the link. Never 25% plus an extra discount. Never "קוד הנחה" or "קוד אישי" | `shared/facts.json` offer, Yarin 11 Oct |
| Commission only, nothing paid (Yarin, 12 Oct). Three tracks, all the same offer, different message angle: General, Professionals, Parents. The Paid UGC and Paid partnership tracks were removed | `shared/facts.json` offer, Yarin 12 Oct |
| Hebrew only: Arabic and Russian creators were removed | user, 3 Oct |
| Contacts are only ones the creator publishes (bio, bio links, own Linktree or site). Instagram is read only: no follows, no DMs from me | research method |
| Kids: record how many, their genders and names, only from public information. Never infer gender from a name | user, 7 Oct |
| Hebrew grammar: follow `src/hebrew-rules.md`. Hand-typed text is only changed when Yarin presses Fix | user, 7 Oct |
| Never edit the built HTML. Edit `src/` and rebuild | CLAUDE.md |
| Commit or push only when Yarin asks | CLAUDE.md |
| Do not mention AI in audience copy | CLAUDE.md |

## 3. Timeline

| When | What |
|---|---|
| 3 Oct | Research brief. First pass: about 70 hand-rated creators, shortlist, archetype map, first barter batch. Expanded to 204 on request (Hebrew only). Published and contact details collected. |
| 3 to 4 Oct | Yossi's offer relayed (20% split between creator earnings and audience discount, personal promo code instead of UTM). Cold DM and email drafted from Yarin's edits. The map became the main tool: light mode, sort by date added, editable per-creator messages, "Save and learn my voice". |
| 4 Oct | Dashboard redesign (versions 20 to 21): sidebar, one page per section, shared search/filter/sort. Shortlist, waves and strategy pages removed (not used). Two message styles (Warm, Short) with tracking. Offer email tab added. |
| 5 Oct | Statuses cut to what Yarin uses, Follow-up due as its own list, automatic timing (24 hours, then a week), In process and No reply added, Said yes removed. |
| 7 Oct | Kids counts and genders, kid-aware grammar, Hebrew definite article rules, Hebrew check with Fix button, no repeated examples after the moment, personal link instead of a discount code, kids' names in messages. |
| 8 Oct | Monorepo move, restyle on the LumeBook design system, commission wording "עד 25%". |
| 10 to 11 Oct | Map rebuilt with two new design-system CSS lines (uncommitted, not republished). |
| 11 Oct, night | Third research pass: 100 more creators (section 4), 304 in total. |
| 11 Oct | Outreach tactic update: collaboration tracks, reasons behind a no or a stall, fit check, track-specific message sequence, follow-up timing from real sends, steps inside In process, funnel and tests, offer check and a data update for saved templates. Built and verified locally. |

## 4. Research

### Method (the map's Method page, `src/template.html`)
- Web search: 6 parallel agents, about 120 searches, Hebrew and English queries and Hebrew listicles. Yield was low.
- Instagram similar-accounts graph: first from 14 seeds, then from 76 verified Hebrew creators (about 2,000 accounts), filtered by name and bio line.
- Instagram account search: 58 keywords.
- Verification: each listed creator opened read-only in a logged-in browser on 3 Oct 2026. Followers, bio, category, the last 12 reels' views and dates (decoded from the reel ID). TikTok with yt-dlp (latest 15 videos). mebook.ai's tagged tab checked for competitor overlap.
- Screened: about 2,600 accounts by name, about 500 checked one by one, 204 kept.

### Third pass (11 Oct 2026, 100 creators)
- Yarin asked for 100 more. Instagram in the browser pane was signed out, so Yarin signed in with his own account; I only read (similar-account lists, searches, profile pages), no follows, likes or messages.
- Discovery: similar-account lists from 117 creators already in the map, then from 74 of the new finds, plus 48 Hebrew keyword searches. About 3,800 accounts seen.
- Checked: 446 profiles opened. For each: exact followers, full bio, bio links, and the latest 12 reels with views; the last reel date is decoded from the reel code. 285 passed the basic test (public, 1K to 50K followers, at least 3 reels, a reel since July 2026).
- Kept 100. Dropped mostly: baby-sleep, breastfeeding, birth and nutrition accounts (outside the book's ages), shops, venues and brands, creators living abroad, and general lifestyle accounts with no children's angle. About 80 of the 100 are a clear fit and about 20 are borderline; each borderline one says why in its risk note.
- Mix: 30 parent guides, 19 parents, 13 child-development professionals, 6 family travel, 6 special education, plus teachers, home daycares, kids' activities, two blended or co-parent families, one twins account, one grandma character.
- Records: `src/research/data3.py` (role, ages, content idea, risk, kids, all written from the bio), `src/research/pass3_raw.json` (the stats as read), `src/research/merge3.py` (adds them to `C_all.json`, `kids.json`, `contacts.json`; it only appends). Ratings are rule-based, like the second pass.
- The map picks a starting track for them: 77 Gifted + affiliate, 13 Paid partnership, 10 Paid UGC. That comes from the estimate, not from the creators.
- Contacts now: 94 of 304 publish an email or phone. Kids info: 113 of 304.

### Scoring
Ten weighted 1 to 5 ratings: audience fit 14, creator-brand fit 14, parent trust 12, UGC potential 12, authenticity 10, content quality 8, professional credibility 8, commercial usability 8, affordability 8, on-camera 6. Score = weighted sum divided by 5, so 100 is the maximum. Follower count is not an input. The 70 first-pass creators and 3 second-pass picks were rated by hand; the other 131 get stricter rule-based ratings. Use the per-creator notes more than small score gaps. Scores remain in the data, but the shortlist and wave ideas were dropped from the UI.

### Notable findings
- `mor_knoll` appears on mebook.ai's tagged tab, so treat her as a competitor conflict.
- The old Drive "Creator Outreach Tracker v2" has drifted: `happymeute` is 1,050 followers (listed 15.7K), `kuchale` is private, three handles no longer exist.
- Held for paid work pending Yossi's approval (from the first batch notes): `lital_magnezi`, `ganotmor`, `almaanddad`.

### Not verified (stated on the Method page)
Comments and engagement quality; on-camera ability and content quality (inferred, videos not watched); sponsorship history beyond bios and MeBook's tagged tab; collaboration rates; audience demographics; which published numbers are personal or business lines; Israel residence of three Arabic-language creators (since removed from the Hebrew-only list).

### Contacts
75 of 204 creators publish an email or phone ([`src/contacts.json`](src/contacts.json); 33 email and 66 phone or WhatsApp in the 3 Oct count). The rest are Instagram DM only.

## 5. The map

### Navigation (sidebar)
- Outreach: Overview, then one page per status: All creators, Not contacted, Message sent, Follow-up due, No reply, In process, Declined, Posted. Each has a live count.
- Saved views: Top scores to contact, WhatsApp first, Has email, Newest added, In process: next steps, Asked for payment, Paid tracks, Offer wording to review, plus any Yarin saves (stored in `settings/main`, can be deleted with Undo).
- Research: Database, Archetype map. Settings: Messages and voice, Method and limits.
- Phone width: the sidebar slides in from a menu button. Old links (`#send`, `#c-replied`, `#c-yes`, `#c-code`, `#shortlist` and so on) redirect.

### Shared toolbar (Creators and Database)
Search (also on `/`), faceted filters with live counts (track, In process step, reason, test version, channel, kids, must-have flags, score, followers, median views, latest reel, research pass, archetype; Database adds status), sort with up to three levels (now also next action date, track, step), group by (status, channel, track, step, reason, archetype, follower band), save view. Must-have flags now include: next action due or overdue, offer wording to review, and "No reply, follow-up still possible". The Database table has a Track column.

### Creator card (simplified 11 Oct, late evening, on Yarin's list)
- Layout (reorganised late on 11 Oct): two columns on a wide screen, stacked on a phone. Left: the handle, which is the link to the profile, the name, numbers, chips (In process step, reason, next action overdue or today, channel, kids, test label) and the Status and Track menus with labels. Right: the message tabs, the message box sized to its text, and one row of actions.
- **Track:** every creator has one. Yarin's choice wins; until he makes one the map picks and marks the chip "auto": already contacted = Gifted + affiliate (the offer they were sent); not contacted = Paid UGC when the profile sells UGC or content for businesses, Paid partnership when the research estimate is a paid collaboration (or contact goes through management, or the creator is on the hold-for-paid list), otherwise Gifted + affiliate. On 11 Oct that gave 104 contacted on gifted, and of the 100 not contacted: 81 gifted, 17 paid partnership, 2 paid UGC. The pick comes from the research estimate, which nobody verified with the creator.
- **Message box, always on the card:** tabs (First message, Email, Follow-up, Final follow-up, Interested reply, Offer details), the editable text, and the Hebrew check and Offer check line. The box opens on the message that is next: first message, the follow-up when one is due, the interested reply when In process.
- One message style. The Short version, its switch and its templates were removed; cards sent in Short before keep "Short" next to the sent date, and that text is kept under "First message as sent".
- No Copy message button (the box has Copy) and no "Save and learn my voice" button: learning is automatic (section 7).
- One action row under the box: Copy (copies whichever tab is open, so the separate copy buttons for email, follow-up, interested reply and offer details are gone), WhatsApp, Email, Mark sent or the follow-up controls (section 6), and at the end the Edited mark with Reset to template.
- Deal row (In process and Declined only): step, next action and its date, "Said they are interested", and the reason. When the reason is about pay, "Move to Paid UGC / Paid partnership" keeps the conversation In process (or reopens a decline) on a paid track.
- "Deal, reply & notes" (closed by default): personal link, channel used, sent date, sales through the link, on a paid track the quoted fee, currency, budget approval, deliverables and (Paid UGC) whether posting on their own account was agreed, their reply in their words, greeting, kids and notes.
- The fit check was removed on Yarin's request.

### Overview
- Tiles: Contacted, Replied, In process (with next actions due), Follow-ups due, Content received (with published).
- Lists: In process next steps (overdue first, then by date, then the ones with no next action), follow-ups due (first or final, days overdue), next to contact.
- Pipeline bar.
- "From first message to published": Contacted, Replied, Expressed interest, Terms agreed, Content received, Published, Attributed sales. Compare by track, channel used, message version or reason. Interest counts only creators ticked as interested or at Terms agreed and later; In process alone is not interest ("n not marked" is shown). Content received includes paid UGC delivered without a post. Sales show "No data" until a number is entered; an empty field is never zero.
- "Reasons behind a no or a stall": counts per reason, declined and still talking apart. No reply is listed separately and is never a reason.
- Warm and Short, the historical style split, is read under "By message version" with a note that it is a record and not a test.
- Tests: see section 7.

### Feedback
Buttons shrink on press, pop green on success and shake on failure; a toast confirms every action (Undo where it makes sense); the learn button shows a spinner. Reduced-motion is respected.

## 6. Statuses, follow-ups and steps

| Status | How a creator gets there |
|---|---|
| Not contacted | default |
| Message sent | Mark sent, or after a follow-up is recorded as sent (waiting again) |
| Follow-up due | automatically 4 days after the first message with no reply; or 7 days after the first follow-up was really sent, only if Yarin planned a final follow-up for that creator; or set by hand |
| No reply | automatically 7 days after the last follow-up that was really sent (the first one when no final is planned, otherwise the final one); or set by hand |
| In process | set by hand: the creator replied and you are talking |
| Declined | set by hand: the creator said no. The follow-ups stop |
| Posted | set by hand: publication confirmed |

- Only the "Follow-up sent" / "Final follow-up sent" buttons record a follow-up. A due date that passes is never counted as sent: an overdue creator stays in Follow-up due.
- Sends are stored apart from due dates: `on`/`sat` first message, `fu`/`fuat` first follow-up, `fu2`/`fu2at` final follow-up, `fuh` the list of every follow-up send. `fu2w` marks the creators picked for a final follow-up. A status change never rewrites a send date.
- A creator in No reply who never got the follow-up (or the final one) can still get it from the card.
- The page works the status out each time it opens (and every minute while open). Nothing is written for the automatic moves, so no clock restarted when the timing changed from 24 hours to 4 days.
- Timing constants: `FU1_MS` = 4 days, `FU2_MS` = 7 days, in `src/template.html`.
- Old values map to the new ones: Replied, Said yes and Code issued show as In process.
- Replies count In process, Posted and Declined. No reply is not a reply and not a reason.
- A status moving to In process, Declined or Posted stamps the reply time once (`rat`).

### Steps inside In process
Discussing offer or rates, Terms agreed, Book preparation, Book sent, Content pending, Content received (`stg`), with a next action and its date (`na`, `nad`). Posted stays the confirmed-publication status. Paid UGC that was delivered and not posted is "In process, Content received" and counts as content received.

### Reasons
Does not accept commission-based work, Commission considered too low, Wants guaranteed project payment, Product or audience mismatch, Timing or workload, Child visibility or privacy, Other, Unknown (`obj`), with the creator's own words (`objq`) and a short note (`objn`). A decline with no recorded reason reads as Unknown; nothing is written or guessed. The 36 existing declines have no notes, so all 36 show as Unknown.

## 7. Messages

### Types and tracks
Six message types: first message, email (subject plus body), follow-up, final follow-up, interested reply, offer details. Each exists per track (Gifted + affiliate, Paid UGC, Paid partnership). There is one style, Yarin's learned voice; the Short style was retired on 11 Oct and its saved `_b` templates sit unused in `settings/main`.
- The track decides the offer. Edits are stored per track, so a text written for one offer never appears under another.
- Gifted + affiliate: the first message states the exchange (a personalised book for one video) and ends with one next step (send a book example and the details). The 25% split is explained in the email, the interested reply and the offer details, not as arithmetic in every first DM.
- Paid UGC and Paid partnership: ask for rates and availability. They promise no payment and name no budget. Paid UGC says the video need not go on the creator's page. `{fee}` is filled only when a fee is quoted and the budget is marked approved for that creator; otherwise it is a visible bracket.
- Follow-up: adds the reason for the fit and offers a book example. Final follow-up: closes the loop. Neither nudges or guilts.
- The gifted offer details are Yarin's own wording. On 11 Oct the three lines about the percentage were corrected to the one-allocation wording; nothing else in that text changed.
- Mark sent records the track, channel, whether the text was hand-edited, and the text itself.

### Tests
A test changes the first-message wording (version A is the current template, version B is Yarin's variant) inside one track and one first channel. Creators are drawn at random and assigned in pairs matched by follower count, 20 per version by default. It writes draft labels only (`exp`, `expv`, and it pins the track) and sends nothing. Results are read at day 7 after each creator's own send, and the page says "not comparable yet" until both groups are complete, then labels the sample as small. It never names a winner. A variant that changes the offer itself is refused.

### Placeholders
`{name}`, `{line}` (the opener about their content), `{moment}`, `{sender}` (default ירין), `{preview}`, `{deliverables}` and `{fee}` (paid tracks).

### What is applied automatically (in `src/template.html`)
- Brand: LumeBook in Latin letters, with a hyphen after a Hebrew prefix (ב-LumeBook). The Warm offer email keeps Yarin's own spelling.
- Kids grammar: the child phrases follow the kids data. One boy or unknown: הילד / שלו. One girl: הילדה / שלה. Two or more, all girls: הילדות / שלהן. Boys, mixed or unknown: הילדים / שלהם. The generic book sentence stays generic.
- Kids' names (from the bio or typed in): "ספר מתנה ללביא ועידו", "סרטון של לביא ועידו עם הספר שלהם". A single named child of unknown gender gets no possessive.
- Definite article: ל, ב, כ before `{line}` absorb the article (לתוכן, not להתוכן); a safety net fixes known nouns after ל, ב, כ.
- No repeated examples: examples after `{moment}` that it already contains are removed.
- Safe punctuation tidy: no space before , . ! ? : ; a space after, no double spaces, no space before %, hyphen after a prefix before Latin text, no long dashes.

### Hebrew check
A line under each message flags the checkable problems and offers Fix: punctuation spacing, double spaces, long dashes, brand in Hebrew letters, missing prefix hyphen, ה after ל/ב/כ, space before %, unclosed brackets, and any mention of "קוד". It never changes text until Yarin presses Fix.

### Offer check
The same line also checks the commercial facts. Fixable with Fix: the old 20% and its old example. Flagged for review only: 25% next to a discount with no split wording (reads as 25% plus a discount), a gifted first message with no video ask, commission in a paid-track message, and an amount named while no budget is approved. The saved view "Offer wording to review" lists creators whose saved, not yet sent messages have such a flag. Messages that already went out are history and are never rewritten.

### Voice learning
Learning is automatic since 11 Oct: when Yarin changes a message and leaves the box, the edit is learned once (a flag `l<edit key>` stops the same text from being learned twice; a failed run is tried again on the next change). It rewrites that creator's other messages to match and nudges the shared templates of that track only. It needs the page open in Claude; in a plain preview the edit is just saved. It keeps creator-specific details out of the templates, keeps the Hebrew rules, and has Undo. Learned so far from 14 edits; 12 voice rules stored.

Facts lock (11 Oct): learning changes how a message sounds, never what it offers. Each track has its own fixed offer facts in the instructions, only edits from the same track teach a track's templates, and a rewritten template is kept only if its commercial fingerprint (percentages, link, code, video ask, gift, price talk, earnings talk) is unchanged. Otherwise that template stays as it was and the page says so.

Full Hebrew checklist: [`src/hebrew-rules.md`](src/hebrew-rules.md).

## 8. Data

### Source files (`src/`)
| File | What |
|---|---|
| `template.html` | the whole page and its scripts |
| `build2.py` | fills the template and writes `../lumebook-creator-map.html`. Reads the offer (25%, split example, hold-for-paid list) from `shared/facts.json` |
| `enrich.py` | waves (unused now), opener lines, moments |
| `C_all.json` | the 204 creators |
| `contacts.json` | published emails and phones |
| `kids.json` | kids per creator: `n`, `b`, `g`, `names`, `note`, `src` |
| `hebrew-rules.md` | Hebrew checklist |
| `research/` | the scripts and records that produced `C_all.json` |

### Kids data
71 of 204 creators have kids info, 33 with names, 10 with genders, all from the Hebrew bios read on 3 Oct. Removed after review: `kesem_maor_livshiz` ("Lital Shoham" looks like his AI character) and the unsupported "two girls" for `anat_gavra`.

### Artifact database (collections)
- `outreach/<handle>`, as before: `s` raw status; `on` sent date; `sat` sent time; `dat` due-since time (manual Follow-up due); `fu` first follow-up date; `ssent` and `sty` style; `x_<type>` and `x_<type>_2` edited texts (and `ax_...` when auto-adapted); `kn`, `kb`, `kg`, `kname` kids overrides; `name`, `line`, `code` (the personal link), `note`; `at` last change.
- `outreach/<handle>`, added 11 Oct (all optional, old records work without them): `trk` track (gift, ugc, partner; empty = the map's automatic pick); `fee`, `cur`, `dlv`, `bud` (asked, ok, no), `post` for paid tracks; `obj`, `objq`, `objn` reason; `fuat`, `fu2`, `fu2at`, `fu2w`, `fuh` follow-ups; `stg`, `na`, `nad`, `int` step, next action, interest; `rat` reply time; `sales`; `trks`, `chs`, `mv`, `msnap` what went out (track, channel, hand-edited or template, the text); `exp`, `expv` test label. Edits on paid tracks use `x_u_<type>` and `x_p_<type>`.
- `settings/main`: `sender`, `preview`, `tpl` (gifted: dm, es, eb, fu, f2, d2 and the `_b` Short versions, `of_b`; paid: the same with `u_` or `p_` in front), `views`, `exps` (tests), `mig` (the data update: when, how many fields, and the backup for Undo).
- `voice/main`: `rules`, `ex` (each example now carries its track `k`), `n`, `prev`.
- Browser fallback (preview only): `lume_outreach_v1`, `lume_ui_v1`.

### Data update for saved templates (in the page)
Templates saved in `settings/main` win over the defaults in `src/template.html`, so new defaults never reach them. When saved templates or voice notes still say 20%, the page shows a callout with a preview of every field, before and after, and writes nothing until Yarin presses Apply. It changes only the percentage and its example, keeps a backup for Undo, and has nothing left to do on a second run. Optional suggestions (one next step instead of two; a follow-up that adds something) are listed unticked. Outreach records are never touched by it.

## 9. Outreach so far (11 Oct, from the database)

| | Creators |
|---|---|
| Contacted | 104 of 204 |
| Message sent (the 10 sent today) | 10 |
| Follow-up due | 48 |
| No reply | 0 |
| In process | 10 |
| Declined | 36 |
| Posted | 0 |

- Sent dates recorded: 21 on 4 Oct, 6 on 5 Oct, 20 on 6 Oct, 24 on 7 Oct, 10 on 11 Oct. 23 contacted creators have no date.
- Replies: 46 of 104 (36 declined, 10 in process). 10 of the 46 who answered are in process.
- Under the 11 Oct timing, a creator leaves Follow-up due only when a follow-up is really sent or the status is changed by hand. No follow-up has been recorded as sent so far.
- Checked on 11 Oct at 18:50 against a copy of the live data in the local preview: 40 Follow-up due and 18 Message sent (the 7 Oct evening sends cross the 4-day mark by about 20:45, which makes it 48 and 10).

### Style test
| Style | Sent | Replies | In process or posted |
|---|---|---|---|
| Warm | 79 (11 have no recorded style) | 36 (46%) | 7 |
| Short | 25 | 10 (40%) | 3 |

This comparison is observational: Yarin chose each style by hand, the groups differ, and the sends are days apart, so the gap cannot be credited to the style, at any sample size. A fair comparison needs a test (section 7), read at equal time since sending.

This is an early snapshot. The sends are between 0 and 7 days old, so the reply count is not final and zero posts says nothing yet about the offer.

## 10. Open issues and what activates the update

The update lives in `src/` and in the built `lumebook-creator-map.html`. The published artifact still runs the 8 Oct version, and the live database was only read, never written.

To activate it:
1. Republish `lumebook-creator-map.html` to the same artifact URL, then run `python3 tools/lumebook.py ack creator-map --published`.
2. Optional, on Messages and voice after republishing: the saved follow-up ("רק מוודא שההודעה לא הלכה לאיבוד") can be swapped for the new one, and the saved email body's double ask for a single next step. Both are unticked by default because they are Yarin's wording.
3. Set "Sample book preview link" on Messages and voice. It is empty, so the interested reply shows a bracket where the book example goes.

### 25% everywhere (11 Oct, evening, on Yarin's instruction "its 25% change it everywhere")
- **Live database, written directly:** the saved templates `d2`, `eb`, `eb_b`, two voice notes, two learning examples, and 24 saved message texts of 20 creators (after-yes drafts and four emails) now say 25%, with the example 15% and 10%. Only the percentage and its example changed; the re-read showed no other field differs. The values from before are in the document `settings/backup-2026-10-11-pct`, and `settings/main` `mig` lets the republished page undo the template and voice-note part. This works with the currently published page too.
- **Not known:** whether any of those texts had already been sent with 20%. The four In process creators with such a draft are `almaanddad`, `etti_haft`, `orli.parenthood`, `rotem__unger`; the emails belong to `efi.rotem`, `ima.shir`, `knafaim.ot_by_noy` (hand-edited) and `yafitdanieli`. If they were told 20%, they need to hear 25%.
- **Ambassadors site source:** 20% to 25% in 9 places (`index.html` 7, `creators/index.html` 2). The link-preview image had "20% עמלה" in the picture; the 0 was redrawn as a 5 in the brand's Rubik font, in `shared/brand/lumebook-whatsapp-preview-1200x630.png` and `sites/lumebook-ambassadors/img/og-preview.jpg` (only that digit's pixels changed). **Not deployed, and it will not be:** Yarin said on 11 Oct that he no longer needs the Vercel ambassadors site. It is marked retired in `lumebook.json` and `CLAUDE.md`, its links and alerts are off the dashboard, and the folder stays as an archive. The old pages were still online with 20% when last checked that evening; taking them offline means removing the Vercel project.
- **Creator CSV:** the old after-yes and email drafts (441 mentions) now say 25%.
- **Live Google Form: still 20%.** Its description says "קוד הנחה אישי לעוקבים שלכם" and "20% עמלה על כל הזמנה דרך הקוד", and the title spells לומיבוק (read from the public form on 11 Oct). Not changed: it needs Yarin's go-ahead.

Still open:
1. **Questions for Yossi** (in `shared/facts.json` offer.open_questions): how the sale value behind the 25% is calculated (price only, or shipping too); payout method and timing; how the personal link and its automatic discount are tracked and attributed at checkout; whether the creator can change their split later. No message states any of these.
2. **Paid tracks have no approved budget.** The paid messages only ask for rates. The line "we will prepare a personalised book and send it before the shoot" in the paid offer details is my assumption (the video needs the book) and should be confirmed.
3. **Code wording in saved messages.** No saved text says 20% any more. 15 creators who have not declined still have a saved follow-up or after-yes text that mentions a code; the saved view "Offer wording to review" lists them and Fix corrects each. First messages that already went out with "קוד הנחה" stay as the record.
4. **History that cannot be recovered:** the channel actually used, whether a sent text was the template or hand-edited, and when each reply arrived were not recorded before 11 Oct. They show as "not recorded" and are not guessed.
5. **Ambassadors site:** retired on 11 Oct. Nothing to do in the project. The old pages stay online at the old address until the Vercel project is removed.
6. **Google Form:** the live form still says 20% and a code (see above). Both form scripts say "עד 25% עמלה" and "קישור אישי עם הנחה".
7. **Coverage:** 133 creators have no kids info; engagement quality was never checked.
8. **Not committed.** Everything since 10 Oct in this folder is uncommitted.

## 11. Daily workflow

1. Overview: clear "In process, next steps" first (overdue on top), then "Follow-ups due", then "Next to contact".
2. In process: set the step, write the next action and its date. If they ask for pay, record the reason and move them to a paid track instead of closing the conversation.
3. Follow-ups: copy, send, press "Follow-up sent". Plan a final follow-up only for the creators worth one more message.
4. New creator: open the profile from the handle, check the track the map picked, adjust the message in the box if needed, copy, send, Mark sent.
5. A no: set Declined and pick the reason, in their words if they gave one.

## 12. How to work on it

```bash
python3 creators/creator-research/src/build2.py        # rebuild the map HTML
python3 tools/lumebook.py status                        # what changed and what it affects
python3 tools/lumebook.py ripple                        # rebuild and sync dependent pages
python3 tools/lumebook.py ack creator-map --published   # after republishing the artifact
```

Preview with the launch config `creator-map-static` (port 8773, serves this folder; open `/lumebook-creator-map.html`). Publish the built file to the same artifact URL so the link stays. Saved views, statuses and templates live in the artifact's database, so a republish does not lose them.

## 12 Oct 2026: commission only, Short is back
- **Tracks:** General, Professionals, Parents. Same offer in all three (book for one agreed video, personal link, the 25% split); only the angle changes. Professionals is written for therapists, parent guides and teachers (the book as a tool for their work with families, an agreed video that does not have to be of a child, no medical claims). Parents is written parent to parent (read it together, a video of the child with the book).
- **Auto pick:** already contacted = General; not contacted = Professionals for professional archetypes (child development, parent guides, gan, teachers, daycare, special education, books, community, screen-free), Parents for parent and family archetypes, otherwise General. On 12 Oct: 104 contacted General; of the 200 not contacted, 109 Professionals, 68 Parents, 23 General.
- **Removed:** Paid UGC, Paid partnership, quoted fee, currency, budget approval, deliverables, the `{deliverables}` and `{fee}` placeholders, the "Move to a paid track" buttons, the Paid tracks saved view, `paid_budget_approved` in shared facts. The offer check now flags any price, rate or fee wording, because nothing is paid. The reasons "Wants guaranteed project payment" and "Commission considered too low" stay, since those are the answers creators give; the saved view "Asked for payment" lists them.
- **Old records:** a creator saved with a paid track (`trk` ugc or partner) simply falls back to the automatic pick. Their old fee, budget and deliverables fields stay in the database, unused.
- **Short style:** back. A Warm | Short switch sits next to the message tabs, Short templates exist per track (`pro_dm_b`, `par_dm_b` and so on), the settings editor has the Warm | Short switch, the Style filter is back, and a test can compare Warm with Short. Your saved Short templates (`dm_b`, `eb_b`, `d2_b`) are used for General again. Professionals and Parents are written from the default texts, not from your saved ones, until you edit them (the voice then learns per track).

## 12 Oct 2026: Declined button on every card
- Every card that is not already Declined has a red X on a light red circle (no text) at the far right of the action row. One press sets the status to Declined (with Undo), which stops the follow-ups; the reason can be added on the card afterwards. It does the same as choosing Declined in the status menu. A first version of this was built as a Trash page for declined creators; it was removed because Yarin meant this button.
- The handle on every card and in the Database opens the creator's reels tab.

## 12 Oct 2026: 5K followers or more
- Yarin: "5k followers +, delete everyone else", then "from now on only 5k+ accounts". Rule: new creators need 5,000 or more followers (up to the 50K ceiling).
- Removed from the map, CSV, contacts and kids data: the 61 creators under 5,000 followers who had never been contacted (no outreach record, or Not contacted), 28 of them from the third pass. The full records are kept in `src/research/removed-2026-10-12.json` and `merge3.py` will not add them back. They are listed on the Database page under "Checked and excluded".
- Kept: the 48 creators under 5K who were already messaged (25 declined, 20 waiting, 2 in process, 1 follow-up due), because deleting them would erase live conversations and the history behind the funnel. Yarin chose this option; say if they should go too.
- Now 243 creators (72 from the third pass), 81 with a published email or phone, 94 with kids info.
- No live outreach records existed for the removed creators, so nothing was deleted from the artifact database.

## 13 Oct 2026: Book sent and Content created statuses, coloured menus
- Two new statuses between In process and Declined: **Book sent** (`book`) and **Content created** (`content`). They appear in the sidebar, the status menu, the filters, the pipeline and the Database. Both count as replied, interested and agreed; Content created counts as content received. Cards on them keep the next action, its date and the "what is holding it up" reason.
- The In process steps are now only Discussing the offer, Terms agreed, Book preparation. A record saved with the old steps reads as the new status without being rewritten (Book sent or Content pending = Book sent, Content received = Content created).
- The Status and Track menus on the card are no longer the browser's own dropdown: a design-system styled list with a colour dot per option, a tick on the current one, keyboard arrows and Escape.

## 13 Oct 2026: no Posted, auto-decline after a month, light only
- **Posted is removed.** Content created is the last status. An old record saved as Posted reads as Content created; the funnel's Published column is gone.
- **In process for 30 days with no status change reads as Declined.** It is worked out from the dates (`sct`, the time of the last status change, or the reply time for older records) and never written, so choosing In process again restarts the clock. The card shows the chip "auto: a month in process". Book sent and Content created never expire.
- **No dark mode on the map** (Yarin): the toggle is removed and the page is always light. Since 05 Nov 2026 every page is white only.

## 14 Oct 2026: the whole project is light mode only
- Yarin: "i want the entire project to only be in light mode from now on". The dark theme was removed from the design system itself (`shared/design/lumebook.css` has no dark tokens), `design.py` sets the light theme and has no toggle, and every published page was republished.

## 14 Oct 2026: a decline is not a reply
- Replied (Overview tile, funnel, tests) now counts only creators who replied and kept talking: In process, Book sent, Content created. Declines are left out (Yarin). The card's "Their reply" box and the reasons chart still cover declines, since a no is still an answer.

## 6 Nov 2026: "אולי בעתיד" (maybe in the future) tab
- A new status and sidebar page, `future`, between "לנסות שוב" and "סירבו" (route `#c-future`, colour `.st-future`). It is in the status menu on every card, the filters, the sort, the Overview pipeline and legend, and the sidebar with a live count. Built in `src/template.html` the same way as "לנסות שוב"; no data changed, so every creator keeps the status they had and the tab starts empty.
- Meaning: "not now, maybe later". It counts as an answer (not in the "didn't answer" count, and the reply time is stamped once) but not as a decline and not as a talk in progress, so it has no reason field; the note box holds why.
- Choosing it suggests the next action "לחזור אליהם בעתיד" in 60 days (`ST_NA`); the date can be changed or cleared in the prompt.
- A card in Declined has a new "אולי בעתיד" button next to "לנסות שוב".
- Built and checked on the project server (page, sidebar, menu, pipeline). Republished the same day to the artifact URL (version 3); the artifact's database and `state/posts.json` were not touched.
