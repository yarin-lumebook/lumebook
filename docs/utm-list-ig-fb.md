# UTM list for Instagram and Facebook

Source of the values: `research/cro-crm/measurement.md` section 4 (taxonomy), `research/carousel-audit/src/audit.py` lines 473 to 479 (what the link maker builds). Rules: lowercase, hyphens instead of spaces, no personal details in a link.

**What makes an order yours:** `utm_medium=social`. Nothing else counts toward your 25%.

## Your links (these count)

Replace `<topic>` with the carousel topic (for example `pacifier-weaning`) and `YYYYMMDD` with the day the link goes out. Add the page address before the `?`.

| Where the link goes | Add to the end of the link |
|---|---|
| Instagram DM (after a comment word) | `?utm_source=instagram&utm_medium=social&utm_campaign=car-<topic>&utm_content=dm-YYYYMMDD` |
| Instagram story link sticker | `?utm_source=instagram&utm_medium=social&utm_campaign=car-<topic>&utm_content=story-YYYYMMDD` |
| Instagram bio | `?utm_source=instagram&utm_medium=social&utm_campaign=car-<topic>&utm_content=bio` |
| Facebook post or comment | `?utm_source=facebook&utm_medium=social&utm_campaign=car-<topic>&utm_content=post-YYYYMMDD` |
| Any of the above, when testing two versions | add `&utm_term=a` or `&utm_term=b` |

The dashboard link maker (Course tab, "Copy and log") builds all four rows for you, including Facebook with the `post-` placement (`sites/dashboard/course/course.js` lines 37 to 38). The Python `audit.py link` tool only knows Instagram; use the dashboard. Whether Yossi has agreed the `post-` value is not recorded in `measurement.md`.

## Not yours (never use these on your links)

| Traffic | `utm_medium` | Who tags it |
|---|---|---|
| Creator links | `creator` | the creator plan |
| Meta ads | `paid-social` | Yossi, in Ads Manager |
| Parent groups | `community` | whoever posts there |
| Store WhatsApp, SMS, email | `crm` | the store |

If an ad or a creator link goes out with `social`, your sales get mixed with theirs. Ask Yossi that ads never use `social`.

## Check every link before sending

1. Open it on your phone. The right page opens.
2. The end of the address still shows `?utm_`. Extra bits like `fbclid` are fine.

## Known gaps

- Instagram adds its own tag to the bio link (`utm_source=ig&utm_medium=social&utm_content=link_in_bio`, no campaign). Use your full tagged link in the bio.
- Links made before 1 Nov may carry `utm_medium=dm`, `bio` or `story`. That is the old format, not a mistake.
