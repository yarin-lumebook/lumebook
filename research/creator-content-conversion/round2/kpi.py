"""Per-post and per-creator purchase-signal KPIs for the 134-creator sample (recent posts, 7 to 90 days).

Comment labels: rule labels (keyword = request for the post's offer, creator = creator's own comment)
plus agent-verified labels on every candidate comment (product_q, intent, purchase, resource_request, help, other).
Every rate states its denominator. Missing = blank."""
import json, glob, os, statistics as st, csv, collections

B = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(B, 'sample.json')))
CM = {}
for f in ['cm.json', 'cm_extra.json', 'cm_new.json']:
    CM.update(json.load(open(os.path.join(B, f))))
RULE = json.load(open(os.path.join(B, 'rule_labels.json')))
VER = {}
for f in glob.glob(os.path.join(B, 'cand_out', '*.json')):
    for x in json.load(open(f)):
        VER[(x['code'], x['i'])] = x['label']
MAP = {c['h']: c for c in json.load(open('/Users/yarinbruner/Claude/Projects/Lumebook/creators/creator-research/src/C_all.json'))}
NEW = set(json.load(open(os.path.join(B, 'new_handles.json'))))


def per(a, b, k=1000):
    return round(a * k / b, 2) if a is not None and b else None


def med(x):
    x = [v for v in x if v is not None]
    return st.median(x) if x else None


rows = []
for u, r in S.items():
    fc = (r.get('prof') or {}).get('fc')
    for q in r['posts']:
        if q['set'] != 'sample':
            continue
        likes = None if q['hid'] else q['likes']
        plays = q.get('plays')
        rec = dict(creator=u, new_in_round2=u in NEW, post_code=q['code'], url=f"https://www.instagram.com/p/{q['code']}/",
                   format=q['format'], published=q['t'], age_days=round(q['age_d'], 1), followers=fc, plays=plays, likes=likes,
                   comments=q['com'], reposts=q.get('rep'), coauthored=bool(q.get('coa')), paid_label=bool(q.get('paid')),
                   caption=(q.get('cap') or '')[:300])
        v = CM.get(q['code'])
        lab = RULE.get(q['code'])
        if v is not None and lab is not None:
            cm = v['comments'][:30]
            final = []
            for i, l in enumerate(lab):
                if l in ('keyword', 'creator'):
                    final.append(l)
                else:
                    final.append(VER.get((q['code'], i), 'other'))
            c = collections.Counter(final)
            n_aud = len(cm) - c['creator']
            sig = c['product_q'] + c['intent'] + c['purchase']
            offer = c['keyword'] + c['resource_request']
            rec.update(sampled=len(cm), sampled_audience=n_aud, product_q=c['product_q'], intent=c['intent'], purchase=c['purchase'],
                       purchase_signals=sig, offer_requests=offer, help=c['help'],
                       purchase_signals_per_100=round(sig * 100 / n_aud, 1) if n_aud else None,
                       offer_share=round(offer / n_aud, 3) if n_aud else None)
            # estimated offer requests on the whole post (share of sample x total comments); an estimate, ranked sample
            rec['offer_requests_est_total'] = round(rec['offer_share'] * q['com']) if n_aud and q['com'] else None
        rec.update(likes_per_1k_plays=per(likes, plays), comments_per_1k_plays=per(q['com'], plays), reposts_per_1k_plays=per(q.get('rep'), plays),
                   plays_per_follower=round(plays / fc, 3) if plays and fc else None,
                   comments_per_1k_followers=per(q['com'], fc), likes_per_1k_followers=per(likes, fc),
                   offer_requests_est_per_1k_plays=per(rec.get('offer_requests_est_total'), plays),
                   offer_requests_est_per_1k_followers=per(rec.get('offer_requests_est_total'), fc))
        rows.append(rec)

json.dump(rows, open(os.path.join(B, 'kpi_posts.json'), 'w'), ensure_ascii=False)
# creator level
by = collections.defaultdict(list)
for r in rows:
    by[r['creator']].append(r)
crow = []
for u, rs in by.items():
    fc = rs[0]['followers']
    cm = [r for r in rs if r.get('sampled')]
    sig = sum(r['purchase_signals'] for r in cm)
    aud = sum(r['sampled_audience'] for r in cm)
    crow.append(dict(
        creator=u, new_in_round2=u in NEW, archetype=MAP.get(u, {}).get('arch'), followers=fc, map_median_views=MAP.get(u, {}).get('med'),
        posts=len(rs), posts_with_comments_sampled=len(cm), comments_sampled=sum(r['sampled'] for r in cm),
        purchase_signals=sig, purchase_signals_per_100=round(sig * 100 / aud, 2) if aud else None,
        posts_with_purchase_signal=sum(1 for r in cm if r['purchase_signals'] > 0),
        offer_requests=sum(r['offer_requests'] for r in cm), posts_with_offer_funnel=sum(1 for r in cm if (r['offer_share'] or 0) >= 0.5),
        median_plays=med([r['plays'] for r in rs if r['format'] == 'reel']),
        median_plays_per_follower=med([r['plays_per_follower'] for r in rs]),
        median_comments_per_1k_plays=med([r['comments_per_1k_plays'] for r in rs]),
        median_reposts_per_1k_plays=med([r['reposts_per_1k_plays'] for r in rs]),
        median_likes_per_1k_plays=med([r['likes_per_1k_plays'] for r in rs]),
        median_comments_per_1k_followers=med([r['comments_per_1k_followers'] for r in rs]),
    ))
json.dump(crow, open(os.path.join(B, 'kpi_creators.json'), 'w'), ensure_ascii=False)
print(len(rows), 'posts', len(crow), 'creators', sum(1 for r in rows if r.get('sampled')), 'with comments')
tot = collections.Counter()
for r in rows:
    if r.get('sampled'):
        for k in ('sampled', 'sampled_audience', 'product_q', 'intent', 'purchase', 'offer_requests', 'help'):
            tot[k] += r[k]
print(dict(tot))
