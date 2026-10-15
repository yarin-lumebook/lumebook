"""Topic/occasion and content-feature aggregates over the recent sample.
Uses within-creator ratios (rel_plays for reels, rel_likes / rel_comments for carousels+images),
so audience size cancels out. Reports n posts, n creators, medians, and how many creators
show the pattern (category median above their own overall median)."""
import json, statistics as st, collections, os, sys
B = os.path.dirname(os.path.abspath(__file__))
R = [r for r in json.load(open(os.path.join(B, 'rows.json'))) if r['set'] == 'sample' and r['topic']]

def med(x):
    x = [v for v in x if v is not None]
    return round(st.median(x), 2) if x else None

def attn(r):
    return r['rel_plays'] if r['format'] == 'reel' else r['rel_likes']

OCC_GROUP = {
    'birthday': 'buying occasion', 'new_sibling': 'buying occasion', 'pregnancy': 'buying occasion', 'pacifier': 'buying occasion',
    'potty_diaper': 'buying occasion', 'gan_start': 'buying occasion', 'first_grade': 'buying occasion',
    'reading_books': 'books and reading', 'sleep_bedtime': 'books and reading', 'holiday': 'buying occasion',
    'gift_general': 'gift', 'grandparent': 'gift',
    'development_learning': 'development and behaviour', 'behaviour_emotions': 'development and behaviour',
    'daily_parenting': 'everyday parenting', 'family_outing': 'other', 'food_home': 'other',
    'humour_entertainment': 'humour', 'other': 'other'}

def table(key, rows=R, min_n=5, label=None):
    g = collections.defaultdict(list)
    for r in rows:
        g[key(r)].append(r)
    out = []
    for k, rs in g.items():
        if len(rs) < min_n:
            continue
        reels = [r for r in rs if r['format'] == 'reel']
        car = [r for r in rs if r['format'] != 'reel']
        out.append(dict(k=k, n=len(rs), creators=len({r['creator'] for r in rs}),
                        reels=len(reels), med_rel_plays=med([r['rel_plays'] for r in reels]),
                        med_c1k=med([r['comments_per_1k_plays'] for r in reels]),
                        med_l1k=med([r['likes_per_1k_plays'] for r in reels]),
                        med_r1k=med([r['reposts_per_1k_plays'] for r in reels]),
                        nonreel=len(car), med_rel_likes_nonreel=med([r['rel_likes'] for r in car]),
                        med_rel_com_all=med([r['rel_comments'] for r in rs])))
    out.sort(key=lambda d: -d['n'])
    print('\n==', label or '', '(sample posts with coding:', len(rows), ')')
    print(f"{'category':28} {'n':>4} {'cr':>3} | reels {'relP':>5} {'c/1k':>5} {'l/1k':>5} {'rp/1k':>5} | other {'relL':>5} | {'relC':>5}")
    for d in out:
        print(f"{str(d['k'])[:28]:28} {d['n']:>4} {d['creators']:>3} | {d['reels']:>5} {str(d['med_rel_plays']):>5} {str(d['med_c1k']):>5} {str(d['med_l1k']):>5} {str(d['med_r1k']):>5} | {d['nonreel']:>5} {str(d['med_rel_likes_nonreel']):>5} | {str(d['med_rel_com_all']):>5}")
    return out

if __name__ == '__main__':
    res = {}
    res['occasion'] = table(lambda r: r['occasion'], label='occasion')
    res['occ_group'] = table(lambda r: OCC_GROUP.get(r['occasion'], 'other'), label='occasion group')
    res['relevance'] = table(lambda r: r['lumebook_relevance'], label='LumeBook relevance')
    res['emotion'] = table(lambda r: r['emotional_angle'], label='emotional angle')
    res['format'] = table(lambda r: r['format_detail'], label='format detail')
    res['cta'] = table(lambda r: r['cta'], label='CTA')
    res['product'] = table(lambda r: r['product_visible'], label='product visibility')
    res['status'] = table(lambda r: r['status'], label='status')
    res['hook'] = table(lambda r: r['hook_type'], label='hook type')
    res['takeaway'] = table(lambda r: 'has takeaway' if (r['practical_takeaway'] or 'none').strip().lower() != 'none' else 'no takeaway', label='practical takeaway')
    res['segment'] = table(lambda r: r['buyer_segment'], label='buyer segment')
    res['stratum'] = table(lambda r: r['stratum'], label='creator stratum')
    # within-creator consistency: for each creator with >=2 high and >=2 low relevance posts
    print('\n== within-creator: high-relevance vs low-relevance posts (attention ratio)')
    by = collections.defaultdict(list)
    for r in R:
        by[r['creator']].append(r)
    wins = 0; tot = 0
    for u, rs in sorted(by.items()):
        hi = [attn(r) for r in rs if r['lumebook_relevance'] == 'high' and attn(r)]
        lo = [attn(r) for r in rs if r['lumebook_relevance'] == 'low' and attn(r)]
        if len(hi) >= 2 and len(lo) >= 2:
            tot += 1; w = st.median(hi) > st.median(lo); wins += w
            print(f"  {u:30} high n={len(hi)} med={st.median(hi):.2f} | low n={len(lo)} med={st.median(lo):.2f} {'HIGH>LOW' if w else ''}")
    print(f'  creators where high-relevance posts beat low-relevance posts: {wins}/{tot}')
    for feat, fn in [('comment_keyword CTA', lambda r: r['cta'] == 'comment_keyword'), ('practical takeaway', lambda r: (r['practical_takeaway'] or 'none').strip().lower() != 'none'), ('humour', lambda r: r['emotional_angle'] == 'humour'), ('product featured/demonstrated', lambda r: r['product_visible'] in ('featured', 'demonstrated'))]:
        w = t = 0
        for u, rs in by.items():
            a = [r['rel_comments'] for r in rs if fn(r) and r['rel_comments']]
            b = [r['rel_comments'] for r in rs if not fn(r) and r['rel_comments']]
            if len(a) >= 1 and len(b) >= 2:
                t += 1; w += st.median(a) > st.median(b)
        w2 = t2 = 0
        for u, rs in by.items():
            a = [attn(r) for r in rs if fn(r) and attn(r)]
            b = [attn(r) for r in rs if not fn(r) and attn(r)]
            if len(a) >= 1 and len(b) >= 2:
                t2 += 1; w2 += st.median(a) > st.median(b)
        print(f'  {feat}: comments ratio higher in {w}/{t} creators; attention ratio higher in {w2}/{t2} creators')
    json.dump(res, open(os.path.join(B, 'aggregates.json'), 'w'), ensure_ascii=False, indent=1)
