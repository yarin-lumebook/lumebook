# Hanukkah and Black Friday 2026 content

18 Nov 2026. Yarin: "i need black friday and hanukkah content - purchase intent, related questions, hooks". Same day: "https://lumebook.com/IL/he/holiday-cards this is for hanukkah, black friday is just awerness for the regular deal". So every Hanukkah piece leads to the free gift page (a personal greeting card or a five-page colouring booklet with the child, plus a holiday code for a printed book on the same page; `shared/facts.json` `gift_pages.hanukkah-free-gift`), and Black Friday only reminds people of the regular deal (₪119 instead of ₪149, one shipping charge for several books the same day).

| File | What it is |
|---|---|
| `hanukkah.md` | Hanukkah, in Hebrew: the free gift and the book code, dates and delivery windows, what is already planned, Google findings, 14 purchase intents (same columns and labels as `research/mebook-customer-research/purchase-intents.md`), related questions with answers, and hooks for reels, test carousels, child-voice carousels, Facebook and stories |
| `black-friday.md` | Black Friday and Cyber Monday, in Hebrew, the same seven sections: the regular deal, 5 purchase intents, questions and hooks |
| `hanukkah.html`, `black-friday.html` | One page for each, built from the md by `build.py` (`python3 tools/lumebook.py build hanukkah-black-friday-2026`); never edited by hand |
| `sources/google-suggest-2026-11-18.json` | Raw Google autocomplete (hl=he, gl=il) for 41 Hebrew seed queries about Hanukkah gifts, gelt and Black Friday, read 18 / 11 / 2026. Shows what people type, not how often |
| `sources/google-suggest-2026-11-18-cards.json` | The same for 24 more seeds about greetings, cards, colouring pages and Black Friday books, read later the same day |

Facts come from `shared/facts.json` (key dates, last order day 05 / 12, regular price), the live store pages read on 18 / 11 / 2026 (the holiday-cards page and its FAQ, book 86, delivery, group prices for kindergartens and companies), the MeBook customer study and `research/mebook-hooks/`. Every hook passed `carousel/carousel-pipeline/scripts/voice_lint.py`; reel hooks keep the reel rules (8 words, 34 characters, no price, sale or digital copy).

Open items for Yarin are in section 7 of each md (price outside reels, the ₪99 code next to the ₪119 deal, pointing the planned Hanukkah pieces at the gift page, a real gift to film, kindergarten orders, delivery to another address, business days).
