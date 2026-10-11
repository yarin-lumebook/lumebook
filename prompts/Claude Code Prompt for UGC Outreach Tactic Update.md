# Claude Code prompt: UGC outreach tactic update

Implement a new outreach tactic in our existing LumeBook UGC creator map.

Work inside `/Users/yarinbruner/Claude/Projects/Lumebook`. Read the project instructions, `creators/creator-research/PROJECT-SUMMARY.md`, the relevant source files, and `shared/facts.json` before making changes. Use the existing map, design system, and persistence architecture.

The goal is to turn outreach into better matched offers and completed collaborations. Make the changes concrete, build the map, and verify the result. Do not stop at a strategy document.

## Context and decisions

The 11 Oct snapshot in `creators/creator-research/PROJECT-SUMMARY.md`, section 9, records:

- 104 contacted creators
- 46 replies: 36 declined and 10 in process
- 48 follow-ups due
- 0 posted

This is an early snapshot with different amounts of time since contact. Do not describe the reply rate as objectively strong or treat zero posts as proof of failure.

Yarin explained in this conversation that the common outcomes are:

- Some creators do not work for commission.
- Some consider the commission too low.
- Some want a guaranteed payment per project.
- Some do not reply.

No reply is its own outcome, not a rejection reason.

Yarin agrees that we need separate offers for different creators and must clearly state the requested content in the first message.

Offer mechanics confirmed by Yarin in this conversation:

- There is a total 25% allocation per sale through the creator’s personal link.
- The creator decides how much goes to their earnings and how much goes to an audience discount.
- The audience discount is automatically applied through that link.
- For example, 15% creator earnings plus 10% audience discount uses the full 25% allocation.
- Do not imply 25% creator earnings plus an additional discount.
- Use personal-link wording, never discount-code wording.

Payout timing and method, the exact sale-value calculation, and tracking implementation remain unconfirmed in the available context. Do not invent answers.

## 1. Add collaboration tracks

Give each creator an editable collaboration track:

1. Gifted + affiliate: a personalised book in exchange for one agreed video, plus the personal-link arrangement.
2. Paid UGC: a guaranteed fee for producing content. Posting on the creator’s own account is a separate requirement and must not be assumed.
3. Paid creator partnership: a guaranteed fee for creating and publishing content to the creator’s audience.
4. Undecided: the default for existing records unless Yarin already recorded an explicit preference.

Follower count alone must not determine the track. Show suggestions based on verified content and stated preferences, but keep the choice editable. Do not infer willingness to accept gifting or affiliate terms.

For paid tracks, record a quoted fee, currency, deliverables, and budget approval state. Budget is not approved by this prompt. Draft outreach that asks for rates and availability without promising payment or a specific budget.

Make the track visible on the creator card and available in filters and saved views. Adapt messages to the selected track.

## 2. Record objections and preferences

Add a structured field for the reason behind a decline or stalled negotiation:

- Does not accept commission-based work
- Commission considered too low
- Wants guaranteed project payment
- Product or audience mismatch
- Timing or workload
- Child visibility or privacy
- Other
- Unknown

Allow a short note and preserve the creator’s wording where available.

A request for payment does not automatically mean the creator declined. Let Yarin keep the conversation in process and move it to a paid track.

Keep nonresponse separate. Do not assign reasons to the existing 36 declines without evidence. Existing declines should start as Unknown unless saved notes explicitly support another reason.

Show objection counts in the overview so the next batch can be chosen using actual feedback.

## 3. Add a lightweight qualification check

Before new outreach, make it easy to review three recent videos and record:

- Family or parenting relevance
- Product recommendations that fit naturally into the content
- Ability to make the proposed video
- Recent posting activity
- Whether children appear publicly, or a parent-only concept is appropriate
- One specific video or moment explaining why LumeBook fits

Use Checked, Not checked, and Not applicable where appropriate. Store an optional source link and review date.

Clearly distinguish verified observations from the existing inferred ratings. Do not present on-camera ability, audience demographics, or commercial preferences as verified when they are not.

Keep this compact inside the creator details. Do not add a long mandatory form.

## 4. Rewrite the outreach sequence

Keep Warm and Short as tone choices. The collaboration track determines the offer.

For each track, provide:

- First DM
- Email subject and body
- Follow-up
- Interested-reply message
- Offer details

The first message should:

- Refer to one specific piece of the creator’s content.
- Explain the personalised book briefly.
- State the exchange or commercial question explicitly.
- End with one easy next step.

