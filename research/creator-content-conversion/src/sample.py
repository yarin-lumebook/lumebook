"""Build the post sample from raw/*.json (one file per creator, collected 14 Oct 2026).

Rules (written up in methodology.md):
- Eligible = feed post (reel, carousel, single image) the creator owns or co-authored,
  published 7 to 90 days before the creator's observation time. Posts under 7 days old
  are logged but kept out of the baseline (metrics still growing).
- Up to 12 most recent eligible posts (consecutive by date). If the 90-day window gives
  fewer than 6, extend to 180 days to reach up to 12 and label the creator window "180d".
- Older breakouts: posts older than the window (or pinned) in the fetched pages whose
  plays (reels) or likes (other formats) are at least 5x the creator's in-sample median
  for the same format. Analysed separately.
"""
import json, glob, os, statistics, datetime, re

RAW = os.path.join(os.path.dirname(__file__), 'raw')
DAY = 86400

def fmt(p):
    if p['pt'] == 'clips' or p['mt'] == 2:
        return 'reel'
    if p['pt'] == 'carousel_container' or p['mt'] == 8:
        return 'carousel'
    return 'image'

def load():
    out = {}
    for f in sorted(glob.glob(os.path.join(RAW, '*.json'))):
        d = json.load(open(f))
        out[d['username']] = d
    return out

def build(d):
    obs = d['at']
    u = d['username']
    seen = set(); posts = []
    for p in d['posts']:
        if p['code'] in seen:
            continue
        seen.add(p['code'])
        q = dict(p)
        q['format'] = fmt(p)
        q['age_d'] = (obs - p['t']) / DAY
        pl = d['plays'].get(p['code']) or {}
        q['plays'] = pl.get('pc') if q['format'] == 'reel' else None
        q['own'] = (p.get('owner') == u) or (u in (p.get('coa') or []))
        posts.append(q)
    posts.sort(key=lambda q: -q['t'])
    elig = lambda q, lo, hi: q['own'] and lo <= q['age_d'] <= hi
    win = '90d'
    s = [q for q in posts if elig(q, 7, 90)]
    if len(s) < 6:
        win = '180d'
        s = [q for q in posts if elig(q, 7, 180)]
    s = s[:12]
    codes = {q['code'] for q in s}
    oldest_in = min((q['t'] for q in s), default=obs)
    # baselines per format inside the sample
    base = {}
    for f in ('reel', 'carousel', 'image'):
        fs = [q for q in s if q['format'] == f]
        if not fs:
            continue
        likes = [q['likes'] for q in fs if q['likes'] is not None and not q['hid']]
        coms = [q['com'] for q in fs if q['com'] is not None]
        plays = [q['plays'] for q in fs if q['plays']]
        base[f] = dict(n=len(fs), likes=statistics.median(likes) if likes else None,
                       com=statistics.median(coms) if coms else None,
                       plays=statistics.median(plays) if plays else None)
    for q in posts:
        q['in_sample'] = q['code'] in codes
        b = base.get(q['format'], {})
        q['rel_plays'] = (q['plays'] / b['plays']) if q.get('plays') and b.get('plays') else None
        q['rel_likes'] = (q['likes'] / b['likes']) if q['likes'] is not None and b.get('likes') and not q['hid'] else None
        q['rel_com'] = (q['com'] / b['com']) if q['com'] is not None and b.get('com') else None
        if q['in_sample']:
            q['set'] = 'sample'
        elif q['own'] and q['age_d'] < 7:
            q['set'] = 'too_recent'
        elif q['own'] and (q['t'] < oldest_in or q['pin']):
            key = q['rel_plays'] if q['format'] == 'reel' else q['rel_likes']
            q['set'] = 'breakout' if key is not None and key >= 5 else 'older'
        elif not q['own']:
            q['set'] = 'not_own'
        else:
            q['set'] = 'skipped'
    return dict(username=u, obs=obs, window=win, n=len(s), base=base, posts=posts,
                prof=d['prof'], n_fetched=len(posts))

if __name__ == '__main__':
    data = load()
    allc = {}
    for u, d in data.items():
        r = build(d)
        allc[u] = r
        sets = {}
        for q in r['posts']:
            sets[q['set']] = sets.get(q['set'], 0) + 1
        fmts = {}
        for q in r['posts']:
            if q['in_sample']:
                fmts[q['format']] = fmts.get(q['format'], 0) + 1
        print(f"{u:30} fc={r['prof'] and r['prof'].get('fc')} win={r['window']} n={r['n']} fmts={fmts} sets={sets} base={ {k:(v['plays'],v['likes'],v['com']) for k,v in r['base'].items()} }")
    json.dump(allc, open(os.path.join(os.path.dirname(__file__), 'sample.json'), 'w'), ensure_ascii=False)
