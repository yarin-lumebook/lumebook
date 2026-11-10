# Event verification across the Ad Library pool — evidence

*Run 25 Aug 2026 with `toolchain/verify-events.py` over `toolchain/adlib-domains.txt`
(87 rows). Raw output: `adlib-events.jsonl`. Superseded runs kept as
`adlib-events-v1.jsonl` and `-v2.jsonl`; **do not read them**, both overstate the
findings — see "Two retracted runs" below.*

This answers a question `scan-dtc.py` cannot: not *is GA4 installed* but *does the
ecommerce tracking fire*. That distinction is 20 of the brief's 100 points and it is
the difference between an opening line that lands and one that is simply false.

## Result

| Verdict | Stores | Meaning |
|---|---:|---|
| `ECOMMERCE CONFIRMED` | 10 | `view_item` **and** `add_to_cart` observed |
| `MEASUREMENT GAP` | 11 | Cart provably changed, **zero** ecommerce events |
| Partial (one of the pair) | 13 | Half the funnel is tracked |
| `UNKNOWN` | 53 | Walk did not complete — says nothing about the store |

**Read `UNKNOWN` as "not measured", never as "not tracked".** 21 stores would not
report their cart state and 8 never rendered; both are scanner limits, not findings.

## The gate that makes this trustworthy

Every "no `add_to_cart`" claim requires the **cart item count to have provably
increased** — read from `/cart.js` (Shopify) or the Woo Store API before and after the
click. Without that gate a failed click is indistinguishable from a missing tag, and
the store gets blamed for the scanner's miss.

Cart state across the pool: **32 confirmed +1**, 8 unchanged (click failed), 21
unreadable, 26 never got that far.

## Confirmed measurement gaps — cart changed, no ecommerce events

Every row: the walk reached a product page, clicked add-to-cart, **the cart
incremented**, and GA4 still sent nothing but pageview/scroll.

| Score | Domain | Ads | GA4 | Events actually sent |
|---:|---|---:|---|---|
| 70 | `oolala.co.il` | 1 | `G-2GCKTW4SD9` +1 more | page_view, scroll |
| 70 | `innerdragon.co` | 1 | `G-X61M2HV01F` | page_view, scroll |
| 69 | `vlinksshop.com` | 1 | `G-28LRS0X43Q` | page_view |
| 69 | `tanaorjewelry.co.il` | 2 | `G-LMMK2KVNNS` | page_view, scroll |
| 69 | `secret-garden.co.il` | 2 | `G-J2YNTLLNEZ` +1 | page_view, scroll |
| 69 | `billy-online.com` | 2 | `G-WQJE7ESRXS` | page_view |
| 69 | `bagstore.co.il` | 1 | `G-53FG862JC4` | page_view |
| 67 | `perfectline.co.il` | 1 | `G-Q4NGD66SS6` | page_view |
| 64 | `stav-fine-jewelry.com` | 2 | `G-EN90D7SKCB` | page_view, scroll |
| 57 | `yuka-tech.co.il` | 1 | `G-HM5DPCPSXW` | page_view |
| 0 | `adinails.co.il` | 1 | `G-EDMGD10GHV` | page_view, scroll |

## Partial gaps — the more interesting half

A store tracking one side of the funnel has someone who set tracking up and stopped.
`goom.co.il` is the strongest single finding in the pool.

**`goom.co.il` — score 79, RECOMMEND(pre), 27 active ads, supplements, median ₪249.**
Verified twice, independently of the batch run: cart went **0 → 1** on
`/products/b12-d3-2`, and GA4 `G-4P0CT3T5PR` sent `page_view`, `scroll`, `view_item`
— and **no `add_to_cart`**. A store with 27 live ads and a ₪249 median basket is
optimising Meta delivery without an add-to-cart signal.

| Score | Domain | Ads | What fires | What is missing |
|---:|---|---:|---|---|
| 83 | `econawa.co` | 10 | add_to_cart | **view_item** |
| 79 | `goom.co.il` | 27 | view_item | **add_to_cart** |
| 77 | `goldjojoba.com` | 2 | add_to_cart, custom `gj_first_interaction` | **view_item** |
| 76 | `joyame.co.il` | 2 | add_to_cart | **view_item** |
| 69 | `notforsaletlv.com` | 1 | add_to_cart | **view_item** |
| 68 | `dealcosmetics.co.il` | 1 | add_to_cart, `Scroll_25%`, `Timer_10sec` | **view_item** |
| 62 | `nsp-organica.co.il` | 1 | add_to_cart | **view_item** |

