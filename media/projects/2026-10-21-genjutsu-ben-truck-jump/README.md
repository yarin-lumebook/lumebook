# Ben and the jumping toy truck (Genjutsu, 21 Oct 2026)

Reference: `generation.mp4` from Yarin's Downloads (11 s, 720x1280, 24 fps): a man sits in a folding camping chair in the desert at sunset, raises his fist, and a black six-wheel Mercedes G-wagon jumps over him, lands behind him and rolls up beside the chair. Yarin asked for the last 8 s only, Ben in the chair and a toy truck instead of the car.

- `reference-original.mp4`: the full clip as downloaded; `analysis/sheets/` has the watch-video contact sheets
- `reference-last8-mute.mp4`: 3.04 s to the end (7.96 s), audio stripped (a known song can trigger `ip_detected`)
- `ben_front.png` (Image 1): copy of the toddler pack `01_front.png`
- `prompt.txt`: Genjutsu prompt (giant red and yellow plastic toy truck at the car's size, "no on-screen text, no license plate, no watermark")
- `genjutsu-job.txt`: job id. Quoted 24 credits at 480p (56 at 720p, 160 at 1080p; Bytedance pro upscale to 1080p 10 more)
- `ben-truck-jump-v1-480p.mp4`: result, 480x854, 24 fps, 8 s, no audio. Job `5f93046a-51e8-4800-8172-59a3944a7e65`, 24 credits
- `ben-truck-jump-v1-480p-sound.mp4`: same video with the reference's original audio from 3.04 s
- `qc/v1/`: contact sheets; `qc/v1-key-frames.jpg`: frames at 1.0, 4.4, 6.9 and 7.8 s

Notes on v1: Ben is on model (glasses, stud earring, haircut, white T-shirt, barefoot) and copies the pose and the fist raise (0.3 to 2.2 s). Genjutsu shrank the chair to his size. The truck reads as a giant red and yellow plastic toy, but keeps the G-wagon shape and six wheels, and its grille carries an embossed Mercedes star (clearest at 4.4 and 6.9 s) despite "no logos" in the prompt. No driver, no plate, no on-screen text. Upscale to 1080p not done.

## Caption versions for trial reels (21 Oct 2026)

Yarin asked for "3 versions" and gave five captions, so there are five. `build_versions.py` + `captions.json` (run with the watch-video `.venv` Python, it has Pillow) write them to `captioned/`. All 1080x1920, 24 fps, 8.04 s, original audio. Caption white bold SF Hebrew with a soft shadow (same look as `2026-10-19-genjutsu-ben-dance-lume`), starting at y 290, just below the top 14% that the Reels player covers (safe zone in `research/israeli-product-reels/playbook.md`). Each version has a seeded random flip (picture only, never the caption) and one slight steady zoom, different in each (1.03 to 1.09), with the crop placed at random sideways and between the top and the centre vertically, so Ben's head never rises into the caption. (A first render had zoom punch-ins; Yarin wanted only a slight zoom per version.) Exact values: `versions.json`. Check sheet: `qc/captions-sheet.jpg` (magenta line = 14%).
- `ben-truck-jump-caption-1.mp4`: "כשאני אומרת לו "נסיך של אמא"" (Yarin's text had "אומרת" twice; one removed), not flipped, zoom 1.033
- `ben-truck-jump-caption-2.mp4`: "POV אמא גאה בי", not flipped, zoom 1.07
- `ben-truck-jump-caption-3.mp4`: "כשהקטן מנסה להסביר לי משהו ואני לא מקשיבה ובסוף מתברר שצדק😅", three lines at 60 px, flipped, zoom 1.045
- `ben-truck-jump-caption-4.mp4`: "הקטן כשסוף סוף קיבל צעצוע שרצה😂", flipped, zoom 1.062
- `ben-truck-jump-caption-5.mp4`: "כשהוא אומר "אמא אני כבר יכול להתקלח לבד"", not flipped, zoom 1.087
The 480p picture is scaled up, not upscaled with a model. The Mercedes star on the grille is still in every version.
