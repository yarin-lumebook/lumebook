# Brief: read the on-screen hook from frame strips

Each JPG in `work/strips/` is one MeBook video (Instagram reel or Meta ad). It shows 6 frames from the opening: 0.2s, 0.8s, 1.5s, 2.3s, 3.2s and 4.5s (labels at the top left of each frame).

For every strip you are given, open the image ONCE and write one JSON object:

```
{"key": "<file name without .jpg>",
 "on_screen": "<the exact Hebrew (or other) overlay text that appears by 3.2s, lines joined with ' / '>",
 "on_screen_kind": "title | subtitles | both | none",
 "first_seen_s": 0.2,
 "printed_only": "<text that is printed on a product, book cover, logo or packaging, if any, else ''>",
 "scene": "<max 15 words: what is shown in the opening (who, what object)>",
 "confidence": "high | medium | low",
 "note": "<anything unclear, e.g. 'text partly hidden', 'second line unreadable'>"}
```

Rules
- `on_screen` is text an editor put over the video (titles, hook text, burned-in subtitles). It is NOT the brand logo, NOT the title printed on a book cover, NOT app interface text. Put those in `printed_only`.
- `title` = a hook line/title that stays on screen; `subtitles` = word-by-word or line-by-line captions of speech; `both` if both exist.
- Copy the Hebrew letter by letter, exactly as written, including spelling mistakes, repeated letters (e.g. סיפוררר), punctuation and emoji. Never correct, translate or paraphrase. If a word is unreadable write [?].
- Only text visible by 3.2s counts as the hook. If the first overlay appears only at 4.5s, still record it but set first_seen_s to 4.5.
- If there is no overlay text in any of the six frames, on_screen = "" and on_screen_kind = "none".
- Do not guess from context. Low confidence is fine; invented text is not.

Write all objects as a JSON array to the output file you were given, valid JSON (escape double quotes inside Hebrew text as \").
