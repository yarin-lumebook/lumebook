"""Markdown leaderboards for report.md. Sample set only (recent posts), one table per KPI."""
import json, os, statistics as st, collections
B = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(B, 'rows.json')))
S = [r for r in R if r['set'] == 'sample']
CP = json.load(open(os.path.join(B, 'comment_posts.json')))
out = []
def link(r):
    return f"[{r['post_code']}]({r['url']})"
def d(r):
    return r['published_utc'][:10]
def topic(r):
    t = (r.get('topic') or '')
    return t[:58] + ('…' if len(t) > 58 else '')
def tbl(title, rows, cols, note=''):
    out.append(f'\n**{title}**' + (f' {note}' if note else '') + '\n')
    out.append('| ' + ' | '.join(c[0] for c in cols) + ' |')
    out.append('|' + '|'.join('---' for _ in cols) + '|')
    for r in rows:
        out.append('| ' + ' | '.join(str(c[1](r)) for c in cols) + ' |')
def fmt(x):
    if x is None: return 'n/a'
    if isinstance(x, float): return f'{x:,.0f}' if x >= 100 else f'{x:,.2f}'
    if isinstance(x, int): return f'{x:,}'
    return str(x)

reels = [r for r in S if r['format'] == 'reel' and r['plays']]
base = [('Creator', lambda r: r['creator']), ('Post', link), ('Published', d), ('Topic (coded)', topic)]
tbl('A1. Reels: highest raw plays', sorted(reels, key=lambda r: -r['plays'])[:10],
    base + [('Plays', lambda r: fmt(r['plays'])), ('Followers', lambda r: fmt(r['followers_14oct']))])
tbl('A2. Reels: plays vs the creator\'s own reel median', sorted([r for r in reels if (r['baseline_n_same_format'] or 0) >= 3 and r['rel_plays']], key=lambda r: -r['rel_plays'])[:10],
    base + [('Plays', lambda r: fmt(r['plays'])), ('Creator median', lambda r: fmt(r['baseline_median_plays'])), ('Ratio', lambda r: f"{r['rel_plays']:.1f}x")], '(only formats with at least 3 sample reels)')
big = [r for r in reels if r['plays'] >= 2000]
tbl('E1. Reels: likes per 1,000 plays', sorted([r for r in big if r['likes_per_1k_plays']], key=lambda r: -r['likes_per_1k_plays'])[:8],
    base + [('Likes', lambda r: fmt(r['likes'])), ('Plays', lambda r: fmt(r['plays'])), ('Likes/1k plays', lambda r: fmt(r['likes_per_1k_plays']))], '(reels with at least 2,000 plays; likes hidden on 41 sample posts)')
tbl('E2a. Reels: comments per 1,000 plays, all CTAs', sorted([r for r in big if r['comments_per_1k_plays']], key=lambda r: -r['comments_per_1k_plays'])[:8],
    base + [('CTA', lambda r: r['cta']), ('Comments', lambda r: fmt(r['comments'])), ('Plays', lambda r: fmt(r['plays'])), ('Comments/1k plays', lambda r: fmt(r['comments_per_1k_plays']))], '(reels with at least 2,000 plays)')
tbl('E2b. Reels: comments per 1,000 plays, posts without a comment-keyword CTA or giveaway', sorted([r for r in big if r['comments_per_1k_plays'] and r['cta'] not in ('comment_keyword', 'join_group_or_course') and r['status'] != 'giveaway'], key=lambda r: -r['comments_per_1k_plays'])[:8],
    base + [('Comments', lambda r: fmt(r['comments'])), ('Plays', lambda r: fmt(r['plays'])), ('Comments/1k plays', lambda r: fmt(r['comments_per_1k_plays']))])
tbl('E3. Reels: reposts per 1,000 plays', sorted([r for r in big if r['reposts_per_1k_plays']], key=lambda r: -r['reposts_per_1k_plays'])[:8],
    base + [('Reposts', lambda r: fmt(r['reposts'])), ('Plays', lambda r: fmt(r['plays'])), ('Reposts/1k plays', lambda r: fmt(r['reposts_per_1k_plays']))], '(public repost count; DM shares are not public)')
