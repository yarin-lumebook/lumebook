"""Weekly refresh, comments step: which reels to read, what the comments say, and purchase signals per creator.

    python3 comments.py todo <collected.json> [--cap 1500] [--per 12]  print the reel codes for comments.js (JSON array)
    python3 comments.py ingest <exported.json>                          store what comments.js read, label it by rules
    python3 comments.py cand <dir> [--batch 350]                        write the comments to check: <dir>/in/NNN.json
    python3 comments.py apply <dir>                                     read the checked labels from <dir>/out/NNN.json
    python3 comments.py stats                                            what the cache holds
    (any command takes --cache <file> for a test run; default cache/comments.json, not in git)

collected.json is what collect.js leaves in localStorage.__rf_out; each profile's `rl` lists its 12 newest reels as
[code, day, views, likes, comments]. todo picks each creator's `per` newest reels that have comments and are not read
yet, creators with nothing read first, up to `cap` reels a run (the rest wait for next week). comments.js reads the
first page of each (up to 15): 12 reels of about 15 comments, like the 14 Oct research's 12 posts.

Labels use the same rules as the 14 Oct 2026 research (research/creator-content-conversion/round2/classify.py): the
creator's own comments and requests for the post's offer (comment word, free file) are not purchase signals; a broad
net picks the comments that might be, and a reader checks them (VERIFY_BRIEF.md). Until a post is checked its rule
labels stand in. Purchase signals = product questions + wanting to buy + saying they bought, per 100 audience comments
(everyone but the creator), the same rate as round2/kpi.py.

Only what the numbers need is kept: no commenter names; a post's comment text is dropped once it is checked.
"""
import json, os, sys, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, 'research', 'creator-content-conversion', 'round2'))
import classify  # noqa: E402  (the research's own rules, so the weekly numbers match the 14 Oct ones)

SIGNALS = ('product_q', 'intent', 'purchase')
OWNER = '__owner__'


def opt(args, name, default):
    return args[args.index(name) + 1] if name in args else default


def load(path):
    if os.path.exists(path):
        return json.load(open(path, encoding='utf-8'))
    return {'posts': {}, 'pending': {}}


