# Coding brief: @matan.nistor Reels (rubric v1, after the 5-Reel pilot of 09 Nov 2026)

You are coding Instagram Reels by @matan.nistor (Israeli entrepreneur and business coach, Hebrew, 205K followers on 09 Nov 2026) for a creative study. Goal: reverse engineer what makes his Reels work (visuals, editing, text, story, retention mechanisms, engagement, conversion). Accuracy beats coverage. Never invent dialogue, shots, timestamps, sounds, metrics or audience reactions.

## Inputs per Reel CODE

- `research/matan-nistor-reels/src/dossiers/CODE.json`: metrics (already computed, do not recompute), caption, `comments_sample` (with how it was sampled), and `pair` (the matched Reel in the other group).
- `media/projects/2026-11-09-matan-nistor-reels/analysis/CODE/index.json`: `duration`, `cuts` (ffmpeg scene changes, threshold 0.28: misses soft cuts and punch-in zooms on the same shot, can fire on fast motion or flashes), `rms_db_per_0_5s` (audio loudness per half second; about -90 = silence, quieter than -40 = near silence, -30 to -12 = speech or music).
- `analysis/CODE/hook_01.jpg ... hook_04.jpg`: the first 5 seconds at 4 frames per second (timestamps above each frame). **Open all of them.**
- `analysis/CODE/sheet_NN.jpg`: the whole Reel, 6 frames per sheet, one frame per second (1.5 s for Reels over 90 s). **Open every sheet, in order.**
- `analysis/CODE/whisper.srt`: machine transcript (Whisper turbo, Hebrew, timestamps). It mishears words, transcribes song lyrics as speech, may output "תודה רבה" or nothing on music. Burned-in captions on the frames are usually more reliable for exact wording. If the file is missing, wait 2 minutes and check again (up to 10 minutes). If it is still missing, code speech from the burned-in captions (hook frames are 4 fps, so hook captions are complete; later captions are sampled once a second and can miss words), write `"transcript": "pending"` in `evidence`, and list in `evidence.limits` which fields came from captions only. A later pass checks them against the transcript.
- `media/projects/2026-11-09-matan-nistor-reels/covers/CODE.jpg`: the cover image shown on the grid.

You cannot hear. Speech comes only from the transcript plus mouth movement on frames. Music: the dossier's `audio_type` is `licensed_music` with a title when Instagram attributes a song; `original_sounds` can still contain music mixed by the creator. Say "music likely" only with evidence (licensed_music, lyrics in the transcript, steady loudness in stretches with no speech, a music sticker); otherwise "unclear". Sound effects: say "not determinable" unless a visual cue makes one obvious, and label it as inferred.

## Output

Write `research/matan-nistor-reels/src/coded/CODE.json` (valid JSON, UTF-8, escape inner quotes). Fill every field; use "unclear" or "not visible" instead of guessing. Lists use the fixed vocabularies below so counts are comparable; add `"other: ..."` only when nothing fits.

