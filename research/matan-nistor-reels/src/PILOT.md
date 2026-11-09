# Rubric pilot (09 Nov 2026)

Rubric v0 (`CODING_BRIEF.md` first version) was tried by hand on five varied Reels from their 4 fps hook frames (0 to 5 s), 1 fps contact sheets and covers. Transcripts were not ready yet, so speech came from the burned-in captions. These notes are also the reference I check the coders against for the same five Reels.

| Reel | Group | Views (grid) | What it actually is |
|---|---|---|---|
| DYJdtg5ovNb | top #1 | 8,233,826 | Street money handout at Azrieli: "show me you follow me" and get ₪490 |
| C_tCtPvoT3x | top #5 | 1,518,907 | Seated podcast-set monologue: don't take career advice from parents who didn't earn much |
| CsoiU5Ro_Bj | top #8 | 971,881 | Podcast clip (headphones, purple light) on media fear; caption says "פס יצור לשכירים" |
| DKwNYG7IRlN | top #11 | 703,485 | Audiobook voiceover ("ואז.. אתה מת") over a crash clip and Hollywood film clips |
| C-VS6pZxd9p | comparison for #5 | 51,000 | The same parents' advice claim, his own podcast set, stock b-roll, numbered text cards |

## What each Reel showed (observed)

**DYJdtg5ovNb.** First frame: Matan full body outside Azrieli Center, mic in hand, a stack of ₪200 notes raised. 0.25 s: cut to a close-up of the notes with "₪20,000" over them; 1.0 s back to him; 2.25 s he walks off. By 2.75 s the first encounter (a security guard), "אתה עוקב?" at 4.25 s, the guard pointing at 4.75 s. Word-by-word white captions in the middle of the frame, the other person's words in yellow, single emphasis words in pink. From 8 s a running counter sits top right ("סך כסף שחולק" in green, ₪200, ₪400, ₪490, ₪980, ₪1,480, ₪1,880, ₪2,460 by 1:18). Confetti overlays when money changes hands (6 s, 57 s), a ₪200 note graphic pops in (8 s), soldiers' faces blurred, POV shots of phones showing they follow him (39 to 41 s). 49 scene cuts in 83 s. Ends with him talking to camera on an escalator with a picture-in-picture of his profile (1:18 to 1:22): follow, and if you see me you get money.

**C_tCtPvoT3x.** Opens seated by a studio mic, side angle, "אני חי בסגנון חיים" as a 2-line phrase caption; at 0.75 s it cuts to him laughing with a backpack in a meadow, "של מעל 100,000₪ בחודש", then a helicopter (1.25 s), a cockpit selfie (1.75 s), a luxury apartment with coffee (2.25 s), sled dogs and a fjord (6 to 7 s), a beach and an infinity pool (10 to 11 s). His own footage proves the number. Gold "מועדון היזמים" logo top right throughout. The argument is an analogy: you wouldn't take advice from a beggar (a YouTube thumbnail of his own video is inset at 30 s), yet you take it from parents who are statistically poor. Ends on a club end card "כי מעל 2000 יזמים לא טועים!" (1:06). 38 cuts in 68 s.

**CsoiU5Ro_Bj.** Fades in from black on a single medium close-up: headphones, studio mic, purple and fire light. First caption, in red: "כולם סתומים." Phrase captions alternate red and yellow. One static shot for about 24 s, then a 5 s club end card ("כי 800 יזמים לא טועים!"). The caption ("פס יצור לשכירים") would have been coded as a skit; the video is a podcast monologue.

**DKwNYG7IRlN.** First frame: a motorcycle POV at a junction with "ואז -"; at 1.0 s a pickup crashes in front of it. The rest is voiceover from his audiobook over film clips (The Truman Show, Suits, Good Will Hunting, Whiplash, The Wolf of Wall Street) inside a rounded "old screen" frame on black, phrase captions with red and green emphasis words. Third-party footage throughout.

**C-VS6pZxd9p.** First frame: his own podcast set (headphones, studio mic, wood wall), pastel "סביבה מנצחת" badge top right, captions "גם אני" then "אני מניח בדיוק כמוכם": a mid-thought start with no claim in the first 2 s. Stock b-roll (a woman by a window, 16 s). Ends with text-only cards on a black grid ("#2 ... שהרוויחו יותר כסף מהם ולהקשיב להם").

## What the pilot changed (v0 to v1)

1. **Caption is not the video.** The topic and format guessed from captions were wrong for 2 of 5 (CsoiU5Ro_Bj, and DKwNYG7IRlN is a film-clip montage, not a talking head). Added `caption_vs_video_note`; topic and format are coded from the video only. The 20 comparisons were paired from captions before watching, so `pair_match` is filled after watching and weak pairs are reported as such.
2. **Opening quality needed two concrete fields.** The clearest top-vs-comparison difference was the first sentence: a self-contained claim with a number (C_tCtPvoT3x) against a mid-thought start (C-VS6pZxd9p). Added `first_sentence_standalone` and `number_or_money_in_first_3s`.
3. **Where b-roll comes from matters.** Own lifestyle footage used as proof (C_tCtPvoT3x) versus stock (C-VS6pZxd9p) versus third-party film clips (DKwNYG7IRlN). Added `broll_source` and the mechanism `visual_proof_of_claim`; added `rights_and_privacy` because film clips and identifiable bystanders limit what LumeBook can copy.
4. **Text devices the v0 lists could not hold:** a running money counter, speaker colour coding, numbered point cards. Added `running_counter_or_scoreboard`, `numbered_point_cards`, `colour_coding`.
5. **Edit moves:** overlay effects (confetti, banknote graphic), inset pictures (profile, YouTube thumbnail), fade from black, end cards. Added to `edit_moves`; added `ending_type` because 2 of 5 end on the same club end card.
6. **Story mechanisms:** `repeated_episodes_with_escalation` (encounter after encounter with a rising total) and `analogy`.
7. **Setting and branding:** `setting_type`, `persistent_branding`, `faces_blurred`.
8. **Transcripts.** The Mac was shared with another transcription job, so Whisper ran far slower than usual. Coders wait for the transcript; where it is still missing they code speech from the burned-in captions and say so (`evidence.transcript: "pending"`), and a later text-only pass checks those fields against the transcript.

Also seen: the #5 Reel has 2.4 likes per 1,000 Instagram views, against 10.1 for #3 (DCgV2ujI0cw). A low ratio on a very high count can mean reach outside the follower base, including paid promotion, but nothing public shows which; it is reported as an unexplained outlier, not as "paid".
