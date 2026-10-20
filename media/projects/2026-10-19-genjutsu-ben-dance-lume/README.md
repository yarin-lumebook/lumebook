# Ben dances, Lume films (Genjutsu, 19 Oct 2026)

Reference: a 15 s 9:16 reel from Yarin's Downloads (`cd697f0e-...mp4`): a black and white cat dances upright in a hallway while a tabby seen from behind holds a phone and films it. Ben replaces the dancing cat, Lume replaces the tabby that films.

- `reference-cats-mute.mp4`: the reference with audio stripped (a known song can trigger `ip_detected`); `analysis/` has the watch-video contact sheets
- `ben_front.png` (Image 1), `lume_front.png` (Image 2): copies of the pack `01_front.png`
- `prompt.txt`: Genjutsu prompt (includes "no on-screen text, no watermark", the reference carried an Instagram handle)
- `ben-dance-lume-v1-480p.mp4`: result, 480x854, 24 fps, 15 s, no audio. Job `4fada637-ad3d-4d3e-be6b-7d403b6e2db4`, 45 credits
- `ben-dance-lume-v1-480p-music.mp4`: same video with the reference's original audio (15 s, trimmed to the video)
- `qc/v1-sheet.jpg`: contact sheet

Notes on v1: hallway, lamp and floor kept, no text or watermark. Ben follows the dance (arms wide, spin, hands up). Lume holds the phone but is seen from behind the whole time, so his face never shows. Upscale to 1080p not done.

## Caption versions (19 Oct 2026)

Each caption ends with 🤣 (Apple Color Emoji, drawn at the left end of the last line). `build_versions.py` + `captions.json` (run with the watch-video `.venv` Python, it has Pillow). All 1080x1920, 30 fps, original audio, caption white bold SF Hebrew at the top (y 240, same look as `2026-10-14-reel-captions-1014`), no bottom text.
- `ben-dance-lume-caption-1.mp4`: "זה מה שקורה כשאני לא נמצאת בבית?", plain, 15 s
- `ben-dance-lume-caption-2-mirrored.mp4`: "זאת הסיבה שאני לא יכולה לעזוב את הקטנים לרגע", picture mirrored (caption not), 15 s
- `ben-dance-lume-caption-3-zoom-13s.mp4`: "מה קורה כשאני לא נמצאת בחדר", 1.08x zoom, whole clip sped up to 13 s (audio tempo-matched), 13 s
The 480p picture is scaled up, not upscaled with a model.
