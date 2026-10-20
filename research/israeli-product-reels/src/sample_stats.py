#!/usr/bin/env python3
"""Counts behind playbook.md section 1 ("What the Reels show"), recomputed from the coded sample.

    python3 research/israeli-product-reels/src/sample_stats.py          # print
    python3 research/israeli-product-reels/src/sample_stats.py --json   # also write src/sample_stats.json

Reads src/review.json (verified Reels only), src/coded/CODE.json, src/media_info_15oct.json and
media/projects/2026-10-15-israeli-product-reels/analysis/CODE/index.json (durations, when present).
Every number here is observed in the coding; interpretation stays in the playbook.
"""
import collections
import json
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.normpath(os.path.join(HERE, '../../../media/projects/2026-10-15-israeli-product-reels/analysis'))

R = json.load(open(os.path.join(HERE, 'review.json'), encoding='utf-8'))
INFO = json.load(open(os.path.join(HERE, 'media_info_15oct.json'), encoding='utf-8'))
V = [k for k, r in R.items() if not k.startswith('_') and r['status'] == 'verified']
EXC = [k for k, r in R.items() if not k.startswith('_') and r['status'] == 'excluded']
C = {k: json.load(open(os.path.join(HERE, 'coded', f'{k}.json'), encoding='utf-8')) for k in V}


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def dur(k):
    p = os.path.join(MEDIA, k, 'index.json')
    if os.path.exists(p):
        return json.load(open(p))['duration']
    return INFO.get(k, {}).get('duration_s')


def text(k, *fields):
    return ' '.join(str(C[k].get(f) or '') for f in fields).lower()


def has_child(k):
    v = str(C[k].get('child_on_camera', '')).lower()
    if v:
        return v.startswith('yes')
    t = text(k, 'solo_without_child')
    return t.startswith('no') or t.startswith('partly')


def cta_kinds(k):
    ct = C[k].get('cta_type')
    if isinstance(ct, list) and ct:
        m = {'comment_word': 'comment', 'code': 'code', 'link_in_bio': 'link_in_bio', 'follow': 'follow', 'dm': 'dm',
             'save_or_share': 'save_or_share', 'website': 'website', 'none': 'none'}
        return {m.get(x, x) for x in ct}
    t = text(k, 'ending_and_cta', 'price_or_code')
    kinds = set()
    if re.search(r'comment|הגיב|תגיב|כתבו|כתבי|תכתב|keyword|comment word|comment-word', t):
        kinds.add('comment')
    if re.search(r'code|קוד|coupon|קופון', t):
        kinds.add('code')
    if re.search(r'bio|ביו', t):
        kinds.add('link_in_bio')
    if re.search(r'follow|עקב', t):
        kinds.add('follow')
    return kinds or {'none'}


def price_shown(k):
    v = str(C[k].get('price_on_screen', '')).strip().lower()
    if v:
        return not v.startswith('no')
    return bool(re.search(r'₪|ש"ח|ש״ח|nis|shekel|\d+\s*שקל', text(k, 'price_or_code', 'selling_language')))


GROUP = {'personalised_book': 'personalised books', 'childrens_book': "children's books", 'toy_game': 'toys, games, learning',
         'educational': 'toys, games, learning', 'parenting_product': 'parenting products', 'other': 'parenting products', 'gift': 'gifts'}

s = {}
s['verified'] = len(V)
s['excluded'] = len(EXC)
s['creators'] = len({INFO.get(k, {}).get('owner') or C[k].get('handle') for k in V})
s['groups'] = dict(collections.Counter(GROUP.get(C[k].get('category'), 'other') for k in V))
fs = [num(C[k].get('product_first_seen_s')) for k in V]
s['product_by_2s'] = sum(1 for x in fs if x is not None and x <= 2)
s['product_by_5s'] = sum(1 for x in fs if x is not None and x <= 5)
s['product_after_5s'] = sorted([(k, x) for k, x in zip(V, fs) if x is not None and x > 5], key=lambda t: -t[1])
s['no_onscreen_text'] = [k for k in V if str(C[k].get('captions_on_screen', '')).lower().startswith('none')]
s['speech'] = dict(collections.Counter(str(C[k]['audio'].get('speech', '')).split(';')[0].split(' (')[0] for k in V))
d = [x for x in (dur(k) for k in V) if x]
s['duration_median_s'] = round(st.median(d), 1)
s['duration_le_30'] = sum(1 for x in d if x <= 30)
s['duration_gt_60'] = sum(1 for x in d if x > 60)
s['cta'] = dict(collections.Counter(x for k in V for x in cta_kinds(k)))
s['collab_posts'] = sum(1 for k in V if INFO.get(k, {}).get('coauthors'))
s['paid_label'] = sum(1 for k in V if INFO.get(k, {}).get('paid_partnership_label'))
s['disclosure_words'] = sum(1 for k in V if re.search(r'בשיתוף|שת"פ|שת״פ|ugc|ממומן|פרסום', str(R[k].get('disclosure', '')) + str(C[k].get('disclosure_visible', '')), re.I))
plays = [INFO[k]['plays'] for k in V if INFO.get(k, {}).get('plays')]
s['plays_median'] = int(st.median(plays)) if plays else None
s['plays_top5'] = sorted(((INFO[k]['plays'], k, INFO[k].get('owner')) for k in V if INFO.get(k, {}).get('plays')), reverse=True)[:5]
pb = [k for k in V if C[k].get('category') == 'personalised_book']
s['pb_n'] = len(pb)
s['pb_brands'] = dict(collections.Counter(str(C[k].get('brand') or INFO.get(k, {}).get('coauthors') or '?') for k in pb))
s['pb_child_on_camera'] = sum(1 for k in pb if has_child(k))
s['pb_price_shown'] = sum(1 for k in pb if price_shown(k))
s['pb_code'] = sum(1 for k in pb if 'code' in cta_kinds(k))
pbp = sorted(INFO[k]['plays'] for k in pb if INFO.get(k, {}).get('plays'))
s['pb_plays'] = pbp
s['price_on_screen_all'] = sum(1 for k in V if price_shown(k))
s['price_in_caption_all'] = sum(1 for k in V if str(C[k].get('price_in_caption', 'no')).strip().lower()[:2] not in ('no', ''))
s['child_on_camera_all'] = sum(1 for k in V if has_child(k))
s['no_face_no_child'] = sum(1 for k in V if not has_child(k) and str(C[k].get('face_on_camera', '')).lower().startswith('no face'))
s['screen_recording'] = sum(1 for k in V if str(C[k].get('screen_recording', '')).lower().startswith('yes'))
s['pb_likeness'] = dict(collections.Counter(str(C[k].get('likeness_proof', '?')) for k in pb))
s['pb_screen_recording'] = sum(1 for k in pb if str(C[k].get('screen_recording', '')).lower().startswith('yes'))
s['comment_word_reels'] = sum(1 for k in V if 'comment' in cta_kinds(k))
s['comment_words'] = dict(collections.Counter(str(C[k].get('comment_word')) for k in V if C[k].get('comment_word') not in (None, 'none')))
s['by_source'] = dict(collections.Counter((R[k].get('round', 1)) for k in V))
s['top_brands_r2'] = dict(collections.Counter(INFO.get(k, {}).get('coauthors', '').split('+')[-1] or 'none' for k in V if R[k].get('round') == 2).most_common(8))
s['approaches'] = dict(collections.Counter(R[k].get('approach', '') for k in V))

for k, v in s.items():
    print(f'{k}: {v}')
if '--json' in sys.argv:
    json.dump(s, open(os.path.join(HERE, 'sample_stats.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
