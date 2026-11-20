# Brief: break down short-form videos for LumeBook

## Who this is for
LumeBook (Hebrew: לומיבוק) is an Israeli brand selling AI-personalised children's books: a parent uploads a photo of their child, AI illustrates the child as the hero, the family sees a free preview and orders a printed book. Its social media manager is 24, has no kids, works alone, and makes short-form video (Reels, TikTok) and carousels by shooting, editing or AI-generating them. They want to learn from kids' brands that do well on social with: child development and milestones (ages 1-10), novelty ideas, experts, and everyday parent-child moments told creatively. Their content pillars: developmental, novelty, craft (how it's made), likeness, FAQ, gifters, milestones, first look. They care most about retention and expert content, on Instagram and TikTok.

## Your inputs per video (folder `analysis/<id>/`)
- `meta.json`: platform, url, account, views, likes, comments, account median views, outlier_x (views / account median), like_rate_pct, caption, duration.
- `frames/index.json` + `frames/sheet_NN.jpg`: frames every 1-2 s at full height, 6 per sheet, timestamp in yellow above each frame. Open EVERY sheet. Open single frames in `frames/` when you need to read small text.
- `whisper.srt` / `whisper.txt`: machine transcript from local Whisper (Hebrew or English). It can mishear words, invent text over music, or be empty. Treat it as "spoken" evidence of medium reliability. If it is missing or empty, say there is no usable speech transcript. You cannot hear music or tone: never describe a song, sound effect or voice quality unless the transcript marks it (e.g. "(upbeat music)").

## Evidence rules
- Label each beat's content: what you SEE in frames (observed), what the transcript SAYS (spoken), and what you conclude (inferred). Never present a spoken claim as something the video visibly proves.
- Quote on-screen Hebrew exactly as it appears in the frame, then give an English translation. If you cannot read it confidently, write `[unclear]` instead of guessing. Do not translate Whisper's Hebrew into on-screen text.
- Do not identify real people beyond the account name and what the caption or on-screen text states.
- like_rate_pct under 0.3 combined with a high outlier_x usually means paid promotion; say so as an inference, not a fact.
- No em dashes anywhere in your output. Use commas, colons or periods.

## Output: write `analysis/<id>/breakdown.json` (valid JSON, escape quotes) with exactly these keys
```
{
 "id": "",
 "one_line": "what the video is, in one plain sentence",
 "niches": ["developmental_milestone" | "novelty" | "expert" | "parent_child_daily"],   // 1-2 values
 "format": "pov_skit | stitch_reaction | talking_head | text_on_broll | hands_demo | screen_recording | animation | repost_curation | creator_collab | slideshow | podcast_clip | asmr | other",
 "made_by": "brand_inhouse | creator_collab | expert_self | repost_of_creator | unclear",
 "hook": {"visual": "", "on_screen_text": "original + (English)", "first_spoken_line": "original + (English) or null", "hook_type": "problem_first | curiosity | contrarian | outcome_first | identity | relatable_moment | question | mistake | demonstration | shock_surprise | story | reaction | other", "why_it_stops_the_scroll": ""},
 "beats": [{"start": 0.0, "end": 0.0, "observed": "", "spoken": "", "on_screen_text": "", "role": "hook | setup | escalation | turn | payoff | proof | cta"}],
 "payoff": "what the viewer gets and when (timestamp)",
 "retention_devices": ["open_loop", "list_or_countdown", "fast_cuts", "burned_in_captions", "payoff_at_end", "relatable_conflict", "curiosity_gap", "before_after", "save_worthy_info", "loop_ending", "direct_address", "kid_reaction", "emotional_turn", "comment_prompt", "series_format", "split_screen_or_pip"],
 "cta": "what it asks the viewer to do, or none",
 "share_or_comment_trigger": "why someone would send, save or comment",
 "why_it_worked": ["3 short points tied to evidence and to the numbers in meta.json"],
 "paid_signal": "no | likely | unclear, with one-line reasoning",
 "solo_route": {
   "verdict": "solo_shoot | solo_ai | solo_edit_or_repost | needs_expert_or_kids | not_replicable",
   "how": "2-4 concrete steps a 24-year-old with no kids could follow alone (phone, CapCut, Canva, LumeBook's own AI book illustrations, AI image/video/voice tools). Be specific about the AI step if there is one.",
   "needs": "what they would still need: permission to repost, a barter expert, a relative's child with parental consent, nothing",
   "effort": "low | medium | high"
 },
 "lumebook_version": {"pillar": "developmental | novelty | craft | likeness | faq | gifters | milestones | first_look", "hook_he": "a short Hebrew hook line for LumeBook's version (write לומיבוק, never לומבוק)", "concept": "1-2 sentences in English"},
 "evidence_notes": "what was observed vs spoken vs inferred, transcript quality, anything you could not verify",
 "frames_cited": ["frames/f_000_000.00s.jpg", "..."]
}
```
Keep beats to 4-10 entries covering the whole video. Be concrete and specific to THIS video; avoid generic marketing advice. After writing all your files, validate each with `python3 -c "import json;json.load(open('<path>'))"` and fix any that fail.
