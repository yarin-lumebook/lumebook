# Sources

Every source behind `report.md` and `tools-compared.md`, with the date it was read, what it was used for and how far to trust it.

**Labels**
- **verified**: the page was opened and says this. For law, "verified" means the text of an unofficial copy says this, not that a court reads it that way.
- **vendor claim**: a company says it about its own product or its market, including its own surveys and benchmark reports.
- **law-firm summary**: a law firm's reading of the law. Treat it like a vendor claim about the law.
- **inference**: my reading. Inferences live in the report, not in this list.

**Read by**
- **lead**: read by the session that wrote the report.
- **assistant**: read by one of three research assistants working inside the same session, each with a fixed source list and search cap. Their full notes were in the session's scratch folder and are not kept.
- **checked**: an assistant's source that the lead opened again on 19 Oct 2026 and found to say what the notes said.

All web pages were read on **19 Oct 2026** unless a row says otherwise. Meta's help pages render with JavaScript; they were read as text in the app's built-in browser pane, with no sign-in.

---

## Internal sources (this repository and its live data)

| Source | Used for |
|---|---|
| `creators/creator-research/src/template.html` | Statuses, follow-up timing, storage, messages, voice learning, tests, saving (report section 2) |
| `creators/creator-research/src/build2.py`, `enrich.py` | How the page is built, offer facts, exclusions |
| `creators/creator-research/src/refresh/README.md`, `refresh.py` | The weekly refresh |
| `creators/creator-research/src/C_all.json`, `kids.json`, `contacts.json` | Field lists and counts (no personal data copied into the report) |
| `creators/creator-research/src/README.md` | Data files and research passes |
| `creators/creator-research/creators-200-2026-10-03.csv` | The CSV the dashboard reads; empty status columns |
| Live export of the creator map's `outreach` collection (261 documents, read only through `ArtifactData`, 19 Oct 2026) | Pipeline counts in section 2.8. Kept only in the session's scratch folder |
| The dashboard's `tracker/state` document (read only, 19 Oct 2026) | `creators: {}`, `outreach: 0` |
| Scheduled task list (read only, 19 Oct 2026) | The refresh task is enabled and has not run |
| Built map at 375 px in the built-in browser (static copy, no data, 19 Oct 2026) | Card height, buttons, no sideways scroll |
| Artifact runtime type definitions, `db.d.ts`, contract 0.2.85 (bundled with Claude Code) | 256 KiB per document, 64 subscriptions per view, unstated caps, error codes |
| `shared/facts.json` | Offer, key dates (Hanukkah creator books 10 Nov), paid-hold list |
| `shared/design/lumebook.css`, `shared/design/categories.json` | Components and the `creator-tracks` category set |
| `research/creator-content-conversion/report.md` (lines 13, 15, 514 to 519, 549, 557 to 564) and `evidence.md:133` | What the store already tracks; buying signals by creator type; disclosure habits |
| `research/organic-content-conversion-notes-2026-10-14.md` | Limits of UTM tags |
| `docs/lumebook-sales-data-decisions-2026-10-12.md` (lines 37, 133) | The request to Yossi; the store's post-purchase WhatsApp message |
| `docs/lumebook-product-brief.md` | Price ₪119, home shipping ₪30 (as of 1 Oct 2026) |
| `docs/lumebook-ugc-ambassador-research.md` | Earlier consent and rights recommendations |
| `research/israeli-product-reels/creator-brief.md` (lines 35, 37 to 41, 208) | Raw footage, consent, disclosure line in the brief |
| `sites/dashboard/board/README.md` | Where the dashboard saves; the 256 KiB note |
| Memory index and entries on the creator offer, creator research, kids info, card simplicity | Context and Yarin's earlier decisions |

---

## Gifting, seeding and ambassador programmes

