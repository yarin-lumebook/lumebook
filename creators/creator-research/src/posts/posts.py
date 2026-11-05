"""Daily numbers for the creators' posts linked in the creator map's books table ("ספרים שנוצרו").

    python3 posts.py todo                  # the posts to read, for posts.js: [{"c": shortcode, "h": owner handle}]
    python3 posts.py ingest <out.json>     # saves what posts.js returned (its `out`) into state/posts.json
    python3 posts.py show                  # the saved numbers, one line per post

The links live in the map's settings (state/settings.json, main.books[].post), typed in the table by Yarin.
state/posts.json is written only here; the map page reads it (state/posts.json next to the map) and shows each post's
views, likes and comments under the creator's name, with the change since the previous day's reading.
A post that is not found keeps its last numbers and gets `miss` (the date it was missed).
--state <dir> reads and writes another state folder (a test run).
"""
import json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
STATE = args[args.index('--state') + 1] if '--state' in args else os.path.join(HERE, '..', '..', 'state')
POSTS = os.path.join(STATE, 'posts.json')
TODAY = datetime.date.today().isoformat()
KEEP_DAYS = 400                                  # history rows kept per post

# instagram.com/p/<code>, /reel/<code>, /reels/<code>, /tv/<code>, optionally after /<username>/
LINK = re.compile(r'instagram\.com/(?:([A-Za-z0-9_.]+)/)?(?:p|reels?|tv)/([A-Za-z0-9_-]{5,})', re.I)


def code_of(url):
    m = LINK.search(url or '')
    if not m: return None, None
    user = m.group(1)
    return m.group(2), (user if user and user.lower() not in ('p', 'reel', 'reels', 'tv', 'stories') else None)


def load_posts():
    try:
        return json.load(open(POSTS, encoding='utf-8'))
    except FileNotFoundError:
        return {'at': None, 'posts': {}}


def save_posts(doc):
    tmp = POSTS + '.tmp'
    json.dump(doc, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, POSTS)


def todo():
    s = json.load(open(os.path.join(STATE, 'settings.json'), encoding='utf-8'))
    books = (s.get('main') or {}).get('books') or []
    out, seen, other = [], set(), 0
    for b in books:
        url = str(b.get('post') or '').strip()
        if not url: continue
        c, user = code_of(url)
        if not c: other += 1; continue           # not an Instagram post link (a story, TikTok...): nothing to read
        h = (user or b.get('h') or '').strip().lstrip('@')
        if c in seen or not h: continue
        seen.add(c); out.append({'c': c, 'h': h})
    print(json.dumps(out))
    print('%d posts to read%s' % (len(out), ', %d links that are not Instagram posts' % other if other else ''), file=sys.stderr)


def ingest(path):
    got = json.load(open(path, encoding='utf-8'))
    if isinstance(got, dict) and 'out' in got: got = got['out']
    doc = load_posts(); P = doc.setdefault('posts', {})
    read = miss = 0
    for c, x in got.items():
        p = P.setdefault(c, {})
        if x.get('err'):
            p['miss'] = TODAY; miss += 1; continue
        p.update({'h': x.get('u') or p.get('h'), 'on': x.get('on') or p.get('on'), 'd': TODAY,
                  'v': x.get('v'), 'l': x.get('l'), 'm': x.get('m')})
        p.pop('miss', None)
        hist = [r for r in p.get('hist', []) if r[0] != TODAY] + [[TODAY, x.get('v'), x.get('l'), x.get('m')]]
        p['hist'] = sorted(hist)[-KEEP_DAYS:]
        read += 1
    doc['at'] = datetime.datetime.now().isoformat(timespec='minutes')
    save_posts(doc)
    print('read %d, not found %d, saved to %s' % (read, miss, os.path.normpath(POSTS)))
    show()


def show():
    P = load_posts().get('posts', {})
    fmt = lambda n: '-' if n is None else format(n, ',')
    for c, p in sorted(P.items(), key=lambda t: t[1].get('h') or ''):
        h = p.get('hist') or []
        prev = h[-2] if len(h) > 1 else None
        dv = ' (+%s views since %s)' % (fmt((p.get('v') or 0) - (prev[1] or 0)), prev[0]) if prev and p.get('v') is not None and prev[1] is not None else ''
        print('%-24s %-12s views %8s  likes %6s  comments %5s  read %s%s%s' % (
            p.get('h'), c, fmt(p.get('v')), fmt(p.get('l')), fmt(p.get('m')), p.get('d'), dv,
            '  NOT FOUND ' + p['miss'] if p.get('miss') else ''))


if __name__ == '__main__':
    cmd = args[0] if args else ''
    if cmd == 'todo': todo()
    elif cmd == 'ingest' and len(args) > 1: ingest(args[1])
    elif cmd == 'show': show()
    else: sys.exit(__doc__)
