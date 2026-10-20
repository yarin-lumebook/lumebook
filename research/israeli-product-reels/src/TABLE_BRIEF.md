# Coding brief: the 8-question table (18 Oct 2026)

You are adding one row per Reel to LumeBook's product Reels playbook. LumeBook sells personalised children's books in Israel; its solo social media manager (Yarin) films Reels with a phone at home, usually without a child on camera. Every Reel below was already watched and coded on 15 Oct (`src/coded/CODE.json`) and checked by a human against its frames. Your job is a second, sharper pass that answers eight questions for each Reel, each with **what happens** (observed) and **why it works or doesn't** (interpretation backed by the research principles below).

Accuracy beats coverage. Never invent dialogue, text, shots, timestamps, numbers or creator details. You cannot hear audio: speech comes only from the transcript, music only when the transcript shows lyrics, a music sticker is visible, or there is clearly no speech.

## Inputs per Reel CODE

Media root: `/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-10-15-israeli-product-reels/`. Project folder: `/Users/yarinbruner/Claude/Projects/Lumebook/research/israeli-product-reels/`.

- `src/coded/CODE.json` (project folder): the first-pass coding. Shots with timestamps, hook, captions style, CTA, audio, proof, product timing. Start from it, but correct it when the frames say otherwise (note corrections in `not_verified`).
- `analysis/CODE/sheet_NN.jpg` (media root): contact sheets, 6 frames each, one frame per second (1.5 s for long videos), timestamp above each frame. **Open every sheet**: question 8 needs the on-screen text through the whole Reel, and question 2 needs what changes every few seconds.
- `analysis/CODE/whisper.srt`: machine transcript (Hebrew, first 90 s). It mishears words and turns lyrics into "speech"; "תודה רבה" alone on a music Reel means no speech. Prefer the creator's burned-in subtitles when quoting.
- `videos/CODE.info.json`: `description` is the caption (question 8).
- `src/media_info_15oct.json` (project folder): public plays, likes, comments read 15 Oct 2026. Use only as context; never claim reach, retention, saves, shares or sales.
- For the eight deep dives (DTugYwmDNKa, DWW7cLNDZvv, Dc6VXOdMWOv, Ddrev0jjauL, DcZCOp4ItbM, Dd5sq3TI1I5, DU3kze_iAnR, DdWglWIKur-) also read the matching section of `breakdowns.md` (project folder); it was written from every frame.

## The research principles you cite

`smm-research/principles-index.md` (project folder) lists every principle with an ID (H1, R3, C2, T4, S1, F2, E5, K3...), its rule, evidence strength and what to look for; `smm-research/principles.md` has the sources if you need more. Read the index before your first Reel. In every `why`, name the principle IDs that explain the choice, and put them in `refs`. Rules for citing:

- Cite a principle only when the Reel visibly does (or visibly breaks) what the principle describes. Breaking a principle is worth citing too ("text covers the face, against T3").
- When a principle's strength is "weak" or "contested", don't lean on it alone.
- If nothing in the list explains a choice, say so in plain words and leave `refs` empty for that part. Don't stretch a principle to fit.
- No outside facts or numbers of your own. The principles file is your only research source.

## Output

Write `/Users/yarinbruner/Claude/Projects/Lumebook/research/israeli-product-reels/src/table/CODE.json` (valid JSON, UTF-8, escape quotes inside strings, no em dashes anywhere). English, with Hebrew quoted exactly as it appears. Word limits are maximums; shorter is better.

