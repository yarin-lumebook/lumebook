# Instagram carousel examples for LumeBook: market scan

Research date: 6 Oct 2026. Researcher: Claude (subagent). Scope: real Instagram carousels from kids/parenting brands, children's books, personalised gifts, educational DTC brands, child-development experts, and Israeli accounts, judged for what LumeBook (@lumebookai) can use in a conversion-focused carousel playbook.

Files:
- Slides and contact sheets: `research/slides/<code>/NN.jpg` and `research/slides/<code>_sheet.jpg` (43 carousels, 44 sheets).
- Per-post metadata from the logged-out embed (owner, date, likes, comments, slide count, caption): `research/meta.json` (52 posts).
- Fetch script: `research/fetch.py` (copy of the project script, extended to save metadata; writes only to the scratchpad).

---

## 0. How the numbers were collected (read before quoting any number)

- **Profile windows.** For each account I opened the profile in the logged-in browser pane (read-only, nothing liked, followed or commented) and captured the JSON of the ~12 posts the grid loads. Pagination did not trigger in the hidden pane, so **every account median below is over 12 posts** (pinned posts included, because the grid includes them). That is small. Treat multiples as rough.
- **Likes.** I use the logged-in `like_count` because the medians come from the same source. The logged-out embed sometimes shows lower numbers for the same post (Merav Levy DRKqmgSDYXo: 961 logged-in vs 675 embed; Etti Haft DdYpED4DTdp: 97/245 vs 66/166). Older posts outside the 12-post window use embed numbers and are marked "(embed)".
- **Shares and saves are not public.** The only share-like field that exists is `media_repost_count` (Instagram's Repost feature). It is filled for most accounts and null for some (Wonderbly's reels, MeBook, LumeBook). It counts public reposts only, not DM sends or saves. I report it as "reposts" where present.
- **Comments.** Counts include replies. I read samples by hand from `/api/v1/media/<id>/comments/` (first page = 15 top-level comments; 54 to 60 for two posts where I paginated). I did not invent or tidy comments; Hebrew ones are translated.
- **Conversion.** No post here has public sales data. For every example: **cannot know if this carousel sold.** The closest public signals are buying-intent comments, keyword comments that trigger a DM link, and discount/creator codes. I count those where I read them.
- **Multiple of median** = post likes / that account's 12-post median likes.

Coverage: 33 accounts screened, about 108 carousels seen at metadata level, 43 carousels downloaded slide by slide, 15 analysed in depth (one entry pairs two Israeli competitors). Accounts I could not load: @kidseatincolor (the route forced a hard reload each time), @wonderkins.co (no posts returned), @starofthebook and @dinkleboo (inactive since 2019 and 2014).

---

## 1. Accounts screened (12-post windows, logged-in counts)

| Account | Category | Carousels in window | Median likes, all | Carousel median | Non-carousel median | Note |
|---|---|---|---|---|---|---|
| wonderbly | Personalised books (UK) | 6 | 86.5 | 154 | 65.5 | Prior session's larger sample: ~108 carousel vs ~103 non-carousel. Recent window is carried by "handcrafted illustration" carousels. |
| hoorayheroes | Personalised books (US) | 4 | 37 | 30.5 | 37 | Mostly dog-parent books; last post July 2026. Two collab posts show 3 likes with 5 to 13 comments (likes hidden or ad delivery: inference). |
| libriogram (Librio, DE) | Personalised books | 3 | 24.5 | 26 | 23 | Giveaway collabs get 300+ comments; own carousels 16 to 26 likes. |
| tinybook.co.il | Personalised books (IL) | 2 | 9.5 | 7.5 | 9.5 | Carousels posted with no caption. |
| mebook.ai | Personalised books (IL) | 1 | 5 (incl. collabs) | 2 | 6 | Own posts get 0 to 6 likes; creator collab reels 20 to 794. First MeBook carousel seen (19 Sep 2026). |
| lumebookai | Personalised books (IL) | 6 of 35 | 0 | 0.5 | 0 | See section 3. |
| biglittlefeelings | Parenting experts | 5 | 7,487.5 | 34,723 | 1,066 | Top carousels are news/advocacy (e.g., Cornell case), not product. |
| drbeckyatgoodinside | Parenting expert (sells app/membership) | 7 | 5,158 | 5,474 | 4,842 | Text-on-photo scripts. |
| solidstarts | Feeding expert, sells app | 5 | 1,161.5 | 921 | 2,000 | Pinned "Comment APP" carousel. |
| biglifejournal | Educational DTC (journals, printables) | 6 | 123.5 | 123.5 | 246.5 | 6 of 12 posts show exactly 3 likes with 25 to 288 comments: likely ads or hidden likes (inference). Median of the 6 normal posts: 877. |
| lovevery | Educational DTC (play kits) | 3 | 1,815 | 2,412 | 1,033 | |
| yotoplay | Audio player DTC | 2 | 111 | 126 | 110.5 | |
| slumberkins | Emotional-learning books + plush | 7 | 57.5 | 55 | 1,007 | Non-carousel median inflated by 3 pinned 2022-2024 posts; recent non-pinned median 55. |
| takingcarababies | Sleep expert, sells courses/swaddle | 3 | 2,172 | 3,243 | 1,101 | |
| busytoddler | Play expert, sells curriculum + affiliate | 7 | 4,902 | 5,200 | 2,159 | Pinned "Comment GUIDE" gift guide. |
| usborne_books | Children's publisher | 3 | 69 | 77 | 64 | |
| kiwico_inc | Educational DTC | 0 | 62 | n/a | 62 | Reels only. |
| sifriyat.pijama | Israeli children's book programme | 1 | 20 | 11 | 21 | |
| shilav_kids | Israeli kids brand | 3 | 49.5 | 44 | 55 | Fashion carousels. |
| materna | Israeli baby brand | 0 | 77.5 | n/a | 77.5 | |
| michaloppenhaim | Hebrew parenting guide | 0 | 600 | n/a | 600 | Reels only. |
| merav.levy | Hebrew parenting guide | 5 | 105 | 233 | 63 | Carousels beat her other posts. |
| iris_maayan | Hebrew parenting guide | 4 | 30.5 | 29 | 40.5 | |
| esther_malka_psychologist | Hebrew child psychologist | 3 | 39 | 14 | 49 | |
| tal_kids_psychology | Hebrew educational psychologist | 7 | 11 | 11 | 11 | Inactive since early 2024. |
| koral_shaul_slp | Hebrew speech therapist | 1 | 7,400 | 1,495 | 9,648 | Reels-led; one carousel at 0.2x. |
| noadotan.ot | Hebrew occupational therapist | 4 | 31.5 | 46 | 31.5 | |
| etti_haft | Hebrew gan teacher, sells kits | 4 | 25.5 | 84 | 21.5 | Comment-for-link culture. |
| saray_halevi | Hebrew gan teacher | 4 | 50.5 | 46 | 67 | |
| razshapira_nurse | Hebrew paediatric ER nurse | 2 | 1,737 | 4,100.5 | 1,691 | Carousels are personal grief posts; excluded. |
| starofthebook, dinkleboo | Personalised books | 0 | n/a | n/a | n/a | Dormant. |

