"""Comment-level aggregates over comments_coded/: totals by class, by post role, by creator stratum,
by occasion and by CTA; and the post leaderboard for purchase-intent signals."""
import json, glob, os, collections
B = os.path.dirname(os.path.abspath(__file__))
rows = {r['post_code']: r for r in json.load(open(os.path.join(B, 'rows.json')))}
DEEP = json.load(open(os.path.join(B, 'deep.json')))
role = {p['code']: p['role'] for ps in DEEP.values() for p in ps}
CL = ['identification', 'personal_experience', 'practical_help_request', 'product_or_price_question', 'objection',
      'explicit_buying_intent', 'purchase_report', 'keyword_request', 'tag_or_share', 'giveaway_entry',
      'generic_praise', 'creator_reply', 'spam_or_unrelated']
posts = []
for f in glob.glob(os.path.join(B, 'comments_coded', '*.json')) + glob.glob(os.path.join(B, 'comments_extra_coded', '*.json')):
    d = json.load(open(f))
    for p in d['posts']:
        r = rows.get(p['code'], {})
        p['creator'] = d['handle']; p['role'] = role.get(p['code'], 'extra_high_relevance'); p['row'] = r
        posts.append(p)
tot = collections.Counter()
for p in posts:
    tot.update(p['counts'])
N = sum(p['n_comments'] for p in posts)
print('posts', len(posts), 'comments', N, 'unique commenters (sum over posts)', sum(p['n_unique_commenters'] for p in posts))
for k in CL:
    print(f'  {k:28} {tot[k]:5}  {tot[k]*100/N:5.1f}%')
print('  about_offer', sum(p['about_offer'] for p in posts), ' gift_mention', sum(p['gift_mention'] for p in posts))
occ = collections.Counter()
for p in posts:
    occ.update({k: v for k, v in (p.get('occasions') or {}).items() if k != 'none'})
print('  occasions mentioned in comments', dict(occ))

def grp(name, keyf):
    g = collections.defaultdict(list)
    for p in posts:
        g[keyf(p)].append(p)
    print(f'\n== by {name}')
    print(f"{'group':26} {'posts':>5} {'cmts':>5} | {'ident+exp':>9} {'help':>5} {'intent':>6} {'kwreq':>6} {'praise':>6} {'objec':>5} | intent/100 substantive/100")
    for k, ps in sorted(g.items(), key=lambda kv: -len(kv[1])):
        c = collections.Counter(); n = sum(p['n_comments'] for p in ps)
        for p in ps:
            c.update(p['counts'])
        intent = c['explicit_buying_intent'] + c['product_or_price_question'] + c['purchase_report']
        sub = c['identification'] + c['personal_experience'] + c['practical_help_request']
        print(f"{str(k)[:26]:26} {len(ps):>5} {n:>5} | {c['identification']+c['personal_experience']:>9} {c['practical_help_request']:>5} {intent:>6} {c['keyword_request']:>6} {c['generic_praise']:>6} {c['objection']:>5} | {intent*100/max(n,1):6.1f} {sub*100/max(n,1):6.1f}")

grp('post role', lambda p: p['role'])
grp('creator stratum', lambda p: p['row'].get('stratum'))
grp('occasion (post coding)', lambda p: p['row'].get('occasion'))
grp('LumeBook relevance', lambda p: p['row'].get('lumebook_relevance'))
grp('CTA', lambda p: p['row'].get('cta'))
grp('product visible', lambda p: p['row'].get('product_visible'))
grp('status', lambda p: p['row'].get('status'))
grp('emotional angle', lambda p: p['row'].get('emotional_angle'))

print('\n== post leaderboard: purchase-intent signals (explicit intent + product/price questions + purchase reports), raw and per comments sampled')
L = []
for p in posts:
    c = p['counts']; intent = c.get('explicit_buying_intent', 0) + c.get('product_or_price_question', 0) + c.get('purchase_report', 0)
    L.append((intent, round(intent * 100 / max(p['n_comments'], 1), 1), p['creator'], p['code'], p['n_comments'], c.get('keyword_request', 0), p['row'].get('topic'), p['row'].get('cta'), p['row'].get('product_detail')))
for x in sorted(L, key=lambda x: (-x[0], -x[1]))[:20]:
    print('  ', x)
print('\n== post leaderboard: substantive discussion (identification + experience + help requests)')
L2 = []
for p in posts:
    c = p['counts']; s = c.get('identification', 0) + c.get('personal_experience', 0) + c.get('practical_help_request', 0)
    L2.append((s, round(s * 100 / max(p['n_comments'], 1), 1), p['creator'], p['code'], p['n_comments'], p['row'].get('topic'), p['row'].get('occasion')))
for x in sorted(L2, key=lambda x: (-x[0], -x[1]))[:20]:
    print('  ', x)
print('\n== keyword-request leaderboard')
for x in sorted([(p['counts'].get('keyword_request', 0), p['creator'], p['code'], p['n_comments'], p['row'].get('topic')) for p in posts], key=lambda x: -x[0])[:15]:
    print('  ', x)
print('\n== gift mentions and objections')
for p in posts:
    if p['gift_mention'] or p['counts'].get('objection'):
        print('  ', p['creator'], p['code'], 'gift', p['gift_mention'], 'obj', p['counts'].get('objection'), '|', p['row'].get('topic'))
json.dump(posts, open(os.path.join(B, 'comment_posts.json'), 'w'), ensure_ascii=False)