| ID | Source | URL | Used for | Label | Read by |
|---|---|---|---|---|---|
| G1 | Modash, creator gifting survey (12 Jun 2026; 25 creator interviews plus a creator poll of unstated size) | https://www.modash.io/blog/creator-gifting-survey | Post about half of accepted gifts; barter 2.4/5 vs no-strings 4.2/5; video seen as too much; 4 in 10 grant usage rights only if paid; aggressive communication a top reason not to post | vendor claim | assistant, checked |
| G2 | Modash, marketer gifting survey (22 May 2026; 74 marketers) | https://www.modash.io/blog/influencer-gifting-survey | 50% vs 43.8% posting; 90.5% say gifting gets ghosted more; 43.2% name creator response; nearly half no contract; 74.3% follow up 2 to 3 times after delivery | vendor claim | assistant |
| G3 | GRIN article republished by eCommerce Fastlane (19 Mar 2026) | https://ecommercefastlane.com/influencer-gifting-the-roi-case-for-sending-product-before-asking-for-content/ | 20% to 40% post rate; existing customers 2 to 3 times more; post-delivery cadence day 0 to 1, 3 to 5, 7 to 10 | vendor claim | assistant |
| G4 | Mighty Scout blog (31 Mar 2024) | https://mightyscout.com/blog/influencer-gifting | Opt-in first; lost parcels; unsourced "61%" figure (not used) | vendor claim | assistant |
| G5 | Archive blog, two articles (27 Jan 2026 and 24 Aug 2026) | https://archive.com/blog/gifting-and-seeding-results ; https://archive.com/blog/influencer-marketing-platforms-gifting | In-house 20% to 50%; self-serve vs managed completion | vendor claim | assistant |
| G6 | Hello Partner, Awin ThinkTank panel report (3 Jun 2025) | https://hellopartner.com/what-gifting-campaigns-get-wrong-and-how-to-fix-them/ | A vendor's 90% vs "around 30%" (unsourced; not relied on) | vendor claim | assistant |
| G7 | Influencer Marketing Hub, opt-in seeding funnel (updated 7 Jul 2025) | https://influencermarketinghub.com/?p=220040 | Opt-in before shipping; 35% target | vendor claim | assistant |
| G8 | Traackr, State of Influencer Product Seeding (26 Apr 2023; 300+ marketers) | https://www.traackr.com/influencer-marketing-reports/influencer-product-seeding-report | 56% run seeding in spreadsheets; 65% re-send to non-posters | vendor claim | assistant |
| G9 | Net Influencer on a Socially Powerful survey (8 Oct 2025; 150 marketers) | https://www.netinfluencer.com/why-brands-gifting-strategies-are-falling-flat-and-how-to-fix-them/ | 38% say creators feel spammed; 30.7% see creators asking for pay | vendor claim | assistant |
| G10 | Hubfluence seeding guide (4 Jul 2026) | https://www.hubfluence.io/blog/product-seeding-influencer-gifting-guide | Track approved, shipped, delivered, posted; light brief | vendor claim | assistant |
| G11 | Fohr, guide to gifting campaigns | https://archive.fohr.co/resources/the-ultimate-guide-to-influencer-gifting-campaigns | Opt-in first; short deadlines make a bigger ask | vendor claim | assistant |
| AF1 | Modash, affiliate sales article (28 Apr 2026) | https://www.modash.io/blog/increase-affiliate-sales | Over a third say fewer than 20% of affiliates are active | vendor claim | assistant |
| AF2 | Roster, ambassador programme benchmarks (updated Sep 2026) | https://www.getroster.com/?p=10301 | Top programmes recruit customers first, low-effort first task | vendor claim | assistant |

## Disclosure