Pattern in this table: carousels beat the account's other formats at Wonderbly, Big Little Feelings, Lovevery, Taking Cara Babies, Busy Toddler, Merav Levy, Noa Dotan and Etti Haft, and lose at Solid Starts, Esther Malka, Koral Shaul and TinyBook. Format alone does not decide it (this matches the earlier session's Wonderbly finding).

---

## 2. In-depth analyses (15 entries)

Each entry: handle, URL, date, likes/comments, multiple of account median, reposts, slide count, then the breakdown. "Inferred" marks anything I did not directly see.

### 2.1 Wonderbly: World Book Day costume ideas (customer photos)
- **URL** https://www.instagram.com/p/DVf6q-ojdHQ/ · **Date** 5 Mar 2026 · **Likes/comments** 165 / 114 (embed) · **Multiple** 1.9x the current 12-post median (about 1.6x the prior session's larger-sample median) · **Slides** 7
- **First slide:** illustrated kids in superhero masks on a sky-blue background with a question, "Need costume ideas for World Book Day / Read Across America?"
- **Promise:** a costume answer for a dated school event, taken from the child's own book.
- **Structure:** 1 question hook; slides 2 to 7 each show a real child dressed as the character of their personalised book, holding the book (name visible on the cover, e.g., "Princess Lucy the Great", "It's Super-Joseph!"), framed on a pastel card with the book title underneath.
- **Pace of reveal:** product on slide 2 of 7, then on every slide.
- **Text density:** about 13 words on slide 1, 3 to 4 words (the book title) on each other slide.
- **Persuasion:** deadline utility (school event), social proof (real families), identity (the child is the hero), playful title wordplay.
- **Save/share mechanism:** saved as a costume list before the event; sent to the other parent or the class group (inferred from the format; save/DM counts are not public).
- **How the product enters:** as the prop the costume is built around.
- **CTA:** none on the slides; the caption just says they have you covered, no link instruction.
- **Comments (first 15 read):** all praise ("every kid should be getting one of these books"); 0 price or link questions.
- **LumeBook can adopt:** an occasion carousel tied to a dress-up date in the Israeli calendar, mainly Purim, also the first day of gan/grade 1. "Purim costume ideas from inside your child's book": the illustrated child in costume on each slide.
- **Does not fit:** real children's faces plus full first names on covers, published by the brand. LumeBook would need written parental consent per child, or should show only the illustrated version.

