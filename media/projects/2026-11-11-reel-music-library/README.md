# Reel music library

Yarin's YouTube playlist (https://www.youtube.com/playlist?list=PLMCcUbO--M9QW9cf-QtnKSeWOnY_x_Y5d), mp3 only, 99 tracks, downloaded 11 / 11 / 2026. Every track is measured (tempo, energy, key, where the singing is, the lyrics) and has a ready 30 second cut of its strongest part in its folder's `30s/`, levelled to -14 LUFS with a 2 s fade at the end. Full numbers: `library.json`.

## Using it for a reel

```bash
python3 media/projects/2026-11-11-reel-music-library/tools/library.py pick --length 16 --mood upbeat --talk
python3 media/projects/2026-11-11-reel-music-library/tools/library.py mix final/reel.mp4 <id> --out final/reel-music.mp4
```

- `pick` lists the best fits: never folder 08 or a cut with strong words; songs with strong words elsewhere come last and say so; cuts whose opening was confirmed come first; `--talk` puts the cuts with the least singing first (a talking take), `--mood` is upbeat, heartfelt, chill, dance, latin, throwback or hiphop.
- `mix` lays the 30 s cut under the video, ducked whenever someone talks, with a fade at the end. `--from S` uses the full song from second S instead.
- With the reel editor: set `"audio": "<cut path>"` in reel.json for a video without its own sound.
- These are commercial songs. Before posting from the business account, pick the same sound from Instagram's music library; a file here is for choosing and timing, not a licence.
- How it was measured: tempo, energy, key and sections with librosa (`tools/analyze.py`); the singing and the lyrics with whisper small.en (`tools/transcribe.sh`, local only, never committed). The best 30 s is the loud, repeated part that opens on a sung line, preferring the first chorus. Energy 1 to 5 is relative to this library. BPM is the beat tracker's reading and can come out double on slow songs (a ballad at 150). Lyrics are machine heard: a 'clean' song can still have a word whisper missed, and songs mostly not in English were not checked. To save time, most songs were transcribed only around their cut (about 15 s before to 45 s after its start); their check says 'around the cut' and covers only that part, so the rest of the song can still have strong words.
- Every usable cut's start was checked by transcribing its opening seconds again (`tools/check_cuts.py`): 'chorus line' and 'sung line' are confirmed; 'unconfirmed' means the two checks disagreed, so listen to the first seconds before using it. Folder 08 was not checked.

Columns: tempo (BPM), energy 1 to 5, singing in the 30 s cut, lyrics check, where the cut starts in the song, what the cut opens on.

## 01-upbeat-feelgood (11)

Bright, positive pop. Hooks, gift moments, sale-day reels, 'smile' endings.

| # | Track | BPM | Energy | Singing in cut | Lyrics | Cut from | Opens on |
|---|---|---|---|---|---|---|---|
| 01 | Zara Larsson - Lush Life (Lyrics) | 99 | 4 | 100% | clean | 1:46 | chorus line |
| 02 | Huntrix - Golden (Lyrics) KPop Demon Hunters | 123 | 4 | 100% | clean | 2:06 | chorus line |
| 07 | I Like It - Shoshana Ami (Official Lyric Video) | 143 | 3 | 80% | strong x1 | 1:46 | sung line |
| 15 | Taylor Swift - The Fate of Ophelia | 123 | 3 | 100% | clean | 0:46 | chorus line |
| 20 | “Golden” Official Lyric Video / KPop Demon Hunters / Sony Animation (same song as 2) | 123 | 2 | 100% | clean (around the cut) | 1:04 | sung line |
| 29 | ROSÉ & Bruno Mars - APT. (Official Music Video) | 152 | 4 | 39% | clean (around the cut) | 0:07 | sung line |
| 44 | Oliver Tree - Life Goes On (Lyrics) | 161 | 4 | 100% | clean | 0:35 | sung line |
| 45 | Meghan Trainor - Title (Lyrics) / this an invitation to kiss my ass go | 89 | 4 | 7% | strong x2 | 1:17 | sung line |
| 47 | Ed Sheeran - Bad Habits (Lyrics) | 123 | 5 | 100% | clean | 0:38 | sung line |
| 80 | Justin Wellington - Iko Iko (Lyrics) (Tiktok Song) / My besty and your | 143 | 5 | 100% | clean | 0:59 | sung line |
| 92 | Dirty Heads - Vacation (Lyrics) / I'm on vacation every single day | 152 | 4 | 100% | strong x3 | 0:14 | chorus line |