| ID | Source | URL | Used for | Label | Read by |
|---|---|---|---|---|---|
| D1 | Instagram Help Center, branded content policy; Meta Business Help Center, same policy | https://help.instagram.com/1695974997209192 ; https://www.facebook.com/business/help/221149188908254 | Free gifts are an exchange of value; use the branded content tool | verified | assistant |
| D2 | Calcalist, lawyers from Barnea Jaffa Lande (5 Jun 2023) | https://www.calcalist.co.il/local_news/article/r1i11ewsin | A free product is a benefit; put disclosure duties in agreements | law-firm summary | assistant |
| D3 | Ynet, report of draft guidelines on incentivised reviews (undated) | https://www.ynet.co.il/economy/article/SyzEMeG0w | Incentives must not depend on a positive review | verified as a news report of a draft | assistant |
| D4 | Consumer Protection Law 5741-1981, sections 1, 7(ג), 7א, unofficial copy on Hebrew Wikisource | https://he.wikisource.org/wiki/חוק_הגנת_הצרכן | "Any other benefit" makes content an advertisement | verified (unofficial copy) | assistant |
| D5 | Attorney General's position on Instagram advertising, signed 20 Jan 2020, gov.il PDF | https://www.gov.il/BlobFolder/dynamiccollectorresultitem/2907504195/he/2907504195.pdf | A tag or hashtag is not enough; say "advertisement" or "sponsored" at the opening; extra force where minors are in the audience | verified (primary document; text extracted from the fetched PDF) | assistant |
| D6 | Consumer Protection Commissioner, draft directive on online reviews, 5 Jan 2021, gov.il PDF | https://www.gov.il/BlobFolder/news/cpfta_internetopinion2021/he/docs_draft_supervisor_guide.pdf | Incentives disclosed next to the review; not conditional on praise. Final status unknown | verified (primary, draft) | assistant |
| D7 | Shibolet on the draft directive (7 Jan 2021) | https://www.shibolet.com/חוות-דעת-דירוגים-וביקורות-ברשת-האינטר/ | Breach treated as deception | law-firm summary | assistant |
| D8 | Pearl Cohen on the AG position (31 Jan 2021) | https://www.pearlcohen.com/israeli-attorney-general-celebritys-advertisement-on-social-media-platforms-must-be-disclosed/ | Tagging the advertiser is not enough | law-firm summary | assistant |
| D9 | Afik, influencer liability (1 Jul 2025) | https://www.afiklaw.com/articles/a443 | Civil and criminal liability; no enforcement outcome reported | law-firm summary | assistant |
| D10 | Instagram Help Center, "How to use the paid partnership label to tag organic branded content on Instagram" | https://help.instagram.com/1109894795810258 | Label required for branded content; the brand partner is notified and gets the post's insights | verified | lead |
| D11 | Instagram Help Center, "About branded content on Instagram" | https://help.instagram.com/128845584325492 | Branded content includes gifted products; creators must tag the partner; affiliate-link content should carry the label | verified | lead |

## Outreach: reply rates and follow-ups

Large-sample studies here are almost all **B2B sales or link-building email**, not creators.

| ID | Source | URL | Used for | Label | Read by |
|---|---|---|---|---|---|
| E1 | Backlinko with Pitchbox, 12 million outreach emails (updated 16 Apr 2019) | https://backlinko.com/email-outreach-study | 8.5% replies; one follow-up lifts replies | vendor claim | assistant |
| E2 | Instantly, Cold Email Benchmark Report 2026 (data 1 Jan to 18 Dec 2025) | https://instantly.ai/cold-email-benchmark-report-2026 | 3.43% average; 42% of replies from follow-ups; top first emails under 80 words | vendor claim | assistant |
| E3 | Woodpecker, follow-up statistics (updated 21 Jan 2025) | https://woodpecker.co/blog/follow-up-statistics/ | 2 to 3 follow-ups best; wait 2 to 3 days at least | vendor claim | assistant |
| E4 | lemlist, follow-up count (updated 10 Aug 2026); lemlist benchmarks overview | https://www.lemlist.com/blog/how-many-cold-email-follow-ups ; https://lemlist.com/blog/cold-email-benchmarks/ | Per-step reply decay | vendor claim | assistant |
| E5 | Belkins, follow-up statistics (7.5 million emails sent in 2025) | https://belkins.io/blog/sales-follow-up-statistics | Later steps bring most replies | vendor claim | assistant |
| E6 | Hunter, State of Cold Email (11 million emails sent in 2024) | https://hunter.io/the-state-of-cold-email-2025 | Unsubscribes rise after the third follow-up; small lists reply more | vendor claim | assistant |
| E7 | Gong, executive reply data (updated 27 May 2026) | https://www.gong.io/blog/do-execs-really-reply-to-cold-email-here-s-what-the-data-says | Replies drop above 100 words | vendor claim | assistant |
| E8 | Kooti et al., WWW 2015, about 2 million Yahoo users (personal email, not cold outreach) | https://ar5iv.labs.arxiv.org/html/1504.00704 | Most personal replies come within a day | verified (peer reviewed) | assistant |
| C1 | Modash newsletter, survey of 51 marketers (17 Jan 2024) | https://newsletter.modash.io/p/influencer-outreach | 72% send 1 to 2 follow-ups to creators | vendor claim | assistant |
| C2 | Modash, communication channels, survey of 37 marketers (17 Jun 2025) | https://www.modash.io/blog/communication-channels | Most start in DMs then move channel | vendor claim | assistant |
| C3 | Favikon outreach guide (Aug 2026) | https://www.favikon.com/blog/how-to-do-influencer-outreach-templates-and-tips-that-actually-get-replies | Unsourced 5% to 15% cold, 20% to 40% warm; one follow-up after 5 to 7 business days | vendor claim (unsourced) | assistant |
| C4 | StarNgage Pro (18 May 2025) | https://starngage.pro/blog/email-vs-dm-vs-creator-marketplaces-analyzing-outreach-response-rates-for-maximum-campaign-success | Unsourced channel ranges (not relied on) | vendor claim (unsourced) | assistant |
| C5 | HireInfluence (5 Jul 2026) | https://hireinfluence.com/blog/influencer-outreach-how-to-get-creators-to-respond/ | Secondhand "72% rejected" claim (not used) | vendor claim | assistant |
| C6 | Drive Research (30 Nov 2022) | https://www.driveresearch.com/market-research-company-blog/contacting-creators/ | Business email in bio as the preferred route | vendor claim | assistant |

