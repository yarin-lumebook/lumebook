"""One dossier per selected Reel (top 100 + 20 comparisons) for the coders, plus metrics.json used by the dataset.

Metrics rules (see README "Metrics"):
- views = play_count, the number Instagram shows on the Reels grid (checked 09 Nov 2026: DfCiXqEoqWg grid 104K =
  play_count 104,438; ig_play_count 103,563). It includes Facebook plays when the Reel was cross-posted.
- likes, comments, shares (reshare_count, the number under the paper plane on the Reel page; DNWIV26oabB page showed
  1,973 = reshare_count) and reposts (media_repost_count) are Instagram-side counts.
- Interaction ratios use ig_play_count as the denominator (likes and comments are Instagram-only).
- Shares are treated as not comparable before 2024-11-01: Reels with millions of views posted earlier show 0 to 5,
  which suggests the counter was not filled back (inference, not documented by Instagram).
- views_per_day = views / days live at collection (2026-11-09 12:00 UTC); descriptive only.
"""
import json, datetime, os
COLLECTED = datetime.datetime(2026, 11, 9, 12, tzinfo=datetime.UTC)
SHARES_FROM = datetime.datetime(2024, 11, 1, tzinfo=datetime.UTC)
info = json.load(open('media_info_2026-11-09.json'))
cm = json.load(open('comments_2026-11-09.json'))
inv = json.load(open('inventory.json'))
rank_all = {x['code']: x['rank_all'] for x in inv['clips']}
pins_grid = {x['code']: x['pinned'] for x in inv['clips']}
bycode = {v['code']: v for v in info.values()}
top = [l.strip() for l in open('top100_codes.txt') if l.strip()]
pairs = json.load(open('comparisons.json'))['pairs']
cmp_of = {p['top']: p['cmp'] for p in pairs}
top_of = {p['cmp']: p for p in pairs}
os.makedirs('dossiers', exist_ok=True)
metrics = {}
def r(a, b, k=1000):
    return round(a * k / b, 2) if (a is not None and b) else None
for group, codes in (('top', top), ('comparison', [p['cmp'] for p in pairs])):
    for code in codes:
        x = bycode[code]
        t = datetime.datetime.fromtimestamp(x['taken_at'], datetime.UTC)
        days = (COLLECTED - t).total_seconds() / 86400
        ig = x.get('ig_play')
        shares_ok = t >= SHARES_FROM
        m = {
            'code': code, 'group': group, 'rank_top100': top.index(code) + 1 if group == 'top' else None,
            'rank_all_reels': rank_all.get(code), 'url': f'https://www.instagram.com/reel/{code}/',
            'published_utc': t.strftime('%Y-%m-%d %H:%M'), 'collected': '2026-11-09', 'days_live': round(days, 1),
            'duration_s': round(x['dur'], 1),
            'views_grid': x['play'], 'ig_views': ig, 'fb_views': x.get('fb_play'),
            'likes': x['likes'], 'comments': x['comments'],
            'shares': x.get('reshare') if shares_ok else None, 'shares_raw': x.get('reshare'), 'shares_comparable': shares_ok,
            'reposts': x.get('reposts'),
            'likes_per_1k_ig_views': r(x['likes'], ig), 'comments_per_1k_ig_views': r(x['comments'], ig),
            'shares_per_1k_ig_views': r(x.get('reshare'), ig) if shares_ok else None,
            'views_per_day': round(x['play'] / days) if days > 0 else None,
            'owner': x.get('owner'), 'coauthors': x.get('coauthors') or [], 'collab': x.get('owner') != 'matan.nistor' or bool(x.get('coauthors')),
            'paid_partnership_label': bool(x.get('paid')), 'sponsor_tags': x.get('sponsors') or [],
            'pinned_reels_tab': bool(x.get('clips_pinned')), 'pinned_profile_grid': bool(x.get('timeline_pinned')),
            'audio_type': x.get('audio_type'), 'music': x.get('music'), 'original_sound_title': (x.get('orig_sound') or {}).get('title'),
            'usertags': x.get('usertags') or [], 'location': x.get('location'), 'caption_edited': x.get('caption_edited'),
            'pair': cmp_of.get(code) if group == 'top' else top_of[code]['top'],
        }
        metrics[code] = m
        c = cm.get(x['pk'], {'comments': [], 'replies': [], 'pages': 0})
        dossier = dict(m)
        dossier['caption'] = x.get('caption')
        if group == 'comparison':
            dossier['pair_match_note'] = top_of[code]['match_note']
        dossier['comments_sample'] = {
            'how': 'First 3 pages (up to ~42) of top-level comments in the order the Instagram web comments endpoint returns them for a signed-in viewer (not sorted by likes or date); up to 5 replies under each of the first 3 comments that had replies. Commenter handles not stored. own = written by @matan.nistor.',
            'pages': c.get('pages'), 'n': len(c['comments']),
            'comments': [{'t': k['t'], 'likes': k['l'], 'replies': k['r'], 'own': k['own'],
                          'date': datetime.datetime.fromtimestamp(k['at'], datetime.UTC).strftime('%Y-%m-%d')} for k in c['comments']],
            'replies_sampled': [{'t': k['t'], 'own': k['own'], 'likes': k['l']} for k in c['replies']],
        }
        json.dump(dossier, open(f'dossiers/{code}.json', 'w'), ensure_ascii=False, indent=1)
json.dump(metrics, open('metrics.json', 'w'), ensure_ascii=False, indent=1)
print('dossiers', len(metrics))
