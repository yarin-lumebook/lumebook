"""Pick each creator's deep-dive posts (comments + transcripts).
strong   = highest performance vs the creator's own same-format median (reels: plays; else likes),
           only formats with >= 3 posts in the sample
ordinary = same format as strong, ratio closest to 1.0 (the creator's typical post)
relevant = up to 2 more sample posts whose caption mentions a LumeBook buying occasion,
           books, gifts or a product offer (keyword match, checked by hand later)
"""
import json, os, math, re
BASE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(BASE, 'sample.json')))
KW = re.compile(r'ספר|סיפור|קריא|מתנ|יום הולדת|יומולדת|יום־הולדת|אח גדול|אחות גדולה|אח קטן|אחות קטנה|אחים|אחאים|הריון|בהריון|לידה|מוצץ|גמיל|טיטול|סיר|גננ|לגן|הגן|כיתה א|כיתה א׳|כיתה א\'|בית ספר|השכב|לפני השינה|חנוכה|סבתא|סבא|נכד|ממליצ|המלצ|קוד|הנחה|קופון|בקישור|לינק|הזמנ')
sel = {}
for u, r in S.items():
    if u == 'lumebookai':
        continue
    smp = [q for q in r['posts'] if q['set'] == 'sample']
    nfmt = {}
    for q in smp:
        nfmt[q['format']] = nfmt.get(q['format'], 0) + 1
    def score(q):
        return q['rel_plays'] if q['format'] == 'reel' else q['rel_likes']
    cands = [q for q in smp if nfmt[q['format']] >= 3 and score(q)]
    if not cands:
        cands = [q for q in smp if score(q)]
    picks = []
    if cands:
        strong = max(cands, key=score)
        picks.append((strong['code'], 'strong', round(score(strong), 2)))
        same = [q for q in smp if q['format'] == strong['format'] and q['code'] != strong['code'] and score(q)]
        if same:
            ordn = min(same, key=lambda q: (abs(math.log(score(q))), abs(q['t'] - strong['t'])))
            picks.append((ordn['code'], 'ordinary', round(score(ordn), 2)))
    chosen = {c for c, _, _ in picks}
    rel = [q for q in smp if q['code'] not in chosen and KW.search(q.get('cap') or '')]
    rel.sort(key=lambda q: -(score(q) or 0))
    for q in rel[:2]:
        picks.append((q['code'], 'relevant_kw', round(score(q) or 0, 2)))
    sel[u] = [dict(code=c, role=role, ratio=ratio,
                   pk=next(q['pk'] for q in smp if q['code'] == c),
                   format=next(q['format'] for q in smp if q['code'] == c)) for c, role, ratio in picks]
json.dump(sel, open(os.path.join(BASE, 'deep.json'), 'w'), ensure_ascii=False, indent=1)
print(sum(len(v) for v in sel.values()), 'deep posts over', len(sel), 'creators;',
      sum(1 for v in sel.values() for p in v if p['format'] == 'reel'), 'reels')