## 02-heartfelt-emotional (20)

Warm love songs and big ballads. Grandparent, birthday, 'his name on the cover' moments.

| # | Track | BPM | Energy | Singing in cut | Lyrics | Cut from | Opens on |
|---|---|---|---|---|---|---|---|
| 08 | Bruno Mars - Risk It All (love song (lyrics)) | 172 | 2 | 94% | clean (around the cut) | 1:05 | sung line |
| 10 | Lady Gaga, Bruno Mars - Die With A Smile (Lyrics) | 152 | 2 | 100% | clean (around the cut) | 0:42 | sung line |
| 18 | Alex Warren - Ordinary (Lyrics) | 112 | 3 | 95% | adult x1 (around the cut) | 1:18 | sung line |
| 25 | Alex Warren - Ordinary (Official Video) (same song as 18) | 112 | 3 | 95% | adult x1 (around the cut) | 1:18 | sung line |
| 28 | Billie Eilish - BIRDS OF A FEATHER (Official Music Video) | 103 | 4 | 100% | clean | 0:58 | chorus line |
| 30 | Jaymes Young - Infinity (Lyrics) | 123 | 2 | 65% | clean | 0:42 | chorus line |
| 32 | Gracie Abrams - That’s So True (Official Lyric Video) | 107 | 3 | 100% | strong x1 | 1:10 | sung line |
| 40 | Lady Gaga, Bruno Mars - Die With A Smile (Official Music Video) (same song as 10) | 152 | 2 | 100% | clean (around the cut) | 0:42 | sung line |
| 43 | The Kid LAROI, Justin Bieber - Stay (Lyrics) | 172 | 4 | 100% | strong x3 (around the cut) | 0:34 | sung line |
| 50 | Lauren Spencer Smith - Fingers Crossed (Lyrics) “so I want all the tea | 112 | 3 | 100% | clean (around the cut) | 0:34 | sung line |
| 51 | Witt Lowry - Into Your Arms (Lyrics) ft. Ava Max - [No Rap] | 112 | 1 | 100% | clean | 1:08 | unconfirmed |
| 55 | Take Me To Church - Hozier (Lyrics) 🎵 | 129 | 2 | 95% | clean (around the cut) | 2:10 | sung line |
| 62 | Tom Odell - Another Love (Lyrics) | 123 | 2 | 81% | strong x2 | 2:18 | sung line |
| 66 | Ellie Goulding - Still Falling For You (Lyrics) | 129 | 2 | 88% | clean | 2:09 | sung line |
| 67 | Bruno Mars - Talking To The Moon (Official Lyric Video) | 143 | 2 | 100% | clean (around the cut) | 0:44 | sung line |
| 73 | As The World Caves In - Matt Maltese (Cover by Sarah Cothran) | 123 | 2 | 100% | adult x1 | 0:47 | sung line |
| 83 | Mike Posner - Please Don't Go (Lyrics) / yeah you got me begging baby  | 117 | 4 | 87% | clean | 2:41 | sung line |
| 89 | Olivia Rodrigo - drivers license (Official Video) | 143 | 2 | 90% | strong x2 | 1:54 | chorus line |
| 90 | Duncan Laurence - Arcade (Lyrics) [Tiktok Version] | 129 | 1 | 100% | clean | 1:52 | unconfirmed |
| 94 | Chloe George - Ghost Town (Lyrics) (TikTok cover) and nothing hurts an | 123 | 2 | 100% | clean (around the cut) | 0:25 | chorus line |

## 03-chill-mellow (14)

Soft, slow, indie and lo-fi. Quiet talking-take reels, behind the scenes, bedtime and reading.

