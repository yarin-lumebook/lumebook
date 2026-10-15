"""Builds ../sources.csv and ../source-index.md from the coded Reels, Instagram media info and captions.

Run from anywhere: python3 research/israeli-product-reels/src/build_index.py
Inputs (all in this folder unless noted):
  coded/CODE.json          first-pass coding (agents) plus my review fields (review.json)
  review.json              my verification status per Reel: verified / partial / excluded, with notes
  media_info_15oct.json    owner, coauthors, paid label, plays, likes, comments, duration, taken_at
  followers.json           follower counts with their source
  media/projects/2026-10-15-israeli-product-reels/videos/CODE.info.json   caption (description)
"""
import csv
import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MEDIA = os.path.join(HERE, '../../../media/projects/2026-10-15-israeli-product-reels')
ACCESS = '2026-10-15'


def load(name):
    return json.load(open(os.path.join(HERE, name), encoding='utf-8'))


info = load('media_info_15oct.json')
followers = load('followers.json')
review = load('review.json')


def fmt(n):
    return f'{n:,}' if isinstance(n, int) else 'unavailable'


rows = []
for code, rv in review.items():
    if code.startswith('_'):
        continue
    c = json.load(open(os.path.join(HERE, 'coded', f'{code}.json'), encoding='utf-8'))
    m = info.get(code, {})
    cap_path = os.path.join(MEDIA, 'videos', f'{code}.info.json')
    hidden = m.get('like_and_view_counts_hidden') == 1
    pub = datetime.fromtimestamp(m['taken_at'], timezone.utc).strftime('%Y-%m-%d') if m.get('taken_at') else 'unavailable'
    f = followers.get(m.get('owner') or c.get('handle'), ['unavailable', ''])
    if m.get('coauthors'):
        rel = f"collaboration post (co-author: @{m['coauthors']})"
    else:
        rel = 'creator-posted'
    rows.append({
        'status': rv['status'],
        'code': code,
        'url': f'https://www.instagram.com/reel/{code}/',
        'handle': '@' + (m.get('owner') or c.get('handle', '')),
        'followers': f[0],
        'followers_source': f[1],
        'product': rv.get('product') or c.get('product', ''),
        'category': c.get('category', ''),
        'published_utc': pub,
        'accessed': ACCESS,
        'relationship': rel,
        'ig_paid_partnership_label': 'yes' if m.get('paid_partnership_label') else 'no',
        'disclosure': rv.get('disclosure') or c.get('disclosure_visible', ''),
        'commercial_relationship': rv.get('commercial', 'unknown'),
        'plays': fmt(m.get('plays')),
        'likes': 'hidden by creator' if hidden else fmt(m.get('likes')),
        'comments': fmt(m.get('comments')),
        'shares_saves': 'unavailable',
        'duration_s': m.get('duration_s', ''),
        'format': c.get('format', ''),
        'approach': rv.get('approach', ''),
        'relevance': rv.get('relevance') or c.get('relevance', ''),
        'why_relevant': rv.get('why', ''),
        'lesson': rv.get('lesson', ''),
        'inspected': rv.get('inspected', ''),
        'deep_dive': rv.get('deep', ''),
    })

order = {'verified': 0, 'partial': 1, 'excluded': 2}
GROUP = {'personalised_book': 0, 'childrens_book': 1, 'toy_game': 2, 'educational': 2, 'parenting_product': 3, 'other': 3, 'gift': 4}
LABEL = {0: 'Personalised books', 1: "Children's books", 2: 'Toys, games and learning products', 3: 'Parenting products', 4: 'Gifts'}
for r in rows:
    r['group'] = LABEL[GROUP.get(r['category'], 3)]
rows.sort(key=lambda r: (order[r['status']], int(r['deep_dive'] or 99), GROUP.get(r['category'], 3),
                         -int(r['plays'].replace(',', '')) if r['plays'][0].isdigit() else 0))