nonreel = [r for r in S if r['format'] != 'reel']
tbl('E4. Carousels and images: highest raw comments', sorted(nonreel, key=lambda r: -(r['comments'] or 0))[:8],
    base + [('CTA / status', lambda r: f"{r['cta']} / {r['status']}"), ('Comments', lambda r: fmt(r['comments'])), ('Likes', lambda r: fmt(r['likes'])), ('Comments vs creator median', lambda r: f"{r['rel_comments']:.1f}x" if r['rel_comments'] else 'n/a')])
tbl('E5. Carousels and images: likes per 1,000 followers (proxy)', sorted([r for r in nonreel if r['likes_per_1k_followers_proxy']], key=lambda r: -r['likes_per_1k_followers_proxy'])[:8],
    base + [('Likes', lambda r: fmt(r['likes'])), ('Followers', lambda r: fmt(r['followers_14oct'])), ('Likes/1k followers', lambda r: fmt(r['likes_per_1k_followers_proxy']))])

# consideration proxies from comments
def cpost(p):
    return p['row']
cp = [p for p in CP if p['n_comments'] >= 5]
def intent(p):
    c = p['counts']; return c.get('explicit_buying_intent', 0) + c.get('product_or_price_question', 0) + c.get('purchase_report', 0)
out.append('\n**C1. Purchase-intent comments (explicit intent + product or price questions + self-reported purchases), raw and per 100 sampled comments** (posts with at least 5 sampled comments; Instagram ranked order)\n')
out.append('| Creator | Post | Topic (coded) | Sampled | Intent comments | Per 100 | Keyword requests (separate) |')
out.append('|---|---|---|---|---|---|---|')
for p in sorted(cp, key=lambda p: (-intent(p), -intent(p) / p['n_comments']))[:10]:
    r = p['row']
    out.append(f"| {p['creator']} | [{p['code']}](https://www.instagram.com/p/{p['code']}/) | {topic(r)} | {p['n_comments']} | {intent(p)} | {intent(p)*100/p['n_comments']:.0f} | {p['counts'].get('keyword_request', 0)} |")
out.append('\n**C2. Requests for an offered link, file or list (keyword requests), per 100 sampled comments** (a request for the creator\'s offer, not spontaneous intent)\n')
out.append('| Creator | Post | Topic (coded) | Sampled | Keyword requests | Post total comments |')
out.append('|---|---|---|---|---|---|')
for p in sorted(cp, key=lambda p: -p['counts'].get('keyword_request', 0) / p['n_comments'])[:10]:
    r = p['row']
    out.append(f"| {p['creator']} | [{p['code']}](https://www.instagram.com/p/{p['code']}/) | {topic(r)} | {p['n_comments']} | {p['counts'].get('keyword_request', 0)} | {fmt(r.get('comments'))} |")
def subst(p):
    c = p['counts']; return c.get('identification', 0) + c.get('personal_experience', 0) + c.get('practical_help_request', 0)
out.append('\n**C3. Substantive discussion (identification + personal experience + help requests), per 100 sampled comments** (posts with at least 10 sampled comments)\n')
out.append('| Creator | Post | Topic (coded) | Sampled | Substantive | Per 100 | Help requests |')
out.append('|---|---|---|---|---|---|---|')
for p in sorted([p for p in cp if p['n_comments'] >= 10], key=lambda p: -subst(p) / p['n_comments'])[:10]:
    r = p['row']
    out.append(f"| {p['creator']} | [{p['code']}](https://www.instagram.com/p/{p['code']}/) | {topic(r)} | {p['n_comments']} | {subst(p)} | {subst(p)*100/p['n_comments']:.0f} | {p['counts'].get('practical_help_request', 0)} |")
open(os.path.join(B, 'leaderboards.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
