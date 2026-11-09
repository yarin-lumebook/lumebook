"""Top 100 Reels by play_count, plus a pool of low performers from the same calendar months
(owned by matan.nistor, no collab, plays at or below that month's 25th percentile) to match 20 comparisons from."""
import json, collections, statistics as st
inv = json.load(open('inventory.json'))
clips = inv['clips']
top = clips[:100]
bymonth = collections.defaultdict(list)
for x in clips:
    bymonth[x['date'][:7]].append(x)
topmonths = collections.Counter(x['date'][:7] for x in top)
pool = []
for m, n in topmonths.items():
    xs = [x for x in bymonth[m] if not x['collab']]
    if len(xs) < 4: continue
    q1 = sorted(x['play_count'] for x in xs)[len(xs)//4]
    low = sorted([x for x in xs if x['play_count'] <= q1], key=lambda x: x['play_count'])
    pool += low[:max(2, n + 1)]
pool = [x for x in pool if x['code'] not in {t['code'] for t in top}]
json.dump({'top': [x['pk'] for x in top], 'pool': [x['pk'] for x in pool]}, open('fetch_list.json', 'w'))
print('months', len(topmonths), 'pool', len(pool))
print('pool plays median', st.median(x['play_count'] for x in pool))
