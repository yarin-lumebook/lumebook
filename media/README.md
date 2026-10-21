# media: every LumeBook creative file in one place

Set up 14 Oct 2026. Images, video and audio that LumeBook makes or collects live here, one folder per job, so there is one copy of each file and an old job can go to the cloud as a single folder.

## Layout

| Folder | What goes there |
|---|---|
| `projects/YYYY-MM-DD-slug/` | One creative job: a reel, a podcast episode, a character pack, a story or highlight set, a trend recreation, a Canva carousel. Everything the job needs sits inside it (inputs, prompts, scripts, raw generations, `final/`), so the folder can move or go to the cloud whole. The date is the day the job started. |
| `inbox/` | New files that are not sorted yet (downloads, WhatsApp exports). File them into a project within the week, or move them to `_to-delete/`. |

Not here, on purpose:

- `shared/brand/`: the canonical logos, mascot, fonts and backgrounds. Sites and the carousel pipeline copy from it (`lumebook.py sync`), so it stays put. Brand explorations that did not become canonical go in a `projects/` folder.
- `carousel/carousel-pipeline/drafts/` and `approved/`: Hook Studio writes its nightly packs and paid production runs there (22:00 task, `carousel_lib.py`). Final carousels stay in `approved/DATE-OPTION/final/`.
- `research/*/videos`, `slides`, `img`: other brands' content downloaded for the research pages; the page builds read it from there.
- `sites/*/img`: deploy copies of brand files, kept equal by `sync`.

## Rules