## Instagram and WhatsApp rules

| ID | Source | URL | Used for | Label | Read by |
|---|---|---|---|---|---|
| M1 | Instagram Help Center, who can message you | https://help.instagram.com/1435783229983256 | DMs to non-followers may arrive as requests | verified | assistant |
| M2 | Instagram Direct features page; Help Center on message requests | https://about.instagram.com/features/direct ; https://help.instagram.com/585369912141614/ | Requests are text only; people can choose not to receive them | verified | assistant |
| M3 | Instagram Help Center, professional inbox folders | https://help.instagram.com/1264898753662278 | Requests folder; not marked "seen" until accepted | verified | assistant |
| M4 | Instagram Help Center, DM limits | https://help.instagram.com/436248864916865 | Warnings, then a block on sending DMs; no number published | verified | assistant |
| M5 | Instagram announcement on Hidden Words and Limits (updated 30 May 2024) | https://about.instagram.com/blog/announcements/introducing-new-ways-to-protect-our-community-from-abuse | Requests can be hidden | verified | assistant |
| M6 | Meta newsroom (updated 11 Feb 2025) | https://about.fb.com/news/2022/10/protecting-people-on-instagram-from-abuse/ | Spam filtering of requests | verified | assistant |
| M7 | Meta newsroom (rule updated 25 Nov 2024) | https://about.fb.com/news/2023/06/parental-supervision-and-teen-time-management-on-metas-apps/amp/ | Text-only requests | verified | assistant |
| M8 | Instagram Help Center, partnership messages; Meta newsroom on the creator marketplace (Feb 2024) | https://help.instagram.com/319025483576137 ; https://about.fb.com/news/2024/02/creator-marketplace-for-brands-and-creators-to-collaborate-on-instagram/ | Partnership message folder; Israel not among listed markets | verified | assistant |
| W1 | WhatsApp Business Messaging Policy (updated 23 Sep 2026) | https://whatsappbusiness.com/policy/ | Opt-in before a business contacts a person; covers the Business app and platform; silent on personal accounts | verified | assistant, checked |
| W2 | WhatsApp Messaging Guidelines (updated 23 Sep 2026) | https://www.whatsapp.com/legal/messaging-guidelines | Repeated unwanted contact counts as spam | verified | assistant |

## Tools (details and prices in `tools-compared.md`)

