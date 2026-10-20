# CTAs, on-screen text, caption and disclosure: evidence notes

Area: calls to action, text on screen, the caption (description), sponsorship disclosure, Hebrew/RTL.
Prepared 2026-10-18 for the LumeBook product Reels playbook. All sources were opened in this task and accessed 2026-10-18. Scope tags on each evidence line: [IG organic] Instagram organic, [IG ads] / [Meta ads] paid placements, [FB] Facebook feed, [lab] experiments outside social media, [IL] Israel.

## 1. Summary

- Instagram ranks Reels on predicted watch time, sends (shares) and likes. Mosseri (Jan 2025) says sends weigh slightly more for reaching non-followers. A CTA that earns a real send to a named person ("שלחי למי שמחפשת מתנה לגיל 3") fits the ranking better than a "save this" or "like if" ask. No study shows that asking for sends causes more of them.
- Asking for engagement just to game reach is engagement bait: Meta demotes it on Facebook, and Instagram says it may leave such content out of recommendations. "Comment a word and get the link by DM" (ManyChat style) is allowed when it starts a real conversation (Instagram, June 2024). Meta's private-reply API allows one DM per comment, within 7 days.
- One CTA beats several. A study of more than 2,000 brand posts found that more than one CTA in a message lowered engagement. The general choice-overload effect is contested: one meta-analysis finds an average of about zero, another finds a real effect when the task is hard or the viewer wants to spend little effort.
- The claim that "85% of video is watched without sound" comes from 2016 publisher data on Facebook, and Meta never confirmed it. Meta itself says over 75% of Instagram Reels views are sound on (Nov 2024). Captions are still worth it: a 2019 survey of 5,616 US adults (Verizon Media / Publicis) found 69% watch with sound off in public, a 2015 review of over 100 studies found captions improve comprehension and memory, and Hebrew was not among Instagram's 17 auto-caption languages at launch. So burn in Hebrew captions, using key words rather than full transcripts.
- Keep text inside Meta's Reels safe zone (top 14%, bottom 35%, sides 6%; this spec is published for ads only). Don't make the Reel mostly text, and don't leave another app's watermark: Instagram shows such Reels less or not at all in recommendations.
- In Hebrew, keep each text card on screen long enough to read at no more than 17 characters per second (Netflix's Hebrew subtitle standard). Start every line with a Hebrew letter, so that Unicode bidi rules do not throw punctuation and numbers to the wrong side.
- The caption is search text: Instagram matches searches against captions and hashtags, not comments. Hashtags are capped at 5 (Dec 2025), and Mosseri says they do not increase reach. Studies of caption length contradict each other. A question in the caption raises comments (Facebook study of 355 posts).
- Disclosure is a legal duty in Israel, not a style choice. The Consumer Protection Authority's 2021 draft directive says payment or a free product must be disclosed clearly, near the content, as advertising. Under the same draft, the free product must not depend on a positive opinion. The Attorney General's position (as reported by a law firm) is that disclosure must be visible at first glance. In 2023 the Authority fined Similac's importer NIS 5.5 million over hidden advertising in mothers' groups. The research on disclosure and persuasion is mixed: a meta-analysis of 61 papers found small losses in brand attitude and credibility, while a field study of 810,168 posts found that posts with the paid-partnership label got more likes.

## 2. Principles

### Calls to action

#### C1. One CTA per Reel

- **Rule:** The Reel asks for one action. The same action may appear in voice, on screen and in the caption, but no second, different action is added.
- **Evidence:**
  - [Driving consumer engagement through diverse calls to action in CSR messages on social media](https://scholars.ln.edu.hk/en/publications/driving-consumer-engagement-through-diverse-calls-to-action-in-co/), Chae, *Sustainability* 13(7) 3812, 2021, DOI 10.3390/su13073812. Peer-reviewed, more than 2,000 branded posts on Facebook and Twitter [FB, Twitter]. More than one CTA in a single message lowered engagement. Invitations to a program or game raised likes and shares, while reward-based calls did worse.
  - [Message content features and social media engagement](https://mural.maynoothuniversity.ie/id/eprint/13927/), Moran, Muzellec and Johnson, *J. Product & Brand Management* 29(5) 533-545, 2020, DOI 10.1108/JPBM-09-2018-2014. Peer-reviewed, 757 Facebook posts from one radio brand over 15 weeks, negative binomial model [FB]. A CTA aimed at one behaviour lifted all four behaviours measured (clicks, likes, comments, shares). One clear ask does not cost the other signals.
  - [Can there ever be too many options? A meta-analytic review of choice overload](https://academic.oup.com/jcr/article-lookup/doi/10.1086/651235), Scheibehenne, Greifeneder and Todd, *J. Consumer Research* 37(3), 2010, DOI 10.1086/651235. Peer-reviewed meta-analysis, 63 conditions from 50 experiments, N = 5,036 [lab]. The mean choice-overload effect was "virtually zero", with high variance between studies.
  - [Choice overload: a conceptual review and meta-analysis](https://api.openalex.org/works/doi:10.1016/j.jcps.2014.08.002), Chernev, Böckenholt and Goodman, *J. Consumer Psychology* 25(2) 333-358, 2015, DOI 10.1016/j.jcps.2014.08.002 (abstract read via OpenAlex). Peer-reviewed meta-analysis, 99 observations, N = 7,202 [lab]. Overload becomes reliable with complex choice sets, hard tasks, uncertain preferences and an effort-minimising goal.
- **Strength:** Moderate. The multiple-CTA result comes from one peer-reviewed study of brand posts (CSR topics, not Reels), and choice overload in general is contested.
- **Transfer to LumeBook:** A scrolling parent wants to spend little effort (one of Chernev's overload conditions), so give one ask: "כתבו לומי ואשלח קישור", not that plus "follow" plus "tag a friend".
- **How to spot it in a Reel:** Count the distinct requested actions across the transcript, the text cards and the caption (comment word, follow, save, send, tag, link in bio, buy). Code 0, 1, or 2 or more. Note whether repeats of the same action appear in several channels.

#### C2. Ask for engagement only when it has a purpose

- **Rule:** Every engagement ask has a real purpose (get a link, answer a question, give a recommendation). There are no "like if", "comment yes", "tag 3 friends" or "share to win" asks whose only goal is the count.
- **Evidence:**
  - [News Feed FYI: Fighting Engagement Bait on Facebook](https://about.fb.com/news/2017/12/news-feed-fyi-fighting-engagement-bait-on-facebook/), Meta (Silverman and Huang), 18 Dec 2017, updated 7 Nov 2019. Platform-official [FB]. Posts that goad people into likes, shares or comments to gain reach are demoted, and Pages that do it repeatedly get Page-level demotion. Since January 2019 this also covers bait spoken in a video's audio. Requests for help, advice or recommendations are exempt.
  - [Engagement bait, Content Distribution Guidelines](https://transparency.meta.com/features/approach-to-ranking/content-distribution-guidelines/engagement-bait/), Meta Transparency Center, undated. Platform-official [FB]. Defines bait as explicitly requesting votes, shares, comments, tags or likes for purposes other than a specific call to action. Stated scope is Facebook only. Listed under demoted content on [Types of content we demote](https://transparency.meta.com/features/approach-to-ranking/types-of-content-we-demote/) (updated 2 Jul 2025).
  - [Helping creators find new audiences (Recommendations and originality)](https://creators.instagram.com/recommendations-and-Originality), Instagram for Creators, 30 Apr 2024. Platform-official [IG organic]. Lists content that users say they dislike, "such as clickbait or engagement bait", as possibly not recommended.
  - [Instagram says using certain CTAs can impact post reach](https://www.socialmediatoday.com/news/instagram-says-using-certain-ctas-can-impact-post-reach/717732/), Social Media Today (Hutchinson), 2 Jun 2024. Trade press reporting an Instagram video that was deleted within about a day [IG organic]. Content that explicitly asks for shares, comments or tags would not be recommended. Open-ended questions and CTAs were called "fair game".
- **Strength:** Strong that the policy exists (platform-official on both apps). Weak on how Instagram detects bait, since Instagram would not say which terms are penalised.
- **Transfer to LumeBook:** Frame every ask as a service ("רוצים לראות איך זה נראה עם השם של הילד? כתבו לומי"). Never "תגיבו כן אם אתם אוהבים".
- **How to spot it in a Reel:** Flag spoken or written asks of the form like / comment X / tag N / share IF or TO WIN with no stated benefit to the viewer. Separate them from asks that deliver something (a link, an answer, a recommendation).

#### C3. Comment-keyword-to-DM is a legitimate conversion CTA within the API rules

- **Rule:** When a Reel's goal is a sale, it can ask for one Hebrew keyword in the comments, and an automated DM then delivers the personal link. The DM goes out within 7 days of the comment, is the only unprompted message, and any follow-up comes only after the person replies.
- **Evidence:**
  - [Send a Private Reply to a Commenter](https://developers.facebook.com/docs/instagram-platform/private-replies/), Meta for Developers, undated. Platform-official [IG organic]. A professional account can send one private reply to a commenter on a post, reel, story, Live or ad, within 7 days of the comment. A follow-up is allowed only if the person responds, within 24 hours of that response. The DM lands in Requests if the person does not follow the account.
  - [Instagram clarifies advice on single-word CTAs](https://www.socialmediatoday.com/news/instagram-clarifies-advice-on-single-word-ctas-and-longer-reels/718151/), Social Media Today, 5 Jun 2024. Trade press reporting Instagram's @creators clarification [IG organic]. Using tools like ManyChat to talk with the audience is fine, and earnest engagement in comments and DMs is not bait. Prompts meant to inflate counts can reduce recommendations, and the article notes it is unclear how the system tells the two apart.
  - [HypeAuditor x Manychat study](https://hypeauditor.com/manychat/), HypeAuditor with Manychat, undated. Industry study, 6,000 US creators with 1,000+ followers, about 3,000 using DM automation [IG organic]. Users of DM automation got 40 to 150% more comments per post and grew 30 to 140% faster per year. The study is correlational, its partner sells the tool, and it does not explain how the groups were matched.
- **Strength:** Strong on the mechanics (API documentation), weak on the effect size (vendor correlation only), contested on reach risk (Instagram reversed its own advice within days).
- **Transfer to LumeBook:** This fits the project's code word לומי and the creator personal link. The DM, not the caption, carries the link, and the DM must not call it a "קוד הנחה".
- **How to spot it in a Reel:** A keyword is named on screen, in voice or in the caption (record the word and where it appears). Check whether the creator's replies show an automated DM. Note whether the keyword is a brand word or a generic word.

#### C4. Give a reason to send, and prioritise sends over saves

- **Rule:** When reach to non-followers is the goal, the Reel gives a specific person to send it to and a reason, tied to a real need. Save prompts are optional and secondary.
- **Evidence:**
  - [Instagram shares algorithm insights to inform strategy](https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/), Social Media Today, 22 Jan 2025, quoting a Mosseri video. Platform-official statement reported by trade press [IG organic]. The top three signals are watch time, likes and sends, and creators should watch likes per reach and sends per reach. Sends are slightly more important for content shown to non-followers, likes for followers.
  - [Instagram Ranking Explained](https://about.instagram.com/blog/announcements/instagram-ranking-explained), Mosseri, 31 May 2023. Platform-official [IG organic]. The most important Reels predictions are the chance you reshare, watch to the end, like, and visit the audio page. Saves and comments appear only as signals about your past activity.
  - [Instagram Reels Chaining system card](https://transparency.meta.com/features/explaining-ranking/ig-reels-chaining/), Meta, updated 11 Nov 2025. Platform-official [IG organic]. Significant predictions include the chance you reshare a reel, share it off Instagram, comment, follow the author, watch more than 95% of viewers of same-length reels, or watch less than 3 seconds. Likes and saves appear only as input signals.
  - Moran et al. 2020 (C1): a CTA aimed at a behaviour lifted that behaviour in Facebook posts [FB].
- **Strength:** Strong that sends matter for ranking (three platform-official sources). Weak that asking for a send produces sends on Reels: no direct study found, and a generic "share this" could read as share bait (C2).
- **Transfer to LumeBook:** Grandparents and gift buyers are the natural targets of a send: "שלחו לסבתא שתמיד שואלת מה לקנות".
- **How to spot it in a Reel:** A send ask is present (yes/no). Code whether the recipient is named ("לאמא", "לחברה שמחפשת מתנה") and whether a reason is given. Code a save ask separately. Note the format (list, tip, gift idea) that might earn a save without being asked.

#### C5. Ask an open, specific question when comments are the goal

- **Rule:** When comments are the goal, the Reel or caption ends with one open, specific question that a parent can answer from their own life, not a yes/no or one-word prompt.
- **Evidence:**
  - [Popularity of Brand Posts on Brand Fan Pages](https://api.openalex.org/works/doi:10.1016/j.intmar.2012.01.003), De Vries, Gensler and Leeflang, *J. Interactive Marketing* 26(2) 83-91, 2012, DOI 10.1016/j.intmar.2012.01.003 (abstract read via OpenAlex). Peer-reviewed, 355 posts from 11 international brands [FB]. A question in a post raises the number of comments, but not likes. Vivid and interactive features raise likes.
  - Reels Chaining system card (C4): the chance you will comment is one of the significant ranking predictions [IG organic].
  - Social Media Today, 2 Jun 2024 (C2): Instagram called open-ended questions "fair game" while warning about asking for a specific word, number or emoji [IG organic].
- **Strength:** Moderate. The peer-reviewed finding is old and from Facebook, while the ranking relevance is official.
- **Transfer to LumeBook:** "איזה שם הייתם שמים על הכריכה?" or "מה הילד שלכם הכי אוהב לשמוע לפני השינה?" invite real answers and give creators material for replies.
- **How to spot it in a Reel:** A question is present at the end of the transcript, on the last text card or in the caption (code where). Classify it as open or closed (yes/no, one word, emoji), and note whether it is answerable from personal experience.

#### C6. Say the CTA and show it, after the value and inside the safe zone

- **Rule:** The CTA is both said and shown on screen, after the product or benefit has been shown, sits inside the safe zone, and is repeated in the first line of the caption.
- **Evidence:**
  - [Deconstructing the Power of Reels: How Creative Strategies Can Drive Success](https://www.facebook.com/business/news/reels-creative-strategies), Meta for Business, 2 Dec 2025. Platform-official research done with Toluna (sample size, markets and dates not given) [Meta ads]. Among direct-response ads, a CTA delivered visually and/or by audio was 1.9 times more likely to rank in the top 20% for purchase intent. For brand ads, brand and main message in the first 5 seconds gave 1.7 times.
  - [Unlock the Power of Reels Ads](https://developers.facebook.com/blog/post/2024/11/07/unlock-the-power-of-reel-ads/), Meta for Developers (Rocha, Wong, Baker), 7 Nov 2024. Platform-official guidance with no statistic for this point [Meta ads]. It advises landing the CTA at the end of the ad and putting key messages in the safe zone.
  - [Instagram Reels ad specs](https://www.facebook.com/business/ads-guide/update/video/instagram-reels), Meta Ads Guide, undated. Platform-official [IG ads]. Keep the top 14%, the bottom 35% and 6% on each side free of text and key elements, so the profile icon and CTA button do not cover them.
- **Strength:** Moderate for ads (official but exploratory, purchase intent probably self-reported). Weak for organic Reels: no organic timing study was found.
- **Transfer to LumeBook:** End the Reel with a short spoken line and a text card ("כתבו לומי בתגובות"), placed above the caption area, and open the caption with the same words.
- **How to spot it in a Reel:** CTA timestamp (first 3 s, middle, last 3 s). CTA channel: voice only, text only, or both. Whether the CTA text box overlaps the bottom 35% or top 14%. Whether the first caption line repeats the CTA.

#### C7. Keep the sell light: little brand time, the product shown twice, a benefit named

- **Rule:** The brand name or logo is on screen for no more than about a quarter of the Reel, the product appears at least twice, and at least one concrete benefit or feature is said or shown.
- **Evidence:**
  - Meta for Business, 2 Dec 2025 (C6), Toluna exploratory research [Meta ads]. For direct-response ads: brand on screen for no more than 25% of the duration gave 4.8 times, product shown more than once 2.7 times, and product context (unique selling points, features) 5.3 times the likelihood of top-20% purchase intent. For brand ads, everyday "slice of life" scenes gave 1.5 times.
  - Chae 2021 (C1): reward-based calls were less effective than invitations [FB, Twitter].
- **Strength:** Weak to moderate. One platform source on ads, no sample size, and a likelihood-of-top-tier measure.
- **Transfer to LumeBook:** Show the child's name on the cover twice (opening and reveal) and name one benefit ("הוא מוצא את עצמו בכל עמוד"). Say לומבוק once, near the end.
- **How to spot it in a Reel:** Seconds with a logo or brand name visible, divided by total length. Count of separate product appearances. Whether a specific benefit or feature is stated. Whether the scene is an everyday routine (bedtime, birthday).

Method note for all C rules: Instagram's trial reels are shown to non-followers first ([Create engaging content](https://creators.instagram.com/create-engaging-content), Instagram for Creators, undated). They are a practical way to A/B test two CTA versions on the same footage.

### On-screen text, caption and disclosure

#### T1. Make the Reel work with sound off: burned-in Hebrew captions or key text

- **Rule:** Anything said that carries the message also appears as burned-in Hebrew text, so a muted viewer gets the point.
- **Evidence:**
  - [Video captions benefit everyone](https://pmc.ncbi.nlm.nih.gov/articles/PMC5214590/), Gernsbacher, *Policy Insights from the Behavioral and Brain Sciences* 2(1) 195-202, 2015, DOI 10.1177/2372732215602130. Peer-reviewed review of more than 100 studies [lab]. Captions improve comprehension, attention and memory, including brand-name memory in literate adults and literacy in hearing children.
  - [80% of video caption users aren't hearing impaired, finds Verizon](https://www.streamingmedia.com/Articles/News/Online-Video-News/80-of-Video-Caption-Users-Arent-Hearing-Impaired-Finds-Verizon-131860.aspx), Streaming Media (Dreier), 20 May 2019, on the Verizon Media / Publicis Media survey. Industry survey, 5,616 US adults aged 18 to 54, April 2019 [all video]. 69% watch with sound off in public and 25% in private. On mobile, captions lifted ad recall by 8% and ad memory quality by 10%. A brand logo plus captions cut ad memory by 12%.
  - [Capture attention with updated features for video ads](https://www.facebook.com/business/news/updated-features-for-video-ads), Facebook for Business, undated (a 2016-era captions launch). Platform-official internal tests [FB ads]. Captioned video ads raised view time by 12% on average, and in one study 41% of video ads were basically meaningless without sound.
  - [Unlock the Power of Reels Ads](https://developers.facebook.com/blog/post/2024/11/07/unlock-the-power-of-reel-ads/), Meta, 7 Nov 2024. Platform-official, no method given [IG]. Over 75% of Reels views on Instagram are sound on. This is the counterweight: captions serve a sizeable minority plus comprehension, not a muted majority.
  - [Instagram is rolling out auto-generated captions](https://techcrunch.com/2022/03/01/instagram-is-rolling-out-auto-generated-captions-for-videos/amp/), TechCrunch (Malik), 1 Mar 2022. Trade press with a list confirmed by Instagram [IG organic]. Auto captions launched in 17 languages, and Hebrew was not one of them. The current list was not verified.
- **Strength:** Moderate. Captions aiding comprehension is strong in lab work, and the sound-off share for Reels is lower than often claimed.
- **Transfer to LumeBook:** Burn the Hebrew captions in (don't rely on Instagram's auto captions). Every LumeBook Reel with a voice line needs them.
- **How to spot it in a Reel:** Captions present (none, auto-style sticker, burned-in). Share of spoken message words that appear on screen. Whether the message is understandable from muted frames alone (a coder watches muted first, then with sound).

#### T2. On-screen text shows key words, not a full transcript, and does not compete with a busy picture

- **Rule:** Captions show short key phrases synced to speech, not a transcript, and no full sentence sits on screen while the product is being demonstrated.
- **Evidence:**
  - [Verbal redundancy in multimedia learning environments: a meta-analysis](https://api.openalex.org/works/doi:10.1037/a0026147), Adesope and Nesbit, *J. Educational Psychology* 104(1) 250-263, 2012, DOI 10.1037/a0026147 (abstract read via OpenAlex). Peer-reviewed meta-analysis of 57 studies [lab]. Spoken plus written beat spoken only, most for system-paced material (as Reels are), for low prior knowledge, and without pictures. Showing key terms instead of verbatim text improved learning and explained much of the advantage.
  - [Multimedia design for learning: an overview of reviews with meta-meta-analysis](https://api.openalex.org/works/doi:10.3102/00346543211052329), Noetel et al., *Review of Educational Research*, 2021, DOI 10.3102/00346543211052329. Peer-reviewed, 29 reviews, 1,189 studies, 78,177 participants [lab]. Signalling, contiguity and captioning of second-language video had the largest benefits, and design mattered more for system-paced material.
  - Verizon / Publicis 2019 (T1): a logo plus captions on mobile cut ad memory by 12% [all video]. Stacking elements can backfire.
- **Strength:** Moderate. The evidence is from learning, not ads, but it is consistent and Reels are system-paced.
- **Transfer to LumeBook:** During the cover reveal, show the child's name and one phrase ("השם שלו על הכריכה"), not the whole sentence the parent is saying.
- **How to spot it in a Reel:** Words on screen per text card. Verbatim or keyword captions. Whether text overlaps the moment the product is shown. Whether captions and a logo or second text block appear at the same time.

#### T3. A headline text card in the first second states the topic or promise

- **Rule:** By about the first second there is a short text card that tells the viewer what they will get. It is delivered together with the opening picture or sound, not after a slow intro.
- **Evidence:**
  - Reels Chaining system card (C4): the chance you watch less than 3 seconds is a significant ranking prediction [IG organic].
  - Meta for Business, 2 Dec 2025 (C6) [Meta ads]: a hook delivered both visually and with sound gave 1.5 times the likelihood of top-20% purchase intent, and brand plus main message in the first 5 seconds 1.7 times (brand ads).
- **Strength:** Moderate. The official ranking input says early skips matter, but the effect of headline text in particular is shown only for ads.
- **Transfer to LumeBook:** Open on the child's face plus a card like "הוא עוד לא יודע שהוא הגיבור של הספר".
- **How to spot it in a Reel:** Time of first text appearance (seconds). Whether it states a topic, promise or question. Words in the first card. Whether voice and text open together.

#### T4. Text stays inside the safe zone, the Reel is not mostly text, and there is no other app's watermark

- **Rule:** All text sits inside the frame, clear of the top 14%, the bottom 35% and 6% on each side. Text does not dominate the Reel, and no watermark from another app or platform is visible.
- **Evidence:**
  - [Instagram Reels ad specs](https://www.facebook.com/business/ads-guide/update/video/instagram-reels), Meta Ads Guide, undated. Platform-official [IG ads]. Safe zone of at least 14% top, 35% bottom and 6% sides; 9:16 format, 1440 x 2560 recommended.
  - [Instagram Reels Safe Zone Checker](https://www.inro.social/tools/instagram-reels-safe-zone-checker), Inro (vendor), undated. Practitioner. Meta publishes these margins only for ads, and no official organic figure exists. Inro also reports that Meta's help article says ads with disclaimers should keep the bottom 40% clear.
  - [Instagram & Facebook Reels ads](https://www.facebook.com/business/ads/facebook-instagram-reels-ads), Meta for Business, undated. Platform-official [Meta ads]. Recommends keeping key messages in the safe zone and reports a 2x gain (metric not named) for 9:16 campaigns with audio and messages in the safe zone.
  - [Instagram Ranking Explained](https://about.instagram.com/blog/announcements/instagram-ranking-explained), Mosseri, 31 May 2023. Platform-official [IG organic]. Reels that are low resolution, watermarked, muted, bordered, mostly text or already posted on Instagram are made less visible.
  - [Recommendations and originality](https://creators.instagram.com/recommendations-and-Originality), Instagram, 30 Apr 2024. Platform-official [IG organic]. Visible watermarks make a Reel ineligible for recommendation.
- **Strength:** Strong for watermarks and mostly-text Reels (organic, official). Strong for the safe zone in ads, moderate when applied to organic Reels (the UI is similar but no official organic figure exists).
- **Transfer to LumeBook:** Export from CapCut or another editor without its end card or watermark, and keep the Hebrew text in the middle band above the caption overlay.
- **How to spot it in a Reel:** Text box bounding boxes compared with the 14/35/6 zones. Share of frames where text covers most of the picture. Any visible watermark or app logo, and from which app.

#### T5. Hebrew text stays long enough to read, in big type with strong contrast

- **Rule:** Each text card stays on screen for at least its character count divided by 17 seconds (never under about 0.8 s), uses at most 2 lines of about 42 characters, and has a contrast of at least 4.5:1 with its background (3:1 for large bold text).
- **Evidence:**
  - [Hebrew Timed Text Style Guide](https://partnerhelp.netflixstudios.com/hc/en-us/articles/220636427-Hebrew-Timed-Text-Style-Guide), Netflix Partner Help, change log to 19 Dec 2025. Industry standard [subtitling, Hebrew]. Hebrew reading speed is capped at 17 characters per second for adult programmes and 13 for children's, with 42 characters per line and two lines at most.
  - [Timed Text Style Guide: General Requirements](https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617), Netflix, updated 7 Oct 2022. Industry standard [subtitling]. A subtitle event lasts at least 5/6 of a second and at most 7 seconds.
  - [Understanding SC 1.4.3 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), W3C WCAG 2.2, updated 6 Sep 2026. Standard [web]. Contrast must be at least 4.5:1 for normal text and 3:1 for large text (18 pt, or 14 pt bold). Text over a background image that lacks contrast is a listed failure.
- **Strength:** Moderate. These are established standards for subtitles and the web, not tested on Reels engagement.
- **Transfer to LumeBook:** A 34-character Hebrew card needs at least 2 seconds. Treat 17 cps as a ceiling for an audience that includes grandparents. Use a solid or shaded plate behind text on busy home footage.
- **How to spot it in a Reel:** For each card: characters, seconds on screen, and characters per second. Number of lines. Text colour against the background (estimate contrast from a frame).

#### T6. Hebrew lines start with a Hebrew letter, and punctuation and numbers are checked for RTL

- **Rule:** Every Hebrew text line begins with a Hebrew letter (not "LumeBook", an emoji or a digit), and its final punctuation, numbers and Latin words display in the right places on the exported frame.
- **Evidence:**
  - [UAX #9: Unicode Bidirectional Algorithm](https://www.unicode.org/reports/tr9/), Unicode Consortium, revision 52, 1 Sep 2026. Technical standard. When an app detects direction automatically, it comes from the first strong letter in the paragraph (rules P2 and P3). Punctuation at the edge of a right-to-left run in a left-to-right paragraph takes the paragraph's direction (rules N1 and N2). Hence a "?" that lands on the wrong side, or a line that flips when it starts with English or a digit.
  - Netflix Hebrew Timed Text Style Guide (T5) [subtitling, Hebrew]. Write numbers 1 to 10 in words except dates, write currency names out, keep English abbreviations only when space or reading speed demands it, and break lines at grammatical points in a bottom-heavy shape.
- **Strength:** Moderate. The standard is authoritative, but editing apps can override it, and no study links RTL errors to engagement.
- **Transfer to LumeBook:** "לומבוק" rather than "LumeBook" at the start of a line. Check the "?" and "!" on the exported frame, not in the editor.
- **How to spot it in a Reel:** Punctuation at the wrong end of a Hebrew line, reversed or misplaced numbers, a line starting with Latin letters, an emoji or a digit, mixed-direction lines.

#### T7. The caption is a searchable Hebrew description: plain keywords, up to 5 specific hashtags, and the hook or CTA in the first line

- **Rule:** The caption names the product and occasion in the words parents would search, has at most 5 specific hashtags in the caption itself (not in a comment), and its first line carries the hook or CTA. Caption length is a free choice to test.
- **Evidence:**
  - [Shedding more light on how Instagram works: Search](https://about.instagram.com/blog/announcements/break-down-how-instagram-search-works), Mosseri, 25 Aug 2021. Platform-official [IG organic]. Typed text is matched against usernames, bios, captions, hashtags and places. Keywords and hashtags belong in the caption, since comments are not used for search.
  - [Instagram Search system card](https://transparency.meta.com/features/explaining-ranking/ig-search/), Meta, updated 23 Jun 2026. Platform-official [IG organic]. Lists word similarity to usernames, profile names, suggested keywords and hashtags. It does not mention captions or on-screen text explicitly.
  - [@creators post on captions](https://www.instagram.com/p/Db_N-P6kbt2/), Instagram @creators, 13 Aug 2026. Platform-official [IG organic]. A caption holds attention, sparks conversation and helps people find content through search. The tips themselves are in carousel slides the fetch could not show. [House of Marketers](https://houseofmarketers.com/?p=22207) (practitioner, 23 Aug 2026) reports those slides as advising an opening question, surprising fact or tease, and one clear next step.
  - [Instagram implements new limits on hashtag use](https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/), Social Media Today, 18 Dec 2025, on an @creators Threads post. Platform statement via trade press [IG organic]. Five hashtags per post or reel, rolling out to everyone after about a year of tests. Mosseri said hashtags "don't work" to increase reach (Feb 2025) but help show what a post is about (May 2025).
  - [Instagram posts and reels will now pop up on Google and Bing](https://www.theweek.in/news/sci-tech/2025/07/12/social-media-instagram-posts-and-reels-will-now-pop-up-on-google-and-bing-searches-how-to-enable-disable-this-setting.amp.html), The Week (Kapoor), 12 Jul 2025. Press, quoting the Help Center [IG organic]. Public Reels and posts from professional accounts run by adults, from 1 Jan 2020 on, can be indexed by search engines (on by default). My inference, not tested: the caption words are what a Google searcher would match.
  - [Instagram caption length study](https://www.socialinsider.io/blog/instagram-caption-length/), Socialinsider, 21 Feb 2024, updated 2 Jun 2026. Industry study, 9,117,401 posts from 82,952 business pages, Jan to Jul 2023, engagement divided by followers [IG organic]. Captions under 30 words usually had higher engagement. No Reels figures in the text.
  - [Instagram caption length](https://postplanify.com/blog/instagram-caption-length), PostPlanify (Cagli), 13 Jul 2026, updated 12 Oct 2026. Industry study, 6,126 posts and Reels from 168 accounts, Jul to Oct 2026, engagement divided by reach [IG organic]. Reels captions up to 125 characters had 1.69% median engagement against 4.32% for 500+, but higher median reach (711 against 241). An earlier wave found little difference. The authors call it correlation.
- **Strength:** Strong for keywords and hashtags in the caption (platform-official), contested for caption length (studies conflict), weak for the first-line advice (practitioner, not measured).
- **Transfer to LumeBook:** First line: hook or "כתבו לומי". Then one plain line with searchable words (ספר ילדים מותאם אישית, מתנה ליום הולדת 3, ספר עם השם של הילד), then up to 5 specific hashtags.
- **How to spot it in a Reel:** Caption characters and words. Number of hashtags and whether they are generic or specific. Whether product and occasion keywords appear. What the first line does (hook, CTA, question, description). Hashtags placed in a comment instead of the caption.

#### T8. Disclose every paid, gifted or commissioned Reel clearly at first view

- **Rule:** Any creator Reel made in exchange for money, a free book, a discount or a commission states the commercial relationship in Hebrew, visible without tapping "more" (an early on-screen text and/or the first caption line), and uses Instagram's paid-partnership label. The free book is not conditional on a positive opinion.
- **Evidence:**
  - [Draft Commissioner's directive on online opinions, ratings and reviews (טיוטת הנחיית ממונה)](https://www.gov.il/BlobFolder/news/cpfta_internetopinion2021/he/docs_draft_supervisor_guide.pdf), Israel Consumer Protection and Fair Trade Authority (Michael Atlan), 5 Jan 2021 (DRAFT; I could not confirm a final version). Regulator [IL]. It applies to businesses marketing through influencers and bloggers. Payment or another incentive, such as free clothing, given for an opinion must be disclosed clearly and close to it ("יש לגלות זאת בצורה ברורה בסמוך לפרסום חוות הדעת"). The disclosure is the commercial relationship, and that the content is in effect an advertisement. Incentives are allowed only if they are given whether the opinion is positive or negative, with that stated in advance. Violations are treated as misleading under section 2 of the Consumer Protection Law, 1981. Summary in [ICE](https://www.ice.co.il/consumerism/news/article/801907), 5 Jan 2021.
  - [The hidden influence: consumer protection law and hidden advertising](https://www.calcalist.co.il/local_news/article/r1i11ewsin), Calcalist, Barnea Jaffa Lande (Even-Chen, Ivri Shtern), 5 Jun 2023. Law-firm commentary [IL]. The Attorney General's opinion (date not given) requires disclosure that is explicit, unambiguous and in common words, prominent at first viewing with no extra step. Free products, discounts and reciprocal promotion also count. Expectations are stricter for content aimed at minors. No specific word is named.
  - [Similac / influencer agency fine](https://www.calcalist.co.il/shopping/article/bkn0eecaj), Calcalist (Yafet), 15 Feb 2023. Press report of regulator enforcement [IL]. The Authority fined Abbott NIS 5.5 million and an influencer agency about NIS 500,000 over fictitious profiles in about 100 Facebook groups, many for mothers, and over "ambassadors" not disclosed as linked to the company. The companies disputed the findings and Abbott appealed.
  - [IDI opinion on the Covert Advertising bill P/2159](https://www.idi.org.il/ministerial-committees/1590), Israel Democracy Institute (Schwartz Altshuler), 29 Apr 2016. Policy analysis [IL]. A 2015 private bill proposed a uniform disclosure label across media. Its status was not stated, and I found no statute specific to influencers.
  - [How Instagram creators can share branded content with the right community](https://creators.instagram.com/blog/instagram-creators-branded-content-share-right-audience-restrictions), Instagram for Creators, 19 Apr 2022. Platform-official [IG organic]. Branded Content Policies require the paid-partnership label on all branded content posts. The full policy pages on help.instagram.com did not render for me.
  - [A meta-analysis of the effects of disclosing sponsored content](https://research.wur.nl/en/publications/a-meta-analysis-of-the-effects-of-disclosing-sponsored-content/), Eisend, van Reijmersdal, Boerman and Tarrahi, *J. Advertising* 49(3) 344-366, 2020, DOI 10.1080/00913367.2020.1765909. Peer-reviewed, 61 papers, 57 data sets [all media]. Disclosure raises recognition, persuasion knowledge and resistance, and lowers brand attitude, credibility and source evaluation. Content, timing and awareness of the disclosure are boundary conditions.
  - [Effects of explicit sponsorship disclosure on user engagement in social media influencer marketing](https://aisel.aisnet.org/misq/vol48/iss1/15), Cao and Belo, *MIS Quarterly* 48(1) 375-392, 2024, DOI 10.25300/misq/2023/17944. Figures from the [OSF preprint](https://osf.io/b8tsg). Peer-reviewed field study plus two experiments, 1,355 matched influencers, 810,168 Facebook and Instagram posts [IG and FB organic]. Sponsored posts disclosed with the platform's header tag ("Paid partnership with") got about 34% more likes and 14% more comments (the comments result at p < 0.1) than sponsored posts without it, explained by transparency. The study is observational with fixed effects, and the published numbers may differ from the preprint.
  - [Effects of disclosing sponsored content in blogs](https://repub.eur.nl/pub/96705), van Reijmersdal et al., *American Behavioral Scientist* 60(12), 2016, DOI 10.1177/0002764216660141. Peer-reviewed, two experiments, N = 118 and 134 [blogs]. Disclosure activated persuasion knowledge, which led to counterarguing and negative affect.
- **Strength:** Strong that there is a duty to disclose in Israel (regulator draft, AG position, enforcement), even though the directive's final status and an exact required word were not confirmed. Contested on the persuasion cost: lab meta-analysis negative, Instagram field data positive for the platform label.
- **Transfer to LumeBook:** Every barter creator states it, for example "שיתוף פעולה עם לומבוק, קיבלתי את הספר במתנה", on an early text card or the first caption line, plus the paid-partnership label. The barter terms state that the book does not depend on a positive review. This is not legal advice: check the final directive and wording with a lawyer.
- **How to spot it in a Reel:** Paid-partnership header present. Hebrew disclosure words ("פרסומת", "שיתוף פעולה", "בשיתוף", "קיבלתי במתנה", "ממומן") and where they appear (on screen with timestamp, first caption line, after "more", hashtag only). Whether the disclosure is visible without tapping.

## 3. Myths and contested claims

- **"85% of Facebook video is watched without sound."** Traced to [Digiday, 17 May 2016](https://digiday.com/media/silent-world-facebook-video/). The figure came from publishers' own Facebook data (LittleThings and Mic 85%, PopSugar 50 to 80%, MEC branded clients 85 to 90%), with no method and no confirmation from Facebook, in the muted-autoplay feed era. Meta now says over 75% of Instagram Reels views are sound on (Nov 2024, no method). Verdict: outdated and platform-specific, don't quote it for Reels.
- **"Viewers are 80% more likely to watch to the end with captions" (Verizon / Publicis 2019).** Neither [Streaming Media's report](https://www.streamingmedia.com/Articles/News/Online-Video-News/80-of-Video-Caption-Users-Arent-Hearing-Impaired-Finds-Verizon-131860.aspx) nor [3Play Media's summary](https://www.3playmedia.com/blog/verizon-media-and-publicis-media-find-viewers-want-captions/) contains it, and [AdAccessibility](https://adaccessibility.org/adaccessibility/2024/06/26/verizon-media-and-publicis-media-find-viewers-want-captions) gives no figures. I found no Verizon original. Verdict: untraced. The traceable figures are 69% sound off in public, plus 8% recall and 10% memory-quality lifts from captions on mobile.
- **"80% of caption users are not deaf or hard of hearing."** Streaming Media reports it as a Verizon survey finding, and 3Play attributes it to Ofcom (UK TV subtitles; I did not open the Ofcom original). It is a self-reported figure about who uses captions, not evidence that captions raise performance.
- **"Sends count 3 to 5 times more than likes."** Not in Mosseri's quoted statements, which only say sends are "slightly more important" for unconnected reach. Verdict: untraced industry estimate.
- **"Comment-a-word CTAs get your reach cut."** Instagram's June 2024 video said asking for a specific word could block recommendations, and days later it clarified that genuine ManyChat-style use is fine. Verdict: contested, and detection is opaque. Keep the keyword purposeful (C2, C3).
- **"Hashtags boost reach; use 30; put them in the first comment."** Mosseri says hashtags don't increase reach (2025), the cap is now 5 (Dec 2025), and Instagram search ignores comments (2021). Verdict: false for 2026.
- **"Instagram reads on-screen text for search."** Repeated by practitioners (Planoly, per search results). None of the Instagram sources I read (2021 search post, 2026 Search system card, 2026 @creators post) mention reading on-screen text. Verdict: untraced. Put keywords in the caption.
- **"Meta's organic Reels safe zone is 14% top, 35% bottom."** These are Meta's Reels ads specs, and no official organic figure exists. Verdict: a reasonable proxy, not an organic rule.
- **"Fewer choices always convert better (the jam study)."** The famous jam study (Iyengar and Lepper 2000) was not opened here. Meta-analyses find an average effect of about zero (Scheibehenne 2010) or a moderated, real effect (Chernev 2015). Verdict: contested. The one-CTA rule rests more on Chae 2021 than on choice overload.
- **"Short captions win" vs "long captions win."** Socialinsider (9.1M posts, divided by followers) favours under 30 words, while PostPlanify (6,126 posts, divided by reach) finds longer Reels captions had higher engagement but lower reach. Verdict: contested, and both are correlational. Test on the account.
- **"Text overlays raise clicks by up to 127%" / "56% higher CTR per Meta".** The [Science Says](https://app.sciencesays.com/p/the-text-overlay-formula-to-optimize-ads) claim is paywalled and names no paper, and [Adobe's](https://blog.adobe.com/en/publish/2024/11/04/unlock-potential-reels-best-practices-for-creative-success-using-adobe-creative-cloud) "Meta's analysis" gives no link. Verdict: untraced.
- **"DM automation gets 90% open rates and 70% click-through."** These figures appeared only in vendor and affiliate search results (not opened, not used). The one structured study (HypeAuditor with Manychat) is correlational and vendor-partnered. Verdict: anecdotal.
- **"Disclosure kills performance."** It lowers brand attitude and credibility in lab studies (Eisend 2020), but on Instagram and Facebook the platform label went with more likes and comments (Cao and Belo 2024). Verdict: contested, and the law decides anyway.
- **"Instagram auto-captions handle Hebrew."** Hebrew was not among the 17 launch languages (2022), and the current list was not verified. Verdict: unverified, so burn captions in.

Gaps (searched, nothing usable found): discount code vs personal link performance (only an EMAC 2022 conference paper on discount codes, whose PDF I could not read); link-in-bio vs DM-link conversion; CTA timing within organic Reels; any study of Hebrew on-screen text and engagement; reading speed of older viewers on phones.

## 4. Sources (all accessed 2026-10-18)

Read and used:
- https://developers.facebook.com/docs/instagram-platform/private-replies/ : Meta for Developers, private replies (7-day window, one message).
- https://transparency.meta.com/features/approach-to-ranking/types-of-content-we-demote/ : Meta, types of content demoted, updated 2 Jul 2025.
- https://transparency.meta.com/features/approach-to-ranking/content-distribution-guidelines/engagement-bait/ : Meta, engagement bait definition (Facebook).
- https://about.fb.com/news/2017/12/news-feed-fyi-fighting-engagement-bait-on-facebook/ : Meta, engagement bait demotion, 18 Dec 2017.
- https://creators.instagram.com/recommendations-and-Originality : Instagram, recommendation eligibility, 30 Apr 2024.
- https://www.socialmediatoday.com/news/instagram-says-using-certain-ctas-can-impact-post-reach/717732/ : SMT, 2 Jun 2024.
- https://www.socialmediatoday.com/news/instagram-clarifies-advice-on-single-word-ctas-and-longer-reels/718151/ : SMT, 5 Jun 2024.
- https://about.instagram.com/blog/announcements/instagram-ranking-explained : Mosseri, 31 May 2023.
- https://transparency.meta.com/features/explaining-ranking/ : Meta system cards index.
- https://transparency.meta.com/features/explaining-ranking/ig-reels-chaining/ : Reels system card, 11 Nov 2025.
- https://transparency.meta.com/features/explaining-ranking/ig-search/ : Search system card, 23 Jun 2026.
- https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/ : SMT on Mosseri signals, 22 Jan 2025.
- https://hypeauditor.com/manychat/ : HypeAuditor x Manychat study.
- https://scholars.ln.edu.hk/en/publications/driving-consumer-engagement-through-diverse-calls-to-action-in-co/ : Chae 2021.
- https://mural.maynoothuniversity.ie/id/eprint/13927/ : Moran et al. 2020.
- https://academic.oup.com/jcr/article-lookup/doi/10.1086/651235 : Scheibehenne et al. 2010.
- https://api.openalex.org/works/doi:10.1016/j.jcps.2014.08.002 : Chernev et al. 2015 abstract.
- https://api.openalex.org/works/doi:10.1016/j.intmar.2012.01.003 : De Vries et al. 2012 abstract.
- https://api.openalex.org/works/doi:10.1037/a0026147 : Adesope and Nesbit 2012 abstract.
- https://api.openalex.org/works/doi:10.3102/00346543211052329 : Noetel et al. 2021 abstract.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5214590/ : Gernsbacher 2015.
- https://www.streamingmedia.com/Articles/News/Online-Video-News/80-of-Video-Caption-Users-Arent-Hearing-Impaired-Finds-Verizon-131860.aspx : Verizon / Publicis coverage, 20 May 2019.
- https://www.3playmedia.com/blog/verizon-media-and-publicis-media-find-viewers-want-captions/ : 3Play, 19 Jul 2019.
- https://adaccessibility.org/adaccessibility/2024/06/26/verizon-media-and-publicis-media-find-viewers-want-captions : AdAccessibility, 26 Jun 2024.
- https://digiday.com/media/silent-world-facebook-video/ : Digiday, 17 May 2016.
- https://www.facebook.com/business/news/updated-features-for-video-ads : Facebook captions launch (undated).
- https://developers.facebook.com/blog/post/2024/11/07/unlock-the-power-of-reel-ads/ : Meta, 7 Nov 2024.
- https://www.facebook.com/business/ads/facebook-instagram-reels-ads : Meta Reels ads page.
- https://www.facebook.com/business/news/reels-creative-strategies : Meta / Toluna Reels creative research, 2 Dec 2025.
- https://houseofmarketers.com/meta-shares-reels-tips-for-marketers-2026/ : practitioner summary used to locate the Meta page, 3 Dec 2025.
- https://blog.adobe.com/en/publish/2024/11/04/unlock-potential-reels-best-practices-for-creative-success-using-adobe-creative-cloud : Adobe, 4 Nov 2024 (untraced Meta figure).
- https://www.facebook.com/business/ads-guide/update/video/instagram-reels : Meta Reels ad specs and safe zone.
- https://www.inro.social/tools/instagram-reels-safe-zone-checker : Inro safe-zone notes.
- https://techcrunch.com/2022/03/01/instagram-is-rolling-out-auto-generated-captions-for-videos/amp/ : TechCrunch, 1 Mar 2022.
- https://about.instagram.com/blog/announcements/break-down-how-instagram-search-works : Mosseri, 25 Aug 2021.
- https://www.socialmediatoday.com/news/instagram-outlines-how-its-search-algorithms-work-and-how-you-can-optimize/605596 : SMT, 25 Aug 2021.
- https://www.instagram.com/p/Db_N-P6kbt2/ : @creators caption post, 13 Aug 2026.
- https://houseofmarketers.com/?p=22207 : House of Marketers on Instagram caption tips, 23 Aug 2026.
- https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/ : SMT, 18 Dec 2025.
- https://www.theweek.in/news/sci-tech/2025/07/12/social-media-instagram-posts-and-reels-will-now-pop-up-on-google-and-bing-searches-how-to-enable-disable-this-setting.amp.html : The Week, 12 Jul 2025.
- https://www.socialinsider.io/blog/instagram-caption-length/ : Socialinsider, 2024 (updated 2026).
- https://postplanify.com/blog/instagram-caption-length : PostPlanify, 2026.
- https://creators.instagram.com/ , https://creators.instagram.com/best-practices , https://creators.instagram.com/create-engaging-content : Instagram creators pages (trial reels).
- https://creators.instagram.com/blog/instagram-creators-branded-content-share-right-audience-restrictions : Instagram, 19 Apr 2022.
- https://research.wur.nl/en/publications/a-meta-analysis-of-the-effects-of-disclosing-sponsored-content/ : Eisend et al. 2020.
- https://repub.eur.nl/pub/96705 : van Reijmersdal et al. 2016.
- https://api.openalex.org/works/doi:10.25300/misq/2023/17944 , https://aisel.aisnet.org/misq/vol48/iss1/15 , https://osf.io/b8tsg (preprint PDF, text extracted locally) : Cao and Belo 2024.
- https://www.gov.il/BlobFolder/news/cpfta_internetopinion2021/he/docs_draft_supervisor_guide.pdf : Consumer Protection Authority draft directive, 5 Jan 2021 (text extracted locally).
- https://www.ice.co.il/consumerism/news/article/801907 : ICE on the draft directive, 5 Jan 2021.
- https://www.calcalist.co.il/local_news/article/r1i11ewsin : Calcalist / Barnea Jaffa Lande, 5 Jun 2023.
- https://www.calcalist.co.il/shopping/article/bkn0eecaj : Calcalist, Similac fine, 15 Feb 2023.
- https://www.idi.org.il/ministerial-committees/1590 : IDI on bill P/2159, 29 Apr 2016.
- https://library.mevaker.gov.il/sites/DigitalLibrary/Pages/Reports/10593-8.aspx : State Comptroller 2026 consumer report summary (no influencer content).
- https://partnerhelp.netflixstudios.com/hc/en-us/articles/220636427-Hebrew-Timed-Text-Style-Guide : Netflix Hebrew guide, updated 19 Dec 2025.
- https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617 : Netflix general requirements, 7 Oct 2022.
- https://partnerhelp.netflixstudios.com/hc/en-us/search?query=Hebrew+Timed+Text+Style+Guide : Netflix help search (to locate the Hebrew guide).
- https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html : W3C WCAG 2.2 contrast, updated 6 Sep 2026.
- https://www.unicode.org/reports/tr9/ : Unicode UAX #9, revision 52, 1 Sep 2026.
- https://app.sciencesays.com/p/the-text-overlay-formula-to-optimize-ads : Science Says, 11 Nov 2025 (paywalled, untraced).

Opened but not readable or not used (JavaScript-only, blocked, wrong page or no content):
- https://help.instagram.com/313829416281232 , https://www.facebook.com/help/instagram/313829416281232 , https://help.instagram.com/1695974997209192 , https://www.facebook.com/policies/brandedcontent/ , https://www.facebook.com/business/help/1675722002698686 : page shells only.
- https://transparency.meta.com/features/explaining-ranking/ig-reels/ , https://about.instagram.com/blog/tips-and-tricks/instagram-ranking-explained/ , https://transparency.meta.com/policies/other-policies/branded-content-policies/ : 404.
- https://www.gov.il/he/departments/news/cpfta_internetopinion2021 , https://www.tandfonline.com/doi/full/10.1080/00913367.2020.1765909 , https://journals.sagepub.com/doi/10.1177/2372732215602130 , https://www.sciencedirect.com/science/article/pii/S1057740814000916 , https://myscp.onlinelibrary.wiley.com/doi/10.1016/j.jcps.2014.08.002 , https://research.rug.nl/files/1401108846/s11002-024-09757-z.pdf (Liu and Zhao 2024 meta-analysis) , https://searchengineland.com/meta-rolls-out-branded-content-on-reels-388801 : 403.
- https://link.springer.com/article/10.1007/s11002-024-09757-z : login redirect.
- https://proceedings.emac-online.org/pdfs/A2022-107739.pdf : PDF text not extractable.
- https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/ : blocked.
- https://partnerhelp.netflixstudios.com/hc/en-us/articles/216001127-Hebrew-Timed-Text-Style-Guide : resolved to the Korean guide.
- Semantic Scholar API records for 10.1037/a0026483, 10.1016/j.jcps.2014.08.002, 10.1016/j.intmar.2012.01.003 : abstracts elided (the first DOI was a wrong guess and is a different paper).