| # | Track | BPM | Energy | Singing in cut | Lyrics | Cut from | Opens on |
|---|---|---|---|---|---|---|---|
| 06 | The Neighbourhood - Sweater Weather (Lyrics) | 123 | 3 | 100% | clean (around the cut) | 0:31 | sung line |
| 09 | Gigi Perez - Sailor Song (Lyrics) | 95 | 1 | 100% | clean (around the cut) | 2:25 | sung line |
| 26 | sombr - back to friends (official video) | 92 | 3 | 91% | clean (around the cut) | 2:17 | sung line |
| 27 | Elley Duhé - Middle of the Night (Lyrics) | 92 | 3 | 99% | clean (around the cut) | 0:30 | chorus line |
| 48 | pinkpantheress - Just For Me (Lyrics) | 136 | 4 | 90% | clean (around the cut) | 0:37 | sung line |
| 49 | Sam Smith - Like I Can (Lyrics) | 99 | 3 | 100% | clean (around the cut) | 1:17 | chorus line |
| 54 | Realestk - WFM (Lyrics) ＂wait for me＂ (slow love song (lyrics)) | 161 | 2 | 97% | clean (around the cut) | 1:12 | sung line |
| 63 | Billie Eilish - Bellyache (Lyrics) | 136 | 3 | 70% | clean (around the cut) | 1:05 | chorus line |
| 71 | VANO 3000 - Running Away (Lyrics) [adult swim] ＂Running away is easy I | 92 | 3 | 100% | clean (around the cut) | 0:10 | sung line |
| 75 | freaks ~ surf curse ( tiktok version ) | 172 | 1 | 25% | clean (around the cut) | 0:48 | sung line |
| 81 | Lonely God - Marlboro Nights (Lyrics) | 117 | 2 | 63% | clean (around the cut) | 0:59 | sung line |
| 93 | Beach Bunny - Cloud 9 (Lyrics) Paravi Das Cover / i hate all men but w | 123 | 1 | 87% | clean (around the cut) | 0:57 | sung line |
| 96 | Hippie Sabotage - Devil Eyes (Golden) (Lyrics) | 152 | 3 | 100% | clean (around the cut) | 0:25 | sung line |
| 98 | Fousheé - Deep End (Lyrics) | 123 | 3 | 91% | strong x3 (around the cut) | 1:00 | chorus line |

## 04-dance-remix-trending (10)

TikTok versions, remixes and mashups. Fast cuts, transitions, countdowns.

