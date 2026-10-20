# Editing and content topic: evidence notes for the product Reels playbook

Scope: how a Reel is cut and finished (E principles) and what it is about and why people watch and share it (K principles). Written 2026-10-18 for the LumeBook product Reels playbook (173 coded Israeli creator Reels).

How to read this file:
- Evidence types, best first: **platform-official** (Instagram, Meta, TikTok), **peer-reviewed** (journal and DOI given), **industry study** (method and sample stated), **news report** (journalist reporting a platform statement), **practitioner** (opinion, used sparingly).
- Every source below was opened in this task. For paywalled journals I read the publisher abstract or the abstract served by the OpenAlex scholarly index (api.openalex.org); the line says "abstract read" when that is all I saw. Full text was read only for Berger and Milkman (JMR) and Dost and Huang (2026).
- "Scope" says what the finding was measured on (TV, paid ads, TikTok, Facebook, news articles) and how far it transfers to organic Instagram Reels.
- Numbers are exactly as the source states them. Where a source gives no method, that is said.

---

## 1. Summary

- **Instagram itself is the strongest evidence for the finishing rules.** Its ranking page and creator FAQ say Reels are for entertainment, that the system predicts reshares, full watches, likes and audio-page visits, and that low-resolution, watermarked, muted, bordered, mostly-text and reposted Reels are shown less. Reels must be 3 minutes or less to reach non-followers. These are checkable rules, not opinions.
- **Originality is now an account-level rule.** Since April 2024 Instagram swaps reposts for the original in recommendations, and since April 2026 (Mosseri, as reported) an account whose posts are mostly other people's content stops being recommended at all. Third-party watermarks reduce reach. A trend recreation has to add LumeBook's own footage or voice.
- **Cut pace has a ceiling.** TV lab work (Annie Lang) shows cuts trigger orienting responses and faster edits within one scene raise arousal and memory, but fast pace plus already-arousing content overloads viewers and lowers recall. The only short-form experiment found (Dost and Huang 2026, N=242, conference paper) found higher pacing reduced intent to keep watching; high-performing German talking-head TikToks averaged 0.37 cuts per second (about one cut every 2.7 s).
- **Sound is on for most Reels viewers, so design for sound, then caption for the rest.** Meta says over 75% of Instagram Reels views are sound-on (no method given). A LumeBook business account cannot use Instagram's licensed music library; it can use Meta's Sound Collection (14,000+ royalty-free tracks) or original audio. Instagram says trending audio can affect distribution but gives no size.
- **For content, high-arousal positive emotion and story outperform information alone.** Peer-reviewed field data (Berger and Milkman, 6,956 NYT articles; Tellis et al. 2019, video ads) agree: awe, amusement, excitement, warmth and surprise are shared; sadness and pure product information are shared less. A meta-analysis of 76 articles (van Laer et al.) supports story transportation as a persuasion route.
- **Relatable humour is backed by both Instagram and research.** Instagram's FAQ says relatable humorous content typically earns more engagement and reshares; a meta-analysis (Eisend, 369 correlations) finds humour raises attention, liking and purchase intention but lowers source credibility, so keep developmental claims straight-faced.
- **The product should be part of the story, with brand talk kept short.** Emotional ads in which the brand is integral get both shares and better brand outcomes (Akpinar and Berger); prominent early branding hurts sharing (Tellis), while brand plus core message in the first 5 seconds raised purchase intent in a Meta and Toluna ad study. For an organic Reel that sells a personalised book, the book in use is the brand.
- **Israel-specific evidence is thin.** DataReportal puts Instagram's Israeli ad reach at 5.00 million (74.0% of adults, 54.2% female) in late 2025. One peer-reviewed comparison found Israeli parents' online forum talk leans to social-emotional development and parenting issues. No Hebrew-language study of Reel editing or content topic was found.

---

## 2. Principles

### Editing

#### E1. Open with motion and the point inside 3 seconds