| ID | Tool | URLs | Label | Read by |
|---|---|---|---|---|
| T1 | CreatorIQ | https://www.creatoriq.com/ ; https://www.creatoriq.com/pricing | vendor claim; price "not public" verified | assistant |
| T2 | Traackr | https://www.traackr.com/ ; https://www.traackr.com/pricing | vendor claim; price verified not public | assistant |
| T3 | Later Influence | https://later.com/about/ ; https://later.com/influencer-marketing-tools/influencer-management-platform/ ; https://later.com/influencer-marketing/ ; https://later.com/pricing/ | name history verified; features vendor claim | assistant |
| T4 | GRIN | https://grin.co/ ; https://grin.co/platform ; https://grin.co/pricing/ | prices verified; features vendor claim | assistant |
| T5 | Aspire | https://www.aspire.io/ ; https://www.aspire.io/plans ; https://help.aspireiq.com/en/articles/5552620-overview-of-campaign-workflow-stages ; https://help.aspireiq.com/en/articles/12167673-beta-how-to-customize-your-workflow ; https://www.aspire.io/blog/creator-product-selection | stage list verified (help centre); rest vendor claim | assistant |
| T6 | Upfluence | https://www.upfluence.com/pricing ; https://www.upfluence.com/creator-relationship-management/ | pricing terms verified; features vendor claim | assistant |
| T7 | HypeAuditor | https://hypeauditor.com/pricing/ ; https://hypeauditor.com/campaign-management/ ; https://help.hypeauditor.com/en/articles/6420670-how-to-manage-influencers-according-to-your-workflow | custom statuses verified; automation vendor claim | assistant |
| T8 | Modash | https://www.modash.io/pricing ; https://help.modash.io/en/articles/13715187-managing-creator-relationships-and-statuses ; https://help.modash.io/en/articles/10476262-creating-and-organizing-creator-lists | default statuses and "Status updates are currently manual" verified | assistant, checked |
| T9 | Influencity | https://influencity.com/pricing | verified (no amounts shown) | assistant |
| T10 | Heepsy | https://www.heepsy.com/pricing | prices verified | assistant |
| T11 | Insense | https://insense.pro/pricing | prices verified; workflow vendor claim | assistant |
| T12 | Archive | https://archive.com/ ; https://archive.com/pricing | vendor claim; price verified not public | assistant |
| T13 | Superfiliate | https://www.superfiliate.com/pricing | verified not public | assistant |
| T14 | Shopify Collabs | https://www.shopify.com/collabs ; https://help.shopify.com/en/manual/promoting-marketing/collabs/merchants ; https://help.shopify.com/en/manual/promoting-marketing/collabs/merchants/managing-creators ; https://help.shopify.com/en/manual/promoting-marketing/collabs/merchants/payments | verified (product documentation) | assistant |
| T15 | UpPromote | https://uppromote.com/pricing/ ; https://docs.uppromote.com/set-up/translation | prices verified | assistant |
| T16 | GoAffPro | https://goaffpro.com/pricing ; https://docs.goaffpro.com/affiliate-coupons/automatically-apply-discount-codes ; https://goaffpro.com/use-case/influencer-marketing | auto-applied discount verified; prices verified | assistant |
| T17 | Collabstr | https://collabstr.com/pricing | not read (HTTP 403) | assistant |
| T18 | Google Sheets | https://workspace.google.com/products/sheets/ ; https://support.google.com/docs/answer/6388102 ; https://support.google.com/googleone/answer/9312312 | verified | assistant |
| T19 | Airtable | https://www.airtable.com/pricing ; https://support.airtable.com/docs/airtable-plans ; https://support.airtable.com/articles/5016991853-airtable-technical-requirements | verified | assistant |
| T20 | Notion | https://www.notion.com/pricing ; https://www.notion.com/help/notion-for-mobile ; https://www.notion.com/help/guides/working-offline-in-notion-everything-you-need-to-know ; template listings: https://www.notion.com/templates/the-influencer-outreach-manager , https://www.notion.com/templates/influencer-campaign-management , https://www.notion.com/templates/influencer-hub | verified; the pricing page and the offline guide disagree on auto-download | assistant |
| T21 | Trello | https://trello.com/pricing ; https://support.atlassian.com/trello/docs/changing-your-language-in-trello/ ; https://www.atlassian.com/blog/trello/trello-mobile-offline (2017) ; https://support.atlassian.com/trello/docs/trello-desktop-apps/ | verified; offline mobile is a 2017 vendor post | assistant |
| T22 | monday.com | https://monday.com/pricing | verified | assistant |
| T23 | HubSpot | https://www.hubspot.com/pricing/crm | verified | assistant |
| T24 | folk | https://www.folk.app/pricing | prices verified; features vendor claim | assistant |
| T25 | Attio | https://attio.com/pricing | verified | assistant |
| T26 | Pipedrive | https://www.pipedrive.com/en/blog/best-crm-software (pricing page returned errors) | vendor claim | assistant |
| T27 | Streak | https://www.streak.com/pricing | verified | assistant |
| T28 | SocialKit outreach tracker template (spreadsheet statuses) | https://socialk.it/en/resources/influencer-ugc-outreach-tracker-template | vendor claim | assistant |
| T29 | SARAL spreadsheet templates (14 Sep 2025) and Modash spreadsheet template (13 May 2025): when a spreadsheet stops being enough | https://www.getsaral.com/academy/influencer-management-spreadsheet-templates ; https://www.modash.io/blog/influencer-marketing-spreadsheet-template | vendor claim (opinions) | assistant |