with open(os.path.join(ROOT, 'sources.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

ver = [r for r in rows if r['status'] == 'verified']
par = [r for r in rows if r['status'] == 'partial']
exc = [r for r in rows if r['status'] == 'excluded']
creators = sorted({r['handle'] for r in ver})

out = []
out.append('# Source index: Israeli creator product Reels\n')
out.append(f"Accessed {ACCESS}. {len(ver)} verified examples from {len(creators)} creators, {len(par)} partly inspected leads, {len(exc)} excluded. "
           'Every row is also in `sources.csv` (one row per Reel, all fields).\n')
out.append(review['_method'] + '\n')
out.append('**How to read the numbers.** Plays, likes and comments are public counts read on 15 Oct 2026 from Instagram (media info in the logged-in Claude browser pane, read only). '
           'They do not show reach, watch time, saves, shares, sales or whether a Reel was boosted as an ad. Shares and saves are not public: unavailable for every row. '
           '"Likes hidden by creator" means the creator turned like counts off. Followers come from the source named in `followers_source`.\n')
out.append('**Relationship.** "Collaboration post" means Instagram lists a brand as co-author of the Reel. "Disclosure" quotes what the caption or video says about payment or gifting. '
           'Instagram\'s paid-partnership label was off on every Reel here. Where nothing is disclosed, the commercial relationship is marked unknown.\n')


def table(rs, deep_note=True):
    t = ['| # | Reel | Creator (followers) | Group and product | Published | Relationship and disclosure | Plays / likes / comments | Approach | Why it matters for LumeBook |',
         '|---|---|---|---|---|---|---|---|---|']
    for i, r in enumerate(rs, 1):
        deep = f" **Deep dive {r['deep_dive']}.**" if (deep_note and r['deep_dive']) else ''
        t.append(f"| {i} | [{r['code']}]({r['url']}) | {r['handle']} ({r['followers']}) | {r['group']}: {r['product']} | {r['published_utc']} | "
                 f"{r['relationship']}. {r['disclosure']}. Commercial: {r['commercial_relationship']} | {r['plays']} / {r['likes']} / {r['comments']} | "
                 f"{r['approach']} | {r['why_relevant']} {r['lesson']}{deep} |")
    return '\n'.join(t) + '\n'


out.append(f'## Verified examples ({len(ver)})\n')
out.append('Watched end to end: every frame sheet (one frame per second) plus the machine transcript of the speech, the caption and the public counts. '
           'Deep dives are in `breakdowns.md`.\n')
out.append('Deep dives come first (in `breakdowns.md` order), then the rest by product group and plays.\n')
out.append(table(ver))
out.append(f'## Partly inspected leads ({len(par)})\n')
out.append('None: every Reel that downloaded was watched in full (one Reel, DbAfvCdowT3, has its last 2 of 125 seconds unchecked by the coding agent; I checked a frame at 2:03). '
           'The leads below were seen only as metadata and were not watched or counted.\n')
leads = json.load(open(os.path.join(HERE, 'leads_not_watched.json'), encoding='utf-8'))
out.append(leads['_note'] + '\n')
out.append('| Account | Post codes | What it is | Why not watched |\n|---|---|---|---|')
for a, codes, what, why in leads['rows']:
    out.append(f'| {a} | {codes} | {what} | {why} |')
out.append('')
out.append(f'## Excluded ({len(exc)})\n')
out.append('| Reel | Creator | Why excluded |\n|---|---|---|')
for r in exc:
    out.append(f"| [{r['code']}]({r['url']}) | {r['handle']} | {r['why_relevant']} |")
out.append('\nCandidates that never became Reels to watch: `DeKFbzRAmIy` (@_shirley_unger_kids_activities) and `DdwREvSCJg2` (@tal_strul) are carousels, not Reels.\n')

open(os.path.join(ROOT, 'source-index.md'), 'w', encoding='utf-8').write('\n'.join(out))
print(len(ver), 'verified,', len(creators), 'creators;', len(par), 'partial;', len(exc), 'excluded')