```json
{
  "code": "",
  "verdict": "works | partly | weak (for what this Reel is trying to do, judged on craft and clarity, never on counts)",
  "one_line": "the one thing to copy from this Reel, 20 words max",
  "q1_hook": {
    "what": "observed 0-3 s: first frame, first words (said), first text (on screen), 40 words max",
    "hook_type": ["one or more of: problem, audience_callout, question, result_first, bold_claim, curiosity_gap, pattern_interrupt, face_to_camera, product_reveal, relatable_moment, list_promise, price_or_offer, none_clear"],
    "text_in_first_frame": "yes | no",
    "face_in_first_frame": "yes | no",
    "why": "why it holds (or loses) the viewer, with principle IDs, 55 words max",
    "refs": []
  },
  "q2_flow": {
    "beats": [
      {"t": "0:00-0:03", "what": "observed, 18 words max", "does": "hook | setup | problem | turn | demo | proof | detail | objection | payoff | reveal | re_hook | cta | filler", "why": "what this beat does for retention or interaction, 18 words max"}
    ],
    "retention_devices": ["any of: open_loop, numbered_list, reveal_held_back, new_visual_every_few_s, re_hook_mid, story_arc, payoff_at_end, loop_ending, repetition, none"],
    "interaction_prompts": "observed invitations to comment, share, save or tag (question on screen or in the caption, a relatable moment to send, a useful tip to save), or 'none', 35 words max",
    "why": "why the flow keeps people watching (or where it sags), with principle IDs, 60 words max",
    "refs": []
  },
  "q3_cta": {
    "what": "the exact CTA in the video (said or written, with time) and in the caption, or 'none', 40 words max",
    "placement": ["any of: on_screen_end, on_screen_early, spoken, caption, none"],
    "why": "why it works or what is missing; for no CTA, what that costs or why it still works, with principle IDs, 50 words max",
    "refs": []
  },
  "q4_shown": {
    "what": "what appears on screen and when: the product, which parts, people, proof, price, screen recording, 45 words max",
    "proof_type": ["any of: in_use, result, before_after, side_by_side, child_reaction, testimonial_story, screen_recording, price, expert_authority, none"],
    "why": "why showing this (and in this order) persuades or doesn't, with principle IDs, 55 words max",
    "refs": []
  },
  "q5_edit": {
    "what": "number of shots, average shot length, cut style (straight, jump cuts, transitions), speed changes, how text and voice are timed, the ending, 45 words max",
    "why": "why the edit helps or hurts attention and clarity, with principle IDs, 50 words max",
    "refs": []
  },
  "q6_topic": {
    "what": "what the Reel is about in one line, and the viewer need it serves, 30 words max",
    "topic_type": ["one or more of: milestone_problem, useful_tip, product_showcase, gift_occasion, personal_story, humour_skit, list_review, unboxing, making_diy, child_using_it, expert_advice"],
    "why": "why this topic gets watched, saved or shared by this audience, with principle IDs, 50 words max",
    "refs": []
  },
  "q7_filmed": {
    "what": "shot types, framing, angles, phone held or propped, light, setting, who is on camera (no names or descriptions of children beyond an age range), 45 words max",
    "why": "why filming it this way works on a phone screen or where it fails, with principle IDs, 50 words max",
    "refs": []
  },
  "q8_text": {
    "on_screen": "the key on-screen text through the Reel, quoted in Hebrew with times (hook text, labels, subtitles style), and where it sits in the frame, 70 words max",
    "caption": "the caption's first line quoted in Hebrew, then its structure: length, CTA, question, hashtags, disclosure, 50 words max",
    "why": "why the words on screen and in the caption work or don't, with principle IDs, 55 words max",
    "refs": []
  },
  "weak_points": "what to avoid copying, 40 words max",
  "lumebook_takeaway": "how Yarin films the copyable part with a phone and no child, 30 words max",
  "not_verified": "anything you could not establish, and any correction to src/coded/CODE.json"
}
```

Beats: one per change that matters (a new shot, a new line of text, a new idea), usually every 2 to 5 seconds, at most 10 beats; merge long stretches of the same thing into one beat.

## Rules

- **What** fields are observed only. **Why** fields are interpretation; they never repeat the what, they explain it.
- Quote Hebrew exactly; never correct it. Mark transcript quotes "(transcript)". Keep quotes short.
- Do not describe children beyond what is needed ("a toddler", "a girl about 5"). No names of children, even when the book shows one; write "the child's name".
- Never claim a Reel's reach, watch time, retention, saves, shares or sales. Plays and likes are public counts only, and a high count is not proof that a choice worked.
- No em dashes in your output.

## Working order

One Reel at a time: open `src/coded/CODE.json`, every contact sheet, the transcript and the caption; write `src/table/CODE.json` straight away; then move on. Images you opened earlier may be dropped from your view once many are open; reopen a sheet before writing a field that depends on it. Never fill a visual field from memory or guesswork: if you could not see it, say so in `not_verified`.

Before writing each file, re-read it against this checklist: every `why` cites at least one principle ID or says plainly that none applies; no em dashes; no child's name; Hebrew copied exactly; valid JSON (run `python3 -c "import json,sys; json.load(open(sys.argv[1]))" FILE`).

When all your Reels are done, reply with one line per Reel: CODE, verdict, one_line.
