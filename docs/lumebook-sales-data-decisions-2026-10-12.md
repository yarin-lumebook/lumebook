# LumeBook: what the sales data says and what social does about it

Written 12 Oct 2026, updated 15 Oct with the 14 Oct findings on link tracking and grandparents. Internal, do not share outside the project: it holds sales figures.

Source for every number: 17 screenshots of the store's admin dashboard taken on 12 Oct 2026 at 09:34, from the Analytics tab (pdf.lumebook.com/api/admin/modern/analytics) and the Marketing tab (pdf.lumebook.com/api/admin/modern/marketing). Values marked ≈ were read off a chart, not a printed number. Anything marked "my reading" or "my guess" is an interpretation, not something the dashboard states. The book price (₪119) comes from `docs/lumebook-product-brief.md` as of 1 Oct and was not re-checked.

## At a glance

| Figure | What it means |
|---|---|
| 1 in 5 | people who start a book pay for it within a week |
| ₪61 to ₪113 | cost of one sale from ads, against a ₪30 goal |
| 31% | of orders are birthday and milestone books |
| ≈115 | orders a month now, against ≈490 in March |

## The situation in plain words

1. **People like making the book, but most don't pay.** Of 6,130 people who started a book, 1,329 paid within a week, about 1 in 5. In the last 30 days, 202 orders reached the payment step and 85 were bought, so about half leave there.
2. **Ads are expensive.** A sale costs ₪61 if ads get credit for every sale and ₪113 on Meta's own count. The company's goal is ₪30 and its ceiling is ₪50, on a ₪119 book. Ads cannot be what grows LumeBook right now.
3. **Sales behave like a tap.** Strong months had ≈300 to 490 orders, weak months ≈15 to 20, and it is about 115 a month now. No steady stream of customers arrives on its own. Building that stream is what social is for.
4. **Sales to people who already know the product cost almost nothing.** A purchase that followed a WhatsApp reminder or a post-purchase message cost $0.16 to $2.34 in message fees. The dashboard says those purchases followed the message, not that the message caused them.
5. **People buy for a moment in the child's life.** Birthday is the number one book. Birthday, new sibling, pacifier, potty and first grade together are 603 of 1,972 orders, almost a third.
6. **The buyers are not only young moms.** In the ads, women 55 to 64 and 35 to 44 have the most purchases, and women 25 to 34 cost the most per purchase among the large groups. My reading is that the older group is grandmothers buying a gift. The data does not prove it.
7. **The admin can't show where a sale came from yet.** Its Marketing tab says the website does not record which link brought an order, so a sale from a post or from a creator looks like any other sale. A 14 Oct read of the store's code found that it does send link data (UTMs, first and last touch) when a book is created, so the gap may be in the admin's reporting rather than in the tracking (`research/creator-content-conversion/report.md`).

## Social decisions

These need no further information and sit inside the social role.

1. **Choose topics by buying moment.** Something on birthdays every week. One milestone theme a month, in order of sales: new sibling, then pacifier, then potty.
2. **One gift-giver post a week.** Aimed at a grandmother or aunt giving the book. It sits outside the carousel rule of mom or both parents, so it runs as a separate test for about a month. A 14 Oct read of 2,982 comments on creator posts found only 5 people who said they were grandparents (`research/creator-content-conversion/report.md`), so the grandmother buyer is still a hypothesis and this test is how to find out.
3. **Pick creators by moment and place, not by size.** First in line: creators living a moment now (second child on the way, a toddler giving up the pacifier, a birthday coming), two or three creators of grandmother age, and creators from the top cities. Each creator gets the book that matches their moment.
4. **Show the finished book and the price openly once a week.** The printed book in a child's hands, what it costs, how fast it arrives. My guess is that people leave at payment because they are unsure what they will get or surprised by the total.
5. **Measure with what social controls.** A one-line daily log of what went out (post, creator video, group post). Every Monday, compare it to orders per day in the admin and mark the days that jumped. Count comments and DMs per post. Thu 8 Oct had ≈13 orders in one day and nothing on the dashboard explains it. A log would.
6. **Start parent groups with the top cities.** Rishon LeZion, Tel Aviv, Ashkelon, Be'er Sheva, Petah Tikva, Holon, Netanya, then outward. (My first draft left Tel Aviv out without a good reason. It is second by orders.)
7. **Publish the week's strongest post on Wednesday evening or Thursday.** Ad sales were cheapest on Thursday and Friday. The dashboard itself says this is not a valid test yet, but it costs nothing to try.
8. **One request to Yossi: show sales per link and per creator in the admin.** Before creator videos go live for Hanukkah (creator books are due 10 Nov). The store already runs an ambassador program with personal links and sends link data with each new book (`research/creator-content-conversion/report.md`), so what's missing is a view of which orders each link brought. Without it nobody can show what social sold or check creator commissions against real sales.

