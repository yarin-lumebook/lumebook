# DJ Ben + Lume (Genjutsu, 16 Oct 2026)

Trend recreation of instagram.com/reel/DeHe0JlOvPk (@lucasthepug_, "Alors on danse"): a black pug plays a mini keyboard and laptop while a fawn pug dances, points, then jumps at the camera. Ben (toddler pack) is the DJ in place of the black pug, Lume replaces the dancing pug.

- `analysis/`: watch-video download (`source.mp4`, 1448x1078, 20 s, VP9 60 fps) and contact sheets
- `reference-pugs-h264.mp4`: source re-encoded to H.264 30 fps
- `ref-a-0-10.mp4`, `ref-b-10-20.mp4`, `ref-a-0-10-mute.mp4`: the two halves sent to Reframe
- `reframe/`: Higgsfield Reframe 9:16 480p outputs per half, the aligned first half and seam checks
- `reference-pugs-9x16-480p.mp4`: the joined 9:16 reference (496x864, 20 s, no audio) fed to Genjutsu
- `ben_front.png`, `lume_front.png`: character stills (copies of the pack `01_front.png`), image order 1 = Ben, 2 = Lume
- `prompt.txt`: Genjutsu prompt
- `dj-ben-lume-v1-480p.mp4`: result, 480x854, 24 fps, 20 s, no audio (add the sound in Instagram)
- `qc/`: contact sheets of the result

Jobs: Reframe b `514269b2`, Reframe a (muted) `fb25c965` (31.5 credits each at 480p for 10 s), Genjutsu `987a27b3-6df2-48b6-81d5-5ddf7332febd` (60 credits). Upscale still to do (the truck-box job used Bytedance pro upscale to 1080p).

What happened on the way:
- Reframe of the full 20 s failed twice with no message (refunded). Split into 10 s halves: the first half with audio came back `ip_detected` (most likely the song), the second half passed; the first half muted passed.
- The two Reframe halves were framed differently (second half 17% tighter). Matched with SIFT on the seam frames (scale 1.1684, shift 33.65, 57.07 px) and scaled and cropped the first half to match before joining.
- Known flaws in v1: Lume holds a microphone he invented from about 13 s to 17 s; at the final jump his fur is a bit darker and he smirks instead of the open grin.
