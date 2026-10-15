# Brief: code Instagram posts by Israeli parenting creators for LumeBook

## Context
LumeBook (Hebrew: לומבוק) sells personalised children's books in Israel: a parent uploads the child's photo and name, the child becomes the illustrated hero, there is a free preview, the printed book costs ₪119 (list ₪149). Best-selling occasions: birthday, new sibling (אח חדש / אחות חדשה), pacifier weaning, potty/diaper weaning, starting gan, first grade. We are studying what content by creators on our creator map interests potential buyers and what prompts buying consideration. You code posts. You do NOT judge whether a post "converts"; there is no sales data per post.

## Inputs
You get one dossier file per creator: `dossiers/<handle>.json` with the creator profile and a list of posts. Each post has: `code`, `url`, `set` (sample = the creator's recent baseline; breakout = older outlier, coded the same way), `format`, `date`, `age_days`, public metrics, `caption` (full text), `alt` (Instagram's automatic image description, can be wrong), tags, `paid_label` (Instagram's paid-partnership flag), `coauthors`, `sheets` (paths to contact sheets), `duration_s`.
- Reels: one contact sheet with 6 frames at 0.3 s, 1.5 s, 3 s, 35%, 65%, 92% of the video, timestamp in yellow above each frame.
- Carousels: sheets with every slide (6 per sheet), labelled "slide N".
- Images: the image.
Open EVERY sheet listed for every post with the Read tool. Where a sheet is missing, code from caption + alt only and say so in `inspection`.

## Evidence rules
- You cannot hear audio. Never describe speech, music or tone. A reel's spoken hook is unknown unless burned-in captions show it. Say "spoken content not available" where it matters.
- Quote on-screen Hebrew exactly as written (keep it short, under 15 words), then an English gloss. If you cannot read it, write `[unclear]`. Do not invent text.
- Separate what you SEE (frames/slides), what the CAPTION says, and what you INFER. Put inferences only in fields marked inference or in `notes`, phrased as "likely" / "appears".
- Do not guess the age, location, income or parenthood of anyone from their looks or name. A child's age only if the caption or on-screen text states it.
- No em dashes anywhere. Use commas, colons or periods.
- Keep personal details out: no children's full names, no addresses, no phone numbers.

## Output
Write `coded/<handle>.json`: a JSON list, one object per post, exactly these keys:
```
{
 "code": "",
 "topic": "short noun phrase, English",
 "problem_or_desire": "the specific parent problem or desire the post speaks to, one sentence",
 "occasion": "birthday | new_sibling | pregnancy | pacifier | potty_diaper | gan_start | first_grade | sleep_bedtime | holiday | gift_general | grandparent | reading_books | development_learning | behaviour_emotions | daily_parenting | family_outing | food_home | humour_entertainment | other",
 "occasion_note": "if a LumeBook buying occasion is present, what exactly (e.g. 'child turning 3 next week'); else ''",
 "buyer_segment": "mother_baby_0_1 | mother_toddler_1_3 | mother_preschool_3_6 | mother_school_6_10 | expecting_parent | father | parents_general | grandparent_or_relative | educator | professional_peer | general_audience | unclear",
 "buyer_segment_basis": "what in the post points to that audience (caption words, on-screen text); 'inferred' if only from topic",
 "format_detail": "talking_head | skit_pov | vlog_day | text_on_broll | hands_demo | product_review | unboxing | before_after | tips_carousel | story_carousel | quote_or_text_card | photo_dump | single_photo | giveaway_post | collab_reel | other",
 "length_s": number or null,
 "hook_text": "first on-screen text in frame 0.3 s / 1.5 s, or slide 1 headline, quoted in Hebrew + English gloss; '' if none visible",
 "caption_first_line": "first line of caption, Hebrew + gloss (short)",
 "hook_type": "problem_first | relatable_moment | curiosity | contrarian | outcome_first | question | list_number | story | emotional_confession | humour_setup | demonstration | announcement | giveaway | none_visible",
 "emotional_angle": "humour | tenderness | nostalgia | reassurance | frustration_relief | pride | guilt | fear_anxiety | inspiration | excitement | neutral_info",
 "practical_takeaway": "the concrete thing a parent can do after this post, or 'none'",
 "product_visible": "none | incidental | featured | demonstrated",
 "product_category": "none | children_book | toy_game | baby_gear | food | home_cleaning | clothing | service_or_course | own_product | app_digital | attraction_trip | other",
 "product_detail": "brand or product named in caption/on screen, or ''",
 "proof": "none | child_reaction | parent_testimonial | before_after | expert_credential | social_proof_numbers | demonstration_result",
 "price_visible": true/false,
 "discount_or_code": "exact wording if a discount/coupon/code/link offer appears (caption or on screen), else ''",
 "cta": "comment_keyword | link_in_bio | dm | tag_friend | share | save | follow | buy_link | join_group_or_course | answer_question | none",
 "cta_detail": "the exact CTA wording, Hebrew + gloss, or ''",
 "destination": "where the CTA sends people: bio link, DM, brand account, website, WhatsApp, none",
 "status": "organic | paid_partnership_label | likely_sponsored | collaboration | giveaway | own_product_promo | unclear",
 "status_basis": "why (paid label, #שיתוף_פעולה, brand tag + code, giveaway rules...)",
 "lumebook_relevance": "high | medium | low",
 "lumebook_relevance_reason": "one sentence: which buying occasion or behaviour links it to a personalised book, or why it does not",
 "inspection": "frames+caption | slides+caption | image+caption | caption_only (no media)",
 "notes": "anything uncertain; inferences labelled"
}
```
Definitions:
- `lumebook_relevance` high = the post is about a LumeBook buying occasion (birthday, new sibling, pacifier, potty, gan, first grade, bedtime stories, reading, a gift for a child) OR recommends a children's book/gift. medium = parenting topic where a book could plausibly help (emotions, behaviour, development, routines). low = unrelated (food, cleaning, fashion, travel, pure humour).
- `status` paid_partnership_label only when the dossier `paid_label` is true. likely_sponsored = brand tagged or named plus a code/link/"שת״פ"/"בשיתוף"/"#ad" but no label. giveaway = הגרלה/זוכה/לזכות rules.

Validate your file at the end: `python3 -c "import json;d=json.load(open('coded/<handle>.json'));print(len(d))"` and fix errors (escape quotes inside strings). Return a 3-line summary: posts coded, how many had media missing, anything odd.