For Gifted + affiliate, disclose the requested video in the first message. Do not frame it as an unconditional gift and reveal the obligation later.

For paid tracks, ask for the relevant rates and deliverables. Do not lead with affiliate commission as though it replaces their fee.

Explain the 25% split accurately and concisely when relevant. Do not lead with complicated arithmetic in every first message.

The next step can be sending a short book example and clear terms. Avoid multiple competing asks such as “send details, book a call, or provide a phone number.”

Follow-ups should add something useful, such as a book example or a clearer explanation of the fit. Avoid guilt or repetitive nudges. Stop after a decline.

Follow the project’s Hebrew and RTL rules and Yarin’s existing learned voice. No AI references in creator-facing copy. Use LumeBook, personal-link terminology, and no long dashes.

Preserve handwritten messages. Flag outdated offer wording for review through the existing explicit Fix or review mechanism. Prevent voice learning from changing commercial facts or mixing offers across tracks.

## 5. Fix follow-up timing and tracking

Implement the following proposed defaults from this conversation:

- First follow-up due four days after the initial send.
- An optional final follow-up seven days after the first follow-up was actually sent, for creators Yarin selects.

Track actual follow-up sends separately from due dates. An overdue follow-up must not be recorded as sent.

Preserve original send dates, follow-up history, and current statuses. Do not restart clocks during migration.

Creators who have not replied remain eligible for appropriate follow-up even if their status becomes No reply. A decline stops the sequence.

## 6. Track progress toward a completed collaboration

Preserve the existing top-level statuses. Within In process, add a lightweight next-step field or stage for:

- Discussing offer or rates
- Terms agreed
- Book preparation
- Book sent
- Content pending
- Content received

Use Posted for confirmed publication. Paid UGC delivered without publication must be countable as completed content without falsely marking it Posted.

Record the next action and its date, so the ten active conversations in the snapshot have a practical path forward.

Surface overdue next actions and outstanding follow-ups in the overview alongside new prospects.

## 7. Improve measurement and experiments

Report:

- Contacted
- Replied
- Expressed interest
- Terms agreed
- Content received
- Published
- Attributed sales, only when real data is available

In process alone is not proof of interest or agreement. Missing sales data must not appear as zero.

Allow comparisons by collaboration track, channel, message version, and objection reason.

Keep the historical Warm versus Short comparison but label it observational: Yarin chose styles manually, and the groups differ, as documented in `PROJECT-SUMMARY.md`, section 9.

Add a lightweight optional experiment label and message-version snapshot. For a future 40-person test, support a balanced random assignment of 20 comparable creators per version within the same track and channel, changing one variable. Assignment is for drafts only and must not send anything.

Compare outcomes after equal time since sending. Do not declare a winner merely because one group reached 50 sends. Clearly label small samples.

## 8. Handle existing data and shared facts carefully

Inspect where current settings and outreach records live. Do not assume the source defaults override templates saved in the artifact database.

Implement a backward-compatible, repeat-safe migration with a preview of affected fields. Preserve:

- Handwritten messages
- Learned voice
- Saved views
- Statuses and timestamps
- Creator notes
- Existing personal links
- Kids information

Update shared offer facts to reflect Yarin’s confirmed split mechanics. Correct obsolete 20% wording in map defaults and safely migrate untouched generated templates. Flag handwritten conflicts for review.

Replace outdated open questions with only those still unresolved. Do not silently rewrite historical outreach records.

Do not change the ambassadors site or live Google Form in this task. List their wording discrepancies in the handoff.

If live artifact storage is unavailable, finish and verify the local implementation and migration mechanism, then explain exactly what must run after republishing. Do not claim live settings were updated.

## Delivery and verification

Edit sources, never built HTML directly. Keep the current design system, both themes, Hebrew RTL, and 390px phone layout working.

Verify the important behavior:

- Correct 25% split wording
- Track-specific messages and deliverables
- Unknown reasons preserved for historical declines
- Nonresponse separated from rejection
- Follow-ups calculated from actual send events
- No data loss on migration or reload
- Content delivery separated from publication
- Unknown metrics displayed accurately

Rebuild the creator map, run the project’s required checks and `python3 tools/lumebook.py ripple`, and update the project summary with implemented behavior and remaining limitations.

Do not send outreach, publish externally, approve spending, commit, or push. Do not mark the component published.

Finish with the built preview, a concise explanation of the new daily workflow, verification results, and any remaining steps needed to activate the changes in the published artifact.