## CRM use and abandonment

| ID | Source | URL | Used for | Label | Read by |
|---|---|---|---|---|---|
| F1 | Zoho press release on an SMB Group survey (31 Aug 2023; more than 1,500 US businesses with 100 or fewer staff) | https://www.zoho.com/news/survey-from-zoho-finds-small-businesses-ready-to-invest-in-crm-solutions.html | Ease of use 53% top selection factor; 39% of non-users on spreadsheets and email | verified that the release says so; vendor-commissioned | assistant |
| F2 | Freshworks, CRM statistics (survey of 600, Apr 2024) | https://www.freshworks.com/theworks/company-news/crm-statistics/ | Training and adoption top challenge | vendor claim | assistant |
| F3 | Salesforce, State of Sales 2026 and 2022 | https://www.salesforce.com/news/stories/state-of-sales-report-announcement-2026/ ; https://www.salesforce.com/news/stories/sales-research-2023/ | Data-entry burden in large teams | vendor claim | assistant |
| F4 | Validity report via CustomerThink (25 Aug 2026) | https://customerthink.com/validity-releases-state-of-crm-data-management-in-2026-report-revealing-marketers-trust-in-their-data-hasnt-caught-up-with-their-ai-goals/ | Time spent fixing data | vendor claim | assistant |
| F5 | Gene Marks column (14 Jul 2022) | https://www.genemarks.com/columns/on-crm-1-in-4-small-businesses-replaced-their-crms-in-2022-and-these-are-the-lessons-learned | Replacement rates | verified as reported (secondary) | assistant |
| F6 | Nomalys statistics page | https://www.nomalys.com/en/28-surprising-crm-statistics-about-adoption-features-benefits-and-mobility/ | The "43% use under half the features" claim has no traceable source | verified that the page says it; numbers unverified | assistant |
| F7 | Influencer Marketing Hub Benchmark Report 2026 (4 May 2026) | https://influencermarketinghub.com/influencer-marketing-benchmark-report/ | Codes are the most-used measurement tool (45.9%) | verified; thin method | assistant |
| F8 | Founders Edition, "Don't buy a CRM" (19 Apr 2024) | https://foundersedition.co/p/don-t-buy-a-crm | Stage, next action, date, notes | verified (opinion) | assistant |
| F9 | UK Business Forums thread (27 Apr 2026) | https://www.ukbusinessforums.co.uk/threads/is-anyone-else-getting-fed-up-with-how-complicated-crms-have-become.430705/ | Essentials owners keep | verified (anecdote) | assistant |
| F10 | Product Hunt discussion | https://www.producthunt.com/p/vibecoding/has-anyone-built-their-own-crm-instead-of-using-one | Tools dropped for not going back to them | verified (anecdote) | assistant |

## Israel: channels, Hebrew in tools, creator norms

