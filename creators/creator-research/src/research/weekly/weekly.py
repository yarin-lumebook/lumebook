"""Weekly creator search (every Saturday night since 24 Oct 2026): the Python steps around the in-page scripts.

    python3 weekly.py next [--date YYYY-MM-DD]     the pass number this run writes (data<N>.py, pass<N>_raw.json), and how many
                                                   creators a weekly pass already added that day (not 0: the run already happened)
    python3 weekly.py prep                         prints the javascript that sets the seeds and the known list in the Instagram tab
    python3 weekly.py shortlist <screened.json> <out dir> [--skip review.json]
                                                   drops known creators, accounts reviewed in the last 90 days, non-Hebrew and
                                                   off-topic bios; writes <out dir>/review.txt (one line per account, most
                                                   suggested first) and <out dir>/review.json
    python3 weekly.py check <read.json> [--date YYYY-MM-DD]
                                                   applies the map's rules to the profiles read.js read (public, 3+ reels, a
                                                   reel in the last 90 days, not already in the map under another handle) and
                                                   the admission bar of 24 Oct 2026 (gate.py: 5,000 to 50,000 followers, median
                                                   views 2,000+, 0.4+ views per follower, 10+ likes and 1+ comment per 1,000
                                                   views), writes ../pass<N>_raw.json with the ones that pass and prints them
                                                   for writing data<N>.py
    python3 weekly.py queue                        the handles Yarin added with the map's "הוספת יוצרים" button that wait for a
                                                   check (read only from state/settings.json main.addq), as a JSON array to add to
                                                   the read.js picks. They skip the shortlist's topic rules but not the admission bar
    python3 weekly.py requests <read.json> [--date YYYY-MM-DD]      (queue and requests take --settings <file> --req <file> for tests)
                                                   after the merge: what happened to each queued handle (added, or why not, in
                                                   Hebrew) into requests.json here, which build2.py shows in the map's add form

Run from src/research/weekly. Method and the order of the steps: README.md here.
"""
import json, os, re, sys, glob, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gate  # noqa: E402  the admission bar (shared/facts.json creators.admission)
RES = os.path.dirname(HERE)
SRC = os.path.dirname(RES)
LEDGER = os.path.join(HERE, 'reviewed.json')        # handle -> date it was last shown in a weekly review (picked or not)
REQ = os.path.join(HERE, 'requests.json')           # handle -> what happened to a creator Yarin added by hand: {r, why, d}
SETTINGS = os.path.join(os.path.dirname(SRC), 'state', 'settings.json')   # the map's saved settings (read only here)
J = lambda p: json.load(open(p, encoding='utf-8'))

def creators(): return J(os.path.join(SRC, 'C_all.json'))

def pass_no(c):
    m = re.match(r'pass(\d+)', str(c.get('extra', '')))
    return int(m.group(1)) if m else 1

def next_pass():          # only a merge changes C_all.json, so a run that stopped before its merge is redone under the same number
    return max(pass_no(c) for c in creators()) + 1

def known_handles():
    hs = {c['h'] for c in creators()}
    hs |= set(J(os.path.join(RES, 'removed-2026-10-12.json'))['handles'])
    b = open(os.path.join(SRC, 'build2.py'), encoding='utf-8').read()          # EDGE, EXCL and TRK: checked before and left out on purpose
    for blk in re.findall(r'\n(?:EDGE|EXCL|TRK)=\[(.*?)\](?=\n[A-Z])', b, re.S): hs |= set(re.findall(r'\b[a-z0-9_.]*[a-z][a-z0-9_.]*', blk))
    return hs

def known_pks(skip=None):          # skip: this run's own pass<N>_raw.json, which a second check rewrites
    pk = {c['pk'] for c in creators() if c.get('pk')}
    lt = os.path.join(SRC, 'refresh', 'latest.json')
    if os.path.exists(lt): pk |= {x['pk'] for x in J(lt)['data'].values() if x.get('pk')}
    for f in glob.glob(os.path.join(RES, 'pass*_raw.json')):
        if os.path.basename(f) != 'pass%s_raw.json' % skip: pk |= {x['pk'] for x in J(f) if x.get('pk')}
    return pk

def ledger(): return J(LEDGER) if os.path.exists(LEDGER) else {}