Not doing: asking for money to boost posts, since ads already cost too much per sale. Views and followers stay in the KPI table as supporting numbers. Orders and books started are the ones that matter.

## Things to do

Concrete steps for the decisions above. Tick them off on the page; the ticks stay in this browser.

### This week

- [ ] **Send Yossi one message.** Ask two things: can the admin show orders per link and per creator, and can creators from the map join the store's ambassador program with their own link. The 14 Oct research lists both as the first thing to settle before any creator test (`research/creator-content-conversion/report.md`, section 10).
- [ ] **Start the publishing log.** One row per day: the date, what went out (post, story, creator video, group post), where, and the link used. About two minutes a day.
- [ ] **Make new sibling October's milestone theme.** אח חדש and אחות חדשה together have 132 orders, the most of any milestone. Plan a reel, a carousel and stories on it for the rest of the month.
- [ ] **Post one birthday piece.** Birthday is the best-selling book (262 orders).
- [ ] **Film the printed book and show the full price.** The book in a child's hands, the price (₪119 on 14 Oct, `research/creator-content-conversion/report.md`), home shipping (₪30) and delivery time (up to 7 business days home, `docs/lumebook-product-brief.md`). Check all three on lumebook.com before posting.
- [ ] **Contact topaz_meir_slp first.** The 14 Oct research's first recommended test: a book-list post by a speech therapist with the pacifier book as the one personalised pick and her own link in the DM (`research/creator-content-conversion/report.md`). She is already "in process" in the [creator map](https://claude.ai/artifact/DCJ2ZT1Y4K8MrcH5bot2Hj).
- [ ] **Shortlist 5 creators who are in a moment now.** From the [creator map](https://claude.ai/artifact/DCJ2ZT1Y4K8MrcH5bot2Hj) and their recent posts: a second baby on the way, a toddler giving up the pacifier, a birthday coming. Write the moment and the city next to each name.
- [ ] **Post the first gift-giver piece.** Made for a grandmother or aunt giving the book. Note its saves, shares, comments and DMs so it can be compared with your other posts after four weeks.

### Every week

- [ ] **Monday: compare the log with orders.** Count orders per day in the admin's All Orders tab, mark the days that jumped, and check what went out the day before.
- [ ] **Count comments with לומי and DMs per post.** It is the one buying signal social can count today.
- [ ] **Keep the weekly mix.** One birthday post, one gift-giver post and one printed-book post, plus the month's milestone theme.
- [ ] **Put the strongest post out on Wednesday evening or Thursday.**
- [ ] **Parent groups: start near home.** The [parent community map](https://claude.ai/artifact/WAcZJ7xXj826wzvLj49dmE) is already ordered closest to Ashkelon, which is third by orders. Then Rishon LeZion and Be'er Sheva.

### On 31 Oct

- [ ] **Take the same admin screenshots again.** The Analytics and Marketing tabs, then compare with 12 Oct: orders per month, the 1 in 5, cost per ad sale, and whether Meta's share of sales recovered. 31 Oct is the "initial analytics and new targets" date in `shared/facts.json`.

### By mid-November

- [ ] **Send the Hanukkah creator books by 10 Nov** (`shared/facts.json`). Pick creators by moment and city, send each the book that fits their moment, and share the [creator brief](https://lumebook-creator-brief.vercel.app) with them.
- [ ] **Have Yossi's answer on sales per link** before the creator videos go up.
- [ ] **Judge the gift-giver test after four weeks.** Compare its saves, shares, comments and DMs with your other posts. Keep it if it holds up; drop it if not.

## The numbers behind it

### Paid ads (Meta), 13 Sep to 12 Oct

| Measure | Value |
|---|---|
| Spent | ₪6,992 |
| Sales in the same days (all sources) | 115 |
| Sales Meta takes credit for | 62 |
| Cost per sale, every sale credited to ads | ₪61 |
| Cost per sale, Meta's count | ₪113 |
| Money back per ₪1 of ads | ₪1.83 |
| Company target and ceiling | ₪30 and ₪50 |
| Times an ad was shown | 292,622 |
| Clicks to the site | 4,214 (1.4% of views) |

- Revenue in this window works out to about ₪111 per sale (₪6,992 × 1.83 ÷ 115).
- Last 7 full days: ₪2,073 spent, 50 orders, ₪41 per order, Meta credits 18 (₪115 each). The 7 days before: ₪1,678, 21 orders, ₪80 per order, Meta ₪210.
- Cost per order by week ≈: ₪44 (week of 7 Sep), ₪36, ₪130, ₪80, ₪41 (week of 5 Oct).
- Meta's share of sales fell from ≈80% in the first two weeks to 36 to 38% in the last two. Either tracking broke around 28 Sep or more sales came from somewhere else. The dashboard's reliability panel warns that server and Meta purchase counts differ by more than 25% and that UTM coverage is under 80%.
- The dashboard shows an active budget of ₪700 a day, but spend in the last 7 full days averaged ₪296 a day.
- Thu 8 Oct: ≈13 to 14 orders in one day, of which Meta credits about 3.

Who the ads reach (Meta delivery and attribution, not verified buyers):

| Segment | Spend | Meta purchases | Cost per purchase | Share of ad views |
|---|---|---|---|---|
| Women 55-64 | ₪1,540 | 17 | ₪91 | 22% |
| Women 35-44 | ₪1,404 | 13 | ₪108 | 14% |
| Women 45-54 | ₪1,114 | 8 | ₪139 | 14% |
| Women 25-34 | ₪1,238 | 7 | ₪177 | 18% |
| Women 65+ | ₪1,219 | 5 | ₪244 | 26% |
| Men 25-34 | ₪112 | 8 | ₪14 | 1.5% |

Women 55 and over get 48% of ad views. The men 25-34 row is too small to trust.

Cost per order by weekday (34 days, the dashboard says no valid test yet): Sun ₪53, Mon ₪55, Tue ₪92, Wed ₪97, Thu ₪31, Fri ₪40, Sat ₪82.

### From book to purchase

- All time: 14,942 books started, 1,844 paid within 7 days (12.3%). Per person: 6,130 started, 1,329 paid within 7 days (21.7%). About 4,800 people with a phone number made a book and did not buy that week.
- Last 30 days (Mixpanel): 527 orders created, 202 reached payment, 85 purchased. Mixpanel undercounts (the server has 115 sales), so the real drop at payment is between 43% and 58%.
- Buyers buy 1.40 books each on average (1,411 buyers).

### WhatsApp messages

Last 30 days, Marketing tab, compared with a small group left alone:

| Message | People contacted | Bought | Extra sales per 100 |
|---|---|---|---|
| Unfinished book reminder | 146 | 13 | +4.1 |
| First coupon | 132 | 7 | +5.4 |
| Third coupon | 125 | 2 | +1.6 |
| Birthday reminder | 2 | none | none |

Last 90 days, Analytics tab, purchases that followed a message (not proof the message caused them):

| Message | Sent | Purchases after | Message cost per purchase |
|---|---|---|---|
| Post-purchase offer | 209 | 48 | $0.16 |
| Reminder to finish the book | 483 | 17 | $1.02 |
| Third coupon | 390 | 8 | $1.75 |
| Second coupon | 269 | 5 | $1.93 |
| First coupon | 521 | 8 | $2.34 |
| Back-to-school broadcast | 813 | 1 | $29.18 |

The whole programme cost about $96 in message fees over 90 days (the dashboard's estimate at $0.036 a message).

### What sells

Paid orders, all time (1,972):

| Book | Orders |
|---|---|
| יום הולדת | 262 |
| Custom story | 237 |
| הלב של יובל | 167 |
| חברים צבעוניים | 118 |
| ביי ביי מוצץ | 86 |
| אח חדש | 72 |
| עדן והחיות החופשיות, נפרדים מהטיטולים | 66 |
| אחות חדשה | 60 |
| שלום כיתה א' | 57 |
| הטורניר הגדול של נוי | 50 |
| מה אהיה מחר? | 43 |

- New sibling combined (אח חדש + אחות חדשה) is 132 and would rank fourth.
- 86% of orders are catalogue books, 12% custom stories, 2% written from scratch.
- This table was set to "all period". Switching the selector to 30 days would show what sells now.

### Who the books are for

- Girls 51%, boys 49%.
- Book language: Hebrew 91.4%, Arabic 4.7% (93 orders), English 1.6%, Russian 0.9%.
- Child age is not usable: 77.5% are "age 5", which the dashboard flags as a likely default. Among the other ages shown, ages 1 to 4 have 334 orders and ages 6 to 8 have 95.

### Where

| City | Orders |
|---|---|
| ראשון לציון | 103 |
| תל אביב-יפו | 69 |
| אשקלון | 62 |
| באר שבע | 61 |
| פתח תקווה | 58 |
| חולון | 52 |
| נתניה | 52 |
| ירושלים | 51 |
| רמת גן | 49 |
| חיפה | 48 |
| אשדוד | 47 |
| רחובות | 47 |

The top 12 cities are 35% of orders, so sales are spread across the country.

### History

Paid orders by month, ≈ read off the chart: Oct 2025 60, Nov 310, Dec 40, Jan 2026 240, Feb 370, Mar 490, Apr 110, May 20, Jun 15, Jul 15, Aug 118, Sep 89, Oct (12 days) 57. Total revenue to date ₪278,116.

## Numbers not to use

- **"Conversion rate 61%"** and the by-source cards (gallery 50%, custom 64%, scratch 73%). The monthly chart shows exactly 100% for six straight months, so unpaid orders from that period are missing. Use 21.7% per person, or 16% per order for the last 30 days.
- **Site visitors.** 129 visitors against 161 add-to-carts in the same week, while Meta reports 4,214 clicks in 30 days. Visitor tracking sees a fraction of the traffic.
- **Child age.** See above.
- **The weekday table as proof.** The dashboard says 4 of the 8 full weeks it needs are missing.

## Things to check with whoever built the dashboard

- The Analytics tab says there is no random control group for WhatsApp, while the Marketing tab reports extra sales against one.
- "+5.4 per 100" for the first coupon is higher than the 5.3% who bought, so the left-alone group is probably tiny.
- The second coupon has fewer sends (269) than the third (390), so step two may be skipped for some people.
- Budget of ₪700 a day shown against ≈₪296 a day actually spent.

## Open questions nobody has answered

1. What ran in Nov 2025 and Feb to Mar 2026, and what stopped in Dec and in May?
2. Was there any ad spend in August 2026? August had ≈118 orders before the Meta data begins on 8 Sep. If no ads ran then, sales without ads were about 3.8 a day, the same as the 30-day ad window, and the ads may be adding very little.
3. What happened on Thu 8 Oct?
4. What do print and shipping cost per book? That sets the real ceiling for cost per sale.

## Beyond social, to raise with Yossi if useful

- Keep ad spend flat (the dashboard recommends the same), stop showing ads to women 65+, try a small ad set for men 25-34, then run the single control against challenger test the dashboard proposes.
- Find where people leave at the payment step, and add a WhatsApp message for people who reached payment and did not pay.
- Turn on the birthday reminder (2 sends so far) and use the post-purchase message to offer a second book and ask for the reveal video.
- Stop broadcasts to the whole list (813 sent, 1 purchase).
- Remove the default child age so real ages are collected.