- **Rule:** By second 3 the viewer has seen a change (a cut, movement or a face reacting) and knows what the Reel is about (spoken line, on-screen text or the book visible).
- **Evidence:**
  - [Instagram for Creators: Frequently Asked Questions](https://creators.instagram.com/faq?locale=en_US), Instagram, undated live page (read 2026-10-18), platform-official. Advises making the first 3 seconds engaging so people do not move on, and to upload the highest resolution possible.
  - [Emotion-Induced Engagement in Internet Video Advertisements](https://doi.org/10.1509/jmr.10.0207), Teixeira, Wedel and Pieters, Journal of Marketing Research, index record dated 2011, peer-reviewed lab experiment with facial-expression detection, eye tracking and recorded zapping (abstract read). Joy and surprise concentrate attention and keep viewers from zapping; the rise in joy matters more for retention than its level. Scope: online video ads in a lab; transfers well to the swipe decision.
  - [Involuntary Attention and Physiological Arousal Evoked by Structural Features and Emotional Content in TV Commercials](https://doi.org/10.1177/009365090017003001), Lang, Communication Research, 1990, peer-reviewed (abstract read). Structural features such as cuts trigger involuntary attention responses measured by heart rate; mild emotional content strengthens them. Scope: TV ads.
  - [Capturing Attention in Feed: The Science Behind Effective Video Creative](https://www.facebook.com/business/news/insights/capturing-attention-feed-video-creative), Facebook IQ, 20 April 2016, platform-official research (850+ to 965 video ads; the page gives both figures). People recalled mobile feed content after 0.25 seconds of exposure; average time per feed item was 1.7 s on mobile. Scope: Facebook feed ads in 2014 to 2015, before Reels; use only as a sign that first frames are read very fast.
  - [What actually makes short-form video ads work? (Meta x Toluna)](https://tolunacorporate.com/what-makes-short-form-video-ads-work-meta-toluna-study/), Toluna, 4 August 2026, industry study (about 100 ads, about 100 viewers per ad, Germany, UK, Italy, Turkey, 65+ coded variables). Ads showing brand and core message in the first 5 seconds were 1.7x more likely to drive strong purchase intent. Scope: paid short-form ads, correlational, no baseline given.
- **Strength:** moderate. Instagram states it plainly, and lab work explains why, but no source gives an Instagram retention curve or a tested 3-second effect size.
- **Transfer to LumeBook:** open on the child's face as they see themselves in the book, or the book opening, not on a logo or a slow establishing shot.
- **How to spot it in a Reel:** `first_change_s` (time of first cut or large movement), `face_by_3s` (yes/no), `topic_clear_by_3s` (spoken line, text or product on screen by 3 s), `opening_type` (face reaction, product, question text, action, logo, static).

#### E2. Cut to remove dead air, at a moderate pace, within one scene

- **Rule:** Talking or demo sections use seamless jump cuts that remove pauses within the same scene, at roughly one cut every 2 to 5 seconds; the Reel avoids rapid unrelated scene changes, especially over emotional moments.
- **Evidence:**
  - [The Effects of Edits on Arousal, Attention, and Memory for Television Messages: When an Edit Is an Edit Can an Edit Be Too Much?](https://doi.org/10.1207/s15506878jobem4401_7), Lang, Zhou, Schwartz, Bolls and Potter, Journal of Broadcasting and Electronic Media, 2000, peer-reviewed (abstract read). As the rate of edits (camera changes within the same scene) rose from slow to very fast, physiological arousal, self-reported arousal and memory rose, without a significant rise in cognitive load. Scope: TV messages in a lab.
  - [The effects of production pacing and arousing content on the information processing of television messages](https://doi.org/10.1080/08838159909364504), Lang, Bolls, Potter and Kawahara, Journal of Broadcasting and Electronic Media, 1999, peer-reviewed (abstract read). Fast pace and arousing content each raise processing resources, but together they overload viewers and lower recognition and cued recall. Scope: TV.
  - [The Effects of Related and Unrelated Cuts on Television Viewers' Attention, Processing Capacity, and Memory](https://doi.org/10.1177/009365093020001001), Lang, Geiger, Strickwerda and Sumner, Communication Research, 1993, peer-reviewed (abstract read). Both cut types caused cardiac orienting responses; unrelated cuts (new scene, new content) needed more capacity and memory was better after related cuts, especially visual memory. Scope: TV; maps well onto jump cuts (related) versus scene-hopping transitions (unrelated).
  - [Jump Cut Editing Style and Transition Frequency Differentially Affect Interactive and Sustained Engagement in Short-Form Video](https://archives.marketing-trends-congress.com/2026/pages/PDF/paper_professor_DOST_HUANG.pdf), Dost and Huang (Brandenburg University of Technology), Marketing Trends Congress 2026, conference paper, peer review not confirmed (full text read). Pre-study: 50 high-performing informative German talking-head TikToks averaged 0.37 cuts/s (SD 0.17, range 0.13 to 0.82). Experiment (N=242 convenience sample, seven versions of one 20 s clip, sound on, self-reported intentions): seamless cuts raised liking versus overlapping cuts and no edit; overlapping cuts raised intent to keep watching or rewatch, but less so as cut frequency rose; higher pacing reduced sustained engagement overall. Scope: TikTok-style talking head, German viewers, intentions not behaviour.
- **Strength:** moderate. Consistent across 30 years of lab work and one short-form experiment, but none of it is on organic Instagram behaviour and the short-form study is small.
- **Transfer to LumeBook:** for a parent talking to camera, cut out pauses and false starts; for the child's reaction, hold the shot and do not stack fast cuts on top of an already emotional moment.
- **How to spot it in a Reel:** `cuts_total` and `cuts_per_10s` (count shot changes from frames), `cut_type` per cut (jump cut same scene, scene change, transition effect), `longest_shot_s`, `cuts_during_peak_emotion` (count of cuts in the 3 s around the reaction).

#### E3. Use speed changes on objects and movement, not on people "enjoying" the product

- **Rule:** Slow motion, if used, is applied to pleasant, detailed movement (pages turning, a gift being unwrapped) and not to a person visibly enjoying the product; fast motion is reserved for energetic, exciting sequences.
- **Evidence:**
  - [The Art of Slowness: Slow Motion Enhances Consumer Evaluations by Increasing Processing Fluency](https://doi.org/10.1177/00222437231179187), Stuppy, Landwehr and McGraw, Journal of Marketing Research, 2024 (online 2023), peer-reviewed, a large field data set plus six experiments (abstract read). Slow motion raised likes, votes and views of short-form videos and raised brand liking, choice and willingness to pay, mostly for pleasant content with complex movement; fast motion helped brand evaluations when viewers wanted excitement. Scope: short-form video including reels, directly relevant.
  - [The Effect of Slow Motion Video on Consumer Inference](https://doi.org/10.1177/00222437211025054), Yin, Jia and Zheng, Journal of Marketing Research, 2021, peer-reviewed, seven studies including eye tracking and a Facebook Ads field experiment (abstract read). Slow motion of people consuming and enjoying a product can backfire: their behaviour looks intentional and paid, which lowers product appeal; the effect reverses with non-human agents. Scope: video ads, including on Facebook.
- **Strength:** moderate. Two multi-study papers in a top journal, and they fit together (slow motion helps objects and movement, can hurt human endorsers).
- **Transfer to LumeBook:** slow motion on the personalised page reveal or the cover in hand is supported; slow motion on a parent's or child's delighted face risks looking staged.
- **How to spot it in a Reel:** `speed_change` (none, slow, fast, ramp), `speed_subject` (object, hands, person face, crowd), `speed_moment` (reveal, transition, reaction).

#### E4. Build for sound on, and caption the speech in short synced chunks

- **Rule:** The Reel carries its message in audio (voice or natural sound), is never silent, and shows short on-screen text or captions timed to the speech, inside the safe zone, never filling most of the frame.
- **Evidence:**
  - [Unlock the power of Reel ads](https://developers.facebook.com/blog/post/2024/11/07/unlock-the-power-of-reel-ads/), Meta for Developers blog, 7 November 2024, platform-official. States that over 75% of Reels views on Instagram are sound-on (no source or method given) and advises building with audio such as voiceover, music or sound effects and keeping key messages inside the safe zone. Scope: written for ads, the sound-on figure is about all Reels views.
  - [Instagram Ranking Explained](https://about.instagram.com/blog/announcements/instagram-ranking-explained), Instagram (Adam Mosseri), 31 May 2023, platform-official. Reels that are muted, have borders or are majority text are made less visible.
  - [Instagram's "How to build effective Reels ads" guide](https://onlinemarketing.de/social-media-marketing/instagrams-how-to-build-effective-reels-ads-leitfaden), OnlineMarketing.de, 12 September 2022, news report of a Meta guide shown at a Meta event. The guide said 80% of Reels are watched with sound and that ads breaking the Reels safe zone had 28% lower click-through rate (no method given). Scope: ads, 2022.
  - [Kantar report: How brands are making noise and driving impact with sound on TikTok](https://ads.tiktok.com/business/en/blog/kantar-report-how-brands-are-making-noise-and-driving-impact-with-sound-on-tiktok), TikTok for Business, 8 June 2021, platform-commissioned industry study (Kantar; sample not stated on the page). 88% of TikTok users said sound is essential; 73% said they would stop and look at TikTok ads with audio. Scope: TikTok; transfers as a sign that short vertical video is a sound-on medium.
  - Meta x Toluna study (link in E1), industry study. Creative combining audio and visual cues outperformed visuals alone. Scope: paid ads.
  - [Video Captions Benefit Everyone](https://doi.org/10.1177/2372732215602130), Gernsbacher, Policy Insights from the Behavioral and Brain Sciences, 2015, peer-reviewed review of more than 100 studies (abstract read). Captions improve comprehension of, attention to and memory for video for most viewers.
  - [Cognitive constraints on multimedia learning: When presenting more material results in less understanding](https://doi.org/10.1037/0022-0663.93.1.187), Mayer, Heiser and Lonn, Journal of Educational Psychology, 2001, peer-reviewed, four experiments with college students (abstract read). On-screen text that summarised or duplicated narration over an animation lowered retention and transfer (redundancy effect). Scope: learning from explanations, not entertainment; it argues for short captions rather than full paragraphs.
- **Strength:** moderate. The sound-on share comes from Meta and TikTok without published methods; captions have strong lab support, but full duplicate text has a counter-finding.
- **Transfer to LumeBook:** record a clear Hebrew voice (parent or Yarin) or the child's real reaction audio; add short Hebrew captions synced to speech for the silent minority; keep text off the bottom UI area.
- **How to spot it in a Reel:** `audio_present` (yes/no), `audio_type` (speech to camera, voiceover, natural sound, music only, mixed), `captions_present`, `text_synced_to_speech` (text changes within 1 s of the line), `max_words_on_screen`, `text_area_share` (estimate of frame covered by text), `text_in_safe_zone`.

#### E5. Choose audio the account may use; treat trending audio as optional

- **Rule:** Music in a LumeBook Reel comes from Meta's Sound Collection or is original audio, and a trending sound is used only if it is available to the account, fits the moment and is still early in its trend.
- **Evidence:**
  - [Access to the licensed music library on Instagram](https://help.instagram.com/402084904469945), Instagram Help Center, undated live page (read 2026-10-18), platform-official. The licensed library is "intended for personal, non-commercial use"; certain business accounts and post types have no access; Meta's Sound Collection has over 14,000 royalty-free songs and sounds that may be used commercially.
  - Instagram creator FAQ (link in E1), platform-official. Says using trending audio can impact distribution because trend popularity is used when ranking content tied to that trend. No size of effect given.
  - Instagram Ranking Explained (link in E4), platform-official. One of the main Reels predictions is whether the viewer goes to the audio page, and the audio track is a ranking input.
  - [Finding success on reels in 2025](https://creators.instagram.com/blog/the-latest-with-instagram), Instagram for Creators, 21 January 2025, platform-official. Audio layering lets creators mix several tracks; each unique mix is attributed to the creator and others can save and remix it.
  - [Evaluating Empirical Research into Music in Advertising: A Congruity Perspective](https://doi.org/10.2501/s0021849907070055), Oakes, Journal of Advertising Research, 2007, peer-reviewed review (abstract read). Music that fits the ad (mood, tempo, genre, image) improves purchase intent, brand attitude, recall and affect. Scope: ads in general.
  - [Sprout Social Index 2025 release](https://www.cmswire.com/the-wire/sprout-social-research-reveals-consumers-think-jumping-on-viral-trends-is-embarrassing-for-brands/), Sprout Social via CMSWire, 7 January 2025, industry survey (4,044 consumers in the US, UK, Canada and Australia, September 2024). A third of consumers find brands jumping on trends embarrassing; 27% think trend participation only works within 24 to 48 hours.
- **Strength:** strong for the licensing constraint (official), weak for any reach gain from trending audio (official but unquantified), moderate for music fit.
- **Transfer to LumeBook:** check the account type before planning a trend recreation; if the track is not offered, use original voice or Sound Collection rather than a ripped track; pick music that matches the moment (warm for a gift reveal, playful for a funny kid moment).
- **How to spot it in a Reel:** `music_present`, `music_source` (licensed track named in the audio label, "Original audio", Sound Collection, unknown), `trend_audio` (yes/no, audio label used by many Reels), `music_fit` (mood matches action: yes/no), `voice_over_music` (speech audible above music).

#### E6. Look native, but technically clean

- **Rule:** The Reel looks like a phone video from a real home (direct to camera, natural light, real setting), yet is sharp, well lit, full-screen 9:16 and uploaded in high resolution, with no borders or letterboxing.
- **Evidence:**
  - Instagram creator FAQ (link in E1), platform-official. Says video quality matters, to upload the highest resolution possible, and that people engage more with high visual quality content.
  - Instagram Ranking Explained (link in E4), platform-official. Low-resolution and bordered Reels are made less visible.
  - Meta x Toluna study (link in E1), industry study. Native-feeling elements (emojis, direct-to-camera delivery, lower-fidelity production) outperformed heavily produced creative; emoji use was linked to a 2.5x uplift in purchase intent. Scope: paid ads, correlational, four markets.
  - [Is a Picture Worth a Thousand Words? An Empirical Study of Image Content and Social Media Engagement](https://doi.org/10.1177/0022243719881113), Li and Xie, Journal of Marketing Research, index record dated 2019, peer-reviewed, Twitter and Instagram posts about airlines and SUVs (abstract read). High-quality, professionally shot pictures had higher engagement on both platforms. Scope: still images, not video; it pulls against "lo-fi wins".
  - Unlock the power of Reel ads (link in E4), platform-official. Campaigns that follow Meta's creative essentials (9:16, audio, safe zone) got 2x higher delivery to the Reels placement (trend analysis of 4 million campaigns, March to May 2024). Scope: paid ads.
- **Strength:** contested. Instagram says technical quality matters; an ad study favours a native, lower-fidelity style; image research favours professional photos. The sources reconcile if "lo-fi" means style (phone, direct address, real home), not poor focus or light.
- **Transfer to LumeBook:** shoot on the phone at home in daylight, lens cleaned, export at 1080x1920, no studio look, no frames or black bars.
- **How to spot it in a Reel:** `aspect_full_9x16` (yes/no), `borders_present`, `sharpness_ok` (subject in focus in key frames), `lighting_ok`, `setting` (home, studio, outdoor, store), `direct_address` (person speaks to lens), `production_style` (phone native, semi-produced, studio).

#### E7. Every Reel is original: own footage, no foreign watermark, real added value

- **Rule:** The Reel is LumeBook's own footage (or a creator's, posted as a Collab), carries no other app's watermark, and if it recreates a trend it adds its own scene, voice or commentary.
- **Evidence:**
  - [Helping Creators Find New Audiences](https://creators.instagram.com/blog/recommendations-and-originality), Instagram for Creators, 30 April 2024, platform-official. When two or more identical pieces are found, only the original is recommended; accounts that repeatedly post others' content without materially enhancing it become ineligible for recommendations; eligible content must have "no visible watermarks"; memes, parodies, new voiceovers and reaction remixes count as material change. The same page lists clickbait, engagement bait and unoriginal content among things not recommended.
  - Instagram creator FAQ (link in E1), platform-official. Tells creators to remove third-party watermarks because they may be limiting reach, and to post original content for the best reach.
  - Instagram Ranking Explained (link in E4), platform-official. Watermarked Reels and Reels already posted on Instagram are made less visible.
  - [New Instagram Policies Target Reposted Content](https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/), PetaPixel, 30 April 2026, news report quoting a Mosseri video. If most of what an account posts is someone else's content, the account is "no longer going to be recommendable"; originality is judged across a month; the rule now covers photos and carousels, not only Reels; crediting, watermarks or minor crops do not count as original, remixing with your own words or commentary does.
  - Finding success on reels in 2025 (link in E5), platform-official. The Edits app exports without a watermark; trial reels let creators test editing styles on non-followers first.
- **Strength:** strong. Repeated, specific platform statements across 2023 to 2026.
- **Transfer to LumeBook:** export from CapCut only without its watermark, or edit in Instagram or Edits; repost creator videos through Collab or the repost button, never as a re-upload; trend recreations must use LumeBook's own child, book and Hebrew voice.
- **How to spot it in a Reel:** `foreign_watermark` (TikTok, CapCut or other logo visible), `reupload_suspected` (same video seen on another account), `collab_tag`, `trend_recreation` (yes/no), `added_value` (own footage, own voice, commentary, none).

#### E8. Stay under 3 minutes, end cleanly, and do not count on loops

- **Rule:** The Reel is under 3 minutes (ideally as short as the story allows), and ends on its payoff or call to action without a dead tail; a seamless loop is optional, not a target.
- **Evidence:**
  - Instagram creator FAQ (link in E1), platform-official. Instagram recommends videos of 3 minutes or less to people who do not follow the account.
  - Finding success on reels in 2025 (link in E5), platform-official. Reels up to 3 minutes became eligible for recommendation in January 2025; before, only reels up to 90 seconds were.
  - [Instagram Officially Expands Reels Length to 3 Minutes](https://www.socialmediatoday.com/news/instagram-officially-expands-reels-length-to-3-minutes/737766/), Social Media Today, 18 January 2025, news report quoting Mosseri's Threads post. Upload limit raised from 90 seconds to 3 minutes after creator feedback.
  - [What Is the Ideal Instagram Reels Length?](https://socialinsider.io/blog/instagram-reels-length/), Socialinsider, 14 July 2026, industry study (about 6 million brand Reels, January to June 2026; number of accounts and metric definitions not given). 45 to 60 s Reels had the highest engagement rate (0.35%) and median views (10,374); Reels over 180 s fell to 0.15% and 4,428 median views; 0 to 30 s had 0.28%. Correlational, content not controlled.
  - [What Drives Virality (Sharing) of Online Digital Content?](https://doi.org/10.1177/0022242919841034), Tellis, MacInnis, Tirunillai and Zhang, Journal of Marketing, 2019, peer-reviewed field studies of video ad sharing (abstract read). Sharing was greatest at moderate ad length, 1.2 to 1.7 minutes. Scope: brand video ads on general social platforms in the 2010s; weak transfer to Reels.
  - Instagram Ranking Explained (link in E4), platform-official. Predicts whether a viewer will "watch a reel all the way through", so completion matters.
  - [Instagram Media Insights reference](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/), Meta for Developers, live page (read 2026-10-18), platform-official. Total reel watch time includes time spent replaying. No source says loops are rewarded beyond that.
  - Dost and Huang 2026 (link in E2) measured intent to rewatch: overlapping cuts at low pace raised it. Weak, intentions only.
- **Strength:** strong for the 3-minute cap; weak for any best length; weak for loop endings (no direct evidence found).
- **Transfer to LumeBook:** most product Reels should fit 15 to 60 s; a reveal-to-reaction story rarely needs more; cut the last frame right after the payoff or CTA.
- **How to spot it in a Reel:** `duration_s`, `length_band` (0 to 15, 15 to 30, 30 to 60, 60 to 90, 90 to 180, over 180), `tail_after_payoff_s` (seconds after the last story beat), `end_type` (payoff, CTA card, logo card, loop to first frame, abrupt), `loop_seamless` (last frame matches first).

### Content topic

#### K1. Aim for a high-arousal positive feeling: surprise, joy, awe, warmth, amusement

- **Rule:** The Reel builds to one clear moment of surprise, delight, awe, warmth or laughter, and does not rest on sadness or calm information.
- **Evidence:**
  - [What Makes Online Content Viral?](https://jonahberger.com/wp-content/uploads/2013/02/ViralityB.pdf), Berger and Milkman, Journal of Marketing Research (ahead-of-print PDF, copyright 2011), DOI 10.1509/jmr.10.0353, peer-reviewed (full text read). Field study of 6,956 New York Times articles over three months plus experiments. Positive content was more viral; high-arousal emotions (awe, anger, anxiety) raised the chance of making the most-emailed list, low-arousal sadness lowered it. A one-SD rise in anger raised the odds by 34% and in awe by 30%. Practical usefulness, interest and surprise were also positively linked. In a lab study a more amusing ad story was more likely to be shared, driven by arousal. Scope: news articles and email sharing; the arousal mechanism transfers, the numbers do not.
  - What Drives Virality (Sharing) of Online Digital Content? (link in E8), Tellis et al., Journal of Marketing, 2019, peer-reviewed (abstract read). Amusement, excitement, inspiration and warmth raised sharing of video ads; drama elements (surprise, plot, characters including babies and animals) arouse emotion; informational content lowered sharing except in risky contexts.
  - Emotion-Induced Engagement in Internet Video Advertisements (link in E1), peer-reviewed. Joy and surprise held attention and reduced zapping.
  - [What Holds Attention? Linguistic Drivers of Engagement](https://doi.org/10.1177/00222429231152880), Berger, Moe and Schweidel, Journal of Marketing, 2023, peer-reviewed (600,000 reading sessions across 35,000+ pieces of content plus experiments; abstract read). Anxious, exciting and hopeful language held attention, sad language discouraged it; easy, concrete words also helped. Scope: written content; supports simple Hebrew and hopeful framing in speech and captions.
- **Strength:** strong. Large field data and experiments in top journals point the same way, though none measured Instagram Reels.
- **Transfer to LumeBook:** the core emotional asset is the child's surprise at seeing their own name and face in a story, and a grandparent's warmth; tears are fine when they are happy tears.
- **How to spot it in a Reel:** `peak_emotion` (surprise, joy, awe, warmth, amusement, sadness, none), `peak_time_s`, `emotion_valence` (positive, negative, mixed), `arousal_level` (high, medium, low, judged from faces, voice and music).

#### K2. Tell a mini story: a character, a want, a turn, a payoff

- **Rule:** The Reel has a recognisable character (child, parent, grandparent), a setup, a turn or reveal, and a payoff, rather than a list of product features.
- **Evidence:**
  - [The role of transportation in the persuasiveness of public narratives](https://doi.org/10.1037/0022-3514.79.5.701), Green and Brock, Journal of Personality and Social Psychology, 2000, peer-reviewed, four experiments (N = 97, 69, 274, 258; abstract read). Being absorbed in a story ("transportation") raised story-consistent beliefs and liking of characters; transported readers found fewer false notes; labelling a story fact or fiction made little difference.
  - [The Extended Transportation-Imagery Model: A Meta-Analysis of the Antecedents and Consequences of Consumers' Narrative Transportation](https://doi.org/10.1086/673383), van Laer, de Ruyter, Visconti and Wetzels, Journal of Consumer Research, index record dated 2013, peer-reviewed meta-analysis of 132 effect sizes from 76 articles (abstract read). Systematises what makes people enter a story world and the persuasion that follows.
  - [Why Narrative Ads Work: An Integrated Process Explanation](https://doi.org/10.1080/00913367.2016.1268984), Kim, Ratneshwar and Thorson, Journal of Advertising, 2017, peer-reviewed (25 narrative and 25 non-narrative TV ads, 484 non-student participants; abstract read). Narrative ads were more persuasive, through emotional response, hedonic value, credibility and a sense the product helps reach a goal. Scope: TV ads.
  - [Self-Referencing and Persuasion: Narrative Transportation versus Analytical Elaboration](https://doi.org/10.1086/510216), Escalas, Journal of Consumer Research, 2007, peer-reviewed, two experiments (abstract read). When viewers imagine themselves in a story, weak arguments hurt persuasion less; ad scepticism moderates the effect. Scope: ads.
  - Tellis et al. 2019 (link in E8): plot and characters are among the drama elements that drive sharing.
- **Strength:** strong for narrative persuasion in ads; moderate for transfer to 15 to 60 s Reels, which leave little room for a long arc.
- **Transfer to LumeBook:** "the child does not believe the book is about them, then finds their name, then reads it to grandma" is a full arc in 20 seconds; problem-solution framing fits here (a bedtime struggle, then the book that the child asks for every night). No peer-reviewed source on problem-solution format in short video specifically was found.
- **How to spot it in a Reel:** `character` (child, parent, grandparent, expert, none), `arc_beats` (setup, turn, payoff present: count 0 to 3), `reveal_moment_s`, `format` (story, demo, list, tutorial, talking head opinion, trend recreation).

#### K3. Use relatable, everyday humour

- **Rule:** When the Reel is funny, the joke comes from a recognisable parenting or kid moment the viewer has lived, not from a gag unrelated to family life.
- **Evidence:**
  - Instagram creator FAQ (link in E1), platform-official. Advises making content relatable: "humorous content that people can relate to typically results in more engagement and reshares".
  - [A meta-analysis of humor in advertising](https://doi.org/10.1007/s11747-008-0096-y), Eisend, Journal of the Academy of Marketing Science, 2009 (online 2008), peer-reviewed meta-analysis of 369 correlations (abstract read on publisher page). Humour raised attention, positive affect, ad liking, brand attitude and purchase intention, and lowered source credibility.
  - [Advertising Content and Consumer Engagement on Social Media: Evidence from Facebook](https://doi.org/10.1287/mnsc.2017.2902), Lee, Hosanagar and Nair, Management Science, index record dated 2017, peer-reviewed (106,316 Facebook messages from 782 companies; abstract read on publisher page). Brand-personality content such as humour and emotion was associated with more likes, comments and shares. Scope: Facebook brand posts, mostly text and images.
  - Berger and Milkman (link in K1), Study 2a: a high-amusement version of an ad story was more likely to be shared than a low-amusement version.
- **Strength:** strong. Platform statement plus a meta-analysis and a large field study.
- **Transfer to LumeBook:** funny kid reactions, sibling jealousy over who got a book, a parent's honest bedtime chaos; keep the developmental or expert line serious, since humour lowers credibility.
- **How to spot it in a Reel:** `humour_present`, `humour_source` (child behaviour, parent struggle, sibling, wordplay, unrelated gag), `relatable_parenting_moment` (yes/no), `expert_claim_in_joke` (a factual claim delivered as a joke).

#### K4. Give practical value, but wrap it in emotion or personality

- **Rule:** Any useful tip or fact (reading at bedtime, why seeing their own name helps a child) is delivered inside a feeling, a story or a laugh, and any developmental claim is modest and checkable.
- **Evidence:**
  - Berger and Milkman (link in K1): practically useful articles were more likely to be emailed.
  - Tellis et al. 2019 (link in E8): information-focused video ads were shared significantly less, except in risky contexts.
  - Lee, Hosanagar and Nair 2017 (link in K3): directly informative content (price, deals) alone was associated with lower engagement, but with higher engagement when combined with humour or emotion; deals and promotions drove click-throughs.
  - [Valuable Virality](https://doi.org/10.1509/jmr.13.0350), Akpinar and Berger, Journal of Marketing Research, index record dated 2016, peer-reviewed (share data from hundreds of online ads plus lab experiments; abstract read). Emotional appeals were shared more; informative appeals improved brand evaluation and purchase; emotional ads in which the brand is integral did both.
  - [Reading personalized books with preschool children enhances their word acquisition](https://doi.org/10.1177/0142723714534221), Kucirkova, Messer and Sheehy, First Language, 2014, peer-reviewed, 18 children with mean age 3 years 10 months (abstract read). Children knew new words better from the personalised sections of a book than from the non-personalised sections. Small sample; supports a careful claim, not a big one.
  - Helping Creators Find New Audiences (link in E7), platform-official. Exaggerated health claims are on the list of content not recommended.
- **Strength:** contested in isolation (usefulness helps email sharing but hurts video-ad sharing), consistent when combined (information plus emotion beats either alone).
- **Transfer to LumeBook:** a parent tip like "kids ask for the book with their name again and again" works when shown through a real child asking; avoid claims like "boosts IQ".
- **How to spot it in a Reel:** `info_units` (count of distinct facts or tips in speech and text), `info_with_emotion` (info delivered alongside a reaction, story or joke: yes/no), `price_or_deal_mentioned`, `developmental_claim` (text of the claim), `claim_strength` (modest, strong, medical-sounding).

#### K5. Make the product part of the story; keep brand talk short

- **Rule:** The book is shown in use as part of the action (being opened, read, given), and explicit brand messaging (logo, name, offer) takes no more than about a quarter of the running time.
- **Evidence:**
  - Valuable Virality (link in K4): emotional ads with the brand integral to the content boost both sharing and brand outcomes.
  - [Why, When, and How Much to Entertain Consumers in Advertisements? A Web-Based Facial Tracking Field Study](https://doi.org/10.1287/mksc.2014.0854), Teixeira, Picard and el Kaliouby, Marketing Science, 2014, peer-reviewed (82 ads shown to 178 consumers at home and work; abstract read). Entertainment had an inverted-U link to purchase intent; entertainment after the brand appeared was positively associated with purchase intent, entertainment before it was not. Scope: TV ads viewed online.
  - Tellis et al. 2019 (link in E8): prominent brand placement (early, long, persistent) hurt sharing.
  - Meta x Toluna study (link in E1), industry study: brand and core message in the first 5 s made strong purchase intent 1.7x more likely; dynamic, repeated branding beat a single end-frame logo (1.8x); for conversion-focused ads, branding under about 25% of duration performed better.
  - Instagram creator FAQ (link in E1), platform-official. Content that promotes a contest or giveaway is listed among content not recommended to non-followers.
- **Strength:** contested. Sharing studies penalise early, heavy branding; purchase-intent studies reward an early brand and message. Showing the product early as part of the story, with little brand talk, satisfies both.
- **Transfer to LumeBook:** the personalised book is the visible product from the first seconds, but "לומבוק" and the offer appear briefly (caption, last beat, Collab tag); giveaway Reels will mostly reach existing followers only.
- **How to spot it in a Reel:** `product_first_s` (first time the book is on screen), `product_in_use` (opened, read, given: yes/no), `brand_mentions` (count of spoken or written brand name and logo), `brand_share_duration` (seconds with logo or brand text divided by duration), `giveaway` (yes/no), `cta_type`.

#### K6. Speak to a real parenting concern or make parents feel "not alone"

- **Rule:** The Reel connects to something parents of 1 to 8 year olds actually deal with (bedtime, routines, emotions, a new sibling, starting kindergarten, reading) and leaves the viewer feeling understood or helped, without hype.
- **Evidence:**
  - [Parents and Social Media](https://www.pewresearch.org/internet/2015/07/16/parents-and-social-media/), Pew Research Center, 16 July 2015, survey (2,003 US adults, September 2014). Of social-media-using parents, 59% came across useful parenting information on social media in the past 30 days (mothers 66%, fathers 48%) and 42% got social or emotional support on a parenting issue. Old and US-only.
  - [Parents on social media: Likes and dislikes of sharenting](https://mottpoll.org/reports-surveys/parents-social-media-likes-and-dislikes-sharenting), C.S. Mott Children's Hospital National Poll on Children's Health, 16 March 2015, survey (569 US parents of children aged 0 to 4). 56% of mothers and 34% of fathers discuss parenting on social media; most-discussed topics were sleep (28%), nutrition (26%), discipline (19%), daycare or preschool (17%); valued benefits were feeling not alone (72%), learning what not to do (70%) and worrying less (62%).
  - [Parents' attitudes and experiences related to digital technology](https://www.pewresearch.org/internet/2020/07/28/parents-attitudes-and-experiences-related-to-digital-technology/), Pew Research Center, 28 July 2020, survey (3,640 US parents, March 2020; see also the [report overview](https://www.pewresearch.org/internet/2020/07/28/parenting-children-in-the-age-of-screens/)). For screen-time advice, parents of a child aged 11 or younger turned to doctors (61%) and other parents (55%) more than social media (29% of social-media users). Social media is a source, not the main authority.
  - [The Use of Social Media as a Mechanism of Social Support in Parents](https://doi.org/10.1007/s10826-017-0716-6), Haslam, Tee and Baker, Journal of Child and Family Studies, 2017, peer-reviewed survey of 523 Australian parents (abstract read). Getting specific information and advice were the top reasons parents used social media for parenting; more use went with more perceived online support.
  - [Consumed by influence: the role of social media in shaping maternal identity and product choices during complementary feeding](https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2025.1730534/full), Ozturk and Kaya, Frontiers in Communication, 19 December 2025, peer-reviewed mixed-methods survey (711 mothers in Turkey, children 6 to 48 months, recruited through social media). Most respondents gave negative evaluations of influencer-recommended purchases (80.8%; denominator not clearly stated), often doubting the product was necessary. Supports avoiding hype.
  - [Forums for Parents of Young Children: Parents' Online Conversations in Israel and France](https://doi.org/10.54195/ijpe.18228), Chen, Aram and Tannenbaum, International Journal about Parents in Education, 2023, peer-reviewed content analysis of 3,244 posts in four forums (abstract read). Israeli parents discussed social-emotional development and parenting issues more than French parents, who discussed cognitive and developmental issues more; both focused on educational settings.
  - [Digital 2026: Israel](https://datareportal.com/reports/digital-2026-israel), DataReportal (Kepios, Simon Kemp), 8 November 2025, industry data from platform ad tools. Instagram ad reach in Israel was 5.00 million, 74.0% of adults 18+, 54.2% female; Facebook 77.1% of adults; TikTok 69.2% of adults (56.0% male). Ad reach is not active users.
- **Strength:** moderate. Several surveys agree that parents seek information and reassurance online, but most are US, several are a decade old, and none isolates Instagram Reels.
- **Transfer to LumeBook:** frame Reels around social-emotional moments that Israeli parents talk about (a new sibling, first day at the gan, confidence, bedtime) and show the book as a small, honest help; the viewer is most likely an Israeli woman on Instagram.
- **How to spot it in a Reel:** `parent_concern` (sleep, routines, emotions, sibling, kindergarten, reading, screen time, none), `reassurance_line` (a "you're not alone" or "us too" moment: yes/no), `hype_words` (miracle, must-have, guaranteed), `speaker_role` (parent, expert, child, brand).

#### K7. Tie the Reel to a buying moment and to the person who buys

- **Rule:** The Reel names or shows a gifting or life moment (birthday, new sibling, holiday, first day of kindergarten, grandparent visit) and makes clear who would buy it (parent or grandparent).
- **Evidence:**
  - [Life Status Changes and Changes in Consumer Preferences and Satisfaction](https://doi.org/10.1086/209014), Andreasen, Journal of Consumer Research, 1984, peer-reviewed cross-sectional survey in one US metropolitan area (abstract read). Households going through a life status change were more likely to change brand preferences and more open to new influences.
  - [International Kids Gifting Behaviours (Giraffe Insights)](https://toyworldmag.co.uk/?p=192007), Toy World Magazine, 17 June 2021, industry study (2,441 people who had given a child a gift in the past 12 months, eight markets: UK, US, Netherlands, France, Spain, Italy, Germany, Belgium; March 2021). Grandparents made up 27% of kids' gift purchases; top gifting motives were to show love (39%) and to entertain (34%); 28% of grandparents valued creating memorable moments. No Israel data.
  - [Grandparents Embrace Changing Attitudes and Technology (2018 AARP Grandparenting Study)](https://www.aarp.org/research/topics/life/info-2019/aarp-grandparenting-study.html), AARP Research, 2018 (page updated 15 August 2024), survey (2,654 US grandparents aged 38+). Grandparents spend about $179 billion a year on grandchildren; over half have a grandchild living more than 200 miles away. US only.
  - [How Instagram Boosts Brands and Drives Sales](https://www.facebook.com/business/news/insights/how-instagram-boosts-brands-and-drives-sales), Facebook IQ, 6 February 2019, platform-commissioned survey (Ipsos, 21,000 weekly Instagram users in 13 countries, November 2018; Israel not included). 54% said they made a purchase after seeing a product or service on Instagram; 79% searched for more information.
- **Strength:** weak to moderate. The life-change mechanism is peer-reviewed but old; gifting numbers are industry surveys outside Israel; no study on birthdays or milestones as triggers for children's books was found.
- **Transfer to LumeBook:** build calendar Reels around birthdays, a new sibling, Rosh Hashana, Hanukkah and the start of the school year, and make some Reels for grandparents (the gift moment, a grandchild far away).
- **How to spot it in a Reel:** `occasion` (birthday, new sibling, holiday name, kindergarten start, grandparent visit, none), `buyer_shown` (parent, grandparent, other relative, none), `gift_moment` (wrapping, giving, unwrapping: yes/no), `occasion_in_caption`.

#### K8. Put a real face, ideally the child's reaction, on screen

- **Rule:** A real person's face is visible for most of the Reel, with the child's reaction as the emotional centre, and a parent speaking to camera when there is talking.
- **Evidence:**
  - [Faces engage us: Photos with faces attract more likes and comments on Instagram](https://doi.org/10.1145/2556288.2557403), Bakhshi, Shamma and Gilbert, CHI 2014, peer-reviewed (1 million Instagram photos; abstract read). Photos with faces were 38% more likely to get likes and 32% more likely to get comments; number, age and gender of faces had no effect. Scope: photos, not video.
  - Li and Xie 2019 (link in E6), peer-reviewed. Face presence raised engagement on Twitter but not on Instagram. Scope: airline and SUV brand images.
  - Tellis et al. 2019 (link in E8): babies, animals and characters arouse emotions that drive sharing; ads used celebrities more than babies or animals.
  - Meta x Toluna study (link in E1), industry study: direct-to-camera delivery was among the native elements linked to stronger performance.
  - [Slapping Cats, Bopping Heads, and Oreo Shakes: Understanding Indicators of Virality in TikTok Short Videos](https://arxiv.org/abs/2111.02452), Ling, Blackburn, De Cristofaro and Stringhini, ACM Web Science Conference 2022 (arXiv preprint 2021), peer-reviewed conference paper (400 labelled TikTok videos; abstract read). Creator follower count was the strongest predictor of virality; shot scale (close-up and medium shots), on-screen text and point of view also mattered. Direction per feature is not given in the abstract.
- **Strength:** contested. Faces help on Instagram photos in one large study and not in another; for video the support is indirect.
- **Transfer to LumeBook:** frame close-ups or medium shots of the child's face at the reveal; when someone speaks, they look at the lens.
- **How to spot it in a Reel:** `face_screen_share` (share of sampled frames with a face), `child_face_at_peak` (yes/no), `shot_scale_at_peak` (close-up, medium, wide), `direct_address` (yes/no).

---

## 3. Myths and contested claims

| Claim | What I found when tracing it | Verdict |
|---|---|---|
| "People have an 8-second attention span, shorter than a goldfish" | The figure appeared in a 2015 Microsoft Canada report, credited to Statistic Brain, not to Microsoft's own research. A UX Psychology review (Panagiotidi, 2021) reports that a BBC journalist could not get Statistic Brain to support it and that no one has measured a goldfish attention span. I could not open the BBC article (blocked) and the WARC article body did not load. | Myth. Do not cite. Attention depends on task and motivation (see Lang's work), not a fixed span. |
| "85% of video is watched without sound" | Digiday (17 May 2016) attributed it to a few publishers' self-reported Facebook figures (LittleThings, Mic; PopSugar said 50 to 80%), with no method. Facebook did not supply it. | Outdated for Reels. Meta now says over 75% of Instagram Reels views are sound-on (also without a method). Design for sound, caption for the rest. |
| "65% of people who watch the first 3 seconds watch 10 seconds" (attributed to Facebook) | Every result was secondhand; the earliest page (a Salesforce blog, 2016) returned 404 when opened. No Facebook original found. | Untraced. Do not cite. Instagram's own advice on the first 3 seconds is qualitative. |
| "Trending audio boosts reach by X%" | Instagram says trending audio can affect distribution and gives no number. Business accounts often cannot use licensed trending tracks at all. | No number exists from the platform. Treat as optional. |
| "Faster cuts always hold attention better" | Lang et al. (1999): fast pace plus arousing content overloads and lowers recall. Dost and Huang (2026): higher pacing reduced intent to keep watching. Lang et al. (2000): faster edits within one scene raised memory. | Contested. Faster helps up to a point and within one scene; it hurts on emotional or dense content. |
| "Lo-fi always beats polished" | Meta x Toluna: native, lower-fidelity ads did better (correlational, paid ads). Instagram FAQ: video quality matters, upload highest resolution. Li and Xie: professional photos got more engagement. | Contested. Native style yes, poor technical quality no. |
| "Reels over 90 seconds are not recommended" | True until January 2025. Instagram now recommends Reels of 3 minutes or less to non-followers. | Outdated. The cap is 3 minutes. |
| "Instagram suppresses Reels with TikTok or CapCut watermarks" | Confirmed by Instagram's ranking page, creator FAQ and the April 2024 originality post. | True, not a myth. |
| "Sad, tear-jerking content goes viral" | Berger and Milkman: sadness was negatively linked to sharing. Tellis et al.: warmth and inspiration raised sharing. | Mostly myth. Warm or moving with a positive turn, yes; sad alone, no. |
| "Sends (DM shares) are the number one ranking signal" (Mosseri, 2025) | Only marketing blogs repeated it in search results; I did not open a primary Mosseri source. Instagram's own ranking page lists reshare likelihood first among the main predictions, alongside full watches, likes and audio-page visits. | Unverified ordering. Safe statement: shares and completion both matter. |
| "Post 10+ Reels a month to grow" | Instagram's FAQ says creators with the fastest follower growth post 10 or more a month on average, and calls frequency one factor of many. | Correlation reported by the platform, not a causal rule. |
| "Facebook is now a network for older people in Israel" | Maariv (26 October 2025) headline and an interviewee's remark; no figures in the article. DataReportal shows Facebook ad reach of 77.1% of Israeli adults, without an age breakdown. | Unsupported by data I could open. |
| "92% of social-media moms buy products recommended on social media" | Seen only as a search result about a 2012 PR-firm panel of self-selected moms; not opened. | Not used. Panel is self-selected. |

---

## 4. Sources (all accessed 2026-10-18)

Platform-official:
- https://about.instagram.com/blog/announcements/instagram-ranking-explained : Instagram, Instagram Ranking Explained, 31 May 2023 (read in WebFetch and in a browser).
- https://creators.instagram.com/blog/recommendations-and-originality : Instagram for Creators, Helping Creators Find New Audiences, 30 April 2024.
- https://creators.instagram.com/faq?locale=en_US : Instagram for Creators, FAQ, undated live page (read in a browser).
- https://creators.instagram.com/blog/the-latest-with-instagram : Instagram for Creators, Finding success on reels in 2025, 21 January 2025.
- https://creators.instagram.com/blog/tips-for-improving-your-reach : Instagram for Creators, Tips for Improving Your Reach, 31 May 2023.
- https://creators.instagram.com/create-engaging-content : Instagram for Creators, Create Engaging Content (opened; its tabbed sections did not expand, nothing cited).
- https://help.instagram.com/402084904469945 : Instagram Help Center, Access to the licensed music library on Instagram (read in a browser).
- https://help.instagram.com/ipad-app/402084904469945 and https://www.facebook.com/help/instagram/402084904469945 : same help article, body did not render in WebFetch.
- https://developers.facebook.com/blog/post/2024/11/07/unlock-the-power-of-reel-ads/ : Meta for Developers, Unlock the power of Reel ads, 7 November 2024.
- https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/ : Meta for Developers, Instagram Media Insights reference.
- https://www.facebook.com/business/news/insights/capturing-attention-feed-video-creative : Facebook IQ, Capturing Attention in Feed, 20 April 2016.
- https://www.facebook.com/business/news/insights/how-instagram-boosts-brands-and-drives-sales : Facebook IQ, How Instagram Boosts Brands and Drives Sales, 6 February 2019.
- https://ads.tiktok.com/business/en/blog/kantar-report-how-brands-are-making-noise-and-driving-impact-with-sound-on-tiktok : TikTok for Business, Kantar sound report, 8 June 2021.

Peer-reviewed (abstract read unless noted):
- https://jonahberger.com/wp-content/uploads/2013/02/ViralityB.pdf : Berger and Milkman, What Makes Online Content Viral?, Journal of Marketing Research (ahead of print 2011), DOI 10.1509/jmr.10.0353 (full text read).
- https://doi.org/10.1207/s15506878jobem4401_7 : Lang et al. 2000, edits and memory, Journal of Broadcasting and Electronic Media (abstract via api.openalex.org; Semantic Scholar and Taylor and Francis pages returned no abstract).
- https://doi.org/10.1111/j.1460-2466.2000.tb02833.x : Lang 2000, The Limited Capacity Model of Mediated Message Processing, Journal of Communication (abstract via OpenAlex; general model, not cited for a specific finding).
- https://doi.org/10.1080/08838159909364504 : Lang, Bolls, Potter and Kawahara 1999, pacing and arousing content (via OpenAlex).
- https://doi.org/10.1177/009365093020001001 : Lang, Geiger, Strickwerda and Sumner 1993, related and unrelated cuts (via OpenAlex).
- https://doi.org/10.1177/009365090017003001 : Lang 1990, involuntary attention to structural features (via OpenAlex).
- https://doi.org/10.1086/673383 : van Laer et al. 2013, narrative transportation meta-analysis (via OpenAlex).
- https://doi.org/10.1037/0022-3514.79.5.701 : Green and Brock 2000, transportation (via OpenAlex).
- https://doi.org/10.1177/0022242919841034 : Tellis et al. 2019, what drives virality of video ads (via OpenAlex).
- https://doi.org/10.1509/jmr.10.0207 : Teixeira, Wedel and Pieters 2011, emotion-induced engagement (via OpenAlex).
- https://doi.org/10.1287/mksc.2014.0854 : Teixeira, Picard and el Kaliouby 2014, how much to entertain (via OpenAlex).
- https://pubsonline.informs.org/doi/10.1287/mnsc.2017.2902 : Lee, Hosanagar and Nair 2017, Facebook ad content and engagement (abstract read in a browser; SSRN and Stanford pages failed).
- https://link.springer.com/article/10.1007/s11747-008-0096-y : Eisend 2009, humour meta-analysis (publisher page).
- https://doi.org/10.1509/jmr.13.0350 : Akpinar and Berger 2016, Valuable Virality (via OpenAlex).
- https://doi.org/10.1177/00222437231179187 : Stuppy, Landwehr and McGraw 2024, slow motion (via OpenAlex).
- https://doi.org/10.1177/00222437211025054 : Yin, Jia and Zheng 2021, slow motion backfire (via OpenAlex).
- https://doi.org/10.1177/00222429231152880 : Berger, Moe and Schweidel 2023, what holds attention (via OpenAlex).
- https://doi.org/10.1509/jm.16.0048 : Liu, Shi, Teixeira and Wedel 2018, Video Content Marketing: The Making of Clips (via OpenAlex; read, not cited: about cutting trailers into clips).
- https://doi.org/10.1086/510216 : Escalas 2007, self-referencing and narrative transportation (via OpenAlex).
- https://doi.org/10.1080/00913367.2016.1268984 : Kim, Ratneshwar and Thorson 2017, why narrative ads work (via OpenAlex).
- https://doi.org/10.2501/s0021849907070055 : Oakes 2007, music congruity review (via OpenAlex).
- https://doi.org/10.1177/2372732215602130 : Gernsbacher 2015, captions (via OpenAlex).
- https://doi.org/10.1037/0022-0663.93.1.187 : Mayer, Heiser and Lonn 2001, redundancy effect (via OpenAlex).
- https://doi.org/10.1145/2556288.2557403 : Bakhshi, Shamma and Gilbert 2014, faces on Instagram (via OpenAlex).
- https://doi.org/10.1177/0022243719881113 : Li and Xie 2019, image content and engagement (via OpenAlex).
- https://doi.org/10.1016/j.intmar.2012.01.003 : de Vries, Gensler and Leeflang 2012, brand post popularity (via OpenAlex; read, not cited).
- https://doi.org/10.1177/0022242919854374 : Hughes, Swaminathan and Brooks 2019, sponsored blogging (via OpenAlex; read, not cited).
- https://doi.org/10.1086/209014 : Andreasen 1984, life status changes (via OpenAlex).
- https://doi.org/10.1177/0142723714534221 : Kucirkova, Messer and Sheehy 2014, personalised books and word learning (via OpenAlex).
- https://doi.org/10.1016/j.pragma.2014.07.007 : Kucirkova, Messer and Sheehy 2014, Journal of Pragmatics (OpenAlex record had no abstract; not cited).
- https://link.springer.com/article/10.1007/s10826-017-0716-6 : Haslam, Tee and Baker 2017, social media as parenting support (abstract read in a browser).
- https://doi.org/10.2196/19985 : Kubb and Foran 2020, parents' online health information seeking review, JMIR (via OpenAlex; read, not cited).
- https://doi.org/10.54195/ijpe.18228 : Chen, Aram and Tannenbaum 2023, Israeli and French parent forums (via OpenAlex).
- https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2025.1730534/full : Ozturk and Kaya 2025, mothers and influencer product choices.
- https://arxiv.org/abs/2111.02452 and https://export.arxiv.org/api/query?search_query=ti:%22Slapping%20Cats%22&max_results=3 : Ling et al., TikTok virality indicators (WebSci 2022 per OpenAlex record https://doi.org/10.1145/3501247.3531551).
- https://archives.marketing-trends-congress.com/2026/pages/PDF/paper_professor_DOST_HUANG.pdf : Dost and Huang 2026, jump cuts and transition frequency (conference paper, full text read).
- https://api.semanticscholar.org/graph/v1/paper/DOI:10.1207/s15506878jobem4401_7 and https://api.semanticscholar.org/graph/v1/paper/DOI:10.1111/j.1460-2466.2000.tb02833.x : Semantic Scholar records, abstracts withheld by publisher.
- https://api.openalex.org/works : OpenAlex index used to read abstracts and find DOIs for the papers above.

Industry studies and surveys:
- https://datareportal.com/reports/digital-2026-israel : DataReportal, Digital 2026: Israel, 8 November 2025.
- https://www.pewresearch.org/internet/2015/07/16/parents-and-social-media/ : Pew Research Center, Parents and Social Media, 16 July 2015.
- https://www.pewresearch.org/internet/2020/07/28/parenting-children-in-the-age-of-screens/ : Pew Research Center, Parenting Children in the Age of Screens, 28 July 2020.
- https://www.pewresearch.org/internet/2020/07/28/parents-attitudes-and-experiences-related-to-digital-technology/ : Pew Research Center, chapter on parents' sources of screen-time advice, 28 July 2020.
- https://mottpoll.org/reports-surveys/parents-social-media-likes-and-dislikes-sharenting : C.S. Mott Children's Hospital National Poll, 16 March 2015.
- https://www.aarp.org/research/topics/life/info-2019/aarp-grandparenting-study.html : AARP Research, 2018 Grandparenting Study.
- https://tolunacorporate.com/what-makes-short-form-video-ads-work-meta-toluna-study/ : Toluna, Meta x Toluna short-form video ad study, 4 August 2026.
- https://socialinsider.io/blog/instagram-reels-length/ : Socialinsider, Reels length benchmarks, 14 July 2026.
- https://www.cmswire.com/the-wire/sprout-social-research-reveals-consumers-think-jumping-on-viral-trends-is-embarrassing-for-brands/ : Sprout Social Index 2025 press release, 7 January 2025.
- https://toyworldmag.co.uk/?p=192007 : Toy World Magazine on Giraffe Insights kids gifting study, 17 June 2021.

News reports and practitioner pages:
- https://www.socialmediatoday.com/news/instagram-officially-expands-reels-length-to-3-minutes/737766/ : Social Media Today, 18 January 2025.
- https://www.gigazine.net/gsc_news/en/20240502-instagram-updated-algorithm-prioritizes-original-content : Gigazine, 2 May 2024 (led to the Instagram primary post).
- https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/ : PetaPixel, 30 April 2026 (WebFetch 403; read in a browser).
- https://onlinemarketing.de/social-media-marketing/instagrams-how-to-build-effective-reels-ads-leitfaden : OnlineMarketing.de, 12 September 2022.
- https://digiday.com/media/silent-world-facebook-video/ : Digiday, 17 May 2016.
- https://uxpsychology.substack.com/p/the-attention-span-myth : UX Psychology (Panagiotidi), 20 October 2021, practitioner.
- https://www.warc.com/newsandopinion/opinion/the_goldfish_myth/2806 : WARC opinion, 30 August 2018 (only title and byline loaded).
- https://www.maariv.co.il/economy/tech/article-1245210 : Maariv, 26 October 2025 (no data in article).
- https://www.bizportal.co.il/advertismentandmarketing/news/article/658814 : Bizportal on the Bezeq Internet Report, 27 November 2017 (1,268 respondents with TNS; teen Instagram 72% versus Facebook 63%; 80% shop online). Too old to use as current evidence.

Attempted, not readable (not cited):
- https://transparency.meta.com/features/explaining-ranking/ig-reels/ (404)
- https://about.instagram.com/blog/announcements/introducing-edits-a-new-video-creation-app (404)
- https://www.facebook.com/business/ads/reels-ads (404)
- https://salesforce.com/content/blogs/us/en/2016/02/facebook-video-ads-global.html (404)
- https://www.bbc.com/news/health-38896790 (blocked)
- https://www.tandfonline.com/doi/abs/10.1207/s15506878jobem4401_7 (403)
- https://academic.oup.com/joc/article-abstract/50/1/46/4110105 (served a different article)
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2290802 (403)
- https://www.gsb.stanford.edu/faculty-research/working-papers/advertising-content-consumer-engagement-social-media-evidence-facebook (404)

Gaps: no Hebrew-language or Israel-specific study on Reel editing, no Israeli survey on parents' Instagram use or children's book gifting, no Israel Internet Association or Bezeq 2025 figures could be opened, and no peer-reviewed study on loop endings, transitions effects or problem-solution framing in short video was found.