```json
{
  "code": "",
  "evidence": {"hook_sheets_opened": 0, "sheets_opened": 0, "sheets_total": 0, "transcript": "good | partial | poor | music only | none (no speech) | unavailable", "cover_opened": true, "comments_read": 0, "limits": "anything you could not see or establish"},

  "topic": "money_giveaway | anti_school_degree | employee_vs_owner | wealth_mindset | business_tactics | marketing_social_media | relationships_gender | travel_lifestyle | couple_life | mortality_meaning | personal_story | own_offer_promo | podcast_guest_talk | humor_skit | other: ...",
  "topic_detail": "one line in English",
  "audience": "who it speaks to, from words and visuals (e.g. salaried employees in their 20s, aspiring business owners, his followers)",
  "format": "talking_head_direct | street_interaction | podcast_or_interview_clip | stage_or_lecture_clip | skit_or_pov | vlog_montage | tour_or_reveal | text_only | b_roll_voiceover | tv_clip | other: ...",
  "setting_type": "studio_podcast | street_public | home | travel_location | stage_event | car | office | mixed",
  "caption_vs_video_note": "if the caption suggests a different topic or format than the video shows, say so (the caption 'פס יצור לשכירים' sat on a podcast clip, not a skit)",
  "purpose": "reach_growth | community_engagement | lead_capture | sell_own_offer | drive_to_long_form | personal_brand | entertainment",

  "opening": {
    "first_frame": "what the very first frame shows (subject, framing, text)",
    "s0_1": "what happens 0-1 s (picture, speech, text, any cut)",
    "s1_3": "1-3 s",
    "s3_5": "3-5 s",
    "visual_hook": "", "spoken_hook": "machine transcript words 0-3 s or 'none'", "text_hook": "exact Hebrew on screen 0-3 s or 'none'",
    "hook_types": ["bold_claim_contrarian | money_or_number | direct_question | curiosity_gap | identity_callout | in_medias_res | visual_spectacle_or_location | pov_or_skit_setup | list_promise | warning_or_urgency | personal_confession | status_or_social_proof | challenge_or_giveaway | humor"],
    "motive": ["question | tension | benefit | surprise | emotion | status | humor | utility"],
    "topic_clear_at_s": 0.0,
    "payoff_promised_at_s": "seconds, or 'never stated'",
    "first_sentence_standalone": "yes | no: does the first spoken or written sentence make sense with no prior context (a mid-thought start like 'גם אני' is no)",
    "number_or_money_in_first_3s": "yes (which) | no",
    "works_without_sound": "yes | partly | no, with why"
  },

  "visual": {
    "shot_size_main": "close_up | medium_close | medium | wide | mixed",
    "angle": "eye level | low | high | selfie arm's length | mixed",
    "eye_contact": "mostly | partly | rarely | n/a",
    "subject_placement": "",
    "setting": "", "lighting": "", "color_contrast": "",
    "on_camera": ["matan | partner (Livnat) | other adult | crowd | none"],
    "props_and_gestures": "",
    "supporting_footage": "b-roll, inserts, screen recordings, photos, or 'none'",
    "broll_source": ["own_lifestyle_proof | own_event_or_client_footage | stock_footage | film_or_tv_clips_third_party | viral_clip_third_party | screen_recording | none"],
    "persistent_branding": "logo bug / podcast badge / handle watermark and where, or 'none'",
    "faces_blurred": "yes | no (bystanders or participants blurred)",
    "visual_progression": "how the picture changes across the Reel, with timestamps",
    "cover_matches_video": "yes | partly | no, with why",
    "ui_interference": "text or key action inside the top 14% / bottom 35% of the frame (Instagram's overlay zone, working rule), or 'none seen'"
  },

  "editing": {
    "cuts_detected": 0, "avg_shot_s": 0.0,
    "edit_moves": ["jump_cut | punch_in_zoom | slow_push | transition_effect | fade_from_black | reframe | insert_broll | inset_picture (screenshot, thumbnail, profile) | overlay_effect (confetti, stickers, money graphics) | text_animation | speed_change | split_screen | end_card | none"],
    "edit_function": "what the edits add: information, emotion, clarity, or stimulation only, with examples",
    "pacing_changes": ["t=..s: what speeds up or slows down"],
    "ending": "what the last 3 s show and say",
    "ending_type": "end_card_brand_promo | direct_cta_to_camera | punchline | loop | cliffhanger | summary_or_point_card | abrupt | fade_out",
    "loop": "yes (last moment leads back into the first) | partial | no, with how",
    "rewatch_reasons": "interpretation"
  },

  "sound": {
    "speech": "direct_to_camera | voiceover | dialogue | lecture_mic | none",
    "delivery": "pace, energy, pauses (cite loudness gaps or transcript gaps with timestamps)",
    "music": "likely (evidence) | unclear | none evident",
    "sfx": "not determinable | inferred: ...",
    "sync": "how speech, cuts and text line up"
  },

  "text": {
    "on_screen": ["word_by_word_captions | phrase_captions | headline_persistent | label_or_title_card | numbers_or_prices | running_counter_or_scoreboard | numbered_point_cards | none"],
    "colour_coding": "how caption colours are used (per speaker, emphasis word, alternating lines) or 'none'",
    "placement": "", "style": "font weight, colour, background box, emphasis colour or highlight",
    "density_and_read_time": "",
    "relation_to_speech": "verbatim | summary | adds information | contradicts or jokes | n/a",
    "language": "sentence length, specificity, tone, humor, slang or audience words; short quotes only (max 12 words each)",
    "caption_structure": "first line, length, list, hashtags, CTA, how it relates to the video",
    "rtl_notes": "Hebrew rendering, mixed numbers or English, any broken RTL"
  },

  "story": {
    "structure": "claim_reasons_close | setup_escalation_payoff | list | story_arc | qa_or_interview | demonstration | montage | announcement | other: ...",
    "setup": "", "stakes": "", "progression": "", "payoff": "", "resolution": "",
    "mechanisms": ["open_question | delayed_reveal | demonstration | numbered_list | escalating_examples | repeated_episodes_with_escalation | callback | contrast_before_after | conflict_or_argument | twist | social_experiment | analogy | visual_proof_of_claim | none"],
    "new_info_or_visual_change_s": [0.0],
    "payoff_delivered": "yes | partly | no, with why",
    "friction_points": ["t=..s: possible friction (repetition, slow setup, unreadable text, confusing) - interpretation"]
  },

  "engagement": {
    "explicit_prompts": [{"type": "comment_keyword | comment_opinion | tag_friend | share | save | follow | like | watch_to_end | poll | story_visit | none", "where": "video | caption | both", "at_s": "seconds or 'caption'", "wording": "short exact quote"}],
    "implicit_triggers": ["relatability | disagreement_bait | identity | utility | humor | emotion | status_aspiration | curiosity | money_reward"],
    "comment_categories": {"appreciation_praise": 0, "agreement": 0, "disagreement_criticism": 0, "question_info_request": 0, "purchase_or_offer_intent": 0, "keyword_entry": 0, "giveaway_entry_or_request": 0, "tag_or_mention": 0, "joke_or_emoji_only": 0, "personal_story": 0, "other": 0},
    "comment_notes": "what the sampled comments show (short quotes, max 12 words); say the sample is not representative",
    "creator_replies_in_sample": 0,
    "creator_reply_pattern": "what his replies do (thanks, answers, keyword DM promise, argues) or 'none seen'"
  },

  "conversion": {
    "next_action": ["comment_keyword_for_dm | link_in_bio | story_link | follow | watch_long_form | buy_ticket_or_course | join_club | read_book | none"],
    "cta_timing": "seconds in video or 'caption only' or 'none'",
    "offer": "", "benefit": "", "proof": "", "objection_handling": "", "urgency": "", "effort_required": "low | medium | high",
    "funnel_entry_visible": "describe what is visible (e.g. 'comment אני to get the episode' = visible DM funnel entry, automation not verified) or 'none'",
    "cta_fits_content": "yes | partly | no, with why",
    "destination": "visible destination and whether it matches the promise, or 'not visible'"
  },

  "pair_match": {"topic": "same | similar | different", "format": "same | different", "duration": "within 30% | not", "notes": "only for comparison Reels: how well it matches its pair after watching; for top Reels write 'n/a'"},

  "rights_and_privacy": "third-party film, TV or viral footage used (yes/no, what); minors or bystanders identifiable (yes/no); matters for what LumeBook can copy",
  "why_it_may_work": "interpretation, 2-3 sentences, tied to observed evidence",
  "why_it_may_underperform": "interpretation, 1-2 sentences",
  "standout_moments": [{"t": 0.0, "what": "a moment worth studying and why"}]
}
```

## Rules

- Observed facts in descriptive fields; opinions only in `why_*`, `rewatch_reasons`, `friction_points`, `standout_moments` and label them as interpretation.
- Quote Hebrew exactly as on screen; never correct it. Mark transcript quotes as machine transcript. Short quotes only (max 12 words); summarise, never copy a whole script.
- Timestamps come from the frame labels or the transcript; say "about" when between frames.
- Do not claim retention, completion, reach, sales or leads. Do not call a Reel organic or paid; only report the visible paid-partnership label.
- Comments: count categories only over the sampled comments you read; never generalise to the whole audience.
- No em dashes in your output.
- Work one Reel at a time: open its hook sheets, every sheet, the transcript, the cover and the dossier, write its JSON, then move on. If an image you need comes back as "media removed", open it again. Never fill a visual field from memory.
- When done, reply with one line per Reel: CODE, format, topic, one-line summary, anything you could not verify.