| ID | Source | URL | Used for | Label | Read by |
|---|---|---|---|---|---|
| IL1 | ICE, report of the Israel Internet Association survey (Geocartography, May 2026, 1,040 people) | https://www.ice.co.il/social/news/article/1114495 | WhatsApp 99%, Facebook 90%, Instagram 82%, TikTok 59% | verified (news report of a survey) | assistant, checked |
| IL2 | Maariv, same survey | https://www.maariv.co.il/economy/tech/article-1326023 | Corroboration | verified (news report) | assistant |
| IL3 | Internet Society, 2022 index | https://news.internetsociety.org/israel-internet-association-unveils-an-index-of-internet-use-in-israel/ | Earlier figures | verified | assistant |
| IL4 | DataReportal, Digital 2026 Israel (8 Nov 2025) | https://datareportal.com/reports/digital-2026-israel | Internet users; ad-reach estimates (not active users); no WhatsApp data | verified | assistant |
| IL5 | DataReportal, Digital 2025 Israel | https://datareportal.com/reports/digital-2025-israel | Comparison | verified | assistant |
| RTL1 | Google Docs Editors Help, right-to-left | https://support.google.com/docs/answer/65166 | Sheets right-to-left per sheet and cell | verified | assistant |
| RTL2 | Notion Help, change your language | https://www.notion.com/help/change-your-language | Hebrew interface, mirrored layout; auto direction except simple tables; databases not mentioned | verified | assistant |
| RTL3 | createwith.com changelog (AI-drafted page) | https://www.createwith.com/tool/notion/updates/notion-adds-arabic-and-hebrew-support | Claimed Notion Hebrew launch date, 26 Jan 2026 (not relied on) | third-party claim | assistant |
| RTL4 | Airtable Support, introduction to Airtable basics | https://support.airtable.com/articles/1747995963-introduction-to-airtable-basics | No Hebrew interface; Hebrew shown left to right | verified | assistant, checked |
| RTL5 | monday.com blog (2 Feb 2023) | https://monday.com/blog/product/kick-off-2023-with-muted-notifications-and-rtl-text/ | Right to left for forms only | verified | assistant |
| RTL6 | monday.com community feature request (2025) | https://community.monday.com/t/feature-request-better-support-for-rtl-languages/120487 | Users report direction problems on boards | verified (user post) | assistant |
| RTL7 | Atlassian issue TRELLO-289 (updated 18 Dec 2025) | https://jira.atlassian.com/browse/TRELLO-289 | Right to left in Trello cards not supported | verified | assistant |
| RTL8 | HubSpot, language offerings (updated 4 Sep 2026) | https://knowledge.hubspot.com/help-and-resources/hubspot-language-offerings | No Hebrew interface | verified | assistant |
| RTL9 | HubSpot, multi-language blog | https://knowledge.hubspot.com/blog/create-a-multi-language-blog | Right to left in the blog editor only | verified | assistant |
| N1 | ICE on FLONCI's pricing guide (12 Oct 2026) | https://www.ice.co.il/advertising-marketing/news/article/1133279 | Micro-creator deals "hundreds to thousands of shekels"; no barter data | vendor claim (reported by news) | assistant |

## Israel: privacy, anti-spam, children

Not legal advice. A lawyer should read the official texts (Nevo or Reshumot).

| ID | Source | URL | Used for | Label | Read by |
|---|---|---|---|---|---|
| P1 | Protection of Privacy Law 5741-1981, unofficial copy on Hebrew Wikisource | https://he.wikisource.org/wiki/חוק_הגנת_הפרטיות | "Database" and its exclusions (s. 3); registration only for data-selling databases above 10,000 people and public bodies (s. 8א); duty to inform (s. 11); direct mailing (s. 17ד to 17ו); sensitive data categories | verified (unofficial copy) | assistant, checked (s. 3 and 8א) |
| P2 | Privacy Protection (Data Security) Regulations 5777-2017, unofficial copy | https://he.wikisource.org/wiki/תקנות_הגנת_הפרטיות_(אבטחת_מידע) | Security levels; "database managed by an individual" | verified (unofficial copy) | assistant |
| P3 | DLA Piper, Data Protection Laws of the World: Israel (modified 25 Dec 2024) | https://www.dlapiperdataprotection.com/?c=IL | Amendment 13 date, registration, section 11, direct mailing guideline | law-firm summary | assistant |
| P4 | Meitar, Amendment 13 note (7 Aug 2024) | https://meitar.com/wp-content/uploads/2024/09/Amendment-13-to-the-Privacy-Protection-Law-Approved-by-the-Knesset-Major-Points-of-the-Amendment-and-Its-Implications.pdf | Fines up to ₪320,000 per violation; registration narrowed | law-firm summary | assistant |
| P5 | Hebrew Wikipedia, "חוק הספאם" | https://he.wikipedia.org/wiki/חוק_הספאם | Section 30A scope (email, SMS, fax, automatic dialling); opt-in; up to ₪1,000 per message | verified (encyclopedia, secondary) | assistant |
| P6 | Pearl Cohen on the anti-spam law (27 May 2008) | https://www.law.co.il/en/news/2008/05/27/knesset-approves-israeli-anti-spam-law/ | One-time offer to a business | law-firm summary | assistant |
| P7 | Afik on anti-spam case law (2023) | https://www.afiklaw.com/articles/a397 | Courts read "advertisement" broadly; social messages possibly covered | law-firm summary | assistant |
| P8 | Consumer Protection (Advertising and Marketing Aimed at Minors) Regulations, unofficial copy | https://he.wikisource.org/wiki/תקנות_הגנת_הצרכן_(פרסומת_ודרכי_שיווק_המכוונים_לקטינים) | Regulation 7A: no use of a minor's details without a parent's consent, except to deliver a product | verified (unofficial copy) | assistant |
| P9 | protocol.co.il, children in shows and advertising (undated legal information site) | https://protocol.co.il/child-work-show-commercial/ | Labour Ministry permit for children under 15 in advertising filming | verified (secondary) | assistant |
| P10 | Meta newsroom, teen and child-safety protections (23 Jul 2025, updated 23 Oct 2025) | https://about.fb.com/news/2025/07/expanding-teen-account-protections-child-safety-features/ | Adult-run accounts featuring children get the strictest message settings | verified | assistant |

