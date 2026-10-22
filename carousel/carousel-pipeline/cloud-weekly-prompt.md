WEEKLY BATCH, CLOUD RUN (Yarin, 16 Oct 2026: "lets move to a weekly batch, 14 games and books carousels, 42 kid and expert, every thursday night", "one pool for the week, dont repeat the same topic twice", about 10 to 20 percent on things that happen in Israel, "mix their order instead of games and then books"). Since 18 Oct 2026 there are NO games and books carousels (Yarin: "i dont want the games and books carousels anymore"): never write reco-carousel.json or reco-carousel-2.json and never run finish-reco.

You run unattended in a cloud clone of github.com/yarinbruner/lumebook, not on Yarin's Mac. Use paths relative to the repo root, never ask a question, never post, message or publish anything, never call fal.ai or any paid service.

What you make: 7 packs on 7 different topics, each a normal drafts/DATE folder with the six kid and expert options (pack.json). That is 42 options. Slot 1 is the Israeli event pack (topic-bank.md "Israeli events"): 6 of 42 options, about 14 percent. The dates are only keys; Yarin sees the batch as one pool.

## 0 · Set up (you, the coordinator)

1. Chrome for the slide PNGs: `python3 -c "import sys; sys.path.insert(0,'carousel/carousel-pipeline/scripts'); import carousel_lib as l; print(l.CHROME)"`. If it prints None: `apt-get update && apt-get install -y chromium` (sudo when not root; README section 9 has the Google Chrome fallback).
2. Plan the week: `python3 carousel/carousel-pipeline/scripts/nightly.py week-plan`. It merges the history the earlier cloud runs pushed to their branches, then prints the plan (also written to carousel/carousel-pipeline/drafts/batches/<id>.json): the batch id, 7 slots with date, topic (slot 1: the event slot with its fallback topic). If it stops because too few topics are free, stop and say so.
3. Read what Yarin thought of the earlier batches: `python3 carousel/carousel-pipeline/scripts/grades.py brief` (Yarin's 1 to 5 grades and reasons from the Carousel Machine grading page, grades.json on main). Keep its output; every slot brief below gets it. If it says there are no grades, go on without.
4. Create the branch `batch/<id>` (if it exists on origin, `batch/<id>-2`), then `git add carousel/carousel-pipeline/drafts/batches/<id>.json carousel/carousel-pipeline/history.json`, commit "Weekly batch <id>: plan" with the GitHub no-reply email, and push that branch. Never push to main, never open a pull request.

## 1 · Build the slots

Run the 7 slots as subagents, at most 3 at a time, slot 1 in the first wave. Give each subagent this brief (fill in N and DATE):

> Build slot N of the LumeBook weekly batch, date DATE. Read carousel/carousel-pipeline/cloud-nightly-prompt.md: its CLOUD RUN NOTES for Chrome, network and skills (ignore its Delivery and branch notes), then follow it from "Build tomorrow morning's LumeBook carousel review pack" to step 6b, with these overrides: (a) step 1 is `python3 carousel/carousel-pipeline/scripts/nightly.py start --date DATE`; its `batch` block gives your topic: use exactly `batch.topic_id`, or, when `batch.event_slot` is true, follow `batch.rule` to find one thing that happens in Israel in the event window and write the pack on it (topic-bank.md "Israeli events": confirm the date in a source you read today; a hard moment follows official guidance on talking with children and records it in talk_source; no politics, no graphic detail, no fear or blame aimed at the parent). (b) Skip step 6b and everything about the games and books carousel: write no reco-carousel.json and do not run finish-reco (none since 18 Oct 2026). (c) Before the hook slate, read Yarin's grades (pasted below this brief): write toward what scored 4 to 5 and away from what scored 1 to 2, following the written reasons; a reason beats a pattern, the same reason twice is a rule, and the skill rules and the validator still win. Grades are taste, never evidence that a hook works. (d) Do not commit, push or touch other slots' folders. Report: topic, the six option ids with child name and slide 1 hook, which grade lessons you applied, and anything you could not do.

Paste the output of `grades.py brief` from step 0.3 under the brief.

When a slot reports `finish` VALID, commit it on the batch branch: `git add carousel/carousel-pipeline/drafts/DATE carousel/carousel-pipeline/history.json`, commit "Weekly batch <id>: slot N (<topic>)" and push. Push after every slot, so a run that stops halfway still delivers what is done. A slot that fails twice: note it and go on.

## 2 · Check the batch

`python3 carousel/carousel-pipeline/scripts/nightly.py batch-check <id>` re-records the history and lists problems across the batch: a repeated topic, a missing pack, no event pack. Fix every ERROR in the later slot (rewrite that pack on its planned topic, then run finish on it again), commit and push. Run batch-check until it prints VALID.

## 3 · Final message, short

Batch id and branch; per slot: date, topic (the event slot: event name, date, tone, source), the six options (id, child, slide 1 hook); batch-check result; the voice status; the grade lessons the slots applied (one line each, in Yarin's words where possible). If something blocked the run, name the exact step and command that failed.