def save(db, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    json.dump(db, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    os.replace(tmp, path)


def window(x, n):
    """A profile's newest n reels from collect.js: [(code, day, views, likes, comments)], newest first."""
    return [tuple(r) for r in (x.get('rl') or [])][:n]


def post_counts(p):
    """(purchase signals, audience comments) of one stored post: checked labels when checked, rule labels until then."""
    return (p['sig'] if p.get('v') else p.get('rsig', 0)), p.get('aud', 0)


def label_post(code, p):
    """Rule labels and candidates for a post just read; a post with no candidate needs no check."""
    cm = [{'u': OWNER if own else '', 't': t} for own, t in p['cm']]
    cand, rule = classify.candidates(OWNER, p.get('cap') or '', cm)
    p['aud'] = sum(1 for l in rule if l != 'creator')
    p['rsig'] = sum(1 for l in rule if l in SIGNALS)
    p['cand'] = cand
    if not cand:                      # nothing that could be a purchase signal: done, keep no text
        p.update(v=1, sig=0); p.pop('cm', None); p.pop('cap', None); p.pop('cand', None)


def cmd_todo(args, cache):
    raw = json.load(open(args[0], encoding='utf-8'))
    cap, per = int(opt(args, '--cap', 1500)), int(opt(args, '--per', 12))
    db = load(cache)
    # a creator read this run keeps only reels still among its 12 newest: older ones no longer count
    keep = {r[0] for x in raw.values() for r in window(x, 12)}
    read = {h for h, x in raw.items() if not x.get('err')}
    db['posts'] = {c: p for c, p in db['posts'].items() if c in keep or p['h'] not in read}
    have = {}
    for c, p in db['posts'].items():
        have.setdefault(p['h'], 0); have[p['h']] += 1
    rows = []
    for h, x in raw.items():
        if x.get('err') or x.get('priv'):
            continue
        new = [r for r in window(x, per) if (r[4] or 0) > 0 and r[0] not in db['posts']]
        for i, r in enumerate(new):
            rows.append((1 if have.get(h) else 0, i, h, r))   # creators with nothing read yet first, then each one's newest
    rows.sort(key=lambda t: (t[0], t[1]))
    rows = rows[:cap]
    db['pending'] = {r[0]: [h, r[1]] for _, _, h, r in rows}
    save(db, cache)
    print(json.dumps([r[0] for _, _, _, r in rows], separators=(',', ':')))
    print('%d reels to read for %d creators (%d already stored)' % (len(rows), len({t[2] for t in rows}), len(db['posts'])), file=sys.stderr)


def cmd_ingest(args, cache):
    got = json.load(open(args[0], encoding='utf-8'))
    db = load(cache); today = datetime.date.today().isoformat(); n = c0 = 0
    for code, p in got.items():
        hd = db['pending'].get(code)
        if not hd:
            continue                  # not asked for in this run's todo
        rec = {'h': hd[0], 'd': hd[1], 'at': today, 'tot': p.get('tot'), 'cap': (p.get('cap') or '')[:800], 'cm': p.get('cm') or []}
        label_post(code, rec)
        db['posts'][code] = rec; n += 1; c0 += len(rec.get('cand') or [])
    save(db, cache)
    print('stored %d reels, %d comments to check' % (n, c0))


def cmd_cand(args, cache):
    out = args[0]; size = int(opt(args, '--batch', 350))
    db = load(cache)
    os.makedirs(os.path.join(out, 'in'), exist_ok=True); os.makedirs(os.path.join(out, 'out'), exist_ok=True)
    batches, cur, k = [], [], 0
    for code, p in sorted(db['posts'].items()):
        if p.get('v') or not p.get('cand'):
            continue
        item = {'c': code, 'cap': (p.get('cap') or '')[:300], 'cm': [{'i': i, 't': p['cm'][i][1]} for i in p['cand']]}
        if cur and k + len(item['cm']) > size:
            batches.append(cur); cur, k = [], 0
        cur.append(item); k += len(item['cm'])
    if cur:
        batches.append(cur)
    for i, b in enumerate(batches, 1):
        json.dump(b, open(os.path.join(out, 'in', '%03d.json' % i), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('%d batches, %d comments to check, in %s/in (labels go to %s/out with the same name)' % (
        len(batches), sum(len(x['cm']) for b in batches for x in b), out, out))


def cmd_apply(args, cache):
    d = args[0]; db = load(cache); done = sig = 0; missing = []
    for f in sorted(glob.glob(os.path.join(d, 'in', '*.json'))):
        of = os.path.join(d, 'out', os.path.basename(f))
        if not os.path.exists(of):
            missing.append(os.path.basename(f)); continue
        labs = {}
        for x in json.load(open(of, encoding='utf-8')):
            if x.get('l') in SIGNALS:
                labs[(x['c'], int(x['i']))] = x['l']
        for item in json.load(open(f, encoding='utf-8')):
            p = db['posts'].get(item['c'])
            if not p or p.get('v'):
                continue
            ok = {int(c['i']) for c in item['cm']}
            s = sum(1 for (c, i), l in labs.items() if c == item['c'] and i in ok)
            p.update(v=1, sig=s); p.pop('cm', None); p.pop('cap', None); p.pop('cand', None)
            done += 1; sig += s
    save(db, cache)
    print('checked %d reels, %d purchase signals%s' % (done, sig, ('; no labels yet for ' + ', '.join(missing)) if missing else ''))


def cmd_stats(args, cache):
    db = load(cache); P = db['posts']
    print('reels %d, checked %d, waiting for a check %d, creators %d' % (
        len(P), sum(1 for p in P.values() if p.get('v')), sum(1 for p in P.values() if not p.get('v')), len({p['h'] for p in P.values()})))


def creator_kpi(cache, h, codes, n=12):
    """Purchase signals for one creator over its newest n stored reels among `codes` (its current 12 newest)."""
    db = load(cache) if isinstance(cache, str) else cache
    ps = sorted((p for c, p in db['posts'].items() if p['h'] == h and c in codes), key=lambda p: p['d'], reverse=True)[:n]
    if not ps:
        return None
    sig = aud = 0
    for p in ps:
        s, a = post_counts(p); sig += s; aud += a
    return {'sig': sig, 'aud': aud, 'posts': len(ps), 'at': max(p['at'] for p in ps), 'checked': all(p.get('v') for p in ps)}


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] not in ('todo', 'ingest', 'cand', 'apply', 'stats'):
        sys.exit(__doc__)
    cache = opt(a, '--cache', os.path.join(HERE, 'cache', 'comments.json'))
    a = [x for i, x in enumerate(a) if x != '--cache' and (i == 0 or a[i - 1] != '--cache')]
    {'todo': cmd_todo, 'ingest': cmd_ingest, 'cand': cmd_cand, 'apply': cmd_apply, 'stats': cmd_stats}[a[0]](a[1:], cache)
