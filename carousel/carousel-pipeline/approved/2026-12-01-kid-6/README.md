# Production run (pictures from ChatGPT)

Pictures are made in ChatGPT in Yarin's Chrome by Claude, free (production.json picture_backend "chatgpt", 30 Oct 2026). fal.ai is never called. Each picture lands in `generated-assets/<job>.png` (cropped to 4:5, 1024 x 1280; the download is kept in `generated-assets/chatgpt-originals/`), the resume point is `state.json`.

## 1 · The cover

```bash
python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/chatgpt_pictures.py next            # the prompt, the file name to download as
python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/chatgpt_pictures.py ingest /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-12-01-kid-6 slide-01
```

Carousel Machine then shows the picture for approval (or another take with a note, which puts it back in `next`).

## 2 · The other slides (after the cover is approved)

`next` then lists `slide-02` to `slide-09`, each with the approved cover as the reference picture. One new ChatGPT chat: attach `generated-assets/slide-01.png`, send the prompts one by one, ingest each download. When the last one is in, Carousel Machine builds the slides and the ZIP by itself.

## Final composition

Carousel Machine runs it by itself after the approval. By hand: `python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/compose_slides.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-12-01-kid-6`. Status: `python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/chatgpt_pictures.py status`