- A new creative job gets `projects/<start date>-<short-slug>/`. Write renders, generations and exports into it, never into a new top-level folder (`output/` and `video/` were folded in here on 14 Oct 2026).
- One copy per file. A file another job needs is referenced by its path here, not copied, unless a tool needs it beside its own inputs (then say so in that job's manifest or README).
- A file nobody needs any more goes to `../_to-delete/` under its original path, with a line in `_to-delete/README.md`. Nothing is deleted from the project directly; Yarin empties that folder.
- Pictures, video and audio are not in git (see `.gitignore`); scripts, prompts, manifests and READMEs are.

## Moving an old project to the cloud

1. Upload the whole `projects/<folder>` to Google Drive.
2. Open it in Drive and check the finals play or open.
3. Move the local folder to `_to-delete/media/projects/<folder>` and add its Drive link to the index below (status `cloud`).

## Index

Status: `active` = still being worked on, `done` = finished and kept locally, `superseded` = a later approach replaced it (a cloud candidate), `cloud` = only in Drive now.

| Project | What it is | Size | Status |
|---|---|---|---|
| `2026-10-06-canva-carousels` | Canva carousel "הוא לא חזר אחורה, הוא מתכונן לקפיצה הבאה" (regression-leap, two exports) and the Claude PDF of the "אמא, אבא, אני לא עושה לכם דווקא" carousel plus handout. From Downloads and the old `carousel/references/`. | 26 MB | done |
| `2026-10-06-fal-carousel-trial` | fal.ai carousel trial, frozen reference. The pipeline's classic look copies `source/flare_carousel.py`. Was `carousel/fal-carousel-trial/`. | 167 MB | superseded |
| `2026-10-07-brand-explorations` | Mascot with the LB letters (7 Oct) and a mascot night-sky Facebook cover (9 Oct) that did not become canonical brand files. From Downloads. | 4.5 MB | done |
| `2026-10-10-genjutsu-hotel-lobby` | Higgsfield Genjutsu inputs: reference clip, mascot, toddler, prompt. From Downloads. | 7.5 MB | done |
| `2026-10-10-hook-studio-bold-look-trials` | Hook Studio bold-look trial renders (games, books, first-grade covers). Was `carousel/references/hook-studio-bold-look/`. | 9.4 MB | superseded |
| `2026-10-11-fan-transition-reel` | Fan-transition outfit reel (kid, kid+mom, family, book last). Was `video/fan-transition/`. | 23 MB | done |
| `2026-10-11-lume-character-pack` | Lume mascot reference pack, 13 angles in `final/`. Was `output/lume/reference-pack-v1/`. | 197 MB | done |
| `2026-10-11-toddler-character-pack` | Toddler "Ben" reference pack, 13 angles in `final/`. Was `output/reel-character/reference-pack-v1/`. | 198 MB | done |
| `2026-10-12-boys-interviews` | Boys interview audio, per boy and combined. Was `output/boys-interviews/`. | 9.6 MB | done |
| `2026-10-12-podcast-lume-pilot` | Podcast talking-shot pilot. Was `output/podcast/lume-pilot-v1/`. | 91 MB | done |
| `2026-10-12-podcast-strawberries` | Strawberry-truck podcast episode and reels (B, C, v1, v2). Was `output/podcast/strawberries-episode-v1/`. | 550 MB | done |
| `2026-10-12-podcast-studio-set` | Purple podcast studio angles. Was `output/imagegen/podcast-studio/`. | 23 MB | done |
| `2026-10-13-reels-superhero-book` | Superhero book reels 1 to 4, cut from the WhatsApp reading session in `source/` (from Downloads). Was `output/reels-2026-10-13-superhero-book/`. | 123 MB | active |
| `2026-10-13-text-pull-ben-reel` | Text-pull reel with Ben. Was `video/text-pull-ben/`. | 22 MB | done |
| `2026-10-14-stories-qa` | Q&A story series. Was `output/stories/2026-10-14-qa/`. | 23 MB | active |
| `2026-10-14-stories-qa-heebo` | Q&A story series redone in Heebo. Was `output/stories/2026-10-14-qa-heebo/`. | 40 MB | active |
| `2026-10-14-stories-kindergarten-offer-end` | Kindergarten offer-ending story. Was `output/stories/2026-10-14-kindergarten-offer-end/`. | 1.6 MB | active |
| `2026-10-14-highlights-qa` | Q&A highlight covers. Was `output/highlights/2026-10-14-qa/`. | 3.9 MB | active |
| `2026-10-14-highlights-book-and-text` | Book and text highlight covers. Was `output/highlights/2026-10-14-book-and-text/`. | 2.6 MB | active |
| `2026-10-15-israeli-product-reels` | 47 Israeli creator Reels downloaded for the filming research in `research/israeli-product-reels/`: videos, frames, contact sheets, transcripts, annotated strips. Other creators' work, internal study only. | 712 MB | done |
| `2026-10-15-genjutsu-lume-rapper` | Genjutsu motion transfer: Lume as the rapper in the red-venue crowd trend. Reference clip (from Downloads), Lume front still, prompt, Higgsfield output `lume_rapper_v1.mp4`. 16 Oct: fal Kling 2.6 Standard cheaper-model test (`lume_rapper_kling26std_test_4s.mp4`, face drift, no venue). | 34 MB | done |
| `2026-10-16-creator-reels` | Gallery page `creator-reels.html` (built by `build.py`) of every creator video about the book in the Drive folder תוכן לקוחות ויוצרים (22 files, 7 creators) plus the 5 re-cuts in Drive 9x16. Videos stay in Drive and play through Drive previews. | 20 KB | active |
| `2026-10-16-genjutsu-truck-box` | Genjutsu trend: truck box flies onto a footbridge, the LumeBook birthday book comes out instead of a hoodie. v1 with the titled cover (`book-box-1080p.mp4`, AI caption baked in). v2 final: clean cover, no on-screen text, Hebrew voice (`book-box-v2-1080p-hebrew.mp4`). 480p Genjutsu then Bytedance pro upscale; Hebrew lines by ElevenLabs v4 on fal. | 51 MB | done |
| `2026-10-16-dj-ben-reel` | Genjutsu trend: Ben as the DJ and Lume dancing, from the @lucasthepug_ pugs reel. Reframed to 9:16 in two halves (aligned), then Genjutsu 480p (`dj-ben-lume-v1-480p.mp4`). Upscale pending. | 66 MB | active |
| `2026-10-19-genjutsu-ben-dance-lume` | Genjutsu trend from a Downloads reel (a cat dances in a hallway while another cat films it): Ben dances, Lume films with the phone. 9:16 reference needed no reframe. Genjutsu 480p (`ben-dance-lume-v1-480p.mp4`, job 4fada637, 45 credits). Upscale pending. | 40 MB | active |
| `2026-10-20-bedtime-story-reel` | Reel in the style of a MeBook bedtime-story reel (book-page layout, narrator, real ending) built from Sapir (sapir_ivan_mugatz)'s clips of Ariel's book. `script.md` has the script and cost estimate; free draft `draft/bedtime-story-draft-v1.mp4` (macOS scratch voice). Waiting for Yarin's approval and the 4 raw clips over 10 MB. | 38 MB | active |
| `2026-10-21-genjutsu-ben-truck-jump` | Genjutsu trend from a Downloads clip (a G-wagon jumps over a man in a desert chair): Ben in the chair, a giant toy truck jumps over him, last 8 s only. Genjutsu 480p (`ben-truck-jump-v1-480p.mp4`, job 5f93046a, 24 credits); the toy truck kept a Mercedes star on the grille. Five caption versions for trial reels (`captioned/ben-truck-jump-caption-1..5.mp4`, random flip and slight zoom each). Upscale not done. | 98 MB | active |