`dealcosmetics.co.il`'s hand-named `Scroll_25%` / `Scroll_75%` / `Timer_10sec` events
are worth noting: somebody configured engagement tracking by hand and never wired the
product view.

## Two placeholder measurement IDs

Read straight off the request, no click involved, so these do not depend on the cart
gate:

- **`chilla.co.il`** sends **`G-12345`** alongside its real `G-D8S6XS1FRG`
- **`myonejewelry.com`** sends **`G-123456789`** alongside its real `G-X9SJ4TT256`

A tag firing into a non-existent property is data thrown away. Both stores also verify
the `G-` regex fix recorded in `../adlib-shortlist-evidence.md` — these are *live hits
carrying the id*, not CSS tokens.

Separately, **17 stores send to more than one GA4 property**. That is not a fault by
itself (a second property is often a legitimate roll-up) and it is not scored.

## The top of the pool by ad count

Sorted on `ads_seen` in `adlib-ranked.csv`, with the event verdict beside it:

| Domain | Ads | Verdict |
|---|---:|---|
| `agalease-baby.co.il` | 27 | UNKNOWN — cart button not found |
| `nutrid.co.il` | 27 | UNKNOWN — cart button not found |
| **`goom.co.il`** | **27** | **`view_item`, no `add_to_cart`** |
| `sabonmichal.co.il` | 25 | ECOMMERCE CONFIRMED |
| `anipet.co.il` | 23 | UNKNOWN — cart button not found |
| `nano-jewelry.co.il` | 21 | UNKNOWN — click failed |
| `marsportwear.com` | 17 | ECOMMERCE CONFIRMED |

**An earlier draft of this file claimed the biggest advertisers all had working
tracking. That was false** — `marsportwear.com` is seventh, and `goom.co.il` sits at
the joint-highest ad count with a verified gap. Recorded here because the claim was
already written down once.

What the table actually supports: **most of the highest-spending stores are UNKNOWN**,
because the walk could not find their cart button. That is a scanner limit and nothing
follows from it about their tracking. Only two of the top seven are confirmed either
way.

One caveat on the ad counts themselves: per `adlib-harvest-method`, a category sweep
returns **floors**, and it flatters small advertisers systematically. A store showing
"1 ad" may be running twenty. **Re-query each shortlisted brand by name before
believing its count** — including the ones at the top of this table.

## A coverage hole in the batch

`adlib-ranked.csv` holds 84 rows; `toolchain/adlib-domains.txt` holds 87 domains, and
the two sets are **not the same**. Three of the highest-ad-count advertisers —
`agalease-baby.co.il`, `anipet.co.il`, `keflahayot.co.il` — are ranked but were never
in the domains file, so the batch never touched them. Scanned separately into
`adlib-events-extra.jsonl`: two UNKNOWN (cart button not found), and
`keflahayot.co.il` did not render at all. **Reconcile the two files before the next
run.**

## Two retracted runs

Kept as `-v1` and `-v2` so the correction is auditable, not to be read as results.

- **v1** reported 39 stores with "no product URL". That was the scanner: an in-browser
  `fetch()` returned a Promise (`awaitPromise` is off) and silently fell through;
  Hebrew Shopify handles (`/products/פאוץ-רוני-...`) and Magento stores with bare
  `.html` slugs were both unfindable. Fixed by resolving product URLs over HTTP through
  `scan-dtc.py`'s `curl`, plus a selector-driven DOM scan (`a.product-item-link`,
  JSON-LD `@type: Product`).
- **v2** reported **29 stores with a measurement gap**. That number was wrong. The
  script recorded that it *clicked* a button, never that the cart changed. On
  `nano-jewelry.co.il` it clicked a real `הוספה להזמנה` and the cart stayed at 0.
  Adding the cart gate cut 29 confirmed gaps to **11**.

Had v2 shipped, the line *"your add-to-cart isn't tracked"* would have been false on an
unknown fraction of 29 businesses — the same failure as the seven burned scripts in
`../adlib-shortlist-evidence.md`.

## What this still cannot tell you

- **`purchase`** — needs a real order. Never attempted, never inferred.
- **Meta events** — no `/tr` fires under headless Chrome anywhere in this pool, while
  Tag Assistant in real Chrome shows pixel `2728102930842213` firing on
  `marsportwear.com`. Cause not established. Meta pixels are therefore reported as
  *initialised*, and their events as *unobserved* — **never as absent**. Confirm the
  Meta half in a real browser with Tag Assistant.
- **Server-side tagging** (CAPI, sGTM) leaves the server, not the browser.
- **Whether a tag is paused.** A paused tag and an absent one look identical.
