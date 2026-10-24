"""Weekly refresh: compare what collect.js read on Instagram with the map, and write the flags the map shows.

    python3 refresh.py <collected.json> [--db <dir with outreach/*.json>] [--date YYYY-MM-DD] [--out <dir>] [--cache <comments.json>]

collected.json is the object collect.js leaves in localStorage.__rf_out (handle -> numbers).
--db is the map's state folder (creators/creator-research/state, whose outreach.json holds every handle's record) or an
older export of the outreach collection (outreach/<handle>.json files); without it the posted check cannot tell who was contacted and flags every LumeBook mention.
Writes refresh/latest.json (read by build2.py: fresh followers, median views and last reel, the flags, and `kpi`: likes
and comments per 1,000 views over the 12 newest reels, and purchase signals per 100 comments from comments.py's cache)
and a dated copy in refresh/history/. --out writes them somewhere else (a test run). C_all.json is never changed.
"""
import json, os, sys, glob, datetime, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)

args = sys.argv[1:]
if not args: sys.exit(__doc__)
raw = json.load(open(args[0], encoding='utf-8'))
db_dir = args[args.index('--db') + 1] if '--db' in args else None
today = args[args.index('--date') + 1] if '--date' in args else datetime.date.today().isoformat()
out_dir = args[args.index('--out') + 1] if '--out' in args else HERE
sys.path.insert(0, HERE)
import comments as CMS  # noqa: E402
CDB = CMS.load(args[args.index('--cache') + 1] if '--cache' in args else os.path.join(HERE, 'cache', 'comments.json'))

def kpi(h, x):
    """The card's engagement numbers: medians per reel over the 12 newest (3 at least), purchase signals over the 12
    newest reels whose comments were read (20 audience comments at least, else the box keeps the older number or says none)."""
    rl = [r for r in (x.get('rl') or []) if r[2]]
    lp = [r[3] * 1000 / r[2] for r in rl if r[3] is not None]
    cp = [r[4] * 1000 / r[2] for r in rl if r[4] is not None]
    k = {}
    if len(lp) >= 3: k['lpk'] = round(statistics.median(lp), 2)
    if len(cp) >= 3: k['cpk'] = round(statistics.median(cp), 2)
    if k: k.update(n=len(rl), d=today)
    b = CMS.creator_kpi(CDB, h, {r[0] for r in (x.get('rl') or [])})
    if b and b['aud'] >= 20:
        k.update(bs=round(b['sig'] * 100 / b['aud'], 2), cm=b['aud'], bn=b['posts'], bd=b['at'])
    return k

C = {c['h']: c for c in json.load(open(os.path.join(SRC, 'C_all.json'), encoding='utf-8'))}
OD = {}
if db_dir and os.path.exists(os.path.join(db_dir, 'outreach.json')):
    OD = json.load(open(os.path.join(db_dir, 'outreach.json'), encoding='utf-8'))
elif db_dir:
    for f in glob.glob(os.path.join(db_dir, 'outreach', '*.json')) + glob.glob(os.path.join(db_dir, '*.json')):
        try: OD[os.path.basename(f)[:-5]] = json.load(open(f, encoding='utf-8'))
        except Exception: pass

def days(a, b):
    return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days

HE_MONTHS = ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני', 'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר']

def he_date(a):                                 # 2026-08-01 -> 1 באוגוסט 2026, like build2.py's chk dates
    d = datetime.date.fromisoformat(a)
    return '%d ב%s %d' % (d.day, HE_MONTHS[d.month - 1], d.year)

out, counts = {}, {}
for h, c in C.items():
    x = raw.get(h)
    if x is None: continue                      # not read this week: keep last week's numbers out of it
    o = OD.get(h, {}); st = o.get('s') or 'new'; sent = o.get('on')
    rf = []                                     # flags are Hebrew, like the map
    if x.get('err'):                            # the profile did not load (a renamed or deleted handle does this; so, rarely, does Instagram)
        rf.append('הפרופיל לא נטען באינסטגרם: לבדוק את שם המשתמש (שונה או נמחק?)')
        out[h] = {'rf': rf}; counts['not loaded'] = counts.get('not loaded', 0) + 1; continue
    f, med, last = x.get('fc'), x.get('med'), x.get('last')
    if x.get('priv'): rf.append('החשבון פרטי עכשיו')
    if f is not None and st == 'new':
        if f < 5000: rf.append('עכשיו פחות מ-5K עוקבים (%s)' % format(f, ','))
        if f > 50000: rf.append('עכשיו יותר מ-50K עוקבים (%s)' % format(f, ','))
    if last and days(last, today) > 60: rf.append('אין רילס חדש מאז ' + he_date(last))
    if c.get('f') and f and abs(f - c['f']) / c['f'] >= 0.25:
        rf.append('העוקבים %s מ-%s ל-%s' % ('עלו' if f > c['f'] else 'ירדו', format(c['f'], ','), format(f, ',')))
    # posted check: a reel that names or tags LumeBook, newer than the first message (or any, if there is no send date).
    # template.html knows this flag by its reel link and cuts the text at ": https://", so keep the link last.
    for r in x.get('lb') or []:
        if st != 'new' and (not sent or r['day'] >= sent):
            rf.append('פרסמו רילס על LumeBook ב-%s (%s צפיות): https://www.instagram.com/reel/%s/' % (he_date(r['day']), format(r['v'] or 0, ','), r['code']))
    for k in rf: kind = ' '.join(k.split()[:2]); counts[kind] = counts.get(kind, 0) + 1   # two words: the third is a number in some Hebrew flags
    out[h] = {k: v for k, v in {'f': f, 'med': med, 'last': last, 'pk': x.get('pk'), 'rf': rf, 'kpi': kpi(h, x)}.items() if v not in (None, '', [], {})}

doc = {'date': today, 'read': len(raw), 'data': out}
os.makedirs(os.path.join(out_dir, 'history'), exist_ok=True)
for p in (os.path.join(out_dir, 'latest.json'), os.path.join(out_dir, 'history', today + '.json')):
    json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
flagged = {h: v['rf'] for h, v in out.items() if v.get('rf')}
print('read', len(raw), '| updated', sum(1 for v in out.values() if 'f' in v), '| flagged', len(flagged),
      '| likes/comments per 1K', sum(1 for v in out.values() if 'lpk' in v.get('kpi', {}) or 'cpk' in v.get('kpi', {})),
      '| purchase signals', sum(1 for v in out.values() if 'bs' in v.get('kpi', {})), '| written to', out_dir)
for k, n in sorted(counts.items(), key=lambda t: -t[1]): print('  %3d  %s' % (n, k))
for h, r in sorted(flagged.items()):
    if any('/reel/' in x for x in r): print('POSTED', h, [x for x in r if '/reel/' in x])
