# Social profile refresh (6 Nov 2026)

New profile picture and Facebook cover for LumeBook, plus bios. Made only from files already in `shared/brand/`, so no image generation and no spend.

| File | What |
|---|---|
| `final/lumebook-profile-1080.png` | Profile picture, 1080 x 1080. Upload the square; Instagram and Facebook cut the circle. Crop of `shared/brand/mascot_full_3d.png` (x 60 to 1060, y 0 to 1000), so the hat tip, ears and open book sit inside the circle. |
| `final/lumebook-facebook-cover-1640x624.png` | Facebook cover, 1640 x 624 (twice the 820 x 312 desktop size). Text and mascot sit inside the centre 1109 px, which is what phones show. Bottom left stays empty for the page's profile picture. Instagram has no cover photo. |
| `final/lumebook-profile-light-1080.png` | Light version of the profile picture (6 Nov: Yarin asked for "light version"). The cut-out mascot (`src/mascot_cut.png`) on a pastel cyan and lavender glow with gold, violet, cyan and pink sparkles. |
| `final/lumebook-facebook-cover-light-1640x624.png` | Light version of the cover: same layout and safe zones, pastel lavender, pink and cyan ground, wordmark in deep violet with a cyan offset, gold pill. |
| `final/preview-sheet.png`, `final/preview-sheet-light.png` | Cover at desktop size and phone crop, profile picture as a circle at 320, 170, 110 and 40 px. For checking only, do not upload. |
| `bio.md` | Instagram name and bios, Facebook intro and About, link tags. |
| `src/` | Rebuild: `cutout.py` (mascot cut from `mascot_closeup_dark_purple_headroom.png`), `cover.html`, `profile.html`, `render.sh` (headless Chrome). |

## Rebuild

```
cd media/projects/2026-11-06-social-profile-refresh
/usr/bin/python3 src/cutout.py ../../../shared/brand/mascot_closeup_dark_purple_headroom.png src/mascot_cut.png 30
src/render.sh
```

`/usr/bin/python3` is the one with Pillow and numpy. Fonts: Heebo Black and Bold from `shared/brand/fonts/`.

## Status

Not yet promoted to `shared/brand/`. Once Yarin approves, copy the two finals there and register them.