## Attribution without a tracking budget

| ID | Source | URL | Used for | Label | Read by |
|---|---|---|---|---|---|
| U1 | Google Analytics Help, URL builders and UTM parameters | https://support.google.com/analytics/answer/10917952 | Source, medium, campaign; case sensitive | verified | assistant |
| U2 | Google Analytics Help, lookback windows | https://support.google.com/analytics/answer/10597962 | 30 and 90 day defaults; retired models | verified | assistant |
| U3 | Google Analytics Help, direct traffic and models | https://support.google.com/analytics/answer/10596866 | Direct visits get no credit unless the whole path is direct | verified | assistant |
| U4 | Shopify Help, marketing reports | https://help.shopify.com/en/manual/reports-and-analytics/shopify-reports/report-types/default-reports/marketing-reports | Attribution models; 30-day reset (a worked example; LumeBook runs its own admin) | verified | assistant |
| U5 | Shopify Help, Collabs programmes | https://help.shopify.com/en/manual/promoting-marketing/collabs/merchants/collabs-programs | Per-creator links and codes | verified | assistant |
| U6 | Meta developer documentation, Instagram media insights | https://developers.facebook.com/documentation/instagram-platform/reference/instagram-media/insights | Story link clicks; up to 48 hours delay; story metrics through the API for 24 hours | verified | assistant |
| U7 | link.boo, Instagram link click tracking guide | https://link.boo/guides/instagram-link-click-tracking | In-app browser strips the referrer (its loss figure is hypothetical) | vendor claim | assistant |
| U8 | MarTech on RadiumOne (2014) | https://martech.org/dark-social-still-near-70-percent/ | About 69% of sharing in private channels (old) | vendor claim | assistant |
| U9 | The Drum on GlobalWebIndex (2019) | https://www.thedrum.com/news/63-people-prefer-share-content-dark-social-channels | 63% prefer private messaging for sharing | vendor claim | assistant |
| U10 | Make Influence, codes vs links | https://www.makeinfluence.com/en/academy/discount-codes-vs-tracking-links | Links miss cross-device buys; its numbers are hypothetical | vendor claim | assistant |
| U11 | Modash, discount codes (Sep 2026) | https://www.modash.io/blog/influencer-discount-codes | Code poaching; codes win when both are used | vendor claim | assistant |
| U12 | Fairing, measuring influencer performance | https://fairing.co/resources/measurement-faqs/how-do-you-measure-influencer-marketing-performance | Post-purchase "how did you hear about us" method | vendor claim | assistant |

## Searched or opened but not used

- Instagram Help Center pages fetched without a browser returned only "Help Center"; they were then read in the browser pane (D10, D11, M-series).
- Collabstr (all pages HTTP 403), Later Influence help centre (403), Pipedrive pricing (403 and 500), monday.com language list (403), Capterra survey pages (403), the Israel Internet Association's own report (403 on the copies tried), the Privacy Protection Authority's service pages (403).
- Bizportal article on creator rates: only 2017 US figures, not used.