| # | Track | BPM | Energy | Singing in cut | Lyrics | Cut from | Opens on |
|---|---|---|---|---|---|---|---|
| 11 | PinkPantheress - Stateside (Lyrics) ft. Zara Larsson | 123 | 4 | 96% | not heard | 0:49 | sung line |
| 17 | Tame Impala, JENNIE - Dracula (JENNIE Remix) (Lyrics) | 117 | 4 | 69% | clean (around the cut) | 0:12 | sung line |
| 35 | Squid Game & Do It To It (Zedd Edit) ('lean with it' is a dance line) | 123 | 5 | 100% | clean (around the cut) | 0:45 | sung line |
| 36 | Jnr Choi - TO THE MOON (Lyrics) Drill Remix TikTok | 117 | 4 | 92% | strong x5 | 0:57 | unconfirmed |
| 38 | Britney Spears, Ginuwine - Toxic X Pony (TikTok Mashup) [Lyrics] | 143 | 3 | 99% | clean (around the cut) | 0:41 | sung line |
| 42 | Elton John & Dua Lipa - Cold Heart (Lyrics) (PNAU Remix) | 117 | 4 | 100% | clean (around the cut) | 0:09 | sung line |
| 52 | Sub Urban & Bella Poarch - INFERNO (Lyrics) | 129 | 4 | 67% | clean (around the cut) | 0:39 | sung line |
| 79 | Pusher - Clear ft. Mothica (Shawn Wasabi Remix) Lyrics TikTok Remix /  | 92 | 3 | 99% | clean (around the cut) | 2:03 | sung line |
| 88 | Charli XCX - Unlock It (CTRL superlove mix) (Lyrics) ＂Lock it＂ [Tiktok | 136 | 4 | 64% | clean | 1:04 | sung line |
| 97 | Phao - 2 Phut Hon (KAIZ Remix) / TikTok Vietnamese Music 2020 | 129 | 4 | 0% | not English | 0:48 | sung line |

## 05-latin-afro-world (9)

Afro, Latin, Brazilian funk, amapiano. Fun, rhythmic montages.

| # | Track | BPM | Energy | Singing in cut | Lyrics | Cut from | Opens on |
|---|---|---|---|---|---|---|---|
| 04 | Papaoutai (Afro Soul) - Stromae | 136 | 2 | 0% | not English | 2:09 | not checked |
| 19 | DAME UN GRR | 117 | 4 | 3% | not English | 0:40 | sung line |
| 33 | Goya Menor, Nektunez – Ameno Amapiano Remix (you want to bamba, you wa | 112 | 4 | 50% | clean (around the cut) | 1:32 | sung line |
| 41 | CKay - Love Nwantiti (TikTok Remix) (Lyrics) ＂I am so obsessed I want  | 117 | 3 | ? | not heard | 1:14 | sung line |
| 53 | J Balvin, Skrillex - In Da Getto (Letra⧸Lyrics) | 129 | 5 | 100% | not English | 0:23 | not checked |
| 57 | Jc La Nevula - Buscate Otro Ft Atomic Otro Way (VIDEO OFICIAL) | 99 | 5 | 100% | not English | 2:20 | sung line |
| 58 | DJ TOPO, MC CYCLOPE, MC PR - PASSARINHO QUE SOM É ESSE | 129 | 5 | 64% | not English | 0:20 | sung line |
| 78 | Kali Uchis - telepatía (Lyrics) | 161 | 3 | 85% | clean (around the cut) | 0:32 | sung line |
| 99 | Abena x Chily - Réseaux / Official Music Video | 117 | 4 | ? | not English | 0:50 | sung line |

## 06-throwback-retro (6)

2000s hits and older. Nostalgia, grandmother and 'when we were kids' reels.

| # | Track | BPM | Energy | Singing in cut | Lyrics | Cut from | Opens on |
|---|---|---|---|---|---|---|---|
| 03 | RAYE - WHERE IS MY HUSBAND! (Lyrics) | 117 | 2 | 100% | strong x1 (around the cut) | 1:14 | sung line |
| 05 | Rock That Body - The Black Eyed Peas (Lyrics) | 123 | 3 | 99% | clean (around the cut) | 0:16 | sung line |
| 16 | Kelis - Milkshake (Lyrics) | 112 | 4 | 90% | clean (around the cut) | 0:41 | sung line |
| 21 | Connie Francis - Pretty Little Baby | 123 | 3 | 100% | clean (around the cut) | 0:41 | sung line |
| 23 | 4 Non Blondes - What's Up (Lyrics) (full song; 13 is a 55 s mashup of it) | 136 | 2 | 83% | clean (around the cut) | 1:10 | chorus line |
| 76 | Flo Rida - Low (feat. T-Pain) [Official Video] | 129 | 3 | 47% | clean (around the cut) | 0:45 | sung line |

## 07-hiphop-rnb (5)

Rap and R&B without strong words in the lyrics. Confident, trend-style reels.

| # | Track | BPM | Energy | Singing in cut | Lyrics | Cut from | Opens on |
|---|---|---|---|---|---|---|---|
| 12 | Kendrick Lamar - luther (Lyrics) ft. SZA | 136 | 4 | 93% | clean (around the cut) | 0:27 | sung line |
| 22 | Doechii - Anxiety (Lyrics) | 129 | 4 | 100% | clean (around the cut) | 1:36 | sung line |
| 64 | Doja Cat - Woman (Lyrics) | 107 | 5 | 46% | clean (around the cut) | 0:18 | sung line |
| 84 | Lil Tjay - Calling My Phone (Lyrics) ft. 6LACK | 103 | 3 | 85% | adult x1 (around the cut) | 0:29 | sung line |
| 87 | Masked Wolf - Astronaut In The Ocean (Official Music Video) | 99 | 4 | 99% | clean (around the cut) | 0:45 | sung line |

## 08-adult-explicit-avoid (22)

Strong words or adult themes in the lyrics. Not for a kids' book brand.

| # | Track | BPM | Energy | Singing in cut | Lyrics | Cut from | Opens on |
|---|---|---|---|---|---|---|---|
| 13 | 4 Non Blondes x Nicki Minaj - What's Up？ x Beez In The Trap (djauxlord (strong words in the cut) | 152 | 2 | 100% | strong x5 (around the cut) | 0:19 | not checked |
| 14 | Boom Boom Skeet Skeet | 117 | 5 | 73% | strong x15 (around the cut) | 2:20 | not checked |
| 24 | Kid Cudi - Maui Wowie (Lyrics) (about smoking weed) | 123 | 3 | 100% | strong x1 (around the cut) | 0:54 | not checked |
| 31 | Tony Michael -   Sin Again [Official Videolizer] (strong words and drugs) | 107 | 3 | 100% | strong x2 (around the cut) | 0:34 | not checked |
| 34 | Lil Nas X - Industry Baby (Lyrics) ft. Jack Harlow (strong word in the cut) | 152 | 4 | 100% | strong x1 (around the cut) | 2:05 | not checked |
| 37 | Yung Lean - Ginseng Strip 2002 (Lyrics) ＂bitches come and go brah＂ Tik | 117 | 3 | 97% | strong x5 (around the cut) | 0:00 | not checked |
| 39 | 16 Missed Calls - Brent Faiyaz (Lyrics) (strong words in the cut) | 86 | 4 | 100% | strong x7 (around the cut) | 0:15 | not checked |
| 56 | Drake - Way 2 Sexy (Lyrics) ft. Future, Young Thug | 136 | 5 | 100% | not heard | 0:14 | not checked |
| 59 | Soulja Boy (Big Draco) - Rick & Morty (strong words throughout) | 103 | 4 | 100% | strong x6 (around the cut) | 0:54 | not checked |
| 60 | FelixThe1st - Own Brand Freestyle (Lyrics) / i ain't never been with a | 129 | 4 | 100% | strong x8 (around the cut) | 0:45 | not checked |
| 61 | Doja Cat - Ain't Shit (Lyrics) | 123 | 5 | 100% | strong x10 (around the cut) | 0:31 | not checked |
| 65 | Doja Cat - Need to Know (Official Video) (strong word in the cut) | 129 | 4 | 99% | strong x1 (around the cut) | 0:23 | not checked |
| 68 | Cochise - Pocket Rocket (slowed⧸TikTok Version) Lyrics / come and get  | 152 | 5 | 100% | strong x2 (around the cut) | 0:06 | not checked |
| 69 | Princess Chelsea - The Cigarette Duet (about smoking) | 103 | 2 | 50% | adult x3 (around the cut) | 1:18 | not checked |
| 70 | Ashlee Keating - FREAKY | 152 | 5 | 33% | strong x1 (around the cut) | 0:25 | not checked |
| 72 | Destiny's Child - Bills, Bills, Bills (Lyrics) (strong word in the cut) | 129 | 4 | 100% | strong x1 (around the cut) | 0:33 | not checked |
| 77 | Busta Rhymes - Touch It (TikTok Remix) Lyrics / touch it clean busta r | 103 | 5 | 100% | strong x8 (around the cut) | 2:03 | not checked |
| 82 | Kevin Gates - Big Gangsta (Lyrics) / b i'm a big gangsta i turn her ou | 143 | 4 | 100% | strong x5 (around the cut) | 1:00 | not checked |
| 85 | Tai Verdes - A-O-K (Lyrics) (strong word in the cut) | 83 | 3 | 100% | strong x1 (around the cut) | 0:38 | not checked |
| 86 | Doja Cat - Kiss Me More (Lyrics) ft. SZA (strong words in the cut) | 112 | 5 | 100% | strong x5 (around the cut) | 0:40 | not checked |
| 91 | Justin Bieber - Peaches (Lyrics) ft. Daniel Caesar, Giveon (strong words and weed in the cut) | 89 | 2 | 71% | strong x8 (around the cut) | 2:28 | not checked |
| 95 | SoFaygo - Knock Knock (Lyrics) ＂I knew shorty was a thottie＂ | 123 | 4 | 99% | strong x5 (around the cut) | 0:15 | not checked |

## 09-check-first (2)

Not sure. Listen before using.

| # | Track | BPM | Energy | Singing in cut | Lyrics | Cut from | Opens on |
|---|---|---|---|---|---|---|---|
| 46 | Lady Gaga - The Dead Dance (Official Music Video) (no strong words heard, but the song is about death and haunting) | 123 | 3 | 100% | adult x1 (around the cut) | 1:44 | sung line |
| 74 | Brooksie - Dude, she's just not into you (Tiktok Song) (whisper heard no lyrics around the cut; was in 08 on its title only) | 99 | 3 | 62% | not heard | 0:09 | sung line |
