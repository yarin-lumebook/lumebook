"""Who may join the creator map (Yarin, 24 Oct 2026): every new creator must pass all of shared/facts.json
creators.admission. Creators already in the map are never checked against it, removed or changed.

    check(x) -> (reason it fails in English, or None; numbers)
    he(x)    -> the same reason in Hebrew for the map (None when it passes)

x is one profile as weekly/read.js reads it: fc (followers), med (median views), and rl, the 12 newest reels as
[code, day, views, likes, comments]. Likes and comments per 1,000 views are the median per reel over those reels with
numbers (3 at least), the same math as the card (src/refresh/refresh.py). A profile whose likes or comments cannot be
read (hidden likes, fewer than 3 reels with numbers) does not pass: it cannot be shown to meet the bar.
"""
import json, os, statistics
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *['..'] * 5))   # the project folder
A = json.load(open(os.path.join(ROOT, 'shared', 'facts.json'), encoding='utf-8'))['creators']['admission']


def numbers(x):
    f, med = x.get('fc'), x.get('med')
    rl = [r for r in (x.get('rl') or []) if r[2]]
    lp = [r[3] * 1000 / r[2] for r in rl if r[3] is not None]
    cp = [r[4] * 1000 / r[2] for r in rl if r[4] is not None]
    return {'vpf': round(med / f, 2) if f and med is not None else None,
            'lpk': round(statistics.median(lp), 2) if len(lp) >= 3 else None,
            'cpk': round(statistics.median(cp), 2) if len(cp) >= 3 else None}


def fail(x):
    """The first rule the profile fails, as a key, or None; and its numbers."""
    n, f, med = numbers(x), x.get('fc'), x.get('med')
    k = ('f?' if f is None else 'f<' if f < A['followers_min'] else 'f>' if f > A['followers_max']
         else 'med?' if med is None else 'med' if med < A['median_views_min']
         else 'vpf' if n['vpf'] < A['views_per_follower_min']
         else 'lpk?' if n['lpk'] is None else 'lpk' if n['lpk'] < A['likes_per_1k_views_min']
         else 'cpk?' if n['cpk'] is None else 'cpk' if n['cpk'] < A['comments_per_1k_views_min'] else None)
    return k, n


def check(x):
    k, n = fail(x)
    f, med, c = x.get('fc'), x.get('med'), lambda v: format(v, ',')
    return ({None: None, 'f?': 'followers unknown', 'f<': 'under %s followers' % c(A['followers_min']),
             'f>': 'over %s followers' % c(A['followers_max']), 'med?': 'median views unknown',
             'med': 'median views %s, under %s' % (c(med or 0), c(A['median_views_min'])),
             'vpf': 'views per follower %s, under %s' % (n['vpf'], A['views_per_follower_min']),
             'lpk?': 'likes per 1K views not readable (hidden likes or under 3 reels)',
             'lpk': 'likes per 1K views %s, under %s' % (n['lpk'], A['likes_per_1k_views_min']),
             'cpk?': 'comments per 1K views not readable (under 3 reels)',
             'cpk': 'comments per 1K views %s, under %s' % (n['cpk'], A['comments_per_1k_views_min'])}[k], n)


def he(x):
    k, n = fail(x)
    f, med, c = x.get('fc'), x.get('med'), lambda v: format(v, ',')
    return {None: None, 'f?': 'לא ידוע כמה עוקבים', 'f<': '%s עוקבים, צריך לפחות %s' % (c(f), c(A['followers_min'])),
            'f>': '%s עוקבים, יותר מ-%s' % (c(f), c(A['followers_max'])), 'med?': 'אין צפיות לרילס',
            'med': 'צפיות חציון %s, צריך לפחות %s' % (c(med), c(A['median_views_min'])),
            'vpf': 'צפיות לעוקב %s, צריך לפחות %s' % (n['vpf'], A['views_per_follower_min']),
            'lpk?': 'הלייקים מוסתרים, אי אפשר לבדוק', 'lpk': 'לייקים ל-1K צפיות %s, צריך לפחות %s' % (n['lpk'], A['likes_per_1k_views_min']),
            'cpk?': 'פחות מ-3 רילס עם תגובות', 'cpk': 'תגובות ל-1K צפיות %s, צריך לפחות %s' % (n['cpk'], A['comments_per_1k_views_min'])}[k]
