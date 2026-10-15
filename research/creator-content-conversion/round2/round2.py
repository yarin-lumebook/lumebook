"""Round 2: which content reaches the public purchase-signal KPIs, across 134 creators.
Groups (recent sample posts with sampled comments):
  top_purchase : >= 3 verified purchase-signal comments (product/price questions, buying intent, self-reported purchases)
  top_offer    : new creators, top 50 by estimated offer requests per 1k followers (offer share >= 50%)
  top_reposts  : new creators, top 30 by reposts per 1k plays (plays >= 2,000)
  baseline     : posts in none of the top groups that have content codes (all 41 round-1 creators' coded
                 posts + 120 random new-creator posts)
Trait shares are compared top vs baseline (lift = top share / baseline share). Observational only."""
import json, glob, os, collections, statistics as st
B = os.path.dirname(os.path.abspath(__file__))
OLD = '/private/tmp/claude-501/-Users-yarinbruner-Claude-Projects-Lumebook/fd0f7925-159f-49b8-a42a-92b54c8e7515/scratchpad'
P = {p['post_code']: p for p in json.load(open(os.path.join(B, 'kpi_posts.json')))}
ROLE = json.load(open(os.path.join(B, 'select2_roles.json')))
CODED = {}
for f in glob.glob(os.path.join(OLD, 'coded', '*.json')) + glob.glob(os.path.join(B, 'coded', '*.json')):
    for x in json.load(open(f)):
        CODED[x['code']] = x
for code, p in P.items():
    if p.get('sampled') and p['purchase_signals'] >= 3:
        ROLE.setdefault(code, [])
        if 'top_purchase' not in ROLE[code]:
            ROLE[code].append('top_purchase')
groups = collections.defaultdict(list)
for code, p in P.items():
    if code not in CODED or not p.get('sampled'):
        continue
    r = ROLE.get(code, [])
    tops = [g for g in r if g != 'baseline']
    if tops:
        for g in tops:
            groups[g].append(code)
    else:
        groups['baseline'].append(code)
print({g: len(v) for g, v in groups.items()})

def tr(code):
    c = CODED[code]
    disc = (c.get('discount_or_code') or '').strip()
    return {
        'product shown (featured or demonstrated)': c.get('product_visible') in ('featured', 'demonstrated'),
        'product demonstrated in use': c.get('product_visible') == 'demonstrated',
        'price visible': c.get('price_visible') in (True, 'True', 'true'),
        'discount, code or deal offered': bool(disc),
        'comment-word CTA': c.get('cta') == 'comment_keyword',
        'link in bio / buy link CTA': c.get('cta') in ('link_in_bio', 'buy_link'),
        'no CTA': c.get('cta') == 'none',
        'sponsored or brand collaboration': c.get('status') in ('likely_sponsored', 'collaboration', 'paid_partnership_label'),
        "creator's own product or service": c.get('status') == 'own_product_promo',
        'practical takeaway': (c.get('practical_takeaway') or 'none').strip().lower() != 'none',
        'humour': c.get('emotional_angle') == 'humour',
        'reassurance': c.get('emotional_angle') == 'reassurance',
        'excitement': c.get('emotional_angle') == 'excitement',
        'proof: demonstration result': c.get('proof') == 'demonstration_result',
        'proof: child reaction': c.get('proof') == 'child_reaction',
        'proof: expert credential': c.get('proof') == 'expert_credential',
        'format: hands demo': c.get('format_detail') == 'hands_demo',
        'format: product review': c.get('format_detail') == 'product_review',
        'format: talking head': c.get('format_detail') == 'talking_head',
        'format: skit / POV': c.get('format_detail') == 'skit_pov',
        'format: tips carousel': c.get('format_detail') == 'tips_carousel',
        'LumeBook relevance high': c.get('lumebook_relevance') == 'high',
        'LumeBook buying occasion': c.get('occasion') in ('birthday', 'new_sibling', 'pregnancy', 'pacifier', 'potty_diaper', 'gan_start', 'first_grade', 'holiday', 'gift_general', 'grandparent', 'reading_books', 'sleep_bedtime'),
        'category: children book / toy / game': c.get('product_category') in ('children_book', 'toy_game'),
        'category: home and cleaning': c.get('product_category') == 'home_cleaning',
        'category: clothing': c.get('product_category') == 'clothing',
        'category: food': c.get('product_category') == 'food',
        'category: attraction or trip': c.get('product_category') == 'attraction_trip',
        'category: baby gear': c.get('product_category') == 'baby_gear',
    }

traits = list(tr(next(iter(CODED))).keys())
def shares(codes):
    n = len(codes)
    return {t: sum(1 for c in codes if tr(c)[t]) / n for t in traits}, n
base, nb = shares(groups['baseline'])
res = {'groups': {g: len(v) for g, v in groups.items()}, 'traits': {}}
for g in ('top_purchase', 'top_offer', 'top_reposts'):
    s, n = shares(groups[g])
    res['traits'][g] = []
    print(f'\n== {g} (n={n}) vs baseline (n={nb})')
    for t in traits:
        lift = (s[t] / base[t]) if base[t] else None
        res['traits'][g].append(dict(trait=t, top=round(s[t] * 100), base=round(base[t] * 100), lift=round(lift, 2) if lift else None))
    for x in sorted(res['traits'][g], key=lambda x: -(x['lift'] or 99 if x['top'] > 0 else 0)):
        print(f"  {x['trait']:42} top {x['top']:3}%  base {x['base']:3}%  lift {x['lift']}")
# occasion / category breakdown of top_purchase
oc = collections.Counter(CODED[c].get('product_category') for c in groups['top_purchase'])
print('\ntop_purchase product categories', oc.most_common())
print('top_purchase occasions', collections.Counter(CODED[c].get('occasion') for c in groups['top_purchase']).most_common())
res['top_purchase_categories'] = oc.most_common()
res['top_purchase_posts'] = [dict(code=c, creator=P[c]['creator'], sig=P[c]['purchase_signals'], product_q=P[c]['product_q'], intent=P[c]['intent'], purchase=P[c]['purchase'],
                                  per100=P[c]['purchase_signals_per_100'], comments=P[c]['comments'], plays=P[c]['plays'], topic=CODED[c]['topic'],
                                  product=CODED[c].get('product_detail'), category=CODED[c].get('product_category'), price=CODED[c].get('price_visible'),
                                  disc=CODED[c].get('discount_or_code'), cta=CODED[c].get('cta'), status=CODED[c].get('status'), fmt=CODED[c].get('format_detail'),
                                  occasion=CODED[c].get('occasion'), relevance=CODED[c].get('lumebook_relevance'))
                             for c in sorted(groups['top_purchase'], key=lambda c: -P[c]['purchase_signals'])]
json.dump(res, open(os.path.join(B, 'round2.json'), 'w'), ensure_ascii=False, indent=1)