### 2.2 Wonderbly: First Mother's Day (the illustrations are the post)
- **URL** https://www.instagram.com/p/DVno-NEFRqJ/ · **Date** 8 Mar 2026 · **Likes/comments** 260 / 131 (embed, re-verified today) · **Multiple** 3.0x · **Slides** 2
- **First slide:** a full-bleed book illustration of a mother, father and baby nose to nose on a bed; no text. Caption opens with her first Mother's Day deserving something special.
- **Promise:** a first-milestone gift that looks like the mother.
- **Structure:** two illustration spreads from the book (family moment; mother kissing baby among peonies).
- **Pace of reveal:** product on slide 1 of 2 (the art is the product).
- **Text density:** 0 words on slides.
- **Persuasion:** tenderness, "first time" milestone, likeness (caption says characters are made to look like Mama).
- **Save/share mechanism:** hint-dropping to a partner. One commenter wrote that she was sending it to her husband.
- **How the product enters:** the illustrations themselves.
- **CTA:** none on slides or in the caption text I read.
- **Comments (54 top-level read):** about 5 show intent (wish list, "would love to have it", one Italian comment planning it as a gift, "I'll check this out", sending to husband); 0 asked for price or link; the rest are generic praise. Several of the same handles comment on other Wonderbly posts too (brookashley94, gabibhessler, forever_normandy, danielj.power): possibly a creator or ambassador community (inference).
- **LumeBook can adopt:** "first" milestone posts with two strong illustrated spreads and no on-slide text (first birthday, becoming a big sibling, a grandparent's first grandchild). Caption written to the gift-giver; CTA "send this to the person who should get it".
- **Does not fit:** Wonderbly's art is hand-illustrated. Full-screen, text-free slides expose illustration quality, so LumeBook should only do this with its best renders. Never imply hand drawing.

### 2.3 Wonderbly: Father's Day, three creator families
- **URL** https://www.instagram.com/p/DZj3-1diudi/ · **Date** 14 Jun 2026 · **Likes/comments** 161 / 111 (embed) · **Multiple** 1.9x · **Slides** 3
- **First slide:** a dad on a sofa with three children reading the open "Happy Father's Day, Daddy!" book.
- **Promise:** "Father's Day sorted" (caption).
- **Structure:** three slides, three different creator families with the same book, each tagged in the caption.
- **Pace of reveal:** product on slide 1 of 3, on every slide.
- **Text density:** 0 words on slides apart from the cover.
- **Persuasion:** social proof across varied families, gift problem solved.
- **Save/share mechanism:** tag a partner; creators re-share (inferred).
- **How the product enters:** being read together.
- **CTA:** none explicit.
- **Comments (first 15):** 3 of 15 show ownership or intent (already own it, excited to get theirs, hoping to receive one), 1 creator thank-you.
- **LumeBook can adopt:** "three families, one book" built from the 12-book creator barter batch: each slide a different family reading the same milestone title, every creator tagged, each with their personal promo code in their own repost.
- **Does not fit:** barter creators need a clear paid-partnership/barter disclosure. Creators' children appear with the creator's consent, not LumeBook's.

### 2.4 Wonderbly: "Reasons NOT to buy" (reverse psychology, counter-example)
- **URL** https://www.instagram.com/p/DdgN7EHiiR8/ · **Date** 20 Sep 2026 · **Likes/comments** 65 / 27 · **Multiple** 0.75x · **Reposts** 4 · **Slides** 5
- **First slide:** lilac text-only slide, roughly "Reasons you should absolutely NOT buy your kids Wonderbly books."
- **Promise:** a joke list that is really a benefits list.
- **Structure:** slides 2 to 5 each give one benefit (early literacy, language, social skills, rereading) with a punchline and a photo of a parent reading with a child.
- **Pace of reveal:** product on slide 2 of 5.
- **Text density:** about 25 to 30 words per slide.
- **Persuasion:** humour/reverse psychology; developmental benefit claims.
- **Save/share mechanism:** weak; nothing to keep.
- **CTA:** none.
- **LumeBook can adopt:** little. The rereading point (children want their own story read again) is the only usable idea.
- **Does not fit:** outcome claims such as raising a "smarty pants" or boosting language development, with no source. The same "regret/don't buy" frame worked for Etti Haft (2.5), so the frame is not what decides the result (inference from n=2).

### 2.5 Solid Starts: "A haunted house, but it's just..." (seasonal meme template)
- **URL** https://www.instagram.com/p/DeFHklroK3E/ · **Date** 4 Oct 2026 · **Likes/comments** 7,586 / 72 · **Multiple** 6.5x · **Reposts** 231 (3.0% of likes) · **Slides** 10
- **First slide:** baby sitting with a pumpkin, horror-font headline: a haunted house, but it's just baby-led weaning.
- **Promise:** laugh at the scary parts of starting solids.
- **Structure:** 1 hook; 2 to 9 the same template line over one relatable moment each (yogurt everywhere, gagging, advice from relatives, the floor after meals, the throwing phase, refusing yesterday's food); 10 reframe that starting solids doesn't have to be scary, app screenshots, link in bio.
- **Pace of reveal:** product on slide 10 of 10.
- **Text density:** about 10 words per slide.
- **Persuasion:** seasonal meme, recognition ("I feel seen" in comments), fear normalisation, then the solution.
- **Save/share mechanism:** sending to a partner or a friend at the same stage; commenters wrote their own "haunted house" lines, so the template invites participation.
- **How the product enters:** only as the answer on the last slide.
- **CTA:** last slide: app plus link in bio. Caption: share your fears in the comments, experts reply, free trial via bio link.
- **Comments (first 15):** jokes extending the template and one practical question; 0 explicit buying intent.
- **LumeBook can adopt:** the repeated-line meme for milestone fears, ending in a gentle reframe and the free preview. Hebrew examples: "a nightmare, but it's just the first night without a dummy", or the first week of gan. Halloween is marginal in Israel, so tie it to a local season or a Hebrew phrase people already use.
- **Does not fit:** jokes at the child's expense, and real babies' faces unless you have consent. Keep the joke on the parent's experience, not the child's distress.

### 2.6 Solid Starts: app tour with "Comment APP" (pinned)
- **URL** https://www.instagram.com/p/DPzA3H7jKI9/ · **Date** 14 Oct 2025, pinned · **Likes/comments** 837 / 1,296 · **Multiple** 0.72x on likes, but 1.55 comments per like · **Reposts** 30 · **Slides** 8
- **First slide:** "Meet the Solid Starts App" with a phone mock-up and a hand-drawn arrow.
- **Promise:** see exactly what the app does.
- **Structure:** one feature per slide (search foods, introduce allergens, plan your week, track progress, recipes, guides and courses); last slide: comment APP and they send a download link.
- **Pace of reveal:** product on slide 1 of 8.
- **Text density:** about 15 to 20 words per slide.
- **Persuasion:** demonstration, authority (caption cites millions of families), low-friction keyword CTA.
- **Save/share mechanism:** the keyword comment is the action; pinning keeps it live.
- **CTA:** "Comment APP" (slide 8 and caption).
- **Comments (first 15):** all "App". This post has the lowest likes in the window and by far the most actions.
- **LumeBook can adopt:** a pinned "how it works" carousel: photo → name and age → choose the milestone → free preview → order. Last slide: comment one Hebrew keyword and get the free-preview link by DM. This is the closest public analogue to LumeBook's funnel.
- **Does not fit:** user-count claims LumeBook cannot back. Show the real preview screens, not mock-ups that overpromise.

### 2.7 Big Life Journal: "Dear Mom and Dad, I love you but..." (child's voice + free worksheet)
- **URL** https://www.instagram.com/p/DeHOmAFExxS/ · **Date** 5 Oct 2026 · **Likes/comments** 1,615 / 578 · **Multiple** 13x the raw median (123.5), 1.8x the median of the account's normal-looking posts (877) · **Reposts** 55 · **Slides** 9
- **First slide:** a girl with a school bag in a sunny doorway, with a white text card written in her voice: "Dear Mom and Dad, I love you but..." She falls apart after school, not because of a bad day.
- **Promise:** understand after-school meltdowns from the child's side.
- **Structure:** 1 child-voice hook; 2 what school demands; 3 to 6 four numbered requests (let me settle, offer a snack, let me move, fewer questions); 7 what it means; 8 summary; 9 "Comment SDC to download" with the worksheet shown.
- **Pace of reveal:** free resource on slide 9 of 9; the paid membership appears only in the caption.
- **Text density:** about 30 to 40 words per slide, short lines, blue key phrase per card.
- **Persuasion:** perspective-taking (the child speaks), numbered list, reciprocity (free printable), scarcity (caption: free for 14 days), keyword CTA.
- **Save/share mechanism:** keyword comment, plus save for "after school today".
- **CTA:** "Comment SDC to download" (slide) and the same in the caption, then "comment ME" for the membership.
- **Comments (first 15):** all "SDC", each with one reply (looks like an automated DM trigger: inference).
- **LumeBook can adopt:** the strongest template for LumeBook. Write the milestone in the child's voice (for example, a child about to become a big sibling, or starting gan) and end on a free asset. LumeBook's natural free asset is the **free preview of a book starring the child**: "comment ספר and we'll DM you the link to a free preview".
- **Does not fit:** artificial scarcity, unless the deadline is real. The model child photo works for them; LumeBook should use an illustrated child or a consenting model.

### 2.8 Busy Toddler: gift guides by age, "Comment GUIDE" (pinned)
- **URL** https://www.instagram.com/p/DQIUIIpgbEv/ · **Date** 22 Oct 2025, pinned · **Likes/comments** 5,200 / 10,709 · **Multiple** 1.06x on likes, 2.06 comments per like · **Reposts** 107 · **Slides** 11
- **First slide:** product collage with "Ultimate Toy List" in big blue and black type.
- **Promise:** one place to find the right gift for any child's age.
- **Structure:** each slide is a guide cover: by age (1 year, toddlers, 3 to 5, 5 to 8, 9 to 12) and by type (non-toy gifts, art supplies, games, books, puzzles).
- **Pace of reveal:** the guide (her affiliate product) is on slide 1 of 11.
- **Text density:** 6 to 8 words per slide.
- **Persuasion:** authority (a year of testing, in the caption), decision relief, segmentation ("find your kid's age"), keyword CTA.
- **Save/share mechanism:** keyword comment; caption thanks people for sharing the lists with family.
- **CTA:** "Comment GUIDE for my updated toy lists" or the profile link.
- **Comments (first 15):** all "Guide".
- **LumeBook can adopt:** a Hanukkah gift-guide carousel (early December 2026), by age and by milestone, made **with an Israeli curator or creator** so LumeBook is one item on a trusted list rather than the whole list. Grandparents are a natural audience.
- **Does not fit:** a brand-made guide that only lists LumeBook books reads as a catalogue (see TinyBook, 2.15).

### 2.9 Dr Becky (Good Inside): "True story from my house this morning"
- **URL** https://www.instagram.com/p/DeIDQsODAis/ · **Date** 5 Oct 2026 · **Likes/comments** 5,474 / 45 · **Multiple** 1.06x · **Reposts** 49 · **Slides** 6
- **First slide:** a photo of a child's messy bedroom (no child visible) with highlighted text boxes: a true story from this morning, the kid screaming they don't want to go to school.
- **Promise:** what to do on a school-refusal morning.
- **Structure:** 1 story hook; 2 what I wanted to say vs what I did (a short "I know that feeling" line, then silence); 3 what happened next; 4 honest caveat that it doesn't always work; 5 the principle (don't add energy to resistance; common phrases that backfire); 6 reassurance and "Save this for your next hard morning."
- **Pace of reveal:** no product; a small logo watermark only.
- **Text density:** 45 to 60 words per slide.
- **Persuasion:** personal story, script contrast (instead of X, say Y), vulnerability, explicit save cue.
- **Save/share mechanism:** "save this" on the last slide.
- **CTA:** save. Caption: try it and tell her how it went.
- **LumeBook can adopt:** the format for gan-separation or bedtime-fear moments, plus the **privacy pattern**: show the setting, never the child. LumeBook would add one final slide where the book is offered as a next step.
- **Does not fit:** clinician authority. LumeBook should source its scripts (it already cites HealthyChildren.org in a first comment) and not present them as therapy.

### 2.10 Dr Becky: the pilot analogy (12.5x)
- **URL** https://www.instagram.com/p/Dcq2baejOXf/ · **Date** 30 Aug 2026 · **Likes/comments** 64,395 / 333 · **Multiple** 12.5x · **Reposts** 1,501 (2.3% of likes) · **Slides** 6
- **First slide:** a plane wing over a city with an unfinished scenario: you're on a flight and the pilot makes an announcement.
- **Promise:** a new way to see your child's protest when you hold a limit.
- **Structure:** 1 scenario; 2 the cabin protests the emergency landing; 3 the pilot gives in and passengers get scared (the punchline: losing control is the scary part); 4 "you are the pilot of your family's plane"; 5 children don't want to fly the plane; 6 expect protest, and the brand appears as "co-pilot".
- **Pace of reveal:** brand on slide 6 of 6, one soft line.
- **Text density:** 40 to 50 words per slide.
- **Persuasion:** analogy plus curiosity gap, reframe, identity ("sturdy"), brand as helper.
- **Save/share mechanism:** reposts (1,501) show it travels as an idea.
- **CTA:** none hard.
- **LumeBook can adopt:** an analogy carousel for the new-sibling milestone told from the child's side (for example, an adult imagining a surprise new colleague taking half their desk), ending with "a story lets them rehearse the change" and the book.
- **Does not fit:** the reach comes from Dr Becky's authority and audience. The same post from a brand with no audience will not get that reach.

### 2.11 Lovevery: "Baby's first Halloween? Just wait... (positive edition)"
- **URL** https://www.instagram.com/p/DeIA5ptklwD/ · **Date** 5 Oct 2026 · **Likes/comments** 2,412 / 15 · **Multiple** 1.3x · **Reposts** 21 · **Slides** 9
- **First slide:** a baby sitting inside a carved pumpkin, with the hook "oh, it's your baby's first halloween? just wait..." and "(positive edition)" underneath.
- **Promise:** a warm flip of the "just wait" warnings new parents get.
- **Structure:** each slide is one tender first (first costume, pumpkin patch photos, handprint keepsakes, seasonal storytime, crinkly leaves); the last is a family in costume, looking back at how small they were.
- **Pace of reveal:** I saw no clear Lovevery product. Slide 5 shows a storytime with a non-Lovevery Halloween book; a toy may be theirs (unclear).
- **Text density:** 10 to 15 words per slide.
- **Persuasion:** nostalgia, firsts, trend reference.
- **Save/share mechanism:** send to a new parent; caption asks for readers' own "just wait" moments.
- **CTA:** engagement question only.
- **LumeBook can adopt:** a "just wait (positive edition)" carousel for a first Hanukkah, first day of gan or becoming a big brother, with the **book as the keepsake on the last slide** ("one day you'll read it together and they'll ask how small they were").
- **Does not fit:** keeping the brand invisible. That works for Lovevery's reach; for LumeBook it would leave nothing to act on.

### 2.12 Slumberkins x @little.kinder.pals (creator collab) vs a Slumberkins brand post
- **URL** https://www.instagram.com/p/DeFz5limy4N/ · **Date** 4 Oct 2026 · **Likes/comments** 93 / 19 · **Multiple** 1.7x Slumberkins' recent non-pinned median (55) · **Reposts** 2 · **Slides** 6
- **First slide:** the product (Hammerhead book and plush) by a routine chart, with the line "we're not just raising children, we're raising future adults" in white rounded type.
- **Promise:** tools that help kids handle big feelings and routines.
- **Structure:** 1 belief hook; 2 to 4 research-sounding claims over photos of a child reading and using the routine chart; 5 empathy (parenting is hard, you don't have to do it alone); 6 keyword CTA.
- **Pace of reveal:** product visible from slide 1, named in the CTA on slide 6 of 6.
- **Text density:** 20 to 25 words per slide.
- **Persuasion:** creator testimonial (caption: her son's impulsive behaviour), authority-sounding claims, empathy, keyword CTA.
- **CTA:** "comment EMOTIONS" (slide 6 and caption).
- **Comments (13 visible):** 1 "EMOTIONS"; the rest praise from teacher/creator accounts (a creator community is likely: inference).
- **Comparison:** the same weekend, Slumberkins' own six-slide Halloween feelings carousel (https://www.instagram.com/p/DeDXYLhma_R/: illustrated ghosts, advice text, no product, no CTA) got 49 likes and 0 comments (0.9x).
- **LumeBook can adopt:** the creator-voiced version: a parent tells their milestone story, the child uses the book (shown as the illustration or with consent), and a keyword CTA ends it. This fits LumeBook's barter batch and personal promo codes.
- **Does not fit:** unsourced developmental claims (for example, that emotion regulation leads to better grades). Brief creators not to make them.

### 2.13 Merav Levy (Hebrew parenting guide): slow-reveal opening, numbered tools
- **URL** https://www.instagram.com/p/DS-j67GDVZH/ · **Date** 1 Jan 2026 · **Likes/comments** 469 / 42 · **Multiple** 4.5x · **Reposts** 7 · **Slides** 15
- **First slide:** her two daughters against a white shutter. Bold outlined Hebrew text with one red keyword says that when we use hurtful words with our kids in a fight... (the sentence continues on the next slides).
- **Promise:** our words become the child's inner voice, and you can repair.
- **Structure:** slides 1 to 7 split one sentence, a phrase per slide (they won't stop loving us / they'll stop loving themselves / they absorb a message / we can repair / we can change); 8 "How?"; 9 to 13 five numbered tools (I-messages, separate the behaviour from the child, an agreed calm-down signal, delay the response, breathe); 14 an engagement graphic (like/comment/share/follow icons) with a handwritten invitation to share and join her parents' community; 15 photo only.
- **Pace of reveal:** her service on slide 14 of 15.
- **Text density:** 5 to 10 words on slides 1 to 8, 25 to 35 on 9 to 13.
- **Persuasion:** guilt then hope, a slow reveal that makes each swipe pay off, numbered tools, share cue.
- **Comments (first 15):** agreement and "saving this", no purchase intent.
- **Second example:** https://www.instagram.com/p/DRKqmgSDYXo/ (17 Nov 2025; 961/67 logged-in, 9.2x; embed shows 675). Four steps to a calmer morning over a **blurred** photo of children, ending with "save the post, send to a friend, share a tip". Comments include two friend tags and "of course I saved".
- **LumeBook can adopt:** for emotional milestones, open with one line per slide for 3 to 6 slides before the tools. Use blurred or illustrated children as backgrounds. Note that Hebrew parenting creators address the reader in the feminine singular (save, send, you'll turn), while LumeBook uses the plural. Worth an A/B test.
- **Does not fit:** a brand showing customers' children's faces unblurred. Her own children are her choice.

### 2.14 Etti Haft (Hebrew gan teacher who sells kits): "I regret the games I brought to my gan"
- **URL** https://www.instagram.com/p/DdYpED4DTdp/ · **Date** 17 Sep 2026 · **Likes/comments** 97 / 245 · **Multiple** 3.8x · **Reposts** 6 · **Slides** 8
- **First slide:** her selfie with Instagram-story-style black highlight text: a small confession, there are games she regrets bringing to her gan.
- **Promise:** a playful tour of kits that "work too well".
- **Structure:** slides 2 to 7 each show a kit she sells (spinning wheel, alef-bet suitcase, cutting workbook, wipe-clean game, colours kit, transitions cube) with a mock complaint; slide 8 asks fellow gan teachers to meet "the magic solution for easy transitions".
- **Pace of reveal:** product on slide 2 of 8.
- **Text density:** 25 to 35 words per slide, in story-native black boxes.
- **Persuasion:** reverse-psychology humour, insider identity (one gan teacher to another), demonstration.
- **CTA:** the caption asks which kit readers are missing. The audience asks for the link itself.
- **Comments (60 top-level read):** about 57 show purchase intent: 51 explicitly ask for the link (the standard Hebrew "would love the link"), several more say "I'd love it", 1 already bought and asks a usage question, 1 asks whether it suits pre-K. She replies in the thread (and presumably by DM: inference).
- **Second example:** https://www.instagram.com/p/DeHCwwijbGq/ (5 Oct 2026; 144/264, 5.6x). Two slides: an autumn musical-chairs game (illustration looks AI-generated: inference) and the activity sheet. CTA: the file goes to her WhatsApp group, comment to join. All 15 first-page comments ask to join.
- **LumeBook can adopt:** Hebrew audiences already comment "would love the link", so "comment a keyword and we'll send the link" fits local habit. A WhatsApp group or channel can serve as the owned list. Gan teachers could also be a recommendation channel (inference).
- **Does not fit:** the cheeky tone suits teachers buying tools. Carousels about a child's fears should stay gentle.

### 2.15 Israeli personalised-book competitors: TinyBook and MeBook
- **TinyBook** https://www.instagram.com/p/DY4UAc2DK8y/ · 28 May 2026 · 5 likes / 0 comments · 0.5x · 7 slides · **no caption**. Slide 1 offers five books your child will be waiting for, with a "swipe to the side" cue whose arrow points left (◀). Slides 2 to 6 are birthday, hero of the gan, fear of the dark, big sibling, a gift from grandparents. Slide 7 asks which story you want to tell and shows a URL button. This is LumeBook's milestone positioning almost word for word, so the space is already contested.
- **MeBook** https://www.instagram.com/p/DdenXHwgA0C/ · 19 Sep 2026 · 1 to 2 likes / 0 comments · 7 slides. Each slide is a book cover with a real child's photo in a circle and an arrow to the illustrated version of that child, plus an orange trust strip (personalised book, "65,000+ satisfied customers", an exciting and empowering gift). The customer number is their claim; I did not verify it. Caption: one line about new books.
- **Takeaway:** in Israel, brand-made catalogue and idea-list carousels get near-zero engagement. The photo-to-illustration before/after is the clearest product demo in the category, but MeBook ran it like an ad, with no story and no CTA.
- **LumeBook can adopt:** the before/after reveal, but as **the payoff slide of a story** (a milestone problem, then "this is how your child becomes the hero", then the free preview). Use only consenting children or an illustrated stand-in.
- **Does not fit:** real children's photos as the "before" without visible consent; unverifiable customer counts.

---

## 3. @lumebookai audit (35 latest posts plus a pinned collab)

Data: the 11 newest via the embed, 24 older via the logged-in grid. Dates: 16 Feb to 27 Sep 2026; 33 of 35 were posted between 12 Aug and 27 Sep. Nothing new in the 9 days to 6 Oct.

| Format | Posts | Median likes | Range | Note |
|---|---|---|---|---|
| Carousel | 6 | 0.5 | 0 to 3 | DcLS4BXm_Nk (3), DdBZCDWG1uN (1), DcdUcxJFsUC (1), Ddlav41GB6W (0), DdZbXZYHW0I (0), DcSssc6GzWs (0) |
| Reel | 25 | 0 | 0 to 5 | 14 of 25 at 0 likes. View counts were not in the captured fields (the earlier "reels median 48" in memory refers to views). |
| Single image | 4 | 1 | 0 to 3 | |
| Pinned creator collab reel (@shoham_novik) | 1 | 72 | n/a | 56 comments: the only post with real engagement. |

- **Comments:** almost every post shows exactly 1 comment. I opened one (DcLS4BXm_Nk): it is LumeBook's own source line (HealthyChildren.org). So **organic comments are essentially 0.**
- **What the carousels look like** (DcLS4BXm_Nk, Ddlav41GB6W, DdZbXZYHW0I, DcdUcxJFsUC seen in full): a clean, consistent template. Teal cover with a big Hebrew title and "swipe" with a left-pointing chevron, numbered cream slides with icons, a "say this" quote box, page counter "2/7", and a purple closing slide with a reframe plus a save/send cue. Topics: a 30-second goodbye ritual at gan, what to say after a potty accident ("don't say / say"), when a child won't say sorry, five skills before grade 1.
- **The gap:** none of the six carousels shows the book, an illustrated child, the free preview, or a way to act (no keyword, no link, no "comment X"). The closing slides ask readers to save, send to someone who is potty training, or comment a number from 1 to 5. Compared with 2.6, 2.7 and 2.14, the playbook move is to add the **product slide plus a keyword-for-free-preview CTA** to this already good educational template.
- **Brand spelling:** caption of Dc8bslnl6Va (6 Sep 2026) spells the brand לומיבוק, which the brand rule then forbade (it was לומבוק until 20 Nov 2026; since then לומיבוק is correct).
- **Cannot know if any LumeBook carousel sold.** With 0 to 3 likes, the problem is reach before format.

---

## 4. Hebrew/Israeli carousel norms observed

- **Swipe cues:** Hebrew carousels that use a cue point it left: LumeBook's "swipe" with a left chevron, TinyBook's "◀ swipe to the side". English accounts use → (Dr Becky, Big Life Journal). Most Hebrew creators (Merav Levy, Etti Haft, Noa Dotan) use no arrow at all.
- **Text density:** wide range. Slow-reveal slides carry 5 to 10 words (Merav Levy). Tip slides carry 20 to 35 words (Merav Levy, Etti Haft, LumeBook). Noa Dotan's OT slides carry 30 to 40. No Hebrew account kept to the 3-word-per-slide style of the product carousels from Wonderbly or Busy Toddler.
- **Typography:** creators mostly use native Instagram/TikTok text styles: white bold with black outline (Merav Levy), black highlight boxes like Stories (Etti Haft), white text on a selfie (Noa Dotan), plus handwriting for personal sign-offs. Brands use designed templates with gradient or flat backgrounds (LumeBook, TinyBook). The native look is what the higher-engagement Hebrew creators use (observation, not proof of cause).
- **Repeated-line hooks** are common: Noa Dotan opens every slide with "just checking you know that...".
- **Form of address:** creators speak to mothers in the feminine singular (save, send, you'll turn). Brands use the plural.
- **CTA style:** (a) the audience comments "would love the link" and the creator replies or DMs (Etti Haft: 51 of 60 comments); (b) comment to join a WhatsApp group (Etti Haft: all 15 sampled); (c) "write in the comments which topic and I'll send it to you" (Noa Dotan); (d) save, send to a friend, tag a friend (Merav Levy, LumeBook). I did not see an Israeli account using an English keyword like "comment APP"; Hebrew keyword triggers were not observed either, so a Hebrew keyword such as ספר is untested here.
- **Children's faces:** mixed. Merav Levy blurs children in one carousel and shows her own daughters in another; Dr Becky shows the room, not the child; MeBook and TinyBook use real or stock child photos.
- **Scale:** Israeli brand accounts (TinyBook, Sifriyat Pijama, Shilav, Materna, MeBook) get 0 to 80 likes on carousels. Hebrew creators get 30 to 1,000. The large Hebrew parenting accounts (Michal Oppenhaim at a 600 median, Koral Shaul at 7,400) are reels-led and post almost no carousels.

---

## 5. Ranked shortlist for LumeBook (most useful first)

1. **Big Life Journal, DeHOmAFExxS:** child's-voice letter, then numbered needs, then a free resource behind a keyword. The ready-made template for "free preview" carousels.
2. **Etti Haft, DdYpED4DTdp (+ DeHCwwijbGq):** Israeli proof that a product carousel plus local comment-for-link habits produces buying-intent comments (about 57 of 60) at 3.8x to 5.6x the account median.
3. **Solid Starts, DPzA3H7jKI9:** pinned how-it-works tour with a keyword CTA. Lowest likes, most actions. The model for LumeBook's pinned "photo → free preview" explainer.
4. **Solid Starts, DeFHklroK3E:** repeated-line meme about stage fears, product only on the last slide, 6.5x. The model for milestone-fear posts.
5. **Wonderbly, DVf6q-ojdHQ:** customer photos built around a dated dress-up event. Translate to Purim and the first day of gan.
6. **Wonderbly, DVno-NEFRqJ:** text-free illustrations for a "first" milestone gift, hint-dropping to a partner, 3.0x.
7. **Slumberkins creator DeFz5limy4N vs brand DeDXYLhma_R:** the creator-voiced version with product and keyword beat the brand-only educational one (93/19 vs 49/0). Supports routing milestone education through barter creators.
8. **Busy Toddler, DQIUIIpgbEv:** gift guide by age with a keyword CTA (10.7K comments). Use for a Hanukkah guide made with an Israeli curator.
9. **Dr Becky, DeIDQsODAis:** "true story" script with the child never shown. A privacy-safe format for gan separation and bedtime.
10. **Merav Levy, DS-j67GDVZH / DRKqmgSDYXo:** Hebrew slow reveal, native outlined type, blurred children, feminine-singular address.

Also study: TinyBook and MeBook (2.15) as competitor baselines, and Dr Becky Dcq2baejOXf for analogy structure (but its 12.5x reflects her authority, not the format).

---

## 6. Cross-example patterns

1. **The last slide decides whether a carousel can sell.** Every post with a large action count ends on a keyword or link instruction: Solid Starts APP (1.55 comments per like), Busy Toddler GUIDE (2.06), Big Life Journal SDC (0.36), Etti Haft (2.5). Educational carousels with no CTA sit at 0.01 to 0.05 comments per like (Dr Becky 0.008, Lovevery 0.006, Merav Levy 0.07 to 0.09).
2. **Likes and actions diverge.** The most action-heavy posts often have average or below-median likes (Solid Starts APP 0.72x, Busy Toddler GUIDE 1.06x). Judge LumeBook carousels on keyword comments and DMs, not likes.
3. **Product in use beats product alone.** Customer or creator photos with the book (Wonderbly occasion posts, 1.9x to 3.0x; the Slumberkins creator post) outperform catalogue/idea lists (TinyBook 0.5x, MeBook, Librio 0.65x, Sifriyat Pijama 0.55x, Yoto sale 1.3x).
4. **Occasions anchor the best personalised-book posts.** Mother's Day, Father's Day, World Book Day, first Halloween. In Israel: Hanukkah, Purim, the first day of school/gan, birthdays, Family Day.
5. **The child's perspective is a strong hook.** "Dear Mom and Dad" (BLJ), the child's school refusal (Dr Becky), the cabin's view (Dr Becky's analogy). LumeBook's books are literally the child's perspective, so this is the most native hook available.
6. **Script contrast** (instead of X, say Y) is the core of expert carousels (Dr Becky, Merav Levy, LumeBook's own). LumeBook already has it; what's missing is the product slide after it.
7. **Pure education with no product only works with big reach.** Dr Becky and Big Little Feelings reach tens of thousands with brand-light carousels; the Slumberkins brand post and LumeBook's carousels get almost nothing.
8. **Text density is not the variable.** Expert carousels run 40 to 60 words per slide and still do 1x to 12x; product carousels run 0 to 8 words. Match density to job: emotional or educational slides can be wordy, product and occasion slides should be nearly wordless.
9. **Reposts are a weak signal.** The highest repost rates were on opinion/news pieces (Dr Becky's Cornell post 9.7% of likes, Big Little Feelings' advocacy carousel 8.8%). Most other posts sat at 2% to 4% (Dr Becky's pilot 2.3%, Solid Starts 3.0% and 3.6%, Busy Toddler 2.1%). Small accounts have 1 to 7 reposts, too few to compare.
10. **Privacy patterns exist and do not obviously cost engagement:** room without child (Dr Becky), blurred children (Merav Levy, 9.2x), illustration only. These suit a brand whose product is a child's likeness.
11. **Trust is a live issue for personalised books:** a commenter on Wonderbly's ABC carousel (Dd3t79siK8a) wrote to confirm it is "not a scam" after receiving her order. LumeBook (AI, new, Israeli) should expect the same doubt and answer it on the CTA slide (free preview first, pay later).

---

## 7. Limits of this evidence

- **No conversion data.** None of these carousels has public sales, clicks, DM volume, saves, DM shares or reach. For every one: cannot know if it sold. Keyword comments show intent to receive a link, not purchases.
- **Small windows.** Medians come from 12 posts per account, including pinned posts that have had months to accumulate likes (DPzA3H7jKI9 and DQIUIIpgbEv are about a year old). One viral post moves a median a lot.
- **Counts differ by source.** Logged-in and embed counts disagree for some posts (up to about 30% fewer likes in the embed). I used logged-in counts for multiples and marked embed-only numbers.
- **Comment samples are partial.** I read the first 15 top-level comments per post, 54 to 60 for two posts. Many keyword comments come with automated replies. Same-handle commenters across Wonderbly posts suggest a creator community or pod (inference). Comments do not show who bought.
- **Paid boosts are invisible.** I flag likely ads or hidden likes only by odd patterns (Big Life Journal's 3-like posts with 25 to 288 comments; Hooray Heroes collabs with 3 likes). These are inferences.
- **Selection bias.** I picked accounts and posts for relevance to LumeBook, not at random. The Hebrew creator sample comes from a few Instagram searches (parent guidance, psychologist, gan teacher, speech therapist, OT) and is small.
- **Audience size dominates.** Big Little Feelings and Dr Becky have audiences thousands of times LumeBook's. Their formats can be copied; their reach cannot.
- **Format effects are confounded** with topic, timing, creator, occasion and paid support. Nothing here shows that a carousel causes sales.
- **Secondary sources.** The only external benchmark I verified is Socialinsider's (35M posts, Jan to Dec 2025, published as "2026"): carousels 0.55%, Reels 0.52%, images 0.37% engagement by followers ([Socialinsider](https://www.socialinsider.io/social-media-benchmarks/instagram)). Vendor blogs claim comment-to-DM flows convert better than link-in-bio ([ManyChat blog](https://manychat.com/blog/instagram-dm-automations-for-ecommerce/), [Smartreply](https://smartreply.io/blog/instagram-comment-dm-automation-guide)). Those are vendor claims I did not verify; do not use them for decisions.
- **Interface details are not verified.** I did not verify whether Instagram mirrors carousel swipe direction for Hebrew-interface users; the arrow observations are about what creators draw, not how the app behaves.
