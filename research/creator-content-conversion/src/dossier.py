import json, os, datetime
BASE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(BASE, 'sample.json')))
C = {c['h']: c for c in json.load(open('/Users/yarinbruner/Claude/Projects/Lumebook/creators/creator-research/src/C_all.json'))}
os.makedirs(os.path.join(BASE, 'dossiers'), exist_ok=True)
import sys
ONLY = set(sys.argv[1].split(',')) if len(sys.argv) > 1 else None
for u, r in S.items():
    if ONLY and u not in ONLY:
        continue
    posts = []
    brk = [q for q in r['posts'] if q['set'] == 'breakout']
    brk.sort(key=lambda q: -((q.get('rel_plays') if q['format'] == 'reel' else q.get('rel_likes')) or 0))
    keep_brk = {q['code'] for q in brk[:3]}
    for q in r['posts']:
        if q['set'] not in ('sample', 'breakout') or (q['set'] == 'breakout' and q['code'] not in keep_brk):
            continue
        d = os.path.join(BASE, 'media', u, q['code'])
        meta = {}
        if os.path.exists(os.path.join(d, 'meta.json')):
            meta = json.load(open(os.path.join(d, 'meta.json')))
        sheets = [s for s in (meta.get('sheets') or []) if s and os.path.exists(s)]
        posts.append(dict(
            code=q['code'], url=f"https://www.instagram.com/p/{q['code']}/", set=q['set'], format=q['format'],
            date=datetime.datetime.fromtimestamp(q['t']).strftime('%Y-%m-%d'), age_days=round(q['age_d'], 1),
            likes=None if q['hid'] else q['likes'], comments=q['com'], plays=q.get('plays'), reposts=q.get('rep'),
            rel_plays=q.get('rel_plays') and round(q['rel_plays'], 2), rel_likes=q.get('rel_likes') and round(q['rel_likes'], 2),
            rel_comments=q.get('rel_com') and round(q['rel_com'], 2),
            caption=q.get('cap'), alt=q.get('alt'), location=q.get('loc'), tags=q.get('tags'), paid_label=q.get('paid'),
            sponsor_tags=q.get('spons'), coauthors=q.get('coa'), owner=q.get('owner'), pinned=q.get('pin'),
            audio=q.get('aud'), audio_title=q.get('audt'), duration_s=meta.get('duration_s'),
            n_slides=q.get('ncar'), sheets=sheets))
    c = C.get(u, {})
    prof = r.get('prof') or {}
    dos = dict(handle=u, followers_14oct=prof.get('fc'), bio=prof.get('bio'), category=prof.get('cat'),
               map_archetype=c.get('arch'), map_role=c.get('role'), map_topics=c.get('topics'),
               window=r['window'], baseline_by_format=r['base'], posts=posts)
    json.dump(dos, open(os.path.join(BASE, 'dossiers', u + '.json'), 'w'), ensure_ascii=False, indent=1)
    print(u, len(posts), sum(1 for p in posts if p['sheets']))
