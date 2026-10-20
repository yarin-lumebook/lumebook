# Genjutsu: LumeBook in the flying truck box (16 Oct 2026)

Trend recreation. Reference (`inputs/reference-truck-box.mp4`, 6.8 s, from Downloads): a truck stacked with boxes passes under a footbridge, a box flies up onto the bridge, a man opens it and pulls out a red hoodie. Here the hoodie is the LumeBook birthday book (ספר היום הולדת של הילה), picked by Yarin.

- `inputs/book-birthday-hila.webp` / `.png`: the book mockup Yarin supplied (png is the upload copy)
- `prompt.txt`: the motion-transfer prompt
- `book-box-480p.mp4`: Genjutsu `hf_mult_motion_control`, 480p (480x854, 7 s), job `fa2245ab-8340-428c-bdd5-09deb7cac4c4`, 21 credits
- `book-box-1080p.mp4`: the final. Bytedance Video Upscale (`bytedance_video_upscale`, pro, preset aigc, 1080p; 1080x1922), job `1510cfcf-e392-4703-aa8e-10fa01b11246`, 10 credits

Notes:
- Genjutsu rebuilt the whole scene, not only the product: different truck, and the caption became "That's not gonna fit" instead of the original.
- The hoodie's motion leaves a white cloth that comes out with the book (reads like tissue paper). The cover's small subtitle line is garbled; logo and title are clean.

## v2: clean cover, no on-screen text, Hebrew voice (16 Oct 2026)

Yarin asked for the full video with no text and a Hebrew voice, using the cover without the title band (`inputs/book-birthday-clean.webp` / `.png`).

- `prompt-v2.txt`: same swap plus "no on-screen text" and "no cloth" lines
- `book-box-v2-480p.mp4`: Genjutsu 480p, job `68d91d00-c723-4131-b280-89809340959a`, 21 credits. No caption this time. The book flexes a little as it is lifted, and a small grey cloth is still in the box
- `book-box-v2-1080p-silent-src.mp4`: Bytedance pro upscale to 1080p, 10 credits (carries the original English audio, do not post)
- `book-box-v2-1080p-hebrew.mp4`: the final, 1080x1922, 7 s, upscale job `b302ac87-6cdb-4770-8239-5fd3d6944684` (took about 80 minutes in the queue; the first try dropped its connection) with the Hebrew soundtrack
- `book-box-v2-480p-hebrew-preview.mp4`: the same soundtrack on the 480p, sent as a quick preview

Audio (`audio/`):
- Original voice (Whisper): "Yo, that truck is sick! Wait, it's not gonna fit" from 0 to 2.9 s, laughter 3.0 to 3.9 s, then music with no words
- Hebrew lines, ElevenLabs Eleven v4 on fal, voice Liam, `language_code he`: "יו, איזו משאית מטורפת!" (`he-liam-1.mp3`) and "רגע, היא לא עוברת!" (`he-liam-2.mp3`). Will versions kept as an alternative (`he-will-*.mp3`)
- `amb-highway-0-3.6s.mp3`: ElevenLabs Sound Effects v2, motorway from a footbridge, lorry approaching, for the first 3 s
- `mix-hebrew.wav`: ambience 0 to 3.4 s + Hebrew line 1 at 0.05 s (sped 1.2x) + line 2 at 2.12 s (1.1x, phone-mic EQ) + the original audio from 3.0 s on (laughter and music)
- Tried and failed: subtracting ElevenLabs Audio Isolation output (`ref-voice-isolated.*`) from the original to keep the real background. The isolated voice is resynthesised, not phase-aligned, so the English stayed fully audible. Higgsfield's dubbing workflow has no Hebrew