def twin_finder():
    # most creators added before 24 Oct have no stored pk, so a renamed one is caught by its numbers instead:
    # the same last reel day, followers within 3% and median views within 10% (art_by_shanina = shanina_advent.learn on 24 Oct 2026)
    lt = os.path.join(SRC, 'refresh', 'latest.json'); RF = J(lt)['data'] if os.path.exists(lt) else {}
    prints = [(c['h'], v['f'], v['last'], v.get('med')) for c in creators() for v in (c, RF.get(c['h'], {})) if v.get('f') and v.get('last')]
    near = lambda a, b, p: a is not None and b is not None and abs(a - b) <= p * max(a, b, 1)
    return lambda x: next((h for h, f, l, m in prints if l == x.get('last') and near(f, x['fc'], .03) and near(m, x.get('med'), .1)), None)

def queued():          # what Yarin added with the map's button, newest last; state/ is only read here
    try: q = J(SETTINGS).get('main', {}).get('addq') or []
    except Exception: q = []
    return [x for x in q if isinstance(x, dict) and x.get('h')]

HEB = re.compile('[֐-׿]')
KID = re.compile(r'ילד|ילדים|ילדה|הורות|הורים|אמא|אימא|אבא|סבתא|סבא|גן|גננת|פעוט|משפח|קלינאית|ריפוי בעיסוק|התפתחות|חינוך|מורה|ספר|קריאה|סיפור|תאומ|מונטסורי|הדרכת|טיול|אטרקצי|יצירה|פעילו|מתבגר|בייבי|תינוק|kids|mom|mama|dad|family|parent|toddler|child|book', re.I)
OFF = re.compile(r'ייעוץ שינה|יועצת שינה|הנקה|לידה|דולה|מיילד|תזונ|דיאט|משלוחים|הזמנות|למכירה|קולקציה|מבצע|חנות|עיצוב שיער|איפור|ציפורניים|נדל|ביטוח|משכנת|מאמנת כושר|פילאטיס|קייטרינג|עוגות|שמלות|בגדי|מתכונים|הריון|פוריות|IVF|איקאה|ריהוט', re.I)
one = lambda s: re.sub(r'\s+', ' ', s or '').replace('|', '/').strip()        # one line, and | stays the column separator

args = sys.argv[1:]
if not args: sys.exit(__doc__)
cmd = args[0]
opt = lambda k, d=None: args[args.index(k) + 1] if k in args else d
SETTINGS, REQ = opt('--settings', SETTINGS), opt('--req', REQ)          # other files, for a test run

if cmd == 'next':
    today = opt('--date', datetime.date.today().isoformat())
    done = sum(1 for c in creators() if c.get('added_on') == today and pass_no(c) >= 6)
    print(next_pass(), '| already added today by a weekly pass:', done)

elif cmd == 'prep':
    C = creators(); pks = {}
    lt = os.path.join(SRC, 'refresh', 'latest.json')
    if os.path.exists(lt): pks.update({h: x['pk'] for h, x in J(lt)['data'].items() if x.get('pk')})
    for f in glob.glob(os.path.join(RES, 'pass*_raw.json')): pks.update({x['h']: x['pk'] for x in J(f) if x.get('pk')})
    pks.update({c['h']: c['pk'] for c in C if c.get('pk')})
    seeds = [[c['h'], pks.get(c['h'])] for c in reversed(C)]                 # newest first
    have = sorted(known_handles())
    s = lambda v: json.dumps(json.dumps(v, separators=(',', ':')))
    print('localStorage.__cw_seeds=%s;localStorage.__cw_have=%s;[%d,%d]' % (s(seeds), s(have), len(seeds), len(have)))

elif cmd == 'shortlist':
    rows, out = J(args[1]), args[2]
    hs, pks, led = known_handles(), known_pks(), ledger()
    cut = (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
    skip = set(J(opt('--skip'))) if opt('--skip') else set()
    keep, why = [], {}
    for h, pk, n, c, f, bio, frm in rows:
        r = ('known' if h in hs or pk in pks else 'reviewed lately' if led.get(h, '') >= cut or h in skip
             else 'no Hebrew' if not HEB.search(n + bio) else 'no kids or parenting word' if not KID.search(n + ' ' + bio)
             else 'off-topic word' if OFF.search(bio + ' ' + n) else None)
        if r: why[r] = why.get(r, 0) + 1; continue
        keep.append((h, f, c, n, bio, frm))
    keep.sort(key=lambda x: -x[2])
    # a handle that shares a distinctive word with a creator in the map may be that creator renamed: marked, not dropped
    common = {'mama', 'mommy', 'family', 'kids', 'parenting', 'travel', 'official', 'israel', 'speech', 'teacher', 'coach', 'imahut', 'horut', 'life', 'momlife', 'therapy', 'yeladim', 'kinder'}
    tok = {}
    for k in hs:
        for t in re.split(r'[._\d]+', k):
            if len(t) >= 7 and t not in common: tok.setdefault(t, k)       # shorter ones are common names (cohen, moran)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'review.txt'), 'w', encoding='utf-8') as fh:
        for h, f, c, n, bio, frm in keep:
            like = next((k for t, k in tok.items() if t in h and k != h), None)
            fh.write('%s|%s|c%d|%s|%s%s\n' % (h, f, c, one(n)[:45], one(bio)[:220], ' |LIKE ' + like if like else ''))
    json.dump([x[0] for x in keep], open(os.path.join(out, 'review.json'), 'w', encoding='utf-8'))
    print('screened in range', len(rows), '| to review', len(keep), '| dropped', why)
    print('wrote', os.path.join(out, 'review.txt'))

elif cmd == 'check':
    rows, today = J(args[1]), opt('--date', datetime.date.today().isoformat())
    n = next_pass(); pks = known_pks(skip=n)
    cut = (datetime.date.fromisoformat(today) - datetime.timedelta(days=90)).isoformat()
    twin = twin_finder()
    ok, bad = [], []
    for x in rows:
        tw = None if x.get('err') else twin(x)
        r = ('did not load' if x.get('err') else 'private' if x.get('priv') else 'already in the map under another handle' if x.get('pk') in pks
             else 'probably %s, already in the map (renamed?): same last reel day and followers' % tw if tw
             else 'fewer than 3 reels' if (x.get('nr') or 0) < 3 else 'no reel since ' + cut if (x.get('last') or '') < cut else None)
        if not r and not x.get('err'):
            r, nums = gate.check(x); x.update(nums)        # followers, views, views per follower, likes and comments per 1K views
        (bad.append((x['h'], r, x.get('fc'), x.get('last'))) if r else ok.append(x))
    p = os.path.join(RES, 'pass%d_raw.json' % n)
    json.dump(ok, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('pass', n, '| read', len(rows), '| pass the rules', len(ok), '| wrote', p)
    for h, r, f, l in bad: print('  OUT', h, '|', r, '|', f, l)
    print('h | followers | median views | views/follower | likes/1K | comments/1K | max | reels | last reel | category | name | bio | links')
    for x in sorted(ok, key=lambda x: x['h']):
        ln = [re.sub(r'^https?://(www\.)?', '', l)[:50] for l in (x.get('links') or [x.get('ext')]) if l][:3]
        print('%s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s' % (x['h'], x['fc'], x['med'], x.get('vpf'), x.get('lpk'), x.get('cpk'), x['max'], x['nr'], x['last'], x.get('cat') or '', one(x.get('n'))[:40], one(x.get('bio')), ', '.join(ln)))

elif cmd == 'queue':
    have, req = {c['h'] for c in creators()}, (J(REQ) if os.path.exists(REQ) else {})
    todo = []
    for x in queued():
        h = x['h']; r = req.get(h, {}).get('r')
        if h in have or h in todo or r in ('added', 'out'): continue          # decided; a profile that did not load is tried again
        todo.append(h)
    print(json.dumps(todo))

elif cmd == 'requests':
    rows, today = {x['h']: x for x in J(args[1])}, opt('--date', datetime.date.today().isoformat())
    have, req = {c['h'] for c in creators()}, (J(REQ) if os.path.exists(REQ) else {})
    pks, twin = known_pks(), twin_finder()
    cut = (datetime.date.fromisoformat(today) - datetime.timedelta(days=90)).isoformat()
    for q in queued():
        h = q['h']
        if req.get(h, {}).get('r') in ('added', 'out'): continue
        if h in have: req[h] = {'r': 'added', 'd': today}; continue
        x = rows.get(h)
        if x is None: continue                                           # not read this run: stays waiting
        if x.get('err'): req[h] = {'r': 'err', 'why': 'הפרופיל לא נטען: לבדוק את שם המשתמש', 'd': today}; continue
        tw = twin(x)
        why = ('חשבון פרטי' if x.get('priv') else 'כבר במפה בשם אחר' if x.get('pk') in pks else 'כנראה כבר במפה בשם @%s' % tw if tw
               else 'פחות מ-3 רילס' if (x.get('nr') or 0) < 3 else 'אין רילס ב-90 הימים האחרונים' if (x.get('last') or '') < cut
               else gate.he(x))
        req[h] = {'r': 'out', 'why': why, 'd': today} if why else {'r': 'pass', 'why': 'עבר את הרף ולא נוסף בריצה הזאת', 'd': today}
    json.dump(req, open(REQ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('requests', len(req), '|', {k: sum(1 for v in req.values() if v['r'] == k) for k in ('added', 'out', 'pass', 'err')})

else:
    sys.exit(__doc__)
